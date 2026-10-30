# agent

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.32.0`

`agent` is a package for [Procedural Prompting](../../README.md). It turns a
conducted workspace into a **house**: a workspace that creates agents, wakes them
without an editor, holds conversations with them and keeps what they answered.

An **agent** is a pp instance in a directory under the house that nobody opens in an
editor. To wake it, the house starts the command-line tool of a coding agent -- the
**harness**: Claude Code, Codex, Gemini or Cursor -- in its non-interactive mode,
conducts the agent's run itself, one launch of the harness per block, and keeps the
harness's last answer as the agent's **response**.

## Role

A conducted workspace works with one operator in one editor session. Some work is
better given to several agents that run on their own: a review, a watch, a team of
specialists. `agent` gives the house the means to create those agents and to drive
them by commands, while each of them stays a normal conducted instance with its own
member, documents and records.

It answers four questions:

- Which agents does the house have, and where do they live?
- How do I give an agent one message, or hold a conversation with it?
- What did each agent answer, what did it cost, and how full is its context?
- How do I give a run its own copy of a repository, and remove a run for good?

## Features

### An agent is its path

`./pp agent add <path>` creates an agent at that path under the house: `agents/dev`
is `<house>/agents/dev`. The path is the agent's name in every command and record, in
its git branches and in its git identity. Two agents with the same last name at two
paths are two agents. `--type member` gives the agent a lighter boot: it does not
present its catalog of skills and does not keep work threads, but it still recalls
and records its operations; `--type chat` also stops recording them and keeps the
recall alone (agent 0.27.0). An agent borrows the house's engine and packages; it has no
editor wiring of its own.

### One exchange: `run`, `start`, `wait`, `result`

`./pp agent run <path> --message "…"` wakes the agent for ONE exchange, exactly as
a message typed in an editor session, and prints its response. The house opens a run
or, with `--run <key>`, resumes one -- the provider's own session is reopened with it.
The provider's command-line tool must be on the PATH: when it is not, the wake-up
refuses `harness-missing` before any run is opened (agent 0.25.0).

Under `conduction: hybrid` in the agent's SETTINGS, a block that asks the agent a
value (a proof, a field, a choice) comes back in its tool result instead of costing a
launch: an exchange of three laps takes 2 launches where `strict`, the default, takes
6 (engine 0.1.0-beta.70).

The launch is set by flags the providers' adapters translate: `--model`, `--effort`,
`--permissions auto|strict|bypass`, `--max-budget-usd` (the budget cap of the whole
run), `--launches` (the most launches one exchange may take), `--package <name>=on|off`
(the packages the run plays). `--dry-run` shows the command without launching it.

The house serves pp's outputs to the harness whole up to the cap the provider's adapter
declares for the run's model (`CAPS` by name: 2M characters on claude's 1M models, 1M on
codex's sol, 2M on gemini's pro; `CAP` for any model: codex, cursor), the engine's
floor of 200 000 characters otherwise (agent 0.30.0).

`start` does the same exchange in the background and returns at once with the run's
key; `wait` waits for its end, `result` reads the last response. One run is played by
one wake-up at a time: a second one is refused while the first holds the run's lock.

### A conversation: `chat`

`./pp agent chat <path>` holds a conversation on one run: each line read on standard
input is one message, each message one exchange. Under `--json` the conversation is a
flow of commands in and events out, one JSON object per line, each event naming its
voice -- the operator, the conduction, the agent, a tool call. The
[`ui`](../ui/README.md) package is built on that flow.

### The material of a run: `--work`

`run --work <repository>` gives the run its own clone of a repository, on the branch
`agent/<path>/<key>`, pushed back to the repository after each exchange.
`./pp agent workdirs` lists those clones with their state; `./pp agent prune` removes
one.

### Reading the house

| command | what it says |
|---|---|
| `./pp agent list` | the agents of the house, with their runs, the wake-ups under way and their responses |
| `./pp agent status <path>` | each run of the agent, the one that spoke last first: its state, its block, its session and provider, its responses; under `--json`, also its policy, its budget, its context and the packages it plays |
| `./pp agent exchanges <path> <key>` | the run's history: each message paired with the response that answers it |
| `./pp agent stats <path> <key>` | the cost, the launches and the conduction's figures of the run, and how full its context is |
| `./pp agent calibrate [<path> ...]` | for every run, the context the provider measured at its last call beside the house's estimates, and the constants that fit them best; reads only |
| `./pp agent flow <path> <key>` | every event the run's exchanges kept |
| `./pp agent responses`, `./pp agent messages` | the latest responses and messages, newest first |
| `./pp agent name <path> <key> <name>` | gives a run a name, as you type it |

`list`, `status`, `exchanges`, `stats` and `flow` take `--json`: one object per line,
the form a program reads. The text form never changes when a field is added.

### How full a context is

When the provider counts what each call sends the model -- Claude Code does --, the house reads it
as the call ends: `agent stats` and `agent status` give the context of the run's last measured call,
and a conversation under `--json` gives each call as it comes. Between two measures, or for a
provider that counts nothing, the house ESTIMATES: the last measure plus what the exchanges carried
since, weighed by the constants the provider's adapter declares; the faces then say `estimated`.
`./pp agent calibrate` compares, run by run, that estimate with what the provider's own store
measured, and prints the constants that would fit the house's runs best (agent 0.32.0).

### Removing runs: `purge`

`./pp agent purge <path> <key>` (or `--before <YYYY-MM-DD>`) says what it would
remove of a run -- the lines of the house's records, the files the agent's engine keeps
-- and removes it for good only with `--yes`. A run under way, or a run held by
another package (a member of a living team), is refused.

### The house's records

The house keeps what its agents did in its own records: `responses.jsonl`,
`messages.jsonl`, `sessions.jsonl`, `names.jsonl`, `workdirs.jsonl` and one flow file
per run. `pp-agent` is their only writer. A response line keeps, beside `response` (the
last launch's answer), `words` -- every words of the exchange's launches, each under
its launch number: the response composed --, and `model` and `effort`, the policy
played (agent 0.25.0); `agent responses` prints the words under the response, `agent
exchanges --json` carries the three fields. `agent flow --exchange <n>` reads the n-th
exchange as `exchanges` numbers it.

## Installation

`agent` requires the `kit`; the installer pulls it automatically. The house must be
installed for the harness its agents will run on (`-claude`, `-codex`, `-gemini` or
`-cursor`).

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> agent -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add agent
```

