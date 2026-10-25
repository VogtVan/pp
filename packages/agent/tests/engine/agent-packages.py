"""Scenario `agent-packages` -- the packages a wake-up plays, switched by its caller and by the agent's SETTINGS,
on a house pinning `agent`, `steering` and `plan` (`plan` mounts `NEXT_MOVE` at `turn.end`, so a run parked at
its AWAIT holds it); the `package` command of a conversation is `agent-packages-chat`'s:
- the face: the last object of `agent status <path> --json` says the packages the agent pins beyond its base,
  `{name, on}`, as an opening's `ready` says them, every package on
- the wake-up: `--package <name>=on|off`, repeated, on `run` and `start`, played under the principal's mark
  before every launch -- on an opening, and on a resume from the exchange's first launch; its refusals
  (`package-unpinned` for a package the agent does not pin switched on, `package-base`, `package-invalid`) open
  nothing and leave the records as they were; switching off a package it does not pin asks nothing: never said,
  never played; a dry run says `package plan off` and opens nothing
- the SETTINGS switch: `package.plan: off` written to the agent's `SETTINGS.md` -- the face and a new
  conversation's `ready` say `plan` off, a run's every output says `plan off`; turned `on` while that run
  stands parked, the face and the run's next exchange say `plan on`: both read SETTINGS at every call
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

from conductor import instance, persistence, settings
from tests.harness import support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench, packages=("agent", "steering", "plan"))
    keys, counted = h.keys, h.counted

    def ready() -> dict:
        """-> the `ready` of a new conversation `agent chat agents/ag1 --json`, quit at once."""
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *h.harnessed_at("play", bench.temp() / "r")]
        played = subprocess.run(argv, input=json.dumps({"kind": "quit"}) + "\n", capture_output=True, text=True,
                                cwd=h.ws, env={**os.environ, **h.env}, timeout=120)
        flow = [json.loads(line) for line in played.stdout.splitlines() if line.strip().startswith("{")]
        return next((one for one in flow if one.get("kind") == "ready"), {})

    def face() -> dict:
        """-> the last object of `agent status agents/ag1 --json`."""
        played = h.call("agent", "status", "agents/ag1", "--json")
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {"rc": played.returncode, "err": played.stderr[-200:]}

    def switch(packages, name: str = "plan") -> object:
        return next((one.get("on") for one in packages or [] if one.get("name") == name), None)

    def switches(key: str) -> int:
        return len([one for one in h.trace(key) if one.get("kind") == "switch"]) if key else -1

    def off(key: str) -> list:
        return persistence.off_of(persistence.slot_of(h.agent_meta, key)) if key else ["?"]

    def fresh(known: set) -> str:
        return next((one for one in keys() if one not in known), "")

    def heading() -> str:
        """-> the packages line of the LAST prompt the witness received: `agent on · steering on · plan off`."""
        return next((line for line in h.read().splitlines() if line.startswith("▌ ") and " on" in line
                     and "plan" in line), "")

    # --- the face says what an opening says, every package on --------------------------------------------
    shown, opening = face(), ready()
    every_on = [{"name": "steering", "on": True}, {"name": "plan", "on": True}]
    if (set(shown) == {"agent", "providers", "last", "weight", "packages"}
            and sorted(shown.get("packages") or [], key=lambda one: one["name"])
            == sorted(every_on + [{"name": "agent", "on": True}], key=lambda one: one["name"])
            and shown.get("packages") == opening.get("packages")):
        held("the face says what an opening says", f"packages {shown['packages']} = ready's")
    else:
        failures.append(f"  ✗ the face                     face={shown} ready={opening.get('packages')}")

    # --- the wake-up: an opening plays the packages named -------------------------------------------------
    known = set(keys())
    opened = h.wake("un", "play", "--package", "plan=off")
    key_wa = fresh(known)
    if opened.returncode == 0 and key_wa and off(key_wa) == ["plan"] and switches(key_wa) == 1 \
            and "package plan off" in opened.stderr:
        held("(a) an opening plays the packages named", f"run {key_wa}: plan off, the switch traced once, stderr says "
             "`package plan off`")
    else:
        failures.append(f"  ✗ (a) opening                rc={opened.returncode} key={key_wa!r} off={off(key_wa)} "
                        f"switches={switches(key_wa)} {opened.stderr[-300:]!r}")

    # --- a resume, the package held by the parked turn --------------------------------------------------
    known = set(keys())
    parked = h.wake("un")
    key_wb = fresh(known)
    resumed = h.call("agent", "run", "agents/ag1", "--run", key_wb, "--message", "deux", "--package", "plan=off",
                     *h.harnessed("play"))
    back = h.call("agent", "run", "agents/ag1", "--run", key_wa, "--message", "deux", "--package", "plan=on",
                  *h.harnessed("play"))
    if parked.returncode == 0 and resumed.returncode == 0 and off(key_wb) == ["plan"] \
            and switches(key_wb) == 1 and back.returncode == 0 and off(key_wa) == [] and switches(key_wa) == 2:
        held("(b) a resume plays them too", f"run {key_wb} parked with plan held, resumed with plan=off: off from its "
             f"exchange; run {key_wa} resumed with plan=on: on again")
    else:
        failures.append(f"  ✗ (b) resume                 rc={parked.returncode}/{resumed.returncode}/{back.returncode} "
                        f"off_b={off(key_wb)} off_a={off(key_wa)} switches={switches(key_wb)}/{switches(key_wa)} "
                        f"{resumed.stderr[-300:]!r}")

    # --- refusals leave nothing --------------------------------------------------------------------------
    before_keys, before_counts = sorted(keys()), counted()
    base = instance.base_of(h.agent_meta)
    refusals = {code: h.wake("never", "play", "--package", value)
                for code, value in (("package-unpinned", "nowhere=on"), ("package-base", f"{base}=off"),
                                    ("package-invalid", "plan=maybe"))}
    if (all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and sorted(keys()) == before_keys and counted() == before_counts):
        held("(c) refusals leave nothing", "package-unpinned, package-base, package-invalid before anything: no run "
             "opened, the records as they were -- KPL32")
    else:
        failures.append("  ✗ (c) refusals               " + " ".join(f"{code}={one.returncode}:{one.stderr[-120:]!r}"
                                                                  for code, one in refusals.items())
                        + f" keys={sorted(set(keys()) - set(before_keys))} counts={before_counts}/{counted()}")

    # --- start and --dry-run -------------------------------------------------------------------------------
    before_keys, before_counts = sorted(keys()), counted()
    dry = h.wake("never", "play", "--package", "plan=off", "--package", "nowhere=off", "--dry-run")
    unopened = sorted(keys()) == before_keys and counted() == before_counts
    started = h.call("agent", "start", "agents/ag1", "--message", "trois", "--package", "plan=off",
                     "--package", "nowhere=off", *h.harnessed("play"))
    key_d = A.report_of(started).get("key", "")
    waited = h.call("agent", "wait", "agents/ag1", key_d, "--timeout", "60") if key_d else None
    if (dry.returncode == 0 and "  package plan off" in dry.stdout.splitlines() and "nowhere" not in dry.stdout and unopened
            and started.returncode == 0 and key_d and waited is not None and waited.returncode == 0
            and off(key_d) == ["plan"] and switches(key_d) == 1):
        held("(d) start and --dry-run", f"the dry run says `package plan off` and nothing of nowhere=off, opens nothing; "
             f"start's run {key_d} plays plan off, one switch: nowhere=off never reaches the engine -- KPL34")
    else:
        failures.append(f"  ✗ (d) start, dry run         rc={dry.returncode}/{started.returncode}/"
                        f"{waited.returncode if waited else None} unopened={unopened} key={key_d!r} off={off(key_d)} "
                        f"{dry.stdout[-200:]!r} {started.stderr[-200:]!r}")

    # --- the SETTINGS switch: the operator's edit, seen by the face and by a new conversation ------------------
    agent_settings = h.agent_meta / "SETTINGS.md"
    text = agent_settings.read_text(encoding="utf-8")
    edited = re.sub(r"^package\.plan: on$", "package.plan: off", text, count=1, flags=re.M)
    agent_settings.write_text(edited, encoding="utf-8")
    shown, opening = face(), ready()
    if edited != text and switch(shown.get("packages")) is False and shown.get("packages") == opening.get("packages"):
        held("a switch of SETTINGS", f"plan off at the face and at a new conversation's ready: {shown['packages']}")
    else:
        failures.append(f"  ✗ a switch                     edited={edited != text} face={shown.get('packages')} "
                        f"ready={opening.get('packages')}")

    # --- off at SETTINGS before a run's first wake-up: the run and the face agree ----------------------------
    settings.write(h.agent_meta, "package.plan", "off")
    known = set(keys())
    woke = h.wake("un")
    key = fresh(known)
    said_off, shown_off = heading(), face()
    if woke.returncode == 0 and key and switch(shown_off.get("packages")) is False and "plan off" in said_off:
        held("(a) off at SETTINGS: the run and the status agree", f"run {key}: its output says `{said_off[2:]}`; "
             "status --json says plan off")
    else:
        failures.append(f"  ✗ (a) off                    rc={woke.returncode} key={key!r} status={shown_off} "
                        f"said={said_off!r}")

    # --- on again while that run stands parked: its next exchange plays it ------------------------------------
    settings.write(h.agent_meta, "package.plan", "on")
    shown_on = face()
    again = h.call("agent", "run", "agents/ag1", "--run", key, "--message", "deux", *h.harnessed("play"))
    said_on = heading()
    if switch(shown_on.get("packages")) is True and again.returncode == 0 and "plan on" in said_on:
        held("(b) on again: the same run plays it", f"status --json says plan on; the next exchange of {key} "
             f"says `{said_on[2:]}` -- SETTINGS read at every call, by the run and by the status alike")
    else:
        failures.append(f"  ✗ (b) on again               status={shown_on} rc={again.returncode} said={said_on!r} "
                        f"{again.stderr[-200:]!r}")
    return 0
