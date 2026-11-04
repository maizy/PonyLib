#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
container_id=""
cleanup() {
  if [[ -n "$container_id" ]]; then
    if [[ "$1" != 0 ]]; then docker logs "$container_id" >&2 || true; fi
    docker rm -f "$container_id" >/dev/null || true
  fi
}
trap 'cleanup "$?"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ -z "${PONYLIB_TEST_DATABASE_URL:-}" ]]; then
  container_id="$(docker run -d --rm \
    -e POSTGRES_USER=ponylib -e POSTGRES_PASSWORD=ponylib-test -e POSTGRES_DB=ponylib \
    -p 127.0.0.1::5432 "postgres:${POSTGRES_VERSION:-12.6}")"
  ready=0
  for ((attempt=0; attempt<60; attempt++)); do
    if docker exec "$container_id" pg_isready -U ponylib -d ponylib >/dev/null 2>&1; then
      ready=1
      break
    fi
    sleep 1
  done
  if [[ "$ready" != 1 ]]; then
    echo 'PostgreSQL did not become ready within 60 seconds' >&2
    exit 1
  fi
  binding="$(docker port "$container_id" 5432/tcp)"
  export PONYLIB_TEST_DATABASE_URL="postgres://ponylib:ponylib-test@127.0.0.1:${binding##*:}/ponylib?sslmode=disable"
fi

go test -tags=integration -race -vet=off -count=1 -timeout 5m ./integration-tests "$@"
