---
# A team preset of the team package: `team declare <name> --template teams/cross-check` writes `teams/<name>/TEAM.md`
# naming it (`template: teams/cross-check`) with its members. Every `team start` reads this preset again and plays its
# `form:`: the first member is the root, every other member reports to it; a `root:` or `reports:` written in TEAM.md
# replaces what the form makes. `{root}` and `{others}` name the team's members in the intention. The limits and
# `schedule:` are the defaults of TEAM.md's own keys. Its `roles:` are written into TEAM.md once, at the birth: each
# key with the members the form puts in the places its line names (`{root}` the root, `{others}` every other member),
# for the team as declared, whatever their names. After the birth, only TEAM.md's `roles:` count: a team that writes
# none has no role key, and never gets this preset's back. The documents (`documents:`) are TEAM.md's own.
description: one judge gives the same task to each twin, who work apart, and compares their answers
form: star
members: |
  judge
  twin-1
  twin-2
roles: |
  twins {others}
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the judge: it receives every task. It must give the same task to each twin ({others}), and once every twin has answered, answer the task with what the answers agree on and say where they differ.

Each twin must do the task on its own, without asking another twin, and answer {root} in a few lines.

Every answer must stay short and say only what the task needs.
