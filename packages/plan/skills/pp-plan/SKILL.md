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

One writer, one structure, as deep as the chain of templates goes:

| Entity | Storage | Identity |
|---|---|---|
| Plan | `plans/<slug>/<TEMPLATE>.md` — `PLAN.md` on the product's `plan` | its slug, born by the first section of its template |
| Node | one directory and `<TEMPLATE>.md` per node, under its parent — `PHASE.md`, `BATCH.md` in the product's chain | its name, prepared as a line of its parent's Items |
| Todo | a line of a leaf's Items, an `item.<n>` entry | its slug, checked off by `done` |

An ADDRESS is bare names — `memo/core/storage` — never the numbered folders.
The NAME is the identity, used by entries and addresses; the disk FOLDER is
indexed, `<n>-<name>`, DERIVED from the position the `item.<n>` keys own. The
script alone renames folders when the order changes, and every birth says its
path from the repo root.

Front matters carry one `item.<n>: <name>  <status>` per child. The statuses:
`todo · doing · done · blocked`, plus `redo` reached only by a guarded reopen.
A plan whose code lives in another tree — a worktree, a branch — carries
`material: <name>` on every node, written by `material` (below).

### The templates

Every node names its TEMPLATE in its front matter: `template: plan`, `phase` or
`batch` in the product's chain. A template is a document under
`plans/_templates/<name>.md` in the tree of the plan, or else the product's own.
Its front matter alone says the structure of its level:

```yaml
name: batch
description: a batch of a phase -- framed, implemented on its GO, delivered
leaf: yes
sections: |
  Ground
  Expected
  Tests
  Choices
  Items
  Delivery
statuses: |
  doing  Choices
  redo  Ground Expected Tests Choices Items
```

- `leaf: yes` or `next: <template>` — one of the two. A LEAF holds todos in its
  Items; a template with `next:` holds nodes on that template. The product's
  chain is `plan` → `phase` → `batch`, the leaf.
- `sections` — the sections of the body, in their order, one per line. A line
  may end, two spaces after the name, on `served` (the default) or `unserved`:
  an `unserved` section is not served when its node is mounted. Items and Delivery
  belong to every template: when `sections` does not place them, they come
  last, Items then Delivery.
- `statuses` — `doing` names the sections whose writing makes a node `doing`;
  `redo` names the sections whose rewriting reopens a `done` node. No other
  status is declared.

The body of a template is the method of its level, for you: its title, how
the level is worked, and what each section asks; a node is born with that
title and the section written alone — its parent's Items line is not copied. `shown:` names the sections a node of the
level shows when a node below it is mounted. A template that cannot serve
refuses `template-invalid`; a name found in no tree refuses `template-unknown`.

A plan is born on the template `--template <name>` names, `plan` without it;
each node under it is born on its parent's `next:`. An address deeper than the
chain refuses `path-unknown`.

### The sections

Write a section by `section`, naming it: a standing section is REPLACED, an
absent one INSERTED at the rank its template gives it, Delivery or the
`--append` flag APPENDS. A name the template does not carry refuses
`section-unknown`. A section a node already holds that its template no longer
carries — a plan written in the old form, with a Target, Arbitrations or
Decisions — is read, served and kept; only writing it is
refused. A subtitle inside a section is written `###`: a prose
carrying a `## ` line, a code block included, refuses `prose-heading` before
anything is written.

### The life of an item

- **PREPARED** — a line `- <slug> -- <brief>` in its parent's Items: the entry
  derived, no document; amend the line freely until the item is framed.
- **BORN** — the first section you write creates its folder and its document
  on its level's template, the brief in the template's first section. A plan
  is born by the first section of its template.
- **DELIVERED** — its statuses moved as the work lands.

### The statuses, deduced from the writing

- A `doing` section of its template makes a node `doing`.
- A node is `done` once ALL its items are `done`, at any depth, and the
  closing rises to the plan, each closing said. A node with no item closes by
  hand alone.
- On a leaf, `section <address> Delivery --item <todo>` delivers one todo: its
  entry `- <todo> -- <text>` is appended and the todo turns `done`. Without
  `--item` it refuses `item-missing`; `node-unframed` before a `doing` section
  is written.
