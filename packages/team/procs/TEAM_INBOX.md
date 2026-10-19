---
name: TEAM_INBOX
kind: proc
description: >-
  The owner's inbox: one line per team where something waits for the owner -- a question without its answer, a notice of the team, a task resolved, a post returned -- served at the start of every exchange of the house, absent when nothing waits.
mount: turn.begin
provides: team-inbox
with: pp-team inbox
payloads: team-inbox
---

# TEAM_INBOX — what the teams wait for

The `team-inbox` section shows one line for each team where something waits for the owner,
the one who started the teams: the questions an agent of the team asked them that nobody
has answered yet; the notices the team sent them -- a limit of the team reached, or a task
whose holder failed or does not answer, which waits for their answer --; and the tasks
finished and the messages that came back to them undelivered since they last marked their
inbox as seen. When nothing waits in any team, the section is absent. To answer a question
or a notice, read a result or mark the inbox as seen, use the skill `pp-team`.
