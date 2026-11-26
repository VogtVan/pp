# team

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `1.36.64`

`team` is a package for [Procedural Prompting](../../README.md). It lets a house --
a workspace with the [`agent`](../agent/README.md) package -- run **teams** of agents
that work on one task together: one member receives the task, delegates parts to
others, waits for their answers and reports back to you.

A team needs no model to move. A short process, the **tick**, reads the team's state,
routes the acts the members say and launches the members that have something to do. Each
wake-up is ONE launch of an agent by the house, with what arrived for it at the head of its prompt.

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
optional limits and ceremonies, and the `name` the team is shown by -- changeable at any
time, the directory staying the team's identity. The body of `TEAM.md` is your word to the
team: pp serves it to every member, and serves it again as soon as you change it. `team start`
renders the team's document beside it, `teams/<name>/TEAM-<name>.md`: it serves your word, the
intention of the template the team names, and the documents the team gives its members. What every member must do in a team -- who answers to whom, the
messages it may send, the answer it owes -- is the package's part of the standing orders,
the same for every team. `team delete <name> --yes` removes a team and what it made.

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

`./pp team templates` lists the templates the house sees, among them nine ready-made teams
(`teams/supervisor-workers`, `teams/lead-reviewers`, `teams/chain`, `teams/solo`, `teams/empty`,
`teams/council`, `teams/triage`, `teams/cross-check`, `teams/tree`).
`./pp team declare <name> --template teams/<t>` writes a `TEAM.md` that names one; `declare` is
the one verb that writes `TEAM.md`. `./pp team declaration <name>` shows how `start` judges
the document, without writing anything.

### Start, post, stop

| command | what it does |
|---|---|
| `./pp team start <name> --message "…"` | reads the declaration, creates the agents the house lacks, opens the first task; without `--message`, the team starts with no task and waits for its ceremonies and your posts |
| `./pp team post <name> --message "…"` | adds a task, an info, a reply or a stop at any time; `--name` names a task; `--task <id> --ask` asks a member of that task a question it owes an answer to |
| `./pp team stop <name>` | stops the open tasks; `--kill` also ends the wake-ups under way |
| `./pp team pause <name>`, `./pp team resume <name>` | holds the team: nobody is woken until it resumes |
| `./pp team resume <name> --task <id>` | takes back a task a limit had stopped; `--to <member>` or `--to all` chooses whom the resume tells |
| `./pp team resume <name> --quota` | lifts a provider's usage limit before its hour, or when the provider gave none; `--member <member>` lifts one member's only |
| `./pp team reset <name> --member <member>` | gives a member a new run at its next wake-up |

### The tick moves the team

`./pp team tick <name>` advances the team once: it collects the wake-ups that ended,
routes each act a member said to the member it is for, judges who waits for whom and
launches the next wake-ups. The end of every wake-up triggers the next tick, and the
NET catches a tick that died: a TIMER the tick arms at its end when something is due --
a process that sleeps until the deadline, ticks once and dies, one per team, none when
nothing is due. `schedule:` of `TEAM.md` says its step, how long it sleeps at most: `10s`,
`2m`, `1h` or a bare number of minutes, 5 minutes unless said, `off` for none. The timer
dies with the machine; ONE relaunch entry per house brings back every team that needs it
when the user opens a session (`@reboot` in the crontab on Linux, a value of the user's Run
key on Windows).

### One act for each message

A member speaks in acts -- a JSON value alone, one element or a list of them, that it hands to pp
by its print call, read as soon as it is taken, while the member still works. The team reads
nothing else: the last message of a launch is never an act. With its acts, a member hands work to the members
who report to it (`do`), asks a question of anyone in the team or of you (`ask`), or
answers a message it received (`{"re": <id>, "text": "…"}` -- « re » means « in answer
to »). Every `do` and `ask` a member receives is a debt: the member owes that message one
answer, in the same wake-up or a later one. The member that holds a task closes it by
answering the message that opened it, with the result; a member who only took part never
closes a task.

A member that puts an answer off is not forgotten. When the team stands still -- everyone
waiting for someone who waits too, or for a member that has nothing left to read -- the tick
reminds the member at the bottom of the chain that it still owes an answer, as long as it owes.
A member that stays SILENT -- `silence:` exchanges without one act, an `info` counts -- gets one
reminder, then is suspected as a failing member is: the tick answers in its place to the members
waiting for it, and a task you opened that its member leaves silent comes back to you: the team
sends you a notice. A member that says where it stands is never stopped by a count.

A member that keeps failing -- a model that errs, a program that crashes -- may be broken, or only
down for a while. The tick does not wait for it, and does not give it up either. Once a wake-up
of the member has failed for good, the member is suspected for a while: 5 minutes, or the
step of the team's schedule, doubled each time it fails again and never past `suspect-max:`
(10 minutes unless said). During that time no member wakes it: whatever a member asks of it
gets an answer from the tick in its place (« r2 is not answering at the moment; it is tried
again at 14:20:05 »). What YOU say to it -- a task, an info, an answer -- reaches it at once: the
tick launches it on your word, and that launch is its try. After that time, its next message
tries it again. If it answers, it is trusted again. Every other member reads, at the top of its
message, who is not answering at the moment. `./pp team resume <name> --task <id>` and a new
`./pp team start` trust it again at once. A launch the house itself refused before the
member's program ran -- a package missing, a run held -- counts against nobody: the member is
launched again at the next tick, and you get one notice.

### Limits that hold

The declaration may bound the team: `parallel` (launches at once), `budget` (dollars
since the start; each launch gets its share of what is left), `budget-launches` and
`launches` (launches of the team and of one task), `retries`, and `timeout` (a launch
stuck longer is ended). When a limit is reached, nothing more is launched and the team
sends you a notice. `./pp team budget <name> <usd>` raises the budget without a
restart.

### Ceremonies

A ceremony is a recurring task: `daily every weekday 09:30 with r1 r2 -> lead`. The
tick rings it once per period; `./pp team ring <name> <ceremony>` rings it at hand.
`any <n>` sets a quorum: the facilitator is woken at the n-th answer.

A task can recur too, without a meeting:
`./pp team post <name> --message "review the PRs" --to w --every "weekday 09:30"`. The tick
opens one task per period. It opens none while the one before is still open. `--every 4h`
makes it come back every four hours instead, the first task at once.
`./pp team recurrence <name> R1 --every "weekday 14:00"` changes its hour, and
`--message "review the PRs and the issues"` its text;
`./pp team recurrence <name> --task T3 --every "mon 09:00"` makes a task you posted once come
back;
`./pp team stop <name> --recurrence R1` ends it. `--context 70%` gives it a context limit:
once the member's run of the recurrence has used 70 % of its context window, the next task
of the recurrence starts in a new run.

### Following a team

| command | what it says |
|---|---|
| `./pp team status [<name>]` | the members, their runs, the tasks, the limits, the cost and what waits for you |
| `./pp team watch <name>` | the team's events as they happen |
| `./pp team log <name>`, `./pp team result <name>`, `./pp team responses <name>` | the journal, the result of a task, the members' answers |
| `./pp team inbox` | what waits for you: questions without an answer, the team's notices, tasks done, messages returned |
| `./pp team stats <name>` | the numbers of one season, read from the journal alone: its tasks, its cost, its times, its losses; `--all` every season, and each task over all its seasons |

`status`, `log`, `responses`, `inbox`, `stats` and `watch` take `--json`, the form a program
reads -- the [`ui`](../ui/README.md) package reads them. In `status --json`, each task
says the hour it was born (`at`) and the hour it ended (`ended`, null while it is open), and
each member says its role keys (`roles`). What waits for you also
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

After a restart, the teams come back by the house's ONE relaunch entry: on Linux an
`@reboot` line in the user's crontab, so `cron` must be running (under WSL: `sudo service
cron start`); on Windows a value of the user's own Run key, which needs no administrator
rights. If the entry cannot be written, the teams run on without it, and you get a notice
that says why.

## Quick start

Declare a team from a template, start it with its first task and follow it:

```sh
./pp team declare review --template teams/lead-reviewers \
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

## Reference

This section states the package in full: every key, verb, event, field and refusal, by
topic.

