---
name: PP-DESIGN
kind: proc
description: >-
  The proc author's pp-conducted guide: every interaction form with a worked example — declaration, dynamics, rendered block — plus composition rules, active and proven while authoring. Call it before writing or revising any conducted document.
output: free
constraints.production: |
  PD2  the LLM initiatives per turn are counted -- equal result, the lower count wins.
  PD3  conducted or neutral: the intended initiative alone decides.
  PD4  the new lives in content alone -- a served example indents, four spaces.
  PD5  constraints short, load-bearing first.
  PD7  an authored document says the PRESENT -- the trajectory lives in the RECORDS, the artifact says what is.
  PD8  a document speaks its OWN layer's concepts -- a word from an upper layer in a brief is a leak.
  PD9  a rule that COUNTS is made mechanical or measured -- bare doctrine erodes under the model's drift.
  PD10  a periodic need is a dated due or a one-line reflex on an existing step -- the instance stays as is.
constraints.behavior: |
  PD1  a new proc is described by its forms before it is written.
  PD6  an authored document is proposed, and installed on the operator's GO alone.
serve: |
  PP_CHEATSHEET.md
  CONDUCTION.md
proc: |
  SERVE
  WORK
---

# `PP-DESIGN` — composing procs

> **The user SDK — the author's face of pp.** This guide teaches how to WRITE conducted documents. The agent's contract for CONSUMING blocks is the `pp` card in the standing rules: nothing here is needed to play an on-screen block, and nothing here becomes an agent reflex.


Worked examples — every instruction's happy path and the patterns that count — are in the served `PP_CHEATSHEET`; each plays as written and the kit bench plays all.

Every rule has LINEAGE in the product's narrative history: what died and what held are named with why; theory remains only where lived experience confirmed it.

A proc's front matter (plain YAML, one flat mapping) DECLARES what the conductor guarantees; its body carries the brief. Describe its FORMS first, then write declaration, then prose. Every form and example follows. Commands are the member's own (`./pp`, workspace console; shortened here to `pp.py`); block excerpts use `…` for engine-filled content.

## The catalog — every form at a glance

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

## What the tool serves

### READING — the tool reads for the agent

    serve: |
      STYLE.md GLOSSARY.md
    proc: |
      SERVE
      INFER

One bare `SERVE` dequeues one whole SECTION of `serve:` — one paragraph, all its lines/documents. Blank lines separate sections: n sections require n SERVEs, in order. The section DECLARES; SERVE is the MOMENT: without it the section is unread; one past the last refuses (`serve-exhausted`). They travel together, normally at proc HEAD. A `CALL` never plays the callee's section: it serves only its BODY; that section waits for its OWN bare SERVE. ONE reader handles every site — section line, mount row, CALLed body — chunks at budget and proves each document ONCE/run by content. Naming it again via another section, `SERVE <doc>`, mount or CALL renders NOTHING; the agent retains/proves nothing itself. Content appears under the row TOKEN, including written path/range (`design/target.md`, `GLOSSARY.md[1-2]`), so same-named files remain distinct; CALLed bodies retain the document name:

    ▌ INFORMATION — STYLE.md
    …the document's text…

Long readings continue across calls: each continuation gets bare recall (`▶ CONTINUE`) and arrives untitled; the delimiter appears once. A token may include ranges (`file.py[10-40]`): convenience, never maintenance duty. Stale ranges clamp; gone documents skip with a note; `serve-stale` signals either, so nobody maintains ranges manually. A line's first token may declare its NATURE; the regime grades line by line. A document without `proc:` serves its section through the mount below.

### HOSTING — the mount

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
    …

    ./pp <key> -mount '[{"doc": "NODE.md", "scope": "nested", "body": true}]'

A document without `proc:` — plan node, framing, ref — carries laws, offers and readings but no flow: CALL has nothing to play there, and stacked frames would create nesting the flow never walks back through. A mount HOSTS it beside the pending step: `constraints:` bind every block, `tools:` joins offers, `serve:` rows play on the call (soft serve-budget cap; gone file skips with note), and body comes when requested. No frame; it lasts ONE exchange and the next rewind removes all mounts.

    ▌ [1] FLOOR ▸ NODE

    ▌ TOOLS
    [pp-authoring]

    ▌ INFORMATION — NODE
    …

    ▌ CONSTRAINTS
    N1  the node's law binds every production under it.

    ▌ [2] FLOOR{1/2}

    ▌ INFORMATION — STYLE.md
    …

