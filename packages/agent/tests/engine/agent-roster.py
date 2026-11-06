"""Scenario `agent-roster` -- the agents of a house: born at their paths, the house its own agent, a profile per
type, the console's verb:
- an agent is born under the house: `agents/ag1/.pp` BORROWS the house's machine (no engine, no vendor, no pins
  of its own), exactly the seed of an interactive instance of the same composition outside `.sys` -- none of what
  an adapter's `wire()` writes, the launcher beside it
- an agent is born at its path: `agent add rep1/ag1` and `agent add ag2` each seed a borrower, the interactive
  seed outside `.sys` but for ONE line -- `max_harness_tool_output: 200000` at its SETTINGS.md --, no door, the
  slug the path's last segment; the birth says the line
- `add` refuses before writing: `agent-exists`, `type-unsupported` under a `--type` other than `member` or `chat`,
  `agent-path-invalid` on `../x`, `/abs/x`, `Rep1/ag1`, `rep1//ag1`, `rep1/ag1/`; `upgrade` is the usage
- two agents of the same name at two paths, `rep1/ag1` and `rep2/ag1`, are two agents: each woken in its own
  directory, the records say each path, the readings of one never show the other
- `list` descends the house: `ag2`, `agents/ag1`, `rep1/ag1`, `rep2/ag1`, by their paths
- a path where no agent stands refuses `agent-unknown`, naming the `agent add` that creates it
- two births of one path at once: five races of two `agent add` on one new path -- each path born once, the other
  add refused `agent-exists`
- the HOUSE is the agent `.`: `agent chat . --json` opens a run on the house itself, under its own state, in the
  principal's mode, its session recorded for `.`; the first prompt carries the house's own member (a mark written
  in its `MEMBER.md`), the boot of the house and not of an agent
- the face of the house shows its runs of the post alone: beside a run the LLM conducts (`-new` unmarked),
  `status . --json` says one run, `list --json` heads with `{agent: "."}` counting it, the text of `list` stays
  the borrowers' alone; `chat . --run <the LLM's key>` refuses `run-unconducted`, nothing launched
- `add .` refuses `agent-exists`; `run . --work <repo>` refuses `work-on-house`; nothing written
- an agent born by `add` keeps its faces beside the house's runs: `status agents/ag1` says its run, text and
  `--json`
- `--type member` in a house pinning continuity and steering: the agent's SETTINGS differs from a birth without
  type by `capabilities: false` and `package.steering: off` alone; the birth says the profile; its boot asks no table
  and runs no pass, and receives the skills and the formats as a birth without type does
- `--type chat`: the member's lines plus `continuity_history_day: never`
- the boot of the member's run: no prompt of its first exchange carries the CAPABILITIES frame nor the THREADS
  pass, where the boot of an agent born without type carries both
- a house without continuity nor steering: `--type chat` writes `capabilities: false` alone, and the birth names
  the keys it left; an unknown type refuses `type-unsupported` and writes nothing
- the console carries the verb: `./pp help` lists `agent` with its package and its `add`; `./pp agent` without a
  verb says the usage in one line, exit 2
- `start` without a message relays `message-missing` in one line, nothing launched, no run opened
- `prune` without the run's key says the usage in one line, nothing touched
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from conductor import instance, persistence
from conductor.packaging.compiling import CATALOGS
from tests.harness import INSTANCE, cli, race, support

A = support(__file__, "agent")
MARK = "HOUSE-MEMBER-MARK-a7f3"
MEMBER = {"capabilities": "false", "package.steering": "off"}
CHAT = {**MEMBER, "continuity_history_day": "never"}
FRAME = re.compile(r"^▌ (?:\[\d+\] )?.*\b(CAPABILITIES|THREADS)\{", re.M)


def objects(text: str) -> list[dict]:
    """-> the JSON objects of a reading, one per line."""
    return [json.loads(line) for line in text.splitlines() if line.strip().startswith("{")]


def front(meta: Path) -> dict[str, str]:
    """-> the top-level `key: value` lines of an instance's SETTINGS front matter."""
    lines = (meta / "SETTINGS.md").read_text(encoding="utf-8").splitlines()
    end = lines.index("---", 1) if lines[:1] == ["---"] and "---" in lines[1:] else 0
    found = {}
    for line in lines[1:end]:
        if line[:1] in (" ", "\t", "#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        found[key.strip()] = value.strip()
    return found


def added(meta: Path, plain: Path) -> dict[str, str]:
    """-> the lines of `meta`'s SETTINGS that differ from those of `plain`, an agent born without type."""
    mine, theirs = front(meta), front(plain)
    return {key: value for key, value in mine.items() if theirs.get(key) != value}


def readings(where: Path) -> set[str]:
    """-> the readings of the boot (`tools.md`, `output.md`) the prompts the witness received at
    `where` carry."""
    seen = set()
    for one in sorted(where.parent.glob(where.name + ".prompt.*")):
        text = one.read_text(encoding="utf-8")
        seen |= {name for name in CATALOGS if f"INFORMATION — {name}" in text}
    return seen


def frames(where: Path) -> set[str]:
    """-> the frames CAPABILITIES and THREADS the prompts the witness received at `where` carry."""
    seen = set()
    for one in sorted(where.parent.glob(where.name + ".prompt.*")):
        seen |= set(FRAME.findall(one.read_text(encoding="utf-8")))
    return seen


def births(bench, h) -> None:
    """The agents born at their paths under `h`, the house of `agents/ag1` alone."""
    held, failures = bench.held, bench.failures
    twin_ws, twin = h.twin()

    # --- an agent is born under the house: it borrows the house's machine ------------------------
    wirings = A.harness_artifacts(bench)                 # what the adapters' wire() write: doors, cards, launchers
    doors = [one for one in h.agent_ws.rglob("*") if one.name in wirings]
    beside = sorted(one.name for one in h.agent_ws.iterdir())
    same = instance.is_instance(h.agent_meta) and A.tree(h.agent_meta) == A.tree(twin)
    declared = instance.read(h.agent_meta) if instance.is_instance(h.agent_meta) else {}
    if (same and not doors and beside == [INSTANCE, "pp", "pp.cmd"] and declared.get("slug") == "ag1"
            and not {"engine", "packages", "source"} & set(declared)
            and not (h.agent_meta / ".sys" / "engine").exists() and not (h.agent_meta / ".sys" / "vendor").exists()):
        held("an agent is born under the house", "agents/ag1/.pp borrows the house's machine, the seed of "
             "an interactive instance byte for byte outside .sys, no door, the launchers `pp`/`pp.cmd` beside it")
    else:
        failures.append(f"  ✗ agent born                  same={same} doors={doors} beside={beside} "
                        f"declared={sorted(declared)}")

    # --- an agent is born at its path: `add` wraps the generic install, no door, the cap written ---
    born = h.call("agent", "add", "rep1/ag1")
    plain = h.call("agent", "add", "ag2")
    born_at = {path: h.ws.joinpath(*path.split("/")) for path in ("rep1/ag1", "ag2")}
    seeds = {path: (instance.is_instance(where / INSTANCE)
                    and A.tree_but_cap(where / INSTANCE) == A.tree_but_cap(twin)
                    and "max_harness_tool_output: 200000\n" in (where / INSTANCE / "SETTINGS.md").read_text(encoding="utf-8")
                    and sorted(one.name for one in where.iterdir()) == [INSTANCE, "pp", "pp.cmd"]
                    and not (where / INSTANCE / ".sys" / "engine").exists()
                    and not (where / INSTANCE / ".sys" / "vendor").exists()
                    and instance.read(where / INSTANCE).get("slug") == path.rsplit("/", 1)[-1])
             for path, where in born_at.items()}
    if (born.returncode == 0 and plain.returncode == 0 and all(seeds.values())
            and "rep1/ag1" in born.stdout and "ag2" in plain.stdout
            and "max_harness_tool_output 200000" in born.stdout and "max_harness_tool_output 200000" in plain.stdout):
        held("an agent is born at its path, the cap written", "agent add rep1/ag1 and agent add ag2: each borrows the "
             "house's machine, the seed of an interactive instance outside .sys but for `max_harness_tool_output: "
             "200000` at SETTINGS.md (said at the birth), no door, `pp`/`pp.cmd` beside it")
    else:
        failures.append(f"  ✗ agent add                   {born.returncode}/{plain.returncode} seeds={seeds} "
                        f"{born.stdout[-160:]!r} {born.stderr[-200:]!r} {plain.stderr[-200:]!r}")

    # --- add refuses before writing: agent-exists, type-unsupported, agent-path-invalid -----------
    before_tree = sorted(str(one.relative_to(h.ws)) for one in h.ws.rglob("*") if ".sys" not in one.parts)
    again = h.call("agent", "add", "rep1/ag1")
    typed = h.call("agent", "add", "rep3/ag1", "--type", "reviewer")
    wrong = [h.call("agent", "add", one) for one in ("../x", "/abs/x", "Rep1/ag1", "rep1//ag1", "rep1/ag1/")]
    upgraded = h.call("agent", "upgrade")
    after_tree = sorted(str(one.relative_to(h.ws)) for one in h.ws.rglob("*") if ".sys" not in one.parts)
    if (again.returncode == 2 and "agent-exists" in again.stderr
            and typed.returncode == 2 and "type-unsupported" in typed.stderr
            and all(one.returncode == 2 and "agent-path-invalid" in one.stderr for one in wrong)
            and upgraded.returncode == 2 and "usage: pp-agent" in upgraded.stderr
            and before_tree == after_tree):
        held("add refuses before writing", "agent-exists on rep1/ag1 again, type-unsupported on --type reviewer, "
             "agent-path-invalid on ../x, /abs/x, Rep1/ag1, rep1//ag1, rep1/ag1/; upgrade is the usage; the tree unchanged")
    else:
        failures.append(f"  ✗ add refusals                {again.returncode}/{typed.returncode}/"
                        f"{[one.returncode for one in wrong]}/{upgraded.returncode} {again.stderr[-120:]!r} "
                        f"{typed.stderr[-120:]!r} {[one.stderr[-80:] for one in wrong]!r} changed={before_tree != after_tree}")

    # --- two agents of the same name at two paths are two agents --------------------------------
    second_born = h.call("agent", "add", "rep2/ag1")
    twins = {path: h.ws.joinpath(*path.split("/")) / INSTANCE for path in ("rep1/ag1", "rep2/ag1")}
    outs = {path: bench.temp() / f"p-{path.replace('/', '-')}" for path in twins}
    woke = {path: h.call("agent", "run", path, "--message", f"hello {path}",
                         *h.harnessed_at("play", outs[path], meta))
            for path, meta in twins.items()}
    cwds = {path: h.read(".cwd", outs[path]) for path in twins}
    kept_by = {path: [one for one in h.responses() if one.get("agent") == path] for path in twins}
    sent_to = {path: [one for one in h.messages() if one.get("to") == path] for path in twins}
    shown = {path: (h.call("agent", "status", path), h.call("agent", "responses", path, "--last", "5"),
                    h.call("agent", "messages", path, "--last", "5")) for path in twins}
    apart = all(other not in "".join(one.stdout for one in shown[path])
                for path in twins for other in twins if other != path)
    if (second_born.returncode == 0 and all(one.returncode == 0 for one in woke.values())
            and all(Path(cwds[path]).resolve() == twins[path].parent.resolve() for path in twins)
            and all(len(kept_by[path]) == 1 and kept_by[path][0]["response"] == "witness answer: play" for path in twins)
            and all(len(sent_to[path]) == 1 and sent_to[path][0]["message"] == f"hello {path}" for path in twins)
            and all(f"pp-agent: {path} · run" in woke[path].stderr for path in twins)
            and all(one.returncode == 0 for trio in shown.values() for one in trio)
            and all(f"{path} · run" in shown[path][1].stdout and f"house -> {path}" in shown[path][2].stdout
                    for path in twins) and apart):
        held("two agents of the same name are two agents", "rep1/ag1 and rep2/ag1 woken in their own directories; "
             "responses.jsonl and messages.jsonl say each path, status, responses and messages of one never show the other")
    else:
        failures.append(f"  ✗ same name, two paths        {second_born.returncode} "
                        f"{[one.returncode for one in woke.values()]} cwds={cwds} "
                        f"kept={ {k: len(v) for k, v in kept_by.items()} } apart={apart} "
                        f"{[one.stderr[-200:] for one in woke.values()]!r}")

    # --- list finds the agents by descending the launcher ---------------------------------------
    listed = h.call("agent", "list")
    rows = [one.split(" · ", 1)[0] for one in listed.stdout.splitlines()]
    if listed.returncode == 0 and rows == ["ag2", "agents/ag1", "rep1/ag1", "rep2/ag1"]:
        held("list descends the launcher", f"every borrower under the house, by its path: {rows}")
    else:
        failures.append(f"  ✗ list by descent             rc={listed.returncode} rows={rows} {listed.stdout[-300:]!r}")

    # --- an unknown path refuses agent-unknown, the add named -------------------------------------
    nobody = h.call("agent", "status", "rep9/ag1")
    if nobody.returncode == 2 and "agent-unknown" in nobody.stderr and "agent add rep9/ag1" in nobody.stderr:
        held("an unknown path refuses agent-unknown", "status rep9/ag1: rc 2, the add that creates it named")
    else:
        failures.append(f"  ✗ unknown path                rc={nobody.returncode} {nobody.stderr[-200:]!r}")

    # --- two births of one path at once: one born, the other agent-exists ---------------------------
    raced = []
    for n in range(1, 6):
        both = race(h.engine, [["--instance", str(h.house), "agent", "add", f"twins/t{n}"]] * 2, cwd=h.ws, env=h.env)
        raced.append((n, sorted(one.returncode for one in both),
                      sum(1 for one in both if f"twins/t{n} born" in one.stdout),
                      sum(1 for one in both if "agent-exists" in one.stderr),
                      instance.is_instance(h.ws / "twins" / f"t{n}" / INSTANCE),
                      [one.stderr.strip()[-120:] for one in both if one.returncode and "agent-exists" not in one.stderr]))
    if all(rcs == [0, 2] and born == 1 and exists == 1 and stands for _, rcs, born, exists, stands, _ in raced):
        held("two births of one path at once", "five races of two `agent add` on one new path: one born, the "
             "other refused agent-exists, each time")
    else:
        failures.append(f"  ✗ births raced                {raced}")


def the_house(bench) -> None:
    """The house as the agent `.`, on a house of its own: its faces read the roster of `agents/ag1` alone."""
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    member = h.house / "MEMBER.md"
    member.write_text(member.read_text(encoding="utf-8").rstrip("\n") + f"\n\n{MARK}\n", encoding="utf-8")
    out = bench.temp() / "house-prompt"

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
    born = h.call("agent", "add", ".")
    worked = h.call("agent", "run", ".", "--message", "work", "--work", str(h.ws), *h.harnessed_at("play", out, h.house))
    if (born.returncode == 2 and "agent-exists" in born.stderr and worked.returncode == 2
            and "work-on-house" in worked.stderr and A.tree(h.house) == before):
        held("add . and --work on . refuse", "agent-exists; work-on-house -- the house's tree unchanged")
    else:
        failures.append(f"  ✗ refusals                    add={born.returncode} {born.stderr[-160:]!r} "
                        f"work={worked.returncode} {worked.stderr[-160:]!r} same={A.tree(h.house) == before}")

    # --- an agent born by add keeps its faces ---------------------------------------------------------------
    woken = h.wake("an agent's run")
    agent_status = h.call("agent", "status", "agents/ag1")
    agent_runs = [one for one in objects(h.call("agent", "status", "agents/ag1", "--json").stdout) if "run" in one]
    if (woken.returncode == 0 and len(agent_runs) == 1 and agent_runs[0].get("agent") == "agents/ag1"
            and agent_status.stdout.startswith(f"run {agent_runs[0].get('run')} · 1 exchange(s) · parked")):
        held("an agent keeps its faces", "status agents/ag1 says its run as before, text and --json")
    else:
        failures.append(f"  ✗ the agent's faces           {woken.returncode} {agent_runs} {agent_status.stdout!r}")


def profiles(bench) -> None:
    """The profile `--type` writes, in a house pinning continuity and steering, then in a house of `agent` alone."""
    held, failures = bench.held, bench.failures
    h = A.House(bench, born=False, packages=("agent", "continuity", "steering"))

    # --- member: two lines beside a birth without type, said at the birth --------------------------
    plain_born = h.call("agent", "add", "agents/plain")
    member_born = h.call("agent", "add", "agents/m", "--type", "member")
    plain, member = (h.ws / "agents" / name / INSTANCE for name in ("plain", "m"))
    member_lines = added(member, plain) if plain_born.returncode == 0 and member_born.returncode == 0 else {}
    if member_lines == MEMBER and all(key in member_born.stdout for key in MEMBER):
        held("member writes its profile", f"agents/m differs from agents/plain by {member_lines}; the birth says them")
    else:
        failures.append(f"  ✗ member                      rc={plain_born.returncode}/{member_born.returncode} "
                        f"lines={member_lines} {member_born.stdout[-200:]!r} {member_born.stderr[-200:]!r}")

    # --- chat: the member's lines plus the silence by cadence ---------------------------------------
    chat_born = h.call("agent", "add", "agents/c", "--type", "chat")
    chat = h.ws / "agents" / "c" / INSTANCE
    chat_lines = added(chat, plain) if chat_born.returncode == 0 else {}
    if chat_lines == CHAT:
        held("chat writes the member's lines and the silence", f"agents/c differs from agents/plain by {chat_lines}")
    else:
        failures.append(f"  ✗ chat                        rc={chat_born.returncode} lines={chat_lines} "
                        f"{chat_born.stderr[-200:]!r}")

    # --- the boot: no CAPABILITIES for the member, the table for a birth without type ----------------
    out_plain, out_member = bench.temp() / "plain", bench.temp() / "member"
    woke_plain = h.call("agent", "run", "agents/plain", "--message", "hello",
                        *h.harnessed_at("play", out_plain, plain))
    woke_member = h.call("agent", "run", "agents/m", "--message", "hello",
                         *h.harnessed_at("play", out_member, member))
    seen_plain, seen_member = frames(out_plain), frames(out_member)
    if (woke_plain.returncode == 0 and woke_member.returncode == 0
            and seen_plain == {"CAPABILITIES"} and seen_member == set()
            and readings(out_plain) == readings(out_member) == set(CATALOGS)):
        held("the member boots without the table", f"agents/plain's prompts carry {sorted(seen_plain)}, "
             "agents/m's none; both carry tools.md and output.md")
    else:
        failures.append(f"  ✗ boot                        rc={woke_plain.returncode}/{woke_member.returncode} "
                        f"plain={sorted(seen_plain)} member={sorted(seen_member)} "
                        f"readings={sorted(readings(out_plain))}/{sorted(readings(out_member))} "
                        f"{woke_plain.stderr[-200:]!r} {woke_member.stderr[-200:]!r}")

    # --- a house without continuity nor steering: the keys it does not know are left and said ----------
    bare = A.House(bench, born=False)
    bare_plain = bare.call("agent", "add", "agents/plain")
    bare_chat = bare.call("agent", "add", "agents/c", "--type", "chat")
    before = sorted(str(one.relative_to(bare.ws)) for one in bare.ws.rglob("*") if ".sys" not in one.parts)
    unknown = bare.call("agent", "add", "agents/x", "--type", "reviewer")
    after = sorted(str(one.relative_to(bare.ws)) for one in bare.ws.rglob("*") if ".sys" not in one.parts)
    left = [key for key in CHAT if key != "capabilities"]
    bare_lines = (added(bare.ws / "agents" / "c" / INSTANCE, bare.ws / "agents" / "plain" / INSTANCE)
                  if bare_plain.returncode == 0 and bare_chat.returncode == 0 else {})
    said = bare_chat.stdout.split("left", 1)[1] if "left" in bare_chat.stdout else ""
    if (bare_lines == {"capabilities": "false"} and all(key in said for key in left)
            and unknown.returncode == 2 and "type-unsupported" in unknown.stderr and before == after):
        held("the keys a house does not know are left and said", f"chat in a house of agent alone: {bare_lines}, "
             f"the birth names {left} as left; --type reviewer refuses type-unsupported, nothing written")
    else:
        failures.append(f"  ✗ bare house                  rc={bare_plain.returncode}/{bare_chat.returncode}/{unknown.returncode} "
                        f"lines={bare_lines} said={said!r} {bare_chat.stderr[-200:]!r} {unknown.stderr[-200:]!r} "
                        f"changed={before != after}")


def console(bench, h) -> None:
    """The console's verb on `h`, where `ag2` stands born by `add` and never woken."""
    held, failures = bench.held, bench.failures
    ag2 = h.ws / "ag2" / INSTANCE

    # --- the console carries the verb ------------------------------------------------------
    helped = h.call("help")
    bare = h.call("agent")
    agent_line = next((one for one in helped.stdout.splitlines() if "./pp agent" in one), "")
    if (helped.returncode == 0 and "(agent)" in agent_line and "`add`" in agent_line
            and bare.returncode == 2 and "usage" in (bare.stderr + bare.stdout).lower()
            and len((bare.stderr + bare.stdout).strip().splitlines()) == 1):
        held("the console carries the verb", "./pp help lists `./pp agent (agent) …` with `add`; "
             "a bare `./pp agent` says the usage in one line, exit 2")
    else:
        failures.append(f"  ✗ console verb                {helped.returncode}/{bare.returncode} "
                        f"{helped.stdout[-200:]!r} {bare.stderr[-200:]!r}")

    # --- start without a message: the child's refusal relayed in one line, nothing launched --------
    bare_start = h.call("agent", "start", "ag2", *A.harnessing("true"))
    if (bare_start.returncode == 2 and "message-missing" in bare_start.stderr and bare_start.stdout == ""
            and len(bare_start.stderr.strip().splitlines()) == 1 and not persistence.slots(ag2)):
        held("start without a message refuses message-missing", "one line on stderr, no report, no run")
    else:
        failures.append(f"  ✗ start refusal               rc={bare_start.returncode} {bare_start.stdout!r} "
                        f"{bare_start.stderr[-200:]!r}")

    # --- prune wants the agent and the run's key: without the key, the usage in one line ---------------
    bare_prune = h.call("agent", "prune", "ag2")
    if (bare_prune.returncode == 2 and "usage" in bare_prune.stderr.lower() and bare_prune.stdout == ""
            and len(bare_prune.stderr.strip().splitlines()) == 1):
        held("prune without a key says the usage", "one line on stderr, exit 2, nothing touched")
    else:
        failures.append(f"  ✗ prune usage                 rc={bare_prune.returncode} {bare_prune.stdout!r} "
                        f"{bare_prune.stderr[-200:]!r}")


def scenario(bench) -> int:
    h = A.House(bench)
    births(bench, h)
    the_house(bench)
    profiles(bench)
    console(bench, h)
    return 0
