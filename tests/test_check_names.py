"""Tests for scripts/check_names.py against the committed catalogue. Run: python -m unittest"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check_names  # noqa: E402

CAT = check_names.Catalogue()


def errors(text: str) -> list[str]:
    return check_names.check_text(CAT, text, "card.md")


class InlineNames(unittest.TestCase):
    def test_current_names_pass(self):
        self.assertEqual(errors("Use `DataFrame.map`, `pd.merge` and `Series.str.contains`."), [])

    def test_removed_name_is_allowed_in_prose(self):
        self.assertEqual(errors("`DataFrame.applymap` is gone; use `DataFrame.map`."), [])

    def test_invented_name_fails(self):
        self.assertEqual(len(errors("Call `DataFrame.smart_merge` first.")), 1)

    def test_groupby_alias(self):
        self.assertEqual(errors("`GroupBy.agg` and `GroupBy.kurt`."), [])


class CodeBlocks(unittest.TestCase):
    def block(self, code: str) -> list[str]:
        return errors(f"```python\n{code}\n```\n")

    def test_valid_example_passes(self):
        code = (
            "import pandas as pd\n"
            "df = pd.DataFrame({'k': ['a', 'b'], 'v': [1, 2]})\n"
            "out = df.groupby('k').agg(total=('v', 'sum'))\n"
            "mask = df['k'].str.contains('a', case=False)\n"
            "filled = df.ffill()\n"
        )
        self.assertEqual(self.block(code), [])

    def test_removed_method_fails_in_code(self):
        found = self.block("df.applymap(str)")
        self.assertEqual(len(found), 1)
        self.assertIn("removed", found[0])

    def test_removed_keyword_fails(self):
        found = self.block("df.fillna(method='ffill')")
        self.assertEqual(len(found), 1)
        self.assertIn("method", found[0])

    def test_invented_top_level_fails(self):
        self.assertEqual(len(self.block("pd.read_magic('x')")), 1)

    def test_accessor_member_checked(self):
        self.assertEqual(len(self.block("s.str.reverse()")), 1)

    def test_foreign_module_ignored(self):
        self.assertEqual(self.block("import numpy as np\nx = np.arange(3)"), [])

    def test_api_types_checked(self):
        self.assertEqual(self.block("pd.api.types.is_integer_dtype(s)"), [])
        self.assertEqual(len(self.block("pd.api.types.is_magic_dtype(s)")), 1)
        self.assertEqual(errors("Use `pandas.api.types.is_float_dtype`."), [])
        self.assertEqual(errors("The checks live in `pandas.api.types`."), [])

    def test_unparseable_block_fails(self):
        self.assertEqual(len(self.block("df.groupby(")), 1)


if __name__ == "__main__":
    unittest.main()
