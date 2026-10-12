"""Scenario `team-names` -- 2 case(s) (batch le-nom-des-taches, 2026-10-11: row 78 of the study § 18, team
0.24.0): a task may carry a NAME, and a ring names its task and says a CONSIGNE instead of its ceremony's
declaration line (s.784). No wake-up plays: every call is `--no-tick`, the clock frozen by `PP_NOW`.
- (a) named: `start --name`, `post --name`, a task without one -- a name a user types (`Prix de la DDR4`,
  `  Réunion fournisseurs  ` kept trimmed); the `task` event carries `name` (absent without), `status --json`
  says it (`null` without), `log --json` too, the text of `status` says `T2 Prix de la DDR4 · open`; an
  empty name, a line break, 81 characters refuse `name-invalid`, the journal byte-identical (rework of
  2026-10-11, team 0.24.1: a free text of one line, no longer a slug)
- (b) a ring at hand on Thursday 10:05 names its task `daily 2026-10-01 10:05`; its task and each `do` to a
  participant say the ceremony rings and whom to answer, never the declaration line
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

DUO = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
       "ceremonies: |\n  daily every weekday 09:30 with p1 p2 -> f\nschedule: off\n---\nName the work.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind = T.by_kind

    # --- (a) a task named at its birth --------------------------------------------------------------
    h.declare("named", DUO)
    started = h.call("team", "start", "named", "--message", "watch the prices", "--name", "  Réunion fournisseurs  ",
                     "--no-tick", now="07:50")
    posted = h.call("team", "post", "named", "--message", "price of DDR4", "--name", "Prix de la DDR4", "--no-tick",
                    now="07:51")
    bare = h.call("team", "post", "named", "--message", "anything else", "--no-tick", now="07:52")
    journal = h.journal_of("named")
    before = journal.read_bytes() if journal.is_file() else b""
    invalid = [h.call("team", "post", "named", "--message", "x", "--name", given, "--no-tick", now="07:53")
               for given in ("   ", "line one\nline two", "x" * 81)]
    untouched = (journal.read_bytes() if journal.is_file() else b"") == before
    tasks = by_kind(h.events("named"), "task")
    faced = h.call("team", "status", "named", "--json", now="07:54").stdout.splitlines()
    face = json.loads(faced[0]) if faced else {}
    named = {one["id"]: one.get("name", "?") for one in face.get("tasks") or []}
    logged = [json.loads(line) for line in h.call("team", "log", "named", "--json", now="07:54").stdout.splitlines()
              if line.strip()]
    logged_names = [one.get("name") for one in logged if one.get("event") == "task"]
    text = h.call("team", "status", "named", now="07:54").stdout
    if (started.returncode == 0 and posted.returncode == 0 and bare.returncode == 0
            and [one.get("name") for one in tasks] == ["Réunion fournisseurs", "Prix de la DDR4", None]
            and "name" not in tasks[2]
            and named == {"T1": "Réunion fournisseurs", "T2": "Prix de la DDR4", "T3": None}
            and logged_names == ["Réunion fournisseurs", "Prix de la DDR4", None]
            and "T2 Prix de la DDR4 · open" in text and "T3 · open" in text
            and all(one.returncode == 2 and "name-invalid" in one.stderr for one in invalid) and untouched):
        bench.refusals += 3
        held("(a) a task named at its birth", "start and post --name write a name a user types (`Réunion "
             "fournisseurs` trimmed, `Prix de la DDR4`); status --json and log --json say it (null without), status "
             "`T2 Prix de la DDR4 · open`; empty, two lines, 81 characters refuse name-invalid")
    else:
        failures.append(f"  ✗ (a) named                  rc={started.returncode}/{posted.returncode}/{bare.returncode}/"
                        f"{[one.returncode for one in invalid]} tasks={[one.get('name') for one in tasks]} face={named} "
                        f"log={logged_names} {[one.stderr.strip()[-100:] for one in invalid]!r} "
                        f"{started.stderr.strip()[-160:]!r}")

    # --- (b) a ring names its task and says a consigne ------------------------------------------------
    h.declare("rung", DUO)
    h.call("team", "start", "rung", "--message", "open the day", "--no-tick", now="07:50")
    rang = h.call("team", "ring", "rung", "daily", "--no-tick", now="10:05")
    found = h.events("rung")
    ring_task = next((one for one in by_kind(found, "task") if one.get("ceremony") == "daily"), {})
    dos = [one for one in by_kind(found, "post", verb="do") if one.get("task") == ring_task.get("task")]
    said = [ring_task.get("text") or ""] + [one.get("text") or "" for one in dos]
    if (rang.returncode == 0 and ring_task.get("name") == "daily 2026-10-01 10:05" and len(dos) == 2
            and all("rings" in one and "every weekday" not in one and "->" not in one for one in said)
            and all(" f" in one.get("text", "") for one in dos)):
        held("(b) a ring names its task and says a consigne", f"`{ring_task.get('name')}`; the do: "
             f"`{dos[0].get('text')}` -- never the declaration line")
    else:
        failures.append(f"  ✗ (b) the ring              rc={rang.returncode} task={ring_task} dos={dos} "
                        f"{rang.stderr.strip()[-160:]!r}")
    return 0
