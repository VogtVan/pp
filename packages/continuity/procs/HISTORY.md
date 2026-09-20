---
name: HISTORY
kind: proc
description: >-
  Weekly digest: synthesize the period since the last entry into one durable paragraph, consign it, and give the operator the week at a glance.
output: free
tools: |
  pp-continuity
proc: |
  WORK
---

# HISTORY — the week's synthesis

A digest connects recorded work, decisions and milestones in one paragraph.
This due step authorizes its addition.

Read `pp-continuity history last 1` and `pp-continuity recall last <days>` to
cover the period since the last digest, or the available work for a first one.
Select that period, synthesize it, record it with `pp-continuity history add`,
then give the operator the digest.
