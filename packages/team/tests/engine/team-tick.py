"""Scenario `team-tick` -- 8 case(s) (batch le-tick, 2026-10-01, les-limites-du-tick and
l-attente for the two cases that read the paper run; split out of `team-review` by
les-scenarios-par-maison, 2026-10-07): a throwaway house with a TEAM witness scripted per agent
and per wake-up, the paper run of the study § 15 replayed on it.
- `--launches` rides the launch flags: kept at `team-started.launch` beside the harness
- the paper run replays: `team start review --harness <witness>` and the ticks the wake-ups fire
  by `--on-end` take the team to `done T1` and `schedule-off` -- 8 wake-ups of which 1 failed, m woken
  3 times (the second with the note, r1's done and r2's ask), r1 1, r2 2, r3 2, m and r2 resumed on
  their run and r3 opened a new one after its death; the multiset of (kind, who, what) equals
  `team-sim.py --trace 7`'s plus the note posted during m's last wake-up and its `returned`; no
  witness alive at the end
- the lock held by the bench: `team tick` exits 0 at once, the mark `tick.pending` posted, nothing
  written; released, a tick plays and clears the mark
- two intents forged without any launch: two `wake-failed launch-missing`, neither final -- a
  launch that never happened costs no retry (team 0.12.0) --, then r1 woken for real on T2, dead
  twice (its script), the second `final` + `terminal` + `escalate` to the task's author
- an intent forged whose tag stands at `messages.jsonl` (an `agent start --tag` the bench played): a
  late `wake-launched` from the record, then the response reaped by (run, index) and routed
- a post left undelivered when the task resolves is `returned` to its author
- the ask passes the wait: in the paper run, m's second intent precedes r3's terminal and carries
  r2's ask
- `status` extended: the limits and the cost, each agent's runs and their state, the manager's
  wait while it waits, the owner's inbox with the post returned; twice to the byte
"""
from __future__ import annotations

import json
import time

