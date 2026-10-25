# material — read a row from another tree

## What you write

- In `SETTINGS.md`, `material.<name>: <path>`: a tree a reading may name — another copy
  of the repository, on another branch for instance — its path relative to the workspace or absolute.
- On a `serve:` row, the mark `@<name>`, first or last: `@alt engine/x.py`,
  `engine/x.py @alt`, `code: @alt engine/t.py[def alpha..def beta]`.
- In a document's front matter, `material: <name>`: every row of that document reads that
  tree, unless the row says otherwise.
- Two names are the engine's own: `@repo`, the repository, and `@work`, the tree the run
  was given at its opening.

## What you get

- The nearest word wins: the row's mark, then the `material:` of the document that carries
  the row, then the nearest caller that declares one, then the run's own tree, then the
  repository. A row that names nothing reads the repository.
- A CALLed document without `material:` reads its caller's tree; a mounted document reads
  its own.
- A path read from a tree renders under `<token> @<name>`; from the repository, under the
  token alone.
- A bare name ignores the material: names resolve as they always do (see
  `context/addressing`). The material chooses the tree of a path, never a name.
- The run's own tree is given the same way under the agent's conduction and the
  principal's, and stays with the run through an upgrade that renews it.
- A reading is proven by its content (see `context/serve`): one text in two trees is
  served once, two texts are two readings.
- What a material cannot give is said, never silent, and the row reads the repository: a
  name `SETTINGS.md` does not declare (`material-unknown`, `@work` too when the run was
  given no tree), a path that is no directory (`material-missing`), a file the tree lacks
  (`serve-stale`) — each a diagnostic of level note.

## When to use it

- A plan whose code lives on a branch, in another copy of the repository: name that copy
  once in `material:`, and its framings read the branch.
- Compare a file on a branch with the repository's: one row each, `@<name>` and `@repo`.
- A proc played in a clone the run was opened on: read that clone by `@work`.

## What refuses

- A row with two marks, or a mark with no name (`@` alone), refuses `material-invalid`.
- `SETTINGS.md` refuses `settings-invalid` for `material.` with no name, for
  `material.repo` and `material.work` (the engine's names), and for an empty path.

## The demonstration

- `procs/MARKED.md` — rows marked first: a whole file, a cut between two tags, a bare name;
  and an unmarked row.
- `procs/TRAILING.md`, `procs/TRAILED.md` — rows marked last, in a proc and in a mounted
  framing.
- `procs/OWNED.md` — a document that says `material: alt`, a row back to `@repo`, a `CALL`
  to `procs/HEIR.md`, which inherits the tree.
- `procs/NODE.md` — a mounted framing that says its own material.
- `procs/WORKER.md` — a row that reads the run's own tree.
- `procs/LACKING.md` — an unknown name, a declared path that is gone, a file the tree lacks.
- `procs/SAME.md` — one text the same in two trees, one that differs.
- `procs/TWICE.md`, `procs/BARE.md` — two marks, an empty mark: they refuse.

## The test

`tests/patterns/context/material.py` writes two trees and `SETTINGS.md`, then plays the
demonstration: the marks first and last, in a proc and at a mount; the unmarked row; the
document's material, `@repo`, the heir, the mounted framing; the run's own tree at the
opening under both conductions, kept through a renewal, and `@work` without one; what is
missing said; one text served once; the refusals of the rows and of `SETTINGS.md`. It also
holds that the build's checks and the writer of rows accept a mark.
