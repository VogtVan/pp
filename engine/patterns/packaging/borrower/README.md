# borrower — an instance that plays the machine of its house

## What you write

Nothing in a document. A BORROWER is an instance that carries no machine of its own (no
`.sys/engine/`, no `.sys/vendor/`) and plays the machine of the nearest instance above it, its
HOUSE. It comes into being in one of two ways:

- **born** under the house: `./pp -install <dir>` played at the house's console, `<dir>` under
  the house's workspace -- or `./pp agent add <path>` with the `agent` package;
- **imported** from an instance that carries its own machine: `./pp agent import <path> --from
  <workspace>` with the `agent` package. The instance's `.pp/` moves under the house, its
  machine is taken out, and it is a borrower from then on.

    house/
    ├── .pp/                  the house: its machine under .sys/engine and .sys/vendor
    ├── agents/born/.pp/      born here: no machine
    └── agents/kept/.pp/      imported: no machine, its own files as they were
        └── procs/KEPT.md

## What you get

- A borrower plays the house's engine, its versions and its packages. It pins nothing; its own
  `package.<name>: off` lines switch a package off for itself alone (see `packaging/package-switch`).
- The house's `doctor`, `upgrade`, `add`, `remove` and `develop` reach every borrower under it:
  they recompose its SETTINGS, its seeds, its console, its catalog and its standing orders. In a
  borrower these verbs refuse `machine-borrowed`.
- An imported instance keeps everything of its own: `MEMBER.md`, `SETTINGS.md`, `FORMATS.md`, its
  `procs/` (`KEPT` above stays in its catalog), its plans, its records and its runs' traces. Its
  manifest keeps the date it was first installed, and its slug becomes the last segment of its
  path. Each run it had is renewed: the run's key reopens it at its next call, on the house's
  machine.
- The import takes out of the old workspace what pp wrote there and nobody changed since: the
  console (`pp`, `pp.cmd`), and what each wired harness wrote (its launchers, the card it
  lists). It leaves the doors (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`), the harness settings and
  any file you edited, and names each one: they are yours to keep or remove.

## When to use it

Bring a workspace that ran on its own machine into a house, so that the house conducts it as one
of its agents: one machine to upgrade, one place for all the agents' records.

## What refuses

| Code | When |
|---|---|
| `machine-missing` | `-install` of a borrower with no instance carrying a machine above it |
| `import-borrowed` | the instance to import borrows a machine already |
| `import-version` | its engine is not the house's: upgrade it in its workspace first |
| `import-packages` | it pins a package the house does not: add it at the house first |
| `import-cross-device` | the instance and the house are not on one filesystem |
| `maintenance-busy` | a pp process is active in the instance to import |

Every refusal comes before anything is written.
