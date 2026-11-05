"""Scenario `continuity-boot` -- what continuity serves at boot.initialize:
- RECALL attaches with its `continuity-recall` section: the entries of the period, oldest
  first, none older; an empty period or `continuity_recall_days: 0` renders neither the
  section nor the brief
- HISTORY, the weekly digest, is a declared cadence: due after an operation newer than the
  last digest once the anchored day is crossed, with pp-continuity offered; the digest
  written from the block consumes the crossing; a stale digest with nothing since and
  `never` stay silent
- RECALL (a contributor) is served before HISTORY (a cadence) when both are due
- the recall-only profile: `continuity_history_day: never` and `continuity_recall_days: 7`
  together serve the recall and no digest
- a heavy record comes through the cut: chunks under the cap, the content whole across them
- the kit alone knows neither RECALL, its section, HISTORY nor pp-continuity

Two houses: the instance with continuity, and the kit alone for the absence.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conductor import contributions, discovery, render
from tests.harness import support

C = support(__file__, "continuity")

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SECTION = "▌ INFORMATION — continuity-recall"
BRIEF = "▌ INFORMATION — RECALL"
DIGEST = "▸ HISTORY{"


def _fresh(env):
    """The environment on a RE-DISCOVERED member: what the records say now."""
    return env.__class__(name=env.name, made=env.made,
                         member=discovery.instance_member(env.engine), engine=env.engine)


def _boot(env):
    """-> (the boot block, its rendering) of a fresh run."""
    opener = _fresh(env).conductor()
    block = opener.start(opener.boot("BOOT.md"))
    shown = render(block)
    opener.forget()
    return block, shown


def _section(shown: str) -> str:
    """-> the recall section's text, up to the next section mark."""
    at = shown.find(SECTION)
    if at < 0:
        return ""
    rest = shown[at + len(SECTION):]
    end = rest.find("\n▌ ")
    return rest if end < 0 else rest[:end]


