# formats — say what form a production takes

## What you write

- On a document that produces, `output: <form>`: the name of a form your instance knows —
  `json`, `table`, `line`, `free`, `any`, or one you declare.
- To declare a form, a `formats:` block in any document's front matter, one form per line:
  its name, its MODE, then its definition in words.

      formats: |
        verdict  inline  approve, revise or reject -- one word

  The mode says how the production travels: `inline` written on the call's line, `stdin`
  piped on the call's standard input, `words` written in the agent's words and standing alone.
- Your instance's own `FORMATS.md` is the place to redeclare a form the engine gives.

## What you get

- The step's line carries the form's NAME: `INFER verdict => words`. Its definition is
  taught once per run, by the reading of the forms every boot serves.
- Where the production goes — the CHANNEL — is never declared: pp derives it from the flow.
  A production the next step takes goes `=> tool`, and the closing shows the call to type:
  on the call's line for an `inline` form, piped by a heredoc otherwise, the form's name
  standing where the production goes (`<json>`). It is CAPTURED: judged on its form when it arrives — an empty one, or a `json` that
  does not parse, replays the document as a REPAIR — then handed over. A production nobody
  takes goes `=> words`: said to the principal, in the agent's words, at its own step. A proven
  production nobody takes is said in the words, and its `PROVE` comes after it.
- A form at the mode `words` is said to the principal as it stands, without the base's
  wrapping; the base may declare its own `said` form, the engine declares none.
- Your instance's redeclaration wins over a package's and the engine's; a form you do not
  redeclare stays the engine's.
- The engine imposes some forms: `options` (a PICK's value), `proof` (a `PROVE`'s array),
  `field` (a described door's elements) and `list` — the form of the step a PICK elects
  from, whatever `output:` says (see `steps/pick`); the document's other steps keep its own
  form. You may reword an imposed form; its mode stays the engine's.
- An overlay may change a document's `output:` (see `composition/overlay`).
- `any` accepts every form: whatever the step asks.

## When to use it

- A production a script or a later step reads: give it a form pp can check (`json`).
- A production the principal reads: a form that says how to present it (`table`, `free`).
- A value said to the principal with no wrapping: a form at the mode `words`.

## What refuses

- An `output:` naming a form nobody declares refuses `format-unknown` when the document is
  read, and `reference-unknown` when the instance builds.
- A form declared twice refuses `format-doubled`; a line without its mode, or with a mode
  other than `inline`, `stdin` or `words`, refuses `format-malformed`; a line at the mode `chat`,
  which the language dropped, refuses `chat-gone` by its name.
- Redeclaring an imposed form with another mode refuses `format-mode-fixed`; the build
  writes neither reading.

## The demonstration

- `procs/FORMS.md` — forms of the instance, among them `verdict`; `procs/JUDGE.md` names it.
- `procs/UNKNOWN.md`, `procs/TWICE.md`, `procs/TORN.md` — a form nobody declares, one declared
  twice, one without its mode.
- `procs/PRODUCER.md` calling `procs/SHIP.md` — a captured JSON value; `procs/LOST.md` — a
  JSON value nobody takes.
- `procs/OWNTABLE.md`, `procs/SPOKEN.md`, `procs/MISMODED.md` — three versions of the
  instance's `FORMATS.md`: its own `table`, forms at `words`, a mode the dialect lacks.
- `procs/ACT.md` and `procs/OPENING.md` — productions in the forms `act` and `said`.
- `procs/PACKAGED.md` — a form a package declares at `words`.
- `procs/TURN.overlay.md`, `procs/TURN.nonesuch.md` — overlays of the base's TURN changing
  `output:`, the second to a form nobody declares.
- `procs/UNTAKEN.md` — a proven line nobody takes; `procs/LISTED.md` and `procs/FREE.md` — a
  list before a PICK, the second in a `free` document.

## The test

`tests/patterns/outputs/formats.py` plays the demonstration: JUDGE's line carrying `verdict`,
the three refusals, PRODUCER's capture and its repairs, LOST without a warning; the
instance's `table` winning, the engine's forms otherwise, `act` said standing alone, the
wrong mode refused, `said` unknown under the witness base; the two readings and their
receipts, a package's `words` form, the dropped mode refused by its name, each imposed form moved and
refused with nothing written,
`options` reworded; the TURN overlay's `line` and its refusal; UNTAKEN's closing; LISTED's
list and its repairs, FREE writing `free` after its PICK.
