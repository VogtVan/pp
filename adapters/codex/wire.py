"""The Codex CLI adapter: the full surface. Codex reads `AGENTS.md` natively --
the door already stands -- so this wires the rest: the CARD at the cross-vendor
skills standard (`.agents/skills/pp/` -- Codex reads it, and so does Cursor), the
MARBLE (`.codex/config.toml`, `developer_instructions` -- the key that APPENDS to
Codex's own instructions), and the PERMISSIONS path (`.codex/rules/default.rules`, a prefix rule on
the conductor's own invocation -- verify it with `codex execpolicy check`).

Written once, never overwritten: whatever already exists is the operator's own --
this says what to add instead of touching it.
"""
from __future__ import annotations

import shutil
from pathlib import Path

HEADER = """# Procedural Prompting -- the MARBLE mode (generated once; yours to edit).
# `developer_instructions` APPENDS the conducted workspace's standing rules to
# Codex's own instructions.
"""

RULES = """# Procedural Prompting -- frictionless approval for the conductor
# (generated once; yours to edit). Verify with: codex execpolicy check
# The blocks speak the console; the long form is the repair path.
prefix_rule(
    pattern = ["./pp"],
)
prefix_rule(
    pattern = ["uv", "run", "{meta}/.sys/engine/pp.py"],
)
"""


def wire(workspace: Path, meta: Path) -> list[str]:
    """`meta` is the instance dir `install` just seeded -- the card comes from ITS
    pinned kit, the marble from ITS compiled artifact: wired text = built text."""
    import sys
    sys.path.insert(0, str(meta / ".sys" / "engine"))
    from conductor import install
    made = []
    written = install.door(workspace, "AGENTS.md")
    if written:
        made.append(str(written))
    card = workspace / ".agents" / "skills" / "pp" / "SKILL.md"
    source = next((meta / ".sys" / "vendor").glob("kit@*/refs/PP.md"), None)
    if source is None:
        print("pp: no kit PP.md under vendor -- card not wired, run `-sync` first")
    else:
        from conductor import install
        done = install.project(meta, card, source.read_text(encoding="utf-8"))
        if done:
            made.append(done)
    marble = meta / ".sys" / "system.md"
    config = workspace / ".codex" / "config.toml"
    if not marble.is_file():
        print("pp: no compiled marble under .sys -- config not wired, run `-build` first")
    else:
        text = marble.read_text(encoding="utf-8").replace("\\", "\\\\").replace('"""', "")
        content = (HEADER.format(meta=meta.name)
                   + 'developer_instructions = """\n' + text.rstrip() + '\n"""\n'
                   + '\n[shell_environment_policy]\nset = { PP_MARBLE = "1" }\n')
        from conductor import install
        if config.exists():
            done = install.merge_codex_config(meta, config, text.rstrip(), content)
        else:
            done = install.project(meta, config, content)
            install.merge_codex_config(meta, config, text.rstrip(), content)  # records the
            # managed field's provenance so a later merge can tell OUR value apart
        if done:
            made.append(done)
            if "candidate" in done:
                print("pp: WARNING -- PP_MARBLE may certify a stale marble in the "
                      "edited config: align developer_instructions with "
                      f"{meta.name}/.sys/system.md, or drop the sentinel")
    rules = workspace / ".codex" / "rules" / "default.rules"
    if rules.exists():
        print(f"pp: {rules} already exists -- left untouched; allow the conductor "
              f"yourself: a prefix rule on `./pp` (and on `uv run "
              f"{meta.name}/.sys/engine/pp.py`, the repair path)")
    else:
        rules.parent.mkdir(parents=True, exist_ok=True)
        rules.write_text(RULES.format(meta=meta.name), encoding="utf-8")
        made.append(str(rules))
        print("pp: verify the generated rule with `codex execpolicy check`")
    return made
