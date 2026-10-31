# The patterns of the engine

A PATTERN is something you write in a proc, a document or a package, and the effect pp gives
you for it. Each pattern has its own folder: a README (what you write, what you get, when to
use it, what refuses), the demonstration documents it plays, and a test on the bench. This
page lists them by drawer, one line each, then the keys of the front matter and of SETTINGS,
each sent to the pattern that teaches it. The detail lives in the pattern's README.

## steps — what you ask the agent, step by step

| pattern | you write | you get |
|---|---|---|
| [proc](steps/proc/README.md) | `proc:`, one step per line | a document pp plays step by step |
| [work](steps/work/README.md) | `WORK` | a free piece of work, closed on its result |
| [infer](steps/infer/README.md) | `INFER` | one production, in the form the document names |
| [pick](steps/pick/README.md) | `PICK <name>` after a list | one value chosen from that list |

## control-flow — in which order, with which branches and loops, when it stops

| pattern | you write | you get |
|---|---|---|
| [root](control-flow/root/README.md) | nothing | the passage ends when the root runs out of steps; the next message replays it |
| [open](control-flow/open/README.md) | `OPEN <doc>`, or `-open` by the agent | a space the messages stay in, until `-close` |
| [section-break](control-flow/section-break/README.md) | `§`, `# ` | an output that ends at the step you choose; a comment line |
| [due](control-flow/due/README.md) | `^ @Doc.field` after a step | the step plays only when the value says so |
| [fusion](control-flow/fusion/README.md) | `fusion:` | how many steps one output carries |
| [next](control-flow/next/README.md) | `next:`, `choose:`, `decide:` | the document that follows when this one leaves |
| [cycle](control-flow/cycle/README.md) | `cycle: <token>` | a loop over the elements a skill renders |
| [field](control-flow/field/README.md) | `field:` | a loop over a list the agent writes |

## composition — how procs are put together, and how their laws combine

| pattern | you write | you get |
|---|---|---|
| [call](composition/call/README.md) | `CALL <doc>` | another document played as a step of yours, its laws in force while it plays |
| [hook](composition/hook/README.md) | `HOOK <socket>`, `attach: <socket>` | other procs played at a point of yours |
| [initialize](composition/initialize/README.md) | `attach:` or `mount:` at `<proc>.initialize` | played once when the proc starts, held while it lives |
| [mount](composition/mount/README.md) | `mount: <socket>`, `mounts:`, a skill's `::mount` | a document's laws and readings at a step, without a step |
| [qualifiers](composition/qualifiers/README.md) | `when:`, `order:` | when a contributor plays, and in which rank |
| [overlay](composition/overlay/README.md) | a document of the same name, nearer | your deltas on a document you do not own |
| [door](composition/door/README.md) | `tools: <PROC>` | a proc the agent opens by its name |
| [adoption](composition/adoption/README.md) | `tools: +<name>` | a skill or a proc your instance does not carry, offered |

## context — what the agent reads, when, and from where

| pattern | you write | you get |
|---|---|---|
| [doc](context/doc/README.md) | `kind: doc` | a document read, never played |
| [serve](context/serve/README.md) | `serve:`, `SERVE` | readings the tool brings to a step |
| [addressing](context/addressing/README.md) | a document's name | where that name leads |
| [material](context/material/README.md) | `material:`, a row `@<name>` | a row read from another tree |
| [tags](context/tags/README.md) | `@Doc.field`, `@SETTINGS.<key>` | a value of another document cited in a text |
| [payload](context/payload/README.md) | `provides:`, `with:`, `payloads:` | a skill's output served as a section |

## rules — what the agent must hold, and how it is checked

| pattern | you write | you get |
|---|---|---|
| [laws](rules/laws/README.md) | `constraints.production:`, `constraints.behavior:` | laws in force at every step of the frame |
| [prove](rules/prove/README.md) | `PROVE` | the work checked against its laws before it leaves |
| [repair](rules/repair/README.md) | nothing | a missed step named and asked again, within a bound |

## outputs — what form a production takes, and where it goes

| pattern | you write | you get |
|---|---|---|
| [formats](outputs/formats/README.md) | `output:`, `formats:` | the form of a production, and its channel |
| [input](outputs/input/README.md) | `input:` | a document that opens on another's production |
| [sink](outputs/sink/README.md) | `sink: <skill>` | a production handed to a skill |

## automation — the deterministic code you plug around the agent

| pattern | you write | you get |
|---|---|---|
| [exec](automation/exec/README.md) | `exec: <verb>` | a script played when a document enters |
| [cadences](automation/cadences/README.md) | `contributes: cadences` | a document played when its week is due |
| [checks-and-signals](automation/checks-and-signals/README.md) | `contributes: checks`, `events` | what your package tells the instance's bus |
| [commands](automation/commands/README.md) | `contributes: commands` | a console verb of your package |

## packaging — how a set of procs is delivered and tuned

| pattern | you write | you get |
|---|---|---|
| [manifest](packaging/manifest/README.md) | `package.yaml` | what a package is, and what it needs |
| [base](packaging/base/README.md) | a base package | the package an instance stands on |
| [sockets](packaging/sockets/README.md) | `contributes: sockets` | a point your package opens for others |
| [settings-fragment](packaging/settings-fragment/README.md) | `settings/SETTINGS.md` | the keys your package lets the operator tune |
| [package-switch](packaging/package-switch/README.md) | `package.<name>: off` | a package out of the play, still installed |
| [system-fragment](packaging/system-fragment/README.md) | `system/`, `override:` | your package's words in the standing orders |
| [package-member](packaging/package-member/README.md) | `user/` | the files your package places at the instance's root |
| [seed](packaging/seed/README.md) | `seed/` | the records your package lays down once |
| [writer-skill](packaging/writer-skill/README.md) | a skill and its record | one script, the one writer of that record |
| [run-context](packaging/run-context/README.md) | a skill your package launches | the script knows the run that started it |
| [proc-folders](packaging/proc-folders/README.md) | `procs/<folder>/` | your procs shelved in folders, their names unchanged |

