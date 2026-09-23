---
name: PLAN_CHEATSHEET
kind: doc
description: >-
  The plan's doctrine on one page: what a plan is, its three levels of
  documents, what each node holds, the frequent steps with the mount and the
  operator's GO each one takes, the life cycle step by step, the table of
  nodes, statuses and the moment each status moves, and the plan's next move.
  Served to the agent at the turn by the TURN overlay's serve row, before it
  touches a plan. A reference, never played.
---

# The plan cheat sheet — what a plan is, what each node holds, when a status moves

A plan CONDUCTS one of the operator's undertakings. It is a tree of documents kept
under `plans/<slug>/`, THREE levels deep, always — the PLAN, its PHASES, their
BATCHES. The depth is fixed, the width varies: the BATCH is the only unit of work
(framed, implemented, proven, closed in one turn), the PHASE is the convergence
milestone of one component, never skipped — a small undertaking is ONE phase with
its batches, a large one several. The scripts, the statuses and the plan's next
move all read this one shape. The `pp-plan`
script alone writes the documents — the structure, the statuses and, through its
`section` verb, every section of the prose: the agent never opens a plan document in
an editor. Every node is a DOCUMENT that carries its own laws and the
readings its work needs (its `serve:` rows), so that MOUNTING the node arms the
agent with everything the level requires — the mount comes first, the work after.

## The three nodes, their sections, and the address

An ADDRESS is bare names — `memo/core/storage` — never the numbered folders on disk
(`plans/memo/1-core/1-storage/BATCH.md`, derived; every birth says its path from the
repo root). Every node is a document of titled SECTIONS, the kind's own list in its
order, each written by `pp-plan section <address> <Name>` (the prose on stdin): a
standing section is replaced, an absent one inserted at its rank, a LOG (Decisions,
Delivery) appended; a name beyond the list lands at the tail — the plan's own lists
(Keep track, Migrations…), replaced, or appended with `--append`. The order is GUIDED:
a section waits the required ones ranked before it (`section-order` names the missing
one).

| section | plan | phase | batch | what it holds | when | mode |
|---|---|---|---|---|---|---|
| Context | ✓ | ✓ | ✓ | what and why: the plan's thesis (the chat framing — the birth); a phase's or a batch's brief, copied at birth from its line in the parent's Items | birth | replaced |
| Survey | ✓ | – | – | the state of play of an existing artefact: titled sections, one whole component per bullet | birth | replaced |
| Ground | – | ✓ | ✓ | the zoom-out measured on-piece and dated: the sources, the code touched, the DEPENDENTS in a last paragraph | framing, re-measured at a reframing | replaced |
| Target | ✓ | ✓ | ✓ | what the node becomes — from scratch or a refactor — and what stays out | framing, amended at the GO | replaced |
| Protocol | ✓ | – | – | the method the plan imposes on its batches beyond the procs: how a batch proves and closes here | framing | replaced |
| Expected | ✓ | ✓ | ✓ | what is TRUE when the node closes, each line with the rendering that shows it | framing | replaced |
| Tests | – | – | ✓ | the bench scenarios to run or to write, the renderings to cite — on a DISPOSABLE path, never the operator's world —, the operator's gate | framing | replaced |
| Arbitrations | ✓ | ✓ | ✓ | the open questions: the options, the recommendation, what returns to the GO | framing | replaced |
| Items | ✓ | ✓ | ✓ | the CHILDREN prepared, one line each `- slug -- brief`: the phases, the batches, the todos — the entries `item.<n>` derive from it; a line is amended freely until its item is framed, a born item never leaves | the last of the framing | replaced — the entries follow |
| Decisions | ✓ | ✓ | ✓ | the dated outcomes: the operator's GO, its amendment, a reframing — one line each | at every word | appended |
| Delivery | – | – | ✓ | the log of the implementation and of every rework: what landed, the renderings, the rows re-aligned | delivery | appended |

