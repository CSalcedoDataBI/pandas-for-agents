# Other top-level functions: conversion, dates, options

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

Between 2.3.3 and 3.1.0 pandas removed several old keyword arguments from conversion and index constructors, such as `infer_datetime_format` in `pd.to_datetime` and `unit` in `pd.TimedeltaIndex`. It also deprecated the `dayfirst`, `yearfirst` and `ambiguous` keywords of `pd.DatetimeIndex`, numeric input combined with `format` in `pd.to_datetime`, `inplace` in `pd.eval`, `pd.set_eng_float_format`, and the string return value of `pd.infer_freq`.

## Traps

- **Passing `infer_datetime_format=True` to `pd.to_datetime`.** Drop the keyword. Strict format inference is already the default. Pass an explicit `format` when you know it. *(since 2.0.0)*
  > Catalogue: “A strict version of this argument is now the default, passing it has no effect.”

- **Building durations with `pd.TimedeltaIndex` and its `unit` keyword, for example from raw seconds.** Convert with `pd.to_timedelta(values, unit="s")`, then wrap the result in `pd.TimedeltaIndex` if you need an index. *(since 2.2.0)*
  > Catalogue: “Use ``pd.to_timedelta`` instead.”

- **Parsing date strings through `pd.DatetimeIndex` with `dayfirst` or `yearfirst`.** Parse with `pd.to_datetime(values, dayfirst=True)` or `pd.to_datetime(values, yearfirst=True)`, then pass the result to `pd.DatetimeIndex`. *(since 3.1.0)*
  > Catalogue: “Use :func:`to_datetime` instead.”

- **Calling `pd.to_datetime` on integer or float values such as 20240105 together with `format="%Y%m%d"`.** Keep or cast the values as strings before passing `format`. Use `unit` for numeric epochs. *(since 3.1.0)*
  > Catalogue: “Passing integer or float values together with ``format`` is deprecated; cast them to strings first.”

- **Using `inplace=True` with `pd.eval`.** Leave out `inplace` and use the object that `pd.eval` returns. *(since 3.1.0)*
  > Catalogue: “This keyword is deprecated and will be removed in pandas 4.0.”

- **Calling `pd.set_eng_float_format` to format floats in output.** Use `pd.set_option` with "display.precision", or pass a callable for "display.float_format". Use `pd.option_context` for a temporary change. *(since 3.1.0)*
  > Catalogue: “to control decimal precision, or pass a custom callable to”

- **Writing the deprecated unit aliases "w", "d", "MIN", "MS", "US" or "NS" in `pd.Timedelta`.** Use the canonical aliases "W", "D", "min", "ms", "us" and "ns": only weeks and days are uppercase; minutes and sub-second units are lowercase. *(since 3.0.0)*
  > Catalogue: “Allowing the values `w`, `d`, `MIN`, `MS`, `US` and `NS` to denote units are deprecated”

- **Relying on `pd.infer_freq` to return a string such as "D".** Opt in with `pd.set_option` and "future.infer_freq_returns_offset" set to True, and handle an offset object as the result. *(since 3.1.0)*
  > Catalogue: “A future version of pandas will return a :class:`BaseOffset` instead of a string.”

## Example

Parses day-first dates with `pd.to_datetime` and no removed keywords, then wraps them in `pd.DatetimeIndex`. Keeps numeric date codes as strings when passing `format`. Builds durations with `pd.to_timedelta` instead of the removed `unit` keyword of `pd.TimedeltaIndex`. Uses the canonical unit aliases "D" and "s" rather than deprecated spellings such as "d" or "MIN". Controls display precision through `pd.option_context`, `pd.set_option`, `pd.get_option` and `pd.reset_option`.

```python
import pandas as pd

df = pd.DataFrame({"when": ["03/04/2024", "15/04/2024"], "code": ["20240105", "20240210"], "secs": [90, 30]})

# The infer_datetime_format keyword is removed; strict inference is already the default.
when = pd.to_datetime(df["when"], dayfirst=True)
assert list(when) == [pd.Timestamp(2024, 4, 3), pd.Timestamp(2024, 4, 15)]

# The dayfirst keyword of DatetimeIndex is deprecated: parse first, then wrap.
idx = pd.DatetimeIndex(when)
assert list(idx) == list(when)

# Numbers combined with format are deprecated: keep the codes as strings.
codes = pd.to_datetime(df["code"], format="%Y%m%d")
assert list(codes) == [pd.Timestamp(2024, 1, 5), pd.Timestamp(2024, 2, 10)]

# The unit keyword of TimedeltaIndex is removed: convert with to_timedelta.
td = pd.TimedeltaIndex(pd.to_timedelta(df["secs"], unit="s"))
assert list(td) == [pd.Timedelta(90, unit="s"), pd.Timedelta(30, unit="s")]

# Canonical aliases: "D" for days (not "d"), lowercase "min", "ms", "us", "ns".
assert pd.Timedelta(1, unit="D") == pd.Timedelta(hours=24)
assert pd.Timedelta(2, unit="min") == pd.Timedelta(seconds=120)

# Use display options instead of set_eng_float_format.
with pd.option_context("display.precision", 2):
    assert pd.get_option("display.precision") == 2
pd.set_option("display.precision", 3)
assert pd.get_option("display.precision") == 3
pd.reset_option("display.precision")
assert pd.get_option("display.precision") == 6
print("ok")
```
