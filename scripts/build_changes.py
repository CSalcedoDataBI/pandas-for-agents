"""Build the 2.x -> current change list from two exported catalogues.

    python scripts/build_changes.py                 # oldest and newest catalog/pandas-*.json
    python scripts/build_changes.py --check         # exits 1 if the committed file differs

Writes catalog/changes-<old>-to-<new>.json. Nothing in it is typed by hand: "removed" is a name in
the old catalogue that the new one lacks, and its "was_deprecated" note is the old docstring's own
`.. deprecated::` text, which usually names the replacement. "deprecated" lists the notes the
current docstrings carry.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"


def version_key(path: Path) -> tuple[int, ...]:
    return tuple(int(p) for p in path.stem.removeprefix("pandas-").split(".") if p.isdigit())


def catalogues() -> list[Path]:
    return sorted(CATALOG.glob("pandas-*.json"), key=version_key)


def build(old: dict, new: dict) -> dict:
    out = {
        "from": old["pandas_version"],
        "to": new["pandas_version"],
        "generated_by": "scripts/build_changes.py",
        "groups": {},
    }
    for group, data in new["groups"].items():
        before = old["groups"].get(group, {}).get("members", {})
        after = data["members"]
        removed = {
            name: {k: v for k, v in (("was_deprecated", before[name].get("deprecated")),) if v}
            for name in sorted(set(before) - set(after))
        }
        removed_params = {}
        for name in sorted(set(before) & set(after)):
            gone = [p for p in before[name].get("params", []) if p not in after[name].get("params", [])]
            if gone and "params" in after[name]:
                notes = [d for d in before[name].get("deprecated", []) if d["target"] in {f"parameter:{p}" for p in gone}]
                removed_params[name] = {"params": gone, **({"was_deprecated": notes} if notes else {})}
        deprecated = {name: e["deprecated"] for name, e in sorted(after.items()) if e.get("deprecated")}
        entry = {
            "removed": removed,
            "removed_params": removed_params,
            "added": sorted(set(after) - set(before)),
            "deprecated": deprecated,
        }
        if any(entry.values()):
            out["groups"][group] = entry
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="compare with the committed file")
    args = parser.parse_args()
    files = catalogues()
    if len(files) < 2:
        print("FAIL need two catalog/pandas-*.json files")
        return 1
    old, new = (json.loads(p.read_text(encoding="utf-8")) for p in (files[0], files[-1]))
    text = json.dumps(build(old, new), indent=1, ensure_ascii=False) + "\n"
    path = CATALOG / f"changes-{old['pandas_version']}-to-{new['pandas_version']}.json"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            print(f"FAIL {path.relative_to(ROOT).as_posix()} is not what build_changes.py produces")
            return 1
        print(f"OK {path.relative_to(ROOT).as_posix()} is up to date")
        return 0
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
