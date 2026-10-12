"""Scenario `migrate-sections` -- 2 case(s):
- the tool migrates a bare `constraints:` to its two sections from the pilot: dry-run
  writes nothing and reports, `--apply` writes both keys, a code without a line goes to
  behavior and is named
- replayed, the tool changes nothing; a comment rides the law after it, a removal rides
  the first section, a document without the bare key says nothing to do
"""
from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path

from tests.harness import SOURCE, load_script


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    tool = load_script(SOURCE / "tools" / "migrate-sections.py")
    home = Path(tempfile.mkdtemp(prefix="pp-migrate-"))
    pilot = home / "regimes.csv"
    pilot.write_text("code,famille,section\nP1,production,production\nH1,comportement,behavior\n",
                     encoding="utf-8")
    doc = home / "LAWS.md"
    text = ("---\nname: LAWS\nconstraints: |\n  # the header comment\n  H1  a way of doing\n"
            "  P1  a fact rendered\n  -T4\n  Z1  a stranger\nproc: |\n  WORK\n---\nx\n")
    doc.write_text(text, encoding="utf-8")
    clean = home / "DONE.md"
    clean.write_text("---\nname: DONE\nconstraints.behavior: |\n  H9  done\n---\ny\n",
                     encoding="utf-8")

    # --- dry-run reports, apply writes ---------------------------------------------------
    told = io.StringIO()
    with contextlib.redirect_stdout(told):
        dry_rc = tool.main([str(home), "--csv", str(pilot)])
    untouched = doc.read_text(encoding="utf-8") == text
    told_apply = io.StringIO()
    with contextlib.redirect_stdout(told_apply):
        apply_rc = tool.main([str(home), "--csv", str(pilot), "--apply"])
    after = doc.read_text(encoding="utf-8")
    if (dry_rc == 0 and untouched and "would migrate" in told.getvalue()
            and "NO LINE for Z1" in told.getvalue() and apply_rc == 0
            and "constraints.production: |\n  P1  a fact rendered\n  -T4\n" in after
            and "constraints.behavior: |\n  # the header comment\n  H1  a way of doing\n  Z1  a stranger\n"
            in after and "constraints: |" not in after and after.endswith("\n")):
        held("the tool migrates from the pilot", "dry-run writes nothing and names Z1; --apply "
             "writes production then behavior, the comment with its law, -T4 in the first section")
    else:
        failures.append(f"  ✗ migrate apply              rc={dry_rc}/{apply_rc} {told.getvalue()!r} "
                        f"{after!r}")

    # --- replayed, nothing moves ----------------------------------------------------------------
    told_again = io.StringIO()
    with contextlib.redirect_stdout(told_again):
        again_rc = tool.main([str(home), "--csv", str(pilot), "--apply"])
    if (again_rc == 0 and doc.read_text(encoding="utf-8") == after
            and "0 carrying a bare" in told_again.getvalue()
            and clean.read_text(encoding="utf-8").startswith("---\nname: DONE\nconstraints.behavior")):
        held("replayed, the tool changes nothing", "idempotent; the migrated and the clean say "
             "nothing to do")
    else:
        failures.append(f"  ✗ migrate replay             {told_again.getvalue()!r}")
    return 0
