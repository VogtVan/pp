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
