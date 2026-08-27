# Decisions

- Backend targets Python 3.14 instead of the spec's 3.12: only 3.14 is installed in this
  environment and no 3.12 interpreter is available to create a venv against.
- Test-database fixture uses an in-memory SQLite database (via `aiosqlite`, dev-only dependency)
  instead of a real Postgres, to avoid depending on / colliding with local Docker Postgres
  containers belonging to other projects on this machine.
- Backend directory renamed from `backend/` to `GT-backend/` at the user's request, after a
  `docker compose` project-name collision with an unrelated `companal/backend` project on this
  machine reconfigured that project's running container.
- `User` does not get `SyncMixin`/`change_seq`: Phase 6 lists only goals, commitments,
  completions and journal as synced tables, and users authenticate directly against the
  server rather than syncing peer-to-peer.
