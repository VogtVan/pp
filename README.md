<img src="PP.png" alt="PP" width="150"> 

# Procedural Prompting

**A lightweight, programmable harness for existing coding agents.**

*Stop asking the agent to manage its own instructions. Serve the right context and
constraints, exactly when they apply.*

Procedural Prompting gives an agent the context, constraints, tools and source
material it needs, at the moment it needs them.

Instead of maintaining one large instruction block and expecting the model to
remember which rules apply, you define **composable procedures**. The harness serves
the relevant documents, scopes and re-emits the active constraints, then hands
control back to the agent inside the environment you already use.

It does not replace Claude Code, Codex, Cursor, VS Code or another agent runtime.
It plugs into them through thin harness adapters — Claude Code, Codex CLI, Gemini
CLI and Cursor are each wired by one install flag; any other environment integrates
through the generic hook contract.

A procedure can be as small as serving one reference document before a task, or as
elaborate as a complete development, review or document-production workflow.
Procedures compose through calls, hooks, overlays and scoped constraints.

The model still performs the work. Procedural Prompting prepares and frames each step.

## Context grows. Monolithic prompts do not scale.

Agent instructions rarely stay small. A project begins with a few conventions,
then accumulates coding rules, review policies, document references, tool
restrictions, workflows and exceptions.

Placed in one permanent context file, these instructions gradually become
harder to maintain. Rules remain active outside the tasks they were written
for, obsolete guidance survives because removing it feels risky, and every new
requirement increases the burden placed on both the model and the person
maintaining the prompt.

Procedural Prompting turns that growing instruction block into a context
architecture.

Instructions live in named documents. Constraints have an explicit scope.
Procedures decide when material enters the context, how it composes with what
is already active, and when it falls away. The result remains readable,
reviewable and extensible as the project grows.

That is the wall I hit in my own workspaces; Procedural Prompting is that
architecture, externalized.

## A step, staged

A procedure is a plain markdown document. This complete example stages a review:
one reference served by the tool, two production laws scoped to the work, and one
verdict requested in a declared form:

```
---
name: REVIEW
kind: proc
description: review a draft against the house rules, then hand down a verdict
output: line
serve: |
  draft.md
constraints.production: |
  C1  you judge the draft; you never rewrite it.
  C2  a finding without the line it comes from is no finding.
proc: |
  SERVE
  INFER
---

Hand down ONE verdict — approve, revise or reject — and the findings that carry it.
```

The agent calls pp and receives the step, fully staged. The output has its own run
heading; the procedure heading below names the active frame and its position:

```
▌ pp · run <key> · … · <time> · +<elapsed>

▌ REVIEW{2/2}

▌ INFORMATION — draft.md
(… the draft, served by the tool …)

▌ NEXT INSTRUCTION CONTEXT — REVIEW
Hand down ONE verdict — approve, revise or reject — and the findings that carry it.

▌ CONSTRAINTS
production:
C1  you judge the draft; you never rewrite it.
C2  a finding without the line it comes from is no finding.

▌ INSTRUCTION
INFER line => chat

▶ CONTINUE
./pp <key>
```

`C1` and `C2` travel with the frame and disappear when it ends. Depending on the
configured conduction effort, later blocks repeat their full text or their codes;
the scope itself does not change. Inside that scope, the agent's judgment stays
its own.

Because these are laws of production, the engine injects a checkpoint before the
answer leaves:

```
▌ INSTRUCTION
INFER proof [C1 C2] on all produced areas => tool (heredoc)

▶ CONTINUE
./pp <key> -
```

There is no proof switch and no author-written `PROVE` step. The engine decides
where a checkpoint is owed. If the proof fails — a rewrite where a verdict was
asked, for example — the same document returns with the miss named in
`DEVIATION`; the repair happens before anything reaches the operator. After the
configured repair bound, pp hands control back rather than pretending the step
succeeded. The full mechanics live in the [reference](REFERENCE.md).

## Core, kit, packages

Procedural Prompting is split into three layers:

| Layer | Current version | Role |
|---|---|---|
| **Core** | `0.1.0-beta.14` | The deterministic engine: it interprets procedures, holds runs and frame stacks, serves readings, scopes constraints, injects checkpoints, composes packages and renders the next block. |
| **Kit** | `0.1.107` | The **default turn model** built on the core: `BOOT` opens a session; `TURN` takes one operator message through `WORK` to `FINAL`; `boot.ready`, `turn.begin` and `turn.end` are its extension sockets. |
| **Packages** | independently versioned | Complete capabilities that plug into that model through declared procedures, skills, settings and contributions. |

