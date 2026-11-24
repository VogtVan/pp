---
name: AUTHOR-RULES
kind: proc
description: >-
  The rules craft -- find a rule its words and its holder: the member, a plan node, a proc, an
  overlay -- and write it as a law.
serve: |
  reference: engine/patterns/rules/laws/README.md engine/patterns/rules/prove/README.md engine/patterns/rules/repair/README.md
tools: |
  pp-authoring
proc: |
  SERVE
  WORK
  PROVE
constraints.production: |
  AR1  every law written names its section and sits at the cheapest holder that covers it
---

# AUTHOR-RULES — a rule finds its words and its holder

Work through the hall's cycle; what is yours here:

- **Law or body.** Must it hold, and be proven, of every answer while its frame lives? It is a
  law. Does it describe the work, the material, the order of the steps? It belongs in the body.
- **Its section.** `constraints.production` for what the agent MAKES -- proven at every `PROVE`;
  `constraints.behavior` for what it does, says or reads -- served at every step, never proven.
- **Its words.** One positive, imperative line, leaning against a pull the model really has:
  flattering the material, rewriting instead of judging, inventing what fits, reading a GO wide.
- **Its holder**, the cheapest that covers it, costliest first: the member (every block of every
  session) › a plan, a phase, a batch (the mounts of its nodes) › a proc (its own frame) › an
  overlay of a bundled proc (`procs/<NAME>.md` in the instance) › already held by the kit ›
  dead, replaced by a mechanism you name.

Sketch an inventory -- rule, statement, section, holder -- and the lines as they will read. On the
operator's GO, write each with `pp-authoring section constrain <doc> --section
production|behavior`, the texts on stdin; the script gives the codes.
