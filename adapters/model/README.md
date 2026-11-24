# The `model` adapter -- the LLM modelled

*Its data: [`semantics.py`](semantics.py) -- the acts, the forms, the readings, the answers, the
strategies, and the closed list of the ZONES of the conduction the campaign's census counts.*

`model` is a provider like `claude` or `codex`, with one difference: its harness is a script of the
product, [`harness.py`](harness.py), and not a model. It reads a block of pp by its STRUCTURE and the
engine's constants, decides by the DATA of the conduction model, and acts exactly as the model says a
conforming agent acts. It is deterministic, has no content, opens no network, and costs 0.

## What it is for

The bench of the conduction. A real model is slow, costs money and answers differently twice: with
`model`, the campaign of the conduction sector (`tests/conduction/`) plays every root, the house conducting, at every
pass of `./pp -test`, and what it measures is the CONDUCTION -- where the engine's text leaves the agent
without an act (a `hole`), how many launches an exchange takes, what a miss costs in repairs. A real
model is played on the operator's word, and compared.

## How a launch plays

1. pp-agent composes the launch through the engine's face (`conductor.adapters.launch("model", …)`):
   the interpreter on `harness.py`, `--variant <model>` from the policy's `model` key, `--session <id>`
   on a resume, the prompt whole on stdin, an empty environment -- the model reads no marble and no
   wiring, it reads the block.
2. The harness isolates the LAST output of pp in the prompt and reads it section by section. It
   takes the title of every section from the engine's list (`engine/conductor/core/language.py`)
   and types none itself. It reads the INSTRUCTION lines
   (keyword, form, codes, channel, document), the OPTIONS, the closing (`▶ CONTINUE`, `▶ AWAIT`) and
   the call under it -- the bare keyed call, the call that carries a message --, the facts under the
   foot, where the INSTRUCTION lines stand (the last segment, an earlier one, none), and the channel
   the last line hands a value by (`tool`, `tool_heredoc`, none). When no output stands it reads the engine's own line that answered a call
   (`pp: value judged — hand back`, a print answered, a bounce, a refusal, a gesture). A result that carries no line of pp is a
   script's own output when the call typed was a gesture (`-s <name>`, whatever the name): on an output of one segment the
   engine renders no anchor line over it. Behind any other call such a result is a `hole`.
3. The data give the CANDIDATE forms (`semantics.READINGS`, by the traits of the text: the channel it
   came on, the closing, the call, a fact, where the lines stand, the value the last line hands) and, per
   form and channel, the act
   (`semantics.FORMS`; `semantics.ANSWERS` for a line): one form, its act -- hand the `=> terminal`
   productions each by its print call (`-print <DOCUMENT> -`), type the call with the production of the form due -- on the call or piped by a
   heredoc, as the channel of its step names --, hand back, stop on a
   refusal that stops the conduction; several forms that agree on the act, that act and the thought
   `ambiguous`; several that disagree, no act, the thought `undecided` and the hand given back without
   a word -- the harness chooses no form among several; none, a `hole`: said as a `thinking` event,
   nothing guessed. A step whose production this launch said is not said again when a view or a mount
   brings it back. Where the launch hands back, its last message is said, ONCE and last, after every
   call: the three dots of the form `empty`, which pp never reads -- every production the principal
   reads goes by its print call. The NEXT door or gesture the intention asks for -- an act of this
   step, which the message puts before the step's production -- plays DURING the free step: the
   productions before it printed, the step's own production held back. A door, a mount, a re-serve
   or a block that moves on serves the step again, and the line comes back with it; after any other
   answer -- a gesture that moved nothing, a space left -- the held production is printed. An output cut into chunks is
   whole at its last chunk only, and a chunk before the last may carry the line of a step. The
   harness keeps such a `=> terminal` line with what its chunk served, and prints nothing for it yet.
   When it reads the last chunk, it prints the productions of the kept lines first, then those of the
   last chunk, in the order of the steps. The kept lines are remembered for the session: at the
   prompt, each chunk is one launch.
4. The call is typed by a subprocess of the console (`./pp <key> …`) and said as a `tool` event with its
   `tool-result`; what the console answered feeds the loop while the sequel comes by the tool. When it
   comes at the next turn, the launch ends on its `result` line: `cost_usd` 0, `denials` [], the
   session, the variant, whether it missed, how many calls it typed. A prompt that carries no output
   of pp is a `hole`: the house conducts, and the model never opens a run of its own.

## The variants

The policy's `model` key names the VARIANT of the judgment -- `conform` by default. Every other
variant makes exactly ONE miss, the one its name says, at the first place where it is possible, then
conforms for the rest of its session (a file under the system's temp dir remembers the miss, as a
model remembers its own conversation):

| variant | the miss | what the engine does |
|---|---|---|
| `wrong-form` | a production of another form where a value is due | a repair; at a proof, the same proof asked again, nothing replayed |
| `wrong-channel` | a `=> terminal` production handed by the value call instead of its print call | the block that stands, its deviation naming the print due, no repair counted |
| `missing-code` | one code left out of a proof | the same proof asked again, nothing replayed |
| `bare-fail` | every code of a proof failed, no fix, no gap | a repair: the document replays |
| `bare-call` | the bare call where a value is due | `principal-advances` in the tool result, then the house's advance repairs the empty answer |
| `empty` | an empty production | a repair |
| `no-response` | the launch hands back without its last message, the three dots | nothing: pp never reads it, and the sheet judges no last message |

## The intention

What a real model would decide of itself on reading its principal's message is said to the harness
by `PP_MODEL_INTENT` (a JSON list of one-key acts, the root's `model:` at the campaign's manifest):
`open` a door the step offers, `pick` an option, answer a `field`, `echo` the matter an INFORMATION
section serves; and the acts of the ordinary situations -- `gesture` (`./pp <key> <args>` typed during
the free step: a script, a mount, a name the step does not offer), `bare` (the bare call where a value
is due), `stray` (a `=> terminal` production handed by the value call, not printed), `unprinted` (the
productions an output asks on `terminal` written in the message, no print call typed), `bounce` (the last call typed again once a held line answered it: the console answers `not
played`), `persist` (the named miss at EVERY place where it is possible, up to the repair bound). Each
act but `echo` and `persist` plays once and what is left is remembered for the session. Over a held
output a gesture plays only when it moves nothing (a view, a script), as the standing orders say; one
that moves the run (a door, a space, a mount, a re-serve) waits for the next turn.

## What it does not do

It wires nothing (`-install` never names it; a launch does, by `--provider model`); it spells no budget,
no effort, no permission regime (`policy-unsupported`); it reads neither `.pp/.sys`, nor the run's log,
nor a record, nor the marble: it knows of the run what the prompt and its own calls tell it -- the ORACLE
of the sheet reads the run's state, the harness never does. It produces no
content and no judgment: a free production names the document and the keyword of its step, the
titles its block served and the element of its lap; a proof is `ok` on every code, and its evidence
says that it is modelled; a choice is the first value of the closed list its step chooses from, the
one shown under `OPTIONS`.
