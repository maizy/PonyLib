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

## Integration tests

Run from the repository root:

```sh
./integration-test.sh
POSTGRES_VERSION=17 ./integration-test.sh
POSTGRES_VERSION=18 ./integration-test.sh
```

The runner starts a disposable PostgreSQL Docker container (12.6 by default),
waits for readiness, and removes it on exit. It uses a random localhost port and
keeps the development database separate. Go and Docker are required.

To use an existing development or disposable database, set
`PONYLIB_TEST_DATABASE_URL`; Docker is then unnecessary. CI uses this mode for
its PostgreSQL 12, 17 and 18 services:

```sh
PONYLIB_TEST_DATABASE_URL='postgres://ponylib:ponylib-dev@127.0.0.1:55432/ponylib?sslmode=disable' \
  ./integration-test.sh
```

The database user needs permission to create schemas. Additional Go test arguments
can be passed to the script, for example `-run TestLibrary`. Test names and step
logs are printed by default. Integration tests use the `integration` build tag
and are excluded from the regular `./test.sh` run.
