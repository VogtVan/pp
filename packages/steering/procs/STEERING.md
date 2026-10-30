---
name: STEERING
kind: proc
description: >-
  The steering space -- open it (`-open STEERING`) to see the board of the steps, look at them through any view, and change several of them at once; `-close` gives the turn back.
tools: |
  pp-steering
proc: |
  WORK
constraints.behavior: |
  ST1  drop a step only when its work no longer has to be done, and give the reason
  ST2  recall an archived step only when its work is due again
  ST3  say every change in one line, the step by its name
  ST4  never dissolve a label the principal named without the principal's word
  ST5  a view you build yourself names the pp-steering calls it comes from -- `list --json`, `labels`, `board` -- and keeps the id of each step
  ST6  a change to several steps is first shown as one table -- step, verb, reason -- then made with one apply, on the principal's word
---

# STEERING — the steps, all of them

This space is where the principal looks at the steps as a whole and puts them in order.

**What the principal sees when it opens.** The board, said as tables: the steps by status,
the last 7 days (born, done, dropped, archived, recalled), how long steps take to close and
how old the steps still to do are, the five least recently touched, and each label with its
freshest steps. Steps left untouched too long are archived just before.

**What the principal can ask for next.** Any view, with `pp-steering`:

- the labels and their counts: `labels`;
- the steps of one label, of one status, older or younger than some days, born before or
  after a date, grouped by label, by age or by status: `list` and its filters, `--by`;
- the archived steps: `list --archived`, with the same filters;
- one step whole: `show`; the least recently touched first: `review`.

When the principal asks for a view the fields cannot give -- "the steps about the engine" --
read `list --json` and choose the steps by their text yourself.

**How the steps change here.** Any view can lead to a change: close what is done (`done`),
drop what no longer has to be done (`drop`), put steps under a label (`label`, `note`,
`order`, `dissolve`), bring an archived step back (`recall`). For several steps at once,
show them first in one table, then make the change with one `apply`.

**How it ends.** When the principal is done, `-close` gives the turn back.
