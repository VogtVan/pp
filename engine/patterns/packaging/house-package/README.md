# house-package — a package the house writes for itself

## What you write

A folder under your instance's `packages/`, beside its `procs/`: `.pp/packages/<name>/`. It has
the same shape as a package of the product — a `package.yaml`, and the folders it needs among
`procs/`, `refs/`, `overlays/`, `skills/`, `settings/`, `seed/`, `system/`, `user/`:

    .pp/packages/chores/
    ├── package.yaml          name: chores · version: 0.0.1 · requires: [kit]
    ├── procs/CHORES.md       offers pp-chores
    └── skills/pp-chores/
        ├── SKILL.md
        └── pp-chores.py

Then add it at the house, as any package: `./pp add chores`.

Its script needs no access to pp's engine. pp names the instance the call serves in the
variable `PP_HOME`, and the script writes there with Python's standard library alone:

    home = Path(os.environ["PP_HOME"])
    chores = home / "chores.txt"
    with chores.open("a", encoding="utf-8") as listed:
        listed.write(chore + "\n")

## What you get

- pp looks for a package in two places, in this order: the product it was installed from, then
  the `packages/` of the house. Every verb of a package plays on yours: `add` pins it and copies
  it into the machine, `doctor` copies it again when you changed a file without changing its
  version, `upgrade` follows its new version, `remove` takes it out.
- Its documents, offers, laws, settings and records are composed like those of any other package.
- An instance that borrows the house's machine — an agent of the house — plays the packages the
  house pins, yours included. Each one switches yours off for itself with `package.<name>: off`
  in its own `SETTINGS.md` (see `packaging/package-switch`).
- Your package may `require` a package of the product; a package of the product never names
  yours.

## Develop a house package

While you write the package, play it from its own folder instead of a copy:

    ./pp develop chores

The pin becomes `chores: develop`, and nothing of `chores` is copied into the machine. Every file
you change in `.pp/packages/chores/` then plays at the next call that reads it, with no verb and
no restart, in the house and in its agents:

- a proc's text, its laws and its offers, a reading, a script of its skills;
- a key you add to its `settings/SETTINGS.md`, which reads at its default value.

Three things wait for something else, as for any document:

- a step you add to a document the run is playing plays from the next message (see
  `control-flow/root`);
- the catalog of tools and formats, and the standing orders from its `system/`, are read when a
  run opens: the next run recompiles them by itself;
- the standing orders a harness was launched with change at its next launch.

`doctor` and `upgrade` leave the pin as it is: there is nothing to copy, and a new `version:`
moves nothing. When the package is ready, copy it back at the version its manifest holds:

    ./pp develop chores off

`develop` and `develop … off` rewrite the machine, like `add`: play them while no pp process is
active (the post closed), once. The runs that stand are renewed, as by `upgrade`.

## When to use it

- To give the house and its agents a procedure and the script it calls, kept with the house and
  switched on or off agent by agent.
- To grow a proc of `procs/` into a package once it needs a script, settings or records of its
  own.

## What refuses

- `add` of a name that the product also carries refuses `package-duplicate`, both paths named;
  nothing is written. Give your package another name, or change the product's package with an
  overlay (`composition/overlay`).
- `add` of a name found in neither place refuses `package-unknown`.
- `add`, `develop`, `doctor`, `upgrade` and `remove` played in an agent refuse `machine-borrowed`:
  they play at the house, which reaches its agents.
- `develop` of a package of the product refuses `develop-product`: only a package of the house
  plays from its sources. `develop … off` of a package not played from its sources refuses
  `develop-absent`.

## The demonstration

- `manifests/chores.yaml` — the package, which requires the base.
- `procs/CHORES.md` — its proc, which offers `pp-chores`.

The script `pp-chores` is the house's to write; the test writes one with two verbs, `add` and
`list`, on the standard library alone.

## The test

`tests/patterns/packaging/house-package.py` places `chores` under the house's `packages/`, adds
it, plays CHORES and its script, then a name the product carries refused; an agent of the house
plays `chores` and switches it off; `doctor` copies a changed file again, `upgrade` follows a new
version and `remove` takes the package out. On a second house, `develop` plays `chores` from its
folder: a script changed under a run plays at its next call (in both conduction modes), a document
and a new setting read at the next call, the next run recompiles the catalog and the standing
orders, the agent plays the folder too, `doctor` and `upgrade` leave the pin, `develop … off`
copies it back, and a package of the product refuses `develop-product`.
