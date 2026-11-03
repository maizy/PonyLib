# PonyLib v2

Fb2 library with CLI & Web UI.

## Setup with docker-compose (recommended)

You need [docker](https://docs.docker.com/engine/install/) & [docker-compose](https://docs.docker.com/compose/install/).

Create some directory for ponylib. By default, all data will be stored in `data/` subdirectory.

Create `ponylib.env` file from [`docs/docker-compose/ponylib.env.example`](docs/docker-compose/ponylib.env.example)
and edit it. It's important to choose right options here **before the first app run**.

Save [`docs/docker-compose/docker-compose.yml`](docs/docker-compose/docker-compose.yml) as `docker-compose.yml` to
the same directory. Add paths to your libraries in `volumes` section.

Run

```
docker-compose up -d
```

It needs some time in the first run to init Database & run DB migrations.

Check status: `docker-compose ps`, `docker-compose logs`.

Scan books from libraries. For example:

```
docker-compose exec ponylib ponylib scan /data/lib1
docker-compose exec ponylib ponylib scan /data/lib3.zip
# ...
```

Also see other ponylib commands:

```
docker-compose exec ponylib ponylib --help
```

## Local development

Requires Go 1.27.3+, Docker and Docker Compose v2. From the repository, run:

```sh
./run-dev.sh
```

This starts PostgreSQL 18.6 in Docker, waits for it to become healthy, builds
`bin/ponylib`, and runs the web UI locally at http://127.0.0.1:55387 with debug mode
and template hot reload. Database migrations run automatically.

PostgreSQL is available at `127.0.0.1:55432`, with database/user `ponylib` and
password `ponylib-dev`. It binds only to localhost and stores data in a Docker
volume. Ctrl+C stops the local service; the database keeps running.

To pass a different command or web UI options:

```sh
./run-dev.sh scan /path/to/library
./run-dev.sh web-ui --dev-mode --debug --port 8080
```

Set `DEV_DB_PORT` to change the PostgreSQL host port. Set `FTS_LANGUAGE` before
the first run to choose the full-text search language (default: `english`); keep
it the same on subsequent runs. The script sets `DATABASE_URL` for the dev database.

```sh
DEV_DB_PORT=55433 FTS_LANGUAGE=russian ./run-dev.sh
```

Stop PostgreSQL with `docker compose -f compose.dev.yml down`. To delete the dev
database as well, use `docker compose -f compose.dev.yml down -v`.

## Setup without docker (advanced)

### Requirements

* PostgreSQL 18+
* Go 1.27.3+

### Upgrading an existing database

The Compose example now uses PostgreSQL 18 and mounts `./data/db` at
`/var/lib/postgresql` (the image stores data in `18/docker`). Existing PostgreSQL 12
data directories cannot be reused directly. Before changing the image or volume
mount, back up the old database with `pg_dump`, stop the old server, keep its data
directory as a backup, and restore the dump into a fresh PostgreSQL 18 database.
See the [PostgreSQL upgrade documentation](https://www.postgresql.org/docs/18/upgrading.html).

### Init DB

Setup PostgreSQL 18+, then

```
su - postgres

createuser -P ponylib
# define password

createdb -O ponylib ponylib
```

### Build

```
./build.sh
```


### Usage

```
DATABASE_URL="postgres://localhost:5432/ponylib?user=ponylib&password=password" FTS_LANGUAGE=english bin/ponylib --help
```


## Additional Tools

### `ponylib-parser`

Parse fb2 files & display metadata. Can be used separately.

Support recursive directory scan, follow symlinks.

Usage:

```
ponylib-parser FILE_OR_DIR [FILE_OR_DIR]
```

---

_[Obsolete python + django based version](https://github.com/maizy/PonyLib/tree/v1)_


## Tests

Run `go test ./...` for unit tests. To also check migrations, JSONB storage and
full-text search, point `PONYLIB_TEST_DATABASE_URL` at a disposable PostgreSQL 18
instance and run `go test -race -timeout 2m ./...`. The integration test creates
and removes its own schema; the database user needs permission to create schemas.
