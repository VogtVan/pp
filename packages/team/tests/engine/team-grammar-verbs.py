"""Scenario `team-grammar-verbs` -- what the verbs of a season, of the house and of the readers refuse before they
act, on one house, no wake-up and no tick: `pair` is in season on one task, `idle` and three more are declared and never
started, `nobody` is declared nowhere.
- (a) a call a verb cannot read is refused with the usage -- `tick`, `follow`, `snapshot`, two flags of a `start`
  without their value, `stop`, `resume`, `budget`, `verify`, `guard`, `mount`, `delete`, the `--sleep` and the
  `--due` of `timer`: exit 2, nothing written
- (b) a start the house cannot open is refused by its code, each on a team of its own: a member nobody declared
  `participant-unknown`, a budget in launches under 1 `budget-invalid`, a silence under 1 for the team and for one
  member `team-invalid`
- (c) a team or a task a verb does not know: `stop`, `budget`, `watch`, `resume` and `resume --recurrence` of a
  team nobody declared `team-unknown`; `resume`, `pause --recurrence`, `resume --recurrence` and `inbox --seen` of a
  team never started `team-not-started`; a task the team does not hold `task-unknown`
- (d) a value a verb cannot read: dollars that are no number and launches not above the launched `budget-invalid`;
  a bound of `watch` that is no number of seconds `for-invalid`; an inbox message named by a word
  `inbox-id-unknown`; `inbox --seen` without a team, in the verb's own words; a vector of another family at
  `verify` and at `guard` `family-foreign`
- (e) a task stopped twice is `task-closed`; off season, a task is not resumed: `season-stopped`
- (f) `delete` without `--yes` says what it would remove and that nothing is written: the team stays
"""
from __future__ import annotations

import re

from tests.harness import cli, support

T = support(__file__, "team")

IDLE = ("idle", "idle-b", "idle-c", "idle-d")        # declared, never started: one per start refused
CODE = re.compile(r"[a-z]+(-[a-z]+)+")      # what a refusal's code looks like: `team-unknown`
TIMER = ("--due", "2026-10-01T09:00:00", "--token", "t")
# (a) the calls no verb can read
UNREAD = [("tick", "pair", "more"), ("follow", "pair"), ("snapshot", "pair", "more"),
          ("start", "idle", "--message", "x", "--no-tick", "--package"),
          ("start", "idle", "--message", "x", "--no-tick", "--member"),
          ("stop", "pair", "--recurrence", "R1", "--task", "T1", "--no-tick"),
          ("resume", "pair", "--message", "x", "--no-tick"), ("budget", "pair"), ("verify", "more"),
          ("guard", "more"), ("mount",), ("delete", "pair", "--agent"),
          ("timer", "pair", "--sleep", "soon", *TIMER), ("timer", "pair", "--sleep", "0", "--due", "soon", "--token", "t")]
# (b) the starts the house cannot open, with the code each is refused by
UNOPENED = {("start", "idle", "--message", "x", "--to", "nobody", "--no-tick"): "participant-unknown",
            ("start", "idle-b", "--message", "x", "--budget-launches", "0", "--no-tick"): "budget-invalid",
            ("start", "idle-c", "--message", "x", "--silence", "0", "--no-tick"): "team-invalid",
            ("start", "idle-d", "--message", "x", "--no-tick", "--member", "gm", "--silence", "0"): "team-invalid"}
# (c) the teams and the tasks a verb does not know
UNKNOWN = {("stop", "nobody"): "team-unknown", ("budget", "nobody", "5"): "team-unknown",
           ("watch", "nobody", "--for", "1"): "team-unknown", ("resume", "nobody"): "team-unknown",
           ("resume", "nobody", "--recurrence", "R1"): "team-unknown",
           ("resume", "idle"): "team-not-started", ("pause", "idle", "--recurrence", "R1"): "team-not-started",
           ("resume", "idle", "--recurrence", "R1"): "team-not-started", ("inbox", "idle", "--seen"): "team-not-started",
           ("stop", "pair", "--task", "T9", "--no-tick"): "task-unknown"}
# (d) the values a verb cannot read
UNVALUED = {("budget", "pair", "plenty"): "budget-invalid", ("budget", "pair", "--launches", "0"): "budget-invalid",
            ("watch", "pair", "--for", "soon"): "for-invalid",
            ("inbox", "pair", "--seen", "--id", "that"): "inbox-id-unknown"}


