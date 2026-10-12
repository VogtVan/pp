"""packages/steering/skills/pp-steering -- the front of the moment (batch steering / le-skill /
les-fils-du-moment), every verb played by the vendored script in a subprocess (KS12):
- a thread's NOTE: `open --note`, `note`, the budget, no date moved, the column and the ledger
- `attach` says the thread's id with the step's
- the actions: up to `steering_next_max` from the pointed step on, then `…`
- a thread with nothing to do has no row; its waiting steps stand at the ⏸ line, `+n` past the cap
- the table keeps `steering_front_min` rows before anything folds: never empty
- `status --all --open`: the ledger of the steps still to do, what the boot serves
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone


def scenario(bench) -> int:
    root = bench.env("moment", ("steering",), pin=False).made
    script = next((root / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"
    spool = root / ".sys" / "records" / "threads.json"
    settings = root / "SETTINGS.md"

    def play(*args: str, stdin: str = "") -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(script), *args], input=stdin, capture_output=True,
                              text=True, cwd=str(root.parent))

    def record() -> dict:
        return json.loads(spool.read_text(encoding="utf-8"))

    def tid_of(name: str) -> str:
        return next(tid for tid, one in record()["threads"].items() if one["name"] == name)

    def rows_of(front: str) -> list[str]:
        return [line for line in front.splitlines() if line.startswith("| ") and not line.startswith("| initiative |")]

    def set_to(key: str, value: int) -> None:
        settings.write_text(re.sub(rf"^{key}:.*$", f"{key}: {value}", settings.read_text(encoding="utf-8"), flags=re.M),
                            encoding="utf-8")

    # --- the note -----------------------------------------------------------------------------
    born = play("open", "le-banc", "--note", "rouges excusés à chaque suite", stdin="les-motifs-morts\nla-cle-en-chiffres\n"
                                                                                   "la-cle-du-run-ferme\nle-marbre-qui-fuit\n")
    assert born.returncode == 0 and "opened -- le-banc [" in born.stdout, born.stderr
    banc = tid_of("le-banc")
    assert record()["threads"][banc]["note"] == "rouges excusés à chaque suite"
    dated = record()["threads"][banc]["worked_at"]
    assert play("note", banc, "motifs", "morts", "levés ;", "3", "rouges", "restent").returncode == 0
    assert record()["threads"][banc]["note"] == "motifs morts levés ; 3 rouges restent"
    assert record()["threads"][banc]["worked_at"] == dated                         # a note is no work
    over = play("note", banc, "x" * 81)
    assert over.returncode == 2 and "budget" in over.stderr and record()["threads"][banc]["note"].startswith("motifs")
    assert play("note", banc, "x" * 80).returncode == 0
    assert play("note", banc, "a | pipe").returncode == 0
    front = play("status").stdout
    assert "| initiative | note | progress | age | next action(s) |" in front, front
    assert "| le-banc | a \\| pipe | ▱▱▱▱▱ 0/4 | now |" in front, front                # a pipe stays in its cell
    ledger = play("status", "--all").stdout
    assert f"~ le-banc [{banc}] (" in ledger and ") — a | pipe" in ledger, ledger
    bench.held("a thread wears a note", "`open --note` gives it, `note` rewrites it without moving the date, 81 "
               "characters refuse `budget`; the front shows it in its column (a pipe escaped), the ledger after `—`")

    # --- attach says the thread's id ------------------------------------------------------------
    added = play("attach", banc, "--as", "la-trace-intermittente")
    assert added.returncode == 0 and f"attached -- le-banc [{banc}] " in added.stdout, added.stdout
    bench.held("attach says the thread's id", "`attached -- <name> [<thread id>] <step id>`: a step minted "
               "after the boot gives its thread's id to the context")

    # --- the actions: three, then … ; the cap is a setting ------------------------------------
    front = play("status").stdout
    [row] = [one for one in rows_of(front) if one.startswith("| le-banc |")]
    assert row.endswith("| `les-motifs-morts` · `la-cle-en-chiffres` · `la-cle-du-run-ferme` … |"), row
    set_to("steering_next_max", 1)
    [row] = [one for one in rows_of(play("status").stdout) if one.startswith("| le-banc |")]
    assert row.endswith("| `les-motifs-morts` … |"), row
    set_to("steering_next_max", 3)
    bench.held("the next actions", "from the pointed step on, in the thread's order, three at most then `…`; "
               "`steering_next_max: 1` names one")

    # --- a thread with nothing to do has no row; the ⏸ line and its cap -------------------------
    parked = play("open", "le-temoin", "--note", "federation off ici", stdin="".join(f"le-defaut-{n}\n" for n in range(1, 10)))
    assert parked.returncode == 0
    temoin = tid_of("le-temoin")
    for sid in record()["threads"][temoin]["steps"]:
        assert play("block", temoin, sid, "federation off ici").returncode == 0
    front = play("status").stdout
    assert not any(one.startswith("| le-temoin |") for one in rows_of(front)), front
    [waiting] = [line for line in front.splitlines() if line.startswith("⏸ ")]
    assert waiting.startswith("⏸ le-temoin › `le-defaut-1` (federation off ici) · ") and waiting.endswith(" · +2"), waiting
    assert waiting.count(" › ") == 7
    assert play("renext", temoin, record()["threads"][temoin]["steps"][0]).returncode == 0
    front = play("status").stdout
    assert any(one.startswith("| le-temoin | federation off ici |") for one in rows_of(front)) and " · +1" in front
    bench.held("no row without an action, the ⏸ line", "a thread whose steps all wait has no row; every waiting "
               "step of the open threads stands at the ⏸ line as `thread › step (reason)`, seven named then `+n`; "
               "released, a step brings its thread back to the table")

    # --- the table keeps five rows before anything folds --------------------------------------
    for n in range(1, 7):
        assert play("open", f"le-fil-{n}", stdin=f"le-pas-{n}\n").returncode == 0
    later = datetime.now(timezone.utc) + timedelta(days=9)
    live = sum(1 for one in record()["threads"].values()
               if any(record()["steps"][sid]["status"] in ("open", "redo") for sid in one["steps"]))
    assert live == 8
    script_module = __import__("importlib").util.spec_from_file_location("front_keeper", script)
    keeper = __import__("importlib").util.module_from_spec(script_module)
    script_module.loader.exec_module(keeper)
    every = keeper.front(root, keeper.load(root), now=later)
    assert len(rows_of(every)) == 5 and every.split("\n")[-1].startswith("💤 ") and every.split("\n")[-1].count(" · ") == 2, every
    awake = keeper.front(root, keeper.load(root))
    assert len(rows_of(awake)) == 8 and "💤" not in awake
    for n in range(1, 7):
        assert play("close", tid_of(f"le-fil-{n}")).returncode == 0
    few = keeper.front(root, keeper.load(root), now=later)
    assert len(rows_of(few)) == 2 and "💤" not in few, few
    bench.held("the table is never empty", "eight threads all dormant: five rows at the table, the three oldest "
               "in the footer; awake, eight rows and no footer; two dormant threads: two rows, no footer")

    # --- the ledger of the steps still to do: what the boot serves ------------------------------
    assert play("done", banc, record()["threads"][banc]["steps"][0]).returncode == 0
    opened = play("status", "--all", "--open").stdout
    whole = play("status", "--all").stdout
    assert "les-motifs-morts" in whole and "les-motifs-morts" not in opened, opened
    assert f"~ le-banc [{banc}]" in opened and "la-cle-en-chiffres" in opened
    assert "le-defaut-2 — federation off ici" in opened and len(opened) < len(whole)
    assert play("status", "--open").returncode == 2                             # --open reads the ledger alone
    bench.held("the open ledger", "`status --all --open` keeps each open thread with its id and note and its steps "
               "still to do -- a waiting one with its reason -- and leaves the delivered out; `--open` alone refuses")
    return 0
