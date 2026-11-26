"""What a rule refuses, said: the refusal `rules` raises is received where the rule is called."""
from __future__ import annotations

from model.refusal import Refusal
from store.refusal import refuse


def ruled(rule, *given):
    """-> what a judgment of `rules` gives of `given`; what it refuses is said on stderr, the exit with it."""
    try:
        return rule(*given)
    except Refusal as refusal:
        refuse(str(refusal))
