"""Scenario `agent-house` -- 4 case(s) (plan ui, batch la-maison-et-ses-themes, 2026-10-09): the HOUSE is the
agent `.` -- its own instance, its own runs, its own boot -- on a throwaway house and the witness harness:
- `agent chat . --json`: a run opened on the house itself, under its own state, in the principal's mode, its
  session recorded for `.`; the first prompt carries the house's own member (a mark written in its
  `MEMBER.md`), the boot of the house and not of an agent
- the face of the house shows its runs of the post alone: beside a run the LLM conducts (`-new` unmarked),
  `status . --json` says one run, `list --json` heads with `{agent: "."}` counting it, the text of `list`
  stays the borrowers' alone; `chat . --run <the LLM's key>` refuses `run-unconducted`, nothing launched
- `add .` refuses `agent-exists`; `run . --work <repo>` refuses `work-on-house`; nothing written
- an agent born by `add` keeps its faces: `status agents/ag1` and `list` say what they said
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from conductor import persistence
from tests.harness import cli, support

A = support(__file__, "agent")
MARK = "HOUSE-MEMBER-MARK-a7f3"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    member = h.house / "MEMBER.md"
    member.write_text(member.read_text(encoding="utf-8").rstrip("\n") + f"\n\n{MARK}\n", encoding="utf-8")
    out = bench.temp() / "house-prompt"

    def objects(text: str) -> list[dict]:
        return [json.loads(line) for line in text.splitlines() if line.strip().startswith("{")]

    def talk(*flags: str, commands: str) -> subprocess.CompletedProcess:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", ".", "--json", *flags,
                *h.harnessed_at("play", out, h.house)]
        return subprocess.run(argv, input=commands, capture_output=True, text=True, cwd=h.ws,
                              env={**os.environ, **h.env}, timeout=120)

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    # --- chat . opens a run on the house itself ---------------------------------------------------------
    talked = talk(commands=command("message", text="bonjour la maison") + command("quit"))
    events = objects(talked.stdout)
    opened = next((one for one in events if one.get("kind") == "opened"), {})
    house_keys = h.keys(h.house)
    key = opened.get("run") or ""
    slot = persistence.slot_of(h.house, key) if key else None
    first = (out.parent / (out.name + ".prompt.w-1.1"))
    prompt = first.read_text(encoding="utf-8") if first.is_file() else ""
    house_sessions = [one for one in h.sessions() if one.get("agent") == "."]
    if (talked.returncode == 0 and key and key in house_keys and key not in h.keys()
            and slot is not None and persistence.mode_of(slot) == persistence.PRINCIPAL
            and opened.get("agent") == "." and [one.get("run") for one in house_sessions] == [key]
            and MARK in prompt and any(one.get("kind") == "verdict" and one.get("state") == "parked" for one in events)):
        held("chat . opens a run on the house", f"run {key} under the house's own state, conducted by its principal, "
             "its session recorded for `.`; the first prompt carries the house's member, the verdict parked")
    else:
        failures.append(f"  ✗ chat .                      rc={talked.returncode} key={key!r} house={house_keys} "
                        f"agent={h.keys()} sessions={house_sessions} mark={MARK in prompt} {talked.stderr[-300:]!r} "
                        f"{[one.get('kind') for one in events]}")

    # --- the face of the house: its runs of the post alone -------------------------------------------------
    llm = cli(h.engine, "--instance", str(h.house), "-new", cwd=h.ws)
    llm_key = next((one for one in h.keys(h.house) if one != key), "")
    status = h.call("agent", "status", ".", "--json")
    runs = [one for one in objects(status.stdout) if "run" in one]
    listed = h.call("agent", "list", "--json")
    lines = objects(listed.stdout)
    text = h.call("agent", "list")
    refused = talk("--run", llm_key, commands=command("quit")) if llm_key else None
    if (llm.returncode == 0 and llm_key and status.returncode == 0 and [one.get("run") for one in runs] == [key]
            and lines and lines[0].get("agent") == "." and lines[0].get("runs") == 1
            and [one.get("agent") for one in lines] == [".", "agents/ag1"]
            and text.returncode == 0 and text.stdout.startswith("agents/ag1 · ") and "\n." not in "\n" + text.stdout
            and refused is not None and refused.returncode == 2 and "run-unconducted" in refused.stderr
            and refused.stdout == "" and persistence.mode_of(persistence.slot_of(h.house, llm_key)) == ""):
        held("the face of the house shows its runs of the post", f"beside the LLM's run {llm_key}: status . says "
             f"{key} alone, list --json heads with `.` (1 run), the text of list says agents/ag1 alone; "
             "chat . --run on the LLM's run refuses run-unconducted, nothing launched")
    else:
        failures.append(f"  ✗ the face                    llm={llm.returncode}/{llm_key!r} runs={runs} list={lines} "
                        f"text={text.stdout!r} refused={refused and (refused.returncode, refused.stderr[-200:])}")

    # --- add . and --work on . refuse, nothing written -------------------------------------------------------
    before = A.tree(h.house)
    added = h.call("agent", "add", ".")
    worked = h.call("agent", "run", ".", "--message", "work", "--work", str(h.ws), *h.harnessed_at("play", out, h.house))
    if (added.returncode == 2 and "agent-exists" in added.stderr and worked.returncode == 2
            and "work-on-house" in worked.stderr and A.tree(h.house) == before):
        held("add . and --work on . refuse", "agent-exists; work-on-house -- the house's tree unchanged")
    else:
        failures.append(f"  ✗ refusals                    add={added.returncode} {added.stderr[-160:]!r} "
                        f"work={worked.returncode} {worked.stderr[-160:]!r} same={A.tree(h.house) == before}")

    # --- an agent born by add keeps its faces ---------------------------------------------------------------
    woken = h.wake("an agent's run")
    agent_status = h.call("agent", "status", "agents/ag1")
    agent_runs = [one for one in objects(h.call("agent", "status", "agents/ag1", "--json").stdout) if "run" in one]
    if (woken.returncode == 0 and len(agent_runs) == 1 and agent_runs[0].get("agent") == "agents/ag1"
            and agent_status.stdout.startswith(f"run {agent_runs[0].get('run')} · 1 exchange(s) · parked at FINAL")):
        held("an agent keeps its faces", "status agents/ag1 says its run as before, text and --json")
    else:
        failures.append(f"  ✗ the agent's faces           {woken.returncode} {agent_runs} {agent_status.stdout!r}")
    return 0
