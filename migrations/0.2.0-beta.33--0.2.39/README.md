# Migration 0.2.0-beta.33 → 0.2.39

This migration brings a house installed at version **0.2.0-beta.33** to version **0.2.39**: the
house itself, every agent under it and every team in it. Between these versions pp moved its
records into one store per instance, renamed the sections of its plans and the family of their
keys, and changed where a team's intention is written. `./pp upgrade` alone moves the code but
not this data, so 0.2.39 would refuse or ignore it. This migration moves the data too.

The rules every migration follows (backup first, no pp running, `--dry-run`, the order of the
steps, the exit codes) are in [the index](../README.md). This page says what this one does.

## Who needs it

You need it if `cat .pp/.sys/engine/conductor/core/version.py` in your house says
`VERSION = "0.2.0-beta.33"`. A house at any other version is refused (`house-version`).

## Before you start

- **The source at 0.2.39, with this migration in it.** Clone the tag of this migration:

  ```sh
  git clone --branch migration-0.2.0-beta.33--0.2.39 https://github.com/VogtVan/pp
  ```

  or download and extract
  `https://github.com/VogtVan/pp/archive/refs/tags/migration-0.2.0-beta.33--0.2.39.tar.gz`.
  Do not use the tag `0.2.39`: it was published before this migration and has no `migrations/`
  folder. A copy at any other version is refused (`source-version`).
- **Nothing running.** Close the post and every chat, and stop every team with
  `./pp team stop <name>`. If a pp process is still running in the house, the migration is refused
  (`house-busy`). From the end of the check until the migration ends, the house is locked: a pp
  you start in it meanwhile is refused and does nothing.
- **Room beside the house.** The folder that holds the house must be writable and have as much
  free space as the house takes (without its `.git`), even though the backup is compressed.
- **uv**, as for pp itself. No network and no git are needed.

## Running it

From the source at 0.2.39, check first:

```sh
uv run --script migrations/0.2.0-beta.33--0.2.39/migrate.py <house> --from <source> --dry-run
```

Then migrate:

```sh
uv run --script migrations/0.2.0-beta.33--0.2.39/migrate.py <house> --from <source>
```

`<house>` is the folder that holds the house's `.pp/`; `<source>` is the folder of the product at
0.2.39.

## What it does

After the check, the backup and `./pp upgrade --from <source>`, it plays five steps on the data, in
this order. Each step reads every instance before it writes the first one, so a step that refuses
has written nothing itself; the steps before it have, so restore the backup before you try again.

1. **`plans`**: In every plan document of the house, of each agent and of each team (`plans/`):
   `kind:` becomes `template:`; the `phase:` line goes; the blueprint law that 0.2.0-beta.33 wrote
   into every new plan goes, because the 0.2.39 template carries it. A section that still holds the
   instruction text of the old template goes: you never wrote it. A section the new templates no
   longer have takes the name of its successor: `Target` becomes `Expected`, `Arbitrations` and
   `Decisions` become `Choices`, `Survey` becomes `Ground`, `Protocol` becomes `Tests` (in a batch)
   or `Expected`, and `Context` becomes `Ground` (in a phase or a batch). When the successor is
   already there, the old section goes in after its text, under a `### <old name>` title. The
   sections are put in the template's order. Statuses are not changed. A document already on
   `template:` is left as it is.

   Refused when a plan document has no front matter (`plan-unreadable`).

2. **`plan-keys`**: The keys `plan-lot:<address>` and `plan-phase:<address>` become
   `plan:<address>`: the `key` of each step in each instance's `steps.json` and in the plans'
   next-move lines (`.sys/records/events.json`)

   Refused when the new key is already another step's (`key-taken`), or `events.json` does not parse
   (`bus-unreadable`).

3. **`steering`**: `steps.json` moves into the store of its instance: the steps (same ids, same
   fields), the labels, the step counter

   Refused when the file does not parse (`steps-unreadable`), or the store already holds steps
   (`steps-taken`).

