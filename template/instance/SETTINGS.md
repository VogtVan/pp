---
name: SETTINGS
kind: doc
description: >-
  This instance's tuning -- the operator's VALUES in the product's SHAPE:
  seeded at install, re-shaped at every upgrade and doctor (the keys in
  their sections, this documentation refreshed), no value you chose ever
  rewritten. Every key stands VALUED: nothing absent, nothing empty -- what
  you read is what plays.
conduction_effort: medium
instructions_fusion: max
verbatim_constraints: true
capture_prompt: false
max_harness_tool_output: 25000
proc_body_serve: always
work_repairs_allowed: 3
---

# SETTINGS — how this instance is tuned

The operator's file: edit a value above, the next call plays with it. A value
that does not parse refuses — nothing played, the reason named. Every key is
seeded VALUED at its default — none absent, none empty. The file is COMPOSED:
the SYSTEM first — the conductor and its kit are one package, their keys bare
— then one named section per package beyond, in the order of its requires
(the plan…), the keys grouped the same way above; a package's keys wear its
prefix (`plan_`), the system's wear none.

## System — the conductor and its kit

### Effort — how lean the blocks render

The agent is never configured by a key: whether a turn is conducted is the
operator's word (`pp off`, `pp on`), said to the agent at the
standing orders, never read from here. The keys below tune what the ENGINE
renders and what the skills do; none of them addresses the agent.

- `conduction_effort` — HOW LEAN the conducted blocks render. A named effort
  presets the four weight keys — their written values stand INERT while it
  is posed; a key the effort does not name stays the operator's.
  `max_harness_tool_output` stays out: it says the HOST's limit, never the
  weight. The keyless `./pp` says the effort in force, for the operator.

  | Effort | verbatim_constraints | instructions_fusion | proc_body_serve | capture_prompt |
  |---|---|---|---|---|
  | `none` | the key rules | the key rules | the key rules | the key rules |
  | `light` | false — the codes after a law's first emission | max | once — a body proven renders nothing | false |
  | `medium` | false | max | once | true |
  | `full` | true | none — one step per block | always | true |

  Every package adds its own keys to a level in its own section (its
  fragment's `effort:` block) — the records' cadence is continuity's
  (5 / 3 / 1), the surface's cap improvement's (1 / 2 / 3), preset there.

### Instructions — how the blocks render

- `instructions_fusion` — yields rendered per output: `max` fuses every
  certain stretch (unchecked chat steps flow in one output, stacked; the
  batch closes on a scope's `§` break, a value the tool must capture, a
  FINAL, the serve budget); a number caps the stretch; `none` renders one
  step per block. A document's own `fusion:` front-matter key caps its frame.

  | Value | Effect |
  |---|---|
  | `max` | one output per certain stretch — the fewest calls |
  | n >= 1 | at most n yields per output |
  | `none` | one step per block — the engine's bare default |

- `verbatim_constraints` — `true`: every block re-emits the constraints as
  their full text; `false`: a law's text at its FIRST emission of the run, its
  code at every re-emission — leaner, nothing unsaid; `-compacted` clears the
  ledger and the texts return.
- `capture_prompt` — when `true`, the FINAL closing's resume asks for the
  operator's next message itself, and the session log keeps it. The effort
  presets it (medium and full → `true`).

### Readings — what the served documents deliver

- a serve row declares its nature by its first token (`architecture:
  DESIGN.md`, from `code | reference | architecture | diagram | contract |
  map`), never by inference — a declaration for the readers, never a hold:
  every row serves, whole, and a repair re-serves nothing already proven.
- `proc_body_serve` — how a BODY rides: the body of a CALLed proc and the body
  a mount serves. `always`: at every CALL and every mount — the brief re-read
  each time (the session's turn CALLs its steps every exchange: their bodies
  ride every exchange). `once`: a body is proven by its content like any
  reading; CALLed or mounted again in the run, it renders nothing, and it comes
  back whole the moment its document changed. The effort presets it (light and
  medium → `once`).

  | Value | Effect |
  |---|---|
  | `always` | the body is forced back at every CALL and every mount |
  | `once` | the body rides once per run while unchanged; a later CALL or mount renders nothing |

- `max_harness_tool_output` — characters ONE tool output may hold at your HOST.
  The engine measures the block it is about to hand over -- all of it, whatever
  the matter -- and cuts it under this at a seam; what is left comes back on a
  bare call, so nothing ever leaves the context for a file. A fact of the host,
  not of pp: Claude Code's VS Code extension persists a result past 30000, and
  25000 leaves the framing its room. Another harness has its own -- measure it.

### Packages — the switch of each

- `package.<name>` — `on` or `off`, one key per pinned package beyond the base,
  seeded `on` when the package enters (install, `add`, `upgrade`, `doctor`),
  dropped when it leaves (`remove`). `off` takes the package out of the play
  — none of its documents, sockets, cadences, checks, commands or overlays
  plays — and every package that requires it goes off with it, its
  cause said under the heading of each output (`<client> off (← <dependency>)`). Off is
  not gone: the pin, the bundle, this file's section and the records stand as
  they are, and `on` brings everything back. The base never switches off, and
  any value but `on` / `off` refuses. The next boot recompiles the catalog and
  the standing rules on a moved switch — nothing to run.

### Work — what a miss costs

The proof has no key: wherever a law of production is in force, the checkpoint
stands before each FINAL and at a frame's exit, and the engine decides — no
document switch, no skip. What is tuned here is the repair bound alone.

- `work_repairs_allowed` — deviations on one instruction before the operator
  is handed back to.
