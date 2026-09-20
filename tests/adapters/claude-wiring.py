"""Scenario `claude-wiring` -- 1 case(s), in the monolith's order:
- `-claude` wires the adapter; re-installing never clobbers what is already there
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
import pp as pp_cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- `-claude` wires the adapter; re-installing never clobbers what is already there
    hamlet = Path(tempfile.mkdtemp())
    with contextlib.redirect_stdout(io.StringIO()):
        claude_rc = pp_cli.main(["-install", str(hamlet / "ws"), "-claude"])
    skill = hamlet / "ws" / ".claude" / "skills" / "pp" / "SKILL.md"
    settings_file = hamlet / "ws" / ".claude" / "settings.json"
    settings_text = (settings_file.read_text(encoding="utf-8")
                     if settings_file.is_file() else "")
    wired = (claude_rc == 0 and skill.is_file()
             and skill.read_bytes() == next(
                 (hamlet / "ws" / ".pp" / ".sys" / "vendor").glob("kit@*/refs/PP.md")).read_bytes()
             and "Bash(./pp:*)" in settings_text
             and ".pp/.sys/engine/pp.py:*" in settings_text
             and json.loads(settings_text))       # valid JSON, the allowlist in
    own = hamlet / "ws2" / ".claude" / "settings.json"
    own.parent.mkdir(parents=True)
    own.write_text('{"mine": true}', encoding="utf-8")   # the operator's own file
    with contextlib.redirect_stdout(io.StringIO()):
        pp_cli.main(["-install", str(hamlet / "ws2"), "-claude"])
    untouched = json.loads(own.read_text(encoding="utf-8")) == {"mine": True}
    if wired and untouched:
        held("-claude wires card and permissions", "the skill copied, Bash(./pp:*) allowed "
             "(the :* covers the run key) -- an operator's own settings stays untouched")
    else:
        failures.append(f"  ✗ -claude adapter           rc={claude_rc} wired={wired} untouched={untouched}")
    return 0
