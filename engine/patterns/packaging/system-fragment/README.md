# system-fragment — your package's words in the standing orders

## What you write

In your package, a `system/` folder with one or two files:

- `system/SYSTEM.COMMON.md` — what every run of the instance must know of your package, whoever
  conducts it: the model, or its principal, served each output in turn.
- `system/SYSTEM.CONDUCT.md` — what the model must know to make pp advance when it conducts the run
  itself.

Each is a document: a front matter, then the text the run receives.

    ---
    name: SYSTEM.COMMON
    kind: doc
    description: herald's word in the standing orders
    ---

    ## The herald

    Herald orders hold: every report the herald gives names its source.

The operator of an instance may write one more file at the instance's root, `SYSTEM_PROMPT.md`,
whose body leads the standing orders a harness pins into its own system prompt; it plays only under
`override: true` in its front matter.

## What you get

- Every build compiles the standing orders twice, one per conduction: for a run the model conducts,
  every `SYSTEM.COMMON.md` then every `SYSTEM.CONDUCT.md`; for a run its principal conducts, the
  `SYSTEM.COMMON.md` files alone. Each run is served the one of its conduction, at its opening and
  again after a declared compaction.
- The sections come in a fixed order: the engine's orders and its card, then the base's section,
  then each package's, in the order of `requires` — a package after the packages it requires.
- Only those two names are read: any other file under `system/` stays the package's own, and a file
  without a body adds nothing.
- A package the operator switches off (`package.<name>: off`) leaves the standing orders, and the
  catalog, at the next boot; switched on, it comes back.
- `SYSTEM_PROMPT.md` under `override: true` gives the harness a version of each compilation that
  opens on its body; without it, or once the operator sets it to `false`, that version is withdrawn.

## When to use it

- A rule your package needs in force in every run, before any of its documents is read — who the
  principal is for the package, a word every exchange must respect.
- A rule that binds one step goes to that document's laws instead (`rules/laws`); a text the agent
  reads when a step needs it goes to a served document (`context/serve`).

## What refuses

- Nothing refuses: a missing folder, a missing file or an empty one compile without them.
- The lint says it when `SYSTEM_PROMPT.md` stands without `override: true`: the file then has no
  effect.

## The demonstration

- `manifests/herald.yaml`, `systems/herald.common.md`, `systems/herald.conduct.md`,
  `procs/HERALD.md` — a package with its two files and one step the catalog lists.
- `manifests/crier.yaml`, `systems/crier.common.md` — a package that requires herald: its section
  comes after herald's.
- `manifests/hush.yaml`, `systems/hush.conduct.md`, `systems/hush.notes.md` — an empty file and a
  file of another name: both compilations stay as they were.
- `prompts/prose.md`, `prompts/closed.md`, `prompts/granted.md` — the instance's `SYSTEM_PROMPT.md`
  as plain prose, under `override: false`, under `override: true`.

A package's file lives in its `system/` folder as `SYSTEM.COMMON.md` or `SYSTEM.CONDUCT.md`; the
demonstration names each by its package and its part (`<package>.common.md`,
`<package>.conduct.md`), and the test places it there.

## The test

`tests/patterns/packaging/system-fragment.py` installs crier, which pulls herald, and reads the two
compilations: the CONDUCT lines in the model's alone, the order of the sections;
adds hush and finds both unchanged; opens one run under each conduction and compacts the
principal's; lays the three prompts in turn; then switches herald off and boots twice.
