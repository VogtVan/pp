---
# A team template of the team package: `team new <name> --template supervisor-workers` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: the first member is the root, every
# other member reports to it. `{root}` and `{others}` name the team's members in the intention,
# `{daily}` is `daily-intention` when the daily stands -- two members or more reporting to the root.
description: one supervisor splits each task and gives one part to each worker; the workers report to it
members: |
  supervisor
  worker-1
  worker-2
daily: every weekday 09:30
daily-intention: >-
  At the `daily` meeting, each worker must say in one line what it did since the last daily
  and what it will do next; {root} must sum up these lines in its answer.
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the supervisor: it receives every task. It must split the task into one small part per worker ({others}), give each worker its part, wait for every report, then answer the task with what the workers reported.

Each worker must do the part it receives and report it to {root} in a few lines.

{daily}

Every answer must stay short and say only what the task needs.
