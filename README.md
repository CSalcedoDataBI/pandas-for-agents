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

## Does the reference stop invented names?

That is the whole reason this repository exists, so it is measured, not asserted. Each question
in the [bank](evals/hallucination/questions.yaml) is asked twice of the same model: once alone
(arm A), and once with the catalogue rows of its category (arm B — names and one-line summaries,
never the card that holds the answer). Every pandas name an answer writes **in runnable code** is
looked up with the repo's own checker ([`scripts/check_names.py`](scripts/check_names.py)); a name
the current catalogue does not have — including one **removed** since pandas 2.x — is an invention.
No model judges another, and any saved run recounts for free with `--replay`.

| Model | Questions compared | Invented, without the reference | Invented, with it |
|---|---|---|---|
| Claude Haiku 5.5 | 13 | 0 | 0 |
| Claude Haiku 4.5 | 13 | 1 | **0** |

The one invention the reference removed is the telling one: asked to apply a function to every
cell of a DataFrame, Haiku 4.5 reached for `DataFrame.applymap` — **removed in pandas 3.x**. With
the catalogue's current rows in front of it, the same model used `DataFrame.map` instead. That is
exactly the failure a from-memory agent makes, because it was trained on pandas 2.x: the names it
remembers are gone. A current flagship model (Haiku 5.5) does not slip here, but the removed-API
trap is real for anything a little older or cheaper, and this measurement keeps watching for it.

```bash
python evals/hallucination/run_ab.py --model claude-haiku-5-5 --out run.json
python evals/hallucination/run_ab.py --replay evals/hallucination/runs/2026-10-23-claude-haiku-4-5.json
python evals/hallucination/test_run_ab.py
```

Raw answers for every run are in [`evals/hallucination/runs/`](evals/hallucination/runs/). The eval
calls the Anthropic or DeepSeek API with `ANTHROPIC_API_KEY` or `DEEPSEEK_API_KEY` read from the
environment (never from the command line, never written into the run file); `--replay` sends
nothing.

## Not in scope

- Running code. This is a reference an agent reads, not an executor.
- Polars. That is [polars-for-agents](https://github.com/CSalcedoDataBI/polars-for-agents).
- A pandas tutorial, or performance tuning in Microsoft Fabric. For that, see the pandas skill in
  [PatrickGallucci/fabric-skills](https://github.com/PatrickGallucci/fabric-skills) (MIT).

## License

[MIT](LICENSE).
