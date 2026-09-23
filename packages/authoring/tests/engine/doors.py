"""Scenario `doors` -- 5 case(s), in the monolith's order:
- M0 les-portes-au-sol: the doors ride the floor, under B5
- M1 PP-MEMBER: the member takes shape -- from the root, under its own laws
- M2 PP-RULES: rules find their words and their scope
- M3 PP-OFFERS: the harness's skills become citizens
- M4 PP-MIGRATE: a standing system moves in -- the sisters offered inside
"""
from __future__ import annotations

import json
from pathlib import Path
from conductor import Conductor, render, compiling, discovery
from tests.harness import bench_key, SOURCE, body_of, kept_document, reaches



class Opened:
    """A door opened through the facade, read like the console would print it."""

    def __init__(self, block) -> None:
        self.returncode = 0 if block is not None else 2
        self.stdout = render(block) if block is not None else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- M0 les-portes-au-sol: the doors ride the floor, under B5 ---------------------
    mentor_made = bench.env("mws", packages=("authoring",)).made
    mentor_engine = mentor_made / ".sys" / "engine" / "pp.py"
    mentor_member = discovery.instance_member(mentor_engine)

    def mentor_c() -> Conductor:
        return Conductor(mentor_member, discovery.siblings_around(mentor_member), mentor_engine, "t")

    mentor_boot = mentor_c().start(mentor_c().boot("BOOT.md"))
    mentor_turn = mentor_c().submit("")
    if (all(any(one.name == door for one in mentor_boot.tools)
            for door in ("PP-MEMBER", "PP-RULES", "PP-OFFERS", "PP-MIGRATE", "PP-DESIGN"))
            and all(any(one.name == door for one in mentor_turn.tools)
                    for door in ("PP-MEMBER", "PP-DESIGN"))
            and not any(one.name == "pp-pp" for one in mentor_boot.tools)
            and any(one.code == "B5" for one in mentor_boot.constraints)
            and any(one.code == "B5" for one in mentor_turn.constraints)
            and not any(one.code in ("PM1", "PR1", "PO1", "PG1", "PD1")
                        for one in mentor_turn.constraints)):
        held("the doors ride the floor", "five doors offered on the boot block AND the "
             "turn's, under the root's B5 -- their own laws NOT in force until one opens")
    else:
        failures.append(f"  ✗ doors floor                 {[t.name for t in mentor_turn.tools]}")

    # --- M1 PP-MEMBER: the member takes shape -- from the root, under its own laws ----
    member_open = Opened(mentor_c().play("PP-MEMBER"))
    if (member_open.returncode == 0 and "▸ PP-MEMBER{" in member_open.stdout
            and "▸ pp-pp" not in member_open.stdout
            and "NEXT INSTRUCTION CONTEXT — PP-MEMBER" in member_open.stdout
            and "INFORMATION — AGENT" not in member_open.stdout
            and "PM4" in member_open.stdout and "B5" in member_open.stdout
            and "PM5" in member_open.stdout and "PM6" in member_open.stdout
            and reaches(member_open.stdout, body_of(kept_document(SOURCE / "packages" / "authoring", "PP-MEMBER")))
            and "serve-stale" in member_open.stdout
            and "weather-cli" in member_open.stdout and "atelier" in member_open.stdout):
        held("the member door opens from the root", "no mentor detour: the door stacks on "
             "the pending step, the current MEMBER proven at the boot renders nothing, the "
             "analysis covers, the ground poses or advises -- PM laws over the root's B5")
    else:
        failures.append(f"  ✗ member open                 rc={member_open.returncode} "
                        f"{member_open.stdout[:150]!r}")

    proving = mentor_c().submit("")     # the INFER said in chat -- the proving order follows
    full_proof = json.dumps([{"code": one.code, "evidence": "held through the shaping",
                              "verdict": "ok"} for one in proving.constraints])
    shaped_back = mentor_c().submit(full_proof)
    member_registry = compiling.render_registry(mentor_member.meta)
    if (proving.instruction.keyword == "PROVE"
            and any(one.code == "PM4" for one in proving.constraints)
            and shaped_back is not None and "PP-MEMBER" not in shaped_back.stack
            and "pp-pp" not in shaped_back.stack
            and "`PM1`" in member_registry and "`PM4`" in member_registry):
        held("the shaping proves and falls", "PROVE covers the PM codes; closed, the "
             "door leaves the stack and the turn resumes; PM registered one-holder")
    else:
        failures.append(f"  ✗ member prove                {proving.instruction} "
                        f"{shaped_back and shaped_back.stack!r}")
    mentor_c().submit("")                  # the door's closing advance, in process

    # --- M2 PP-RULES: rules find their words and their scope --------------------------
    rules_open = Opened(mentor_c().play("PP-RULES"))
    if (rules_open.returncode == 0 and "▸ PP-RULES{" in rules_open.stdout
            and "▸ pp-pp" not in rules_open.stdout
            and "INFORMATION — AGENT" not in rules_open.stdout
            and "INFORMATION — constraints" not in rules_open.stdout
            and reaches(rules_open.stdout, body_of(kept_document(SOURCE / "packages" / "authoring", "PP-RULES")))
            and "atelier" in rules_open.stdout):
        held("the rules door grounds itself", "opened from the root: the member proven at "
             "the boot renders nothing, and no register rides -- the code inventory is the "
             "script's; the counterweights and the atelier on screen")
    else:
        failures.append(f"  ✗ rules open                  rc={rules_open.returncode} "
                        f"{rules_open.stdout[:150]!r}")

    rules_proving = mentor_c().submit("")
    rules_proof = json.dumps([{"code": one.code, "evidence": "held while scoping",
                               "verdict": "ok"} for one in rules_proving.constraints])
    rules_back = mentor_c().submit(rules_proof)
    rules_registry = compiling.render_registry(mentor_member.meta)
    if (rules_proving.instruction.keyword == "PROVE"
            and any(one.code == "PR5" for one in rules_proving.constraints)
            and any(one.code == "PR6" for one in rules_proving.constraints)
            and rules_back is not None and "PP-RULES" not in rules_back.stack
            and "`PR1`" in rules_registry and "`PR7`" in rules_registry
            and "`PD1`" in rules_registry):
        held("the scoping proves and falls", "PROVE covers PR1-PR7, gate and grounding "
             "included; PR and PD registered one-holder; the door leaves the stack")
    else:
        failures.append(f"  ✗ rules prove                 {rules_proving.instruction} "
                        f"{rules_back and rules_back.stack!r}")
    mentor_c().submit("")                  # the door's closing advance, in process

    # --- M3 PP-OFFERS: the harness's skills become citizens ---------------------------
    offers_open = Opened(mentor_c().play("PP-OFFERS"))
    if (offers_open.returncode == 0 and "▸ PP-OFFERS{" in offers_open.stdout
            and "INFORMATION — tools" not in offers_open.stdout
            and reaches(offers_open.stdout, body_of(kept_document(SOURCE / "packages" / "authoring", "PP-OFFERS")))
            and "PO4" in offers_open.stdout and "▸ pp-pp" not in offers_open.stdout):
        held("the offers door reads the catalog", "opened from the root: tools.md, proven at "
             "the boot, renders nothing; the ladder, both placements and the receipt on screen")
    else:
        failures.append(f"  ✗ offers open                 rc={offers_open.returncode} "
                        f"{offers_open.stdout[:150]!r}")

    offers_proving = mentor_c().submit("")
    offers_proof = json.dumps([{"code": one.code, "evidence": "held while surveying",
                                "verdict": "ok"} for one in offers_proving.constraints])
    offers_back = mentor_c().submit(offers_proof)
    offers_registry = compiling.render_registry(mentor_member.meta)
    if (offers_proving.instruction.keyword == "PROVE"
            and any(one.code == "PO4" for one in offers_proving.constraints)
            and any(one.code == "B5" for one in offers_proving.constraints)
            and offers_back is not None and "PP-OFFERS" not in offers_back.stack
            and "`PO1`" in offers_registry and "`PO4`" in offers_registry):
        held("the offering proves and falls", "PROVE covers PO1-PO4 and the root's "
             "B5; PO registered one-holder; the door leaves the stack")
    else:
        failures.append(f"  ✗ offers prove                {offers_proving.instruction} "
                        f"{offers_back and offers_back.stack!r}")
    mentor_c().submit("")                  # the door's closing advance, in process

    # --- M4 PP-MIGRATE: a standing system moves in -- the sisters offered inside ------
    migrate_open = Opened(mentor_c().play("PP-MIGRATE"))
    migrate_tools = next((line for line in migrate_open.stdout.splitlines()
                          if line.startswith("[")), "")
    if (migrate_open.returncode == 0 and "▸ PP-MIGRATE{" in migrate_open.stdout
            and "INFORMATION — tools" not in migrate_open.stdout
            and "INFORMATION — constraints" not in migrate_open.stdout
            and "ESSENCE" in migrate_open.stdout
            and "collision" in migrate_open.stdout
            and "The sheet" in migrate_open.stdout
            and "PG5" in migrate_open.stdout and "PG7" in migrate_open.stdout
            and "▸ pp-pp" not in migrate_open.stdout
            and all(name in migrate_tools
                    for name in ("PP-MEMBER", "PP-RULES", "PP-OFFERS"))):
        held("the migrate door grounds itself", "opened from the root: the catalog "
             "baseline proven earlier in the run renders nothing; the map, essence, "
             "collisions, the sheet and its gate on screen; the three sisters offered inside")
    else:
        failures.append(f"  ✗ migrate open                rc={migrate_open.returncode} "
                        f"{migrate_tools!r} {migrate_open.stdout[:120]!r}")

    deep_open = Opened(mentor_c().play("PP-RULES"))
    deep_proving = mentor_c().submit("")
    if (deep_open.returncode == 0 and "▸ PP-MIGRATE ▸ PP-RULES{" in deep_open.stdout
            and deep_proving.instruction.keyword == "PROVE"
            and any(one.code == "PR5" for one in deep_proving.constraints)
            and any(one.code == "PG5" for one in deep_proving.constraints)):
        held("a sister stacks inside the migration", "PP-MIGRATE ▸ PP-RULES -- "
             "the depth holds, PG and PR both in force at the bottom")
    else:
        failures.append(f"  ✗ migrate depth               rc={deep_open.returncode} "
                        f"{deep_proving.instruction}")

    deep_proof = json.dumps([{"code": one.code, "evidence": "held at depth",
                              "verdict": "ok"} for one in deep_proving.constraints])
    mentor_c().submit(deep_proof)          # PP-RULES falls -> the migration's own INFER
    migrate_proving = mentor_c().submit("")
    migrate_proof = json.dumps([{"code": one.code, "evidence": "held while migrating",
                                 "verdict": "ok"} for one in migrate_proving.constraints])
    migrate_back = mentor_c().submit(migrate_proof)
    migrate_registry = compiling.render_registry(mentor_member.meta)
    if (migrate_proving.instruction.keyword == "PROVE"
            and any(one.code == "PG6" for one in migrate_proving.constraints)
            and migrate_back is not None and "PP-MIGRATE" not in migrate_back.stack
            and "`PG1`" in migrate_registry and "`PG6`" in migrate_registry):
        held("the migration proves and falls", "PROVE covers PG1-PG6; PG registered "
             "one-holder; the door leaves the stack")
    else:
        failures.append(f"  ✗ migrate prove               {migrate_proving.instruction} "
                        f"{migrate_back and migrate_back.stack!r}")
    mentor_c().submit("")                  # the door's closing advance, in process
    return 0
