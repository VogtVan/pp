"""Scenario `ui-memory` -- the post's memory of the conversations it keeps open, and `u` that reads a run's past again,
on ONE post of the bench's `pp-chat` witness whose script changes by `use()`:
- two conversations opened: the engine reads them in the space `ui` of the house's metadata, in order, each with its run
- the post opened with no agent named gives them back DORMANT: their tabs back, each run's exchanges read and shown in
  history, no `agent chat` launched, no flow read
- a message sent in a tab given back opens its conversation on its run, the answer in that tab
- `x` on both: the space `ui` is gone
- the same pair twice in the memory: one tab, its exchanges read once, nothing launched
- `u` on a tab given back reads its kept flow after its exchanges and shows it as lived, the history gone
- `u` reads the tab's kept flow and builds it in ONE mount: the transcript laid out no more for thirty turns than for
  ten -- both taller than the screen --, one arrangement apart at most under the load of a pass
- the turn reloaded reads as the same turn lived, the hours aside
- during a turn `u` reloads nothing and the remedy line says why
- a tab given back reads its past when it is first shown: the hidden one reads nothing until then (batch
  la-borne-et-le-demarrage); a tab given back carries the name the catalogue says of its run
"""
from __future__ import annotations

import json
import re

from conductor.state import metadata
from tests.harness import support

P = support(__file__, "dialogue")

TURN = "i,h,i,enter,wait:waiting"
TIME = re.compile(r"\d\d:\d\d:\d\d")
ANSWERED = P.FACES["exchanges"]["ag1"]["w00001"][0]["response"]    # what the history of ag1's run says


def flowed(turns: int) -> dict:
    """`ag1`'s flow whose run keeps `turns` exchanges of the witness's first one, dated as `agent flow` dates them --
    what `u` reads again."""
    flow = P.script("w00001", "the agent says")
    lived = [one for one in flow["exchanges"][0] if "sleep" not in one]
    past = [{**one, "at": "2026-10-17T10:00:00+00:00", **({"exchange": n} if "exchange" in one else {})}
            for n in range(1, turns + 1) for one in lived]
    return {"agents": {"ag1": flow}, "faces": {**P.FACES, "flow": {"ag1": {"w00001": past}}}}


