"""Scenario `team-season-refusals` -- 1 case(s) (batch la-saison, 2026-10-12: row 82 of the study § 18, team 0.31.0):
a season is judged whole before any write; the profiles themselves are `team-season-profiles`'s.
- (b) refusals leave nothing (KS16): `package-required` (agent off), `participant-unknown`, `package-invalid`,
  `package-unpinned`, and `member-held` (TEAM.md drops a member that holds an open task) -- the journal to the
  byte, no agent born
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={
        "x": [{"sleep": 0.1, "body": {"do": ["y"]}}],
        "y": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which?"}}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- (b) refusals leave nothing -- KS16 ------------------------------------------------------------------
    h.declare("none", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    tries = {"package-required": ("--member", "n", "--package", "agent=off"),
             "participant-unknown": ("--member", "nobody", "--model", "m2"),
             "package-invalid": ("--member", "n", "--package", "plan=maybe"),
             "package-unpinned": ("--member", "n", "--package", "nowhere=off")}
    said = {code: h.call("team", "start", "none", "--message", "x", *h.harnessed, "--no-tick", *extra)
            for code, extra in tries.items()}
    untouched = not h.journal_of("none").exists() and not h.agent_stands("agents/n")
    h.declare("hold", "---\nagents: |\n  x agents/x\n  y agents/y\nreports: |\n  y -> x\nroot: x\nschedule: off\n"
                      "---\nHold it.\n")
    h.call("team", "start", "hold", "--message", "ask around", *h.harnessed)
    asked = h.settled("hold", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    before = h.journal_of("hold").read_bytes()
    h.declare("hold", "---\nagents: |\n  x agents/x\nroot: x\nschedule: off\n---\nHold it alone.\n")
    dropped = h.call("team", "start", "hold", *h.harnessed, "--no-tick")
    if (all(one.returncode == 2 and code in one.stderr for code, one in said.items()) and untouched
            and asked and dropped.returncode == 2 and "member-held" in dropped.stderr and "y" in dropped.stderr
            and h.journal_of("hold").read_bytes() == before):
        held("(b) refusals leave nothing", "package-required, participant-unknown, package-invalid, package-unpinned: "
             "no journal, no agent born; member-held: the journal to the byte -- KS16")
    else:
        failures.append("  ✗ (b) refusals               " + " ".join(f"{code}={one.returncode}:{one.stderr.strip()[-90:]!r}"
                                                                  for code, one in said.items())
                        + f" untouched={untouched} asked={asked} dropped={dropped.returncode}:{dropped.stderr.strip()[-120:]!r}")
    return 0
