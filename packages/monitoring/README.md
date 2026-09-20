# monitoring

> **Experimental package.** Its measurement formats and user-facing behavior
> may change between versions.
>
> **Current version:** `0.1.0`

`monitoring` is a package for [Procedural Prompting](../../README.md). It turns
the trace the core already records into an analysis of the conduction: context
volume by function and package, engine activity, agent time, scenario coverage and
comparable campaign reports.

The package adds no instrumentation to the engine. It reads the weights and named
events already present in run traces, and adds an optional turn-end stamp so the
otherwise invisible tail of the agent's work can be measured.

## Role

A conducted workflow can be correct and still be heavier, slower or less stable than
it needs to be. `monitoring` makes those costs observable without asking the agent to
estimate them from memory or adding measurement prose to the procedures under study.

It provides a method for answering five recurring questions:

- Which readings, bodies, constraints and scaffolding account for the context served?
- Which package and function own that volume?
- Where does agent time fall across the turns of a real conducted session?
- Did a scenario campaign exercise every observable feature it set out to cover?
- Which setting offers a measured lever, and can the result be reproduced later?

## Features

### Engine-native metrics — measure without changing the subject

Every rendered block already records exact character counts for constraints,
payloads, options, instructions, framing and the whole output. Served subjects are
itemized, and provider, sink and gesture events name the work the engine performed.
`monitoring` reads those facts and attributes them to their function and owning
package.

Token counts remain estimates rather than invented precision. Reports mark them with
`~` and keep the exact character counts beside them. The estimator uses the standard
library only, with no network or tokenizer dependency.

### Playbooks — conduct repeatable scenarios

A playbook is an operator-owned markdown file. It names the package composition, then
defines ordered sessions with optional fixtures and a table of operator gestures.
Each session gets its own run, and each gesture becomes one exchange in table order.

Campaigns run on a derived disposable repository, never on the measured instance.
The expected result remains a human or agent judgment: the runner reproduces the
scenario and collects evidence, but does not silently decide whether the expectation
was met.

### Reports — show cost by function and by turn

Every report renders two complementary views. The by-function table totals volume,
agent time, engine time and the governing setting for each subject. The by-turn table
keeps one row per stamped turn so a cost hidden by an average can be located in the
operator exchange that caused it.

The report states the measured package versions, model and effort level, settings and
fusion regime before interpreting the figures. When the trace cannot support a finer
resolution, the report says so rather than assigning time to steps it cannot separate.

### Turn-end capture — close the time window

The core can measure agent work between one block and the next call. Measuring the
answer after the final block also needs the moment the turn ended. With Claude Code,
the package supplies a Stop-hook integration that stamps that boundary.

`monitoring_capture` is `false` by default. Turning it on enables stamps immediately;
turning it off makes the declared command silent while leaving the hook in place. If
several runs are live, the stamp targets the most recently written trace and is
therefore indicative rather than attributed with certainty.

### Campaign archives — keep the evidence reproducible

A complete campaign keeps the report, the deterministic conduction-and-chat record,
the raw traces, transcripts and played settings together. The scenario book and its
coverage register stay beside the witness batch that owns the campaign.

An archived trace set can be analysed again later. Missing transcripts or settings
are reported as missing evidence; they are never guessed. A deviation discovered by
the campaign reopens the faulty work instead of changing the expected result to make
the campaign pass.

## Installation

`monitoring` requires the `kit`; the installer pulls it automatically.

For a new workspace:

```sh
uv run procedural-prompting/engine/pp.py -install <workspace> monitoring -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add monitoring
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start). The core's trace measurements are already
available; enable `monitoring_capture` only for sessions whose turn-end time should be
included.

## Quick start

Start with a small playbook that names the composition and one deterministic session:

```markdown
composition: kit steering

## S1 — the steering surface

| id | gesture | expected |
|---|---|---|
| S1.01 | Track the documentation as an initiative. | NEXT shows the initiative. |
| S1.02 | End this session. | The turn closes normally. |
```

For a timed Claude Code campaign, set the package switch in `.pp/SETTINGS.md`:

```yaml
monitoring_capture: true
```

Then ask the conducted agent to set up the analysis, wire the Claude turn-end link,
run the playbook on a disposable repository and render the report. Review both tables:
the function view explains the total distribution, while the turn view points to the
specific exchange worth simplifying.

Keep the report with its traces, transcripts, settings and deterministic session
record when the measurement will be compared after a change. Turn capture off when
the campaign is over; the hook may remain installed.
