---
name: PP_CHEATSHEET
kind: doc
description: >-
  One-sheet pp language: playable examples of document anatomy, every instruction's happy path, and the key patterns (serve+SERVE, CALL body-only, mount, feed, floor, armed document, overlay, door). The package's body test installs and plays them all.
---

# The pp cheatsheet — examples that play

Every example below is a COMPLETE playable document: place it in `.pp/` or `procs/` as `<name>.md`, matching `name:`. Each is followed by its engine rendering, with engine-filled parts elided as `…`: a `…` on a line of its own stands for any lines, a line ending with ` …` shows its head, and between two elisions the lines are CONSECUTIVE. A rendering below shows the SEGMENT alone: every real output opens once on its own heading — `▌ pp · run <key> · … · <HH:MM:SS> · +<elapsed>` — then the line saying which packages play, and the standing orders on the run's first output; the segment headings follow, `▌ [n] <stack>` under fusion, `▌ <stack>` alone. Examples reference each other; paste any named by a section or CALL. The package's body test (`tests/body/PP_CHEATSHEET.py`) installs every document below on a throwaway instance, plays every rendering and compares it line for line: a broken example reddens the suite.

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
    constraints.behavior: |
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
    behavior:
    C1  you judge the draft; you never rewrite it.

    ▌ INSTRUCTION
    INFER line => chat

    ▌ END
    the conduction is over — report to the operator; do not call the tool again.

The instruction names form (`line`, from formats) and channel (`=> chat` here: no later draft delivery). Closings: `CONTINUE` now, `FINAL` after operator reply, `END` nothing; this one-step document ends on END. A law says its SECTION: `behavior:` binds what you do and is never proven; `production:` binds what you make and is proven at the checkpoint the engine injects (see The proven document). Standing orders appear only on the run's FIRST output; later renderings elide them.

The BODY carrying the pending instruction is promoted above ordinary reading — the ask's own brief:

Write a `proc:` body as its brief: one concern, addressed to whoever acts now. It arrives on CALL through the same reader and is proven by content. With `proc_body_serve: once`, once proven in the run it renders nothing on later CALLs: brief once, laws every block. `always` forces it back on every CALL.

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

An unconsumed `WORK`/`INFER` speaks to the operator. CHANNEL is flow-derived, never declared: before the turn frontier it is `=> ephemeral` — a DRAFT delivered once by FINAL, validated and in step order; adjacent to the frontier with no draft held it is `=> chat`; with no `FINAL` ahead it is immediately `=> chat`:

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
    …

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

