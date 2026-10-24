# DataFrame: reshape and combine

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

In pandas 3.1.0, `DataFrame.swapaxes` is gone, and the `method`, `limit`, `fill_axis` and `broadcast_axis` keywords of `DataFrame.align` are removed. Several keywords are deprecated: `copy` on `DataFrame.merge`, `DataFrame.align` and `DataFrame.transpose`; `dropna`, `sort` and `future_stack` on `DataFrame.stack`; `verify_integrity` on `DataFrame.set_index` (all since 3.0); and `inplace` on `DataFrame.set_index` and `DataFrame.reset_index`, plus `lsuffix`/`rsuffix` on `DataFrame.join` (since 3.1.0).

## Traps

- **Calling `DataFrame.swapaxes` to swap rows and columns.** Use `DataFrame.transpose`. *(since 2.1.0)*
  > Catalogue: “``swapaxes`` is deprecated and will be removed. Please use ``transpose`` instead.”

- **Passing `method`, `limit`, `fill_axis` or `broadcast_axis` to `DataFrame.align`.** Call `DataFrame.align` with only the remaining parameters: `join`, `axis`, `level` and `fill_value`. *(since 2.1)*
  > Catalogue: “level: 'Level | None' = None, copy: 'bool | lib.NoDefault' = <no_default>, fill_value: 'Hashable | None' = None)”

- **Passing `lsuffix=` and `rsuffix=` to `DataFrame.join` for overlapping column names.** Pass one tuple, for example `suffixes=("_l", "_r")`, to `DataFrame.join`. *(since 3.1.0)*
  > Catalogue: “Use ``suffixes`` instead.”

- **Using `inplace=True` with `DataFrame.set_index` or `DataFrame.reset_index`.** Assign the returned frame: `df = df.set_index("key")` or `df = df.reset_index()`. *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0. See the `whatsnew note on PDEP-8”

- **Passing `verify_integrity=True` to `DataFrame.set_index` to reject duplicate keys.** Call `DataFrame.set_index` without it. Then check uniqueness on the result's index yourself, as the deprecation note says. *(since 3.0.0)*
  > Catalogue: “The ``verify_integrity`` keyword is deprecated and will be removed in a future version. Check ``result.index.is_unique`` directly instead.”

- **Passing `dropna=`, `sort=` or `future_stack=` to `DataFrame.stack`.** Call `DataFrame.stack` with only `level`. *(since 3.0)*
  > Catalogue: “This parameter is deprecated and will be removed in a future version of pandas.”

- **Passing `copy=False` or `copy=True` to `DataFrame.merge`, `DataFrame.align` or `DataFrame.transpose`.** Drop the keyword. Copy-on-Write always returns a new object with a lazy copy. *(since 3.0.0)*
  > Catalogue: “This keyword is ignored and will be removed in pandas 4.0. Since pandas 3.0, this method always returns a new object using a lazy copy mechanism”

## Example

This script uses only the 3.1.0 forms, so it runs cleanly when every warning is an error: `DataFrame.merge` and `DataFrame.join` with `suffixes`, `DataFrame.set_index` with reassignment, `DataFrame.transpose` in place of the removed `DataFrame.swapaxes`, `DataFrame.align` with `join` and `fill_value` only, and `DataFrame.stack` without its deprecated keywords.

```python
import pandas as pd

left = pd.DataFrame({"key": ["a", "b", "c"], "val": [1, 2, 3]})
right = pd.DataFrame({"key": ["a", "b", "d"], "val": [10, 20, 40]})

# merge: no copy keyword
merged = left.merge(right, on="key", how="inner", suffixes=("_l", "_r"))
assert list(merged.columns) == ["key", "val_l", "val_r"]
assert list(merged["val_r"]) == [10, 20]

# set_index: reassign instead of the inplace keyword
l_idx = left.set_index("key")
r_idx = right.set_index("key")
assert list(l_idx.index) == ["a", "b", "c"]
assert l_idx.index.is_unique

# join: one suffixes tuple instead of lsuffix/rsuffix
joined = l_idx.join(r_idx, how="inner", suffixes=("_l", "_r"))
assert list(joined.columns) == ["val_l", "val_r"]
assert list(joined["val_r"]) == [10, 20]

# transpose replaces the removed swapaxes
t = joined.transpose()
assert list(t.columns) == ["a", "b"]
assert list(t.index) == ["val_l", "val_r"]

# align: only join and fill_value
a, b = l_idx.align(r_idx, join="outer", fill_value=0)
assert list(a.index) == ["a", "b", "c", "d"]
assert list(a["val"]) == [1, 2, 3, 0]
assert list(b["val"]) == [10, 20, 0, 40]

# stack: no dropna/sort/future_stack keywords
stacked = joined.stack()
assert len(stacked) == 4
assert stacked[("a", "val_r")] == 10
assert stacked[("b", "val_l")] == 2
print("ok")
```
