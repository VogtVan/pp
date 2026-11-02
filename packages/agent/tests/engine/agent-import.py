"""Scenario `agent-import` -- 4 case(s) (batch l-import, plan wsl-house, 2026-11-01):
- an instance that carries its own machine, wired for claude, a run opened in it, is imported
  as the agent `ag1` of a house: listed, no machine, a borrower's manifest keeping its birth date,
  its records and its own files byte-identical, its run renewed and reopened under its key; the
  workspace keeps only what pp did not write intact, each file left named
- the imported agent plays: `-new` opens a run on the house's machine, the house's upgrade
  restates it
- each refusal leaves the house and the workspace as they were: agent-exists, agent-path-invalid,
  instance-missing, import-borrowed, import-version, import-packages, maintenance-busy
- two filesystems refuse `import-cross-device`, nothing written
"""
from __future__ import annotations

import hashlib

from conductor import adapters, install, instance, persistence, settings
from conductor.core.errors import Refusal
from conductor.state import lock
from tests.harness import INSTANCE, bench_key, cli

OWN = ("MEMBER.md", "FORMATS.md")


def _digest(root) -> dict[str, str]:
    """-> {relative path: sha256} of every file under `root` -- the lock files and the holders'
    markers left out: a call takes them and lets them go, nothing of the trees."""
    found = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not path.name.endswith(".lock") and lock.MARKERS not in relative.parts:
            found[str(relative)] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def _kept(meta) -> dict[str, str]:
    """-> the sha256 of what an import carries as it is: the records and the instance's own files."""
    found = {f"records/{key}": value for key, value in _digest(meta / instance.RECORDS).items()}
    found.update({name: hashlib.sha256((meta / name).read_bytes()).hexdigest() for name in OWN})
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    engine = bench.engine()
    top = bench.temp()
    ws = top / "house"
    house = install.install(engine, ws / INSTANCE, ["agent", "continuity"])
    console = house / ".sys" / "engine" / "pp.py"

    def member(name: str, packages: list[str]):
        place = top / name
        return place, install.install(engine, place / INSTANCE, packages)

    def call(*args: str):
        return cli(console, *args, cwd=ws)

    # --- the import --------------------------------------------------------------------------------
    m1_ws, m1 = member("m1", ["continuity"])
    adapters.load("claude", m1).wire(m1_ws, m1)
    edited = m1_ws / "claude-pp.cmd"
    edited.write_text(edited.read_text(encoding="utf-8") + "rem mine\n", encoding="utf-8")
    opened = cli(m1 / ".sys" / "engine" / "pp.py", "-new", cwd=m1_ws)
    key = bench_key(m1) if opened.returncode == 0 else ""
    born = instance.read(m1).get("installed")
    settings.write(m1, "continuity_recall_days", "3")       # a value of the member's own SETTINGS
    before = _kept(m1)
    done = call("agent", "import", "ag1", "--from", str(m1_ws))
    ag1 = ws / "ag1" / INSTANCE
    listed = call("agent", "list", "--json")
    declared = instance.read(ag1) if instance.is_instance(ag1) else {}
    gone = [name for name in (INSTANCE, "pp", "pp.cmd", "claude-pp", ".claude/skills/pp/SKILL.md")
            if (m1_ws / name).exists()]
    stays = [name for name in ("CLAUDE.md", ".claude/settings.json", "claude-pp.cmd") if not (m1_ws / name).exists()]
    machine = [part for part in ("engine", "vendor", "projections.yaml") if (ag1 / ".sys" / part).exists()]
    named = all(name in done.stdout for name in ("CLAUDE.md", "settings.json", "claude-pp.cmd"))
    renewed = persistence.renewed(persistence.slot_of(ag1, key)) if key else None
    after = _kept(ag1) if ag1.is_dir() else {}
    same = [name for name, digest in before.items() if after.get(name) != digest]
    recall = settings.of(ag1).of_package("continuity_recall_days") if ag1.is_dir() else None
    if (done.returncode == 0 and '"ag1"' in listed.stdout and not machine and not gone and not stays and named
            and declared == {"slug": "ag1", "installed": born, **({"member_seed": instance.read(ag1)["member_seed"]}
                                                                 if "member_seed" in declared else {})}
            and not same and str(recall) == "3" and renewed is not None):
        held("an instance is imported as an agent", f"ag1 listed, no machine, {{slug, installed {born}}}, "
             f"{len(before)} records and own files byte-identical, its SETTINGS value kept, run {key} renewed; the workspace keeps "
             "CLAUDE.md, settings.json and the edited claude-pp.cmd, each named")
    else:
        failures.append(f"  ✗ imported                    rc={done.returncode} {done.stdout[-400:]!r} "
                        f"{done.stderr.strip()[-300:]!r} machine={machine} gone={gone} stays={stays} named={named} "
                        f"declared={declared} changed={same} recall={recall!r} "
                        f"renewed={renewed is not None}")

    # --- the imported agent plays -----------------------------------------------------------------------
    if not ag1.is_dir():
        failures.append("  ✗ plays                       no agent imported")
        return 0
    fresh = cli(console, "--instance", str(ag1), "-new", cwd=ag1.parent)
    resumed = cli(console, "--instance", str(ag1), key, cwd=ag1.parent) if key else None
    upgraded = call("doctor")
    if (fresh.returncode == 0 and resumed is not None and resumed.returncode == 0
            and "ag1 restated" in upgraded.stdout):
        held("the imported agent plays", f"-new opens a run on the house's machine; {key} reopens under its key; "
             "the house's doctor restates ag1")
    else:
        failures.append(f"  ✗ plays                       new={fresh.returncode} {fresh.stderr.strip()[-200:]!r} "
                        f"resumed={resumed.returncode if resumed else None} doctor={upgraded.returncode} "
                        f"{upgraded.stdout[-300:]!r}")

    # --- each refusal leaves both trees as they were ----------------------------------------------------
    m2_ws, m2 = member("m2", ["continuity"])
    m3_ws, m3 = member("m3", ["continuity"])
    stamped = instance.read(m3)
    instance.write(m3, {**stamped, "engine": "0.0.0-older"})
    m4_ws, m4 = member("m4", ["steering"])
    bare = top / "bare"
    bare.mkdir()
    refused = []
    cases = [("agent-exists", ("ag1", m2_ws), None),
             ("agent-path-invalid", ("Bad/..", m2_ws), None),
             ("instance-missing", ("ag2", bare), None),
             ("import-borrowed", ("ag2", ws / "ag1"), None),
             ("import-version", ("ag2", m3_ws), None),
             ("import-packages", ("ag2", m4_ws), None),
             ("maintenance-busy", ("ag2", m2_ws), m2)]
    for code, (path, source), busy in cases:
        trees = (_digest(ws), _digest(source))
        if busy is not None:
            with lock.serving(busy):
                played = call("agent", "import", path, "--from", str(source))
        else:
            played = call("agent", "import", path, "--from", str(source))
        if not (played.returncode == 2 and code in played.stderr and (_digest(ws), _digest(source)) == trees):
            refused.append(f"{code}: rc={played.returncode} {played.stderr.strip()[-200:]!r} "
                           f"same={(_digest(ws), _digest(source)) == trees}")
    if not refused:
        held("each refusal leaves both trees as they were", ", ".join(code for code, _, _ in cases))
    else:
        failures.append("  ✗ refusals                    " + " | ".join(refused))

    # --- two filesystems --------------------------------------------------------------------------------
    trees = (_digest(ws), _digest(m2_ws))
    devices = iter(range(1, 1000))
    standing = install._device
    install._device = lambda path: next(devices)       # every path on a filesystem of its own
    try:
        install.imported(m2, ws / "ag3" / INSTANCE, "ag3")
        crossed = "nothing refused"
    except Refusal as refusal:
        crossed = str(refusal)
    finally:
        install._device = standing
    if crossed.startswith("import-cross-device") and (_digest(ws), _digest(m2_ws)) == trees:
        held("two filesystems refuse", "import-cross-device, nothing written")
    else:
        failures.append(f"  ✗ cross-device                {crossed[:200]!r} same={(_digest(ws), _digest(m2_ws)) == trees}")
    return 0
