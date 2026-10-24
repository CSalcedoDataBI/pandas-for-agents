# DataFrame: selection, indexing and labels

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

`DataFrame.bool`, `DataFrame.first` and `DataFrame.last` were deprecated in 2.1 and removed in pandas 3, so they are absent in 3.1.0. The copy keyword on `DataFrame.reindex`, `DataFrame.rename`, `DataFrame.set_axis` and `DataFrame.truncate` has been ignored and deprecated since 3.0.0, and the inplace keyword on `DataFrame.drop`, `DataFrame.drop_duplicates` and `DataFrame.rename` is deprecated in 3.1.0.

## Traps

- **Calling `DataFrame.bool` to get the truth value of a single-element object.** For a Series, the deprecation note names `Series.item` as the replacement. It gives no DataFrame replacement. As an unofficial workaround for a one-element DataFrame, read the cell with `DataFrame.iat` and pass it to Python's built-in bool(). *(since 2.1.0)*
  > Catalogue: “bool is deprecated and will be removed in future version of pandas. For ``Series`` use ``pandas.Series.item``.”

- **Calling `DataFrame.first` with a date offset to keep the initial period of a time series.** Build a boolean mask on the index or a column and select the rows with `DataFrame.loc`. *(since 2.1)*
  > Catalogue: “:meth:`.first` is deprecated and will be removed in a future version. Please create a mask and filter using `.loc` instead.”

- **Calling `DataFrame.last` with a date offset to keep the final period of a time series.** Build a boolean mask and select the rows with `DataFrame.loc`. *(since 2.1)*
  > Catalogue: “:meth:`.last` is deprecated and will be removed in a future version. Please create a mask and filter using `.loc` instead.”

- **Passing inplace=True to `DataFrame.drop`, `DataFrame.drop_duplicates` or `DataFrame.rename`. This keyword is deprecated in 3.1.0 and now emits a deprecation warning.** Omit the keyword and reassign the result, for example df = df.drop(columns=[...]). *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0. See the `whatsnew note on PDEP-8”

- **Passing copy=True or copy=False to `DataFrame.reindex`, `DataFrame.rename`, `DataFrame.set_axis` or `DataFrame.truncate`.** Omit the keyword. Under Copy-on-Write these methods already return a new object and copy lazily. *(since 3.0.0)*
  > Catalogue: “This keyword is ignored and will be removed in pandas 4.0. Since pandas 3.0, this method always returns a new object using a lazy copy mechanism”

## Example

The script replaces the old offset-based first/last selection with a boolean mask and `DataFrame.loc`. It reassigns results instead of passing inplace or copy. It gets a single truth value through `DataFrame.iat` plus built-in bool(), which is an unofficial workaround.

```python
import pandas as pd

df = pd.DataFrame({"day": [1, 2, 3, 4, 5], "value": [10, 20, 30, 40, 50]})

# old offset-based first/last selection: use a boolean mask with .loc
early = df.loc[df["day"] <= 2]
assert len(early) == 2
late = df.loc[df["day"] >= 4]
assert late.iat[0, 1] == 40

# no inplace keyword: reassign the returned frame
df = df.drop(columns=["day"])
assert list(df) == ["value"]
df = df.rename(columns={"value": "amount"})
assert list(df) == ["amount"]
df = df.drop_duplicates()
assert len(df) == 5

# no copy keyword: reindex already returns a new object
reindexed = df.reindex([0, 1, 9], fill_value=0)
assert reindexed.at[9, "amount"] == 0
assert df.at[0, "amount"] == 10

# truth value of a single cell without the removed bool method (unofficial workaround)
single = df.loc[df["amount"] == 30]
flag = bool(single.iat[0, 0] == 30)
assert flag is True
```
