"""Scenario `team-intention` -- 6 case(s) (batch le-rythme-et-les-entrees, rework of 2026-10-10, team
0.17.0): the team's intention is the body of `teams/<name>/TEAM.md`, SERVED by pp to the team's runs --
`TEAM-<name>.md` names it in its `serve:` row at the kit's `turn.begin` -- never copied into a message
nor into the journal.
- (a) the opening: the member's first prompt carries `INFORMATION — TEAM.md` and the body in pp's
  output; the message of the wake-up carries no intention
- (b) a resume, `TEAM.md` unchanged: the reading is not served again
- (c) the body edited between two wake-ups of the same run -- no start, no reset: the next wake-up,
  under the same key, serves the new body and never the old one
- (d) the team's document: without entries it serves `TEAM.md` and carries no `next:` nor `decide:`;
  with entries its `next:` and `decide:` stand beside the row; with entries and no body it serves
  itself; with neither, no document
- (e) a run of the same agent opened without the team's root never reads the intention
- (f) `team-started` keeps no `intention`, its `digest` stays; a journal written before, with the
  field, reads; `status` says a `TEAM.md` changed since the start
"""
from __future__ import annotations

import json
import re
import time

from tests.harness import cli, support

T = support(__file__, "team")
BODY = "Merge what is asked."
EDITED = "Merge and tag what is asked."
READING = "INFORMATION — TEAM.md"
CHANGED = "TEAM.md changed since the start"


def _split(prompt: str) -> tuple[str, str]:
    """-> (the message of a wake-up, pp's output after it)."""
    at = prompt.find("▌ pp · run")
    return (prompt, "") if at < 0 else (prompt[:at], prompt[at:])


