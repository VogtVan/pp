---
name: SETTINGS
kind: fragment
package: continuity
description: >-
  The continuity package's own settings -- the records' cadence, the weekly
  digest's anchor and the recall's period. Composed into the instance's
  SETTINGS under the `continuity_` prefix, read by its documents.
continuity_memory_frequency: 3
continuity_history_day: monday
continuity_recall_days: 7
continuity_entry_budget: 500
continuity_digest_budget: 1500
types: |
  continuity_memory_frequency  free
  continuity_history_day  one_of[monday|tuesday|wednesday|thursday|friday|saturday|sunday|never]
  continuity_recall_days  free
  continuity_entry_budget  free
  continuity_digest_budget  free
effort: |
  continuity_memory_frequency  light=5 medium=3 full=1
---

## Continuity — the records, the digest, the recall

The package's keys wear the `continuity_` prefix; its documents read them by
name (the consignation's guard, the digest's anchor, the recall's period). The
effort presets one of them; a preset key's written value stays inert while an
effort is named.

- `continuity_memory_frequency` — how often the operations record is written
  (`operations.jsonl`): `0` never, `1` every exchange, `n` every n
  exchanges — the consignation comes at the turn's TAIL, so the span reaches
  the present (the effort presets it: light 5, medium 3, full 1).
- `continuity_history_day` — the anchored weekday of the weekly digest
  (`monday` … `sunday`): the first boot at or past it synthesizes the week in
  chat and consigns it (`history.jsonl`); `never` turns the digest off.
- `continuity_recall_days` — the period the boot's recall reads back, in
  days: the operations of the last n days come with the boot (`7` by
  default); `0` recalls nothing.
- `continuity_entry_budget` — characters one consigned operation may hold
  (`500` by default): one line is a record, not a report — over it,
  `pp-continuity` refuses and writes nothing; `0` lifts the limit.
- `continuity_digest_budget` — characters one weekly digest may hold
  (`1500` by default): a digest, not a report — over it, `pp-continuity`
  refuses and writes nothing; `0` lifts the limit.
