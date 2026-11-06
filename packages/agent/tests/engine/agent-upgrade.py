"""Scenario `agent-upgrade` -- 6 case(s) (batch la-mise-a-niveau-de-la-maison, 2026-10-01; batch
la-machine-en-remontant, 2026-10-03):
- the house's upgrade reaches its agents: a throwaway house with two agents born under it (they
  borrow its machine), installed from a copy of the product whose kit version then moves;
  `./pp upgrade` at the house answers 0 and the three play the new kit -- the agents still
  carry no machine and pin nothing
- nothing to do touches nothing: replayed, 0, the three manifests byte-identical
- a pp process alive at an agent holds the whole upgrade: the bench holds the machine shared
  through ag1, a new move -> 2, `maintenance-busy`, nothing moved
- released, the same verb moves the house and both agents and renews ag1's run
- the house's `doctor` descends too: it restates both agents, at the same versions, and their
  runs stand
- a run a wake-up opened is renewed by the upgrade and resumed under the mark: the resume's first prompt
  is the boot under the message, the run's second response kept
"""
from __future__ import annotations

import json
import re
import sys

from conductor import install, instance, persistence
from conductor.state import lock
from tests.harness import INSTANCE, bench_key, cli, support

A = support(__file__, "agent")


def _bumped(manifest) -> str:
    """The kit's version at the source copy, raised by one on its last number -> the new version."""
    text = manifest.read_text(encoding="utf-8")
    found = re.search(r"^version: (\S+)$", text, re.M)
    assert found, text[:200]
    head, last = found.group(1).rsplit(".", 1)
    new = f"{head}.{int(last) + 1}"
    manifest.write_text(text.replace(f"version: {found.group(1)}", f"version: {new}", 1), encoding="utf-8")
    return new


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    engine = bench.source_with("kit-witness")          # a copy of the product: its versions may move
    source = engine.parent.parent
    ws = bench.temp() / "house"
    house = install.install(engine, ws / INSTANCE, ["agent"])
    console = house / ".sys" / "engine" / "pp.py"
    kit_manifest = source / "bases" / "kit" / "package.yaml"

    def call(*args: str):
        return cli(console, *args, cwd=ws)

    agents = {name: ws / "agents" / name / INSTANCE for name in ("ag1", "ag2")}
    for name, meta in agents.items():
        install.install(console, meta, [], slug=name, doors=False, borrow=True)
    every = [("house", house), *agents.items()]

    def pins() -> dict[str, str]:
        return {label: instance.pins(meta)["kit"] for label, meta in every}

    def manifests() -> dict[str, bytes]:
        return {label: (meta / instance.MANIFEST).read_bytes() for label, meta in every}

    def borrowing() -> bool:
        return all(not (meta / ".sys" / "engine").exists() and "packages" not in instance.read(meta)
                   for meta in agents.values())

    before = pins()["house"]
    target = _bumped(kit_manifest)

    # --- the house's upgrade reaches its agents ----------------------------------------------------
    moved = call("upgrade")
    if moved.returncode == 0 and before != target and set(pins().values()) == {target} and borrowing():
        held("the house's upgrade reaches its agents", f"kit {before} -> {target}; agents/ag1 and agents/ag2 "
             "restated and playing it, still without a machine nor pins of their own")
    else:
        failures.append(f"  ✗ one verb                    rc={moved.returncode} {moved.stdout[-300:]!r} "
                        f"{moved.stderr.strip()[-200:]!r} pins={pins()} borrowing={borrowing()}")

    # --- nothing to do: said, nothing touched ------------------------------------------------------
    stood = manifests()
    again = call("upgrade")
    if again.returncode == 0 and manifests() == stood:
        held("already current, the manifests byte-identical", "replayed: rc 0, nothing moved")
    else:
        failures.append(f"  ✗ already current             rc={again.returncode} {again.stdout[-300:]!r} "
                        f"same={manifests() == stood}")

    # --- a pp process alive at ag1 holds the whole upgrade -----------------------------------------
    target2 = _bumped(kit_manifest)
    ag1 = agents["ag1"]
    opened = cli(console, "--instance", str(ag1), "-new", cwd=ag1.parent)
    key = bench_key(ag1) if opened.returncode == 0 else ""
    with lock.serving(ag1):                        # the bench, a pp process of the agent
        cut = call("upgrade")
    if (opened.returncode == 0 and cut.returncode == 2 and "maintenance-busy" in cut.stderr
            and set(pins().values()) == {target}):
        held("a pp process at an agent holds the whole upgrade", f"maintenance-busy; "
             f"the house and both agents still at {target}")
    else:
        failures.append(f"  ✗ wake held                   open={opened.returncode} rc={cut.returncode} "
                        f"{cut.stderr.strip()[-300:]!r} pins={pins()}")
    caught = call("upgrade")
    if (caught.returncode == 0 and set(pins().values()) == {target2}
            and persistence.renewed(persistence.slot_of(ag1, key)) is not None):
        held("released, the upgrade moves all three", f"kit {target} -> {target2} on the house and its agents; "
             f"ag1's run {key} renewed")
    else:
        failures.append(f"  ✗ caught up                   rc={caught.returncode} {caught.stdout[-300:]!r} "
                        f"{caught.stderr.strip()[-200:]!r} pins={pins()}")

    # --- the house's doctor descends: the agents restated, their runs standing --------------------------
    kept = cli(console, "--instance", str(ag1), "-new", cwd=ag1.parent)
    key2 = bench_key(ag1) if kept.returncode == 0 else ""
    repaired = call("doctor")
    if (repaired.returncode == 0 and "pp: agents/ag1 restated" in repaired.stdout
            and "pp: agents/ag2 restated" in repaired.stdout and persistence.slot_of(ag1, key2).is_file()
            and set(pins().values()) == {target2}):
        held("the house's doctor descends", f"agents/ag1 and agents/ag2 restated at {target2}; ag1's run {key2} stands")
    else:
        failures.append(f"  ✗ doctor descends             rc={repaired.returncode} {repaired.stdout[-300:]!r} "
                        f"{repaired.stderr.strip()[-200:]!r}")

    # --- a run a wake-up opened is renewed by the upgrade and resumed under the mark ----------------------
    witness = bench.temp() / "witness.py"
    witness.write_text(A.WITNESS, encoding="utf-8")
    out = bench.temp() / "wprompt"
    harness = f"{sys.executable} {witness} {console} {ag1} play {out}"
    woken = call("agent", "run", "agents/ag1", "--message", "before the upgrade", *A.harnessing(harness))
    key3 = next((persistence.run_id_of(one) for one in persistence.slots(ag1)
                 if persistence.run_id_of(one) not in (key, key2)), "")
    target4 = _bumped(kit_manifest)
    moved_again = call("upgrade")
    renewed = persistence.renewed(persistence.slot_of(ag1, key3)) if key3 else None
    resumed = call("agent", "run", "agents/ag1", "--run", key3, "--message", "after the upgrade", *A.harnessing(harness))
    trace_path = persistence.trace_of(persistence.slot_of(ag1, key3)) if key3 else None
    kinds = ([json.loads(line).get("kind") for line in (ag1 / persistence.DIRECTORY / trace_path).read_text(encoding="utf-8").splitlines()
              if line.strip()] if trace_path else [])
    resumed_prompt = out.with_name(out.name + ".prompt.w-1.2")       # the session's second launch: the resume's first
    first_prompt = resumed_prompt.read_text(encoding="utf-8") if resumed_prompt.is_file() else ""
    kept = [one for one in A.lines(house / ".sys" / "records" / "responses.jsonl") if one.get("run") == key3]
    if (woken.returncode == 0 and key3 and moved_again.returncode == 0 and renewed is not None
            and resumed.returncode == 0 and [one.get("index") for one in kept] == [1, 2]
            and "reopened" in kinds and kinds.index("reopened") > kinds.index("new")
            and first_prompt.startswith(f"{A.HEAD}\nafter the upgrade\n\n▌ pp · run {key3}")
            and set(pins().values()) == {target4}):
        held("a renewed run is resumed under the mark", f"ag1's run {key3}, opened by a wake-up, renewed by kit "
             f"{target2} -> {target4}; `agent run --run {key3}` reopened it by the marked call: the boot in the "
             "first prompt under the message, exchange 2, parked")
    else:
        failures.append(f"  ✗ renewed run resumed         woken={woken.returncode} key={key3!r} upgrade={moved_again.returncode} "
                        f"renewed={renewed is not None} resumed={resumed.returncode} kinds={kinds[-6:]} "
                        f"prompt={first_prompt[:60]!r} {woken.stderr.strip()[-200:]!r} {resumed.stderr.strip()[-300:]!r}")
    return 0

