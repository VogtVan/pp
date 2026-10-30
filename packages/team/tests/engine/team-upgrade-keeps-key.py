"""Scenario `team-upgrade-keeps-key` -- 1 case(s) (batch le-tick, rework: the members, team 0.13.1;
split out of `team-review` by les-scenarios-par-maison, 2026-10-07): a house installed from a COPY
of the product, so that the kit of its source can be raised and the house upgraded.
- (r) an upgrade keeps the member's key [50] (I7, I18): uk asks the owner; the kit of the house's
  source raised, `./pp upgrade` renews uk's run; the reply resumes `--run <the same key>`, its trace
  says `renewed` then `reopened`, no history told; T1 done -- green before as well (arbitration 29)
"""
from __future__ import annotations

import json
import re
import time

from conductor import persistence
from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    engine3 = bench.source_with("kit-witness")        # a copy of the product: the house's source
    h = T.House(bench, engine=engine3, script={
        "uk": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which version?"}}},
               {"sleep": 0.1, "body": {"done": "upgraded"}}]})
    by_kind, all_ended, result_of, runs_launched = T.by_kind, T.all_ended, T.result_of, T.runs_launched

    # --- (r) an upgrade keeps the member's key [50] -- I7, I18: a real upgrade ------------------------
    h.declare("keep", "---\nagents: |\n  uk agents/uk\nroot: uk\nschedule: off\n---\nKeep the key.\n")
    keep = h.call("team", "start", "keep", "--message", "bump it", *h.harnessed)
    asked_k = h.settled("keep", lambda found: bool(by_kind(found, "wake-ended", agent="uk")) and all_ended(found), 60)
    found_k3 = h.events("keep")
    key_k = next((one.get("run") for one in by_kind(found_k3, "wake-ended", agent="uk")), "")
    ask_k = next((one["id"] for one in by_kind(found_k3, "post", verb="ask")), -1)
    kit3 = engine3.parent.parent / "bases" / "kit" / "package.yaml"
    text3 = kit3.read_text(encoding="utf-8")
    version3 = re.search(r"^version: (\S+)$", text3, re.M).group(1)
    head3, last3 = version3.rsplit(".", 1)
    kit3.write_text(text3.replace(f"version: {version3}", f"version: {head3}.{int(last3) + 1}", 1), encoding="utf-8")
    upgraded = None
    deadline = time.monotonic() + 30                  # the last on-end tick may still be leaving
    while time.monotonic() < deadline:
        upgraded = cli(h.engine, "--instance", str(h.house), "upgrade", cwd=h.ws, env=h.env)
        if upgraded.returncode == 0 or "maintenance-busy" not in upgraded.stderr:
            break
        time.sleep(0.5)
    meta_k = h.meta_of("agents/uk")
    slot_k = persistence.slot_of(meta_k, key_k) if key_k else h.ws
    marked_k = slot_k.is_file() and "renewed" in json.loads(slot_k.read_text(encoding="utf-8") or "{}")
    replied_k = h.call("team", "post", "keep", "--task", "T1", "--reply", str(ask_k), "--message", "the next one")
    done_k = h.settled("keep", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found_k3 = h.events("keep")
    intents_k = by_kind(found_k3, "wake-intent", agent="uk")
    traces_k = sorted((meta_k / ".sys" / "state").glob(f"session-*-{key_k}.jsonl")) if key_k else []
    kinds_k = [one.get("kind") for one in T.lines(traces_k[0])] if len(traces_k) == 1 else []
    told_k = h.prompts_of("uk")[-1] if h.prompts_of("uk") else ""
    module = h.module()
    state_k = module.state_of(h.journal_of("keep"))
    history_k = module.history_of(state_k, "uk", "T1").split("\n", 1)[0]
    reply_k = next((one for one in by_kind(found_k3, "post", **{"from": "house"}) if one.get("re") == ask_k), {})
    shown_k = module.message_of(state_k, "uk", state_k["messages"][reply_k["id"]]) if reply_k else None
    if (keep.returncode == 0 and asked_k and key_k and upgraded is not None and upgraded.returncode == 0
            and "renewed" in upgraded.stdout + upgraded.stderr and marked_k
            and replied_k.returncode == 0 and done_k and len(intents_k) == 2 and intents_k[1].get("run") == key_k
            and runs_launched(found_k3, "uk") == {key_k}
            and "renewed" in kinds_k and "reopened" in kinds_k[kinds_k.index("renewed"):]
            and history_k and history_k not in told_k and shown_k and shown_k.split(" -- ", 1)[0] in told_k
            and result_of(found_k3, "T1") == "upgraded"):
        held("(r) an upgrade keeps the member's key", f"uk's run {key_k} renewed by the house's upgrade (kit "
             f"{version3} -> {head3}.{int(last3) + 1}); the reply resumes --run {key_k}, one trace saying renewed then "
             "reopened, no history told; T1 done -- I7, I18 (green before as well: the renewal mark stands at the "
             "slot's path)")
    else:
        failures.append(f"  ✗ (r) the key kept            {keep.returncode}/{getattr(upgraded, 'returncode', None)}/"
                        f"{replied_k.returncode} asked={asked_k} key={key_k} marked={marked_k} done={done_k} "
                        f"intents={[(one['id'], one.get('run')) for one in intents_k]} traces={len(traces_k)} "
                        f"kinds={kinds_k[-8:]} {getattr(upgraded, 'stdout', '')[-200:]!r} "
                        f"{getattr(upgraded, 'stderr', '')[-200:]!r} {told_k[:300]!r}")
    return 0
