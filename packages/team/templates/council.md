---
# A team template of the team package: `team new <name> --template council` writes
# `teams/<name>/TEAM.md` from it. The FORM is the script's: the first member is the root, every
# other member reports to it. `{root}` and `{others}` name the team's members in the intention,
# `{quorum}` and `{count}` say how many answers the root waits for, of how many members.
description: one facilitator asks every expert the same question and concludes once most of them have answered
members: |
  facilitator
  expert-1
  expert-2
  expert-3
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the facilitator: it receives every task. It must give the same question to every expert ({others}) in one `do`, with `"await": {"any": {quorum}}` beside it, then answer the task once {quorum} of the {count} experts have answered: what their answers agree on, and where they differ.

Each expert must answer the question it receives on its own, without asking another expert, in a few lines.

Every answer must stay short and say only what the task needs.
