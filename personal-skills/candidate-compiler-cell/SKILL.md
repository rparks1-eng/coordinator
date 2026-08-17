---
name: candidate-compiler-cell
description: Prepare one evidence-traceable inactive skill-update candidate for a selected target. Use when a coordinator work order supplies verified knowledge, one exact target SKILL.md path, and a separate inactive root. Never modify active skills or install candidates.
---

# Candidate Compiler Cell

First read `$coordinator-core` and its work-order reference. Require one exact target, baseline hash, knowledge paths, and inactive root; otherwise return `needs-human`.

Invoke `$system-update` only for that declared candidate. Preserve its validation result and return the required host report. A candidate is non-active and never delivery authority.
