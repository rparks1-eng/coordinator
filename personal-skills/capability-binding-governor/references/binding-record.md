# Capability Binding Record

Required fields: `binding_id`, `capability_path`, `capability_sha256`, `proposed_owner` (`core|cell:<name>|shared-on-demand|unassigned`), `owner_alternatives`, `purpose`, `trigger`, `inputs`, `outputs`, `forbidden_effects`, `evidence_paths`, `motivating_cases`, `held_out_neighbor`, `evaluation_status`, `lifecycle` (`proposed|tested|approved|active|deprecated|quarantine-proposed|retired`), `human_gate`, `rollback`, `created_at`.

Lifecycle: proposal → owner comparison → independent evaluation → human decision → inactive candidate → validation → optional approved activation. Retirement: active → deprecated → replacement/rollback test → exact quarantine proposal → optional approved recoverable action.

`core` is reserved for capabilities needed across held-out routes. A binding record is a proposal, never activation or removal authority.
