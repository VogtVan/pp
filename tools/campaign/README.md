# The campaign -- a set of procs played on a harness, its conduction measured

`tools/campaign/campaign.py` plays a SET of procs on a harness and writes what the conduction
crossed. The harness is the modelled LLM (`--provider model`: deterministic, no content, no
network, cost 0 -- `adapters/model/`) or a real one on the operator's word (`--provider claude`,
`codex`, `gemini`, `cursor`: it launches and costs). The situations of the conduction sector are its
first set (`tests/conduction/roots`, the default of `--set`; `tests/conduction/README.md`); any
directory shaped as below is another.

    uv run tools/campaign/campaign.py plan [--set <dir>]                 # one plan per root x channel, nothing launched
    uv run tools/campaign/campaign.py play --provider model              # the campaign under the model: coverage written
    uv run tools/campaign/campaign.py play --provider claude --model sonnet --effort low --repeat 3 --root laps
                                                                        # the REAL mode: one root, three times, on your word
    uv run tools/campaign/campaign.py prepare                            # the operator's bench: one house per root
    uv run tools/campaign/campaign.py runsheet                           # the run sheet of that bench
    uv run tools/campaign/campaign.py report <date>                      # the report of a campaign, replayed from its artifacts
    uv run tools/campaign/campaign.py sheet <date>                       # the SHEET OF RESPONSE of a campaign, replayed from its artifacts
    uv run tools/campaign/campaign.py sheet <date> --mask chunk,bounce   # the same, the lines of those zones masked and counted apart
    uv run tools/campaign/campaign.py sheet <date> --against <date>      # the same, then compare.json and COMPARE.md against an earlier sheet
    uv run tools/campaign/campaign.py zones                              # the CENSUS of the conduction tests, written in the model's document
    uv run tools/campaign/campaign.py zones --check                      # the engine the census stands on; `engine-moved` when the engine moved
    uv run tools/campaign/campaign.py sheet --house <ws> --agent <a> --run <key> --out <dir>   # the sheet of one run of a house

## A set

A set is a directory: `campaign.yaml` at its root, and one sub-directory per ROOT of documents --
what `PP_DOCUMENTS` serves to a run (`--documents` at `agent run`, the variable at `./pp -new`). The
manifest says:

```yaml
name: patterns              # the set's name: the house's slug, the folder of the operator's bench
agent: agents/pat           # the agent of the house the campaign plays on
files:                      # accessories laid in the agent's workspace: <name there>: <path under the set>
  LINES.txt: LINES.txt
skills:                     # witness skills copied into the agent's instance (.pp/skills/<name>)
  - ../skills/pp-cyclewit
packages: [plan, steering]  # packages of the source the set's house carries beside `agent` (the agent borrows them)
clean:                      # what an exchange leaves in the agent's workspace, removed before the next one
  - .pp/cyclewit.done
roots:
  laps:                     # a sub-directory of the set
    door: LAPS.md           # the document the run enters on (PP_DOOR); absent: the kit's TURN
    message: "Play the door: one line per element, in order."   # the principal's message, owed
    manual: "Open the door LAPS offered to you and play it…"      # the message typed by hand at the operator's bench
    look: one `words` per lap, the proof of LP1 at the exit       # what the operator looks at
    model:                  # the INTENTION of the modelled LLM (below); absent: it conforms alone
      - field: [alpha, beta, gamma]
    expect:                 # what one EXPECTS of the root, in counts, judged per exchange by the sheet (below)
      words: 5
      launches: {strict: 5, hybrid: 2, bare: 1}
      parked: true
      proofs: 3
  bounded:
    door: BOUNDED.md
    message: "Say « first », then « second »."
    launches: 1             # the bound of ONE wake-up on the relayed channel, for this root alone (`--launches` otherwise)
  renewed:
    door: RENEWED.md
    message: "Say « first », then « second »."
    renew: true             # the exchange in two wake-ups: the first bounded at one launch, the run renewed between
                            # them (as an upgrade renews it), the second taking it up by `--run <key>`
```

