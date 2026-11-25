#!/usr/bin/env bash
set -euo pipefail

git fetch --no-tags origin refs/heads/master:refs/remotes/origin/master refs/heads/custom:refs/remotes/origin/custom
git fetch --no-tags upstream refs/heads/master
mirror=$(git rev-parse origin/master)
upstream=$(git rev-parse FETCH_HEAD)
custom=$(git rev-parse origin/custom)

if ! git merge-base --is-ancestor "$mirror" "$upstream"; then
  echo "::error::Fork master cannot fast-forward to upstream master. Investigate before retrying."
  exit 1
fi
if [[ "$mirror" != "$upstream" ]]; then
  git push origin "$upstream:refs/heads/master"
fi

# A competing update must not change the PR head we intend to validate.
remote_master=$(git ls-remote --exit-code origin refs/heads/master)
if [[ "${remote_master%%$'\t'*}" != "$upstream" ]]; then
  echo "::error::Fork master changed during synchronization. Retry the workflow."
  exit 1
fi
if git merge-base --is-ancestor "$upstream" "$custom"; then
  echo "custom already contains master." >> "$GITHUB_STEP_SUMMARY"
  exit 0
fi

repo=${GITHUB_REPOSITORY:?}
pr=$(gh api --method GET "repos/$repo/pulls" -f state=open -f base=custom \
  -f "head=${repo%/*}:master" --jq '.[0].number // empty')
if [[ -z "$pr" ]]; then
  pr=$(gh api --method POST "repos/$repo/pulls" -f base=custom -f head=master \
    -f title='Sync upstream master into custom' \
    -f body='Review the upstream changes and the validation run before merging. Use a merge commit to preserve upstream ancestry.' \
    --jq '.number')
fi

printf 'pr=%s\nhead=%s\nbase=%s\n' "$pr" "$upstream" "$custom" >> "$GITHUB_OUTPUT"
printf 'Validate PR [#%s](%s/%s/pull/%s) at %s against %s.\n' \
  "$pr" "$GITHUB_SERVER_URL" "$repo" "$pr" "$upstream" "$custom" >> "$GITHUB_STEP_SUMMARY"
