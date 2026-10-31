# writer-skill — one script, the one writer of its record

## What you write

A skill of your package: a folder under the package's `skills/` holding its card, `SKILL.md`,
and its script `pp-<package>.py`. The script reaches pp's engine through the bootstrap every
package carries beside its skills, `skills/_core.py`, finds the instance it serves, and writes
its record through pp's face alone:

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core, home
    conductor = core(__file__)
    LEDGER = home(__file__) / "ledger.txt"
    with conductor.record.held(LEDGER):
        lines = LEDGER.read_text().splitlines() if LEDGER.exists() else []
        conductor.record.replace(LEDGER, "\n".join([*lines, entry]) + "\n")

A proc offers the skill by name (`tools:`, see `composition/door`), and its brief says which
verbs to call.

## What you get

- `conductor.record.held(path)` holds the record's lock while you read and change it:
  writers started together, from different runs, wait for one another and lose nothing.
- `conductor.record.replace(path, text)` swaps the whole file in one move: a reader never sees a
  half-written record and never needs the lock — it reads at once, even while a writer holds it.
- Every change of the record goes through the one script: its guards are the record's guards.
  A guard that refuses prints its code and exits 2 before anything is written.
- The agent calls the script as a gesture, `-s <skill> <verb> …`; what it prints comes back in
  the tool result.

## When to use it

- Any record the work keeps between exchanges or between runs: a ledger, a register, a list of
  what is done.
- A record several runs may touch at once.
- To write the agent's production into a record without a gesture, hand it to a sink
  (`outputs/sink`); to update a record when a document enters, play the script by `exec:`
  (`automation/exec`).

## What refuses

- The script's own guards, by the codes you give them: an entry it cannot take, a budget it
  exceeds — each one exits 2 and writes nothing.

## The demonstration

- `manifests/ledger.yaml` — the package, which requires the base.
- `procs/LEDGERED.md` — the package's proc that offers `pp-ledger` and tells the agent to record
  each entry through it.

The script `pp-ledger` is the package's to write; the test writes one with two verbs, `add` and
`read`, and two guards, an empty entry and an entry past its budget, with the `_core.py` it
carries.

## The test

`tests/patterns/packaging/writer-skill.py` pins `ledger` with its writer, then plays LEDGERED: the
step offers the writer; eight writers from eight runs add at once and every entry lands whole;
under a held lock a writer waits and the record stands still while a reader reads it at once; the
guards refuse by their codes, the record unchanged.
