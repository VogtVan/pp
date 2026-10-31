"""Scenario `ui-agents-reading` -- how the AGENTS tab reads its faces (plan ui, batch la-borne-et-le-demarrage), on the
bench's `pp-chat` witness replaying the faces of `agent`:
- a face its verb did not finish within the bound (`PP_UI_TIMEOUT`) is said on the remedy line, `verb-timeout`, and the
  agent's line shows no runs: its first object alone is never taken for the face
- the statuses of the agents are read together, four at most at once: eight witnesses of one second each, their start
  and end kept by the witness
- the footer holds its columns: the zones of the status, the activity and the clock stand at the same place at rest
  and while a face is read, at 120 and at 80 columns (batch les-zones-fixes)
"""
from __future__ import annotations

import json
import re

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-agents-reading")
    render = post.render

    # --- the bound: a face its verb did not finish is said, never shown as whole --------------------------
    post.use({**P.SCRIPT, "faces": {**P.FACES, "hang": {"status": 5}}})
    post.env["PP_UI_TIMEOUT"] = "1"
    cut = render("--render", "agents", "--size", "120x30")
    del post.env["PP_UI_TIMEOUT"]
    row = next((line for line in cut.stdout.split("\n") if re.search(r"^\s*ag1\s", line)), "")
    cell = re.search(r"^\s*ag1\s+(\S+)", row)
    runs_cell = cell.group(1) if cell else ""
    if cut.returncode == 0 and "verb-timeout" in P.remedy_of(cut.stdout) and runs_cell == P.palette_constant("NONE"):
        held("a face past the bound is said", f"the remedy says verb-timeout; ag1's runs `{runs_cell}`, its first "
             "object alone never counted as its runs")
    else:
        failures.append(f"  ✗ bound                       rc={cut.returncode} row={row!r} remedy={P.remedy_of(cut.stdout)!r} "
                        f"{cut.stderr[-300:]!r}")

    # --- the statuses read together, four at most ----------------------------------------------------------
    extra = [f"ag{n}" for n in range(3, 9)]
    statuses = {**P.FACES["status"], **{name: [dict(one, agent=name) for one in P.FACES["status"]["ag2"]]
                                         for name in extra}}
    listed = P.FACES["list"] + [{**P.FACES["list"][1], "agent": name} for name in extra]
    post.use({**P.SCRIPT, "faces": {**P.FACES, "list": listed, "status": statuses, "slow": {"status": 1.0}}})
    times = post.journal.with_name(post.journal.name + ".times.jsonl")
    times.unlink(missing_ok=True)
    together = render("--render", "agents", "--size", "120x40")
    calls = [json.loads(one) for one in times.read_text(encoding="utf-8").splitlines()] if times.is_file() else []
    marks = sorted([(one["start"], 1) for one in calls] + [(one["end"], -1) for one in calls])
    peak, now = 0, 0
    for _, step in marks:
        now += step
        peak = max(peak, now)
    if together.returncode == 0 and len(calls) >= 8 and 2 <= peak <= 4 and all(name in together.stdout for name in extra):
        held("the statuses are read together", f"8 statuses of 1 s each, {peak} at most at once; every agent in the table")
    else:
        failures.append(f"  ✗ together                    rc={together.returncode} calls={len(calls)} peak={peak} "
                        f"{together.stderr[-300:]!r}")

    # --- the footer holds its columns while a face is read, at two widths -----------------------------------
    post.use({**P.SCRIPT, "faces": {**P.FACES, "slow": {"status": 2.0}}})
    foot = ("status", "activity", "clock")
    for size in ("120x30", "80x24"):
        rest = render("--render", "agents", "--size", size, "--regions")
        busy = render("--render", "agents", "--size", size, "--regions", "--press", "u,spinning")
        at_rest = {zone: P.zones_of(rest.stdout).get(zone) for zone in foot}
        busy_zones = {zone: P.zones_of(busy.stdout).get(zone) for zone in foot}
        spun = re.search(r"^spinning (\d+)$", busy.stdout, re.M)
        if (rest.returncode == 0 and busy.returncode == 0 and all(at_rest.values()) and at_rest == busy_zones
                and spun and spun.group(1) == "1"):
            held(f"the footer holds its columns ({size})", f"{at_rest} at rest and while a face is read")
        else:
            failures.append(f"  ✗ footer zones ({size})        {at_rest} / {busy_zones} spun={spun and spun.group(1)} "
                            f"{busy.stderr[-300:]!r}")
    return 0
