# pp × Claude Code

*Last verified: 2026-08-03.*

`-install <workspace> -claude` wires the full surface:

| Piece | Where | What it does |
|---|---|---|
| Card | `.claude/skills/pp/SKILL.md` | the conductor's card, listed by Claude Code as the `pp` skill |
| Door | `CLAUDE.md` (workspace root, written by the flag) | points any session at the conductor |
| Marble | `claude-pp` (workspace root) | launches `claude --append-system-prompt-file .pp/.sys/system.md` — the standing rules ride the system prompt |
| Permissions | `.claude/settings.json` (written once) | `Bash(./pp:*)` + the repair path `Bash(uv run .pp/.sys/engine/pp.py:*)` — the `:*` wildcard covers the run key; an existing file is left untouched and the entries to add are said |

## CLI mode — marble guarantee

```sh
./claude-pp            # any claude arguments pass through
```

The standing rules are pinned at launch and survive the whole session, compaction
included. On Windows, `.\claude-pp` — the launcher's `.cmd` twin, written by the
same flag.

## Extension mode — recall guarantee

Reload the window, open the workspace: the door points at the registered card, the
agent boots the conductor and follows its blocks. Launch flags do not reach the
panel — the hold is the taught reflex, re-armed by every block.

## Scope

Everything `-claude` writes lives **inside the workspace** — `~/.claude` is never
touched; the launcher's flag acts per invocation. Your other repositories and
Claude Code sessions elsewhere are unaffected.

## Add to an existing instance

From the workspace root: `./pp -install -claude` — no workspace argument: the
flag wires THIS instance, write-once (a replay answers `already wired`).

## External references

- CLI flags: <https://code.claude.com/docs/en/cli-reference>
- System prompt options: <https://code.claude.com/docs/en/agent-sdk/modifying-system-prompts>
- Settings and permissions: <https://code.claude.com/docs/en/settings>
