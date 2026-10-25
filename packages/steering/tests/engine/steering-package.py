"""Scenario `steering-package` -- the package comes and goes on an instance that conducts:
- the kit alone carries no file, no catalogue line and no setting of steering
- a LATE add lands its keys, its offer and its turn.end contributor on an instance already
  running, and nothing but its declared surface: no record before a call
- its section of the standing orders: compiled into both marbles, gone from them at the boot
  that follows `package.steering: off`
- the LEDGER mounted at `boot.initialize` sweeps first (`exec: sweep`), then serves the active
  steps still to do at the run's first block -- a step untouched past its life archived and
  absent -- and the next exchange does not serve it again
- the steps are the INSTANCE's data: an upgrade and a doctor leave `steps.json` byte for byte
- remove gives back exactly what the add put, leaves the keys unowned and the record alone,
  and the socket falls silent again
"""
from __future__ import annotations

import contextlib
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tests.harness import na_proof, support
from conductor import compiling, install, instance, reading

S = support(__file__, "steering")

NOW = datetime(2026, 10, 25, 12, 0, 0, tzinfo=timezone.utc)
CLOCK = "PP_NOW"
MARBLES = ("system.md", "system.common.md")


def _offers(meta) -> set:
    """-> what TURN offers here: the composed tools, overlays applied."""
    document = reading.read(instance.resolve(meta, "TURN.md"))
    return {one.name for one in compiling.effective(meta, document)[1]}


def _steering_at(meta: Path, socket: str) -> list[str]:
    """-> the documents of the steering bundle contributing at `socket`."""
    return [name for name in instance.attached(meta, socket)
            if "steering@" in str(instance.resolve(meta, name))]


