"""Scenario `team-sharing` -- 3 case(s) (batch le-partage-tire, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the pulled sharing, on the paper run's
prompts and journal.
- the head of a wake-up names what the others answered since the agent's last wake-up: m-1 no
  line, m-2 r1 and r2 with `--since` the id of m's first intent and the house console, m-3 r3 and
  r2 and nothing of m-2 again, r2-2 r1 and m
- the line costs little: under 200 characters, against the texts it names
- `team responses --since` reads the texts the line names, `--agent`, `--task --last`, `--last`;
  the journal unchanged
"""
from __future__ import annotations

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
    m1, m2, m3 = (h.prompt_of(f"m-{n}") for n in (1, 2, 3))
    r22 = h.prompt_of("r2-2")
    m2_named, m2_console, m2_since, m2_line = T.shared_in(m2)
    m3_named, _, m3_since, _ = T.shared_in(m3)
    r22_named, _, r22_since, _ = T.shared_in(r22)
    want_m2 = [(one["agent"], "T1", one["id"]) for one in new_for("m", m_intents[0]["id"], m_intents[1]["id"])] if len(m_intents) > 1 else []
    want_m3 = [(one["agent"], "T1", one["id"]) for one in new_for("m", m_intents[1]["id"], m_intents[2]["id"])] if len(m_intents) > 2 else []
    want_r22 = [(one["agent"], "T1", one["id"]) for one in new_for("r2", r2_intents[0]["id"], r2_intents[1]["id"])] if len(r2_intents) > 1 else []
    if (m1 and not T.SHARED_LINE.search(m1) and m2_named == want_m2 and [one[0] for one in m2_named] == ["r1", "r2"]
            and m2_console == str(h.ws.resolve() / "pp") and m2_since == m_intents[0]["id"]
            and m3_named == want_m3 and [one[0] for one in m3_named] == ["r3", "r2"] and m3_since == m_intents[1]["id"]
            and not {one[2] for one in m2_named} & {one[2] for one in m3_named}
            and r22_named == want_r22 and {"r1", "m"} <= {one[0] for one in r22_named} and r22_since == r2_intents[0]["id"]
            and m2_line.startswith("[new responses") and m2 != m1):
        held("the head names what the others answered", f"m-1 no line; m-2: {[one[0] for one in m2_named]} since #{m2_since}, "
             f"the house console; m-3: {[one[0] for one in m3_named]} since #{m3_since}, nothing of m-2 again; "
             f"r2-2: {[one[0] for one in r22_named]}")
    else:
        failures.append(f"  ✗ sharing line                m1_line={bool(T.SHARED_LINE.search(m1))} m2={m2_named} want={want_m2} "
                        f"console={m2_console!r} since={m2_since}/{m_intents[0]['id'] if m_intents else '?'} m3={m3_named} want3={want_m3} "
                        f"r22={r22_named} want22={want_r22} {m2[-300:]!r}")

    # --- the line costs little: its length against the texts it names ---------------------------------
    answers = T.lines(h.records / "responses.jsonl")

    def text_of(agent: str, run: str, index) -> str:
        return next((str(one.get("response") or "") for one in answers
                     if one.get("agent") == agent and one.get("run") == run and one.get("index") == index), "")

    by_id = {one["id"]: one for one in ended_all}
    texts = [text_of(by_id[i]["agent"], by_id[i]["run"], by_id[i]["index"]) for _, _, i in m2_named if i in by_id]
    mass = sum(len(one) for one in texts)
    if m2_line and len(m2_line) < 200 and texts and all(texts):
        held("the line costs little", f"the line of m-2: {len(m2_line)} characters; the {len(texts)} texts it names: "
             f"{mass} characters at the record ({', '.join(str(len(one)) for one in texts)})")
    else:
        failures.append(f"  ✗ sharing mass                line={len(m2_line)} texts={[len(one) for one in texts]}")

    # --- team responses reads the texts the line names -------------------------------------------------
    before_r = journal.read_bytes()
    since = h.call("team", "responses", "review", "--since", str(m2_since if m2_since >= 0 else 0))
    only_r2 = h.call("team", "responses", "review", "--agent", "r2")
    last_t1 = h.call("team", "responses", "review", "--task", "T1", "--last", "1")
    last_two = h.call("team", "responses", "review", "--last", "2")

    def heads(played) -> list[tuple[int, str, str]]:
        return [(int(line.split()[0].lstrip("#")), line.split()[1], line.split()[3])
                for line in played.stdout.splitlines() if line.startswith("#")]

    since_heads = heads(since)
    line_ids = {i for _, _, i in m2_named}
    if (since.returncode == 0 and all(one[0] > m2_since for one in since_heads)
            and [(one[1], one[0]) for one in since_heads if one[0] in line_ids] == [(a, i) for a, _, i in m2_named]
            and '{"done": true}' in since.stdout and '"ask"' in since.stdout
            and only_r2.returncode == 0 and heads(only_r2) and all(one[1] == "r2" for one in heads(only_r2))
            and last_t1.returncode == 0 and len(heads(last_t1)) == 1 and heads(last_t1)[0][2] == "T1" and '"LGTM"' in last_t1.stdout
            and last_two.returncode == 0 and len(heads(last_two)) == 2
            and journal.read_bytes() == before_r):
        held("team responses reads the texts the line names", f"--since #{m2_since}: {len(since_heads)} response(s) all after it, "
             f"the line's {len(m2_named)} among them with their texts; --agent r2: {len(heads(only_r2))}; --task T1 --last 1: m's LGTM; "
             "--last 2: two; the journal unchanged")
    else:
        failures.append(f"  ✗ team responses              {since.returncode}/{only_r2.returncode}/{last_t1.returncode}/"
                        f"{last_two.returncode} heads={since_heads[:4]} want={[(a, i) for a, _, i in m2_named]} "
                        f"{since.stdout[:300]!r} {since.stderr[-200:]!r}")
    return 0
