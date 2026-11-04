# Repository guide

PonyLib v2 is a Go application for scanning FictionBook (FB2) libraries and
searching them through a CLI and web UI. The module is `dev.maizy.ru/ponylib`.

## Layout

- `cmd/ponylib`: main CLI; Cobra commands live in `cmd/ponylib/cmd`.
- `cmd/ponylib-parser`: standalone metadata parser CLI.
- `fb2_parser`: metadata types, formatting and genre definitions.
- `internal/fb2`: XML parsing, annotation conversion and filename generation.
- `fb2_scanner`: directory, file and ZIP scanning, including symbolic links.
- `fb2_scanner/resource`: resource identifier encoding and decoding.
- `ponylib_app/db`: pgx database access and embedded SQL migrations.
- `ponylib_app/search`: PostgreSQL full-text search queries.
- `ponylib_app/web`: Gin handlers, embedded templates and static assets.
- `local`: local startup scripts, Compose configuration, documentation and ignored binaries.
- `docs/docker-compose`: deployment example; keep separate from local development tooling.

## Build and run

Use the Go version declared in `go.mod` (currently 1.27.3). Run commands from the
repository root unless otherwise stated.

```sh
./build.sh                  # Build both CLIs into bin/ with version metadata
./local/run-dev.sh          # Start Docker PostgreSQL, build and run the local web UI
./local/run-dev.sh migrate  # Build and run a different CLI command against the dev DB
```

The local web UI listens on `http://127.0.0.1:55387`. PostgreSQL binds to
`127.0.0.1:55432`; `DEV_DB_PORT` overrides that port. See `local/README.md` for
credentials and options. Stop the dev database with
`docker compose -f local/compose.dev.yml down`; this preserves its data volume.

## Validation

For Go changes, format touched files with `gofmt` and run:

```sh
go test ./...
go vet ./...
go build ./...
```

Use `go test -race -timeout 2m ./...` for concurrency changes. Integration tests
live in `integration-tests/` behind the `integration` build tag. Run them with
`./integration-test.sh`: it starts and removes a disposable PostgreSQL 12.6 Docker
container, or uses `PONYLIB_TEST_DATABASE_URL` when set. `POSTGRES_VERSION` selects
another Docker image version. See `local/README.md` for details.

The integration tests create and remove isolated schemas. Use a development or
disposable database. CI runs unit tests and vet on Linux and macOS and integration
tests against PostgreSQL 12, 17 and 18. `test.sh` runs unit tests and go vet.

For local tooling changes, check `bash -n local/run-dev.sh` and
`docker compose -f local/compose.dev.yml config --quiet`, then exercise the relevant
startup path. Documentation-only changes do not require Go tests.

## Change conventions

- Follow existing package boundaries and use idiomatic Go. Wrap errors with `%w`
  when retaining the underlying error matters.
- Preserve metadata JSON, resource identifiers, CLI behavior and search semantics
  unless the task calls for changing them. Add regression tests for behavior changes.
- Scanner changes must preserve channel completion, file cleanup and semaphore
  limits; cover error paths as well as successful scans.
- SQL migrations live in `ponylib_app/db/db_migrations` and are embedded in the
  binary. Add a new ordered migration for schema changes rather than editing an
  already applied migration. `FTS_LANGUAGE` is selected before initial migration
  and must remain consistent with the stored full-text vectors.
- Keep PostgreSQL at the existing 12.6 image version unless explicitly asked to
  change it. Maintain compatibility with PostgreSQL 12+.
- Keep all local startup tooling and its documentation under `local/`. Generated
  binaries belong in ignored `bin/` or `local/bin/` directories.
- Templates and static assets are embedded. Dev mode reloads templates from the
  source tree, so the local runner changes to the repository root before launch.
- Update `go.mod` and `go.sum` together when changing dependencies; run
  `go mod tidy`. Keep Go version references in build and CI configuration consistent.
- Keep the root README focused on setup and usage; document local workflows in
  `local/README.md`.
