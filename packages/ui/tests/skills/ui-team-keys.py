"""Scenario `ui-team-keys` -- `l` and `v` (plan ui, batches le-fil-de-la-tache and les-deux-onglets), on the
bench's `pp-team` witness:
- `l` on the Teams tab shows the whole journal of the team (`team log <name> --json`) in an overlay
- `v` on the Tasks tab shows the result of the task under the cursor (`team result <name> <task>`);
  on an open task, `task-open` goes to the remedy line as the verb said it
- outside the Teams and Tasks tabs `l` and `v` play nothing; `t` stays the themes
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-keys")

    done = house.render("--render", "teams", "--size", "120x34", "--press", "l")
    flat = _flat(done.stdout)
    if (done.returncode == 0 and "journal" in flat and "#1 " in done.stdout and "team-started" in flat
            and "#47 " in done.stdout and "log core-review" in house.journal_lines()):
        held("l shows the whole journal", "team log core-review --json in an overlay, #1 to #47")
    else:
        failures.append(f"  ✗ journal                     rc={done.returncode} {house.journal_lines()} "
                        f"{done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    done = house.render("--render", "tasks", "--size", "120x34", "--press", "shift+tab,shift+tab,down,tab,tab,up,v")
    flat = _flat(done.stdout)
    if done.returncode == 0 and '"verdict": "LGTM"' in flat and "result core-review T2" in house.journal_lines():
        held("v shows a resolved task's result", "team result core-review T2, the JSON indented")
    else:
        failures.append(f"  ✗ result                      rc={done.returncode} {done.stdout[-1200:]!r}")

    done = house.render("--render", "tasks", "--size", "120x34", "--press", "v")
    remedy = done.stdout.rstrip("\n").split("\n")[-2] if done.stdout else ""
    if done.returncode == 0 and "task-open -- T3 is open" in remedy:
        held("v on an open task: the refusal on the remedy line", remedy.strip())
    else:
        failures.append(f"  ✗ result refused              rc={done.returncode} {remedy!r} {done.stdout[-600:]!r}")

    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "120x34", "--press", "l,v")
    played = house.journal_lines()
    themes = house.render("--render", "teams", "--size", "120x34", "--press", "t")
    if (done.returncode == 0 and played == [] and themes.returncode == 0
            and "textual-dark" in themes.stdout and "keeps" in themes.stdout):
        held("l and v act on the tabs of the teams alone; t stays the themes",
             "no call of team from the dialogue; t lists the themes")
    else:
        failures.append(f"  ✗ keys elsewhere              {played} {themes.stdout[-600:]!r}")
    return 0
