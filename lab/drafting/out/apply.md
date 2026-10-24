# DataFrame: apply, map, transform and eval

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

In 3.1.0 `DataFrame.applymap` is removed in favour of `DataFrame.map`, and `DataFrame.query` no longer accepts arbitrary **kwargs. The inplace keyword of `DataFrame.eval` and `DataFrame.query` is deprecated as of 3.1.0, so assign the returned DataFrame instead.

## Traps

- **Calling `DataFrame.applymap` to apply a function to every element.** Call `DataFrame.map` with the same function. Pass na_action="ignore" if NaN should be skipped. *(since 2.1.0)*
  > Catalogue: “DataFrame.applymap has been deprecated. Use DataFrame.map instead.”

- **Passing inplace=True to `DataFrame.eval` to add or change a column on the existing frame.** Leave out inplace and assign the result, for example df = df.eval("c = a + b"). *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0.”

- **Passing inplace=True to `DataFrame.query` to filter rows on the existing frame.** Leave out inplace and assign the returned frame, for example df = df.query("a > 1"). *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0. See the `whatsnew note on PDEP-8”

- **Passing extra, unnamed keyword arguments to `DataFrame.query`; its **kwargs are gone in 3.1.0.** Pass only the named parameters of `DataFrame.query`: parser, engine, local_dict, global_dict, resolvers and level. Supply variable values through local_dict or global_dict. *(since 3.1.0)*
  > Catalogue: “resolvers: 'list[Mapping] | None' = None, level: 'int' = 0, inplace: 'bool | lib.NoDefault' = <no_default>)”

## Example

Elementwise work with `DataFrame.map`, then `DataFrame.eval` and `DataFrame.query` with their results assigned instead of using inplace, and a query variable supplied through local_dict.

```python
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3], "b": [10.0, 20.0, float("nan")]})

# elementwise function: use DataFrame.map (the old elementwise method name is removed)
doubled = df.map(lambda x: x * 2, na_action="ignore")
assert doubled["a"].tolist() == [2, 4, 6]
assert doubled["b"].isna().sum() == 1

# eval returns a new frame; assign it instead of modifying in place
df2 = df.eval("c = a + b")
assert "c" not in df.columns
assert df2["c"].iloc[0] == 11

# query returns a new frame; assign it
small = df2.query("a >= 2", parser="pandas")
assert small["a"].tolist() == [2, 3]

# variable values go through local_dict, a named parameter
res = df.query("a > @t", local_dict={"t": 1})
assert len(res) == 2
print("ok")
```
