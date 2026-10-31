# The adapters

*The claude column verified on 2026-09-26 (claude 2.1.270, WSL2); codex, gemini
and cursor read from their docs the same day, NOT verified on a machine.*

An adapter is one directory, `adapters/<host>/`: a module `wire.py` and a
README. The engine knows no harness by name: `-install … -<host>` loads
`adapters/<host>/wire.py` by its path and plays its `wire(workspace, meta)`,
which writes the harness surface — the card, the door, the marble launcher or
config, the permissions — and says what it skipped. `install.wired_providers`
reads those artifacts back to know which adapters a workspace carries. The
interactive surface, flag by flag, is REFERENCE § The adapter surface; each
README says its host's story.

This page is the reference of the **non-interactive mode**: how pp launches
ONE exchange of a harness by its command line — an agent of a house is woken
by a command, plays its blocks, parks when its root is exhausted. It is the exchange the
editor's extension launches, and nothing else: the extension invokes the same
CLI. An exchange is one call of a **session of the provider** — opened (a new
conversation the provider keeps and names) or resumed (the identity the
provider gave) — and a run is conducted exactly as in the chat; only the
principal and the launch differ. The facts below are what the `launch()`
contract composes: the face `conductor.adapters.launch(provider, workspace,
meta, prompt, marble=None, root=None, wiring=None, policy=None, session=None)`
at the engine and one `launch()` per adapter (engine `0.1.0-beta.24`, the
session since `0.1.0-beta.30`, kept by `tests/adapters/launch.py`); the skill
`pp-agent` launches it from a house.

## The marble at every call

At EVERY call of the model — the first and every one after — the system prompt
and the whole context reach the agent. The marble (the compiled standing rules)
rides the system prompt when the host has a channel for it, the standing rules
served inline otherwise. Three cases, one per kind of host:

| the host | what pp does | hosts |
|---|---|---|
| no system-prompt channel | no receipt: the engine serves the standing rules inline at the opening, and the session's history brings them back at every resume | cursor |
| a channel, but a session that does not reliably record the system prompt | the marble at EVERY launch, the resume included, with the receipt `PP_MARBLE=1` | claude — `--system-prompt-snapshot` (default `on`) records the prompt at the first request, but has « no effect where system-prompt recording is not yet enabled » and drops the record at a compaction; handed again, the marble changes nothing where the record holds and restores it where it does not · gemini — `GEMINI_SYSTEM_MD` is read by the process, and `--resume` restores the conversation, not the system prompt (docs, not verified on a machine) |
| a channel the host re-reads by itself at every process | nothing by the call -- the receipt said in `env` as DATA all the same, for the principal's own calls | codex — `.codex/config.toml` (`developer_instructions`) and its receipt |

## The contract: `launch()`

Every `adapters/<host>/wire.py` gains three faces beside `wire()`:

    launch(workspace, meta, marble, prompt, wiring=None, policy=None, session=None, workdir=None) -> (argv, env, stdin)
    answer(stdout, stderr) -> {cost_usd, denials, error, session}
    events(line) -> [{kind, …}]        # see "The third face: events()"

The model's text has ONE source: the `words` of `events()`, in their order. `answer()` reads
no text (engine `0.1.0-beta.72`); a caller composes what it shows or keeps from
the words -- `pp-agent` keeps them per launch and writes `response`, their composition, once.

