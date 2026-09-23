"""The Claude Code adapter: registers the conductor's card -- `PP.md`, the ONE
source the kit carries (served at boot to every harness), copied here into
`.claude/skills/pp/SKILL.md` so Claude Code lists it -- writes the MARBLE
mode launcher, `claude-pp` (the standing rules appended to the host's own
system prompt), and the PERMISSIONS (`.claude/settings.json`: a `Bash(./pp:*)`
allowlist entry -- the `:*` wildcard covers the run key and every argument).

Written once, never overwritten: an existing `.claude/skills/pp` or `claude-pp`
is the operator's own -- this only fills what is missing, and says what it skipped.
"""
from __future__ import annotations

import shutil
from pathlib import Path

LAUNCHER = """#!/bin/sh
# Procedural Prompting -- the MARBLE mode launcher (generated once; yours to edit).
# Appends the conducted workspace's standing rules to Claude Code's system prompt.
here="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$here/{meta}/.sys/system.replace.md" ]; then
  PP_MARBLE=1 exec claude --system-prompt-file "$here/{meta}/.sys/system.replace.md" "$@"
fi
PP_MARBLE=1 exec claude --append-system-prompt-file "$here/{meta}/.sys/system.md" "$@"
"""

CMD_LAUNCHER = """@echo off
rem Procedural Prompting -- the MARBLE mode launcher (generated once; yours to edit).
rem Appends the conducted workspace's standing rules to Claude Code's system prompt.
set "PP_MARBLE=1"
if exist "%~dp0{meta}\\.sys\\system.replace.md" (
  claude --system-prompt-file "%~dp0{meta}\\.sys\\system.replace.md" %*
) else (
  claude --append-system-prompt-file "%~dp0{meta}\\.sys\\system.md" %*
)
"""


SETTINGS = """{{
  "permissions": {{
    "allow": [
      "Bash(./pp:*)",
      "Bash(uv run {meta}/.sys/engine/pp.py:*)"
    ]
  }}
}}
"""


def wire(workspace: Path, meta: Path) -> list[str]:
    """`meta` is the instance dir `install` just seeded (e.g. `workspace/.pp`) --
    the card is copied from ITS pinned kit: the wired text is the served text."""
    import sys
    sys.path.insert(0, str(meta / ".sys" / "engine"))
    from conductor import install
    made = []
    written = install.door(workspace, "CLAUDE.md")
    if written:
        made.append(str(written))
    card = workspace / ".claude" / "skills" / "pp" / "SKILL.md"
    source = next((meta / ".sys" / "vendor").glob("kit@*/refs/PP.md"), None)
    if source is None:
        print("pp: no kit PP.md under vendor -- card not wired, run `-sync` first")
    else:
        from conductor import install
        done = install.project(meta, card, source.read_text(encoding="utf-8"))
        if done:
            made.append(done)
    launcher = workspace / "claude-pp"
    if launcher.exists():
        print(f"pp: {launcher} already exists -- left untouched")
    else:
        launcher.write_text(LAUNCHER.format(meta=meta.name), encoding="utf-8")
        launcher.chmod(0o755)
        made.append(str(launcher))
    twin = workspace / "claude-pp.cmd"
    if twin.exists():
        print(f"pp: {twin} already exists -- left untouched")
    else:
        twin.write_text(CMD_LAUNCHER.format(meta=meta.name), encoding="utf-8")
        made.append(str(twin))
    settings = workspace / ".claude" / "settings.json"
    if settings.exists():
        print(f"pp: {settings} already exists -- left untouched; allow the conductor "
              'yourself: add "Bash(./pp:*)" (and the repair path, "Bash(uv run '
              f'{meta.name}/.sys/engine/pp.py:*)") to permissions.allow')
    else:
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(SETTINGS.format(meta=meta.name), encoding="utf-8")
        made.append(str(settings))
    return made
