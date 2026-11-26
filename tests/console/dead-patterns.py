"""Scenario `dead-patterns` -- the published product names no retired gesture:
- the published product carries none of the dead patterns
- the sweep reads the product alone: the root's documents and the published trees
- a witness planted under a published tree is named; one under an instance or a projected card is not
- the messages live in one module: no `"pp: …"` literal in `engine/` outside `core/messages.py`, no
  refusal of the play (`execution/`, `pp.py`) that types its detail, and none of the retired names --
  the deviation module, the tables of the held and printed lines, the bounce, the armed line, the
  frame's marks read off `Block` and the title's separator off `language` -- in
  the engine, the adapters, the tools, the packages, the bases or the bench
- the readers read the module: the model, the campaign's judge and fake console, the doc bench and
  the packages' faces type none of the engine's lines again
"""
from __future__ import annotations

import re
from pathlib import Path

from tests.harness import PRODUCT_ENGINE
from conductor import install as install_module

# The PUBLISHED product: the repository's own documents at the top, then these trees.
# The list ENUMERATES -- a member's instance (`.pp/`, its plans, its records, its
# vendored copies), the projected cards and whatever is born at the root tomorrow
# stay outside without any exclusion to keep up to date.
DIRECTORIES = ("adapters", "bases", "design", "engine", "migrations", "packages",
          "template", "tests", "tools")
BANNED_MD = ("./pp pp-", "pp.py pp-", "NEXT_CALL", "pp.py <key>",
             "./pp -answer", "./pp -run", "=> chat", "=> ephemeral", "ephemerals =>", "PP_CHEATSHEET")
BANNED_PY = ("pp.py -sync", "./pp pp-", "pp.py pp-", "NEXT_CALL", "=> chat",
             "=> ephemeral", "ephemerals =>", "PP_CHEATSHEET")
SKIP = {".venv", "__pycache__", ".git", "state"}
MESSAGES = Path("engine/conductor/core/messages.py")   # the one module that writes the engine's lines
SAID = re.compile(r"""\bf?(["'])pp: """)              # a line of the console typed as a literal
PLAY = (Path("engine/conductor/execution"), Path("engine/pp.py"))   # where the refusals of the play are raised
TYPED = re.compile(r"""Refusal\(\s*["'][a-z0-9-]+["']\s*,\s*f?["']""")   # a refusal whose detail is a literal
RETIRED = re.compile(r"\bHELD_SAID\b|\bPRINT_SAID\b|\b_HELD_BOUNCE\b|\berrors\.ARMED\b|\bimport ARMED\b"
                     r"|\bARMED,|(?<![.\w])deviation\.[a-z_]+\(|\bimport deviation\b|\bcore/deviation\.py\b"
                     r"|\bBlock\.(?:MARK|SIGNAL|ANCHOR)\b|\blanguage\.(?:titled|SUBJECT)\b")
READERS = ("adapters", "tools", "packages")            # the trees whose code reads the engine's lines
RETYPED = ("pp: value judged", "printed -- other calls are due", "not played -- call already done",
           "pp: REFUSED — ", "REFUSED — ", '"value judged"', '"held open"')


def _swept(root: Path, pattern: str) -> list[Path]:
    """-> the files of the published product under `root`, its own documents first."""
    found = [one for one in sorted(root.glob(pattern)) if one.is_file()]
    for directory in DIRECTORIES:
        found += [one for one in sorted((root / directory).rglob(pattern))
                  if not (SKIP & set(one.parts))]
    return found


def _rotten(root: Path) -> tuple[list[str], int]:
    """-> the dead gestures published under `root`, and the number of files read."""
    found, read = [], 0
    for path in _swept(root, "*.md"):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8", errors="ignore")
        found += [f"{rel}: {one}" for one in BANNED_MD
                  if one in text]
        read += 1
    for path in _swept(root, "*.py"):
        if "tests" in path.parts:      # the bench NAMES the retired gestures as asserts
            continue
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8", errors="ignore")
        found += [f"{rel}: {one}" for one in BANNED_PY
                  if one in text]
        read += 1
    return found, read


