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
- `Goal` (the first model using `SyncMixin`) fails to insert under the sqlite test fixture:
  SQLite has no equivalent to Postgres's `Identity()`/bigserial for a non-primary-key column, so
  `change_seq` never gets populated. Added a test-only `before_insert` event in
  `tests/conftest.py` that assigns `change_seq` client-side when the dialect is sqlite; Postgres
  keeps using the real server-generated identity untouched.
- `Commitment.journal_id` has no database FK constraint yet: the `journals` table doesn't exist
  until Phase 5. It's a plain nullable UUID column for now; ownership/existence validation is
  application-level in the schema/service layer (same as it will be once Phase 5 adds the FK).
- `POST /commitments` validates `goal_id` ownership (goals already exist) but not `journal_id`
  ownership: there is no `journals` table to check against until Phase 5. `journal_id` is
  accepted as-is for now; Phase 5 will add the same ownership check used for `goal_id`.
- `app/schemas/journal_entry.py` has no pydantic validator enforcing value-vs-kind rules: a
  journal entry's `journal_id` is the only link to its kind, which lives on the `Journal` row and
  requires a database lookup unavailable at schema-parse time. That check lives in the upsert
  service function once the journal is loaded, mirroring how completion-vs-commitment-type
  validation was done in `services/completions.py` rather than `schemas/completion.py`.
- Drift local tables store enum-like fields (goal status, commitment type/cadence/comparator,
  journal kind, completion status) as plain `TextColumn`s, not Drift type converters: keeps the
  schema simple for v1; Dart-side code converts to/from the app's enum types at the DAO
  boundary. Numeric fields that are `Decimal` on the backend (`target_value`, completion/journal
  `value`) are stored as `RealColumn` locally — full decimal precision isn't needed for a value
  that's only ever displayed and compared client-side, and Drift has no native decimal type.
- Completions/JournalEntries drift tables enforce `(commitmentId, localDate)` /
  `(journalId, localDate)` uniqueness with a plain (non-partial) `uniqueKeys` override, unlike
  the backend's partial index (`WHERE deleted_at IS NULL`): the DAOs always find-and-update the
  existing local row in place for a given key (including re-clearing `deletedAt` on untick/retick)
  rather than inserting a new row after a soft delete, so a plain unique index is sufficient and
  SQLite's partial-index support isn't needed locally.
- `flutter_riverpod` bumped from `^2.6.1` to `^3.4.2`: `riverpod_generator` (needed as a dev
  dependency) only resolves against Riverpod 3.x; pinning `riverpod_generator` back to an old
  2.x-compatible release seemed worse for a brand-new v1 project than starting on current
  Riverpod.
- Flutter app org set to `com.goaltracker` (`flutter create --org com.goaltracker`): the spec
  does not name a real org/domain, and this project has no distribution identity yet. Package
  name kept as the default derived from the `app/` directory name.
- Sync rows (`app/schemas/sync.py`) omit `change_seq`: the cursor is opaque to the client, and
  `change_seq` is a server-internal ordering column, not app data. The cursor itself is planned
  as a per-entity map of last-seen `change_seq` values (JSON-encoded into the opaque string),
  since each entity's identity sequence advances independently — a single scalar cursor value
  could not resume each entity type correctly on its own. `SyncPullResponse.has_more` is one
  flag for the whole response (true if any entity type was capped), not per entity: the client
  only needs to know whether to call pull again, not which entity type was capped.
