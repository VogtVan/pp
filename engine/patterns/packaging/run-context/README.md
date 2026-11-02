# run-context — a package's script knows the run that started it

## What you write

A script of your package, started by pp: at the entry of one of the package's documents
(`exec:`, see `automation/exec`), as the provider of a payload (`with:`, see `context/payload`),
as a sink (`sink:`, see `outputs/sink`), or as a gesture the agent plays (`-s pp-<package>`). The
script reaches pp's engine through the bootstrap every package carries beside its skills,
`skills/_core.py`, and asks:

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core, home
    conductor = core(__file__)
    ctx = conductor.context.current(home(__file__))

`core` gives the engine of the instance the package is installed in; `home` gives the instance the
call serves — the one that borrows that engine when it has none of its own.

## What you get

- `ctx.key` — the key of the run whose call started the script.
- `ctx.exchange()` — the number of the exchange under way, 1 at the first.
- `ctx.is_new()` — true during the run's first exchange.
- `ctx.is_boot()` — true when the agent's context started from nothing at this exchange: the
  run's first, or the exchange where a compaction was declared (`-compacted`).
- The answer is read, never written: the run is byte-identical after the question.
- Two runs side by side never see each other: each script gets the key of the call that
  started it.
- Under the principal's conduction the exchanges count the same way.

## When to use it

- A script that keeps a record per run, or per exchange: a log line, a count, a stamp.
- A script that must act once per run, or again after a compaction: it reads `is_new()` or
  `is_boot()` instead of keeping its own memory.

## What refuses

- A script started outside any run — by hand, or by a console command without a key — refuses
  `context-no-run`.
- A key that no run holds refuses `run-unknown`.

## The demonstration

- `manifests/alpha.yaml` — the package: it requires the base and opens the point `runner.end`.
- `procs/RUNNER.md` — a root that calls `ASK.md` at every passage and offers `pp-alpha` as a
  gesture.
- `procs/ASK.md` — starts the script three ways: at its entry (`exec: ctx exec`), as the
  provider of `alpha-ctx`, as its sink.
- `procs/CTXDOC.md` — the provider of `alpha-ctx`: `pp-alpha ctx provider`.

The script `pp-alpha` is the package's to write; the test writes it, with the `_core.py` it
carries.

## The test

`tests/patterns/packaging/run-context.py` pins `alpha` with its script, then plays four exchanges
of RUNNER through the console: each path writes the run's key and the exchange's values, a
compaction at the third makes it a boot; the run is unchanged around a gesture; a second run
beside it keeps its own key; the script started by hand refuses `context-no-run`, then
`run-unknown` under a key no run holds; a run opened by its principal counts its exchanges the
same way.
