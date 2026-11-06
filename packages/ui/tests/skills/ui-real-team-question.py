"""Scenario `ui-real-team-question` -- a member's question to the owner, from the post, on the REAL verbs of `team`,
its wake-ups played by the team witness, never a provider; `dev`, delegated T1 by `lead`, asks the owner:
- on the Tasks tab, `enter` on T1 opens its thread: the question stands there `[open]`
- `b` opens the owner's inbox read from the real `team inbox --json`: the question's row names its id, its sender and
  its task; `x` writes one `inbox-seen` at the journal, and the question still waits there
- `m`, the question chosen in `reply to`, a text: the real `team post --reply` -- the journal's `post` is a `re` of the
  owner citing the question, the question leaves `waiting`, T1 done; no witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
P = support(__file__, "dialogue")      # the readers of a capture
T = support(__file__, "teams")
SIZE = ("--size", "200x50")
REPLY = "m,o,k,shift+tab,space,down,enter,tab,enter"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team, ask, owner, begun = R.asking(bench, "ui-real-team-question")
    mark = f"#{ask.get('id')}"

    # --- enter on T1: the question open in its thread -------------------------------------------------------------
    shown = team.render("--render", "tasks", *SIZE, "--press", "enter")
    line = next((one for one in shown.stdout.split("\n") if f"{mark} " in one and "→" in one), "")
    if begun and ask and ask.get("to") == owner and ask.get("task") == "T1" and "[open]" in line:
        held("a question to the owner is open in the thread", f"{mark} ask from dev to {owner} [open]")
    else:
        failures.append(f"  ✗ question open               begun={begun} ask={ask} owner={owner!r} {line!r} "
                        f"{shown.stdout[-1500:]!r}")

    # --- b, x: the real inbox, marked seen --------------------------------------------------------------------------
    face = team.face("team", "inbox", R.TEAM, "--json")
    question = next((one for one in face.get("questions") or [] if one.get("id") == ask.get("id")), {})
    seen = team.render("--render", "teams", *SIZE, "--press", "b,x,b")
    rows = [one for one in P.overlay_rows(seen.stdout) if T.in_order(one, mark, "dev", "T1")]
    marks = team.kinds("inbox-seen")
    if (seen.returncode == 0 and question.get("from") == "dev" and question.get("task") == "T1" and len(rows) == 1
            and len(marks) == 1):
        held("b reads the real inbox, x marks it seen", f"{mark} from dev on T1 as team inbox --json says it; "
             f"inbox-seen #{marks[0].get('id')}, the question still waiting")
    else:
        failures.append(f"  ✗ inbox                       rc={seen.returncode} question={question} rows={rows} "
                        f"marks={marks} {seen.stdout[-1500:]!r} {seen.stderr[-300:]!r}")

    # --- m: the reply, the team to its end --------------------------------------------------------------------------
    done = team.render("--render", "tasks", *SIZE, "--press", REPLY, "--wait", "team:done:40")
    replies = [one for one in team.kinds("post", verb="re") if one.get("from") == owner]
    finished = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))
    waiting = (team.state().get("waiting") or {}).get("questions")
    if (done.returncode == 0 and len(replies) == 1 and replies[0].get("re") == ask.get("id")
            and replies[0].get("text") == "ok" and finished and waiting == []):
        held("m replies to the question", f"post #{replies[0].get('id')} re {mark} from {owner}; done T1; "
             "waiting.questions []")
    else:
        failures.append(f"  ✗ reply                       rc={done.returncode} replies={replies} finished={finished} "
                        f"waiting={waiting} {done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
