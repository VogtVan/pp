---
# A team template of the team package: `team new <name> --template chain` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: each member reports to the one
# before it, the first is the root. `{root}`, `{chain}` and `{last}` name the team's members.
description: a chain of steps; each member does its step, hands the next step to the next member and passes its result back up
members: |
  step-1
  step-2
  step-3
budget: 5
launches: 24
timeout: 900
schedule: off
---
This team works as a chain: {chain}. {root} receives every task.

Each member that has a next member in the chain must do its own step of the task, give the next member what it needs for the following step, wait for its report, then answer the one who asked with its own step and that report, summed up in a few lines.

{last} is the end of the chain: it must do the step it receives and report it in a few lines.

Every answer must stay short and say only what the task needs.
