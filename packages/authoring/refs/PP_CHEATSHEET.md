---
name: PP_CHEATSHEET
kind: doc
description: >-
  One-sheet pp language: playable examples of document anatomy, every instruction's happy path, and the key patterns (serve+SERVE, CALL body-only, mount, feed, floor, armed document, overlay, door). The kit bench extracts and plays them all.
---

# The pp cheatsheet — examples that play

Every example below is a COMPLETE playable document: place it in `.pp/` or `procs/` as `<name>.md`, matching `name:`. Each is followed by its engine rendering, with engine-filled parts elided as `…`. A rendering below shows the SEGMENT alone: every real output opens once on its own heading — `▌ pp · run <key> · … · <HH:MM:SS> · +<elapsed>` — and the segment headings follow it, `▌ [n] <stack>` under fusion, `▌ <stack>` alone. Examples reference each other; paste any named by a section or CALL. The bench plays them all; a broken one reddens the suite.

## 1. Anatomy

### A served document — `kind: doc`

    ---
    name: STYLE
    kind: doc
    description: the house style, served to whoever writes.
    ---

    Short sentences. One idea per paragraph. Name the thing, never the feeling.

A TOOL-read document has no `proc:` and never executes — any text file serves whole, the hash pp computes on it proves what was served. Glossary, spec, map: anything named by `serve:`.

    ---
    name: GLOSSARY
    kind: doc
    description: the words of the house, one per line.
    ---

    draft -- the text under review, never the final.
    verdict -- approve, revise or reject; one word.
    finding -- a defect with the line it comes from.
    ground -- the documents a role reads at every session.

### A conducted document — `proc:`

    ---
    name: REVIEW
    kind: proc
    description: judge a draft, hand ONE verdict with its findings.
    output: line
    constraints.production: |
      C1  you judge the draft; you never rewrite it.
    proc: |
      INFER
    ---

    Hand down ONE verdict — approve, revise or reject — with the findings
    that carry it.

`proc:` makes the document CONDUCTED: front matter declares guarantees; body is the pending step's brief:

    ▌ REVIEW{1/1}

    ▌ INFORMATION — standing orders
    …

    ▌ NEXT INSTRUCTION CONTEXT — REVIEW
    Hand down ONE verdict — approve, revise or reject — with the findings
    that carry it.

    ▌ CONSTRAINTS
    C1  you judge the draft; you never rewrite it.

    ▌ INSTRUCTION
    INFER line => chat

    ▌ END
    the conduction is over — report to the operator; do not call the tool again.

The instruction names form (`line`, from formats) and channel (`=> chat` here: no later draft delivery). Closings: `CONTINUE` now, `FINAL` after operator reply, `END` nothing; this one-step document ends on END. Standing orders appear only on the run's FIRST output; later renderings elide them.

## 2. The instructions — the happy path

### WORK — the free step

    ---
    name: ASK
    kind: proc
    description: serve the operator's ask, whatever it takes.
    proc: |
      WORK
    ---

    The operator's message is the ask — serve its RESULT in this exchange:
    chain tools, read, produce as many times as it takes.

    ▌ ASK{1/1}

    ▌ NEXT INSTRUCTION CONTEXT — ASK
    The operator's message is the ask — …

    ▌ INSTRUCTION
    WORK free => chat

    ▌ END
    …

### INFER — one production, one form

    ---
    name: TALLY
    kind: proc
    description: count what exists, in one table.
    output: table
    proc: |
      INFER
    ---

    One table: what was asked, what was delivered, what remains.

    ▌ INSTRUCTION
    INFER table => chat

`output:` names the form; unknown names refuse at parse. Flow derives channel: `=> chat` without FINAL ahead, `=> ephemeral` before one, `=> tool` when consumed (PICK, callee, engine).

### PICK — a choice from a produced list

    ---
    name: TRIAGE
    kind: proc
    description: list the candidates, then elect one.
    output: json
    proc: |
      INFER
      PICK candidate
    ---

    List the candidates as a JSON array of short ids, then elect ONE.

INFER produces the stdin `json`; PICK's OPTIONS ARE it. No upstream production refuses `options-empty`:

    ▌ TRIAGE{1/2}

    ▌ INSTRUCTION
    INFER json => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -   (your <output> on stdin -- heredoc)

    ./pp <key> - <<'EOF'
    ["approve", "revise", "reject"]
    EOF

    ▌ TRIAGE{2/2}

    ▌ OPTIONS
    approve
    revise
    reject

    ▌ INSTRUCTION
    PICK candidate options => tool

    ▶ CONTINUE
    ./pp <key> <your-choice>

