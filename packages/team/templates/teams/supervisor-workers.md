---
# A team preset of the team package: `team declare <name> --template teams/supervisor-workers` writes
# `teams/<name>/TEAM.md` naming it (`template: teams/supervisor-workers`) with its members. Every `team start` reads
# this preset again and plays its `form:`: the first member is the root, every other member reports to it; a `root:`
# or `reports:` written in TEAM.md replaces what the form makes. `{root}` and `{others}` name the team's members in
# the intention. `{daily}` is `daily-intention` when the daily stands -- two members or more reporting to the root --,
# its rhythm the value `daily`, which TEAM.md may give under `values:`; a ceremony named `daily` written in TEAM.md
# replaces it. The limits and `schedule:` are the defaults of TEAM.md's own keys. Its `roles:` are written into TEAM.md
# once, at the birth: each key with the members the form puts in the places its line names (`{root}` the root,
# `{others}` every other member), for the team as declared, whatever their names. After the birth, only TEAM.md's
# `roles:` count: a team that writes none has no role key, and never gets this preset's back. The documents
# (`documents:`) are TEAM.md's own.
description: one supervisor splits each task and gives one part to each worker; the workers report to it
form: star
members: |
  supervisor
  worker-1
  worker-2
roles: |
  supervisor {root}
  workers {others}
values: |
  daily = every weekday 09:30 -- the daily's rhythm, `every day|weekday|mon..sun HH:MM`; left empty in TEAM.md (`daily =`), no daily
daily-intention: >-
  At the `daily` meeting, each worker must say in one line what it did since the last daily
  and what it will do next; {root} must sum up these lines in its answer.
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the supervisor: it receives every task. It must split the task into one small part per worker ({others}), give each worker its part, and once every worker has reported, answer the task with what the workers reported.

Each worker must do the part it receives and report it to {root} in a few lines.

{daily}

Every answer must stay short and say only what the task needs.
