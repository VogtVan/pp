---
name: PP-OFFERS
kind: proc
description: >-
  Register harness skills in pp: survey skill homes, classify conductibility, propose scoped +name offers, then read the build back. An instance door, opened on the operator's GO.
output: free
constraints.production: |
  PO2  a superseded skill is not offered -- it is said, with the kit mechanism that covers it.
  PO3  every proposed offer names its scope -- the member, or the proc it serves.
constraints.behavior: |
  PO1  an offer is what the operator wants conducted -- that alone.
  PO4  the build is run and its warnings read back -- one left is said.

serve: |
  tools.md
  PP_CHEATSHEET.md[# The pp cheatsheet..## 1. Anatomy] PP_CHEATSHEET.md[### The overlay..### The described door]
proc: |
  SERVE
  WORK
---
# PP-OFFERS — the harness's skills become registered elements

The served catalog shows what is already offered, adopted or declared. Survey harness skills, classify them, propose offers, and close on the build's word.

## The survey

List and read the workspace skill homes — `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`. Every classification cites the file inspected; unopened skills are not classified.

## The ladder

Four verdicts, one/skill. Conductible means readable front matter and a `description:`. Surveying `atelier`:

    skill              home              verdict            the call
    -----------------  ----------------  -----------------  --------------------------
    commit-style       .claude/skills/   conductible        offer it (below)
    deploy-checklist   .claude/skills/   one call away      add its `description:` line
    log-your-work      .claude/skills/   superseded         the operations record
                                                            already keeps it -- say so
    browser-debug      .claude/skills/   harness-native     a named hole; offer
                                                            name-only IF a flow must
                                                            scope it, else leave it

PROPOSE missing pieces as exact edits; the operator owns the file, never touch it yourself. Never offer a superseded skill: name the kit mechanism replacing it. If a recommendation names an unoffered skill, use this door.

## The scope of each offer

Write an offer where its work lives:

- **the member's `tools:`** — whole-session offer; every block pays the name: use for skills spanning asks;
- **a proc's `tools:`** — that step only: for one workflow (in a solution, a sub-project tool belongs to its proc); adjust a BUNDLED proc via overlay (`+name` at home).

An offer LIVES with the output carrying its step: fused segments keep OWN lists; calls route to the owning numbered segment, using `-s <name>@<n>` only on ambiguity; the next output retires addresses. Scope offers ON the step that needs them: session-wide names cost every block, step-scoped names exist exactly when needed.

Both placements, ready to paste:

    # session-wide -- in your MEMBER.md front matter:
    tools: |
      +commit-style

    # step-scoped -- in the proc that needs it (procs/RELEASE.md):
    tools: |
      +commit-style

## The receipt

After the operator places offers, run `./pp -build` and read it back.

    pp: .pp/.sys/tools.md compiled.
    pp: WARNING -- offered-not-conductible: `deploy-checklist` (...) -- it
        declares no `description:`; offered name-only, nothing conducted

Report every remaining warning with its missing piece. Catalog section "Adopted skills" is the receipt: full entries, constraints registered.

## Not a call

Never COPY a harness skill into the instance: two truths under one name is the defect this product eliminates. Adoption on offer is the mechanism: file stays home, offer grants the read.
