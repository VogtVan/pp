#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Migrates a house from 0.2.0-beta.33 to 0.2.39 -- the house and every agent under it.

    uv run --script migrate.py <house> --from <the product at 0.2.39> [--dry-run]

The frame (`migrations/_common`) checks, backs up, holds the house, upgrades it, then plays these
gestures in their order -- plans, then their keys, then steering (it takes over the keys
rewritten), then continuity, then the teams --, counts, and removes what 0.2.39 no longer reads
once every count is equal. See README.md."""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
sys.dont_write_bytecode = True

import yaml                                                           # noqa: E402
from _common import read, run                                         # noqa: E402
from gestures import cleanup, continuity, keys, plans, steering, teams  # noqa: E402

FROM, TO = "0.2.0-beta.33", "0.2.39"

GESTURES = [("plans", plans.gesture), ("plan-keys", keys.gesture), ("steering", steering.gesture),
            ("continuity", continuity.gesture), ("teams", teams.gesture)]


NEXT = "next-unpinned"          # what `said` names: the package next is not pinned
REPAIR = "plans-repair"         # the plans keep their statuses, `pp-plan repair` stays the user's


def said(argv: list[str]) -> tuple[Path, list[str]]:
    """What stays the user's after a migration: the package next, the plans' repair. The house is
    read by the frame's own grammar (`<house> --from <source> [--dry-run]`, in any order), `next`
    in the packages `instance.yaml` pins; a dry run -- `--dry-run` or any abbreviation the parser
    takes -- says nothing. -> (the house's root, the codes said)."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("house")
    parser.add_argument("--from", dest="source")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_known_args(argv)[0]
    house = read(Path(args.house).expanduser())
    if args.dry_run:
        return house.root, []
    declared = yaml.safe_load((house.meta / ".sys" / "instance.yaml").read_text(encoding="utf-8")) or {}
    codes = []
    if "next" not in (declared.get("packages") or {}):
        codes.append(NEXT)
        print("migrate: next is not pinned, as in a new house -- `./pp add next` brings it", flush=True)
    if house.plans:
        codes.append(REPAIR)
        print("migrate: the plans keep their statuses -- `pp-plan check` judges them, `pp-plan repair` mends "
              "what it names, on your word", flush=True)
    return house.root, codes


if __name__ == "__main__":
    code = run(sys.argv[1:], FROM, TO, GESTURES, cleanup.cleanup)
    if code == 0:
        said(sys.argv[1:])
    sys.exit(code)
