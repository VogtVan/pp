# The operator's console

This file covers the `./pp` console at the workspace root: its own verbs, the commands packages add to it, what a launched script knows, which instance and machine a call plays, and how a package is switched off.

- [The operator's console](#the-operators-console)
  - [The eight verbs](#the-eight-verbs)
  - [The packages' commands](#the-packages-commands)
  - [What a launched script knows](#what-a-launched-script-knows)
  - [Which instance a call addresses](#which-instance-a-call-addresses)
  - [Where the machine lives](#where-the-machine-lives)
  - [Which base an instance stands on](#which-base-an-instance-stands-on)
  - [The rest passes through](#the-rest-passes-through)
- [Switching a package off](#switching-a-package-off)
  - [A package that may use another](#a-package-that-may-use-another)
- [See also](#see-also)

## The operator's console

The install writes two scripts at the workspace root:

- `pp` (POSIX);
- `pp.cmd` (Windows: `.\pp`).

Every block's closing names them. They are **the one spelling** of the conductor, for the agent and for you.

### The eight verbs

Eight bare verbs are the operator's own. They are resolved before any skill name.

| Verb | What it does |
|---|---|
| `./pp upgrade` | Every pinned package moves to the version the source holds now, re-materialized. Standing runs are RENEWED: each keeps its key and reopens at its next call (see "A run an upgrade renewed" in [The instance on disk](instance.md#the-instance-on-disk)), and the count is told. Already current: a statement, nothing touched. `./pp upgrade --from <checkout>` names the instance's source anew first, then upgrades from it. When the source carries another engine, that engine is copied under the machine FIRST and the whole upgrade is delegated to it (below). At a machine, it DESCENDS to every instance that borrows it (see [Where the machine lives](#where-the-machine-lives)). |
| `./pp add <package>` | One more package into this instance, its prerequisites pinned. User-level files are protected: an edited file survives as `.old`, and a fresh sibling is offered instead. |
| `./pp remove <package>` | One package out. Refused while another pin requires it. |
| `./pp repo <name>` | A sibling workspace, installed with this instance's packages and wired with the providers detected here. |
| `./pp doctor` | Repair in place at **constant pins**: re-materialize, recompile, rewrite the console, refresh the wired projections. Standing runs stand (`upgrade` is the void). It rewrites only what moved and names each file it rewrote, so a second `doctor` rewrites nothing. When the source carries another engine, the whole repair is delegated to it, as `upgrade` does. At a machine, it descends too. |
| `./pp acquit <vector>` | A treated signal vector stops asking: its counter and its latch fall together (see [The bus and the diagnostics](misses.md#the-bus-and-the-diagnostics)). |
| `./pp version [-json]` | The source checkout and the pinned versions. In an instance that borrows a machine: the machine's source, the machine itself, and the upgrade to play there. `-json` says them as one object `{source, machine, engine, at_source, packages}`: `machine` is null outside a borrower; `at_source` is the source's engine when it differs, else null. |
| `./pp help` | The console's usage: its own verbs, then the packages' commands. Any other word refuses `verb-unknown` in one line, naming the package of the source that declares it as a command when one does. |

#### The engine in place judges nothing of the source

`./pp upgrade` runs the instance's OWN engine. The source may hold manifests, sockets or documents that engine cannot read.

So when the source carries another engine version, `upgrade` copies the source's engine under the machine (`.sys/engine`) before it reads anything of the target. It then delegates the WHOLE upgrade to that copy, under the same maintenance hold:

```text
uv run .sys/engine/pp.py --instance <.pp> upgrade
```

The code N+1 reads the manifests, judges the composition, moves the pins, renews the runs and composes the settings. The engine in place only relays its lines (`engine <old> -> <new>` among them).

A copy whose upgrade could not finish refuses `delegation-failed`. It leaves a machine the next `./pp upgrade` plays as it stands: the manifest's `engine` mark moves with the delegated upgrade, never before.

`doctor` follows the same rule: the source's engine is copied first and the whole repair is delegated to it.

`add` and `remove` move no engine. When the engine that runs them, or the copy the manifest names, is behind the source's, they refuse `engine-behind` and write nothing. Run `./pp upgrade` first, then replay the verb.

#### An instance on an older engine

An instance standing on an engine OLDER than that rule (`0.1.0-beta.76` and before, or `0.2.0-beta.4`) plays it once from the source's side:

```text
uv run <source>/engine/pp.py --instance <workspace>/.pp upgrade
```

The source's engine upgrades the instance, the launcher is rewritten, and `./pp upgrade` works again from there. The instance's own documents are never touched by that step.

#### Two properties to know

- **The scripts are the machine's own.** They are the exception at your root: rewritten byte-stable by install, doctor and upgrade, never yours to edit. An edit does not survive; that is what keeps the agent's channel unbreakable. At a first install, a foreign file already named `pp` refuses (`pp-name-taken`), and nothing is overwritten. The engine underneath answers the same calls: `uv run .pp/.sys/engine/pp.py …` is the repair path when the console is gone.
- **The eight verbs are reserved names.** A skill taking one of them is unreachable through `pp <name>`, and the build says so (a `skill-shadows-verb` warning, never a silence). A package command never takes one either (`command-taken`).

### The packages' commands

The packages' commands resolve next, before the run's key.

#### Declaring and running a command

A package declares its commands in its manifest: `contributes: commands: [{verb, skill [, args]}]`. Then `./pp <verb> [args]` runs the declared skill in a subprocess; the engine imports no package code.

- The manifest's `args` come first, yours after.
- The skill's stderr is written to yours as the skill goes, so a long skill can say where it is.
- Its stdout is relayed once it ends.
- Its exit code is returned as is.

What the skill says to the bus (`::push`, `::clear`) is harvested on a clean exit. A `::mount` has no run to land in at the console: it refuses `mount-without-run` after the skill ran.

`./pp help` lists every command after the console's own, in the composition's order (requires topology, then declaration), with its package and the description its skill's contract carries.

#### A command at the terminal

A command declared `tty: true` — `{verb, skill, tty: true}` — hands the skill the terminal instead. Stdin, stdout and stderr are the console's own; nothing is captured or read back, so a skill that draws a screen owns it. Its exit code is returned as is.

Such a skill never speaks to the bus: a `::push` or a `::mount` it prints reaches the screen like any other line.

The engine opens no terminal and tests none. It hands over its streams, whatever they are, and the skill judges them. `tty` is `true` or `false`, nothing else.

A Ctrl-C at the terminal reaches the console and the skill alike. The console ignores it while the skill plays and waits for the skill to end. What the skill does with the signal, and its exit code, are the answer.

#### Asking for a relaunch

One exit code asks more. A skill that writes `then: upgrade` or `then: doctor` in its package's space of the metadata and exits on `RELAUNCH` (75) asks the console to:

1. give back its hold on the machine;
2. play that verb at the terminal;
3. play the same command again, told `PP_RELAUNCHED=<verb> <exit code>`.

A command played again that asks again gets its code back: one relaunch, never a loop. Any other verb refuses `relaunch-invalid`, and nothing is played.

The post's `U` is its first user. The post of a house (the `ui` package's terminal screen) is described in [packages/ui/README.md](../../packages/ui/README.md#the-post-of-a-house).

#### Conflicts

The conflicts are settled at the build, and nothing is written:

| Refusal | When |
|---|---|
| `command-taken` | a verb of the console, or declared twice |
| `contribution-malformed` | a verb outside `[a-z][a-z0-9-]*`, or shaped like a run's key (six hex digits); a `tty` that is neither `true` nor `false` |
| `command-skill-unknown` | a skill that is no script of the composition |
| `name-unprefixed` | a verb that does not wear its package's name — `<package>-<verb>`, or the package's name alone |

At the console, a declared command whose script is gone refuses `command-broken`. An undeclared word still answers the usage.

### What a launched script knows

#### Its run

Every script the engine plays under a keyed call finds the run's key in its environment as `PP_RUN`. This covers a payload provider, a sink, an `exec:`, a family's verifier and a `-s` gesture. `PP_RUN` is set once where the engine binds the run, inherited by every subprocess it launches, and read in the same process by a gesture.

Through the engine's face, a script reads that run. `conductor.context.current(<instance>)` gives:

| Reading | What it says |
|---|---|
| `key` | the run's key |
| `exchange()` | the exchange under way, 1 at the first |
| `is_new()` | the run's first exchange |
| `is_boot()` | the run's first exchange, the one where `-compacted` was declared, or the one a renewed run reopened at |

It is a reading of the run's slot, never a write.

Without `PP_RUN` the face refuses `context-no-run`. The keyless console (`./pp <command>`, `./pp`, `-stats`) drops whatever the shell inherited, so a run is designated by a command's key alone. A key no run holds refuses `run-unknown`.

#### Its instance and its engine

A script the engine launches (a payload provider, a sink, a check, a command, a gesture) is a file of a bundle in the vendor of a MACHINE. It imports the engine of the machine it finds by walking up from its own file.

The engine names, in the script's environment, `PP_HOME`: the instance the call serves. The script takes it as its instance when that instance BORROWS the machine the script lives in; otherwise its instance is the machine's own.

A neighbour's script, launched by another instance's, keeps its own home: the caller's instance does not borrow the neighbour's machine.

#### Its settings

A script never opens `SETTINGS.md` itself:

- it reads a value through `conductor.settings.of(<instance>)`;
- it writes one through `conductor.settings.write(<instance>, <key>, <value>)`, the one face that poses a setting.

The key must be one the instance knows: a protocol key, a key a pinned package's fragment declares, a switch `package.<name>`, a `cap.<sector>`, a `material.<name>`. Any other refuses `settings-invalid`.

The write changes ONE line of the front matter. The line is rewritten in place, or added before the closing `---` when absent, and every other byte stays as it was.

The value is judged by the same reading `of()` makes. A value the reading would refuse is refused by the write, `settings-invalid`, and the file stays as it was. The call returns the previous value, empty when the line was absent.

Fixture: `tests/engine/state/settings.py`.

### Which instance a call addresses

Every call may say it: `--instance <dir>` comes first. `<dir>` is the instance directory itself (`<workspace>/.pp`), and the flag may stand anywhere in the call.

Without it, an INSTALLED engine conducts the instance it lives in. The console `./pp` passes nothing, and a `PP_HOME` inherited from another instance's script never redirects it.

The `PP_HOME` variable serves an engine that has no instance of its own: the product's checkout, the case of a harness a script launches.

The flag lets the product's own engine open or advance a run on any instance from any directory (`uv run pp/engine/pp.py --instance <dir> -new`). A directory carrying no `instance.yaml` refuses `instance-missing`; nothing is played.

### Where the machine lives

An instance that carries `.sys/engine/` plays its own machine. This is the classic instance: the engine and the bundles copied under it.

An instance that carries none BORROWS the machine of the nearest instance of the same name above its workspace (`<ancestor>/.pp`). It plays that machine's engine, its versions and its composition, and pins nothing of its own. Its own `package.<name>: off` switches narrow what it plays.

Nothing is written to say so: the tree is the authority. No machine above refuses `machine-missing`.

#### Birth

`./pp -install <dir>` played at the console of an installed engine seeds an instance that BORROWS when `<dir>` lies under a machine. It writes:

- the root, seeded;
- a manifest that says who it is (slug, birth) and nothing of a machine;
- its records, seeded;
- its SETTINGS, composed;
- its launcher: `pp`, running the machine's engine by its relative path and addressing the instance (`--instance`);
- its marble and catalog, compiled.

It writes no `engine/` and no `vendor/`. `-own` gives it a copy of the machine instead. Packages and `-base` are the machine's (`install-borrowed` otherwise).

Played by the product's engine, `-install` copies the machine as always.

#### The machine's verbs

`doctor`, `upgrade`, `add` and `remove` are played at the machine. In an instance that borrows one, they refuse `machine-borrowed`, naming the machine.

At the machine they DESCEND its workspace:

- Every directory below whose `<dir>/.pp/` is an instance without an engine, and whose manifest names no `source:` and no `packages:`, is a borrower.
- A directory whose `.pp/` carries its own machine, or names one (the clone of an instance, whose git ignores the copies), belongs to that machine and is not entered.
- The hidden directories are never walked.

The machine and its borrowers share ONE maintenance lock (see "Maintenance under living runs" in [The instance on disk](instance.md#the-instance-on-disk)). While a pp process lives at the machine or at any borrower, these verbs refuse `maintenance-busy`.

`upgrade` rewrites the machine, then does each borrower's STATE work (SETTINGS, seeds, launcher, marble and catalog: `<dir> restated`) and closes its runs. `doctor`, `add` and `remove` restate the borrowers too; their runs stand.

### Which base an instance stands on

`-install <workspace> [packages…] -base <package>` composes the instance on the named package instead of the kit:

- the manifest says `base: <package>`;
- the composition is `[base] + packages`;
- `./pp remove` refuses the base by `package-base`.

A base OWES `procs/BOOT.md` and `procs/TURN.md`; its `system/` is its own to give or not.

The build judges the target before anything is written and refuses `base-incomplete` by name. The target directory does not exist after the refusal.

An install that names no base writes no `base:` and stands on the kit.

### The rest passes through

Anything else passes through verbatim:

| Call | What it does |
|---|---|
| `./pp` | where the run stands, read-only |
| `./pp <key>` | advances it |
| `./pp <key> -s <skill> [args]` | plays a skill (a script called bare mounts its manual) |
| `./pp -test [-serial\|-detail] [-repeat <n>] [area\|name\|path ...]` | runs the engine's fixtures: `-serial` plays them live, `-detail` renders what they wrote, `-repeat <n>` compares n passes and names whatever moved |
| `./pp -stats [<key>\|<days>] [--blocks] [-json]` | says what the runs cost |

The raw engine also accepts `-sync` as its low-level re-materialization primitive. The operator's complete repair at constant pins is `./pp doctor`.

## Switching a package off

A package is composed for good, and yet a session does not always want all of it. Two switches take one out of the CONDUCTION, and they have exactly the same effect.

Nothing of that package is served or played:

- no document, socket, cadence, check, command or overlay;
- no line of the catalog: no entry, no format, no offered name. A `tools:` naming its skill offers nothing, and the catalog leaves to your harness only the names nothing pp composes owns.

Every package whose `requires` names it goes out with it, its cause said.

The base is never switched off, and off is not GONE. The pin, the bundle, the package's section of `SETTINGS.md` and its records stand as they are, so `on` brings everything back.

| Switch | Where | Lives |
|---|---|---|
| durable | `package.<name>: on\|off` in `SETTINGS.md` — yours to write | until you write the other value; seeded `on` when the package enters (install, `add`, `upgrade`, `doctor`), dropped when it leaves (`remove`) |
| for one run | `./pp <key> -disable <package>` · `./pp <key> -enable <package>` — the agent places it on your word | with the run: a run opened beside it plays every package, and `-new` starts with nothing out |

#### What the run's verbs answer

The run's verbs answer with the block that STANDS: a switch is your word, never a step, so the run does not move. Three refusals name their reason and write nothing:

| Refusal | Reason |
|---|---|
| `package-base` | the base of every instance |
| `package-unpinned` | no such pin here |
| `package-in-flight` | a document of that package holds the standing view: a frame of the stack, or a standing mount under any of its address forms (a document by its name, a manual by its skill's name, a file by `<package>:<path>`), each named as the run keeps it. The frame finishes, then the word plays. |

Each one is written to the run's trace, and `./pp -stats` counts them among the period's switches.

#### What a run says it plays

What a run plays is said UNDER the heading of each of its outputs: one cell per pin beyond the base, dependencies first so a cause reads before what it took out. Here, on an instance composing three packages of its own:

```text
▌ pp · run 71ccb9 · 19:28:28 · +0:00:01
▌ alpha on · beta off · gamma off (<- beta)
```

Keyless, `./pp` says the durable state alone when no run stands.

An instance that pins nothing beyond its base says nothing of packages. A moved durable switch recompiles the catalog and the standing rules at the next boot; there is nothing to run.

### A package that may use another

A package names under `optional:` in its manifest the packages it may USE when they are there, beside the ones it `requires`.

A document of it that mounts or attaches at a socket of an optional package (`mount: steering.threads.begin`) is a SOFT reference:

- When the package is in the composition, the document plays at that socket without the package being required.
- When it is not pinned, the document SLEEPS: nothing hooks its socket, nothing serves it, and `pp build` says so once in its warnings (`attach-dormant` for an `attach:`).

The warning, for a `mount:` whose package `steering` is not pinned:

``mount-dormant: `steering.threads.begin` mounted by …/NEXT_MOVE.md -- `steering` is not pinned: the document sleeps``

#### What still refuses

- A socket the present package declares nowhere, or a socket of a package neither required nor optional, refuses as before (`reference-unknown`, `attach-unhooked`, `dependency-undeclared`).
- A name optional AND required, or a package optional to itself, refuses `manifest-malformed`.

Off is not absent. A package switched off is still pinned, so its client's document is not dormant: it simply never plays, since the switched-off package hooks nothing.

## See also

- [The instance on disk](instance.md) — the machine's files, the maintenance lock and the renewed runs the console's verbs act on.
- [The loop and the commands](agent-face.md) — the run's own calls (`./pp <key>`, `-disable`, `-enable`, `-stats`) in detail.
- [The bus and the diagnostics](misses.md) — the signals `./pp acquit` treats.
- [packages/ui/README.md](../../packages/ui/README.md) — the post of a house, the first user of a `tty` command.
