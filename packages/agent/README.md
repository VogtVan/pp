# agent

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.29.0`

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
| `./pp agent status <path>` | each run of the agent, the one that spoke last first: its state, its block, its session and provider, its responses |
| `./pp agent exchanges <path> <key>` | the run's history: each message paired with the response that answers it |
| `./pp agent stats <path> <key>` | the cost, the launches and the conduction's figures of the run, and how full its context is |
| `./pp agent flow <path> <key>` | every event the run's exchanges kept |
| `./pp agent responses`, `./pp agent messages` | the latest responses and messages, newest first |
| `./pp agent name <path> <key> <name>` | gives a run a name, as you type it |

`list`, `status`, `exchanges`, `stats` and `flow` take `--json`: one object per line,
the form a program reads. The text form never changes when a field is added.

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
