# The bench of Procedural Prompting

One harness, the product's: `tests/harness.py`. The tests of every AREA live at
home under their own `tests/` -- same structure, same harness. `./pp -test` (at
the source: `uv run engine/pp.py -test`) is ONE command: a vendored engine hands
the call over to the product's own, so the conductor the scenarios import and the
one they install from are the same code, and the pass opens on a line naming the
engine it plays and its version. It collects every area, lints the
structure, plays every scenario in its own process -- the body scenarios
together on one shared environment -- and reports the count, scenario by
scenario. The COUNT is what a pass renders: the table, the time targets, the
failures and the verdict -- the lines a scenario printed wait for `-detail`,
and a line under the table says how many are waiting. A scenario that FAILS
renders its lines with its ✗, flag or no flag: a red pass names itself in one
call. What a scenario printed is ALL of it, whichever stream it wrote on:
nothing a pass prints stands outside its report. `-serial` plays them one
after the other, output live; a selection names an area (`kit`, `plan`,
`body`), a scenario, or a leading path.
Two TARGETS ride the report and never fail it: `SCENARIO_TARGET` (20s) and
`WALL_TARGET` (60s) are what the bench refuses to exceed, set from what it
measures -- a target well above the p90 and well under the slowest names the
scenarios that are a case apart, and no more than five lines of them, the rest
held in one line. A warning that sounds thirty times warns of nothing, so the
measure that justifies the numbers lives beside them, dated.
`-repeat <n>` plays the selection n times and compares the passes: a scenario
whose count or verdict MOVED is named with what it held pass by pass, the
first failing pass renders its lines, and a count that moves is a red of its
own -- what a load-dependent scenario looks like when it does not fail
outright. `./pp -test engine/execution -repeat 10` is how a flake is caught.

    procedural-prompting/
    ├── engine/   conductor/  pp.py                          the product's code
    ├── kit/  packages/  template/  adapters/                its documents and bundles
    ├── tests/                                               the PRODUCT's bench -- ./pp -test [-serial] [area|name|path ...]
    │   ├── README.md                this document: the structure, written once
    │   ├── harness.py               Env · Town · shared() · expect_exit · the factories · the parallel runner · the lint
    │   ├── engine/                  the MECHANICS of conductor/, text-agnostic -- one directory per sector
    │   │   ├── core/  state/  reading/  execution/  rendering/  packaging/
    │   ├── console/                 the CLI as the operator drives it
    │   └── adapters/                the wiring per host and the marble channel
    ├── kit/tests/                   the KIT's tests
    │   ├── body/                    the TEXT kept -- one file per document, NAMED as it (BOOT.py ↔ kit/procs/BOOT.md)
    │   └── skills/                  the kit's scripts, when it carries any (a package's live under packages/<p>/tests/skills/)
    ├── packages/<p>/tests/          a PACKAGE's tests -- body/ skills/ engine/
    └── template/tests/              the template's -- body/ engine/

## The rules -- what the lint refuses before any scenario plays

1. A file under `*/body/` keeps ONE document of its area and bears its name
   (`kit/tests/body/BOOT.py` keeps `kit/procs/BOOT.md`): it reads the
   document at the source and asserts its phrases; where a phrase must REACH the
   block, it renders on `bench.shared()` -- the one environment the body tests
   share, installed once with the system packages, never mutated.
2. Outside `body/`, no phrase of a kept document: the mechanics compare with
   the document read at run time, never with a literal. The reference is the
   TEXT of every document a `body/` test keeps -- not the phrases such a test
   happens to pin. Two things make a literal a pin, and both are needed: it
   rides a COMPARISON or an assert (a `held()` line's wording is prose for the
   reader), and it is long enough to be a SENTENCE (`PINNED_CHARS` 40,
   `PINNED_WORDS` 6). Under that length what a test compares is what the ENGINE
   renders -- `▌ INSTRUCTION`, `=> tool`, `a reading continues` -- which the card
   and the cheat sheets quote because they document it; measured on this bench,
   the length alone accuses 111 files where the two together accuse the 2 real
   ones. What the lint finds is CORRECTED, never allowed: there is no allowlist.
3. A scenario lives in the sector of what it proves; its name is english kebab
   and says its subject -- or, under `body/`, the document's name.
4. The lint checks 1-3 at every `./pp -test`; a refusal names the file and the
   rule, nothing plays.
5. This structure is written here once; the pp plans carry it as a law (a batch
   that touches a test respects it, the lint proves it).
6. The bench owns its environment: at its entry it drops every `PP_*` variable
   the session carries and names what it dropped. A `PP_MARBLE` or a `PP_RUN`
   inherited from the operator's shell would make a throwaway instance boot as a
   wired one, and every child of the bench inherits the cleaned environment,
   whatever launches it -- the promise of hermeticity is kept at one site.
7. A scenario that sweeps the repository ENUMERATES the published product --
   the root's own documents, then `adapters/ design/ engine/ kit/
   packages/ template/ tests/ tools/` -- and never excludes its way there: a
   member's instance (`.pp/` with its plans, its records, its vendored copies),
   the projected cards and whatever is born at the root tomorrow stay outside.
   The operator's matter is not the product, and a sweep that reads it judges
   the wrong thing. `tests/console/dead-patterns.py` is its one reader today.
8. A scenario's DETAIL is everything it wrote, on either stream: `play()` and
   `play_many()` send stdout AND stderr to one buffer, in the order the scenario
   wrote them, and the report alone decides what leaves. A free stream prints
   beside every report, before the pass even has a verdict -- 59 % of what a
   full pass printed on 2026-09-20, the manual of a skill twice over. The
   `live` mode wraps nothing, by design: `-serial` and a single scenario are
   asked for their detail at the fly.

## The harness, in short

- `bench.env(name, packages=(), pin=True, bare=False)` -- an ENVIRONMENT on
  demand: a pp instance installed in a temp dir from the product engine; `bare`
  drops the compiled marble and the settings (the engine's mechanics alone).
- `bench.federation(names)` -- several environments side by side, a Town.
- `bench.shared()` -- the body tests' environment, one per bench, never mutated.
- `env.conductor(key)` -- the engine's facade, fresh at every call, like the
  console's; `env.cli(...)` -- the console itself; `env.write(relpath, text)` --
  the operator's edit.
- `bench.held(label, detail)` -- one ✓; `bench.expect(code, call)` -- an engine
  refusal (`Refusal`); `bench.expect_exit(code, call)` -- a script's refusal
  (`SystemExit`, the code on stderr); `bench.over(block)` -- the END block.
- A scenario is a file exposing `scenario(bench) -> int`; its cases play in the
  declared order on the environments it makes; nothing depends on another file.