| Term | What it is |
|---|---|
| `workspace` | the member's root — the directory the harness runs in |
| `meta` | the instance directory (`workspace/.pp`) |
| `marble` | the compiled standing rules the harness must carry — `.sys/system.md`, or the host's own composition (`.sys/system.gemini.md`); a marble HANDED by its path reaches the provider's channel as the adapter spells it: claude appends the file, gemini names the composition `wire()` made beside it (`system.common.md` → `system.common.gemini.md`, the file itself before `wire()` composed it), codex and cursor read no marble at the call (engine `0.1.0-beta.59`). The marble of a run its principal conducts is `.sys/system.common.md`: the caller names it |
| `prompt` | the text of the exchange: the pending block and the message, as the caller hands it — written on the process's STANDARD INPUT, never an argument (engine `0.1.0-beta.59`): Linux bounds one argument at 128 KiB, a prompt that carries whole blocks is bounded by the model alone |
| `wiring` | the directory whose harness configuration is HANDED to the process — the home of an agent, wired once; `None` when there is nothing to hand. Claude reads `<wiring>/.claude/settings.json` by `--settings` when the file stands (the permissions the home wrote, read by a process running in the agent's directory); gemini, codex and cursor read nothing: their no-question modes need no allowlist |
| `policy` | what the exchange may spend and do, judged ONCE at the engine's face (`conductor.adapters.judged`): `model` (a non-empty name), `max_budget_usd` (a number above 0: the bound of THIS launch -- the `agent` package hands it the remainder of a run's budget cap, and drops it where the adapter does not spell it), `permissions` (`auto`, `strict` or `bypass` — see *The permission regime*) and `effort` (`low`, `medium`, `high`, `xhigh` or `max` — see *The effort*) — an unknown key refuses `policy-unknown`, a value that does not parse `policy-invalid`, both naming the key. Each adapter spells what its host knows and refuses what it does not, naming itself and the key (`policy-unsupported`): claude `--model`, `--max-budget-usd`, `--permission-mode`, `--effort`; gemini `-m`; codex `-m`, `-c model_reasoning_effort=…`; cursor `--model`, the effort as the model's suffix; the budget and a regime other than `auto` are spelled at claude alone, the effort everywhere but gemini |
| `session` | the identity of a session of the provider — the one its `answer()` returned —, judged ONCE at the engine's face (`conductor.adapters.session_of`): `None` OPENS a new session, which the provider keeps and names; a non-blank text RESUMES that one; anything else refuses `session-invalid`. pp creates, keeps and looks up no session: claude `--resume <id>`, codex `exec … resume <id>` (after the options of `exec`), gemini `--resume <id>`, cursor `--resume <id>`; no line ever carries `--no-session-persistence` |
| `workdir` | the MATERIAL the exchange works on — the clone a run edits, under the workspace —, judged ONCE at the engine's face (`conductor.adapters.material`): a mapping of `path` (where it stands, a path RELATIVE to the workspace, no `..`; the face reads no disk: whether it stands is the caller's business), `branch` and `base` (non-empty texts, optional — `agent/dev1/a1b2c3`, `main@1234abc`); anything else refuses `workdir-invalid`, naming the key. The face composes it the SAME for every provider, by no provider flag: the prompt opens on the head `[material <path> · branch <branch> · from <base> · console <console> -- reach the material by git -C and relative paths, never cd; the target's hooks are not in the clone]` (the segments a material does not name are absent), a blank line, then the prompt as given; `env` gains `PP_WORKDIR=<path>` and `PP_CONSOLE=<console>`, the console being `<workspace>/pp` (`pp.cmd` on Windows) by its absolute path — what a harness calls once its model has left the workspace by `cd`. The adapter receives the material as judged and changes nothing (the four write under their current directory already); one whose `launch` takes no `workdir` refuses `workdir-unsupported` by its name when a material is handed, and composes as before without one. `None`, the default, changes nothing: the lines of before, byte for byte. The git identity of the exchange is not the face's: the house's skill sets it in the environment |
| `argv` | the command line that plays ONE exchange and exits: the binary, the non-interactive flag, the system-prompt channel when the host has one by argument, the permission flag of the regime the policy names (none answers a question), the output format — and no prompt: claude and cursor read stdin without a prompt argument, codex names it by the last argument `-`, gemini reads stdin without `-p` |
| `stdin` | the text the skill writes on the process's standard input, then closes: the prompt as the face composed it — the material's head, a blank line, the prompt — whole, whatever its size |
| `env` | the variables to ADD to the launcher's environment: the receipt `PP_MARBLE=1` where the host carries the marble — claude and gemini by the environment, codex by its config (`shell_environment_policy`) and in `env` as data too (what `pp-agent` reads to carry the receipt on its own calls to the conductor), cursor carries no marble and gets no receipt —, `GEMINI_SYSTEM_MD=<marble>` for gemini, whose system prompt travels by a variable and not by an argument, and `PP_WORKDIR`/`PP_CONSOLE` when a material is handed (engine `0.1.0-beta.42`) |

