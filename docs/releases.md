# Publishing a release

Run from a clean checkout of the branch you want to publish. The script requires
Git, Docker, GitHub CLI (`gh`), and access to the `origin` remote. Authenticate with
`gh auth login` and `docker login ghcr.io` before running it.

```sh
./publish-release.sh          # Patch: v2.0.8 -> v2.0.9
./publish-release.sh --patch  # Same as the default
./publish-release.sh --minor  # Minor: v2.0.8 -> v2.1.0
./publish-release.sh --major  # Major: v2.0.8 -> v3.0.0
```

The script fetches tags from `origin` and finds the highest version matching
`vX.Y.Z`, ignoring prerelease and other tags. That tag must be an ancestor of the
current commit. At least one existing release tag is required.

It tags the current commit, calls `TARGET_ENV=github ./build-docker.sh`, and pushes
`ghcr.io/maizy/ponylib:vX.Y.Z`. It then updates the image in
`docs/docker-compose/docker-compose.yml`, commits that change, and pushes the
current branch and new tag together with an atomic Git push. Finally, it publishes
a GitHub release in `maizy/PonyLib` using `gh release create`. Release notes list
commit hashes and subjects since the previous version, through the tagged commit.
The later Compose update commit is outside the release tag.

Publishing spans Git, GHCR and GitHub and cannot be rolled back atomically. On
failure, completed steps remain in place. Inspect the reported stage and existing
artifacts before retrying; do not blindly rerun the script, which computes a new
version from the tags. For example, if only release creation failed, finish with
`gh release create vX.Y.Z --repo maizy/PonyLib --verify-tag --title vX.Y.Z --notes-file <notes-file>`.
