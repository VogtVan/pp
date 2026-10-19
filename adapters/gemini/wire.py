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


COMPOSITIONS = (("system.md", "system.gemini.md"),                 # the marble a run the LLM conducts carries
                ("system.common.md", "system.common.gemini.md"))   # the marble of a run its principal conducts


def _composed(marble: Path, composition: Path, baseline: Path, made: list[str]) -> None:
    """Writes `composition` -- the baseline, a blank line, `marble` -- when the marble
    stands and the composition differs; a marble the build did not compile composes
    nothing."""
    if not marble.is_file():
        return
    current = baseline.read_text(encoding="utf-8").rstrip() + "\n\n" + marble.read_text(encoding="utf-8")
    if not composition.exists() or composition.read_text(encoding="utf-8") != current:
        composition.write_text(current, encoding="utf-8")
        made.append(f"{composition} composed on the current marble")


def wire(workspace: Path, meta: Path) -> list[str]:
    """Dumps the host baseline (gemini itself writes it), composes baseline+marble --
    one composition per marble the build compiled: `system.gemini.md` and, since the
    two marbles, `system.common.gemini.md` --, writes the door, the `/pp` command and
    the launcher. Gemini absent or silent: the miss is SAID, nothing hidden."""
    import sys
    from conductor import install, instance      # the engine loading this adapter
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
        for one, composition in COMPOSITIONS:          # each marble the build compiled, its composition
            _composed(meta / ".sys" / one, meta / ".sys" / composition, baseline, made)
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
            for one, composition in COMPOSITIONS:
                _composed(meta / ".sys" / one, meta / ".sys" / composition, baseline, made)
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
    source = install.card(meta)   # the card a harness receives: the engine's, then its SYSTEM.CONDUCT.md
    if source is None:
        print("pp: no PP.md under the engine's refs -- `/pp` not wired, run `-sync` first")
    else:
        text = source
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


SPELLS = ("model",)   # the policy's keys `launch` spells
MODELS = ()           # no model name verified on a machine yet; any name passes as given
COST = None           # the scope of the cost `answer` reads: none -- the stream reports no cost


def launch(workspace: Path, meta: Path, marble: Path | None, prompt: str,
           wiring: Path | None = None, policy: dict | None = None,
           session: str | None = None, workdir: dict | None = None) -> tuple[list[str], dict[str, str], str]:
    """The non-interactive face: the command line that plays ONE exchange of a session
    and exits, composed, never run. No `session` opens one; a session is resumed by
    `--resume <id>`. `workdir`, the material the exchange works on, is taken and changes
    nothing here: it is under the workspace, where gemini writes already -- the face
    composed its head and its variables. The system prompt travels by the variable `GEMINI_SYSTEM_MD` at
    EVERY launch, the resume included: the process reads it, and a resumed session
    restores the conversation, not the system prompt. As `gemini-pp` sets it: `marble`
    None takes the replace artifact when it stands, the
    composition (baseline + standing rules) otherwise; a marble handed names ITS
    composition when `wire()` composed one beside it (`system.common.md` ->
    `system.common.gemini.md`), the file itself otherwise; the receipt rides `env` too. The
    model is spelled `-m`; a budget and an effort have no flag here (the effort is a setting's
    `thinkingConfig`, never a flag of the call) and the regime is `auto` alone
    (`policy-unsupported`); `wiring` is not read: `--approval-mode yolo` needs no allowlist.
    The prompt goes on stdin -- the headless mode reads it there without `-p` (read in the
    docs, not verified on a machine). The output is the STREAM (`--output-format stream-json`):
    one JSON event per line -- `events` reads each line, `answer` the whole (read in the docs,
    NOT verified on a machine)."""
    if marble is None:
        replace = meta / ".sys" / "system.replace.md"
        marble = replace if replace.is_file() else meta / ".sys" / "system.gemini.md"
    else:
        composition = next((Path(marble).with_name(one) for name, one in COMPOSITIONS
                            if Path(marble).name == name and Path(marble).with_name(one).is_file()), None)
        marble = composition if composition is not None else marble
    policy = _spellable(policy, "gemini")
    argv = ["gemini"] + (["--resume", session] if session else []) + [
            "--approval-mode", "yolo", "--output-format", "stream-json"]
    if "model" in policy:
        argv += ["-m", policy["model"]]
    return argv, {"GEMINI_SYSTEM_MD": str(marble), "PP_MARBLE": "1"}, prompt

