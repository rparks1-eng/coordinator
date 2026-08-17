# PXPress Wix draft acceptance checklist

- [ ] Local HTML and embedded widget payload hashes match.
- [ ] Target is `Pxpress Llc` site ID `c34a9507-d52b-49f7-bb59-d3cbff227b7b`, not `Dev Sitex`.
- [ ] `wix dev-site current` and Wix dev output both show the exact target site ID.
- [ ] Unit tests pass and Wix build completes.
- [ ] Desktop routes and booking flow render.
- [ ] iPhone home, menu, and booking form have no horizontal overflow.
- [ ] Calendar stays open when changing months.
- [ ] Time picker uses 15-minute intervals.
- [ ] Wix desktop preview shows the current HTML revision.
- [ ] The user-requested browser shows the actual target site's editor/preview; another site's preview does not count.
- [ ] Wix mobile custom-element host has enough height.
- [ ] Pickup, destination, and return suggestions populate for a generic query.
- [ ] Ohio suggestions rank before out-of-state matches when relevant.
- [ ] Nationwide fallback remains available.
- [ ] Preview version ID recorded; production version ID unchanged.
- [ ] No release or publish action occurred.
