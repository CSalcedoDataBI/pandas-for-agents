# pandas-for-agents

> **Pre-release.** This repository is public from day one, but nothing in it is ready to install
> yet. The API catalogue is still being generated, and there is no plugin to add. Watch the
> repository or follow the [v0.1 epic](https://github.com/CSalcedoDataBI/pandas-for-agents/issues/2)
> if you want to know when that changes.

The pandas reference for AI agents: every top-level function and every method of `DataFrame`,
`Series`, `Index`, `GroupBy`, `Resampler` and the `.str`, `.dt`, `.cat`, `.sparse` and `.plot`
accessors, **exported from the installed library itself** instead of typed from memory. Each one
comes with its signature, its docstring summary, and whether it is deprecated or was removed
between pandas 2.x and the current release — the trap agents fall into most often.

It is the sibling of [dax-for-agents](https://github.com/CSalcedoDataBI/dax-for-agents),
[powerquery-m-for-agents](https://github.com/CSalcedoDataBI/powerquery-m-for-agents) and
[spark-for-agents](https://github.com/CSalcedoDataBI/spark-for-agents), and it follows the same
rule: **an agent never reads a function name that did not come from the engine.**

## What it will contain

| Piece | Source | Status |
|---|---|---|
| API catalogue (`catalog/pandas-<version>.json`) | introspection of the installed `pandas` package, re-exported in CI | first version |
| Deprecated / removed flags (`catalog/changes-*.json`) | the docstrings' `deprecated` notes, and the diff between the last 2.x and the current catalogue | first version |
| Trap cards with examples (`skills/pandas-reference/traps/`) | drafted per group from the catalogue; every name, every quote and every example checked by script | first version |
| `pandas-reference` skill | points an agent to the cards, the change list and the catalogue | first version |
| `pandas-feedback` skill and the plugin manifest | report a wrong or missing card as a public issue | planned |

How the cards are checked: every pandas name must be in the catalogue (`scripts/check_names.py`,
in CI), every trap quotes the catalogue text that proves it, and every example runs on the current
pandas with every warning turned into an error. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Not in scope

- Running code. This is a reference an agent reads, not an executor.
- Polars. That is [polars-for-agents](https://github.com/CSalcedoDataBI/polars-for-agents).
- A pandas tutorial, or performance tuning in Microsoft Fabric. For that, see the pandas skill in
  [PatrickGallucci/fabric-skills](https://github.com/PatrickGallucci/fabric-skills) (MIT).

## License

[MIT](LICENSE).