Membership validates; anything else is a MISS -- see The miss below. The list itself is judged at its CAPTURE, on the form a FIELD has -- a JSON array of scalars, none empty, each once: a list of objects, an empty array or a bare scalar is a MISS named under DEVIATION, and a number renders as its text (`[1, 2]` offers `1` and `2`); a list no capture judged (a callee's seed) refuses `options-invalid`.

### SERVE — the tool reads for the agent

Bare `SERVE` dequeues ONE whole `serve:` SECTION (contiguous lines; blank line separates) in one call. ONE reader serves section rows, mount rows and CALLed bodies, proving each document ONCE/run by content; repeat names via another section, `SERVE <doc>`, mount or CALL render nothing. Readings are TITLED by the exact row token, including path/range (`INFORMATION — design/target.md`, `INFORMATION — GLOSSARY.md[7-8]`), so same-named files stay distinct; CALLed bodies keep the document name.

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

A line may name several documents, ranges (`GLOSSARY.md[7-8]` — a range counts the FILE's lines, front matter included, so GLOSSARY's body starts at line 7; stale clamps, gone skips with note, `serve-stale` signals either), and a first-token NATURE (`reference:` · `architecture:` · `diagram:` · `contract:` · `map:` · `code:`) — a declaration for the readers, never a hold: every row serves. Several lines still form ONE section/one SERVE; a blank line starts the next. Thus n sections require n bare SERVEs, in order, pacing readings across the step:

    ---
    name: GROUNDED
    kind: proc
    description: one section of two lines, then a second section of its own.
    serve: |
      reference: STYLE.md GLOSSARY.md[7-8]
      reference: GLOSSARY.md[9-10]

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

    ▌ INFORMATION — GLOSSARY.md[7-8]
    draft -- the text under review, never the final.
    verdict -- approve, revise or reject; one word.

    ▌ INFORMATION — GLOSSARY.md[9-10]
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

Long readings continue across calls: each continuation gets bare recall (`▶ CONTINUE`) and arrives untitled; the delimiter appears once. A token may cut a document between two TAGS (`file.py[def play..def stop]`, each the start of a line, still pointing at the same part when lines are added above) or, as a last resort, by ranges (`file.py[10-40]`): convenience, never maintenance duty. Stale ranges clamp; gone documents skip with a note; `serve-stale` signals either, so nobody maintains ranges manually. A line's first token may declare its NATURE; the regime grades line by line. A document without `proc:` serves its section through the mount below.

Between two TAGS, a token reads the document as plain lines whatever its type: the start of a line is enough, the end tag is excluded and sought after the start, either side may stay open (`tests/engine/reading/tagged-serve.py`); the lines keep pointing at the same part when the document grows above them, which a line range never does:

    ---
    name: TAGGED
    kind: proc
    description: read two lines of the glossary, between two tags.
    serve: |
      GLOSSARY.md[draft --..finding --]
    proc: |
      SERVE
      INFER
    ---

    Use the two words served above, none other.

    ▌ TAGGED{2/2}

    ▌ INFORMATION — GLOSSARY.md[draft --..finding --]
    draft -- the text under review, never the final.
    verdict -- approve, revise or reject; one word.

    ▌ NEXT INSTRUCTION CONTEXT — TAGGED
    Use the two words served above, none other.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

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
    behavior:
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
    …

    ▌ INSTRUCTION
    INFER free => ephemeral
    WORK free => ephemeral

    ▶ FINAL ephemerals => chat (EXCHANGE)
    ./pp <key> <the operator's next message>
       (once the operator replies -- no law of production in force: no proof owed)

The FINAL names, in parentheses, the documents whose drafts it delivers, in step order; the note under the call says whether the turn closes on a proof first.

The closing belongs to the flow, never the author. A closing owing a call has `▶`; `END` owes none:

The FINAL names, in step order, the documents whose drafts it delivers (`tests/engine/execution/final-names.py`); with no draft standing it is a bare `▶ FINAL`, and with `capture_prompt: false` the command is `./pp <key>` alone. The note rides its own line so the command stays copyable, and says what the call closes on — that no proof is owed, or that the turn closes on its proof when a law of production is in force. The agent copies the command verbatim — run `<key>` first.

Place `FINAL` deliberately: it is exchange frontier and delivery point for all preceding drafts — its closing line names their documents in step order (`ephemerals => chat (A · B)`), which is what lets the delivery separate one draft from the next. Keyed advance moves the flow; pp never needs the agent's own text back.

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
    …

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
    …

    ▌ INSTRUCTION
    WORK free => chat

    ▌ END
    …

The boot that opens on something: When dates require it — new week, undigested record — the engine INJECTS a start step, playing the cadenced document before member takeover. The author defines the injected proc (e.g. continuity weekly digest); the engine owns when.

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

    ▌ INFORMATION — tools.md
    …

    ▌ NEXT INSTRUCTION CONTEXT — CAPABILITIES
    …

    ▌ CONSTRAINTS
    behavior:
    …
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

A document without `proc:` — plan node, framing, ref — carries laws, offers and readings but no flow: CALL has nothing to play there, and stacked frames would create nesting the flow never walks back through. A mount HOSTS it beside the pending step: `constraints:` bind every block, `tools:` joins offers, `serve:` rows play on the call (soft serve-budget cap; gone file skips with note), and body comes when requested. The laws and the offers are those of the document's COMPOSITION, as for a frame: its own sections, then the deltas of its overlays — an overlay applies to the BASE of its name alone, and a homonym mounted by its path keeps its own sections (`tests/engine/execution/mount-overlays.py`). No frame; it lasts ONE exchange and the next rewind removes all mounts.

    ./pp <key> -mount '[{"doc": "NODE.md", "scope": "nested", "body": true}]'

    ▌ [1] FLOOR ▸ NODE

    ▌ TOOLS
    [pp-authoring]

    ▌ INFORMATION — NODE
    The framing established here: what the work must hold, what it reads.

    ▌ CONSTRAINTS
    N1  the node's law binds every production under it.

    ▌ [2] FLOOR{2/2}

    ▌ TOOLS
    [pp-authoring]

    ▌ INFORMATION — STYLE.md
    Short sentences. One idea per paragraph. Name the thing, never the feeling.

    ▶ FINAL
    ./pp <key> <the operator's next message>
       (once the operator replies -- …

A mount never advances the run: it re-shows the block that STANDS — here the FINAL the first output closed on, since FLOOR's WORK and FINAL fused into one output — in its richer view: the offer joins the step's TOOLS, the row plays, and under N1 the turn now closes on its proof. The JSON entry selects `body`, `constraints`, `tools`, `scope`: `nested` creates its own numbered/addressable scope; `stacked` (default for bare `./pp <key> -mount NODE.md`) accompanies the pending frame as INFORMATION. A `-s` script can emit `::mount [...]` in the same call: script derives the chain, pp hosts it — how plan/phase/batch enter force together.

A document also enters a SOCKET by its own front matter — `mount: <socket>`, exclusive of `attach:` (`attach-and-mount` refuses at build): hosted at its socket every turn, no skill, no directive — the figures below (the contributor, the mounted step) say when each door fits.

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

**Consumption is USE, not transport** — pp catches whatever accompanies a call, but production RETURNS only when consumed. Three consumers exist, only the first declared: a callee (`input:`); an election (PICK options ARE upstream production); and **the engine itself** — checkpoint proof consumed by the judge, sunk production by the bus, or document `sink:` by its named skill (stdin in, `::push` / `::clear` out). Engine-consumed production travels `=> tool` like any FEED; authors never declare channels.

**Capture is not a channel.** The keyed call is ONE bidirectional wire: the OPERATOR's message reaches resume at the frontier (FINAL asks for it under `capture_prompt`); the AGENT's production returns only when consumed. The frontier distinguishes directions — never a declaration.

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
    …

    ▌ CONSTRAINTS
    production:
    C1  every claim carries the line it comes from.

    ▌ INSTRUCTION
    INFER free => chat
    INFER proof [C1] on all produced areas => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -
       (your proof on stdin -- heredoc)

Range `{1-2/2}` means fused production + engine-injected checkpoint before FINAL.

Laws live in TWO sections: `constraints.production` governs what the agent MAKES and is proven at checkpoints, its text naming whether rendering covers whole, sample or trace fact; `constraints.behavior` governs what it does, says or reads, is served every block and never proven. Bare `constraints:` refuses at parse (`constraints-unsectioned`). Both appear with EVERY block while their frame lives, under ONE title, production first, and disappear with the frame:

Constraints ACCUMULATE: a CALLed document adds its own over its caller's. Placement — MEMBER › proc › overlay › kit › dead, with plan-package nodes between member and proc — is PP-RULES's craft, which arbitrates where a rule belongs.

A law of production turns the document into a machine-checked contract; authors never write the checkpoint. The engine injects it before each `FINAL` — nothing leaves unproven — and on frame exit; no key arms it, no switch silences it. The proof names the codes at risk, at least one; a code unnamed is n/a; no active production law means silent checkpoint. Behavior laws bind the block and are never proven.

The proof itself, piped:

    ./pp <key> - <<'EOF'
    [{"code": "C1", "evidence": "judged line 12 on its own terms", "verdict": "ok"}]
    EOF

Coverage/shape are mechanical; evidence truth is kept honest by doctrine and audit sampling, never assumed.

### The overlay — deltas on a same-name document in a nearer space

    ---
    name: TURN
    constraints.production: |
      X1  every answer closes on the ask's status.
    ---

A same-named document in instance space (`.pp/TURN.md` or `.pp/procs/TURN.md`) is an OVERLAY, not a shadow: section DELTAS add laws (`X1`/`+X1`), remove laws (`-T4`), add offers (`+pp-authoring`, also adopting a harness skill), or remove offers (`-pp-authoring`). Kit TURN shows X1 from the next boot, under the section the delta named:

    ▌ [2] BOOT ▸ MEMBER ▸ TURN{2/4}
    …

    ▌ CONSTRAINTS
    production:
    X1  every answer closes on the ask's status.

Nearer applies later and wins: instance, package `overlays/`, package bases.

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
    …

    ▌ INSTRUCTION
    WORK free => chat

    ./pp <key> -s REVIEW

`tools:` lists step offers; `-s <name>` plays one THROUGH pp: pending block first, then a `proc:` door stacks under its laws, a script runs, or a bare contract opens as a step. Offers live with their output: place the call ON the step that needs it.

The block lists names; the catalog holds contracts. Offered names are in scope at this step; anything else is caught:

A harness-provided name can also be offered (`+name` in an overlay's `tools:`): pp lists/scopes it; the harness runs it.

A named skill through pp is ONE call: pending block first, work after. Out of block scope, work does not happen. Three kinds share this form: conducted (`proc:` skill), executed (script), served (augmented contract with neither — this guide). A script called BARE — no argument — does not run: pp mounts its manual, the contract of its verbs, and the run stands where it was (`tests/console/skill-gesture.py`). A gesture's output over the host's cap comes in chunks: the bare keyed call serves the next one, any other call bounces `chunk-pending` (`tests/engine/rendering/cut.py`).

Offers LIVE with their output. Fused outputs number headings; each segment owns ITS OWN list. Calls route under the owning segment's snapshotted laws; `-s <name>@<n>` resolves a tie; the next rendered output retires addresses. Place `tools:` on the step that needs the call.

### The described door — `field:`

    ---
    name: MONTH
    kind: proc
    description: close the month -- every account, then the total.
    proc: |
      CALL ACCOUNTS.md
      INFER
    ---

    Say the total once every account is closed.

    ---
    name: ACCOUNTS
    kind: proc
    description: one line per account, the accounts asked of the agent.
    field: |
      The accounts to close this month, one lap each.
    constraints.production: |
      L1  the lap's line names its account.
    proc: |
      INFER
    ---

    Close the account served under field: one line.

`field:` holds, in prose, what the door turns on; no skill is written; the door lives in `procs/` and is CALLed -- a `field:` elsewhere, or on a document without `proc:`, refuses `field-unplayable` at the build. At the door's entry the engine injects a step the agent sees as `INFER field`, the prose its brief; the answer is ONE JSON array judged on its form alone:

    ▌ MONTH ▸ ACCOUNTS{1/2}

    ▌ INFORMATION — MONTH
    Say the total once every account is closed.

    ▌ NEXT INSTRUCTION CONTEXT — field
    The accounts to close this month, one lap each.

    ▌ INFORMATION — ACCOUNTS
    Close the account served under field: one line.

    ▌ CONSTRAINTS
    production:
    L1  the lap's line names its account.

    ▌ INSTRUCTION
    INFER field => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -
       (your field on stdin -- heredoc: a JSON array)

    ./pp <key> - <<'EOF'
    ["north", "south"]
    EOF

    ▌ MONTH ▸ ACCOUNTS{2-3/3}

    ▌ INFORMATION — field
    north

    ▌ CONSTRAINTS
    production:
    L1  the lap's line names its account.

    ▌ INSTRUCTION
    INFER free => chat
    INFER proof [L1] on all produced areas => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -
       (your proof on stdin -- heredoc)

Accepted, the array is the field: each lap serves its head under `INFORMATION — field`, proves under the laws on screen, and the lap that closes drops it; an empty array opens no lap. The iterated door (`cycle: <token>`, above) is the same door with a skill as its iterator (`tests/engine/execution/cycle-described.py`).

### The workflow — `next:` and `choose:`

    ---
    name: ROUTE
    kind: proc
    description: open the stage, then say where it went.
    proc: |
      CALL STAGE.md
      INFER
    ---

    Say which way the stage went.

    ---
    name: STAGE
    kind: proc
    description: one step, then a fork.
    next: LEFT.md RIGHT.md
    choose: |
      LEFT when the draft is short, RIGHT otherwise.
    proc: |
      INFER
    ---

    Say how long the draft is.

    ---
    name: LEFT
    kind: proc
    description: the short way.
    proc: |
      INFER
    ---

    One line: the short way.

    ---
    name: RIGHT
    kind: proc
    description: the long way.
    proc: |
      INFER
    ---

    One line: the long way.

`next:` names the successors a document may leave to; several need a decider — `choose: |`, the prose the agent reads at an injected `PICK next`, the OPTIONS the names of `next:`. The decision comes at the exit, fused here with the step before it:

    ▌ ROUTE ▸ STAGE{1-2/2}

    ▌ INFORMATION — ROUTE
    Say which way the stage went.

    ▌ NEXT INSTRUCTION CONTEXT — STAGE
    Say how long the draft is.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ NEXT INSTRUCTION CONTEXT — next
    LEFT when the draft is short, RIGHT otherwise.

    ▌ OPTIONS
    LEFT.md
    RIGHT.md

    ▌ INSTRUCTION
    PICK next options => tool

    ▶ CONTINUE
    ./pp <key> <your-choice>

    ./pp <key> LEFT.md

    ▌ [1] ROUTE ▸ LEFT{1/1}

    ▌ NEXT INSTRUCTION CONTEXT — LEFT
    One line: the short way.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ [2] ROUTE{3/3}

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

The successor enters as a SIBLING — `ROUTE ▸ LEFT`, never `ROUTE ▸ STAGE ▸ LEFT`: an injected CALL in the caller's frame, the laws of the document that left gone with it, and the caller's own steps counted after it (`{3/3}`). A `next:` on the floor refuses `next-floor`; `decide: <verb>` asks the owner's skill instead of the agent (`tests/engine/execution/workflow-acyclic.py`).

### The contributor — `mount:` at a socket, `when:` its guard

    ---
    name: DOCK
    kind: proc
    description: let whatever is moored at `docked` enter, then unload.
    proc: |
      HOOK docked
      INFER
    ---

    Say what is unloaded.

    ---
    name: CARGO
    kind: doc
    description: enters at the dock, brings its law and its manifest, asks nothing.
    mount: docked
    constraints.production: |
      G1  every crate is named on the manifest.
    ---

    The manifest: three crates, one sealed.

    ---
    name: GATED
    kind: doc
    description: enters at the dock every n exchanges only.
    mount: docked
    when: "@SETTINGS.cargo_due"
    ---

    The customs form, due now and then.

Where `attach:` opens a frame that asks for a production, `mount: <socket>` HOSTS the document at the socket: its body, its laws and its offers ride the block that follows the HOOK, and it asks nothing. `when:` guards it like `^ @Doc.field` guards a CALL — here `cargo_due: 3` at SETTINGS, so GATED sits out the first exchanges:

    ▌ DOCK{2/2}

    ▌ INFORMATION — CARGO
    The manifest: three crates, one sealed.

    ▌ NEXT INSTRUCTION CONTEXT — DOCK
    Say what is unloaded.

    ▌ CONSTRAINTS
    production:
    G1  every crate is named on the manifest.

    ▌ INSTRUCTION
    INFER free => chat

    ▌ END
    …

The two entry verbs are exclusive (`attach-and-mount`); a mounted contributor re-enters at every lap of a cycling floor (`tests/engine/execution/hooks.py`).

### The frame's pace — `fusion:`

    ---
    name: STEPPED
    kind: proc
    description: two steps, one output each, whatever the instance fuses.
    fusion: none
    proc: |
      INFER
      INFER
    ---

    First the count, then the verdict.

A document's own `fusion:` pins its frame's pace over the instance's `instructions_fusion` — `max` here, and yet:

    ▌ STEPPED{1/2}

    ▌ NEXT INSTRUCTION CONTEXT — STEPPED
    First the count, then the verdict.

    ▌ INSTRUCTION
    INFER free => chat

    ▶ CONTINUE
    ./pp <key>

    ./pp <key>

    ▌ STEPPED{2/2}

    ▌ INSTRUCTION
    INFER free => chat

    ▶ CONTINUE
    ./pp <key>

### Played by the bench alone

Some mechanisms need a skill, a manifest or the host's cap, which a document alone cannot bring; the sheet cites them and names the scenario that plays them:

- `exec: <verb> [args]` — a skill of the document's owner played at every ENTRY, before the body (`tests/engine/execution/exec-at-entry.py`; the figure The entry act);
- `decide: <verb>` — the owner's skill prints the successor's name (`tests/engine/execution/workflow-acyclic.py`);
- `provides:` + `with:` and `payloads:` — a skill's output served as a section at the document that names the token (`tests/engine/execution/hooks.py`; the figures The contributor and The payload);
- `sink: <skill>` — the production handed to a skill on stdin, its `::push` back as a section (`tests/engine/execution/cycle-iterated.py`; SWEEP above);
- `order:` — a contributor's rank at a socket, against a PACKAGE; inert between two documents of one instance (`tests/engine/execution/hooks.py`, `exec-at-entry.py`):

    # SECOND.md, a contributor of the instance
    order: |
      boot.ready before witness

- `override:` — `true` on `SYSTEM_PROMPT.md`, the marble replaced (`tests/engine/packaging/marble.py`):

    # SYSTEM_PROMPT.md
    override: true

- `./pp <key> -disable <package>` · `-enable` — one package out of the run's play, said under every output's heading (`tests/engine/execution/package-switch-run.py`);
- the chunks — an output over `max_harness_tool_output` comes in pieces, the bare call serving the next, any other call bouncing `chunk-pending` (`tests/engine/rendering/cut.py`, `tests/console/gesture-cut.py`).

### The miss — the named correction

A watched miss reopens the WHOLE document at its first instruction, names the miss, and preserves the count:

TRIAGE, above, answered its PICK outside the OPTIONS:

    ./pp <key> - <<'EOF'
    ["approve", "revise", "reject"]
    EOF

    ./pp <key> maybe

    ▌ TRIAGE{1/2} · REPAIR 1

    ▌ DEVIATION
    `maybe` is not in OPTIONS (approve, revise, reject). Take one of them, verbatim.

    ▌ INSTRUCTION
    INFER json => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -   (your <output> on stdin -- heredoc)

At `work_repairs_allowed`, the conductor stops repairing and returns the operator. Only WATCHED moves count; status calls do not.

### The operator's own — ASK, VERBATIM, GATE and TUNING

The operator's message is the brief; turn WORK serves it. pp never makes the operator repeat: their words reach the agent through the harness, not a block.

    # SETTINGS.md
    capture_prompt: true

FINAL asks for the operator's next message itself; the trace keeps their uninterpreted words — decision spoken, not understood.

Approve, reject and GO belong to the operator, never the agent. A proc reaching a gate goes FINAL; working an unapproved request is contractually out of bounds.

Between exchanges the operator edits their own `SETTINGS.md`, `FORMATS.md`, `MEMBER.md`, `procs/`, overlays. Invalid values refuse before anything plays and name the reason. Bundles are never edited: customize by redeclaring at home. A package is switched off without leaving: `package.<name>: on|off` at SETTINGS for good, `./pp <key> -disable <package>` / `-enable` for one run, placed by the agent on the operator's word — nothing of it plays, and every package requiring it goes with it (`tests/engine/execution/package-switch-run.py`).

### The conventions — BLOCKED and RECALL

When the required form is untenable, answer `#BLOCKED <reason>` in chat and stop. This is convention, not mechanism; the operator takes over.

Every transition — first `-new`, continuation, keyed advance, call after FINAL — is agent initiative. Nothing forces it; doors, standing rules, the `▶` exact command, and every offered name being a pp entry secure it. Even a misplaced call recalls: pending block answers, nothing plays, nothing counts.

## 4. The forms at a glance

Every form one line of front matter or `proc:` puts in play, with the guarantee the engine gives it; the section above that plays it is named by its keyword or its pattern.

| Form | You declare / it happens | Guarantee |
|---|---|---|
| READING | `serve:` sections, `SERVE` | mechanical (chunk; each continuation costs a recall) |
| HOSTING | `mount: <socket>`, or `-mount <doc>` / a skill's `::mount` — laws/offers/rows in force, no frame | mechanical, one exchange |
| CONTEXT | body of the `proc:` document | mechanical |
| LAW | `constraints:` | mechanical, re-emitted while frame lives |
| OFFER | `tools:` | mechanical scope |
| MISS | watched miss | mechanical, bounded (`work_repairs_allowed`) |
| SIGNAL | closing — flow decides it | mechanical |
| ELECTION | `PICK` | mechanical on the form |
| PRODUCTION | `WORK`/`INFER`, not consumed | framed, never guaranteed |
| FEED | `WORK`/`INFER` consumed downstream (`input:`) | mechanical on the form |
| SELF-PROOF | the checkpoint — every document with a law of production | mechanical coverage |
| BLOCKED | `#BLOCKED <reason>` | convention |
| RECALL | each agent call | good will, secured |
| GESTURE | named skill | free initiative, mechanical scope |
| DUE | `^ @Doc.field` | mechanical cadence |
| WAKE | engine start injection | mechanical |
| ASK | the operator's message | — |
| VERBATIM | `capture_prompt: true` | mechanical capture |
| GATE | approve / reject — the operator's GO | contractual |
| TUNING | operator files between exchanges | mechanical (invalid refuses) |

## 5. The front matter, key by key

| Key | Declares | Notes |
|---|---|---|
| `name` | identity | skill-directory name IS identity (`SKILL.md` is the form) |
| `kind` | `proc` · `doc` · `boot` | classification; `doc` never executes |
| `description` | catalog line | menu text; required when offered |
| `proc:` | flow, one keyword/line | presence makes it CONDUCTED |
| `output:` | production form | formats-enumeration NAME; unknown refuses |
| `input:` | consumed form | caller adjacent production becomes captured FEED |
| `serve:` | reading sections | one paragraph/bare `SERVE`; multi-line/docs allowed; without SERVE unread; document proven once/run; a token is `DOC`, `DOC[start..end]` (two tags, each the start of a line) or, as a last resort, `DOC[x-y,…]` |
| `tools:` | frame offers | `+name` adopts harness skill; overlay `-name` removes |
| `constraints.production:` | checkpoint laws, `CODE  text`/line | what agent MAKES; ONE line/law; wrapping parses a new code |
| `constraints.behavior:` | served, unproven laws | what agent does/says/reads; bare `constraints:` refuses (`constraints-unsectioned`) |
| `formats:` | `name  mode  description` | extends enumeration; redeclaration overrides |
| `attach:` | HOOK socket | CALLed wherever hook plays, after manifest hooks there; a socket orders its contributors by the requires topology of their HOMES, and between SIBLINGS by the pins' order — never by the document's name |
| `mount:` | socket the document ENTERS | hosted at its socket — no frame, no `proc:` owed; exclusive of `attach:` (`attach-and-mount`) |
| `provides:` | token this document SERVES | paired with `with:` — one without the other refuses (`contribution-malformed`); the token wears its package's name, another's is JOINED under ITS prefix (`name-unprefixed`) |
| `with:` | `<skill> <args>` serving the token | a skill of the document's OWN package — a foreign name refuses (`with-foreign`); two packages sharing a skill name refuse (`skill-taken`) |
| `order:` | `<hook> before\|after <package>` | a contributor's stated rank at a socket: the derived topology first, preferences over it; a preference toward a package the composition lacks is inert, two that each want to be first refuse `order-cycle` |
| `exec:` | `<verb> [args]` — a skill played at every ENTRY | the `pp-<package>` of the file's own package (an instance document names one of its own skills first: `exec: <skill> <verb>`), once per CALL, mount or lap, before the body and before anything served; a `@Doc.field` argument takes the value a guard would read, never empty; a non-zero exit refuses `exec-refused` and nothing enters; its output goes to the bus alone (`::push`, `::clear`; a `::mount` refuses `exec-mount`) |
| `when:` | `"@Doc.field"` (quoted YAML) | contributor switch/cadence, judged like `^ @Doc.field`; socket knows no key |
| (manifest) `cadences:` / `checks:` | `{name, anchor: "@SETTINGS.<key>", record, play, at[, since]}` / `{signal, predicate: record-crossing, record, anchor}` | socket document / boot signal when anchored weekday crosses record |
| `payloads:` | space-separated tokens the document CONSUMES | providers found by scanning the composition's DOCUMENTS; each runs and lands as `INFORMATION — <token>`; a token of another package is named under ITS prefix |
| `sink:` | the skill the production is handed to | one per document: a `WORK`/`INFER` production reaches it on stdin, its `::push` / `::clear` return as a block section |
| `cycle:` | `true` = session floor · `<token>` = iterated door | exhaustion rewinds and sweeps the mounts · exhaustion asks the token: a lap per element (payloads re-resolved, mounts kept, each lap proven), the exit when nothing is due; `cycle-unprovided` when nobody provides |
| `field:` | the DESCRIBED door | the prose of what the door turns on — its presence declares the door; the engine asks the agent for the field once (`INFER field`, a JSON array judged on its form), then serves one element per lap under `field`; never beside `cycle:` (`cycle-and-field`) |
| `next:` | the SUCCESSORS the document may leave to | names as `CALL` writes them; one follows alone, several are decided at the exit and the one elected enters the caller's frame as a sibling CALL; the graph of the composition is acyclic (`next-cycle` at the build) |
| `choose:` / `decide:` | the decider of a `next:` of several names | `choose: \|` the prose the agent reads at a `PICK next`, `decide: <verb> [args]` the owner's skill that prints the name; one of the two, never both (`choose-and-decide`) |
| `fusion:` | `max` · n · `none` | frame pace over instance |
| `override:` | `true` on `SYSTEM_PROMPT.md` | composes replace artifact — lock, otherwise retracted |

Any text file is SERVABLE whole — there is no terminal marker; the hash pp computes on what it serves proves what was served.

The `proc:` language is `PICK <name>` · `SERVE` · `CALL <doc>` · `HOOK <name>` · `WORK` · `INFER` · `FINAL`; plus lone `§` (fusion never crosses this section break), `# ` comments (uncommenting arms them in `proc:` and constraints), and guard suffix `^ @Doc.field` (declared cadence). Two steps the ENGINE injects and no author writes: `INFER field` at a described door's entry and `PICK next` at the exit of a document with several successors — written `FIELD` or `NEXT` refuses at parse (`field-keyword`, `next-keyword`), like the checkpoint no author writes. `PROVE` and `prove:` are gone: the checkpoint needs no key, and a document still carrying `prove:` refuses `prove-gone` at its opening.

## 6. SETTINGS, key by key — engine default ⟂ seed

| Key | Engine default | Template seeds | Observable effect |
|---|---|---|---|
| `conduction_effort` | — | `medium` | SIZE: `none` no preset ⟂ `light` ⟂ `medium` ⟂ `full`; presets weight knobs (`verbatim_constraints`, `instructions_fusion`, `proc_body_serve`, `capture_prompt`, package additions) |
| `instructions_fusion` | `none` | `max` | one step/block ⟂ capped ⟂ one output/certain stretch (`max`) |
| `verbatim_constraints` | `true` | `true` | full text/block ⟂ text at the run's first emission, codes after |
| `capture_prompt` | `false` | `false` | FINAL resume carries/traces operator message; medium and full preset `true` |
| `max_harness_tool_output` | 25000 | 25000 | host cap per tool output; engine cuts below it |
| `proc_body_serve` | `always` | `always` | CALLed body every CALL ⟂ `once`/run by content; later CALL empty; light and medium preset `once` |
| `work_repairs_allowed` | 3 | 3 | MISS bound before operator handback |
| (a package's keys) | — | — | package settings-fragment keys, documented there |

Absent file/key → engine default. Invalid values refuse before work. Template seeds documented values; instance edits belong to the operator from day one. Conductor and kit are ONE system: bare keys, documented once in template. A PACKAGE BEYOND declares prefixed keys (e.g. `plan_`) in `settings/SETTINGS.md`, including defaults, `types:`, `effort:`/`role:` presets and its body SECTION. Sync composes the instance file from system template + fragments in requires topology while preserving operator values.

## 7. The figures — what a package makes of the forms

A figure is cited, never played here: each one shows its real employer's lines or the bench door that plays it, and names that door -- the mechanism's proof is the scenario, the example is the package's own file.

The served `CONDUCTION` says WHEN to choose each figure — where a piece of work comes from and where it is played; this catalog says how each one is written.

Two catalogs, two axes. The FORMS above are the raw material: what one line of front matter or `proc:` puts in play. A FIGURE is the shape a whole package document takes to enter the flow — it composes several forms toward one intent. Sixteen figures cover the eight shipped packages (survey: `plans/pp-split/PATTERNS.md`, 2026-09-01); each entry says what the author writes, what the engine guarantees, and cites a real employer as written. Two qualifiers — the guard and the order preference — cross several figures and close the catalog.

### The conducted step — hook the turn, ask for a production

A document that attaches to a socket and ASKS the agent for a production of its own. The author writes `attach: <socket>` and a `proc:` with at least one yielding keyword (`WORK`, `INFER`, `PICK`). At the socket's HOOK the engine gathers the contributors — declared and attached — orders them by the requires topology of their homes then by `order:` preferences, and injects one CALL each: the frame adds its laws over the caller's, its block renders while it lives, its `output:` names the form. Real, `steering/procs/NEXT.md` — the surface that closes every exchange:

    attach: turn.end
    proc: |
      INFER

Choose it when the package needs the AGENT to produce at a moment of the turn.

### The contributor — enter the socket, bring, ask nothing

A document that ENTERS its socket and brings — its body, its rows, its payloads — and asks nothing: no `proc:`. The author writes `mount: <socket>`, what it consumes (`payloads:`) and what it serves (`provides:` + `with:`). Hosted at the socket, its body and matter compose in the CALL's order, its laws ride every block and are owed at the checkpoint, its offers join TOOLS; the next rewind sweeps it, the socket brings it back each turn; `when:` guards it like any callee. `attach:` cannot say this — a CALL opens a frame that expects a production. Real, `continuity/procs/RECALL.md`, its whole declaration:

    mount: boot.ready
    provides: continuity-recall
    with: pp-continuity recall
    payloads: continuity-recall

Lineage: before `mount:` the four employers invented one dead socket each and could not even declare a law — the one figure whose mechanism was a workaround; the verb closed it (2026-09-01).

### The door — a proc offered by name, opened on the operator's word

An ordinary proc (`SERVE` then `WORK`, or `WORK` alone), never attached; its name enters a `tools:` — the member's, or an overlay's `+name`. The block lists the offers in scope; the agent plays `./pp <key> -s <NAME>` and the proc stacks over the pending step — one door at a time, on the operator's GO. Real, `authoring/overlays/BOOT.md`, whole:

    tools: |
      +PP-MEMBER
      +PP-RULES
      +PP-OFFERS
      +PP-MIGRATE
      +PP-DESIGN

### The mounted step — a skill hosts a document by directive

A `kind: doc` document without `proc:` — never played — that a SKILL hosts by printing `::mount <json>` on its stdout; the console harvests the directive and the HOSTING above happens: body as brief, laws in force — the document's own and its overlays' deltas, as for a frame —, rows served; the agent's keyed call closes it. The socket's door is the contributor; this is the gesture's door — same hosting, different trigger. Real, `packages/plan/skills/pp-plan/pp-plan.py` mounting a plan chain:

    print("::mount " + json.dumps(chain))

### The overlay — a mode over a floor you do not own

Prose, law deltas, offer deltas and READINGS on a same-named document another package owns. The body joins the base's composition (deep packages first, the user last); the deltas (`+CODE text` / `-CODE`, `+name` / `-name`) apply to the base's frame; the `serve:` rows ADD readings to the base — served whole as the base enters, in application order, each titled by its token, `+` optional, no `-` (`overlay-serve-removal`): the way a package hands the agent a doctrine at the turn without owning TURN (`plan/overlays/TURN.md` serves `+PLAN_CHEATSHEET.md`). An overlay carrying `proc:` refuses (`overlay-carries-proc`); an idle delta refuses (`overlay-adds-existing`, `overlay-removes-nothing`). Its limit counts: an overlay has NO guard — a conditional law cannot ride one. A mount reads the overlays of the base it hosts, like a frame would (`tests/engine/execution/mount-overlays.py`). Real, `improvement/overlays/TURN.md`, whole:

    tools: |
      +UPKEEP
      +pp-improvement

### The payload — a skill's output served as a section

The matter door. A provider document declares `provides: <token>` and `with: <skill> <args>`; a consumer declares `payloads: <token>`; one document may do both. At frame entry — or when a mounted document enters — the engine resolves EVERY provider of each consumed token by scanning the composition's DOCUMENTS in requires topology, runs each skill and serves its output under `INFORMATION — <token>`. A provider is DATA — it serves without being in flight; an empty output renders nothing; a refusing skill is said in the section and the turn continues. One token, several providers, contiguous sections — the merged view is the mechanism, not an exception. Provide only a token your own package's name prefixes; consume any token of a package you require. Real: `steering-threads` is provided by `steering/procs/NEXT.md` (`with: pp-steering status`) and consumed by `improvement/procs/IMPROVE.md` and `federation/procs/WEAVE.md`; `WEAVE.md` also provides and consumes its own `federation-weave` (`with: pp-federation weave`).

### The sink — the production handed to a skill

The author writes `sink: <skill>` on a document whose `WORK`/`INFER` production should land in a record: the production reaches the skill on stdin; the skill owns its grammar — the engine never reads it — and answers through printed directives (`::push`, `::clear`); what it says returns as a block section. One sink per document. Real, `improvement/procs/IMPROVE.md`:

    sink: pp-improvement

### The iterated door — a token turns a proc into laps

The author writes `cycle: <token>` on a proc with a law of production of its own, and a `sink:` that consumes what a lap produces. At the CALL the engine asks the token's providers BEFORE the body: nothing due, no lap opens and the line under the token says it; an element, the body is served and the frame opens with the element under `INFORMATION — <token>`. Exhausted, the frame asks again: an element, a lap — the instructions back to the first step, the `payloads:` re-resolved, the mounts kept, the lap proven under every law on screen; nothing due, the frame leaves like any callee, its last production to the caller. The iterator is a REQUEST: the providers render what remains due, the engine keeps no count, the accepted production moves it; a provider that refuses ends the cycle, said on the block that follows; a token nobody provides refuses `cycle-unprovided`. Real, the engine's bench `tests/engine/execution/cycle-iterated.py` (`DOOR.md`), until the doc package's sweep takes it:

    cycle: laps
    sink: pp-laps

Choose it when the agent must produce ONCE PER ELEMENT of a list a skill knows, under the same laws, without a cursor at the engine.

### The described door — the field asked of the agent

The author writes `field: |` on a proc with a law of production of its own: the prose of what the door turns on, `@Doc.field` references allowed (one resolving to nothing refuses `field-argument-empty`). No skill is written. At the door's entry the engine injects a step the agent sees as `INFER field => tool (heredoc)`, the prose its brief: the answer is ONE JSON array judged on its FORM alone — valid, scalars none empty, each once, 200 at most — never on what an element is. Accepted, the array is the field, held by the frame as what remains due: each lap serves the head under `INFORMATION — field`, the lap that closes drops it, a rewind never touches it, a compaction re-serves its head; an empty array opens no lap and the door leaves like any callee. `field:` beside `cycle:` refuses `cycle-and-field` at the build, an empty key `field-empty`, a document the engine never CALLs `field-unplayable`, a written `FIELD` `field-keyword`. Real, the engine's bench `tests/engine/execution/cycle-described.py` (`DOOR.md`):

    field: |
      The words of @LIST.items, one lap each.

Choose it when the list to walk is something the AGENT can enumerate from what it is served — the iterated door above when a skill knows it.

### The workflow — the successor decided at the exit

The author writes `next:` on a proc: the SUCCESSORS it may leave to, document names as `CALL` writes them — the edges of a workflow. One name follows without a decision. Several need a decider, one of two: `choose: |`, the prose the agent reads — the engine injects a step seen as `PICK next options => tool`, the prose its brief under `NEXT INSTRUCTION CONTEXT — next`, the `OPTIONS` the names of `next:`, a name outside them a miss that repairs; or `decide: <verb> [args]`, the owner's `pp-<package>` skill that prints the one name (a name outside `next:` refuses `next-foreign`, a non-zero exit `next-refused`). The decision comes after the exit checkpoint, and the successor enters as a SIBLING: an injected `CALL` in the caller's frame, right after the one that just resolved — the laws of the document that left fall with it, the root's hold on the whole path, and the production of the one that left is the successor's upstream (its seed, under `input:`). A successor declares its own `next:` in turn; a rewind or a repair of the caller purges the injected CALLs. The build judges the graph of the whole composition: a loop refuses `next-cycle`, several names without a decider `next-undecided`, both deciders `choose-and-decide`, a decider under fewer than two names `decision-idle`, a name nowhere `reference-unknown`, an edge whose `output:` and `input:` differ `format-mismatch`; a written `NEXT` refuses `next-keyword` at parse, a `next:` on the floor `next-floor`. Real, the engine's bench `tests/engine/execution/workflow-acyclic.py` (`A.md`, then `A2.md` deciding by skill):

    next: B.md C.md
    choose: |
      B when the batch is @LIST.choices, C otherwise.

    next: B.md C.md
    decide: next

Choose it when a document's exit picks which document plays next — ten steps in a row never stack ten frames.

### The entry act — a skill played when the document enters

The author writes `exec: <verb> [args]` on a proc or a mounted document: the engine plays the `pp-<package>` skill of the file's OWNER once at every ENTRY — a CALL, a mount, each lap of an iterated door — before the body and before anything the frame serves; never on `-peek`, a chunk, `-compacted`, a repair or the floor's rewind. An instance document names one of the instance's own skills first (`exec: <skill> <verb>`). Arguments pass as words; a `@Doc.field` takes the value a guard would read, an empty one refuses `exec-argument-empty`. A non-zero exit refuses `exec-refused`: the frame is not pushed, the mount is not written. What the skill prints goes to the bus alone (`::push`, `::clear`) — an exec PREPARES, it serves nothing; a `::mount` refuses `exec-mount`. The base and each overlay of a document may declare their own, each playing its own package's skill, in the requires order of their homes, re-ordered by `order: exec before|after <package>`. A document the engine neither CALLs nor mounts refuses `exec-unplayable`. Real, the engine's bench `tests/engine/execution/exec-at-entry.py` (the witness package `alpha`, its document `ENTRY`):

    exec: stamp @ALPHA.mode @SETTINGS.alpha_mode plain

Choose it when a record must be brought up to date, or a signal pushed, at the very moment a document enters — before the agent reads anything.

### The cadence — a document played when a crossing is due

At the manifest, `cadences:` — `{name, anchor: "@SETTINGS.<key>", record, play, at [, since]}`. At each HOOK the engine asks whether the anchored weekday has been crossed since the record's last entry (and the `since` record moved); if due, the `play` document is CALLed after the socket's contributors. `anchor: never` extinguishes it; an unresolvable `play` is said at the trace and skipped — a cadence never breaks a boot. Real, `continuity/package.yaml`:

    cadences:
      - {name: history, anchor: "@SETTINGS.continuity_history_day", record: history.jsonl,
         since: operations.jsonl, play: HISTORY.md, at: boot.ready}

### The check and the signal — a predicate feeds the bus

At the manifest, `checks:` — `{signal, predicate, record, anchor, home}` — and the bus data under `events:`. The engine knows no signal, sector or family by name: a generic predicate evaluates each check and pushes its signal to the bus, which HOLDS the entry, arbitrates by declared priority then count, and serves under the sector's cap; `./pp acquit <vector>` clears a counter and its entry in one call. Real, `authoring/package.yaml`:

    checks:
      - {signal: member-bare, predicate: fingerprint, home: MEMBER.md}

**The events a package declares** — a package feeds the instance BUS as DATA through `package.yaml` under `contributes:`:

    contributes:
      events:
        sectors:
          review: {cap: 2, icon: 🔎}
        vectors:
          review: {verify: pp-review}
        signals:
          review-idle: {door: REVIEW, at: gesture:review-scan, sector: review, priority: 1}

`vectors:` declares projection families and their VERIFIER: `verify` names the package's own skill the engine runs at every entry of the bus (push, stand) and at the service (a latch whose vector no longer verifies drops) -- the verb `verify`, the whole vector on stdin, rc 0 says valid, any other says no with its reason (`vector-unverified`, nothing written). **No vector without its verifier**: a bare family refuses at the build (`family-unverified`); the engine holds no referential, the package that owns the nodes answers. The family's DESCRIPTION to the agent never rides the manifest (structures only): a TURN overlay of the package carries it in its body. `signals:` declares motor output: `door` is the outlet; `threshold: n` or `"@SETTINGS.<key>"` (a key owned by the package fragment) makes a counter, absence a predicate; `at: gesture:<skill>` is the codeless motor pushed when that call plays. Undeclared pushes refuse. The bus-serving step (with improvement package, IMPROVE) serves only crossed signals, ARBITRATED by `sectors:`. Each package owns its sectors: `cap` limits served lines (e.g. 2 unsaid); `icon` leads each, or sector name if absent. A signal's `sector:` must name one of ITS OWN sectors; none falls into the package's ONE `default: true` sector. `priority:` sorts within a sector: smaller first, absent last, then count. Sector names belong to their declarant: collisions refuse; foreign claims refuse unowned.

### The package command — a bare console verb

At the manifest, `commands:` — `{verb, skill, args}`. The console resolves a bare verb AFTER the system verbs and before a run key: it launches the declared skill in a subprocess with the manifest's args then the operator's, relays the output, returns the code as is — the engine imports no package code. `./pp help` composes the system verbs then each declared command; a colliding verb refuses at build (`command-taken`), one wearing no package's name too (`name-unprefixed`) — `doc` below is the package's own name. Real, `doc/package.yaml`:

    commands:
      - {verb: doc, skill: pp-doc}

### The writer skill — one script, one record, under lock

A deterministic script, its card (`SKILL.md`), and the few-line vendored `skills/_core.py` to reach the engine's face. The skill is the ONE writer of its record: every write rides one primitive (`state.record`) — file lock, the read INSIDE the lock, the change, an atomic replace; a reader never blocks and never takes the lock. Guards refuse by name, exit 2, nothing written; a budget guards every entry. Real: every package skill vendors `_core.py`, whose brief opens on the walk — "`home(start)` walks up from the CALLER's own file". A skill the engine launches — a provider, a sink, a verifier, an `exec:` — knows its run: `conductor.context.current(home)` gives `key`, `exchange()`, `is_new()` and `is_boot()`, reads the slot and writes nothing.

### The settings fragment — prefixed keys, read through the face

`settings/SETTINGS.md`, `kind: fragment`, `package: <name>`: keys PREFIXED by the package's name, a `types:` block, an `effort:` block where levels differ. The instance's SETTINGS is COMPOSED — the system's bare keys first, then one named section per package in requires order; an unparsable value refuses by name. A skill reads its key through the face and gets the EFFECTIVE value, effort presets included; removing the package leaves its keys `unowned` so a later `add` recovers the operator's values. Real, `continuity/settings/SETTINGS.md`:

    kind: fragment
    package: continuity

### The two qualifiers — guard and order

`when: "@Doc.field"` on an attached or mounted contributor: the injected CALL inherits the guard — the mechanism that silences a package without removing it (`federation/WEAVE` under `federation_coordinator`). An overlay has no guard. `order: <socket> before|after <package>`: a contributor states its own rank at a socket, beating the derived topology — `improvement/IMPROVE` declares `order: turn.end before steering` so its lines are held before the surface renders them. The client declares its order; a provider never names its clients.

## 8. The doctrine — what each piece IS

### The review gate — one exchange, complete

A sequence chains one EXCHANGE out of the forms: reading, a closed verdict under law, the proof owed at the exit -- PICK elects from the production BEFORE it (INFER's list becomes OPTIONS):

    ---
    name: VERDICT
    kind: proc
    description: judge a draft, hand ONE verdict.
    output: json
    constraints.production: |
      C1  you judge the draft; you never rewrite it.
      C2  a finding without the line it comes from is no finding.
    serve: |
      DRAFT.md
    proc: |
      SERVE
      INFER
      PICK verdict
    ---

    Say the findings with their lines, then list the allowed verdicts — approve, revise, reject — as a JSON array; elect ONE.

    ---
    name: DRAFT
    kind: doc
    description: the draft under review.
    ---

    The introduction restates the abstract; section 2 buries the headline number.

    ▌ VERDICT{2/3}

    ▌ INFORMATION — DRAFT.md
    The introduction restates the abstract; section 2 buries the headline number.

    ▌ NEXT INSTRUCTION CONTEXT — VERDICT
    Say the findings with their lines, then list the allowed verdicts — approve, revise, reject — as a JSON array; elect ONE.

    ▌ CONSTRAINTS
    production:
    C1  you judge the draft; you never rewrite it.
    C2  a finding without the line it comes from is no finding.

    ▌ INSTRUCTION
    INFER json => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -   (your <output> on stdin -- heredoc)

    ./pp <key> - <<'EOF'
    ["approve", "revise", "reject"]
    EOF

    ▌ VERDICT{3/3}

    ▌ CONSTRAINTS
    production:
    C1  you judge the draft; you never rewrite it.
    C2  a finding without the line it comes from is no finding.

    ▌ OPTIONS
    approve
    revise
    reject

    ▌ INSTRUCTION
    PICK verdict options => tool

    ▶ CONTINUE
    ./pp <key> <your-choice>

The PICK's OPTIONS are the array the INFER produced; the laws ride every block of the frame, and the frame's exit owes their proof.

### The lived doctrine — what each piece IS, and what died proving it

The product's retakes refined every piece; this is the residue carried by that history.

- **A constraint** is positive, short, against real model drift; it belongs in production or behavior, and a production law names whether proof covers whole, sample or trace fact. When it COUNTS, make it mechanical or measured. Proof honesty as prose produced 5 900 ok for 3 fail; it changed only when verdicts, evidence form and repair incentive became mechanics. Dead: maxim, negative wording, engine-vocabulary clause in a proc body, undeclared drifting form.
- **A body** is served savoir-faire — brief, worked examples (indented, never fenced), method. Never law (body reads once; law re-arms every block), never a mirror of another document (three mirrors lived and died), never dated state: artifact says PRESENT; trajectory lives in records.
- **A proc** is one métier with a declared frontier: free WORK, guarded CALLs, enumeration closing. Never another motif's envelope (`PROVEN_INFERENCE` died inlined, lived as a `prove:` key, and returned as the engine's own checkpoint), never a scheduled element (ADVISOR/mentor died: periodic need became dated due over append-only record or one-line turn reflex). Step POSITION is normative: steering restitution closes on NEXT; continuity consignation closes the turn.
- **A scripted skill** is the ONE writer of its record: named calls, named stderr refusals, atomic writes, guarded budget, hermetic bench. Script owns structure; agent owns prose. Template titles the born document; piped prose starts at content.
- **A ref** is served knowledge — by section/SERVE or mount — never played; **an overlay** is one package's mode over another's floor: deltas only.
- **A format** is a NAME in pp's enumeration. Stable restitution DECLARES its format: steering NEXT drifted three weeks under doctrine alone and stabilized when its form was declared.

### Prove it mechanically

`-build` compiles the catalog and refuses lies — doubled constraints, bare `constraints:` (`constraints-unsectioned`), unhooked attaches, unknown formats — and lints forgotten productions. `-peek` renders what a real call would show without effect; `-test` runs engine fixtures; a real install plays the document end to end. Whose document it is decides the SEVERITY: a defect in YOUR instance's documents warns and the build passes (`pp: WARNING -- …`, the offending line simply not in force), the same defect in a package's refuses by name. The bare `constraints:` key refuses on both sides — the migration gate, not a law defect.
