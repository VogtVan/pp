"""Scenario `launcher/plan` -- 5 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
la-campagne-au-banc and le-mode-reel, 2026-10-27/28): the campaign's launcher (`tools/campaign/campaign.py`)
proven WITHOUT a real harness:
- (a) `plan --set <a throwaway set of two roots>` writes one plan per root x channel (relayed strict,
  relayed hybrid, bare), launches nothing: every plan says `launched: false`, names its command, its
  door and its root; the launcher is generic -- its code names no root of the patterns
- (b) a manifest is judged by its name: a root without `message:` refuses `manifest-invalid`, a set
  without `campaign.yaml` refuses `manifest-missing`, a root the set lacks refuses `root-unknown`; the
  set's `packages:` rides every plan, a package the source does not carry refuses `manifest-invalid`
- (c) the set of the patterns is the launcher's default: twenty roots planned (the six patterns of the
  engine, the fourteen ordinary situations of a turn), each root of documents judged by the engine -- a
  throwaway instance opens on it under `PP_DOCUMENTS` (and `PP_DOOR` where the root has a door) and renders
  its first block without a refusal: READ_LINES a WORK, LAPS its field, CYCLE its element, ROUTE a PICK next
  between LEFT and RIGHT, BEGIN before the WORK, REVIEW offered to the WORK; LONG_READ its reading cut under
  the host's cap (the bare call under CONTINUE carries its fact), TWO_STEPS, BOUNDED and RENEWED their first
  WORK, PROOF (twice) and STUBBORN their line, STRAY and HELLO (four times) a WORK; every
  root carries its `expect:` (the plan copies it); a key the manifest does not know under `expect:` refuses
  `manifest-invalid` naming it; the relayed plan of `bounded` carries the root's own `--launches 1`, the plan
  of `renewed` its `resume` (`--run <key>`) after a first wake-up bounded at one launch (batch
  les-zones-muettes, 2026-10-29)
- (d) the provider's binary is the adapter's: `play --provider claude` on a PATH without `claude`
  refuses `provider-missing` naming the binary; `--provider model` asks no binary (the refusal
  that follows is the set's, never the provider's); `report` on a date no campaign wrote refuses
  `campaign-missing`
- (g) the DRY PLAN of a real provider: `plan --provider claude --model sonnet --effort low --repeat 3` writes
  its plans with `repeat` 3 and `effort` low, the relayed command carrying `--effort low`, the binary never
  consulted (an empty PATH); `--repeat 0` refuses `repeat-invalid`, an effort the engine does not know
  refuses `policy-invalid`"""
from __future__ import annotations

import json
import os
import re
import shutil

import yaml

from tests.harness import SOURCE, cli, support