A root without `message:`, a door that is no document of its root, a package the source does not carry, a file or a skill that does not
stand, a path of `clean:` outside the agent's workspace, a key under `expect:` the launcher does not
know, a `launches:` that is no whole number at least 1, a `renew:` that is not true or false:
`manifest-invalid`, naming the root and the key. A root that renews is played on the relayed channel in
two wake-ups: the plan carries the second as `resume`; the bare channel plays no renewal (the model does
not hold the house's console). The house of the campaign is installed from the source at the engine's own
version, so `./pp upgrade` would move nothing and renew nothing: the launcher renews the run by the
engine's own face (`persistence.renew`, `renewed` written in the trace). `plan` writes one JSON plan per root x channel (`launched: false`): the command, its stdin,
its environment, the door and the root -- nothing launched.

## The channels

| channel | how the exchange plays | one launch per |
|---|---|---|
| `relayed`, `strict` | the house conducts: `agent run <agent> --message … --documents <root> [--door …] --provider <p>` -- every output of pp is the prompt of a launch | output of pp |
| `relayed`, `hybrid` | the same, the agent's `conduction` setting written `hybrid` through the engine's settings face before the exchange and put back after: an output whose closing asks a value comes back in the model's tool result | output that moves the run on |
| `bare` | the provider's harness launched by hand on the agent's workspace, the message on its stdin, `PP_DOCUMENTS` and `PP_DOOR` in its environment: the model calls pp itself (`./pp -new`, then every call) until the passage ends | exchange |

`--channel` and `--conduction` select; without them, every root plays the three. The agent of the
house stands under the host's cap (`max_harness_tool_output` 25 000): on the bare channel the boot
is cut in chunks served by the model's own bare calls, as in the editor's extension; on the relayed
channel the engine's floor for a principal's run (200 000) applies.

The provider's binary is the adapter's to say: `BINARY` at `adapters/<host>/wire.py` (`claude`,
`codex`, `gemini`, cursor's `agent`; `None` for `model`). `play` refuses `provider-missing` only
when a binary is due and absent from the machine; a name no adapter carries refuses
`provider-unknown`.

The campaign's own environment is cleaned of the `PP_*` variables of the operator's session (a
marble receipt, a run, a home): what reaches a launch is the plan's and the adapter's.

## The real mode

The same campaign plays on a real harness, on the operator's word alone -- the word names the
provider, the model, the effort and the repetitions: `play --provider claude --model sonnet --effort
low --repeat 3`. `--effort` is one of the engine's five words (`low`, `medium`, `high`, `xhigh`,
`max`), judged at the engine's face before anything is written; it rides the `agent run` line on the
relayed channel and the policy of the launch on the bare one, and the adapter spells it or refuses
it (`model` refuses: it reasons as much as its data say). `--repeat <n>` plays every plan n times on
the same agent: a new run each time, the workspace cleaned between two, the exchange kept under
`<out>/<date>/<root>-<channel>[-<conduction>]#<k>/` (no suffix when n is 1).

Played on 2026-10-28 on `long-read` and `laps` (three channels, `--repeat 2`, effort `medium`,
`--budget 8`: bound 96 USD each): sonnet 3.07 USD, 346 s, 26 launches; opus 5.62 USD, 314 s, 26
launches; the 24 exchanges parked. Their light artifacts and their comparison to the `model` campaign
of the day are kept in the source repository, under `tests/conduction/evidence/campaigns/`.

Before the first launch `play` says the BOUND of the cost: plans x repetitions x `--budget` USD
where the adapter spells a budget (`max_budget_usd` in its `SPELLS`: the cap handed to every
exchange), 0 USD where the adapter needs no binary (the modelled LLM spends nothing), no bound where
a binary spells no budget. After the last exchange it says the REAL cost, summed from the records
(`cost_usd` of each exchange, read by the adapter in its `COST` scope), never estimated. `plan` writes
`repeat` and `effort` in every plan and consults no binary: the dry plan of a real provider is what the
bench proves.

On the bare channel of a real provider the model reads the agent's workspace as the editor's
extension would: `play` wires it for the provider by the provider's own adapter first --
`<agent>/pp -install -<provider>`, idempotent, the card and the permission `Bash(./pp:*)` the model
needs -- and hands it to the launch as its `wiring`; `prepare` shares the gesture; `model` wires
nothing.

## The report

`report <date> [--out <dir>]` reads what `play` kept under `<out>/<date>/` -- `campaign.json` (the
provider, the model, the effort, the repetitions, the budget, the bound, the exchanges in their
order), each exchange's `run.json` and `stats.json` -- and writes there:

- `coverage.json` and `COVERAGE.md`, the coverage below, rewritten from the same artifacts;
- `campaign.json` says the ENGINE the campaign played on (`engine`, the engine's own version): the census
  below refuses a campaign that does not;
- `report.json` and `REPORT.md`: one line per exchange -- the run, parked, the cost, the launches,
  the seconds, the blocks, the repairs, the refusals, the holes, the bounces, the held and inline
  outputs, the values handed, the mass and the tokens of the conduction, the error -- and, per root x
  channel over its repetitions, the cost and the launches as mean and p90 (at the nearest rank,
  `ceil(0.9 n)`, said as it is whatever n), the seconds, the passages finished (`parked`), the
  DEVIATIONS (repairs + refusals + holes + bounces), the held and inline outputs, the values and the
  CONFORMITY: the values handed without a repair over the values handed, as the engine judged them
  (`repairs` and `values` of its `-stats -json`, relayed by `agent stats`).

`play` writes the report itself at its end; `report` replays it: on the same artifacts it renders the
same bytes, so every figure of a campaign is read again from `<out>/<date>/` by one command. The lines
of `report.json` are the matter of a measure of what pp changes; the campaign judges nothing.

## The sheet of response

For every text pp handed to the agent -- the prompt of a launch, the result of a call of the console:
a block, a chunk of it, a `pp:` line, a refusal, the output of a gesture -- the sheet writes ONE line
with three readings of the same moment and a verdict (`sheet.json`, `SHEET.md` under `<out>/<date>/`,
written by `play` at its end and by `sheet <date>`: the same bytes on the same artifacts):

| column | what it says | read from |
|---|---|---|
| the oracle | the form the state of the run gives the text (`V` a value due, `T` a free step pending or said last, `M` the root exhausted, `R` a chunk before the last, `D` an answer, `S` a stopping refusal), what the stack awaits, who owes the next step, how the sequel comes, the act due | the run's trace alone: `outputs_of(trace)` cuts it into the items handed over |
| the reader | the candidate forms the text's traits admit (`adapters/model/semantics.py`, `READINGS`) and the act when they agree -- several candidates stay several, no order settles them | the text alone, by the modelled harness's grammar |
| the observed | the words said, the calls typed (by kind), the hand given back, and the act they make | the flow (`conduction`, `tool`, `tool-result`, `words`), or the harness's own lines on the bare channel |
| the verdict | `vert`; `rouge-conduction` when the reader admits several forms, or one that is not the oracle's, or when the console bounced a gesture (a call that moves nothing); `rouge-agent` when the agent did not do the act the reader gives; `trou` when the reader admits none | the three columns |

The texts are aligned per channel in the order they were handed; a text the console answered without
playing anything (a bounce, the block a name not offered brings back) has no item of the trace and its
oracle says the run did not move; an output the trace rendered and no launch carried (the root at its
end, when the house conducts) is counted at the foot. Every line carries the ZONE of the oracle's item
that handed its text: the root at its end `root`, a cut output `chunk` (every piece), a held one
`held-output`, else the act that opened it (`boot` after `new`, `value-judged` after an answer, `door`
after a routed door, `mount`, `inline`, `space`, `compaction`, `renewal`, `package-switch`,
`soft-catch`, `offer-absent`, `repair`), else `free-step`; a bounce `bounce`, a stopping refusal
`stopping-refusals`, `principal-advances` `bare-call`. The foot counts the lines by verdict, by
channel, by zone of the line and by zone crossed (the coverage of each line's exchange). `sheet --house
<ws> --agent <name> --run <key> --out <dir>` renders the same lines for one run of a house, its flow
read by the house's console and its trace at the agent's slot, under `<out>/<key>/`; a run the house
never opened refuses `run-unknown`, a date no campaign wrote `campaign-missing`. The verdict never
reads what the model knows of the run, and the harness never reads the trace.

Measured on 2026-10-28 (engine `0.2.0-beta.19`, the fourteen roots under `model`, three channels): 42
exchanges, 161 lines -- 153 vert, 5 rouge-conduction, 3 rouge-agent, 0 trou; 24 texts never handed -- counted `launcher_parked` when they are the root at its end (the launcher parks on
the trace without launching: no agent is owed those texts), `launcher_kept` when the launcher's bound stopped
the exchange (the output pending for the next wake-up), `unhanded` otherwise (none expected).

### The mask

`--mask <zone>[,<zone>…]` on `sheet` and on `play` names zones of a line, and the word `agent` for the
`rouge-agent` lines: a masked line KEEPS its verdict and carries `masked: true`; every count of the foot
leaves the masked lines out, and they are counted apart with their reds (`masked` in `sheet.json`, the
head line of `SHEET.md`). The lines with and without a mask differ by that flag alone: a mask shows what
one change of the conduction moves and hides what another will. A name no zone says refuses
`mask-unknown`. On the fourteen roots under `model`, `--mask chunk,bounce` leaves zero
`rouge-conduction` outside the mask.

### The expectation

A root's `expect:` says what one looks at of it IN COUNTS, over the whole exchange -- `words` (every
`words` said, the boot's table and the turn's line included), `launches`, `parked`, `proofs` (the
answers to a PROVE), `calls` (the calls of the console) -- each once for every channel, or as a mapping
of `strict`, `hybrid`, `bare` where the channels differ. The sheet judges them per exchange in its
EXPECT table (expected, seen, held) and counts the exchanges whose expectation is not held
(`expect_missed`); it compares no text of a production. The manifest of the patterns carries the counts
measured under `model` on 2026-10-29 (engine `0.2.0-beta.23`), every one held; `bounded` expects
`parked: false` on the relayed channels, its exchange stopped at the launcher's bound by nature.

### The comparison

`sheet <date> --against <date-before>` writes the sheet, then `compare.json` and `COMPARE.md` under
`<out>/<date>/`: the lines of the two sheets paired by (exchange, channel, rank), the verdict before and
after, the lines that appeared and disappeared, the counts of each side by verdict, by zone of the line,
masked apart. The other sheet is a date under the same `<out>`, or a path. It serves two readings: a
change of the conduction before and after under `model` (the same roots, the same channels), and a real
model against the modelled one on the same campaign. A side without its `sheet.json` refuses
`sheet-missing`. The light artifacts of a real campaign and of the `model` campaign it is compared to
(`campaign.json`, `report.json`, `coverage.json`, `sheet.json`, `SHEET.md`, `compare.json`,
`COMPARE.md`) are kept under `tests/conduction/evidence/campaigns/<date>/`, in git; the flows and the
traces stay out.

## The intention of the model

The modelled LLM has no content: what a real model would decide of itself on reading its
principal's message -- open the REVIEW door during the WORK, choose LEFT, answer three elements --
is said to it by the root's `model:` list, handed to the harness as `PP_MODEL_INTENT` (a JSON list of
one-key acts) and read as the message of a principal, never as a state of the run. Each act plays
once, at the first place where it can, and what is left is remembered for the session (the model's
own memory of its conversation, as its one miss is); `echo` is never consumed.

| act | what the model does |
|---|---|
| `open: REVIEW` | where a free step (`=> words`) offers `REVIEW` under TOOLS: says its production, then types `./pp <key> -s REVIEW` |
| `pick: LEFT.md` | where a PICK offers it among OPTIONS: elects it instead of the first value |
| `field: [a, b, c]` | where a field is due: answers that list |
| `echo: <title>` | names in every free production the matter an `INFORMATION — <title>` section serves (the element of a lap, so that a sink reads it) |
| `read: <file>` | at the WORK of a document: reads the file named in the workspace and says ONE `words` per line of it, each carrying its line -- what a real model does of « read the lines one at a time » |
| `gesture: <args>` | once the step's productions are said and its door answered: types `./pp <key> <args>` -- a script (`-s pp-cyclewit next`), a mount (`-mount NOTE.md`), a name the step does not offer (`-s NOBODY`), a space (`-open ROOM`, `-close`), a compaction (`-compacted`), a switch (`-disable agent`); over a held output only a gesture that moves nothing plays at once (a view, a script), one that moves the run waits for the next launch |
| `bare: true` | where a value is due: types the bare call |
| `bounce: true` | once a held line answered its call (`pp: value judged`): types the same call again -- the console answers `not played`, the model hands back |
| `stray: true` | hands a `=> words` production to the tool instead of saying it |
| `persist: <variant>` | makes the named miss (`wrong-form`…) at EVERY place where it is possible, never remembered as made: the repairs up to the bound, then `repair-exhausted` |

Without `model:`, `conform` alone: the first option, three elements of its own, no door opened. Every
free production of the model CITES what it read -- the document and the keyword of its step, the titles
the block served, the element of the lap (`STRATEGIES` in `adapters/model/semantics.py`) -- so that the
sheet reads, in the words said, which block the model answered; a proof's evidence names its code.

## The census -- the coverage section of the model's document

`zones [--evidence <dir>] [--model <date>] [--real <date>]… [--doc <path>]` reads the evidence alone -- by
default the latest COMPLETE `model` campaign under `tests/conduction/evidence/campaigns/` (every root of its set
on the three channels, its engine said) and every real campaign standing there -- and writes the coverage
section of the document `--doc` names between its two markers, `<!-- coverage:begin … -->` and
`<!-- coverage:end -->`: the model campaign, its date and the engine it played on, the real campaigns
(provider, model, effort, engine, exchanges, the sheet's counts), then one row per zone of `semantics.ZONES`
-- what it is, the roots and the channels that cross it under the model, the real exchanges that cross it on
the same engine and on an older one (apart), its STATUS -- and the count by status. A zone exists on the
channels its data say (`semantics.ZONES`: the three, the relayed ones alone for what the conduction of the
principal alone renders, hybrid alone for `inline`). It is `safe` when the model campaign crosses it on every
channel it exists on and three real exchanges at least, on the same engine, cross it with no
`rouge-conduction` and no `trou` on their lines (`SAFE_REAL`); `measured` when the model campaign crosses it
on every channel it exists on; `partial` when on fewer; `silent` when never. The section is
inserted at the end of a document that carries none and replaced otherwise; nothing else of the document
moves; no date of now is written: replayed on the same evidence it renders the same bytes. The begin marker
carries the keys (`model`, `engine`, `real`, `zones`, `safe`) and `zones --check` reads them: it says the
engine the census stands on, its campaigns and the zones safe, and refuses `engine-moved` when the engine
in place is another -- the reminder before a publication; `coverage-missing` without the section. A
campaign whose `campaign.json` says no engine refuses `evidence-unversioned`; no complete model campaign,
`model-missing`; a `ZONE_EVENTS` whose keys are not `ZONES`, `zones-mismatch` at the first verb.

Written on 2026-10-29 from the model campaign `2026-10-29T0744-model` (engine `0.2.0-beta.22`, 42
exchanges, 0 rouge-conduction) and the five real campaigns of the evidence: 25 zones -- 1 safe (`chunk`),
11 measured, 4 partial (free-step, held-output, inline, advance: never on the bare channel), 9 silent
(section-break, space, compaction, renewal, bounce, soft-catch, offer-absent, package-switch,
launcher-bound). Written again the same day from `2026-10-29T0853-model` (engine `0.2.0-beta.23`:
twenty roots, 60 exchanges, 0 rouge-conduction): 25 zones measured, 0 partial, 0 silent;
0 safe, the real campaigns of the evidence standing on older engines.

## The coverage

After each exchange the campaign reads the run's trace (its events), the agent's flow (the `words`,
`tool`, `tool-result`, `thinking` of every launch), the harness's own lines on the bare channel, and
the records (`exchanges.json`, `stats.json`), and writes under `<out>/<date>/`:

- `<root>-<channel>[-<conduction>]/`: `run.json` (the plan, the verdict, the exchange's coverage),
  `stdout.txt`, `stderr.txt`, `flow.jsonl`, `exchanges.json`, `stats.json`, `trace.jsonl`,
  `harness.jsonl` (bare);
- `coverage.json` and `COVERAGE.md`: the ZONES of the conduction (`adapters/model/semantics.py`)
  crossed by each exchange, zone x exchange x count; the zones never crossed; per exchange the run,
  whether the passage ended (parked), the launches, the seconds, the blocks, the calls, the HOLES
  (a text the model has no act for), the bounces (`pp: not played`), the refusals, the error.

A zone is read from the events of the trace -- `boot` from `new`, `free-step` from `pending`,
`fusion` from `batched`, `chunk` from `cut` and `chunk`, `held-output` from `held`, `value-judged`
from `answer`, `proof` from the answers to a PROVE, `mount` from `mounted`, `door` from `door`
(the entry) and `routed` (a door opened by `-s`), `space` from `opened` and `closed`, `lap`, `next`,
`inline`, `advance`, `repair`, `switch`, `refusal`… -- or elsewhere when no event says it: `hole`
from the harness's thinking, `bounce` and `bare-call` from its tool calls, `launcher-bound` from
the agent's `launches-spent`. Since engine `0.2.0-beta.23` the trace says what it
did not: `section-break` from `section` (a `§` crossed, with the marked step), `soft-catch` from `stray`
(the soft catch, with the step), `offer-absent` from `offer-absent` (the name denied), `space` from
`opened` (the name the agent opened) and `closed`.

Measured on 2026-10-27 (engine `0.2.0-beta.19`, the six patterns under `model`, three channels): 18
exchanges, 18 parked, 33 launches, 18 s, 0 hole, 0 bounce, 0 refusal; `--repeat 2` on 2026-10-28:
36 exchanges, 36 parked, 66 launches, 36 s, 0 deviation, the report rendered in 0.08 s. The fourteen
roots on 2026-10-28: 42 exchanges, 38 parked (`stubborn` stops on `repair-exhausted` on the three
channels, `two-steps` by the tool stalls where the modelled LLM is undecided), 74 launches, 42 s. The
twenty roots on 2026-10-29 (engine `0.2.0-beta.23`): 60 exchanges, 58 parked (`bounded` stops at the
launcher's bound on the relayed channels, by nature), 104 launches, 61 s, 0 hole; the sheet 220 lines, 215
vert, 0 rouge-conduction, 5 rouge-agent (the three handed lines of `stray`, the proof handed again in
`bouncing`: the agent's own misses, wanted), 0 trou; against `2026-10-29T0744-model`, the 162 lines of the
fourteen roots of before paired, 0 changed. The real campaign of that day (sonnet medium, the nine new
roots, `--repeat 3`): 81 exchanges, 75 parked, 119 launches, 1 295 s, 5.38 USD under a bound of 81;
208 lines, 181 vert, 0 rouge-conduction, 27 rouge-agent, 0 trou; against the model played three times, 192
paired, 35 changed between vert and rouge-agent; opus medium on the same
roots: 81 exchanges, 75 parked, 116 launches, 1 063 s, 8.96 USD, 0 deviation, 175 lines, 153 vert, 0
rouge-conduction, 22 rouge-agent (all a gesture typed before the line said), 0 trou; the census: 17 zones safe
on beta.23, 8 measured.

## The operator's bench

`prepare` builds one disposable house per root under `~/.local/share/pp-campaign/<set>/` (outside
the repository), each the product installed with `agent` and `ui`, the set's agent born, the root's
documents laid in its procs with an overlay of `TURN` that OFFERS the door, the accessories and the
skills laid, the agent's cap at the host's, Claude Code wired at the agent's folder and at the
house's root -- so the same message plays in the editor's extension (the model calls pp itself) and
at the post (`./pp ui <agent>`; the house calls pp), on the same house, to compare. A house that
stands is kept and upgraded from the source (`standing`); `--fresh` rebuilds it. `runsheet` says, per
root, the message to type and what to look at (`RUNSHEET.md` beside the houses).

## The bench

The conduction sector of the bench, `tests/conduction/` (tests/README.md, rule 11), keeps the campaign
honest at every `./pp -test`, under the model alone, on throwaway houses -- `launcher/`, the launcher's
verbs: `plan.py` (the plans of a throwaway set, the manifest
judged, the twenty roots of the patterns opened by the engine, the bound and the renewal at the plan, the binary of the provider, `prepare`
and `runsheet`, the dry plan of a real provider with `--repeat` and `--effort` on an empty PATH, and the
report of a campaign played `--repeat 2` under the model: the mean equal to the values, p90 equal to
the mean, `coverage.json` rewritten byte for byte), `relayed.py`, `hybrid.py` and
`bare.py` (one channel each: the six patterns of the engine parked at cost 0, the zones of
each root in the table, the channel's own zones, the intention played), `sheet.py` (the sheet
of `long-read`, `review`, `gesture-while-held` and `read-lines` on the relayed channel: one line per
text handed, the chunk at the prompt read R alone and the gesture played over the held output, the replay byte for byte, the sheet
of one run of the house equal to the campaign's, the refusals, the four lines of `read-lines` carried
one per `words`, the expectations judged and a witness set's missed), `mask.py` (the zone of
every line, the mask that changes no verdict, two campaigns compared to zero change and replayed byte
for byte, the mask on one side), `zones.py` (the closed list of the zones and `ZONE_EVENTS` keyed
on it, the engine in the evidence, the census written and replayed byte for byte on a throwaway document, a
real campaign read -- `safe` on the same engine, nothing on another --, `zones --check` and the refusals);
`zones/<zone>.py`, one scenario per zone of the conduction, each playing the fewest roots that cross it on
every channel the zone exists on (the data's, never the scenario's) and reading the sheet of that play --
an exchange parked unless its root expects otherwise on that channel; `census.py`, the census of the sector
(every zone carried by a scenario or declared `silent:` at the manifest with the work that owes it, every
root played, no CHANNELS constant in a scenario).
A real provider is never launched by the bench.
