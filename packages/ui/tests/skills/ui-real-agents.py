"""Scenario `ui-real-agents` -- the Agents tab on the REAL faces of `agent` (plan ui, batch
le-reel-du-poste-recadre), a real run of two exchanges made first at the post, the model set to `m2`
between them:
- the table says `agents/ag1` and its run, read from `agent list --json` and `agent status --json`
- its run resumed from the overlay of its runs, `p` names it (the last field of its parameters): `names.jsonl`
  one line, `agent status --json` says the name
(the statistics and a new run prefilled are `ui-real-agents-stats`'s; the run resumed with its history is
`ui-real-resume`'s)
"""
from __future__ import annotations


from tests.harness import support

R = support(__file__, "real")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-agents")
    made = post.talk()
    runs = post.status_json()
    key = runs[0]["run"] if runs else ""
    if made.returncode != 0 or len(runs) != 1 or len(post.responses()) != 2:
        failures.append(f"  ✗ real run                    rc={made.returncode} runs={runs} {made.stderr[-300:]!r}")
        return 0

    # --- the table, then the run resumed and named by p ------------------------------------------------
    table = post.render("--render", "agents", "--size", "120x30")
    named = post.render("--render", "dialogue", "--size", "120x30", "--press",
                        "2,down,enter,enter,wait:waiting,escape,p,wait:none:1.5,tab,tab,tab,tab,tab,d,e,m,o,enter",
                        "--wait", "none:2")
    names, after = post.names(), post.status_json()
    if (table.returncode == 0 and R.AGENT in table.stdout and "1 agent(s) · 1 run(s) · read " in table.stdout
            and named.returncode == 0 and len(names) == 1 and names[0]["name"] == "demo" and names[0]["run"] == key
            and after and after[0]["name"] == "demo"):
        held("the table reads the real faces, p names the run", f"{R.AGENT} and its run {key}; p + demo: names.jsonl "
             "one line, status --json says demo")
    else:
        failures.append(f"  ✗ real table and name         {table.stdout!r} names={names} after={after[:1]} {named.stderr[-300:]!r}")

    return 0
