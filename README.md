# PonyLib v2

Fb2 library with web interface.

**Being rewritten in golang. Work in progress**

## Requirements

* PostgreSQL 12+

## Installation Instructions

### Init database & user

```
su - postgres
createuser -P ponylib
createdb -O ponylib ponylib
```

## Tools

### `ponylib-parser`

Parse fb2 files & display metadata. Can be used separately.

Support recursive directory scan, follow symlinks.

Usage:

```
ponylib-parser FILE_OR_DIR [FILE_OR_DIR]
```

---

_[Obsolete python + django based version](https://github.com/maizy/PonyLib/tree/v1)_

