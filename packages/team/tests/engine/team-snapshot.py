"""Scenario `team-snapshot` -- 3 case(s) (batch les-garde-fous, 2026-10-01, and the reworks of
team 0.13.0; split out of `team-review` by les-scenarios-par-maison, 2026-10-07): the snapshot
of a journal, on a journal the product writes without a wake-up and on a forged journal.
- the snapshot changes no truth: on the review team's journal (a task opened, a second one stopped,
  its `do` returned to the owner -- no witness, no wake-up), `team snapshot` writes ONE event,
  `team status` and `team log` render the same bytes before and after; on a forged journal of
  1 950 events (650 tasks resolved) the state read (`state_of`: the tail parsed from the last
  snapshot on, the resolved tasks' messages pruned at the pack) is measurably shorter after
  the snapshot (both times cited, measured in-process)
- a snapshot keeps the owner's box (rework, the demo's step 73): on the review team, whose
  `do` was RETURNED to the owner, the face's `owner_inbox` keeps it `returned`, and `team status` and
  `team inbox` render the same bytes before and after `team snapshot` -- the returned post's id
  survives the JSON round trip; on the
  journals snapshotted (review, long) the state read from the snapshot equals the full replay
  key by key (the pruned messages apart)
- a snapshot of team 0.13.0 reads back (arbitration 27): runs as `[member, task, run]` rows, each member
  takes the run of its last row; a snapshot written now packs `[member, run]` -- read on a journal of
  team 0.32.2 (`OLD_JOURNAL`), whose members hold runs
"""
from __future__ import annotations

