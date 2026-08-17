# Testing protocol

## Static validation

Run the skill validator and require a successful result. Compile the checkpoint helper to catch syntax errors.

## Synthetic checkpoint test

Run `python3 scripts/test_checkpoint.py`. It must verify deterministic fingerprints, the 100-message cap, non-mutation during dry runs, unseen detection after commit, private file permissions, and the absence of message text from checkpoint state. Synthetic fixtures must contain invented text only.

## Live Messages dry run

1. Open Messages read-only with Computer Use.
2. Identify and verify the father's pinned conversation.
3. Read a small representative sample from the newest end. Do not type into the composer.
4. Verify that text, links, and visible attachment indicators can be recognized without saving them.
5. Generate an in-memory PXpress relevance summary containing no unnecessary personal details.
6. Do not open suspicious links. A safe public link may be opened read-only only if needed to verify the link path.
7. Do not commit fingerprints.
8. Refresh app state and verify no outbound bubble, reaction, draft, or other mutation was created by the test.

If macOS blocks access, report the exact permission needed and stop before changing it.

## Pass criteria

Pass only when static and synthetic tests succeed and the live dry run confirms read-only collection from the correct conversation. If the live portion is blocked or the conversation identity is ambiguous, report a partial pass rather than claiming full functionality.
