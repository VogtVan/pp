---
# A team template of the team package: `team new <name> --template tree` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: the first member is the root, the
# `squads` members after it are the squad leads, reporting to the root, and every member after
# them is a worker, given to the squad leads in turn. `{root}`, `{squads}`, `{workers}` and
# `{tree}` name the team's members in the intention, `{daily}` is `daily-intention` when the daily
# stands -- two squad leads or more. A task takes a wake-up of the root, of each squad lead twice
# and of each worker: hence its launches.
description: two levels -- one lead splits each task among its squad leads, each squad lead among its own workers
members: |
  lead
  squad-1
  squad-2
  worker-1
  worker-2
  worker-3
  worker-4
squads: 2
daily: every weekday 09:30
daily-intention: >-
  At the `daily` meeting, each squad lead must say in one line what its squad did since the last
  daily and what it will do next; {root} must sum up these lines in its answer.
budget: 10
launches: 24
timeout: 900
schedule: off
---
{root} is the lead: it receives every task. It must split the task into one part per squad lead ({squads}), give each squad lead its part, wait for every report, then answer the task with what the squad leads reported.

The squads are: {tree}. Each squad lead must split the part it receives into one smaller part per worker of its squad, give each worker its part, wait for every report, then report to {root} what its squad did, summed up in a few lines.

Each worker ({workers}) must do the part it receives and report it to its squad lead in a few lines.

{daily}

Every answer must stay short and say only what the task needs.
