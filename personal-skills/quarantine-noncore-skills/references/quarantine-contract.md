# Quarantine contract

Quarantine is a reversible discovery change, not deletion. It applies only to
`~/.codex/skills/<exact-folder>`, never `.system`, shared-agent, plugin, or
symlink paths. The manifest binds the validated core-profile hash, source root,
quarantine root, exact direct folder names, and a SHA-256 tree hash for each
folder. Restore means moving the recorded folder back and revalidating its
hash.
