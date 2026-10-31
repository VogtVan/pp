# The bench of Procedural Prompting

One harness, the product's: `tests/harness.py`. The tests of every AREA live at
home under their own `tests/` -- same structure, same harness. `./pp -test` (at
the source: `uv run engine/pp.py -test`) is ONE command: a vendored engine hands
the call over to the product's own, so the conductor the scenarios import and the
one they install from are the same code, and the pass opens on a line naming the
engine it plays and its version. It collects every area, lints the
structure, plays every scenario in its own process and reports the count,
scenario by scenario. The COUNT is what a pass renders: the table, the time targets, the
failures and the verdict -- the lines a scenario printed wait for `-detail`,
and a line under the table says how many are waiting. A scenario that FAILS
renders its lines with its ✗, flag or no flag: a red pass names itself in one
call. What a scenario printed is ALL of it, whichever stream it wrote on:
nothing a pass prints stands outside its report. `-serial` plays them one
after the other, output live; a selection names an area (`kit`, `plan`), a
scenario, or a leading path.
An area whose `tests/` carries an `opt-in` file stays out of a pass without a
selection and plays when a selection names it -- the area, a path under it or
one of its scenarios; the lint reads it all the same.
Two TARGETS ride the report and never fail it: `SCENARIO_TARGET` (20s, a scenario
named past 22 s -- `SCENARIO_TOLERANCE`, 10 %, rule 10) and `WALL_TARGET` (60s) are
what the bench refuses to exceed, set from what it
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
    │   └── patterns/<category>/<pattern>/                   the engine's PATTERNS: what a proc's author writes and gets -- a README and the demonstration procs, copied into every instance with the engine
    ├── bases/  packages/  template/  adapters/              its documents and bundles -- the base (kit) under bases/, the packages under packages/
    ├── tools/  campaign/                                    the CAMPAIGN's launcher: a SET of procs played on a harness -- the modelled LLM at every pass (`tests/conduction/`), a REAL harness on the operator's word, never at -test (tools/campaign/README.md)
    ├── tests/                                               the PRODUCT's bench -- ./pp -test [-serial] [area|name|path ...]
    │   ├── README.md                this document: the structure, written once
    │   ├── harness.py               Env · Town · expect_exit · the factories · the parallel runner · the lint
    │   ├── witness/kit/             the bench's STAND-IN for the base: what the engine asks of a base and nothing of the kit's text (rule 9)
    │   ├── witness/packages/        the witness packages a root case pins (`wit`, `sayer`, `greeter`, `motor`), never a real one
    │   ├── engine/                  the MECHANICS of conductor/, text-agnostic -- one directory per sector
    │   │   ├── core/  state/  reading/  execution/  rendering/  packaging/
    │   ├── patterns/<category>/     one scenario per pattern of engine/patterns/: it plays that pattern's demonstration procs on the stand-in (rule 9)
    │   ├── console/                 the CLI as the operator drives it
    │   ├── adapters/                the wiring per host and the marble channel
    │   └── conduction/              the CONDUCTION sector (rule 11): `roots/` the set of the situations the campaign plays, `_skills/` its witness skill, `evidence/` the light artifacts of the campaigns kept in git, `launcher/` the launcher's verbs, `zones/<zone>.py` one scenario per zone of the conduction, `census.py` the census, `README.md` the set's own document
    ├── bases/<b>/tests/             a BASE's tests (kit)
    │   ├── engine/                  what the base's documents make the engine do (the member's identity is behavior)
    │   └── skills/                  the base's scripts, when it carries any
    └── packages/<p>/tests/          a PACKAGE's tests -- skills/ engine/
        └── engine/_<name>.py        a SUPPORT module: what the area's scenarios share, never a scenario itself (rule 10)

## The rules -- what the lint refuses before any scenario plays

1. A scenario proves BEHAVIOR -- the logic, the code, the structure, the chain
   of the procedures -- and never the wording of a text an agent or a user
   reads. No scenario keeps a document's text: that text is the author's, and
   the scenarios that PLAY the document (its chain, its offers, what it serves)
   are what redden when it breaks.
2. A scenario compares no sentence an agent or a user reads. What it compares
   is a field (`--json`), an event, an exit or refusal code, a structure, one
   call or rendering with another, or a constant read from the module that
   prints it -- never a sentence typed again in the test. A literal of a
   sentence's length (`PINNED_CHARS` 40, `PINNED_WORDS` 6) inside a comparison
   or an assert is such a sentence; a `held()` line's wording is prose for the
   reader, never a comparison. The lint reads every scenario and support
   module for such sentences (`pinned()` in the harness) and, with
   `PINNED_REFUSES` on, refuses every file that compares one before any
   scenario plays; switched off, a pass would only end on a `⚠` line naming
   them, its verdict unmoved. What breaks this rule is CORRECTED, never allowed: there is
   no allowlist.
