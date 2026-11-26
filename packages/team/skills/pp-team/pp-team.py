#!/usr/bin/env python3
"""The house's hand over its teams: a team is DECLARED by its owner at
`<house>/teams/<name>/TEAM.md`, started, posted to, stopped, read -- and ADVANCED by ticks.
Its state is its JOURNAL, read again at every reading. The skill keeps no clock: a tick is
one short process, launched by the end of a wake-up (`--on-end`), by a post, or by the team's
TIMER -- the NET under every other trigger, a process the tick arms and that dies after one tick --,
and after a restart by the team's relaunch entry in the system's scheduler, laid and removed by the skill
on the owner's commands (the engine never writes the scheduler); the wake-ups a tick launches
are the house's own console's (`agent start`). The house is the instance the skill belongs to.

This entry keeps its path -- the console, the timer and the relaunch entry call it here -- and passes `argv` to the
verb it names. The code lives in seventeen DOMAINS, one folder each beside it, in the order below; a folder holds one
module per LAYER it has code for -- `model`, `replay`, `rules`, `faces`, `store`, `acts`, `verbs` --, and the head of
each module says its part. In `model`, `replay`, `rules`, `faces` and `store`, a module imports only its own domain and
the domains before it; `acts` and `verbs` orchestrate, and import the lower layers of any domain:

  house        the values, the paths and the tools every domain stands on
  template     the team templates, listed, read and rendered (`templates`, `document`)
  declaration  `TEAM.md` read, judged and written; its members, roles and preset (`declaration`, `declare`)
  season       a season opened, paused and closed; `SEASON.md` (`start`, `stop`, `pause`)
  documents    the documents a start renders and a member is served (`verify`, `mount`, `entry`)
  task         the tasks, the posts, the debts, the inboxes (`post`, `result`, `inbox`, `resume`)
  rhythm       the ceremonies and the recurrences (`ring`, `recurrence`)
  wake         a member's wake-up, launched, followed and reaped (`follow`, `responses`, `reset`, `guard`)
  budget       the money and the launches spent (`budget`)
  health       the silences, the suspicions, the deadlocks
  net          the team's timer and the house's relaunch entry (`timer`)
  journal      the journal read, folded and written (`log`, `snapshot`)
  tick         one advance of the team (`tick`)
  stats        the costs and the times of the seasons (`stats`)
  watch        a team followed as it moves (`watch`)
  status       the faces of the teams (`status`, `roster`)
  admin        a team deleted or renamed (`delete`, `rename`)

The usage:

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
         `teams/<name>/SEASON.md` read and judged (`documents:`, `documents/acts.py`, `season-invalid`, `document-unknown`,
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
  pp-team tick <name>                 -> ONE advance of the team (`tick/acts.py`); an on-end tick carries `PP_AGENT_RUN`
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
         else the last one; `--season <n>` another; `--all` each season in which a wake-up launched, then
         their median, the seasons without one listed apart. A season runs from one `team start` to the
         next; its number counts the starts from 1. A WAKE-UP is one launch of a member, from its intent
         to its end. For a season: its dates and its state (`running`, `paused`, `stopped`); its tasks
         closed, stopped and open -- a task shows in each season where it is born, woken, closed or
         stopped, and counts there only the wake-ups of that season; closed and stopped count what closed
         or stopped in the season --; its cost and its launches; its delegations (the `do` of its tasks),
         its cost per delegation, per launch and per hour of effort, its root member and its share, its
         tasks stopped and their cost, its budget -- `against` gives some of these measures against the
         median of the seasons --; three times -- ELAPSED, the clock time from its start to its end or to
         now; ACTIVE, the clock time during which at least one wake-up runs; EFFORT, the durations of all
         its wake-ups added up, the failed ones included, more than the active time when several members
         work at once --; its PARALLELISM, effort divided by active time: how many members work at once,
         on average; the effort and the cost in each slot of 2 hours from its start, a wake-up's cost in
         the slot where it ends; the wait before a wake-up launches (median, and p90: the value nine
         wake-ups in ten do not pass); the questions members asked a principal, how many were answered
         and how long they waited, and the same for the questions a principal asked a member
         (`post --ask`, `principal.from_principal` under `--json`); the share of the context a wake-up
         left at its end, and the runs renewed; its launches by model, by band of duration (under 1
         minute, 1-3, 3-10, 10-30, 30 and over) and by band of the context at their end (under 25 %,
         25-50, 50-75, 75-90, 90 and over), each with its launches, its cost and its share, its cost per
         launch and per hour of effort -- a launch whose `wake-launched` names no model, and an end
         without a launch that carries a cost, are said on a line of their own, a wake-up never launched
         and without a cost on no line, one without a measure of context in no band; the shares by model
         add up to 1 where the season's cost is known; a line, a band or a slot whose wake-ups report no
         cost costs 0 there, a line and a band with a share of 0, a slot with no share --; the losses --
         wake-ups failed, their cost and their reasons, silences. The text says a cost, a pace, a median
         and a ratio with two decimals, hours with one; the JSON keeps four, and it says each model and
         each band on its own line. `--cost` chooses the unit every cost is said in: `usd` (by default)
         the dollars the provider reports, `-` when it reports none, never 0; `launches` the launches;
         `tokens` what the wake-ups sent the model, marked `~` (estimated) when a wake-up only gives the
         size of its last call. Under `--json` ONE object `{team, base, season}` (`{team, base, seasons,
         median, empty, by_task, total, task_cost}` under `--all`), each cost in the three units at once
         (`null` where none is known), then one line per task and one per member: cost, launches, `do`
         and `re`, failed wake-ups, the three times, the largest share of context, the cost per hour of
         effort and that cost `against` the median of the seasons, and for a member its models, its cost
         per launch and the median delay from a `do` it received to its `re`; a task's line also gives
         the hours of its first and last event in the season (`first`, `last`). Under `--all`, `by_task`
         gives each task over ALL its seasons, one line per task, made by pp-team: its costs, `do`, `re`,
         failures, active time and effort added up over its seasons, its cost per delegation and per hour
         of effort over them all; its elapsed time the clock time from its first event to its last,
         whatever the seasons between; the largest share of context kept; its name and state its last
         line's. `team-unknown`, `team-not-started`, `season-unknown`, `cost-invalid`; `--season` with
         `--all`: the usage. Read in the HOUSE, whatever instance calls. Nothing written.
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
      -> the teams of the HOUSE -- the machine the skill lives in, whatever instance calls it --, read: one
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
                                         house is the machine the skill lives in. Nothing written.
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
           <key>|all <document> ...     the lines the season ADDS to `TEAM.md`'s (`documents/acts.py`)
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

Any other call says the usage in one line, exit 2.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # the skill's folder: its domains
from house.model import USAGE  # noqa: E402
from house.store import refuse  # noqa: E402
from template.verbs import document_verb, templates_verb  # noqa: E402
from declaration.verbs import declaration_verb, declare_verb, new_retired  # noqa: E402
from season.verbs import pause_verb, start, stop  # noqa: E402
from documents.verbs import entry_verb, mount_verb, verify_verb  # noqa: E402
from task.verbs import inbox_verb, post, result, resume_verb  # noqa: E402
from rhythm.verbs import recurrence_verb, ring_verb  # noqa: E402
from wake.verbs import follow, guard_verb, reset_verb, responses_verb  # noqa: E402
from budget.verbs import budget_verb  # noqa: E402
from net.verbs import timer_verb  # noqa: E402
from journal.verbs import log_verb, snapshot_verb  # noqa: E402
from tick.verbs import tick  # noqa: E402
from stats.verbs import stats_verb  # noqa: E402
from watch.verbs import watch  # noqa: E402
from status.verbs import roster_verb, status  # noqa: E402
from admin.verbs import delete_verb, rename_verb  # noqa: E402


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
