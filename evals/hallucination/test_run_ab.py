"""Tests for the invented-name A/B that make no API calls.

    python -m unittest evals.hallucination.test_run_ab
    python evals/hallucination/test_run_ab.py

They pin the metric (invented() flags a bogus or removed name and passes a real snippet), assert
every question's category is a real catalogue group, and assert every documented trap is genuinely
absent from the CURRENT catalogue -- so a name pandas later restores stops being a trap loudly.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_ab  # noqa: E402


class Metric(unittest.TestCase):
    def test_valid_snippet_has_no_inventions(self):
        text = "```python\ndf.groupby(\"region\")[\"sales\"].sum()\n```"
        self.assertEqual(run_ab.invented(text), [])

    def test_bogus_method_flagged(self):
        text = "```python\ndf.totally_made_up_method()\n```"
        self.assertTrue(run_ab.invented(text))

    def test_removed_api_flagged(self):
        # applymap was removed in pandas 3.x; a model that writes it must be caught.
        self.assertTrue(run_ab.invented("```python\ndf.applymap(f)\n```"))

    def test_bogus_pd_function_in_code_flagged(self):
        self.assertTrue(run_ab.invented("```python\npd.load_csv(\"f.csv\")\n```"))

    def test_prose_mention_not_counted(self):
        # Naming a removed API in prose to warn about it is not a hallucination.
        self.assertEqual(run_ab.invented("The old `Series.iteritems()` is gone; use `.items()`."),
                         [])


class Bank(unittest.TestCase):
    def setUp(self):
        self.questions = run_ab.load_questions()
        self.rows = run_ab.catalog_rows()

    def test_categories_are_real_groups(self):
        for q in self.questions:
            self.assertIn(q["category"], self.rows, f"{q['id']}: bad category")

    def test_regimes_known(self):
        for q in self.questions:
            self.assertIn(q["regime"], ("core", "deep"), q["id"])

    def test_traps_are_absent_from_catalog(self):
        # In CODE (which is what the metric scans): the inline checker deliberately tolerates a
        # REMOVED name so a trap note can mention it, but check_code flags it. A trap pandas later
        # restores to the catalogue would stop being flagged here, failing this loudly.
        for q in self.questions:
            for trap in q.get("traps", []):
                self.assertTrue(run_ab.invented(f"```python\n{trap}\n```"),
                                f"{q['id']}: trap {trap} is NOT flagged (shipped by pandas?)")


if __name__ == "__main__":
    unittest.main()