### SERVE — the tool reads for the agent

Bare `SERVE` dequeues ONE whole `serve:` SECTION (contiguous lines; blank line separates) in one call. ONE reader serves section rows, mount rows and CALLed bodies, proving each document ONCE/run by content; repeat names via another section, `SERVE <doc>`, mount or CALL render nothing. Readings are TITLED by the exact row token, including path/range (`INFORMATION — design/target.md`, `INFORMATION — GLOSSARY.md[1-2]`), so same-named files stay distinct; CALLed bodies keep the document name.

    ---
    name: BRIEFED
    kind: proc
    description: read the style, then judge.
    serve: |
      STYLE.md
    proc: |
      SERVE
      INFER
    ---

    Judge the draft against the style served above.

    ▌ BRIEFED{2/2}

    ▌ INFORMATION — STYLE.md
    Short sentences. One idea per paragraph. Name the thing, never the feeling.

    ▌ NEXT INSTRUCTION CONTEXT — BRIEFED
    Judge the draft against the style served above.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

Explicit `SERVE <doc>` names the document inline; no section needed:

    ---
    name: DIRECT
    kind: proc
    description: read the glossary named on the line.
    proc: |
      SERVE GLOSSARY.md
      INFER
    ---

    Use the words of the glossary, none other.

A line may name several documents, ranges (`GLOSSARY.md[1-2]`: stale clamps, gone skips with note, `serve-stale` signals either), and a first-token NATURE (`reference:` · `architecture:` · `diagram:` · `contract:` · `map:` · `code:`) — a declaration for the readers, never a hold: every row serves. Several lines still form ONE section/one SERVE; a blank line starts the next. Thus n sections require n bare SERVEs, in order, pacing readings across the step:

    ---
    name: GROUNDED
    kind: proc
    description: one section of two lines, then a second section of its own.
    serve: |
      reference: STYLE.md GLOSSARY.md[1-2]
      reference: GLOSSARY.md[3-4]

      reference: STYLE.md
    proc: |
      SERVE
      INFER
      SERVE
      INFER
    ---

    Write with the style and the words served above; then say it again.

    ▌ GROUNDED{2-4/4}

    ▌ INFORMATION — STYLE.md
    …

    ▌ INFORMATION — GLOSSARY.md[1-2]
    draft -- the text under review, never the final.
    verdict -- approve, revise or reject; one word.

    ▌ INFORMATION — GLOSSARY.md[3-4]
    finding -- a defect with the line it comes from.
    ground -- the documents a role reads at every session.

    ▌ NEXT INSTRUCTION CONTEXT — GROUNDED
    …

    ▌ INSTRUCTION
    INFER free => chat
    INFER free => chat

    ▌ END
    …

First SERVE reads its whole section — three readings on two lines. Second SERVE plays the next: STYLE is already proven, so renders NOTHING; with nothing between them, both INFERs share one INSTRUCTION title. Under `instructions_fusion: max`, the stretch fuses as `{2-4/4}`; a PICK between sections would force a separate output.

### Addressing — where a name resolves

Bare names resolve nearest-first through member SEARCH PATHS: instance `.pp/`, `procs/`, `.sys/`; each vendor package's `admin/`, `overlays/`, `procs/`, `refs/`; then MEMBER REPO ROOT. A vendored `.sys/vendor/<package>@<version>/…` path is a PIN and is never written:

    ---
    name: SITUATED
    kind: proc
    description: two readings, two addresses, one line.
    serve: |
      reference: README.md PP_CHEATSHEET.md
    proc: |
      SERVE
      INFER
    ---

    Say where each reading came from.

- `README.md` — MEMBER REPO: if instance/packages do not answer, its bare path resolves at repo root (`design/target.md`, `fleet/placement.yaml` alike). If nothing answers, it is GONE — reported to improve, never served.
- `PP_CHEATSHEET.md` — PACKAGE document (authoring `refs/`): bare-name resolution like package procs. Instance/package documents outrank same-named repo files; repo is last resort, never an overlay.

    ▌ SITUATED{2/2}

    ▌ INFORMATION — README.md
    …

    ▌ INFORMATION — PP_CHEATSHEET.md
    …

### CALL — the body first, then the frame

    ---
    name: GATE
    kind: proc
    description: open the review, take its verdict.
    proc: |
      CALL REVIEW.md
      INFER
    ---

    Say what the verdict decides.

