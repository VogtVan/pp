"""Scenario `agent-remove` -- `agent remove <path> [--yes] [--json]` takes an agent out of the house: its runs purged
(the same path as `agent purge`), then what pp wrote in its directory -- the console, each wired harness's files,
`.pp/` --, then the directory when nothing else stands in it (batch les-equipes-au-poste, agent 0.36.0).
- said, nothing written: without `--yes` the verb says the agent's runs and the files it would take out; under `--json`
  one object `{dry, agent, runs, files, left}`; the house's records and the agent's directory the same to the byte
- taken away: under `--yes` the runs leave the records and the agent's state, the consoles and `.pp/` are gone, the
  directory with them; `agent list --json` no longer says the agent; `status` refuses `agent-unknown`
- a directory not empty is kept: an agent whose directory carries a file of its own (`notes.md`) loses `.pp/` and the
  console, keeps the directory, and the verb says `directory-kept` naming what stands (rc 0; the face says
  `directory: kept`, `left` names the file)
- a held run refuses: a conversation open on a run of the agent, `--yes` refuses `run-busy` and nothing is removed --
  neither the run nor a file of the directory
- the refusals: a path nobody knows `agent-unknown`; the usage without a path
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from tests.harness import support

A = support(__file__, "agent")
RECORDS = ("responses.jsonl", "messages.jsonl", "sessions.jsonl", "names.jsonl", "workdirs.jsonl")


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root`."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(path for path in root.rglob("*") if path.is_file())} \
        if root.is_dir() else {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)                                       # agents/ag1 born as `add` births it: .pp, pp, pp.cmd
    h.wake("first run")
    h.wake("second run")
    keys = h.keys()

    def lines_of(name: str) -> list[dict]:
        """-> the lines of each record that carry the agent `name`."""
        return [one for record in RECORDS for one in A.lines(h.records / record)
                if one.get("agent") == name or one.get("to") == name]

    def listed() -> list[str]:
        played = h.call("agent", "list", "--json")
        return [json.loads(one).get("agent") for one in played.stdout.splitlines() if one.strip()]

    # --- said, nothing written --------------------------------------------------------------------------------
    records_before, ws_before = files_under(h.records), files_under(h.agent_ws)
    said = h.call("agent", "remove", "agents/ag1")
    counted = h.call("agent", "remove", "agents/ag1", "--json")
    try:
        told = json.loads(counted.stdout)
    except ValueError:
        told = {}
    if (said.returncode == 0 and counted.returncode == 0 and len(keys) == 2 and told.get("dry") is True
            and told.get("agent") == "agents/ag1" and sorted(told.get("runs") or []) == sorted(keys)
            and "pp" in (told.get("files") or []) and any(one.startswith(".pp") for one in told.get("files") or [])
            and told.get("left") == [] and files_under(h.records) == records_before and files_under(h.agent_ws) == ws_before):
        held("said, nothing written", f"runs {', '.join(keys)}; files {told.get('files')}; the records and the "
             "directory the same to the byte")
    else:
        failures.append(f"  ✗ said                        rc={said.returncode}/{counted.returncode} keys={keys} told={told} "
                        f"{said.stderr[-300:]!r} {counted.stderr[-300:]!r}")

    # --- a held run refuses -----------------------------------------------------------------------------------
    talking = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                                "--run", keys[-1] if keys else "", "--json", *h.harnessed("play")], stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=h.ws,
                               env={**os.environ, **h.env})
    assert talking.stdout is not None and talking.stdin is not None
    ready = talking.stdout.readline()                    # `ready`: the conversation holds the run's wake lock
    records_held, ws_held = files_under(h.records), files_under(h.agent_ws)
    busy = h.call("agent", "remove", "agents/ag1", "--yes")
    talking.stdin.close()
    talking.wait(timeout=30)
    if ('"ready"' in ready and busy.returncode == 2 and "run-busy" in busy.stderr
            and files_under(h.records) == records_held and files_under(h.agent_ws) == ws_held):
        bench.refusals += 1
        held("a held run refuses", f"a conversation open on {keys[-1] if keys else '?'}: run-busy, nothing removed")
    else:
        failures.append(f"  ✗ run-busy                    rc={busy.returncode} ready={ready[:60]!r} {busy.stderr[-300:]!r}")

    # --- taken away -------------------------------------------------------------------------------------------
    before = listed()
    gone = h.call("agent", "remove", "agents/ag1", "--yes", "--json")
    try:
        result = json.loads(gone.stdout)
    except ValueError:
        result = {}
    after = h.call("agent", "status", "agents/ag1")
    if (gone.returncode == 0 and result.get("dry") is False and result.get("directory") == "removed"
            and not h.agent_ws.exists() and not lines_of("agents/ag1")
            and "agents/ag1" in before and "agents/ag1" not in listed()
            and after.returncode == 2 and "agent-unknown" in after.stderr):
        held("taken away", f"agents/ag1 gone -- {len(result.get('runs') or [])} run(s) purged, {len(result.get('files') or [])} "
             "file(s) removed, the directory with them; list silent, status agent-unknown")
    else:
        failures.append(f"  ✗ taken away                  rc={gone.returncode}/{after.returncode} result={result} "
                        f"exists={h.agent_ws.exists()} lines={len(lines_of('agents/ag1'))} listed={listed()} "
                        f"{gone.stderr[-300:]!r}")

    # --- a directory not empty is kept ------------------------------------------------------------------------
    born = h.call("agent", "add", "agents/ag2")
    own = h.ws / "agents" / "ag2" / "notes.md"
    own.write_text("mine\n", encoding="utf-8")
    kept = h.call("agent", "remove", "agents/ag2", "--yes", "--json")
    try:
        result = json.loads(kept.stdout)
    except ValueError:
        result = {}
    plain = h.call("agent", "add", "agents/ag3")
    (h.ws / "agents" / "ag3" / "notes.md").write_text("mine\n", encoding="utf-8")
    plain = h.call("agent", "remove", "agents/ag3", "--yes")
    if (born.returncode == 0 and kept.returncode == 0 and result.get("directory") == "kept"
            and result.get("left") == ["notes.md"] and own.is_file() and not (own.parent / ".pp").exists()
            and not (own.parent / "pp").exists() and plain.returncode == 0 and "directory-kept" in plain.stdout
            and "notes.md" in plain.stdout):
        held("a directory not empty is kept", "agents/ag2: .pp/ and the console gone, notes.md stands, the directory "
             "kept and said: directory-kept")
    else:
        failures.append(f"  ✗ kept                        rc={born.returncode}/{kept.returncode}/{plain.returncode} "
                        f"result={result} own={own.is_file()} pp={(own.parent / '.pp').exists()} {plain.stdout[-300:]!r} "
                        f"{kept.stderr[-300:]!r}")

    # --- the refusals -----------------------------------------------------------------------------------------
    unknown = h.call("agent", "remove", "agents/nobody", "--yes")
    bare = h.call("agent", "remove")
    if unknown.returncode == 2 and "agent-unknown" in unknown.stderr and bare.returncode == 2 and "usage" in bare.stderr:
        bench.refusals += 2
        held("the refusals", "agents/nobody agent-unknown; no path the usage")
    else:
        failures.append(f"  ✗ refusals                    {unknown.returncode} {unknown.stderr[-200:]!r} {bare.returncode} "
                        f"{bare.stderr[-200:]!r}")
    return 0
