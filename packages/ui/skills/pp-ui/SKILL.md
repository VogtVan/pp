---
name: pp-ui
description: >-
  The post of the house: `ui [<agent> ...]` opens the terminal screen with one conversation tab per agent, then the Agents and Teams tabs; `ui --render <pane> --size WxH` prints a pane and exits; without a terminal `ui` refuses `tty-missing`. A main, not an engine -- it renders what the verbs say and plays nothing itself; the calls are in the body.

---

# `pp-ui` — the post of the house

## The hand, in one breath

The post of the house -- `ui [<agent> ...]` opens the terminal screen on the house's own terminal (`q` closes it), one conversation tab per agent named (`--run <key>` resumes a run of the last one; what follows `--` goes to `agent chat`), then the Agents tab (the agents of the house, the runs of each in an overlay -- resume, new, name, stats) -- no agent named, the conversations kept open last time come back; `ui --render <pane> --size WxH` prints a pane as text and exits; without a terminal `ui` refuses `tty-missing` in one line. A main, not an engine -- it renders what the verbs say and plays nothing itself.


The post is a terminal screen the house opens on its own terminal. It renders
what the verbs of `pp` say and delegates every gesture to them: it conducts
nothing and reads no file of the instance; it writes its own memory of the
conversations open alone, through the engine's `metadata` face.

## The calls

