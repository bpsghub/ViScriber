# Releasing ViScriber

This guide is for maintainers who publish binaries to GitHub Releases.

## Overview

Release automation is defined in [../.github/workflows/build.yml](../.github/workflows/build.yml).

When a tag like `v1.0.0` is pushed, GitHub Actions builds:

- Windows installer: `ViScriber-Setup.exe`
- macOS installer: `ViScriber.dmg`
- Linux package: `ViScriber-x86_64.AppImage`

Then it creates or updates the GitHub Release for that tag and uploads the artifacts.

## Recommended Flow (Tag Push)

1. Ensure `master` is up to date and all required changes are committed.
2. Create an annotated tag.
3. Push the tag.
4. Wait for the Build & Release workflow to finish.
5. Verify assets are visible on the Releases page.

Commands:

```bash
git checkout master
git pull
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin v1.0.1
```

## Manual Flow (Actions UI)

Use this only when you already have a tag and want to re-run release publishing.

1. Open GitHub Actions.
2. Open workflow `Build & Release`.
3. Click `Run workflow`.
4. Enter an existing tag (example: `v1.0.1`).

Note: manual runs build from the tagged commit, not from the latest `master` unless the tag points to it.

## Troubleshooting

- No release appears:
  - Check the workflow run status in Actions.
  - If `build` fails, `release` will be skipped.
- Tag pushed but old workflow behavior:
  - The workflow version is taken from the tagged commit.
  - Create a new tag after workflow fixes are merged.
- Missing one platform artifact:
  - Open the failed matrix job logs to see the failing build step.

## Versioning Suggestion

Use semantic versioning:

- Patch: `v1.0.1` (bug fixes)
- Minor: `v1.1.0` (new features, backward compatible)
- Major: `v2.0.0` (breaking changes)
