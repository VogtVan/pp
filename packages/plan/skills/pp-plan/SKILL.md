---
name: pp-plan
description: >-
  Keep this instance's plans -- plans/<slug>/ as documents whose structure, statuses
  and prose THIS script alone writes: sections, todos, laws, readings, moves; the
  statuses deduced from the writing; the chain mounted, the next move said. Use
  whenever a plan is created or advances; never open a plan document in an editor.
---

# `pp-plan` — the plans keeper

## Entities

One writer, one structure, three levels — always:

| Entity | Storage | Identity |
|---|---|---|
| Plan | `plans/<slug>/PLAN.md` | its slug, born by its Context |
| Phase | one directory and `PHASE.md` per phase | its name, prepared as a line of the plan's Items |
| Batch | one directory and `BATCH.md` per batch | its name, prepared as a line of the phase's Items |
| Todo | a line of the batch's Items, an `item.<n>` entry | its slug, checked off by `done` |

An ADDRESS is bare names — `memo/core/storage` — never the numbered folders.
The NAME is the identity, used by entries and addresses; the disk FOLDER is
indexed, `<n>-<name>`, DERIVED from the position the `item.<n>` keys own. The
script alone renames folders when the order changes, and every birth says its
path from the repo root.

Front matters carry one `item.<n>: <name>  <status>` per child. The statuses:
`todo · doing · done · blocked`, plus `redo` reached only by a guarded reopen.
A plan whose code lives in another tree — a worktree, a branch — carries
`material: <name>` on every node, written by `material` (below).

### The sections

The BODY is titled SECTIONS in the kind's order:

| Kind | Sections, in order |
|---|---|
| plan | Context, Survey, Target, Protocol, Expected, Arbitrations, Items, Decisions |
| phase | Context, Ground, Target, Expected, Arbitrations, Items, Decisions |
| batch | Context, Ground, Target, Expected, Tests, Arbitrations, Items, Decisions, Delivery |

Each is written by `section`: a standing section is REPLACED, an absent one
INSERTED at its rank, a log (Decisions, Delivery) or the `--append` flag
APPENDS, a name beyond the list lands at the tail. The order is GUIDED: a
required section waits the required ones before it (`section-order`). A
subtitle inside a section is written `###`: a prose carrying a `## ` line, a
code block included, refuses `prose-heading` before anything is written.

### The life of an item

- **PREPARED** — a line `- <slug> -- <brief>` in its parent's Items: the entry
  derived, no document; amend the line freely until the item is framed.
- **BORN** — its first section (Ground) creates its folder and its document
  from the line, the brief as Context. The plan alone is born by its Context.
- **DELIVERED** — its statuses moved as the work lands.

### The statuses, deduced from the writing

- Expected makes a node `doing`.
- Delivery makes a batch `done` — its todos all done, `items-open` otherwise —
  and the closing rises to the phase and the plan, each closing said.
- A framing section rewritten on a `done` node reopens it: `redo`, the
  ancestry rising with it (closed phase → `redo`, closed plan → `doing`), so
  the rework stays visible to the plan's next move.
- `block` says a stop, lifted by the next framing section.
- `done` checks a todo off.

No other verb moves a status, and no word closes a node. Every move is
surgical: the one `status:` line and its parent entry.

## Commands

