# The editor mode

pp started inside the editor: you talk to Claude Code, Codex, Gemini or Cursor as
usual, and the model calls pp to receive each step. This mode stays fully
supported when you do not want the house and its post; the house is the
recommended way ([Quick start](../README.md#quick-start)).

- [Install](#install)
- [Two guarantees](#two-guarantees)
- [Starting the host](#starting-the-host)
- [What a session looks like](#what-a-session-looks-like)
- [Day-two gestures](#day-two-gestures)
- [Try it with Daneel](#try-it-with-daneel)

## Install

```sh
uv run pp/engine/pp.py -install <workspace> -<provider>
```

`<workspace>` is any path; `install` creates it. Keep it a **sibling** of the
clone, not nested inside it. `<provider>` is the harness you run pp under —
`claude`, `codex`, `gemini` or `cursor`, so the flag reads `-claude`, `-codex`,
`-gemini` or `-cursor`. The flags add up in one install. pp wires the
**harness**, never the model: the model running underneath is the harness's own
choice.

The install writes the instance (`<workspace>/.pp`) and, per flag, that harness's
**door** — the file it reads on its own: `CLAUDE.md` for `-claude`, `AGENTS.md`
for `-codex`, `GEMINI.md` for `-gemini`; `-cursor` writes `AGENTS.md` and
`CLAUDE.md`, plus `GEMINI.md`. It also registers pp's **card** — its usage
contract — where that harness lists its skills or commands, and the system-prompt
wiring where the harness allows it. With no flag, the two generic doors
(`CLAUDE.md`, `AGENTS.md`) are written for you to wire a harness yourself.

Two options ride the same call: `-base <package>` puts the instance on another
base package than the kit, and every later call may name the instance it
addresses with `--instance <dir>` or `PP_HOME` (see
[the operator's console](reference/console.md)).

## Two guarantees

The way you run the host decides which **guarantee** holds the conduction:

- **marble** — the standing rules ride the host's **own system prompt**: pinned at
  launch, they hold for the whole session, compaction included.
- **recall** — the taught reflex: the doors and the registered card, re-armed by
  every block.

| Provider | Mode | Install | Guarantee |
|---|---|---|---|
| **Claude Code** ([ref](../adapters/claude/README.md)) | CLI | `-install <workspace> -claude` | **marble** |
| | VS Code extension | same install | recall |
| **Codex** ([ref](../adapters/codex/README.md)) | CLI | `-install <workspace> -codex` | **marble** |
| | VS Code extension | same install | **marble** — the extension shares the CLI's config layers |
| **Gemini** ([ref](../adapters/gemini/README.md)) | CLI | `-install <workspace> -gemini` — the `gemini` CLI must be on PATH | **marble** |
| | CLI Companion (VS Code) | same install | recall |
| **Cursor** ([ref](../adapters/cursor/README.md)) | CLI (`cursor-agent`) | `-install <workspace> -cursor` | recall — no system-prompt channel on Cursor |
| | the IDE | same install | recall — one install covers every model Cursor runs |

## Starting the host

| Provider | Mode | Linux / macOS | Windows (PowerShell) |
|---|---|---|---|
| **Claude Code** | CLI | `./claude-pp` | `.\claude-pp` |
| | VS Code extension | reload the window, open the workspace | same |
| **Codex** | CLI | `codex` — the project config carries the rules (trust the project when Codex asks) | same |
| | VS Code extension | open the workspace | same |
| **Gemini** | CLI | `./gemini-pp` | `.\gemini-pp` |
| | CLI Companion (VS Code) | open the workspace | same |
| **Cursor** | CLI | `cursor-agent` — Cursor's own terminal agent, installed separately | same |
| | the IDE | open the workspace | same |

## What a session looks like

The blocks, checkpoints and repairs are agent and conductor talking to each other
**in tool calls**. They are not a second interface you have to drive. You ask, and
you get an answer followed by the next decisions:

```
you:   update the parser and keep the documentation work visible

agent: The parser and its tests are updated. The README pass remains open.

       | # | your best choice(s) |
       |---|---|
       | 1 | Review the README rewrite, which unlocks the public documentation pass. |
```

The choices at the end come from the `steering` package, which keeps the steps of
work across sessions. The only visible cost is a small **delay**: staging each
step takes a round trip through the harness.

## Day-two gestures

They ride the console the install wrote at the workspace root (`.\pp` on Windows):

| gesture | what it does |
|---|---|
| `./pp upgrade` | moves the instance to the source's current versions |
| `./pp add <package>` | installs one more package and its prerequisites |
| `./pp doctor` | repairs the instance in place |
| `./pp -install -codex` | wires one more harness onto the standing instance (any host flag, no workspace) |
| `./pp help` | lists every verb, the packages' own included |

The full console is in [the reference](reference/console.md).

## Try it with Daneel

The repository ships a demonstration persona, **R. Daneel Olivaw**, an homage to
Isaac Asimov's humaniform robot:

```sh
uv run pp/engine/pp.py -install <workspace> daneel -<provider>
```

or `./pp add daneel` in an instance you already have. Then launch the host and say
hello. His **Laws** never fade — ask him to break one and watch the refusal — and
his nature holds turn after turn because it is served, not remembered. See
[packages/daneel](../packages/daneel/README.md); Daneel is excluded from the core's
Apache license ([NOTICE](../packages/daneel/NOTICE.md)).

## See also

- [The conduction](conduction.md) — why a conductor, and the two ways to conduct
- [The adapters](../adapters/) — one page per coding agent
- [The reference](../REFERENCE.md) — every keyword, command and file
