"""Scenario `append-under-lock` -- 3 case(s) (batch les-ecrivains-partages, 2026-09-30):
- the record's lock held by another process: `register` waits for it and writes once it
  is released -- nothing lands while the lock is held
- eight registers at once: eight lines, each one whole
- a last line still being written is skipped by `recall`; a torn line anywhere else still
  refuses -- this script is the only writer, the file is not for hand edits
"""
from __future__ import annotations

import json
import subprocess
import sys

from tests.harness import holding, race


def _entries(path) -> list[dict]:
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            found.append(json.loads(line))
        except ValueError:
            found.append({"torn": line})
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("appends", ("continuity",))
    script = next((env.made / ".sys" / "vendor").glob("continuity@*/skills/pp-continuity/pp-continuity.py"))
    record = env.made / ".sys" / "records" / "operations.jsonl"

    # --- the lock held by another process: the append waits ------------------------------------
    with holding(record.with_name(record.name + ".lock")):
        proc = subprocess.Popen([sys.executable, str(script), "register", "written under the lock"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            proc.wait(timeout=1.5)
            early = True
        except subprocess.TimeoutExpired:
            early = False
    out, err = proc.communicate(timeout=20)
    landed = [one for one in _entries(record) if one.get("entry") == "written under the lock"]
    if early:
        failures.append(f"register wrote while the record's lock was held (rc {proc.returncode})")
    elif proc.returncode or len(landed) != 1:
        failures.append(f"register after the release: rc {proc.returncode} landed {len(landed)} -- {err.strip()[:120]}")
    else:
        held("an append waits for the record's lock, writes once released", "held 1.5s · then rc 0, one line")

    # --- eight at once, each line whole ------------------------------------------------------------
    texts = [f"line {index} " + "x" * 400 for index in range(8)]
    results = race(script, [["register", text] for text in texts], cwd=env.root)
    entries = _entries(record)
    whole = [text for text in texts if any(one.get("entry") == text for one in entries)]
    torn = [one for one in entries if "torn" in one]
    if any(one.returncode for one in results):
        failures.append("a register among eight failed: " + " | ".join(one.stderr.strip()[:80] for one in results if one.returncode))
    elif len(whole) != 8 or torn:
        failures.append(f"eight registers at once: {len(whole)} whole lines, {len(torn)} torn")
    else:
        held("eight appends at once: eight lines, each whole", f"{len(entries)} entries, 0 torn")

    # --- a last line still being written is skipped; a torn line elsewhere refuses -----------------
    with record.open("a", encoding="utf-8") as handle:
        handle.write('{"at": "2026-09-30T13:00')            # a writer mid-line: no newline yet
    recalled = subprocess.run([sys.executable, str(script), "recall", "last", "7"],
                              capture_output=True, text=True)
    text = record.read_text(encoding="utf-8")
    torn_line, good = text.rsplit("\n", 1)[1], text.rsplit("\n", 1)[0]
    record.write_text(torn_line + "\n" + good + "\n", encoding="utf-8")   # the torn line moved to the head
    refused = subprocess.run([sys.executable, str(script), "recall", "last", "7"],
                             capture_output=True, text=True)
    if recalled.returncode or "written under the lock" not in recalled.stdout:
        failures.append(f"recall over a torn last line: rc {recalled.returncode} -- {recalled.stderr.strip()[:120]}")
    elif refused.returncode != 2 or "is not a record" not in refused.stderr:
        failures.append(f"recall over a torn line elsewhere: rc {refused.returncode} -- {refused.stderr.strip()[:120]}")
    else:
        held("a last line being written is skipped, a torn line elsewhere refuses", "rc 0 · then rc 2")
    return len(failures)
