# addressing — where a name leads

## What you write

A name wherever a document names another: a `serve:` row, `SERVE <name>`, `CALL <name>`,
an offer, a mount. Three forms:

- a bare NAME: `LEDGER.md`;
- a PATH, a token that carries a `/`: `engine/x.py`, `plans/p/PLAN.md`;
- in a mount, `<package>:<path>`: a file of a package's bundle, `shelf:kinds/NOTE.md`.

## What you get

- A bare name is searched in your instance's own space, then in each package your
  instance plays — a package before the packages it requires. The document is the
  deepest one found; a same name found nearer amends it (see `composition/overlay`).
  Only when no space answers is the repository's root read (`README.md`,
  `design/target.md`); the repository never amends anything.
- A path reads the repository's file when the repository holds it — the source beside
  your instance — and your instance's otherwise; `.sys/<path>` reads the machine's copy.
  When both hold the path, the repository is served and the shadowing is said once in the
  run (`serve-shadowed`). A material chooses another tree for a path (see
  `context/material`).
- A mount takes the three forms: a package's document by its bare name, a document by its
  path (your instance first, the repository last), a file a package carries outside its
  documents by `<package>:<path>`. Its laws are in force, its body served when asked.
- A mounted document that disappears is said once in the run, `mount-gone` of level note,
  on the blocks that follow — never on a `-peek` — and its laws leave.
- A served name found nowhere is said gone in the block (see `context/serve`).
- Never write the path of a package's pinned copy under `.sys/vendor/`: an upgrade moves
  it. Name the document instead.

## When to use it

- Serve a package's reference or your repository's own documents by their bare names.
- Name a document no bare name tells apart — a node of a plan — by its path.
- Mount a file a package keeps outside its documents by its package's address.

## What refuses

- A mount of an absolute path, a `..`, a package your instance does not play, or an
  address no file answers refuses `mount-missing`; nothing is mounted.
- A `CALL` whose name resolves nowhere refuses `document-missing` (see `composition/call`).

## The demonstration

- `procs/LEDGER.md` — a package's document, with its law `AD1`; `procs/NOTE.md` — a file
  the same package keeps outside its documents, with its law `AD2`.
- `procs/FINDER.md` — two bare names: one the package answers, one only the repository's
  root holds.
- `procs/PATHS.md` — one path read from the repository and from the machine's copy.
- `procs/DESK.md` — the steps the documents are mounted on.

## The test

`tests/patterns/context/addressing.py` writes the package `shelf` (LEDGER among its
documents, NOTE under `kinds/`), the repository's files and the machine's copy, then plays
the demonstration: the package's LEDGER served while its repository twin is not, MANUAL
from the repository's root; the path served from the repository, from the machine, the
place and the shadowing said, the instance answering once the repository's file is gone;
LEDGER mounted by name and NOTE by `shelf:kinds/NOTE.md`, their laws in force; the four
addresses that refuse `mount-missing`; NOTE removed, `mount-gone` said once, never on a
peek.
