---
name: pp-ui
description: >-
  The post of the house: `ui [<agent> ...]` opens the terminal screen with one conversation tab per agent, then the Agents and Teams tabs; `ui --render <pane> --size WxH` prints a pane and exits; without a terminal `ui` refuses `tty-missing`. A main, not an engine -- it renders what the verbs say and plays nothing itself; the calls are in the body.

---

# `pp-ui` — the post of the house

## The hand, in one breath

The post of the house -- `ui [<agent> ...]` opens the terminal screen on the house's own terminal (`q` closes it), one conversation tab per agent named (`--run <key>` resumes a run of the last one; what follows `--` goes to `agent chat`), then the Agents tab (the agents of the house, the runs of each in an overlay -- resume, new, name, stats) -- no agent named, the conversations kept open last time come back; `ui --render <pane> --size WxH` prints a pane as text and exits; `ui crash [--json]` prints the trace of the post's last crash; without a terminal any other `ui` refuses `tty-missing` in one line. A main, not an engine -- it renders what the verbs say and plays nothing itself.


The post is a terminal screen the house opens on its own terminal. It renders
what the verbs of `pp` say and delegates every gesture to them: it conducts
nothing and reads no file of the instance; it writes its own memory of the
conversations open alone, through the engine's `metadata` face.

## The calls