C = support(__file__, "conduction")
KEY = re.compile(r"run ([0-9a-f]{6})")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- (a) the plans of a throwaway set, nothing launched --------------------------------------------
    made = C.witness_set(bench)
    out = bench.temp() / "dry"
    planned = C.launcher("plan", "--set", str(made), "--out", str(out))
    files = sorted(out.glob("*.json")) if out.is_dir() else []
    plans = [json.loads(one.read_text(encoding="utf-8")) for one in files]
    code = C.LAUNCHER.read_text(encoding="utf-8")
    named = [one for one in ("read-lines", "READ_LINES", "LAPS", "cyclewit") if one in code]
    if (planned.returncode == 0 and len(plans) == 6 and not named
            and all(one.get("launched") is False and one.get("command") and one.get("documents") for one in plans)
            and {(one["channel"], one["conduction"]) for one in plans}
            == {(C.RELAYED, C.STRICT), (C.RELAYED, C.HYBRID), (C.BARE, None)}
            and all("--door" in one["command"] for one in plans if one["channel"] == C.RELAYED)
            and all(one["environment"].get("PP_DOOR") and one["stdin"] for one in plans if one["channel"] == C.BARE)):
        held("(a) the plans of a set, nothing launched", f"{len(plans)} plans for 2 roots x 3 channels, every one "
             "`launched: false`; the launcher names no root of the patterns")
    else:
        failures.append(f"  ✗ (a) the plans               rc={planned.returncode} n={len(plans)} named={named} "
                        f"{planned.stderr[-200:]!r}")

    # --- (b) the manifest judged ---------------------------------------------------------------------------
    mute = C.witness_set(bench, message=False)
    no_message = C.launcher("plan", "--set", str(mute), "--out", str(bench.temp()))
    empty = bench.temp() / "empty"
    empty.mkdir()
    no_manifest = C.launcher("plan", "--set", str(empty), "--out", str(bench.temp()))
    unknown = C.launcher("plan", "--set", str(made), "--root", "gamma", "--out", str(bench.temp()))
    housed = bench.temp() / "housed"
    with_packages = C.launcher("plan", "--set", str(C.witness_set(bench, packages=["plan"])), "--out", str(housed))
    carried = [json.loads(one.read_text(encoding="utf-8")).get("packages") for one in sorted(housed.glob("*.json"))] \
        if housed.is_dir() else []
    nowhere = C.launcher("plan", "--set", str(C.witness_set(bench, packages=["no-such-package"])), "--out", str(bench.temp()))
    if (with_packages.returncode == 0 and len(carried) == 6 and all(one == ["plan"] for one in carried)
            and nowhere.returncode == 2 and "manifest-invalid" in nowhere.stderr and "no-such-package" in nowhere.stderr
            and no_message.returncode == 2 and "manifest-invalid" in no_message.stderr and "message" in no_message.stderr
            and no_manifest.returncode == 2 and "manifest-missing" in no_manifest.stderr
            and unknown.returncode == 2 and "root-unknown" in unknown.stderr):
        held("(b) the manifest is judged by its name", "a root without message: manifest-invalid naming the key; "
             "no campaign.yaml: manifest-missing; a root the set lacks: root-unknown -- exit 2, nothing written; "
             "the set's `packages:` carried by every plan, a package the source lacks: manifest-invalid naming it")
    else:
        failures.append(f"  ✗ (b) the manifest            {no_message.returncode} {no_message.stderr[-120:]!r} "
                        f"{no_manifest.returncode} {unknown.returncode} {unknown.stderr[-100:]!r} "
                        f"packages={with_packages.returncode}/{carried} nowhere={nowhere.returncode} {nowhere.stderr[-100:]!r}")

    # --- (c) the set of the patterns, default of the launcher, its six roots opened --------------------------
    out = bench.temp() / "patterns"
    planned = C.launcher("plan", "--out", str(out))
    plans = [json.loads(one.read_text(encoding="utf-8")) for one in sorted(out.glob("*.json"))] if out.is_dir() else []
    env = bench.env("campaign-roots")
    shutil.copytree(C.SECTOR / "_skills" / "pp-cyclewit",
                    env.made / "skills" / "pp-cyclewit", dirs_exist_ok=True)
    (env.root / "LINES.txt").write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")

    def opened(root: str, door: str | None):
        extra = {"PP_DOCUMENTS": str(C.SET / root), **({"PP_DOOR": door} if door else {})}
        return cli(env.engine, "-new", cwd=env.root, env=extra)

    read = opened("read-lines", "READ_LINES.md")
    laps = opened("laps", "LAPS.md")
    cycle = opened("cycle", "CYCLE.md")
    route = opened("route", "ROUTE.md")
    route_key = KEY.search(route.stdout).group(1) if KEY.search(route.stdout) else ""
    picked = cli(env.engine, route_key, cwd=env.root) if route_key else None
    begin = opened("begin", None)
    review = opened("review", None)
    manifest = yaml.safe_load((C.SET / C.MANIFEST).read_text(encoding="utf-8"))
    situations = {root: opened(root, manifest["roots"][root].get("door")) for root in C.SITUATIONS}
    every = [read, laps, cycle, route, begin, review, *situations.values()]
    checks = {
        "read-lines": "▸ READ_LINES" in read.stdout and "WORK any => words" in read.stdout,
        "laps": "▸ LAPS" in laps.stdout and "INFER field => tool  (" in laps.stdout,
        "cycle": "▸ CYCLE" in cycle.stdout and "cyclewit-items" in cycle.stdout and "alpha" in cycle.stdout,
        "route": "▸ STAGE" in route.stdout and picked is not None and "PICK next" in picked.stdout
                 and "LEFT" in picked.stdout and "RIGHT" in picked.stdout,
        "begin": "▸ BEGIN" in begin.stdout and begin.stdout.find("▸ BEGIN") < begin.stdout.find("WORK"),
        "review": "WORK" in review.stdout and "REVIEW" in review.stdout,
        "long-read": "▸ LONG_READ" in situations["long-read"].stdout
                     and re.search(r"^\./pp [0-9a-f]{6}\s+\(", situations["long-read"].stdout, re.M) is not None,
        "two-steps": "▸ TWO_STEPS{1/2}" in situations["two-steps"].stdout,
        "bare-call": "▸ PROOF" in situations["bare-call"].stdout and "INFER" in situations["bare-call"].stdout,
        "stubborn": "▸ STUBBORN" in situations["stubborn"].stdout,
        "stray": "▸ STRAY" in situations["stray"].stdout and "WORK" in situations["stray"].stdout,
        "unoffered": "▸ HELLO" in situations["unoffered"].stdout,
        "mounted": "▸ HELLO" in situations["mounted"].stdout,
        "gesture-while-held": "REVIEW" in situations["gesture-while-held"].stdout,
        "space": "▸ HELLO" in situations["space"].stdout,     # ROOM is offered by the TURN below the door: the zone scenario proves it
        "compacted": "▸ HELLO" in situations["compacted"].stdout,
        "switched": "▸ HELLO" in situations["switched"].stdout,
        "bounded": "▸ BOUNDED{1/2}" in situations["bounded"].stdout,
        "bouncing": "▸ PROOF" in situations["bouncing"].stdout,
        "renewed": "▸ RENEWED{1/2}" in situations["renewed"].stdout,
    }
    expected = [one for one in plans if isinstance(one.get("expect"), dict) and "words" in one["expect"]]
    by_name = {one["name"]: one for one in plans}
    bounded_plan = by_name.get("bounded-relayed-strict") or {}
    renewed_plan = by_name.get("renewed-relayed-hybrid") or {}
    bounded_launches = (bounded_plan.get("command") or [])
    bounded_launches = bounded_launches[bounded_launches.index("--launches") + 1] if "--launches" in bounded_launches else None
    resume = renewed_plan.get("resume") or []
    odd_expect = C.launcher("plan", "--set", str(C.witness_set(bench, expect={"wordz": 1})), "--out", str(bench.temp()))
    if (planned.returncode == 0 and len(plans) == 60 and {one["root"] for one in plans} == set(C.ROOTS) | set(C.SITUATIONS)
            and all(one.returncode == 0 and "REFUSED" not in one.stderr for one in every) and all(checks.values())
            and len(expected) == 60 and odd_expect.returncode == 2 and "manifest-invalid" in odd_expect.stderr
            and "wordz" in odd_expect.stderr
            and bounded_plan.get("launches") == 1 and bounded_launches == "1" and bounded_plan.get("resume") is None
            and renewed_plan.get("renew") is True and "--run" in resume and "<key>" in resume
            and "--launches" in renewed_plan.get("command", []) and renewed_plan["command"][renewed_plan["command"].index("--launches") + 1] == "1"
            and all(one.get("resume") is None for one in plans if one["root"] != "renewed" or one["channel"] != C.RELAYED)):
        held("(c) the patterns are the default set", "60 plans for twenty roots, every one with its `expect`; twenty "
             "`-new` under PP_DOCUMENTS, no refusal: READ_LINES a WORK => words, LAPS its field, CYCLE its first "
             "element, ROUTE a PICK next between LEFT and RIGHT, BEGIN before the WORK, REVIEW offered; LONG_READ cut, "
             "TWO_STEPS, BOUNDED and RENEWED at their first step, PROOF (twice), STUBBORN, STRAY, HELLO (four times) opened; `wordz:` under expect: manifest-invalid; bounded's relayed plans carry `--launches 1`, "
             "renewed's a first wake-up at one launch and its `resume` by `--run <key>`")
    else:
        failures.append(f"  ✗ (c) the patterns            rc={planned.returncode} n={len(plans)} expected={len(expected)} "
                        f"opened={[one.returncode for one in every]} odd={odd_expect.returncode} "
                        f"bounded={bounded_plan.get('launches')}/{bounded_launches} renew={renewed_plan.get('renew')} "
                        f"resume={resume} {odd_expect.stderr[-120:]!r} {checks}")

    # --- (d) the binary of the provider, the report -----------------------------------------------------------
    bare_path = {**os.environ, "PATH": str(bench.temp() / "nowhere")}
    missing = C.launcher("play", "--provider", "claude", "--set", str(made), "--out", str(bench.temp()), env=bare_path)
    nobody = C.launcher("play", "--provider", "nobody-has-this-adapter", "--set", str(made), "--out", str(bench.temp()))
    report = C.launcher("report", "2026-10-27T0000", "--out", str(bench.temp()))
    if (missing.returncode == 2 and "provider-missing" in missing.stderr and "claude" in missing.stderr
            and nobody.returncode == 2 and "provider-unknown" in nobody.stderr
            and report.returncode == 2 and "campaign-missing" in report.stderr):
        held("(d) the binary is the adapter's", "`claude` absent from PATH: provider-missing naming the binary; "
             "a name no adapter carries: provider-unknown; `report` on no campaign: campaign-missing -- exit 2, "
             "nothing launched")
    else:
        failures.append(f"  ✗ (d) the binary              {missing.returncode} {missing.stderr[-160:]!r} "
                        f"{nobody.returncode} {nobody.stderr[-100:]!r} {report.returncode}")

    # --- (g) the dry plan of a real provider: repeated, with its effort, the binary never consulted -------------
    dry = bench.temp() / "real"
    real = C.launcher("plan", "--set", str(made), "--provider", "claude", "--model", "sonnet", "--effort", "low",
                      "--repeat", "3", "--out", str(dry), env=bare_path)
    plans = [json.loads(one.read_text(encoding="utf-8")) for one in sorted(dry.glob("*.json"))] if dry.is_dir() else []
    relayed = [one["command"] for one in plans if one["channel"] == C.RELAYED]
    zero = C.launcher("plan", "--set", str(made), "--repeat", "0", "--out", str(bench.temp()))
    odd = C.launcher("plan", "--set", str(made), "--effort", "enormous", "--out", str(bench.temp()))
    zero_launches = C.launcher("plan", "--set", str(C.witness_set(bench, launches=0)), "--out", str(bench.temp()))
    odd_renew = C.launcher("plan", "--set", str(C.witness_set(bench, renew="yes")), "--out", str(bench.temp()))
    if (real.returncode == 0 and len(plans) == 6
            and zero_launches.returncode == 2 and "manifest-invalid" in zero_launches.stderr and "launches" in zero_launches.stderr
            and odd_renew.returncode == 2 and "manifest-invalid" in odd_renew.stderr and "renew" in odd_renew.stderr
            and all(one.get("repeat") == 3 and one.get("effort") == "low" and one.get("launched") is False
                    and one.get("provider") == "claude" and one.get("model") == "sonnet" for one in plans)
            and all(command[command.index("--effort") + 1] == "low" and command[command.index("--model") + 1] == "sonnet"
                    for command in relayed)
            and zero.returncode == 2 and "repeat-invalid" in zero.stderr
            and odd.returncode == 2 and "policy-invalid" in odd.stderr and "effort" in odd.stderr):
        held("(g) the dry plan of a real provider", "6 plans under claude/sonnet/low x 3 on an empty PATH, nothing "
             "launched; `--repeat 0`: repeat-invalid; an unknown effort: policy-invalid naming the key; `launches: 0` "
             "and `renew: yes` at a root: manifest-invalid naming the key")
    else:
        failures.append(f"  ✗ (g) the dry plan            rc={real.returncode} n={len(plans)} "
                        f"{real.stderr[-200:]!r} {zero.returncode} {odd.returncode} {odd.stderr[-120:]!r} "
                        f"{zero_launches.returncode} {zero_launches.stderr[-100:]!r} {odd_renew.returncode}")
    return 0
