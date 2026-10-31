# The adapter surface

This file covers the exact surface each install flag wires, the non-interactive face that composes one exchange of a harness, and the hook channel that carries the conduction to any model.

- [The adapter surface](#the-adapter-surface)
- [The hook channel](#the-hook-channel)
- [See also](#see-also)

## The adapter surface

The modes and their guarantees are the [README](../../README.md)'s story; here is the exact
surface each flag wires.

#### The agent contract and its projections

The agent contract is the engine's own card, in two files:

- `engine/refs/PP.COMMON.md` — the calls of the agent's tasks, both modes;
- `engine/refs/PP.CONDUCT.md` — the calls that advance a run the LLM conducts.

Every instance carries both with its engine, and they are compiled into the marble.

Cards and the Gemini command are **projections with provenance**:

- a pristine projection follows the current contract on day-2/doctor/upgrade;
- an edited one is preserved, the fresh projection lands beside it as `.candidate`, and the drift is said.

The `card-drift` signal is the engine's own. It is pushed at boot whether or not any package
declares a check, and rendered as a diagnostic in the boot's block, once per run:
`card-drift · warning · <home> differs from the contract -- ./pp doctor`.

Per-provider details and external links live under [adapters/](../../adapters/).
How pp launches ONE exchange of a harness by its command line — the non-interactive mode, the
exchange the editor's extension launches, and the `launch()` contract pp adapts per provider —
is in [adapters/README.md](../../adapters/README.md).

#### The non-interactive face

#### `launch()` — composing one exchange

```
conductor.adapters.launch(provider, workspace, meta, prompt, marble=None, root=None,
                          wiring=None, policy=None, session=None) -> (argv, env, stdin)
```

`launch()` composes the command line of ONE exchange of a session of the provider and never
runs it. The skill that calls it launches the process, writes `stdin` — the prompt, whole — on
the process's standard input, waits, and reads the exit code.

The prompt is never an argument. One argument is bounded (128 KiB on Linux); a prompt that
carries whole blocks is bounded by the model alone. An adapter whose launch renders anything
but the three elements refuses `launch-malformed`.

#### Sessions

`session` left out OPENS a session, which the provider keeps and names. The identity the
provider gave RESUMES it: claude, gemini, cursor `--resume <id>`, codex `exec … resume <id>`.
The session is judged once at the face (`session-invalid` for anything but a non-blank text).

pp creates, keeps and looks up no session, and no line throws one away.

At every call of the model, the system prompt and the whole context reach the agent:

- claude and gemini, whose sessions do not reliably record the system prompt, carry the marble and the receipt at EVERY launch, the resume included;
- codex re-reads its config by itself;
- cursor, with no channel, carries no receipt, and the standing rules the engine serves inline ride the session's history.

#### Where the adapter is found, and the marble

The adapter is found by its path under the product (`adapters.product_of(meta)`): the running
engine's own checkout, or the `source:` the instance declares. A vendored engine carries no
adapters.

`marble` left out lets the adapter name the marble its own launcher carries
(`system.replace.md` when it stands). A marble handed wins. The marble of the run's mode —
`system.common.md` for a run its principal conducts — reaches the provider's channel as the
adapter spells it:

- claude: the file;
- gemini: the composition `wire()` made beside it;
- codex and cursor: they read no marble at the call.

#### `policy` — what the exchange may spend and do

`policy` is `{"model": …, "max_budget_usd": …, "permissions": …, "effort": …}`. It is judged
once at the face: `policy-unknown` for a key outside those four, `policy-invalid` for a value
that does not parse.

The adapter spells it in its host's flags, or the adapter whose host has no such flag refuses
it (`policy-unsupported`, naming the provider and the key). The budget and a regime other than
`auto` are spelled at claude alone; the effort is refused at gemini.

`effort` says how much the model reasons: `low`, `medium`, `high`, `xhigh`, `max`. Each adapter
maps them to its provider's channel:

- claude: `--effort`;
- codex: `-c model_reasoning_effort=…`;
- cursor: the model's suffix ([adapters/README.md § The effort](../../adapters/README.md#the-effort)).

`permissions` says what the harness may do without asking:

| Regime | Meaning |
|---|---|
| `auto` (the default) | what it judges safe itself |
| `strict` | the rules the house's settings write and nothing else |
| `bypass` | everything |

At claude these are `--permission-mode auto|dontAsk|bypassPermissions`
([adapters/README.md § The permission regime](../../adapters/README.md#the-permission-regime)).

#### `wiring` — the harness configuration handed to the process

`wiring` is the directory whose harness configuration is handed to the process — an agent's
home, wired once. claude reads its `.claude/settings.json` by `--settings`; the three others
read nothing. [adapters/README.md](../../adapters/README.md) spells both `policy` and `wiring`
per provider.

#### `answer()` — what the harness answered

`conductor.adapters.answer(provider, meta, stdout, stderr)`

`answer()` reads what the harness ANSWERED beside its words, in the output format the adapter
chose, as one shape — `{cost_usd, denials, error, session}`, no text:

| Provider | What is read |
|---|---|
| claude | `total_cost_usd`, `permission_denials` and `session_id`; its `subtype` as the error under `is_error` |
| gemini | `error` and `session_id` |
| codex | `turn.failed` and the `thread_id` of `thread.started` |
| cursor | `session_id` |

A stdout no reading parses says `unreadable` with its tail.

The SCOPE of that `cost_usd` is what the adapter declares beside its faces, `COST`:

- `session` — claude: the session's cumul at that launch;
- `launch` — that launch alone;
- `None` — codex, gemini, cursor: no cost.

A caller reads `COST` through `conductor.adapters.load`, never the engine.

The session is OWED: a reading without it refuses `session-missing`. An adapter without that
face refuses `answer-unsupported`; one without the `events` face refuses `events-unsupported`.

Nothing is run by either face: the skill that launched hands the streams it captured.

#### `events()` — one line of output, in a common schema

`conductor.adapters.events(provider, meta, line)`

`events()` reads ONE line of the harness's output as the exchange plays, through the adapter's
third face, and renders its events in a COMMON SCHEMA no host names:

| Kind | Fields | Meaning |
|---|---|---|
| `tool` | {id, name, title, shell, input} | a call of a tool; `shell` is its command when it runs one |
| `tool-result` | {id, content, error} | the result of a tool call |
| `thinking` | {text and/or tokens} | the model's thought |
| `words` | {text, delta} | the ONE source of the model's text; `delta` (true alone) marks a piece of a message the host streams in pieces |
| `context` | {tokens, id} | what ONE call sent the model, its input read from the cache or written to it as the host counts it; `id` is the message the call answered |

The face drops the fields the schema does not name, poses the optional ones, and refuses
`events-malformed` for anything outside it. An adapter without the face refuses
`events-unsupported`.

#### `reader()` — the reader of one launch

`conductor.adapters.reader(provider, meta)`

`reader()` is the READER of one launch, the one a launcher reads with. Its `heard(line)`
renders the line's events through `events`.

It holds the `words` an adapter marks `delta` and renders them as ONE whole `words` at the next
event of another nature, at a whole `words`, or at `end()`, which is owed at the launch's end.
What it renders never carries `delta`.

A `context` repeating the `id` of the last one it said is said once (a host repeats a
message's usage on each of its blocks).

#### `contexts()` — what the provider's own store keeps

`conductor.adapters.contexts(provider, meta, session)`

`contexts()` reads what the provider's OWN store keeps of a session, through the adapter's
`contexts(session)` face:

- `calls` — the context each call sent, in order;
- `compactions` — those the host made.

It renders None where the adapter has no such face or its store no such session, and refuses
`contexts-malformed` for a reading of another shape. It reads only.

#### Estimates an adapter may declare

Beside its faces, an adapter may declare the estimate of a context no call measured:

| Name | What it declares |
|---|---|
| `CONTEXT_BASE` | the tokens of a session's first call: the system prompt, the tools, the standing orders |
| `FLOW_RATIO` | the weight of a token the engine estimates in the model's tokenizer |
| `THINKING_KEPT` | the part of the model's thought the context keeps |
| `STORE_ENV` | the variable that moves its store |

claude declares the four.

#### The streams read

Claude, gemini and cursor are launched on their STREAM (`stream-json`), codex on its JSONL, and
both faces read it. claude's stream is verified on a machine; codex's, gemini's and cursor's are
read in their docs ([adapters/README.md § The third face](../../adapters/README.md#the-third-face-events)).

#### The launch per provider

| Provider | `argv` | `env` |
|---|---|---|
| claude | `claude -p [--resume <id>] --append-system-prompt-file <marble> --permission-mode auto|dontAsk|bypassPermissions --permission-prompts none --output-format stream-json --verbose` — the mode from `permissions`, `auto` without it; `--system-prompt-file` on the replace marble; the marble at every launch; the prompt on stdin | `PP_MARBLE=1` |
| codex | `codex exec --sandbox workspace-write --full-auto --json [resume <id>] -` — the prompt on stdin, named by `-` | `PP_MARBLE=1` as data — `.codex/config.toml` carries the marble and sets the receipt for the CLI itself |
| gemini | `gemini [--resume <id>] --approval-mode yolo --output-format stream-json` — the prompt on stdin, no `-p` | `GEMINI_SYSTEM_MD=<marble>` (the composition of the marble handed, `system.common.gemini.md` for `system.common.md`, when `wire()` made it), `PP_MARBLE=1` — at every launch |
| cursor | `agent -p [--resume <id>] --force --output-format stream-json` — the prompt on stdin | — (no system-prompt channel, no receipt) |

#### Refusals

| Refusal | When |
|---|---|
| `provider-unknown` | no `adapters/<name>/wire.py` under the product |
| `launch-unsupported` | an adapter that wires but composes no launch |
| `launch-malformed` | an adapter whose launch renders anything but `(argv, env, stdin)` |
| `answer-unsupported` | an adapter that composes a launch but reads no answer |
| `events-unsupported` | an adapter without the `events` face -- the model's words cannot be read (at `events` and at `answer`) |
| `events-malformed` | an adapter whose `events` face renders no list, or an event outside the common schema (a kind outside `tool`, `tool-result`, `thinking`, `words`, `context`; a required field missing or of another type; a `context` whose tokens are no count) — the adapter and the kind named |
| `contexts-malformed` | an adapter whose `contexts` face renders something else than `calls` (counts) and `compactions` — the adapter named |
| `policy-unknown` · `policy-invalid` | a policy key outside `model`, `max_budget_usd`, `permissions`, `effort`; a value that does not parse (an empty model, a budget not above 0, a regime outside `auto`, `strict`, `bypass`, an effort outside `low`, `medium`, `high`, `xhigh`, `max`) — refused at the face, before any adapter |
| `policy-unsupported` | a key the provider's CLI cannot spell — the budget, and a regime other than `auto`, at gemini, codex, cursor — named with the provider |
| `session-invalid` | a session that is not a non-blank text — refused at the face, before any adapter |
| `session-missing` | an answer whose reading carries no session identity — the provider named, the error read or the stream's tail cited |
| `source-missing` | a vendored engine whose instance points at a source gone |

#### What each install flag wires

| Flag | Card | Door (written by the flag) | Marble | Permissions |
|---|---|---|---|---|
| `-claude` | `.claude/skills/pp/` | `CLAUDE.md` | `claude-pp` | `.claude/settings.json` — `Bash(./pp:*)`: the `:*` covers the run key and every argument; written once |
| `-codex` | `.agents/skills/pp/` — a standard **Cursor reads too** | `AGENTS.md` | `.codex/config.toml` — pp manages exactly TWO fields (`developer_instructions`, the `PP_MARBLE` sentinel), spliced only when pristine, every other key byte-preserved | `.codex/rules/default.rules` — verify with `codex execpolicy check` |
| `-gemini` | `.gemini/commands/pp.toml` (`/pp` serves the card) | `GEMINI.md` — read natively, points at `/pp` | `gemini-pp` — the composition rebuilds on the current marble; the baseline moves only on explicit rewire | documented only: a `coreTools` allowlist may RESTRICT the whole tool set — choose your approval mode yourself |
| `-cursor` | `.agents/skills/pp/` — the same card `-codex` writes (shared, cumulable) | `AGENTS.md` + `CLAUDE.md` (Cursor-recognized) · `GEMINI.md` written for workspace interop | — no system-prompt channel: recall guarantee | `.cursor/permissions.json` — a `terminalAllowlist` PREFIX on `./pp` (the run key passes free); written once |

#### Doors and the receipt

A bare install (no flag) writes the two generic doors — `CLAUDE.md` and `AGENTS.md` — for a
harness you wire yourself.

Every door is ONE text: the first call, `./pp -new`, and nothing to invoke before it. The
standing orders that call serves carry the card. The skill or the command a harness registers
stays the operator's own, never a second copy the agent reads first.

`PP_MARBLE` is a **receipt**, not a switch: declared with nothing compiled to carry, the boot
refuses (`marble-missing`) rather than playing blind.

The house's own calls to an agent's conductor (`pp-agent`: `principal_environment`) carry the
receipt whenever the adapter's launch declares it — claude, gemini and codex do, as data of
their `env`. So the boot block handed to the CLI repeats no standing orders the system prompt
already carries.

#### Day 2

**Day 2** — a standing instance gains an adapter with the same flags, no workspace:
`./pp -install -codex` wires the current instance (several flags cumulate); a replay answers
`already wired`.

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

## See also

- [console.md](console.md) — the operator's console, its verbs and `-install`.
- [instance.md](instance.md) — the instance on disk, where the marble and the cards live.
- [block.md](block.md) — the block the hook channel carries, section by section.
- [adapters/README.md](../../adapters/README.md) — per-provider launch details and external references.
