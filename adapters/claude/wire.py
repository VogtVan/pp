"""The Claude Code adapter: registers the conductor's card -- the engine's two cards and
its SYSTEM.CONDUCT.md (`install.card`, served at boot to every harness), copied here into
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
      "Bash(uv run {engine}:*)"
    ]
  }},
  "env": {{
    "PP_MARBLE": "1"
  }}
}}
"""   # `engine`: the repair path the launcher runs, under the instance; `env`: the receipt the
      # editor's extension carries -- no launcher runs there, the settings file is the one channel
      # for a variable, and the card the extension lists holds the standing rules already

SPELLS = ("model", "max_budget_usd", "permissions", "effort")   # the policy's keys `launch` spells
MODELS = ("claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5",   # the model names verified on a
          "claude-haiku-4-5-20251001")                                  # machine; any other name passes as given
CONTEXT_WINDOWS = {   # the context window of a model, in tokens, under every name `--model` takes for it -- the id
    # and the CLI's alias: the 1M models read at platform.claude.com/docs/en/models/overview on 2026-10-29 (opus 5.5
    # also seen in the stream, `modelUsage.contextWindow`, 2026-10-28; sonnet 5.5 measured 2026-10-28: 1 200 196
    # characters piped, 466 825 tokens, answered); `haiku` at 200K measured 2026-10-27 (`claude -p --model haiku`
    # refused ~282 505 tokens: « limit 200 000 »)
    "claude-fable-5-1": 1_000_000, "fable": 1_000_000,
    "claude-opus-5-5": 1_000_000, "opus": 1_000_000,
    "claude-sonnet-5-5": 1_000_000, "sonnet": 1_000_000,
    "claude-haiku-5-5": 1_000_000,
    "claude-haiku-4-5-20251001": 200_000, "haiku": 200_000,
}
CHARS_PER_TOKEN = 2.5   # « 1M tokens is roughly … 2.5M Unicode characters on the current tokenizer » (platform.claude.com,
                        # 2026-10-29); 2.57 measured on a block of pp, 2026-10-28
PROBED = ((1_499_977, 395_182), (2_699_964, 703_212))   # piped to `claude -p --model sonnet` on 2.1.287, 2026-10-29:
                        # (characters, tokens created in cache) -- both read whole in one request, neither refused; the
                        # ~1.78x count of a piped prompt reported at anthropics/claude-code #92305 (2.1.259-261) is NOT
                        # observed on 2.1.287: 703 212 tokens x 1.78 would have passed the 1M window
SHARE = 0.8             # the share of the window one prompt may take: the rest for the system prompt, the tools, the answer
CAP = None              # the client bounds a piped prompt at 10 485 760 characters (« piped stdin input exceeds 10MB »,
                        # 2.1.128+), far above any window: without a model named, no cap -- the engine's floor holds
CAPS = {name: int(window * CHARS_PER_TOKEN * SHARE)   # the cap of a prompt, in characters, by model name:
        for name, window in CONTEXT_WINDOWS.items()}   # 2 000 000 at 1M, 400 000 at 200K
COST = "session"   # the scope of the cost `answer` reads: `total_cost_usd`, the session's cumul at that launch
# The estimate of a run's context where no call measured it (`agent calibrate` fits them on the house's runs): the
# tokens of a session's first call -- the system prompt, the tools, the standing orders --, the weight of a token the
# engine estimates in the model's tokenizer, the part of the model's thinking the context keeps. Fitted on 2026-10-29
# over 106 runs of the house without a compaction (claude 2.1.287, opus and fable): median gap 7 %, p90 89 %.
CONTEXT_BASE = 90_354
FLOW_RATIO = 1.5
THINKING_KEPT = 0.0
STORE_ENV = "CLAUDE_CONFIG_DIR"   # the variable that moves the CLI's own store -- its sessions under projects/
BINARY = "claude"            # the binary a launch needs on the machine: the CLI `claude -p` plays

PERMISSION_MODES = {                 # the policy's regime -> claude's --permission-mode
    "auto": "auto",                  # the harness's own judgment, the mode of an interactive session
    "strict": "dontAsk",             # the rules written at the settings alone; anything else denied
    "bypass": "bypassPermissions",   # every check skipped -- a container or a VM without a network
}


def wire(workspace: Path, meta: Path) -> list[str]:
    """`meta` is the instance dir `install` just seeded (e.g. `workspace/.pp`) --
    the card is copied from ITS engine: the wired text is the served text."""
    import sys
    from conductor import install, instance      # the engine loading this adapter
    made = []
    written = install.door(workspace, "CLAUDE.md")
    if written:
        made.append(str(written))
    elif install.door_kept(workspace, "CLAUDE.md"):
        print(install.door_kept(workspace, "CLAUDE.md"))
    card = workspace / ".claude" / "skills" / "pp" / "SKILL.md"
    source = install.card(meta)   # the card a harness receives: the engine's two cards, then its SYSTEM.CONDUCT.md
    if source is None:
        print("pp: no card under the engine's refs -- card not wired, run `-sync` first")
    else:
        from conductor import install
        done = install.project(meta, card, source)
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
              f'{install.engine_invocation(meta)}:*)") to permissions.allow')
    else:
        settings.parent.mkdir(parents=True, exist_ok=True)
        settings.write_text(SETTINGS.format(engine=install.engine_invocation(meta)), encoding="utf-8")
        made.append(str(settings))
    return made