The house's own sessions are unchanged; the commands below are played from its root.

## Quick start

Create an agent, give it one message, then hold a conversation with it:

```sh
./pp agent add agents/dev
./pp agent run agents/dev --message "Read the README and list what is missing."
./pp agent chat agents/dev
```

Resume the same run later, and read what it did:

```sh
./pp agent status agents/dev
./pp agent run agents/dev --run <key> --message "Now write the missing section."
./pp agent exchanges agents/dev <key>
./pp agent stats agents/dev <key>
```

Give a run its own clone of a repository, with a budget cap:

```sh
./pp agent run agents/dev --work ~/src/project --max-budget-usd 2 \
  --message "Fix the failing test and commit."
```

Each agent can be shaped like any conducted workspace: edit its `MEMBER.md` to give
it a role, and pin the packages it needs in its own instance.

## Reference

### The house and its agents

#### An agent is its path

A workspace that pins the `agent` package is a **house**. An agent is an instance
anywhere under the house that borrows the house's machine.

An agent IS its PATH relative to the house, slugs joined by `/` (`ag1`, `rep1/ag1`).
That path is the argument of every verb, the agent's name in every record, its branch
and its git identity. Two agents of the same name at two paths are two agents.

#### Birth: `./pp agent add <path>`

`./pp agent add <path>` gives the agent birth. It is the engine's generic install,
specialized:

- the house's machine is borrowed;
- no door, no host flag;
- the launcher `pp` beside it;
- no `.claude/`, no wiring of its own.

These refusals come before anything is written: `agent-path-invalid`, `agent-exists`,
and `type-unsupported` (a `--type` other than `member` or `chat`).

`--type member` writes `capabilities: false` (no table; the two readings come all the
same) and `package.steering: off` at the agent's SETTINGS. `--type chat` adds
`continuity_history_day: never`. When the house does not pin the package a key belongs
to, that key is left out and named at the birth.

The birth plays under the house's birth lock for that path
(`state/born-<digest>.lock`; `born-busy` past `call_lock_wait`), so that a path is born
once. `team start` does the same at the paths `TEAM.md` gives.

`./pp agent list` finds every borrower under the house by descending it. The house's
`./pp upgrade` reaches them by descending too.

### One exchange: `./pp agent run`

