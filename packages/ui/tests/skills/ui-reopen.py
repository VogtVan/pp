"""Scenario `ui-reopen` -- the post's memory of the conversations it keeps open (plan ui, batch
le-poste-sans-hub), on the bench's `pp-chat` witness:
- two conversations opened: the engine reads them in the space `ui` of the house's metadata, in order, each with its run
- the post opened with no agent named opens them again, each with its history, their tabs back
- `x` on both: the space `ui` is gone
- the same pair twice in the memory (batch l-onglet-unique-par-run): one conversation at the start, one opening
"""
from __future__ import annotations

import json

from conductor.state import metadata
from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-reopen")
    render, tabs_of = post.render, post.tabs_of

    # --- two conversations opened: the memory says them ----------------------------------------------
    opened = render("ag1", "ag2", "--render", "dialogue", "--size", "100x30")
    kept = post.remembered()
    if (opened.returncode == 0
            and kept == [{"agent": "ag1", "run": "w00001"}, {"agent": "ag2", "run": "w00002"}]):
        held("the open conversations are remembered", f"the engine reads {kept} in the space `ui`")
    else:
        failures.append(f"  ✗ remembered                  rc={opened.returncode} {kept} {opened.stderr[-300:]!r}")
        return 0

    # --- no agent named: the remembered ones come back, with their history ------------------------------
    post.clear_journal()
    again = render("--render", "dialogue", "--size", "100x30", keep=True)
    bar = tabs_of(again.stdout)
    journal = post.journal_lines()
    if (again.returncode == 0 and "ag1 · w00001" in bar and "ag2 · w00002" in bar
            and "exchanges ag1 w00001 --json" in journal and "open ag1 --run w00001" in journal
            and "open ag2 --run w00002" in journal):
        held("the post opens the remembered conversations again", f"bar {bar.strip()!r}; the journal says the "
             "history read and each run taken up by --run")
    else:
        failures.append(f"  ✗ reopened                    rc={again.returncode} {bar!r} {journal} {again.stdout!r} {again.stderr[-300:]!r}")

    # --- x on both: the memory is empty, its space gone ----------------------------------------------
    closed = render("--render", "dialogue", "--size", "100x30", "--press", "escape,x,escape,x", keep=True)
    left = post.remembered()
    if closed.returncode == 0 and left == [] and "ag1 · w00001" not in tabs_of(closed.stdout):
        held("closing both tabs empties the memory", "the space `ui` is gone from the metadata")
    else:
        failures.append(f"  ✗ forgotten                   rc={closed.returncode} {left} {tabs_of(closed.stdout)!r} {closed.stderr[-300:]!r}")

    # --- the same pair twice in the memory: one conversation, one opening ---------------------------------
    path = metadata.path_of(post.made)
    kept = json.loads(path.read_text(encoding="utf-8") or "{}") if path.is_file() else {}
    kept["ui"] = {"open": [{"agent": "ag1", "run": "w00001"}, {"agent": "ag1", "run": "w00001"}]}
    path.write_text(json.dumps(kept), encoding="utf-8")                  # the bench's own hand on its house
    post.clear_journal()
    twice = render("--render", "dialogue", "--size", "100x30", keep=True)
    bar_t = tabs_of(twice.stdout)
    opens = [one for one in post.journal_lines() if one.startswith("open ")]
    if twice.returncode == 0 and bar_t.count("ag1 · w00001") == 1 and opens == ["open ag1 --run w00001"]:
        held("a pair twice in the memory opens once", f"bar {bar_t.strip()!r}; the journal says one opening")
    else:
        failures.append(f"  ✗ memory twice                rc={twice.returncode} {bar_t!r} {opens} {twice.stderr[-300:]!r}")
    return 0