An item lives in three moments. PREPARED: a line in its parent's Items — an entry
`todo`, no document — seen at `status`, at the next move (« awaits its framing »),
mountable (its kind's method rides ahead); the operator amends the line until « frame »
names the item; an item not even prepared mounts the same way under a born parent, so the combined GO « frame p2 with one batch, frame it, deliver it » mounts `X/p2/b` once. BORN: its first section (Ground) creates its folder and its document,
the brief as Context; then its own framing, down to its own Items. DELIVERED: its
statuses moved as the work lands. The plan alone is born by its Context, after the chat
framing. A section repeated at a lower level carries the matter OF that level, never a
restatement of the level above — that is what makes the mount productive: each level
arms the next without repeating it.

## The frequent steps — one GO, one mount, the calls

The operator's GO is « frame X », « GO X », a rework said — never « create », never « close »: an item is
prepared by its parent's framing and born by its own. The agent mounts ONCE per turn —
the node's address, a prepared item mounting its kind's method ahead — then writes by
the script under the method's segment (`-s pp-plan@<n>`).

| the operator's GO | the mount (once, first) | the calls, in order | statuses after |
|---|---|---|---|
| « frame the plan X » (after the chat framing) | `section X Context` births it, THEN `mount X` (2 documents: the PLAN method, the plan) | Survey on an existing artefact; Target, Expected, Arbitrations, Protocol when the plan imposes a method; Items — the phases PREPARED, one line each; THEN `constrain X` (only the laws every batch can violate) and `serve X` (references), posed LAST; the plan is `doing` since its Expected | X `doing`, phases `todo` prepared |
| « frame X/p1 » | `mount X/p1` (3 documents: the plan chain, the PHASE method ahead) | `section X/p1 Ground` births p1 from its line; Target, Expected, Arbitrations; Items — the batches PREPARED; THEN `constrain`, `serve` on X/p1; p1 is `doing` since its Expected | p1 `doing`, batches `todo` prepared |
| « frame X/p1/b1 » | `mount X/p1/b1` (5 documents: the chain to the phase, the BATCH method ahead) | `section X/p1/b1 Ground` births b1; Target, Expected, Tests, Arbitrations; Items — the todos; THEN `serve` (the touched code, then the dependent) and `constrain` (its own laws — the proof mode), posed LAST; b1 is `doing` since its Expected | b1 `doing`, todos `todo` |
| « GO b1 » (the implementation) | `mount X/p1/b1` (6 documents) | the upstream VERIFIED; what is about to be done said in a few lines; the work under every law on screen; `done X/p1/b1/<todo>` as each lands; a piece touched that no row named gets its `serve` row; the proof by RENDERING; the rows RE-ALIGNED on what really moved, then `section X/p1/b1 Delivery` (the log) — its todos all done, that write closes the batch, and the phase and the plan when it was their last; the script says each closing | b1 `done` |
| « rework b1 » | `mount X/p1/b1` | `section X/p1/b1 Items` with the new todos — a framing section written on a `done` node reopens it (`redo`, the ancestry rises); delivered like a batch, by its Delivery | `redo` → `done` |
| « change the line of b2 », « add b4 », « drop b3 » | `mount X/p1` | `section X/p1 Items` rewritten — the entries follow; a born item never leaves, a todo one does | as written |
| « rename p1 », « rename b1 » | `mount X/p1` | `rename X/p1 <new>` — the entry at its rank, the Items line, the derived folder, `slug:` and the batches' `phase:` follow in one call; the prose that says the old name is yours; a plan keeps its name, a todo renames by Items | as before |
| « amend the law K1 », « retire K1 » | the node's chain | `constrain X/p1/b1 --section production` with `K1  the new text` piped replaces it in place (a bare line derives the next code); `constrain X/p1/b1 --retire K1` takes it out and keeps the code under `retired:` — a code never returns | as before |

The serve rows of a batch LIVE with it: born at the framing (touched, then dependent —
each whole, else between tags `DOC[a..b]`, line ranges last), kept as pieces
enter or leave during the implementation, re-aligned at the landing — never a later pass. The laws come LAST, at every level: a constraint is derived from the detailed framing —
the ground read, the pieces seen, the expected and the tests written — never posed before
it; a law written first is a guess the framing will contradict. A mount shows the node at work whole and its ancestors from their Target on; `mount X --whole` shows every ancestor whole. One chain per turn: a
second mount in the same turn refuses (`mount-collision`); a new turn carries a new chain. After a mount every segment offers `pp-plan`: a bare
`-s pp-plan` refuses `address-ambiguous` — address the segment, `-s pp-plan@<n>`.

## The life cycle, five steps — one form

1. **The chat framing, then « frame the plan X »** — the undertaking takes shape in the
   exchange; on that GO, `pp-plan section X Context` births the plan (the context and
   the brief), then `mount X` (2). Survey on an existing artefact; Target, Expected
   (the plan is `doing` the moment it is written — deduced), Arbitrations, Protocol when
   the plan imposes a method on its batches; Items — the phases PREPARED by component,
   one line each; THEN its laws and readings, posed last. Nothing is born below: the
   operator amends a prepared line until « frame » names the phase.
2. **« frame X/p1 »** — `mount X/p1` (3, the PHASE method ahead); `section X/p1 Ground`
   births the phase from its line (the brief as Context); Target; Expected (`doing`);
   Arbitrations; Items — the batches PREPARED; THEN its laws and readings.
3. **« frame X/p1/b1 »** — `mount X/p1/b1` (5, the BATCH method ahead); `section X/p1/b1
   Ground` births the batch; Target (from scratch or refactor, what stays out); Expected
   (`doing`); Tests; Arbitrations; Items — the todos, one line each; THEN its readings
   (`serve`) and its own laws (`constrain`), derived from all of the above. The
   implementation waits the GO that names the batch.
4. **« GO b1 »** — `mount X/p1/b1` (6); the upstream verified first, what is about to be
   done said in a few lines, then the work under every law on screen, each todo checked
   off AS IT LANDS (`done X/p1/b1/<todo>`), the serve rows kept as pieces enter or leave,
   the proof by RENDERING (bench, diff, grep) on a DISPOSABLE path — a mktemp directory,
   a copy, never the operator's world —, the rows re-aligned on what really moved,
   then the log by `section X/p1/b1 Delivery` — its todos all done, that write closes
   the batch, the phase when it was the last batch, the plan with the phase; the script
   says each closing. No word closes a node. What cannot close honestly is SAID: the
   batch stops, it never stretches.
5. **A rework** — a framing section rewritten on a `done` node reopens it: a new todo in
   its Items, its Target amended — `done` → `redo`, the ancestry rising with it — never a
   twin node; it delivers like a batch, by its Delivery. A stop is said by `block X/p1/b1
   <reason>` (the reason a dated Decisions line), lifted by the next framing section.

## Nodes, statuses, when they move — with the mount and the GO

| node | status | when | the mount | the operator's GO | description |
|---|---|---|---|---|---|
| plan | `todo` | born by its Context, after the chat framing | none before birth, then `mount X` (2) | « frame the plan X » | the context written; not framed yet |
| plan | `doing` | its Expected is written — deduced | `mount X` (2) | the same GO — the framing rides it | the phases prepared in Items, then the laws posed last; then the phases framed and worked |
| plan | `done` | its last phase closes — the script's cascade, same call | `mount X` | none owed — the script closes it | the undertaking is delivered |
| plan | `blocked` | `block X <reason>` — the reason a dated Decisions line | any | « block the plan », or the agent ALERTS | lifted by the next framing section |
| plan | back to `doing` | a framing section rewritten below — a rework | the reworked node's chain | a rework said | the rework rises to the plan's line |
| phase | `todo` | PREPARED by a line of the plan's Items — an entry, no document | `mount X/p` (3, the method ahead) | none — the plan's framing prepares it; its line is amendable until « frame phase p » | not born yet |
| phase | `doing` | born by its Ground, `doing` at its Expected — deduced | `mount X/p` (3 before its birth, 4 after) | « frame phase p » | the batches prepared in Items, then the laws posed last; then the batches framed and worked |
| phase | `done` | its last batch closes — the script's cascade, same call | `mount X/p` (4) | none owed — the script closes it | the component converges clean |
| phase | `blocked` | an upstream the phase depends on is missing | `mount X/p` | the agent ALERTS; « block phase p » | said, waits the lift |
| phase | `redo` | a framing section rewritten on the `done` phase, or a batch below reworked | `mount X/p` | a rework said | the rework is open; closes `done` again by its batches, or by `repair` when none is left |
| batch | `todo` | PREPARED by a line of the phase's Items — an entry, no document | `mount X/p/b` (5, the method ahead) | none — the phase's framing prepares it; its line is amendable until « frame batch b » | not born yet |
| batch | `doing` | born by its Ground, `doing` at its Expected — deduced; stays so through the implementation | `mount X/p/b` (5 before its birth, 6 after) | « frame batch b » ; then « GO b » | Ground, Target, Expected, Tests, Arbitrations, Items — then readings and laws LAST; then the GO; then the work |
| batch | `done` | its Delivery is written — its todos all done, the expected met, the tests rendered, the rows re-aligned | `mount X/p/b` (6) | « GO b » | the phase closes with it when it was the last batch, the plan with the phase |
| batch | `blocked` | an upstream dependency is missing (verified, never presumed) | `mount X/p/b` | the agent ALERTS; « block batch b » | alerted; the batch stops there |
| batch | `redo` | a framing section rewritten on the `done` batch — a new todo in Items | `mount X/p/b` | a rework said | delivers like a batch, by its Delivery |
| todo | `todo` · `done` | prepared in the batch's Items; checked off by `done` as the work lands, never in an end sweep | the batch's chain | the batch's GO | the name says the work |

No verb moves a status but `done` (a todo) and `block`: `doing` comes with Expected,
`done` with Delivery and the cascade, `redo` with a framing section rewritten on a
`done` node — the operator has no word to close, one to rework. `status` derives the
progress table from the front matters, the prepared items shown; `check` reddens
wherever a `done` node still carries an engaged child, or a hand edit broke a line;
`repair` mends what is mechanical — the numbering, a line against its document, a
derived folder (`<n>-<name>`) without its entry — and says the rest with its gesture, on
the operator's GO; any other directory is the plan's own material and never reddens.

## The plan's NEXT MOVE

After every mutating call the script computes the plan's NEXT MOVE — the deepest
node that awaits something and the GO it awaits (« the phase p1 awaits its
framing », « the batch p1/b1 awaits its implementation — on the GO that names
it ») — and pushes it to the bus as ONE held line per plan, replaced by the next
call, cleared when the plan is `done`. At the turn's end that line arrives under
`INFORMATION — plan-next-move` (the package's `NEXT_MOVE` document, mounted at `turn.end`
before the steering surface) and is CARRIED into the steering surface at
the thread that holds the plan's work — the line ends with the node's vector
(`(plan-lot:X/p1/b1)`), the KEY of the thread's step: `attach --key` the first time,
`done` or `renext` the step that carries it after. It DESCRIBES what the plan asks
for next; the GO it names is the operator's — the line is never played in the
turn. `pp-plan next-move` reads the held lines back.

The plans' nodes are also VECTORS a reflex may project a frustration on: `plan:<slug>`,
`plan-phase:<slug>/<phase>`, `plan-lot:<slug>/<phase>/<batch>` -- the address every verb takes, the
family saying the grain; `pp-plan verify` answers the engine (born or prepared node).
