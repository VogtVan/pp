"""_common -- what every migration of a house shares: the FRAME that orders its steps, and its pieces.

A migration lives in `migrations/<from>--<to>/`; its `migrate.py` puts `migrations/` at the head of
`sys.path` (computed from its own `__file__`), imports this package, declares its gestures and its
cleanup, and hands them to `run`. Nothing else: the frame alone checks, backs up, upgrades, holds the
house, plays the gestures, counts, removes and repairs.

    from _common import Refused, run
    GESTURES = [("records", moved)]            # (name, gesture(house, engine) -> count rows)
    def cleanup(house): return [...]           # what the arriving version no longer reads
    sys.exit(run(sys.argv[1:], FROM, TO, GESTURES, cleanup))
"""
import sys

sys.dont_write_bytecode = True      # importing the house's engine writes nothing in the house

from .refusal import MIGRATED, REFUSED, UNEQUAL, Refused   # noqa: E402
from .house import House, read                              # noqa: E402
from .engine import mounted, store_of                       # noqa: E402
from .frame import run                                      # noqa: E402

__all__ = ["MIGRATED", "REFUSED", "UNEQUAL", "Refused", "House", "read", "mounted", "store_of", "run"]
