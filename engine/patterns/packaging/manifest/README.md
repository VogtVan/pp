# manifest — what a package is, and what it needs

## What you write

A package is a folder whose `package.yaml` says who it is and what it needs:

    name: crown
    version: 0.0.1
    description: a package that needs stem -- and, through it, the base
    requires: [stem]
    optional: [opener]

- `name`, `version` — the package's identity; both are owed.
- `requires` — the packages it cannot work without. The base is one of them as soon as a
  document names something the base carries.
- `optional` (optional) — the packages it uses when they are there and does without otherwise.
- `contributes` (optional) — where its pieces plug in: `sockets` (`packaging/sockets`), `cadences`,
  `checks`, `commands`, `events` (`automation/…`).
- Nothing else: a key outside these six refuses.

## What you get

- Adding a package pins what it requires with it, level by level, each at the version its source
  carries — one transaction: either the whole closure lands or nothing does.
- The packages are read in the order of `requires`: what a package needs comes before it. An
  overlay or a document of a later package therefore sees the earlier ones beneath it.
- Removing goes the other way: a package still required by another stays; once nothing requires
  it, it can go.
- A prerequisite missing from the pins makes the instance refuse to read until `./pp -sync` pins
  it back.
- A document of yours may name — CALL, `attach:`, offer under `tools:`, overlay, serve — what the
  packages you require carry, and nothing else.
- A document mounted at the socket of an `optional` package sleeps while that package is absent
  (the build says `mount-dormant`) and plays as soon as it is added. `optional` changes no order:
  the packages are read in the order of `requires` alone.

## When to use it

- Always: every package has one. Keep `requires` to what your documents really name; reach for
  `optional` when your package only rides another's socket and works without it.
- To switch a package off without removing it, use `package-switch`; to declare the keys the
  operator tunes, `settings-fragment`.

## What refuses

- Reading a manifest: a key outside the six above refuses `manifest-key-unknown` — a misspelled
  `require:` would otherwise drop a dependency in silence.
- Adding: a package the source carries nowhere refuses `package-unknown`; two packages requiring
  each other `package-cycle`; a contribution kind the engine does not know `contribution-kind-unknown`
  — and the add writes nothing.
- Removing: a package another still requires refuses `package-required-by`.
- Reading: a pinned package whose prerequisite is not pinned refuses `package-required`.
- Building: a reference to a package you neither require nor name optional refuses
  `dependency-undeclared`; a socket the present optional package opens nowhere refuses as well.

## The demonstration

- `manifests/crown.yaml`, `manifests/stem.yaml` — a chain: crown requires stem, stem the base.
- `manifests/ring.yaml`, `manifests/rung.yaml` — a loop.
- `manifests/widget.yaml`, `manifests/needy.yaml` — an unknown contribution kind, and a package
  that pulls it in.
- `manifests/typo.yaml` — a package whose `requires:` is misspelled `require:`.
- `manifests/loner.yaml`, `manifests/heir.yaml` — the same documents in a package that requires
  nothing and in one that requires the base.
- `procs/REACH_CALL.md`, `procs/REACH_ATTACH.md`, `procs/REACH_TOOL.md`, `procs/REACH_SERVE.md`,
  `overlays/TURN.md` — the five ways a document names what the base carries.
- `manifests/opener.yaml`, `manifests/client.yaml`, `manifests/stranger.yaml` — a package that opens
  a socket, a client that names it optional, one that names it nowhere.
- `procs/PASS.md` — opener's proc, which opens the socket; `procs/STAMP.md`,
  `procs/LOST_STAMP.md` — readings mounted at that socket and at one opener never opens.

## The test

`tests/patterns/packaging/manifest.py` installs from a source carrying the chain, the loop and the
widget, then plays: the closure, `package-unknown`, `package-cycle`, `manifest-key-unknown`; the add and the order of the
homes; the refused add that writes nothing; `package-required-by`; the prerequisite dropped by hand
and pinned back; the removal one by one. It pins loner with each of the five references
(`dependency-undeclared`) and heir with all of them (built); then client without opener (dormant),
with it (played), with a socket opener never opens (refused), and stranger (`dependency-undeclared`).