4. **`continuity`**: `operations.jsonl` and `history.jsonl` move into the store, each entry keeping
   its date. A last line cut in the middle is skipped, and the count table shows it on its own row.

   Refused when another line does not parse (`records-unreadable`), or the store already holds
   entries (`records-taken`).

5. **`teams`**: The intention that `team new` wrote into `teams/<name>/TEAM-<name>.md` becomes the
   body of `TEAM.md`, word for word. 0.2.39 reads the owner's word there, and renders
   `TEAM-<name>.md` itself at the next start. The front of `TEAM.md` does not change.

   Refused when the body of `TEAM.md` is already written and holds a different text
   (`team-intention`).

It then counts, per instance and per record, what each step found and what it wrote:

| record | before | after |
|---|---|---|
| `plan-documents` | the plan documents | the ones on `template:` |
| `plan-lines` | the lines of your text in them | the ones still there |
| `step-keys`, `bus-lines` | the old keys found | the keys rewritten |
| `steps`, `labels`, `counters` | in `steps.json` | in the store, read back equal |
| `operations`, `history` | in the `.jsonl` file | in the store, read back with the same date and text |
| `operations-torn`, `history-torn` | the cut last line skipped, when there is one | the same number: it is not taken over |
| `team-intention` | the lines of `TEAM-<name>.md` | the ones in the body of `TEAM.md` |

When every count is equal, it removes what 0.2.39 no longer reads. The backup keeps a copy of each:

- in every instance: `operations.jsonl`, `history.jsonl`, `steps.json` and their `.lock` files,
  and `.sys/system.common.md`;
- in every team: `TEAM-<name>.md`, now that its text is in `TEAM.md`;
- in the folder of the house and of every agent: `CLAUDE.md`, `AGENTS.md` and `GEMINI.md`, but
  only if their content is still exactly what the 0.2.0-beta.33 install wrote. A file you edited
  is kept, and the migration names it.

If a count differs, nothing is removed. Last, `./pp doctor` checks the house.

## After it

- If the house has no `next` package, the output says so: a new 0.2.39 house does not have it
  either. Add it with `./pp add next` if you want it.
- The plans keep their statuses. A batch whose todos are all done but which is still open is
  named in the output: close it with `pp-plan done` if you want. Run `pp-plan check`; if it
  reports a problem, `pp-plan repair` fixes it when you ask. The migration runs neither.

## Exit codes and going back

| code | meaning |
|---|---|
| 0 | migrated: every count equal, the old files removed, `./pp doctor` passed |
| 2 | refused, with a code. At the check or the backup, the house is untouched. At a later step, the steps after it are not played and the house may be half migrated: restore the backup |
| 3 | a count differs: nothing was removed, and the table marks the instance and the record that differ |

On a 2 after the backup, or on a 3, the output names the backup and prints the commands that put
it back in place; the migration never runs them itself. See [the index](../README.md#going-back).

Played a second time, the migration refuses at the check (`house-version`): the house is already at
0.2.39.

## Outside this migration

- The package `next`: not added (see above).
- `pp-plan repair`: not run; run it yourself if `pp-plan check` asks for it.
- The post (`ui`): it was not tested across this jump.
- Windows: this migration has been tried on Linux only.
- Your harness conversations and the agents' own records (responses, messages, sessions, flows):
  not touched, since 0.2.39 reads them as they are.
- Instances that are not in a house (standalone instances): bring them into a house first with
  `./pp agent import`.
- The packages `doc`, `federation` and `improvement`, which are not public.

## For the maintainers

The plan node of this migration is `migrations-de-maison/0-2-0-beta-33--0-2-39`. The frozen
copies of what 0.2.0-beta.33 wrote are in [`data/`](data/README.md). The scenarios in `tests/`
play the five steps on a throwaway 0.2.39 house written in the old form, and play the entry's
refusals: `./pp -test migrations`.
