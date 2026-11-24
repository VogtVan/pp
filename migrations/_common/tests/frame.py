"""Scenario `frame` -- the frame every migration plays, on a throwaway house at the source's version:
- (a) a dry run checks and writes nothing: the house's fingerprint unmoved, no backup, no journal
- (b) the check refuses by code, rc 2, nothing written: `house-version`, `source-version`,
  `house-busy`, `space`
- (c) the walk finds the house's instances (the root and a borrowing agent), its plan roots, its teams
- (d) a green migration from another engine: rc 0, the backup listable -- the house's own `.git` left
  out, an agent's kept --, the steps in order, the
  engine mounted again after the upgrade (the gestures read the arriving version), a pp launched
  during the backup or during the gestures refused `maintenance-in-progress` -- the lock held from
  the check, its token written only once the backup stands --, every count equal, the cleanup played --
  a relative path removed from the house's root, a link removed as a link, its target kept
- (e) a gesture that refuses: rc 2, the next gesture not played, no cleanup; the restoring commands
  said, played, and the house's fingerprint back to the one before the migration
- (f) a count that differs: rc 3, no cleanup
- (g) a cleanup that names a path outside the house and one under the house's `.git`: rc 2
  `cleanup-outside` naming both, nothing removed
A demonstration migration is written beside the house and played in its own process, as a user
plays a `migrate.py`; the codes are read by the frame's own refusal line (rule 2).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
from pathlib import Path

from tests.harness import ENGINE_VERSION, INSTANCE, SOURCE
from conductor import install
from conductor.state import lock

MIGRATIONS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(MIGRATIONS))
from _common import house as walked   # noqa: E402 -- `_common` lives beside the migrations
from _common.refusal import code_of, restore_of   # noqa: E402

RECORD = "demo"
RETIRED = "retired.txt"          # what the demonstration's cleanup names, relative to the house
LINKED = "linked"                # a link in the house the cleanup removes -- its target outside stays
SECOND = "written-by-second"     # what a gesture after a refusal would write
OTHER = f"{ENGINE_VERSION}-frame"   # the version a house's engine is rewritten to, to migrate from it
ORDER = ("check", "lock", "backup", "upgrade", "gesture", "counts", "cleanup", "doctor", "migrated")

DEMO = """import json, os, subprocess, sys
sys.path.insert(0, {migrations!r})
from _common import Refused, run

FROM = os.environ.get("DEMO_FROM", {version!r})
TO = os.environ.get("DEMO_TO", {version!r})
MODE = os.environ.get("DEMO_MODE", "green")
PROBE = os.environ.get("DEMO_PROBE")
ARCHIVED = os.environ.get("DEMO_ARCHIVED")


def launched(house_root):
    environ = {{key: value for key, value in os.environ.items() if not key.startswith("PP_")}}
    return subprocess.run([sys.executable, os.path.join(house_root, ".pp", ".sys", "engine", "pp.py"), "version"],
                          cwd=house_root, capture_output=True, text=True, env=environ, stdin=subprocess.DEVNULL)


if ARCHIVED:                                  # what stands while the backup is written
    import _common.backup as kept
    archiving = kept.archive

    def probing(root, target):
        done = launched(root)
        with open(ARCHIVED, "w", encoding="utf-8") as handle:
            json.dump({{"rc": done.returncode, "said": done.stderr,
                       "lock": open(os.environ["DEMO_LOCK"], encoding="utf-8").read()}}, handle)
        return archiving(root, target)
    kept.archive = probing


def counted(house, engine):
    rows = []
    for meta in house.instances:
        store = engine.store.of(meta)
        before = store.count({record!r})
        if MODE == "unequal":
            store.append({record!r}, {{"n": 0}})
        rows.append((meta, {record!r}, before, store.count({record!r})))
    return rows


def probed(house, engine):
    if PROBE:
        done = launched(house.root)
        with open(PROBE, "w", encoding="utf-8") as handle:
            json.dump({{"version": engine.VERSION, "rc": done.returncode, "said": done.stderr}}, handle)
    return []


