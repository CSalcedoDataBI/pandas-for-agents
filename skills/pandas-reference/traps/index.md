# Index

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

pandas 3.1.0 removes the `Index` dtype-check methods deprecated in 2.0.0 (`Index.is_integer`, `Index.is_floating`, `Index.is_numeric`, `Index.is_boolean`, `Index.is_object`, `Index.is_categorical`, `Index.is_interval`, `Index.holds_integer`); the excerpt also lists `Index.sort` and `Index.format` as removed. The downcast keyword of `Index.fillna`, deprecated in 2.1.0, is gone, so `Index.fillna` now takes only a value.

## Traps

- **Calling `Index.is_integer` to test for an integer index.** Pass the dtype to `pandas.api.types.is_integer_dtype`. *(since 2.0.0)*
  > Catalogue: “Use `pandas.api.types.is_integer_dtype` instead.”

- **Calling `Index.is_floating` (or `Index.is_numeric`) to test for float or numeric data.** Use `pandas.api.types.is_float_dtype`, or `pandas.api.types.is_numeric_dtype` for any numeric dtype. *(since 2.0.0)*
  > Catalogue: “Use `pandas.api.types.is_float_dtype` instead”

- **Calling `Index.is_boolean` to test for a boolean index.** Pass the dtype to `pandas.api.types.is_bool_dtype`. *(since 2.0.0)*
  > Catalogue: “Use `pandas.api.types.is_bool_dtype` instead.”

- **Calling `Index.is_object` to test for object dtype.** Pass the dtype to `pandas.api.types.is_object_dtype`. *(since 2.0.0)*
  > Catalogue: “Use `pandas.api.types.is_object_dtype` instead.”

- **Calling `Index.is_categorical`, or replacing it with `pandas.api.types.is_categorical_dtype`, which is deprecated since 2.2.0 and warns.** Check `isinstance(idx.dtype, pandas.api.types.CategoricalDtype)`. *(since 2.0.0)*
  > Catalogue: “Use `isinstance(index.dtype, pd.CategoricalDtype)` instead.”

- **Calling `Index.is_interval`, or `pandas.api.types.is_interval_dtype`, which is deprecated since 2.2.0.** Check `isinstance(idx.dtype, pandas.api.types.IntervalDtype)`. *(since 2.0.0)*
  > Catalogue: “Use `isinstance(index.dtype, pd.IntervalDtype)` instead.”

- **Calling `Index.holds_integer` to see whether the labels are integers.** Call `pandas.api.types.infer_dtype` on the index and inspect the string label it returns. *(since 2.0.0)*
  > Catalogue: “Use `pandas.api.types.infer_dtype` instead”

- **Passing the downcast keyword to `Index.fillna`.** Call `Index.fillna` with only the value, then cast explicitly with `Index.astype` if you need another dtype. *(since 2.1.0)*
  > Catalogue: “"target": "parameter:downcast"”

## Example

The script replaces the removed `Index` type checks with `pandas.api.types.is_integer_dtype`, `pandas.api.types.is_float_dtype`, `pandas.api.types.is_numeric_dtype`, `pandas.api.types.is_bool_dtype`, `pandas.api.types.is_object_dtype`, `pandas.api.types.infer_dtype` and a dtype isinstance check, then fills missing values without downcast and casts with `Index.astype`. It runs cleanly with warnings treated as errors.

```python
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype, infer_dtype, is_bool_dtype, is_float_dtype, is_integer_dtype, is_numeric_dtype, is_object_dtype

ints = pd.Index([3, 1, 2])
floats = pd.Index([1.5, np.nan, 0.5])
bools = pd.Index([True, False, True])
objs = pd.Index([1, "a"], dtype=object)

# old Index.is_integer: check the dtype instead
assert is_integer_dtype(ints.dtype)
# old Index.is_floating and Index.is_numeric
assert is_float_dtype(floats.dtype)
assert is_numeric_dtype(floats.dtype)
# old Index.is_boolean and Index.is_object
assert is_bool_dtype(bools.dtype)
assert is_object_dtype(objs.dtype)
assert not is_object_dtype(ints.dtype)
# old Index.holds_integer: infer_dtype returns a string label
label = infer_dtype(ints)
assert isinstance(label, str)
assert label == "integer"

# old Index.is_categorical: isinstance check on the dtype
cats = pd.Index(["a", "b", "a"]).astype("category")
assert isinstance(cats.dtype, CategoricalDtype)
assert not isinstance(ints.dtype, CategoricalDtype)

# sorting uses sort_values, which returns a sorted copy
assert ints.sort_values().tolist() == [1, 2, 3]

# fillna takes only a value: fill, then cast explicitly
filled = floats.fillna(0.0)
assert not filled.hasnans
assert filled.tolist() == [1.5, 0.0, 0.5]
as_int = pd.Index([1.0, np.nan]).fillna(0.0).astype("int64")
assert is_integer_dtype(as_int.dtype)
assert as_int.tolist() == [1, 0]
print("ok")
```
