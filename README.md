<img src="PP.png" alt="PP" width="120">

# Procedural Prompting

**Your coding agents, as a team. Your repositories, in one house.**

<img src="pp-chat.png" alt="The pp post: a conversation with the house, its cost and its next choices" width="640">

**[📸 See the post in pictures →](docs/screenshots.md)**

Give each repository its own agent. Write down who reports to whom. Post a task,
then watch Claude, Codex or Gemini agents hand work to one another, ask you when
they need you, and stop within the budget you set.

All from one terminal screen. No editor to keep open, no prompt to babysit.

## See it in five commands

```sh
uv run pp/engine/pp.py -install house agent team ui -claude
cd house
./pp team new release --template lead-reviewers
./pp team start release --message "Review the open pull request and tell me if it can ship."
./pp ui
```

The first line builds the house. The third writes a team: a lead who does the work
and two reviewers who check it. The fourth gives it a task. The last opens the
post, where you follow the team member by member, read each exchange, and answer
when an agent asks you something.

## What you get

**🏠 One house, many repositories.** One central workspace holds every agent. Point
an agent at a repository and each of its runs works on its own clone and its own
branch, pushed back after every exchange. One engine, one upgrade, for all of them.

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
│   └── procs/HOUSE.md    the rules, readings and tools every agent shares
├── agents/
│   ├── backend/          an agent — works on ../backend, one clone per run
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

**Linux / macOS**

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh     # uv: brings Python, no setup needed
git clone https://github.com/VogtVan/pp.git
uv run pp/engine/pp.py -install house agent team ui -claude
```

**Windows** (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/VogtVan/pp.git
uv run pp\engine\pp.py -install house agent team ui -claude
```

Keep `house` beside the clone, not inside it. Replace `-claude` by `-codex`,
`-gemini` or `-cursor` to choose the coding agent your agents run on. Then, from
the house:

| you want to | type |
|---|---|
| open the post | `./pp ui` |
| create an agent | `./pp agent add agents/backend` |
| talk to it | `./pp agent chat agents/backend` |
| create a team | `./pp team new <name> --template <shape>` (`./pp team templates` lists them) |
| give it a task | `./pp team start <name> --message "…"` |
| see what waits for you | `./pp team inbox` |
| update everything | `./pp upgrade` |

> **Prefer your editor?** pp still conducts Claude Code, Codex, Gemini or Cursor
> directly inside your editor session, the way it started. That mode is fully
> supported; the house is the recommended way. See [the editor mode](docs/editor-mode.md).

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

## Status

**Experimental.** The formats of procedures, packages and adapters may change
between versions.

**Not all providers have been exercised end to end.** Claude Code, Codex and
Cursor have been tested; Gemini was wired from its official documentation.
Please report what misbehaves. The Windows path is untested.

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