| call | what happens |
|---|---|
| `./pp ui` | opens the post on the terminal at once, with the conversations its memory kept: each tab shows its run's exchanges as history, and no `agent chat` starts before you send a message, `p`, `o` or `k` in that tab; `q` closes it, the digits switch the tabs |
| `./pp ui <agent> [<agent> ...] [--run <key>] [-- <flags>]` | opens the post with one conversation TAB per agent named: `agent chat <agent> --json` is held under the post for each; `--run <key>` resumes a standing run of the last agent named; what follows `--` goes to every `agent chat` the post opens -- at the start and from the Agents tab -- as it is (`--harness`, `--permissions`, `--launches`…; the overlay's own flags come after it), and its `--harness` rides `team start` when `S` starts a team, with the `--provider` beside it -- the grammar the command's output is read in, in place of the overlay's provider; the memory is left aside |
| `./pp ui --render <pane> --size WxH` | prints the pane as text at that size and exits -- no terminal needed; `<pane>` is `frame` (the whole screen on its first tab), `dialogue`, `agents`, `teams` or `tasks`; `--size` defaults to `80x24`; `--regions` prints where the menu, the folded line and each band of the centre stand instead of the text |
| `./pp ui --render <pane> --press <keys>` | the same, after the keys are pressed in order -- comma-separated, Textual's names (`2`, `3`, `tab`, the letters); `wait:<kind>` in the list pauses until one more event of that kind reached the dialogue, `wait:team:<event>` one more object of the Teams tab's watch; `nodes` notes the widgets of the last block of the agent's words (`nodes <n> …` on a last line); `blur` and `focus` make the post lose and take back the terminal's focus and note the widget focused and the post's focus (`focused <id>:<0|1> …`) |
| `./pp ui <agent> --render dialogue --wait <kind>[:<seconds>]` | the capture waits for one more event of that kind (10 seconds by default): `--wait waiting` shows the dialogue after an exchange ended; `--wait team:<event>` an object of the Teams tab's watch |
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
said it: what the principal typed (`▶`, the hour) rendered as markdown; per launch, ONE line of
the CONDUCTION -- pp's output served to the agent (`◇`, the launch, the block it serves as the
flow names it, its size) --, what the agent did meanwhile -- ONE line per call of a tool (`⚙`, its name or `pp`
for a call of the agent's console, its title, `✓` and the size of its result, red with `✗` on an error, `…` until the
result comes), ONE line of its thought (`∴`, the last count of tokens or the start of its text), its words (`◀`, the
last ones not twice when the agent's line repeats them) --, ONE line of its steps counted by kind (bold yellow on a refusal),
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
tools and of their results, each showing its own again (`[c] conduction: shown`, `[b] calls: shown` in the footer). Every block is selectable with the mouse: `ctrl+a` selects
the whole transcript (in an overlay, its content), `ctrl+c` copies the selection (the status
says `copied <n> chars`). While a turn runs, a spinner turns on the tab's title and at the head of
the status, bold in the theme's accent and followed by how long the turn has run; the message line --
one row at rest, growing to 8, `enter` sends, `ctrl+enter` (sent as `ctrl+j` by most terminals) goes to the
line -- stays open -- what is typed there is kept, dim -- and `enter`
waits: it sends nothing until the turn ended (`enter: waits` in the footer), then sends the
line. `s` stacks the statistics of the conversation's run (`agent stats --json`). `u` reads the tab's past again -- its
kept flow (`agent flow --json`), else its exchanges -- and shows it all at once, as it was lived; while a turn
runs, `u` reloads nothing and the remedy line says why. While a turn runs, a
`■ stop` button stands beside the message line and the footer says `[ctrl+g] stop the turn`: the button
(a click, or `tab` to it then `enter`) or `ctrl+g` sends `stop` during an exchange; at rest the button is gone.
`escape` never stops a turn: it leaves the message line, during a turn as at rest, so that the letters
act; `i` alone goes to it -- no line takes the focus by itself, at the opening of a conversation, a switch of
tabs or the end of a turn; `p` opens the run's parameters, its NAME the last field (`agent name` keeps
it at once, or at `opened` for a run that opens, the tab follows); `x` closes the tab (`quit` to its verb: the run stands; 5 seconds later the verb's whole process group is ended, `pp-agent` and its wake lock with it); ONE run, ONE tab: taking up a run a LIVE tab holds -- from the Agents tab, or named twice at the start -- activates that tab and launches nothing; a run whose tab ENDED is taken up IN PLACE -- the same tab, its transcript kept (the memory of a turn's lines is the tab's), a new `agent chat --run` under it, the history not read again --; a new run (`n`) always opens its own tab; `o` suspends the conduction of the conversation or brings it back (`conduct` to the verb:
`⏸` on the title, `pp off` on the status, `[o] pp: off` in the footer, a `pp OFF` banner heading the tab and
the message line bordered in the warning colour; under `pp off` a message is a
bare exchange, verdict `✓ unconducted`, no line of conduction); `k` opens the run's packages as the flow said
them, an editor: `space` toggles a line and sends nothing, `enter` sends one `package` per line changed,
`escape` nothing; a switch the verb holds waits (`⧗` on the title, `packages: … …` on the status, `… pending`
at `k`) until it plays; a refusal goes to the remedy with its detail (no list in the flow, the remedy says so);
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
turn changes; beside the message line, the gauge says the run's context as `agent stats --json` says it --
`ctx ▰▰▱▱▱▱▱▱▱▱ 17% · pp 33%`, pp's share in the accent, `ctx —` without a context --, read after each verdict
and when a run is taken up. A cap the engine raised (`ready.cap`, `opened.cap`, `applied` above `set`)
is said there too, `<agent>: cap <set> lifted to <applied> for this run`, while the run rests.
Every overlay keeps its line of keys in sight: its body scrolls inside the box, the focused field
scrolled into view; the post shows no tooltip. An overlay renders what the agent wrote -- its answer
at a launch, its words -- as markdown, any other content as the text it is. `U+FE0F` is taken out of what the post renders as
markdown, of the lines' summaries and of an overlay's content, so that a table's columns stay
aligned on the terminal; an overlay copies what it shows.

## The agents

