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

## CLI mode (`cursor-agent`) — recall guarantee

Cursor does ship a CLI — `cursor-agent`, headless included (`-p`,
`--output-format json`). It reads the same doors and skills; there is still no
system-prompt flag, so the guarantee stays the recall.

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
