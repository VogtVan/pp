"""Scenario `ui-team-runs` -- a run of a team, known in the Agents tab (plan ui, batch le-membre-inspecte),
on the bench's witnesses:
- the overlay of the runs of `agents/reviewer` says `core-review/reviewer` on `a01389`, the run its
  member holds as `team status core-review --json` says it, and `—` on `a00007`; `veille`, never started,
  is not read
- `enter` on `a01389` opens the run in a read-only tab of the dialogue, replayed from its kept flow (batch
  le-suivi-des-taches) -- no `agent chat` launched
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-runs")

    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "160x40", "--press", "2,enter")
    rows = {key: next((line for line in done.stdout.split("\n") if key in line), "") for key in ("a01389", "a00007")}
    journal = house.journal_lines()
    if (done.returncode == 0 and "core-review/reviewer" in rows["a01389"] and "core-review" not in rows["a00007"]
            and "—" in rows["a00007"] and "status" in journal and "status core-review" in journal
            and "status veille" not in journal):
        held("the run of a member is marked", f"{rows['a01389'].strip()[:80]!r}; the other run —")
    else:
        failures.append(f"  ✗ marked                      rc={done.returncode} {rows} {journal} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "160x40", "--press", "2,enter,enter")
    chat = house.chat_lines()
    if (done.returncode == 0 and "core-review/reviewer" in done.stdout and "read only" in done.stdout
            and "LGTM" in done.stdout and "flow agents/reviewer a01389 --json" in chat
            and not any(one.startswith("open") for one in chat)):
        held("enter on a run of a team opens it read only", "the tab core-review/reviewer, its kept flow replayed "
             "(LGTM); no agent chat")
    else:
        failures.append(f"  ✗ opened read only            rc={done.returncode} {chat} {done.stdout[-1500:]!r}")
    return 0
