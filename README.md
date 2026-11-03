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
