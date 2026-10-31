# The language

This file covers the procedure language, keyword by keyword: what each line of a `proc:` declares, what it does, and the keys that shape how a document turns.

- [The language, keyword by keyword](#the-language-keyword-by-keyword)
- [See also](#see-also)

## The language, keyword by keyword

#### The front matter

The front matter is **YAML** (`yaml.safe_load`): one flat mapping.

- Values keep their YAML types (`true` is a bool).
- A key left bare declares nothing.
- `#` comments vanish.
- Inside a block scalar (`constraints: |`), a `# `-prefixed line is a comment of pp's own. Uncommenting it arms the line.

#### The procedure

A **procedure** is the `proc:` key of that front matter: one keyword per line, optionally followed by an argument.

Every entry below follows one format: **name · declares · effect · example**.

### `PICK <name>`

*Declares* — a closed choice: the model elects ONE id.

*Effect* — the block renders `OPTIONS`, fed by the upstream production (the pipeline is the options source). It validates by membership; anything else repairs. The answer rides the command, verbatim.

The list the upstream hands it is judged at its CAPTURE, on the form a `field` has: a JSON array of scalars (strings or numbers), none empty, each once, 200 at most.

- A list of objects, an empty array or a bare scalar is a miss that repairs, the element named under `DEVIATION`.
- A number renders as its text (`[1, 2]` offers `1` and `2`).
- A list no capture judged (a callee's seed under `input:`) refuses `options-invalid`, the element named.
- A `PICK` with no producer before it refuses `options-empty`.

*Example* —

    proc: |
      PICK verdict

### `SERVE [doc]`

*Declares* — a reading the TOOL performs; the model has nothing to prove.

#### Sections

One bare `SERVE` dequeues one whole SECTION of `serve:`. A section is a paragraph of the block (a blank line separates sections), every line and document of it. n sections take n bare SERVEs, in order.

The section declares, the SERVE plays:

- a section without its SERVE is never read;
- a SERVE past the last section refuses `serve-exhausted`.

#### Chunks

The text is injected under `INFORMATION`. An output over the host's cap comes in chunks.

- An intermediate chunk says what remains: `(a reading continues: <n> characters in <m> more chunk(s))`.
- The bare call serves it. Any other call bounces, `chunk-pending`.
- `./pp <key> -skip` drops the rest instead. The block's closing comes at once, the readings the cut output carried stay unproven, and the trace says `chunk-dropped` with the characters left.

In a run its principal conducts, a chunk carries no command and says the rest comes at the next prompt (see [*The two conduction modes*](block.md#the-two-conduction-modes)). There the principal's call alone serves or skips it.

Each document is proven ONCE per run by its content, when its last chunk has left. Named again (another section, a `SERVE <doc>`, a mount, a CALL), it renders nothing, never the text.

#### How a token resolves

A token is addressed as the engine resolves it.

**A bare NAME** resolves through the member's search paths, in this order:

1. the instance's own space;
2. `procs/`;
3. the packages (a ref by its bare name);
4. the root of the member's repo (`README.md`).

The instance and the packages keep the upper hand on a same name.

A `procs/` space (the instance's, a package's) may shelve its documents in folders of its own. `procs/workflows/REVIEW.md` is `REVIEW.md` by name, everywhere: the catalog, a CALL, an offer, a mount, an overlay.

- A folder or a file whose name opens on `_` is never read.
- Two files of one name in one `procs/` refuse `document-duplicate` at the build, both paths named.

The pattern: `packaging/proc-folders`.

**A PATH** is a token carrying a `/` (`design/target.md`, `engine/pp.py`). It belongs to:

1. its MATERIAL, when one is named and holds it (below);
2. else the repository, when the repository holds it;
3. the instance otherwise.

So a member without the source reads the machine's copy. `.sys/engine/pp.py` addresses the machine wherever the source stands beside it. A path standing at both the repository and the instance is said once per run (the engine's signal `serve-shadowed`). A vendored path is a pin, never written.

#### The material of a reading

A MATERIAL is a named tree of files: a worktree, a clone, the repository itself.

| Name | What it is |
|---|---|
| `repo` | the repository around the instance, tacit |
| `work` | the tree a LAUNCHER gave the run (`PP_WORKDIR` at `-new`, kept at the slot) |
| any other name | yours, declared at `SETTINGS.md` as `material.<name>: <path>` |

A declared path is relative to the workspace or absolute, `~` expanded. A name must be given and is neither `repo` nor `work`, else `settings-invalid`. The path is judged on disk at the reading, never at SETTINGS.

A row reads from a material in three ways, the nearest word winning:

1. the row carries `@<name>` as its first token after its nature or as its last (`code: @core engine/pp.py[def forward..]`, `engine/pp.py @core`). This covers every document of the row; one mark a row.
2. the document that carries the row declares `material: <name>`;
3. a CALLed document without one inherits the nearest calling frame's.

Without any word, the run's `work` answers, and without a `work`, the repository. A row with no word reads exactly as it always has.

A material changes nothing for a bare NAME: an instance document is the instance's wherever the code lives.

The reading says its tree. Its title carries ` @<name>` when the material is not the repository (`INFORMATION — engine/pp.py[def forward..] @core`), and the ledger's place column names it (`-stats --blocks`).

What a material cannot give is served as today and SAID, a `note` diagnostic each:

| Signal | When |
|---|---|
| `material-unknown` | a name no catalogue knows (`@work` in a run given none included) |
| `material-missing` | a declared path that is no directory |
| `serve-stale` | a file the material lacks (« not in material ») |

A bare `@`, or two marks on one row, refuse `material-invalid`.

The lint of topology skips the mark; `pp-plan serve` writes it like any token.

A plan whose code lives in such a tree says it once, `pp-plan material <slug> [<name>]`. Every node born under it carries `material: <name>`, and a mount serves its rows from that tree (the plan package's `pp-plan` contract).

#### The three forms of a token

Preferred in this order:

| Form | Example | What is served |
|---|---|---|
| whole | `GLOSSARY.md` | the default; write it unless the document is too large for what the step needs |
| between two tags | `engine/pp.py[def _played..def _skill]`, `PHASE.md[## Target..## Arbitrations]` | the lines from the first line that starts with the first tag to the first line after it that starts with the second tag, that second line left out |
| by line ranges | `GLOSSARY.md[1-2,8-12]` | still served, as a last resort only: the numbers point elsewhere as soon as the file changes, and nothing warns you when they do; written through `pp-plan serve`, the answer says so |

The rules of a tag:

- leading blanks of a line are ignored;
- a tag may hold blanks, and the start of a line is enough (`def _pla`);
- a tag holds neither `..` nor `]`;
- either side may stay empty: `DOC[..end]` starts at the top, `DOC[start..]` runs to the end;
- a token holds one pair of tags; two parts of one document are two tokens.

The file is read as plain lines, whatever its type. So the same rule serves markdown, code and YAML, and the tags keep pointing at the same part when lines are added above it.

#### What could not be served

What is served is titled by the token as written and proven by the hash of the selected lines. The engine SAYS what it could not serve:

- the start tag found on no line: nothing of that token is served, a line in the block says so, and the engine pushes `serve-stale`;
- the end tag found on no line after the start: the document is served to its end, and `serve-stale` says it;
- a range past the end: the lines that exist are served, the same signal;
- a badly written token (`[..]`, three tags, brackets holding neither `..` nor line ranges, a bracket left open) refuses `serve-range-malformed`, naming the row and its document.

*Example* —

    serve: |
      STYLE.md GLOSSARY.md
    proc: |
      SERVE
      INFER

### `CALL <doc>`

*Declares* — a SERVE that also executes.

*Effect* — the callee's BODY travels first, then its procedure plays in a new frame.

- The callee's `serve:` section stays its own: a CALL never plays it, the callee's bare `SERVE` does.
- Its `constraints:` and `tools:` **accumulate, never lighten**, and fall with the frame.
- Its last production flows out to the caller's next step.

*Example* —

    proc: |
      CALL REVIEW.md

### `OPEN <doc>`

*Declares* — a CALL that opens a SPACE: a frame that never leaves by its exhaustion.

*Effect* — the document enters exactly as a CALL's callee does: body, readings, `exec:`, `input:`, its `initialize` mounts held while it stands, its laws and offers stacked.

Wherever the step stands, the space becomes the ROOT of the passage (see [`AWAIT`](#await--the-end-of-a-passage) below). Its last step done, the passage ends in it and the next message replays it from its first step.

The caller's steps after the `OPEN`, its `PROVE` included, do not play while the space stands. A space may open another; the deepest is the root.

The space leaves by `./pp <key> -close` alone (see ["The loop and the commands"](agent-face.md#the-loop-and-the-commands)). The caller then takes up at the step after its `OPEN`, in the same passage. What the space produced stays due at the caller's next written `PROVE`, the space's laws of production with it.

The build judges the argument as a CALL's (`reference-unknown`). It refuses `open-unplayable` on a document without `proc:` or with `next:`, `cycle:` or `field:`.

The pattern: `engine/patterns/control-flow/open`.

*Example* —

    proc: |
      WORK
      OPEN REVIEW.md
      INFER
      PROVE

### `HOOK <name>`

*Declares* — a socket by name.

*Effect* — every document carrying `attach: <name>` is CALLed there, in the requires topology of their homes and, within one home, in name order. Nothing attached is a strict no-op.

A contributor may say where it wants to stand: `order: <hook> before|after <package>`.

- `before` places it just before the first contributor of that package; `after`, just after the last.
- The preference moves that contributor alone; the others keep their order.
- Two contributors that each want to come first refuse `order-cycle`.

Packages extend each other, and you extend packages, **without ever editing a bundle**.

*Example* —

    proc: |
      HOOK turn.begin

#### The implicit `initialize` socket

Every proc also carries an IMPLICIT socket, `<proc>.initialize`. It is never written as a HOOK line (`socket-reserved`) and is played ONCE at the frame's entry, before its first step.

- What attaches there is CALLed once, and its laws and offer then stay on screen for the frame's life.
- What mounts there is mounted for the frame's life.
- Neither re-enters at a lap; both leave with the frame.
- `-compacted` re-serves the mounts.

The kit's boot contributors (RECALL, LEDGER, HISTORY, a house note) live at `boot.initialize`.

### `WORK`

*Declares* — the free step.

*Effect* — the agent serves the standing ask (the operator's message, or the calling context's brief), chaining tools and productions at will.

The step closes on its RESULT, in this exchange. The result's form is the document's `output:`. Untenable, it closes `#BLOCKED <reason>`.

*Example* —

    output: free
    proc: |
      WORK

### `INFER`

*Declares* — the unitary production.

*Effect* — ONE production in the named form, nothing else: the proof loop, a closing table.

- Consumed downstream, it is captured and validated.
- Unconsumed, it speaks to the operator (see [channels](block.md#channels-and-the-delivery)).

*Example* —

    output: table
    proc: |
      INFER

### `PROVE` — the checkpoint

*Declares* — the one point of proof.

A `proc:` writes `PROVE` where its author wants the proof. The engine injects none: not at the end of a passage, not at a frame's exit, not at a lap. `prove:` is no key, and `prove-gone`, `prove-retired` are no refusals.

#### What a `PROVE` asks

*Effect* — the step asks the proof over EVERY law of production on screen (the frame chain, the mounts, the laws a contributor left DUE). It covers everything produced since the last `PROVE` played in the run, whatever frame produced it. The debt is the run's: a callee's line under the caller's law is paid by the caller's `PROVE`.

A `PROVE` with nothing to ask (no law of production in force, or nothing produced since the last proof) resolves on one line (`nothing due: …`, traced `prove-idle`) and asks nothing.

Without a written `PROVE`, nothing is due: a frame leaves and a passage ends without a checkpoint.

A document a socket called (a contributor, a cadence) leaves its own laws DUE at the run after its frame pops; the trace says `owed`. They ride the blocks that follow among the laws in force, and the next `PROVE` names them.

The kit's `TURN` writes `PROVE` after `turn.end`, its last step. A door that carries a law of its own writes `PROVE` as its last step.

*Example* —

    proc: |
      HOOK turn.begin
      WORK
      HOOK turn.end
      PROVE

#### What the proof names

The proof names EVERY code the line asks: the laws of production in force, one object each, `n/a` written out where a law has no bearing.

- A code left unnamed is a miss (`the PROOF leaves N code(s) unnamed: …`).
- A code not in force is a miss too.
- A behavior code named in addition is tolerated.
- A mini-proof names its repaired codes alone, machine-checked.

There is no switch on the agent's side: the author writes the point of proof, the agent never judges whether to prove. The upstream production passes THROUGH a proven checkpoint; the proof itself never travels.

#### A failed object

A failed object has three issues:

| Form | Effect |
|---|---|
| bare `fail` | replays the document |
| `fail` naming its `"fix"` | repairs IN PLACE: the agent corrects the production and pipes a mini-proof over those codes alone |
| `fail` carrying `"blocked": "<what is missing>"` (a non-empty text) | DECLARES a gap (below) |

A declared gap works this way:

- the checkpoint closes without a repair, and the production leaves;
- the trace writes a `blocked` line (the codes and their texts), counted by `-stats` as gaps declared;
- the closing of the block that follows says `(a gap declared: <code> -- <text>)`;
- the agent tells the principal that gap in its answer.

In one proof, a bare `fail` outweighs the rest. An object carrying both `fix` and `blocked` repairs in place, and its mini-proof may declare the gap.

*Example* —

    constraints.production: |
      C1  a finding without the line it comes from is no finding.
    proc: |
      WORK

### `AWAIT` — the end of a passage

*Rendered, never written* — no keyword closes a passage. A `FINAL` written in a `proc:` refuses `final-gone` at the build; a `cycle: true` refuses `cycle-gone`.

#### The root

The ROOT of the passage is the deepest frame of the chain that still yields a step. The chain starts at the deepest SPACE (`OPEN`, `-open`) or at the floor, then follows each callee the LAST step of the frame below opened. The root exhausts, and the run PARKS on it.

The first line of every output names it: `▌ pp · run <key> · root <name> · …`. The block and its trace line carry it as `root`, beside the unchanged `stack`.

#### The closing

*Effect* — the closing is a bare `▶ AWAIT`.

- It delivers nothing: every unconsumed production was said `=> words` at its own step.
- It proves nothing: the proof is the `PROVE` the document wrote before it.

At that one site, the exchange is counted, the cadences and the payload tags advance, the mounts of the passage are swept, and the held ones are kept.

#### Waiting for a message

The run then AWAITS a MESSAGE. `persistence.awaits_of` reads `message`, or `production` while a step is pending; this is what `-peek`, the renewal mark and the launchers read.

The principal's next message, or a bare call, rewinds the root, and the next passage opens on its first step, under the same key.

A door opened on a parked run plays and leaves it parked, nothing counted again. A frame an injected CALL opened (a door, a contributor) is never the root.

*Example* — the kit's `TURN`, the root of every passage of a kit instance:

    proc: |
      HOOK turn.begin
      WORK
      HOOK turn.end
      PROVE

### `§` — the section break

A lone paragraph mark. Fusion never crosses it: the marked step always opens a fresh output. It is the author's strict-order lever.

It belongs to the document whose step needs it, never to a floor on behalf of its contributors:

- the kit's `TURN` carries none: with nothing at `turn.end`, the end of the passage closes the WORK's own output;
- steering's `THREADS` opens on one (the pass after the work) and keeps one before `NEXT` (the table after the pass).

A reading a script computes (`with:`) is thus never rendered ahead of the work it depends on.

#### The launch frontier

In a run its principal conducts, `§` is the author's LAUNCH FRONTIER. The output ends there, on no closing line, and the launch ends with it.

The next launch opens on the marked step, the stack still awaiting a production: nothing proven, nothing parked. A message that arrived meanwhile rides the head of that prompt.

It is the one way an author forces a boundary between two launches inside a passage; no other word does it. The trace says `section` once per break, with the marked step.

### `# ` — a comment line

An inert line, in `proc:` as in `constraints:`. Uncommenting arms it: that is how a seed ships OFF and turns ON at home.

### `^ @Doc.field` — a guard suffix

A cadence read from a document field. The line plays every *n* completed exchanges (the field's value) and resolves silently otherwise; never before the first. One tag, no algebra.

*Example* —

    proc: |
      CALL DIGEST.md ^ @SETTINGS.digest_every

### Around the keywords

#### `cycle:`

**`cycle:`** says how a document turns.

- A root needs no key to turn: exhausted, it parks the run, and the next message starts it again on its first step (see [`AWAIT`](#await--the-end-of-a-passage)). `cycle: true` refuses `cycle-gone` at the build.
- `cycle: <token>` makes it an ITERATED door: a lap per element the token's providers render.
  - The payloads are re-resolved at each lap; a rendering the exchange already delivered is spared by its content.
  - The mounts are kept, and each lap is proven under the laws on screen.
  - The frame leaves like any callee when nothing is due.
  - A token nobody provides refuses `cycle-unprovided`.

#### `field:`

**`field:`** makes it a DESCRIBED door: the same laps, but the iterator is asked of the agent instead of a provider, so no skill is written. The key holds, in prose, what the door turns on.

At the door's entry the engine injects a step the agent sees as `INFER field => tool (heredoc)`, the prose its brief. Its `@Doc.field` references are resolved as an exec's arguments are; one resolving to nothing refuses `field-argument-empty`.

The answer is a JSON array judged on its FORM alone: valid, an array, scalars none empty, each once, 200 at most. It is never judged on what an element is: an array of integers passes like an array of paths.

Accepted, the array is the field, held by the frame as what remains due. A rewind never touches it, and a compaction re-serves its head.

- Each lap serves the head under `INFORMATION — field`.
- Two calls in a row render the same head.
- The lap that closes drops it.
- An empty array opens no lap: the door leaves like any callee.

The build refuses:

| Refusal | When |
|---|---|
| `cycle-and-field` | `field:` and `cycle:` on one document |
| `field-empty` | an empty `field:` |
| `field-unplayable` | `field:` on a document the engine never CALLs as a proc |
| `field-keyword` (at parse) | a written `FIELD` |

#### `next:`

**`next:`** names the SUCCESSORS a document may leave to: the edges of a workflow, document names as `CALL` writes them. One name follows without a decision. Several are decided when the document leaves, by the same two mechanisms as the doors:

- **`decide: <verb> [args]`** asks the owner's `pp-<package>` skill (an instance document names its own skill first). The one name it prints follows. A name outside `next:` refuses `next-foreign`; a non-zero exit, `next-refused`.
- **`choose: |`** asks the agent. The engine injects a step the agent sees as `PICK next options => tool`, the prose its brief under `NEXT INSTRUCTION CONTEXT — next`. Its `@Doc.field` references are resolved; one resolving to nothing refuses `choose-argument-empty`. The `OPTIONS` are the names of `next:`; a name outside them is a miss that repairs.

The decision comes after the exit checkpoint, and the successor enters as a SIBLING: an injected `CALL` in the caller's frame, right after the `CALL` that just resolved.

- The laws of the document that left fall with it; the root's laws hold on the whole path.
- A workflow of ten steps never stacks ten frames.
- The production of the one that left is the successor's upstream (its seed, under `input:`).
- A successor declares its own `next:` in turn.
- A rewind or a repair of the caller purges the injected CALLs, so a workflow under a session cycle replays afresh.
- `-compacted` finds the injected CALLs at the slot.

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

Each transition leaves a `next` line at the trace (the document, the successor, `by: alone|skill|agent`), and `-stats` counts the transitions.

#### Fusion

**Fusion** (`SETTINGS.fusion: max | <n> | none`) lets one output carry a whole certain stretch. The batch closes on:

- a `§`;
- a value the tool must capture;
- the end of the passage;
- the serve budget or the cap.

A document's own `fusion:` key pins its frame's pace.

#### `output:` / `input:`

**`output:` / `input:`** chain steps into pipelines: a consumed production is captured (inline or stdin, the format's mode decides) and seeds the callee.

#### The conductor holds the rest

Everything else is held by the conductor:

- the state **is** the instruction stack;
- the run survives the process;
- anything unresolved **refuses**: exit 2, a named reason, nothing played.

## See also

- [The front matter](front-matter.md) — every front-matter key, and how to write your own procedures.
- [The block](block.md) — the block section by section, the channels and the two conduction modes.
- [The agent's face](agent-face.md) — the loop and the `./pp` commands (`-close`, `-open`, `-skip`, `-compacted`).
- [Offered skills](skills.md) — the skills a document offers and how adoption works.
