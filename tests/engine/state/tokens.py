"""Scenario `tokens` -- 2 case(s):
- the estimate holds against the reference encoding: four synthetic texts of one nature
  each, their o200k counts recorded, the exact counts and the tolerance measured
- the estimator is a pure function of the standard library: empty, a word, a run of
  spaces, an accented word against an ascii one, a punctuation run
"""
from __future__ import annotations

import json

from conductor.state import metrics

# documentary: the four texts are GENERATED here, byte for byte the ones measured on
# 2026-08-28 with tiktoken (o200k_base) outside the engine -- no phrase of any kept
# document, no fixture file to keep in step
FR = ("La rivière longe le village avant de rejoindre la plaine ; les jardins descendent jusqu'à l'eau, "
      "et chaque maison garde une barque amarrée sous les saules. Le matin, la brume efface les collines, "
      "puis le soleil rend aux toits leur couleur d'ardoise. ")
EN = ("The archive keeps one folder per year, and every folder holds the letters in the order they arrived; "
      "a reader who wants the reply must find the next folder, because the copies were never filed with "
      "their originals. ")
CODE = ("def merge(left: list[int], right: list[int]) -> list[int]:\n    out: list[int] = []\n    i = j = 0\n"
        "    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            out.append(left[i]); i += 1\n"
        "        else:\n            out.append(right[j]); j += 1\n    return out + left[i:] + right[j:]\n\n")
ROWS = "\n".join(f"| item-{n} | {n*137:,} | {'yes' if n % 3 else 'no'} | {n * 0.75:.2f} |" for n in range(1, 25))
TABLE = "| name | count | kept | ratio |\n|---|---:|:---:|---:|\n" + ROWS + "\n"
OBJECTS = [{"id": f"r{n:03d}", "label": f"row {n}", "score": round(n / 7, 3), "tags": ["alpha", "beta"][: n % 3]}
           for n in range(40)]
TEXTS = {
    "prose_fr": FR * 12,
    "prose_en": EN * 14,
    "code_and_table": CODE * 6 + TABLE,
    "json_objects": json.dumps(OBJECTS, ensure_ascii=False, indent=1),
}
# the reference counts (tiktoken o200k_base, 2026-08-28) and the estimator's exact ones
TRUTH = {"prose_fr": 745, "prose_en": 589, "code_and_table": 956, "json_objects": 1530}
EXACT = {"prose_fr": 697, "prose_en": 603, "code_and_table": 1002, "json_objects": 1450}
TOLERANCE = 0.10      # the measured drift of one nature alone stays under 7 %; 10 % is the bound


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the estimate against the reference --------------------------------------------
    counted = {name: metrics.tokens(text) for name, text in TEXTS.items()}
    within = {name: abs(counted[name] - TRUTH[name]) / TRUTH[name] for name in TEXTS}
    if counted == EXACT and all(drift <= TOLERANCE for drift in within.values()):
        held("the estimate holds against o200k", ", ".join(
            f"{name} {counted[name]}/{TRUTH[name]} ({within[name] * 100:+.1f} %)".replace("+", "")
            for name in TEXTS))
    else:
        failures.append(f"  ✗ tokens estimate            {counted} vs exact {EXACT}, truth {TRUTH}")

    # --- a pure function of the standard library ------------------------------------------
    if (metrics.tokens("") == 0 and metrics.tokens("hello") == 1 and metrics.tokens("   ") == 1
            and metrics.tokens("épaisseurs") > metrics.tokens("thickness")
            and metrics.tokens("réveillées") > metrics.tokens("awakened")
            and metrics.tokens("::::") == 2 and metrics.tokens("a b") == 2
            and metrics.tokens("12345") == 2):
        held("the estimator's rules", "empty 0, a word 1, spaces 1, an accented word splits "
             "sooner, punctuation by pairs, digits by threes")
    else:
        failures.append("  ✗ tokens rules               " + str([metrics.tokens(s) for s in
                        ("", "hello", "   ", "épaisseurs", "thickness", "réveillées", "awakened",
                         "::::", "a b", "12345")]))
    return 0
