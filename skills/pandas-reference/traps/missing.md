# DataFrame and Series: missing data, fill and replace

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

In 3.1.0 the removed `DataFrame.pad`, `DataFrame.backfill`, `Series.pad` and `Series.backfill` are gone, as are the method keyword of `DataFrame.fillna`, the downcast keyword of the fill and interpolate methods, and the method and limit keywords of `DataFrame.replace`. Use `DataFrame.ffill` and `DataFrame.bfill` for directional fills, and assign results instead of passing the inplace keyword of `DataFrame.dropna`, which is newly deprecated in 3.1.0.

## Traps

- **Calling `DataFrame.pad` or `Series.pad` to forward-fill missing values.** Call `DataFrame.ffill` or `Series.ffill`. *(since 2.0)*
  > Catalogue: “Series/DataFrame.pad is deprecated. Use Series/DataFrame.ffill instead.”

- **Calling `DataFrame.backfill` or `Series.backfill` to back-fill missing values.** Call `DataFrame.bfill` or `Series.bfill`. *(since 2.0)*
  > Catalogue: “Series/DataFrame.backfill is deprecated. Use Series/DataFrame.bfill instead.”

- **Passing the method keyword to `DataFrame.fillna` or `Series.fillna` with 'ffill' or 'bfill'.** Call `DataFrame.ffill` or `DataFrame.bfill` directly. Keep `DataFrame.fillna` for constant or mapping values. *(since 2.1.0)*
  > Catalogue: “Use ffill or bfill instead.”

- **Passing the downcast keyword to `DataFrame.fillna`, `DataFrame.ffill` or `DataFrame.bfill`, or to the matching `Series` methods.** Drop the downcast keyword. If you need a different dtype, convert the result explicitly afterwards. *(since 2.2.0)*
  > Catalogue: “(axis: 'Axis | None' = None, inplace: 'bool' = False, limit: 'int | None' = None, limit_area: "Literal['inside', 'outside'] | None" = None)”

- **Passing the downcast keyword to `DataFrame.interpolate` or `Series.interpolate`.** Drop the downcast keyword. The other keywords in the signature, including method-specific options passed through **kwargs, still work. *(since 2.1.0)*
  > Catalogue: “(method: 'InterpolateOptions' = 'linear', axis: 'Axis' = 0, limit: 'int | None' = None, inplace: 'bool' = False”

- **Passing the method or limit keywords to `DataFrame.replace` or `Series.replace` to pad replaced values.** Drop the method and limit keywords. The remaining keywords (to_replace, value, regex, inplace) still work. For directional filling, use `DataFrame.ffill` or `DataFrame.bfill` with their limit keyword. *(since 2.1.0)*
  > Catalogue: “(to_replace=None, value=<no_default>, inplace: 'bool' = False, regex: 'bool' = False)”

- **Passing inplace=True to `DataFrame.dropna` or `Series.dropna`, which now emits a deprecation warning.** Assign the returned object, for example df = df.dropna(). *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0.”

## Example

Forward and backward fills via `DataFrame.ffill` and `DataFrame.bfill`, constant fills via `DataFrame.fillna`, `Series.interpolate`, `Series.replace` with regex, and `DataFrame.dropna` with assignment, all without removed names or keywords.

```python
import numpy as np
import pandas as pd

df = pd.DataFrame({"a": [1.0, np.nan, np.nan, 4.0], "b": [np.nan, 2.0, np.nan, 8.0]})

# forward fill: use ffill
fwd = df.ffill()
assert list(fwd["a"]) == [1.0, 1.0, 1.0, 4.0]
assert list(fwd["b"].isna()) == [True, False, False, False]

# limit still works on ffill
limited = df["a"].ffill(limit=1)
assert list(limited.isna()) == [False, False, True, False]

# backward fill: use bfill
back = df.bfill()
assert list(back["a"]) == [1.0, 4.0, 4.0, 4.0]
assert list(back["b"]) == [2.0, 2.0, 8.0, 8.0]

# constant fill per column
const = df.fillna({"a": 0.0, "b": -1.0})
assert list(const["a"]) == [1.0, 0.0, 0.0, 4.0]
assert list(const["b"]) == [-1.0, 2.0, -1.0, 8.0]

# linear interpolation
interp = df["a"].interpolate()
assert list(interp) == [1.0, 2.0, 3.0, 4.0]

# replace with a mapping
s = pd.Series([1, 2, 3])
assert list(s.replace({2: 20})) == [1, 20, 3]

# replace with regex still works
t = pd.Series(["x1", "y2", "x3"])
assert list(t.replace(r"^x", "z", regex=True)) == ["z1", "y2", "z3"]

# dropna: assign the result
cleaned = df.dropna(ignore_index=True)
assert list(cleaned["a"]) == [4.0]
assert list(cleaned["b"]) == [8.0]

print("ok")
```
