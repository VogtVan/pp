---
name: batch
description: a batch of a phase -- framed, implemented on its GO, delivered
leaf: yes
sections: |
  Ground
  Expected
  Tests
  Choices
  Items
  Delivery
statuses: |
  doing  Choices
  redo  Ground Expected Tests Choices Items
constraints.production: |
  BA3  a comment speaks the DOMAIN in the present tense: concise, the current implementation, zero meta -- the records hold plans, history and decisions.
constraints.behavior: |
  BA1  a defect met mid-batch is SAID and treated in its own frame -- the batch keeps to the work it opened on.
  BA2  every upstream dependency is VERIFIED before acting -- presumed done, proven on sight; a gap is ALERTED and the batch stops there.
  BA4  the batch's laws are posed LAST at the framing -- after the zoom-out, the zoom-in, the expected, the tests and the todos, from what the framing read; a law written before is a guess.
  BA5  the serve rows FOLLOW the work: posed at the framing (the TOUCHED code, then the DEPENDENT code), kept as pieces enter or leave during the implementation, re-aligned at the landing -- a row is never a later pass.
  BA6  a verification of the batch plays on a DISPOSABLE path -- a mktemp directory, a copy -- never on the principal's world: no file under the home, no live instance, no record touched to check a behavior; what a live run alone proves is the principal's gate (PH3), said and left to them.
---

# BATCH `{slug}` — phase `{parent}`, plan `{plan}`

A batch is the only unit of work of a plan: the largest piece one turn can open, do, prove and close. It is framed on one GO and implemented on another. The script `pp-plan` writes every section and every status.

## The framing, on the GO that names the batch

The framing waits a GO that names the batch; the implementation waits a GO of its own. A GO that opened the plan or the phase is neither.

1. **Ground** — it gives the batch its birth. Read around the pieces you touch: the code that calls them, the code they call, the upstream they need, verified on sight. In a last paragraph, list what DEPENDS on them. The alignment of each dependent a change would break is a todo of this batch, shown to the principal, never left for later. *e.g. `storage.py` `list()` lines 30-41 at `a1b2c3d`; depends on it: `cli.py` line 12.*
2. **The readings** — the batch's `serve` rows: the first row the code you touch, the second the code that depends on it, more when the Ground asks. Serve a small file whole; a large one by the tags of what you need, `file[def a..def b]` (`serve` refuses `serve-heavy` above the plan's budget). The rows live with the batch: keep them true as the work moves.
3. **Expected** — first what is true when the batch closes, each line with what shows it; then what stays outside. Say what the pieces become: a new piece with its shape and its contract with what stands, or the change and what moves, in its new form alone, with no wrapper kept for the old one. *e.g. `search("x")` returns the notes that hold x, the test's output cited; the CLI wiring is the next batch.*
4. **Tests** — what proves the Expected: the tests the change touches, to run or to write, and the output to cite. Write a new test first: it fails before the change and passes after it. When a live run alone can prove it, that run is the principal's: say so. *e.g. `tests/test_storage.py::test_search`, written first, red then green, on a mktemp store, never the principal's own file.*
5. **Choices** — every choice the implementation will meet: the choice, its reason, its strongest objection, and whether it waits the principal's GO. Writing Choices makes the batch `doing`. *e.g. a search that ignores case, because a note is read by a person; objection: `Memo` and `memo` mean two things in code.*
6. **Items** — the todos, one line each, `- <slug> -- <text>`: each slug a name the status lines can speak, each text precise enough to act on. *e.g. `- search-function -- search(word) in storage.py, a linear scan`*
7. **The laws**, last (below).
8. **Give the framing to the principal, and stop**: the todos, the Expected, the Tests, the Choices. Wait the GO that names the batch.

## The laws of the batch

A batch always has laws of its own: they are what its proof judges. A batch framed without them is a framing defect. Write them last, from everything above; a law written before the Ground is read is a guess.

- A law says what must hold while THIS work is done, and how that is seen. It never says what the work is: Expected says that. A law carries no figure: a figure goes to Expected.
- Give each law its section: `constraints.production` for what you make, judged at every proof; `constraints.behavior` for how you work, shown at every block and never proven.
- The script keeps the front matter keys it does not own; the principal's GO makes them the principal's.

## The implementation, on its GO

- Verify the upstream the batch needs before you touch anything. A gap stops the batch: say it.
- Say in a few lines what you will do: the logic, how it fits what stands, what it adds and what it removes, as the involvement settings ask.
- Work under every law on screen. A choice the framing wrote returns to the GO as the settings say; a new choice met on the way is said, never made in silence. A defect outside the batch is said and kept for its own frame.
- Deliver each todo as it lands, never in a final pass: `section <address> Delivery --item <todo>`, what landed and its proof.
- A piece you touch that no row names gets its row when you touch it.
- Prove by output — a bench, a dry run, a grep, a diff — against the Expected and the Tests, on a throwaway path (a mktemp directory, a copy). Never in the principal's world: a tool's default file under the home is no bench.
- Run the tests the change touches, once. A flaky test is hunted as soon as it shows: run it alone until you understand it.
- Re-align the rows on what really moved before the last todo is delivered. That last delivery closes the batch, and the phase and the plan when it was their last; the script says each closing. No word closes a batch.
- What cannot close honestly is said: the batch stops, it never stretches.

## A rework

New work on what this batch established comes back here: rewrite one of its framing sections (a new todo in Items, a new Expected) and the batch reopens (`redo`, its ancestors with it). Its new todos join Items under their own slugs and its Delivery grows: one component, one document. Of the past, keep the reasons alone, one dated line in Choices.
