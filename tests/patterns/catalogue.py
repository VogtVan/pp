"""Scenario `catalogue` -- the catalogue of the engine's patterns, `engine/patterns/README.md`:
- every pattern directory `engine/patterns/<drawer>/<pattern>/` opens exactly one line of the
  catalogue, its link resolving to that pattern's README; no line names a pattern that is not on
  disk
- every key of the catalogue's tables opens one row, once, and points to a pattern that exists or
  to the engine's reference
- every SETTINGS key the engine seeds has its row
The scenario compares paths and key names, read from the tree and from the settings module.
"""
from __future__ import annotations

import re

from conductor.state import settings
from tests.harness import PATTERNS, SOURCE

ENTRY = re.compile(r"^\|\s*\[[^\]]+\]\(([a-z-]+/[a-z-]+)/README\.md\)\s*\|")   # a pattern's line
KEYROW = re.compile(r"^\|\s*`([^`]+)`\s*\|.*\|\s*(?:\[[^\]]+\]\(([^)]+)\)|`(docs/reference/[a-z-]+\.md)`)\s*\|\s*$")
REFERENCE = "docs/reference/"   # a key the engine's reference documents, no pattern teaches it


def _key(raw: str) -> str:
    """-> the key a row names, its trailing `:` dropped."""
    return raw.strip().rstrip(":")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    catalogue = PATTERNS / "README.md"
    if not catalogue.is_file():
        failures.append(f"  ✗ the catalogue               {catalogue} is absent")
        return 0
    lines = catalogue.read_text(encoding="utf-8").splitlines()

    on_disk = sorted(f"{drawer.name}/{pattern.name}" for drawer in PATTERNS.iterdir() if drawer.is_dir()
                     for pattern in drawer.iterdir() if pattern.is_dir() and not pattern.name.startswith("_"))
    listed = [match.group(1) for line in lines if (match := ENTRY.match(line))]
    missing = sorted(set(on_disk) - set(listed))
    extra = sorted(set(listed) - set(on_disk))
    twice = sorted({one for one in listed if listed.count(one) > 1})
    unresolved = [one for one in listed if not (PATTERNS / one / "README.md").is_file()]
    if on_disk and not (missing or extra or twice or unresolved):
        held("every pattern has its line", f"{len(on_disk)} pattern directories, {len(listed)} lines, "
             "each once, each README resolved")
    else:
        failures.append(f"  ✗ the patterns                missing={missing} extra={extra} twice={twice} "
                        f"unresolved={unresolved}")

    rows = [(_key(match.group(1)), match.group(2) or match.group(3))
            for line in lines if (match := KEYROW.match(line))]
    keys = [key for key, _ in rows]
    repeated = sorted({key for key in keys if keys.count(key) > 1})
    lost = [(key, target) for key, target in rows
            if not (SOURCE / target if target.startswith(REFERENCE) else PATTERNS / target).is_file()]
    if rows and not repeated and not lost:
        held("every key points somewhere", f"{len(rows)} key rows, each once, each to a pattern README "
             "or to the reference")
    else:
        failures.append(f"  ✗ the keys                    repeated={repeated} lost={lost}")

    seeded = [key for key, _ in settings.SEEDS]
    unseated = [key for key in seeded if key not in keys]
    if not unseated:
        held("every seeded setting has its row", f"{len(seeded)} keys of settings.SEEDS in the table")
    else:
        failures.append(f"  ✗ the settings                without a row: {unseated}")
    return 0
