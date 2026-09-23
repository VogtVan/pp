"""Scenario `bench-streams` -- 3 case(s):
- les-deux-flux-au-meme-tampon: what a scenario writes rides one buffer, in its order
- l-echec-rend-ses-flux: a scenario that fails renders both its streams with its ✗
- l-imbrication-du-refus: expect_exit hands the case its text and the report the rest
"""
from __future__ import annotations

import contextlib
import io

from tests.harness import play, report

BOTH = """
import sys

def scenario(bench):
    print("out: first")
    print("err: second", file=sys.stderr)
    print("out: third")
    return 0
"""

FALLS = """
import sys

def scenario(bench):
    print("out: falling")
    print("err: falling", file=sys.stderr)
    return 1
"""

REFUSES = """
import sys

def scenario(bench):
    def refuse():
        print("bench-witness-refusal", file=sys.stderr)
        raise SystemExit(2)

    text = bench.expect_exit("bench-witness-refusal", refuse)
    print("out: the case read", "bench-witness-refusal" in text)
    return 0
"""


def _thrown(bench, name: str, text: str) -> str:
    """A scenario written at the run, under the bench's own throwaway directory: the
    witness reads what `play` renders of it and never writes on the streams of the
    process that carries it -- a test that printed to prove itself would judge itself."""
    path = bench.temp() / f"{name}.py"
    path.write_text(text, encoding="utf-8")
    return str(path)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- les-deux-flux-au-meme-tampon: one buffer, the order kept ---------------------
    both = play("witness/both", _thrown(bench, "both", BOTH))
    written = [line for line in both["out"].splitlines() if line[:4] in ("out:", "err:")]
    if written == ["out: first", "err: second", "out: third"]:
        held("both streams, one buffer", "a scenario prints on stdout, on stderr, then on "
             "stdout again: the three lines come back in its detail, in the order it wrote them")
    else:
        failures.append(f"  ✗ the two streams captured    {written!r}")

    # --- l-echec-rend-ses-flux: a ✗ carries everything the scenario wrote --------------
    fallen = play("witness/falls", _thrown(bench, "falls", FALLS))
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        verdict = report([fallen], 0.9)
    spoken = said.getvalue()
    if verdict == 1 and "out: falling" in spoken and "err: falling" in spoken:
        held("a failure renders both streams", "the report shows the lines of a scenario "
             "that failed without any flag -- whichever stream they were written on")
    else:
        failures.append(f"  ✗ the failure's detail        rc={verdict} "
                        f"{spoken.splitlines()[:4]!r}")

    # --- l-imbrication-du-refus: expect_exit under the capture -------------------------
    refused = play("witness/refuses", _thrown(bench, "refuses", REFUSES))
    detail = refused["out"]
    if (not refused["failures"] and refused["refusals"] == 1
            and "out: the case read True" in detail
            and detail.count("bench-witness-refusal") == 1):     # the ✓ line alone
        held("a refusal stays the case's own", "expect_exit swaps the stream under the "
             "capture: the case reads the refusal it expects, the report keeps the ✓ and "
             "the text is neither doubled nor lost")
    else:
        failures.append(f"  ✗ the refusal nested          {refused['failures']!r} "
                        f"{detail!r}")
    return 0
