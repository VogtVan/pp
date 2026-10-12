"""Scenario `strip-eos` -- 2 case(s) (plan pp-split, phase le-noyau-generique, batch
la-fin-du-marqueur):
- the tool removes the closing marker: dry-run writes nothing and names the document,
  `--apply` strips the last `[EOS]` with the blank lines before it, a marker standing
  elsewhere is said and left, a document without the marker says nothing to do
- replayed, the pass changes nothing; `.sys` is never entered; a file named as it is
  goes through
"""
from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path

from tests.harness import SOURCE, load_script


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    tool = load_script(SOURCE / "tools" / "strip-eos.py")
    home = Path(tempfile.mkdtemp(prefix="pp-strip-"))
    (home / "procs").mkdir()
    (home / ".sys").mkdir()
    closed = home / "procs" / "CLOSED.md"
    closed.write_text("---\nname: CLOSED\n---\n\nthe body\n\n\n[EOS]\n", encoding="utf-8")
    elsewhere = home / "ELSEWHERE.md"
    elsewhere.write_text("[EOS]\nthe marker opens, nothing closes on it\n", encoding="utf-8")
    bare = home / "BARE.md"
    bare.write_text("---\nname: BARE\n---\n\nalready nude\n", encoding="utf-8")
    vendored = home / ".sys" / "VENDORED.md"
    vendored.write_text("vendored\n\n[EOS]\n", encoding="utf-8")
    aside = home.parent / (home.name + "-aside.md")
    aside.write_text("a file named as it is\n\n[EOS]\n", encoding="utf-8")

    told = io.StringIO()
    with contextlib.redirect_stdout(told):
        dry_rc = tool.main([str(home), str(aside)])
    untouched = (closed.read_text(encoding="utf-8").endswith("[EOS]\n")
                 and aside.read_text(encoding="utf-8").endswith("[EOS]\n"))
    told_apply = io.StringIO()
    with contextlib.redirect_stdout(told_apply):
        apply_rc = tool.main([str(home), str(aside), "--apply"])
    if (dry_rc == 0 and untouched and "(dry run)" in told.getvalue()
            and "CLOSED.md" in told.getvalue() and "2 stripped, 1 said, 1 nothing to do" in told.getvalue()
            and apply_rc == 0
            and closed.read_text(encoding="utf-8") == "---\nname: CLOSED\n---\n\nthe body\n"
            and aside.read_text(encoding="utf-8") == "a file named as it is\n"
            and elsewhere.read_text(encoding="utf-8").startswith("[EOS]\n")
            and "ELSEWHERE.md" in told_apply.getvalue() and "elsewhere" in told_apply.getvalue()
            and bare.read_text(encoding="utf-8").endswith("already nude\n")):
        held("the tool strips the closing marker", "dry-run writes nothing and names the "
             "document; --apply removes the last [EOS] and the blanks before it, says a "
             "misplaced one, leaves a nude document alone")
    else:
        failures.append(f"  ✗ strip apply                rc={dry_rc}/{apply_rc} {told.getvalue()!r} "
                        f"{closed.read_text(encoding='utf-8')!r}")

    told_again = io.StringIO()
    with contextlib.redirect_stdout(told_again):
        again_rc = tool.main([str(home), str(aside), "--apply"])
    if (again_rc == 0 and "0 stripped, 1 said, 3 nothing to do" in told_again.getvalue()
            and vendored.read_text(encoding="utf-8").endswith("[EOS]\n")
            and closed.read_text(encoding="utf-8") == "---\nname: CLOSED\n---\n\nthe body\n"):
        held("the pass is idempotent and never enters .sys",
             "replayed: nothing stripped; the vendored copy keeps its marker untouched")
    else:
        failures.append(f"  ✗ strip replay               rc={again_rc} {told_again.getvalue()!r}")
    return 0
