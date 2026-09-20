---
name: BATCH
kind: proc
description: >-
  Conducts a batch's work on the operator's GO: the framing that sizes the
  work and sets its own constraints, the implementation the GO green-lights,
  the rework that appends to the same history -- one generic step, the gates
  in the settings and the GO.
output: free
tools: |
  pp-plan
constraints.production: |
  BA3  a comment speaks the DOMAIN in the present tense: concise, the current implementation, zero meta -- the records hold plans, history and decisions.
constraints.behavior: |
  BA1  a defect met mid-batch is SAID and treated in its own frame -- the batch keeps to the work it opened on.
  BA2  every upstream dependency is VERIFIED before acting -- presumed done, proven on sight; a gap is ALERTED and the batch stops there.
  BA4  the batch's laws are posed LAST at the framing -- after the zoom-out, the zoom-in, the expected, the tests and the todos, from what the framing read; a law written before is a guess.
  BA5  the serve rows FOLLOW the work: posed at the framing (the TOUCHED code, then the DEPENDENT code), kept as pieces enter or leave during the implementation, re-aligned at the landing -- a row is never a later pass.
  BA6  a verification of the batch plays on a DISPOSABLE path -- a mktemp directory, a copy -- never on the operator's world: no file under the home, no live instance, no record touched to check a behavior; what a live run alone proves is the operator's gate (PH3), said and left to them.
proc: |
  WORK
---

# BATCH — a batch's work

A batch is the LARGEST unit one turn can open, apply, verify and close —
sized at the framing, closed in the turn that opens it; it is the only unit
of work of a plan. Its structure and statuses stay the `pp-plan` script's
hand; the method alone lives here. The batch document holds its SECTIONS,
written by `pp-plan section` and never by hand: the CONTEXT (its brief, from
the phase's Items line at birth), the GROUND, the TARGET, the EXPECTED, the
TESTS, the ARBITRATIONS, the ITEMS — the todos — the DECISIONS and the
DELIVERY log.

## The framing — the operating mode, in order

0. **The gate.** The framing plays on the GO that names the batch; the
   implementation waits a GO of its own — a GO that opened the plan or the
   phase is not one.
1. **Zoom out — Ground.** Read the ground around the pieces: the code that calls them,
   the code they call, their DEPENDENTS — every piece a change here would
   break enters the perimeter. A REFACTOR lists them: the alignment of each
   dependent is a todo of this batch, presented to the operator, never left
   to a later pass.
2. **The readings, whole.** Write the batch's serve rows — CODE in SECTIONS:
   the first row the TOUCHED code, the second the DEPENDENT code, more when
   the ground asks — the ORDER is the convention, no grammar beyond it. Any
   text file serves WHOLE, code included; a line range is a CONVENIENCE that
   scopes, never a requirement — the soft serve's signal keeps the rows
   honest, no hand maintains them. The rows scope the code the batch
   touches: they are born here and LIVE with the batch — kept as the work
   moves, re-aligned at the landing.
3. **Zoom in — Target.** Look at the pieces to touch: FROM SCRATCH, a new piece — its
   shape, its place, its contract with what stands; REFACTOR, what breaks and
   what moves — the new form alone, no half-measure, no transitional wrapper.
4. **Expected and Tests.** Write what is TRUE when the batch closes —
   the observable exit criteria — and what proves it: the bench scenarios to
   run or to write, the renderings to cite, the operator's gate when a live
   run is the only proof.
5. **The todos — Items.** Write the work down as the lines of Items
   (`pp-plan section <address> Items`, one line `- <slug> -- <text>` each —
   the entries derive from them), each NAMED by its own meaningful
   slug — the name is what every status line will speak — and each precise
   enough to act on.
6. **Arbitrations.** Every architecture or choice the implementation will
   meet, written down with the framing: the options, the recommendation, what
   returns to the operator's GO.
7. **The laws, last.** A batch ALWAYS carries its OWN constraints — they are
   its PROOF MODE, the laws the checkpoint judges, what replaces the legacy
   proof rituals: the objectives THIS work must hold, derived from everything
   above and written to the BATCH document's front matter — a batch framed
   without its laws is a framing defect, a law written before the ground is
   read is a guess. A law you WRITE says its SECTION: `constraints.production`
   for what the agent MAKES — proven at every checkpoint — and
   `constraints.behavior` for what it does, says or reads — served at every
   block, never proven. The script preserves the keys it does not own, and
   the operator's GO makes them the OPERATOR's; their codes are namespaced
   per batch. A plan document is a BLUEPRINT, not a history manual: write
   the state TRUE at the moment you write it, and of the history keep the
   reasons and the justifications alone, one dated line.
8. **Restitute, and stop.** The framing is a deliverable: the batch is `doing`
   since its Expected, the framing is restituted — the todos, the expected, the tests,
   the arbitrations — and the agent waits the GO that names the batch.

## The implementation, on the GO

The GO names the step it approves — a framing arbitrates, an
implementation green-lights; anything else is served, never coded. VERIFY
the upstream the batch depends on before touching anything. SAY in a few
lines what is about to be implemented — the logic, the model, how it fits
what stands, what it brings and what it removes — as the involvement
settings ask. Implement under every law on screen — an arbitration the
framing wrote returns to the GO as the involvement settings say, and a NEW
one met mid-work is never decided in silence — and CHECK OFF each todo as
it arrives (`pp-plan done <address>/<todo>`) — never in a final pass; a piece
touched that no row named gets its row as it is touched. Prove by
RENDERING — bench, dry-run, grep, diff — against the expected and the
tests written at the framing, on a DISPOSABLE path (a mktemp directory, a
copy — never the operator's world: a tool's default file under the home is
not a bench), and write the log by `section … Delivery`; the writing
re-aligns the serve rows on what really moved — the update is part of
closing the batch, never a later pass — and the Delivery, its todos all done,
closes the batch, the phase when it was the last batch, the plan with the
phase, each closing said by the script; no word closes. What cannot close
honestly is said: the batch stops, it never stretches. A REWORK appends to the
same history: a framing section rewritten reopens the batch (`redo`, the
ancestry rises), it keeps its document, its new todos join Items under their
own slugs, its log grows — one component, one memory.
