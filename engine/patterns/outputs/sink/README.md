# sink — hand a production to a skill

## What you write

On the document that produces, `sink: <skill>`: a skill of your instance that takes the
production.

    sink: pp-tally

One sink per document. The skill is a script: it reads the production on its standard
input and prints what it has to say.

## What you get

- The document's `WORK` and `INFER` productions go to the tool, never to the principal: each
  one, once accepted, is handed to the skill on its standard input.
- What the skill prints comes back as a section of the next block, under `sink <skill>`, and
  the run's record of what it served notes it as `sink`; the run's trace counts each play.
- The lines the skill prints as directives — `::push <signal> <vector> <text>`, `::clear
  <signal> <vector>` — are taken by the instance's bus, not shown; a signal is held only when
  a package declares it (see `automation/checks-and-signals`).
- A skill that fails is said back in the section, with its words; the run goes on.

## When to use it

- A production that must land in a record: a script writes it where it belongs (see
  `packaging/writer-skill`), and knows the run it serves (see `packaging/run-context`).
- A production a script turns into a signal for later exchanges.

## What refuses

- A directive written out of form (`::push` without its three parts, `::clear` without its
  two) refuses `push-malformed`.
- A `sink:` naming a skill nobody carries refuses `reference-unknown` when the instance
  builds.

## The demonstration

- `procs/TALLIED.md` — a production handed to `pp-tally`.
- `procs/SOUR.md` — a production handed to `pp-sour`, a skill that fails.
- `procs/LOUD.md` — a production handed to `pp-loud`, which prints a directive out of form.

## The test

`tests/patterns/outputs/sink.py` writes the three skills, then plays the demonstration:
TALLIED's step to the tool, pp-tally's words back under `sink pp-tally`, the run's ledger and
trace; SOUR's refusal said back, the run parked; LOUD refusing `push-malformed`.
