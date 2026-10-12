"""Scenario `agent-work` -- 13 case(s) (batch le-materiau-par-run, 2026-10-01; batch le-package-agent,
its rework, 2026-10-03):
- a wake-up with a material: `run ag1 --work <target> --harness <witness work>` clones the target
  under `ag1/work/<key>` on the branch `agent/ag1/<key>`, the witness commits there by
  `git -C` and the skill pushes the branch to the target; `workdirs.jsonl` says `open` then
  `pushed` with one commit, clean; the prompt opens on the material's head
- the clone is made of hard links: a loose object of the target has two names after the clone
- two wake-ups on one target at once (`race`): two branches at the target, its main untouched
- a witness that `cd`s into the material still reaches its console by `PP_CONSOLE`
- `--dry-run --work` shows the head, `PP_WORKDIR`, `PP_CONSOLE` and the git identity, and
  clones nothing
- a run keeps its material: the resume reopens the same clone (the witness's file still there,
  two commits pushed), `--work` on that run refuses `work-standing`
- a push that fails keeps the response: the target made unreadable, `pushed: false` with its
  reason, exit 2
- the clone removed by hand refuses `workdir-missing` before any launch, the wake lock free and
  its mark unchanged
- `agent workdirs ag1` says one line per material: run, branch, commits ahead, clean or dirty,
  pushed or not, the run's state
- `agent prune` refuses `run-busy` under a held wake lock and `workdir-unpushed` over a commit
  not sent, removes the clone under `--force` and writes `pruned`
- a pruned run is never resumed: `workdir-missing`, pruned said, nothing launched, its mark unchanged
- a target that is no repository refuses `work-clone-failed`: no slot, no record line, no wake
  lock file left
- two agents of the same name on one target, `rep1/ag1` and `rep2/ag1`: two branches
  `agent/<path>/<key>` pushed, each commit signed by its path (`rep1.ag1@<slug>`)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

from conductor import install, instance, persistence
from conductor.state import lock
from tests.harness import INSTANCE, PRODUCT_ENGINE, cli, holding, race, support

A = support(__file__, "agent")   # `harnessing`: the witness below writes the grammar of the support's


def launcher(meta, key: str):
    """-> the launcher's file of the run `key` -- the `agent` package's published contract,
    `session-<key>.wake.lock` beside the slot; the engine names none."""
    return persistence.slot_of(meta, key).with_name(f"session-{key}.wake.lock")

# The witness: the one of `agent-home` (its run conducted by the house: it reads the prompt,
# deposits the value a block asks and nothing more), with two modes for the material. `work`
# writes a line under PP_WORKDIR at the first launch of a wake-up -- after checking the path is
# under its current directory, as a confined harness would -- and commits it by `git -C`; `cd`
# does the same, then moves into the material and reaches its console by PP_CONSOLE instead of
# the engine.

WITNESS = r'''import json, os, re, subprocess, sys
from pathlib import Path


engine, meta, mode, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
prompt = sys.stdin.read()                           # the prompt comes on stdin: the house's head, then pp's output
given = os.environ.get("PP_AGENT_SESSION", "")
home = Path(os.getcwd())
workdir, console = os.environ.get("PP_WORKDIR", ""), os.environ.get("PP_CONSOLE", "")
first = "[message from your principal]" in prompt    # the first launch of a wake-up carries the message
Path(out).write_text(prompt, encoding="utf-8")
Path(out + ".env").write_text(json.dumps({"PP_WORKDIR": workdir, "PP_CONSOLE": console,
                                          "GIT_AUTHOR_NAME": os.environ.get("GIT_AUTHOR_NAME", ""),
                                          "GIT_AUTHOR_EMAIL": os.environ.get("GIT_AUTHOR_EMAIL", "")}),
                              encoding="utf-8")
if mode in ("work", "cd") and workdir and first:
    material = (home / workdir).resolve()
    if not material.is_relative_to(home.resolve()):
        sys.stderr.write("witness: the material is outside my directory\n")
        sys.exit(3)
    note = material / "witness.txt"
    with note.open("a", encoding="utf-8") as handle:
        handle.write("a line by the witness\n")
    subprocess.run(["git", "-C", str(material), "add", "witness.txt"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(material), "commit", "-q", "-m", "witness"], check=True, capture_output=True)
if mode == "cd":
    os.chdir(home / workdir)
memory = Path(out + ".memory.json")
sessions = json.loads(memory.read_text(encoding="utf-8")) if memory.is_file() else {}
session = given or f"w-{len(sessions) + 1}"
sessions[session] = {"launches": sessions.get(session, {}).get("launches", 0) + 1}
memory.write_text(json.dumps(sessions), encoding="utf-8")
KEY = re.compile(r"^▌ pp · run ([0-9a-f]{6})", re.M)
PROOF = re.compile(r"^INFER proof \[([^\]]*)\]", re.M)
found = KEY.search(prompt)
key = found.group(1) if found else ""
if key and PROOF.search(prompt):                     # the one call the witness makes: the value asked
    codes = PROOF.search(prompt).group(1).split()
    proof = json.dumps([{"code": c, "evidence": "witness", "verdict": "n/a"} for c in codes])
    command = [console, key, "-"] if mode == "cd" else [sys.executable, engine, "--instance", meta, key, "-"]
    subprocess.run(command, capture_output=True, text=True, input=proof)
print(json.dumps({"result": "witness answer: " + mode, "total_cost_usd": 0.01, "permission_denials": [],
                  "session_id": session}))
'''


def _lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)


def _repo(path: Path) -> Path:
    """A throwaway target repository: one commit on `main`, a README."""
    path.mkdir(parents=True)
    _git("init", "-q", "-b", "main", cwd=path)
    (path / "README.md").write_text("# target\n", encoding="utf-8")
    _git("add", "README.md", cwd=path)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "root", cwd=path)
    return path


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    ws = bench.temp() / "house"
    house = install.install(PRODUCT_ENGINE, ws / INSTANCE, ["agent"])
    engine = house / ".sys" / "engine" / "pp.py"
    env: dict[str, str] = {}
    agent_ws = ws / "ag1"
    agent_meta = agent_ws / INSTANCE
    records = house / ".sys" / "records"
    witness = bench.temp() / "witness.py"
    witness.write_text(WITNESS, encoding="utf-8")
    target = _repo(bench.temp() / "target")
    main_before = _git("rev-parse", "main", cwd=target).stdout.strip()

    def call(*args: str):
        return cli(engine, "--instance", str(house), *args, cwd=ws, env=env)

    def harness(mode: str, out: Path) -> str:
        return f"{sys.executable} {witness} {engine} {agent_meta} {mode} {out}"

    def workdirs() -> list[dict]:
        return _lines(records / "workdirs.jsonl")

    def of_run(key: str) -> list[dict]:
        return [one for one in workdirs() if one.get("run") == key]

    def keys() -> list[str]:
        return [persistence.run_id_of(one) for one in persistence.slots(agent_meta)]

    def branches() -> list[str]:
        return _git("branch", "--list", "agent/*", "--format=%(refname:short)", cwd=target).stdout.split()

    def key_of(played) -> str:
        found = re.search(r"run ([0-9a-f]{6})", played.stderr)
        return found.group(1) if found else ""

    install.install(engine, agent_meta, [], slug="ag1", doors=False, borrow=True)   # born at the path `ag1`

    # --- a wake-up with a material --------------------------------------------------------------
    out = bench.temp() / "a"
    woke = call("agent", "run", "ag1", "--work", str(target), "--message", "feature X",
                *A.harnessing(harness("work", out)))
    key = key_of(woke)
    clone = agent_ws / "work" / key
    prompt = out.read_text(encoding="utf-8") if out.is_file() else ""
    lines = of_run(key)
    ahead = _git("rev-list", "--count", f"main..agent/ag1/{key}", cwd=target).stdout.strip()
    head = (f"[material work/{key} · branch agent/ag1/{key} · from main@{main_before[:7]} · console "
            f"{agent_ws.resolve() / 'pp'} -- reach the material by git -C and relative paths, never cd; "
            "the target's hooks are not in the clone]")
    if (woke.returncode == 0 and key and (clone / "witness.txt").is_file() and f"agent/ag1/{key}" in branches()
            and ahead == "1" and prompt.startswith(head + "\n\n")
            and [one.get("state") for one in lines] == ["open", "pushed"]
            and lines[-1].get("pushed") is True and lines[-1].get("commits") == 1 and lines[-1].get("dirty") is False
            and lines[0].get("repo") == str(target.resolve()) and lines[0].get("branch") == f"agent/ag1/{key}"
            and (agent_ws / "work" / ".gitignore").read_text(encoding="utf-8") == "*\n"):
        held("a wake-up with a material", f"clone at work/{key}, the witness committed by git -C, branch "
             f"agent/ag1/{key} pushed with 1 commit; workdirs: open then pushed; the head opens the prompt")
    else:
        failures.append(f"  ✗ material wake-up            rc={woke.returncode} key={key!r} ahead={ahead!r} "
                        f"lines={lines} prompt={prompt[:200]!r} {woke.stderr.strip()[-300:]!r}")

    # --- the clone is made of hard links -----------------------------------------------------------
    loose = [one for one in (target / ".git" / "objects").rglob("*")
             if one.is_file() and len(one.parent.name) == 2]
    linked = [one for one in loose if os.stat(one).st_nlink >= 2]
    if clone.is_dir() and loose and linked:
        held("the clone is made of hard links", f"{len(linked)} of {len(loose)} loose objects of the target have "
             "two names after the clone")
    else:
        failures.append(f"  ✗ hard links                  loose={len(loose)} linked={len(linked)}")

    # --- two wake-ups on one target at once ----------------------------------------------------------
    outs = [bench.temp() / "c1", bench.temp() / "c2"]
    pair = race(engine, [["--instance", str(house), "agent", "run", "ag1", "--work", str(target),
                          "--message", f"bug {n}", *A.harnessing(harness("work", out))]
                         for n, out in enumerate(outs)], cwd=ws, env=env)
    pair_keys = [key_of(one) for one in pair]
    main_after = _git("rev-parse", "main", cwd=target).stdout.strip()
    if (all(one.returncode == 0 for one in pair) and all(pair_keys) and len(set(pair_keys)) == 2
            and all(f"agent/ag1/{k}" in branches() for k in pair_keys) and main_after == main_before
            and all(_git("rev-list", "--count", f"main..agent/ag1/{k}", cwd=target).stdout.strip() == "1"
                    for k in pair_keys)):
        held("two wake-ups on one target at once", f"runs {pair_keys[0]} and {pair_keys[1]}: two branches at the "
             "target, one commit each, main untouched")
    else:
        failures.append(f"  ✗ race on one target          {[(one.returncode, one.stderr.strip()[-160:]) for one in pair]} "
                        f"keys={pair_keys} main_same={main_after == main_before}")

    # --- a witness that cd's still reaches its console --------------------------------------------------
    out_cd = bench.temp() / "d"
    moved = call("agent", "run", "ag1", "--work", str(target), "--message", "cd me",
                 *A.harnessing(harness("cd", out_cd)))
    key_cd = key_of(moved)
    if moved.returncode == 0 and key_cd and f"agent/ag1/{key_cd}" in branches():
        held("a witness that cd's still reaches its console", f"run {key_cd}: the witness moved into work/{key_cd} "
             "and played its console by PP_CONSOLE to its frontier; its branch pushed")
    else:
        failures.append(f"  ✗ cd witness                  rc={moved.returncode} key={key_cd!r} {moved.stderr.strip()[-300:]!r}")

    # --- a dry run with a material clones nothing ----------------------------------------------------------
    def clones() -> list[str]:
        return sorted(one.name for one in (agent_ws / "work").iterdir()) if (agent_ws / "work").is_dir() else []

    before = (len(workdirs()), clones())
    dry = call("agent", "run", "ag1", "--work", str(target), "--message", "m", "--provider", A.providers(house)[0],
               "--dry-run")
    after = (len(workdirs()), clones())
    if (dry.returncode == 0 and "[material work/" in dry.stdout and "env PP_WORKDIR=work/" in dry.stdout
            and f"env PP_CONSOLE={agent_ws.resolve() / 'pp'}" in dry.stdout and "env GIT_AUTHOR_NAME=ag1" in dry.stdout
            and f"env GIT_AUTHOR_EMAIL=ag1@{instance.read(house).get('slug')}" in dry.stdout and before == after):
        held("a dry run with a material clones nothing", "the head, PP_WORKDIR, PP_CONSOLE and the git identity "
             "said; no clone, no record line")
    else:
        failures.append(f"  ✗ dry run                     rc={dry.returncode} {dry.stdout[-400:]!r} {before} {after}")

    # --- a run keeps its material ----------------------------------------------------------------------------
    again = call("agent", "run", "ag1", "--run", key, "--message", "more", *A.harnessing(harness("work", out)))
    note = (clone / "witness.txt").read_text(encoding="utf-8") if (clone / "witness.txt").is_file() else ""
    last = of_run(key)[-1] if of_run(key) else {}
    standing = call("agent", "run", "ag1", "--run", key, "--work", str(target), "--message", "m",
                    *A.harnessing(harness("work", out)))
    if (again.returncode == 0 and note.count("a line by the witness") == 2 and last.get("commits") == 2
            and last.get("pushed") is True
            and standing.returncode == 2 and "work-standing" in standing.stderr):
        held("a run keeps its material", f"the resume reopened work/{key}: the witness's file carries two lines, "
             "two commits pushed; --work on that run refuses work-standing")
    else:
        failures.append(f"  ✗ resume keeps the material   rc={again.returncode}/{standing.returncode} note={note!r} "
                        f"last={last} {again.stderr.strip()[-200:]!r} {standing.stderr.strip()[-160:]!r}")

    # --- a push that fails keeps the response ------------------------------------------------------------
    mode = (target / ".git").stat().st_mode
    os.chmod(target / ".git", 0)
    try:
        failed = call("agent", "run", "ag1", "--run", key, "--message", "push me", *A.harnessing(harness("work", out)))
    finally:
        os.chmod(target / ".git", stat.S_IMODE(mode))
    last = of_run(key)[-1] if of_run(key) else {}
    kept = [one for one in _lines(records / "responses.jsonl") if one.get("run") == key]
    if (failed.returncode == 2 and "push failed" in failed.stderr and failed.stdout.strip() == "witness answer: work"
            and last.get("pushed") is False and last.get("state") == "unpushed" and last.get("reason")
            and len(kept) == 3):
        held("a push that fails keeps the response", f"the target unreadable: response kept (3 for the run), "
             f"workdirs says pushed: false -- {str(last.get('reason'))[:60]!r}; exit 2")
    else:
        failures.append(f"  ✗ push failed                 rc={failed.returncode} last={last} kept={len(kept)} "
                        f"{failed.stdout[-100:]!r} {failed.stderr.strip()[-200:]!r}")

    # --- the clone removed by hand ---------------------------------------------------------------------------
    shutil.rmtree(clone)
    mark_key = launcher(agent_meta, key).read_bytes() if launcher(agent_meta, key).is_file() else b""
    gone = call("agent", "run", "ag1", "--run", key, "--message", "m", *A.harnessing(harness("work", out)))
    mark_gone = launcher(agent_meta, key).read_bytes() if launcher(agent_meta, key).is_file() else b""
    if (gone.returncode == 2 and "workdir-missing" in gone.stderr and not lock.held(launcher(agent_meta, key))
            and mark_key and mark_gone == mark_key):
        held("a clone gone refuses workdir-missing", f"run {key}: refused before any launch, the wake lock free, "
             "its mark unchanged")
    else:
        failures.append(f"  ✗ workdir missing             rc={gone.returncode} {gone.stderr.strip()[-200:]!r}")

    # --- agent workdirs --------------------------------------------------------------------------------------
    listed = call("agent", "workdirs", "ag1")
    rows = [one for one in listed.stdout.splitlines() if one.startswith("ag1 · run ")]
    k2 = pair_keys[0]
    row = next((one for one in rows if f"run {k2}" in one), "")
    if (listed.returncode == 0 and len(rows) == 4 and f"agent/ag1/{k2}" in row and "1 ahead" in row
            and "clean" in row and "pushed" in row and "parked" in row
            and any(f"run {key}" in one and "gone" in one for one in rows)):
        held("agent workdirs", f"{len(rows)} materials: {row}")
    else:
        failures.append(f"  ✗ workdirs                    rc={listed.returncode} {listed.stdout[-400:]!r}")

    # --- agent prune -----------------------------------------------------------------------------------------
    clone2 = agent_ws / "work" / k2
    with holding(launcher(agent_meta, k2)):
        busy = call("agent", "prune", "ag1", k2)
    kept_busy = clone2.is_dir()
    (clone2 / "more.txt").write_text("more\n", encoding="utf-8")
    _git("add", "more.txt", cwd=clone2)
    _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "unsent", cwd=clone2)
    unpushed = call("agent", "prune", "ag1", k2)
    kept_unpushed = clone2.is_dir()
    forced = call("agent", "prune", "ag1", k2, "--force")
    unknown = call("agent", "prune", "ag1", "ffffff")
    if (busy.returncode == 2 and "run-busy" in busy.stderr and kept_busy
            and unpushed.returncode == 2 and "workdir-unpushed" in unpushed.stderr and kept_unpushed
            and forced.returncode == 0 and not clone2.exists() and of_run(k2)[-1].get("state") == "pruned"
            and unknown.returncode == 2 and "workdir-unknown" in unknown.stderr):
        held("agent prune", f"run {k2}: run-busy under the held wake lock, workdir-unpushed over a commit not sent, "
             "removed under --force and written pruned; ffffff: workdir-unknown")
    else:
        failures.append(f"  ✗ prune                       {busy.returncode}/{unpushed.returncode}/{forced.returncode}/"
                        f"{unknown.returncode} {busy.stderr.strip()[-120:]!r} {unpushed.stderr.strip()[-120:]!r} "
                        f"{forced.stderr.strip()[-120:]!r} {unknown.stderr.strip()[-120:]!r} "
                        f"clone2={clone2.exists()} last={of_run(k2)[-1] if of_run(k2) else None}")

    # --- a pruned run is never resumed without its material ------------------------------------------------
    mark_k2 = launcher(agent_meta, k2).read_bytes() if launcher(agent_meta, k2).is_file() else b""
    counts_k2 = (len(_lines(records / "messages.jsonl")), len(of_run(k2)))
    pruned_again = call("agent", "run", "ag1", "--run", k2, "--message", "after the prune",
                        *A.harnessing(harness("work", out)))
    if (pruned_again.returncode == 2 and "workdir-missing" in pruned_again.stderr and "pruned" in pruned_again.stderr
            and not lock.held(launcher(agent_meta, k2))
            and counts_k2 == (len(_lines(records / "messages.jsonl")), len(of_run(k2)))
            and (launcher(agent_meta, k2).read_bytes() if launcher(agent_meta, k2).is_file() else b"") == mark_k2):
        held("a pruned run is not resumed", f"run {k2}: workdir-missing, pruned said, nothing launched, no record, "
             "the wake lock free and its mark unchanged")
    else:
        failures.append(f"  ✗ pruned resume               rc={pruned_again.returncode} {pruned_again.stderr.strip()[-200:]!r} "
                        f"counts={counts_k2}/{(len(_lines(records / 'messages.jsonl')), len(of_run(k2)))}")

    # --- a target that is no repository ----------------------------------------------------------------------
    nowhere = bench.temp() / "nowhere"
    nowhere.mkdir()
    state = agent_meta / persistence.DIRECTORY
    locks_before = sorted(one.name for one in state.glob("session-*.wake.lock"))
    counts = (len(keys()), len(_lines(records / "messages.jsonl")), len(workdirs()))
    broken = call("agent", "run", "ag1", "--work", str(nowhere), "--message", "m", *A.harnessing(harness("work", out)))
    locks_after = sorted(one.name for one in state.glob("session-*.wake.lock"))
    if (broken.returncode == 2 and "work-clone-failed" in broken.stderr
            and counts == (len(keys()), len(_lines(records / "messages.jsonl")), len(workdirs()))
            and locks_before == locks_after):
        held("a target that is no repository", "work-clone-failed: no slot, no message, no workdirs line, "
             "no wake lock file left")
    else:
        failures.append(f"  ✗ clone failed                rc={broken.returncode} {broken.stderr.strip()[-200:]!r} "
                        f"counts={counts} locks={len(locks_before)}/{len(locks_after)}")

    # --- two agents of the same name on one target: two branches, two authors -----------------------------
    born = [call("agent", "add", path) for path in ("rep1/ag1", "rep2/ag1")]
    paired = {}
    for path in ("rep1/ag1", "rep2/ag1"):
        meta = ws.joinpath(*path.split("/")) / INSTANCE
        where = bench.temp() / f"w-{path.replace('/', '-')}"
        played = call("agent", "run", path, "--work", str(target), "--message", f"work {path}",
                      *A.harnessing(f"{sys.executable} {witness} {engine} {meta} work {where}"))
        paired[path] = (played, key_of(played), where)
    authors = {path: _git("log", "-1", "--format=%an <%ae>", f"agent/{path}/{key}", cwd=target).stdout.strip()
               for path, (_, key, _) in paired.items() if key}
    slug = instance.read(house).get("slug")
    if (all(one.returncode == 0 for one in born)
            and all(played.returncode == 0 and key and f"agent/{path}/{key}" in branches()
                    for path, (played, key, _) in paired.items())
            and authors == {"rep1/ag1": f"rep1/ag1 <rep1.ag1@{slug}>", "rep2/ag1": f"rep2/ag1 <rep2.ag1@{slug}>"}
            and all(one.get("agent") == path for path, (_, key, _) in paired.items() for one in of_run(key))):
        held("two agents of the same name on one target", "rep1/ag1 and rep2/ag1: two branches "
             f"agent/<path>/<key> pushed, each commit signed by its path ({sorted(authors.values())}), "
             "workdirs.jsonl names each path")
    else:
        failures.append(f"  ✗ same name on one target     born={[one.returncode for one in born]} "
                        f"{ {p: (v[0].returncode, v[1]) for p, v in paired.items()} } authors={authors} "
                        f"branches={branches()} {[v[0].stderr[-200:] for v in paired.values()]!r}")
    return len(failures)
