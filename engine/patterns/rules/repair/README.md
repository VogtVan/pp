# repair — what happens when the agent misses

## What you write

Nothing in your document. The agent writes it, in a proof (see `rules/prove`): a `fail`
object may carry `"fix"` — the correction it will make — or `"blocked"` — what is missing
to meet the law. The operator's setting `work_repairs_allowed` bounds the repairs.

## What you get

- A miss the tool sees — a `PICK` outside its OPTIONS, a bare `fail`, a proof that misses
  — replays the whole document from its first step: the heading says `REPAIR <n>`, a
  DEVIATION says the miss. The readings already served are not served again.
- A block served again without an answer is no miss: it comes back the same, no repair.
- A `fail` that names its `"fix"` repairs in place: the work stays, the agent corrects it,
  then proves the failed codes alone. A proof naming other codes is asked again; the same
  code failing a second time replays the document.
- A `fail` that carries `"blocked"` closes the proof without a repair: the work leaves, the
  closing says the gap, and the agent tells the principal. An empty `"blocked"` is a bare
  `fail`.
- An empty answer to a `PROVE` is no proof: it repairs.
- What counts toward the bound is what replays or misses — a bare `fail`, a relapse, an
  empty answer, a proof that misses; a fix that holds counts nothing. The count survives
  the replays; past the bound the run hands back to the principal. `-stats` counts the same
  repairs.
- Steps fused in one output repair together: the whole output is played again, and the
  heading of each step the repair plays again says `REPAIR <n>`.
- Repairs play the same under the agent's conduction and the principal's.

## When to use it

- Write procedures whose steps a miss can safely replay from the start: a step that reads
  or produces again gives the same result.
- Write laws the agent can prove, so that a `fix` or a `blocked` is possible rather than a
  replay.
- Raise or lower `work_repairs_allowed` to say how often the agent may try before the
  operator is asked to look.

## What refuses

- Past `work_repairs_allowed`, the next miss refuses `repair-exhausted`: the run hands back
  to the principal, nothing more is played.

## The demonstration

- `procs/CLAIM.md` — one law of production, an `INFER`, a `PROVE`.
- `procs/REDO.md` — names to list, a reading, then one name to `PICK`.
- `procs/CALLER.md` calling `procs/CRAFT.md` — a proof that can miss its codes.
- `procs/PAIR.md` — a piece of work and its `PROVE`, fused in one output.
- `procs/BROKE.md` — an `INFER`, a `§`, then its `PROVE`: the output closes before the proof.

## The test

`tests/patterns/rules/repair.py` plays the demonstration: CLAIM's bare `fail` replaying the
document, the fix in place and its exact mini-proof, the relapse; REDO's block served again
with no repair, its missed `PICK` replaying without serving the reading again; the declared
gap, the empty one, fixes that hold under a bound of one, the relapse counted once, a fix and
a gap together; `repair-exhausted` on bare fails, on a relapse past the bound and on missed
`PICK`s; CRAFT's empty answer repairing, CALLER's stranger codes handing back at the bound;
PAIR repairing whole; BROKE's repaired `PROVE`, closed early by the `§`, asked again at the bare call
and never judged empty; CLAIM's repair under the principal's conduction.
