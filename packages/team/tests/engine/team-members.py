"""Scenario `team-members` -- 5 case(s): a team declares `<name> <path>` -- the member's name, then the path
of the agent that plays it; several members may share one agent, each wake-up its own run. Two teams run side
by side in one house under the witness, each under its own names; five races of two starts on one new path
play beside them; each case waits for its team, then reads its journal.
- (a) two members on one agent: `ra agents/dev`, `rb agents/dev` under `ml agents/lead` -- agents/dev stands
  once, `team-started.agents` maps the names to their paths, two runs of agents/dev are launched together (two
  keys, two sessions), each intent carries its `path`, every head names its member
- (b) the neighbours line of two members of one agent quotes the first line of the neighbour's message: the
  neighbour's run key and its head, which names the neighbour
- (c) two births of one path at once: five races of two `team start` declaring one new path -- each path
  stands, both teams start, each journal maps its member to the path
- (d) two members of one agent in parallel, a member's two tasks: d delegates T1 to d1 (asleep) and d2, both
  played by agents/dd and launched together, two runs; T2 posted to d once d2 answered: d is woken on T2 before
  d1's answer, in its ONE run; `parallel: 2` is never exceeded
- (e) the cursor of the member's run: d's wake-up on T2 names d2's answer since its run's opening; its resume on
  T1 names d1 alone, since its wake-up on T2 -- what its run read is never named twice
"""
from __future__ import annotations

import re

