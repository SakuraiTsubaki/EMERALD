# Regional forms teachable-learnset extraction contract

The teachable arrays are build-policy outputs, not immutable species facts. They must therefore be captured from the generated header of the exact expansion checkout and configuration chosen for EMERALD.

Reference source snapshot: `rh-hideout/pokeemerald-expansion` commit `75b806a3ab57a81ff1eb6179288981f0b3cc3050`.

After building that checkout with the chosen TM/HM/tutor policy, run:

```sh
python tools/extract_regional_teachables.py \
  manifests/regional-forms/regional_forms_master.csv \
  path/to/pokeemerald-expansion/src/data/pokemon/teachable_learnsets.h \
  --json-output manifests/regional-forms/regional_forms_teachable_reference.json \
  --markdown-output manifests/regional-forms/regional_forms_teachable_reference.md \
  --require-complete
```

The extractor records the SHA-256 of both the master CSV and generated header, preserves each surveyed species key and learnset symbol, and fails when any master row lacks a generated array. This prevents an incomplete or differently configured build from being presented as the selected EMERALD ruleset.

The generated JSON and Markdown are committed after the exact source/configuration checkout has been built. ROM data is neither needed nor read by this step.
