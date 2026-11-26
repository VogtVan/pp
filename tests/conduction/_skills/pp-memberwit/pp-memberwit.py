"""The witness of a document rewritten under the run: `grow` gives the member a reading, as the member
craft writes it -- its `# SERVE` step uncommented and a `serve:` row. Played as a GESTURE by the console
(`-s pp-memberwit grow`), `main(argv)` is its entry."""
import os
import sys
from pathlib import Path

HOME = Path(os.environ.get("PP_HOME") or Path(__file__).resolve().parents[2])
MEMBER = HOME / "MEMBER.md"
OFF, ON = "  # SERVE\n", "  SERVE\n"
ROW = "serve: |\n  reference: LINES.txt\n"


def main(argv: list[str]) -> int:
    if argv != ["grow"]:
        print("usage: grow")
        return 2
    text = MEMBER.read_text(encoding="utf-8")
    if OFF in text:
        MEMBER.write_text(text.replace(OFF, ON, 1).replace("proc: |\n", ROW + "proc: |\n", 1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