## The front matter, key by key

| key | what it declares | pattern |
|---|---|---|
| `name:` | the document's identity | [proc](steps/proc/README.md) |
| `kind:` | `proc` or `doc` | [doc](context/doc/README.md) |
| `description:` | the catalogue line of tools | [door](composition/door/README.md) |
| `proc:` | the steps, one per line | [proc](steps/proc/README.md) |
| `output:` | the form of the production | [formats](outputs/formats/README.md) |
| `formats:` | forms of your own | [formats](outputs/formats/README.md) |
| `input:` | the production this document opens on | [input](outputs/input/README.md) |
| `sink:` | the skill the production goes to | [sink](outputs/sink/README.md) |
| `serve:` | the readings, in sections | [serve](context/serve/README.md) |
| `material:` | the tree a row reads from | [material](context/material/README.md) |
| `provides:` | the token this document serves | [payload](context/payload/README.md) |
| `with:` | the skill that renders the token | [payload](context/payload/README.md) |
| `payloads:` | the tokens this document consumes | [payload](context/payload/README.md) |
| `tools:` | the offers of the frame | [door](composition/door/README.md) |
| `constraints.production:` | laws on what the agent makes | [laws](rules/laws/README.md) |
| `constraints.behavior:` | laws on what the agent does | [laws](rules/laws/README.md) |
| `attach:` | the socket that calls this document | [hook](composition/hook/README.md) |
| `mount:` | the socket this document enters | [mount](composition/mount/README.md) |
| `mounts:` | the documents mounted at your sockets | [mount](composition/mount/README.md) |
| `when:` | the guard of a contributor | [qualifiers](composition/qualifiers/README.md) |
| `order:` | the rank of a contributor | [qualifiers](composition/qualifiers/README.md) |
| `exec:` | the script played at each entry | [exec](automation/exec/README.md) |
| `cycle:` | the token a loop turns on | [cycle](control-flow/cycle/README.md) |
| `field:` | the list the agent writes for a loop | [field](control-flow/field/README.md) |
| `next:` | the documents that may follow | [next](control-flow/next/README.md) |
| `choose:` | the agent decides which follows | [next](control-flow/next/README.md) |
| `decide:` | a skill decides which follows | [next](control-flow/next/README.md) |
| `fusion:` | this document's pace | [fusion](control-flow/fusion/README.md) |
| `override:` | a system file that replaces | [system-fragment](packaging/system-fragment/README.md) |

## package.yaml, key by key

| key | what it declares | pattern |
|---|---|---|
| `requires` | the packages this one needs | [manifest](packaging/manifest/README.md) |
| `optional` | the packages it uses when present | [manifest](packaging/manifest/README.md) |
| `contributes: sockets` | points opened for others | [sockets](packaging/sockets/README.md) |
| `contributes: cadences` | documents played on a due week | [cadences](automation/cadences/README.md) |
| `contributes: checks` | predicates read at the boot | [checks-and-signals](automation/checks-and-signals/README.md) |
| `contributes: events` | signals, vectors, sectors | [checks-and-signals](automation/checks-and-signals/README.md) |
| `contributes: commands` | console verbs | [commands](automation/commands/README.md) |

## SETTINGS, key by key

| key | what it tunes | pattern |
|---|---|---|
| `instructions_fusion` | how many steps an output carries | [fusion](control-flow/fusion/README.md) |
| `verbatim_constraints` | a law's text at every block, or its code after the first | [laws](rules/laws/README.md) |
| `proc_body_serve` | a called body at every CALL, or once | [serve](context/serve/README.md) |
| `work_repairs_allowed` | the repairs before the operator takes over | [repair](rules/repair/README.md) |
| `package.<name>` | a package on or off | [package-switch](packaging/package-switch/README.md) |
| `<package>_<key>` | a package's own keys | [settings-fragment](packaging/settings-fragment/README.md) |
| `conduction_effort` | the preset that weighs the keys above | [settings-fragment](packaging/settings-fragment/README.md) |
| `max_harness_tool_output` | the size of one tool output at the host | `docs/reference/block.md` |
| `conduction` | which outputs a principal's run answers at once | `docs/reference/block.md` |
| `capabilities` | the base's catalogue played at the boot | `docs/reference/front-matter.md` |
| `capture_prompt` | the base asks for the next message itself | `docs/reference/front-matter.md` |

## What pp guarantees

- **Enforced**: what you declare in a front matter or a `proc:` -- the readings served, the
  documents hosted, the laws re-said at every block, the offers, the choice of a `PICK` and the
  form of a production a step consumes, the proof at a `PROVE`, the repair bound, the due steps,
  the closings -- `▶ CONTINUE` and the call owed, `▶ AWAIT` when the principal's message is
  awaited, `▶ MORE` when an output continues at the agent's next turn, none when a free step
  ends on the agent's word. A value that breaks a rule refuses before anything plays.
- **Framed, never guaranteed**: what the agent produces at a `WORK` or an `INFER` nothing
  consumes -- the laws frame it, the proof checks it.
- **The agent's conventions**, said by the standing orders: `#BLOCKED <reason>` when a form
  cannot be served, and calling pp back at every transition.
- **The operator's**: the message (the ask), the approvals, and the files they tune between
  two exchanges.
