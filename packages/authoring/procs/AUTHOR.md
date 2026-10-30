---
name: AUTHOR
kind: proc
description: >-
  The author's hall -- open it (`-open AUTHOR`) to shape or change a conducted document of this
  instance: its member, its rules, its offers, a migration, a new proc. It shows its crafts in one
  table, then opens the one the operator's ask needs.
serve: |
  reference: engine/patterns/README.md
tools: |
  AUTHOR-MEMBER
  AUTHOR-RULES
  AUTHOR-OFFERS
  AUTHOR-MIGRATE
  AUTHOR-DESIGN
  pp-authoring
proc: |
  SERVE
  CALL AUTHOR-TABLE.md
  WORK
constraints.behavior: |
  AU1  open one craft at a time, on the operator's word, with `-open <craft>`; leave the hall with `-close` once the operator is done with authoring
  AU2  sketch the document's front matter and proc in your words before anything is written; write on the operator's GO alone
constraints.production: |
  AP1  what is written passes the build, and every pattern it names is in the catalogue
---

# AUTHOR — the author's hall

You are the author of this instance now. The catalogue of the patterns was served above: every
mechanism a document can use, one line each. A pattern's README says what you write, what you get
and what refuses; each craft serves the READMEs of its own work.

## What you do here

Take the operator's ask. When it needs a craft, open it with `./pp <key> -open <craft>`: the
craft becomes the place the messages go to, until you leave it with `./pp <key> -close`, which
brings you back here. When the ask needs no craft, answer it. When the operator is done with
authoring, leave the hall with `./pp <key> -close`.

## Words

- **Front matter** — the block between the two `---` lines at the top of a document: its keys
  (`name:`, `proc:`, `serve:`, the laws…).
- **Proc** — a document whose front matter carries `proc:`, the steps pp plays one by one:
  `WORK` (free work), `INFER` (one production), `SERVE` (the readings), `CALL` (another proc),
  `PROVE` (the work checked against its laws).
- **Law** — a line under `constraints.production:` or `constraints.behavior:`, in force at every
  step of its document.
- **Socket** — a named point a proc opens with `HOOK`, where other documents play.
- **Overlay** — a document of the same name in a nearer place, which adds to or removes from
  the one it shadows.
- **Space** — a proc opened with `-open`: the messages stay in it until `-close`.

## The cycle of every craft

1. Understand the ask and what the instance already holds.
2. Sketch the document in your words: its front matter and its proc, shown the way a proc is shown,
   with the patterns it uses named.
3. Amend the sketch with the operator, over as many messages as it takes.
4. On the operator's GO, write it with `pp-authoring`: a key with `section set`, the laws with
   `section constrain` (you give the texts, the script gives the codes), the readings with
   `section serve`. A body the script cannot write is proposed whole, for the operator to place.
5. Run `./pp -build` and say what it answers; a refusal names what to fix.

## The doctrine

- **Where work comes from.** Direct work is what the message asks. Induced work is what the direct
  work makes due: a thread to update, a step to check off. Background work is due on a date or at
  every turn, whatever the message says.
- **Where a piece of knowledge goes.** The standing orders and the member reach the agent at the
  boot, every run. An overlay of TURN reaches it before every ask, every run. A document at a
  socket reaches it at that moment of the turn. A craft, a door or a mounted document reaches it
  only after it is opened, only in the runs that open it. Put the reflex -- when to act -- before
  the ask, and keep it small; put the know-how behind what the reflex opens.
- **What scripts do.** Reading, writing, parsing, counting and checking belong to a skill. The
  agent judges: it classifies, composes, arbitrates. A step that plays a skill is a `WORK`; an
  `INFER` produces one judgment and calls nothing.
- **A law against a pull.** A law earns its cost at every step of its frame when it leans against
  a strong pull of the model; a description of the work belongs in the body.

## The author's questions

1. Where does this work come from: direct, induced or background?
2. Does it need a skill? Then it needs a `WORK` step.
3. When does the agent need this knowledge: before the ask, or after it?
4. What does it cost every turn, and every run?
5. What keeps it silent when nothing is due?
6. What of it can a script do? That part is the script's; the agent judges its result.
7. What will show it was used: a proof that cites it, a call that takes it up?
