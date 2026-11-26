"""The verbs of an agent's life: add, import, name, prune, purge, remove."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from acts.material import unpushed
from acts.mounts import held_by_guardian
from acts.settings import profiled, capped
from faces.life import (born_line, imported_lines, lock_left_line, named_line, pruned_line, purge_lines,
                        purge_object, purged_run, removal_object, removed_lines, would_remove_line)
from model.run import Naming
from model.words import NAMES, WORKDIRS, USAGE, PROFILES, HOUSE, PURGED
from rules.refusals import cause_of, unrefused
from store.clock import now
from store.houses import house, engine_of, refusal_line
from store.locks import locks, launch_of, birth_lock_of
from store.records import record, lines_of, append, name_of, flow_of, workdir_of, of_run, rewritten_without
from store.refusal import refuse
from store.settings import call_wait
from store.traces import run_known, engine_purge_of
from verbs.asked import agent_of, json_flag, keyed, named_agent

NAME_CHARS = 60                                        # a run's name: a title a user types, never a key


def add(rest: list[str]) -> int:
    """`agent add <path> [--type member|chat]`: gives birth to the agent at `<path>` by the
    engine's own install -- an instance that BORROWS the house's machine, with no harness wired, the seed
    of an interactive instance, its slug the path's last segment --, then writes the PROFILE
    `--type` names (`profiled`). Refuses before writing: `agent-path-invalid`, `agent-exists`,
    `type-unsupported` (a type `PROFILES` does not carry), and a path under a subtree that
    carries another machine. The birth plays under the house's
    BIRTH lock for that path (`born-busy` past `call_lock_wait`), the one a caller's start takes:
    one path is born once, whoever asks."""
    root, conductor = house()
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    path, rest = rest[0], rest[1:]
    if rest and (rest[0] != "--type" or len(rest) != 2):
        refuse(USAGE)
    meta = agent_of(root, conductor, path)
    profile = rest[1] if rest else None
    if profile is not None and profile not in PROFILES:
        refuse(f"type-unsupported -- `--type {profile}`: the types are {' and '.join(PROFILES)}.")
    if conductor.instance.is_instance(meta):
        refuse(f"agent-exists -- an instance stands at `{path}` already ({meta}).")
    if any(one.exists() and not one.is_dir() for one in [meta.parent, *meta.parent.parents]
           if one.is_relative_to(root.parent)):
        refuse(f"agent-path-invalid -- `{path}`: a file stands on that path under {root.parent}.")
    instance = conductor.instance
    try:
        machine, borrowed = instance.machine_of(root), instance.machine_of(meta)
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    if borrowed != machine:
        refuse(f"agent-path-invalid -- `{path}` stands under {borrowed.parent}, which carries a machine of its own: "
               "an agent borrows the house's machine.")
    lock = locks(conductor)
    gate = birth_lock_of(root, conductor, path)
    gate.parent.mkdir(parents=True, exist_ok=True)
    lease = lock.acquire(gate, wait=call_wait(conductor, root))
    if lease is None:
        refuse(f"born-busy -- `{path}` is being born by another call that has not finished within call_lock_wait: "
               "replay once it has.")
    try:
        if instance.is_instance(meta):
            refuse(f"agent-exists -- an instance stands at `{path}` already ({meta}).")
        try:
            conductor.install.install(instance.engine_root(root) / "pp.py", meta, [], slug=path.rsplit("/", 1)[-1],
                                      borrow=True)
        except conductor.Refusal as refusal:
            refuse(str(refusal))
    finally:
        lock.release(lease)
    said = capped(conductor, meta)
    print(born_line(path, str(meta), str(machine), said,
                    profiled(conductor, meta, profile) if profile is not None else None))
    return 0


def import_(rest: list[str]) -> int:
    """`agent import <path> --from <workspace>`: makes the instance of `<workspace>`, which carries its
    own machine, the agent at `<path>` by the engine's import (`install.imported`) -- judged as `add`
    judges a birth, under the same BIRTH lock --, then sets its cap (`capped`); its profile is its own
    and stays. Says the import, then one line per file of the workspace taken out or left."""
    root, conductor = house()
    if len(rest) != 3 or rest[0].startswith("--") or rest[1] != "--from":
        refuse(USAGE)
    path, workspace = rest[0], Path(rest[2]).expanduser().resolve()
    meta = agent_of(root, conductor, path)
    if conductor.instance.is_instance(meta):
        refuse(f"agent-exists -- an instance stands at `{path}` already ({meta}).")
    if any(one.exists() and not one.is_dir() for one in [meta.parent, *meta.parent.parents]
           if one.is_relative_to(root.parent)):
        refuse(f"agent-path-invalid -- `{path}`: a file stands on that path under {root.parent}.")
    lock = locks(conductor)
    gate = birth_lock_of(root, conductor, path)
    gate.parent.mkdir(parents=True, exist_ok=True)
    lease = lock.acquire(gate, wait=call_wait(conductor, root))
    if lease is None:
        refuse(f"born-busy -- `{path}` is being born by another call that has not finished within call_lock_wait: "
               "replay once it has.")
    try:
        if conductor.instance.is_instance(meta):
            refuse(f"agent-exists -- an instance stands at `{path}` already ({meta}).")
        try:
            told = conductor.install.imported(workspace / root.name, meta, path.rsplit("/", 1)[-1])
        except conductor.Refusal as refusal:
            refuse(str(refusal))
    finally:
        lock.release(lease)
    for line in imported_lines(path, str(workspace), str(meta), str(conductor.instance.machine_of(meta)),
                               capped(conductor, meta), told):
        print(line)
    return 0


def prune(rest: list[str]) -> int:
    """`agent prune <path> <key> [--force]`: removes the run's clone -- `run-busy` while a
    wake-up plays the run, `workdir-unpushed` over commits the repository has not received
    (`--force` removes them), `workdir-unknown` without a material on record; `pruned` written."""
    root, conductor = house()
    name, key, rest = keyed(rest)
    force = rest == ["--force"]
    if rest and not force:
        refuse(USAGE)
    name, meta, _ = named_agent(root, conductor, [name])
    entry = workdir_of(root, name, key)
    if entry is None or entry.state == "pruned":
        refuse(f"workdir-unknown -- run {key} of {name} has no material on record.")
    lock = locks(conductor)
    if lock.held(launch_of(meta, key)):
        refuse(f"run-busy -- a wake-up plays run {key}: prune its material once it is over.")
    clone = meta.parent / entry.path
    ahead = unpushed(entry, clone) if not force else 0
    if ahead:
        refuse(f"workdir-unpushed -- {ahead} commit(s) of {entry.branch} were not sent to {entry.repo}: "
               "`--force` removes them.")
    shutil.rmtree(clone, ignore_errors=True)
    append(record(root, WORKDIRS), entry.pruned(now()).json())
    print(pruned_line(name, key, entry.path))
    return 0


def purge(rest: list[str]) -> int:
    """`agent purge <path> (<key> … | --before <YYYY-MM-DD>) [--yes] [--force] [--json]`: removes for good
    what the house keeps of runs of the agent -- their lines in the six records, their clone -- then has
    the engine remove what the agent keeps of them, `./pp -purge` played on the agent's instance: each
    record by its writer. Without `--yes` it says what it would remove and writes nothing. All or nothing:
    a run whose wake lock is held refuses `run-busy`, a clone with unsent commits `workdir-unpushed`
    (`--force` removes them), the engine's `call-busy` is relayed -- and nothing is removed anywhere."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    confirmed, force = "--yes" in rest, "--force" in rest
    rest = [one for one in rest if one not in ("--yes", "--force")]
    engine_purge = engine_purge_of(conductor)
    before = None
    if "--before" in rest:
        at = rest.index("--before")
        value = rest[at + 1] if at + 1 < len(rest) else ""
        try:
            before = datetime.strptime(value, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            refuse(f"purge-invalid -- `--before {value}`: a date is written YYYY-MM-DD.")
        del rest[at:at + 2]
    if (before is None) == (not rest) or any(one.startswith("-") for one in rest):
        refuse(USAGE)
    lines = {record_name: lines_of(record(root, record_name)) for record_name in PURGED}
    recorded = {one.get("run") for found in lines.values() for one in found
                if one.get("agent") == name or one.get("to") == name}
    persistence = conductor.persistence
    if before is None:
        keys = list(dict.fromkeys(rest))
        unknown = [key for key in keys if key not in recorded and not engine_purge.files_of(meta, key)
                   and not flow_of(root, name, key).is_file()]
        if unknown:
            refuse(f"run-unknown -- `{' '.join(unknown)}`: no run of {name} wears that key; nothing removed.")
    else:
        candidates = sorted((recorded | set(engine_purge.known(meta))) - {None})
        if name == HOUSE:                                  # the house's own: its runs of the post alone
            candidates = [key for key in candidates
                          if key in recorded or persistence.slot_of(meta, key).is_file()]
        keys = []
        for key in candidates:
            ats = [one.get("at") for found in lines.values() for one in found if of_run(one, name, key) and one.get("at")]
            last = max((datetime.fromisoformat(at) for at in ats), default=None)
            written = engine_purge.last_write(engine_purge.files_of(meta, key))
            newest = max((one for one in (last, written) if one is not None), default=None)
            if newest is not None and newest < before:
                keys.append(key)
    held_by_guardian(conductor, root, name, keys)         # all or nothing: the family's guardian first
    lock = locks(conductor)
    leases = []
    try:
        for key in keys:                                   # all or nothing: every wake lock first
            wake = launch_of(meta, key)
            if not confirmed or not wake.exists():
                taken = lock.held(wake)
            else:
                lease = lock.try_(wake)
                taken = lease is None
                if lease is not None:
                    leases.append(lease)
            if taken:
                refuse(f"run-busy -- a wake-up or a conversation holds run {key} of {name}: nothing removed; "
                       "purge it once it is over.")
        # by key: the lines of the run, its clone, its flow, the files and the bytes the engine says
        counted, materials, flows, engine_said = {}, {}, {}, {}
        for key in keys:
            entry = workdir_of(root, name, key)
            clone = meta.parent / entry.path if entry is not None and entry.state != "pruned" else None
            if confirmed and clone is not None and not force:
                ahead = unpushed(entry, clone)
                if ahead:
                    refuse(f"workdir-unpushed -- {ahead} commit(s) of {entry.branch} were not sent to "
                           f"{entry.repo}: `--force` removes them; nothing removed.")
            kept_flow = flow_of(root, name, key)
            counted[key] = {record_name: sum(1 for one in found if of_run(one, name, key))
                            for record_name, found in lines.items()}
            materials[key] = entry.path if clone is not None and clone.is_dir() else None
            flows[key] = kept_flow.stat().st_size if kept_flow.is_file() else None
        held_keys = [key for key in keys if engine_purge.files_of(meta, key)]
        if held_keys:                                      # the agent first: its engine removes, or nothing does
            played = subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta),
                                     "-purge", *held_keys, "-json"] + (["--yes"] if confirmed else []),
                                    stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=root.parent)
            if played.returncode != 0:
                refuse(f"{unrefused(refusal_line(), cause_of(refusal_line(), played.stderr)).strip()} -- the engine of {name} "
                       "refused; nothing removed.")
            told = json.loads(played.stdout)
            for one in told.get("runs") or []:
                engine_said[one.get("key")] = (list(one.get("files") or []), int(one.get("bytes") or 0))
        if confirmed:
            for record_name in PURGED:
                rewritten_without(record(root, record_name), name, set(keys))
            for key in keys:
                if materials[key]:
                    shutil.rmtree(meta.parent / materials[key], ignore_errors=True)
                flow_of(root, name, key).unlink(missing_ok=True)
    finally:
        for lease in leases:
            lock.release(lease)
    if confirmed:                                          # the wake locks' own files, once released: the engine
        for lease in leases:                               # leaves a file this process holds open
            try:
                lease.path.unlink(missing_ok=True)
            except PermissionError:
                print(lock_left_line(lease.path.name), file=sys.stderr)
    runs = [purged_run(key, counted[key], *engine_said.get(key, ([], 0)), materials[key], flows[key]) for key in keys]
    if as_json:
        print(json.dumps(purge_object(not confirmed, name, runs), ensure_ascii=False))
        return 0
    for line in purge_lines(confirmed, name, runs):
        print(line)
    return 0


