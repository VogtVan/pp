"""Scenario `steering-package` -- the package comes and goes on an instance that conducts:
- the kit alone carries no file, no catalogue line and no setting of steering
- a LATE add lands its keys, its offer and its attach on an instance already running, and
  nothing but its declared surface: every file it adds is its own, no record before a call
- the threads are the INSTANCE's data: an upgrade re-materializes the bundle and leaves the
  records byte for byte, and a doctor repairs at constant pins
- remove gives back exactly what the add put -- files, catalogue, laws, offer, attach --
  leaves the keys unowned and the records untouched, and the socket falls silent again
"""
from __future__ import annotations

from pathlib import Path

from tests.harness import support
from conductor import compiling, install, instance, reading

S = support(__file__, "steering")


def _offers(meta) -> set:
    """-> what TURN offers here: the composed tools, overlays applied."""
    document = reading.read(instance.resolve(meta, "TURN.md"))
    return {one.name for one in compiling.effective(meta, document)[1]}


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


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("cycle")                 # the kit alone: no steering anywhere
    meta = env.made
    conductor = env.conductor("t")
    conductor.start(conductor.boot("BOOT.md"))   # the instance has conducted before the add
    before = (env.read("SETTINGS.md"), _offers(meta), instance.attached(meta, "turn.end"))
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
    landed = ("steering_step_budget: 100" in settings and "steering_name_max: 60" in settings
              and "pp-steering" in _offers(meta) and "THREADS.md" in instance.attached(meta, "turn.end")
              and not list(instance.attached(meta, "turn.begin")) + list(instance.mounting(meta, "turn.begin")))
    was_bare = ("steering_" not in before[0] and "pp-steering" not in before[1]
                and "THREADS.md" not in before[2])
    if was_bare and landed:
        held("a late add lands the whole surface",
             "on an instance that already conducts: the two keys at the composed SETTINGS, the offer at TURN, THREADS among turn.end's contributors, nothing at turn.begin")
    else:
        failures.append(f"  ✗ late add                   bare={was_bare} landed={landed}")

    # --- and nothing but its own ----------------------------------------------------------
    present = _surface(meta)
    added = {key: present[key] - absent[key] for key in absent}
    if (added["files"] and all("steering" in one for one in added["files"])
            and added["catalogue"] and added["laws"] and added["settings"]
            and not added["records"]):
        held("adding it puts its surface there", f"{len(added['files'])} files, "
             f"{len(added['catalogue'])} catalogue lines, {len(added['laws'])} laws, "
             f"{len(added['settings'])} settings, 0 record -- records are born at the first call")
    else:
        failures.append(f"  ✗ the added surface          {[(k, len(v)) for k, v in added.items()]}")

    # --- the records are the instance's data: an upgrade leaves them alone ----------------
    S.keeper_module(meta).open_thread(meta, "le-fil-du-cycle", "un-pas-avant-le-cycle | un pas ecrit avant le cycle\n")
    spool = meta / ".sys" / "records" / "threads.json"
    written = spool.read_bytes()
    pins_before = dict(instance.read(meta)["packages"])
    install.upgrade(env.member)
    kept = spool.read_bytes() == written
    install.doctor(env.member)
    steady = (dict(instance.read(meta)["packages"]) == pins_before
              and spool.read_bytes() == written and "pp-steering" in _offers(meta))
    if kept and steady:
        held("upgrade and doctor leave the records alone",
             "the bundle re-materializes and the repair runs at constant pins; threads.json stands byte for byte, the offer with it")
    else:
        failures.append(f"  ✗ upgrade and doctor         kept={kept} steady={steady}")

    # --- remove gives back what the add put, never the data --------------------------------
    install.remove_package(env.member, "steering")
    after = env.read("SETTINGS.md")
    gone = ("pp-steering" not in _offers(meta) and "THREADS.md" not in instance.attached(meta, "turn.end")
            and not [one for one in instance.vendored(meta) if one.name.startswith("steering@")])
    left = _surface(meta)
    given_back = {key: present[key] - left[key] for key in absent}
    exact = (given_back["files"] == added["files"] and given_back["laws"] == added["laws"]
             and given_back["catalogue"] == added["catalogue"])
    unowned = "# ---- unowned ----" in after and "steering_step_budget: 100" in after
    if gone and exact and unowned and spool.read_bytes() == written:
        held("remove takes the surface, never the data",
             "offer, attach and bundle leave -- the files, catalogue lines and laws the add put, exactly; "
             "the keys ride on as unowned and threads.json is untouched -- the instance's own")
    else:
        failures.append(f"  ✗ remove                     gone={gone} unowned={unowned} "
                        f"back={[(k, len(v)) for k, v in given_back.items()]} "
                        f"records={spool.read_bytes() == written}")

    # --- and the socket falls silent again --------------------------------------------------
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))
    blocks, pending, steps = [], env.conductor("t").submit(""), 0
    while pending is not None and steps < 6:
        steps += 1
        blocks.append(pending.document)
        if "FINAL" in (pending.next_call or ""):
            break
        pending = env.conductor("t").submit("")
    if "NEXT" not in blocks and "THREADS" not in blocks and "steering_" not in _offers(meta):
        held("the absent package costs nothing",
             "no block at the socket, no offer, no active path")
    else:
        failures.append(f"  ✗ absence                    blocks={blocks}")
    return 0
