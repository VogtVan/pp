"""Scenario `ui-real-team-ring` -- a ceremony rung from the post on the REAL verbs of `team`, its wake-ups played by
the team witness, never a provider, the clock frozen before the daily's hour; `essai` started once, T1 done --
- `g` opens the ceremonies, `g` again on `daily`: the real `team ring` -- `ceremony-due` under `manual-<id>`, by the
  owner, one task to `lead`, closed once `dev` and `rev` answered: `lead`, launched by every message for it, says
  nothing at the ring's opening nor at `dev`'s answer and concludes at `rev`'s, which `rev` gives once the journal
  shows `lead`'s launch on `dev`'s answer ended
- `c` shows the ceremonies: the progress of `daily` is the face's, every participant answered; no process of the
  witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
SIZE = ("--size", "200x50")
def script(gate) -> dict:
    """-> the witness's script: `lead` answers T1, then on the daily's ring says nothing at its opening, nothing at
    `dev`'s answer, and concludes at `rev`'s; `rev` holds at `gate` before it answers."""
    return {"lead": {"T1": [{"body": {"done": "started"}}],
                     "T2": [{"body": []}, {"body": []}, {"body": {"done": "daily held"}}]},
            "dev": [{"body": {"done": "yesterday: tests"}}],
            "rev": [{"gate": str(gate), "body": {"done": "yesterday: reviews"}}]}


def _done(task):
    return lambda events: any(one.get("kind") == "done" and one.get("task") == task for one in events)


def _heard(facilitator: str, task, member: str):
    """-> the journal's predicate: the facilitator's launch that carried `member`'s answer on the task has ended."""
    def judged(events) -> bool:
        answer = next((one["id"] for one in events if one.get("kind") == "post" and one.get("verb") == "re"
                       and one.get("task") == task and one.get("from") == member), None)
        ended = {one.get("tag") for one in events if one.get("kind") == "wake-ended"}
        return answer is not None and any(
            one.get("kind") == "wake-intent" and one.get("agent") == facilitator and one.get("tag") in ended
            and answer in (one.get("messages") or []) for one in events)
    return judged


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gate = bench.temp() / "rev.gate"                     # rev's answer waits for it
    team = R.RealTeam(bench, "ui-real-team-ring", script(gate))
    begun = team.start("go")
    started = team.settled(_done("T1"))
    owner = team.state().get("owner")

    # --- g rings the daily ---------------------------------------------------------------------------
    rung = team.render("--render", "teams", *SIZE, "--press", "g,g")
    due = team.kinds("ceremony-due", ceremony="daily")
    period = str(due[0].get("period")) if due else ""
    task = next((one.get("task") for one in team.kinds("task") if one.get("ceremony") == "daily"), None)
    heard = team.settled(_heard("lead", task, "dev"), timeout=40.0)
    gate.write_text("open", encoding="utf-8")            # lead's launch on dev's answer is over: rev answers
    closed = team.settled(_done(task), timeout=40.0)
    if (begun.returncode == 0 and started and rung.returncode == 0 and len(due) == 1 and period == f"manual-{due[0]['id']}"
            and due[0].get("by") == owner and task and heard and closed):
        held("g rings the ceremony at hand", f"ceremony-due daily {period} by {owner}; task {task} to lead, closed")
    else:
        failures.append(f"  ✗ ring                        rc={begun.returncode},{rung.returncode} started={started} due={due} "
                        f"task={task} heard={heard} closed={closed} {rung.stdout[-1200:]!r} {rung.stderr[-300:]!r}")

    # --- c: the progress of the ring, from the face --------------------------------------------------
    shown = team.render("--render", "teams", *SIZE, "--press", "c")
    progress = next((one.get("progress") for one in team.state().get("ceremonies") or [] if one.get("name") == "daily"), None)
    count = f"{sum(1 for one in progress or [] if one.get('answered'))}/{len(progress or [])}"
    row = next((one for one in shown.stdout.split("\n") if "daily" in one.split() and count in one.split()), "")
    if shown.returncode == 0 and progress and count == "2/2" and row:
        held("the progress of the ring, from the real face", f"{row.strip()[:60]!r}; progress {progress}")
    else:
        failures.append(f"  ✗ progress                    rc={shown.returncode} {count} {progress} {shown.stdout[-1500:]!r}")
    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
