# proc — write a document that pp plays step by step

## What you write

A document with a front matter between two `---` lines, and in it a `proc:` key: one
step per line, each line a keyword and, for some keywords, an argument.

    ---
    name: STEPS
    kind: proc
    description: draft a note, then do what the operator asks of it.
    proc: |
      INFER
      WORK
    ---

    Draft the note in three lines, then do what the operator asks of it.

`name` is the document's identity: the name a `CALL`, an offer or a serve row uses. `kind`
classifies it: `proc` for a document pp plays, `doc` for one that is only read (see
`context/doc`). `description` is the one line the instance's catalogue of tools shows for it.

The keywords that ask the agent for something: `WORK` (see `steps/work`), `INFER` (see
`steps/infer`), `PICK` (see `steps/pick`) and `PROVE` (see `rules/prove`). The keywords that
pp plays itself, without stopping: `CALL` (see `composition/call`), `OPEN` (see
`control-flow/open`), `SERVE` (see `context/serve`) and `HOOK` (see `composition/hook`). A line `§` cuts the output there
(see `control-flow/section-break`); a line that starts with `# ` is a comment.

## What you get

- pp plays the steps in order, one output at a time. Each output shows the step it
  asks for, and its heading counts the steps: `STEPS{1/2}`, then `STEPS{2/2}`.
- The body of the document, below the front matter, is the context of its first step.
- When the last step is done, the passage is over: the run waits for the principal's
  next message (see `control-flow/root`).

## When to use it

- Whenever the agent must do a piece of work in a fixed order: the procedure holds the
  order, so the agent does not have to.
- Keep one document per piece of work; split a long one into several and join them with
  `CALL`.

## What refuses

pp reads the document when it is played. When it cannot read it as a procedure, it
refuses with one of these codes, and nothing plays:

- `front-matter-missing` — the document has no front matter.
- `front-matter-unterminated` — the front matter opens with `---` and is never closed.
- `front-matter-invalid` — the front matter is not valid YAML, or is not a set of keys
  and values (a list, for instance).
- `procedure-undeclared` — the document is played as a step but has no `proc:` key.
- `unknown-keyword` — a line starts with a word that is not a keyword.
- `instruction-malformed` — a line is not written `KEYWORD [argument]` (two arguments, for
  instance), or a keyword that needs an argument has none (`CALL` alone, for instance).

## The demonstration

- `procs/STEPS.md` — a document with two steps, an `INFER` then a `WORK`.
- The refusing documents: `procs/UNFRAMED.md` (no front matter),
  `procs/UNCLOSED.md` (never closed), `procs/PROSE.md` (no `proc:`), `procs/DANCE.md` (an
  unknown keyword), `procs/CROWDED.md` (a `CALL` with two arguments) and
  `procs/BARECALL.md` (a `CALL` without its argument).
- `front-matter-invalid` has no document here: every instance reads the documents of
  these patterns when it builds, and a front matter that is not valid YAML stops the build.

## The test

`tests/patterns/steps/proc.py` plays `STEPS.md` one step at a time, its body the context of
the first step and the passage over after the second, then plays each refusing document
and checks the code it refuses with. `front-matter-invalid` is checked by the engine's own
bench.