def refusing(house, engine):
    if MODE == "refuse":
        raise Refused("demo-refused", "the demonstration refuses")
    return []


def second(house, engine):
    (house.root / {second!r}).write_text("written", encoding="utf-8")
    return []


GESTURES = [("count", counted), ("probe", probed), ("refuse", refusing), ("second", second)]


def cleanup(house):
    if MODE == "outside":
        return [{retired!r}, house.root.parent / "elsewhere", ".git/HEAD"]
    return [{retired!r}, house.root / {linked!r}]


sys.exit(run(sys.argv[1:], FROM, TO, GESTURES, cleanup))
"""


def tree(top: Path, *ignored: Path) -> dict[str, str]:
    """-> every path under `top` with the digest of its content -- but the `ignored` paths."""
    return {path.relative_to(top).as_posix(): (hashlib.sha256(path.read_bytes()).hexdigest()
                                               if path.is_file() and not path.is_symlink() else "")
            for path in sorted(top.rglob("*")) if path not in ignored}


def fingerprint(top: Path, *ignored: Path) -> str:
    """-> one digest of a tree: every path under `top`, every content -- but the `ignored` paths."""
    return hashlib.sha256(json.dumps(tree(top, *ignored)).encode()).hexdigest()


def house(bench, name: str):
    """-> a throwaway house at the source's version: the plan package pinned, a borrowing agent,
    a plan root, a team with its plans, a record filled, what the cleanup retires -- a file and a
    link whose target stands outside the house."""
    env = bench.env(name, packages=("plan",))
    install.install(env.engine, env.root / "agents" / "a1" / INSTANCE, [], slug="a1", borrow=True)
    (env.made / "plans").mkdir(exist_ok=True)
    (env.root / "teams" / "t1" / "plans").mkdir(parents=True)
    (env.root / "teams" / "t1" / "TEAM.md").write_text("# t1\n", encoding="utf-8")
    env.filled(RECORD, 3)
    for repository in (env.root, env.root / "agents" / "a1"):         # the house's .git, an agent's
        (repository / ".git").mkdir()
        (repository / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (env.root / RETIRED).write_text("retired", encoding="utf-8")
    target = bench.temp() / "target"
    target.write_text("kept", encoding="utf-8")
    (env.root / LINKED).symlink_to(target)
    script = bench.temp() / "migrate.py"
    script.write_text(DEMO.format(migrations=str(MIGRATIONS), version=ENGINE_VERSION, record=RECORD,
                                  second=SECOND, retired=RETIRED, linked=LINKED), encoding="utf-8")
    return env, script, target


def migrate(script: Path, root: Path, *extra: str, **demo: str) -> subprocess.CompletedProcess:
    environ = {**os.environ, **{f"DEMO_{key.upper()}": value for key, value in demo.items()}}
    return subprocess.run([sys.executable, str(script), str(root), "--from", str(SOURCE), *extra],
                          capture_output=True, text=True, env=environ, cwd=script.parent,
                          stdin=subprocess.DEVNULL)


def beside(root: Path, suffix: str) -> list[Path]:
    return sorted(root.parent.glob(f"{root.name}.pre-*{suffix}"))


def journal(root: Path) -> list[dict]:
    logs = beside(root, ".log")
    return [json.loads(line) for line in logs[0].read_text(encoding="utf-8").splitlines()] if logs else []


def steps(entries: list[dict]) -> list[str]:
    return [entry["step"] for entry in entries]


def failing(bench, label: str, done: subprocess.CompletedProcess, more: str = "") -> None:
    bench.failures.append(f"  ✗ {label:<28}rc {done.returncode} code {code_of(done.stderr)!r} {more} "
                          f"-- {done.stderr.strip()[-400:]}")


def scenario(bench) -> int:
    if bench.on_stand_in():
        bench.failures.append(f"  ✗ {'area':<28}on the stand-in")
    else:
        bench.held("area", f"{bench.area} on the product's kit and packages")

    env, script, _ = house(bench, "house")
    root = env.root

    # (a) the dry run
    before = fingerprint(root.parent)
    done = migrate(script, root, "--dry-run")
    if done.returncode == 0 and fingerprint(root.parent) == before and not beside(root, ""):
        bench.held("dry-run", "rc 0, nothing written, no backup, no journal")
    else:
        failing(bench, "dry-run", done)

    # (b) the check refuses by code, nothing written
    for code, demo in (("house-version", {"from": "0.0.0"}), ("source-version", {"to": "0.0.0"})):
        before = fingerprint(root.parent)
        done = migrate(script, root, **demo)
        if done.returncode == 2 and code_of(done.stderr) == code and fingerprint(root.parent) == before:
            bench.held(code, "rc 2, nothing written")
        else:
            failing(bench, code, done)
    lease = lock.try_(lock.maintenance_of(env.made), shared=True)        # a pp living in the house
    try:
        before = fingerprint(root.parent)
        done = migrate(script, root)
        if done.returncode == 2 and code_of(done.stderr) == "house-busy" and fingerprint(root.parent) == before:
            bench.held("house-busy", "rc 2, nothing written")
        else:
            failing(bench, "house-busy", done)
    finally:
        lock.release(lease)
    if os.geteuid() == 0:                     # root writes through any mode: chmod denies it nothing
        print(f"  - {'space':<32}skipped: the bench runs as root, a parent without write proves nothing")
    else:
        before = fingerprint(root.parent)
        root.parent.chmod(0o555)                                          # nowhere to write the backup
        try:
            done = migrate(script, root)
        finally:
            root.parent.chmod(0o755)
        if done.returncode == 2 and code_of(done.stderr) == "space" and fingerprint(root.parent) == before:
            bench.held("space", "rc 2, nothing written")
        else:
            failing(bench, "space", done)

    # (c) the walk
    found = walked.read(root)
    wanted = {"instances": [env.made, root / "agents" / "a1" / INSTANCE],
              "plans": [env.made / "plans", root / "teams" / "t1" / "plans"],
              "teams": [root / "teams" / "t1"]}
    got = {"instances": found.instances, "plans": found.plans, "teams": found.teams}
    if got == wanted and found.version == ENGINE_VERSION:
        bench.held("walk", "2 instances, 2 plan roots, 1 team, the house's version")
    else:
        bench.failures.append(f"  ✗ {'walk':<28}{got} != {wanted}")

    # (d) a green migration, from an engine that says another version
    env, script, target = house(bench, "green")
    root = env.root
    said = env.made / ".sys" / "engine" / "conductor" / "core" / "version.py"
    said.write_text(re.sub(r'(?m)^VERSION = ".*"$', f'VERSION = "{OTHER}"', said.read_text(encoding="utf-8")),
                    encoding="utf-8")
    probe, archived = bench.temp() / "probe.json", bench.temp() / "archived.json"
    held = lock.maintenance_of(env.made)
    standing = held.read_text(encoding="utf-8") if held.is_file() else ""
    done = migrate(script, root, **{"from": OTHER, "probe": str(probe), "archived": str(archived),
                                    "lock": str(held)})
    entries = journal(root)
    order = steps(entries)
    archive = beside(root, ".tar.gz")
    listed = tarfile.open(archive[0]).getnames() if archive else []
    counts = [entry for entry in entries if entry["step"] == "counts"]
    seen = json.loads(probe.read_text(encoding="utf-8")) if probe.is_file() else {}
    if (done.returncode == 0 and f"{root.name}/{INSTANCE}/.sys/instance.yaml" in listed
            and f"{root.name}/agents/a1/.git/HEAD" in listed
            and not [one for one in listed if one.startswith(f"{root.name}/.git")]
            and list(dict.fromkeys(one for one in order if one in ORDER)) == list(ORDER)
            and counts and counts[0]["equal"] and (root / SECOND).exists()):
        bench.held("green", "rc 0, backup without the house's .git, an agent's kept, the steps in order, counts equal")
    else:
        failing(bench, "green", done, f"steps {order}")
    if walked.read(root).version == ENGINE_VERSION and seen.get("version") == ENGINE_VERSION:
        bench.held("mounted-again", f"{OTHER} -> {ENGINE_VERSION}, the gestures on the arriving engine")
    else:
        bench.failures.append(f"  ✗ {'mounted-again':<28}house {walked.read(root).version} gestures {seen.get('version')}")
    if seen.get("rc") and "maintenance-in-progress" in seen.get("said", ""):
        bench.held("maintenance-in-progress", "a pp launched during the gestures refused")
    else:
        bench.failures.append(f"  ✗ {'maintenance-in-progress':<28}{seen}")
    during = json.loads(archived.read_text(encoding="utf-8")) if archived.is_file() else {}
    if during.get("rc") and "maintenance-in-progress" in during.get("said", "") and during.get("lock") == standing:
        bench.held("held-while-archived", "a pp launched during the backup refused, the token not yet written")
    else:
        bench.failures.append(f"  ✗ {'held-while-archived':<28}{during}")
    if not (root / RETIRED).exists() and not (root / LINKED).is_symlink() and target.is_file():
        bench.held("cleanup", "a relative path and a link removed, the link's target kept")
    else:
        bench.failures.append(f"  ✗ {'cleanup':<28}retired {(root / RETIRED).exists()} "
                              f"link {(root / LINKED).is_symlink()} target {target.is_file()}")

    # (e) a gesture that refuses, then the way back played
    env, script, _ = house(bench, "refused")
    root = env.root
    held = lock.maintenance_of(env.made)      # created with its folder by the check when no pp ever
    before = tree(root, held, held.parent)    # ran: in the backup
    done = migrate(script, root, mode="refuse")
    archive = beside(root, ".tar.gz")
    order = steps(journal(root))
    if (done.returncode == 2 and code_of(done.stderr) == "demo-refused" and not (root / SECOND).exists()
            and (root / RETIRED).exists() and archive and str(archive[0]) in done.stderr
            and "cleanup" not in order):
        bench.held("gesture-refused", "rc 2, the rest not played, no cleanup, the backup named")
    else:
        failing(bench, "gesture-refused", done, f"steps {order}")
    command = restore_of(done.stderr)
    back = subprocess.run(["sh", "-c", command or "false"], capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    after = tree(root, held, held.parent)
    if back.returncode == 0 and after == before and held.is_file():
        bench.held("restored", "the commands said, played: the house as it was before")
    else:
        moved = sorted(one for one in set(before) | set(after) if before.get(one) != after.get(one))
        bench.failures.append(f"  ✗ {'restored':<28}rc {back.returncode} {back.stderr.strip()[-200:]} moved {moved[:8]}")

    # (f) a count that differs
    env, script, _ = house(bench, "unequal")
    root = env.root
    done = migrate(script, root, mode="unequal")
    counts = [entry for entry in journal(root) if entry["step"] == "counts"]
    if (done.returncode == 3 and counts and not counts[0]["equal"] and (root / RETIRED).exists()
            and beside(root, ".tar.gz") and str(beside(root, ".tar.gz")[0]) in done.stderr):
        bench.held("count-unequal", "rc 3, no cleanup, the backup named")
    else:
        failing(bench, "count-unequal", done)

    # (g) a cleanup outside the house, and one under the house's .git
    env, script, _ = house(bench, "outside")
    root = env.root
    done = migrate(script, root, mode="outside")
    named = [entry.get("detail", "") for entry in journal(root) if entry["step"] == "refused"]
    if (done.returncode == 2 and code_of(done.stderr) == "cleanup-outside" and (root / RETIRED).exists()
            and (root / ".git" / "HEAD").is_file() and named
            and str(root.parent / "elsewhere") in named[0] and str(root / ".git" / "HEAD") in named[0]):
        bench.held("cleanup-outside", "rc 2, outside the house and under its .git both refused, nothing removed")
    else:
        failing(bench, "cleanup-outside", done)
    return 0
