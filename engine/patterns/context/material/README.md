# material — read a row from another tree

## What you write

- In a document's front matter, `materials:`, a block with one line `<name>: <path>` per
  tree: a tree a reading may name — another copy of the repository, on another branch for
  instance. The path is absolute, or relative to the folder of the document that declares it.
- On a `serve:` row, the mark `@<name>`, first or last: `@alt engine/x.py`,
  `engine/x.py @alt`, `code: @alt engine/t.py[def alpha..def beta]`.
- In a document's front matter, `material: <name>`: every row of that document reads that
  tree, unless the row says otherwise.
- Nothing, for the run's own tree: a row that names no tree reads the tree the run was
  given at its opening, and the repository when it was given none.

## What you get

- The nearest word wins: the row's mark, then the `material:` of the document that carries
  the row, then the nearest caller that says one.
- A row that names a tree is read from that tree and from no other. When the tree cannot
  answer, the reading is not served: the block carries one line `(not served: …)` in its
  place, under the title `<token> @<name>`, and nothing is read from another tree. Three
  causes: a name no document in play declares (`material-unknown`), a path that is no
  directory (`material-missing`), a file the tree does not hold (`serve-stale`) — each
  also a diagnostic of level note, and the block's trace notes the reading `missing`, the
  cause under `lacks`. The step goes on. To get the reading: declare the name in a
  `materials:` block, correct its path, or bring the file into the tree.
- A row that names no tree reads the run's own tree when the run was given one and it
  holds the file, the repository otherwise (see `context/addressing`).
- A CALLed document without `material:` reads its caller's tree; a mounted document reads
  its own.
- A name is looked up in the documents in play, the nearest first, and the first that
  declares it wins: the document that carries the row; for a mounted document, the
  documents mounted before it, the last mounted first; then the calling procs, the nearest
  first. One declaration at the top — a plan's head — serves every document under it; a
  document that declares the name again wins for its own rows and for those it calls.
- A relative path is read from the folder of the document that declares it, never from the
  workspace of the reader: two workspaces that read one document read one tree.
- The rows an overlay adds to a document read as that document's own rows: in a called
  document, the tree its caller names and the trees its callers declare (see
  `composition/overlay`).
- After a compaction, a row comes back from the tree it was first read in.
- A path read from a named tree renders under `<token> @<name>`; a row that names none,
  under the token alone.
- A bare name ignores the material: names resolve as they always do (see
  `context/addressing`). The material chooses the tree of a path, never a name.
- The run's own tree is given at the opening and stays with the run through an upgrade that renews it.
- A reading is proven by its content (see `context/serve`): one text in two trees is
  served once, two texts are two readings.
- `SETTINGS.md` declares no tree. A `material.<name>` key left there is read by nothing:
  `./pp upgrade` and `./pp doctor` keep it under `unowned` and say it once.

## When to use it

- A plan whose code lives on a branch, in another copy of the repository: declare that copy
  once at the plan's head (`materials:`), name it in `material:`, and the framings read the
  branch — in every workspace that mounts the plan.
- Compare a file on a branch with the repository's, in a document that says no
  `material:`: one row marked `@<name>`, one unmarked.
- A proc played in a clone the run was opened on: its unmarked rows read that clone.

## What refuses

- A row with two marks, or a mark with no name (`@` alone), refuses `material-invalid`.
- A `materials:` block refuses `material-invalid`, naming the document, when a row of that
  document is read or looks a name up in it: a value that is no block of lines, a line
  without a name or without a path, a name declared twice.
- No tree is called `repo` or `work`: a mark `@repo` or `@work`, a `material: repo` or
  `material: work`, and a declaration of either name refuse `material-invalid`. Give the
  tree a name of its own; for the run's own tree, name no tree at all.

## The demonstration

- `procs/MARKED.md` — rows marked first: a whole file, a cut between two tags, a bare name;
  and an unmarked row.
- `procs/TRAILING.md`, `procs/TRAILED.md` — rows marked last, in a proc and in a mounted
  framing.
- `procs/OWNED.md` — a document that declares two trees and says `material: alt`, a row
  marked for the other tree, a `CALL` to `procs/HEIR.md`, which inherits the tree.
- `procs/NODE.md` — a mounted framing that declares and says its own material.
- `procs/CHAIN.md`, `procs/NEAR.md` — a proc that declares two trees and calls a document
  that declares one of them again: the nearest declaration wins, the other name comes
  from the caller.
- `procs/TREES.md`, `procs/LEAF.md` — a head that declares a tree and a framing mounted
  after it, which names that tree without declaring it.
- `procs/SHARED.md` — a document that declares its tree beside itself, mounted by two
  workspaces.
- `procs/WORKER.md` — a row that names no tree: it reads the run's own.
- `procs/LACKING.md` — an unknown name, a declared path that is gone, a file the tree
  lacks: three readings not served, each said in the block.
- `procs/SAME.md` — one text the same in two trees, one that differs.
- `procs/TWICE.md`, `procs/BARE.md` — two marks, an empty mark: they refuse.
- `procs/MISDECLARED.md` — a declaration that takes the name `repo`: it refuses.
- `procs/RETIRED.md` — a row marked `@repo`: it refuses.
- `procs/MISCHAIN.md` — a caller whose declaration gives a name no path: the row of the
  document it calls refuses when it looks the tree up there.
- `procs/HEIR.overlay.md` — an overlay of `HEIR.md`, placed at its name in the workspace: the
  rows it adds read the tree `OWNED.md`, the caller, names and declares.

## The test

`tests/patterns/context/material.py` writes two trees and a shared root, then plays the
demonstration: the marks first and last, in a proc and at a mount; the unmarked row; the
document's material, a row marked for another tree, the heir, the mounted framing, the
heir's row after a compaction; the run's own tree at the opening,
read by a row that names none and kept through a renewal, and the same row without one;
the readings not served said in the block, nothing read from another tree, among them a
name only a `material.` key of `SETTINGS.md` carries; one text served once; the nearest declaration in a chain of calls and at a
mount; two workspaces without any `material.` key that mount one document and get one
reading, with one proof; the rows an overlay adds to a called document; the refusals of
the rows and of the declarations, a declaration looked up through a call and the two
names no tree takes among them. It also holds that the build's checks and the writer of
rows accept a mark.
