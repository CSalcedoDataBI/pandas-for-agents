# Reading and writing data

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

As of 3.1.0, `pd.read_gbq` is gone, `pd.read_csv` and `pd.read_table` no longer accept `delim_whitespace`, `date_parser`, `infer_datetime_format`, `verbose` or `keep_date_col`, `pd.read_excel` no longer accepts `date_parser`, and `pd.read_parquet` no longer accepts `use_nullable_dtypes`. pandas 3.1.0 also deprecates `float_precision` in `pd.read_csv` and `pd.read_table`, `convert_dates` and `keep_default_dates` in `pd.read_json`, and the 'fastparquet' and 'auto' engines of `pd.read_parquet`.

## Traps

- **Passing the `delim_whitespace` keyword to `pd.read_csv` or `pd.read_table` to split on runs of spaces.** Pass the `sep` keyword with the regex `\s+` to `pd.read_csv` or `pd.read_table`. *(since 2.2.0)*
  > Catalogue: “Use ``sep="\s+"`` instead.”

- **Passing a `date_parser` callable to `pd.read_csv`, `pd.read_table` or `pd.read_excel`.** Pass `date_format` (with `parse_dates`) to the reader, or read the column in as `object` and then apply `pd.to_datetime` as needed when a single format string cannot express the parsing logic. *(since 2.0.0)*
  > Catalogue: “Use ``date_format`` instead, or read in as ``object`` and then apply :func:`~pandas.to_datetime` as-needed.”

- **Passing `infer_datetime_format` to `pd.read_csv` or `pd.read_table`.** Drop the keyword; the strict version is already the default and passing it had no effect. *(since 2.0.0)*
  > Catalogue: “A strict version of this argument is now the default, passing it has no effect.”

- **Calling `pd.read_gbq` to load Google BigQuery data.** Use `pandas_gbq.read_gbq` from the separate pandas-gbq package. *(since 2.2.0)*
  > Catalogue: “Please use ``pandas_gbq.read_gbq`` instead.”

- **Passing `float_precision` to `pd.read_csv` or `pd.read_table`.** Omit `float_precision`; every mode now uses the same converter. *(since 3.1.0)*
  > Catalogue: “All float precision modes now use the same converter. The ``float_precision`` argument will be removed in a future version.”

- **Passing `convert_dates` or `keep_default_dates` to `pd.read_json`.** Pass `dtype=False` to `pd.read_json` to disable type conversion, or parse date columns with `pd.to_datetime` after reading. *(since 3.1.0)*
  > Catalogue: “Pass ``dtype=False`` to disable type conversion, or parse date columns with :func:`~pandas.to_datetime` after reading.”

- **Passing 'fastparquet' or 'auto' as the `engine` of `pd.read_parquet`.** Pass 'pyarrow' as the `engine`, or omit `engine` to use the default. *(since 3.1.0)*
  > Catalogue: “The ``'fastparquet'`` and ``'auto'`` engine options are deprecated. Use ``'pyarrow'`` or do not pass ``engine`` to use the default.”

## Example

Reads whitespace-separated text with `pd.read_csv` using `sep` with a regex instead of the whitespace flag that is no longer accepted, parses dates with `parse_dates` and `date_format` instead of a parser callable, and reads a TSV with `pd.read_table` without `float_precision`.

```python
from io import StringIO
import pandas as pd

raw = "date value\n2024-01-05 10\n2024-02-10 20\n2024-03-15 30\n"
# old code used the whitespace flag and a date parser callable; neither keyword is accepted as of 3.1.0
df = pd.read_csv(StringIO(raw), sep=r"\s+", parse_dates=["date"], date_format="%Y-%m-%d")
assert list(df.columns) == ["date", "value"]
assert df.shape == (3, 2)
assert "datetime64" in str(df["date"].dtype)
assert df["value"].tolist() == [10, 20, 30]

tsv = "name\tscore\na\t1.5\nb\t2.5\n"
# no float precision keyword: all modes use the same converter in 3.1.0
t = pd.read_table(StringIO(tsv))
assert t["score"].tolist() == [1.5, 2.5]
assert t.shape == (2, 2)
print("ok")
```
