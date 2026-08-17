---
name: web-interface-refinement
description: Audit, refine, animate, and verify an existing website or web-app interface without losing its content, behavior, brand, or hosting constraints. Use for UI/UX polish, non-generic visual redesigns, responsive layout repair, interaction or animation lifecycle bugs, booking and form flows, accessibility, hover/focus states, galleries, calendars/time pickers, Wix-embedded HTML, and browser-based visual QA.
---

# Web Interface Refinement

Own the full refinement loop: inspect the running interface, preserve its truths, set a specific visual direction, implement bounded improvements, and verify the result in a browser. This is a router and quality gate; use installed specialist skills for their domains instead of duplicating them here.

## Start with the real interface

1. Read project instructions and identify the actual entry point, styling, scripts, assets, and host constraints.
2. Inspect the current rendered interface before proposing a redesign. Exercise representative navigation and one complete critical flow when safe. For a booking flow, use clearly fake data and do not submit to a live external system.
3. Capture a desktop and mobile baseline. Record content that must not change, functional invariants, known defects, and the user's explicit visual preferences.
4. Classify the request:
   - **Refine:** preserve identity, copy, behavior, and information architecture outside the requested scope.
   - **Redesign:** preserve product truth and functionality, but replace the visual system or layout.
   - **Repair:** fix a behavioral, responsive, performance, accessibility, or animation defect with minimal visual drift.
5. If the interface is not renderable, diagnose that first. Do not design from source code alone when a browser view is available.

## Route specialist work

Use the minimum specialist set needed:

- Overall visual direction or cross-page composition: `designly:designly-director`.
- Layout and hierarchy: `designly:composition-director`.
- Type pairing, hierarchy, and legibility: `designly:typography-director`.
- Existing visual-language extraction: `designly:taste-engine` or `designly:brand-intelligence`.
- Independent visual hard gate: `designly:visual-qa`.
- Motion specified in Figma: `figma:figma-implement-motion` plus the required Figma prerequisite skills.
- Direct browser exercising and screenshots: `vercel:agent-browser-verify` or the available browser-control skill.
- Wix implementation or host constraints: the relevant `wix:*` skill.

Do not invoke every specialist by default. Do not use Figma skills when no Figma artifact or Figma work is requested. The user's brief outranks any specialist's stylistic preference.

## Establish the direction

Before editing, write a compact internal direction:

- page job and primary user action;
- brand mood in 3–5 concrete adjectives;
- restrained color tokens and type roles;
- layout logic and responsive behavior;
- one memorable signature element at most;
- motion purpose and reduced-motion behavior;
- anti-references: patterns the user rejected or that make the result feel templated.

Spend visual boldness in one place. Structural devices must encode meaning. Avoid card grids, numbered labels, icon tiles, glows, gradients, oversized type, or decorative motion unless the content and brief justify them.

## Implement in bounded passes

1. Fix underlying state and event defects before layering animation.
2. Consolidate tokens and repeated interaction primitives before making many one-off edits.
3. Preserve semantic HTML, keyboard operation, focus visibility, readable contrast, and touch targets.
4. Treat motion as state communication. Load [motion-lifecycle.md](references/motion-lifecycle.md) for route/page replay, hover effects, galleries, steppers, pickers, or scroll reveals.
5. For geographic maps or spatial overlays, load [spatial-overlay-verification.md](references/spatial-overlay-verification.md). Never position geographic markers by visual percentages independently of the rendered geometry.
6. Apply the pinned interface checklist in [web-quality-gates.md](references/web-quality-gates.md) to edited surfaces.
7. Keep the pass bounded: one implementation pass, one batched desktop/mobile inspection, one correction pass, then final verification. Continue beyond that only for a concrete failed acceptance check.

## Verify the whole story

Load [verification-matrix.md](references/verification-matrix.md) and verify proportionately to risk.

At minimum:

- desktop and mobile layout;
- keyboard navigation and visible focus;
- reduced-motion behavior;
- animation replay after leaving and returning to every changed page;
- rapid repeated interaction without stale, hidden, or stuck states;
- critical flow completion, validation, review, and final action;
- no new console errors or broken assets;
- preserved copy and behavior outside scope.

For visual claims, include screenshot evidence. For behavior claims, exercise the interaction. Source inspection alone is not verification.

## Report

Lead with what is now improved and verified. Name any rejected acquisition or missing external dependency only when it affects use. Separate local visualization readiness from Wix or production readiness; do not imply that embedded HTML, Wix-native components, or live backend integrations are identical without testing them in that environment.

## Safety

- Do not fetch live design rules during a refinement run. Use the pinned local references.
- Do not install packages or enable hooks just to improve appearance.
- Do not send source, screenshots, or user data to an external service without authorization.
- Do not change production hosting, Wix configuration, credentials, or public content unless the user explicitly requests that separate action.
- Honor `prefers-reduced-motion`; do not make content depend on animation completing.
