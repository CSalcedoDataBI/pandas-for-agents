"""Fail when a card names something that is not in the exported pandas catalogue.

    python scripts/check_names.py                    # every skills/**/*.md
    python scripts/check_names.py lab/drafting/out   # or any files / folders given

Two kinds of reference are checked, against the newest catalog/pandas-*.json:

- Inline code in prose (`DataFrame.map`, `pd.merge`, `Series.str.contains`, `GroupBy.agg`): the
  name must exist in the current catalogue, or be listed as removed in catalog/changes-*.json,
  because a trap note has to be able to say what is gone.
- Fenced ```python blocks: they must parse, and every pandas name in them must exist in the
  current catalogue. Removed names are not allowed in code, not even in a "before" example; write
  them in a comment. `pd.<name>` is checked against the top-level functions, `<x>.str.<name>` (and
  .dt, .cat, .sparse, .plot) against that accessor, any other `<x>.<name>` against the members of
  every group. Keyword arguments of a call are checked against the parameters of that name.

Standard library only, so CI needs no install step. Exit code 1 lists every failure.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

# Names whose attributes are not pandas: modules an example may import next to pandas.
FOREIGN = {"np", "numpy", "math", "datetime", "re", "json", "os", "sys", "time", "random", "plt",
           "matplotlib", "pathlib", "Path", "itertools", "functools", "operator", "string"}
ACCESSORS = {"str": ["Series.str"], "dt": ["Series.dt (datetime)", "Series.dt (timedelta)", "Series.dt (period)"],
             "cat": ["Series.cat"], "sparse": ["Series.sparse", "DataFrame.sparse"],
             "plot": ["Series.plot", "DataFrame.plot"]}
OWNERS = {"pd": ["pandas"], "pandas": ["pandas"], "pd.api.types": ["pandas.api.types"],
          "pandas.api.types": ["pandas.api.types"], "DataFrame": ["DataFrame"], "Series": ["Series"],
          "Index": ["Index"], "GroupBy": ["DataFrameGroupBy", "SeriesGroupBy"],
          "DataFrameGroupBy": ["DataFrameGroupBy"], "SeriesGroupBy": ["SeriesGroupBy"],
          "Resampler": ["Resampler"]}
INLINE = re.compile(r"(?<![\w.])(pd\.api\.types|pandas\.api\.types|pd|pandas|DataFrame|Series|Index|GroupBy|DataFrameGroupBy|SeriesGroupBy|Resampler)"
                    r"\.(\w+)(?:\.(\w+))?")
FENCE = re.compile(r"^```python[^\n]*\n(.*?)^```", re.S | re.M)
INLINE_CODE = re.compile(r"`([^`\n]+)`")


def version_key(path: Path) -> tuple[int, ...]:
    return tuple(int(p) for p in path.stem.removeprefix("pandas-").split(".") if p.isdigit())


class Catalogue:
    def __init__(self) -> None:
        files = sorted(CATALOG.glob("pandas-*.json"), key=version_key)
        if not files:
            raise SystemExit("FAIL no catalog/pandas-*.json: run scripts/export_catalog.py")
        current = json.loads(files[-1].read_text(encoding="utf-8"))
        self.version = current["pandas_version"]
        self.groups = {g: d["members"] for g, d in current["groups"].items()}
        self.removed: dict[str, set[str]] = {}
        for changes in CATALOG.glob(f"changes-*-to-{self.version}.json"):
            for g, d in json.loads(changes.read_text(encoding="utf-8"))["groups"].items():
                self.removed.setdefault(g, set()).update(d["removed"])
        self.all_members = {n for g, m in self.groups.items() if not g.startswith("pandas") for n in m}

    def entries(self, groups: list[str], name: str) -> list[dict]:
        return [self.groups[g][name] for g in groups if name in self.groups.get(g, {})]

    def is_removed(self, groups: list[str], name: str) -> bool:
        return any(name in self.removed.get(g, ()) for g in groups)


def check_inline(cat: Catalogue, text: str) -> list[str]:
    errors = []
    prose = FENCE.sub("", text)
    for code in INLINE_CODE.findall(prose):
        for owner, name, sub in INLINE.findall(code):
            groups = OWNERS[owner]
            if owner in ("pd", "pandas") and name == "api":
                continue  # the module path itself; its members are matched as pandas.api.types.<name>
            if sub and name in ACCESSORS:
                groups, name = ACCESSORS[name], sub
            if not cat.entries(groups, name) and not cat.is_removed(groups, name):
                errors.append(f"`{code}`: {name} is not in {' / '.join(groups)} of pandas {cat.version}")
    return errors


def check_call_keywords(cat: Catalogue, call: ast.Call, groups: list[str], name: str, where: str) -> list[str]:
    entries = [e for e in cat.entries(groups, name) if "params" in e]
    if not entries or any("kwargs" in e["params"] for e in entries):
        return []
    known = {p for e in entries for p in e["params"]}
    return [f"{where}: {name}() has no parameter '{kw.arg}' in pandas {cat.version}"
            for kw in call.keywords if kw.arg and kw.arg not in known]


def check_code(cat: Catalogue, code: str, where: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return [f"{where}: python block does not parse ({exc.msg}, line {exc.lineno})"]
    errors = []
    calls = {id(n.func): n for n in ast.walk(tree) if isinstance(n, ast.Call)}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        base, name = node.value, node.attr
        if isinstance(base, ast.Name) and base.id in FOREIGN:
            continue
        if isinstance(base, ast.Name) and base.id in ("pd", "pandas"):
            if name == "api":
                continue
            groups = ["pandas"]
            ok = bool(cat.entries(groups, name))
        elif isinstance(base, ast.Attribute) and base.attr == "types" and isinstance(base.value, ast.Attribute) \
                and base.value.attr == "api":
            groups = ["pandas.api.types"]
            ok = bool(cat.entries(groups, name))
        elif isinstance(base, ast.Attribute) and base.attr in ("api", "types") and name in ("types", "api"):
            continue
        elif isinstance(base, ast.Attribute) and base.attr in ACCESSORS:
            groups = ACCESSORS[base.attr]
            ok = bool(cat.entries(groups, name))
        else:
            groups = [g for g in cat.groups if not g.startswith("pandas")]
            ok = name in cat.all_members
        if not ok:
            gone = " (removed: see catalog/changes-*.json)" if cat.is_removed(groups, name) else ""
            errors.append(f"{where}: .{name} is not in pandas {cat.version}{gone}")
        elif id(node) in calls:
            errors += check_call_keywords(cat, calls[id(node)], groups, name, where)
    return errors


def check_text(cat: Catalogue, text: str, where: str) -> list[str]:
    errors = [f"{where}: {e}" for e in check_inline(cat, text)]
    for i, block in enumerate(FENCE.findall(text), 1):
        errors += check_code(cat, block, f"{where} block {i}")
    return errors


def targets(args: list[str]) -> list[Path]:
    paths = [Path(a) for a in args] or [ROOT / "skills"]
    files = []
    for p in paths:
        p = p if p.is_absolute() else ROOT / p
        if p.is_dir():
            files += sorted(p.rglob("*.md"))
        elif p.exists():
            files.append(p)
    return files


def main() -> int:
    cat = Catalogue()
    errors = []
    files = targets(sys.argv[1:])
    for f in files:
        errors += check_text(cat, f.read_text(encoding="utf-8"), f.relative_to(ROOT).as_posix())
    for error in errors:
        print(f"FAIL {error}")
    if not errors:
        print(f"OK names in {len(files)} file(s) are all in pandas {cat.version}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
