---
name: resolve-youtube-video
description: Resolve a public YouTube creator videos page or a direct video URL to canonical public video URLs. Use when a task needs the newest upload from a channel /videos page, a selected older upload, a batch of newest uploads, or normalized video links before another YouTube workflow.
---

# Resolve YouTube video

Resolve the input before reading, summarizing, or extracting from a video.

1. Accept only public `youtube.com` or `youtu.be` URLs. Do not bypass access controls or use authenticated browser state.
2. Run the resolver. A direct video URL is normalized without a network request. A creator or channel page resolves to its newest listed upload by default.

   ```bash
   python3 ~/.codex/skills/resolve-youtube-video/scripts/resolve_youtube_video.py "YOUTUBE_URL"
   ```

3. Use `--index N` to select the Nth upload displayed by the channel page, where `1` is the newest. Use `--count N` to return the newest N uploads. Use `--json` when a consuming script needs resolution metadata.
4. Pass the resolved video URL—not the channel URL—to downstream video tooling. Report a clear error if YouTube supplies no public video entry.

The resolver requires the installed Python `yt-dlp` package only for channel-page resolution.
