"""Scenario `ui-purge` -- the weight of the runs and their purge, shown first then played, on the bench's `pp-chat`
witness replaying the faces of `agent`:
- the Agents tab says each agent's `weight` (`1.2 MB` for ag1, `812 B` for ag2), the overlay of the runs each run's
- `P` on a run plays the purge WITHOUT `--yes` first and shows what it would remove -- its bytes -- and the exact
  `--yes` command; a key typed wrong, or `escape`, plays nothing more
- `P`, the run's key typed, `enter`: the `--yes` command plays word for word as shown, after the purge without
  `--yes`; the overlay of the runs is read again, the run gone; a conversation the post kept open on the purged run
  leaves its memory
- `B` asks the date; `enter` plays the purge without `--yes`, then `--yes` once the date is typed again; a date
  written otherwise: the verb's `purge-invalid` on the remedy line, nothing more
The purges the verb refuses are `ui-purge-refused`'s.
"""
from __future__ import annotations

import json

from conductor.state import metadata
from tests.harness import support

P = support(__file__, "dialogue")
KEY = ",".join("w00001")
DAY = "2026-10-09"
DATE = ",".join(DAY).replace("-", "minus")
SIZE = ("--size", "140x40")


def said(*words: str) -> str:
    """-> a command the witness journals, written word by word."""
    return " ".join(words)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-purge")
    render, remedy = post.render, P.remedy_of

    def purges() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("purge ")]

    def row_of(text: str, name: str) -> str:
        return next((line for line in text.split("\n") if f" {name} " in f" {line} "), "")

    # --- P: the purge without --yes, shown over the Agents tab; a key typed wrong plays nothing more ---------------
    post.clear_journal()
    shown = render("--render", "dialogue", *SIZE, "--press", f"2,enter,P,{KEY[:-1]}2,enter", "--wait", "none:1")
    text = shown.stdout
    if (shown.returncode == 0 and "1.2 MB" in row_of(text, "ag1") and "812 B" in row_of(text, "ag2")
            and purges() == ["purge ag1 w00001 --json"]
            and "1.2 MB" in P.on_top(text)
            and said("./pp", "agent", "purge", "ag1", "w00001", "--yes", "--json") in P.on_top(text)):
        held("P shows the purge first, a wrong key plays nothing", f"ag1 1.2 MB and ag2 812 B on the Agents tab; the "
             f"purge's overlay says its bytes and the --yes command; w00002 typed, enter: the journal says {purges()}, "
             "no --yes")
    else:
        failures.append(f"  ✗ shown first                 rc={shown.returncode} {purges()} {text[-2000:]!r} {shown.stderr[-300:]!r}")

    # --- escape plays nothing; P and the key typed: the --yes command plays as shown, the memory forgets the run --
    path = metadata.path_of(post.made)          # the post's memory written by the bench's own hand: ag1's run open
    memory = json.loads(path.read_text(encoding="utf-8") or "{}") if path.is_file() else {}
    path.write_text(json.dumps({**memory, "ui": {"open": [{"agent": "ag1", "run": "w00001"}]}}), encoding="utf-8")
    before = [one.get("run") for one in post.remembered()]
    post.clear_journal()
    played = render("--render", "dialogue", *SIZE, "--press", f"escape,2,enter,P,escape,P,{KEY},enter",   # escape first: the line of the tab the memory opens
                    "--wait", "none:1.5", keep=True)
    after = [one.get("run") for one in post.remembered()]
    if (before == ["w00001"] and played.returncode == 0
            and purges() == ["purge ag1 w00001 --json", "purge ag1 w00001 --json", "purge ag1 w00001 --yes --json"]
            and "w00009" in row_of(played.stdout, "w00009") and row_of(played.stdout, "w00001") == "" and after == []):
        held("escape plays nothing, the purge plays as shown", f"P, escape, P, the key: the journal says {purges()}, "
             f"no --yes before the key; the overlay read again, w00009 alone; "
             f"the memory {before} -> {after}")
    else:
        failures.append(f"  ✗ played                      {purges()} memory {before} -> {after} "
                        f"{played.stdout[-1500:]!r} {played.stderr[-300:]!r}")

    # --- B: the runs before a date; a date written otherwise refused by the verb ------------------------------
    post.clear_journal()
    dated = render("--render", "dialogue", *SIZE, "--press", f"2,enter,B,{DATE},enter,{DATE},enter,"
                   f"B,{','.join('2026')},minus,1,3,minus,4,5,enter", "--wait", "none:1.5")
    if (dated.returncode == 0 and "purge-invalid" in remedy(dated.stdout)
            and purges() == [said("purge", "ag1", "--before", DAY, "--json"),
                             said("purge", "ag1", "--before", DAY, "--yes", "--json"),
                             said("purge", "ag1", "--before", "2026-13-45", "--json")]):
        held("B purges the runs before a date", f"the journal says {purges()}; the date written otherwise: "
             "purge-invalid on the remedy line, no --yes")
    else:
        failures.append(f"  ✗ before                      {purges()} {remedy(dated.stdout)!r} {dated.stdout[-1500:]!r} "
                        f"{dated.stderr[-300:]!r}")

    return 0