def _surface(meta: Path) -> dict:
    """The four surfaces a package may touch, plus its records -- read off the disk."""
    def lines(name: str) -> set[str]:
        path = meta / name
        return set(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else set()
    records = (meta / ".sys" / "records")
    return {"files": {str(p.relative_to(meta)) for p in meta.rglob("*")
                      if p.is_file() and ".sys/state" not in str(p.relative_to(meta))
                      and "__pycache__" not in p.parts},
            "catalogue": lines(".sys/tools.md"),
            "laws": set(compiling.render_registry(meta).splitlines()),   # derived: no registry file
            "settings": lines("SETTINGS.md"),
            "records": {p.name for p in records.glob("*")} if records.is_dir() else set()}


def _section(meta: Path) -> str:
    """-> the body of the vendored `system/SYSTEM.COMMON.md`, its front matter dropped."""
    vendored = next((meta / ".sys" / "vendor").glob("steering@*")) / "system" / "SYSTEM.COMMON.md"
    return vendored.read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()


def _marbles(meta: Path) -> list[str]:
    return [(meta / ".sys" / name).read_text(encoding="utf-8") for name in MARBLES]


@contextlib.contextmanager
def _clock(instant: datetime):
    """The keeper's clock -- read by every process the case starts -- set for the block."""
    kept = os.environ.get(CLOCK)
    os.environ[CLOCK] = instant.isoformat()
    try:
        yield
    finally:
        if kept is None:
            os.environ.pop(CLOCK, None)
        else:
            os.environ[CLOCK] = kept


def _boot(env):
    opener = env.conductor("t")
    return opener.start(opener.boot("BOOT.md"))


def _close(env) -> list:
    """-> the blocks from the work's own output to the closing; a proof is answered n/a."""
    blocks, pending = [], env.conductor("t").submit("")
    for _ in range(12):
        if pending is None:
            break
        blocks.append(pending)
        if pending.judged:
            env.conductor("t").submit(na_proof(pending))
            break
        if pending.wait:
            break
        pending = env.conductor("t").submit("")
    return blocks


def _switch(env, state: str) -> None:
    settings = env.made / "SETTINGS.md"
    text = settings.read_text(encoding="utf-8")
    other = "off" if state == "on" else "on"
    settings.write_text(text.replace(f"package.steering: {other}", f"package.steering: {state}"), encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("cycle")                 # the kit alone: no steering anywhere
    meta = env.made
    _boot(env)                               # the instance has conducted before the add
    before = (env.read("SETTINGS.md"), _offers(meta), list(instance.attached(meta, "turn.end")))
    absent = _surface(meta)

    # --- the kit alone knows nothing of steering ---------------------------------------------
    if (not any("steering" in one for one in absent["files"])
            and not any("steering" in one for one in absent["catalogue"] | absent["settings"])):
        held("the kit alone knows no steering", "no file, no catalogue line, no setting names it")
    else:
        failures.append(f"  ✗ kit alone                  {sorted(absent['files'])[:3]}")

    # --- the late add lands the whole surface --------------------------------------------
    install.add_package(env.member, "steering")
    settings = env.read("SETTINGS.md")
    landed = ("steering_life_days:" in settings and "steering_active_max:" in settings
              and "pp-steering" in _offers(meta) and _steering_at(meta, "turn.end")
              and not list(instance.attached(meta, "turn.begin")) + list(instance.mounting(meta, "turn.begin")))
    was_bare = "steering_" not in before[0] and "pp-steering" not in before[1]
    if was_bare and landed:
        held("a late add lands the whole surface",
             "on an instance that already conducts: its keys at the composed SETTINGS, the offer at TURN, its "
             "contributor at turn.end, nothing at turn.begin")
    else:
        failures.append(f"  ✗ late add                   bare={was_bare} landed={landed}")

    # --- and nothing but its own ----------------------------------------------------------
    present = _surface(meta)
    added = {key: present[key] - absent[key] for key in absent}
    if (added["files"] and all("steering" in one for one in added["files"])
            and added["catalogue"] and added["settings"]
            and not added["records"]):
        held("adding it puts its surface there", f"{len(added['files'])} files, "
             f"{len(added['catalogue'])} catalogue lines, {len(added['laws'])} laws, "
             f"{len(added['settings'])} settings, 0 record -- records are born at the first call")
    else:
        failures.append(f"  ✗ the added surface          {[(k, len(v)) for k, v in added.items()]}")

    # --- its words in the standing orders -------------------------------------------------
    section = _section(meta)
    if section and all(section in one for one in _marbles(meta)):
        held("the standing orders carry its section", "both marbles hold the body of system/SYSTEM.COMMON.md, "
             "compared with the vendored file")
    else:
        failures.append(f"  ✗ the section                {[section in one for one in _marbles(meta)]}")

    # --- the ledger: swept, then served once at the boot ----------------------------------
    keeper = S.keeper_module(meta)
    with _clock(NOW - timedelta(days=16)):
        keeper.add(meta, "un-pas-oublie", "un travail laisse seize jours", [], None)
    with _clock(NOW - timedelta(days=2)):
        keeper.add(meta, "un-pas-recent", "un travail touche avant-hier", [], None)
    record = keeper.load(meta)
    old = next(sid for sid, one in record["steps"].items() if one["name"] == "un-pas-oublie")
    young = next(sid for sid, one in record["steps"].items() if one["name"] == "un-pas-recent")
    with _clock(NOW):
        booted = _boot(env)
        ledger = dict(booted.payloads).get("steering-ledger", "") if booted is not None else ""
        archived = keeper.load(meta)["steps"][old]["archived"]
        if young in ledger and old not in ledger and archived:
            held("the boot sweeps then serves the ledger", "the first block carries `steering-ledger` with the "
                 "step touched two days ago; the one untouched for sixteen days is archived and absent")
        else:
            failures.append(f"  ✗ ledger at boot              archived={archived} {ledger[:160]!r}")
        later = _close(env) + [env.conductor("t").submit("the operator's next message")] + _close(env)
    if not [block for block in later if block is not None and "steering-ledger" in dict(block.payloads)]:
        held("the next exchange does not serve it again", "the blocks after the boot carry no `steering-ledger`")
    else:
        failures.append("  ✗ ledger re-served            a later block carries the ledger again")

    # --- the steps are the instance's data: an upgrade leaves them alone ------------------
    spool = meta / ".sys" / "records" / "steps.json"
    written = spool.read_bytes()
    pins_before = dict(instance.read(meta)["packages"])
    install.upgrade(env.member)
    kept = spool.read_bytes() == written
    install.doctor(env.member)
    steady = (dict(instance.read(meta)["packages"]) == pins_before
              and spool.read_bytes() == written and "pp-steering" in _offers(meta))
    if kept and steady:
        held("upgrade and doctor leave the steps alone",
             "the bundle re-materializes and the repair runs at constant pins; steps.json stands byte for byte")
    else:
        failures.append(f"  ✗ upgrade and doctor         kept={kept} steady={steady}")

    # --- switched off, its section leaves the standing orders -----------------------------
    _switch(env, "off")
    _boot(env)
    gone_off = not any(section in one for one in _marbles(meta))
    _switch(env, "on")
    _boot(env)
    back_on = all(section in one for one in _marbles(meta))
    if gone_off and back_on:
        held("switched off, its section leaves", "the boot after `package.steering: off` recompiles both marbles "
             "without it; switched on, it comes back")
    else:
        failures.append(f"  ✗ switch                     off={gone_off} on={back_on}")

    # --- remove gives back what the add put, never the data --------------------------------
    install.remove_package(env.member, "steering")
    after = env.read("SETTINGS.md")
    gone = ("pp-steering" not in _offers(meta) and not [name for name in instance.attached(meta, "turn.end")
                                                         if name not in before[2]]
            and not [one for one in instance.vendored(meta) if one.name.startswith("steering@")])
    left = _surface(meta)
    given_back = {key: present[key] - left[key] for key in absent}
    exact = (given_back["files"] == added["files"] and given_back["laws"] == added["laws"]
             and given_back["catalogue"] == added["catalogue"])
    unowned = "# ---- unowned ----" in after and "steering_step_budget:" in after
    if gone and exact and unowned and spool.read_bytes() == written:
        held("remove takes the surface, never the data",
             "offer, contributor and bundle leave -- the files, catalogue lines and laws the add put, exactly; "
             "the keys ride on as unowned and steps.json is untouched")
    else:
        failures.append(f"  ✗ remove                     gone={gone} unowned={unowned} "
                        f"back={[(k, len(v)) for k, v in given_back.items()]} "
                        f"records={spool.read_bytes() == written}")

    # --- and the socket falls silent again --------------------------------------------------
    _boot(env)
    blocks, pending, steps = [], env.conductor("t").submit(""), 0
    while pending is not None and steps < 6:
        steps += 1
        blocks.append(pending.document)
        if pending.wait:
            break
        pending = env.conductor("t").submit("")
    if "NEXT" not in blocks and "pp-steering" not in _offers(meta):
        held("the absent package costs nothing", "no block at the socket, no offer")
    else:
        failures.append(f"  ✗ absence                    blocks={blocks}")
    return 0