from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    journal = h.journal_of("review")

    # --- the paper run replays --------------------------------------------------------------------
    paper = T.paper_run(h)
    started, noted, late_post, done = paper["started"], paper["noted"], paper["late_post"], paper["done"]
    kept_launch = ([one for one in h.events() if one.get("kind") == "team-started"] or [{}])[-1].get("launch")
    if started.returncode == 0 and kept_launch == {"harness": h.harness, "provider": T.WITNESS_GRAMMAR, "launches": "6"}:
        held("--launches rides the launch flags", "team start --launches 6: kept at team-started.launch beside the "
             "harness and its grammar, replayed at every wake-up")
    else:
        failures.append(f"  ✗ launches kept               rc={started.returncode} launch={kept_launch} {started.stderr[-200:]!r}")
    found = paper["found"]
    paper_found = found
    shape = sorted(T.shape(one) for one in found if one.get("kind") in T.SIM_KINDS)
    wakes = {agent: len(T.intents_of(found, agent)) for agent in ("m", "r1", "r2", "r3")}
    runs = {agent: {one.get("run") for one in found if one.get("kind") == "wake-launched" and one.get("agent") == agent}
            for agent in ("m", "r1", "r2", "r3")}
    second = T.intents_of(found, "m")[1] if len(T.intents_of(found, "m")) > 1 else {}
    by_id = {one.get("id"): one for one in found}
    second_verbs = sorted(by_id.get(mid, {}).get("verb", "?") for mid in second.get("messages", []))
    done_event = next((one for one in found if one.get("kind") == "done"), {})
    alive = T.witness_alive(h)
    second_prompt = h.prompt_of("m-2")
    if (started.returncode == 0 and noted.returncode == 0 and late_post is not None and late_post.returncode == 0
            and done and shape == T.PAPER_SHAPE
            and wakes == {"m": 3, "r1": 1, "r2": 2, "r3": 2}
            and {agent: len(keys) for agent, keys in runs.items()} == {"m": 1, "r1": 1, "r2": 1, "r3": 2}
            and second_verbs == ["ask", "done", "note"]
            and done_event.get("task") == "T1" and done_event.get("result") == "LGTM"
            and "change of course" in second_prompt and "scope?" in second_prompt
            and alive == ""):
        held("the paper run replays", f"8 wake-ups (1 failed), m 3 · r1 1 · r2 2 · r3 2; m and r2 resumed their run, r3 opened a new one after its death; "
             f"the journal's shape is team-sim --trace 7's plus the late note returned; done T1 = LGTM; "
             f"{len(found)} events, no witness alive")
    else:
        missing = [one for one in T.PAPER_SHAPE if one not in shape]
        extra = [one for one in shape if one not in T.PAPER_SHAPE]
        failures.append(f"  ✗ paper run                   {started.returncode}/{noted.returncode}/"
                        f"{getattr(late_post, 'returncode', None)} done={done} wakes={wakes} runs={ {a: len(k) for a, k in runs.items()} } "
                        f"second={second_verbs} result={done_event.get('result')!r} alive={alive!r} "
                        f"missing={missing} extra={extra} {started.stderr[-200:]!r}")

    # --- the lock held: the mark posted, nothing written; released, a tick plays ------------------
    tick_lock = journal.parent / "tick.lock"
    mark = journal.parent / "tick.pending"
    before = journal.read_bytes() if journal.is_file() else b""
    with holding(tick_lock):
        started_at = time.monotonic()
        marked = h.call("team", "tick", "review")
        took = time.monotonic() - started_at
        mark_seen = mark.exists()
        unchanged = (journal.read_bytes() if journal.is_file() else b"") == before
    played = h.call("team", "tick", "review")
    if (marked.returncode == 0 and took < 2.0 and mark_seen and unchanged
            and played.returncode == 0 and not mark.exists()):
        held("the lock held: marked, nothing written", f"tick exited 0 in {took:.2f}s with tick.pending posted and the "
             "journal untouched; released, a tick played and cleared the mark")
    else:
        failures.append(f"  ✗ lock held                   {marked.returncode}/{played.returncode} took={took:.2f} "
                        f"mark={mark_seen} unchanged={unchanged} after={mark.exists()} {marked.stderr[-200:]!r} "
                        f"{played.stderr[-200:]!r}")

    # --- intents forged without any launch cost no retry; r1 woken for real, dead twice, final -----
    opened = h.call("team", "post", "review", "--to", "r1", "--message", "look again", "--no-tick")
    found = h.events()
    do_id = max([one["id"] for one in found if one.get("kind") == "post" and one.get("task") == "T2"] or [0])
    last_id = T.forge_intents(h, "review", "T2", "r1", ("forged-1", "forged-2"), [do_id])
    ticked = h.call("team", "tick", "review")

    def r1_final(found: list[dict]) -> bool:
        return any(one.get("kind") == "wake-failed" and one.get("final") and one.get("task") == "T2" for one in found)

    h.tick_until("review", r1_final)                 # a dead wake-up fires no on-end: the bench ticks
    found = h.events()
    after = [one for one in found if one.get("id", 0) > last_id + 2]
    fails = [(one.get("tag"), one.get("final"), one.get("reason")) for one in after
             if one.get("kind") == "wake-failed" and one.get("task") == "T2"]
    real = [one for one in after if one.get("kind") == "wake-launched" and one.get("agent") == "r1"]
    tail = [(one.get("kind"), one.get("agent") or one.get("from"), one.get("verb"), one.get("to")) for one in after
            if one.get("kind") in ("terminal", "post") and one.get("task") == "T2"]
    launched_tags = {one.get("tag") for one in T.lines(h.records / "messages.jsonl")}
    if (opened.returncode == 0 and ticked.returncode == 0
            and fails[:2] == [("forged-1", False, "launch-missing"), ("forged-2", False, "launch-missing")]
            and [(final, reason) for _, final, reason in fails[2:]] == [(False, "wake-dead"), (True, "wake-dead")]
            and len(real) == 2
            and tail == [("terminal", "r1", None, None), ("post", "r1", "escalate", "house")]
            and not launched_tags & {"forged-1", "forged-2"}):
        held("intents without a launch cost no retry", "two wake-failed launch-missing, neither final; r1 "
             "woken for real twice, wake-dead then final, terminal r1, post escalate r1 -> house")
    else:
        failures.append(f"  ✗ forged intent               {opened.returncode}/{ticked.returncode} fails={fails} "
                        f"real={len(real)} tail={tail} {ticked.stderr[-200:]!r}")

    # --- an intent forged whose tag stands at messages.jsonl: a late launch, the response reaped ---
    opened3 = h.call("team", "post", "review", "--to", "r2", "--message", "once more", "--no-tick")
    found = h.events()
    do3 = max([one["id"] for one in found if one.get("kind") == "post" and one.get("task") == "T3"] or [0])
    begun = h.call("agent", "start", "r2", "--message", "once more", "--tag", "forged-3", *h.harnessed)
    report = json.loads(begun.stdout.strip() or "{}") if begun.returncode == 0 else {}
    waited = h.call("agent", "wait", "r2", str(report.get("key", "")), "--timeout", "60") if report else None
    last_id = T.forge_intents(h, "review", "T3", "r2", ("forged-3",), [do3])   # read again: a tick may have written meanwhile
    ticked3 = h.call("team", "tick", "review")
    found = h.events()
    after = [one for one in found if one.get("id", 0) > last_id + 1]
    kinds3 = [one.get("kind") for one in after]
    launched3 = next((one for one in after if one.get("kind") == "wake-launched"), {})
    if (opened3.returncode == 0 and begun.returncode == 0 and waited is not None and waited.returncode == 0
            and ticked3.returncode == 0
            and kinds3[:3] == ["wake-launched", "wake-ended", "terminal"]
            and launched3.get("tag") == "forged-3" and launched3.get("run") == report.get("key")
            and any(one.get("kind") == "done" and one.get("task") == "T3" for one in after)):
        held("an intent found by its tag is reaped", f"wake-launched written from messages.jsonl (run {report.get('key')}), "
             "then wake-ended, terminal r2, done T3")
    else:
        failures.append(f"  ✗ forged tag                  {opened3.returncode}/{begun.returncode}/"
                        f"{getattr(waited, 'returncode', None)}/{ticked3.returncode} {kinds3} {launched3} "
                        f"{begun.stderr[-200:]!r} {ticked3.stderr[-200:]!r}")

    # --- a post left undelivered when the task resolves is returned --------------------------------
    returned = [one for one in h.events() if one.get("kind") == "returned"]
    note_ids = [one["id"] for one in h.events() if one.get("kind") == "post" and one.get("text") == "one more thing"]
    if (len(returned) == 1 and returned[0].get("to") == "house" and returned[0].get("message") in note_ids):
        held("a post left on a resolved task is returned", f"returned #{returned[0].get('message')} to house")
    else:
        posts = {one["id"]: (one.get("verb"), one.get("from"), one.get("to"), one.get("task")) for one in h.events() if one.get("kind") == "post"}
        failures.append(f"  ✗ returned                    {[(one.get('message'), one.get('to'), posts.get(one.get('message'))) for one in returned]} notes={note_ids}")

    # --- the ask passes the wait: m's second intent precedes r3's terminal ---------------------------
    second_m = T.intents_of(paper_found, "m")[1] if len(T.intents_of(paper_found, "m")) > 1 else {}
    r3_terminal = next((one for one in paper_found if one.get("kind") == "terminal" and one.get("agent") == "r3"), {})
    paper_by_id = {one.get("id"): one for one in paper_found}
    carried = [paper_by_id.get(mid, {}) for mid in second_m.get("messages", [])]
    if (second_m and r3_terminal and second_m["id"] < r3_terminal["id"]
            and any(one.get("verb") == "ask" and one.get("from") == "r2" for one in carried)):
        held("the ask passes the wait", f"m's second intent #{second_m['id']} before r3's terminal #{r3_terminal['id']}, "
             "carrying r2's ask")
    else:
        failures.append(f"  ✗ ask passes                  second={second_m.get('id')} r3={r3_terminal.get('id')} "
                        f"carried={[(one.get('verb'), one.get('from')) for one in carried]}")

    # --- status extended: the cost, the runs and their state, the wait seen, the owner's inbox ----------
    waits_seen = paper["waits_seen"]
    before2 = journal.read_bytes()
    first2 = h.call("team", "status", "review")
    second2 = h.call("team", "status", "review")
    lines2 = first2.stdout.splitlines()
    m_line = next((line for line in lines2 if line.startswith("m · ")), "")
    r3_line = next((line for line in lines2 if line.startswith("r3 · ")), "")
    if (first2.returncode == 0 and first2.stdout == second2.stdout and journal.read_bytes() == before2
            and "cost 0.08 USD" in first2.stdout and "budget spent" not in first2.stdout      # the paper run's 0.07 + the launch the bench played itself
            and "· run " in m_line and m_line.endswith("· ended · on T1") and "waits" not in m_line
            and r3_line.endswith("· ended · on T1")
            and "owner inbox 2" in first2.stdout and "note from house on T1 · returned" in first2.stdout
            and "escalate from r1 on T2" in first2.stdout
            and waits_seen.startswith("m · ") and "· waits " in waits_seen):
        held("status says the runs, the wait, the owner's inbox, the cost", f"cost 0.08 USD, m's one run ended, on T1, "
             f"owner inbox 2 (the note returned, r1's escalate); while m waited: {waits_seen.split('· waits ')[1]!r}; twice to the byte")
    else:
        failures.append(f"  ✗ status extended             rc={first2.returncode} same={first2.stdout == second2.stdout} "
                        f"waits={waits_seen!r} {first2.stdout[-500:]!r}")
    return 0