def transcript_rows(text: str) -> list[str]:
    """-> the rows of a capture's transcript, the hours taken out: under the tab bar, above the message line's rule."""
    rows = text.split("\n")
    end = next((n for n in range(len(rows) - 1, 3, -1) if rows[n].strip().startswith("─")), len(rows))
    end = next((n for n in range(end - 1, 3, -1) if rows[n].strip().startswith("─")), end)
    return [TIME.sub("hh:mm:ss", row).rstrip() for row in rows[5:end] if row.strip()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-memory")
    render, tabs_of = post.render, post.tabs_of

    def remember(*pairs: tuple[str, str]) -> None:
        """The post's memory written by the bench's own hand on its house: these conversations open."""
        path = metadata.path_of(post.made)
        kept = json.loads(path.read_text(encoding="utf-8") or "{}") if path.is_file() else {}
        kept["ui"] = {"open": [{"agent": agent, "run": run} for agent, run in pairs]}
        path.write_text(json.dumps(kept), encoding="utf-8")

    # --- two conversations opened: the memory says them ----------------------------------------------
    opened = render("ag1", "ag2", "--render", "dialogue", "--size", "100x30")
    kept = post.remembered()
    if (opened.returncode == 0
            and kept == [{"agent": "ag1", "run": "w00001"}, {"agent": "ag2", "run": "w00002"}]):
        held("the open conversations are remembered", f"the engine reads {kept} in the space `ui`")
    else:
        failures.append(f"  ✗ remembered                  rc={opened.returncode} {kept} {opened.stderr[-300:]!r}")
        return 0

    # --- no agent named: the remembered ones come back dormant, in history ------------------------------
    post.clear_journal()
    again = render("--render", "dialogue", "--size", "100x30", "--press", "ctrl+left", keep=True)
    bar = tabs_of(again.stdout)
    journal = post.journal_lines()
    if (again.returncode == 0 and "ag1 · w00001" in bar and "ag2 · w00002" in bar
            and "exchanges ag1 w00001 --json" in journal and "exchanges ag2 w00002 --json" in journal
            and not [one for one in journal if one.startswith(("open ", "flow "))]
            and ANSWERED in again.stdout and not P.heads_of(again.stdout)):
        held("the post gives the remembered conversations back in history", f"bar {bar.strip()!r}; the journal "
             "says both exchanges read, no opening, no flow; ag1 shows its history's answer, no turn lived")
    else:
        failures.append(f"  ✗ reopened                    rc={again.returncode} {bar!r} {journal} {again.stdout!r} {again.stderr[-300:]!r}")

    # --- a message in a tab given back: its conversation opens on its run ---------------------------------
    post.clear_journal()
    woken = render("--render", "dialogue", "--size", "100x30", "--press", "i,h,i,enter", "--wait", "waiting",
                   keep=True)
    said = post.journal_lines()
    at = {line: n for n, line in enumerate(said)}
    if (woken.returncode == 0 and "open ag2 --run w00002" in at and "message ag2 hi" in at
            and at["open ag2 --run w00002"] < at["message ag2 hi"] and "open ag1 --run w00001" not in at
            and "two says two" in woken.stdout):
        held("a message wakes the conversation of its tab", "ag2 opened on --run w00002 then the message, ag1 left "
             "dormant; the answer in the tab")
    else:
        failures.append(f"  ✗ woken                       rc={woken.returncode} {said} {woken.stdout!r} {woken.stderr[-300:]!r}")

    # --- x on both: the memory is empty, its space gone ----------------------------------------------
    closed = render("--render", "dialogue", "--size", "100x30", "--press", "escape,x,escape,x", keep=True)
    left = post.remembered()
    if closed.returncode == 0 and left == [] and "ag1 · w00001" not in tabs_of(closed.stdout):
        held("closing both tabs empties the memory", "the space `ui` is gone from the metadata")
    else:
        failures.append(f"  ✗ forgotten                   rc={closed.returncode} {left} {tabs_of(closed.stdout)!r} {closed.stderr[-300:]!r}")

    # --- the same pair twice in the memory: one conversation, one opening ---------------------------------
    remember(("ag1", "w00001"), ("ag1", "w00001"))
    post.clear_journal()
    twice = render("--render", "dialogue", "--size", "100x30", keep=True)
    bar_t = tabs_of(twice.stdout)
    said_t = post.journal_lines()
    opens = [one for one in said_t if one.startswith("open ")]
    if (twice.returncode == 0 and bar_t.count("ag1 · w00001") == 1 and not opens
            and said_t.count("exchanges ag1 w00001 --json") == 1):
        held("a pair twice in the memory gives one tab", f"bar {bar_t.strip()!r}; its exchanges read once, nothing "
             "launched")
    else:
        failures.append(f"  ✗ memory twice                rc={twice.returncode} {bar_t!r} {opens} {twice.stderr[-300:]!r}")

    # --- u on a tab given back: its kept flow after its exchanges, shown as lived, the history gone ----------------
    script = P.script("w00001", "the agent says")
    lived = [one for one in script["exchanges"][0] if "sleep" not in one]
    post.use({"agents": {"ag1": script, "ag2": P.script("w00002", "two says")},
              "faces": {**P.FACES, "flow": {"ag1": {"w00001": lived}}}})
    remember(("ag1", "w00001"), ("ag2", "w00002"))
    post.clear_journal()
    taken = render("--render", "dialogue", "--size", "100x30", "--press", "ctrl+left,u", keep=True)
    said = post.journal_lines()
    read = said.index("exchanges ag1 w00001 --json") if "exchanges ag1 w00001 --json" in said else -1
    flowed_at = said.index("flow ag1 w00001 --json") if "flow ag1 w00001 --json" in said else -1
    if (taken.returncode == 0 and 0 <= read < flowed_at and not [one for one in said if one.startswith("open ")]
            and "the agent says one" in taken.stdout and "the agent says two" in taken.stdout
            and ANSWERED not in taken.stdout):
        held("u reads the kept flow of a tab given back", "its exchanges read at the opening, its flow at u; its words "
             "shown as lived, the history gone, nothing launched")
    else:
        failures.append(f"  ✗ u and the flow              rc={taken.returncode} {said} {taken.stdout!r} {taken.stderr[-300:]!r}")

    # --- u: the kept flow built in one mount, as long as it is ---------------------------------------------
    resumed = ("ag1", "--run", "w00001", "--render", "dialogue", "--size", "120x40")
    post.use(flowed(10))
    short = render(*resumed, "--press", "layouts,u,layouts")       # both taller than the screen: one scrollbar
    post.use(flowed(30))
    post.clear_journal()
    long = render(*resumed, "--press", "layouts,u,layouts")
    counts = [re.search(r"^layouts (\d+) (\d+)$", done.stdout, re.M) for done in (short, long)]
    grown = [int(found.group(2)) - int(found.group(1)) for found in counts if found]
    if (short.returncode == 0 and long.returncode == 0 and len(grown) == 2 and grown[1] <= grown[0] + 1
            and "flow ag1 w00001 --json" in post.journal_lines() and "the agent says two" in long.stdout):
        held("u builds the kept flow in one mount", f"the transcript laid out {grown[0]} more time(s) for ten turns "
             f"and {grown[1]} for thirty; the flow read, its last turn shown")
    else:
        failures.append(f"  ✗ u in one mount              rc={short.returncode}/{long.returncode} grown={grown} "
                        f"{post.journal_lines()} {long.stdout[-1500:]!r} {long.stderr[-400:]!r}")

    # --- the turn reloaded reads as the turn lived ---------------------------------------------------------
    post.use(flowed(1))
    lived_t = render(*resumed, "--press", TURN)
    reloaded = render(*resumed, "--press", "u")
    seen, again_read = transcript_rows(lived_t.stdout), transcript_rows(reloaded.stdout)
    if lived_t.returncode == 0 and reloaded.returncode == 0 and seen and seen == again_read:
        held("a turn reloaded reads as the turn lived", f"{len(again_read)} rows the same, hours aside")
    else:
        failures.append(f"  ✗ reloaded as lived           {seen} / {again_read} {reloaded.stderr[-300:]!r}")

    # --- u during a turn: nothing reloaded, the remedy line says why ---------------------------------------
    post.use(P.SCRIPT)
    post.clear_journal()
    busy = render("ag3", "--run", "w00003", "--render", "dialogue", "--size", "120x40",
                  "--press", "i,h,i,enter,wait:principal,escape,u")
    refused = P.remedy_of(busy.stdout)
    if (busy.returncode == 0 and refused and refused != P.remedy_of(lived_t.stdout)
            and not [line for line in post.journal_lines() if line.startswith("flow ")]):
        held("u during a turn reloads nothing", "the remedy line says why; no flow read")
    else:
        failures.append(f"  ✗ u during a turn             rc={busy.returncode} {refused!r} {post.journal_lines()} "
                        f"{busy.stdout[-800:]!r} {busy.stderr[-300:]!r}")

    # --- a tab given back reads its past when it is first shown; a hidden one waits ------------------------
    remember(("ag1", "w00001"), ("ag2", "w00002"))
    post.clear_journal()
    hidden = render("--render", "dialogue", "--size", "100x30", keep=True)
    said_h = post.journal_lines()
    post.clear_journal()
    shown = render("--render", "dialogue", "--size", "100x30", "--press", "ctrl+left", keep=True)
    said_s = post.journal_lines()
    if (hidden.returncode == 0 and "exchanges ag2 w00002 --json" in said_h
            and "exchanges ag1 w00001 --json" not in said_h
            and shown.returncode == 0 and said_s.count("exchanges ag1 w00001 --json") == 1):
        held("a tab given back reads its past when shown", "the active tab (ag2) read its exchanges, the hidden one "
             "(ag1) nothing; shown, ag1 read them once")
    else:
        failures.append(f"  ✗ past when shown             {said_h} / {said_s} {hidden.stderr[-300:]!r}")

    # --- a tab given back carries the name the catalogue says of its run --------------------------------------
    named = json.loads(json.dumps(P.SCRIPT))
    named["faces"]["status"]["ag1"][0]["name"] = "demo"
    post.use(named)
    remember(("ag1", "w00001"))
    titled = render("--render", "dialogue", "--size", "100x30", keep=True)
    if titled.returncode == 0 and "demo" in tabs_of(titled.stdout):
        held("a tab given back carries its run's name", f"bar {tabs_of(titled.stdout).strip()!r}")
    else:
        failures.append(f"  ✗ name given back             {tabs_of(titled.stdout)!r} {titled.stderr[-300:]!r}")
    return 0
