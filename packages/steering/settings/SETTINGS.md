---
name: SETTINGS
kind: fragment
package: steering
description: >-
  The steering package's own settings -- the budgets a thread's record holds to.
  Composed into the instance's SETTINGS under the `steering_` prefix, read by its
  skill.
steering_step_budget: 100
steering_name_max: 60
steering_dormant_days: 7
steering_note_budget: 80
steering_next_max: 3
steering_line_max: 7
steering_front_min: 5
types: |
  steering_step_budget  free
  steering_name_max  free
  steering_dormant_days  free
  steering_note_budget  free
  steering_next_max  free
  steering_line_max  free
  steering_front_min  free
---

## Steering — the budgets of a thread

The package's keys wear the `steering_` prefix; `pp-steering` reads them by name at
the instance's `SETTINGS.md`, and falls back to the values above when a line is
missing. A value that is not a whole number refuses.

- `steering_step_budget` — the characters a step's TEXT holds: the text is a complement
  to the step's name, not the sentence of the work; empty is allowed; a text past the
  budget refuses `budget`, and a crossing's text is cut to it and said. The same budget
  holds a blocking reason.
- `steering_name_max` — the characters a thread name or a step name holds. A name is
  kebab-case, the slugs' own grammar.
- `steering_dormant_days` — the days without work after which a thread FOLDS at the
  front: it leaves the table for the footer line, where its name, its pointed step and
  its age stand, read at its `worked_at` -- past the rows `steering_front_min` keeps.
- `steering_note_budget` — the characters a thread's NOTE holds: its why, then what to
  know now; a note past the budget refuses `budget`.
- `steering_next_max` — the next actions a row of the front names, in the thread's
  order from the pointed step, before `…`.
- `steering_line_max` — the waiting steps the `⏸` line names before `+n`.
- `steering_front_min` — the rows the table keeps before any thread folds to the footer:
  the freshest threads with a step to do stay, dormant or not, so the front is never
  empty while threads stand.
