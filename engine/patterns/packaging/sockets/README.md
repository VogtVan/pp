# sockets — a point your package opens for others to plug into

## What you write

In your package's manifest, the sockets your procs open, each as `<proc>.<hook>`:

    name: opener
    requires: [kit]
    contributes:
      sockets: [pass.begin]

In the proc named before the dot, the step that opens it:

    proc: |
      HOOK pass.begin
      WORK

In another package — one that requires yours — a document that plugs in, naming the socket with
your package's name in front: `mount: opener.pass.begin` or `attach: opener.pass.begin`.

## What you get

- Your package's socket is addressed `<package>.<proc>.<hook>` by everyone: a document of another
  package mounted or attached there plays when your proc reaches its `HOOK`, as it would at a
  socket of the base (`composition/hook`, `composition/mount`).
- The base is the exception: its sockets are written in two segments (`turn.begin`), and a
  two-segment name always means the base.
- The name is free inside your package: two packages may open the same `<proc>.<hook>` and never
  meet, each address carries its package.
- The catalog lists the sockets each package declares.

## When to use it

- Your package runs a pass of its own and wants others to bring documents into it — a reading at
  its start, a step at its end — without your package knowing them.
- To plug into the base's turn, you need no socket of your own: attach or mount at the base's.

## What refuses

- A proc of your package that `HOOK`s a socket your manifest does not declare refuses
  `socket-undeclared`.
- A declaration with your package's name in it (`opener.pass.begin`) refuses
  `contribution-malformed`: declare the minimum, `<proc>.<hook>`.
- Inside your own manifest too, a socket is named with its package: a cadence `at: pass.begin`
  looks for the base's and refuses `socket-unknown`.
- A document of a package mounted or attached where no proc opens a socket — the two-segment name
  the base does not open, a qualified name no proc hooks — refuses `attach-unhooked`.

## The demonstration

- `manifests/opener.yaml` with `procs/PASS.md` — the package that opens `pass.begin` at the turn's end.
- `manifests/rider.yaml` — a package requiring opener, with `procs/STAMP.md` (mounted at
  `opener.pass.begin`), `procs/BARE_STAMP.md` (at `pass.begin`), `procs/GONE_STAMP.md` (at
  `opener.gone.begin`) and `procs/DANGLING.md` (attached where nobody opens).
- `manifests/rival.yaml` — a second package opening a socket of the same name.
- `manifests/mute.yaml`, `manifests/selfish.yaml`, `manifests/overqualified.yaml` — the socket left
  undeclared, named in two segments by its own package, declared with the package's name.

## The test

`tests/patterns/packaging/sockets.py` reads the base's own declaration in the catalog, pins opener
and rider and builds with each of rider's readings (the qualified one mounted, the two others
refused), then DANGLING (refused); then mute (`socket-undeclared`), opener beside rival (two
addresses), selfish (`socket-unknown`) and overqualified (`contribution-malformed`).
