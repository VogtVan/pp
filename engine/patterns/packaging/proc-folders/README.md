# proc-folders — your procs, shelved in folders

## What you write

Inside a `procs/` folder -- your instance's `.pp/procs/`, or a package's `procs/` -- any
folder of your own, to keep related procs together:

    .pp/procs/
      workflows/
        REVIEW.md
        RELEASE.md
      _drafts/
        IDEA.md

A document keeps the NAME of its file: `procs/workflows/REVIEW.md` is `REVIEW`, wherever
you name it.

## What you get

- The document plays exactly as if it stood at the top of `procs/`: it is in the catalog,
  a `CALL REVIEW.md` reaches it, `tools:` offers it, a door opens it, a `mount:` or an
  `attach:` it declares plugs it in, a mount names it `REVIEW.md`.
- Its overlay keeps the same name, where any overlay stands (see `composition/overlay`):
  `.pp/REVIEW.md` amends `procs/workflows/REVIEW.md`.
- A folder whose name starts with `_` is your workshop, like a file whose name starts with
  `_`: nothing in it is ever read.
- An instance whose procs all stand at the top of `procs/` is served exactly as before.

## When to use it

- Shelve the procs of one workflow together, or a package's procs by theme.
- Keep drafts beside the procs that play, in a `_` folder.
- The folder groups your files; it is not part of the name: two documents of one `procs/`
  never share a name, whatever their folders.

## What refuses

- Two files of the same name anywhere in one `procs/` refuse `document-duplicate` at the
  build, naming both paths; nothing is compiled.
