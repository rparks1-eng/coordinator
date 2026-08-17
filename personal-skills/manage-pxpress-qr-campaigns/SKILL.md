---
name: manage-pxpress-qr-campaigns
description: Create, revise, verify, and safely launch PXpress QR codes for business cards, flyers, signs, or other offline campaigns. Use when Codex needs to choose an owned Wix destination, configure or audit a PXpress redirect, generate branded QR and print files, test exact exports, preserve rollback, or assess whether a QR order is ready for bulk printing.
---

# Manage PXpress QR campaigns

Use the durable workflow at `/Users/brandonparks/Documents/ChatGPT/Pxpress/business-operations/marketing/qr-code-system` as the system of record. Read its `AGENTS.md`, then route through its `CONTEXT.md`. Keep campaign facts there instead of duplicating them in this skill.

## Operate in gates

1. Confirm the intended public destination and campaign tag.
2. Prefer an unused, owner-controlled `pxpressllc.com/<slug>` redirect so printed codes can survive future page changes.
3. Before changing Wix, capture the current route response and identify an independently usable rollback. Treat redirect creation, editing, and deletion as production changes that require explicit owner authorization.
4. Keep the QR square, black on white, with a four-module quiet zone and no embedded logo. Put branding outside its protected white field.
5. Generate a direct-domain fallback alongside the redirect-based primary code.
6. Decode every exact deliverable, including the composed card or flyer and a rasterized copy of each final PDF.
7. Verify the live destination with a normal mobile-style GET, the redirect chain, and the final response. Do not treat a successful HEAD request as sufficient.
8. Record hashes, dimensions, payloads, dates, results, remaining gates, and rollback instructions.

## Apply the print-readiness rule

Label digital assets verified after deterministic decoding and live navigation pass. Do not label a bulk print order ready until:

- a printed proof scans successfully on both a recent iPhone and a recent Android in ordinary lighting;
- the exact vendor-processed proof is downloaded, hashed, and decoded;
- the readable recovery URL and call to action remain visible after trim;
- the owner can still edit the redirect without access escalation.

Navigation is a customer-path requirement. Wix Analytics attribution is a separate measurement claim; validate it independently and disclose cookie-consent limitations.

## Reuse the implementation

- Destination record: `01_destination/output/destination.md`
- Generator: `_system/generate_qr_kit.py`
- Native independent decoder: `_system/verify_qr.swift`
- Pinned dependencies: `_system/requirements.lock`
- Generated deliverables: `02_generate/output/`
- Verification evidence: `03_verify/output/verification.md`

Use the pinned QR dependency in an isolated environment. If the packaged Python image or PDF libraries move, locate them through the Codex workspace dependency runtime instead of installing replacements into the user's global Python environment.

## Stop when evidence fails

Stop and report rather than publish or print when the redirect target is ambiguous, the route is occupied, the exact export fails decoding, the live path produces an unexpected chain or non-200 destination, the quiet zone is altered, a vendor reprocesses the artifact unsuccessfully, or rollback authority is unproven.
