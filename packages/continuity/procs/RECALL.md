---
name: RECALL
kind: proc
description: >-
  Boot recall: operations from the last continuity_recall_days days arrive with the boot block as session ground, read and held, never restated.
mount: boot.ready
provides: continuity-recall
with: pp-continuity recall
payloads: continuity-recall
---

# RECALL — the workspace's earlier work

Continuity keeps the workspace's operations across sessions. `continuity-recall`
supplies recent entries in recording order.

Use them to ground the work and avoid repeating it. This recall calls for no chat
report; cite a recorded fact when the answer needs it. An absent section means
this recall supplied no entries.
