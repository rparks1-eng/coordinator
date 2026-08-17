---
name: educator
description: Research current, trustworthy videos, articles, and primary source materials, then create and save a tailored learning path. Use when a user wants to learn a topic or skill, wants a study curriculum, asks for educational resources, or needs a guided path from a stated level to a practical goal.
---

# Educator

Create one new learning-path file for every invocation. Research before drafting; do not reuse an old resource list as if it were current.

## Establish the learning brief

Extract the topic, intended outcome, learner level, available time, preferred format, constraints, and target date from the current prompt. If a missing fact would not materially change the path, state a reasonable default: beginner, four weeks, and four to six hours per week. Ask one focused question only when the missing fact changes the route substantially.

## Research and verify

Use internet search on every invocation. Search for the current topic plus the learner's goal; include official documentation, standards bodies, universities, government agencies, original research, professional associations, and reputable publishers as appropriate.

Open every source selected for the path and verify that it is reachable, directly relevant, and matches its claimed format. Prefer primary sources for factual, technical, medical, legal, financial, or changing material. Add high-quality explanatory articles only where they improve comprehension. For videos, prefer official educators, universities, recognized professional organizations, or well-established practitioners with material that directly supports a stage of the path.

Avoid search-result snippets, SEO listicles, anonymous pages, unsourced claims, expired links, and videos whose title or description does not establish relevance. Mark paywalled, sign-in-required, or region-limited resources clearly; offer a free alternative when practical. For high-stakes topics, include an educational-use disclaimer and do not substitute the path for professional advice.

## Create the path file

Run `scripts/create_learning_path.py --topic "<topic>"` from the target workspace before writing. It creates and reserves a unique file under `learning-paths/`; pass `--directory <path>` only when the user specifies a different output location. Never overwrite a prior learning path.

Populate the created file with:

1. Title, creation date, learner brief, assumptions, and a measurable completion outcome.
2. Prerequisites and a short diagnostic or starting exercise.
3. Ordered phases or weeks. For each phase, state objective, estimated time, learn/practice activities, one or more selected resources, and a checkpoint.
4. A concise resource library grouped as videos, trusted articles, and primary/verified materials. Link every item; include the publisher/creator, format, and why it is in the path.
5. A capstone or assessment with clear evidence of completion, plus a next-step option.
6. A sources-verification note with the research date and any access limitations.

When this path enters a governed learning loop, use `$handoff-envelope` after writing to stamp the exact file as `learning-path` for `learning-path-binder`. Preserve the controller’s run ID and do not treat the stamp as approval or as a request to execute downstream skills.

Fit the plan to the learner's time budget. Favor active practice, retrieval, building, and feedback over passive watching. Keep the resource list selective: each link must serve a named purpose in the sequence.

## Finish

Confirm the exact saved path and summarize the recommended first action. Report any assumption, inaccessible source, or limitation plainly.
