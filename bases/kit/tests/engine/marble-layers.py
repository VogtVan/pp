"""Scenario `marble-layers` -- 1 case(s) (batch le-marbre-et-la-carte-au-noyau, 2026-09-26; the
half of `tests/engine/packaging/marble-layers.py` that reads the KIT's text, cut here at
le-tri-de-l-execution-et-du-packaging, 2026-10-06):
- no rule lost: every sentence of the marble and the card of 966643e (frozen under
  witness/) stands in the compiled marble of a kit-only instance -- verbatim, with
  `principal` for `operator`, or with `response` for the channel `chat` -- but the rules a
  later batch withdrew, each named with its batch and absent from the compiled marble
"""
from __future__ import annotations

import re
from pathlib import Path

WITNESS = Path(__file__).parent / "witness"
CHANNEL = (("=> chat", "=> response"),                      # the channel said to the principal
           ("), chat, tool", "), response (said to the principal), tool"),
           ("as ONE final chat message**", "as ONE `=> response`: your final chat message**"))
RETIRED = {   # a rule of 966643e a later batch withdrew on purpose -> the batch, its date, why
    "A key answering `run-unknown` — e.g. after an upgrade closed the open runs — also requires "
    "`-new`, never improvisation.":
        "la-cle-gardee-par-l-upgrade, 2026-10-04: an upgrade keeps the key, the run reopens",
    "Either path counts against the repair bound.":
        "la-sortie-du-fail, 2026-10-04: a fix whose mini-proof holds counts nothing",
    "You judge what you prove: the codes at risk, at least one, a code unnamed is n/a.":
        "les-codes-non-nommes-refuses, 2026-10-04: every code the line asks takes a verdict",
    "One JSON array, the codes at risk — one object each, the deepest first; a code unnamed is n/a:":
        "les-codes-non-nommes-refuses, 2026-10-04: every code the line asks takes a verdict",
    "A parenthesis is never a closure: the run and its key survive; resume with `-peek`, then "
    "the owed call, as the card's **“Parenthesis”** says.":
        "les-canaux-du-tour, 2026-10-06: the parenthesis is the standing orders' own section now",
}
SWAPS = (("operator's", "principal's"), ("operator-", "principal-"), ("Operator", "Principal"),
         ("operator", "principal")) + CHANNEL


def sentences(text: str) -> list[str]:
    """-> the fragments a rule is made of: every line cut on its sentence ends."""
    found = []
    for line in text.splitlines():
        for piece in re.split(r"(?<=[.!?;])\s+(?=[A-Z*`(\[])", line.strip()):
            if len(piece) >= 20:
                found.append(piece)
    return found


def swapped(piece: str, swaps: tuple = SWAPS) -> str:
    for old, new in swaps:
        piece = piece.replace(old, new)
    return piece


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    compiled = (bench.env("layers").made / ".sys" / "system.md").read_text(encoding="utf-8")

    # --- no rule lost --------------------------------------------------------------------
    old_marble = (WITNESS / "MARBLE-966643e.md").read_text(encoding="utf-8").split("\n---\n", 1)[1]
    old_card = (WITNESS / "PP-966643e.md").read_text(encoding="utf-8").split("\n---\n", 1)[1]
    pieces = sentences(old_marble) + sentences(old_card)
    lost = [one for one in pieces if one not in compiled and swapped(one) not in compiled
            and swapped(one, CHANNEL) not in compiled and one not in RETIRED]
    standing = [one for one in RETIRED if one in compiled or one not in pieces]
    if pieces and not lost and not standing:
        held("no rule of 966643e is lost", f"{len(pieces)} sentences of the old marble and card, "
             "each found in the compiled marble verbatim, with `principal` for `operator`, "
             f"or with `response` for the channel `chat`; {len(RETIRED)} withdrawn by name, "
             "and absent")
    else:
        failures.append(f"  ✗ lost sentences              {len(lost)} of {len(pieces)}: {lost[:3]!r} "
                        f"retired yet standing or unknown: {standing!r}")
    return 0
