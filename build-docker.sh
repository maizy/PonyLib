#!/bin/bash

set -o xtrace
set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "${PROJECT_DIR}"

DATE=$(date -u "+%Y-%m-%dT%H:%M:%S%Z")
VER=$(git describe --tags --always)
REV=$(git rev-parse HEAD)
if [[ "$VER" == "" || "${VER}" != v* ]]; then
  VER="pre-release-${VER}"
fi

if [ -z "${TARGET_ENV}" ]; then
  TARGET_ENV="local"
fi

if [ "${TARGET_ENV}" == "github" ]; then
  IMAGE="ghcr.io/maizy/ponylib:${VER}"
else
  IMAGE="ponylib:${VER}"
fi

DOCKER_BUILDKIT=1 docker build \
  --label "org.opencontainers.image.created=${DATE}" \
  --label "org.opencontainers.image.revision=${REV}" \
  --label "org.opencontainers.image.version=${VER}" \
  -t "${IMAGE}" .
