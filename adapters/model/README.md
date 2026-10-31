# The `model` adapter -- the LLM modelled

*Its data: [`semantics.py`](semantics.py) -- the acts, the forms, the readings, the answers, the
strategies, and the closed list of the ZONES of the conduction the campaign's census counts.*

`model` is a provider like `claude` or `codex`, with one difference: its harness is a script of the
product, [`harness.py`](harness.py), and not a model. It reads a block of pp by its STRUCTURE and the
engine's constants, decides by the DATA of the conduction model, and acts exactly as the model says a
conforming agent acts. It is deterministic, has no content, opens no network, and costs 0.

## What it is for

The bench of the conduction. A real model is slow, costs money and answers differently twice: with
`model`, the campaign of the conduction sector (`tests/conduction/`) plays every root on the three channels at every
pass of `./pp -test`, and what it measures is the CONDUCTION -- where the engine's text leaves the agent
without an act (a `hole`), how many launches an exchange takes, what a miss costs in repairs. A real
model is played on the operator's word, and compared.

## How a launch plays

1. pp-agent composes the launch through the engine's face (`conductor.adapters.launch("model", …)`):
   the interpreter on `harness.py`, `--variant <model>` from the policy's `model` key, `--session <id>`
   on a resume, the prompt whole on stdin, an empty environment -- the model reads no marble and no
   wiring, it reads the block.
2. The harness isolates the LAST output of pp in the prompt and reads it: the INSTRUCTION lines
   (keyword, form, codes, channel, document), the OPTIONS, the closing (`▶ CONTINUE`, `▶ AWAIT`) and
   the call under it -- a template naming the form due, the bare keyed call, the call that carries a
   message --, the facts under the foot, and where the INSTRUCTION lines stand (the last segment, an
   earlier one, none). When no output stands it reads the engine's own line that answered a call
   (`pp: value judged`, a bounce, a refusal, a gesture).
3. The data give the CANDIDATE forms (`semantics.READINGS`, by the traits of the text: the channel it
   came on, the closing, the call, a fact, where the lines stand) and, per form and channel, the act
   (`semantics.FORMS`; `semantics.ANSWERS` for a line): one form, its act -- say the `=> words`
   productions as `words`, type the call with the production of the form due, hand back, stop on a
   refusal that stops the conduction; several forms that agree on the act, that act and the thought
   `ambiguous`; several that disagree, no act, the thought `undecided` and the hand given back without
   a word -- the harness chooses no form among several; none, a `hole`: said as a `thinking` event,
   nothing guessed. A step whose production this launch said is not said again when a view or a mount
   brings it back.
4. The call is typed by a subprocess of the console (`./pp <key> …`) and said as a `tool` event with its
   `tool-result`; what the console answered feeds the loop while the sequel comes by the tool. When it
   comes at the next turn, the launch ends on its `result` line: `cost_usd` 0, `denials` [], the
   session, the variant, whether it missed, how many calls it typed.
5. Without an output in the prompt (the bare channel: the editor's extension, `agent chat` under
   `conduct off`), the model opens the run itself by `./pp -new`, as the door of its workspace tells
   it to, and conducts it to the end of the passage.

## The variants

The policy's `model` key names the VARIANT of the judgment -- `conform` by default. Every other
variant makes exactly ONE miss, the one its name says, at the first place where it is possible, then
conforms for the rest of its session (a file under the system's temp dir remembers the miss, as a
model remembers its own conversation):

| variant | the miss | what the engine does |
|---|---|---|
| `wrong-form` | a production of another form where a value is due | a repair |
| `wrong-channel` | a `=> words` production handed to the tool | the soft catch: a block with a deviation, no repair counted |
| `missing-code` | one code left out of a proof | a repair of the proof |
| `bare-call` | the bare call where a value is due | `principal-advances` when the house conducts, then the house's advance repairs the empty answer; the empty-answer repair at once on the bare channel |
| `empty` | an empty production | a repair |

## The intention

What a real model would decide of itself on reading its principal's message is said to the harness
by `PP_MODEL_INTENT` (a JSON list of one-key acts, the root's `model:` at the campaign's manifest):
`open` a door the step offers, `pick` an option, answer a `field`, `echo` the matter an INFORMATION
section serves; and the acts of the ordinary situations -- `gesture` (`./pp <key> <args>` typed once
the step's productions are said and its door answered: a script, a mount, a name the step does not
offer), `bare` (the bare call where a value is due), `stray` (a `=> words` production handed to
the tool), `bounce` (the last call typed again once a held line answered it: the console answers `not
played`), `persist` (the named miss at EVERY place where it is possible, up to the repair bound). Each
act but `echo` and `persist` plays once and what is left is remembered for the session. Over a held
output a gesture plays only when it moves nothing (a view, a script), as the standing orders say; one
that moves the run (a door, a space, a mount, a re-serve) waits for the next turn.

## What it does not do

It wires nothing (`-install` never names it; a launch does, by `--provider model`); it spells no budget,
no effort, no permission regime (`policy-unsupported`); it reads neither `.pp/.sys`, nor the run's log,
nor a record, nor the marble: it knows of the run what the prompt and its own calls tell it -- the ORACLE
of the sheet reads the run's state, the harness never does. It produces no
content and no judgment: a `line` is `a line of the model`, a proof is `ok` on every code with the
evidence `the model: no rendering, the proof is modelled`, a choice is the first value of OPTIONS.
