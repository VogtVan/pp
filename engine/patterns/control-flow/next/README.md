# next — the document that follows when a procedure leaves

## What you write

In the front matter of a procedure that is CALLed, `next:` names the documents it may leave to:

    next: LEFT.md RIGHT.md
    choose: |
      LEFT when the draft is @SHELF.state, RIGHT otherwise.

- One name: that document follows, nothing to decide.
- Two names or more: add ONE decider.
  - `choose:` — prose the agent reads to elect the successor. A `@Document.field` in it is
    replaced by that field's value.
  - `decide:` — a skill prints the successor's name. In a document of your instance, the first
    word names the skill and the rest are its arguments (`decide: pp-route pick`). In a
    package's document, every word is an argument of the package's own skill, `pp-<package>`.

## What you get

- The procedure plays its steps; when it leaves, its successor enters BESIDE it, in the frame of
  the document that called it — `ROUTE ▸ LEFT`, never `ROUTE ▸ STAGE ▸ LEFT`. The successor may
  have its own `next:`; when the path ends, the caller goes on with its next step.
- Under `choose:`, the agent gets one more step at the exit: the prose as its brief, the names as
  OPTIONS, the elected name piped back like a PICK. A name outside the OPTIONS is a miss: the
  procedure plays again from its first step, the miss named.
- A `PROVE` the procedure writes comes before the choice; nothing is proven after it.
- The laws of the procedure that left are gone with it; the laws of the caller hold all along the
  path.
- When a successor declares `input:` (see `outputs/input`), the last production of the procedure
  before it goes to the tool, judged like any production a step takes; the successor opens on it and sees it under
  `input`.
- A document attached at a socket hands its successor the same place: the successor plays where
  the socket stands.
- The successors are added for the passage only: the next message rewinds the root and they are
  gone. A compaction re-serves the successor in flight.
- The run's trace notes each transition and who decided it (alone, the agent, a skill);
  `./pp -stats` counts them.

## When to use it

- A procedure whose next piece of work depends on what it found: a review that goes to a fix or to
  an approval, a triage that sends each case down its own path.
- A chain of documents written once and reused, each knowing only what comes after it.
- A loop is never a chain of successors: to repeat a step, turn a door (`control-flow/cycle`,
  `control-flow/field`).

## What refuses

- At the build: successors that lead back to a document already on the path (`next-cycle`); two
  names and no decider (`next-undecided`); a decider with no successor, or with one alone
  (`decision-idle`); `choose:` and `decide:` together (`choose-and-decide`); `next:` on a document
  with no steps (`next-unplayable`); a name no document carries, or a `decide:` skill that does not
  exist (`reference-unknown`); a procedure whose `output:` differs from its successor's `input:`
  (`format-mismatch`).
- In the steps: a `NEXT` written by hand (`next-keyword`) — the choice is the engine's step.
- When the run plays: `next:` on the run's root (`next-floor`); a `@Document.field` of `choose:`
  that names nothing (`choose-argument-empty`); a skill that prints a name outside `next:`
  (`next-foreign`) or fails (`next-refused`).

## The demonstration

- `procs/ROUTE.md` — the root: `CALL STAGE.md`, then an `INFER`.
- `procs/STAGE.md` — the fork: a line, its `PROVE`, then `next: LEFT.md RIGHT.md` under `choose:`.
- `procs/SHELF.md` — the value the choice reads, `@SHELF.state`.
- `procs/LEFT.md` — takes STAGE's line (`input: line`) and leaves to its one successor, TAIL.
- `procs/RIGHT.md`, `procs/TAIL.md` — the ends of the paths.
- `procs/DECIDE.md` — the same fork decided by a skill, `decide: pp-route pick`.
- `procs/HOLLOW.md` — a `choose:` whose reference names nothing.
- `procs/CIRCLE.md` and `procs/BACK.md`, `procs/UNDECIDED.md`, `procs/IDLE.md`, `procs/LONE.md`,
  `procs/BOTH.md`, `procs/STRAY.md`, `procs/WIDE.md`, `procs/WRITTEN.md` — one refusal each.

## The test

`tests/patterns/control-flow/next.py` plays ROUTE: STAGE proves, then asks its choice; LEFT enters
beside it, leaves to TAIL, and ROUTE resumes — with a law on ROUTE and one on STAGE, only ROUTE's
rides the path. It plays DECIDE with a skill of the instance and with the same document in a
package, a name outside `next:` and a failing skill; a missed election; a compaction mid-way and
the next message; a successor at a socket; the transitions counted; the weight of the choice beside
a written PICK; a CALL without `next:`; the two refusals of the run; then each refusing document
alone at the build; and the inferred path again under the principal's conduction.
