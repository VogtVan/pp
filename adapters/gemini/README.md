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
