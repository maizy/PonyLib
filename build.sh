#!/bin/bash

set -o xtrace
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${PROJECT_DIR}"

VERSION=`git describe --tags --always`

go build -o bin -ldflags "-X dev.maizy.ru/ponylib/ponylib_app.version=${VERSION}" -x ./...
