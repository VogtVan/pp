"""Scenario `team-sharing` -- 3 case(s) (batch le-partage-tire, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the pulled sharing, on the paper run's
prompts and journal.
- the head of a wake-up names what the others answered since the agent's last wake-up: m-1 no
  line; m-2 (the owner's note), m-3, m-4 and r2-2 each the `wake-ended` of the others between the run's
  cursor and its own intent, read on the journal -- the order of the wake-ups is the tick's, never assumed
  --, a line with `--since` the id of the run's cursor and the house console; something named across m's
  wake-ups, nothing named twice
- the line costs little: under 200 characters, against the texts it names
- `team responses --since` reads the texts the line names, `--agent`, `--task --last`, `--last`;
  the journal unchanged
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    paper_found = T.paper_run(h)["found"]
    journal = h.journal_of("review")
    m_intents = T.intents_of(paper_found, "m")
    r2_intents = T.intents_of(paper_found, "r2")
    ended_all = [one for one in paper_found if one.get("kind") == "wake-ended"]

    def new_for(agent: str, cursor: int, upto: int) -> list[dict]:
        return [one for one in ended_all if cursor < one["id"] < upto and one.get("agent") != agent]

    # --- the head of a wake-up names what the others answered since the agent's last wake-up ------
    m1, m_note, m2, m3 = (h.prompt_of(f"m-{n}") for n in (1, 2, 3, 4))   # m-2 woke on the owner's note
    r22 = h.prompt_of("r2-2")
    module = h.module()
    m2_named, m2_console, m2_since, m2_line = T.shared_in(module, m2)
    m3_named, _, m3_since, m3_line = T.shared_in(module, m3)
    r22_named, _, r22_since, _ = T.shared_in(module, r22)
    note_named = T.shared_in(module, m_note)[0]
    want_note = [(one["agent"], "T1", one["id"]) for one in new_for("m", m_intents[0]["id"], m_intents[1]["id"])] if len(m_intents) > 1 else []
    want_m2 = [(one["agent"], "T1", one["id"]) for one in new_for("m", m_intents[1]["id"], m_intents[2]["id"])] if len(m_intents) > 2 else []
    want_m3 = [(one["agent"], "T1", one["id"]) for one in new_for("m", m_intents[2]["id"], m_intents[3]["id"])] if len(m_intents) > 3 else []
    want_r22 = [(one["agent"], "T1", one["id"]) for one in new_for("r2", r2_intents[0]["id"], r2_intents[1]["id"])] if len(r2_intents) > 1 else []
    named_m = [*note_named, *m2_named, *m3_named]
    # the first line m's wake-ups carried -- which one depends on the order of the wake-ups, the tick's
    _, _, note_since, note_line = T.shared_in(module, m_note)
    shown_named, shown_since, shown_line = next(((named, since, line) for named, since, line in (
        (m2_named, m2_since, m2_line), (m3_named, m3_since, m3_line), (note_named, note_since, note_line)) if line),
        ([], -1, ""))
    if (m1 and not T.shared_in(module, m1)[3] and m_note and note_named == want_note
            and m2_named == want_m2
            and (not m2_named or (m2_console == str(h.ws.resolve() / "pp") and m2_since == m_intents[1]["id"]))
            and m3_named == want_m3 and (not m3_named or m3_since == m_intents[2]["id"])
            and len({one[2] for one in named_m}) == len(named_m) and named_m
            and r22_named == want_r22 and (not r22_named or r22_since == r2_intents[0]["id"])
            and m2 != m1):
        held("the head names what the others answered", f"m-1 no line; m-2: {[one[0] for one in note_named]}; m-3: {[one[0] for one in m2_named]} since "
             f"#{m2_since}, the house console; m-4: {[one[0] for one in m3_named]} since #{m3_since}, nothing of m-3 again; "
             f"r2-2: {[one[0] for one in r22_named]}")
    else:
        failures.append(f"  ✗ sharing line                m1={bool(m1)}/{bool(T.shared_in(module, m1)[3])} "
                        f"note={bool(m_note)}/{note_named} want_note={want_note} m2={m2_named} want={want_m2} "
                        f"console={m2_console!r} since={m2_since}/{m_intents[1]['id'] if len(m_intents) > 1 else '?'} m3={m3_named} want3={want_m3} "
                        f"r22={r22_named} want22={want_r22} {m2[-300:]!r}")

    # --- the line costs little: its length against the texts it names ---------------------------------
    def text_of(agent: str, run: str, launch) -> str:
        flowed = h.call("agent", "flow", agent, run, "--json", "--exchange", str(launch))
        return "\n\n".join(str(json.loads(line).get("text") or "") for line in flowed.stdout.splitlines()
                           if line.strip() and json.loads(line).get("kind") == "words")

    by_id = {one["id"]: one for one in ended_all}
    paths = {member: path for member, path in (T.by_kind(h.events("share"), "team-started")[0].get("agents") or {}).items()} \
        if T.by_kind(h.events("share"), "team-started") else {}
    texts = [text_of(paths.get(by_id[i]["agent"], by_id[i]["agent"]), by_id[i]["run"], by_id[i]["launch"])
             for _, _, i in shown_named if i in by_id]
    mass = sum(len(one) for one in texts)
    if shown_line and len(shown_line) < 200 and texts and all(texts):
        held("the line costs little", f"the first line of m's wake-ups: {len(shown_line)} characters; the {len(texts)} texts it names: "
             f"{mass} characters at the record ({', '.join(str(len(one)) for one in texts)})")
    else:
        failures.append(f"  ✗ sharing mass                line={len(shown_line)} texts={[len(one) for one in texts]}")

    # --- team responses reads the texts the line names -------------------------------------------------
    before_r = journal.read_bytes()
    since = h.call("team", "responses", "review", "--since", str(shown_since if shown_since >= 0 else 0))
    only_r2 = h.call("team", "responses", "review", "--agent", "r2")
    last_t1 = h.call("team", "responses", "review", "--task", "T1", "--last", "1")
    last_two = h.call("team", "responses", "review", "--last", "2")

    def heads(played) -> list[tuple[int, str, str]]:
        return [(int(line.split()[0].lstrip("#")), line.split()[1], line.split()[3])
                for line in played.stdout.splitlines() if line.startswith("#")]

    since_heads = heads(since)
    line_ids = {i for _, _, i in shown_named}
    if (since.returncode == 0 and all(one[0] > shown_since for one in since_heads)
            and [(one[1], one[0]) for one in since_heads if one[0] in line_ids] == [(a, i) for a, _, i in shown_named]
            and '{"re": ' in since.stdout and '"ask"' in since.stdout
            and only_r2.returncode == 0 and heads(only_r2) and all(one[1] == "r2" for one in heads(only_r2))
            and last_t1.returncode == 0 and len(heads(last_t1)) == 1 and heads(last_t1)[0][2] == "T1" and '"LGTM"' in last_t1.stdout
            and last_two.returncode == 0 and len(heads(last_two)) == 2
            and journal.read_bytes() == before_r):
        held("team responses reads the texts the line names", f"--since #{shown_since}: {len(since_heads)} response(s) all after it, "
             f"the line's {len(shown_named)} among them with their texts; --agent r2: {len(heads(only_r2))}; --task T1 --last 1: m's LGTM; "
             "--last 2: two; the journal unchanged")
    else:
        failures.append(f"  ✗ team responses              {since.returncode}/{only_r2.returncode}/{last_t1.returncode}/"
                        f"{last_two.returncode} heads={since_heads[:4]} want={[(a, i) for a, _, i in shown_named]} "
                        f"{since.stdout[:300]!r} {since.stderr[-200:]!r}")
    return 0
