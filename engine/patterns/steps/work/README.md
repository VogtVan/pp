# work — give the agent a free piece of work

## What you write

One line in your `proc:`: `WORK`, with no argument. The body of your document says the
work to do.

## What you get

- The step's line reads `WORK any => words`: what the agent does there, it says to
  the principal, in its words, at this step. Nothing is handed to the tool.
- The principal's last message rides the block as the context of the step: the work
  serves that message.
- Inside the step the agent is free: it reads, chains its tools and produces as many
  times as the work takes, under the laws on screen.
- When the `WORK` is the last step of the document, the passage is over once it is
  said: the run waits for the principal's next message (see `control-flow/root`).
  Otherwise the call with the key alone moves on to the next step.
- A production handed to the tool on a `WORK` is not recorded: the same step comes back
  with a DEVIATION that says to write it in the words instead. No repair is counted.
- In a run its principal conducts, the steps are the same and an output that owes the
  tool nothing has no closing line: the principal's call moves the run on. The last free step of an output stays
  open until that call, and only then is the passage over (the engine's bench proves it
  in `tests/engine/execution/principal-hold.py`).

## When to use it

- The work cannot be cut into fixed productions: an investigation, a fix, an answer to
  the operator's ask.
- You want the agent to act with its own tools, and only the result to reach the
  principal.
- When you need one production in a given form, use `INFER` instead (see `steps/infer`).

## What refuses

Nothing: a `WORK` takes no argument and has no form to judge. A production handed to the
tool bounces, as said above; it is not a refusal.

## The demonstration

- `procs/ASK.md` — one `WORK` alone: said to the principal, then the passage is over.
- `procs/HANDOFF.md` — a `WORK` then an `INFER`: the `WORK` comes first, the call with the
  key alone moves on to the summary.

## The test

`tests/patterns/steps/work.py` plays `ASK.md` and checks its line, its context and its
closing; plays `HANDOFF.md`, hands the tool a production on the `WORK` and checks the
bounce, then the move to the `INFER`; and plays `HANDOFF.md` again under the principal's
conduction: the same steps, no closing line, the passage over at the principal's call.
