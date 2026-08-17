# Artifact runtime capability map

## Objective

Make Coordinator display the real provider-produced image, HTML application, document, media file, or other artifact in its primary canvas; support conversational edits and versions; and prevent completion when no corresponding rendered artifact exists.

## Existing relevant capabilities

### Strong and directly reusable

- `imagegen`: generate and edit raster images in Codex tasks.
- Designly direction skills: composition, typography, photography, manipulation, prompting, reference memory, and visual QA.
- Documents, PDF, Presentations, and Spreadsheets: create and inspect major office artifact types.
- Expo UI, native data fetching, DOM, and web-to-native skills: implement the cross-platform surface.
- Browser, Chrome, Computer Use, and verification skills: exercise the public UI and capture visible evidence.
- Codex app-server integration: stream authenticated Codex account events and enumerate accessible apps.
- Claude Code stream JSON and MCP integration: stream Claude work and call connected tools.
- Figma and Canva skills: design creation, editing, translation, feedback, and design-to-code workflows.
- `skill-creator`, `skill-installer`, and plugin management: create, install, and inspect procedural packages.
- `icm-architect`: persist cold-startable run context and evidence.
- `guard-production-deployments`: keep provider, network, cost, and release gates explicit.

### Helpful but not sufficient by themselves

- Skills and prompts can improve routing and output instructions, but cannot transport or render bytes.
- MCP and connected apps expose tools, but do not guarantee that a tool returns a downloadable artifact.
- Image/design tools can generate media in their host environment, but Coordinator still needs an output adapter and artifact store.

## Gaps to implement in product code

1. Provider-neutral artifact envelope and lifecycle events.
2. Content-addressed local artifact storage with version lineage.
3. Provider-owned `emit_artifact` tool and bounded binary ingestion.
4. Renderer registry for image, sandboxed HTML, PDF, text/code, office previews, audio/video, and safe unknown-file fallback.
5. Active-artifact context, edit/version/undo/revert behavior.
6. Render acknowledgement tied to the exact artifact hash.
7. Deterministic blank/no-op/stale-output prevention.
8. Capability registry describing create/edit/stream/cost/auth support per provider and tool.
9. Sandboxed conversion workers for formats not directly renderable.
10. Clean-state end-to-end benchmarks through Coordinator's public composer.

These are primitive, adapter, and verification gaps—not missing prompt skills.

## Optional execution capabilities to evaluate later

- PDF.js for web PDF rendering.
- LibreOffice headless for isolated office-document preview conversion.
- A local image service such as ComfyUI when hardware and model licenses are acceptable.
- Account-included image/design connectors that return real assets.
- A paid image API only after explicit approval and a cost cap.

## First acceptance slice

1. Ask Codex through Coordinator to create an HTML artifact; display and persist it.
2. Ask Claude through Coordinator to create a PNG or PDF through an available tool; display the actual bytes.
3. Follow up with an edit; create a new version while preserving the old one.
4. Stop mid-generation; preserve the last fully rendered version.
5. Refresh the website; recover conversation and active artifact.
6. Reject a text-only "created" claim when no artifact was emitted.
7. Block network, navigation, secrets, and host access from generated HTML.
8. Record capability-missing honestly when neither provider has an image generator.
