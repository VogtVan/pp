# mount — bring a document's laws and readings without a step

## What you write

A document to mount is usually a `kind: doc` with no `proc:`: its laws
(`constraints.production`, `constraints.behavior`), its offers (`tools:`), its readings
and its body. Three ways bring it in:

- The document mounts itself at a point a proc hooks: `mount: <proc>.<hook>` in its
  front matter (`mount: bench.open`; see `composition/hook` for the `HOOK` line).
- The proc that hooks the point names what mounts there: a `mounts:` table in its front
  matter, `<proc>.<hook>: <NAME>.md` (`hall.open: NOTES.md`), or in an overlay of that
  proc (see `composition/overlay`).
- A skill prints one line `::mount [{"doc": "<NAME>.md"}]`; each entry may add
  `"body": true` (serve the body) or a list of selections (serve those parts, see
  `context/serve`), `"scope": "nested"` (a segment of its own) or `"scope": "stacked"`
  (the default).
- Every way names the document by its address (see `context/addressing`): a bare name, a
  path, or `<package>:<path>` for a file a package keeps outside its documents.

## What you get

- The document's laws are in force, its offers join the step's, its body and readings
  are served (see `context/serve`), and the tokens it names render as sections (see
  `context/payload`). It asks nothing: no frame, no step, no production of its own.
- Its laws are asked at the next `PROVE` like any law on screen (see `rules/prove`).
- Its own `when:` decides whether it enters (see `composition/qualifiers`); its overlays'
  changes come with it (see `composition/overlay`).
- Mounted at a point, it comes back at every passage: the `HOOK` of each passage mounts
  it again, its law once each time.
- What a `mounts:` table names mounts after the documents that mount themselves there.
  Under `proc_body_serve: once`, its body is served the first time and spared after.
- Mounted by a skill, it lasts until the end of the passage.
- Mounted `nested`, it takes a numbered segment of its own: its laws are written there,
  the pending step holds their codes, and `<offer>@<n>` reaches its offers.

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
- A `mounts:` line for a point the proc does not hook refuses `mounts-hook-unknown`; a
  name found nowhere refuses `reference-unknown`.
- From a skill: a document already mounted refuses `mount-collision`, a name found
  nowhere `mount-missing`, an entry that is not `{"doc": …}` or an unknown scope
  `mount-invalid`.

## The demonstration

- `procs/BENCH.md` — a host: `HOOK bench.open`, one `INFER`, then `PROVE`.
- `procs/TOOLKIT.md` — mounts itself at `bench.open`: its law `MT1` and the offer `HALL`.
- `procs/HALL.md` — a host whose `mounts:` names `NOTES.md` at its own point.
- `procs/LAMP.md` — mounts itself at `hall.open`, before what HALL names: its law `MT3`.
- `procs/NOTES.md` — a document named by HALL, by an overlay or by a skill: its law
  `MT2`, the offer `LAMP`.
- `procs/BOTH.md` — both entry verbs at once: it refuses.

## The test

`tests/patterns/composition/mount.py` plays them: TOOLKIT rides BENCH's step and comes
back at the next passage, under both conductions, and brings nothing without its
`mount:` line; HALL mounts NOTES after LAMP, its body spared once proven; an overlay of
BENCH mounts NOTES too; a skill written by the test mounts NOTES, its law asked at the
`PROVE`, then mounts it nested; every refusal above is played.
