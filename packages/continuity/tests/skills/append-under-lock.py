"""Scenario `append-under-lock` -- the record of operations has one writer, the store:
- a write transaction held open on the records' base by another process: `register` waits for
  it and writes once it ends -- nothing lands while it is held
- eight registers at once: eight entries, each one whole
- a period past the bound: `recall last <n>` prints its latest operations up to the bound, oldest
  first, then says how many older ones it left and the call that reads them (`--skip`); the pages
  together give every operation once; a `--skip` past the total says none is left past it, rc 0
"""
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

from conductor import store
from tests.harness import race


def _script(env):
    return next((env.made / ".sys" / "vendor").glob("continuity@*/skills/pp-continuity/pp-continuity.py"))


def _entries(made) -> list[str]:
    """-> the text of every operation the record holds (a page of the store, under its bound)."""
    return [one.body.get("entry") for one in store.of(made).read("operations").rows]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("appends", ("continuity",))
    script = _script(env)

    # --- a write transaction held by another process: the append waits ---------------------------
    with store.of(env.made).transaction() as session:
        session.append("operations", {"entry": "written by the holder"})
        proc = subprocess.Popen([sys.executable, str(script), "register", "written after the holder"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            proc.wait(timeout=1.5)
            early = True
        except subprocess.TimeoutExpired:
            early = False
    out, err = proc.communicate(timeout=20)
    landed = _entries(env.made)
    if early:
        failures.append(f"  ✗ transaction held           register wrote while a write transaction was open (rc {proc.returncode})")
    elif proc.returncode or landed != ["written by the holder", "written after the holder"]:
        failures.append(f"  ✗ transaction ended          register after the holder: rc {proc.returncode} "
                        f"landed {landed} -- {err.strip()[:120]}")
    else:
        held("an append waits for the open write, writes once it ends", "held 1.5s · then rc 0, after the holder's entry")

    # --- eight at once, each entry whole ---------------------------------------------------------
    texts = [f"line {index} " + "x" * 400 for index in range(8)]
    results = race(script, [["register", text] for text in texts], cwd=env.root)
    entries = _entries(env.made)
    whole = [text for text in texts if entries.count(text) == 1]
    if any(one.returncode for one in results):
        failures.append("  ✗ eight at once              a register failed: " + " | ".join(one.stderr.strip()[:80] for one in results if one.returncode))
    elif len(whole) != 8 or len(entries) != 10:
        failures.append(f"  ✗ eight at once              eight registers: {len(whole)} whole entries of {len(entries)}")
    else:
        held("eight appends at once: eight entries, each whole", f"{len(entries)} entries in the store")

    # --- a period past the bound: the latest operations, the rest said with the call that reads it ----
    paged = bench.env("pages", ("continuity",))
    paged_script = _script(paged)
    start = datetime.now(timezone.utc) - timedelta(hours=1)
    store.of(paged.made).extend("operations", ({"at": start + timedelta(seconds=n), "body": {"entry": f"op {n:03d}"}}
                                               for n in range(100)))
    pages, call, seen = [], ["recall", "last", "7"], []
    while call and len(pages) < 10:
        out = subprocess.run([sys.executable, str(paged_script), *call], capture_output=True, text=True)
        pages.append(out)
        seen = re.findall(r"op (\d{3})", out.stdout) + seen
        told = re.search(r"`recall last 7 --skip (\d+)`", out.stdout)
        call = ["recall", "last", "7", "--skip", told.group(1)] if told else None
    first = re.findall(r"op (\d{3})", pages[0].stdout)
    past = subprocess.run([sys.executable, str(paged_script), "recall", "last", "7", "--skip", "120"],
                          capture_output=True, text=True)
    if (all(one.returncode == 0 for one in pages) and len(pages) > 1 and first
            and first == sorted(first) and first[-1] == "099" and len(first) < 100
            and f"{100 - len(first)} older operation(s)" in pages[0].stdout
            and seen == [f"{n:03d}" for n in range(100)]
            and past.returncode == 0 and "none past the 120 latest" in past.stdout
            and not re.search(r"op \d{3}", past.stdout)):
        held("a period past the bound is read in pages", f"100 operations: the first page the {len(first)} latest, "
             f"oldest first, the {100 - len(first)} older said with their `--skip` call; {len(pages)} pages, "
             "every operation once, in order; `--skip 120` says none past the 120 latest, rc 0")
    else:
        failures.append(f"  ✗ recall past the bound      {len(pages)} page(s), the first {len(first)} operation(s), "
                        f"rc {[one.returncode for one in pages]} -- {pages[0].stdout[-160:]!r} {pages[-1].stderr[-120:]!r} "
                        f"past: rc {past.returncode} {past.stdout[-120:]!r}")
    return 0
