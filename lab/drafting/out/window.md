# Windows, shifts and resampling

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

Between 2.3.3 and 3.1.0 the axis keyword was removed from `DataFrame.rolling`, `DataFrame.expanding`, `DataFrame.ewm` and `DataFrame.resample`, along with kind on `DataFrame.resample` and limit on `DataFrame.pct_change`. On the Resampler side, `Resampler.fillna` and `Resampler.grouper` are gone, `Resampler.interpolate` no longer takes inplace or downcast, and `Resampler.get_group` no longer takes obj.

## Traps

- **Passing axis=1 to `DataFrame.rolling` to roll across columns.** Call `DataFrame.rolling` without axis. For column-wise windows, transpose the DataFrame first and then roll. *(since 2.1.0)*
  > Catalogue: “The axis keyword is deprecated. For ``axis=1``, transpose the DataFrame first instead.”

- **Passing axis to `DataFrame.resample`.** Call `DataFrame.resample` on a frame whose row index holds the timestamps. Transpose the frame first if the timestamps are on the columns. *(since 2.0.0)*
  > Catalogue: “Use frame.T.resample(...) instead.”

- **Passing kind='period' or kind='timestamp' to `DataFrame.resample`.** Convert the index to the type you want before calling `DataFrame.resample`. *(since 2.2.0)*
  > Catalogue: “Convert index to desired type explicitly instead.”

- **Passing limit to `DataFrame.pct_change`.** Call `DataFrame.pct_change` with periods and freq only; fill_method accepts only None. If you need gaps filled, fill them yourself before the call. *(since 2.1)*
  > Catalogue: “periods: 'int' = 1, fill_method: 'None' = None, freq=None, **kwargs”

- **Calling `Resampler.fillna` with method='ffill', 'bfill' or 'nearest' after upsampling.** Call `Resampler.ffill`, `Resampler.bfill` or `Resampler.nearest` directly. Each takes an optional limit. *(since 3.1.0)*
  > Catalogue: “Fill missing values introduced by upsampling.”

- **Calling `Resampler.get_group` with obj=df.** Call `Resampler.get_group` with the group name only, or use the positions from `Resampler.indices` to select rows from the frame yourself. *(since 2.1.0)*
  > Catalogue: “The obj is deprecated and will be removed in a future version.”

- **Passing downcast to `Resampler.interpolate`.** Call `Resampler.interpolate` without downcast and change dtypes in a separate step if needed. *(since 2.1.0)*
  > Catalogue: “method: 'InterpolateOptions' = 'linear', axis: 'Axis' = 0, limit: 'int | None' = None”

- **Passing axis to `DataFrame.expanding` or `DataFrame.ewm`.** Call `DataFrame.expanding` and `DataFrame.ewm` without axis. Transpose the DataFrame first for column-wise windows. *(since 3.1.0)*
  > Catalogue: “(min_periods: 'int' = 1, method:”

## Example

Rolling, expanding, downsampling, upsampling with ffill and interpolate, and pct_change, all written without removed keywords or the removed Resampler fill method.

```python
from datetime import datetime, timedelta
import pandas as pd

idx = [datetime(2024, 1, 1) + timedelta(hours=h) for h in range(6)]
df = pd.DataFrame({"x": [1.0, 2.0, None, 4.0, 5.0, 6.0]}, index=idx)

# rolling without the removed axis keyword
roll = df.rolling(2, min_periods=1).sum()
assert list(roll["x"]) == [1.0, 3.0, 2.0, 4.0, 9.0, 11.0]

# expanding without axis
exp = df.expanding().sum()
assert list(exp["x"]) == [1.0, 3.0, 3.0, 7.0, 12.0, 18.0]

# downsample without axis or kind
r = df.resample("2h").sum()
assert list(r["x"]) == [3.0, 4.0, 11.0]

# upsample: use ffill instead of the removed fillna with a method argument
df2 = pd.DataFrame({"y": [10.0, 20.0]}, index=idx[:2])
up = df2.resample("30min").ffill()
assert list(up["y"]) == [10.0, 10.0, 20.0]

# interpolate returns a new object; no inplace or downcast
interp = df2.resample("30min").interpolate()
assert list(interp["y"]) == [10.0, 15.0, 20.0]

# pct_change without limit; fill_method stays None
p = pd.DataFrame({"p": [100.0, 110.0, 121.0]})
pc = list(p.pct_change()["p"])
assert pc[0] != pc[0]  # first value is NaN
assert abs(pc[1] - 0.1) < 1e-12 and abs(pc[2] - 0.1) < 1e-12

print("ok")
```
