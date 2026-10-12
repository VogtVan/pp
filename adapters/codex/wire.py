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
    pattern = ["uv", "run", "{engine}"],
)
"""   # `engine`: the repair path the launcher runs, under the instance


def wire(workspace: Path, meta: Path) -> list[str]:
    """`meta` is the instance dir `install` just seeded -- the card comes from ITS
    engine, the marble from ITS compiled artifact: wired text = built text."""
    import sys
    from conductor import install, instance      # the engine loading this adapter
    made = []
    written = install.door(workspace, "AGENTS.md")
    if written:
        made.append(str(written))
    card = workspace / ".agents" / "skills" / "pp" / "SKILL.md"
    source = install.card(meta)   # the card a harness receives: the engine's, then its SYSTEM.CONDUCT.md
    if source is None:
        print("pp: no PP.md under the engine's refs -- card not wired, run `-sync` first")
    else:
        from conductor import install
        done = install.project(meta, card, source)
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
              f"{install.engine_invocation(meta)}`, the repair path)")
    else:
        rules.parent.mkdir(parents=True, exist_ok=True)
        rules.write_text(RULES.format(engine=install.engine_invocation(meta)), encoding="utf-8")
        made.append(str(rules))
        print("pp: verify the generated rule with `codex execpolicy check`")
    return made


SPELLS = ("model", "effort")   # the policy's keys `launch` spells
MODELS = ()                    # no model name verified on a machine yet; any name passes as given
COST = None                    # the scope of the cost `answer` reads: none -- `exec --json` reports no cost

EFFORTS = {"low": "low", "medium": "medium", "high": "high", "xhigh": "xhigh",   # pp's word ->
           "max": "xhigh"}                                                     # model_reasoning_effort


def launch(workspace: Path, meta: Path, marble: Path | None, prompt: str,
           wiring: Path | None = None, policy: dict | None = None,
           session: str | None = None, workdir: dict | None = None) -> tuple[list[str], dict[str, str], str]:
    """The non-interactive face: the command line that plays ONE exchange of a session
    and exits, composed, never run. No `session` opens one, which codex names
    (`thread.started`); a session is resumed by the sub-verb `resume <id>`, after the
    options of `exec`. `workdir`, the material the exchange works on, is taken and changes
    nothing here: it is under the workspace, inside the `workspace-write` sandbox
    already -- the face composed its head and its variables. `marble` is not read: `.codex/config.toml`, written by `wire`,
    carries the standing rules (`developer_instructions`), re-read by every process --
    the resume included -- and sets the receipt for the
    commands codex runs -- nothing travels by the call. The model is spelled `-m`; the effort
    by the config override `-c model_reasoning_effort="<word>"`, from `EFFORTS` (pp's `max` is
    codex's `xhigh`, its highest); a budget has no flag here and the regime is `auto` alone
    (`policy-unsupported`); `wiring` is not read: `--full-auto` needs no allowlist. The prompt
    goes on stdin, named by the last argument `-` (`codex exec -`; read in the docs, not
    verified on a machine)."""
    policy = _spellable(policy, "codex")
    argv = ["codex", "exec", "--sandbox", "workspace-write", "--full-auto", "--json"]
    if "model" in policy:
        argv += ["-m", policy["model"]]
    if "effort" in policy:
        argv += ["-c", f'model_reasoning_effort="{EFFORTS[policy["effort"]]}"']
    if session:
        argv += ["resume", session]
    argv.append("-")
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
    """The reading of ONE exchange's answer, as `--json` renders it: JSONL events, the
    assistant's message the last `item.completed` whose item is an `agent_message`; when
    no such event stands, the last non-empty line is the answer as it is; the session's
    identity the `thread_id` of `thread.started`. Codex reports no cost and no denial by
    this stream; a `turn.failed` event names the error."""
    import json
    text, error, session = None, None, None
    lines = [line for line in str(stdout).splitlines() if line.strip()]
    for line in lines:
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        item = event.get("item") if isinstance(event.get("item"), dict) else {}
        if event.get("type") == "thread.started":
            session = str(event.get("thread_id") or "").strip() or None
        if event.get("type") == "item.completed" and item.get("type") == "agent_message":
            text = str(item.get("text") or "").strip() or None
        if event.get("type") == "turn.failed":
            failed = event.get("error")
            error = str(failed.get("message") or failed) if isinstance(failed, dict) else str(failed or "turn.failed")
    if text is None and lines:
        last = lines[-1].strip()
        try:
            json.loads(last)
        except ValueError:
            text = last                          # a plain last message, as `-o` would write it
    if text is None and error is None and not lines:
        error = f"unreadable: {stderr.strip()[-300:]}"
    return {"response": text, "cost_usd": None, "denials": [], "error": error, "session": session}


def events(line: str) -> list[dict]:
    """ONE line of the `--json` stream -> its events in the common schema
    (`conductor.adapters.events`): an `item.started` of a `command_execution` is a `tool` (`shell`
    its `command`), its `item.completed` the `tool-result` (`aggregated_output`, an error when the
    exit code is not 0 or the status `failed`); an `mcp_tool_call` the same, by its server and
    tool; a completed `file_change` a `tool` and its `tool-result`; a completed `reasoning` a
    `thinking` {text}; a completed `agent_message` `words`. Read in the docs, NOT verified on a
    machine (the CLI is absent here)."""
    import json
    try:
        data = json.loads(line)
    except ValueError:
        return []
    if not isinstance(data, dict) or data.get("type") not in ("item.started", "item.completed"):
        return []
    item = data.get("item") if isinstance(data.get("item"), dict) else {}
    done, kind, ident = data["type"] == "item.completed", item.get("type"), str(item.get("id") or "")
    if kind == "command_execution":
        command = str(item.get("command") or "")
        if not done:
            return [{"kind": "tool", "id": ident, "name": "command_execution", "title": " ".join(command.split())[:200],
                     "shell": command, "input": {"command": command}}]
        code = item.get("exit_code")
        return [{"kind": "tool-result", "id": ident, "content": str(item.get("aggregated_output") or ""),
                 "error": item.get("status") == "failed" or (isinstance(code, int) and code != 0)}]
    if kind == "mcp_tool_call":
        name = f"{item.get('server', '')}/{item.get('tool', '')}"
        if not done:
            given = item.get("arguments") if isinstance(item.get("arguments"), dict) else {}
            return [{"kind": "tool", "id": ident, "name": name, "title": name, "shell": None, "input": given}]
        failed = item.get("error")
        content = json.dumps(item.get("result") if failed is None else failed, ensure_ascii=False)
        return [{"kind": "tool-result", "id": ident, "content": content,
                 "error": item.get("status") == "failed" or failed is not None}]
    if kind == "file_change" and done:
        changes = item.get("changes") if isinstance(item.get("changes"), list) else []
        paths = ", ".join(str(one.get("path", "")) for one in changes if isinstance(one, dict))
        return [{"kind": "tool", "id": ident, "name": "file_change", "title": paths[:200], "shell": None,
                 "input": {"changes": changes}},
                {"kind": "tool-result", "id": ident, "content": str(item.get("status") or ""),
                 "error": item.get("status") == "failed"}]
    if kind == "reasoning" and done and str(item.get("text") or "").strip():
        return [{"kind": "thinking", "text": str(item["text"])}]
    if kind == "agent_message" and done and str(item.get("text") or "").strip():
        return [{"kind": "words", "text": str(item["text"])}]
    return []