def remove(rest: list[str]) -> int:
    """`agent remove <path> [--yes] [--json]`: takes the agent OUT of the house -- the inverse of `add`. Judged before
    any write: `agent-unknown`, the house itself (`agent-path-invalid`), `run-busy` when a wake-up or a conversation
    holds a run of the agent, and every refusal of `purge` on its runs (`run-held`, `workdir-unpushed` -- `--force`
    is not offered here: prune or purge that run first). Under `--yes`: every run of the agent purged (the path of
    `purge`), then what pp wrote in its directory taken out -- the consoles and each wired harness's files, when
    nobody changed them (`install.unwired`) --, then its instance whole, then the directory when nothing else
    stands in it; a directory that keeps something of its own (an imported repository, a file the operator wrote,
    a harness's settings) is KEPT and said, `directory-kept`, what stands named -- never an error. Without
    `--yes` it says what it would remove and writes nothing. Under `--json` ONE object `{dry, agent, runs, files,
    left, directory}` -- `files` what is (or would be) taken out, relative to the agent's directory, `left` what
    stands beside, `directory` `removed` or `kept` once played."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    confirmed = "--yes" in rest
    rest = [one for one in rest if one != "--yes"]
    if rest:
        refuse(USAGE)
    if name == HOUSE:
        refuse("agent-path-invalid -- `.` is the house itself: it is not removed by its own hand.")
    workspace = meta.parent
    persistence, lock = conductor.persistence, locks(conductor)
    keys = sorted({persistence.run_id_of(slot) for slot in persistence.slots(meta)}
                  | {one.get("run") for record_name in PURGED for one in lines_of(record(root, record_name))
                     if (one.get("agent") == name or one.get("to") == name) and one.get("run")}
                  | {path.name.removeprefix("session-").split(".", 1)[0]
                     for path in (meta / persistence.DIRECTORY).glob("session-*.wake.lock")})
    for key in keys:
        if lock.held(launch_of(meta, key)):
            refuse(f"run-busy -- a wake-up or a conversation holds run {key} of {name}: nothing removed; "
                   "remove the agent once it is over.")
    owned = {"pp", "pp.cmd", meta.name}
    standing = sorted(one.name for one in workspace.iterdir()) if workspace.is_dir() else []
    files = [one for one in standing if one in owned]
    left = [one for one in standing if one not in owned]
    if not confirmed:
        if as_json:
            print(json.dumps(removal_object(True, name, keys, files, left), ensure_ascii=False))
            return 0
        print(would_remove_line(name, keys, files, left))
        return 0
    if keys:
        played = subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(root), "agent",
                                 "purge", name, *keys, "--yes"], stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, cwd=root.parent, env=dict(os.environ))
        if played.returncode != 0:
            refuse(f"{cause_of(refusal_line(), played.stderr).removeprefix('pp-agent: ').strip()} -- the purge of the runs of {name} "
                   "refused; nothing removed.")
    told = conductor.install.unwired(meta)
    shutil.rmtree(meta, ignore_errors=True)
    removed = [one for one in files if not (workspace / one).exists()]
    left = sorted(one.name for one in workspace.iterdir()) if workspace.is_dir() else []
    directory = "kept"
    if workspace.is_dir() and not left:
        workspace.rmdir()
        directory = "removed"
    if as_json:
        print(json.dumps(removal_object(False, name, keys, removed, left, directory), ensure_ascii=False))
        return 0
    for line in removed_lines(name, keys, removed, left, directory, told):
        print(line)
    return 0


def name_run(rest: list[str]) -> int:
    """`name <path> <key> [<name>]`: the run's name, kept by this script alone at
    `names.jsonl`; without a name, the current one is said."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    if not rest or len(rest) > 2 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    if not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    if len(rest) == 1:
        current = name_of(root, name, key)
        print(named_line(name, key, current))
        return 0
    wanted = rest[1].strip()
    if not wanted or len(wanted) > NAME_CHARS or not wanted.isprintable():   # a line break would split a table's row
        shown = " ".join(rest[1].split())[:40]
        refuse(f"name-invalid -- `{shown}`: a run's name is one line of 1 to {NAME_CHARS} printable characters.")
    append(record(root, NAMES), Naming(at=now(), agent=name, run=key, name=wanted).json())
    print(named_line(name, key, wanted))
    return 0
