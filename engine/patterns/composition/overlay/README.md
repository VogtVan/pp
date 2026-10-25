# overlay — amend a document you do not own

## What you write

A document of the SAME name as the one you amend, nearer: in your instance's space
(`.pp/procs/` over a package's document, `.pp/` over one of your own `procs/`; the order of
the spaces is in `context/addressing`). Its front
matter carries `name:` and the changes, nothing else:

- laws: `+<CODE>  <text>` adds a law, `-<CODE>` lifts one, under the section they belong
  to (`constraints.production`, `constraints.behavior`; see `rules/laws`);
- offers: `+<NAME>` adds an offer to `tools:`, `-<NAME>` withdraws one (see
  `composition/door`; a name your instance does not carry is adopted, see
  `composition/adoption`);
- readings: `+<NAME>.md` in `serve:` adds a reading (see `context/serve`);
- forms: `output:` or `input:` replaces the base's own (see `outputs/formats` and
  `outputs/input`);
- its body, if any, is added after the body of the document it amends.

## What you get

- Wherever the document plays — called, mounted, opened — its laws, its offers and its
  readings are the composition: the base's, then your changes.
- The document still resolves to its own file and keeps its steps: an overlay changes no
  flow. An `output:` or `input:` it writes is the one the document plays with.
- The readings you add are served when the document enters, each under its own title.
- A mounted document carries its overlay's changes the same way, stacked or nested; the
  laws asked at the next `PROVE` are the composed ones, and a lifted law is not one of them.
- A document mounted by another path, outside the name's chain, takes none of the changes.

## When to use it

- Add a law, an offer or a reading to a package's proc — `TURN` for instance — without
  copying it.
- Lift a law or an offer that does not fit your instance.
- Change the form a package's proc produces or receives, with `output:` or `input:`.
- An overlay has no guard: to switch a document on and off, guard a contributor instead
  (see `composition/qualifiers`).

## What refuses

- Adding a law or an offer that is already there refuses `overlay-adds-existing`; lifting
  one that is not there refuses `overlay-removes-nothing`.
- An overlay that carries `proc:` refuses `overlay-carries-proc`: steps are added at a
  point (see `composition/hook`), never by an overlay.
- `-<NAME>.md` in `serve:` refuses `overlay-serve-removal`: an overlay adds readings, it
  never removes one.
- An `overlays/` directory at the root of your instance is never read: the build warns
  `overlays-ignored`.
- Two mounted documents whose composed laws share a code refuse `mount-collision`.

## The demonstration

- `procs/DRAFT.md` — the base a package owns: laws `OV1`, `OV2`, the offer `REVISE`, one `INFER`.
- `procs/DRAFT.overlay.md` — its overlay: `+OV3`, `-OV2`, `+EDITOR`, `-REVISE`, `+STYLE.md`,
  and a line of body; it is placed at `.pp/procs/DRAFT.md`.
- `procs/DRAFT.doubled.md`, `procs/DRAFT.absent.md`, `procs/DRAFT.flow.md`,
  `procs/DRAFT.minus.md` — overlays that refuse, one per refusal above.
- `procs/REVISE.md`, `procs/EDITOR.md`, `procs/STYLE.md` — the offers and the reading.
- `procs/NODE.md` and `procs/NODE.overlay.md` — a framing and its overlay (`-OV6`, `+OV7`,
  `+REVISE`), the overlay placed at `.pp/NODE.md`.
- `procs/OTHER.md` and `procs/OTHER.overlay.md` — a framing whose overlay adds `OV7` too.
- `procs/NODE.homonym.md` — a `NODE.md` placed elsewhere, outside the name's chain.
- `procs/SHIFT.md` — one `INFER`, then `PROVE`: the proc the framings are mounted on.

## The test

`tests/patterns/composition/overlay.py` plays them, with a package `desk` written by the
test to own DRAFT and REVISE: the overlay's changes, its body after DRAFT's and STYLE
served; DRAFT alone without it; the four refusals; `overlays-ignored`; NODE mounted on
SHIFT with OV5 and OV7, OV6 refused as a stranger at the `PROVE`, under both conductions;
nested; OTHER refusing `mount-collision`; the homonym taking no change.
