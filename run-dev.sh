#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

for dependency in go docker; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        echo "Required command not found: $dependency" >&2
        exit 1
    fi
done
docker compose version >/dev/null

export DEV_DB_PORT="${DEV_DB_PORT:-55432}"
if [[ ! "$DEV_DB_PORT" =~ ^[0-9]{1,5}$ ]] || (( 10#$DEV_DB_PORT < 1 || 10#$DEV_DB_PORT > 65535 )); then
    echo "DEV_DB_PORT must be a port number between 1 and 65535" >&2
    exit 1
fi

docker compose -f "$PROJECT_DIR/compose.dev.yml" up -d --wait --wait-timeout 60 db

VERSION="$(git describe --tags --always 2>/dev/null || printf 'dev')"
go build -o "$PROJECT_DIR/bin/ponylib" \
    -ldflags "-X dev.maizy.ru/ponylib/ponylib_app.version=$VERSION" ./cmd/ponylib

export DATABASE_URL="postgres://ponylib:ponylib-dev@127.0.0.1:${DEV_DB_PORT}/ponylib?sslmode=disable"
export FTS_LANGUAGE="${FTS_LANGUAGE:-english}"

if [[ $# -eq 0 ]]; then
    set -- web-ui --dev-mode --debug
fi

printf 'PostgreSQL is ready on 127.0.0.1:%s. It will keep running after the local process exits.\n' "$DEV_DB_PORT"
exec "$PROJECT_DIR/bin/ponylib" "$@"
