"""Scenario `agent-purge` -- `agent purge <path> (<key> … | --before <date>) [--yes] [--force] [--json]` removes
for good what the house keeps of a run of an agent, then has the engine remove what the agent keeps of it
(`./pp -purge` on the agent's instance) -- each record by its writer.
- said first: without `--yes` one line per run and the total; the house's records and the agent's state the
  same to the byte before and after
- `--json`: one object -- `dry`, `runs` [{key, lines, files, bytes, workdir}], the totals
- removed: after `--yes` no line of the five records carries the run for that agent, no file of the agent's
  state carries its key, `status` no longer says it; the other run's lines and files the same to the byte
- the flow kept: the run's flow file (`flows/<digest>/<key>.jsonl`) removed with it, the other run's kept
- never a run held: under a conversation open on the run, `--yes` refuses `run-busy` and nothing is removed --
  neither that run nor another named with it
- the refusals: a key nobody knows `run-unknown`, a date that does not read `purge-invalid`, no key and no date
  the usage -- nothing removed
- by age: `--before` an old date retains nothing; `--before` tomorrow retains the run left
- the family: `pp-agent verify` -- the engine's call for the vector family `agent-run:<path>/<key>` -- says
  rc 0 on a run the house keeps, `run-unknown` on a key nobody knows
- the material of a run (its clone under `<path>/work/<key>`), the rule of `prune`: a clone with a commit the
  repository has not received refuses `workdir-unpushed`, and nothing is removed -- neither the clone, nor a
  line of the records, nor a file of the agent's state; `--force` removes it with the run's lines and files
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

from conductor import persistence
from tests.harness import support

A = support(__file__, "agent")
RECORDS = ("responses.jsonl", "messages.jsonl", "sessions.jsonl", "names.jsonl", "workdirs.jsonl")


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          env={"GIT_AUTHOR_NAME": "bench", "GIT_AUTHOR_EMAIL": "bench@bench",
                               "GIT_COMMITTER_NAME": "bench", "GIT_COMMITTER_EMAIL": "bench@bench",
                               "HOME": str(cwd), "PATH": "/usr/bin:/bin:/usr/local/bin"})


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root`."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()} \
        if root.is_dir() else {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    state = h.agent_meta / persistence.DIRECTORY

    h.wake("first run")
    h.wake("second run")
    keys = h.keys()
    first, second = (keys + ["", ""])[:2]
    h.call("agent", "name", "agents/ag1", first, "the first")

    def lines_of(key: str) -> dict[str, list[dict]]:
        """-> the lines of each record that carry `key` for the agent."""
        return {name: [one for one in A.lines(h.records / name) if one.get("run") == key
                       and (one.get("agent") == "agents/ag1" or one.get("to") == "agents/ag1")] for name in RECORDS}

    def agent_files(key: str) -> dict[str, bytes]:
        return {name: data for name, data in files_under(state).items() if key and key in name}

    # --- said first: nothing written without --yes ---------------------------------------------------------
    records_before, state_before = files_under(h.records), files_under(state)
    said = h.call("agent", "purge", "agents/ag1", first)
    if (said.returncode == 0 and first in said.stdout and "would" in said.stdout
            and files_under(h.records) == records_before and files_under(state) == state_before):
        held("said first, nothing written", f"run {first}: {said.stdout.strip().splitlines()[0][:90]}; the records and "
             "the agent's state the same to the byte")
    else:
        failures.append(f"  ✗ said first                  rc={said.returncode} {said.stdout[-300:]!r} {said.stderr[-300:]!r}")

    # --- --json: one object -------------------------------------------------------------------------------
    counted = h.call("agent", "purge", "agents/ag1", first, "--json")
    try:
        told = json.loads(counted.stdout)
    except ValueError:
        told = {}
    runs = told.get("runs") or [{}]
    if (counted.returncode == 0 and told.get("dry") is True and [one.get("key") for one in runs] == [first]
            and runs[0].get("lines", {}).get("responses.jsonl") == len(lines_of(first)["responses.jsonl"])
            and runs[0].get("files") and isinstance(runs[0].get("bytes"), int)):
        held("--json says the same in one object", f"dry, run {first}: lines {runs[0].get('lines')}, "
             f"{len(runs[0].get('files'))} file(s), {runs[0].get('bytes')} bytes")
    else:
        failures.append(f"  ✗ json                        rc={counted.returncode} {counted.stdout[-300:]!r} "
                        f"{counted.stderr[-300:]!r}")

    # --- removed: the run leaves nothing of itself, the other stays to the byte ------------------------------
    flows = h.records / "flows" / hashlib.sha1("agents/ag1".encode("utf-8")).hexdigest()[:12]
    first_flow, second_flow = flows / f"{first}.jsonl", flows / f"{second}.jsonl"
    flowed = first_flow.is_file() and second_flow.is_file()
    second_kept = second_flow.read_bytes() if second_flow.is_file() else b""
    second_lines, second_files = lines_of(second), agent_files(second)
    gone = h.call("agent", "purge", "agents/ag1", first, "--yes")
    left = lines_of(first)
    listed = h.call("agent", "status", "agents/ag1").stdout
    if (gone.returncode == 0 and first in gone.stdout and not any(left.values()) and not agent_files(first)
            and not persistence.slot_of(h.agent_meta, first).is_file() and f"run {first} ·" not in listed
            and lines_of(second) == second_lines and agent_files(second) == second_files and second_files):
        held("a run purged leaves nothing of itself", f"run {first}: no line in the five records, no file of the "
             f"agent's state, status silent; run {second} the same to the byte")
    else:
        failures.append(f"  ✗ removed                     rc={gone.returncode} left={ {k: len(v) for k, v in left.items()} } "
                        f"files={sorted(agent_files(first))} {gone.stdout[-300:]!r} {gone.stderr[-300:]!r}")

    if flowed and gone.returncode == 0 and not first_flow.exists() and second_flow.read_bytes() == second_kept:
        held("the flow kept goes with the run", f"flows/…/{first}.jsonl removed; {second}'s the same to the byte")
    else:
        failures.append(f"  ✗ flow removed                before={flowed} after={first_flow.exists()}")

    # --- never a run held: a conversation open on the run ---------------------------------------------------
    talking = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                                "--run", second, "--json", *h.harnessed("play")], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=h.ws,
                               env={**os.environ, **h.env})
    assert talking.stdout is not None and talking.stdin is not None
    ready = talking.stdout.readline()                    # `ready`: the conversation holds the run's wake lock
    records_held, state_held = files_under(h.records), files_under(state)
    busy = h.call("agent", "purge", "agents/ag1", second, "--yes")
    talking.stdin.close()
    talking.wait(timeout=30)
    if ('"ready"' in ready and busy.returncode == 2 and "run-busy" in busy.stderr
            and files_under(h.records) == records_held and files_under(state) == state_held):
        bench.refusals += 1
        held("never a run held", f"a conversation open on {second}: run-busy, nothing removed")
    else:
        failures.append(f"  ✗ run-busy                    rc={busy.returncode} ready={ready[:60]!r} {busy.stderr[-300:]!r}")

    # --- the refusals -----------------------------------------------------------------------------------------
    records_now, state_now = files_under(h.records), files_under(state)
    unknown = h.call("agent", "purge", "agents/ag1", "zzzzzz", "--yes")
    invalid = h.call("agent", "purge", "agents/ag1", "--before", "2026-13-45")
    bare = h.call("agent", "purge", "agents/ag1")
    if (unknown.returncode == 2 and "run-unknown" in unknown.stderr and invalid.returncode == 2
            and "purge-invalid" in invalid.stderr and bare.returncode == 2 and "usage" in bare.stderr.lower()
            and files_under(h.records) == records_now and files_under(state) == state_now):
        bench.refusals += 2
        held("the refusals", "run-unknown, purge-invalid, the usage without key nor date -- nothing removed")
    else:
        failures.append(f"  ✗ refusals                    {unknown.returncode}/{invalid.returncode}/{bare.returncode} "
                        f"{unknown.stderr[-160:]!r} {invalid.stderr[-160:]!r} {bare.stderr[-160:]!r}")

    # --- by age ---------------------------------------------------------------------------------------------
    old = h.call("agent", "purge", "agents/ag1", "--before", "2000-01-01", "--json")
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    recent = h.call("agent", "purge", "agents/ag1", "--before", tomorrow, "--json")
    try:
        old_told, recent_told = json.loads(old.stdout), json.loads(recent.stdout)
    except ValueError:
        old_told, recent_told = {}, {}
    if (old.returncode == 0 and old_told.get("runs") == [] and recent.returncode == 0
            and [one.get("key") for one in recent_told.get("runs") or []] == [second]
            and files_under(h.records) == records_now):
        held("by age", f"--before 2000-01-01 retains nothing; --before {tomorrow} retains {second}, said, not removed")
    else:
        failures.append(f"  ✗ by age                      {old.returncode}/{recent.returncode} {old.stdout[-200:]!r} "
                        f"{recent.stdout[-200:]!r} {recent.stderr[-200:]!r}")

    # --- the family: pp-agent verifies `agent-run:<path>/<key>` -------------------------------------------
    script = next(iter((h.house / ".sys" / "vendor").glob("agent@*/skills/pp-agent/pp-agent.py")), None)
    asked = [subprocess.run([sys.executable, str(script), "verify"], input=vector, capture_output=True, text=True,
                            cwd=h.ws) for vector in (f"agent-run:agents/ag1/{second}", "agent-run:agents/ag1/zzzzzz")]
    if script and asked[0].returncode == 0 and asked[1].returncode == 2 and "run-unknown" in asked[1].stderr:
        bench.refusals += 1
        held("the family verified", f"agent-run:agents/ag1/{second} rc 0; an unknown key run-unknown")
    else:
        failures.append(f"  ✗ verify                      script={script} rc={[one.returncode for one in asked]} "
                        f"{[one.stderr[-160:] for one in asked]!r}")

    # --- the material: a run with its clone, woken last -- the cases above count the runs ------------------------
    target = bench.temp() / "target"
    target.mkdir()
    git("init", "-q", "-b", "main", cwd=target)
    (target / "README").write_text("target\n", encoding="utf-8")
    git("add", "README", cwd=target)
    git("commit", "-q", "-m", "first", cwd=target)
    before = set(h.keys())
    worked = h.wake("work on it", "play", "--work", str(target))
    key = next((one for one in h.keys() if one not in before), "")
    clone = h.agent_ws / "work" / key
    git("commit", "-q", "--allow-empty", "-m", "not sent", cwd=clone)   # a commit the repository never received

    def counted_lines() -> int:
        return sum(len(found) for found in lines_of(key).values()) if key else 0

    # --- a clone with unsent commits refuses, nothing removed ------------------------------------------------
    records_before, state_before, kept = files_under(h.records), files_under(state), counted_lines()
    refused = h.call("agent", "purge", "agents/ag1", key, "--yes")
    if (worked.returncode == 0 and clone.is_dir() and refused.returncode == 2 and "workdir-unpushed" in refused.stderr
            and files_under(h.records) == records_before and files_under(state) == state_before and kept):
        bench.refusals += 1
        held("a clone with unsent commits refuses", f"run {key}: workdir-unpushed, the clone, {kept} line(s) and the "
             "agent's state untouched")
    else:
        failures.append(f"  ✗ unpushed                    rc={worked.returncode}/{refused.returncode} clone={clone.is_dir()} "
                        f"{refused.stderr[-300:]!r} {worked.stderr[-300:]!r}")

    # --- --force removes it ------------------------------------------------------------------------------------
    forced = h.call("agent", "purge", "agents/ag1", key, "--yes", "--force")
    left = [name for name in files_under(state) if key and key in name]
    if (forced.returncode == 0 and key and not clone.exists() and counted_lines() == 0 and not left
            and f"material work/{key}" in forced.stdout):
        held("--force removes the clone with the run", f"run {key}: the clone, the lines and the agent's files gone")
    else:
        failures.append(f"  ✗ forced                      rc={forced.returncode} clone={clone.exists()} lines={counted_lines()} "
                        f"left={left} {forced.stdout[-300:]!r} {forced.stderr[-300:]!r}")
    return 0