`launch()` COMPOSES and never launches: it runs no process, waits for nothing,
reads no output — the engine keeps no clock and holds no process (CONDUCTION
§ The principal). The skill that calls it runs `argv` under `env`, writes
`stdin` on the process's standard input, waits, and reads the exit code;
`--harness <command>` lets the bench give a witness command in place of a
provider (the witness reads its prompt on stdin too). A provider name no adapter
carries refuses `provider-unknown`; an adapter that wires but composes no launch
refuses `launch-unsupported`; one whose launch renders anything but the three
elements `(argv, env, stdin)` refuses `launch-malformed`. The face `conductor.adapters.launch(provider, workspace, meta,
prompt, marble=None)` finds the adapter by its path as `wire` is found —
`adapters.load(name)` under `adapters.product_of(meta)`, the product checkout: the
running engine's own, or the `source:` an instance declares.

`marble` may be left out: the adapter then names the marble its own launcher
carries — `.sys/system.replace.md` when it stands, else the compiled marble
(claude) or the composition (gemini); codex and cursor read no marble at the call.
A marble handed wins. The policy of an exchange — the model, a budget, the
permission regime, the model's effort — travels by `policy`, spelled by the adapter
(engine `0.1.0-beta.26`; the regime since `0.1.0-beta.34`, the effort since
`0.1.0-beta.49`); a turn bound has no place (an
exchange is several harness turns: the budget bounds it), and a list of tools is
not a policy: the regime says how much the harness decides alone, not which tools
it holds.

Six constants beside the faces say what an adapter knows, read by the `agent` package and by the campaign
(`agent providers --json`, the cost of a launch, the budget cap of a run) through the engine's
`conductor.adapters.load`, never by the engine itself:

