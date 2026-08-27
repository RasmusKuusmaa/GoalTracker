# Decisions

- Backend targets Python 3.14 instead of the spec's 3.12: only 3.14 is installed in this
  environment and no 3.12 interpreter is available to create a venv against.
- Test-database fixture uses an in-memory SQLite database (via `aiosqlite`, dev-only dependency)
  instead of a real Postgres, to avoid depending on / colliding with local Docker Postgres
  containers belonging to other projects on this machine.
