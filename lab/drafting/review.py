"""Second pass: an independent Claude call reviews each passing draft against its excerpt.

    python lab/drafting/review.py                # every passing draft not yet reviewed
    python lab/drafting/review.py --only groupby

The scripted checks in draft.py prove that names exist, quotes are verbatim and the example runs.
They cannot prove that a trap's advice follows from its evidence. This pass asks for exactly that,
with clean context, and records the verdict in lab/drafting/out/<batch>.review.json. A card with
problems is redrafted once with the review as the failure list, and re-verified.
"""

from __future__ import annotations

import argparse
import json
import sys

import draft

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict", "problems"],
    "properties": {
        "verdict": {"type": "string", "enum": ["ok", "fix"]},
        "problems": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["where", "problem"],
                "properties": {"where": {"type": "string"}, "problem": {"type": "string"}},
            },
        },
    },
}

PROMPT = """You review one trap card of pandas-for-agents before it is published for AI agents.
You did not write it. The card is checked by script already: every pandas name exists in the
catalogue, every evidence quote is verbatim, and the example runs on pandas {new} with warnings as
errors. Your job is what a script cannot check:

- Does each trap's advice ("instead") follow from its evidence and the excerpt? Flag advice that
  names a replacement the excerpt does not support, or that states a behaviour the excerpt does not
  show.
- Is any trap wrong about what was removed vs deprecated, or about the version?
- Does the summary claim anything the excerpt does not back?
- Does the example's explanation match what the code does?

Return verdict "ok" with no problems if the card is sound. Only report real problems, each with
where it is (trap number, summary or example) and what is wrong. Do not report style.

Card:
{card}

Catalogue excerpt (pandas {old} -> {new}):
{excerpt}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--only", nargs="*", choices=sorted(draft.BATCHES))
    parser.add_argument("--budget", type=float, default=35.0)
    args = parser.parse_args()
    old, new, changes = draft.catalogue_pair()
    versions = (old["pandas_version"], new["pandas_version"])
    for batch in args.only or list(draft.BATCHES):
        result_file = draft.OUT / f"{batch}.json"
        review_file = draft.OUT / f"{batch}.review.json"
        if not result_file.exists() or not draft.load(result_file)["passed"]:
            print(f"skip {batch}: no passing draft")
            continue
        if review_file.exists() and not args.only:
            print(f"skip {batch}: already reviewed")
            continue
        if draft.spent() >= args.budget:
            print(f"stop: US${draft.spent()} spent, budget US${args.budget}")
            return 1
        result = draft.load(result_file)
        card = result["attempts"][-1]["card"]
        ex = draft.excerpt(batch, old, new, changes)
        ex_text = json.dumps(ex, indent=1, ensure_ascii=False)
        prompt = PROMPT.format(card=json.dumps(card, indent=1, ensure_ascii=False), excerpt=ex_text,
                               old=versions[0], new=versions[1])
        draft.SCHEMA, saved = SCHEMA, draft.SCHEMA
        try:
            review = draft.call(prompt, batch, None)
        finally:
            draft.SCHEMA = saved
        record = {"batch": batch, "review": review}
        if review["verdict"] == "fix" and review["problems"]:
            failures = [f"review, {p['where']}: {p['problem']}" for p in review["problems"]]
            base = draft.RULES.format(old=versions[0], new=versions[1], title=draft.BATCHES[batch][0], excerpt=ex_text)
            fixed = draft.call(base + draft.REPAIR.format(previous=json.dumps(card, indent=1, ensure_ascii=False),
                                                          failures="\n".join(f"- {f}" for f in failures)), batch, None)
            md = draft.render(batch, fixed, versions)
            quotes = ex_text + "\n" + "\n".join(draft.leaves(ex))
            checks = draft.verify(batch, fixed, md, quotes, versions[1])
            record["fixed"] = {"card": fixed, "failures": checks}
            if not checks:
                result["attempts"].append({"card": fixed, "failures": [], "from_review": True})
                result_file.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                       newline="\n")
                (draft.OUT / f"{batch}.md").write_text(md, encoding="utf-8", newline="\n")
        review_file.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                               newline="\n")
        state = review["verdict"]
        if "fixed" in record:
            state += ", fixed" if not record["fixed"]["failures"] else ", fix failed checks (kept previous)"
        print(f"{batch}: {state} ({len(review['problems'])} problem(s)); spent US${draft.spent()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
