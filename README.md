# PonyLib v2

Fb2 library with CLI & web UI.

**Being rewritten in golang. Work in progress**

## Requirements

* PostgreSQL 12+
* Go 1.16+

## Setup with docker-compose

_TODO_


## Manual installation

### Init DB

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
DATABASE_URL="postgres://localhost:5432/ponylib?user=ponylib&password=password" bin/ponylib --help
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

