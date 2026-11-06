"""Scenario `team-reset` -- 5 case(s): a member's runs are forgotten -- every one by `team reset <name> [--member
<m>]`, which judges before it forgets, or one at its agent's console by `-reset` -- and the member's next wake-up on
a task whose run is forgotten opens a NEW run told the history of that task's carrier alone. Five teams stand side
by side in one house, each under its own names; each case waits for its team, then reads its journal, its face and
the head of the new run.
- (a) judged before forgetting: `team-unknown`, `team-not-started`, `participant-unknown`; `member-running` on a
  member whose intent has no end, then on a member whose run's wake lock the bench holds -- rc 2 each, the slot
  standing, no `run-reset`
- (b) the tick lock held: the bench holds `tick.lock`, `team reset` waits `call_lock_wait` (1 s) then refuses
  `team-busy`, nothing forgotten
- (c) the reset: u holds T1 in run K1 and T2 in run K2; `team reset --member u` writes one `run-reset` per run,
  `{u, K1}` then `{u, K2}`, both slots gone at the agent, the face says u's run `—`, `reset`; the owner's reply on
  T1 wakes u on a NEW run whose head carries the history of T1 alone (the do delivered and the ask posted), then
  the inbox with the reply, `[you still owe an answer to]` naming T1's do alone (T2's do owed too, never said),
  the team's intention served once in pp's output after it; T1 merged, T2 left open, no wake-up failed,
  nothing returned to the owner
- (d) a member without a run: `team reset` without `--member` succeeds and writes nothing, the member's face
  still without a run
- (e) a run forgotten at its agent: w holds T1 in run K1 and T2 in run K2; K1 is forgotten by `-reset` at w's
  console (no `run-reset` in the journal), K2's slot stands; the reply on T1 opens ONE new run whose head carries
  the history of T1 alone, the inbox, the intention served once in the output; T1 merged, T2 left open, no
  wake-up failed, nothing returned to the owner
"""
from __future__ import annotations

import contextlib
import json
import re

from conductor import persistence
from conductor.state import lock
from tests.harness import cli, support

T = support(__file__, "team")

UP = "---\nagents: |\n  u agents/u\nroot: u\nschedule: off\n---\nMerge what is asked.\n"
SIDE = "---\nagents: |\n  w agents/w\nroot: w\nschedule: off\n---\nMerge and tag what is asked.\n"

# The head of a new run, read by structure: each block opens on its own line.
HISTORY = re.compile(r"^\[history of (\S+) for (\S+)\]$", re.M)
INBOX = re.compile(r"^\[inbox\]$", re.M)
OUTPUT = re.compile(r"^▌ pp · run [0-9a-f]{6}", re.M)       # the header of pp's block
SERVED = re.compile(r"^▌ INFORMATION — TEAM-\S+$", re.M)    # the section that serves the intention
TOLD = re.compile(r"^#(\d+) \S+ (?:from|to) \S+:", re.M)      # one line of a history: the message's id
OWED = re.compile(r"^\[you still owe an answer to\]$", re.M)   # the block of the debts said at the head
OWED_LINE = re.compile(r"^#(\d+) [A-Z]+ ", re.M)               # one debt: the message's id


def intention_of(declared: str) -> str:
    """-> the body of a declaration the scenario wrote: the team's intention."""
    return declared.split("---\n", 2)[2].strip()


def head_of(prompt: str, member: str, intention: str) -> tuple[list[str], dict[str, set[int]], int]:
    """-> the head of a run read by structure: its blocks in the order they stand (each history by its task,
    `inbox`, `output`, `served`, `intention`), the ids each history tells, and how often the intention stands."""
    found = [(one.start(), one.group(1)) for one in HISTORY.finditer(prompt) if one.group(2) == member]
    told = {}
    for at, task in found:
        block = prompt[at:prompt.find("\n\n", at) if "\n\n" in prompt[at:] else len(prompt)]
        told[task] = {int(one) for one in TOLD.findall(block)}
    for label, pattern in (("inbox", INBOX), ("output", OUTPUT), ("served", SERVED)):
        one = pattern.search(prompt)
        if one:
            found.append((one.start(), label))
    if intention in prompt:
        found.append((prompt.find(intention), "intention"))
    return [label for _, label in sorted(found)], told, prompt.count(intention)


