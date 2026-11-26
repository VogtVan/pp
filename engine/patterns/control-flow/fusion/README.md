# fusion — choose how many steps one output carries

## What you write

Nothing, to take the instance's pace: the setting `instructions_fusion` of its
`SETTINGS.md` says how many steps an output may carry — `none` (one step per output, the
engine's default), a number, or `max` (every step pp can join).

To set the pace of one document whatever the instance says, the key `fusion:` in its front
matter, with the same values:

    fusion: none

How the steps of one output group into SEGMENTS is not written in a proc: it follows the
laws in force. The setting `tools_in_scope` of `SETTINGS.md` says whether the offers count
too: `false` (the default) or `true`.

## What you get

- Under `max`, pp joins into one output every step it can render in a row: the steps the
  agent says in its message, one line each. A step that reads something of its own -- its
  brief, the list it chooses from -- shows it first, then its line under an INSTRUCTION
  title of its own; the lines that nothing separates follow one another under a single
  INSTRUCTION title. The heading gives the range: `TRIO{1-3/3}`.
- Under a number n, an output carries at most n steps; the next call carries the rest.
- A document's own `fusion:` wins over the setting while that document plays.
- pp never joins across a `§` (see `control-flow/section-break`), and never joins a step
  whose production goes to the tool with the step after it: such a step ends the output.
- The steps of one output read in SEGMENTS. A segment is a heading, then its readings, its
  `TOOLS` and its `CONSTRAINTS` said once, then its steps. A step joins the segment above it
  when the laws in force for it are that segment's, whatever document it belongs to. A step
  under other laws opens a new segment; the segments are numbered `[n]` when an output
  carries several.
- The heading of a segment is the one of the step that opens it, and its range counts the
  steps of that document alone. A step of another document that joins the segment is said
  by its line, which ends on the name of its document: `INFER any => terminal  (RIGHT)`.
- Under `tools_in_scope: false`, a difference of offers opens no segment: the `TOOLS` of a
  segment name what each of its steps offers, each name once. Under `true`, two steps under
  the same laws and with different offers read in two segments.
- A `PROVE` joins the last segment when the laws in force for it are that segment's; its
  line names the codes it asks. Like any step that asks a value, it closes the output, after
  the steps said above it, whatever document they belong to.
- The block that closes an output follows the same rule: under the laws of the last segment
  it joins it, under other laws it opens a heading of its own. The block that ends a passage
  is read under the laws its steps were said under: the documents mounted for the passage
  leave with it, and their leaving opens no segment.
- A heading a repair opens under the laws of the segment above says neither `TOOLS` nor
  `CONSTRAINTS` again: that segment said them.

## When to use it

- Fewer, larger outputs cost fewer calls: `max` suits an instance whose steps are short.
- A document whose steps must be read one at a time — a review, a careful sequence —
  sets `fusion: none` for itself, whatever the instance does.

## What refuses

- A value that is not `none`, `max` or a whole number from 1 refuses `settings-invalid`,
  in `SETTINGS.md` as in a document's own `fusion:`.

## The demonstration

- `procs/TRIO.md` — three `INFER` in a row.
- `procs/STEPPED.md` — two `INFER` with `fusion: none`.
- `procs/LEFT.md`, `procs/RIGHT.md` — one `INFER` each, with no law and no offer of their own.
- `procs/RULED.md` — one `INFER` under a law of its own, `FU2`.
- `procs/TOOLED.md` — one `INFER`, with an offer of its own, `TRIO`.
- `procs/DUET.md` — calls LEFT then RIGHT: two documents under the same laws.
- `procs/APART.md` — calls LEFT then RULED: the second under its own law.
- `procs/GEARED.md` — calls LEFT then TOOLED: the same laws, one more offer.
- `procs/CHECKED.md` — an `INFER`, a call to LEFT, then `PROVE`, under its law `FU1`.
- `procs/SOLO.md` — an `INFER` and its `PROVE`, under `FU1`.

## The test

`tests/patterns/control-flow/fusion.py` plays `TRIO.md` under `max` (one output, the range in
the heading) and under 2 (two steps, then the third), then `STEPPED.md` under `max` (one step
per output). Under `max` it plays DUET (one segment, two lines, each naming its document) and
APART (two segments); GEARED under `tools_in_scope: false` (one segment, its `TOOLS` the union
of the offers) and under `true` (two segments); CHECKED (LEFT's step joins the segment, the
proof closes the same output) and SOLO (the line and its proof in
one output, the proof in the last segment, its codes on its line).
