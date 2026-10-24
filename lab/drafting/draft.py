"""Draft trap cards with Claude, grounded in the exported catalogue, and verify them.

    python lab/drafting/draft.py                 # every batch without a passing draft
    python lab/drafting/draft.py --only io dt    # just these batches
    python lab/drafting/draft.py --budget 35     # stop once this repo's calls cost US$35

For each batch of catalogue members it writes a prompt with the members' catalogue entries and
change-list entries, calls `claude-review` (structured output, key from Secrets Manager), renders
the answer to Markdown and verifies it three ways:

1. scripts/check_names.py: every pandas name is in the catalogue (removed names only in prose).
2. Every trap's `evidence` is a verbatim quote of the excerpt the model was given.
3. The example runs on the current pandas with every warning turned into an error, so it can use
   nothing deprecated.

A failed draft gets one repair call with the failures. Results go to lab/drafting/out/<batch>.json
and .md; promoting a passing draft to skills/ is a separate, reviewed step.
Spend is read from claude-review's own log (~/.claude-review/gasto.jsonl, rows of this repo).
`claude-review` is the maintainer's tool; nobody needs it to use or check the cards.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "out"
sys.path.insert(0, str(ROOT / "scripts"))

import check_names  # noqa: E402

LOG = Path.home() / ".claude-review" / "gasto.jsonl"
REPO = ROOT.name

TOP_IO = re.compile(r"^(read_\w+|json_normalize|ExcelWriter|ExcelFile|HDFStore)$")
TOP_RESHAPE = {"merge", "merge_asof", "merge_ordered", "concat", "pivot", "pivot_table", "melt",
               "wide_to_long", "crosstab", "get_dummies", "from_dummies", "cut", "qcut", "factorize",
               "unique", "lreshape", "value_counts"}
DF_MISSING = {"fillna", "ffill", "bfill", "pad", "backfill", "interpolate", "replace", "dropna", "isna",
              "isnull", "notna", "notnull", "where", "mask", "clip"}
DF_APPLY = {"apply", "map", "applymap", "transform", "pipe", "agg", "aggregate", "eval", "query", "assign"}
DF_SELECT = {"loc", "iloc", "at", "iat", "xs", "get", "filter", "select", "head", "tail", "take", "sample",
             "truncate", "first", "last", "reindex", "set_axis", "rename", "drop", "drop_duplicates",
             "duplicated", "bool"}
DF_RESHAPE = {"pivot", "pivot_table", "melt", "stack", "unstack", "explode", "set_index", "reset_index",
              "swaplevel", "swapaxes", "merge", "join", "combine", "combine_first", "update", "align",
              "compare", "transpose"}
DF_WINDOW = {"rolling", "expanding", "ewm", "resample", "shift", "diff", "pct_change"}
DF_NAMED = DF_MISSING | DF_APPLY | DF_SELECT | DF_RESHAPE | DF_WINDOW

# batch -> (title, [(catalogue group, name filter)])
BATCHES = {
    "io": ("Reading and writing data", [("pandas", lambda n: bool(TOP_IO.match(n)))]),
    # Series.value_counts is where the removed pd.value_counts went; without it the card has no
    # catalogue entry to ground the replacement on.
    "reshape-top": ("Top-level merge, concat and reshape", [("pandas", lambda n: n in TOP_RESHAPE),
                                                            ("Series", lambda n: n == "value_counts")]),
    "top-other": ("Other top-level functions: conversion, dates, options",
                  [("pandas", lambda n: not TOP_IO.match(n) and n not in TOP_RESHAPE)]),
    "missing": ("DataFrame and Series: missing data, fill and replace",
                [("DataFrame", lambda n: n in DF_MISSING), ("Series", lambda n: n in DF_MISSING)]),
    "apply": ("DataFrame: apply, map, transform and eval", [("DataFrame", lambda n: n in DF_APPLY)]),
    "select": ("DataFrame: selection, indexing and labels", [("DataFrame", lambda n: n in DF_SELECT)]),
    "reshape-frame": ("DataFrame: reshape and combine", [("DataFrame", lambda n: n in DF_RESHAPE)]),
    "window": ("Windows, shifts and resampling", [("DataFrame", lambda n: n in DF_WINDOW),
                                                  ("Resampler", lambda n: True)]),
    "frame-other": ("DataFrame: conversion, export and statistics",
                    [("DataFrame", lambda n: n not in DF_NAMED)]),
    "series": ("Series-only members", [("Series", "series-only")]),
    "index": ("Index", [("Index", lambda n: True), ("pandas.api.types", lambda n: True)]),
    "groupby": ("GroupBy", [("DataFrameGroupBy", lambda n: True), ("SeriesGroupBy", lambda n: True)]),
    "str": ("The .str accessor", [("Series.str", lambda n: True)]),
    "dt": ("The .dt accessor", [("Series.dt (datetime)", lambda n: True), ("Series.dt (timedelta)", lambda n: True),
                                ("Series.dt (period)", lambda n: True)]),
    "cat-sparse-plot": ("The .cat, .sparse and .plot accessors",
                        [("Series.cat", lambda n: True), ("Series.sparse", lambda n: True),
                         ("DataFrame.sparse", lambda n: True), ("Series.plot", lambda n: True)]),
}

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["summary", "traps", "example"],
    "properties": {
        "summary": {"type": "string"},
        "traps": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["trap", "instead", "since", "evidence"],
                "properties": {
                    "trap": {"type": "string"},
                    "instead": {"type": "string"},
                    "since": {"type": "string"},
                    "evidence": {"type": "string"},
                },
            },
        },
        "example": {
            "type": "object",
            "additionalProperties": False,
            "required": ["explains", "code"],
            "properties": {"explains": {"type": "string"}, "code": {"type": "string"}},
        },
    },
}

RULES = """You write one trap card of pandas-for-agents, a reference that AI agents read before
writing pandas {new} code. Agents trained on older pandas keep using names and keyword arguments
that pandas deprecated in 2.x and removed in {new}. The card must stop that.

