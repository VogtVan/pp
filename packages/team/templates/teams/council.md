---
# A team preset of the team package: `team declare <name> --template teams/council` writes `teams/<name>/TEAM.md`
# naming it (`template: teams/council`) with its members. Every `team start` reads this preset again and plays its
# `form:`: the first member is the root, every other member reports to it; a `root:` or `reports:` written in TEAM.md
# replaces what the form makes. `{root}` and `{others}` name the team's members in the intention, `{quorum}` and
# `{count}` say how many answers are enough for the root, of how many members. The limits and `schedule:` are the
# defaults of TEAM.md's own keys. Its `roles:` are written into TEAM.md once, at the birth: each key with the members
# the form puts in the places its line names (`{root}` the root, `{others}` every other member), for the team as
# declared, whatever their names. After the birth, only TEAM.md's `roles:` count: a team that writes none has no role
# key, and never gets this preset's back. The documents (`documents:`) are TEAM.md's own.
description: one facilitator asks every expert the same question and concludes once most of them have answered
form: star
members: |
  facilitator
  expert-1
  expert-2
  expert-3
roles: |
  experts {others}
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the facilitator: it receives every task. It must give the same question to every expert ({others}) in one `do`. Each answer reaches it as a message: it must answer the task once {quorum} of the {count} experts have answered, and say nothing before: what their answers agree on, and where they differ.

Each expert must answer the question it receives on its own, without asking another expert, in a few lines.

Every answer must stay short and say only what the task needs.
