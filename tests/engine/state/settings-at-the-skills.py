"""Scenario `settings-at-the-skills` -- a setting is read through the face, never by hand
(plan pp-split, batch les-cles-au-reglage):
- no skill of the product opens `SETTINGS.md` itself: the regex reader is gone everywhere
- a key a fragment PRESETS by effort is the one a hand reader would get wrong -- the guard
  derives those keys from the fragments, so a preset added tomorrow is covered by itself
"""
from __future__ import annotations

import re

from tests.harness import SOURCE

DOCUMENT = re.compile(r"SETTINGS\.md")


def skills() -> list:
    """-> every skill script of the product: `packages/<p>/skills/<name>/<name>.py`."""
    return sorted(one for one in SOURCE.glob("packages/*/skills/*/*.py")
                  if one.stem == one.parent.name)


def preset_keys() -> set:
    """-> the keys a fragment presets by effort, read from the fragments themselves: the
    day one is added, this guard covers it without a line changing here."""
    found = set()
    for fragment in sorted(SOURCE.glob("packages/*/settings/SETTINGS.md")):
        head = fragment.read_text(encoding="utf-8").split("---")[1]
        block = re.search(r"^effort: \|\n((?:  .*\n)+)", head, re.M)
        if block:
            found |= {line.split()[0] for line in block.group(1).splitlines() if line.strip()}
    return found


def code_of(path) -> str:
    """-> the file without its comment tails: a mention in prose is not a reader."""
    return "\n".join(line.split("#", 1)[0] for line in path.read_text(encoding="utf-8").splitlines())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- no skill opens the settings document by itself
    openers = [one.stem for one in skills()
               if DOCUMENT.search(code_of(one)) and "of_package" not in code_of(one)]
    if not openers:
        held("no skill reads the settings by hand",
             f"{len(skills())} skills, none opens SETTINGS.md on its own")
    else:
        failures.append(f"  ✗ hand readers               {openers}")

    # --- a key preset by an effort is read through the face, or not at all
    presets = preset_keys()
    astray = [(one.stem, key) for one in skills() for key in presets
              if key in code_of(one) and "of_package" not in code_of(one)]
    if presets and not astray:
        held("a preset key goes through the face",
             f"{len(presets)} keys preset by an effort ({', '.join(sorted(presets))}), none read by hand")
    else:
        failures.append(f"  ✗ preset read by hand        {astray or 'no preset declared at all'}")
    return 0
