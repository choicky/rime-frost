# Repository instructions

## Fork development

- Work in `choicky/rime-frost`. Create topic branches from `origin/custom` and open PRs with `gh pr create --repo choicky/rime-frost --base custom --head <branch>`. Check the repository and base before submitting. Open upstream PRs only when explicitly asked.
- `master` mirrors `gaboolic/rime-frost:master`. Only upstream fast-forwards belong on it. Integrate upstream into `custom` with a reviewed merge commit to preserve ancestry.
- Prefer Rime `*.custom.yaml` patches for fork settings. Keep changes to inherited schemas, dictionaries, and Lua out of unrelated PRs.
- Use [OPERATIONS.md](OPERATIONS.md) for synchronization, validation, and conflict recovery.

## Upstream dictionary maintenance

Apply these inherited content rules when a task explicitly calls for dictionary work. Use the fork development rules above for branches and PRs.

| Entry | Destination |
| --- | --- |
| Independent words, terminology, brands, products, and slang | `cn_dicts/others.dict.yaml` |
| People and fictional characters | `cn_dicts_cell/name.dict.yaml` |
| Places, sites, and institutions | `cn_dicts_cell/place.dict.yaml` |
| Meaningful phrases and collocations | `cn_dicts_cell/composite.dict.yaml` |
| Game or literary terms | The corresponding existing cell dictionary |
| Misspellings of an existing standard form | `others/错字词.txt` |
| Input correction from incorrect pinyin | `cn_dicts/corrections.dict.yaml` |

- Drop confirmed fragments of longer expressions. Treat function words and script flags as signals for manual review. Confirm `name?` and `place?` candidates and route valid names to their cell dictionaries.
- Examine source contexts and neighboring characters. Low neighbor entropy or a dominant adjacent character suggests a fragment. Prioritize two-character candidates using corroborating frequency and jieba token ratio. For three characters use token ratio ≥ 0.8 and PMI ≥ 7, or corroborating frequency ≥ 10. For four characters use PMI ≥ 10, minimum neighbor entropy ≥ 2, and corpus frequency ≥ 25 as review guides. Hold uncertain candidates for later review.
- Append confirmed entries as `word<TAB>pinyin<TAB>0`. Check both dictionary directories and the batch for duplicates, including alternate readings. Match the number of pinyin syllables to the character count and spot-check 10–20 readings, especially polyphonic characters.
- Add a dated source comment for each batch and preserve existing ordering. For conflicting append-only batches, retain both after checking for duplicates.
- Write typo mappings in UTF-8 as `misspelling<TAB>standard`, without a header. Ensure the standard form exists first. Fold misspelling counts into the standard form before frequency analysis.
- See [the mining script guide](scripts/README_new_words.md) for dependencies and usage. Keep raw MNBVC archives and ignored corpus and candidate files local. Use Zhihu question and answer body text for frequency analysis. Check memory before a large run and raise the frequency threshold if needed.
- For Zhihu hot-list review, run `python3 scripts/generate_missing_words.py --limit 30` from the repository root. Playwright downloads the list. Use `--skip-hot` to reuse an existing download. Review `data/corpus/zhihu_missing_<date>.txt` line by line, skipping comment lines and applying the same routing and entry checks above.
