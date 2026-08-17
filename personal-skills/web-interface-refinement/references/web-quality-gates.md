# Web quality gates

Apply these checks to edited surfaces and their shared primitives. The brief and product truth win when a stylistic rule conflicts, but accessibility and operability remain gates.

## Semantics and accessibility

- Use semantic HTML before ARIA: buttons for actions, anchors for navigation, labels for controls.
- Give icon-only controls accurate accessible names; hide decorative icons from assistive technology.
- Preserve logical heading order and include a skip link when the document has repeated navigation.
- Make every flow keyboard-operable with visible `:focus-visible` treatment.
- Use `aria-live="polite"` for asynchronous validation, confirmations, and status changes.
- Keep mobile touch targets at least 44 by 44 CSS pixels where practical.
- Never disable browser zoom.

## Forms and booking flows

- Inputs need labels, meaningful names, suitable `type`, `inputmode`, and `autocomplete` values.
- Keep labels and checkbox/radio controls inside one continuous hit target.
- Never block paste.
- Show errors next to the field, associate them with the control, and focus the first invalid field after submit.
- Disable submit only after a real request begins; expose progress and recovery.
- Use specific action labels that match the resulting status message.
- Preserve entered values across validation errors and backward step navigation.
- Date, time, address, guest, luggage, and service rules must be enforced in logic, not only visually disabled.

## Focus and overlays

- Do not remove outlines without a visible replacement.
- Use `:focus-within` for compound controls such as wheel-style time pickers.
- Dialogs and popovers manage initial focus, trap focus when modal, close with Escape, and return focus to the invoker.
- Prevent background interaction only while a true modal is open.

## Motion

- Honor `prefers-reduced-motion` and keep all content accessible without animation.
- Animate compositor-friendly properties and name transitions explicitly.
- Make animation interruptible and deterministic across repeated navigation.
- Set intentional transform origins; wrap SVG parts in a group when transforming them.

## Typography and content

- Use a deliberate display/body hierarchy with readable measures and line height.
- Balance headings and prevent widows where supported.
- Use tabular numerals for aligned times, prices, counts, and comparisons.
- Handle empty, short, average, and very long content without overflow.
- Give flex/grid children `min-width: 0` when text must shrink or truncate.
- Keep UI copy active, specific, consistent, and written from the rider's point of view.
- Error text states what happened and what to do next.

## Images and media

- Provide accurate `alt` text or empty alt text for decorative media.
- Set explicit dimensions or aspect ratios to prevent layout shift.
- Prioritize the first meaningful hero image; lazy-load media below the fold.
- Verify crop, focal point, resolution, and loading state at desktop and mobile sizes.

## Layout and touch

- Prefer CSS grid/flex layout over JavaScript measurement.
- Test safe areas, horizontal overflow, browser zoom, and narrow screens.
- Set touch behavior intentionally and contain overscroll in sheets, drawers, and modals.
- Do not make hover the only way to reveal essential information or actions.

## Theme, locale, and state

- Declare the correct `color-scheme` and match browser theme color to the page.
- Give native selects explicit foreground and background colors in dark mode.
- Format dates, times, numbers, and currency with locale-aware APIs.
- Make meaningful navigable state linkable when the host architecture supports it.
- Confirm destructive actions; do not execute them on a single accidental click.

## Performance and resilience

- Avoid layout reads during render and repeated read/write interleaving.
- Decode or preload images that must switch instantly.
- Avoid expensive per-keystroke work in controlled inputs.
- Preload only critical fonts and use `font-display: swap`.
- Verify with missing images, slow image decoding, long text, rapid input, and empty data.

## Provenance

Adapted from Vercel Labs' Web Interface Guidelines, pinned at commit `4e799d45c17aec1498c269287a83b9dba22b966b` (MIT License, copyright 2025 Vercel Labs). The active reference is local and intentionally removes the upstream skill's live-fetch behavior. Primary upstream: `https://github.com/vercel-labs/web-interface-guidelines`.
