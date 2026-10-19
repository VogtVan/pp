# Procedural Prompting — the reference

The mechanics behind the [README](README.md): the block, the language, your
own procedures, what happens when an answer misses, and the instance on disk.

## Why a conductor

A language model is excellent at judgment and poor at bookkeeping. Ask one to
follow a long procedure and you have handed it two jobs at once: the work, and
the management of the work — the current position, the rules in force, what
was already read, what comes next.

It performs the second job from memory, and memory is exactly where a model
degrades: instructions stated once fade as the context grows, scope creeps
because nothing structural resists it, and a reading is *claimed* rather than
proven.

Procedural Prompting externalizes the bookkeeping. A small deterministic
**conductor** plays the procedure and hands the model **one output at a
time**. The model's freedom is untouched *inside* the step — judgment,
wording, reasoning stay its own. The **limits** around the step are not its
concern anymore: it does not track them, so it cannot lose them. And the
limits are **yours to write**: what you put in a procedure is what every block
will enforce — the specification holds because it never leaves the screen.

This reference documents BOTH faces of the product:

- the **user face** — what an operator builds and tunes: procedures,
  settings, packages;
- the **agent face** — what a conducted model consumes: blocks, commands,
  channels, repairs.

Its overlap with the agent's own card and with the author's catalog
`PP_CHEATSHEET` is deliberate: same mechanics, technical wording — this
document is never the source of an agent reflex.

## Index

**The user face — building and tuning**