Hard rules (a script checks every one, and a card that breaks one is thrown away):

1. Use ONLY names that appear in the catalogue excerpt below. Do not use pandas names from memory.
2. Write a pandas name in prose as inline code with its owner: `DataFrame.map`, `Series.str.contains`,
   `GroupBy.agg`, `pd.merge`. A name the excerpt marks as removed may appear ONLY in prose.
3. Each trap is grounded: `evidence` is an exact, verbatim quote (copy it character for character,
   at least a few words) from the excerpt: a deprecation note, a signature, or a removed-list
   entry. If you cannot quote evidence for a trap, leave the trap out. Prefer what the excerpt
   says was removed, removed as a keyword argument, or is deprecated now. 3 to 8 traps.
4. `since` is the pandas version the excerpt gives for the deprecation, or "{new}" for a removal
   without a version.
5. `example.code` is one complete Python script that runs as is on pandas {new} with every warning
   turned into an error: `import pandas as pd` (numpy as np if needed), builds its own small data,
   no files or network (use io.StringIO for readers), no removed names and no removed keyword
   arguments anywhere in the code (mention old forms only in # comments, without the call),
   column access with brackets (df["col"]), and asserts on the result so it proves something.
   For plotting, call matplotlib through `.plot` only; the backend is Agg.
6. `summary`: two sentences on what changed for this group between {old} and {new}.
7. English, concise, no marketing words.

Catalogue excerpt for "{title}" (pandas {old} -> {new}). `current` is the {new} entry, `removed`
lists names gone in {new} with the old deprecation note, `removed_params` lists keyword arguments
gone in {new}:

{excerpt}
"""

REPAIR = """
Your previous card failed the checks below. Return the whole card again, fixed. Drop a trap rather
than keep one whose evidence is not a verbatim quote of the excerpt.

Previous card:
{previous}

Failures:
{failures}
"""


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def catalogue_pair() -> tuple[dict, dict, dict]:
    files = sorted((ROOT / "catalog").glob("pandas-*.json"), key=check_names.version_key)
    old, new = load(files[0]), load(files[-1])
    changes = load(ROOT / "catalog" / f"changes-{old['pandas_version']}-to-{new['pandas_version']}.json")
    return old, new, changes


def excerpt(batch: str, old: dict, new: dict, changes: dict) -> dict:
    out: dict = {}
    for group, keep in BATCHES[batch][1]:
        now = new["groups"][group]["members"]
        before = old["groups"].get(group, {}).get("members", {})
        if keep == "series-only":
            frame = set(new["groups"]["DataFrame"]["members"]) | set(old["groups"]["DataFrame"]["members"])
            keep = lambda n, frame=frame: n not in frame  # noqa: E731
        ch = changes["groups"].get(group, {})
        entry = {
            "current": {n: e for n, e in now.items() if keep(n)},
            "removed": {n: {"old": before[n], **v} for n, v in ch.get("removed", {}).items() if keep(n)},
            "removed_params": {n: v for n, v in ch.get("removed_params", {}).items() if keep(n)},
        }
        for e in entry["current"].values():
            e.pop("params", None)
        out[group] = entry
    return out


def spent() -> float:
    if not LOG.exists():
        return 0.0
    total = 0.0
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("cwd") == REPO:
            total += row.get("usd") or 0.0
    return round(total, 4)


def call(prompt: str, name: str, model: str | None) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        p, s, o = (Path(tmp) / f for f in ("p.md", "s.json", "out.json"))
        p.write_text(prompt, encoding="utf-8")
        s.write_text(json.dumps(SCHEMA), encoding="utf-8")
        # On PATH, or named by CLAUDE_REVIEW.
        tool = os.environ.get("CLAUDE_REVIEW") or shutil.which("claude-review")
        if not tool:
            raise RuntimeError(f"{name}: claude-review is not on PATH (or set CLAUDE_REVIEW)")
        cmd = [tool, "--prompt-file", str(p), "--schema", str(s), "-o", str(o)]
        if model:
            cmd += ["--model", model]
        run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if run.returncode != 0 or not o.exists():
            raise RuntimeError(f"{name}: claude-review failed: {run.stderr.strip()[-800:]}")
        return load(o)


def render(batch: str, card: dict, versions: tuple[str, str]) -> str:
    title = BATCHES[batch][0]
    lines = [f"# {title}", "", f"*pandas {versions[0]} → {versions[1]}. Drafted with Claude from the "
             "exported catalogue; every name and every evidence quote is checked by script.*", "",
             card["summary"].strip(), "", "## Traps", ""]
    for t in card["traps"]:
        lines += [f"- **{t['trap'].strip()}** {t['instead'].strip()} *(since {t['since'].strip()})*",
                  f"  > Catalogue: “{t['evidence'].strip()}”", ""]
    lines += ["## Example", "", card["example"]["explains"].strip(), "", "```python",
              card["example"]["code"].strip(), "```", ""]
    return "\n".join(lines)


def leaves(node) -> list[str]:
    """Every string in the excerpt, decoded, so a quote copied without JSON escapes still matches."""
    if isinstance(node, str):
        return [node]
    items = node.values() if isinstance(node, dict) else node if isinstance(node, list) else []
    return [s for item in items for s in leaves(item)]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def run_example(code: str, version: str) -> str | None:
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "example.py"
        script.write_text(code, encoding="utf-8")
        # EXAMPLE_PYTHON: an interpreter that already has pandas==<version> and matplotlib, which
        # avoids reinstalling them per example.
        python = os.environ.get("EXAMPLE_PYTHON")
        launcher = [python] if python else ["uv", "run", "-q", "--no-project", "--python", "3.13", "--with",
                                            f"pandas=={version}", "--with", "matplotlib", "python"]
        run = subprocess.run(launcher + ["-I", "-W", "error", str(script)], capture_output=True, text=True,
                             encoding="utf-8", cwd=tmp,
                             env={**os.environ, "MPLBACKEND": "Agg"}, timeout=300)
        if run.returncode == 0:
            return None
        # The failure is stored in out/, which is versioned: no machine paths in it.
        error = run.stderr.replace(str(script), "example.py")
        error = re.sub(r'File "[^"]*[\\/](site-packages|Lib)[\\/]', r'File "<\1>/', error)
        return error.strip()[-1500:]


def verify(batch: str, card: dict, md: str, quote_source: str, version: str) -> list[str]:
    cat = check_names.Catalogue()
    failures = check_names.check_text(cat, md, f"{batch}.md")
    haystack = normalize(quote_source)
    for t in card["traps"]:
        if normalize(t["evidence"]) not in haystack:
            failures.append(f"evidence is not a verbatim quote of the excerpt: {t['evidence'][:160]}")
    if not card["traps"]:
        failures.append("no traps")
    error = run_example(card["example"]["code"], version)
    if error:
        failures.append(f"example fails on pandas {version} with warnings as errors:\n{error}")
    return failures


def draft(batch: str, model: str | None) -> dict:
    old, new, changes = catalogue_pair()
    ex = excerpt(batch, old, new, changes)
    ex_text = json.dumps(ex, indent=1, ensure_ascii=False)
    quotes = ex_text + "\n" + "\n".join(leaves(ex))
    versions = (old["pandas_version"], new["pandas_version"])
    prompt = RULES.format(old=versions[0], new=versions[1], title=BATCHES[batch][0], excerpt=ex_text)
    attempts = []
    card = call(prompt, batch, model)
    for attempt in range(2):
        md = render(batch, card, versions)
        failures = verify(batch, card, md, quotes, versions[1])
        attempts.append({"card": card, "failures": failures})
        if not failures or attempt == 1:
            break
        card = call(prompt + REPAIR.format(previous=json.dumps(card, indent=1, ensure_ascii=False),
                                           failures="\n".join(f"- {f}" for f in failures)), batch, model)
    result = {"batch": batch, "title": BATCHES[batch][0], "from": versions[0], "to": versions[1],
              "passed": not attempts[-1]["failures"], "attempts": attempts}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{batch}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                       newline="\n")
    (OUT / f"{batch}.md").write_text(md, encoding="utf-8", newline="\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--only", nargs="*", choices=sorted(BATCHES))
    parser.add_argument("--budget", type=float, default=35.0, help="US$ this repo may spend in total")
    parser.add_argument("--model")
    parser.add_argument("--redo", action="store_true", help="also redraft batches that already passed")
    args = parser.parse_args()
    for batch in args.only or list(BATCHES):
        done = OUT / f"{batch}.json"
        if done.exists() and load(done)["passed"] and not args.redo:
            print(f"skip {batch}: already passed")
            continue
        if spent() >= args.budget:
            print(f"stop: US${spent()} spent, budget US${args.budget}")
            return 1
        try:
            r = draft(batch, args.model)
        except RuntimeError as exc:
            print(f"FAIL {exc}")
            continue
        print(f"{'PASS' if r['passed'] else 'FAIL'} {batch} ({len(r['attempts'])} call(s)); spent US${spent()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
