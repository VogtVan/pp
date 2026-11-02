# seed — the records your package lays down once

## What you write

In your package, a `seed/` folder: each file in it is a record your package keeps — most often an
empty journal, or one with a first line — copied into the instance's records under the same name.

    seed/
      ledger.jsonl        {"entry": "the ledger opens"}

Nothing is declared in the manifest: the folder is the declaration.

## What you get

- At the install, and when the operator adds your package later, each file of `seed/` is copied into
  the instance's records — only where no record of that name stands yet.
- From then on the records are the instance's: what your scripts or the operator write in them is
  kept byte for byte through every sync, repair (`./pp doctor`), upgrade at constant versions and
  `add` of another package.
- Removing your package leaves its records where they are: adding it back finds them.
- An instance that borrows a house's machine gets your seeds the same way.

## When to use it

- Your package has a record its skills read from the first call on, and an empty one is a valid
  state: a journal, a register, a list of entries.
- A value the operator tunes is a key of your settings (`packaging/settings-fragment`); a record
  written by one script under lock is the writer skill (`packaging/writer-skill`).

## What refuses

- At the reading of the manifest: a seed declared under `contributes:` (`resources: {seed: …}`)
  refuses `contribution-kind-unknown` — `resources` is no contribution — and nothing is written.

## The demonstration

- `manifests/ledger.yaml`, `seeds/ledger/ledger.jsonl` — a package with one seeded record.
- `manifests/plain.yaml` — a package without `seed/`.
- `manifests/declared.yaml` — a package that declares its seed as a contribution.

A package's records live in its `seed/` folder; the demonstration names each folder by its package
(`seeds/<package>/`), and the test places it there.

## The test

`tests/patterns/packaging/seed.py` installs ledger and finds its record; edits it, adds plain,
syncs and upgrades, and finds it unchanged each time; removes ledger and finds it standing; installs
plain alone and finds no record; and tries to install declared.
