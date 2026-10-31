# pp × Claude Code

*Last verified: 2026-09-26 (claude 2.1.270).*

`-install <workspace> -claude` wires the full surface:

| Piece | Where | What it does |
|---|---|---|
| Card | `.claude/skills/pp/SKILL.md` | the conductor's card, listed by Claude Code as the `pp` skill |
| Door | `CLAUDE.md` (workspace root, written by the flag) | points any session at the conductor |
| Marble | `claude-pp` (workspace root) | launches `claude --append-system-prompt-file .pp/.sys/system.md` — the standing rules ride the system prompt |
| Permissions | `.claude/settings.json` (written once) | `Bash(./pp:*)` + the repair path `Bash(uv run .pp/.sys/engine/pp.py:*)` — the `:*` wildcard covers the run key; an existing file is left untouched and the entries to add are said |
| Receipt | the same `.claude/settings.json`, key `env` | `PP_MARBLE: "1"` -- the editor's extension runs no `claude-pp`, so the settings file is the one channel for the receipt: `-new` then serves no standing orders inline (the card the extension lists carries them), the bare boot under 8 000 characters where it was 32 500 (plan fixes2) |

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
| Output | `--output-format json` gives one object: `result`, `is_error`, `subtype`, `total_cost_usd`, `num_turns`, `session_id`, `modelUsage`; `stream-json` (with `--verbose`) streams one JSON object per line -- `system/init`, `system/thinking_tokens`, `assistant` (`tool_use`, `thinking`, `text`), `user` (`tool_result`), then the `result` line with the fields of the one object. pp launches the STREAM (engine `0.1.0-beta.63`): `events()` reads each line, `answer()` the last -- **verified** on claude 2.1.287 with Opus 5.5 (2026-10-09; the `thinking` blocks come signed with NO text: the count alone is said). Each `assistant` line carries its call's `usage`: `events()` says it as `context`, `input_tokens + cache_read_input_tokens + cache_creation_input_tokens`, under the message's `id` (the usage is repeated on every block of a message; the reader says it once, engine `0.2.0-beta.24`) |
| Store | the CLI keeps each session at `projects/<the workspace, every character but letters and digits as ->/<session>.jsonl` under `$CLAUDE_CONFIG_DIR`, else `~/.claude` -- one line per message, the `assistant` ones with their `usage`, a `system/compact_boundary` line at each compaction. `contexts(session)` finds the transcript by the session's identity (the harness may run in a `--work` clone) and reads its calls once per message and its compactions; `STORE_ENV` names the variable. Read on 2026-10-29 over 117 runs of the house (claude 2.1.287) |
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

## The window and the cap of a prompt

`CONTEXT_WINDOWS` names the 1M models (fable 5.1, opus 5.5, sonnet 5.5, haiku 5.5, read at
platform.claude.com/docs/en/models/overview on 2026-10-29) and the aliases the CLI takes; `haiku` stays at
200K, measured on 2026-10-27 (`claude -p --model haiku` refused ~282 505 tokens). `CAPS` derives the cap of
a prompt in characters: `window x CHARS_PER_TOKEN x SHARE` -- 2.5 characters per token (the vendor's own
figure for the current tokenizer; 2.57 measured on a block of pp on 2026-10-28), 20 % kept for the system
prompt, the tools and the answer: 2 000 000 characters at 1M, 400 000 at 200K. The ~1.78x count of a piped
prompt reported at anthropics/claude-code #92305 (2.1.259-261) is NOT observed on 2.1.287: probed on
2026-10-29 with sonnet, 1 499 977 characters (395 182 tokens) and 2 699 964 characters (703 212 tokens)
piped were each read whole in one request, neither refused (`PROBED` in `wire.py`); a 703k-token prompt
counted 1.78x would have passed the window. The client itself refuses a piped prompt over 10 485 760
characters (2.1.128+); `CAP` is `None`: without a model named the engine's floor holds. Seen on the same
probes: the CLI played two turns and created the prompt twice in its cache (1 404 712 tokens for 703 212),
so a launch may cost twice its prompt; `--max-budget-usd` is checked between turns, a bound of 4 USD let
5.62 USD through.

`CONTEXT_BASE`, `FLOW_RATIO` and `THINKING_KEPT` estimate a run's context where no call was measured
(an exchange whose harness said no usage, a run from before agent 0.32.0). They were fitted on
2026-10-29 by `./pp agent calibrate` over the 106 runs of the house without a compaction: 90 354
tokens at a session's first call (median, max 109 970), the flow but the thought weighed 1.5, the
thought weighed 0 -- the median gap to the measure goes from 60 % (the flow alone) to 7 %, the p90
from 237 % to 89 %. The tail is what the CLI clears or compacts on its own, which no estimate sees:
the measure is the figure to read.

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
