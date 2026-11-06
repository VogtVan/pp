---
name: AUTHOR-OFFERS
kind: proc
description: >-
  The offers craft -- survey the skills the harness carries, and offer each one worth it at the
  scope where its work lives.
serve: |
  reference: engine/patterns/composition/door/README.md engine/patterns/composition/adoption/README.md engine/patterns/composition/overlay/README.md
tools: |
  pp-authoring
proc: |
  SERVE
  WORK
  PROVE
constraints.production: |
  AO1  every offer names its scope, and no harness skill is copied into the instance
---

# AUTHOR-OFFERS — the harness's skills, offered

Work through the hall's cycle; what is yours here:

1. **Survey** the skill homes of the workspace -- `.claude/skills/`, `.agents/skills/`,
   `.cursor/skills/` -- and read each skill before you classify it.
2. **Classify** each one: CONDUCTIBLE (readable front matter with a `description:`), ONE CALL AWAY
   (its `description:` missing: say the line to add), SUPERSEDED (a mechanism of pp already does
   it: name the mechanism), HARNESS-NATIVE (offered by name only, when a flow must scope it).
3. **Scope** each offer where its work lives: the member's `tools:` for a skill used across asks,
   a proc's `tools:` for one workflow; a bundled proc is adjusted by an overlay in the instance.
   An offer the instance adds reads `+<name>`.
4. **Write** on the operator's GO with `pp-authoring section set <doc> tools`, then run
   `./pp -build` and read its warnings back -- `offered-not-conductible` names the missing piece.

A harness skill is never copied into the instance: the offer reads it where it lives.
