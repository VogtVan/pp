"""Scenario `model-variants` -- 9 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
l-adaptateur-model, 2026-10-27): every variant of the modelled judgment that misses once provokes what its
name says -- `quota`, the provider's usage limit at every launch, misses nothing and is proven by `agent-run` --,
read from the run's trace (`-stats <key> -json`: repairs, refusals) and from the exchange's flow, then
the passage ends all the same -- one agent whose TURN carries a law of production (a proof at every
exchange: a value due), one `agent run --provider model --model <variant>` per variant:
- `conform`: no repair, no refusal -- the baseline and its launches
- `wrong-form`: a production of another form where the proof is due -> one repair
- `empty`: an empty production -> one repair
- `missing-code`: a code left out of the proof -> one repair (of the proof)
- `bare-fail`: every code of the proof failed, no fix, no gap -> one repair (the document replays)
- `wrong-channel`: a production due to the principal handed to the tool -> the soft catch (a block that carries a
  deviation), no repair counted
- `bare-call`: the bare call where the proof is due -> `principal-advances` in the model's tool result (the
  house conducts), then the house's advance repairs the empty answer
Each variant misses ONCE (the flow says `miss <variant>` once) and the run ends parked.
- the intention `bounce: true` (batch les-zones-muettes, 2026-10-29): once the held line of the value answered
  the proof, the model types the same call again -> the bounce (`messages.bounced`) in its tool result, the
  run moved by neither, parked all the same, no repair
- the intention `unprinted: true` (batch le-terminal-capture, 2026-11-19): the model writes in its message the
  productions its steps ask on `terminal` and pipes the proof fused under them -> its call is caught while the
  prints are due (a `stray` naming the documents due, the value handed, no repair) and the block that stands comes
  back in its tool result; the model prints there, proves again, and the run parks in the baseline's one launch
"""
from __future__ import annotations

from conductor.core import messages
from conductor import persistence
from tests.harness import support

