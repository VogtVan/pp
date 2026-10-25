---
name: SETTINGS
kind: fragment
package: steering
description: >-
  The steering package's own settings -- the budgets of a step and how long it stays
  active. Composed into the instance's SETTINGS under the `steering_` prefix, read by
  its skill.
steering_step_budget: 100
steering_name_max: 60
steering_note_budget: 80
steering_life_days: 15
steering_active_max: 60
types: |
  steering_step_budget  free
  steering_name_max  free
  steering_note_budget  free
  steering_life_days  free
  steering_active_max  free
---

## Steering — the steps of work

The package's keys wear the `steering_` prefix; `pp-steering` reads them by name at
the instance's `SETTINGS.md`, and falls back to the values above when a line is
missing. A value that is not a whole number refuses.

- `steering_step_budget` — the characters a step's work, its comment or a reason holds,
  on one line; longer refuses `budget`.
- `steering_name_max` — the characters a step name or a label holds. A name is lowercase
  words joined by hyphens.
- `steering_note_budget` — the characters a label's note holds; longer refuses `budget`.
- `steering_life_days` — the days a step stays active without being touched (a comment,
  a status) or recalled: past them, `sweep` archives it.
- `steering_active_max` — the steps still to do (`open`, `waiting`) that stay active at
  most: past them, `sweep` archives the least recently touched.
