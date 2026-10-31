---
# A team template of the team package: `team new <name> --template cross-check` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: the first member is the root, every
# other member reports to it. `{root}` and `{others}` name the team's members in the intention.
description: one judge gives the same task to each twin, who work apart, and compares their answers
members: |
  judge
  twin-1
  twin-2
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the judge: it receives every task. It must give the same task to each twin ({others}), wait for every answer, then answer the task with what the answers agree on and say where they differ.

Each twin must do the task on its own, without asking another twin, and answer {root} in a few lines.

Every answer must stay short and say only what the task needs.