Prefix each form with `./pp <key> -s pp-plan` (after a mount every segment
offers `pp-plan`: address the method's segment, `-s pp-plan@<n>`):

    ./pp <key> -s pp-plan section memo/core/storage Ground -

| Form | Effect |
|---|---|
| `section <address> <Name> [--append]` | Write one section, the prose on stdin (`-` marks it). |
| `section <address> <Name> --remove[=<n>]` | Remove one section, heading and text, no stdin; a name standing several times needs its rank (`section-ambiguous`); a section of the kind's list standing once refuses `section-kept`; no status moves. |
| `done <slug>/<phase>/<batch>/<todo>` | Check a todo off. |
| `block <address> <reason ...>` | Say a stop; the reason a dated Decisions line. |
| `move <src-address> <dst-parent-address> <index>` | Transfer a phase to another plan, a batch to another phase, or reorder within its parent. |
| `rename <address> <new-name>` | Give a phase or a batch a new name. |
| `mount <address> [--whole]` | Host the node's document chain in the view (read-only, any time). |
| `constrain <address> [<prefix>] --section production\|behavior` | Pose laws, on stdin; a line opening on a posed code replaces it in place. |
| `constrain <address> --retire <code>` | Take a law out: the line leaves, nothing is kept — on the principal's word alone (PN15). |
| `serve <address> <token ...>` | Append ONE row to the last section of the node's `serve:` rows. |
| `serve <address> -` | Replace the whole block with the rows piped, a blank line separating two sections; an empty block refuses `value-malformed`. |
| `material <slug> [<name>\|-]` | Write the plan's material — `material: <name>` on the plan and on every phase and batch born under it, the slug by default; `-` takes the key out everywhere; a name SETTINGS does not declare refuses `material-undeclared`. |
| `next-move` | Print the next-move lines the bus holds, one per open plan; pushes nothing. |
| `status [<slug>]` | The progress table, DERIVED from the front matters alone, the prepared items shown. |
| `check` | Lint every plan (below). |
| `repair` | Mend what is mechanical (below); played on the operator's GO. |
| `verify` | The engine's call, never the agent's: a vector on stdin. |

### Moving and renaming

`move` writes the entry at `<index>`, both parents renumber, folders follow
their derived names, the moved document's model keys name its new home and
its Items line follows it; a prepared item moves by its parent's Items alone.
The call SAYS what remains yours: the subtree's prose, including references
to the old home.

`rename` moves the parent's entry at its rank, the Items line, the derived
folder, `slug:` and the batches' `phase:` in one call, every refusal before
the first write. A plan keeps the name it was born under; a todo renames by
its parent's Items. The prose that says the old name stays yours, and the
call says so.

The TITLE line of every document `move` and `rename` touch — the node and the
batches it carries — follows in the same call: it becomes the title its kind's
template gives its front matter, the rest of the body byte for byte. A free
title, one not opening on `# PLAN`, `# PHASE` or `# BATCH`, is left.

### Laws and readings

A law amends BY ITS CODE: a `constrain` line opening on a code posed here
replaces that law in place, a bare line derives a new code. `--retire` makes a
law disappear and keeps nothing, so its number may be derived again. Both wait the
principal's word: the plan method's PN15 makes the agent stop and ask before either.

A `serve` token is written in one of three forms, preferred in this order:

1. the whole document — `DOC`;
2. the lines between two tags — `DOC[start..end]`, either side may stay
   empty; a tag may hold blanks, so quote the token on the command line (a
   piped row needs no quotes);
3. line ranges — `DOC[x-y,...]`, as a last resort: the answer names every
   line range it wrote, because the numbers stop pointing at the same lines
   when the file changes.

A piped row with a bracket left open refuses `serve-range-malformed`; a token
the engine's writer refuses (`token-invalid`, `serve-range-malformed`) refuses
here by the same name.

### The material

A MATERIAL is a tree a reading reads from: the repository (`repo`, tacit) or a
tree the operator declares at SETTINGS, `material.<name>: <path>`. A plan whose
code lives in such a tree says it once: `material <slug> [<name>]` writes
`material: <name>` on the plan and on every phase and batch already born, the
slug by default (one plan, one branch, its slug); every node born later copies
the plan's key at its birth. A mount then serves the node's rows from that
tree, each titled `<token> @<name>`. The verb reads the catalogue through the
engine's settings face, never the document itself; a name not declared refuses
`material-undeclared` and names the line to write; `repo` needs no declaration;
`-` takes the key out of every node. A document of the repository itself — a
README, a design — keeps reading from it when its row is marked `@repo`: on a
node with a material, `serve` answers one reminder line for a row left
unmarked, and writes the row as asked.

### The mount

`mount` derives the document chain to host from an address and emits a
`::mount <json>` directive pp collects: one pp call mounts the whole chain,
nothing is written, no status moves. The chain GROWS by level:

| Address | Documents mounted |
|---|---|
| a plan | 2 — the package's PLAN method nested with its body, the plan stacked |
| a phase | 4 (3 before its birth: the PHASE method ahead) |
| a batch | 6 (5 before its birth: the BATCH method ahead) |

A PREPARED item, or one not even prepared yet under a born parent, mounts its
kind's method ahead, so the framing that births it plays under its laws, and
a combined GO that frames a parent then a child mounts once.

The LAST document of the chain — the node named, or its parent when the node
is still to come — mounts its whole body. Each ancestor mounts the sections
that arm the level below, from its Target on: a plan shows Target and
Expected, a phase Target, Expected and Arbitrations, each part served under
`<title>[<start>..<end>]`; a section the ancestor lacks says nothing; its
laws, offers and `serve:` rows come as before. `--whole` mounts every
ancestor's whole body instead — for a framing that needs an ancestor's Ground
or Items.

### Check and repair

`check` reddens: a done node still carrying an engaged child, a line against
its document, a broken numbering, a DERIVED folder without its entry, a
section name twice in one document, a level title that differs from its front
matter, a missing title, a `material:` SETTINGS no longer declares (one line
per plan, `material-undeclared`). Any other directory is the plan's own material and
says nothing; a prepared todo without a document is no finding. `check`
confronts every line with its document, so hand edits cannot hide.

`repair` mends what is MECHANICAL — the numbering, a line against its document
(the document wins), a derived folder without its entry, a plan or a phase
open over children all done (closed: the cascade that never ran), a level
title set from its front matter or a missing one inserted — and says every
mend; every other finding is said with its gesture and left.

### Vectors and `verify`

The plans' nodes are VECTORS a reflex may project a frustration on — three
families this package declares at its manifest, each `verify: pp-plan`:

| Family | Address |
|---|---|
| `plan:<slug>` | a plan |
| `plan-phase:<slug>/<phase>` | one of its phases |
| `plan-lot:<slug>/<phase>/<batch>` | one of its batches |

`verify` is the engine's call at every entry and service of the bus: the
address must RESOLVE in the tree — a plan born; a phase or a batch born or
PREPARED as an Items entry — `path-unknown` otherwise, `address-depth` when
the depth does not fit the family, `family-foreign` for a family this package
does not declare.

## Refusals

Refusals exit 2 and write nothing; a malformed call says the verb's usage in
one sentence. Writes are atomic.

| Code | When |
|---|---|
| `path-unknown` | no such node: an absent entry says Items, a numbered segment says the bare address, a prepared item says its first section |
| `section-unknown` · `section-order` · `section-ambiguous` · `section-kept` | a section the kind does not know, written out of order, standing several times, or the kind's own removed |
| `item-line-malformed` · `item-engaged` · `items-open` | an Items line without `- <slug> -- <brief>`, a born item rewritten out, a Delivery over open todos |
| `done-invalid` · `status-invalid` · `reopen-invalid` | a status the writing does not allow |
| `slug-taken` · `name-invalid` · `kind-mismatch` | a name already used, malformed, or of another kind |
| `code-unknown` | a `--retire` on a code never posed |
| `prose-missing` · `prose-heading` | no prose on stdin, or a `## ` line inside a section |
| `index-invalid` · `target-unknown` | a `move` to a rank or a parent that does not exist |
| `value-malformed` · `token-invalid` · `serve-range-malformed` | an empty serve block, a token the engine refuses, a bracket left open |
| `material-undeclared` | a material name SETTINGS does not declare, or `work`, the launcher's — `repo` alone needs no declaration |
| `frontmatter-malformed` | a document the script cannot read |
| `argument-missing` · `argument-unexpected` · `verb-unknown` | a malformed call |
| `method-missing` · `not-an-instance` | the package's method document absent, or no instance to write in |
