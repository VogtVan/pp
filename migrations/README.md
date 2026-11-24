# Migrations — bringing a house across versions

`./pp upgrade` brings a house's code to a new version. Sometimes a new version also reads its
data in a new form: records, plans or files written by an older version. A **migration** moves
that data. It plays the upgrade itself, then rewrites the data in place, then checks that
nothing was lost.

You need a migration only to leave a version listed in the table below. A house at any other
version is updated with `./pp upgrade` alone.

## The migrations

| from | to | packages covered | folder |
|---|---|---|---|
| 0.2.0-beta.33 | 0.2.39 | continuity, steering, plan, team (agent read as it is) | [`0.2.0-beta.33--0.2.39/`](0.2.0-beta.33--0.2.39/README.md) |

Each migration covers one jump, from one exact version to another, and only for the houses
installed from this repository. Agents under the house are migrated with it. An instance that
runs on its own machine is not migrated: bring it into a house first with
`./pp agent import`.

## Before you start

- **The source.** A migration needs a copy of the product at exactly its arrival version, `to`
  in the table, that also carries the migration itself. On GitHub, each migration has its own tag,
  `migration-<from>--<to>`, which marks such a copy; the migration's page gives the clone command.
  Do not use the version tag (`0.2.39`): it can be older than the migration and lack the
  `migrations/` folder. A copy at any other version is refused (`source-version`).
- **No pp running.** Close the post and every chat, and stop every team of the house. If a pp
  process is still running in the house, the migration is refused (`house-busy`). Once the check
  has passed, the house stays locked until the migration ends: any pp you start in it meanwhile
  is refused (`maintenance-in-progress`) and does nothing.
- **Room beside the house.** The backup is written in the folder that holds the house, so that
  folder must be writable and have room for a copy of the house.
- **uv.** The migration runs under `uv`, as pp does. It needs no network and no git.
- **Not on Windows.** Migrations have not been tried on Windows, and the restore commands below
  are for a Linux or macOS shell.

## Running it

From the product copy at the arrival version, play the check alone first:

```sh
uv run --script migrations/<from>--<to>/migrate.py <house> --from <source> --dry-run
```

`<house>` is the folder that holds the house's `.pp/`; `<source>` is the product copy at the
arrival version. `--dry-run` runs the check, then lists the migration's own steps (its
gestures, step 4 below) and the names the backup and the journal would take. It writes nothing
at all, not even the journal, and it does not lock the house.

Then the migration itself, the same line without `--dry-run`:

```sh
uv run --script migrations/<from>--<to>/migrate.py <house> --from <source>
```

The steps, always in this order:

| # | step | what it does |
|---|---|---|
| 1 | check | the house is at the starting version, the source at the arrival version, the backup has room, and no pp is running; then, last, the house is locked until the migration ends. A refusal stops here and nothing is written |
| 2 | backup | the whole house except its own `.git` folder, in one archive beside the house |
| 3 | upgrade | `./pp upgrade --from <source>`: the house's code moves to the arrival version |
| 4 | gestures | the migration's own steps, called gestures, rewrite the data one after the other |
| 5 | counts | every record moved is counted, per instance, before and after; the table is printed |
| 6 | cleanup | when every count is equal, the files the arrival version no longer reads are removed (they stay in the backup) |
| 7 | doctor | `./pp doctor` checks the house and repairs what it can |

The lock is released at the end, whether the migration succeeds or is refused.

Played twice, a migration refuses at the check: the house is no longer at the starting version.

## What it writes beside the house

