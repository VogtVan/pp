---
# A team template of the team package: `team new <name> --template lead-reviewers` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: the first member is the root, every
# other member reports to it. `{root}` and `{others}` name the team's members in the intention,
# `{daily}` is `daily-intention` when the daily stands -- two members or more reporting to the root.
description: one lead does the work and has each reviewer check its draft; the reviewers report to it
members: |
  lead
  reviewer-1
  reviewer-2
daily: every weekday 09:30
daily-intention: >-
  At the `daily` meeting, each reviewer must say in one line what it checked since the last
  daily and what it still has to check; {root} must sum up these lines in its answer.
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the lead: it receives every task and does the work itself. When its draft is ready, it must send the draft to each reviewer ({others}) with what to check, wait for every review, fix what the reviews found, then answer the task with the final result.

Each reviewer must check the draft it receives and report to {root} in a few lines: what is wrong, what is missing, or that the draft is fine. A reviewer must not redo the work.

{daily}

Every answer must stay short and say only what the task needs.
