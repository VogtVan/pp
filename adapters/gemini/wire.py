"""The Gemini CLI adapter: the MARBLE mode over a replace-only host. Gemini has
no append flag -- `GEMINI_SYSTEM_MD` replaces the whole system prompt -- so the
"append" is a COMPOSITION: the host's own baseline, dumped by Gemini itself
(`GEMINI_WRITE_SYSTEM_MD`), with the standing rules appended after it. The
baseline is a snapshot: re-wire after a Gemini upgrade.

The `gemini-pp` launcher points `GEMINI_SYSTEM_MD` at the composition.

Written once, never overwritten: an existing `gemini-pp` or composition is the
operator's own.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

LAUNCHER = """#!/bin/sh
# Procedural Prompting -- the MARBLE mode launcher (generated once; yours to edit).
# Gemini's system prompt is replace-only: the "append" is a composition of the
# host's dumped baseline + the standing rules.
here="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$here/{meta}/.sys/system.replace.md" ]; then
  GEMINI_SYSTEM_MD="$here/{meta}/.sys/system.replace.md" PP_MARBLE=1 exec gemini "$@"
fi
GEMINI_SYSTEM_MD="$here/{meta}/.sys/system.gemini.md" PP_MARBLE=1 exec gemini "$@"
"""

CMD_LAUNCHER = """@echo off
rem Procedural Prompting -- the MARBLE mode launcher (generated once; yours to edit).
rem Gemini's system prompt is replace-only: the "append" is a composition of the
rem host's dumped baseline + the standing rules.
set "PP_MARBLE=1"
if exist "%~dp0{meta}\\.sys\\system.replace.md" (
  set "GEMINI_SYSTEM_MD=%~dp0{meta}\\.sys\\system.replace.md"
) else (
  set "GEMINI_SYSTEM_MD=%~dp0{meta}\\.sys\\system.gemini.md"
)
gemini %*
"""


def wire(workspace: Path, meta: Path) -> list[str]:
    """Dumps the host baseline (gemini itself writes it), composes baseline+marble,
    writes the door, the `/pp` command and the launcher. Gemini absent or silent:
    the miss is SAID, nothing hidden."""
    import sys
    sys.path.insert(0, str(meta / ".sys" / "engine"))
    from conductor import install
    made = []
    written = install.door(workspace, "GEMINI.md")
    if written:
        made.append(str(written))
    marble = meta / ".sys" / "system.md"
    if not marble.is_file():
        print("pp: no compiled marble under .sys -- nothing to wire, run `-build` first")
        return made
    composed = meta / ".sys" / "system.gemini.md"
    baseline = meta / ".sys" / "system.gemini.baseline.md"
    if baseline.is_file() and baseline.read_text(encoding="utf-8").strip():
        current = (baseline.read_text(encoding="utf-8").rstrip() + "\n\n"
                   + marble.read_text(encoding="utf-8"))
        if not composed.exists() or composed.read_text(encoding="utf-8") != current:
            composed.write_text(current, encoding="utf-8")
            made.append(f"{composed} recomposed on the current marble")
    elif composed.exists():
        print(f"pp: {composed} stands but its baseline is gone -- left untouched")
    elif shutil.which("gemini") is None:
        print("pp: REFUSED -- gemini-missing: the gemini CLI is not on PATH, "
              "no baseline to compose over")
    else:
        try:
            subprocess.run(["gemini", "--version"],
                           env={**os.environ, "GEMINI_WRITE_SYSTEM_MD": str(baseline)},
                           capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            pass
        if baseline.is_file() and baseline.read_text(encoding="utf-8").strip():
            composed.write_text(baseline.read_text(encoding="utf-8").rstrip() + "\n\n"
                                + marble.read_text(encoding="utf-8"), encoding="utf-8")
            made.append(str(composed))
        else:
            print("pp: WARNING -- gemini did not dump its baseline; compose it "
                  f"yourself: GEMINI_WRITE_SYSTEM_MD={baseline} gemini, then "
                  f"concatenate it with {marble} into {composed}")
    launcher = workspace / "gemini-pp"
    if launcher.exists():
        print(f"pp: {launcher} already exists -- left untouched")
    else:
        launcher.write_text(LAUNCHER.format(meta=meta.name), encoding="utf-8")
        launcher.chmod(0o755)
        made.append(str(launcher))
    twin = workspace / "gemini-pp.cmd"
    if twin.exists():
        print(f"pp: {twin} already exists -- left untouched")
    else:
        twin.write_text(CMD_LAUNCHER.format(meta=meta.name), encoding="utf-8")
        made.append(str(twin))
    command = workspace / ".gemini" / "commands" / "pp.toml"
    source = next((meta / ".sys" / "vendor").glob("kit@*/refs/PP.md"), None)
    if source is None:
        print("pp: no kit PP.md under vendor -- `/pp` not wired, run `-sync` first")
    else:
        text = source.read_text(encoding="utf-8")
        parts = text.split("---\n", 2)
        body = (parts[2] if len(parts) == 3 else text).strip()
        content = (
            "# Procedural Prompting -- the conductor's card as `/pp` (generated once; "
            "yours to edit).\n"
            'description = "The conductor of this workspace: what the tool is, what it '
            'never does, the protocol for its blocks"\n'
            'prompt = """\n' + body.replace('"""', "") + '\n"""\n')
        from conductor import install
        done = install.project(meta, command, content)
        if done:
            made.append(done)
    return made