def _history(made, when: datetime) -> None:
    path = made / ".sys" / "records" / "history.jsonl"
    path.write_text(json.dumps({"at": when.isoformat(timespec="seconds"), "entry": "bench"}) + "\n",
                    encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    now = datetime.now(timezone.utc)
    today = WEEKDAYS[now.weekday()]
    env = bench.env("boot", packages=("continuity",))

    def setting(key: str, value: str) -> None:
        if not C.setting(env, key, value):
            failures.append(f"  ✗ setting                    {key} absent from SETTINGS.md")

    # --- a fresh install: no recall, no digest ------------------------------------------------
    setting("continuity_history_day", today)
    _, first = _boot(env)
    if DIGEST not in first:
        held("a fresh install boots silent", "the seeds are empty: no operation since, the digest is not due")
    else:
        failures.append("  ✗ fresh install              HISTORY played on empty records")

    # --- three operations, the day crossed: the recall of the period, the digest due ----------
    C.operations(env.made, [(now - timedelta(days=10), "the old one"),
                            (now - timedelta(days=3), "the recent two"),
                            (now - timedelta(days=1), "the recent one")])
    block, served = _boot(env)
    section = _section(served)
    if (BRIEF not in first and SECTION not in first and BRIEF in served and section
            and "the recent two" in section and "the recent one" in section and "the old one" not in section
            and section.find("the recent two") < section.find("the recent one")):
        held("the recall serves the period, oldest first",
             "a fresh install: neither brief nor section; three operations: the two within 7 days, the 10-day one left out")
    else:
        failures.append(f"  ✗ recall period              fresh={BRIEF in first or SECTION in first} "
                        f"brief={BRIEF in served} section={section[:120]!r}")
    if DIGEST in served and "pp-continuity" in served:
        held("the digest is due after an operation and the crossing",
             "HISTORY CALLed at boot.initialize from the manifest's cadence; pp-continuity offered")
    else:
        failures.append(f"  ✗ digest due                 {DIGEST in served} {'pp-continuity' in served}")
    if SECTION in served and block.document == "HISTORY":
        held("the recall comes before the digest",
             "RECALL (attach) is served behind, HISTORY (cadence) is the pending frame ahead -- contributors, then the cadences due")
    else:
        failures.append(f"  ✗ order at boot              recall={SECTION in served} pending={block.document!r}")

    # --- the digest written from the block: one line, the next boot silent ------------------
    record = env.made / ".sys" / "records" / "history.jsonl"
    before = record.read_text(encoding="utf-8") if record.is_file() else ""
    rc, _, err = contributions.run_skill(
        env.made, "pp-continuity", ["history", "add", "the week in one paragraph"])
    lines = [json.loads(one) for one in record.read_text(encoding="utf-8").splitlines() if one.strip()]
    _, after = _boot(env)
    if (rc == 0 and before.strip() == "" and len(lines) == 1
            and lines[0]["synthesis"] == "the week in one paragraph" and DIGEST not in after):
        held("the digest lands and consumes the crossing",
             "pp-continuity history add writes ONE {at, synthesis} line; the next boot carries no HISTORY")
    else:
        failures.append(f"  ✗ digest lands               rc={rc} {err.strip()[-80:]!r} lines={len(lines)} "
                        f"again={DIGEST in after}")

    # --- the key at 0: neither the section nor the brief -------------------------------------
    setting("continuity_recall_days", "0")
    _, muted = _boot(env)
    setting("continuity_recall_days", "7")
    if SECTION not in muted and BRIEF not in muted:
        held("the key at 0 recalls nothing", "no recall section, and no brief without it")
    else:
        failures.append(f"  ✗ key at 0                   section={SECTION in muted} brief={BRIEF in muted}")

    # --- a stale digest with nothing since: silent; `never`: silent; a move: due ------------
    _history(env.made, now - timedelta(days=8))
    C.operations(env.made, [(now - timedelta(days=9), "before the digest")])
    _, quiet = _boot(env)
    C.operations(env.made, [(now - timedelta(days=1), "an operation of yesterday")])
    setting("continuity_history_day", "never")
    _, never = _boot(env)
    setting("continuity_history_day", today)
    _, moved = _boot(env)
    if DIGEST not in quiet and DIGEST not in never and DIGEST in moved:
        held("nothing since is silent, never is silent, a move is due",
             "a stale digest with no newer operation owes nothing; `never` switches the digest off; an operation since brings it back")
    else:
        failures.append(f"  ✗ since/never                quiet={DIGEST in quiet} never={DIGEST in never} "
                        f"moved={DIGEST in moved}")

    # --- the recall-only profile: the two keys together --------------------------------------
    setting("continuity_history_day", "never")
    setting("continuity_recall_days", "7")
    _, alone = _boot(env)
    if (BRIEF in alone and SECTION in alone and "an operation of yesterday" in _section(alone)
            and DIGEST not in alone):
        held("the boot serves the recall alone", "RECALL and its section carry yesterday's operation; no HISTORY under `never`")
    else:
        failures.append(f"  ✗ recall-only boot           brief={BRIEF in alone} section={SECTION in alone} "
                        f"history={DIGEST in alone}")

    # --- a heavy record comes through the cut ------------------------------------------------
    cap = 25000
    setting("max_harness_tool_output", str(cap))
    entries = [(now - timedelta(minutes=20 * n), f"entry {n:04d} " + "x" * 180) for n in range(320, 0, -1)]
    C.operations(env.made, entries)
    opener = _fresh(env).conductor()
    block = opener.resume(opener.boot("BOOT.md"))
    chunks = [opener.rendered(block)]
    while opener.pending() and len(chunks) < 50:
        chunks.append(opener.next_chunk())
    joined = "".join(chunks)
    over = [len(one) for one in chunks if len(one) > cap]
    opener.forget()
    if len(chunks) >= 3 and not over and "entry 0320" in joined and "entry 0001" in joined:
        held("a heavy recall comes through the cut",
             f"{len(entries)} entries (~{sum(len(e) for _, e in entries)} chars): {len(chunks)} chunks, "
             f"biggest {max(len(one) for one in chunks)}, none over {cap}; first and last entries carried")
    else:
        failures.append(f"  ✗ heavy recall               chunks={len(chunks)} over={over} "
                        f"first={'entry 0320' in joined} last={'entry 0001' in joined}")

    # --- the kit alone: no recall, no digest --------------------------------------------------
    bare = bench.env("boot-kit")
    C.operations(bare.made, [(now - timedelta(days=1), "an operation the kit ignores")])
    _, kit = _boot(bare)
    if "RECALL" not in kit and SECTION not in kit:
        held("the kit alone recalls nothing", "an operation written, a boot: no RECALL, no payload section")
    else:
        failures.append("  ✗ kit alone                  RECALL or its payload appeared")
    if "HISTORY" not in kit and "pp-continuity" not in kit:
        held("the kit alone knows no digest", "an operation stamped, a boot: no HISTORY, no pp-continuity offer")
    else:
        failures.append("  ✗ kit alone                  HISTORY or pp-continuity appeared")
    return 0
