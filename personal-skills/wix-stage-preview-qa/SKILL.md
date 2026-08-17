---
name: wix-stage-preview-qa
description: Stage an existing Wix CLI app or custom-element website into a dedicated Wix development site or preview version without publishing, then verify exact embedded HTML, desktop and iPhone behavior, Wix editor sizing, and address-autocomplete bridges. Use for draft commits, Wix preview QA, responsive regressions, embedded HTML synchronization, Ohio-prioritized address search, and safe pre-release handoff.
---

# Wix Stage & Preview QA

## Objective

Move an exact local website revision into Wix draft/preview state, prove what was uploaded, test the real Wix-rendered experience, and leave production unchanged.

## Required companion skills

Read and follow `guard-production-deployments` and the applicable Wix skill before making changes. For visual inspection, also use `web-interface-refinement` and a browser-control skill.

## Workflow

1. Bind the Wix account, app ID, dedicated development site ID, production site ID, current version IDs, and exact source/widget paths.
   - Write the user-named target site and its verified site ID as the acceptance target.
   - Reject any similarly named development site, preview site, or app-level preview as a substitute.
2. Confirm the CLI development target is a non-production site. Never infer this from a site name.
3. If the widget embeds compressed HTML, run `scripts/sync_embedded_html.mjs` and record matching SHA-256 hashes.
4. Run the project's tests and Wix build. Separate blocking build failures from unrelated type-check debt.
5. Test the local source at desktop and iPhone-sized viewports. Exercise navigation, mobile menu, route transitions, booking steps, calendar month changes, time selection, horizontal overflow, and final actions.
6. Create a Wix preview version with `wix preview`. Do not run `wix release` and do not click Publish.
7. Use `wix dev` only against the dedicated development site. Open Wix Preview and inspect the nested rendered site, not just the editor chrome.
   - If the user explicitly requests the real site's unpublished draft, select that exact site ID before `wix dev`, then require the CLI's `Current development site` output to match it.
8. Verify desktop and mobile Wix previews. Measure the custom-element host. If mobile content is clipped while local responsive QA passes, diagnose Wix element dimensions separately from app CSS.
9. Exercise address search with a generic, non-sensitive address. Verify suggestions appear, Ohio results sort first when relevant, and nationwide fallback remains available. Do not submit a real booking.
10. Stop temporary servers. Record evidence and confirm production state is unchanged.

## No-false-completion gate

Do not say the website was committed, staged, or updated to the requested Wix site unless all three are true:

1. The verified target site ID equals the user-named site.
2. Wix reports that same site ID as the current development target and confirms the manifest update.
3. The requested browser shows the actual target site's editor or preview with the current website revision.

If browser verification is unavailable, report the Wix synchronization separately and ask for the narrow browser handoff needed to complete visual proof. Never replace target-site evidence with a different development site's successful preview.

## Acceptance evidence

- Exact source and embedded payload hashes match.
- Project tests and Wix build pass, or remaining failures are explicitly classified.
- Desktop and iPhone local views have no horizontal clipping.
- Wix preview version ID is recorded.
- Production version ID is unchanged and nothing was published.
- Address suggestions populate in the staged Wix experience.
- Any editor-only sizing issue has a concrete Wix-layout fix and retest plan.

## Safety rules

- Treat preview, development, and production as separate targets.
- A preview version is not a release. A synchronized dev manifest is not a published site.
- Preserve the previous production version as the rollback anchor.
- Never install the preview app into the production site during verification.
- Browser-based Wix editor mutations require confirmation unless explicitly authorized for that exact change.
- Use test addresses and stop before sending forms, emails, payments, or bookings.

## PXPress-specific verification

Test both Wix Atlas and its nationwide fallback path. Confirm the Northeast Ohio origin/Ohio extent ranking logic remains present, but do not claim it works until suggestions are observed in the staged Wix runtime. If the mobile Wix host is proportionally scaled to a short height, fix the Wix editor element height or move to a full-page extension; do not hide the problem with iframe CSS.

## Learning loop

After each run, convert repeated failure modes into a deterministic check. Add only checks that prevent an observed class of defect, and keep production mutations behind the release guard.
