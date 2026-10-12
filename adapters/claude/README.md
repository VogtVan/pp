# pp × Claude Code

*Last verified: 2026-09-26 (claude 2.1.270).*

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

## Non-interactive

**Verified on this machine on 2026-09-26** (claude 2.1.270, WSL2), on a
`mktemp -d` with a three-line witness marble. The pp contract these facts feed is
[`adapters/README.md`](../README.md).

```sh
PP_MARBLE=1 claude -p [--resume <session_id>] --append-system-prompt-file .pp/.sys/system.md \
  --permission-mode auto|dontAsk|bypassPermissions --permission-prompts none \
  --output-format stream-json --verbose     # the prompt on stdin
```

The line pp composes since engine `0.1.0-beta.30`: the session is kept (no
`--no-session-persistence`), `answer()` reads its `session_id`, and a later
exchange resumes it by `--resume <session_id>`. The marble rides EVERY launch,
the resume included: `--system-prompt-snapshot` (2.1.283, default `on`) records
the system prompt at the conversation's first request and resends the record
at every later request and resume, « even when a later launch passes different
text, until the conversation is compacted », with « no effect where
system-prompt recording is not yet enabled » — handed again, the marble
changes nothing where the record holds and restores it where it does not.

The mode follows the policy's `permissions` (engine `0.1.0-beta.34`): `auto` —
the default — gives `--permission-mode auto`, `strict` gives `dontAsk`, `bypass`
gives `bypassPermissions`; `--permission-prompts none` rides all three, since
nobody answers a prompt under `-p`. What each mode does, and why `auto` is the
default — `dontAsk` refused a heredoc piped to `./pp` and `Write` in the essay
S9 (2.1.283), `auto` let the same exchange through — is
[`adapters/README.md` § The permission regime](../README.md#the-permission-regime).

| Concern | What 2.1.270 does |
|---|---|
| Prompt | one argument, or stdin; `--input-format text\|stream-json`; `-p` skips the workspace trust dialog |
| System prompt | `--append-system-prompt-file <path>` APPENDS (the marble as the launcher carries it); `--system-prompt-file` REPLACES; the `-file` forms are accepted but **not listed by `--help`** (the inline forms are) |
| Permissions | `--permission-mode acceptEdits\|auto\|bypassPermissions\|manual\|dontAsk\|plan`; `--permission-prompts none` denies anything that would prompt; `--allowedTools`, `--tools`, `--restricted` narrow the set |
| Output | `--output-format json` gives one object: `result`, `is_error`, `subtype`, `total_cost_usd`, `num_turns`, `session_id`, `modelUsage`; `stream-json` (with `--verbose`) streams one JSON object per line -- `system/init`, `system/thinking_tokens`, `assistant` (`tool_use`, `thinking`, `text`), `user` (`tool_result`), then the `result` line with the fields of the one object. pp launches the STREAM (engine `0.1.0-beta.63`): `events()` reads each line, `answer()` the last -- **verified** on claude 2.1.287 with Opus 5.5 (2026-10-09; the `thinking` blocks come signed with NO text: the count alone is said) |
| Limits | `--max-budget-usd <amount>`; `--max-turns <n>` is accepted but **not listed by `--help`** — a budget under the price of one exchange refuses the whole exchange (`subtype: error_max_budget_usd`, exit 1, no `result`). **Verified on 2026-10-11** (2.1.287, Haiku, a `mktemp -d`): the bound compares what THIS process spent, checked between two turns, although `total_cost_usd` is the session's cumul (`COST = "session"`) -- a session resumed at 0.0242 went to 0.0402 under `--max-budget-usd 0.025` (`success`, 5 turns); a new session stopped after one turn at 0.0102 under 0.008 (`error_max_budget_usd`). A launch thus goes past its bound by one turn at most |
| Exit codes | `0` success · `1` failure — seen: not logged in, budget exhausted |
| Resume | `-r/--resume <id>`, `-c/--continue`, `--session-id <uuid>`, `--fork-session`; `--no-session-persistence` keeps nothing on disk. pp resumes by `--resume <session_id>`, the identity the previous answer gave; it never names a session itself (`--session-id`) and never throws one away |
| System prompt at resume | `--system-prompt-snapshot <on\|off>` (2.1.283): the record wins while it holds; pp hands the marble at every launch (see above) |
| `--bare` | no hooks, no `CLAUDE.md` discovery, no OAuth: auth is **`ANTHROPIC_API_KEY` alone** — on this machine's claude.ai login it answers `Not logged in · Please run /login`, exit 1 |

The call that answered — `claude -p --model haiku --append-system-prompt-file
marble.md --permission-mode dontAsk --permission-prompts none --output-format
json --no-session-persistence --max-budget-usd 0.10 --max-turns 1 "Reply with
the single word: pong"` — returned `"result":"pong"`, `"is_error":false`, exit
0, `"total_cost_usd":0.045` (list price), `"duration_ms":2398`. The same call
on the default model exhausted a 0.10 budget on its own system prompt (10 975
cache-creation tokens, 0.223 USD) and returned no result. Nothing more to wire
for this mode: `Bash(./pp:*)` covers the console; the other tools follow the
regime the policy names.

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
- Permission modes: <https://code.claude.com/docs/en/permission-modes>
