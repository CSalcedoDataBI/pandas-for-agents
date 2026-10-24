---
name: pandas-reference
description: "Use before writing or reviewing pandas code, and whenever a pandas name, method or keyword argument is in doubt: whether `DataFrame.applymap`, `fillna(method=...)`, `groupby(axis=...)` or another 2.x habit still exists, what replaced it, or what a method's signature is in the current pandas. Looks the name up in the catalogue exported from the installed pandas package, per version, and in the trap cards. Not for Polars (polars-for-agents), not a tutorial, and it does not run code."
---

# pandas reference

Every pandas name below comes from the catalogue exported from the installed package, never from
memory. Check a name here before you write it.

## Where to look

1. **The trap card for the group** you are about to use: [traps/README.md](traps/README.md). Each
   card lists what pandas removed or deprecated between the last 2.x and the current release, what
   to write instead, the catalogue text that proves it, and an example that runs on the current
   release with every warning turned into an error.
2. **The change list**: `catalog/changes-<old>-to-<new>.json` at the plugin root. Per group:
   `removed` (with the old deprecation note, which usually names the replacement),
   `removed_params` (keyword arguments that are gone), `added` and `deprecated`.
3. **The catalogue**: `catalog/pandas-<version>.json`. Per group (`pandas` for the top level,
   `DataFrame`, `Series`, `Index`, `DataFrameGroupBy`, `SeriesGroupBy`, `Resampler` and the
   `.str`, `.dt`, `.cat`, `.sparse` and `.plot` accessors): every public member with its kind,
   signature, docstring summary and deprecation notes.

## Rules

- A name that is not in the catalogue of the target version does not exist. Do not write it.
- A name in `removed` is a trap: use the replacement its note gives.
- A member with a `deprecated` note still works but warns; prefer the replacement.
- Ask which pandas version the code targets when it matters. The newest catalogue is the default.
