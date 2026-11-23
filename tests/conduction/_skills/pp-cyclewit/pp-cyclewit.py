"""The witness of the iterated door: `next` says what remains due; as a sink, it marks done.
Played as a GESTURE by the console (`-s pp-cyclewit next`), `main(argv)` is its entry; launched as a
provider or a sink, the module's own call is."""
import os
import sys
from pathlib import Path

ITEMS = ("alpha", "beta", "gamma")
HOME = Path(os.environ.get("PP_HOME") or Path(__file__).resolve().parents[2])
DONE = HOME / "cyclewit.done"


def done() -> set:
    return set(DONE.read_text(encoding="utf-8").split()) if DONE.is_file() else set()


def due():
    for one in ITEMS:
        if one not in done():
            return one
    return None


def main(argv: list[str]) -> int:
    if argv == ["next"]:
        element = due()
        if element:
            print(element)
        return 0
    production = sys.stdin.read()
    element = due()
    if element and element in production:
        with DONE.open("a", encoding="utf-8") as out:
            out.write(element + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