- [The declaration](#the-declaration)
- [The journal](#the-journal)
- [Starting a season](#starting-a-season)
- [Posting, stopping, taking a task back](#posting-stopping-taking-a-task-back)
- [Pausing, raising the budget, resetting a member](#pausing-raising-the-budget-resetting-a-member)
- [The tick](#the-tick)
- [Acts, debts and waits](#acts-debts-and-waits)
- [Deadlocks and relances](#deadlocks-and-relances)
- [Members that fail](#members-that-fail)
- [Notices of the team](#notices-of-the-team)
- [Limits](#limits)
- [The schedule and its net](#the-schedule-and-its-net)
- [Ceremonies](#ceremonies-1)
- [Entries and the team's directory](#entries-and-the-teams-directory)
- [One run per task](#one-run-per-task)
- [Task names](#task-names)
- [Templates](#templates)
- [Reading a declaration](#reading-a-declaration)
- [Following a team](#following-a-team-1)
- [The faces](#the-faces)
- [Routes and answers](#routes-and-answers)
- [Names and paths](#names-and-paths)

### The declaration

A house that pins the `team` package has **teams**. The owner DECLARES each team at
`teams/<name>/TEAM.md`. Its front matter says who the team is and how it is bounded; its
body is the owner's word to the team, served to every member. `team declare` writes it
([`team declare`](#team-declare)); you may also edit it by hand.

#### The keys of `TEAM.md`

| key | what it holds |
|---|---|
| `agents: |` | the MEMBERS, one `<name> <path>` per line: the member's name, then the path of the agent under the house that plays it, or `.` for the house itself. One path may play several members at will. A member may not take the house's own name. |
| `reports: |` | who reports to whom, as edges `a b c -> d` |
| `root` | the member that receives a task |
| `principals: |` | the mandators allowed to post. The owner, the house's slug, is always admitted. |
| `ceremonies: |` | the ceremonies to come, read for their names, their participants and their `after` graph ([Ceremonies](#ceremonies-1)) |
| `template` | the team preset the team is shaped by, `teams/<t>` ([Templates](#templates)) |
| `values: |` | the values the preset and the documents declare, `<name> = <value>` per line ([Templates](#templates)) |
| `roles: |` | the role keys, `<key> [<member> ...]` per line ([Role keys](#role-keys)) |
| `documents: |` | the documents each member receives, `<key> <document> ...` per line ([Documents](#documents)) |
| `name` | the name the team is shown by: one line of 1 to 80 printable characters, read at every call. A rename moves nothing: the directory is the team's identity. |
| `description` | what the team does: one line of 1 to 200 printable characters, read at every call |
| `schedule:` | the step of the team's net ([The schedule and its net](#the-schedule-and-its-net)) |
| `entries:` | the document a wake-up plays on each trigger ([Entries and the team's directory](#entries-and-the-teams-directory)) |
| `parallel`, `budget`, `budget-launches:`, `launches:`, `retries:`, `timeout:` | the limits ([Limits](#limits)) |
| `silence:` | the silent exchanges that earn a member one reminder, 3 unless said ([Deadlocks and relances](#deadlocks-and-relances)) |
| `suspect-max:` | the longest suspicion of a failing member ([Members that fail](#members-that-fail)) |

`work:` is the season's: in `TEAM.md` it refuses `key-moved`, naming `SEASON.md`
([The season's values](#the-seasons-values)).

#### The owner's word and the team's document

The body of `TEAM.md` is the OWNER'S WORD. pp serves it to every member as it stands -- no
hole is filled -- and reads it again as soon as it changes, with no new start. A `TEAM.md`
without a body serves nothing.

`teams/<name>/TEAM-<name>.md` is the TEAM'S DOCUMENT. Every `team start` renders it whole,
head and body; it is pp's, never edited by hand.

- Its head is attached at the kit's `turn.begin` (`proc: SERVE`). It serves the document
  itself, then `TEAM.md` when its body says something, then the package's `TEAM_WORK.md` (how
  a team works), then `SEASON.md` when its body says something, then every
  `TEAM-<name>-<x>.md` standing in the directory, by name. A document whose front matter
  declares `mount:` is mounted by the engine instead of served.
- Its body is the INTENTION of the template `TEAM.md` names, each hole filled by the team's
  values; it is empty without a template.

`team start` refuses `rendered-edited` when the document it rendered last was edited since,
and `intention-misplaced` when a `TEAM-<name>.md` no start rendered holds another body: the
owner's words go in the body of `TEAM.md`, and pp moves nothing.

The engine serves each body at a member's opening, and again at the exchange after it
changes, under the same key. The intention is never copied into a message nor into the
journal.

`team status` says `TEAM.md changed since the start` when the declaration differs from the
start's `digest`.

#### The season's values

`teams/<name>/SEASON.md` is the owner's file for the SEASON: what a start plays, beside what
`TEAM.md` says the team is. Every `team start` reads it. Its front matter may say:

- `template:`, a SEASON preset (a template with `documents:` and no `form:`, `members:` nor
  `reports:`), `values: |` and `documents: |` -- the documents and values the season adds to the
  team's;
- the season's launch: `provider:`, `harness:`, `model:`, `permissions:`, `effort:`;
- its limits: `budget:`, `budget-launches:`, `silence:`, and `context:` (`<n>%`, the context
  limit of a task that has none of its own);
- `packages: |` (`<name>=on|off` per line), `profiles: |` (`<member> <key>=<value> ...` per
  line) and `work:` (the repository every opening clones).

Its body is the owner's word for the season, served like the body of `TEAM.md`. `team start`
without a flag opens the season the file writes; a flag of `start` covers its key and is
written into the file, key by key, the rest kept to the byte. `team declare --season` writes
it too. A key the file may not say refuses `season-invalid`.

#### Role keys

`roles: |` of `TEAM.md` gives the team ROLE KEYS, one `<key> [<member> ...]` per line: a key
is the owner's own word, a slug, and its members are declared members. pp deduces no key from an
edge, the root or a name. A key chooses documents, never a right: a line of `documents:` names
the key it reaches. A line that names a key `roles:` does not declare refuses `role-unknown`. A
team preset's `roles:` names places of its form (`{root}`, `{others}`, ...): `team declare`
fills them with the team's members once, at the birth, and writes the lines into `TEAM.md`.
`status --json` says each member's keys (`members[].roles`).

#### Documents

`documents: |`, in `TEAM.md` and in `SEASON.md` with the same grammar, says what each member
receives: one `<key> <document> ...` per line, the key `all` for every member, a role key for
the members who hold it. A document is a template the house sees, `<directory>/<name>`, or a
file `<name>.md` of the team's directory. `SEASON.md`'s lines are added to `TEAM.md`'s for the
season. `team start` renders each one, its holes `{<name>}` filled by the values: a document
of `all` at `teams/<name>/TEAM-<name>-<document>.md`, served to everyone; a document of a role
under `teams/<name>/roles/`, mounted in the runs of the members who hold that key. A document
that is neither a template nor a file of the directory refuses `document-unknown`; a file of
the directory with a hole refuses `document-holes`.

#### The contract of the acts

The rules every member follows -- the acts it may say, the answer it owes -- are the
package's fragment of the standing orders, `packages/team/system/SYSTEM.md`. That
fragment is compiled into every marble of the house (see
[The marble, in layers](../../docs/reference/instance.md#the-marble-in-layers)).

#### Deleting a team

`team delete <name> [--agent <path>]... [--yes] [--json]` removes a team and what it made:

- its timer;
- its relaunch entry;
- every run its wake-ups opened (`agent purge`, once `deleting` lets the guard go);
- its journal;
- `teams/<name>/`.

The agents are left standing, unless `--agent <path>` names one: it is then taken away
with the team by `agent remove` -- its runs purged, the files pp wrote in its directory and
its instance removed, its directory when nothing else stands in it. Only an agent the team
alone declares may be named: the dry run lists them under `agents`; another one refuses
`agent-shared` before anything is written. While a task is open, the command refuses
`team-busy`.

#### Renaming a team

`team rename <name> <new> [--json]` moves the team to `teams/<new>/` -- the name every verb
and the post address it by -- with its journal and the files beside it; the intention
`TEAM-<name>.md` becomes `TEAM-<new>.md`, and `name:` of `TEAM.md` is rewritten when it was
the old directory's name (a name of your own stays). It plays on a team at rest: a task
open or a wake-up under way refuses `team-busy`, a name taken `team-exists`, a name that is
not a slug `team-invalid`. The timer is disarmed and armed again by the next tick; the
relaunch entry does not change; the members' entries are laid again at the next start.

### The journal

The team's state is its JOURNAL, `.pp/.sys/records/teams/<name>/journal.jsonl`. It holds one
event per line, `{at, id, kind, team, …}`, each id being the previous one + 1.

`pp-team` alone writes it, appending under the record's lock. It is never rewritten, and it
is read again at every reading. A last line still being written is skipped; a torn line
anywhere else makes the reading refuse, by its name.

#### Snapshots

`./pp team snapshot <name>` writes ONE `snapshot {upto, state}` event under the journal's
lock: the replayed state, packed as JSON. The resolved tasks' messages are pruned from it;
the posts returned to the owner are kept by their ids.

Every state reader -- the tick, `status`, `responses`, `inbox` -- parses the journal from its
last snapshot line on and restarts there. `log` and `watch` read the whole history and never
show the snapshot. Nothing is rewritten: `status` renders the same bytes before and after.

#### Journals written by earlier versions

The code still reads older journals:

- A journal written before team 0.33.0 reads as written. Its `delegation` and `terminal`
  events still count, and a member's `done` or `escalate` to the member that delegated is
  read as the answer to that member's last `do`.
- `log` and `watch` say such a journal in today's words: a member's `done`, `reply` or
  `escalate` as `re` (`was` gives its old verb), an `escalate` to a principal as the team's
  `notice`. They never show `delegation` nor `terminal`, which the replay still reads.
- A journal written before team 0.40.0 keeps no rank: the tick routes nothing of the
  exchanges before it.
- A `launch.max_budget_usd` that an older journal kept is never passed on; `status` says so
  once.

### Starting a season

```
./pp team start <name> [--message "<text>" [--to <member>] [--name <text>]] [--budget <usd>]
    [--budget-launches <n>] [--context <n>%] [--silence <n>] [--provider <name>] [--harness <command>]
    [--model <m>] [--permissions auto|strict|bypass] [--effort low|medium|high|xhigh|max]
    [--package <name>=on|off]... [--no-tick]
    [--member <member> [--provider|--model|--effort|--permissions|--silence <v>] [--package <name>=on|off]...]...
```

`team start` opens a SEASON of the team: the first one, or the next once `team stop` ended the
last. In season it refuses `season-running`, naming `team stop`.

#### What start refuses

`team start` reads the declaration whole -- `TEAM.md`, `SEASON.md`, the preset, the documents
-- and refuses before anything is written:

| refusal | when |
|---|---|
| `season-running` | the season under way was not stopped |
| `team-unknown`, `team-invalid`, `season-invalid`, `name-invalid`, `root-missing`, `participant-unknown`, `ceremony-cycle`, `budget-invalid`, `context-invalid`, `package-invalid` | the declaration or the flags fail the judge, as named |
| `key-moved` | `TEAM.md` says `work:`, which belongs to `SEASON.md` |
| `template-unknown`, `template-invalid`, `value-unknown`, `value-missing`, `role-unknown`, `document-unknown`, `document-holes`, `document-collision` | the preset, the values, the role keys or the documents cannot shape the team |
| `rendered-edited`, `intention-misplaced` | a document pp renders was written by hand ([The owner's word and the team's document](#the-owners-word-and-the-teams-document)) |
| `entry-missing` | an entry stands neither in the team's directory nor in the instance of an agent whose members play it |
| `package-required` | a member switches off `team` or a package it requires, read from the manifests |
| `package-unpinned` | a package the house does not pin is switched on (switched off, it asks nothing) |
| `package-dependency` | a package is switched on while the same composition switches off a package it requires |
| `born-busy` | the birth lock of a path is held past `call_lock_wait` |

#### The season's own settings

The season's `--budget` and `--budget-launches` stand above those of `TEAM.md`. They are kept
at `team-started.season`; `TEAM.md` is left untouched. Each flag of `start` is also written
into `SEASON.md`, key by key, so a later start without flags opens the same season
([The season's values](#the-seasons-values)).

The flags after a `--member`, up to the next one, are that member's profile, kept at
`team-started.profiles`. They replace the team's provider, model, effort or permissions for
that member.

#### The season decides the packages

In a team, the season decides which packages a member plays, never the member's own
`SETTINGS.md`. `team start` writes the SET of each member's packages: one `<name>=on|off`
for every package the house pins beyond its base.

- A package is `on` when the season switches it on, or when the team requires it (`team`
  and what it requires).
- Every other package is `off`.
- `--package <name>=on|off` before the first `--member` is the team's. A member's
  `--package` covers the team's, name by name.
- A season that names no package gives every member the packages the team requires, and
  nothing else.

The set is kept whole at `team-started.packages`, and at the `packages` of a profile that
names some. Every wake-up hands the whole set to the member's `agent start`: a run's
opening composes its first block with it, and a resume plays what the run does not hold
yet. A member therefore plays its season from its first block, whatever its agent's
settings say.

A package switched on whose requirement the set switches off refuses `package-dependency`
before anything is written: `--package doc=on` needs `--package steering=on` beside it.

A journal written by team 0.49.0 to 0.51.0 lists only the packages its season named. It is
read under the same rule: a package it does not name is off.

#### What a season keeps

A season keeps the members' runs, keys and sessions, the tasks, their waits and their
failures. It counts afresh the cost, `budget-spent`, `budget-launches` and each task's
`launches:`. A task that a final failure left blocked is taken back by `resume`.

#### What start writes

`team start` creates the agents the house lacks, at their paths. Each path is born once,
under the house's birth lock for that path (`state/born-<digest>.lock`, the same lock
`agent add` takes). Each new agent borrows the house's machine.

It then writes `team-started`. Under `--message` it also writes the task `T<n>` and its `do`
post from the owner to `--to`, or to the root.

Without `--message`, no task opens. The season stands on its ceremonies and on the posts to
come, and the team is `idle`. The relaunch entry is laid at the start only when a task is
open or a ceremony is declared; otherwise the first post lays it.

### Posting, stopping, taking a task back

`start`, `post` and `stop` tick right after their write; `--no-tick` spares that tick.

#### `team post`

```
./pp team post <name> [--message …] [--to <member>] [--task <id> [--ask] | --name <text> [--context <n>%]] [--reply <id>] [--stop] [--as <principal>] [--every "<when>" [--context <n>%] [--description <text>]] [--no-tick]
```

`team post` adds a new task, or an `info`, a question, a `reply` or a `stop` on a standing one.
`post --reply <id>` writes the principal's answer, a `re`. `post --every "<when>"` lays a
recurring task instead ([Recurring tasks](#recurring-tasks)).

`post --task <id>` alone writes an `info` to `--to`, or to the task's member: it waits for no
answer. `post --task <id> --ask` writes an `ask` instead: the principal's QUESTION to that
member. The member owes it an answer, and its `re` settles it; `team stats` counts these
questions apart from the members' own (team 1.35.14). `--ask` without `--task`, or beside
`--reply` or `--stop`, is the usage, and nothing is written.

`--context <n>%` on a post that opens a task gives that task its context limit: once the
member's run on the task stops with its last measure at or past it, the next wake-up opens a
new run (`run-renewed`).

| refusal | when |
|---|---|
| `task-closed` | the task is stopped or resolved |
| `principal-unknown` | the name is neither the owner nor a mandator |
| `every-invalid` | the period is neither `day`, `weekday` or a day of the week, then `HH:MM`, nor `<n>m`, `<n>h` or `<n>d` |
| `context-invalid` | the context limit is not a whole number from 1 to 99, with or without `%` |

#### `team stop`

```
./pp team stop <name> [--task <id>] [--kill]
./pp team stop <name> --recurrence <R<n>>
```

`team stop --recurrence R<n>` ends a recurring task: no new task opens for it. The task it
opened last, if still open, goes on; `--task` stops it. `recurrence-unknown` names no
recurrence of the team; `recurrence-stopped` names one already ended.

#### `team recurrence`

```
./pp team recurrence <name> <R<n>> [--every "<when>"] [--context <n>%|off] [--message <text>] [--as <principal>] [--no-tick]
./pp team recurrence <name> --task <T<n>> --every "<when>" [--context <n>%] [--as <principal>] [--no-tick]
```

`team recurrence` changes when a recurring task comes back -- its day, its hour, both, or
from a day and an hour to a duration and back --,
its context limit, or its text; give one of `--every`, `--context` and `--message` at least.
`--context off` takes the limit away. A new text applies to the tasks the recurrence opens from
now on; a task it has already opened keeps the text it opened with. To tell the member of
that task, post an `info` on it. The recurrence keeps its id, its member and its name; to
change one of those, stop it and post a new one. A day is counted once: if the task already
opened today, the new hour starts at the next day it applies to. A duration given this way
starts one duration after the change, never at once. A new limit applies from the next task
of the recurrence.

With `--task T<n>` instead of an id, `team recurrence` makes a task that exists come back: a
NEW recurrence, with that task's member, text and name; you are its principal. The task
itself counts as the recurrence's last task: while it is still open, every period passes
without opening anything, so the member never holds the same work twice. Once it is closed,
the next period opens a task in a new run of the member. A task already closed is accepted:
« do that again every Monday ». `--every` is required; the text comes from the task, so
`--message` is refused.

| refusal | when |
|---|---|
| `recurrence-unknown` | no recurrence of the team has that id |
| `task-unknown` | `--task` names no task of the team |
| `task-recurrent` | `--task` names a task a recurrence or a meeting opened |
| `message-missing` | `--message` is empty |
| `recurrence-stopped` | the recurrence was stopped |
| `every-invalid` | the period is neither `day`, `weekday` or a day of the week, then `HH:MM`, nor `<n>m`, `<n>h` or `<n>d` |
| `context-invalid` | the context limit is not a whole number from 1 to 99, with or without `%`, nor `off` |
| `recurrence-unchanged` | every value given is the one in force already |

`team stop` stops one task, or every open one. It posts the `stop` to every agent holding
the task: the task's agent unless it answered the opening, and each delegate that has not
answered its last `do`. It returns the posts left undelivered on the task.

The stop is delivered at once. A wake-up under way is not interrupted: it ends, its answer
is reaped and routed nowhere, and no agent is woken for the stop.

`--kill` ends, now, every wake-up under way on the task that has not answered: the launcher,
the harness and what it runs, all at once. It writes `wake-killed {tag, agent, task, run,
pid}`. Nothing is kept, nothing is retried, and the stop counts as delivered.

A wake-up that has answered is spared; the tick ends it and counts its cost. Whether it has
answered is read as the reap reads it: by (run, index), then without a run under the key
handed. A `stop --kill` ends the wake-up of its own task alone: the member keeps its key for
its other tasks.

A task stops whatever holds it. Every stop writes `stopped {task, by}` before its posts. A
task nobody holds any more stops without any post (`stopped -- nobody held it`), and the
team is free to start again.

#### `team resume --task`

`team resume <name> --task <id> [--to <member>|all] [--message <text>] [--as <principal>] [--no-tick]`
takes back ONE task that a guard left with nobody due: a task stopped, held by a member's final
failure, past `launches:`, a member halted on it, or a member of it held by a provider's limit
that gave no hour.

It is judged under the journal's lock. It refuses `member-unknown` (`--to` names no member of
the season), `task-unknown`, `task-resolved`, `budget-spent` and `task-not-blocked`. `--to`
without `--task` is the usage.

It writes `resumed {task, by, from}` -- `from` the causes it lifts, among `stopped`, `failed`,
`launches-spent`, `halted` and `quota` -- and an `info` to each member it revives:

- the holders at the stop;
- the members whose final failure stands;
- the members halted on the task;
- the members a limit without an hour holds;
- the members with messages due past `launches:`.

`--to <member>` aims that `info`: it goes to the member named alone, and `--to all` sends it to
every member of the season (team 1.35.13). The text is `--message`, `the task resumes` unless
said.

The replay opens the task again. It counts the task's failures and its `launches:` from that
event, and drops the `terminal` that a final failure wrote. A resume never resets the team's
`budget` nor `budget-launches`, and the posts returned at the stop stay returned.

The next tick wakes each revived member in its run, under its key.

#### `team resume --quota`

When a provider says a member reached its usage limit, the reap writes `quota-reached {agent,
task, until, said}` instead of an end: no failure, no retry, no suspicion. The member's messages
go back to its inbox and the tick launches it on no task until `until`, the hour the provider
gave -- the timer wakes the team then. A limit without an hour holds until `team resume --task`
takes back a task the member is on, or until `team resume --quota` lifts it.

`team resume <name> --quota [--member <member>] [--as <principal>] [--no-tick]` (team 1.35.11)
lifts that limit at once, dated or not: the limit of the member `--member` names, else of every
member a limit holds now. It is judged under the journal's lock:

| refusal | when |
|---|---|
| `team-not-started` | the team was never started |
| `principal-unknown` | `--as` names neither a mandator nor the owner |
| `member-unknown` | `--member` names a member the season does not know |
| `quota-not-held` | no provider's limit holds that member, or any member |

`--quota` beside `--task`, `--recurrence` or `--message`, and `--member` without `--quota`, are
the usage. It writes ONE `quota-lifted {by, members}`, lays the relaunch entry again, then
ticks unless `--no-tick`: each member lifted is launched on what waits for it. It resumes no
task: a task a guard holds is taken back by `resume --task`.

### Pausing, raising the budget, resetting a member

#### `team pause` and `team resume`

`team pause <name> [--as <principal>]` PAUSES the team. It is judged under the journal's
lock and refuses `team-not-started`, `principal-unknown` or `team-paused`. It writes
`paused {by}` and kills nothing: the wake-ups under way end on their own, and the tick reaps
them and routes their answers.

`team resume <name> [--as <principal>] [--no-tick]` ends the pause by writing
`unpaused {by}`; on a team not paused it refuses `team-not-paused`. Until then, the tick
writes no `wake-intent` and no `ceremony-due`; the pause is judged under the journal's lock
at each write.

During a pause, `post`, `stop`, `ring`, `budget`, `resume --task`, `reset` and a season write
as ever. The tick they play says `paused: nobody woken until team resume`. A season keeps
the pause.

The resume's tick does what is due at that moment. Each member due is woken in its own run.
A ceremony's period of the day rings when its hour is past and it never rang; a period that
passed during the pause never rings.

`status` says `paused since …`; its face says `state: paused` and `paused {by, at}`. The
relaunch entry stays.

#### `team budget`

`team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]` RAISES the
team's `budget` or `budget-launches`, without a start. It is judged under the journal's
lock:

| refusal | when |
|---|---|
| `team-not-started` | the team was never started |
| `budget-invalid` | the new bound is at or below what the team spent since its start |

It writes `budget-raised {budget, launches, by}`. The replay takes the new bounds and lifts
`budget-spent`. The members keep their runs, and the next tick wakes the members due in
them.

#### `team reset`

`team reset <name> [--member <m>]` makes the team forget every run of a member. The agent's
console plays `-reset <key>` for each, and one `run-reset {member, run}` is written per run. It is judged first under
`tick.lock` and refuses `team-busy` or `member-running`. The member's next wake-up opens a
new run ([One run per task](#one-run-per-task)).

### The tick

`./pp team tick <name>` ADVANCES the team. It is one short process.

#### The tick's lock

The tick runs under `tick.lock`, beside the journal, taken without waiting. When the lock is
held, the tick posts the mark `tick.pending` and leaves. The holder clears the mark, plays,
releases the lock, then reads the mark and plays again when it is set.

#### What one tick does

1. It reaps the wake-ups that ended.
2. It routes the ACTS the members said ([Acts, debts and waits](#acts-debts-and-waits)).
3. Before it wakes anyone, it breaks a deadlock ([Deadlocks and relances](#deadlocks-and-relances)).
4. It judges the waits.
5. It launches the next wake-ups.

The end of every wake-up ticks by `--on-end`. The schedule's net catches a tick that never
came ([The schedule and its net](#the-schedule-and-its-net)).

#### Reaping

The tick finds a launch by its `wake-launched` event, or by its tag at `messages.jsonl`; it
finds the response by (run, index). The reap judges the wake lock first, then reads the flow,
since a launch that is over wrote its end before it gave the lock back. So a launch that
ended is never taken for dead, and a kept answer is never killed.

A wake lock free without a response is a dead wake-up: it gets one retry, then it is
`final`. The tick then answers, in the member's place, every message of that wake-up that
owes an answer -- never a principal's opening.

For the root, the team's `notice` goes instead to a PERSON who has a box: the member that
delegated the task, else the task's principal; the owner when the team itself wrote the
task, as for a ceremony's task.

#### Reading a launch's flow

A wake-up is ONE launch (`agent start --launches 1`). The tick reads the launch's flow from
the exchange the launch OPENED. That exchange is found by the tag the house writes at its
`opened` (`agent start --tag`), looked for from the rank the journal last kept of the run.

The acts are read in that flow three ways: by `agent flow --from --follow` while the launch
plays, by the launch's FOLLOWER `team follow`, and again by the reap after it. Each act is
routed once, by its rank: `wake-routed`.

The launch's end is read at the flow too: `wake-ended {run, launch, state, cost, context, tokens}`.
Its `state` is what the house said of the run at `--on-end`: `standing` or `parked`. A
`standing` run is relaunched as soon as its wake lock is free, with `[nothing new]` at its
head when nothing is due. Its `context` is the last measure of the member's context that the
flow of the launch said, `{tokens, used, window}` as the house said it, or `null` when the
launch measured nothing. So the member's context can be read when it is at rest. Its `tokens`
is what the calls of the launch sent the model, added up, or `null` when the harness does not
measure it (team 1.35.12).

#### Launching a wake-up

The tick launches by the house's [console](../../docs/reference/console.md), in three
writes:

1. `wake-intent`, written FIRST;
2. `agent start --tag --on-end "<engine> --instance <house> team tick <name>"`, with
   `--run` to resume the agent's run on that task and the flags `team start` was given.
   `--harness` and `--provider` go together, the provider naming the grammar in which
   `pp-agent` reads the command's output;
3. `wake-launched`.

See the [`agent`](../agent/README.md) package for `agent start`.

#### The message of a wake-up

The message opens on the head line `[team <name> · you are <member>]`
([Names and paths](#names-and-paths)). Then come:

- the agent's inbox: each message as its head line, such as
  `#163 DO from supervisor on T8 -- you owe an answer`, with its text indented under it;
- the messages it still owes from earlier wake-ups;
- the contract: the three forms and the debt.

The team's intention is served by pp, never in the message.

What the others answered reaches a woken agent as ONE line. The head of its message names
each response other agents gave since its last wake-up in the team, by agent, task and
journal id. The cursor is its last `wake-intent` -- the journal's own cursor, nothing written.
The line gives the house console's absolute path and `team responses <name> --since <id>`.

While a member is suspected, every other wake-up's head says so after its first line:
`[not answering at the moment: <member> -- tried again at HH:MM:SS]`.

### Acts, debts and waits

#### What an act is

A member's ACT is a production of the engine's FORMAT mechanism (see
[The form of a said production](../../docs/reference/block.md#the-form-of-a-said-production)).
The format is `team-act`, declared once by the team package in `procs/TEAM-ACT.md`, mode
`words`: the value alone, no head.

An entry's step names the format (`INFER team-act => terminal`: the member hands the value by its
print call). The contract of the standing orders, `system/SYSTEM.md` of the package, describes it. The engine prescribes the
form and judges nothing of it.

There is no law: a message is a `words` -- a production the member handed to pp by its print call
(team 1.35.10). A text it wrote between two calls is no message, and neither is the last message
of its launch. Every JSON object of a `words` that
carries the key of a form (`do`, `ask`, `re`) -- given alone as the contract asks, or found among
other text -- is an act, routed in its order; an act printed twice is routed twice. An act whose form is broken (cut short, a key its form does not carry,
a value of the wrong kind) is refused and the member is told why, as for an act whose sense is
wrong. A `words` without an act is SAID: it is routed to nobody and fails nothing.

| act | where it goes |
|---|---|
| `{"do": …}` | along the `reports:` edges: one `do` post per delegate, plus the `wait` of its `await` |
| `{"ask": …}` | to any member, or to a principal |
| `{"re": <id>, "text"}` | the answer to the message `#<id>` delivered to the member; it goes to that message's author |
| `{"info": {"to": …, "text"}}` | a piece of information to any member or principal (team 0.47.0): it opens no debt and holds no wait; a member's info launches nobody and rides the head of its recipient's next launch, a principal's wakes; to a principal it reaches their inbox at once |

#### Refused acts

An act whose sense is wrong is REFUSED at the routing: the tick writes `wake-refused` and
sends an `info` to the member, and the launch goes on. An act is refused when it names a
member nobody declared, when it is a `do` off the edges, or when it is a `re` citing a
message never delivered or citing an `info`.

#### Debts

Each `do` and `ask` delivered to a member opens ONE debt. The first answer that cites it
settles it; a later answer is posted as `info`.

The ROOT's answer to its task's opening:

- writes `done` with its text;
- settles every debt of the task;
- writes a `returned` for every post left undelivered on the task;
- writes `schedule-off`.

The root speaks to its principal by its own elements alone: `ask`, and the `re` to the
opening that closes the task.

#### Waits

A delegating member waits for its delegates. `wait-met` is written when every delegate has
answered its `do`. Every message except an answer to the round's `do`s and to the task's
opening passes an open wait.

The wait is the agent's to shorten. An answer that delegates may carry
`"await": {"any": n}`: the tick then relaunches the agent once n of that act's delegates
have answered, instead of all of them (`wait` at the journal). An `await` without a number
is refused at the routing.

### Deadlocks and relances

Before it wakes anyone, the tick breaks a DEADLOCK. It builds the wait-for graph of the open
tasks: a member waits for the members whose answer it awaits, and for a principal whose
reply to its question it awaits.

The greatest set of idle members -- no wake-up under way, nothing to receive -- whose every
wait stays inside the set is deadlocked (Chandy, Misra, Haas, 1983).

A member at the bottom of that set (waiting for nobody, or in a knot) that owes an answer is
RELANCED: it gets a wake-up with no new message, and its intent carries
`relance: "owed" | "cycle"`. No count bounds the relances (team 0.48.0): what bounds a long task
is `launches:`, `budget:` and `budget-launches:`. A member whose run STANDS on the task is
not relanced but CONTINUED (team 0.54.1): its run is relaunched with `[nothing new]` at its
head and its debts under `[you still owe an answer to]`; the relance plays only where that
continuation launched nothing -- its wait on the task holds.

What the tick watches is the member's SILENCE: its exchanges that end without one act (a `re`, a
`do`, an `ask`, an `info`) while it owes. At `silence:` such exchanges (3 unless `TEAM.md` says;
`team start --silence <n>`, `--member <m> --silence <n>`) the relance is a REMINDER
(`relance: "reminder"`), its head asking an answer or an `info`; one more silent exchange and the
member is SUSPECTED, as a failing member is ([Members that fail](#members-that-fail)): the tick
answers in its place to the members waiting for it, and a root's principal gets the team's
`notice` about it. A member that acts at every exchange is never reminded.

### Members that fail

The tick is a failure detector (Eventually Perfect, Chandra and Toueg, 1996), read from the
journal alone.

#### Suspicion

A member whose final failure stands -- on a task not stopped, with a reason other than
`budget-share` -- is SUSPECTED for an interval counted from the hour of that failure.

The interval's base is the step of the team's net in seconds (`schedule:`), 5 minutes
without it or under `off`. It doubles at each final failure in a row and never goes past
`suspect-max:` (10 minutes without it).

During the interval:

- no member wakes the suspected member;
- each tick answers in its place every debt it owes to a member, and every `do` or `ask` of
  a member that reaches it (`re`, `by: tick`, `suspected: true`, « no answer: <member> is not
  answering at the moment; it is tried again at HH:MM:SS »);
- what a PRINCIPAL says to it -- a task, an `info`, a `re` -- launches it at that very tick, and
  that launch is its try.

#### The try

Past the interval, the member's next message is its TRY. A member that owes only a
principal's opening is tried by a relance on it (`relance: "tried"`).

A try that fails is final at once and doubles the interval. A try that answers ends the
suspicion, and the member is tolerated one silent retry more (`retries:` + 1 per
repentance).

Nobody is excluded for good. `team resume --task` ends the suspicion of the task's members;
a season ends every suspicion.

#### Launches the house refused

A launch the HOUSE refused before any harness ran -- `agent start` ended without its report
-- is no failure of the member. The tick writes `wake-failed {house: true}`: never final, no
retry spent, no fall.

The member's messages go back to its inbox, and the next tick launches it again. The team
sends the owner one notice per (member, cause).

### Notices of the team

The tick says nothing to a principal in a member's name. Every post of the tick to a
principal is a NOTICE of the team (`{verb: notice, from: <team>}`):

- a guard was reached;
- or the notice is `about` a root that failed for good or is suspected -- by its falls, or by
  its silence (`cause: silence`).

A notice opens no debt. A notice about the root holds its wait on the principal
until the principal's answer cites it.

### Limits

The declaration may bound the tick.

| key | what it bounds | when it is reached |
|---|---|---|
| `parallel` | the wake-ups under way at most | an agent due beyond it is `deferred` and launched by a later tick |
| `budget` | the dollars the team may spend since its start: the sum of the costs its wake-ups reported | nothing is launched, `budget-spent` is written once and the owner gets the team's `notice` |
| `retries` | the wake-ups played again after a dead one, 1 unless said | the wake-up is `final` |
| `timeout:` | the seconds a wake lock may stay held after its launch (the journal's UTC `at` against the real clock) | the wake-up is ended by the kill gesture and FAILS: `wake-failed wake-timeout`, retried under `retries` |
| `launches:` | the launches of one task, retries included | `launches-spent` is written once, the owner gets the team's `notice`, the task is left open |
| `budget-launches:` | the team's total launches, counted from the last `team-started` | `budget-spent {unit: launches}` is written once |

A timeout is never written `wake-killed`: that event stays the owner's `stop --kill`.
`budget-launches:` is the bound that holds when the provider reports no cost.

Every launch that ended counts in the team's cost. `launches:` and `budget-launches:` count
the launches; a `launch-missing` spends no retry.

`team status` says the limits, the cost, each agent's runs and their state, the delegates it
waits for and the owner's inbox.

#### Each wake-up's share of the money

`pp-agent` caps a RUN, and a member's run lives through the team's whole work. So where the
adapter of the launch's grammar declares a cost scope (`COST`), the intent carries an
`allowance`: the wake-up's PART of what the team has left.

    allowance = min((budget - cost kept) / k,  budget - cost kept - allowances of the wake-ups under way)

Here k is the number of wake-ups that may play together, min(`parallel`, the members), so
that k members due together launch together. The allowance is reserved until the wake-up
ends.

`agent start --max-budget-usd` is the member's run cap: what the run spent plus the
allowance. A member due whose rest is all reserved is `deferred {reserved}`.

No cap per wake-up exists. `team start --max-budget-usd` refuses `flag-retired`. Without
`budget:`, no cap goes to `agent start`.

A wake-up that its run cap stopped between two launches -- its response's `error` is
`budget-spent` -- fails `budget-share {share, spent}`, read before its body. It is retried in
its run under `retries:` with a new share; its final notice says the share and the team's
rest.

`status` says `budget <spent>/<cap> USD · reserved <r> · left <l>`; `status --json` says
`budget {cap, spent, reserved, left}`.

### The schedule and its net

The team keeps its own NET: a timer, at every step. Its step is `schedule:` of `TEAM.md`,
read in seconds and kept at `team-started.schedule` with `unit: s`.

| `schedule:` | meaning |
|---|---|
| `5s`, `90s` | a step in seconds |
| `2m`, or a bare number of minutes | a step in minutes |
| `1h` | a step in hours |
| absent | 5 minutes |
| `off` | no net, ever |
| anything else | `team-invalid` |

#### The timer

A tick that ends leaving a deadline arms one detached process, the timer. It sleeps until
the earliest deadline, at most one step away, plays one tick and dies. While it sleeps it
holds nothing of the machine: an `./pp upgrade` plays at any hour, and the tick the timer
plays at its deadline runs the code the machine holds then. A deadline is any of:

- a launch under way (its `timeout:` when one is declared);
- a suspected member with something to deliver;
- a member due but deferred;
- a standing run;
- the next ring of a ceremony.

There is one timer per team (`tick.timer` beside the journal), none when nothing is due, and
it is gone at `schedule-off`. The tick hands each timer a token and writes it in that mark:
the timer knows itself by it, on every system. The journal gets `timer-armed {due}` when a tick arms one where
none stood. A team at rest costs nothing: no tick plays while nothing is due.

#### The relaunch entry

The timer is a process: it dies when the machine stops or the user's session ends. So that
the teams come back on their own, the house keeps ONE relaunch entry for all of them. The
entry plays `team tick --all` once when the user opens a session: one tick for every team
that needs its net, and each tick arms its team's timer again.

| system | the entry | rights |
|---|---|---|
| Windows | the value `pp-team-<12 hex of the house>` of the user's Run key, `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`; its command runs `team tick --all` through `uvw` (uv's launcher without a window) when it is installed, through `<house>\pp.cmd` otherwise | the user's own key: no administrator rights, no elevation |
| Linux, WSL | the line `@reboot <python> <engine> --instance <house> team tick --all # pp-team <house>` in the user's crontab, found again by its mark | `cron` must run (under WSL: `sudo service cron start`); `@reboot` plays when cron starts |

A team needs its net while its `schedule:` is not `off` and a task is open or a ceremony is
declared. `team start` lays the entry when its team needs it and it is absent, and a `post`
that finds it gone lays it again. The tick, `team stop` and `team delete` remove it only when
NO team of the house needs it any more. The entry is laid, and the need judged and the entry
removed, under the house's relaunch lock (`state/relaunch.lock`): the stop of one team and
the start of another at the same moment never take the net of the team that needs it. The
journal gains no event for the entry: the system is the one truth of it.

An earlier version laid one entry per team. On Linux the house's first lay replaces those
lines. On Windows, a task an administrator account laid under team 0.44 is removed by hand:
`schtasks /Delete /TN pp-team\<12 hex>\<name> /F`.

#### When the system refuses the entry

A system may refuse the entry: a company policy that locks the Run key, `cron` not
installed, a crontab that cannot be written. The team starts anyway and runs on its timer;
only the relaunch after a restart is missing. The refusal is said three ways:

- on stderr: `relaunch not laid -- <why>`, rc 0;
- once per season, a `notice` of the team to the owner, in the inbox: what is missing and
  what to do to have it;
- at the face: `relaunch: false` and its `reason`.

`status` says `schedule · every 300 s · timer armed | no timer · relaunch laid | absent (<why>)`,
or `schedule · off`; the face says `schedule {seconds, timer, relaunch, reason}`.

Under `PP_CRONTAB=<file>` and `PP_RUNKEY=<file>`, those files stand for the crontab and the
Run key (the bench, a try); `PP_SCHEDULER=nt|posix` chooses which one the skill writes.

### Ceremonies

The tick RINGS the ceremonies.

#### When a ceremony rings

`start` judges the when of each ceremony line whole; anything else than these two forms is
`team-invalid`:

- `every day|weekday|mon..sun HH:MM with a b -> c`
- `after <other> with a b -> c`

A ceremony is due when its period is due and it has not rung yet in it. Under `every`, the
day conforms and the hour is past, by the house's local clock (`PP_NOW` stands for that
clock at the bench). Under `after`, the followed ceremony's task is resolved.

`ceremony-due` names the period: a ceremony rings once per period, and the journal is the
judge.

#### The ceremony task

A due ceremony becomes ONE ceremony task, from the team to its facilitator: its opening
`do` to the facilitator, and a `do` per participant. The wait gathers the answers, and the
opening waits with them. The facilitator concludes; its answer to the opening is the
result.

A ring names its task `<ceremony> YYYY-MM-DD HH:MM` (its local hour). It says a CONSIGNE,
never the ceremony's declaration line: the facilitator gathers the answers and concludes;
each participant takes part as the team's intention says and answers the facilitator.

#### Ringing at hand

`team ring <name> <ceremony> [--as <principal>] [--no-tick]` rings a declared ceremony at
hand, out of its hour. It is the tick's own ring -- `ceremony-due {ceremony, period, by}`,
ONE task to the facilitator, its opening `do` to the facilitator and a `do` per participant
-- under the period `manual-<id>`, the id of its own `ceremony-due`. So an `every` ceremony
still rings its date at its hour.

| refusal | when |
|---|---|
| `ceremony-unknown` | no such ceremony is declared |
| `ceremony-open` | a task of the ceremony is open |

#### Quorum

A ceremony line may end on `any <n>`, its QUORUM, with n from 1 to its participants
(`team-invalid` at `start` otherwise). Every ring of it writes
`wait {facilitator, any: n, to: the participants}` after its delegations. The facilitator
is woken at the n-th answer to its participants' `do`s.

### Recurring tasks

`team post <name> --message <text> [--to <member>] [--name <text>] [--as <principal>]
--every "<when>" [--context <n>%] [--description <text>]` lays a RECURRENCE: the same task,
given again at a set time. `<when>` is read as a ceremony's: `day`, `weekday` or `mon` to `sun`, then the local hour `HH:MM` -- or it
is a DURATION, `<n>m`, `<n>h` or `<n>d` with n a whole number from 1 (a ceremony has no
duration). The post writes `recurrence {recurrence: R<n>, from, to, text, name, when, since, context}` and
opens nothing. `--context <n>%` sets `context`, the recurrence's context limit (below); it is
`null` without one. `--description <text>` says what the recurrence does, one line of 1 to 200
printable characters (`description-invalid` otherwise).

At each tick, a recurrence whose day has come and whose hour has passed opens ONE task for
that day: an OCCURRENCE. The occurrence is a task like one `post` opens -- its `do` to the
member (the root without `--to`), its answer, its stop -- and carries `recurrence` and
`period` (the local date). It is named `<name> YYYY-MM-DD HH:MM`, the recurrence's id when
no name was given.

- The first occurrence comes at the first period after the post: posted at 10:00, a
  `09:30` recurrence starts the next day.
- While the occurrence before is still open, the period opens nothing and writes
  `recurrence-skipped {recurrence, period, open}`: a member never holds the same work twice.
- Under a pause nothing opens; a period that passed during the pause never opens.
- A season keeps the recurrences; `team delete` removes them with the journal.

A live recurrence keeps the team's net: no `schedule-off`, the relaunch entry stays, and the
timer sleeps until its next period at most. `team stop <name> --recurrence R<n>` writes
`recurrence-stopped {recurrence, by}`.

`team recurrence <name> R<n> --every "<when>"` writes `recurrence-changed {recurrence, when,
since, by}`, `since` the local hour of the change. From then on the tick reads the new `when`
and the new `since`; the periods already handled stay handled. A period is the local DATE: it
opens once, whatever hour is in force when it comes. Changed at 10:00 from `09:30` to
`14:00`, a recurrence that opened its task at 09:30 opens nothing more that day, and opens the
next one at 14:00. Changed to an hour already past that day, it opens nothing that day.

A recurrence by a DURATION keeps `when {kind: interval, every, seconds}` -- `--every 4h` is
`{kind: interval, every: "4h", seconds: 14400}`. Its SLOTS fall at `since + k x seconds`:
posted at 10:00, at 10:00, 14:00, 18:00 and so on. The first slot is the post itself, so the
tick that follows the post opens the first task. A slot is a period like a day: its period
is its local instant `YYYY-MM-DDTHH:MM`, and its task is named `<name> YYYY-MM-DD HH:MM`.
Only the slot under way is judged: a slot that passed without a tick -- the machine down, the
team paused -- never opens later, and a tick at 22:01 opens the slot of 22:00 alone, not the
one of 18:00 it missed. While the task before is still open the slot writes
`recurrence-skipped`, as a day does. `team recurrence --every` moves a recurrence from one
form to the other; given by a change, a duration opens its first task one duration after
the change.
`--context <n>%` writes `context` and `--context off` writes `context: null`; a change writes
only what changes, so a new limit alone leaves `when` and `since` as they are. `--message`
writes `text`; the tick opens the next tasks with it, and a task opened keeps the text of its
opening -- the journal is never rewritten.

`team recurrence <name> --task T<n> --every "<when>"` writes `recurrence {recurrence, from,
to, text, name, when, since, context, task}`: `to`, `text` and `name` are the task's, `from`
the principal who plays the verb, `task` its ORIGIN. The replay makes the origin the
recurrence's last task, so a period that comes while it is open writes
`recurrence-skipped {open: T<n>}`. The origin keeps its own run; the recurrence's tasks have
the recurrence for carrier, in a run of their own. `status --json` says
`recurrences[].task`, `null` for a recurrence posted by `post --every`.

Every occurrence is played in the member's ONE run for the recurrence, so that run grows from
one occurrence to the next. A context LIMIT renews it: the limit is a share of the context
window, a whole number from 1 to 99 (`70` and `70%` are the same). At the member's FIRST
wake-up on a new occurrence, the tick reads the last `wake-ended` of the recurrence's run that
carries a `context`. When its `used` (tokens divided by the window) is at or past the limit,
the tick writes `run-renewed {member, recurrence, task, run, used, limit}` just before the
wake-up's intent, and the wake-up opens a NEW run, named after the recurrence. The new run is
told only the recurrence's open occurrences. In every other case the run is kept: under the
limit, without a limit, or without a measure (no `context`, or a model whose window the
adapter does not declare). A later wake-up within the same occurrence, such as one for an
answer it receives, always keeps the run of that occurrence: the run never changes in the
middle of a task. The old run stays with the agent: nothing forgets it, `team delete` still
removes it, and `agent purge` may remove it while the team lives.

### Entries and the team's directory

`entries:` of `TEAM.md` (`<trigger> -> <document>`, the trigger being `do` or a ceremony's
name) names the document a wake-up on that trigger plays. That document is a SUCCESSOR of
the agent's procedure, elected at EVERY exchange, opening or resume.

Everything of a team lives in ITS directory, `teams/<team>/`, and nothing in an agent's
instance. Every wake-up gets `agent start --documents teams/<team>`, the root of documents
of the run it opens.

A plan the members share lives there too: `pp-plan section <slug> Context --shared` births it under
`teams/<team>/plans/`, and every member's run reads and writes it with the plan package's own verbs
(its README says how). `TEAM.md` has nothing to declare for it.

`team start` writes there, beside `TEAM.md`, `SEASON.md` and the entries' documents the owner
writes:

- `TEAM-<team>.md`, always, head and body ([The owner's word and the team's
  document](#the-owners-word-and-the-teams-document)). With entries, its `next:` lists every
  entry of the team, then the neutral `TEAM-IDLE.md`, and it says `decide: pp-team entry <team>`.
- the members' sheet `TEAM-<team>-members.md`: one row per member -- whom it reports to, its
  role keys, its model and effort, its description;
- the documents `documents:` names ([Documents](#documents));
- the neutral `TEAM-IDLE.md`;
- `TURN.md`, an overlay of the kit's turn that carries `output: team-act` and nothing else: the
  WORK line of every exchange of a run opened under the team's directory asks for the form of an
  act (`WORK team-act => terminal`), handed by the print call. A `TURN.md` an earlier version
  wrote there is replaced, and stderr says so; any other `TURN.md` is the owner's: it is kept,
  and stderr says so.

There is no law: a message is a `words`, a production printed. The last message of a launch is
none.

`pp-team entry <team>` prints the entry of the team's wake-up under way on a run -- the run
given by `--run`, else `PP_RUN` -- and the neutral otherwise. It finds the house as the
machine the skill lives in.

The pilot, never the model, picks the procedure. No wake-up carries a door: `--door` and
`PP_DOOR` stay for `agent run`.

#### Teams laid before team 0.15.0

What a version before 0.15.0 laid at an agent is removed by the next start; a file that
differs is kept and said. A team standing across that upgrade is stopped, then started
again: its members' runs carry no root of documents (`documents-fixed`).

### One run per task

A member holds ONE run per task: one key and one session of its harness. The member's first
wake-up on a task OPENS that run; every later wake-up on the task (an answer received, a
relance, a run that stands) resumes it by `--run`. The occurrences of a recurrence share the
recurrence's run, and the rings of a ceremony the ceremony's: what the task is carried by
keeps the run, the CARRIER. A run is the one that first answered, readable or not (a
`response-unreadable` keeps its run for the retry).

Every run a team opens is NAMED after its carrier by `agent name`: the task's name (`--name`),
else `<team> T<n>`; the recurrence's name, else `<team> R<n>`; the ceremony's name -- cut at 60
characters. A name the house refuses is written on `wake-launched` (`name-refused`) and the
wake-up plays on.

A member plays ONE wake-up at a time, on the first due task in the tasks' order; its other
tasks wait for its next wake-up, each in its own run. Its wait, its `await` and last delegation
included, stays by (member, task). The members play in parallel, `parallel:` bounding the
team.

The sharing line counts from the RUN's last wake-up, or from the team's start for a new run.

A house's `upgrade` keeps the key. It leaves the renewal mark at the slot's path; the next
wake-up resumes `--run <the same key>`, and the engine reopens the run under it.

A run whose slot `-reset` took, or that `team reset` forgot, gives way to a NEW run. The new
run's message opens on the history of its carrier's open tasks, then its inbox; the intention
is served in its output.

A kept run whose wake lock is still held is busy, and never resumed.

`work:` of `SEASON.md` gives every opening `agent start --work <repo>`: one clone per run, kept with it.
`status` says each member's last run, its state and its tasks, and its runs by carrier;
`status --json` says them under `members[].runs`.

#### The engine's calls: `guard`, `verify`, `mount`

Three verbs are called by the engine or the launcher, never by an agent. They read only:
nothing written, no lock, never a tick.

| verb | what it does | refusals |
|---|---|---|
| `team guard` | guards the runs: `agent purge` asks it before removing a run (the vector `agent-run:<path>/<key>` on stdin). A run a member of a living team holds -- the team started, a task open or a ceremony declared -- is kept, and the refusal names `team reset <team> --member <member>`. | `member-run`; `family-foreign` for another family |
| `team verify` | judges a vector `team-member:<team>/<member>` (on stdin) for the instance and the run that ask | `team-unknown`, `team-not-started`, `member-unknown`, `member-foreign` (the instance calling does not play the member), `root-foreign` (the run's root of documents is not the team's directory), `family-foreign` |
| `team mount <team>/<member>` | prints ONE `::mount` line: an entry per document of the member's role keys in its season ([Documents](#documents)), nothing for a member without one | as `verify`, but `family-foreign` |

### Task names

A task may carry a NAME, free text given by `--name <text>` at `team start` and at a
`team post` that opens a task. It is one line of 1 to 80 printable characters a user types,
its edges trimmed; anything else refuses `name-invalid`.

The name is kept as `name` on the `task` event. `status` says it (`T2 Prix de la DDR4 · open`),
and so do `status --json`, `log --json` and `watch --json`. A ceremony's ring names its task
itself ([The ceremony task](#the-ceremony-task)).

### Templates

A TEMPLATE is a file `<directory>/<name>.md`, named `<directory>/<name>`. The house sees two
places, in this order: its own `.pp/teams/templates/`, then the package's
`packages/team/templates/`; a name of the house replaces the package's.

- A template that carries `form:`, `members:` or `reports:` is a TEAM PRESET, named by
  `template:` of `TEAM.md`.
- A template that carries `documents:` without those keys is a SEASON PRESET, named by
  `template:` of `SEASON.md`.
- Any other template is a DOCUMENT, named on a line of `documents:`.

Each template declares its values (`values: |`, `<name> [= <default>] -- <description>`).

`team templates [--json]` lists every template the house sees: its name, its kind, its origin
and what it is, then its values. The package's nine team presets live in
`packages/team/templates/teams/`; each says its shape on its own `form:` line:

| template | `form:` | the team it makes |
|---|---|---|
| `teams/supervisor-workers` | `star` | one supervisor splits each task and gives one part to each worker |
| `teams/lead-reviewers` | `star` | one lead does the work and has each reviewer check its draft |
| `teams/chain` | `chain` | each member does its step, hands the next step to the next member and passes its result back up |
| `teams/solo` | `one` | one member does every task itself |
| `teams/empty` | `one` | one member and nothing else; the owner writes the rest of `TEAM.md` |
| `teams/council` | `star` | one facilitator asks every expert the same question and concludes once most of them have answered |
| `teams/triage` | `star` | one dispatcher hands each task whole to the one specialist it calls for |
| `teams/cross-check` | `star` | one judge gives the same task to each twin and compares their answers |
| `teams/tree` | `tree` | one lead over `squads` squad leads (2 unless said), each over its own workers |

Every `team start` reads the preset again. Its `form:` makes the edges when `TEAM.md` writes no
`reports:`, and the root -- the first member -- when it writes no `root:`. It adds the daily
ceremony, at the rhythm of the value `daily`, when two members or more report to the root,
unless `TEAM.md` writes a ceremony named `daily`. The preset's `budget:`, `launches:`,
`timeout:` and `schedule:` are the defaults of `TEAM.md`'s own keys.

`team templates --render <directory>/<name> [--value <name>=<value>]... [--team <name>]` shows
ONE document exactly as `start` would write it, holes filled, and writes nothing.

#### `team declare`

```
team declare <name> [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]...
    [--document "<key>|all <document> ..."]... [--no-document <key>]... [--body-file <path>|-]
    [--member <name> <path>]... [--no-member <name>]... [--role <key> [<member> ...]]... [--no-role <key>]...
    [--report "<member>... -> <member>"]... [--no-report <member>]... [--root <member>] [--principal <p>]...
    [--budget <usd>] [--launches <n>] [--parallel <n>] [--timeout <s>] [--schedule <step>|off]
    [--description <text>] [--json]
team declare <name> --season [--template <directory>/<name>] [--value …]... [--document …]... [--body-file <path>|-]
    [--budget <usd>] [--budget-launches <n>] [--silence <n>] [--context <n>%] [--provider|--model|--effort|--permissions|--harness <v>]
    [--package <name>=on|off]... [--member <member> [<flag> <v>]...]... [--json]
```

`team declare` is the ONE verb that writes `teams/<name>/TEAM.md`, or `teams/<name>/SEASON.md`
under `--season`. It writes off season only: before a first start, or after `team stop`; in
season it refuses `season-running`.

- Without the file, it writes it from the flags. At this birth, without `--member`, the members
  are the preset's own, at `agents/<name>/<member>`, and the preset's role keys are written with
  them.
- With the file, it writes the keys its flags name and they alone: every other key, line and
  the body stay as they are. `--body-file` replaces the body, the owner's word.
- Each `--no-…` takes its line out.

Before it writes, `declare` reads the declaration as it stands, then as it would stand, with
`start`'s own checks. A check that passed before and would fail after refuses, by `start`'s
code -- `template-unknown`, `value-unknown`, `role-unknown`, `document-unknown`,
`team-invalid`, `participant-unknown`, `root-missing`, `season-invalid` and the others -- and
nothing is written. It writes no event, renders nothing and launches nobody: what it writes
applies at the next `team start`. It says the keys written, the verdict `start` would give and
the gap to the last start.

`team new`, the verb of before, refuses `verb-retired`, naming `team declare`.

#### `team document`

`team document <directory>/<name> [--new | --body-file <path>|- | --delete] [--json]` is the
one writer of the house's own documents, `.pp/teams/templates/<directory>/<name>.md`. Without
an action it prints the source of the document the house uses, the house's file or else the
package's. `--new` creates the house's document from a skeleton; `--body-file` replaces its
text once checked; `--delete` removes it. The package's documents can be read, never changed.

| refusal | when |
|---|---|
| `template-invalid` | the name is not `<directory>/<name>`, each part a slug |
| `document-unknown` | no document of that name, or a preset to replace or delete |
| `document-exists` | `--new` on a name the house already has |
| `document-preset` | `--new` on the name of a package preset, which the house's document would hide |
| `document-readonly` | a document only the package has, to replace or delete |
| `document-invalid` | a text that fails the check, or `--body-file` naming no file |
| `document-used` | `--delete` while a line of `documents:` still names it |

### Reading a declaration

`team declaration <name> [--json]` READS a declaration. It says:

- `TEAM.md` whole;
- the verdict of `start`'s own judge: `ok`, or the refusal `start` would write, said with
  rc 0 (the judge DECLINES; `start` and `new` refuse with its words);
- its gap to the last start: `{key, started, declared}` for each front-matter key kept by
  `team-started` that the file now says otherwise.

The body is never pending: pp serves it at once. Nothing is written, there is no lock and no
tick.

#### `declared` under `--json`

The `--json` object says `declared`: the front matter as that judge reads it. That is the
members and their paths in order, the root, the edges, the principals, the limits of
`TEAM.md` alone, the schedule and the ceremonies' lines -- what the next start writes. It is
`null` under a refused verdict.

Each member there says `born` (an instance stands at its path) and `packages [{name, on}]`:
what a season that names no package gives it, born or not -- the packages the team requires
on, every other package the house pins beyond its base off. The member's SETTINGS plays no
part.

So a post knows what a season gives before it names a package.

### Following a team

A team is FOLLOWED without being moved.

| command | what it does |
|---|---|
| `./pp team status [<name>]` | reads the tasks, each agent's inbox and the last event; without a name, one line per team declared |
| `./pp team watch <name> [--task] [--json] [--heartbeat <s>] [--for <s>] [--until-done]` | writes on stderr every journal event as it arrives, every step of every wake-up under way and what its harness does between two steps (a tool called, its result, a thought, the words, the context); says `no event for <n>s` after the heartbeat |
| `./pp team log <name> [--task] [--last <n>]` | prints the journal, one line per event |
| `./pp team result <name> [<task>]` | prints a resolved task's result as JSON; refuses `task-open` or `result-missing` |
| `./pp team responses <name> [--since] [--agent] [--task] [--last]` | prints the members' responses, with their texts read at `responses.jsonl` |
| `./pp team inbox <name> --seen` | marks what waits for the owner as seen |
| `./pp team roster [--json]` | one row per team of the house -- its name, description, root, members, state and the caller's part in it --, then one row per live recurrence; nothing in a run a team opened. It also reaches every exchange outside the team's runs, under `INFORMATION — team-roster` |
| `./pp team stats <name> [--season <n> \| --all] [--cost usd\|launches\|tokens] [--json]` | prints the numbers of one season, or of every season ([`team stats`](#team-stats)) |

`watch` reads the agents' traces by the engine's reader and never writes them. It takes no
lock, writes nothing and never ticks.

For every wake-up it follows, `watch` also reads the run's flow (`agent flow --follow`, the
same reader as the follower's) and says the ACTIVITY of the harness between two steps, one
object `event: activity` per event under `--json` -- `{at, agent, run, event: activity, kind,
task, tag, launch, …}`, `kind` one of:

| kind | what the object carries |
|---|---|
| `tool` | `name`, `title` (its input on one line), `pp` (true for a call of the agent's console) |
| `tool-result` | `error`, `size` (the characters of the result) -- never its content |
| `thinking` | `text`, or `tokens` when the harness counts them alone |
| `words` | `text` |
| `context` | `tokens`, `used` (the part of the model's window), `window` |

Every text is cut at 80 characters (`ACTIVITY_TEXT`). The relay is bounded: at most 4
objects a second per wake-up (`ACTIVITY_RATE`); past that, the latest one is said once the
second turned, with `more` counting the objects it stands for; a `context` is always said.
Without `--json`, one line each: `[HH:MM:SS] <member> · <run> · tool Read · pp.py`,
`result ✓ 10.0 kB`, `thinking <text>`, `words <text>`, `context 34000 tokens`.

#### `team stats`

`team stats <name> [--season <n> | --all] [--cost usd|launches|tokens] [--json]` prints the
numbers of one SEASON of the team, read from its journal alone (team 1.35.12). It writes
nothing. A season runs from one `team-started` to the next, or to its stop; its number is the
rank of its start, from 1. By default it is the season under way, else the last one;
`--season <n>` chooses another.

For a season, `stats` says:

- its dates and its state: `running`, `paused` or `stopped`;
- its tasks closed, stopped and open. A task shows in each season where it is born, woken,
  closed or stopped, and counts there only the wake-ups of that season, so the tasks of a season
  add up to its cost;
- its DELEGATIONS (`delegations`, team 1.36.62). A delegation is one `do` posted in a task,
  the `do` that opens the task included; the season adds up the `do` of its tasks;
- its cost and its launches;
- since team 1.36.62, its cost per delegation in each unit (`per_delegation`); its cost per
  launch in dollars and tokens (`per_launch`), given without a median: a longer launch costs
  more without the work being dearer; and its cost per hour of EFFORT (`per_effort_hour`, in
  dollars and tokens): the cost divided by the effort in hours. The effort of the failed
  wake-ups counts, so an hour lost makes the hour dearer;
- its ROOT member (`root`): the member its `team-started` names as `root`, what that member
  cost in each unit and its share of the season's cost. When `team-started` names no root,
  `member`, and the cost and share in all three units, are `null`;
- its tasks stopped at its end (`stopped_tasks`): how many, what they cost in each unit, and
  their share of the season's cost. Without a stopped task, the cost and the share are `0`, never
  `null`, in each unit where the season's cost is known. The field `stopped` stays the hour the
  season stopped;
- its BUDGET (`budget`), in dollars (`usd`) and in launches (`launches`). For each: the cap,
  what the season spent, the share of the cap spent, the pace of the spending per hour of
  ACTIVE time (`per_active_hour`), and the hours left at that pace (`hours_left`): what remains
  of the cap divided by the pace, `0` once the cap is passed, `null` once the season is stopped
  or when there is no pace yet. The cap is the one the season's `team-started` sets, raised by
  each `team budget` of the season. The money the wake-ups under way hold back is not counted:
  only the live state of the team knows it (`team status`). A unit without a cap is `null`;
  `budget` is `null` when neither unit has one;
- three times: ELAPSED, the clock time from its start to its end or to now; ACTIVE, the clock
  time during which at least one wake-up runs; EFFORT, the durations of all its wake-ups added
  up. Its parallelism is effort divided by active time: how many members work at once, on
  average. The effort is also given per slot of 2 hours from the start. Since team 1.36.64, the
  cost is given per slot too, in each unit (`time.cost_by_slot`): the cost of a wake-up counts in
  the slot where it ends, a wake-up still running in the slot of now, and an end without an hour
  in the slot of its launch;
- the wait from a wake-up's intent to its launch, median and p90;
- the questions the members asked a principal: how many were answered and how long they
  waited; under `from_principal`, the same for the questions a principal asked a member
  (`post --ask`);
- the share of the context a wake-up left at its end, and the runs renewed. Since team 1.36.64,
  the wake-ups by BAND of that share (`context.by_band`): under 25 %, 25 to 50 %, 50 to 75 %, 75 to
  90 %, and 90 % and over, the share at which a run is renewed. A wake-up whose end gives no
  measure of its context is in no band;
- since team 1.36.64, its launches BY MODEL (`by_model`): one line per model and provider that a
  `wake-launched` names, the most launched first. A launch whose `wake-launched` names no model,
  and an end without a launch that carries a cost, count on a last line whose `model` is `null`:
  their model is unknown, and never guessed. A wake-up never launched that carries no cost -- an
  intent alone, or an end without a launch and without a cost -- counts on no line. The shares of
  the lines add up to 1 in each unit where the season's cost is known;
- since team 1.36.64, its launches BY DURATION, from the launch to the end (`by_duration`): under
  1 minute, 1 to 3 minutes, 3 to 10, 10 to 30, and 30 minutes and over. Only the launches that
  ended count;
- the losses: the wake-ups failed, their cost and their reasons, and the silences.

A wake-up still running counts up to now.

A line of `by_model`, `by_duration` or `context.by_band` gives its `launches`, its `cost` in each
unit, its `share` of the season's cost, its cost per launch (`per_launch`) and its cost per hour of
effort (`per_effort_hour`). A line of `by_model` also gives its `model`, its `provider` and its
`effort` in seconds. A band gives its bounds: `from`, included, and `to`, excluded, in seconds for
a duration and as a share of the window for a context; `to` is `null` for the last band. A wake-up
on a bound counts in the band that starts there. The bands are the same for every team.

A line of `by_model`, a band, or a slot of `time.cost_by_slot` whose wake-ups report no cost --
a band without a launch and a slot where no wake-up ends among them -- gives a cost of 0 in each
unit where the season's cost is known: nothing was spent there. A line and a band then give a share
of 0 too; a slot gives a cost alone, never a share. In a unit whose cost is unknown, the cost and
the share are `null`. The `per_launch` and the `per_effort_hour` of a band without a launch are
`null`: they have no value.

The effort, and so every cost per hour of effort, counts all the wake-ups, the failed ones
included: an hour lost makes the hour dearer.

Each season also gives some of its measures against the MEDIAN of the seasons (`against`,
team 1.36.62): the cost per delegation in each unit, the cost per hour of effort in dollars and
tokens, the failed wake-ups, and the p90 of the context. `against` has the shape of the
measures: `against.<group>.<key>` is `{median, ratio, over}`, for instance
`against.per_delegation.usd`. `median` is taken over the seasons in which a wake-up launched,
the season read among them, by the nearest rank: of an even number of values, the lower of the
two in the middle. `ratio` is the measure divided by that median, `null` when either is unknown
or the median is 0: a median of 0 judges nothing. `over` is how many seasons the median is taken
over: the seasons in which a wake-up launched and that have a value for this measure. A season
read alone, without `--all`, gives `against` too.

Each line of `by_task` also gives its `share` of the season's cost in each unit, its cost per
delegation (`per_delegation`: its cost divided by its `do`), and that cost against the same
median as the season's (`against.per_delegation.<unit>`). Since team 1.36.64, it also gives its
cost per hour of effort in dollars and tokens (`per_effort_hour`, in the shape of the season's),
and that cost against the same median as the season's (`against.per_effort_hour.<unit>`).

Each line of `by_member` also gives its `share` of the season's cost. Since team 1.36.64, it also
gives the models of its launches, the most used first and `null` last for the launches that name
none (`models`), its cost per hour of effort (`per_effort_hour`), and that cost against the same
median as the season's (`against.per_effort_hour.<unit>`).

`--cost` chooses the unit the text says every cost in: `usd` by default (`-` when the provider
reports no cost, never 0); `launches`; or `tokens`, the `tokens` of the wake-ups' ends -- for a
wake-up without them, the `context.tokens` of its end, the size of its last call only, and the
sum is then marked `~`.

In the text, a season opens with four lines (team 1.36.62), its costs in the unit of `--cost`:

| line | what it says |
|---|---|
| `spent` | the cost; when the unit has its own cap, also the cap, the share spent, the pace per active hour and the hours left |
| `work` | the delegations, and the tasks closed, stopped and open |
| `price` | the cost per delegation, with its median and its ratio (`median <median> · x<ratio>`); except under `--cost launches`, the cost per hour of effort and per launch |
| `load` | the launches per delegation, with its median and its ratio; the root member and its share |

After the line of the context, the text says the launches of the season (team 1.36.64), each
part on its own line, its costs in the unit of `--cost`:

| line | what it says |
|---|---|
| `model` | one line per model of `by_model`, its provider, then `no model` last when there is one: its launches, its cost and its share, its cost per launch and per hour of effort |
| `duration` | one line per band of `by_duration`, its bounds in seconds: the same figures |
| `band` | one line per band of `context.by_band`, its bounds in percents of the window: the same figures |
| `slots` | the cost per slot of 2 hours, each wake-up in the slot where it ends: a launch, or an end without a launch |

Under `--cost launches`, a line of `model`, `duration` or `band` says its launches and its share
alone. The text says the cost per hour of effort of no task and no member: it has no line per task
or per member.

The text rounds each figure to be read (team 1.36.63): a cost, a pace, a median and a ratio
with two decimals, hours with one decimal, a share in whole percents; `-` for a figure that is
unknown. The JSON keeps four decimals.

`--all` says each season in which a wake-up launched, then their median, and lists the seasons
without one apart. It also says each task over ALL its seasons, one line per task in the order
it first comes (team 1.35.13): its costs, its `do` and `re`, its failures, its active time and
its effort added up over its seasons; its name and state as its last season says them. Its
ELAPSED time is the clock time from the task's first event to its last, never a sum of its
seasons. Since team 1.36.62, each of these lines also gives the `seasons` it comes from and its
cost per delegation over all of them (`per_delegation`), and since team 1.36.64 its cost per hour
of effort over all of them (`per_effort_hour`); it gives no `share` and no `against`.
The `median` also covers the measures a season gives against it.

Under `--all`, since team 1.36.62, `stats` also gives:

- `total`, the seasons in which a wake-up launched, added up: how many, their cost, their
  delegations, the cost per delegation, per launch and per hour of effort over them all, their
  failed wake-ups, their tasks closed, stopped and open, and the stopped ones with their cost
  and share (`stopped_tasks`). Here each task counts ONCE, by its last state over those seasons:
  a task open at the end of one season and stopped in the next counts as stopped, with its whole
  cost;
- `task_cost`, the cost of a task in each unit: its `median`, its `p90`, and its
  `concentration`, `{tasks, of}`: how many tasks, the dearest first, carry 80 % of the cost, out
  of how many tasks with a known cost. It is taken over the tasks of `total` (those of the
  seasons in which a wake-up launched) that launched at least one wake-up: the same tasks in
  every unit, except a task whose cost in that unit is unknown.

In the text, an `all` line closes the seasons: how many, their cost, their delegations, the cost
per delegation, the tasks closed, stopped and open, and the failed wake-ups.

Under `--json`, `stats` prints ONE object, `{team, base, season}`, or `{team, base, seasons,
median, empty, by_task, total, task_cost}` under `--all`. Each cost is given in the three units
at once (`null` where none is known), then one line per task (`by_task`) and per member
(`by_member`).

| refusal | when |
|---|---|
| `team-not-started` | the team was never started, `--all` included |
| `season-unknown` | `--season` names a season the team does not have |
| `cost-invalid` | `--cost` is not `usd`, `launches` or `tokens` |

`--season` with `--all` is the usage.

#### What waits for the owner

What waits for the owner reaches their own exchange. The package mounts `TEAM_INBOX.md` at
the kit's `turn.begin`, which plays `pp-team inbox`. It serves, under
`INFORMATION — team-inbox`, one line per team where, since the owner last said
`./pp team inbox <name> --seen`:

- a question (an agent's `ask`), or a notice of the team about a member, awaits its answer;
- a task was resolved;
- a notice of a guard came, or a post was returned.

`--seen` writes `inbox-seen` at the journal, the one event these readers write. When nothing
waits, there is no section.

The document says what that line renders and teaches no call. The gestures it sends the
agent to -- `inbox --seen`, `post --reply`, `result` -- live in `pp-team`'s `SKILL.md`.

### The faces

The fields below are what a program reads; the [`ui`](../ui/README.md) package reads them.

#### `team status --json`

`team status [<name>] --json` is the face a program reads, the post of `ui` first; the text's
bytes stay unchanged. With a name it prints ONE JSON object on one line; without a name, one
object per team declared. A team never started is
`{team, started: null, state: "never", waiting_on: []}`.

| field | what it says |
|---|---|
| the team's tasks | their text; their last event as `log --task` keeps them; holders, delegations, waits; their `cost`; `dos [{id, from, to, answered}]`; `waits` (`answered` of `of`); the `relance` of a wake-up under way; `running` (the wake-ups under way on the task) |
| `root` | the root member the team's last `team start` declared (team 1.35.13) |
| its members | run, state, `roles` (the member's role keys: each key of `roles:` that names it, as the last start read the declaration, in the order declared; `[]` for a member without one; team 1.35.16), `context` (what its last wake-up left, `null` before its first one), the posts not delivered yet, the other members' answers since its run's last wake-up, the `packages` their run plays (read as `agent status` reads them); `owes`; `health {suspected, falls, tried_at, repents}` |
| its ceremonies | `next_due`, the local `YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring; `due`, the next tick rings it; the last ring and who answered it |
| its recurrences | `recurrences [{id, name, text, from, to, when, since, next_due, due, stopped, last}]`: `next_due` its next period, `null` once stopped; `due`, the next tick opens it; `last {period, task, state}` its last occurrence. Each task says its `recurrence`, `null` for a task no recurrence opened |
| the owner's box | what waits for the owner |
| `required` | the packages a member may not switch off: `team` and what it requires, the list `package-required` names. Every object says it, a team never started included. |
| `state` | derived from the replay, never written: `working` while a wake-up plays, `idle` when no task is open, else `waiting`; `paused` under a pause |
| `waiting_on` | every guard that holds, in the order the tick judges them: `members`, `launches`, `budget`, then `owner`, `suspected`, `due`. A suspected member gives `suspected` instead of `blocked`. |
| `season {n, state, at, stopped, budget, budget-launches}` | the number of the season (the starts, counted by the replay), `running` or `stopped` once `team stop` ended it -- `stopped {at, by, id}` then --, and the season's own budget |
| `launch` | what the next wake-up gets, never `max_budget_usd`, with its `packages`; each member's is the same, its profile applied |
| `budget {cap, spent, reserved, left}` | the money ([Each wake-up's share of the money](#each-wake-ups-share-of-the-money)) |
| `schedule {seconds, timer, relaunch, reason}` | the net: its step, whether a timer is armed, whether the relaunch entry stands and why the system refused it |
| `paused {by, at}` | who paused the team, and when |

Both forms, with and without a name, say the team's `state`. Without a name, a team's line
counts `asks` (the agents' questions), `notices` (the team's) and `done` (the tasks resolved
and not seen), as `team inbox` does, and says its `season {n, state}`; a team never started
has no `season`.

#### The other faces

| command | what it prints |
|---|---|
| `team log <name> --json` | one object per event, the object `watch --json` writes (`{at, team, event, id, …}`): a reader takes the history there and the live flow at `watch` |
| `team responses <name> --json` | one object per response, its whole text or `null` |
| `team inbox [<name>] --json` | one object per team where something waits for the owner, the questions and the returned posts with their texts; each message says its `at`, the moment it was written in the journal |

`inbox` tells `questions` from `notices`, and says `awaits` while a notice about a member
holds it.

### Routes and answers

The routes and the answers hold:

- a `do` goes to an agent that reports to the answering one; on a ceremony task, its
  participants report to its facilitator;
- an `ask` goes to ANY member of the team, or to a principal;
- a `reply` goes only where an `ask` from its target to the answering member stands on the
  task;
- a `do` off the edges, an `ask` to a name nobody declared and a `re` citing a message never
  delivered are refused at the routing (`wake-refused`, an info to the member);
- a post to a principal -- the owner, a mandator, the team -- is delivered at its writing and
  never `returned`.

### Names and paths

A team speaks NAMES and addresses its agents by PATHS.

These say the member's name:

- the journal, whose `agent` field is the member's name;
- the inbox;
- `status` (`r1 · agents/reviewer · inbox 0`);
- the head of every wake-up, `[team <name> · you are <member>]`, after the lines
  `agent start` sets at the head of a prompt (the material's and the neighbours').

Every birth, `agent start`, wake lock and record of the house is addressed by the member's
path, read at `team-started.agents` (`{member: path}`) or at the intent's `path`.

A line of `agents:` written before reads the same way: `m manager` is the member `m` played
by the agent at `manager`.

## See also

- [`agent`](../agent/README.md) -- the house and `agent start`, which every wake-up uses.
- [`ui`](../ui/README.md) -- the post that reads the team's faces.
- [The operator's console](../../docs/reference/console.md) -- the console the tick launches by.
- [Channels and the delivery](../../docs/reference/block.md#channels-and-the-delivery) -- the said productions an act is one of.
