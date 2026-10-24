# The .dt accessor

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

Between 2.3.3 and 3.1.0 no `.dt` member was removed, but the catch-all *args/**kwargs were removed from methods such as `Series.dt.round`, `Series.dt.tz_localize`, `Series.dt.strftime` and `Series.dt.to_timestamp`, so they accept only their named parameters. In 3.1.0 the legacy aliases `Series.dt.dayofweek`, `Series.dt.weekday`, `Series.dt.dayofyear` and `Series.dt.daysinmonth` are deprecated, and on datetime and timedelta Series `Series.dt.freq` is deprecated because it will return an offset object instead of a string.

## Traps

- **Using `Series.dt.dayofweek` or `Series.dt.weekday` for the weekday number (Monday=0).** Use `Series.dt.day_of_week`. *(since 3.1.0)*
  > Catalogue: “Use :attr:`Series.dt.day_of_week` instead.”

- **Using `Series.dt.dayofyear` for the ordinal day.** Use `Series.dt.day_of_year`. *(since 3.1.0)*
  > Catalogue: “Use :attr:`Series.dt.day_of_year` instead.”

- **Using `Series.dt.daysinmonth` for the month length.** Use `Series.dt.days_in_month`. *(since 3.1.0)*
  > Catalogue: “Use :attr:`Series.dt.days_in_month` instead.”

- **On a datetime or timedelta Series, reading `Series.dt.freq` and treating the result as a string. This member is deprecated for those dtypes. On a period Series, `Series.dt.freq` is not deprecated and already returns the frequency object.** For datetime and timedelta Series, do not depend on `Series.dt.freq` returning a string. Opt in to the future behavior with the future.infer_freq_returns_offset option and handle an offset or None. *(since 3.1.0)*
  > Catalogue: “A future version of pandas will return a :class:`BaseOffset` object (or ``None``) instead of a string.”

## Example

Uses the current names `Series.dt.day_of_week`, `Series.dt.day_of_year` and `Series.dt.days_in_month`, and calls `Series.dt.round`, `Series.dt.floor`, `Series.dt.day_name` and `Series.dt.total_seconds` with only their named parameters. The asserts check each result.

```python
import pandas as pd

s = pd.Series(["2024-02-28 10:40:00", "2024-02-29 23:10:00", "2024-03-03 08:05:00"], dtype="datetime64[ns]")

# old aliases dayofweek / weekday / dayofyear / daysinmonth are deprecated in 3.1.0
assert list(s.dt.day_of_week) == [2, 3, 6]
assert list(s.dt.day_of_year) == [59, 60, 63]
assert list(s.dt.days_in_month) == [29, 29, 31]

# round/floor accept only freq, ambiguous, nonexistent (no extra *args/**kwargs)
rounded = s.dt.round("h", ambiguous="raise", nonexistent="raise")
assert list(rounded.dt.hour) == [11, 23, 8]
floored = s.dt.floor("D")
assert list(floored.dt.day) == [28, 29, 3]
assert list(floored.dt.hour) == [0, 0, 0]

assert list(s.dt.day_name(locale=None)) == ["Wednesday", "Thursday", "Sunday"]

td = pd.Series(["1 days 02:30:00", "0 days 00:00:45"], dtype="timedelta64[ns]")
assert list(td.dt.total_seconds()) == [95400.0, 45.0]
assert list(td.dt.days) == [1, 0]

print("ok")
```
