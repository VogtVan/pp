# Procedural Prompting — the reference

The mechanics behind the [README](README.md): the block, the language, your own
procedures, what happens when an answer misses, and the instance on disk.

A language model is excellent at judgment and poor at bookkeeping. Ask one to follow a
long procedure and you have handed it two jobs at once: the work, and the management of
the work — the current position, the rules in force, what was already read, what comes
next. It performs the second job from memory, and memory is exactly where a model
degrades: instructions stated once fade as the context grows, scope creeps because
nothing structural resists it, and a reading is *claimed* rather than proven.

This reference documents BOTH faces of the product — the **user face** (what an
operator builds and tunes: procedures, settings, packages) and the **agent face**
(what a conducted model consumes: blocks, commands, channels, repairs). Its
overlap with the agent's own card and with the author's catalog `PP_CHEATSHEET` is
deliberate: same mechanics, technical wording — this document is never the
source of an agent reflex.

Procedural Prompting externalizes the bookkeeping. A small deterministic **conductor**
plays the procedure and hands the model **one output at a time**. The model's freedom is
untouched *inside* the step — judgment, wording, reasoning stay its own. The **limits**
around the step are not its concern anymore: it does not track them, so it cannot lose
them. And the limits are **yours to write**: what you put in a procedure is what every
block will enforce — the specification holds because it never leaves the screen.

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
14. [The improvement sink](#the-improvement-sink)
15. [The upkeep pass — on the operator's word](#the-upkeep-pass--on-the-operators-word)
16. [When an answer misses](#when-an-answer-misses)

---

# The user face — building and tuning

## The language, keyword by keyword

The front matter is **YAML** (`yaml.safe_load`) — one flat mapping: values
keep their YAML types (`true` is a bool), a key left bare declares nothing,
`#` comments vanish; inside a block scalar (`constraints: |`), a `# `-prefixed
line is a comment of pp's own — uncommenting it arms the line.

A **procedure** is the `proc:` key of that front matter — one keyword,
optionally followed by an argument, per line. Every entry below follows one
format: **name · declares · effect · example**.

**`PICK <name>`**
*Declares* — a closed choice: the model elects ONE id.
*Effect* — the block renders `OPTIONS` (fed by the upstream production — the
pipeline is the options source) and validates by membership; anything else
repairs. The list the upstream hands it is judged at its CAPTURE, on the form a
`field` has — a JSON array of scalars (strings or numbers), none empty, each
once, 200 at most: a list of objects, an empty array or a bare scalar is a miss
that repairs, the element named under `DEVIATION`, and a number renders as its
text (`[1, 2]` offers `1` and `2`). A list no capture judged — a callee's seed
under `input:` — refuses `options-invalid`, the element named; a `PICK` with no
producer before it refuses `options-empty`. The answer rides the command,
verbatim.
*Example* —

    proc: |
      PICK verdict

**`SERVE [doc]`**
*Declares* — a reading the TOOL performs; the model has nothing to prove.
*Effect* — one bare `SERVE` dequeues one whole SECTION of `serve:` — a
paragraph of the block (a blank line separates sections), every line and
document of it; n sections take n bare SERVEs, in order. The text is injected
(`INFORMATION`); an output over the host's cap comes in chunks, an intermediate chunk
saying what remains and that the bare call alone serves it (any other call bounces,
`chunk-pending`), and each document is proven ONCE per run by its content, when its last
chunk has left — named again (another section,
a `SERVE <doc>`, a mount, a CALL) it renders nothing, never the text. The section
declares, the SERVE plays: a section without its SERVE is never read; a SERVE
past the last section refuses (`serve-exhausted`). A token is addressed as the engine resolves it: a bare
NAME through the member's search paths — the instance's own space, `procs/`,
then the packages (a ref by its bare name), then the root of the member's repo
(`README.md`; the instance and the packages keep the upper hand on a same
name); a PATH — a token carrying a `/` (`design/target.md`, `engine/pp.py`) —
is the repository's when the repository holds it, the instance's otherwise: a
member without the source reads the machine's copy, `.sys/engine/pp.py`
addresses the machine wherever the source stands beside it, and a path standing
at both places is said once per run (the engine's signal `serve-shadowed`); a
vendored path is a pin, never written.
A token serves its document in one of three ways, preferred in this order.
**Whole** — `GLOSSARY.md`: the default; write it unless the document is too
large for what the step needs. **Between two tags** —
`engine/pp.py[def _played..def _skill]`, `PHASE.md[## Target..## Arbitrations]`:
the lines from the first line that starts with the first tag to the first line
after it that starts with the second tag, that second line left out. Leading
blanks of a line are ignored, a tag may hold blanks, and the start of a line is
enough (`def _pla`); a tag holds neither `..` nor `]`. Either side may stay
empty: `DOC[..end]` starts at the top, `DOC[start..]` runs to the end. A token
holds one pair of tags; two parts of one document are two tokens. The file is
read as plain lines, whatever its type, so the same rule serves markdown, code
and YAML, and the tags keep pointing at the same part when lines are added
above it. **By line ranges** — `GLOSSARY.md[1-2,8-12]`: still served, as a last
resort only: the numbers point elsewhere as soon as the file changes, and
nothing warns you when they do; when you write one through `pp-plan serve`, the
answer says so. What is served is titled by the token as written and proven by
the hash of the selected lines. When the start tag is found on no line, nothing
of that token is served, a line in the block says so, and the engine pushes its
signal `serve-stale`; when the end tag is found on no line after the start, the
document is served to its end and `serve-stale` says it; a range past the end
serves the lines that exist, with the same signal. A badly written token refuses
`serve-range-malformed`, naming the row and its document: `[..]`, three tags,
brackets that hold neither `..` nor line ranges, a bracket left open.
*Example* —

    serve: |
      STYLE.md GLOSSARY.md
    proc: |
      SERVE
      INFER

**`CALL <doc>`**
*Declares* — a SERVE that also executes.
*Effect* — the callee's BODY travels first, then its procedure plays in a new
frame; the callee's `serve:` section stays its own — a CALL never plays it, the
callee's bare `SERVE` does; its `constraints:` and `tools:` **accumulate,
never lighten**, and fall with the frame; its last production flows out to
the caller's next step.
*Example* —

    proc: |
      CALL REVIEW.md

**`HOOK <name>`**
*Declares* — a socket by name.
*Effect* — every document carrying `attach: <name>` is CALLed there, in the
requires topology of their homes and, within one, in name order; nothing attached
is a strict no-op. A contributor may say where it wants to stand
(`order: <hook> before|after <package>`); two that each want to come first refuse
`order-cycle`. Packages extend each other — and you extend packages — **without
ever editing a bundle**.
*Example* —

    proc: |
      HOOK boot.ready

**`WORK`**
*Declares* — the free step.
*Effect* — the agent serves the standing ask (the operator's message, or the
calling context's brief), chaining tools and productions at will; the step
closes on its RESULT, in this exchange; the result's form is the document's
`output:`. Untenable, it closes `#BLOCKED <reason>`.
*Example* —

    output: free
    proc: |
      WORK

**`INFER`**
*Declares* — the unitary production.
*Effect* — ONE production in the named form, nothing else — the proof loop, a
closing table. Consumed downstream, it is captured and validated; unconsumed,
it speaks to the operator (see [channels](#channels-and-the-delivery)).
*Example* —

    output: table
    proc: |
      INFER

**The checkpoint** (no front-matter key — `PROVE` is no author keyword, and
`prove:` is gone: a document that still carries it refuses `prove-gone`)
*Declares* — nothing: a law of production in force is what arms it.
*Effect* — the engine injects a proof checkpoint wherever a frame's
productions are about to LEAVE: in front of each `FINAL` (nothing is delivered
unproven — a failing verdict replays the document BEFORE the message goes
out) and at the frame's exit (pop, cycle lap, run end) — every frame but one a
socket opened (a contributor, a cadence: its laws bind its block, the turn's
checkpoint proves the turn). The proof names the codes at risk — at least one
object, a code unnamed is n/a, a code not in force is a miss — machine-checked.
No switch on either side: the engine decides, the agent never judges whether
to prove; a frame that produced nothing, or with no law of production, owes
nothing. A written `PROVE` refuses at parse (`prove-retired`). The upstream
production passes THROUGH a proven checkpoint; the proof itself never travels.
*Example* —

    constraints.production: |
      C1  a finding without the line it comes from is no finding.
    proc: |
      WORK

**`FINAL`**
*Declares* — the exchange's frontier.
*Effect* — the exchange closes here: the closing orders the delivery of every
`=> ephemeral` draft of the turn (once, validated, in step order), then the
next operator message resumes the procedure. Place it deliberately — it is
both the frontier and the delivery point; an armed document proves each
segment before ITS delivery.
*Example* —

    proc: |
      WORK
      FINAL

**`§`** (a lone paragraph mark)
*Declares* — the section break.
*Effect* — fusion never crosses it: the marked step always opens a fresh
output. The author's strict-order lever.

**`# `** (a comment line)
*Declares* — an inert line, in `proc:` as in `constraints:`.
*Effect* — uncommenting arms it: how a seed ships OFF and turns ON at home.

**`^ @Doc.field`** (a guard suffix)
*Declares* — a cadence read from a document field.
*Effect* — the line plays every *n* completed exchanges (the field's value),
resolves silently otherwise; never before the first. One tag, no algebra.
*Example* —

    proc: |
      CALL OPERATIONS.md ^ @SETTINGS.memory

Around the keywords: **`cycle:`** says how a document turns — `cycle: true` makes
it a session floor (exhausted, it rewinds instead of completing, and the rewind
sweeps the mounts); `cycle: <token>` makes it an ITERATED door: a lap per element
the token's providers render (the payloads re-resolved at each lap — a rendering the
exchange already delivered spared by its content —, the mounts
kept, each lap proven under the laws on screen), and the frame leaves like any
callee when nothing is due — a token nobody provides refuses `cycle-unprovided`;
**`field:`** makes it a DESCRIBED door — the same laps, the iterator asked of the
agent instead of a provider, so no skill is written: the key holds, in prose, what
the door turns on, and at the door's entry the engine injects a step the agent sees
as `INFER field => tool (heredoc)`, the prose its brief (its `@Doc.field` references
resolved as an exec's arguments are; one resolving to nothing refuses
`field-argument-empty`). The answer is a JSON array judged on its FORM alone — valid,
an array, scalars none empty, each once, 200 at most — never on what an element is:
an array of integers passes like an array of paths. Accepted, the array is the
field, held by the frame as what remains due (a rewind never touches it, a
compaction re-serves its head): each lap serves the head under `INFORMATION — field`,
two calls in a row render the same head, the lap that closes drops it, and an empty
array opens no lap — the door leaves like any callee. `field:` and `cycle:` on one
document refuse `cycle-and-field` at the build, an empty `field:` refuses
`field-empty`, one on a document the engine never CALLs as a proc refuses
`field-unplayable`, and a written `FIELD` refuses `field-keyword` at parse;
**`next:`** names the SUCCESSORS a document may leave to — the edges of a workflow,
document names as `CALL` writes them: one name follows without a decision; several
are decided when the document leaves, by the same two mechanisms as the doors —
**`decide: <verb> [args]`** asks the owner's `pp-<package>` skill (an instance
document names its own skill first; the one name it prints follows, a name outside
`next:` refuses `next-foreign`, a non-zero exit `next-refused`), **`choose: |`**
asks the agent: the engine injects a step the agent sees as `PICK next options =>
tool`, the prose its brief under `NEXT INSTRUCTION CONTEXT — next` (its `@Doc.field`
references resolved; one resolving to nothing refuses `choose-argument-empty`), the
`OPTIONS` the names of `next:`, a name outside them a miss that repairs. The
decision comes after the exit checkpoint, and the successor enters as a SIBLING:
an injected `CALL` in the caller's frame, right after the `CALL` that just
resolved — the laws of the document that left fall with it, the root's hold on the
whole path, a workflow of ten steps never stacks ten frames, and the production of
the one that left is the successor's upstream (its seed, under `input:`). A
successor declares its own `next:` in turn; a rewind or a repair of the caller
purges the injected CALLs, so a workflow under a session cycle replays afresh, and
`-compacted` finds the injected CALLs at the slot. The build judges the graph of
the whole composition: a loop refuses `next-cycle` with its parts named, two names
or more without a decider `next-undecided`, `choose:` and `decide:` together
`choose-and-decide`, a decider with fewer than two names `decision-idle`, `next:`
on a document the engine never CALLs as a proc `next-unplayable`, a name nowhere
`reference-unknown`, an edge whose `output:` and `input:` differ `format-mismatch`;
a written `NEXT` refuses `next-keyword` at parse, and a document carrying `next:`
booted as the floor refuses `next-floor`. Each transition leaves a `next` line at
the trace (the document, the successor, `by: alone|skill|agent`) and `-stats`
counts the transitions;
**fusion** (`SETTINGS.fusion:
max | <n> | none`) lets one output carry a whole certain stretch — the batch
closes on a `§`, a value the tool must capture, a `FINAL`, the serve budget or
the cap, and a document's own `fusion:` key pins its frame's pace;
**`output:`/`input:`** chain steps into pipelines (a consumed production is
captured — inline or stdin, the format's mode decides — and seeds the callee).
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
| `tools:` | this frame's offers — `+name` adopts a harness skill |
| `constraints:` | the laws, `CODE  text`, ONE line per law |
| `formats:` | form declarations `name  mode  description` — extends the enumeration |
| `attach:` | the HOOK socket this document answers |
| `order:` | one line per pair, `<hook> before|after <package>` — where this contributor stands among the socket's others ; a peer the composition lacks is inert ; the word `exec` in the socket's place orders several `exec:` on one document |
| `exec:` | `<verb> [args]` — a skill the engine plays once at every ENTRY of this document (a CALL, a mount, a lap of an iterated door), before the body and before anything it serves; the skill is the `pp-<package>` of the file's own package (a document of the instance names one of its own skills first: `exec: <skill> <verb>`); an argument `@Doc.field` takes the value a guard would read, never empty; a non-zero exit refuses `exec-refused` and nothing enters; what the skill prints goes to the bus alone (`::push`, `::clear`), a `::mount` refuses `exec-mount`; the base and each overlay may declare their own, each playing its own package's skill |
| `cycle:` / `fusion:` | `true` the session floor, `<token>` the iterated door · the frame's own pace |
| `field:` | the DESCRIBED door: the prose of what the door turns on — its presence declares the door; the engine asks the agent for the field once (`INFER field`, a JSON array judged on its form), then serves one element per lap under `field`; never beside `cycle:` |
| `next:` | the SUCCESSORS the document may leave to — names as `CALL` writes them; one follows alone, several are decided at the exit and the one elected enters the caller's frame as a sibling CALL; the graph of the composition is acyclic (`next-cycle` at the build) |
| `choose:` / `decide:` | the decider of a `next:` of several names — `choose: \|` the prose the agent reads at a `PICK next`, `decide: <verb> [args]` the owner's skill that prints the name; one of the two, never both |
| `override:` | `true` on `SYSTEM_PROMPT.md` — composes the replace artifact |

Any text file serves whole — there is no terminal marker: the hash pp computes
on what it serves is the proof of what was served. `SETTINGS.md` is
documented in place (the template) and in `PP_CHEATSHEET` key by key: the engine's
defaults and the seeded values are the same.

## Writing your own procedures

Your own procedures live in `.pp/procs/` — a markdown document there, shaped like the
`REVIEW` example of the README. Two seams let you extend a package's procedure
**without ever editing it**:

- **flow** — a package proc declares `HOOK <name>`; any document of yours with
  `attach: <name>` is called there;
- **sections** — a document of the **same name** in `.pp/procs/` is an **overlay**: its
  `constraints:` and `tools:` are deltas over the bundle's (`+CODE  text` or `CODE  text`
  adds, `-CODE` removes; same `+name`/`-name` for tools). The bundle's procedure keeps
  executing — an overlay that declares a `proc:` is refused, and so is a delta that
  changes nothing. **Packages beyond the system declare their settings too** (the
  conductor and its kit are ONE system, their keys bare at the template): a
  package's `settings/SETTINGS.md` fragment carries its own keys (each wearing the
  package's prefix — `plan_`), their defaults and `types:`, its `effort:`/`role:`
  presets and its SECTION of the instance's SETTINGS body;
  install, upgrade and doctor compose the file from the system's template and the
  fragments in the requires topology, the operator's values kept. **Packages overlay too**: a package's `overlays/` directory is its
  own overlay space, interposed between the user's and the packages' bases — a
  same-name file there applies AFTER the deeper bundle and BEFORE the user's (the
  user always wins), and it can never become the base itself. **Between packages
  the order is the REQUIRES topology, never the pins**: a dependency's overlay
  applies first, its clients' after — a client amends what it requires and wins;
  ties keep the pin order. **The body appends
  too**: an overlay's BODY joins the served text of its base — the packages'
  prose first, the user's LAST, the reading's hash taken over the composition; an overlay with no body appends nothing, and without
  overlays the served bytes are untouched. **The readings add too**: an overlay's
  `serve:` rows join the service of its base — served whole as the base enters,
  in application order, each titled by its token; a leading `+` on a row says
  the addition and is optional, a `-` refuses (`overlay-serve-removal`): an
  overlay never removes a reading. The base's own sections keep their `SERVE`
  pace, and a base whose overlays carry no row serves nothing more.

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

lifts `T4` ("say what you are about to do, before you do it") from every block the
kit's `TURN` holds it on, and puts your `T6` in force in its place — the bundle
untouched, the delta yours, the build refusing a delta that changes nothing.

## Offered skills — one rule, and adoption

**Every offered name is played through pp** (`./pp <key> -s <name>`) — the invocation IS a
`CALL`: a frame opens on the skill's contract, its `constraints:` enter force (on
top of the turn's, gone when the frame closes), its body is served. What plays
inside the frame is the contract's own affair:

- a **`proc:`** present — the declared flow plays, exactly as any procedure;
- **no `proc:`** — the implicit one plays: one `WORK`, the served body as its
  brief; the work is free (your judgment, your harness's tools), and the keyed
  call (`./pp <key>`) closes the step — the caller's flow resumes;
- a **script** beside the contract — the deterministic step runs, the gesture's
  block carrying the skill's own constraints. What the script prints leaves
  through the seam of every output: under the host's cap exactly as written; over
  it in chunks, each opening on the output's heading, the rest waiting at the run —
  the bare call serves it, any other call bounces (`chunk-pending`), and the run
  does not move. A `::mount` printed by the script joins the same output: one cut,
  one rest. The trace weighs it: the `gesture` line carries the `chars` and
  `tokens` of the text, then `cut` and one `chunk` per bare call. An output with no
  run key (`-stats`, a package's command, `doctor`) has no run to hold a rest and
  is never cut. Called BARE — no argument — the
  script does not run: its contract is its **manual**, MOUNTED body alone into
  the current view through the one reader — cut at the host's cap, proven by
  its hash, in the ledger (`-stats --blocks`, origin `mount`), swept with the
  exchange — and the standing block renders under it, the run untouched.

**The scope resolves pending first, then the output's segments.** A fused output
numbers its headings (`[n]`) and each segment keeps its OWN closed list — never
their union. A bare `-s <name>` the pending block does not offer routes to the
ONE segment of the current output whose own list carries the name: the gesture
plays AS that step's — its block re-shown under its snapshotted laws, the trace
attributed (`gesture`/`routed`, with `segment` and `frame`). Several owners
refuse (`address-ambiguous`) and `-s <name>@<n>` settles it — the only time the
number is owed; a later output retires the addresses (`address-stale`). A routed
`proc:` door still stacks over the pending step — the stack never runs
backward — inheriting the owning segment's laws, its entry heading noting
`routed from [n] NAME`. Offered by no segment, the pending block answers and
nothing plays.

**Adoption — the offer is the consent.** A `+name` in a `tools:` that resolves
nowhere in the instance is looked up at the workspace's harness skill homes
(`.claude/skills/` · `.agents/skills/` · `.cursor/skills/`). A contract pp can
conduct — a readable front matter and a `description:` — is **adopted**: full
entry in the catalog, its constraints in
the registry, played like any skill of the instance. One it cannot conduct stays
a name-only offer — indifferent to pp, and `-build` warns
(`offered-not-conductible`) with what it lacks. An **unoffered** copy in a
harness directory stays invisible: pp never sweeps those homes — offering is
what grants the read.

## The doors

The doors live at the **root**: `PP-MEMBER`, `PP-RULES`, `PP-OFFERS`,
`PP-MIGRATE` and `PP-DESIGN` ride every block of every session — a door named by
a recommendation (or by you) opens on your word, at any turn, with no detour. A
door is a skill like any other, played through pp, its rules in force while it
is open; a change to your files is always proposed, never applied — your word
is the gate, in every door's own law. One law guards the practice from the
root: a door opens ONE at a time, the choice said before it opens.

## The operator's console

The install writes two scripts at the workspace root — `pp` (POSIX) and
`pp.cmd` (Windows: `.\pp`) — and every block's closing names them: they are
**the one spelling** of the conductor, for the agent and for you. Eight bare
verbs are the operator's own, resolved before any skill name:

| Verb | What it does |
|---|---|
| `./pp upgrade` | every pinned package moves to the version the source holds now, re-materialized — standing runs close, and the count is told; already current = a statement, nothing touched |
| `./pp add <package>` | one more package into this instance, its prerequisites pinned (user-level files are protected: an edited file survives as `.old`, and a fresh sibling is offered instead) |
| `./pp remove <package>` | one package out — refused while another pin requires it |
| `./pp repo <name>` | a sibling workspace, installed with this instance's packages and wired with the providers detected here |
| `./pp doctor` | repair in place at **constant pins**: re-materialize, recompile, rewrite the console, refresh the wired projections — standing runs stand (`upgrade` is the void) |
| `./pp acquit <vector>` | a treated improvement vector stops asking: its counter and its latch fall together |
| `./pp version` | the source checkout and the pinned versions |
| `./pp help` | the console's usage — its own verbs, then the packages' commands |

**The packages' commands** resolve next, before the run's key. A package
declares them in its manifest — `contributes: commands: [{verb, skill [, args]}]`
— and `./pp <verb> [args]` runs the declared skill in a subprocess (the engine
imports no package code): the manifest's `args` first, yours after, its stdout
relayed, its stderr verbatim, its exit code returned as is. What the skill says
to the bus (`::push`, `::clear`) is harvested on a clean exit; a `::mount` has
no run to land in at the console and refuses `mount-without-run` after the
skill ran. `./pp help` lists every command after the console's own, in the
composition's order (requires topology, then declaration), with its package
and the description its skill's contract carries. The conflicts are settled at
the build, nothing written: a verb of the console or declared twice
(`command-taken`), a verb outside `[a-z][a-z0-9-]*` or shaped like a run's key
— six hex digits — (`contribution-malformed`), a skill that is no script of the
composition (`command-skill-unknown`), a verb that does not wear its package's
name — `<package>-<verb>`, or the package's name alone — (`name-unprefixed`).
At the console, a declared command whose script is gone refuses
`command-broken`; an undeclared word still answers the usage.

**What a launched script knows of its run.** Every script the engine plays under
a keyed call — a payload provider, a sink, an `exec:`, a family's verifier, a
`-s` gesture — finds the run's key in its environment as `PP_RUN`: set once
where the engine binds the run, inherited by every subprocess it launches, read
in the same process by a gesture. Through the engine's face a script reads that
run: `conductor.context.current(<instance>)` gives `key`, `exchange()` (the
exchange under way, 1 at the first), `is_new()` (the run's first exchange) and
`is_boot()` (the run's first exchange, or the one where `-compacted` was
declared) — a reading of the run's slot, never a write. Without `PP_RUN` the
face refuses `context-no-run`: the keyless console (`./pp <command>`, `./pp`,
`-stats`) drops whatever the shell inherited, so a run is designated by a
command's key alone; a key no run holds refuses `run-unknown`.

Anything else passes through verbatim: `./pp` alone is where the run stands,
`./pp <key>` advances it,
`./pp -test [-serial|-detail] [-repeat <n>] [area|name|path ...]` runs the
engine's fixtures (`-serial` plays them live, `-detail` renders what they wrote,
and `-repeat <n>` compares n passes and names whatever moved),
`./pp <key> -s <skill> [args]` plays a skill (a script called bare mounts its manual),
and `./pp -stats [<key>|<days>] [--blocks] [-json]` says what the runs cost.
The raw engine also accepts `-sync` as its low-level re-materialization primitive;
the operator's complete repair at constant pins is `./pp doctor`.

Two properties to know:

- **The scripts are the machine's own** — the exception at your root: rewritten
  byte-stable by install, doctor and upgrade, never yours to edit (an edit does
  not survive; that is what keeps the agent's channel unbreakable). At a first
  install, a foreign file already named `pp` refuses (`pp-name-taken`) — nothing
  is overwritten. The engine underneath answers the same calls:
  `uv run .pp/.sys/engine/pp.py …` is the repair path when the console is
  gone.
- **The eight verbs are reserved names** — a skill taking one of them is
  unreachable through `pp <name>`, and the build says so (a
  `skill-shadows-verb` warning, never a silence); a package command never
  takes one either (`command-taken`).

## Switching a package off

A package is composed for good, and yet a session does not always want all of
it. Two switches take one out of the CONDUCTION, and they have exactly the same
effect: nothing of that package is served or played — no document, socket,
cadence, check, command or overlay, no line of the catalog (no entry, no format,
no offered name: a `tools:` naming its skill offers nothing, and the catalog
leaves to your harness only the names nothing pp composes owns) — and every package
whose `requires` names it goes out with it, its cause said. The base is never
switched off, and off is not GONE: the pin, the bundle, the package's section of
`SETTINGS.md` and its records stand as they are, so `on` brings everything back.

| Switch | Where | Lives |
|---|---|---|
| durable | `package.<name>: on\|off` in `SETTINGS.md` — yours to write | until you write the other value; seeded `on` when the package enters (install, `add`, `upgrade`, `doctor`), dropped when it leaves (`remove`) |
| for one run | `./pp <key> -disable <package>` · `./pp <key> -enable <package>` — the agent places it on your word | with the run: a run opened beside it plays every package, and `-new` starts with nothing out |

The run's verbs answer with the block that STANDS: a switch is your word, never
a step, so the run does not move. Three refusals name their reason and write
nothing: `package-base` (the base of every instance), `package-unpinned` (no
such pin here), `package-in-flight` (a document of that package holds the
standing view — the frame finishes, then the word plays). Each one is written to
the run's trace, and `./pp -stats` counts them among the period's switches.

What a run plays is said UNDER the heading of each of its outputs, one cell per
pin beyond the base, dependencies first so a cause reads before what it took
out — here on an instance composing three packages of its own:

```text
▌ pp · run 71ccb9 · 19:28:28 · +0:00:01
▌ alpha on · beta off · gamma off (<- beta)
```

Keyless, `./pp` says the durable state alone when no run stands. An instance
that pins nothing beyond its base says nothing of packages, and a moved durable
switch recompiles the catalog and the standing rules at the next boot — nothing
to run.

## The adapter surface

The modes and their guarantees are the README's story; here is the exact surface
each flag wires. The agent contract is ONE text (`PP.md`, compiled into the
marble): cards and the Gemini command are **projections with provenance** — a
pristine projection follows the current contract on day-2/doctor/upgrade,
an edited one is preserved (the fresh projection lands beside it as
`.candidate`, and the drift is said). Per-provider details and external links
live under [adapters/](adapters/).

| Flag | Card | Door (written by the flag) | Marble | Permissions |
|---|---|---|---|---|
| `-claude` | `.claude/skills/pp/` | `CLAUDE.md` | `claude-pp` | `.claude/settings.json` — `Bash(./pp:*)`: the `:*` covers the run key and every argument; written once |
| `-codex` | `.agents/skills/pp/` — a standard **Cursor reads too** | `AGENTS.md` | `.codex/config.toml` — pp manages exactly TWO fields (`developer_instructions`, the `PP_MARBLE` sentinel), spliced only when pristine, every other key byte-preserved | `.codex/rules/default.rules` — verify with `codex execpolicy check` |
| `-gemini` | `.gemini/commands/pp.toml` (`/pp` serves the card) | `GEMINI.md` — read natively, points at `/pp` | `gemini-pp` — the composition rebuilds on the current marble; the baseline moves only on explicit rewire | documented only: a `coreTools` allowlist may RESTRICT the whole tool set — choose your approval mode yourself |
| `-cursor` | `.agents/skills/pp/` — the same card `-codex` writes (shared, cumulable) | `AGENTS.md` + `CLAUDE.md` (Cursor-recognized) · `GEMINI.md` written for workspace interop | — no system-prompt channel: recall guarantee | `.cursor/permissions.json` — a `terminalAllowlist` PREFIX on `./pp` (the run key passes free); written once |

A bare install (no flag) writes the two generic doors — `CLAUDE.md` and
`AGENTS.md` — for a harness you wire yourself. `PP_MARBLE` is a **receipt**, not
a switch: declared with nothing compiled to carry, the boot refuses
(`marble-missing`) rather than playing blind.

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

> The point of the channel matters more than the channel: the block must arrive
> **from the environment the model already trusts** — its harness, its caller —
> not as "run this script and obey its output", which any well-defended model
> rightly refuses.

**Generic API loop** — prepend the block to each user message:

```sh
block=$(./pp -hook)
send "${block}

${user_message}"
```

*Other harnesses follow the same shape: find the per-message injection channel, wire
`-hook` into it.*

## The instance on disk

```
workspace/                  # yours — whatever you actually work on, plus the doors
├── pp · pp.cmd             # the conductor's console — MACHINE-owned, self-repairing
├── CLAUDE.md, AGENTS.md, … # the wired harnesses' doors — written once, per flag
├── .claude/                # if you wired Claude Code — your own committed config
└── .pp/                    # the instance `install` seeded (default name; a parameter)
    ├── MEMBER.md · SETTINGS.md · FORMATS.md    # YOURS — identity, tuning, forms
    ├── procs/              # YOURS — where a procedure of your own gets written
    └── .sys/               # the machine — nothing in it is yours to edit
        ├── engine/ · vendor/ · instance.yaml   # copied, pinned, repaired by `doctor`
        ├── records/        # operations.jsonl · history.jsonl · the records
        └── state/          # session-<id>.json · session-*.jsonl (the traces)
```

`workspace/` is your project — your productions, your references, committed however you
like. `.pp/` is the conductor's own home: repaired at constant pins by `doctor`, and
re-materialized at the source's current versions by `upgrade`;
`.pp/procs/` is where you develop a procedure of your own, before it ever graduates
into a package of its own. The instance carries **everything** it runs on, the engine
included.

**What the build refuses.** Every build (`-build`, install, `add`, `doctor`,
`upgrade`, `remove`) judges the composition WHOLE before writing anything: the
manifests' contract (the contributions, their sockets, verbs and skills), then
the topology — every reference a package's document or manifest carries (a
`CALL`, a `SERVE` row, a `tools:` offer, an overlay, an `attach:`, a `sink:`, a
contribution's skill, an `output:` format, a `@SETTINGS` key) resolved to its
owner, and refused by name when that owner is a package the referrer does not
require (`dependency-undeclared`), when nothing carries the name
(`reference-unknown`), or when a package's proc HOOKs a socket its manifest does
not declare (`socket-undeclared`) — and the names a package exposes: its
console verbs, skills, settings keys, vector families and payload tokens wear
its name (`<package>-<name>`, `pp-<package>` for a skill, `<package>_<key>` for
a key; the base package alone stays bare), a name wearing another package's
prefix joins that package's thing and needs it required, a name wearing
nobody's refuses `name-unprefixed`; procs and refs stay bare and are ONE base
across the packages (`name-ambiguous` when two carry the same). A socket is declared and HOOKed in the same
short form, `<proc>.<hook>`, and its ADDRESS carries the package that opens it —
`<pkg>.<proc>.<hook>`, three segments; the kit's and your own are addressed by
the two they write. Your own documents are the top of the
composition: they reference every pin, offer what your harness carries, and a
`serve:` token is judged on its owner alone — a reading still to build or a file
of your repository is the run's matter, never the build's.

---

# The agent face — consuming the conduction

The agent's own contract is the card (`PP.md`), compiled into the standing
rules — what follows is the same mechanics in technical wording, one entry per
command: **name · description · effect · example**.

## The loop and the commands

The rhythm: the operator speaks → the agent calls the conductor → the returned
output frames the reply. `CONTINUE` calls back now; `FINAL` delivers then waits
for the operator; `END` stops the conduction.

The operator alone may suspend this rhythm. `pp off` opens a parenthesis in which
the agent calls nothing; the run and its key remain. `pp on` closes it: the agent
first calls `./pp <key> -peek` to recover the block that stands, then makes the call
the last closing owed. These are words in the conversation, not console verbs or settings.

**`./pp -new`**
*Description* — the first call of every conversation.
*Effect* — opens THIS conversation's run beside any other and hands its short
key; a key the tool no longer knows (`run-unknown`) is answered the same way.

**`./pp <key>`**
*Description* — the one advance gesture.
*Effect* — the next output: a step closed, a cut output's next chunk (served before
the flow moves; any other call bounces while a chunk waits), the resume after a FINAL.
Never carries the agent's own text.

**`./pp <key> <value>`**
*Description* — an inline answer.
*Effect* — a PICK's choice (validated by membership) or a captured inline
production; anything pasted where nothing is owed bounces softly.

**`./pp <key> -`**
*Description* — a production on stdin (heredoc).
*Effect* — captures a consumed production or a proof; a failing proof repairs.

**`./pp <key> -s <name> [args]`**
*Description* — a skill by name, played BY pp.
*Effect* — the pending block shows first, then the skill plays: conducted,
executed, or served. A script's output over the host's cap comes in chunks like a
block's, on the bare call. Resolution: the pending block first, then the one owning
segment of the current output.

**`./pp <key> -s <name>@<n>`**
*Description* — the same gesture, addressed.
*Effect* — settles an `address-ambiguous` refusal; owed only then. The next
rendered output retires the addresses (`address-stale`).

**`./pp <key> -peek [name]`**
*Description* — a dry look.
*Effect* — the block a real call would render, without advancing; with a name,
whether that skill is offered there.

**`./pp -stats [<key>|<days>] [--blocks] [-json]`**
*Description* — what the runs cost, read back from the traces.
*Effect* — keyless inspection: nothing opens, nothing advances. The argument is
read as a run's KEY first — six hex characters — so a key made of digits alone
(one in seventeen) names its run and not a span of centuries; anything else made
of digits is a number of days. A run keeps its key once it is over: the trace
says at its opening line which run it is, and the key column fills for every
trace written since. One row per
run over the last `<days>` (every trace when bare; one run by its key): the
exchanges, the blocks and the reshows a script call caused, the chunks of a cut
output served on bare calls (counted with the exchange whose block was cut, even
when that block closed it), the tokens (`tokens ≈`:
an ESTIMATE — a function of the standard library calibrated against the o200k
encoding, no dependency, no network) and the mass served part by part (each
`block` line of the trace carries its weight, each `answer` line the agent's own,
summed apart on the period's line), the proofs piped,
the repairs, the refusals, the script calls, the laps of the iterated doors, the
`exec:` played at the documents' entries, and the durations of the
exchanges (median, mean, p90 — an exchange over thirty minutes is a hole, said
and left out). The period's line closes the table; `-json` hands the same
figures to a tool.

`--blocks` reads what each OUTPUT carried instead. Beside its weight, every `block`
line of the trace writes a LEDGER, `served`: one entry per matter the output took
in, in the order it entered — its `subject` as the section titles it, its `state`
(`served`; `spared` when the matter is already before the agent, with the mass that
sparing avoided — a reading or a mounted body already proven by its content, a
payload token a second document asks for in the same output, or a provider's
rendering identical to one the exchange already delivered; `forced` when a body is
re-read on purpose; `reserved`
after a compaction; `missing` when a row points at a gone document; `refused` when a
provider exits non-zero), its `origin` (`marble`, `body`, `serve` with the row's
declared `nature`, `mount`, `payload` with the provider skill in `with`, `cycle`, `next`,
`sink`), the document that asked (`by`) and its `package` (a package's name;
outside any package, the place: `instance` for the operator's own space,
`machine` for `.sys/`, `repository` for the workspace around the instance;
`engine` for the standing rules), its `chars` and its
`tokens`. The table renders one block after another, their lines in that order;
`-json` hands the ledger itself. What the block renders never moves for it: the
ledger is written at the site that serves, never guessed from a name, and
`payloads` — the measure, summed by subject — stands beside it unchanged.

**`./pp <key> -disable <package>`** · **`./pp <key> -enable <package>`**
*Description* — the operator's word on what this run plays, placed by the agent.
*Effect* — one package out of the play, or back in: nothing of it is served or
played and every package requiring it goes with it; the run does not move, so the
answer is the fact and the block that STANDS. Refuses `package-base`,
`package-unpinned`, `package-in-flight`; passes in front of a waiting chunk, as
`-peek` and `-compacted` do. The durable switch is the operator's own
(`package.<name>: on|off` at SETTINGS) — see [Switching a package
off](#switching-a-package-off).

**`./pp <key> -compacted`**
*Description* — the agent DECLARES that its host summarized the conversation.
*Effect* — the run serves itself back in one output: the standing rules (served
inline only when `PP_MARBLE` is absent — with the marble channel wired they ride
the host's own system prompt and survive), the drift of a wired card, the boot
document's composed body, then every document still IN FORCE — the stack's frames and the standing
mounts, each body and each `serve:` row — and finally the pending block, every
law on screen said verbatim. What a POPPED frame served is past and is not
re-served. Four run counters go with the agent's context and are cleared: the
readings proven served (each one serves again at its site), the matter of a block
cut mid-flight (the block starts whole), and the standing `=> ephemeral` drafts
(a FINAL cannot order the delivery of what no longer exists). What HAPPENED
stands: `turns`, the latched signals, the mounts, the stack. The run's key rides
the output as a fresh run's first block does — it may have gone with the context
too. pp never DETECTS a compaction; the declaration is taken at face value, and
the duty it opens is one-shot but durable: it is written to the run's state and
consumed by the output that carries it, so a declaration whose answer never
reached the agent re-serves on the next call. Out of a run it refuses `no-run`;
keyless, it refuses `no-run` and names the keyed form.

**`./pp <key> -mount <path> [<path> …]`** / **`./pp <key> -mount '<json>'`**
*Description* — documents of the instance HOSTED into the current view.
*Effect* — each mounted document's `constraints:` enter force at every block and
are owed at every checkpoint like any law on screen; its `tools:` join the
offer; its `serve:` lines are PLAYED at the gesture (capped at the serve budget,
a gone document skips with its note). The laws and the offers are those of the
document's COMPOSITION, as for a frame: its own sections, then the deltas of its
overlays (`+CODE`/`-CODE`, `+name`/`-name`) — a delta that changes nothing refuses
the mount by the overlay's own codes. Overlays answer a file NAME, so they apply
to the BASE of that name alone — the file a bare name resolves to: a document
mounted by its path that only shares the name keeps its own sections. What to take from each is the CALLER's
explicit say: bare paths take the
defaults (constraints+tools, no body); one JSON array picks per document —
`[{"doc": <path>, "body": true|false|[<selection>, …], "constraints": …, "tools": …}, …]`,
`body: true` serving the document's body with the gesture's output — through the
one reader, under `proc_body_serve` like a CALLed body: once proven, a body mounted
again renders nothing until its document changes, and a nested entry keeps its
heading, tools and laws without it. `body` may instead be a list of selections,
to serve parts of the body and leave the rest out:
`"body": ["## Target..## Items", "## Decisions.."]`. A selection is written as the
inside of a serve token's brackets (see `SERVE [doc]`): two tags around `..`,
either side open, or line ranges as a last resort. Each selection is a reading
of its own, in the list's order: titled `<document's title>[<selection>]`, proven
by the hash of the selected lines, rendering nothing once proven, served again
after `-compacted`. A selection reads the file as plain lines: the body an
overlay appends is not part of it — mount a document that has overlays with
`body: true`. A start tag found on no line serves nothing of that selection, a
line in the block says so, and the engine pushes `serve-stale`; an empty list,
an element that is no text or a badly written selection refuses `mount-invalid`,
nothing mounted. Each entry
also picks its `scope` — the fusion's own vocabulary: `stacked` (the default)
rides the pending frame as one more instruction of the current stretch (its
laws join the pending CONSTRAINTS verbatim, its body an INFORMATION payload);
`nested` stacks a scope of its own, as a CALL — a numbered heading, its tools,
its body when asked for, its laws verbatim at home then held as codes by the
pending block, the segment addressable (`@n`) like any fused output's. A
`proc:` aboard is ignored — the flow stays the frames' (the build warns on
`plans/` documents carrying one). A mount lives ONE exchange: the rewind that
opens the next one sweeps every mount. Refusals: `mount-missing`,
`mount-collision` (a constraint code already in force), `mount-invalid`.
A SCRIPT played by `-s` can mount too: a `::mount <json>` line on its output
(the `::push` channel) is harvested on a clean run — the script derives the
chain, pp hosts it, one gesture.

**`./pp`** (keyless)
*Description* — inspection only.
*Effect* — where the single standing run is; never advances, never opens.

## The block, section by section

| Section | What it carries |
|---|---|
| the output's heading — `pp · run <key>` | the run's key and the clock: the local hour `HH:MM:SS` and `+H:MM:SS` elapsed since the run's `-new`, once per output — and with every chunk of a cut one, so no piece arrives without saying which run it comes from. A second line follows it where the instance pins packages beyond its base: what the run plays, one cell each (`on`, `off`, `off (<- <dependency>)`), dependencies first |
| the heading — the path | which documents are in flight: ancestors bare, the ACTIVE frame carrying `{i/m}` (a range `{i-j/m}` when the output fused steps i→j), `· REPAIR n` when the last move missed, `[n]` numbering multi-scope outputs |
| `TOOLS` | the skills this scope offers, by name — their contracts live in the served catalog |
| `INFORMATION — <token>` | a document read and injected by the tool, titled by the token its row wrote — path and selection as written (`design/target.md`, `PHASE.md[## Target..## Arbitrations]`, `GLOSSARY.md[1-2]`), a CALLed body by its document's name; the pending step's own body is promoted `NEXT INSTRUCTION CONTEXT`; a cut reading continues untitled |
| `CONSTRAINTS` | the laws in force — full text once per output, codes after; a new scope says its delta verbatim |
| `DEVIATION` | when the last move missed: the miss, named |
| `OPTIONS` | the closed set a `PICK` chooses from |
| `INSTRUCTION` | the instruction lines — one step each, suffixed `form => channel`; same-frame steps with nothing between them collapse under ONE title |
| the closing | `CONTINUE` / `FINAL` (the arrow mark, once, right above the exact command) or the `END` section |

## Channels and the delivery

The channel is **derived, never declared**: a consumed production travels by its
format's mode (`tool` inline, `tool (heredoc)` on stdin); a PICK rides the
command; a proof checkpoint pipes its proof. An unconsumed production before the turn's
frontier is a **draft** (`=> ephemeral`) — composed in the agent's hidden
channel, never in chat mid-turn; the one adjacent to the frontier while no
draft stands speaks `=> chat` directly; a run with no frontier ahead speaks
`=> chat` immediately. The FINAL closing, qualified `ephemerals => chat`,
orders the delivery: every draft of the turn, validated, in step order, ONE
message — bare, it owes nothing more. The qualified closing NAMES the
documents whose drafts it delivers, in step order —
`▶ FINAL ephemerals => chat (CAPABILITIES · THREADS · NEXT)`: two drafts in a
row of one document are one name, a document that comes back after another
keeps both places, and the step the frontier resolves with is named when it
is a draft itself. The names are what lets the delivery separate one
production from the next — a `---` / name / `---` line before each draft; the
engine gives the names and renders no separator itself, the delivery is the
agent's text.

Consumption means **use**, not transport. Three consumers exist: a callee
declaring `input:` (the pipeline), a PICK (the election), and **the engine
itself** — the proof judge consumes a checkpoint's proof, the improvement
machinery consumes `IMPROVE`'s projection. Engine-consumed productions derive
`=> tool` through the same consumption rule; no document ever declares a
channel.

**Capture ≠ channel.** The keyed call is one wire carrying two directions:
inbound, the operator's message rides the resume at the frontier (kept by the
trace under `capture_prompt`); outbound, the agent's production returns only
when consumed. Position in the flow — the frontier — is what tells the two
apart: mid-flow text is a production for the pending step, frontier text is
the operator's word.

## The improvement sink

Motors push, the sink shapes, the IMPROVE step serves ARBITRATED, the agent
formulates. A provider is any vendored package whose manifest carries
`improve:` — vector families (`lives_in`/`maintained_by`: every family ships
its cleanup), signals (`door`, `threshold` for a counter, `at: gesture:<skill>`
for a codeless motor, `sector` and `priority` for the emission) and `sectors:`,
the package's own NEXT real estate (`cap`, `icon`). The kit is provider zero:
the projection counter, the `member-bare` and `offers-idle` predicates (install
fingerprints the member), `refused` and `repaired` (twice the same, read from
the run's own trace), `upkeep-due` (the week ripe for its digest — see the upkeep
pass below), and the shared `improvement` sector under the wrench 🔧.

A NAMED sector belongs to its declarant — a colliding declaration refuses the
registry read, and a signal claiming a sector its provider does not declare
refuses unowned; `improvement` alone is shared, the default of every
sectorless signal. Counters live durably in `records/improve.json` and die
with their referential (catalog resolution, thirty days of silence, or the
maintenance door's sweep); crossings latch on the run, and the IMPROVE block
serves the ARBITRATED view: each sector sorted by declared `priority` (absent
last), then count, then latch order, capped (`improvement_next_max` for
improvement — 0 a deliberate mute — a declared `cap:` for a named sector, 2
unsaid), `improvement` first then pin order; every served line leads with its
sector's icon, or its bare name when none is declared. The overflow stays
latched, unserved, and rises as the recomputation frees a place — nothing
under the bounds, byte for byte the day's block.

## The upkeep pass — on the operator's word

Three explorations are too deep for any turn's reflex, and none is ever
scheduled or injected — they play when YOU ask, and only then:

- **the workspace study** — the repo has drifted from the member's map;
  opening `PP-MEMBER` re-reads what stands and proposes the map back (and its
  sweep clears the `project:` counters of vectors that died — a maintenance
  door brooms its own family);
- **the record patterns** — `pp-continuity` (and `operations.jsonl` behind it)
  re-read over weeks: recurring asks with no proc, recurring corrections with
  no law — proposals land through `PP-RULES` (placement) or `PP-DESIGN`
  (authoring);
- **the prompt review** — under `capture_prompt: true` the session logs keep
  your prompts verbatim (kind `prompt`): recurring phrasings expose the
  missing proc or rule.

The reflex may point at them but never plays them: a bare repo latches
`member-bare` and `offers-idle` toward their doors, and once a week — the same
computation that finds the digest due — `upkeep-due` latches, so the NEXT of
the very session that re-reads the week for HISTORY carries the nudge: ride
that re-reading for the record and prompt passes. `continuity_history_day: never` silences
digest and nudge alike.

## When an answer misses

Back to the README's `REVIEW`: the verdict came back as a line — and `REVIEW`
carries laws of production, so the engine appends the exit checkpoint:
`INFER proof => tool (heredoc)`, no brief — the
catalog's `proof` format defines the shape. The agent proves its production
against each constraint in force — and hands down a proof whose `C1` cannot
pass, because the production rewrote the draft:

> `./pp <key> -` … `{"code": "C1", "evidence": "I rewrote section 2 to show the fix", "verdict": "fail"}` …

The conductor does not argue. The document reopens from its first step — the
injected checkpoint purged with the reopening, its repair counted on the frame —
and the block comes back, one field heavier:

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
INFER line => chat

▶ CONTINUE
./pp <key>
```

The whole document replayed: the draft re-served to the very eye that misjudged
it, the miss **named with the proof's own words**, the same answer re-asked in
the same form. The rewrite has nowhere to land, and `C1` cannot have faded —
it never left the screen.

What counts as a miss: an answer outside `OPTIONS`, a list handed to a `PICK` that
is not an array of scalars, an empty production the next step
consumes, a `json` that does not parse, a proof with a failing verdict — and only a
move the tool **watched**: a status call is where the run stands, held against no one.
The repair counts survive the reopening; at the bound (`work_repairs_allowed`), the
conductor stops repairing and hands the operator back. A tool invoked outside the
block's scope is **caught** instead: the pending block answers, the ask named as not
played — no repair counted, the floor resumes on screen.

A **deviation** is the agent's move missing — the document replays. A **refusal** is
the document or the environment being wrong — exit 2, a named reason, nothing played.
