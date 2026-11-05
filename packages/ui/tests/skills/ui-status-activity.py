"""Scenario `ui-status-activity` -- the activity zone of the status row, on the bench's `pp-chat` witness:
- while a face is read (`u` on the Agents tab, the witness's statuses slow), the spinner turns and the status says
  what is read (`READING` of the palette; batch la-borne-et-le-demarrage)
- the footer says a reading, not a turn (batch la-saisie-et-le-tour): during `ag3`'s turn the spinner's interval is
  alive and the status row carries no glyph -- the turn is said in the message line's zone
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "120x30")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-status-activity")

    # --- a reading under way: the spinner turns and the status says what is read ---------------------------
    post.use({**P.SCRIPT, "faces": {**P.FACES, "slow": {"status": 2.0}}})
    loading = post.render("--render", "agents", "--size", "120x30", "--press", "u,spinning")
    spun = re.search(r"^spinning (\d+)$", loading.stdout, re.M)
    said = P.status_of("\n".join(line for line in loading.stdout.split("\n") if not line.startswith("spinning ")))
    try:
        reading = P.palette_constant("READING")
    except KeyError:
        reading = None
    if loading.returncode == 0 and spun and spun.group(1) == "1" and reading and reading in said:
        held("a reading under way is said", f"the spinner turns; the status: {said.strip()[:90]!r}")
    else:
        failures.append(f"  ✗ loading said                rc={loading.returncode} spun={spun and spun.group(1)} "
                        f"reading={reading!r} status={said!r} {loading.stderr[-300:]!r}")

    # --- the footer says a reading, not a turn ----------------------------------------------------------------
    post.use(P.SCRIPT)
    turning = post.render("ag3", "--render", "dialogue", *SIZE, "--press", "i,h,i,enter,wait:principal,spinning")
    spun = re.search(r"^spinning (\d+)$", turning.stdout, re.M)
    status = P.status_of("\n".join(line for line in turning.stdout.split("\n") if not line.startswith("spinning ")))
    glyphs = P.palette_constant("SPINNER")
    if turning.returncode == 0 and spun and spun.group(1) == "1" and not any(one in status for one in glyphs):
        held("the footer says a reading, not a turn", f"the spinner's interval alive; the status row: {status.strip()[-60:]!r}")
    else:
        failures.append(f"  ✗ no turn in the footer       rc={turning.returncode} spun={spun and spun.group(1)} "
                        f"status={status!r} {turning.stderr[-300:]!r}")
    return 0
