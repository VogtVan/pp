# system-fragment — your package's words in the standing orders

## What you write

In your package, a `system/` folder with one file, `system/SYSTEM.md`: what every run of the
instance must know of your package.

It is a document: a front matter, then the text the run receives.

    ---
    name: SYSTEM
    kind: doc
    description: herald's word in the standing orders
    ---

    ## The herald

    Herald orders hold: every report the herald gives names its source.

The operator of an instance may write one more file at the instance's root, `SYSTEM_PROMPT.md`,
whose body leads the standing orders a harness pins into its own system prompt; it plays only under
`override: true` in its front matter.

## What you get

- Every build compiles the standing orders once, into `.sys/system.md`, from every `SYSTEM.md`. Every
  run is served them at its opening and again after a declared compaction.
- The sections come in a fixed order: the engine's orders and its card, then the base's section,
  then each package's, in the order of `requires` — a package after the packages it requires.
- Only that name is read: any other file under `system/` stays the package's own, and a file
  without a body adds nothing.
- A package the operator switches off (`package.<name>: off`) leaves the standing orders, and the
  catalog, at the next boot; switched on, it comes back.
- `SYSTEM_PROMPT.md` under `override: true` gives the harness a version of the standing orders that
  opens on its body (`.sys/system.replace.md`); without it, or once the operator sets it to `false`, that version is withdrawn.

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

- `manifests/herald.yaml`, `systems/herald.md`, `procs/HERALD.md` — a package with its file and one
  step the catalog lists.
- `manifests/crier.yaml`, `systems/crier.md` — a package that requires herald: its section
  comes after herald's.
- `manifests/hush.yaml`, `systems/hush.md`, `systems/hush.notes.md` — an empty file and a file of
  another name: the standing orders stay as they were.
- `prompts/prose.md`, `prompts/closed.md`, `prompts/granted.md` — the instance's `SYSTEM_PROMPT.md`
  as plain prose, under `override: false`, under `override: true`.

A package's file lives in its `system/` folder as `SYSTEM.md`; the demonstration names it by its
package (`<package>.md`), a file of another name by its package and its part (`hush.notes.md`, placed
as `SYSTEM.NOTES.md`), and the test places them there.

## The test

`tests/patterns/packaging/system-fragment.py` installs crier, which pulls herald, and reads the one
compilation: the order of the sections; adds hush and finds it unchanged; opens one run and compacts
it, the standing orders served both times; lays the three prompts in turn; then switches herald off and boots twice.
