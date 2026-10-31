# The loop and the commands

The agent's own contract is the card (`PP.COMMON.md`, and `PP.CONDUCT.md` when the LLM conducts), compiled into the standing rules; what follows is the same mechanics in technical wording, one entry per command: **name · description · effect**.

Contents:

- [The loop and the commands](#the-loop-and-the-commands)
  - [`./pp -new [<message> …]`](#pp--new-message-)
  - [`./pp <key>`](#pp-key)
  - [`./pp <key> <value>`](#pp-key-value)
  - [`./pp <key> -`](#pp-key--)
  - [`./pp <key> -s <name> [args]`](#pp-key--s-name-args)
  - [`./pp <key> -s <name>@<n>`](#pp-key--s-namen)
  - [`./pp <key> -open <name>`](#pp-key--open-name)
  - [`./pp <key> -close`](#pp-key--close)
  - [`./pp <key> -peek [name]`](#pp-key--peek-name)
  - [`./pp -stats`](#pp--stats-keydays---blocks--json)
  - [`./pp <key> -disable` / `-enable`](#pp-key--disable-package--pp-key--enable-package)
  - [`./pp <key> -compacted`](#pp-key--compacted)
  - [`./pp <key> -mount`](#pp-key--mount-address-address---pp-key--mount-json)
  - [`./pp` (keyless)](#pp-keyless)
- [See also](#see-also)

## The loop and the commands

The rhythm: the operator speaks, the agent calls the conductor, and the
returned output frames the reply. `CONTINUE` calls back now. `AWAIT` ends the
passage and waits for the operator.

The operator alone may suspend this rhythm:

- `pp off` opens a parenthesis in which the agent calls nothing. The run and
  its key remain.
- `pp on` closes it. The agent first calls `./pp <key> -peek` to recover the
  block that stands, then makes the call the last closing owed.

These are words in the conversation, not console verbs or settings.

### `./pp -new [<message> …]`

*Description* — the first call of every conversation.

*Effect* — opens THIS conversation's run beside any other and hands its short
key. A key the tool no longer knows (`run-unknown`) is answered the same way.

The words after `-new` are the principal's MESSAGE, joined by a blank: the
grammar of `./pp <key> <message>`, at the opening. The message is traced
`prompt` right after `new`, before the first block. What a base serves of it
is its own: the kit serves none. Bare, the opening is exactly what it was.

#### The key is always drawn

The key is always DRAWN here. Its slot is reserved exclusively before
anything is written, and a refused opening leaves no run behind.

A launcher names no key. `PP_NEW_KEY`, its adoption (`persistence.adopt`) and
the refusals `new-key-invalid` and `new-key-taken` are retired. A launcher
that wants the key plays `-new` itself and reads it on the first output, as
the run's principal does (see
[The two conduction modes](block.md#the-two-conduction-modes)).

#### A run conducted by its principal

A LAUNCHER that makes the run advance itself says so at the opening:
`PP_CONDUCTED_BY_PRINCIPAL=true` makes `-new` open a run **conducted by its
principal**.

| Value of `PP_CONDUCTED_BY_PRINCIPAL` | Result |
|---|---|
| `true` | the run is conducted by its principal |
| absent, empty or `false` | the run is conducted by the LLM — today's run, byte for byte |
| any other value | refuses `conducted-by-invalid` before anything is written |

The mode is the RUN's. It is written `conducted_by: principal` in its slot and
on its trace's `new` line (a run the LLM conducts writes neither). It is kept
by an upgrade's renewal mark and given back at the reopening.

A run its principal conducts may stand MID-EXCHANGE: its slot awaits a
production, so an agent is at work on it. There, a `-new` WITHOUT the mark is
that agent's. It opens nothing and answers one line, rc 0:
`pp: a run is already open -- <key>`. A marked `-new`, or one while every
such run is parked on its AWAIT, opens as always.

What the mode changes in the blocks and in the keyed calls is said under
[Channels and the delivery](block.md#channels-and-the-delivery),
§ [The two conduction modes](block.md#the-two-conduction-modes).

#### The run's material: `PP_WORKDIR`

A LAUNCHER may also name the run's MATERIAL, the tree it works on:
`PP_WORKDIR=<path>`, relative to the workspace or absolute. It is read by
`-new` alone and kept at the slot as the material `work`: on the trace's `new`
line, and through an upgrade's renewal mark.

A serve row reads that tree by `@work`; see
[The language, keyword by keyword](language.md#the-language-keyword-by-keyword),
*The material of a reading*. `pp-agent --work` already hands it.

#### One more root of documents: `PP_DOCUMENTS`

A LAUNCHER may also give the run one more ROOT of documents:
`PP_DOCUMENTS=<absolute directory>`. It is read by `-new` alone and kept at
the slot: on the trace's `new` line, and through an upgrade's renewal mark.

For that run alone, the directory is a space of documents between the
instance's own space and the packages':

- a name it carries resolves there (a `PP_DOOR`, a `CALL`, an offer);
- a document there declares (`attach:`, `mount:`, `provides:`);
- a document there named as a package's document is that document's overlay;
- the instance's space keeps the last word.

The root is flat: its own `*.md` files, no subdirectory, a `_` file never
read.

The console without a key, the build, `upgrade` and `doctor` compose without
it, and another run of the instance sees nothing of it. The instance's own
documents never name a document of a root: the build judges their `CALL`s
without one.

Refusals:

- a path that is not an absolute directory refuses `documents-unknown` before
  anything is written;
- a keyed call that names another root refuses `documents-fixed`, nothing
  played.

### `./pp <key>`

*Description* — the one advance gesture.

*Effect* — the next output: a step closed, a cut output's next chunk, or the
resume after an AWAIT. A waiting chunk is served before the flow moves, and
any other call bounces while a chunk waits. The call never carries the agent's
own text.

In a run its principal conducts, the call is the principal's when it carries
`PP_CONDUCTED_BY_PRINCIPAL=true`, and the agent's otherwise:

- the agent's bare call refuses `principal-advances`;
- the principal's serves the output the agent's last value left HELD, else
  advances (see [The two conduction modes](block.md#the-two-conduction-modes)).

### `./pp <key> <value>`

*Description* — an inline answer.

*Effect* — a PICK's choice (validated by membership) or a captured inline
production. Anything pasted where nothing is owed bounces softly.

### `./pp <key> -`

*Description* — a production on stdin (heredoc).

*Effect* — captures a consumed production or a proof. A failing proof
repairs.

### `./pp <key> -s <name> [args]`

*Description* — a skill by name, played BY pp.

*Effect* — the pending block shows first, then the skill plays: conducted,
executed, or served. A script's output over the host's cap comes in chunks
like a block's, on the bare call.

Resolution: the pending block first, then the one owning segment of the
current output.

### `./pp <key> -s <name>@<n>`

*Description* — the same gesture, addressed.

*Effect* — settles an `address-ambiguous` refusal; owed only then. The next
rendered output retires the addresses (`address-stale`).

### `./pp <key> -open <name>`

*Description* — the agent opens a SPACE.

*Effect* — the name is read as `-s` reads it: offered by the current output,
`@<n>` when several segments offer it. It must be a proc that can be a space;
otherwise the call refuses `open-unplayable` (no `proc:`, or `next:`,
`cycle:`, `field:`).

The proc enters at the pending step as an `OPEN` written there would, and
becomes the root (see [`OPEN <doc>`](language.md#open-doc)). In a run its
principal conducts, the call answers `pp: opened` and the space's first block
comes at the principal's next call.

### `./pp <key> -close`

*Description* — the deepest space leaves.

*Effect* — the space and every frame stacked over it are popped:

- a step pending there is dropped;
- what was said stays said;
- their productions stay due at the next written `PROVE` below, their laws of
  production with them.

The caller takes up where it stood, in the same passage: the step after its
`OPEN`, or the step that was pending when `-open` opened the space. The next
block renders.

The trace says `closed`, as it says `opened` with the name when `-open` opens
a space. With no space open, the call refuses `space-none`. In a run its
principal conducts, the call answers `pp: closed`.

### `./pp <key> -peek [name]`

*Description* — a dry look.

*Effect* — the block a real call would render, without advancing. With a
name: whether that skill is offered there.

### `./pp -stats [<key>|<days>] [--blocks] [-json]`

*Description* — what the runs cost, read back from the traces.

*Effect* — keyless inspection: nothing opens, nothing advances.

#### The argument

The argument is read as a run's KEY first (six hex characters). So a key made
of digits alone (one in seventeen) names its run and not a span of centuries.
Anything else made of digits is a number of days.

A run keeps its key once it is over: the trace says at its opening line which
run it is, and the key column fills for every trace written since.

At a machine, a key its own traces do not hold is looked for among the
instances that borrow it. The run found is rendered under a line naming where
it lives. A key no trace holds refuses `run-unknown`.

#### What a row counts

One row per run over the last `<days>` (every trace when bare; one run by its
key):

- the exchanges, the blocks and the reshows a script call caused, and the
  chunks of a cut output served on bare calls (counted with the exchange whose
  block was cut, even when that block closed it);
- the tokens — `tokens ≈`, an ESTIMATE: a function of the standard library
  calibrated against the o200k encoding, no dependency, no network;
- the mass served part by part: each `block` line of the trace carries its
  weight, each `answer` line the agent's own, summed apart on the period's
  line;
- the proofs piped, the VALUES the agent handed, the repairs, the refusals,
  the script calls, the laps of the iterated doors, and the `exec:` played at
  the documents' entries;
- the durations of the exchanges (median, mean, p90). An exchange over thirty
  minutes is a hole, said and left out.

The time conducted and the time spent by kind (work, proofs, script calls,
answers) count the same exchanges: the closed ones that are no hole. The time
of the holes and of the open exchange is said apart, `outside them`.

#### What counts as a value

A VALUE is what the agent hands the conduction: an `answer` line whose
`channel` goes to the tool (`tool`, `tool (heredoc)`). It is counted by its
keyword: a proof, a PICK, a NEXT, a field, an INFER or a WORK whose
production a step consumes.

A bare close is no value. Neither is a stray production: its channel is
`words`, it bounces softly, and the trace marks it `stray`.

Every `answer` line carries the step's `channel` from engine `0.1.0-beta.53`
on. A line written before counts by its keyword alone (PROVE, PICK, NEXT,
FIELD), and the period says how many such lines it read.

#### The closing lines and `-json`

The period's line closes the table, and one more line follows: the averages
per CLOSED exchange. It gives the conduction calls (blocks and chunks), the
chunks, the values with their keywords, and the script calls. For example, on
this product's own traces, 2026-09-29 → 2026-10-05:

`per closed exchange: 15.7 conduction call(s) (7.0 chunk(s)), 1.0 value(s) (PROVE 1.0), 11.3 script call(s)`

`-json` hands the same figures to a tool: per run its totals and, under
`detail`, its exchanges one by one; over the period `values` and
`per_exchange`.

#### `--blocks`: what each output carried

**`--blocks`** reads what each OUTPUT carried instead. Beside its weight,
every `block` line of the trace writes a LEDGER, `served`: one entry per
matter the output took in, in the order it entered.

| Field | What it says |
|---|---|
| `subject` | as the section titles it |
| `state` | `served`; `spared` when the matter is already before the agent, with the mass that sparing avoided (a reading or a mounted body already proven by its content, a payload token a second document asks for in the same output, a provider's rendering identical to one the exchange already delivered); `forced` when a body is re-read on purpose; `reserved` after a compaction; `missing` when a row points at a gone document; `refused` when a provider exits non-zero |
| `origin` | `marble`, `body`, `serve` with the row's declared `nature`, `mount`, `payload` with the provider skill in `with`, `cycle`, `next`, `sink` |
| `by` · `package` | the document that asked, and its package — or, outside any package, the place: `instance` for the operator's own space, `machine` for `.sys/`, `repository` for the workspace around the instance; `engine` for the standing rules |
| `chars` · `tokens` | the mass |

The table renders one block after another, their lines in that order. `-json`
hands the ledger itself.

What the block renders never moves for it. The ledger is written at the site
that serves, never guessed from a name. `payloads` (the measure, summed by
subject) stands beside it unchanged.

### `./pp <key> -disable <package>` · `./pp <key> -enable <package>`

*Description* — the operator's word on what this run plays, placed by the
agent.

*Effect* — one package out of the play, or back in. Nothing of it is served or
played, and every package requiring it goes with it. The run does not move, so
the answer is the fact and the block that STANDS.

- Refusals: `package-base`, `package-unpinned`, `package-in-flight`.
- It passes in front of a waiting chunk, as `-peek` and `-compacted` do.

The durable switch is the operator's own (`package.<name>: on|off` at
SETTINGS); see
[Switching a package off](console.md#switching-a-package-off).

Who places it depends on who conducts the run:

- in a run the LLM conducts, the verb and the principal's word on the
  packages are taught in `engine/system/SYSTEM.CONDUCT.md`, served to that
  run alone;
- in a run its principal conducts, the house plays the verb itself under the
  principal's mark: `agent chat --json` takes
  `{"kind": "package", "name": …, "on": …}`.

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

What a POPPED frame served is past and is not re-served.

#### What is cleared, what stands

Three run counters go with the agent's context and are cleared:

- the readings proven served (each one serves again at its site);
- the matter of a block cut mid-flight (the block starts whole);
- the codes-mode ledger (every law says its text again).

What HAPPENED stands: `turns`, the latched signals, the mounts, the stack.

The run's key rides the output as a fresh run's first block does: it may have
gone with the context too.

#### A declaration, never a detection

pp never DETECTS a compaction; the declaration is taken at face value. The
duty it opens is one-shot but durable: it is written to the run's state and
consumed by the output that carries it. So a declaration whose answer never
reached the agent re-serves on the next call.

Out of a run it refuses `no-run`. Keyless, it refuses `no-run` and names the
keyed form.

### `./pp <key> -mount <address> [<address> …]` / `./pp <key> -mount '<json>'`

*Description* — documents of the composition, each named by its ADDRESS,
HOSTED into the current view.

#### The address

**The address** names a document as a `CALL` does, in one of three forms,
resolved by one reader from the instance's own `vendor/`:

| Form | Example | What it names |
|---|---|---|
| a NAME | `BATCH.md`, `pp-plan` | the composition's base document of that name — a package's proc or ref, its overlays applying — or, failing a document, the contract of the skill of that name |
| a PATH | `plans/core/4-l-execution/PHASE.md` | the document at that place, the instance first, the repository last — the form for a document no name distinguishes (a node of a plan, a sidecar) |
| `<package>:<path>` | `doc:kinds/_generic.md` | a file of that package that a name does not reach (outside its `procs/`, `refs/` and `overlays/`), taken from the copy of the package the instance plays |

An absolute path, a `..`, a package not in play or an address no file answers
refuses `mount-missing`.

The run keeps the ADDRESS, never a path of the machine: a mount survives
`doctor` and `upgrade`.

#### What a mount brings

*Effect* — for each mounted document:

- its `constraints:` enter force at every block and are owed at every
  checkpoint like any law on screen;
- its `tools:` join the offer;
- its `serve:` lines are PLAYED at the gesture (capped at the serve budget; a
  gone document skips with its note).

The laws and the offers are those of the document's COMPOSITION, as for a
frame: its own sections, then the deltas of its overlays (`+CODE`/`-CODE`,
`+name`/`-name`). A delta that changes nothing refuses the mount by the
overlay's own codes.

Overlays answer a file NAME, so they apply to the BASE of that name alone: the
file a bare name resolves to. A document mounted by its path that only shares
the name keeps its own sections.

#### What to take from each

**What to take from each** is the CALLER's explicit say:

- bare paths take the defaults — constraints and tools, no body;
- one JSON array picks per document — `[{"doc": <path>, "body":
  true|false|[<selection>, …], "constraints": …, "tools": …}, …]`.

`body: true` serves the document's body with the gesture's output, through
the one reader, under `proc_body_serve` like a CALLed body. Once proven, a
body mounted again renders nothing until its document changes. A nested
entry keeps its heading, tools and laws without it.

#### Body selections

`body` may instead be a list of selections, to serve parts of the body and
leave the rest out: `"body": ["## Target..## Items", "## Decisions.."]`.

A selection is written as the inside of a serve token's brackets (see
[`SERVE [doc]`](language.md#serve-doc)): two tags around `..`, either side
open, or line ranges as a last resort.

Each selection is a reading of its own, in the list's order. It is titled
`<document's title>[<selection>]` and proven by the hash of the selected
lines. It renders nothing once proven, and is served again after
`-compacted`.

A selection reads the file as plain lines: the body an overlay appends is not
part of it. Mount a document that has overlays with `body: true`.

When a selection fails:

- a start tag found on no line serves nothing of that selection; a line in the
  block says so, and the engine pushes `serve-stale`;
- an empty list, an element that is no text or a badly written selection
  refuses `mount-invalid`, nothing mounted.

#### The scope of an entry

Each entry also picks its `scope`, the fusion's own vocabulary:

- `stacked` (the default) rides the pending frame as one more instruction of
  the current stretch. Its laws join the pending CONSTRAINTS verbatim, its
  body an INFORMATION payload. A contributor that declares `payloads:`
  (`TEAM_INBOX`, `RECALL`, `LEDGER`, `NEXT_MOVE`) serves its body WITH the
  section its tokens render, before it, and not at all when nothing rendered:
  a brief without its matter instructs nothing.
- `nested` stacks a scope of its own, as a CALL: a numbered heading, its
  tools, its body when asked for, its laws verbatim at home then held as codes
  by the pending block. The segment is addressable (`@n`) like any fused
  output's.

#### Lifetime and repeated mounts

A `proc:` aboard is ignored: the flow stays the frames'. The build warns on
`plans/` documents carrying one.

A mount lives ONE exchange: the rewind that opens the next one sweeps every
mount.

An address already mounted is not mounted again: its laws and offers stand,
and the slot keeps its one entry. So:

- a mount that names the chain already there plus a deeper document adds that
  document alone;
- naming it again with its body asked serves that body once more; nothing when
  nothing is asked.

Several mounts in one passage build one view.

#### `replaces`

An entry may name what it REPLACES: `"replaces": [<address>, ...]`. Before
anything enters, the entries of the passage at those addresses leave the
slot, their laws, offers and matter with them, so a code they carried no
longer collides. This is traced `released` with `by: replaces`.

An address not in the view does nothing. An entry a frame holds from its
`initialize` stays with its frame.

`pp-plan mount` names under it the other born nodes of the plan, so a batch
mounted after its sibling takes the sibling out of the view.

#### Refusals and a gone document

| Refusal | When |
|---|---|
| `mount-missing` | see the address |
| `mount-collision` | a NEW document brings a constraint code already in force |
| `mount-invalid` | an entry that is not `{"doc": …}`, an unknown scope, a `replaces` that is not a list of addresses |

A standing mount whose document disappears mid-run (a file removed, a package
switched out from under it) mounts nothing from then on and says so. This is
the engine's own `mount-gone`, a diagnostic of level note
(`mount-gone · note · <address> -- gone`), once per address and per run,
never from a view.

#### A script mounts too

A SCRIPT played by `-s` can mount too: a `::mount <json>` line on its output
(the `::push` channel) is harvested on a clean run. The script derives the
chain, pp hosts it: one gesture.

#### The host mounts too

**The host mounts too.** A document that HOOKs a socket can name what mounts
there itself, in its front matter or in an overlay of it:

```
---
name: TURN
mounts:
  turn.begin: HOUSE.md
---
```

The names follow the socket's own contributors (`mount: <socket>`), each
judged by its own `when:`, and enter exactly as they do:

- laws in force and owed at the checkpoint;
- offers;
- body (spared once proven under `proc_body_serve: once`);
- readings;
- remounted at every turn and served again after `-compacted`.

A name resolves as a CALL does, so an agent mounts a proc of its house: the
house's `procs/HOUSE.md`, its laws, offers and readings shared by every agent
that writes the line, and by none that does not.

The build refuses a socket the document's proc never hooks
(`mounts-hook-unknown`) and a name found nowhere (`reference-unknown`).

Where to mount:

- `turn.begin` enters before the WORK: the laws bind while the work is done,
  the readings give its ground. A law of production is proven over the whole
  turn, so it belongs at `turn.begin`.
- `turn.end` enters after it: for a reading of the state the work left, and
  the laws that bind the closing. A reading at `turn.end` computed by a script
  needs a `§` before the socket, or the fused output computes it before the
  work.

### `./pp` (keyless)

*Description* — inspection only.

*Effect* — where the single standing run is; never advances, never opens.

## See also

- [The block, section by section](block.md) — what each output carries, the channels and the two conduction modes.
- [The language, keyword by keyword](language.md) — `OPEN`, `SERVE`, `CALL` and the other keywords the commands play.
- [The operator's console](console.md) — the operator's verbs and switching a package off.
- [When an answer misses](misses.md) — the bus, the diagnostics and what counts as a miss.