M = support(__file__, "model")
VARIANTS = ("conform", "wrong-form", "empty", "missing-code", "bare-fail", "wrong-channel", "bare-call")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = M.House(bench)
    h.lawful("ag1")
    seen: dict[str, dict] = {}
    for variant in VARIANTS:
        before = set(h.keys("ag1"))
        done = h.run("ag1", f"play {variant}", variant=variant)
        key = next(iter(set(h.keys("ag1")) - before), "")   # the run this wake-up opened
        stats = h.stats("ag1", key) if key else {}
        flow = h.flow(key) if key else []
        trace = h.trace("ag1", key) if key else []
        misses = [one for one in flow if one.get("kind") == "thinking" and one.get("text") == f"miss {variant}"]
        refused = [one for one in flow if one.get("kind") == "tool-result" and one.get("error") is True
                   and "principal-advances" in str(one.get("content", ""))]
        seen[variant] = {"rc": done.returncode, "key": key, "awaits": h.awaits("ag1", key) if key else "",
                         "repairs": stats.get("repairs"), "refusals": stats.get("refusals"),
                         "launches": (h.responses()[-1] if h.responses() else {}).get("launches"),
                         "misses": len(misses), "advances_refused": len(refused),
                         "deviations": sum(1 for one in trace if one.get("kind") == "block" and one.get("deviation")),
                         "strays": sum(1 for one in trace if one.get("kind") == "stray"),
                         "stderr": done.stderr[-200:]}

    before = set(h.keys("ag1"))
    bounced_run = h.run("ag1", "play bounce", intent=[{"bounce": True}])
    bounced_key = next(iter(set(h.keys("ag1")) - before), "")
    bounced_flow = h.flow(bounced_key) if bounced_key else []
    answers = [str(one.get("content", "")).strip() for one in bounced_flow if one.get("kind") == "tool-result"]
    bounces = [one for one in answers if one == messages.bounced()]
    judged = [one for one in answers if one == messages.held("value")]
    calls = [str(one.get("shell", "")).splitlines()[0] for one in bounced_flow if one.get("kind") == "tool"]
    bounced_stats = h.stats("ag1", bounced_key) if bounced_key else {}

    before = set(h.keys("ag1"))
    unprinted_run = h.run("ag1", "play unprinted", intent=[{"unprinted": True}])
    unprinted_key = next(iter(set(h.keys("ag1")) - before), "")
    unprinted_trace = h.trace("ag1", unprinted_key) if unprinted_key else []
    unprinted_flow = h.flow(unprinted_key) if unprinted_key else []
    caught = [one for one in unprinted_trace if one.get("kind") == "stray" and one.get("due")]
    taken = [one for one in unprinted_trace if one.get("kind") == "answer" and one.get("channel") == "terminal"
             and one.get("document")]
    written = [one for one in unprinted_flow if one.get("kind") == "words" and one.get("launch") == 1]
    unprinted_stats = h.stats("ag1", unprinted_key) if unprinted_key else {}
    unprinted_launches = (h.responses()[-1] if h.responses() else {}).get("launches")

    def ended(one: dict) -> bool:
        return one["rc"] == 0 and one["awaits"] == persistence.MESSAGE

    base = seen["conform"]
    if ended(base) and base["repairs"] == 0 and base["refusals"] == 0 and base["misses"] == 0 and base["deviations"] == 0:
        held("conform: the baseline", f"run {base['key']}: {base['launches']} launches, parked, 0 repair, 0 refusal")
    else:
        failures.append(f"  ✗ conform                    {base}")
    if (bounced_run.returncode == 0 and bounced_key and h.awaits("ag1", bounced_key) == persistence.MESSAGE
            and len(judged) >= 1 and len(bounces) == 1 and bounced_stats.get("repairs") == 0
            and len(calls) >= 2 and calls[-1] == calls[-2]):
        held("bounce: the call typed again while the output waits", f"run {bounced_key}: the held line of the value then the same "
             f"call once more, answered `not played`; {len(calls)} calls, parked, 0 repair")
    else:
        failures.append(f"  ✗ bounce                     rc={bounced_run.returncode} key={bounced_key!r} judged={len(judged)} "
                        f"bounces={len(bounces)} calls={calls[-3:]} repairs={bounced_stats.get('repairs')} "
                        f"{bounced_run.stderr[-200:]!r}")
    if (unprinted_run.returncode == 0 and unprinted_key
            and h.awaits("ag1", unprinted_key) == persistence.MESSAGE and len(caught) == 1
            and caught[0].get("handed") and len(taken) == len(caught[0]["due"]) and written
            and unprinted_stats.get("repairs") == 0 and unprinted_launches == base["launches"]):
        held("unprinted: the house's advance caught while a print is due", f"run {unprinted_key}: the production "
             f"written in the first launch's message, its proof caught once naming {len(caught[0]['due'])} "
             f"print(s) due, then printed and proven in the same launch -- 0 repair, {unprinted_launches} "
             "launch(es), the baseline's, parked")
    else:
        failures.append(f"  ✗ unprinted                  rc={unprinted_run.returncode} key={unprinted_key!r} "
                        f"caught={[(one.get('due'), one.get('handed')) for one in caught]} taken={len(taken)} written={len(written)} "
                        f"repairs={unprinted_stats.get('repairs')} launches={unprinted_launches}/{base['launches']} "
                        f"{unprinted_run.stderr[-200:]!r}")
    for variant in ("wrong-form", "empty", "missing-code", "bare-fail"):
        one = seen[variant]
        if ended(one) and one["misses"] == 1 and isinstance(one["repairs"], int) and one["repairs"] >= 1:
            held(f"{variant}: one miss, repaired", f"run {one['key']}: {one['repairs']} repair, {one['launches']} "
                 f"launches, parked")
        else:
            failures.append(f"  ✗ {variant:<28} {one}")
    soft = seen["wrong-channel"]
    if ended(soft) and soft["misses"] == 1 and soft["repairs"] == 0 and soft["strays"] >= 1:
        held("wrong-channel: the catch", f"run {soft['key']}: a production handed as a value, {soft['strays']} stray(s) "
             f"on the trace, 0 repair counted, {soft['launches']} launches, parked")
    else:
        failures.append(f"  ✗ wrong-channel              {soft}")
    bare = seen["bare-call"]
    if (ended(bare) and bare["misses"] == 1 and bare["advances_refused"] >= 1
            and isinstance(bare["repairs"], int) and bare["repairs"] >= 1):
        held("bare-call: refused at the prompt, repaired by the advance", f"run {bare['key']}: principal-advances in "
             f"the model's tool result, {bare['repairs']} repair, {bare['launches']} launches, parked")
    else:
        failures.append(f"  ✗ bare-call                  {bare}")
    return 0
