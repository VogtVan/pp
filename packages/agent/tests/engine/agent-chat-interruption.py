"""Scenario `agent-chat-interruption` -- an exchange the principal interrupts or does not conduct, said to the LLM:
- pp on, in the conversation: `stop` during the `pause` witness, then `go on` -- the first prompt of the next
  wake-up opens on `INTERRUPTED`, then `HEAD`, the message, then pp's output; `opened.interrupted` on that exchange
  alone; the message after it carries no such head, nor does any `conduction`
- pp off, the run taken up by `chat --run <key>`: under `conduct off`, the prompt after the `stop` is
  `PARENTHESIS`, `INTERRUPTED`, `HEAD` and the message, nothing of pp
- from one process to another: a conversation interrupted then closed leaves `interrupted: true` in the MARK of its
  wake lock; `run --run <key>` opens on the head, its verdict says `after an interruption`, the mark is cleared,
  the next wake-up has neither
- no record gains a field: `responses.jsonl`, `messages.jsonl`, `sessions.jsonl`
- the take marks the wake lock before any message: `held: "chat"`, the hour of the take, the head of the run's
  last message, no `responses`; a neighbour's `run --dry-run` reads `since HH:MM « <head> »`, also when the lock
  file was gone before the take; a mark carrying `interrupted: true` keeps it through the take and the first
  message opens on `INTERRUPTED`; a conversation resumed then closed without a message leaves its run `parked`
- `conduct off` in a fresh conversation: the bare prompt opens on `PARENTHESIS`, `HEAD`, the message; no prompt of
  the conducted exchanges carries `PARENTHESIS`
- `stop` during an exchange of a lawful house: the harness dies, the lock stays held, the verdict says
  `interrupted` with nothing kept, the conversation waits; the next message takes the standing run up
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from conductor.state import lock
from tests.harness import support

A = support(__file__, "agent")
SKILL = A.skill()
HEAD = SKILL.HEAD
INTERRUPTED = SKILL.INTERRUPTED
PARENTHESIS = SKILL.PARENTHESIS
HOLD = 10.0
SENT_FIELDS = {"at", "from", "to", "run", "message", "policy", "conducted"}
SESSION_FIELDS = {"at", "agent", "run", "provider", "session"}


def talk(h, mode: str, where: Path, *flags: str) -> subprocess.Popen:
    """`agent chat agents/ag1 --json` under the witness in `mode`, left running."""
    argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
            "--json", *flags, *h.harnessed_at(mode, where)]
    return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, cwd=h.ws, env={**os.environ, **h.env})


def command(kind: str, **fields) -> str:
    return json.dumps({"kind": kind, **fields}) + "\n"


def events_of(out: str) -> list[dict]:
    found = []
    for line in out.splitlines():
        if not line.strip():
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            found.append({"kind": "UNREADABLE", "line": line})
    return found


def until_kind(live, kind: str) -> list[dict]:
    """-> the events read on `live` up to the first of `kind` (or the end of its stdout)."""
    seen = []
    while True:
        line = live.stdout.readline()
        if not line:
            return seen
        seen.append(json.loads(line))
        if seen[-1].get("kind") == kind:
            return seen


def until(condition, bound: float = HOLD) -> bool:
    opened = time.monotonic()
    while time.monotonic() - opened < bound:
        if condition():
            return True
        time.sleep(0.05)
    return condition()


def prompts(where: Path) -> dict[str, str]:
    """-> {`<session>.<launch>`: prompt} the witness received at `where`."""
    return {one.name.split(".prompt.", 1)[1]: one.read_text(encoding="utf-8")
            for one in sorted(where.parent.glob(where.name + ".prompt.*"))}


def first_with(where: Path, text: str) -> str:
    """-> the prompt the witness received that carries the message `text` under its head."""
    return next((one for one in prompts(where).values() if f"{HEAD}\n{text}" in one), "")


def mark_of(h, key: str) -> dict:
    """-> the mark the wake lock of `key` carries, {} when it carries none."""
    try:
        read = json.loads(A.launcher(h.agent_meta, key).read_text(encoding="utf-8"))
        return read if isinstance(read, dict) else {}
    except (OSError, ValueError):
        return {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # === a plain house: the interruption said, conducted or not, in a process or the next ===============
    h = A.House(bench)

    def stopped(live, where: Path, text: str) -> list[dict]:
        """`text` sent, then `stop` once the witness sleeps in its pause: the events up to the verdict."""
        live.stdin.write(command("message", text=text))
        live.stdin.flush()
        until(lambda: bool(h.read(".pid", where)))
        live.stdin.write(command("stop"))
        live.stdin.flush()
        return until_kind(live, "verdict")

    # --- pp on, in the conversation: the head once, before the message's, then pp's output -----------
    known = set(h.keys())
    out_a = bench.temp() / "ia"
    live = talk(h, "pause", out_a)
    first = stopped(live, out_a, "think")
    key_a = next((one for one in h.keys() if one not in known), "")
    live.stdin.write(command("message", text="go on") + command("message", text="again") + command("quit"))
    out, err = live.communicate(timeout=120)
    flow = first + events_of(out)
    openings = [one for one in flow if one.get("kind") == "opened"]
    verdicts = [one.get("state") for one in flow if one.get("kind") == "verdict"]
    resumed = first_with(out_a, "go on")
    after = first_with(out_a, "again")
    conductions = [str(one.get("text", "")) for one in flow if one.get("kind") == "conduction"]
    if (live.returncode == 0 and err == "" and key_a and verdicts == ["interrupted", "parked", "parked"]
            and resumed.startswith(f"{INTERRUPTED}\n{HEAD}\ngo on\n\n▌ pp · run {key_a}")
            and after.startswith(f"{HEAD}\nagain\n") and INTERRUPTED not in after
            and INTERRUPTED not in first_with(out_a, "think")
            and [one.get("interrupted") for one in openings] == [None, True, None]
            and conductions and not any(INTERRUPTED in one for one in conductions)):
        held("pp on: the interruption said once", f"run {key_a}: `go on` opens on {INTERRUPTED} then the message's "
             "head, the message and pp's output; opened.interrupted on that exchange alone; `again` and every "
             f"conduction without it ({len(conductions)} conductions)")
    else:
        failures.append(f"  ✗ pp on                       rc={live.returncode} err={err[-200:]!r} verdicts={verdicts} "
                        f"opened={[one.get('interrupted') for one in openings]} resumed={resumed[:160]!r} "
                        f"after={after[:80]!r} prompts={list(prompts(out_a))}")

    # --- pp off, the run taken up by another conversation: the two heads and the message alone ------
    known = set(h.keys())
    made = h.wake("first", "play")
    key_b = next((one for one in h.keys() if one not in known), "")
    out_b = bench.temp() / "ib"
    live = talk(h, "pause", out_b, "--run", key_b)
    live.stdin.write(command("conduct", on=False))
    live.stdin.flush()
    first = stopped(live, out_b, "think")
    live.stdin.write(command("message", text="go on") + command("quit"))
    out, err = live.communicate(timeout=120)
    flow = first + events_of(out)
    verdicts = [one.get("state") for one in flow if one.get("kind") == "verdict"]
    openings = [one for one in flow if one.get("kind") == "opened"]
    bare = first_with(out_b, "go on")
    if (made.returncode == 0 and live.returncode == 0 and key_b and verdicts == ["interrupted", "unconducted"]
            and bare == f"{PARENTHESIS}\n{INTERRUPTED}\n{HEAD}\ngo on" and "▌ pp" not in bare
            and [one.get("interrupted") for one in openings] == [None, True]):
        held("pp off: the parenthesis, the two heads and the message", f"run {key_b}: under conduct off the prompt "
             f"after the stop is {bare!r}, nothing of pp; opened.interrupted")
    else:
        failures.append(f"  ✗ pp off                      rc={made.returncode}/{live.returncode} err={err[-200:]!r} "
                        f"verdicts={verdicts} bare={bare!r} opened={[one.get('interrupted') for one in openings]}")

    # --- from one process to another: the mark keeps it, run --run says it, then it is gone ---------
    out_c = bench.temp() / "ic"
    live = talk(h, "pause", out_c, "--run", key_b)
    first = stopped(live, out_c, "think")
    live.stdin.write(command("quit"))
    live.communicate(timeout=120)
    kept_mark = mark_of(h, key_b)
    out_d = bench.temp() / "id"
    taken = h.call("agent", "run", "agents/ag1", "--run", key_b, "--message", "go on", *h.harnessed_at("play", out_d))
    cleared = mark_of(h, key_b)
    again = h.call("agent", "run", "agents/ag1", "--run", key_b, "--message", "again", *h.harnessed_at("play", out_d))
    taken_up = first_with(out_d, "go on")
    if ([one.get("state") for one in first if one.get("kind") == "verdict"] == ["interrupted"]
            and kept_mark.get("interrupted") is True and "interrupted" not in cleared
            and taken.returncode == 0 and "· after an interruption" in taken.stderr
            and taken_up.startswith(f"{INTERRUPTED}\n{HEAD}\ngo on\n\n▌ pp · run {key_b}")
            and again.returncode == 0 and "after an interruption" not in again.stderr
            and first_with(out_d, "again").startswith(f"{HEAD}\nagain")):
        held("from one process to another, through the mark", f"run {key_b}: the closed conversation left the mark "
             f"{sorted(kept_mark)}; run --run opened on the head, its verdict `after an interruption`, the mark "
             "cleared; the next run --run without either")
    else:
        failures.append(f"  ✗ across processes            mark={kept_mark} cleared={cleared} rc={taken.returncode}/"
                        f"{again.returncode} taken={taken.stderr[-200:]!r} prompt={taken_up[:120]!r}")

    # --- no record gains a field --------------------------------------------------------------------
    answered = {field for one in h.responses() for field in one}
    sent = {field for one in h.messages() for field in one}
    opened_sessions = {field for one in h.sessions() for field in one}
    if answered <= A.RECORD_FIELDS | {"conducted"} and sent <= SENT_FIELDS and opened_sessions <= SESSION_FIELDS:
        held("no record gains a field", f"responses {sorted(answered)}; messages {sorted(sent)}; "
             f"sessions {sorted(opened_sessions)}")
    else:
        failures.append(f"  ✗ records                     responses={sorted(answered)} messages={sorted(sent)} "
                        f"sessions={sorted(opened_sessions)}")

    # === a house of one run, woken once: the mark its wake lock carries ==================================
    m = A.House(bench)
    m.wake("first message of A", "play")
    key = m.keys()[0] if m.keys() else ""
    lock_file = A.launcher(m.agent_meta, key)

    def taken_at(where: Path) -> subprocess.Popen:
        """`chat --run <key> --json` launched and read up to its first `waiting`: the lock is taken."""
        live = talk(m, "play", where, "--run", key)
        until_kind(live, "waiting")
        return live

    def closed(live, *commands: dict) -> None:
        live.communicate("".join(json.dumps(one) + "\n" for one in (*commands, {"kind": "quit"})), timeout=120)

    def neighbours() -> str:
        dry = m.wake("probe", "play", "--dry-run")
        return next((one for one in dry.stdout.splitlines() if one.startswith("[runs under way")), "")

    def line_of(seen: dict) -> str:
        local = datetime.fromisoformat(str(seen.get("at"))).astimezone().strftime("%H:%M") if seen.get("at") else "?"
        return f"[runs under way: {key} since {local} « first message of A »]"

    # --- after a wake-up: the take writes its own mark -----------------------------------------------
    before = mark_of(m, key)
    time.sleep(1.1)                                   # the hour of the take, one second at least after the wake-up's
    live = taken_at(bench.temp() / "m1")
    seen, read = mark_of(m, key), neighbours()
    closed(live)
    if (key and seen.get("held") == "chat" and "responses" not in seen and seen.get("message") == "first message of A"
            and str(seen.get("at")) > str(before.get("at")) and read == line_of(seen)):
        held("the take marks the lock", f"run {key}: {seen}; the neighbour reads {read!r}")
    else:
        failures.append(f"  ✗ take                        before={before} seen={seen} read={read!r}")

    # --- the lock file gone before the take: still a mark, never `?` ----------------------------------
    lock_file.unlink(missing_ok=True)
    live = taken_at(bench.temp() / "m2")
    seen, read = mark_of(m, key), neighbours()
    closed(live)
    if seen.get("held") == "chat" and read == line_of(seen) and "since ?" not in read:
        held("a lock file gone is marked at the take", f"{read!r}")
    else:
        failures.append(f"  ✗ gone                        seen={seen} read={read!r}")

    # --- an interruption kept through the take ------------------------------------------------------
    lock_file.write_text(json.dumps({"at": A.now_iso(), "message": "think", "responses": len(m.responses()),
                                     "interrupted": True}) + "\n", encoding="utf-8")   # the mark a `stop` leaves
    where = bench.temp() / "m3"
    live = taken_at(where)
    seen = mark_of(m, key)
    closed(live, {"kind": "message", "text": "go on"})
    prompt = next(iter(prompts(where).values()), "")
    if seen.get("interrupted") is True and "responses" not in seen and prompt.startswith(f"{INTERRUPTED}\n{HEAD}\ngo on"):
        held("the interruption crosses the take", f"the take's mark {sorted(seen)}; the first prompt opens on "
             f"{INTERRUPTED}")
    else:
        failures.append(f"  ✗ interrupted                 seen={seen} prompt={prompt[:120]!r}")

    # --- resumed then closed without a message: parked, never dead ----------------------------------
    live = taken_at(bench.temp() / "m4")
    closed(live)
    rows = {one["run"]: one for one in events_of(m.call("agent", "status", "agents/ag1", "--json").stdout)
            if "run" in one}
    if rows.get(key, {}).get("state") == "parked":
        held("a conversation closed without a message leaves its run parked", f"status --json: {key} parked")
    else:
        failures.append(f"  ✗ closed bare                 {rows.get(key)}")

    # === the plain house again: conduct off in a fresh conversation =====================================
    out_p = bench.temp() / "jp"
    commands = [{"kind": "message", "text": "first"}, {"kind": "conduct", "on": False},
                {"kind": "message", "text": "bare one"}, {"kind": "conduct", "on": True},
                {"kind": "message", "text": "again"}, {"kind": "quit"}]
    live = talk(h, "play", out_p)
    out, err = live.communicate("".join(json.dumps(one) + "\n" for one in commands), timeout=120)
    texts = list(prompts(out_p).values())
    bare_ones = [one for one in texts if "bare one" in one]
    conducted = [one for one in texts if "bare one" not in one]
    opening = bare_ones[0].splitlines()[:3] if len(bare_ones) == 1 else []
    if (live.returncode == 0 and opening == [PARENTHESIS, HEAD, "bare one"]
            and conducted and not any(PARENTHESIS in one for one in conducted)):
        held("conduct off opens on the parenthesis", f"the bare prompt opens on PARENTHESIS, HEAD, the message; "
             f"the {len(conducted)} prompts of the conducted exchanges never carry it")
    else:
        failures.append(f"  ✗ parenthesis                 rc={live.returncode} bare={len(bare_ones)} opening={opening} "
                        f"conducted={len(conducted)} carried={[PARENTHESIS in one for one in conducted]} "
                        f"{err[-200:]!r}")

    # === a lawful house: two launches an exchange, the stop in the first =================================
    s = A.House(bench)
    s.lawful()

    # --- stop during an exchange: the harness dies, the verdict says interrupted, the run stands -----
    known = set(s.keys())
    out_s = bench.temp() / "jc"
    live = talk(s, "pause", out_s, "--quiet")
    live.stdin.write(command("message", text="think"))
    live.stdin.flush()
    shown = until(lambda: bool(s.read(".pid", out_s)))
    pid = int(s.read(".pid", out_s) or 0)
    live.stdin.write(command("stop"))
    live.stdin.flush()
    dead = until(lambda: not A.alive(pid)) if pid else False
    seen_events = until_kind(live, "verdict")
    key_s = next((one for one in s.keys() if one not in known), "")
    still = bool(key_s) and lock.held(A.launcher(s.agent_meta, key_s))
    live.stdin.write(command("message", text="go on") + command("quit"))
    out, err = live.communicate(timeout=120)
    later = events_of(out)
    verdicts = [one for one in seen_events + later if one.get("kind") == "verdict"]
    openings = [one for one in seen_events + later if one.get("kind") == "opened"]
    if (shown and pid and dead and still and live.returncode == 0 and err == ""
            and len(verdicts) == 2 and verdicts[0].get("state") == "interrupted" and verdicts[0].get("kept") is False
            and str(verdicts[0].get("reason", "")).startswith("interrupted")
            and verdicts[1].get("state") == "parked"
            and len(openings) == 2 and openings[1].get("standing") is True
            and [one.get("kind") for one in later][-1] == "closed"):
        held("stop during an exchange", f"the harness (pid {pid}) dead, the lock held, verdict interrupted with "
             "nothing kept and its reason; `go on` reopened the standing run (opened.standing) and parked it; closed")
    else:
        failures.append(f"  ✗ stop                        shown={shown} pid={pid} dead={dead} still={still} "
                        f"rc={live.returncode} err={err[-200:]!r} verdicts={verdicts} openings={openings} "
                        f"later={[o.get('kind') for o in later]}")
    return 0
