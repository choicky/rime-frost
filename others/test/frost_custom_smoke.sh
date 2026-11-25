#!/usr/bin/env bash
# Deploy the distributable ZIP as a clean Rime user directory.
set -euo pipefail

root=$(cd -- "$(dirname -- "$0")/../.." && pwd)
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
mkdir "$scratch/shared" "$scratch/user"
python3 -m zipfile -e "${1:?usage: frost_custom_smoke.sh ZIP}" "$scratch/user"

"${CXX:-c++}" -std=c++11 "$root/others/test/frost_custom_smoke_test.cc" \
  -lrime -o "$scratch/smoke"
"$scratch/smoke" "$scratch/shared" "$scratch/user"

for schema in melt_eng radical_pinyin rime_frost_aux; do
  test -s "$scratch/user/build/$schema.schema.yaml"
done
