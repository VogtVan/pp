# pp × OpenAI Codex CLI

*Last verified: 2026-08-03.*

`-install <workspace> -codex` wires the full surface:

| Piece | Where | What it does |
|---|---|---|
| Card | `.agents/skills/pp/SKILL.md` | the conductor's card at the cross-vendor skills standard — Codex reads it, **and so does Cursor** |
| Door | `AGENTS.md` (workspace root, written by the flag) | Codex reads it natively (concatenated root→cwd, 32 KiB combined cap) |
| Marble | `.codex/config.toml` | `developer_instructions` appends the standing rules to Codex's own instructions — trusted-project config, OS-neutral, no launcher needed |
| Permissions | `.codex/rules/default.rules` | a `prefix_rule` on the conductor's own invocation — **verify it**: `codex execpolicy check` |

## CLI mode — marble guarantee

```sh
codex                  # the project config carries the rules; codex exec works too
```

## Non-interactive

**Not verified on this machine (CLI absent)** — read from the Codex docs on
2026-09-26 (`non-interactive-mode`, `config-file/config-reference`, linked below).
The pp contract these facts feed is [`adapters/README.md`](../README.md).

```sh
codex exec --sandbox workspace-write --full-auto --json "<prompt>"   # or: codex exec - < prompt.txt
```

| Concern | What the docs say |
|---|---|
| Prompt | one argument, or stdin (`codex exec -`); a prompt argument plus piped stdin makes the pipe extra context |
| System prompt | `developer_instructions` (APPENDS — the field `-codex` already writes at `.codex/config.toml`); `model_instructions_file` REPLACES the built-in instructions; `codex exec` honors the project config **only once the project is trusted** |
| Permissions | `--sandbox read-only\|workspace-write\|danger-full-access`, `-a/--ask-for-approval`, `--full-auto`, `--dangerously-bypass-approvals-and-sandbox`; `-c key=value` and `--profile` override the config |
| Output | `--json` (JSONL events on stdout), `-o/--output-last-message <path>`, `--output-schema <path>`; progress on stderr, the final message on stdout. `events()` (engine `0.1.0-beta.63`) reads each line: `command_execution` started and completed, `mcp_tool_call`, `file_change`, `reasoning`, `agent_message` -- read in the docs, NOT verified on a machine |
| Limits | no turn or budget flag documented |
| Exit codes | not documented |
| Resume | `codex exec resume --last "<instruction>"`, `codex exec resume <session id>`. pp composes `codex exec <options> resume <thread_id> "<prompt>"` — the options of `exec` first, then the sub-verb — with the `thread_id` of the previous answer's `thread.started`; the marble needs nothing at the call: `.codex/config.toml` is re-read by every process. Not verified on a machine |
| Isolation | `--ephemeral` (no session files), `--ignore-user-config`, `--ignore-rules`, `--skip-git-repo-check` |

**Discrepancy to settle when codex is installed:** the marble rides the project
config, and the project config applies to a TRUSTED project only — how a headless
run trusts its workspace is not documented. Until then, a headless codex run on a
fresh pp instance may play WITHOUT the standing rules; the recall (door and card)
still teaches the reflex.

## Extension mode — the marble holds here too

The Codex extension (VS Code marketplace `openai.chatgpt`) shares the CLI's
configuration layers — *"The CLI and IDE extension share the same configuration
layers"* (Codex docs) — so the project config's standing rules ride the panel as
well, once the project is trusted. Codex is the one harness whose extension gets
the marble: its vehicle is configuration, not a launch flag. The door and the
card do the teaching on top.

## Scope

Everything `-codex` writes lives **inside the workspace** — `~/.codex` is never
touched. The project config and rules apply **only once you trust the project**
(Codex asks on first run), and only to this project.

## Add to an existing instance

From the workspace root: `./pp -install -codex` — no workspace argument: the
flag wires THIS instance, write-once (a replay answers `already wired`).

## External references

- AGENTS.md discovery: <https://learn.chatgpt.com/docs/agent-configuration/agents-md>
- Config reference (`developer_instructions`): <https://learn.chatgpt.com/docs/config-file/config-reference>
- Skills: <https://learn.chatgpt.com/docs/build-skills>
- Rules / approvals: <https://learn.chatgpt.com/docs/agent-approvals-security>
- Headless (`codex exec`): <https://learn.chatgpt.com/docs/non-interactive-mode>
