"""Scenario `team-season-written` -- 4 case(s) (batch la-saison-ecrite, split out of `team-season-profiles` by rule 10):
the season `teams/<name>/SEASON.md` writes -- the team's launch, its limits, its packages, the members' profiles --
opened by `team start` without a flag, each flag covering its key and written there, the rest at its bytes, judged
whole before any write. One house pinning `agent`, `team`, `steering` and `plan`; each team under its own names,
stopped before its next season.
- (a) the season written: `SEASON.md` says the team's launch, its budget, a package and two profiles; `start` without
  a flag keeps them at `team-started` (`launch`, `season`, `packages`, `profiles`, in their form), w2's launch carries
  its model; a second `start` without a flag opens the same season on those four keys
- (b) a flag covers and writes: `--member w2 --model mx` opens the season on mx, `SEASON.md` the bytes of before but
  w2's `model=`; the next `start` without a flag opens the same season; and byte for byte, each write the key a flag
  gives alone: team flags (`--model`, `--budget`) on a CRLF file, its line endings kept; a `--package` on a block
  written inline, become a `|` block with the new line; a file without front matter, its body under the one laid
- (c) `SEASON.md` born of a flag alone: a `start` without a flag writes no file; `--member c1 --effort high` writes it
  with that line alone
- (d) a refused season writes nothing: an unknown key and a profile line out of its form (`season-invalid`), a budget
  of 0 (`budget-invalid`), a profile of nobody (`participant-unknown`), a flag of nobody over a standing file -- the
  team's directory byte for byte, no journal, no agent born
"""
from __future__ import annotations

import json
import re

from tests.harness import support

T = support(__file__, "team")

REFUSAL = re.compile(r"^pp-team: ([a-z][a-z-]*)", re.M)


def code(played) -> str:
    """-> the code of the refusal a call wrote on stderr, '' when none."""
    found = REFUSAL.search(played.stderr or "")
    return found.group(1) if found else ""


