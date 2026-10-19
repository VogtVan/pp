"""Scenario `team-season-profiles` -- 4 case(s): a season gives a member its PROFILE -- its model, effort and package
switches over the team's flags --, replayed at each of its wake-ups in its run, and is judged whole before any write;
TEAM.md stays without provider or package. Three teams stand in one house pinning `agent`, `team`, `steering` and
`plan`, each under its own names; each case waits for its team, then reads its journal, its face and its records.
- (a) a member's profile: `--member b --model m2 --effort high --package plan=off` -- b's messages carry
  `{model: m2, effort: high}`, its run plays `plan` off, a keeps the team's launch; `members[].launch` says it;
  TEAM.md the same to the byte
- (b) what each member's run plays: `members[].packages` of `status --json` and the agents of `declaration --json`
  say b `plan` off and a `plan` on, as each run plays them; both members, born by the start as members, say
  `steering` off
- (c) a refused profile leaves nothing: `package-required` (agent off), `package-invalid`, `package-unpinned`, each
  by its code -- no journal, no agent born
- (d) a member that holds a task is kept: TEAM.md drops y while y holds an open task -- `member-held`, the journal
  to the byte
"""
from __future__ import annotations

import hashlib
import json
import re

from conductor import persistence
from tests.harness import support

T = support(__file__, "team")

REFUSAL = re.compile(r"^pp-team: ([a-z][a-z-]*)", re.M)


def code(played) -> str:
    """-> the code of the refusal a call wrote on stderr, '' when none."""
    found = REFUSAL.search(played.stderr or "")
    return found.group(1) if found else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={
        # (a)(b) a delegates to b, which plays its profile
        "a": [{"sleep": 0.1, "body": {"do": ["b"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "b": [{"sleep": 0.1, "body": {"done": True}}],
        # (d) x delegates to y, which asks the house and so holds its task
        "x": [{"sleep": 0.1, "body": {"do": ["y"]}}],
        "y": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which?"}}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def policies(path: str) -> list[dict]:
        return [one.get("policy") or {} for one in T.lines(h.records / "messages.jsonl") if one.get("to") == path]

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("prof", "---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n"
                      "---\nTwo profiles.\n")
    h.declare("none", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    h.declare("hold", "---\nagents: |\n  x agents/x\n  y agents/y\nreports: |\n  y -> x\nroot: x\nschedule: off\n"
                      "---\nHold it.\n")
    doc = h.teams / "prof" / "TEAM.md"
    sha = hashlib.sha256(doc.read_bytes()).hexdigest()
    started = h.call("team", "start", "prof", "--message", "review PR 15", *h.harnessed,
                     "--member", "b", "--model", "m2", "--effort", "high", "--package", "plan=off")
    holding = h.call("team", "start", "hold", "--message", "ask around", *h.harnessed)
    tries = {"package-required": ("--member", "n", "--package", "agent=off"),
             "package-invalid": ("--member", "n", "--package", "plan=maybe"),
             "package-unpinned": ("--member", "n", "--package", "nowhere=off")}
    said = {wanted: h.call("team", "start", "none", "--message", "x", *h.harnessed, "--no-tick", *extra)
            for wanted, extra in tries.items()}

    # --- (a) a member's profile ------------------------------------------------------------------------------
    done = h.settled("prof", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("prof")
    run_b = next((one.get("run") for one in by_kind(found, "wake-launched", agent="b")), "")
    off_b = persistence.off_of(persistence.slot_of(h.meta_of("agents/b"), run_b)) if run_b else ["?"]
    face = h.face("prof")
    members = {one.get("member"): one.get("launch") for one in face.get("members") or []}
    if (started.returncode == 0 and done and policies("agents/b") and all(p.get("model") == "m2" and p.get("effort") == "high"
                                                                          for p in policies("agents/b"))
            and all("model" not in p for p in policies("agents/a")) and off_b == ["plan"]
            and (members.get("b") or {}).get("model") == "m2" and (members.get("b") or {}).get("packages") == ["plan=off"]
            and (members.get("a") or {}).get("model") is None and (members.get("a") or {}).get("packages") == []
            and hashlib.sha256(doc.read_bytes()).hexdigest() == sha):
        held("(a) a member's profile", f"b on m2/high with plan off in its run {run_b}, a on the team's launch; "
             "members[].launch says it; TEAM.md the same to the byte")
    else:
        failures.append(f"  ✗ (a) a member's profile     rc={started.returncode} done={done} b={policies('agents/b')} "
                        f"a={policies('agents/a')} off={off_b} members={members} {started.stderr.strip()[-200:]!r}")

    # --- (b) what each member's run plays ---------------------------------------------------------------------
    def played(entries: list, key: str) -> dict:
        return {one.get(key): {pack.get("name"): pack.get("on") for pack in one.get("packages") or []}
                for one in entries}

    status_packs = played(face.get("members") or [], "member")
    declared = h.call("team", "declaration", "prof", "--json")
    try:
        agents = (json.loads(declared.stdout.strip().splitlines()[-1]).get("declared") or {}).get("agents") or []
    except (ValueError, IndexError):
        agents = []
    declared_packs = played(agents, "member")
    wanted = {"a": {"plan": True, "steering": False}, "b": {"plan": False, "steering": False}}
    if (declared.returncode == 0
            and all({name: packs.get(name) for name in ("plan", "steering")} == wanted[member]
                    for packs_of in (status_packs, declared_packs) for member, packs in
                    ((one, packs_of.get(one) or {}) for one in ("a", "b")))):
        held("(b) what each member's run plays", f"status {status_packs}, declaration {declared_packs}: b plan off, "
             "a plan on, both steering off")
    else:
        failures.append(f"  ✗ (b) packages played        rc={declared.returncode} status={status_packs} "
                        f"declaration={declared_packs} {declared.stderr.strip()[-200:]!r}")

    # --- (c) a refused profile leaves nothing ------------------------------------------------------------------
    untouched = not h.journal_of("none").exists() and not h.agent_stands("agents/n")
    if all(one.returncode == 2 and code(one) == wanted_code for wanted_code, one in said.items()) and untouched:
        held("(c) a refused profile leaves nothing", "package-required, package-invalid, package-unpinned: "
             "no journal, no agent born")
    else:
        failures.append("  ✗ (c) refused profiles       " + " ".join(f"{wanted_code}={one.returncode}:{code(one)!r}"
                                                                    for wanted_code, one in said.items())
                        + f" untouched={untouched}")

    # --- (d) a member that holds a task is kept -----------------------------------------------------------------
    asked = h.settled("hold", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    before = h.journal_of("hold").read_bytes() if h.journal_of("hold").is_file() else b""
    h.declare("hold", "---\nagents: |\n  x agents/x\nroot: x\nschedule: off\n---\nHold it alone.\n")
    dropped = h.call("team", "start", "hold", *h.harnessed, "--no-tick")
    if (holding.returncode == 0 and asked and dropped.returncode == 2 and code(dropped) == "member-held"
            and before and h.journal_of("hold").read_bytes() == before):
        held("(d) a member that holds a task is kept", "TEAM.md drops y while y holds an open task: member-held, "
             "the journal to the byte")
    else:
        failures.append(f"  ✗ (d) member held            rc={holding.returncode} asked={asked} "
                        f"dropped={dropped.returncode}:{code(dropped)!r} {dropped.stderr.strip()[-160:]!r}")
    return 0