| file | what it holds |
|---|---|
| `<house>.pre-<to>-<date>.tar.gz` | the backup: the whole house except its own `.git` folder; a `.git` deeper in the house (an agent's) is kept |
| `<house>.pre-<to>-<date>.log` | the journal: one JSON object per line -- the check, the backup, each step with its output, the counts |

`<house>` is the name of the house's folder, `<date>` the moment the migration started
(`20261123-194500`). Both files sit in the folder that holds the house, never inside it.
Nothing is written in the house before the check has passed and the backup is complete, with
one exception: in a house where no pp has ever run, locking it creates its empty lock file,
`.pp/.sys/state/maintenance.lock`.

## Exit codes

| code | meaning | the house |
|---|---|---|
| 0 | migrated | at the arrival version, every count equal, the cleanup done, `./pp doctor` passed |
| 2 | refused | at the check or the backup: untouched. At a later step: the steps after it are not played, and the house may be half migrated -- restore the backup |
| 3 | a count differs | upgraded and rewritten, nothing removed; the table marks each differing row `DIFFERS`, with its instance and its record |

A refusal is printed as `migrate: refused <code> -- <detail>`. The codes:

| code | when |
|---|---|
| `house-missing` | the folder holds no house (`.pp/` with its engine) |
| `house-version` | the house is not at the starting version -- for example, it is already migrated |
| `source-missing`, `source-version` | the source is not a copy of the product, or not at the arrival version |
| `space` | the folder that holds the house is read-only or has no room for the backup |
| `house-busy` | a pp process is running in the house |
| `upgrade` | `./pp upgrade` failed (its last line is said), or left the house at another version than the arrival one |
| `doctor` | `./pp doctor` failed; its last line is said |
| a gesture's own code | a gesture refused; the next gestures are not played |
| `cleanup-outside` | the cleanup named a path it may not remove -- outside the house, the house itself, or inside a `.git`; nothing is removed |
| `<step>-failed` | an unexpected error at that step (`check-failed`, `backup-failed`, `gesture-failed`...); the error is printed |

Any error is a refusal with a code: the migration never stops without one.

## Going back

On any refusal after the backup, or on a code 3, the migration prints where the backup is and the
commands that restore it. It never restores on its own. The commands move the migrated house
aside, extract the backup in its place (with every `.git` deeper in the house) and put the
house's own `.git` back:

```sh
mv <house> <house>.migrated && tar -xzf <backup> -C <folder holding the house> \
  && (test ! -d <house>.migrated/.git || mv <house>.migrated/.git <house>/)
```

Once you have checked the restored house, delete `<house>.migrated`.

## Going further than one jump

A published migration never changes, and it accepts only the source at its own arrival version.
To cross several jumps, play the migrations one after the other, in the order of the table, each
with the source of its own `migration-<from>--<to>` tag. Then bring the house to the latest version with
`./pp upgrade --from <latest source>`.

## Writing a migration

A migration lives in `migrations/<from>--<to>/`, the versions written with their dots
(`0.2.0-beta.33--0.2.39`):

| piece | what it is |
|---|---|
| `migrate.py` | the entry: it declares `FROM`, `TO`, its gestures and its cleanup, and hands them to `_common.run` |
| its gestures | the functions that rewrite the data: `gesture(house, engine)` returns the count rows `(instance, record, before, after)`, or raises `Refused(code, detail)`; any other error refuses `gesture-failed` |
| `data/` | the frozen copies of what the starting version wrote (old templates, old forms) |
| `README.md` | what the jump changes, its gestures, what its cleanup removes |
| `tests/` | its scenarios, played by `./pp -test migrations` on throwaway houses |

A migration imports only `migrations/_common/` and the engine of the house it migrates
(`engine.store.of(meta)` for an instance's records). It never backs up, upgrades or removes
anything itself: `_common.run` orders every step. It names no particular house, member, path
or record: it speaks of any house that stands at its starting version.

```python
#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _common import Refused, run

FROM, TO = "<from>", "<to>"


def gesture(house, engine):
    rows = []
    for meta in house.instances:
        ...          # rewrite the data, count each record before and after
    return rows


GESTURES = [("<name>", gesture)]


def cleanup(house):
    return []        # the paths under the house the arrival version no longer reads


sys.exit(run(sys.argv[1:], FROM, TO, GESTURES, cleanup))
```