| call | what happens |
|---|---|
| `./pp ui` | opens the post on the terminal at once, with the conversations its memory kept: each tab shows its run's exchanges as history, read when the tab is first shown, its run's policy, budget, packages and context as the Agents tab read them, and no `agent chat` starts before you send a message, `o`, or what `p` or `k` changes in that tab; `q` closes it, the digits switch the tabs |
| `./pp ui <agent> [<agent> ...] [--run <key>] [-- <flags>]` | opens the post with one conversation TAB per agent named: `agent chat <agent> --json` is held under the post for each; `--run <key>` resumes a standing run of the last agent named; what follows `--` goes to every `agent chat` the post opens -- at the start and from the Agents tab -- as it is (`--harness`, `--permissions`, `--launches`…; the overlay's own flags come after it), and its `--harness` rides `team start` when `S` starts a team, with the `--provider` beside it -- the grammar the command's output is read in, in place of the overlay's provider; the memory is left aside |
| `./pp ui --render <pane> --size WxH` | prints the pane as text at that size and exits -- no terminal needed; `<pane>` is `frame` (the whole screen on its first tab), `dialogue`, `agents`, `teams` or `tasks`; `--size` defaults to `80x24`; `--regions` prints where the menu, the folded line, each band of the centre and each named part of a band stand instead of the text, and each part of the pane that shows a horizontal scroll bar, on a line that starts with `hbar` |
| `./pp ui --render <pane> --press <keys>` | the same, after the keys are pressed in order -- comma-separated, Textual's names (`2`, `3`, `tab`, the letters); `wait:<kind>` in the list pauses until one more event of that kind reached the dialogue, `wait:team:<event>` one more object of the Teams tab's watch; `nodes` notes the widgets of the last block of the agent's words (`nodes <n> …` on a last line); `rows` notes the rows the Tasks tab's band drew of its thread before the thread's history came (`rows <n> …`), `live` the activity of each member of that band (`live <member>=<what it does> …`); `blur` and `focus` make the post lose and take back the terminal's focus and note the widget focused and the post's focus (`focused <id>:<0|1> …`) |
| `./pp ui <agent> --render dialogue --wait <kind>[:<seconds>]` | the capture waits for one more event of that kind (10 seconds by default): `--wait waiting` shows the dialogue after an exchange ended; `--wait team:<event>` an object of the Teams tab's watch |
| `./pp ui crash [--json]` | prints the trace of the post's last crash and exits 0 -- no terminal needed; with nothing kept, one line says so; `--json` prints `{"crash": <trace>}`, `null` when nothing is kept |
| `./pp ui --help` | this usage, in one line |

## The dialogue

The tabs come in the order `1·Dialogue`, `2·Agents`, `3·Teams`, `4·Tasks`. The dialogue tab is a POST
OF CONVERSATIONS: a row of tabs of its own, ONE per conversation; with none open it says
where to open one. The agents named at the start open theirs BEFORE the post draws, on the
loop the post runs on: a refusal of the verb (`agent-unknown`, `run-unknown`, `run-busy`) is
relayed in one line, exit 2, nothing drawn. A tab keeps its own `agent chat --json` and its
own transcript: switching tabs reloads nothing; a conversation of the background goes on,
and what it says that you have not read is counted in bold on its title, until you open it.

A conversation's tab shows the transcript above the message line, in the order the flow
said it: what the principal typed (`▶`, the hour) rendered as markdown, four columns to the right on a light
veil of the theme's accent; per launch, ONE line of
the CONDUCTION -- pp's output served to the agent (`◇`, the launch, the block it serves as the
flow names it, its size) --, what the agent did meanwhile -- ONE line per call of a tool (`⚙`, its name or `pp`
for a call of the agent's console, its title, `✓` and the size of its result, red with `✗` on an error, `…` until the
result comes), ONE line of its thought (`∴`, the last count of tokens or the start of its text), its words (`◀`, the
last ones not twice when the agent's line repeats them), the model's own texts beside its words, each a block of its own under its launch, where the flow said it, rendered as markdown: an ASIDE (`◁`, the hour, the launch), a text the agent wrote before a call, muted, italic and set in by two cells, a note; the LAST MESSAGE of the launch (`⏎`, the hour, the launch, its length), its text plain with a gutter `▎` along it in the theme's secondary colour; the words of a print (`◀`) keep neither. The hand-back mark `...` and a last message of blanks alone make no block; a last message an older flow kept by its length alone is one dim line, `⏎ … · 812 chars · its text was not kept` --, ONE line of its steps counted by kind (bold yellow on a refusal),
ONE line of what the agent answered (`◀`, the launch, its cost, the start of its words); the
answer of the turn rendered as markdown -- tables, code, lists: each markdown text ONE widget, drawn by Rich at its
width and in the colours of the theme, drawn again when either changes, its rows copied without the spaces that pad
them; the verdict of each exchange
(`✓ parked`, `⚠ interrupted`, `✗` and the reason) with its cost and its launches; the end of
the flow (`✗ ended rc <n>` and what the verb said: the tab STAYS, `x` alone closes it). A line
whose overlay has a content to show is LIVE; a line with nothing to show -- a thought of a count
alone, words or a result left blank -- is STALE: drawn in the theme's disabled text, italic, it
takes no focus and opens nothing; a thought turns live when its text comes. A live line
takes the focus (`tab`) and opens WHOLE in an overlay on `enter` or a click -- its title on ONE line,
the kind of the line in bold (`conduction`, `steps`, `tool call · <name>`, `tool result`, `thinking`, `words`,
`agent answer`, read from the flow's `kind`) then its summary cut at the width; the content folded to the
width, scrolled, built when it opens -- a call shows its input as indented JSON, then its result;
`escape` comes back. `c` hides the lines of conduction, of steps and of thought, `b` the lines of the calls of
tools and of their results, `w` the asides and the last messages together, each showing its own again (`[c] conduction: shown`, `[b] calls: shown`, `[w] model: shown` in the footer). Every block is selectable with the mouse: `ctrl+a` selects
the whole transcript (in an overlay, its content), `ctrl+c` copies the selection (the status
says `copied <n> chars`); in a field that has the focus -- the message line, the text of a gesture --
`ctrl+a` selects ITS text and `ctrl+c` copies its selection, and `ctrl+x`, `ctrl+v`, `ctrl+z` are the field's own.
While a turn runs, a spinner turns on the tab's title and in the TURN ZONE of the message line -- between the alert
and the box, on a marked background of the theme's accent, bold and followed by how long the turn has run; the zone
keeps its place, empty, at rest --; the activity zone of the status row says the faces being read alone; the message line --
one row at rest, growing to 8, `enter` goes to the line, `ctrl+enter` sends (most terminals send it as `ctrl+j`,
which sends too) -- stays open -- what is typed there is kept, dim -- and `ctrl+enter`
waits: it sends nothing until the turn ended (`ctrl+enter: waits` in the footer); once it ended, `ctrl+enter` sends
the line. `s` stacks the statistics of the conversation's run (`agent stats --json`). `u` reads the tab's past again -- its
kept flow (`agent flow --json`), else its exchanges -- and shows it all at once, as it was lived; while a turn
runs, `u` reloads nothing and the remedy line says why. While a turn runs, a
`■ stop` button stands right of the message line and the footer says `[ctrl+g] stop the turn`: the button
(a click, or `tab` to it then `enter`) or `ctrl+g` sends `stop` during an exchange; at rest the button is hidden, its
place kept.
`escape` never stops a turn: it leaves the message line, during a turn as at rest, so that the letters
act; `i` alone goes to it -- no line takes the focus by itself, at the opening of a conversation, a switch of
tabs or the end of a turn; `p` opens the run's parameters, its NAME the last field (`agent name` keeps
it at once, or at `opened` for a run that opens, the tab follows); `x` closes the tab (`quit` to its verb: the run stands; 5 seconds later the verb's whole process group is ended, `pp-agent` and its wake lock with it); ONE run, ONE tab: taking up a run a LIVE tab holds -- from the Agents tab, or named twice at the start -- activates that tab and launches nothing; a run whose tab ENDED is taken up IN PLACE -- the same tab, its transcript kept (the memory of a turn's lines is the tab's), a new `agent chat --run` under it, the history not read again --; a new run (`n`) always opens its own tab; `o` suspends the conduction of the conversation or brings it back (`conduct` to the verb:
`⏸` on the title, `pp off` on the status, `[o] pp: off` in the footer, `⏸ pp OFF` in the alert zone left of the message
line and the message line bordered in the warning colour; under `pp off` a message is a
bare exchange, verdict `✓ unconducted`, no line of conduction); `k` opens the run's packages as the flow said
them, an editor: `space`, `enter` or a click toggles a line, the overlay kept and nothing sent; `ctrl+enter` alone sends one
`package` per line changed; `escape` nothing, asked first once a line is toggled; a switch the verb holds waits (`⧗` on the title, `packages: … …` on the status, `… pending`
at `k`) until it plays; a refusal goes to the remedy with its detail (no list in the flow, the remedy says so); the ROW OF THE SPACES stands just
above the message line when the flow says the run has a space (`spaces {open, openable}` of `ready`, of each `block`
step and of each `space`; `root` of each `block` step; nothing read in a text): the root of the passage (`root TURN`)
while no space is open, else the stack open from the outermost to the deepest -- `×` on the deepest, which a click
closes; a click on an outer one sends one `close` per space it stands under, each once the one before answered --,
then one `+ NAME` button per element of the offer, its name as the flow says it -- the row folds onto as many lines
as its buttons need, no space hidden --; a click sends `open`/`close` with the bare name to the verb -- an `open` with
the message typed, if any, the line emptied; the line empty, the space opens and plays without a message --, the status says `space: open PLANS …` until the flow answers `space` (`✓ PLANS open` on the transcript),
a refusal (`space-open`, `offer-absent`, `space-none`) goes to the remedy with its detail; the row is hidden while the run has no space, absent from a run read,
greyed while a turn runs or a command waits;
`ctrl+right`
and `ctrl+left` go to the neighbouring conversation; `n` goes to the Agents tab; `q` closes
every conversation (`quit` to each) and the post. What the house says (`refused`, the end
of a flow) goes to the remedy line, prefixed by the agent; the active conversation's run
and state go to the status line -- from the tab's opening, before any message: the flow says its run
first (`ready`), so the status line says provider · model · budget · effort, `k` lists the packages and
`p` opens on the run's policy at once; the budget is the run's own once the flow says it (`budget
{cap, spent, left}`): `budget 0.42/2.00 USD` and a bar of ten cells, green, yellow past 80 %, bold red
at the cap, `—` without a cap. Above the transcript, the bubble says the principal's message of the turn at
the top of the view (`history #n` for a turn of history), the last turn at the end, rewritten only when that
turn changes. The message line is a row of ZONES of fixed width, each as wide as the widest thing it says and kept
even empty, so that nothing that comes or goes moves its neighbours: the gauge, the alert, the message, the stop
button. The gauge says the run's context as `agent stats --json` says it --
`ctx ▰▰▱▱▱▱▱▱▱▱ 17% · pp 33%`, pp's share in the accent, `ctx —` without a context; under 70 columns without pp's
share --, read after each verdict and when a run is taken up. A cap the engine raised (`ready.cap`, `opened.cap`, `applied` above `set`)
is said there too, `<agent>: cap <set> lifted to <applied> for this run`, while the run rests.
Every overlay keeps its line of keys in sight: its body scrolls inside the box, the focused field
scrolled into view; the post shows no tooltip. An overlay renders what the agent wrote -- its answer
at a launch, its words -- as markdown, any other content as the text it is. `U+FE0F` is taken out of what the post renders as
markdown, of the lines' summaries and of an overlay's content, so that a table's columns stay
aligned on the terminal; an overlay copies what it shows.

## The agents

The Agents tab is the table of the agents of the house -- the house itself first (`.`, named by its folder
and `(house)`, a run of its own instance), when `agent list --json` says it --, read from `agent list --json` and
`agent status --json` -- agent, runs, running, the state of its last run, cost, launches, its weight (what a purge of its runs would remove,
`1.2 MB`), the moment of its last event (its hour today, `DD/MM HH:MM` another day, the year when it differs) --, read at
the start, on `u`, after every verdict a conversation receives, after a team born or deleted from the post, and by a ROUND
while the tab is shown -- `agent list --json` every 20 times what the list cost, 5 seconds at least: a list equal to the
catalogue reads nothing, an agent more, less or whose runs changed is read again alone, the teams with it --; the statuses
four at a time, each line filled as its face arrives; a face whose verb did not finish within
its bound (30 seconds, `PP_UI_TIMEOUT` when it names another) is said on the remedy line, `verb-timeout`, and the
agent keeps the line of the last reading, `—` without one; the status says the count and the hour of the reading. On an agent: `n`
opens a new conversation with it; `enter` opens the OVERLAY of its runs -- its table
bounded to the screen and scrolling, its keys the last row of the box --, where `ctrl+enter` (or `enter`, its alias)
resumes the run under the cursor in a tab of the dialogue -- a run a member of a team holds, marked in its `team` column with the name of that team as its face says it, the
member not named (ui 1.10.24; from `team status <name> --json`: the started teams read while
the tab is shown, once at its first showing; the table itself names no team -- an agent may be a member of several),
opens READ instead; a run opened under a root of documents (`documents` of `agent status --json`) is marked `◈ <team>` in
that column -- `◈` then the name of the root's folder, which is the team's (`pp-team` keeps a team in `teams/<name>`);
the post keeps no cache of it --, and so is its tab in the dialogue, from the `documents` its `ready` and `opened` say back; a run without a root
bears nothing, and the Dialogue's own way, the Agents tab, opens every run without one -- (its history, `agent exchanges
--json`, replayed dim first and dated the same way, then the live flow), `n` opens a new conversation, `s`
stacks its statistics (`agent stats --json`: the sums, then the conduction's detail, the time in `h min s`),
`P` purges the run under the cursor and `B` the agent's runs before a date, `u` reads again, `escape` closes.
Each run says its `weight`. A purge is asked before it plays: `agent purge` WITHOUT `--yes` says what it would
remove, shown, and the `--yes` verb plays only once the run's key -- or the date -- is typed as it
is; `workdir-unpushed` brings the purge asked again with `--force`, typed a second time; every refusal of the verb
(`run-busy`, `run-held`, `run-unconducted`, `call-busy`, `purge-invalid`, `run-unknown`) goes to the remedy line as
it said it, and the runs removed leave the post's memory. The post types nothing outside a conversation's message line: the name
of a run is asked in the overlay of its parameters, with its help under it.

## The teams

Two tabs show the teams of the house as `team status --json` says them, each read from the first time
it is shown, each a MENU on the left and a CENTRE of horizontal bands, never two parts side by side -- but the
head of the Teams tab and the summary of its season (below); the menus of the two tabs have one width, given by one
rule of the post (`.menu`: 32 cells, at most 45 % of the screen);
under 70 columns the menu folds into one line, which `[` `]` (and `{` `}`) change. The TEAMS tab: the
menu of the teams (each name in the look of its state -- working, waiting, paused with `⏸`, idle, never --, then,
dim, the number of the season under way, `s3`, as `season {n, state}` of the face's line says it -- none for a
season stopped or a team never started (ui 1.10.19) --, the wake-ups under way, the questions to the owner, the tasks done not seen; `-` for a team never started); the
HEAD of the team chosen (its owner and mandators, its state -- `waiting · owner, budget`, `paused since … by …` --,
its budget `spent/cap · reserved · left`, its launches
against their bound, its net, what waits for the owner counted on one line), then its MEMBERS (the agent that plays the member -- a member the house plays shows the Agents tab's word for the house, never `.` --,
the `season` its next wake-up gets -- its model and its effort, `sonnet·high`, from `members[].launch` --, the run,
`ctx` -- the context of that run: while its wake-up runs, the last one the team's watch measured, in cyan; at rest, the
one its last wake-up left, `members[].context` (team 0.54.0); `17%` of the window, else `34k` tokens, `—` without --, how
it stands, its tasks, the debts it owes -- `owes`, bold yellow once one was reminded --, `live`; a
member the face says suspected in bold red, `try HH:MM` the hour of its next try; a member its provider's usage limit stopped (`members[].quota`, team 1.25.0) in the same bold red, its state `quota`, `live` `until HH:MM` the hour the provider gave, or `until resume` when it gave none -- the house lifts it by `team resume --task`; `d` says the quota: until when, and the provider's words). The frame of the head carries in its title the team, its season and that season's state
(`pp-workers ── season 13 · running`; the team alone when it was never started). From 130 columns on, the SUMMARY of
that season stands at the right of the head, titled `season stats`, as `team stats --json` says it -- its tasks, its
cost and its cost per closed task, its three times and their parallelism, the peak and the median of its context, its
losses; the post computes no number. Under 130 columns the summary is hidden, and what its title offers with it. In
its title, the unit every cost is said in -- `USD`, `launches` or `tokens`, chosen in the SETTINGS (`O`) --, and `⊞`
opens the DASHBOARD of the team's seasons: it takes the whole centre, beside the
menu of the teams, which stays shown and played -- another team chosen there shows its dashboard. Its title carries
the same unit, then `[s.<n>] … [all]`, the seasons latest first: `[s.<n>]` draws that season
in ZONES, each framed and titled, set apart from the others, two by two from 100 columns -- its yield against the
median of the seasons, the cost of a task, where the cost goes, the time, the principal in the loop, the context, the
losses; a zone whose block the face does not give is not shown --, the summary's season while none is chosen; `[all]`
two zones, one row per season not empty with the empty ones named under them, then one sparkline per measure from
season to season. `⊟` or `escape` closes it. `⊞` and `⊟` light up under the mouse, as the glyphs of the Tasks tab do. `[s.<n>]` and `[all]` are clicked with the mouse. Under the members, the TASKS of the
member under the cursor in a band three lines high whatever their number: its head (`tasks of reviewer · 100 · 3
open`), as many tasks as the width holds in the order of their birth, the oldest on the left, each its id and the look
of its state -- the spinner while a wake-up plays it --, those hidden on each side counted (`‹ 38` … `51 ›`), then the
task under its cursor: its id and name, who gave it, when it was born; the cursor starts on the task that member's
cursor last stood on while the tab lives, else on the newest open task, else on the newest. A reading of the team
changes the cells of the menu and of the members in place while their lines stay the same: the member under the
cursor, the task of its band and its sequence stay where they are. Under the band, the SEQUENCE of that task as the Tasks tab draws it, centred on the member: its column
first, `║`, then those it exchanged with in the task alone, the rows it sends, receives or wakes in alone. Its title ends on `⊞`, lit under the mouse: a click on it expands the sequence over the whole centre, the menu of the teams kept beside it, and turns the glyph to `⊟`; a second click on it, or `escape`, folds it back, and so does opening the dashboard. `tab` goes
from the members to the band -- `left` `right` a task, `<` `>` a page, `j` the next open task, `home` `end` --, then to
the sequence; `escape` comes back to the members. The team's ONE `team watch <name> --json` -- at most one per team, shared by
the two tabs, a thread and a read tab, never one per task -- follows the team chosen and reads it again at each
object but `quiet`; choosing another team leaves it, ended when nothing else follows it; leaving the post ends
every watch whole; `u` reads again. The TASKS tab: the filters `SHOW` (`recent` first -- the open tasks and those the face says ended
within the last 24 hours --, `running`, `for you`, `stopped`, `resolved`, `recurring` -- the live recurrences of the
face's `recurrences`, the nearest `next_due` first, in the columns of a recurrence and its team -- a recurrence of a
team out of season in italic, the whole line, `off season` in place of its next period: it opens no task until the
next season (ui 1.10.23) --, the band saying the one
under the cursor whole, a recurrence laid from the tab followed there --, `all` -- every task --, each with
its count) and `TEAM`; the tasks of every team started they keep, the most recently born first, the teams mingled (the id -- `T6 ↻` for an
occurrence of a recurrence, as the face's `tasks[].recurrence` says it --, the name,
else the start of the text, in 25 cells at most, `…` last when it is longer (`TASK_CELL`, the spinner counted within
them); the team, the state, the holders, in 25 cells at most the same way, the moment the task was born as the face's
`at` says it -- its hour today, `DD/MM HH:MM` another day --, then the task's numbers over all its seasons, each read
from its line of `team stats --all --json` (`by_task`), none computed by the post: `elapsed` -- the clock time from its first
event to its last -- and `effort` (`42 s`, `12 min`, `1h02`, `2d 3h`), its cost in the unit chosen in the settings (`O`) -- the column titled `USD`, `cost`
(for the launches) or `tok`, `~` before tokens estimated --, `lnch` its launches, `do` and `re`, `fail` its failed wake-ups, `ctx` the
largest share of the context its wake-ups left; a cell stays empty where the stats say no number; every freshness of the two tabs is an age against the post's one
clock, the hour of its reading on the status line: `12 s`, `3 min`, `2 h`, `3 d`), read by one `status <name> --json` per team started and
again at each object of a team's watch but a step and `quiet` -- a task a wake-up plays (`running`) with the spinner
before its name, the tab's title counting them (`4·Tasks ⠹ 2`), then, in the theme's alert colour, the asks to
the owner still waiting for an answer in every team started (`4·Tasks ⚑ 1`, ui 1.10.22) --; then the task under the cursor whole and, under it,
ONE of two. Its SEQUENCE: one column per participant -- the principal who gave the task, then each member in the order
it appears --, beside each member's name the context of its run (`ctx 17%`, as the last `context` object of the team's
watch said it), under it its role keys between brackets (`[workers, reviewers]`, the member's `roles` at the team's face, team 1.35.16; `[principal]` for the team's owner, each of its principals and the team itself -- the first column of a task its ceremony opened; nothing for a member without a key; the head has five lines, four when no column has a part -- no role key, no principal), under them in blue the pile of procs its wake-up under way plays on the task (the last step the
team's watch said) and in cyan what it does now (`⚙ Read · pp.py` a call of a tool, `⚙ Read ✓ 1.2k chars` its
result, `∴ …` a thought, `◀ …` its words -- the `activity` objects of the watch, team 0.50.0; `+3` when the watch
folded more into one), each tied to its member and its task by the face's own `agent` and `task`; none once that
wake-up ended -- this head stays in sight while the rows scroll, and follows them sideways --; under the head, each
ask of a member to you that waits for your answer (the face's `waiting.questions`) stays PINNED, one line each under
`⚑` in magenta, whatever the scroll -- three lines at most: beyond, the first two and a line that counts the others,
`⚑ 2 more asks waiting for you -- [b] the inbox lists them all` --, its row in the body marked `⚑` in the same colour, and the summary of
the task counts them (`questions 2 waiting for you`); answered, or its task closed, an ask is no longer pinned nor
counted and its row takes its usual colour; then one row per post (`do`, `ask`, `re` citing the message it answers, `stop`) drawn as an arrow from its
sender to its receiver with its text on the right, the time elapsed since the task was born beside its head (`42s`,
`4m30`, `1h05`, `2d3h`, as the journal dates them; nothing for a row without a date), a notice of the team dashed, a wake-up `⚡` with its run and its
cost, `◆` a wait met, `■` a stop, `✓` an end; the thread read by `team log --json --task` once the cursor has rested
0.3 s on the task -- what the watch said of it meanwhile drawn before the history returns --, then fed by the team's watch -- an end of a wake-up said without a task reads it again --, the row
under its own cursor said below it. Or, for a task resolved that no wake-up plays, its RESULT (`team result <name>
<task>`, read once and kept, drawn as markdown -- a text as it is, any other value its JSON in a block of code), whole,
in a frame that scrolls; never both. `tab` goes from the tasks to that band, then to the filters: in the sequence `up`
`down` (`home` `end`) move its cursor, `left` `right` slide its rows and its head, `enter` opens the row's text whole in an overlay,
rendered as markdown -- a click on a row puts the cursor on it, and on its text opens the same overlay --, `w` leaves the wake-ups out or
brings them back; in the result `up` `down` `pageup` `pagedown` scroll it; `escape` comes back to the tasks; the footer
says the keys of where the focus stands. Members gains `live`: a member's last step and what it does now (the
frame of its block, then `⚙ Read · pp.py`, `∴ …`, `◀ …`), or `since` while it runs. `enter` opens the task's THREAD in an
overlay, live: its history by `team log --json --task`, then what the team's watch says that names the task, an
`id` shown once, an end of a wake-up reading the history again; `escape` closes it. Both tabs PILOT by the verbs of `team` alone, no command
ever shown, its refusal on the remedy line as the verb said it, what it did said in words on the status line. A
gesture that asks more than a yes is WRITTEN in an overlay, `GestureScreen`: its fields, each with its help, `ctrl+enter`
from any field playing the verb they make -- in a text `enter` goes to the line, in a line it goes to the next field --; a field left as it opened composes no flag (`to` on the holders, `as` on
the owner, an empty name). The forms of `n`, `m` and `r` on TASKS play their verb without closing: once the verb
accepts, the form closes; when it refuses, the form stays open, each field as you typed it, and the refusal -- its code
and its phrase -- is said under the fields until the next `ctrl+enter`; while the verb plays, `ctrl+enter` and `escape` do
nothing. On TASKS: `m` writes on the task under the cursor (`kind` -- `info`, read at the next
wake-up and waiting for no answer, or `ask`, a question the member answers --, `to` -- the root at the opening,
left blank the holders --, `as`, `reply to` read from `team status --json`, then the text), `s` stops the task, `r` resumes it (`to` -- who is told: the root at the opening, a member, or `all` --,
a message, `as`), `k` kills its
wake-ups once its name is typed, `v` changes its result for its sequence and back (on a task still open, `task-open`
on the remedy line), `b` the owner's inbox of the task's team -- of the `TEAM` filter's when no task is under the
cursor --, as the Teams tab shows it, the footer counting its messages beside the key (`[b] inbox (2)`, see below), `n` a new task (its team,
its name, `to`, `as`, its message, then `every` -- left empty the task is given once; typed, `--every` as typed, the
period `team` reads, `day|weekday|mon..sun HH:MM` or a duration `30m`, `4h`, `1d`, a refusal `every-invalid` on the
remedy line --, then `context`, the context limit of the recurrence, passed as typed in `--context` with a period
only) -- FOLLOWED: the next reading puts the cursor on the
task its team says that it did not say before, `SHOW` turned to `recent` when the filter in place hides it --, `l` the
journal, `e` the RECURRENCES of the task's team -- of the `TEAM` filter's when no task is under the cursor -- in an
overlay, as the face's `recurrences` says them (one line each: its id, its period, its name or the start of its text,
its member, its last occurrence, its next period, `stopped` or `paused`, or `off season` in italic, the whole line,
while the team is out of season; none said), where `x` stops the line under the cursor
once its id is typed (`team stop <name> --recurrence <R>`), `m` changes its period, its text and its context limit in a
gesture prefilled from the face -- the verb carries the fields changed alone (`team recurrence <name> <R> [--every
<period>] [--message <text>] [--context <n>%|off]`, `off` for a limit emptied; nothing changed, nothing plays) --,
`space` pauses it -- or resumes it when the face says it paused -- in a gesture of its `as` alone, prefilled with the
owner (`team pause <name> --recurrence <R>`, `team resume <name> --recurrence <R>`, ui 1.3.8), `l` opens one
occurrence more now, without a confirmation, its schedule unchanged (`team recurrence <name> <R> --now`, ui 1.4.25), and
`p` makes a task given once come back, chosen among those no recurrence and no meeting opened (`team recurrence <name>
--task <T> --every <period> [--context <n>%]`); a period by a duration is said as
team writes it, `4h`. On TEAMS: `N`, `E` and `S` open the FORM of a values file (`ValuesForm`, ui 1.6.0) -- `N` and `E` TEAM.md, `S`
SEASON.md --, one box of one size whatever it shows: on top the bar of its SECTIONS (`ctrl+pagedown`, `ctrl+pageup`, or a
click on a title; `tab` goes from field to field, and on to the next section), on the left the fields of the section
shown, each with its help under it and, while empty, an example in its place, on the right the SIDE PANE, as tall as
the fields; at the bottom the line of state and the line of keys. In a text field of several lines, `enter` goes to
the line and `tab` leaves the field, and the line of keys names `enter` `new line` there (`palette.FORM_TEXT_ENTER`,
ui 1.10.12); in a field of one line, `enter` goes to the next field; a list unrolled keeps `enter` to choose; `ctrl+enter`
writes the form from any field (ui 1.10.41). The side pane changes with the
section and shows one of four things (ui 1.10.0):
the FILE as `team declare` will write it, rendered as markdown as `e` renders a declaration (its keys in a block of
code, then its body); what each MEMBER reads; the DOCUMENT chosen in the list (see below); or the WORD typed, rendered
as markdown. The file, the view and the word are made anew at each change. The form of TEAM.md has the sections Team
(its name for a new team, its description, its roles, `<key> <member> ...` per line; pane: the file), Preset (below; pane: the file),
Members (`<name> <path>` per line: the path is any path under the house, or `.` for the house itself; then the root, the principals, `<member> ... -> <member>` per line; pane: what each member
reads), Documents (the list below; pane: the document), Limits (the budget, the launches, the parallel -- how many
members may work at the same time, a whole number of 1 or more (ui 1.10.6) --, the timeout and the schedule -- a team to be born opens on `30s`, which `ctrl+enter` writes as a value typed
(`team declare --schedule 30s`, ui 1.10.20); a team that stands shows the schedule its TEAM.md says; pane: the
file) and Owner's word (the body of TEAM.md,
its field as tall as the left half of the form; pane: the word); the form of SEASON.md has Preset (below; pane: the file), Documents (the
list below; pane: the document), Launch (`work:` shown, not changed; the budget, the launches and the silence of the
season; pane: the file -- the silence is a whole number: how many exchanges a member may end without a word on a task
it owes before it is reminded once; its help says where the value comes from, SEASON.md, TEAM.md or the team's default,
and what TEAM.md says (ui 1.10.10)), Members (the table of the members: `all`, then one row per member -- the agent `.` shown by the Agents tab's word for the house --, each edited
in its `ProfileScreen`, a member's field left empty taking `all`'s, a package `required` greyed; under it the context of the
season, in percent, 90 when SEASON.md gives none and the season is not running; pane: what each member reads) and
Season's word (the body of SEASON.md, its field as tall as the left half of the form; pane: the word). In both forms, PRESET shows the
preset the file names (`template:`) -- a team preset for TEAM.md, a season preset for SEASON.md -- and under it one
field for each value that preset asks, its description under it, its default as an example; a value typed there is
written to `values:` by its name. A value that only a document asks is typed under Documents, beside the document; a
value that the preset and a document both ask has a field in both places, and both write the same line of `values:`. Choosing another
preset makes the fields again: a value both presets ask keeps what was typed, and a value typed for the old preset
that neither the new one nor a document of the list asks is taken out of `values:`; a value that the file already
held goes back to what the file says, and `team declare` judges it. With no preset chosen, or a preset that asks for no value, one line says so and no field
shows. `values:` itself is no longer a field of the form. The season's form opens no task: `ctrl+s` starts the season
without one, and a task is posted with `n` (ui 1.8.0).
In both forms, Documents is a LIST of every document `team templates --json` says (ui 1.9.0): the house's first,
then the product's under the line `product · read only`. Beside each document stand the role keys it is given to,
`—` when it is given to nobody. `enter` opens the roles as checks -- `all` and the team's role keys (for TEAM.md the keys typed
under roles on Team, for SEASON.md the keys of TEAM.md) --: `space`, `enter` or a click ticks or unticks one, the overlay kept; `ctrl+enter` alone keeps them (`escape`, asked
first once one is changed, keeps nothing), and each key
ticked is one line of `documents:`, nothing ticked takes the document out. The list rewrites the lines of
`documents:` that `ctrl+enter` on the form then writes. It shows and writes ONE line per key: for a key written on two
lines, it shows the documents of both and writes them on one line, but `team declare --document` replaces the first
line of the key only, so the second line stays in the file; a key written twice that no tick changes plays nothing.
A line the list does
not show -- a file of the team's directory, a name `team templates` does not say -- stays as it is written, shown in
a last group `kept as written`. On Documents, the side pane follows the document under the cursor (a click chooses one too): on
top, one field per value it asks, filled from `values:` and written there by `ctrl+enter` on the form, a value shared by
name between documents; under it, its text rendered as markdown by `team templates --render`, from the opening of the
tab, a value not given yet left as `{name}`. When the team exists, the text is rendered on the form's file as it is
typed, not yet written (`--team <team> [--season] --text-file -`): a value cleared in the form is gone from the text,
and a value the other file still gives stays there -- on the form of TEAM.md, a value SEASON.md gives, since it wins.
Before the team exists, each value typed is given with `--value`. `n` asks the name of a new document of the house, `<directory>/<name>`,
creates it from a skeleton (`team document --new`) and opens its source; `e` opens the source of a house's document in
the pane, and `e` again, back on the list, saves it (`team document --body-file -`), `escape` throws it away; `d`
deletes a house's document once its name is typed (`team document --delete`) -- refused on the line of state while
a role of the form holds it, or while a `TEAM.md`, a `SEASON.md` or a preset of the house names it (`document-used`,
each one said). A document of the product is read only:
no `e`, no `d`, but it can be given to a role. In the form of SEASON.md the list shows the season's documents alone,
never the team's, and the lines its season preset gives are shown locked, `= <key>`, under the line `given by the
preset <preset>`: no key changes them. A key the preset gives, ticked on another document, writes the preset's whole
line for that key with it; after each gesture on the list, a line of `documents:` whose documents are exactly the
preset's whole line for its key (order aside) is taken out, so SEASON.md never copies the preset -- a line that gives
fewer documents than the preset's, or more, stays.
Both open on the file as the `text` of `team declaration --json` says it, never read on disk; `N`
opens on the first team preset and its members' names, `E` on the team chosen, `S` on its season. `ctrl+enter` plays `team
declare --json` (`--season` for SEASON.md) for the keys and the lines changed alone, the body given on the verb's input
(`--body-file -`) -- a change the verb cannot write (the preset, a principal, the root, a limit, the schedule or the
description emptied) is said on the line of state and nothing plays, and `N` on the name of a team that stands plays
nothing: `E` changes it --. In the form of SEASON.md, `ctrl+enter` also writes the limits and the members' lines changed
(`team declare --season`, with the same flags as `team start`: `all`'s keys, each package whose state changed, each
member's changes after its `--member`); `ctrl+s` writes them the same way, with the context at the form's default when
SEASON.md gives none and the post's harness, then plays `team start` without a flag, which opens the season just
written (ui 1.10.8). The form of TEAM.md starts nothing. Under `ctrl+enter`, a form left as it is writes nothing; in the
form of SEASON.md, `ctrl+s` on a form left as it is still writes the form's default context when SEASON.md gives none,
and the post's harness, then starts the season. During a season both forms are READ ONLY: the line of
state says to stop the season first,
and in the form of SEASON.md `X` stops it (the same confirmation as `X` on the tab): once `team stop` played, the
form closes and the form of SEASON.md opens again in its place, read anew and no longer read only, off season; a stop
refused keeps the form open and read only, its refusal written on the form's line of state, and on the remedy
line too (ui 1.10.21). A refused `declare`, a `declare` that
writes while its `verdict` says the next start refuses -- no `start` played --, or a `start` refused after a file written
opens the form again on its values -- on the team that stands once TEAM.md is written --, the line of state saying the
refusal and the files written; a team whose declaration cannot be read opens no form: its refusal goes to the remedy
line; the post writes no file), `n` a new task, `T` ticks, `s` shows the SEASON of the team READ ONLY (its lines
`all` and one per member from `team status --json` alone -- `launch`, `members[].launch`, their sets of packages --, the
column of the packages saying the packages on of `all`'s set and what a member changes of it, the fields closed, `season
n · started <at>` under the fields, no `ctrl+s`, `X` stops the season -- once played, this view gives way to the form of SEASON.md, off season, as
above --, `enter` on a line its profile closed, its packages each with its state
as its face says them; `no season` on the remedy line for a team never started),
`B` raises its budget (`team budget`, prefilled
from the face, a field changed alone played), `b` shows the owner's inbox (`team inbox --json`: the questions first, then the team's notices -- those that wait for
your answer first --, then the infos -- a member's or the team's word that asks nothing, `(was a note)` for a note of
before, `(closed)` for an ask whose task is resolved or stopped, which takes no reply --, the tasks done, the posts
returned; within each group the latest first; each row says when its message was written, after its head, as the
`at` of `team inbox --json` gives it (its hour today, `DD/MM HH:MM` another day, the year when it differs; nothing without `at`; ui
1.10.18)
-- in a box
as large as an event's, the one under the cursor whole in a pane of fixed height under the title, scrolled by its bar,
then each message on one row cut by `…`; a click on a row shows it and opens nothing; `enter` on a question replies on
its task in an overlay over the inbox, with `--reply` even when the face does not hold the question yet -- sent or
`escape`, the inbox back on top, read again once sent; a reply `team` refuses (`task-closed`, …) is said under the
list, and that line empties when the cursor moves or the inbox is read again; `enter` on a row that is not a question
nor a notice waiting for your answer says it takes no reply --, `x`
marks the one message under the cursor read (`team inbox --seen --id`; the overlay stays, its row leaves; a refusal
of `team` -- `inbox-question` on a question -- is said under the list like a refused reply, and the row stays; ui
1.10.17), `a` marks it all read (`team inbox --seen`) and
closes; in the footer, `b` counts the messages of the inbox it opens -- the team chosen here, the team at hand on
the Tasks tab -- in the theme's warning colour, `[b] inbox (2)`, and the count follows each reading of the team: an
`x` lowers it (ui 1.10.22)), `e` its declaration (`team declaration --json`, read only), rendered as markdown: a title, a table of the
verdict, the start and the keys a start would change, then TEAM.md -- its front matter in a code block, its body as
markdown (ui 1.8.0),
`X` stops the SEASON once the team's name is typed (`team stop <name>`): first it names what stops -- each open task, who holds it, each recurring task silent until the next start, which makes up nothing it missed --; then nobody is woken until the next `team start`, and TEAM.md and SEASON.md can be written; `D` deletes the team chosen -- what `team
delete <name> --json` would remove shown (its folder, its journal, its calendar line and timer, its runs), then the
agents the face says the team alone declares as a list of CHECKS, none checked: `space` checks one and the verb
gains its `--agent <path>` (the agent leaves with the team, by `agent remove`), `tab` goes to the line; the `--yes`
verb played once the team's directory is typed; a refusal, `team-busy`, on the remedy line --, `r`
renames the team chosen (one field, the new name; `ctrl+enter` plays `team rename <team> <new>`; the teams read again, the team renamed chosen), `P` pauses the team or resumes it, `l` the journal; on the member under the cursor, `R` resets its run once its name is typed, `d` shows
it whole, `a` its responses (`team responses --json --agent`), and `enter` or `i` opens its run READ in a tab of
the dialogue -- titled `<team>/<member>`, a `◉ read only` banner, no message line, no `agent chat` launched:
its kept flow (`agent flow --json`) replayed as lived turns -- conduction, calls, thought, answer --, then its
wake-ups live from its team's watch, of which the tab keeps the objects of that member AND that run, the exchange
a step names read again; a run without a kept flow replayed from its exchanges (`agent exchanges --json`) --; a member without a run says so on the
remedy line. `C` on a member opens a CONVERSATION with its agent under the root of the team -- the folder of the `path`
`team declaration <team> --json` says, resolved from the house; the post composes no path of a team --: `agent chat
<member's path> --json --documents <root> [--vector <vector>]` (the flags of `--` before it; `--vector` when the
member's row in `team status --json` names one, `members[].vector`, passed as the face gives it -- the post composes
no vector), the dialogue of any run in a tab of its own -- a new run, the operator's, no act of the team --; `i` and `enter` keep reading the member's run. `c` opens the CEREMONIES of the team in an overlay: their table (the progress of the last ring,
counted on the face's `progress`; the next ring as `team` computed it), the detail of the one under the cursor
(its chain `after`/`then`, the participants still waited for, the wait of the task of its last ring), the `as`
of a ring and its command; `g` there rings the ceremony at hand (`team ring`), `ctrl+enter` (or `enter`, its alias) leads to the task of its
last ring on the Tasks tab. The tabs compute no state of a team and
hide no key by one: `team` judges.

## The parameters of a run

ONE profile, `ProfileScreen`, wherever the post launches something: provider (the providers wired), model (free,
the adapter's names suggested and listed), budget, effort (the five words suggested), permissions (`auto` left
blank, `strict`, `bypass` -- its help a warning), then the line of the PACKAGES (the state of each package beyond
the base; `enter` on it opens them, `space` toggles, the lines changed come back to the line and nothing is sent
before the profile is confirmed; a package marked required is greyed and never toggles), each with its help, what
each provider spells and names read from `agent providers --json` as it opens; a caller leaves the budget or the
packages out. `RunParamsScreen` is that profile and the run's name under it. `n` on an agent opens
it prefilled with what the agent last played (`last` of `agent status --json`), its packages as that face says them
(`packages`), and `ctrl+enter` opens the conversation with `--provider --model --max-budget-usd --effort --permissions`
filled in, then one `--package <name>=on|off` per package changed, after the flags of `--` (no `--provider` for a
caller's command); `p` on a conversation opens it with the provider fixed and its packages as the flow said them,
and `ctrl+enter` sends the CHANGED parameters as a `set` (`policy` answers, the status follows), then one `package` per
package changed, as `k` does. `S` on a team opens one profile per line of its season: no budget, no name.
`ctrl+enter` confirms from any field; `enter` goes to the next field from a line or a closed list, opens the line of the
packages, and chooses in a list unrolled -- `space` (or `down`, `up`) unrolls one. `model` and `effort` are lines that list: `down` or a click on their `▼` unrolls
the names they know in a list that floats over the fields below -- every name for a line empty or holding
an exact name (the cursor on it), the names a typed start begins (any case), every name when none begins
so --, `enter` in that list fills the line, `escape` folds it.
The status of a conversation says its state, `pp on|off`, then provider · model · budget · effort. `a` on the Agents tab asks
a path, `./pp agent add <path>` shown under the line, and `ctrl+enter` plays it; a refusal goes to the
remedy line.

## The memory

The conversations open are kept from one opening of the post to the next -- the agent
and the run of each tab, written at every opening and closing of a tab in the space `ui`
of the instance's metadata, through the engine's face. `./pp ui` with no agent named gives
them back at once: each tab shows its run's exchanges as history, read when the tab is first shown -- a tab never shown
reads nothing --, its run's provider, policy, budget, packages and context taken from the Agents tab's reading (`agent
status --json`) as soon as it is read -- the status, the gauge, `p` and `k` full before anything is launched --, and its
`agent chat` starts at the first message, `p`'s or `k`'s `ctrl+enter`, or `o` sent there; `u` shows its whole kept flow. Closing every tab empties the memory; `q` keeps it.

## The frame

One line of header at the top (the brand `pp` and the house's name on the left; on the right the engine's
version and the post's, as `./pp version -json` says them, then the house's root), the tabs `1·Dialogue`, `2·Agents`, `3·Teams`, `4·Tasks` (the digits
and the mouse switch them), the body of the active tab as the only part that scrolls,
and a footer at the bottom: the keys of the active tab, on as many lines as the width asks
(a line breaks between two keys), the remedy, the status row. The status row is three zones of fixed width, so that
nothing that comes or goes moves the rest: the status (the house, the pane's state, the last note), the ACTIVITY on
the right -- the turn under way, else the faces being read --, then the clock, the hour of its reading. While a face
is read, the spinner turns in the activity zone and says what is read, each verb once with how many of it
(`reading agent status ×4`), cut by `…` past the width of the longest turn; under 100 columns the zone shows the
glyph alone. The frame holds at any size from 40x8 up by its
layout alone; the status line of a team gives up its counts before its name, its `⚠` and the hour of its reading,
so it ends on that hour and the clock from 80 columns up; under a table's cursor a cell keeps its own colour; `q` closes the post; `t` opens the list of Textual's themes (light, dark, `ansi-*`, the current one
marked): the one under the cursor shows once the cursor has rested 0.4 s, so that a key held runs through the list, `ctrl+enter`
(or `enter`, its alias) keeps it at once in the memory, `escape` brings the one of before back. When the terminal's focus goes to another
window, the post leaves the widget focused -- its cursor stops -- and gives it the focus back on its return, without
styling the screen again. `O`, shown at the foot of every tab, opens the SETTINGS (`SettingsScreen`, `panes/settings.py`):
the unit every cost is said in, `USD`, `launches` or `tokens`, in a list; `ctrl+enter` applies it to the summary of a
season, its dashboard and the cost column of the Tasks table, and the post keeps it in its memory for the next opening
(`memory.keep_base`, as the theme); `escape` asks first once the choice moved. `U`, shown at the foot of every tab,
upgrades or repairs the machine: `upgrade` or `doctor`, then the post opens again on its tabs. An exception that
leaves the application ends the post: its whole trace is kept in the post's memory first (`ui.crash` of the
instance's metadata, the last one alone), and the terminal says the exception's line and the file the trace is in. `./pp ui crash` prints that trace.
Overlays take the cockpit's form: centred, 80 % of the width up to 100 columns (the runs of an
agent 95 % up to 160), a heavy border, their fields in a thin line, their own line of keys; they stack. `escape` closes the one on top; once you changed a value in it -- a source of a
document typed included --, it asks first (`palette.LEAVE_TYPED`): `ctrl+enter` closes it and loses what you typed,
`escape` gives it back as you left it; an overlay left as it opened closes at once. A field's title
is bold, its first letter in capital; its help under it is as light as a placeholder; a free field left empty shows an
example of what it takes (`e.g. 2.5`). Every zone
of a tab is FRAMED and LABELLED, in the theme's colour of a border out of focus -- on Teams the menu (`Teams · read 12 s
ago`), the head of the team (its name), `Members`, `Tasks of <member>`, `Sequence`; on Tasks `Show`, `Team`, `Tasks`,
the band of the task chosen (`T3 · review PR 88`); on Agents `Agents · read …`; on a conversation its transcript
(`<agent> · run <key>`, `read only` for a run read) --: from 70 columns and 30 rows a round frame, its label in its top
edge; under either, COMPACT, one thin line above the zone carrying its label, no row spent on a title, and one thin
`│` between the menu of Teams or Tasks and its centre (a frame's side takes its place in ample size). The message
line and the footer keep one thin line `─` above them; the header and the tabs carry none.

## What it needs

`uv` on the PATH. Textual is pinned in the script's own inline metadata
(`textual==8.2.8`, with `pyyaml` for the engine's face the memory goes through); the first call resolves it from uv's cache (or downloads it
once), the next ones start in a fraction of a second. The engine never imports
it.

The post plays each verb through the house's console: `pp`, or `pp.cmd` on Windows. Each verb runs apart from the
post's terminal -- on Windows in a hidden window of its own -- and a verb the post reads gets nothing typed on that
terminal, so the post's keys and mouse stay the post's. Closing a conversation or leaving a team's tab stops the
verb and every program it started (`taskkill /T /F` on Windows). A gesture whose verb of `team` ticks at its end
(`start`, `post`, `stop`, `resume`, `budget`, `ring`, `recurrence`) plays with `--no-tick`, and once it has answered the
post starts `team tick <team>` apart and never waits for it: the tick launches the members due one after the other,
never ended by the bound of a verb nor by the post's own end (ui 1.3.4).

## The refusals -- one line on stderr, exit 2

| refusal | when |
|---|---|
| `tty-missing` | stdin or stdout is not a terminal and neither `--render` nor `crash` was asked |
| `pane-unknown` | `--render` names a pane the post does not have |
| `size-invalid` | `--size` is not `WxH`, or smaller than 40x8 -- the least the frame fits in |
| `press-invalid` | `--press` names no key |
| `wait-invalid` | `--wait` is not `<kind>` or `<kind>:<seconds>` |
| `argument-unknown` | a word the usage does not know |
| `uv-missing` | `uv` is not on the PATH |
| `textual-missing` | uv could not give the script Textual (no cache, no network) |
| `chat-silent` | `agent chat` said nothing in 10 seconds |
| the verb's own | `agent-unknown`, `run-unknown`, `run-busy`… -- relayed as `agent chat` said them |
