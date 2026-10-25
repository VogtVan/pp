# infer — ask the agent for one production in a given form

## What you write

One line in your `proc:`: `INFER`, with no argument. The body of your document says what to
produce; the key `output:` in the front matter names its form — one of the forms your
instance lists in its `output.md` (`json`, `table`, `line`…). Without `output:`, the form is
`any`: whatever the step asks.

## What you get

- The step's line names the form and where the production goes: `INFER table => response`.
- When no later step takes the production, it goes `=> response`: the agent says it to
  the principal, in its message, at this step. When it is the document's last step, the
  passage is over once it is said.
- When the next step takes the production — a `PICK` (see `steps/pick`), or a called
  document that declares `input:` (see `outputs/input`) — it goes to the tool instead:
  `=> tool` for a form written on the call's line, `=> tool (heredoc)` for a form piped
  on the call's standard input. The closing gives the command to use.
- Before a `PICK`, the form is the engine's `list`, whatever `output:` says: you write
  nothing for it.
- A called document that declares `input:` opens on your production and sees it under
  `input`, served once when it opens.
- A production that goes to the tool is judged when it arrives. An empty one, or one that
  breaks its form (a `json` that does not parse, for instance), is a miss: the document
  replays from its first step as a REPAIR, the miss named under DEVIATION. A good one is
  handed to the next step.

## When to use it

- You need one production, and its form matters: a table to read, a list to choose from,
  a JSON value for a script.
- The production feeds the next step: declare the form the next step takes, and pp checks
  it before handing it over.
- When the work is free and takes many productions, use `WORK` instead (see `steps/work`).

## What refuses

- An `output:` that names a form your instance does not know refuses when the document is
  read (see `outputs/formats`).
- A called document whose `input:` is not the form you produce refuses `format-mismatch`
  (see `outputs/input`).

## The demonstration

- `procs/NOTE.md` — an `INFER` without `output:`: `any`, said to the principal.
- `procs/TALLY.md` — an `INFER` with `output: table`, said to the principal.
- `procs/COUNT.md` — an `INFER` with `output: json`, then `CALL REPORT.md`.
- `procs/REPORT.md` — the called document: it declares `input: json`, so COUNT's list goes
  to the tool and is judged before REPORT opens, and REPORT sees it under `input`.

## The test

`tests/patterns/steps/infer.py` plays `NOTE.md` and `TALLY.md` and checks their lines and
closings; then plays `COUNT.md`: its line goes to the tool, an empty production and a broken
JSON each repair, and a good list opens `REPORT.md`.