def _block(h, path: str) -> str:
    """-> what a run of the agent opened WITHOUT the team's root serves, chunk after chunk."""
    meta = h.meta_of(path)
    opened = cli(h.engine, "--instance", str(meta), "-new", cwd=meta.parent, env=h.env)
    chunks = [opened.stdout]
    key = re.search(r"run ([0-9a-f]{6})", opened.stdout)
    for _ in range(12):
        if not key or "a reading continues" not in chunks[-1]:
            break
        chunks.append(cli(h.engine, "--instance", str(meta), key.group(1), cwd=meta.parent, env=h.env).stdout)
    return "".join(chunks)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"lead": {"T1": [{"sleep": 0.1, "body": {"done": "one"}}],
                                        "T2": [{"sleep": 0.1, "body": {"done": "two"}}],
                                        "T3": [{"sleep": 0.1, "body": {"done": "three"}}]}})
    by_kind, all_ended, runs_launched = T.by_kind, T.all_ended, T.runs_launched

    h.declare("aim", f"---\nagents: |\n  lead agents/lead\nroot: lead\nschedule: off\n---\n{BODY}\n")
    started = h.call("team", "start", "aim", "--message", "merge PR 11", *h.harnessed)
    first = h.settled("aim", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    time.sleep(0.5)

    # --- (a) the opening: the intention served by pp, absent from the message --------------------------
    prompts = h.prompts_of("lead")
    message, served = _split(prompts[0] if prompts else "")
    if (started.returncode == 0 and first and READING in served and BODY in served[served.find(READING):]
            and BODY not in message):
        held("(a) the opening serves the intention", f"lead's first prompt: `{READING}` and the body in pp's "
             f"output ({len(prompts[0])} c), the message ({len(message)} c) without it")
    else:
        failures.append(f"  ✗ (a) the opening              rc={started.returncode} first={first} "
                        f"reading={READING in served} in_message={BODY in message} {started.stderr[-200:]!r} "
                        f"{message[-300:]!r}")

    # --- (b) a resume, TEAM.md unchanged: nothing served again -------------------------------------------
    second = h.call("team", "post", "aim", "--to", "lead", "--message", "merge PR 12")
    resumed = h.settled("aim", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), 60)
    time.sleep(0.5)
    prompts = h.prompts_of("lead")
    again = prompts[1] if len(prompts) > 1 else ""
    if second.returncode == 0 and resumed and again and READING not in again and BODY not in again:
        held("(b) a resume does not read it again", f"lead's second prompt ({len(again)} c): no `{READING}`, "
             "no body -- the reading proven in the run")
    else:
        failures.append(f"  ✗ (b) the unchanged resume     rc={second.returncode} resumed={resumed} "
                        f"prompts={len(prompts)} reading={READING in again} body={BODY in again}")

    # --- (c) the body edited mid-run: served at the next exchange, same key ------------------------------
    doc = h.teams / "aim" / "TEAM.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace(BODY, EDITED), encoding="utf-8")
    third = h.call("team", "post", "aim", "--to", "lead", "--message", "tag release 3")
    edited = h.settled("aim", lambda found: bool(by_kind(found, "done", task="T3")) and all_ended(found), 60)
    time.sleep(0.5)
    found = h.events("aim")
    prompts = h.prompts_of("lead")
    later = prompts[2] if len(prompts) > 2 else ""
    message3, served3 = _split(later)
    runs = runs_launched(found, "lead")
    if (third.returncode == 0 and edited and len(runs) == 1 and READING in served3 and EDITED in served3
            and BODY not in later and EDITED not in message3
            and not by_kind(found, "team-started")[1:] and not by_kind(found, "run-reset")):
        held("(c) an edited body reaches the member mid-run", f"TEAM.md rewritten, no start nor reset: lead's "
             f"third prompt, run {sorted(runs)[0]}, serves the new body, never the old one")
    else:
        failures.append(f"  ✗ (c) the edited body          rc={third.returncode} edited={edited} runs={runs} "
                        f"reading={READING in served3} new={EDITED in served3} old={BODY in later}")

    # --- (d) the team's document, entries or not ---------------------------------------------------------
    own = h.teams / "aim" / "TEAM-aim.md"
    aim_doc = own.read_text(encoding="utf-8") if own.is_file() else ""
    h.declare("beat", "---\nagents: |\n  b agents/b\nroot: b\nentries: |\n  do -> WORK.md\nschedule: off\n---\n"
                      "Keep the beat.\n")
    (h.teams / "beat" / "WORK.md").write_text("---\nproc: |\n  WORK\n---\n# WORK\n\nDo it.\n", encoding="utf-8")
    h.declare("mute", "---\nagents: |\n  q agents/q\nroot: q\nentries: |\n  do -> WORK.md\nschedule: off\n---\n")
    (h.teams / "mute" / "WORK.md").write_text("---\nproc: |\n  WORK\n---\n# WORK\n\nDo it.\n", encoding="utf-8")
    h.declare("bare", "---\nagents: |\n  z agents/z\nroot: z\nschedule: off\n---\n")
    made = [h.call("team", "start", name, "--message", "x", *h.harnessed, "--no-tick")
            for name in ("beat", "mute", "bare")]
    beat_doc = (h.teams / "beat" / "TEAM-beat.md").read_text(encoding="utf-8") \
        if (h.teams / "beat" / "TEAM-beat.md").is_file() else ""
    mute_doc = (h.teams / "mute" / "TEAM-mute.md").read_text(encoding="utf-8") \
        if (h.teams / "mute" / "TEAM-mute.md").is_file() else ""
    if (all(one.returncode == 0 for one in made)
            and "serve: |\n  TEAM.md\n" in aim_doc and "attach: turn.begin" in aim_doc
            and "next:" not in aim_doc and "decide:" not in aim_doc
            and "serve: |\n  TEAM.md\n" in beat_doc and "next: WORK.md TEAM-IDLE.md" in beat_doc
            and "decide: pp-team entry beat" in beat_doc
            and "serve: |\n  TEAM-mute.md\n" in mute_doc and "decide: pp-team entry mute" in mute_doc
            and not (h.teams / "bare" / "TEAM-bare.md").exists()):
        held("(d) the team's document serves the intention", "without entries: `serve: TEAM.md`, no next nor "
             "decide; with entries: the row beside next and decide; entries without a body: itself; neither: "
             "no document")
    else:
        failures.append(f"  ✗ (d) the team's document      rc={[one.returncode for one in made]} aim={aim_doc!r} "
                        f"beat={beat_doc!r} mute={mute_doc!r} bare={(h.teams / 'bare' / 'TEAM-bare.md').exists()}")

    # --- (e) a run without the team's root never reads it ------------------------------------------------
    outside = _block(h, "agents/lead")
    if outside and READING not in outside and EDITED not in outside and BODY not in outside:
        held("(e) a run without the root does not read it", f"a run of agents/lead opened without "
             f"--documents ({len(outside)} c): no `{READING}`, no body")
    else:
        failures.append(f"  ✗ (e) outside the team         {len(outside)}c reading={READING in outside} "
                        f"body={EDITED in outside or BODY in outside}")

    # --- (f) the journal keeps no copy; status says a changed TEAM.md ------------------------------------
    started_event = (by_kind(found, "team-started") or [{}])[0]
    line = h.status_line("aim", CHANGED)
    h.declare("old", "---\nagents: |\n  o agents/o\nroot: o\nschedule: off\n---\nThe old way.\n")
    forged = {**started_event, "id": 1, "team": "old", "agents": {"o": "agents/o"}, "root": "o",
              "intention": "The old way.", "digest": "000000000000"}
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(json.dumps(forged) + "\n", encoding="utf-8")
    old = h.call("team", "status", "old")
    if (started_event and "intention" not in started_event and len(str(started_event.get("digest") or "")) == 12
            and line and old.returncode == 0 and "team old" in old.stdout):
        held("(f) the journal keeps no copy", f"team-started without `intention`, digest "
             f"{started_event.get('digest')}; status says {line.strip()!r}; a journal with the field reads")
    else:
        failures.append(f"  ✗ (f) the journal              keys={sorted(started_event)} line={line!r} "
                        f"old={old.returncode} {old.stderr[-200:]!r}")
    return 0
