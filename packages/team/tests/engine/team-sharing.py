"""Scenario `team-sharing` -- 2 case(s) (batch le-partage-tire, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07; the head's line retired by la-ligne-des-reponses-retiree,
2026-11-11): what a member reads of the others' answers, on the paper run's prompts and journal.
- the head of a wake-up names none of the others' answers: m-1, m-2 (the owner's note), m-3, m-4 and r2-2 name no
  `wake-ended` of another member, though the others answered between the run's cursor and its intent, read on the
  journal -- the order of the wake-ups is the tick's, never assumed --; each head's size in characters said
- `team responses --since` reads the others' answers on demand, after a journal id: `--since` m's first intent
  gives each answer after it with its text, `--agent`, `--task --last`, `--last`; the journal unchanged
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

    # --- the head of a wake-up names none of the others' answers ---------------------------------------
    prompts = {name: h.prompt_of(name) for name in ("m-1", "m-2", "m-3", "m-4", "r2-2")}   # m-2 woke on the note
    named = {name: T.ends_named(prompt, paper_found, name.split("-")[0]) for name, prompt in prompts.items()}
    windows = [new_for("m", one["id"], other["id"]) for one, other in zip(m_intents, m_intents[1:4])]
    windows += [new_for("r2", r2_intents[0]["id"], r2_intents[1]["id"])] if len(r2_intents) > 1 else []
    sizes = ", ".join(f"{name} {len(prompt)}" for name, prompt in prompts.items())
    if all(prompts.values()) and not any(named.values()) and any(windows) and len(m_intents) > 3:
        held("the head names none of the others' answers", f"m-1 to m-4 and r2-2 name no wake-ended of another "
             f"member, though {sum(len(one) for one in windows)} answered within their windows; heads in characters: "
             f"{sizes}")
    else:
        failures.append(f"  ✗ head without the others     named={named} windows={[len(one) for one in windows]} "
                        f"prompts={[bool(one) for one in prompts.values()]} sizes: {sizes}")

    # --- team responses reads the others' answers on demand ---------------------------------------------
    before_r = journal.read_bytes()
    cursor = m_intents[0]["id"] if m_intents else 0
    since = h.call("team", "responses", "review", "--since", str(cursor))
    only_r2 = h.call("team", "responses", "review", "--agent", "r2")
    last_t1 = h.call("team", "responses", "review", "--task", "T1", "--last", "1")
    last_two = h.call("team", "responses", "review", "--last", "2")

    def heads(played) -> list[tuple[int, str, str]]:
        return [(int(line.split()[0].lstrip("#")), line.split()[1], line.split()[3])
                for line in played.stdout.splitlines() if line.startswith("#")]

    since_heads = heads(since)
    after = [(one.get("agent"), one["id"]) for one in ended_all if one["id"] > cursor]
    others = [one for one in after if one[0] != "m"]
    if (since.returncode == 0 and [(one[1], one[0]) for one in since_heads] == after and others
            and '{"re": ' in since.stdout and '"ask"' in since.stdout
            and only_r2.returncode == 0 and heads(only_r2) and all(one[1] == "r2" for one in heads(only_r2))
            and last_t1.returncode == 0 and len(heads(last_t1)) == 1 and heads(last_t1)[0][2] == "T1" and '"LGTM"' in last_t1.stdout
            and last_two.returncode == 0 and len(heads(last_two)) == 2
            and journal.read_bytes() == before_r):
        held("team responses reads the others' answers on demand", f"--since #{cursor} (m's first intent): "
             f"{len(since_heads)} response(s), each wake-ended after it in the journal's order, {len(others)} of the "
             f"others among them with their texts; --agent r2: {len(heads(only_r2))}; --task T1 --last 1: m's LGTM; "
             "--last 2: two; the journal unchanged")
    else:
        failures.append(f"  ✗ team responses              {since.returncode}/{only_r2.returncode}/{last_t1.returncode}/"
                        f"{last_two.returncode} heads={since_heads[:6]} want={after[:6]} "
                        f"{since.stdout[:300]!r} {since.stderr[-200:]!r}")
    return 0
