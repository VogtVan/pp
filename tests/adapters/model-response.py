"""Scenario `model-response` -- 3 case(s): the LAST MESSAGE of a launch, under the modelled LLM -- one agent whose
TURN carries a law of production (every exchange owes a proof), one `agent run --provider model` per variant;
no output asks a last message (the engine adds no line `=> response` since 0.2.24), every production the
principal reads goes by its print call. The flow says each production pp took as `words` and the last
message of a launch as `final`, its length and its text -- the three dots of the form `empty` count none:
- `conform`: every launch of the exchange ends on a `final` of no characters, said AFTER its calls; the
  trace holds no line the engine added (`response-added`)
- `no-response`: the model hands back ONCE without it -- one launch ends on no `final`; the engine catches
  nothing (no repair, no deviation) and the run parks all the same
- the JUDGE never reads the last message: the sheets of both runs hold no agent's red
"""
from __future__ import annotations

import json
import subprocess
import sys

from conductor import persistence
from tests.harness import SOURCE, support

M = support(__file__, "model")
LAUNCHER = SOURCE / "tools" / "campaign" / "campaign.py"
RED = "rouge-agent"            # the verdict of a line where the agent did not do the act due
FINAL = "final"                # the kind of the flow that says the last message of a launch, its length and text


def _launches(flow: list[dict]) -> dict:
    """-> per launch of the flow, what the agent did in order: `words`, `tool` and `final` alone."""
    done: dict = {}
    for one in flow:
        if one.get("kind") in ("words", "tool", FINAL) and one.get("launch") is not None:
            done.setdefault(one["launch"], []).append(one)
    return done


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = M.House(bench)
    h.lawful("ag1")
    seen: dict[str, dict] = {}
    for variant in ("conform", "no-response"):
        before = set(h.keys("ag1"))
        done = h.run("ag1", f"play {variant}", variant=variant)
        key = next(iter(set(h.keys("ag1")) - before), "")
        flow = h.flow(key) if key else []
        stats = h.stats("ag1", key) if key else {}
        trace = h.trace("ag1", key) if key else []
        out = bench.temp() / f"sheet-{variant}"
        sheet = subprocess.run([sys.executable, str(LAUNCHER), "sheet", "--house", str(h.ws), "--agent",
                                "agents/ag1", "--run", key, "--out", str(out)], capture_output=True, text=True,
                               cwd=str(SOURCE))
        path = out / key / "sheet.json"
        lines = json.loads(path.read_text(encoding="utf-8")).get("lines", []) if path.is_file() else []
        seen[variant] = {
            "rc": done.returncode, "key": key, "awaits": h.awaits("ag1", key) if key else "",
            "launches": _launches(flow), "repairs": stats.get("repairs"),
            "deviations": sum(1 for one in trace if one.get("kind") == "block" and one.get("deviation")),
            "added": sum(1 for one in trace if one.get("kind") == "response-added"),
            "misses": sum(1 for one in flow if one.get("kind") == "thinking" and one.get("text") == f"miss {variant}"),
            "sheet": sheet.returncode, "verdicts": [one.get("verdict") for one in lines], "stderr": done.stderr[-200:]}

    def last_kinds(one: dict) -> list[str]:
        return [done[-1]["kind"] for done in one["launches"].values()]

    def finals(one: dict) -> int:
        """-> the launches whose last message is the hand-back alone: a `final` of no characters."""
        return sum(1 for done in one["launches"].values() for said in done
                   if said["kind"] == FINAL and said.get("chars") == 0)

    def said(one: dict) -> int:
        return sum(1 for done in one["launches"].values() for act in done if act["kind"] == "words")

    base, mute = seen["conform"], seen["no-response"]
    if (base["rc"] == 0 and base["awaits"] == persistence.MESSAGE and base["launches"]
            and all(kind == FINAL for kind in last_kinds(base)) and base["added"] == 0
            and finals(base) == len(base["launches"]) and base["repairs"] == 0 and base["misses"] == 0):
        held("conform: every launch ends on the three dots", f"run {base['key']}: {len(base['launches'])} launch(es), "
             f"each ending on a `final` of no characters said after its calls; no line added by the engine; "
             f"parked, 0 repair")
    else:
        failures.append(f"  ✗ conform                    last={last_kinds(base)} added={base['added']} finals={finals(base)} "
                        f"repairs={base['repairs']} rc={base['rc']} {base['stderr']!r}")
    if (mute["rc"] == 0 and mute["awaits"] == persistence.MESSAGE and mute["misses"] == 1
            and finals(mute) == finals(base) - 1 and said(mute) == said(base)
            and len(mute["launches"]) == len(base["launches"]) and mute["repairs"] == 0 and mute["deviations"] == 0):
        held("no-response: one launch hands back without it", f"run {mute['key']}: the miss made once, "
             f"{finals(mute)} launch(es) ending on a `final` where the conform run has {finals(base)}, in as many "
             f"launches, {said(mute)} production(s) taken in both; the engine catches nothing -- 0 repair, "
             "0 deviation --, the run parks all the same")
    else:
        failures.append(f"  ✗ no-response                finals={finals(mute)}/{finals(base)} said={said(mute)}/{said(base)} "
                        f"launches={len(mute['launches'])} "
                        f"misses={mute['misses']} repairs={mute['repairs']} deviations={mute['deviations']} {mute['stderr']!r}")
    if (base["sheet"] == 0 and mute["sheet"] == 0 and base["verdicts"] and mute["verdicts"]
            and RED not in base["verdicts"] and RED not in mute["verdicts"]):
        held("the judge never reads the last message", f"the sheet of the conform run: {len(base['verdicts'])} "
             f"line(s), the one of the no-response run: {len(mute['verdicts'])}; no agent's red on either")
    else:
        failures.append(f"  ✗ the judge                  sheet={base['sheet']}/{mute['sheet']} conform={base['verdicts']} "
                        f"no-response={mute['verdicts']}")
    return 0
