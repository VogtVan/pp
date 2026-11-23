"""Scenario `ui-transcript-cost` -- the cost of a line added to the transcript (plan pp-fixes, batch
le-transcript-virtualise, s.1372), `ui-transcript`'s sibling (rule 10): on a `TranscriptView` alone in a Textual app of
160x45 played in a subprocess, no house:
- a past of 500, 2000 then 4000 events built (`rebuild`, ten events a turn: the message, the conduction, two steps, a
  call and its result, a thought, the words in markdown, the launch's end, the verdict): the widgets under the
  transcript are counted -- the same count whatever the number of events
- one line added (`add`) on each past: the same widgets, the same objects -- nothing mounted again
- the time of the add, net of what a bare pause costs the pilot, is said beside the count and never judged: a time
  depends on the load of the pass (rule 10)
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE

SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
PASTS = (500, 2000, 4000)                  # the events of the pasts built
PROBE = r'''
import asyncio, json, sys, time
sys.path.insert(0, sys.argv[1])
PASTS = [int(one) for one in sys.argv[2:]]
from textual.app import App
from model.dialogue import Event
from panes.transcript import TranscriptView


def turn(n):
    at = f"2026-11-07T10:{(n // 60) % 60:02d}:{n % 60:02d}+00:00"
    said = lambda kind, **fields: Event(kind, at, "r00001", fields)
    return [said("principal", text=f"question {n}"),
            said("conduction", launch=1, chars=1200, blocks=[{"stack": "BOOT ▸ MEMBER ▸ TURN{2/4}"}], text="served"),
            said("step", event="launch", launch=1), said("step", event="repair", n=1),
            said("tool", id=f"t{n}", name="Bash", input={"command": "ls"}),
            said("tool-result", id=f"t{n}", content="a.py"),
            said("thinking", launch=1, tokens=40, text="a thought"),
            said("words", launch=1, text=f"the answer to {n}\n\n| a | b |\n|---|---|\n| 1 | 2 |"),
            said("agent", launch=1, cost_usd=0.01),
            said("verdict", state="parked", cost_usd=0.01, launches=1)]


class Probe(App):
    def compose(self):
        yield TranscriptView()


async def main():
    app, out = Probe(), {"pasts": []}
    events = [one for n in range(max(PASTS) // 10 + 1) for one in turn(n)]
    async with app.run_test(size=(160, 45)) as pilot:
        view = app.query_one(TranscriptView)
        for count in PASTS:
            await view.rebuild(events[:count])
            await pilot.pause()
            before = list(view.walk_children())
            bare = []
            for _ in range(3):
                started = time.perf_counter()
                await pilot.pause()
                bare.append((time.perf_counter() - started) * 1000)
            started = time.perf_counter()
            await view.add(Event("tool", "2026-11-07T11:00:00+00:00", "r00001", {"id": "late", "name": "Read"}))
            await pilot.pause()
            gross = (time.perf_counter() - started) * 1000
            after = list(view.walk_children())
            kept = len(after) >= len(before) and all(one is two for one, two in zip(before, after))
            out["pasts"].append({"events": count, "widgets": len(before), "after": len(after), "kept": kept,
                                 "ms": round(gross - sorted(bare)[1], 1)})
    print(json.dumps(out))


asyncio.run(main())
'''


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    probe = bench.temp() / "transcript-cost-probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL), *(str(one) for one in PASTS)],
                            capture_output=True, text=True, cwd=bench.temp(), timeout=180)
    try:
        pasts = json.loads(played.stdout.strip().splitlines()[-1])["pasts"]
    except (ValueError, IndexError, KeyError):
        pasts = []
    widgets = [one["widgets"] for one in pasts]
    timed = ", ".join(f"{one['events']}: {one['ms']} ms" for one in pasts)

    # --- the widgets under the transcript bounded, a line added mounting nothing ----------------------------------
    if (played.returncode == 0 and [one["events"] for one in pasts] == list(PASTS) and len(set(widgets)) == 1
            and all(one["after"] == one["widgets"] and one["kept"] for one in pasts)):
        held("a line added mounts nothing", f"{widgets[0]} widget(s) under the transcript at "
             f"{', '.join(map(str, PASTS))} events, the same after a line added; the add, net of a pause: {timed}")
    else:
        failures.append(f"  ✗ the cost of a line           rc={played.returncode} (events, widgets, after, kept) "
                        f"{[(one['events'], one['widgets'], one['after'], one['kept']) for one in pasts]}; {timed} "
                        f"{played.stderr[-600:]!r}")
    return 0