A document also enters a SOCKET by its own front matter — `mount: <socket>`, exclusive of `attach:` (`attach-and-mount` refuses at build): hosted at its socket every turn, no skill, no directive — the figures below (the contributor, the mounted step) say when each door fits.

Each JSON entry selects `body`, `constraints`, `tools`, and `scope`: `nested` creates a numbered node scope addressable like a fused segment; `stacked`, default for a bare path, accompanies the pending frame. A script run with `-s` may mount in the same call through stdout `::mount [...]`, bringing an entire plan chain (plan, phase, batch) into force at once. Whatever a framing establishes on its node, every mount reads.

### CONTEXT — the privileged brief

The BODY carrying the pending instruction is promoted above ordinary reading — the ask's own brief:

    ▌ NEXT INSTRUCTION CONTEXT — REVIEW
    Judge the draft against the checklist; verdicts are yours alone.

Write a `proc:` body as its brief: one concern, addressed to whoever acts now. It arrives on CALL through the same reader and is proven by content. With `proc_body_serve: once`, once proven in the run it renders nothing on later CALLs: brief once, laws every block. `always` forces it back on every CALL.

### LAW — the rule that never fades

    constraints.production: |
      C1  verdicts are yours alone — the draft's own claims prove nothing.
      C2  cite the line you judge.

Laws live in TWO sections: `constraints.production` governs what the agent MAKES and is proven at checkpoints, its text naming whether rendering covers whole, sample or trace fact; `constraints.behavior` governs what it does, says or reads, is served every block and never proven. Bare `constraints:` refuses at parse (`constraints-unsectioned`). Both appear with EVERY block while their frame lives, under ONE title, production first, and disappear with the frame:

    ▌ CONSTRAINTS
    C1  verdicts are yours alone — the draft's own claims prove nothing. C2  cite the line you judge.

Constraints ACCUMULATE: a CALLed document adds its own over its caller's. Placement — MEMBER › proc › overlay › kit › dead, with plan-package nodes between member and proc — is PP-RULES's craft, which arbitrates where a rule belongs.

### OFFER — the perimeter of free will

    tools: |
      pp-authoring

The block lists names; the catalog holds contracts. Offered names are in scope at this step; anything else is caught:

    ▌ TOOLS
    [pp-authoring pp-design]