```sh
./pp agent run <path> (--message "<text>" | --message-file <path>)
  [--model <m>] [--max-budget-usd <n>] [--permissions auto|strict|bypass]
  [--effort low|medium|high|xhigh|max] [--new | --run <key>] [--provider <name>]
  [--harness <command>] [--json] [--quiet] [--heartbeat <seconds>] [--dry-run]
  [--launches <n>]
```

`run` wakes the agent for ONE exchange, as a message typed in a session, CONDUCTED BY
THE HOUSE. The other options of a run (`--door`, `--documents`, `--package`, `--work`)
are described below.

#### How the house conducts the exchange

The house plays `-new "<message>"` on the agent's instance under the principal's mark
(`PP_CONDUCTED_BY_PRINCIPAL=true`, on its own calls alone). It reads the key on the
first line and launches the harness in `<path>/`, in a session of its provider.

The launch's environment names the run it conducts: `PP_CONDUCTED_RUN=<key>`.

- A `-new` the model plays inside that launch, while that run stands mid-exchange,
  opens nothing and says so in one line.
- A `-new` played without that variable, or naming another run, opens even while a run
  of the post stands (an editor's conversation beside the post).

The harness runs on the PROMPT. At the first launch it is the message under
`[message from your principal]`, then pp's whole output. Every later launch gets pp's
output alone.

After each launch the house reads the run: an output held by the agent's value, a chunk
waiting, a block to advance. It makes the run advance by its marked bare call. There is
one launch of the harness per output that ASKS the agent something.

An output that parks the run with nothing held, nothing pending and no instruction line
(the bare AWAIT after a judged proof) is served and never launched. So a relayed
exchange under a law of production costs two launches (the boot with the WORK, then the
checkpoint), and each exchange after it costs one.

This goes on until the run is PARKED on its AWAIT with nothing held. The harness's last
answer is the response.

#### Bounding the launches: `--launches`

`--launches <n>` (24 unless said) bounds the launches of a wake-up. When they are spent
the wake-up stops with `launches-spent`: the last response is kept and the run is left
standing.

#### The budget cap: `--max-budget-usd`

`--max-budget-usd <n>` is the BUDGET CAP of the RUN. It covers what the run spends over
all its exchanges and their launches, conducted or bare: the sum of its responses'
`cost_usd` plus the launches of the exchange under way.

Before every launch the remainder is computed. When none is left, nothing is launched
and the wake-up says `budget-spent`:

- before an exchange: nothing is recorded, the run stays as it was;
- between two launches: the last response is kept, the run is left standing.

The remainder is handed to the launch's policy as `max_budget_usd` where the adapter
spells that key (`SPELLS`). A launch may go past the cap by what the provider's own
bound lets through. Where the adapter spells no such key, the run may go past it by one
launch.

Under an adapter whose `COST` is `None`, a cap refuses `budget-unmeasured`.

#### Resuming a run: `--run`

With `--run`, the run's own session is reopened from `sessions.jsonl`. The marked
`<key> "<message>"` opens the exchange. A run left standing is taken up where it
stands, and the house says `standing resumed`.

| refusal | when |
|---|---|
| `session-missing` | no session is recorded for the run |
| `provider-mismatch` | the run was opened under another provider |

#### What the harness runs with

The harness runs with the marble of the MODE (`.sys/system.common.md`), the house's
wiring, and the policy and the session as data (`conductor.adapters.launch`).

The same face takes `workdir`, the material a run works on under the agent's
directory, and composes it the same way for every provider:

- the head of the prompt names it, and names the console by its absolute path;
- `PP_WORKDIR` and `PP_CONSOLE` are set in the environment;
- no provider flag is used.

It refuses `workdir-invalid` and `workdir-unsupported`.

#### The entry document: `--door`

`--door <document>` names the run's ENTRY, at an opening only (`door-on-resume` with
`--run`). It is handed by `PP_DOOR` and read by `-new` alone.

The agent's instance resolves the document and opens it as a CALL above the boot: the
first exchange carries it. `door-unknown` leaves nothing behind. The trace says `door`.

#### The root of documents: `--documents`

