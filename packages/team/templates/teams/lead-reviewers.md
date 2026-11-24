---
# A team preset of the team package: `team declare <name> --template teams/lead-reviewers` writes
# `teams/<name>/TEAM.md` naming it (`template: teams/lead-reviewers`) with its members. Every `team start` reads this
# preset again and plays its `form:`: the first member is the root, every other member reports to it; a `root:` or
# `reports:` written in TEAM.md replaces what the form makes. `{root}` and `{others}` name the team's members in the
# intention. `{daily}` is `daily-intention` when the daily stands -- two members or more reporting to the root --, its
# rhythm the value `daily`, which TEAM.md may give under `values:`; a ceremony named `daily` written in TEAM.md
# replaces it. The limits and `schedule:` are the defaults of TEAM.md's own keys. Its `roles:` are written into TEAM.md
# once, at the birth: each key with the members the form puts in the places its line names (`{root}` the root,
# `{others}` every other member), for the team as declared, whatever their names. After the birth, only TEAM.md's
# `roles:` count: a team that writes none has no role key, and never gets this preset's back. The documents
# (`documents:`) are TEAM.md's own.
description: one lead does the work and has each reviewer check its draft; the reviewers report to it
form: star
members: |
  lead
  reviewer-1
  reviewer-2
roles: |
  lead {root}
  reviewers {others}
values: |
  daily = every weekday 09:30 -- the daily's rhythm, `every day|weekday|mon..sun HH:MM`; left empty in TEAM.md (`daily =`), no daily
daily-intention: >-
  At the `daily` meeting, each reviewer must say in one line what it checked since the last
  daily and what it still has to check; {root} must sum up these lines in its answer.
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the lead: it receives every task and does the work itself. When its draft is ready, it must send the draft to each reviewer ({others}) with what to check; once every reviewer has answered, it must fix what the reviews found, then answer the task with the final result.

Each reviewer must check the draft it receives and report to {root} in a few lines: what is wrong, what is missing, or that the draft is fine. A reviewer must not redo the work.

{daily}

Every answer must stay short and say only what the task needs.
