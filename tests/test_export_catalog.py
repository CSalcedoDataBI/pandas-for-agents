"""Tests for the deprecation parser of scripts/export_catalog.py. Run: python -m unittest

The parser is pure text, but the module imports pandas, so these tests are skipped without it.
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    import export_catalog
except ImportError:  # CI's plain-Python step has no pandas; the export step has it
    export_catalog = None

DOC = """Return unbiased skew within groups.

Parameters
----------
numeric_only : bool, default False
    Include only float, int, boolean columns.
method : str, default None
    How to fill.

    .. deprecated:: 2.1.0
        Use ffill instead.

**kwargs
    Additional keyword arguments.

.. deprecated:: 3.1.0
    Passing ``**kwargs`` to GroupBy.skew is deprecated.

Returns
-------
Series
"""


@unittest.skipIf(export_catalog is None, "pandas is not installed")
class Deprecations(unittest.TestCase):
    def test_targets(self):
        found = {d["version"]: d["target"] for d in export_catalog.deprecations(DOC)}
        self.assertEqual(found["2.1.0"], "parameter:method")
        self.assertEqual(found["3.1.0"], "parameter:kwargs")

    def test_column_zero_note_belongs_to_member(self):
        doc = "Summary.\n\nParameters\n----------\nx : int\n    A value.\n\n.. deprecated:: 3.0.0\n    Use y.\n"
        self.assertEqual(export_catalog.deprecations(doc)[0]["target"], "member")


if __name__ == "__main__":
    unittest.main()
