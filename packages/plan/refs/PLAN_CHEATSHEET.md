---
name: PLAN_CHEATSHEET
kind: doc
description: >-
  The plan's doctrine on one page: what a plan is, the levels of its
  documents, what each node holds, the frequent steps with the mount and the
  principal's GO each one takes, the life cycle step by step, the table of
  nodes, statuses and the moment each status moves, and the plan's next move.
  Served to the agent at the turn by the TURN overlay's serve row, before it
  touches a plan. A reference, never played.
---

# The plan cheat sheet — what a plan is, what each node holds, when a status moves

A plan CARRIES one undertaking of the principal. It is a tree of documents under
`plans/<slug>/`, as deep as the chain of its templates. The product's chain has three
levels: the PLAN, its PHASES, their BATCHES. The BATCH is the only unit of work (framed,
implemented, proven and closed in one turn); the PHASE is where one part of the plan comes
together. Lay a plan out one of two ways: one phase per component, each with its batches; or,
for fixes or a short rework, ONE phase with one batch per component. The `pp-plan` script
alone writes the documents — the structure, the statuses and, through its `section` verb,
every section of the prose: never open a plan document in an editor. Each node carries its
own laws and the readings its work needs (its `serve:` rows), so MOUNTING the node gives you
everything the level asks: mount first, work after.

## The nodes, their sections, and the address

Each template says `next: <template>` (its items are nodes on that template) or `leaf: yes`
(its items are todos). A plan born by `section <slug> <first section> --template <name>`
follows that template's chain, and a node's file is named after its template
(`<TEMPLATE>.md`). A line of a template's `sections` may end on `unserved`: that section is
not served when its node is mounted. `pp-plan templates [--json]` lists the templates the
tree sees, its own first; they come as the reading `plan-templates` whenever the PLAN
proc opens, and last at every mount: choose the template of a birth there.

