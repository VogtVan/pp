# Procedural Prompting — the reference

The mechanics behind the [README](README.md): the block, the language, your
own procedures, what happens when an answer misses, and the instance on disk.

## Why a conductor

A language model is excellent at judgment and poor at bookkeeping. Ask one to
follow a long procedure and you have handed it two jobs at once: the work, and
the management of the work — the current position, the rules in force, what
was already read, what comes next.

It performs the second job from memory, and memory is exactly where a model
degrades: instructions stated once fade as the context grows, scope creeps
because nothing structural resists it, and a reading is *claimed* rather than
proven.

Procedural Prompting externalizes the bookkeeping. A small deterministic
**conductor** plays the procedure and hands the model **one output at a
time**. The model's freedom is untouched *inside* the step — judgment,
wording, reasoning stay its own. The **limits** around the step are not its
concern anymore: it does not track them, so it cannot lose them. And the
limits are **yours to write**: what you put in a procedure is what every block
will enforce — the specification holds because it never leaves the screen.

## How this reference is organised

It documents both faces of the product, one file per subject under
[`docs/reference/`](docs/reference/):

- the **user face** — what an operator builds and tunes: procedures,
  settings, packages;
- the **agent face** — what a conducted model consumes: blocks, commands,
  channels, repairs.

Its overlap with the agent's own card and with the catalogue of the engine's
patterns ([`engine/patterns/README.md`](engine/patterns/README.md)) is
deliberate: same mechanics, technical wording. This reference is never the
source of an agent reflex.

### The user face — building and tuning

| file | what it covers |
|---|---|
| [The language](docs/reference/language.md) | the procedure language, keyword by keyword: `PICK`, `SERVE`, `CALL`, `OPEN`, `HOOK`, `WORK`, `INFER`, `PROVE`, `AWAIT`, `§` |
| [The front matter and your own procedures](docs/reference/front-matter.md) | the front matter key by key; writing procedures, settings, overlays and laws |
| [Skills and the author's hall](docs/reference/skills.md) | offered skills, what a script prints, the scope, adoption; the author's hall |
| [The operator's console](docs/reference/console.md) | the verbs, the packages' commands, which instance a call addresses, where the machine lives, switching a package off |
| [The adapter surface](docs/reference/adapters.md) | what each host adapter provides, the non-interactive face, the hook channel |
| [The instance on disk](docs/reference/instance.md) | the tree of an instance, runs and their calls, maintenance, upgrades, purges, cadences, the marble, what the build refuses |

### The agent face — consuming the conduction

| file | what it covers |
|---|---|
| [The loop and the commands](docs/reference/agent-face.md) | the loop of a conducted agent and every `./pp` command it types |
| [The block and the channels](docs/reference/block.md) | the block section by section, the channels and the delivery, the two conduction modes |
| [The bus, the diagnostics and the misses](docs/reference/misses.md) | the bus, the diagnostics, what counts as a miss and how it repairs |

### The packages

Each package documents its own surface in its README:

| package | what it covers |
|---|---|
| [agent](packages/agent/README.md#reference) | the house: agents as instances, their runs, conversations and records |
| [team](packages/team/README.md#reference) | teams: declaration, the tick, acts and routes, limits, ceremonies, the journal |
| [ui](packages/ui/README.md#reference) | the post of a house: its tabs, gestures and panes |
| [plan](packages/plan/README.md), [steering](packages/steering/README.md), [continuity](packages/continuity/README.md), [authoring](packages/authoring/README.md), [monitoring](packages/monitoring/README.md) | their skills and documents |
