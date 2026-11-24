"""Scenario `team-grammar` -- what `pp team` refuses before it acts, on one house, no wake-up and no tick:
- a declaration `team start` cannot read is refused `team-invalid`, no agent born, no journal written: an edge
  without its arrow, an edge to two members, two principals on one line, a ceremony declared twice, a ceremony
  that follows one nobody declared, an entry without its arrow, an entry to two documents, a trigger declared
  twice, a ceremony after two, a ceremony with two facilitators, a bound of the suspicion that is no duration;
  a ceremony that names a member nobody declared is refused `participant-unknown`
- a member the house cannot give birth to (a file stands on its path): `agent-add-failed`, no journal written;
  the team's `status` says it declared, not started
- a post the verb cannot read: `--name` and `--vector` on a standing task are refused with the usage, a post
  without its text `message-missing`, a reply to a message the task does not hold -- by a number or by a word --
  `message-unknown`; nothing written
- the readings: `log --last` under 1 or no number `last-invalid`; `result` before any task is resolved
  `result-missing`; `responses` of a team nobody declared `team-unknown`, its `--last` and `--since` that are no
  whole number `last-invalid` and `since-invalid`; a clock that is no date-time (`PP_NOW`) `now-invalid`
- an act whose form is broken is refused by `act_formed`, read by a probe: an element that is no object, two forms
  in one element, a vector that is none, an `ask` and an `info` out of their form, a `re` that cites a word
- `reset` when the agent's console keeps the run (a call holds it): `reset-failed`, no `run-reset` written
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

from conductor.state import lock
from tests.harness import holding, support

T = support(__file__, "team")

ENTRIES = "---\nReview the pull request"          # where a declaration's `entries:` block goes: the end of its front
# the declarations `team start` cannot read, each one fault away from the review team's
UNREAD = {
    "an edge without its arrow": T.REVIEW.replace("r1 r2 r3 -> m", "r1 r2 r3 m"),
    "an edge to two members": T.REVIEW.replace("r1 r2 r3 -> m", "r1 r2 -> m r3"),
    "two principals on a line": T.REVIEW.replace("  pm\n", "  pm po\n"),
    "a ceremony declared twice": T.REVIEW.replace("  retro after daily with r1 r2 -> m",
                                                  "  daily every weekday 10:30 with r1 -> m"),
    "a ceremony after nobody's": T.REVIEW.replace("retro after daily", "retro after weekly"),
    "an entry without its arrow": T.REVIEW.replace(ENTRIES, "entries: |\n  do ACTS.md\n" + ENTRIES),
    "an entry to two documents": T.REVIEW.replace(ENTRIES, "entries: |\n  do -> A.md B.md\n" + ENTRIES),
    "a trigger declared twice": T.REVIEW.replace(ENTRIES, "entries: |\n  do -> A.md\n  do -> B.md\n" + ENTRIES),
    # the line of a ceremony and the bound of the suspicion
    "a ceremony after two": T.REVIEW.replace("retro after daily", "retro after daily weekly"),
    "a ceremony with two facilitators": T.REVIEW.replace("with r1 r2 r3 -> m", "with r1 r2 -> m r3"),
    "a suspicion bound that is no duration": T.REVIEW.replace("root: m\n", "root: m\nsuspect-max: soon\n")}
# one more, refused by another code: a ceremony names a member nobody declared
UNKNOWN = T.REVIEW.replace("with r1 r2 r3 -> m", "with r1 r9 -> m")


# the acts `act_formed` judges: the forms broken, and three it reads
ACTS = {"an element that is no object": ["a text alone"],
        "two forms in one element": [{"do": ["m"], "ask": "which?"}],
        "a do with a vector that is none": [{"do": {"m": {"text": "sort", "vector": "novector"}}}],
        "an ask that is a list": [{"ask": ["which?"]}],
        "an info with a key of its own": [{"info": {"to": "m", "note": "x"}}],
        "a re that cites a word": [{"re": "that", "text": "done"}],
        "formed: an ask said as a text": [{"ask": "which?"}],
        "formed: an info said as a text": [{"info": "noted"}],
        "formed: a do with its vector": [{"do": {"m": {"text": "sort", "vector": "plan:x"}}}]}


def coded(played) -> str:
    """-> the code a refusal opens on; the exit code of a call that did not refuse."""
    return T.refusal_code(played.stderr) if played.returncode == 2 else f"rc {played.returncode}"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    usage = f"pp-team: {h.module().USAGE}"
    journals = h.records / "teams"

    # --- a declaration team start cannot read ------------------------------------------------------------------
    for at, text in enumerate(UNREAD.values(), 1):
        h.declare(f"unread-{at}", text)
    unread = {what: h.call("team", "start", f"unread-{at}", "--message", "x", "--no-tick")
              for at, what in enumerate(UNREAD, 1)}
    codes = {what: coded(one) for what, one in unread.items()}
    h.declare("unread-member", UNKNOWN)
    unknown = h.call("team", "start", "unread-member", "--message", "x", "--no-tick")
    if (set(codes.values()) == {"team-invalid"} and not any(one.stdout for one in unread.values())
            and coded(unknown) == "participant-unknown"
            and not any(h.agent_stands(one) for one in ("m", "r1", "r2", "r3")) and not journals.exists()):
        bench.refusals += len(UNREAD) + 1
        held("a declaration team start cannot read is refused", f"{', '.join(UNREAD)}: team-invalid each; a ceremony "
             "that names a member nobody declared: participant-unknown; no agent born, no journal written")
    else:
        failures.append(f"  ✗ declarations                "
                        f"{ {what: said for what, said in codes.items() if said != 'team-invalid'} } "
                        f"member={coded(unknown)} journals={journals.exists()}")

    # --- a member the house cannot give birth to -----------------------------------------------------------------
    (h.ws / "taken").write_text("a file, where a directory is wanted\n", encoding="utf-8")
    h.declare("unborn", "---\nagents: |\n  um taken/um\nroot: um\nschedule: off\n---\nOne member, on a path a file holds.\n")
    unborn = h.call("team", "start", "unborn", "--message", "x", "--no-tick")
    declared = h.call("team", "status", "unborn")
    if (coded(unborn) == "agent-add-failed" and (h.ws / "taken").is_file() and not h.journal_of("unborn").exists()
            and declared.returncode == 0 and len(declared.stdout.splitlines()) == 1):
        bench.refusals += 1
        held("a member that cannot be born refuses the start", "taken/um, a file on its path: agent-add-failed, "
             "no journal written; its status says one line, the team declared and not started")
    else:
        failures.append(f"  ✗ agent-add-failed            {coded(unborn)} {unborn.stderr.strip()[-200:]!r} "
                        f"journal={h.journal_of('unborn').exists()} status={declared.returncode} {declared.stdout!r}")

    # --- a post the verb cannot read ------------------------------------------------------------------------------
    h.declare("pair", T.PAIR.format(m="gm", w="gw"))
    started = h.call("team", "start", "pair", "--message", "do it", "--no-tick")
    before = h.events("pair")
    posts = {"--name on a task": h.call("team", "post", "pair", "--task", "T1", "--name", "n", "--message", "x", "--no-tick"),
             "--vector on a task": h.call("team", "post", "pair", "--task", "T1", "--vector", "plan:x", "--message", "x",
                                          "--no-tick"),
             "no text": h.call("team", "post", "pair", "--no-tick"),
             "a reply to #99": h.call("team", "post", "pair", "--task", "T1", "--reply", "99", "--message", "x", "--no-tick"),
             "a reply to a word": h.call("team", "post", "pair", "--task", "T1", "--reply", "that", "--message", "x",
                                         "--no-tick")}
    said = {what: (one.stderr.strip() == usage and "usage") or coded(one) for what, one in posts.items()}
    if (started.returncode == 0 and len(before) == 3
            and said == {"--name on a task": "usage", "--vector on a task": "usage", "no text": "message-missing",
                         "a reply to #99": "message-unknown", "a reply to a word": "message-unknown"}
            and all(one.returncode == 2 for one in posts.values()) and h.events("pair") == before):
        bench.refusals += len(posts)
        held("a post the verb cannot read is refused", f"{said}; the journal at its {len(before)} events")
    else:
        failures.append(f"  ✗ posts refused               start={started.returncode} {started.stderr.strip()[-120:]!r} "
                        f"{said} events={len(h.events('pair'))}/{len(before)}")

    # --- the readings ---------------------------------------------------------------------------------------------
    readings = {"log --last 0": h.call("team", "log", "pair", "--last", "0"),
                "log --last many": h.call("team", "log", "pair", "--last", "many"),
                "result": h.call("team", "result", "pair"),
                "responses of nobody's team": h.call("team", "responses", "nobody"),
                "responses --last many": h.call("team", "responses", "pair", "--last", "many"),
                "responses --since -1": h.call("team", "responses", "pair", "--since", "-1"),
                "a clock that is no date-time": h.call("team", "tick", "pair", now="soon")}
    read = {what: coded(one) for what, one in readings.items()}
    if (read == {"log --last 0": "last-invalid", "log --last many": "last-invalid", "result": "result-missing",
                 "responses of nobody's team": "team-unknown", "responses --last many": "last-invalid",
                 "responses --since -1": "since-invalid", "a clock that is no date-time": "now-invalid"}
            and not any(one.stdout for one in readings.values()) and h.events("pair") == before):
        bench.refusals += len(readings)
        held("the readings refuse what they cannot read", f"{read}; nothing written")
    else:
        failures.append(f"  ✗ readings refused            {read} "
                        f"{ {what: one.stderr.strip()[-90:] for what, one in readings.items()} }")

    # --- reset when the agent's console keeps the run ----------------------------------------------------------------
    opening = {key: value for key, value in before[0].items() if key not in ("at", "id", "team")}
    h.declare("kept", T.PAIR.format(m="gm", w="gw"))        # the same two agents, a journal written by hand
    h.written("kept", [opening,
                       {"kind": "task", "task": "T1", "from": "house", "to": "gm", "text": "do it"},
                       {"kind": "post", "task": "T1", "from": "house", "to": "gm", "verb": "do", "text": "do it"},
                       {"kind": "wake-intent", "tag": "k1", "agent": "gm", "path": "agents/gm", "task": "T1",
                        "index": 1, "messages": [3]},
                       {"kind": "wake-launched", "tag": "k1", "agent": "gm", "run": "abc123", "pid": 1, "launch": 1},
                       {"kind": "wake-ended", "tag": "k1", "agent": "gm", "run": "abc123", "state": "parked",
                        "cost": 0.01}], T.THURSDAY + "09:00:00")
    kept = h.events("kept")
    own = h.meta_of("agents/gm") / "SETTINGS.md"           # the agent's own wait for a call on one of its runs
    standing = own.read_text(encoding="utf-8")
    own.write_text(re.sub(r"^call_lock_wait: \d+$", "call_lock_wait: 1", standing, count=1, flags=re.M),
                   encoding="utf-8")
    with holding(lock.call_of(h.meta_of("agents/gm"), "abc123")):     # a call holds the run at the agent
        reset = h.call("team", "reset", "kept", "--member", "gm")
    own.write_text(standing, encoding="utf-8")
    if coded(reset) == "reset-failed" and "abc123" in reset.stderr and h.events("kept") == kept:
        bench.refusals += 1
        held("reset refuses when the agent keeps the run", "run abc123 of gm, its call lock held by the bench: "
             "the agent's console refuses after call_lock_wait (1 s), reset-failed, no run-reset written")
    else:
        failures.append(f"  ✗ reset-failed                {coded(reset)} {reset.stdout[-120:]!r} "
                        f"{reset.stderr.strip()[-200:]!r} events={len(h.events('kept'))}/{len(kept)}")

    # --- an act whose form is broken ------------------------------------------------------------------------------------
    probe = T.probe_script(h, "said = {}\nfor what, act in json.loads(sys.argv[1]).items():\n    try:\n"
                              "        mod.act_formed(act)\n        said[what] = 'formed'\n"
                              "    except mod.Refused:\n        said[what] = 'refused'\nprint(json.dumps(said))\n")
    formed = subprocess.run([sys.executable, str(probe), json.dumps(ACTS)], capture_output=True, text=True)
    try:
        acts = json.loads(formed.stdout)
    except ValueError:
        acts = {}
    if acts == {what: "formed" if what.startswith("formed") else "refused" for what in ACTS}:
        held("an act whose form is broken is refused", f"{', '.join(what for what in ACTS if not what.startswith('formed'))}: "
             "refused each; an ask and an info said as a text, a do with its vector: formed")
    else:
        failures.append(f"  ✗ the form of an act          {acts} {formed.stderr.strip()[-200:]!r}")
    return 0
