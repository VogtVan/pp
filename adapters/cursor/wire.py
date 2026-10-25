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
    from conductor import install, instance      # the engine loading this adapter
    made = []
    for name in install.DOORS:
        written = install.door(workspace, name)
        if written:
            made.append(str(written))
        elif install.door_kept(workspace, name):
            print(install.door_kept(workspace, name))
    card = workspace / ".agents" / "skills" / "pp" / "SKILL.md"
    source = install.card(meta)   # the card a harness receives: the engine's, then its SYSTEM.CONDUCT.md
    if source is None:
        print("pp: no PP.md under the engine's refs -- card not wired, run `-sync` first")
    else:
        from conductor import install
        done = install.project(meta, card, source)
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


SPELLS = ("model", "effort")   # the policy's keys `launch` spells (the effort on the model's name)
MODELS = ()                    # no model name verified on a machine yet; any name passes as given
COST = None                    # the scope of the cost `answer` reads: none -- the stream reports no cost

EFFORTS = {"low": "low", "medium": "medium", "high": "high", "xhigh": "xhigh",   # pp's word ->
           "max": "xhigh"}                                                     # the model's suffix


def launch(workspace: Path, meta: Path, marble: Path | None, prompt: str,
           wiring: Path | None = None, policy: dict | None = None,
           session: str | None = None, workdir: dict | None = None) -> tuple[list[str], dict[str, str], str]:
    """The non-interactive face: the command line that plays ONE exchange of a session
    and exits, composed, never run. No `session` opens one, which cursor names
    (`session_id`); a session is resumed by `--resume <id>`. `workdir`, the material the
    exchange works on, is taken and changes nothing here: it is under the workspace,
    where cursor writes already -- the face composed its head and its variables. Cursor has no system-prompt
    channel and carries no receipt: the engine serves the standing rules inline at the
    opening, and the resumed session's history brings them back at every call; the
    doors at the workspace are the recall; `marble` is not read. The model is spelled
    `--model`; the effort rides the model's name as its suffix, `<model>-<word>` from `EFFORTS`
    (pp's `max` is cursor's `xhigh`), so an effort without a model refuses `policy-unsupported`;
    a budget has no flag here and the regime is `auto` alone (`policy-unsupported`); `wiring`
    is not read: `--force` needs no allowlist. The prompt goes on stdin -- `agent -p` without
    a prompt argument reads it there (read in the docs, not verified on a machine). The output is
    the STREAM (`--output-format stream-json`): one JSON event per line, the `result` line last --
    `events` reads each line, `answer` the last (read in the docs, NOT verified on a machine)."""
    policy = _spellable(policy, "cursor")
    if "effort" in policy and "model" not in policy:
        from conductor.core.errors import Refusal
        raise Refusal("policy-unsupported",
                      "`cursor` spells `effort` on the model's name -- give the model too")
    argv = ["agent", "-p"] + (["--resume", session] if session else []) + [
            "--force", "--output-format", "stream-json"]
    if "model" in policy:
        model = policy["model"]
        argv += ["--model", f"{model}-{EFFORTS[policy['effort']]}" if "effort" in policy else model]
    return argv, {}, prompt

def _spellable(policy: dict | None, provider: str) -> dict:
    """-> the policy this host can spell: the model, and the `auto` regime its line plays --
    a budget, or a regime other than `auto`, refuses `policy-unsupported`, the provider and
    the key named (no such flag at its CLI, or no other mode verified on a machine)."""
    from conductor.core.errors import Refusal
    policy = policy or {}
    if "max_budget_usd" in policy:
        raise Refusal("policy-unsupported",
                      f"`{provider}` cannot spell `max_budget_usd` -- its CLI has no budget flag")
    if policy.get("permissions", "auto") != "auto":
        raise Refusal("policy-unsupported",
                      f"`{provider}` cannot spell `permissions: {policy['permissions']}` -- its line plays "
                      "`auto` alone, no other mode verified on a machine")
    return policy



def answer(stdout: str, stderr: str) -> dict:
    """The reading of ONE exchange's answer, on the stream `launch()` asks for: its LAST
    `result` line -- or the one object `--output-format json` renders -- whose `session_id` is
    the session's identity; `is_error` names its `subtype` as the error. Cursor reports no cost
    and no denial. Its `result`, the assistant's last message, is not read: the stream said it in
    an `assistant` message, `events` reads it there. A stdout with no such object is unreadable:
    the error says so and cites its tail. Read in the docs, NOT verified on a machine."""
    import json
    read = None
    try:
        whole = json.loads(stdout)
    except ValueError:
        whole = None
    if isinstance(whole, dict):
        read = whole
    else:
        for line in reversed(str(stdout).splitlines()):
            try:
                one = json.loads(line)
            except ValueError:
                continue
            if isinstance(one, dict) and one.get("type") == "result":
                read = one
                break
    if read is None:
        return {"cost_usd": None, "denials": [],
                "error": f"unreadable: {(stdout or stderr).strip()[-300:]}", "session": None}
    return {"cost_usd": None, "denials": [],
            "error": (str(read.get("subtype") or "error") if read.get("is_error") else None),
            "session": str(read.get("session_id") or "").strip() or None}


def events(line: str) -> list[dict]:
    """ONE line of the stream -> its events in the common schema (`conductor.adapters.events`): a
    `tool_call` `started` is a `tool` -- its name the key of its call without `ToolCall`
    (`shellToolCall` -> `shell`, its `command` the `shell` field) --, its `completed` the
    `tool-result` (the `stdout` or the `content` of a success, an error under `error` or a non-zero
    `exitCode`); an `assistant` message's text `words`. Read in the docs, NOT verified on a machine
    (the CLI is absent here)."""
    import json
    try:
        data = json.loads(line)
    except ValueError:
        return []
    if not isinstance(data, dict):
        return []
    kind = data.get("type")
    if kind == "tool_call" and isinstance(data.get("tool_call"), dict) and data["tool_call"]:
        key, call = next(iter(data["tool_call"].items()))
        call = call if isinstance(call, dict) else {}
        given = call.get("args") if isinstance(call.get("args"), dict) else {}
        ident, name = str(data.get("call_id") or ""), str(key).removesuffix("ToolCall")
        if data.get("subtype") == "started":
            command = given.get("command") if key == "shellToolCall" else None
            title = next((given[one] for one in ("command", "path", "pattern", "query") if isinstance(given.get(one), str)), "")
            return [{"kind": "tool", "id": ident, "name": name, "title": " ".join(str(title).split())[:200],
                     "shell": command if isinstance(command, str) else None, "input": given}]
        if data.get("subtype") == "completed":
            result = call.get("result") if isinstance(call.get("result"), dict) else {}
            success = result.get("success") if isinstance(result.get("success"), dict) else {}
            failed = result.get("error")
            content = (str(success.get("stdout") or success.get("content") or "") if success
                       else str(failed.get("errorMessage") or failed) if isinstance(failed, dict) else str(failed or ""))
            code = success.get("exitCode")
            return [{"kind": "tool-result", "id": ident, "content": content,
                     "error": failed is not None or (isinstance(code, int) and code != 0)}]
        return []
    if kind == "assistant":
        content = (data.get("message") or {}).get("content")
        return [{"kind": "words", "text": str(one["text"])} for one in content if isinstance(one, dict)
                and one.get("type") == "text" and str(one.get("text") or "").strip()] if isinstance(content, list) else []
    return []
