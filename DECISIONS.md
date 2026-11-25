# Decisions

- Keep the upstream mirror separate from fork development. Merge upstream integration PRs with merge commits so the next synchronization can detect ancestry.
- Reuse the PR validation workflow directly from the sync run. GitHub can hold ordinary PR runs created by `GITHUB_TOKEN` for approval. The direct call validates the proposed merge with read-only permissions. See [GitHub token trigger rules](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs).
- Guard inherited publishing jobs on `custom` and disable their workflow paths in the fork settings. The mirror retains the upstream workflow files.
