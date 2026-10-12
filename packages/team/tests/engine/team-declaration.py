"""Scenario `team-declaration` -- 4 case(s) (batch la-declaration-de-l-equipe, 2026-10-11: row 80 of the study
§ 18, team 0.26.0): `team declaration <name> [--json]` READS a team's declaration -- its text, start's own
judge's verdict and its gap to the start, key by key -- and writes nothing. No wake-up plays: every start is
`--no-tick`.
- (a) before any start: the text byte for byte, `verdict {ok: true}`, `started: null`, `pending: []`; the
  text says `not started`
- (b) the gap to the start: `budget` raised and a member added with its edge -- `changed: true`, `pending`
  on `agents`, `reports` and `limits` with the start's values and the file's; then the body alone rewritten --
  `changed: true`, `pending: []` (the body is served at once, never pending)
- (c) a broken TEAM.md is said: a root nobody declares -- rc 0, `verdict {ok: false, refusal}`, the refusal
  word for word the one `team start` writes on the same file, `pending: null`
- (d) refused, and nothing written: `team-unknown`, the usage; the journal, TEAM.md and the calendar to the
  byte across every read
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

FRONT = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
         "budget: 5\nschedule: off\n---\n")
BODY = "Name the work.\n"
WIDER = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\n  p3 agents/p3\nreports: |\n  p1 p2 p3 -> f\n"
         "root: f\nbudget: 9\nschedule: off\n---\n")
BROKEN = FRONT.replace("root: f", "root: ghost")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    doc = h.teams / "d" / "TEAM.md"
    reads: list[tuple[bytes, bytes, bytes]] = []

    def kept() -> tuple[bytes, bytes, bytes]:
        journal = h.journal_of("d")
        return (journal.read_bytes() if journal.is_file() else b"", doc.read_bytes() if doc.is_file() else b"",
                h.crontab.read_bytes() if h.crontab.is_file() else b"")

    def read(*flags: str):
        before = kept()
        said = h.call("team", "declaration", "d", *flags, now="08:00")
        reads.append((before, kept()))
        return said

    def faced():
        said = read("--json")
        lines = said.stdout.splitlines()
        return said, (json.loads(lines[0]) if said.returncode == 0 and len(lines) == 1 else {})

    # --- (a) before any start ---------------------------------------------------------------------
    h.declare("d", FRONT + BODY)
    said, face = faced()
    text = read()
    if (said.returncode == 0 and face.get("team") == "d" and face.get("text") == FRONT + BODY
            and face.get("verdict") == {"ok": True, "refusal": None} and face.get("started") is None
            and face.get("pending") == [] and face.get("changed") is False and str(face.get("path", "")).endswith("TEAM.md")
            and text.returncode == 0 and "not started" in text.stdout and "verdict ok" in text.stdout
            and "Name the work." in text.stdout):
        held("(a) before any start", "the text byte for byte, verdict ok, started null, pending [], changed false; "
             "the text says `not started`")
    else:
        failures.append(f"  ✗ (a) before the start      rc={said.returncode}/{text.returncode} face={face} "
                        f"{(said.stderr or text.stderr).strip()[-160:]!r}")

    # --- (b) the gap to the start ---------------------------------------------------------------
    h.call("team", "start", "d", "--message", "go", "--no-tick", now="07:50")
    started = next(iter(T.by_kind(h.events("d"), "team-started")), {})
    doc.write_text(WIDER + BODY, encoding="utf-8")
    _, wide = faced()
    text = read()
    doc.write_text(FRONT + "Name the work, now in one line each.\n", encoding="utf-8")
    _, body = faced()
    pending = {one["key"]: one for one in wide.get("pending") or []}
    if (wide.get("changed") is True and wide.get("verdict", {}).get("ok") is True
            and list(pending) == ["agents", "reports", "limits"]
            and pending["agents"]["started"] == started.get("agents")
            and pending["agents"]["declared"] == {**started.get("agents", {}), "p3": "agents/p3"}
            and pending["reports"]["declared"] == [{"from": ["p1", "p2", "p3"], "to": "f"}]
            and pending["limits"]["started"] == {"budget": 5} and pending["limits"]["declared"] == {"budget": 9}
            and (wide.get("started") or {}).get("id") == started.get("id")
            and "limits:" in text.stdout and "agents:" in text.stdout
            and body.get("changed") is True and body.get("pending") == []):
        held("(b) the gap to the start", "budget 5 -> 9 and p3 added: pending agents, reports, limits with the "
             "start's values and the file's; the body alone rewritten: changed, pending []")
    else:
        failures.append(f"  ✗ (b) the gap              wide={wide.get('changed')} {list(pending)} {pending} "
                        f"body={body.get('changed')}/{body.get('pending')} {text.stdout[-200:]!r}")

    # --- (c) a broken TEAM.md is said -------------------------------------------------------------
    doc.write_text(BROKEN + BODY, encoding="utf-8")
    said, broken = faced()
    text = read()
    refused = h.call("team", "start", "d", "--message", "again", "--no-tick", now="08:01")
    words = refused.stderr.strip().removeprefix("pp-team: ")
    if (said.returncode == 0 and refused.returncode == 2 and "participant-unknown" in words
            and broken.get("verdict") == {"ok": False, "refusal": words} and broken.get("pending") is None
            and broken.get("text") == BROKEN + BODY and text.returncode == 0 and words in text.stdout):
        held("(c) a broken TEAM.md is said", f"rc 0, verdict refused word for word as start: `{words[:70]}…`; "
             "pending null")
    else:
        failures.append(f"  ✗ (c) broken                rc={said.returncode} verdict={broken.get('verdict')} "
                        f"start={words!r} pending={broken.get('pending', '?')}")

    # --- (d) refused, and nothing written ---------------------------------------------------------
    unknown = h.call("team", "declaration", "ghost")
    bare = h.call("team", "declaration")
    flagged = h.call("team", "declaration", "d", "--yes")
    if (unknown.returncode == 2 and "team-unknown" in unknown.stderr and bare.returncode == 2 and "usage" in bare.stderr
            and flagged.returncode == 2 and "usage" in flagged.stderr
            and reads and all(before == after for before, after in reads)):
        bench.refusals += 3
        held("(d) refused, nothing written", f"team-unknown, the usage twice; the journal, TEAM.md and the calendar "
             f"to the byte across {len(reads)} reads")
    else:
        failures.append(f"  ✗ (d) refused / written     rc={unknown.returncode}/{bare.returncode}/{flagged.returncode} "
                        f"unchanged={[before == after for before, after in reads]}")
    return 0
