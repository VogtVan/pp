#!/usr/bin/env python3
"""The house's hand over its teams: a team is DECLARED by its owner at
`<house>/teams/<name>/TEAM.md`, started, posted to, stopped, read -- and ADVANCED by ticks.
Its state is its JOURNAL, read again at every reading. This script keeps no clock: a tick is
one short process, launched by the end of a wake-up (`--on-end`), by a post, or by the team's
TIMER -- the NET under every other trigger, a process the tick arms and that dies after one tick --,
and after a restart by the team's relaunch entry in the system's scheduler, laid and removed by this
script on the owner's commands (the engine never writes the scheduler); the wake-ups a tick launches
are the house's own console's (`agent start`).

A team is made of MEMBERS: `agents: |` of `TEAM.md` declares one `<name> <path>` per line -- the
member's NAME, a slug unique in the team, then the PATH of the agent that plays it; one path may
come back, several members on one agent. The journal (its `agent` field is the member's name), the
inbox, `status` and the head of every wake-up (`[team <team> · you are <member>]`) speak names;
every call to the house -- `agent start`, a wake lock, a record of the house, a birth -- is
addressed by the member's path, read at `team-started.agents` (`{name: path}`).

`roles: |` of `TEAM.md` declares ROLE KEYS, one `<key> [<member> ...]` per line: the key a slug said once, the
author's own word -- pp reserves none and deduces none from an edge, the root, a profile or a member's name --, its
members declared by `agents:`, each once on its line; a key without a member is reserved, and said. A key chooses
documents, never a right: a line of `documents:` names the key it reaches (below). A team preset's `roles:` names,
after each key, PLACES of the preset's form, written as holes: `{root}` the root, `{others}` every other member,
`{last}` the last member, and for `tree` alone `{squads}` the squad leads and `{workers}` the workers. `star`,
`chain` and a preset without `form:` have `{root}`, `{others}` and `{last}`; `one` has `{root}` and `{last}`; a
place the form does not have, or a member's name, refuses `template-invalid`. At the birth alone, each place is
filled with the members the form puts there for the team declared, and the lines are written into `TEAM.md`.
Kept by every season at `team-started.roles` (`{key: [members]}`),
followed by `declaration`, said by the members' sheet.

`template:` of `TEAM.md` NAMES a TEAM preset the house sees, `<directory>/<name>` -- a template that carries `form:`,
`members:` or `reports:` --, and `values: |` gives the values the preset and the documents declare, one
`<name> = <value>` per line (a value with a default may be left out; `daily =`, left empty, takes the daily out).
The key is optional: without it nothing is chosen in silence, the team is what `TEAM.md` writes. With it, every
`start` reads the preset again and the team PLAYS as both make it: the preset's `form:` makes the edges when
`TEAM.md` writes no `reports:`, the root when it writes no `root:` (the first member; a root written is the form's
head), and adds the daily to `ceremonies:` -- the value `daily` its rhythm, two members or more reporting to the
root in the edges as the team plays, `TEAM.md`'s own when it writes `reports:` -- unless `TEAM.md` writes a
ceremony named `daily`; the preset's `budget:`, `launches:`, `timeout:` and
`schedule:` are the defaults of `TEAM.md`'s own keys. A preset without `form:` makes no edge and no root:
`TEAM.md` writes its own. A member added under `agents:` or a preset changed takes effect at the next `start`,
no edge written; `declaration` says the gap first. One function reads a declaration (`team_played`): `start`,
`declaration`, `declare`, the roster, the members `status` and `delete` say. Kept by every season at
`team-started.template` (`{template, origin}`; no key without a preset), the values `TEAM.md` applies at
`team-started.values` (`{name: value}`).

`TEAM.md` is the OWNER'S file: pp writes it on the owner's gesture alone (`team declare`: the keys its flags name,
the rest at its bytes), never in season. Its BODY is the owner's word:
the head of `TEAM-<name>.md` serves it by its name, as it stands -- no hole is filled --, and a member reads it
again as soon as it changes, without a start; a `TEAM.md` without a body is not served. `TEAM-<name>.md` is pp's:
RENDERED by every `start` -- its head, then for its body the INTENTION of the preset `TEAM.md` names, each hole
filled for the team as it plays: the values `TEAM.md` applies, then the ten values built in every team preset,
which the form makes of the members (`{root}`, `{others}`, `{chain}`, `{last}`, `{squads}`, `{workers}`, `{tree}`,
`{quorum}`, `{count}`, `{daily}`); empty without a preset. A member added or a preset changed is in the
intention at the next season. Its digest is kept at `team-started.rendered`: retouched, the next `start` refuses
`rendered-edited`; a `TEAM-<name>.md` no start rendered whose body is not that intention refuses
`intention-misplaced` -- the words belong in the body of `TEAM.md`, and pp moves nothing.

`documents: |` of `TEAM.md` and of `SEASON.md` -- the same grammar, read by ONE code (`documents_of`) -- names the
documents of each key, one `<key> <document> ...` per line, each key once in a file: the key `all` for every
member, a role key for the members who hold it, or a hole `{<name>}` a value fills; each document
`<directory>/<name>`, a template the house sees, or `<name>`, a file `<name>.md` of the team's directory, once on its
line. A preset's lines are the defaults of the file that names it: a line of the file replaces the preset's line
of the same key once both keys are filled. `SEASON.md`'s lines are ADDED to `TEAM.md`'s for the season: a key both
files name receives the documents of both. Every `start` renders each document ONCE (`documents_rendered`), as
`TEAM-<name>-<document>.md`, `<document>` the last part of its name -- at the root when the key `all` names it,
under `roles/` otherwise: a template's body under its conducted head, its holes filled (`document_rendered`); a
file of the team's directory as it stands, refused `document-holes` when it has a hole. The values: the presets
and the documents declare them, `TEAM.md` gives them, `SEASON.md` gives them over `TEAM.md`'s name by name,
`{team}` built in. A line taken out, its documents leave at the next `start`. Kept at `team-started.documents`
(`[{document, template, origin, roles}]`), their digests at `team-started.rendered`, the digest of `SEASON.md` at
`team-started.season-digest` when it says documents or values.

  pp-team start <name> [--message <text> [--to <member>]] [--budget <usd>] [--budget-launches <n>]
                       [--context <n>%] [--provider <name>] [--harness <command>] [--model <m>]
                       [--permissions auto|strict|bypass] [--effort low|medium|high|xhigh|max] [--no-tick]
                       [--package <name>=on|off]...
                       [--member <member> [--provider|--model|--effort|--permissions <v>]
                        [--package <name>=on|off]...]...
      -> a SEASON: the first one, or the next one once `team stop` has ended the last -- a team in season
         refuses `season-running`, naming `team stop`, nothing written; the members' runs kept, the cost,
         budget-spent, budget-launches and each task's launches: counted afresh; a start after a stop writes
         `since` at `team-started`, the hour from which nothing is made up: each recurrence and each ceremony
         counts its periods from it; `--message` optional -- without it no task opens, the
         season stands on its ceremonies and the posts to come, the relaunch entry laid only under an
         open task or a declared ceremony; the
         season's budget at `team-started.season`, its context limit `--context <n>%` (1% to 99%,
         `context-invalid`) written to SEASON.md as `context:` -- the limit of a task without its
         own --, the team's packages (`--package` before the first
         `--member`: every member's run, over its agent's SETTINGS) at `team-started.packages`, each
         member's profile at `team-started.profiles` -- its own `--package` covers the team's name by name
         (`participant-unknown`, `package-invalid`, `package-required`, `package-unpinned` for a package
         not pinned switched on, `package-dependency` for a package switched on whose requirement the
         season switches off, `budget-invalid` -- all judged before any write);
         `--max-budget-usd` refuses `flag-retired`, nothing written: a wake-up's share is computed on
         the team's `budget:` (`team budget` raises it);
         the season is SEASON.md's (below): without a flag `start` opens the season the file writes, two starts
         without a flag the same season; a flag covers the file's value for its key and is WRITTEN there, key
         by key -- a team's flag its key, a `--package` its line of `packages:`, a member's flag its key on the
         member's line of `profiles:` --, every other key, line and the body at their bytes, after every judge
         and before `team-started`; the file born when a flag gives a value, with those keys alone;
         `TEAM.md` read WHOLE with the preset it names and judged before anything is written (`team-unknown`,
         `team-invalid`, `root-missing`, `participant-unknown`, `ceremony-cycle`, `template-unknown`,
         `template-invalid`, `value-unknown` -- a value nothing declares --, `value-missing` -- a value
         without a default nobody gives --, `value-undeclared` -- a hole nothing declares --,
         `rendered-edited` and `intention-misplaced` on `TEAM-<name>.md`,
         `entry-missing` -- an entry absent from the instance of an agent that
         plays it; `common-code-prefix`, `common-collision`, `common-tool-unknown`,
         `common-serve-unknown` -- a `TEAM-<name>-<x>.md` declaring `mount:` judged at every member,
         a member not born at the house's machine: `common_judged`); then the DOCUMENTS of `TEAM.md` and
         `teams/<name>/SEASON.md` read and judged (`documents:` above, `season-invalid`, `document-unknown`,
         `document-collision`, `document-holes`, `role-unknown`), each document judged as it will stand --
         `rendered-edited` (a document the last start rendered, edited since: never written over),
         `document-collision` (a name a file no start rendered holds), the mounted ones by `common_judged` --,
         a role key without a member and a document that reaches nobody said, never refused;
         the agents the house lacks born at their paths, each path once, under
         the house's birth lock for that path (`install(…, borrow=True)`: an instance that borrows
         the house's machine, no door); then the team's documents written in ITS directory,
         `teams/<name>/` -- the root of documents of every run the team opens (`agent start
         --documents`), nothing written in an agent's instance: the documents (each
         `TEAM-<name>-<document>.md` rendered, at the root or under `roles/`, each no line names any more
         removed), the members' sheet
         `TEAM-<name>-members.md`, rewritten (no front matter: one row per member -- whom it reports to, its
         role keys when the team declares any,
         the model and effort of its profile, else of the launch, else the agent's default, the
         `description:` of its `MEMBER.md`, `no description` when absent or still the kit's template);
         then `TEAM-<name>.md`, always: its HEAD (attached at the kit's `turn.begin`, `proc: SERVE`
         serving the document itself, `TEAM.md` when its body says something, `TEAM_WORK.md`, `SEASON.md` when
         its body says something, then every
         `TEAM-<name>-<x>.md` of the directory by name, read by
         their names alone, but the ones that declare `mount:` -- the engine mounts them; with entries,
         `next:` every entry of the team then `TEAM-IDLE.md`, `decide: pp-team entry <name>`), then its BODY --
         the intention of the team's preset, rendered again, empty without one --, its digest and those of
         the documents kept at `team-started.rendered`; `TEAM.md` is never written;
         and, with entries, the neutral `TEAM-IDLE.md` (from
         `agent-idle.md`); `team-started.documents` keeps the documents, `team-started.season-digest` the
         digest of SEASON.md when it says documents or values; and `TURN.md`, always: the overlay of the
         kit's turn, which carries `output: team-act` (`ACT_FORMAT`) and nothing else, so that the WORK
         line of every exchange of a run opened under the team's directory asks for the form of an act
         (`WORK team-act => words`); such a run needs the package `team` switched on -- the team's own
         launches always have it, a run a principal opens there with `team` switched off refuses
         `format-unknown` at `-new`; a `TURN.md` an earlier version wrote there is replaced by the
         overlay, and stderr says so; any other `TURN.md` standing there is the owner's: it is kept,
         stderr says so, and the team's runs then play the turn it writes -- they ask for the form only
         if it carries `output: team-act`. At each agent of the team, what an earlier
         version laid there -- `procs/TURN.md`, `procs/TEAM-IDLE.md`, `skills/team-entry/` at the
         team's bytes, `procs/TEAM-<name>.md` deciding by `team-entry <name>` -- is removed; another
         is the agent's own: kept and said;
         then, under the journal's lock, `team-started` (the launch flags kept under `launch`),
         `task T<n>` and the `do` post from the owner to `--to` or the root; then a tick, unless
         `--no-tick`.
  pp-team post <name> [--message <text>] [--to <member>] [--task <id> [--ask] | [--name <text>] [--context <n>%]]
                      [--reply <id>] [--stop] [--as <principal>] [--no-tick]
      -> without `--task` a NEW task (`task` + its `do` post) to `--to` or the root, `--name` its name --
         one line of 1 to 80 printable characters, a user's text (`name-invalid`; at `start` too),
         `--context <n>%` its context limit, over the season's (`context-invalid`): its run is renewed
         at the wake-up after it parks past it (`run-renewed`); with
         `--task` an `info` on that task -- read at the member's next wake-up, it waits for no answer;
         an `ask` under `--ask`: a principal's QUESTION to the member, which the member's answer `re`
         settles; a `reply` under `--reply <id>`, a `stop` under `--stop` --; `--ask` without `--task`,
         or with `--reply` or `--stop`, gives the usage; `--as` a mandator or the owner (`principal-unknown`); `team-not-started`,
         `season-stopped` (off season: a post waits for the next `team start`), `task-unknown`, `task-closed`,
         `message-unknown`, `message-missing`; then a tick.
  pp-team stop <name> [--kill] [--json] [--no-tick]
  pp-team stop <name> --task <id> [--kill] [--no-tick]
      -> without `--task` nor `--recurrence`, ENDS THE SEASON: every open task stopped as below, then
         `season-stopped {by, tasks, recurrences}` -- the tasks it stopped and the recurrences it silences:
         those still live and not paused. A paused recurrence is silent already: it is not named, and it
         stays paused. Every recurrence keeps its own state --, both named in its output and,
         under `--json`, in ONE object `{team, stopped: {id, tasks, recurrences}}`; a pause under way ends
         with it. Until the next `team start` the team is OFF SEASON: the tick wakes nobody, rings no
         ceremony, sounds no recurrence and arms no timer, the relaunch entry is removed, and only then does
         `team declare` write TEAM.md and SEASON.md; nothing missed off season is made up. With `--task`, ONE
         task: `stopped {task, by}` -- the task stops whatever holds it --, then a `stop` post to every member
         holding the task (its member unless terminal, and every delegate without a terminal; none when nobody
         holds it: `stopped -- nobody held it`), delivered at once -- to a run STANDING on the task, at the head
         of one more launch; the posts left undelivered on it `returned`. A wake-up under way ends on its own
         and its answer is routed nowhere -- under `--kill` it is ended now by its launcher's process group
         (`wake-killed`), nothing kept, never retried. Judged under the journal's lock: `team-unknown`,
         `team-not-started`, `season-stopped` (off season already -- with `--task` and `--recurrence` too),
         `task-unknown`, `task-closed`.
  pp-team tick <name>                 -> ONE advance of the team (below); an on-end tick carries `PP_AGENT_RUN`
                                         and `PP_AGENT_STATE`, the end of the launch that fired it
  pp-team tick --all [--entry]        -> one advance of every team of the house that needs its net, in the order
                                         of their names; a team that fails is said on stderr, the others advance.
                                         `--entry` is what the house's relaunch entry plays at logon: the PATH
                                         kept at `state/relaunch.path` when the entry was laid replaces the tick's
                                         own before any team advances (absent: the tick keeps its own)
  pp-team follow <name> <tag>         -> the FOLLOWER of one launch: keeps `agent flow --from --follow` open on
                                         its flow, routes each act as it comes, writes the launch's end at its
                                         `verdict`, ticks after; spawned detached by the tick at every launch,
                                         its output at `follow.log` beside the journal
  pp-team status [<name>] [--json]    -> the state read from the journal; without a name, one
                                         line per team declared under `teams/`. Under `--json`
                                         the face a program reads: ONE object for the team named
                                         (its state and what it waits on, its season, its launch,
                                         its tasks and the wake-ups under way on each, members,
                                         ceremonies with their next ring, the owner's box), one per
                                         line without a name (its state, `asks` and `done` as the
                                         inbox counts them); each says `team`, the directory -- the
                                         team's identity --, and `name`, the `name:` of its `TEAM.md`
                                         (one line of 1 to 80 printable characters, `name-invalid`;
                                         the directory's name without it), read at every call: a
                                         rename moves nothing. The texts say the name, the directory
                                         after it when they differ. Nothing written.
  pp-team watch <name> [--task <id>] [--json] [--heartbeat <s>] [--for <s>] [--until-done]
      -> a READER: the journal's events as they arrive, the steps of every wake-up under way and
         what its harness does between two steps -- its flow read by `agent flow --follow`: a
         tool called, its result by its size, a thought, the words, the context measured --
         on stderr (`[HH:MM:SS] <team> · #<id> <kind> …`, `[HH:MM:SS] <member> · <run> · <step>`,
         `[HH:MM:SS] <member> · <run> · tool <name> · <title>`), `no event for <n>s` after
         `--heartbeat` seconds without one (60), one JSON object per line under `--json` (an
         activity: `event: activity`, its `kind`, at most ACTIVITY_RATE a second per wake-up,
         `more` on the one said for those it stands for); until Ctrl-C, `--for` seconds, or
         `--until-done` (no wake-up under way, and no task open or nothing due on them). No lock,
         nothing written, never a tick. Read in the HOUSE, whatever instance calls.
  pp-team log <name> [--task <id>] [--last <n>] [--json]
      -> the journal, one line per event, on stdout; under `--json` one object per event, the
         form `watch --json` writes (`event_object`). Read in the HOUSE, whatever instance calls.
  pp-team result <name> [<task>]      -> a resolved task's result as JSON on stdout (the last
                                         resolved without a task); `task-open`, `result-missing`.
                                         Read in the HOUSE, whatever instance calls.
  pp-team stats <name> [--season <n> | --all] [--cost usd|launches|tokens] [--json]
      -> the numbers of one SEASON of the team, computed from its journal alone: the season under way,
         else the last one; `--season <n>` another; `--all` each season in which a wake-up launched,
         then their median, the seasons without one listed apart. A season runs from one `team start`
         to the next; its number counts the starts from 1. A WAKE-UP is one launch of a member, from its
         intent to its end. For a season: its dates and its state (`running`, `paused`, `stopped`); its
         tasks closed, stopped and open -- a task shows in each season where it is born, woken, closed or
         stopped, and counts there only the wake-ups of that season; closed and stopped count what closed
         or stopped in the season --; its cost, per closed task and per launch; the cost of a task
         (least, median, most, and each task's) and the cost of each role key with its share -- a member
         who holds two keys counts under the first one, in the order of `team-started.roles` --; three
         times -- ELAPSED, the clock time from its start to its end or to now; ACTIVE, the clock time
         during which at least one wake-up runs; EFFORT, the durations of all its wake-ups added up,
         more than the active time when several members work at once --; its PARALLELISM, effort
         divided by active time: how many members work at once, on average; the effort in each slot of
         2 hours from its start; the wait before a wake-up launches (median, and p90: the value nine
         wake-ups in ten do not pass); the questions members asked a principal, how many were answered
         and how long they waited, and the same for the questions a principal asked a member
         (`post --ask`, `principal.from_principal` under `--json`); the share of the context a wake-up left at its end, and the runs
         renewed; the losses -- wake-ups failed, their cost and their reasons, silences, and each `do`
         sent again to the same member on the same task. `--cost` chooses the unit every cost is said
         in: `usd` (by default) the dollars the provider reports, `-` when it reports none, never 0;
         `launches` the launches; `tokens` what the wake-ups sent the model, marked `~` (estimated) when
         a wake-up only gives the size of its last call. Under `--json` ONE object `{team, base,
         season}` (`{team, base, seasons, median, empty, by_task}` under `--all`), each cost in the three
         units at once (`null` where none is known), then one line per task and one per member: cost,
         launches, `do` and `re`, failed wake-ups, the three times, the largest share of context, and for
         a member its cost per launch and the median delay from a `do` it received to its `re`; a task's
         line also gives the hours of its first and last event in the season (`first`, `last`). Under
         `--all`, `by_task` gives each task over ALL its seasons, one line per task, made by pp-team: its
         costs, `do`, `re`, failures, active time and effort added up over its seasons; its elapsed time
         the clock time from its first event to its last, whatever the seasons between; the largest
         share of context kept; its name and state its last line's. `team-unknown`,
         `team-not-started`, `season-unknown`, `cost-invalid`; `--season` with `--all`:
         the usage. Read in the HOUSE, whatever instance calls. Nothing written.
  pp-team responses <name> [--since <id>] [--agent <a>] [--task <t>] [--last <n>] [--json]
      -> the responses the team's agents gave, one per `wake-ended`, the text read at the house's
         record by (agent, run, index); `--since` those after a journal id; under `--json` one
         object per response, its text whole or `null`. Nothing written. Read in the HOUSE,
         whatever instance calls.
  pp-team inbox [<name>] [--seen [--id <n>] | --json]
      -> one line per team where something waits for the owner (the questions without a reply on
         an open task, the infos, the tasks resolved and the posts returned since the last
         `inbox-seen` and not read one by one), one object per such team under `--json`. An ask
         whose task is resolved or stopped is no longer a question: nobody can answer it any more
         (`task-closed`); until it is read it is listed with the infos, `closed: true` under
         `--json`, and counted as an info. `--seen` writes `inbox-seen`, `--seen
         --id <n>` writes `inbox-read` for the one message n -- the writes of these readers; a
         question refuses `inbox-question` (its answer alone takes it out), an id the inbox does
         not hold `inbox-id-unknown`. Read in the HOUSE, whatever instance calls; `--seen` writes
         at the instance that calls.
  pp-team roster [--json]
      -> the teams of the HOUSE -- the machine this script lives in, whatever instance calls it --, read: one
         row per team declared under `teams/` (`team`, `name`, `description` or `—`, `root`, `members`,
         `state`, `membership` -- the caller's part: `root (<member>)`, `member (<member>, …)` by the
         paths of `agents:`, `—` for none and at the house itself), then one row per live recurrence
         (`team`, `id`, `description` -- else its name --, `when`, `next_due`, `paused`); under `--json`
         ONE object `{teams, recurrences}`. Nothing when the house declares no team, nor in a run a team
         opened (`PP_RUN` naming a run whose root of documents is a team's directory): the contributor
         `TEAM_ROSTER.md` plays it at every exchange outside them. Nothing written.
  pp-team entry <name> [--run <key>]  -> the document the team's wake-up under that run (`PP_RUN`
                                         when `--run` is absent) plays this exchange: its task's
                                         ceremony's entry, else `do`'s, else `TEAM-IDLE.md` -- also
                                         for a key no wake-up of the team holds. The decider of the
                                         team's document, played by the engine of the agent; the
                                         house is the machine this script lives in. Nothing written.
  pp-team reset <name> [--member <m>] -> the run of each member named (every member without
                                         `--member`) FORGOTTEN by its agent's console (`-reset
                                         <key>`), then `run-reset {member, run}`: its next wake-up
                                         opens a new run told every open task; judged first under
                                         `tick.lock` (`team-busy` past `call_lock_wait`):
                                         `team-not-started`, `participant-unknown`, `member-running`.
  pp-team pause <name> [--as <principal>]
      -> PAUSES the team: judged under the journal's lock (`team-unknown`, `team-not-started`,
         `principal-unknown`, `team-paused` -- paused already), then `paused {by}`. Nothing is killed: the
         wake-ups under way end on their own and the tick reaps them and routes their answers; until the
         resume, the tick rings no ceremony and wakes nobody -- a post, a stop, a ring at hand, a budget, a
         task's resume or a season are written as ever, and the tick they play says `paused: nobody woken
         until team resume`. A start keeps the pause; `team stop` ends it, and a team off season refuses
         `season-stopped`. No tick.
  pp-team pause <name> --recurrence <R<n>> [--as <principal>]
      -> SUSPENDS one recurrence: judged under the journal's lock (`team-unknown`, `team-not-started`,
         `principal-unknown`, `recurrence-unknown`, `recurrence-stopped`, `recurrence-paused` -- suspended
         already), then `recurrence-paused {recurrence, by}`. It sounds no period and arms no timer until its
         resume; it stays live -- `team recurrence` changes it, `team stop --recurrence` stops it --, its open
         occurrence lives on. Independent of the team's pause. No tick.
  pp-team resume <name> [--as <principal>] [--no-tick]
      -> RESUMES the paused team: judged under the journal's lock (`team-unknown`, `team-not-started`,
         `principal-unknown`, `team-not-paused`), then `unpaused {by}`; then the relaunch entry laid again,
         and a tick: what is due NOW -- each member due woken in its own run, the day's period of a ceremony
         rung when its hour is past and it never rang; a period passed during the pause is never rung.
  pp-team resume <name> --recurrence <R<n>> [--as <principal>] [--no-tick]
      -> RESUMES one suspended recurrence: judged under the journal's lock (`team-unknown`, `team-not-started`,
         `principal-unknown`, `recurrence-unknown`, `recurrence-stopped`, `recurrence-live` -- not suspended),
         then `recurrence-resumed {recurrence, by, since}`, `since` the local hour of the resume; then the
         relaunch entry laid again, and a tick unless `--no-tick`. Nothing is caught up: its next period is the
         first after the resume -- a conforming day whose hour follows it, for a duration `since` + the duration.
  pp-team resume <name> --task <id> [--to <member>|all] [--message <text>] [--as <principal>] [--no-tick]
      -> takes back ONE task a guard left with nobody due: STOPPED, held by a member's final failure,
         past `launches:`, a member HALTED on it (`wake-halted`), or a member of it held by a provider's
         limit without an hour (`quota-reached`). Judged under the journal's lock before anything is
         written (`team-unknown`,
         `team-not-started`, `principal-unknown`, `member-unknown` -- `--to` names no member of the season
         --, `task-unknown`, `task-resolved`, `budget-spent` -- the team's `budget` or `budget-launches`
         reached: never reset by a resume, raised by `team budget` --, then `task-not-blocked`);
         then `resumed {task, by, from}` -- the task open again, its members' failures at zero, the
         terminals its final failures wrote dropped, its halts and its members' limits without an hour
         lifted, its wake-ups counted afresh -- and an `info` (the
         message, `the task resumes` unless said) to each member it revives: the holders at the stop,
         the members whose final failure stands, the members halted or held by a limit without an hour,
         the members with messages due past `launches:`. Under `--to`, the `info` goes to the one member
         named instead, or to every member of the season under `all`; `--to` without `--task` gives the
         usage. The posts returned at the stop stay returned. Then the relaunch entry laid again, and a tick.
  pp-team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]
      -> RAISES the team's `budget` (dollars) or `budget-launches` (wake-ups) without a start: judged
         under the journal's lock (`team-unknown`, `team-not-started`, `principal-unknown`,
         `budget-invalid` -- a number at or below what the team spent since its start: the cost kept,
         the launches); then `budget-raised {budget, launches, by}` -- the replay's limits raised,
         `budget-spent` lifted: the next exhaustion writes it again --; the members keep their runs.
         Then the relaunch entry laid again, and a tick.
  pp-team ring <name> <ceremony> [--as <principal>] [--no-tick]
      -> rings a declared ceremony AT HAND, out of its hour: what the tick's ring writes --
         `ceremony-due {ceremony, period, by}`, ONE task from the team to the facilitator, its opening
         `do` to the facilitator, a `do` per participant -- under the period `manual-<id>`, the id of
         its own `ceremony-due`: no date is taken, the `every` rings its day at its hour all the same.
         Judged under the journal's lock first: `team-unknown`, `team-not-started`, `season-stopped` (off
         season), `principal-unknown`, `ceremony-unknown`, `ceremony-open` (a task of the ceremony still
         open). Then the relaunch entry laid again, and a tick.

  teams/<name>/SEASON.md -- the season's values, the owner's file, read at every `start`, written by `team declare
  --season` never in season:
         ---
         template: <directory>/<name>   a SEASON preset the house sees: `documents:` without `form:`, `members:`
                                        or `reports:`
         values: |
           <name> = <value>             one per value the preset and the documents declare; one with a default may
                                        be left out; a name `TEAM.md` gives too takes this value
         documents: |
           <key>|all <document> ...     the lines the season ADDS to `TEAM.md`'s (`documents:` above)
         provider: harness: model: permissions: effort:   the team's launch, each member's default
         budget: budget-launches: silence: context:   the season's own limits, over TEAM.md's
         packages: |
           <name>=on|off                one per package named; a pin it does not name: on when the team needs it
         profiles: |
           <member> <key>=<value> ...   provider, model, effort, permissions, silence, package.<name>=on|off
         work: <repository>             the material every opening gets (`--work`, a clone per run)
         ---
         <the owner's word>             served to every member as it is, read again as soon as it changes
      -> without the file, or without `template:` and `documents:`, the season adds no document: none is chosen in
         silence. Without the file or the season's keys, the season opens on the team's defaults. The season's keys
         are judged by `start`'s own judges before any write: `season-invalid` (a front matter the engine cannot
         read, a key `SEASON.md` does not say, a line of another form, a key or a value said twice, a name or a member
         twice), `template-unknown` (no season preset of that name), `template-invalid`, `document-unknown`,
         `document-collision`, `document-holes`, `value-unknown`, `value-missing`, `value-undeclared`, `role-unknown`
         (a key of a line `roles:` does not declare, the line and its file named), `rendered-edited`,
         `budget-invalid`, `participant-unknown`, `package-invalid`, `package-required`, `package-unpinned`,
         `package-dependency`, `grammar-missing`. `work:` in TEAM.md refuses `key-moved`, naming SEASON.md.

  The documents of a ROLE -- the VIEW of a member (`view_of`, the one place that decides who receives what): every
         `TEAM-<name>-<x>.md` at the root of the team's directory is for everyone -- served by the head of
         `TEAM-<name>.md`, or mounted by the engine when it declares `mount:`; a document written by hand has no
         filter. A document whose lines name role keys and not `all` is rendered under `teams/<name>/roles/` -- always
         opening on a front matter, empty when it keeps no key --, which the engine's flat reading of the root never
         sees, and is MOUNTED by the vector `team-member:<team>/<member>` (the family this
         package declares) in the runs of the members who hold one of its keys, once whatever the keys they share:
         its laws in force, its tools offered and its body served when it declares `mount:` (`mount: turn.begin`,
         the one moment a vector mounts at), its body alone otherwise. A document of a role missing on disk stays
         in its members' views: their next launch fails `vector-refused`, `mount-missing` naming it; a start
         renders it again. Every launch of a member passes the whole set
         of its vectors -- its task's, then its own when its season's view holds a document of a role --, `--vector -`
         when that set is empty. `start` and `declaration` judge the view of EACH member: `common-code-prefix`,
         `common-collision` (a code twice in one member's view -- two documents of disjoint roles may share it -- or
         declared at the member), `common-tool-unknown`, `common-serve-unknown`, `common-mount-moment` (a document of
         a role mounted at another moment than `turn.begin`), the member and the document named.
  pp-team verify            (the vector `team-member:<team>/<member>` on stdin)
  pp-team mount <team>/<member>
      -> the engine's and the launcher's calls, never an agent's -- `pp-team` is offered at `TURN` (the package's
         overlay) for the launcher's gesture to play. Both judge the vector for the instance and the run that ask:
         `team-unknown`, `team-not-started`, `member-unknown` (a member the season under way does not know),
         `member-foreign` (the instance calling, `PP_HOME`, is not the agent that plays the member), `root-foreign`
         (the run's root of documents is not the team's directory); `verify` also refuses `family-foreign`. `mount`
         then prints ONE `::mount` line, an entry per document of the member's roles in its season's view, in the
         order of the documents -- `{doc: roles/TEAM-<team>-<document>.md, body: true}`, plus
         `constraints: false, tools: false` for one that does not mount --, nothing for a member without one. Both
         read only: nothing written, no lock, never a tick.

  pp-team declaration <name> [--json] [[--season] --text-file <path>|-]
      -> the declaration READ: `TEAM.md` whole, the verdict of `start`'s own judge -- `ok`, or the
         refusal `start` would write, said with rc 0 (a broken `TEAM.md` is shown to be mended, never
         refused), `SEASON.md`, the documents, the mounted documents' judge and `entry-missing` included -- and
         its GAP to the last start: `{key, started, declared}` per key `team-started` kept that the files now say
         otherwise (`agents`, `reports`, `root`, `principals`, `ceremonies` by their lines, `entries`, `limits`,
         `schedule`, `roles`, `template` by its name, `values` as applied) -- each side the team as it plays: a
         member added under a form puts `agents` AND `reports` there, the edges the form makes -- what a new
         `start` would change, `launch`, `season`, `packages`, `profiles` and `work` when SEASON.md opens the season
         otherwise than the last start kept it, and `documents` when the documents the next start renders -- their
         names, keys and digests -- differ from those the last start rendered; the bodies are never pending, pp
         serves them at once; `changed` counts `SEASON.md` beside `TEAM.md`. Under `--json` ONE object `{team,
         name, description, path, text, digest, verdict: {ok, refusal}, started: {at, id, digest, state} | null,
         changed, pending, season: {path, text, digest} | null, declared}` (`started.state` `running` in season,
         `stopped` off season; `declared` what the next start writes and `pending` a list, both null only when
         `TEAM.md` itself is refused -- a refusal of the season, the entries, the documents or the directory leaves
         them, `declared.season`, `.documents` or `.values` null as the case may be: `declared.agents[]` each
         member with its `path`, `born`, `packages`, its
         `description`, as the members' sheet says it, and its `roles`; `declared.root`, `.reports`, `.principals`,
         `.ceremonies`, `.entries`, `.limits` and `.schedule` what `TEAM.md` writes, else what its preset makes;
         `declared.work`; `declared.season` what a start without a flag opens, `{launch, limits, packages,
         profiles, work}`, null when refused; `declared.roles` the role keys in the order declared, `[{role,
         members}]`; `declared.documents` the lines of `documents:` by key, `[{key, team, season}]`, null when the
         documents are refused; `declared.views` each member's view as the next start renders it, `[{member, roles,
         documents: [{document, template, roles, effect, by}]}]` -- `effect` `served` or `mounted`, `by` `head`,
         `engine` or `vector`; `declared.template` the preset `TEAM.md` names, `{template, origin, values: [{name,
         value, from}]}` -- `from` `team` or `default` --, null without one; `declared.values` the values the
         documents apply, `[{name, value, from}]` -- `from` `team`, `season`, `default` or `built-in`); the text
         says the path and the text, SEASON.md's path and text when it stands, `verdict ok` or the refusal, the
         preset named with its values, a line per role key (`no member` for a reserved one), then a line per key
         pending, or `not started`.
         Under `--text-file`, a CANDIDATE text -- a file, or `-` for standard input -- is read in the place of
         `TEAM.md`, or of `SEASON.md` under `--season`, and said as if it were written: its text, its verdict,
         `declared` and each member's view; `--season` without `--text-file` is the usage; a path that is no
         file refuses `team-invalid`. Nothing written, no lock, never a tick; `team-unknown`, the usage.
  pp-team templates [--json]
      -> every TEMPLATE the house sees, one line each -- its name, its kind, its origin, a team preset's default
         members, what it is --, then one line per value it declares and, for a preset, one line per line of its
         `documents:`. A template is a file `<directory>/<name>.md`, named `<directory>/<name>`, each part a slug;
         the directory is the owner's choice and only groups files. Two places only: `<house>/.pp/teams/templates/`
         then the team package's `templates/`; a name of the house replaces the package's; a template whose
         `requires:` names a package the house does not pin is not seen. A template is a PRESET when it carries
         `documents:`, `form:` or `members:`; its lines are the defaults of the values file that names it by
         `template:` -- a line of the file replaces the preset's line of the same key, once both keys are filled.
         Two lines of the preset that fall on one key once filled refuse `template-invalid`, citing the preset,
         wherever a values file names it -- as two lines of the file refuse in that file. A preset is a TEAM
         preset when it carries `form:`, `members:` or `reports:`, a SEASON preset otherwise: `TEAM.md` names only
         a team preset, `SEASON.md` only a season preset -- another refuses `template-unknown`, nothing written. A
         team preset also makes the team's members, edges and intention. Any other template is a DOCUMENT: a line
         of `documents:` names it, and `start` renders it. Each template says the values it declares (`values: |`,
         `<name> [= <default>] -- <description>`). Under `--json` one object per template, `{template, kind,
         origin, description, values}` -- `kind` `preset` or `document`, `origin` `house` or `package`, each value
         `{name, description, default}` --, `requires` when it names packages, a preset's `documents` (`[{key,
         documents}]`, the keys as written: a template knows no team) and, for a team preset, `{form, members,
         root, reports, ceremony, limits, intention}`, the team it makes for its default members, with `roles`
         (`[{role, places}]`, the places as written, `{root}`) when it has `roles:` -- without
         `members:`, the members its `root:` and its `reports:` name, the root first, then each member of an edge
         in its order. A template the verb cannot read -- a front matter the engine cannot read, a
         line of another form -- still has its line, which gives the refusal instead: `<name>  refused · <origin>
         -- <refusal>`, under `--json` `{template, origin, refusal}`; the other templates are listed as usual.
         That refusal, `template-invalid`, stops only a values file or a line that names the template. Nothing
         written; a template name that is no slug refuses `template-invalid`, citing the file.
  pp-team templates --render <directory>/<name> [--value <name>=<value>]... [--team <name> [[--season] --text-file <path>|-]] [--json]
      -> ONE document, exactly as `start` writes it in a team's directory: its head and its body, each hole `{<name>}`
         filled. Nothing is written. Each hole takes its value from, in this order: a `--value` given; under `--team`,
         the team -- `team` is its name, then the values of its `TEAM.md`, then those of its `SEASON.md`, which win;
         the default the template declares. Under `--text-file`, a text -- a file, or `-` for standard input -- is
         read in the place of `TEAM.md`, or of `SEASON.md` under `--season`; the other file is read on the disk. The
         values are then the ones `start` would take if that text were written. A `--value <name>=` left empty takes
         the value away: then neither `TEAM.md` nor `SEASON.md` gives it, even under `--team`, and the hole takes the
         template's default, or refuses `value-missing`. Without `--json`, the document's text alone; under `--json`,
         ONE object `{template, text, values}`, each value `{name, value, from}` -- `from` is `given` for a
         `--value`, `default` for any other.
         Refuses: `template-unknown` -- no document of that name, or a preset, which renders no document --,
         `template-invalid`, `team-unknown`, `team-invalid` for a `--text-file` path that is no file, the team's
         own refusal, `value-unknown` -- a `--value` the template does not declare --, `value-missing` -- a hole
         left without a value, named; `team` needs `--team` or `--value team=<name>`, and a value taken away needs a
         `--value` that is not empty. These are the usage: a `--value` without `=`; `--value`, `--team`, `--season`
         or `--text-file` without `--render`; `--season` or `--text-file` without `--team`; `--season` without
         `--text-file`.
  pp-team document <directory>/<name> [--new | --body-file <path>|- | --delete] [--json]
      -> reads one DOCUMENT of the house, or writes it: the one verb that writes
         `<house>/.pp/teams/templates/<directory>/<name>.md`. Without an action, it prints the source of the document
         the house uses -- the house's file, else the package's --: its name, kind, origin and path, then its whole
         text; under `--json`, ONE object `{template, origin, kind, path, text}`. Nothing is written. `--new` creates
         the house's document from a skeleton (a `description:` to fill, a title and a sentence to replace); its
         directory is created when needed; `--new` on the name of a preset of the package refuses, because the house's
         document would hide that preset. `--body-file` replaces the text of the house's document by the text of the
         file, or of standard input for `-`, read byte for byte: its line endings stay as written, so a text equal to
         the file writes nothing. The text is checked before anything is written: its front matter must be
         readable, it must carry no key of a preset (`documents`, `form`, `members`), and its `values:` must have the
         form a template's values have. `--delete` removes the house's document, and its directory with the last
         document in it. A house's document hides the package's document of the same name: `--new` says so, and
         `--delete` says that the package's document is used again. Under `--json`, an action prints ONE object
         `{template, done, path, package}`. The verb never writes a team's file, a journal or the package; a refusal
         writes nothing. Refuses: `template-invalid` (a name that is not `<directory>/<name>`), `document-unknown` (no
         document of that name, or a preset to replace or delete), `document-exists`, `document-preset` (`--new` on the
         name of a preset of the package), `document-readonly` (a document
         of the package, to replace or delete), `document-invalid`, `document-used` (a line of `documents:` in a
         `TEAM.md`, a `SEASON.md` or a house's preset still names it; each one is said, with its file and its key).
         Two actions at once is the usage.
  pp-team declare <name> [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]...
                     [--document "<key>|all <document> ..."]... [--no-document <key>]...
                     [--body-file <path>|-] [--member <name> <path>]... [--no-member <name>]...
                     [--role <key> [<member> ...]]... [--no-role <key>]... [--report "<member>... -> <member>"]...
                     [--no-report <member>]... [--root <member>] [--principal <p>]...
                     [--budget <usd>] [--launches <n>] [--parallel <n>] [--timeout <s>]
                     [--schedule <n>s|<n>m|<n>h|<minutes>|off] [--description <text>] [--json]
  pp-team declare <name> --season [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]...
                     [--document "<key>|all <document> ..."]... [--no-document <key>]...
                     [--body-file <path>|-] [--budget <usd>] [--budget-launches <n>] [--silence <n>]
                     [--context <n>%] [--provider <name>] [--model <m>] [--effort low|medium|high|xhigh|max]
                     [--permissions auto|strict|bypass] [--harness <command>] [--package <name>=on|off]... [--json]
                     [--member <member> [--provider|--model|--effort|--permissions|--silence <v>]
                      [--package <name>=on|off]...]...
      -> a team's VALUES WRITTEN, the team born or standing: the one verb that writes `teams/<name>/TEAM.md` --
         or, under `--season`, `teams/<name>/SEASON.md`, the documents and values the season adds to the team's
         (the team must stand: `team-unknown`). Without the file, it is written from the flags; with it, the keys
         the flags name are written and they alone: every other key, every other line of a block and the body
         stay at their bytes -- a `reports:`, a ceremony, an entry, a `name:`, a comment written by hand are never
         touched. Each flag its key: `--template <directory>/<name>` `template:`, a preset; `--value
         <name>=<value>` its line of `values:` (`<name> = <value>`, the value empty or not); `--document "<key>
         <document> ..."` the WHOLE line of its key in `documents:` -- the key `all` for every member, a role key
         for the members who hold it, or a hole `{<name>}` a value fills; each document `<directory>/<name>`, a
         template, or `<name>`, a file `<name>.md` of the team's directory --; `--member <name> <path>` its line
         of `agents:`; `--role <key> [<member> ...]` the WHOLE line of the key in `roles:` -- its members are those
         the flag names, none reserves the key --; `--report "<member>... -> <member>"` the line of `reports:`
         whose target is the member after `->`, written whole; `--root` `root:`; `--principal` its line of
         `principals:`; a limit or `--schedule` its key; `--description` `description:`; `--body-file` the BODY,
         the owner's word, replaced by the file's text -- `--body-file -` by the text read on standard input --,
         read byte for byte: its line endings stay as written. Under `--season`, the season's flags of `start`
         (`--budget`, `--budget-launches`, `--silence`, `--context`, `--provider`, `--model`, `--effort`,
         `--permissions`, `--harness`, `--package`, then `--member <member>` followed by that member's own flags)
         write their keys in SEASON.md as `team start` writes them, and each is judged as `start` judges it: what
         `start` refuses, `declare` refuses with the same code, and nothing is written; `--json` may stand anywhere
         on the line. Each contrary takes its line out, the block with its last line: `--no-value <name>`,
         `--no-document <key>`, `--no-member <name>`, `--no-role <key>`, `--no-report <member>` (the edge whose
         target it is) -- nothing where no such line stands, and no file is born of contraries alone. A line of a
         block is named by its first word -- a value by its name before `=` --, and an edge of `reports:` by its
         target, the member after `->`: when several lines have the same name, a flag writes ONE line in place of
         all of them, and its contrary takes all of them out -- `--document
         "<key> ..."` leaves one line for its key, `--no-document <key>` none. A key the file lacks is laid at the end
         of the front matter. `--compose` and `--no-compose` refuse `flag-retired`, naming `--document` and
         `--no-document`; nothing is written. At a BIRTH (no `TEAM.md`): without `--member`, the members are the
         preset's defaults at `agents/<name>/<member>`; a preset without `form:` has its own `reports:` and its
         `root:` written as they stand -- a form's edges and root are never written: every `start` makes them
         again. Both files are written OFF SEASON alone -- before a first start, or after `team stop` --: in
         season `declare` refuses `season-running`, naming `team stop`, and nothing is written. `declare`
         REFUSES a write that makes one of `start`'s checks fail when that check passed before
         it: the declaration is read as it stands, then as it would stand with the text to write -- `TEAM.md` and
         `SEASON.md` TOGETHER, by `start`'s own checks, in `start`'s order: the team, the season, the entries,
         the documents, the directory. A check that passed at the first reading and fails at the second refuses,
         by `start`'s code, and nothing is written; at a birth, every refusal does. Among them:
         `template-unknown` (no preset of that name), `template-invalid`, `document-unknown` (a document that is
         neither a template nor a file of the team's directory, or a preset named on a line), `document-collision`
         (two documents of one name, a document named `members`, a name that a file no start rendered holds),
         `document-holes` (a file of the team's directory with a hole), `value-unknown`, `value-missing`,
         `value-undeclared`, `role-unknown` (a key of a line of either file that `roles:` does not declare),
         `team-invalid` (a member's path, a form given members it cannot hold, a limit that is no number, a
         `parallel` under 1, a line of another form, a `--report` that is not one edge, a name given twice or to a
         flag and its contrary, a line break), `participant-unknown`
         (a role, an edge, a profile of the season for a member nobody declares), `root-missing`,
         `season-invalid`, `package-…` (a package the season switches on that the house does not pin, or whose
         requirement is off), `entry-missing`, the mounted documents' (`common-…`: a document, a member or a role
         given, that lays a document in a member's view), the usage (a flag `declare` does not take, a `--value`
         without `=`, a `--document` without a key and a document, a flag of `TEAM.md` under `--season`, no key
         named). A check that already failed before the call, or that could not run because an earlier one
         failed, does NOT stop the write, even when the call adds a problem to it -- a rendered document edited by
         hand, a file laid under a name to render, the intention written by hand, a value of the other file, a
         `SEASON.md` written under a `TEAM.md` that is refused: it writes, answers rc 0, and `verdict` names the
         refusal `start` would give. Each check stops at its first problem: the one behind it is told by
         `verdict` once the first is gone. Written under the team's `tick.lock`, waited within `call_lock_wait`
         (`team-busy` beyond): two calls write one after the other. No event in the journal, no document
         rendered, nobody launched -- what is written applies at the next `team start`. Says the file, the keys
         written, `declaration`'s verdict and the gap to the last start; under `--json` ONE object `{team, file,
         written, verdict: {ok, refusal}, pending}` -- `written` the keys
         whose text changed in the file, in the order a birth lays them, `body` last: a call that changes nothing
         answers rc 0 with `written` empty and says so; `verdict` and `pending` as `declaration --json` says them:
         `ok`, or the refusal the next start would write, and what that start applies. `new`, the verb of before,
         refuses `verb-retired` naming this one.
  pp-team delete <name> [--yes] [--json]
      -> the team REMOVED with what it made: its timer, its relaunch entry, every run its wake-ups opened
         (`agent purge <path> <run>... --yes` by the house's console), its journal and the files beside it,
         then `teams/<name>/` whole; without `--yes` it says what it would remove and writes nothing; under
         `--json` ONE object `{team, name, dry, directory, journal, relaunch, timer, runs: [{member, path,
         run}], agents}` -- `agents` the paths the team declares that no other team does: they stay. Under
         `tick.lock` waited within `call_lock_wait`: `team-unknown`, `team-busy` (a task open, a wake-up
         under way, the lock held -- `team stop <name> --kill` first); `deleting` written first, so that the
         guard lets the team's runs go; a purge refused stops it, `delete-failed`, and `delete --yes` again
         goes on. The agents and the runs the team never opened stay.

A TICK takes `tick.lock` beside the journal WITHOUT waiting: held by another tick, it posts the
mark `tick.pending`, tries once more and exits 0 having written nothing. The holder clears the
mark, plays its steps, releases the lock, THEN reads the mark: set, it takes the lock again
and plays once more. A wake-up is ONE LAUNCH of the harness (`agent start … --launches 1`), and what
the member says in it is read AS IT COMES: each `words` of the launch (a block of text between two
calls of the tool, kept at the run's flow by the house) is read by `agent flow --from` -- by the
launch's FOLLOWER while it plays, by the reap after --, and each ACT a `words` carries (`candidates_of`:
a JSON object, or a list of them, with the key of a form -- `do`, `ask`, `re`, `info` -- alone or
written among other text) is routed once by its rank (`wake-routed {run, launch, words, line}`), or refused
and said to the member when its form or its sense is wrong (`wake-refused`, an `info`); a `words` without
an act is SAID: nothing written, nothing fails. The steps: 1. REAP -- each `wake-intent` without an end: its launch by
its `wake-launched` event, else by its tag at the house's `messages.jsonl` (read from the cursor
`tick.cursor`: a late `wake-launched`), else none: `wake-failed launch-missing`, never final and costing
no retry -- nothing was launched; launched, its wake lock is judged FIRST: held within `timeout:`, the
launch plays and its follower reads it; free, or held past the bound, its flow is read from the rank the
journal reached and the launch ENDED as the flow says: `wake-ended {run, launch, state, cost, flow, tokens}` -- or
`wake-failed harness-error` when the response was kept on an error of the harness and the launch routed no act,
`quota-reached` on the provider's usage limit (the member launched on no task before its `until`, or before
`team resume --task` without one, or a season that gives it another provider) --; `state` what the house said of the run at `--on-end`, `standing` (the run
waits for a production:
relaunched as soon as its lock is free) or `parked` (it waits for a message), `tokens` what the launch's
calls sent the model, added up (`null` when the harness does not measure it) --, or `wake-failed
wake-dead` when no response stands (the harness died: one retry, its messages back in the inbox;
spent: `final`, and the tick ANSWERS in the member's place every message of the launch that owes --
never the opening a principal posted: the team tells that principal with a `notice` about the root),
`wake-timeout` when held past the bound (killed) -- a launch born in ANOTHER process space than the tick's
(`wake-launched.space`: a sandbox's) is never killed by its pid, and, its lock free without an end, ended with that
space: `launch-failed … house: true`, never final, nobody suspected (team 1.14.3); 2. ROUTE -- an act's elements become posts in their
order: `do` to a member that reports to the acting one (on a ceremony task its participants report to
its facilitator), `ask` to any member of the team or to a principal,
the answer `{"re": <id>}` to the author of the message it cites; a `do` off the edges, an `ask` to a name
nobody declared, a `re` citing a message never delivered to the member are
REFUSED (`wake-refused {…, why}`, an `info` to the member): nothing posted, the launch goes on. Each `do`
or `ask` delivered to a member opens ONE debt: the
first answer that cites it settles it, a later one is
posted `info`; the ROOT's answer to the task's opening writes `done` with its text, settles every
debt of the task, `returned` for every post to an agent left undelivered on it, and `schedule-off`
when no task stays open and no ceremony is declared; a post to a principal is delivered at its
writing and never returned; step 3 is gone (team 1.14.0): nothing holds a member, every message for it
launches it, and it answers a task once the answers it wants are in; 4. RING -- each ceremony whose period is due (`every`: the day conforms and the
hour is past, by `PP_NOW` or the local clock; `after`: the followed ceremony's task resolved)
and not yet rung (`ceremony-due` names the period: the journal is the judge) becomes ONE
ceremony task from the team to its facilitator, its OPENING `do` to the facilitator and a `do` per
participant -- each answer reaches the facilitator as a message, and its answer to the opening resolves it;
5. WAKE -- each MEMBER, in the declaration's order, with messages due, no launch of its under way
and the wake lock of its run free, is LAUNCHED ONCE -- on the first task, in the tasks' order, that has a
message for it:
`wake-intent` WRITTEN FIRST, then `agent start … --launches 1 --tag <tag> --on-end "<engine> --instance
<house> team tick <name>"` (`--run <key>`, the member's run for the task's CARRIER, while its slot stands --
a renewal mark an upgrade left included; none yet, an OPENING, named after the carrier by `agent name`; an
OPENING too when the run is renewed, `run-renewed` written before the intent: parked past its context
limit, or opened under another model or provider than the season gives the member now), then
`wake-launched` with the launch's RANK in the run, then its follower spawned; its other tasks wait for its
next launch, each in the run of its carrier. A member whose run STANDS (its last
launch left it waiting for a production) is RELAUNCHED on the task it stands on as soon as its lock is
free, `[nothing new]` at its head: nothing but a stop is delivered to a run that stands and is still continued
-- what is due waits for its park and opens the launch after, a turn of its own; a run whose task has spent its
`launches:` is continued no more and takes its messages. A member
holds ONE run, ONE key and ONE session per CARRIER of its tasks -- a task alone, the recurrence of its
occurrences, the ceremony of its rings --: the run that first answered there, the carrier's later tasks
arriving in it; it plays one launch at a time. The members play in parallel; `parallel:` bounds the team. The HEAD
of a launch -- what the tick writes before pp's output in the prompt -- opens on the inbox of that task
-- each message its head line, `#<id> DO from <member> on <task> -- you owe an answer`, its text
indented under it; under an answer the tick wrote in a member's place (`by: tick`), a line that says the team
wrote it, why, and that the message it answers is closed, then that message whole, with its vector when it
carries one --, or `[nothing new]`, then the messages it still owes from earlier launches;
nothing else -- what the others answered is read on demand, `team responses <name> --since <id>` --:
what an act is and what it owes is said by the team's fragment of the standing orders (`SYSTEM.md`); a NEW
run of a member whose run `-reset` or `team reset` forgot opens on `[history of <task> for <member>]` for the
open tasks of its carrier -- what it was told there and what it answered --, then its inbox. The head never carries
the team's intention -- the body of `TEAM-<name>.md` -- nor the owner's word -- the body of `TEAM.md`: pp serves
both to the team's runs, the team's document naming them in its `serve:` row at the kit's `turn.begin`, each
served again at the next exchange when it changes. An
OPENING carries the season's material (`work:` of SEASON.md -- passed as `--work`, a clone per run, kept with
its run); a resume never does. No wake-up carries a door: the trigger's ENTRY (`entries:` of
TEAM.md -- a ceremony task: its entry; else `do`'s) is a successor the agent's DAG elects at
EVERY exchange, opening or resume -- the team's document at the kit's `turn.begin`, in the team's
directory, decides by `pp-team entry <name>`. Every wake-up gets `--documents teams/<name>`: the
run opens under the team's root of documents. On a STOPPED task an answer is routed
nowhere, a dead wake-up is never retried, and nobody is woken: the stop is delivered at once -- a run STANDING on the task gets it at the head of one more launch.
The bounds count from the last `team-started`: the cost of every wake-up that answered (ended
or failed), and the wake-ups LAUNCHED under `launches` and `budget-launches`. A wake-up gets its SHARE of
the money: under `budget:`, where the adapter of the launch's grammar declares a cost scope (`COST`),
its intent carries an `allowance` -- min((`budget` - the cost kept) / k, `budget` - the cost kept -
the allowances of the wake-ups under way), k the wake-ups that may play together, min(`parallel`, the
members) -- reserved until its end, and `agent start --max-budget-usd` is the member's RUN cap: what
the run spent (its responses' `cost_usd`) plus the allowance; a member due whose rest is all reserved
is `deferred {reserved}`. Elsewhere no cap goes to `agent start`, and nothing is reserved: no per-wake
cap exists, and a `launch.max_budget_usd` an older journal kept is never passed. A wake-up being one
launch, the cap never falls between two launches: the share is the cap the harness plays under, and
what the launch reports is charged whole at its end.

THE NET of a team is its TIMER, at every step of `schedule:` (`off` for none ever, 5 minutes unless
said, kept in seconds at `team-started.schedule`): the tick arms it when a deadline stands, the
step bounding its sleep. The timer dies with the machine; ONE RELAUNCH ENTRY per HOUSE plays
`team tick --all --entry` at the user's next logon -- one tick per team that needs its net -- and so arms the
timers again: the value `pp-team-<12 hex of the house>` of the user's Run key
(`HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`) under Windows, written with no right the
user lacks; a line `@reboot <python> <engine> --instance <house> team tick --all --entry >/dev/null 2>&1
# pp-team <house>` in the user's crontab elsewhere, and under WSL (`WSL_DISTRO_NAME` set) the same value of the
Run key too, `wsl.exe -d <distro> --exec <python> <engine> --instance <house> team tick --all --entry`, written by
`reg.exe`:
Windows starts the distribution at logon -- or, under `PP_CRONTAB=<file>` and
`PP_RUNKEY=<file>`, those files (the bench, a try); `PP_SCHEDULER=nt|posix` names the façade. A
verb whose team needs its net -- a task open or a ceremony declared -- lays it after writing its
journal (`start`, a `post` that finds it gone); the tick at `schedule-off`, `stop` and `delete`
remove it only when NO team of the house needs it any more, judged and removed under
`state/relaunch.lock`. The system plays the entry with its own minimal PATH, where a harness's command is not found:
every lay keeps the PATH of the process that lays it at `state/relaunch.path`, written whole even when the entry
stands unchanged, and removed with the entry; `--entry` takes it up before any team advances, so the timers and the
launches inherit it -- an entry laid by an earlier version, without `--entry`, differs and is rewritten at the next
lay. An entry the system refuses is SAID -- stderr (`relaunch not laid`), a notice
of the team to the owner once per season, the face -- and the team starts: it runs on its timer.

The house is the instance this script belongs to. The journal `.sys/records/teams/<name>/journal.jsonl` is APPEND-ONLY and this script
is its only writer: `{at, id, kind, team, ...}`, the id the previous one + 1, read and written
under the record's lock. A reader skips a last line still being written; a line that does
not parse anywhere else refuses by its name. Any other call says the usage in one line, exit 2.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import queue
import re
import secrets
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

TEAMS = "teams"                  # under the house's root: one directory per team, its TEAM.md
TEAM_DOC = "TEAM.md"
JOURNAL = "journal.jsonl"        # under the house's records: teams/<name>/journal.jsonl
TICK_LOCK = "tick.lock"          # beside the journal: one tick at a time
TICK_MARK = "tick.pending"       # beside the journal: a tick asked while another played
MESSAGES = "messages.jsonl"      # the house's record pp-agent writes at every launch: read here for a late launch
TICK_CURSOR = "tick.cursor"      # beside the journal: how far the tick read messages.jsonl, the tags it keeps
TICK_TIMER = "tick.timer"        # beside the journal: the TIMER armed under the minute, {pid, due}, one at most
TIMER_WAIT = 2.0                 # seconds a timer waits for its mark to carry its token, before it leaves
TIMER_RETRY = 2.0                # seconds a timer waits before it plays its tick again under a maintenance
TIMER_RETRIES = 300              # the ticks a timer plays again under a maintenance at most: ten minutes
FOLLOW_LOG = "follow.log"        # beside the journal: what the followers of the launches said
CREATE_NEW_PROCESS_GROUP = 0x00000200   # Windows' process creation flags and answers, read on any system
CREATE_NO_WINDOW = 0x08000000
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
ERROR_ACCESS_DENIED = 5
BORDER = "---"
MODES = ("every", "after")       # a ceremony's rhythm: at a period, or after another ceremony
DOWS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")   # the days `every <dow> HH:MM` may name
NOW = "PP_NOW"                   # names the tick's wall clock (ISO, naive local): the bench, a try
CLOSED = ("stopped", "resolved")
ELEMENTS = {"do": {"do"}, "ask": {"ask"}, "re": {"re", "text"}, "info": {"info"}}   # an act's forms and their keys
RETIRED_VERBS = ("done", "reply", "escalate", "note")   # the verbs of before -- an answer's until team 0.33.0, the
#                                                  principal's note until 0.47.0 --: read in a journal alone
OWED = "you owe an answer"                       # what the head says of a message whose debt stands
IDENTITY = "[team {team} · you are {member}]"    # the first line of a WAKE-UP's head: who is launched
RELANCED = ("[nothing new arrived for you, and you still owe an answer: send it now, or send an `info` that says "
            "where you stand]")                  # the line a relance's head says why on, for a debt alone
CYCLED = ("[you and {member} each wait for the other's answer: send yours first, or send an `info` that says "
          "where you stand]")                    # the same, for a member in a cycle of waits
BEAT = ("[you owe an answer on {task}. Exchanges left to send the team a message about it, this one included: "
        "{left}. A message is your answer, a question or an `info`. Once they are spent without a message from "
        "you, the team stops waiting for you and answers in your place]")   # the BEAT a wake-up's head says to a
#                                                  member that owes (row 115)
NOTHING_NEW = "[nothing new]"                    # the head of a relaunch of a standing run nothing arrived for
DEFAULT_SILENCE = 3                              # silent passages in a row that make a member suspected, unless TEAM.md says
MEMBER_TYPE = "member"                           # the profile `agent add` gives a member born by a start
DEFAULT_RETRIES = 1                              # wake-ups played again after a dead one, unless TEAM.md says
HALT_AFTER = 3                                   # the same failure in a row of a member on a task: launched there no more
HARNESS_SPARED = ("quota", "budget-spent", "interrupted")   # the errors of a kept response that are no harness error
LIMITS = ("parallel", "budget", "retries", "timeout", "launches", "budget-launches", "suspect-max", "silence")   # the keys of TEAM.md that bound the tick
RETIRED_LIMITS = {"wakes": "launches", "budget-wakes": "budget-launches"}   # the keys of before: refused by name where written,
#                                                                            read where a journal already wrote them
RETIRED_FLAGS = {"--wakes": "--launches", "--budget-wakes": "--budget-launches"}
STOPPED_HEAD = "[the task is stopped: say no act, let your run park]"   # the head of the last launch of a run standing on a stopped task
CLOSED_HEAD = "[the task is closed: no act is awaited]"   # the head of a continuation of a run standing on a resolved task
ANSWERED_FOR = {                                 # what the head says of a `re` the tick wrote in a member's place, by its cause:
    "returned": "[the team wrote this answer in {member}'s place: {member} never received your message #{id} and will "
                "not receive it. The message is closed: if you still need it, send it again in a new message, to "
                "another member now or to {member} once it answers again]",
    "suspected": "[the team wrote this answer in {member}'s place: {member} was given your message #{id} and did not "
                 "answer it. The message is closed: if you still need it, send it again in a new message, to "
                 "another member now or to {member} once it answers again]",
    "failed": "[the team wrote this answer in {member}'s place: the launch of {member} that carried your message "
              "#{id} failed, and the next line says why. The message is closed: if you still need it, send it again "
              "in a new message]"}
#                                                  a message no intent carried, a message an intent carried, a launch that failed
HANDED_BACK = "[your message #{id}, as you wrote it:]"   # the head line of the message such a `re` cites, its text under it
HANDED_BACK_VECTOR = "[your message #{id}, as you wrote it, with its vector {vector}:]"   # the same, for a message that carries a vector
RETURNED_MARK = " · returns a message never delivered"   # what the text of `log` says of a post that returns a message
DEFAULT_SCHEDULE = 300                           # seconds between two ticks of the net, unless TEAM.md says
DEFAULT_SUSPECT_MAX = 600                        # seconds: the longest interval a suspected member waits, unless TEAM.md says
MINUTE = 60                                      # the seconds of `m` and of a bare number of minutes in a duration
HOUR = 60 * MINUTE                               # the seconds of `h`
CRONTAB = "PP_CRONTAB"                           # names a file that stands for the user's crontab: the bench, a try
SCHEDULER = "PP_SCHEDULER"                       # names the scheduler's façade, `nt` or `posix`: the bench plays both
RUNKEY = "PP_RUNKEY"                             # names a file that stands for the user's Run key: one value per line
TIMER_ENV = "PP_TEAM_TIMER"                      # marks the tick a timer plays: read then taken out by `tick`
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"   # under HKEY_CURRENT_USER: played at the user's logon
WSL_DISTRO = "WSL_DISTRO_NAME"                   # set by WSL in its distribution: the posix façade lays the Run key too
RELAUNCH_PREFIX = "pp-team"                      # the head of the house's value in the Run key
RELAUNCH_LOCK = "relaunch.lock"                  # under the house's state: the relaunch entry laid, judged, removed
RELAUNCH_PATH = "relaunch.path"                  # under the house's state: the PATH of the process that laid the entry
USAGE = ("usage: pp-team start <name> [--message <text> [--to <member>] [--name <text>]] [--budget <usd>] "
         "[--budget-launches <n>] [--context <n>%] [--provider <name>] [--harness <command>] "
         "[--model <m>] [--permissions auto|strict|bypass] "
         "[--effort low|medium|high|xhigh|max] [--no-tick] [--package <name>=on|off]... "
         "[--member <member> [--provider <name>] [--model <m>] [--effort <e>] [--permissions <p>] "
         "[--package <name>=on|off]...]... | "
         "post <name> [--message <text>] [--to <member>] [--task <id> [--ask] | [--name <text>] [--context <n>%]] [--reply <id>] [--stop] "
         "[--as <principal>] [--every \"day|weekday|mon..sun HH:MM\" [--context <n>%] [--description <text>]] "
         "[--no-tick] | stop <name> [--task <id>] [--kill] [--json] [--no-tick] | "
         "stop <name> --recurrence <R<n>> [--no-tick] | "
         "recurrence <name> <R<n>> [--every \"day|weekday|mon..sun HH:MM\"] [--context <n>%|off] [--message <text>] "
         "[--description <text>] [--as <principal>] [--no-tick] | "
         "recurrence <name> <R<n>> --now [--as <principal>] [--no-tick] | "
         "recurrence <name> --task <T<n>> --every \"day|weekday|mon..sun HH:MM\" [--context <n>%] "
         "[--description <text>] [--as <principal>] "
         "[--no-tick] | "
         "tick <name> | tick --all [--entry] | follow <name> <tag> | "
         "timer <name> --sleep <seconds> --due <local date-time> --token <token> | "
         "status [<name>] [--json] | "
         "watch <name> [--task <id>] [--json] [--heartbeat <seconds>] [--for <seconds>] [--until-done] | "
         "log <name> [--task <id>] [--last <n>] [--json] | result <name> [<task>] | "
         "responses <name> [--since <id>] [--agent <member>] [--task <t>] [--last <n>] [--json] | "
         "stats <name> [--season <n> | --all] [--cost usd|launches|tokens] [--json] | "
         "inbox [<name>] [--seen [--id <n>] | --json] | roster [--json] | "
         "snapshot <name> | entry <name> --run <key> | reset <name> [--member <member>] | "
         "pause <name> [--as <principal>] | resume <name> [--as <principal>] [--no-tick] | "
         "pause <name> --recurrence <R<n>> [--as <principal>] | "
         "resume <name> --recurrence <R<n>> [--as <principal>] [--no-tick] | "
         "resume <name> --task <id> [--to <member>|all] [--message <text>] [--as <principal>] [--no-tick] | "
         "resume <name> --quota [--member <member>] [--as <principal>] [--no-tick] | "
         "budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick] | "
         "ring <name> <ceremony> [--as <principal>] [--no-tick] | templates [--json] | "
         "templates --render <directory>/<name> [--value <name>=<value>]... "
         "[--team <name> [[--season] --text-file <path>|-]] [--json] | "
         "document <directory>/<name> [--new | --body-file <path>|- | --delete] [--json] | "
         "declare <name> [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]... "
         "[--document \"<key>|all <document> ...\"]... [--no-document <key>]... [--body-file <path>|-] "
         "[--member <name> <path>]... [--no-member <name>]... [--role <key> [<member> ...]]... [--no-role <key>]... "
         "[--report \"<member>... -> <member>\"]... [--no-report <member>]... "
         "[--root <member>] [--principal <p>]... [--budget <usd>] [--launches <n>] [--parallel <n>] [--timeout <s>] "
         "[--schedule <n>s|<n>m|<n>h|<minutes>|off] [--description <text>] [--json] | "
         "declare <name> --season [--template <directory>/<name>] [--value <name>=<value>]... [--no-value <name>]... "
         "[--document \"<key>|all <document> ...\"]... [--no-document <key>]... [--body-file <path>|-] "
         "[--budget <usd>] [--budget-launches <n>] [--silence <n>] [--context <n>%] [--provider <name>] [--model <m>] "
         "[--effort low|medium|high|xhigh|max] [--permissions auto|strict|bypass] [--harness <command>] "
         "[--package <name>=on|off]... [--json] [--member <member> [--provider <name>] [--model <m>] [--effort <e>] "
         "[--permissions <p>] [--silence <n>] [--package <name>=on|off]...]... | "
         "declaration <name> [--json] [[--season] --text-file <path>|-] | "
         "delete <name> [--agent <path>]... [--yes] [--json] | rename <name> <new> [--json]")
LAUNCH_FLAGS = {"provider": True, "harness": True, "model": True, "permissions": True, "effort": True}
START_FLAGS = {"message": True, "to": True, "name": True, "no-tick": False, "budget": True, "budget-launches": True,
               "silence": True, "context": True, **LAUNCH_FLAGS}
PROFILE_KEYS = ("provider", "model", "effort", "permissions")   # what a member's profile may replace
POST_FLAGS = {"message": True, "to": True, "task": True, "reply": True, "stop": False, "as": True, "name": True,
              "every": True, "context": True, "description": True, "no-tick": False, "vector": True, "ask": False}
MANY = ("vector", "value")                         # the flags of `flags` a verb takes several times: a list
VECTOR_REFUSED = "vector-refused"                  # the launcher's one code for a vector it refuses, at the head of
#                                                  its refusal (`<launcher>: vector-refused -- <the cause>`), rc 2
REFUSAL_CODE = re.compile(r"^[\w.-]+: ([a-z0-9]+(?:-[a-z0-9]+)*)(?: --|$)", re.M)   # a refusal's head: its code
STOP_FLAGS = {"task": True, "kill": False, "recurrence": True, "json": False, "no-tick": False}
RECURRENCE_FLAGS = {"every": True, "context": True, "message": True, "task": True, "description": True, "as": True,
                    "now": False, "no-tick": False}
WATCH_FLAGS = {"task": True, "json": False, "heartbeat": True, "for": True, "until-done": False}
LOG_FLAGS = {"task": True, "last": True, "json": False}
INBOX_FLAGS = {"seen": False, "json": False, "id": True}
ROSTER_FLAGS = {"json": False}
DELETE_FLAGS = {"yes": False, "json": False}     # `--agent <path>`, repeatable, is taken out before (`agents_asked`)
RENAME_FLAGS = {"json": False}
RESPONSES_FLAGS = {"since": True, "agent": True, "task": True, "last": True, "json": False}
ENTRY_FLAGS = {"run": True}
RESET_FLAGS = {"member": True}
RESUME_FLAGS = {"task": True, "message": True, "recurrence": True, "as": True, "no-tick": False, "quota": False,
                "member": True, "to": True}
PAUSE_FLAGS = {"recurrence": True, "as": True}
RING_FLAGS = {"as": True, "no-tick": False}
BUDGET_FLAGS = {"launches": True, "as": True, "no-tick": False}
STATUS_FLAGS = {"json": False}
TEMPLATES_FLAGS = {"json": False, "render": True, "value": True, "team": True,   # `templates`, and its dry render
                   "season": False, "text-file": True}
DOCUMENT_FLAGS = {"new": False, "body-file": True, "delete": False, "json": False}   # `document`: one action at most
DECLARATION_FLAGS = {"json": False, "season": False, "text-file": True}   # `declaration`: a candidate text read
RESUMED = "the task resumes"                     # the note of a resume that names no message
NO_DESCRIPTION = "no description"                # the sheet's word for a member without a description of its own
IDLE = "TEAM-IDLE.md"                            # the neutral successor: a wake-up whose trigger names no entry
SPEC = "TEAM_WORK.md"                            # how a team works: the package's `refs/`, served after the intention
IDLE_SOURCE = "agent-idle.md"                    # beside this script -> the team's directory: the same bytes for every team
DECIDER = "pp-team entry"                        # what a team document's `decide:` plays: this skill's verb
ACT_FORMAT = "team-act"                          # the OUTPUT format an act is a production of (procs/TEAM-ACT.md declares it)
RETIRED = {("procs", "TURN.md"): "retired/agent-turn-0.32.txt",   # what an earlier version laid at an agent -> the
           ("procs", IDLE): "agent-idle.md",       # bytes it laid, beside this script or under `retired/`
           ("skills", "team-entry", "SKILL.md"): "retired/agent-entry.md",
           ("skills", "team-entry", "team-entry.py"): "retired/agent-entry.py"}
TURN_DOC = "TURN.md"                             # the kit's turn: the name its overlay takes in the team's directory
RETIRED_IN_TEAM = {TURN_DOC: ("retired/agent-turn-0.32.txt", "retired/agent-turn-0.39.txt")}   # the team's own law of
                                                 # an earlier version, in the team's directory: replaced at the start
ELEMENTS_LIST = ("do", "ask", "re", "info")      # the forms, in the order the contract says them
DEFAULT_HEARTBEAT = 60                           # seconds without a step before watch says so
ACTIVITY_RATE = 4                                # activity objects `watch` says per second and per launch: a reader
                                                 # takes in four lines a second; the surplus is folded into the last
                                                 # one said (`more`), a `context` always passes
ACTIVITY_TEXT = 80                               # characters of a text an activity object carries: a tool's title,
                                                 # a thought, the words -- never the content of a result
ACTIVITY_KINDS = ("tool", "tool-result", "thinking", "words", "context")   # what a flow says of a launch's activity
ACTIVITY_DRAIN = 1.0                             # seconds a reader of a flow keeps draining after its wake-up ended
DEAD = ("delegation", "terminal", "wait", "wait-met")   # the events no version writes any more, which no face says:
                                                 # the first two (before team 0.33.0) the replay reads, the last two
                                                 # (before team 1.14.0) it skips -- nothing holds a member
HISTORY_CHARS = 200                              # a message's text in a reopened run's history
NAME_CHARS = 80                                  # a task's name: one line a user types, read in a table
DESCRIPTION_CHARS = 200                          # a team's or a recurrence's description: one sentence read in a table
RUN_NAME_CHARS = 60                              # a run's name, as `agent name` bounds it
TEMPLATES = Path(__file__).resolve().parents[2] / "templates"   # the package's templates, `<directory>/<name>.md`
TEMPLATES_PLACE = Path(TEAMS) / "templates"      # under the house's instance: the house's templates, read first
DOCUMENT_SKELETON = ("---\ndescription: what this document tells the members, in one sentence\n---\n# {name}\n\n"
                     "Write here what the members must know or do.\n")
#                                                 what `team document --new` writes: a document, no preset key
TEMPLATE_KEYS = ("description", "requires", "values")   # a document's own keys: never rendered
PRESET_KEYS = ("documents", "form", "members")   # the keys that make a template a PRESET, never a document
TEAM_KEYS = ("form", "members", "reports")      # the keys that make a preset a TEAM's: TEAM.md names it, SEASON.md never
ALL = "all"                                      # the key of a `documents:` line every member receives
SHEET = "members"                                # the name of the members' sheet: no document takes it
SEASON_DOC = "SEASON.md"                         # in the team's directory: the season's values, the owner's file
SEASON_LIMITS = ("budget", "budget-launches", "silence", "context")   # the season's own limits, over TEAM.md's
PROFILE_LINE = ("provider", "model", "effort", "permissions", "silence")   # a profile line's keys, beside
#                                                 `package.<name>`
SEASON_KEYS = ("template", "values", "documents", *LAUNCH_FLAGS, *SEASON_LIMITS, "packages", "profiles", "work")
SEASON_LAUNCH = (*SEASON_LIMITS, *LAUNCH_FLAGS)   # the season's flags of `start` that `declare --season` takes too
#                                                 what SEASON.md may say in its front matter
BUILT_IN = "team"                                # the one value no template declares: the team's name
ROLES_DIR = "roles"                              # under the team's directory: the documents of a role, which the
                                                 # engine's flat reading of the root never sees -- mounted by a vector
MEMBER_FAMILY = "team-member"                    # the vector family this package declares: `team-member:<team>/<member>`
MOUNT_MOMENT = "turn.begin"                      # the one moment a document of a role may declare: its vector mounts
                                                 # it before the message of every exchange
EMPTIED = "-"                                    # `--vector -`: the launcher's word for a run that keeps no vector
HOLE = re.compile(r"\{\{|\}\}|\{([a-z0-9]+(?:-[a-z0-9]+)*)\}")   # a hole `{<name>}`, or a brace written twice
TEAM_LAW = "TM"                                  # the prefix of a team's laws: every code a mounted document declares
FORM_NAMES = ("star", "chain", "one", "tree")    # the forms `formed` plays, a team template's `form:`
SQUADS = 2                                       # the squad leads of a `tree` its template does not count
PLACES = {None: ("root", "others", "last"), "star": ("root", "others", "last"),   # the places each form has, what
          "chain": ("root", "others", "last"), "one": ("root", "last"),             # a preset's `roles:` line names
          "tree": ("root", "others", "squads", "workers", "last")}
DECLARE_FLAGS = {"season": 0, "json": 0, "template": 1, "value": 1, "no-value": 1, "document": 1, "no-document": 1,
                 "body-file": 1, "member": 2, "no-member": 1, "role": None, "no-role": 1, "root": 1, "principal": 1,
                 "budget": 1, "launches": 1, "parallel": 1, "timeout": 1, "schedule": 1, "description": 1, "report": 1,
                 "no-report": 1}                 # the flags of `declare`:
#                                                 the words each takes -- None: a key, then its members up to the next flag
DECLARE_MANY = ("value", "no-value", "document", "no-document", "member", "no-member", "role", "no-role", "principal",
                "report", "no-report")
#                                                 the flags `declare` takes several times
DECLARE_TEAM = ("member", "no-member", "role", "no-role", "root", "principal", "budget", "launches", "parallel",
                "timeout", "schedule", "description", "report", "no-report")       # the flags of TEAM.md alone: the usage under `--season`
DECLARE_PAIRS = (("value", "no-value"), ("document", "no-document"), ("member", "no-member"), ("role", "no-role"),
                 ("report", "no-report"))
#                                                 a flag and its contrary: one line of a block written, taken out


def refuse(said: str) -> None:
    sys.stderr.write(f"pp-team: {said}\n")
    raise SystemExit(2)


class Declined(Exception):
    """A declaration the judge does not accept: its text is the refusal `start` writes."""


def decline(said: str) -> None:
    raise Declined(said)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- the house -----------------------------------------------------------------------------

def house():
    """-> (the house's instance root, the conductor module) -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core, home                          # noqa: E402 -- the bootstrap
    root = home(__file__)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(__file__)


def machine_house() -> tuple[Path, object]:
    """-> (the HOUSE's instance root, the conductor module): the machine this script lives in (`_machine()`),
    whatever instance calls it -- an agent that borrows the machine reads its house's teams, never its own
    instance alone. The one resolution the verbs that address the house from an agent share."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import _machine, core                      # noqa: E402 -- the bootstrap
    root = _machine(__file__)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(__file__)


def caller() -> Path | None:
    """-> the instance the call serves (`home()`: the one `PP_HOME` names when it borrows the machine)."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import home                                # noqa: E402 -- the bootstrap
    found = home(__file__)
    return found.resolve() if found is not None else None


def locks(conductor):
    """-> the engine's `state.lock` module: the tick lock, and the launchers' files it tests."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.lock")


def tracing(conductor):
    """-> the engine's `state.log` module: the one reader of a trace (`tail`, `follow`,
    `step_of`, `said`), shared with `pp-agent`."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.log")


def house_console(root: Path, conductor) -> Path:
    """-> the house's console by its absolute path (`pp`, `pp.cmd` on Windows): what an agent
    calls to read what the head of its message names."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.packaging.adapters").console_of(root.parent)


def owner_of(root: Path, conductor) -> str:
    """-> the team's OWNER: the house's slug."""
    return str(conductor.instance.slug(root))


def team_doc(root: Path, name: str) -> Path:
    return root.parent / TEAMS / name / TEAM_DOC


def team_root(root: Path, name: str) -> Path:
    """-> the team's directory: its TEAM.md, its entries, its documents -- the root of documents of
    every run the team opens."""
    return root.parent / TEAMS / name


def journal_of(root: Path, name: str) -> Path:
    return root / ".sys" / "records" / TEAMS / name / JOURNAL


def record_of(root: Path, name: str) -> Path:
    """-> one of the house's records -- written by pp-agent, read here."""
    return root / ".sys" / "records" / name


def agent_meta(root: Path, path: str) -> Path:
    """-> where the agent `path` stands: an agent IS its path under the house, slugs joined by
    `/` (`m`, `squad/r9`), its instance directory named as the house's own. The path is judged
    at the declaration (`path_valid`)."""
    return root.parent.joinpath(*path.split("/")) / root.name


def path_valid(conductor, path: str) -> bool:
    """-> whether `path` is an agent's path: slugs joined by `/`, no `..`, no leading `/`, no
    empty segment."""
    return bool(path) and all(conductor.instance.valid_slug(one) for one in path.split("/"))


def path_of(state: dict, member: str) -> str:
    """-> the path of the agent that plays `member`, read at `team-started.agents`: the team
    speaks names, the house addresses its agents by their paths."""
    return str(((state["started"] or {}).get("agents") or {}).get(member, member))


def path_of_intent(state: dict, intent: dict) -> str:
    """-> the path of the agent a wake-up woke: the `path` its intent carries, else its
    member's path."""
    return str(intent.get("path") or path_of(state, intent["agent"]))


def launch_of(conductor, meta: Path, run: str) -> Path:
    """-> the launcher's file of an agent's run, `session-<run>.wake.lock` beside its slot --
    the `agent` package's published contract: held while a wake-up plays."""
    return conductor.persistence.slot_of(meta, run).with_name(f"session-{run}.wake.lock")


def space_now() -> str | None:
    """-> the process SPACE this process plays in, as the kernel names it (`pid:[4026531836]`: its pid namespace,
    Linux); None where the system names none. A pid means something inside its space alone: a launcher detached
    from a sandbox is born in the sandbox's space, where the tick that launched it plays too, and ends with it."""
    try:
        return os.readlink("/proc/self/ns/pid")
    except OSError:
        return None


def foreign(launch: dict) -> bool:
    """-> whether the launch was born in ANOTHER process space than the one that reads it: its `wake-launched`
    kept a `space`, this process names its own, and they differ. Its pid then names nobody here -- never killed
    by it --, and its death with a free wake lock is its space's end, the house's failure, never the member's."""
    born, here = launch.get("space"), space_now()
    return bool(born) and bool(here) and born != here


def engine_of(root: Path, conductor) -> Path:
    """-> the engine the house's console runs: the one a tick names in `--on-end`."""
    return conductor.instance.engine_root(root) / "pp.py"


def retired_flags(rest: list[str]) -> None:
    """A flag of before (`--wakes`, `--budget-wakes`: the bounds counted wake-ups) refuses `flag-retired`
    naming the flag that took its place; nothing is parsed after it."""
    for flag in rest:
        if flag in RETIRED_FLAGS:
            refuse(f"flag-retired -- `{flag}`: the bounds count launches -- say `{RETIRED_FLAGS[flag]}`.")


def flags(rest: list[str], table: dict[str, bool]) -> dict:
    """-> the verb's flags from its table (True: takes a value), a flag of `MANY` as the list of its values;
    anything else is the usage."""
    found: dict = {name: ([] if name in MANY else None if takes else False) for name, takes in table.items()}
    index = 0
    while index < len(rest):
        word = rest[index]
        name = word[2:] if word.startswith("--") else ""
        if name not in table:
            refuse(USAGE)
        if table[name]:
            if index + 1 >= len(rest):
                refuse(USAGE)
            if name in MANY:
                found[name].append(rest[index + 1])
            else:
                found[name] = rest[index + 1]
            index += 2
        else:
            found[name] = True
            index += 1
    return found


def vector_formed(value) -> bool:
    """-> whether a VECTOR is formed: a text `<family>:<id>`, both sides said, no blank in it. What it names, the
    team never reads: the vector is an opaque string the launcher alone resolves."""
    if not isinstance(value, str) or any(one.isspace() for one in value):
        return False
    family, colon, ident = value.partition(":")
    return bool(family and colon and ident)


def named_team(conductor, rest: list[str]) -> tuple[str, list[str]]:
    """-> (the team's name, the rest): the first word names the team, a slug."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    name = rest[0]
    if not conductor.instance.valid_slug(name):
        refuse(f"team-invalid -- `{name}`: a team's name is lowercase, digits and single dashes.")
    return name, rest[1:]


# --- the declaration: TEAM.md read whole ---------------------------------------------------

def block(front: dict, key: str) -> list[str]:
    """-> the non-empty lines of a `key: |` block, stripped; nothing for an absent key."""
    return [line.strip() for line in str(front.get(key, "")).splitlines() if line.strip()]


def team_name(root: Path, conductor, name: str) -> str:
    """-> the name a team is SHOWN by: the `name:` of its `TEAM.md`, read at every call -- the directory's name, the
    team's identity, when the key is absent or the file cannot be read. Nothing keyed by it: a rename moves no
    journal, no relaunch entry, no file."""
    try:
        said = front_read(conductor, team_doc(root, name)).get("name")
    except (Declined, OSError):
        return name
    shown = "" if said is None else str(said).strip()
    return shown if shown and len(shown) <= NAME_CHARS and shown.isprintable() else name


def described_well(said) -> bool:
    """-> whether a description is one line of 1 to `DESCRIPTION_CHARS` printable characters, its edges stripped."""
    return bool(said) and len(said) <= DESCRIPTION_CHARS and said.isprintable()


def team_description(root: Path, conductor, name: str) -> str | None:
    """-> what a team DOES, as its `TEAM.md` says it under `description:`, read at every call and never written to the
    journal: a description rewritten is read at the next call, without a start. None when the key is absent, the file
    cannot be read or the description is not one judged line (`judged` refuses it at the start)."""
    try:
        said = front_read(conductor, team_doc(root, name)).get("description")
    except (Declined, OSError):
        return None
    shown = "" if said is None else str(said).strip()
    return shown if described_well(shown) else None


def labelled(root: Path, conductor, name: str) -> str:
    """-> how a text says a team: its name, the directory's name after it when they differ."""
    shown = team_name(root, conductor, name)
    return name if shown == name else f"{shown} ({name})"


def body_of(text: str) -> str:
    """-> the text after the front matter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != BORDER:
        return ""
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    return "\n".join(lines[end + 1:]).strip() if end is not None else ""


def when_of(words: list[str]) -> dict | None:
    """-> the period an `every` names, `{kind, at}` -- `day`, `weekday` or a day of the week, then the local hour
    `HH:MM` --, or None when the words say anything else: the ONE reader of a period, a ceremony's and a
    recurrence's."""
    at = words[1] if len(words) == 2 else ""
    timed = (len(at) == 5 and at[2] == ":" and at[:2].isdigit() and at[3:].isdigit()
             and int(at[:2]) < 24 and int(at[3:]) < 60)
    if len(words) != 2 or words[0] not in ("day", "weekday", *DOWS) or not timed:
        return None
    return {"kind": words[0], "at": at}


UNITS = {"m": MINUTE, "h": HOUR, "d": 24 * HOUR}  # the units of a recurrence's duration


def every_of(text: str) -> dict:
    """-> the period a recurrence's `--every` names: a dated one, `{kind, at}` as `when_of` reads it, or a DURATION
    `<n>m|<n>h|<n>d` -- n a whole number from 1, a minute at least --, `{kind: "interval", every, seconds}`;
    `every-invalid` naming both forms otherwise. A ceremony reads `when_of` alone: it has no duration."""
    words = text.split()
    found = when_of(words)
    duration = re.fullmatch(r"([1-9][0-9]*)([mhd])", words[0]) if len(words) == 1 else None
    if found is None and duration is not None:
        found = {"kind": "interval", "every": words[0], "seconds": int(duration.group(1)) * UNITS[duration.group(2)]}
    if found is None:
        refuse(f"every-invalid -- `--every {' '.join(words)[:40]}`: a recurrence comes back "
               "`day|weekday|mon..sun HH:MM`, the local hour, or every `<n>m|<n>h|<n>d`.")
    return found


def said_when(when: dict) -> str:
    """-> a recurrence's period as the faces say it after `every`: `weekday 09:30`, or `4h`."""
    return str(when.get("every")) if when.get("kind") == "interval" else f"{when.get('kind')} {when.get('at')}"


def ceremony_of(line: str, agents: dict, path: Path) -> dict:
    """-> one ceremony as its line declares it: `<name> every … [with a b -> c [any <n>]]` or
    `<name> after <other> … [with a b -> c [any <n>]]` -- the name, the mode, what it follows, its
    participants, its facilitator and its quorum (n of the participants whose answers are enough for the
    facilitator to conclude, said in its consigne and holding nothing, `None` for all); the rest of the words kept as the text the rhythm will read."""
    words = line.split()
    if len(words) < 2 or words[1] not in MODES:
        decline(f"team-invalid -- {path}: ceremonies: `{line}` -- a line is `<name> every …` or `<name> after <other> …`.")
    name, mode = words[0], words[1]
    spec = words[2:words.index("with")] if "with" in words else words[2:]
    after, when = None, None
    if mode == "after":
        if len(spec) != 1 or spec[0] == "with":
            decline(f"team-invalid -- {path}: ceremonies: `{line}` -- `after` names the ceremony it follows, "
                   "and nothing else.")
        after = spec[0]
    else:
        when = when_of(spec)
        if when is None:
            decline(f"team-invalid -- {path}: ceremonies: `{line}` -- the when is "
                   "`every day|weekday|mon..sun HH:MM`.")
    participants: list[str] = []
    facilitator, quorum = None, None
    if "with" in words:
        tail = words[words.index("with") + 1:]
        if "->" in tail:
            at = tail.index("->")
            participants, targets = tail[:at], tail[at + 1:]
            if len(targets) == 3 and targets[1] == "any":       # the quorum: `-> c any <n>`
                n = targets[2]
                if not n.isdigit() or not 1 <= int(n) <= len(participants):
                    decline(f"team-invalid -- {path}: ceremonies: `{line}` -- the quorum is `any <n>`, n from 1 to "
                           f"the {len(participants)} participant(s).")
                quorum, targets = int(n), targets[:1]
            if len(targets) != 1:
                decline(f"team-invalid -- {path}: ceremonies: `{line}` -- one facilitator after `->`, "
                       "then `any <n>` at most.")
            facilitator = targets[0]
        else:
            participants = tail
        for one in participants + ([facilitator] if facilitator else []):
            if one not in agents:
                decline(f"participant-unknown -- {path}: ceremony `{name}` names `{one}`, a member nobody declared.")
    if facilitator is None or not participants:
        decline(f"team-invalid -- {path}: ceremonies: `{line}` -- a ceremony owes its participants and its "
               "facilitator: `with a b -> c`.")
    return {"name": name, "mode": mode, "after": after, "when": when, "participants": participants,
            "facilitator": facilitator, "quorum": quorum, "text": line}


def acyclic(ceremonies: list[dict], path: Path) -> None:
    """The `after` graph must be a DAG: a loop would ring for ever -- `ceremony-cycle`."""
    follows = {one["name"]: one["after"] for one in ceremonies}
    for start in follows:
        seen, step = [start], follows[start]
        while step is not None:
            if step in seen:
                decline(f"ceremony-cycle -- {path}: `{' -> '.join(seen + [step])}` -- `after` loops; the chain "
                       "of ceremonies must end.")
            seen.append(step)
            step = follows.get(step)


def declared(root: Path, conductor, name: str) -> dict:
    """-> the team as it plays (`team_played`), read WHOLE and judged before anything is written: a defect refuses."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    try:
        return team_played(root, conductor, name)
    except Declined as declining:
        refuse(str(declining))


def front_read(conductor, path: Path, text: str | None = None) -> dict:
    """-> the front matter of a `TEAM.md`, its ONE reading: the file standing at `path`, or `text`, what `declare` is
    about to write there. DECLINES `team-invalid` for a front matter the engine cannot read; a file that is not there
    raises OSError."""
    try:
        if text is None:
            return conductor.reading.read(path).front
        lines = text.splitlines()
        start, end = conductor.sections.front_span(lines)
        return conductor.reading.front_matter(lines[start:end])
    except conductor.Refusal as refusal:
        decline(f"team-invalid -- {path}: {refusal}")


def team_played(root: Path, conductor, name: str, text: str | None = None) -> dict:
    """-> the team as it PLAYS: what `teams/<name>/TEAM.md` and the preset it names make together, judged whole
    (`judged`) -- the ONE reader of a declaration: `start`, `declaration`, `declare` (the `text` it is about to write)
    and every face that says a team's members or its root. `template:`, `documents:` and `values:` are read by
    `documents_of`, the reader `SEASON.md` shares; the team's values are judged on what its preset and its documents
    declare (`values_applied`). The preset's form makes the edges, the root and the daily `TEAM.md` does not write, its
    limits and `schedule:` are the defaults of `TEAM.md`'s own keys (`shaped`), its intention is rendered for the team
    (`intention_rendered`). Without `template:` nothing is chosen in silence: the team is what `TEAM.md` writes, its
    intention empty. DECLINES by name: `team-invalid` (a front matter the engine cannot read, a `values:` or
    `documents:` line of another form, a form given members it cannot hold), `template-unknown`, `template-invalid`,
    `document-unknown`, `value-unknown`, `value-missing`, `value-undeclared` (a hole of the intention nothing
    declares), and the judge's own."""
    path = team_doc(root, name)
    front = front_read(conductor, path, text)
    data = path.read_bytes() if text is None else text.encode("utf-8")
    read = documents_of(root, conductor, team_root(root, name), front, path, "team-invalid")
    applied = values_applied(read["declared"], read["given"], path, "what TEAM.md names", "team")
    return judged(conductor, front, data, path, name, {"template": read["template"], "applied": applied, "read": read})


def preset_roles(template: dict, team: dict) -> list[str]:
    """-> the lines of `roles:` a team preset gives a team at its birth: each of its keys with the members the form
    puts in the places its line names (`team`, `formed`'s, its `places`), each once, in the order the places say --
    a key whose places hold nobody stays, reserved."""
    lines = []
    for line in template["roles"]:
        key, *places = line.split()
        held = [one for place in places for one in team["places"][place.strip("{}")]]
        lines.append(" ".join([key, *dict.fromkeys(held)]))
    return lines


def shaped(front: dict, template: dict, values: dict[str, str], members: list[str]) -> tuple[dict, dict]:
    """-> (the front matter of a `TEAM.md` as it plays under its template, the team its form makes of the members
    -- `formed`): the template's limits and `schedule:` where
    `TEAM.md` writes none; under a `form:`, the edges the form makes of the members when `TEAM.md` writes no
    `reports:`, its root when `TEAM.md` writes no `root:` -- a root written is the form's head --, and the daily
    added to `TEAM.md`'s ceremonies unless one of them is named `daily`. The daily counts the members who report to
    the root in the edges as the team plays (`daily_of`): `TEAM.md`'s own when it writes `reports:`, the form's
    otherwise. A template without `form:` makes no edge and no root: `TEAM.md` writes its own."""
    made = {**template["limits"], **({} if template["schedule"] is None else {"schedule": template["schedule"]}),
            **front}
    said = str(front.get("root") or "").strip() or None
    team = formed(template, members, said, values)
    if template["form"] is None:
        return made, team
    daily = team["ceremony"]
    if "reports" not in front:
        made["reports"] = "\n".join(team["reports"])
    else:                                              # the edges TEAM.md writes: who reports to the root there
        edges = [line.split("->", 1) for line in block(front, "reports") if "->" in line]
        chiefs = [one for sources, target in edges if target.split() == [team["root"]] for one in sources.split()]
        daily = daily_of(template["form"], values, list(dict.fromkeys(chiefs)), team["root"])
    if said is None:
        made["root"] = team["root"]
    ceremonies = block(front, "ceremonies")
    if daily and not any(line.split()[0] == "daily" for line in ceremonies):
        made["ceremonies"] = "\n".join([*ceremonies, daily])
    return made, team


def judged(conductor, front: dict, data: bytes, path: Path, name: str, made: dict | None = None) -> dict:
    """-> the team a declaration's text declares, judged whole -- the agents and their types, the
    edges, the root, the mandators, the ceremonies (their names, participants and `after`
    graph), `key-moved` for a `work:` (the season's, in SEASON.md),
    the role keys (`roles:`, `<key> [<member> ...]` per line: the author's words, each a slug said once, its
    members declared, each once on its line, a key without a member reserved), the name shown -- `name:`, the
    directory's name without it --, the `description:` (None without
    it; never written to the journal) and the digest; each defect
    DECLINES by its name (`Declined`, its
    text the refusal `start` writes). Under what `TEAM.md` names (`made`: its `template` -- `template_of`'s, None
    without one --, the values `applied`, what `documents_of` `read`), the members once judged, the front matter is
    the one the preset shapes (`shaped`); `template` says the preset named and the values it declares, as applied --
    `{template, origin, values: [{name, value, from}]}`, None without a preset --, `applied` every value the team
    applies, `read` its documents' lines for the start to render (`documents_rendered`), `intention` the preset's
    intention rendered for the team (`intention_rendered`), "" without a preset. Called by `team_played` alone."""
    said = front.get("name")
    shown = name if said is None else str(said).strip()
    if not shown or len(shown) > NAME_CHARS or not shown.isprintable():
        decline(f"name-invalid -- {path}: `name: {' '.join(str(said).split())[:40]}` -- a team's name is one line of 1 "
                f"to {NAME_CHARS} printable characters.")
    told = front.get("description")
    description = None if told is None else str(told).strip()
    if description is not None and not described_well(description):
        decline(f"team-invalid -- {path}: `description: {' '.join(str(told).split())[:40]}` -- a team's description is "
                f"one line of 1 to {DESCRIPTION_CHARS} printable characters.")
    agents: dict[str, str] = {}
    for line in block(front, "agents"):
        words = line.split()
        if len(words) != 2:
            decline(f"team-invalid -- {path}: agents: `{line}` -- one line per member, `<name> <path>`.")
        member, at = words
        if not conductor.instance.valid_slug(member):
            decline(f"team-invalid -- {path}: agents: `{member}` -- a member's name is one slug (lowercase, "
                   "digits and single dashes), no `/`.")
        if not path_valid(conductor, at):
            decline(f"team-invalid -- {path}: agents: `{at}` -- an agent is its path under the house, slugs "
                   "(lowercase, digits and single dashes) joined by `/`.")
        if member in agents:
            decline(f"team-invalid -- {path}: agents: `{member}` declared twice -- one name per member.")
        agents[member] = at
    if not agents:
        decline(f"team-invalid -- {path}: `agents:` declares nobody.")
    template = (made or {}).get("template")
    values = {one["name"]: one["value"] for one in (made or {}).get("applied") or []}
    shape = None
    if template is not None:
        front, shape = shaped(front, template, values, list(agents))
    reports = []
    for line in block(front, "reports"):
        if "->" not in line:
            decline(f"team-invalid -- {path}: reports: `{line}` -- an edge is `a b -> c`.")
        left, right = line.split("->", 1)
        sources, targets = left.split(), right.split()
        if not sources or len(targets) != 1:
            decline(f"team-invalid -- {path}: reports: `{line}` -- members on the left, one member on the right.")
        for one in sources + targets:
            if one not in agents:
                decline(f"participant-unknown -- {path}: reports: `{one}` is a member nobody declared.")
        reports.append({"from": sources, "to": targets[0]})
    root_agent = str(front.get("root") or "").strip()
    if not root_agent:
        decline(f"root-missing -- {path}: `root:` names the member a task goes to when no `--to` names one.")
    if root_agent not in agents:
        decline(f"participant-unknown -- {path}: root `{root_agent}` is a member nobody declared.")
    principals = []
    for line in block(front, "principals"):
        if len(line.split()) != 1:
            decline(f"team-invalid -- {path}: principals: `{line}` -- one name per line.")
        principals.append(line)
    ceremonies = [ceremony_of(line, agents, path) for line in block(front, "ceremonies")]
    names = [one["name"] for one in ceremonies]
    for one in ceremonies:
        if names.count(one["name"]) > 1:
            decline(f"team-invalid -- {path}: ceremonies: `{one['name']}` declared twice.")
        if one["after"] is not None and one["after"] not in names:
            decline(f"team-invalid -- {path}: ceremonies: `{one['name']}` follows `{one['after']}`, a ceremony nobody declared.")
    acyclic(ceremonies, path)
    entries: dict[str, str] = {}
    for line in block(front, "entries"):
        if "->" not in line:
            decline(f"team-invalid -- {path}: entries: `{line}` -- one line is `<trigger> -> <document>`.")
        trigger, document = (part.strip() for part in line.split("->", 1))
        if not trigger or len(document.split()) != 1:
            decline(f"team-invalid -- {path}: entries: `{line}` -- one trigger, one document.")
        if trigger != "do" and trigger not in names:
            decline(f"team-invalid -- {path}: entries: `{trigger}` is neither `do` nor a declared "
                   "ceremony's name.")
        if trigger in entries:
            decline(f"team-invalid -- {path}: entries: `{trigger}` declared twice.")
        entries[trigger] = document
    roles: dict[str, list[str]] = {}
    for line in block(front, "roles"):
        key, *members = line.split()
        if not conductor.instance.valid_slug(key):
            decline(f"team-invalid -- {path}: roles: `{key}` -- a role key is one slug (lowercase, digits and single "
                    "dashes), the author's own word.")
        if key in roles:
            decline(f"team-invalid -- {path}: roles: `{key}` declared twice -- one line per key.")
        for at, member in enumerate(members):
            if member not in agents:
                decline(f"participant-unknown -- {path}: roles: `{member}` is a member nobody declared.")
            if member in members[:at]:
                decline(f"team-invalid -- {path}: roles: `{line}` -- `{member}` twice on the line.")
        roles[key] = members
    if "work" in front:
        decline(f"key-moved -- {path}: `work:` is the season's -- move the line to teams/{name}/{SEASON_DOC}.")
    applied = (made or {}).get("applied") or []
    named = [one["name"] for one in (template or {}).get("values") or []]
    return {"agents": agents, "reports": reports, "root": root_agent, "principals": principals,
            "ceremonies": ceremonies, "entries": entries, "roles": roles,
            "limits": limits_of(front, path), "schedule": schedule_of(front, path),
            "name": shown, "description": description, "digest": hashlib.sha256(data).hexdigest()[:12],
            "template": None if template is None else
                        {"template": template["template"], "origin": template["origin"],
                         "values": [value for value in applied if value["name"] in named]},
            "applied": applied, "read": (made or {}).get("read") or documents_none(path),
            "intention": "" if template is None else intention_rendered(
                template, shape, values, any(one["name"] == "daily" for one in ceremonies))}


def seconds_of_duration(value) -> int | None:
    """-> the SECONDS a declaration's duration says -- `10s`, `2m`, `1h`, or a bare whole number of MINUTES (the form
    of before: `schedule: 5`) --, None for a form this contract cannot read or a duration under a second."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value * MINUTE if value >= 1 else None
    text = str(value).strip()
    unit = 1 if text.endswith("s") else MINUTE if text.endswith("m") else HOUR if text.endswith("h") else None
    digits = text[:-1] if unit is not None else text
    if not digits.isdigit() or int(digits) < 1:
        return None
    return int(digits) * (unit or MINUTE)


def schedule_of(front: dict, path: Path) -> int | None:
    """-> the net's step in SECONDS: `schedule:` of `TEAM.md` -- `off` (None: no net, ever), `<n>s`, `<n>m`, `<n>h`
    or a bare whole number of minutes, DEFAULT_SCHEDULE when the key is absent; any other value refuses
    `team-invalid` naming the four forms."""
    if "schedule" not in front:
        return DEFAULT_SCHEDULE
    value = front["schedule"]
    if value is False or (isinstance(value, str) and value.strip() == "off"):
        return None
    seconds = seconds_of_duration(value)
    if seconds is None:
        decline(f"team-invalid -- {path}: `schedule: {value}` -- `off`, or how long the team's timer sleeps at most, "
                "a second at least: `10s`, `2m`, `1h`, or a bare number of minutes (`5`).")
    return seconds


def schedule_seconds(started: dict | None) -> int | None:
    """-> the net's step in seconds as the start kept it: `team-started.schedule` with its `unit` (`s`, team 0.41.0),
    minutes when a journal written before kept no unit, DEFAULT_SCHEDULE when the start kept nothing; None under
    `off`."""
    if not started or "schedule" not in started:
        return DEFAULT_SCHEDULE
    value = started.get("schedule")
    if value is None:
        return None
    return int(value) if started.get("unit") == "s" else int(value) * MINUTE


def limits_of(front: dict, path: Path) -> dict:
    """-> the bounds `TEAM.md` declares, each judged: `parallel` a whole number of 1 or more,
    `budget` a number above 0 (dollars), `retries` a whole number of 0 or more, `timeout` a
    number of seconds above 0, `launches` (the launches of one task) and `budget-launches` (the
    launches of the season) whole numbers of 1 or more, `suspect-max` a duration (`20s`, `2m`, bare minutes),
    kept in seconds, `silence` a whole number of 1 or more (the silent passages in a row that make a member
    suspected; DEFAULT_SILENCE without it); an absent key is no bound; any other value
    refuses `team-invalid` naming the key and the value; a key of before (`launches`, `budget-launches`: the
    bounds counted wake-ups) refuses `limit-retired` naming the key that took its place."""
    found: dict = {}
    for key, now in RETIRED_LIMITS.items():
        if key in front:
            decline(f"limit-retired -- {path}: `{key}:` is gone -- the bounds count launches: say `{now}:`.")
    for key in LIMITS:
        if key not in front:
            continue
        value = front[key]
        whole = isinstance(value, int) and not isinstance(value, bool)
        number = whole or (isinstance(value, float) and value == value)
        if key == "parallel" and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `parallel: {value}` -- a whole number of 1 or more.")
        if key == "budget" and (not number or value <= 0):
            decline(f"team-invalid -- {path}: `budget: {value}` -- a number of dollars above 0.")
        if key == "retries" and (not whole or value < 0):
            decline(f"team-invalid -- {path}: `retries: {value}` -- a whole number of 0 or more.")
        if key == "timeout" and (not number or value <= 0):
            decline(f"team-invalid -- {path}: `timeout: {value}` -- a number of seconds above 0.")
        if key in ("launches", "budget-launches") and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `{key}: {value}` -- a whole number of 1 or more.")
        if key == "silence" and (not whole or value < 1):
            decline(f"team-invalid -- {path}: `silence: {value}` -- a whole number of 1 or more: the exchanges in a "
                    "row a member that owes an answer may end without a message to the team before it is suspected.")
        if key == "suspect-max":                           # kept in seconds: the longest interval of a suspicion
            value = seconds_of_duration(value)
            if value is None:
                decline(f"team-invalid -- {path}: `suspect-max: {front[key]}` -- a duration: seconds (`20s`), "
                        "minutes (`2m`, `10`).")
        found[key] = value
    return found


# --- the templates: a TEAM.md to start from ------------------------------------------------

def templates_of(root: Path, conductor) -> dict[str, dict]:
    """-> every template the house SEES, by its name `<directory>/<name>`: each `<directory>/<name>.md` under
    `<house>/.pp/teams/templates/` first, then under the package's `templates/`, nothing else -- a name of the house
    replacing the package's. A template is a PRESET when its front matter carries one of `PRESET_KEYS` (the
    `documents:` it gives, a team's `form:` or `members:`), a DOCUMENT otherwise; a preset's `nature` is `team` when it
    carries one of `TEAM_KEYS`, `season` otherwise; one whose `requires:` names a package the house does not pin is not
    seen. Each `{template, kind, nature, origin, path, front, description, requires, error}`,
    sorted by name -- `error` the refusal a template whose front matter the engine cannot read gives where it is named
    (`template-invalid`), None otherwise. REFUSES `template-invalid`, citing the file: a directory or a name that is no
    slug."""
    found: dict[str, dict] = {}
    for origin, place in (("house", root / "teams" / "templates"), ("package", TEMPLATES)):
        if not place.is_dir():
            continue
        for path in sorted(place.glob("*/*.md")):
            name = f"{path.parent.name}/{path.stem}"
            if name in found:
                continue
            if not (conductor.instance.valid_slug(path.parent.name) and conductor.instance.valid_slug(path.stem)):
                refuse(f"template-invalid -- {path}: `{name}` -- a template is `<directory>/<name>.md`, each a slug.")
            try:
                front, error = conductor.reading.read(path).front, None
            except conductor.Refusal as refusal:
                front, error = {}, f"template-invalid -- {path}: {refusal}"
            needed = front.get("requires") or []
            needed = [str(one) for one in needed] if isinstance(needed, list) else re.split(r"[\s,]+", str(needed))
            found[name] = {"template": name, "origin": origin, "path": path, "front": front,
                           "kind": "preset" if any(key in front for key in PRESET_KEYS) else "document",
                           "nature": "team" if any(key in front for key in TEAM_KEYS) else "season",
                           "description": str(front.get("description") or ""),
                           "requires": [one for one in needed if one], "error": error}
    pinned = set(conductor.instance.pins(root))
    return {name: found[name] for name in sorted(found) if set(found[name]["requires"]) <= pinned}


def template_of(conductor, templates: dict[str, dict], template: str, where, nature: str | None = None) -> dict:
    """-> the PRESET `template` names as its file says it: its description, the values it declares (`values: |`,
    `values_declared`), the lines of its `documents:` (`documents_declared`) and, for a team, its form, its default
    members, its root and edges (what a preset without `form:` writes as they stand), the paragraph the intention
    gains with the daily, its limits, `schedule`, its role keys (`roles: |`, `<key> <place>...` per line, each place
    one its form has (`PLACES`) written as a hole, `{root}`: filled by the members the form puts there and written
    into a team's `TEAM.md` at its birth, never read for the team after it) and its intention. DECLINES, citing
    `where`: `template-unknown` for a
    name no preset the house sees carries, or one of another `nature` than the one asked (`team` for `TEAM.md`,
    `season` for `SEASON.md`); `template-invalid` for a front matter the engine cannot read, a `form:` no
    form, a `values:` or `documents:` line of another form, a `roles:` line that names anything but places its form
    has, or a `daily:` or `squads:` key: each is a value the preset declares."""
    found = templates.get(template)
    if found is not None and found["error"]:
        decline(found["error"])
    if found is None or found["kind"] != "preset" or nature not in (None, found["nature"]):
        presets = [name for name, one in templates.items()
                   if one["kind"] == "preset" and nature in (None, one["nature"])]
        decline(f"template-unknown -- {where}: `template: {template}` -- the presets are "
                f"{', '.join(presets) or 'none'} (`team templates`).")
    path, front = found["path"], found["front"]
    form = front.get("form")
    if form is not None and str(form) not in FORM_NAMES:
        decline(f"template-invalid -- {path}: `form: {form}` -- {', '.join(FORM_NAMES)}.")
    for key in ("daily", "squads"):
        if key in front:
            decline(f"template-invalid -- {path}: `{key}:` -- a template declares it as a value: `values: |`, "
                    f"`{key} = {front[key]} -- <description>`.")
    places = PLACES[None if form is None else str(form)]
    for line in block(front, "roles"):
        if any(not (one.startswith("{") and one.endswith("}") and one[1:-1] in places) for one in line.split()[1:]):
            decline(f"template-invalid -- {path}: roles: `{line}` -- a line names its key, then places of "
                    + (f"the form `{form}`" if form is not None else "a preset without `form:`") + ", which are "
                    + ", ".join(f"{{{one}}}" for one in places) + ".")
    return {"template": template, "origin": found["origin"], "path": path,
            "values": values_declared(conductor, front, path),
            "documents": documents_declared(conductor, front, path, "template-invalid"),
            "description": found["description"], "form": None if form is None else str(form),
            "team": bool(set(TEAM_KEYS) & set(front)),
            "members": block(front, "members"), "root": front.get("root"), "reports": block(front, "reports"),
            "roles": block(front, "roles"),
            "daily_intention": str(front.get("daily-intention") or ""),
            "limits": {key: front[key] for key in ("budget", "launches", "timeout") if key in front},
            "schedule": front.get("schedule"),
            "intention": body_of(path.read_text(encoding="utf-8"))}


def documents_declared(conductor, front: dict, path: Path, code: str) -> list[tuple[str, list[str]]]:
    """-> the lines of a `documents: |` block, one per key, `<key> <document> ...`, in their order: `(key, documents)`
    -- the key `all`, a role key or a hole `{<name>}` the values fill (a hole by its name: `{{` and `}}` are none); a
    document `<directory>/<name>`, a template the house sees, or `<name>`, a file `<name>.md` of the team's directory.
    DECLINES `code` citing `path` for a line of another form: a key said twice, a key without a document, a document
    twice on its line, a word no such name."""
    found: list[tuple[str, list[str]]] = []
    slug = conductor.instance.valid_slug
    for line in block(front, "documents"):
        key, *documents = line.split()
        if (not documents or any(key == one for one, _ in found) or len(set(documents)) != len(documents)
                or not (key == ALL or slug(key) or ((hole := HOLE.fullmatch(key)) is not None and hole.group(1)))
                or any(not all(slug(part) for part in one.split("/")) or one.count("/") > 1 for one in documents)):
            decline(f"{code} -- {path}: documents: `{line}` -- one line per key, `<key>|{ALL} <document> ...`, the key "
                    "once, each document `<directory>/<name>` or `<name>` once on its line.")
        found.append((key, documents))
    return found


def document_found(templates: dict[str, dict], directory: Path, document: str, at: Path) -> dict:
    """-> where a document a line names stands: `{template, origin, path}` -- a template the house sees for
    `<directory>/<name>` (`origin` house or package), the file `<name>.md` of the team's `directory` for `<name>`
    (`origin` team). DECLINES `document-unknown` citing `at`: no such document, or a preset; `template-invalid` for a
    template whose front matter the engine cannot read."""
    if "/" in document:
        found = templates.get(document)
        if found is not None and found["error"]:
            decline(found["error"])
        if found is None or found["kind"] != "document":
            decline(f"document-unknown -- {at}: documents: `{document}` -- "
                    + ("a preset, named by `template:`" if found else "no template of that name")
                    + " (`team templates`).")
        return {"template": document, "origin": found["origin"], "path": found["path"]}
    path = directory / f"{document}.md"
    if not path.is_file():
        decline(f"document-unknown -- {at}: documents: `{document}` -- no {path}: a name without `/` is a file of the "
                "team's directory, `<directory>/<name>` a template (`team templates`).")
    return {"template": document, "origin": "team", "path": path}


def edges_members(preset: dict) -> list[str]:
    """-> the members a team preset without `members:` names by its `root:` and its `reports:` -- the root first, then
    each member of an edge in its order, each once: what `team templates` shows of its team."""
    named = [str(preset["root"])] if preset.get("root") else []
    for edge in preset["reports"]:
        sources, _, target = edge.partition("->")
        named += [*sources.split(), *target.split()]
    return list(dict.fromkeys(named))


def documents_none(path: Path) -> dict:
    """-> what `documents_of` says of a values file that names no preset and no document."""
    return {"path": path, "template": None, "lines": [], "documents": {}, "declared": [], "given": {}}


def documents_of(root: Path, conductor, directory: Path, front: dict, path: Path, code: str) -> dict:
    """-> what ONE values file -- `TEAM.md` (`code` `team-invalid`), `SEASON.md` (`season-invalid`) -- says of its
    documents, the ONE reader of both: the preset its `template:` names (`template_of`, of the file's nature; None
    without one), the lines of `documents:` -- the preset's first, each line of the file replacing, in place, the
    preset's line whose key is the same once filled (`key_named`: the file's values over the preset's defaults) --,
    `[(key, documents, at)]`, `at` the file the line is read from, two lines of one file on one key refused; each
    document found once (`document_found`), `{name: {template, origin, path}}`; the values the preset and the documents
    declare, the preset's first and the first of a name winning, `[{name, description, default, at}]`; the values the
    file gives (`values_given`). DECLINES `code` (`team-invalid`, `season-invalid`) for a line of another form, and
    `template-unknown`, `template-invalid`, `document-unknown`."""
    chosen = str(front.get("template") or "").strip() or None
    own = documents_declared(conductor, front, path, code)
    read = {**documents_none(path), "given": values_given(conductor, front, path, code)}
    if chosen is None and not own:
        return read
    templates = templates_of(root, conductor)
    nature = "team" if code == "team-invalid" else "season"
    preset = None if chosen is None else template_of(conductor, templates, chosen, path, nature)
    filling = {**{one["name"]: one["default"] for one in (preset or {}).get("values") or []
                  if one["default"] is not None}, **read["given"]}
    lines: dict[str, tuple] = {}
    sources = (((preset or {}).get("documents") or [], (preset or {}).get("path"), {}, "template-invalid"),
               (own, path, {}, code))
    for source, at, lined, refused in sources:
        for key, documents in source:
            named = key_named(key, filling)
            if named in lined:
                decline(f"{refused} -- {at}: documents: `{key}` -- the key `{named}` said twice once filled: one line "
                        "per key.")
            lined[named] = True
            lines[named] = (key, documents, at)
    found: dict[str, dict] = {}
    declared: dict[str, dict] = {one["name"]: {**one, "at": path} for one in (preset or {}).get("values") or []}
    for _, documents, at in lines.values():
        for one in documents:
            if one in found:
                continue
            found[one] = document_found(templates, directory, one, at)
            if found[one]["origin"] != "team":
                for value in values_declared(conductor, templates[one]["front"], found[one]["path"]):
                    declared.setdefault(value["name"], {**value, "at": path})
    return {**read, "template": preset, "lines": list(lines.values()),
            "documents": found, "declared": list(declared.values())}


def key_named(key: str, values: dict[str, str]) -> str:
    """-> a key of a `documents:` line as its values name it: a hole `{<name>}` filled when a value names it, the key as
    written otherwise -- what two lines are compared by."""
    hole = HOLE.fullmatch(key)
    return values.get(hole.group(1), key) if hole is not None and hole.group(1) else key


def quoted(names: list[str]) -> str:
    """-> names as the intention says them: `a`, `a` and `b`, `a`, `b` and `c`."""
    marked = [f"`{one}`" for one in names]
    return marked[0] if len(marked) == 1 else ", ".join(marked[:-1]) + " and " + marked[-1]


def daily_of(form: str | None, values: dict[str, str], chiefs: list[str], head: str) -> str | None:
    """-> the daily's line under a wide form (`star`, `tree`): the value `daily` its rhythm, the `chiefs` -- the
    members who report to the root `head` -- its participants, the root its facilitator; None for another form, an
    empty rhythm, or fewer than two chiefs."""
    rhythm = values.get("daily") or ""
    return (f"daily {rhythm} with {' '.join(chiefs)} -> {head}"
            if form in ("star", "tree") and rhythm and len(chiefs) >= 2 else None)


def formed(template: dict, members: list[str], root: str | None, values: dict[str, str]) -> dict:
    """-> the team a template's FORM makes of its members, in their order, under the `values` applied (`{name:
    value}`): `star` -- the root (the first, or `root` moved to the head) and every other member reporting to it,
    the daily when two of them or more report to it; `chain` -- each member reporting to the one before it,
    the first the root; `one` -- a single member, the root; `tree` -- the root, then `squads` squad
    leads reporting to it (the value `squads`, a whole number of 1 or more, else SQUADS), then the workers, given to
    the squad leads in turn and reporting to theirs, the daily of the squad leads when they are two or
    more. The daily's rhythm is the value `daily`: empty, or not declared, no daily. A template without `form:`
    says its own `reports:` as they stand, its root `root`, else its
    `root:`, else the first member, no daily. A form given members it cannot hold DECLINES `team-invalid`;
    a root nobody declared is said as asked, for the judge to refuse. `holes` are the values built in a team preset,
    which the form makes of the members: what the intention names them by (`intention_rendered`); `places` the same
    places as lists of members (`PLACES` says those each form has): what a preset's role keys name (`preset_roles`)."""
    form, name = template["form"], template["template"]
    if form is None:
        root = root or (str(template["root"]) if template["root"] else None)
    if form == "one" and len(members) != 1:
        decline(f"team-invalid -- template `{name}` holds one member: {len(members)} given.")
    if form not in ("one", None) and len(members) < 2:
        decline(f"team-invalid -- template `{name}` holds two members or more: {len(members)} given.")
    squads = values.get("squads") if form == "tree" else None
    if squads is not None and (not squads.isdigit() or int(squads) < 1):
        decline(f"team-invalid -- template `{name}`: `squads = {squads}` -- a whole number of 1 or more.")
    leads = SQUADS if squads is None else int(squads)
    if form == "tree" and len(members) < 1 + 2 * leads:
        decline(f"team-invalid -- template `{name}` with {leads} squad lead(s) holds {1 + 2 * leads} members or "
                f"more -- the root, the squad leads, one worker each at least: {len(members)} given.")
    order = ([root] + [one for one in members if one != root]) if root in members else list(members)
    head = root or order[0]
    others = [one for one in order if one != head]
    chiefs, workers = (others[:leads], others[leads:]) if form == "tree" else (others, [])
    crews = {chief: workers[at::leads] for at, chief in enumerate(chiefs)} if form == "tree" else {}
    if form in ("star", "tree"):
        reports = ([f"{' '.join(chiefs)} -> {head}"] if chiefs else []) + [
            f"{' '.join(crew)} -> {chief}" for chief, crew in crews.items()]
    elif form == "chain":
        reports = [f"{order[at]} -> {order[at - 1]}" for at in range(1, len(order))]
    elif form is None:
        reports = list(template["reports"])
    else:
        reports = []
    daily = daily_of(form, values, chiefs, head)
    holes = {"root": f"`{head}`", "others": quoted(others) if others else "",
             "chain": " -> ".join(f"`{one}`" for one in order), "last": f"`{order[-1]}`",
             "squads": quoted(chiefs) if chiefs else "", "workers": quoted(workers) if workers else "",
             "tree": "; ".join(f"`{chief}` with {quoted(crew)}" for chief, crew in crews.items()),
             "quorum": str(max(1, len(others) - 1)), "count": str(len(others))}
    places = {"root": [head], "others": others, "squads": chiefs, "workers": workers, "last": [order[-1]]}
    return {"members": order, "root": head, "reports": reports, "ceremony": daily, "holes": holes, "places": places}


def intention_rendered(template: dict, team: dict, values: dict[str, str], daily: bool) -> str:
    """-> the intention a team preset makes of a team (`formed`'s): its body, each hole filled by the one filling
    (`holes_filled`) -- the values applied, then the values built in a team preset (`{root}`, `{others}`,
    `{chain}`, `{last}`, `{squads}`, `{workers}`, `{tree}`, `{quorum}`, `{count}`), which win name by name, and
    `{daily}`, the template's `daily-intention` when the daily stands (`daily`), nothing otherwise; a paragraph left
    empty closes up. DECLINES `value-undeclared` citing the template."""
    where = template.get("path") or f"template `{template['template']}`"
    holes = {**values, **team["holes"], "daily": ""}
    holes["daily"] = holes_filled(template["daily_intention"], holes, where).strip() if daily else ""
    return re.sub(r"\n{3,}", "\n\n", holes_filled(template["intention"], holes, where)).strip()


def asked_declare(rest: list[str], launched: bool = False) -> dict:
    """-> `declare`'s flags (`DECLARE_FLAGS`): `--season` and `--json` bare; a flag of `DECLARE_MANY` the list of what
    it was given -- `--member` a `(name, path)`, `--value` a `(name, value)` cut at its first `=`, `--role` a `(key,
    [members])`, its members the words up to the next flag, the others a word --; any other flag once, None when not
    given. Refused before anything is read: `flag-retired` (a bound of before, `--compose`, `--no-compose`); the usage
    for a flag `declare` does not take, a flag short of its words, a flag given twice, a `--value` without `=`, a
    `--document` without a key and a document, a flag of
    `TEAM.md` alone (`DECLARE_TEAM`) under `--season`, and a call that names no key -- `launched`: the season's flags
    of `start` named one (`season_declared`); `team-invalid` for a line
    break in a word a line of the file is made of, and for one name given twice to a flag or given to a flag and to
    its contrary (`DECLARE_PAIRS`): a call says each line once."""
    found: dict = {flag: [] if flag in DECLARE_MANY else False if words == 0 else None
                   for flag, words in DECLARE_FLAGS.items()}
    given: set[str] = set()
    index = 0
    while index < len(rest):
        word = rest[index]
        flag = word[2:] if word.startswith("--") else ""
        if word in RETIRED_FLAGS:
            refuse(f"flag-retired -- `{word}`: the bounds count launches -- say `{RETIRED_FLAGS[word]}`.")
        if word in ("--compose", "--no-compose"):
            now = "--no-document <key>" if word == "--no-compose" else '--document "<key>|all <document> ..."'
            refuse(f"flag-retired -- `{word}`: a team names its documents by key -- say `{now}`.")
        if flag not in DECLARE_FLAGS or (flag in given and flag not in DECLARE_MANY):
            refuse(USAGE)
        given.add(flag)
        words = DECLARE_FLAGS[flag]
        if words is None:                                  # a role: its key, then its members up to the next flag
            last = next((at for at in range(index + 1, len(rest)) if rest[at].startswith("--")), len(rest))
            said = rest[index + 1:last]
        else:
            last = index + 1 + words
            said = rest[index + 1:last]
            if len(said) != words:
                refuse(USAGE)
        if not said and words != 0:
            refuse(USAGE)
        if flag not in ("description", "body-file") and any("\n" in one or "\r" in one for one in said):
            refuse(f"team-invalid -- `--{flag}`: one line, no line break.")
        if flag == "value":
            named, equal, value = said[0].partition("=")
            if not equal or not named.strip():
                refuse(USAGE)
            found[flag].append((named.strip(), value.strip()))
        elif flag == "document":
            if len(said[0].split()) < 2:
                refuse(USAGE)
            found[flag].append(" ".join(said[0].split()))
        elif flag == "report":                         # an edge: its members, then the one they report to
            sources, arrow, target = said[0].partition("->")
            if not arrow or not sources.split() or len(target.split()) != 1:
                refuse(f"team-invalid -- `--report {said[0]}`: one edge, `<member>... -> <member>`.")
            found[flag].append((target.strip(), f"{' '.join(sources.split())} -> {target.strip()}"))
        elif flag == "member":
            found[flag].append((said[0], said[1]))
        elif flag == "role":
            found[flag].append((said[0], said[1:]))
        elif flag in DECLARE_MANY:
            found[flag].append(said[0])
        else:
            found[flag] = True if words == 0 else said[0]
        index = last
    if found["season"] and any(flag in given for flag in DECLARE_TEAM):
        refuse(USAGE)
    if not given - {"season", "json"} and not launched:    # no key named: nothing to write
        refuse(USAGE)
    named_by = {"value": lambda one: one[0], "document": lambda one: one.split()[0], "member": lambda one: one[0],
                "role": lambda one: one[0], "report": lambda one: one[0]}
    for flag, contrary in DECLARE_PAIRS:
        names = [named_by[flag](one) for one in found[flag]]
        twice = next((one for one in names if names.count(one) > 1), None)
        if twice is None:
            twice = next((one for one in found[contrary] if found[contrary].count(one) > 1), None)
            flag = contrary if twice is not None else flag
        if twice is not None:
            refuse(f"team-invalid -- `--{flag} {twice}` given twice: a call says each line once.")
        both = next((one for one in names if one in found[contrary]), None)
        if both is not None:
            refuse(f"team-invalid -- `--{flag} {both}` and `--{contrary} {both}`: a call writes a line or takes it "
                   "out, never both.")
    return found


def season_declared(rest: list[str]) -> tuple[list[str], dict | None]:
    """-> (`declare`'s own flags, the season's flags of `start` `{asked, packages, profiles}`) of a `declare
    --season`: the words read by `start`'s reader (`season_flags`) -- what follows a `--member <name>` that member's
    profile, a `--package` the season's --, then a flag of `SEASON_LAUNCH` and its word taken out of the team's part,
    `--json` wherever it stands; the rest is `declare`'s (`asked_declare`). Without `--season`, (the words, None). A
    season's flag given twice, or short of its word, is the usage."""
    if "--season" not in rest:
        return rest, None
    team_part, packages, profiles = season_flags([one for one in rest if one != "--json"])
    kept, asked, index = [], {}, 0
    while index < len(team_part):
        flag = team_part[index][2:] if team_part[index].startswith("--") else ""
        if flag in SEASON_LAUNCH:
            if flag in asked or index + 1 >= len(team_part):
                refuse(USAGE)
            asked[flag] = team_part[index + 1]
            index += 2
            continue
        words = DECLARE_FLAGS.get(flag)
        step = 1 + (words if isinstance(words, int) else 0)
        kept += team_part[index:index + step]
        index += step
    return kept + [one for one in rest if one == "--json"], {"asked": asked, "packages": packages, "profiles": profiles}


def launch_judged(root: Path, conductor, name: str, launched: dict, text: str) -> None:
    """`start`'s judges (`season_opened`) on the season's flags of a `declare --season`, over `text`, SEASON.md as
    the call writes it without them: what `start` refuses of them refuses, by its code. A `TEAM.md` or a `SEASON.md`
    that `start` refuses already leaves the flags judged on their own, over no SEASON.md -- or unjudged, TEAM.md
    refused: the write goes on, as `declare` writes beside a refusal it did not cause."""
    try:
        team = team_played(root, conductor, name)
    except Declined:
        return
    flagged = (launched["asked"], launched["packages"], launched["profiles"])
    try:
        season_opened(root, conductor, name, team, *flagged, text=text)
        return
    except Declined as declining:
        refused = str(declining)
    try:
        season_opened(root, conductor, name, team, {}, [], {}, text=text)
    except Declined:
        try:
            season_opened(root, conductor, name, team, *flagged, text="")
        except Declined as declining:
            refuse(str(declining))
        return
    refuse(refused)


def numbered(flag: str, value: str, whole: bool):
    """-> a limit given on the command line as the number it says -- `team-invalid` naming the flag
    otherwise; the judge then bounds it as it bounds `TEAM.md`'s."""
    try:
        return int(value) if whole or value.isdigit() else float(value)
    except ValueError:
        refuse(f"team-invalid -- `--{flag} {value}`: a {'whole number' if whole else 'number'}.")


def templates_verb(rest: list[str]) -> int:
    """`team templates [--json]`: every template the house sees (`templates_of`), one line each -- its name, its kind
    (`preset` or `document`), its origin, a team preset's default members, its description --, under it one line per
    value it declares and, for a preset, one per line of its `documents:`; under `--json` one object per template,
    `{template, kind, origin, description, values}` -- each value `{name, description, default}` --, `requires` when
    it names packages, a preset's `documents` (`[{key, documents}]`, the keys as written: a template knows no team)
    and, for a team preset, `{form, members, root, reports, ceremony, limits, intention}`, the team it makes for its
    default members, with `roles` (`[{role, places}]`, the places as written) when it has `roles:`. Nothing
    written; a template the engine cannot read, or a line of another form, gives its own line
    `{template, origin, refusal}` (`template-invalid`), the others listed. Read in the HOUSE (`machine_house()`),
    whatever instance calls. `--render` renders one document instead (`render_dry`)."""
    root, conductor = machine_house()
    asked = flags(rest, TEMPLATES_FLAGS)
    if asked["render"] is not None:
        return render_dry(root, conductor, asked)
    if asked["value"] or asked["team"] is not None or asked["season"] or asked["text-file"] is not None:
        refuse(USAGE)
    for name, one in templates_of(root, conductor).items():
        try:
            if one["error"]:
                decline(one["error"])
            said = {"template": name, "kind": one["kind"], "origin": one["origin"], "description": one["description"],
                    "values": values_declared(conductor, one["front"], one["path"])}
            if one["requires"]:
                said["requires"] = one["requires"]
            if one["kind"] == "preset":
                preset = template_of(conductor, {name: one}, name, one["path"])
                said["documents"] = [{"key": key, "documents": documents} for key, documents in preset["documents"]]
                if preset["team"]:
                    defaults = {value["name"]: value["default"] or "" for value in preset["values"]}
                    team = formed(preset, preset["members"] or edges_members(preset), None, defaults)
                    said.update({"form": preset["form"], "members": team["members"], "root": team["root"],
                                 "reports": [{"from": edge.split("->")[0].split(), "to": edge.split("->")[1].strip()}
                                             for edge in team["reports"]],
                                 "ceremony": team["ceremony"], "limits": preset["limits"],
                                 "intention": intention_rendered(preset, team, defaults, bool(team["ceremony"]))})
                    if preset["roles"]:
                        said["roles"] = [{"role": line.split()[0], "places": line.split()[1:]}
                                         for line in preset["roles"]]
        except Declined as declining:
            said = {"template": name, "origin": one["origin"], "refusal": str(declining)}
        if asked["json"]:
            print(json.dumps(said, ensure_ascii=False))
            continue
        if "refusal" in said:
            print(f"{name}  refused · {one['origin']} -- {said['refusal']}")
            continue
        members = f"  {', '.join(said['members'])}" if "members" in said else ""
        print(f"{name}  {one['kind']} · {one['origin']}{members} -- {one['description']}")
        for value in said["values"]:
            default = f" = {value['default']}" if value["default"] is not None else ""
            print(f"    {value['name']}{default} -- {value['description']}")
        for line in said.get("documents") or []:
            print(f"    documents: {line['key']} {' '.join(line['documents'])}")
    return 0


def render_dry(root: Path, conductor, asked: dict) -> int:
    """`team templates --render <directory>/<name> [--value <name>=<value>]... [--team <team> [[--season] --text-file
    <path>|-]] [--json]`: ONE document rendered as `team start` writes it at the root of a team's directory -- its
    conducted head and its body, holes filled by the one filling (`document_rendered`) -- and NOTHING written. The
    values: each `--value` given, else the team's under `--team` (`team` its name, the values its `TEAM.md` applies,
    those its `SEASON.md` gives over them -- under `--text-file`, the CANDIDATE text (`candidate_read`) in the place
    of `TEAM.md`, of `SEASON.md` under `--season`, the other file read on the disk: the values the start takes if
    the text is written), else the document's default; a value given empty (`--value <name>=`) is WITHDRAWN: the team's is not
    taken, the document's default is, or `value-missing`; under `--json` ONE object `{template, text, values: [{name,
    value, from}]}`, `from` `given` or `default`, the text alone otherwise. Refuses: `template-unknown` (no document
    of that name -- a preset is none), `template-invalid`, `team-unknown`, `team-invalid` (a `--text-file` path that
    is no file), the team's own refusal, `value-unknown` (a value the document does not declare), `value-missing` (a
    value without one, named), the usage (a `--value` without `=`, `--season` or `--text-file` without `--team`,
    `--season` without `--text-file`)."""
    if (asked["team"] is None and (asked["season"] or asked["text-file"] is not None)
            or asked["season"] and asked["text-file"] is None):
        refuse(USAGE)
    candidate = candidate_read(asked)
    name = asked["render"]
    given: dict[str, str] = {}
    for one in asked["value"]:
        named, equal, value = one.partition("=")
        if not equal or not named.strip():
            refuse(USAGE)
        given[named.strip()] = value.strip()
    withdrawn = {named for named, value in given.items() if not value}   # given empty: the team's not taken
    asked_names = list(given)
    given = {named: value for named, value in given.items() if value}
    found = templates_of(root, conductor).get(name)
    try:
        if found is not None and found["error"]:
            decline(found["error"])
        if found is None or found["kind"] != "document":
            decline(f"template-unknown -- `--render {name}`: no document of that name"
                    + (" -- a preset renders none" if found else "") + " (`team templates`).")
        defaults: dict[str, str] = {}
        if asked["team"] is not None:
            team_name, _ = named_team(conductor, [asked["team"]])
            if not team_doc(root, team_name).is_file():
                refuse(f"team-unknown -- no {team_doc(root, team_name)}: the owner declares the team there.")
            season_path = team_root(root, team_name) / SEASON_DOC
            team = team_played(root, conductor, team_name, None if asked["season"] else candidate)
            season = season_front(conductor, season_path, candidate if asked["season"] else None) or {}
            defaults = {BUILT_IN: team_name, **{one["name"]: one["value"] for one in team["applied"]},
                        **values_given(conductor, season, season_path, "season-invalid")}
        declared = values_declared(conductor, found["front"], found["path"])
        names = [BUILT_IN, *(one["name"] for one in declared)]
        for named in asked_names:
            if named not in names:
                decline(f"value-unknown -- `--value {named}`: {name} declares "
                        f"{', '.join(f'`{one}`' for one in names[1:]) or 'no value'} (`team templates`).")
        values = []
        for named, default in [(BUILT_IN, None), *((one["name"], one["default"]) for one in declared)]:
            if named in given:
                values.append({"name": named, "value": given[named], "from": "given"})
            elif named in defaults and named not in withdrawn:
                values.append({"name": named, "value": defaults[named], "from": "default"})
            elif default is not None:
                values.append({"name": named, "value": default, "from": "default"})
            elif named != BUILT_IN and named in withdrawn:
                decline(f"value-missing -- `--render {name}`: `{named}` has no default, and `--value {named}=` took "
                        f"its value away -- give it a value, `--value {named}=<value>`.")
            elif named != BUILT_IN:
                decline(f"value-missing -- `--render {name}`: `{named}` has no default -- give it, `--value "
                        f"{named}=<value>`, or name a team that gives it (`--team`).")
        holes = {hole.group(1) for hole in HOLE.finditer(found["path"].read_text(encoding="utf-8")) if hole.group(1)}
        if BUILT_IN in holes and not any(one["name"] == BUILT_IN for one in values) and BUILT_IN in withdrawn:
            decline(f"value-missing -- `--render {name}`: `{BUILT_IN}` -- the team's name, taken away by `--value "
                    f"{BUILT_IN}=` -- give it, `--value {BUILT_IN}=<name>`.")
        if BUILT_IN in holes and not any(one["name"] == BUILT_IN for one in values):
            decline(f"value-missing -- `--render {name}`: `{BUILT_IN}` -- the team's name: `--team <team>` or "
                    f"`--value {BUILT_IN}=<name>`.")
        text = document_rendered(conductor, found["path"], {one["name"]: one["value"] for one in values})
    except Declined as declining:
        refuse(str(declining))
    if asked["json"]:
        print(json.dumps({"template": name, "text": text, "values": values}, ensure_ascii=False))
    else:
        sys.stdout.write(text)
    return 0


# --- a house's documents: their source read, created, replaced, deleted ---------------------------

def document_places(root: Path, conductor, name: str) -> tuple[Path, Path]:
    """-> (the house's file of the document `name`, the package's): `<house>/.pp/teams/templates/<directory>/<name>.md`
    and `templates/<directory>/<name>.md` of the package, standing or not. REFUSES `template-invalid` for a name that is
    not `<directory>/<name>`, each a slug."""
    parts = name.split("/")
    if len(parts) != 2 or not all(conductor.instance.valid_slug(part) for part in parts):
        refuse(f"template-invalid -- `{name}`: a document is named `<directory>/<name>`, each part a slug.")
    return root / TEMPLATES_PLACE / parts[0] / f"{parts[1]}.md", TEMPLATES / parts[0] / f"{parts[1]}.md"


def text_handed(given: str) -> str | None:
    """-> the text `--body-file <given>` hands over, read in BYTES and decoded as UTF-8, its line endings as they are:
    standard input's for `-`, the file's otherwise; None when no such file stands."""
    if given == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    path = Path(given)
    return path.read_bytes().decode("utf-8") if path.is_file() else None


def document_kind(conductor, path: Path) -> str:
    """-> `preset` when the file's front matter carries one of `PRESET_KEYS`, `document` otherwise -- a front matter
    the engine cannot read included: its source is still read, replaced or deleted."""
    try:
        front = conductor.reading.read(path).front
    except conductor.Refusal:
        return "document"
    return "preset" if any(key in front for key in PRESET_KEYS) else "document"


def document_judged(conductor, name: str, text: str) -> None:
    """Judges the text `--body-file` hands over for the house's document `name`: a front matter the engine reads, no
    key of a preset (`PRESET_KEYS`), its `values:` of the form a template declares (`values_declared`). REFUSES
    `document-invalid`, naming what fails."""
    lines = text.splitlines()
    try:
        start, end = conductor.sections.front_span(lines)
        front = conductor.reading.front_matter(lines[start:end])
    except conductor.Refusal as refusal:
        refuse(f"document-invalid -- {name}: {refusal} -- a document starts with its front matter, between two `---` "
               "lines.")
    preset = [key for key in PRESET_KEYS if key in front]
    if preset:
        refuse(f"document-invalid -- {name}: `{preset[0]}:` is a key of a preset; a document has none of `documents`, "
               "`form` or `members`.")
    try:
        values_declared(conductor, front, Path(name))
    except Declined as declining:
        refuse(f"document-invalid -- {name}: {str(declining).split(' -- ', 1)[-1]}")


def document_users(root: Path, conductor, name: str) -> list[str]:
    """-> who NAMES the house's document `name` on a line of `documents:`, one `<who> <file> <key>` each, the key
    between backquotes: every `TEAM.md` and `SEASON.md` of the house's teams, read without judging the team, and every
    preset of the house. A file whose front matter the engine cannot read names nothing."""
    files = []
    home = root.parent / TEAMS
    if home.is_dir():
        for directory in sorted(one for one in home.iterdir() if one.is_dir()):
            files += [(directory.name, directory / one) for one in (TEAM_DOC, SEASON_DOC)]
    shelf = root / TEMPLATES_PLACE
    if shelf.is_dir():
        files += [(f"{path.parent.name}/{path.stem}", path) for path in sorted(shelf.glob("*/*.md"))]
    found = []
    for who, path in files:
        if not path.is_file():
            continue
        try:
            front = conductor.reading.read(path).front
        except conductor.Refusal:
            continue
        for line in block(front, "documents"):
            key, *documents = line.split()
            if name in documents:
                found.append(f"{who} {path.relative_to(root.parent) if path.is_relative_to(root.parent) else path} "
                             f"`{key}`")
    return found


def document_verb(rest: list[str]) -> int:
    """`team document <directory>/<name> [--new | --body-file <path>|- | --delete] [--json]`: the ONE writer of the
    house's documents, `<house>/.pp/teams/templates/<directory>/<name>.md`, as `declare` is the one writer of the
    values files. Without an action, the SOURCE of the document the house sees -- the house's file first, else the
    package's -- read, nothing written: its name, kind, origin and path, then its text whole; under `--json` ONE
    object `{template, origin, kind, path, text}`. `--new` writes the skeleton of a document (`DOCUMENT_SKELETON`),
    its directory born when needed; `--body-file` replaces the text of the house's document by the file's -- `-` by
    standard input's --, judged first (`document_judged`); `--delete` removes it, and its directory with its last
    document. Each writes the house's file alone: a team's file, a journal and the package are never touched, and a
    refusal writes nothing. Says what it did -- and the package's document of the same name, which the house's masks
    once created and shows again once deleted --; under `--json` ONE object `{template, done, path, package}`,
    `package` that document's path or null. REFUSES: `template-invalid` (a name that is not `<directory>/<name>`),
    `document-unknown` (no document of that name, or a preset to replace or delete), `document-exists` (`--new` on a
    name the house has), `document-preset` (`--new` on the name of a package's preset, which it would hide),
    `document-readonly` (a document the package alone carries, to replace or delete), `document-invalid` (a text
    `document_judged` refuses, or `--body-file` naming no file), `document-used` (a line of `documents:` names it,
    `document_users`, each said); two actions, or an action without its argument, are the usage. Read and written in
    the HOUSE (`machine_house()`), whatever instance calls."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    root, conductor = machine_house()
    name, asked = rest[0], flags(rest[1:], DOCUMENT_FLAGS)
    if sum(1 for action in ("new", "body-file", "delete") if asked[action] not in (None, False)) > 1:
        refuse(USAGE)
    own, packaged = document_places(root, conductor, name)
    package = packaged if packaged.is_file() else None
    shown = (lambda path: str(path.relative_to(root.parent)) if path.is_relative_to(root.parent) else str(path))
    origin = "house" if own.is_file() else "package" if package is not None else None

    def said(done: str, path: Path, line: str) -> int:
        if asked["json"]:
            print(json.dumps({"template": name, "done": done, "path": shown(path),
                              "package": None if package is None else shown(package)}, ensure_ascii=False))
        else:
            print(f"pp-team: {name} {line}")
        return 0

    if asked["new"]:
        if own.is_file():
            refuse(f"document-exists -- {shown(own)}: the house already has `{name}` -- `team document {name}` prints "
                   "it, `--body-file` replaces its text.")
        if package is not None and document_kind(conductor, package) == "preset":
            refuse(f"document-preset -- {shown(package)}: `{name}` is a preset of the package, and a house document "
                   f"of that name would hide it -- choose another name; `team document {name}` prints the preset.")
        placed(own, DOCUMENT_SKELETON.format(name=own.stem).encode("utf-8"))
        return said("created", own, f"created · {shown(own)}" + (f" · it hides the package's {shown(package)}"
                                                                    if package is not None else ""))
    if origin is None:
        refuse(f"document-unknown -- `{name}`: neither the house nor the package has a document of that name "
               "(`team templates` lists them).")
    if asked["body-file"] is None and not asked["delete"]:
        path = own if origin == "house" else package
        text = path.read_bytes().decode("utf-8")
        kind = document_kind(conductor, path)
        if asked["json"]:
            print(json.dumps({"template": name, "origin": origin, "kind": kind, "path": shown(path), "text": text},
                             ensure_ascii=False))
        else:
            sys.stdout.write(f"pp-team: {name} · {kind} · {origin} · {shown(path)}\n{text}")
        return 0
    if origin == "package":
        refuse(f"document-readonly -- {shown(package)}: `{name}` belongs to the package and cannot be changed -- "
               f"`team document {name} --new` gives the house its own document of that name, used in its place.")
    if document_kind(conductor, own) == "preset":
        refuse(f"document-unknown -- {shown(own)}: `{name}` is a preset, not a document: this verb prints a preset "
               "but never replaces or deletes one.")
    if asked["delete"]:
        users = document_users(root, conductor, name)
        if users:
            refuse(f"document-used -- `{name}` is still named on a line of `documents:` by " + "; ".join(users)
                   + " -- take it off each of these lines first: `team declare <team> [--season] --document "
                   "\"<key> <document> ...\"` rewrites a line, `--no-document <key>` removes it; a house's preset is "
                   "changed in its own file.")
        own.unlink()
        if not any(own.parent.iterdir()):
            own.parent.rmdir()
        return said("deleted", own, f"deleted · {shown(own)}" + (f" · the package's {shown(package)} is used again"
                                                                    if package is not None else ""))
    text = text_handed(asked["body-file"])
    if text is None:
        refuse(f"document-invalid -- `--body-file {Path(asked['body-file'])}`: there is no such file.")
    document_judged(conductor, name, text)
    if own.read_bytes() == text.encode("utf-8"):
        return said("unchanged", own, f"unchanged · {shown(own)} · the same text, nothing written")
    placed(own, text.encode("utf-8"))
    return said("replaced", own, f"replaced · {shown(own)}")


def conducted_head(conductor, text: str) -> str:
    """-> the front matter of a template without the template's own keys (`TEMPLATE_KEYS`), cut by the engine's
    spans (`sections.front_span`, `key_span`) -- each other key at its bytes, in its order; "" when none is left."""
    lines = text.splitlines()
    try:
        start, end = conductor.sections.front_span(lines)
    except conductor.Refusal:
        return ""
    spans = [span for key in TEMPLATE_KEYS if (span := conductor.sections.key_span(lines, start, end, key))]
    for first, last in sorted(spans, reverse=True):
        del lines[first:last]
        end -= last - first
    kept = lines[start:end]
    return f"{BORDER}\n" + "\n".join(kept) + f"\n{BORDER}\n" if any(one.strip() for one in kept) else ""


def holes_filled(text: str, values: dict[str, str], where) -> str:
    """-> `text` with each hole `{<name>}` replaced by its value and `{{`, `}}` one brace each -- the ONE filling of the
    product: a team preset's intention (`intention_rendered`), a document (`document_rendered`) and a key of a line. A
    placeholder `<name>` the member fills in is never read. A hole no value names DECLINES `value-undeclared`, citing
    `where`."""
    def one(found: re.Match) -> str:
        if found.group(1) is None:
            return found.group(0)[0]
        if found.group(1) not in values:
            decline(f"value-undeclared -- {where}: `{found.group(0)}` -- no template declares `{found.group(1)}` "
                    "(`values:`); a brace of the text itself is written twice, `{{` or `}}`.")
        return values[found.group(1)]
    return HOLE.sub(one, text)


def values_declared(conductor, front: dict, path: Path) -> list[dict]:
    """-> the values a template declares under `values: |`, one line each `<name> [= <default>] -- <description>`, in
    their order: `{name, description, default}`, `default` None without `=`. DECLINES `template-invalid` citing the
    template for a line of another form, a name no slug, a name said twice, or `team` -- the value built in."""
    found: list[dict] = []
    for line in block(front, "values"):
        said, cut, description = line.partition(" -- ")
        named, equal, default = said.partition("=")
        named = named.strip()
        if (not cut or not description.strip() or not conductor.instance.valid_slug(named) or named == BUILT_IN
                or any(one["name"] == named for one in found) or (equal and not default.strip())):
            decline(f"template-invalid -- {path}: values: `{line}` -- one line per value, `<name> [= <default>] -- "
                    f"<description>`, its name a slug said once, `{BUILT_IN}` built in.")
        found.append({"name": named, "description": description.strip(),
                      "default": default.strip() if equal else None})
    return found


def values_given(conductor, front: dict, path: Path, code: str) -> dict[str, str]:
    """-> the values a values file GIVES under `values: |`, one line each `<name> = <value>`, the value empty or not:
    `{name: value}` in their order -- the ONE reader of them, `SEASON.md`'s and `TEAM.md`'s. DECLINES `code`
    (`season-invalid`, `team-invalid`) for a line of another form, a name no slug or said twice."""
    given: dict[str, str] = {}
    for line in block(front, "values"):
        named, equal, value = line.partition("=")
        named = named.strip()
        if not equal or not conductor.instance.valid_slug(named) or named in given:
            decline(f"{code} -- {path}: values: `{line}` -- one line per value, `<name> = <value>`, each once.")
        given[named] = value.strip()
    return given


def values_applied(declared: list[dict], given: dict[str, str], path: Path, whose: str, source: str) -> list[dict]:
    """-> the values a values file APPLIES to what its template declares (`values_declared`'s, in their order):
    `[{name, value, from}]`, `from` the `source` (`season`, `team`) for a value given, `default` otherwise -- the ONE
    judge of them. DECLINES `value-unknown` for a value given that `whose` template does not declare,
    `value-missing` for a value without a default that is not given."""
    names = [one["name"] for one in declared]
    for named in given:
        if named not in names:
            decline(f"value-unknown -- {path}: values: `{named}` -- {whose} declares "
                    f"{', '.join(f'`{one}`' for one in names) or 'no value'} (`team templates`).")
    values = []
    for one in declared:
        if one["name"] in given:
            values.append({"name": one["name"], "value": given[one["name"]], "from": source})
        elif one["default"] is not None:
            values.append({"name": one["name"], "value": one["default"], "from": "default"})
        else:
            decline(f"value-missing -- {path}: `{one['name']}` ({one['description']}) has no default -- give it under "
                    "`values:`, `<name> = <value>`.")
    return values


def document_rendered(conductor, path: Path, values: dict[str, str], headed: bool = False) -> str:
    """-> the document a template makes: its body under its CONDUCTED head (`conducted_head`: every key but the
    template's own, at its bytes), the holes of both filled (`holes_filled`). `headed`: the document opens on a front
    matter even when no key is left -- an empty one: a document of a role is mounted, and the engine mounts no
    document without one. DECLINES `value-undeclared`."""
    text = path.read_text(encoding="utf-8")
    fronted = text.lstrip().startswith(BORDER)
    body = holes_filled(body_of(text) if fronted else text.strip(), values, path)
    head = holes_filled(conducted_head(conductor, text), values, path) if fronted else ""
    if headed and not head:
        head = f"{BORDER}\n{BORDER}\n"
    return head + (body + "\n" if body else "")


def season_text(path: Path, text: str | None = None) -> tuple[str, list[str] | None, str] | None:
    """-> (the text of SEASON.md, its lines when it opens on a front matter -- None otherwise --, its body: the whole
    text without a front matter) -- None without the file. `text`: what `declare` is about to write there, read
    in the file's place."""
    if text is None:
        if not path.is_file():
            return None
        text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != BORDER:
        return text, None, text.strip()
    return text, lines, body_of(text)


def season_word(directory: Path) -> str:
    """-> the owner's word of the season: the body of SEASON.md, "" without the file or its body."""
    read = season_text(directory / SEASON_DOC)
    return "" if read is None else read[2]


def season_front(conductor, path: Path, text: str | None = None) -> dict | None:
    """-> the front matter of SEASON.md -- the file, or `text` in its place --, read and judged by its keys
    (`SEASON_KEYS`) -- `{}` for a file without one,
    None without the file. DECLINES `season-invalid`: a front matter that never closes or that the engine cannot read,
    a key SEASON.md does not say."""
    read = season_text(path, text)
    if read is None:
        return None
    _, lines, _ = read
    front: dict = {}
    if lines is not None:
        end = next((at for at, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
        if end is None:
            decline(f"season-invalid -- {path}: its front matter never closes.")
        try:
            front = conductor.reading.front_matter(lines[1:end])
        except conductor.Refusal as refusal:
            decline(f"season-invalid -- {path}: {refusal}")
    for key in front:
        if key not in SEASON_KEYS:
            decline(f"season-invalid -- {path}: `{key}:` -- {SEASON_DOC} says {', '.join(f'`{one}:`' for one in SEASON_KEYS)}.")
    return front


def season_written(root: Path, conductor, name: str, text: str | None = None) -> dict:
    """-> the season `teams/<name>/SEASON.md` writes -- the file, or `text` in its place --, in the form of `start`'s flags: `{launch: {key: value}, limits:
    {key: value}, packages: [<name>=on|off], profiles: {member: {key: value, packages: [...]}}, work}` -- empty
    without the file or its keys. `packages:` one `<name>=on|off` per line; `profiles:` one line per member, `<member>
    <key>=<value> ...`, the keys those of `PROFILE_LINE` and `package.<name>`. DECLINES `season-invalid`, nothing
    written: a line of another form, a name or a member said twice."""
    path = team_root(root, name) / SEASON_DOC
    front = season_front(conductor, path, text) or {}
    found: dict = {"launch": {key: str(front[key]) for key in LAUNCH_FLAGS if front.get(key) is not None},
                   "limits": {key: front[key] for key in SEASON_LIMITS if front.get(key) is not None},
                   "packages": [], "profiles": {},
                   "work": None if front.get("work") is None else str(front["work"])}
    switch = re.compile(r"[a-z0-9][a-z0-9_-]*=(on|off)")
    for line in block(front, "packages"):
        if not switch.fullmatch(line) or line.partition("=")[0] in [one.partition("=")[0] for one in found["packages"]]:
            decline(f"season-invalid -- {path}: packages: `{line}` -- one line per package, `<name>=on|off`, each once.")
        found["packages"].append(line)
    for line in block(front, "profiles"):
        member, *pairs = line.split()
        profile: dict = {}
        for pair in pairs:
            key, equal, value = pair.partition("=")
            package = key.removeprefix("package.") if key.startswith("package.") else None
            if (not equal or not value or (package is None and key not in PROFILE_LINE)
                    or (package is not None and not switch.fullmatch(f"{package}={value}")) or key in profile
                    or (package is not None and package in [one.partition("=")[0] for one in profile.get("packages", [])])):
                decline(f"season-invalid -- {path}: profiles: `{line}` -- `<member> <key>=<value> ...`, the keys "
                        f"{', '.join(PROFILE_LINE)} and package.<name> (on|off), each once.")
            if package is None:
                profile[key] = value
            else:
                profile.setdefault("packages", []).append(f"{package}={value}")
        if not pairs or member in found["profiles"]:
            decline(f"season-invalid -- {path}: profiles: `{line}` -- one line per member, said once, with one "
                    "`<key>=<value>` at least.")
        found["profiles"][member] = profile
    return found


def season_opened(root: Path, conductor, name: str, team: dict, asked: dict, packages: list, profiles: dict,
                  text: str | None = None) -> dict:
    """-> the season a `start` opens, in the form `team-started` keeps -- `{launch, season, packages, profiles, work}`:
    SEASON.md's values (`season_written`; `text` read in the file's place) each covered by the start's flag for the same key -- a team's flag its key,
    a member's flag its profile's key, a `--package` its name --, then judged whole by the season's judges: a
    `--harness` without its `--provider` (`grammar-missing`), the limits (`season_of`), the packages and the profiles
    (`profiles_judged`); the packages written as the whole SET (`season_set`). DECLINES, nothing written."""
    written = season_written(root, conductor, name, text)
    limits = {**written["limits"], **{key: asked[key] for key in SEASON_LIMITS if asked.get(key) is not None}}
    launch = {**written["launch"], **{key: asked[key] for key in LAUNCH_FLAGS if asked.get(key) is not None}}
    launch = {key: launch[key] for key in ("harness", "provider", "model", "permissions", "effort") if key in launch}
    if launch.get("harness") is not None and launch.get("provider") is None:   # every wake-up would refuse it
        decline("grammar-missing -- `--harness` runs a caller's command at every wake-up: name the grammar its "
                "output is read in with `--provider <name>` beside it -- the provider whose adapter reads it.")
    season = season_of({key: limits.get(key) for key in SEASON_LIMITS})
    composed_packages = [f"{key}={value}" for key, value in switches_composed(written["packages"], packages).items()]
    composed_profiles: dict = {member: dict(profile) for member, profile in written["profiles"].items()}
    for member, flagged in profiles.items():
        profile = composed_profiles.setdefault(member, {})
        for key, value in flagged.items():
            if key == "packages":
                profile["packages"] = [f"{one}={state}" for one, state in
                                       switches_composed(profile.get("packages") or [], value).items()]
            else:
                if not str(value).strip() or any(one.isspace() for one in str(value)):
                    decline(f"season-invalid -- `--member {member} --{key} {value}`: a profile's value is one word.")
                profile[key] = value
    profiles_judged(root, conductor, team, composed_packages, composed_profiles)
    whole = season_set(root, conductor, switches_composed(composed_packages))
    for profile in composed_profiles.values():
        if profile.get("packages"):
            profile["packages"] = season_set(root, conductor, switches_composed(whole, profile["packages"]))
    return {"launch": launch, "season": season, "packages": whole, "profiles": composed_profiles,
            "work": written["work"]}


def season_said(value) -> str:
    """-> a value as SEASON.md's front matter reads it back: bare when the engine's reader reads it as that very string,
    a JSON string otherwise."""
    text = str(value)
    return text if re.fullmatch(r"[A-Za-z0-9_./@+-]+", text) and not re.fullmatch(r"[-+.0-9eE]+", text) \
        and text.lower() not in ("yes", "no", "on", "off", "true", "false", "null", "y", "n", "~") else json.dumps(text)


def row_named(key: str, row: str) -> str | None:
    """-> the name of a line of the block `key`, by which `values_written` reaches it: an edge of `reports:`,
    `<member>... -> <target>`, by its target -- an edge has no key --; any other line by its first word, up to an
    `=`; None for a blank line."""
    if key == "reports":
        sources, arrow, target = row.partition("->")
        return target.strip() if arrow and target.strip() else None
    return row.split()[0].partition("=")[0] if row.split() else None


def values_written(conductor, text: str, changes: list[tuple], body: str | None = None) -> str:
    """-> the text of a VALUES FILE -- `TEAM.md`, `SEASON.md` -- with the keys `changes` name written: the ONE writer
    of a key of one, `declare`'s and `start`'s (the flags of a season). Every other key, line and token of the front
    matter and the body stay at their bytes; a line written takes the file's own line ending; a text without a front
    matter gains one before it. `changes`, in the order new keys are laid, each `(key, change)`:
    - a text: the line `<key>: <text>`, in the key's place when it stands, at the end of the front matter otherwise;
    - None: the key taken out, its block with it;
    - a list of `(word, form)`: the lines of the block `<key>: |`, each named by `row_named`. `form` receives the
      first line named `word` (None when no line has that name) and returns the line to write: it takes the place of
      ALL the lines named `word`, or is added after the block's last line when none stood; None takes all of them
      out. `word` None adds a line whatever stands; a block left without a line leaves with its key.
    `body`: the text after the front matter, replaced whole. A front matter that never closes raises the engine's
    `Refusal`."""
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != BORDER:        # no front matter: one is laid before the text
        lines = [f"{BORDER}{eol}", f"{BORDER}{eol}", *lines]
    start, end = conductor.sections.front_span([one.rstrip("\r\n") for one in lines])

    def placed_at(key: str, new: list[str]) -> None:
        nonlocal end
        found = conductor.sections.key_span([one.rstrip("\r\n") for one in lines], start, end, key)
        first, last = (end, end) if found is None else found
        lines[first:last] = new
        end += len(new) - (last - first)

    for key, change in changes:
        if change is None or isinstance(change, str):
            placed_at(key, [] if change is None else [f"{key}: {change}{eol}"])
            continue
        found = conductor.sections.key_span([one.rstrip("\r\n") for one in lines], start, end, key)
        head, rows = f"{key}: |{eol}", []
        if found is not None:
            said = lines[found[0]].rstrip("\r\n").split(":", 1)[1].strip()
            head = lines[found[0]] if said == "|" else head
            rows = lines[found[0] + 1:found[1]] if said in ("|", "") else [f"  {said}{eol}"]
        for word, form in change:
            named = [] if word is None else [rank for rank, row in enumerate(rows) if row_named(key, row) == word]
            at = named[0] if named else None
            new = form(None if at is None else rows[at].strip())
            for rank in reversed(named if new is None else named[1:]):   # a key said on several lines: one, or none
                del rows[rank]
            if new is not None and at is None:
                last = max((rank for rank, row in enumerate(rows) if row.strip()), default=-1) + 1
                rows.insert(last, f"  {new}{eol}")
            elif new is not None and new != rows[at].strip():
                rows[at] = f"  {new}{eol}"
        placed_at(key, [head, *rows] if any(row.strip() for row in rows) else [])
    if body is not None:
        if not lines[end].endswith(("\n", "\r")):
            lines[end] += eol
        lines[end + 1:] = [body] if body else []
    return "".join(lines)


def season_changes(asked: dict, packages: list, profiles: dict) -> list[tuple]:
    """-> the changes the season's FLAGS make to SEASON.md, in the form `values_written` takes -- a team's flag its
    key, a `--package` its line of `packages:`, a member's flag its key on the member's line of `profiles:`, the
    member's other tokens at their place --; [] when no flag gives a value. The one writer of these keys, for `start`
    (`season_flagged`) and for `declare --season`."""
    scalars = {key: asked[key] for key in (*LAUNCH_FLAGS, *SEASON_LIMITS) if asked.get(key) is not None}

    def profile_line(old: str | None, member: str, given: dict) -> str:
        tokens = old.split()[1:] if old else []
        pairs = [(key, str(value)) for key, value in given.items() if key != "packages"]
        pairs += [(f"package.{one.partition('=')[0]}", one.partition("=")[2]) for one in given.get("packages") or []]
        for key, value in pairs:
            at = next((rank for rank, token in enumerate(tokens) if token.partition("=")[0] == key), None)
            if at is None:
                tokens.append(f"{key}={value}")
            else:
                tokens[at] = f"{key}={value}"
        return " ".join([member, *tokens])

    changes: list[tuple] = [                           # a limit's number bare, the engine's reader types it; a
        #                                                share of the window `<n>%`, as `--context` says it
        (key, f"{window_share(str(value))}%" if key == "context"
         else str(value) if key in SEASON_LIMITS and re.fullmatch(r"[0-9]+(\.[0-9]+)?", str(value)) else season_said(value))
        for key, value in scalars.items()]
    if packages:
        changes.append(("packages", [(one.partition("=")[0], lambda old, new=one: new) for one in packages]))
    if profiles:
        changes.append(("profiles", [(member, lambda old, member=member, given=given: profile_line(old, member, given))
                                     for member, given in profiles.items()]))
    return changes


def season_flagged(conductor, path: Path, asked: dict, packages: list, profiles: dict) -> bool:
    """Writes into SEASON.md the values the start's FLAGS give, key by key (`season_changes`, `values_written`), every
    other key, line and token and the body at their bytes; the file is born when a flag gives a value and it stands
    not, with those keys alone. -> whether a flag gave a value. Called after every judge and before `team-started`."""
    changes = season_changes(asked, packages, profiles)
    if not changes:
        return False
    text = path.read_bytes().decode("utf-8") if path.is_file() else ""   # its line endings as they are
    placed(path, values_written(conductor, text, changes).encode("utf-8"))
    return True


def documents_rendered(root: Path, conductor, name: str, team: dict, text: str | None = None) -> dict:
    """-> the team's DOCUMENTS as the next start renders them, judged whole and rendered in memory: the lines of
    `TEAM.md` (`team["read"]`, `documents_of`'s) and of `teams/<name>/SEASON.md` -- the file, or `text`, what `declare
    --season` is about to write there --, read by the same code, the season's lines ADDED to the team's: a key said by
    both files receives the documents of both. Each key filled by the values (a hole `{<name>}`), then judged on the
    team's `roles:`; each document rendered ONCE, as `TEAM-<name>-<document's name>.md` -- at the root when the key
    `all` names it, under `roles/` otherwise, for the members who hold one of its keys --: a template's body under its
    conducted head, holes filled (`document_rendered`), a file of the team's directory as it stands. The values: what
    the presets and the documents of both files declare, given by `TEAM.md` then by `SEASON.md`, which wins name by
    name, `{team}` built in. `{documents: [{document, template, origin, roles, members}], lines: [{key, team,
    season}], values: [{name, value, from}], texts: {document: text}, season}` -- `members` None for a document of
    everyone, `[]` for one no key's member holds; `season` the digest of SEASON.md when it says documents or values,
    None otherwise. DECLINES, nothing written: `season-invalid`, `template-unknown`, `template-invalid`,
    `document-unknown`, `value-unknown` (a value SEASON.md gives that nothing declares), `value-missing`,
    `value-undeclared`, `role-unknown` (a key `roles:` does not declare, the line's file named),
    `document-collision` (two documents of one name, or a document named `members`), `document-holes` (a file of the
    team's directory with a hole)."""
    folder = team_root(root, name)
    path = folder / SEASON_DOC
    front = season_front(conductor, path, text)
    season = None
    if front is not None and any(key in front for key in ("template", "documents", "values")):
        season = documents_of(root, conductor, folder, front, path, "season-invalid")
    reads = [("team", team["read"]), *([("season", season)] if season is not None else [])]
    declared: dict[str, dict] = {}
    for _, read in reads:
        for one in read["declared"]:
            declared.setdefault(one["name"], one)
    given = {"team": team["read"]["given"], "season": (season or {}).get("given") or {}}
    for named in given["season"]:
        if named not in declared:
            decline(f"value-unknown -- {path}: values: `{named}` -- what TEAM.md and SEASON.md name declares "
                    f"{', '.join(f'`{one}`' for one in declared) or 'no value'} (`team templates`).")
    values = [{"name": BUILT_IN, "value": name, "from": "built-in"}]
    for one in declared.values():
        source = next((source for source in ("season", "team") if one["name"] in given[source]), None)
        if source is not None:
            values.append({"name": one["name"], "value": given[source][one["name"]], "from": source})
        elif one["default"] is not None:
            values.append({"name": one["name"], "value": one["default"], "from": "default"})
        else:
            decline(f"value-missing -- {one['at']}: `{one['name']}` ({one['description']}) has no default -- give it "
                    "under `values:`, `<name> = <value>`.")
    filled = {one["name"]: one["value"] for one in values}
    lines: dict[str, dict] = {}
    found: dict[str, dict] = {}
    for source, read in reads:
        for key, documents, at in read["lines"]:
            said = holes_filled(key, filled, at)
            if said != ALL and said not in team["roles"]:
                decline(f"role-unknown -- {at}: documents: `{key} {' '.join(documents)}` -- the role `{said}` is not "
                        f"declared by teams/{name}/{TEAM_DOC}'s `roles:` "
                        f"({', '.join(f'`{one}`' for one in team['roles']) or 'no key'}).")
            line = lines.setdefault(said, {"key": said, "team": [], "season": []})
            for one in documents:
                line[source] += [] if one in line[source] else [one]
                entry = found.setdefault(one, {**read["documents"][one], "keys": []})
                entry["keys"] += [] if said in entry["keys"] else [said]
    named: dict[str, str] = {}
    for one, entry in found.items():
        short = one.rsplit("/", 1)[-1]
        if short == SHEET or short in named:
            other = f"the members' sheet `TEAM-{name}-{SHEET}.md`" if short == SHEET else f"`{named[short]}`"
            decline(f"document-collision -- documents: `{one}` and {other} -- both would be rendered as "
                    f"TEAM-{name}-{short}.md: name one of them.")
        named[short] = one
    documents, texts = [], {}
    for one, entry in found.items():
        roles = [] if ALL in entry["keys"] else entry["keys"]
        short = one.rsplit("/", 1)[-1]
        document = f"{ROLES_DIR}/TEAM-{name}-{short}.md" if roles else f"TEAM-{name}-{short}.md"
        if entry["origin"] == "team":
            own = entry["path"].read_text(encoding="utf-8")
            if any(hole.group(1) for hole in HOLE.finditer(own)):
                decline(f"document-holes -- {entry['path']}: a hole `{{<name>}}` -- a file of the team's directory is "
                        "served as it stands: lay a template under .pp/teams/templates/ to fill values.")
            texts[document] = own if not roles or own.lstrip().startswith(BORDER) else f"{BORDER}\n{BORDER}\n{own}"
        else:
            texts[document] = document_rendered(conductor, entry["path"], filled, bool(roles))
        documents.append({"document": document, "template": one, "origin": entry["origin"], "roles": roles,
                          "members": list(dict.fromkeys(member for key in roles for member in team["roles"][key]))
                          if roles else None})
    digest = None
    if season is not None:
        digest = hashlib.sha256(path.read_bytes() if text is None else text.encode("utf-8")).hexdigest()[:12]
    return {"documents": documents, "lines": list(lines.values()), "values": values, "texts": texts, "season": digest}


def document_front(conductor, path: Path, data: bytes | None = None) -> dict | None:
    """-> the front matter of a document of the team's directory, from its bytes about to be written (`data`) or from
    the file; None when it has none the engine can read."""
    try:
        document = conductor.reading.read(path) if data is None else document_planned(conductor, path, data)
    except (conductor.Refusal, OSError):
        return None
    return document.front


def view_of(conductor, directory: Path, name: str, roles: dict, composed: list[dict], member: str | None = None,
            planned: dict[str, bytes | None] | None = None) -> list[dict]:
    """-> the VIEW of a member: the documents of the team's directory it receives, in order, each `{document,
    template, roles, effect, by}` -- the ONE place that decides who receives what. First every `TEAM-<name>-<x>.md` at
    the root, sorted by name, for everyone: `served` by the head of `TEAM-<name>.md` (`by: head`), or `mounted` by the
    engine when its front matter declares `mount:` (`by: engine`); a document written by hand has no filter. Then, for
    `member`, each document of `composed` rendered under `roles/` for a role key the member holds (`roles`: `{key:
    [members]}`), once whatever the keys it shares, in their order: mounted by the member's vector (`by: vector`),
    `mounted` when it declares `mount:` (its laws, its tools, its body), `served` otherwise (its body alone). A
    document of a role the season rendered and that is missing on disk STAYS in the view: the member's next mount
    refuses `mount-missing` naming it, never a vector dropped in silence; a start renders it again. Without
    `member`, the root alone: what every member receives. From a season (`team-started.documents`, the files on
    disk) or from the declaration (the documents in memory and the `planned` bytes, `documents_planned`)."""
    planned = planned or {}
    known = {one["document"]: one for one in composed}
    standing = {one.name for one in team_documents(directory, name) if planned.get(one.name, b"") is not None}
    found = []
    for document in sorted(standing | {one for one, data in planned.items() if data is not None and "/" not in one}):
        front = document_front(conductor, directory / document, planned.get(document)) or {}
        mounts = bool(str(front.get("mount") or "").strip())
        entry = known.get(document) or {}
        found.append({"document": document, "template": entry.get("template"), "roles": [],
                      "effect": "mounted" if mounts else "served", "by": "engine" if mounts else "head"})
    if member is None:
        return found
    held = {key for key, members in roles.items() if member in members}
    for one in composed:
        if not one["roles"] or not held & set(one["roles"]):
            continue
        data = planned.get(one["document"])
        if data is None and one["document"] in planned:
            continue                                   # removed by this start
        front = document_front(conductor, directory / one["document"], data) or {}   # missing: kept, its mount says it
        mounts = bool(str(front.get("mount") or "").strip())
        found.append({"document": one["document"], "template": one["template"], "roles": one["roles"],
                      "effect": "mounted" if mounts else "served", "by": "vector"})
    return found


def season_view(root: Path, conductor, name: str, started: dict | None, member: str) -> list[dict]:
    """-> the view of a member in the season under way (`view_of`): the roles and the documents `team-started` kept,
    the documents its start rendered on disk; [] for a team never started."""
    if not started:
        return []
    return view_of(conductor, team_root(root, name), name, started.get("roles") or {}, started.get("documents") or [],
                   member)


def member_vector(root: Path, conductor, name: str, started: dict | None, member: str) -> str | None:
    """-> the vector of a member, `team-member:<team>/<member>`, when its season's view holds a document of a role;
    None otherwise: a member without one pays no gesture."""
    view = season_view(root, conductor, name, started, member)
    return f"{MEMBER_FAMILY}:{name}/{member}" if any(one["by"] == "vector" for one in view) else None


def documents_kept(rendering: dict) -> list[dict]:
    """-> what `team-started.documents` keeps of the documents a start renders: `[{document, template, origin,
    roles}]`, in their order."""
    return [{key: one[key] for key in ("document", "template", "origin", "roles")} for one in rendering["documents"]]


def documents_planned(root: Path, conductor, name: str, started: dict | None, team: dict,
                      season: str | None = None, directory: bool = True) -> tuple[dict, dict]:
    """-> (the team's documents as rendered in memory, `documents_rendered`'s; the plan of the team's directory:
    `{document: bytes to write, or None to remove}`), judged before any write, the DOCUMENTS whole -- `season`, a text
    of SEASON.md read in the file's place --, then the documents that mount as they WILL stand (`common_judged`), then
    the DIRECTORY (`directory_judged`) -- `directory` False leaves it to the caller, `declaration_read`, which says each
    check apart. A document the last start rendered that no line names any more is removed; one deleted by hand is
    rendered again. `TEAM-<name>.md` itself is written by `documents_written`: its head names what stands then."""
    folder = team_root(root, name)
    rendering = documents_rendered(root, conductor, name, team, season)
    planned: dict[str, bytes | None] = {one: text.encode("utf-8") for one, text in rendering["texts"].items()}
    planned.update({one: None for one in rendered_kept(started) if one not in rendering["texts"]
                    and one != document_name(name) and (folder / one).is_file()})
    common_judged(root, conductor, name, team, planned, rendering["documents"])
    if directory:
        directory_judged(root, name, started, team, planned)
    return rendering, planned


def rendered_kept(started: dict | None) -> dict[str, str]:
    """-> the documents the last start rendered, `{document: digest}`: `TEAM-<name>.md` and each document of a line."""
    return dict((started or {}).get("rendered") or {})


def directory_judged(root: Path, name: str, started: dict | None, team: dict, planned: dict[str, bytes | None]) -> None:
    """Judges the team's DIRECTORY against the plan a start has for it (`documents_planned`), before any write:
    `rendered-edited` for a document the last start rendered whose bytes no longer carry the digest the journal
    kept -- the owner's edit is never written over; `document-collision` for a document to render whose name a
    file the last start did not render holds; `intention-misplaced` for a `TEAM-<name>.md` no start rendered whose
    body is not the intention this start renders -- the owner's word lives in the body of `TEAM.md`, and pp moves
    nothing. DECLINES; what it judges no value of `TEAM.md` nor of `SEASON.md` settles alone."""
    folder = team_root(root, name)
    kept = rendered_kept(started)
    document = document_name(name)
    for one, digest in kept.items():
        target = folder / one
        if target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()[:12] != digest:
            where = (f"the body of {TEAM_DOC}" if one == document else
                     f"{TEAM_DOC}, {SEASON_DOC} or a template")
            decline(f"rendered-edited -- {target}: rendered by the last start, edited since -- a rendered document is "
                    f"never edited: move the words to {where}, or delete it to render it again.")
    for one, data in planned.items():
        if data is not None and one not in kept and (folder / one).exists():
            decline(f"document-collision -- {folder / one}: stands and no start rendered it -- the owner's: "
                    "move it, or name another document.")
    target = folder / document
    if target.is_file() and document not in kept:      # never rendered: nothing but the intention may stand there
        data = target.read_bytes()
        text = data.decode("utf-8")
        body = body_of(text) if text.lstrip().startswith(BORDER) else text.strip()
        if (body and body != team["intention"]
                and hashlib.sha256(data).hexdigest()[:12] not in kept.values()):   # a document renamed with its team
            decline(f"intention-misplaced -- {target}: its body was written by hand -- `team start` renders this "
                    f"document from the team's template: move these words to the body of {team_doc(root, name)}, "
                    "the owner's word, served to every member, then start again.")


def key_stands(conductor, text: str | None, key: str) -> str | None:
    """-> what a values file says under `key`, at its bytes: the key's lines in its front matter, or, for `body`, the
    text after it -- None without the file, the key, or a body."""
    if not text:
        return None
    lines = text.splitlines(keepends=True)
    if lines[0].strip() != BORDER:                     # no front matter: the whole text is the body
        return text if key == "body" else None
    bare = [one.rstrip("\r\n") for one in lines]
    start, end = conductor.sections.front_span(bare)
    if key == "body":
        return "".join(lines[end + 1:]) or None
    found = conductor.sections.key_span(bare, start, end, key)
    return None if found is None else "".join(lines[found[0]:found[1]])


def declare_changes(root: Path, conductor, name: str, asked: dict, born: bool) -> tuple[list[tuple], list[str]]:
    """-> (the changes `declare`'s flags make to a values file, in the form `values_written` takes, the keys they
    name): `description:` JSON-quoted, so that any printable sentence reads back; `template:`; `values:`, a line
    `<name> = <value>` per `--value`; `documents:`, the WHOLE line of each `--document`, named by its key; `agents:`, a
    line `<name> <path>` per `--member`; `reports:`, the line of each `--report`, named by its target (`row_named`);
    `roles:`, the WHOLE line of each `--role`, its key then the members given;
    `root:`; `principals:`, a line per `--principal`; a limit and `schedule:` under their keys. Each line takes the
    place of every line of the block with the same name, so a name written on several lines is left on one. Each
    contrary (`--no-value`, `--no-document`, `--no-member`, `--no-role`, `--no-report` its target) takes out every
    line of that name, nothing where none stands. At a BIRTH (`born`: no `TEAM.md` stands), what the preset gives a
    team no flag describes: its role keys, filled by place (`preset_roles`), its default members at
    `agents/<name>/<member>` without a `--member`, and, for a preset without `form:`, its own `reports:` and its root
    as they stand -- a form's edges and root are never written: every `start` makes them again. Refuses
    `template-unknown`, `template-invalid` at a birth, `team-invalid` for a limit that is no number or a principal that
    is not one name."""
    changes: list[tuple] = []
    out = lambda old: None
    said = lambda line: (lambda old: line)

    def lines_of_block(key: str, set_: list[tuple[str | None, str]], gone: list[str]) -> None:
        if set_ or gone:
            changes.append((key, [*((word, out) for word in gone), *((word, said(line)) for word, line in set_)]))

    if asked["description"] is not None:
        changes.append(("description", json.dumps(asked["description"].strip(), ensure_ascii=False)))
    if asked["template"] is not None:
        changes.append(("template", season_said(asked["template"])))
    lines_of_block("values", [(named, f"{named} = {value}".rstrip()) for named, value in asked["value"]],
                   asked["no-value"])
    lines_of_block("documents", [(line.split()[0], line) for line in asked["document"]], asked["no-document"])
    members, reports, head, keys = list(asked["member"]), [], asked["root"], []
    if born and asked["template"] is not None:
        try:
            template = template_of(conductor, templates_of(root, conductor), asked["template"], "`--template`", "team")
        except Declined as declining:
            refuse(str(declining))
        members = members or [(one, f"agents/{name}/{one}") for one in template["members"]]
        if template["roles"]:                          # the preset's role keys, filled by place at the birth
            values = {**{one["name"]: one["default"] or "" for one in template["values"]}, **dict(asked["value"])}
            try:
                keys = preset_roles(template, formed(template, [member for member, _ in members], head, values))
            except Declined as declining:
                refuse(str(declining))
        if template["form"] is None:                   # no form: the preset's edges and its root are written
            reports = list(template["reports"])
            head = head or (str(template["root"]) if template["root"] else members[0][0] if members else None)
    lines_of_block("agents", [(member, f"{member} {at}") for member, at in members], asked["no-member"])
    lines_of_block("roles", [(line.split()[0], line) for line in keys], [])
    lines_of_block("reports", [(None, edge) for edge in reports], [])
    lines_of_block("reports", list(asked["report"]), asked["no-report"])
    lines_of_block("roles", [(key, " ".join([key, *held])) for key, held in asked["role"]], asked["no-role"])
    if head is not None:
        changes.append(("root", season_said(head)))
    for one in asked["principal"]:
        if not one or len(one.split()) != 1 or one != one.strip():
            refuse(f"team-invalid -- `--principal {one}`: one name, no blank.")
    lines_of_block("principals", [(one, one) for one in asked["principal"]], [])
    for flag, whole in (("budget", False), ("launches", True), ("parallel", True), ("timeout", False)):
        if asked[flag] is not None:
            changes.append((flag, str(numbered(flag, asked[flag], whole))))
    if asked["schedule"] is not None:                  # `off`, `5s`, `2m`, minutes: the judge reads it
        bare = re.fullmatch(r"[A-Za-z0-9]+", asked["schedule"])
        changes.append(("schedule", asked["schedule"] if bare else json.dumps(asked["schedule"])))
    return changes, [key for key, _ in changes]


def declare_verb(rest: list[str]) -> int:
    """`team declare <name> [--season] …`: the ONE verb that WRITES a team's values, the team born or standing --
    `teams/<name>/TEAM.md`, or `teams/<name>/SEASON.md` under `--season` (the season's documents: `--template`,
    `--value`, `--document`, `--body-file`; and the season's flags of `start`, read by `season_declared`, judged by
    `launch_judged` and written by `season_changes`, as `start` writes them; the team must stand, `team-unknown`
    otherwise). Without the file, it is
    written from the flags; with it, the keys the flags name are written and they alone (`declare_changes`,
    `values_written`): every other key, every other line of a block and the body stay at their bytes --
    `--body-file` replaces the body, the owner's word, by the file's text -- `--body-file -` by standard input's. The verb REFUSES a write that makes one of
    `start`'s checks fail when that check passed before it: the declaration is read as it stands, then as it would
    stand with the text to write, by `start`'s own checks in `start`'s order (`declaration_read`: the team, the
    season, the entries, the documents, the directory). A check that passed at the first reading and fails at the second refuses, and nothing is
    written -- at a birth, every refusal does. A check that already failed before the call, or that could not run
    because an earlier one failed, never stops the write: the verb writes, and its verdict names the refusal `start`
    would give -- so a `SEASON.md` written under a `TEAM.md` that is refused is written unjudged. Both files are
    written OFF SEASON alone -- before a first start, or after `team stop` --: in season the verb refuses
    `season-running`, naming `team stop`, nothing written. Written under the team's `tick.lock`, waited
    within `call_lock_wait` (`team-busy` beyond): a tick never reads a file half written, and two calls write one
    after the other; a birth is judged once before the lock, so that a refusal leaves no record of a team that is not.
    No event is written to the journal, no document is rendered, nobody is launched -- what is written applies at
    the next `team start`. Says the file, the keys written (`written`: the keys
    whose text changed in the file, in the order a birth lays them, `body` last -- none for a call that changes
    nothing), `declaration`'s verdict -- `ok`, or the refusal of a check the call did not break -- and the gap to the last start; under `--json` ONE object `{team, file, written, verdict: {ok, refusal}, pending}`.
    Written in the HOUSE (`machine_house()`), whatever instance calls: an agent that borrows the machine writes its
    house's team, never one of its own."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    rest, launched = season_declared(rest)
    asked = asked_declare(rest, launched=bool(launched and (launched["asked"] or launched["packages"]
                                                            or launched["profiles"])))
    season = asked["season"]
    doc = team_doc(root, name)
    path = team_root(root, name) / SEASON_DOC if season else doc
    if season and not doc.is_file():
        refuse(f"team-unknown -- no {doc}: `team declare {name}` writes the team first, then its season.")
    body = None if asked["body-file"] is None else text_handed(asked["body-file"])   # `-`: what a form hands over
    if asked["body-file"] is not None and body is None:
        refuse(f"team-invalid -- `--body-file {Path(asked['body-file'])}`: no such file.")
    if body is not None:
        body = "" if not body.strip() else body if body.endswith("\n") else body + "\n"

    def made() -> tuple[str | None, str | None, list[str], dict]:
        """-> (the file's text, None when it stands not, the text as the flags make it -- None when they leave a
        file that stands not without a key and without a body --, the keys whose text changes, the declaration as
        it would stand, `declaration_read`), judged: a check that passed on the declaration as it stands and fails
        with the text to write refuses -- at a birth, every check that fails --; in season, `season-running`."""
        running = in_season(name, state_of(journal_of(root, name)), f"writing {path.name}")
        if running:
            refuse(running)
        before = path.read_bytes().decode("utf-8") if path.is_file() else None
        born = before is None and not season
        changes, keys = declare_changes(root, conductor, name, asked, born)
        if launched:                                   # the season's flags of `start`: judged, then its one writer
            try:
                stood = values_written(conductor, before or "", changes, body)
            except conductor.Refusal as refusal:
                refuse(f"season-invalid -- {path}: {refusal}")
            launch_judged(root, conductor, name, launched, stood)
            more = season_changes(launched["asked"], launched["packages"], launched["profiles"])
            changes, keys = changes + more, keys + [key for key, _ in more]
        try:
            after = values_written(conductor, before or "", changes, body)
        except conductor.Refusal as refusal:
            refuse(f"{'season' if season else 'team'}-invalid -- {path}: {refusal}")
        stood = declaration_read(root, conductor, name)["checks"] if doc.is_file() else None
        read = declaration_read(root, conductor, name, **{"season" if season else "doc": after})
        broken = next((said for check, said in read["checks"].items() if said is not None
                       and (stood is None or stood.get(check, "") is None)), None)
        if broken is not None:
            refuse(broken)
        if before is None and after == values_written(conductor, "", []):
            after = None                               # contraries alone on a file that stands not: none is born
        moved = [key for key in (*keys, *(["body"] if body is not None else []))
                 if key_stands(conductor, before, key) != key_stands(conductor, after, key)]
        return before, after, moved, read

    if not doc.is_file():                              # a birth: judged before the lock lays the team's records
        made()
    lock = locks(conductor)
    lease = lock.acquire(journal_of(root, name).parent / TICK_LOCK, wait=call_wait(root, conductor))
    if lease is None:
        refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing written, replay once "
               "it has played.")
    try:
        before, after, keys, read = made()
        if after != before:
            placed(path, after.encode("utf-8"))
    finally:
        lock.release(lease)
    shown = str(path.relative_to(root.parent))
    verdict = {"ok": read["refusal"] is None, "refusal": read["refusal"]}
    if asked["json"]:
        print(json.dumps({"team": name, "file": shown, "written": keys, "verdict": verdict,
                          "pending": read["pending"]}, ensure_ascii=False))
        return 0
    started = read["started"]
    gap_said = (f"not started -- start it: team start {name} --message <text>" if started is None else
                f"pending until a new start (#{started.get('id')}): {', '.join(one['key'] for one in read['pending'])}"
                if read["pending"] else f"nothing pending since the start (#{started.get('id')})")
    print(f"pp-team: {shown} " + (f"written · {', '.join(keys)}" if keys else "as it stood · nothing written")
          + (" · verdict ok" if read["refusal"] is None else f" · verdict refused: {read['refusal']}") + f" · {gap_said}")
    return 0


def new_retired(rest: list[str]) -> int:
    """`new`: the verb of before -- refuses `verb-retired`, naming the verb that took its place."""
    refuse("verb-retired -- `new` is gone: `team declare <name> --template <directory>/<name> "
           "[--member <name> <path>]...` writes a team's values, the team born or standing -- then `team start <name>`.")


# --- the declaration read: its text, its verdict, its gap to the start ---------------------------

PENDING = ("agents", "reports", "root", "principals", "ceremonies", "entries", "limits", "schedule", "roles",
           "template", "values")
SEASON_PENDING = ("launch", "season", "packages", "profiles", "work")   # the season's, from SEASON.md


def kept_at_start(started: dict, key: str):
    """-> what `team-started` kept of one key of the front matter, in the journal's form -- a ceremony by
    its declaration line, the preset by its name (None without one), the team's values as applied (`{name:
    value}`)."""
    if key == "ceremonies":
        return [one.get("text") for one in started.get("ceremonies") or []]
    if key == "template":
        return (started.get("template") or {}).get("template")
    if key == "schedule":
        return schedule_seconds(started)
    empty = {"agents": {}, "reports": [], "principals": [], "entries": {}, "limits": {}, "roles": {}, "values": {}}
    return started.get(key, empty.get(key))


def gap(started: dict, team: dict) -> list[dict]:
    """-> what a new `start` would change: `{key, started, declared}` per key `team-started` kept that the team as
    it would play (`team_played`) now says otherwise, in `PENDING`'s order -- the edges, the root and the daily a form
    makes among them, the preset by its name, the team's values as applied. The body, the owner's word, is never
    pending: pp serves it to the team's runs as soon as it changes."""
    found = []
    for key in PENDING:
        now_said = ([one["text"] for one in team["ceremonies"]] if key == "ceremonies" else
                    (team["template"] or {}).get("template") if key == "template" else
                    values_kept(team) if key == "values" else team[key])
        then = kept_at_start(started, key)
        if then != now_said:
            found.append({"key": key, "started": then, "declared": now_said})
    return found


def template_kept(team: dict) -> dict | None:
    """-> what `team-started.template` keeps of the preset a team names: `{template, origin}` -- None without one:
    the key is not written."""
    named = team["template"]
    return None if named is None else {"template": named["template"], "origin": named["origin"]}


def values_kept(team: dict) -> dict[str, str]:
    """-> what `team-started.values` keeps of the values `TEAM.md` applies to its preset and its documents:
    `{name: value}`."""
    return {one["name"]: one["value"] for one in team["applied"]}


def season_gap(root: Path, conductor, started: dict, opened: dict) -> list[dict]:
    """-> what a new `start` without a flag would change of the season: `{key, started, declared}` per key of
    `SEASON_PENDING` that SEASON.md now opens otherwise than `team-started` kept it -- the kept side read as it plays:
    the launch's keys a launch passes (`LAUNCH_FLAGS`), the packages and each profile's as the whole set
    `season_played` reads a journal's lists with, a journal of before included."""
    launch = {key: value for key, value in (started.get("launch") or {}).items()
              if key in LAUNCH_FLAGS and value is not None}
    profiles = {member: {**profile, **({"packages": season_played(root, conductor, started, member)}
                                       if profile.get("packages") else {})}
                for member, profile in (started.get("profiles") or {}).items()}
    kept = {"launch": launch, "season": started.get("season") or {},
            "packages": season_played(root, conductor, started), "profiles": profiles,
            "work": started.get("work")}
    return [{"key": key, "started": kept[key], "declared": opened[key]} for key in SEASON_PENDING
            if kept[key] != opened[key]]


def documents_gap(name: str, started: dict, rendering: dict) -> dict | None:
    """-> the entry `documents` of `pending` -- `{key, started, declared}`, each side the documents (`documents_kept`)
    and the digest of each, `TEAM-<name>.md` apart -- when the documents the next start renders differ from those the
    last start rendered; None when they are the same."""
    head = document_name(name)
    then = {"documents": started.get("documents") or [],
            "rendered": {one: digest for one, digest in (started.get("rendered") or {}).items() if one != head}}
    now = {"documents": documents_kept(rendering),
           "rendered": {one: hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
                        for one, text in rendering["texts"].items()}}
    return None if then == now else {"key": "documents", "started": then, "declared": now}


def declared_face(root: Path, conductor, name: str, team: dict, rendering: dict | None = None,
                  planned: dict[str, bytes | None] | None = None, opened: dict | None = None) -> dict:
    """-> the team as it plays (`team_played`), what the next start writes: the members and
    their paths in the order declared -- each with `born` (an instance stands at its path), the `packages` a season
    without `--package` gives it (`season_set`: the packages the team requires on, every other pin off), born or not,
    and its `description` as the members' sheet says it (`description_of`) --,
    the root, the edges, the principals, the limits, the schedule, the ceremonies' lines -- `TEAM.md`'s own, else
    what its preset's form and defaults make --, the entries, the work, the season a start without a flag opens
    (`season`: `{launch, limits, packages, profiles, work}`, None when SEASON.md is refused), the role keys in the
    order declared (`[{role, members}]`, each member's keys on its line), the lines of `documents:` by key, the
    team's and the season's (`documents`: `[{key, team, season}]`, None when the documents are refused), each
    member's VIEW as the next start renders it (`view_of`: `[{member, roles, documents}]`), the preset named
    (`{template, origin, values: [{name, value, from}]}`, `from` `team` or `default`; None without one) and the values
    the documents apply (`values`, `[{name, value, from}]`) -- the owner's word and the digest left to the text."""
    silent = [{"name": name, "on": state == "on"} for name, state in set_of(season_set(root, conductor, {})).items()]
    template = template_description(root, conductor)
    return {"agents": [{"member": member, "path": path,
                        "born": conductor.instance.is_instance(agent_meta(root, path)), "packages": silent,
                        "description": description_of(root, conductor, path, template),
                        "roles": [key for key, members in team["roles"].items() if member in members]}
                       for member, path in team["agents"].items()],
            "root": team["root"], "reports": team["reports"], "principals": team["principals"],
            "limits": team["limits"], "schedule": team["schedule"],
            "ceremonies": [one["text"] for one in team["ceremonies"]], "entries": team["entries"],
            "work": (opened or {}).get("work"),
            "season": None if opened is None else {"launch": opened["launch"], "limits": opened["season"],
                                                   "packages": opened["packages"], "profiles": opened["profiles"],
                                                   "work": opened["work"]},
            "roles": [{"role": key, "members": members} for key, members in team["roles"].items()],
            "documents": None if rendering is None else rendering["lines"],
            "views": [{"member": member, "roles": [key for key, members in team["roles"].items() if member in members],
                       "documents": view_of(conductor, team_root(root, name), name, team["roles"],
                                            (rendering or {}).get("documents") or [], member, planned)}
                      for member in team["agents"]],
            "template": team["template"],
            "values": None if rendering is None else rendering["values"]}


def packages_at(root: Path, conductor, path: str, run: str | None = None, season: dict | None = None) -> dict:
    """-> `{born, packages [{name, on}]}` for the agent at `path`: born, the packages its instance pins beyond its
    base as `run` plays them -- the run's own switches over its SETTINGS, their dependents with them, read on the
    engine's faces as `agent status` reads them, the run's slot set into the play for the reading and taken out
    after; without a run, the `season`'s set (`season_played`: what its next opening gets, every pin named) --; not
    born yet, the house's pins beyond its base under the season's set."""
    instance, persistence, meta = conductor.instance, conductor.persistence, agent_meta(root, path)
    season = dict(season or {})
    if not instance.is_instance(meta):
        base = instance.base_of(root)
        return {"born": False, "packages": [{"name": name, "on": season.get(name, "on") == "on"}
                                            for name in instance.pins(root) if name != base]}
    slot = persistence.slot_of(meta, run) if run else None
    instance.play_switches(meta, persistence.switches_of(slot) if slot is not None and slot.is_file() else season)
    try:
        off = instance.switched_off(meta)
    finally:
        instance.play_switches(meta, {})
    base = instance.base_of(meta)
    return {"born": True, "packages": [{"name": name, "on": name not in off}
                                       for name in instance.pins(meta) if name != base]}


def declaration_read(root: Path, conductor, name: str, doc: str | None = None, season: str | None = None) -> dict:
    """-> a team's declaration as it stands -- `doc` and `season`: a text of `TEAM.md`, of `SEASON.md`, read in the
    file's place, what `declare` is about to write --, judged by `start`'s own checks in `start`'s order, the two
    files TOGETHER, and never refused: `{team` (as it plays, None when refused), `checks` (each check that RAN, in
    order, `{check: its refusal, None when it passes}`: `team` the team as it plays; then, the team read, `season`
    the season a start without a flag opens, `entries` an entry nothing resolves, `documents` the documents of both files and those that mount; then, the
    documents passed, `directory` the team's directory against the plan -- a check that could not run, the one
    before it failing, is absent), `refusal` (the first refusal of `checks`, the one `start` would write; None
    without one), `started` (the last `team-started`, None before one), `rendering`, `planned` and `opened` (the
    documents rendered in memory, the plan of the directory and the season; None when not judged), `pending` (the gap
    to the last start, key by key: `gap`, `documents_gap`, `season_gap`; `[]` before a start, None when `TEAM.md` is
    refused), `changed}` (the file differs from the one the last start read). Nothing written, no lock, never a
    tick: the ONE reading `declaration` says and `declare` judges its write by."""
    team, checks = None, {}

    def ran(check: str, judge):
        """-> what `judge` returns, None when it declines; `checks[check]` its refusal, None when it passes."""
        try:
            found = judge()
        except Declined as declining:
            checks[check] = str(declining)
            return None
        checks[check] = None
        return found

    team = ran("team", lambda: team_played(root, conductor, name, doc))
    state = state_of(journal_of(root, name))
    started = state["started"]
    rendering, planned, opened = None, None, None
    if team is not None:
        opened = ran("season", lambda: season_opened(root, conductor, name, team, {}, [], {}, season))
        ran("entries", lambda: entries_judged(root, conductor, name, team))
        found = ran("documents", lambda: documents_planned(root, conductor, name, started, team, season,
                                                           directory=False))
        if found is not None:
            rendering, planned = found
            ran("directory", lambda: directory_judged(root, name, started, team, planned))
    pending = None if team is None else ([] if started is None else gap(started, team))
    if pending is not None and started is not None and rendering is not None:
        moved = documents_gap(name, started, rendering)
        pending += [moved] if moved else []
    if pending is not None and started is not None and opened is not None:
        pending += season_gap(root, conductor, started, opened)
    return {"team": team, "refusal": next((said for said in checks.values() if said is not None), None),
            "checks": checks, "started": started, "stopped": state["stopped"], "rendering": rendering, "planned": planned,
            "opened": opened,
            "pending": pending, "changed": bool(started) and changed_since_start(root, name, started)}


def candidate_read(asked: dict) -> str | None:
    """-> the CANDIDATE text `--text-file` names -- `-` the standard input, else a file --, None without the flag.
    Refuses `team-invalid` for a path that is no file."""
    if asked["text-file"] is None:
        return None
    if asked["text-file"] == "-":
        return sys.stdin.read()
    own = Path(asked["text-file"])
    if not own.is_file():
        refuse(f"team-invalid -- `--text-file {own}`: no such file.")
    return own.read_text(encoding="utf-8")


def declaration_verb(rest: list[str]) -> int:
    """`team declaration <name> [--json] [[--season] --text-file <path>|-]`: the team's declaration READ -- `TEAM.md`
    whole, start's own judge's verdict (`ok`, or the refusal `start` would write: said, never refused) and its gap to
    the last start, key by key (`declaration_read`). Under `--text-file`, a CANDIDATE text -- `-`: standard input --
    read in the place of `TEAM.md`, or of `SEASON.md` under `--season`, and said as if it were written: its text, its
    verdict, `declared` and each member's view; `--season` without it is the usage. Nothing written, no lock, never a
    tick. Read in the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, DECLARATION_FLAGS)
    as_json = asked["json"]
    if asked["season"] and asked["text-file"] is None:
        refuse(USAGE)
    candidate = candidate_read(asked)
    path = team_doc(root, name)
    if not path.is_file():
        refuse(f"team-unknown -- no {path}: the owner declares the team there.")
    data = candidate.encode("utf-8") if candidate is not None and not asked["season"] else path.read_bytes()
    read = declaration_read(root, conductor, name, **({} if candidate is None else
                                                      {"season" if asked["season"] else "doc": candidate}))
    team, refusal, started, rendering = read["team"], read["refusal"], read["started"], read["rendering"]
    planned, opened, pending, changed = read["planned"], read["opened"], read["pending"], read["changed"]
    shown_path = str(path.relative_to(root.parent))
    text = data.decode("utf-8")
    season = team_root(root, name) / SEASON_DOC
    season_face = None
    if season.is_file() or (candidate is not None and asked["season"]):
        said = candidate.encode("utf-8") if candidate is not None and asked["season"] else season.read_bytes()
        season_face = {"path": str(season.relative_to(root.parent)), "text": said.decode("utf-8"),
                       "digest": hashlib.sha256(said).hexdigest()[:12]}
    if as_json:
        print(json.dumps({"team": name, "name": team_name(root, conductor, name),
                          "description": None if team is None else team["description"], "path": shown_path, "text": text,
                          "digest": hashlib.sha256(data).hexdigest()[:12],
                          "verdict": {"ok": refusal is None, "refusal": refusal},
                          "started": None if started is None else {"at": started.get("at"), "id": started.get("id"),
                                                                    "digest": started.get("digest"),
                                                                    "state": "stopped" if read["stopped"] else "running"},
                          "changed": changed, "pending": pending, "season": season_face,
                          "declared": None if team is None else declared_face(root, conductor, name, team, rendering,
                                                                               planned, opened)},
                         ensure_ascii=False))
        return 0
    print(f"pp-team: {shown_path}")
    print(harmless(text.rstrip("\n")))
    if season_face is not None:
        print(f"pp-team: {season_face['path']}")
        print(harmless(season_face["text"].rstrip("\n")))
    print("verdict ok" if refusal is None else f"verdict refused: {refusal}")
    named = (team or {}).get("template")
    if named:
        print(f"template {named['template']} ({named['origin']})"
              + "".join(f" · {one['name']} = {one['value']}" for one in named["values"]))
    for one in (rendering or {}).get("lines") or []:
        print(f"documents {one['key']}: " + " ".join([*one["team"], *one["season"]]))
    for key, members in (team or {}).get("roles", {}).items():
        print(f"role {key}: {', '.join(members) if members else 'no member'}")
    if started is None:
        print("not started")
    elif pending:
        print(f"pending until a new start (#{started.get('id')}):")
        for one in pending:
            print(f"  {one['key']}: {json.dumps(one['started'], ensure_ascii=False)} -> "
                  f"{json.dumps(one['declared'], ensure_ascii=False)}")
    elif changed:
        print(f"changed since the start (#{started.get('id')}): the body alone, served already")
    elif team is not None:
        print(f"unchanged since the start (#{started.get('id')})")
    return 0


# --- the journal: the team's one truth ----------------------------------------------------

def lines_of(path: Path) -> list[dict]:
    """-> the record's lines, oldest first. A LAST line that does not parse is a writer still
    writing it and is skipped; one anywhere else is a hand in the file and refuses."""
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8").splitlines()
    found = []
    for number, line in enumerate(raw, 1):
        if not line.strip():
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            if number == len(raw):
                continue
            refuse(f"line {number} of {path.name} is not a record -- this script is the "
                   "only writer, the file is not for hand edits.")
    return found


PLAIN = ("started", "tasks", "done", "intents", "launched", "stops", "limits", "deferred",
         "delegations", "schedule", "cost", "budget_spent", "seen", "rung", "ends", "fails", "last",
         "seasons", "paused", "routed", "flow", "deleting", "recurrences", "silences",
         "context", "total", "halts", "quotas", "stopped", "since")   # the JSON-ready parts


def packed(state: dict) -> dict:
    """-> the replayed state as JSON data, for ONE `snapshot` event: sets and tuples become
    lists, tuple keys and integer keys become rows (JSON would turn an integer key into its
    digits, and a reader asking by the id would find nothing). The messages of RESOLVED
    tasks are PRUNED unless the owner's box still reads them (a post to the owner, a post
    returned to the owner): no reader replays them -- the inboxes filter resolved tasks out, a reply cites
    an open task's post, a post the tick returned to a member is read at that member's next head alone -- and the
    pruning is what makes a long journal's state light."""
    owner = str((state["started"] or {}).get("owner"))
    resolved = {task_id for task_id, one in state["tasks"].items() if one.get("state") == "resolved"}
    kept = {key: value for key, value in state["messages"].items()
            if value.get("task") not in resolved or value.get("to") == owner or state["returned_to"].get(key) == owner}
    return {**{key: state[key] for key in PLAIN},
            "messages": {str(key): value for key, value in kept.items()},
            "returned_to": [[key, to] for key, to in state["returned_to"].items()],
            "delivered": sorted(state["delivered"]),
            "ended": sorted(state["ended"]),
            "failures": [[agent, task, count] for (agent, task), count in state["failures"].items()],
            "terminals": sorted([agent, task] for agent, task in state["terminals"]),
            "runs": [[member, carrier, run] for member, held in state["runs"].items() for carrier, run in held.items()],
            "returned": sorted(state["returned"]),
            "killed": sorted(state["killed"]),
            "kills": sorted([agent, task] for agent, task in state["kills"]),
            "launches_spent": sorted(one for one in state["launches_spent"] if one is not None),
            "reset": dict(state["reset"]),
            "resumed": dict(state["resumed"]),
            "fell": sorted([agent, task] for agent, task in state["fell"]),
            "standing": sorted([agent, task] for agent, task in state["standing"]),
            "debts": [[key, value] for key, value in state["debts"].items()],
            "health": {member: dict(one) for member, one in state["health"].items()},
            "house": sorted(state["house"]),
            "read": sorted(state["read"])}


def unpacked(data: dict) -> dict:
    """-> the state a `snapshot` event kept, back in its working types; a key a snapshot of an earlier
    version did not keep takes its empty value."""
    empty = {"fails": [], "routed": {}, "flow": {}, "deleting": False, "recurrences": {}, "silences": [], "halts": [],
             "quotas": {}, "stopped": None, "since": None,
             "context": {}}
    standing = data.get("standing") or []
    if isinstance(standing, dict):                   # a snapshot of before (team 1.4.7): member -> the task it stood on
        standing = list(standing.items())
    return {**{key: data.get(key, empty.get(key)) for key in PLAIN},
            "limits": {RETIRED_LIMITS.get(key, key): value                # a snapshot of before (team 0.39.0): its
                       for key, value in (data.get("limits") or {}).items()},   # bounds counted wake-ups
            "messages": {int(key): value for key, value in (data.get("messages") or {}).items()},
            "returned_to": {int(key): to for key, to in (data.get("returned_to") or [])},
            "total": float(data["total"] if data.get("total") is not None else data.get("cost") or 0.0),   # a
            #                                     snapshot of before (team 1.18): the cost of its season alone
            "delivered": set(data.get("delivered") or []),
            "ended": set(data.get("ended") or []),
            "failures": {(agent, task): count for agent, task, count in (data.get("failures") or [])},
            "terminals": {(agent, task) for agent, task in (data.get("terminals") or [])},
            "runs": runs_unpacked(data.get("runs") or [], data),
            "returned": set(data.get("returned") or []),
            "killed": set(data.get("killed") or []),
            "kills": {(agent, task) for agent, task in (data.get("kills") or [])},
            "launches_spent": set(data.get("launches_spent") or data.get("wakes_spent") or []),   # `wakes_spent`: a snapshot of before
            "reset": dict(data.get("reset") or {}),
            "resumed": dict(data.get("resumed") or {}),
            "fell": {(agent, task) for agent, task in (data.get("fell") or [])},
            "standing": {(agent, task) for agent, task in standing},
            "debts": ({int(key): value for key, value in data["debts"]} if "debts" in data
                      else debts_rebuilt(data)),
            "health": {member: dict(one) for member, one in (data.get("health") or {}).items()},
            "house": set(data.get("house") or []),
            "read": set(data.get("read") or [])}


def debts_rebuilt(data: dict) -> dict:
    """-> the debts a snapshot of team 0.32.2 or before did not keep, rebuilt from the messages it kept: a
    `do` or an `ask` to a member on an open task owes until an answer of its member cites it."""
    messages = {int(key): value for key, value in (data.get("messages") or {}).items()}
    agents = ((data.get("started") or {}).get("agents") or {})
    open_tasks = {key for key, one in (data.get("tasks") or {}).items() if one.get("state") == "open"}
    debts: dict = {}
    state = {"messages": {}, "started": data.get("started")}
    for key in sorted(messages):
        one = messages[key]
        state["messages"][key] = one
        if one.get("verb") in ("do", "ask") and one.get("to") in agents and one.get("task") in open_tasks:
            debts[key] = None
        cited = cited_of(state, one)
        if cited is not None and debts.get(cited, "x") is None and messages[cited].get("to") == one.get("from"):
            debts[cited] = key
    return debts


def runs_unpacked(rows: list, data: dict) -> dict:
    """-> the runs each member holds by CARRIER, from a snapshot's rows `[member, carrier, run]`; a row
    `[member, run]` of team 1.0.0 goes to the carrier of the task of the member's last intent."""
    found: dict = {}
    for row in rows:
        if len(row) == 3:
            found.setdefault(row[0], {})[row[1]] = row[2]
            continue
        last = max((one for one in (data.get("intents") or {}).values() if one.get("agent") == row[0]),
                   key=lambda one: int(one.get("id") or 0), default=None)
        if last is not None:
            found.setdefault(row[0], {})[carrier_of(data, last.get("task"))] = row[1]
    return found


def carrier_of(state: dict, task: str | None) -> str | None:
    """-> the CARRIER of a task, what a member's run is kept by: an occurrence's recurrence, a ring's
    ceremony, any other task itself."""
    held = (state.get("tasks") or {}).get(task) or {}
    return held.get("recurrence") or held.get("ceremony") or task


def run_held(state: dict, member: str, task: str | None) -> str | None:
    """-> the run the member holds for the task's carrier, None before its first wake-up there."""
    return (state["runs"].get(member) or {}).get(carrier_of(state, task))


def carrier_name(state: dict, team: str, carrier: str) -> str:
    """-> the name a run of the carrier carries: a recurrence's name, else `<team> R<n>`; a task's name, else
    `<team> T<n>`; a ceremony's; cut at the run name's bound."""
    recurrence = state["recurrences"].get(carrier)
    task = state["tasks"].get(carrier)
    if recurrence is not None:
        text = recurrence.get("name") or f"{team} {carrier}"
    elif task is not None:
        text = task.get("name") or f"{team} {carrier}"
    else:
        text = carrier
    return " ".join(str(text).split())[:RUN_NAME_CHARS].strip()


def tailed(path: Path) -> list[dict]:
    """-> the journal's events FROM its last `snapshot` line on (found by a text scan and
    verified by a parse), or all of them when none stands -- the read a state needs: the
    lines before the snapshot are never parsed."""
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8")
    at = raw.rfind('"kind": "snapshot"')
    while at >= 0:
        start = raw.rfind("\n", 0, at) + 1
        end = raw.find("\n", at)
        try:
            candidate = json.loads(raw[start:] if end < 0 else raw[start:end])
        except ValueError:
            candidate = None
        if isinstance(candidate, dict) and candidate.get("kind") == "snapshot":
            found = []
            lines = raw[start:].splitlines()
            for number, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                try:
                    found.append(json.loads(line))
                except ValueError:
                    if number == len(lines):
                        continue
                    refuse(f"line {number} of the journal's tail is not a record -- this script is "
                           "the only writer, the file is not for hand edits.")
            return found
        at = raw.rfind('"kind": "snapshot"', 0, at)   # the match was a text's: scan on
    return lines_of(path)


def state_of(path: Path) -> dict:
    """-> the team's state, read from the last snapshot on: what every judge and every
    status reads -- `lines_of` whole stays the historians' (`log`, `watch`, `of_task`)."""
    return replay(tailed(path))


def cited_of(state: dict, one: dict) -> int | None:
    """-> the id of the message a post ANSWERS, or None: a `re` cites it, a principal's `reply` too; in a journal
    written before team 0.33.0 a member's `reply` cites the ask it answered, and its `done` or `escalate` to the
    member that delegated answers that member's last `do` to it on the task."""
    verb = one.get("verb")
    if verb == "re":
        return one.get("re")
    if verb == "reply":
        return one.get("reply")
    if verb in ("done", "escalate") and is_member(state, one.get("to")):
        dos = [key for key, message in state["messages"].items()
               if message.get("verb") == "do" and message.get("from") == one.get("to")
               and message.get("to") == one.get("from") and message.get("task") == one.get("task") and key < one["id"]]
        return max(dos) if dos else None
    return None


def opening_of(state: dict, task: str) -> int | None:
    """-> the task's OPENING message: the first `do` its author posted to its member -- what the member that
    holds the task answers to close it. None when the journal holds none (a ceremony rung before team 0.33.0)."""
    held = state["tasks"].get(task) or {}
    return next((key for key in held.get("messages") or []
                 if (state["messages"].get(key) or {}).get("verb") == "do"
                 and state["messages"][key].get("from") == held.get("from")
                 and state["messages"][key].get("to") == held.get("to")), None)


def owes(state: dict, key) -> bool:
    """-> whether the message's debt stands: a `do` or an `ask` delivered to a member, no answer of its yet."""
    return state["debts"].get(key, "x") is None


def is_notice(state: dict, one: dict) -> bool:
    """-> whether a post is a NOTICE of the team to a principal: a `notice`, or an `escalate` to a principal in a journal
    written before team 0.36.0."""
    return one.get("verb") == "notice" or (one.get("verb") == "escalate" and not is_member(state, one.get("to")))


def notice_about(state: dict, one: dict) -> str | None:
    """-> the member a notice concerns -- its `about`, or the member that wrote an `escalate` to a principal before team
    0.36.0 --; None for a guard's notice."""
    if one.get("verb") == "notice":
        return one.get("about")
    return one.get("from") if is_member(state, one.get("from")) else None


def principal_answered(state: dict) -> set:
    """-> the ids a principal's answer cites: its `re`, or its `reply` written before team 0.36.0."""
    return {cited_of(state, one) for one in state["messages"].values()
            if one.get("verb") in ("re", "reply") and is_principal(state, one.get("from"))} - {None}


def worded(state: dict, one: dict) -> dict:
    """-> a post as the faces say it, in the words of the debt: a member's `done`, `reply` or `escalate` to a member,
    and a principal's `reply`, written before team 0.36.0, said `re` to the message it answers (`cited_of`; a `done` to a
    principal answers the task's opening) with `was` its verb; an `escalate` to a principal said as the team's `notice`,
    `about` the member that wrote it; a `note` written before team 0.47.0 said `info`; any other post as it is."""
    verb = one.get("verb")
    if verb == "note":                                           # the principal's note until team 0.47.0: an info
        return {**{key: value for key, value in one.items() if key != "verb"}, "verb": "info", "was": verb}
    if verb not in RETIRED_VERBS:
        return one
    rest = {key: value for key, value in one.items() if key not in ("verb", "reply")}
    if verb == "escalate" and not is_member(state, one.get("to")):
        about = one.get("from") if is_member(state, one.get("from")) else None
        return {**rest, "verb": "notice", "from": (state["started"] or {}).get("team") or one.get("team"),
                **({"about": about} if about else {}), "was": verb}
    cited = cited_of(state, one)
    if cited is None and verb == "done":
        cited = opening_of(state, one.get("task"))
    return {**rest, "verb": "re", "re": cited, "was": verb}


def said_so_far() -> dict:
    """-> what a reader of the journal keeps of the events it read, to say the next ones (`read_on`)."""
    return {"started": None, "messages": {}, "tasks": {}}


def read_on(context: dict, one: dict) -> dict | None:
    """-> one event as `log` and `watch` say it, `context` -- what the events before it said -- kept up to date: a post
    in the words of the debt (`worded`), None for an event no version writes any more (`DEAD`), any other as it is."""
    kind = one.get("kind")
    if kind == "team-started":
        context["started"] = one
    elif kind == "task":
        context["tasks"][one["task"]] = {"from": one.get("from"), "to": one.get("to"), "messages": []}
    elif kind == "post":
        held = context["tasks"].get(one.get("task"))
        if held is not None and one["id"] not in context["messages"]:
            held["messages"].append(one["id"])
        context["messages"][one["id"]] = one
        return worded(context, one)
    return None if kind in DEAD else one


def replay(events: list[dict]) -> dict:
    """-> the team's STATE, computed from its journal alone: the last `team-started`, the tasks
    with their state and their messages, every message by its id, the messages delivered (the
    ones an intent carried, the ones returned, a stop to an agent whose wake-up was killed), the
    intents and their launches, ends, failures and kills, the terminals, the delegations, the
    runs each member holds, ONE per CARRIER of its tasks (`carrier_of`) -- the last that answered there, readable or not --, the stops posted
    to each agent, the results, the owner's cursor (`inbox-seen`), the members `team reset` took
    their run from (`run-reset`, the member's run dropped), the (member, task) whose terminal a final
    failure wrote, the starts counted (`seasons` -- each a SEASON: its limits TEAM.md's under the season's own,
    the cost, `budget-spent` and `launches-spent` afresh, the members' runs kept), the bounds `team budget` raised (`budget-raised`: the limits raised, `budget_spent`
    lifted), and the last `resumed` of each task -- `team resume` opens the task again, sets its
    members' failures to zero, drops the terminals its final failures wrote and lifts `launches-spent`:
    the task's counters count from there. A journal written by team 0.39.0 counted wake-ups: its
    `team-started.limits` and `season` keys `launches` and `budget-launches` are read as `launches` and
    `budget-launches`, its `wakes-spent` as `launches-spent`, its `budget-raised {wakes}` as `{launches}`;
    nothing is written under those names again. The run a failed launch leaves: `wake-failed {state}`, read at
    agent's face, says whether it STANDS (relaunched while its retries last) or is parked; a final failure stands
    nobody. A `stop` posted to an agent whose run stands on the task is not delivered at once: it rides the head
    of one more launch (`dues`). A ceremony's task rung at hand keeps who rang it (`by`, from
    its `ceremony-due`). The team is PAUSED from a `paused` to its `unpaused` (`paused` `{by, at, id}`,
    else None). Each task keeps its `text` and its `last` event `{id, kind, at}` -- the last
    event that belongs to it (`task_of`). The DEBTS: each `do` or `ask` posted to a member on an open
    task opens one (`None`), the first answer of that member that cites it settles it (the answer's id;
    `closed` when the task resolves); the delegations are the `do`s between members, and a member is
    TERMINAL on a task once its last `do` there is answered -- by it, or in its place after a final failure
    (`delegation` and `terminal` events of a journal written before team 0.33.0 read the same). A `launch-missing` counts no failure: nothing was launched. A
    post to a principal is delivered at its writing: the principal's box reads it, and it is
    never returned. A task stops by its `stopped` event, whatever holds it (a `stop` post stops
    it too: a journal written before the event). The HEALTH of each member (`health`, the failure detector
    ◇P): `falls` its final failures in a row since it last answered -- on a task not stopped, a `budget-share`
    apart -- and `at` the hour of the last, the member SUSPECTED while `falls` stands; a launch the HOUSE refused
    (`wake-failed {house: true}`, never final) counts no failure and no fall (`house`: its tags); a wake-up that ends
    answered makes a suspected member REPENT (`falls` back to 0, its failures counted afresh, `repents` one
    more: one silent retry more); `team resume --task` ends the suspicion of the task's members, a season ends
    every suspicion. A `silence {agent, task, passages}` the tick wrote (row 115) is a fall too (`cause: silence`),
    lifted by a routed act of the member alone -- never by a launch that ends saying nothing. The tick's
    answer in a suspected member's place takes the message it answers out of the member's inbox (`delivered`): under
    `suspected`, a message a `wake-intent` of the member carried; under `returned`, a message none carried, which is
    RETURNED to its author as well (`returned`, `returned_to`). A `suspected` alone, as a journal of before writes it
    on both, reads as a message carried. The RECURRENCES the owner posted
    (`recurrence {R<n>}`) keep the periods they sounded -- by an occurrence, a task that carries `recurrence` and
    `period`, or by a `recurrence-skipped` --, their last occurrence, their stop (`recurrence-stopped`) and their
    suspension (`recurrence-paused`, `paused {by, at, id}`, lifted by `recurrence-resumed`, which replaces `since` and
    counts its first slot one later); a `recurrence-changed` replaces its `when` and its `since`, its context limit
    (`context`) or its text, the periods sounded kept: a period is its date, counted once; a recurrence born of a task (`recurrence {task}`) has that task
    for its last occurrence; a `run-renewed` detaches the run it names from its carrier -- its recurrence, its
    ceremony or its task --: the member's next wake-up there opens a new one. A task keeps the context limit of its
    birth (`context`, None without one). Each member's CONTEXT is the `context` of its last `wake-ended` (`None` without one, or for a journal written
    before team 0.54.0). The season under way ENDS at its `season-stopped` (`stopped` `{by, at, id, tasks,
    recurrences}`, None in season or before a start; its pause ends with it); the next `team-started` opens the next
    one, and its `since` -- written when it follows a stop -- is the hour nothing before is caught up from: each
    recurrence counts from it, as after its resume, and an `every` ceremony owes no period whose hour is not after it."""
    state: dict = {"started": None, "tasks": {}, "messages": {}, "delivered": set(),
                   "intents": {}, "launched": {}, "ended": set(), "failures": {}, "terminals": set(),
                   "delegations": [], "runs": {}, "done": {}, "returned": set(),
                   "schedule": True,
                   "limits": {}, "cost": 0.0, "total": 0.0, "budget_spent": False, "deferred": [], "returned_to": {},
                   "killed": set(), "kills": set(), "stops": {}, "seen": 0, "read": set(),
                   "launches_spent": set(), "rung": {}, "ends": [], "fails": [], "last": None, "reset": {},
                   "resumed": {}, "fell": set(), "seasons": 0, "paused": None, "debts": {}, "health": {},
                   "routed": {}, "flow": {}, "standing": set(), "house": set(),
                   "deleting": False, "recurrences": {},
                   "silences": [], "context": {}, "halts": [], "quotas": {}, "stopped": None, "since": None}
    floor = 0
    rung_by: dict = {}
    snap = next((one for one in reversed(events) if one.get("kind") == "snapshot"), None)
    if snap is not None:                           # the replay restarts at the LAST snapshot
        state = unpacked(snap.get("state") or {})
        floor = int(snap.get("upto") or 0)
    for one in events:
        kind = one.get("kind")
        if kind == "snapshot" or int(one.get("id") or 0) <= floor:
            continue
        state["last"] = {"id": one.get("id"), "kind": kind, "at": one.get("at")}
        if kind == "team-started":                        # a season: the counts afresh, the runs kept
            before = state["started"] or {}
            state["quotas"] = {member: held for member, held in state["quotas"].items()   # the old provider's limit
                               if launch_kept(before, member)["provider"] == launch_kept(one, member)["provider"]}
            state["started"] = one
            state["seasons"] = int(state.get("seasons") or 0) + 1
            state["schedule"] = True
            state["limits"] = {RETIRED_LIMITS.get(key, key): value for key, value in {
                **dict(one.get("limits") or {}),
                **{key: value for key, value in (one.get("season") or {}).items() if value is not None}}.items()}
            state["cost"], state["budget_spent"] = 0.0, False
            state["launches_spent"] = set()
            state["health"] = {}                          # nobody suspected at a season's start
            state["halts"] = []                           # nobody held by its failures in a row
            state["stopped"], state["since"] = None, one.get("since")
            if one.get("since"):                          # after a stop: nothing passed off season is caught up
                for recurrence in state["recurrences"].values():
                    recurrence["since"], recurrence["first"] = one["since"], 1
        elif kind == "season-stopped":                    # `team stop <team>`: the season ends, its pause with it
            state["stopped"] = {key: one.get(key) for key in ("by", "at", "id", "tasks", "recurrences")}
            state["paused"] = None
        elif kind == "task":
            state["tasks"][one["task"]] = {"id": one["task"], "from": one.get("from"), "to": one.get("to"),
                                           "text": one.get("text"), "state": "open", "messages": [],
                                           "ceremony": one.get("ceremony"), "period": one.get("period"),
                                           "name": one.get("name"), "at": one.get("at"), "ended": None,
                                           "recurrence": one.get("recurrence"), "context": one.get("context"),
                                           "vectors": list(one.get("vectors") or [])}
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:                    # an occurrence: its period sounded, none for one launched now
                if one.get("period") is not None:
                    recurrence["sounded"].append(one.get("period"))
                recurrence["last"] = one["task"]
            if one.get("ceremony") and rung_by.get((one["ceremony"], one.get("period"))):
                state["tasks"][one["task"]]["by"] = rung_by[(one["ceremony"], one.get("period"))]
        elif kind == "post":
            state["messages"][one["id"]] = one
            task = state["tasks"].get(one.get("task"))
            if task is not None:
                task["messages"].append(one["id"])
            verb, to = one.get("verb"), one.get("to")
            if verb == "do" and is_member(state, to):
                if is_member(state, one.get("from")):     # a delegation is the do itself
                    state["delegations"].append({"id": one["id"], "from": one["from"], "to": to,
                                                 "task": one.get("task")})
                state["terminals"].discard((to, one.get("task")))   # a new round for that member
            if verb in ("do", "ask") and is_member(state, to) and task is not None and task["state"] == "open":
                state["debts"][one["id"]] = None          # one debt, open until its first answer
            cited = cited_of(state, one)
            if cited is not None and owes(state, cited) and state["messages"][cited].get("to") == one.get("from"):
                state["debts"][cited] = one["id"]         # the first answer settles it
                if state["messages"][cited].get("verb") == "do":
                    state["terminals"].add((one.get("from"), one.get("task")))
                if one.get("verb") == "stop" and task["state"] == "open":
                    task["state"], task["ended"] = "stopped", one.get("at")
            if one.get("suspected") and cited is not None:  # answered in a suspected member's place: delivered
                state["delivered"].add(cited)
            if one.get("returned") and one.get("by") == "tick" and cited is not None:   # answered before any launch
                state["delivered"].add(cited)              # delivered it: out of the member's inbox, and back to
                state["returned"].add(cited)               # its author
                state["returned_to"][cited] = one.get("to")
            if one.get("verb") == "stop":                 # delivered at once -- but to a run STANDING on the task:
                state["stops"].setdefault(one.get("to"), []).append(one["id"])   # the head of one more launch
                if (one.get("to"), one.get("task")) not in state["standing"]:
                    state["delivered"].add(one["id"])
            elif is_principal(state, one.get("to")):      # delivered at once: the principal's box reads it
                state["delivered"].add(one["id"])
            if is_member(state, one.get("from")) and one.get("by") != "tick":   # an act of a member suspected by
                health = state["health"].get(one.get("from")) or {}        # silence lifts it: it repents (row 115)
                if health.get("falls") and health.get("cause") == "silence":
                    health.update({"falls": 0, "repents": int(health.get("repents") or 0) + 1})
        elif kind == "silence":                           # the member's silence fell: a fall of the detector (row 115)
            state["silences"].append(one)
            health = state["health"].setdefault(one.get("agent"), {"falls": 0, "repents": 0})
            health.update({"falls": int(health.get("falls") or 0) + 1, "at": one.get("at"), "cause": "silence",
                           "id": one.get("id")})
        elif kind == "stopped":
            task = state["tasks"].get(one.get("task"))
            if task is not None and task["state"] == "open":
                task["state"], task["ended"] = "stopped", one.get("at")
        elif kind == "wake-intent":
            state["intents"][one["tag"]] = one
            state["delivered"].update(one.get("messages") or [])
        elif kind == "wake-launched":
            state["launched"][one["tag"]] = one
        elif kind == "wake-routed" or kind == "wake-refused":   # an act read at the flow: the rank reached
            state["routed"][one["tag"]] = max(int(state["routed"].get(one["tag"]) or 0), int(one.get("line") or 0))
        elif kind == "wake-ended":
            state["ended"].add(one["tag"])
            state["ends"].append(one)
            charged(state, one)
            intent = state["intents"].get(one["tag"])
            if intent is not None:                          # an exchange played: the provider's limit is over
                state["quotas"].pop(intent["agent"], None)
            if intent is not None:                          # the context its exchange left, null unmeasured
                state["context"][intent["agent"]] = one.get("context")
            if intent is not None and one.get("run"):       # the run that answered is the carrier's
                state["runs"].setdefault(intent["agent"], {})[carrier_of(state, intent.get("task"))] = one["run"]
                if one.get("flow") is not None:
                    state["flow"][str(one["run"])] = int(one["flow"])
                pair = (intent["agent"], intent.get("task"))
                if one.get("state") == "standing" and not closed_before(state, intent):   # the run waits for a
                    state["standing"].add(pair)             # production: continued, nothing delivered to it until
                else:                                       # it parks (`continued_run`) -- parked, or standing
                    state["standing"].discard(pair)         # after its ONE continuation on a closed task
            health = state["health"].get((intent or {}).get("agent")) or {}
            if health.get("falls") and health.get("cause") != "silence":   # a fallen member answered: it repents;
                #                                              a silence is lifted by an act of its alone (row 115)
                health.update({"falls": 0, "repents": int(health.get("repents") or 0) + 1})
                for slot in [slot for slot in state["failures"] if slot[0] == intent["agent"]]:
                    del state["failures"][slot]
        elif kind == "quota-reached":                     # the provider's limit: the member held, nothing failed
            state["ended"].add(one["tag"])
            charged(state, one)
            intent = state["intents"].get(one["tag"])
            if intent is not None:
                state["quotas"][intent["agent"]] = {"until": one.get("until"), "said": one.get("said"),
                                                    "at": one.get("at"), "task": intent.get("task"), "tag": one["tag"]}
                state["delivered"].difference_update(intent.get("messages") or [])   # read at its next launch
                if one.get("run"):                          # the run that met the limit stays the carrier's
                    state["runs"].setdefault(intent["agent"], {})[carrier_of(state, intent.get("task"))] = one["run"]
                    if one.get("flow") is not None:
                        state["flow"][str(one["run"])] = int(one["flow"])
        elif kind == "wake-halted":                       # the same failure in a row: launched there no more
            state["halts"].append(one)
        elif kind == "wake-failed":
            state["ended"].add(one["tag"])
            state["fails"].append(one)
            charged(state, one)
            intent = state["intents"].get(one["tag"])
            if intent is not None and one.get("run"):       # a launch that failed: its run stays the carrier's
                state["runs"].setdefault(intent["agent"], {})[carrier_of(state, intent.get("task"))] = one["run"]
            launched_run = (state["launched"].get(one["tag"]) or {}).get("run") or one.get("run")
            if launched_run and one.get("flow") is not None:   # the flow of a dead launch is read: never again
                state["flow"][str(launched_run)] = int(one["flow"])
            if one.get("house"):                            # the house refused the launch: the member did nothing
                state["house"].add(one["tag"])
            if intent is not None:
                slot = (intent["agent"], intent["task"])
                if one.get("reason") != "launch-missing" and not one.get("house"):   # the agent's retries count what it did
                    state["failures"][slot] = state["failures"].get(slot, 0) + 1
                if (one.get("state") == "standing" and not one.get("final")
                        and not closed_before(state, intent)):                # the run stands: relaunched
                    state["standing"].add(slot)
                elif one.get("state") is not None or one.get("final"):      # parked, or its retries spent
                    state["standing"].discard(slot)
                if one.get("final") and (state["tasks"].get(intent["task"]) or {}).get("state") != "stopped":
                    state["fell"].add(slot)                     # its terminal is the failure's
                    state["terminals"].add(slot)
                    if not one.get("house"):                    # the house refused: the member did nothing
                        health = state["health"].setdefault(intent["agent"], {"falls": 0, "repents": 0})   # SUSPECTED
                        health.update({"falls": int(health.get("falls") or 0) + 1, "at": one.get("at"), "cause": "fall",
                                       "id": one.get("id")})
                for mid in intent.get("messages") or []:    # a retry sends them again; a final failure keeps them
                    if one.get("final"):
                        state["delivered"].add(mid)
                    else:
                        state["delivered"].discard(mid)
        elif kind == "wake-killed":
            state["ended"].add(one["tag"])
            state["killed"].add(one["tag"])
            state["kills"].add((one["agent"], one.get("task")))
        elif kind == "terminal":
            state["terminals"].add((one["agent"], one["task"]))
        elif kind == "delegation":                        # written before team 0.33.0: its do counts
            pass
        elif kind == "done":
            state["done"][one["task"]] = one
            task = state["tasks"].get(one["task"])
            if task is not None:
                task["state"], task["ended"] = "resolved", one.get("at")
                state["terminals"].add((task["to"], one["task"]))
            for key, settled in list(state["debts"].items()):
                if settled is None and (state["messages"].get(key) or {}).get("task") == one["task"]:
                    state["debts"][key] = "closed"        # the root's answer settles every debt of the task
        elif kind == "returned":
            state["returned"].add(one["message"])
            state["returned_to"][one["message"]] = one.get("to")
            state["delivered"].add(one["message"])
        elif kind == "schedule-off":
            state["schedule"] = False
        elif kind == "budget-spent":
            state["budget_spent"] = True
        elif kind == "budget-raised":                     # `team budget` raised a bound: spent no more
            if one.get("budget") is not None:
                state["limits"]["budget"] = float(one["budget"])
            raised = one.get("launches", one.get("wakes"))     # `wakes`: the field of before (team 0.39.0)
            if raised is not None:
                state["limits"]["budget-launches"] = int(raised)
            state["budget_spent"] = False
        elif kind in ("launches-spent", "wakes-spent"):      # `wakes-spent`: the kind of before (team 0.39.0)
            state["launches_spent"].add(one.get("task"))
        elif kind == "ceremony-due":
            state["rung"].setdefault(str(one.get("ceremony")), []).append(str(one.get("period")))
            if one.get("by"):                             # a ring at hand: its task, written next, keeps who rang
                rung_by[(one.get("ceremony"), one.get("period"))] = one["by"]
        elif kind == "deferred":
            state["deferred"].append(one)
        elif kind == "inbox-seen":
            state["seen"] = int(one.get("upto") or 0)
        elif kind == "inbox-read":                        # one message marked read by the owner (team 1.12.1)
            state["read"].add(int(one.get("message") or 0))
        elif kind == "run-reset":                         # `team reset` forgot one run of the member
            held = state["runs"].get(one.get("member")) or {}
            forgot = [carrier for carrier, run in held.items() if run == one.get("run")]
            for carrier in forgot:
                del held[carrier]
            for pair in [pair for pair in state["standing"]   # the pairs of the run forgotten
                         if pair[0] == one.get("member") and carrier_of(state, pair[1]) in forgot]:
                state["standing"].discard(pair)
            state["reset"][one.get("member")] = one["id"]
        elif kind == "paused":                            # `team pause`: nobody woken, nothing rung
            state["paused"] = {"by": one.get("by"), "at": one.get("at"), "id": one.get("id")}
        elif kind == "unpaused":                          # `team resume` without a task: the team back
            state["paused"] = None
        elif kind == "quota-lifted":                      # `team resume --quota`: the owner lifts the provider's limit
            for member in one.get("members") or []:
                state["quotas"].pop(member, None)
        elif kind == "deleting":                          # `team delete --yes`: the team lives no more
            state["deleting"] = True
        elif kind == "recurrence":                        # `team post --every`: a task that comes back
            state["recurrences"][one["recurrence"]] = {
                "id": one["recurrence"], "from": one.get("from"), "to": one.get("to"), "text": one.get("text"),
                "name": one.get("name"), "when": one.get("when"), "since": one.get("since"), "at": one.get("at"),
                "context": one.get("context"), "description": one.get("description"), "first": 0, "stopped": None,
                "paused": None, "sounded": [],
                "task": one.get("task"),
                "last": one.get("task")}                  # a recurrence born of a task: its origin its last occurrence
        elif kind == "recurrence-skipped":                # the occurrence before still open: the period sounded
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:
                recurrence["sounded"].append(one.get("period"))
        elif kind == "recurrence-stopped":                # `team stop --recurrence`
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:
                recurrence["stopped"] = {"by": one.get("by"), "at": one.get("at"), "id": one.get("id")}
        elif kind == "recurrence-paused":                 # `team pause --recurrence`: it sounds nothing until resumed
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:
                recurrence["paused"] = {"by": one.get("by"), "at": one.get("at"), "id": one.get("id")}
        elif kind == "recurrence-resumed":                # `team resume --recurrence`: from its resume, nothing caught up
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None:
                recurrence["paused"], recurrence["since"], recurrence["first"] = None, one.get("since"), 1
        elif kind == "recurrence-changed":                # `team recurrence`: what it carries replaced, the periods kept
            recurrence = state["recurrences"].get(one.get("recurrence"))
            if recurrence is not None and "when" in one:       # a duration a change gives: its first slot one later
                recurrence["when"], recurrence["since"] = one.get("when"), one.get("since")
                recurrence["first"] = 1
            if recurrence is not None and "context" in one:
                recurrence["context"] = one["context"]
            if recurrence is not None and "text" in one:       # the occurrences to come open with it
                recurrence["text"] = one["text"]
            if recurrence is not None and "description" in one:
                recurrence["description"] = one["description"]
        elif kind == "run-renewed":                       # the run detached from its carrier: a new one opens there
            held = state["runs"].get(one.get("member")) or {}
            carrier = one.get("recurrence") or carrier_of(state, one.get("task"))
            if held.get(carrier) == one.get("run"):
                del held[carrier]
        elif kind == "resumed":                           # `team resume` took the task back
            task = state["tasks"].get(one.get("task"))
            if task is not None and task["state"] == "stopped":
                task["state"], task["ended"] = "open", None
            state["resumed"][one.get("task")] = one["id"]
            state["launches_spent"].discard(one.get("task"))
            for slot in [slot for slot in state["failures"] if slot[1] == one.get("task")]:
                del state["failures"][slot]
            for slot in [slot for slot in state["fell"] if slot[1] == one.get("task")]:
                state["fell"].discard(slot)
                state["terminals"].discard(slot)
            for member in members_of(state, one.get("task")):   # the owner trusts them again
                if (state["health"].get(member) or {}).get("falls"):
                    state["health"][member]["falls"] = 0
                if member in state["quotas"] and state["quotas"][member].get("until") is None:
                    del state["quotas"][member]           # a limit without an hour: lifted by the owner
            state["halts"] = [held for held in state["halts"] if held.get("task") != one.get("task")]
        task = state["tasks"].get(task_of(state, one))
        if task is not None:
            task["last"] = {"id": one.get("id"), "kind": kind, "at": one.get("at")}
    return state


def charged(state: dict, one: dict) -> None:
    """Adds the cost a wake-up's end carries to the team's season and to the task of its intent (`cost` of the
    task, kept with the task through every season and every snapshot)."""
    cost = one.get("cost")
    if not isinstance(cost, (int, float)) or isinstance(cost, bool):
        return
    state["cost"] += float(cost)
    state["total"] = float(state.get("total") or 0.0) + float(cost)   # every season's, never counted afresh
    task = state["tasks"].get((state["intents"].get(one.get("tag")) or {}).get("task"))
    if task is not None:
        task["cost"] = float(task.get("cost") or 0.0) + float(cost)


def task_of(state: dict, one: dict) -> str | None:
    """-> the task an event belongs to, as `log --task` keeps it (`of_task`): the task it names, or
    the task of the intent its `tag` names -- a launch, an end, a failure of a wake-up."""
    if one.get("task"):
        return one["task"]
    return (state["intents"].get(one.get("tag")) or {}).get("task") if one.get("tag") else None


def members_of(state: dict, task: str | None) -> list[str]:
    """-> the members a task concerns: the one that holds it, those a message on it was posted to, those woken
    on it."""
    held = state["tasks"].get(task) or {}
    found = [held.get("to")] + [one.get("to") for one in state["messages"].values() if one.get("task") == task]
    found += [one.get("agent") for one in state["intents"].values() if one.get("task") == task]
    return [one for one in dict.fromkeys(found) if is_member(state, one)]


def open_intents(state: dict) -> list[dict]:
    """-> the intents without an end: the wake-ups under way, in the journal's order."""
    return [one for tag, one in state["intents"].items() if tag not in state["ended"]]


def unproven(root: Path, conductor, state: dict) -> set[str]:
    """-> the tags of the intents without an end whose launch NOBODY holds: launched (`wake-launched`) and its wake
    lock free -- its launcher ended and the next tick reads its end, or it died with its process space and no tick
    came since. A wake lock is what the house SEES of a launch, from any process space; a pid is not. An intent not
    launched yet is the tick's that writes it: never in."""
    lock = locks(conductor)
    gone = set()
    for one in open_intents(state):
        launch = state["launched"].get(one["tag"]) or {}
        if launch.get("run") and not lock.held(launch_of(conductor, agent_meta(root, path_of_intent(state, one)),
                                                         str(launch["run"]))):
            gone.add(str(one["tag"]))
    return gone


def faced(root: Path, conductor, name: str) -> dict:
    """-> the state a FACE reads: the journal replayed, and `gone` -- the launches nobody holds (`unproven`), read
    now, never replayed nor packed. The faces say `running` of a PROVEN launch alone (`played`); the tick judges
    on the journal, and never reads `gone`."""
    state = state_of(journal_of(root, name))
    state["gone"] = unproven(root, conductor, state) if state["started"] is not None else set()
    return state


def played(state: dict) -> list[dict]:
    """-> the wake-ups a face says are under way: the intents without an end, less the ones `faced` proved gone."""
    gone = state.get("gone") or ()
    return [one for one in open_intents(state) if str(one["tag"]) not in gone]


def reserved_of(state: dict) -> float:
    """-> the money the wake-ups under way may still spend: the allowances of the intents without an
    end since the last `team-started`."""
    since = int((state["started"] or {}).get("id") or 0)
    return round(sum(float(one.get("allowance") or 0) for one in open_intents(state)
                     if int(one.get("id") or 0) > since), 6)


def share_of(state: dict) -> dict | None:
    """-> the team's budget as the faces say it, `{cap, spent, reserved, left}`: `left` the rest no wake-up
    holds, below 0 when the last ones went past; None without `budget:`."""
    cap = state["limits"].get("budget")
    if cap is None:
        return None
    reserved = reserved_of(state)
    return {"cap": float(cap), "spent": round(state["cost"], 6), "reserved": reserved,
            "left": round(float(cap) - state["cost"] - reserved, 6)}


def allowance_of(state: dict, started: dict) -> float | None:
    """-> the money a wake-up launched now may spend: its PART of the team's rest, min((budget - the cost
    kept) / k, the rest no wake-up under way holds) -- k the wake-ups that may play together, min(`parallel`,
    the members), the members without `parallel:` --, down to the micro-dollar; None without `budget:`."""
    share = share_of(state)
    if share is None:
        return None
    members = max(1, len(started.get("agents") or {}))
    parallel = state["limits"].get("parallel")
    k = members if parallel is None else max(1, min(int(parallel), members))
    part = min((share["cap"] - share["spent"]) / k, share["left"])
    return math.floor(part * 1e6) / 1e6


def measured(root: Path, conductor, started: dict) -> bool:
    """-> whether the adapter of the launches' grammar declares a scope for the cost it reads (`COST`):
    the provider `team start` kept, else the one the house is wired with -- what `agent start` holds a
    run's cap by. False when none is known or the adapter refuses."""
    grammar = (started.get("launch") or {}).get("provider")
    if grammar is None:
        wired = conductor.install.wired_providers(root.parent)
        grammar = wired[0] if len(wired) == 1 else None
    if grammar is None:
        return False
    try:
        return getattr(conductor.adapters.load(str(grammar), root), "COST", None) in ("session", "launch")
    except conductor.Refusal:
        return False


def inbox(state: dict, agent: str) -> list[dict]:
    """-> the messages to `agent` that no event delivered, on tasks not resolved, in order."""
    return [one for one in state["messages"].values()
            if one.get("to") == agent and one["id"] not in state["delivered"]
            and (state["tasks"].get(one.get("task")) or {}).get("state") != "resolved"]


def is_open(state: dict, task) -> bool:
    return (state["tasks"].get(task) or {}).get("state") == "open"


def busy(state: dict, member: str) -> bool:
    """-> whether a wake-up of the member is under way: an intent of its without an end, whatever
    its task -- a member plays one wake-up at a time, in its one run."""
    return any(one["agent"] == member and tag not in state["ended"] for tag, one in state["intents"].items())


def owed_by(state: dict, member: str) -> list[int]:
    """-> the debts the member owes, in order: each `do` or `ask` delivered to it on an open task that no
    answer of its settled yet."""
    return [key for key, one in sorted(state["messages"].items())
            if one.get("to") == member and owes(state, key) and key in state["delivered"]
            and is_open(state, one.get("task"))]


def waits_for(state: dict) -> dict[str, set[str]]:
    """-> the WAIT-FOR graph of the team, on every open task: a -> b while a `do` or an `ask` of the member a
    to the member b still owes its answer, and a -> p while an `ask` of a to the principal p, or a notice of the team to p
    about a, has no answer of p that cites it -- a notice of a silence holds no wait: the try waits for no answer
    (row 115). A principal waits on nobody."""
    answered = principal_answered(state)
    edges: dict[str, set[str]] = {}
    for key, one in state["messages"].items():
        to = one.get("to")
        notice = is_notice(state, one) and one.get("cause") != "silence"   # a silence notice holds no wait (row 115)
        frm = notice_about(state, one) if notice else one.get("from")
        if not is_member(state, frm) or not is_open(state, one.get("task")):
            continue
        if (owes(state, key) and is_member(state, to)) or (
                (one.get("verb") == "ask" or notice) and is_principal(state, to) and key not in answered):
            edges.setdefault(str(frm), set()).add(str(to))
    return edges


def receives(state: dict, member: str) -> bool:
    """-> whether the member has something to receive: a message the ordinary rule would deliver it now;
    the members' `info`s alone are nothing to receive (`quiet`)."""
    return any(loud(state, box) for task, box in dues(state, member))


def deadlocked(state: dict) -> set[str]:
    """-> the DEADLOCKED set of the team (Chandy, Misra, Haas 1983, the communication model): the greatest set of
    IDLE members -- no wake-up under way, nothing to receive -- whose every wait stays in the set; a principal is
    in none, since it may always post. Computed from the idle members, dropping any whose wait leaves the set,
    until nothing moves."""
    edges = waits_for(state)
    members = list((state["started"] or {}).get("agents") or {})
    found = {one for one in members if not busy(state, one) and not receives(state, one)}
    moved = True
    while moved:
        moved = False
        for one in list(found):
            if any(other not in found for other in edges.get(one, ())):
                found.discard(one)
                moved = True
    return found


def reached(edges: dict[str, set[str]], member: str) -> set[str]:
    """-> every member and principal the member reaches by its waits."""
    seen, stack = set(), list(edges.get(member, ()))
    while stack:
        one = stack.pop()
        if one not in seen:
            seen.add(one)
            stack.extend(edges.get(one, ()))
    return seen


def at_bottom(state: dict, member: str) -> bool:
    """-> whether the member stands at the BOTTOM of the deadlocked set: in it, and every member it reaches by its
    waits reaches it back -- a sink (it waits for nobody) or a knot. Its answer unblocks those that wait on it."""
    if member not in deadlocked(state):
        return False
    edges = waits_for(state)
    return all(member in reached(edges, one) for one in reached(edges, member))


def principal_opening(state: dict, key: int) -> bool:
    """-> whether the debt is the opening a principal posted: never answered in its member's place."""
    message = state["messages"].get(key) or {}
    return key == opening_of(state, message.get("task")) and not is_member(state, message.get("from"))


def silence_since(state: dict, member: str, task: str) -> int:
    """-> the journal id the member's SILENCE on the task counts from: the latest of its last routed act on the task
    (a post of its, `info` included, never one the tick wrote in its place), the task's `resumed`, the season's
    `team-started`, and its last `silence` fall there."""
    acts = [key for key, one in state["messages"].items()
            if one.get("from") == member and one.get("task") == task and one.get("by") != "tick"]
    falls = [int(one.get("id") or 0) for one in state["silences"] if one.get("agent") == member and one.get("task") == task]
    return max(acts + falls + [state["resumed"].get(task, 0), int((state["started"] or {}).get("id") or 0)])


def stood(state: dict, member: str, task: str) -> bool:
    """-> whether the member's run for the task's CARRIER stands: its last launch there left it waiting for a
    production, and nothing parked it since."""
    carrier = carrier_of(state, task)
    return any(one == member and carrier_of(state, other) == carrier for one, other in state["standing"])


def passages_of(state: dict, member: str, task: str) -> list[dict]:
    """-> the member's PASSAGES on the task, in the journal's order (row 115): each WAKE-UP of its there and its
    CONTINUATIONS, until the run parks -- `{id, end}`, the id of the wake-up's intent and the id of the `wake-ended`
    that parked the run, None while it stands, plays, or died. A launch is a continuation when it resumes a run
    that stood at its intent: read on the earlier end of the member's launches on the task's carrier, as the replay
    holds it -- a `wake-ended {state: standing}`, or a `wake-failed` that left the run standing with a retry; the
    one continuation on a closed task (`closed_before`) parks the run whatever its end says: the first launch on
    the carrier's next task is a wake-up --, never on a field of the intent, so that a journal of before reads the
    same."""
    carrier = carrier_of(state, task)
    ends = {one.get("tag"): one for one in state["ends"]}
    fails = {one.get("tag"): one for one in state["fails"]}
    found: list[dict] = []
    standing = False
    for tag, intent in state["intents"].items():
        if intent.get("agent") != member or carrier_of(state, intent.get("task")) != carrier:
            continue
        if not (standing and intent.get("run") and found):       # a WAKE-UP: it opens a passage
            found.append({"id": int(intent.get("id") or 0), "task": intent.get("task"), "end": None})
        if tag in ends:
            standing = ends[tag].get("state") == "standing" and not closed_before(state, intent)
            found[-1]["end"] = None if standing else int(ends[tag].get("id") or 0)
        elif tag in fails:
            standing = (fails[tag].get("state") == "standing" and not fails[tag].get("final")
                        and not closed_before(state, intent))
    return [one for one in found if one["task"] == task]


def owed_at(state: dict, member: str, task: str, at: int) -> bool:
    """-> whether the member owed an answer on the task at the journal id `at`: a `do` or an `ask` a launch of its
    had carried by then, that no answer settled before."""
    carried = {key for one in state["intents"].values()
               if one.get("agent") == member and int(one.get("id") or 0) <= at for key in one.get("messages") or []}
    for key in carried:
        message = state["messages"].get(key) or {}
        settled = state["debts"].get(key, "x")
        if (message.get("to") == member and message.get("task") == task and settled != "x"
                and (settled is None or not isinstance(settled, int) or settled > at)):
            return True
    return False


def awaited_principal(state: dict, member: str, task: str, at: int) -> bool:
    """-> whether the member waited for a PRINCIPAL's answer on the task at the journal id `at`: a question of its
    own to a principal, asked before, that no answer of a principal cited by then."""
    answered: dict = {}
    for key, one in state["messages"].items():
        cited = cited_of(state, one) if one.get("verb") in ("re", "reply") and is_principal(state, one.get("from")) else None
        if cited is not None:
            answered[cited] = min(answered.get(cited, key), key)
    return any(one.get("verb") == "ask" and one.get("from") == member and one.get("task") == task
               and is_principal(state, one.get("to")) and key < at and answered.get(key, at) >= at
               for key, one in state["messages"].items())


def silence_of(state: dict, member: str, task: str, after: int = 0) -> int:
    """-> the member's SILENCE on the task (row 115): its silent PASSAGES there since `silence_since` -- and since
    `after`, the fall a suspect's passages count from. A passage is silent when its run PARKED, the member owed an
    answer on the task at its wake-up, said no routed act since -- an act moves `silence_since` -- and waited for no
    principal's answer at the park. A CONTINUATION counts for nothing: a run that stands is continued while it does
    not park. Read from the journal alone: nothing is written to count."""
    since = max(silence_since(state, member, task), after)
    return sum(1 for one in passages_of(state, member, task)
               if one["id"] > since and one["end"] is not None and owed_at(state, member, task, one["id"])
               and not awaited_principal(state, member, task, one["end"]))


def beat_of(state: dict, member: str, task: str, box: list[dict]) -> int | None:
    """-> the BEAT a WAKE-UP keeps on its intent and says at its head: the exchanges left to the member to say an act
    on the task, this one counted -- `silence:` less its silent passages in a row there, never under 1; 1 for a
    suspected member, whose silent try is one more fall; None for a member that owes nothing on the task once its
    box is delivered: nothing is asked of it."""
    owing = (any(state["messages"][key].get("task") == task for key in owed_by(state, member))
             or any(owes(state, one["id"]) and one.get("to") == member for one in box))
    if not owing:
        return None
    if suspicion_of(state, member) is not None:
        return 1
    return max(1, silence_limit(state, member) - silence_of(state, member, task))


def closed_before(state: dict, intent: dict) -> bool:
    """-> whether a launch was a CONTINUATION ON A CLOSED TASK: its intent written after the `done` of its task. A
    run that stands on a task its root closed gets ONE such launch, under `CLOSED_HEAD`, to end its passage; when
    it stands after it, the replay holds it as parked -- nothing continues it any more, a message alone launches
    it again (s.1409: twelve old runs continued without end on 2026-11-08, an open task starved). Nothing is
    written for it: the journal's `wake-ended {state: standing}` stays what the house said of the run."""
    done = state["done"].get(intent.get("task"))
    return done is not None and int(intent.get("id") or 0) > int(done.get("id") or 0)


def standing_of(state: dict, member: str) -> list[str]:
    """-> the tasks the member's runs STAND on and are continued on, one (member, task) each: open or resolved -- a
    run standing on a closed task is continued ONCE (`closed_before`); a stopped one is launched once more by its
    stop (`dues`) --, in the tasks' order, from the one after the task of its last launch: each in its turn."""
    order = list(state["tasks"])
    tasks = [task for task in order if (member, task) in state["standing"]
             and state["tasks"][task].get("state") in ("open", "resolved")]
    last = next((one.get("task") for one in reversed(state["intents"].values()) if one.get("agent") == member), None)
    after = order.index(last) if last in order else -1
    return [task for task in tasks if order.index(task) > after] + [task for task in tasks if order.index(task) <= after]


def continued_run(state: dict, member: str, task: str) -> bool:
    """-> whether the member's run for the task's CARRIER stands and is still continued: a pair (member, task') of
    that carrier stands, its run held, its task open or resolved, its launches not spent -- what `woken_on` asks of
    a continuation. ONE run is one passage: nothing but a stop is delivered to it until it parks -- the messages
    due wait, and open the launch after its park, a turn of their own (s.1377). A run that is continued no more
    -- its task's `launches:` spent, or a first launch dead before any run was kept -- takes its messages, so that
    nothing starves."""
    carrier = carrier_of(state, task)
    return any(one == member and carrier_of(state, other) == carrier and other not in state["launches_spent"]
               and (state["tasks"].get(other) or {}).get("state") in ("open", "resolved")
               and run_held(state, member, other) is not None
               for one, other in state["standing"])


def silent_tasks(state: dict, member: str) -> list[str]:
    """-> the tasks the member's silence is judged on: each task it owes an answer on. A run that stands is not
    judged for itself: it is continued while it does not park; a closed task has no silence."""
    return list(dict.fromkeys(str(state["messages"][key].get("task")) for key in owed_by(state, member)))


def silence_limit(state: dict, member: str) -> int:
    """-> the silent passages in a row that make the member suspected: its profile's `--silence`, else the season's
    or `TEAM.md`'s `silence:` (`state["limits"]`), else DEFAULT_SILENCE."""
    profile = profile_of(state["started"] or {}, member)
    if profile.get("silence") is not None:
        return int(profile["silence"])
    return int(state["limits"].get("silence") or DEFAULT_SILENCE)


def relance_of(state: dict, member: str) -> tuple[str, str | None] | None:
    """-> why the tick RELANCES the member: it owes an answer on a task that does not halt it (`owed_free`) and stands
    at the bottom of the deadlocked set --
    `("owed", None)` a sink, `("cycle", <member>)` a knot, naming a member it waits on --; None otherwise. Every
    relance asks an answer or an info, whatever the member's silence. No count bounds the relances: its silence
    makes the member suspected, and `launches:`, `budget:` and `budget-launches:` bound a long task."""
    debts = owed_free(state, member)
    if not debts or not at_bottom(state, member):
        return None
    waits = sorted(waits_for(state).get(member, ()))
    return ("owed", None) if not waits else ("cycle", waits[0])


def silences(state: dict, name: str, clock: datetime, member: str | None = None) -> list[dict]:
    """-> what the tick writes for each member whose SILENCE fell (row 115): `silence {agent, task, passages}` for a
    member, no wake-up of its under way, whose silent passages in a row on a task it owes on (`silent_tasks`)
    reach `silence:`; for a member suspected already, once its interval passed, ONE silent passage begun since its
    last fall -- of a launch or of its silence: its try said nothing -- is one more fall. The replay makes each a
    fall of the detector (`health.falls + 1`,
    `cause: silence`). A root's principal gets the team's notice about it, once per opening. Judged for ONE member
    (`member`) right before its own wake, on the journal as it stands then -- a launch of its may have ended
    since the tick began --, or for every member."""
    events: list[dict] = []
    for member in ([member] if member else list((state["started"] or {}).get("agents") or {})):
        if busy(state, member):
            continue
        suspicion = suspicion_of(state, member)
        fallen_at = int(((state.get("health") or {}).get(member) or {}).get("id") or 0) if suspicion is not None else 0
        for task in silent_tasks(state, member):
            n = silence_of(state, member, task, fallen_at)
            fell = (n >= 1 and clock >= suspicion["until"]) if suspicion is not None else (
                n >= silence_limit(state, member))
            if not fell:
                continue
            events.append({"kind": "silence", "agent": member, "task": task, "passages": n})
            opening = opening_of(state, task)
            told = any(is_notice(state, one) and one.get("about") == member and one.get("task") == task
                       and one["id"] > int(opening or 0) for one in state["messages"].values())
            if is_root(state, member, task) and not told:
                events.append({"kind": "post", "task": task, "from": name, "to": told_of(state, member, task),
                               "verb": "notice", "about": member, "cause": "silence",
                               "text": f"{member} owes an answer on {task} and ended {n} exchange(s) in a row without "
                                       "a message to the team: it is suspected, and the team tries it again after a pause"})
            break                                                # one fall per tick and member
    return events


def suspicion_of(state: dict, member: str) -> dict | None:
    """-> the member's SUSPICION (the failure detector ◇P, Chandra and Toueg 1996), read from the journal alone:
    `{falls, until}` while a final failure of its stands -- its INTERVAL runs from the hour of the last one for the
    base of the team's net in seconds (`schedule:`, DEFAULT_SCHEDULE without it or under `off`) doubled at each
    final failure in a row and never above `suspect-max:` (DEFAULT_SUSPECT_MAX without it), `until` the local hour
    it ends --, None for a member not suspected."""
    health = (state.get("health") or {}).get(member) or {}
    falls = int(health.get("falls") or 0)
    if not falls or not health.get("at"):
        return None
    base = schedule_seconds(state.get("started")) or DEFAULT_SCHEDULE
    bound = int(state["limits"].get("suspect-max") or DEFAULT_SUSPECT_MAX)
    at = datetime.fromisoformat(str(health["at"])).astimezone().replace(tzinfo=None)
    return {"falls": falls, "until": at + timedelta(seconds=min(base * 2 ** (falls - 1), bound))}


def within(state: dict, member: str, clock: datetime) -> bool:
    """-> whether the member is suspected and its interval still runs: nobody wakes it."""
    suspicion = suspicion_of(state, member)
    return suspicion is not None and clock < suspicion["until"]


def not_answering(member: str, suspicion: dict) -> str:
    return (f"no answer: {member} is not answering at the moment. A message sent to {member} from "
            f"{suspicion['until']:%H:%M:%S} on reaches it again")


def suspected_answers(state: dict, clock: datetime) -> list[dict]:
    """-> what the tick writes for each SUSPECTED member within its interval, no wake-up of its under way: every
    debt it owes to a MEMBER and every `do` or `ask` of a member that reaches it answered in its place (`re`, `by:
    tick`, its text the hour from which a message reaches the member again), which takes the message out of the
    member's inbox and wakes its author: `suspected` on a message a `wake-intent` of the member carried -- a debt
    delivered, or a message a dead launch gave back to the inbox for its retry --, `returned` on a message no
    `wake-intent` of the member ever carried -- the replay holds that one for returned to its author. Either way the
    author's head shows the message whole (`message_of`). What a PRINCIPAL
    says to the member is never answered for: a launch of the member delivers it at this very tick (`woken`), and
    that launch is its try; a principal's opening delivered before the fall stays owed, tried once the interval
    passed (`tried_of`). A member's message that owes nothing waits for the try."""
    events: list[dict] = []
    for member in list((state["started"] or {}).get("agents") or {}):
        suspicion = suspicion_of(state, member)
        if suspicion is None or clock >= suspicion["until"] or busy(state, member):
            continue
        said = not_answering(member, suspicion)
        carried = {key for one in state["intents"].values() if one.get("agent") == member
                   for key in one.get("messages") or []}       # what a launch of the member carried, whatever its end
        reaching = [one["id"] for one in inbox(state, member) if owes(state, one["id"]) and is_open(state, one.get("task"))]
        for key in dict.fromkeys(owed_by(state, member) + reaching):
            message = state["messages"][key]
            if is_member(state, message.get("from")):
                how = "suspected" if key in carried or key in state["delivered"] else "returned"
                events.append({"kind": "post", "task": message.get("task"), "from": member, "to": message.get("from"),
                               "verb": "re", "re": key, "by": "tick", how: True, "text": said})
    return events


def tried_of(state: dict, member: str, clock: datetime) -> tuple[str, None] | None:
    """-> `("tried", None)` when the tick TRIES the suspected member by a relance: its interval passed, no wake-up
    of its under way, and a principal's opening among its debts -- what nothing else would deliver it again. A
    member with another message to receive is tried by that message, as any wake-up."""
    suspicion = suspicion_of(state, member)
    if suspicion is None or clock < suspicion["until"] or busy(state, member):
        return None
    return ("tried", None) if any(principal_opening(state, key) for key in owed_free(state, member)) else None


def health_lines(state: dict, member: str) -> str:
    """-> the HEALTH VIEW a wake-up's head carries: one line per other member suspected, the hour of its try --
    '' when nobody is."""
    found = []
    for other in list((state.get("started") or {}).get("agents") or {}):
        suspicion = suspicion_of(state, other) if other != member else None
        if suspicion is not None:
            found.append(f"[not answering at the moment: {other} -- tried again at {suspicion['until']:%H:%M:%S}]")
    return "\n".join(found)


def is_member(state: dict, name) -> bool:
    return name in ((state["started"] or {}).get("agents") or {})


def parent_of(state: dict, agent: str, task: str) -> str:
    """-> whom the agent reports to on this task: the one that delegated it, else the task's
    author (a principal)."""
    for one in reversed(state["delegations"]):
        if one["to"] == agent and one["task"] == task:
            return str(one["from"])
    return str((state["tasks"].get(task) or {}).get("from") or (state["started"] or {}).get("owner") or "")


def told_of(state: dict, member: str, task: str) -> str:
    """-> whom the team's NOTICE about the member on this task goes to -- a person with a box, never the team: the
    member that delegated the task to it, else the task's principal, the owner when the team itself wrote the task (a
    ceremony's)."""
    for one in reversed(state["delegations"]):
        if one["to"] == member and one["task"] == task:
            return str(one["from"])
    started = state["started"] or {}
    author = (state["tasks"].get(task) or {}).get("from")
    return str(author if author and author != started.get("team") else started.get("owner") or "")


def is_root(state: dict, agent: str, task: str) -> bool:
    """-> whether the agent holds the task from a principal: its `done` resolves the task."""
    held = state["tasks"].get(task) or {}
    return held.get("to") == agent and not is_member(state, held.get("from"))


def is_principal(state: dict, name) -> bool:
    """-> whether `name` is one a team answers to: its owner, a mandator of `principals:`, or the
    team itself (the author of a ceremony task)."""
    started = state["started"] or {}
    return name is not None and (name == started.get("owner") or name == started.get("team")
                                 or name in (started.get("principals") or []))


def edges_of(state: dict, task: str) -> set[tuple[str, str]]:
    """-> the (agent, the one it reports to) pairs that route on the task: the `reports:` edges,
    and on a ceremony task each participant reporting to the ceremony's facilitator."""
    started = state["started"] or {}
    pairs = {(child, str(one.get("to"))) for one in started.get("reports") or [] for child in one.get("from") or []}
    ceremony = (state["tasks"].get(task) or {}).get("ceremony")
    for one in started.get("ceremonies") or []:
        if ceremony is not None and one.get("name") == ceremony:
            pairs |= {(child, str(one.get("facilitator"))) for child in one.get("participants") or []}
    return pairs


def written(conductor, root: Path, path: Path, name: str, judge, undeclared: bool = False) -> list[dict]:
    """The journal's critical section: under its lock the team's declaration is read again -- a team deleted
    meanwhile refuses `team-unknown`, and the directory the lock made, holding no journal, leaves with the
    refusal --, then the events are read, `judge(state, events)` says the events to append -- without `at`,
    `id`, `team` -- or refuses, and they are appended with the next ids. `undeclared` is the writer that speaks of
    a team whose declaration is away while its journal stands (the timer's notice of a failed tick): the journal
    standing is enough for it. -> the events written, whole."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with conductor.record.held(path):
        declaration = team_doc(root, name)
        if not declaration.is_file() and not (undeclared and path.is_file()):
            if not path.is_file():
                shutil.rmtree(path.parent, ignore_errors=True)
            refuse(f"team-unknown -- no {declaration}: the owner declares the team there.")
        events = tailed(path)
        state = replay(events)
        last = max((int(one.get("id") or 0) for one in events), default=0)
        made = []
        for offset, one in enumerate(judge(state, events), 1):
            made.append({"at": now(), "id": last + offset, "kind": one["kind"], "team": name,
                         **{key: value for key, value in one.items() if key != "kind"}})
        with path.open("a", encoding="utf-8") as handle:
            for one in made:
                handle.write(json.dumps(one, ensure_ascii=False) + "\n")
    return made


def appended(conductor, root: Path, path: Path, name: str, events: list[dict], undeclared: bool = False) -> list[dict]:
    """Appends the events given, judged already: the tick's writes; `undeclared` as `written` takes it."""
    return written(conductor, root, path, name, lambda state, lines: events, undeclared) if events else []


def next_task(state: dict) -> str:
    return f"T{len(state['tasks']) + 1}"


def deleting_said(name: str) -> str:
    """-> the refusal of a write on a team a delete has begun to remove (`deleting` written)."""
    return f"team-deleting -- {name} is being deleted: `team delete {name} --yes` again finishes it."


# --- the agents, by the house's console ----------------------------------------------------

def born(root: Path, conductor, paths: list[str]) -> list[str]:
    """Creates the agents the house lacks by the house's own console, `agent add <path> --type member`: an
    instance at each path under the house that BORROWS the house's machine, no door, its
    SETTINGS at the cap and the member's profile `add` writes (its boot without the catalog of skills nor
    the threads' pass) -- each path once, however many members it plays -- never
    by an import of another package's script. `add` plays under the house's BIRTH lock for the
    path (`born-busy` past `call_lock_wait`): two starts that name one new path give it birth
    once, the other reads `agent-exists`. -> the paths born."""
    engine = engine_of(root, conductor)
    made = []
    for name in dict.fromkeys(paths):
        if conductor.instance.is_instance(agent_meta(root, name)):
            continue
        added = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "add", name,
                                "--type", MEMBER_TYPE],
                               capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
        if added.returncode == 0:
            made.append(name)
        elif "agent-exists" not in added.stderr:
            refuse(f"agent-add-failed -- `{name}` could not be born under the house: "
                   f"{(added.stderr or added.stdout).strip()[-300:]}")
    return made


def placed(target: Path, data: bytes) -> None:
    """Writes `target` whole: a temporary beside it, then one rename."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}-{secrets.token_hex(3)}")
    temporary.write_bytes(data)
    os.replace(temporary, target)


# --- the entries: successors of each agent's DAG, from the team's directory --------------------

def entries_at(team: dict) -> dict[str, list[str]]:
    """-> for each agent's path, the entry documents its members may play, in the declaration's
    order: `do`'s for every member, a ceremony's for its participants and its facilitator."""
    played: dict[str, list[str]] = {}
    ceremonies = {one["name"]: one for one in team["ceremonies"]}
    for trigger, document in team["entries"].items():
        members = (list(team["agents"]) if trigger == "do"
                   else [*ceremonies[trigger]["participants"], ceremonies[trigger]["facilitator"]])
        for member in members:
            documents = played.setdefault(team["agents"][member], [])
            if document not in documents:
                documents.append(document)
    return played


def entries_judged(root: Path, conductor, name: str, team: dict) -> None:
    """DECLINES `entry-missing` before anything is written when an entry is neither in the team's
    directory nor resolved by the instance of an agent that plays it (a document of its type) --
    the agent's run would name a successor it cannot play, and would play no exchange at all."""
    directory = team_root(root, name)
    missing = [f"{path} lacks {document}" for path, documents in entries_at(team).items()
               for document in documents
               if not (directory / document).is_file()
               and (not conductor.instance.is_instance(agent_meta(root, path))
                    or not conductor.instance.resolve(agent_meta(root, path), document).is_file())]
    if missing:
        decline(f"entry-missing -- {'; '.join(missing)}: an entry lives in the team's directory "
               f"({TEAMS}/{name}/), or in the instance of every agent that plays it -- lay it there, then start again.")


def team_document(name: str, documents: list[str], intention: str, served: list[str]) -> bytes:
    """-> `TEAM-<name>.md` of the team's directory: the HEAD this skill writes -- called at the kit's
    `turn.begin` of every exchange of the team's runs, its `SERVE` serves `served` (`served_of`: the document
    itself, the package's `TEAM_WORK.md`, then the team's other documents), each body read once and again when it changes; with entries, at
    its exit this skill's verb `entry` elects among them and the neutral successor -- then the BODY, the team's
    intention as `start` renders it from the template `TEAM.md` names, empty without one."""
    elected = (f"next: {' '.join([*documents, IDLE])}\ndecide: {DECIDER} {name}\n" if documents else "")
    lines = "".join(f"  {one}\n" for one in served)
    return (f"---\nproc: |\n  SERVE\nserve: |\n{lines}attach: turn.begin\n{elected}---\n" + intention).encode("utf-8")


def turn_overlay() -> bytes:
    """-> `TURN.md` of the team's directory: the overlay of the kit's turn, its `output:` the form of an act
    (`ACT_FORMAT`) and nothing else -- no law, no body. The directory is the root of documents of every run the
    team opens: the WORK line of each of their exchanges names that form."""
    return f"---\nname: {Path(TURN_DOC).stem}\noutput: {ACT_FORMAT}\n---\n".encode("utf-8")


def team_documents(directory: Path, name: str) -> list[Path]:
    """-> every `TEAM-<name>-<x>.md` standing in the team's directory, sorted by name."""
    prefix = f"TEAM-{name}-"
    if not directory.is_dir():
        return []
    return sorted((one for one in directory.iterdir() if one.is_file() and one.name.startswith(prefix)
                   and one.name.endswith(".md") and len(one.name) > len(prefix) + len(".md")), key=lambda one: one.name)


def served_of(conductor, directory: Path, name: str) -> list[str]:
    """-> what the head of `TEAM-<name>.md` serves: the document itself, then `TEAM.md` when its body says something
    -- the owner's word, served as it is and read again as soon as it changes --, then the package's `TEAM_WORK.md`
    -- how a
    team works, read before the team's other documents it tells how to read --, then `SEASON.md` when its body says
    something -- the owner's word of the season, served as it is and read again as soon as it changes --, then what
    every member's view (`view_of`) gives the head to serve: each `TEAM-<name>-<x>.md` of the root that does not
    mount, sorted by name -- the engine mounts the others, a second reading would bring their body twice; a document
    of a role, under `roles/`, is its members' vector's. Their NAMES alone, never their bodies: pp serves them, the
    spec found by its name in the refs of the package the member's instance plays."""
    declared = directory / TEAM_DOC
    word = body_of(declared.read_text(encoding="utf-8")) if declared.is_file() else ""
    return [document_name(name), *([TEAM_DOC] if word else []), SPEC, *([SEASON_DOC] if season_word(directory) else []),
            *(one["document"] for one in view_of(conductor, directory, name, {}, []) if one["by"] == "head")]


def document_planned(conductor, path: Path, data: bytes):
    """-> the engine's document of a text about to be written at `path` -- its front matter read as the engine reads a
    file's (`reading.front_matter`); `conductor.Refusal` when it opens on none or never closes it."""
    lines = data.decode("utf-8").splitlines()
    if not lines or lines[0].strip() != BORDER:
        raise conductor.Refusal("front-matter-missing", f"{path.name} does not open with a front matter")
    end = next((at for at, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    if end is None:
        raise conductor.Refusal("front-matter-unterminated", f"{path.name} never closes its front matter")
    return conductor.Document(name=path.stem, front=conductor.reading.front_matter(lines[1:end]), path=path)


def common_judged(root: Path, conductor, name: str, team: dict, planned: dict[str, bytes | None] | None = None,
                  composed: list[dict] | None = None) -> None:
    """Judges the VIEW of each member (`view_of`) before anything is written -- the documents it mounts, as they WILL
    stand when `planned` is given (`{document: bytes about to be written, or None about to be removed}`) and with the
    documents of a role `composed` renders (`documents_planned`): `start` refuses what it declines, `declaration` says
    it. Each
    defect DECLINES by its name, the member and the document named: `common-code-prefix`, a law whose code does not
    open on `TM` -- the prefix kept for the team's laws --; `common-collision`, a code two documents of one member's
    view declare, or a code declared at the member -- its every exchange would refuse `mount-collision` --: two
    documents of disjoint roles may carry the same code; `common-tool-unknown`, a `tools:` name nothing resolves at
    the member (a document, a skill, a contract of a harness home); `common-serve-unknown`, a `serve:` document
    neither in the team's directory -- one this start removes counts as gone -- nor resolved at the member (its
    instance, its repository, a skill); `common-mount-moment`, a document of a role whose `mount:` names another
    moment than `turn.begin`, the one its vector mounts it at. A member is judged at its instance; a member not born yet
    at the house's machine -- the base and the pins `agent add` gives it --, nothing written. The codes declared at a
    member are the engine's inventory (`sections.inventory`, the one `pp-authoring` derives free codes from) of its
    instance and of each package it plays; a row read from a material (`@<name>`) is the run's to resolve, not
    judged."""
    directory = team_root(root, name)
    planned, composed = planned or {}, composed or []
    read: dict[str, tuple | None] = {}

    def judged_document(document: str) -> tuple | None:
        if document not in read:
            path = directory / document
            try:
                parsed = (conductor.reading.read(path) if planned.get(document) is None
                          else document_planned(conductor, path, planned[document]))
            except (conductor.Refusal, OSError):
                read[document] = None                  # no front matter to read: it mounts nothing
                return None
            try:
                laws = conductor.reading.constraints(parsed)
                served = [conductor.reading.ranged(token)[0] for row in conductor.reading.serve_lines(parsed)
                          if not any(one.startswith("@") for one in row)
                          for token in (row[1:] if row and row[0].endswith(":")
                                        and row[0][:-1] in conductor.settings.SERVE_NATURES else row)]
            except conductor.Refusal as refusal:
                decline(f"team-invalid -- {path}: {refusal}")
            read[document] = (parsed, laws, served)
        return read[document]

    inventories: dict[Path, set[str]] = {}

    def inventory(home: Path) -> set[str]:
        if home not in inventories:
            inventories[home] = conductor.sections.inventory(home)
        return inventories[home]

    for member, agent in team["agents"].items():
        mounted = [one for one in view_of(conductor, directory, name, team.get("roles") or {}, composed, member,
                                          planned) if one["effect"] == "mounted"]
        if not mounted:
            continue
        meta = agent_meta(root, agent)
        born = conductor.instance.is_instance(meta)
        at = meta if born else root                    # not born: the house's machine, what `agent add` gives it
        where = agent if born else f"{agent}, not born: the house's machine"
        declared = set().union(*(inventory(home) for home in conductor.instance.vendored(at)),
                               inventory(meta) if born else set())
        held: dict[str, str] = {}
        for entry in mounted:
            found = judged_document(entry["document"])
            if found is None:
                continue
            document, laws, served = found
            named = entry["document"]
            moment = str(document.front.get("mount") or "").strip()
            if entry["by"] == "vector" and moment != MOUNT_MOMENT:
                decline(f"common-mount-moment -- `mount: {moment}` ({named}), in the view of {member}: a document of "
                        f"a role is mounted by its member's vector before the message of every exchange -- declare "
                        f"`mount: {MOUNT_MOMENT}`.")
            for law in laws:
                if not law.code.startswith(TEAM_LAW):
                    decline(f"common-code-prefix -- `{law.code}` ({named}): a law of a document the team mounts "
                            f"opens on `{TEAM_LAW}`, the prefix kept for the team's laws -- recode it `{TEAM_LAW}<n>`.")
                if law.code in held:
                    decline(f"common-collision -- `{law.code}` ({named}) is declared by {held[law.code]} too: both "
                            f"are mounted in the runs of {member} -- give one of them another code.")
                held[law.code] = named
                if law.code in declared:
                    decline(f"common-collision -- `{law.code}` ({named}) is already declared at {member} ({where}): "
                            "mounted in its runs, it would refuse `mount-collision` at every exchange -- recode it.")
            unknown = [one.name for one in conductor.compiling.tools_of(document, at) if not one.contract]
            if unknown:
                decline(f"common-tool-unknown -- `{unknown[0]}` ({named}): nothing resolves it at {member} "
                        f"({where}) -- no document, no skill, no contract of a harness home; name one it plays.")
            lost = [one for one in served if (planned[one] is None if one in planned   # removed by this start
                                              else not served_at(conductor, directory, at, born, one))]
            if lost:
                decline(f"common-serve-unknown -- `{lost[0]}` ({named}): neither in the team's directory "
                        f"({TEAMS}/{name}/) nor resolved at {member} ({where}) -- lay it there, or name what it reads.")


def served_at(conductor, directory: Path, meta: Path, born: bool, document: str) -> bool:
    """-> whether a `serve:` document resolves for a run of the team: in the team's directory -- its runs' root of
    documents --, at the instance `meta` (`instance.resolve`), at the member's repository when it is born, or, for a
    bare name, as a skill's contract (the instance's skills, a harness home, the house's procs)."""
    if (directory / document).is_file() or conductor.instance.resolve(meta, document).is_file():
        return True
    if born and (meta.parent / document).is_file():
        return True
    stem = Path(document).stem
    return "/" not in document and (conductor.instance.skill_contract(meta, stem)
                                    or conductor.instance.adopted(meta, stem)) is not None


def sheet_name(name: str) -> str:
    """-> the file name of the members' sheet: `TEAM-<name>-members.md`."""
    return f"TEAM-{name}-members.md"


def said_description(conductor, path: Path) -> str:
    """-> the `description:` of a document's front matter, its blanks folded; "" when absent or unreadable."""
    try:
        said = conductor.reading.read(path).front.get("description")
    except (conductor.Refusal, OSError):
        return ""
    return " ".join(str(said or "").split())


def template_description(root: Path, conductor) -> str:
    """-> the `description:` of the member template the house's base carries (`MEMBER.md` of its user layer, the
    copy the house vendors), "" when none stands: a member still saying it has no description of its own."""
    package = manifests_named(root, conductor).get(conductor.instance.base_of(root))
    seed = package / conductor.install.USER / "MEMBER.md" if package is not None else None
    return said_description(conductor, seed) if seed is not None and seed.is_file() else ""


def description_of(root: Path, conductor, path: str, template: str) -> str:
    """-> what the members' sheet says of the agent at `path`: the `description:` of its `MEMBER.md`, or
    `no description` when it is absent, empty or still the template's."""
    said = said_description(conductor, agent_meta(root, path) / "MEMBER.md")
    return said if said and said != template else NO_DESCRIPTION


def sheet_of(root: Path, conductor, name: str, team: dict, launch: dict, profiles: dict) -> bytes:
    """-> `TEAM-<name>-members.md`: no front matter, one table, one row per member in the declaration's order --
    whom it reports to (`reports:`), its role keys when the team declares any (`roles:`, joined by a comma, `—` for
    none), the model and the effort of its profile, else of the season's launch, else the agent's default, its
    description (`description_of`). A team without a role key keeps the five columns."""
    above = {child: str(one.get("to")) for one in team["reports"] for child in one.get("from") or []}
    template = template_description(root, conductor)
    cell = lambda text: " ".join(str(text).split()).replace("|", "\\|")
    rows = []
    for member, path in team["agents"].items():
        profile = profiles.get(member) or {}
        model = profile.get("model") or launch.get("model") or "agent default"
        effort = profile.get("effort") or launch.get("effort") or "default"
        keys = [key for key, members in team["roles"].items() if member in members]
        held = f" {cell(', '.join(keys) or '—')} |" if team["roles"] else ""
        rows.append(f"| {cell(member)} | {cell(above.get(member, '—'))} |{held} {cell(model)} | {cell(effort)} | "
                    f"{cell(description_of(root, conductor, path, template))} |")
    roles_head, roles_rule = (" roles |", "---|") if team["roles"] else ("", "")
    return (f"# The members of {name}\n\n| member | reports to |{roles_head} model | effort | description |\n"
            f"|---|---|{roles_rule}---|---|---|\n" + "\n".join(rows) + "\n").encode("utf-8")


def document_name(name: str) -> str:
    """-> the file name of the team's document: `TEAM-<name>.md`."""
    return f"TEAM-{name}.md"


def documents_written(root: Path, conductor, name: str, team: dict, launch: dict, profiles: dict,
                      planned: dict[str, bytes | None]) -> dict[str, str]:
    """Writes the team's documents in its directory, at every start, and -> the digest of each document it renders
    (`team-started.rendered`, by its place): the documents of the lines first -- each document `planned` written, each
    no line names any more removed (`documents_planned`) --, the members' sheet (`sheet_of`), then
    `TEAM-<name>.md` -- its head serving `TEAM.md`'s body and every `TEAM-<name>-<x>.md` standing then, the sheet
    with them; its body the intention rendered (`team["intention"]`) --, `TEAM-IDLE.md` with entries, and `TURN.md`,
    the overlay of the kit's turn (`turn_overlay`). `TEAM.md` is never written. The law an earlier version laid
    there, `TURN.md` at its bytes (`RETIRED_IN_TEAM`), is replaced by the overlay and said; a `TURN.md` or a
    `TEAM-IDLE.md` standing there and different is the owner's: kept, and said -- under the owner's `TURN.md` the
    team's runs play the turn it writes."""
    here = Path(__file__).resolve().parent
    directory = team_root(root, name)
    entries = list(dict.fromkeys(team["entries"].values()))
    target, data = directory / TURN_DOC, turn_overlay()
    if not target.is_file():
        placed(target, data)
    elif any(target.read_bytes() == (here / one).read_bytes() for one in RETIRED_IN_TEAM[TURN_DOC]):
        placed(target, data)                            # an earlier version's law: the team's, replaced
        print(f"pp-team: {TEAMS}/{name}/{TURN_DOC} replaced by the overlay of the turn -- it was the law of an "
              "earlier version", file=sys.stderr)
    elif target.read_bytes() != data:
        print(f"pp-team: {TEAMS}/{name}/{TURN_DOC} kept -- it is the owner's own: the team's runs ask for the form "
              f"`{ACT_FORMAT}` only if it carries `output: {ACT_FORMAT}`", file=sys.stderr)
    if entries:
        target, data = directory / IDLE, (here / IDLE_SOURCE).read_bytes()
        if target.is_file() and target.read_bytes() != data:
            print(f"pp-team: {TEAMS}/{name}/{IDLE} kept -- not the team's: the owner's own stays", file=sys.stderr)
        elif not target.is_file():
            placed(target, data)
    for document, data in planned.items():
        if data is None:
            (directory / document).unlink(missing_ok=True)
            print(f"pp-team: {TEAMS}/{name}/{document} removed -- no line names it any more", file=sys.stderr)
        else:
            placed(directory / document, data)
    roles = directory / ROLES_DIR
    if roles.is_dir() and not any(roles.iterdir()):
        roles.rmdir()                                  # no document of a role left
    placed(directory / sheet_name(name), sheet_of(root, conductor, name, team, launch, profiles))
    own = team_document(name, entries, team["intention"] + "\n" if team["intention"] else "",
                        served_of(conductor, directory, name))
    placed(directory / document_name(name), own)
    return {document_name(name): hashlib.sha256(own).hexdigest()[:12],
            **{one: hashlib.sha256(data).hexdigest()[:12] for one, data in planned.items() if data is not None}}


def cleared(root: Path, name: str, team: dict) -> None:
    """Removes from each agent of the team what an earlier version laid in its instance: the files at
    the team's very bytes (`RETIRED`: the law and the neutral successor of team 0.32, the decider skill)
    and `procs/TEAM-<name>.md` deciding by `team-entry <name>`; a file that differs is the agent's own --
    kept, and said. Nothing of a team is written there."""
    here = Path(__file__).resolve().parent
    for path in dict.fromkeys(team["agents"].values()):
        meta = agent_meta(root, path)
        for where, source in RETIRED.items():
            target = meta.joinpath(*where)
            if not target.is_file():
                continue
            if (here / source).is_file() and target.read_bytes() == (here / source).read_bytes():
                target.unlink()
            else:
                print(f"pp-team: {path} · {'/'.join(where)} kept -- not the team's: the agent's own stays",
                      file=sys.stderr)
        skill = meta / "skills" / "team-entry"
        if skill.is_dir() and not any(skill.iterdir()):
            skill.rmdir()
        laid = meta / "procs" / f"TEAM-{name}.md"
        if laid.is_file():
            if f"decide: team-entry {name}" in laid.read_text(encoding="utf-8", errors="replace"):
                laid.unlink()
            else:
                print(f"pp-team: {path} · procs/TEAM-{name}.md kept -- not the team's: the agent's own stays",
                      file=sys.stderr)


def entry_of(root: Path, name: str, run: str) -> str:
    """-> the document the wake-up of the team under the run `run` plays: the last wake-up of the
    team launched under that key and not ended -- its intent's run, its `wake-launched`, else its
    tag at the house's `messages.jsonl` (an opening's first exchange plays before the tick writes
    `wake-launched`) --; its task's ceremony names its entry, any other task `do`'s; no entry, no
    such wake-up, no journal: the neutral `TEAM-IDLE.md`. Nothing written, no lock."""
    journal = journal_of(root, name)
    if not journal.is_file():
        return IDLE
    state = state_of(journal)
    standing = open_intents(state)
    under = [one for one in standing
             if run in (one.get("run"), (state["launched"].get(one["tag"]) or {}).get("run"))]
    if not under:
        opening = {one["tag"] for one in standing if one.get("run") is None}
        under = [state["intents"][line["tag"]] for line in lines_of(record_of(root, MESSAGES))
                 if line.get("run") == run and line.get("tag") in opening]
    if not under:                                  # an opening under way: the house opened the run before any
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # record names it -- the agent's slot says it
        from _core import core                     # noqa: E402 -- the bootstrap
        persistence = core(__file__).persistence
        under = [one for one in standing if one.get("run") is None
                 and persistence.slot_of(agent_meta(root, path_of_intent(state, one)), run).is_file()]
    if not under:
        return IDLE
    entries = (state["started"] or {}).get("entries") or {}
    task = state["tasks"].get(under[-1].get("task")) or {}
    document = entries.get(str(task["ceremony"])) if task.get("ceremony") else entries.get("do")
    return str(document or IDLE)


# --- the relaunch entry: the house's way back after a restart, ONE for all its teams ------------

def table_read() -> tuple[list[str], str]:
    """-> (the calendar's lines, '') -- the file `PP_CRONTAB` names when it is set (absent:
    empty), else the user's crontab (`crontab -l`; none yet: empty); or ([], why) when no
    table can be read."""
    given = os.environ.get(CRONTAB)
    if given:
        path = Path(given)
        if not path.is_file():
            return [], ""
        try:
            return path.read_text(encoding="utf-8").splitlines(), ""
        except OSError as why:
            return [], f"{given}: {why}"
    try:
        played = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    except OSError as why:
        return [], f"crontab: {why}"
    if played.returncode == 0:
        return played.stdout.splitlines(), ""
    if "no crontab" in (played.stderr or ""):
        return [], ""
    return [], (played.stderr or "").strip() or f"crontab -l rc {played.returncode}"


def table_write(lines: list[str]) -> str:
    """Replaces the calendar with these lines -- the `PP_CRONTAB` file, or `crontab -`.
    -> '' or why it could not be written."""
    text = "\n".join(lines) + ("\n" if lines else "")
    given = os.environ.get(CRONTAB)
    if given:
        try:
            Path(given).write_text(text, encoding="utf-8")
            return ""
        except OSError as why:
            return f"{given}: {why}"
    try:
        played = subprocess.run(["crontab", "-"], input=text, capture_output=True, text=True)
    except OSError as why:
        return f"crontab: {why}"
    return "" if played.returncode == 0 else ((played.stderr or "").strip() or f"crontab - rc {played.returncode}")


def mark_of(root: Path) -> str:
    """-> the mark that ends the house's one line in the crontab: how it is found again and removed."""
    return f"# pp-team {root}"


def marked(line: str, root: Path) -> bool:
    """-> whether a crontab line is the house's: its mark, or the mark of one of its teams that an earlier version laid
    (`# pp-team <house> <team>`) -- never the line of a house whose path only begins like this one's."""
    _, found, rest = line.rstrip().rpartition(" # pp-team ")
    return bool(found) and (rest == str(root) or rest.startswith(f"{root} "))


def value_name(root: Path) -> str:
    """-> the house's value in the user's Run key: `pp-team-<12 hex of the house's path>`, so that two houses of one
    user never take each other's."""
    return f"{RELAUNCH_PREFIX}-{hashlib.sha1(str(root).encode('utf-8')).hexdigest()[:12]}"


def reg_played(*args: str) -> tuple[str, str]:
    """-> (stdout, '') of `reg.exe <args>` -- Windows' own console on the registry, reached from WSL --, or ('', why)."""
    try:
        played = subprocess.run(["reg.exe", *args], capture_output=True, text=True, errors="replace")
    except OSError as why:
        return "", f"reg.exe: {why}"
    if played.returncode == 0:
        return played.stdout, ""
    return "", f"reg.exe: {(played.stderr or played.stdout or '').strip() or f'rc {played.returncode}'}"


def runkey_read() -> tuple[dict[str, str], str]:
    """-> ({value: command}, '') of the user's Run key -- the file `PP_RUNKEY` names when it is set (one line
    `<value>\t<command>` per value; absent: empty), else `RUN_KEY` under HKEY_CURRENT_USER by `winreg`, else by
    `reg.exe query` (WSL); or ({}, why)."""
    given = os.environ.get(RUNKEY)
    if given:
        path = Path(given)
        if not path.exists():
            return {}, ""
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as why:
            return {}, f"{given}: {why}"
        return dict(one.split("\t", 1) for one in lines if "\t" in one), ""
    try:
        import winreg
        found: dict[str, str] = {}
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            index = 0
            while True:
                try:
                    value, data, _ = winreg.EnumValue(key, index)
                except OSError:
                    return found, ""
                found[str(value)] = str(data)
                index += 1
    except ImportError:
        pass
    except OSError as why:
        return {}, f"Run key: {why}"
    said, why = reg_played("query", f"HKCU\\{RUN_KEY}")
    if why:
        return {}, why
    rows = (re.match(r"^ {4}(.+?) {4}REG_\w+ {4}(.*)$", one) for one in said.splitlines())
    return {row.group(1): row.group(2) for row in rows if row}, ""


def runkey_write(value: str, command: str | None) -> str:
    """Writes ONE value of the user's Run key -- `command` set, None removed -- in the `PP_RUNKEY` file, by `winreg`, or
    by `reg.exe add|delete` (WSL), under no right the user lacks. -> '' or why it could not be written."""
    given = os.environ.get(RUNKEY)
    if given:
        found, why = runkey_read()
        if why:
            return why
        found.pop(value, None)
        if command is not None:
            found[value] = command
        try:
            Path(given).write_text("".join(f"{one}\t{data}\n" for one, data in found.items()), encoding="utf-8")
            return ""
        except OSError as why:
            return f"{given}: {why}"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if command is None:
                winreg.DeleteValue(key, value)
            else:
                winreg.SetValueEx(key, value, 0, winreg.REG_SZ, command)
        return ""
    except FileNotFoundError:
        return ""
    except ImportError:
        pass
    except OSError as why:
        return f"Run key: {why}"
    if command is None:
        return reg_played("delete", f"HKCU\\{RUN_KEY}", "/v", value, "/f")[1]
    return reg_played("add", f"HKCU\\{RUN_KEY}", "/v", value, "/t", "REG_SZ", "/d", command, "/f")[1]


def call_wait(root: Path, conductor) -> float:
    """-> `call_lock_wait` as the house's SETTINGS say it, 30 s without them: how long a verb
    waits for one of the house's locks."""
    try:
        return float(conductor.settings.of(root).call_lock_wait)
    except (AttributeError, TypeError, ValueError):
        return 30.0


def relaunch_held(root: Path, conductor):
    """-> the lease on the house's RELAUNCH lock (`state/relaunch.lock`), waited for within `call_lock_wait` -- the
    entry is laid, judged and removed under it, so that the stop of one team and the start of another at once never
    take the net of the team in need --, or None past the bound."""
    return locks(conductor).acquire(root / ".sys" / "state" / RELAUNCH_LOCK, wait=call_wait(root, conductor))


def scheduler(system: str | None = None) -> str:
    """-> the façade that holds the relaunch entry: `nt` (the user's Run key) or `posix` (the user's crontab) -- the
    system given, else `PP_SCHEDULER` (the bench plays both façades on one machine), else the system this process runs
    on."""
    return system or os.environ.get(SCHEDULER) or ("nt" if os.name == "nt" else "posix")


def run_command(root: Path, conductor) -> str:
    """-> what the Run key plays at logon: `uvw run <engine> --instance <house> team tick --all --entry` -- uv's
    launcher without a window -- when `uvw` is found, else the house's console by its absolute path."""
    windowless = shutil.which("uvw")
    if windowless:
        return f'"{windowless}" run "{engine_of(root, conductor)}" --instance "{root}" team tick --all --entry'
    return f'"{house_console(root, conductor)}" team tick --all --entry'


def wsl_distro(system: str | None = None) -> str:
    """-> the WSL distribution this process runs in under the posix façade (`WSL_DISTRO_NAME`), '' elsewhere: where
    the Run key's value must start the distribution at logon, cron playing `@reboot` only once it runs."""
    return os.environ.get(WSL_DISTRO, "") if scheduler(system) == "posix" else ""


def wsl_command(root: Path, conductor, distro: str) -> str:
    """-> what the Run key plays at logon under WSL: `wsl.exe -d <distro> --exec <python> <engine> --instance <house>
    team tick --all --entry`, the paths absolute -- the tick played by the distribution it starts, cron or not."""
    return subprocess.list2cmdline(["wsl.exe", "-d", distro, "--exec", sys.executable, str(engine_of(root, conductor)),
                                    "--instance", str(root), "team", "tick", "--all", "--entry"])


def runkey_laid(value: str, command: str) -> str:
    """Lays ONE value of the Run key when it differs. -> '' or why the system refused it."""
    found, why = runkey_read()
    if why:
        return why
    return "" if found.get(value) == command else runkey_write(value, command)


def runkey_removed(value: str) -> str:
    """Removes ONE value of the Run key when it stands. -> '' or why the system refused it."""
    found, why = runkey_read()
    return why or (runkey_write(value, None) if value in found else "")


def reboot_line(root: Path, conductor) -> str:
    """-> the house's relaunch line in the crontab: `@reboot`, the interpreter and the engine by their absolute paths --
    the form `--on-end` composes, a line cron replays as is."""
    engine = engine_of(root, conductor)
    return (f"@reboot {shlex.quote(sys.executable)} {shlex.quote(str(engine))} "
            f"--instance {shlex.quote(str(root))} team tick --all --entry >/dev/null 2>&1 {mark_of(root)}")


def needing(root: Path, but: str | None = None) -> list[str]:
    """-> the teams of the house that need their net, in the order of their names: started, `schedule:` not `off`, a
    task open or a ceremony declared -- `but` left out (a team being deleted)."""
    home = root.parent / TEAMS
    names = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    found = []
    for name in names:
        journal = journal_of(root, name)
        if name == but or not journal.is_file():
            continue
        state = state_of(journal)
        if state["started"] is not None and schedule_seconds(state["started"]) is not None and not netless(state):
            found.append(name)
    return found


def kept_path(root: Path) -> Path:
    """-> where the house keeps the PATH of the process that laid its relaunch entry: `state/relaunch.path`."""
    return root / ".sys" / "state" / RELAUNCH_PATH


def laid_now(root: Path, conductor, system: str | None = None) -> str:
    """Lays the house's entry, the relaunch lock held by the caller: the PATH of this process kept at
    `state/relaunch.path` at every lay, then the Run key's value when it differs, or the crontab with every line marked
    for the house replaced by its one line -- and under WSL the Run key's value that starts the distribution as well.
    -> '' or why the system refused it."""
    placed(kept_path(root), os.environ.get("PATH", "").encode("utf-8"))
    if scheduler(system) == "nt":
        return runkey_laid(value_name(root), run_command(root, conductor))
    lines, why = table_read()
    if not why:
        line = reboot_line(root, conductor)
        kept = [one for one in lines if not marked(one, root)]
        why = "" if [one for one in lines if marked(one, root)] == [line] else table_write(kept + [line])
    distro = wsl_distro(system)
    said = runkey_laid(value_name(root), wsl_command(root, conductor, distro)) if distro else ""
    return "; ".join(one for one in (why, said) if one)


def relaunch_laid(root: Path, conductor, system: str | None = None) -> str:
    """Lays the house's ONE relaunch entry under the relaunch lock -- after the verb wrote its journal. -> '' or why the
    system refused it."""
    lease = relaunch_held(root, conductor)
    if lease is None:
        return "the relaunch lock is busy"
    try:
        return laid_now(root, conductor, system)
    finally:
        locks(conductor).release(lease)


def relaunch_removed(root: Path, conductor, name: str, but: str | None = None, system: str | None = None) -> None:
    """Removes the house's relaunch entry when NO team of the house needs its net any more (`but` left out) -- judged
    and removed in one hold of the relaunch lock; a removal the system refuses is said on stderr, in the words of the
    team `name` whose verb tried it."""
    lease = relaunch_held(root, conductor)
    if lease is None:
        sys.stderr.write(f"pp-team: {name} · relaunch not removed -- the relaunch lock is busy\n")
        return
    try:
        if needing(root, but):
            return
        if scheduler(system) == "nt":
            why = runkey_removed(value_name(root))
        else:
            lines, why = table_read()
            kept = [one for one in lines if not marked(one, root)]
            if not why and len(kept) != len(lines):
                why = table_write(kept)
            said = runkey_removed(value_name(root)) if wsl_distro(system) else ""
            why = "; ".join(one for one in (why, said) if one)
        if why:
            sys.stderr.write(f"pp-team: {name} · relaunch not removed -- {why}\n")
        else:
            kept_path(root).unlink(missing_ok=True)        # the entry gone, the PATH it took up goes with it
    finally:
        locks(conductor).release(lease)


def relaunch_standing(root: Path, system: str | None = None) -> bool:
    """-> whether the house's relaunch entry stands: its value in the Run key, or its line in the crontab -- and under
    WSL its value in the Run key as well."""
    if scheduler(system) == "nt":
        return value_name(root) in runkey_read()[0]
    return (any(one.rstrip().endswith(mark_of(root)) for one in table_read()[0])
            and (not wsl_distro(system) or value_name(root) in runkey_read()[0]))


def relaunch_notice(state: dict) -> dict | None:
    """-> the last notice of the season that said the relaunch entry was refused, None when none did."""
    since = int((state["started"] or {}).get("id") or 0)
    said = [one for one in state["messages"].values()
            if one.get("relaunch") and one.get("verb") == "notice" and int(one["id"]) > since]
    return said[-1] if said else None


def relaunch_said(root: Path, conductor, name: str, journal: Path) -> None:
    """Lays the relaunch entry, and SAYS a refusal of the system without failing: on stderr, and ONCE per season as a
    notice of the team to the owner (`relaunch: true`, its `why`, no `about`: it holds no wait); the team runs on its
    timer meanwhile."""
    why = relaunch_laid(root, conductor)
    if not why:
        return
    sys.stderr.write(f"pp-team: {name} · relaunch not laid -- {why}\n")
    state = state_of(journal)
    if relaunch_notice(state) is not None:
        return
    task = next((one["id"] for one in state["tasks"].values() if one["state"] == "open"), None)
    appended(conductor, root, journal, name, [
        {"kind": "post", "task": task, "from": name, "to": str((state["started"] or {}).get("owner")), "verb": "notice",
         "relaunch": True, "why": why,
         "text": (f"the team {name} cannot be relaunched after a restart: the system refused its entry at logon "
                  f"({why}). It runs on its timer until this session ends. To keep it running across a restart, "
                  f"let the user write their Run key (Windows) or start cron (Linux), then start the team again.")}])


def netted(root: Path, conductor, name: str, state: dict) -> None:
    """Lays the team's relaunch entry again when a verb finds it gone and the team needs its net; the timer is armed
    by the tick that follows the verb (`armed`); nothing under `off`."""
    if schedule_seconds(state["started"]) is not None and not netless(state) and not relaunch_standing(root):
        relaunch_said(root, conductor, name, journal_of(root, name))


TIMER_TICKING = False            # set in the timer's own tick: the timer it arms next is no news for the journal


def timer_mark(root: Path, name: str) -> Path:
    return journal_of(root, name).parent / TICK_TIMER


def timer_standing(root: Path, name: str) -> dict:
    """-> the TIMER that stands for the team, `{pid, due, token}` while its process is alive -- the mark beside the
    journal, read and judged by its pid --, {} when none stands or the process is gone."""
    try:
        found = json.loads(timer_mark(root, name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    pid = found.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return {}
    return found if alive(pid) else {}


def alive(pid: int, system: str = os.name) -> bool:
    """-> whether the process `pid` runs. Under Windows the system is asked (`asked_alive`): there `os.kill`
    sends no signal 0, it ends the process. Elsewhere the signal 0, which a process of another user answers
    by a refusal -- alive all the same."""
    if system == "nt":
        return asked_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def asked_alive(pid: int) -> bool:
    """-> whether Windows says the process `pid` runs: `OpenProcess` for its exit code alone, then
    `GetExitCodeProcess` -- `STILL_ACTIVE` while it runs. A process the system refuses to open (another
    user's) runs; one it cannot find has ended."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    handle = kernel.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ctypes.get_last_error() == ERROR_ACCESS_DENIED
    try:
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == STILL_ACTIVE
    finally:
        kernel.CloseHandle(handle)


def apart(system: str = os.name) -> dict:
    """-> the arguments that start a process detached from the caller: under Windows a console of its own that
    no window shows, in a process group of its own -- closing the operator's window ends nothing; elsewhere a
    session of its own, its group, which `ended_now` ends whole."""
    if system == "nt":
        return {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}


def disarmed(root: Path, name: str) -> None:
    """Ends the team's timer, when one stands, and removes its mark: the net leaves with `schedule-off`."""
    standing = timer_standing(root, name)
    if standing:
        ended_now(int(standing["pid"]))
    timer_mark(root, name).unlink(missing_ok=True)


def due_now(state: dict, member: str, clock: datetime) -> bool:
    """-> whether the member is due a launch the tick did not play: idle, no provider's limit holding it, something to
    receive on an open task whose launches are not spent and that does not halt it, the budget not spent -- held by
    `parallel:` or by the budget's rest, launched by a later tick --, or one of its runs standing on an open or a
    resolved task (`standing_of`) that does not halt it."""
    if busy(state, member) or state["budget_spent"] or quota_of(state, member, clock) is not None:
        return False
    if any(halted_of(state, member, task) is None for task in standing_of(state, member)):
        return True
    return any(task not in state["launches_spent"] and halted_of(state, member, task) is None and loud(state, box)
               for task, box in dues(state, member))


def deadline_of(state: dict, clock: datetime, step: int) -> datetime | None:
    """-> the hour the next tick is DUE under the timer, None when nothing is due: a launch under way (its `timeout:`
    when one is declared, else the step), a suspected member within its interval with something to deliver, to
    answer or a run standing (its `until`: a fallen standing run is continued once its interval passed, never at
    the step), a member due but not launched (the step), a member a provider's limit holds (its `until`, however far:
    the limit itself says when to launch it again, so never the step), the next ring of an `every` ceremony or the
    next period of a live recurrence -- the earliest of them, never before the next second. A paused team waits on its launches
    under way alone, and so does a team off season."""
    soon = clock + timedelta(seconds=step)
    due: list[datetime] = []
    timeout = state["limits"].get("timeout")
    for tag in state["intents"]:
        if tag in state["ended"]:
            continue
        launched = state["launched"].get(tag)
        if launched is not None and timeout is not None and launched.get("at"):
            born = datetime.fromisoformat(str(launched["at"])).astimezone().replace(tzinfo=None)
            due.append(min(soon, born + timedelta(seconds=float(timeout))))
        else:
            due.append(soon)
    if not state["paused"] and not state.get("stopped"):
        for member in list((state["started"] or {}).get("agents") or {}):
            suspicion = suspicion_of(state, member)
            if suspicion is not None and clock < suspicion["until"]:
                if (silent_tasks(state, member) or standing_of(state, member)
                        or any(loud(state, box) for _, box in dues(state, member))):
                    due.append(min(soon, suspicion["until"]))
            elif due_now(state, member, clock):
                due.append(soon)
            held = quota_of(state, member, clock)
            if held is not None and held.get("until") is not None:   # its provider's limit ends: launched again
                ends = datetime.fromisoformat(str(held["until"])).astimezone().replace(tzinfo=None)
                due.append(max(ends, clock + timedelta(seconds=1)))
        for ceremony in (state["started"] or {}).get("ceremonies") or []:
            ring = next_due(ceremony, state)
            if ring is not None:
                due.append(max(datetime.fromisoformat(ring), clock + timedelta(seconds=1)))
        for recurrence in live_recurrences(state):
            sound = recurrence_next(recurrence)
            if sound is not None:
                due.append(max(datetime.fromisoformat(sound), clock + timedelta(seconds=1)))
    return max(min(due), clock + timedelta(seconds=1)) if due else None


def armed(root: Path, conductor, name: str, journal: Path) -> int:
    """The TIMER, under any `schedule:` but `off`, armed by the tick at the start of each round and again at its
    step 7 -- a tick killed between the two leaves the first standing. When the state leaves a deadline (`deadline_of`),
    ONE process is spawned detached -- this script, `timer <name> --token <t>`, outside the console: it holds no hold
    on the machine while it sleeps until that hour, then plays one tick by the house's console and dies --, and the mark beside the journal says `{pid, due, token}`: the pid of the process spawned (uv's
    launcher under Windows, alive while the timer lives: the test of life and the root of the tree a stop ends), its
    hour, and the TOKEN the timer knows itself by; the journal is read again once the mark is written, and a team
    that no longer needs its net (a `stop` wrote and disarmed meanwhile, outside the tick's lock) is disarmed at once;
    a timer standing for an hour no later
    than the new one is kept, a later one ended and replaced; nothing is spawned when nothing is due. `timer-armed {due}` is
    written when a tick arms a timer where none stood -- once: the arming of step 7 finds the one of the round's
    start standing; the timer's own tick, which arms the next, writes nothing. -> the events written."""
    state = state_of(journal)
    seconds = schedule_seconds(state["started"])
    if seconds is None or netless(state):
        return 0
    clock = tick_now()
    due = deadline_of(state, clock, seconds)
    if due is None:
        return 0
    standing = timer_standing(root, name)
    if standing:
        try:
            if datetime.fromisoformat(str(standing.get("due"))) <= due:
                return 0                                         # a timer stands for an hour no later: kept
        except ValueError:
            pass
        ended_now(int(standing["pid"]))
    if not timer_spawned(root, name, journal, clock, due):
        return 0
    if standing or TIMER_TICKING:
        return 0
    return len(appended(conductor, root, journal, name, [{"kind": "timer-armed", "due": due.isoformat(timespec="seconds")}]))


def timer_spawned(root: Path, name: str, journal: Path, clock: datetime, due: datetime) -> bool:
    """Spawns ONE timer for `due` -- this script, `timer <name> --token <t>`, detached, its output in the follow log --
    and writes its mark `{pid, due, token}`; the journal is read again once the mark is written, and a team that no
    longer needs its net (a `stop` wrote and disarmed meanwhile, outside the tick's lock) is disarmed at once. -> whether
    the timer stands."""
    wait = max(0.0, (due - clock).total_seconds())
    token = secrets.token_hex(8)
    log = journal.parent / FOLLOW_LOG
    with log.open("ab") as handle:                # the skill itself, never the console: no hold on the machine while it sleeps
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "timer", name,
                                  "--sleep", f"{wait:.3f}", "--due", due.isoformat(timespec="seconds"),
                                  "--token", token],
                                 stdin=subprocess.DEVNULL, stdout=handle, stderr=handle, cwd=str(root.parent),
                                 env={**os.environ, "PP_HOME": str(root)}, **apart())
    mark = timer_mark(root, name)
    temporary = mark.with_name(f".{mark.name}.{os.getpid()}")
    temporary.write_text(json.dumps({"pid": child.pid, "due": due.isoformat(timespec="seconds"), "token": token}),
                         encoding="utf-8")
    os.replace(temporary, mark)
    if netless(state_of(journal)):                 # a verb that leaves the net (a stop) wrote and disarmed while this
        disarmed(root, name)                       # tick spawned: read again after the mark, the timer leaves with it
        return False
    return True


def timer_verb(rest: list[str]) -> int:
    """`team timer <name> --sleep <seconds> --due <local date-time> --token <token>`: the TIMER's own process, spawned
    by the tick (`armed`) as this script itself, outside the console: it holds no hold on the machine while it sleeps,
    and a maintenance plays meanwhile. It knows itself by the TOKEN the tick handed it, never by a pid: under Windows
    uv's launcher stands between the process the tick spawned and the Python that plays this script. It waits for its
    mark to carry its token (TIMER_WAIT at most: a mark the tick never wrote, it leaves). Then it sleeps until the
    first of two moments: `--sleep` seconds have passed, or the wall clock (`tick_now`) reaches `--due` -- the wall
    clock counts the time the machine slept, a monotonic clock does not. It leaves at once when its mark no longer
    carries its token: disarmed, or replaced by a timer due earlier. Then it takes its mark away and plays ONE tick by
    the house's console (`ticked_by_console`), which arms the next timer when a deadline still stands; a tick that
    FAILS and leaves no timer standing, the timer arms the next itself (`timer_relayed`). Then it dies: no process
    outlives its deadline."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, {"sleep": True, "due": True, "token": True})
    if not asked["token"]:
        refuse(USAGE)
    try:
        left = float(asked["sleep"] or "")
    except ValueError:
        refuse(USAGE)
    try:
        due = datetime.fromisoformat(asked["due"]) if asked["due"] else None
    except ValueError:
        refuse(USAGE)
    if due is not None and due.tzinfo is not None:
        due = due.astimezone().replace(tzinfo=None)
    mark = timer_mark(root, name)
    token = asked["token"]
    named_at = time.monotonic() + TIMER_WAIT
    while timer_standing(root, name).get("token") != token:
        if time.monotonic() >= named_at:
            return 0                                             # never named: not the team's timer
        time.sleep(0.05)
    deadline = time.monotonic() + max(0.0, left)
    while time.monotonic() < deadline and (due is None or tick_now() < due):
        if timer_standing(root, name).get("token") != token:
            return 0                                             # disarmed, or replaced
        time.sleep(min(0.5, max(0.0, deadline - time.monotonic())))
    if timer_standing(root, name).get("token") == token:
        mark.unlink(missing_ok=True)
    played = ticked_by_console(root, conductor, name)
    if played.returncode != 0:
        timer_relayed(root, conductor, name, played.stderr)
    return played.returncode


def timer_relayed(root: Path, conductor, name: str, said: str) -> None:
    """The timer whose tick FAILED before its net (step 7) armed the next: when no timer stands after it and the team
    still needs its net (`schedule:` not `off`, not `netless`, no delete begun), ONE timer is armed at the team's step
    -- under the tick's lock taken without waiting: a tick that holds it arms its own --, and the owner is told ONCE
    per season (a `notice`, `timer: true`, the tick's stderr as its `why`, clipped, no `about`: it holds no wait). The
    notice is written on the journal that stands, the declaration away or not: a tick that fails `team-unknown` is
    told as any other. A team whose `deleting` stands gets neither a timer nor a notice, its declaration standing or
    gone: a delete is finishing it."""
    journal = journal_of(root, name)
    lock = locks(conductor)
    lease = lock.try_(journal.parent / TICK_LOCK)
    if lease is None:
        return
    try:
        state = state_of(journal)
        seconds = schedule_seconds(state["started"])
        if seconds is None or netless(state) or state["deleting"] or timer_standing(root, name):
            return
        clock = tick_now()
        if not timer_spawned(root, name, journal, clock, clock + timedelta(seconds=seconds)):
            return
        state = state_of(journal)
        since = int((state["started"] or {}).get("id") or 0)
        if any(one.get("timer") and one.get("verb") == "notice" and int(one["id"]) > since
               for one in state["messages"].values()):
            return
        why = " ".join(str(said or "").split())[-300:] or "no output"
        task = next((one["id"] for one in state["tasks"].values() if one["state"] == "open"), None)
        appended(conductor, root, journal, name, [
            {"kind": "post", "task": task, "from": name, "to": str((state["started"] or {}).get("owner")),
             "verb": "notice", "timer": True, "why": why,
             "text": f"the team {name}'s timer played a tick that failed ({why}); the next timer is armed at the "
                     f"step, {seconds} s: the team ticks on, and this is said once this season."}],
            undeclared=True)
    finally:
        lock.release(lease)


def ticked_by_console(root: Path, conductor, name: str) -> subprocess.CompletedProcess:
    """The timer's tick, played by the house's console -- a process of its own under the machine's shared hold, the
    engine and this package as the machine holds them at that hour (after an upgrade, the new ones) --, marked by
    `TIMER_ENV`; a tick the console refuses `maintenance-in-progress` is played again every TIMER_RETRY seconds,
    TIMER_RETRIES times at most, then said, a failure as any other: the timer arms the next (`timer_relayed`). -> the
    tick played: its exit code and its stderr."""
    argv = [sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "team", "tick", name]
    played = None
    for _ in range(TIMER_RETRIES + 1):
        played = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=str(root.parent),
                                env={**os.environ, TIMER_ENV: "1"})
        if "maintenance-in-progress" not in played.stderr:
            break
        time.sleep(TIMER_RETRY)
    sys.stdout.write(played.stdout)
    sys.stderr.write(played.stderr)
    if "maintenance-in-progress" in played.stderr:
        sys.stderr.write(f"pp-team: {name} · the timer's tick met a maintenance {TIMER_RETRIES} times -- "
                         "the next timer is armed at the step\n")
    return played


def netless(state: dict) -> bool:
    """-> whether the team no longer needs its net: started, and off season or with no task open, no ceremony
    declared, no recurrence live -- the condition under which `schedule-off` is written."""
    started = state["started"]
    if started is not None and state.get("stopped"):
        return True
    return (started is not None
            and not any(one["state"] == "open" for one in state["tasks"].values())
            and not (started.get("ceremonies") or [])
            and not live_recurrences(state))


# --- the tick: one advance of the team ------------------------------------------------------

def launch_flags(launch: dict) -> list[str]:
    """-> the flags `agent start` gets from what `team start` kept: the harness or the
    provider, the model, the budget, the permission regime, the model's effort. A wake-up is ONE
    launch: `--launches 1` rides every call, never a flag of the start."""
    found: list[str] = []
    for key, flag in (("harness", "--harness"), ("provider", "--provider"), ("model", "--model"),
                      ("max_budget_usd", "--max-budget-usd"), ("permissions", "--permissions"),
                      ("effort", "--effort")):
        if launch.get(key) is not None:
            found += [flag, str(launch[key])]
    return found + ["--launches", "1"]


def cursor_of(state: dict, agent: str, run: str | None, before: int) -> int:
    """-> the RUN's cursor in the team: the id of the last `wake-intent` of that run before the
    one being written (`before`) -- an intent that resumed it, or the one that opened it --, or
    the `team-started` for a new run: a new session knows nothing. The cursor is the journal's:
    nothing is written to share."""
    mine = [int(one.get("id") or 0) for tag, one in state["intents"].items()
            if run is not None and one.get("agent") == agent and int(one.get("id") or 0) < before
            and (one.get("run") == run or (state["launched"].get(tag) or {}).get("run") == run)]
    return max(mine or [int((state["started"] or {}).get("id") or 0)])


def shared(state: dict, agent: str, cursor: int) -> list[dict]:
    """-> the `wake-ended` events of OTHER agents after the cursor: the responses new to the
    agent, in the journal's order."""
    return [one for one in state["ends"] if int(one.get("id") or 0) > cursor and one.get("agent") != agent]


def clipped(text) -> str:
    """-> a message's text as a history line carries it: HISTORY_CHARS at most."""
    text = str(text or "")
    return text if len(text) <= HISTORY_CHARS else text[:HISTORY_CHARS - 1] + "…"


def history_of(state: dict, agent: str, task: str) -> str:
    """-> what a NEW run must be told of a task the member already worked: the messages
    delivered to the member on the task, then the posts its answers made there, one line each,
    under `[history of <task> for <agent>]` -- or '' when the member has no past on the task.
    The texts are clipped; `team responses` reads the answers whole."""
    told = [f"#{one['id']} {one.get('verb')} from {one.get('from')}: {clipped(one.get('text'))}".rstrip()
            for one in state["messages"].values()
            if one.get("to") == agent and one.get("task") == task and one["id"] in state["delivered"]]
    said = [f"#{one['id']} {one.get('verb')} to {one.get('to')}: {clipped(one.get('text'))}".rstrip()
            for one in state["messages"].values() if one.get("from") == agent and one.get("task") == task]
    if not told and not said:
        return ""
    return f"[history of {task} for {agent}]\n" + "\n".join(told + said)


def histories_of(state: dict, member: str, task: str) -> str:
    """-> what a NEW run of a member must be told: the history of the open tasks of the task's CARRIER -- the
    task alone, or the open occurrences of a recurrence, the open rings of a ceremony --, in the tasks' order;
    '' when the member has no past there."""
    carrier = carrier_of(state, task)
    return "\n\n".join(one for one in (history_of(state, member, other) for other, held in state["tasks"].items()
                                       if held.get("state") == "open" and carrier_of(state, other) == carrier) if one)


def message_of(state: dict, agent: str, one: dict) -> str:
    """-> a message as a wake-up's head shows it: `#163 DO from supervisor on T8 -- you owe an answer`, the
    kind in capitals and the id an answer cites (`RE #175`); the debt said while it stands -- and, for the
    opening of a task the member holds, that its answer closes the task --; the text indented under it. A `re` the
    tick wrote in a member's place (`by: tick`) hands the message it cites back to its author. A first line says that
    the team wrote the answer, why (`ANSWERED_FOR`: the member never received the message under `returned`, was
    given it and did not answer under `suspected`; under neither field the launch that carried the message failed --
    dead after it carried it, or refused before it reached the member), that the message is closed and how to send
    it again. Then comes the tick's text, then the message cited -- its number, its
    vector when it carries one, its whole text (`HANDED_BACK`, `HANDED_BACK_VECTOR`) --, composed from the journal's
    message: nothing is copied into the `re`."""
    cited = cited_of(state, one)
    head = (f"#{one['id']} {str(one.get('verb') or '').upper()}" + (f" #{cited}" if cited is not None else "")
            + f" from {one.get('from')} on {one.get('task')}")
    if owes(state, one["id"]) and one.get("to") == agent:
        head += f" -- {OWED}"
        if one["id"] == opening_of(state, one.get("task")):
            head += f", and your answer to it closes {one.get('task')}"
    text = str(one.get("text") or "")
    said, back = [], []
    message = state["messages"].get(cited) if one.get("by") == "tick" and one.get("verb") == "re" else None
    if message is not None:
        how = "returned" if one.get("returned") else "suspected" if one.get("suspected") else "failed"
        said = [ANSWERED_FOR[how].format(member=one.get("from"), id=cited)]
        vector = message.get("vector")
        back = [HANDED_BACK_VECTOR.format(id=cited, vector=vector) if vector else HANDED_BACK.format(id=cited),
                *(f"  {line}" for line in str(message.get("text") or "").splitlines())]
    return head + "".join(f"\n  {line}" for line in [*said, *text.splitlines(), *back])


def headed(team: str, agent: str, box: list[dict], history: str = "", state: dict | None = None,
           relance: tuple[str, str | None] | None = None, task: str | None = None, continued: bool = False,
           beat: int | None = None) -> str:
    """-> the HEAD of a launch, what the tick writes before pp's output in the prompt. A WAKE-UP alone says what
    holds for its whole passage: its first line, who is launched (`IDENTITY`); for a NEW run of a member that had
    one, the history of its open tasks; for a RELANCE, the line that says why the member is launched -- `RELANCED`,
    or, in a cycle of waits, `CYCLED` naming the member it waits on: an answer or an info asked --; and the BEAT
    (`BEAT`: the exchanges left to say an act on the task, this one counted) of a member that owes there. EVERY
    head, a CONTINUATION's (`continued`) included, says what varies: the HEALTH VIEW while another member is
    suspected, one line each (`[not answering at the moment: <member> -- tried again at HH:MM]`); then the inbox --
    what arrived for the member since its last launch, each message its head line and its text under it
    (`message_of`), a relance's the members' infos that waited --, or `[nothing new]` when a standing run is
    relaunched with nothing to deliver -- `CLOSED_HEAD` when its task is resolved: no act is awaited, one said
    reaches its author as a second answer does --; a `stop` at the head of a run standing on the stopped task opens
    on `STOPPED_HEAD`: the run says no act and parks; then the messages delivered at an earlier launch that the
    member still owes an answer on the TASK of the launch (every open task when none is named), under `[you still
    owe an answer to]`. Nothing else -- what the others answered is read on demand (`team responses`) --: the
    contract of the acts is the body of the team's document, served by pp at the start of the member's exchange,
    and the team's intention is never in the message: pp serves it from `TEAM.md` (`team_document`)."""
    state = state if state is not None else {"messages": {}, "debts": {}, "tasks": {}, "started": None}
    health = health_lines(state, agent)
    shown = {one["id"] for one in box}
    lines = [message_of(state, agent, one) for one in box]
    still = [message_of(state, agent, one) for key, one in sorted(state["messages"].items())
             if key not in shown and one.get("to") == agent and owes(state, key) and key in state.get("delivered", ())
             and is_open(state, one.get("task")) and (task is None or one.get("task") == task)]
    first = "" if continued else IDENTITY.format(team=team, member=agent) + "\n\n"
    told = history + "\n\n" if history and not continued else ""
    left = BEAT.format(left=beat, task=task) + "\n\n" if beat is not None and not continued else ""
    if relance is not None and not continued:
        why = RELANCED if relance[1] is None else CYCLED.format(member=relance[1])
        inboxed = why + "\n\n" + left + ("[inbox]\n" + "\n".join(lines) + "\n\n" if lines else "")
    elif lines:
        inboxed = left + "[inbox]\n" + "\n".join(lines) + "\n\n"
        if any(one.get("verb") == "stop" for one in box):      # a run standing on a stopped task: its last launch
            inboxed = STOPPED_HEAD + "\n\n" + inboxed
    elif (state["tasks"].get(task) or {}).get("state") == "resolved":   # a run standing on a closed task, continued
        inboxed = CLOSED_HEAD + "\n\n"
    else:
        inboxed = left + NOTHING_NEW + "\n\n"
    return (first + (health + "\n\n" if health else "") + told + inboxed
            + ("[you still owe an answer to]\n" + "\n".join(still) + "\n\n" if still else "")).rstrip("\n") + "\n"


def spent_on(state: dict, run: str) -> float:
    """-> what the run spent in the team's wake-ups, as the journal charged them: the sum of the costs
    of its ends and failures -- what `agent start --max-budget-usd` gets added to a wake-up's share."""
    return round(sum(float(one.get("cost") or 0) for one in state["ends"] + state["fails"]
                     if one.get("run") == run), 6)


ACT_OPENED = re.compile(r'\{\s*"(?:do|ask|re|info)"\s*:')   # an object that opens on the key of a form


def candidates_of(text: str) -> list[tuple[list | None, str]]:
    """-> the CANDIDATES a `words` carries, in their order: each JSON value found in its text -- the text alone,
    a sentence around it, a ``` block, several values -- that is an object, or a list of objects, with a key of
    a form (`do`, `ask`, `re`, `info`) at its first level, as `(elements, "")`; and each object opened on such a key
    that does not read as JSON, as `(None, why)`. Anything else is SAID: prose, a table, a JSON value without
    the key of a form, a verb of an answer before team 0.33.0 (`done`, `reply`, `escalate`) -- nothing of it
    is a candidate. A value read is never searched inside: what it holds is its own."""
    decoder, found, spans, at = json.JSONDecoder(), [], [], 0
    while True:
        starts = [one for one in (text.find("{", at), text.find("[", at)) if one >= 0]
        if not starts:
            break
        start = min(starts)
        try:
            value, end = decoder.raw_decode(text, start)
        except ValueError:
            at = start + 1
            continue
        if not isinstance(value, (dict, list)):
            at = start + 1
            continue
        spans.append((start, end))
        elements = [value] if isinstance(value, dict) else value
        if elements and all(isinstance(one, dict) for one in elements) and any(
                form in one for one in elements for form in ELEMENTS):
            found.append((start, elements, ""))
        at = end
    for opened in ACT_OPENED.finditer(text):
        if not any(start <= opened.start() < end for start, end in spans):
            found.append((opened.start(), None, f"`{text[opened.start():opened.start() + 40]}` is no JSON value: "
                                                "an act is one JSON object, or a list of them, written whole"))
    return [(elements, why) for _, elements, why in sorted(found, key=lambda one: one[0])]


def act_formed(elements: list) -> None:
    """Judges the FORM of a candidate before its sense: every element an object of ONE form, no key beyond
    that form's, its values of their kind -- `do` an object of member -> work or a list of members, `ask` and
    `info` an object of `to` and `text` or a text, `re` the id of a message and a text. A fault raises `Refused`
    with its reason."""
    for one in elements:
        if not isinstance(one, dict):
            raise Refused(f"{json.dumps(one)[:40]} is not an object: each element of an act is one object")
        forms = [form for form in ELEMENTS if form in one]
        if len(forms) != 1:
            raise Refused(f"an element carries {' and '.join(forms) or 'none'} of the forms do, ask, re, info: "
                          "it carries exactly one")
        form = forms[0]
        extra = sorted(set(one) - ELEMENTS[form])
        if extra:
            raise Refused(f"the key `{extra[0]}` does not belong to the form `{form}`, whose keys are "
                          + ", ".join(f"`{key}`" for key in sorted(ELEMENTS[form])))
        said = one[form]
        if form == "do" and not (
                (isinstance(said, dict) and said and all(isinstance(key, str) and (isinstance(work, str) or (
                    isinstance(work, dict) and isinstance(work.get("text"), str) and not set(work) - {"text", "vector"}))
                                                         for key, work in said.items()))
                or (isinstance(said, list) and said and all(isinstance(name, str) for name in said))):
            raise Refused(f"do {json.dumps(said)[:40]}: the form is {{\"<member>\": \"<the work>\"}}, "
                          "{\"<member>\": {\"text\": \"<the work>\", \"vector\": \"<family>:<id>\"}} or a list of members")
        if form == "do" and isinstance(said, dict):
            for work in said.values():
                if isinstance(work, dict) and "vector" in work and not vector_formed(work["vector"]):
                    raise Refused(f"vector-invalid -- do {json.dumps(work['vector'])[:40]}: a vector is "
                                  "`<family>:<id>`")
        if form == "ask" and not (isinstance(said, str) or (
                isinstance(said, dict) and not set(said) - {"to", "text"}
                and all(isinstance(value, str) for value in said.values()))):
            raise Refused(f"ask {json.dumps(said)[:40]}: the form is {{\"to\": \"<member>\", \"text\": \"...\"}}")
        if form == "info" and not (isinstance(said, str) or (
                isinstance(said, dict) and not set(said) - {"to", "text"}
                and all(isinstance(value, str) for value in said.values()))):
            raise Refused(f"info {json.dumps(said)[:40]}: the form is {{\"to\": \"<member or principal>\", \"text\": \"...\"}}")
        if form == "re" and (cited_id(said) is None or not isinstance(one.get("text", ""), str)):
            raise Refused(f"re {json.dumps(said)[:40]}: the form is {{\"re\": <the message number>, \"text\": \"...\"}}")


class Refused(Exception):
    """An act the tick refuses to route, said to the member: its form broken (`act_formed`, `candidates_of`) or its
    sense wrong -- a member nobody declared, a `do` off the edges, a `re` citing a message never delivered to the
    member."""


def resolution(state: dict, task: str, result) -> list[dict]:
    """-> what closes a task the root answered: `done` with the result, a `returned` for every post to an agent
    left undelivered on it, `schedule-off` when no task stays open, no ceremony is declared and no recurrence lives."""
    events: list[dict] = [{"kind": "done", "task": task, "result": result}]
    for one in state["messages"].values():
        if one.get("task") == task and one["id"] not in state["delivered"]:
            events.append({"kind": "returned", "message": one["id"], "to": one.get("from")})
    others_open = [one for one in state["tasks"].values() if one["id"] != task and one["state"] == "open"]
    if (not others_open and not ((state["started"] or {}).get("ceremonies") or []) and not live_recurrences(state)
            and state["schedule"]):
        events.append({"kind": "schedule-off"})
    return events


def cited_id(said) -> int | None:
    """-> the id a `re` names -- `12` or `"#12"` --, None for any other value."""
    if isinstance(said, bool):
        return None
    if isinstance(said, int):
        return said
    text = str(said).strip().lstrip("#")
    return int(text) if text.isdigit() else None


def routed(state: dict, intent: dict, elements: list[dict], settled: set | None = None,
           closed: set | None = None) -> list[dict]:
    """-> the events an ACT writes: its ELEMENTS as posts, in their order -- a `do` to each member named that
    reports to the acting one, an `ask` to any member of the team or
    to a principal, an answer `{"re": <id>}` to the author of the message it cites, on that message's task,
    an `info` to any member or principal (the parent on the task when it names nobody): no debt, off
    every edge (row 114). The first answer to a `do` or an `ask` settles its debt; a later one is posted `info:
    true`. The ROOT's answer to its task's opening resolves the task (`resolution`). Refused, nothing written: a
    member nobody declared, a `do` off the edges, a `re` citing a message never delivered to the member or
    citing an `info`. `settled` and `closed` carry what the acts said before it in the
    same `words` settled and closed."""
    agent, task = intent["agent"], intent["task"]
    events: list[dict] = []
    held = state["tasks"].get(task) or {}
    edges = edges_of(state, task)
    settled = set() if settled is None else settled
    closed = set() if closed is None else closed
    for one in elements:
        form = next(form for form in ELEMENTS if form in one)
        if form == "do":
            asked = one["do"]
            pairs = list(asked.items()) if isinstance(asked, dict) else [(name, held.get("text") or "")
                                                                          for name in (asked or [])]
            for target, work in pairs:
                if not is_member(state, target):
                    raise Refused(f"do names `{target}`, a member nobody declared")
                if (target, agent) not in edges:
                    raise Refused(f"do names `{target}`, off the edges: `{target}` does not report to `{agent}`")
                text, vector = (work.get("text"), work.get("vector")) if isinstance(work, dict) else (work, None)
                events.append({"kind": "post", "task": task, "from": agent, "to": target, "verb": "do",
                               "text": str(text), **({"vector": vector} if vector else {})})
        elif form == "ask":
            asked = one["ask"] if isinstance(one["ask"], dict) else {"text": one["ask"]}
            target = asked.get("to") or parent_of(state, agent, task)
            if not is_member(state, target) and not is_principal(state, target):
                raise Refused(f"ask names `{target}`, a member nobody declared")
            events.append({"kind": "post", "task": task, "from": agent, "to": target, "verb": "ask",
                           "text": str(asked.get("text") or "")})
        elif form == "info":
            said = one["info"] if isinstance(one["info"], dict) else {"text": one["info"]}
            target = said.get("to") or parent_of(state, agent, task)
            if not is_member(state, target) and not is_principal(state, target):
                raise Refused(f"info names `{target}`, a member nobody declared")
            events.append({"kind": "post", "task": task, "from": agent, "to": target, "verb": "info",
                           "text": str(said.get("text") or "")})
        else:
            cited = cited_id(one["re"])
            answered = state["messages"].get(cited) if cited is not None else None
            if answered is None or answered.get("to") != agent or cited not in state["delivered"]:
                raise Refused(f"re #{str(one['re']).lstrip('#')}: no message #{str(one['re']).lstrip('#')} "
                              f"was delivered to `{agent}`")
            if answered.get("verb") == "info":
                raise Refused(f"re #{cited} answers an info: an info owes nothing, nobody answers it")
            on = answered.get("task")
            due = owes(state, cited) and cited not in settled and on not in closed
            post = {"kind": "post", "task": on, "from": agent, "to": answered.get("from"), "verb": "re",
                    "re": cited, "text": str(one.get("text") or "")}
            if not due:
                post["info"] = True
            events.append(post)
            if due:
                settled.add(cited)
                if cited == opening_of(state, on) and is_root(state, agent, on):
                    closed.add(on)
                    events += resolution(state, on, post["text"])
    return events


# --- the flow of a launch: read by agent's face, routed as it comes ------------------------------

def flow_lines(root: Path, conductor, path: str, run: str, start: int) -> list[tuple[int, dict]]:
    """-> the lines of the run's flow from the rank `start` on (the first line is 1), each with its rank,
    read by the house's own console: `agent flow <path> <run> --json --from <start>` -- the one way the
    tick reads what a launch says, never the file. A console that refuses (a run the agent forgot)
    reads as nothing."""
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                             "--json", "--from", str(max(1, start))], capture_output=True, text=True,
                            cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return []
    found = []
    for offset, line in enumerate(played.stdout.splitlines()):
        if not line.strip():
            continue
        try:
            found.append((max(1, start) + offset, json.loads(line)))
        except ValueError:
            continue
    return found


def act_routed(conductor, root: Path, journal: Path, name: str, tag: str, rank: int, ordinal: int, text: str) -> list[dict]:
    """ONE `words` of a launch, routed under the journal's lock -- once: a `wake-routed` of the tag at
    that rank standing, nothing is written again (the follower and the tick read the same flow). Each
    CANDIDATE the `words` carries (`candidates_of`) is judged in its order, whole or not at all: one whose
    form and sense are right writes `wake-routed {tag, agent, run, launch, words, line}` then its posts; one
    whose form is broken (`act_formed`) or whose sense is wrong writes `wake-refused {…, why}` and an `info` to the
    member; on a stopped task each goes nowhere (`wake-routed` with `nowhere`); a `words` without a candidate
    writes nothing. -> the events written."""
    found = candidates_of(text)
    if not found:
        return []

    def judge(state: dict, events: list[dict]) -> list[dict]:
        intent = state["intents"].get(tag)
        launch = state["launched"].get(tag) or {}
        if intent is None or rank <= int(state["routed"].get(tag) or 0):
            return []
        marked = {"kind": "wake-routed", "tag": tag, "agent": intent["agent"], "run": launch.get("run"),
                  "launch": launch.get("launch"), "words": ordinal, "line": rank}
        if (state["tasks"].get(intent["task"]) or {}).get("state") == "stopped":
            return [{**marked, "nowhere": True} for _ in found]
        written_now: list[dict] = []
        settled: set = set()
        closed: set = set()
        for elements, broken in found:
            try:
                if elements is None:
                    raise Refused(broken)
                act_formed(elements)
                written_now += [marked, *routed(state, intent, elements, settled, closed)]
            except Refused as why:
                written_now += [{**marked, "kind": "wake-refused", "why": str(why)},
                                {"kind": "post", "task": intent["task"], "from": name, "to": intent["agent"],
                                 "verb": "info", "text": f"your act was refused: {why}"}]
        return written_now
    return written(conductor, root, journal, name, judge)


def opened_by(one: dict, tag: str) -> bool:
    """-> whether a line of a flow OPENS the launch's own exchange: an `opened` carrying the tag the tick handed
    `agent start` (agent 0.31.1) -- what the reader starts at, never a kept rank alone; an `opened` of another
    exchange (a chat, a launch of before) closes what is read."""
    return one.get("kind") == "opened" and str(one.get("tag") or "") == tag


def flow_read(root: Path, conductor, name: str, journal: Path, tag: str) -> dict:
    """Reads the flow of the launch `tag` from the rank the journal last kept of the run (from 1 when it kept
    none), finds the exchange the launch OPENED by its tag (`opened_by`) and routes every `words` of that
    exchange that reads as an act, in order (`act_routed`); nothing before that `opened` is routed. -> what the
    flow said of the launch's END: `{"ended", "response", "verdict", "cost", "context", "rank"}` -- `ended` once its
    `verdict` line stands (the house wrote the end of the exchange before it gave the wake lock back), `response`
    the `response` line's fields when one was kept, `cost` the sum of the `agent` events' costs, `context` the last
    `context` the exchange said (`measured_of`), `rank` the last line read. Nothing written beyond the routing."""
    state = state_of(journal)
    intent, launch = state["intents"].get(tag) or {}, state["launched"].get(tag) or {}
    run, path = str(launch.get("run") or ""), path_of_intent(state, intent)
    told = {"ended": False, "response": None, "verdict": None, "cost": 0.0, "context": None,
            "rank": int(state["flow"].get(run) or 0)}
    if not run:
        return told
    ordinal, opened = 0, False
    for rank, one in flow_lines(root, conductor, path, run, told["rank"] + 1):
        kind = one.get("kind")
        told["rank"] = rank
        if kind == "opened":                       # the launch's own exchange opens here, by its tag: what
            ordinal, opened = 0, opened_by(one, tag)   # stands before it is an earlier one's, never routed
        if not opened:
            continue
        if kind == "words":
            ordinal += 1
            act_routed(conductor, root, journal, name, tag, rank, ordinal, str(one.get("text") or ""))
        elif kind == "agent":
            cost = one.get("cost_usd")
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                told["cost"] = round(told["cost"] + float(cost), 6)
        elif kind == "context":
            told["context"] = measured_of(one)
        elif kind == "response":
            told["response"] = one
        elif kind == "verdict":
            told["verdict"], told["ended"] = one, True
            break
    return told


def measured_of(one: dict) -> dict:
    """-> a flow's `context` object as the journal keeps it, `{tokens, used, window}` as the house said them."""
    return {key: one.get(key) for key in ("tokens", "used", "window")}


def followed(root: Path, conductor, name: str, journal: Path, tag: str) -> int:
    """`team follow <name> <tag>`: the FOLLOWER of one launch -- keeps ONE `agent flow <path> <run> --json
    --from <rank> --follow` open on the launch's flow, from the rank the journal last kept of the run (from 1
    when it kept none), finds the exchange the launch OPENED by its tag (`opened_by`) and reads what it
    streams line by line: each `words` of that exchange that is an act routed as it comes (`act_routed`, once
    by its rank), the team ticked after it (an act may wake another member); at the exchange's `verdict` the
    launch's END is written (`ended_from_flow`) and the team ticked, and the follower leaves -- as it does when
    the stream ends (no launch plays and nothing comes), or when the intent is ended in the journal. A stream
    that ends at the `verdict` of an EARLIER exchange, before the launch's `opened`, is opened again from the
    rank reached while the launch's wake lock is held. Spawned detached by the tick at every launch, outside
    the tick's lock. -> the acts it routed."""
    state = state_of(journal)
    intent, launch = state["intents"].get(tag), state["launched"].get(tag) or {}
    run = str(launch.get("run") or "")
    if intent is None or not run or tag in state["ended"]:
        return 0
    path = path_of_intent(state, intent)
    engine = engine_of(root, conductor)
    told = {"ended": False, "response": None, "verdict": None, "cost": 0.0, "context": None,
            "rank": int(state["flow"].get(run) or 0)}
    routed_count, ordinal, opened = 0, 0, False
    while True:
        start = told["rank"] + 1
        stream = subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                                   "--json", "--from", str(start), "--follow"],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, cwd=str(root.parent),
                                  env=dict(os.environ))
        assert stream.stdout is not None
        for rank, line in enumerate(stream.stdout, start):
            if not line.strip():
                continue
            try:
                one = json.loads(line)
            except ValueError:
                continue
            kind = one.get("kind")
            told["rank"] = rank
            if kind == "opened":                   # the launch's own exchange opens here, by its tag: what
                ordinal, opened = 0, opened_by(one, tag)   # stands before it is an earlier one's, never routed
            if not opened:
                continue
            if kind == "words":
                ordinal += 1
                if act_routed(conductor, root, journal, name, tag, rank, ordinal, str(one.get("text") or "")):
                    routed_count += 1
                    ticked(root, conductor, name)
            elif kind == "agent":
                cost = one.get("cost_usd")
                if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                    told["cost"] = round(told["cost"] + float(cost), 6)
            elif kind == "context":
                told["context"] = measured_of(one)
            elif kind == "response":
                told["response"] = one
            elif kind == "verdict":
                told["verdict"], told["ended"] = one, True
                break
        stream.stdout.close()
        stream.wait()
        if told["ended"] or opened or not held_run(root, conductor, path, run):
            break                                  # over; or the launch's exchange seen or gone: the reap reads on
    if told["ended"]:                               # the launch is over: its end written here, the tick after
        state = state_of(journal)
        if tag not in state["ended"] and tag in state["intents"]:
            ending(conductor, root, journal, name, tag,
                   ended_from_flow(state, state["intents"][tag], state["launched"].get(tag) or {}, told, None,
                                   (None, False) if told.get("response") else awaits_of(root, conductor, path, run)))
        ticked(root, conductor, name)
    return routed_count


def follow(rest: list[str]) -> int:
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    journal = journal_of(root, name)
    if not journal.is_file():
        refuse(f"team-not-started -- {name} was never started.")
    count = followed(root, conductor, name, journal, rest[0])
    print(f"pp-team: {name} · follow {rest[0]} · {count} act(s) routed")
    return 0


def following(root: Path, conductor, name: str, tag: str) -> None:
    """Spawns the follower of the launch `tag`, detached -- its own session, its output appended to
    `follow.log` beside the journal --: the tick that launched it goes on."""
    engine = engine_of(root, conductor)
    log = journal_of(root, name).parent / FOLLOW_LOG
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("ab") as handle:
        subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "team", "follow", name, tag],
                         stdin=subprocess.DEVNULL, stdout=handle, stderr=handle, cwd=str(root.parent),
                         env=dict(os.environ), **apart())


def failed(state: dict, intent: dict, reason: str, cost=None, run: str | None = None,
           extra: dict | None = None, forced: bool = False) -> list[dict]:
    """-> the events a dead wake-up writes: `wake-failed` -- a retry left: its messages go back
    to the inbox (the replay discards them from the delivered); spent: `final`, and the tick ANSWERS
    in the member's place each message of the wake-up whose debt stands (`re`, `by: tick`, neither `suspected` nor
    `returned`, « the launch of <member> failed: <reason> »), which wakes their authors: a member's head
    shows the message whole (`message_of`), a principal reads the `re` in its box, without the message --
    never the opening a principal posted:
    the root's debt stays owed and the team tells its principal (a `notice` about the root). On a stopped task it is
    `final` at once and goes nowhere.
    A `launch-missing` -- a tick died between the intent and the spawn -- is never final and
    spends no retry: nothing was launched. A wake-up that answered before it failed carries the
    `cost` its answer reported, and the `run` that answered when the answer was conducted -- or the run the
    face knows the state of (`state`, read at agent's face: `standing` or `parked`): that run
    stays the member's, and the retry resumes it. `extra` joins the event's fields (the rank of the flow
    read). A member that repented is
    tolerated one silent retry more per repentance; a SUSPECTED member's failure -- its try -- is final at once;
    `forced` makes it final at once whatever the retries (a launch the launcher refused its vectors). The same failure
    HALT_AFTER times in a row on the task halts the member there (`halting`)."""
    agent, task = intent["agent"], intent["task"]
    stopped = (state["tasks"].get(task) or {}).get("state") == "stopped"
    retries = (state["limits"].get("retries", DEFAULT_RETRIES)
               + int(((state.get("health") or {}).get(agent) or {}).get("repents") or 0))
    final = stopped or forced or (reason != "launch-missing" and (suspicion_of(state, agent) is not None
                                                        or state["failures"].get((agent, task), 0) >= retries))
    events: list[dict] = [{"kind": "wake-failed", "tag": intent["tag"], "agent": agent, "task": task,
                           "final": final, "reason": reason}]
    if isinstance(cost, (int, float)) and not isinstance(cost, bool):
        events[0]["cost"] = cost
    if run:
        events[0]["run"] = run
    events[0].update({key: value for key, value in (extra or {}).items() if value is not None})
    if not stopped:
        events += halting(state, intent, reason)
    if final and not stopped:
        said = f"the launch of {agent} failed: {reason}"
        for key in intent.get("messages") or []:
            message = state["messages"].get(key) or {}
            on = message.get("task")
            if not owes(state, key) or (key == opening_of(state, on) and not is_member(state, message.get("from"))):
                continue
            events.append({"kind": "post", "task": on, "from": agent, "to": message.get("from"), "verb": "re",
                           "re": key, "text": said, "by": "tick"})
        if is_root(state, agent, task):
            events.append({"kind": "post", "task": task, "from": (state["started"] or {}).get("team"),
                           "to": told_of(state, agent, task), "verb": "notice", "about": agent, "text": said})
    return events


def vectors_of(state: dict, agent: str, task: str) -> list[str]:
    """-> the VECTORS a run of the member carries on the task, each once in its order: the task's own (`post
    --vector`), then the one of the LAST `do` to the member on that task that carries one -- a later `do`'s vector
    replaces an earlier one's: a corrected node. What each launch of that run passes to the launcher, `--vector
    <v>`. Opaque: the team reads no family, no id."""
    found = list((state["tasks"].get(task) or {}).get("vectors") or [])
    last = None
    for one in state["messages"].values():
        if one.get("task") == task and one.get("verb") == "do" and one.get("to") == agent and one.get("vector"):
            last = str(one["vector"])
    return list(dict.fromkeys(found + ([last] if last else [])))


def vector_refused(state: dict, intent: dict, why: str, vectors: list[str]) -> list[dict]:
    """-> the events a launch carrying VECTORS writes when the launcher refuses a vector -- rc 2 under the code
    `vector-refused` (`VECTOR_REFUSED`); any other refusal is the house's (`house_failed`) --: the node cannot be
    played, a retry would meet the same refusal -- the failure is FINAL at once and said to the task as a
    failed wake-up says it (`failed`: each `do` of the launch answered by the tick, the root's principal told),
    `house: true` (the member did nothing: no suspicion), the vectors on the event; never launched again on it."""
    said = " ".join(why.split())
    return failed(state, intent, f"launch-refused: {said}", forced=True, extra={"house": True, "vectors": vectors})


def house_failed(state: dict, name: str, intent: dict, why: str) -> list[dict]:
    """-> the events a launch the HOUSE refused writes: `agent start` ended before any harness, without its report
    (a package the agent does not pin, a run held, a session missing, a provider unwired). `wake-failed {reason:
    launch-failed: <why>, house: true}`, never final: no retry spent, no fall, no suspicion -- the member did
    nothing --, its messages back in its inbox, so that the next tick launches it again; and ONE notice of the
    team to the owner per (member, cause) since the season began (`house: true`, no `about`: it holds no wait); the
    same refusal HALT_AFTER times in a row on the task halts the member there (`halting`)."""
    said = " ".join(why.split())
    events: list[dict] = [{"kind": "wake-failed", "tag": intent["tag"], "agent": intent["agent"], "task": intent["task"],
                           "final": False, "reason": f"launch-failed: {said}", "house": True}]
    told = f"the house could not launch {intent['agent']}: {said}"
    since = int((state["started"] or {}).get("id") or 0)
    if not any(one.get("house") and one.get("verb") == "notice" and one.get("text") == told and one["id"] > since
               for one in state["messages"].values()):
        events.append({"kind": "post", "task": intent["task"], "from": name, "to": str((state["started"] or {}).get("owner")),
                       "verb": "notice", "house": True, "text": told})
    return events + halting(state, intent, events[0]["reason"])


def failure_identity(reason) -> str:
    """-> a failure's reason as the guard compares it: its CODED prefix alone, never what a harness or a house said --
    `harness-error: <error>`, the error cut at its first colon (`harness rc <n>` for an exit without an error of its
    own); `launch-failed: <code>` and `launch-refused: <code>`, the refusal's code; `wake-dead`, `wake-timeout` and
    any reason without a colon as they are."""
    said = " ".join(str(reason or "").split())
    head, colon, rest = said.partition(": ")
    if not colon:
        return head
    if head == "harness-error":
        return f"{head}: {rest.split(':', 1)[0].strip()}"
    coded = re.match(r"(?:[\w.-]+: )?([A-Za-z]\w*(?:-[a-z0-9]+)*)", rest)
    return f"{head}: {coded.group(1) if coded else ''}"


def owed_free(state: dict, member: str) -> list[int]:
    """-> the debts of the member (`owed_by`) on the tasks that do not halt it (`halted_of`): what a relance or a try
    carries."""
    return [key for key in owed_by(state, member)
            if halted_of(state, member, state["messages"][key].get("task")) is None]


def halted_of(state: dict, agent: str, task: str | None) -> dict | None:
    """-> the `wake-halted` that holds the member on the task, None when nothing holds it there."""
    return next((one for one in state.get("halts") or [] if one.get("agent") == agent and one.get("task") == task), None)


def halting(state: dict, intent: dict, reason: str) -> list[dict]:
    """-> `wake-halted {agent, task, reason, count}` and ONE notice of the team to the owner (`halted: true`, no
    `about`: it holds no wait) when the failure of `intent` is the HALT_AFTER-th one in a row of its member on its task
    with the same identity (`failure_identity`) since the task's last resume or the season's start -- an end of the
    member there breaks the row, a `launch-missing` launched nothing and is never counted --; [] otherwise. The member
    is launched on that task no more until `team resume --task`."""
    agent, task = intent["agent"], intent["task"]
    if reason == "launch-missing" or halted_of(state, agent, task) is not None:
        return []
    since = max(int(state["resumed"].get(task, 0) or 0), int((state["started"] or {}).get("id") or 0))
    mine = sorted((one for one in [*state["ends"], *state["fails"]] if int(one.get("id") or 0) > since
                   and (state["intents"].get(one.get("tag")) or {}).get("agent") == agent
                   and (state["intents"].get(one.get("tag")) or {}).get("task") == task),
                  key=lambda one: int(one.get("id") or 0))
    same, identity = 1, failure_identity(reason)
    for one in reversed(mine):
        if one.get("reason") == "launch-missing":
            continue
        if one.get("kind") != "wake-failed" or failure_identity(one.get("reason")) != identity:
            break
        same += 1
    if same < HALT_AFTER:
        return []
    started = state["started"] or {}
    team = started.get("team")
    return [{"kind": "wake-halted", "agent": agent, "task": task, "reason": reason, "count": same},
            {"kind": "post", "task": task, "from": team, "to": str(started.get("owner")), "verb": "notice",
             "halted": True, "text": f"{agent} failed {same} times in a row on {task} ({reason}): the team no longer "
                                     f"launches it on {task} until `team resume {team} --task {task}`"}]


def quota_of(state: dict, member: str, clock: datetime) -> dict | None:
    """-> the provider's limit that holds the member at `clock`, `{until, said, at, task, tag}` -- its `until` still to
    come, or none said --, None when no limit holds it."""
    held = (state.get("quotas") or {}).get(member)
    if not held:
        return None
    if held.get("until") is None:
        return held
    try:
        until = datetime.fromisoformat(str(held["until"])).astimezone().replace(tzinfo=None)
    except ValueError:
        return held
    return held if clock < until else None


def quota_face(state: dict, member: str) -> dict | None:
    """-> `{until, said, at}` of the provider's limit that holds the member now, None when none holds it."""
    held = quota_of(state, member, tick_now())
    return None if held is None else {key: held.get(key) for key in ("until", "said", "at")}


def aged(launch: dict) -> float:
    """-> the launch's age in seconds: the journal's UTC `at` against the real UTC clock
    (`PP_NOW` plays no part here: a timeout compares two wall-clock stamps)."""
    try:
        born = datetime.fromisoformat(str(launch.get("at")))
    except ValueError:
        return 0.0
    return (datetime.now(timezone.utc) - born).total_seconds()


def ending(conductor, root: Path, journal: Path, name: str, tag: str, events: list[dict]) -> list[dict]:
    """Appends the events that END the intent `tag`, judged under the journal's lock: nothing
    when another writer ended it meanwhile (a `stop --kill`, another tick)."""
    return written(conductor, root, journal, name, lambda state, lines: [] if tag in state["ended"] else events)


def messages_cursor(root: Path, name: str, state: dict) -> dict[str, dict]:
    """-> the tags `agent start` wrote at the house's `messages.jsonl` for launches the journal does not
    know the launch of yet, each with its `run` and `pid`: the record is read INCREMENTALLY, from the byte
    the cursor `tick.cursor` beside the journal reached (whole lines alone), under the tick's lock; the
    tags of intents launched or ended leave the cursor. What a late `wake-launched` and the bounds'
    count of the launches read, in place of the record whole."""
    cursor_path = journal_of(root, name).parent / TICK_CURSOR
    try:
        cursor = json.loads(cursor_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cursor = {}
    offset, tags = int(cursor.get("offset") or 0), dict(cursor.get("tags") or {})
    record = record_of(root, MESSAGES)
    if record.is_file():
        with record.open("rb") as handle:
            handle.seek(offset)
            raw = handle.read()
        whole = raw[:raw.rfind(b"\n") + 1] if b"\n" in raw else b""
        for line in whole.decode("utf-8", "replace").splitlines():
            try:
                one = json.loads(line)
            except ValueError:
                continue
            if isinstance(one, dict) and one.get("tag"):
                tags[str(one["tag"])] = {"run": one.get("run"), "pid": one.get("pid")}
        offset += len(whole)
    tags = {tag: one for tag, one in tags.items() if tag in state["intents"] and tag not in state["launched"]
            and tag not in state["ended"] or tag not in state["intents"]}
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = cursor_path.with_name(f".{cursor_path.name}.{os.getpid()}")
    temporary.write_text(json.dumps({"offset": offset, "tags": tags}), encoding="utf-8")
    os.replace(temporary, cursor_path)
    return tags


def answered_in_flow(root: Path, conductor, state: dict, intent: dict, launch: dict) -> bool:
    """-> whether the launch's flow carries the END of its exchange (a `response` line after the `opened` that
    carries the launch's tag): a wake-up that answered -- the kill spares it, the reap ends it with its cost."""
    run = launch.get("run")
    if not run:
        return False
    start = int(state["flow"].get(str(run)) or 0) + 1
    opened = False
    for _, one in flow_lines(root, conductor, path_of_intent(state, intent), str(run), start):
        if one.get("kind") == "opened":
            opened = opened_by(one, str(intent.get("tag")))
        if opened and one.get("kind") == "response":
            return True
    return False


def awaits_of(root: Path, conductor, path: str, run: str) -> tuple[str | None, bool]:
    """-> (what the run's stack awaits, whether its harness session stands), read at agent's FACE (`agent
    status <path> --json`: `awaits`, `session`): `standing` (a production: the run is relaunched) or `parked`
    (a message); (None, False) when the face says nothing of that run. The one reading of a run's state a
    launch without a response leaves -- never deduced from the failure; the run is resumed only with its
    session (a launch killed before its harness said anything left none: `session-missing` otherwise)."""
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "status", path, "--json"],
                            capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    for line in played.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if one.get("run") == run and one.get("awaits") in ("message", "production"):
            return ("parked" if one["awaits"] == "message" else "standing"), bool(one.get("session"))
    return None, False


def ended_from_flow(state: dict, intent: dict, launch: dict, told: dict, hint: str | None,
                    awaits: tuple[str | None, bool] = (None, False)) -> list[dict]:
    """-> the events that END a launch whose flow said its end: `wake-ended {tag, agent, run, launch, state,
    cost, flow, context, tokens}` when a response was kept -- `state` what the house said of the run at `--on-end` (the
    `response` line's, else `hint`, the `PP_AGENT_STATE` the on-end tick carries): `standing`, the run
    waits for a production and is relaunched; `parked`, it waits for a message --; `wake-failed wake-dead
    {state}` when the launch ended without a response (the harness died): `state` what the run awaits, read at
    agent's face (`awaits`); no run on it, the member keeps the run that answered before or opens a new one.
    `flow` is the rank of the flow the journal reached: the next launch of the run reads from there; `context` the
    last context the exchange measured, None when it measured none; `tokens` what its calls sent the model (`sent_of`).
    A response kept on an ERROR of the harness -- its
    `error` set or its `harness_rc` not 0, but for the errors that are no fault of it (`HARNESS_SPARED`) -- whose launch
    routed no act is no answer: `wake-failed {reason: harness-error: <error>}`, the run kept (`failed`); one on the
    provider's usage limit (`error: quota`) is `quota-reached {agent, task, until, said}`: no failure, no retry, no
    fall -- the member is launched on no task before `until`, or before `team resume --task` without one."""
    response = told.get("response") or {}
    cost = told.get("cost") if told.get("cost") else response.get("cost_usd")
    run, rank = launch.get("run"), told.get("rank")
    if not told.get("response"):
        said, resumable = awaits
        return failed(state, intent, "wake-dead", None, run if resumable else None, {"flow": rank, "state": said})
    said = str(response.get("state") or hint or "parked")
    error, rc = response.get("error"), response.get("harness_rc")
    if error == "quota":                                         # the provider's limit: a stop, never a failure
        quota = response.get("quota") or {}
        return [{"kind": "quota-reached", "tag": intent["tag"], "agent": intent["agent"], "task": intent["task"],
                 "run": run, "launch": launch.get("launch"), "state": said, "cost": cost, "flow": rank,
                 "until": quota.get("until"), "said": quota.get("said")}]
    if error not in HARNESS_SPARED and (error is not None or rc not in (0, None)) and not state["routed"].get(intent["tag"]):
        return failed(state, intent, f"harness-error: {error or f'harness rc {rc}'}", cost, run,
                      {"flow": rank, "state": said, "harness_rc": rc})
    return [{"kind": "wake-ended", "tag": intent["tag"], "agent": intent["agent"], "run": run,
             "launch": launch.get("launch"), "state": said, "cost": cost, "flow": rank, "context": told.get("context"),
             "tokens": sent_of(response)}]


def sent_of(response: dict) -> int | None:
    """-> the tokens the calls of a wake-up sent the model, as its response's record says them (`tokens_sent`);
    None when the adapter measured none."""
    sent = response.get("tokens_sent")
    return sent if isinstance(sent, int) and not isinstance(sent, bool) else None


def reaped(root: Path, conductor, name: str, journal: Path, hint: tuple[str, str] | None = None) -> int:
    """Step 1 and 2 (and 6 on a root's `done`): each intent without an end is matched to its launch,
    its flow is READ from the rank the journal reached -- every `words` that reads as an act routed, once
    (`flow_read`; the follower reads the same flow while the launch plays, and a launch under way within
    `timeout:` is left to it) --, and the launch is ended when its flow says so (`ended_from_flow`):
    `wake-ended` with the run's state and its cost, or `wake-failed`. A launch whose flow has no end:
    its wake lock held past `timeout:`, it is killed and fails `wake-timeout`; its lock free, it died
    without saying so -- `wake-failed wake-dead`; born in another process space than this tick's (`foreign`), it
    ended with that space: the house's failure (`house_failed`), and its pid is never killed. A launch that fails
    carries the run's `state`, read at
    agent's face (`awaits_of`): standing, the run is relaunched while its retries last. `hint` is what the on-end tick carries, `(run, state)`
    from `PP_AGENT_RUN` and `PP_AGENT_STATE`. -> the events written."""
    lock = locks(conductor)
    count = 0
    state = state_of(journal)
    for tag in list(state["intents"]):
        intent = state["intents"][tag]
        if tag in state["ended"]:
            continue
        launch = state["launched"].get(tag)
        if launch is None:
            found = messages_cursor(root, name, state).get(tag)
            if found is None or not found.get("run"):
                count += len(ending(conductor, root, journal, name, tag, failed(state, intent, "launch-missing")))
                state = state_of(journal)
                continue
            launch = appended(conductor, root, journal, name, [{"kind": "wake-launched", "tag": tag, "agent": intent["agent"],
                                                          "run": found["run"], "pid": found.get("pid"),
                                                          "launch": launches_of_run(state, str(found["run"])) + 1}])[0]
            count += 1
            state = state_of(journal)
        run = str(launch.get("run") or "")
        path = path_of_intent(state, intent)
        held = lock.held(launch_of(conductor, agent_meta(root, path), run))   # judged BEFORE the flow is read: a
        bound = state["limits"].get("timeout")                                # launch over wrote its end first
        if held and (bound is None or aged(launch) <= float(bound)):
            continue                                           # the launch plays: its follower reads its flow
        told = flow_read(root, conductor, name, journal, tag)
        state = state_of(journal)
        if not told["ended"]:
            if held:
                # a stuck launch: past the bound it is ended by the kill gesture and
                # FAILS -- the retries apply; `wake-killed` stays the principal's word
                pid = launch.get("pid")
                if isinstance(pid, int) and not foreign(launch):   # a pid of another space names nobody here
                    ended_now(pid)
                said, resumable = awaits_of(root, conductor, path, run)
                count += len(ending(conductor, root, journal, name, tag,
                                    failed(state, intent, "wake-timeout", None, run if resumable else None,
                                           {"flow": told["rank"], "state": said})))
            elif foreign(launch):
                # its launcher was born in another process space -- a sandbox's -- and ended with it: the
                # house's failure, never final; a fresh run at the next launch (this one never had a session)
                events = house_failed(state, name, intent, "its launcher played in another process space, which "
                                      "ended before the exchange did -- tick the team from the house's own")
                events[0].update({"flow": told["rank"], "space": launch.get("space")})
                count += len(ending(conductor, root, journal, name, tag, events))
            else:
                said, resumable = awaits_of(root, conductor, path, run)
                count += len(ending(conductor, root, journal, name, tag,
                                    failed(state, intent, "wake-dead", None, run if resumable else None,
                                           {"flow": told["rank"], "state": said})))
            state = state_of(journal)
            continue
        said = hint[1] if hint is not None and hint[0] == run else None
        if (state["tasks"].get(intent["task"]) or {}).get("state") == "stopped" and told.get("response"):
            events = [{"kind": "wake-ended", "tag": tag, "agent": intent["agent"], "run": run,
                       "launch": launch.get("launch"), "state": str((told["response"] or {}).get("state") or said or "parked"),
                       "cost": told.get("cost") or (told["response"] or {}).get("cost_usd"), "flow": told["rank"],
                       "context": told.get("context"), "tokens": sent_of(told["response"] or {})}]
        else:
            events = ended_from_flow(state, intent, launch, told, said,
                                     (None, False) if told.get("response") else awaits_of(root, conductor, path, run))
        count += len(ending(conductor, root, journal, name, tag, events))
        state = state_of(journal)
    return count


def launches_of_run(state: dict, run: str) -> int:
    """-> the launches the journal knows of the run: its `wake-launched` events -- the rank the next one
    takes, and the rank of the exchange in the run's flow (`agent flow --exchange`)."""
    return sum(1 for one in state["launched"].values() if one.get("run") == run)


def tick_now() -> datetime:
    """-> the tick's wall clock, LOCAL and naive: `PP_NOW` (ISO) when the variable is set --
    the bench, a try --, else the house's local time (the one the timer and the relaunch entry play under)."""
    given = os.environ.get(NOW, "").strip()
    if not given:
        return datetime.now()
    try:
        return datetime.fromisoformat(given)
    except ValueError:
        refuse(f"now-invalid -- `{NOW}={given}` is no ISO date-time.")


def conforms(when: dict, day) -> bool:
    """-> whether an `every` ceremony rings on that day (a date or a date-time): every day, a
    weekday, or its one day of the week -- the ONE reading of the rhythm's days."""
    kind = when.get("kind")
    weekday = day.weekday()
    return kind == "day" or (kind == "weekday" and weekday < 5) or (kind in DOWS and weekday == DOWS.index(kind))


def due_period(ceremony: dict, state: dict) -> str | None:
    """-> the period the ceremony owes a ring for, or None. An `every` ceremony is due once
    its day conforms and its hour is past (the period is the local date); an `after` one is
    due for each period its followed ceremony RESOLVED and it did not ring yet (inherited).
    The periods already rung are the state's (`rung`): a snapshot carries them."""
    already = set(state["rung"].get(str(ceremony["name"]), []))
    if ceremony["mode"] == "every":
        now = tick_now()
        when = ceremony.get("when") or {}
        since = state.get("since")
        if conforms(when, now) and now.strftime("%H:%M") >= str(when.get("at")):
            period = now.date().isoformat()
            moment = datetime.fromisoformat(f"{period}T{when.get('at')}")
            if period not in already and (not since or moment > datetime.fromisoformat(str(since))):
                return period
        return None
    for period in sorted(set(state["rung"].get(str(ceremony["after"]), []))):
        held_task = next((one for one in state["tasks"].values()
                          if one.get("ceremony") == ceremony["after"] and one.get("period") == period), None)
        if held_task is not None and held_task["state"] == "resolved" and period not in already:
            return period
    return None


def next_due(ceremony: dict, state: dict) -> str | None:
    """-> the local date-time `YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring: today when
    the day conforms and its period is not rung yet -- its hour past or not --, else the next
    conforming day; None for an `after` ceremony, which follows the one it names. A ring at hand
    (`manual-<id>`) takes no date: it moves nothing here, as in `due_period`."""
    if ceremony["mode"] != "every":
        return None
    when = ceremony.get("when") or {}
    already = set(state["rung"].get(str(ceremony["name"]), []))
    since = datetime.fromisoformat(str(state["since"])) if state.get("since") else None
    today = tick_now().date()
    for ahead in range(8):
        day = today + timedelta(days=ahead)
        moment = f"{day.isoformat()}T{when.get('at')}"
        if (conforms(when, day) and day.isoformat() not in already
                and (since is None or datetime.fromisoformat(moment) > since)):
            return moment
    return None


def named(conductor, asked: dict) -> dict:
    """-> the `name` field a task is born with: `{"name": <text>}` under `--name`, `{}` without --
    a task born without a name writes the fields it always wrote. A name is what a user types: free
    text on ONE line, its spaces at the edges dropped, 1 to `NAME_CHARS` characters, every one
    printable -- a line break or a control character would split the task's line in `status`, `log`
    and `watch`. `name-invalid` otherwise."""
    given = asked.get("name")
    if given is None:
        return {}
    text = given.strip()
    if not text or len(text) > NAME_CHARS or not text.isprintable():
        shown_name = " ".join(given.split())[:40]
        refuse(f"name-invalid -- `--name {shown_name}`: a task's name is one line of 1 to {NAME_CHARS} printable "
               "characters.")
    return {"name": text}


def recurrence_description(given: str) -> str:
    """-> the description `--description` gives a recurrence: one sentence of what it does, beside its short name --
    one line, its edges stripped, 1 to `DESCRIPTION_CHARS` printable characters; `description-invalid` otherwise."""
    text = given.strip()
    if not described_well(text):
        refuse(f"description-invalid -- `--description {' '.join(given.split())[:40]}`: a recurrence's description is "
               f"one line of 1 to {DESCRIPTION_CHARS} printable characters.")
    return text


def consignes(team: str, ceremony: dict, at: str) -> tuple[str, str]:
    """-> (the facilitator's task text, each participant's `do` text): what a ring ASKS, never the
    ceremony's declaration line -- the team's intention and the ceremony's entry say what to do."""
    head = f"the ceremony `{ceremony['name']}` of team {team} rings ({at})"
    participants = ", ".join(str(one) for one in ceremony["participants"])
    enough = f" ({ceremony['quorum']} of them are enough)" if ceremony.get("quorum") else ""
    return (f"{head}: gather the answers of {participants}{enough}, then answer this message with the conclusion -- "
            "your answer closes the ceremony.",
            f"{head}: take part in it as the team's intention says, and answer {ceremony['facilitator']}.")


def ringing(state: dict, team: str, ceremony: dict, period: str, by: str | None = None) -> list[dict]:
    """-> the events one ring writes: `ceremony-due` (with `by`, the principal, for a ring at
    hand), ONE ceremony task from the team to the facilitator, its OPENING `do` from the team to the
    facilitator, then a `do` post facilitator -> each participant -- each answer reaches the facilitator as a
    message, the line's quorum is said in its consigne, and its answer to the opening resolves the task. The task is
    NAMED `<ceremony> YYYY-MM-DD HH:MM`, the local hour of the ring, and says a consigne."""
    task = next_task(state)
    facilitator = str(ceremony["facilitator"])
    at = tick_now().strftime("%Y-%m-%d %H:%M")
    asked, taking = consignes(team, ceremony, at)
    due = {"kind": "ceremony-due", "ceremony": ceremony["name"], "period": period}
    if by is not None:
        due["by"] = by
    events: list[dict] = [due,
                          {"kind": "task", "task": task, "from": team, "to": facilitator,
                           "ceremony": ceremony["name"], "period": period, "name": f"{ceremony['name']} {at}",
                           "text": asked},
                          {"kind": "post", "task": task, "from": team, "to": facilitator, "verb": "do", "text": asked}]
    for one in ceremony["participants"]:
        events.append({"kind": "post", "task": task, "from": facilitator, "to": one, "verb": "do",
                       "text": taking})
    return events


def live_recurrences(state: dict) -> list[dict]:
    """-> the recurrences of the team not stopped, in the order they were posted -- a suspended one among them."""
    return [one for one in (state.get("recurrences") or {}).values() if one.get("stopped") is None]


def sounds_at(recurrence: dict, day) -> datetime:
    """-> the local date-time a recurrence's period of that day sounds at: the day, at the recurrence's hour."""
    hour, minute = (int(part) for part in str(recurrence["when"]["at"]).split(":"))
    return datetime(day.year, day.month, day.day, hour, minute)


def slot_of(recurrence: dict, now: datetime) -> tuple[int, datetime]:
    """-> the SLOT of a recurrence by a duration under way at `now` -- its rank k and its instant, `since + k x seconds`,
    k never under the recurrence's first (0 at the pose, 1 after a change that gave the duration)."""
    since = datetime.fromisoformat(str(recurrence["since"]))
    seconds = int(recurrence["when"]["seconds"])
    rank = max(int((now - since).total_seconds() // seconds), int(recurrence.get("first") or 0))
    return rank, since + timedelta(seconds=rank * seconds)


def slot_period(moment: datetime) -> str:
    """-> the period of a slot: its local instant `YYYY-MM-DDTHH:MM`."""
    return moment.isoformat(timespec="minutes")


def recurrence_period(recurrence: dict) -> str | None:
    """-> the period a live recurrence owes now, or None: its day conforms, its hour is past, that period sounds after
    the recurrence was posted (`since`) and it has not sounded yet -- by an occurrence or a skip. The period is the
    local date, as a ceremony's. By a DURATION, the slot under way alone -- its instant past and not sounded --: a
    slot that passed whole without a tick, or under a pause, never sounds later. None while it is suspended."""
    if recurrence.get("stopped") is not None or recurrence.get("paused"):
        return None
    now = tick_now()
    if recurrence["when"].get("kind") == "interval":
        _, moment = slot_of(recurrence, now)
        period = slot_period(moment)
        return period if moment <= now and period not in recurrence["sounded"] else None
    if not conforms(recurrence["when"], now):
        return None
    moment = sounds_at(recurrence, now.date())
    period = now.date().isoformat()
    if now >= moment and moment > datetime.fromisoformat(str(recurrence["since"])) \
            and period not in recurrence["sounded"]:
        return period
    return None


def recurrence_next(recurrence: dict) -> str | None:
    """-> the local date-time `YYYY-MM-DDTHH:MM` a live recurrence sounds at next: the first conforming day from today,
    its period not sounded and after `since`; by a duration, the slot under way while it is not sounded, else the slot
    after it; None once it is stopped, and while it is suspended."""
    if recurrence.get("stopped") is not None or recurrence.get("paused"):
        return None
    if recurrence["when"].get("kind") == "interval":                 # the slot under way while it owes, else the next
        now = tick_now()
        _, moment = slot_of(recurrence, now)
        if moment <= now and slot_period(moment) in recurrence["sounded"]:
            moment += timedelta(seconds=int(recurrence["when"]["seconds"]))
        return slot_period(moment)
    since = datetime.fromisoformat(str(recurrence["since"]))
    today = tick_now().date()
    for ahead in range(8):
        day = today + timedelta(days=ahead)
        if (conforms(recurrence["when"], day) and day.isoformat() not in recurrence["sounded"]
                and sounds_at(recurrence, day) > since):
            return sounds_at(recurrence, day).isoformat(timespec="minutes")
    return None


def sounding(state: dict, recurrence: dict, period: str) -> list[dict]:
    """-> the events one period of a recurrence writes: its OCCURRENCE -- a task like one `post` opens, from the
    recurrence's principal to its member, NAMED `<name> YYYY-MM-DD HH:MM` (the recurrence's id without a name), with
    `recurrence` and `period`, then its opening `do` -- or, while the occurrence before it is still open,
    `recurrence-skipped {open}` and nothing opened: a member never holds the same work twice."""
    before = state["tasks"].get(recurrence.get("last") or "")
    if before is not None and before["state"] == "open":
        return [{"kind": "recurrence-skipped", "recurrence": recurrence["id"], "period": period, "open": before["id"]}]
    task = next_task(state)
    sender, to, text = recurrence.get("from"), recurrence.get("to"), recurrence.get("text")
    return [{"kind": "task", "task": task, "from": sender, "to": to,
             "name": f"{recurrence.get('name') or recurrence['id']} "
                     + (period.replace("T", " ") if recurrence["when"].get("kind") == "interval"
                        else f"{period} {recurrence['when']['at']}"), "text": text,
             "recurrence": recurrence["id"], "period": period},
            {"kind": "post", "task": task, "from": sender, "to": to, "verb": "do", "text": text}]


def sounded(conductor, root: Path, name: str, journal: Path) -> int:
    """Step 4, after the ceremonies: each live recurrence whose period is due SOUNDS it -- once per period, the
    journal the judge, the period judged again under the journal's lock; a paused team, and a team a delete has
    begun to remove (`deleting`), sound nothing. -> the events written."""
    count = 0
    for one in live_recurrences(state_of(journal)):
        if recurrence_period(one) is None:
            continue

        def judge(now_state: dict, events: list[dict], key=one["id"]) -> list[dict]:
            recurrence = now_state["recurrences"].get(key) or {}
            period = recurrence_period(recurrence) if recurrence else None
            return ([] if now_state["paused"] or now_state["stopped"] or now_state["deleting"] or period is None
                    else sounding(now_state, recurrence, period))
        count += len(written(conductor, root, journal, name, judge))
    return count


def rung(conductor, root: Path, name: str, journal: Path) -> int:
    """Step 4: each ceremony whose period is due and not yet rung is RUNG -- once per period,
    the journal the judge: two ticks in one minute ring once. A paused team rings nothing, nor a team a delete
    has begun to remove (`deleting`), judged under the journal's lock at the write. -> the events written."""
    state = state_of(journal)
    ceremonies = (state["started"] or {}).get("ceremonies") or []
    count = 0
    for one in ceremonies:
        state = state_of(journal)
        period = due_period(one, state)
        if period is not None:
            count += len(written(conductor, root, journal, name, lambda now_state, events, one=one, period=period:
                                 [] if now_state["paused"] or now_state["stopped"] or now_state["deleting"]
                                 else ringing(now_state, name, one, period)))
    return count


def launched(root: Path, conductor, name: str, started: dict, path: str, run: str | None,
             tag: str, message: str, allowance: float | None = None, member: str | None = None,
             vectors: list[str] | None = None) -> tuple[dict | None, str, int]:
    """`agent start <path>` by the house's own console -- the agent that plays the member: the
    message, the tag, the on-end tick, the run to resume -- or, at an opening, the team's material
    (`work:`: a clone per member, `pp-agent`'s; a resume reopens its own) --, the launch flags kept
    at `team-started`, and the team's directory as the run's root of documents (`--documents`). No
    door: the entry is a successor the agent's DAG elects at every exchange (`documents_written`). Under an
    `allowance`, `--max-budget-usd` is the member's RUN cap: what the run spent plus the allowance; without
    one no cap is passed. The member's PROFILE at `team-started.profiles` replaces the team's provider, model,
    effort or permissions it names; the switches of the season -- the team's `--package`, covered name by name
    by the member's -- go as `--package <name>=on|off`, which the run's opening composes its first block with and
    a resume plays before its first launch. The `vectors` the member's run carries on its task (`vectors_of`), then
    the member's own (`member_vector`), go as `--vector <v>` each, at every launch -- the whole set, `--vector -` when
    it is empty, so that a run never keeps the vector of a season gone: opaque strings, the launcher alone resolves
    them. -> ({key, pid}, '', '') or
    (None, why, the code at the head of the launcher's refusal when it ended rc 2, '' otherwise)."""
    engine = engine_of(root, conductor)
    on_end = f"{shlex.quote(sys.executable)} {shlex.quote(str(engine))} --instance {shlex.quote(str(root))} team tick {name}"
    argv = [sys.executable, str(engine), "--instance", str(root), "agent", "start", path,
            "--message", message, "--tag", tag, "--on-end", on_end, "--documents", str(team_root(root, name))]
    if run:
        argv += ["--run", run]
    elif started.get("work"):
        argv += ["--work", str(material_of(root, str(started["work"])))]
    launch = dict(started.get("launch") or {})
    launch.pop("max_budget_usd", None)                   # an older journal's per-wake cap is never passed
    profile = profile_of(started, member)
    launch.update({key: profile[key] for key in PROFILE_KEYS if profile.get(key) is not None})
    if allowance is not None:
        spent = spent_on(state_of(journal_of(root, name)), run) if run else 0.0
        launch["max_budget_usd"] = round(spent + allowance, 6)
    argv += launch_flags(launch)
    for value in season_played(root, conductor, started, member):   # the season's set: one switch per pin
        argv += ["--package", value]
    for vector in vectors or []:                                      # the nodes the run carries, opaque
        argv += ["--vector", vector]
    played = subprocess.run(argv, capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        head = REFUSAL_CODE.search(played.stderr or "") if played.returncode == 2 else None
        return (None, (played.stderr or played.stdout).strip()[-300:] or f"agent start rc {played.returncode}",
                head.group(1) if head else "")
    try:
        report = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None, f"agent start reported `{played.stdout.strip()[:80]}`", ""
    return report, "", ""


def material_of(root: Path, work: str) -> Path:
    """-> the repository `work:` of SEASON.md names: absolute, `~` expanded, a relative path read
    from the house's root."""
    path = Path(work).expanduser()
    return path if path.is_absolute() else root.parent / path


def held_run(root: Path, conductor, path: str, run: str) -> bool:
    """-> whether the run's wake lock is held at the agent `path`: a wake-up of it plays, or has
    kept its answer and is still releasing -- the reap's own test. Resumed now, `agent start
    --run` would refuse `run-busy`; the end of that wake-up ticks once the lock is free."""
    return locks(conductor).held(launch_of(conductor, agent_meta(root, path), run))


def went(state: dict, tagged: set[str], tag: str) -> bool:
    """-> whether the intent was LAUNCHED: its `wake-launched` event, or its tag at the house's
    `messages.jsonl` (`tagged`: what the cursor read of it) -- the reap's own test. The bounds count
    these alone."""
    return tag in state["launched"] or tag in tagged


def woken(root: Path, conductor, name: str, journal: Path) -> int:
    """Step 5: each member, in the declaration's order, with messages due on its tasks, no launch of its
    under way and its run not held, is LAUNCHED once -- on the first task, in the tasks' order, that has a
    message for it: the intent WRITTEN FIRST, then the launch, then
    `wake-launched` -- or `wake-failed` when the console launched nothing. Its other tasks wait for
    its next launch, each in the run of its carrier. A run STANDS per (member, task) (its last launch there left it
    waiting for a production: `wake-ended {state: standing}`); each run a member holds standing is RELAUNCHED on its
    task in its turn (`standing_of`: the tasks' order, one launch at a time) as soon as its wake lock is free, while
    it does not park -- on a resolved task ONE launch more, under `CLOSED_HEAD`, then held as parked (s.1409) --, with `[nothing new]` at its head
    when nothing is due -- a CONTINUATION, judged BEFORE any relance: a standing debtor continues, its debts under
    `[you still owe an answer to]`, never with the head of a relance. Before them, the SILENCES (`silences`): each
    member whose silent PASSAGES in a row -- a wake-up and its continuations, parked without one act of its -- on a
    task it owes on reached `silence:` falls -- `silence` written, the member suspected; a continuation counts for
    nothing: a standing run is continued while it does not park, `launches:` and `budget:` its only bounds. A
    member at the bottom of the deadlocked set that OWES an answer and whose continuation launched nothing (no run
    standing) is RELANCED (`relance_of`), without a count: launched on the first task where it owes, its debts for
    messages, under every guard of a launch. Each intent says whether it CONTINUES a standing run (`continued`); a
    WAKE-UP of a member that owes keeps its BEAT (`beat_of`).
    Before all, the failure detector: each SUSPECTED member within its interval is answered for on the messages
    of members (`suspected_answers`) and launched on what a PRINCIPAL says to it alone -- that launch is its try;
    its interval passed, its next message is its try, and a member owing a principal's opening alone is tried by a
    relance on it (`tried_of`). The members play
    in parallel, one run each; `parallel:` bounds the team. `launches:` bounds the launches of one task
    and `budget-launches:` those of the season. A stopped task launches nobody -- but a run STANDING on it,
    launched ONE more time with the stop at its head (`dues`); under `work:` a run RELAUNCHABLE on its standing
    task takes no other task's head (one clone, one task at a time: T7) -- held by that task's
    `launches:` spent, it does, as a run without `work:`: a member's other tasks never starve. A member whose share of the budget is all held by
    the launches under way is deferred; a paused team, or one off season, launches nobody. -> the events written."""
    count = 0
    state = state_of(journal)
    if state["paused"] or state["stopped"]:
        return 0
    started = state["started"] or {}
    tagged = set(messages_cursor(root, name, state))
    clock = tick_now()
    count += len(written(conductor, root, journal, name, lambda now_state, events: suspected_answers(now_state, clock)))
    fallen = False
    for agent in list(started.get("agents") or {}):
        if quota_of(state_of(journal), agent, clock) is not None:
            continue                                             # its provider's limit holds it: launched on no task
        fell = written(conductor, root, journal, name, lambda now_state, events: silences(now_state, name, clock, agent))
        if fell:                                                 # its silence fell: answered for at this very tick
            count += len(fell)
            count += len(written(conductor, root, journal, name, lambda now_state, events: suspected_answers(now_state, clock)))
            fallen = True
        now_state = state_of(journal)
        suspected = within(now_state, agent, clock)              # within its interval: what a principal says to it
        launched_now = 0                                         # launches it -- its try --, nothing else does
        for task, box in dues(now_state, agent):
            if not loud(now_state, box):                         # members' infos alone: they ride the head of its
                continue                                         # next launch, whatever its cause [114]
            if suspected and not any(is_principal(now_state, one.get("from")) for one in box):
                continue
            launched_now += woken_on(root, conductor, name, journal, started, tagged, agent, task)
        count += launched_now
        if suspected:
            continue
        if not launched_now:                                     # nothing received: its try, its continuation, else a relance
            now_state = state_of(journal)
            tried = tried_of(now_state, agent, clock) if suspicion_of(now_state, agent) is not None else None
            continued = 0                                        # each run that stands: relaunched in its turn
            for standing_on in (standing_of(now_state, agent) if tried is None else []):
                continued = woken_on(root, conductor, name, journal, started, tagged, agent, standing_on, standing=True)
                if continued:                                    # one launch at a time
                    break
            count += continued
            if continued:                                        # a standing debtor CONTINUES: never the head of a relance
                continue
            now_state = state_of(journal)
            why = tried or relance_of(now_state, agent)          # a suspect past its interval: its TRY first; then a
            if why is not None:                                  # debtor whose continuation launched nothing (no run stands)
                debts = owed_free(now_state, agent)              # its first debt on a task that does not halt it
                key = next((one for one in debts if principal_opening(now_state, one)), debts[0]) if why[0] == "tried" else debts[0]
                task = now_state["messages"][key].get("task")
                count += woken_on(root, conductor, name, journal, started, tagged, agent, task, relance=why)
    if fallen:                                                   # a fall answered for a member judged already: once more
        count += woken(root, conductor, name, journal)
    return count


def woken_on(root: Path, conductor, name: str, journal: Path, started: dict, tagged: set[str],
             agent: str, task: str, relance: tuple[str, str | None] | None = None, standing: bool = False) -> int:
    """One (member, task) of step 5, judged on the state read again; the house is addressed by
    the member's path. The member's run for the task's CARRIER (`carrier_of`: the task, an occurrence's
    recurrence, a ring's ceremony) is resumed while its slot stands -- a renewal mark an upgrade left
    included --; none yet, its slot gone (`-reset`) or its run dropped (`team reset`), a new run OPENS, told
    the history of the carrier's open tasks, and is NAMED after the carrier (`run_named`) -- as it does when its parked
    run is renewed (`renewal_of`: its context limit reached, or opened under another model or provider than the
    season's; `run-renewed` written with the intent): `wake-launched` keeps the model and the provider of the launch
    (`launch_kept`). A name the house
    refuses is said at `wake-launched` (`name-refused`), the launch plays on. A RELANCE (`relance`: its reason) carries
    the member's debts on the task as its messages and, as its inbox, the members' infos waiting there alone. A STANDING run (`standing`) is
    relaunched on the task it stands on, `[nothing new]` at its head. The intent says `continued` when it resumes a
    run that stood (`stood`) -- its head then carries what varies alone --, and a WAKE-UP of a member that owes
    keeps its `beat` (`beat_of`), said at its head. EVERY launch on a run that stands
    (`continued_run`) is a continuation whatever is due: the stop alone at its head, the messages due waiting for
    its park -- never delivered to a run in the middle of its passage, which would park without a turn on them
    (s.1377) --, and opening the launch after; the TRY of a suspected member alone delivers whatever its run
    (row 108). The launch is ONE launch of the harness (`--launches 1`); its
    `wake-launched` carries the launch's RANK in the run, and its FOLLOWER is spawned to read its flow
    while it plays. A launch the house refuses before any harness is no fall (`house_failed`), and so is one whose
    preparation RAISES once its intent is written: the exception's type and message its cause, the tick goes on to
    its net; a naming that raises is a name refused. -> the events written."""
    count = 0
    state = state_of(journal)
    path = path_of(state, agent)
    if halted_of(state, agent, task) is not None or quota_of(state, agent, tick_now()) is not None:
        return 0                                                 # held by its failures in a row, or by its provider
    if relance is None:
        box, carried = dict(dues(state, agent)).get(task) or [], []
        if continued_run(state, agent, task) and suspicion_of(state, agent) is None:   # its run stands: a
            box = [one for one in box if one.get("verb") == "stop"]   # continuation, the stop alone at its head -- the
            #                                                          rest waits for its park and opens the launch after
        if not standing and not loud(state, box):
            return 0                                             # members' infos alone launch nobody [114]
    else:
        box = [one for one in dict(dues(state, agent)).get(task) or [] if quiet(state, one)]   # the infos ride its head
        carried = [key for key in owed_by(state, agent) if state["messages"][key].get("task") == task]
        judged = tried_of(state, agent, tick_now()) if relance[0] == "tried" else relance_of(state, agent)
        if judged != relance or not carried:
            return 0
    if standing and ((agent, task) not in state["standing"] or run_held(state, agent, task) is None):
        return 0
    if started.get("work") and relance is None and any(
            other != task and other not in state["launches_spent"] for other in standing_of(state, agent)):
        return 0                                                 # under work: a run relaunchable on its standing task takes no
        #                                                          other task's head; held by the task's bound, it does
        #                                                          (no starvation)
    if not (box or carried or standing) or busy(state, agent):
        return 0
    kept = run_held(state, agent, task)                         # the run of the task's carrier
    if kept is not None and held_run(root, conductor, path, kept):
        return 0
    per_task = state["limits"].get("launches")
    since = max(state["resumed"].get(task, 0),                  # a resume, or a season, counts afresh
                int((state["started"] or {}).get("id") or 0))
    task_wakes = sum(1 for tag, one in state["intents"].items()
                     if one.get("task") == task and int(one.get("id") or 0) > since and went(state, tagged, tag))
    if per_task is not None and task_wakes >= per_task:     # the task's launches are spent
        if task not in state["launches_spent"]:
            count += len(appended(conductor, root, journal, name, [
                {"kind": "launches-spent", "task": task, "spent": task_wakes, "launches": per_task},
                {"kind": "post", "task": task, "from": name, "to": str(started.get("owner")), "verb": "notice",
                 "text": f"the task's launches are spent: {task_wakes} of {per_task}; {agent} stays due on {task}"}]))
        return count
    budget = state["limits"].get("budget")
    if budget is not None and state["cost"] >= budget:        # the team has spent what it may
        if not state["budget_spent"]:
            count += len(appended(conductor, root, journal, name, [
                {"kind": "budget-spent", "spent": round(state["cost"], 6), "budget": budget},
                {"kind": "post", "task": task, "from": name, "to": str(started.get("owner")), "verb": "notice",
                 "text": f"the budget is spent: {state['cost']:g} of {budget:g} USD; {agent} stays due on {task}"}]))
        return count
    total_bound = state["limits"].get("budget-launches")
    since_start = sum(1 for tag, one in state["intents"].items()
                      if int(one.get("id") or 0) > int(started.get("id") or 0) and went(state, tagged, tag))
    if total_bound is not None and since_start >= total_bound:   # the costless bound, since the start
        if not state["budget_spent"]:
            count += len(appended(conductor, root, journal, name, [
                {"kind": "budget-spent", "spent": since_start, "budget": total_bound, "unit": "launches"},
                {"kind": "post", "task": task, "from": name, "to": str(started.get("owner")), "verb": "notice",
                 "text": f"the budget is spent: {since_start} of {total_bound} launches; {agent} stays due on {task}"}]))
        return count
    parallel = state["limits"].get("parallel")
    if parallel is not None and len(open_intents(state)) >= parallel:
        return len(appended(conductor, root, journal, name, [{"kind": "deferred", "agent": agent, "task": task}]))
    allowance = allowance_of(state, started) if measured(root, conductor, started) else None
    if allowance is not None and allowance <= 0:                 # the rest all held by the wake-ups under way
        return len(appended(conductor, root, journal, name, [{"kind": "deferred", "agent": agent, "task": task,
                                                        "reserved": reserved_of(state)}]))
    run = kept
    if run is not None and not conductor.persistence.slot_of(agent_meta(root, path), run).is_file():
        run = None                                               # forgotten (`-reset`): a new run
    renewal = renewal_of(state, agent, task, run)
    if renewal is not None:
        run = None                                               # past its limit, or another model: a new run
    history = histories_of(state, agent, task) if run is None else ""   # an opening is told its carrier's past
    continued = run is not None and stood(state, agent, task)    # it resumes a run that stands: its passage goes on
    beat = None if continued else beat_of(state, agent, task, box)   # a WAKE-UP alone carries the beat
    tag = f"{agent}-{task}-{secrets.token_hex(3)}"
    made = written(conductor, root, journal, name, lambda now_state, events: [] if now_state["paused"] or now_state["stopped"] else [
        *([renewal] if renewal is not None else []),
        {"kind": "wake-intent", "tag": tag, "agent": agent, "path": path, "task": task, "run": run,
         "messages": [one["id"] for one in box] if relance is None else carried + [one["id"] for one in box],
         "continued": continued, **({"beat": beat} if beat is not None else {}),
         **({"relance": relance[0]} if relance else {}),
         **({"allowance": allowance} if allowance is not None else {})}])
    if not made:
        return count                                             # paused meanwhile: nobody woken
    intent = made[-1]
    count += len(made)
    own = member_vector(root, conductor, name, started, agent)
    vectors, code = vectors_of(state, agent, task) + ([own] if own else []), ""
    try:                                                         # the intent written: what raises before the launch
        fresh = state_of(journal)                                # is the house's refusal, never the tick's death
        report, why, code = launched(root, conductor, name, started, path, run, tag,
                                   headed(name, agent, box, history, fresh, relance, task, continued, beat), allowance,
                                   member=agent, vectors=vectors or [EMPTIED])
    except Exception as error:                                   # noqa: BLE001 -- any cause, said whole
        report, why = None, f"{type(error).__name__}: {error}"
    if report is None and vectors and code == VECTOR_REFUSED:    # the launcher refused the run its node: said, final
        return count + len(appended(conductor, root, journal, name, vector_refused(state_of(journal), intent, why, vectors)))
    if report is None:                                           # the house refused, before any harness: no fall
        return count + len(appended(conductor, root, journal, name, house_failed(state_of(journal), name, intent, why)))
    born = space_now()
    try:                                                         # launched: a naming that raises is a name refused
        refused = "" if run else run_named(root, conductor, path, str(report.get("key")), carrier_name(fresh, name, carrier_of(fresh, task)))
    except Exception as error:                                   # noqa: BLE001 -- the launch plays on unnamed
        refused = f"{type(error).__name__}: {error}"
    made = written(conductor, root, journal, name, lambda now_state, events: [
        {"kind": "wake-launched", "tag": tag, "agent": agent, "run": report.get("key"), "pid": report.get("pid"),
         "launch": launches_of_run(now_state, str(report.get("key"))) + 1, **launch_kept(started, agent),
         **({"space": born} if born else {}),               # the launcher's process space: this tick's own
         **({"name-refused": refused} if refused else {})}])
    following(root, conductor, name, tag)
    return count + len(made)


def renewal_of(state: dict, agent: str, task: str, run: str | None) -> dict | None:
    """-> the `run-renewed {member, task, run, why, ...}` the member's wake-up on `task` writes before its intent, None
    when it resumes `run` -- the ONE decision of a renewal, read at a wake-up, never in the middle of a passage: a run
    STANDING on the task is continued until it parks, unless its PROVIDER changed -- a session lives under its provider
    alone, and `agent start` refuses to resume it under another (`provider-mismatch`). Two causes, the first that holds:
    - `why: model` -- the run was opened under another model or provider than the season's profile gives the member
      now (`opened_under`, `launch_kept`), with `was` and `now`; a run whose opening kept no trace is not renewed so;
    - `why: context` -- the last measure of `run` (the last `wake-ended` of that run that carries a context, read from
      the journal alone) reached the limit, with `used` and `limit`: on an OCCURRENCE, its recurrence's `context`, at
      the member's FIRST wake-up on it (an occurrence is never cut between two runs), `recurrence` said; on a task of
      its own carrier, the task's `context` (its `post --context`), else the season's (`context:` of SEASON.md).
    Without a limit, without a measure, or under it, the run is resumed."""
    if run is None:
        return None
    was, now = opened_under(state, run), launch_kept(state["started"] or {}, agent)
    if (agent, task) in state["standing"] and (was is None or was["provider"] == now["provider"]):
        return None
    held = state["tasks"].get(task) or {}
    recurrence = state["recurrences"].get(held.get("recurrence"))
    head = {"kind": "run-renewed", "member": agent, **({"recurrence": recurrence["id"]} if recurrence else {}),
            "task": task, "run": run}
    if was is not None and was != now:
        return {**head, "why": "model", "was": was, "now": now}
    if recurrence is not None:
        limit = recurrence.get("context")
        if any(one.get("agent") == agent and one.get("task") == task for one in state["intents"].values()):
            return None
    elif carrier_of(state, task) == task:
        limit = held.get("context") if held.get("context") is not None else state["limits"].get("context")
    else:
        return None
    measure = next((one["context"] for one in reversed(state["ends"])
                    if one.get("run") == run and isinstance(one.get("context"), dict)), None)
    used = (measure or {}).get("used")
    if limit is None or not isinstance(used, (int, float)) or used * 100 < limit:
        return None
    return {**head, "why": "context", "used": used, "limit": limit}


def launch_kept(started: dict, member: str) -> dict:
    """-> `{model, provider}` a member's launch takes from the season: its profile's, else the team's launch -- `null`
    when neither names one."""
    kept, profile = started.get("launch") or {}, profile_of(started, member)
    return {key: profile.get(key) if profile.get(key) is not None else kept.get(key) for key in ("model", "provider")}


def opened_under(state: dict, run: str) -> dict | None:
    """-> `{model, provider}` the run was OPENED under: what its first `wake-launched` kept; None when that launch kept
    neither (a journal of before team 1.24.0)."""
    first = next((one for one in state["launched"].values() if one.get("run") == run), None)
    if first is None or not ("model" in first or "provider" in first):
        return None
    return {key: first.get(key) for key in ("model", "provider")}


def dues(state: dict, agent: str) -> list[tuple[str, list[dict]]]:
    """-> what a launch of the agent would deliver, task by task in the tasks' order: (task, its inbox
    on that task) for each task that has some -- a stopped task has none to deliver, its stop delivered
    at once, unless a run of the agent STANDS on it, (agent, task): then its stop alone, the head of one more launch
    (the run parks there)."""
    waiting = inbox(state, agent)
    found = []
    for task, held in state["tasks"].items():
        if held.get("state") == "resolved":
            continue
        box = [one for one in waiting if one.get("task") == task]
        if held.get("state") == "stopped":
            box = [one for one in box if one.get("verb") == "stop" and (agent, task) in state["standing"]]
        if box:
            found.append((task, box))
    return found


def quiet(state: dict, one: dict) -> bool:
    """-> whether a message launches nobody: a MEMBER's `info` -- it waits in its recipient's box and rides the head of
    its next launch, whatever its cause; an `info` of a principal or of the team is due as any message (row 114)."""
    return one.get("verb") == "info" and is_member(state, one.get("from"))


def loud(state: dict, box: list[dict]) -> list[dict]:
    """-> the messages of a box that make their recipient due: every one but the members' `info`s (`quiet`)."""
    return [one for one in box if not quiet(state, one)]


def ticked(root: Path, conductor, name: str, hint: tuple[str, str] | None = None) -> int:
    """ONE advance of the team under `tick.lock`, taken without waiting: held, the mark is
    posted and the tick leaves; the holder clears the mark, ARMS the timer on the deadline the state read now
    gives (`armed`) -- a tick killed at any point after it, in a launch above all, leaves its net standing --, plays
    reap, ring, wake and the net again (the relaunch entry removed and the timer disarmed at `schedule-off`,
    the timer armed again when a deadline stands: an earlier hour replaces the standing one, a later one keeps it),
    releases, then reads the mark and plays again when it is set. Off season it reaps alone and the net leaves.
    `hint` is what an on-end tick carries of the
    launch that fired it: `(run, state)`. -> the events written."""
    journal = journal_of(root, name)
    if state_of(journal)["started"] is None:
        print(f"pp-team: {name} · not started: nothing to advance")
        return 0
    lock = locks(conductor)
    home = journal.parent
    home.mkdir(parents=True, exist_ok=True)
    path, mark = home / TICK_LOCK, home / TICK_MARK
    lease = lock.try_(path)
    if lease is None:
        try:
            with open(mark, "x", encoding="utf-8") as handle:
                handle.write(now() + "\n")
        except FileExistsError:
            pass
        lease = lock.try_(path)
        if lease is None:
            print(f"pp-team: {name} · a tick plays: marked pending")
            return 0
    count, rounds = 0, 0
    while True:
        mark.unlink(missing_ok=True)
        rounds += 1
        count += armed(root, conductor, name, journal)   # 0. the net first: a tick killed past here leaves its timer
        count += reaped(root, conductor, name, journal, hint)
        hint = None
        if not state_of(journal)["stopped"]:       # off season: the ends reaped, nothing rung, sounded or woken
            count += rung(conductor, root, name, journal)
            count += sounded(conductor, root, name, journal)
            count += woken(root, conductor, name, journal)
        if netless(state_of(journal)):             # 7. the net, under the lock: a tick that arms and one that
            relaunch_removed(root, conductor, name)   # disarms never cross -- the condition of schedule-off: the
            disarmed(root, name)                   # net leaves with it
        else:
            count += armed(root, conductor, name, journal)   # the timer, when a deadline stands
        lock.release(lease)
        if not mark.exists():
            break
        lease = lock.try_(path)
        if lease is None:
            break                                              # the tick that marked plays now
    print(f"pp-team: {name} · tick · {count} event(s) written in {rounds} round(s)")
    if state_of(journal)["paused"]:
        print(f"pp-team: {name} · paused: nobody woken until team resume")
    return count


def tick(rest: list[str]) -> int:
    global TIMER_TICKING
    TIMER_TICKING = os.environ.pop(TIMER_ENV, "") == "1"     # the timer's own tick: taken out, no child inherits it
    root, conductor = house()
    if rest == ["--all", "--entry"]:              # the relaunch entry: the PATH of the process that laid it, taken up
        kept = kept_path(root)
        if kept.is_file():
            os.environ["PATH"] = kept.read_text(encoding="utf-8")
        rest = ["--all"]
    if rest == ["--all"]:
        for name in needing(root):                 # the house's relaunch entry at logon: every team in need
            try:
                ticked(root, conductor, name)
            except SystemExit as failed:           # a team that refuses is said; the others advance
                if failed.code not in (0, None):
                    sys.stderr.write(f"pp-team: {name} · tick failed, the other teams advance\n")
        return 0
    name, rest = named_team(conductor, rest)
    if rest:
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    run, said = os.environ.get("PP_AGENT_RUN", "").strip(), os.environ.get("PP_AGENT_STATE", "").strip()
    ticked(root, conductor, name, (run, said) if run and said else None)   # an on-end tick says its launch's end
    return 0


# --- the verbs -----------------------------------------------------------------------------

MEMBER_FLAGS = {"provider": True, "model": True, "effort": True, "permissions": True, "package": True, "silence": True}


def season_flags(rest: list[str]) -> tuple[list[str], list[str], dict]:
    """-> (the team's flags, the team's packages, the members' profiles): what follows a `--member <name>` up to the
    next one is that member's -- `--provider`, `--model`, `--effort`, `--permissions` and `--package <name>=on|off`
    repeated --, as `{member: {key: value, packages: [...]}}`; the flags before the first `--member` are the team's,
    its `--package <name>=on|off`, repeated, taken apart as the team's packages. Anything else is the usage."""
    at, team_part, packages, profiles = 0, [], [], {}
    while at < len(rest) and rest[at] != "--member":
        if rest[at] == "--package":
            if at + 1 >= len(rest):
                refuse(USAGE)
            packages.append(rest[at + 1])
            at += 2
            continue
        team_part.append(rest[at])
        at += 1
    while at < len(rest):
        if at + 1 >= len(rest) or rest[at + 1].startswith("--"):
            refuse(USAGE)
        profile = profiles.setdefault(rest[at + 1], {})
        at += 2
        while at < len(rest) and rest[at] != "--member":
            key = rest[at][2:] if rest[at].startswith("--") else ""
            if key not in MEMBER_FLAGS or at + 1 >= len(rest):
                refuse(USAGE)
            if key == "package":
                profile.setdefault("packages", []).append(rest[at + 1])
            else:
                profile[key] = rest[at + 1]
            at += 2
    return team_part, packages, profiles


def season_of(asked: dict) -> dict:
    """-> the season's own limits, `{budget, budget-launches, silence, context}` -- the ones given, each judged: a number
    of dollars above 0, whole numbers of 1 or more, a share of the window (`window_share`); DECLINES `budget-invalid`,
    `team-invalid` for `--silence`, `context-invalid` for `--context`."""
    found: dict = {}
    if asked.get("context") is not None:
        found["context"] = window_share(str(asked["context"]))
        if found["context"] is None:
            decline(context_invalid(str(asked["context"])))
    if asked["budget"] is not None:
        try:
            found["budget"] = float(asked["budget"])
        except ValueError:
            found["budget"] = 0.0
        if not found["budget"] > 0:
            decline(f"budget-invalid -- `--budget {asked['budget']}`: a number of dollars above 0.")
    if asked["budget-launches"] is not None:
        if not str(asked["budget-launches"]).isdigit() or int(asked["budget-launches"]) < 1:
            decline(f"budget-invalid -- `--budget-launches {asked['budget-launches']}`: a whole number of 1 or more.")
        found["budget-launches"] = int(asked["budget-launches"])
    if asked.get("silence") is not None:
        if not str(asked["silence"]).isdigit() or int(asked["silence"]) < 1:
            decline(f"team-invalid -- `--silence {asked['silence']}`: a whole number of 1 or more.")
        found["silence"] = int(asked["silence"])
    return found


def manifests_named(root: Path, conductor) -> dict[str, Path]:
    """-> {package name: its vendored root} over the house's WHOLE composition, switched off included."""
    named: dict = {}
    for package_root in conductor.instance.vendored(root, switched=False):
        try:
            named[str(conductor.instance.manifest_of(package_root)["name"])] = package_root
        except conductor.Refusal:
            continue
    return named


def required_by_team(root: Path, conductor) -> set[str]:
    """-> `team` and every package it requires, transitively, as the house's manifests say them
    (`topology.closure`)."""
    return conductor.topology.closure(manifests_named(root, conductor), "team")


def switches_composed(*lists: list) -> dict[str, str]:
    """-> `{name: "on"|"off"}` from lists of `<name>=on|off`, each later list covering the earlier name by name, the
    last word on a name winning within a list; the order is the order the names first came."""
    found: dict[str, str] = {}
    for values in lists:
        for value in values or []:
            name, _, state = str(value).partition("=")
            found[name] = state
    return found


def season_switches(started: dict, member: str | None = None) -> dict[str, str]:
    """-> the switches the season gives a member's wake-up, `{name: "on"|"off"}`: the team's packages
    (`team-started.packages`), covered name by name by the member's profile; the team's alone without a member."""
    return switches_composed(started.get("packages") or [], profile_of(started, member).get("packages") or [])


def season_set(root: Path, conductor, switches: dict[str, str]) -> list[str]:
    """-> the SET of a member's packages a season gives, `[<name>=on|off, ...]`: one per pin of the house beyond its
    base, in the pins' order -- `on` when `switches` switches it on or the team requires it (`required_by_team`),
    `off` otherwise. The one rule of a season's packages: `start` writes it, and a journal of before, whose list
    names some pins alone, is read under it -- a pin it does not name is off. The member's SETTINGS plays no part."""
    instance = conductor.instance
    base, needed = instance.base_of(root), required_by_team(root, conductor)
    return [f"{name}={switches.get(name) or ('on' if name in needed else 'off')}"
            for name in instance.pins(root) if name != base]


def set_of(values: list) -> dict[str, str]:
    """-> `{name: on|off}` of a set (`season_set`), in its order."""
    return switches_composed(values)


def season_played(root: Path, conductor, started: dict, member: str | None = None) -> list[str]:
    """-> the set a member's wake-up plays: the season's lists at `team-started` (`season_switches`) read under the
    rule of the set (`season_set`) -- the journal's set itself, every pin of a journal of before named."""
    return season_set(root, conductor, season_switches(started, member))


def profiles_judged(root: Path, conductor, team: dict, packages: list, profiles: dict) -> None:
    """Judges the team's packages and the members' profiles before any write: a member nobody declared
    (`participant-unknown`), a switch off its form (`package-invalid`), a package the team needs switched off
    (`package-required` -- `team` and what it requires), a package the house does not pin switched on
    (`package-unpinned`), a package switched on whose requirement the season's SET -- the team's switches covered by
    the member's, every other pin off unless the team requires it (`season_set`) -- switches off
    (`package-dependency`). A package the house does not pin, switched off, asks nothing: it leaves the set."""
    if not packages and not profiles:
        return
    named = manifests_named(root, conductor)
    needed = conductor.topology.closure(named, "team")
    pinned = set(conductor.instance.pins(root))

    def judged(values: list, whom: str) -> None:
        for value in values or []:
            package, _, state = str(value).partition("=")
            if not package or state not in ("on", "off"):
                decline(f"package-invalid -- `--package {value}` for {whom}: the form is <name>=on or <name>=off.")
            if state == "off" and package in needed:
                decline(f"package-required -- `{package}` cannot be switched off for {whom}: the team needs it "
                       f"({', '.join(sorted(needed))}).")
            if package not in pinned and state == "on":
                decline(f"package-unpinned -- `{package}` is not pinned by the house: the packages it pins are "
                       f"{', '.join(sorted(pinned))}.")

    def dependent(composed: dict, whom: str) -> None:
        off = {name for name, state in composed.items() if state == "off"}
        for name, state in composed.items():
            if state != "on":
                continue
            lacking = sorted((conductor.topology.closure(named, name) - {name}) & off)
            if lacking:
                decline(f"package-dependency -- `{name}=on` for {whom} needs {', '.join(lacking)}, which the season "
                       "switches off: a package never plays without what it requires.")

    judged(packages, "the team")
    dependent(set_of(season_set(root, conductor, switches_composed(packages))), "the team")
    for member, profile in profiles.items():
        if member not in team["agents"]:
            decline(f"participant-unknown -- `--member {member}` names a member nobody declared.")
        if profile.get("silence") is not None:
            if not str(profile["silence"]).isdigit() or int(profile["silence"]) < 1:
                decline(f"team-invalid -- `--member {member} --silence {profile['silence']}`: a whole number of 1 or more.")
            profile["silence"] = int(profile["silence"])
        judged(profile.get("packages") or [], member)
        dependent(set_of(season_set(root, conductor, switches_composed(packages, profile.get("packages") or []))),
                  member)


def start(rest: list[str]) -> int:
    """`team start`: a SEASON of the team -- the first, or the next one OFF SEASON, after `team stop`: a team in season
    refuses `season-running`, naming `team stop`; a start after a stop writes `since`, the hour from which nothing
    passed off season is caught up. `TEAM.md` read whole and
    judged, the season SEASON.md writes -- its launch, budget, packages, profiles and work, each covered by the
    start's flag for the same key (`season_opened`) -- and the gestures judged before any write; then the flags'
    values written into SEASON.md (`season_flagged`), the agents the house lacks born, the team's documents written,
    `team-started` (its `season`, `packages` and `profiles` when given)
    and, under `--message`, a task and its `do` -- without it no task opens, the season stands on its ceremonies and
    the posts to come; the relaunch entry laid under an open task or a declared ceremony, the first `post` laying it
    otherwise; a tick unless `--no-tick`. The members keep their runs."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if "--max-budget-usd" in rest:
        refuse("flag-retired -- `--max-budget-usd`: no cap per wake-up any more -- a wake-up's share is computed on "
               "the team's `budget:` of TEAM.md (each its part of the rest), and `team budget` raises it.")
    retired_flags(rest)
    team_part, flagged_packages, flagged_profiles = season_flags(rest)
    asked = flags(team_part, START_FLAGS)
    team = declared(root, conductor, name)
    try:                                               # SEASON.md, each value covered by its flag, judged whole
        opened = season_opened(root, conductor, name, team, asked, flagged_packages, flagged_profiles)
    except Declined as declining:
        refuse(str(declining))
    season, packages, profiles = opened["season"], opened["packages"], opened["profiles"]
    journal = journal_of(root, name)
    before = state_of(journal)
    if before["deleting"]:
        refuse(deleting_said(name))
    running = in_season(name, before, "a start")
    if running:
        refuse(running)
    standing = [one["id"] for one in before["tasks"].values() if one["state"] == "open"]
    naming = named(conductor, asked) if asked["message"] is not None else {}
    target = asked["to"] or team["root"]
    if target not in team["agents"]:
        refuse(f"participant-unknown -- `--to {target}` names a member nobody declared.")
    try:
        entries_judged(root, conductor, name, team)
        rendering, planned = documents_planned(root, conductor, name, before["started"], team)
    except Declined as declining:
        refuse(str(declining))
    for key, members in team["roles"].items():         # said, never refused: an author reserves a key
        if not members:
            print(f"pp-team: {name} · role `{key}` has no member -- reserved", file=sys.stderr)
    for one in rendering["documents"]:                 # said, never refused: a key reserved
        if one["members"] == []:
            print(f"pp-team: {name} · document `{one['template']}` reaches nobody -- no member holds "
                  f"{', '.join(f'`{key}`' for key in one['roles'])}", file=sys.stderr)
    season_path = team_root(root, name) / SEASON_DOC
    if season_flagged(conductor, season_path, asked, flagged_packages, flagged_profiles) and rendering["season"]:
        rendering["season"] = hashlib.sha256(season_path.read_bytes()).hexdigest()[:12]   # the file the season keeps
    created = born(root, conductor, list(team["agents"].values()))
    launch = opened["launch"]
    rendered = documents_written(root, conductor, name, team, launch, profiles, planned)
    cleared(root, name, team)
    owner = owner_of(root, conductor)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["deleting"]:
            refuse(deleting_said(name))
        running = in_season(name, state, "a start")
        if running:
            refuse(running)
        made = [{"kind": "team-started", "agents": team["agents"], "reports": team["reports"], "root": team["root"],
                 "principals": team["principals"], "owner": owner, "ceremonies": team["ceremonies"],
                 "entries": team["entries"], "roles": team["roles"], "work": opened["work"],
                 "launch": launch, "limits": team["limits"],
                 **({"season": season} if season else {}), "packages": packages,
                 **({"profiles": profiles} if profiles else {}),
                 "schedule": team["schedule"], "unit": "s", "digest": team["digest"],
                 **({"template": template_kept(team)} if team["template"] else {}),
                 **({"values": values_kept(team)} if team["applied"] else {}),
                 "documents": documents_kept(rendering), "rendered": rendered,
                 **({"season-digest": rendering["season"]} if rendering["season"] else {}),
                 **({"since": tick_now().isoformat(timespec="seconds")} if state["stopped"] else {})}]
        if asked["message"] is not None:
            task = next_task(state)
            made += [{"kind": "task", "task": task, "from": owner, "to": target, **naming, "text": asked["message"]},
                     {"kind": "post", "task": task, "from": owner, "to": target, "verb": "do", "text": asked["message"]}]
        return made

    made = written(conductor, root, journal, name, judge)
    said = (f" · task {made[1]['task']} to {target} · post #{made[2]['id']} do {owner} -> {target}"
            if len(made) > 1 else " · no task opened" + (f", {', '.join(standing)} open" if standing else ""))
    print(f"pp-team: {name} started · members {', '.join(team['agents'])}"
          + (f" (born: {', '.join(created)})" if created else " (all standing)") + said)
    if team["schedule"] is not None and not netless(state_of(journal)):   # the relaunch entry under a task, a
        relaunch_said(root, conductor, name, journal)                    # ceremony or a recurrence; the first post
        #                                                                  lays it otherwise; the tick arms the timer
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def principal_of(state: dict, owner: str, asked: str | None) -> str:
    """-> who posts: the mandator `--as` names (declared under `principals:`) or the owner."""
    if asked is None:
        return owner
    allowed = [owner] + list((state["started"] or {}).get("principals") or [])
    if asked not in allowed:
        refuse(f"principal-unknown -- `--as {asked}`: the principals are {', '.join(allowed)} (the owner, then "
               "`principals:` of TEAM.md).")
    return asked


def window_share(text: str) -> int | None:
    """-> the context limit a text says: a whole percentage of the window from 1 to 99, `70` worth `70%`; None for any
    other text."""
    said = text.strip()
    number = said[:-1] if said.endswith("%") else said
    return int(number) if number.isdigit() and 1 <= int(number) <= 99 else None


def context_invalid(text: str, off: bool = False) -> str:
    """-> the refusal of a context limit `window_share` does not read."""
    return (f"context-invalid -- `--context {text.strip()[:20]}`: a context limit is a share of the window, "
            "1% to 99%" + (", or off" if off else "") + ".")


def limit_of(text: str, off: bool = False) -> int | None:
    """-> the context limit `--context` says (`window_share`) -- of a recurrence, of a task at its birth, of a season --;
    None for `off` where `off` is allowed (the limit taken away); `context-invalid` otherwise."""
    if off and text.strip() == "off":
        return None
    limit = window_share(text)
    if limit is None:
        refuse(context_invalid(text, off))
    return limit


def post(rest: list[str]) -> int:
    root, conductor = machine_house()                      # the house's team, whatever instance posts
    name, rest = named_team(conductor, rest)
    asked = flags(rest, POST_FLAGS)
    if asked["reply"] is not None and (asked["task"] is None or asked["stop"]):
        refuse(USAGE)
    if asked["ask"] and (asked["task"] is None or asked["reply"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a principal's question: on an open task, alone
    if asked["name"] is not None and asked["task"] is not None:   # a name is given at a task's birth alone
        refuse(USAGE)
    if asked["every"] is not None and (asked["task"] is not None or asked["reply"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a recurrence is laid on a task to come alone
    if asked["description"] is not None and asked["every"] is None:
        refuse(USAGE)                                             # a description: a recurrence's alone
    if asked["context"] is not None and (asked["task"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a context limit: a recurrence's, or a task's at its birth
    if asked["vector"] and (asked["task"] is not None or asked["every"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a vector is laid on a task at its birth alone
    for vector in asked["vector"]:
        if not vector_formed(vector):
            refuse(f"vector-invalid -- `{vector}`: a vector is `<family>:<id>`, both sides said, no blank.")
    vectors = list(dict.fromkeys(asked["vector"]))
    limit = limit_of(asked["context"]) if asked["context"] is not None else None
    describing = {} if asked["description"] is None else {"description": recurrence_description(asked["description"])}
    when = None
    if asked["every"] is not None:
        when = every_of(asked["every"])
    if asked["message"] is None and not asked["stop"]:
        refuse("message-missing -- a post carries its text: --message <text> (optional under --stop).")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)
    naming = named(conductor, asked)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        started = state["started"]
        if started is None:
            refuse(f"team-not-started -- {name} was never started: `team start {name} --message …` first.")
        if state["deleting"]:
            refuse(deleting_said(name))
        if state["stopped"]:
            refuse(off_season(name, state))
        agents = list(started.get("agents") or {})
        sender = principal_of(state, owner, asked["as"])
        if asked["to"] is not None and asked["to"] not in agents:
            refuse(f"participant-unknown -- `--to {asked['to']}` names a member nobody declared.")
        if when is not None:                      # a recurrence: nothing opens now, the tick sounds its periods
            return [{"kind": "recurrence", "recurrence": f"R{len(state['recurrences']) + 1}", "from": sender,
                     "to": asked["to"] or str(started.get("root")), **naming, "text": asked["message"], "when": when,
                     "since": tick_now().isoformat(timespec="seconds"), "context": limit, **describing}]
        if asked["task"] is None:
            target = asked["to"] or str(started.get("root"))
            task = next_task(state)
            return [{"kind": "task", "task": task, "from": sender, "to": target, **naming, "text": asked["message"],
                     **({"vectors": vectors} if vectors else {}), **({"context": limit} if limit is not None else {})},
                    {"kind": "post", "task": task, "from": sender, "to": target, "verb": "do", "text": asked["message"]}]
        task = state["tasks"].get(asked["task"])
        if task is None:
            refuse(f"task-unknown -- no task `{asked['task']}` of {name}: the tasks are "
                   f"{', '.join(state['tasks']) or 'none'}.")
        if task["state"] in CLOSED:
            refuse(f"task-closed -- {task['id']} is {task['state']}: a post opens a new task instead.")
        verb, cited = ("ask" if asked["ask"] else "info"), None   # a note informs; `--ask` asks, an answer due
        target = asked["to"] or task["to"]
        if asked["stop"]:
            text = asked["message"] if asked["message"] is not None else ""
            return stopping(state, task, sender, text, [target] if asked["to"] else holders(state, task))
        if asked["reply"] is not None:
            try:
                cited = int(asked["reply"].lstrip("#"))
            except ValueError:
                cited = -1
            answered = state["messages"].get(cited)
            if answered is None or answered.get("task") != task["id"]:
                refuse(f"message-unknown -- no post #{asked['reply']} on {task['id']}.")
            verb = "re"
            if asked["to"] is None and answered.get("from") in agents:
                target = str(answered["from"])
            elif asked["to"] is None and answered.get("about") in agents:
                target = str(answered["about"])
        one = {"kind": "post", "task": task["id"], "from": sender, "to": target, "verb": verb,
               "text": asked["message"] if asked["message"] is not None else ""}
        if cited is not None:
            one["re"] = cited
        return [one]

    made = written(conductor, root, journal, name, judge)
    if made[0]["kind"] == "recurrence":
        print(f"pp-team: {name} · recurrence {made[0]['recurrence']} to {made[0]['to']} · every "
              f"{said_when(made[0]['when'])}"
              + (f" · context {made[0]['context']}%" if made[0]["context"] is not None else "")
              + f" · #{made[0]['id']} -- the tick opens one task per period")
    if made[0]["kind"] == "task":
        print(f"pp-team: {name} · task {made[0]['task']} to {made[0]['to']}"
              + (f" · context {made[0]['context']}%" if made[0].get("context") is not None else "")
              + f" · post #{made[1]['id']} do {made[1]['from']} -> {made[1]['to']}")
    for one in made:
        if one["kind"] == "stopped":
            posted = any(other["kind"] == "post" for other in made)
            print(f"pp-team: {name} · {one['task']} · stopped #{one['id']}" + ("" if posted else " -- nobody held it"))
        elif one["kind"] == "post" and made[0]["kind"] != "task":
            print(f"pp-team: {name} · {one['task']} · post #{one['id']} {one['verb']} {one['from']} -> {one['to']}")
        elif one["kind"] == "returned":
            print(f"pp-team: {name} · post #{one['message']} returned to {one['to']}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # a post lays the net again when it finds it gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def holders(state: dict, task: dict) -> list[str]:
    """-> the agents holding the task: its agent unless it is terminal on it, then every delegate
    on it without a terminal, in the order of their delegations."""
    found = [] if (task["to"], task["id"]) in state["terminals"] else [str(task["to"])]
    for one in state["delegations"]:
        if one["task"] == task["id"] and (one["to"], task["id"]) not in state["terminals"] and one["to"] not in found:
            found.append(str(one["to"]))
    return found


def stopping(state: dict, task: dict, sender: str, text: str, to: list[str]) -> list[dict]:
    """-> the events that stop a task: `stopped {task, by}` -- the task stops whatever holds it --,
    then a `stop` post to each agent named (none when nobody holds the task), then a `returned`
    for every post left undelivered on the task, to its author."""
    events: list[dict] = [{"kind": "stopped", "task": task["id"], "by": sender}]
    events += [{"kind": "post", "task": task["id"], "from": sender, "to": one, "verb": "stop", "text": text}
               for one in to]
    for mid in task["messages"]:
        one = state["messages"][mid]
        if mid not in state["delivered"]:
            events.append({"kind": "returned", "message": mid, "to": one.get("from")})
    return events


def ended_now(pid: int) -> bool:
    """Ends a detached launcher by its process group -- the launcher, the harness it runs and
    what that runs. -> False when the group was gone already. Windows: `taskkill /T`."""
    if os.name == "nt":
        return subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True).returncode == 0
    try:
        os.killpg(pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError):
        return False
    return True


def kills(root: Path, conductor, name: str, state: dict, task: str, said: list[str]) -> list[dict]:
    """-> `wake-killed` for every launch under way on the task whose flow says no end, its launcher
    ended by its process group; a launch that answered (its `response` at the flow) is spared -- the reap
    ends it, its cost counted --; a launcher gone already, not launched yet, or born in another process space
    (`foreign`: its pid names nobody here), is said and left to the reap."""
    events = []
    for one in open_intents(state):
        if one["task"] != task:
            continue
        launch = state["launched"].get(one["tag"]) or messages_cursor(root, name, state).get(one["tag"]) or {}
        pid = launch.get("pid")
        if launch.get("run") and answered_in_flow(root, conductor, state, one, launch):
            said.append(f"{task} · {one['agent']} has answered: spared -- the reap ends it")
        elif not isinstance(pid, int):
            said.append(f"{task} · {one['agent']} not launched yet: it ends on its own")
        elif foreign(launch):
            said.append(f"{task} · {one['agent']}'s launcher plays in another process space ({launch.get('space')}): "
                        f"its pid {pid} names nobody here, left to the reap")
        elif ended_now(pid):
            said.append(f"{task} · killed {one['agent']} (pid {pid}, run {launch.get('run')})")
            events.append({"kind": "wake-killed", "tag": one["tag"], "agent": one["agent"], "task": task,
                           "run": launch.get("run"), "pid": pid})
        else:
            said.append(f"{task} · {one['agent']}'s pid {pid} is gone already")
    if not any(line.startswith(f"{task} · killed") for line in said):
        said.append(f"{task} · nothing to kill")
    return events


def stop(rest: list[str]) -> int:
    """`team stop <name> [--task <id>] [--recurrence <R<n>>] [--kill] [--json] [--no-tick]`: without `--task` nor
    `--recurrence`, the SEASON stopped -- each open task stopped (`stopping`; `--kill` kills its runs too), then
    `season-stopped {by, tasks, recurrences}`, the tasks stopped and the recurrences it silences -- live and not
    paused: a paused one is silent already, is not named, and stays paused --, each kept as it stands; until the
    next `team start` the team is OFF SEASON: the tick wakes, rings and sounds nothing, its net leaves, and only then
    are `TEAM.md` and `SEASON.md` written. With `--task`, one task stopped; with `--recurrence`,
    one recurrence -- in season alone. Judged under the journal's lock: `team-not-started`, `season-stopped` (off
    season already). Under `--json` ONE object `{team, stopped: {id, tasks, recurrences}}` for a season stopped."""
    root, conductor = machine_house()                      # the house's team, whatever instance stops it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, STOP_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    said: list[str] = []
    if asked["recurrence"] is not None and (asked["task"] is not None or asked["kill"]):
        refuse(USAGE)                                             # a recurrence stops alone: its occurrence by --task
    season = asked["recurrence"] is None and asked["task"] is None

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["stopped"]:
            refuse(off_season(name, state))
        if asked["recurrence"] is not None:            # a suspended one stops as well
            recurrence = held_recurrence(state, name, asked["recurrence"])
            return [{"kind": "recurrence-stopped", "recurrence": recurrence["id"], "by": owner}]
        if asked["task"] is not None:
            task = state["tasks"].get(asked["task"])
            if task is None:
                refuse(f"task-unknown -- no task `{asked['task']}` of {name}.")
            if task["state"] in CLOSED:
                refuse(f"task-closed -- {task['id']} is {task['state']} already.")
            chosen = [task]
        else:
            chosen = [one for one in state["tasks"].values() if one["state"] == "open"]
        made: list[dict] = []
        for task in chosen:
            if asked["kill"]:
                made += kills(root, conductor, name, state, task["id"], said)
            made += stopping(state, task, owner, "", holders(state, task))
        if season:
            made.append({"kind": "season-stopped", "by": owner, "tasks": [task["id"] for task in chosen],
                         "recurrences": [one["id"] for one in live_recurrences(state) if not one.get("paused")]})
        return made

    made = written(conductor, root, journal_of(root, name), name, judge)
    closing = next((one for one in made if one["kind"] == "season-stopped"), None)
    if made[0]["kind"] == "recurrence-stopped":
        print(f"pp-team: {name} · recurrence {made[0]['recurrence']} stopped #{made[0]['id']} -- its open occurrence "
              "lives on")
    for line in said:
        print(f"pp-team: {name} · {line}")
    for one in made:
        if one["kind"] == "stopped":
            posted = any(other["kind"] == "post" and other.get("task") == one["task"] for other in made)
            print(f"pp-team: {name} · {one['task']} · stopped #{one['id']}" + ("" if posted else " -- nobody held it"))
        elif one["kind"] == "post":
            print(f"pp-team: {name} · {one['task']} · post #{one['id']} stop {one['from']} -> {one['to']}")
        elif one["kind"] == "returned":
            print(f"pp-team: {name} · post #{one['message']} returned to {one['to']}")
    if closing is not None:
        print(f"pp-team: {name} · season stopped #{closing['id']} by {closing['by']} · tasks stopped: "
              f"{', '.join(closing['tasks']) or 'none'} · recurrences silenced: {', '.join(closing['recurrences']) or 'none'}"
              f" -- off season until `team start {name}`")
    if netless(state_of(journal_of(root, name))):
        relaunch_removed(root, conductor, name)    # the last task stopped, no ceremony, or off season: the net leaves
        disarmed(root, name)
    if asked["json"] and closing is not None:
        print(json.dumps({"team": name, "stopped": {key: closing[key] for key in ("id", "tasks", "recurrences")}},
                         ensure_ascii=False))
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def off_season(name: str, state: dict) -> str:
    """-> the refusal `season-stopped` of a gesture that needs a season under way."""
    stopped = state["stopped"] or {}
    return (f"season-stopped -- {name} is off season since #{stopped.get('id')} (`team stop`): `team start {name}` "
            "opens the next season.")


def in_season(name: str, state: dict, what: str) -> str | None:
    """-> the refusal `season-running` of `what` -- a write of `TEAM.md` or `SEASON.md`, a start -- while a season
    is under way (started, not stopped), None off season or before a first start."""
    if state["started"] is None or state["stopped"]:
        return None
    return (f"season-running -- {name} is in season since #{state['started'].get('id')}: {what} waits off season -- "
            f"`team stop {name}` ends the season, then write, then `team start {name}`.")


def snapshot_verb(rest: list[str]) -> int:
    """`team snapshot <name>`: ONE `snapshot {upto, state}` event, written under the
    journal's lock -- the replay restarts there; nothing is rewritten, no reader changes."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if rest:
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started: `team start {name} --message …` first.")
        last = max((int(one.get("id") or 0) for one in events), default=0)
        return [{"kind": "snapshot", "upto": last, "state": packed(state)}]

    made = written(conductor, root, journal_of(root, name), name, judge)
    print(f"pp-team: {name} · snapshot #{made[0]['id']} upto #{made[0]['upto']}")
    return 0


def counted(messages: list[dict]) -> str:
    """-> `do 1, note 2`: the messages by verb, in the order the verbs appear."""
    seen: dict[str, int] = {}
    for one in messages:
        seen[one.get("verb", "?")] = seen.get(one.get("verb", "?"), 0) + 1
    return ", ".join(f"{verb} {count}" for verb, count in seen.items())


def changed_since_start(root: Path, name: str, started: dict) -> bool:
    """-> whether `TEAM.md` differs from the `digest` its start kept, or `SEASON.md` from the digest its start kept
    (`team-started.season-digest`) -- a SEASON.md that said no documents nor values at the start counts once it says
    some (`template:`, `documents:` or `values:`)."""
    if bool(started.get("digest")) and (
            hashlib.sha256(team_doc(root, name).read_bytes()).hexdigest()[:12] != started["digest"]):
        return True
    kept = started.get("season-digest")
    season = team_root(root, name) / SEASON_DOC
    read = season_text(season)
    if read is None:
        return kept is not None
    now = hashlib.sha256(season.read_bytes()).hexdigest()[:12]
    lines = read[1] or []
    end = next((at for at, line in enumerate(lines[1:], 1) if line.strip() == BORDER), len(lines))
    head = "\n".join(lines[1:end])
    return now != kept and (kept is not None or re.search(r"^(template|documents|values):", head, re.M) is not None)


def owner_box(state: dict, owner: str) -> list[dict]:
    """-> the posts to the owner and the posts returned to them, in the journal's order."""
    return [one for one in state["messages"].values()
            if one.get("to") == owner or state["returned_to"].get(one["id"]) == owner]


def status_of(root: Path, conductor, name: str) -> int:
    """`team status <name>`: the state read from the journal -- nothing written."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = faced(root, conductor, name)
    started = state["started"]
    if started is None:
        print(f"team {name} · declared, not started")
        return 0
    principals = list(started.get("principals") or [])
    owner = str(started.get("owner"))
    print(f"team {name} · owner {owner} · principals {', '.join(principals) or '—'}"
          f" · started {started.get('at')} (#{started.get('id')})")
    paused = state["paused"]
    if paused:
        print(f"paused since {paused.get('at')} by {paused.get('by')} (#{paused.get('id')}) · nobody is woken "
              f"until team resume")
    if state["stopped"]:
        print(f"off season since {state['stopped'].get('at')} by {state['stopped'].get('by')} "
              f"(#{state['stopped'].get('id')}) · nobody is woken until team start")
    if changed_since_start(root, name, started):
        print("TEAM.md changed since the start · the body reaches the members at their next exchange · "
              "the front matter waits a stop then a start")
    limits = state["limits"]
    if limits:
        said = [f"parallel {limits['parallel']}" if "parallel" in limits else "",
                f"budget {limits['budget']:g} USD" if "budget" in limits else "",
                f"retries {limits['retries']}" if "retries" in limits else "",
                f"timeout {limits['timeout']:g}" if "timeout" in limits else "",
                f"launches {limits['launches']}" if "launches" in limits else "",
                f"budget-launches {limits['budget-launches']}" if "budget-launches" in limits else "",
                f"suspect-max {limits['suspect-max']} s" if "suspect-max" in limits else "",
                f"silence {limits['silence']}" if "silence" in limits else ""]
        print("limits · " + " · ".join(one for one in said if one))
    seasons = int(state.get("seasons") or 1)
    if seasons > 1 or started.get("season") or started.get("profiles"):
        own = started.get("season") or {}
        print(f"season {seasons} · since {started.get('at')}"
              + (f" · budget {own['budget']:g} USD" if own.get("budget") is not None else "")
              + (f" · budget-launches {own['budget-launches']}" if own.get("budget-launches") is not None else "")
              + (f" · silence {own['silence']}" if own.get("silence") is not None else "")
              + (f" · profiles {', '.join(started.get('profiles') or {})}" if started.get("profiles") else "")
              + f" · cost {state['cost']:g} USD, {float(state.get('total') or 0.0):g} USD over every season")
    retired = (started.get("launch") or {}).get("max_budget_usd")
    if retired is not None:
        print(f"launch · the start's --max-budget-usd {float(retired):g} is never passed: a wake-up's share is "
              "computed on budget:")
    seconds = schedule_seconds(started)
    if seconds is None:
        print("schedule · off")
    else:
        face = schedule_face(root, name, started, state)
        print(f"schedule · every {seconds} s · " + ("timer armed" if face["timer"] else "no timer") + " · relaunch "
              + ("laid" if face["relaunch"] else "absent" + (f" ({face['reason']})" if face["reason"] else "")))
    print(f"cost {state['cost']:.2f} USD" + (" · budget spent" if state["budget_spent"] else ""))
    share = share_of(state)
    if share is not None:
        print(f"budget {share['spent']:g}/{share['cap']:g} USD · reserved {share['reserved']:.2f} · "
              f"left {share['left']:.2f}")
    for one in state["recurrences"].values():
        last = state["tasks"].get(one.get("last") or "")
        print(f"{one['id']}" + (f" {one['name']}" if one.get("name") else "")
              + f" · every {said_when(one['when'])} · to {one['to']}"
              + (f" · from {one['task']}" if one.get("task") else "")
              + (f" · context {one['context']}%" if one.get("context") is not None else "")
              + (f" · stopped #{one['stopped']['id']}" if one["stopped"]
                 else f" · paused #{one['paused']['id']}" if one.get("paused") else f" · next {recurrence_next(one)}")
              + (f" · last {last['id']} {last['state']}" if last else ""))
    for task in state["tasks"].values():
        resumed = state["resumed"].get(task["id"]) if task["state"] == "open" else None
        print(f"{task['id']}" + (f" {task['name']}" if task.get("name") else "") + f" · {task['state']}"
              + (f" · resumed #{resumed}" if resumed else "") + (f" · of {task['recurrence']}" if task.get("recurrence") else "")
              + f" · to {task['to']} · {len(task['messages'])} message(s)")
    for agent in started.get("agents") or {}:
        waiting = inbox(state, agent)
        line = (f"{agent} · {path_of(state, agent)} · inbox {len(waiting)}"
                + (f" ({counted([worded(state, one) for one in waiting])})" if waiting else ""))
        held = run_of(state, agent)
        if held is not None:
            key, how, tasks = held
            line += f" · run {key} · {how}" + (f" since {launched_at(state, agent)}" if how == "running" else "")
            line += " · on " + " ".join(tasks) if tasks else ""
        carried = state["runs"].get(agent) or {}
        if len(carried) > 1:                                 # one run per carrier: each said
            line += " · runs " + " ".join(f"{carrier} {run}" for carrier, run in carried.items())
        owed = owed_by(state, agent)
        if owed:
            line += f" · owes {len(owed)}"
        suspicion = suspicion_of(state, agent)
        if suspicion is not None:
            line += f" · suspected · tried again at {suspicion['until']:%H:%M:%S}"
        print(line)
    box = owner_box(state, owner)
    print(f"owner inbox {len(box)}")
    for one in (worded(state, one) for one in box):
        print(f"  #{one['id']} {'question' if one.get('verb') == 'ask' else one.get('verb')} from {one.get('from')} "
              f"on {one.get('task')}" + (f" · about {one['about']}" if one.get("about") else "")
              + (" · returned" if state["returned_to"].get(one["id"]) == owner else ""))
    last = state["last"] or {}
    print(f"last event #{last.get('id')} {last.get('kind')} at {last.get('at')}")
    return 0


def status_object(root: Path, conductor, name: str, state: dict) -> dict:
    """`team status <name> --json`: the team as ONE JSON-ready object, every field read from the
    state the text reads -- the team, its state and what it waits on (`team_state`), its season -- `state`
    `running` or `stopped`, and `stopped {at, by, id}` off season -- and the launch its next wake-up gets, its cost (`cost`, the season's) and `total` (every season's, a snapshot of before
    counting from its own season), its tasks (text, last event, holders, delegations, the wake-ups
    under way on it, their cost, the hour of its birth `at` and of its end `ended`, null while it is open), its
    members (run, state, their role keys `roles` -- the keys of the season's `roles:` that name the member, in the
    order declared, `[]` without one --, their launch, their runs by carrier -- each its own state, hour and context
    (`run_face`) --, the packages their run plays, what waits for
    them, the answers of the others they have not seen, and `vector`, `team-member:<team>/<member>`, when the season's view
    of the member holds a document of a role -- absent otherwise), its ceremonies (the next ring, whether the next tick rings, the last ring
    and who answered it), the owner's box and what still waits for them. `{team, started: null, state:
    "never", waiting_on: []}` for a team never started."""
    started = state["started"]
    if started is None:
        return {"team": name, "started": None, **team_state(state)}
    owner = str(started.get("owner"))
    launch = launch_face(root, conductor, started)
    tasks = []
    for task in state["tasks"].values():
        tasks.append({"id": task["id"], "name": task.get("name"), "text": task.get("text"), "last": task.get("last"),
                      "at": task.get("at"), "ended": task.get("ended") if task["state"] in CLOSED else None,
                      "state": task["state"], "from": task.get("from"), "to": task["to"],
                      "ceremony": task.get("ceremony"), "period": task.get("period"),
                      "recurrence": task.get("recurrence"),
                      "messages": len(task["messages"]), "resumed": state["resumed"].get(task["id"]),
                      "cost": round(float(task.get("cost") or 0.0), 6),
                      "holders": holders(state, task) if task["state"] != "resolved" else [],
                      "dos": [{"id": one["id"], "from": one["from"], "to": one["to"],
                               "answered": answer_of_debt(state, one["id"])}
                              for one in state["delegations"] if one["task"] == task["id"]],
                      "running": running_on(state, task["id"])})
    members = []
    held = started.get("roles") or {}
    for member in started.get("agents") or {}:
        run, how, carried = run_of(state, member) or (None, None, [])
        last = last_launch(state, member) if how == "running" else None
        current = run if run not in (None, "?", "—") else None   # the run of its last launch
        cursor = cursor_of(state, member, current, 10 ** 12)
        members.append({"member": member, "path": path_of(state, member), "run": run, "how": how,
                        "roles": [key for key, names in held.items() if member in names],
                        "since": (last or {}).get("at"), "tasks": carried,
                        "owes": [{"id": key, "verb": state["messages"][key].get("verb"),
                                  "from": state["messages"][key].get("from"), "task": state["messages"][key].get("task")}
                                 for key in owed_by(state, member)],
                        "silence": [{"task": task, "passages": silence_of(state, member, task),
                                     "limit": silence_limit(state, member)} for task in silent_tasks(state, member)],
                        "health": health_face(state, member), "quota": quota_face(state, member),
                        "context": state["context"].get(member),
                        "launch": launch_face(root, conductor, started, member),
                        "runs": [{"carrier": carrier, "run": key, "name": carrier_name(state, name, carrier),
                                  **run_face(state, member, key)}
                                 for carrier, key in (state["runs"].get(member) or {}).items()],
                        "packages": packages_at(root, conductor, path_of(state, member), current,
                                                set_of(season_played(root, conductor, started, member)))["packages"],
                        "pending": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"),
                                     "task": one.get("task")} for one in (worded(state, one) for one in inbox(state, member))],
                        "unseen": [{"member": one.get("agent"),
                                    "task": (state["intents"].get(one.get("tag")) or {}).get("task"), "id": one["id"]}
                                   for one in shared(state, member, cursor)],
                        **({"vector": vector} if (vector := member_vector(root, conductor, name, started, member))
                           else {})})
    ceremonies = []
    for ceremony in started.get("ceremonies") or []:
        rings = [task for task in state["tasks"].values() if task.get("ceremony") == ceremony["name"]]
        last = rings[-1] if rings else None
        ceremonies.append({"name": ceremony["name"], "mode": ceremony["mode"], "when": ceremony.get("when"),
                           "after": ceremony.get("after"), "participants": list(ceremony["participants"]),
                           "facilitator": ceremony["facilitator"], "quorum": ceremony.get("quorum"),
                           "next_due": next_due(ceremony, state), "due": due_period(ceremony, state) is not None,
                           "last": None if last is None else {"period": last.get("period"), "task": last["id"],
                                                               "state": last["state"], "by": last.get("by")},
                           "progress": [] if last is None else
                           [{"member": one, "answered": (one, last["id"]) in state["terminals"]}
                            for one in ceremony["participants"]]})
    recurrences = []
    for one in state["recurrences"].values():
        last = state["tasks"].get(one.get("last") or "")
        recurrences.append({"id": one["id"], "name": one.get("name"), "text": one.get("text"), "from": one.get("from"),
                            "to": one.get("to"), "when": one.get("when"), "since": one.get("since"),
                            "context": one.get("context"), "description": one.get("description"),
                            "task": one.get("task"), "next_due": recurrence_next(one), "due": recurrence_period(one) is not None,
                            "stopped": one["stopped"], "paused": one.get("paused"),
                            "last": None if last is None else {"period": last.get("period"), "task": last["id"],
                                                               "state": last["state"]}})
    waits = waiting(state)
    return {"team": name, "owner": owner, "principals": list(started.get("principals") or []),
            "root": started.get("root"),
            "started": {"at": started.get("at"), "id": started.get("id")}, **team_state(state),
            "paused": paused_face(state),
            "season": {**season_now(state), "at": started.get("at"),
                       **({"stopped": {key: state["stopped"].get(key) for key in ("at", "by", "id")}}
                          if state["stopped"] else {}),
                       "budget": (started.get("season") or {}).get("budget"),
                       "budget-launches": (started.get("season") or {}).get(          # `budget-wakes`: a season of before
                           "budget-launches", (started.get("season") or {}).get("budget-wakes"))}, "launch": launch,
            "changed": changed_since_start(root, name, started), "limits": dict(state["limits"]),
            "schedule": schedule_face(root, name, started, state),
            "cost": round(state["cost"], 6), "total": round(float(state.get("total") or 0.0), 6),
            "budget_spent": state["budget_spent"], "budget": share_of(state),
            "launches": {"launched": launched_since_start(root, state), "bound": state["limits"].get("budget-launches")},
            "last": state["last"], "tasks": tasks, "members": members, "ceremonies": ceremonies,
            "recurrences": recurrences,
            "owner_inbox": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"), "about": one.get("about"),
                             "task": one.get("task"), "returned": state["returned_to"].get(one["id"]) == owner}
                            for one in (worded(state, one) for one in owner_box(state, owner))],
            "waiting": {"questions": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"),
                                       "task": one.get("task")} for one in waits["questions"]],
                        "notices": [{"id": one["id"], "from": one.get("from"), "about": one.get("about"),
                                     "task": one.get("task"), "awaits": one["awaits"]} for one in waits["notices"]],
                        "infos": [{"id": one["id"], "from": one.get("from"), "task": one.get("task")}
                                  for one in waits["infos"]],
                        "done": [one["task"] for one in waits["done"]], "returned": list(waits["returned"])}}


def schedule_face(root: Path, name: str, started: dict, state: dict) -> dict:
    """-> the net as the face says it: `{seconds, timer, relaunch, reason}` -- `seconds` the step, `timer` whether a
    timer is armed, `relaunch` whether the relaunch entry stands, `reason` why the system refused it this season
    while it stays absent, else null; every one null under `off`."""
    seconds = schedule_seconds(started)
    if seconds is None:
        return {"seconds": None, "timer": None, "relaunch": None, "reason": None}
    standing = relaunch_standing(root)
    refused = None if standing else relaunch_notice(state)
    return {"seconds": seconds, "timer": bool(timer_standing(root, name)), "relaunch": standing,
            "reason": (refused or {}).get("why")}


def answer_of_debt(state: dict, key: int) -> int | None:
    """-> the id of the answer that settled the debt of the message `key`, None while it stands or when the task's close
    settled it."""
    settled = state["debts"].get(key)
    return settled if isinstance(settled, int) and not isinstance(settled, bool) else None


def health_face(state: dict, member: str) -> dict | None:
    """-> the member's HEALTH as the face says it: `{suspected, falls, cause, tried_at, repents}` -- `cause` of the
    last fall, `fall` or `silence` (row 115); `tried_at` the local hour of its try to the second while it is
    suspected --, None for a member that never fell since the season began."""
    health = (state.get("health") or {}).get(member)
    if not health:
        return None
    suspicion = suspicion_of(state, member)
    return {"suspected": suspicion is not None, "falls": int(health.get("falls") or 0), "cause": health.get("cause"),
            "tried_at": suspicion["until"].strftime("%Y-%m-%dT%H:%M:%S") if suspicion else None,
            "repents": int(health.get("repents") or 0)}


def paused_face(state: dict) -> dict | None:
    """-> `{by, at}` of the pause that stands, None when the team is not paused."""
    paused = state.get("paused")
    return None if not paused else {"by": paused.get("by"), "at": paused.get("at")}


def declared_members(root: Path, conductor, name: str, template: str) -> list[dict]:
    """-> `[{member, path, description}]`: the members a team's `TEAM.md` declares, in its order, each with what the
    members' sheet says of it (`description_of`: `no description` when its `MEMBER.md` says none); [] when the
    declaration cannot be read or is refused -- by its judge, or by a template the house lays wrong."""
    try:
        team = team_played(root, conductor, name)
    except (Declined, OSError, SystemExit):
        return []
    return [{"member": member, "path": at, "description": description_of(root, conductor, at, template)}
            for member, at in team["agents"].items()]


def season_now(state: dict) -> dict:
    """-> the season of a started team: its number `n` -- the starts the journal holds -- and its `state`, `running`,
    or `stopped` once a stop ended it."""
    return {"n": int(state.get("seasons") or 1), "state": "stopped" if state.get("stopped") else "running"}


def team_badges(name: str, state: dict) -> dict:
    """-> one line of `team status --json` without a name: the team, its start, its state and what it
    waits on, its tasks by state, the wake-ups under way, what waits for the owner as the inbox counts it
    (`waiting()`: `asks` the agents' questions, `notices` the team's notices, `done` the tasks resolved not seen),
    the last event, its season (`season_now`) -- none for a team never started."""
    if state["started"] is None:
        return {"team": name, "started": None, **team_state(state)}
    by_state = {"open": 0, "stopped": 0, "resolved": 0}
    for task in state["tasks"].values():
        by_state[task["state"]] = by_state.get(task["state"], 0) + 1
    waits = waiting(state)
    return {"team": name, "started": {"at": state["started"].get("at"), "id": state["started"].get("id")},
            **team_state(state), "paused": paused_face(state), "tasks": by_state, "running": len(played(state)),
            "asks": len(waits["questions"]), "notices": len(waits["notices"]), "done": len(waits["done"]),
            "last": state["last"], "season": season_now(state)}


def team_state(state: dict) -> dict:
    """-> `{state, waiting_on}`, the team as its face says it -- derived from the replay, never written:
    `never` before a start, `paused` from a `team pause` to its resume (above every other state),
    `working` while a wake-up plays -- a launch the house sees (`played`) --, `idle` when no task is open, else `waiting`
    with every guard that holds: `reap` first (a launch nobody holds, its end not read: the next tick reaps it), then, in the
    order `woken_on` judges them -- `launches` (an open task launches-spent), `budget` (money or budget-launches
    spent) --, then `owner` (a question to the owner, or a notice that holds a member, on an open task), `suspected` (a
    member of an open task is suspected: its final failure stands), `due` (messages due: the next tick launches)."""
    if state["started"] is None:
        return {"state": "never", "waiting_on": []}
    if state["paused"]:
        return {"state": "paused", "waiting_on": []}
    if played(state):
        return {"state": "working", "waiting_on": []}
    open_tasks = [task for task, one in state["tasks"].items() if one["state"] == "open"]
    if not open_tasks:
        return {"state": "idle", "waiting_on": []}
    members = list(state["started"].get("agents") or {})
    due = {task for member in members for task, box in dues(state, member) if loud(state, box)}
    holds = []
    if any(one.get("task") in open_tasks for one in open_intents(state)):   # none plays: every one of them is gone
        holds.append("reap")
    if any(task in state["launches_spent"] for task in open_tasks):
        holds.append("launches")
    if state["budget_spent"]:
        holds.append("budget")
    waits = waiting(state)
    if any(one.get("task") in open_tasks for one in waits["questions"] + [one for one in waits["notices"] if one["awaits"]]):
        holds.append("owner")
    if any(suspicion_of(state, member) is not None for task in open_tasks for member in members_of(state, task)):
        holds.append("suspected")
    if not state["budget_spent"] and any(task not in state["launches_spent"] for task in due):
        holds.append("due")
    return {"state": "waiting", "waiting_on": holds}


LAUNCH_KEYS = ("harness", "provider", "model", "permissions", "effort")


def launch_face(root: Path, conductor, started: dict, member: str | None = None) -> dict:
    """-> what the next wake-up gets of the launch `team start` kept: each key, `null` when absent -- never
    `max_budget_usd`, a per-wake cap an older journal may keep and the tick never passes --, and `packages`, the
    season's SET as `<name>=on|off`, one per pin (`season_played`): the team's; for a member, what its profile
    replaces, and the set its wake-up plays."""
    kept = started.get("launch") or {}
    profile = profile_of(started, member)
    face = {key: kept.get(key) for key in LAUNCH_KEYS}
    face.update({key: profile[key] for key in PROFILE_KEYS if profile.get(key) is not None})
    face["packages"] = season_played(root, conductor, started, member)
    return face


def profile_of(started: dict, member: str | None) -> dict:
    """-> the member's profile of the season (`team-started.profiles`), {} for none."""
    return dict(((started.get("profiles") or {}).get(member) or {})) if member else {}


def running_on(state: dict, task: str) -> list[dict]:
    """-> the wake-ups under way on the task, in the journal's order: each intent without an end that
    carries it -- its member, tag, run and hour once launched (`null` before), its allowance. A launch nobody
    holds (`faced`: its wake lock free) is not under way: what a post turns a spinner on is a launch PROVEN."""
    found = []
    gone = state.get("gone") or ()
    for tag, one in state["intents"].items():
        if tag in state["ended"] or one.get("task") != task or str(tag) in gone:
            continue
        launched = state["launched"].get(tag) or {}
        found.append({"member": one.get("agent"), "tag": tag, "run": launched.get("run"),
                      "since": launched.get("at"), "allowance": one.get("allowance"), "relance": one.get("relance")})
    return found


def last_launch(state: dict, member: str) -> dict | None:
    """-> the `wake-launched` of the member's last intent, None while that intent stands launched
    by nobody yet."""
    latest = None
    for one in sorted(state["intents"].values(), key=lambda entry: int(entry.get("id") or 0)):
        if one.get("agent") == member:
            latest = state["launched"].get(one.get("tag"))
    return latest


def launched_at(state: dict, member: str) -> str:
    """-> `HH:MM` (UTC) of the member's last launch -- `?` while its intent stands launched by
    nobody yet."""
    launch = last_launch(state, member)
    return str(launch["at"])[11:16] if launch is not None and launch.get("at") else "?"


def run_of(state: dict, member: str) -> tuple[str, str, list[str]] | None:
    """-> (run, state, tasks) of the member, or None before its first wake-up: the run
    its last launch carried (`?` when none was launched); `running` while its last intent has no
    end -- `gone` when nobody holds that launch (`faced`: its end is not read yet, or it died with its process
    space) --, `killed` when a `stop --kill` ended it, `refused` when the house refused its launch, `dead` when it
    failed, `ended` otherwise -- and `kept` when that last intent and its end are of a season BEFORE the one that
    plays: a season starts nobody suspected (`team-started`), and what a launch of the season before said is no
    state of this one; the run is kept, nothing was launched since; the
    tasks its wake-ups carried, on EVERY run it holds -- one per carrier, each said by `run_face` --, in the
    order of their first intent. After a `team reset`
    the intents before it are the forgotten runs': none since, the run is `—` and its state `reset`."""
    since = int(state["reset"].get(member) or 0)
    intents = [one for one in sorted(state["intents"].values(), key=lambda entry: int(entry.get("id") or 0))
               if one.get("agent") == member and int(one.get("id") or 0) > since]
    if not intents:
        return ("—", "reset", []) if member in state["reset"] else None
    runs = {str(one.get("tag")): (state["launched"].get(one.get("tag")) or {}).get("run") for one in intents}
    run = next((key for key in reversed(list(runs.values())) if key), None)
    tasks = list(dict.fromkeys(str(one.get("task")) for one in intents))
    last_tag = str(intents[-1].get("tag"))
    answered = {str(one.get("tag")) for one in state["ends"]}
    season = int((state["started"] or {}).get("id") or 0)
    ended_at = max((int(one.get("id") or 0) for one in [*state["ends"], *state["fails"]]
                    if str(one.get("tag")) == last_tag), default=0)
    if last_tag not in state["ended"]:
        how = "gone" if last_tag in (state.get("gone") or ()) else "running"
    elif max(int(intents[-1].get("id") or 0), ended_at) < season:
        how = "kept"
    elif last_tag in state["killed"]:
        how = "killed"
    elif last_tag in answered:
        how = "ended"
    elif last_tag in state["house"]:
        how = "refused"
    elif ((state.get("quotas") or {}).get(member) or {}).get("tag") == last_tag:
        how = "quota"
    else:
        how = "dead"
    return run or "?", how, tasks


def run_face(state: dict, member: str, key: str) -> dict:
    """-> `{how, since, context}` of ONE run of the member, read from that run's launches alone -- its
    intents, `wake-launched`, ends, failures and kills --, never from the replay's `standing`: `running`
    while a launch of the run has no end, `since` its intent's hour -- `gone` when nobody holds that launch
    (`faced`) --; otherwise the state its last end said,
    `standing` or `parked`, `ended` when that end says neither (killed, a final failure, the house's
    refusal), `since` that end's hour (null for a kill, whose hour the state does not keep); `context` the
    one of the run's last `wake-ended` that carries one, null without."""
    ends = {str(one.get("tag")): one for one in [*state["ends"], *state["fails"]]}

    def run_at(tag: str, intent: dict) -> str | None:
        return ((state["launched"].get(tag) or {}).get("run") or intent.get("run")
                or (ends.get(tag) or {}).get("run"))

    launches = [(str(tag), one) for tag, one in sorted(state["intents"].items(),
                                                       key=lambda entry: int(entry[1].get("id") or 0))
                if one.get("agent") == member and run_at(str(tag), one) == key]
    context = next((one.get("context") for one in reversed(state["ends"])
                    if one.get("context") is not None and str(one.get("tag")) in dict(launches)), None)
    running = [(tag, one) for tag, one in launches if tag not in state["ended"]]
    if running:
        gone = state.get("gone") or ()
        return {"how": "gone" if all(tag in gone for tag, _ in running) else "running",
                "since": running[-1][1].get("at"), "context": context}
    if not launches:
        return {"how": None, "since": None, "context": context}
    tag = launches[-1][0]
    end = ends.get(tag)
    if tag in state["killed"] or end is None:
        return {"how": "ended", "since": None, "context": context}
    said = end.get("state")
    how = said if said in ("standing", "parked") and not end.get("final") and not end.get("house") else "ended"
    return {"how": how, "since": end.get("at"), "context": context}


def status(rest: list[str]) -> int:
    """`team status [<name>] [--json]`: the text the owner reads, or under `--json` the face a
    program reads -- ONE object for the team named, one line per team declared without a name, each with
    `required`: the packages a member may not switch off (`required_by_team`, sorted), read once; without a name each
    line also says `declared_members [{member, path, description}]` as its `TEAM.md` declares them (`[]` when it is refused).
    Read in the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, rest = named_team(conductor, rest)
    as_json = flags(rest, STATUS_FLAGS)["json"]
    if name is not None:
        if not as_json:
            return status_of(root, conductor, name)
        if not team_doc(root, name).is_file():
            refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
        print(json.dumps({**status_object(root, conductor, name, faced(root, conductor, name)),
                          "name": team_name(root, conductor, name),
                          "description": team_description(root, conductor, name),
                          "required": sorted(required_by_team(root, conductor))}, ensure_ascii=False))
        return 0
    home = root.parent / TEAMS
    found = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    if as_json:
        needed = sorted(required_by_team(root, conductor)) if found else []
        template = template_description(root, conductor) if found else ""
        for one in found:
            print(json.dumps({**team_badges(one, faced(root, conductor, one)),
                              "name": team_name(root, conductor, one),
                              "description": team_description(root, conductor, one),
                              "declared_members": declared_members(root, conductor, one, template),
                              "required": needed},
                             ensure_ascii=False))
        return 0
    if not found:
        print(f"pp-team: no team declared under {home} yet.")
        return 0
    for name in found:
        state = state_of(journal_of(root, name))
        if state["started"] is None:
            print(f"{labelled(root, conductor, name)} · declared, not started")
            continue
        by_state: dict[str, int] = {}
        for task in state["tasks"].values():
            by_state[task["state"]] = by_state.get(task["state"], 0) + 1
        tally = ", ".join(f"{count} {kind}" for kind, count in by_state.items()) or "none"
        last = state["last"] or {}
        print(f"{labelled(root, conductor, name)} · {len(state['tasks'])} task(s): {tally} · last event "
              f"#{last.get('id')} {last.get('kind')} "
              f"at {last.get('at')}")
    return 0


# --- the readers: watch, log, result, inbox ------------------------------------------------

def harmless(text: str) -> str:
    """-> a text an agent or a principal wrote, as stdout may print it: each line opening on
    `::`, blanks before it included, prefixed with a backslash -- the console reads such a line
    as a directive of the house's bus, and nobody's words give pp an order."""
    return "\n".join("\\" + one if one.lstrip().startswith("::") else one for one in text.split("\n"))


def shown(one: dict) -> str:
    """-> one event as ONE line: `#<id> <kind> <what it says>` -- the form `log` prints and
    `watch` writes on stderr; a text of several lines is said on one."""
    kind = one.get("kind")
    text = " ".join(str(one.get("text") or "").split())
    short = text if len(text) <= 60 else text[:57] + "…"
    if kind == "post":
        return (f"#{one.get('id')} post {one.get('verb')}" + (f" #{one['re']}" if one.get("re") is not None else "")
                + f" {one.get('from')} -> {one.get('to')} on {one.get('task')}"
                + (f" · about {one['about']}" if one.get("about") else "")
                + (" · info" if one.get("info") else "") + (" · by the tick" if one.get("by") == "tick" else "")
                + (RETURNED_MARK if one.get("returned") else "")
                + (f": {short}" if short else ""))
    if kind == "task":
        return (f"#{one.get('id')} task {one.get('task')}" + (f" {one['name']}" if one.get("name") else "")
                + f" from {one.get('from')} to {one.get('to')}: {short}")
    if kind == "team-started":
        return f"#{one.get('id')} team-started · members {', '.join(one.get('agents') or {})} · root {one.get('root')}"
    if kind == "wake-intent":
        return f"#{one.get('id')} wake-intent {one.get('agent')} on {one.get('task')} · tag {one.get('tag')}"
    if kind == "wake-launched":
        return (f"#{one.get('id')} wake-launched {one.get('agent')} · run {one.get('run')} · pid {one.get('pid')}"
                + (f" · name refused: {one['name-refused']}" if one.get("name-refused") else ""))
    if kind == "wake-ended":
        return (f"#{one.get('id')} wake-ended {one.get('agent')} · run {one.get('run')}"
                + (f" · launch {one.get('launch')}" if one.get("launch") is not None else "")
                + (f" · {one.get('state')}" if one.get("state") else "") + f" · cost {one.get('cost')}")
    if kind == "wake-routed":
        return (f"#{one.get('id')} wake-routed {one.get('agent')} · run {one.get('run')} · words {one.get('words')}"
                + (" · nowhere" if one.get("nowhere") else ""))
    if kind == "wake-refused":
        return f"#{one.get('id')} wake-refused {one.get('agent')} · run {one.get('run')} · {one.get('why')}"
    if kind == "wake-failed":
        return (f"#{one.get('id')} wake-failed {one.get('agent')} on {one.get('task')} · {one.get('reason')}"
                + (f" · spent {one.get('spent')} of its share {one.get('share')} USD" if "share" in one else "")
                + (" · the house" if one.get("house") else "") + (" · final" if one.get("final") else ""))
    if kind == "wake-halted":
        return (f"#{one.get('id')} wake-halted {one.get('agent')} on {one.get('task')} · {one.get('count')} failures in "
                f"a row · {one.get('reason')}")
    if kind == "quota-reached":
        return (f"#{one.get('id')} quota-reached {one.get('agent')} on {one.get('task')} · until "
                f"{one.get('until') or 'team resume'}" + (f" · {one['said']}" if one.get("said") else ""))
    if kind == "quota-lifted":
        return f"#{one.get('id')} quota-lifted {', '.join(one.get('members') or [])} · by {one.get('by')}"
    if kind == "timer-armed":
        return f"#{one.get('id')} timer-armed · due {str(one.get('due'))[11:19]}"
    if kind == "wake-killed":
        return f"#{one.get('id')} wake-killed {one.get('agent')} on {one.get('task')} · run {one.get('run')} · pid {one.get('pid')}"
    if kind == "deferred":
        return f"#{one.get('id')} {kind} {one.get('agent')} on {one.get('task')}"
    if kind == "done":
        return f"#{one.get('id')} done {one.get('task')} · {json.dumps(one.get('result'), ensure_ascii=False)}"
    if kind == "returned":
        return f"#{one.get('id')} returned #{one.get('message')} to {one.get('to')}"
    if kind == "stopped":
        return f"#{one.get('id')} stopped {one.get('task')} by {one.get('by')}"
    if kind == "ceremony-due":
        return (f"#{one.get('id')} ceremony-due {one.get('ceremony')} · {one.get('period')}"
                + (f" by {one.get('by')}" if one.get("by") else ""))
    if kind == "resumed":
        return f"#{one.get('id')} resumed {one.get('task')} by {one.get('by')} · from {', '.join(one.get('from') or [])}"
    if kind == "recurrence":
        when = one.get("when") or {}
        return (f"#{one.get('id')} recurrence {one.get('recurrence')}" + (f" {one['name']}" if one.get("name") else "")
                + f" from {one.get('from')} to {one.get('to')} · every {said_when(when)}"
                + (f" · from {one['task']}" if one.get("task") else "")
                + (f" · context {one['context']}%" if one.get("context") is not None else "") + f": {short}")
    if kind == "recurrence-skipped":
        return f"#{one.get('id')} recurrence-skipped {one.get('recurrence')} · {one.get('period')} · {one.get('open')} open"
    if kind == "recurrence-stopped":
        return f"#{one.get('id')} recurrence-stopped {one.get('recurrence')} by {one.get('by')}"
    if kind in ("recurrence-paused", "recurrence-resumed"):
        return f"#{one.get('id')} {kind} {one.get('recurrence')} by {one.get('by')}"
    if kind == "recurrence-changed":
        when = one.get("when") or {}
        return (f"#{one.get('id')} recurrence-changed {one.get('recurrence')} by {one.get('by')}"
                + (f" · every {said_when(when)}" if "when" in one else "")
                + (f" · context {one['context']}%" if one.get("context") is not None
                   else " · context off" if "context" in one else "")
                + (" · description changed" if "description" in one else "")
                + (f": {short}" if "text" in one else ""))
    if kind == "run-renewed":                            # a null model or provider is said `none`; a pair unchanged, silent
        said = lambda value: "none" if value is None else value
        return (f"#{one.get('id')} run-renewed {one.get('member')} · run {one.get('run')}"
                + (f" of {one.get('recurrence')}" if one.get("recurrence") else "") + f" on {one.get('task')} · "
                + (", ".join(f"{key} {said((one.get('was') or {}).get(key))} -> {said((one.get('now') or {}).get(key))}"
                             for key in ("model", "provider")
                             if (one.get("was") or {}).get(key) != (one.get("now") or {}).get(key))
                   if one.get("why") == "model"
                   else f"used {round(float(one.get('used') or 0) * 100)}% of {one.get('limit')}%"))
    if kind == "budget-spent":
        return (f"#{one.get('id')} budget-spent {one.get('spent')} of {one.get('budget')} "
                + ("launches" if one.get("unit") in ("launches", "wakes") else "USD"))
    if kind == "silence":
        return (f"#{one.get('id')} silence {one.get('agent')} on {one.get('task')} · "
                f"{one.get('passages', one.get('exchanges'))} exchange(s)")   # `exchanges`: a journal of before
    if kind == "inbox-seen":
        return f"#{one.get('id')} inbox-seen up to #{one.get('upto')}"
    if kind == "inbox-read":
        return f"#{one.get('id')} inbox-read #{one.get('message')}"
    return f"#{one.get('id')} {kind}"


def of_task(events: list[dict], task: str) -> list[dict]:
    """-> the events of one task: those that name it, and the launches and ends of the
    intents it opened (found by their tag)."""
    tags = {one.get("tag") for one in events if one.get("kind") == "wake-intent" and one.get("task") == task}
    return [one for one in events if one.get("task") == task or (one.get("tag") in tags and one.get("kind") != "wake-intent")]


def event_object(name: str, one: dict) -> dict:
    """-> one journal event as the faces give it: `{at, team, event, ...}` -- its kind as `event`,
    the rest of its fields, its `id` among them. `watch --json` and `log --json` both write it."""
    return {"at": one.get("at"), "team": name, "event": one.get("kind"),
            **{key: value for key, value in one.items() if key not in ("at", "kind", "team")}}


def said_event(name: str, one: dict, as_json: bool) -> None:
    """One journal event on stderr, as `watch` says it: the line, or the JSON object;
    a `snapshot` is a reader's aid, not a team event, and is never said."""
    if one.get("kind") == "snapshot":
        return
    if as_json:
        text = json.dumps(event_object(name, one), ensure_ascii=False)
    else:
        text = f"[{datetime.now().strftime('%H:%M:%S')}] {name} · {shown(one)}"
    sys.stderr.write(text + "\n")
    sys.stderr.flush()


def seconds_of(asked: dict, flag: str, floor: float) -> float | None:
    """-> the seconds a flag names, at least `floor`; None without the flag."""
    if asked[flag] is None:
        return None
    try:
        value = float(asked[flag])
    except ValueError:
        value = -1.0
    if value < floor:
        refuse(f"{flag}-invalid -- `--{flag} {asked[flag]}`: a number of seconds, at least {floor:g}.")
    return value


def quiescent(state: dict) -> bool:
    """-> whether nothing can move: no intent without an end, and no task open -- or nothing a
    tick could still launch on them: no agent has a message due, or the budget is spent, or
    the due tasks' wake-ups are."""
    if open_intents(state):
        return False
    if not any(one["state"] == "open" for one in state["tasks"].values()) or state["budget_spent"]:
        return True
    for agent in (state["started"] or {}).get("agents") or {}:
        if any(task not in state["launches_spent"] and loud(state, box) for task, box in dues(state, agent)):
            return False
    return True


def activity_of(kind: str, one: dict) -> dict:
    """-> what an `activity` object of `watch` says of one event of a flow: a `tool` its `name`, its `title` and
    `pp`; a `tool-result` its `error` and the `size` of its content -- never the content --; a `thinking` its
    `tokens` or its `text`; `words` its `text`; a `context` its `tokens`, `used` and `window`; every text cut at
    `ACTIVITY_TEXT`."""
    def cut(text: object) -> str:
        return " ".join(str(text or "").split())[:ACTIVITY_TEXT]
    if kind == "tool":
        return {"kind": kind, "name": str(one.get("name") or ""), "title": cut(one.get("title")), "pp": one.get("pp") is True}
    if kind == "tool-result":
        return {"kind": kind, "error": one.get("error") is True, "size": len(str(one.get("content") or ""))}
    if kind == "thinking":
        tokens = one.get("tokens")
        return {"kind": kind, "tokens": tokens} if isinstance(tokens, int) else {"kind": kind, "text": cut(one.get("text"))}
    if kind == "words":
        return {"kind": kind, "text": cut(one.get("text"))}
    return {"kind": kind, "tokens": one.get("tokens"), "used": one.get("used"), "window": one.get("window")}


def activity_line(fields: dict) -> str:
    """-> an activity as the text watch says it: `tool Read · pp.py`, `result ✓ 10.0 kB`, `thinking <text>`,
    `words <text>`, `context 34000 tokens`."""
    kind = fields.get("kind")
    if kind == "tool":
        return f"tool {fields.get('name')}" + (f" · {fields['title']}" if fields.get("title") else "")
    if kind == "tool-result":
        size = int(fields.get("size") or 0)
        said = f"{size} B" if size < 1024 else f"{size / 1024:.1f} kB"
        return f"result {'✗' if fields.get('error') else '✓'} {said}"
    if kind == "context":
        return f"context {fields.get('tokens')} tokens"
    return f"{kind} {fields.get('text') if fields.get('text') is not None else fields.get('tokens', '')}".rstrip()


class ActivityReader:
    """The FLOW of one launch the watch follows, read by `agent flow <path> <run> --json --from <rank> --follow`
    in a thread of its own -- the same call as the follower --: from the `opened` of the launch's exchange, found
    by its tag, the events that say what the harness does (`ACTIVITY_KINDS`) come out of `fresh()` as the fields
    of an `activity` object, at most `ACTIVITY_RATE` per second: past that, the latest is HELD and the ones it
    replaces are counted, said with `more` once the second turned or at `close()`; a `context` always passes.
    `done` once the stream ended on its own."""

    def __init__(self, engine: Path, root: Path, path: str, run: str, tag: str, start: int) -> None:
        self.tag, self.opened, self.done = tag, False, False
        self.window: float | None = None             # the instant the current second opened
        self.count = 0                               # the objects said in it
        self.held: dict | None = None                # the latest object past the rate, said when the second turns
        self.dropped = 0                             # the objects it replaced
        self._queue: queue.Queue = queue.Queue()
        self._process = subprocess.Popen([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                                          "--json", "--from", str(max(1, start)), "--follow"],
                                         stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                                         cwd=str(root.parent), env=dict(os.environ))
        self._thread = threading.Thread(target=self._read, daemon=True)
        self._thread.start()

    def _read(self) -> None:
        assert self._process.stdout is not None
        for line in self._process.stdout:
            if line.strip():
                try:
                    self._queue.put(json.loads(line))
                except ValueError:
                    continue
        self._queue.put(None)

    def fresh(self, now: float) -> list[dict]:
        """-> the activity objects to say now: those read since the last call, under the rate, and the held one
        once the second turned."""
        said: list[dict] = []
        while True:
            try:
                one = self._queue.get_nowait()
            except queue.Empty:
                break
            if one is None:
                self.done = True
                break
            kind = one.get("kind")
            if kind == "opened":                     # the launch's own exchange opens here; another closes it
                self.opened = opened_by(one, self.tag)
            elif self.opened and kind in ACTIVITY_KINDS:
                fields = activity_of(str(kind), one)
                said += [fields] if kind == "context" else self._bounded(fields, now)
        return said + self._turned(now)

    def _bounded(self, fields: dict, now: float) -> list[dict]:
        out = self._turned(now)
        if self.window is None or now - self.window >= 1.0:
            self.window, self.count = now, 0
        if self.count < ACTIVITY_RATE - 1:           # the last slot of the second is the held one's
            self.count += 1
            return out + [fields]
        if self.held is not None:
            self.dropped += 1
        self.held = fields
        return out

    def _turned(self, now: float) -> list[dict]:
        """-> the held object once the second turned: it opens the next one."""
        if self.held is None or (self.window is not None and now - self.window < 1.0):
            return []
        self.window, self.count = now, 1
        return [self._flushed()]

    def _flushed(self) -> dict:
        said = {**self.held, **({"more": self.dropped} if self.dropped else {})}
        self.held, self.dropped = None, 0
        return said

    def close(self) -> list[dict]:
        """The stream ended: the process ended when still alive, the held object said. -> what is left to say."""
        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._process.kill()
        return [self._flushed()] if self.held is not None else []


def watched(root: Path, conductor, name: str, asked: dict) -> int:
    """`team watch`: the journal and the traces of the wake-ups under way FOLLOWED -- read,
    never written, no lock taken -- until the bound asked, or Ctrl-C. Under `--json` each step of a
    wake-up says the `task`, the `tag` and the `launch` (its rank in the run) of the intent it follows.
    Beside the trace, the FLOW of each wake-up followed is read by its own `agent flow --follow`
    (`ActivityReader`, closed with the wake-up): what the harness does between two blocks is said as
    `activity` objects -- `{at, agent, run, event: activity, kind, task, tag, launch, …}` --, one line
    of text each without `--json`."""
    log = tracing(conductor)
    engine = engine_of(root, conductor)
    journal = journal_of(root, name)
    task = asked["task"]
    as_json = asked["json"]
    beat = int(seconds_of(asked, "heartbeat", 1) or DEFAULT_HEARTBEAT)
    bound = seconds_of(asked, "for", 0)
    state = state_of(journal)
    tail = log.tail(journal, from_end=True)
    context = said_so_far()                                # what the journal said: the next events said in its words
    for one in lines_of(journal):
        if one.get("kind") != "snapshot":
            read_on(context, one)
    follows: dict[str, tuple[str, str, object]] = {}      # tag -> (member, run, the run's reader)
    activities: dict[str, ActivityReader] = {}            # tag -> the reader of the launch's flow
    closing: dict[str, float] = {}                        # tag -> when its wake-up ended: its reader drains, then closes
    intents: dict[str, dict] = {str(tag): one for tag, one in state["intents"].items()}   # tag -> its wake-intent
    launches: dict[str, dict] = {str(tag): one for tag, one in state["launched"].items()}   # tag -> its wake-launched
    members = dict((state["started"] or {}).get("agents") or {})          # name -> the agent's path
    paths = {tag: path_of_intent(state, one) for tag, one in state["intents"].items()}   # tag -> path
    tags_of_task: set[str] = {tag for tag, one in state["intents"].items() if one.get("task") == task}
    for one in open_intents(state):                        # the wake-ups already under way: read on
        launch = state["launched"].get(one["tag"])
        if launch and launch.get("run") and (task is None or one["tag"] in tags_of_task):
            follows[one["tag"]] = (one["agent"], launch["run"],
                                   log.follow(agent_meta(root, paths[one["tag"]]), launch["run"], from_end=True))
            activities[one["tag"]] = ActivityReader(engine, root, paths[one["tag"]], str(launch["run"]), one["tag"],
                                                    int(state["flow"].get(str(launch["run"])) or 0) + 1)
    resumed: set[str] = {tag for tag, one in state["intents"].items() if one.get("run")}
    opened, still, beats = time.monotonic(), time.monotonic(), 0
    try:
        while True:
            moved = False
            arrived = tail.fresh()                         # the journal's new events: the state is read again on them alone
            for one in arrived:
                kind, tag = one.get("kind"), one.get("tag")
                said = read_on(context, one) if kind != "snapshot" else one
                if kind == "team-started":
                    members = dict(one.get("agents") or {})
                if kind == "wake-intent":
                    paths[str(tag)] = str(one.get("path") or members.get(one.get("agent"), one.get("agent")))
                    intents[str(tag)] = one
                if kind == "wake-intent" and one.get("task") == task:
                    tags_of_task.add(str(tag))
                if kind == "wake-intent" and one.get("run"):       # a run resumed: its trace read from its end
                    resumed.add(str(tag))
                if kind == "wake-launched":
                    launches[str(tag)] = one
                if task is not None and one.get("task") != task and tag not in tags_of_task:
                    continue
                if said is not None:
                    said_event(name, said, as_json)
                    moved = True
                if kind == "wake-launched" and one.get("run") and tag not in follows:
                    at = paths.get(str(tag)) or str(members.get(one.get("agent"), one.get("agent")))
                    follows[str(tag)] = (str(one.get("agent")), str(one["run"]),
                                         log.follow(agent_meta(root, at), str(one["run"]),
                                                    from_end=str(tag) in resumed))
                    activities[str(tag)] = ActivityReader(engine, root, at, str(one["run"]), str(tag),
                                                          int(state["flow"].get(str(one["run"])) or 0) + 1)
            for tag in list(follows):
                agent, run, reader = follows[tag]
                intent = intents.get(tag) or {}
                for line, kind, fields in filter(None, map(log.step_of, reader.fresh())):
                    if as_json:                             # the step said with the intent it follows
                        fields = {**fields, "task": intent.get("task"), "tag": tag,
                                  "launch": (launches.get(tag) or {}).get("launch")}
                    log.said(run, line, kind, fields, as_json, who=agent)
                    moved = True
            now_at = time.monotonic()
            for tag in list(activities):                    # the activity of each launch followed, under the rate
                reader = activities[tag]
                agent, run = (follows.get(tag) or (intents.get(tag, {}).get("agent"), (launches.get(tag) or {}).get("run")))[:2]
                over = tag in closing and (reader.done or now_at - closing[tag] >= ACTIVITY_DRAIN)
                for fields in reader.fresh(now_at) + (reader.close() if over else []):
                    log.said(str(run), activity_line(fields), "activity",
                             {**fields, "task": (intents.get(tag) or {}).get("task"), "tag": tag,
                              "launch": (launches.get(tag) or {}).get("launch")}, as_json, who=str(agent))
                    moved = True
                if over:
                    del activities[tag], closing[tag]
            if arrived:                                     # a journal at rest is not read again: its state stands
                state = state_of(journal)
            for tag in list(follows):                       # a wake-up over leaves the watch; its flow drains, then closes
                if tag in state["ended"]:
                    del follows[tag]
                    if tag in activities:
                        closing[tag] = time.monotonic()
            if moved:
                still, beats = time.monotonic(), 0
            elif time.monotonic() - still >= beat * (beats + 1):
                beats += 1
                if as_json:
                    said_event(name, {"at": now(), "kind": "quiet", "seconds": beat * beats}, True)
                else:
                    sys.stderr.write(f"[{datetime.now().strftime('%H:%M:%S')}] {name} · no event for {beat * beats}s\n")
                    sys.stderr.flush()
            if asked["until-done"] and state["started"] is not None and quiescent(state):
                break
            if bound is not None and time.monotonic() - opened >= bound:
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        pass
    finally:
        for reader in activities.values():
            reader.close()
    return 0


def watch(rest: list[str]) -> int:
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, WATCH_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    return watched(root, conductor, name, asked)


def log_verb(rest: list[str]) -> int:
    """`team log`: the journal rendered, one line per event, by task and by tail, in the words of the debt (`read_on`);
    under `--json` one object per event, the form `watch --json` writes."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, LOG_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    context, events = said_so_far(), []
    for one in lines_of(journal_of(root, name)):
        said = read_on(context, one) if one.get("kind") != "snapshot" else None
        if said is not None:
            events.append(said)
    if asked["task"] is not None:
        events = of_task(events, asked["task"])
    if asked["last"] is not None:
        try:
            last = int(asked["last"])
        except ValueError:
            last = -1
        if last < 1:
            refuse(f"last-invalid -- `--last {asked['last']}`: a whole number of 1 or more.")
        events = events[-last:]
    for one in events:
        print(json.dumps(event_object(name, one), ensure_ascii=False) if asked["json"] else harmless(shown(one)))
    return 0


def result(rest: list[str]) -> int:
    """`team result`: a resolved task's result as JSON on stdout."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    if len(rest) > 1 or (rest and rest[0].startswith("--")):
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    if rest:
        task = state["tasks"].get(rest[0])
        if task is None:
            refuse(f"task-unknown -- no task `{rest[0]}` of {name}: the tasks are {', '.join(state['tasks']) or 'none'}.")
        if task["state"] != "resolved":
            refuse(f"task-open -- {task['id']} is {task['state']}: no result yet.")
        chosen = state["done"][task["id"]]
    else:
        resolved = list(state["done"].values())
        if not resolved:
            refuse(f"result-missing -- no task of {name} is resolved yet.")
        chosen = resolved[-1]
    print(json.dumps(chosen.get("result"), ensure_ascii=False))
    return 0


def responses_verb(rest: list[str]) -> int:
    """`team responses`: what the team's members said, one per `wake-ended`, the words of its launch read
    at the run's flow by the house's console; `--since`, `--agent`, `--task` filter, `--last` cuts; under
    `--json` one object per end, its text whole or `null`. Nothing written."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESPONSES_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    if state["started"] is None:
        refuse(f"team-not-started -- {name} was never started.")
    numbers: dict[str, int] = {}
    for flag in ("since", "last"):
        if asked[flag] is not None:
            try:
                numbers[flag] = int(asked[flag])
            except ValueError:
                numbers[flag] = -1
            if numbers[flag] < 0:
                refuse(f"{flag}-invalid -- `--{flag} {asked[flag]}`: a whole number of 0 or more.")
    chosen = []
    for one in state["ends"]:
        task = (state["intents"].get(one.get("tag")) or {}).get("task")
        if "since" in numbers and one["id"] <= numbers["since"]:
            continue
        if asked["agent"] is not None and one.get("agent") != asked["agent"]:
            continue
        if asked["task"] is not None and task != asked["task"]:
            continue
        chosen.append((one, task))
    if "last" in numbers:
        chosen = chosen[-numbers["last"]:] if numbers["last"] else []
    for one, task in chosen:
        intent = state["intents"].get(one.get("tag"))
        at = path_of_intent(state, intent) if intent else path_of(state, str(one.get("agent")))
        text = words_of(root, conductor, at, str(one.get("run") or ""), one.get("launch"))
        if asked["json"]:
            print(json.dumps({"id": one["id"], "member": one.get("agent"), "path": at, "task": task,
                              "run": one.get("run"), "launch": one.get("launch"), "at": one.get("at"),
                              "cost_usd": one.get("cost"), "response": text}, ensure_ascii=False))
            continue
        print(f"#{one['id']} {one.get('agent')} on {task} · run {one.get('run')}")
        print(harmless(text) if text is not None else "(response missing at the record)")
        print()
    return 0


# --- the stats of a season ---------------------------------------------------------------------------------

STATS_FLAGS = {"season": True, "all": False, "cost": True, "json": False}
COST_BASES = ("usd", "launches", "tokens")         # the units a cost is said in: `--cost`, `usd` by default
SLOT = 7200                                        # the width of one slot of `effort_by_slot`, in seconds
ENDS = ("wake-ended", "wake-failed", "quota-reached", "wake-killed")   # what ends a wake-up


def moment(at) -> datetime | None:
    """-> an event's `at` as an aware datetime (a naive one read as UTC); None when it reads as none."""
    try:
        found = datetime.fromisoformat(str(at))
    except (TypeError, ValueError):
        return None
    return found if found.tzinfo is not None else found.replace(tzinfo=timezone.utc)


def ranked(values: list, share: float):
    """-> the value at `share` of the values by the NEAREST RANK -- the ceil(share x n)-th of them sorted, the
    first for share 0 --, None without a value: the one rule of every median (0.5) and p90 (0.9) of the stats."""
    found = sorted(one for one in values if one is not None)
    if not found:
        return None
    return found[max(0, math.ceil(share * len(found)) - 1)]


def spans_union(spans: list[tuple[datetime, datetime]]) -> float:
    """-> the seconds of wall time at least one of the spans covers."""
    total, reach = 0.0, None
    for start, end in sorted(spans):
        if reach is None or start > reach:
            total += (end - start).total_seconds()
            reach = end
        elif end > reach:
            total += (end - reach).total_seconds()
            reach = end
    return total


def costs_of(wakes: list[dict]) -> dict:
    """-> what the wake-ups cost in each base: `usd` the sum of the costs reported (None when none reports one,
    never 0), `launches` the wake-ups launched, `tokens` the tokens sent -- a wake-up without `tokens` counts its
    end's `context.tokens`, the floor of one call, and makes the sum `tokens_estimated` --, None when no wake-up
    measured any."""
    usd = [one["usd"] for one in wakes if one["usd"] is not None]
    tokens = [one["tokens"] for one in wakes if one["tokens"] is not None]
    return {"usd": round(sum(usd), 6) if usd else None,
            "launches": sum(1 for one in wakes if one["launched"] is not None),
            "tokens": sum(tokens) if tokens else None,
            "tokens_estimated": any(one["estimated"] for one in wakes)}


def per(value, count):
    """-> value / count, None when either is none or the count is 0."""
    if value is None or not count:
        return None
    return round(value / count, 4)


def spread(values: list) -> dict:
    """-> the minimum, the median, the maximum of the values that are numbers, and the `series` whole."""
    found = [one for one in values if one is not None]
    return {"min": min(found) if found else None, "median": ranked(found, 0.5), "max": max(found) if found else None,
            "series": values}


def times_of(wakes: list[dict], clock: datetime) -> dict:
    """-> the active time of the wake-ups (the union of their spans `wake-launched` -> end, a wake-up in flight up
    to `clock`) and their effort (the sum of those spans), in seconds."""
    spans = [(one["launched"], one["ended"] or clock) for one in wakes if one["launched"] is not None]
    spans = [(start, max(start, end)) for start, end in spans]
    return {"active": round(spans_union(spans)),
            "effort": round(sum((end - start).total_seconds() for start, end in spans))}


def wakes_read(events: list[dict], seasons: list[int]) -> dict[str, dict]:
    """-> every wake-up of the journal by its tag: its member, its task, its season (that of its intent), the hours
    of its intent, launch and end, the kind of its end and its reason, what it cost in each base, the share of
    the context its end left (`used`)."""
    wakes: dict[str, dict] = {}
    for rank, one in enumerate(events):
        kind, tag = one.get("kind"), one.get("tag")
        if kind == "wake-intent":
            wakes[tag] = {"tag": tag, "agent": one.get("agent"), "task": one.get("task"), "season": seasons[rank],
                          "intent": moment(one.get("at")), "launched": None, "ended": None, "end": None,
                          "reason": None, "usd": None, "tokens": None, "estimated": False, "used": None}
            continue
        wake = wakes.get(tag)
        if wake is None:
            continue
        if kind == "wake-launched" and wake["launched"] is None:
            wake["launched"] = moment(one.get("at"))
        elif kind in ENDS and wake["end"] is None:
            wake.update(ended=moment(one.get("at")), end=kind, reason=one.get("reason"))
            cost = one.get("cost")
            if isinstance(cost, (int, float)) and not isinstance(cost, bool):
                wake["usd"] = float(cost)
            context = one.get("context") if isinstance(one.get("context"), dict) else {}
            sent, floor = one.get("tokens"), context.get("tokens")
            if isinstance(sent, int) and not isinstance(sent, bool):
                wake["tokens"] = sent
            elif isinstance(floor, int) and not isinstance(floor, bool):
                wake["tokens"], wake["estimated"] = floor, True
            if kind == "wake-ended" and isinstance(context.get("used"), (int, float)):
                wake["used"] = float(context["used"])
    return wakes


def tasks_read(own: list[dict], wakes: dict[str, dict], births: dict[str, dict]) -> dict[str, dict]:
    """-> the tasks of ONE season by their id, in the order they come in it: a task born in it (its `task` event),
    woken in it (a `wake-intent` on it) or closed or stopped in it (its `done`, its `stopped`). Each says its name, the
    season it was born in, its state at the season's end -- `resolved` at its `done`, `stopped` at its `stopped`,
    `open` again at its `resumed`, `open` when the season says none --, the hours of its first and last event in the
    season, its `do` and its `re` there (the tick's apart), and its wake-ups of the season by their tags."""
    def task_of_event(one: dict):
        return one.get("task") if one.get("task") else (wakes.get(one.get("tag")) or {}).get("task")
    tasks: dict[str, dict] = {}
    for one in own:
        task = task_of_event(one)
        if task and task not in tasks and (one.get("kind") in ("task", "done", "stopped")
                                           or (one.get("kind") == "wake-intent" and wakes.get(one.get("tag")))):
            born = births.get(task) or {}
            tasks[task] = {"task": task, "name": born.get("name"), "season": born.get("season"), "state": "open",
                           "first": None, "last": None, "do": 0, "re": 0, "tags": []}
    for one in own:
        held = tasks.get(task_of_event(one))
        if held is None:
            continue
        kind, at = one.get("kind"), moment(one.get("at"))
        if at is not None:
            held["first"] = at if held["first"] is None else min(held["first"], at)
            held["last"] = at if held["last"] is None else max(held["last"], at)
        if kind == "wake-intent" and one.get("tag") in wakes:
            held["tags"].append(one["tag"])
        elif kind == "done":
            held["state"] = "resolved"
        elif kind == "stopped" and held["state"] == "open":
            held["state"] = "stopped"
        elif kind == "resumed" and held["state"] == "stopped":
            held["state"] = "open"
        elif kind == "post" and one.get("verb") == "do":
            held["do"] += 1
        elif kind == "post" and one.get("verb") == "re" and one.get("by") != "tick":
            held["re"] += 1
    return tasks


def task_face(task: dict, wakes: list[dict], clock: datetime) -> dict:
    """-> one task's line of a season's stats, read on the season alone: what its wake-ups of the season cost in
    each base, its `do` and `re` there, its failed wake-ups, its three times (elapsed from its first to its last
    event of the season), the hours of those two events (`first`, `last`), the largest share of the context its
    wake-ups left."""
    elapsed = (task["last"] - task["first"]).total_seconds() if task["first"] and task["last"] else 0
    hour = lambda at: None if at is None else at.isoformat()
    return {"task": task["task"], "name": task["name"], "season": task["season"], "state": task["state"],
            "cost": costs_of(wakes), "do": task["do"], "re": task["re"],
            "failures": sum(1 for one in wakes if one["end"] == "wake-failed"),
            "time": {"elapsed": round(elapsed), **times_of(wakes, clock)},
            "first": hour(task["first"]), "last": hour(task["last"]),
            "context_max": max((one["used"] for one in wakes if one["used"] is not None), default=None)}


def tasks_total(seasons: list[dict]) -> list[dict]:
    """-> each task's line over all the seasons, in the order it first comes, without `season`: its season lines
    summed -- its costs base by base (None where no season measured one; `tokens_estimated` where one says it), its
    `do`, its `re`, its failures, its active time and its effort --, its `first` event the earliest of theirs and its
    `last` the latest, its elapsed time the wall between them, the largest share of the context they say, its name and
    its state as its last line says them."""
    plus = lambda one, other: None if one is None and other is None else round((one or 0) + (other or 0), 6)
    found: dict[str, dict] = {}
    for season in seasons:
        for line in season["by_task"]:
            held = found.get(line["task"])
            if held is None:
                found[line["task"]] = {**{key: value for key, value in line.items() if key != "season"},
                                       "cost": dict(line["cost"]), "time": dict(line["time"])}
                continue
            held.update(name=line["name"], state=line["state"], do=held["do"] + line["do"], re=held["re"] + line["re"],
                        failures=held["failures"] + line["failures"],
                        context_max=max((one for one in (held["context_max"], line["context_max"]) if one is not None),
                                        default=None))
            cost = held["cost"]
            cost.update(usd=plus(cost["usd"], line["cost"]["usd"]), launches=cost["launches"] + line["cost"]["launches"],
                        tokens=plus(cost["tokens"], line["cost"]["tokens"]),
                        tokens_estimated=cost["tokens_estimated"] or line["cost"]["tokens_estimated"])
            for key in ("active", "effort"):
                held["time"][key] += line["time"][key]
            if moment(line["first"]) is not None and (moment(held["first"]) is None
                                                      or moment(line["first"]) < moment(held["first"])):
                held["first"] = line["first"]
            if moment(line["last"]) is not None and (moment(held["last"]) is None
                                                     or moment(line["last"]) > moment(held["last"])):
                held["last"] = line["last"]
            if moment(held["first"]) is not None and moment(held["last"]) is not None:
                held["time"]["elapsed"] = round((moment(held["last"]) - moment(held["first"])).total_seconds())
    return list(found.values())


def member_face(member: str, roles: list[str], wakes: list[dict], posts: list[dict], answered: dict,
                clock: datetime) -> dict:
    """-> one member's line of a season's stats: its role keys, what it cost in each base and per launch, the `do`
    it received and the `re` it gave (the tick's apart), its failed wake-ups, its three times (elapsed from its first
    launch to its last end), the largest share of the context its wake-ups left, the median delay from a `do` it
    received to its first `re` citing it."""
    cost = costs_of(wakes)
    spans = [one for one in wakes if one["launched"] is not None]
    elapsed = ((max(one["ended"] or clock for one in spans) - min(one["launched"] for one in spans)).total_seconds()
               if spans else 0)
    dos = [one for one in posts if one.get("verb") == "do" and one.get("to") == member]
    delays = [(answered[one["id"]] - moment(one.get("at"))).total_seconds() for one in dos
              if one["id"] in answered and moment(one.get("at")) is not None]
    return {"member": member, "roles": roles, "cost": cost,
            "per_launch": {"usd": per(cost["usd"], cost["launches"]), "tokens": per(cost["tokens"], cost["launches"])},
            "do": len(dos),
            "re": sum(1 for one in posts
                      if one.get("verb") == "re" and one.get("from") == member and one.get("by") != "tick"),
            "failures": sum(1 for one in wakes if one["end"] == "wake-failed"),
            "time": {"elapsed": round(max(0.0, elapsed)), **times_of(wakes, clock)},
            "context_max": max((one["used"] for one in wakes if one["used"] is not None), default=None),
            "do_re_median": None if not delays else round(ranked(delays, 0.5))}


def season_stats(events: list[dict], clock: datetime) -> list[dict]:
    """-> the stats of every SEASON of a journal, oldest first -- a season runs from one `team-started` to the next,
    numbered by its rank from 1; computed from the journal's events alone, `clock` the hour a season or a wake-up
    still under way counts up to. A season ends at the next `team-started`, the last one at its `season-stopped`, or
    runs (`running`, `paused` under a pause). Each says its bounds and its state; `empty` when no wake-up launched in
    it; its tasks (`tasks_read`: born, woken, closed or stopped in it), counted by their state at its end -- born,
    closed, stopped, open --, each read on the season alone, so that its `by_task` sum to its cost; its `cost` in the three bases (`costs_of`) and its `yield`
    per closed task and per launch; the `task_cost` spread in each base; the cost by `roles` -- a member counted
    under the first role key of `team-started.roles` that holds it, `null` for a member without one --, with its
    share; its `time` (elapsed, active, effort, their ratios, the effort by slot of `SLOT` seconds from its start);
    the `opening` of a wake-up (`wake-intent` -> `wake-launched`); the `principal`'s questions (an `ask` of a member
    to the owner, a mandator or the team) and the wait of their first answer, and under `from_principal` the
    questions a principal asked a member (`post --ask`) and the wait of theirs; the `context` its wake-ups left at
    their end and the runs renewed; its `losses` -- the wake-ups failed, their cost and their reasons (the head of
    each reason, before its `:`), the silences, the `do` beyond the first one per task and member --; then one line
    `by_task` and one `by_member` (`task_face`, `member_face`)."""
    events = [one for one in events if one.get("kind") != "snapshot"]
    starts = [rank for rank, one in enumerate(events) if one.get("kind") == "team-started"]
    seasons, number = [], 0
    for rank, one in enumerate(events):
        if one.get("kind") == "team-started":
            number += 1
        seasons.append(number)
    wakes = wakes_read(events, seasons)
    births = {}                                      # a task by its id -> its name and the season of its birth
    for rank, one in enumerate(events):
        if one.get("kind") == "task" and one.get("task") not in births:
            births[one["task"]] = {"name": one.get("name"), "season": seasons[rank]}
    answered: dict[int, datetime] = {}               # a message by its id -> the hour of its first answer
    for one in events:
        cited = one.get("re") if one.get("verb") == "re" else one.get("reply") if one.get("verb") == "reply" else None
        if one.get("kind") == "post" and isinstance(cited, int) and cited not in answered and moment(one.get("at")):
            answered[cited] = moment(one.get("at"))
    found = []
    for number, rank in enumerate(starts, 1):
        started = events[rank]
        last = starts[number] if number < len(starts) else len(events)
        own = events[rank:last]
        stop = next((one for one in own if one.get("kind") == "season-stopped"), None)
        pause = None
        for one in own:
            pause = one if one.get("kind") == "paused" else None if one.get("kind") == "unpaused" else pause
        begun = moment(started.get("at")) or clock
        if number < len(starts):
            until, state = events[last].get("at"), "stopped"
        elif stop is not None:
            until, state = stop.get("at"), "stopped"
        else:
            until, state = None, "paused" if pause is not None else "running"
        ended = None if until is None else moment(until) or clock
        elapsed = max(0.0, ((ended or clock) - begun).total_seconds())
        mine = [one for one in wakes.values() if one["season"] == number]
        tasks = tasks_read(own, {tag: one for tag, one in wakes.items() if one["season"] == number}, births)
        held_tasks = list(tasks.values())
        posts = [one for one in own if one.get("kind") == "post"]
        cost = costs_of(mine)
        closed = sum(1 for one in held_tasks if one["state"] == "resolved")
        times = times_of(mine, clock)
        slots = [0.0] * max(1, math.ceil(elapsed / SLOT))
        for one in mine:
            if one["launched"] is None:
                continue
            start = max(0.0, (one["launched"] - begun).total_seconds())
            end = max(start, ((one["ended"] or clock) - begun).total_seconds())
            while start < end:
                slot = int(start // SLOT)
                edge = min(end, (slot + 1) * SLOT)
                if slot >= len(slots):
                    slots.extend([0.0] * (slot + 1 - len(slots)))
                slots[slot] += edge - start
                start = edge
        held = dict(started.get("roles") or {})
        agents = list((started.get("agents") or {}).keys())
        role_of = {member: next((key for key, members in held.items() if member in members), None) for member in agents}
        roles = []
        for key in [*held, None]:
            members = [member for member in agents if role_of[member] == key]
            if key is None and not members:
                continue
            part = costs_of([one for one in mine if role_of.get(one["agent"]) == key])
            roles.append({"role": key, "members": members, "cost": part,
                          "share": {base: per(part[base], cost[base]) for base in COST_BASES}})
        principals = {started.get("owner"), started.get("team"), *(started.get("principals") or [])} - {None}
        asks = [one for one in posts if one.get("verb") == "ask" and one.get("to") in principals
                and one.get("from") in agents]
        waits = [(answered[one["id"]] - moment(one.get("at"))).total_seconds() for one in asks
                 if one["id"] in answered and moment(one.get("at")) is not None]
        questions = [one for one in posts if one.get("verb") == "ask" and one.get("from") in principals
                     and one.get("to") in agents]
        awaited = [(answered[one["id"]] - moment(one.get("at"))).total_seconds() for one in questions
                   if one["id"] in answered and moment(one.get("at")) is not None]
        openings = [(one["launched"] - one["intent"]).total_seconds() for one in mine
                    if one["launched"] is not None and one["intent"] is not None]
        used = [one["used"] for one in mine]
        failed = [one for one in mine if one["end"] == "wake-failed"]
        reasons: dict[str, int] = {}
        for one in failed:
            head = str(one["reason"] or "unknown").split(":")[0].strip()
            reasons[head] = reasons.get(head, 0) + 1
        pairs: dict[tuple, int] = {}
        for one in posts:
            if one.get("verb") == "do" and one.get("to") in agents and one.get("task"):
                pairs[(one["task"], one["to"])] = pairs.get((one["task"], one["to"]), 0) + 1
        by_task = [task_face(task, [wakes[tag] for tag in task["tags"]], clock) for task in held_tasks]
        found.append({
            "season": number, "started": started.get("at"), "ended": until,
            "stopped": None if stop is None else stop.get("at"), "state": state, "empty": not cost["launches"],
            "tasks": {"born": sum(1 for one in held_tasks if one["season"] == number), "closed": closed,
                      "stopped": sum(1 for one in held_tasks if one["state"] == "stopped"),
                      "open": sum(1 for one in held_tasks if one["state"] == "open")},
            "cost": cost,
            "yield": {"usd_per_closed": per(cost["usd"], closed), "launches_per_closed": per(cost["launches"], closed),
                      "tokens_per_closed": per(cost["tokens"], closed),
                      "usd_per_launch": per(cost["usd"], cost["launches"])},
            "task_cost": {base: spread([one["cost"][base] for one in by_task]) for base in COST_BASES},
            "roles": roles,
            "time": {"elapsed": round(elapsed), **times, "active_share": per(times["active"], round(elapsed)),
                     "parallelism": per(times["effort"], times["active"]), "slot": SLOT,
                     "effort_by_slot": [round(one) for one in slots]},
            "opening": {"count": len(openings), "median": ranked(openings, 0.5), "p90": ranked(openings, 0.9)},
            "principal": {"asked": len(asks), "answered": len(waits),
                          "wait_median": None if not waits else round(ranked(waits, 0.5)),
                          "wait_max": None if not waits else round(max(waits)),
                          "from_principal": {"asked": len(questions), "answered": len(awaited),
                                             "wait_median": None if not awaited else round(ranked(awaited, 0.5)),
                                             "wait_max": None if not awaited else round(max(awaited))}},
            "context": {"median": ranked(used, 0.5), "p90": ranked(used, 0.9),
                        "max": max((one for one in used if one is not None), default=None),
                        "renewals": sum(1 for one in own if one.get("kind") == "run-renewed")},
            "losses": {"failed": len(failed), "cost": costs_of(failed), "reasons": reasons,
                       "silences": sum(1 for one in own if one.get("kind") == "silence"),
                       "do_extra": sum(count - 1 for count in pairs.values()),
                       "pairs_extra": sum(1 for count in pairs.values() if count > 1), "pairs": len(pairs),
                       "do_per_pair": per(sum(pairs.values()), len(pairs))},
            "by_task": by_task,
            "by_member": [member_face(member, [key for key, members in held.items() if member in members],
                                      [one for one in mine if one["agent"] == member], posts, answered, clock)
                          for member in agents]})
    return found


MEDIAN_OF = (("tasks", "closed"), ("tasks", "stopped"), ("cost", "usd"), ("cost", "launches"), ("cost", "tokens"),
             ("yield", "usd_per_closed"), ("yield", "launches_per_closed"), ("yield", "tokens_per_closed"),
             ("yield", "usd_per_launch"), ("time", "elapsed"), ("time", "active"), ("time", "effort"),
             ("time", "active_share"), ("time", "parallelism"), ("opening", "median"), ("principal", "wait_median"),
             ("context", "median"), ("losses", "failed"), ("losses", "do_per_pair"))


def seasons_median(seasons: list[dict]) -> dict:
    """-> the median of each measure of `MEDIAN_OF` over the seasons given, in their shape."""
    found: dict = {}
    for group, key in MEDIAN_OF:
        found.setdefault(group, {})[key] = ranked([one[group][key] for one in seasons], 0.5)
    return found


def lasted(seconds) -> str:
    """-> a duration said short: `8 s`, `52 min`, `1 h 49`; `-` for none."""
    if seconds is None:
        return "-"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} s"
    if seconds < 3600:
        return f"{seconds // 60} min"
    return f"{seconds // 3600} h {seconds % 3600 // 60:02d}"


def costed_as(cost: dict, base: str) -> str:
    """-> a cost said in its base: `41.2 USD`, `38 launches`, `1200000 tokens` (`~` when estimated), `-` unknown."""
    value = cost.get(base)
    if value is None:
        return "-"
    if base == "usd":
        return f"{value:.2f} USD"
    if base == "tokens":
        return f"{'~' if cost.get('tokens_estimated') else ''}{value} tokens"
    return f"{value} launches"


def share_said(value) -> str:
    return "-" if value is None else f"{round(100 * value)} %"


def season_lines(one: dict, base: str) -> list[str]:
    """-> one season's stats as text, its costs said in `base`."""
    tasks, cost, times, losses = one["tasks"], one["cost"], one["time"], one["losses"]
    unit = {"usd": "usd", "launches": "launches", "tokens": "tokens"}[base]
    per_closed = per(cost[base], tasks["closed"])
    lines = [f"season {one['season']} · {one['state']} · {one['started']} -> {one['ended'] or 'now'} · "
             f"{lasted(times['elapsed'])}" + (" · empty" if one["empty"] else ""),
             f"  tasks     {tasks['closed']} closed · {tasks['stopped']} stopped · {tasks['open']} open",
             f"  cost      {costed_as(cost, base)} · {cost['launches']} launches · "
             f"{'-' if per_closed is None else per_closed} {unit} / closed task",
             f"  task cost min {one['task_cost'][base]['min']} · median {one['task_cost'][base]['median']} · "
             f"max {one['task_cost'][base]['max']} {unit}",
             "  roles     " + (" · ".join(f"{role['role'] or '-'} {share_said(role['share'][base])}"
                                         for role in one["roles"]) or "-"),
             f"  time      {lasted(times['elapsed'])} elapsed · {lasted(times['active'])} active "
             f"({share_said(times['active_share'])}) · {lasted(times['effort'])} effort · "
             f"x{times['parallelism'] if times['parallelism'] is not None else '-'} parallel",
             f"  opening   median {lasted(one['opening']['median'])} · p90 {lasted(one['opening']['p90'])}",
             f"  principal {one['principal']['asked']} asked · {one['principal']['answered']} answered · "
             f"median {lasted(one['principal']['wait_median'])} · max {lasted(one['principal']['wait_max'])}",
             f"  context   median {share_said(one['context']['median'])} · p90 {share_said(one['context']['p90'])} · "
             f"{one['context']['renewals']} renewals",
             f"  losses    {losses['failed']} failed ({costed_as(losses['cost'], base)}) "
             + " ".join(f"{reason} {count}" for reason, count in losses["reasons"].items())
             + f" · {losses['silences']} silences · {losses['do_extra']} do more on {losses['pairs_extra']} "
               f"pairs task x member"]
    return lines


def stats_verb(rest: list[str]) -> int:
    """`team stats`: the stats of a season of the team, computed from its journal alone (`season_stats`) -- the one
    under way or the last by default, `--season <n>` another, `--all` every season not empty with their median, the
    empty ones apart and each task over all its seasons (`tasks_total`); `--cost usd|launches|tokens` the base the text says its costs in, `--json` the object
    with the three bases. Nothing written."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, STATS_FLAGS)
    base = asked["cost"] or "usd"
    if asked["all"] and asked["season"] is not None:
        refuse(USAGE)
    if base not in COST_BASES:
        refuse(f"cost-invalid -- `--cost {base}`: one of {', '.join(COST_BASES)}.")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    seasons = season_stats(lines_of(journal_of(root, name)), tick_now().astimezone(timezone.utc))
    if not seasons:
        refuse(f"team-not-started -- {name} was never started.")
    if asked["all"]:
        full = [one for one in seasons if not one["empty"]]
        said = {"team": name, "base": base, "seasons": full, "median": seasons_median(full),
                "empty": [one["season"] for one in seasons if one["empty"]], "by_task": tasks_total(seasons)}
        if asked["json"]:
            print(json.dumps(said, ensure_ascii=False))
            return 0
        print(f"{name} · {len(seasons)} seasons · {len(said['empty'])} empty")
        for one in full:
            print(f"  s.{one['season']:<3} {str(one['started'])[:10]}  {costed_as(one['cost'], base):>16}  "
                  f"{one['tasks']['closed']:>3} closed  {per(one['cost'][base], one['tasks']['closed'])} / closed  "
                  f"active {share_said(one['time']['active_share'])}  x{one['time']['parallelism']}")
        if said["empty"]:
            print("  empty: " + ", ".join(str(one) for one in said["empty"]))
        return 0
    chosen = seasons[-1]
    if asked["season"] is not None:
        chosen = next((one for one in seasons if str(one["season"]) == asked["season"]), None)
        if chosen is None:
            refuse(f"season-unknown -- {name} has no season `{asked['season']}`: its seasons are 1 to {len(seasons)}.")
    if asked["json"]:
        print(json.dumps({"team": name, "base": base, "season": chosen}, ensure_ascii=False))
        return 0
    print(f"{name} · " + "\n".join(season_lines(chosen, base)))
    return 0


def words_of(root: Path, conductor, path: str, run: str, launch) -> str | None:
    """-> what a launch SAID, its `words` joined by a blank line, read at the run's flow by the house's
    console (`agent flow --exchange <launch> --json`); None when the launch is unknown or its flow
    carries no words."""
    if not run or not isinstance(launch, int):
        return None
    engine = engine_of(root, conductor)
    played = subprocess.run([sys.executable, str(engine), "--instance", str(root), "agent", "flow", path, run,
                             "--json", "--exchange", str(launch)], capture_output=True, text=True,
                            cwd=str(root.parent), env=dict(os.environ))
    if played.returncode != 0:
        return None
    texts = []
    for line in played.stdout.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict) and one.get("kind") == "words" and str(one.get("text") or "").strip():
            texts.append(str(one["text"]).strip())
    return "\n\n".join(texts) if texts else None


def waiting(state: dict) -> dict:
    """-> what waits for the owner: the QUESTIONS -- an agent's `ask` to them on an open task no answer of theirs
    cites --; the NOTICES of the team to them, each in the words of the debt (`worded`) with `awaits` -- a notice about
    a member on an open task no answer cites, which holds that member's wait and stays until the answer --, the others
    since the cursor `inbox-seen`; the INFOS sent to them since the cursor, which hold nobody, in id order -- among
    them an `ask` no answer cites whose task is resolved or stopped: nobody can answer it any more --; the tasks
    resolved and the posts returned to them since the cursor -- an info, a notice that holds nobody, a task resolved
    (by its id) or a post returned the owner marked read one by one (`inbox-read`) leaves too."""
    owner = str((state["started"] or {}).get("owner") or "")
    answered = principal_answered(state)
    to_owner = [one for one in state["messages"].values() if one.get("to") == owner]
    asked = [one for one in to_owner if one.get("verb") == "ask" and one["id"] not in answered]
    questions = [one for one in asked if is_open(state, one.get("task"))]

    def unread(mid: int) -> bool:
        return mid > state["seen"] and mid not in state["read"]

    infos = sorted((one for one in to_owner if unread(one["id"]) and (one.get("verb") == "info" or (
        one in asked and not is_open(state, one.get("task"))))), key=lambda one: one["id"])
    notices = []
    for one in to_owner:
        if not is_notice(state, one):
            continue
        awaits = (notice_about(state, one) is not None and one["id"] not in answered
                  and is_open(state, one.get("task")) and one.get("cause") != "silence")   # a silence holds nobody
        if awaits or unread(one["id"]):
            notices.append({**worded(state, one), "awaits": awaits})
    done = [one for one in state["done"].values() if unread(int(one.get("id") or 0))]
    returned = [mid for mid, to in state["returned_to"].items() if to == owner and unread(mid)]
    return {"questions": questions, "notices": notices, "infos": infos, "done": done, "returned": returned}


def inbox_line(name: str, state: dict) -> str:
    """-> `review: T1 done · 1 question waiting for you · 2 notices · 1 info · 1 post returned`, or '' when
    nothing waits for the owner."""
    waits = waiting(state)
    parts = [f"{one['task']} done" for one in waits["done"]]
    asks, told = len(waits["questions"]), len(waits["notices"])
    if asks:
        parts.append(f"{asks} question{'s' if asks > 1 else ''} waiting for you")
    if told:
        parts.append(f"{told} notice{'s' if told > 1 else ''}")
    if waits["infos"]:
        parts.append(f"{len(waits['infos'])} info{'s' if len(waits['infos']) > 1 else ''}")
    if waits["returned"]:
        parts.append(f"{len(waits['returned'])} post{'s' if len(waits['returned']) > 1 else ''} returned")
    return f"{name}: " + " · ".join(parts) if parts else ""


def inbox_object(name: str, state: dict) -> dict | None:
    """-> what waits for the owner in one team, to READ: the questions, the notices, the infos and the posts returned
    with their texts, the tasks resolved by task and id, each with the `at` of its event -- None when nothing waits.
    `waiting()` decides. Each info says `closed`: true for an ask whose task is resolved or stopped, false for an
    info."""
    waits = waiting(state)
    if not (waits["questions"] or waits["notices"] or waits["infos"] or waits["done"] or waits["returned"]):
        return None

    def post(one: dict) -> dict:
        return {"id": one["id"], "verb": one.get("verb"), "from": one.get("from"), "task": one.get("task"),
                "text": one.get("text"), "at": one.get("at")}

    return {"team": name, "questions": [post(one) for one in waits["questions"]],
            "notices": [{"id": one["id"], "from": one.get("from"), "about": one.get("about"), "task": one.get("task"),
                         "text": one.get("text"), "awaits": one["awaits"], "at": one.get("at")}
                        for one in waits["notices"]],
            "infos": [{"id": one["id"], "from": one.get("from"), "task": one.get("task"), "text": one.get("text"),
                       "closed": one.get("verb") == "ask", "at": one.get("at")} for one in waits["infos"]],
            "done": [{"task": one["task"], "id": one.get("id"), "at": one.get("at")} for one in waits["done"]],
            "returned": [post(state["messages"][mid]) for mid in waits["returned"] if mid in state["messages"]]}


def inbox_verb(rest: list[str]) -> int:
    """`team inbox`: one line per team where something waits for the owner -- under `--json` one
    object per such team, nothing in a run a team opened; `--seen` writes the owner's cursor at the team's
    journal, `--seen --id <n>` marks the one message n read (`inbox-read`) -- the writes of the readers, never
    beside `--json`."""
    # without `--seen`, the house's teams whatever instance calls; `--seen` writes at the instance that calls
    root, conductor = house() if "--seen" in rest else machine_house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, rest = named_team(conductor, rest)
    asked = flags(rest, INBOX_FLAGS)
    if (asked["seen"] and asked["json"]) or (asked["id"] is not None and not asked["seen"]):
        refuse(USAGE)
    one_id = None
    if asked["id"] is not None:
        try:
            one_id = int(asked["id"])
        except ValueError:
            refuse(f"inbox-id-unknown -- `{asked['id']}`: --id names a message of the inbox by its number.")
    if asked["seen"]:
        if name is None:
            refuse("inbox --seen names the team whose inbox was read: `team inbox <name> --seen`.")
        if not team_doc(root, name).is_file():
            refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")

        def judge(state: dict, events: list[dict]) -> list[dict]:
            if state["started"] is None:
                refuse(f"team-not-started -- {name} was never started.")
            if one_id is not None:
                waits = waiting(state)
                if one_id in [one["id"] for one in waits["questions"]] + [
                        one["id"] for one in waits["notices"] if one["awaits"]]:
                    refuse(f"inbox-question -- #{one_id} waits for your answer: `team post {name} --task <id> "
                           f"--reply {one_id}` takes it out of the inbox.")
                held = ([one["id"] for one in waits["notices"] + waits["infos"]] + waits["returned"]
                        + [int(one.get("id") or 0) for one in waits["done"]])
                if one_id not in held:
                    refuse(f"inbox-id-unknown -- #{one_id} is not in the inbox of {name}: `team inbox {name} --json` "
                           "says the ids it holds.")
                return [{"kind": "inbox-read", "message": one_id}]
            upto = max((int(one.get("id") or 0) for one in events), default=0)
            return [{"kind": "inbox-seen", "upto": upto}] if upto > state["seen"] else []

        made = written(conductor, root, journal_of(root, name), name, judge)
        if one_id is not None:
            print(f"pp-team: {name} · #{one_id} read")
            return 0
        print(f"pp-team: {name} · inbox seen up to #{made[0]['upto']}" if made else f"pp-team: {name} · inbox seen already")
        return 0
    meta = caller()
    if meta is not None and in_team_run(root, conductor, meta):
        return 0                                   # the owner's inbox is the owner's: a member's run reads none
    home = root.parent / TEAMS
    names = [name] if name else (sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else [])
    for one in names:
        state = state_of(journal_of(root, one))
        if state["started"] is None:
            continue
        if asked["json"]:
            found = inbox_object(one, state)
            if found is not None:
                print(json.dumps({**found, "name": team_name(root, conductor, one)}, ensure_ascii=False))
            continue
        line = inbox_line(labelled(root, conductor, one), state)
        if line:
            print(line)
    return 0


def run_documents(conductor, meta: Path) -> str:
    """-> the root of documents of the run the call plays in: `PP_DOCUMENTS`, the root the launcher gives the run (at
    its `-new`, while its slot is staged in the engine's process and not on disk yet), else the root kept at the slot
    of the run `PP_RUN` names at `meta`; "" without one."""
    documents = os.environ.get(conductor.context.DOCUMENTS, "").strip()
    run = os.environ.get(conductor.context.VARIABLE, "").strip()
    if not documents and run:
        slot = conductor.persistence.slot_of(meta, run)
        documents = conductor.persistence.documents_of(slot) if slot.exists() else ""
    return documents or ""


def member_judged(root: Path, conductor, ident: str) -> tuple[str, str, dict]:
    """-> (team, member, the team's `team-started`) a vector `team-member:<team>/<member>` names, judged for the
    instance and the run that ask -- each defect refused by its code, read-only: `team-unknown` (no `TEAM.md`),
    `team-not-started`, `member-unknown` (a member the season under way does not know), `member-foreign` (the instance
    calling, `PP_HOME`, is not the agent that plays the member), `root-foreign` (the run's root of documents is not
    the team's directory)."""
    name, _, member = ident.strip().partition("/")
    if not name or not team_doc(root, name).is_file():
        refuse(f"team-unknown -- `{name}`: no {TEAMS}/{name}/{TEAM_DOC} in this house.")
    started = state_of(journal_of(root, name))["started"]
    if not started:
        refuse(f"team-not-started -- `{name}`: no season under way, no member's view to mount.")
    agents = started.get("agents") or {}
    if member not in agents:
        refuse(f"member-unknown -- `{member}`: the season of `{name}` knows {', '.join(agents) or 'nobody'}.")
    calling = caller()
    if calling is None or calling.resolve() != agent_meta(root, agents[member]).resolve():
        refuse(f"member-foreign -- `{name}/{member}` is played by {agents[member]}: another agent's vector is never "
               "mounted.")
    documents = run_documents(conductor, calling)
    if not documents or Path(documents).resolve() != team_root(root, name).resolve():
        refuse(f"root-foreign -- the run's root of documents is `{documents or 'none'}`, not {TEAMS}/{name}/: a "
               "member's documents are mounted under its team's directory alone.")
    return name, member, started


def verify_verb(rest: list[str]) -> int:
    """`pp-team verify` (the vector on stdin): the VERIFIER of the family `team-member:<team>/<member>` -- the
    engine's call when a launcher is given a member's vector, never an agent's. Judged by `member_judged`; a family
    this package does not declare refuses `family-foreign`. Reads only, writes nothing, takes no lock."""
    if rest:
        refuse(USAGE)
    root, conductor = machine_house()
    prefix, _, ident = conductor.reading.piped().strip().partition(":")
    if prefix != MEMBER_FAMILY:
        refuse(f"family-foreign -- `{prefix}:` is not a family this package verifies ({MEMBER_FAMILY})")
    member_judged(root, conductor, ident)
    return 0


def mount_verb(rest: list[str]) -> int:
    """`pp-team mount <team>/<member>`: what the member's vector mounts -- the launcher's gesture at every exchange
    of the member's run, never an agent's. Judged as `verify` judges (`member_judged`), then the member's view in the
    season under way (`season_view`): ONE line `::mount` with an entry per document of its roles, in the
    start's order -- `{"doc": "roles/TEAM-<team>-<name>.md", "body": true}` for one that
    mounts, the same with `"constraints": false, "tools": false` for one that is served. Nothing printed for a member
    without one. Reads only, writes nothing, takes no lock, never a tick."""
    if len(rest) != 1:
        refuse(USAGE)
    root, conductor = machine_house()
    name, member, started = member_judged(root, conductor, rest[0])
    entries = [{"doc": one["document"], "body": True,
                **({} if one["effect"] == "mounted" else {"constraints": False, "tools": False})}
               for one in season_view(root, conductor, name, started, member) if one["by"] == "vector"]
    if entries:
        print("::mount " + json.dumps(entries))
    return 0


def in_team_run(root: Path, conductor, meta: Path) -> bool:
    """-> whether the call plays in a run a TEAM opened: its root of documents is the directory of a team of the
    house -- `PP_DOCUMENTS`, the root the launcher gives the run (at its `-new`, while its slot is staged in the
    engine's process and not on disk yet), else the root kept at the slot of the run `PP_RUN` names at `meta`."""
    documents = run_documents(conductor, meta)
    if not documents:
        return False
    directory = Path(documents).resolve()
    return directory.parent == (root.parent / TEAMS).resolve() and (directory / TEAM_DOC).is_file()


def roster_of(root: Path, conductor, meta: Path | None) -> dict:
    """-> `{teams, recurrences}` of the house: each team declared under `teams/` -- its row as the team plays
    (`team_played`: its members, its root, `TEAM.md`'s or its template's form's; none of a declaration refused), the part
    the instance `meta` plays in it by the paths of `agents:` --, then each live recurrence of a started team."""
    home = root.parent / TEAMS
    names = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    teams, recurrences = [], []
    for name in names:
        try:
            team = team_played(root, conductor, name)
        except (Declined, OSError, SystemExit):
            team = {"agents": {}, "root": None}
        agents = list(team["agents"].items())
        mine = [member for member, path in agents
                if meta is not None and meta != root.resolve() and agent_meta(root, path).resolve() == meta]
        head = team["root"]
        part = (f"root ({head})" if head in mine else
                f"member ({', '.join(mine)})" if mine else "—")
        state = faced(root, conductor, name)
        teams.append({"team": name, "name": team_name(root, conductor, name),
                      "description": team_description(root, conductor, name), "root": head,
                      "members": len(agents), "state": team_state(state)["state"], "membership": part})
        for one in state["recurrences"].values():
            if one.get("stopped") is None:
                recurrences.append({"team": name, "id": one["id"], "description": one.get("description") or one.get("name"),
                                    "when": said_when(one["when"]) if one.get("when") else None,
                                    "next_due": recurrence_next(one),
                                    "paused": bool(one.get("paused"))})
    return {"teams": teams, "recurrences": recurrences}


def roster_verb(rest: list[str]) -> int:
    """`team roster [--json]`: the teams of the house and their live recurrences, the caller's part in each -- read
    at the house `machine_house()` resolves; nothing printed without a team, nor in a run a team opened. Nothing
    written, no lock, never a tick."""
    root, conductor = machine_house()
    asked = flags(rest, ROSTER_FLAGS)
    meta = caller()
    if meta is not None and in_team_run(root, conductor, meta):
        return 0
    found = roster_of(root, conductor, meta)
    if not found["teams"]:
        return 0
    if asked["json"]:
        print(json.dumps(found, ensure_ascii=False))
        return 0
    cell = lambda value: "—" if value in (None, "") else " ".join(str(value).split()).replace("|", "\\|")
    lines = ["**The teams of the house**", "", "| team | what it does | root | members | state | your part |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {cell(one['name'])} | {cell(one['description'])} | {cell(one['root'])} | {one['members']} | "
              f"{cell(one['state'])} | {cell(one['membership'])} |" for one in found["teams"]]
    if found["recurrences"]:
        lines += ["", "**The recurrences**", "", "| team | id | what it does | when | next | paused |",
                  "|---|---|---|---|---|---|"]
        lines += [f"| {cell(one['team'])} | {cell(one['id'])} | {cell(one['description'])} | {cell(one['when'])} | "
                  f"{cell(one['next_due'])} | {'yes' if one['paused'] else 'no'} |" for one in found["recurrences"]]
    print("\n".join(lines))
    return 0


def entry_verb(rest: list[str]) -> int:
    """`team entry <name> [--run <key>]` -- prints the document the team's wake-up under that run
    (`PP_RUN` when `--run` is absent) plays this exchange (`entry_of`): the decider of the team's
    document, played by the agent's engine -- whose `PP_HOME` names the AGENT, so the house is the
    machine this script lives in, never the instance served. A team never started, a key no wake-up
    of the team holds: the neutral `TEAM-IDLE.md`, so that the agent's exchange always goes on.
    Nothing written."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, ENTRY_FLAGS)
    run = asked["run"] or os.environ.get("PP_RUN", "").strip()
    if not run:
        refuse(USAGE)
    print(entry_of(root, name, run))
    return 0


def run_named(root: Path, conductor, path: str, run: str, text: str) -> str:
    """`agent name <path> <run> <text>` by the house's console: an opening carries its carrier's name. -> ''
    once named, else what the house said -- the wake-up plays on unnamed."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent", "name",
                             path, run, text], capture_output=True, text=True, cwd=str(root.parent), env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-200:] or f"rc {played.returncode}"


def forgotten(root: Path, conductor, path: str, run: str) -> str:
    """`-reset <run>` by the console of the agent at `path` -- the house's engine addressing the
    agent's instance, the gesture an owner plays by hand. -> '' once forgotten, else what the
    engine said (`call-busy`: a call holds the run)."""
    meta = agent_meta(root, path)
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(meta), "-reset", run],
                            capture_output=True, text=True, cwd=str(meta.parent), env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def reset_verb(rest: list[str]) -> int:
    """`team reset <name> [--member <m>]`: every run of each member named -- every member without
    `--member` -- forgotten by its agent's console, one `run-reset {member, run}` per run; the next
    wake-up of the member on a task opens a new run, a new session, told the history of that task's carrier.
    Judged before anything is forgotten, under `tick.lock` waited within `call_lock_wait`
    (`team-busy` beyond) and held to the last write: no tick launches on a key being forgotten.
    A member without a run is said, nothing written for it; an agent's console that refuses stops
    the verb, the members forgotten before it written."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESET_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    journal = journal_of(root, name)
    journal.parent.mkdir(parents=True, exist_ok=True)
    lock = locks(conductor)
    lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
    if lease is None:
        refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing forgotten, "
               "replay once it has played.")
    said: list[str] = []
    try:
        state = state_of(journal)
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started: nothing to forget.")
        members = list((state["started"].get("agents") or {}))
        if asked["member"] is not None:
            if not is_member(state, asked["member"]):
                refuse(f"participant-unknown -- `{asked['member']}` is no member of {name}.")
            members = [asked["member"]]
        for member in members:
            runs = list(dict.fromkeys((state["runs"].get(member) or {}).values()))
            held = next((run for run in runs if held_run(root, conductor, path_of(state, member), run)), None)
            if busy(state, member) or held is not None:
                refuse(f"member-running -- a wake-up of {member} plays" + (f" in run {held}" if held else "")
                       + ": nothing forgotten, replay once it has ended.")
        for member in members:
            runs = list(dict.fromkeys((state["runs"].get(member) or {}).values()))
            if not runs:
                said.append(f"{member} · no run to forget")
            for run in runs:                                     # every run of the member, one per carrier
                why = forgotten(root, conductor, path_of(state, member), run)
                if why:
                    for line in said:
                        print(f"pp-team: {name} · {line}")
                    refuse(f"reset-failed -- the console of {path_of(state, member)} kept run {run}: {why}")
                made = appended(conductor, root, journal, name, [{"kind": "run-reset", "member": member, "run": run}])
                said.append(f"{member} · run {run} forgotten (run-reset #{made[0]['id']})")
    finally:
        lock.release(lease)
    for line in said:
        print(f"pp-team: {name} · {line}")
    if (journal.parent / TICK_MARK).exists():
        ticked(root, conductor, name)              # a tick asked while the reset held the lock plays now
    return 0


def team_runs(state: dict, events: list[dict]) -> list[dict]:
    """-> every run a wake-up of the team opened, `{member, path, run}` in the order the journal met them: the
    runs its `wake-launched` and `wake-ended` name, a member's path read at its intent or at the start."""
    paths: dict[str, str] = {}
    by_tag: dict[str, str] = {}
    found: dict[tuple[str, str], dict] = {}
    for one in events:
        kind = one.get("kind")
        if kind == "team-started":
            paths.update({str(member): str(path) for member, path in (one.get("agents") or {}).items()})
        elif kind == "wake-intent" and one.get("path"):
            by_tag[str(one.get("tag"))] = str(one["path"])
        elif kind in ("wake-launched", "wake-ended") and one.get("run"):
            member = str(one.get("agent"))
            path = by_tag.get(str(one.get("tag"))) or paths.get(member)
            if path:
                found.setdefault((path, str(one["run"])), {"member": member, "path": path, "run": str(one["run"])})
    for member, run in ((member, run) for member, held in state["runs"].items() for run in held.values()):
        if run and paths.get(member):
            found.setdefault((paths[member], run), {"member": member, "path": paths[member], "run": run})
    return list(found.values())


def declared_paths(root: Path, conductor, name: str) -> set[str]:
    """-> the paths of the agents a team's `TEAM.md` declares; none when it cannot be read or judged."""
    try:
        return set(team_played(root, conductor, name)["agents"].values())
    except (Declined, OSError, SystemExit):
        return set()


def purged(root: Path, conductor, path: str, runs: list[str]) -> str:
    """`agent purge <path> <run> ... --yes` by the house's console -> '' once removed, else what it said."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent",
                             "purge", path, *runs, "--yes"], capture_output=True, text=True, cwd=str(root.parent),
                            env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def purged_already(said: str) -> set[str]:
    """-> the run keys `agent purge` refused as `run-unknown` -- runs no longer at the agent: a delete taken up after
    a `delete-failed` purged them the first time, nothing of them is left."""
    found = re.search(r"run-unknown -- `([^`]*)`", said or "")
    return set(found.group(1).split()) if found else set()


def agents_asked(rest: list[str]) -> tuple[list[str], list[str]]:
    """-> (the paths `--agent <path>` names, in their order, each once; the rest of the flags)."""
    paths, kept, index = [], [], 0
    while index < len(rest):
        if rest[index] == "--agent":
            if index + 1 >= len(rest) or rest[index + 1].startswith("--"):
                refuse(USAGE)
            paths.append(rest[index + 1])
            index += 2
            continue
        kept.append(rest[index])
        index += 1
    return list(dict.fromkeys(paths)), kept


def agent_removed(root: Path, conductor, path: str) -> str:
    """`agent remove <path> --yes` by the house's console -> '' once removed, else what it said."""
    played = subprocess.run([sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "agent",
                             "remove", path, "--yes"], capture_output=True, text=True, cwd=str(root.parent),
                            env=dict(os.environ))
    return "" if played.returncode == 0 else (played.stderr or played.stdout).strip()[-300:] or f"rc {played.returncode}"


def delete_verb(rest: list[str]) -> int:
    """`team delete <name> [--agent <path>]... [--yes] [--json]`: removes the team and what it made -- its timer, its
    relaunch entry, every run its wake-ups opened (by `agent purge`, at each agent), its journal and the files beside
    it, then its directory, the owner's declaration and documents with it -- and, under `--agent`, the agents named
    (by `agent remove`, after the purge of the runs and before the directory goes). An agent named must be one the
    dry face lists under `agents` -- declared by this team and by no other -- else `agent-shared`, judged before any
    write. Without `--yes` it says what it would remove and writes nothing. Judged under `tick.lock` waited within
    `call_lock_wait` (`team-busy` beyond) and held to the end: `team-unknown`, `team-busy` while a task is open or a
    wake-up plays. Under `--yes`, the tasks are judged again and `deleting` written in ONE section of the journal's
    lock, before anything is removed: a task a post wrote meanwhile -- a post takes the journal's lock alone --
    refuses `team-busy`, nothing written, the timer, the relaunch entry and the runs in place; once `deleting` stands,
    every writer that opens work -- a post, a start, a resume, a ring -- refuses `team-deleting`, the tick rings and
    sounds nothing, and the team's guard lets its runs go. A purge or a removal refused stops the verb, said --
    `delete` played again goes on: a run its agent no longer knows (`run-unknown`) was purged the first time. The
    journal's directory and the team's directory leave last, under `tick.lock`; a write that comes after finds no
    declaration (`written`). The agents not named stay: the ones no other team declares are said."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    wanted, rest = agents_asked(rest)
    asked = flags(rest, DELETE_FLAGS)
    directory = team_root(root, name)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    journal = journal_of(root, name)
    lock = locks(conductor)
    lease = None
    if journal.parent.is_dir():
        lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
        if lease is None:
            refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing removed, "
                   "replay once it has played.")
    try:
        state = state_of(journal)
        events = lines_of(journal) if journal.is_file() else []
        opened = [one["id"] for one in state["tasks"].values() if one["state"] == "open"]
        if opened or open_intents(state):
            refuse(f"team-busy -- {name} is at work ({', '.join(opened) or 'a wake-up plays'}): stop it first "
                   f"(`team stop {name} --kill`), then delete it.")
        runs = team_runs(state, events)
        relaunch = relaunch_standing(root)
        timer = bool(timer_standing(root, name))
        mine = set((state["started"] or {}).get("agents", {}).values()) if state["started"] else set()
        mine |= declared_paths(root, conductor, name)
        home = root.parent / TEAMS
        others: set[str] = set()
        for other in (sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []):
            if other != name:
                others |= declared_paths(root, conductor, other)
        agents = sorted(mine - others)
        shared = [one for one in wanted if one not in agents]
        if shared:
            refuse(f"agent-shared -- {', '.join(shared)}: not an agent {name} alone declares (another team declares it, "
                   f"or none does); the agents the team may take away are {', '.join(agents) or 'none'}; nothing removed.")
        told = {"team": name, "name": team_name(root, conductor, name), "dry": not asked["yes"],
                "directory": str(directory.relative_to(root.parent)),
                "journal": str(journal.parent.relative_to(root.parent)) if journal.parent.is_dir() else None,
                "relaunch": relaunch, "timer": timer, "runs": runs, "agents": agents, "removed": []}
        if asked["yes"]:
            def judge(now: dict, lines: list[dict]) -> list[dict]:
                at_work = [one["id"] for one in now["tasks"].values() if one["state"] == "open"]
                if at_work or open_intents(now):
                    refuse(f"team-busy -- {name} is at work ({', '.join(at_work) or 'a wake-up plays'}): stop it "
                           f"first (`team stop {name} --kill`), then delete it.")
                return [] if now.get("deleting") else [{"kind": "deleting"}]

            if journal.is_file():
                written(conductor, root, journal, name, judge)
            disarmed(root, name)
            if relaunch:
                relaunch_removed(root, conductor, name, but=name)
            by_path: dict[str, list[str]] = {}
            for one in runs:
                by_path.setdefault(one["path"], []).append(one["run"])
            for path, keys in by_path.items():
                if not agent_meta(root, path).is_dir():
                    continue
                why = purged(root, conductor, path, keys)
                gone = purged_already(why)
                if gone and set(keys) - gone:              # a delete taken up: what an earlier one purged is gone
                    why = purged(root, conductor, path, [one for one in keys if one not in gone])
                elif gone:
                    why = ""
                if why:
                    refuse(f"delete-failed -- the purge of {', '.join(keys)} at {path} refused: {why} -- nothing more "
                           f"removed; `team delete {name} --yes` again goes on")
            for path in wanted:
                if not agent_meta(root, path).is_dir():
                    continue
                why = agent_removed(root, conductor, path)
                if why:
                    refuse(f"delete-failed -- the removal of {path} refused: {why} -- nothing more removed; "
                           f"`team delete {name} --yes` again goes on")
                told["removed"].append(path)
            shutil.rmtree(journal.parent, ignore_errors=True)
            shutil.rmtree(directory, ignore_errors=True)
    finally:
        if lease is not None:
            lock.release(lease)
    if asked["json"]:
        print(json.dumps(told, ensure_ascii=False))
        return 0
    verb = "removed" if asked["yes"] else "would remove"
    print(f"pp-team: {name} · {verb}: {told['directory']}" + (f", {told['journal']}" if told["journal"] else "")
          + (", the relaunch entry" if relaunch else "") + (", the timer" if timer else "")
          + (f", {len(runs)} run(s): " + ", ".join(f"{one['path']} {one['run']}" for one in runs) if runs else ""))
    if told["removed"]:
        print(f"pp-team: {name} · the agents removed: {', '.join(told['removed'])}")
    staying = [one for one in agents if one not in told["removed"]]
    if staying:
        print(f"pp-team: {name} · the agents stay: {', '.join(staying)} -- no other team declares them"
              + ("" if asked["yes"] else f" (`--agent <path>` takes one away)"))
    if not asked["yes"]:
        print(f"pp-team: {name} · nothing written -- `team delete {name} --yes` removes it")
    return 0


def rename_verb(rest: list[str]) -> int:
    """`team rename <name> <new> [--json]`: moves the team to a new directory name -- its identity. Judged before any
    write: `new` as a team's name (`team-invalid`), `team-unknown`, `team-exists` when `teams/<new>/` or the records of
    `<new>` stand, `team-busy` under `tick.lock` past `call_lock_wait` or while a task is open or a wake-up plays.
    Then, the lock held: the timer disarmed (the next tick arms it again), `teams/<name>/` moved to `teams/<new>/`
    with the intention `TEAM-<name>.md` renamed `TEAM-<new>.md` inside it, the records of the team (its journal and
    the files beside it) moved, and `name:` of `TEAM.md` rewritten when it was the old directory's name -- a name of
    the owner's own stays. The house's relaunch entry does not change; the members' entries are laid again at the
    next start. Under `--json` ONE object `{from, to, name}`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    new, rest = named_team(conductor, rest)
    asked = flags(rest, RENAME_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    directory, target = team_root(root, name), team_root(root, new)
    journal, moved = journal_of(root, name), journal_of(root, new)
    if new == name or target.exists() or moved.parent.exists():
        refuse(f"team-exists -- {target} or its records stand already: another name.")
    lock = locks(conductor)
    lease = None
    if journal.parent.is_dir():
        lease = lock.acquire(journal.parent / TICK_LOCK, wait=call_wait(root, conductor))
        if lease is None:
            refuse(f"team-busy -- a tick of {name} holds {TICK_LOCK} past call_lock_wait: nothing moved, "
                   "replay once it has played.")
    try:
        state = state_of(journal)
        opened = [one["id"] for one in state["tasks"].values() if one["state"] == "open"]
        if opened or open_intents(state):
            refuse(f"team-busy -- {name} is at work ({', '.join(opened) or 'a wake-up plays'}): stop it first "
                   f"(`team stop {name} --kill`), then rename it.")
        shown = team_name(root, conductor, name)
        disarmed(root, name)
        own = directory / document_name(name)
        if own.is_file() and not (directory / document_name(new)).exists():
            os.replace(own, directory / document_name(new))
        if journal.parent.is_dir():
            moved.parent.parent.mkdir(parents=True, exist_ok=True)
            os.replace(journal.parent, moved.parent)
        os.replace(directory, target)
    finally:
        if lease is not None:
            lock.release(lease)
    if shown == name:
        doc = team_doc(root, new)
        text = doc.read_text(encoding="utf-8")
        lines = text.split("\n")
        end = lines.index(BORDER, 1) if BORDER in lines[1:] else 0
        for index in range(1, end):
            if lines[index].rstrip() == f"name: {name}":
                lines[index] = f"name: {new}"
                placed(doc, "\n".join(lines).encode("utf-8"))
                break
        shown = new
    if asked["json"]:
        print(json.dumps({"from": name, "to": new, "name": shown}, ensure_ascii=False))
        return 0
    print(f"pp-team: {name} · renamed {new} · {TEAMS}/{new}/ and its records moved"
          + (f" · name: {shown}" if shown == new else f" · shown as {shown}"))
    return 0


def spent(root: Path, state: dict) -> str:
    """-> what the team has spent past its own bound since its last start, '' when nothing: the money
    (`budget`), the wake-ups launched (`budget-launches`), or a `budget-spent` already written -- the
    bounds of step 5, which a resume never resets."""
    limits = state["limits"]
    if state["budget_spent"]:
        return "budget-spent is written since the last start"
    if limits.get("budget") is not None and state["cost"] >= limits["budget"]:
        return f"{state['cost']:g} of {limits['budget']:g} USD spent"
    if limits.get("budget-launches") is not None:
        launched = launched_since_start(root, state)
        if launched >= limits["budget-launches"]:
            return f"{launched} of {limits['budget-launches']} launches"
    return ""


def launched_since_start(root: Path, state: dict) -> int:
    """-> the team's wake-ups LAUNCHED since its last `team-started` -- the `wake-launched` event,
    else the tag at the house's `messages.jsonl`: what `budget-launches` counts."""
    started = state["started"] or {}
    tagged = {str(one.get("tag")) for one in lines_of(record_of(root, MESSAGES)) if one.get("tag")}
    return sum(1 for tag, one in state["intents"].items()
               if int(one.get("id") or 0) > int(started.get("id") or 0) and went(state, tagged, tag))


def resume_verb(rest: list[str]) -> int:
    """`team resume <name> --task <id> [--to <member>|all] [--message <text>] [--as <principal>] [--no-tick]`: takes
    back ONE task a guard left with nobody due -- stopped, held by a member's final failure, or past
    `launches:` --, judged under the journal's lock before anything is written; then `resumed {task, by,
    from}`, the origin the task's counters count from, and an `info` from the resumer to each member it
    revives: the holders at the stop, the members whose final failure stands, the members with
    messages due past `launches:` -- under `--to`, to the member it names alone, or to every member of the
    season under `all`; a member the season does not know refuses `member-unknown`, `--to` without `--task` is the
    usage. The posts returned at the stop stay returned; the team's `budget` and
    `budget-launches` are never reset; off season it refuses `season-stopped`. Then the relaunch entry laid again,
    and a tick unless `--no-tick`.
    With `--recurrence`, one suspended recurrence taken back (`recurrence_resumed`): beside `--task` or `--message`,
    the usage. In the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESUME_FLAGS)
    if asked["to"] is not None and asked["task"] is None:
        refuse(USAGE)                                     # --to names whom a task's resume tells
    if asked["quota"]:
        if asked["task"] is not None or asked["recurrence"] is not None or asked["message"] is not None:
            refuse(USAGE)                                 # a limit lifted alone: a task by --task
        return quota_lifted(root, conductor, name, asked)
    if asked["member"] is not None:
        refuse(USAGE)                                     # --member names whose limit --quota lifts
    if asked["recurrence"] is not None:
        if asked["task"] is not None or asked["message"] is not None:
            refuse(USAGE)                                 # a recurrence resumes alone: a task by --task
        return recurrence_resumed(root, conductor, name, asked)
    if asked["task"] is None:
        if asked["message"] is not None:
            refuse(USAGE)
        return unpause(root, conductor, name, asked)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)
    text = asked["message"] if asked["message"] is not None else RESUMED

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["deleting"]:
            refuse(deleting_said(name))
        if state["stopped"]:
            refuse(off_season(name, state))
        sender = principal_of(state, owner, asked["as"])
        season = list((state["started"].get("agents") or {}))
        if asked["to"] is not None and asked["to"] != ALL and asked["to"] not in season:
            refuse(f"member-unknown -- `{asked['to']}` is no member of {name}'s season: its members are "
                   f"{', '.join(season)}, or `{ALL}`.")
        task = state["tasks"].get(asked["task"])
        if task is None:
            refuse(f"task-unknown -- no task `{asked['task']}` of {name}: the tasks are "
                   f"{', '.join(state['tasks']) or 'none'}.")
        if task["state"] == "resolved":
            refuse(f"task-resolved -- {task['id']} is resolved: a post opens a new task instead.")
        why = spent(root, state)
        if why:
            refuse(f"budget-spent -- {name}: {why}; a resume never resets the team's budget -- `team budget "
                   f"{name} <usd> | --launches <n>` raises it.")
        fell = [agent for agent, one in sorted(state["fell"]) if one == task["id"]]
        causes = ((["stopped"] if task["state"] == "stopped" else []) + (["failed"] if fell else [])
                  + (["launches-spent"] if task["id"] in state["launches_spent"] else []))
        halted = [one["agent"] for one in state["halts"] if one.get("task") == task["id"]]
        limited = [member for member in members_of(state, task["id"])
                   if member in state["quotas"] and state["quotas"][member].get("until") is None]
        causes += (["halted"] if halted else []) + (["quota"] if limited else [])
        if not causes:
            refuse(f"task-not-blocked -- {task['id']} is open, no final failure stands on it and its launches "
                   "are not spent: nothing to take back.")
        revived = holders(state, task) if task["state"] == "stopped" else []
        revived += fell + halted + limited
        if task["id"] in state["launches_spent"]:
            revived += [agent for agent in (state["started"].get("agents") or {})
                        if any(one.get("task") == task["id"] for one in inbox(state, agent))]
        if asked["to"] is not None:                       # the resume aimed: the member named, or every one
            revived = season if asked["to"] == ALL else [asked["to"]]
        return ([{"kind": "resumed", "task": task["id"], "by": sender, "from": causes}]
                + [{"kind": "post", "task": task["id"], "from": sender, "to": one, "verb": "info", "text": text}
                   for one in dict.fromkeys(revived)])

    made = written(conductor, root, journal, name, judge)
    for one in made:
        if one["kind"] == "resumed":
            print(f"pp-team: {name} · {one['task']} · resumed #{one['id']} from {', '.join(one['from'])}")
        else:
            print(f"pp-team: {name} · {one['task']} · post #{one['id']} info {one['from']} -> {one['to']}")
    netted(root, conductor, name, state_of(journal))   # the task open again: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def pause_verb(rest: list[str]) -> int:
    """`team pause <name> [--as <principal>]`: the team PAUSED -- `paused {by}`, judged under the journal's
    lock; nothing killed, no tick: the wake-ups under way end on their own, and until `team resume <name>`
    the tick reaps and routes but rings and wakes nobody; a team off season refuses `season-stopped`, its stop ends
    the pause. With `--recurrence`, one recurrence suspended alone (`recurrence_paused`). In the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, PAUSE_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    if asked["recurrence"] is not None:
        return recurrence_paused(root, conductor, name, owner, asked)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["stopped"]:
            refuse(off_season(name, state))
        sender = principal_of(state, owner, asked["as"])
        if state["paused"]:
            refuse(f"team-paused -- {name} is paused since #{state['paused'].get('id')}: `team resume {name}` "
                   "takes it back.")
        return [{"kind": "paused", "by": sender}]

    made = written(conductor, root, journal_of(root, name), name, judge)[0]
    running = len(open_intents(state_of(journal_of(root, name))))
    print(f"pp-team: {name} · paused #{made['id']} by {made['by']} · {running} wake-up(s) under way end on their own"
          f" · nobody is woken until `team resume {name}`")
    return 0


def quota_lifted(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> --quota [--member <member>] [--as <principal>] [--no-tick]`: the provider's limit lifted by
    the owner -- the member's, or every member's a limit holds now, dated or not --, judged under the journal's lock:
    `team-unknown`, `team-not-started`, `team-deleting`, `season-stopped`, `principal-unknown`, `member-unknown` (a
    member the season under way does not know), `quota-not-held` (no limit holds the member, or nobody); then ONE
    `quota-lifted {by, members}`, the relaunch entry laid again, and a tick unless `--no-tick`: each member lifted is
    launched on what waits for it (s.1811, team 1.35.11)."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["deleting"]:
            refuse(deleting_said(name))
        if state["stopped"]:
            refuse(off_season(name, state))
        sender = principal_of(state, owner, asked["as"])
        agents = state["started"].get("agents") or {}
        if asked["member"] is not None and asked["member"] not in agents:
            refuse(f"member-unknown -- `{asked['member']}`: the season of `{name}` knows "
                   f"{', '.join(agents) or 'nobody'}.")
        clock = tick_now()
        named = [asked["member"]] if asked["member"] is not None else list(agents)
        lifted = [member for member in named if quota_of(state, member, clock) is not None]
        if not lifted:
            refuse(f"quota-not-held -- no provider's limit holds {asked['member'] or 'a member of ' + name} now: "
                   "nothing to lift.")
        return [{"kind": "quota-lifted", "by": sender, "members": lifted}]

    made = written(conductor, root, journal, name, judge)[0]
    print(f"pp-team: {name} · quota-lifted #{made['id']} {', '.join(made['members'])} by {made['by']}")
    netted(root, conductor, name, state_of(journal))   # the members free again: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def unpause(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> [--as <principal>] [--no-tick]`: the paused team taken back -- `unpaused {by}`,
    judged under the journal's lock; then the relaunch entry laid again, and a tick unless `--no-tick`:
    what is due now, each member in its own run."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["deleting"]:
            refuse(deleting_said(name))
        sender = principal_of(state, owner, asked["as"])
        if not state["paused"]:
            refuse(f"team-not-paused -- {name} is not paused: `team resume {name} --task <id>` takes a task back.")
        return [{"kind": "unpaused", "by": sender}]

    made = written(conductor, root, journal, name, judge)[0]
    print(f"pp-team: {name} · unpaused #{made['id']} by {made['by']}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # the team back: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def held_recurrence(state: dict, name: str, called: str) -> dict:
    """-> the recurrence `called` of the team, live: `recurrence-unknown` (the ids said), `recurrence-stopped`."""
    recurrence = state["recurrences"].get(called)
    if recurrence is None:
        refuse(f"recurrence-unknown -- no recurrence `{called}` of {name}: the recurrences are "
               f"{', '.join(state['recurrences']) or 'none'}.")
    if recurrence["stopped"] is not None:
        refuse(f"recurrence-stopped -- {recurrence['id']} was stopped at #{recurrence['stopped']['id']}.")
    return recurrence


def recurrence_paused(root: Path, conductor, name: str, owner: str, asked: dict) -> int:
    """`team pause <name> --recurrence <R<n>> [--as <principal>]`: ONE recurrence SUSPENDED -- `recurrence-paused
    {recurrence, by}`, judged under the journal's lock (`team-not-started`, `principal-unknown`, `recurrence-unknown`,
    `recurrence-stopped`, `recurrence-paused`); no tick. It sounds no period and arms no timer until its resume, stays
    live -- changed by `team recurrence`, stopped by `team stop --recurrence` -- and its open occurrence lives on; the
    team's pause is another matter."""

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        recurrence = held_recurrence(state, name, asked["recurrence"])
        if recurrence.get("paused"):
            refuse(f"recurrence-paused -- {recurrence['id']} is paused since #{recurrence['paused']['id']}: `team "
                   f"resume {name} --recurrence {recurrence['id']}` takes it back.")
        return [{"kind": "recurrence-paused", "recurrence": recurrence["id"], "by": sender}]

    made = written(conductor, root, journal_of(root, name), name, judge)[0]
    print(f"pp-team: {name} · recurrence {made['recurrence']} paused #{made['id']} by {made['by']} -- no period sounds "
          f"until `team resume {name} --recurrence {made['recurrence']}`, its open occurrence lives on")
    return 0


def recurrence_resumed(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> --recurrence <R<n>> [--as <principal>] [--no-tick]`: ONE suspended recurrence taken back --
    `recurrence-resumed {recurrence, by, since}`, `since` the local hour of the resume, judged under the journal's lock
    (`team-unknown`, `team-not-started`, `principal-unknown`, `recurrence-unknown`, `recurrence-stopped`,
    `recurrence-live`); nothing caught up: its next period is the first after `since`. Then the net laid again, and a
    tick unless `--no-tick`."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["deleting"]:
            refuse(deleting_said(name))
        sender = principal_of(state, owner, asked["as"])
        recurrence = held_recurrence(state, name, asked["recurrence"])
        if not recurrence.get("paused"):
            refuse(f"recurrence-live -- {recurrence['id']} is not paused: `team pause {name} --recurrence "
                   f"{recurrence['id']}` suspends it.")
        return [{"kind": "recurrence-resumed", "recurrence": recurrence["id"], "by": sender,
                 "since": tick_now().isoformat(timespec="seconds")}]

    made = written(conductor, root, journal, name, judge)[0]
    print(f"pp-team: {name} · recurrence {made['recurrence']} resumed #{made['id']} by {made['by']} -- nothing caught "
          f"up, its next period after {made['since']}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # the recurrence back: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def budget_verb(rest: list[str]) -> int:
    """`team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]`: RAISES the team's bounds
    without a start -- `budget` in dollars, `budget-launches` in launches --, judged under the journal's lock
    before anything is written: each above what the team spent since its last start (`budget-invalid`).
    Then `budget-raised {budget, launches, by}`: the replay takes the new limits and lifts `budget-spent`;
    the members keep their runs. Then the relaunch entry laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    usd = None
    if rest and not rest[0].startswith("--"):
        usd, rest = rest[0], rest[1:]
    retired_flags(rest)
    asked = flags(rest, BUDGET_FLAGS)
    if usd is None and asked["launches"] is None:
        refuse(USAGE)
    try:
        money = None if usd is None else float(usd)
        wakes = None if asked["launches"] is None else int(asked["launches"])
    except ValueError:
        refuse(f"budget-invalid -- `{usd if asked['launches'] is None else asked['launches']}`: dollars are a number, "
               "launches a whole number.")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        if money is not None and not money > state["cost"]:
            refuse(f"budget-invalid -- {name}: {money:g} USD is not above the {state['cost']:g} USD spent since "
                   "the start.")
        launched = launched_since_start(root, state)
        if wakes is not None and not wakes > launched:
            refuse(f"budget-invalid -- {name}: {wakes} launches is not above the {launched} launched since the "
                   "start.")
        return [{"kind": "budget-raised", "by": sender,
                 **({"budget": money} if money is not None else {}), **({"launches": wakes} if wakes is not None else {})}]

    made = written(conductor, root, journal, name, judge)[0]
    said = " · ".join(one for one in (f"budget {made['budget']:g} USD" if "budget" in made else "",
                                      f"budget-launches {made['launches']}" if "launches" in made else "") if one)
    print(f"pp-team: {name} · raised #{made['id']} · {said}")
    state = state_of(journal)
    if any(one["state"] == "open" for one in state["tasks"].values()):
        netted(root, conductor, name, state)       # a task open: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def guard_verb(rest: list[str]) -> int:
    """`pp-team guard` (the vector on stdin): the GUARDIAN of the family `agent-run:<path>/<key>` -- the
    engine's call when `agent purge` asks before removing a run. A run a member of a LIVING team holds (the
    team started, a task open or a ceremony declared, and no `deleting` written) refuses, the team, the member and `team reset` named:
    purged, the member's next wake-up would find no run. Reads only, no lock."""
    if rest:
        refuse(USAGE)
    root, conductor = house()
    prefix, _, ident = conductor.reading.piped().strip().partition(":")
    if prefix != "agent-run":
        refuse(f"family-foreign -- `{prefix}:` is not a family this package guards (agent-run)")
    path, _, key = ident.rpartition("/")
    home = root.parent / TEAMS
    for name in sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []:
        journal = journal_of(root, name)
        if not journal.is_file():
            continue
        state = state_of(journal)
        if state["started"] is None or netless(state) or state.get("deleting"):
            continue
        for member, run in ((member, run) for member, held in state["runs"].items() for run in held.values()):
            if run == key and path_of(state, member) == path:
                refuse(f"member-run -- run {key} of {path} is the run of member {member} of team {name}, "
                       f"which lives: `team reset {name} --member {member}` first, or wait for the team's end")
    return 0


def ring_verb(rest: list[str]) -> int:
    """`team ring <name> <ceremony> [--as <principal>] [--no-tick]`: rings ONE declared ceremony at
    hand, out of its hour -- the tick's ring (`ringing`) under the period `manual-<id>`, the id of its
    own `ceremony-due`, which `by` names the principal of; judged under the journal's lock before
    anything is written, one ring of a ceremony at a time (`ceremony-open`), in season alone (`season-stopped`). Then the relaunch entry
    laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    called, rest = rest[0], rest[1:]
    asked = flags(rest, RING_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        if state["deleting"]:
            refuse(deleting_said(name))
        if state["stopped"]:
            refuse(off_season(name, state))
        sender = principal_of(state, owner, asked["as"])
        declared = state["started"].get("ceremonies") or []
        ceremony = next((one for one in declared if one.get("name") == called), None)
        if ceremony is None:
            refuse(f"ceremony-unknown -- {name} declares no ceremony `{called}`: the ceremonies are "
                   f"{', '.join(str(one.get('name')) for one in declared) or 'none'}.")
        held = [one["id"] for one in state["tasks"].values()
                if one.get("ceremony") == called and one["state"] == "open"]
        if held:
            refuse(f"ceremony-open -- {held[0]} of `{called}` is open: one ring at a time, ring again once it "
                   "is resolved or stopped.")
        first = max((int(one.get("id") or 0) for one in events), default=0) + 1
        return ringing(state, name, ceremony, f"manual-{first}", by=sender)

    made = written(conductor, root, journal, name, judge)
    task = next(one for one in made if one["kind"] == "task")
    print(f"pp-team: {name} · {called} rung at hand · {made[0]['period']} #{made[0]['id']} · task {task['task']} "
          f"to {task['to']}")
    netted(root, conductor, name, state_of(journal))   # a task open: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def same_period(one: dict, other: dict) -> bool:
    """-> whether two periods of a recurrence come back alike: the same dated period, or durations of the same
    seconds (`4h` and `240m`)."""
    if one.get("kind") == "interval" and other.get("kind") == "interval":
        return one.get("seconds") == other.get("seconds")
    return one == other


def recurrence_verb(rest: list[str]) -> int:
    """`team recurrence <name> <R<n>> [--every "<when>"] [--context <n>%|off] [--message <text>] [--description <text>]
    [--as <principal>] [--no-tick]`: CHANGES a live recurrence -- its period, its context limit, its text, its
    description, one of them at least. `recurrence-changed {recurrence, when, since, context, text, description, by}`
    carries what changes alone: `when` and `since` -- the local hour of the change -- for a new period, `context` for a
    new limit (`null` under `off`, the limit taken away), `text` for a new intention, `description` for a new sentence
    of what it does (`description-invalid` past one line of `DESCRIPTION_CHARS`); judged under the journal's lock before anything is written, `message-missing` for an
    empty text, `recurrence-unchanged` when every value asked is in force. The replay replaces what the event carries
    and keeps the periods it sounded: a new hour holds from its next period after the change, a new limit from the next
    first wake-up on an occurrence, a new text from the next occurrence -- an occurrence sounded keeps its own.
    `team recurrence <name> <R<n>> --now [--as <principal>] [--no-tick]`: LAUNCHES one occurrence more of a live
    recurrence, paused or not, now -- a `task` like a period's, from the recurrence's principal to its member, with
    `recurrence`, `now: true` and `by` and WITHOUT `period`, named `<name> YYYY-MM-DD HH:MM` at the local hour of the
    launch, then its `do` --; its planning untouched -- `when`, `since`, the periods sounded, the pause --, the task its
    LAST occurrence, so that a period skips while it is open. Judged under the journal's lock (`team-unknown`,
    `team-not-started`, `season-stopped` off season, `principal-unknown`, `recurrence-unknown`, `recurrence-stopped`,
    `recurrence-open` while its last occurrence is open); `--now` beside another flag of a change, the usage.
    `team recurrence <name> --task <T<n>> --every "<when>" [--context <n>%] [--description <text>] [--as <principal>]
    [--no-tick]`: lays a NEW recurrence on a task that exists -- `recurrence {R<n>, from, to, text, name, when, since,
    context, task, description?}`, its member,
    its text and its name the task's, its principal the one who plays the verb --; the replay makes the task its LAST
    occurrence, so that no period opens one while it is open (`task-unknown`, `task-recurrent` for an occurrence or a
    ring's task; `R<n>` or `--message` beside `--task`, the usage). Then the net laid again, and a tick unless
    `--no-tick`."""
    root, conductor = machine_house()                      # the house's recurrence, whatever instance changes it
    name, rest = named_team(conductor, rest)
    called = None
    if rest and not rest[0].startswith("--"):
        called, rest = rest[0], rest[1:]
    asked = flags(rest, RECURRENCE_FLAGS)
    changing = ("task", "every", "context", "message", "description")
    if asked["now"] and (called is None or any(asked[key] is not None for key in changing)):
        refuse(USAGE)                                 # a launch now is played alone, on a recurrence named
    if called is None and (asked["task"] is None or asked["every"] is None or asked["message"] is not None):
        refuse(USAGE)                                 # a recurrence born of a task: its period owed, its text the task's
    if called is not None and not asked["now"] and (asked["task"] is not None
                               or all(asked[key] is None for key in ("every", "context", "message", "description"))):
        refuse(USAGE)
    if asked["message"] is not None and not asked["message"].strip():
        refuse("message-missing -- a recurrence carries its text: --message <text>, not empty.")
    when = None
    if asked["every"] is not None:
        when = every_of(asked["every"])
    limit = limit_of(asked["context"], off=called is not None) if asked["context"] is not None else None
    description = None if asked["description"] is None else recurrence_description(asked["description"])
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def born(state: dict, sender: str) -> list[dict]:
        task = state["tasks"].get(asked["task"])
        if task is None:
            refuse(f"task-unknown -- no task `{asked['task']}` of {name}: the tasks are "
                   f"{', '.join(state['tasks']) or 'none'}.")
        if task.get("recurrence") or task.get("ceremony"):
            refuse(f"task-recurrent -- {task['id']} is an occurrence of "
                   + (f"{task['recurrence']}" if task.get("recurrence") else f"the ceremony `{task['ceremony']}`")
                   + ": its run has a carrier already.")
        return [{"kind": "recurrence", "recurrence": f"R{len(state['recurrences']) + 1}", "from": sender,
                 "to": task["to"], **({"name": task["name"]} if task.get("name") else {}), "text": task.get("text"),
                 "when": when, "since": tick_now().isoformat(timespec="seconds"), "context": limit, "task": task["id"],
                 **({} if description is None else {"description": description})}]

    def launched(state: dict, sender: str) -> list[dict]:
        recurrence = held_recurrence(state, name, called)  # a suspended one launches, and stays suspended
        before = state["tasks"].get(recurrence.get("last") or "")
        if before is not None and before["state"] == "open":
            refuse(f"recurrence-open -- {before['id']}, the last occurrence of {recurrence['id']}, is still open: a "
                   "member never holds the same work twice.")
        task = next_task(state)
        recurrent, to, text = recurrence.get("from"), recurrence.get("to"), recurrence.get("text")
        return [{"kind": "task", "task": task, "from": recurrent, "to": to,
                 "name": f"{recurrence.get('name') or recurrence['id']} {tick_now().strftime('%Y-%m-%d %H:%M')}",
                 "text": text, "recurrence": recurrence["id"], "now": True, "by": sender},
                {"kind": "post", "task": task, "from": recurrent, "to": to, "verb": "do", "text": text}]

    def judge(state: dict, events: list[dict]) -> list[dict]:
        if state["started"] is None:
            refuse(f"team-not-started -- {name} was never started.")
        sender = principal_of(state, owner, asked["as"])
        if called is None:
            return born(state, sender)
        if asked["now"]:
            if state["stopped"]:
                refuse(off_season(name, state))
            return launched(state, sender)
        recurrence = held_recurrence(state, name, called)  # a suspended one changes, and stays suspended
        changes: dict = {}
        if when is not None and not same_period(recurrence["when"], when):
            changes.update(when=when, since=tick_now().isoformat(timespec="seconds"))
        if asked["context"] is not None and recurrence.get("context") != limit:
            changes["context"] = limit
        if asked["message"] is not None and recurrence.get("text") != asked["message"]:
            changes["text"] = asked["message"]
        if description is not None and recurrence.get("description") != description:
            changes["description"] = description
        if not changes:
            refuse(f"recurrence-unchanged -- {recurrence['id']} comes back every {said_when(recurrence['when'])}, "
                   "its context limit "
                   + (f"{recurrence['context']}%" if recurrence.get("context") is not None else "off")
                   + ", its text and its description as asked already.")
        return [{"kind": "recurrence-changed", "recurrence": recurrence["id"], **changes, "by": sender}]

    made = written(conductor, root, journal, name, judge)[0]
    if made["kind"] == "task":
        print(f"pp-team: {name} · recurrence {made['recurrence']} launched now · {made['task']} to {made['to']} by "
              f"{made['by']} · #{made['id']} -- its planning untouched, no period opens a task while {made['task']} "
              "is open")
    elif made["kind"] == "recurrence":
        print(f"pp-team: {name} · recurrence {made['recurrence']} to {made['to']} from {made['task']} · every "
              f"{said_when(made['when'])}" + (f" · context {made['context']}%" if made["context"] is not None else "")
              + f" · #{made['id']} -- no period opens a task while {made['task']} is open")
    else:
        print(f"pp-team: {name} · recurrence {made['recurrence']}"
              + (f" · every {said_when(made['when'])}" if "when" in made else "")
              + (f" · context {made['context']}%" if made.get("context") is not None
                 else " · context off" if "context" in made else "")
              + (" · text changed" if "text" in made else "")
              + (" · description changed" if "description" in made else "")
              + f" · #{made['id']} -- from its next period" + (" and its next occurrence" if "context" in made else ""))
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # a live recurrence keeps the net
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def main(argv: list[str]) -> int:
    verbs = {"start": start, "post": post, "stop": stop, "tick": tick, "follow": follow, "timer": timer_verb, "status": status,
             "watch": watch, "log": log_verb, "result": result, "responses": responses_verb, "stats": stats_verb,
             "inbox": inbox_verb, "roster": roster_verb, "snapshot": snapshot_verb, "entry": entry_verb, "reset": reset_verb,
             "resume": resume_verb, "pause": pause_verb, "ring": ring_verb, "budget": budget_verb, "guard": guard_verb,
             "recurrence": recurrence_verb,
             "templates": templates_verb, "document": document_verb,
             "declare": declare_verb, "new": new_retired, "declaration": declaration_verb, "delete": delete_verb,
             "rename": rename_verb, "verify": verify_verb, "mount": mount_verb}
    if not argv or argv[0] not in verbs:
        refuse(USAGE)
    return verbs[argv[0]](argv[1:])


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
