"""Scenario `upgrade-and-doctor` -- the standing instance kept current: versions, upgrade, doctor, receipts:
- one version: the engine constant, pyproject and a fresh instance's record agree
- doctor repairs the console byte-stable and keeps the standing run; upgrade on a current
  instance touches nothing; upgrade moves the pins and renews the standing runs, each slot
  a renewal mark and a `renewed` event naming the move; a drifted engine copy moves like a
  pin; doctor keeps a bundle the source outran, and sync refuses it `package-missing`
- the build receipts: every compiled artifact carries its engine and inputs; doctor twice
  moves nothing -- no line says a rewrite, the engine, the bundles and the artifacts keep their
  files; a wrong engine, a missing receipt or a moved input refuses the boot
  `artifact-stale`; moved catalog inputs leave `output.md` stale at the doctor's word and
  recompile it at the boot, a dead format refused `reference-unknown`; a drifted card latches `card-drift` and the verifier names it
- an engine of an older version hands the WHOLE upgrade over to the copied engine: the source's
  engine is copied before anything of the target is judged, so a composition the old engine
  cannot read (a socket it does not know) moves in one call; `doctor` hands its repair over the
  same way, before it judges anything; `add` and `remove` at an engine behind the source refuse
  `engine-behind`, nothing written
- `upgrade --from <checkout>` names the instance's source anew, then upgrades from it
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


def _files(meta) -> dict:
    """-> (inode, mtime) of the machine's copies and compiled artifacts: a file rewritten,
    even to the same bytes, moves its inode."""
    sys_ = meta / ".sys"
    held = [sys_ / "engine" / "pp.py", sys_ / "engine" / "conductor" / "core" / "version.py",
            *sorted((sys_ / "vendor").glob("*/package.yaml")),
            *(sys_ / name for name in ("tools.md", "system.md", "system.common.md", "receipts.yaml"))]
    return {str(path): (path.stat().st_ino, path.stat().st_mtime_ns) for path in held if path.is_file()}


def _aged(made):
    """Turns the engine copy of `made` into an OLDER engine: its version `PAST`, its card
    unread, and no implicit socket -- the greeter's `boot.initialize` contributor is a socket it
    cannot resolve, a composition of the source it cannot judge. -> the old engine's root."""
    old = made / ".sys" / "engine"
    (old / "conductor" / "core" / "version.py").write_text(f'VERSION = "{PAST}"\n', encoding="utf-8")
    compiler = old / "conductor" / "packaging" / "compiling.py"
    compiler.write_text(compiler.read_text(encoding="utf-8")
                        .replace("if card.is_file():", "if False:"), encoding="utf-8")
    sockets = old / "conductor" / "packaging" / "topology.py"
    sockets.write_text(sockets.read_text(encoding="utf-8").replace(
        "owners.setdefault(contributions.address(name, contributions.initialize_of(path), base), name)",
        "pass"), encoding="utf-8")
    record = instance.read(made)
    record["engine"] = PAST
    instance.write(made, record)
    return old


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

    # --- upgrade --from: the source named anew --------------------------------------------
    recorded = instance.read(made)
    kept_source = str(recorded.get("source", ""))
    recorded["source"] = str(bench.temp() / "moved-away")
    instance.write(made, recorded)
    sourced = cli(vendored, "upgrade", "--from", kept_source, cwd=made.parent)
    if sourced.returncode == 0 and str(instance.read(made).get("source", "")) == kept_source:
        held("upgrade --from names the source", "the manifest pointed nowhere; `upgrade --from <checkout>` "
             "writes it, then upgrades from it")
    else:
        failures.append(f"  ✗ upgrade --from              rc={sourced.returncode} {sourced.stderr[-200:]!r} "
                        f"source={instance.read(made).get('source')!r}")
        recorded["source"] = kept_source
        instance.write(made, recorded)

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
    standing_files = _files(receipted)
    twice = install.doctor(receipted_member)
    if (not any("refreshed" in one or "candidate" in one or one.endswith("rewritten") for one in twice)
            and _files(receipted) == standing_files and len(standing_files) >= 7
            and (receipted / ".sys" / "system.md").read_bytes() == artifact
            and not any("STALE" in one or "DRIFTED" in one for one in twice)
            and any(one.startswith("receipt system.md: current") for one in twice)
            and any(one.startswith("card .claude") for one in twice)):
        held("doctor twice is silence", f"no projection moves, nothing said rewritten, "
             f"{len(standing_files)} files of the engine, the bundles and the artifacts keep their "
             "inode and mtime, and the verifier names every receipt and card current")
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
    stale_said = install.verify(receipted_member)
    catalog_boot = fresh().start(fresh().boot("BOOT.md"))
    fresh().forget()
    forms = (receipted / ".sys" / compiling.OUTPUT).read_text(encoding="utf-8")
    forms_receipt = (compiling.receipts(receipted).get(compiling.OUTPUT) or {}).get("catalog")
    if (catalog_boot is not None and "`motto`" in forms
            and "`motto`" in render(catalog_boot)
            and any(one.startswith(f"receipt {compiling.OUTPUT}: STALE") for one in stale_said)
            and forms_receipt == compiling.catalog_inputs(receipted)):
        held("a moved format recompiles at the boot", "a format declared after the build leaves "
             "output.md stale at the doctor's word; the boot recompiles it and serves it, the "
             "receipt follows")
    else:
        failures.append(f"  ✗ formats receipt             motto={'`motto`' in forms} "
                        f"said={[one for one in stale_said if compiling.OUTPUT in one]} "
                        f"receipt={forms_receipt is not None}")
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

    # --- an older engine hands the WHOLE upgrade over to the copied one -------------------
    crossed_made = bench.env("crossed", packages=("greeter",)).made
    old = _aged(crossed_made)
    (crossed_made / ".sys" / "system.md").write_text("old envelope alone\n", encoding="utf-8")
    (crossed_made / ".sys" / "receipts.yaml").unlink()
    crossed = cli(old / "pp.py", "upgrade")
    marble = (crossed_made / ".sys" / "system.md").read_text(encoding="utf-8")
    receipt = compiling.receipts(crossed_made).get("system.md") or {}
    crossed_again = cli(old / "pp.py", "upgrade")
    if (crossed.returncode == 0
            and f"engine {PAST} -> " in crossed.stdout
            and reaches(marble, body_of(kept_document(SOURCE / "engine", "PP")))
            and receipt.get("engine") == VERSION
            and instance.read(crossed_made).get("engine") == VERSION
            and VERSION in (old / "conductor" / "core" / "version.py").read_text(encoding="utf-8")
            and crossed_again.returncode == 0 and "engine" not in crossed_again.stdout):
        held("the old engine hands the whole upgrade over", "upgrade run BY alpha.0 copies the "
             "current engine before it judges anything, then delegates the upgrade to it: the "
             "composition the old engine could not read moves, the move is told, the marble carries "
             "the canon and the receipt names the NEW engine; played again, nothing moves")
    else:
        failures.append(f"  ✗ cross-version upgrade       rc={crossed.returncode} "
                        f"receipt={receipt!r} {crossed.stderr[-160:]!r} "
                        f"again={crossed_again.returncode} {crossed_again.stdout[-80:]!r}")

    # --- doctor hands its repair over the same way; add and remove refuse behind the source -
    behind_made = bench.env("behind", packages=("greeter",)).made
    behind = _aged(behind_made)
    repaired = cli(behind / "pp.py", "doctor")
    if (repaired.returncode == 0
            and VERSION in (behind / "conductor" / "core" / "version.py").read_text(encoding="utf-8")
            and instance.read(behind_made).get("engine") == VERSION
            and (compiling.receipts(behind_made).get("system.md") or {}).get("engine") == VERSION):
        held("the old engine hands the repair over", "doctor run BY alpha.0 copies the current engine "
             "before it judges the composition it could not read, then delegates: the record and the "
             "receipt name the NEW engine")
    else:
        failures.append(f"  ✗ cross-version doctor         rc={repaired.returncode} "
                        f"{repaired.stderr[-200:]!r} {repaired.stdout[-120:]!r}")
    behind = _aged(behind_made)
    pinned = dict(instance.pins(behind_made))
    added = cli(behind / "pp.py", "add", "wit")
    removed = cli(behind / "pp.py", "remove", "greeter")
    if (added.returncode == 2 and "engine-behind" in added.stderr
            and removed.returncode == 2 and "engine-behind" in removed.stderr
            and instance.pins(behind_made) == pinned):
        held("add and remove refuse behind the source", "an engine older than the source's refuses "
             "`engine-behind` and names the upgrade -- the pins untouched")
    else:
        failures.append(f"  ✗ engine-behind               add rc={added.returncode} {added.stderr[-160:]!r} "
                        f"remove rc={removed.returncode} {removed.stderr[-160:]!r}")
    return 0
