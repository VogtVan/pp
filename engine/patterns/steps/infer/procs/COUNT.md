---
name: COUNT
kind: proc
description: list the open items, then hand them to the report.
output: json
proc: |
  INFER
  CALL REPORT.md
---

List the open items as a JSON array of short names.