`--documents <dir>` (absolute, or relative to the house's directory) gives the run its
ROOT of documents at an opening. It is handed by `PP_DOCUMENTS` on the house's `-new`
alone (see [`./pp -new`](../../docs/reference/agent-face.md#pp--new-message-)), and is
never inherited by the harness nor by another call.

Under `--run`, a root other than the run's refuses `documents-fixed` before any launch.
`chat --json` says the root as `documents` in `ready` and `opened`.

#### The packages a run plays: `--package`

`--package <name>=on|off`, given once per package on `run`, `start` and `chat`, names
the packages the run plays.

The switches are first judged against the packages the agent's instance pins, before
anything is opened or written. They refuse `package-invalid`, `package-base`, and
`package-unpinned` for a package the instance does not pin switched on. A package the
instance does not pin, switched off, asks nothing and is left out.

Then each switch the run does not play already is played on the run under the
principal's mark, by the engine's `-disable` or `-enable`. This happens before the
first launch, at an opening as at a resume. While the package holds the run's view
(`package-in-flight`), the switch is tried again before every launch: this is the
waiting list of a conversation.

The state is the engine's, at the run's slot; no record gains a field. `--dry-run`
says `package <name> on|off` and plays nothing.

#### The material of a run: `--work`

`--work <repo> [--base <ref>]` gives the run its material. Before the launch, under the
house's lock for the repository, the house makes a local clone by hard links under
`<path>/work/<key>`, on the branch `agent/<path>/<key>`.

The git identity of the exchange is set in the environment from the agent's path:
`rep1/ag1 <rep1.ag1@<the house's slug>>`.

After the harness, the branch is pushed back by the repository's absolute path.
`workdirs.jsonl` keeps each run's material with its state: `open`, `pushed`,
`unpushed` (with its reason) or `pruned`.

`./pp agent workdirs` lists them. `./pp agent prune <path> <key> [--force]` removes a
clone. A run pruned is never resumed (`workdir-missing`).

### Removing runs for good: `./pp agent purge`

`./pp agent purge <path> (<key> … | --before <YYYY-MM-DD>) [--yes] [--force] [--json]`
removes runs FOR GOOD, each record by its writer:

- the house's records are rewritten without the runs' lines (the one write of a record
  that is not an append);
- their clones are removed;
- what the agent keeps of them is removed by `./pp -purge` played on the agent's
  instance.

Without `--yes` it says what it would remove and writes nothing. It is all or nothing:

| refusal | when |
|---|---|
| `run-busy` | a wake lock is held |
| `workdir-unpushed` | a clone is not pushed (`--force`) |
| `call-busy` | the engine's refusal, relayed |
| `run-held` | the run's guardian holds it |

`agent` declares the vector family `agent-run:<path>/<key>` (verified by
`pp-agent verify`). `purge` asks the engine for its guardian before any removal, dry or
not.

`team` declares itself that guardian: the run a member of a living team holds is never
purged. Play `team reset` first.

### The flow of an exchange: `./pp agent flow`

Every exchange (`run`, `start`, `chat`, conducted or bare) KEEPS its flow. Each event
its flow says (the conduction whole, the voices, the steps, `response` and `verdict`,
the very objects `chat --json` says) is appended to
`records/flows/<digest of the agent's path>/<key>.jsonl`, one file per run.

```sh
./pp agent flow <path> <key> [--exchange <n>] [--from <n>] [--follow] [--json]
```

`agent flow` reads it back:

- `--from <n>`: the lines from the n-th line of the file on;
- `--follow`: the lines streamed as the file gains them, until the exchange's
  `verdict`. This is what a reader following a launch keeps open while it plays.

`purge` removes the flow with the run.

### Weight and packages in `agent status`

`agent status <path> --json` says each run's `weight {lines, files, bytes, flow}`: what
`purge` would count of it, without asking for one. The last object and
`agent list --json` give their sum.

That last object also says `packages`: the packages the agent's instance pins beyond
its base, as its SETTINGS switch them. It is what `ready` says at an opening, before
any run.

### What the agent may call

The agent calls pp for its values alone (`./pp <key> -`):

- a bare call it types is refused `principal-advances`;
- a `-new` it types mid-exchange opens nothing;
- a `-new` it types on a parked run opens a STRAY run, said and counted at the verdict.

### The answer and the house's records

The adapter reads the answer at every launch (`conductor.adapters.answer`). A
`--harness` command's answer is read by the adapter of the GRAMMAR that `--provider`
names beside it; that `--provider` is owed with every `--harness` (`grammar-missing`;
`team start` refuses it too). `pp-agent` reads no field of a harness's output itself.

The answer owes its session identity: without it nothing is kept. It is kept at the
HOUSE's records, described below.

#### `messages.jsonl`

`{at, from, to, run, message, policy}`, written at the launch, the policy as the face
judged it. `tag` and `pid` are added when a caller gave them.

#### `responses.jsonl`

`{at, agent, run, index, response, cost_usd, session_cost_usd, launches, denials, error, harness_rc, flow}`

| field | meaning |
|---|---|
| `cost_usd` | the SUM of the launches' costs, each read in the scope its adapter declares (`COST`: under `session`, the difference between the cumul reported and the cumul before it) |
| `session_cost_usd` | the run's cumul in that session |
| `launches` | the launches of the wake-up |
| `flow` | what the flow of the exchange carried, summed by voice in tokens as the engine estimates them (`principal`, `conduction`, `pp_input`, `pp_result`, `tool_input`, `tool_result`, `words`, `thinking`), and its `calls` to the model |
| `context` | present once a call was MEASURED: what the exchange's last measured call sent the model, as its adapter's `context` events say it |

A wake-up its run cap stopped between two launches says `error: "budget-spent"` and
`budget {cap, spent}`. A launch always has its run.

#### `sessions.jsonl`

`{at, agent, run, provider, session}`. A run's last line holds its session.

#### The context of a run

From the responses' `context`, `agent stats --json` says the run's context
(`context`):

| part | meaning |
|---|---|
| `measured` {tokens, index} | the last measure |
| `tokens` | that measure plus the flow of the exchanges after it, weighed by the adapter's `FLOW_RATIO` and `THINKING_KEPT`; without a measure, its `CONTEXT_BASE` plus the whole flow weighed |
| `estimated` | whether anything was added to a measure |
| window | the window of the run's model as its adapter declares it (`CONTEXT_WINDOWS`), and the part `used` |
| pp's share | pp's share of the flow |

`agent status --json` says it reduced: {tokens, used, pp, estimated}.

The flow of `chat --json` says each measured call as `context` {tokens, window, used}
while the launch plays. `run` never says it.

#### Calibrating the estimate: `./pp agent calibrate`

`./pp agent calibrate [<path> ...] [--json]` sets, per run, the context the provider's
own store measured at its last call (`conductor.adapters.contexts`) beside the flow
alone and the calibrated estimate, with their gaps.

Then, per provider, it gives their spread and the constants fitted on its runs without
a compaction: what an adapter's declaration is copied from. It writes nothing.

### A conversation: `./pp agent chat`

`./pp agent chat <path> [--run <key>]` holds a CONVERSATION at the foreground.

- The messages are read on stdin, one per line. A line ending on a backslash goes on
  with the next.
- Each message is ONE exchange (the same one `run` plays) of one run, held from a
  message to the next with its session and its wake lock (`run-busy` for anyone else
  meanwhile).
- After each exchange, the response goes to stdout and the verdict to stderr. An
  exchange that ends badly is said, and the conversation goes on.
- A SIGINT while waiting, or the end of stdin, closes the conversation, exit 0.

#### Interrupting an exchange

A SIGINT to `pp-agent` during an exchange ends the harness and says `interrupted`. The
interruption is kept in the mark of the run's wake lock (`interrupted: true`).

The run's next wake-up, in this conversation or another process, then opens its first
prompt on `[interrupted by your principal]` before the message's head, and says
`· after an interruption` at its verdict.

#### The JSON flow: `chat --json`

`chat <path> --json` makes the conversation a FLOW: commands on stdin, events on
stdout, one JSON object per line; stderr is silent.

| commands | `message`, `stop`, `quit`, `set`, `conduct`, `package` |
|---|---|
| events (by `kind`) | `principal`, `conduction`, `agent`, `step`, `response`, `verdict`, `waiting`, `refused`, `closed` |

Each event names its voice by its `kind`.

#### What a launch does, live

What a launch does reaches the flow WHILE it plays. Each line the harness prints is read
by its adapter's `events` face (`conductor.adapters.events`) and said as one of:

- `tool` (with `pp`: whether its `shell` calls the agent's console);
- `tool-result`;
- `thinking`;
- `words`.

These come always before the `agent` event of their launch. They are never in the five
records and never said by `run`.

A line the adapter refuses is a `step` `refusal` (`events-malformed`), and the launch
goes on.

#### Changing the policy: `set`

A `set` command changes the model, the budget or the effort of the next launches, said
by a `policy` event. `provider` and `permissions` stay as opened.

`status --json` says each run's policy and the agent's `last`. `agent providers [--json]`
says what each wired adapter spells and the model names verified with it (`SPELLS`,
`MODELS` of its `wire.py`).

#### Suspending the conduction: `conduct`

`{"kind": "conduct", "on": false}` makes the next exchanges BARE:

- one launch on the session;
- the prompt opens on the line that says the principal has suspended conduction and
  the run resumes at their word, then the message;
- no call of pp;
- the records are marked `conducted: false`;
- the run does not move.

`on` brings the conduction back.

#### Switching a package: `package`

`package` is the engine's switch, played on the run under the mark. `opened` says the
run's `packages`.

A `package` the run cannot take yet WAITS in the conversation's list. This happens
before the run is opened, or while the package holds the run's view
(`package-in-flight`, mid-passage). A parked run holds no mount and takes the switch at
once.

A waiting switch is played again before every launch until the engine takes it. The
`package` event says `pending`; a `refused` one carries the engine's `detail`.

#### The cap: `opened`

`opened` says the run's `cap {set, applied}`: the agent's `max_harness_tool_output`,
and the cap its outputs are cut under, the floor of a principal's cap applied by the
engine's `settings.served_cap`. The [post](../ui/README.md#the-post-of-a-house) says a
raised cap on its remedy line.

#### The first event: `ready`

The flow opens on `ready`, once, before the first `waiting` and any message. It says
the agent, `resumed`, the provider, the policy, the packages, the cap and `conducted`,
as the conversation judged them. Its `run` is the key under `--run`, `null` at an
opening. A reader thus knows its run without sending anything.

#### Rule B4 and the console's streams

The kit has no rule B4 (a tool call before every answer) anymore: the LLM that
conducts its run reads that rule at `SYSTEM.CONDUCT` § Advancing.

The verb `agent` is declared `tty: true`: the console hands the skill its streams.

### In the background: `start`, `wait`, `result`

`./pp agent start` plays the same exchange detached. The child holds the wake lock and
reports `{key, pid}` at once. Its words go to `session-<key>.wake.log` beside the lock.

`./pp agent wait <name> <key>` waits for the lock to be free and prints the response as
`run` does (`wake-dead` when the wake-up ended without one). `result` reads it at once.

`--on-end <command>` plays after the lock is released.

### What `run` prints

On stdout, `run` prints what it kept:

- the response's text, where a line opening on `::` is put behind a backslash, so that
  no agent's words give pp an order (`::push`, `::clear`, `::mount`);
- or, with `--json`, the response's record line plus `session` and `state`.

Its verdict line and its refusals go to stderr.

Every reading of a text an agent or a message carried (`agent responses`,
`agent messages`, `team responses`, `team log`) prints such a line the same way.

### Judged before the launch

Everything is judged before a launch: the run, its session and provider, its material,
the composed line. Only then is the wake lock's mark written. A refused resume leaves
its run as it was; a refused opening takes its reserved key back.

#### The neighbours line

When other runs of the agent play, the prompt opens on the neighbours line,
`[runs under way: <key> since HH:MM « <head> »]`: the local hour of each wake lock's
mark and the first line of its message.

A conversation that resumes a run marks its wake lock at the take, before any message:
the hour of the take, the head of the run's last message, `held: "chat"`, an
interruption kept, and no count of responses. Its neighbours read it the same way.

### Following the trace

While the harness plays, `run` follows the run's trace with the engine's reader
(`conductor.state.log`: `tail`, `follow`, `step_of`, `said`). The trace is read, never
written.

`run` says each step on stderr as it happens: `[HH:MM:SS] <key> · opened`, the stack of
a block served, `parked`, `answer`, `refused <code>`, … Under `--json` it says one JSON
object per line.

After `--heartbeat` seconds without a step (60 by default) it says
`no event for <n>s`. `--quiet` says none of it.

`list`, `status <name>`, `responses` and `messages` read back (see
[Reading the house](#reading-the-house)).

## See also

- [The loop and the commands](../../docs/reference/agent-face.md) — the engine's `-new`, bare call and value call an agent's run is made of.
- [The adapter surface](../../docs/reference/adapters.md) — what each provider's adapter declares: `SPELLS`, `COST`, the context constants.
- [team](../team/README.md) — teams of agents built on the house.
- [ui](../ui/README.md) — the post, built on the `chat --json` flow.