CALL is SERVE plus execution: callee BODY appears first, then its procedure runs in a new frame; its constraints/tools ACCUMULATE over the caller's and fall with the frame, and its last production feeds the caller's next step. The body uses the same reader/content proof: with `proc_body_serve: once` (light-effort preset), an already proven body renders nothing on later CALLs; `always` forces it every time. Heading shows the path; only the active frame has a pointer:

    ▌ [1] GATE ▸ REVIEW{1/1}

    ▌ INFORMATION — GATE
    Say what the verdict decides.

    ▌ NEXT INSTRUCTION CONTEXT — REVIEW
    Hand down ONE verdict — …

    ▌ CONSTRAINTS
    C1  you judge the draft; you never rewrite it.

    ▌ INSTRUCTION
    INFER line => chat

    ▌ [2] GATE{2/2}

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

With `instructions_fusion: max`, callee step and caller's next step fuse into ONE output under numbered scopes (`[1]`, `[2]`); caller body is INFORMATION, pending-step body CONTEXT.

### HOOK and `attach:` — the socket

    ---
    name: SHIP
    kind: proc
    description: ship, then let whoever attaches to `shipped` play.
    proc: |
      INFER
      HOOK shipped
    ---

    Say what ships.

    ---
    name: NOTIFY
    kind: proc
    description: tell the operator what just shipped.
    attach: shipped
    proc: |
      INFER
    ---

    One line: what shipped, where it is.

Every `attach: shipped` document is CALLed at `HOOK shipped`, in name order; an empty socket resolves silently. Scan is live: dropping a document into `procs/` is enough.

    ▌ [1] SHIP{1/2}

    ▌ NEXT INSTRUCTION CONTEXT — SHIP
    Say what ships.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ [2] SHIP ▸ NOTIFY{1/1}

    ▌ NEXT INSTRUCTION CONTEXT — NOTIFY
    One line: what shipped, where it is.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

### FINAL — the exchange's frontier

    ---
    name: EXCHANGE
    kind: proc
    description: one exchange -- the inventory, the work, then deliver.
    proc: |
      INFER
      WORK
      FINAL
    ---

    Take stock, serve the ask; the FINAL delivers what you drafted.

Before FINAL, productions are `=> ephemeral` hidden DRAFTS. FINAL delivers all validated turn drafts, in order, as ONE chat message, then waits for the operator. An ADJACENT production with no held draft is `=> chat`; e.g. lone `WORK` before `FINAL` speaks directly.

    ▌ EXCHANGE{1-2/3}

    ▌ INSTRUCTION
    INFER free => ephemeral
    WORK free => ephemeral

    ▶ FINAL ephemerals => chat
    ./pp <key>   (once the operator replies)

### `§` and `# ` — the section break and the comment

    ---
    name: PACED
    kind: proc
    description: two steps the fusion never fuses; one line kept for later.
    proc: |
      INFER
      §
      INFER
      # INFER
    ---

    First the inventory, then — on its own output — the verdict.

With `instructions_fusion: max`, a certain stretch is ONE output; lone `§` is the boundary fusion never crosses. `# ` comments `proc:` or `constraints:`; uncommenting arms the line.

    ▌ PACED{1/2}

    ▌ INSTRUCTION
    INFER free => chat

    ▶ CONTINUE
    ./pp <key>

    ▌ PACED{2/2}

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

### `^ @Doc.field` — the due

    ---
    name: CADENCED
    kind: proc
    description: work, and consign every n exchanges.
    proc: |
      WORK
      CALL NOTE.md ^ @SETTINGS.note_frequency
    ---

    Serve the ask; the note plays on its own cadence.

    ---
    name: NOTE
    kind: proc
    description: one dated line about what was done.
    proc: |
      INFER
    ---

    Consign one line: what was done since the last note.

The guard reads cadence from a document field — here SETTINGS — and plays the CALL every n completed exchanges, otherwise silently. The agent keeps no calendar. When not due:

    ▌ CADENCED{1/2}

    ▌ INSTRUCTION
    WORK free => chat

    ▌ END
    …

### `formats:` and `output:` — the form is a name

    ---
    name: FORMED
    kind: proc
    description: a form of this document's own, then a production in it.
    formats: |
      verdict  inline  one word -- approve, revise or reject
    output: verdict
    proc: |
      INFER
    ---

    Hand the verdict in its own form.

    ▌ INSTRUCTION
    INFER verdict => chat

Format syntax is `name  inline|stdin  definition`; MODE sets transport (on-call or piped). Declaration extends the enumeration; redeclaration overrides.

## 3. The patterns