def coded(played) -> str:
    """-> the code a refusal opens on; the exit code of a call that did not refuse."""
    return T.refusal_code(played.stderr) if played.returncode == 2 else f"rc {played.returncode}"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    usage = f"pp-team: {h.module().USAGE}"
    h.declare("pair", T.PAIR.format(m="gm", w="gw"))
    for name in IDLE:
        h.declare(name, T.PAIR.format(m="gm", w="gw"))
    started = h.call("team", "start", "pair", "--message", "do it", *h.harnessed, "--no-tick")
    standing = h.events("pair")

    def refused(calls) -> dict:
        """-> what each call was refused by: `usage`, its code, or the exit code of one that went through."""
        found = {}
        for call in calls:
            played = h.call("team", *call)
            found[call] = "usage" if played.returncode == 2 and played.stderr.strip() == usage else coded(played)
        return found

    def strays(found: dict, owed) -> dict:
        return {" ".join(call): said for call, said in found.items()
                if said != (owed[call] if isinstance(owed, dict) else owed)}

    # --- (a) a call a verb cannot read ----------------------------------------------------------------------------
    unread = strays(refused(UNREAD), "usage")
    if started.returncode == 0 and len(standing) == 3 and not unread and h.events("pair") == standing:
        bench.refusals += len(UNREAD)
        held("(a) a call a verb cannot read is refused with the usage", f"{len(UNREAD)} calls over 11 verbs: exit 2, "
             "the usage, the journal of pair as it was")
    else:
        failures.append(f"  ✗ (a) the usage               start={started.returncode} {started.stderr.strip()[-120:]!r} "
                        f"strays={unread} events={len(h.events('pair'))}/{len(standing)}")

    # --- (b) a start the house cannot open ------------------------------------------------------------------------
    unopened = strays(refused(UNOPENED), UNOPENED)
    born = [name for name in IDLE if h.journal_of(name).exists()]
    if not unopened and h.events("pair") == standing and not born:
        bench.refusals += len(UNOPENED)
        held("(b) a start the house cannot open is refused by its code", f"{sorted(set(UNOPENED.values()))}: no "
             "journal for the four teams asked, the journal of pair as it was")
    else:
        failures.append(f"  ✗ (b) the starts              strays={unopened} started={born}")

    # --- (c) a team or a task a verb does not know ----------------------------------------------------------------
    unknown = strays(refused(UNKNOWN), UNKNOWN)
    if not unknown and h.events("pair") == standing and not h.journal_of("idle").exists():
        bench.refusals += len(UNKNOWN)
        held("(c) a team or a task a verb does not know", f"{len(UNKNOWN)} calls: team-unknown for nobody, "
             "team-not-started for idle, task-unknown for T9; nothing written")
    else:
        failures.append(f"  ✗ (c) the unknown             strays={unknown} idle={h.journal_of('idle').exists()}")

    # --- (d) a value a verb cannot read ---------------------------------------------------------------------------
    unvalued = strays(refused(UNVALUED), UNVALUED)
    bare = h.call("team", "inbox", "--seen")
    foreign = {verb: cli(h.engine, "--instance", str(h.house), "team", verb, cwd=h.ws, env=h.env, stdin="plan:x")
               for verb in ("verify", "guard")}
    if (not unvalued and bare.returncode == 2 and bare.stderr.strip() != usage and not CODE.fullmatch(coded(bare))
            and {verb: coded(one) for verb, one in foreign.items()} == {"verify": "family-foreign",
                                                                        "guard": "family-foreign"}
            and h.events("pair") == standing):
        bench.refusals += len(UNVALUED) + 3
        held("(d) a value a verb cannot read is refused", f"{sorted(set(UNVALUED.values()))}; inbox --seen without "
             "a team, in the verb's own words; a vector of another family at verify and at guard: family-foreign")
    else:
        failures.append(f"  ✗ (d) the values              strays={unvalued} bare={bare.returncode} {coded(bare)!r} "
                        f"foreign={ {verb: coded(one) for verb, one in foreign.items()} }")

    # --- (e) a task stopped twice; off season, a task is not resumed ----------------------------------------------
    once = h.call("team", "stop", "pair", "--task", "T1", "--no-tick")
    twice = h.call("team", "stop", "pair", "--task", "T1", "--no-tick")
    ended = h.call("team", "stop", "pair", "--no-tick")
    stop_id = next((one["id"] for one in reversed(h.events("pair")) if one.get("kind") == "season-stopped"), None)
    closed = h.events("pair")
    late = h.call("team", "resume", "pair", "--task", "T1", "--no-tick")
    if (once.returncode == 0 and coded(twice) == "task-closed" and ended.returncode == 0 and stop_id
            and coded(late) == "season-stopped" and h.events("pair") == closed):
        bench.refusals += 2
        held("(e) a task stopped twice, a task resumed off season", "stop --task T1 again: task-closed; the season "
             "stopped, resume --task T1: season-stopped, nothing written")
    else:
        failures.append(f"  ✗ (e) closed and off season   {once.returncode}/{coded(twice)}/{ended.returncode}/{coded(late)} "
                        f"stop={stop_id} moved={h.events('pair') != closed}")

    # --- (f) delete without --yes says what it would remove --------------------------------------------------------
    dry = h.call("team", "delete", "idle")
    if dry.returncode == 0 and len(dry.stdout.splitlines()) == 2 and (h.teams / "idle" / "TEAM.md").is_file():
        held("(f) delete without --yes writes nothing", "team delete idle: two lines -- what it would remove, and "
             "that nothing is written --, idle still declared")
    else:
        failures.append(f"  ✗ (f) delete, dry             rc={dry.returncode} {dry.stdout!r} {dry.stderr.strip()[-160:]!r}")
    return 0
