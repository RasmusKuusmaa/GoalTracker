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
- Refresh tokens expire after a fixed 30 days (`REFRESH_TOKEN_EXPIRY_DAYS`): the spec's
  `Settings` only names one "jwt expiry", used here for access tokens.
- Pinned `bcrypt<4.1`: passlib 1.7.4's bcrypt backend detection crashes against bcrypt>=4.1,
  which removed the `__about__` module it reads for a version check.