def launch(workspace: Path, meta: Path, marble: Path | None, prompt: str,
           wiring: Path | None = None, policy: dict | None = None,
           session: str | None = None, workdir: dict | None = None) -> tuple[list[str], dict[str, str], str]:
    """The non-interactive face: the command line that plays ONE exchange of a session
    and exits, composed, never run. No `session` opens one, which claude keeps and names
    (`session_id`); a session is resumed by `--resume <id>`. `workdir`, the material the
    exchange works on, is taken and changes nothing here: it is under the workspace,
    where claude writes already -- the face composed its head and its variables. The marble rides EVERY
    launch, the resume included: claude records the system prompt in its session only
    where its snapshot is enabled, and drops the record at a compaction -- handed again,
    it changes nothing where the record holds and restores it where it does not.
    `marble` None takes what `claude-pp` carries -- the replace
    artifact when it stands, the compiled marble otherwise -- and the flag follows the
    file: `--system-prompt-file` replaces, `--append-system-prompt-file` appends; a
    marble handed (the marble of the run's mode) rides the same flag. The
    policy is spelled as claude names it (`--model`, `--max-budget-usd`, the regime by
    `--permission-mode` from `PERMISSION_MODES`, `auto` without one, the effort by
    `--effort`, pp's five words being claude's own); the wiring
    is handed by `--settings <wiring>/.claude/settings.json` when that file stands --
    the permissions the home wrote once, read by a process running elsewhere. The
    prompt goes on stdin -- `claude -p` without a prompt argument reads it there
    (`--input-format text`, the default) --; the receipt rides `env`. The output is the STREAM
    (`--output-format stream-json --verbose`, verified on claude 2.1.287): one JSON object per
    line as the exchange plays, the `result` line last -- `events` reads each line, `answer` the
    last."""
    if marble is None:
        replace = meta / ".sys" / "system.replace.md"
        marble = replace if replace.is_file() else meta / ".sys" / "system.md"
    flag = ("--system-prompt-file" if Path(marble).name == "system.replace.md"
            else "--append-system-prompt-file")
    policy = policy or {}
    argv = ["claude", "-p"] + (["--resume", session] if session else []) + [
            flag, str(marble),
            "--permission-mode", PERMISSION_MODES[policy.get("permissions", "auto")],
            "--permission-prompts", "none",
            "--output-format", "stream-json", "--verbose"]
    if "model" in policy:
        argv += ["--model", policy["model"]]
    if "max_budget_usd" in policy:
        argv += ["--max-budget-usd", f"{policy['max_budget_usd']:g}"]
    if "effort" in policy:
        argv += ["--effort", policy["effort"]]
    if wiring is not None:
        settings = Path(wiring) / ".claude" / "settings.json"
        if settings.is_file():
            argv += ["--settings", str(settings)]
    return argv, {"PP_MARBLE": "1"}, prompt


def answer(stdout: str, stderr: str) -> dict:
    """The reading of ONE exchange's answer, on the stream `launch()` asks for: its LAST
    `result` line -- or the one object `--output-format json` renders -- whose
    `total_cost_usd` is the cost the CLI reports (list price), `permission_denials` the tools
    it was denied, `session_id` the session's identity; `is_error` names its `subtype` as the
    error. Its `result`, the assistant's last message, is not read: the stream said it as a
    `text` block, `events` reads it there. A stdout with no such object is unreadable: the
    error says so and cites its tail."""
    read = _result_of(stdout)
    if read is None:
        return {"cost_usd": None, "denials": [],
                "error": f"unreadable: {(stdout or stderr).strip()[-300:]}", "session": None}
    cost = read.get("total_cost_usd")
    return {"cost_usd": float(cost) if isinstance(cost, (int, float)) else None,
            "denials": list(read.get("permission_denials") or []),
            "error": (str(read.get("subtype") or "error") if read.get("is_error") else None),
            "session": str(read.get("session_id") or "").strip() or None}


def _result_of(stdout: str) -> dict | None:
    """-> the answer's object: the whole stdout when it is ONE object, else the last line of
    the stream whose `type` is `result`; None when there is none."""
    import json
    try:
        whole = json.loads(stdout)
    except ValueError:
        whole = None
    if isinstance(whole, dict):
        return whole
    for line in reversed(str(stdout).splitlines()):
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict) and one.get("type") == "result":
            return one
    return None


