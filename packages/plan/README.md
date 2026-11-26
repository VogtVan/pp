# plan

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.8.0`

`plan` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace a durable structure for an undertaking: a tree of documents as deep
as the chain of its templates. On the product's templates that is one plan,
component-scoped phases, and batches sized to be framed, implemented, verified and closed
in one turn.

The package separates framing from implementation. Direction takes shape in the chat,
the operator's GO creates and frames the named node, and a separate GO authorizes the
work that framing defined.

## Role

Complex work needs more than a checklist. Its intent, component boundaries, proof,
decisions and current position must survive across turns without asking the model to
reconstruct them from conversation history. `plan` keeps those facts in a tree of
documents under `.pp/plans/<slug>/` and derives progress from what they contain.

It provides a method for answering five recurring questions:

- What undertaking is being conducted, and what observable result closes it?
- How is the work laid out -- one phase per component, or one phase with one batch per
  component -- so that each component converges cleanly?
- What is the largest unit that can be applied, verified and closed in one turn?
- Which decisions belong to the operator before implementation begins?
- What is the deepest plan node that now awaits framing, implementation or rework?

## Features

### `PLAN` — structure the undertaking

One proc, `PLAN`, conducts the work of a plan at every level. It turns a mature chat
framing into the root document of an undertaking, then frames, implements and delivers
the nodes under it, each on the operator's GO. The method of each level is not in the
proc: it is the body of that level's template (below).

On the product's `plan` template, the plan's document holds its Context (what the
undertaking is and why), its Ground (what stands before the work, read before anything
else), its Expected result, its Choices and its Items: the phases it prepares -- one per
component, or one phase alone for fixes or a short rework -- one line each, with how each
ends and how that is proved. Delivery is its journal. The plan's laws and readings are
written last, from what the framing has read. A law belongs to the plan only when every
batch under it can break it; narrower laws descend to the phase or batch where they apply.
A law, once posed, is retired or amended only on the operator's word, when a rework has
changed its context.

Only the `pp-plan` script writes a plan: one named section per call, a section the
node's template carries. No plan document is opened in an editor. A plan written in an
older form keeps the sections its template no longer carries (Target, Arbitrations,
Survey, Protocol, Decisions): the script reads, serves and keeps them, but refuses to
write them.

Nothing is created merely because a direction appeared in conversation. The agent
first develops the framing with the operator, proposes a plan when it is mature, and
waits for the GO that names it.

### Templates — the method of each level

Every node of a plan names its template (`template:` in its front matter), and its level
is read from that template. The template's front matter says the node's sections in their
order, which sections make it `doing` and which reopen it (`statuses`), whether its items
are nodes on another template (`next:`) or todos (`leaf: yes`), which of its sections a
deeper mount shows (`shown:`), and the laws of its level. The template's body is the
method of its level: the agent follows it when it works on a node of that level.

A plan is as deep as the chain of its templates. The product's chain is
`templates/plan.md` → `phase.md` → `batch.md`, the leaf. A tree may carry its own
templates under `plans/_templates/<name>.md`; they are read before the shared root's and
the product's. A plan is born on the template `--template <name>` names, on `plan`
without it, and each node under it on its parent's `next:`. `pp-plan templates [--json]`
lists the templates the tree sees; the document `PLANS-TEMPLATES` serves that list as the
reading `plan-templates` as soon as `PLAN` opens, and last at every mount, so a birth
chooses its template from it.

A mount (`pp-plan mount <address>`) shows `PLAN`, the method and laws of the template of
the node at work, the laws alone of each template above it, the sections each node above
names in `shown:`, and the node at work whole, except the sections its template marks
`unserved`. `plan-templates` comes last.

### `phase` — the convergence milestone

On the product's templates, a phase is the milestone between the plan and its executable
work: one component when the plan is laid out one phase per component, the whole plan when
it is laid out as one phase with one batch per component. Its Ground reads its sources,
the code it touches and what depends on that code, then its Items prepare the batches that
bring its subject to a clean end state.

The path through a phase may include breaking changes; the phase ends clean. The node that
carries a whole component -- the phase, by its last batch, in the first layout; the batch
in the second -- runs once the test suite of that component and of the components that
depend on it, and does not close before it is green. The project's whole suite is the
plan's to run, at its last batch. Implementation does not happen at this level: the
batches do the work.

### `batch` — deliver one bounded unit of work

On the product's templates, the batch is the leaf and the only implementation unit of a
plan: the largest piece one turn can open, apply, verify and close. Its framing writes, in
order, its Ground (the code it touches, the code around it, and what depends on it), its
readings (the touched code, then the dependent code), its Expected result, its Tests, its
Choices and its Items -- the todos -- before its own laws are added last.

Implementation starts only on a GO that names the batch. Upstream dependencies are
verified first, each todo is delivered as its work lands, and proof runs on a disposable
path rather than the operator's live world. The tests a batch runs are the tests its
changes touch, once; a flaky test met on the way is hunted as soon as it shows. When only
a live run can prove a behavior, that verification remains the operator's gate. The
readings are re-aligned on what really moved before the last todo is delivered, and that
last delivery closes the batch. Work that cannot close honestly is stopped and reported
instead of stretching the batch.

Later work that revisits what a closed batch established reopens that batch and
appends to its Delivery; it does not create a parallel replacement for the same work.

### `NEXT_MOVE` — carry the next GO to the operator

After a plan mutation, the package computes the deepest node that awaits something
and describes the GO it needs. One current line is kept per open plan, replaced as
the work advances and cleared when the plan is complete. Each line ends with the vector
of the node it names, `(plan:<address>)`, at every depth.

`next` is optional. When it is installed, `NEXT_MOVE` is attached to NEXT, at its point
`next.begin`, at the end of each exchange: the line is read after the work, so it says what the plans
ask for now, and a choice of NEXT may carry it to the operator. Without `next`,
`NEXT_MOVE` stays idle (the build says so once) and `pp-plan next-move` reads the line
on demand. Either way it describes the next move but never plays it:
framing, implementation and rework remain operator decisions.

### `PLANS` — the plans at a glance

`./pp <key> -open PLANS` opens the plans space (plan 0.1.52). Its welcome, `PLANS-BOARD`,
reads `pp-plan status --all --engaged --json` once and has the agent say the board as tables:
the open plans with their progress and their next move, the nodes under way (`doing`,
`redo`, `blocked`) each named by its template, whatever the form of the plan, the closed
plans in one line, and the steps of the run that are tied to a plan by their key --
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

Statuses require no separate bookkeeping command from the operator. Writing a `doing`
section of its template (Choices, on the product's templates) makes a node `doing`; a node
is `done` once all its items are, and the closing rises to the plan; rewriting a `redo`
section on a `done` node reopens it and its ancestors for rework.

### The vector family `plan`

The package declares one vector family, `plan:<address>`, at every depth: `plan:<slug>`
names a plan, `plan:<slug>/<node>/…` a node under it. A run that the agents' launcher
starts with `--vector plan:<address>` mounts that node at every exchange, once
`pp-plan verify` has checked that the address resolves in the tree, born or prepared. A
step of `steering` belongs to a plan, or to a node under it, when its key names it.

### The material of a plan

A plan whose code lives in another tree — a git worktree, a branch checked out beside
the repository — says it once: `pp-plan material <slug> <name> <path>` declares the tree
in the plan's own `materials:` block (the path absolute, or relative to the plan's folder)
and writes `material: <name>` on the plan and on every node born under it; every node born
later copies it. No `SETTINGS.md` is read. `material <slug> <name>` chooses a tree the plan
already declares, `material <slug> -` takes the key out everywhere, and
`material <slug> - <name>` withdraws one declaration. A name the plan does not declare is
refused and nothing is written; no tree may be called `repo` or `work`. A mount then
serves the node's readings from that tree and no other, each titled with its material
(`engine/x.py @core`); a row whose tree lacks the file is not served. A document of
another tree takes the mark of a tree the plan declares, `@<name>`, and `serve` reminds
the agent when a row on such a plan is left unmarked.

### A plan shared by several runs

A run opened with a root of documents (`--documents` of `agent run`, the team's
directory at every wake-up of a team) has a second tree of plans, `<root>/plans/`. A
plan born there by `pp-plan section <slug> Context --shared` is shared: every run opened
under the same root reads it, mounts it, frames, checks off and delivers it with the
same verbs, each write under the plan's own lock in that root. A slug lives in one tree:
a birth refuses a slug that stands in either, and a plan found in both is refused
(`plan-twice`) rather than one tree winning in silence. `pp-plan status` lists the shared plans after the instance's, marked `shared`;
the board of the plans space shows them the same way. The next move of a shared plan is
read from its document each time, because another run may have moved it since this run
last pushed its line; the line `NEXT_MOVE` carries at the end of an exchange is the one
read then. A shared plan that names no material reads each run's own tree. The package names no role: who frames and who delivers a shared
plan is said by a law of the plan or by the team's own text. The lock holds on one
filesystem; a root shared over a network is not covered.

## Installation

`plan` requires the `kit`, which the installer pulls automatically. `next` and
`steering` are optional: install `next` beside `plan` to have each plan's next move
reach the choices that end each answer; install `steering` to keep the work as steps.

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
the turn, and with `next` each open plan's next move reaches the choices at its end.

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
decision -- through NEXT when `next` is installed, through `pp-plan next-move` otherwise.