3. A scenario lives in the sector of what it proves; its name is english kebab
   and says its subject.
4. The lint checks rule 3, the support modules of rule 10 and rule 2 at every
   `./pp -test`; a refusal names the file and the rule, nothing plays.
5. This structure is written here once; the pp plans carry it as a law (a batch
   that touches a test respects it, the lint proves what it can).
6. The bench owns its environment: at its entry it drops every `PP_*` variable
   the session carries and names what it dropped. A `PP_MARBLE` or a `PP_RUN`
   inherited from the operator's shell would make a throwaway instance boot as a
   wired one, and every child of the bench inherits the cleaned environment,
   whatever launches it -- the promise of hermeticity is kept at one site.
   The same entry gives the pass its OWN uv cache: uv builds one environment
   per script path, and every house of the bench is a new path, so in the
   user's cache those environments would stay forever (181 for one whole pass,
   14 783 standing on 2026-10-18). The pass's cache stands beside the user's
   (`<uv cache dir>/../pp-bench-uv/<pid>-…`), on the same filesystem, because uv
   moves a wheel it unpacks into the cache by a rename. Every bucket of it is a
   link to the user's, so the wheels are shared, except `environments-v2/`,
   which is its own. `UV_CACHE_DIR` names it for every child, and it is
   removed when the pass ends; a pass directory whose bench died is removed at
   the next entry. The same entry gives the pass its OWN temp, on disk:
   `pp-bench-tmp/<pid>-…` under the user's cache, which `TMPDIR`, `TEMP` and
   `TMP` name for every child. Every house of the bench is installed under the
   temp, and the system's may be held in RAM (WSL's `/tmp`, a 5.9 GB tmpfs, which
   a whole pass filled until the machine fell on 2026-10-26 and 2026-10-31). The
   pass opens on a line naming that directory; it is removed when the pass ends,
   and one whose bench died is removed at the next entry.
