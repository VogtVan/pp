# pick — have the agent choose one value from a list

## What you write

Two lines in your `proc:`: a step that produces the list, then `PICK <name>`, where the
name says what is chosen (`PICK candidate`). Nothing else: the step before a PICK takes
the engine's form `list` by itself, whatever your document's `output:` says (see
`outputs/formats`).

    ---
    name: TRIAGE
    kind: proc
    description: list the candidates, then elect one.
    proc: |
      INFER
      PICK candidate
    ---

    List the candidates by their short names, then elect one.

## What you get

- The `INFER` goes to the tool, in the form `list`: its line says `INFER list => tool`,
  its closing pipes `<list>` by a heredoc, and the instance's `output.md` defines the form — a JSON array of strings or
  numbers, each once, none empty.
- The list is judged when it arrives. A text, a list of objects, an empty array or a
  repeated value is a miss; a number is offered as its text (`[1, 2]` offers `1` and `2`).
- The PICK's block shows the list under OPTIONS, one value per line, then the line
  `PICK candidate options => tool`, then a CONTINUE over the call `./pp <key> <options>`:
  the chosen value goes in place of `<options>`.
- A value from the OPTIONS, written exactly, is taken, and the procedure goes on. Any
  other value is a miss.
- A miss replays the document from its first step as a REPAIR: the agent lists again,
  then chooses again; the DEVIATION names the value or the list that missed.
- Your document's other steps keep its own `output:`: only the step before the PICK takes
  the list.

## When to use it

- The agent must choose among values it finds itself, and the choice must be one of them:
  a verdict, a next move, a file among several.
- You want the choice written on the tool's call, where pp can check it, and not in prose.

## What refuses

- A `PICK` with no step before it that produces a list refuses `options-empty` when the
  document is played; nothing plays.
- A list that reaches the PICK from another document, without having been judged as a
  list to choose from (a called document that declares `input: json` and opens on its
  `PICK`), refuses `options-invalid` when it is not a list of strings or numbers.

## The demonstration

- `procs/TRIAGE.md` — an `INFER`, then `PICK candidate`: the list without a word of `output:`.
- `procs/CHOOSE.md` — a `PICK` alone: it refuses `options-empty`.
- `procs/BALLOT.md` — `CALL SHORTLIST.md` then `CALL ELECT.md`: `SHORTLIST.md` produces the
  list, `ELECT.md` takes it by `input: json` and picks from it; a list of objects refuses
  `options-invalid`.

## The test

`tests/patterns/steps/pick.py` plays `TRIAGE.md`: the OPTIONS, the PICK's line and closing,
a value taken, a value outside that repairs, every malformed list that repairs, numbers
offered as values; then `CHOOSE.md` and `BALLOT.md`, each with the code it refuses.
