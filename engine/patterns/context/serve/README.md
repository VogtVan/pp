# serve — readings the tool brings to a step

## What you write

- In the front matter, `serve:`: rows of tokens, one row per line, sections separated by
  a blank line. A token is a document's name or path, whole (`STYLE.md`), between two
  tags (`GLOSSARY.md[draft --..finding --]`, either end may stay open:
  `[..draft --]`, `[verdict --..]`), or by line ranges (`GLOSSARY.md[7-8]`). A row may
  start with a nature, `code:` or `reference:`.
- In the `proc:`, `SERVE`: bare, it reads the next section of `serve:`; named
  (`SERVE <NAME>.md`, a tag or a range allowed), it reads that token.
- On a mounted document, the same `serve:` rows: they play when the document is mounted
  (see `composition/mount`). A mount may also ask for parts of the document's body: a
  list of selections, each written as the inside of a tag token (`## Beta..## Gamma`).

## What you get

- `SERVE` asks the agent nothing: the tool reads, and the reading rides the block of
  the next step — or the closing that parks, when nothing is asked after it.
- A bare `SERVE` reads one section, whole: every row of it, every token of each row.
  The next bare `SERVE` reads the next section.
- Each reading renders under its title, the token as you wrote it (path, tag or range).
- A reading is proven once per run, by its content: brought again by another section, a
  named `SERVE`, a mount or another name holding the same bytes, it renders nothing.
  From one passage to the next it stays spared.
- A bare name resolves in the instance first, then its packages, then at the
  repository's root (`README.md`, `design/target.md`); the instance keeps the upper hand
  on a same name (see `context/addressing`). A name found nowhere is said gone in the
  block.
- A row may read its path from another tree, a branch's worktree for instance (see
  `context/material`).
- A tag is read at the start of a line; the end tag is excluded and sought after the
  start. A start tag found nowhere serves nothing and is said; an end tag found nowhere
  serves to the end. A line range past the end serves what stands. Any text file
  serves: a code file named without a range rides whole.
- A CALLed proc's body is a reading too: under `proc_body_serve: once` it rides the
  first CALL only, under `always` every CALL.
- At a mount, the rows play softly: a document gone is noted in its section, a range
  clamped; what is missing is signalled for the run's review. A selected part renders
  under `<NAME>[<selection>]`, is proven on its own, and comes back after a compaction.

## When to use it

- Pace the readings of a long procedure: one section per step, read when the step
  needs it.
- Name exactly the part of a long document a step needs, with tags rather than line
  numbers: tags survive the edits around them.
- Frame a mounted document with the readings it rests on.
- To render a skill's output rather than a document, see `context/payload`; for a
  document that is only read, see `context/doc`.

## What refuses

- A bare `SERVE` with no section left refuses `serve-exhausted`.
- A token badly written (`[..]`, `[a..b..c]`, `[abc]`, an unclosed `[`) refuses
  `serve-range-malformed`, and so does a line range out of order, from zero, overlapping
  or not numeric.
- A mount whose row refuses mounts nothing — nor the documents mounted with it in the
  same gesture; the view and the run stand as before, and the repaired gesture plays
  whole.
- A mount whose selection is badly written (`..`, `a..b..c`, an empty list, a
  non-text) refuses `mount-invalid` and writes nothing.

## The demonstration

- The readings: `procs/STYLE.md`, `procs/GLOSSARY.md` (one word per line, the tags),
  `procs/NOTES.md`, `procs/PARTS.md` (a body in four parts), `procs/TWICE.md` and
  `procs/COPY.md` (the same bytes under two names).
- `SERVE`: `procs/RIDE.md` (a named `SERVE` then an `INFER`), `procs/ALONE.md` (a
  `SERVE` alone), `procs/BUNDLE.md` (one row of two), `procs/PACED.md` (two sections),
  `procs/OVERRUN.md` (one section, two `SERVE`), `procs/SECTION.md` (three lines, one
  section), `procs/ONCE.md` (a reading in two sections), `procs/TWINS.md`,
  `procs/ROOTED.md` (names found in the repository, the instance and nowhere).
- The rows: `procs/TAGGED.md` (tokens with blanks, tags gone), `procs/TORN.md` (a row
  badly written), `procs/WHOLE.md` (a code file), `procs/RANGE.md` (a line range),
  `procs/CALLER.md` calling `procs/ONE.md` twice.
- The mounts: `procs/DESK.md` (the step they join), `procs/FRAMING.md` (a gone document
  and a clipped range), `procs/FRAMING2.md` (the style again, a tagged row),
  `procs/ATOMIC.md` (a row that refuses), `procs/CHAIN1.md` to `procs/CHAIN3.md` (a
  chain whose last row refuses).

## The test

`tests/patterns/context/serve.py` plays the demonstration: what rides and when,
section by section, then `serve-exhausted`; a reading proven once, by content too, and
spared from one passage to the next under the agent's conduction and the principal's;
the titles, the repository's root; the tagged rows, the absent said, the badly written
refused, the whole file, the line range, the CALLed body under `once` and `always`; the
mount's rows soft, signalled, silent once proven, atomic, repaired; the selections
stacked, spared, kept, nested, absent, refused. It also holds the grammar the reader,
the writer of rows and the lint share. The repository's files the rows name are written
at the test's time.
