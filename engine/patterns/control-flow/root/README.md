# root — what happens when the procedure runs out of steps

## What you write

Nothing: no key and no keyword end a passage. The document a run opens on is its ROOT;
write its steps in the order one exchange needs them.

## What you get

- A PASSAGE is everything the run does between two messages of the principal. It ends
  when the root has no step left: the last step's block closes on AWAIT, and the run waits
  for the principal's next message.
- Before that, the run waits for a production: a text handed to the tool then is not a
  message, it comes back under a DEVIATION, with no repair counted.
- A `§` does not end the passage (see `control-flow/section-break`). The exchange is
  counted, and the documents mounted for it are taken down, at the end of the passage
  only.
- The next message rewinds the root to its first step, under the same run key, and the
  next passage begins. A root whose last step is its first block parks on that block. A message given when the run opens is the context of its first
  passage.
- In a run its principal conducts, the last free step waits for the principal's call;
  after it, AWAIT, and the next message rewinds the root the same way.
- A step that ends the document is said to the principal at its own step (see
  `steps/work` and `steps/infer`); the AWAIT itself delivers nothing and proves nothing:
  a proof is asked where the document writes `PROVE` (see `rules/prove`).

## When to use it

- Every run has one: the base's TURN is such a root.
- A document opened by `OPEN` or `-open` becomes the root while it stands, wherever its step
  is (see `control-flow/open`).
- Put a step at the end of the root only when it must be the last thing of every
  exchange; put a `PROVE` before the end when the passage's work must be proven.

## What refuses

Nothing here: the root ends by itself. A root that declares a successor (`next:`) refuses
`next-floor` (see `control-flow/next`).

## The demonstration

- `procs/FLOOR.md` — the root: an `INFER`, a `§`, then a `WORK`.
- `procs/HOSTED.md` — a document mounted during the passage, to show it taken down at its
  end.
- `procs/LINEAR.md` — a root of one reading and one step: its first block ends the passage.

## The test

`tests/patterns/control-flow/root.py` plays `FLOOR.md`: a text handed mid-passage bounces;
across the `§` the count stands and the mount lives; the last step ends the passage (AWAIT,
the count moves, the mount is gone); the next message rewinds the root under the same key;
a message opens a run; LINEAR parks on its first block and a bare call plays it again,
each passage counted; then the same passage under the principal's conduction.
