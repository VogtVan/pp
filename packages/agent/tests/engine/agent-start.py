"""Scenario `agent-start` -- 7 case(s) (batches l-agent-detache, 2026-09-30, and le-result-a-la-sortie;
split out of `agent-home` by les-scenarios-par-maison, 2026-10-07): the detached wake-up.
- `agent start` prints `{key, pid}` under a second and returns; the CHILD holds the wake lock
  after the parent is gone, `list` counts it running; `wait` prints the response as `run` does
  and `result` reads it again; the message line is written at the launch with `tag`, `pid` and
  an `at` no later than the response's, `messages` shows the tag
- a dead wake-up (the witness crashes at its first launch): `wait` says `wake-dead`, the wake log says
  `harness rc 1`, `status` says `dead (a wake-up ended without its response)`, `result` says `wake-dead`
- `--on-end` plays after the release and may reopen the very run: two responses, the marker,
  `on-end rc 0` in the wake log
- a refusal before the report is relayed (`run-busy` under a held wake lock, no report line,
  no record); `--json` refuses `flag-unsupported` under start
- `wait --timeout 1` under a held wake lock: `wait-timeout`; `result` says `wake-running`;
  released without a response: `status` dead, `result` wake-dead
"""
from __future__ import annotations

import json
import re
import shlex
import sys
import time

from conductor.state import lock
from tests.harness import holding, support

