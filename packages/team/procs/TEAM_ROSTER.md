---
name: TEAM_ROSTER
kind: proc
description: >-
  The house's teams at a glance: one row per team -- what it does, its root, its members, its state, and the part this agent plays in it -- and one row per recurrence still alive, served at the start of every exchange outside the runs of a team, absent when the house has no team.
mount: turn.begin
provides: team-roster
with: pp-team roster
payloads: team-roster
---

# TEAM_ROSTER — the teams of the house

The `team-roster` section shows the teams of the house this agent belongs to, all of them,
whichever agent you are. The first table has one row per team: its name, what it does (`—`
when its owner wrote no description), its root -- the member the team's tasks go to first --,
how many members it has, whether it is at work, and the part you play in it: `root (<member>)`
when you play its root, `member (<member>, …)` when you play other members of it, `—` when you
play none. The second table has one row per recurrence that is still alive: its team, its id,
what it does, when it comes back, when it comes next, and whether it is paused. A recurrence
opens a new task in its team at each of its periods. The section is absent when the house has
no team, and in the runs a team opens: a member at work there reads its own team's documents.
To read a team in full, use the skill `pp-team`.
