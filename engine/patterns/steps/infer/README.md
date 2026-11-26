# infer — ask the agent for one production in a given form

## What you write

One line in your `proc:`: `INFER`, with no argument. The body of your document says what to
produce; the key `output:` in the front matter names its form — one of the forms your
instance lists in its `output.md` (`json`, `table`, `line`…). Without `output:`, the form is
`any`: whatever the step asks.

## What you get

- The step's line names the form and where the production goes: `INFER table => terminal`.
- When no later step takes the production, it goes to the principal. On `=> terminal` the
  agent hands it to pp by the print call, `./pp <key> -print <DOCUMENT> - <<'EOF'`, the production, `EOF`, the
  document the line names in brackets; pp keeps it as handed, even the last production of its
  output (see `control-flow/root`). When it is the document's last step, the passage is over
  once it is printed.
- When the next step takes the production — a `PICK` (see `steps/pick`), or a called
  document that declares `input:` (see `outputs/input`) — it is handed to pp instead, and its
  line names how: `=> tool` for a form written on the call (`./pp <key> "<production>"`),
  `=> tool_heredoc` for a form piped by a heredoc (`./pp <key> - <<'EOF'`, the production,
  `EOF`). No closing repeats the call.
- Before a `PICK`, the form is the engine's `list`, whatever `output:` says: you write
  nothing for it.
- A called document that declares `input:` opens on your production and sees it under
  `input`, served once when it opens.
- A production that goes to the tool is judged when it arrives. An empty one, or one that
  breaks its form (a `json` that does not parse, for instance), is a miss: the document
  replays from its first step as a REPAIR, the miss named under DEVIATION. A good one is
  handed to the next step.
- A print is judged on its form too: an empty one, or one that breaks its form, is refused at
  the return of the call and stays due -- no document replays. After `work_repairs_allowed`
  refusals pp lifts it and keeps nothing; the run goes on.

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

- `procs/NOTE.md` — an `INFER` without `output:`: `any`, printed for the principal.
- `procs/TALLY.md` — an `INFER` with `output: table`, printed for the principal.
- `procs/COUNT.md` — an `INFER` with `output: json`, then `CALL REPORT.md`.
- `procs/REPORT.md` — the called document: it declares `input: json`, so COUNT's list goes
  to the tool and is judged before REPORT opens, and REPORT sees it under `input`.

## The test

`tests/patterns/steps/infer.py` plays `NOTE.md` and `TALLY.md` and checks their lines and
closings; then plays `COUNT.md`: its line goes to the tool, an empty production and a broken
JSON each repair, and a good list opens `REPORT.md`.
