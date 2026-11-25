# Operations

## GitHub setup

- Set the default branch to `custom`, enable GitHub Actions, and enable **Allow GitHub Actions to create and approve pull requests**. The sync job must be allowed to fast-forward `master`. Keep force pushes blocked.
- Keep the inherited `nightly.yml` and `release.yml` disabled in the fork's Actions settings. The mirrored copies retain the upstream triggers.
- Keep merge commits enabled and preserve the `master` and `custom` branches after PR merges.

## Sync and review

Run **Sync upstream** from `custom` or let it run daily at 02:00 UTC (10:00 Beijing time). A divergence error leaves `master` unchanged and requires investigation. If GitHub rejects a change to workflow files due to token permissions, disable inherited publishing workflows first, then perform the same fast-forward with an authorized credential and rerun **Sync upstream**.

When an integration PR is open, use the sync run summary to match the PR number and both validated SHAs to the current PR. Rerun synchronization if either branch moved. Approve the ordinary PR workflow separately if a branch rule requires its check. After review, merge with **Create a merge commit** as a maintainer so the resulting push triggers the custom release workflow.

For conflicts, create a topic branch from current `custom`, merge fork `master` locally, and resolve the conflicts there. Open a PR from the resolution branch into `custom` and preserve its merge ancestry. Keep the fork guards when resolving publishing workflow conflicts and review new upstream automation before merging it. Do not push resolutions to the mirror.

## Install and select a schema

Download [the latest custom ZIP](https://github.com/choicky/rime-frost/releases/latest/download/rime-frost-schemas.zip), extract it into your Rime user directory, and redeploy. Back up an existing `default.custom.yaml` and merge any personal settings you want to keep. The packaged menu lists Natural Code first and Full Pinyin second. A new profile starts with Natural Code. Existing users may need to select it once because Rime remembers the last schema.

## Release and rollback

**Publish custom release** runs on pushes to `custom`, including merges performed by a maintainer. It can also be dispatched from `custom`. Validation builds and deploys the ZIP before the publisher receives it. The publisher checks that the tested SHA is still the branch tip before staging a draft and again before promotion. The tag identifies the source SHA and run attempt, and the notes record the full SHA. Validation failures and unpublished drafts leave Latest pointing to the previous successful release.

Download `rime-frost-schemas.zip` and `SHA256SUMS` from the same release. Run `sha256sum --check SHA256SUMS` and confirm the source SHA in the notes matches the release tag's commit. Run the clean deployment test below when checking a downloaded artifact.

To roll back, disable **Publish custom release** temporarily and cancel or wait for pending and in-progress release runs. Verify a known-good release and mark it Latest with `gh release edit <tag> --latest --repo choicky/rime-frost`. Confirm that the permanent download returns the selected ZIP. Re-enable publishing after the fix is ready and dispatch the workflow from `custom` if needed. Remove obsolete unpublished drafts from superseded or failed uploads as needed.

## Local validation

Run `actionlint` and the existing fourteen-key and stroke smoke tests. **Validate PR** also checks YAML and runtime Lua syntax. Build the ZIP from the Git index and test it with a C++ compiler, librime development headers, and a compatible librime-lua plugin.

```bash
output=$(mktemp -d)
python3 .github/scripts/package-custom.py "$output"
bash others/test/frost_custom_smoke.sh "$output/rime-frost-schemas.zip"
(cd "$output" && sha256sum rime-frost-schemas.zip > SHA256SUMS && sha256sum --check SHA256SUMS)
```