- On a branch, Delivery is a journal: it is appended and moves nothing;
  `--item` refuses `item-is-node`.
- A `redo` section rewritten on a `done` node reopens it: `redo`, the plan
  included, the ancestry rising with it, so the rework stays visible to the
  plan's next move.
- `block` says a stop, its reason a dated line of Delivery; the next section
  you write lifts it.
- `done <address>` closes by hand: a todo of a leaf; a born node, its todos
  left open named in a dated line of its Delivery; a prepared item, without
  being born. A node with an item under way refuses `item-engaged`.

No other verb moves a status, and no word closes a node. Every move is
surgical: the one `status:` line and its parent entry.

## Commands

Prefix each form with `./pp <key> -s pp-plan` (a mount makes no segment of its
own: `-s pp-plan` plays without an address where one segment offers it):

    ./pp <key> -s pp-plan section memo/core/storage Ground -

| Form | Effect |
|---|---|
| `section <address> <Name> [--append]` | Write one section, the prose on stdin (`-` marks it). On Items, `--append` adds the lines piped after the lines already written; a name already there refuses `slug-taken`. |
| `section <address> <Name> --remove[=<n>]` | Remove one section, heading and text, no stdin; a name standing several times needs its rank (`section-ambiguous`); a section of the node's template standing once refuses `section-kept`; no status moves. |
| `section <slug> <first section> --shared` | Birth a plan under the run's ROOT OF DOCUMENTS instead of the instance (below, « The shared root »): `documents-none` when the run has no root, `slug-taken` when the slug stands in either tree; the flag goes nowhere else. |
| `section <slug> <first section> --template <name>` | Birth a plan on the template `<name>`. |
| `done <address of a leaf>/<todo>` | Check a todo off. |
| `block <address> <reason ...>` | Say a stop; the reason a dated line of Delivery. |
| `move <src-address> <dst-parent-address> <index>` | Transfer a node under a parent whose `next:` is its template, or reorder it within its parent (`kind-mismatch` otherwise). |
| `rename <address> <new-name>` | Give a node under a plan a new name. |
| `mount <address> [--whole]` | Host the node's document chain in the view (read-only, any time). |
| `constrain <address> [<prefix>] --section production\|behavior` | Pose laws, on stdin; a line opening on a posed code replaces it in place. |
| `constrain <address> --retire <code>` | Take a law out: the line leaves, nothing is kept — on the principal's word alone (PN15). |
| `serve <address> <token ...>` | Append ONE row to the last section of the node's `serve:` rows. |
| `serve <address> -` | Replace the whole block with the rows piped, a blank line separating two sections; an empty block refuses `value-malformed`. |
| `material <slug> [<name> [<path>]\|-]` | Write the plan's material — `material: <name>` on the plan and on every node born under it, the slug by default; with `<path>`, `<name>: <path>` declared first in the PLAN.md's `materials:` block (the path as given, relative to the plan's folder; a declared name has its line rewritten); `-` takes the key out everywhere, the declaration kept; a name the plan does not declare refuses `material-undeclared`; no tree is called `repo` or `work` (`material-undeclared`; `material-invalid` with a path). No SETTINGS is read. |
| `material <slug> - <name>` | Withdraw one tree: the line `<name>` leaves the PLAN.md's `materials:` block, and nothing else is written; a name the block does not hold refuses `material-undeclared`. A node that still names it is then said by `check`. |
| `next-move` | Print the next-move lines, one per open plan: the line the bus holds for a plan of the instance, the line computed from the document for a shared plan; for a plan standing in both trees, neither line: its `plan-twice` finding, the one `check` says; pushes nothing. |
| `status [<slug>] [--all] [--engaged] [--json]` | The progress LIST, read from the front matters alone, one line per node. Without a slug: the open plans, each with its next move, then the closed ones counted; `--all` lists them too; `--engaged` adds under each open plan its nodes that are `doing`, `redo` or `blocked`. With a slug: the plan and every node under it, a leaf's todos counted on its line. A node counts its born children done over born, its prepared items apart; the plans of the instance come first, the shared ones after them with `shared` after their status. `--json` gives the same nodes as data: `address`, `template`, `status`, `born`, `depth`, `vector` (`plan:<address>`), `shared`, `children` (with the `template` of the children) or `todos`, and `next` on an open plan. |
| `templates [--json]` | The templates the tree sees, read-only: its own (`plans/_templates/`) first, the shared root's, then the product's. One line each — or, with `--json`, one object each: `name`, `origin` (`tree`, `shared`, `product`), `description`, `leaf`, the `chain` it opens down to its leaf, its `sections`; a product's template a tree overrides says `shadowed`; one that cannot serve carries its `refusal` (`code`, `detail`) instead. The document `PLANS-TEMPLATES` provides it as the reading `plan-templates`, served whenever `PLAN` opens and last at every mount: a plan's birth chooses `--template` from it. |
| `check` | Lint every plan (below). |
| `repair` | Mend what is mechanical (below); played on the principal's GO. |
| `verify` | The engine's call, never the agent's: a vector on stdin. |

### Moving and renaming

`move` writes the entry at `<index>`, both parents renumber, folders follow
their derived names, the moved document's model keys name its new home and
its Items line follows it; a prepared item moves by its parent's Items alone.
A node under way (`doing`, `redo`, `blocked`) moved under a `done` parent
reopens that parent (`redo`), its ancestry rising as for a rework.
The call SAYS what remains yours: the subtree's prose, including references
to the old home.

`rename` moves the parent's entry at its rank, the Items line, the derived
folder and `slug:` in one call, every refusal before
the first write. A plan keeps the name it was born under; a todo renames by
its parent's Items. The prose that says the old name stays yours, and the
call says so.

The TITLE line of every document `move` and `rename` touch — the node and the
nodes under it — follows in the same call: it becomes the title its template
gives its front matter, the rest of the body byte for byte. A free title, one
that does not open on the first word of its template's title (`# PLAN`,
`# PHASE`, `# BATCH` in the product's chain), is left.

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

A MATERIAL is a tree a reading reads from: a tree the PLAN declares in its own
`PLAN.md`, a `materials:` block of `<name>: <path>` lines. A node that names no
material reads the tree the launcher gave the run, or the repository when the
run has none. A plan whose code
lives in such a tree says it once: `material <slug> <name> <path>` declares the
tree -- the path kept as given, absolute or relative to the plan's folder, so
every instance that reads the plan reads the same tree -- and writes
`material: <name>` on the plan and on every node already born;
`material <slug> [<name>]` without a path chooses a tree the plan declares
already, the slug by default (one plan, one branch, its slug); every node born
later copies the plan's key at its birth. A mount then serves the node's rows
from that tree, each titled `<token> @<name>`: the engine looks the name up in
the node's document, then in the documents mounted before it -- its phase, its
plan. No SETTINGS is read; a name not declared refuses `material-undeclared` and
names the call that declares it; no tree is called `repo` or `work`: choosing either
refuses `material-undeclared`, declaring either `material-invalid`; `-` takes the key out of every node and keeps the declaration. A tree the plan
no longer needs is withdrawn by `material <slug> - <name>`: its line leaves the block,
nothing else moves, and `check` says any node still naming it. The verb rewrites the
block line by line: a `#` line a hand wrote there stays as written. On a node with a
material every row reads that tree, and that tree alone: a row whose tree does not hold
the file is not served -- the mount's block carries `(not served: …)` in its place, and
nothing is read from another tree; bring the file into the tree, or mark the row for a
tree that holds it. A document of
another tree takes the mark of a tree the plan declares (`@<name>`); `serve` answers one
reminder line for a row left unmarked and writes the row as asked, and refuses
`material-invalid` a row marked `@repo` or `@work`.

### The shared root

A run opened with a ROOT OF DOCUMENTS (`PP_DOCUMENTS` at `-new`: the directory a
launcher gives the run, a team's `teams/<team>/` at every wake-up) has a second tree
of plans: `<root>/plans/`. A plan born there by `section <slug> <first section> --shared` is
SHARED: every run opened under the same root reads it, mounts it, frames, checks off
and delivers it with the same verbs, each under the plan's own lock, `<root>/plans/<slug>.lock`.
The script learns the root at one place, the slot of the run `PP_RUN` names; without
a run, or for a run opened with no root, `--shared` refuses `documents-none` and
nothing is written.

A slug lives in ONE tree, the instance or the shared root; the birth refuses
`slug-taken` when the slug stands in either tree, so no plan is born in the shadow of
another. A plan that stands in both all the same -- a copy, a plan born before the root --
is refused `plan-twice` by every verb that resolves its slug, the message naming both
directories, nothing read and nothing written: no tree wins in silence; `status` says the
double once, `plan-twice` and its two directories (`"status": "plan-twice"`, `"twice"` in
`--json`), `next-move` says it in place of either line, and `check` reddens on it, until one
of the two is removed by hand.
`status`, `check` and `repair` walk both trees, the instance first; a shared
node says `shared` in the list and `"shared": true` in `--json`. The next move of a
shared plan is computed from its document every time it is read (`next-move`,
`status`), because the bus that holds a pushed line is this run's alone and another run
may have moved the plan since. A mount names the document by its path, `plans/<slug>/PLAN.md`,
and the engine resolves it in the instance, then in the root of documents. A shared plan
whose nodes name no material reads, in each run, the tree the launcher gave that run; a
tree the shared plan declares by a relative path is read from the plan's folder under the
root, the same tree for every run. The lock holds on one filesystem: a root shared over a
network is not covered. Nothing in the package says who frames and who delivers a
shared plan: a law of the plan, or the team's own text, does.

### The mount

`mount` derives the document chain to host from an address and emits a
`::mount <json>` directive pp collects: one pp call mounts the whole chain,
nothing is written, no status moves. The chain is the one method `PLAN`,
then, for each level from the plan down to the node, its TEMPLATE and its node,
then `PLANS-TEMPLATES` last -- also served whenever `PLAN` opens, so the
templates are on screen before a plan is born:

| document | what is served |
|---|---|
| `PLAN` | its body: how a tree of levels is kept |
| the template of the node you work on | its body (the method of its level) and its laws |
| the template of a node above it | its laws alone |
| a node above it | the sections its template names in `shown:` |
| the node you work on | its whole body, but the sections its template marks `unserved` |
| `PLANS-TEMPLATES` | its body and the reading `plan-templates`, after everything above; also whenever `PLAN` opens |

A product template mounts as `plan:templates/<name>.md`, a tree's own by its
path. A PREPARED item, or one not even prepared yet under a born parent, mounts
its template ahead, so the framing that births it plays under its laws, and
a combined GO that frames a parent then a child mounts once; a child mounted
later in the same turn extends the chain the engine already holds -- the
documents there are skipped, the deeper ones added. The node mounted REPLACES
the other born nodes of its plan: its entry names them under `replaces`, so a
batch mounted after its sibling takes the sibling, its laws and its offers out
of the view.

The LAST document of the chain — the node named, or its parent when the node
is still to come — mounts its whole body. Each ancestor mounts the sections
that arm the level below, the ones its template names in `shown:` — Expected
and Choices for a plan and a phase of the product —, each part served under
`<title>[<start>..<end>]`; a section the ancestor lacks says nothing; its
laws, offers and `serve:` rows come as before. `--whole` mounts every
ancestor's whole body instead — for a framing that needs an ancestor's Ground
or Items.

### Check and repair

`check` reddens: a done node still carrying an engaged child, a line against
its document, a broken numbering, a DERIVED folder without its entry, a
section name twice in one document, a level title that differs from its front
matter, a missing title, a `material:` no document of the node's chain declares
(one line per plan and name, `material-undeclared`; a node that names `repo` or `work` among them), a `materials:` block badly
written (`material-invalid`, once per document, whether a node names it or not), a node of the form
before the templates (`kind:` without `template:`, a `phase:` key) — the migration script of the
re-pin rewrites it, never `repair`. Any other directory is the plan's own material and
says nothing; a prepared todo without a document is no finding. `check`
confronts every line with its document, so hand edits cannot hide.

`repair` mends what is MECHANICAL — the numbering, a line against its document
(the document wins), a derived folder without its entry, a plan or a phase
open over children all done (closed: the cascade that never ran), a level
title set from its front matter or a missing one inserted, the next move of a
plan whose folder is gone taken off the bus — and says every mend; every other
finding is said with its gesture and left. It then announces the next move of
every plan it mended. `nothing to repair` is said only when it mended nothing
and left nothing.

### Vectors and `verify`

The plans' nodes are VECTORS — one family this package declares at its
manifest, `plan`, `verify: pp-plan`: `plan:<address>`, the address every verb
takes, at every depth (`plan:<slug>` a plan, `plan:<slug>/<node>/…` a node
under it). A run that the agents' launcher starts with its option
`--vector plan:<address>` (`./pp agent run` or `./pp agent start`) mounts that
node at every exchange, once `verify` has checked its address.

`verify` is the engine's call at every entry and service of the bus: the
address must RESOLVE in the tree — a plan born; a node under it born or
PREPARED as an Items entry — `path-unknown` otherwise, `address-malformed` for
an empty address or name, `family-foreign` for a family other than `plan`.

## Refusals

Refusals exit 2 and write nothing; a malformed call says the verb's usage in
one sentence. Writes are atomic.

A verb that writes takes the plan's lock, `plans/<slug>.lock`, AFTER it has read
its stdin: a call waiting for its prose holds nobody up. What needs no lock is
refused before it is taken -- a plan born in no tree, a prose missing or opening
a section of its own --, so no lock file is made for a plan that is not there,
and pp-plan never removes one.

| Code | When |
|---|---|
| `path-unknown` | no such node: an absent entry says Items, a numbered segment says the bare address, a prepared item says its first section; a plan born in no tree, for `done`, `block`, `rename`, `move`, `constrain`, `serve`, `material` and a `section` under it, says `plans/<slug> has no PLAN.md -- no plan of that name is born`, before any lock |
| `section-unknown` · `section-ambiguous` · `section-kept` | a section the node's template does not carry, a section standing several times, or a section of the template removed |
| `template-unknown` · `template-invalid` · `template-missing` | a template no tree carries (a `next:` included), a template whose front cannot serve (neither or both of `leaf` and `next`), a node whose front carries `kind:` instead of `template:` (the migration script of the re-pin rewrites it) |
| `node-twice` | a plan's folder holding two node files |
| `node-unframed` | a Delivery on a node no `doing` section has framed |
| `item-line-malformed` · `item-engaged` · `item-missing` · `item-is-node` | an Items line without `- <slug> -- <brief>`, a born item rewritten out or a node closed by hand over work under way, a leaf's Delivery without `--item`, `--item` on a branch |
| `done-invalid` · `status-invalid` · `reopen-invalid` | a status the writing does not allow |
| `slug-taken` · `name-invalid` · `kind-mismatch` | a name already used, malformed, or of another kind |
| `code-unknown` | a `--retire` on a code never posed |
| `prose-missing` · `prose-heading` | no prose on stdin, or a `## ` line inside a section |
| `index-invalid` · `target-unknown` | a `move` to a rank or a parent that does not exist |
| `value-malformed` · `token-invalid` · `serve-range-malformed` | an empty serve block, a token the engine refuses, a bracket left open |
| `serve-heavy` | a token without a range whose file, read in the plan's material, weighs more characters than `plan_serve_budget` (40000 by default): serve it by a range on its function or section tags |
| `material-undeclared` | a material name the plan does not declare in its `materials:` — declare it by `material <slug> <name> <path>`; `repo` and `work` name no tree |
| `material-invalid` | a path given for `repo` or `work`, a name that is not one word, a `materials:` block the engine's reader refuses, or a `serve` row marked `@repo` or `@work` |
| `plan-twice` | a slug whose `PLAN.md` stands in the instance AND under the run's root of documents: every verb that resolves it, nothing read or written; the message names both directories -- remove one by hand |
| `documents-none` | `--shared` under a run opened with no root of documents, or with no run naming the call |
| `frontmatter-malformed` | a document the script cannot read |
| `argument-missing` · `argument-unexpected` · `verb-unknown` | a malformed call: no verb (one line of usage, never this text), a flag where an address is due (no lock taken) |
| `method-missing` · `not-an-instance` | the package's method document absent, or no instance to write in |
