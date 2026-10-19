"""Scenario `authoring-doors` -- the authoring package's doors, on the boot and the turn:
- the five doors ride the floor under the root's B5, `pp-authoring` beside them on the
  turn; their own laws wait until one opens
- PP-MEMBER, PP-RULES, PP-OFFERS each open from the root with their body on screen,
  prove their codes and fall from the stack
- PP-MIGRATE opens with the three sisters offered inside; a sister stacks under it, and
  the migration proves and falls
- the package's overlays compose with the instance's own: a TURN overlay adds a tool
  beside the package's, an overlay on PP-MEMBER appends its section after the door's body
- the kit alone offers none of the doors

Two houses: the instance with authoring, and the kit alone for the absence.
"""
from __future__ import annotations

import json

from conductor import compiling, render
from tests.harness import SOURCE, body_of, kept_document, reaches

DOORS = ("PP-MEMBER", "PP-RULES", "PP-OFFERS", "PP-MIGRATE", "PP-DESIGN")
AUTHORING = SOURCE / "packages" / "authoring"


class Opened:
    """A door opened through the facade, read like the console would print it."""

    def __init__(self, block) -> None:
        self.returncode = 0 if block is not None else 2
        self.stdout = render(block) if block is not None else ""


def _names(block) -> set[str]:
    return {one.name for one in block.tools} if block is not None else set()


def _blocks(env):
    """-> (the boot block, the turn block) of a fresh run on `env`."""
    conductor = env.conductor()
    boot = conductor.start(conductor.boot("BOOT.md"))
    turn = env.conductor().submit("")
    return boot, turn


def _body(name: str) -> str:
    return body_of(kept_document(AUTHORING, name))


