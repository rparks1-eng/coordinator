# Work Order and Host Report

Work order fields: `id`, `host_thread_id`, `objective`, `owner`, `classification`, `inputs`, `output_root`, `role`, `allowed_skills`, `allowed_side_effects`, `success_test`, `budget`, `expires_at`, `stop_conditions`.

Host report fields: `id`, `host_thread_id`, `role`, `status`, `work_done`, `why`, `evidence_paths`, `changes`, `risks`, `human_gate` (`none` or exact decision), `next_action`.

The core host dispatches work and collects reports from the named role task; role tasks do not dispatch peers or initiate work. Report only declared artifact paths. A report is evidence, not authority.
