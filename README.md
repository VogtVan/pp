<img src="docs/images/PP.png" alt="PP" width="120">

# Procedural Prompting

**Your coding agents, as a team. Your repositories, in one house.**

<img src="docs/images/pp-chat.png" alt="The pp post: a conversation with the house, its cost and its next choices" width="640">

**[📸 See the post in pictures →](docs/screenshots.md)**

Give each repository its own agent. Write down who reports to whom. Post a task,
then watch Claude, Codex or Gemini agents hand work to one another, ask you when
they need you, and stop within the budget you set.

## What you get

**🏠 One house, many repositories.** One central workspace holds every agent. Give a
run a repository (`--work <repository>`) and it works on its own clone and its own
branch, pushed back to that repository after every exchange. One engine, one upgrade, for all of them.

**🤖 Agents that work without you.** An agent wakes on a message, works in the
background, and keeps its answer for you. Talk to it in a conversation, or let it
run while you do something else.

**👥 Teams that organise themselves.** Agents delegate, ask and answer one another.
A small process with no model keeps the team moving: it routes every message,
reminds the agent who owes an answer, and brings back to you what only you can
decide. Nine ready-made shapes: lead and reviewers, chain, council, triage, tree…

**🖥️ One screen for everything.** `./pp ui` shows your conversations, your agents
and your teams side by side: who is working, who is waiting, what each task cost,
and the whole exchange behind every answer.

**📜 Rules that never fade.** An agent's rules are not a wall of text it must
remember. They are served at the very step they apply to, and every answer is
checked against them before it leaves. Break one, and the agent repairs its work
before you ever see it.

**💰 Every dollar counted.** Budgets per team, limits per task, timeouts per
launch. When a limit is reached, nothing more is launched and you get a notice.
Every run says what it cost and how full its context is.

## The house

```
house/
├── .pp/                  the house: one engine, its packages, its records
│   └── procs/HOUSE.md    the rules, readings, tools and house procs every agent shares
├── agents/
│   ├── backend/          an agent — works on ../backend, one clone per run
│   │   └── .pp/procs/    its own procs, beside its MEMBER.md (who it is)
│   ├── frontend/         an agent — works on ../frontend
│   └── reviewer/         an agent — reads what the others push
└── teams/
    └── release/
        ├── TEAM.md       who is in the team, who reports to whom, the limits
        └── TEAM-release.md   what the team is for
```

An agent is just a directory under the house. It borrows the house's engine and
packages, so there is nothing to install twice and nothing to keep in sync. The
house keeps every message, every answer and every cost in one place.

## Why it holds

Each agent runs under a **conductor**: a small, deterministic program that holds
the procedure, the rules and the position in the work, and hands the model one
step at a time. The model keeps its judgment. It no longer has to keep track of
its own instructions, so it cannot lose them.

That is what lets a team of agents run for hours and stay on track. How it works:
[the conduction](docs/conduction.md).

## Quick start

**On Linux / macOS:**

```sh
curl -LsSf https://raw.githubusercontent.com/VogtVan/pp/main/install.sh | sh
```


