---
name: TEAMS-BOARD
kind: proc
description: >-
  The welcome of the teams space -- played once when the space opens: the teams of the house, their members without a description and the templates, said to the principal as tables.
attach: team.teams.initialize
provides: team-board
with: pp-team status --json
payloads: team-board team-templates
formats: |
  team-board  words  the board as titled markdown tables -- the teams (team, name, description, state), the members without a description with the path of their `MEMBER.md`, the templates (template, kind, description); a table with nothing to say left out; nothing the board does not say
output: team-board
proc: |
  INFER
---

# TEAMS-BOARD — the welcome of the teams space

`team-board` is what `pp-team status --json` says of the teams of the house, read from their
declarations and their journals: one object per team, with its `team` (its directory), its
`name`, its `description` (`null` when its `TEAM.md` has none), its `state`, and its
`declared_members`, each with its `path` and its `description` (`no description` when its
`MEMBER.md` says none).
`team-templates` is what `pp-team templates --json` says: one object per template, its kind
`preset` or `document`.

A team without a description and a member without one are both missing a sentence: say them,
the member with the path of its `MEMBER.md`, which is `<path>/.pp/MEMBER.md` under the house. A house without a team says so in one line.

Say the board to the principal as tables, one per part, each with its title.
