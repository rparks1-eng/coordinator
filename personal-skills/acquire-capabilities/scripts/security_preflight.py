#!/usr/bin/env python3
"""Inert, local-only preflight for acquired repositories, packages, and archives.

The scanner never executes candidate code and never uses the network. It reports
risk indicators; it cannot prove that code is safe.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import tarfile
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "blocker": 4}
CODE_SUFFIXES = {
    ".c", ".cc", ".cpp", ".cs", ".go", ".java", ".js", ".jsx", ".mjs",
    ".php", ".pl", ".ps1", ".py", ".rb", ".rs", ".sh", ".swift", ".ts",
    ".tsx", ".vue",
}
TEXT_SUFFIXES = CODE_SUFFIXES | {
    ".css", ".html", ".json", ".md", ".toml", ".txt", ".xml", ".yaml", ".yml",
}
ARCHIVE_SUFFIXES = {".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz"}
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "openai-style-key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
}
SENSITIVE_PATH = re.compile(
    r"(?:^|[/\\])(?:\.ssh|\.aws|\.codex|\.claude|Keychains|pairing\.json|auth\.json|"
    r"\.npmrc|\.pypirc|id_rsa|id_ed25519|Login Data|Cookies)(?:$|[/\\])",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
BEHAVIOR_PATTERNS = {
    "credential-path-access": ("blocker", re.compile(
        r"(?:\.codex[/\\]auth\.json|\.claude(?:[/\\]|\.json)|pairing\.json|"
        r"\.ssh[/\\]|\.aws[/\\]credentials|Library[/\\]Keychains|Login Data|Cookies)",
        re.IGNORECASE,
    )),
    "persistence-mechanism": ("blocker", re.compile(
        r"(?:LaunchAgents|LaunchDaemons|crontab|schtasks|CurrentVersion[/\\]Run|login item)",
        re.IGNORECASE,
    )),
    "shell-or-subprocess": ("high", re.compile(
        r"(?:child_process|\bexecFile\s*\(|\bspawn\s*\(|subprocess\.|os\.system\s*\(|"
        r"Runtime\.getRuntime\(\)\.exec)",
    )),
    "dynamic-code-execution": ("high", re.compile(
        r"(?:\beval\s*\(|\bFunction\s*\(|exec\s*\(\s*base64|eval\s*\(\s*atob)",
        re.IGNORECASE,
    )),
    "screen-camera-clipboard": ("high", re.compile(
        r"(?:screencapture|AVCapture|ScreenCaptureKit|getUserMedia|pbpaste|clipboard)",
        re.IGNORECASE,
    )),
    "network-client": ("medium", re.compile(
        r"(?:\bfetch\s*\(|\baxios\b|\bWebSocket\b|requests\.|urllib\.|httpx\.|aiohttp\.|"
        r"\bsocket\.|\bcurl\s|\bwget\s|net\.Dial)",
        re.IGNORECASE,
    )),
    "environment-access": ("medium", re.compile(
        r"(?:process\.env|os\.environ|os\.getenv|System\.getenv)",
    )),
}


class Preflight:
    def __init__(self, root: Path, max_files: int, max_total: int, max_file: int) -> None:
        self.root = root
        self.max_files = max_files
        self.max_total = max_total
        self.max_file = max_file
        self.findings: list[dict[str, str]] = []
        self.file_count = 0
        self.total_bytes = 0
        self.binary_count = 0
        self.network_hosts: set[str] = set()
        self.manifest = hashlib.sha256()

    def add(self, severity: str, code: str, rel: str, detail: str) -> None:
        self.findings.append({"severity": severity, "code": code, "path": rel, "detail": detail})

    def rel(self, path: Path) -> str:
        if path == self.root:
            return path.name
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return "<outside-target>"

    def scan(self) -> dict[str, object]:
        if self.root.is_symlink():
            self.add("blocker", "root-symlink", self.root.name, "Target root is a symlink.")
        elif self.root.is_file():
            self.scan_file(self.root)
        elif self.root.is_dir():
            for directory, dirnames, filenames in os.walk(self.root, topdown=True, followlinks=False):
                base = Path(directory)
                kept = []
                for name in sorted(dirnames):
                    child = base / name
                    if child.is_symlink():
                        self.add("blocker", "symlink-directory", self.rel(child), "Symlinked directory can escape the candidate root.")
                    elif name == ".git":
                        continue
                    else:
                        kept.append(name)
                dirnames[:] = kept
                for name in sorted(filenames):
                    self.scan_file(base / name)
        else:
            self.add("blocker", "invalid-target", self.root.name, "Target is not a regular file or directory.")

        antivirus = self.run_clamav()
        if self.binary_count and not antivirus["available"]:
            self.add("high", "antivirus-unavailable", "<target>", "Binary content exists but no local signature scanner is installed.")
        highest = max((RANK[item["severity"]] for item in self.findings), default=0)
        decision = "fail" if highest >= RANK["blocker"] else "review" if highest >= RANK["high"] else "pass"
        counts = {level: sum(item["severity"] == level for item in self.findings) for level in RANK}
        return {
            "schema": 1,
            "decision": decision,
            "claim": "Risk indicators only; this report is not a malware-free warranty.",
            "target": self.root.name,
            "files": self.file_count,
            "bytes": self.total_bytes,
            "binaries": self.binary_count,
            "manifest_sha256": self.manifest.hexdigest(),
            "network_hosts": sorted(self.network_hosts),
            "counts": counts,
            "local_controls": diagnostics(),
            "antivirus": antivirus,
            "findings": sorted(self.findings, key=lambda item: (-RANK[item["severity"]], item["path"], item["code"])),
        }

    def scan_file(self, path: Path) -> None:
        rel = self.rel(path)
        try:
            info = path.lstat()
        except OSError as error:
            self.add("high", "stat-failed", rel, type(error).__name__)
            return
        if stat.S_ISLNK(info.st_mode):
            self.add("blocker", "symlink-file", rel, "Symlinked file can escape the candidate root.")
            return
        if not stat.S_ISREG(info.st_mode):
            self.add("blocker", "special-file", rel, "Sockets, devices, and other special files are forbidden.")
            return
        if SENSITIVE_PATH.search(rel) or (path.name.startswith(".env") and path.name not in {".env.example", ".env.sample", ".env.template"}):
            self.add("blocker", "sensitive-file-name", rel, "Candidate contains a credential- or profile-associated path.")
        self.file_count += 1
        self.total_bytes += info.st_size
        if self.file_count > self.max_files:
            self.add("blocker", "file-count-limit", rel, f"Candidate exceeds {self.max_files} files.")
            return
        if self.total_bytes > self.max_total:
            self.add("blocker", "total-size-limit", rel, f"Candidate exceeds {self.max_total} bytes.")
            return
        if info.st_size > self.max_file:
            self.add("high", "file-size-limit", rel, f"File exceeds inert-scan limit of {self.max_file} bytes.")
            return
        digest = hashlib.sha256()
        try:
            with path.open("rb") as handle:
                head = handle.read(4096)
                digest.update(head)
                while chunk := handle.read(1024 * 1024):
                    digest.update(chunk)
        except OSError as error:
            self.add("high", "read-failed", rel, type(error).__name__)
            return
        self.manifest.update(f"{rel}\0{info.st_size}\0{digest.hexdigest()}\n".encode())

        kind = binary_kind(head, path)
        if kind:
            self.binary_count += 1
            self.inspect_binary(path, rel, kind)
        elif stat.S_IXUSR & info.st_mode and path.suffix.lower() in CODE_SUFFIXES:
            self.add("medium", "executable-source", rel, "Source file is marked executable.")

        if path.suffix.lower() in ARCHIVE_SUFFIXES:
            self.inspect_archive(path, rel)
        if path.name == "package.json":
            self.inspect_package_json(path, rel)
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"Dockerfile", "Makefile", "package.json"}:
            self.inspect_text(path, rel)

    def inspect_binary(self, path: Path, rel: str, kind: str) -> None:
        if kind != "mach-o":
            self.add("high", "foreign-or-opaque-binary", rel, f"Detected {kind} binary; do not execute on this host.")
            return
        code = run_local(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(path)])
        gate = run_local(["/usr/sbin/spctl", "--assess", "--type", "execute", str(path)])
        if code["returncode"] != 0:
            self.add("blocker", "invalid-or-missing-signature", rel, "macOS code-signature verification failed.")
        if gate["returncode"] != 0:
            self.add("blocker", "gatekeeper-rejected", rel, "macOS Gatekeeper assessment rejected the executable.")

    def inspect_archive(self, path: Path, rel: str) -> None:
        try:
            if zipfile.is_zipfile(path):
                with zipfile.ZipFile(path) as archive:
                    members = archive.infolist()
                    self.check_members(rel, [(m.filename, m.file_size, m.compress_size, (m.external_attr >> 16) & 0o170000 == stat.S_IFLNK) for m in members])
            elif tarfile.is_tarfile(path):
                with tarfile.open(path, "r:*") as archive:
                    members = archive.getmembers()
                    self.check_members(rel, [(m.name, m.size, max(path.stat().st_size, 1), m.issym() or m.islnk()) for m in members])
        except (OSError, tarfile.TarError, zipfile.BadZipFile, RuntimeError) as error:
            self.add("high", "archive-parse-failed", rel, type(error).__name__)

    def check_members(self, rel: str, members: list[tuple[str, int, int, bool]]) -> None:
        if len(members) > self.max_files:
            self.add("blocker", "archive-file-count", rel, "Archive expands beyond the file-count limit.")
        expanded = 0
        compressed = 0
        for name, size, packed, is_link in members[: self.max_files + 1]:
            normalized = PurePosixPath(name.replace("\\", "/"))
            if normalized.is_absolute() or ".." in normalized.parts:
                self.add("blocker", "archive-path-traversal", rel, "Archive contains an absolute or parent-traversal path.")
            if is_link:
                self.add("blocker", "archive-link", rel, "Archive contains a symbolic or hard link.")
            expanded += max(size, 0)
            compressed += max(packed, 0)
        if expanded > self.max_total:
            self.add("blocker", "archive-expanded-size", rel, "Archive expands beyond the total-size limit.")
        if compressed and expanded / compressed > 200:
            self.add("blocker", "archive-compression-ratio", rel, "Archive has a suspicious compression ratio.")

    def inspect_package_json(self, path: Path, rel: str) -> None:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            self.add("high", "package-json-invalid", rel, type(error).__name__)
            return
        scripts = data.get("scripts", {}) if isinstance(data, dict) else {}
        if isinstance(scripts, dict):
            for name in ("preinstall", "install", "postinstall"):
                if name in scripts:
                    self.add("high", "install-lifecycle-script", rel, f"Package defines `{name}`; inspect before installation.")
            if "prepare" in scripts:
                self.add("medium", "prepare-lifecycle-script", rel, "Package defines `prepare`; inspect before packaging or install.")
        if isinstance(data, dict) and data.get("bin"):
            self.add("medium", "package-executable", rel, "Package publishes a command-line executable.")

    def inspect_text(self, path: Path, rel: str) -> None:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")[: 1024 * 1024]
        except OSError as error:
            self.add("high", "text-read-failed", rel, type(error).__name__)
            return
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                self.add("blocker", "embedded-secret", rel, f"Detected {name}; value was not recorded.")
        if path.suffix.lower() in CODE_SUFFIXES or path.name in {"Dockerfile", "Makefile", "package.json"}:
            for code, (severity, pattern) in BEHAVIOR_PATTERNS.items():
                if pattern.search(text):
                    self.add(severity, code, rel, "Behavior requires explicit capability-specific review.")
            if any(len(line) > 20000 for line in text.splitlines()):
                self.add("high", "obfuscated-or-generated-code", rel, "Code contains an unusually long line.")
            for raw in URL_PATTERN.findall(text):
                host = urlsplit(raw.rstrip(".,);]")).hostname
                if host:
                    self.network_hosts.add(host.lower())

    def run_clamav(self) -> dict[str, object]:
        scanner = shutil.which("clamscan")
        if not scanner:
            return {"available": False, "status": "not-run", "reason": "clamscan is not installed"}
        result = run_local([
            scanner, "--recursive=yes", "--infected", "--no-summary", "--official-db-only=yes",
            "--follow-dir-symlinks=0", "--follow-file-symlinks=0", "--cross-fs=no",
            f"--max-files={self.max_files}", f"--max-filesize={self.max_file}",
            f"--max-scansize={self.max_total}", str(self.root),
        ], timeout=120)
        if result["returncode"] == 1:
            self.add("blocker", "antivirus-detection", "<target>", "ClamAV reported a detection; signature output was not copied into this report.")
            return {"available": True, "status": "detected"}
        if result["returncode"] != 0:
            self.add("high", "antivirus-error", "<target>", "ClamAV could not complete with official local signatures.")
            return {"available": True, "status": "error"}
        return {"available": True, "status": "clean"}


def binary_kind(head: bytes, path: Path) -> str | None:
    if head.startswith(b"\x7fELF"):
        return "elf"
    if head.startswith(b"MZ"):
        return "pe"
    if head[:4] in {b"\xfe\xed\xfa\xce", b"\xce\xfa\xed\xfe", b"\xfe\xed\xfa\xcf", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe"}:
        return "mach-o"
    if path.suffix.lower() in {".dylib", ".so", ".dll", ".exe", ".node"}:
        return "opaque"
    return None


def run_local(command: list[str], timeout: int = 30) -> dict[str, object]:
    env = {"PATH": "/usr/bin:/bin:/usr/sbin:/sbin", "LANG": "C", "LC_ALL": "C"}
    try:
        completed = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=env, timeout=timeout, check=False)
        return {"returncode": completed.returncode}
    except (OSError, subprocess.TimeoutExpired):
        return {"returncode": 124}


def diagnostics() -> dict[str, object]:
    tools = {}
    for name in ("spctl", "codesign", "sandbox-exec", "clamscan", "freshclam", "yara", "osv-scanner", "semgrep", "trivy"):
        tools[name] = bool(shutil.which(name))
    gatekeeper = run_local(["/usr/sbin/spctl", "--status"])["returncode"] == 0 if tools["spctl"] else False
    return {"system": platform.system(), "release": platform.release(), "gatekeeper_enabled": gatekeeper, "tools": tools}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", type=Path)
    parser.add_argument("--diagnose", action="store_true")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--max-total-bytes", type=int, default=512 * 1024 * 1024)
    parser.add_argument("--max-file-bytes", type=int, default=64 * 1024 * 1024)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.diagnose:
        report: dict[str, object] = {"schema": 1, "local_controls": diagnostics()}
        exit_code = 0
    else:
        if args.target is None:
            parser.error("target is required unless --diagnose is used")
        target = args.target.expanduser().absolute()
        report = Preflight(target, args.max_files, args.max_total_bytes, args.max_file_bytes).scan()
        exit_code = {"pass": 0, "review": 2, "fail": 3}[str(report["decision"])]
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        if args.output.exists() or args.output.is_symlink():
            raise SystemExit(f"refusing to overwrite output: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
