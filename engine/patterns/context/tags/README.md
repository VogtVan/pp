# tags — let a law cite a value of another document

## What you write

In a law's text, `@<Document>.<field>`: the name of a document and a key of its front
matter.

    constraints.production: |
      TG1  review in @BRIEF.mode mode, for @BRIEF.owner.
      TG2  sign your review as @MEMBER.name.

The document is any the instance resolves by its name (see `context/addressing`): one of
your own, `MEMBER`, `SETTINGS`.

## What you get

- Wherever the law is in force — its document opened, called, played at a point, mounted,
  amended by an overlay (see `composition/overlay`) — each tag is replaced by that field's
  value, and the law reads with the value in its place.
- A tag reads the value a guard reads (see `control-flow/due`): `@SETTINGS.<key>` takes the
  value written in `SETTINGS.md`, the effort's presets applied, and a key left out takes its
  default; a true or false value reads `true` or `false`.

## When to use it

- Write a value once — a member's name, a mode, an owner — and let several laws cite it.
- Let a law follow a setting the operator changes.
- To play a step only when a value says so, write a guard instead (see `control-flow/due`).

## What refuses

`tag-unresolved`, when the law comes in force, for a tag whose document no name answers, or
whose field is absent or empty — the member's field included — and a `SETTINGS` key that no
one gives a default.

## The demonstration

- `procs/BRIEF.md` — the values: `mode` and `owner`.
- `procs/CITED.md` — laws that cite the brief, the member's `name` and `character`, and a
  setting written in `SETTINGS.md`.
- `procs/NOTED.md`, mounted on `procs/DESK.md` — a framing whose law cites the brief.
- `procs/ABSENT.md` — a field the brief lacks; `procs/UNKNOWN.md` — a document no name
  answers: each refuses.
- `procs/DEFAULTED.md` — a law citing a setting left to its default: it reads the default.

## The test

`tests/patterns/context/tags.py` writes the member and `SETTINGS.md`, then plays the
demonstration: CITED's laws read the brief, the member and the setting; NOTED mounted reads
the brief's owner; DEFAULTED reads the default of `work_repairs_allowed`; ABSENT, UNKNOWN and
CITED under a member without `character` refuse `tag-unresolved`.
