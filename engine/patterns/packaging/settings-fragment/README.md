# settings-fragment — the keys your package lets the operator tune

## What you write

In your package, `settings/SETTINGS.md`: a front matter naming the package, one line per key with
its default, the type of each key, and the levels of effort where its value differs; under it, the
section the operator reads about those keys.

    ---
    name: SETTINGS
    kind: fragment
    package: keeper
    description: keeper's keys
    keeper_care: asked
    keeper_depth: 2
    types: |
      keeper_care   one_of[asked|total]
      keeper_depth  natural
    effort: |
      keeper_depth  light=1 medium=2 full=3
    ---
    ## Keeper — how far the keeper looks

    - `keeper_care` — …

- Every key wears your package's name as its prefix, `<package>_`: the prefix is the ownership.
- `types` — `flag`, `natural`, `positive`, `one_of[a|b]`, `piped` or `free`.
- `effort` (optional) — a value per level, `light`, `medium`, `full`: the operator's
  `conduction_effort` presets your key the way it presets the engine's.

A script of your package reads and writes a key through pp's face alone:

    import conductor
    depth = conductor.settings.of(meta).of_package("keeper_depth")
    previous = conductor.settings.write(meta, "keeper_care", "total")

## What you get

- The instance's `SETTINGS.md` is composed from the engine's keys and every package's fragment:
  your keys under their own group, your section in the body, the packages in the order of
  `requires`. Each install, add and upgrade composes it again; the operator's values are kept and
  composing twice changes nothing.
- A key the operator leaves out plays its default; a value is read parsed by its type, and the
  effort's presets arrive typed too.
- `write` changes one line and nothing else, adds the line before the closing `---` when it is
  absent, and returns the previous value (empty when there was none). What the reading would
  refuse, the writing refuses, the file left byte for byte.
- Removing your package leaves its keys under `# ---- unowned ----`, the operator's values intact;
  adding it back brings them home.

## When to use it

- Your package has a behavior the operator should choose — a level of care, a depth, a day of the
  week — and a document or a script reads it (`@SETTINGS.keeper_care`, see `context/tags`).
- A value only your own record needs stays in that record (`packaging/writer-skill`).

## What refuses

- At the reading of the fragments: a key without the prefix, a type the engine does not know, a
  `types` line naming no key, an effort level other than `light`, `medium`, `full` refuse
  `settings-fragment-invalid`.
- At the reading of `SETTINGS.md`, and so at a `write`: a value its type refuses, a key no fragment
  of the instance owns refuse `settings-invalid`.

## The demonstration

- `manifests/keeper.yaml`, `fragments/keeper.md` — a package with two typed keys, one preset by
  the effort.
- `manifests/loose.yaml`, `fragments/loose.md` — a key without its prefix.
- `manifests/levels.yaml`, `fragments/levels.md` — an effort level the engine does not know.

A fragment lives in a package as `settings/SETTINGS.md`; the demonstration names each by its
package, and the test places it there.

## The test

`tests/patterns/packaging/settings-fragment.py` pins keeper with its fragment and composes: the
group, the section, a second sync moving nothing; then writes through the face — one line moves,
the value kept by the next sync, a depth that is no number and an unknown key refused with the
bytes kept, an absent key added — and reads the depth under the three efforts. It pins loose and
levels (`settings-fragment-invalid`), then installs keeper from a source, sets a value, removes
and adds the package: the key waits under `unowned` and comes home.
