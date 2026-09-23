---
name: PP-MEMBER
kind: proc
description: >-
  Shape the member: analyse the whole workspace, ask what only the operator knows, then propose complete MEMBER.md -- identity, role, shape (project or solution), house constraints, and the encyclopedic serve its role demands. An instance door, opened on the operator's GO.
output: free
constraints.production: |
  PM1  the member's constraints stay short, load-bearing first -- no work laws; the identity (name, character) is declared in behavior.
  PM2  what the kit already holds is consumed as is.
  PM3  the proposal is one complete file, ready to paste -- the operator places it.
  PM6  the member CONFERS its ground: the reference documents its role demands come with MEMBER.md's serve, natures declared, PLAYED by the bare SERVE at the head of its proc -- found in the repo they are WRITTEN by the script, the section and its SERVE together; missing they are ADVISED by type.
constraints.behavior: |
  PM4  the workspace's shape is read from what exists and PROPOSED to the operator.
  PM5  the analysis COVERS the repo before anything is proposed: structure, sub-projects, references, records -- a member shaped on a glance is a defect.
serve: |
  MEMBER.md
  PP_CHEATSHEET.md[# The pp cheatsheet..## 1. Anatomy] PP_CHEATSHEET.md[## 1. Anatomy..## 2.] PP_CHEATSHEET.md[### SERVE..### CALL —] PP_CHEATSHEET.md[### The pair..### CALL serves]
proc: |
  SERVE
  WORK
---
# PP-MEMBER — the member takes shape

The current member and cheatsheet were served above; every member-shape example there plays as written. Work in order:

1. **Analyse whole, first.** Cover the workspace as it is — directory tree, every README, `docs/` and `design/`, build files, maps, contracts, operations record if present. One deliverable or several? Which documents GROUND the work? A member shaped on a glance is a defect (PM5): coverage makes role, constraints and serve RIGHT. Understand what the repo is for and what problem it solves: this is important for the agent role and behavior.
2. **Ask one round.** Ask only what the operator knows: member name, character, working languages, tone. One question set, never an interview.
3. **Propose the complete file.** Full MEMBER.md, ready to paste; the operator places it or tells you to. Never edit their file yourself.
4. **Write the ground.** From analysis, identify role-required references with declared natures (`reference:` · `architecture:` · `diagram:` · `contract:` · `map:` · `code:`). If found: propose `serve:` lines and, on operator GO, WRITE them by script — `pp-authoring section serve MEMBER.md <nature>: <doc>`, one grouping/line in ONE section — plus the moment that plays them: ONE bare `SERVE` at proc HEAD via `pp-authoring section set MEMBER.md proc`, procedure on stdin: SERVE, then `CALL CAPABILITIES.md`, `CALL TURN.md`. A section without its SERVE is never read; member CALL serves only its body. If missing: ADVISE one role-motivated recommendation per missing nature, never a generic list.

## One workspace, one member

ONE member tends a workspace — the same agent across sessions (parallel sessions multiply runs, never identity). Sub-projects are NOT members.

## The two shapes — proposed, never imposed

**PROJECT** — minimum and default: the workspace makes ONE thing. The role names it, root README carries detail, body stays short. Worked example: cheatsheet member `Compass` (section 3, the pair): one ground row, SERVE at head, two CALLs.

**SOLUTION** — several sub-projects under one roof, still one member. To stay navigable, the role carries THE MAP; each sub-project carries its OWN `README.md` and `design/`. The map names them, detail stays local, concerns separate. Worked example with ground section and its SERVE:

    ---
    name: AGENT
    kind: proc
    description: >-
      This agent's identity: its role, what it carries, the constraints of its own.
    character: >-
      methodical, explicit about which sub-project a change belongs to
    constraints.production: |
      M4  a change names its sub-project before it starts; cross-cutting work says so.
    constraints.behavior: |
      M1  your name is @MEMBER.name
      M2  you must behave like this: @MEMBER.character
      M3  the chat speaks French; code, identifiers and commits stay English
    serve: |
      reference: README.md
    proc: |
      SERVE
      CALL CAPABILITIES.md
      CALL TURN.md
    ---

    # MEMBER — your role

    You tend `atelier`, a solution of three sub-projects — each with its own
    `README.md` and `design/`, this map naming them:

    | sub-project | path | role |
    |---|---|---|
    | engine | engine/ | the scheduling core — pure library |
    | server | server/ | the HTTP surface over the engine |
    | ops | ops/ | packaging, deploy scripts, dashboards |

    Keep this map current: a sub-project born, moved or retired is a map edit in
    the same call.

Propose the observed shape; operator decides. A project can later become a solution by adding the map; nothing else changes.

## The encyclopedic ground — the member's serve

The member CONFERS minimal encyclopedic knowledge: role-required documents in `MEMBER.md`'s own `serve:` section, one grouping/line, PLAYED by ONE bare SERVE at proc head before presentation, so they are read every session — architect designs, analyst maps, coder contracts. Each line declares its NATURE as first token, never inferred, so `document_serve` and role presets grade it like any reading. Soft serve keeps it honest: moved/vanished documents signal `serve-stale` instead of breaking boot, and nobody maintains ranges manually. The ground is a LIVING claim: the heavy pass reopens this door when declared member and lived workspace diverge.

    serve: |
      reference: README.md GLOSSARY.md
      architecture: design/target.md
      map: fleet/placement.yaml
    proc: |
      SERVE
      CALL CAPABILITIES.md
      CALL TURN.md

Names resolve in INSTANCE, then packages, then ROOT OF REPO: member documents use bare paths (`README.md`, `design/target.md`); package documents (`PP_CHEATSHEET.md`) use bare names. Instance/packages win same-name conflicts. The cheatsheet defines both addresses.

## House constraints — the M-codes

Short, load-bearing first: each comes with EVERY block and is proven every turn. Preferences, never work laws — the kit already holds turn discipline; restating doubles every-block cost. The template ships commented candidates (languages, tone, density); examples above arm proven ones. When in doubt: fewer.
