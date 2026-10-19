# team

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.39.0`

`team` is a package for [Procedural Prompting](../../README.md). It lets a house --
a workspace with the [`agent`](../agent/README.md) package -- run **teams** of agents
that work on one task together: one member receives the task, delegates parts to
others, waits for their answers and reports back to you.

A team needs no model to move. A short process, the **tick**, reads the team's state,
routes the answers and wakes the members that have something to do. Each wake-up is
one exchange of an agent, launched by the house.

## Role

A single agent answers one message at a time. Work such as a review by several
reviewers, a daily round of reports or a chain of steps needs agents that hand work to
one another, wait for one another and stop within limits you set. `team` keeps that
coordination explicit and bounded, and tells you what waits for you.

It answers four questions:

- Who is in the team, who reports to whom, and who receives a task?
- How do I give the team a task, follow it, and stop it?
- How much may the team spend, and how many wake-ups may it take?
- What does the team wait for from me: an answer, a decision, a result to read?

## Features

### A team is declared in one document

You declare a team in `teams/<name>/TEAM.md`: its members, each a name played by one
agent of the house (`r1 agents/reviewer`; one agent may play several members), who
reports to whom, the **root** that receives a task, the people allowed to post, and
optional limits and ceremonies. The body of the document is the team's intention,
served to every member.

```
---
agents: |
  lead agents/lead
  r1 agents/reviewer
  r2 agents/reviewer
reports: |
  r1 r2 -> lead
root: lead
budget: 5
---
Review the pull request together: the lead delegates, the reviewers report.
```

`./pp team templates` lists ready-made forms (`supervisor-workers`,
`lead-reviewers`, `chain`, `solo`, `empty`, `council`, `triage`, `cross-check`, `tree`), and `./pp team new <name> --template <t>`
writes a `TEAM.md` from one. `./pp team declaration <name>` shows how `start` judges
the document, without writing anything.

### Start, post, stop

| command | what it does |
|---|---|
| `./pp team start <name> --message "…"` | reads the declaration, creates the agents the house lacks, opens the first task; without `--message`, the team starts with no task and waits for its ceremonies and your posts |
| `./pp team post <name> --message "…"` | adds a task, a note, a reply or a stop at any time; `--name` names a task |
| `./pp team stop <name>` | stops the open tasks; `--kill` also ends the wake-ups under way |
| `./pp team pause <name>`, `./pp team resume <name>` | holds the team: nobody is woken until it resumes |
| `./pp team resume <name> --task <id>` | takes back a task a limit had stopped |
| `./pp team reset <name> --member <member>` | gives a member a new run at its next wake-up |

### The tick moves the team

`./pp team tick <name>` advances the team once: it collects the wake-ups that ended,
routes each JSON answer to the member it is for, judges who waits for whom and launches
the next wake-ups. The end of every wake-up triggers the next tick, and one line of the
system's calendar (cron) is the safety net that catches a tick that died. On Windows
the skill writes no calendar line: a Task Scheduler entry (`schtasks`) that runs the
tick every few minutes does the same job.

### One answer for each message

A member answers in JSON, one element or a list of them: it hands work to the members
who report to it (`do`), asks a question of anyone in the team or of you (`ask`), or
answers a message it received (`{"re": <id>, "text": "…"}` -- « re » means « in answer
to »). Every `do` and `ask` a member receives is a debt: the member owes that message one
answer, in the same wake-up or a later one. The member that holds a task closes it by
answering the message that opened it, with the result; a member who only took part never
closes a task.

A member that puts an answer off is not forgotten. When the team stands still -- everyone
waiting for someone who waits too, or for a member that has nothing left to read -- the tick
reminds the member at the bottom of the chain that it still owes an answer. After two
reminders without an answer, the tick answers in its place (« no answer »), so that the member
waiting for it goes on; it never answers in your place: a task you opened that its member does
not close comes back to you: the team sends you a notice.

A member that keeps failing -- a model that errs, a program that crashes -- may be broken, or only
down for a while. The tick does not wait for it, and does not give it up either. Once a wake-up
of the member has failed for good, the member is suspected for a while: 5 minutes, or the
interval of the team's schedule, doubled each time it fails again. During that time nobody
wakes it: whatever is asked of it gets an answer from the tick in its place (« r2 is not
answering at the moment; it is tried again at 14:20 »), and if you open a task with it, you are
told so. After that time, its next message tries it again. If it answers, it is trusted again.
Every other member reads, at the top of its message, who is not answering at the moment.
`./pp team resume <name> --task <id>` and a new `./pp team start` trust it again at once.

### Limits that hold

The declaration may bound the team: `parallel` (wake-ups at once), `budget` (dollars
since the start; each wake-up gets its share of what is left), `budget-wakes` and
`wakes` (wake-ups of the team and of one task), `retries`, and `timeout` (a wake-up
stuck longer is ended). When a limit is reached, nothing more is launched and the team
sends you a notice. `./pp team budget <name> <usd>` raises the budget without a
restart.

### Ceremonies

A ceremony is a recurring task: `daily every weekday 09:30 with r1 r2 -> lead`. The
tick rings it once per period; `./pp team ring <name> <ceremony>` rings it at hand.
`any <n>` sets a quorum: the facilitator is woken at the n-th answer.

### Following a team

| command | what it says |
|---|---|
| `./pp team status [<name>]` | the members, their runs, the tasks, the limits, the cost and what waits for you |
| `./pp team watch <name>` | the team's events as they happen |
| `./pp team log <name>`, `./pp team result <name>`, `./pp team responses <name>` | the journal, the result of a task, the members' answers |
| `./pp team inbox` | what waits for you: questions without an answer, the team's notices, tasks done, messages returned |

`status`, `log`, `responses`, `inbox` and `watch` take `--json`, the form a program
reads -- the [`ui`](../ui/README.md) package reads them. What waits for you also
reaches your own sessions in the house, at the start of each exchange.

### One journal

A team's state is its journal: events appended, never rewritten, under the house's
records. Every reading computes the same state from the same lines. `pp-team` is its
only writer.

## Installation

`team` requires the `agent` package and the `kit`; the installer pulls both
automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> team -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add team
```

On Linux the tick's safety net uses the user's crontab; under WSL, `cron` must be
running (`sudo service cron start`).

## Quick start

Write a team from a template, start it with its first task and follow it:

```sh
./pp team new review --template lead-reviewers \
  --member lead agents/lead --member rev agents/rev --budget 5
./pp team start review --message "Review the pull request #12."
./pp team watch review
```

Answer what the team asks you, then read the result:

```sh
./pp team inbox
./pp team post review --task <task> --reply <id> --message "Yes, keep the old API."
./pp team result review
```

Give the team another task later, or stop it:

```sh
./pp team post review --name "Second review" --message "Review #13 the same way."
./pp team stop review
```
