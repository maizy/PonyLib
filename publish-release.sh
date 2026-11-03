#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'USAGE'
Usage: ./publish-release.sh [--patch | --minor | --major]

Publish a release from the current commit (default: --patch).
Requires a clean working tree, an origin remote, Docker with GHCR login,
and an authenticated GitHub CLI with access to maizy/PonyLib.
USAGE
}

BUMP=patch
case "${1:-}" in
    '') ;;
    --patch) BUMP=patch ;;
    --minor) BUMP=minor ;;
    --major) BUMP=major ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac
if (( $# > 1 )); then
    usage >&2
    exit 2
fi

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"
for dependency in git docker gh awk mktemp; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        echo "Required command not found: $dependency" >&2
        exit 1
    fi
done

if [[ -n "$(git status --porcelain)" ]]; then
    echo "Commit or stash working tree changes before publishing." >&2
    exit 1
fi
BRANCH="$(git symbolic-ref --quiet --short HEAD)" || {
    echo "Check out a branch before publishing." >&2
    exit 1
}
RELEASE_COMMIT="$(git rev-parse HEAD)"
git remote get-url origin >/dev/null
gh auth status --hostname github.com >/dev/null
docker info >/dev/null
git fetch --tags origin

LATEST_VERSION=''
while IFS= read -r tag; do
    if [[ "$tag" =~ ^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]]; then
        LATEST_VERSION="$tag"
        break
    fi
done < <(git tag --list --sort=-version:refname)
if [[ -z "$LATEST_VERSION" ]]; then
    echo "No release tag matching vX.Y.Z found." >&2
    exit 1
fi
if ! git merge-base --is-ancestor "$LATEST_VERSION" "$RELEASE_COMMIT"; then
    echo "Latest release $LATEST_VERSION is not an ancestor of HEAD." >&2
    exit 1
fi
IFS=. read -r MAJOR MINOR PATCH <<< "${LATEST_VERSION#v}"
case "$BUMP" in
    major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
    minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
    patch) PATCH=$((PATCH + 1)) ;;
esac
VERSION="v${MAJOR}.${MINOR}.${PATCH}"
IMAGE="ghcr.io/maizy/ponylib:${VERSION}"
COMPOSE_FILE=docs/docker-compose/docker-compose.yml
if git show-ref --verify --quiet "refs/tags/$VERSION"; then
    echo "Tag $VERSION already exists." >&2
    exit 1
fi

TEMP_DIR="$(mktemp -d)"
STAGE=preparation
cleanup() {
    local status=$?
    rm -rf "$TEMP_DIR"
    if (( status != 0 )); then
        printf 'Release %s failed during %s. Inspect local/remote tags, commits, image and GitHub release before retrying.\n' "$VERSION" "$STAGE" >&2
    fi
}
trap cleanup EXIT

# Validate and prepare the Compose update before making release changes.
awk -v image="$IMAGE" '
    /^[[:space:]]*image: ghcr\.io\/maizy\/ponylib:/ {
        sub(/ghcr\.io\/maizy\/ponylib:[^[:space:]]+/, image)
        count++
    }
    { print }
    END { if (count != 1) exit 1 }
' "$COMPOSE_FILE" > "$TEMP_DIR/compose.yml"
{
    printf '## Changes since %s\n\n' "$LATEST_VERSION"
    git log --reverse --format='- %h %s' "${LATEST_VERSION}..${RELEASE_COMMIT}"
} > "$TEMP_DIR/release-notes.md"

printf 'Publishing %s -> %s from %s\n' "$LATEST_VERSION" "$VERSION" "$RELEASE_COMMIT"
STAGE=tagging
git tag -a "$VERSION" "$RELEASE_COMMIT" -m "Release $VERSION"
STAGE='Docker build'
TARGET_ENV=github ./build-docker.sh
STAGE='Docker push'
docker push "$IMAGE"
STAGE='Compose version commit'
cat "$TEMP_DIR/compose.yml" > "$COMPOSE_FILE"
git add -- "$COMPOSE_FILE"
git commit -m "docs: use $VERSION Docker image"
STAGE='Git push'
git push --atomic origin "HEAD:refs/heads/$BRANCH" "refs/tags/$VERSION:refs/tags/$VERSION"
STAGE='GitHub release'
gh release create "$VERSION" --repo maizy/PonyLib --verify-tag \
    --title "$VERSION" --notes-file "$TEMP_DIR/release-notes.md"
printf 'Published %s and %s\n' "$VERSION" "$IMAGE"
