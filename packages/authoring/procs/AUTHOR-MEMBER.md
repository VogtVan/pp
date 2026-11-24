---
name: AUTHOR-MEMBER
kind: proc
description: >-
  The member craft -- shape who the agent is in this workspace: its role, its character, the
  readings its role needs and its own laws, in MEMBER.md.
serve: |
  reference: engine/patterns/composition/initialize/README.md engine/patterns/context/serve/README.md
tools: |
  pp-authoring
proc: |
  SERVE
  WORK
  PROVE
constraints.production: |
  AM1  the member's front matter is written by pp-authoring alone; its body is proposed whole for the operator to place
  AM2  the member's description: is ONE sentence, in the third person, that says the same role and specialty as its body
---

# AUTHOR-MEMBER — the member takes shape

ONE member tends a workspace: the same agent across sessions; the parts of a repository are not
members. Work through the hall's cycle, with these steps of your own:

1. **Read the whole workspace first** -- its tree, every README, `docs/` and `design/`, the build
   files. Say what the repository is for, and whether it makes one thing (a PROJECT) or holds
   several parts under one roof (a SOLUTION).
2. **Ask one round** -- only what the operator alone knows: the member's name, its character, the
   languages it works in, its tone.
3. **Sketch `MEMBER.md`** -- its front matter, its proc and its body:
   - the role: for a project, the one thing it makes; for a solution, the map of its parts, one
     line each with its path, each part keeping its own `README.md` and `design/`;
   - its `description:`, written with the body: one sentence, in the third person, that sums up
     the role and specialty the body describes -- its peers read it in `tools.md` and in a team's
     members sheet to know what to hand it;
   - the readings the role needs, in `serve:`, each line opening on its nature (`reference:`,
     `architecture:`, `contract:`, `map:`, `code:`), played by ONE bare `SERVE` at the head of its
     proc, before `CALL CAPABILITIES.md ^ @SETTINGS.capabilities` and `CALL TURN.md`;
   - its own laws: few, short, the load-bearing ones first -- each one rides every block and is
     proven every turn.
4. **On the operator's GO** -- write the front matter with `pp-authoring` (`section set MEMBER.md
   description`, `section serve MEMBER.md <nature>: <doc>`, `section set MEMBER.md proc`, `section
   constrain MEMBER.md`); the body is proposed whole, and the operator places it. Before you prove,
   read the description and the body side by side: they must say the same role.
