"""The Cursor adapter: the CARD at the cross-vendor skills standard
(`.agents/skills/pp/`), which Cursor lists as an Agent Skill -- the doors
(`CLAUDE.md`/`AGENTS.md`) it reads natively are the install's own -- and the
PERMISSIONS (`.cursor/permissions.json`: a `terminalAllowlist` PREFIX on
`./pp`, so the variable run key and every argument pass unprompted). Cursor is
a multi-model harness: this one surface serves it whatever model runs
underneath, so there is nothing model-specific to wire. No system-prompt
channel exists on Cursor -- the guarantee is the recall.

Written once, never overwritten: an existing card is the operator's own.
"""
from __future__ import annotations

import shutil
from pathlib import Path


def wire(workspace: Path, meta: Path) -> list[str]:
    """`meta` is the instance dir `install` just seeded -- the card is copied from
    ITS pinned kit: the wired text is the served text. Cursor is multi-model, so it
    gets EVERY door: whatever context file the underlying stack looks for, it stands."""
    import sys
    sys.path.insert(0, str(meta / ".sys" / "engine"))
    from conductor import install
    made = []
    for name in install.DOORS:
        written = install.door(workspace, name)
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
    permissions = workspace / ".cursor" / "permissions.json"
    if permissions.exists():
        print(f"pp: {permissions} already exists -- left untouched; allow the "
              'conductor yourself: "./pp" in terminalAllowlist (a prefix)')
    else:
        permissions.parent.mkdir(parents=True, exist_ok=True)
        permissions.write_text('{\n  "terminalAllowlist": ["./pp"]\n}\n',
                               encoding="utf-8")
        made.append(str(permissions))
    return made
