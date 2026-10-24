# Series-only members

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

pandas 3.1.0 removes `Series.ravel` and `Series.view` from Series; both were deprecated in 2.2.0. The other Series-only members in the catalogue keep their 2.3.3 form, and no keyword arguments were removed from this group.

## Traps

- **Calling `Series.ravel` to get the Series data as a numpy array.** Use `Series.to_numpy`. A Series is already 1D, so no flattening step is needed. *(since 2.2.0)*
  > Catalogue: “Use :meth:`to_numpy` for conversion to a numpy array instead.”

- **Calling `Series.ravel` to get the underlying ExtensionArray of an extension-dtype Series.** Use `Series.array` to get the backing array directly, or `Series.to_numpy` when a numpy array is needed. *(since 2.2.0)*
  > Catalogue: “Return the flattened underlying data as an ndarray or ExtensionArray.”

- **Calling `Series.view` with a dtype to reinterpret or change the dtype of a Series.** Use `Series.astype` to change the dtype. *(since 2.2.0)*
  > Catalogue: “``Series.view`` is deprecated and will be removed in a future version. Use :meth:`Series.astype` as an alternative to change the dtype.”

## Example

The script gets a numpy array with `Series.to_numpy` instead of the removed flattening method, reads the backing array with `Series.array`, and changes the dtype with `Series.astype` instead of the removed view method.

```python
import numpy as np
import pandas as pd

s = pd.Series([3, 9, 1, 7], index=["a", "b", "c", "d"], name="v")

# A Series is already 1D: convert with to_numpy, no flattening call needed.
arr = s.to_numpy()
assert isinstance(arr, np.ndarray)
assert arr.ndim == 1
assert arr.tolist() == [3, 9, 1, 7]

# The backing array of an extension dtype Series.
m = pd.Series([1, None, 3], dtype="Int64")
back = m.array
assert len(back) == 3
assert str(back.dtype) == "Int64"

# Change the dtype with astype.
f = s.astype("float64")
assert f.dtype == np.dtype("float64")
assert f.to_list() == [3.0, 9.0, 1.0, 7.0]
print("ok")
```
