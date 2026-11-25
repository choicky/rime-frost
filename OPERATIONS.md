# Operations

## GitHub setup

- Set the default branch to `custom`, enable GitHub Actions, and enable **Allow GitHub Actions to create and approve pull requests**. The sync job must be allowed to fast-forward `master`. Keep force pushes blocked.
- Disable the inherited `nightly.yml` and `release.yml` in the fork's Actions settings if they are registered. Do this before any human-authenticated push to `master` or fork release. The mirrored copies retain their original triggers. A normal sync push uses `GITHUB_TOKEN`, which suppresses push-triggered runs.
- Keep merge commits enabled and preserve the `master` and `custom` branches after PR merges.

## Sync and review

Run **Sync upstream** from `custom` or let it run daily at 02:00 UTC (10:00 Beijing time). The workflow becomes available after its files land on the default branch. A divergence error leaves `master` unchanged and requires investigation. If GitHub rejects a change to workflow files due to token permissions, disable inherited publishing workflows first, then perform the same fast-forward with an authorized credential and rerun **Sync upstream**.

When an integration PR is open, use the sync run summary to match the PR number and both validated SHAs to the current PR. Rerun synchronization if either branch moved. Approve the ordinary PR workflow separately if a branch rule requires its check. Merge only after review, using **Create a merge commit**.

For conflicts, create a topic branch from current `custom`, merge fork `master` locally, and resolve the conflicts there. Open a PR from the resolution branch into `custom` and preserve its merge ancestry. Keep the fork guards when resolving publishing workflow conflicts and review new upstream automation before merging it. Do not push resolutions to the mirror.

## Local validation

Run `actionlint` and `shellcheck .github/scripts/sync-upstream.sh`. **Validate PR** checks repository YAML, including Rime dictionary headers, and compiles the runtime Lua files for syntax. On Linux with a C++ compiler, librime development headers and a compatible librime-lua plugin, run both deployment smoke tests:

```bash
bash others/test/frost_14key_smoke.sh
bash others/test/frost_stroke_smoke.sh
```
