"""Scenario `upgrade-and-doctor` -- the standing instance kept current: versions, upgrade, doctor, receipts:
- one version: the engine constant, pyproject and a fresh instance's record agree
- doctor repairs the console byte-stable and keeps the standing run; upgrade on a current
  instance touches nothing; upgrade moves the pins and renews the standing runs, each slot
  a renewal mark and a `renewed` event naming the move; a drifted engine copy moves like a
  pin; doctor keeps a bundle the source outran, and sync refuses it `package-missing`
- the build receipts: every compiled artifact carries its engine and inputs; doctor twice
  moves nothing; a wrong engine, a missing receipt or a moved input refuses the boot
  `artifact-stale`; moved catalog inputs recompile at the boot, a dead format refused
  `reference-unknown`; a drifted card latches `card-drift` and the verifier names it
- an engine of an older version hands the upgrade's compile over to the copied engine
"""
from __future__ import annotations

import json

from conductor import VERSION, Conductor, Refusal, compiling, discovery, install, instance, persistence, render
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, cli, kept_document, load_script, reaches, session_of

PAST = "0.1.0-alpha.0"                 # an engine version older than any the source holds


def _renewals(slot) -> list[dict]:
    """-> the `renewed` events of the trace the run at `slot` writes to."""
    name = persistence.trace_of(slot)
    trace = slot.parent / name if name else None
    if trace is None or not trace.is_file():
        return []
    events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [event for event in events if event.get("kind") == "renewed"]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    engine = bench.engine()
    product = install.product_root(engine)

    # --- one version: constant, pyproject, the instance's record ---------------------------
    made = bench.env("standing").made
    vendored = made / ".sys" / "engine" / "pp.py"
    member = discovery.instance_member(vendored)
    checkout = install.product_root(PRODUCT_ENGINE)
    pyproject = (checkout / "pyproject.toml").read_text(encoding="utf-8")
    if (instance.read(made).get("engine") == VERSION
            and f'version = "{VERSION}"' in pyproject
            and install.source_version(checkout) == VERSION):
        held("one version, one truth", "the constant, pyproject and the fresh instance's "
             "record all say the same thing")
    else:
        failures.append(f"  ✗ version record            {instance.read(made).get('engine')!r}")

    # --- doctor at constant pins: the console repaired, the run standing ------------------
    conductor = Conductor(member, vendored)
    conductor.start(conductor.boot("BOOT.md"))
    standing = persistence.slots(made)
    sh = made.parent / "pp"
    sh_text = sh.read_text(encoding="utf-8")
    sh.write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
    told = install.doctor(member)
    told_again = install.doctor(member)
    if (sh.read_text(encoding="utf-8") == sh_text
            and any(str(sh) in one for one in told)
            and not any(str(sh) in one for one in told_again)
            and persistence.slots(made) == standing and standing):
        held("doctor repairs the console", "an edit is overwritten byte-stable; "
             "constant pins keep the standing run")
    else:
        failures.append(f"  ✗ doctor                    {told} / {told_again}")

    # --- upgrade: a statement when current, a move that renews the runs otherwise ---------
    if install.upgrade(member) == [] and persistence.slots(made) == standing:
        held("upgrade current is a statement", "nothing moved, nothing touched -- the run stands")
    else:
        failures.append("  ✗ upgrade no-op             touched a current instance")
    kit = instance.pins(made)["kit"]
    downgraded = instance.read(made)
    downgraded["packages"] = {**instance.pins(made), "kit": "0.0.1-past"}
    instance.write(made, downgraded)
    moved = install.upgrade(member)
    marks = [persistence.renewed(one) for one in standing]
    events = [event for one in standing for event in _renewals(one)]
    move = {"from": {"kit": "0.0.1-past"}, "to": {"kit": kit}}
    if (moved and instance.pins(made)["kit"] == kit
            and persistence.slots(made) == standing
            and all(mark is not None and mark[persistence.RENEWED]["from"] == move["from"]
                    and mark[persistence.RENEWED]["to"] == move["to"] for mark in marks)
            and len(events) == len(standing)
            and all({"from": event.get("from"), "to": event.get("to")} == move for event in events)
            and (made / ".sys" / "vendor" / f"kit@{kit}").is_dir()):
        held("upgrade moves the pins", "source versions land, re-materialized; "
             "the renewed runs are counted, each slot a renewal mark")
    else:
        failures.append(f"  ✗ upgrade                   {moved} {marks} {events}")

    # --- a drifted engine copy moves like a pin -------------------------------------------
    leaf = made / ".sys" / "engine" / "conductor" / "core" / "version.py"
    leaf.write_text(leaf.read_text(encoding="utf-8").replace(VERSION, PAST), encoding="utf-8")
    stale = instance.read(made)
    stale["engine"] = PAST
    instance.write(made, stale)
    engine_moved = install.upgrade(member)
    if (any(one.startswith(f"engine {PAST} -> ") for one in engine_moved)
            and VERSION in leaf.read_text(encoding="utf-8")
            and instance.read(made).get("engine") == VERSION):
        held("upgrade moves the engine too", "a drifted copy is a move like any pin -- "
             "told, refreshed, recorded")
    else:
        failures.append(f"  ✗ engine move               {engine_moved!r}")

    # --- doctor keeps what the source outran; sync refuses it -----------------------------
    current = instance.pins(made)["kit"]
    (made / ".sys" / "vendor" / f"kit@{current}").rename(made / ".sys" / "vendor" / "kit@0.0.9-past")
    outrun = instance.read(made)
    outrun["packages"] = {**instance.pins(made), "kit": "0.0.9-past"}
    instance.write(made, outrun)
    try:
        repaired = install.doctor(member)
    except Refusal as refusal:
        repaired = [refusal.code]
    try:
        install.sync(member)
        refused = ""
    except Refusal as refusal:
        refused = refusal.code
    if (any("kit@0.0.9-past" in one and current in one for one in repaired)
            and instance.pins(made)["kit"] == "0.0.9-past"
            and (made / ".sys" / "vendor" / "kit@0.0.9-past").is_dir()
            and refused == "package-missing"):
        held("doctor keeps what the source outran", "the repair stays useful -- the stale "
             "bundle stands, the way forward is named; the refusal guides the same way")
    else:
        failures.append(f"  ✗ doctor partial            {repaired!r} / {refused!r}")

    # --- the build receipts: every artifact carries its engine and inputs -----------------
    receipted = bench.env("receipted").made
    receipted_member = discovery.instance_member(receipted / ".sys" / "engine" / "pp.py")

    def fresh() -> Conductor:
        return Conductor(receipted_member, receipted / ".sys" / "engine" / "pp.py", "t")

    receipts = compiling.receipts(receipted)
    first = fresh().start(fresh().boot("BOOT.md"))
    fresh().forget()
    if (all((receipts.get(name) or {}).get("engine") == VERSION for name in ("system.md", "tools.md"))
            and receipts["system.md"]["inputs"] == compiling.receipt_inputs(receipted)
            and first is not None and "recall drift" not in render(first)):
        held("every build leaves a receipt", "system and tools each carry engine + "
             "inputs; a receipted boot passes, no drift said")
    else:
        failures.append(f"  ✗ build receipts              {receipts!r}")

    load_script(product / "adapters" / "claude" / "wire.py").wire(receipted.parent, receipted)
    install.doctor(receipted_member)
    artifact = (receipted / ".sys" / "system.md").read_bytes()
    twice = install.doctor(receipted_member)
    if (not any("refreshed" in one or "candidate" in one for one in twice)
            and (receipted / ".sys" / "system.md").read_bytes() == artifact
            and not any("STALE" in one or "DRIFTED" in one for one in twice)
            and any(one.startswith("receipt system.md: current") for one in twice)
            and any(one.startswith("card .claude") for one in twice)):
        held("doctor twice is silence", "no projection moves, the artifacts hold their "
             "bytes, and the verifier names every receipt and card current")
    else:
        failures.append(f"  ✗ doctor x2                   {twice!r}")

    receipts_path = receipted / ".sys" / "receipts.yaml"
    receipts_text = receipts_path.read_text(encoding="utf-8")
    receipts_path.write_text(receipts_text.replace(VERSION, PAST), encoding="utf-8")
    expect("artifact-stale", lambda: fresh().start(fresh().boot("BOOT.md")))
    receipts_path.unlink()
    expect("artifact-stale", lambda: fresh().start(fresh().boot("BOOT.md")))
    receipts_path.write_text(receipts_text, encoding="utf-8")
    late = next((receipted / ".sys" / "vendor").glob("kit@*")) / "system" / "SYSTEM.COMMON.md"
    late_kept = late.read_bytes()
    late.write_bytes(late_kept + b"\nLate law.\n")
    expect("artifact-stale", lambda: fresh().start(fresh().boot("BOOT.md")))
    late.write_bytes(late_kept)
    back = fresh().start(fresh().boot("BOOT.md"))
    fresh().forget()
    if back is not None:
        held("a stale artifact refuses the boot", "wrong engine, no receipt and moved "
             "inputs each refuse aloud and name the repair; receipts restored, the boot passes")
    else:
        failures.append("  ✗ artifact-stale recovery     the restored receipt did not boot")

    # --- the catalog's inputs moved: the boot recompiles ----------------------------------
    (receipted / "FORMATS.md").write_text(
        "---\nname: FORMATS\nkind: doc\nformats: |\n  motto  inline  one line, the house motto\n---\n",
        encoding="utf-8")
    catalog_boot = fresh().start(fresh().boot("BOOT.md"))
    fresh().forget()
    catalog = (receipted / ".sys" / "tools.md").read_text(encoding="utf-8")
    catalog_receipt = (compiling.receipts(receipted).get("tools.md") or {}).get("catalog")
    if (catalog_boot is not None and "`motto`" in catalog
            and catalog_receipt == compiling.catalog_inputs(receipted)):
        held("a moved catalog recompiles at the boot", "a format declared after the build is "
             "in the catalog the boot serves; the receipt follows")
    else:
        failures.append(f"  ✗ catalog receipt             motto={'`motto`' in catalog} "
                        f"receipt={catalog_receipt is not None}")
    (receipted / "procs" / "DEADFMT.md").write_text(
        "---\nname: DEADFMT\nkind: proc\noutput: nowhere\nproc: |\n  INFER\n---\nbody\n",
        encoding="utf-8")
    expect("reference-unknown", lambda: fresh().start(fresh().boot("BOOT.md")))
    (receipted / "procs" / "DEADFMT.md").unlink()

    # --- a drifted card: the boot latches the signal, the verifier names it ---------------
    card = receipted.parent / ".claude" / "skills" / "pp" / "SKILL.md"
    card.write_text(card.read_text(encoding="utf-8") + "\nOLD LAW\n", encoding="utf-8")
    fresh().start(fresh().boot("BOOT.md"))
    latched = persistence.signals_of(session_of(receipted))
    fresh().forget()
    verified = install.verify(receipted_member)
    if (any(one.get("signal") == "card-drift" for one in latched)
            and any("DRIFTED" in one for one in verified)):
        held("a drifted card is said", "the boot latches card-drift -- an old card "
             "cannot conduct in silence; the verifier names the drifted card")
    else:
        failures.append(f"  ✗ card drift                  {latched!r} / {verified!r}")

    # --- an older engine hands the compile over to the copied one -------------------------
    crossed_made = bench.env("crossed").made
    old = crossed_made / ".sys" / "engine"
    (old / "conductor" / "core" / "version.py").write_text(f'VERSION = "{PAST}"\n', encoding="utf-8")
    compiler = old / "conductor" / "packaging" / "compiling.py"
    compiler.write_text(compiler.read_text(encoding="utf-8")
                        .replace("if card.is_file():", "if False:"), encoding="utf-8")
    old_record = instance.read(crossed_made)
    old_record["engine"] = PAST
    instance.write(crossed_made, old_record)
    (crossed_made / ".sys" / "system.md").write_text("old envelope alone\n", encoding="utf-8")
    (crossed_made / ".sys" / "receipts.yaml").unlink()
    crossed = cli(old / "pp.py", "upgrade")
    marble = (crossed_made / ".sys" / "system.md").read_text(encoding="utf-8")
    receipt = compiling.receipts(crossed_made).get("system.md") or {}
    if (crossed.returncode == 0
            and f"engine {PAST} -> " in crossed.stdout
            and reaches(marble, body_of(kept_document(SOURCE / "engine", "PP")))
            and receipt.get("engine") == VERSION):
        held("the old engine hands the compile over", "upgrade run BY alpha.0 copies the "
             "current engine then delegates its tail: the marble carries the canon and "
             "the receipt names the NEW engine -- pin N+1 is compiled by code N+1")
    else:
        failures.append(f"  ✗ cross-version upgrade       rc={crossed.returncode} "
                        f"receipt={receipt!r} {crossed.stderr[-120:]!r}")
    return 0