def _strays(root: Path) -> list[str]:
    """-> the engine's lines written outside its module under `root`: a `pp: ` literal in `engine/`, a
    refusal of the play that types its detail, a retired name anywhere in the product's code, a reader
    that types an engine's line again."""
    found = []
    if (root / "engine" / "conductor" / "core" / "deviation.py").is_file():
        found.append("engine/conductor/core/deviation.py: stands")
    for path in sorted((root / "engine").rglob("*.py")):
        rel = path.relative_to(root)
        if SKIP & set(rel.parts) or rel == MESSAGES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        found += [f"{rel}:{n}: a `pp: ` literal" for n, line in enumerate(text.splitlines(), 1)
                  if SAID.search(line) and not line.lstrip().startswith("#")]
        if any(rel == one or one in rel.parents for one in PLAY):
            found += [f"{rel}: a refusal typing its detail" for _ in TYPED.finditer(text)][:1]
    for directory in ("engine", "adapters", "tools", "packages", "bases", "tests"):
        for path in sorted((root / directory).rglob("*.py")):
            rel = path.relative_to(root)
            if SKIP & set(rel.parts) or path.name == "dead-patterns.py":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            found += [f"{rel}: {one.group(0)}" for one in RETIRED.finditer(text)][:3]
            if rel.parts[0] in READERS and "tests" not in rel.parts:
                found += [f"{rel}: retypes {one!r}" for one in RETYPED if one in text]
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    product_root = install_module.product_root(PRODUCT_ENGINE)
    # --- D2d le-lint-des-motifs-morts: published gestures never rot again ------------
    rotten, read = _rotten(product_root)
    if rotten:
        failures.append(f"  ✗ dead patterns               {rotten[:4]}")
    else:
        held("the dead patterns stay dead", "every published gesture and word is the "
             "current CLI -- the sweep rides the suite")

    swept = _swept(product_root, "*.md") + _swept(product_root, "*.py")
    strayed = sorted({str(one.relative_to(product_root)).split("/")[0] for one in swept
                      if str(one.relative_to(product_root)).startswith(".")})
    if strayed:
        failures.append(f"  ✗ the perimeter is published  {strayed} -- the sweep left the product")
    else:
        held("the sweep reads the product alone", f"{read} file(s) read under the root's own "
             f"documents and {len(DIRECTORIES)} published tree(s) -- no instance, no projected card")

    # --- le-registre-des-messages: the engine's lines are written in one module -----------------
    strays = _strays(product_root)
    if strays:
        failures.append(f"  ✗ the messages module          {len(strays)} stray(s): {strays[:6]}")
    else:
        held("the messages live in one module", "no `pp: ` literal in engine/ outside core/messages.py, no "
             "refusal of the play typing its detail, no retired name, no reader typing an engine's line")

    made = bench.temp()                # the witnesses, inside and outside the product
    for relative, text in (("bases/kit/refs/TEMOIN.md", "NEXT_CALL rides here\n"),
                           ("engine/temoin.py", "# ./pp pp-plan\n"),
                           (".pp/plans/x/BATCH.md", "NEXT_CALL rides here\n"),
                           (".pp/.sys/vendor/kit@0.1.0/procs/TEMOIN.md", "NEXT_CALL\n"),
                           (".claude/skills/pp/SKILL.md", "NEXT_CALL\n")):
        (made / relative).parent.mkdir(parents=True, exist_ok=True)
        (made / relative).write_text(text, encoding="utf-8")
    witnessed, _ = _rotten(made)
    owed = ["bases/kit/refs/TEMOIN.md: NEXT_CALL", "engine/temoin.py: ./pp pp-"]
    if sorted(witnessed) != sorted(owed):
        failures.append(f"  ✗ the witnesses               {witnessed} -- owed {owed}")
    else:
        held("a published witness rots, an instance's does not", "the same dead gesture "
             "under bases/kit/ and engine/ is named; under .pp/plans, .pp/.sys/vendor and "
             ".claude/ it is not -- the operator's matter is never judged here")
    return 0
