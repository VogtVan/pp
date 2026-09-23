"""Scenario `messages` -- the engine's messages in flat words (plan pp-split,
batch les-messages-du-moteur):
- no metaphor of the list in any message literal of the engine (refusal details, deviation texts, console lines, generated headers, format definitions) -- docstrings and comments are not messages; `play` is pp's verb and stays
- the fixed forms the card quotes are present byte for byte
- the mass of the message literals is measured and printed, never pinned
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

from tests.harness import PRODUCT_ENGINE

METAPHORS = re.compile(r"\b(gestures?|stands?|rides?|doors?|lands?|marble|frontier|the operator's word"
                       r"|posed?|weave|citizen|vitrine|braid|sisters?|lever|grave)\b")
FIXED = ("pp: REFUSED — ", "  nothing played.", "(your proof on stdin -- heredoc",
         "<the operator's next message>", "<output>", "<your-choice>")


def literals(path: Path) -> list[tuple[int, str]]:
    """-> (line, text) of every message-like literal: a string constant that is no
    docstring, longer than 12 characters, carrying a space -- the usage of pp.py is
    a message too (the module docstring is what `SystemExit(__doc__)` prints)."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            first = node.body[0] if node.body else None
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                    and not (isinstance(node, ast.Module) and path.name == "pp.py")):
                docs.add(id(first.value))
    return [(node.lineno, node.value) for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docs and len(node.value) > 12 and " " in node.value]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    engine = PRODUCT_ENGINE.parent
    found = [(path, line, text) for path in sorted(engine.rglob("*.py"))
             for line, text in literals(path)]
    hits = [(path.relative_to(engine), line, match.group(1))
            for path, line, text in found for match in METAPHORS.finditer(text)]
    if not hits:
        held("messages in flat words", f"{len(found)} message literals, no metaphor of the list "
             f"(docstrings excluded, the usage of pp.py included)")
    else:
        failures.append(f"  ✗ metaphors                    {hits[:6]!r}")
    corpus = "\n".join(text for _, _, text in found)
    missing = [form for form in FIXED if form not in corpus]
    if not missing:
        held("the fixed forms stand byte for byte", f"{len(FIXED)} forms the card quotes, all present")
    else:
        failures.append(f"  ✗ fixed forms                  missing {missing!r}")
    print(f"  · message literals: {len(found)}, mass {sum(len(t) for _, _, t in found)} chars -- said, never pinned")
    return 0