7. A scenario that sweeps the repository ENUMERATES the published product --
   the root's own documents, then `adapters/ bases/ design/ engine/
   packages/ template/ tests/ tools/` -- and never excludes its way there: a
   member's instance (`.pp/` with its plans, its records, its vendored copies),
   the projected cards and whatever is born at the root tomorrow stay outside.
   The operator's matter is not the product, and a sweep that reads it judges
   the wrong thing. `tests/console/dead-patterns.py` is its one reader today.
8. A scenario's DETAIL is everything it wrote, on either stream: `play()` sends
   stdout AND stderr to one buffer, in the order the scenario
   wrote them, and the report alone decides what leaves. A free stream prints
   beside every report, before the pass even has a verdict -- 59 % of what a
   full pass printed on 2026-09-20, the manual of a skill twice over. The
   `live` mode wraps nothing, by design: `-serial` and a single scenario are
   asked for their detail at the fly.
9. The ROOT area proves the engine on the bench's STAND-IN for the base, never on
   the kit's text: `tests/witness/kit/` carries what the engine asks of a base --
   `package.yaml`, `procs/BOOT.md`, `procs/TURN.md` -- and one optional
   `system/SYSTEM.COMMON.md`, the section a base may give its marble, and nothing else, no member, no law, no settings; a script of a witness package is a
   fixture, never a scenario. A root scenario's environment
   installs from a WITNESS source, the product copied with that stand-in in the
   kit's place and the witness packages of `tests/witness/packages/` beside the
   product's (`bench.env()`, `bench.install()`, `bench.engine()`; an explicit
   `base=` names another base, the stand-in renamed). What a case needs beyond
   that, it writes at run time -- a document `attach:`ed or `mount:`ed at the
   base's sockets, a `PP_DOOR` the console opens at `-new`, an overlay of `TURN`
   -- and that is what it proves; a case that proves what the KIT's text makes
   the engine do lives under `bases/kit/tests/`. Every other area stands on the
   product's own kit. No root sector
   stands on the kit through `bench.env()`: `KIT_BOUND` in the harness is empty, and the probe
   `console/bench-self` keeps it so; the conduction sector (rule 11) stands on it
   through the house the campaign's launcher installs, by design. A member a case needs is written at run
   time by `env.write_member()` (`procs/MEMBER.md`, attached at `boot.initialize`); a package
   a case needs is a WITNESS package under `tests/witness/packages/` -- `wit` (a
   manifest), `sayer` (a `system/` fragment), `greeter` (a document mounted at
   `boot.initialize`, a settings fragment), `motor` (a `user/` member, the boot checks,
   a counting signal with its family) -- never a real one of the product.
10. A scenario is ONE house and ONE subject, and it stays under `SCENARIO_TARGET`,
    within a TOLERANCE of 10 % (`SCENARIO_TOLERANCE`: 22 s for a target of 20 s): a
    file that chains independent parts is split, one scenario per part, and a part
    still over the target is cut by case when its cases do not need one another. A
    `⚠ … over the 20s target (+10% tolerated)` line of a pass -- a scenario past the
    target AND its tolerance -- is an ORDER to split; within the tolerance the pass
    says nothing. The time of a scenario is not deterministic, so a target never fails
    a pass, and the 10 % absorb what the load of a pass adds to a scenario that holds
    its target alone; but the wall of a pass is its slowest scenario, and one long file cancels the
    parallelism of all the others (measured on 2026-10-07: one scenario of 3 010
    lines held the wall at 303 s while the other 228 were done in 67 s). What the
    scenarios of an area SHARE -- a witness, the declarations, the factory of their
    houses, a run replayed by several -- lives in a SUPPORT module beside them,
    `_<name>.py`: the runner never collects a file whose name opens on `_`, nor
    anything under a directory whose name opens on `_` (the MATERIAL of a sector: a
    witness skill of a set, `conduction/_skills/`), the lint refuses a support module
    that exposes `scenario(bench)`, and a scenario loads it by `support(__file__,
    "<name>")` from the harness -- the nearest `_<name>.py` beside it or above it in
    its sector, so the sub-directories of a sector (`conduction/zones/`) share their
    sector's. A scenario never imports
    another scenario, and never reads what another scenario wrote: each installs its
    own house.
11. The CONDUCTION sector, `tests/conduction/`, proves the CONDUCTION -- what the engine's
    texts make an agent do -- and not the engine's mechanics: its scenarios play the
    campaign's launcher (`tools/campaign/campaign.py`) on a throwaway house installed
    from the source WITH the product's kit (the one exception to rule 9: the real
    campaigns play on the kit, and the modelled LLM must agree with them on the same
    texts), under the MODELLED LLM alone -- a real provider is never launched by the
    bench -- and read verdicts, counts and zones on the coverage and the sheet of their
    own play, never a text of a block and never the versioned evidence. One scenario per
    ZONE of `adapters/model/semantics.py` `ZONES` under `zones/<zone>.py`, two
    constants each -- `ZONE`, `ROOTS` (the fewest roots of the set that cross it) --
    and one call to the support's `zone_case`, which plays them on the three channels
    and holds the zone crossed on every channel it EXISTS on (the data's, `ZONES`: a
    scenario declares no channel); a zone no root crosses yet is declared `silent:` at
    the set's manifest with the batch or the step that owes it. `census.py` reads those
    constants on the scenarios' syntax tree and refuses by name a zone neither carried
    nor silent, a scenario of a zone ZONES does not know, a zone both silent and
    carried, a silent zone nobody owes, a scenario that declares CHANNELS, a root of the
    set no zone scenario plays. The light artifacts of
    the campaigns (`evidence/campaigns/<date>/`, kept in the source repository) are what
    the launcher's census of the zones reads; `./pp -test conduction` plays
    the sector at any hour.

## The harness, in short

- `bench.env(name, packages=(), pin=True, bare=False, base=None)` -- an ENVIRONMENT
  on demand: a pp instance installed in a temp dir from the engine the scenario's
  area stands on (rule 9); `bare` drops the compiled marble and the settings (the
  engine's mechanics alone); `base` names another base.
- `bench.install(target, packages=(), **kw)` -- an instance installed BY HAND, from
  that same engine; `bench.engine()` -- that engine, for a case that drives the
  console's own `-install`; `bench.source()` -- the root of the source that engine
  lives in, for a case that copies or reduces a source of its own;
  `bench.source_with(base)` -- a witness source carrying `bases/<base>`, made once
  per bench.
- `env.write_member(front, body, proc, name)` -- the member a case needs, written at run
  time: `procs/MEMBER.md` attached at `boot.initialize`, its laws, offers and serve rows in
  `front`, the steps it plays in `proc`; `member_of(made, ...)` does the same for an
  instance installed by hand.
- `bench.town(names)` -- several environments side by side, a Town.
- `env.conductor(key)` -- the engine's facade, fresh at every call, like the
  console's; `env.cli(...)` -- the console itself; `env.write(relpath, text)` --
  the operator's edit.
- `bench.held(label, detail)` -- one ✓; `bench.expect(code, call)` -- an engine
  refusal (`Refusal`); `bench.expect_exit(code, call)` -- a script's refusal
  (`SystemExit`, the code on stderr); `bench.over(block)` -- the END block.
- `support(__file__, name)` -- the SUPPORT module `_<name>.py` beside the calling
  scenario (rule 10): what the scenarios of an area share, loaded by path like a
  scenario and never collected as one.
- A scenario is a file exposing `scenario(bench) -> int`; its cases play in the
  declared order on the environments it makes; it depends on no other scenario --
  what it shares with its area lives in the area's support module.
