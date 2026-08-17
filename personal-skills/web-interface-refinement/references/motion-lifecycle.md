# Motion lifecycle

Use motion to clarify hierarchy, continuity, state, and response. Avoid ambient movement that competes with the task.

## State model

Treat every animated surface as a small state machine:

`inactive → entering → active → leaving → inactive`

Re-entry must create a fresh transition. Do not leave permanent inline styles, stale `data-*` flags, observer state, timers, or classes that prevent the next entry.

For a single-page site:

1. On route/tab leave, cancel active animations and remove temporary entering/leaving classes.
2. Hide the old page only after its exit state is complete or immediately when reduced motion is active.
3. Activate the new page, reset its reveal targets to the initial state, then start entry on the next animation frame.
4. Reconnect scroll observers for the active page and disconnect observers for hidden pages.
5. When navigating back, repeat the same lifecycle rather than relying on a one-time page-load observer.

Prefer a single owner for page transitions. Event handlers may request a transition, but they must not independently manipulate the same classes and timers.

## Interaction rules

- Animate `transform` and `opacity` when possible.
- Name transitioned properties; never use `transition: all`.
- Make motion interruptible. A second click, swipe, or route change cancels or reverses cleanly.
- Keep controls operable during decorative motion; disable only for a real transactional constraint.
- Do not animate text scale directly when it harms rasterization; animate a wrapper.
- Avoid bounce and elastic easing for a premium interface unless the brand explicitly calls for playfulness.
- Default durations: 120–180 ms for direct control feedback, 180–280 ms for local state changes, and 300–500 ms for page/section entrances. Use one easing family across the site.

## Galleries and image switches

- Preload adjacent images or decode the destination image before fading the source.
- Keep one authoritative selected index.
- Ignore stale image-load completions by matching them to the latest requested index.
- Never leave both panels hidden if a request is interrupted.
- Update selected semantics (`aria-selected`, labels, or tabs) synchronously with the user's action.

## Scroll reveals

- Reveal only meaningful groups, not every label and icon.
- Hidden initial states must exist only when JavaScript is available.
- Reinitialize when the page becomes active again.
- If an element is already in view on entry, reveal it immediately or during the page entrance rather than waiting for scroll.

## Reduced motion

Under `prefers-reduced-motion: reduce`:

- remove parallax, large translation, continuous movement, and scroll-linked motion;
- reduce duration to near-zero or use a brief opacity change;
- show all content and keep the same final states and functions;
- retain focus, hover contrast, and non-motion feedback.

## Verification stress cases

- Enter, leave, and re-enter each page three times.
- Change tabs or gallery images rapidly ten times.
- Interrupt a page entrance with another navigation action.
- Resize across a responsive breakpoint during and after a transition.
- Repeat with reduced motion enabled.
- Confirm no timers, observers, or classes accumulate after each cycle.
