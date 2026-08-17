# Spatial overlay verification

Use this reference whenever a web interface places cities, airports, service areas, routes, counties, floor-plan hotspots, or other real-world points over geometry.

## Coordinate integrity gate

1. Identify an authoritative geometry source and authoritative point coordinates. Record their coordinate reference systems and vintage.
2. Convert the geometry and every overlay point through one explicit projection and one shared fit transform. Do not fit points separately and do not use hand-tuned percentages as geographic coordinates.
3. Keep the projected anchor at the true location. Offset only its label, tooltip, or leader line when resolving visual collisions.
4. Bind generated output to the source and transform. Prefer a deterministic generator over manually copied path data.
5. Reject the pass if the rendered anchor cannot be traced back to its source longitude/latitude or source-space coordinate.
6. Render geometry and geographic anchors in the same native coordinate layer whenever possible. An SVG map uses SVG markers; a canvas map uses canvas markers. HTML/CSS overlays or `foreignObject` markers require a screen-space equality test at every target viewport before they may pass.
7. Keep projection transforms on a stable parent layer. Entry, hover, and selection animations must run on a nested visual child so CSS animation cannot replace the anchor's transform attribute or matrix.

## Visual verification gate

- Capture the full map at desktop and mobile sizes.
- Measure rendered anchor centers for every edited marker and compare them to the same SVG or canvas transform used by the geometry.
- Run a rectangle collision check across markers, city dots, and labels. A deliberate overlap needs a documented reason; accidental overlaps fail.
- Check geographic ordering: north/south and east/west relationships must agree with source coordinates.
- Exercise every interactive marker by pointer and keyboard. The selected detail must match the visible anchor.
- Measure the marker before and during hover. A requested upward motion passes only when its rendered y-position decreases; checking the keyframe text alone is insufficient.
- When close locations cannot be legible at the current scale, enlarge the map or use a leader line/inset. Never move the anchor to make the composition easier.

## Failed patterns

- CSS `left`/`top` percentages guessed from a screenshot.
- Applying a new `viewBox` or crop without rerunning the point projection.
- Verifying only that a marker is clickable while ignoring whether it is geographically correct.
- Treating a visually plausible state outline as proof that city or airport coordinates are correct.
- Increasing icon size until nearby but distinct locations overlap.
- Animating the same element that carries the geographic transform, allowing `transform` keyframes to silently move every anchor.
- Mixing an SVG map with absolutely positioned HTML markers and treating matching source numbers as rendered alignment proof.

## Completion evidence

Report the geometry source, point source, projection/fit method, collision result, desktop/mobile screenshots, and interaction result. “Looks aligned” is not sufficient evidence.
