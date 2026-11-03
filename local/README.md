# Local development

Requires Go 1.27.3+, Docker and Docker Compose v2. From the repository, run:

```sh
./local/run-dev.sh
```

This starts PostgreSQL 12.6 in Docker, waits for it to become healthy, builds
`local/bin/ponylib`, and runs the web UI locally at http://127.0.0.1:55387 with debug mode
and template hot reload. Database migrations run automatically.

PostgreSQL is available at `127.0.0.1:55432`, with database/user `ponylib` and
password `ponylib-dev`. It binds only to localhost and stores data in a Docker
volume. Ctrl+C stops the local service; the database keeps running.

To pass a different command or web UI options:

```sh
./local/run-dev.sh scan /path/to/library
./local/run-dev.sh web-ui --dev-mode --debug --port 8080
```

Set `DEV_DB_PORT` to change the PostgreSQL host port. Set `FTS_LANGUAGE` before
the first run to choose the full-text search language (default: `english`); keep
it the same on subsequent runs. The script sets `DATABASE_URL` for the dev database.

```sh
DEV_DB_PORT=55433 FTS_LANGUAGE=russian ./local/run-dev.sh
```

Stop PostgreSQL with `docker compose -f local/compose.dev.yml down`. To delete the dev
database as well, use `docker compose -f local/compose.dev.yml down -v`.
