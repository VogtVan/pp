"""Scenario `ui-task-members` -- one `live:` line per member in the band of a task (plan ui, batch les-taches-vivantes),
on the bench's witnesses: `core-review`'s watch says a step of `lead` on T3 (its exchange 4), one of `reviewer` (its
exchange 3), then the end of `lead`'s wake-up; `agent flow` replays each one's kept flow:
- the band of T3 says two `live:` lines, each its run, its step and its call read from ITS exchange -- one `flow`
  reading per member in the journal of `agent`
- the end of `lead`'s wake-up dims its line alone (`--styles`)
- a member the face says `running` with no step seen: `live: sre · run b11111 · launched …` on ops' T1
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

SIZE = ("--size", "160x40")


def _line(text: str, mark: str) -> str:
    return next((one for one in text.split("\n") if mark in one), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script(watch={"core-review": T.TWO_WATCH})
    script["states"]["ops"] = [T.LIVE_OPS]
    house = T.Teams(bench, "ui-task-members", script)

    # --- two members, two lines, two readings ---------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended")
    lead, reviewer = _line(done.stdout, "live: lead"), _line(done.stdout, "live: reviewer")
    flows = [one for one in house.chat_lines() if one.startswith("flow ")]
    of_lead = [one for one in flows if "agents/lead a77f10" in one and "--exchange 4" in one]
    of_reviewer = [one for one in flows if "agents/reviewer a01389" in one and "--exchange 3" in one]
    if (done.returncode == 0 and "run a77f10" in lead and "TURN{3/4}" in lead and "Read" in lead
            and "run a01389" in reviewer and "TURN{4/4}" in reviewer and "WebSearch" in reviewer
            and len(of_lead) == 1 and len(of_reviewer) == 1 and "before:" not in done.stdout):
        held("one live line per member, its call from its exchange", f"{lead.strip()[:60]!r}; "
             f"{reviewer.strip()[:60]!r}; {flows}")
    else:
        failures.append(f"  ✗ two members                 rc={done.returncode} {lead!r} {reviewer!r} {flows} "
                        f"{done.stdout[-2000:]!r} {done.stderr[-400:]!r}")

    # --- the end of lead's wake-up dims its line alone ---------------------------------------------------
    styled = house.render("--render", "tasks", *SIZE, "--wait", "team:wake-ended", "--styles")
    lead, reviewer = _line(styled.stdout, "lead · run"), _line(styled.stdout, "reviewer · run")
    bold = "\x1b[1;"                       # the label `live:` of a wake-up under way, bold; dim once it ended
    if styled.returncode == 0 and lead and reviewer and bold not in lead and bold in reviewer:
        held("the end of a wake-up dims its member's line alone", "lead's line without its bold label, reviewer's with")
    else:
        failures.append(f"  ✗ dimmed                      rc={styled.returncode} {lead!r} {reviewer!r}")

    # --- a wake-up with no step seen yet ---------------------------------------------------------------------
    rest = house.render("--render", "tasks", *SIZE, "--press", "down")
    sre = _line(rest.stdout, "live: sre")
    if rest.returncode == 0 and "run b11111" in sre and "launched" in sre:
        held("a wake-up with no step seen says it was launched", sre.strip()[:60])
    else:
        failures.append(f"  ✗ launched                    rc={rest.returncode} {sre!r} {rest.stdout[-1500:]!r}")
    return 0
