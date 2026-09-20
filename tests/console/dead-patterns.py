"""Scenario `dead-patterns` -- 1 case(s), in the monolith's order:
- D2d le-lint-des-motifs-morts: published gestures never rot again
"""
from __future__ import annotations

from pathlib import Path

from tests.harness import PRODUCT_ENGINE
from conductor import install as install_module

# The PUBLISHED product: the repository's own documents at the top, then these trees.
# The list ENUMERATES -- a member's instance (`.pp/`, its plans, its records, its
# vendored copies), the projected cards and whatever is born at the root tomorrow
# stay outside without any exclusion to keep up to date.
SPACES = ("adapters", "design", "engine", "kit", "packages",
          "template", "tests", "tools")
BANNED_MD = ("./pp pp-", "pp.py pp-", "NEXT_CALL", "pp.py <key>",
             "./pp -answer", "./pp -run")
BANNED_PY = ("pp.py -sync", "./pp pp-", "pp.py pp-", "NEXT_CALL")
SKIP = {".venv", "__pycache__", ".git", "state"}
ALLOW: set[tuple[str, str]] = set()   # (published path, pattern) -- history only


def _swept(root: Path, pattern: str) -> list[Path]:
    """-> the files of the published product under `root`, its own documents first."""
    found = [one for one in sorted(root.glob(pattern)) if one.is_file()]
    for space in SPACES:
        found += [one for one in sorted((root / space).rglob(pattern))
                  if not (SKIP & set(one.parts))]
    return found


def _rotten(root: Path) -> tuple[list[str], int]:
    """-> the dead gestures published under `root`, and the number of files read."""
    found, read = [], 0
    for path in _swept(root, "*.md"):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8", errors="ignore")
        found += [f"{rel}: {one}" for one in BANNED_MD
                  if one in text and (rel, one) not in ALLOW]
        read += 1
    for path in _swept(root, "*.py"):
        if "tests" in path.parts:      # the bench NAMES the retired gestures as asserts
            continue
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8", errors="ignore")
        found += [f"{rel}: {one}" for one in BANNED_PY
                  if one in text and (rel, one) not in ALLOW]
        read += 1
    return found, read


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    product_root = install_module.product_root(PRODUCT_ENGINE)
    # --- D2d le-lint-des-motifs-morts: published gestures never rot again ------------
    rotten, read = _rotten(product_root)
    if rotten:
        failures.append(f"  ✗ dead patterns               {rotten[:4]}")
    else:
        held("the dead patterns stay dead", "every published gesture and word is the "
             "current CLI -- the sweep rides the suite, an allowlist names any history")

    swept = _swept(product_root, "*.md") + _swept(product_root, "*.py")
    strayed = sorted({str(one.relative_to(product_root)).split("/")[0] for one in swept
                      if str(one.relative_to(product_root)).startswith(".")})
    if strayed:
        failures.append(f"  ✗ the perimeter is published  {strayed} -- the sweep left the product")
    else:
        held("the sweep reads the product alone", f"{read} file(s) read under the root's own "
             f"documents and {len(SPACES)} published tree(s) -- no instance, no projected card")

    made = bench.temp()                # the witnesses, inside and outside the product
    for relative, text in (("kit/refs/TEMOIN.md", "NEXT_CALL rides here\n"),
                           ("engine/temoin.py", "# ./pp pp-plan\n"),
                           (".pp/plans/x/BATCH.md", "NEXT_CALL rides here\n"),
                           (".pp/.sys/vendor/kit@0.1.0/procs/TEMOIN.md", "NEXT_CALL\n"),
                           (".claude/skills/pp/SKILL.md", "NEXT_CALL\n")):
        (made / relative).parent.mkdir(parents=True, exist_ok=True)
        (made / relative).write_text(text, encoding="utf-8")
    witnessed, _ = _rotten(made)
    owed = ["kit/refs/TEMOIN.md: NEXT_CALL", "engine/temoin.py: ./pp pp-"]
    if sorted(witnessed) != sorted(owed):
        failures.append(f"  ✗ the witnesses               {witnessed} -- owed {owed}")
    else:
        held("a published witness rots, an instance's does not", "the same dead gesture "
             "under kit/ and engine/ is named; under .pp/plans, .pp/.sys/vendor and "
             ".claude/ it is not -- the operator's matter is never judged here")
    return 0
