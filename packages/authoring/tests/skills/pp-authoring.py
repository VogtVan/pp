"""packages/authoring/skills/pp-authoring -- the DISPATCH of the engine's front matter writer:
its verbs answer, its refusals keep their names and their line, and the document it does
not own travels byte for byte. The WRITER itself is proven at `tests/engine/core/sections.py`
since batch pp-split / le-noyau-generique / le-core-importable. The `section` group leads
every verb: the package's writer answers there, its other crafts keep their own room.
What the author writes, the engine's reader reads back -- a colon inside, a comment mark, a
word YAML would type -- and the author's gesture through the console keeps the instance readable.
A piped `serve` section is cut as the reader cuts it: a blank inside a token's brackets belongs
to the token, on the piped form as on the call.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys

from conductor import reading
from conductor.core import document
from tests.harness import SOURCE, cli, load_script

RISKY = ("a: b", "x #y", "yes", "3", "- a", "@x", "café: é")

BATCH = """---
slug: un-lot-banc
kind: batch
plan: saga
phase: p1
status: doing
created: 2026-08-19
---

# BATCH `un-lot-banc`

La prose du lot, jamais touchée.
"""


@contextlib.contextmanager
def fed(text: str):
    """The piped value the dispatch reads on stdin."""
    spot, sys.stdin = sys.stdin, io.StringIO(text)
    try:
        yield
    finally:
        sys.stdin = spot


def scenario(bench) -> int:
    root = bench.env("dispatch", ("authoring",), pin=False).made
    # the VENDORED copy is the one that runs: its bootstrap walks up to `.sys/engine`
    vendored = next((root / ".sys" / "vendor").glob("authoring@*"))
    dispatch = load_script(vendored / "skills" / "pp-authoring" / "pp-authoring.py")
    doc = root / "plans" / "saga" / "1-p1" / "1-un-lot-banc" / "BATCH.md"
    doc.parent.mkdir(parents=True)
    doc.write_text(BATCH, encoding="utf-8")
    spec = "plans/saga/1-p1/1-un-lot-banc/BATCH.md"

    # the dispatch reaches the engine through the vendored bootstrap
    library = dispatch.library()
    assert hasattr(library, "edit") and hasattr(library, "constrain")
    bench.held("the dispatch reaches the engine's writer",
               "`_core.py` walks up to `.sys/engine` and hands back `conductor.sections` -- "
               "the dispatch owns no span, no code derivation, no rows grammar")

    before = doc.read_bytes()
    with fed("KZZ1  a law posed through the dispatch.\n"):
        assert dispatch.main(["section", "constrain", spec, "KZZ", "--section", "production"]) == 0
    after = doc.read_text(encoding="utf-8")
    assert "constraints.production: |" in after and "KZZ1  a law posed through the dispatch." in after
    assert "La prose du lot, jamais touchée." in after
    assert after.startswith("---\nslug: un-lot-banc\nkind: batch\n")
    bench.held("a verb writes through, the rest travels verbatim",
               "`constrain` poses its law and every untouched line is byte for byte the one "
               f"it was ({len(before)} bytes in, the front matter's head unmoved)")

    kept = doc.read_bytes()
    bench.expect_exit("document-missing",
                      lambda: dispatch.main(["section", "get", "plans/ghost.md", "slug"]))
    with fed("\n"):
        bench.expect_exit("value-malformed", lambda: dispatch.main(["section", "set", spec, "slug"]))
    assert doc.read_bytes() == kept
    bench.held("the dispatch says the refusal and writes nothing",
               "a missing document and an empty value refuse by name on stderr, exit 2 -- the "
               "library raises, the dispatch translates, and the document is untouched")

    # --- what the author writes, the reader reads back ----------------------------------
    lost = []
    for value in RISKY:
        with fed(value + "\n"):
            assert dispatch.main(["section", "set", spec, "slug"]) == 0
        lines = doc.read_text(encoding="utf-8").splitlines()
        read = document.front_matter(lines[1:lines[1:].index("---") + 1]).get("slug")
        shown = io.StringIO()
        with contextlib.redirect_stdout(shown):
            dispatch.main(["section", "get", spec, "slug"])
        if read != value or shown.getvalue().rstrip("\n") != value:
            lost.append((value, read, shown.getvalue().strip()))
    if not lost:
        bench.held("what the author writes reads back",
                   f"{len(RISKY)} risky values set through the dispatch, read back by the engine's "
                   "reader and by `section get` as given")
    else:
        bench.failures.append(f"  ✗ values read back           {lost!r}")

    # --- a piped serve section: a token with blanks is one token, as the reader reads it --
    (root / "W.md").write_text("# Title\n## Alpha\na1\n## Beta\nb1\n## Gamma\ng1\n", encoding="utf-8")
    (root / "NOTE.md").write_text("the note\n", encoding="utf-8")
    with fed("reference: W.md[## Beta..## Gamma] NOTE.md\n\nreference: W.md[..## Alpha]\n"):
        assert dispatch.main(["section", "serve", spec, "-"]) == 0
    assert dispatch.main(["section", "serve", spec, "reference:", "W.md[## Beta..## Gamma]", "NOTE.md"]) == 0
    back = reading.serve_sections(reading.read(doc))
    row = ("reference:", "W.md[## Beta..## Gamma]", "NOTE.md")
    assert back == ((row,), (("reference:", "W.md[..## Alpha]"), row)), back
    bench.held("a piped row with blanks is cut as the reader cuts it",
               "two sections piped, a tagged token with blanks kept whole and read back token for token; "
               "the same row appended by the call form reads the same")

    # --- the gesture of 2026-09-13, through the console ---------------------------------
    lived = bench.env("author", ("authoring",))
    shown = lived.cli("-new").stdout
    key = re.search(r"run ([0-9a-f]{6})", shown).group(1)
    for _ in range(6):             # the step that offers the skill: the turn, past the boot's own
        if "reading continues" not in shown and "pp-authoring" in shown.split("▌ TOOLS")[-1].split("▌")[0]:
            break
        shown = lived.cli(key).stdout
    written = cli(lived.engine, key, "-s", "pp-authoring", "section", "set", "MEMBER.md", "character",
                  cwd=lived.root, stdin="statistics-minded and helpful: a claim comes with its figure\n")
    renewed = lived.cli("-new")
    if (written.returncode == 0 and renewed.returncode == 0
            and "front-matter-invalid" not in renewed.stdout + renewed.stderr
            and "a claim comes with its figure" in lived.read("MEMBER.md")):
        held_text = "`./pp -s pp-authoring section set MEMBER.md character` with a colon inside, " \
                    "then `-new`: the member reads back, no refusal"
        bench.held("the author's gesture keeps the instance readable", held_text)
    else:
        bench.failures.append(f"  ✗ the gesture                rc={written.returncode}/{renewed.returncode} "
                              f"{(renewed.stdout + renewed.stderr)[-160:]!r}")
    return 0
