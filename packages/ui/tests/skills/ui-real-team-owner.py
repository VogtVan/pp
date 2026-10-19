"""Scenario `ui-real-team-owner` -- the owner's gestures on a team at the post, on the REAL verbs of `team`, its
wake-ups played by the team witness, never a provider: `essai` under `budget: 3`, started once, T1 done --
- `e` reads the real `team declaration --json`: verdict ok, no key pending; the overlay opens on its path
- `B` raises the budget to 5: `budget-raised` at the journal, `status --json` says the cap 5
- `P`, `enter` pauses: `paused` at the journal, the face `state: paused`, the menu marks `essai` paused, the head
  names the owner
- a task posted while paused wakes nobody; `P`, `enter` resumes: `unpaused`, T2 done, the team awake
- the owner edits `root: lead` into `root: dev`: `e` says the key `root` waiting a start, from `lead` to `dev`;
  no process of the witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
P = support(__file__, "dialogue")      # the readers of an overlay and of the palette's source
SIZE = ("--size", "200x50")
ERASE = ",".join(["backspace"] * 4)
PAUSED = P.palette_constant("PAUSED")
SCRIPT = {"lead": [{"body": {"done": "first"}}, {"body": {"done": "after the pause"}}]}


def _gap_row(rows: list[str]) -> str:
    """-> the overlay's row that holds the key `root` with its value at the start and the one declared."""
    return next((row for row in rows if {"root", "lead", "dev"} <= set(row.split())), "")


def _done(task: str):
    return lambda events: any(one.get("kind") == "done" and one.get("task") == task for one in events)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-owner", SCRIPT, R.BUDGETED)
    begun = team.start("first")
    started = team.settled(_done("T1"))
    owner = team.state().get("owner")

    # --- e: the declaration as started ---------------------------------------------------------------
    read = team.render("--render", "teams", *SIZE, "--press", "e")
    face = team.face("team", "declaration", R.TEAM, "--json")
    rows = P.overlay_rows(read.stdout)
    path = face.get("path") or ""
    if (begun.returncode == 0 and started and read.returncode == 0 and (face.get("verdict") or {}).get("ok") is True
            and face.get("pending") == [] and path and any(path in row for row in rows) and not _gap_row(rows)):
        held("e reads the real declaration", f"verdict ok, pending [] at the face; the overlay on {path}")
    else:
        failures.append(f"  ✗ declaration                 started={started} face={face} {read.stdout[-1500:]!r} "
                        f"{read.stderr[-300:]!r}")

    # --- B: the budget raised ------------------------------------------------------------------------
    raised = team.render("--render", "teams", *SIZE, "--press", f"B,{ERASE},5,enter")
    events = team.kinds("budget-raised")
    cap = (team.state().get("budget") or {}).get("cap")
    if raised.returncode == 0 and len(events) == 1 and events[0].get("budget") == 5 and cap == 5:
        held("B raises the budget on the real verb", f"budget-raised #{events[0].get('id')} budget 5; status --json cap {cap}")
    else:
        failures.append(f"  ✗ budget                      events={events} cap={cap} {raised.stdout[-1200:]!r} "
                        f"{raised.stderr[-300:]!r}")

    # --- P: the pause, seen at the post --------------------------------------------------------------
    paused = team.render("--render", "teams", *SIZE, "--press", "P,enter,wait:team:paused")
    state = team.state()
    menu = next((one for one in paused.stdout.split("\n") if f"{PAUSED} {R.TEAM}" in one), "")
    if (paused.returncode == 0 and team.kinds("paused", by=owner) and state.get("state") == "paused" and menu
            and f"by {owner}" in paused.stdout):
        held("P pauses the team, the post says it", f"paused by {owner} at the journal; state paused; {menu.strip()[:40]!r}")
    else:
        failures.append(f"  ✗ pause                       paused={team.kinds('paused')} state={state.get('state')} "
                        f"{paused.stdout[-1500:]!r} {paused.stderr[-300:]!r}")

    # --- a task posted while paused, then the resume -------------------------------------------------
    before = len(team.kinds("wake-intent"))
    team.call("team", "post", R.TEAM, "--message", "while paused")
    after = len(team.kinds("wake-intent"))
    resumed = team.render("--render", "teams", *SIZE, "--press", "P,enter")
    done = team.settled(_done("T2"))
    unpaused = team.kinds("unpaused")
    woken = team.kinds("wake-intent", task="T2")
    if (after == before and resumed.returncode == 0 and unpaused and woken and woken[0]["id"] > unpaused[0]["id"] and done
            and team.state().get("state") in ("idle", "working", "waiting")):
        held("nobody woken while paused, P resumes it", f"{after} wake-intent(s) across the post; unpaused "
             f"#{unpaused[0]['id']}, T2 woken #{woken[0]['id']} after it, done")
    else:
        failures.append(f"  ✗ resume                      intents={before}->{after} unpaused={unpaused} woken={woken} "
                        f"done={done} {resumed.stdout[-1500:]!r} {resumed.stderr[-300:]!r}")

    # --- the owner's edit: e says the key waiting a start --------------------------------------------
    team.edit("root: lead", "root: dev")
    gap = team.render("--render", "teams", *SIZE, "--press", "e")
    pending = team.face("team", "declaration", R.TEAM, "--json").get("pending")
    row = _gap_row(P.overlay_rows(gap.stdout))
    if gap.returncode == 0 and pending == [{"key": "root", "started": "lead", "declared": "dev"}] and row:
        held("e says the key the edit leaves pending", f"pending root lead -> dev at the face; {row!r}")
    else:
        failures.append(f"  ✗ pending                     pending={pending} {gap.stdout[-1500:]!r} {gap.stderr[-300:]!r}")
    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
