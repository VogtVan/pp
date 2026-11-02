---
name: STAMPED
kind: proc
description: a proc that stamps at its entry, then reads the stamp back as a payload.
mode: fast
exec: pp-stamp stamp @STAMPED.mode @SETTINGS.max_harness_tool_output plain
payloads: alpha-seen
proc: |
  INFER
---

Say what the stamp wrote.