### The pair — a `serve:` section plays on its SERVE (the member's ground)

The section DECLARES; bare SERVE is its MOMENT. Without SERVE the section is unread; SERVE without a section refuses `serve-exhausted`. The member ground — session readings for its role — puts SERVE at proc HEAD, before presentation:

    ---
    name: Compass
    kind: proc
    description: >-
      This agent's identity: its role, what it carries, the constraints of its own.
    character: >-
      terse, dry humor
    constraints.behavior: |
      M1  your name is @MEMBER.name
      M2  you must behave like this: @MEMBER.character
    serve: |
      reference: GROUND.md
    proc: |
      SERVE
      CALL CAPABILITIES.md
      CALL TURN.md
    ---

    # MEMBER — your role

    You tend `weather-cli`, a Rust command-line client for aviation weather: one
    binary, one crate, its README at the workspace root.

    ---
    name: GROUND
    kind: doc
    description: what the role reads at every session.
    ---

    The README's contract: offline first, terse output, releases by checklist.

This is the instance's `MEMBER.md` (`name:` remains the member's; filename stays MEMBER.md). At boot, ground precedes the kit-requested presentation:

    ▌ [1] BOOT ▸ MEMBER ▸ CAPABILITIES{2/2}

    ▌ TOOLS
    [PP-MEMBER PP-RULES PP-OFFERS PP-MIGRATE PP-DESIGN]

    ▌ INFORMATION — standing orders
    …

    ▌ INFORMATION — Compass
    # MEMBER — your role
    …

    ▌ INFORMATION — GROUND.md
    The README's contract: offline first, terse output, releases by checklist.

    ▌ INFORMATION — tools
    …

    ▌ NEXT INSTRUCTION CONTEXT — CAPABILITIES
    …

    ▌ CONSTRAINTS
    M1  your name is Compass
    M2  you must behave like this: terse, dry humor
    …

    ▌ INSTRUCTION
    INFER table => ephemeral

CALL served member body (Compass), then its proc: SERVE read ground before CAPABILITIES requested presentation.

`pp-authoring section serve MEMBER.md reference: GROUND.md` writes the line; `pp-authoring section set MEMBER.md proc` (proc on stdin, SERVE first) writes its moment — the pattern's two calls.

### CALL serves the body alone — the callee's section is its own SERVE's

    ---
    name: HOLLOW
    kind: proc
    description: declares a reading, never plays it.
    serve: |
      STYLE.md
    proc: |
      INFER
    ---

    Judge the draft against the style.

    ---
    name: OPENER
    kind: proc
    description: opens HOLLOW.
    proc: |
      CALL HOLLOW.md
    ---

    Open the judgment.

HOLLOW's body appears; STYLE does not — its section is inert, so the brief points at nothing. CALL serves only callee BODY; its section needs ITS OWN bare SERVE:

    ---
    name: WHOLE
    kind: proc
    description: declares a reading and plays it at its entry.
    serve: |
      STYLE.md
    proc: |
      SERVE
      INFER
    ---

    Judge the draft against the style served above.

    ▌ OPENER ▸ HOLLOW{1/1}

    ▌ INFORMATION — OPENER
    Open the judgment.

    ▌ NEXT INSTRUCTION CONTEXT — HOLLOW
    Judge the draft against the style.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ WHOLE{2/2}

    ▌ INFORMATION — STYLE.md
    Short sentences. One idea per paragraph. Name the thing, never the feeling.

    ▌ NEXT INSTRUCTION CONTEXT — WHOLE
    Judge the draft against the style served above.

### The mount — hosting a document that has no `proc:`

    ---
    name: NODE
    kind: doc
    description: a framing's node -- its laws, its readings, its offers; no flow.
    constraints.production: |
      N1  the node's law binds every production under it.
    serve: |
      STYLE.md
    tools: |
      pp-authoring
    ---

    The framing established here: what the work must hold, what it reads.

A knowledge/law node has no procedure: CALL cannot play it, while stacking frames merely to keep it IN FORCE creates nesting the flow never unwinds. MOUNT hosts it beside the pending step (here FLOOR WORK): `constraints:` bind blocks, `tools:` join offers, `serve:` rows PLAY on call (soft budget cap), body comes when requested; no frame, ONE exchange, removed on next rewind.

    ./pp <key> -mount '[{"doc": "NODE.md", "scope": "nested", "body": true}]'

    ▌ [1] FLOOR ▸ NODE

    ▌ TOOLS
    [pp-authoring]

    ▌ INFORMATION — NODE
    The framing established here: what the work must hold, what it reads.

    ▌ CONSTRAINTS
    N1  the node's law binds every production under it.

    ▌ [2] FLOOR{1/2}

    ▌ INFORMATION — STYLE.md
    Short sentences. One idea per paragraph. Name the thing, never the feeling.

    ▌ INSTRUCTION
    WORK free => chat

    ▶ FINAL
    ./pp <key>   (once the operator replies)

