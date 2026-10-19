---
name: PP-MIGRATE
kind: proc
description: >-
  Move an instruction system into pp: map what pp takes over, capture each skill's essence, check collisions, orient each piece (proc, skill or script), and sequence verifiable steps; other PP-* doors handle their craft. An instance door, opened on the operator's GO.
output: free
constraints.production: |
  PG2  each step ends verifiable -- a block, a catalog line, a warning gone.
  PG3  hand work and conducted work are told apart.
  PG4  a migrated skill is captured by its ESSENCE -- what it guarantees alone.
  PG5  no element takes a taken name, code or role -- names and roles are checked against the served catalog; a code collision is mechanical: `pp-authoring section constrain` derives the free codes and the build refuses a double.
  PG6  the other doors do their own craft -- rules to PP-RULES, offers to PP-OFFERS, the member to PP-MEMBER; the hand-over is said.
constraints.behavior: |
  PG1  nothing breaks before its replacement is in force.
  PG7  the sheet is proposed -- it applies on the operator's GO alone.
serve: |
  tools.md
  PP_CHEATSHEET.md[# The pp cheatsheet..## 1. Anatomy] PP_CHEATSHEET.md[## 1. Anatomy..## 2.] PP_CHEATSHEET.md[### The proven document..### The described door]
tools: |
  PP-MEMBER
  PP-RULES
  PP-OFFERS
proc: |
  SERVE
  WORK
---
# PP-MIGRATE — an existing system moves in

The served catalog holds every existing name and role: the collision baseline. Codes are mechanical -- `pp-authoring section constrain` derives the free ones and the build refuses a double. Map the existing system, capture essences, check collisions, orient each piece, and hand other crafts to their doors — as verifiable steps.

## The map

Before touching anything, sort the existing system into three columns:

    pp takes over              stays (for now)          dies -- mechanism named
    ------------------------   ----------------------   ------------------------
    the turn's discipline      domain workflows not     "acknowledge the rules
    the operations record      yet worth a proc         each turn" -- the laws
    the weekly digest                                   re-emit themselves
    the closing next-actions                            "read the guidelines
                                                        first" -- the serve
                                                        proves each reading

## Capture the essence

Migrate a skill by what it GUARANTEES — laws, checks, calls — never by pasting prose. Three probes:

    what does it make TRUE?      -> a constraint, or arming the doc (prove:)
    what does it FORBID?         -> a constraint
    what does it PRODUCE?        -> a step, its output named

Before and after:

    legacy prose (a page):     "Always write tests first. Remember to run the
                               whole suite before you say you are done. Be
                               careful with flaky tests..."
    the essence (two lines):   W1  the suite is green before a change is claimed.
                               one INFER step, prove: true -- W1 proven on the way out.

## The collision check

Check against what was SERVED, never memory:

    a taken NAME        -> rename the newcomer, or merge into the existing one
    an overlapping ROLE -> extend the existing element (an overlay, a section)
                           -- never a twin: two truths under one concern
    a taken CODE prefix -> a fresh prefix; `pp-authoring section constrain` says every code in force

## Skill or proc — the orientation

Intended initiative decides, never shelf. Three legacy pieces, three ways:

    "our release ritual, six ordered steps, gates"  -> a PROC: the flow must hold
    "our API style reference, consulted at need"    -> a SKILL: served on demand
    "the changelog formatter, deterministic"        -> a SCRIPT beside its contract

## The other doors

Their craft is theirs, offered here:

- the member's shape (role, scope, house codes)  → PP-MEMBER
- a rule's wording and its scope                 → PP-RULES
- offering the harness's skills                  → PP-OFFERS

THIS door keeps the sheet, essences and collisions. Say each hand-over as you make it.

## The sheet

Sequence operator-verifiable steps — replacement IN FORCE before the old way falls:

    step                        call                  verifiable by
    --------------------------  --------------------  ------------------------
    member proposed and placed  PP-MEMBER + operator  the boot block shows it
    laws scoped and placed      PP-RULES + operator   the build: one holder per code
    offers placed, build read   PP-OFFERS + operator  Adopted section, 0 warning
    legacy ritual retired       hand (operator)       the old file gone; its
                                                      mechanism named in the map
