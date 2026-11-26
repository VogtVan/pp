# mount — bring a document's laws and readings without a step

## What you write

A document to mount is usually a `kind: doc` with no `proc:`: its laws
(`constraints.production`, `constraints.behavior`), its offers (`tools:`), its readings
and its body. Two ways bring it in:

- The document mounts itself at a point a proc hooks: `mount: <proc>.<hook>` in its
  front matter (`mount: bench.open`; see `composition/hook` for the `HOOK` line).
- A skill prints one line `::mount [{"doc": "<NAME>.md"}]`; each entry may add
  `"body": true` (serve the body) or a list of selections (serve those parts, see
  `context/serve`), and `"replaces": ["<NAME>.md", …]` (the documents it takes the place of).
- Every way names the document by its address (see `context/addressing`): a bare name, a
  path, or `<package>:<path>` for a file a package keeps outside its documents.

A document that must come with another one wherever it goes is not mounted at a point: the
other one imports it (see `composition/import`).

## What you get

- The document's laws are in force, its offers join the step's, its body and readings
  are served (see `context/serve`), and the tokens it names render as sections (see
  `context/payload`). It asks nothing: no frame, no step, no production of its own.
- Its laws are asked at the next `PROVE` like any law on screen (see `rules/prove`).
- Its own `when:` decides whether it enters (see `composition/qualifiers`); its overlays'
  changes come with it (see `composition/overlay`).
- Mounted at a point, it comes back at every passage: the `HOOK` of each passage mounts
  it again, its law once each time.
- Mounted by a skill, it lasts until the end of the passage. When it leaves, no segment
  opens: the closing of the passage stands with the steps said under it.
- A document already mounted is not mounted again: its laws and offers stand, and a mount
  that names what is there plus a deeper document -- a plan's node after its parent's, in
  the same passage -- adds the deeper one alone. Naming it again with `"body": true` serves
  its body once more (or says it spared, see `context/serve`); without a body asked, naming
  it again brings nothing. Several mounts in one passage build one view.
- An entry with `replaces` takes the documents it names out of the view before it adds its
  own: their laws and offers leave, so a law one of them carried can come back with the new
  document. A name that is not mounted changes nothing; a document mounted at a proc's
  `initialize` belongs to that proc and stays. The trace says `released`.
- A mount makes no segment of its own. Its body is a reading at the head of the segment of
  the step that stands, its laws join that step's `CONSTRAINTS`, its offers its `TOOLS`.
  Several bodies read in the order of the entries, then their `serve:` rows.
- Mounted by a skill, it shows the block that stands again, with the laws now in force.
  When the principal holds the output open (`PP_HOLD_OUTPUT=true` beside its mark, on the
  call that opens the run or carries the message and on each mount), nothing is shown
  before its bare call. The call that carries the message opens the exchange and renders
  no block. Each mount is posed: its laws and its offers are in force, and what it serves
  waits at the run, in the order of the mounts. The principal's bare call then plays the
  exchange and renders ONE output, once: what the mounts serve stands at the head of the
  first block, before its first step, and every step carries the laws of every mount. On a
  run that stands on a step, the bare call renders that step, once. What the skill prints
  answers its call and goes into no output. While the exchange the message opened is not played, a door or a space named
  on the run is refused like a name no step offers: no frame stacks before the bare call.

## When to use it

- Put a framing in force — the laws and readings of a plan's node — while the work
  goes on in another proc.
- Bring a context to every passage of a proc without adding a step to it.
- Let a skill decide what is in force, after it has computed it.
- Bring a record up to date each time the document is mounted, before it is served: `exec:`
  (see `automation/exec`).

## What refuses

- A document that declares both `attach:` and `mount:` refuses `attach-and-mount`: it is
  called or mounted, never both.
- A front matter that still writes `mounts:` refuses `mounts-gone` when the instance is
  built: a document takes what it stands on with `imports:` (see `composition/import`).
- From a skill: a NEW document whose law carries a code another document already has in
  force refuses `mount-collision`, a name found nowhere `mount-missing`, an entry that is
  not `{"doc": …}`, an entry that carries a `scope` key or a `replaces` that is not a list
  of names `mount-invalid`.

## The demonstration

- `procs/BENCH.md` — a host: `HOOK bench.open`, one `INFER`, then `PROVE`.
- `procs/TOOLKIT.md` — mounts itself at `bench.open`: its law `MT1` and the offer `HALL`.
- `procs/HALL.md` — a host: `HOOK hall.open`, one `INFER`; TOOLKIT offers it.
- `procs/LAMP.md` — mounts itself at `hall.open`, and a skill mounts it too: its law `MT3`.
- `procs/NOTES.md` — a document a skill mounts by name: its law `MT2`, the offer `LAMP`;
  the test also gives it `mount: bench.open`.
- `procs/BOTH.md` — both entry verbs at once: it refuses.

## The test

`tests/patterns/composition/mount.py` plays them: TOOLKIT rides BENCH's step and comes
back at the next passage, and brings nothing without its `mount:` line; an overlay of BENCH
that writes `mounts:` refuses `mounts-gone`; NOTES given `mount: bench.open` is not mounted
again when a repair replays BENCH's point; a skill written by the test mounts NOTES, its law
asked at the `PROVE`, then mounts it again, with LAMP and with its body asked -- LAMP alone added, the body
served again, MT2 once --; the mount makes no segment, its offer
routes on the one segment of the step that stands, and an entry with a `scope` refuses; LAMP
replaces NOTES, then a second holder of MT2 replaces NOTES; every
refusal above is played.
On an output BENCH's principal holds open, NOTES then LAMP show no block, and the
principal's bare call shows BENCH's step once, MT2 and MT3 in force; the same mounts without
the hold show it once each. `tests/engine/execution/principal-open-output.py` plays the hold
from the console: an opening, a message, two mounts, the release.
