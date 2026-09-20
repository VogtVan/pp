# plan

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.1.40`

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
- Which component-scoped phases let the whole system converge cleanly?
- What is the largest unit that can be applied, verified and closed in one turn?
- Which decisions belong to the operator before implementation begins?
- What is the deepest plan node that now awaits framing, implementation or rework?

## Features

### `PLAN` — structure the undertaking

Turns a mature chat framing into the root document of an undertaking. An existing
artifact is surveyed before the target is set; phases are then prepared by component,
with observable completion criteria and the references that ground all work below.

A plan is the top of a fixed three-level tree: plan, phases, batches. Its document
holds the thesis, current survey, target, expected result, operator decisions and the
prepared phases. Rules belong here only when every batch can violate them; narrower
rules descend to the phase or batch where they apply.

Nothing is created merely because a direction appeared in conversation. The agent
first develops the framing with the operator, proposes a plan when it is mature, and
waits for the GO that names it.

### `PHASE` — converge one component

Makes one component the milestone between the plan and its executable work. The
phase begins by zooming out over its sources, touched code and dependents, then
prepares the batches required to bring that component to a clean end state.

The path through a phase may include breaking changes, but the phase itself closes
only after the component and its dependents converge. A small undertaking still has
one phase; a larger one has several. The phase is never skipped, and implementation
does not happen at this level.

### `BATCH` — deliver one bounded unit of work

Defines the only implementation unit of a plan: the largest piece one turn can open,
apply, verify and close. Its framing records the surrounding ground, touched and
dependent code, target, observable result, proof, todos and open arbitrations before
its own rules are added last.

Implementation starts only on a GO that names the batch. Upstream dependencies are
verified first, todos are completed as their work lands, and proof runs on a
disposable path rather than the operator's live world. When only a live run can prove
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

At the end of the turn, that line joins the existing plan thread in `steering`.
It describes the next move but never plays it: framing, implementation and rework
remain operator decisions.

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

## Installation

`plan` requires `steering`, which requires the `kit`; the installer pulls both
automatically.

For a new workspace:

```sh
uv run procedural-prompting/engine/pp.py -install <workspace> plan -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add plan
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start). Plan-shaped work enters plan mode during
the turn, and each open plan's next move reaches the steering surface at its end.

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
decision through `steering`.
