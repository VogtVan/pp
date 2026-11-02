# fusion — choose how many steps one output carries

## What you write

Nothing, to take the instance's pace: the setting `instructions_fusion` of its
`SETTINGS.md` says how many steps an output may carry — `none` (one step per output, the
engine's default), a number, or `max` (every step pp can join).

To set the pace of one document whatever the instance says, the key `fusion:` in its front
matter, with the same values:

    fusion: none

## What you get

- Under `max`, pp joins into one output every step it can render in a row: the steps the
  agent says in its message, one line each under a single INSTRUCTION title. The heading
  gives the range: `TRIO{1-3/3}`.
- Under a number n, an output carries at most n steps; the next call carries the rest.
- A document's own `fusion:` wins over the setting while that document plays.
- pp never joins across a `§` (see `control-flow/section-break`), and never joins a step
  whose production goes to the tool with the step after it: such a step ends the output.

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

## The test

`tests/patterns/control-flow/fusion.py` plays `TRIO.md` under `max` (one output, the range in
the heading) and under 2 (two steps, then the third), then `STEPPED.md` under `max` (one step
per output).
