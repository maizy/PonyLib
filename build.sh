#!/bin/bash

set -o xtrace
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${PROJECT_DIR}"

go build -o bin -x ./...
