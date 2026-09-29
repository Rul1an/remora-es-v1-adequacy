# Reproduce

```sh
git clone https://github.com/darklordVirtual/REMORA-research.git remora
git -C remora archive 31c4060630923344d43d9fac26821150262c3687 conformance/evidence-sufficiency-v1 \
  | tar -x --strip-components=2 -C subject      # after: mkdir subject
cp -r adapter/. subject/ && cp manifests/*.json subject/
git clone https://github.com/corpus-adequacy/corpus-adequacy.git ca && git -C ca checkout 5fa2ff587497b00ac684a767335b9068f7e520a6
# one row at a time; the tool locks the tree, so concurrent rows on one tree are refused
python3 -B ca/corpus_adequacy.py subject/ca_row1-verdict.manifest.json --json > row1.json
python3 -B ca/corpus_adequacy.py subject/ca_row2-guidance.manifest.json --json > row2.json
python3 -B ca/corpus_adequacy.py subject/ca_row3-runner.manifest.json --json > row3.json
```

`gen_mutants.py subject/checker.py mutants.json` regenerates `mutants.json` byte for byte from the pinned checker.
Standard-library Python only; no network after the two clones. Measured with Python 3.14.3 on Darwin arm64.
