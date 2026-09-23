---
name: OPERATIONS
kind: proc
description: >-
  Consign the session's operations -- the durable, dated, one-line-per-operation record of what was done in this workspace.
output: line
tools: |
  pp-continuity
proc: |
  WORK
attach: turn.end
when: "@SETTINGS.continuity_memory_frequency"
---

# OPERATIONS — record the work

An operation is a fact worth keeping for a later session: progress, a regression
or a decision grounded in the work. Each entry stands alone for a reader who was
absent.

This step authorizes recording what happened since the last consignation,
including this exchange. Read the record if needed to find that boundary.
Write one concise fact per `pp-continuity register` call; the script dates it.
Consign while the skill is offered, then report what was recorded. If nothing
qualifies, say so and leave the record as it stands.
