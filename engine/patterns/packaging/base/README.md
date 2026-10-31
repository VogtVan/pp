# base — the package an instance stands on

## What you write

A base is a package the instance stands on: every run boots on it. It carries:

- its manifest, `package.yaml` — its name and version; it requires nothing, and declares the
  sockets its turn opens;
- `procs/BOOT.md` — the bootstrap a run opens on: the readings it serves, then the turn;
- `procs/TURN.md` — one exchange, from the ask to its result;
- optionally, `system/SYSTEM.COMMON.md` — its word in the standing orders: who the principal is here
  — and `system/SYSTEM.CONDUCT.md`, its word to the model that conducts (see
  `packaging/system-fragment`);
- optionally, `settings/SETTINGS.md` — its own keys, written bare, without a prefix (see
  `packaging/settings-fragment`).

    proc: |
      HOOK turn.begin
      WORK
      §
      HOOK turn.end
      PROVE

The operator names the base at the install (`-install -base <name>`); without it, the instance
stands on the product's own.

## What you get

- The instance's manifest says `base: <name>`, the instance carries your base and not the product's,
  and a run boots on your BOOT, whoever conducts it.
- Your section of the standing orders comes right after the engine's, before every other package's.
- Your names are bare: a socket of yours is written `turn.begin`, and a document of the instance
  mounted at `boot.initialize` reaches the boot; a key of yours is `glow`, never `<base>_glow`.
- A base without `system/` installs: the standing orders are then the engine's alone.
- An install that names no base writes no `base:` at the manifest.

## When to use it

- Your instances need another bootstrap or another turn than the product's — another member, other
  readings at the boot, another shape of exchange.
- To add a step, a reading or a law to the product's turn, a package of documents attached at its
  sockets is enough (`composition/hook`, `composition/mount`).

## What refuses

- At the install: a base without `procs/BOOT.md` or `procs/TURN.md` refuses `base-incomplete`
  before anything is written.
- At `./pp remove`: the base refuses `package-base` — an instance never leaves its base.

## The demonstration

- `manifests/lantern.yaml`, `procs/BOOT.md`, `procs/TURN.md`, `systems/lantern.common.md`,
  `systems/lantern.conduct.md`, `fragments/lantern.md` — a whole base with its two files of the
  standing orders and one bare key.
- `manifests/stub.yaml` with `procs/BOOT.md` alone — a base without its turn.
- `manifests/wick.yaml` with both procs — a base without `system/`.

A base's word in the standing orders lives in its `system/` folder and its keys in `settings/`; the
demonstration names each by the base (`lantern.common.md`, `lantern.conduct.md`, `lantern.md`), and
the test places them there.

## The test

`tests/patterns/packaging/base.py` installs on lantern, mounts a document of the instance at
`boot.initialize`, boots under each conduction and tries to remove the base; installs without a
base; then tries stub and installs on wick.
