# Decisions

- Keep the upstream mirror separate from fork development. Merge upstream integration PRs with merge commits so the next synchronization can detect ancestry.
- Call PR validation directly from the sync run. GitHub can hold ordinary PR runs created by `GITHUB_TOKEN` for approval. The direct call validates the proposed merge with read-only permissions. See [GitHub token trigger rules](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs).
- Select Natural Code first and Full Pinyin second through `default.custom.yaml`. Preserve the upstream schemas and their dependencies in the bundle.
- Use the upstream ZIP generator on a staging directory containing tracked runtime files. Add the fork patch and the tracked phrase template explicitly because the generator excludes names containing `custom`.
- Publish from `custom` through a dedicated workflow. Stage the tested ZIP and checksum on a draft, then publish and mark it Latest in one operation. Keep inherited publishing workflows disabled.