def _proof(block, evidence: str) -> str:
    return json.dumps([{"code": one.code, "evidence": evidence, "verdict": "ok"}
                       for one in block.constraints])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("doors", packages=("authoring",))

    def c():
        return env.conductor("t")

    # --- the floor: five doors offered, their laws waiting ----------------------------
    boot = c().start(c().boot("BOOT.md"))
    turn = c().submit("")
    if (set(DOORS) <= _names(boot)
            and {"PP-MEMBER", "PP-DESIGN", "pp-authoring"} <= _names(turn)
            and "pp-pp" not in _names(boot)
            and any(one.code == "B5" for one in boot.constraints)
            and any(one.code == "B5" for one in turn.constraints)
            and not any(one.code in ("PM1", "PR1", "PO1", "PG1", "PD1")
                        for one in turn.constraints)):
        held("the doors ride the floor", "five doors offered on the boot block AND the "
             "turn's, pp-authoring on the turn, under the root's B5 -- their own laws NOT "
             "in force until one opens")
    else:
        failures.append(f"  ✗ doors floor                 boot={sorted(_names(boot))} "
                        f"turn={sorted(_names(turn))}")

    # --- PP-MEMBER: the member takes shape, from the root, under its own laws ---------
    member_open = Opened(c().play("PP-MEMBER"))
    if (member_open.returncode == 0 and "▸ PP-MEMBER{" in member_open.stdout
            and "▸ pp-pp" not in member_open.stdout
            and "NEXT INSTRUCTION CONTEXT — PP-MEMBER" in member_open.stdout
            and "INFORMATION — AGENT" not in member_open.stdout
            and all(code in member_open.stdout for code in ("PM4", "PM5", "PM6", "B5"))
            and reaches(member_open.stdout, _body("PP-MEMBER"))):
        held("the member door opens from the root", "no mentor detour: the door stacks on "
             "the pending step, the current MEMBER proven at the boot renders nothing, the "
             "door's body on screen -- PM laws over the root's B5")
    else:
        failures.append(f"  ✗ member open                 rc={member_open.returncode} "
                        f"{member_open.stdout[:150]!r}")

    proving = c().submit("")               # the INFER said in chat -- the proving order follows
    shaped_back = c().submit(_proof(proving, "held through the shaping"))
    registry = compiling.render_registry(env.member.meta)
    if (proving.instruction.keyword == "PROVE"
            and any(one.code == "PM4" for one in proving.constraints)
            and shaped_back is not None and "PP-MEMBER" not in shaped_back.stack
            and "pp-pp" not in shaped_back.stack
            and "`PM1`" in registry and "`PM4`" in registry):
        held("the shaping proves and falls", "PROVE covers the PM codes; closed, the "
             "door leaves the stack and the turn resumes; PM registered one-holder")
    else:
        failures.append(f"  ✗ member prove                {proving.instruction} "
                        f"{shaped_back and shaped_back.stack!r}")
    c().submit("")                         # the door's closing advance

    # --- PP-RULES: rules find their words and their scope -----------------------------
    rules_open = Opened(c().play("PP-RULES"))
    if (rules_open.returncode == 0 and "▸ PP-RULES{" in rules_open.stdout
            and "▸ pp-pp" not in rules_open.stdout
            and "INFORMATION — AGENT" not in rules_open.stdout
            and "INFORMATION — constraints" not in rules_open.stdout
            and reaches(rules_open.stdout, _body("PP-RULES"))):
        held("the rules door grounds itself", "opened from the root: the member proven at "
             "the boot renders nothing, and no register rides -- the code inventory is the "
             "script's; the door's body on screen")
    else:
        failures.append(f"  ✗ rules open                  rc={rules_open.returncode} "
                        f"{rules_open.stdout[:150]!r}")

    rules_proving = c().submit("")
    rules_back = c().submit(_proof(rules_proving, "held while scoping"))
    registry = compiling.render_registry(env.member.meta)
    if (rules_proving.instruction.keyword == "PROVE"
            and any(one.code == "PR5" for one in rules_proving.constraints)
            and any(one.code == "PR6" for one in rules_proving.constraints)
            and rules_back is not None and "PP-RULES" not in rules_back.stack
            and "`PR1`" in registry and "`PR7`" in registry and "`PD1`" in registry):
        held("the scoping proves and falls", "PROVE covers PR1-PR7, gate and grounding "
             "included; PR and PD registered one-holder; the door leaves the stack")
    else:
        failures.append(f"  ✗ rules prove                 {rules_proving.instruction} "
                        f"{rules_back and rules_back.stack!r}")
    c().submit("")                         # the door's closing advance

    # --- PP-OFFERS: the harness's skills become citizens ------------------------------
    offers_open = Opened(c().play("PP-OFFERS"))
    if (offers_open.returncode == 0 and "▸ PP-OFFERS{" in offers_open.stdout
            and "INFORMATION — tools" not in offers_open.stdout
            and reaches(offers_open.stdout, _body("PP-OFFERS"))
            and "PO4" in offers_open.stdout and "▸ pp-pp" not in offers_open.stdout):
        held("the offers door reads the catalog", "opened from the root: tools.md, proven at "
             "the boot, renders nothing; the door's body and PO4 on screen")
    else:
        failures.append(f"  ✗ offers open                 rc={offers_open.returncode} "
                        f"{offers_open.stdout[:150]!r}")

    offers_proving = c().submit("")
    offers_back = c().submit(_proof(offers_proving, "held while surveying"))
    registry = compiling.render_registry(env.member.meta)
    if (offers_proving.instruction.keyword == "PROVE"
            and any(one.code == "PO4" for one in offers_proving.constraints)
            and any(one.code == "B5" for one in offers_proving.constraints)
            and offers_back is not None and "PP-OFFERS" not in offers_back.stack
            and "`PO1`" in registry and "`PO4`" in registry):
        held("the offering proves and falls", "PROVE covers PO1-PO4 and the root's "
             "B5; PO registered one-holder; the door leaves the stack")
    else:
        failures.append(f"  ✗ offers prove                {offers_proving.instruction} "
                        f"{offers_back and offers_back.stack!r}")
    c().submit("")                         # the door's closing advance

    # --- PP-MIGRATE: a standing system moves in, the sisters offered inside -----------
    migrate_open = Opened(c().play("PP-MIGRATE"))
    migrate_tools = next((line for line in migrate_open.stdout.splitlines()
                          if line.startswith("[")), "")
    if (migrate_open.returncode == 0 and "▸ PP-MIGRATE{" in migrate_open.stdout
            and "INFORMATION — tools" not in migrate_open.stdout
            and "INFORMATION — constraints" not in migrate_open.stdout
            and reaches(migrate_open.stdout, _body("PP-MIGRATE"))
            and "PG5" in migrate_open.stdout and "PG7" in migrate_open.stdout
            and "▸ pp-pp" not in migrate_open.stdout
            and all(name in migrate_tools for name in ("PP-MEMBER", "PP-RULES", "PP-OFFERS"))):
        held("the migrate door grounds itself", "opened from the root: the catalog "
             "baseline proven earlier in the run renders nothing; the door's body, PG5 and "
             "PG7 on screen; the three sisters offered inside")
    else:
        failures.append(f"  ✗ migrate open                rc={migrate_open.returncode} "
                        f"{migrate_tools!r} {migrate_open.stdout[:120]!r}")

    deep_open = Opened(c().play("PP-RULES"))
    deep_proving = c().submit("")
    if (deep_open.returncode == 0 and "▸ PP-MIGRATE ▸ PP-RULES{" in deep_open.stdout
            and deep_proving.instruction.keyword == "PROVE"
            and any(one.code == "PR5" for one in deep_proving.constraints)
            and any(one.code == "PG5" for one in deep_proving.constraints)):
        held("a sister stacks inside the migration", "PP-MIGRATE ▸ PP-RULES -- "
             "the depth holds, PG and PR both in force at the bottom")
    else:
        failures.append(f"  ✗ migrate depth               rc={deep_open.returncode} "
                        f"{deep_proving.instruction}")

    c().submit(_proof(deep_proving, "held at depth"))   # PP-RULES falls -> the migration's INFER
    migrate_proving = c().submit("")
    migrate_back = c().submit(_proof(migrate_proving, "held while migrating"))
    registry = compiling.render_registry(env.member.meta)
    if (migrate_proving.instruction.keyword == "PROVE"
            and any(one.code == "PG6" for one in migrate_proving.constraints)
            and migrate_back is not None and "PP-MIGRATE" not in migrate_back.stack
            and "`PG1`" in registry and "`PG6`" in registry):
        held("the migration proves and falls", "PROVE covers PG1-PG6; PG registered "
             "one-holder; the door leaves the stack")
    else:
        failures.append(f"  ✗ migrate prove               {migrate_proving.instruction} "
                        f"{migrate_back and migrate_back.stack!r}")
    c().submit("")                         # the door's closing advance
    c().forget()

    # --- the overlays compose: the instance's own beside the package's ----------------
    env.write("procs/TURN.md", "---\nname: TURN\ntools: |\n  +TAGGED\n---\n")
    env.write("TAGGED.md", "---\nname: TAGGED\ndescription: a tool of the instance\n---\nmatter\n")
    env.write("procs/PP-MEMBER.md", "---\nname: PP-MEMBER\n---\n\n## The section an overlay "
              "hands back\n\nmatter of the overlay\n")
    _, layered_turn = _blocks(env)
    layered = _names(layered_turn)
    if {"TAGGED", "pp-authoring", "PP-DESIGN"} <= layered:
        held("the overlays compose across spaces", "TURN offers TAGGED (the instance's "
             "overlay) and pp-authoring, PP-DESIGN (authoring's) at once")
    else:
        failures.append(f"  ✗ offers compose             {sorted(layered)}")

    served = render(env.conductor().play("PP-MEMBER"))
    env.conductor().forget()
    last_heading = [line[3:] for line in _body("PP-MEMBER").splitlines()
                    if line.startswith("## ")][-1]
    if (last_heading in served and "matter of the overlay" in served
            and served.index(last_heading) < served.index("matter of the overlay")):
        held("an overlay appends its section at the end", "the instance's overlay on PP-MEMBER "
             "rides after the base body")
    else:
        failures.append(f"  ✗ member overlay             {served[-300:]!r}")

    # --- the kit alone: the absence ---------------------------------------------------
    bare_boot, bare_turn = _blocks(bench.env("doors-kit"))
    bare = _names(bare_boot) | _names(bare_turn)
    if not (bare & (set(DOORS) | {"pp-authoring"})):
        held("the kit alone offers no author tool", f"boot+turn: {sorted(bare) or 'nothing'}")
    else:
        failures.append(f"  ✗ offers without authoring   {sorted(bare)}")
    return 0