def _spellable(policy: dict | None, provider: str) -> dict:
    """-> the policy this host can spell: the model, and the `auto` regime its line plays --
    a budget, or a regime other than `auto`, refuses `policy-unsupported`, the provider and
    the key named (no such flag at its CLI, or no other mode verified on a machine)."""
    from conductor.core.errors import Refusal
    policy = policy or {}
    if "max_budget_usd" in policy:
        raise Refusal("policy-unsupported",
                      f"`{provider}` cannot spell `max_budget_usd` -- its CLI has no budget flag")
    if "effort" in policy:
        raise Refusal("policy-unsupported",
                      f"`{provider}` cannot spell `effort` -- its CLI has no effort flag (a setting's thinkingConfig)")
    if policy.get("permissions", "auto") != "auto":
        raise Refusal("policy-unsupported",
                      f"`{provider}` cannot spell `permissions: {policy['permissions']}` -- its line plays "
                      "`auto` alone, no other mode verified on a machine")
    return policy



def answer(stdout: str, stderr: str) -> dict:
    """The reading of ONE exchange's answer, on the stream `launch()` asks for: the session's
    identity the `session_id` of the `init` event, the error what an `error` event or a
    `result` whose `status` is `error` names -- or, from `--output-format json`, the one
    object's `session_id` and `error`; gemini reports no cost and no denial. The assistant's
    `message` events are not read here: they are `words`, `events` reads them. A stdout that
    is neither is unreadable: the error says so and cites its tail. Read in the docs, NOT
    verified on a machine."""
    import json
    try:
        whole = json.loads(stdout)
    except ValueError:
        whole = None
    if isinstance(whole, dict) and "type" not in whole:
        failed = whole.get("error")
        error = (str(failed.get("message") or failed) if isinstance(failed, dict) else str(failed)) if failed else None
        return {"cost_usd": None, "denials": [], "error": error,
                "session": str(whole.get("session_id") or "").strip() or None}
    session, error, read = None, None, False
    for line in str(stdout).splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        read = True
        kind = event.get("type")
        if kind == "init":
            session = str(event.get("session_id") or "").strip() or None
        elif kind == "error" or (kind == "result" and event.get("status") == "error"):
            failed = event.get("error") if kind == "result" else event
            error = str(failed.get("message") or failed) if isinstance(failed, dict) else str(failed or "error")
    if not read:
        return {"cost_usd": None, "denials": [],
                "error": f"unreadable: {(stdout or stderr).strip()[-300:]}", "session": None}
    return {"cost_usd": None, "denials": [], "error": error, "session": session}


def events(line: str) -> list[dict]:
    """ONE line of the stream -> its events in the common schema (`conductor.adapters.events`): a
    `tool_use` is a `tool` (`shell` the `command` of a `run_shell_command`), a `tool_result` its
    `tool-result` (an error when its `status` is not `success`), an assistant's `message` `words` -- a
    `delta` one a piece of the message under way, `delta` said.
    Read in the docs, NOT verified on a machine (the CLI is absent here)."""
    import json
    try:
        data = json.loads(line)
    except ValueError:
        return []
    if not isinstance(data, dict):
        return []
    kind = data.get("type")
    if kind == "tool_use":
        given = data.get("parameters") if isinstance(data.get("parameters"), dict) else {}
        name = str(data.get("tool_name") or "")
        command = given.get("command") if name == "run_shell_command" else None
        title = next((given[key] for key in ("command", "absolute_path", "file_path", "path", "pattern")
                      if isinstance(given.get(key), str)), "")
        return [{"kind": "tool", "id": str(data.get("tool_id") or ""), "name": name,
                 "title": " ".join(str(title).split())[:200],
                 "shell": command if isinstance(command, str) else None, "input": given}]
    if kind == "tool_result":
        failed = data.get("error")
        content = str(data.get("output") or "") or (str(failed.get("message") or "") if isinstance(failed, dict) else "")
        return [{"kind": "tool-result", "id": str(data.get("tool_id") or ""), "content": content,
                 "error": data.get("status") != "success"}]
    if kind == "message" and data.get("role") == "assistant" and str(data.get("content") or "").strip():
        return [{"kind": "words", "text": str(data["content"]), **({"delta": True} if data.get("delta") is True else {})}]
    return []
