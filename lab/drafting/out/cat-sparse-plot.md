# The .cat, .sparse and .plot accessors

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

Between 2.3.3 and 3.1.0 the `Series.cat` methods lost their args and kwargs parameters, so each method accepts only the parameters in its 3.1.0 signature. The excerpt lists no removed names or keyword arguments for the `Series.sparse`, `DataFrame.sparse` and `Series.plot` accessors.

## Traps

- **Passing arguments other than new_categories, ordered and rename to `Series.cat.set_categories`, relying on the old args and kwargs parameters.** Pass only new_categories, ordered and rename, then assign the returned Series: s = s.cat.set_categories([...]). *(since 3.1.0)*
  > Catalogue: “(new_categories, ordered=None, rename: 'bool' = False)”

- **Passing arguments other than new_categories and ordered to `Series.cat.reorder_categories`, relying on the old args and kwargs parameters.** Pass new_categories and, if needed, ordered=..., then assign the returned Series. *(since 3.1.0)*
  > Catalogue: “(new_categories, ordered=None)”

- **Passing anything besides new_categories to `Series.cat.rename_categories`, relying on the old args and kwargs parameters.** Pass only new_categories and assign the returned Series. *(since 3.1.0)*
  > Catalogue: “(new_categories)”

- **Passing anything besides new_categories to `Series.cat.add_categories`, relying on the old args and kwargs parameters.** Pass only new_categories and assign the returned Series. *(since 3.1.0)*
  > Catalogue: “(new_categories)”

- **Passing anything besides removals to `Series.cat.remove_categories`, relying on the old args and kwargs parameters.** Pass only removals and assign the returned Series. *(since 3.1.0)*
  > Catalogue: “(removals)”

## Example

Chains the `Series.cat` methods, passing only parameters that exist in their 3.1.0 signatures. It assigns each returned Series and asserts on the categories, codes and ordering.

```python
import pandas as pd

s = pd.Series(["b", "a", "c", "a"], dtype="category")

# Each call below uses only parameters present in its 3.1.0 signature.
# set_categories also accepts ordered and rename; the old args/kwargs parameters are gone.
s = s.cat.set_categories(["a", "b", "c", "d"])
assert list(s.cat.categories) == ["a", "b", "c", "d"]

s = s.cat.remove_unused_categories()
assert list(s.cat.categories) == ["a", "b", "c"]

s = s.cat.add_categories(["z"])
s = s.cat.reorder_categories(["c", "b", "a", "z"], ordered=True)
assert s.cat.ordered
assert list(s.cat.codes) == [1, 2, 0, 2]

s = s.cat.rename_categories(["c", "b", "a", "zz"])
assert list(s.cat.categories) == ["c", "b", "a", "zz"]
s = s.cat.remove_categories(["zz"])
assert list(s.cat.categories) == ["c", "b", "a"]

s = s.cat.as_unordered()
assert not s.cat.ordered
s = s.cat.as_ordered()
assert s.cat.ordered
print("ok")
```
