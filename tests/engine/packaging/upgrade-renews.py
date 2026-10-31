"""Scenario `upgrade-renews` -- 9 case(s) (batch la-cle-gardee-par-l-upgrade, 2026-10-04): an upgrade
RENEWS the runs it finds -- the slot becomes a renewal mark at the same path, the key stays held --
and the next call on the key reopens the run under it.
- (r1) at the frontier: the message handed after the upgrade reopens the run on its boot, under its
  key; ONE trace says `renewed`, `reopened`, then the message (`prompt`); `-stats <key>` counts one run;
  under `PP_MARBLE` the reopened output carries no standing orders, its mass said (plan fixes2, s.741)
- (r2) off the frontier: a production piped on a renewed key plays nothing -- the boot, a line saying
  it was not played, no `answer` and no `prompt` traced after the reopening
- (r3) the look: `-peek` and the keyless inspection say the renewal, the mark byte-identical after
- (r4) what the reopening keeps: the exchanges completed (`turns`), the boot set there
  (`context.is_boot()`), and a package the run switched off stays off
- (r5) a borrower: the run of an instance that borrows the machine is renewed by the machine's
  upgrade and reopened under its key
- (r6) a mark holds no claim: a cadence period claimed by a renewed run is free for another run
- (r7) `-reset` forgets a mark for good: the key answers `run-unknown`
- (r8) two upgrades: a mark crosses a second upgrade -- `to` follows, `at` is kept -- and reopens
- (r9) the slot's other readers on a mark: a launcher's key on it refuses `new-key-taken`, the trace
  follower finds its trace, the facade's peek sees no stack and its advance refuses `no-run`;
  `-hook` (the resume) on an instance holding one mark reopens that run
"""
from __future__ import annotations

import json
import os
import re

from conductor import Conductor, Refusal, cadences, discovery, instance, persistence
from conductor import install
from conductor.state import context, log
from tests.harness import INSTANCE, cli, member_of, pin_step


def _bumped(manifest) -> str:
    """The package's version at the source copy, raised by one on its last number -> the new version."""
    text = manifest.read_text(encoding="utf-8")
    found = re.search(r"^version: (\S+)$", text, re.M)
    assert found, text[:200]
    head, last = found.group(1).rsplit(".", 1)
    new = f"{head}.{int(last) + 1}"
    manifest.write_text(text.replace(f"version: {found.group(1)}", f"version: {new}", 1), encoding="utf-8")
    return new


def _events(meta, key: str) -> list[dict]:
    """-> the events of the run `key`'s traces at `meta`, every file of that key in order."""
    found = []
    for trace in sorted((meta / persistence.DIRECTORY).glob(f"session-*Z-{key}.jsonl")):
        found += [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()]
    return found


def _traces(meta, key: str) -> int:
    return len(list((meta / persistence.DIRECTORY).glob(f"session-*Z-{key}.jsonl")))


