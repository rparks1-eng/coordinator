#!/usr/bin/env python3
"""Resolve a public YouTube video or creator videos page to a canonical video URL."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse

YOUTUBE_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com", "youtu.be", "www.youtu.be"}
VIDEO_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]{11}")
CHANNEL_PREFIXES = {"channel", "c", "user"}


class ResolutionError(RuntimeError):
    """The input cannot be safely resolved to a public YouTube video."""


def video_id_from_url(url: str) -> str | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    host = (parsed.hostname or "").lower().rstrip(".")
    parts = [part for part in parsed.path.split("/") if part]
    candidate: str | None = None
    if host in {"youtu.be", "www.youtu.be"} and parts:
        candidate = parts[0]
    elif host in {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            candidate = urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in {"shorts", "embed", "live"}:
            candidate = parts[1]
    return candidate if candidate and VIDEO_ID_PATTERN.fullmatch(candidate) else None


def canonical_video_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def channel_videos_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme not in {"http", "https"} or host not in YOUTUBE_HOSTS - {"youtu.be", "www.youtu.be"}:
        raise ResolutionError("Provide a public YouTube video URL or creator/channel page URL.")
    parts = [part for part in parsed.path.split("/") if part]
    channel_parts = parts[:-1] if parts and parts[-1] == "videos" else parts
    if not channel_parts or (not channel_parts[0].startswith("@") and channel_parts[0] not in CHANNEL_PREFIXES):
        raise ResolutionError("Provide a public YouTube creator or channel URL ending in /videos.")
    return urllib.parse.urlunparse(("https", "www.youtube.com", "/" + "/".join(channel_parts) + "/videos", "", "", ""))


def _entry_video_id(entry: dict) -> str | None:
    candidate = str(entry.get("id") or "")
    if VIDEO_ID_PATTERN.fullmatch(candidate):
        return candidate
    url = str(entry.get("url") or entry.get("webpage_url") or "")
    return video_id_from_url(url) or (url if VIDEO_ID_PATTERN.fullmatch(url) else None)


def resolve_youtube_videos(url: str, count: int = 10) -> list[dict[str, object]]:
    """Resolve a direct video or the newest public uploads from a creator page."""
    if count < 1:
        raise ResolutionError("--count must be 1 or greater.")
    direct_video_id = video_id_from_url(url)
    if direct_video_id:
        return [{"input_url": url, "input_kind": "direct_video", "selection": "direct", "video_id": direct_video_id, "video_url": canonical_video_url(direct_video_id)}]
    videos_url = channel_videos_url(url)
    try:
        from yt_dlp import YoutubeDL
    except ImportError as error:
        raise ResolutionError("Channel-page resolution requires yt-dlp. Install it with: python3 -m pip install --user yt-dlp") from error
    options = {"quiet": True, "no_warnings": True, "skip_download": True, "extract_flat": "in_playlist", "playlistend": count, "ignore_no_formats_error": True}
    try:
        with YoutubeDL(options) as downloader:
            playlist = downloader.extract_info(videos_url, download=False)
    except Exception as error:
        raise ResolutionError(f"Could not retrieve the public creator videos page: {error}") from error
    entries = list((playlist or {}).get("entries") or [])
    resolved: list[dict[str, object]] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            continue
        video_id = _entry_video_id(entry)
        if not video_id:
            continue
        resolved.append({"input_url": url, "input_kind": "creator_videos_page", "selection": f"upload_index_{index}", "video_id": video_id, "video_url": canonical_video_url(video_id), "title": entry.get("title"), "channel": entry.get("channel") or entry.get("uploader")})
    if not resolved:
        raise ResolutionError("YouTube returned no usable public video IDs from this creator page.")
    return resolved


def resolve_youtube_video(url: str, index: int = 1) -> dict[str, object]:
    """Resolve one direct video or one selected creator upload for existing callers."""
    videos = resolve_youtube_videos(url, index)
    if video_id_from_url(url):
        return videos[0]
    if len(videos) < index:
        raise ResolutionError(f"The creator videos page has no public upload at index {index}.")
    return videos[index - 1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resolve a public YouTube video or creator videos page.")
    parser.add_argument("url", help="public YouTube video URL or creator/channel videos URL")
    parser.add_argument("--index", type=int, help="creator upload position, newest first")
    parser.add_argument("--count", type=int, help="return this many creator uploads, newest first")
    parser.add_argument("--json", action="store_true", help="emit resolution metadata as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.index and args.count:
            raise ResolutionError("Use either --index or --count, not both.")
        result = resolve_youtube_videos(args.url, args.count) if args.count else resolve_youtube_video(args.url, args.index or 1)
    except ResolutionError as error:
        print(str(error), file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    elif isinstance(result, list):
        print("\n".join(str(item["video_url"]) for item in result))
    else:
        print(result["video_url"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
