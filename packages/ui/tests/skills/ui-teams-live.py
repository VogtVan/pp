"""Scenario `ui-teams-live` -- the Teams tab follows the chosen team (plan ui, batch le-volet-des-equipes),
on the bench's `pp-team` witness whose `watch --json` writes a post, then a quiet:
- ONE watch on the chosen team; a post makes `status <team> --json` read again -- its last event on the status
  line --, a quiet reads nothing
- choosing another team ends the watch of the first and opens one on the second
- the post's end ends the watch WHOLE: `watch-end` in the journal, no process of the witness left
- the column `live` of Members (batch les-taches-vivantes): a member running with no step seen says `since`, a step
  of `reviewer` on the watch puts its stack in its line, a member at rest says `—`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

POST = {"event": "post", "id": 48, "task": "T4", "from": "pm", "to": "lead", "verb": "do", "text": "a new task"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script(watch={"core-review": [{"sleep": 0.5}, POST, {"sleep": 0.5},
                                             {"event": "quiet", "seconds": 1}]})
    script["states"]["core-review"] = [T.CORE, T.CORE_NEXT]
    house = T.Teams(bench, "ui-teams-live", script)

    # --- a post reads the team again, a quiet does not ------------------------------------------------
    done = house.render("--render", "teams", "--size", "140x34", "--press", "wait:team:post,wait:team:quiet")
    journal = house.journal_lines()
    reads = [one for one in journal if one == "status core-review"]
    status = done.stdout.rstrip("\n").split("\n")[-1]
    if (done.returncode == 0 and "last #48" in status and len(reads) == 2
            and journal.count("watch core-review") == 1 and journal.count("status") == 1
            and journal[-1] == "watch-end core-review" and not house.alive()):
        held("a post reads the team again, a quiet does not", f"last #48 on the status; the journal {journal}; "
             "no witness left")
    else:
        failures.append(f"  ✗ live                        rc={done.returncode} {status!r} {journal} "
                        f"alive={house.alive()} {done.stdout[-900:]!r} {done.stderr[-400:]!r}")

    # --- another team chosen: the first watch ended, one on the second -----------------------------------
    house.clear_journal()
    house.use(T.script())
    done = house.render("--render", "teams", "--size", "120x34", "--press", "down")
    journal = [one for one in house.journal_lines() if one.startswith("watch")]
    if (done.returncode == 0 and journal == ["watch core-review", "watch-end core-review", "watch ops",
                                              "watch-end ops"] and not house.alive()):
        held("one watch, on the team chosen", f"{journal}; no witness left")
    else:
        failures.append(f"  ✗ watch switched              rc={done.returncode} {journal} alive={house.alive()} "
                        f"{done.stderr[-400:]!r}")

    # --- the column live: since, then the last step; a member at rest ----------------------------------------
    house.use(T.script(watch={"core-review": [{"sleep": 0.6}, T.STEP]}))
    before = house.render("--render", "teams", "--size", "150x34")
    after = house.render("--render", "teams", "--size", "150x34", "--press", "wait:team:block")

    def row(done, member: str) -> str:
        return next((one for one in done.stdout.split("\n") if f" {member} " in one and f"agents/{member}" in one), "")
    if (before.returncode == 0 and after.returncode == 0 and "live" in before.stdout
            and "since" in row(before, "reviewer") and "TURN{4/4}" in row(after, "reviewer")
            and "TURN" not in row(after, "lead") and "since" not in row(after, "lead")):
        held("the column live of Members", f"{row(before, 'reviewer').strip()[-30:]!r} -> "
             f"{row(after, 'reviewer').strip()[-30:]!r}; lead {row(after, 'lead').strip()[-10:]!r}")
    else:
        failures.append(f"  ✗ column live                 rc={before.returncode},{after.returncode} "
                        f"{row(before, 'reviewer')!r} {row(after, 'reviewer')!r} {row(after, 'lead')!r} "
                        f"{after.stdout[-1500:]!r}")
    return 0
