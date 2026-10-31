# plan

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.2.1`

`plan` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace a durable structure for an undertaking: one plan, component-scoped
phases and batches sized to be framed, implemented, verified and closed in one turn.

The package separates framing from implementation. Direction takes shape in the chat,
the operator's GO creates and frames the named node, and a separate GO authorizes the
work that framing defined.

## Role

Complex work needs more than a checklist. Its intent, component boundaries, proof,
decisions and current position must survive across turns without asking the model to
reconstruct them from conversation history. `plan` keeps those facts in a fixed tree
of documents under `.pp/plans/<slug>/` and derives progress from what they contain.

It provides a method for answering five recurring questions:

- What undertaking is being conducted, and what observable result closes it?
- How is the work laid out -- one phase per component, or one phase with one batch per
  component -- so that each component converges cleanly?
- What is the largest unit that can be applied, verified and closed in one turn?
- Which decisions belong to the operator before implementation begins?
- What is the deepest plan node that now awaits framing, implementation or rework?

## Features

### `PLAN` — structure the undertaking

Turns a mature chat framing into the root document of an undertaking. An existing
artifact is surveyed before the target is set; phases are then prepared -- one per
component, or one phase alone for fixes or a short rework -- with observable completion criteria and the references that ground all work below.

A plan is the top of a fixed three-level tree: plan, phases, batches. Its document
holds the thesis, current survey, target, expected result, operator decisions and the
prepared phases. At its Protocol, the plan also recommends how the project is laid
out so that its batches can be proven at the right size: the code arranged by domains
and namespaces, and the tests arranged to mirror them. Rules belong here only when every batch can violate them; narrower
rules descend to the phase or batch where they apply. A rule, once posed, is retired
or amended on the operator's word alone: the agent stops and asks first.

Nothing is created merely because a direction appeared in conversation. The agent
first develops the framing with the operator, proposes a plan when it is mature, and
waits for the GO that names it.

### `PHASE` — the convergence milestone

Makes the milestone between the plan and its executable work: one component when the
plan is laid out one phase per component, the whole plan when it is laid out as one
phase with one batch per component. The phase begins by zooming out over its sources,
touched code and dependents, then prepares the batches that bring its subject to a
clean end state.

The path through a phase may include breaking changes; what closes follows the subject a
node carries. The node that carries a whole component -- the phase in the first layout,
the batch in the second -- is recommended not to close before the test suite of that
component and of the components that depend on it is green, run once. The project's
whole suite is the plan's to run, at its last batch. The phase is never skipped, and
implementation does not happen at this level.

### `BATCH` — deliver one bounded unit of work

Defines the only implementation unit of a plan: the largest piece one turn can open,
apply, verify and close. Its framing records the surrounding ground, touched and
dependent code, target, observable result, proof, todos and open arbitrations before
its own rules are added last.

Implementation starts only on a GO that names the batch. Upstream dependencies are
verified first, todos are completed as their work lands, and proof runs on a
disposable path rather than the operator's live world. The tests a batch runs are
the tests its changes impact, and those alone, once -- never twice; a flaky test met on
the way is hunted when it appears and never left for long. When only a live run can prove
a behavior, that verification remains the operator's gate. Delivery closes the batch
only when every todo is done, the expected result is demonstrated and the readings
match what actually moved. Work that cannot close honestly is stopped and reported
instead of stretching the batch.

Later work that revisits what a closed batch established reopens that batch and
appends to its history; it does not create a parallel replacement for the same work.

### `NEXT_MOVE` — carry the next GO to the operator

After a plan mutation, the package computes the deepest node that awaits something
and describes the GO it needs. One current line is kept per open plan, replaced as
the work advances and cleared when the plan is complete.

`steering` is optional. When it is installed, `NEXT_MOVE` plays with the steering
pass at the end of each exchange: the line is read after the work, so it says what the
plans ask for now, and the pass carries it into the existing plan thread. Without
`steering`, `NEXT_MOVE` stays idle (the build says so once) and `pp-plan next-move`
reads the line on demand. Either way it describes the next move but never plays it:
framing, implementation and rework remain operator decisions.

### `PLANS` — the plans at a glance

`./pp <key> -open PLANS` opens the plans space (plan 0.1.52). Its welcome, `PLANS-BOARD`,
reads `pp-plan status --all --engaged --json` once and has the agent say the board as tables:
the open plans with their progress and their next move, the phases and batches under way,
the closed plans in one line, and the steps of the run that are tied to a plan by their key --
the ones the run already holds, never a reading of `steering`. The plan cheat sheet
(`refs/PLAN_CHEATSHEET.md`) is no longer served at every turn: it arrives with the opening of the
space or with the first mount of a plan in the run, and is spared after that (plan 0.1.53). From
there the agent frames, mounts and delivers as at the turn; each message ends on the proof of the laws in force;
`-close` gives the turn back. `pp-plan status` itself is a LIST: one line per node, the open
plans with their next move and the closed ones counted (`--all`), the engaged nodes under each
open plan (`--engaged`), one plan whole with its todos counted (`status <slug>`), the same as
data (`--json`).

### Operator involvement in implementation

Two `plan_` settings control how framing arbitrations return before coding. The
operator's explicit GO always supersedes both.

- `plan_implementation_care` ranges from agent-owned decisions (`none`) through
  recorded or reported decisions (`traced`, `told`) to approval gates (`asked`,
  `total`). Its default is `asked`.
- `plan_implementation_control` selects the sectors watched by `asked` from
  `architecture`, `contracts`, `naming`, `data` and `flow`. Its default is
  `architecture | contracts`.

Statuses require no separate bookkeeping command from the operator. Writing the
expected result makes a node active, delivery closes it through the tree, and
rewriting a framing section reopens the affected ancestry for rework.

### The material of a plan

A plan whose code lives in another tree — a git worktree, a branch checked out beside
the repository — says it once: `pp-plan material <slug> [<name>]` writes `material: <name>`
on the plan and on every phase and batch born under it, and every node born later copies
it. The name is a tree the operator declares in `SETTINGS.md`, `material.<name>: <path>`;
a name not declared is refused and nothing is written. A mount then serves the node's
readings from that tree, each titled with its material (`engine/x.py @core`). A document
of the repository itself — a README, a design note — keeps its row marked `@repo`, and
`serve` reminds the agent when a row on such a plan is left unmarked.

## Installation

`plan` requires the `kit`, which the installer pulls automatically. `steering` is
optional: install it beside `plan` to have each plan's next move carried into the work
threads.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> plan -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add plan
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start). Plan-shaped work enters plan mode during
the turn, and with `steering` each open plan's next move reaches the work threads at its end.

## Quick start

Begin with the undertaking rather than a file operation. Ask the conducted agent to
help shape the direction and survey what already exists:

```text
I want to replace the current cache without changing the public API. Help me frame
the undertaking as a plan: survey the existing components, identify the convergence
phases and bring the open decisions back to me.
```

Review the proposed thesis, boundaries, observable result and phases. When they are
right, give a GO that names the plan framing. The same rhythm then continues down the
tree:

```text
GO, frame the cache replacement plan.

Frame the storage phase.

Frame the invalidation batch.

GO, implement the invalidation batch.
```

Each approval names only the step it authorizes. A framing GO does not authorize its
implementation, and a question or defect report is not a GO. The package keeps the
plan documents and statuses aligned as the work advances and returns the next required
decision -- through `steering` when it is installed, through `pp-plan next-move` otherwise.
