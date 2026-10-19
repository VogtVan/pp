---
# A team template of the team package: `team new <name> --template triage` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: the first member is the root, every
# other member reports to it. `{root}` and `{others}` name the team's members in the intention.
description: one dispatcher hands each task whole to the one specialist its subject calls for and relays the answer
members: |
  dispatcher
  spec-a
  spec-b
  spec-c
budget: 5
wakes: 8
timeout: 900
schedule: off
---
{root} is the dispatcher: it receives every task. It must not split the task: it must choose ONE specialist among {others} by the subject of the task, give it the whole task, wait for its answer, then answer the task with it. When the specialist says the task is not for it, {root} must give the task to another specialist.

Each specialist must do the task it receives and answer {root} in a few lines. A specialist that is not the right one for the task must say so in one line, without doing the work.

Every answer must stay short and say only what the task needs.
