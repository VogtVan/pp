---
name: TEAMS_CHEATSHEET
kind: doc
description: >-
  The author's reference of a team on one page: the values files, the documents by role, the
  season, the exchange of a member, the templates, five patterns and the traps. Served by the TEAMS
  space beside TEAM_WORK.md. A reference, never played.
---

# The teams cheat sheet — the values files, the documents a start renders, what a member sees

A TEAM is a set of agents that work together on tasks. Its owner DECLARES it in one directory of
the house, `teams/<name>/`; the script `pp-team` reads that declaration, starts the team, carries
its messages and writes its journal. This page is for the AUTHOR of a team. A member reads
`TEAM_WORK.md` instead -- how a team works, seen from inside.

The words, used below as defined here:

- A MEMBER is a name in the team (`lead`, `reviewer-1`) played by an AGENT, an instance under the
  house given by its PATH (`agents/alpha/lead`). Several members may share one agent.
- An EXCHANGE is one wake-up of a member: one message in, the work, the answers out.
- A SEASON runs from a `team start` to a `team stop`. Between a stop and the next start the team
  is OFF SEASON: nobody is woken. `TEAM.md` and `SEASON.md` are written before the first start, or
  off season.
- A VALUES FILE is the author's: `TEAM.md` for the team, `SEASON.md` for the season. Both say their
  documents and their values with the same keys, `documents:` and `values:`; the body of each is
  the author's own word.
- A DOCUMENT is a text the members receive: a template `<directory>/<name>`, or a file `<name>.md`
  the author lays in the team's directory.
- A ROLE KEY is a word the author gives to members (`roles:`). It decides which documents a member
  receives; it gives no right and no rank.
- A TEMPLATE is a DOCUMENT, or a PRESET that gives ready-made lines for a values file (section 5).
- A RENDERED document is pp's: every start writes it again from the values files; never edit it.
- A document is ATTACHED at a socket (`attach: turn.begin`): pp plays it as a step there and serves
  what it names. A document is MOUNTED at a socket (`mount: turn.begin`): its laws and tools are in
  force for the whole exchange, its body and its `serve:` rows served with it.
- A VECTOR is the address pp passes with a member's launch, `team-member:alpha/<member>`: through it,
  the documents of that member's role keys are mounted.

All the examples use one team, `alpha`: `lead` receives the tasks, `reviewer-1` and `reviewer-2`
report to it.

## 1. The team's directory

```
teams/alpha/                       written by        a member's run sees it as
├── TEAM.md                        the author        its body, served when it is not empty
├── SEASON.md                      the author        its body, served when it is not empty
├── <name>.md                      the author        a document a line of `documents:` names
├── TEAM-alpha.md                  start (rendered)  the attached document of every exchange
├── TEAM-alpha-members.md          start             a reading served by the head
├── TEAM-alpha-<name>.md           start (rendered)  a document of `all`: served, or mounted when it mounts
├── roles/TEAM-alpha-<name>.md     start (rendered)  a document of a role key: mounted for its members alone
├── TEAM-IDLE.md                   start             the neutral successor (entries only)
└── WORK.md, DAILY.md …            the author        entries: the document a wake-up plays
```

The directory is the ROOT OF DOCUMENTS of every run the team opens: a name cited resolves there
first; nothing of the team is written in an agent's instance.
`TEAM_WORK.md` is a reference of the team package (`refs/`), found by its name.