The JSON entry selects `body`, `constraints`, `tools`, `scope`: `nested` creates its own numbered/addressable scope; `stacked` (default for bare `./pp <key> -mount NODE.md`) accompanies the pending frame as INFORMATION. A `-s` script can emit `::mount [...]` in the same call: script derives the chain, pp hosts it — how plan/phase/batch enter force together.

### The feed — a production seeds its consumer

    ---
    name: PLANNER
    kind: proc
    description: produce the plan as data, then hand it to the builder.
    output: json
    proc: |
      INFER
      CALL BUILDER.md
    ---

    One JSON object: the steps to build, in order.

    ---
    name: BUILDER
    kind: proc
    description: build what the planner handed over.
    input: json
    proc: |
      INFER
    ---

    Build the steps of the plan received.

Callee `input:` CAPTURES the caller's adjacent production (`json` must parse) and seeds its pipeline. Consumption is USE, not transport: production returns only when used.

    ▌ INSTRUCTION
    INFER json => tool (heredoc)

### The floor — `cycle: true`

    ---
    name: FLOOR
    kind: proc
    description: the session's floor -- every exchange, the same two steps.
    cycle: true
    proc: |
      WORK
      FINAL
    ---

    Serve the ask, deliver, wait for the next message.

Exhausted `cycle: true` REWINDS instead of completing; the next operator message reaches step one. Kit TURN is one.

### The iterated door — `cycle: <token>`

    ---
    name: SWEEP
    kind: proc
    description: one lap per element the token renders; the door leaves when nothing is due.
    cycle: doc-sources
    sink: pp-doc
    constraints.production: |
      S1  the lap's production names its element.
    proc: |
      INFER
    ---

    Write the element served under the token, then hand it to the sink.

The token's providers (`provides: doc-sources`, `with: <skill> <args>`) render the element that remains DUE — a request, never a cursor; the accepted production moves it. Each lap re-resolves the payloads, keeps the mounts and proves under every law on screen; nothing due, the frame leaves like any callee — `cycle-unprovided` when no document provides the token.

### The proven document — a law of production

    ---
    name: PROVEN
    kind: proc
    description: a production proven against its laws before it leaves.
    constraints.production: |
      C1  every claim carries the line it comes from.
    proc: |
      INFER
      FINAL
    ---

    Say what holds; prove it before it leaves.

The checkpoint is engine-injected before each FINAL and at frame exit, wherever a law of production is in force — no key, no switch: the proof names the codes at risk, at least one, a code unnamed is n/a. Behavior laws bind but are never proven; a document with no production law owes nothing.

    ▌ PROVEN{1-2/2}

    ▌ CONSTRAINTS
    C1  every claim carries the line it comes from.

    ▌ INSTRUCTION
    INFER free => chat
    INFER proof [B1 B2 …] on all produced areas => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -   (your proof on stdin -- heredoc)

Range `{1-2/2}` means fused production + engine-injected checkpoint before FINAL.

### The overlay — deltas on a same-name document in a nearer space

    ---
    name: TURN
    constraints.production: |
      X1  every answer closes on the ask's status.
    ---

A same-named document in instance space (`.pp/TURN.md` or `.pp/procs/TURN.md`) is an OVERLAY, not a shadow: section DELTAS add laws (`X1`/`+X1`), remove laws (`-T4`), add offers (`+pp-authoring`, also adopting a harness skill), or remove offers (`-pp-authoring`). Kit TURN shows X1 from next boot. Nearer applies later and wins: instance, package `overlays/`, package bases.

### The door — an offer opened by name

    ---
    name: DESK
    kind: proc
    description: the step that offers the review as a door.
    tools: |
      REVIEW
    proc: |
      WORK
    ---

    Serve the ask; open the review when the draft is ready.

    ▌ DESK{1/1}

    ▌ TOOLS
    [REVIEW]

    ▌ INSTRUCTION
    WORK free => chat

    ./pp <key> -s REVIEW

`tools:` lists step offers; `-s <name>` plays one THROUGH pp: pending block first, then a `proc:` door stacks under its laws, a script runs, or a bare contract opens as a step. Offers live with their output: place the call ON the step that needs it.
