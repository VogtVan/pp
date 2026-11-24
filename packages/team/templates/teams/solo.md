---
# A team preset of the team package: `team declare <name> --template teams/solo` writes `teams/<name>/TEAM.md` naming
# it (`template: teams/solo`) with its members. One member, the root; `{root}` names it in the intention. The limits
# and `schedule:` are the defaults of TEAM.md's own keys. The role keys (`roles:`) and the documents (`documents:`)
# are TEAM.md's own.
description: one member does every task itself
form: one
members: |
  worker
budget: 5
launches: 24
timeout: 900
schedule: off
---
{root} is the only member of this team: it must do every task it receives and answer it with the result in a few lines.
