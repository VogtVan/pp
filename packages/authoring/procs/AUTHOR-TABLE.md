---
name: AUTHOR-TABLE
kind: proc
description: The hall's table -- one line per craft of the author's space.
output: table
proc: |
  INFER
constraints.behavior: |
  AT1  render one table of the crafts, columns: craft | what it does for the operator | the procs and patterns it uses
  AT2  say nothing else
---

# AUTHOR-TABLE — the crafts of the hall

The crafts the hall opens, each with what it does and what it uses:

- `AUTHOR-MEMBER` — shapes the member: who the agent is in this workspace, its role, its readings
  and its own laws, written to `MEMBER.md`. Uses `composition/initialize`, `context/serve`.
- `AUTHOR-RULES` — finds a rule its words and its holder: the member, a plan node, a proc, an
  overlay. Uses `rules/laws`, `rules/prove`, `rules/repair`, `composition/overlay`.
- `AUTHOR-OFFERS` — offers the skills the harness carries, each at its scope. Uses
  `composition/door`, `composition/adoption`, `composition/overlay`.
- `AUTHOR-MIGRATE` — brings an existing set of instructions into pp, piece by piece. Uses the
  catalogue and the other crafts.
- `AUTHOR-DESIGN` — designs a new conducted document for the operator's ask. Uses the catalogue.
