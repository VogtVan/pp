---
# A team preset of the team package: `team declare <name> --template teams/triage` writes `teams/<name>/TEAM.md`
# naming it (`template: teams/triage`) with its members. Every `team start` reads this preset again and plays its
# `form:`: the first member is the root, every other member reports to it; a `root:` or `reports:` written in TEAM.md
# replaces what the form makes. `{root}` and `{others}` name the team's members in the intention. The limits and
# `schedule:` are the defaults of TEAM.md's own keys. Its `roles:` are written into TEAM.md once, at the birth: each
# key with the members the form puts in the places its line names (`{root}` the root, `{others}` every other member),
# for the team as declared, whatever their names. After the birth, only TEAM.md's `roles:` count: a team that writes
# none has no role key, and never gets this preset's back. The documents (`documents:`) are TEAM.md's own.
description: one dispatcher hands each task whole to the one specialist its subject calls for and relays the answer
form: star
members: |
  dispatcher
  spec-a
  spec-b
  spec-c
roles: |
  specialists {others}
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the dispatcher: it receives every task. It must not split the task: it must choose ONE specialist among {others} by the subject of the task, give it the whole task, and once the specialist has answered, answer the task with it. When the specialist says the task is not for it, {root} must give the task to another specialist.

Each specialist must do the task it receives and answer {root} in a few lines. A specialist that is not the right one for the task must say so in one line, without doing the work.

Every answer must stay short and say only what the task needs.