def as_set(values) -> dict:
    """-> `{name: on|off}` of a list of `<name>=on|off`."""
    return dict(str(one).partition("=")[::2] for one in values or [])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan"), script={
        # (a) w1 delegates to w2, which plays the profile SEASON.md writes
        "w1": [{"sleep": 0.1, "body": {"do": ["w2"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "w2": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def policies(path: str) -> list[dict]:
        return [one.get("policy") or {} for one in T.lines(h.records / "messages.jsonl") if one.get("to") == path]

    # --- (a) the season written ---------------------------------------------------------------------------------
    command, grammar = h.harnessed[1], h.harnessed[3]
    h.declare("wr", "---\nagents: |\n  w1 agents/w1\n  w2 agents/w2\nreports: |\n  w2 -> w1\nroot: w1\n"
                    "schedule: off\n---\nA written season.\n")
    season = h.teams / "wr" / "SEASON.md"
    season.write_text(f"---\nharness: {json.dumps(command)}\nprovider: {grammar}\neffort: low\nbudget: 9\n"
                      "packages: |\n  steering=on\nprofiles: |\n  w1 model=mw1\n  w2 model=mw2 effort=high package.plan=on\n"
                      "---\nThe owner's word on the season.\n", encoding="utf-8")
    written = h.call("team", "start", "wr", "--message", "both of you")
    wr_done = h.settled("wr", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    h.off_season("wr")
    again = h.call("team", "start", "wr", "--no-tick")
    seasons = by_kind(h.events("wr"), "team-started")
    keys = ("launch", "season", "packages", "profiles")
    first, second = (seasons + [{}, {}])[:2]
    on = {"agent": "on", "team": "on", "steering": "on", "plan": "off"}
    w2 = (first.get("profiles") or {}).get("w2") or {}
    if (written.returncode == 0 and wr_done and again.returncode == 0 and len(seasons) == 2
            and first.get("launch") == {"harness": command, "provider": grammar, "effort": "low"}
            and first.get("season") == {"budget": 9.0} and as_set(first.get("packages")) == on
            and (first.get("profiles") or {}).get("w1") == {"model": "mw1"}
            and {key: w2.get(key) for key in ("model", "effort")} == {"model": "mw2", "effort": "high"}
            and as_set(w2.get("packages")) == {**on, "plan": "on"}
            and policies("agents/w2") and all(one.get("model") == "mw2" for one in policies("agents/w2"))
            and all(first.get(key) == second.get(key) for key in keys)):
        held("(a) the season written", "SEASON.md's launch, budget 9, steering on and two profiles at team-started; "
             "w2 launched on mw2; a second start without a flag the same on launch, season, packages, profiles")
    else:
        failures.append(f"  ✗ (a) the season written     rc={written.returncode}/{again.returncode} done={wr_done} "
                        f"first={ {key: first.get(key) for key in keys} } second_same="
                        f"{[first.get(key) == second.get(key) for key in keys]} w2={policies('agents/w2')} "
                        f"{written.stderr.strip()[-200:]!r}")

    # --- (b) a flag covers and writes ------------------------------------------------------------------------------
    before = season.read_bytes()
    h.off_season("wr")
    flagged = h.call("team", "start", "wr", "--no-tick", "--member", "w2", "--model", "mx")
    after = season.read_bytes()
    h.off_season("wr")
    replayed = h.call("team", "start", "wr", "--no-tick")
    seasons = by_kind(h.events("wr"), "team-started")
    third, fourth = (seasons + [{}, {}, {}, {}])[2:4]
    if (flagged.returncode == 0 and replayed.returncode == 0 and len(seasons) == 4
            and (((third.get("profiles") or {}).get("w2") or {}).get("model")) == "mx"
            and (((third.get("profiles") or {}).get("w2") or {}).get("effort")) == "high"
            and after == before.replace(b"w2 model=mw2 ", b"w2 model=mx ")
            and all(third.get(key) == fourth.get(key) for key in keys)):
        held("(b) a flag covers and writes", "--member w2 --model mx: the season on mx, effort high kept; SEASON.md "
             "the bytes of before but `model=mx`; the next start without a flag the same season")
    else:
        failures.append(f"  ✗ (b) a flag that writes      rc={flagged.returncode}/{replayed.returncode} "
                        f"w2={(third.get('profiles') or {}).get('w2')} after={after!r} "
                        f"same={[third.get(key) == fourth.get(key) for key in keys]} {flagged.stderr.strip()[-200:]!r}")

    h.declare("wb", "---\nagents: |\n  b9 agents/b9\nroot: b9\nschedule: off\n---\nWrites byte for byte.\n")
    written_to = h.teams / "wb" / "SEASON.md"
    crlf = "\r\n".join(["---", "model: m1", "profiles: |", "  b9 effort=low", "---", "Body", ""])
    inline = "\n".join(["---", "packages: plan=off", "---", "Word.", ""])
    bare_body = "The owner's word, no front matter.\n"
    writes = [("team flags on CRLF", crlf, ("--model", "mz", "--budget", "2.5"),
               crlf.replace("model: m1", "model: mz").replace("  b9 effort=low\r\n", "  b9 effort=low\r\nbudget: 2.5\r\n")),
              ("a package on an inline block", inline, ("--package", "steering=on"),
               inline.replace("packages: plan=off\n", "packages: |\n  plan=off\n  steering=on\n")),
              ("a file without front matter", bare_body, ("--effort", "high"), "---\neffort: high\n---\n" + bare_body)]
    wrong_writes = []
    for label, text, extra, wanted_text in writes:
        written_to.write_bytes(text.encode("utf-8"))
        h.off_season("wb")
        played = h.call("team", "start", "wb", "--no-tick", *extra)
        got = written_to.read_bytes()
        if played.returncode != 0 or got != wanted_text.encode("utf-8"):
            wrong_writes.append(f"{label}: rc={played.returncode} got={got!r} {played.stderr.strip()[-160:]!r}")
    if not wrong_writes:
        held("(b) each write byte for byte", "--model and --budget on a CRLF file, its endings kept; --package on an "
             "inline block, now a | block; a file without front matter, its body under the one laid")
    else:
        failures.append(f"  ✗ (b) each write byte for byte {wrong_writes}")

    # --- (c) SEASON.md born of a flag alone ---------------------------------------------------------------------
    h.declare("cr", "---\nagents: |\n  c1 agents/c1\nroot: c1\nschedule: off\n---\nNo season yet.\n")
    born_file = h.teams / "cr" / "SEASON.md"
    bare = h.call("team", "start", "cr", "--no-tick")
    absent = not born_file.exists()
    h.off_season("cr")
    profiled = h.call("team", "start", "cr", "--no-tick", "--member", "c1", "--effort", "high")
    made = born_file.read_text(encoding="utf-8") if born_file.is_file() else ""
    if bare.returncode == 0 and absent and profiled.returncode == 0 and made == "---\nprofiles: |\n  c1 effort=high\n---\n":
        held("(c) SEASON.md born of a flag alone", "no flag: no file; --member c1 --effort high: the file with that line "
             "alone")
    else:
        failures.append(f"  ✗ (c) SEASON.md born          rc={bare.returncode}/{profiled.returncode} absent={absent} "
                        f"made={made!r} {profiled.stderr.strip()[-200:]!r}")

    # --- (d) a refused season writes nothing --------------------------------------------------------------------------
    h.declare("bad", "---\nagents: |\n  b1 agents/b1\nroot: b1\nschedule: off\n---\nNever started.\n")
    bad_season = h.teams / "bad" / "SEASON.md"
    good = "---\nmodel: m1\nprofiles: |\n  b1 effort=low\n---\nThe owner's word.\n"
    tries = [("season-invalid", good.replace("model: m1", "colour: red"), ()),
             ("season-invalid", good.replace("b1 effort=low", "b1 effort"), ()),
             ("budget-invalid", good.replace("model: m1", "budget: 0"), ()),
             ("participant-unknown", good.replace("b1 effort=low", "ghost effort=low"), ()),
             ("participant-unknown", good, ("--member", "ghost", "--model", "m9"))]
    wrong = []
    for wanted_code, text, extra in tries:
        bad_season.write_text(text, encoding="utf-8")
        files = {one.name: one.read_bytes() for one in (h.teams / "bad").iterdir()}
        tried = h.call("team", "start", "bad", "--no-tick", *extra)
        if (tried.returncode != 2 or code(tried) != wanted_code or h.journal_of("bad").exists()
                or h.agent_stands("agents/b1")
                or {one.name: one.read_bytes() for one in (h.teams / "bad").iterdir()} != files):
            wrong.append(f"{wanted_code}: {tried.returncode}:{code(tried)!r} {tried.stderr.strip()[-160:]!r}")
    if not wrong:
        bench.refusals += len(tries)
        held("(d) a refused season writes nothing", "season-invalid twice, budget-invalid, participant-unknown from the "
             "file and from a flag: the directory byte for byte, no journal, no agent born")
    else:
        failures.append(f"  ✗ (d) a refused season       {wrong}")

    return 0
