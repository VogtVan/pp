# The block and the channels

This file covers what the engine prints at each step: the block section by section, the channel each production travels by, the form of a said production, the two conduction modes and what consumption means.

- [The block, section by section](#the-block-section-by-section)
- [Channels and the delivery](#channels-and-the-delivery)
  - [The form of a said production](#the-form-of-a-said-production)
  - [The two conduction modes](#the-two-conduction-modes)
  - [Consumption](#consumption)
- [See also](#see-also)

## The block, section by section

| Section | What it carries |
|---|---|
| the output's heading — `pp · run <key>` | The run's key and the clock: the local hour `HH:MM:SS` and `+H:MM:SS` elapsed since the run's `-new`. It comes once per output, and with every chunk of a cut one, so no piece arrives without saying which run it comes from. A second line follows it where the instance pins packages beyond its base: what the run plays, one cell each (`on`, `off`, `off (<- <dependency>)`), dependencies first. |
| the heading — the path | Which documents are in flight: ancestors bare, the ACTIVE frame carrying `{i/m}` (a range `{i-j/m}` when the output fused steps i→j), `· REPAIR n` when the last move missed, `[n]` numbering multi-scope outputs. |
| `TOOLS` | The skills this scope offers, by name. Their contracts live in the served catalog. |
| `INFORMATION — <token>` | A document read and injected by the tool, titled by the token its row wrote: path and selection as written (`design/target.md`, `PHASE.md[## Target..## Arbitrations]`, `GLOSSARY.md[1-2]`), followed by ` @<name>` when it was read from a material other than the repository (see *The material of a reading* in [the language](language.md)). A CALLed body is titled by its document's name. The pending step's own body is promoted `NEXT INSTRUCTION CONTEXT`. A cut reading continues untitled. |
| `CONSTRAINTS` | The laws in force: full text once per output, codes after. A new scope says its delta verbatim. |
| `DEVIATION` | When the last move missed: the miss, named. |
| `DIAGNOSTIC` | What the engine itself found wrong with the conduction, one line per diagnostic: `<signal> · <level> · <fact> -- <way out>`. See [The bus and the diagnostics](misses.md#the-bus-and-the-diagnostics). |
| `OPTIONS` | The closed set a `PICK` chooses from. |
| `NEXT INSTRUCTION CONTEXT — the ask` | Under the WORK of the frame that opens an exchange, at every exchange. The principal's last message is the context of that step: say the productions above, then play the call. The message itself is never copied there. |
| `INSTRUCTION` | The instruction lines, one step each, suffixed `form => channel  (DOCUMENT)`, the name of the step's document last. Same-frame steps with nothing between them collapse under ONE title. A step without `output:` yields `any`. |
| the closing | `CONTINUE` / `AWAIT` (the arrow mark, once, right above the exact command). |

## Channels and the delivery

The channel is **derived, never declared**:

- a consumed production travels by its format's mode: `tool` inline, `tool
  (heredoc)` on stdin;
- a PICK rides the command;
- a proof checkpoint pipes its proof;
- an unconsumed production is said to the principal at its own step, `=>
  response`, whatever stands ahead.

The end of the passage delivers nothing. There is no drawer of drafts
(`ephemeral`).

`response` is what the principal receives. The engine names the channel; the
base says where it lands. Under the kit, it lands with the operator reading the
agent's words. The word lives at one place of the engine (`language.RESPONSE`),
read by the derived channel and the soft catch.

### The form of a said production

#### A form, never a rule of the channel

What a said production opens on is a FORM, never a rule of the channel. The
`formats:` dialect has three modes, one per transport:

| Mode | Transport |
|---|---|
| `inline` | on the call |
| `stdin` | piped |
| `words` | written in the agent's words — the text it writes outside any tool call |

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

A form of the tool (`table`, `free`, `any`…) said to the principal travels
inside that form. A form declared at the mode `words` (a team's act,
`team-act`) has no wrapper.

An instance redefines the opening by redeclaring `said` in its `FORMATS.md` or
in an overlay of `TURN`. A base that declares none (the bench's witness) leaves
a said production to the form the step names, and `output: said` is then
unknown like any name.

#### The `words` channel

The channel of a said production is `=> words`. One word, `words`, names the
channel and the mode alike. The agent has two destinations, its words and the
tool, and the standing orders define both.

- `chat`, the mode's former name, refuses `chat-gone` by its name at the build.
- `response` is the glossary's word for everything the agent produces during
  its turn, never a channel nor a mode.

No document declares a channel: it is derived by the flow. `output.md` carries
the forms alone; the standing orders say the channels.

The engine renders no header itself and judges nothing of the form. The heading
of the block carries the name; the text is the agent's.

In the relayed channel (a run its principal conducts), each production is thus
ONE message of the launch that produced it, never repeated at the end of the
passage. The readers of the response (the house, the teams, the post) still
keep the LAST text of the final launch until their own batches read the words
of every step.

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

### The two conduction modes

A run is conducted either:

- by the LLM, which calls pp to advance — today's mode; or
- by its PRINCIPAL, whose launcher opens it under
  `PP_CONDUCTED_BY_PRINCIPAL=true` (see [`./pp -new`](agent-face.md)), serves
  each output in the prompt and makes pp advance.

The engine knows no turn. It knows the mode, and the rules below hold in the
principal's mode.

#### No meta-conduction

The agent never learns that someone else advances the run.

An output that owes the tool nothing — a pending FREE step, a `§`, the end of
the passage — has **no closing line at all**: no CONTINUE, and AWAIT does not
exist in this mode. A chunk before the last closes on `▶ MORE` and the fact
that the reading continues.

The FOOT of every output is decided at ONE site, `blocks.closing(awaited, channel)`. It is decided from two things:

- what the stack awaits after the output: a value, a response, a message, a
  reading that continues;
- the channel it reaches the agent by: the result of its own call, or the
  prompt of a launch.

The mode chooses the channel, never the foot.

An output that asks the tool for a VALUE — a proof, a field, a choice, a
production a consumer takes — closes on `▶ CONTINUE` and the call to type, in
both modes:

- for a form piped: `./pp <key> - <<'EOF'`, the form's name (`<proof>`,
  `<json>`…), `EOF`;
- for a form on the call: `./pp <key> <options>` or `./pp <key> "<line>"`.

The INSTRUCTION line says `=> tool`; the closing says how. The standing orders
the agent receives in this mode (`system.common.md`) carry the common card
alone: no AWAIT, no bare call.

#### The last `=> words` step of an output stays pending

A production said in the words is the agent's own text, and its term is the
principal's call. So the last FREE step an output batched is handed back to
PENDING (`asked`, not done; traced `pending`). That is the step nothing follows
in that output: a `§`, the fusion cap, a HOOK that would inject a step behind
it, a checkpoint of another segment, the end of the passage.

The output closes on it with a bare CONTINUE. The steps batched before it stay
batched (the boot's CAPABILITIES table under the TURN's WORK).

A checkpoint owed right behind it, with nothing to inject before, keeps it
batched. The proof is asked in the same output, one launch, as the LLM's mode
asks it.

Whatever the agent plays during its message — a mount, a gesture, a door, a
view — acts on THAT step: `-peek` renders `TURN{2/4}`, a `-s` stacks on it.

The principal's bare call resolves the step (`submit("")`, as a bare call
resolves an asked WORK in the LLM's mode). It goes on in the same call, through
the `§` the next document opens on (THREADS): one output, no order block of its
own.

A FREE step last of the root is never fused with the end of the passage in this
mode: the AWAIT comes at the principal's next call, launched on nothing. In the
LLM's mode the step is batched as before
(`tests/engine/execution/principal-hold.py`, case n).

#### `conduction: hybrid`

`conduction:` is a SETTINGS key, `strict` by default. Under `hybrid`, the
output whose closing asks the agent such a VALUE is not held. It comes back in
the agent's tool result, its command with it, cut under the HOST's cap
(`max_harness_tool_output`, never the principal's floor: it lands in a tool
result).

The rest is served by the agent's bare keyed call, chunk by chunk (the
`viewing` slot a view uses; the readings it staged are proven when the last
chunk leaves). The trace says `inline` with the act that rendered it, and
`-stats` counts them (`N inline` on the period's line, `inline` in the json).

An output that MOVES the run on — one that owes no call, a FREE step said in
the words — is held as under `strict`. A door opened by `-s` has no case of its
own: its first block follows the rule.

The invariant holds in both values: the agent's bare call never advances the
run.

Measured on the bench's laps witness (three laps, a proof each): 2 launches of
the harness under `hybrid` where `strict` takes 6
(`tests/engine/execution/principal-mode.py`,
`packages/agent/tests/engine/agent-exchange-record.py`).

#### The prompt cap and the chunks

An output over the cap comes in chunks, under the cap the LAUNCHER names on its
marked call: `PP_PROMPT_CAP`, in characters, beside the mark. The launcher
knows the model and its window; the engine names neither. The `agent` package
names it from what the adapter of the run's provider declares: `CAPS` by the
model's name and `CAP` for any (see [the adapters
README](../../adapters/README.md)).

- A value that is not a positive number refuses `prompt-cap-invalid`.
- The variable is inert in the LLM's mode and on an unmarked call.

Without it, a FLOOR holds: the larger of `max_harness_tool_output` and 200 000
(`settings.PRINCIPAL_CAP`, the one rule `settings.served_cap`). The output
reaches the harness on its standard input, never as a tool output, and one
output is one launch.

An instance cut for its host (VSCode at 20 000) therefore serves its
principal's runs whole up to the floor, and no setting lowers it; a higher
setting holds.

A chunk before the last closes on `▶ MORE` and the fact `(a reading continues:
n characters in m more chunk(s))`, with no call and no instruction. The
principal's next bare call serves the rest.

#### Facts, not orders

The engine's own lines say a fact and give no order. The soft catches, a
renewed run, a call bounced while a reading continues all say what happened.
What the agent does then is the standing orders' to say.

`-hook` serves the pending block in both modes (every block but an END).

The card says it in one sentence under *Closings*. What tells the agent to call
pp lives in the `SYSTEM.CONDUCT.md` of each section, compiled into the standing
orders of a run the LLM conducts alone. A run its principal conducts is served
`system.common.md`, which carries none of it (see [The marble, in
layers](instance.md#the-marble-in-layers)).

#### Whose call it is

In such a run the launcher carries the same mark,
`PP_CONDUCTED_BY_PRINCIPAL=true`, on EACH of its own keyed calls — never in the
environment of the CLI it launches. A marked call is the principal's, any other
the agent's. A CLI that filters its shell's environment cannot make the agent
pass for the principal.

The console alone reads the mark, and only in a run its principal conducts
(`context.by_principal`), and hands the answer to the facade. An odd value
refuses `conducted-by-invalid`.

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

The served text goes to whoever conducts the run: the tool return in the LLM's
mode, the next prompt in the principal's. The answer goes to the caller in both
modes.

ONE seam decides, never the call site:
`Conductor.delivered(block, by_principal, lead, act, view)` is the one way a
block leaves the engine on a keyed call, and no line of the console prints a
block itself.

#### The calls, case by case

- **The agent's call that serves** plays its act at once, exactly as in the
  LLM's mode: a value judged by `submit` (traced `answer`, checked, repaired in
  place or by reopening, given), a mount written, a door pushed.
  - The block it renders is HELD at the run (`held` in the slot: the same
    pieces a cut keeps, and the `act` that held it; traced `held` with that
    `act`).
  - The tool return carries what the act answers (a script's own text) and one
    line naming the act and nothing more: `pp: value judged`, `pp: mounted`,
    `pp: opened`, `pp: re-served`, `pp: reopened`. Where the output comes is
    the standing orders' to say, once.
  - A second hold in the SAME call (a script's second `::mount`) joins the
    first.

- **The agent's call that only SHOWS** is answered at once, in both modes:
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
  - Nothing is held, nothing traced: a view writes no state of the run.

- **The agent's bare call** serves the rest of a view when one waits. With none
  it refuses `principal-advances` (« call already done »): nothing played, a
  chunk of the principal's waiting included.

- **One output is held at a time.**
  - A call of the agent that MOVES the run while one is held — a value, a door,
    a `-mount`, a `-compacted` — bounces: `pp: not played -- call already
    done`, rc 0, nothing played, the slot byte-identical. The agent has not
    read the block it would act upon.
  - A call that moves nothing — `-peek`, a switch, a name not offered, a script
    with its arguments — PLAYS: the view comes back in the tool return, the
    script runs, and its `::mount` JOINS the held output (its matter after the
    held one's).
  - The same rule holds while a chunk of a reading waits, in both modes: a view
    or a gesture plays over it; a text that would need the run's rest slot is
    clipped and its clip said by a fact; the waiting reading stays untouched.

- **The principal's bare call** serves the held output when one stands, cut
  under the cap as if it left then, the rest served by its next bare calls; the
  slot forgets it.
  - With no held output it advances as today (a value due and absent: the
    empty-answer repair).
  - On a parked run it carries the principal's message.
  - Each is traced `advance` (`held: true|false`, `prompt`).

- **A marked call carrying a text over a held output** refuses `output-held`
  (« an answer waits its principal's bare call -- it is served first »).

- **`-stats`** counts the held outputs and the principal's advances per closed
  exchange, and says them on the period's line where any happened (`N held, N
  principal advance(s)`). `-json` carries `held`, `held_by` (the held outputs
  by act) and `advances`.

A script that wants to SERVE a reading goes through `::mount`: what it prints
itself is its answer.

The agent reads none of the mark. No text it is served names it, and no text it
is served says who advances the run. The lines that answer its calls say a
fact — `pp: value judged`, `pp: not played -- call already done` — and nothing
more.

### Consumption

Consumption means **use**, not transport. Three consumers exist:

- a callee declaring `input:` (the pipeline): a CALL that names it, or a
  successor under `next:` that declares it;
- a PICK (the election);
- **the engine itself**: the proof judge consumes a checkpoint's proof, and a
  document's declared `sink:` consumes its projection.

Engine-consumed productions derive `=> tool` through the same consumption rule.
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
