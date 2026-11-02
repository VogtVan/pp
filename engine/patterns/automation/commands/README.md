# commands — a console verb of your package

## What you write

In your package's manifest, under `contributes:`, one `commands:` entry per verb:

    commands:
      - {verb: witness, skill: pp-witness, args: [from-manifest]}
      - {verb: witness-screen, skill: pp-witness-screen, tty: true}

- `verb` — your package's name, or your package's name and a dash before a word of your own.
- `skill` — one of your package's skills (`pp-<package>` or `pp-<package>-<name>`), a script.
- `args` (optional) — the words the script always gets first.
- `tty: true` (optional) — the script takes the terminal itself.

## What you get

- `./pp <verb> …` runs the skill's script with your `args`, then the operator's words; the
  console's own verbs come first, a verb nobody declares refuses.
- Without `tty`, the output is captured: the lines are relayed, the `::push` and `::clear` lines
  go to the bus (see `automation/checks-and-signals`), stderr reaches the caller as it is written,
  and the script's exit code is the console's.
- With `tty: true`, the script owns stdin, stdout and stderr: its lines reach the terminal as it
  writes them, the bus hears nothing, and its exit code is the console's.
- `./pp help` lists your verbs after the console's own, with your package and your skill's
  description.

## When to use it

- An operator's verb that has nothing to do with a run: a status, a maintenance, a screen.
- For a verb the agent plays during a run, offer the skill to its step instead (`-s <skill>`,
  see `composition/door`).

## What refuses

- At the console: a verb nobody declares refuses `verb-unknown`; a declared verb whose script is
  gone refuses `command-broken`; a captured script that prints a `::mount` line refuses
  `mount-without-run` — there is no run to mount into.
- At the build: a verb the console owns refuses `command-taken`; a verb shaped like a run's key
  (six hexadecimal digits) or a `tty` that is neither true nor false refuses
  `contribution-malformed`; a skill nobody carries refuses `command-skill-unknown`; a verb that
  does not wear your package's name refuses `name-unprefixed`.

## The demonstration

- `manifests/witness.yaml` — six verbs: one with `args`, one that refuses, one that tries to
  mount, one slow on stderr, one at the terminal and its captured twin.
- `manifests/taken.yaml`, `manifests/keylike.yaml`, `manifests/skillless.yaml`,
  `manifests/ttyless.yaml`, `manifests/unprefixed.yaml` — the five verbs the build refuses.

## The test

`tests/patterns/automation/commands.py` writes the skills, then plays: a verb before and after
its declaration, the args, the push, `help`, a refusal relayed, a mount refused, a withdrawn verb,
stderr as it comes; the verb at the terminal, its streams, its exit code and its captured twin;
`tty` in the catalog; a broken command; the five manifests refused at the build, nothing written.
