"""Behaviour: weighing what the tool serves, so a policy is tuned on numbers.

A run is a session -- the floor frame never pops -- so what accumulates here is
what the whole session cost, part by part. The weigh mirrors the RENDER: a coded
constraint weighs its code (the text was said once, earlier), a fused segment
weighs at its OWN block (the assembled output subtracts what it re-prints) -- a
part is never counted twice, and `frame` (the scaffolding) never goes negative
on a fused run. Beside the characters, every block carries an ESTIMATE of its tokens:
a pure function of the standard library, calibrated once against a reference
encoding -- no dependency, no network, the number said approximate where it renders.
"""
from __future__ import annotations

import math
import re

from ..core.model import Block

PARTS = ("constraints", "payload", "options", "instruction", "frame")

# documentary: the estimator's pre-tokenizer -- the shape of a BPE tokenizer's first cut,
# in the standard library's `re` alone: a word with its leading space (and an English
# contraction), a number of one to three digits, a run of punctuation, a run of line
# breaks, the spaces before a word, any other whitespace
PIECE = re.compile(r" ?[^\W\d_]+(?:'(?:s|t|re|ve|m|ll|d))?| ?\d{1,3}| ?[^\w\s]+[\r\n]*"
                   r"|\s*[\r\n]+|\s+(?!\S)|\s+")
WORD_ASCII = 7        # characters of an ascii word per extra token beyond the first
WORD_ACCENTED = 4     # an accented word splits sooner: a letter is several bytes there
PUNCTUATION = 2       # characters of a punctuation run per token


def tokens(text: str) -> int:
    """-> an ESTIMATE of the tokens `text` costs a model -- a pure function of the
    standard library, no dependency and no network, calibrated once against the o200k
    encoding on rendered blocks (2026-08-28: 1.7 % median error, 4.5 % at p90, 9.1 % at
    worst over 21 blocks of about six thousand characters; a text of one nature alone
    drifts up to 6-7 % -- French prose under, code over). The number is said approximate
    wherever it renders (`tokens ≈`); the characters beside it are exact."""
    count = 0
    for piece in PIECE.finditer(text):
        core = piece.group(0).strip()
        if not core:                                 # a whitespace run: one token
            count += 1
        elif core[0].isalpha() or core[0] == "'":
            # a word: one token, then one more per WORD characters -- an accented word
            # (several bytes a letter) earns them sooner
            step = WORD_ASCII if core.isascii() else WORD_ACCENTED
            count += 1 + (len(core) - 1) // step
        elif core.isdigit():                         # up to three digits: one token
            count += 1
        else:                                        # punctuation: pairs of characters merge
            count += math.ceil(len(core) / PUNCTUATION)
    return count


def weigh(block: Block, text: str) -> dict[str, int]:
    """-> the block's characters, part by part, `text` being the block as rendered (the
    caller renders: a datum weighs what it is handed). `frame` is what is left: the
    scaffolding."""
    if not block.constraints or block.merged:
        constraints = 0            # a merged segment re-prints no CONSTRAINTS section
    else:
        said = [one for one in block.constraints if one.code not in block.coded]
        held = [one for one in block.constraints if one.code in block.coded]
        constraints = (sum(len(str(one)) + 1 for one in said)
                       + (sum(len(one.code) + 1 for one in held) + 2 if held else 0))
    measured = {
        "constraints": constraints,
        "payload": sum(len(text_) for _, text_ in block.payloads),
        "options": sum(len(one) + 1 for one in block.options),
        "instruction": len(block.command) + len(block.output),
    }
    total = len(text) - sum(len(one) + 1 for one in block.stacked)
    # the tokens weigh what this block newly prints, like `total`: a re-printed segment
    # was estimated at its own block
    estimated = max(0, tokens(text) - sum(tokens(one) for one in block.stacked))
    return {**measured, "frame": total - sum(measured.values()), "blocks": 1, "total": total,
            "tokens": estimated}


def accumulate(totals: dict[str, int], weighed: dict[str, int]) -> dict[str, int]:
    """-> `totals` grown by one weighed block -- the run's `served`, part by part."""
    return {key: totals.get(key, 0) + value for key, value in weighed.items()}


def add(totals: dict[str, int], block: Block, text: str) -> dict[str, int]:
    return accumulate(totals, weigh(block, text))