import json
import subprocess
import sys

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    h.declare("review", T.REVIEW)                          # a journal the product writes without a wake-up: a task
    h.call("team", "start", "review", "--message", "review PR 42", "--no-tick")   # opened, a second one stopped,
    h.call("team", "post", "review", "--to", "r1", "--message", "look at the tests", "--no-tick")   # its do
    h.call("team", "stop", "review", "--task", "T2", "--no-tick")                  # returned to the owner
    returned = [one.get("message") for one in h.events("review") if one.get("kind") == "returned"]

    # --- the snapshot changes no truth ----------------------------------------------------------------
    before_status = h.call("team", "status", "review")
    before_log = h.call("team", "log", "review")
    snapped = h.call("team", "snapshot", "review")
    snaps = [one for one in h.events("review") if one.get("kind") == "snapshot"]
    after_status = h.call("team", "status", "review")
    after_log = h.call("team", "log", "review")
    h.declare("long", "---\nagents: |\n  s s\nroot: s\n---\nA net under one agent.\n")
    longteam = h.call("team", "start", "long", "--message", "hold the line", "--no-tick")
    jlong = h.journal_of("long")
    last_id = max((int(one.get("id") or 0) for one in T.lines(jlong)), default=0)
    with jlong.open("a", encoding="utf-8") as handle:        # the bench's hand on a disposable journal
        # a standing team's history: 650 tasks opened, delegated and resolved (1 950 events)
        for n in range(650):
            task = f"T{n + 2}"
            for one in ({"kind": "task", "task": task, "from": "house", "to": "s", "text": f"job {n}"},
                        {"kind": "post", "task": task, "from": "house", "to": "s", "verb": "do", "text": f"job {n}"},
                        {"kind": "done", "task": task, "result": f"done {n}"}):
                last_id += 1
                handle.write(json.dumps({"at": "2026-10-01T21:00:00+00:00", "id": last_id, "team": "long", **one}) + "\n")
    probe = T.probe_script(h, "journal = Path(sys.argv[1])\n"
                              "begun = time.perf_counter()\n"
                              "for _ in range(50):\n"
                              "    mod.state_of(journal)\n"
                              "print(f'{time.perf_counter() - begun:.4f}')\n")

    def replay_time() -> float:
        played = subprocess.run([sys.executable, str(probe), str(jlong)], capture_output=True, text=True)
        return float(played.stdout.strip() or "nan")

    long_before = replay_time()
    snap_long = h.call("team", "snapshot", "long")
    long_after = replay_time()
    if (before_status.returncode == 0 and snapped.returncode == 0 and len(snaps) == 1
            and isinstance(snaps[0].get("upto"), int) and isinstance(snaps[0].get("state"), dict)
            and after_status.stdout == before_status.stdout and after_log.stdout == before_log.stdout
            and longteam.returncode == 0 and snap_long.returncode == 0 and long_after < long_before):
        held("the snapshot changes no truth", f"review: ONE snapshot event, status and log byte-identical "
             f"before and after; 50 state reads on 1 950 forged events: {long_before:.3f}s before, "
             f"{long_after:.3f}s after the snapshot")
    else:
        failures.append(f"  ✗ snapshot                    {snapped.returncode}/{snap_long.returncode} "
                        f"snaps={len(snaps)} same_status={after_status.stdout == before_status.stdout} "
                        f"same_log={after_log.stdout == before_log.stdout} "
                        f"times={long_before:.3f}/{long_after:.3f} {snapped.stderr[-200:]!r}")

    # --- a snapshot keeps the owner's box: the returned post survives the JSON round trip ---------------
    box_status = h.call("team", "status", "review")
    box_inbox = h.call("team", "inbox", "review")
    box_face = h.face("review")
    snap_box = h.call("team", "snapshot", "review")
    box_status2 = h.call("team", "status", "review")
    box_inbox2 = h.call("team", "inbox", "review")
    box_face2 = h.face("review")
    kept_box = [(one.get("id"), one.get("returned")) for one in box_face2.get("owner_inbox") or []]
    # the whole state, not one reader: read from the snapshot on, it equals the full replay key by
    # key -- the messages of resolved tasks pruned, the others kept as they were
    same = T.probe_script(h, "out = {}\n"
                             "for name in sys.argv[1:]:\n"
                             "    journal = Path(name)\n"
                             "    full = mod.replay([one for one in mod.lines_of(journal) if one.get('kind') != 'snapshot'])\n"
                             "    cut = mod.state_of(journal)\n"
                             "    out[journal.parent.name] = sorted([key for key in full if key != 'messages' and full[key] != cut.get(key)]\n"
                             "        + [f'messages#{key}' for key, one in cut['messages'].items() if full['messages'].get(key) != one])\n"
                             "print(json.dumps(out))\n")
    compared = subprocess.run([sys.executable, str(same)] + [str(h.journal_of(name)) for name in ("review", "long")],
                              capture_output=True, text=True)
    differing = json.loads(compared.stdout or "null") or {"probe": [compared.stderr[-300:]]}
    if (box_status.returncode == 0 and snap_box.returncode == 0 and box_inbox2.returncode == 0
            and len(returned) == 1 and kept_box == [(returned[0], True)]
            and box_face2.get("owner_inbox") == box_face.get("owner_inbox")
            and box_status2.stdout == box_status.stdout and box_inbox2.stdout == box_inbox.stdout
            and not any(differing.values())):
        held("a snapshot keeps the owner's box", f"review: the do #{returned[0]} returned to the owner still in its "
             "face after the snapshot, `status` and `inbox` byte-identical; review and long: "
             "the state read from the snapshot equals the full replay, key by key")
    else:
        failures.append(f"  ✗ snapshot owner box          {snap_box.returncode}/{box_inbox2.returncode} "
                        f"same_status={box_status2.stdout == box_status.stdout} "
                        f"same_inbox={box_inbox2.stdout == box_inbox.stdout} differing={differing} "
                        f"returned={returned} box={kept_box} "
                        f"{box_status2.stdout[-300:]!r} {box_inbox2.stderr[-300:]!r}")

    # --- a snapshot of team 0.13.0 reads back: a member takes the run of its last row (arbitration 27) --------
    older_snap = T.probe_script(h, "old = mod.unpacked({'runs': [['x', 'T1', 'aaa111'], ['y', 'T1', 'ccc333'], ['x', 'T2', 'bbb222']]})\n"
                                   "state = mod.state_of(Path(sys.argv[1]))\n"
                                   "back = mod.unpacked(json.loads(json.dumps(mod.packed(state))))\n"
                                   "print(json.dumps({'old': {str(k): v for k, v in old['runs'].items()},\n"
                                   "                  'packed': mod.packed(state)['runs'],\n"
                                   "                  'same': back['runs'] == state['runs']}))\n")
    h.declare("old", T.OLD_DECLARED)                       # a journal with runs: three members, each its run
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(T.OLD_JOURNAL, encoding="utf-8")
    read_old = subprocess.run([sys.executable, str(older_snap), str(h.journal_of("old"))], capture_output=True, text=True)
    seen_old = json.loads(read_old.stdout or "null") or {}
    if (read_old.returncode == 0 and seen_old.get("old") == {"x": "bbb222", "y": "ccc333"}
            and all(isinstance(row, list) and len(row) == 2 for row in seen_old.get("packed") or [None])
            and seen_old.get("same") is True):
        held("a snapshot of team 0.13.0 reads back", "runs as [member, task, run] rows: each member takes the run "
             "of its last row; a snapshot written now packs [member, run] and reads back the same runs")
    else:
        failures.append(f"  ✗ snapshot 0.13.0             rc={read_old.returncode} {seen_old} {read_old.stderr[-300:]!r}")
    return 0
