"""Scenario `diagnostic` -- the engine renders its own diagnostics (plan agent, batch
le-diagnostic-au-bloc): a signal declaring a `level:` is said IN the block, by the engine,
whether or not any package reads the bus.
- a drifted card renders `card-drift · warning · <home> differs from the contract -- ./pp doctor`
  on the boot's first block, between the laws and the instruction; the bus latches as before
- once per run and per fact: a view and a later block stay silent, a fresh run says it again
- a document repaired twice renders `repaired · warning · <document>` on the REPAIR block
- a refusal met twice renders `refused · note · <code>` on the NEXT block -- the refusal
  happened outside any block
- a serve row whose start tag is gone renders `serve-stale · note · …`
- the section is weighed as the `diagnostic` part of the trace's block line, summed by the reader
- a signal declaring a level outside the three refuses `level-invalid` at the build, by name
"""
from __future__ import annotations

import json

from conductor import Conductor, render, discovery, persistence, events, instance
from conductor.core.errors import Refusal
from conductor.state import traces
from conductor import install as install_module
from tests.harness import load_script, PRODUCT_ENGINE, session_of

LOUD = """name: loud
version: 0.0.1
description: a package whose signal claims a level the engine does not know
requires: []
contributes:
  events:
    signals:
      shouted: {level: loud, priority: 1}
"""


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("diag")
    made = env.made
    ws = made.parent
    env.write_member("constraints.behavior: |\n  D1  the member's law stands on the first block\n")
    adapters = install_module.product_root(PRODUCT_ENGINE) / "adapters"
    load_script(adapters / "claude" / "wire.py").wire(ws, made)
    projected = ws / ".claude" / "skills" / "pp" / "SKILL.md"
    projected.write_text(projected.read_text(encoding="utf-8") + "\nOLD LAW\n", encoding="utf-8")

    # --- a drifted card is said on the boot's first block, and still latched ------------
    first_c = env.conductor("t")
    first = render(first_c.start(first_c.boot("BOOT.md")))
    line = ("card-drift · warning · .claude/skills/pp/SKILL.md differs from the contract"
            " -- ./pp doctor")
    latched = persistence.signals_of(session_of(made))
    placed = ("▌ DIAGNOSTIC" in first and line in first
              and first.index("▌ CONSTRAINTS") < first.index("▌ DIAGNOSTIC")
              < first.index("▌ INSTRUCTION"))
    if (placed and first.count("▌ DIAGNOSTIC") == 1
            and any(one.get("signal") == "card-drift" and one.get("source") == "engine"
                    for one in latched)):
        held("a drifted card is a diagnostic", "the engine says it in the boot's block -- "
             "signal · level · fact -- way out -- after the laws, before the ask; the bus "
             "latches the same entry as before")
    else:
        failures.append(f"  ✗ card-drift diagnostic       placed={placed} "
                        f"count={first.count('▌ DIAGNOSTIC')} latched={latched!r}")

    # --- once per run and per fact: a view and a later block stay silent -------------
    viewed = render(env.conductor("t").peek())
    later = render(env.conductor("t").submit(""))
    env.conductor("t").forget()
    again_c = env.conductor("t")
    again = render(again_c.start(again_c.boot("BOOT.md")))
    if ("DIAGNOSTIC" not in viewed and "DIAGNOSTIC" not in later
            and line in again):
        held("a diagnostic is said once per run", "the peek re-forms none, the next block "
             "carries none -- a fresh run says the drift again")
    else:
        failures.append(f"  ✗ once per run                view={'DIAGNOSTIC' in viewed} "
                        f"later={'DIAGNOSTIC' in later} again={line in again}")

    # --- a document repaired twice (a fused environment: WORK and its proof on one block)
    rep_env = bench.env("diag-repair", pin=False)
    (rep_env.made / "REP.md").write_text(
        "---\nname: REP\nkind: proc\ndescription: proves under one law\n"
        "constraints.production: |\n  R1  say it plainly\nproc: |\n  WORK\n---\nthe ask\n",
        encoding="utf-8")
    rep_c = rep_env.conductor("r")
    rep_c.start(rep_env.made / "REP.md")
    failing = '[{"code": "R1", "evidence": "off", "verdict": "fail"}]'
    once = rep_env.conductor("r").submit(failing)
    twice = rep_env.conductor("r").submit(failing)
    once_text, twice_text = render(once), render(twice)
    if (once.repair == 1 and "DIAGNOSTIC" not in once_text
            and twice.repair == 2 and "repaired · warning · REP" in twice_text):
        held("a document repaired twice is a diagnostic", "the first repair says nothing; the "
             "second renders `repaired · warning · REP` on the REPAIR block itself")
    else:
        failures.append(f"  ✗ repaired diagnostic         {once.repair}/{twice.repair} "
                        f"{'repaired' in twice_text}")

    # --- a refusal met twice, outside any block, is said on the next one -------------------
    bound = rep_env.conductor("r")
    bound.resume(bound.boot("BOOT.md"))          # binds the run: its trace is the refusal's home
    bound.noted(Refusal("ghost-door", "a door nobody has"))
    bound.noted(Refusal("ghost-door", "a door nobody has"))
    after = render(rep_env.conductor("r").resume(rep_env.conductor("r").boot("BOOT.md")))
    if "refused · note · ghost-door" in after and "repaired · warning · REP" not in after:
        held("a refusal met twice is said on the next block", "the refusal happened with no "
             "block to carry it -- the trace keeps the line, the next block renders it once; "
             "the repair diagnostic, already rendered, does not return")
    else:
        failures.append(f"  ✗ refused diagnostic          {after[-600:]!r}")

    # --- a serve row whose start tag is gone -------------------------------------------------
    (made / "NOTE.md").write_text("# A note\n\n## Somewhere\n\ntext\n", encoding="utf-8")
    (made / "STALE.md").write_text(
        "---\nname: STALE\nkind: proc\ndescription: serves a lost tag\n"
        "proc: |\n  SERVE NOTE.md[## Nowhere..]\n  INFER\n---\nread it\n", encoding="utf-8")
    stale_c = env.conductor("s")
    stale = render(stale_c.start(made / "STALE.md"))
    if ("serve-stale · note · NOTE.md -- start tag gone, nothing served: `## Nowhere`" in stale
            and "no line of this document starts with" in stale):
        held("a lost tag is a diagnostic", "the reading's own line says the miss, and the "
             "DIAGNOSTIC section says it with its level")
    else:
        failures.append(f"  ✗ serve-stale diagnostic      {stale[-400:]!r}")

    # --- the section is weighed, the reader sums it ---------------------------------------
    trace_lines = [json.loads(one) for one in
                   (session_of(made).parent / persistence.trace_of(session_of(made)))
                   .read_text(encoding="utf-8").splitlines() if one.strip()]
    blocks = [one for one in trace_lines if one.get("kind") == "block"]
    formed = [one for one in trace_lines if one.get("kind") == "diagnostic"]
    weights = [one.get("weight", {}).get("diagnostic") for one in blocks]
    found = traces.runs(made / instance.STATE)
    summed = sum(exchange.parts.get("diagnostic", 0)
                 for run in found for exchange in run.exchanges)
    if (weights and weights[0] and weights[0] > 0 and all(w == 0 for w in weights[1:])
            and formed and formed[0].get("signal") == "card-drift"
            and formed[0].get("level") == "warning"
            and summed >= weights[0]
            and "diagnostic" in traces.render(found, None, None)):
        held("the section is weighed", f"`diagnostic` {weights[0]} c on the boot's block, 0 after; "
             "the trace keeps the formed line; the reader sums the part and -stats names it")
    else:
        failures.append(f"  ✗ weighed                     {weights[:3]} formed={len(formed)} "
                        f"summed={summed}")

    # --- a level the engine does not know refuses at the build ---------------------------
    root = made / instance.VENDOR / "loud@0.0.1"
    root.mkdir(parents=True)
    (root / "package.yaml").write_text(LOUD, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["loud"] = "0.0.1"
    instance.write(made, pins)
    expect("level-invalid", lambda: events.providers(made))
    held("an unknown level refuses at the registry", "`level: loud` on `shouted` -- refused by "
         "the signal's name before anything is written; the three levels are the engine's")
    return 0