**On Windows:** [Download ZIP](https://github.com/VogtVan/pp/archive/refs/heads/main.zip),
extract it, then double-click `pp-install.cmd`.

Alternative (cmd or PowerShell):

```bat
powershell -ExecutionPolicy ByPass -c "irm https://raw.githubusercontent.com/VogtVan/pp/main/install.ps1 | iex"
```

Options and details: [installing pp](docs/install.md).

Then, from the house:

| you want to | Linux / macOS | Windows (cmd) |
|---|---|---|
| open the post | `./pp ui`, or `../pp-ui` | `pp ui`, or double-click `pp-ui.cmd` beside the house |
| update everything | `./pp upgrade` | `pp upgrade`, or double-click `pp-install.cmd` again |

Everything else is done in the post; the command beside each line does the same from a
terminal:

| you want to | in the post | or type |
|---|---|---|
| create an agent | Agents tab, `a` | `./pp agent add agents/backend` |
| talk to it | Agents tab, `n` on the agent | `./pp agent chat agents/backend` |
| create a team | Teams tab, `N` | `./pp team new <name> --template <shape>` |
| give it a task | Teams or Tasks tab, `n` | `./pp team start <name> --message "…"` |
| see what waits for you | Teams tab, `b` | `./pp team inbox` |

> **Prefer your editor extension?** pp still conducts Claude Code, Codex, Gemini or Cursor
> directly inside your editor session, the way it started. That mode is fully
> supported for chat only; the house is the recommended way for full features. See [the editor mode](docs/editor-mode.md). You can also open pp in any command terminal of your editor.

## Packages

The house is built from packages. Install only what you need; `./pp add <package>`
brings its prerequisites with it.

| | package | what it adds |
|---|---|---|
| **the house** | [`agent`](packages/agent/README.md) | agents under the house, woken by a message, held in conversation |
| | [`team`](packages/team/README.md) | teams of agents: delegation, limits, ceremonies, one inbox |
| | [`ui`](packages/ui/README.md) | the post: one terminal screen for conversations, agents and teams |
| **the workshop** | [`plan`](packages/plan/README.md) | plans, phases and batches, framed and delivered on your GO |
| | [`steering`](packages/steering/README.md) | the steps of work kept across sessions, and your two next choices |
| | [`continuity`](packages/continuity/README.md) | a dated record of the work done, recalled at every session |
| | [`authoring`](packages/authoring/README.md) | guided doors to write your own rules and procedures |
| | [`monitoring`](packages/monitoring/README.md) | measures of what the conduction costs |
| **a demo** | [`daneel`](packages/daneel/README.md) | R. Daneel Olivaw, a persona whose Laws never fade |

## Main features

- **A conductor.** A small deterministic program plays the procedure and hands the
  model one step at a time: the documents that step needs, the rules in force, one
  instruction and the form of the answer. It reads the sources itself, keeps the
  position and the rules across nested work, and records every step in a trace. The
  model keeps its judgment inside the step. [The conduction](docs/conduction.md)
- **Four provider adapters.** Claude Code, Codex, Gemini and Cursor, one adapter each; the
  members of one team may run on different ones.
- **Procedures in plain markdown.** A procedure is a list of steps (`WORK`, `INFER`, `PICK`,
  `CALL`, `OPEN`, `PROVE`…); the conductor hands the model one step at a time. 47 patterns,
  each with a working example, in [engine/patterns](engine/patterns/README.md).
- **Rules that are checked.** Every rule has a code; at each checkpoint the agent proves
  the rules in force, and a broken one sends the work back for repair.
- **Teams.** Nine ready-made shapes, ceremonies at set times, budgets per team and per
  task, and one inbox for what only you can decide.
- **One clone per run.** Give a run a repository (`--work <repository>`) and it works on
  its own clone and its own branch, pushed back to that repository after every exchange.
- **Plans and memory.** Plans, phases and batches framed and delivered on your GO; the
  steps of work and a dated record of what was done, recalled at every session.
- **One screen.** The post shows conversations, agents, teams and tasks, on Linux, macOS
  and Windows. Conversations are named and stay open side by side in tabs, and the tabs
  come back when you open the post again.
- **A test bench for procedures.** A modelled agent plays your procedures before a real
  one does, and a campaign compares their answers.
- **Light.** The engine is Python with a single dependency; uv brings everything else.

## Status

**Not all providers have been exercised end to end.** Claude Code, Codex and
Cursor have been tested; Gemini was wired from its official documentation.
Please report what misbehaves. On Windows, the installer and the post have been tried
by hand (in cmd, October 2026); the rest of the Windows path is not tested yet.

**Everything stays in the house.** pp writes inside the house only: never in your
home directory, never in a provider's global configuration. It changes nothing in
the model: it decides what each step serves, never how the model thinks.

## Going further

| | |
|---|---|
| [Screenshots](docs/screenshots.md) | the post in pictures: a conversation, a team at work, the forms |
| [The conduction](docs/conduction.md) | why a conductor, how a step is staged, the two ways to conduct |
| [The editor mode](docs/editor-mode.md) | pp inside Claude Code, Codex, Gemini or Cursor, without the house |
| [The reference](REFERENCE.md) | every keyword, command and file, in detail |
| [adapters/](adapters/) | one page per coding agent |

## License

Procedural Prompting **core: Apache License 2.0** — [LICENSE](LICENSE) (a scope
preamble, then the canonical Apache 2.0 text; also at
[LICENSES/Apache-2.0.txt](LICENSES/Apache-2.0.txt)). Copyright 2026 Jean-Philippe
Labays — see [NOTICE](NOTICE).

The **Daneel demonstration package** (`packages/daneel/`) is **separately
identified and excluded from the Apache license** — demonstration-only terms in
[LICENSES/LicenseRef-Daneel-Demonstration.txt](LICENSES/LicenseRef-Daneel-Demonstration.txt),
status in [packages/daneel/NOTICE.md](packages/daneel/NOTICE.md).
