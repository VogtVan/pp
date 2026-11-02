# package-switch — a package off without removing it

## What you write

Nothing in your package: the switch is the operator's. In the instance's `SETTINGS.md`, one line
per package beyond the base:

    package.alpha: off

For one run only, at the console: `./pp <key> -disable alpha`, then `./pp <key> -enable alpha`.

## What you get

- A package switched off leaves the play: its documents, its offers, its forms and its
  contributions are gone from the catalog and from every block. Every package that `requires` it
  leaves with it, its cause said; a package that names it under `optional:` stays.
- Off is not gone: the package stays pinned and installed, its settings section stays, and `on`
  brings everything back as it was, the catalog byte for byte.
- The key is written for you: each install and add seeds `package.<name>: on` under
  `# ---- packages ----`, a removal drops it, and the operator's `off` is kept across them.
- `-disable` and `-enable` switch a package for the run alone and answer with the block that
  stands; another run of the same instance plays every package. The same holds under the
  principal's conduction.
- Every output of a run says the state of each package beyond the base, in the order the packages
  are read: `alpha off · beta off (<- alpha)`. With no run standing, `./pp` alone says the state
  `SETTINGS.md` sets.

## When to use it

- To try the instance without a package, or to keep one installed while it should not play.
- To leave a package out of one run — a run that must not carry its weight — use `-disable`; the
  other runs are untouched.
- To remove a package for good, `remove` it (see `packaging/manifest`).

## What refuses

- At `SETTINGS.md`: the base switched off, or a value other than `on` and `off`, refuses
  `settings-invalid`; a write through pp's face leaves the file as it was.
- At `-disable`: the base refuses `package-base`, a name the instance does not pin
  `package-unpinned`, a package one of whose documents holds the block that stands
  `package-in-flight` — and the run is left as it was.

## The demonstration

- `manifests/alpha.yaml` with `procs/ALPHA.md` (a step at the turn's end, in alpha's own form) and
  `fragments/alpha.md` (alpha's key); its skill `pp-alpha` is written by the test.
- `manifests/beta.yaml` with `procs/BETA.md` — a package that requires alpha, its step offering
  alpha's skill.
- `manifests/gamma.yaml` — a package that names alpha under `optional:`.

## The test

`tests/patterns/packaging/package-switch.py` installs alpha, beta and gamma from a source, then
plays: the keys seeded; alpha switched off, beta leaving with it and gamma staying; off is not
gone; the base and a wrong value refused with the bytes kept; the sync following the pins; the
catalog without alpha's skill and form, then byte for byte with alpha on. In runs: `-disable beta`
answering the standing block, BETA not played, a run beside playing everything, `-enable`, the
cause said, the three refusals, the same switch under the principal's conduction, the keyless view.