from tests.harness import race, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (a) (b) the lead delegates to two members of one agent, who answer after a second
        "ml": [{"sleep": 0.2, "body": {"do": ["ra", "rb"]}},
               {"sleep": 0.1, "body": {"done": "both read"}}],
        "ra": [{"sleep": 1.0, "body": {"done": True}}],
        "rb": [{"sleep": 1.0, "body": {"done": True}}],
        # (d) (e) d delegates T1, then answers T2 in the same run while d1 still works
        "d": {"T1": [{"sleep": 0.2, "body": {"do": ["d1", "d2"]}},
                     {"sleep": 0.2, "body": {"done": "first"}}],
              "T2": [{"sleep": 0.2, "body": {"done": "second"}}]},
        "d1": [{"sleep": 4.0, "body": {"done": True}}],
        "d2": [{"sleep": 0.2, "body": {"done": True}}]})
    by_kind, all_ended, intents_on, terminal_of, peak, result_of = (
        T.by_kind, T.all_ended, T.intents_on, T.terminal_of, T.peak, T.result_of)

    # --- every witness team declared and started before the first wait: they run side by side --------------
    h.declare("pair", "---\nagents: |\n  ml agents/lead\n  ra agents/dev\n  rb agents/dev\nreports: |\n  ra rb -> ml\n"
                      "root: ml\nschedule: off\n---\nTwo members on one agent.\n")
    h.declare("duo", "---\nagents: |\n  d d\n  d1 agents/dd\n  d2 agents/dd\nreports: |\n  d1 d2 -> d\n"
                     "root: d\nparallel: 2\nschedule: off\n---\nTwo tasks for one manager.\n")
    gate_p = bench.temp() / "pair-gate"                 # ra and rb held until both are launched: each run under way
    pair = h.call("team", "start", "pair", "--message", "review PR 50", *T.gated(h, gate_p, ("ra", "rb")))
    duo = h.call("team", "start", "duo", "--message", "review PR 7", *h.harnessed)

    # d's second task is posted once d2 answered, while d1 still works
    d2_done = h.settled("duo", lambda found: terminal_of(found, "d2") < 10 ** 9, timeout=60)
    second_task = h.call("team", "post", "duo", "--to", "d", "--message", "review PR 8")

    # --- (c) the races: two starts on one new path, five times, while the witness teams work -----------------
    raced_births = []
    for n in range(1, 6):
        for side in ("a", "b"):
            h.declare(f"race{n}{side}", f"---\nagents: |\n  w{n}{side} shared/d{n}\nroot: w{n}{side}\nschedule: off\n---\n"
                                        "A birth raced.\n")
        both = race(h.engine, [["--instance", str(h.house), "team", "start", f"race{n}{side}", "--message", "x", "--no-tick"]
                               for side in ("a", "b")], cwd=h.ws, env=h.env)
        mapped = [next(iter(by_kind(h.events(f"race{n}{side}"), "team-started")), {}).get("agents") for side in ("a", "b")]
        raced_births.append((n, [one.returncode for one in both], h.agent_stands(f"shared/d{n}"),
                             mapped == [{f"w{n}{side}": f"shared/d{n}"} for side in ("a", "b")],
                             [one.stderr.strip()[-120:] for one in both if one.returncode]))

    # --- (a) two members on one agent ------------------------------------------------------------------------
    both_p = h.settled("pair", lambda found: {one.get("agent") for one in by_kind(found, "wake-launched")}
                       >= {"ra", "rb"}, timeout=60)
    gate_p.write_text("open", encoding="utf-8")
    done_pair = h.settled("pair", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_p = h.events("pair")
    started_p = next(iter(by_kind(found_p, "team-started")), {})
    launched_p = {one.get("agent"): one for one in by_kind(found_p, "wake-launched") if one.get("agent") in ("ra", "rb")}
    first_end = min((one["id"] for one in by_kind(found_p, "wake-ended") if one.get("agent") in ("ra", "rb")), default=0)
    intents_p = {one.get("agent"): one for one in by_kind(found_p, "wake-intent") if one.get("agent") in ("ra", "rb")}
    sessions_p = h.sessions_at("agents/dev")
    head_of = {name: rf"^\[team pair · you are {name}\]$" for name in ("ml", "ra", "rb")}
    headed_p = {name: bool(h.prompts_of(name)) and all(re.search(head_of[name], one, re.M) for one in h.prompts_of(name))
                for name in ("ml", "ra", "rb")}
    if (pair.returncode == 0 and both_p and done_pair
            and h.agent_stands("agents/dev") and h.agent_stands("agents/lead")
            and not any((h.ws / one).exists() for one in ("ml", "ra", "rb"))
            and started_p.get("agents") == {"ml": "agents/lead", "ra": "agents/dev", "rb": "agents/dev"}
            and set(launched_p) == {"ra", "rb"} and launched_p["ra"].get("run") != launched_p["rb"].get("run")
            and all(one["id"] < first_end for one in launched_p.values())
            and all(intents_p.get(name, {}).get("path") == "agents/dev" for name in ("ra", "rb"))
            and len(sessions_p) == 2 and len({run for run, _ in sessions_p}) == 2
            and len({session for _, session in sessions_p}) == 2
            and all(headed_p.values())
            and result_of(found_p, "T1") == "both read"):
        held("(a) two members on one agent", f"ra and rb on agents/dev, one instance; team-started.agents "
             f"{started_p.get('agents')}; two runs of agents/dev launched before the first end, two keys, two "
             "sessions; the journal in names, each intent with its path; every head names its member")
    else:
        failures.append(f"  ✗ (a) two members, one agent rc={pair.returncode} done={done_pair} "
                        f"dev={h.agent_stands('agents/dev')} lead={h.agent_stands('agents/lead')} "
                        f"agents={started_p.get('agents')} launched={ {k: (v['id'], v.get('run')) for k, v in launched_p.items()} } "
                        f"first_end={first_end} paths={ {k: v.get('path') for k, v in intents_p.items()} } "
                        f"sessions={sessions_p} heads={headed_p} {pair.stderr[-200:]!r}")

    # --- (b) the neighbours line of two members of one agent quotes the neighbour's head ----------------------
    # a prompt launched while the neighbour's run plays opens on the neighbours line: the neighbour's run key,
    # and the first line of the neighbour's message -- the head naming the neighbour
    runs_p = {name: one.get("run") for name, one in launched_p.items()}
    heads_p = {name: next((line for one in h.prompts_of(name) for line in one.splitlines()
                           if re.fullmatch(head_of[name][1:-1], line)), None) for name in ("ra", "rb")}
    neighbours_p, strays_p = [], []
    for name, other in (("ra", "rb"), ("rb", "ra")):
        for one in h.prompts_of(name):
            first = one.splitlines()[0] if one else ""
            if not (runs_p.get(other) and runs_p[other] in first):
                continue                                    # no neighbour under way at its launch
            line_holds = (heads_p.get(other) and heads_p[other] in first
                          and not (runs_p.get(name) and runs_p[name] in first)
                          and name not in re.findall(r"\b(r[ab])\b", first))
            (neighbours_p if line_holds else strays_p).append(first)
    if neighbours_p and not strays_p:
        held("(b) the neighbours line names the member", f"{neighbours_p[0]!r}: the neighbour's run key and the "
             "first line of its message, the head of a team's wake-up")
    else:
        failures.append(f"  ✗ (b) neighbours line       held={neighbours_p!r} strays={strays_p!r} runs={runs_p} "
                        f"heads={heads_p}")

    # --- (c) two births of one path at once ----------------------------------------------------------------
    if all(rcs == [0, 0] and stands and mapped for _, rcs, stands, mapped, _ in raced_births):
        held("(c) two births of one path at once", "five races of two team starts on one new path: each path "
             "stands, both teams started, each journal maps its member to the path")
    else:
        failures.append(f"  ✗ (c) births raced           {raced_births}")

    # --- (d) two members of one agent in parallel, a member's two tasks in its run -----------------------------
    both = h.settled("duo", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=90)
    found_d = h.events("duo")
    d_t1, d_t2 = intents_on(found_d, "d", "T1"), intents_on(found_d, "d", "T2")
    keys_d = {one.get("run") for one in by_kind(found_d, "wake-launched", agent="d")}
    devs_d = {one.get("agent"): one for one in by_kind(found_d, "wake-launched") if one.get("agent") in ("d1", "d2")}
    first_dev_end = min((one["id"] for one in by_kind(found_d, "wake-ended") if one.get("agent") in ("d1", "d2")),
                        default=0)
    if (duo.returncode == 0 and d2_done and second_task.returncode == 0 and both
            and len(d_t1) == 2 and len(d_t2) == 1 and d_t2[0]["id"] < terminal_of(found_d, "d1")
            and len(keys_d) == 1 and d_t2[0].get("run") in keys_d
            and set(devs_d) == {"d1", "d2"} and devs_d["d1"].get("run") != devs_d["d2"].get("run")
            and all(one["id"] < first_dev_end for one in devs_d.values())
            and peak(found_d) <= 2
            and result_of(found_d, "T1") == "first" and result_of(found_d, "T2") == "second"):
        held("(d) two members of one agent in parallel", f"d1 and d2 of agents/dd launched together, two runs; d "
             f"woken on T2 (#{d_t2[0]['id']}) before d1's answer (#{terminal_of(found_d, 'd1')}), in its ONE run "
             f"{sorted(keys_d)[0]}; parallel 2 never exceeded (peak {peak(found_d)}); T1 first, T2 second")
    else:
        failures.append(f"  ✗ (d) two members, a member's two tasks  {duo.returncode}/{second_task.returncode} "
                        f"d2={d2_done} both={both} t1={[one['id'] for one in d_t1]} "
                        f"t2={[(one['id'], one.get('run')) for one in d_t2]} d1_term={terminal_of(found_d, 'd1')} "
                        f"keys={keys_d} devs={ {k: (v['id'], v.get('run')) for k, v in devs_d.items()} } "
                        f"first_dev_end={first_dev_end} peak={peak(found_d)} "
                        f"results={result_of(found_d, 'T1')!r}/{result_of(found_d, 'T2')!r} {second_task.stderr[-200:]!r}")

    # --- (e) the cursor of the member's run ----------------------------------------------------------------
    d_prompts = h.prompts_of("d")
    wake_t2 = next((one for one in d_prompts if re.search(r"^#\d+ DO from house on T2 ", one, re.M)), "")
    resume_t1 = next((one for one in d_prompts if re.search(r"^#\d+ RE #\d+ from d1 on T1$", one, re.M)), "")
    module = h.module()
    items_t2, _, since_t2, _ = T.shared_in(module, wake_t2)
    items_t1, _, since_t1, _ = T.shared_in(module, resume_t1)
    named_t2, named_t1 = [one[0] for one in items_t2], [one[0] for one in items_t1]
    if (wake_t2 and resume_t1 and d_t1 and d_t2
            and named_t2 == ["d2"] and since_t2 == d_t1[0]["id"]
            and named_t1 == ["d1"] and since_t1 == d_t2[0]["id"]):
        held("(e) the cursor of the member's run", f"d's wake-up on T2 names {named_t2} since its run's opening "
             f"(#{since_t2}); its resume on T1 names {named_t1} alone since its wake-up on T2 (#{since_t1}): "
             "what its run already read is never named twice")
    else:
        failures.append(f"  ✗ (e) cursor of the run       t2={named_t2}/{since_t2} t1={named_t1}/{since_t1} "
                        f"intents={[one['id'] for one in d_t1]}/{[one['id'] for one in d_t2]} "
                        f"{wake_t2[-300:]!r} {resume_t1[-300:]!r}")
    return 0