A = support(__file__, "agent")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    keys, counted, responses, messages = h.keys, h.counted, h.responses, h.messages
    launcher, report_of, alive = A.launcher, A.report_of, A.alive
    h.wake("first ask")                                   # one run parked, whose wake lock the cases hold
    key = keys()[0] if keys() else ""

    # --- agent start: {key, pid} under a second, the CHILD holds the wake lock ------------------------
    out_s = bench.temp() / "ps"
    t0 = time.monotonic()
    started = h.call("agent", "start", "agents/ag1", "--message", "started", "--tag", "t3", *h.harnessed_at("pause", out_s))
    took = time.monotonic() - t0
    report = report_of(started)
    skey, spid = str(report.get("key", "")), int(report.get("pid", 0) or 0)
    child_alive = spid > 0 and alive(spid)
    locked = len(skey) == 6 and lock.held(launcher(h.agent_meta, skey))
    roster = h.call("agent", "list")
    if (started.returncode == 0 and set(report) == {"key", "pid"} and took < 3.0 and child_alive and locked
            and roster.returncode == 0 and re.search(r"^agents/ag1 · \d+ run\(s\) · 1 running ·", roster.stdout, re.M)):
        held("agent start returns {key, pid} at once, the child holds the wake lock",
             f"{took:.2f}s; pid {spid} alive after the parent returned; {skey} held; list counts 1 running")
    else:
        failures.append(f"  ✗ agent start                 rc={started.returncode} took={took:.2f} report={report} "
                        f"alive={child_alive} locked={locked} {started.stderr[-200:]!r} {roster.stdout!r}")

    # --- wait renders the response as run does; result reads it again ---------------------------------
    waited_for = h.call("agent", "wait", "agents/ag1", skey)
    got = h.call("agent", "result", "agents/ag1", skey)
    if (waited_for.returncode == 0 and waited_for.stdout == "witness answer: pause\n"
            and f"pp-agent: agents/ag1 · run {skey} · exchange 1 · parked · harness rc 0" in waited_for.stderr
            and got.returncode == 0 and got.stdout == waited_for.stdout
            and not lock.held(launcher(h.agent_meta, skey))):
        held("wait renders the response as run does, result reads it again", "rc 0, stdout the response, the verdict on stderr")
    else:
        failures.append(f"  ✗ wait/result                 {waited_for.returncode}/{got.returncode} {waited_for.stdout!r} "
                        f"{waited_for.stderr[-200:]!r} {got.stderr[-120:]!r}")

    # --- the message is written at the launch, with its tag and pid ------------------------------------
    sent = [one for one in messages() if one.get("run") == skey]
    kept = [one for one in responses() if one.get("run") == skey]
    shown_tag = h.call("agent", "messages", "agents/ag1", "--last", "1")
    if (len(sent) == 1 and len(kept) == 1 and sent[0].get("tag") == "t3" and sent[0].get("pid") == spid
            and sent[0]["at"] <= kept[0]["at"] and sent[0]["message"] == "started"
            and shown_tag.returncode == 0 and "tag t3" in shown_tag.stdout):
        held("the message is written at the launch, with its tag and pid", f"tag t3, pid {spid}, at <= the response's; "
             "messages shows the tag")
    else:
        failures.append(f"  ✗ message at launch           sent={sent} kept={[one.get('at') for one in kept]} {shown_tag.stdout[-120:]!r}")

    # --- a dead wake-up: the harness crashed at its first launch ----------------------------------------
    dead = h.call("agent", "start", "agents/ag1", "--message", "will crash", *h.harnessed("crash"))
    dkey = str(report_of(dead).get("key", ""))
    gone = h.call("agent", "wait", "agents/ag1", dkey) if dkey else None
    wake_log = h.agent_meta / ".sys" / "state" / f"session-{dkey}.wake.log"
    res = h.call("agent", "result", "agents/ag1", dkey) if dkey else None
    dead_line = h.status_line(dkey) if dkey else ""
    if (dead.returncode == 0 and dkey and gone is not None and gone.returncode == 2 and "wake-dead" in gone.stderr
            and wake_log.is_file() and "harness rc 1" in wake_log.read_text(encoding="utf-8")
            and "dead (a wake-up ended without its response)" in dead_line
            and res is not None and res.returncode == 2 and "wake-dead" in res.stderr):
        held("a dead wake-up is seen", f"wait: wake-dead; the wake log says harness rc 1; status: {dead_line!r}; result: wake-dead")
    else:
        failures.append(f"  ✗ dead wake-up                rc={dead.returncode} key={dkey!r} wait={getattr(gone, 'returncode', None)} "
                        f"{getattr(gone, 'stderr', '')[-200:]!r} log={wake_log.is_file()} status={dead_line!r} "
                        f"result={getattr(res, 'stderr', '')[-120:]!r}")

    # --- --on-end plays after the release and may reopen the very run ------------------------------------
    marker = bench.temp() / "marker"
    out_o = bench.temp() / "po"
    on_end = (f"{shlex.quote(sys.executable)} {shlex.quote(str(h.engine))} --instance {shlex.quote(str(h.house))} agent run agents/ag1 "
              f"--run $PP_AGENT_RUN --message again {shlex.join(h.harnessed_at('play', out_o))} && touch {shlex.quote(str(marker))}")
    ended = h.call("agent", "start", "agents/ag1", "--message", "with on-end", "--on-end", on_end, *h.harnessed_at("play", out_o))
    okey = str(report_of(ended).get("key", ""))
    first_wait = h.call("agent", "wait", "agents/ag1", okey) if okey else None
    deadline = time.monotonic() + 40
    while time.monotonic() < deadline and not (marker.is_file() and len([one for one in responses() if one.get("run") == okey]) == 2):
        time.sleep(0.2)
    o_log = h.agent_meta / ".sys" / "state" / f"session-{okey}.wake.log"
    o_text = o_log.read_text(encoding="utf-8") if o_log.is_file() else ""
    if (ended.returncode == 0 and okey and first_wait is not None and first_wait.returncode == 0 and marker.is_file()
            and len([one for one in responses() if one.get("run") == okey]) == 2 and "on-end rc 0" in o_text):
        held("--on-end plays after the release and reopens the run", "the resume inside --on-end succeeded: two responses, "
             "the marker written, `on-end rc 0` in the wake log")
    else:
        failures.append(f"  ✗ on-end                      rc={ended.returncode} key={okey!r} first={getattr(first_wait, 'returncode', None)} "
                        f"marker={marker.is_file()} responses={len([one for one in responses() if one.get('run') == okey])} "
                        f"log={o_text[-300:]!r}")

    # --- a refusal before the report is relayed; --json and --dry-run refuse under start -----------------
    recorded = counted()
    with holding(launcher(h.agent_meta, key)):
        busy2 = h.call("agent", "start", "agents/ag1", "--run", key, "--message", "x", *h.harnessed("play"))
    flagged = h.call("agent", "start", "agents/ag1", "--message", "x", "--json", *h.harnessed("play"))
    if (busy2.returncode == 2 and "run-busy" in busy2.stderr and busy2.stdout == ""
            and flagged.returncode == 2 and "flag-unsupported" in flagged.stderr and counted() == recorded):
        held("a refusal before the report is relayed", "run-busy on stderr, no report line, no record; --json: flag-unsupported")
    else:
        failures.append(f"  ✗ start refusals              {busy2.returncode}/{flagged.returncode} {busy2.stdout!r} "
                        f"{busy2.stderr[-160:]!r} {flagged.stderr[-120:]!r}")

    # --- wait has a bound; result says running; then dead once the lock is free without a response --------
    launched = len([one for one in responses() if one.get("run") == key])
    launcher(h.agent_meta, key).write_text(json.dumps({"at": A.now_iso(), "message": "held by the bench",
                                                       "responses": launched}) + "\n", encoding="utf-8")
    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as handle:     # a launch the bench records
        handle.write(json.dumps({"at": A.now_iso(), "from": "house", "to": "agents/ag1", "run": key,
                                 "message": "held by the bench", "policy": {}}) + "\n")
    with holding(launcher(h.agent_meta, key)):
        t0 = time.monotonic()
        timed = h.call("agent", "wait", "agents/ag1", key, "--timeout", "1")
        took = time.monotonic() - t0
        running_result = h.call("agent", "result", "agents/ag1", key)
    after_result = h.call("agent", "result", "agents/ag1", key)
    key_line = h.status_line(key)
    if (timed.returncode == 2 and "wait-timeout" in timed.stderr and 0.9 <= took <= 4.0
            and running_result.returncode == 2 and "wake-running" in running_result.stderr
            and "dead (a wake-up ended without its response)" in key_line
            and after_result.returncode == 2 and "wake-dead" in after_result.stderr):
        held("wait has a bound, result says running, then dead", f"wait-timeout after {took:.2f}s; wake-running under "
             "the lock; released without a response: status dead, result wake-dead")
    else:
        failures.append(f"  ✗ wait bound                  {timed.returncode}/{running_result.returncode}/{after_result.returncode} "
                        f"took={took:.2f} {timed.stderr[-120:]!r} {running_result.stderr[-120:]!r} status={key_line!r}")
    return 0