def events(line: str) -> list[dict]:
    """ONE line of the stream -> its events in the common schema (`conductor.adapters.events`):
    a `tool_use` of an `assistant` message is a `tool` (`shell` the `command` of a `Bash`), a
    `tool_result` of a `user` message a `tool-result`, a `thinking` block with text a `thinking`
    {text} -- the blocks recent models sign without text say nothing --, a `system/thinking_tokens`
    line a `thinking` {tokens}, a `text` block `words`, the `usage` of an `assistant` message a
    `context` {tokens, id} first -- the input of its call, read from the cache and written to it --;
    any other line, or one that does not read, says nothing. Verified on claude 2.1.287 (the probe of
    2026-10-09)."""
    import json
    try:
        data = json.loads(line)
    except ValueError:
        return []
    if not isinstance(data, dict):
        return []
    kind = data.get("type")
    if kind == "system" and data.get("subtype") == "thinking_tokens":
        tokens = data.get("estimated_tokens")
        return [{"kind": "thinking", "tokens": tokens}] if isinstance(tokens, int) else []
    content = (data.get("message") or {}).get("content") if kind in ("assistant", "user") else None
    said: list[dict] = []
    sent = _sent(data.get("message")) if kind == "assistant" else None
    if sent is not None:
        said.append({"kind": "context", "tokens": sent, "id": str(data["message"].get("id") or "")})
    for block in content if isinstance(content, list) else []:
        if not isinstance(block, dict):
            continue
        part = block.get("type")
        if kind == "assistant" and part == "tool_use":
            given = block.get("input") if isinstance(block.get("input"), dict) else {}
            command = given.get("command") if block.get("name") == "Bash" else None
            said.append({"kind": "tool", "id": str(block.get("id") or ""), "name": str(block.get("name") or ""),
                         "title": _title(given), "shell": command if isinstance(command, str) else None,
                         "input": given})
        elif kind == "user" and part == "tool_result":
            said.append({"kind": "tool-result", "id": str(block.get("tool_use_id") or ""),
                         "content": _text(block.get("content")), "error": bool(block.get("is_error"))})
        elif kind == "assistant" and part == "thinking" and str(block.get("thinking") or "").strip():
            said.append({"kind": "thinking", "text": str(block["thinking"])})
        elif kind == "assistant" and part == "text" and str(block.get("text") or "").strip():
            said.append({"kind": "words", "text": str(block["text"])})
    return said


def _sent(message) -> int | None:
    """-> what the call that wrote `message` sent the model, in tokens -- `input_tokens`,
    `cache_read_input_tokens` and `cache_creation_input_tokens` of its `usage` --; None without a usage."""
    usage = message.get("usage") if isinstance(message, dict) else None
    if not isinstance(usage, dict):
        return None
    counts = [usage.get(key) for key in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")]
    return sum(one for one in counts if isinstance(one, int) and not isinstance(one, bool))


def contexts(session: str) -> dict | None:
    """-> what the CLI's own store keeps of a session's calls: `calls`, the context each call sent, once per
    message, in order, and `compactions`, the compactions the CLI made of it -- read from the session's
    transcript, `projects/<the workspace>/<session>.jsonl` under `$CLAUDE_CONFIG_DIR` or `~/.claude`, found by
    the session's identity whatever directory the harness ran in; None when no transcript holds it. Reads
    only."""
    import json
    import os
    store = Path(os.environ.get(STORE_ENV) or Path.home() / ".claude") / "projects"
    found = sorted(store.glob(f"*/{session}.jsonl")) if session and store.is_dir() else []
    if not found:
        return None
    calls, compactions, last = [], 0, None
    with found[0].open(encoding="utf-8", errors="replace") as transcript:
        for line in transcript:
            try:
                data = json.loads(line)
            except ValueError:
                continue
            if not isinstance(data, dict):
                continue
            if data.get("type") == "system" and data.get("subtype") == "compact_boundary":
                compactions += 1
            message = data.get("message") if data.get("type") == "assistant" else None
            sent = _sent(message)
            if sent is None or (message.get("id") and message.get("id") == last):
                continue
            last = message.get("id")
            calls.append(sent)
    return {"calls": calls, "compactions": compactions}


def _title(given: dict) -> str:
    """-> a tool's input on one line: its command, its path, its pattern or its address, else
    its first text."""
    for key in ("command", "file_path", "path", "pattern", "url", "query"):
        if isinstance(given.get(key), str):
            return " ".join(given[key].split())[:200]
    first = next((value for value in given.values() if isinstance(value, str)), "")
    return " ".join(first.split())[:200]


def _text(content) -> str:
    """-> what a tool gave back, as text: the text itself, or its text blocks joined."""
    import json
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(one.get("text", "")) if isinstance(one, dict) else str(one) for one in content)
    return "" if content is None else json.dumps(content, ensure_ascii=False)
