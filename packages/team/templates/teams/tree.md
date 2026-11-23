---
# A team preset of the team package: `team declare <name> --template teams/tree` writes `teams/<name>/TEAM.md` naming
# it (`template: teams/tree`) with its members. Every `team start` reads this preset again and plays its `form:`: the
# first member is the root, the `squads` members after it (the value `squads`) are the squad leads, reporting to the
# root, and every member after them is a worker, given to the squad leads in turn. `{root}`, `{squads}`, `{workers}`
# and `{tree}` name the team's members in the intention, `{daily}` is `daily-intention` when the daily stands -- two
# squad leads or more. A task takes a wake-up of the root, of each squad lead twice and of each worker: hence its
# launches. TEAM.md may give `squads` and `daily` under `values:`; a `root:`, a `reports:` or a ceremony named `daily`
# written in TEAM.md replace what the form makes. The limits and `schedule:` are the defaults of TEAM.md's own keys.
# The role keys (`roles:`) and the documents (`documents:`) are TEAM.md's own.
description: two levels -- one lead splits each task among its squad leads, each squad lead among its own workers
form: tree
members: |
  lead
  squad-1
  squad-2
  worker-1
  worker-2
  worker-3
  worker-4
values: |
  squads = 2 -- how many squad leads report to the root, a whole number of 1 or more
  daily = every weekday 09:30 -- the daily's rhythm, `every day|weekday|mon..sun HH:MM`; left empty in TEAM.md (`daily =`), no daily
daily-intention: >-
  At the `daily` meeting, each squad lead must say in one line what its squad did since the last
  daily and what it will do next; {root} must sum up these lines in its answer.
budget: 10
launches: 24
timeout: 900
schedule: off
---
{root} is the lead: it receives every task. It must split the task into one part per squad lead ({squads}), give each squad lead its part, and once every squad lead has reported, answer the task with what the squad leads reported.

The squads are: {tree}. Each squad lead must split the part it receives into one smaller part per worker of its squad, give each worker its part, and once every worker has reported, report to {root} what its squad did, summed up in a few lines.

Each worker ({workers}) must do the part it receives and report it to its squad lead in a few lines.

{daily}

Every answer must stay short and say only what the task needs.
