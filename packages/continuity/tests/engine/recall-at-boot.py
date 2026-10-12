"""Scenario `recall-at-boot` -- the operations of the last days come with the boot (plan
pp-split, phase continuity, batch le-rappel-au-boot):
- RECALL attaches at boot.ready: its brief is served; the `continuity-recall` payload renders
  the entries of the period, oldest first, none older; an empty period or the key at 0 renders no section
- the kit alone knows neither RECALL nor its payload
- RECALL (a contributor) opens before HISTORY (a cadence) when both are due
- a heavy record comes through the cut: chunks under the cap, the content whole across them
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone

from conductor import discovery, render

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
SECTION = "▌ INFORMATION — continuity-recall"
BRIEF = "▌ INFORMATION — RECALL"


def _operations(made, stamped: list[tuple[datetime, str]]) -> None:
    path = made / ".sys" / "records" / "operations.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps({"at": when.isoformat(timespec="seconds"), "entry": text}) + "\n"
                            for when, text in stamped), encoding="utf-8")


def _setting(env, key: str, value: str) -> None:
    text = env.read("SETTINGS.md")
    edited = re.sub(rf"^{key}: .*$", f"{key}: {value}", text, flags=re.M)
    assert edited != text or f"{key}: {value}" in text, text[:300]
    env.write("SETTINGS.md", edited)


def _fresh(env):
    return env.__class__(name=env.name, made=env.made,
                         member=discovery.instance_member(env.engine), engine=env.engine)


def _boot(env, block_too: bool = False):
    opener = _fresh(env).conductor()
    block = opener.start(opener.boot("BOOT.md"))
    shown = render(block)
    opener.forget()
    return (block, shown) if block_too else shown


def _section(shown: str) -> str:
    """-> the recall section's text, up to the next section mark."""
    at = shown.find(SECTION)
    if at < 0:
        return ""
    rest = shown[at + len(SECTION):]
    end = rest.find("\n▌ ")
    return rest if end < 0 else rest[:end]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    now = datetime.now(timezone.utc)

    # --- the brief comes, the period decides the section -------------------------------------
    env = bench.env("recall", packages=("continuity",))
    fresh = _boot(env)
    _operations(env.made, [(now - timedelta(days=10), "the old one"),
                           (now - timedelta(days=3), "the recent two"),
                           (now - timedelta(days=1), "the recent one")])
    served = _boot(env)
    section = _section(served)
    if (BRIEF in fresh and SECTION not in fresh and BRIEF in served and section
            and "the recent two" in section and "the recent one" in section and "the old one" not in section
            and section.find("the recent two") < section.find("the recent one")):
        held("the recall serves the period, oldest first",
             "a fresh install: the brief alone; three operations: the two within 7 days, the 10-day one left out")
    else:
        failures.append(f"  ✗ recall period              fresh={SECTION in fresh} section={section[:120]!r}")

    # --- the key at 0: no section, the brief still comes --------------------------------------
    _setting(env, "continuity_recall_days", "0")
    muted = _boot(env)
    _setting(env, "continuity_recall_days", "7")
    if SECTION not in muted and BRIEF in muted:
        held("the key at 0 recalls nothing", "no recall section; RECALL's brief still comes")
    else:
        failures.append(f"  ✗ key at 0                   section={SECTION in muted} brief={BRIEF in muted}")

    # --- the kit alone: neither the brief nor the section -------------------------------------
    bare = bench.env("recallkit")
    _operations(bare.made, [(now - timedelta(days=1), "an operation the kit ignores")])
    alone = _boot(bare)
    if "RECALL" not in alone and SECTION not in alone:
        held("the kit alone recalls nothing", "an operation written, a boot: no RECALL, no payload section")
    else:
        failures.append("  ✗ kit alone                  RECALL or its payload appeared")

    # --- the order at boot.ready: the contributor before the cadence --------------------------
    order = bench.env("recallorder", packages=("continuity",))
    _setting(order, "continuity_history_day", WEEKDAYS[now.weekday()])
    _operations(order.made, [(now - timedelta(days=1), "an operation since")])
    block, both = _boot(order, block_too=True)
    if SECTION in both and block.document == "HISTORY":
        held("the recall comes before the digest",
             "RECALL (attach) is served behind, HISTORY (cadence) is the pending frame ahead -- contributors, then the cadences due")
    else:
        failures.append(f"  ✗ order at boot              recall={SECTION in both} pending={block.document!r}")

    # --- a heavy record comes through the cut -----------------------------------------------------------
    mass = bench.env("recallmass", packages=("continuity",))
    _setting(mass, "max_harness_tool_output", "25000")
    entries = [(now - timedelta(minutes=20 * n), f"entry {n:04d} " + "x" * 180) for n in range(320, 0, -1)]
    _operations(mass.made, entries)
    opener = _fresh(mass).conductor()
    block = opener.resume(opener.boot("BOOT.md"))
    chunks = [opener.rendered(block)]
    while opener.pending() and len(chunks) < 50:
        chunks.append(opener.next_chunk())
    joined = "".join(chunks)
    cap = 25000
    over = [len(one) for one in chunks if len(one) > cap]
    opener.forget()
    if len(chunks) >= 3 and not over and "entry 0320" in joined and "entry 0001" in joined:
        held("a heavy recall comes through the cut",
             f"{len(entries)} entries (~{sum(len(e) for _, e in entries)} chars): {len(chunks)} chunks, "
             f"biggest {max(len(one) for one in chunks)}, none over {cap}; first and last entries carried")
    else:
        failures.append(f"  ✗ heavy recall               chunks={len(chunks)} over={over} "
                        f"first={'entry 0320' in joined} last={'entry 0001' in joined}")
    return 0
