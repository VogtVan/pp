# pp × Cursor

*Last verified: 2026-08-03.*

`-install <workspace> -cursor` wires the surface:

| Piece | Where | What it does |
|---|---|---|
| Card | `.agents/skills/pp/SKILL.md` | listed as a Cursor Agent Skill — the same cross-vendor location `-codex` uses: the two flags share one card, cumulable without conflict |
| Doors | `AGENTS.md` · `CLAUDE.md` — the **Cursor-recognized** doors; the flag also writes `GEMINI.md` so the same workspace stays ready for Gemini (interop, not a claimed Cursor capability) | applied as rules alongside `.cursor/rules`, nested included |
| Marble | — | Cursor exposes **no system-prompt channel**: the guarantee is the **recall**, in both modes |
| Permissions | `.cursor/permissions.json` (written once) | a `terminalAllowlist` PREFIX on `./pp` — the run key and arguments pass free; an existing file is left untouched and the entry to add is said |

## One install, every model

Cursor is a **multi-model harness**: its model picker runs Anthropic, OpenAI,
Google and other models, switchable per chat. pp wires the **harness surface** —
rules, skills, permissions — and that surface does not change with the model:
**one `-cursor` install covers them all**, no per-model flag exists or is needed.
Switch models freely mid-work; the conduction does not notice. What follows the
harness (not the model) is the **guarantee**: no system-prompt channel on Cursor
means the recall guarantee, even when a Claude model runs underneath.

## The IDE — recall guarantee

Open the workspace in Cursor: doors + card teach the reflex; every block re-arms it.

## CLI mode (`agent`) — recall guarantee

Cursor does ship a CLI — `agent` (the docs of 2026-09-26 name it so; earlier
texts, this one included, said `cursor-agent`), headless included (`-p`,
`--output-format json`). It reads the same doors and skills; there is still no
system-prompt flag, so the guarantee stays the recall.

## Non-interactive

**Not verified on this machine (CLI absent)** — read from the Cursor docs on
2026-09-26 (`cli/using`, `cli/reference/parameters`, linked below). The pp contract
these facts feed is [`adapters/README.md`](../README.md).

```sh
agent -p --force --output-format stream-json   # the prompt on stdin
```

| Concern | What the docs say |
|---|---|
| Prompt | one argument, or stdin |
| System prompt | none — no flag, no variable; the rules (`.cursor/rules`), `AGENTS.md` and `CLAUDE.md` at the project root are read: the recall guarantee |
| Permissions | `--force` (alias `--yolo`): "Force allow commands unless explicitly denied"; `--approve-mcps`; "Cursor has full write access in non-interactive mode" |
| Output | `--output-format text\|json\|stream-json`. pp launches the STREAM (engine `0.1.0-beta.63`): `answer()` reads its last `result` line, `events()` its `tool_call` started and completed (the call's key less `ToolCall`, `shellToolCall` the shell) and the `assistant` text -- read in the docs, NOT verified on a machine |
| Limits | no turn or budget flag documented |
| Exit codes | not documented |
| Resume | `--resume [chat id]`. pp composes `agent -p --resume <session_id> --force --output-format json "<prompt>"` with the `session_id` of the previous result object (docs: `cursor.com/docs/cli/reference/output-format`); cursor has no system-prompt channel: the engine serves the standing rules inline at the opening, and the resumed session's history brings them back. Not verified on a machine |
| Model, auth, place | `--model <model>`, `--api-key <key>` or `CURSOR_API_KEY`, `--workspace <path>` |

Nothing more to wire: the `terminalAllowlist` prefix on `./pp` and the doors serve
the headless run as they serve the IDE.

## The window and the cap of a prompt

Cursor gives a model 200K tokens of context unless its name asks for more -- `<model>[context=1m]` on the
models that carry 1M (cursor.com/docs/models: « up to 1M tokens with extended context » for the Claude
5.x; the suffix read at forum.cursor.com on 2026-10-29, kept in `-p` mode per the CLI changelog). `CAP` is
the default: `400_000` characters (200K x 2.5 x 0.8) whatever the model. The names the CLI takes are not
documented (`agent --list-models` says them on a machine): `CONTEXT_WINDOWS` and `CAPS` are empty until a
name and its `[context=1m]` form enter them with their window -- then that form lifts the cap to
2 000 000 characters.

## Scope

Nothing Cursor-global is ever written — the card and doors are workspace files;
your permissions file is yours to add. Other repositories are unaffected.

## Add to an existing instance

From the workspace root: `./pp -install -cursor` — no workspace argument: the
flag wires THIS instance, write-once (a replay answers `already wired`).

## External references

- Rules and context files: <https://cursor.com/docs/rules>
- The CLI: <https://cursor.com/docs/cli/using>
- Agent Skills: <https://cursor.com/docs/skills>
- Permissions: <https://cursor.com/docs/reference/permissions>