def _mark(meta, key: str) -> dict:
    """-> the renewal mark the slot of `key` holds, {} when the slot is gone or is a run."""
    slot = persistence.slot_of(meta, key)
    if not slot.is_file():
        return {}
    data = json.loads(slot.read_text(encoding="utf-8") or "{}")
    return data.get("renewed") or {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    engine = bench.source_with("kit-witness")          # a copy of the product: its versions may move
    source = engine.parent.parent
    kit = source / "bases" / "kit" / "package.yaml"
    ws = bench.temp() / "ws"
    made = install.install(engine, ws / INSTANCE, ["wit"])
    pin_step(made)             # one step per output, a wide cap: the boot lands whole, step by step
    member_of(made)            # the boot opens on the member's INFER: the turn's WORK is one call away
    console = instance.engine_root(made) / "pp.py"
    born = cli(console, "-install", "agents/a", cwd=ws)
    agent = ws / "agents" / "a" / INSTANCE
    if born.returncode:
        failures.append(f"  ✗ the borrower              {born.stderr.strip()[-300:]}")
        return len(failures)

    def call(*args: str, at=None, stdin: str | None = None, env: dict | None = None):
        where = ("--instance", str(at)) if at is not None else ()
        return cli(console, *where, *args, cwd=ws, stdin=stdin, env=env)

    def opened(at=None) -> str:
        """-> the key of a run opened by `-new` at `at` (the house by default), its first
        output read whole -- the bare calls a cut output asks for serve its chunks."""
        meta = at or made
        before = {persistence.run_id_of(one) for one in persistence.slots(meta)}
        out = call("-new", "the first message", at=at).stdout
        key = ({persistence.run_id_of(one) for one in persistence.slots(meta)} - before).pop()
        while "a reading continues" in out.rsplit("▶", 1)[-1]:
            out = call(key, at=at).stdout
        return key

    def to_frontier(key: str, at=None) -> str:
        """Bare calls until the output closes on an AWAIT -> that output."""
        out = ""
        for _ in range(8):
            out = call(key, at=at).stdout
            if "▶ AWAIT" in out:
                break
        return out

    # --- the runs, prepared before ONE upgrade ------------------------------------------------------
    k1 = opened()
    to_frontier(k1)
    k2 = opened()
    mid = call(k2).stdout                      # the member's INFER closed: the turn's WORK stands
    k4 = opened()
    to_frontier(k4)
    call(k4, "the second message")
    to_frontier(k4)
    call(k4, "-disable", "wit")
    turns4 = persistence.turns_of(persistence.slot_of(made, k4))
    k5 = opened(agent)
    to_frontier(k5, agent)
    k6 = opened()
    to_frontier(k6)
    period = "2026-W40"
    cadences.claim(made, "bench-sighting", period, k6, lambda run: True)
    k7 = opened()
    to_frontier(k7)
    k8 = opened()
    to_frontier(k8)
    first = _bumped(kit)
    upgraded = call("upgrade")
    if upgraded.returncode:
        failures.append(f"  ✗ the first upgrade         {upgraded.stderr.strip()[-300:]}")
        return len(failures)
    mark8 = _mark(made, k8)

    # --- (r3) the look: -peek and the keyless inspection say the renewal, nothing written ------------
    slot5 = persistence.slot_of(agent, k5)
    frozen = slot5.read_bytes() if slot5.is_file() else b""
    peeked = call(k5, "-peek", at=agent)
    looked = call(at=agent)
    if (frozen and peeked.returncode == 0 and looked.returncode == 0
            and "renewed by an upgrade" in peeked.stdout and "renewed by an upgrade" in looked.stdout
            and slot5.read_bytes() == frozen):
        held("(r3) the look says the renewal", f"`-peek` and `./pp` at the borrower name run {k5} renewed; "
             "its mark the same to the byte after both")
    else:
        failures.append(f"  ✗ (r3) the look               rc={peeked.returncode}/{looked.returncode} "
                        f"{peeked.stdout[-200:]!r} {peeked.stderr.strip()[-200:]!r} {looked.stdout[-200:]!r}")

    # --- (r1) at the frontier: the message reopens the run under its key ------------------------------
    reopened = call(k1, "the message after the upgrade", env={"PP_MARBLE": "1"})   # the harness carries the orders
    kinds1 = [one.get("kind") for one in _events(made, k1)]
    tail1 = kinds1[kinds1.index("renewed"):] if "renewed" in kinds1 else []
    prompts1 = [one.get("text") for one in _events(made, k1) if one.get("kind") == "prompt"]
    stats1 = call("-stats", k1, "-json")
    counted = json.loads(stats1.stdout).get("runs", []) if stats1.returncode == 0 else []
    if (reopened.returncode == 0 and f"run {k1}" in reopened.stdout and "▸ MEMBER" in reopened.stdout
            and "standing orders" not in reopened.stdout
            and tail1[:3] == ["renewed", "reopened", "prompt"]
            and prompts1[-1:] == ["the message after the upgrade"]
            and _traces(made, k1) == 1 and len(counted) == 1 and counted[0].get("key") == k1):
        held("(r1) the frontier: reopened under its key", f"run {k1} answers its boot; one trace: "
             "renewed, reopened, prompt (the message); -stats counts one run; under PP_MARBLE the "
             f"reopened output carries no standing orders -- {len(reopened.stdout)} c (plan fixes2, s.741)")
    else:
        failures.append(f"  ✗ (r1) the frontier           rc={reopened.returncode} {reopened.stderr.strip()[-200:]!r} "
                        f"tail={tail1[:4]} traces={_traces(made, k1)} runs={len(counted)}")

    # --- (r2) off the frontier: a production plays nothing, and the block says so -------------------
    piped = call(k2, "-", stdin="a production for the old documents")
    whole = piped.stdout                       # the output read whole: its chunks, by bare calls
    for _ in range(8):
        if piped.returncode or "a reading continues" not in whole.rsplit("▶", 1)[-1]:
            break
        whole += call(k2).stdout
    kinds2 = [one.get("kind") for one in _events(made, k2)]
    after2 = kinds2[kinds2.index("reopened"):] if "reopened" in kinds2 else []
    if (piped.returncode == 0 and "WORK any" in mid and "▸ MEMBER" in whole
            and "not played" in whole and after2 and "answer" not in after2 and "prompt" not in after2):
        held("(r2) off the frontier: nothing played", f"run {k2} reopened on its boot; the piped production "
             "said not played; no answer, no prompt traced after `reopened`")
    else:
        failures.append(f"  ✗ (r2) off the frontier       rc={piped.returncode} {piped.stderr.strip()[-200:]!r} "
                        f"after={after2[:5]} said={'not played' in whole}")

    # --- (r4) what the reopening keeps: turns, the boot there, the run's switch -----------------------
    kept = call(k4, "the message after the upgrade")
    slot4 = persistence.slot_of(made, k4)
    spot = os.environ.get(context.VARIABLE)
    os.environ[context.VARIABLE] = k4
    try:
        now4 = context.current(made) if slot4.is_file() else None
    except Exception:
        now4 = None
    finally:
        if spot is None:
            os.environ.pop(context.VARIABLE, None)
        else:
            os.environ[context.VARIABLE] = spot
    if (kept.returncode == 0 and turns4 >= 1 and now4 is not None and now4.turns == turns4
            and now4.exchange() == turns4 + 1 and now4.is_boot()
            and "wit off" in kept.stdout and "wit" in persistence.off_of(slot4)):
        held("(r4) the reopening keeps turns and the switch", f"run {k4}: {turns4} exchange(s) kept, the "
             f"reopened one is #{turns4 + 1} and a boot; wit still off")
    else:
        failures.append(f"  ✗ (r4) what is kept           rc={kept.returncode} {kept.stderr.strip()[-200:]!r} "
                        f"turns={turns4} now={now4} off={'wit off' in kept.stdout}")

    # --- (r5) a borrower: renewed by the machine's upgrade, reopened under its key --------------------
    borrowed = call(k5, "the message after the upgrade", at=agent)
    kinds5 = [one.get("kind") for one in _events(agent, k5)]
    if (borrowed.returncode == 0 and f"run {k5}" in borrowed.stdout
            and "renewed" in kinds5 and "reopened" in kinds5 and _traces(agent, k5) == 1):
        held("(r5) a borrower's run renewed and reopened", f"agents/a's run {k5}: the house's upgrade "
             "renewed it, its next call reopened it in the same trace")
    else:
        failures.append(f"  ✗ (r5) the borrower           rc={borrowed.returncode} {borrowed.stderr.strip()[-200:]!r} "
                        f"kinds={kinds5[-4:]}")

    # --- (r6) a mark holds no claim ----------------------------------------------------------------
    judge = Conductor(discovery.instance_member(console), console)
    alive6 = judge._claimant_alive(k6)
    taken = cadences.claim(made, "bench-sighting", period, "abcdef", judge._claimant_alive)
    if not alive6 and taken:
        held("(r6) a mark holds no claim", f"run {k6} renewed, never reopened: its claim on {period} is void, "
             "another run takes the period")
    else:
        failures.append(f"  ✗ (r6) the claim              alive={alive6} taken={taken} mark={_mark(made, k6)}")

    # --- (r7) -reset forgets a mark for good ---------------------------------------------------------
    reset = call("-reset", k7)
    after7 = call(k7, "anyone there?")
    if reset.returncode == 0 and after7.returncode == 2 and "run-unknown" in after7.stderr:
        held("(r7) -reset forgets a mark", f"run {k7} renewed then forgotten: its key answers run-unknown")
    else:
        failures.append(f"  ✗ (r7) -reset                 rc={reset.returncode}/{after7.returncode} "
                        f"{after7.stderr.strip()[-200:]!r}")

    # --- (r8) two upgrades: the mark crosses the second, then reopens ----------------------------------
    second = _bumped(kit)
    again = call("upgrade")
    mark8b = _mark(made, k8)
    back = call(k8, "the message after two upgrades")
    if (again.returncode == 0 and mark8 and mark8b
            and mark8b.get("at") == mark8.get("at")
            and (mark8.get("to") or {}).get("kit") == first and (mark8b.get("to") or {}).get("kit") == second
            and back.returncode == 0 and f"run {k8}" in back.stdout and _traces(made, k8) == 1):
        held("(r8) a mark crosses a second upgrade", f"run {k8}: `at` kept, `to` kit {first} -> {second}; "
             "reopened in its one trace")
    else:
        failures.append(f"  ✗ (r8) two upgrades           rc={again.returncode}/{back.returncode} "
                        f"{mark8} {mark8b} {back.stderr.strip()[-200:]!r}")

    # --- (r9) the slot's other readers, each met on a mark ---------------------------------------------
    marked = persistence.slot_of(made, k6)
    frozen6 = marked.read_bytes() if marked.is_file() else b""
    followed = log.follow(made, k6).path
    facade = Conductor(discovery.instance_member(console), console, k6)
    viewed = facade.peek()
    try:
        facade.submit("an answer to nothing")
        refused = ""
    except Refusal as caught:
        refused = caught.code
    hooked = call("-hook", at=agent)             # agents/a holds one run: k5, renewed again by the second upgrade
    reopenings = [one for one in _events(agent, k5) if one.get("kind") == "reopened"]
    if (frozen6 and hooked.returncode == 0 and k5 in hooked.stdout and len(reopenings) == 2
            and followed is not None and followed.name == persistence.trace_of(marked)
            and viewed is None and refused == "no-run" and marked.read_bytes() == frozen6):
        held("(r9) every other reader meets a mark", f"run {k6}'s mark: "
             "the trace follower finds its trace, the facade's peek sees no stack and its submit refuses "
             f"no-run; the mark the same to the byte; `-hook` at agents/a reopens {k5}")
    else:
        failures.append(f"  ✗ (r9) the other readers      "
                        f"followed={followed} viewed={viewed} refused={refused!r} hook={hooked.returncode} "
                        f"reopenings={len(reopenings)} {hooked.stderr.strip()[-200:]!r}")
    return len(failures)
