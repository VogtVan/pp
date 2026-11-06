# package-switch — a package off without removing it

## What you write

Nothing in your package: the switch is the operator's. In the instance's `SETTINGS.md`, one line
per package beyond the base:

    package.alpha: off

For one run only, at the console: `./pp <key> -disable alpha`, then `./pp <key> -enable alpha`.

A LAUNCHER gives a run its composition at its opening: `PP_PACKAGES=alpha=on,beta=off ./pp -new`.

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
- The run's own switches BEAT `SETTINGS.md`, name by name: `-enable alpha` on an instance whose
  SETTINGS says `package.alpha: off` plays alpha and its dependents for that run, from the next
  output on; `-disable` on a package SETTINGS leaves on takes it out. A name the run never switched
  plays as SETTINGS says. The run's slot keeps them as `switches: {alpha: on}`; an upgrade's
  renewal mark carries them.
- `PP_PACKAGES=<name>=on|off[,<name>=on|off…]` is read by `-new` alone, judged before anything is
  written, and written at the run's switches BEFORE its first block is composed: the first output
  already says `alpha on` at its heading and offers alpha's skills; the trace's `new` line says the
  switches. A keyed call under the variable ignores it: a run's composition moves by its own
  switches alone. The two catalog readings the boot serves (`tools.md`, `output.md`) are compiled
  on SETTINGS; the heading and the TOOLS of every block say the run's composition.
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
- At `-new` under `PP_PACKAGES`: a piece that is not `<name>=on|off` refuses `packages-invalid`,
  the base `package-base`, a name the instance does not pin `package-unpinned` — nothing written,
  no run opened.

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
cause said, the run's switch over SETTINGS both ways and `PP_PACKAGES` composing the first output,
the three refusals, the same switch under the principal's conduction, the keyless view.
