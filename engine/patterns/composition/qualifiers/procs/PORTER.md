---
name: PORTER
kind: proc
description: called at the gatehouse only when the switch is open.
attach: gatehouse.open
when: "@SWITCH.open"
proc: |
  INFER
---

Name who is waiting at the gate.
