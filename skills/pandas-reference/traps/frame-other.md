# DataFrame: conversion, export and statistics

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

Between 2.3.3 and 3.1.0, `DataFrame.to_gbq` and the `axis` keyword of `DataFrame.groupby` were removed. Version 3.0.0 made the `copy` keyword a no-op under Copy-on-Write, and 3.1.0 deprecated `inplace` on sorting, the `convert_*` keywords of `DataFrame.convert_dtypes`, dict input to `DataFrame.from_records` and the 'fastparquet'/'auto' engines of `DataFrame.to_parquet`.

## Traps

- **Calling `DataFrame.to_gbq` to write to Google BigQuery.** `DataFrame.to_gbq` is removed. Call `pandas_gbq.to_gbq` from the separate pandas-gbq package. *(since 2.2.0)*
  > Catalogue: “Please use ``pandas_gbq.to_gbq`` instead.”

- **Passing axis=1 to `DataFrame.groupby` to group columns.** Transpose with `DataFrame.T`, call `DataFrame.groupby` on the result, and transpose back if needed. *(since 2.1.0)*
  > Catalogue: “For ``axis=1``, do ``frame.T.groupby(...)`` instead.”

- **Passing copy=False or copy=True to `DataFrame.astype`, `DataFrame.infer_objects`, `DataFrame.tz_localize`, `DataFrame.to_period` or `DataFrame.set_flags`.** Leave `copy` out. These methods always return a new object, and copying is lazy under Copy-on-Write. *(since 3.0.0)*
  > Catalogue: “This keyword is ignored and will be removed in pandas 4.0. Since pandas 3.0, this method always returns a new object using a lazy copy mechanism”

- **Passing convert_string, convert_integer, convert_boolean, convert_floating or infer_objects to `DataFrame.convert_dtypes`.** Call `DataFrame.convert_dtypes` without these keywords. *(since 3.1.0)*
  > Catalogue: “The ``convert_string`` keyword is deprecated and will be removed in a future version.”

- **Using inplace=True with `DataFrame.sort_values`, `DataFrame.sort_index` or `DataFrame.rename_axis`.** Assign the result, for example df = df.sort_values("a"). *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0.”

- **Passing a dict to `DataFrame.from_records`.** Pass dicts to the `DataFrame` constructor or to `DataFrame.from_dict`. Use `DataFrame.from_records` only for records or structured arrays. *(since 3.1.0)*
  > Catalogue: “Passing a dict is deprecated. Use the DataFrame constructor or :meth:`DataFrame.from_dict` instead.”

- **Passing engine='fastparquet' or engine='auto' to `DataFrame.to_parquet`.** Omit `engine`, or pass 'pyarrow'. *(since 3.1.0)*
  > Catalogue: “The ``'fastparquet'`` and ``'auto'`` engine options are deprecated.”

- **Relying on date_format='epoch' in `DataFrame.to_json`.** Pass date_format='iso' explicitly. *(since 3.0.0)*
  > Catalogue: “'epoch' date format is deprecated and will be removed in a future version, please use 'iso' instead.”

## Example

The 3.1.0 forms of the trapped calls, all asserted. Grouping columns uses a transpose instead of the axis keyword. Sorting assigns the result instead of using inplace. Casting and dtype conversion pass no deprecated keywords. A dict goes to `DataFrame.from_dict`, and JSON export passes date_format='iso'.

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})

# group columns: transpose, group rows, transpose back (no axis keyword)
grouped = df.T.groupby({"a": "x", "b": "x", "c": "y"}).sum().T
assert list(grouped["x"]) == [4, 6]
assert list(grouped["y"]) == [5, 6]

# sort by assigning the result (no inplace keyword)
out = df.sort_values("a", ascending=False)
assert list(out["a"]) == [2, 1]
assert list(df["a"]) == [1, 2]

# cast without the copy keyword
df2 = df.astype("float64")
assert df2.dtypes["a"] == "float64"

# convert_dtypes without convert_* keywords
f = pd.DataFrame({"n": [1.0, None]}).convert_dtypes()
assert str(f.dtypes["n"]) == "Int64"

# dict input goes to from_dict, not from_records
d = pd.DataFrame.from_dict({"r1": {"a": 1}, "r2": {"a": 2}}, orient="index")
assert list(d.index) == ["r1", "r2"]
assert list(d["a"]) == [1, 2]

# JSON export with an explicit iso date format
s = df.to_json(orient="records", date_format="iso")
assert s == '[{"a":1,"b":3,"c":5},{"a":2,"b":4,"c":6}]'
```
