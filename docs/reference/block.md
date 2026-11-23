# The block and the channels

This file covers what the engine prints at each step: the block section by section, the channel each production travels by, the form of a said production, the conduction at the prompt and what consumption means.

- [The block, section by section](#the-block-section-by-section)
- [Channels and the delivery](#channels-and-the-delivery)
  - [The form of a said production](#the-form-of-a-said-production)
  - [The conduction at the prompt](#the-conduction-at-the-prompt)
  - [Consumption](#consumption)
- [See also](#see-also)

## The block, section by section

The sections come in the order of this table, which is the engine's own list (`language.BLOCK_SECTIONS`, then `language.STEP_SECTIONS`). The sections of the block come once. Then each step comes in its turn, as a GROUP: what the step alone reads, its context, its `OPTIONS`, its line.

| Section | What it carries |
|---|---|
| the output's heading — `pp · run <key>` | The run's key and the clock: the local hour `HH:MM:SS` and `+H:MM:SS` elapsed since the run's `-new`. It comes once per output, and with every chunk of a cut one, so no piece arrives without saying which run it comes from. A second line follows it where the instance pins packages beyond its base: what the run plays, one cell each (`on`, `off`, `off (<- <dependency>)`), dependencies first. |
| the heading — the path | The heading of a SEGMENT: which documents are in flight at its first step, ancestors bare, the ACTIVE frame carrying `{i/m}` (a range `{i-j/m}` over the steps of that frame the segment carries), `· REPAIR n` when the last move missed, `[n]` numbering the segments of an output that carries several. A segment holds the steps of one SCOPE: the laws in force are the same for all of them, whatever their document. A step under other laws opens the next segment; a step of another document that joins a segment is said by its line, which names its document. Under `tools_in_scope: true` -- the effort `full` presets it; `false` otherwise -- the offers are part of the scope: a difference of offers opens a segment too. A mounted document opens none, and none opens when the mounts of a passage leave at its end: the closing of the passage stays in the segment of the steps said under them. |
| `INFORMATION — <token>` | A document read and injected by the tool, titled by the token its row wrote: path and selection as written (`design/target.md`, `PHASE.md[## Target..## Arbitrations]`, `GLOSSARY.md[1-2]`), followed by ` @<name>` when it was read from a material other than the repository (see *The material of a reading* in [the language](language.md)). A CALLed body is titled by its document's name. A reading stands at the head of its segment, whichever step of the segment brings it. Two readings are proper to a step and stand in its group, above its context: the element of a lap (`field`, or the name of the door's token) and the production a document opens on (`input`). A cut reading continues untitled. |
| `TOOLS` | The skills the steps of the segment offer, by name, each once: the union of their offers. The engine accepts at the pending step any name the segment shows. Their contracts live in the served catalog. |
| `CONSTRAINTS` | The laws in force for every step of the segment, said once: full text once per output, codes after. A new segment says its delta verbatim. A heading a repair opens under the laws of the segment above says neither `TOOLS` nor `CONSTRAINTS` again. |
| `DEVIATION` | When the last move missed: the miss, named. |
| `DIAGNOSTIC` | What the engine itself found wrong with the conduction, one line per diagnostic: `<signal> · <level> · <fact> -- <way out>`. See [The bus and the diagnostics](misses.md#the-bus-and-the-diagnostics). |
| `INSTRUCTION CONTEXT — <title>` | What the step whose line follows works from. `<NAME>`: the body of the step's own document. `field` and `next`: the brief of an `INFER field` and of a `PICK next`. `the ask`: under the WORK of the frame that opens an exchange, at every exchange, the principal's last message is the context of that step; the message itself is never copied there. |
| `OPTIONS` | The closed set a `PICK` chooses from, between the context of its step and its line. |
| `INSTRUCTION` | The instruction lines, one step each, suffixed `form => channel  (DOCUMENT)`, the name of the step's document last. A step that reads something of its own -- a context, `OPTIONS`, a reading proper to it -- opens a title of its own; steps with nothing between them follow one another under ONE title. A step without `output:` yields `any`. |
| the closing | `CONTINUE` / `AWAIT` / `MORE` (the arrow mark, once), right above the exact command when one is owed; the `AWAIT` and the `MORE` of a prompt stand alone. |

## Channels and the delivery

The channel is **derived, never declared**:

- a consumed production travels by its format's mode: `tool` for an inline form, on
  the call; `tool_heredoc` for every other, piped by a heredoc;
- a PICK rides the command;
- a proof checkpoint pipes its proof;
- an unconsumed production goes to the principal at its own step: `=> terminal`, handed by its
  print call (`./pp <key> -print <DOCUMENT> -`) and kept at the trace as handed.

The end of the passage delivers nothing. There is no drawer of drafts
(`ephemeral`).

A production nobody takes is written to the principal. The engine names its
channel `terminal` (`language.TERMINAL`), read by the derived channel and the
soft catch.

### The form of a said production

#### A form, never a rule of the channel

What a said production opens on is a FORM, never a rule of the channel. The
`formats:` dialect has three modes, one per transport:

| Mode | Transport |
|---|---|
| `inline` | on the call |
| `stdin` | piped |
| `words` | said to the principal, standing alone — on the channel `terminal` |

A form at the mode `words` stands alone there: its definition says what it
opens on and what it carries. It enters the enumeration like any form:
`output:` names it, `format-doubled` applies within a level, and the nearest
level wins. The reading `output.md` says it under § The OUTPUT formats with its
mode.

#### The kit's `said` form

The kit declares the generic one on its `TURN`: `said  words  …`. The
production opens on three lines: `---`, the name of the document on the
INSTRUCTION line, `---`. Then comes the production itself, in the form the step
names (free prose when `said` is the form named). After a `CONTINUE` that owes
no production, nothing is said.

A form of the tool (`table`, `free`, `any`…) printed for the principal travels
inside that form, and is judged on it as a value of that form is. A form declared at the mode `words` (a team's act,
`team-act`) has no wrapper.

An instance redefines the opening by redeclaring `said` in its `FORMATS.md` or
in an overlay of `TURN`. A base that declares none (the bench's witness) leaves
a said production to the form the step names, and `output: said` is then
unknown like any name.

#### The channels of a said production

A said production goes `=> terminal`: handed to pp by its print call (`./pp <key>
-print <DOCUMENT> -`, the production piped) while the work goes on, and kept for the
principal. A text the agent writes between two calls is no production, and neither is
the last message of a launch: pp never reads it. Everything the principal reads goes by a
print call. `words` names the mode alone: what an author writes on a `formats:` line.
`chat`, the mode's former name, refuses `chat-gone` by its name at the build.

No document declares a channel: it is derived by the flow. `output.md` lists
each form with its channel -- `terminal · response` for a form at the mode
`words`; the standing orders say what each channel asks.

The engine renders no header itself and judges nothing of the form. The heading
of the block carries the name; the text is the agent's.

Each production is thus ONE message of the launch that produced it, never repeated at
the end of the passage. The house composes the response of an exchange from the
productions pp took and the last message of each launch, in their order, a bare `...`
left out (`pp-agent`, `rules/passage.composed`).

#### The engine's imposed forms

The engine's IMPOSED forms keep the engine's mode:

| Form | Used by |
|---|---|
| `options` | a PICK |
| `proof` | a PROVE |
| `field` | the field of a described door |
| `list` | the step a PICK elects from |

A `formats:` line may give one of them its own definition at that mode; another
mode refuses `format-mode-fixed` at the build.

`field` and `list` are one entry of the engine's table (`language.LISTS`): a
JSON array of strings or numbers, each once, none empty, `FIELD_MAX` at most,
judged by `scalars_form`. `list` asks one element at least.

### The conduction at the prompt

Every run is conducted by its PRINCIPAL: a launcher (`pp-agent`, see
[`./pp -new`](agent-face.md)) opens it, serves each output at the agent's
prompt and makes pp advance; the agent hands its productions back by its own
`./pp <key> …` calls.

The engine knows no turn. The rules below hold for every run.

#### No meta-conduction

The agent never learns that someone else advances the run.

An output that leaves a step to the agent — a pending FREE step, a `§` — has
**no closing line at all**: no CONTINUE. The end of the passage closes on
`▶ AWAIT` with no call under it: the launcher carries the next message. A
chunk before the last closes on `▶ MORE` and the fact that the reading
continues. So a prompt that has no closing always carries a step that stands:
a production to say, or a value its line hands to pp.

The FOOT of every output is decided at ONE site, `blocks.closing(awaited, channel)`. It is decided from two things:

- what the stack awaits after the output: a value, a production the agent
  says, a message, a reading that continues;
- the channel it reaches the agent by: the result of its own call, or the
  prompt of a launch.

An output that asks pp for a VALUE — a proof, a field, a choice, a production a
consumer takes — closes on no line, on either channel. The INSTRUCTION line names the
channel the value is handed by:

- `=> tool_heredoc` for a form piped: `./pp <key> - <<'EOF'`, the production, `EOF`;
- `=> tool` for a form on the call: `./pp <key> <value>`.

The agent types the call itself, with the key of the output's heading. The standing
orders (`system/SYSTEM.md`) and the card (`refs/PP.md`) say the rest: `▶ AWAIT` with
no call under it where a passage is over, and the bare call only to read the rest of a
cut output.

#### The steps said on `terminal` are due until their print

A step said on `=> terminal` is DUE from the moment its output is rendered until the print call that
answers it (`-print <DOCUMENT> -`, the production piped). The debt lives at the run's state, one
entry per step (`persistence.prints_of`), traced `print-due`; it survives a gesture and the exit of
the step's frame. A print accepted is traced `answer` (channel `terminal`, the document named, the
text as handed); a print that is empty or breaks its form is refused at the return of the call and
stays due; at `work_repairs_allowed` refusals the entry leaves without a capture (`print-waived`)
and the run goes on. A door opened from a step due stands for its production: the entry leaves,
traced `print-by-door`.

While a print is due, a value, a proof, the agent's bare call or the principal's call that would
move the run comes back with a DEVIATION naming each print due: nothing played, no repair counted.
The principal's next message is never sent back: on a parked run it opens the passage, and the
prints left due are lifted (`print-waived`, one each).

#### The last said step of an output stays pending

The last FREE step of the current frame that an output closes on is handed back to PENDING
(`asked`, traced `pending`); its line stays `=> terminal`, due until its print like any other.
A HOOK does not close the output on its WORK: the contributors and the
proof follow in the same output. An order block that closes a stretch (`§`, the fusion cap, a proof
under another document's step) takes no step back: the steps said stay due, and the last print
moves the run on -- the next block comes in the call's result when it asks a value, held otherwise
(`tests/engine/execution/print-owed.py`, `print-catch.py`).

Whatever the agent plays during its message — a mount, a gesture, a door, a
view — acts on THAT step: `-peek` renders `TURN{2/4}`, a `-s` stacks on it.

The principal's bare call resolves the step (`submit("")`). It goes on in the same call, through
the `§` the next document opens on (THREADS): one output, no order block of its
own.

A FREE step last of the root is never fused with the end of the passage: the AWAIT
comes at the principal's next call, launched on nothing
(`tests/engine/execution/principal-hold.py`).

#### A value asked comes back in the tool result

The output whose step asks the agent a VALUE
(a proof, a field, a choice) is not held. It comes back in the agent's tool
result, cut under the HOST's cap (`max_harness_tool_output`, never the
principal's floor: it lands in a tool result). No setting chooses it.

The rest is served by the agent's bare keyed call, chunk by chunk (the
`viewing` slot a view uses; the readings it staged are proven when the last
chunk leaves). The trace says `inline` with the act that rendered it, and
`-stats` counts them (`N inline` on the period's line, `inline` in the json).

An output that MOVES the run on — one that owes no call, a FREE step that is
the launch's last message — is held for the principal. A door opened by `-s`
has no case of its own: its first block follows the rule.

The agent's bare call never advances the run.

Measured on the bench's laps witness (three laps, a proof each): 2 launches of
the harness for the whole exchange
(`tests/engine/execution/principal-mode.py`,
`packages/agent/tests/engine/agent-exchange-record.py`).

#### The prompt cap and the chunks

An output over the cap comes in chunks, under the cap the LAUNCHER names on its
own call: `PP_PROMPT_CAP`, in characters. The launcher
knows the model and its window; the engine names neither. The `agent` package
names it from what the adapter of the run's provider declares: `CAPS` by the
model's name and `CAP` for any (see [the adapters
README](../../adapters/README.md)).

- A value that is not a positive number refuses `prompt-cap-invalid`.
- The variable is inert on the agent's call.

Without it, a FLOOR holds: the larger of `max_harness_tool_output` and 200 000
(`settings.PRINCIPAL_CAP`, the one rule `settings.served_cap`). The output
reaches the harness on its standard input, never as a tool output, and one
output is one launch.

An instance cut for its host (VSCode at 20 000) therefore serves its
principal's runs whole up to the floor, and no setting lowers it; a higher
setting holds.

The cap is always held. An output is cut as a run of pieces, in their order:

- its matter first -- what stands before its first step: the segments that ask nothing, then the
  heading, the readings, the tools and the laws of the first segment that asks a step --, at a
  section boundary when one fits;
- then every piece from that step on: the GROUP of each step -- what it reads, its `OPTIONS`, its
  line --, in whatever segment the step stands, and, between two steps of different segments, the
  head of the later segment. When they all fit under the cap with the last piece of the matter,
  they follow it. When they do not, the cut falls between two pieces: a group stays in one chunk;
- a piece larger than the cap by itself has what it reads cut like any reading, and its `OPTIONS`
  and its line follow the last piece of it.

A chunk before the last closes on the fact `(a reading continues: n characters in m more
chunk(s))`: at the prompt under `▶ MORE`, with no call; by the tool under `▶ CONTINUE` and
the bare call. Such a chunk may
carry the line of a step: nothing is due for that step before the output is whole. The foot of
the output comes with its last chunk. The principal's next bare call serves the rest.

#### Facts, not orders

The engine's own lines say a fact and give no order. The soft catches, a
renewed run, a call bounced while a reading continues all say what happened.
What the agent does then is the standing orders' to say.

`-hook` serves the pending block (every block but an END).

The card says it in one sentence under *Closings*. Every run is served the same
standing orders and the same card (see [The marble, in
layers](instance.md#the-marble-in-layers)).

#### Whose call it is

The launcher names the run it conducts to the CLI it launches:
`PP_CONDUCTED_RUN=<key>`, in that CLI's environment, so every call the agent
makes carries it. A keyed call on that run is the agent's; any other call is
the principal's.

The console alone reads it (`context.agents`), and hands the answer to the
facade.

The dynamics are those of every run: a value or an act handed by a tool call,
one judge, a repair. Only the delivery of what the engine serves changes
channel.

#### Two texts leave a call

What the engine SERVES is everything it renders of a block:

- the step after a value;
- a REPAIR;
- the view of a mount (`-mount`, a script's `::mount`, the manual of a script
  called bare);
- a routed door or a bare contract;
- the re-serve of `-compacted`;
- the block after a switch (`-disable`, `-enable`);
- a `-peek`;
- the block an offer out of the step brings back.

What a call ANSWERS is what a script prints of its act, a bounce line, a
refusal — and what only SHOWS: a `-peek`, the manual of a script called bare,
the block an offer out of the step brings back, the block after a switch. None
of them moves what the principal relays.

The served text goes to the principal, who relays it at the next prompt. The
answer goes to the caller.

ONE seam decides, never the call site:
`Conductor.delivered(block, agents, lead, act, view, gesture)` is the one way a
block leaves the engine on a keyed call, and no line of the console prints a
block itself.

#### The calls, case by case

- **The agent's call that serves** plays its act at once: a value judged by
  `submit` (traced `answer`, checked, repaired in place or by reopening, given),
  a mount written, a door pushed.
  - The block it renders is HELD at the run (`held` in the slot: the same
    pieces a cut keeps, and the `act` that held it; traced `held` with that
    `act`).
  - The tool return carries what the act answers (a script's own text) and one
    line naming the act and what is due: `pp: value judged — hand back`,
    `pp: mounted — hand back`, `pp: opened — hand back`, `pp: closed — hand back`,
    `pp: re-served — hand back`, `pp: reopened — hand back`. Where the output
    comes is the standing orders' to say, once.
  - A second hold -- a script's second `::mount` in the SAME call, a view a
    gesture mounts over an output that waits -- joins the first, and a step is
    said ONCE. When the block rendered again carries the step the output that
    waited closed on, it takes that step's place: its heading, its offers and
    its laws as they are now, what the step read then with what it reads now,
    its line once. What stood before that step stays. A block of another step
    follows the output that waited, whose closing lines leave with its foot.

- **The principal's gesture between two exchanges** -- `-open` and `-close` on
  its own call -- moves the run to a block the AGENT owes, so it is held like the
  agent's own: `held` in the slot with its `act`, the line `pp: opened — your bare
  call serves it` or `pp: closed — your bare call serves it` printed, the block
  served whole by the principal's bare call. A
  launcher that opens a space and then launches an exchange without a message
  hands the agent the space's first output, its fused segments included.

- **The agent's call that only SHOWS** is answered at once:
  `-peek`; the manual of a script called bare (its mount written, proven, in
  the ledger, as ever — its block alone comes back instead of waiting); an
  offer not at this step (exit 2 kept, the DEVIATION in the tool return); a
  switch (its fact and the block).
  - The text is cut under the HOST's cap — the instance's
    `max_harness_tool_output`, never the principal's floor: it lands in a tool
    result, not on the harness's stdin.
  - The rest waits at the slot (`viewing`) for the agent's bare keyed call
    alone, chunk by chunk, the closing of each chunk saying so. Any other act of
    either caller forgets it.
  - Nothing is held, nothing traced. A `-peek` writes one thing: the offer map
    keeps the segment it shows, so the `@<n>` the agent reads on the view is
    the one the router judges, and an earlier segment's refuses `address-stale`.

- **The agent's bare call** serves the rest of a view when one waits. With none
  it refuses `principal-advances` (`pp: REFUSED — principal-advances — call
  already done`, then `pp: nothing was played`), a chunk of the principal's
  waiting included.

- **One output is held at a time.**
  - A call of the agent that MOVES the run while one is held — a value, a door,
    a `-mount`, a `-compacted` — bounces: `pp: not played — hand back`, rc 0,
    nothing played, the slot byte-identical. The agent has not
    read the block it would act upon.
  - A call that moves nothing — `-peek`, a switch, a name not offered, a script
    with its arguments — PLAYS: the view comes back in the tool return, the
    script runs, and its `::mount` JOINS the held output: the block it renders
    takes the place of the step that output closed on, said once, with the laws
    now in force.
  - The same rule holds while a chunk of a reading waits: a view
    or a gesture plays over it; a text that would need the run's rest slot is
    clipped and its clip said by a fact; the waiting reading stays untouched.

- **The principal's bare call** serves the held output when one stands, cut
  under the cap as if it left then, the rest served by its next bare calls; the
  slot forgets it.
  - With no held output it advances as today (a value due and absent: the
    empty-answer repair).
  - On a parked run it carries the principal's message.
  - Each is traced `advance` (`held: true|false`, `prompt`).

- **An exchange the principal holds OPEN** -- with `PP_HOLD_OUTPUT=true` on its
  call, an exchange plays in three moves, and nothing is rendered before the
  last.
  - **The call that carries the message** -- a `-new`, or `<key> "<message>"` --
    opens the exchange and renders no block. It prints the output's heading,
    where a launcher reads the key, and one line: `pp: exchange opened — your
    bare call plays it`, or `pp: run reopened — your bare call plays it` for a
    renewed run. A parked run opens its passage; a run
    that stands on a step opens nothing more. The stack does not advance.
  - **Each mount played next** (`-s <script> mount`) is POSED. Its entries join
    the view, their laws and their offers in force; what it serves waits at
    the run with the open output, in the order of the mounts. The call prints
    the script's own text, then one line (`pp: mounted — your bare call serves
    it`): that text answers the
    call and goes into no output. The script is named alone, with no `@<n>`:
    the engine judges the name on what the ROOT of the exchange offers -- the
    document the message feeds, read with its overlays --, never on a segment
    of an output. An address a mount already posed serves nothing more when a
    later mount names it again.
  - **The principal's bare call** plays the exchange from where the stack
    stands and renders ONE output, once: the readings that waited stand at the
    head of the first segment, before its first step, and every step carries
    the laws then in force -- the mounts' with the others. A mount adds no
    segment. The output is cut under the cap like any output. On a run that
    stands on a step, the bare call renders that step.
  - **A door or a space** named on the run while the exchange the message
    opened is not played -- `-s <proc>`, `-open <name>`, with or without `@<n>`,
    with or without the flag on the call -- is denied like a name no step
    offers: the pending block answers, exit 2, and no frame stacks before the
    bare call. On a run that stands on a step, a door is routed as anywhere.
  - Each of these calls is traced `held` (`open: true`); the release traces
    each block, then `advance` (`held: true`). A release that fails serves
    nothing and leaves the output open at the run.
  - When an output that closed already waits at the run, the message opens
    nothing and a mount under the flag joins that output as any held output
    does (`pp: mounted — your bare call serves it`). On the agent's call, the
    flag changes nothing.

- **The principal's call carrying a text over a held output** refuses `output-held`
  (`pp: REFUSED — output-held — an answer waits its principal's bare call — it is
  served first`).

- **`-stats`** counts the held outputs and the principal's advances per closed
  exchange, and says them on the period's line where any happened (`N held, N
  principal advance(s)`). `-json` carries `held`, `held_by` (the held outputs
  by act) and `advances`.

A script that wants to SERVE a reading goes through `::mount`: what it prints
itself is its answer.

No text the agent is served says who advances the run. The lines that answer
its calls say what was done and what is due — `pp: value judged — hand back`,
`pp: not played — hand back` — and nothing more.

### Consumption

Consumption means **use**, not transport. Three consumers exist:

- a callee declaring `input:` (the pipeline): a CALL that names it, or a
  successor under `next:` that declares it;
- a PICK (the election);
- **the engine itself**: the proof judge consumes a checkpoint's proof, and a
  document's declared `sink:` consumes its projection.

Engine-consumed productions derive `=> tool` or `=> tool_heredoc` through the same
consumption rule, by the mode of their form.
No document ever declares a channel.

The step a PICK elects from produces the engine's form `list`, whatever its
document's `output:` says. Its line names it and its capture judges it; a text,
a list of objects or a repeated value repairs.

A callee entered on a production it receives is served it ONCE, under
`INFORMATION — input`, at its frame's first block (a JSON value rendered as
JSON), and again by `-compacted` while the frame stands. A callee whose first
producing step is a PICK sees it as its OPTIONS alone.

#### Capture ≠ channel

The keyed call is one wire carrying two directions:

- **inbound**, the operator's message rides the resume of a parked run — and
  the opening, `-new <message>` — traced `prompt` whatever the tuning;
- **outbound**, the agent's production returns only when consumed.

What the run AWAITS is what tells the two apart. Awaiting a production, text is
a production for the pending step (a stray one bounces softly, nothing
recorded, the trace saying `stray` with the step). Awaiting a message, text is
the operator's word.

`capture_prompt` is the KIT's key, not the engine's. It only decides whether the
AWAIT closing asks for the message itself (`./pp <key> <the principal's next message>`) or closes bare. The engine reads it by name, as it reads any key a
base declares, and a base that declares none gets the bare closing.

## See also

- [The bus, the diagnostics and the misses](misses.md) — the `DIAGNOSTIC` section, deviations, repairs and refusals.
- [The agent face](agent-face.md) — the loop and every `./pp` command that serves these blocks.
- [The language](language.md) — the keywords whose steps the block renders, `PROVE` and `AWAIT` included.
- [The instance on disk](instance.md) — the standing orders and the marble, in layers.
