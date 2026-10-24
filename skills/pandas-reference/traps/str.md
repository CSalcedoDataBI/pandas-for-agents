# The .str accessor

*pandas 2.3.3 → 3.1.0. Drafted with Claude from the exported catalogue; every name and every evidence quote is checked by script.*

Between 2.3.3 and 3.1.0 the catalogue records one change for the `.str` accessor: the kwargs parameter of `Series.str.wrap` is gone, and no `Series.str` method was removed. Textwrap options must now be passed as the named keywords in the 3.1.0 `Series.str.wrap` signature; for the other `Series.str` methods the catalogue lists only the current signatures.

## Traps

- **Passing arbitrary extra keyword arguments through `Series.str.wrap` to textwrap, relying on its old kwargs catch-all.** Pass only the named parameters in the `Series.str.wrap` signature, such as width, break_long_words, max_lines and placeholder. The kwargs parameter was removed after 2.3.3 and is absent by 3.1.0; the signature ends at placeholder. *(since 3.1.0)*
  > Catalogue: “max_lines: 'int | None' = None, placeholder: 'str' = ' [...]')”

- **Passing a regular expression to `Series.str.replace` without setting regex, expecting it to be treated as a regex.** Pass regex=True when pat is a regular expression and regex=False when it is a literal string. The signature default is regex=False. *(since 3.1.0)*
  > Catalogue: “case: 'bool | None' = None, flags: 'int' = 0, regex: 'bool' = False”

- **Leaving na unset in `Series.str.contains` on data with missing values and then filtering with the result.** Pass na=False (or na=True) so your code sets the result for missing entries. The default is the <no_default> sentinel, and the catalogue does not say what it resolves to. *(since 3.1.0)*
  > Catalogue: “flags: 'int' = 0, na=<no_default>, regex: 'bool' = True”

- **Combining several `Series.str.startswith` or `Series.str.endswith` calls with | to test more than one prefix or suffix.** Pass a tuple of strings as pat in a single call, which the signature accepts. Pass na explicitly as well. *(since 3.1.0)*
  > Catalogue: “pat: 'str | tuple[str, ...]'”

- **Using `Series.str.match` to check that a whole string fits a pattern.** Use `Series.str.fullmatch` for whole-string checks. `Series.str.match` only requires a match at the start, so trailing characters still pass. *(since 3.1.0)*
  > Catalogue: “Determine if each string starts with a match of a regular expression.”

- **Calling `Series.str.cat` with another Series that has a different index and expecting a purely positional concatenation.** Remember that others are aligned using join, which defaults to 'left'. Pass join explicitly, and pass na_rep to set the text used for missing parts. *(since 3.1.0)*
  > Catalogue: “na_rep=None, join: 'AlignJoin' = 'left'”

## Example

Calls the `.str` accessor with explicit regex, na and join keywords and only named `Series.str.wrap` parameters, and asserts each result.

```python
import pandas as pd

# replace: state regex explicitly for both regex and literal patterns
s = pd.Series(["apple pie", "Banana-split", "cherry tart"])
r = s.str.replace(r"[-\s]+", "_", regex=True)
assert r.tolist() == ["apple_pie", "Banana_split", "cherry_tart"]
lit = pd.Series(["a.b", "axb"]).str.replace(".", "-", regex=False)
assert lit.tolist() == ["a-b", "axb"]

# contains / startswith: set na yourself; startswith takes a tuple of prefixes
m = pd.Series(["apple", "Banana", None, "cherry"])
mask = m.str.contains("an", case=False, na=False)
assert mask.tolist() == [False, True, False, False]
starts = m.str.startswith(("apple", "cherry"), na=False)
assert starts.tolist() == [True, False, False, True]

# match needs a match at the start only; fullmatch checks the whole string
d = pd.Series(["2024-01-05", "2024-01-05x"])
assert d.str.match(r"\d{4}-\d{2}-\d{2}").tolist() == [True, True]
assert d.str.fullmatch(r"\d{4}-\d{2}-\d{2}").tolist() == [True, False]

# split: state whether the pattern is a regex
parts = pd.Series(["a1b22c"]).str.split(r"\d+", regex=True, expand=True)
assert parts.iloc[0].tolist() == ["a", "b", "c"]

# wrap: only the named textwrap parameters are accepted
w = pd.Series(["the quick brown fox"]).str.wrap(width=10, break_long_words=False)
assert w.iloc[0] == "the quick\nbrown fox"

# cat aligns others using join; set join and na_rep explicitly
left = pd.Series(["a", "b"], index=[0, 1])
right = pd.Series(["x", "y"], index=[1, 2])
c = left.str.cat(right, sep="-", na_rep="?", join="left")
assert c.tolist() == ["a-?", "b-x"]
print("ok")
```