A harness-provided name can also be offered (`+name` in an overlay's `tools:`): pp lists/scopes it; the harness runs it.

### MISS — the named correction

A watched miss reopens the WHOLE document at its first instruction, names the miss, and preserves the count:

    ▌ REVIEW{1/2} · REPAIR 1

    ▌ DEVIATION
    `maybe` is not in OPTIONS (approve, revise, reject). Take one of them, verbatim.

At `work_repairs_allowed`, the conductor stops repairing and returns the operator. Only WATCHED moves count; status calls do not.

### SIGNAL — when to call, what to type

The closing belongs to the flow, never the author. A closing owing a call has `▶`; `END` owes none:

    ▶ CONTINUE
    ./pp <key>

    ▶ FINAL
    ./pp <key>   (once the operator replies)

    ▌ END
    the conduction is over — report to the operator…

The agent copies the command verbatim — run `<key>` first.

## What the agent produces

### ELECTION — judgment compressed into a closed choice

    proc: |
      PICK verdict

The block supplies the closed set; answer with one member verbatim:

    ▌ OPTIONS
    approve revise reject

    ▌ INSTRUCTION
    PICK verdict

    ▶ CONTINUE
    ./pp <key> <your-choice>

Membership validates; anything else is a MISS.

### PRODUCTION — the work, addressed to the operator

    output: table
    proc: |
      INFER

An unconsumed `WORK`/`INFER` speaks to the operator. CHANNEL is flow-derived, never declared: before the turn frontier it is `=> ephemeral` — a DRAFT delivered once by FINAL, validated and in step order; adjacent to the frontier with no draft held it is `=> chat`; with no `FINAL` ahead it is immediately `=> chat`:

    ▌ INSTRUCTION
    INFER table => ephemeral

    ▶ CONTINUE
    ./pp <key>

Place `FINAL` deliberately: it is exchange frontier and delivery point for all preceding drafts. Keyed advance moves the flow; pp never needs the agent's own text back.

### FEED — the work, addressed to the machine

    # in the producer          # in the consumer, BUILDER.md
    output: json               input: json
    proc: |                    proc: |
      INFER                      INFER
      CALL BUILDER.md

When the adjacent callee declares `input:`, production is CAPTURED and validated (`json` must parse), then seeds its pipeline. Format mode determines transport:

    ▶ CONTINUE
    ./pp <key> -   (your <json> on stdin -- heredoc)

**Consumption is USE, not transport** — pp catches whatever accompanies a call, but production RETURNS only when consumed. Three consumers exist, only the first declared: a callee (`input:`); an election (PICK options ARE upstream production); and **the engine itself** — checkpoint proof consumed by the judge, sunk production by the bus, or document `sink:` by its named skill (stdin in, `::push` / `::clear` out). Engine-consumed production travels `=> tool` like any FEED; authors never declare channels.

**Capture is not a channel.** The keyed call is ONE bidirectional wire: the OPERATOR's message reaches resume at the frontier (FINAL asks for it under `capture_prompt`); the AGENT's production returns only when consumed. The frontier distinguishes directions — never a declaration.

### SELF-PROOF — the honest self-check

    constraints.production: |
      C1  a finding without the line it comes from is no finding.
    proc: |
      INFER

A law of production turns the document into a machine-checked contract; authors never write the checkpoint. The engine injects it before each `FINAL` — nothing leaves unproven — and on frame exit; no key arms it, no switch silences it. The proof names the codes at risk, at least one; a code unnamed is n/a; no active production law means silent checkpoint. Behavior laws bind the block and are never proven.

    ▌ INSTRUCTION
    INFER proof [B1 B2 …] on all produced areas => tool (heredoc)

    ▶ CONTINUE
    ./pp <key> -   (your proof on stdin -- heredoc)

    ./pp <key> - <<'EOF'
    [{"code": "C1", "evidence": "judged line 12 on its own terms", "verdict": "ok"}]
    EOF

Coverage/shape are mechanical; evidence truth is kept honest by doctrine and audit sampling, never assumed.

### BLOCKED — the honest stop

When the required form is untenable, answer `#BLOCKED <reason>` in chat and stop. This is convention, not mechanism; the operator takes over.

## The agent's initiative

### RECALL — the atom everything depends on

Every transition — first `-new`, continuation, keyed advance, call after FINAL — is agent initiative. Nothing forces it; doors, standing rules, the `▶` exact command, and every offered name being a pp entry secure it. Even a misplaced call recalls: pending block answers, nothing plays, nothing counts.

### GESTURE — judgment decides, the script executes

    ./pp <key> -s pp-authoring section serve MEMBER.md reference: README.md

A named skill through pp is ONE call: pending block first, work after. Out of block scope, work does not happen. Three kinds share this form: conducted (`proc:` skill), executed (script), served (augmented contract with neither — this guide).

Offers LIVE with their output. Fused outputs number headings; each segment owns ITS OWN list. Calls route under the owning segment's snapshotted laws; `-s <name>@<n>` resolves a tie; the next rendered output retires addresses. Place `tools:` on the step that needs the call.

## Time

### DUE — the cadence the agent never keeps

    proc: |
      CALL JOURNAL.md ^ @SETTINGS.journal_frequency

The guard reads cadence from a document field: plays every n completed exchanges, otherwise resolves silently. The tool owns the calendar; the agent remembers none.

### WAKE — the boot that opens on something

When dates require it — new week, undigested record — the engine INJECTS a start step, playing the cadenced document before member takeover. The author defines the injected proc (e.g. continuity weekly digest); the engine owns when.

## The operator's own

### ASK — what opens every exchange

The operator's message is the brief; turn WORK serves it. pp never makes the operator repeat: their words reach the agent through the harness, not a block.

### VERBATIM — the decision, raw

    # SETTINGS.md
    capture_prompt: true

FINAL asks for the operator's next message itself; the trace keeps their uninterpreted words — decision spoken, not understood.

### GATE — the operator's GO is the gate

Approve, reject and GO belong to the operator, never the agent. A proc reaching a gate goes FINAL; working an unapproved request is contractually out of bounds.

### TUNING — shaping without touching a bundle

Between exchanges the operator edits their own `SETTINGS.md`, `FORMATS.md`, `MEMBER.md`, `procs/`, overlays. Invalid values refuse before anything plays and name the reason. Bundles are never edited: customize by redeclaring at home.

## The author's reference — front matter, key by key

| Key | Declares | Notes |
|---|---|---|
| `name` | identity | skill-directory name IS identity (`SKILL.md` is the form) |
| `kind` | `proc` · `doc` · `boot` | classification; `doc` never executes |
| `description` | catalog line | menu text; required when offered |
| `proc:` | flow, one keyword/line | presence makes it CONDUCTED |
| `output:` | production form | formats-enumeration NAME; unknown refuses |
| `input:` | consumed form | caller adjacent production becomes captured FEED |
| `serve:` | reading sections | one paragraph/bare `SERVE`; multi-line/docs allowed; without SERVE unread; document proven once/run |
| `tools:` | frame offers | `+name` adopts harness skill; overlay `-name` removes |
| `constraints.production:` | checkpoint laws, `CODE  text`/line | what agent MAKES; ONE line/law; wrapping parses a new code |
| `constraints.behavior:` | served, unproven laws | what agent does/says/reads; bare `constraints:` refuses (`constraints-unsectioned`) |
| `formats:` | `name  mode  description` | extends enumeration; redeclaration overrides |
| `attach:` | HOOK socket | CALLed wherever hook plays, after manifest hooks there; a socket orders its contributors by the requires topology of their HOMES, and between SIBLINGS by the pins' order — never by the document's name |
| `mount:` | socket the document ENTERS | hosted at its socket — no frame, no `proc:` owed; exclusive of `attach:` (`attach-and-mount`) |
| `provides:` | token this document SERVES | paired with `with:` — one without the other refuses (`contribution-malformed`); the token wears its package's name, another's is JOINED under ITS prefix (`name-unprefixed`) |
| `with:` | `<skill> <args>` serving the token | a skill of the document's OWN package — a foreign name refuses (`with-foreign`); two packages sharing a skill name refuse (`skill-taken`) |
| `order:` | `<hook> before\|after <package>` | a contributor's stated rank at a socket: the derived topology first, preferences over it; a preference toward a package the composition lacks is inert, two that each want to be first refuse `order-cycle` |
| `when:` | `"@Doc.field"` (quoted YAML) | contributor switch/cadence, judged like `^ @Doc.field`; socket knows no key |
| (manifest) `cadences:` / `checks:` | `{name, anchor: "@SETTINGS.<key>", record, play, at[, since]}` / `{signal, predicate: record-crossing, record, anchor}` | socket document / boot signal when anchored weekday crosses record |
| `payloads:` | space-separated tokens the document CONSUMES | providers found by scanning the composition's DOCUMENTS; each runs and lands as `INFORMATION — <token>`; a token of another package is named under ITS prefix |
| `cycle:` | `true` = session floor · `<token>` = iterated door | exhaustion rewinds and sweeps the mounts · exhaustion asks the token: a lap per element (payloads re-resolved, mounts kept, each lap proven), the exit when nothing is due; `cycle-unprovided` when nobody provides |
| `fusion:` | `max` · n · `none` | frame pace over instance |
| `override:` | `true` on `SYSTEM_PROMPT.md` | composes replace artifact — lock, otherwise retracted |

Any text file is SERVABLE whole — there is no terminal marker; the hash pp computes on what it serves proves what was served.

The `proc:` language is `PICK <name>` · `SERVE` · `CALL <doc>` · `HOOK <name>` · `WORK` · `INFER` · `FINAL`; plus lone `§` (fusion never crosses this section break), `# ` comments (uncommenting arms them in `proc:` and constraints), and guard suffix `^ @Doc.field` (declared cadence). `PROVE` is retired author vocabulary: `prove:` arms proof; written `PROVE` refuses at parse.

## SETTINGS, key by key — engine default ⟂ seed

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

## The figures — what a package makes of the forms

The served `CONDUCTION` says WHEN to choose each figure — where a piece of work comes from and where it is played; this catalog says how each one is written.

Two catalogs, two axes. The FORMS above are the raw material: what one line of front matter or `proc:` puts in play. A FIGURE is the shape a whole package document takes to enter the flow — it composes several forms toward one intent. Twelve figures cover the eight shipped packages (survey: `plans/pp-split/PATTERNS.md`, 2026-09-01); each entry says what the author writes, what the engine guarantees, and cites a real employer as written. Two qualifiers — the guard and the order preference — cross several figures and close the catalog.

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

A `kind: doc` document without `proc:` — never played — that a SKILL hosts by printing `::mount <json>` on its stdout; the console harvests the directive and the HOSTING above happens: body as brief, laws in force, rows served; the agent's keyed call closes it. The socket's door is the contributor; this is the gesture's door — same hosting, different trigger. Real, `packages/plan/skills/pp-plan/pp-plan.py` mounting a plan chain:

    print("::mount " + json.dumps(chain))

### The overlay — a mode over a floor you do not own

Prose, law deltas, offer deltas and READINGS on a same-named document another package owns. The body joins the base's composition (deep packages first, the user last); the deltas (`+CODE text` / `-CODE`, `+name` / `-name`) apply to the base's frame; the `serve:` rows ADD readings to the base — served whole as the base enters, in application order, each titled by its token, `+` optional, no `-` (`overlay-serve-removal`): the way a package hands the agent a doctrine at the turn without owning TURN (`plan/overlays/TURN.md` serves `+PLAN_CHEATSHEET.md`). An overlay carrying `proc:` refuses (`overlay-carries-proc`); an idle delta refuses (`overlay-adds-existing`, `overlay-removes-nothing`). Its limit counts: an overlay has NO guard — a conditional law cannot ride one. Real, `improvement/overlays/TURN.md`, whole:

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

A deterministic script, its card (`SKILL.md`), and the few-line vendored `skills/_core.py` to reach the engine's face. The skill is the ONE writer of its record: every write rides one primitive (`state.record`) — file lock, the read INSIDE the lock, the change, an atomic replace; a reader never blocks and never takes the lock. Guards refuse by name, exit 2, nothing written; a budget guards every entry. Real: every package skill vendors `_core.py`, whose brief opens on the walk — "`home(start)` walks up from the CALLER's own file".

### The settings fragment — prefixed keys, read through the face

`settings/SETTINGS.md`, `kind: fragment`, `package: <name>`: keys PREFIXED by the package's name, a `types:` block, an `effort:` block where levels differ. The instance's SETTINGS is COMPOSED — the system's bare keys first, then one named section per package in requires order; an unparsable value refuses by name. A skill reads its key through the face and gets the EFFECTIVE value, effort presets included; removing the package leaves its keys `unowned` so a later `add` recovers the operator's values. Real, `continuity/settings/SETTINGS.md`:

    kind: fragment
    package: continuity

### The two qualifiers — guard and order

`when: "@Doc.field"` on an attached or mounted contributor: the injected CALL inherits the guard — the mechanism that silences a package without removing it (`federation/WEAVE` under `federation_coordinator`). An overlay has no guard. `order: <socket> before|after <package>`: a contributor states its own rank at a socket, beating the derived topology — `improvement/IMPROVE` declares `order: turn.end before steering` so its lines are held before the surface renders them. The client declares its order; a provider never names its clients.

## Three sequences of an exchange, complete

A sequence chains one EXCHANGE out of the forms — the figures above say how a package hooks the flow; these three compose it end to end.

**The review gate** — reading, closed verdict under law, proof obliged at exit (PICK elects from the production BEFORE it — INFER's list becomes OPTIONS):

    ---
    name: REVIEW
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
    List allowed verdicts — approve, revise, reject — as a JSON array with their findings, then elect ONE.

**The consigning turn** — a cadenced record, the call offered on its step (a `journal` package's own skill and key: a public name wears its package's name):

    ---
    name: JOURNAL
    kind: proc
    description: consign what happened, one dated line per operation.
    tools: |
      pp-journal
    proc: |
      WORK
    ---
    Consign record-worthy facts since the last entry — one `./pp <key> -s pp-journal add <line>` per operation.

    # caller: operator-paced, at sequence TAIL; behind work calls the register window holds, and the span reaches the present
    proc: |
      CALL JOURNAL.md ^ @SETTINGS.journal_frequency

**The pipeline** — a validated production seeds its consumer:

    # PLANNER.md                # BUILDER.md
    output: json                input: json
    proc: |                     proc: |
      INFER                       INFER
      CALL BUILDER.md

Planner JSON is captured (stdin, by format mode), parsed, and seeds builder. A following PICK also consumes it: validated JSON IS data; the pipeline can source OPTIONS.

## The rules of composition — five by design, four the history added

1. **Describe a new proc by its forms before writing it.** If it needs a form outside this catalog, name the composition deliberately: new bricks answer named needs, never accidents.
2. **Count the LLM initiatives per turn** — every recall, including hidden continuation recalls, and every free call. Equal result, lower count wins. pp entry is amortized (even misplaced it recalls); a harness skill is naked: maximize amortized share.
3. **Conducted or neutral: intended initiative decides.** `proc:` alone divides the same registered-element kind. Flow decides → give it `proc:`. Agent free will decides → leave neutral: script beside contract or served guide. Choose initiative, not shelf.
4. **The new lives in content, never in form.** Add no section, marker or block wording; customize answer forms through `FORMATS.md`. Meta-form is capital, spent once by design, never drift. Served examples indent four spaces, never fences: fences break harness renderers and make content look like live protocol.
5. **Constraints short, load-bearing first.** Every block re-emits all of them: each line costs per step, and list heads are retained best.
6. **A rule that counts is made mechanical or measured.** Declare form, script structure, change incentive, or measure drift; bare doctrine silently erodes under model drift at scale.
7. **A periodic need is a dated due or a reflex — never a registered element.** Dates over append-only records decide; agent keeps no calendar, and the floor needs no scheduled personality.
8. **Placement is law.** Step position in sequence, offer position in fused output, law position in list each changes what plays; design positions as deliberately as words.
9. **A public name wears its package's name.** A console verb, a skill, a settings key, a vector family, a payload token: `<package>-<name>` — `pp-<package>` for a skill, `<package>_<key>` for a key — and the package's own name alone counts (`doc`, `plan:`). Wearing ANOTHER package's prefix JOINS its thing (a family it guards, a token it serves or consumes) and requires it like any reference; wearing nobody's refuses `name-unprefixed` at the five gates, before anything is written. Procs and refs stay BARE, resolved by package: two packages carrying one base name refuse `name-ambiguous` — an overlay keeps the source name, which is why a proc is never prefixed.

## The lived doctrine — what each piece IS, and what died proving it

The product's retakes refined every piece; this is the residue carried by that history.

- **A constraint** is positive, short, against real model drift; it belongs in production or behavior, and a production law names whether proof covers whole, sample or trace fact. When it COUNTS, make it mechanical or measured. Proof honesty as prose produced 5 900 ok for 3 fail; it changed only when verdicts, evidence form and repair incentive became mechanics. Dead: maxim, negative wording, engine-vocabulary clause in a proc body, undeclared drifting form.
- **A body** is served savoir-faire — brief, worked examples (indented, never fenced), method. Never law (body reads once; law re-arms every block), never a mirror of another document (three mirrors lived and died), never dated state: artifact says PRESENT; trajectory lives in records.
- **A proc** is one métier with a declared frontier: free WORK, guarded CALLs, enumeration closing. Never another motif's envelope (`PROVEN_INFERENCE` died inlined and returned as `prove:`), never a scheduled element (ADVISOR/mentor died: periodic need became dated due over append-only record or one-line turn reflex). Step POSITION is normative: steering restitution closes on NEXT; continuity consignation closes the turn.
- **A scripted skill** is the ONE writer of its record: named calls, named stderr refusals, atomic writes, guarded budget, hermetic bench. Script owns structure; agent owns prose. Template titles the born document; piped prose starts at content.
- **A ref** is served knowledge — by section/SERVE or mount — never played; **an overlay** is one package's mode over another's floor: deltas only.
- **A format** is a NAME in pp's enumeration. Stable restitution DECLARES its format: steering NEXT drifted three weeks under doctrine alone and stabilized when its form was declared.

## Prove it mechanically

`-build` compiles the catalog and refuses lies — doubled constraints, bare `constraints:` (`constraints-unsectioned`), unhooked attaches, unknown formats — and lints forgotten productions. `-peek` renders what a real call would show without effect; `-test` runs engine fixtures; a real install plays the document end to end. Whose document it is decides the SEVERITY: a defect in YOUR instance's documents warns and the build passes (`pp: WARNING -- …`, the offending line simply not in force), the same defect in a package's refuses by name. The bare `constraints:` key refuses on both sides — the migration gate, not a law defect.

## What this guide is not

Not a validator — the engine is. Not operator onboarding — README and REFERENCE own that path. Not the examples — the served cheatsheet is, and the bench plays them. Not a place for content rules: inside a step, work is free.
