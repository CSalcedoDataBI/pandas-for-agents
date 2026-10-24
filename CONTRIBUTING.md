# Contributing

Thanks for helping. This repository is a reference that AI agents read, so it has one rule above
all others: **no pandas name that did not come from the exported catalogue.**

## Report a problem

Open an [issue](https://github.com/CSalcedoDataBI/pandas-for-agents/issues) when:

- a function, method or keyword argument is missing from the catalogue, or catalogued wrongly
  (wrong signature, wrong deprecation, wrongly marked as removed);
- a trap card gives advice that is wrong for the pandas version it names;
- an example does not run on the pandas version it names.

Say which pandas version you used, and paste the code and the output or warning you got.

## Change something

Everything enters through a pull request. `main` is protected, and the required check is
`Validate`, which runs on every PR:

- `scripts/export_catalog.py --check` re-exports each `catalog/pandas-<version>.json` from that
  pandas version and fails if the file differs. The catalogue is generated: never edit it by hand.
- `scripts/build_changes.py --check` does the same for the change list.
- `scripts/check_names.py` fails if anything under `skills/` names a pandas function, method,
  accessor member or keyword argument that is not in the newest catalogue. A removed name may
  appear in prose, never in code.
- `python -m unittest discover -s tests` and `scripts/check_repo.py`.

To add a pandas version, run the exporter under that version and commit the new file:

```bash
uv run --no-project --python 3.13 --with pandas==<version> python scripts/export_catalog.py
```

## License

By contributing you agree that your contribution is released under the [MIT License](LICENSE).
