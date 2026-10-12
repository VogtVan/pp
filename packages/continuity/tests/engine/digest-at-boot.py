"""Scenario `digest-at-boot` -- the weekly digest is a declared cadence (plan pp-split,
phase continuity, batch l-historique-a-cadence):
- a fresh install boots silent: no operation since, nothing due
- an operation newer than the last digest, the anchored day crossed: HISTORY opens at
  boot.ready with pp-continuity offered; a digest at the boundary silences it;
  `never` silences it; the kit alone knows nothing of it
- the digest written from the block lands in history.jsonl, and the next boot is silent
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from conductor import contributions, discovery, render

WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _stamp(made, record: str, when: datetime) -> None:
    path = made / ".sys" / "records" / record
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"at": when.isoformat(timespec="seconds"), "entry": "bench"}) + "\n",
                    encoding="utf-8")


def _anchor(env, day: str) -> None:
    """The operator's edit of the composed SETTINGS: the digest's anchored weekday."""
    text = env.read("SETTINGS.md")
    import re
    edited = re.sub(r"^continuity_history_day: .*$", f"continuity_history_day: {day}", text, flags=re.M)
    assert edited != text or f"continuity_history_day: {day}" in text, text[:300]
    env.write("SETTINGS.md", edited)


def _boot(env) -> str:
    """A boot on a RE-DISCOVERED member: what the records say now, nothing remembered."""
    fresh = env.__class__(name=env.name, made=env.made,
                          member=discovery.instance_member(env.engine), engine=env.engine)
    opener = fresh.conductor()
    block = opener.start(opener.boot("BOOT.md"))
    shown = render(block)
    opener.forget()
    return shown


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    now = datetime.now(timezone.utc)
    today = WEEKDAYS[now.weekday()]

    # --- a fresh install: nothing since, nothing due ------------------------------------------
    env = bench.env("digest", packages=("continuity",))
    _anchor(env, today)
    first = _boot(env)
    if "▸ HISTORY{" not in first:
        held("a fresh install boots silent", "the seeds are empty: no operation since, the digest is not due")
    else:
        failures.append("  ✗ fresh install              HISTORY played on empty records")

    # --- an operation since, the day crossed: HISTORY at boot.ready ---------------------------
    _stamp(env.made, "operations.jsonl", now - timedelta(days=1))
    due = _boot(env)
    if "▸ HISTORY{" in due and "pp-continuity" in due:
        held("the digest is due after an operation and the crossing",
             "HISTORY CALLed at boot.ready from the manifest's cadence; pp-continuity offered")
    else:
        failures.append(f"  ✗ digest due                 {'HISTORY' in due} {'pp-continuity' in due}")

    # --- the digest written from the block: one line, the next boot silent ------------------
    record = env.made / ".sys" / "records" / "history.jsonl"
    before = record.read_text(encoding="utf-8") if record.is_file() else ""
    rc, out, err = contributions.run_skill(
        env.made, "pp-continuity", ["history", "add", "the week in one paragraph"])
    lines = [json.loads(one) for one in record.read_text(encoding="utf-8").splitlines() if one.strip()]
    after = _boot(env)
    if (rc == 0 and before.strip() == "" and len(lines) == 1
            and lines[0]["synthesis"] == "the week in one paragraph" and "▸ HISTORY{" not in after):
        held("the digest lands and consumes the crossing",
             "pp-continuity history add writes ONE {at, synthesis} line; the next boot carries no HISTORY")
    else:
        failures.append(f"  ✗ digest lands               rc={rc} {err.strip()[-80:]!r} lines={len(lines)} again={'HISTORY' in after}")

    # --- a stale digest with nothing since: silent; `never`: silent ---------------------------
    _stamp(env.made, "history.jsonl", now - timedelta(days=8))
    _stamp(env.made, "operations.jsonl", now - timedelta(days=9))
    quiet = _boot(env)
    _stamp(env.made, "operations.jsonl", now - timedelta(days=1))
    _anchor(env, "never")
    never = _boot(env)
    _anchor(env, today)
    moved = _boot(env)
    if "▸ HISTORY{" not in quiet and "▸ HISTORY{" not in never and "▸ HISTORY{" in moved:
        held("nothing since is silent, never is silent, a move is due",
             "a stale digest with no newer operation owes nothing; `never` switches the digest off; an operation since brings it back")
    else:
        failures.append(f"  ✗ since/never                quiet={'HISTORY' in quiet} never={'HISTORY' in never} moved={'HISTORY' in moved}")

    # --- the kit alone: nothing -----------------------------------------------------------------
    bare = bench.env("digestkit")
    _stamp(bare.made, "operations.jsonl", now - timedelta(days=1))
    alone = _boot(bare)
    if "HISTORY" not in alone and "pp-continuity" not in alone:
        held("the kit alone knows no digest", "an operation stamped, a boot: no HISTORY, no pp-continuity offer")
    else:
        failures.append("  ✗ kit alone                  HISTORY or pp-continuity appeared")
    return 0
