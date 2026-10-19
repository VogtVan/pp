"""Scenario `patterns-dry` -- the campaign of the patterns (`tools/patterns/`) proven WITHOUT a harness.
- (a) `run-patterns.py plan` writes the 12 plans of launch (6 patterns x 2 channels) and
  launches nothing: every plan says `launched: false`, names its command, its door and its
  root of documents
- (b) the six roots of documents are judged by the engine: a throwaway instance opens on
  each one under `PP_DOCUMENTS` (and `PP_DOOR` where the pattern has a door), no refusal
- (c) each pattern's first block is the expected one: READ_LINES `WORK any => response`,
  LAPS `INFER field => tool (heredoc)`, CYCLE its element under `cyclewit-items`, ROUTE then
  `PICK next` with LEFT and RIGHT as OPTIONS, BEGIN before the WORK, REVIEW offered to the WORK
- (d) `report` refuses `report-not-yet`; `play` on a provider this machine lacks refuses
  `provider-missing` -- nothing launched either way
- (e) `prepare --pattern read-lines` builds ONE house on a throwaway path: its agent's cap set to
  the host's, 25000 (`agent add` raises it to 200000, the relayed channel's), its boot cut in chunks
  served by the agent's own bare calls, the kit's turn with `READ_LINES` offered to the WORK,
  `LINES.txt` laid; a second `prepare` says `standing`
- (f) `sheet` renders six sections, one per pattern, each naming its house, its message and the two gestures
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys

from tests.harness import SOURCE, cli

LAUNCHER = SOURCE / "tools" / "patterns" / "run-patterns.py"
DOCS = SOURCE / "tools" / "patterns" / "docs"
KEY = re.compile(r"run ([0-9a-f]{6})")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- (a) the plans, nothing launched --------------------------------------------------------------
    out = bench.temp() / "dry"
    planned = subprocess.run([sys.executable, str(LAUNCHER), "plan", "--out", str(out)],
                             capture_output=True, text=True, cwd=str(SOURCE))
    files = sorted(out.glob("*.json")) if out.is_dir() else []
    plans = [json.loads(one.read_text(encoding="utf-8")) for one in files]
    if (planned.returncode == 0 and len(plans) == 12
            and all(one.get("launched") is False and one.get("command") and one.get("documents") for one in plans)
            and {one["channel"] for one in plans} == {"bare", "relayed"}
            and sum(1 for one in plans if one["channel"] == "bare" and one["stdin"] and "conduct off" in one["stdin"]) == 6
            and all("--door" in one["command"] for one in plans
                    if one["channel"] == "relayed" and one["door"])):
        held("(a) the plans are written, nothing launched", f"{len(plans)} plans under dry/, 6 bare under "
             "`conduct off`, 6 relayed by `agent run`, every one `launched: false`")
    else:
        failures.append(f"  ✗ (a) the plans               rc={planned.returncode} n={len(plans)} "
                        f"{planned.stderr[-200:]!r}")

    # --- (b) + (c) the six roots, judged and opened -------------------------------------------------------
    env = bench.env("patterns-roots")
    shutil.copytree(SOURCE / "tools" / "patterns" / "skills" / "pp-cyclewit",
                    env.made / "skills" / "pp-cyclewit", dirs_exist_ok=True)
    (env.root / "LINES.txt").write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")

    def opened(pattern: str, door: str | None):
        extra = {"PP_DOCUMENTS": str(DOCS / pattern), **({"PP_DOOR": door} if door else {})}
        return cli(env.engine, "-new", cwd=env.root, env=extra)

    read = opened("read-lines", "READ_LINES.md")
    laps = opened("laps", "LAPS.md")
    cycle = opened("cycle", "CYCLE.md")
    route = opened("route", "ROUTE.md")
    route_key = KEY.search(route.stdout).group(1) if KEY.search(route.stdout) else ""
    picked = cli(env.engine, route_key, cwd=env.root) if route_key else None
    begin = opened("begin", None)
    review = opened("review", None)
    all_opened = [read, laps, cycle, route, begin, review]
    if all(one.returncode == 0 and "REFUSED" not in one.stderr for one in all_opened):
        held("(b) the six roots are judged", "six `-new` under PP_DOCUMENTS, no refusal, each root composed")
    else:
        failures.append(f"  ✗ (b) the roots               rc={[one.returncode for one in all_opened]} "
                        f"{[one.stderr[-120:] for one in all_opened if one.returncode]!r}")
    checks = {
        "read-lines": "▸ READ_LINES" in read.stdout and "WORK any => response" in read.stdout,
        "laps": "▸ LAPS" in laps.stdout and "INFER field => tool (heredoc)" in laps.stdout,
        "cycle": "▸ CYCLE" in cycle.stdout and "cyclewit-items" in cycle.stdout and "alpha" in cycle.stdout,
        "route": "▸ STAGE" in route.stdout and picked is not None and "PICK next" in picked.stdout
                 and "LEFT" in picked.stdout and "RIGHT" in picked.stdout,
        "begin": "▸ BEGIN" in begin.stdout and begin.stdout.find("▸ BEGIN") < max(begin.stdout.find("WORK"), 10 ** 9),
        "review": "WORK" in review.stdout and "REVIEW" in review.stdout,
    }
    if all(checks.values()):
        held("(c) each pattern opens on its block", "READ_LINES a WORK => response, LAPS its field, CYCLE "
             "its first element, ROUTE a PICK next between LEFT and RIGHT, BEGIN before the WORK, REVIEW offered")
    else:
        failures.append(f"  ✗ (c) the first blocks        {checks} {cycle.stdout[-300:]!r} "
                        f"{(picked.stdout if picked else '')[-300:]!r}")

    # --- (d) the refusals ----------------------------------------------------------------------------------
    report = subprocess.run([sys.executable, str(LAUNCHER), "report", "2026-10-15"], capture_output=True, text=True)
    missing = subprocess.run([sys.executable, str(LAUNCHER), "play", "--provider", "nobody-has-this-binary"],
                             capture_output=True, text=True)
    if (report.returncode == 2 and "report-not-yet" in report.stderr
            and missing.returncode == 2 and "provider-missing" in missing.stderr):
        held("(d) the refusals", "`report` says report-not-yet, `play` on a missing provider says "
             "provider-missing -- exit 2, nothing launched")
    else:
        failures.append(f"  ✗ (d) the refusals            {report.returncode} {report.stderr[-120:]!r} "
                        f"{missing.returncode} {missing.stderr[-120:]!r}")

    # --- (e) the operator's bench: one house prepared -------------------------------------------------------
    houses = bench.temp() / "houses"
    built = subprocess.run([sys.executable, str(LAUNCHER), "prepare", "--pattern", "read-lines", "--out", str(houses)],
                           capture_output=True, text=True, cwd=str(SOURCE))
    again = subprocess.run([sys.executable, str(LAUNCHER), "prepare", "--pattern", "read-lines", "--out", str(houses)],
                           capture_output=True, text=True, cwd=str(SOURCE))
    house = houses / "read-lines"
    agent = house / "agents" / "pat"
    engine = house / ".pp" / ".sys" / "engine" / "pp.py"
    opened_turn = cli(engine, "--instance", str(agent / ".pp"), "-new", cwd=agent) if agent.is_dir() else None
    # the bare channel's boot is cut at the host's cap: the agent's own bare calls serve the chunks, the
    # turn's block comes with the last
    whole = opened_turn.stdout if opened_turn is not None else ""
    key = KEY.search(whole).group(1) if KEY.search(whole) else ""
    chunks = 1
    while key and "a reading continues" in whole.rsplit("▶ ", 1)[-1] and chunks < 8:
        whole += cli(engine, "--instance", str(agent / ".pp"), key, cwd=agent).stdout
        chunks += 1
    capped = "max_harness_tool_output: 25000" in (agent / ".pp" / "SETTINGS.md").read_text(encoding="utf-8") \
        if (agent / ".pp" / "SETTINGS.md").is_file() else False
    if (built.returncode == 0 and "built" in built.stdout and again.returncode == 0 and "standing" in again.stdout
            and (agent / "LINES.txt").is_file() and (agent / ".pp" / "procs" / "READ_LINES.md").is_file()
            and (houses / "SHEET.md").is_file() and opened_turn is not None and opened_turn.returncode == 0
            and capped and chunks >= 2 and "READ_LINES" in whole and "WORK" in whole):
        held("(e) one house of the operator's bench", "prepared under a throwaway path, standing at the second "
             f"call; the agent's cap at 25000, its boot cut in {chunks} chunks served by its own bare calls, "
             "the turn with READ_LINES offered, LINES.txt laid, the sheet written")
    else:
        failures.append(f"  ✗ (e) the house               rc={built.returncode}/{again.returncode} capped={capped} "
                        f"chunks={chunks} {built.stdout[-160:]!r} {built.stderr[-200:]!r} "
                        f"opened={opened_turn and opened_turn.returncode} {whole[-200:]!r}")

    # --- (f) the sheet ----------------------------------------------------------------------------------------
    said = subprocess.run([sys.executable, str(LAUNCHER), "sheet", "--out", str(houses)], capture_output=True, text=True)
    sections = [line for line in said.stdout.splitlines() if line.startswith("## ")]
    if (said.returncode == 0 and len(sections) == 6 and said.stdout.count("- VS Code:") == 6
            and said.stdout.count("- post:") == 6 and said.stdout.count("- message:") == 6):
        held("(f) the sheet", "six sections, each with its house, its message, the VS Code and the post gestures")
    else:
        failures.append(f"  ✗ (f) the sheet               rc={said.returncode} sections={len(sections)}")
    return 0
