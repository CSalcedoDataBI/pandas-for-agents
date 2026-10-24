# GroupBy

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

`DataFrameGroupBy.fillna`, `SeriesGroupBy.fillna` and `DataFrameGroupBy.grouper` are absent in 3.1.0, along with the `obj` keyword of `DataFrameGroupBy.get_group` and the `axis` keyword of `DataFrameGroupBy.shift`, `DataFrameGroupBy.diff`, `DataFrameGroupBy.rank`, `DataFrameGroupBy.idxmax`, `DataFrameGroupBy.idxmin`, `DataFrameGroupBy.skew`, `DataFrameGroupBy.take`, `DataFrameGroupBy.pct_change`, `DataFrameGroupBy.corrwith` and the cumulative methods; all were removed between 2.3.3 and 3.1.0. pandas 3.1.0 also deprecates index notation on `DataFrameGroupBy.nth`, extra positional and keyword arguments to `DataFrameGroupBy.cumsum` and `DataFrameGroupBy.cumprod`, and extra keyword arguments to `DataFrameGroupBy.cummax` and `DataFrameGroupBy.cummin`.

## Traps

- **Calling `DataFrameGroupBy.fillna` or `SeriesGroupBy.fillna` with a fill method such as forward fill.** Use `DataFrameGroupBy.ffill` or `DataFrameGroupBy.bfill` (`SeriesGroupBy.ffill` / `SeriesGroupBy.bfill` for a single column). To fill with a constant, use `DataFrame.fillna` or `Series.fillna` on the ungrouped object. *(since 2.2.0)*
  > Catalogue: “Use the :meth:`.DataFrameGroupBy.ffill` or :meth:`.DataFrameGroupBy.bfill` for forward or backward filling instead. If you want to fill with a single value, use :meth:`DataFrame.fillna` instead.”

- **Passing `axis` to `DataFrameGroupBy.shift`, `DataFrameGroupBy.diff`, `DataFrameGroupBy.rank`, `DataFrameGroupBy.idxmax`, `DataFrameGroupBy.idxmin`, `DataFrameGroupBy.skew` or `DataFrameGroupBy.take`.** Drop the `axis` keyword. For column-wise work, operate on the underlying object instead of the groupby. *(since 2.1.0)*
  > Catalogue: “For axis=1, operate on the underlying object instead. Otherwise the axis keyword is not necessary.”

- **Passing the `obj` keyword to `DataFrameGroupBy.get_group` to pull an existing group's rows out of a different frame.** Look up the group's row positions in `DataFrameGroupBy.indices` (with `.get(name)`) and select those rows from the other frame by position with iloc, as the deprecation note shows. Call `DataFrameGroupBy.get_group` with only the name when you want the group from the grouped frame itself. *(since 2.1.0)*
  > Catalogue: “The obj is deprecated and will be removed in a future version. Do ``df.iloc[gb.indices.get(name)]`` instead of ``gb.get_group(name, obj=df)``.”

- **Using square-bracket index notation on `DataFrameGroupBy.nth`.** Call `DataFrameGroupBy.nth` as a method with the position (or list of positions) as its argument. *(since 3.1.0)*
  > Catalogue: “Index notation (``g.nth[n]``) is deprecated in favor of calling ``g.nth(n)`` and will be removed in a future version of pandas.”

- **Passing extra positional or keyword arguments (numpy-compat leftovers) to `DataFrameGroupBy.cumsum` or `DataFrameGroupBy.cumprod`.** Pass only `numeric_only` and `skipna`, by keyword. *(since 3.1.0)*
  > Catalogue: “Passing ``*args`` to GroupBy.cumsum is deprecated and will be removed in a future version of pandas.”

- **Passing extra keyword arguments to `DataFrameGroupBy.cummax` or `DataFrameGroupBy.cummin`.** Pass only `numeric_only` and `skipna`, by keyword. *(since 3.1.0)*
  > Catalogue: “Passing ``**kwargs`` to GroupBy.cummax is deprecated and will be removed in a future version of pandas.”

## Example

Group-wise forward and backward fill replace the removed groupby fillna. The script also shows shift, diff and rank without axis, nth called as a method, cumsum and cummax without extra arguments, and the indices/iloc replacement for get_group with obj.

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({
    "key": ["a", "a", "a", "b", "b"],
    "val": [1.0, np.nan, 3.0, np.nan, 5.0],
    "n": [1, 2, 3, 4, 5],
})
gb = df.groupby("key")

# old: groupby fillna with a fill method (removed); use ffill / bfill
filled = gb["val"].ffill()
assert filled.isna().tolist() == [False, False, False, True, False]
back = gb["val"].bfill()
assert back.tolist() == [1.0, 3.0, 3.0, 5.0, 5.0]

# no axis keyword on shift / diff / rank
shifted = gb["n"].shift(1, fill_value=0)
assert shifted.tolist() == [0, 1, 2, 0, 4]
diffs = gb["n"].diff()
assert diffs.isna().tolist() == [True, False, False, True, False]
ranks = gb["n"].rank()
assert ranks.tolist() == [1.0, 2.0, 3.0, 1.0, 2.0]

# nth is called, not indexed
first_rows = gb.nth(0)
assert list(first_rows.index) == [0, 3]

# cumulative methods without extra positional or keyword arguments
cs = gb["n"].cumsum()
assert cs.tolist() == [1, 3, 6, 4, 9]
cm = gb["n"].cummax()
assert cm.tolist() == [1, 2, 3, 4, 5]

# old: get_group with an obj keyword (removed); take positions from indices
other = pd.DataFrame({"w": [10, 20, 30, 40, 50]})
rows_b = other.iloc[gb.indices.get("b")]
assert rows_b["w"].tolist() == [40, 50]

# get_group on the grouped frame itself, name only
group_b = gb.get_group("b")
assert group_b["n"].tolist() == [4, 5]

print("ok")
```