def owed_in(prompt: str) -> set[int]:
    """-> the ids the head's `[you still owe an answer to]` block names, read by structure; empty without it."""
    block = OWED.search(prompt)
    if not block:
        return set()
    end = prompt.find("\n\n", block.end())
    return {int(one) for one in OWED_LINE.findall(prompt[block.end():end if end != -1 else len(prompt)])}


def runs_by_task(found: list[dict], member: str) -> dict[str, str]:
    """-> the run of each task of the member: the key its first launch there reported."""
    launched = {one.get("tag"): one.get("run") for one in found if one.get("kind") == "wake-launched"}
    runs: dict[str, str] = {}
    for one in found:
        if one.get("kind") == "wake-intent" and one.get("agent") == member and launched.get(one["tag"]):
            runs.setdefault(one.get("task"), launched[one["tag"]])
    return runs


def replied_in(prompt: str, reply: int, ask: int, text: str) -> bool:
    """-> whether the inbox carries the owner's reply: its head (`#<id> RE #<ask> from house on T1`), its text under."""
    inbox = INBOX.search(prompt)
    return bool(inbox) and bool(re.search(rf"^#{reply} RE #{ask} from house on T1\b.*\n  {re.escape(text)}$",
                                          prompt[inbox.end():], re.M))


@contextlib.contextmanager
def taken(path, wait: float = 30.0):
    """The lock held by the bench for the block's time, once its holder has let it go (`wait` at most); None past it."""
    lease = lock.acquire(path, wait=wait)
    try:
        yield lease
    finally:
        if lease is not None:
            lock.release(lease)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "u": {"T1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
                     {"sleep": 0.1, "body": {"done": "merged"}}],
              "T2": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which tag?"}}},
                     {"sleep": 0.1, "body": {"done": "tagged"}}]},
        "w": {"T1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}},
                     {"sleep": 0.1, "body": {"done": "merged"}}],
              "T2": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which tag?"}}},
                     {"sleep": 0.1, "body": {"done": "tagged"}}]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    settings = h.house / "SETTINGS.md"                      # the owner's edit: a short wait for the house's locks
    settings.write_text(re.sub(r"^call_lock_wait: \d+$", "call_lock_wait: 1", settings.read_text(encoding="utf-8"),
                               count=1, flags=re.M), encoding="utf-8")

    # --- every team declared and started before the first wait -------------------------------------------
    h.declare("up", UP)
    h.declare("side", SIDE)
    h.declare("never", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    h.declare("busy", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\n---\nBusy.\n")
    h.declare("fresh", "---\nagents: |\n  v agents/v\nroot: v\nschedule: off\n---\nNot woken yet.\n")
    up = h.call("team", "start", "up", "--message", "merge PR 11", *h.harnessed)
    side = h.call("team", "start", "side", "--message", "merge PR 12", *h.harnessed)
    started_b = h.call("team", "start", "busy", "--message", "work", *h.harnessed, "--no-tick")
    fresh = h.call("team", "start", "fresh", "--message", "later", *h.harnessed, "--no-tick")

    # u and w each ask the owner on T1, then on T2, each task in its own run
    first = {name: h.settled(name, lambda found, m=member: bool(by_kind(found, "wake-ended", agent=m))
                             and all_ended(found), 60) for name, member in (("up", "u"), ("side", "w"))}
    up2 = h.call("team", "post", "up", "--to", "u", "--message", "tag release 2")
    side2 = h.call("team", "post", "side", "--to", "w", "--message", "tag release 3")
    asked = {name: first[name] and h.settled(name, lambda found, m=member: len(by_kind(found, "wake-ended", agent=m))
                                             == 2 and all_ended(found), 60)
             for name, member in (("up", "u"), ("side", "w"))}

    # (e)'s gestures, played here so that w's new run plays beside (a) to (d): w's T1 run forgotten at its console,
    # then the owner's reply
    found_w = h.events("side")
    runs_w0 = runs_by_task(found_w, "w")                    # T1's run forgotten, T2's kept
    kept_w = runs_w0.get("T1", "")
    slot_w2 = persistence.slot_of(h.meta_of("agents/w"), runs_w0["T2"]) if runs_w0.get("T2") else None
    posts_w = {(one.get("verb"), one.get("task")): one["id"] for one in by_kind(found_w, "post")
               if one.get("verb") in ("do", "ask")}
    ask_w = posts_w.get(("ask", "T1"), -1)
    slot_w = persistence.slot_of(h.meta_of("agents/w"), kept_w) if kept_w else h.ws
    meta_w, forgot = h.meta_of("agents/w"), None
    for _ in range(10):                  # once w's last wake-up has let its run's locks go; call-busy: once more
        with taken(slot_w.with_name(f"session-{kept_w}.wake.lock")), taken(lock.call_of(meta_w, kept_w)):
            pass
        forgot = cli(h.engine, "--instance", str(meta_w), "-reset", kept_w, cwd=h.ws, env=h.env)
        if forgot.returncode == 0 or "call-busy" not in forgot.stderr:
            break
    gone = bool(kept_w) and not slot_w.exists()
    standing_w2 = slot_w2 is not None and slot_w2.is_file()
    replied_w = h.call("team", "post", "side", "--task", "T1", "--reply", str(ask_w), "--message", "main")

    found = h.events("up")
    kept = next((one.get("run") for one in reversed(by_kind(found, "wake-ended", agent="u"))), "")
    slot = persistence.slot_of(h.meta_of("agents/u"), kept) if kept else h.ws
    stands = bool(kept) and slot.is_file()

    # --- (a) judged before anything is forgotten ---------------------------------------------------------
    unknown = h.call("team", "reset", "nope")
    never = h.call("team", "reset", "never")
    nobody = h.call("team", "reset", "up", "--member", "zz")
    found_b = h.events("busy")
    do_b = next(one["id"] for one in by_kind(found_b, "post", verb="do"))
    last_b = max(one["id"] for one in found_b)
    with h.journal_of("busy").open("a", encoding="utf-8") as handle:   # an intent of b without an end
        handle.write(json.dumps({"at": "2026-10-09T12:00:00+00:00", "id": last_b + 1, "team": "busy",
                                 "kind": "wake-intent", "tag": "busy-b", "agent": "b", "path": "agents/b",
                                 "task": "T1", "run": None, "index": 1, "messages": [do_b]}) + "\n")
    running_b = h.call("team", "reset", "busy")
    lock_u = h.meta_of("agents/u") / ".sys" / "state" / f"session-{kept}.wake.lock"
    with taken(lock_u) as lease_u:                          # once u's last wake-up has let it go: u's run "playing"
        running_u = h.call("team", "reset", "up", "--member", "u")
    refusals = {"team-unknown": unknown, "team-not-started": never, "participant-unknown": nobody,
                "member-running": running_b}
    untouched = slot.is_file() and not by_kind(h.events("up"), "run-reset") and not by_kind(h.events("busy"), "run-reset")
    if (up.returncode == 0 and up2.returncode == 0 and asked["up"] and stands and started_b.returncode == 0
            and lease_u is not None
            and all(one.returncode == 2 and code in one.stderr for code, one in refusals.items())
            and running_u.returncode == 2 and "member-running" in running_u.stderr and untouched):
        held("(a) judged before forgetting", "team-unknown, team-not-started, participant-unknown, member-running "
             f"(an intent without an end; u's wake lock held): rc 2 each, {kept}'s slot standing, no run-reset")
    else:
        failures.append(f"  ✗ (a) judged before forgetting  rc={up.returncode}/{up2.returncode} asked={asked} "
                        f"stands={stands} lease={lease_u is not None} "
                        f"{[(code, one.returncode, one.stderr.strip()[-120:]) for code, one in refusals.items()]} "
                        f"u={running_u.returncode} {running_u.stderr.strip()[-160:]!r} untouched={untouched}")

    # --- (b) the tick lock held: team-busy past call_lock_wait -------------------------------------------
    with taken(h.journal_of("up").parent / "tick.lock") as lease_t:
        waited = h.call("team", "reset", "up", "--member", "u")
    if (lease_t is not None and waited.returncode == 2 and "team-busy" in waited.stderr and slot.is_file()
            and not by_kind(h.events("up"), "run-reset")):
        held("(b) the tick lock held", "team reset waits call_lock_wait (1 s), then team-busy: nothing forgotten")
    else:
        failures.append(f"  ✗ (b) the tick lock held        lease={lease_t is not None} rc={waited.returncode} "
                        f"{waited.stderr.strip()[-200:]!r} slot={slot.is_file()}")

    # --- (c) the reset: every run forgotten, a new run told its task's history alone ------------------------
    runs_u = runs_by_task(h.events("up"), "u")             # T1's run and T2's, both forgotten
    slots_u = [persistence.slot_of(h.meta_of("agents/u"), one) for one in runs_u.values()]
    reset = h.call("team", "reset", "up", "--member", "u")
    found = h.events("up")
    resets = [(one.get("member"), one.get("run")) for one in by_kind(found, "run-reset")]
    face_u = next((one for one in h.face("up").get("members") or [] if one.get("member") == "u"), {})
    posts = {(one.get("verb"), one.get("task")): one["id"] for one in by_kind(found, "post")
             if one.get("verb") in ("do", "ask")}
    ask_u = posts.get(("ask", "T1"), -1)
    replied = h.call("team", "post", "up", "--task", "T1", "--reply", str(ask_u), "--message", "main")
    done = h.settled("up", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    found = h.events("up")
    reply_u = next((one["id"] for one in by_kind(found, "post", verb="re") if one.get("re") == ask_u), -1)
    reopened = next((one for one in h.prompts_of("u") if any(m.group(2) == "u" for m in HISTORY.finditer(one))), "")
    order, told, served = head_of(reopened, "u", intention_of(UP))
    new_runs = {one.get("run") for one in by_kind(found, "wake-launched", agent="u")} - set(runs_u.values())
    owed_u = owed_in(reopened)
    tasks_u = {one.get("id"): one.get("state") for one in h.face("up").get("tasks") or []}
    if (reset.returncode == 0 and len(runs_u) == 2 and len(set(runs_u.values())) == 2 and kept in runs_u.values()
            and resets == [("u", runs_u["T1"]), ("u", runs_u["T2"])] and not any(one.is_file() for one in slots_u)
            and face_u.get("run") == "—" and face_u.get("how") == "reset"
            and replied.returncode == 0 and done and len(new_runs) == 1
            and order == ["T1", "inbox", "output", "served", "intention"] and served == 1
            and told == {"T1": {posts.get(("do", "T1")), ask_u}}
            and owed_u == {posts.get(("do", "T1"))}
            and replied_in(reopened, reply_u, ask_u, "main")
            and not by_kind(found, "wake-failed") and not by_kind(found, "returned")
            and result_of(found, "T1") == "merged" and tasks_u == {"T1": "resolved", "T2": "open"}):
        held("(c) the reset", f"run-reset {{u, {runs_u['T1']}}} then {{u, {runs_u['T2']}}}, both slots gone, the "
             f"face: u's run {face_u.get('run')} {face_u.get('how')}; the reply opens run {sorted(new_runs)[0]} told "
             "T1's history alone (its do and ask), then the inbox with the reply, the debt said T1's do alone, "
             "the intention served once in its output; T1 merged, T2 left open, nothing failed, nothing returned")
    else:
        failures.append(f"  ✗ (c) the reset                 rc={reset.returncode}/{replied.returncode} "
                        f"{reset.stderr.strip()[-200:]!r} runs_u={runs_u} resets={resets} "
                        f"slots={[one.is_file() for one in slots_u]} owed={owed_u} "
                        f"face={face_u.get('run')!r}/{face_u.get('how')!r} done={done} runs={new_runs} "
                        f"order={order} told={told} posts={posts} reply={reply_u} served={served} tasks={tasks_u} "
                        f"failed={by_kind(found, 'wake-failed')} returned={by_kind(found, 'returned')} "
                        f"{reopened[:600]!r}")

    # --- (d) a member without a run ----------------------------------------------------------------------
    journal_v = h.journal_of("fresh")
    before = journal_v.read_bytes() if journal_v.is_file() else b""
    none = h.call("team", "reset", "fresh")
    face_v = next((one for one in h.face("fresh").get("members") or [] if one.get("member") == "v"), {})
    after = journal_v.read_bytes() if journal_v.is_file() else b""
    if (fresh.returncode == 0 and none.returncode == 0 and before and after == before
            and face_v.get("member") == "v" and face_v.get("run") is None and face_v.get("how") is None):
        held("(d) a member without a run", "team reset without --member: rc 0, the journal unchanged, v's face "
             "still without a run")
    else:
        failures.append(f"  ✗ (d) a member without a run    rc={fresh.returncode}/{none.returncode} "
                        f"{(none.stdout + none.stderr).strip()[-200:]!r} same={after == before} face={face_v}")

    # --- (e) a run forgotten at its agent's console ------------------------------------------------------
    done_w = h.settled("side", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 45)
    found_w = h.events("side")
    intents_w = by_kind(found_w, "wake-intent", agent="w")
    runs_w = {one["tag"]: one.get("run") for one in by_kind(found_w, "wake-launched", agent="w")}
    reopening = [one for one in intents_w if one.get("run") is None and one.get("task") == "T1"][1:]
    reply_w = next((one["id"] for one in by_kind(found_w, "post", verb="re") if one.get("re") == ask_w), -1)
    reopened_w = next((one for one in h.prompts_of("w") if any(m.group(2) == "w" for m in HISTORY.finditer(one))), "")
    order_w, told_w, served_w = head_of(reopened_w, "w", intention_of(SIDE))
    tasks_w = {one.get("id"): one.get("state") for one in h.face("side").get("tasks") or []}
    if (side.returncode == 0 and side2.returncode == 0 and asked["side"] and forgot is not None
            and forgot.returncode == 0 and gone and standing_w2 and not by_kind(found_w, "run-reset")
            and replied_w.returncode == 0 and done_w and len(intents_w) == 3 and len(reopening) == 1
            and reopening[0]["id"] == intents_w[-1]["id"]
            and runs_w.get(reopening[0]["tag"]) not in (None, kept_w, runs_w0.get("T2"))
            and order_w == ["T1", "inbox", "output", "served", "intention"] and served_w == 1
            and told_w == {"T1": {posts_w.get(("do", "T1")), ask_w}}
            and replied_in(reopened_w, reply_w, ask_w, "main")
            and not by_kind(found_w, "wake-failed") and not by_kind(found_w, "returned")
            and result_of(found_w, "T1") == "merged" and tasks_w == {"T1": "resolved", "T2": "open"}):
        held("(e) a run forgotten at its agent", f"w's T1 run {kept_w} forgotten by -reset at its console, no "
             f"run-reset written, T2's run {runs_w0.get('T2')} standing; the reply opens ONE new run "
             f"{runs_w.get(reopening[0]['tag'])} told T1's history alone, then the inbox with the reply, the "
             "intention served once in its output; T1 merged, T2 left open, nothing failed, nothing returned")
    else:
        failures.append(f"  ✗ (e) a run forgotten at its agent  rc={side.returncode}/{side2.returncode}/"
                        f"{getattr(forgot, 'returncode', None)}/{replied_w.returncode} asked={asked} gone={gone} "
                        f"runs_w={runs_w0} t2_stands={standing_w2} "
                        f"done={done_w} intents={[(one['id'], one.get('task'), one.get('run')) for one in intents_w]} "
                        f"order={order_w} told={told_w} posts={posts_w} reply={reply_w} served={served_w} tasks={tasks_w} "
                        f"failed={by_kind(found_w, 'wake-failed')} returned={by_kind(found_w, 'returned')} "
                        f"{getattr(forgot, 'stderr', '')[-200:]!r} {reopened_w[:600]!r}")
    return 0