| Constant | What it holds |
|---|---|
| `SPELLS` | the policy's keys `launch()` spells -- claude `model`, `max_budget_usd`, `permissions`, `effort`; codex and cursor `model`, `effort`; gemini `model`; what is not listed refuses `policy-unsupported` at the launch |
| `MODELS` | the model names verified on a machine with that host -- claude's four; empty where none is verified yet (codex, gemini, cursor). A name absent from the list is never refused: it goes to the host as given |
| `COST` | the SCOPE of the `cost_usd` its `answer()` reads -- `"session"` (the session's cumul at that launch: claude's `total_cost_usd`), `"launch"` (that launch alone), or `None` (no cost read: codex, gemini, cursor). A caller reads a launch's cost in that scope and names no provider; a budget cap cannot be held where it is `None` (`budget-unmeasured` at `agent`) |
| `BINARY` | the binary a launch needs on the machine -- `"claude"`, `"codex"`, `"gemini"`, cursor's `"agent"`; `None` where the launch needs none (`model`: the interpreter on its harness). A caller asks it before it launches (`shutil.which`) and refuses `provider-missing` only when one is due and absent (the campaign, `tools/campaign/campaign.py`) |
| `CONTEXT_WINDOWS` | the context window of a model, in tokens, under every name `--model` takes for it (the id and the CLI's alias) -- what `agent stats` reads to say how full a run's context is. claude: the 1M models (fable 5.1, opus 5.5, sonnet 5.5, haiku 5.5; `haiku` at 200K, measured 2026-10-27), codex: `gpt-6.1-sol` 500 000 (its default in Codex), `gpt-5` and `gpt-5-codex` 272 000; gemini: the two pro at 1 048 576; cursor: none named (the names are not documented: `agent --list-models` says them); each value dated with its source in `wire.py` |
| `CAP` | the cap of a prompt in CHARACTERS whatever the model: the client's own bound -- codex refuses a turn over `1_048_576` characters (`MAX_USER_INPUT_TEXT_CHARS`, openai/codex #20742); cursor's default window of 200K gives `400_000`; `None` where nothing is known without a model (claude, gemini, model): the engine's floor holds |
| `CAPS` | the cap of a prompt in characters BY MODEL NAME, as `--model` receives it, derived in `wire.py` from `CONTEXT_WINDOWS` by named constants: `window x CHARS_PER_TOKEN (2.5) x SHARE (0.8)` -- claude 2 000 000 at 1M, 400 000 at 200K (the ~1.78x count of a piped prompt reported at anthropics/claude-code #92305 is not observed on 2.1.287: 703 212 tokens piped were read whole on 2026-10-29); codex `min(CAP, …)`: 1 000 000 for sol, 544 000 for gpt-5; gemini 2 097 152; cursor and model empty. The `agent` package puts the value on its marked calls as `PP_PROMPT_CAP` (`launcher_cap`): the outputs it serves at the prompt are whole up to it (agent 0.30.0) |

### The third face: `events()`

`events(line)` reads ONE line of the harness's standard output -- without its line break --
as the exchange plays, and renders the events it carries, each in the COMMON SCHEMA below; a
line that says nothing, or does not read, renders `[]`. Like `launch` and `answer`, it runs
nothing and reads no disk. It lets a reader show a launch as it plays -- the tools called,
what they gave back, the model's thought and words -- without knowing which provider plays it
(engine `0.1.0-beta.63`); and it is the ONE source of the model's text: no other face says it
(engine `0.1.0-beta.72`).

| kind | fields | what it is |
|---|---|---|
| `tool` | `id` (text), `name` (the tool's name at its host), `title` (its input on one line), `shell` (the command when the tool runs a shell command, `None` otherwise), `input` (the input as the host gives it, a mapping) | a call of a tool, as it leaves |
| `tool-result` | `id` (the call's), `content` (text), `error` (true or false) | what the tool gave back, as the model read it |
| `thinking` | `text` and/or `tokens` (an integer) | the model's thought: its text when the host gives it, what it counts of it otherwise |
| `words` | `text`, `delta` (true alone, absent otherwise) | words of the model during the launch, its last text included -- every text the model says, in order; `delta` marks a piece of a message the host streams in pieces: pieces that follow one another, no event between them, are one text |

The engine's face `conductor.adapters.events(provider, meta, line)` finds the adapter as
`answer` does and holds the schema: it drops a field the schema does not name, gives an
optional field its default (`title: ""`, `shell: None`, `input: {}`, `error: false`), and
refuses `events-malformed`, naming the adapter and the kind, for a kind outside the four, a
required field missing or of another type -- a blank `words` text among them --, a `delta` that
is no boolean, or a face that renders no list. An adapter without the face refuses
`events-unsupported`, at `events` and at `answer`: a host whose words nobody can read gives no
text. Each host, and whether a machine verified it:

| host | the stream `launch()` asks for | what `events()` reads | verified |
|---|---|---|---|
| claude | `--output-format stream-json --verbose`; `answer()` reads its last `result` line (one object still reads), its `result` text not read: the stream said it as a `text` block | `tool_use` -> `tool` (`shell` the `command` of a `Bash`), `tool_result` -> `tool-result`, a `thinking` block with text -> `thinking`, `system/thinking_tokens` -> `thinking` {tokens}, `text` -> `words`; a `thinking` block signed WITHOUT text (recent models, the text omitted) says nothing | **yes** -- claude 2.1.287 and Opus 5.5, 2026-10-09: `tests/adapters/streams/claude.jsonl`, the probe's two streams, the `system/init` line reduced to its stable fields |
| codex | `--json` (unchanged) | `command_execution` started -> `tool` (`shell` its `command`), completed -> `tool-result`; `mcp_tool_call` alike; a completed `file_change` -> `tool` and `tool-result`; `reasoning` -> `thinking` {text}; `agent_message` -> `words` | NO -- from its docs, `streams/codex.from-docs.jsonl` |
| gemini | `--output-format stream-json`; `answer()` reads the session from `init`, the error from `error` or a failed `result` (one object still reads) | `tool_use` -> `tool` (`shell` the `command` of `run_shell_command`), `tool_result` -> `tool-result`, an assistant `message` -> `words`, `delta` when the host says it | NO -- from its docs, `streams/gemini.from-docs.jsonl` |
| cursor | `--output-format stream-json`; `answer()` reads its last `result` line (one object still reads), its `result` text not read | a `tool_call` started -> `tool` (its name the call's key less `ToolCall`, `shell` the `command` of `shellToolCall`), completed -> `tool-result`; an `assistant` message's text -> `words` | NO -- from its docs, `streams/cursor.from-docs.jsonl` |
| model | its harness says one JSON object per line, `kind` among the four, the `result` line last; `answer()` reads that line (`cost_usd` 0, the session) | each line IS its event: `words`, `tool`, `tool-result`, `thinking` as the harness says them; the `result` line says nothing | **yes** -- the product's own harness, `tests/adapters/model-*.py` (2026-10-27) |

Above the face stands the engine's READER of a launch, `conductor.adapters.reader(provider, meta)`
(engine `0.2.0-beta.7`): `heard(line)` renders the events of one line through `events`, and the
`words` an adapter marks `delta` are HELD -- pieces that follow one another, no event between them --
and rendered as ONE `words` at the next event of another nature, at a whole `words`, or at `end()`,
owed once the launch is over. What the reader renders never carries `delta`: a launcher reads
whole words, the adapter stays a translation of one line, and the only host that streams in pieces,
gemini (one `message` `delta: true` per chunk of its SDK, the assistant never whole, read at
gemini-cli's code), is read like the others.

What a host does not verify on a machine may be wrong: the stream is the only source of the
model's text, so a misread stream costs the RESPONSE, not only the events -- the verification
is owed when the CLI of codex, gemini and cursor is installed.

## The effort

`effort` says how much the model reasons before it answers. pp has five words,
`low`, `medium`, `high`, `xhigh` and `max`, judged at the face; each adapter spells
them by its provider's own channel and maps them to its provider's own words.

| pp's word | claude `--effort` | codex `-c model_reasoning_effort="…"` | cursor `--model <model>-<suffix>` | gemini |
|---|---|---|---|---|
| `low` | `low` | `low` | `<model>-low` | `policy-unsupported` |
| `medium` | `medium` | `medium` | `<model>-medium` | `policy-unsupported` |
| `high` | `high` | `high` | `<model>-high` | `policy-unsupported` |
| `xhigh` | `xhigh` | `xhigh` | `<model>-xhigh` | `policy-unsupported` |
| `max` | `max` | `xhigh` (codex's highest) | `<model>-xhigh` | `policy-unsupported` |

- **claude** — `--effort <level>`, verified on this machine (`claude --help`, 2.1.287,
  2026-10-03): the five words are claude's own.
- **codex** — the config override `-c model_reasoning_effort="<value>"` at the call
  (values `minimal`, `low`, `medium`, `high`, `xhigh`); docs read on 2026-10-03, NOT
  verified on a machine (the CLI is absent here).
- **cursor** — the effort rides the model's NAME as its suffix (`gpt-5.5-high`), so an
  effort without `model` refuses `policy-unsupported`; read on the Cursor forum on
  2026-10-03, which also reports a defect: the CLI may drop the suffix and play
  `medium`. NOT verified on a machine.
- **gemini** — no flag carries it: the effort is a setting (`modelConfigs` →
  `generateContentConfig.thinkingConfig`, `thinkingLevel` for Gemini 3,
  `thinkingBudget` for 2.5, geminicli.com « Advanced Model Configuration », read on
  2026-10-03), never a flag of the call: `policy-unsupported` naming `effort`.

## The permission regime

`permissions` says what the harness may do without asking anyone — under `-p`
nobody is there to answer. Three words, the same for every provider; each
adapter spells them in its host's flags or refuses one by its name
(`policy-unsupported`). Without the key, the adapter plays `auto`.

| regime | what runs without asking | claude | gemini · codex · cursor |
|---|---|---|---|
| `auto` (the default) | what the harness itself judges safe — the mode of an interactive session | `--permission-mode auto --permission-prompts none` | their line of 2026-09-26: `--approval-mode yolo` · `--sandbox workspace-write --full-auto` · `--force` |
| `strict` | the rules the house's settings write (`Bash(./pp:*)`), nothing else: anything that would ask is denied | `--permission-mode dontAsk --permission-prompts none` | `policy-unsupported` — no stricter mode verified on a machine |
| `bypass` | everything, every check skipped | `--permission-mode bypassPermissions --permission-prompts none` | `policy-unsupported` — no mode verified on a machine |

What the claude modes do, seen on this machine (claude 2.1.283) and read in
its docs:

- **`dontAsk` refuses a heredoc.** Under `strict` the house's
  `Bash(./pp:*)` rule does NOT cover `./pp <key> - <<'EOF'` nor
  `cat <<'EOF' | ./pp <key> -`, and `Write` is denied (3 denials, essay S9,
  2026-09-27): an agent that must pipe its proof or write a file needs `auto`.
  A confined agent pays that price.
- **`auto` passed where `dontAsk` failed**: the same exchange, by hand, under
  `--permission-mode auto --permission-prompts none` — `permission_denials: []`,
  `Write` accepted (S9, 2026-09-27). Claude's own safety checks still run in
  the background.
- **`bypassPermissions` skips every check**, the writes to protected paths
  (`.git`, `.claude`) included; allow rules have no effect, deny rules still
  block. Under `-p` no warning dialog is shown. Claude refuses it when it runs
  as root or under `sudo` on Linux and macOS (outside a recognized sandbox),
  and under `--restricted`. It offers no protection against prompt
  injection: the docs keep it for containers and VMs without a network
  (<https://code.claude.com/docs/en/permission-modes>). Not played with a
  model here.

The lines of gemini, codex and cursor already approve every tool: they are
closer to `bypass` than to claude's `auto`. They stay the `auto` of this table
until a machine verifies what each mode does (their CLIs are absent here).

Why `(argv, env, stdin)` and not `argv` alone: a `env VAR=… cmd` at the head of
the argv is not portable (no `env` on Windows), and every launcher pp writes sets
a variable (`PP_MARBLE=1`) before the binary — the contract says it as data; and
the prompt leaves by stdin at the four since engine `0.1.0-beta.59`: a run its
principal conducts receives whole blocks in its prompt (a boot of 26-30 k
characters, a reading of a plan above 100 k), beyond the 128 KiB Linux allows one
argument. Codex, gemini and cursor read stdin by their docs (read 2026-09-26),
NOT verified on a machine; claude's `--help` (2.1.287, 2026-10-07) says the prompt
argument is optional and `-p` is « useful for pipes ».

`answer()` READS what the harness answered, in the output format `launch()`
chose, and runs nothing either -- no text: the model's text is the `words`
of `events()` (engine `0.1.0-beta.72`). `cost_usd` what the harness
reports (None when it reports none), `denials` the permissions it was denied,
`error` what it names (None on success; `unreadable` with its tail when no
reading parses the stdout), `session` the identity the provider gave. The
identity is OWED: a reading that carries none refuses `session-missing` at
the face, naming the provider and citing the error read or the stream's
tail — no answer without the session it belongs to. The face
`conductor.adapters.answer(provider, meta, stdout, stderr)` finds the adapter
as `launch` does and refuses `answer-unsupported` when it has no such face,
`events-unsupported` when it has no `events` face (engine `0.1.0-beta.27`; the
session since `0.1.0-beta.30`; `events-unsupported` since `0.1.0-beta.72`); the
skill `pp-agent` hands it the streams it captured and keeps the reading, with
the words of every launch and their composition, at the house's `responses.jsonl`.

## The four harnesses, one exchange each

| | claude | codex | gemini | cursor |
|---|---|---|---|---|
| **status** | **verified** — claude 2.1.270, `claude -p …` played on a `mktemp -d` on 2026-09-26 | not verified — docs read 2026-09-26 | not verified — docs read 2026-09-26 | not verified — docs read 2026-09-26 |
| **binary, mode** | `claude -p` (`--print`) | `codex exec` | `gemini -p` (`--prompt`) | `agent -p` (`--print`; the docs name the binary `agent`, not `cursor-agent`) |
| **prompt** | argument or stdin; `--input-format text\|stream-json` — `launch()` gives no argument: stdin, `text` | argument or stdin (`codex exec -`) — `launch()` ends the line on `-`: stdin | `-p <text>` (appended to piped stdin); `-i` to continue interactive — `launch()` gives no `-p`: stdin alone (NOT verified) | argument or stdin — `launch()` gives no argument: stdin (NOT verified) |
| **system prompt** | APPEND: `--append-system-prompt <text>` / `--append-system-prompt-file <path>`; REPLACE: `--system-prompt` / `--system-prompt-file` (the `-file` forms are accepted but not listed by `--help`) | APPEND: `developer_instructions` at the project's `.codex/config.toml` (already written by `-codex`; applies to a TRUSTED project only); REPLACE: `model_instructions_file` | REPLACE only, by the variable `GEMINI_SYSTEM_MD=<path>` — no flag | none — rules, `AGENTS.md`, `CLAUDE.md` read from the workspace (recall) |
| **permissions** | `--permission-mode acceptEdits\|auto\|bypassPermissions\|manual\|dontAsk\|plan`, `--permission-prompts host\|none` (`none`: anything that would prompt is denied), `--allowedTools`, `--disallowedTools`, `--tools`, `--dangerously-skip-permissions`, `--restricted` | `--sandbox read-only\|workspace-write\|danger-full-access`, `-a/--ask-for-approval`, `--full-auto`, `--dangerously-bypass-approvals-and-sandbox` | `--approval-mode default\|auto_edit\|yolo\|plan` (`--yolo`, `--allowed-tools` deprecated) | `--force` (alias `--yolo`), `--approve-mcps`; full write access in non-interactive mode |
| **output** | `--output-format text\|json\|stream-json`; `--json-schema`; `--verbose` -- `launch()` asks `stream-json --verbose` | `--json` (JSONL), `-o/--output-last-message <path>`, `--output-schema`; progress on stderr, final message on stdout | `--output-format text\|json\|stream-json` | `--output-format text\|json\|stream-json` |
| **limits** | `--max-budget-usd <amount>`; `--max-turns <n>` accepted (not listed by `--help` 2.1.270) | none documented | a turn limit exists (exit 53); no flag documented | none documented |
| **policy spelled by `launch()`** | `--model <m>`, `--max-budget-usd <n>`, `--permission-mode auto\|dontAsk\|bypassPermissions` from `permissions` (`auto` without it), `--effort <e>` | `-m <m>`, `-c model_reasoning_effort="<e>"`; a budget, or `permissions` other than `auto`, refuses `policy-unsupported` | `-m <m>`; a budget, an effort, or `permissions` other than `auto`, refuses `policy-unsupported` | `--model <m>`, the effort as its suffix (`--model <m>-<e>`, an effort without a model refused); a budget, or `permissions` other than `auto`, refuses `policy-unsupported` |
| **wiring handed by `launch()`** | `--settings <wiring>/.claude/settings.json` when the file stands — whether `permissions.allow` is read from it under `-p` is NOT written in the docs: verify with a real call (the batch's gate) | nothing: `--full-auto` needs no allowlist | nothing: `--approval-mode yolo` needs no allowlist | nothing: `--force` needs no allowlist |
| **answer read by `answer()`** (no text: the words of `events()`) | the stream's last `result` line (one object still reads): `total_cost_usd`, `permission_denials`, `session_id`; `is_error` names `subtype` as the error | the JSONL: `turn.failed` names the error; the session the `thread_id` of `thread.started`; no cost, no denial | the stream: the session of `init`, the error of `error` or a failed `result` -- one object still reads (`error`, `session_id`): NOT verified; no session refuses `session-missing` | the stream's last `result` line (one object still reads): `session_id` (docs: `cursor.com/docs/cli/reference/output-format`); `is_error` names `subtype`; no cost, no denial: NOT verified |
| **exit codes** | `0` success; `1` failure or limit reached — verified: not logged in → 1, budget exhausted → 1 (`subtype: error_max_budget_usd`), success → 0 | not documented | `0` · `1` error · `42` input error · `53` turn limit | not documented |
| **resume** | `-r/--resume <id>`, `-c/--continue`, `--session-id <uuid>`, `--fork-session`; `--no-session-persistence` to keep nothing | `codex exec resume --last \| <id>`; `--ephemeral` to keep nothing | `--resume/-r latest\|<id>` | `--resume [chat id]` |
| **session spelled by `launch()`** | open: no resume flag, the session kept; resume: `--resume <id>`, the marble and `PP_MARBLE=1` as at the opening | open: as before; resume: `codex exec <options> resume <id> -` — nothing more: the config carries the marble | open: as before; resume: `--resume <id>`, `GEMINI_SYSTEM_MD` and `PP_MARBLE=1` as at the opening | open: as before; resume: `--resume <id>` — no channel, no receipt: the session's history carries the standing rules |
| **isolation** | `--bare`: no hooks, no `CLAUDE.md` discovery, no OAuth — **auth is `ANTHROPIC_API_KEY` alone** (verified: a Max login answers `Not logged in`, exit 1) | `--ignore-user-config`, `--ignore-rules`, `--skip-git-repo-check` | `--include-directories` | `--workspace <path>`, `--api-key` / `CURSOR_API_KEY` |
| **wired in addition** | the receipt: `env.PP_MARBLE = "1"` at `.claude/settings.json` (a fresh file alone), the one channel of the editor's extension; `Bash(./pp:*)` there covers the console under every regime; the other tools follow the regime `permissions` names | nothing to write — but the marble applies to a TRUSTED project only, and how a headless run trusts its workspace is not documented (discrepancy, see the codex README) | nothing: the launch sets the same variable `gemini-pp` sets; gemini must be on PATH at wiring (the baseline dump) | nothing: the `terminalAllowlist` prefix and the doors serve |

The exit codes pp reads are the HARNESS's: they say whether the process played,
not whether the run parked — that, the skill reads at the run
(`records/reports.jsonl`, the trace).

## What the claude verification showed

Four calls on a `mktemp -d`, a three-line witness marble
(`--append-system-prompt-file marble.md`), `--permission-mode dontAsk
--permission-prompts none --output-format json --no-session-persistence`, the
directory removed after; the operator's login is claude.ai (subscription max),
costs are LIST prices reported by the CLI:

| call | flags added | result |
|---|---|---|
| 1 | `--bare --max-budget-usd 0.10` | `"result":"Not logged in · Please run /login"`, `is_error: true`, exit 1, cost 0 — `--bare` never reads OAuth |
| 2 | `--bare --max-budget-usd 0.10 --max-turns 1` | same; the flag `--max-turns` is ACCEPTED by 2.1.270 though `--help` does not list it |
| 3 | `--max-budget-usd 0.10 --max-turns 1` (default model) | `subtype: error_max_budget_usd`, `terminal_reason: budget_exhausted`, exit 1, `total_cost_usd: 0.223` — the model's own system prompt (10 975 cache-creation tokens) costs more than the budget; no `result` text is returned |
| 4 | `--model haiku --max-budget-usd 0.10 --max-turns 1` | `"result":"pong"`, `is_error: false`, exit 0, `total_cost_usd: 0.045`, `duration_ms: 2398` |

Two lessons for the launch: a budget under the price of one exchange at list
cost refuses the whole exchange (size `--max-budget-usd` from the model, or
leave it out); `--bare` fits an agent that holds an API key, not a run on the
operator's login.

## The fifth provider: the modelled LLM

`adapters/model/` is a provider whose harness is a script of the product, not a model: it reads a
block by its structure and the engine's constants, decides by the data of the conduction model
(`adapters/model/semantics.py`) and acts as a conforming agent does --
or misses exactly once, by the VARIANT its policy's `model` key names (`conform`, `wrong-form`,
`wrong-channel`, `missing-code`, `bare-call`, `empty`). It wires nothing, spells no budget, no effort
and no regime (`policy-unsupported`), costs 0 (`COST` `"launch"`), opens no network, and reads neither
`.pp/.sys` nor a trace: a launch names it by `--provider model`. Its story, its loop and its variants:
[`adapters/model/README.md`](model/README.md).

## External references

- claude: <https://code.claude.com/docs/en/cli-reference> · <https://code.claude.com/docs/en/permission-modes>
- codex: <https://learn.chatgpt.com/docs/non-interactive-mode> · <https://learn.chatgpt.com/docs/config-file/config-reference>
- gemini: <https://geminicli.com/docs/cli/headless/> · <https://geminicli.com/docs/cli/cli-reference/>
- cursor: <https://cursor.com/docs/cli/using> · <https://cursor.com/docs/cli/reference/parameters>
