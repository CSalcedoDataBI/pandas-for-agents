# Top-level merge, concat and reshape

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

The top-level `pd.value_counts` function present in 2.3.3 is gone in 3.1.0. Use `Series.value_counts` instead, which takes the same counting options. Since 3.0.0 the `copy` keyword of `pd.concat` and `pd.merge` is deprecated and ignored, because these functions always return a new object that uses lazy Copy-on-Write copies.

## Traps

- **Calling the top-level `pd.value_counts` function to count values. It is absent in 3.1.0.** Wrap the values in a Series and call `Series.value_counts`. It accepts the same `normalize`, `sort`, `ascending`, `bins` and `dropna` arguments and returns counts sorted in descending order. *(since 3.1.0)*
  > Catalogue: “(values, sort: 'bool' = True, ascending: 'bool' = False, normalize: 'bool' = False, bins=None, dropna: 'bool' = True)”

- **Passing `copy=False` or `copy=True` to `pd.concat` to control memory use. Since 3.0.0 the keyword is deprecated and ignored, and it is scheduled for removal in pandas 4.0.** Omit `copy` from `pd.concat`. Copy-on-Write already defers copies until they are needed. *(since 3.0.0)*
  > Catalogue: “This keyword is ignored and will be removed in pandas 4.0.”

- **Passing `copy=False` to `pd.merge` and expecting the result to share memory with the inputs, or to write back into them.** Omit `copy` from `pd.merge`. Treat the merged frame as a new object: modifying it in place never changes `left` or `right`. *(since 3.0.0)*
  > Catalogue: “Since pandas 3.0, this method always returns a new object using a lazy copy mechanism that defers copies until necessary (Copy-on-Write).”

## Example

Calls `pd.merge` and `pd.concat` without the deprecated `copy` keyword. It modifies each result in place with `.loc` and asserts that the inputs are unchanged. It also counts values with `Series.value_counts` in place of the removed top-level counting function, using the `normalize` and `dropna` options.

```python
import pandas as pd

left = pd.DataFrame({"key": ["a", "b", "c"], "x": [1, 2, 3]})
right = pd.DataFrame({"key": ["a", "b", "d"], "y": [10, 20, 40]})

# Old code passed a copy keyword here; it is ignored since 3.0, so omit it.
merged = pd.merge(left, right, on="key", how="inner", validate="one_to_one")
assert list(merged["key"]) == ["a", "b"]
assert list(merged["y"]) == [10, 20]

# In-place change of the result does not reach the input (Copy-on-Write).
merged.loc[0, "x"] = 100
assert list(merged["x"]) == [100, 2]
assert list(left["x"]) == [1, 2, 3]

# Concatenate without the copy keyword.
more = pd.DataFrame({"key": ["e"], "x": [5]})
stacked = pd.concat([left, more], ignore_index=True)
assert list(stacked["key"]) == ["a", "b", "c", "e"]
stacked.loc[0, "x"] = -1
assert list(stacked["x"]) == [-1, 2, 3, 5]
assert list(left["x"]) == [1, 2, 3]

# Count values with the Series method (the top-level function is gone).
values = pd.Series(["a", "b", "a", None, "a"])
counts = values.value_counts()
assert list(counts.index) == ["a", "b"]
assert list(counts) == [3, 1]

shares = values.value_counts(normalize=True)
assert list(shares) == [0.75, 0.25]

with_missing = values.value_counts(dropna=False)
assert int(with_missing.sum()) == 5
assert len(with_missing) == 3
print("ok")
```