| file | what it holds |
|---|---|
| `TEAM.md` | `template:` (a team preset), `values:`, `documents:`, `agents:`, `roles:`, `root:`, `reports:`, `principals:`, `ceremonies:`, `entries:`, the limits (`budget:`, `launches:`, `timeout:`, `parallel:`, `retries:`, `budget-launches:`, `silence:`, `suspect-max:`), `schedule:`, `name:`, `description:` |
| `SEASON.md` | `template:` (a season preset), `values:`, `documents:` -- added to the team's for this season --, the launch (`provider:`, `model:`, `effort:` …), `budget:`, `budget-launches:`, `silence:`, `context:`, `packages:`, `profiles:`, `work:` |
| `TEAM-alpha.md` | head: `proc: SERVE`, `serve:`, `attach: turn.begin`, with entries `next:` and `decide:`; body: the INTENTION of the team preset, its holes filled from the members and the values; empty without a preset |
| `TEAM-alpha-members.md` | one row per member: whom it reports to, its role keys when the team has some, model, effort, the `description:` of its `MEMBER.md` |
| `TEAM-alpha-<name>.md` | one per document of the key `all` (a role key's goes under `roles/`), `<name>` the last part of its name: a template's body under the keys pp reads (`mount:`, `constraints.*`, `tools:`, `serve:`), holes filled; a file of the directory as it stands |

The head serves, in this order: `TEAM-alpha.md`, `TEAM.md` when its body is not empty,
`TEAM_WORK.md`, `SEASON.md` when its body is not empty, then every `TEAM-alpha-<x>.md` at the root
that does not mount, sorted by name. A body is served as it stands and read again as soon as it
changes, without a start.

## 2. Documents by role

```yaml
# TEAM.md (extract)
roles: |
  writers lead
  readers reviewer-1 reviewer-2
documents: |
  all notes/house-style
  readers review/checklist house-rules
```

One line per key: `<key> <document> ...`, each key once. The key `all` reaches every member; a role
key reaches the members who hold it. A preset writes a hole, `{reviewers}`, in place of a key: the
value `reviewers` chooses the team's key (`reviewers = readers`). Each document is rendered ONCE: at the root for `all`, under
`roles/` otherwise. A member with two keys receives each document once.

`SEASON.md` says `documents:` the same way, and its lines are ADDED to the team's for the season: a
key both files name receives the documents of both. The next season without them, they leave.

The values: each preset and each document declares the values it asks; `TEAM.md` gives them under
`values:`, `SEASON.md` too, and `SEASON.md` wins name by name. `{team}`, the team's name, is built in.

## 3. The season

| gesture | what happens |
|---|---|
| `team declare alpha …` | writes `TEAM.md`, or `SEASON.md` with `--season`, the keys its flags name and they alone; judged as the next start would judge it; never in season (`season-running`) |
| `team declaration alpha` | the verdict of the next start, `pending` (what it would change), under `--json` each member's documents (`declared.views`) and `started.state` (`running`, `stopped`) |
| `team start alpha` | renders the documents and opens the season; `season-running` when one is open already |
| `team stop alpha` | ends the season: stops the open tasks, silences the recurring tasks that are not paused, names both; a paused one stays paused and is not named; nothing passed off season is made up later |

## 4. The exchange of a member

```
 message in (a task, a reply, a ceremony)
      │
      ▼
 kit TURN ── turn.begin ──┬── MOUNT  TEAM-alpha-<x>.md that mount  (every member)
      │                   ├── MOUNT  roles/TEAM-alpha-<name>.md     (by the vector team-member:alpha/<member>,
      │                   │      laws TM…, tools ──────────► in force until the exchange ends   its keys' documents)
      │                   │      body + serve: rows ──────► served once, with the mount
      │                   │
      │                   └── ATTACH TEAM-alpha.md           (attach: turn.begin, proc: SERVE)
      │                          SERVE: TEAM-alpha.md, TEAM.md, TEAM_WORK.md, SEASON.md,
      │                                 TEAM-alpha-members.md, TEAM-alpha-<name>.md …
      │                          with entries: leaves to the successor `pp-team entry alpha` elects
      ▼
 the member's own work (its MEMBER.md, its laws) … its answers, read by the team as they come
```

| mechanism | key | what holds it | lifetime at the member |
|---|---|---|---|
| attach | `attach: turn.begin` | the head of `TEAM-alpha.md` | one step at the start of each exchange; each reading read once in the run, and again when it changes |
| mount | `mount: turn.begin` | a document that declares it | laws and tools for the whole exchange, mounted again at each exchange |
| vector | `team-member:alpha/<member>` | each launch of a member with a document of a role | its documents under `roles/`; one without `mount:` gives its body alone |
| serve | `serve:` | the head, a mounted document | the readings, each one a body of its own |
| successor | `next:` + `decide:` | the head, with `entries:` | the entry document the wake-up plays |

## 5. Templates

Two places, the house's first: `<house>/.pp/teams/templates/<directory>/<name>.md`, then the team
package's `templates/`. A house template replaces the package's of the same name; a template whose
`requires:` names a package the house does not pin is not listed. `team templates` lists them with
their values; `team templates --render <directory>/<name> [--value <name>=<value>]... [--team alpha
[[--season] --text-file <path>|-]]` shows one document as `start` would write it, and writes nothing;
`--text-file` reads a text in the place of `TEAM.md`, or of `SEASON.md` under `--season`.
`team document <directory>/<name>` prints the source of one document. It is the one way to write
the house's documents: `--new` creates one from a skeleton, `--body-file <path>|-` replaces its text
once checked, read byte for byte (its line endings stay as written), `--delete` removes it. The
package's documents are read only: `--new` gives the house its own of that name, used in their
place -- never for a preset of the package, which it would hide.

| key of a template | what it does |
|---|---|
| `description:` | what it is for, said by `team templates` |
| `values: \|` | one `<name> [= <default>] -- <description>` per line |
| `requires:` | the packages it needs |
| `documents: \|` | a PRESET's lines, the defaults of the file that names it: a line of the file replaces the preset's line of the same key |
| `form:`, `members:`, `reports:`, `root:`, `roles:` | a TEAM preset's team: `form:` (`star`, `chain`, `tree`, `one`) makes the edges and the root at every start; `roles:` gives each key places of the form (`{root}` `{others}` `{last}`; `one` lacks `{others}`; `tree` adds `{squads}` `{workers}`), filled and written into `TEAM.md` at the birth only |
| `mount:`, `constraints.*`, `tools:`, `serve:` | a DOCUMENT's keys pp renders with its body |

A team preset is named by `template:` of `TEAM.md`, a season preset (`documents:` without `form:`,
`members:` or `reports:`) by `template:` of `SEASON.md`. In a body, `{<name>}` is filled by the value,
`{{` and `}}` are one brace, and `<name>` is left for the member to fill (a task, a branch).

A document no line names any more leaves at the next start; the keys of both files wait for it.

## 6. Patterns

### (a) A team from a preset

```yaml
# TEAM.md
template: teams/lead-reviewers
values: |
  daily = every weekday 09:30
description: Writes the house's notes and has them reviewed.
agents: |
  lead agents/alpha/lead
  reviewer-1 agents/alpha/reviewer-1
  reviewer-2 agents/alpha/reviewer-2
```

`team declare alpha --template teams/lead-reviewers --value "daily=every weekday 09:30" --member lead
agents/alpha/lead …` writes it, with the preset's role keys. The form `star` makes `lead` the root.

### (b) A document of the house for every member: laws and tools

```yaml
# <house>/.pp/teams/templates/common/rules.md
description: the team's branch, and one answer per piece of work
values: |
  branch -- the branch the team works on
mount: turn.begin
constraints.behavior: |
  TM<n>  work on {branch} only, never on the default branch
tools: |
  pp-team
```

`team declare alpha --document "all common/rules" --value branch=notes` writes the line; every start
renders `TEAM-alpha-rules.md`, mounted for every member. Write `<n>` as the rank of the law in the
team: `TM1`, `TM2`.

### (c) A document for one role key

`team declare alpha --role readers reviewer-1 reviewer-2 --document "readers review/checklist"`:
`roles/TEAM-alpha-checklist.md` is mounted by the vectors of `reviewer-1` and `reviewer-2` alone;
`lead` never receives it.

### (d) A season from a preset

```yaml
# SEASON.md
template: seasons/files
values: |
  contributors = writers
  reviewers = readers
  source-folder = notes/sources
  draft-folder = notes/drafts
  result-folder = notes/results
```

`team declare alpha --season --template seasons/files --value …` writes it. The preset's lines
`{contributors} …` and `{reviewers} …` fall on the team's keys `writers` and `readers`. A next season
may name another preset: the team stays.

### (e) Entries, ceremonies and recurring tasks

```yaml
# TEAM.md (extract)
ceremonies: |
  retro after daily with reviewer-1 reviewer-2 -> lead
entries: |
  do -> WORK.md
  daily -> DAILY.md
```

At each exchange, `pp-team entry alpha` prints the successor: the entry of the task's ceremony,
else the entry of `do`, else `TEAM-IDLE.md`. An entry lives in the team's directory, or in the
instance of every agent whose members play it (`entry-missing` otherwise).

| what | how it is written | what happens |
|---|---|---|
| a ceremony | `<name> every day\|weekday\|mon..sun HH:MM with <participants> -> <facilitator> [any <n>]` | at its hour, the tick opens ONE task to the facilitator, a `do` per participant; `any <n>` tells the facilitator n answers are enough |
| after another | `<name> after <other> with … -> …` | rung once the other one's task of the same period is resolved |
| at hand | `team ring alpha daily` | the same task, out of its hour |
| a recurring task | `team post alpha --every "weekday 09:30" --message <text> --description <text>` | a RECURRENCE `R<n>`: the task comes back at each period |
| change, pause, stop it | `team recurrence alpha R1 …`, `team pause` / `resume` / `stop alpha --recurrence R1` | a resumed recurrence catches nothing up |

## 7. Traps

| trap | what happens | what to do |
|---|---|---|
| `team declare` in season | `season-running`, nothing written | `team stop alpha`, then write |
| a post, a ring or a stop off season | `season-stopped` | `team start alpha` |
| a rendered document edited by hand | `start` refuses `rendered-edited`; its verdict says it | put the change in a values file or a template |
| words written in the body of `TEAM-alpha.md` | `start` refuses `intention-misplaced` | move them to the body of `TEAM.md` |
| `work:` in `TEAM.md` | `key-moved` | it is the season's: move it to `SEASON.md` |
| a document that is neither a template nor a file of the directory, or a preset on a line | `document-unknown` | name it as `team templates` says it |
| two documents of one name, a document named `members`, or a file no start rendered under a name to render | `document-collision` | name one of them otherwise |
| a file of the directory with a hole `{<name>}` | `document-holes` | lay a template under `.pp/teams/templates/` to fill values |
| `--compose`, `--no-compose` | `flag-retired` | `--document`, `--no-document` |
| a value without a default left out | `value-missing`, naming it | give it under `values:` |
| a value nothing declares | `value-unknown` | take it out |
| a key `roles:` does not declare | `role-unknown`, naming the line | declare the key, or give the preset's role value |
| a document of a role that mounts at another moment than `turn.begin` | `common-mount-moment` | mount it at `turn.begin` |
| a law of a mounted document coded outside `TM` | `common-code-prefix` | code the team's laws `TM1`, `TM2` … |
| one code twice in a member's view, or already at the member | `common-collision` | give the law another code |
| a `tools:` or `serve:` name unknown at one member | `common-tool-unknown` · `common-serve-unknown` | name what it plays, or lay the file |
| `team document --delete` on a document a line of `documents:` names | `document-used`, naming each team or house preset, its file and its key | take it off each line -- `team declare` for a team, its own file for a preset --, then delete |
| `--body-file` or `--delete` on a document of the package | `document-readonly` | `team document <directory>/<name> --new` |
| `team document --new` on the name of a preset of the package | `document-preset` | choose another name |
| a `--reply` to an `ask` whose task is resolved or stopped | `task-closed`; `team inbox` lists that ask with the infos, `closed: true`, until it is read | post a new task if the answer still matters |
| a refused start | the journal and the directory stay byte for byte | fix the file named, start again |