The Agents tab is the table of the agents of the house -- the house itself first (`.`, named by its folder
and `(house)`, a run of its own instance), when `agent list --json` says it --, read from `agent list --json` and
`agent status --json` -- agent, runs, running, the state of its last run, cost, launches, its weight (what a
purge of its runs would remove, `1.2 MB`),
the moment of its last event (its hour today, `DD/MM HH:MM` another day, the year when it differs) --, read at the start, on `u` and after every verdict a conversation receives,
never polled; the status says the count and the hour of the reading. On an agent: `n`
opens a new conversation with it; `enter` opens the OVERLAY of its runs, where `enter`
resumes the run under the cursor in a tab of the dialogue -- a run a member of a team holds, marked `<team>/<member>` in the column `team`, opens READ instead -- (its history, `agent exchanges
--json`, replayed dim first and dated the same way, then the live flow), `n` opens a new conversation, `s`
stacks its statistics (`agent stats --json`: the sums, then the conduction's detail, the time in `h min s`),
`P` purges the run under the cursor and `B` the agent's runs before a date, `u` reads again, `escape` closes.
Each run says its `weight`. A purge is shown before it plays: `agent purge` WITHOUT `--yes` says what it would
remove, shown with the exact `--yes` command, which plays only once the run's key -- or the date -- is typed as it
is; `workdir-unpushed` brings the purge shown again with `--force`, typed a second time; every refusal of the verb
(`run-busy`, `run-held`, `run-unconducted`, `call-busy`, `purge-invalid`, `run-unknown`) goes to the remedy line as
it said it, and the runs removed leave the post's memory. The post types nothing outside a conversation's message line: the name
of a run is asked in the overlay of its parameters, with its help under it.

## The teams

Two tabs show the teams of the house as `team status --json` says them, each read from the first time
it is shown, each a MENU on the left and a CENTRE of horizontal bands, never two parts side by side;
under 70 columns the menu folds into one line, which `[` `]` (and `{` `}`) change. The TEAMS tab: the
menu of the teams (each name in the look of its state -- working, waiting, paused with `⏸`, idle, never --,
the wake-ups under way, the questions to the owner, the tasks done not seen; `-` for a team never started); the
HEAD of the team chosen (its owner and mandators, its state -- `waiting · owner, budget`, `paused since … by …` --,
its budget `spent/cap · reserved · left`, its wake-ups
against their bound, its net, what waits for the owner counted on one line), then its MEMBERS (the agent,
the run, how it stands, its tasks, the debts it owes -- `owes`, bold yellow once one was reminded --, `live`; a
member the face says suspected in bold red, `try HH:MM` the hour of its next try). The team's ONE `team watch <name> --json` -- at most one per team, shared by
the two tabs, a thread and a read tab, never one per task -- follows the team chosen and reads it again at each
object but `quiet`; choosing another team leaves it, ended when nothing else follows it; leaving the post ends
every watch whole; `u` reads again. The TASKS tab: the filters `SHOW` (`running` first, `for you`, `stopped`,
`resolved`, `all`, each with its count) and `TEAM`; the tasks of every team started they keep (the id, the name,
else the start of the text cut at 30 characters; the team, the state, the holders, the progress counted on
the face's `dos`, the age of the last event -- every freshness of the two tabs is an age against the post's one
clock, the hour of its reading on the status line: `12 s`, `3 min`, `2 h`, `3 d`), read by one `status <name> --json` per team started and
again at each object of a team's watch but a step and `quiet` -- a task a wake-up plays (`running`) with the spinner
before its name, the tab's title counting them (`4·Tasks ⠹ 2`) --; then the task under the cursor whole and its LAST
ACTION, one `live:` line per member -- its last step on the task and the last call of a tool of that wake-up read
from its kept flow (`agent flow <path> <run> --exchange <index> --json`, one reading per member at a time), dim once
the wake-up ended; `launched 12 s ago` for a member running with no step seen, `relance owed` for a wake-up the face
says is a reminder; a task at rest its `last` event --, a step
tied to its member and its task by the face's own `agent` and `task`. Members gains `live`: a member's last step,
or `since` while it runs. `enter` opens the task's THREAD in an
overlay, live: its history by `team log --json --task`, then what the team's watch says that names the task, an
`id` shown once, an end of a wake-up reading the history again; `escape` closes it. Both tabs PILOT by the verbs of `team` alone, each command SHOWN
before it plays, word for word, its refusal on the remedy line as the verb said it. A gesture that asks more
than a yes is WRITTEN in an overlay, `GestureScreen`: its fields, each with its help, the command they make under
them, `enter` from any field playing it; a field left as it opened composes no flag (`to` on the holders, `as` on
the owner, an empty name). On TASKS: `m` writes on the task under the cursor (`to`, `as`, `reply to` read from
`team status --json`, then the text), `s` stops the task, `r` resumes it (a message, `as`), `k` kills its
wake-ups once its name is typed, `v` shows its result (`task-open` on the remedy line), `n` a new task (its team,
its name, `to`, `as`, its message), `l` the journal. On TEAMS: `N` gives birth to a team from a template (the form
reads `team templates --json`: the template, the name, the members -- left as they are, team writes their paths;
changed, `<name> <path>` per line --, the root, the principals, the ceremony, the limits, the schedule; `enter` plays
`team new` as shown, `ctrl+s` plays it then starts the team born by the path of `S`; the post writes no file, the
intention is the one team writes), `n` a new task, `T` ticks, `S` opens the SEASON of the team (`SeasonScreen`:
`all` and one line per member of `declared` -- `team declaration --json` --, each edited in its `ProfileScreen`, a
member's field left empty `all`'s, a package `required` greyed; a new season opens on the face's `launch` and
`members[].launch`, a first one on the agents' `last`; the budget and the wake-ups of the season, the first task's
name and message -- optional: without it the season stands on its ceremonies and the posts to come (team 0.38.0) --; the packages of a line read from the declaration, a member not born yet included; the command composes what `all` carries, each member's changes
and switches, `--budget`/`--budget-wakes` where they differ from `TEAM.md`'s, the harness before any `--member`,
never a `--max-budget-usd`; `ctrl+s` plays it; a declaration `start` would refuse opens nothing), `B` raises its budget (`team budget`, prefilled
from the face, a field changed alone played), `b` shows the owner's inbox (`team inbox --json`: `enter` on a
question replies on its task, `x` marks it seen), `e` its declaration (`team declaration --json`, read only),
`X` stops all tasks once the team's name is typed, saying what it stops, `P` pauses the team or resumes it, `l` the journal; on the member under the cursor, `R` resets its run once its name is typed, `d` shows
it whole, `a` its responses (`team responses --json --agent`), and `enter` or `i` opens its run READ in a tab of
the dialogue -- titled `<team>/<member>`, a `◉ read only` banner, no message line, no `agent chat` launched:
its kept flow (`agent flow --json`) replayed as lived turns -- conduction, calls, thought, answer --, then its
wake-ups live from its team's watch, of which the tab keeps the objects of that member AND that run, the exchange
a step names read again; a run without a kept flow replayed from its exchanges (`agent exchanges --json`) --; a member without a run says so on the
remedy line. `c` opens the CEREMONIES of the team in an overlay: their table (the progress of the last ring,
counted on the face's `progress`; the next ring as `team` computed it), the detail of the one under the cursor
(its chain `after`/`then`, the participants still waited for, the wait of the task of its last ring), the `as`
of a ring and its command; `g` there rings the ceremony at hand (`team ring`), `enter` leads to the task of its
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
(`packages`), and `enter` opens the conversation with `--provider --model --max-budget-usd --effort --permissions`
filled in, then one `--package <name>=on|off` per package changed, after the flags of `--` (no `--provider` for a
caller's command); `p` on a conversation opens it with the provider fixed and its packages as the flow said them,
and `enter` sends the CHANGED parameters as a `set` (`policy` answers, the status follows), then one `package` per
package changed, as `k` does. `S` on a team opens one profile per line of its season: no budget, no name.
`enter` confirms from any field, a closed list included -- the line of the packages aside, which `enter` opens; `space` (or `down`, `up`) unrolls a list,
where `enter` chooses. `model` and `effort` are lines that list: `down` or a click on their `▼` unrolls
the names they know in a list that floats over the fields below -- every name for a line empty or holding
an exact name (the cursor on it), the names a typed start begins (any case), every name when none begins
so --, `enter` in that list fills the line, `escape` folds it.
The status of a conversation says its state, `pp on|off`, then provider · model · budget · effort. `a` on the Agents tab asks
a path, `./pp agent add <path>` shown under the line, and `enter` plays it; a refusal goes to the
remedy line.

## The memory

The conversations open are kept from one opening of the post to the next -- the agent
and the run of each tab, written at every opening and closing of a tab in the space `ui`
of the instance's metadata, through the engine's face. `./pp ui` with no agent named gives
them back at once: each tab shows its run's exchanges as history, and its `agent chat` starts at the first
message, `p`, `o` or `k` sent there; `u` shows its whole kept flow. Closing every tab empties the memory; `q` keeps it.

## The frame

One line of header at the top (the brand `pp` and the house's name on the left, the
house's root on the right), the tabs `1·Dialogue`, `2·Agents`, `3·Teams`, `4·Tasks` (the digits
and the mouse switch them), the body of the active tab as the only part that scrolls,
and a footer at the bottom: the keys of the active tab, on as many lines as the width asks
(a line breaks between two keys), the remedy, the status with the hour of its reading. The frame holds at any size from 40x8 up by its
layout alone; the status line of a team gives up its counts before its name, its `⚠` and the hour of its reading,
so it ends on that hour and the clock from 80 columns up; under a table's cursor a cell keeps its own colour; `q` closes the post; `t` opens the list of Textual's themes (light, dark, `ansi-*`, the current one
marked): the one under the cursor shows once the cursor has rested 0.4 s, so that a key held runs through the list, `enter`
keeps it at once in the memory, `escape` brings the one of before back. When the terminal's focus goes to another
window, the post leaves the widget focused -- its cursor stops -- and gives it the focus back on its return, without
styling the screen again. `U`, shown at the foot of every tab,
upgrades or repairs the machine: `upgrade` or `doctor`, then the post opens again on its tabs.
Overlays take the cockpit's form: centred, 80 % of the width up to 100 columns (the runs of an
agent 95 % up to 160), a heavy border, their fields in a thin line, their own line of keys; they stack. A field's title
is bold, its first letter in capital; its help under it is as light as a placeholder; a free field left empty shows an
example of what it takes (`e.g. 2.5`). Every zone
of the post is set apart by one thin line in the theme's colour of a border out of focus -- `─` above the message
line, the footer and a band that follows another, `│` between a menu and its centre --; the header and the tabs carry
none.

## What it needs

`uv` on the PATH. Textual is pinned in the script's own inline metadata
(`textual==8.2.8`, with `pyyaml` for the engine's face the memory goes through); the first call resolves it from uv's cache (or downloads it
once), the next ones start in a fraction of a second. The engine never imports
it.

## The refusals -- one line on stderr, exit 2

| refusal | when |
|---|---|
| `tty-missing` | stdin or stdout is not a terminal and no `--render` was asked |
| `pane-unknown` | `--render` names a pane the post does not have |
| `size-invalid` | `--size` is not `WxH`, or smaller than 40x8 -- the least the frame fits in |
| `press-invalid` | `--press` names no key |
| `wait-invalid` | `--wait` is not `<kind>` or `<kind>:<seconds>` |
| `argument-unknown` | a word the usage does not know |
| `uv-missing` | `uv` is not on the PATH |
| `textual-missing` | uv could not give the script Textual (no cache, no network) |
| `chat-silent` | `agent chat` said nothing in 10 seconds |
| the verb's own | `agent-unknown`, `run-unknown`, `run-busy`… -- relayed as `agent chat` said them |
