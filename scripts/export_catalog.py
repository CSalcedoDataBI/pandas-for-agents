"""Export the pandas API catalogue from the installed `pandas` package.

    python scripts/export_catalog.py            # writes catalog/pandas-<version>.json
    python scripts/export_catalog.py --check    # exits 1 if the committed file differs

Run it once per pandas version, each in its own environment, for example:

    uv run --no-project --python 3.13 --with pandas==3.1.0 python scripts/export_catalog.py

Every name an agent reads in this repository comes from one of these files. The catalogue is the
only generated artefact: never edit it by hand (CLAUDE.md).

What is exported, per group: every public member (name not starting with `_`), its kind, its
signature (parameter names and the rendered signature), the first paragraph of its docstring, and
every `.. deprecated::` note in that docstring, attached to the member or to the parameter it sits
under. Groups are found from live objects (`pd.Series(...).str` and so on), not from private module
paths, so the same script works across versions.

The docstring summaries are pandas' own text: pandas is BSD-3-Clause, and the notice travels in
each file's `source` block.
"""

from __future__ import annotations

import argparse
import inspect
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"

# The directive sits at column 0 for a member, or indented under a parameter; its text is every
# following line indented deeper than the directive, blank lines included.
DEPRECATED = re.compile(r"^([ \t]*)\.\. deprecated::[ \t]*(\S+)[ \t]*\n((?:\1[ \t]+.*\n?|[ \t]*\n)*)", re.M)
PARAM_HEADER = re.compile(r"^(\*{0,2}[A-Za-z_][A-Za-z0-9_]*)(?:, ?\*{0,2}[A-Za-z_][A-Za-z0-9_]*)*\s*:", re.M)
SECTION = re.compile(r"^([A-Z][A-Za-z ]+)\n-{3,}\s*$", re.M)


def groups() -> dict[str, type]:
    """The classes behind each group, taken from live objects."""
    s = pd.Series(["a", "b"])
    dt = pd.Series(pd.to_datetime(["2024-01-01", "2024-01-02"]))
    td = pd.Series(pd.to_timedelta(["1D", "2D"]))
    per = pd.Series(pd.period_range("2024-01", periods=2, freq="M"))
    cat = s.astype("category")
    sparse = pd.Series([0, 1], dtype="Sparse[int64]")
    frame = pd.DataFrame({"k": ["a", "a"], "v": [1, 2]})
    by_time = pd.DataFrame({"v": [1, 2]}, index=dt.values)
    return {
        "DataFrame": pd.DataFrame,
        "Series": pd.Series,
        "Index": pd.Index,
        "DataFrameGroupBy": type(frame.groupby("k")),
        "SeriesGroupBy": type(frame.groupby("k")["v"]),
        "Resampler": type(by_time.resample("D")),
        "Series.str": type(s.str),
        "Series.dt (datetime)": type(dt.dt),
        "Series.dt (timedelta)": type(td.dt),
        "Series.dt (period)": type(per.dt),
        "Series.cat": type(cat.cat),
        "Series.sparse": type(sparse.sparse),
        "DataFrame.sparse": type(pd.DataFrame({"x": sparse}).sparse),
        "Series.plot": type(s.plot),
        "DataFrame.plot": type(frame.plot),
    }


STAR_ARGS = re.compile(r"``\*{1,2}(args|kwargs)``")
ADDRESS = re.compile(r"<object object at 0x[0-9A-Fa-f]+>")


def render(params) -> str:
    """The signature text, with sentinel defaults' memory addresses replaced so the file is
    reproducible."""
    return ADDRESS.sub("<sentinel>", "(" + ", ".join(str(p) for p in params) + ")")


def summary(doc: str) -> str:
    first = doc.strip().split("\n\n", 1)[0]
    return " ".join(line.strip() for line in first.splitlines())


