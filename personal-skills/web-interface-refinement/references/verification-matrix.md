# Verification matrix

Choose checks based on what changed, but never claim a visual or behavioral result without exercising it.

| Area | Required evidence |
| --- | --- |
| Visual hierarchy | Desktop and mobile screenshots; headings, actions, and content order are immediately clear. |
| Responsive layout | Narrow mobile, wide mobile/tablet, and desktop; no clipping, accidental horizontal scroll, or detached overlays. |
| Navigation | Every changed nav item and CTA reaches the intended surface; browser Back behavior remains coherent. |
| Motion lifecycle | Page/tab entry replays after leave/return; rapid switching cannot leave content hidden, stale, or doubled. |
| Reduced motion | Same content and functions with large movement removed and no animation-dependent visibility. |
| Keyboard | Logical tab order, visible focus, Enter/Space behavior, Escape for overlays, focus restoration. |
| Forms | Labels, required states, inline errors, first-error focus, preserved values, bounds, and conditional fields. |
| Critical flow | Start to final action using fake data; review content matches inputs; final button fires exactly once. |
| Media | Correct image per selector, stable dimensions, intentional crop, graceful decode/loading behavior. |
| Runtime | No new console errors, unhandled rejections, missing assets, or duplicate event execution. |
| Copy preservation | Protected quotes, owner text, legal terms, factual claims, and user-supplied wording remain unchanged. |
| Host compatibility | Test in the actual host or clearly state what remains unverified for Wix, iframe, CSP, or native components. |

## Animation replay protocol

For every changed page:

1. Navigate in and wait for completion.
2. Navigate to a different page before the first page's animation completes.
3. Return immediately, then return again after completion.
4. Repeat with keyboard navigation.
5. Repeat with reduced motion.
6. Confirm final styles, focus, active navigation state, observers, and event counts are correct.

## Booking-flow protocol

Use fake information and cover each conditional branch touched by the change:

- service selection and preselection;
- one-way, round-trip, or hourly differences;
- minimum duration and unavailable time rules;
- outbound/return chronological validation;
- conditional address, airport, luggage, oversized-item, event, or after-hours fields;
- traveler count bounds;
- review content and back navigation;
- final action once, including loading, confirmation, and recoverable failure states.

## Finish criteria

Pass only when all applicable checks have direct evidence. A local HTML pass does not establish Wix-native integration or production backend behavior. Record those as separate gates instead of weakening the result.
