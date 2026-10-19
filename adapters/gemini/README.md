# pp × Gemini CLI

*Last verified: 2026-08-03.*

`-install <workspace> -gemini` wires the full surface (the gemini CLI must be on
PATH — the marble composes over its dumped baseline; the install refuses upfront
otherwise):

| Piece | Where | What it does |
|---|---|---|
| Card | `.gemini/commands/pp.toml` | `/pp` serves the conductor's card, inline |
| Door | `GEMINI.md` (workspace root, written by the flag) | read natively by Gemini; points at the `/pp` card |
| Marble | `gemini-pp` (workspace root) | launches gemini with `GEMINI_SYSTEM_MD` pointing at `.pp/.sys/system.gemini.md` — Gemini's own dumped baseline with the standing rules appended |
| Permissions | documented only | a `coreTools` allowlist can RESTRICT the whole tool set — choose your approval mode yourself |

## CLI mode — marble guarantee

```sh
./gemini-pp            # any gemini arguments pass through
```

On Windows, `.\gemini-pp` — the launcher's `.cmd` twin, written by the same flag.

Gemini's system prompt is **replace-only**, so the "append" is a composition:
its own baseline, dumped by Gemini itself, with the rules after it. The baseline
is a **snapshot** — after a Gemini upgrade, delete `.pp/.sys/system.gemini.md`
and re-run the wire's dump (`GEMINI_WRITE_SYSTEM_MD`) to re-compose.

## Non-interactive

**Not verified on this machine (CLI absent)** — read from the Gemini CLI docs on
2026-09-26 (`cli/headless/`, `cli/cli-reference/`, linked below). The pp contract
these facts feed is [`adapters/README.md`](../README.md).

```sh
GEMINI_SYSTEM_MD=.pp/.sys/system.gemini.md PP_MARBLE=1 gemini --approval-mode yolo --output-format stream-json   # the prompt on stdin
```

| Concern | What the docs say |
|---|---|
| Prompt | `-p/--prompt <text>` forces non-interactive mode (appended to stdin when stdin is piped); `-i/--prompt-interactive` runs the prompt then stays interactive |
| System prompt | the environment variable `GEMINI_SYSTEM_MD` alone, REPLACE-only — the same composition `gemini-pp` points at; no flag exists, so the launch carries a VARIABLE, not an argument |
| Permissions | `--approval-mode default\|auto_edit\|yolo\|plan`; `--yolo/-y` and `--allowed-tools` are deprecated (the Policy Engine replaces the latter) |
| Output | `--output-format text\|json\|stream-json` — `json` is one object (`response`, `stats`, optional `error`), `stream-json` newline-delimited events (`init`, `message`, `tool_use`, `tool_result`, `error`, `result`). pp launches the STREAM (engine `0.1.0-beta.63`): `answer()` reads the session of `init`, the response of the assistant's `message` deltas, the error of `error` or a failed `result`; `events()` reads `tool_use`, `tool_result` and the assistant's `message` -- read in the docs, NOT verified on a machine |
| Limits | a turn limit exists (exit code 53) but no flag for it is documented |
| Exit codes | `0` success · `1` general or API error · `42` input error · `53` turn limit exceeded |
| Resume | `--resume/-r latest\|<session id>`. pp composes `gemini --resume <session_id> -p "<prompt>" …` with `GEMINI_SYSTEM_MD` and `PP_MARBLE=1` at EVERY launch: the variable is read by the process, and the session docs list what `--resume` restores — the prompts, the answers, the tools, the tokens — not the system prompt. The identity is read from `session_id` in the `--output-format json` object; the headless docs name only `response`, `stats`, `error` and put the session ID in the `init` event of `stream-json` — not verified on a machine: an answer without `session_id` refuses `session-missing` |
| Model, context | `-m/--model`, `--include-directories` |

The wiring already requires gemini on PATH (the baseline dump): nothing more to
wire for the non-interactive mode — the launch sets the variable the launcher sets.

## Extension mode — recall guarantee

Yes, Gemini has one: the **Gemini CLI Companion** (VS Code), which also powers
Gemini Code Assist's agent mode. The door and `/pp` do the teaching there.

## Heads-up

Google is transitioning individual/free usage to the **Antigravity CLI** (`agy`),
which keeps the same concepts (context files, commands, skills) under partially
renamed paths; the open-source `gemini-cli` remains active and paid/enterprise
API keys are unaffected.

## Scope

Everything `-gemini` writes lives **inside the workspace** — `~/.gemini` is never
touched; `GEMINI_SYSTEM_MD` is set per invocation by the launcher. Your other
repositories and Gemini sessions elsewhere are unaffected.

## Add to an existing instance

From the workspace root: `./pp -install -gemini` — no workspace argument: the
flag wires THIS instance, write-once (a replay answers `already wired`).

## External references

- Context files (`GEMINI.md`, `context.fileName`): <https://geminicli.com/docs/cli/gemini-md/>
- System prompt (`GEMINI_SYSTEM_MD`): <https://geminicli.com/docs/cli/system-prompt/>
- Custom commands (TOML, `/pp`): <https://geminicli.com/docs/cli/custom-commands/>
- Headless (`gemini -p`): <https://geminicli.com/docs/cli/headless/>
- VS Code companion: <https://geminicli.com/docs/ide-integration/>
- Antigravity migration: <https://antigravity.google/docs/cli/gcli-migration>
