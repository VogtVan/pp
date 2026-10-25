# checks-and-signals — what your package tells the instance's bus

## What you write

In your package's manifest, under `contributes:`:

    contributes:
      checks:
        - {signal: sighting-due, predicate: record-crossing, record: sightings.jsonl,
           anchor: "@SETTINGS.sighting_day"}
      events:
        sectors:
          watch: {icon: 👁, default: true}
          aside: {cap: 1}
        vectors:
          witness-spot: {verify: pp-witness}
        signals:
          noticed: {threshold: "@SETTINGS.witness_patience", priority: 2, door: WATCH}
          aside-seen: {sector: aside, priority: 3}
          swept: {door: REVIEW, at: gesture:pp-probe-broom}

- `signals` — what your package can raise: `door`, the document to open about it; `threshold`,
  a count (or a setting) a signal must reach before it is served; `priority`, its rank; `sector`,
  one of your own sectors; `at: gesture:<skill>`, the signal raised each time that skill is
  played as a gesture, without a line of code.
- `sectors` — where your signals are served: `cap`, how many lines at most; `icon`; one
  `default: true` sector for the signals that name none.
- `vectors` — a family of subjects your signals point at (`witness-spot:door`), with the skill
  that says whether a subject still exists (`verify`) and, from another package, the skill that
  says whether it is free (`guard`).
- `checks` — a predicate the engine judges at the boot, raising its signal: `record-crossing`
  (a record not written since its anchored day), `fingerprint` (a file still as installed),
  `home-idle` (harness skills that nothing offers).
- A script raises or clears a signal by printing a line: `::push <signal> <vector> <text>`,
  `::clear <signal> <vector>` — from a sink (`outputs/sink`), an `exec:` (`automation/exec`), a
  command (`automation/commands`) or any skill the engine starts.

## What you get

- The bus counts each push per subject; a signal is served once its threshold is crossed — the
  instance's own setting wins over your package's default.
- A pushed line STANDS until it is cleared: `::clear` takes it out; `./pp acquit <vector>` drops
  its count and its line together.
- The bus ranks what it serves by priority, then by count, and serves each sector under its own
  cap; `cap.<sector>` in the instance's settings widens or mutes it.
- Before anything is written, the family's verifier is asked: a subject it refuses is never
  counted, and a line it refuses later drops from what is served — the verifier is the broom. A
  guardian, when one is declared, can refuse a subject still held elsewhere.
- The engine names no signal, sector or family of its own: everything served comes from a
  declaration.

## When to use it

- Your package must tell the agent, at the next exchanges, that something waits: a digest due, a
  file left as installed, a subject that came back three times.
- A script must leave a note that outlives its run.

## What refuses

- At a push: a provider, a signal or a family nobody declared refuses `provider-unknown`,
  `signal-unknown`, `family-unknown`; a subject the verifier refuses `vector-unverified`, a
  verifier nobody carries `verifier-missing`; a line out of form `push-malformed`; an acquit of a
  subject nothing counts `vector-unknown`.
- At a guard: a held subject refuses `vector-guarded`, a guardian nobody carries
  `guardian-missing`.
- At the build or any read: a family without a verifier refuses `family-unverified`; two
  guardians `family-collision`; a sector declared twice, or two default sectors,
  `sector-collision`; a signal in a sector its package does not own `sector-unowned`.
- The retired key `improve:` refuses `manifest-key-unknown`, like any key a manifest does not
  know (see `packaging/manifest`).

## The demonstration

- `manifests/witness.yaml` — sectors `watch` (the default) and `aside`, the family
  `witness-spot`, three signals; `witness.bare.yaml`, `witness.nowhere.yaml`,
  `witness.guarded.yaml`, `witness.defaults.yaml`, `witness.retired.yaml` — a family without its
  verifier, a verifier nobody carries, a family guarded by its own verifier, two default
  sectors, the retired key.
- `manifests/keeper.yaml`, `manifests/keeper.ghost.yaml` — a package guarding the witness's
  family, and one guarding a family nobody verifies.
- `manifests/probe.yaml`, `manifests/rival.yaml`, `manifests/rival.foreign.yaml` — a sector of
  one's own, the same sector declared again, a signal in another's sector.
- `manifests/probe.arbitration.yaml` — signals of several priorities in three sectors.
- `manifests/broom.yaml` and `procs/SWEEP.md` — a signal raised by a gesture, and the step that
  offers it.

## The test

`tests/patterns/automation/checks-and-signals.py` pins the manifests and writes the verifier, the
guardian, the sink and the broom, then plays the bus: declarations, threshold, sectors, stand and
acquit, caps; a push that stands and a clear that drops it; a sink's push; the undeclared pushes;
the verifier at every entry and at the service, the guardian, the retired key refused; the gesture's
signal; a sector's owner and the arbitration.
