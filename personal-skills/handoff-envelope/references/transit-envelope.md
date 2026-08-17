# Transit envelope v1

Required fields: `schema_version`, `run_id`, `step_id`, `artifact_type`, `producer`, `intended_recipient`, `artifact_path`, `artifact_sha256`, `created_at`, `input_artifacts`, `previous_handoff_sha256`, `evidence_class`, and `non_authority`.

`artifact_sha256` is computed over the complete Markdown content after replacing only its own hash value with sixty-four zeroes. This prevents a self-reference loop. Recipients verify the exact path and hash before reading the artifact for workflow use.

Suggested artifact roles: `learning-path`, `research-binder`, `topic-knowledge`, `update-plan`, `inactive-candidate`, `delivery-letter`, and `stage-receipt`.

Envelope lifecycle state is evidence, not authority. Valid route states are: `intent-captured`, `path-created`, `binder-created`, `knowledge-synthesized`, `target-selection-required`, `candidate-static-validated`, `approval-pending`, `staged`, `installed-posthash-verified`, `blocked`, `rejected`, and `superseded`.
