"""What a layer with effects says when it refuses: the line on stderr, the exit."""
from __future__ import annotations

import sys
from typing import NoReturn


def refuse(said: str) -> NoReturn:
    sys.stderr.write(f"pp-agent: {said}\n")
    raise SystemExit(2)
