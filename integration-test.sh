#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
container_id=""
cleanup() {
  if [[ -n "$container_id" ]]; then
    if [[ "$1" != 0 ]]; then docker logs "$container_id" >&2 || true; fi
    echo "[integration-tests] Removing temporary PostgreSQL container"
    docker rm -f "$container_id" >/dev/null || true
  fi
}
trap 'cleanup "$?"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if [[ -z "${PONYLIB_TEST_DATABASE_URL:-}" ]]; then
  echo "[integration-tests] Starting PostgreSQL ${POSTGRES_VERSION:-12.6} in Docker"
  container_id="$(docker run -d --rm \
    -e POSTGRES_USER=ponylib -e POSTGRES_PASSWORD=ponylib-test -e POSTGRES_DB=ponylib \
    -p 127.0.0.1::5432 "postgres:${POSTGRES_VERSION:-12.6}")"
  echo "[integration-tests] Waiting for PostgreSQL readiness"
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
  echo "[integration-tests] PostgreSQL is ready"
else
  echo "[integration-tests] Using PostgreSQL from PONYLIB_TEST_DATABASE_URL"
fi

echo "[integration-tests] Running integration tests with race detector"
go test -tags=integration -race -v -count=1 -timeout 5m ./integration-tests "$@"