The analogy is a kernel, a default session process, then applications. The core
does not require the kit: an alternative base package can define another boot,
turn model and interaction paradigm. The packages shipped in this repository
deliberately target the kit, directly or through another package. The kit is
optional at the core boundary; it is the required base for the packages shipped
here.

## Features

### Out of the box

The core:

- **Stages the right context** — one block at a time: the documents the step needs,
  one instruction, the form of the answer and the exact call back.
- **Scopes constraints structurally** — a law is pushed with its frame, remains in
  force through nested work and disappears when that frame ends. Its lifetime no
  longer depends on the model remembering where it came from.
- **Proves work before it leaves** — a law of production arms checkpoints at the
  frontiers where the work can escape. Failed proofs repair before delivery, within
  an explicit bound.
- **Performs the readings** — pp reads and injects the source material itself,
  tracks it by content and says when a host limit requires another chunk. The model
  does not certify its own reading.
- **Composes without patching** — calls, sockets, overlays, mounts, providers and
  sinks extend one procedure or package from another while each source stays intact.
- **Plugs into existing harnesses** — Claude Code, Codex, Gemini and Cursor each
  wired by one install flag; any other environment through one contract (`-hook`:
  the pending block, plaintext, on stdout).

### Runtime and operational features

- **Keeps conversations apart** — every conversation has its own run and key; the
  procedure stack survives between invocations and can be restored after a declared
  host compaction.
- **Fits the host** — readings and blocks are cut below the declared harness cap;
  instruction fusion and procedure-body repetition trade weight for visibility.
- **Controls every production** — formats determine shape and transport, pipelines
  carry outputs between steps, and a declared `FINAL` is the only exchange frontier.
- **Bounds failure** — validation misses and failed proofs reopen the relevant work
  within the configured repair bound; unresolved state becomes a named refusal with
  exit 2 and no partial advance.
- **Scopes tools with the work** — procedures expose only their declared offers;
  conducted skills add their own constraints while they run, and package scripts
  execute through pp.
- **Validates the composition** — package dependencies, public names, sockets,
  formats and contributions are checked before the composition is materialized.
- **Switches packages without uninstalling them** — a package can leave one run or
  the durable play; everything that requires it leaves with it, and the base stays.
- **Leaves a trace** — blocks, readings, gestures, proofs, refusals and timings are
  recorded per run so the conduction can be inspected and measured.
- **Carries its machine** — an instance contains its engine, pinned packages, state
  and records. Clone it, back it up or restore it and the procedural layer travels
  with the workspace.

The instance root remains the operator's space. Put your own conducted documents
in `.pp/procs/`, extend bundled procedures with same-name overlays, attach work to
declared sockets, redeclare formats and settings at home, and adopt harness skills
with `+name`. The engine composes that surface without editing its pinned packages.

## Quick start

**Linux / macOS**

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh     # uv: brings Python, no setup needed
git clone https://github.com/VogtVan/pp.git
uv run pp/engine/pp.py -install <workspace> -<provider>
```

**Windows** (PowerShell)

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/VogtVan/pp.git
uv run pp\engine\pp.py -install <workspace> -<provider>
```