An ADDRESS is bare names — `memo/core/storage` — never the numbered folders on disk
(`plans/memo/1-core/1-storage/BATCH.md`, derived; every birth says its path from the repo
root). A node is a document of titled SECTIONS, the ones its TEMPLATE declares in its front
matter (`template: plan`, `phase` or `batch` — the tree's own under `plans/_templates/`,
else the product's). Write each one with `pp-plan section <address> <Name>`, the prose on
stdin: a standing section is replaced, an absent one inserted at its rank, Delivery
appended, any section appended with `--append`. A name the template does not carry is
refused (`section-unknown`). The product's templates:

| section | plan | phase | batch | what it holds | when | mode |
|---|---|---|---|---|---|---|
| Context | ✓ | – | – | what the undertaking is and why, in the principal's terms | the birth of the plan | replaced |
| Ground | ✓ | ✓ | ✓ | what stands before the work, read on the pieces and dated: the sources, the code touched, and in a last paragraph what DEPENDS on it; a phase and a batch are born by it | framing, read again at a reframing | replaced |
| Expected | ✓ | ✓ | ✓ | first what is TRUE when the node closes, each line with what shows it; then what stays outside | framing | replaced |
| Tests | – | – | ✓ | what proves the Expected: the tests to run or to write first, the output to cite, on a THROWAWAY path; the principal's gate when only a live run proves it | framing | replaced |
| Choices | ✓ | ✓ | ✓ | each choice the node makes: the choice, its reason, its strongest objection; writing it makes the node `doing` | framing | replaced |
| Items | ✓ | ✓ | ✓ | the CHILDREN, one line each `- slug -- brief`: the phases, the batches, the todos — the entries `item.<n>` come from it; a line is amended freely until its item is framed, a born item never leaves | the end of the framing | replaced — the entries follow |
| Delivery | ✓ | ✓ | ✓ | on a batch, one todo delivered per call (`--item`), what landed and its proof; on a plan or a phase, the journal | the work | appended |

An item lives in three moments. PREPARED: a line in its parent's Items — an entry `todo`, no
document — seen at `status` and at the next move (« awaits its framing »), mountable (its
template comes ahead); the principal amends the line until « frame » names the item. An item
not even prepared mounts the same way under a born parent, so the combined GO « frame p2 with
one batch, frame it, deliver it » mounts `X/p2/b` once. BORN: the first section written (Ground)
creates its folder and its document on its level's template, with its title and that section
alone — its Items line is not copied; then comes its own framing, down to its own Items.
DELIVERED: its statuses move as the work lands. The plan is born by its Context, after the
framing in the exchange. A section repeated at a lower level holds the matter OF that level,
never a restatement of the level above: each level prepares the next without repeating it.

A plan written in the old form may hold sections the templates no longer carry (Target,
Arbitrations, Survey, Protocol, Decisions, a Context on a node under the plan): they are read, served
and kept, never written again. Take such a node up in the current form: its Choices before
its Items.

## The frequent steps — one GO, one mount, the calls

The principal's GO is « frame X », « GO X », a rework said — never « create », never
« close »: an item is prepared by its parent's framing and born by its own. Mount the node
FIRST — its address; a prepared item mounts its template ahead — then write with the script
(`-s pp-plan`). A deeper node mounted later in the same turn extends the chain (the documents
already there are skipped) and REPLACES the sibling nodes.

| the principal's GO | the mount (first) | the calls, in order | statuses after |
|---|---|---|---|
| « frame the plan X » (after the framing in the exchange) | `section X Context` gives its birth, THEN `mount X` (PLAN, the template `plan`, the plan) | Ground; Expected; Choices (the plan is `doing`); Items — the phases PREPARED, one line each; THEN `constrain X` (only the laws every batch can break) and `serve X` (references), LAST | X `doing`, phases `todo` prepared |
| « frame X/p1 » | `mount X/p1` (the plan's chain, the template `phase` ahead) | `section X/p1 Ground` gives p1 its birth; Expected; Choices (`doing`); Items — the batches PREPARED; THEN `constrain`, `serve` on X/p1 | p1 `doing`, batches `todo` prepared |
| « frame X/p1/b1 » | `mount X/p1/b1` (the chain to the phase, the template `batch` ahead) | `section X/p1/b1 Ground` gives b1 its birth; Expected; Tests; Choices (`doing`); Items — the todos; THEN `serve` (the touched code, then the dependent code) and `constrain` (its own laws, what its proof judges), LAST | b1 `doing`, todos `todo` |
| « GO b1 » (the implementation) | `mount X/p1/b1` (PLAN, the three templates, the three nodes) | the upstream VERIFIED; what you will do said in a few lines; the work under every law on screen; `section X/p1/b1 Delivery --item <todo>` as each todo lands, with its proof; a piece touched that no row names gets its `serve` row; the tests the change touches, once; the proof by output; the rows RE-ALIGNED on what really moved; the last todo delivered closes the batch, and the phase and the plan when it was their last — the script says each closing | b1 `done` |
| « rework b1 » | `mount X/p1/b1` | `section X/p1/b1 Items` with the new todos — a `redo` section written on a `done` node reopens it (`redo`, its ancestors with it); delivered like a batch, todo by todo | `redo` → `done` |
| « change the line of b2 », « add b4 », « drop b3 » | `mount X/p1` | `section X/p1 Items` rewritten — the entries follow; a born item never leaves, a todo may | as written |
| « rename p1 », « rename b1 » | `mount X/p1` | `rename X/p1 <new>` — the entry at its rank, the Items line, the derived folder and `slug:` follow in one call; the prose that says the old name is yours to change; a plan keeps its name, a todo is renamed by Items | as before |
| « amend the law K1 », « retire K1 » | the node's chain | `constrain X/p1/b1 --section production` with `K1  the new text` piped replaces it in place (a bare line derives the next code); `constrain X/p1/b1 --retire K1` takes it out and keeps nothing — both on the principal's word alone | as before |

The serve rows of a batch LIVE with it: written at the framing (the touched code, then the
dependent code — each whole, else between tags `DOC[a..b]`, line ranges last), kept true as
pieces enter or leave, re-aligned at the landing — never in a later pass. The laws come LAST,
at every level, from the detailed framing: a law written first is a guess the framing will
contradict. A law says what must hold while the work is done, and how that is seen; it never
says what the work is — Expected says that. A law carries no figure: a figure goes to
Expected. A mount shows the node you work on whole, and of each node above it the sections
its template names in `shown:` (Expected and Choices on the product's plan and phase);
`mount X --whole` shows every ancestor whole. A mount makes no segment of its own: the
methods and the nodes are read, in the order of the chain, at the head of the step that
stands, and `-s pp-plan` plays without an address where one segment offers it.

A plan whose code lives in another tree (a worktree, a branch) declares its MATERIAL once,
`material X <name> <path>` — the tree written in the plan's own `materials:` block, the path
relative to the plan's folder or absolute, no SETTINGS read; `material X <name>` then chooses
a declared tree, `material X - <name>` withdraws one. Every node born under the plan carries
`material: <name>`, and a mount serves its rows from that tree and from no other
(`engine/x.py @<name>`): a row whose tree lacks the file is not served (`(not served: …)` in
the block), and a row of another tree takes the mark of a tree the plan declares; no tree is
called `repo` or `work` (refused). A plan born by `section X Context --shared` lives under the
run's ROOT OF DOCUMENTS (`<root>/plans/`, a team's directory at every wake-up): every run
opened under that root reads and writes it with the same verbs, `status` says `shared`, and a
plan that names no material reads each run's own tree.

## The life cycle, five steps

1. **The framing in the exchange, then « frame the plan X »** — the undertaking takes shape in
   the exchange; on that GO, `pp-plan section X Context` gives the plan its birth, then
   `mount X`. Ground; Expected; Choices (the plan is `doing` once they are written); Items —
   the phases PREPARED (one per component, or one phase alone), one line each; THEN its laws
   and readings. Nothing is born below: the principal amends a prepared line until « frame »
   names the phase.
2. **« frame X/p1 »** — `mount X/p1` (the template `phase` ahead); `section X/p1 Ground` gives
   the phase its birth; Expected; Choices (`doing`); Items — the batches PREPARED; THEN its
   laws and readings.
3. **« frame X/p1/b1 »** — `mount X/p1/b1` (the template `batch` ahead); `section X/p1/b1
   Ground` gives the batch its birth; Expected (what it becomes, what stays outside); Tests
   (the new test written first); Choices (`doing`); Items — the todos, one line each; THEN its
   readings (`serve`) and its own laws (`constrain`), from all of the above. The
   implementation waits the GO that names the batch.
4. **« GO b1 »** — `mount X/p1/b1`; the upstream verified first, what you will do said in a few
   lines, then the work under every law on screen, each todo DELIVERED AS IT LANDS
   (`section X/p1/b1 Delivery --item <todo>`), the serve rows kept true, the proof by output
   (bench, diff, grep) on a THROWAWAY path — a mktemp directory, a copy, never the principal's
   world —, the rows re-aligned on what really moved; the last todo delivered closes the
   batch, the phase when it was the last batch, the plan with the phase, and the script says
   each closing. The node that carries a whole component — the phase, by its last batch, or
   the batch itself when the plan is one phase with one batch per component — runs once the
   suite of that component and of the components that depend on it; the plan's last batch
   runs the project's whole suite once: none closes before its suite is green. No word closes
   a node. What cannot close honestly is SAID: the batch stops, it never stretches.
5. **A rework** — a `redo` section of its template rewritten on a `done` node reopens it: a
   new todo in its Items, its Expected amended — `done` → `redo`, its ancestors with it —
   never a twin node; it is delivered like a batch, todo by todo. A stop is said by `block
   X/p1/b1 <reason>` (the reason a dated line of Delivery), lifted by the next section written.

## Nodes, statuses, when they move — with the mount and the GO

| node | status | when | the mount | the principal's GO | description |
|---|---|---|---|---|---|
| plan | `todo` | born by its Context, after the framing in the exchange | none before the birth, then `mount X` | « frame the plan X » | the context written; not framed yet |
| plan | `doing` | its Choices are written | `mount X` | the same GO — the framing comes with it | the phases prepared in Items, then the laws LAST; then the phases framed and worked |
| plan | `done` | its last phase closes — the script's cascade, in the same call | `mount X` | none owed — the script closes it | the undertaking is delivered |
| plan | `blocked` | `block X <reason>` — the reason a dated line of Delivery | any | « block the plan », or the agent WARNS | lifted by the next section written |
| plan | `redo` | a `redo` section rewritten below it — a rework | the reworked node's chain | a rework said | the rework rises to the plan's line |
| phase | `todo` | PREPARED by a line of the plan's Items — an entry, no document | `mount X/p` (its template ahead) | none — the plan's framing prepares it; its line can be amended until « frame phase p » | not born yet |
| phase | `doing` | born by its Ground, `doing` once its Choices are written | `mount X/p` | « frame phase p » | the batches prepared in Items, then the laws LAST; then the batches framed and worked |
| phase | `done` | its last batch closes — the script's cascade, in the same call | `mount X/p` | none owed — the script closes it | its part of the plan comes together clean |
| phase | `blocked` | an upstream the phase depends on is missing | `mount X/p` | the agent WARNS; « block phase p » | said, waits the lift |
| phase | `redo` | a `redo` section rewritten on the `done` phase, or a batch below reworked | `mount X/p` | a rework said | the rework is open; closes `done` again by its batches, or by `repair` when none is left |
| batch | `todo` | PREPARED by a line of the phase's Items — an entry, no document | `mount X/p/b` (its template ahead) | none — the phase's framing prepares it; its line can be amended until « frame batch b » | not born yet |
| batch | `doing` | born by its Ground, `doing` once its Choices are written; stays so through the implementation | `mount X/p/b` | « frame batch b »; then « GO b » | Ground, Expected, Tests, Choices, Items — then readings and laws LAST; then the GO; then the work |
| batch | `done` | its last todo is delivered (`Delivery --item`) — the Expected met, the tests run, the rows re-aligned | `mount X/p/b` | « GO b » | the phase closes with it when it was the last batch, the plan with the phase |
| batch | `blocked` | an upstream it depends on is missing (verified, never presumed) | `mount X/p/b` | the agent WARNS; « block batch b » | the batch stops there |
| batch | `redo` | a `redo` section rewritten on the `done` batch — a new todo in Items | `mount X/p/b` | a rework said | delivered like a batch, todo by todo |
| todo | `todo` · `done` | prepared in the batch's Items; delivered by `Delivery --item` as the work lands, never in a final sweep | the batch's chain | the batch's GO | its name says the work |

No verb moves a status but `done` (closing by hand) and `block`: `doing` comes with a `doing`
section (Choices), `done` when all the items of a node are done — a batch's by
`Delivery --item` — and the cascade, `redo` with a `redo` section rewritten on a `done` node.
`status` reads the progress from the front matters, one line per node, the prepared items
apart; `check` reddens wherever a `done` node still carries a child under way, or a hand edit
broke a line; `repair` mends what is mechanical — the numbering, a line against its document,
a derived folder (`<n>-<name>`) without its entry — and says the rest with its gesture, on the
principal's GO; any other directory is the plan's own material and never reddens.

## The plan's NEXT MOVE

After every call that writes, the script computes the plan's NEXT MOVE — the deepest node that
waits for something and the GO it waits for (« the phase p1 awaits its framing », « the batch
p1/b1 awaits its implementation — on the GO that names it ») — and pushes it as ONE held line
per plan, replaced by the next call, cleared when the plan is `done`. The line ends with the
node's vector (`(plan:X/p1/b1)`). It DESCRIBES what the plan asks for next; the GO it names is
the principal's — never play the line in the turn. `pp-plan next-move` reads the held lines
back, at any time.

The packages next and steering are OPTIONAL to plan. When next is there, the package's
`NEXT_MOVE` document is mounted on NEXT's socket `next.begin`: the line comes under
`INFORMATION — plan-next-move` in NEXT's block at the end of the answer, computed after the
work, and a choice of NEXT may carry it to the principal. When steering is there, the vector
is the KEY of the step that tracks the plan's work. Without next, `NEXT_MOVE` sleeps (the build
says `mount-dormant` once) and the line is read with `pp-plan next-move` when needed.

The plans' nodes are also VECTORS: `plan:<address>`, the address every verb takes, at every
depth — `plan:X`, `plan:X/p1`, `plan:X/p1/b1`. A run that the agents' launcher starts with its
option `--vector` on one of them (`./pp agent run` or `./pp agent start`) mounts that node at
every exchange; `pp-plan verify` checks the address first (a node born or prepared).