1. [The language, keyword by keyword](#the-language-keyword-by-keyword)
2. [The front matter, key by key](#the-front-matter-key-by-key)
3. [Writing your own procedures](#writing-your-own-procedures)
4. [Offered skills — one rule, and adoption](#offered-skills--one-rule-and-adoption)
5. [The doors](#the-doors)
6. [The operator's console](#the-operators-console)
7. [Switching a package off](#switching-a-package-off)
8. [The adapter surface](#the-adapter-surface)
9. [The hook channel](#the-hook-channel)
10. [The instance on disk](#the-instance-on-disk)

**The agent face — consuming the conduction**

11. [The loop and the commands](#the-loop-and-the-commands)
12. [The block, section by section](#the-block-section-by-section)
13. [Channels and the delivery](#channels-and-the-delivery)
14. [The bus and the diagnostics](#the-bus-and-the-diagnostics)
15. [When an answer misses](#when-an-answer-misses)

---

# The user face — building and tuning

## The language, keyword by keyword

The front matter is **YAML** (`yaml.safe_load`) — one flat mapping. Values keep
their YAML types (`true` is a bool), a key left bare declares nothing, `#`
comments vanish. Inside a block scalar (`constraints: |`), a `# `-prefixed line
is a comment of pp's own — uncommenting it arms the line.

A **procedure** is the `proc:` key of that front matter — one keyword,
optionally followed by an argument, per line. Every entry below follows one
format: **name · declares · effect · example**.

### `PICK <name>`

*Declares* — a closed choice: the model elects ONE id.

*Effect* — the block renders `OPTIONS`, fed by the upstream production (the
pipeline is the options source), and validates by membership; anything else
repairs. The answer rides the command, verbatim.

The list the upstream hands it is judged at its CAPTURE, on the form a `field`
has — a JSON array of scalars (strings or numbers), none empty, each once, 200
at most:

- a list of objects, an empty array or a bare scalar is a miss that repairs,
  the element named under `DEVIATION`;
- a number renders as its text (`[1, 2]` offers `1` and `2`);
- a list no capture judged — a callee's seed under `input:` — refuses
  `options-invalid`, the element named;
- a `PICK` with no producer before it refuses `options-empty`.

*Example* —

    proc: |
      PICK verdict

### `SERVE [doc]`

*Declares* — a reading the TOOL performs; the model has nothing to prove.

*Effect* — one bare `SERVE` dequeues one whole SECTION of `serve:` — a
paragraph of the block (a blank line separates sections), every line and
document of it; n sections take n bare SERVEs, in order. The section declares,
the SERVE plays: a section without its SERVE is never read; a SERVE past the
last section refuses `serve-exhausted`.

The text is injected under `INFORMATION`. An output over the host's cap comes
in chunks: an intermediate chunk says what remains and that the bare call
alone serves it (any other call bounces, `chunk-pending`); in a run its principal
conducts, it carries no command and says the rest comes at the next prompt (see
*The two conduction modes*). Each document is
proven ONCE per run by its content, when its last chunk has left — named again
(another section, a `SERVE <doc>`, a mount, a CALL) it renders nothing, never
the text.

**How a token resolves.** A token is addressed as the engine resolves it:

- a bare NAME — through the member's search paths: the instance's own space,
  `procs/`, then the packages (a ref by its bare name), then the root of the
  member's repo (`README.md`); the instance and the packages keep the upper
  hand on a same name;
- a PATH — a token carrying a `/` (`design/target.md`, `engine/pp.py`) — is
  its MATERIAL's when one is named and holds it (below), else the
  repository's when the repository holds it, the instance's otherwise: a
  member without the source reads the machine's copy, `.sys/engine/pp.py`
  addresses the machine wherever the source stands beside it, and a path
  standing at the repository and the instance is said once per run (the
  engine's signal `serve-shadowed`); a vendored path is a pin, never written.

**The material of a reading** (engine `0.1.0-beta.58`). A MATERIAL is a named
tree of files — a worktree, a clone, the repository itself. `repo` is the
repository around the instance, tacit; `work` is the tree a LAUNCHER gave the
run (`PP_WORKDIR` at `-new`, kept at the slot); any other name is yours,
declared at `SETTINGS.md` as `material.<name>: <path>` (relative to the
workspace or absolute, `~` expanded; a name must be given and is neither
`repo` nor `work`, else `settings-invalid`; the path is judged on disk at the
reading, never at SETTINGS). A row reads from a material in three ways, the
nearest word winning: the row carries `@<name>` as its first token after its
nature or as its last (`code: @core engine/pp.py[def forward..]`, `engine/pp.py
@core` — every document of the row, one mark a row); the document
that carries the row declares `material: <name>`; a CALLed document without
one inherits the nearest calling frame's. Without any word the run's `work`
answers, and without a `work` the repository: a row written before this
version reads exactly as it did. A material changes nothing for a bare NAME —
an instance document is the instance's wherever the code lives. The reading
says its tree: its title carries ` @<name>` when the material is not the
repository (`INFORMATION — engine/pp.py[def forward..] @core`) and the
ledger's place column names it (`-stats --blocks`). What a material cannot give
is served as today and SAID, a `note` diagnostic each: a name no catalogue
knows (`material-unknown`, `@work` in a run given none included), a declared
path that is no directory (`material-missing`), a file the material lacks
(`serve-stale`, « not in material »). A bare `@`, or two marks on one row,
refuse `material-invalid`.
The lint of topology skips the mark; `pp-plan serve` writes it like any token.
A plan whose code lives in such a tree says it once, `pp-plan material <slug>
[<name>]`: every node born under it carries `material: <name>`, and a mount
serves its rows from that tree (the plan package's `pp-plan` contract).

**The three forms of a token**, preferred in this order:

| Form | Example | What is served |
|---|---|---|
| whole | `GLOSSARY.md` | the default; write it unless the document is too large for what the step needs |
| between two tags | `engine/pp.py[def _played..def _skill]`, `PHASE.md[## Target..## Arbitrations]` | the lines from the first line that starts with the first tag to the first line after it that starts with the second tag, that second line left out |
| by line ranges | `GLOSSARY.md[1-2,8-12]` | still served, as a last resort only: the numbers point elsewhere as soon as the file changes, and nothing warns you when they do; written through `pp-plan serve`, the answer says so |

The rules of a tag: leading blanks of a line are ignored, a tag may hold
blanks, and the start of a line is enough (`def _pla`); a tag holds neither
`..` nor `]`. Either side may stay empty: `DOC[..end]` starts at the top,
`DOC[start..]` runs to the end. A token holds one pair of tags; two parts of
one document are two tokens. The file is read as plain lines, whatever its
type, so the same rule serves markdown, code and YAML, and the tags keep
pointing at the same part when lines are added above it.

What is served is titled by the token as written and proven by the hash of
the selected lines. The engine SAYS what it could not serve:

- the start tag found on no line — nothing of that token is served, a line in
  the block says so, and the engine pushes `serve-stale`;
- the end tag found on no line after the start — the document is served to
  its end, and `serve-stale` says it;
- a range past the end — the lines that exist are served, the same signal;
- a badly written token — `[..]`, three tags, brackets holding neither `..`
  nor line ranges, a bracket left open — refuses `serve-range-malformed`,
  naming the row and its document.

*Example* —

    serve: |
      STYLE.md GLOSSARY.md
    proc: |
      SERVE
      INFER

### `CALL <doc>`

*Declares* — a SERVE that also executes.

*Effect* — the callee's BODY travels first, then its procedure plays in a new
frame. The callee's `serve:` section stays its own: a CALL never plays it, the
callee's bare `SERVE` does. Its `constraints:` and `tools:` **accumulate,
never lighten**, and fall with the frame; its last production flows out to
the caller's next step.

*Example* —

    proc: |
      CALL REVIEW.md

### `HOOK <name>`

*Declares* — a socket by name.

*Effect* — every document carrying `attach: <name>` is CALLed there, in the
requires topology of their homes and, within one, in name order; nothing
attached is a strict no-op. A contributor may say where it wants to stand
(`order: <hook> before|after <package>`); two that each want to come first
refuse `order-cycle`. Packages extend each other — and you extend packages —
**without ever editing a bundle**.

*Example* —

    proc: |
      HOOK boot.ready

### `WORK`

*Declares* — the free step.

*Effect* — the agent serves the standing ask (the operator's message, or the
calling context's brief), chaining tools and productions at will. The step
closes on its RESULT, in this exchange; the result's form is the document's
`output:`. Untenable, it closes `#BLOCKED <reason>`.

*Example* —

    output: free
    proc: |
      WORK

### `INFER`

*Declares* — the unitary production.

*Effect* — ONE production in the named form, nothing else: the proof loop, a
closing table. Consumed downstream, it is captured and validated; unconsumed,
it speaks to the operator (see [channels](#channels-and-the-delivery)).

*Example* —

    output: table
    proc: |
      INFER

### The checkpoint

No front-matter key: `PROVE` is no author keyword, and `prove:` is gone — a
document that still carries it refuses `prove-gone`; a written `PROVE`
refuses at parse (`prove-retired`).

*Declares* — nothing: a law of production in force is what arms it.

*Effect* — the engine injects a proof checkpoint wherever a frame's
productions are about to LEAVE:

- in front of each `FINAL` — nothing is delivered unproven: a failing verdict
  replays the document BEFORE the message goes out;
- at the frame's exit — pop, cycle lap, run end — when the frame leaves with
  productions its OWN laws of production have not proven;
- for a document a socket called — a contributor, a cadence, and the successor
  one of them leaves to — the same debt goes to the turn's checkpoint instead:
  its own laws stay DUE at the run after its frame leaves, ride the blocks that
  follow among the laws in force, and the next checkpoint names them (one proof
  for the turn, no step of its own; the trace says `owed`).

The proof names EVERY code the line asks — the laws of production in force,
one object each, `n/a` written out where a law has no bearing; a code left
unnamed is a miss (`the PROOF leaves N code(s) unnamed: …`), a code not in
force is a miss too; a behavior code named in addition is tolerated. A
mini-proof names its repaired codes alone — machine-checked. No switch on either
side: the engine decides, the agent never judges whether to prove; a frame
that produced nothing, or with no law of production, owes nothing. The
upstream production passes THROUGH a proven checkpoint; the proof itself never
travels.

A failed object has three issues. A bare `fail` replays the document. A
`fail` naming its `"fix"` repairs IN PLACE: the agent corrects the production
and pipes a mini-proof over those codes alone. A `fail` carrying
`"blocked": "<what is missing>"` -- a non-empty text -- DECLARES a gap: the
checkpoint closes without a repair, the production leaves, the trace writes a
`blocked` line (the codes and their texts, counted by `-stats` as gaps
declared), and the closing of the block that follows says
`(a gap declared: <code> -- <text>)`; the agent tells the principal that gap
in its answer. In one proof a bare `fail` outweighs the rest; an object
carrying both `fix` and `blocked` repairs in place, and its mini-proof may
declare the gap.

*Example* —

    constraints.production: |
      C1  a finding without the line it comes from is no finding.
    proc: |
      WORK

### `FINAL`

*Declares* — the exchange's frontier.

*Effect* — the exchange closes here: nothing leaves before its proof, nothing
plays after it until the next operator message resumes the procedure. The
closing is always a bare `▶ FINAL`: it delivers nothing, every unconsumed
production was said `=> response` at its own step. Place it deliberately — it
is the frontier; an armed document proves each segment before ITS production
leaves.

*Example* —

    proc: |
      WORK
      FINAL

### `§` — the section break

A lone paragraph mark. Fusion never crosses it: the marked step always opens a
fresh output. The author's strict-order lever. It belongs to the document whose
step needs it, never to a floor on behalf of its contributors: the kit's `TURN`
carries none (plan fixes1, 2026-10-16) -- with nothing at `turn.end` the frontier
closes the WORK's own output --, and steering's `THREADS` opens on one (the pass
after the work) and keeps one before `NEXT` (the table after the pass); a
reading a script computes (`with:`) is thus never rendered ahead of the work it
depends on.

### `# ` — a comment line

An inert line, in `proc:` as in `constraints:`. Uncommenting arms it: how a
seed ships OFF and turns ON at home.

### `^ @Doc.field` — a guard suffix

A cadence read from a document field: the line plays every *n* completed
exchanges (the field's value), resolves silently otherwise; never before the
first. One tag, no algebra.

*Example* —

    proc: |
      CALL OPERATIONS.md ^ @SETTINGS.memory

### Around the keywords

**`cycle:`** says how a document turns.

- `cycle: true` makes it a session floor: exhausted, it rewinds instead of
  completing, and the rewind sweeps the mounts.
- `cycle: <token>` makes it an ITERATED door: a lap per element the token's
  providers render — the payloads re-resolved at each lap (a rendering the
  exchange already delivered is spared by its content), the mounts kept, each
  lap proven under the laws on screen; the frame leaves like any callee when
  nothing is due. A token nobody provides refuses `cycle-unprovided`.

**`field:`** makes it a DESCRIBED door: the same laps, the iterator asked of
the agent instead of a provider, so no skill is written. The key holds, in
prose, what the door turns on. At the door's entry the engine injects a step
the agent sees as `INFER field => tool (heredoc)`, the prose its brief (its
`@Doc.field` references resolved as an exec's arguments are; one resolving to
nothing refuses `field-argument-empty`).

The answer is a JSON array judged on its FORM alone — valid, an array, scalars
none empty, each once, 200 at most — never on what an element is: an array of
integers passes like an array of paths. Accepted, the array is the field, held
by the frame as what remains due (a rewind never touches it, a compaction
re-serves its head): each lap serves the head under `INFORMATION — field`, two
calls in a row render the same head, the lap that closes drops it, and an
empty array opens no lap — the door leaves like any callee.

The build refuses `field:` and `cycle:` on one document (`cycle-and-field`),
an empty `field:` (`field-empty`), one on a document the engine never CALLs as
a proc (`field-unplayable`); a written `FIELD` refuses `field-keyword` at
parse.

**`next:`** names the SUCCESSORS a document may leave to — the edges of a
workflow, document names as `CALL` writes them. One name follows without a
decision; several are decided when the document leaves, by the same two
mechanisms as the doors:

- **`decide: <verb> [args]`** asks the owner's `pp-<package>` skill (an
  instance document names its own skill first); the one name it prints
  follows — a name outside `next:` refuses `next-foreign`, a non-zero exit
  `next-refused`;
- **`choose: |`** asks the agent: the engine injects a step the agent sees as
  `PICK next options => tool`, the prose its brief under `NEXT INSTRUCTION
  CONTEXT — next` (its `@Doc.field` references resolved; one resolving to
  nothing refuses `choose-argument-empty`), the `OPTIONS` the names of
  `next:`, a name outside them a miss that repairs.

The decision comes after the exit checkpoint, and the successor enters as a
SIBLING: an injected `CALL` in the caller's frame, right after the `CALL` that
just resolved. The laws of the document that left fall with it, the root's
hold on the whole path, a workflow of ten steps never stacks ten frames, and
the production of the one that left is the successor's upstream (its seed,
under `input:`). A successor declares its own `next:` in turn; a rewind or a
repair of the caller purges the injected CALLs, so a workflow under a session
cycle replays afresh, and `-compacted` finds the injected CALLs at the slot.

The build judges the graph of the whole composition:

| Refusal | When |
|---|---|
| `next-cycle` | a loop, its parts named |
| `next-undecided` | two names or more without a decider |
| `choose-and-decide` | `choose:` and `decide:` together |
| `decision-idle` | a decider with fewer than two names |
| `next-unplayable` | `next:` on a document the engine never CALLs as a proc |
| `reference-unknown` | a name nowhere |
| `format-mismatch` | an edge whose `output:` and `input:` differ |
| `next-keyword` (at parse) | a written `NEXT` |
| `next-floor` | a document carrying `next:` booted as the floor |

Each transition leaves a `next` line at the trace (the document, the
successor, `by: alone|skill|agent`) and `-stats` counts the transitions.

**Fusion** (`SETTINGS.fusion: max | <n> | none`) lets one output carry a whole
certain stretch — the batch closes on a `§`, a value the tool must capture, a
`FINAL`, the serve budget or the cap; a document's own `fusion:` key pins its
frame's pace.

**`output:` / `input:`** chain steps into pipelines: a consumed production is
captured — inline or stdin, the format's mode decides — and seeds the callee.

Everything else is held by the conductor: the state **is** the instruction
stack, the run survives the process, and anything unresolved **refuses** —
exit 2, a named reason, nothing played.

## The front matter, key by key

| Key | Declares |
|---|---|
| `name` | the document's identity (a skill directory's name IS the identity — `SKILL.md` is the mold) |
| `kind` | `proc` · `doc` · `boot` — a `doc` never executes |
| `description` | the catalog line — required for anything offered |
| `proc:` | the flow; its presence makes the document conducted |
| `output:` / `input:` | the pipeline's two ends — names of the formats enumeration |
| `serve:` | reading sections (paragraphs), one per bare `SERVE`; each line a grouping, its nature first, then its tokens separated by blanks — a blank inside a token's brackets does not separate; a token is `DOC`, `DOC[start..end]` or, as a last resort, `DOC[x-y,…]` (see `SERVE [doc]`) |
| `tools:` | this frame's offers — `+name` adopts a harness skill, or a proc of the house the instance is installed under |
| `constraints:` | the laws, `CODE  text`, ONE line per law |
| `formats:` | form declarations `name  mode  description` — extends the enumeration |
| `attach:` | the HOOK socket this document answers |
| `mount:` | the HOOK socket this document ENTERS at -- its laws, offers, body and readings ride the view there, it asks nothing |
| `mounts:` | what this document MOUNTS at its own sockets: a table `<socket>: <names>` (`turn.begin: HOUSE.md`, a name or a list), the socket as its `proc:` writes it -- written on the document or on an overlay of it; the names mount after the socket's `mount:` contributors, each under its own `when:`, and resolve as a CALL does, the house of an agent included (`mounts-hook-unknown` for a socket the proc never hooks) |
| `order:` | one line per pair, `<hook> before\|after <package>` — where this contributor stands among the socket's others; a peer the composition lacks is inert; the word `exec` in the socket's place orders several `exec:` on one document |
| `exec:` | `<verb> [args]` — a skill the engine plays once at every ENTRY of this document (a CALL, a mount, a lap of an iterated door), before the body and before anything it serves; the skill is the `pp-<package>` of the file's own package (a document of the instance names one of its own skills first: `exec: <skill> <verb>`); an argument `@Doc.field` takes the value a guard would read, never empty; a non-zero exit refuses `exec-refused` and nothing enters; what the skill prints goes to the bus alone (`::push`, `::clear`), a `::mount` refuses `exec-mount`; the base and each overlay may declare their own, each playing its own package's skill |
| `cycle:` / `fusion:` | `true` the session floor, `<token>` the iterated door · the frame's own pace |
| `field:` | the DESCRIBED door: the prose of what the door turns on — its presence declares the door; the engine asks the agent for the field once (`INFER field`, a JSON array judged on its form), then serves one element per lap under `field`; never beside `cycle:` |
| `next:` | the SUCCESSORS the document may leave to — names as `CALL` writes them; one follows alone, several are decided at the exit and the one elected enters the caller's frame as a sibling CALL; the graph of the composition is acyclic (`next-cycle` at the build) |
| `choose:` / `decide:` | the decider of a `next:` of several names — `choose: \|` the prose the agent reads at a `PICK next`, `decide: <verb> [args]` the owner's skill that prints the name; one of the two, never both |
| `override:` | `true` on `SYSTEM_PROMPT.md` — composes the replace artifact |

Any text file serves whole — there is no terminal marker: the hash pp computes
on what it serves is the proof of what was served. `SETTINGS.md` is documented
in place (the template) and in `PP_CHEATSHEET` key by key: the engine's
defaults and the seeded values are the same.

## Writing your own procedures

Your own procedures live in `.pp/procs/` — a markdown document there, shaped
like the `REVIEW` example of the README. Two seams let you extend a package's
procedure **without ever editing it**:

- **flow** — a package proc declares `HOOK <name>`; any document of yours
  with `attach: <name>` is called there;
- **sections** — a document of the **same name** in `.pp/procs/` is an
  **overlay**: its `constraints:` and `tools:` are deltas over the bundle's
  (`+CODE  text` or `CODE  text` adds, `-CODE` removes; same `+name`/`-name`
  for tools). The bundle's procedure keeps executing — an overlay that
  declares a `proc:` is refused, and so is a delta that changes nothing.

### Packages declare their settings too

The conductor's protocol keys are seeded bare at the template; the base
package declares its own in a `settings/SETTINGS.md` fragment, bare too (the
kit's `capture_prompt`, and `capabilities` -- `false` boots straight to the
turn, without the `CAPABILITIES` step and its catalog; the member's
`CALL CAPABILITIES.md ^ @SETTINGS.capabilities` reads it, and no effort
presets it: the written value rules). A package beyond it carries the same fragment: its
own keys (each wearing the package's prefix — `plan_`), their defaults and
`types:`, its `effort:`/`role:` presets and its SECTION of the instance's
SETTINGS body. Install, upgrade and doctor compose the file from the system's
template and the fragments in the requires topology, the operator's values
kept.

### Packages overlay too

A package's `overlays/` directory is its own overlay space, interposed between
the user's and the packages' bases: a same-name file there applies AFTER the
deeper bundle and BEFORE the user's (the user always wins), and it can never
become the base itself.

Between packages the order is the REQUIRES topology, never the pins: a
dependency's overlay applies first, its clients' after — a client amends what
it requires and wins; ties keep the pin order.

- **The body appends too**: an overlay's BODY joins the served text of its
  base — the packages' prose first, the user's LAST, the reading's hash taken
  over the composition; an overlay with no body appends nothing, and without
  overlays the served bytes are untouched.
- **The readings add too**: an overlay's `serve:` rows join the service of
  its base — served whole as the base enters, in application order, each
  titled by its token; a leading `+` on a row says the addition and is
  optional, a `-` refuses (`overlay-serve-removal`): an overlay never removes
  a reading. The base's own sections keep their `SERVE` pace, and a base whose
  overlays carry no row serves nothing more.

### Any bundled constraint bends — add yours, remove any

Every rule a **bundled procedure** holds in force — the kit's included — is
yours to lift or extend, by its code (your harness's own system, safety and
provider rules are not pp's to bend). Bothered by one? A file
`.pp/procs/TURN.md` holding nothing but:

```
---
name: TURN
constraints: |
  -T4
  T6  answers stay under ten lines unless asked otherwise.
---
```

lifts `T4` ("say what you are about to do, before you do it") from every block
the kit's `TURN` holds it on, and puts your `T6` in force in its place — the
bundle untouched, the delta yours, the build refusing a delta that changes
nothing.

## Offered skills — one rule, and adoption

**Every offered name is played through pp** (`./pp <key> -s <name>`) — the
invocation IS a `CALL`: a frame opens on the skill's contract, its
`constraints:` enter force (on top of the turn's, gone when the frame closes),
its body is served. What plays inside the frame is the contract's own affair:

- a **`proc:`** present — the declared flow plays, exactly as any procedure;
- **no `proc:`** — the implicit one plays: one `WORK`, the served body as its
  brief; the work is free (your judgment, your harness's tools), and the keyed
  call (`./pp <key>`) closes the step — the caller's flow resumes;
- a **script** beside the contract — the deterministic step runs, the
  gesture's block carrying the skill's own constraints.

### What a script prints

What the script prints leaves through the seam of every output: under the
host's cap exactly as written; over it in chunks, each opening on the output's
heading, the rest waiting at the run — the bare call serves it, any other call
bounces (`chunk-pending`), and the run does not move. A `::mount` printed by
the script joins the same output: one cut, one rest.

The trace weighs it: the `gesture` line carries the `chars` and `tokens` of
the text, then `cut` and one `chunk` per bare call. An output with no run key
(`-stats`, a package's command, `doctor`) has no run to hold a rest and is
never cut.

Called BARE — no argument — the script does not run: its contract is its
**manual** — the `SKILL.md` the skill's NAME addresses, wherever its package
lives (the instance or its vendor) — MOUNTED body alone into the
current view through the one reader —
cut at the host's cap, proven by its hash, in the ledger (`-stats --blocks`,
origin `mount`), swept with the exchange — and the standing block renders
under it, the run untouched.

### The scope resolves pending first, then the output's segments

A fused output numbers its headings (`[n]`) and each segment keeps its OWN
closed list — never their union. A bare `-s <name>` the pending block does not
offer routes to the ONE segment of the current output whose own list carries
the name: the gesture plays AS that step's — its block re-shown under its
snapshotted laws, the trace attributed (`gesture`/`routed`, with `segment` and
`frame`).

Several owners refuse (`address-ambiguous`) and `-s <name>@<n>` settles it —
the only time the number is owed; a later output retires the addresses
(`address-stale`). A routed `proc:` door still stacks over the pending step —
the stack never runs backward — inheriting the owning segment's laws, its
entry heading noting `routed from [n] NAME`. A door routed from a FREE step (the turn's WORK) takes that step with it: when the door's frame falls, the step is consumed by the door's production -- one production for the ask, never two (traced `consumed-by-door`). What rides a door's call as an argument (`-s ROUTE 7`) is ignored, said on the first line of the tool return (`pp: argument ignored: 7 -- …`) and traced `door-argument`; a door opens on its own documents and reads nothing from the call (plan fixes2, batch la-forme-du-tour). Offered by no segment, the
pending block answers and nothing plays.

### Adoption — the offer is the consent

A `+name` in a `tools:` that resolves nowhere in the instance -- nothing it
composes owns the name, a switched-off package included -- is looked up in two
places, the nearer first: the workspace's harness skill homes
(`.claude/skills/` · `.agents/skills/` · `.cursor/skills/`), then, for an
instance installed under another one whose machine it borrows (an agent under
its house), the house's own `procs/<name>.md`. A proc of the house is written
for the instances under it: adopted, it plays as one of theirs -- its laws, its
readings, its `@SETTINGS` keys and its CALLs resolve in the instance that
offered it, and its `attach:` or `mount:` never plays there (the offer opens a
door, it plugs nothing into the instance's turn). A name the instance carries
itself is never looked up in the house; the house's root, its overlays and the
procs nobody offers stay the house's. The catalog says where each adopted
contract came from, `(harness)` or `(house)`.

- A contract pp can conduct — a readable front matter and a `description:` —
  is **adopted**: full entry in the catalog, its constraints in the registry,
  played like any skill of the instance.
- One it cannot conduct stays a name-only offer — indifferent to pp, and
  `-build` warns (`offered-not-conductible`) with what it lacks.
- An **unoffered** copy in a harness directory stays invisible: pp never
  sweeps those homes — offering is what grants the read.

## The doors

The doors live at the **root**: `PP-MEMBER`, `PP-RULES`, `PP-OFFERS`,
`PP-MIGRATE` and `PP-DESIGN` ride every block of every session — a door named
by a recommendation (or by you) opens on your word, at any turn, with no
detour.

A door is a skill like any other, played through pp, its rules in force while
it is open; a change to your files is always proposed, never applied — your
word is the gate, in every door's own law. One law guards the practice from
the root: a door opens ONE at a time, the choice said before it opens.

## The operator's console

The install writes two scripts at the workspace root — `pp` (POSIX) and
`pp.cmd` (Windows: `.\pp`) — and every block's closing names them: they are
**the one spelling** of the conductor, for the agent and for you.

### The eight verbs

Eight bare verbs are the operator's own, resolved before any skill name:

| Verb | What it does |
|---|---|
| `./pp upgrade` | every pinned package moves to the version the source holds now, re-materialized — standing runs are RENEWED: each keeps its key and reopens at its next call (see "A run an upgrade renewed"), and the count is told; already current = a statement, nothing touched. At a machine, it DESCENDS to every instance that borrows it (see "Where the machine lives") |
| `./pp add <package>` | one more package into this instance, its prerequisites pinned (user-level files are protected: an edited file survives as `.old`, and a fresh sibling is offered instead) |
| `./pp remove <package>` | one package out — refused while another pin requires it |
| `./pp repo <name>` | a sibling workspace, installed with this instance's packages and wired with the providers detected here |
| `./pp doctor` | repair in place at **constant pins**: re-materialize, recompile, rewrite the console, refresh the wired projections — standing runs stand (`upgrade` is the void); at a machine, it descends too |
| `./pp acquit <vector>` | a treated signal vector stops asking: its counter and its latch fall together (see "The bus and the diagnostics") |
| `./pp version` | the source checkout and the pinned versions |
| `./pp help` | the console's usage — its own verbs, then the packages' commands |

`upgrade` runs the instance's OWN engine against the source, so an engine that
predates a move of the source's trees cannot read them: since `0.1.0-beta.23`
the bases live under `bases/` (the kit), and an instance on
`beta.22` or older refuses `package-unknown -- kit` at `./pp upgrade`. Run
the source's engine on the instance once — `uv run <source>/engine/pp.py
--instance <workspace>/.pp upgrade` — the pins move, the launcher is
rewritten, and `./pp upgrade` works again from there. The instance's own
documents are never touched by that step.

Two properties to know:

- **The scripts are the machine's own** — the exception at your root:
  rewritten byte-stable by install, doctor and upgrade, never yours to edit
  (an edit does not survive; that is what keeps the agent's channel
  unbreakable). At a first install, a foreign file already named `pp` refuses
  (`pp-name-taken`) — nothing is overwritten. The engine underneath answers
  the same calls: `uv run .pp/.sys/engine/pp.py …` is the repair path when
  the console is gone.
- **The eight verbs are reserved names** — a skill taking one of them is
  unreachable through `pp <name>`, and the build says so (a
  `skill-shadows-verb` warning, never a silence); a package command never
  takes one either (`command-taken`).

### The packages' commands

They resolve next, before the run's key. A package declares them in its
manifest — `contributes: commands: [{verb, skill [, args]}]` — and `./pp
<verb> [args]` runs the declared skill in a subprocess (the engine imports no
package code): the manifest's `args` first, yours after, its stderr written
to yours as the skill goes (a long skill can say where it is), its stdout
relayed once it ends, its exit code returned as is.

What the skill says to the bus (`::push`, `::clear`) is harvested on a clean
exit; a `::mount` has no run to land in at the console and refuses
`mount-without-run` after the skill ran. `./pp help` lists every command
after the console's own, in the composition's order (requires topology, then
declaration), with its package and the description its skill's contract
carries.

A command declared `tty: true` — `{verb, skill, tty: true}` — hands the skill
the terminal instead: stdin, stdout and stderr are the console's own, nothing
is captured or read back, so a skill that draws a screen owns it; its exit
code is returned as is. Such a skill never speaks to the bus: a `::push` or a
`::mount` it prints reaches the screen like any other line. The engine opens
no terminal and tests none — it hands over its streams, whatever they are, and
the skill judges them. `tty` is `true` or `false`, nothing else. A Ctrl-C at the
terminal reaches the console and the skill alike: the console ignores it while the
skill plays and waits for the skill to end — what the skill does with the signal, and
its exit code, are the answer. One code asks more (engine `0.1.0-beta.73`): a skill that
writes `then: upgrade` or `then: doctor` in its package's space of the metadata and exits
on `RELAUNCH` (75) asks the console to give back its hold on the machine, play that verb
at the terminal, then play the same command again, told `PP_RELAUNCHED=<verb> <exit
code>`. A command played again that asks again gets its code back: one relaunch, never a
loop. Any other verb refuses `relaunch-invalid`, nothing played. The post's `U` is its
first user.

The conflicts are settled at the build, nothing written:

| Refusal | When |
|---|---|
| `command-taken` | a verb of the console, or declared twice |
| `contribution-malformed` | a verb outside `[a-z][a-z0-9-]*`, or shaped like a run's key (six hex digits); a `tty` that is neither `true` nor `false` |
| `command-skill-unknown` | a skill that is no script of the composition |
| `name-unprefixed` | a verb that does not wear its package's name — `<package>-<verb>`, or the package's name alone |

At the console, a declared command whose script is gone refuses
`command-broken`; an undeclared word still answers the usage.

### The post of a house

A house that pins the `ui` package has a post: `./pp ui` opens a terminal screen
on the house's own terminal — a command played at the terminal, as above. The
post is a main, not an engine: it renders what the verbs of `pp` say and
delegates every gesture to them; it conducts nothing, writes no record and reads
no file of the instance. Textual is pinned in the skill's own script
(`textual==8.2.8`) and resolved by uv when the script re-executes itself; the
engine never imports it. `./pp ui --render <pane> --size WxH [--press <keys>]`
prints a pane as text and exits — no terminal needed, the keys pressed first;
`./pp ui` without a terminal refuses `tty-missing` in one line. The package's
README says the frame, the tabs, the keys and the least size.

The tabs come in the order Dialogue · Agents · Teams · Tasks. The DIALOGUE tab holds the
conversations open, one tab each, each holding its own `agent chat --json` on the post's
loop: `./pp ui ag1 ag2 [--run <key>]` opens one per agent named, before the post draws (a
refusal of the verb is relayed in one line, exit 2); with no agent named, the conversations its
memory kept come back at once, each DORMANT -- no `agent chat` until a message, `p`, `o` or `k` speaks
to it -- and its run's exchanges read in the background, shown as history (ui 0.47.0); `u` reads the
active tab's kept flow again, else its exchanges, and mounts it whole in one mount -- the same blocks
as the live, laid out once whatever its length; refused while a turn runs. A reading of the Teams, Tasks
or Agents tab that raises says so on the remedy line, and the post stands; `U` shows at the foot of every
tab. A tab whose flow ended stays with the refusal in its transcript, and `x` alone closes it. One run, one tab (ui 0.14.1): taking up a run a
live tab holds activates that tab and launches nothing; a run whose tab ended is taken up in place,
its transcript kept; closing a conversation ends the verb's whole process group, `pp-agent` and its
wake lock with it. Every overlay keeps its keys in sight, its body scrolling (ui 0.14.2); an event's
overlay titles itself on one line with the kind of the line, read from the flow's `kind`. `pp off`
shows in the tab itself, a banner and a bordered message line; `s` gives a conversation's statistics;
`U+FE0F` is taken out of what the post renders, so that tables stay aligned (ui 0.14.3). The
transcript reads a turn in the order
the flow said it (ui 0.13.0, agent 0.12.0): the principal's message as markdown; per launch ONE
line of the conduction -- the block it serves, as the `conduction` event names it (`blocks`,
read from the run's trace, never from pp's text) --, what the agent did meanwhile (ui 0.14.0,
agent 0.13.0: ONE `⚙` line per call of a tool, `pp` for a call of the agent's console, updated by
its result -- `✓`, or `✗` and the line red --, ONE `∴` line of the launch's thought, its words as `◀`
lines, the last ones not twice), ONE line of its steps counted by kind, ONE line of what the agent
answered; then the answer of the turn as markdown and the verdict. A line whose overlay has a
content to show is LIVE and opens WHOLE in an
overlay (`enter` or a click) -- a call its input then its result --, folded to the width and built
when it opens; a line with nothing to show (ui 0.15.0: a thought of a count alone, words or a result
left blank) is STALE -- the theme's disabled text, italic, no focus, nothing opens --, judged again by
its event's fields at each update, so a thought turns live when its text comes; `c` hides the lines of conduction, of steps, of calls and of thought and shows them
again; every block is
selectable with the mouse and copied by `ctrl+c`; an overlay renders the agent's answer and words as
markdown, any other content as the text it is (ui 0.28.0). While a turn runs, a spinner turns on the
tab's title and the status, bold in the theme's accent and followed by how long the turn has run, and the
message line holds what is typed until the turn ends.
The message line holds several lines (ui 0.20.0): one row at rest, growing to 8; `enter` sends the
whole text, `shift+enter` -- or `alt+enter`, `ctrl+j` -- goes to the line (ui 0.28.0). The footer
lays its keys on as many lines as the width asks, a line breaking between two keys only.
A tab knows its run from its opening, before any message (ui 0.16.0, agent 0.15.0): the flow's `ready`
gives the provider, the policy, the packages, the cap and whether it is conducted -- read from its fields,
no line of the transcript for it --, so the status line, `k` and `p` hold before anything was sent.
A turn is stopped by its `■ stop` button, shown beside the message line while the turn runs, or by
`ctrl+g` (ui 0.17.0); `escape` never stops a turn, it leaves the message line.
Above the transcript, a bubble says the principal's message of the turn at the top of the view, rewritten
only when that turn changes; beside the message line, a gauge says the run's context as `context` of
`agent stats --json` says it -- `ctx ▰▰▱▱▱▱▱▱▱▱ 17% · pp 33%`, pp's share in the theme's accent, `ctx —`
without one --, read after each verdict and when a run is taken up (ui 0.31.0).
On a conversation, `p` opens the parameters of its run and sends the changed ones as a `set`;
its last field is the run's NAME, played by `agent name` -- at once, or at `opened` for a run that
opens (ui 0.28.0); the status says the run's budget once the flow says it (`budget {cap, spent,
left}`, agent 0.19.0): `budget 0.42/2.00 USD` and a bar of ten cells, green, yellow past 80 %, bold
red at the cap;
`o` suspends its conduction or brings it back (`conduct` to the verb: `⏸` on its tab, `pp off`
on the status; under `pp off` a message is a bare exchange, the verdict `unconducted`); `k`
opens the packages its run plays beyond its base in an overlay that edits them -- `space` toggles
a line and sends nothing, `enter` sends one `package` per line changed, `escape` nothing (ui
0.20.0, agent 0.16.0); a switch the verb holds waits until it plays (`pending`), seen meanwhile as
`⧗` on the tab, `packages: … …` on the status and `… pending` at `k` — the state shown is always
the one the flow said.

The AGENTS tab is the table of the agents of the house, read from `agent list --json` and
`agent status --json` at the start, on `u` and after every verdict, never polled. The HOUSE
itself heads it (agent 0.11.0, ui 0.12.0): `.` names the house's own instance for every verb of
`agent` -- `./pp ui .` and `n` on its line open a run NEW on it, with its threads, its plans and
its continuity; its face counts its runs of the post alone, the conversations of its host
(VSCode) staying out (`run-unconducted` on one of them), and `--work` on it refuses
`work-on-house`. On an
agent, `enter` opens the overlay of its runs — `enter` resumes a run in a tab of the dialogue
with its kept flow replayed as it was lived (`agent flow --json`; `agent exchanges --json` for a run that keeps no
flow, ui 0.45.0) -- a run is named in its parameters (`agent name`
-- what a user types, one line of 1 to 60 printable characters, accents kept, agent 0.23.1) --, `P` purges
the run under the cursor and `B` the agent's runs before a date, SHOWN first (ui 0.30.0): `agent purge` played
without `--yes` says what it would remove, and its `--yes` command plays only once the run's key -- or the date --
is typed as it is, `--force` offered after `workdir-unpushed` under a second typing, every refusal of the verb on
the remedy line; each run and each agent says its `weight` (agent 0.23.0), `s` stacks
its statistics (`agent stats --json`: the run, pp as the engine counts it, and the context
approached from the run's flow -- the same overlay as `s` on a conversation's tab; ui 0.21.0),
and the table of the runs says each run's `pp` and `ctx` (`~xx %`, read from `context` of
`agent status --json`) — and `n` asks for a new run: the parameters of a run --
provider, model, budget, effort -- live in ONE overlay, prefilled with what the agent last
played (`last` of `agent status --json`, the models and the spells of `agent providers
--json`) and the permission regime (`auto` left blank, `strict`, `bypass` warned), then the
line of its PACKAGES, read from `packages` of `agent status --json` and toggled in their overlay
(ui 0.35.0: that overlay is the PROFILE of a launch, `ProfileScreen`, the one form wherever the post
launches something; a package the caller holds required is greyed and never toggles), and `enter`
opens the conversation with those flags -- one `--package <name>=on|off` per package changed among
them -- after the ones of `--`; `p` sends a package changed on its line as `k` does; on a run, `p` changes the regime
too, a `set` like the model's (`policy-unsupported` for a provider that does not spell it). `a`
plays `agent add <path>`, its exact command shown first. The post types nothing outside a
conversation's message line: what it asks, it asks in an overlay, the cockpit's form,
overlays stacking. What follows `--` goes to every `agent chat` the post opens (`--harness`,
`--permissions`, `--launches`).

The TEAMS and TASKS tabs (ui 0.22.0 to 0.27.1, recomposed in two at ui 0.29.0) show the teams of the house
as `team status --json` says them, from the first time each is shown, and pilot them by the verbs of `team`
alone. Each is a MENU on the left and a CENTRE of horizontal bands -- never two parts side by side --, the rest
in overlays; under 70 columns the menu folds into one line, which `[` `]` (and `{` `}`) change -- the layout
alone does it, no code reacts to a resize. The TEAMS tab says WHO the teams are: the menu of the teams
declared (each name in the look of its `state` -- `working`, `waiting`, bold when the owner alone lifts what holds
it, `paused` with `⏸`, `idle`, `never` (team 0.30.0, 0.32.0; ui 0.38.0) --, the wake-ups under way, the questions to
the owner as the inbox counts them, the tasks done not seen, `-` for a team never started); the head of the
team chosen -- its owner and mandators, its state (`waiting · owner, budget`, `paused since … by …`), its budget as the face says it (`budget 1.84/2.00 USD · reserved 0.10 ·
left 0.06`, team 0.22.0), its wake-ups against their bound, its net, what waits for the owner counted on one
line --; its members (the agent, the run, how it stands, the tasks, the debts it still owes -- `owes`, bold yellow once one
was reminded --, `live`; a member the face says suspected in bold red with `try HH:MM`; ui 0.40.0, team 0.36.0). The team's ONE `team watch <name> --json`
follows the team chosen -- its objects read on its stderr -- and every object but `quiet` reads the team again;
the post holds at most one watch per team, shared by the two tabs, a thread and a read tab, never one per task
(ui 0.32.0): choosing another team leaves the first's, ended when nothing else follows it, leaving the post ends
every watch whole. The TASKS tab says WHAT the teams do:
the filters `SHOW` (`running` first, `for you` -- a question to the owner or an end not seen, as the face's
`waiting` lists them --, `stopped`, `resolved`, `all`) and `TEAM`, each with its count; the tasks of every team
started they keep, read by one `team status <name> --json` per team -- the id, the name, else the start of the task's
text cut at 30 characters (`text`, team 0.27.0), the holders, the progress counted on the face's `dos`, its cost
(`cost`, team 0.39.0; ui 0.45.0), the age of the last event (`last`, team 0.27.0; `3 min`), the spinner before the name of a task a wake-up plays
(`running`, team 0.30.0; ui 0.37.0) and the tab's title counting them, `4·Tasks ⠹ 2` --; then the task under the
cursor whole -- its name, its text whole, its cost (ui 0.45.0) -- and its LAST ACTION (ui 0.32.0, team 0.28.0), ONE `live:` line per member (ui 0.37.0): the last step a
wake-up of that member said on the task, tied to its member and its task by the step's own `agent` and `task`,
then the last call of a tool of that wake-up read from its kept flow (`agent flow <path> <run> --exchange <index>
--json`, one reading per member at a time), dim once that wake-up ended; `launched` for a member the face says
running with no step seen (`launched 12 s ago`), `relance owed` after the run of a wake-up the face says is a reminder; a task at rest says its `last` event. The members of the Teams tab say `live`: a
member's last step on its team's watch, or `since` while the face says it running. Every freshness of the two tabs is
an AGE against the post's one clock, the hour of its reading on the status line (ui 0.40.0): `12 s`, `3 min`, `2 h`,
`3 d`, the menus saying `read 12 s ago`; the thread of a task and the journal keep the hour of each event, and say
the debt in the face's words -- `re #45`, `notice about lead`, `by tick · preempted`, `(was done)`. `enter` opens its THREAD in an overlay: its
history read by `team log --json --task`, then what the team's watch says that names the task, the history read
again at the overlay's first object and at an end of a wake-up -- an `id` shown once, nothing lost --, and a
`live:` line with the last step of a wake-up of the task. Each
gesture's command is made from what is chosen and SHOWN before it plays, word for word, its refusal on the
remedy line as the verb said it, the team or the tasks read again after it. A gesture that asks more than a
yes is written in an overlay (ui 0.33.0): its fields, each with its help, the command they make under them,
`enter` from any field playing it; a field left as it opened composes no flag. On Tasks: `m` writes on the task
under the cursor -- `to`, `as`, `reply to` read from `team status --json`, the owner writing no `--as`, then the
text --; `s` stops the task, `r` resumes it (a message, `as`), `k` kills its wake-ups once its id is typed, `v`
shows its result (`team result`), `n` posts a new task (its team, its name -- `--name` --, `to`, `as`, its
message), `l` shows the journal -- each gesture on a task titled by its id and its name, `T3 · review PR 88`. On Teams: `N` gives birth to a team from a template (ui 0.34.0, team 0.25.0) -- the form reads `team templates --json`, plays `team new` as it shows it, a field left as it opened composing no flag, the post writing no file; `ctrl+s` then starts the team born --, `n`, `T` ticks, `S` opens the SEASON of the team (ui 0.36.0, team 0.32.2:
`SeasonScreen` -- `all` and one line per member of `declared` (`team declaration --json`), each edited in its
`ProfileScreen`, a member's field left empty `all`'s, a package the face says `required` greyed; a new season opens on
the face's `launch` and `members[].launch`, a first one on the agents' `last`; the command composes what `all` carries
-- `team start` keeps only what it is given --, each member's changes and switches, `--budget`/`--budget-wakes` where
they differ from `TEAM.md`'s, never a `--max-budget-usd`; the message owed when no task is open; a declaration `start`
would refuse opens nothing), `B` raises its budget (`team budget`, prefilled
from the face, a field changed alone played), `b` shows the owner's inbox (`team inbox --json`: `enter` on a
question replies on its task, `x` marks it seen), `e` its declaration (`team declaration --json`, read only),
`X` stops all tasks once the team's name is typed, its overlay saying what it stops as the face counts it, `P`
pauses the team or resumes it when the face says it paused (`team pause`, `team resume <name>`, `--as`; ui 0.38.0),
`l` the journal; on a member, `R` resets its run once its name is typed, `d` shows it whole, `a` its
responses (`team responses --json --agent`). The tabs compute no state of a team and hide no key by one: `team`
judges. The run of a MEMBER is read in a tab of the dialogue (ui 0.25.0): `enter` or `i` on a member, or `enter`
on a run the overlay of an agent's runs marks `<team>/<member>` (read from `team status <name> --json`, the
member's `path` and `run`), opens it with a `◉ read only` banner and no message line -- no `agent chat` holds
the run the team wakes --, its kept flow replayed as lived turns (`agent flow --json`: what pp served, the calls,
the thought, the answer; ui 0.32.0), then its wake-ups live from its team's watch, of which it keeps the objects
of that member AND that run, the exchange a step names read again; a run without a kept flow (before agent
0.22.0) is replayed from its exchanges. The CEREMONIES open over the Teams tab
(`c`; ui 0.26.0, team 0.19.0 for `team ring`): their table says the progress of each last ring (`1/3 any 2`,
counted on the face's `progress`), the detail its chain (`after`, `then`), the participants still waited for and
the wait the task of its last ring carries, as its `waits` say it; `g` there rings the ceremony under the cursor
at hand (`team ring <team> <ceremony> [--as]`, the command shown under the table, `ceremony-open` on the remedy
line), and `enter` leads to the task of its last ring on the Tasks tab. `./pp ui --render <pane> --regions` says
where the menu, the folded line and each band of a pane stand -- what the bench measures. A `--harness
<command>` given after `--` to `./pp ui` rides `team start` when `S` starts a team (ui 0.27.0), with the
`--provider <name>` beside it -- the grammar its output is read in, in place of the overlay's provider (ui
0.27.1) --, before any `--member` of a season (ui 0.36.0), and no other flag of `--` does; the tabs are proven on the REAL verbs of `team` too, a team of the
bench woken by `team`'s own witness harness, never a provider (`ui-real-team-*`): a team born from a template by
`N` and started, a named task followed in Tasks to its thread, the budget raised by `B`, the inbox read and seen
by `b`, the declaration and its gap by `e`, a reply, a stop and a resume, a ring at hand.

A run resumed -- from the Agents tab or from the memory -- keeps what it was: `agent chat
--run` takes the provider of its session and its last policy for what the call does not name.
`t` opens the list of Textual's themes, light then dark, the current one marked: the one under
the cursor shows at once, `enter` keeps it in the memory, `escape` brings the one of before back.

The post reads the faces of `agent` and plays its verbs; the one thing it writes is its
MEMORY of the conversations open -- the agent and the run of each tab, in the space `ui` of
the instance's `metadata.json`, through the engine's face (`metadata.update`) -- and `./pp
ui` with no agent named opens them again, each with its history.

### What a launched script knows

**Its run.** Every script the engine plays under a keyed call — a payload
provider, a sink, an `exec:`, a family's verifier, a `-s` gesture — finds the
run's key in its environment as `PP_RUN`: set once where the engine binds the
run, inherited by every subprocess it launches, read in the same process by a
gesture.

Through the engine's face a script reads that run:
`conductor.context.current(<instance>)` gives `key`, `exchange()` (the
exchange under way, 1 at the first), `is_new()` (the run's first exchange) and
`is_boot()` (the run's first exchange, the one where `-compacted` was
declared, or the one a renewed run reopened at) — a reading of the run's slot, never a write. Without `PP_RUN` the
face refuses `context-no-run`: the keyless console (`./pp <command>`, `./pp`,
`-stats`) drops whatever the shell inherited, so a run is designated by a
command's key alone; a key no run holds refuses `run-unknown`.

**Its instance and its engine.** A script the engine launches (a payload
provider, a sink, a check, a command, a gesture) is a file of a bundle in the
vendor of a MACHINE: it imports the engine of the machine it finds by walking
up from its own file. The engine names, in the script's environment, `PP_HOME`
-- the instance the call serves -- and the script takes it as its instance
when that instance BORROWS the machine the script lives in; otherwise its
instance is the machine's own. A neighbour's script, launched by another
instance's, keeps its own home: the caller's instance does not borrow the
neighbour's machine.

**Its settings.** A script never opens `SETTINGS.md` itself: it reads a value
through `conductor.settings.of(<instance>)` and writes one through
`conductor.settings.write(<instance>, <key>, <value>)` — the one face that
poses a setting. The key must be one the instance knows: a protocol key, a
key a pinned package's fragment declares, a switch `package.<name>`, a
`cap.<sector>`, a `material.<name>`; any other refuses `settings-invalid`.
The write changes ONE line of the front matter — rewritten in place, or added
before the closing `---` when absent — and leaves every other byte as it was;
the value is judged by the same reading `of()` makes, so a value the reading
would refuse is refused by the write, `settings-invalid`, and the file stays
as it was. The call returns the previous value, empty when the line was
absent. Fixture `tests/engine/state/settings.py`.

### Which instance a call addresses

Every call may say it: `--instance <dir>` — the instance directory itself
(`<workspace>/.pp`), wherever the flag stands in the call — comes first.

Without it, an INSTALLED engine conducts the instance it lives in, exactly as
before: the console `./pp` passes nothing, and a `PP_HOME` inherited from
another instance's script never redirects it. The `PP_HOME` variable serves
an engine that has no instance of its own — the product's checkout — the case
of a harness a script launches.

The flag lets the product's own engine open or advance a run on any instance
from any directory (`uv run pp/engine/pp.py --instance <dir> -new`). A
directory carrying no `instance.yaml` refuses `instance-missing`; nothing is
played.

### Where the machine lives

An instance that carries `.sys/engine/` plays its own machine -- the classic
instance, the engine and the bundles copied under it. An instance that carries
none BORROWS the machine of the nearest instance of the same name above its
workspace (`<ancestor>/.pp`): it plays that machine's engine, its versions and
its composition, and pins nothing of its own; its own `package.<name>: off`
switches narrow what it plays. Nothing is written to say so -- the tree is the
authority. No machine above refuses `machine-missing`.

- **Birth.** `./pp -install <dir>` played at the console of an installed
  engine seeds an instance that BORROWS when `<dir>` lies under a machine: the
  root seeded, a manifest that says who it is (slug, birth) and nothing of a
  machine, its records seeded, its SETTINGS composed, its launcher -- `pp`
  running the machine's engine by its relative path and addressing the
  instance (`--instance`) -- and its marble and catalog compiled; no `engine/`,
  no `vendor/`. `-own` gives it a copy of the machine instead; packages and
  `-base` are the machine's (`install-borrowed` otherwise). Played by the
  product's engine, `-install` copies the machine as always.
- **The machine's verbs.** `doctor`, `upgrade`, `add` and `remove` are played
  at the machine; in an instance that borrows one they refuse
  `machine-borrowed`, naming the machine. At the machine they DESCEND its
  workspace: every directory below whose `<dir>/.pp/` is an instance without
  an engine is a borrower; a directory whose `.pp/` carries its own machine
  belongs to that machine and is not entered, and the hidden directories are
  never walked. The machine and its borrowers share ONE maintenance lock (see
  "Maintenance under living runs"): while a pp process lives at the machine or
  at any borrower, these verbs refuse `maintenance-busy`. `upgrade` rewrites
  the machine, then does each borrower's STATE work (SETTINGS, seeds,
  launcher, marble and catalog: `<dir> restated`) and closes its runs.
  `doctor`, `add` and `remove` restate the borrowers too; their runs stand.

### Which base an instance stands on

`-install <workspace> [packages…] -base <package>` composes the instance on
the named package instead of the kit: the manifest says `base: <package>`, the
composition is `[base] + packages`, and `./pp remove` refuses the base by
`package-base`.

A base OWES `procs/BOOT.md`, `procs/TURN.md` and its `system/SYSTEM.COMMON.md`:
the build judges the target before anything is written and refuses
`base-incomplete` or `base-silent` by name — the target directory does not
exist after the refusal. An install that names no base writes no `base:` and
stands on the kit, as it always did.

### The rest passes through

Anything else passes through verbatim:

| Call | What it does |
|---|---|
| `./pp` | where the run stands, read-only |
| `./pp <key>` | advances it |
| `./pp <key> -s <skill> [args]` | plays a skill (a script called bare mounts its manual) |
| `./pp -test [-serial\|-detail] [-repeat <n>] [area\|name\|path ...]` | runs the engine's fixtures: `-serial` plays them live, `-detail` renders what they wrote, `-repeat <n>` compares n passes and names whatever moved |
| `./pp -stats [<key>\|<days>] [--blocks] [-json]` | says what the runs cost |

The raw engine also accepts `-sync` as its low-level re-materialization
primitive; the operator's complete repair at constant pins is `./pp doctor`.

## Switching a package off

A package is composed for good, and yet a session does not always want all of
it. Two switches take one out of the CONDUCTION, and they have exactly the
same effect: nothing of that package is served or played — no document,
socket, cadence, check, command or overlay, no line of the catalog (no entry,
no format, no offered name: a `tools:` naming its skill offers nothing, and
the catalog leaves to your harness only the names nothing pp composes owns) —
and every package whose `requires` names it goes out with it, its cause said.

The base is never switched off, and off is not GONE: the pin, the bundle, the
package's section of `SETTINGS.md` and its records stand as they are, so `on`
brings everything back.

| Switch | Where | Lives |
|---|---|---|
| durable | `package.<name>: on\|off` in `SETTINGS.md` — yours to write | until you write the other value; seeded `on` when the package enters (install, `add`, `upgrade`, `doctor`), dropped when it leaves (`remove`) |
| for one run | `./pp <key> -disable <package>` · `./pp <key> -enable <package>` — the agent places it on your word | with the run: a run opened beside it plays every package, and `-new` starts with nothing out |

### A package that may use another

A package names under `optional:` in its manifest the packages it may USE when they
are there, beside the ones it `requires`. A document of it that mounts or attaches at a
socket of an optional package -- `mount: steering.threads.begin` -- is a SOFT reference:
when the package is in the composition the document plays at that socket without the
package being required; when it is not pinned, the document SLEEPS -- nothing hooks its
socket, nothing serves it, and `pp build` says so once in its warnings:
`mount-dormant: `steering.threads.begin` mounted by …/NEXT_MOVE.md -- `steering` is not
pinned: the document sleeps` (`attach-dormant` for an `attach:`). A socket the present
package declares nowhere, or a socket of a package neither required nor optional, refuses
as before (`reference-unknown`, `attach-unhooked`, `dependency-undeclared`); a name
optional AND required, or a package optional to itself, refuses `manifest-malformed`.
Off is not absent: a package switched off is still pinned, so its client's document is
not dormant -- it simply never plays, since the switched-off package hooks nothing.

The run's verbs answer with the block that STANDS: a switch is your word,
never a step, so the run does not move. Three refusals name their reason and
write nothing:

- `package-base` — the base of every instance;
- `package-unpinned` — no such pin here;
- `package-in-flight` — a document of that package holds the standing view —
  a frame of the stack, or a standing mount under any of its address forms
  (a document by its name, a manual by its skill's name, a file by
  `<package>:<path>`), each named as the run keeps it: the frame finishes,
  then the word plays.

Each one is written to the run's trace, and `./pp -stats` counts them among
the period's switches.

What a run plays is said UNDER the heading of each of its outputs, one cell
per pin beyond the base, dependencies first so a cause reads before what it
took out — here on an instance composing three packages of its own:

```text
▌ pp · run 71ccb9 · 19:28:28 · +0:00:01
▌ alpha on · beta off · gamma off (<- beta)
```

Keyless, `./pp` says the durable state alone when no run stands. An instance
that pins nothing beyond its base says nothing of packages, and a moved
durable switch recompiles the catalog and the standing rules at the next
boot — nothing to run.

## The adapter surface

The modes and their guarantees are the README's story; here is the exact
surface each flag wires.

The agent contract is ONE text — the engine's own card, `engine/refs/PP.md`,
carried by every instance with its engine and compiled into the marble.
Cards and the Gemini command are **projections with provenance**: a pristine
projection follows the current contract on day-2/doctor/upgrade; an edited
one is preserved, the fresh projection lands beside it as `.candidate`, and
the drift is said — the `card-drift` signal is the engine's own, pushed at
boot whether or not any package declares a check, and rendered as a
diagnostic (`card-drift · warning · <home> differs from the contract -- ./pp
doctor`) in the boot's block, once per run. Per-provider details and external
links live under [adapters/](adapters/); how pp launches ONE exchange of a
harness by its command line — the non-interactive mode, the exchange the
editor's extension launches, and the `launch()` contract pp adapts per
provider — is [adapters/README.md](adapters/README.md).

**The non-interactive face** — `conductor.adapters.launch(provider, workspace,
meta, prompt, marble=None, root=None, wiring=None, policy=None, session=None) ->
(argv, env, stdin)` composes the command line of ONE exchange of a session of the
provider and never runs it: the skill that calls it launches, writes `stdin` —
the prompt, whole — on the process's standard input, waits and reads the exit
code. The prompt is never an argument (engine `0.1.0-beta.59`): one argument is
bounded (128 KiB on Linux), a prompt that carries whole blocks is bounded by the
model alone; an adapter whose launch renders anything but the three elements
refuses `launch-malformed`. `session` left out OPENS a session, which the provider keeps and
names; the identity the provider gave RESUMES it (claude, gemini, cursor
`--resume <id>`, codex `exec … resume <id>`) — judged once at the face
(`session-invalid` for anything but a non-blank text); pp creates, keeps and
looks up no session, and no line throws one away. At every call of the model
the system prompt and the whole context reach the agent: claude and gemini,
whose sessions do not reliably record the system prompt, carry the marble and
the receipt at EVERY launch, the resume included; codex re-reads its config
by itself; cursor, with no channel, carries no receipt, and the standing rules
the engine serves inline ride the session's history. The
adapter is found by its path under the product (`adapters.product_of(meta)`:
the running engine's own checkout, or the `source:` the instance declares — a
vendored engine carries no adapters). `marble` left out lets the
adapter name the marble its own launcher carries (`system.replace.md` when it
stands); a marble handed wins — the marble of the run's mode, `system.common.md`
for a run its principal conducts, reaches the provider's channel as the adapter
spells it (claude the file, gemini the composition `wire()` made beside it, codex
and cursor read no marble at the call). `policy` is what the exchange may spend and do —
`{"model": …, "max_budget_usd": …, "permissions": …, "effort": …}` — judged once at
the face (`policy-unknown` for a key outside those four, `policy-invalid` for a value
that does not parse) and spelled by the adapter in its host's flags, or refused
by the adapter whose host has no such flag (`policy-unsupported`, naming the
provider and the key: the budget and a regime other than `auto` at claude
alone, the effort at gemini). `effort` says how much the model reasons --
`low`, `medium`, `high`, `xhigh`, `max`, each adapter mapping them to its
provider's channel: claude `--effort`, codex `-c model_reasoning_effort=…`,
cursor the model's suffix ([adapters/README.md § The effort](adapters/README.md#the-effort)).
`permissions` says what the harness may do without asking: `auto` (the
default) what it judges safe itself, `strict` the rules the house's settings
write and nothing else, `bypass` everything — claude `--permission-mode
auto|dontAsk|bypassPermissions` ([adapters/README.md § The permission
regime](adapters/README.md#the-permission-regime)). `wiring` is the directory whose harness
configuration is handed to the process — an agent's home, wired once: claude
reads its `.claude/settings.json` by `--settings`; the three others read
nothing. [adapters/README.md](adapters/README.md) spells both per provider.
`conductor.adapters.answer(provider, meta, stdout, stderr)` reads what the
harness ANSWERED beside its words, in the output format the adapter chose, as one
shape — `{cost_usd, denials, error, session}`, no text: claude's `total_cost_usd`,
`permission_denials` and `session_id`, its `subtype` as the error under
`is_error`; gemini's `error` and `session_id`; codex's `turn.failed` and the
`thread_id` of `thread.started`; cursor's `session_id`; a stdout no reading parses
says `unreadable` with its tail. The SCOPE of that `cost_usd` is what the adapter declares
beside its faces, `COST` -- `session` (claude: the session's cumul at that launch),
`launch` (that launch alone) or `None` (codex, gemini, cursor: no cost) --, read by a
caller through `conductor.adapters.load`, never by the engine. The session is OWED: a reading without it refuses
`session-missing`. An adapter without that face refuses `answer-unsupported`, one
without the `events` face `events-unsupported` (engine `0.1.0-beta.27`; the session
since `0.1.0-beta.30`; no text and `events-unsupported` since `0.1.0-beta.72`). Nothing
is run by either face: the skill that launched hands the streams it captured.
`conductor.adapters.events(provider, meta, line)` (engine `0.1.0-beta.63`) reads ONE line of
the harness's output as the exchange plays, through the adapter's third face, and
renders its events in a COMMON SCHEMA no host names: `tool` {id, name, title, shell, input} --
a call of a tool, `shell` its command when it runs one --, `tool-result` {id, content, error},
`thinking` {text and/or tokens}, `words` {text, delta} -- the ONE source of the model's text,
`delta` (true alone) a piece of a message the host streams in pieces. The face drops the
fields the schema does not name, poses the optional ones, and refuses `events-malformed` for
anything outside it; an adapter without the face refuses `events-unsupported`. Claude, gemini
and cursor are launched on their STREAM (`stream-json`), codex on its JSONL, and both faces
read it; claude's stream is verified on a machine, codex's, gemini's and cursor's are read in
their docs
([adapters/README.md § The third face](adapters/README.md#the-third-face-events)).

| Provider | `argv` | `env` |
|---|---|---|
| claude | `claude -p [--resume <id>] --append-system-prompt-file <marble> --permission-mode auto|dontAsk|bypassPermissions --permission-prompts none --output-format stream-json --verbose` — the mode from `permissions`, `auto` without it; `--system-prompt-file` on the replace marble; the marble at every launch; the prompt on stdin | `PP_MARBLE=1` |
| codex | `codex exec --sandbox workspace-write --full-auto --json [resume <id>] -` — the prompt on stdin, named by `-` | `PP_MARBLE=1` as data (plan fixes1) — `.codex/config.toml` carries the marble and sets the receipt for the CLI itself |
| gemini | `gemini [--resume <id>] --approval-mode yolo --output-format stream-json` — the prompt on stdin, no `-p` | `GEMINI_SYSTEM_MD=<marble>` (the composition of the marble handed, `system.common.gemini.md` for `system.common.md`, when `wire()` made it), `PP_MARBLE=1` — at every launch |
| cursor | `agent -p [--resume <id>] --force --output-format stream-json` — the prompt on stdin | — (no system-prompt channel, no receipt) |

| Refusal | When |
|---|---|
| `provider-unknown` | no `adapters/<name>/wire.py` under the product |
| `launch-unsupported` | an adapter that wires but composes no launch |
| `launch-malformed` | an adapter whose launch renders anything but `(argv, env, stdin)` — the shape since engine `0.1.0-beta.59` |
| `answer-unsupported` | an adapter that composes a launch but reads no answer |
| `events-unsupported` | an adapter without the `events` face -- the model's words cannot be read (at `events` and at `answer`) |
| `events-malformed` | an adapter whose `events` face renders no list, or an event outside the common schema (a kind outside `tool`, `tool-result`, `thinking`, `words`; a required field missing or of another type) — the adapter and the kind named |
| `policy-unknown` · `policy-invalid` | a policy key outside `model`, `max_budget_usd`, `permissions`, `effort`; a value that does not parse (an empty model, a budget not above 0, a regime outside `auto`, `strict`, `bypass`, an effort outside `low`, `medium`, `high`, `xhigh`, `max`) — refused at the face, before any adapter |
| `policy-unsupported` | a key the provider's CLI cannot spell — the budget, and a regime other than `auto`, at gemini, codex, cursor — named with the provider |
| `session-invalid` | a session that is not a non-blank text — refused at the face, before any adapter |
| `session-missing` | an answer whose reading carries no session identity — the provider named, the error read or the stream's tail cited |
| `source-missing` | a vendored engine whose instance points at a source gone |

| Flag | Card | Door (written by the flag) | Marble | Permissions |
|---|---|---|---|---|
| `-claude` | `.claude/skills/pp/` | `CLAUDE.md` | `claude-pp` | `.claude/settings.json` — `Bash(./pp:*)`: the `:*` covers the run key and every argument; written once |
| `-codex` | `.agents/skills/pp/` — a standard **Cursor reads too** | `AGENTS.md` | `.codex/config.toml` — pp manages exactly TWO fields (`developer_instructions`, the `PP_MARBLE` sentinel), spliced only when pristine, every other key byte-preserved | `.codex/rules/default.rules` — verify with `codex execpolicy check` |
| `-gemini` | `.gemini/commands/pp.toml` (`/pp` serves the card) | `GEMINI.md` — read natively, points at `/pp` | `gemini-pp` — the composition rebuilds on the current marble; the baseline moves only on explicit rewire | documented only: a `coreTools` allowlist may RESTRICT the whole tool set — choose your approval mode yourself |
| `-cursor` | `.agents/skills/pp/` — the same card `-codex` writes (shared, cumulable) | `AGENTS.md` + `CLAUDE.md` (Cursor-recognized) · `GEMINI.md` written for workspace interop | — no system-prompt channel: recall guarantee | `.cursor/permissions.json` — a `terminalAllowlist` PREFIX on `./pp` (the run key passes free); written once |

A bare install (no flag) writes the two generic doors — `CLAUDE.md` and
`AGENTS.md` — for a harness you wire yourself. Every door is ONE text (plan
fixes1): the first call, `./pp -new`, and nothing to invoke before it -- the
standing orders that call serves carry the card, and the skill or the command a
harness registers stays the operator's own, never a second copy the agent reads
first. `PP_MARBLE` is a **receipt**, not a switch: declared with nothing
compiled to carry, the boot refuses (`marble-missing`) rather than playing
blind. The house's own calls to an agent's conductor (`pp-agent`:
`principal_environment`) carry the receipt whenever the adapter's launch
declares it -- claude, gemini and codex do, as data of their `env` --, so the
boot block handed to the CLI repeats no standing orders the system prompt
already carries.

**Day 2** — a standing instance gains an adapter with the same flags, no
workspace: `./pp -install -codex` wires the current instance (several flags
cumulate); a replay answers `already wired`.

## The hook channel

The conductor knows **no provider and no harness**: integration is a set of
thin adapters over one contract —

```
./pp -hook    ->  the pending block, on stdout, plaintext
                  (silent once the run is over; never fails)
```

Any channel that can put text in front of the model alongside the operator's
message can carry the conduction: a harness hook, a middleware, a five-line
wrapper around an API loop, even a manual paste.

> The point of the channel matters more than the channel: the block must
> arrive **from the environment the model already trusts** — its harness, its
> caller — not as "run this script and obey its output", which any
> well-defended model rightly refuses.

**Generic API loop** — prepend the block to each user message:

```sh
block=$(./pp -hook)
send "${block}

${user_message}"
```

*Other harnesses follow the same shape: find the per-message injection
channel, wire `-hook` into it.*

## The instance on disk

```
workspace/                  # yours — whatever you actually work on, plus the doors
├── pp · pp.cmd             # the conductor's console — MACHINE-owned, self-repairing
├── CLAUDE.md, AGENTS.md, … # the wired harnesses' doors — written once, per flag
├── .claude/                # if you wired Claude Code — your own committed config
└── .pp/                    # the instance `install` seeded (default name; a parameter)
    ├── MEMBER.md · SETTINGS.md · FORMATS.md    # YOURS — identity, tuning, forms
    │                       # seeded in two layers: the engine's template (SETTINGS,
    │                       # FORMATS, the shelf of procs), then the base's user/ layer
    │                       # (the kit's MEMBER.md) — a base without user/ seeds no member
    ├── procs/              # YOURS — where a procedure of your own gets written
    └── .sys/               # the machine — nothing in it is yours to edit
        ├── engine/ · vendor/ · instance.yaml   # copied, pinned, repaired by `doctor`
        │                   # instance.yaml: source, slug, engine, the pins -- and `base:`
        │                   # when `-install … -base` named another base than the kit
        │                   # engine/system/SYSTEM.COMMON.md, SYSTEM.CONDUCT.md and
        │                   # engine/refs/PP.md: the orders and the card, the engine's
        │                   # own, compiled into system.md and system.common.md
        ├── records/        # operations.jsonl · history.jsonl · the records ·
        │                   # claims.jsonl (which run plays what is due once)
        └── state/          # session-<key>.json (a run's saved state) · its trace
                            # session-<stamp>Z-<key>.jsonl · its call lock,
                            # session-<key>.call.lock · a launcher's own files beside it
                            # (the agent package's session-<key>.wake.lock and .wake.log) ·
                            # maintenance.lock (the machine's: shared by every pp process,
                            # exclusive while a maintenance verb rewrites the machine)
```

`workspace/` is your project — your productions, your references, committed
however you like. `.pp/` is the conductor's own home: repaired at constant
pins by `doctor`, and re-materialized at the source's current versions by
`upgrade`; `.pp/procs/` is where you develop a procedure of your own, before
it ever graduates into a package of its own. The instance carries
**everything** it runs on, the engine included.

**One run, several calls.** A run's saved state is written by one call at a
time: every keyed call of the console but `-peek` holds the run's CALL lock
(`session-<key>.call.lock`) from its start to its exit — a harness that runs
two tools at once, or a second terminal on the same key, waits for it. The
wait is bounded: `call_lock_wait` seconds (SETTINGS, 30 by default), then the
call refuses `call-busy` and plays nothing — replay it once the first has
answered. A reader (`-peek`, `-stats`, the keyless `./pp`) takes no call lock
and blocks no call (like every pp process, it holds the machine's maintenance
lock shared). A process a call launches — a skill — inherits
`PP_CALL=<instance>:<key>`, the run its parent holds; one that calls that run
back refuses `call-reentrant` instead of waiting for ever. A key is reserved
by its SLOT, the same way for every run: `-new` creates the slot of the key it
draws exclusively; a LAUNCHER opens a run by playing `-new` itself, under the
principal's mark (`./pp agent run`, agent 0.4.0), and reads the key on the
output's first line. A key whose slot stands is never drawn. A launcher's own files
beside a run are its own affair: the engine names none of them (`./pp agent
run` holds its lock `session-<key>.wake.lock` for the wake-up's whole life;
see [packages/agent/README.md](packages/agent/README.md)).
Every write of the saved state arrives whole — a temporary of its own, one
rename — and a trace is named by its run's key and created once: two runs
opened in the same second have two traces.

**Maintenance under living runs.** The machine has ONE maintenance lock,
`state/maintenance.lock` beside the runs of the instance that carries the
machine; every instance that borrows the machine uses that same lock. It has
two modes:

- **shared**: every pp process takes it when it starts and keeps it until it
  ends -- a keyed call, `-new`, `-peek`, `-stats`, the keyless `./pp`, a
  package's command, the detached child of `agent start`. A process that
  launches a harness keeps it as long as it lives, so a wake-up keeps it for
  its whole length. Shared holders never block each other.
- **exclusive**: `upgrade`, `doctor`, `add`, `remove` and `-sync` try it
  without waiting. If any pp process holds it shared, the verb refuses
  `maintenance-busy` and reads and writes nothing; replay it once that
  process has ended. While a verb holds it exclusive, every other pp process
  refuses `maintenance-in-progress` when it starts and plays nothing.

An engine that a maintenance verb launches (a newer engine finishing the
verb) plays under its parent's hold: the parent writes a fresh token into
the lock file and hands it in `PP_MAINTENANCE`.

Under the exclusive no pp process lives, so `upgrade` takes no lock of a run:
it moves the pins, RENEWS every run of the machine and of its borrowers (below),
and sweeps the files of runs already gone. `-reset` is no maintenance verb: it
forgets each run under that run's call lock, tried without waiting, and a run
whose call is under way refuses `call-busy`. A call whose reader of stdout is gone
before the console prints (`| head -c 0`) has PLAYED: the run's state is saved before
anything prints; the console says it in one stderr line, exits 0, and `-peek` shows the
block that stands (plan fixes2).

**Purging runs** (engine `0.1.0-beta.66`). `-reset` forgets a run and keeps its
history: its trace stays, `-stats` still counts it. `./pp -purge` removes it for
good -- its slot or renewal mark, every `session-<key>.*` beside it (its call
lock, whatever a launcher put there), and every trace of its key:

- `./pp -purge <key> [<key> ...]` -- the runs named; a key no file belongs to
  refuses `run-unknown`;
- `./pp -purge --before <YYYY-MM-DD>` -- every run whose last write (its newest
  trace, its slot when it has none) is older than the date, and every trace
  that names no run (written before a trace carried its key) older than it; a
  malformed date refuses `purge-invalid`;
- without `--yes` the verb writes nothing: it says, run by run, the files and
  bytes it would remove, then the total; with `--yes` it removes them and says
  the same; `-json` renders that count as one object `{dry, runs: [{key, files,
  bytes}], files, bytes}` for a program;
- each run under ITS call lock, tried without waiting: a run whose call is under
  way refuses `call-busy`, and NOTHING is removed;
- the claims of `records/claims.jsonl` stay: a claim whose run's slot is gone is
  void already.

The verb plays on any instance -- a house, or an agent that borrows its
machine, from its own console. What a package's script writes (its records) is
that script's to purge.

**A run an upgrade renewed.** A run's state binds to the versions it was played
on; its key does not. The upgrade replaces the slot of every run standing -- a
chat waiting for its message, a wake-up between two calls, at the machine and at
every borrower -- by a RENEWAL MARK at the same path, `session-<key>.json`:
`{"renewed": {"at", "from", "to"}, "log", "turns", "off", "frontier"}` -- the
versions that moved, the trace's name, the exchanges completed, the packages the
run switched off, and whether the run waited for the principal's message. The
run's other files (`session-<key>.*`: its call lock, a launcher's file) go; its
trace stays and says `renewed`. The console says `n run(s) renewed by the update`.
A launcher's reservation no opening took holds no run: it is dropped.

- The next keyed call on the key REOPENS the run under it: the boot served as at
  an opening, the trace continued (`reopened`), the exchanges counted on, the boot
  set there (`context.is_boot()` holds at the reopened exchange), the packages the
  run switched off still off. One key, one trace: `-stats <key>` counts one run.
- The text that call carries is the principal's message when the run waited for it
  (traced `prompt`, served as `-new <message>` serves it); a production, a value or
  a verb (`-s`, `-compacted`, `-disable`) is NOT played, and the first block says it
  in its DEVIATION section.
- `-peek` and `./pp` on a mark print one line -- the run renewed, the versions,
  the call that reopens it -- and write nothing.
- A mark holds no cadence claim: the period is free for the next boot.
- A mark crosses a further upgrade: `to` follows, `at` and `from` are kept. It
  stands until its run reopens or `-reset` forgets it; `run-unknown` answers only a
  key forgotten or never handed.
- The upgrade that first installs this behaviour is played by the engine it
  replaces, which still closes the runs; the upgrades after it renew them.

The lock is `flock` under POSIX. Under Windows it is `LockFileEx` on one
byte far past the file's content (a Windows lock forbids other processes to
read the bytes it covers); this Windows path is written but NOT tested.

**What is due once is played once.** A cadence -- `HISTORY`, a dated step -- is
played by ONE run per period: the boot that finds it due CLAIMS its period (the
cadence's name and the last passage of its anchored weekday) at
`records/claims.jsonl`, under that record's lock, before the document is
injected; a boot that finds the period claimed by a living run injects nothing
and says so in its trace (`cadence-claimed`). A claim holds while its run's
saved state stands -- one rule for every run, whoever launched it -- and is
void once that state is gone; the next boot re-claims. A run that died during
its exchange keeps the period until it is forgotten: one period lost at most,
and no clock, the date is still computed from the records. The checks pushed at boot are not claimed:
a signal is the reminder of one run. The shared records -- the house's journals,
continuity's two -- are appended under their lock, and a reader skips a last line
still being written; every compiled artifact (`tools.md`, `system.md`,
`receipts.yaml`) arrives whole, by a temporary and one rename.

The root is seeded in two layers. The engine's template puts down what is the
protocol's own — `SETTINGS.md`, `FORMATS.md`, the `_`-shelved procs. The base
then places its `user/` layer over it: the kit's is `MEMBER.md`, the member's
identity; a base without `user/` seeds no member at all. One package at most
may carry a `user/` layer of its own (daneel does) and replaces the base's —
two such packages refuse `user-packages-conflict`. A file still equal to a
seed swaps silently on `add`; an edited one is saved to `.old` first.

A workspace that pins the `agent` package is a **house**: an agent is an
instance anywhere under the house that borrows the house's machine, and it IS
its PATH relative to the house, slugs joined by `/` (`ag1`, `rep1/ag1`) -- the
argument of every verb, its name in every record, its branch and its git
identity; two agents of the same name at two paths are two agents (agent
0.3.0). `./pp agent add <path>` gives it birth -- the engine's generic install,
specialized: the house's machine borrowed, no door, no host flag, the
launcher `pp` beside it, no `.claude/`, no wiring of its own; `agent-path-invalid`,
`agent-exists`, `type-unsupported` (a `--type` other than `member` or `chat`) refuse
before writing; `--type member` writes `capabilities: false` and `package.steering: off`
at the agent's SETTINGS, `--type chat` adds `continuity_memory_frequency: 0` and
`continuity_history_day: never`, a key whose package the house does not pin left and
named at the birth (agent 0.27.0); the
birth plays under the house's birth lock for that path (`state/born-<digest>.lock`,
`born-busy` past `call_lock_wait`; agent 0.3.2), so that a path is born once --
and `team start` does the same at the paths `TEAM.md` gives; `./pp agent list`
finds every borrower under the house by descending it; the house's
`./pp upgrade` reaches them by descending. `./pp agent run <path> (--message "<text>" | --message-file <path>)
[--model <m>] [--max-budget-usd <n>] [--permissions auto|strict|bypass]
[--effort low|medium|high|xhigh|max] [--new | --run <key>] [--provider <name>] [--harness <command>] [--json]
[--quiet] [--heartbeat <seconds>] [--dry-run] [--launches <n>]` wakes it for ONE exchange, as a message
typed in a session, CONDUCTED BY THE HOUSE (agent 0.4.0): the house plays `-new
"<message>"` on the agent's instance under the principal's mark
(`PP_CONDUCTED_BY_PRINCIPAL=true`, on its own calls alone), reads the key on
the first line and launches the harness in `<path>/` -- its environment naming
the run it conducts, `PP_CONDUCTED_RUN=<key>` (plan fixes2): a `-new` the model
plays inside that launch, while that run stands mid-exchange, opens nothing and
says so in one line; a `-new` played without that variable, or naming another
run, opens even while a run of the post stands (an editor's conversation beside
the post) --, in a session of its
provider, on the PROMPT -- the message under `[message from your principal]`
then pp's whole output, every later launch pp's output alone --; after each
launch it reads the run (an output held by the agent's value, a chunk waiting,
a block to advance) and makes it advance by its marked bare call, one launch of
the harness per output that ASKS the agent something -- an output that parks the
run with nothing held, nothing pending and no instruction line, the bare FINAL
after a judged proof, is served and never launched (plan fixes2: a relayed
exchange under a law of production costs two launches, the boot with the WORK
then the checkpoint, and the exchanges after it one) --, until the run is PARKED
at its FINAL with nothing held: the harness's last answer is the response; `--launches <n>` (24 unless said)
bounds the launches of a wake-up (`launches-spent`: the last response kept, the
run left standing). `--max-budget-usd <n>` is the BUDGET CAP of the RUN (agent 0.19.0):
what it spends over all its exchanges and their launches, conducted or bare -- the sum
of its responses' `cost_usd` plus the launches of the exchange under way; before every
launch the remainder is computed -- none left, nothing is launched (`budget-spent`:
before an exchange nothing recorded, the run as it was; between two launches the last
response kept, the run standing) --, and handed to the launch's policy as
`max_budget_usd` where the adapter spells that key (`SPELLS`); a launch may go past it
by what the provider's own bound lets through, one launch where the adapter spells
none; under an adapter whose `COST` is `None` a cap refuses `budget-unmeasured`. With `--run`, the run's own session is reopened from
`sessions.jsonl` (the marked `<key> "<message>"` opens the exchange; a run left
standing is taken up where it stands, `standing resumed`; `session-missing` when
none is recorded, `provider-mismatch` under another provider). The harness
runs with the marble of the MODE (`.sys/system.common.md`), the house's wiring,
the policy and the session as data
(`conductor.adapters.launch`; the same face takes `workdir`, the material a run
works on under the agent's directory, and composes it the same for every
provider — the head of the prompt that names it and the console by its
absolute path, `PP_WORKDIR` and `PP_CONSOLE` in the environment, no provider
flag; `workdir-invalid`, `workdir-unsupported` — engine `0.1.0-beta.42`).
`--door <document>` (agent 0.1.12) names the run's ENTRY at an opening alone
(`door-on-resume` with `--run`): handed by `PP_DOOR`, read by `-new` alone
(engine `0.1.0-beta.44`), the document resolved by the agent's instance and
opened as a CALL above the boot -- the first exchange carries it,
`door-unknown` leaves nothing, the trace says `door`. `--documents <dir>` (agent
0.17.0) -- absolute, or relative to the house's directory -- gives the run its
ROOT of documents at an opening: handed by `PP_DOCUMENTS` on the house's `-new`
alone (engine `0.1.0-beta.64`, § `-new`), never inherited by the harness nor by
another call; under `--run` a root other than the run's refuses `documents-fixed`
before any launch; `chat --json` says it as `documents` in `ready` and `opened`.
`--package <name>=on|off` (agent 0.24.0), given once per package on `run`, `start` and `chat`,
names the packages the run plays: judged before anything is opened or written against the
packages the agent's instance pins (`package-invalid`, `package-base`, `package-unpinned`),
then each switch the run does not play already is played on the run under the principal's mark
-- the engine's `-disable` or `-enable` -- before the first launch, at an opening as at a resume,
and again before every launch while the package holds the run's view (`package-in-flight`): the
waiting list of a conversation. The state is the engine's, at the run's slot; no record gains a
field; `--dry-run` says `package <name> on|off` and plays nothing.
`--work <repo> [--base <ref>]` gives the run that material (agent 0.1.10):
before the launch, under the house's lock for the repository, a local clone
by hard links under `<path>/work/<key>` on the branch
`agent/<path>/<key>`; the git identity of the exchange in the environment
(the agent's path, `rep1/ag1 <rep1.ag1@<the house's slug>>`);
after the harness the branch is pushed back by the repository's absolute
path, and `workdirs.jsonl` keeps each run's material (`open`, `pushed` or
`unpushed` with its reason, `pruned`); `./pp agent workdirs` lists them,
`./pp agent prune <path> <key> [--force]` removes a clone -- a run pruned is never resumed
(`workdir-missing`). `./pp agent purge <path> (<key> … | --before <YYYY-MM-DD>) [--yes] [--force] [--json]`
(agent 0.21.0) removes runs FOR GOOD, each record by its writer: the house's records rewritten without
their lines (the one write of a record that is not an append), their clones, and, by `./pp -purge` played
on the agent's instance (beta.66), what the agent keeps of them; without `--yes` it says what it would
remove and writes nothing; all or nothing -- `run-busy` under a held wake lock, `workdir-unpushed`
(`--force`), the engine's `call-busy` relayed. Since agent 0.22.0 every exchange (`run`, `start`, `chat`, conducted or
bare) KEEPS its flow: each event its flow says -- the conduction whole, the voices, the steps, `response`
and `verdict`, the very objects `chat --json` says -- appended to `records/flows/<digest of the agent's
path>/<key>.jsonl`, one file per run; `./pp agent flow <path> <key> [--exchange <n>] [--json]` reads it
back, and `purge` removes it with the run. Since agent 0.23.0 `agent status <path> --json` says each run's
`weight {lines, files, bytes, flow}` -- what `purge` would count of it, without asking for one -- and the
last object and `agent list --json` their sum; since agent 0.24.1 that last object also says `packages`,
the packages the agent's instance pins beyond its base as its SETTINGS switch them -- what `ready` says at an
opening, before any run; `agent` declares the vector family `agent-run:<path>/<key>`
(verified by `pp-agent verify`) and `purge` asks the engine for its guardian before any removal, dry or not
(`run-held`); `team` declares itself that guardian (team 0.23.0): the run a member of a living team holds is
never purged -- `team reset` first. The agent calls pp for its values alone (`./pp <key> -`): a
bare call it types is refused `principal-advances`, a `-new` it types
mid-exchange opens nothing, one it types at the FINAL opens a STRAY run, said
and counted at the verdict. The answer, read by the adapter at every launch
(`conductor.adapters.answer`) -- a `--harness` command's by the adapter of the
GRAMMAR `--provider` names beside it, owed with every `--harness` (`grammar-missing`, agent 0.20.0;
`team start` refuses it too, team 0.21.1): `pp-agent` reads no
field of a harness's output itself (agent 0.13.0) --, owes its session identity — without it nothing
is kept — and is kept at the HOUSE's records: `messages.jsonl` (`{at, from, to,
run, message, policy}`, written at the launch, the policy as the face judged it,
`tag` and `pid` when a caller gave them), `responses.jsonl` (`{at, agent, run,
index, response, cost_usd, session_cost_usd, launches, denials, error,
harness_rc, flow}` -- a wake-up its run cap stopped between two launches says `error: "budget-spent"`
and `budget {cap, spent}` (agent 0.23.3); `cost_usd` the SUM of the launches' costs, each read in the
scope its adapter declares (`COST`: under `session` the difference between the cumul
reported and the cumul before it),
`session_cost_usd` the run's cumul in that session, `launches` the launches of the wake-up, `flow` (agent
0.18.0) what the flow of the exchange carried, summed by voice in tokens as the engine
estimates them -- `principal`, `conduction`, `pp_input`, `pp_result`, `tool_input`,
`tool_result`, `words`, `thinking` -- and its `calls` to the model, from which
`agent stats --json` approaches the run's context and pp's share of it (`context`, the
harness's own base left out; the window of the run's model as its adapter declares it,
`CONTEXT_WINDOWS`) and `agent status --json` says it reduced; a launch
always has its run), `sessions.jsonl` (`{at, agent, run, provider, session}`, a
run's last line holding its session). `./pp agent chat <path> [--run <key>]` (agent 0.5.0) holds a CONVERSATION at the
foreground: the messages read on stdin, one per line (a line ending on a backslash
goes on with the next), each ONE exchange -- the same `run` plays -- of one run held
from a message to the next with its session and its wake lock (`run-busy` for anyone
else meanwhile); the response on stdout and the verdict on stderr after each, an
exchange that ends badly said and the conversation going on; a SIGINT to `pp-agent`
during an exchange ends the harness and says `interrupted` -- kept in the mark of the run's wake
lock (`interrupted: true`), so that the run's next wake-up, in this conversation or another
process, opens its first prompt on `[interrupted by your principal]` before the message's head and
says `· after an interruption` at its verdict (agent 0.14.0) --, one while waiting or the
end of stdin closes the conversation, exit 0; `chat <path> --json` (agent 0.6.0) makes it a FLOW --
commands on stdin (`message`, `stop`, `quit`), events on stdout, one JSON object per line
naming its voice by its `kind` (`principal`, `conduction`, `agent`, `step`, `response`,
`verdict`, `waiting`, `refused`, `closed`), stderr silent; since agent 0.13.0 what a launch does
reaches the flow WHILE it plays -- each line the harness prints read by its adapter's `events` face
(`conductor.adapters.events`, engine `0.1.0-beta.63`) and said as `tool` (with `pp`, whether its
`shell` calls the agent's console), `tool-result`, `thinking` or `words`, always before the `agent`
event of its launch, never in the five records, never said by `run`; a line the adapter refuses is a `step`
`refusal` (`events-malformed`) and the launch goes on; since agent 0.8.0 a `set` command changes
the model, the budget or the effort of the next launches, said by a `policy` event (`provider` and
`permissions` stay as opened), `status --json` says each run's policy and the agent's `last`, and
`agent providers [--json]` says what each wired adapter spells and the model names verified with it
(`SPELLS`, `MODELS` of its `wire.py`). Since agent 0.9.0 the flow takes `conduct` -- `{"kind": "conduct",
"on": false}` makes the next exchanges BARE (one launch on the session, the prompt opening on the
line that says the principal has suspended conduction and the run resumes at their word -- agent
0.27.0 --, then the message, no call of pp, the records marked `conducted: false`, the run unmoved) and `on` brings the conduction
back -- and `package`, the engine's switch played on the run under the mark; `opened` says the
run's `packages`. Since agent 0.16.0 a `package` the run cannot take yet -- before the run is opened, or
while the package holds the run's view (`package-in-flight`, a run parked at its FINAL keeping the mounts of
its turn) -- WAITS in the conversation's list and is played again before every launch until the engine
takes it: the `package` event says `pending`, a `refused` one carries the engine's `detail`. Since agent 0.10.0 `opened` says the run's `cap {set, applied}` -- the agent's
`max_harness_tool_output` and the cap its outputs are cut under, the floor of a principal's cap
applied by the engine's `settings.served_cap`; the post (ui 0.11.0) says a raised cap on its remedy line. Since
agent 0.15.0 the flow opens on `ready`, once, before the first `waiting` and any message: the agent, `resumed`,
the provider, the policy, the packages, the cap and `conducted` as the conversation judged them -- its `run` the
key under `--run`, `null` at an opening -- so that a reader knows its run without sending anything. The kit's B4 (a tool call before every answer) is gone (kit 0.1.113): the LLM
that conducts its run reads that rule at `SYSTEM.CONDUCT` § Advancing. The verb `agent` is declared `tty: true`:
the console hands the skill its streams. `./pp agent start` plays the same exchange detached: the
child holds the wake lock and reports `{key, pid}` at once, its words go to
`session-<key>.wake.log` beside the lock; `./pp agent wait <name> <key>`
waits for the lock to be free and prints the response as `run` does
(`wake-dead` when the wake-up ended without one), `result` reads it at once;
`--on-end <command>` plays after the lock is released. `run` prints on stdout what it kept — the response's text,
a line opening on `::` behind a backslash so that no agent's words give pp an
order (`::push`, `::clear`, `::mount`), or with `--json` the response's record line plus `session` and
`state` — and its verdict line and refusals on stderr; every reading of a text an agent or a
message carried -- `agent responses`, `agent messages`, `team responses`, `team log` -- prints
such a line the same way (agent 0.3.3, team 0.13.5). Everything is judged before a launch --
the run, its session and provider, its material, the composed line --, and only then is the wake
lock's mark written: a refused resume leaves its run as it was, a refused opening takes its
reserved key back. When other runs of the agent play, the prompt opens on the neighbours line,
`[runs under way: <key> since HH:MM « <head> »]`, the local hour of each wake lock's mark and the
first line of its message. A conversation that resumes a run marks its wake lock at the take, before
any message -- the hour of the take, the head of the run's last message, `held: "chat"`, an
interruption kept, no count of responses (agent 0.18.1) --, so that its neighbours read it the same. While the harness plays,
`run` follows the run's trace with the engine's reader (`conductor.state.log`:
`tail`, `follow`, `step_of`, `said` — engine `0.1.0-beta.43`), read and never
written, and says each step on
stderr as it happens (`[HH:MM:SS] <key> · opened`, the stack of a block served,
`parked`, `answer`, `refused <code>`, …; one JSON object per line under
`--json`), and `no event for <n>s` after `--heartbeat` seconds without a step
(60 by default); `--quiet` says none of it. `list`, `status <name>`, `responses`, `messages` read
back ([packages/agent/README.md](packages/agent/README.md)).

A house that pins the `team` package has **teams**: a team is DECLARED by its
owner at `teams/<name>/TEAM.md` — a front matter naming the
MEMBERS (`agents: |`, one `<name> <path>` per line -- the member's name, then the
path of the agent under the house that plays it, one path playing several members
at will -- team 0.13.0), who
reports to whom (`reports: |`, edges `a b c -> d`), the `root` that receives
a task, the mandators allowed to post (`principals: |`; the owner, the house's
slug, is always admitted), the ceremonies to come (`ceremonies: |`, read for
their names, their participants and their `after` graph) and `work` (the repository
each opening clones); the body
is the team's intention, served by pp to the team's runs (team 0.17.0): the team's document
`teams/<name>/TEAM-<name>.md`, written by `team start` when the body is not empty or entries are
declared, names `TEAM.md` in its `serve:` row at the kit's `turn.begin` -- the engine serves the body
at a member's opening and again at the exchange after the owner edits it, under the same key, with no
start; it is never copied into a message nor into the journal, and `team status` says `TEAM.md changed
since the start` when the file differs from the start's `digest`. The team's state is its JOURNAL,
`.pp/.sys/records/teams/<name>/journal.jsonl` — one event per line, `{at, id,
kind, team, …}`, the id the previous one + 1, appended under the record's lock
by `pp-team` alone, never rewritten, read again at every reading (a last line
still being written is skipped, a torn line elsewhere refuses by its name).
`./pp team start <name> [--message "<text>" [--to <agent>]] [--budget <usd>]
[--budget-wakes <n>] [--member <agent> [--provider|--model|--effort|--permissions <v>]
[--package <name>=on|off]...]...` opens a SEASON of the team (team 0.31.0), the first or one
more on a team at work: it reads the declaration whole and refuses before anything is written
(`team-unknown`, `team-invalid`, `root-missing`, `participant-unknown`, `ceremony-cycle`,
`entry-missing` -- an entry neither in the team's directory nor in the instance of an agent
whose members play it --, `budget-invalid`, `package-invalid`, `package-required` -- a member
switching off `team` or a package it requires, read from the manifests --, `package-unpinned`,
`member-held` when `TEAM.md` drops a member holding an open task). The season's `--budget`/`--budget-wakes` stand above
`TEAM.md`'s until the next season (`team-started.season`, `TEAM.md` untouched); the flags after
a `--member`, up to the next, are that member's profile (`team-started.profiles`): they replace
the team's provider, model, effort or permissions for it, and each `--package` goes to its
`agent start`, in its run. A season keeps the members' runs, keys and sessions, the tasks, their
waits and failures, and counts afresh the cost, `budget-spent`, `budget-wakes` and each task's
`wakes:` -- a task a final failure left blocked is taken back by `resume`. It creates the agents the house lacks at
their paths -- each path once, under the house's birth lock for that path
(`state/born-<digest>.lock`, the one `agent add` takes: `born-busy` past
`call_lock_wait`) --, each borrowing the house's machine, no door, then writes `team-started`,
under `--message` the task `T<n>` and its `do` post from the owner to `--to` or the root -- without it
no task opens (team 0.38.0): the season stands on its ceremonies and the posts to come, the team `idle`,
and the calendar line is laid at the start only under an open task or a declared ceremony, the first
post laying it otherwise. `./pp team
post <name> [--message …] [--to <agent>] [--task <id>] [--reply <id>] [--stop]
[--as <principal>]` adds a new task, or a `note`, a `reply` or a `stop` on a
standing one (`task-closed` on a stopped or resolved task, `principal-unknown`
for a name neither the owner nor a mandator); `./pp team stop <name> [--task
<id>]` stops one task or every open one; `./pp team status [<name>]` reads —
the tasks, each agent's inbox, the last event, or one line per team declared.
`./pp team tick <name>` ADVANCES the team (team 0.2.0): one short process
under `tick.lock` beside the journal, taken without waiting -- held, the tick
posts the mark `tick.pending` and leaves; the holder clears it, plays, releases,
then reads it and plays again when it is set. It reaps the wake-ups that ended
(the launch found by its `wake-launched` event or by its tag at
`messages.jsonl`, the response by (run, index); a wake lock free without a
response is a dead wake-up: one retry, then `final`, and the tick answers in the
member's place every message of that wake-up that owes -- never a principal's
opening: the team's `notice` about the root goes to its principal), routes the elements an agent answered
-- since team 0.33.0 one JSON element or a list: `{"do": …}` along the `reports:`
edges (a `do` post per delegate, the `wait` of its `await`), `{"ask": …}` to any
member or a principal, `{"re": <id>, "text"}` the answer to the message `#<id>`
delivered to the member, to its author; `done`, `reply`, `escalate` are
`response-unreadable` --; each `do` and `ask` delivered to a member opens ONE
debt, settled by the first answer that cites it (a later one is posted `info`), and
the ROOT's answer to its task's opening writes `done` with its text, settles every
debt of the task, a `returned` for every post left undelivered on it and
`schedule-off`), judges the waits (`wait-met` when every delegate has answered its
`do`; every message but an answer to the round's `do`s and the task's opening passes
an open wait) and launches the next wake-ups by
the house's console -- `wake-intent` written FIRST, then `agent start --tag
--on-end "<engine> --instance <house> team tick <name>"` (`--run` to resume
the agent's run on that task, the flags `team start` was given -- `--harness`
and `--provider` together since team 0.14.1, the provider naming the grammar
`pp-agent` reads the command's output in), then
`wake-launched`. The message of a wake-up opens on the agent's inbox -- each message
its head line, `#163 DO from supervisor on T8 -- you owe an answer`, its text indented
under it --, the messages it still owes from earlier wake-ups, and the contract (the
three forms and the debt); the team's intention is served by pp, never in the message.
A journal written before team 0.33.0 reads as written: its `delegation` and `terminal`
events still count, a member's `done` or `escalate` to the member that delegated is read
as the answer to that member's last `do`. Since team 0.34.0 the tick breaks a DEADLOCK
before it wakes anyone: on the wait-for graph of the open tasks (a member waits for the
members whose answer it awaits, and for a principal whose reply to its question it awaits),
the greatest set of idle members -- no wake-up under way, nothing to receive -- whose every
wait stays inside is deadlocked (Chandy, Misra, Haas, 1983); a member at its bottom (waiting
for nobody, or in a knot) that owes is RELANCED -- a wake-up with no new message,
`relance: "owed" | "cycle"` on its intent --, and two relances on a debt still owed, the tick
answers it in the member's place (`re`, `by: tick`, `preempted`), never a principal's opening:
the team's `notice` about the root goes to its principal instead. Since team 0.35.0 the tick is a failure detector
(Eventually Perfect, Chandra and Toueg, 1996), read from the journal alone: a member whose final
failure stands -- on a task not stopped, its reason not `budget-share` -- is SUSPECTED for an
interval from the hour of that failure, the base of the team's calendar (`schedule:`, 5 minutes
without it or under `off`) doubled at each final failure in a row; during it nobody wakes the
member, and each tick answers in its place every debt it owes and every `do` or `ask` reaching it
(`re`, `by: tick`, `suspected: true`, « no answer: <member> is not answering at the moment; it is
tried again at HH:MM »), a principal's opening never -- the team tells that principal once per
opening, with the same words (a `notice` about the member). Past the interval its next message is its TRY (a member
owing a principal's opening alone is tried by a relance on it, `relance: "tried"`); a try that
fails is final at once and doubles the interval, a try that answers ends the suspicion and
tolerates the member one silent retry more (`retries:` + 1 per repentance). Nobody is excluded
for good; `team resume --task` ends the suspicion of the task's members, a season every
suspicion. While a member is suspected, every other wake-up's head says it after its first line,
`[not answering at the moment: <member> -- tried again at HH:MM]`. Since team 0.36.0 the tick
says nothing to a principal in a member's name: every post of the tick to a principal is a NOTICE
of the team (`{verb: notice, from: <team>}`) -- a guard reached, or `about` a root that failed for
good, was preempted on the principal's opening or is suspected; a notice opens no debt, and one
about the root holds its wait on the principal until the principal's answer cites it. The root
speaks to its principal by its own elements alone, `ask` and the `re` to the opening that closes
the task. `post --reply <id>` writes the principal's answer `re`. The faces speak the debt:
`status --json` says each member's `owes` and `health {suspected, falls, tried_at, repents}`, each
task's `dos [{id, from, to, answered}]`, its `waits` (`answered` of `of`) and the `relance` of a
wake-up under way, `waiting_on` `suspected` instead of `blocked`; `inbox` tells `questions` from
`notices` (`awaits` while one about a member holds it); `log` and `watch` say a journal written
before in the same words -- a member's `done`, `reply` or `escalate` as `re` (`was` its verb), an
`escalate` to a principal as the team's `notice` -- and never `delegation` nor `terminal`, which
the replay still reads.
`start`, `post` and `stop` tick right after their write (`--no-tick` spares
it); the end of every wake-up ticks by `--on-end`. The declaration may bound
the tick (team 0.3.0): `parallel` (the wake-ups under way at most; beyond it an
agent due is `deferred` and launched by a later tick), `budget` (the dollars
the team may spend since its start, the sum of the costs its wake-ups
reported; reached, nothing is launched, `budget-spent` is written once and the
owner gets the team's `notice`; each wake-up's share and `team budget` below) and `retries` (the wake-ups played again after
a dead one, 1 unless said); `team status` says the limits, the cost, each
agent's runs and their state, the delegates it waits for and the owner's
inbox. The wait is the agent's to shorten (team 0.4.0): an answer that
delegates may carry `"await": {"any": n}`, and the tick wakes it once n of
that answer's delegates have answered instead of all of them (`wait` at the
journal; any other form is `response-unreadable`). `./pp team stop <name>
[--task <id>] [--kill]` posts the `stop` to every agent holding the task --
its agent unless it answered the opening and each delegate that has not answered its last `do` -- and returns the posts left
undelivered on it; a wake-up under way is not interrupted: it ends, its answer
is reaped and routed nowhere, and no agent is woken for the stop (team 0.10.0: the stop is delivered at once);
`--kill` ends every wake-up under way on the task that has not answered, now -- the
launcher, the harness and what it runs, all at once (`wake-killed {tag, agent, task, run,
pid}`, nothing kept, nothing retried, the stop counted as delivered); a wake-up that has
answered -- read as the reap reads it, by (run, index), then without a run under the key
handed -- is spared and ended by the tick, its cost counted (team 0.13.2). A team is
FOLLOWED without being moved (team 0.5.0): `./pp team watch <name> [--task]
[--json] [--heartbeat <s>] [--for <s>] [--until-done]` writes on stderr every
journal event as it arrives and every step of every wake-up under way (the
agents' traces read by the engine's reader, never written), `no event for
<n>s` after the heartbeat, no lock, nothing written, never a tick; `./pp team
log <name> [--task] [--last <n>]` prints the journal one line per event, `./pp
team result <name> [<task>]` a resolved task's result as JSON (`task-open`,
`result-missing`). What waits for the owner reaches their own exchange: the
package mounts `TEAM_INBOX.md` at the kit's `turn.begin`, which plays `pp-team
inbox` and serves, under `INFORMATION — team-inbox`, one line per team where a
question (an agent's `ask`) or a notice of the team about a member awaits its answer, a task resolved,
a notice of a guard or a post returned since the owner last said `./pp team inbox <name> --seen`
(`inbox-seen` at the journal, the one event these readers write); no section
when nothing waits. The document says what that line renders and teaches no
call (team 0.13.4): the gestures it sends the agent to -- `inbox --seen`,
`post --reply`, `result` -- live in `pp-team`'s `SKILL.md`. What the others answered reaches a woken agent as ONE
line (team 0.6.0): the head of its message names each response other agents
gave since its last wake-up in the team -- its last `wake-intent`, the journal's
own cursor, nothing written -- by agent, task and journal id, with the house
console's absolute path and `team responses <name> --since <id>`; `./pp team
responses <name> [--since] [--agent] [--task] [--last]` prints those
responses with their texts read at `responses.jsonl`. The team lays its own
SCHEDULE (team 0.7.0): ONE line of the user's crontab per team -- a tick every
`schedule:` minutes of `TEAM.md` (5 unless said; `off`: none, ever;
`team-invalid` otherwise), the interpreter, the engine and the house by their
absolute paths, found again and removed by its mark `# pp-team <house> <name>`
-- the NET that catches a dead tick, a dead wake-up or a machine asleep. `team
start` lays it, a `post` that finds it gone with a task open lays it again,
the tick and `team stop` remove it when no task stays open and no ceremony is
declared; the journal gains no event: the calendar is the one truth of its own
line, and `status` reads it there (`schedule · every 5 min · laid | absent`,
`schedule · off`). The calendar is written by the skill on the owner's
commands and in the tick alone, never by the engine, and the table is read
and rewritten whole under the house's calendar lock (`state/crontab.lock`):
two verbs of two teams at once lose no line; a table that cannot be
written is said (`schedule not laid`, stderr, rc 0) and the team starts --
it advances by `--on-end`, without its net. Under `PP_CRONTAB=<file>` that
file stands for the table (the bench, a try); on Windows the skill writes
nothing, and the WSL and Task Scheduler ways are the README's. The tick RINGS the
ceremonies (team 0.8.0): the when is judged whole at `start` (`every
day|weekday|mon..sun HH:MM with a b -> c`, or `after <other> with a b -> c`;
`team-invalid` otherwise), and each ceremony whose period is due -- the day
conforms and the hour is past, by the house's local clock (`PP_NOW` stands for
it at the bench); under `after`, the followed ceremony's task resolved -- and
not yet rung (`ceremony-due` names the period: once per period, the journal
the judge) becomes ONE ceremony task from the team to its facilitator, its opening
`do` to the facilitator and a `do` per participant: the wait gathers the answers (the
opening waits with them), the facilitator concludes, its answer to the opening is the result. `entries:` of `TEAM.md`
(`<trigger> -> <document>`, the trigger `do` or a ceremony's name) names the
document a wake-up on that trigger plays -- a SUCCESSOR of the agent's procedure,
elected at EVERY exchange, opening or resume (team 0.13.3). Everything of a team
lives in ITS directory, `teams/<team>/`, and nothing in an agent's instance (team
0.15.0): every wake-up gets `agent start --documents teams/<team>`, the root of
documents of the run it opens; `team start` writes there `TURN.md` (below),
`TEAM-<team>.md` (attached at the kit's `turn.begin`, `next:` every entry of the
team then the neutral `TEAM-IDLE.md`, `decide: pp-team entry <team>`) and the
neutral, beside `TEAM.md` and the entries' documents the owner writes; `pp-team
entry <team>` -- `--run`, else `PP_RUN` -- prints the entry of the team's wake-up
under way on that run, the neutral otherwise, the house found as the machine the
skill lives in; what a version before 0.15.0 laid at an agent is removed by the
next start, a file that differs kept and said, and a team standing across that
upgrade is stopped then started again (its members' runs carry no root:
`documents-fixed`). The pilot, never the model, picks the procedure, and no
wake-up carries a door (`--door` and `PP_DOOR` stay for `agent run`). The GUARDS hold at the tick (team 0.9.0): a wake-up
whose wake lock is held past `timeout:` seconds after its launch (the journal's
UTC `at` against the real clock) is ended by the kill gesture and FAILS --
`wake-failed wake-timeout`, retried under `retries`, never `wake-killed`, which
stays the owner's `stop --kill`; `wakes:` bounds the wake-ups of one task
(retries included: `wakes-spent` once, the team's `notice` to the owner, the task left
open) and `budget-wakes:` the team's total (`budget-spent {unit: wakes}` once) --
the bound that holds when the provider reports no cost; `./pp team snapshot
<name>` writes ONE `snapshot {upto, state}` event under the journal's lock, the
replayed state packed as JSON (the resolved tasks' messages pruned, the posts
returned to the owner kept by their ids -- team 0.9.1), and every state reader
-- the tick, `status`, `responses`, `inbox` -- parses the journal from its last
snapshot line on and restarts there, while `log` and `watch` read
the whole history and never show it: nothing is rewritten, `status` renders the
same bytes before and after. An agent's ANSWER is a conducted production (team
0.10.0): the message asks the run conducted and the TURN as ONE JSON object;
`team start` writes the law in the team's directory, `teams/<team>/TURN.md` (the
law `TJ1`, the bytes of the skill's `agent-turn.md`), the overlay of the kit's
TURN in the team's runs alone -- a run of the agent the team did not open, a
`chat`, never reads it; the tick reads the last TURN draft of
the kit's delivery as strict JSON; an answer the house kept without a run fails
`run-unfound` under the retries, never routed; every wake-up that answered counts
in the team's cost, and `budget-wakes` counts from the last `team-started`.
A member holds ONE run (team 0.13.1): one key and one session of its harness for the
team's whole work -- the run that first answered, readable or not (a `response-unreadable`
keeps its run for the retry) --, every task of the member arriving in it by `--run`; it
plays ONE wake-up at a time, on the first due task in the tasks' order, the others waiting
for its next wake-up in the same run; its wait (its `await` and last delegation included)
stays by (member, task); the members play in parallel, `parallel:` bounding the team; the
sharing line counts from the RUN's last wake-up, the team's start for a new run; a house's
`upgrade` keeps the key -- the renewal mark at the slot's path, the next wake-up resumes
`--run <the same key>` and the engine reopens the run under it --, while a run whose slot
`-reset` took -- or that `team reset <name> [--member <m>]` forgot (team 0.16.0: the agent's
console plays `-reset <key>`, `run-reset {member, run}` is written; judged first under
`tick.lock`, `team-busy`, `member-running`) -- gives way to a NEW run whose message opens on
the history of every open task of the member; a `stop --kill` ends the wake-up of its task alone, the member keeping its
key for its other tasks; a `launch-missing` spends no retry, and `wakes:` and `budget-wakes:`
count the wake-ups launched; a kept run whose wake lock is still held is busy, never
resumed; `work:` gives a member's opening `agent start --work <repo>`, one clone per member,
kept with its run; `status` says each member's run, its state and its tasks.
`team resume <name> --task <id> [--message <text>] [--as <principal>] [--no-tick]` (team
0.18.0) takes back ONE task a guard left with nobody due -- stopped, held by a member's final
failure, or past `wakes:` --: judged under the journal's lock (`task-resolved`,
`budget-spent` -- judged first since team 0.22.0 --, `task-not-blocked`), it writes `resumed {task, by, from}` and a `note` to each
member it revives -- the holders at the stop, the members whose final failure stands, the
members with messages due past `wakes:` --; the replay opens the task again, counts its failures
and its `wakes:` from that event and drops the `terminal` a final failure wrote, while the team's
`budget` and `budget-wakes` are never reset by a resume and the posts returned at the stop stay returned;
the next tick wakes each member revived in its run, under its key.
`team pause <name> [--as <principal>]` (team 0.32.0) PAUSES the team: judged under the journal's
lock (`team-not-started`, `principal-unknown`, `team-paused`), it writes `paused {by}` and kills
nothing -- the wake-ups under way end on their own, and the tick reaps them and routes their
answers; until `team resume <name> [--as <principal>] [--no-tick]` writes `unpaused {by}`
(`team-not-paused` otherwise), the tick writes no `wake-intent` and no `ceremony-due`, the pause
judged under the journal's lock at each write. `post`, `stop`, `ring`, `budget`, `resume --task`,
`reset` and a season write as ever, the tick they play saying `paused: nobody woken until team
resume`; a season keeps the pause. The resume's tick does what is due at that moment: each member
due woken in its own run, a ceremony's period of the day rung when its hour is past and it never
rang -- a period that passed during the pause never rings. `status` says `paused since …`, its
face `state: paused` and `paused {by, at}`; the calendar line stays.
`team budget <name> [<usd>] [--wakes <n>] [--as <principal>] [--no-tick]` (team 0.22.0) RAISES the
team's `budget` or `budget-wakes` without a start: judged under the journal's lock
(`team-not-started`, `budget-invalid` -- at or below what the team spent since its start), it
writes `budget-raised {budget, wakes, by}`; the replay takes the new bounds and lifts
`budget-spent`, the members keep their runs, and the next tick wakes the members due in them. A
wake-up gets its SHARE of the money (team 0.22.0): `pp-agent` caps a RUN (agent 0.19.0) and a
member's run lives the team's whole work, so where the adapter of the launch's grammar declares a
cost scope (`COST`) the intent carries `allowance` -- its PART of the team's rest (team 0.29.0):
min((`budget` - the cost kept) / k, `budget` - the cost kept - the allowances of the wake-ups under
way), k the wake-ups that may play together, min(`parallel`, the members), so that k members due
together launch together -- reserved until the wake-up ends, and `agent start --max-budget-usd` is
the member's run cap: what the run spent plus the allowance; a member due whose rest is all reserved
is `deferred {reserved}`. No cap per wake-up exists: `team start --max-budget-usd` refuses
`flag-retired`, and a `launch.max_budget_usd` an older journal kept is never passed (`status` says it
once); without `budget:` no cap goes to `agent start`. A wake-up its run cap stopped between two
launches -- its response's `error` is `budget-spent` -- fails `budget-share {share, spent}`, read
before its body: retried in its run under `retries:` with a new share, its final notice saying the
share and the team's rest. `status` says `budget <spent>/<cap> USD · reserved <r> · left <l>`,
`status --json` `budget {cap, spent, reserved, left}`. A task may carry a NAME (team 0.24.0; free text since 0.24.1): `--name <text>`
at `team start` and at a `team post` opening a task -- one line of 1 to 80 printable characters a user
types, its edges trimmed (`name-invalid` otherwise) --, `name` on the `task` event,
said by `status` (`T2 Prix de la DDR4 · open`), `status --json`, `log --json` and `watch --json`; a ring names its
task `<ceremony> YYYY-MM-DD HH:MM` (its local hour) and says a CONSIGNE -- the facilitator gathers the
answers and concludes, each participant takes part as the team's intention says and answers the
facilitator --, never the ceremony's declaration line.
A team may be born from a TEMPLATE (team 0.25.0; nine since team 0.37.0): `team templates [--json]` lists them --
`supervisor-workers` (the root splits each task, one part per worker), `lead-reviewers` (the root does
the work, each reviewer checks its draft; one reviewer is the pair), `chain` (each member hands the next
step to the next one and passes the result back up), `solo`, `empty` (one member, the smallest
declaration), `council` (the root asks every expert the same question in one `do` and concludes at
`await {any: n - 1}`), `triage` (the root hands each task whole to ONE specialist), `cross-check` (the
root gives the same task to each twin and compares), `tree` (the root over `--squads <n>` squad leads,
two unless said, each over the workers given to it in turn; the daily of the squad leads) -- their text in `packages/team/templates/<t>.md`, their FORM in the script; `team new
<name> --template <t> [--member <name> <path>]... [--root <member>] [--principal <p>]... [--budget <usd>]
[--wakes <n>] [--timeout <s>] [--schedule <minutes>|off] [--no-ceremony] [--intention-file <path>]
[--squads <n>]` writes `teams/<name>/TEAM.md`: `--member` replaces the default members (`agents/<name>/<member>`) and
the form makes the root, the edges, the daily (two members or more reporting to the root) and the names
of the intention of them; the limits `budget: 5`, `wakes: 8`, `timeout: 900`, `schedule: off` unless
given. The text is judged by `start`'s own judge (`judged`, `declared` its reading of the file) before
any write, then linked in place only where no `TEAM.md` stands -- `team-exists`, `template-unknown`,
`team-invalid`, `participant-unknown`, `root-missing`, nothing left behind; `new` starts nothing.
`team declaration <name> [--json]` (team 0.26.0) READS a declaration: `TEAM.md` whole, the verdict of
`start`'s own judge -- `ok`, or the refusal `start` would write, said with rc 0 (the judge DECLINES,
`start` and `new` refuse with its words) -- and its gap to the last start, `{key, started, declared}` per
front-matter key `team-started` kept that the file now says otherwise; the body is never pending (pp
serves it at once); nothing written, no lock, no tick. Since team 0.32.2 its `--json` object says `declared`, the
front matter as that judge reads it -- the members and their paths in order, the root, the edges, the principals,
the limits of `TEAM.md` alone, the schedule, the ceremonies' lines --: what the next start writes, `null` under a
refused verdict. Since team 0.38.0 each member there says `born` -- an instance stands at its path -- and
`packages [{name, on}]`, the packages it plays: for an agent born, what its instance pins beyond its base as the
member's run plays them -- its SETTINGS and the switches of that run (team 0.39.0) --, read on the engine's faces as
`agent status --json` reads them; for one not born yet, what
its birth gives, the house's pins beyond its base, each on -- so that a post chooses a member's packages before
its first season.
`team ring <name> <ceremony> [--as <principal>] [--no-tick]` (team 0.19.0) rings a declared
ceremony at hand, out of its hour: the tick's own ring -- `ceremony-due {ceremony, period, by}`,
ONE task to the facilitator, its opening `do` to the facilitator and a `do` per participant -- under the period
`manual-<id>`, the id of its own `ceremony-due`, so that an `every` still rings its date at its
hour; `ceremony-unknown`, and `ceremony-open` while a task of the ceremony is open. A ceremony
line may end on `any <n>`, its QUORUM (n from 1 to its participants, `team-invalid` at `start`
otherwise): every ring of it writes `wait {facilitator, any: n, to: the participants}` after its
delegations, and the facilitator is woken at the n-th answer to its participants' `do`s.
`team status [<name>] --json` (team 0.20.0) is the face a program reads -- the post of `ui`
first --, the text's bytes unchanged: with a name ONE JSON object on one line -- the team, its
tasks (their text, their last event as `log --task` keeps them -- team 0.27.0 --, holders,
delegations, waits, their `cost` -- team 0.39.0), its members (run, state, the posts not delivered yet, the
other members' answers since its run's last wake-up, the `packages` their run plays, read as `agent status` reads
them -- team 0.39.0), its ceremonies (`next_due`, the local
`YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring; `due`, the next tick rings it; the last
ring and who answered it), the owner's box --, `{team, started: null, state: "never", waiting_on: []}` for a
team never started; without a name, one object per team declared. Since team 0.32.1 every object, a team never
started included, says `required` -- the packages a member may not switch off, `team` and what it requires, the list
`package-required` names. Since team 0.30.0 both say the team's `state`,
derived from the replay and never written -- `working` while a wake-up plays, `idle` when no task is open, else
`waiting`, with `waiting_on` listing every guard that holds in the order the tick judges them (`members`,
`wakes`, `budget`, then `owner`, `suspected`, `due`) --; the object says `season {n, at, budget, budget-wakes}` (the
starts, counted by the replay, and the season's own budget -- team 0.31.0), `launch` (what the next wake-up gets,
never `max_budget_usd`, with its `packages`; each member's the same, its profile applied) and each task's
`running` (the wake-ups under way on it); a team's line counts `asks` (the agents' questions), `notices` (the team's) and `done` (the tasks
resolved not seen) as `team inbox` does. `team log <name> --json` gives one object per
event, the object `watch --json` writes (`{at, team, event, id, …}`), so that a reader takes the
history there and the live flow at `watch`; `team responses <name> --json` one object per
response, its whole text or `null`; `team inbox [<name>] --json` one object per team where
something waits for the owner, the questions and the returned posts with their texts (team
0.21.0). The fields are named in the team README's "The faces".
The routes and the answers hold (team 0.12.1): a `do` goes to an agent that reports
to the answering one -- on a ceremony task its participants report to its
facilitator --, an `ask` to ANY member of the team or to a principal (team 0.16.0), a
`reply` only where an `ask` from its target to the answering member stands on the task;
a `do` off the edges, an `ask` to a name nobody declared and a `reply` that answers no
`ask` are `response-unreadable`, retried then final; a post to a principal -- the
owner, a mandator, the team -- is delivered at its writing and never `returned`; the
reap reads the answer first -- by (run, index), then the one kept without a run under
the key handed (`handed`) -- and the wake lock and `timeout:` after, so that two
wake-ups of one agent without their runs each fail with their own cost and a kept
answer is never killed; a new run opens on the
history of the member's open tasks, then its inbox, the intention served in its output. A task stops whatever holds it (team 0.12.2): every
stop writes `stopped {task, by}` before its posts, and a task nobody holds any more
stops without any post (`stopped -- nobody held it`), the team free to start again.
A team speaks NAMES and addresses its agents by PATHS (team 0.13.0): the journal --
whose `agent` field is the member's name --, the inbox, `status` (`r1 · agents/reviewer
· inbox 0`) and the head of every wake-up, `[team <name> · you are <member>]` -- after the lines
`agent start` sets at the head of a prompt, the material's and the neighbours' --, say the member; every birth, `agent start`, wake lock and record of the
house is addressed by the member's path, read at `team-started.agents` (`{member:
path}`) or at the intent's `path`; a line written before reads the same way, `m
manager` the member `m` played by the agent at `manager`
([packages/team/README.md](packages/team/README.md)).

### The marble, in layers

The marble compiles SECTION BY SECTION, ONE ARTIFACT PER CONDUCTION MODE
(engine `0.1.0-beta.56`) — `.sys/system.md` for a run the LLM conducts,
`.sys/system.common.md` for a run its principal conducts. Every section —
the engine, the base, each package — gives the marble at most TWO files of
its `system/`, and the build reads no other:

- `SYSTEM.COMMON.md` — what holds in both modes, compiled into both
  artifacts;
- `SYSTEM.CONDUCT.md` — what tells the agent to make pp advance when it
  conducts the run itself (the first call, the call each block names, the
  closings, the chunks, the compaction, the parenthesis, and the words only
  that mode uses), compiled into `system.md` alone.

A file absent, or without a body, adds nothing; the rest of `system/` is free
for another use. The sections compile in the order of the imports, each its
COMMON then its CONDUCT:

1. the engine — `engine/system/SYSTEM.COMMON.md` (its orders, written on the
   word *principal*, the one a run answers to, and naming no base), then
   `engine/system/SYSTEM.CONDUCT.md`, then the engine's card
   `engine/refs/PP.md`, last of the engine's section in both modes;
2. the base — its precision: who the principal is here (the kit's COMMON says
   *the operator*, in the chat, and the delivery of FINAL; its CONDUCT the
   conducted turn and the parenthesis);
3. every other package, in the requires topology.

Each artifact has its build receipt; `doctor` names both. Under
`SYSTEM_PROMPT.md` with `override: true`, each has its replace:
`system.replace.md` and `system.common.replace.md`. The boot serves the
run's own (`standing orders`), and so does the re-serve of `-compacted`; a
stale receipt of that artifact refuses the opening (`artifact-stale`).
Adapters and launchers pass `system.md` — a harness session is one the LLM
conducts. The card a harness RECEIVES (`.claude/skills/pp/SKILL.md`,
`.agents/skills/pp/SKILL.md`, gemini's `/pp`) is the card followed by the
engine's `SYSTEM.CONDUCT.md`: one composition, written by every adapter, compared by
`doctor` and by the boot's `card-drift` at the two skill homes (gemini's `/pp`
is written, never compared).

The base is the package `base:` names at `instance.yaml` (the kit when the
key is absent): the engine resolves it by that role alone — its sockets are
their own address, its settings keys are bare, its `BOOT.md` opens the run
and its `TURN.md` plays the turn. A base that carries no
`system/SYSTEM.COMMON.md` refuses at the build (`base-silent`): a marble that says *the principal*
without saying who is not served; one that lacks `procs/BOOT.md` or
`procs/TURN.md` refuses `base-incomplete`.

### What the build refuses

Every build (`-build`, install, `add`, `doctor`, `upgrade`, `remove`) judges
the composition WHOLE before writing anything: the manifests' contract (the
contributions, their sockets, verbs and skills), then the topology.

Every reference a package's document or manifest carries — a `CALL`, a
`SERVE` row, a `tools:` offer, an overlay, an `attach:`, a `sink:`, a
contribution's skill, an `output:` format, a `@SETTINGS` key — is resolved to
its owner and refused by name:

| Refusal | When |
|---|---|
| `dependency-undeclared` | the owner is a package the referrer does not require |
| `reference-unknown` | nothing carries the name |
| `socket-undeclared` | a package's proc HOOKs a socket its manifest does not declare |
| `name-unprefixed` | a public name wears nobody's package |
| `name-ambiguous` | two packages carry the same proc or ref as a base |

The names a package exposes — its console verbs, skills, settings keys,
vector families and payload tokens — wear its name (`<package>-<name>`,
`pp-<package>` for a skill, `<package>_<key>` for a key; the base package
alone stays bare); a name wearing another package's prefix joins that
package's thing and needs it required. Procs and refs stay bare and are ONE
base across the packages.

A socket is declared and HOOKed in the same short form, `<proc>.<hook>`, and
its ADDRESS carries the package that opens it — `<pkg>.<proc>.<hook>`, three
segments; the base's and your own are addressed by the two they write.

Your own documents are the top of the composition: they reference every pin,
offer what your harness carries, and a `serve:` token is judged on its owner
alone — a reading still to build or a file of your repository is the run's
matter, never the build's.

---

# The agent face — consuming the conduction

The agent's own contract is the card (`PP.md`), compiled into the standing
rules — what follows is the same mechanics in technical wording, one entry
per command: **name · description · effect**.

## The loop and the commands

The rhythm: the operator speaks → the agent calls the conductor → the returned
output frames the reply. `CONTINUE` calls back now; `FINAL` delivers then
waits for the operator; `END` stops the conduction.

The operator alone may suspend this rhythm. `pp off` opens a parenthesis in
which the agent calls nothing; the run and its key remain. `pp on` closes it:
the agent first calls `./pp <key> -peek` to recover the block that stands,
then makes the call the last closing owed. These are words in the
conversation, not console verbs or settings.

### `./pp -new [<message> …]`

*Description* — the first call of every conversation.

*Effect* — opens THIS conversation's run beside any other and hands its short
key; a key the tool no longer knows (`run-unknown`) is answered the same way.
The words after `-new` are the principal's MESSAGE — joined by a blank, the
grammar of `./pp <key> <message>` at the opening — traced `prompt` right after
`new`, before the first block. What a base serves of it is its own: the kit
serves none. Bare, the opening is exactly what it was.

The key is always DRAWN here: its slot is reserved exclusively before anything
is written, and a refused opening leaves no run behind. A launcher names no
key: `PP_NEW_KEY`, its adoption (`persistence.adopt`) and the refusals
`new-key-invalid` and `new-key-taken` are retired (engine `0.1.0-beta.57`) —
a launcher that wants the key plays `-new` itself and reads it on the first
output, as the run's principal does (see § The two conduction modes).

A LAUNCHER that makes the run advance itself says so at the opening:
`PP_CONDUCTED_BY_PRINCIPAL=true` makes `-new` open a run **conducted by its
principal** (engine `0.1.0-beta.54`). Absent, empty or `false`, the run is
conducted by the LLM — today's run, byte for byte; any other value refuses
`conducted-by-invalid` before anything is written. The mode is the RUN's:
`conducted_by: principal` in its slot and on its trace's `new` line (a run the
LLM conducts writes neither), kept by an upgrade's renewal mark and given back
at the reopening. Where a run its principal conducts stands MID-EXCHANGE (its
slot off the frontier: an agent is at work on it), a `-new` WITHOUT the mark
is that agent's: it opens nothing and answers one line, rc 0 — `pp: a run is
already open -- <key>, conducted by its principal; this call opens nothing:
end your message.`; a marked `-new`, or one while every such run is parked on
its FINAL, opens as always (engine `0.1.0-beta.57`). What the mode changes in
the blocks and in the keyed calls is said under *Channels and the delivery*,
§ The two conduction modes.

A LAUNCHER may also name the run's MATERIAL, the tree it works on:
`PP_WORKDIR=<path>` (relative to the workspace or absolute), read by `-new`
alone and kept at the slot as the material `work` — on the trace's `new`
line, through an upgrade's renewal mark. A serve row reads that tree by
`@work`; see § The language, *The material of a reading* (engine
`0.1.0-beta.58`). `pp-agent --work` already hands it.

A LAUNCHER may also give the run one more ROOT of documents:
`PP_DOCUMENTS=<absolute directory>`, read by `-new` alone and kept at the
slot — on the trace's `new` line, through an upgrade's renewal mark. For that
run alone, the directory is a space of documents between the instance's own
space and the packages': a name it carries resolves there (a `PP_DOOR`, a
`CALL`, an offer), a document there declares (`attach:`, `mount:`,
`provides:`), and a document there named as a package's document is that
document's overlay, while the instance's space keeps the last word. The root
is flat: its own `*.md` files, no subdirectory, a `_` file never read. The
console without a key, the build, `upgrade` and `doctor` compose without it,
and another run of the instance sees nothing of it: the instance's own
documents never name a document of a root (the build judges their `CALL`s
without one). A path that is not an absolute directory refuses
`documents-unknown` before anything is written; a keyed call that names
another root refuses `documents-fixed`, nothing played (engine
`0.1.0-beta.64`).

### `./pp <key>`

*Description* — the one advance gesture.

*Effect* — the next output: a step closed, a cut output's next chunk (served
before the flow moves; any other call bounces while a chunk waits), the resume
after a FINAL. Never carries the agent's own text. In a run its principal
conducts, the call is the principal's when it carries
`PP_CONDUCTED_BY_PRINCIPAL=true` and the agent's otherwise: the agent's bare
call refuses `principal-advances`; the principal's serves the output the
agent's last value left HELD, else advances (§ The two conduction modes).

### `./pp <key> <value>`

*Description* — an inline answer.

*Effect* — a PICK's choice (validated by membership) or a captured inline
production; anything pasted where nothing is owed bounces softly.

### `./pp <key> -`

*Description* — a production on stdin (heredoc).

*Effect* — captures a consumed production or a proof; a failing proof repairs.

### `./pp <key> -s <name> [args]`

*Description* — a skill by name, played BY pp.

*Effect* — the pending block shows first, then the skill plays: conducted,
executed, or served. A script's output over the host's cap comes in chunks
like a block's, on the bare call. Resolution: the pending block first, then
the one owning segment of the current output.

### `./pp <key> -s <name>@<n>`

*Description* — the same gesture, addressed.

*Effect* — settles an `address-ambiguous` refusal; owed only then. The next
rendered output retires the addresses (`address-stale`).

### `./pp <key> -peek [name]`

*Description* — a dry look.

*Effect* — the block a real call would render, without advancing; with a
name, whether that skill is offered there.

### `./pp -stats [<key>|<days>] [--blocks] [-json]`

*Description* — what the runs cost, read back from the traces.

*Effect* — keyless inspection: nothing opens, nothing advances.

The argument is read as a run's KEY first — six hex characters — so a key
made of digits alone (one in seventeen) names its run and not a span of
centuries; anything else made of digits is a number of days. A run keeps its
key once it is over: the trace says at its opening line which run it is, and
the key column fills for every trace written since.

One row per run over the last `<days>` (every trace when bare; one run by its
key):

- the exchanges, the blocks and the reshows a script call caused, the chunks
  of a cut output served on bare calls (counted with the exchange whose block
  was cut, even when that block closed it);
- the tokens — `tokens ≈`, an ESTIMATE: a function of the standard library
  calibrated against the o200k encoding, no dependency, no network;
- the mass served part by part: each `block` line of the trace carries its
  weight, each `answer` line the agent's own, summed apart on the period's
  line;
- the proofs piped, the VALUES the agent handed, the repairs, the refusals,
  the script calls, the laps of the iterated doors, the `exec:` played at the
  documents' entries;
- the durations of the exchanges (median, mean, p90 — an exchange over
  thirty minutes is a hole, said and left out).

A VALUE is what the agent hands the conduction: an `answer` line whose
`channel` goes to the tool (`tool`, `tool (heredoc)`), counted by its keyword
— a proof, a PICK, a NEXT, a field, an INFER or a WORK whose production a
step consumes. A bare close and a stray production (its channel `response`,
bounced softly) are none. Every `answer` line carries the
step's `channel` since `0.1.0-beta.53`; a line written before counts by its
keyword alone — PROVE, PICK, NEXT, FIELD — and the period says how many such
lines it read.

The period's line closes the table, and one more line follows: the averages
per CLOSED exchange — the conduction calls (blocks and chunks), the chunks,
the values with their keywords, the script calls (`per closed exchange: 15.7
conduction call(s) (7.0 chunk(s)), 1.0 value(s) (PROVE 1.0), 11.3 script
call(s)` on this product's own traces, 2026-09-29 → 2026-10-05). `-json` hands the same figures to a tool: per run its totals and,
under `detail`, its exchanges one by one; over the period `values` and
`per_exchange`.

**`--blocks`** reads what each OUTPUT carried instead. Beside its weight,
every `block` line of the trace writes a LEDGER, `served`: one entry per
matter the output took in, in the order it entered —

| Field | What it says |
|---|---|
| `subject` | as the section titles it |
| `state` | `served`; `spared` when the matter is already before the agent, with the mass that sparing avoided (a reading or a mounted body already proven by its content, a payload token a second document asks for in the same output, a provider's rendering identical to one the exchange already delivered); `forced` when a body is re-read on purpose; `reserved` after a compaction; `missing` when a row points at a gone document; `refused` when a provider exits non-zero |
| `origin` | `marble`, `body`, `serve` with the row's declared `nature`, `mount`, `payload` with the provider skill in `with`, `cycle`, `next`, `sink` |
| `by` · `package` | the document that asked, and its package — or, outside any package, the place: `instance` for the operator's own space, `machine` for `.sys/`, `repository` for the workspace around the instance; `engine` for the standing rules |
| `chars` · `tokens` | the mass |

The table renders one block after another, their lines in that order; `-json`
hands the ledger itself. What the block renders never moves for it: the
ledger is written at the site that serves, never guessed from a name, and
`payloads` — the measure, summed by subject — stands beside it unchanged.

### `./pp <key> -disable <package>` · `./pp <key> -enable <package>`

*Description* — the operator's word on what this run plays, placed by the
agent.

*Effect* — one package out of the play, or back in: nothing of it is served
or played and every package requiring it goes with it; the run does not move,
so the answer is the fact and the block that STANDS. Refuses `package-base`,
`package-unpinned`, `package-in-flight`; passes in front of a waiting chunk,
as `-peek` and `-compacted` do. The durable switch is the operator's own
(`package.<name>: on|off` at SETTINGS) — see [Switching a package
off](#switching-a-package-off). Who places it depends on who conducts the run (engine
`0.1.0-beta.61`): the verb and the principal's word on the packages are taught in
`engine/system/SYSTEM.CONDUCT.md`, served to a run the LLM conducts alone; in a run its
principal conducts, the house plays the verb itself under the principal's mark -- `agent chat
--json` takes `{"kind": "package", "name": …, "on": …}`.

### `./pp <key> -compacted`

*Description* — the agent DECLARES that its host summarized the conversation.

*Effect* — the run serves itself back in one output:

1. the standing rules — served inline only when `PP_MARBLE` is absent: with
   the marble channel wired they ride the host's own system prompt and
   survive;
2. the drift of a wired card;
3. the boot document's composed body;
4. every document still IN FORCE — the stack's frames and the standing
   mounts: each body, the `serve:` sections a frame's `SERVE`s had played (a
   mount's rows all), the rows their overlays add, and their payloads;
5. the pending block, every law on screen said verbatim.

What a POPPED frame served is past and is not re-served. Three run counters go
with the agent's context and are cleared: the readings proven served (each one
serves again at its site), the matter of a block cut mid-flight (the block
starts whole), and the codes-mode ledger (every law says its text again).
What HAPPENED stands: `turns`, the
latched signals, the mounts, the stack. The run's key rides the output as a
fresh run's first block does — it may have gone with the context too.

pp never DETECTS a compaction; the declaration is taken at face value, and the
duty it opens is one-shot but durable: it is written to the run's state and
consumed by the output that carries it, so a declaration whose answer never
reached the agent re-serves on the next call. Out of a run it refuses
`no-run`; keyless, it refuses `no-run` and names the keyed form.

### `./pp <key> -mount <address> [<address> …]` / `./pp <key> -mount '<json>'`

*Description* — documents of the composition, each named by its ADDRESS,
HOSTED into the current view.

**The address** names a document as a `CALL` does, in one of three forms,
resolved by one reader from the instance's own `vendor/` (engine
`0.1.0-beta.33`):

| Form | Example | What it names |
|---|---|---|
| a NAME | `BATCH.md`, `pp-plan` | the composition's base document of that name — a package's proc or ref, its overlays applying — or, failing a document, the contract of the skill of that name |
| a PATH | `plans/core/4-l-execution/PHASE.md` | the document at that place, the instance first, the repository last — the form for a document no name distinguishes (a node of a plan, a sidecar) |
| `<package>:<path>` | `doc:kinds/_generic.md` | a file of that package that a name does not reach (outside its `procs/`, `refs/` and `overlays/`), taken from the copy of the package the instance plays |

An absolute path, a `..`, a package not in play or an address no file answers
refuses `mount-missing`. The run keeps the ADDRESS, never a path of the
machine: a mount survives `doctor` and `upgrade`.

*Effect* — each mounted document's `constraints:` enter force at every block
and are owed at every checkpoint like any law on screen; its `tools:` join the
offer; its `serve:` lines are PLAYED at the gesture (capped at the serve
budget, a gone document skips with its note).

The laws and the offers are those of the document's COMPOSITION, as for a
frame: its own sections, then the deltas of its overlays (`+CODE`/`-CODE`,
`+name`/`-name`) — a delta that changes nothing refuses the mount by the
overlay's own codes. Overlays answer a file NAME, so they apply to the BASE of
that name alone — the file a bare name resolves to: a document mounted by its
path that only shares the name keeps its own sections.

**What to take from each** is the CALLER's explicit say:

- bare paths take the defaults — constraints and tools, no body;
- one JSON array picks per document — `[{"doc": <path>, "body":
  true|false|[<selection>, …], "constraints": …, "tools": …}, …]`.

`body: true` serves the document's body with the gesture's output — through
the one reader, under `proc_body_serve` like a CALLed body: once proven, a
body mounted again renders nothing until its document changes, and a nested
entry keeps its heading, tools and laws without it.

`body` may instead be a list of selections, to serve parts of the body and
leave the rest out: `"body": ["## Target..## Items", "## Decisions.."]`. A
selection is written as the inside of a serve token's brackets (see `SERVE
[doc]`): two tags around `..`, either side open, or line ranges as a last
resort. Each selection is a reading of its own, in the list's order: titled
`<document's title>[<selection>]`, proven by the hash of the selected lines,
rendering nothing once proven, served again after `-compacted`. A selection
reads the file as plain lines: the body an overlay appends is not part of it
— mount a document that has overlays with `body: true`. A start tag found on
no line serves nothing of that selection, a line in the block says so, and
the engine pushes `serve-stale`; an empty list, an element that is no text or
a badly written selection refuses `mount-invalid`, nothing mounted.

Each entry also picks its `scope` — the fusion's own vocabulary:

- `stacked` (the default) rides the pending frame as one more instruction of
  the current stretch: its laws join the pending CONSTRAINTS verbatim, its
  body an INFORMATION payload -- a contributor that declares `payloads:`
  (`TEAM_INBOX`, `RECALL`, `LEDGER`, `NEXT_MOVE`) serves its body WITH the
  section its tokens render, before it, and not at all when nothing rendered
  (plan fixes1): a brief without its matter instructs nothing;
- `nested` stacks a scope of its own, as a CALL: a numbered heading, its
  tools, its body when asked for, its laws verbatim at home then held as codes
  by the pending block, the segment addressable (`@n`) like any fused
  output's.

A `proc:` aboard is ignored — the flow stays the frames' (the build warns on
`plans/` documents carrying one). A mount lives ONE exchange: the rewind that
opens the next one sweeps every mount. Refusals: `mount-missing` (see the
address), `mount-collision` (a constraint code already in force),
`mount-invalid`. A standing mount whose document disappears mid-run — a file
removed, a package switched out from under it — mounts nothing from then on and
says so: the engine's own `mount-gone` (a diagnostic of level note, `mount-gone
· note · <address> -- gone`), once per address and per run, never from a view.

A SCRIPT played by `-s` can mount too: a `::mount <json>` line on its output
(the `::push` channel) is harvested on a clean run — the script derives the
chain, pp hosts it, one gesture.

**The host mounts too.** A document that HOOKs a socket can name what mounts
there itself, in its front matter or in an overlay of it:

```
---
name: TURN
mounts:
  turn.begin: HOUSE.md
---
```

The names follow the socket's own contributors (`mount: <socket>`), each judged
by its own `when:`, and enter exactly as they do: laws in force and owed at the
checkpoint, offers, body (spared once proven under `proc_body_serve: once`),
readings, remounted at every turn and served again after `-compacted`. A name
resolves as a CALL does, so an agent mounts a proc of its house -- the house's
`procs/HOUSE.md`, its laws, offers and readings shared by every agent that writes
the line, and by none that does not. The build refuses a socket the document's
proc never hooks (`mounts-hook-unknown`) and a name found nowhere
(`reference-unknown`).

Where to mount: `turn.begin` enters before the WORK -- the laws bind while the
work is done, the readings give its ground; `turn.end` enters after it -- for a
reading of the state the work left, and the laws that bind the closing. A law of
production is proven over the whole turn, so it belongs at `turn.begin`; a
reading at `turn.end` computed by a script needs a `§` before the socket, or the
fused output computes it before the work.

### `./pp` (keyless)

*Description* — inspection only.

*Effect* — where the single standing run is; never advances, never opens.

## The block, section by section

| Section | What it carries |
|---|---|
| the output's heading — `pp · run <key>` | the run's key and the clock: the local hour `HH:MM:SS` and `+H:MM:SS` elapsed since the run's `-new`, once per output — and with every chunk of a cut one, so no piece arrives without saying which run it comes from. A second line follows it where the instance pins packages beyond its base: what the run plays, one cell each (`on`, `off`, `off (<- <dependency>)`), dependencies first |
| the heading — the path | which documents are in flight: ancestors bare, the ACTIVE frame carrying `{i/m}` (a range `{i-j/m}` when the output fused steps i→j), `· REPAIR n` when the last move missed, `[n]` numbering multi-scope outputs |
| `TOOLS` | the skills this scope offers, by name — their contracts live in the served catalog |
| `INFORMATION — <token>` | a document read and injected by the tool, titled by the token its row wrote — path and selection as written (`design/target.md`, `PHASE.md[## Target..## Arbitrations]`, `GLOSSARY.md[1-2]`), followed by ` @<name>` when it was read from a material other than the repository (§ The material of a reading); a CALLed body by its document's name; the pending step's own body is promoted `NEXT INSTRUCTION CONTEXT`; a cut reading continues untitled |
| `CONSTRAINTS` | the laws in force — full text once per output, codes after; a new scope says its delta verbatim |
| `DEVIATION` | when the last move missed: the miss, named |
| `DIAGNOSTIC` | what the engine itself found wrong with the conduction — one line per diagnostic, `<signal> · <level> · <fact> -- <way out>`; see [The bus and the diagnostics](#the-bus-and-the-diagnostics) |
| `OPTIONS` | the closed set a `PICK` chooses from |
| `NEXT INSTRUCTION CONTEXT — the ask` | under the WORK of the frame that opens an exchange, at every exchange: the principal's last message is the context of that step — say the productions above, then play the call; the message itself is never copied there (plan fixes2, batch la-forme-du-tour) |
| `INSTRUCTION` | the instruction lines — one step each, suffixed `form => channel  (DOCUMENT)`, the name of the step's document last; same-frame steps with nothing between them collapse under ONE title; a step without `output:` yields `any` |
| the closing | `CONTINUE` / `FINAL` (the arrow mark, once, right above the exact command) or the `END` section |

## Channels and the delivery

The channel is **derived, never declared**:

- a consumed production travels by its format's mode — `tool` inline, `tool
  (heredoc)` on stdin;
- a PICK rides the command;
- a proof checkpoint pipes its proof;
- an unconsumed production is said to the principal at its own step, `=>
  response`, whatever stands ahead — the FINAL is the frontier alone and
  delivers nothing (engine `0.1.0-beta.67`, batch `la-production-au-message`:
  the drawer of drafts, `ephemeral`, is gone).

`response` is what the principal receives: the engine names the channel, the
base says where it lands — under the kit, the operator's chat. The word lives
at one place of the engine (`language.RESPONSE`, engine `0.1.0-beta.31`),
read by the derived channel and the soft catch.

### The header of a response

The kit's standing orders say how a response is said: it opens on three lines
— `---`, the name of the document on the INSTRUCTION line, `---` — and is
said now, in the agent's message, before the next call; after a `CONTINUE`
that owes no production, nothing is said. The engine renders no header
itself: the heading of the block carries the name, the text is the agent's.
In the relayed channel (a run its principal conducts) each production is thus
ONE message of the launch that produced it, never repeated at the FINAL; the
readers of the response (the house, the teams, the post) still keep the LAST
text of the final launch until their own batches read the words of every step.

### The two conduction modes

A run is conducted by the LLM — it calls pp to advance, today's mode — or by
its PRINCIPAL, whose launcher opens it under `PP_CONDUCTED_BY_PRINCIPAL=true`
(see `./pp -new`), serves each output in the prompt and makes pp advance. The
engine knows no turn; it knows the mode, and in the principal's mode:

- a closing that moves the run on carries **no command and no note** (plan
  fixes1): CONTINUE renders bare, FINAL bare with its look-ahead alone --
  `(no law of production in force: no proof owed)`, `(the turn closes on its
  proof)`, `(proof given)` after a judged checkpoint -- and an unconsumed FREE
  step closes the same way; the order of a block (the `=> response`
  productions written, then the call) is the standing orders' (`SYSTEM.CONDUCT`
  § Mandatory pp use), never redone under a block; a closing that asks the
  tool for a VALUE — a proof, a field, a choice, a production a consumer takes
  — keeps its command;
- **the last `=> response` step of an output stays PENDING** (engine `0.1.0-beta.70`,
  plan fixes2, batch la-conduction-hybride, operator word 2026-10-17): a production
  said to the chat is the agent's message, and its term is the principal's call. So
  the last FREE step an output batched -- the one nothing follows in that output: a
  `§`, the fusion cap, a HOOK that would inject a step behind it, a checkpoint of
  another segment, the frontier with no proof owed -- is handed back to PENDING
  (`asked`, not done; traced `pending`) and the output closes on it with a bare
  CONTINUE, the steps batched before it staying batched (the boot's CAPABILITIES
  table under the TURN's WORK). A checkpoint owed right behind it, with nothing to
  inject before, keeps it batched: the proof is asked in the same output, one launch,
  as the LLM's mode asks it. Whatever the agent plays during its
  message -- a mount, a gesture, a door, a view -- acts on THAT step: `-peek` renders
  `TURN{2/4}`, a `-s` stacks on it. The principal's bare call resolves the step
  (`submit("")`, as a bare call resolves an asked WORK in the LLM's mode) and goes on
  in the same call, through the `§` the next document opens on (THREADS): one output,
  no order block of its own. A FREE step right before the frontier is never fused with
  the FINAL in this mode: the FINAL comes at the principal's next call, launched on
  nothing. In the LLM's mode the step is batched as before
  (`tests/engine/execution/principal-hold.py`, case n);
- **`conduction: hybrid`** (SETTINGS, `strict` by default; engine `0.1.0-beta.70`,
  plan fixes2, batch la-conduction-hybride): the output whose closing asks the
  agent such a VALUE is not held -- it comes back in the agent's tool result, its
  command with it, cut under the HOST's cap (`max_harness_tool_output`, never the
  principal's floor: it lands in a tool result), the rest served by the agent's
  bare keyed call chunk by chunk (the `viewing` slot a view uses, the readings it
  staged proven when the last chunk leaves); the trace says `inline` with the act
  that rendered it and `-stats` counts them (`N inline` on the period's line,
  `inline` in the json). An output that MOVES the run on -- a bare CONTINUE, a
  FINAL, a FREE step said to the chat -- is held as under `strict`, and a door
  opened by `-s` has no case of its own: its first block follows the rule. The
  invariant holds in both values: the agent's bare call never advances the run.
  Measured on the bench's laps witness (three laps, a proof each): 2 launches of
  the harness under `hybrid` where `strict` takes 6
  (`tests/engine/execution/principal-mode.py`, `packages/agent/tests/engine/agent-exchange-record.py`);
- an output over the cap comes in chunks, under a FLOOR of the cap: the larger
  of `max_harness_tool_output` and 200 000 (`settings.PRINCIPAL_CAP`, the one rule
  `settings.served_cap`; beta.62). The output reaches the harness on its standard
  input, never as a tool output, and one output is one launch -- an instance cut
  for its host (VSCode at 20 000) serves its principal's runs whole up to the
  floor, and no setting lowers it; a higher setting holds. A prompt has its limit
  too: an output past that cap comes in chunks under it. Only the
  closing of a chunk before the last changes — no command, `(a reading continues:
  <n> characters in <m> more chunk(s) -- they come at your next prompt: end your
  message now, and act only once the last has come)`; the next bare call serves
  the rest, as today;
- the texts that would send the agent back to pp speak of its message: the
  two soft catches (`end your message`), a cut view (`this view is cut under
  the host's cap`), a renewed run (`its principal's next call reopens it`), a
  call bounced while a reading continues (`comes at your next prompt`);
- `-hook` serves the pending block in both modes (every block but an END).

The card says it in one sentence under *Closings*. What tells the agent to call
pp lives in the `SYSTEM.CONDUCT.md` of each section, compiled into the
standing orders of a run the LLM conducts alone: a run its principal conducts
is served `system.common.md`, which carries none of it (see § The marble,
in layers).

**Whose call it is** (engine `0.1.0-beta.65`). In such a run the launcher
carries the same mark, `PP_CONDUCTED_BY_PRINCIPAL=true`, on EACH of its own
keyed calls — never in the environment of the CLI it launches: a marked call
is the principal's, any other the agent's, and a CLI that filters its shell's
environment cannot make the agent pass for the principal. The console alone
reads the mark, and only in a run its principal conducts (`context.by_principal`),
and hands the answer to the facade; an odd value refuses `conducted-by-invalid`.
The dynamics are those of every run — a value or an act handed by a tool call,
one judge, a repair —; only the delivery of what the engine serves changes
channel.

**Two texts leave a call.** What the engine SERVES is everything it renders of
a block: the step after a value, a REPAIR, the view of a mount (`-mount`, a
script's `::mount`, the manual of a script called bare), a routed door or a
bare contract, the re-serve of `-compacted`, the block after a switch
(`-disable`, `-enable`), a `-peek`, the block an offer out of the step brings
back. What a call ANSWERS is what a script prints of its act, a bounce line,
a refusal — and, since engine `0.1.0-beta.68` (batch `le-peek-en-sortie`),
what only SHOWS: a `-peek`, the manual of a script called bare, the block an
offer out of the step brings back, the block after a switch — none of them
moves what the principal relays. The served text goes to whoever conducts the
run — the tool return in the LLM's mode, the next prompt in the principal's;
the answer goes to the caller in both modes. ONE seam decides, never the call
site:
`Conductor.delivered(block, by_principal, lead, act, view)` is the one way a
block leaves the engine on a keyed call, and no line of the console prints a
block itself.

- **the agent's call that serves** plays its act at once, exactly as in the
  LLM's mode — a value judged by `submit` (traced `answer`, checked, repaired
  in place or by reopening, given), a mount written, a door pushed —; the
  block it renders is HELD at the run (`held` in the slot: the same pieces a
  cut keeps, and the `act` that held it; traced `held` with that `act`) and
  the tool return carries what the act answers — a script's own text — and
  one line naming the act and nothing more: `pp: value judged`, `pp: mounted`,
  `pp: opened`, `pp: re-served`, `pp: reopened` — where the output comes is the
  standing orders' to say, once (plan fixes2, batch la-forme-du-tour); a second hold in the SAME
  call — a script's second `::mount` — joins the first;
- **the agent's call that only SHOWS** is answered at once, in both modes:
  `-peek`, the manual of a script called bare (its mount written, proven, in
  the ledger, as ever — its block alone comes back instead of waiting), an
  offer not at this step (exit 2 kept, the DEVIATION in the tool return), a
  switch (its fact and the block). The text is cut under the HOST's cap — the
  instance's `max_harness_tool_output`, never the principal's floor: it lands
  in a tool result, not on the harness's stdin — and the rest waits at the slot
  (`viewing`) for the agent's bare keyed call alone, chunk by chunk, the
  closing of each chunk saying so; any other act of either caller forgets it.
  Nothing is held, nothing traced: a view writes no state of the run;
- **the agent's bare call** serves the rest of a view when one waits; with
  none it refuses `principal-advances` (« this run advances at its
  principal's call -- end your message »): nothing played, a chunk of the
  principal's waiting included;
- **one output is held at a time**: any call of the agent while one is held —
  a value, a `-s`, a `-mount`, a `-compacted`, a `-peek`, a switch — bounces:
  `pp: an answer is held for your principal's call -- end your message`, rc
  0, nothing played, the slot byte-identical — the agent has not read the
  block it would act upon;
- **the principal's bare call** serves the held output when one stands — cut
  under the cap as if it left then, the rest served by its next bare calls —
  and the slot forgets it; with no held output it advances as today (a value
  due and absent: the empty-answer repair); at the frontier it carries the
  principal's message; each is traced `advance` (`held: true|false`, `prompt`);
- **a marked call carrying a text over a held output** refuses `output-held`
  (« an answer waits its principal's bare call -- it is served first »);
- `-stats` counts the held outputs and the principal's advances per closed
  exchange and says them on the period's line where any happened (`N held, N
  principal advance(s)`); `-json` carries `held`, `held_by` (the held outputs
  by act) and `advances`.

A script that wants to SERVE a reading goes through `::mount`: what it prints
itself is its answer. The agent reads none of the mark: no text it is served
names it; the card says that what pp serves on its call and moves the run
comes at its next prompt, that what only shows comes back in the tool result,
and the neutral line and the refusals tell it to end its message.

### Consumption

Consumption means **use**, not transport. Three consumers exist: a callee
declaring `input:` (the pipeline), a PICK (the election), and **the engine
itself** — the proof judge consumes a checkpoint's proof, a document's
declared `sink:` consumes its projection. Engine-consumed productions derive
`=> tool` through the same consumption rule; no document ever declares a
channel.

**Capture ≠ channel.** The keyed call is one wire carrying two directions:
inbound, the operator's message rides the resume at the frontier — and the
opening, `-new <message>` — traced `prompt` whatever the tuning; outbound, the
agent's production returns only when consumed. Position in the flow — the
frontier — is what tells the two apart: mid-flow text is a production for the
pending step (a stray one bounces softly, nothing recorded), frontier text is
the operator's word. `capture_prompt` is the KIT's key, not the engine's: it
only decides whether the FINAL closing asks for the message itself
(`./pp <key> <the principal's next message>`) or closes bare — the engine
reads it by name, as it reads any key a base declares, and a base that
declares none gets the bare closing.

## The bus and the diagnostics

The engine keeps ONE bus of operational signals, and says the ones that
matter itself.

### The bus

A signal is PUSHED where its fact happens:

- by the engine for its own — `card-drift` (a projected card differs from the
  contract), `refused` (a call the engine refused by name), `repaired` (a
  document replayed after a miss), `serve-stale`, `serve-shadowed`,
  `material-unknown` and `material-missing` (a
  reading whose tag or path moved), `mount-gone` (a standing mount whose
  document no longer answers its address);
- by a package for the ones its manifest declares under `contributes:
  events:` — `signals`, their `sector` and `priority`; `vectors`, the families
  a signal may point at; `sectors`, its own NEXT real estate with an `icon`
  and a `cap`.

It is LATCHED at the run as one entry, `{signal, source, vector, door,
sector, n}`: the source is the declarant, the door the way out when the
signal has one, the count grows while the fact stands.

The `protocol` sector is the commons every declarant may name; a named sector
belongs to the package that declares it — a colliding declaration refuses the
registry read, a signal claiming a sector its provider does not declare
refuses unowned. What a package DOES with the bus — a counter, a threshold, a
sink shaping what the agent formulates — is that package's mechanism,
described in its own README; the engine only carries.

### A diagnostic is a signal with a level

A signal may declare `level: critical | warning | note` — the engine's own
do; a package's under `contributes.events.signals`; any other word refuses
`level-invalid` at every read of the registry, the build's included.

With a level, the engine RENDERS the signal itself, in the block where it
happens or the next one, under a `▌ DIAGNOSTIC` section — one line per
diagnostic:

```
<signal> · <level> · <fact> -- <way out>
```

- the fact is the push's evidence, the way out the signal's door;
- the line is said ONCE per run and per fact (a second `repaired` on another
  document is a new fact), whether or not any package reads the bus — a
  kit-only instance sees its drifted card at boot;
- the section sits between `DEVIATION` and `OPTIONS`, near the instruction; a
  view (`-peek`) forms none;
- it is WEIGHED at the trace as the `diagnostic` part of the block's line and
  counted by `-stats`.

The levels posed today:

| Signal | Level |
|---|---|
| `card-drift` · `repaired` | warning |
| `refused` · `serve-stale` · `serve-shadowed` · `mount-gone` · `material-unknown` · `material-missing` | note |

No `critical` yet — reserved for what keeps a run from holding its word. The
standing orders say what the agent does with one: say it to the principal
with its level, a `critical` before any work.

### The operator's hand

`./pp acquit <vector>` retires a treated signal vector: its counter and its
latch fall together, and the bus stops asking. A package whose reflex reads
the bus (a sink, a `NEXT` overlay) leaves with `package.<name>: off` or
`-disable`; the diagnostics stay: they are the engine's.

## When an answer misses

Back to the README's `REVIEW`: the verdict came back as a line — and `REVIEW`
carries laws of production, so the engine appends the exit checkpoint:
`INFER proof => tool (heredoc)`, no brief — the catalog's `proof` format
defines the shape. The agent proves its production against each constraint
in force — and hands down a proof whose `C1` cannot pass, because the
production rewrote the draft:

> `./pp <key> -` … `{"code": "C1", "evidence": "I rewrote section 2 to show the fix", "verdict": "fail"}` …

The conductor does not argue. The document reopens from its first step — the
injected checkpoint purged with the reopening, its repair counted on the
frame — and the block comes back, one field heavier:

```
▌ pp · REVIEW{2/2} · REPAIR 1

▌ INFORMATION — draft.md
# Q3 report — draft

The introduction restates the abstract almost verbatim. Section 2 presents the
results before the method, and its lead paragraph buries the headline number.

▌ CONSTRAINTS
C1  you judge the draft; you never rewrite it.
C2  a finding without the line it comes from is no finding.

▌ DEVIATION
your own proof failed -- C1: I rewrote section 2 to show the fix

▌ INSTRUCTION
INFER line => response

▶ CONTINUE
./pp <key>
```

The whole document replayed: the draft re-served to the very eye that
misjudged it, the miss **named with the proof's own words**, the same answer
re-asked in the same form. The rewrite has nowhere to land, and `C1` cannot
have faded — it never left the screen.

### What counts as a miss

- an answer outside `OPTIONS`;
- a list handed to a `PICK` that is not an array of scalars;
- an empty production the next step consumes;
- a `json` that does not parse;
- a proof that leaves a code the line asks unnamed;
- a proof with a failing verdict that declares no gap (no `blocked`).

Only a move the tool **watched** counts: a status call is where the run
stands, held against no one. The repair counts survive the reopening; at the
bound (`work_repairs_allowed`), the conductor stops repairing and hands the
operator back. What counts against the bound is a replay or a miss: a bare
`fail`, a code failing again at its mini-proof, an empty answer, a mini-proof
that names other codes than the repaired ones. A fix whose mini-proof holds
counts nothing, and a declared gap (`blocked`, see "The checkpoint") is no
miss at all: the checkpoint closes on it. A tool invoked outside the block's scope is **caught**
instead: the pending block answers, the ask named as not played — no repair
counted, the floor resumes on screen.

A **deviation** is the agent's move missing — the document replays. A
**refusal** is the document or the environment being wrong — exit 2, a named
reason, nothing played.
