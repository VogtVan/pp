---
name: ROUTE
kind: proc
output: any
description: the workflow's root -- it calls the stage, whose successor the agent picks
proc: |
  CALL STAGE.md
---

# ROUTE

The root of the workflow: it calls STAGE and resumes when the path is walked.