def deprecations(doc: str) -> list[dict]:
    """Each `.. deprecated::` note, attached to the parameter it sits under when it is inside the
    Parameters section, otherwise to the member itself.

    A note that names ``*args`` or ``**kwargs`` is about those, wherever it sits: pandas puts such
    notes after an unrelated parameter (GroupBy.skew, GroupBy.take). Only an indented note belongs
    to the parameter documented above it; one at column 0 belongs to the member."""
    sections = [(m.start(), m.group(1).strip()) for m in SECTION.finditer(doc)]
    out = []
    for m in DEPRECATED.finditer(doc):
        text = " ".join(line.strip() for line in m.group(3).splitlines() if line.strip())
        section = next((name for start, name in reversed(sections) if start < m.start()), None)
        target = "member"
        star = STAR_ARGS.search(text)
        if star:
            target = "parameter:" + star.group(1)
        elif m.group(1) and section in ("Parameters", "Other Parameters"):
            headers = [h for h in PARAM_HEADER.finditer(doc) if h.start() < m.start()]
            if headers:
                target = "parameter:" + headers[-1].group(1).lstrip("*")
        out.append({"version": m.group(2), "target": target, "note": text})
    return out


def describe(obj, kind: str) -> dict:
    entry: dict = {"kind": kind}
    target = obj.fget if isinstance(obj, property) else obj
    if callable(target) and kind not in ("property", "accessor", "class"):
        try:
            sig = inspect.signature(target)
        except (TypeError, ValueError):
            sig = None
        if sig is not None:
            params = [p for p in sig.parameters.values() if p.name not in ("self", "cls")]
            entry["signature"] = render(params)
            entry["params"] = [p.name for p in params]
    doc = inspect.getdoc(obj) or ""
    entry["summary"] = summary(doc)
    notes = deprecations(doc)
    if notes:
        entry["deprecated"] = notes
    return entry


def member_kind(cls: type, name: str) -> str:
    static = inspect.getattr_static(cls, name)
    if isinstance(static, property) or type(static).__name__ in ("cache_readonly", "AxisProperty"):
        return "property"
    if type(static).__name__ in ("CachedAccessor", "Accessor"):
        return "accessor"
    if isinstance(static, classmethod):
        return "classmethod"
    if isinstance(static, staticmethod):
        return "staticmethod"
    if inspect.isclass(static):
        return "class"
    if callable(static):
        return "method"
    return "attribute"


def export_class(cls: type) -> dict:
    members = {}
    for name in sorted(dir(cls)):
        if name.startswith("_"):
            continue
        kind = member_kind(cls, name)
        static = inspect.getattr_static(cls, name)
        obj = static if kind == "property" else getattr(cls, name, static)
        members[name] = describe(obj, kind)
    return {"class": f"{cls.__module__}.{cls.__qualname__}", "members": members}


def export_module(module, label: str) -> dict:
    members = {}
    for name in sorted(dir(module)):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if inspect.ismodule(obj):
            continue
        if inspect.isclass(obj):
            kind = "class"
        elif callable(obj):
            kind = "function"
        else:
            kind = "attribute"
        entry = describe(obj, kind)
        if kind == "class":
            try:
                params = list(inspect.signature(obj).parameters.values())
                entry["signature"] = render(params)
                entry["params"] = [p.name for p in params]
            except (TypeError, ValueError):
                pass
        members[name] = entry
    return {"class": label, "members": members}


def build() -> dict:
    catalog = {
        "pandas_version": pd.__version__,
        # major.minor only, so CI can reproduce the file on any patch release.
        "python_version": ".".join(map(str, sys.version_info[:2])),
        "generated_by": "scripts/export_catalog.py",
        "source": {
            "package": "pandas",
            "license": "BSD-3-Clause",
            "notice": "Signatures and docstring summaries are taken from pandas. "
            "Copyright (c) 2008-2011, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData "
            "Development Team; 2011-2025, Open source contributors.",
        },
        # pandas.api.types is where the removed Index.is_* checks point to.
        "groups": {"pandas": export_module(pd, "pandas"),
                   "pandas.api.types": export_module(pd.api.types, "pandas.api.types")},
    }
    for group, cls in groups().items():
        catalog["groups"][group] = export_class(cls)
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="compare with the committed file")
    args = parser.parse_args()
    text = json.dumps(build(), indent=1, ensure_ascii=False, sort_keys=False) + "\n"
    path = CATALOG / f"pandas-{pd.__version__}.json"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            print(f"FAIL {path.relative_to(ROOT).as_posix()} is not what the export produces")
            return 1
        print(f"OK {path.relative_to(ROOT).as_posix()} matches pandas {pd.__version__}")
        return 0
    CATALOG.mkdir(exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