`<workspace>` below is any path — pick a name, `install` creates it. Keep it a
**sibling** of the clone, not nested inside it. `<provider>` is the harness you
run pp under — `claude`, `codex`, `gemini` or `cursor`, so the flag reads
`-claude`, `-codex`, `-gemini` or `-cursor`; the table below says what each one
gives. The commands abbreviate
`uv run pp/engine/pp.py` (Windows: `\` as separator); the
flags are **cumulable** in one install, and pp wires the **harness**, never the
model — the model running underneath is the harness's own choice.

### Two modes, two guarantees

You will use pp in one of two **modes** — **CLI** (the host launched from a
terminal) or **VS Code extension** (a panel, nothing to launch) — and the mode
decides which **guarantee** holds the conduction:

- **marble** — the standing rules ride the host's **own system prompt**: pinned at
  launch, they hold for the whole session, compaction included; pp only ever
  appends them.
- **recall** — the taught reflex: the doors and the registered card, re-armed by
  every block.

| Provider | Mode | Install | Guarantee |
|---|---|---|---|
| **Claude Code** ([ref](adapters/claude/README.md)) | CLI | `-install <workspace> -claude` | **marble** |
| | VS Code extension | same install | recall |
| **Codex** ([ref](adapters/codex/README.md)) | CLI | `-install <workspace> -codex` | **marble** |
| | VS Code extension | same install | **marble** — the extension shares the CLI's config layers |
| **Gemini** ([ref](adapters/gemini/README.md)) | CLI | `-install <workspace> -gemini` — the `gemini` CLI must be on PATH | **marble** |
| | CLI Companion (VS Code) | same install | recall |
| **Cursor** ([ref](adapters/cursor/README.md)) | CLI (`cursor-agent`) | `-install <workspace> -cursor` | recall — no system-prompt channel on Cursor |
| | the IDE | same install | recall — one install covers every model Cursor runs |

The install writes the instance (`<workspace>/.pp`) and, per flag, that harness's
**door** — the pointer file it reads on its own: `CLAUDE.md` for `-claude`,
`AGENTS.md` for `-codex`, `GEMINI.md` for `-gemini`; `-cursor` writes
`AGENTS.md` and `CLAUDE.md` as Cursor-recognized doors, plus `GEMINI.md` so the
same workspace stays ready for Gemini — its **card** — the conductor's usage contract,
registered where that harness lists its skills or commands — and the marble wiring
where the harness allows it. With no flag, the two generic doors (`CLAUDE.md`,
`AGENTS.md`) are written for you to wire a harness yourself. Launching comes next:
[Using it](#using-it) has the commands, and each provider has its own page under
[adapters/](adapters/).

> **Everything stays in the workspace.** Whatever the provider, the install writes
> **inside `<workspace>` only** — never in your home directory, never in a provider's
> global configuration: your other repositories and your provider agents elsewhere
> are untouched. The launchers act per invocation (a flag, an environment variable);
> project-scoped config applies to this project alone.

> **The model is untouched.** pp alters none of the LLM's capabilities or the
> underlying tool implementations — it is a conduction layer, nothing more. A
> procedure may scope which harness tools are exposed to the current step;
> inside that frame, the model's reasoning and judgment remain those provided
> by the harness.

**Only the Claude Code environment has been exercised end to end.** The Codex,
Gemini and Cursor integrations were prepared from their official documentation
alone — problems may surface there; please report them.

**The Windows path is untested.** The `.cmd` launchers and the Windows commands
were written from documented batch semantics on a Linux bench — report anything
that misbehaves.

**The procedure, package and adapter formats are experimental** and may evolve
between versions.

## Using it

The blocks, readings, checkpoints, closings (`CONTINUE` / `FINAL`) and repairs are
agent and conductor talking to each other **in tool calls**. They do not become a
second interface the operator has to drive.

Add the `steering` package and one exchange illustrates the composition. The kit
owns the turn; steering attaches its own pass at `turn.end`, then calls the surface
that returns the current initiatives:

```text
▌ TURN{…}
  the operator's work

▌ TURN ▸ THREADS{1/2}
  keep the initiatives and their steps true

▌ TURN ▸ THREADS ▸ NEXT{1/1}
  render the work that is due and the decisions still owed
```

Those are real procedure boundaries, not headings the model invented. `TURN` comes
from the kit; `THREADS` and `NEXT` come from `steering`. Their constraints and tools
accumulate down the displayed stack and fall away as each frame closes.

What reaches the operator is the answer, followed by the actionable surface:

```
you:   update the parser and keep the documentation work visible

agent: The parser and its tests are updated. The README pass remains open.

       | initiative | note | progress | age | next action(s) |
       |---|---|---|---|---|
       | documentation | align the public surface | ▰▰▰▱▱ 3/5 | now | `rewrite-readme` · `review-links` |

       | # | your best choice(s) |
       |---|---|
       | 1 | Review the README rewrite, which unlocks the public documentation pass. |
```

You ask, you get an answer and the next decisions. The only visible operational
difference is a small **delay**: staging each step requires a round trip through the
harness. The context management and the continuity of the work no longer rest on
the agent's memory.

**Starting the host**, per provider and mode — the guarantees each combination
holds are in [Quick start](#quick-start):

| Provider | Mode | Linux / macOS | Windows (PowerShell) |
|---|---|---|---|
| **Claude Code** ([ref](adapters/claude/README.md)) | CLI | `./claude-pp` | `.\claude-pp` |
| | VS Code extension | reload the window, open the workspace | same |
| **Codex** ([ref](adapters/codex/README.md)) | CLI | `codex` — the project config carries the rules (trust the project when Codex asks) | same — the config is OS-neutral |
| | VS Code extension | open the workspace | same |
| **Gemini** ([ref](adapters/gemini/README.md)) | CLI | `./gemini-pp` | `.\gemini-pp` |
| | CLI Companion (VS Code) | open the workspace | same |
| **Cursor** ([ref](adapters/cursor/README.md)) | CLI | `cursor-agent` — Cursor's own terminal agent, installed separately from cursor.com | same |
| | the IDE | open the workspace | same |

**Day-two gestures** ride the console the install wrote at the workspace root:
`./pp upgrade` moves the instance to the source's current versions, `./pp add
<package>` installs one more package ([Demo](#demo--meet-daneel) uses it),
`./pp doctor` repairs in place, and `./pp -install -codex` (any host flag, no
workspace) wires one more harness onto the standing instance — write-once, a
replay answers `already wired`; a package's own verbs (`commands:` in its
manifest) answer the same console, listed by `./pp help` after its own.
Windows spells it `.\pp`. The full console —
every verb, and why the file is the machine's own — is in the
[reference](REFERENCE.md#the-operators-console).

## Demo — meet Daneel

> Daneel is a **demonstration package** — separately identified and **excluded
> from the core's MIT license**: see [License](#license) and
> [packages/daneel/NOTICE.md](packages/daneel/NOTICE.md).

The repository ships a demonstration persona: **R. Daneel Olivaw**, an homage to
Isaac Asimov's humaniform robot. Name `daneel` at install time:

```sh
uv run pp/engine/pp.py -install <workspace> daneel -<provider>
```

or add it to an instance you already have — from the workspace, through the
console the install wrote there:

```sh
./pp add daneel
```

Then launch the host and say hello. What the sections above describe becomes a
character you can talk to: the **Laws** (quoted, attributed) never fade — ask him
to break one and watch the refusal, courteous and reasoned; the **nature** — calm,
literal, no contractions, "Partner" — holds turn after turn because it is served,
not remembered; and every answer is **proven** against the Laws before it reaches
you. One session tells you more about conduction than any paragraph here.

Daneel takes the identity seat (`MEMBER.md`): on a lived-in instance the tool says
so first, saves your file to `.old`, and offers a fresh sibling workspace instead —
the comfortable path.

## Optional packages

The core and kit stay small. Install only the applications the workspace needs;
`install` and `./pp add <package>` pull their declared prerequisites automatically.

> **All packages below are experimental.** Their procedures, settings, records,
> contribution contracts and user-facing behavior may change between versions.
> Pin their versions and expect migration work when upgrading.

| Package | Current version | What it adds | Requires |
|---|---|---|---|
| **[`authoring`](packages/authoring/README.md)** | `0.1.12` | The authoring face of pp: guided doors for the member, rules, offers, migrations and procedure design, plus the author reference and cheatsheet. | `kit` |
| **[`steering`](packages/steering/README.md)** | `0.7.3` | Persistent initiatives and ordered steps, maintained during the turn and rendered as the operator's actionable `NEXT` surface. | `kit` |
| **[`continuity`](packages/continuity/README.md)** | `0.1.0` | A dated operations record, session recall and a weekly digest, each with its own cadence and budget. | `kit` |
| **[`plan`](packages/plan/README.md)** | `0.1.40` | Plans as documents: plans, phases and batches with explicit state, readings, expected renderings and operator-controlled implementation arbitrations. | `steering` |
| **[`monitoring`](packages/monitoring/README.md)** | `0.1.0` | Analysis of the trace the core already records: scenario runs, package measurements and comparable reports. | `kit` |
| **[`daneel`](packages/daneel/README.md)** | `0.1.0` | The demonstration persona above: a durable nature and attributed Laws, under its separate demonstration license. | `kit` |

Every package is independently versioned and declares where it contributes. A
package extends the composition; it does not patch the core or the package it
depends on.

## What pp weighs in a session

pp weighs **5 % to 20 %** of a session, depending on the degree of conduction set
in the settings.

The first exchange — the boot — carries the heaviest weight and the most
noticeable latency: pp serves there what the rest of the session will not be
served again. It does not come back.

A high degree of conduction asks for a comfortable context window.

## Going further

The mechanics — the block's anatomy, the procedure keywords, writing and composing
your own procedures, what happens when an answer misses, the adapter surface, the
hook channel for any other environment, the operator's console, the instance on
disk — live in the [reference](REFERENCE.md); each provider has its own page
under [adapters/](adapters/).

## License

Procedural Prompting **core: MIT** — [LICENSE](LICENSE) (a scope preamble, then
the canonical MIT text; also at [LICENSES/MIT.txt](LICENSES/MIT.txt)).

The **Daneel demonstration package** (`packages/daneel/`) is **separately
identified and excluded from MIT** — demonstration-only terms in
[LICENSES/LicenseRef-Daneel-Demonstration.txt](LICENSES/LicenseRef-Daneel-Demonstration.txt),
status in [packages/daneel/NOTICE.md](packages/daneel/NOTICE.md).
