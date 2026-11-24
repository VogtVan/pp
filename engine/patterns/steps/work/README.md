# work — give the agent a free piece of work

## What you write

One line in your `proc:`: `WORK`, with no argument. The body of your document says the
work to do.

## What you get

- The step's line reads `WORK any => terminal  (DOCUMENT)`: what the agent produces there is
  for the principal, and it hands it to pp by the PRINT call, `./pp <key> -print <DOCUMENT> - <<'EOF'`, the production, `EOF` -- the
  document the line names in brackets. pp keeps the production as handed and answers one
  line. The last `WORK` its output says keeps `=> terminal` too (see `control-flow/root`).
- The step is DUE from the moment its output is rendered until its print call. A gesture in
  between -- a mount, `-peek`, a space opened or closed -- leaves it due, and the block that
  comes back shows its line again, above the step that stands.
- The principal's last message rides the block as the context of the step: the work
  serves that message.
- Inside the step the agent is free: it reads, chains its tools and produces as many
  times as the work takes, under the laws on screen.
- When the `WORK` is the last step of the document, the passage is over once it is
  printed: the run waits for the principal's next message (see `control-flow/root`).
  Otherwise the run moves on to the next step once the print is in.
- A production handed by the value call (`./pp <key> -`) instead of its print call is not
  recorded: the block that stands comes back with a DEVIATION that names the print call to
  make. A value, a proof or the bare call while a print is due comes back the same way. No
  repair is counted.
- An output that owes the tool nothing has no closing line: the principal's call moves the run on. The last free step of an output stays
  open until that call, and only then is the passage over (the engine's bench proves it
  in `tests/engine/execution/principal-hold.py`).

## When to use it

- The work cannot be cut into fixed productions: an investigation, a fix, an answer to
  the operator's ask.
- You want the agent to act with its own tools, and only the result to reach the
  principal.
- When you need one production in a given form, use `INFER` instead (see `steps/infer`).

## What refuses

Nothing: a `WORK` takes no argument and its form, `any`, takes any text. An empty print is
refused at the return of the call and stays due; after `work_repairs_allowed` refusals pp lifts
it and keeps nothing. A production handed by the value call bounces, as said above; it is not a
refusal.

## The demonstration

- `procs/ASK.md` — one `WORK` alone: printed for the principal, then the passage is over.
- `procs/HANDOFF.md` — a `WORK` then an `INFER`: the `WORK` printed, the run moves on to the
  summary.
- `procs/TWOFOLD.md` — two `WORK`s then an `INFER`, said in one output: each `WORK` printed by
  its own call; a `-peek` between the two prints shows the second still due.

## The test

`tests/patterns/steps/work.py` plays `ASK.md` and checks its line, its context and its
closing; plays `HANDOFF.md`, hands a production on the `WORK` by the value call and checks the
bounce, then prints it and checks the move to the `INFER`; plays `HANDOFF.md` again: its
steps on no closing line, the passage over at the principal's call, closed on AWAIT with no call
under it; and plays `TWOFOLD.md`: a `-peek` between its two prints leaves the second due, and both
productions are kept as handed.
