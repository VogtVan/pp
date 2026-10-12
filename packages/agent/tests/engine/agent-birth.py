"""Scenario `agent-birth` -- 7 case(s) (batch le-package-agent, 2026-09-27, its reworks of 2026-10-03
and 2026-10-07, and l-equipe-et-son-journal, rework, agent 0.3.2; split out of `agent-home` by
les-scenarios-par-maison, 2026-10-07): an agent is born at its path under the house, it borrows the
house's machine, and it IS its path in every verb and record.
- an agent is born under the house: `agents/ag1/.pp` BORROWS the house's machine (no engine, no
  vendor, no pins of its own), exactly the seed of an interactive instance of the same
  composition outside `.sys` -- none of what an adapter's `wire()` writes, the launcher beside it
- an agent is born at its path: `agent add rep1/ag1` and `agent add ag2` each seed a borrower,
  the interactive seed outside `.sys` but for ONE line -- `max_harness_tool_output: 200000` at its
  SETTINGS.md, so that pp's outputs reach the prompt in one or two launches --, no door, the slug
  the path's last segment; the birth says the line
- `add` refuses before writing: `agent-exists`, `type-unsupported` under `--type`,
  `agent-path-invalid` on `../x`, `/abs/x`, `Rep1/ag1`, `rep1//ag1`, `rep1/ag1/`; `upgrade` is the usage
- two agents of the same name at two paths, `rep1/ag1` and `rep2/ag1`, are two agents: each woken
  in its own directory, the records say each path, the readings of one never show the other
- `list` descends the house: `ag2`, `agents/ag1`, `rep1/ag1`, `rep2/ag1`, by their paths
- a path where no agent stands refuses `agent-unknown`, naming the `agent add` that creates it
- two births of one path at once (batch l-equipe-et-son-journal, rework, agent 0.3.2): five races of
  two `agent add` on one new path -- each path born once, the other add refused `agent-exists`
"""
from __future__ import annotations

from pathlib import Path

from conductor import instance
from tests.harness import INSTANCE, race, support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
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
    added = h.call("agent", "add", "rep1/ag1")
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
    if (added.returncode == 0 and plain.returncode == 0 and all(seeds.values())
            and "rep1/ag1" in added.stdout and "ag2" in plain.stdout
            and "max_harness_tool_output 200000" in added.stdout and "max_harness_tool_output 200000" in plain.stdout):
        held("an agent is born at its path, the cap written", "agent add rep1/ag1 and agent add ag2: each borrows the "
             "house's machine, the seed of an interactive instance outside .sys but for `max_harness_tool_output: "
             "200000` at SETTINGS.md (said at the birth), no door, `pp`/`pp.cmd` beside it")
    else:
        failures.append(f"  ✗ agent add                   {added.returncode}/{plain.returncode} seeds={seeds} "
                        f"{added.stdout[-160:]!r} {added.stderr[-200:]!r} {plain.stderr[-200:]!r}")

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
        held("add refuses before writing", "agent-exists on rep1/ag1 again, type-unsupported on --type, "
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

    # --- two births of one path at once: one born, the other agent-exists (KC33) ----------------------
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
    return 0
