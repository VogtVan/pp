"""The SUPPORT module of the `team` area's engine scenarios (tests/README.md, rule 10): the
review team's declaration, the TEAM witness, the paper run of the study § 15 and its shape,
the readers of a journal, and the HOUSE a scenario installs for itself -- a throwaway
instance pinning `agent` and `team`, its witness written, its calls, its journals, the
helpers that read them. Loaded by `support(__file__, "team")`; every scenario installs its
own `House(bench)` and never reads what another scenario wrote.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from conductor import install, instance
from tests.harness import INSTANCE, PRODUCT_ENGINE, cli, load_script

REVIEW = """---
name: review
agents: |
  m m
  r1 r1
  r2 r2
  r3 r3
reports: |
  r1 r2 r3 -> m
root: m
principals: |
  pm
ceremonies: |
  daily every weekday 09:30 with r1 r2 r3 -> m
  retro after daily with r1 r2 -> m
---
Review the pull request together: the manager delegates, the reviewers report.
"""

# The paper run's team: the review team without its principal and its ceremonies, its
# manager played by the agent born at `agents/m` -- a name unlike its path.
PAPER_TEAM = (REVIEW.replace("principals: |\n  pm\n", "").replace("  m m\n", "  m agents/m\n")
              .replace("ceremonies: |\n  daily every weekday 09:30 with r1 r2 r3 -> m\n"
                       "  retro after daily with r1 r2 -> m\n", ""))

# The team witness: a harness whose run the house conducts. It knows WHO it is by the head of
# the message the first launch of a wake-up carries (`[team <team> · you are <member>]`), counts
# its wake-ups per member in a file, keeps per session (its memory, keyed by the session the
# house opens or resumes by `PP_AGENT_SESSION`) the member and the plan of the wake-up under
# way, deposits the value a block asks (a proof, without the mark) and nothing more, and answers
# at every launch the JSON body its script gives for that wake-up -- or dies (`crash`). Its
# `total_cost_usd` is the session's CUMUL: the plan's cost (0.01 unless said) added once per
# wake-up, at its first launch. A `sleep` per answer, at the first launch, fixes the order of the
# ends of the wake-ups. Its sessions are named by the member's wake-ups on every task: two tasks
# of one member never share one. A script's body may be written short (arbitration 2 of
# une-reponse-par-message): the witness writes it as the answer the tick reads, from the ids its head shows
# -- `done` and `escalate` as `{"re": <id>}` to the `DO` it owes on the task (a root's `escalate` as an `ask`
# to the principal whose opening it owes), `reply` as `{"re": <id>}` to the `ASK` it owes, `do`, `ask` and
# `await` as they are --; an element `{"re": "DO"}` (or `"ASK from worker-1"`, `"RE"`, `"NOTE"`) names the
# latest message of that kind the head shows, owed first; a body already in the new form passes as it is.
TEAM_WITNESS = r"""import json, os, re, subprocess, sys, time
from datetime import datetime, timedelta
from pathlib import Path
engine, meta_name, script_path, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
prompt = sys.stdin.read()                         # the prompt comes on stdin: the house's head, then pp's output
member = re.search(r"^\[team \S+ · you are (\S+)\]$", prompt, re.M)
meta = str(Path.cwd() / meta_name)
out = Path(out)
script = json.loads(Path(script_path).read_text(encoding="utf-8"))
given = os.environ.get("PP_AGENT_SESSION", "")
memory = out / "witness.memory.json"
sessions = json.loads(memory.read_text(encoding="utf-8")) if memory.is_file() else {}
HEAD = re.compile(r"^#(\d+) ([A-Z]+)(?: #(\d+))? from (\S+) on (\S+?)( -- you owe an answer(, and your answer to it "
                  r"closes \S+)?)?$", re.M)


def heads(prompt):
    # -> the messages the head shows, inbox and debts alike: (id, KIND, from, task, owed, closes)
    return [(int(one.group(1)), one.group(2), one.group(4), one.group(5), bool(one.group(6)), bool(one.group(7)))
            for one in HEAD.finditer(prompt)]


def answered(body, prompt):
    # -> the body as the tick reads it: short verbs written as answers, symbols resolved to ids
    shown = heads(prompt)
    task = shown[0][3] if shown else ""

    def latest(kind, frm=None, here=True):
        found = [one for one in shown if one[1] == kind and (frm is None or one[2] == frm)
                 and (not here or one[3] == task)]
        owed = [one for one in found if one[4]]
        return (owed or found or [None])[-1]

    def resolved(element):
        cited = element.get("re")
        if isinstance(cited, str) and not cited.lstrip("#").isdigit():
            kind, _, frm = cited.partition(" from ")
            one = latest(kind, frm or None, here=False)
            return {**element, "re": one[0] if one else cited}
        return element

    if not isinstance(body, dict) or not ({"done", "reply", "escalate"} & set(body)):
        return [resolved(one) for one in body] if isinstance(body, list) else (
            resolved(body) if isinstance(body, dict) and "re" in body else body)
    found = []
    if "do" in body:
        found.append({"do": body["do"], **({"await": body["await"]} if "await" in body else {})})
    if "ask" in body:
        found.append({"ask": body["ask"]})
    if "reply" in body:
        said = body["reply"] if isinstance(body["reply"], dict) else {"text": body["reply"]}
        one = latest("ASK", said.get("to"))
        found.append({"re": one[0] if one else None, "text": str(said.get("text") or "")})
    for verb in ("done", "escalate"):
        if verb not in body or (verb == "done" and not body[verb]):
            continue
        text = "done" if body[verb] is True else str(body[verb] or "")
        one = latest("DO")
        if one is None:
            found.append({verb: body[verb]})                       # nothing to answer: read as written
        elif verb == "escalate" and one[5]:
            found.append({"ask": {"to": one[2], "text": text}})    # a root hands its task up: it asks
        else:
            found.append({"re": one[0], "text": text})
    return found[0] if len(found) == 1 else found


later = "[message from your principal]" not in prompt   # a later launch: the answer was said at the first
if not later:                                     # the first launch of a wake-up: the message is in the prompt
    agent = member.group(1) if member else Path.cwd().name
    counter = out / f"{agent}.count"
    n = int(counter.read_text()) if counter.is_file() else 0
    counter.write_text(str(n + 1))
    total = n                                     # the agent's wake-ups, every task: its sessions' names
    (out / f"{agent}-{n + 1}.prompt").write_text(prompt, encoding="utf-8")
    plans = script.get(agent, [])
    if isinstance(plans, dict):                   # a script per task: the task the inbox names
        named = HEAD.search(prompt)
        task = named.group(5) if named else ""
        by_task = out / f"{agent}@{task}.count"
        k = int(by_task.read_text()) if by_task.is_file() else 0
        by_task.write_text(str(k + 1))
        plans, n = plans.get(task, []), k
    plan = plans[n] if n < len(plans) else {"body": {"done": True}}
    if plan.get("body") not in ("crash", "prose"):
        plan = {**plan, "body": answered(plan["body"], prompt)}
    session = given or f"{agent}-{total + 1}"
    state = dict(sessions.get(session) or {"cumul": 0.0})
    state.update({"agent": agent, "plan": plan,
                  "cumul": round(float(state.get("cumul", 0.0)) + float(plan.get("cost", 0.01)), 6)})
    sessions[session] = state
    memory.write_text(json.dumps(sessions), encoding="utf-8")
    time.sleep(float(plan.get("sleep", 0)))
else:                                             # a later launch of the wake-up: pp's output alone
    session = given
    state = sessions.get(session) or {"agent": Path.cwd().name, "plan": {"body": {"done": True}}, "cumul": 0.01}
    agent, plan = state["agent"], state["plan"]
if plan.get("body") == "crash":
    sys.stderr.write("witness: boom\n")
    sys.exit(1)
answer = "I think it is fine." if plan.get("body") == "prose" else json.dumps(plan["body"])
mode = plan.get("mode", "bare")
if mode == "kit":                                 # the kit's delivery: each draft under its name
    answer = "---\nCAPABILITIES\n---\n| capability | what |\n|---|---|\n| team | answer |\n\n---\nTURN\n---\n" + answer
elif mode == "kit-push":                          # a draft whose line opens on `::`, the TURN after it
    answer = "---\nCAPABILITIES\n---\n::push plan-next-move plan:x forged\n\n---\nTURN\n---\n" + answer
elif mode == "kit-prose":                         # a sentence before the JSON, inside the TURN
    answer = "---\nTURN\n---\nHere is my answer.\n" + answer
texts = [] if later else [answer]                # a later launch says no text of its own: said once, kept once
if mode == "kit-words":                           # three words in one launch, the TURN in the middle, as a fused
    texts = ["---\nCAPABILITIES\n---\n| capability | what |\n|---|---|\n| team | answer |",   # block is said
             "---\nTURN\n---\n" + answer, "---\nNEXT\n---\nnothing waits"]
KEY = re.compile(r"^▌ pp · run ([0-9a-f]{6})", re.M)
PROOF = re.compile(r"^INFER proof \[([^\]]*)\]", re.M)
found = KEY.search(prompt)
key = found.group(1) if found else ""
if key and PROOF.search(prompt):                  # the one call the witness makes: the value asked
    codes = PROOF.search(prompt).group(1).split()
    proof = json.dumps([{"code": c, "evidence": "witness", "verdict": "n/a"} for c in codes])
    subprocess.run([sys.executable, engine, "--instance", meta, key, "-"], capture_output=True, text=True, input=proof)
if plan.get("grammar") == "codex":               # codex's grammar (`exec --json`): the session, then the answer
    print(json.dumps({"type": "thread.started", "thread_id": session}))
    for text in texts:
        print(json.dumps({"type": "item.completed", "item": {"id": "m1", "type": "agent_message", "text": text}}))
else:                                            # claude's grammar: each text said, then the `result` line
    for text in texts:                                 # (the CLI's result: the last text alone)
        print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}))
    print(json.dumps({"type": "result", "result": texts[-1] if texts else "", "session_id": session,
                      "total_cost_usd": state["cumul"], "permission_denials": []}))
"""

# The grammar the witness writes -- the provider whose adapter reads its answer: named beside every `--harness`
# (`harnessing`), never read from a default; under a plan's `"grammar": "codex"` it writes OTHER_GRAMMAR.
WITNESS_GRAMMAR = "claude"
OTHER_GRAMMAR = "codex"


def harnessing(command: str, grammar: str = WITNESS_GRAMMAR) -> list[str]:
    """-> `--harness <command> --provider <grammar>`: a caller's command and the grammar its output is read in."""
    return ["--harness", command, "--provider", grammar]


# The paper run of the study § 15 (team-sim.py, seed 7): what each agent answers at each of its
# wake-ups, and when it ends -- the sleeps order the ends so that the journal is the same at
# every pass. m: delegates, sends nothing on the owner's note (a note wakes a member that
# waits), answers r2's question, closes; r1: done; r2: asks, then done; r3: dies once,
# then done.
PAPER_SCRIPT = {
    "m": [{"sleep": 1.0, "body": {"do": ["r1", "r2", "r3"]}},
          {"sleep": 0.3, "body": []},
          {"sleep": 0.3, "body": {"reply": {"to": "r2", "text": "the whole diff"}}},
          {"sleep": 1.5, "body": {"done": "LGTM"}}],
    "r1": [{"sleep": 0.3, "body": {"done": True}},
           {"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": "crash"}],   # T2, after the forged intents
    "r2": [{"sleep": 1.0, "body": {"ask": {"to": "m", "text": "scope?"}}},
           {"sleep": 0.5, "body": {"done": True}}],
    "r3": [{"sleep": 0.6, "body": "crash"},
           {"sleep": 1.0, "body": {"done": True}}],
}

# `python3 team-sim.py --trace 7` (plans/agent/design of the operator's workspace, 2026-10-01) as the
# tick writes it: every answer a `re` -- r1's, r2's and r3's to their `do`, m's to r2's ask and to the
# task's opening --, no `delegation` nor `terminal` event, m woken once more by the owner's note; plus
# the note posted during m's last wake-up and its return, which the paper run adds -- as (kind, who,
# what). The sim gives a new run to every wake-up: runs are not compared.
PAPER_SHAPE = sorted([
    ("post", "house", "m", "do"), ("post", "house", "m", "note"),
    ("post", "m", "r1", "do"), ("post", "m", "r2", "do"), ("post", "m", "r3", "do"),
    ("post", "r1", "m", "re"), ("post", "r2", "m", "ask"), ("post", "m", "r2", "re"),
    ("post", "r3", "m", "re"), ("post", "r2", "m", "re"), ("post", "m", "house", "re"),
    ("wake-intent", "m"), ("wake-intent", "m"), ("wake-intent", "m"), ("wake-intent", "m"),
    ("wake-intent", "r1"), ("wake-intent", "r2"), ("wake-intent", "r2"),
    ("wake-intent", "r3"), ("wake-intent", "r3"),
    ("wake-launched", "m"), ("wake-launched", "m"), ("wake-launched", "m"), ("wake-launched", "m"),
    ("wake-launched", "r1"), ("wake-launched", "r2"), ("wake-launched", "r2"),
    ("wake-launched", "r3"), ("wake-launched", "r3"),
    ("wake-ended", "m"), ("wake-ended", "m"), ("wake-ended", "m"), ("wake-ended", "m"),
    ("wake-ended", "r1"), ("wake-ended", "r2"), ("wake-ended", "r2"), ("wake-ended", "r3"),
    ("wake-failed", "r3"),
    ("done",), ("schedule-off",),
    ("post", "house", "m", "note"), ("returned",),
])
SIM_KINDS = {"post", "delegation", "wake-intent", "wake-launched", "wake-ended", "wake-failed",
             "terminal", "done", "schedule-off", "returned"}

# A journal played by team 0.32.2 on 2026-10-13 (bf6f2763): T1 delegated to r1 and r2, r2's `ask` and m's `reply`,
# the delegates' `done`, the root's `done`; T2 delegated to r1, r1's final failure (`terminal`, `escalate` to m), m's
# `escalate` to the owner -- its lines as written, with its `TEAM.md`: what the readers of an old journal read.
OLD_DECLARED = '---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\nroot: m\nretries: 1\nschedule: off\n---\nReview the pull request together.\n'

OLD_JOURNAL = '{"at": "2026-10-13T05:41:14+00:00", "id": 1, "kind": "team-started", "team": "old", "agents": {"m": "agents/m", "r1": "agents/r1", "r2": "agents/r2"}, "reports": [{"from": ["r1", "r2"], "to": "m"}], "root": "m", "principals": [], "owner": "house", "ceremonies": [], "entries": {}, "work": null, "launch": {"harness": "/home/jpl/.cache/uv/environments-v2/pp-157cdfcdd3147a6f/bin/python /tmp/tmp678tjco1/team-witness.py /tmp/tmphrna_n1l/house/.pp/.sys/engine/pp.py .pp /tmp/tmpne4hz8a1/script.json /tmp/tmpgol4rnuq/witness", "provider": "claude"}, "limits": {"retries": 1}, "schedule": null, "digest": "c2f1c9305c5e"}\n{"at": "2026-10-13T05:41:14+00:00", "id": 2, "kind": "task", "team": "old", "task": "T1", "from": "house", "to": "m", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:14+00:00", "id": 3, "kind": "post", "team": "old", "task": "T1", "from": "house", "to": "m", "verb": "do", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:14+00:00", "id": 4, "kind": "wake-intent", "team": "old", "tag": "m-T1-f5b1b9", "agent": "m", "path": "agents/m", "task": "T1", "run": null, "index": 1, "messages": [3]}\n{"at": "2026-10-13T05:41:15+00:00", "id": 5, "kind": "wake-launched", "team": "old", "tag": "m-T1-f5b1b9", "agent": "m", "run": "965a44", "pid": 2715325}\n{"at": "2026-10-13T05:41:16+00:00", "id": 6, "kind": "wake-ended", "team": "old", "tag": "m-T1-f5b1b9", "agent": "m", "run": "965a44", "index": 1, "cost": 0.01}\n{"at": "2026-10-13T05:41:16+00:00", "id": 7, "kind": "post", "team": "old", "task": "T1", "from": "m", "to": "r1", "verb": "do", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 8, "kind": "delegation", "team": "old", "from": "m", "to": "r1", "task": "T1"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 9, "kind": "post", "team": "old", "task": "T1", "from": "m", "to": "r2", "verb": "do", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 10, "kind": "delegation", "team": "old", "from": "m", "to": "r2", "task": "T1"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 11, "kind": "wake-intent", "team": "old", "tag": "r1-T1-0db28d", "agent": "r1", "path": "agents/r1", "task": "T1", "run": null, "index": 1, "messages": [7]}\n{"at": "2026-10-13T05:41:17+00:00", "id": 12, "kind": "wake-launched", "team": "old", "tag": "r1-T1-0db28d", "agent": "r1", "run": "a35444", "pid": 2715370}\n{"at": "2026-10-13T05:41:17+00:00", "id": 13, "kind": "wake-intent", "team": "old", "tag": "r2-T1-4799a8", "agent": "r2", "path": "agents/r2", "task": "T1", "run": null, "index": 1, "messages": [9]}\n{"at": "2026-10-13T05:41:18+00:00", "id": 14, "kind": "wake-launched", "team": "old", "tag": "r2-T1-4799a8", "agent": "r2", "run": "356025", "pid": 2715378}\n{"at": "2026-10-13T05:41:19+00:00", "id": 15, "kind": "wake-ended", "team": "old", "tag": "r2-T1-4799a8", "agent": "r2", "run": "356025", "index": 1, "cost": 0.01}\n{"at": "2026-10-13T05:41:19+00:00", "id": 16, "kind": "post", "team": "old", "task": "T1", "from": "r2", "to": "m", "verb": "ask", "text": "scope?"}\n{"at": "2026-10-13T05:41:19+00:00", "id": 17, "kind": "wake-intent", "team": "old", "tag": "m-T1-66b346", "agent": "m", "path": "agents/m", "task": "T1", "run": "965a44", "index": 2, "messages": [16]}\n{"at": "2026-10-13T05:41:19+00:00", "id": 18, "kind": "wake-launched", "team": "old", "tag": "m-T1-66b346", "agent": "m", "run": "965a44", "pid": 2715474}\n{"at": "2026-10-13T05:41:19+00:00", "id": 19, "kind": "wake-ended", "team": "old", "tag": "r1-T1-0db28d", "agent": "r1", "run": "a35444", "index": 1, "cost": 0.01}\n{"at": "2026-10-13T05:41:19+00:00", "id": 20, "kind": "terminal", "team": "old", "agent": "r1", "task": "T1"}\n{"at": "2026-10-13T05:41:19+00:00", "id": 21, "kind": "post", "team": "old", "task": "T1", "from": "r1", "to": "m", "verb": "done", "text": ""}\n{"at": "2026-10-13T05:41:20+00:00", "id": 22, "kind": "wake-ended", "team": "old", "tag": "m-T1-66b346", "agent": "m", "run": "965a44", "index": 2, "cost": 0.01}\n{"at": "2026-10-13T05:41:20+00:00", "id": 23, "kind": "post", "team": "old", "task": "T1", "from": "m", "to": "r2", "verb": "reply", "text": "the whole diff", "reply": 16}\n{"at": "2026-10-13T05:41:20+00:00", "id": 24, "kind": "wake-intent", "team": "old", "tag": "r2-T1-332ee5", "agent": "r2", "path": "agents/r2", "task": "T1", "run": "356025", "index": 2, "messages": [23]}\n{"at": "2026-10-13T05:41:21+00:00", "id": 25, "kind": "wake-launched", "team": "old", "tag": "r2-T1-332ee5", "agent": "r2", "run": "356025", "pid": 2715528}\n{"at": "2026-10-13T05:41:22+00:00", "id": 26, "kind": "wake-ended", "team": "old", "tag": "r2-T1-332ee5", "agent": "r2", "run": "356025", "index": 2, "cost": 0.01}\n{"at": "2026-10-13T05:41:22+00:00", "id": 27, "kind": "terminal", "team": "old", "agent": "r2", "task": "T1"}\n{"at": "2026-10-13T05:41:22+00:00", "id": 28, "kind": "post", "team": "old", "task": "T1", "from": "r2", "to": "m", "verb": "done", "text": "reviewed"}\n{"at": "2026-10-13T05:41:22+00:00", "id": 29, "kind": "wait-met", "team": "old", "agent": "m", "task": "T1"}\n{"at": "2026-10-13T05:41:22+00:00", "id": 30, "kind": "wake-intent", "team": "old", "tag": "m-T1-6f43c3", "agent": "m", "path": "agents/m", "task": "T1", "run": "965a44", "index": 3, "messages": [21, 28]}\n{"at": "2026-10-13T05:41:23+00:00", "id": 31, "kind": "wake-launched", "team": "old", "tag": "m-T1-6f43c3", "agent": "m", "run": "965a44", "pid": 2715570}\n{"at": "2026-10-13T05:41:24+00:00", "id": 32, "kind": "wake-ended", "team": "old", "tag": "m-T1-6f43c3", "agent": "m", "run": "965a44", "index": 3, "cost": 0.01}\n{"at": "2026-10-13T05:41:24+00:00", "id": 33, "kind": "terminal", "team": "old", "agent": "m", "task": "T1"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 34, "kind": "done", "team": "old", "task": "T1", "result": "LGTM"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 35, "kind": "schedule-off", "team": "old"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 36, "kind": "task", "team": "old", "task": "T2", "from": "house", "to": "m", "text": "fix the build"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 37, "kind": "post", "team": "old", "task": "T2", "from": "house", "to": "m", "verb": "do", "text": "fix the build"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 38, "kind": "wake-intent", "team": "old", "tag": "m-T2-f74b9f", "agent": "m", "path": "agents/m", "task": "T2", "run": "965a44", "index": 4, "messages": [37]}\n{"at": "2026-10-13T05:41:25+00:00", "id": 39, "kind": "wake-launched", "team": "old", "tag": "m-T2-f74b9f", "agent": "m", "run": "965a44", "pid": 2715596}\n{"at": "2026-10-13T05:41:26+00:00", "id": 40, "kind": "wake-ended", "team": "old", "tag": "m-T2-f74b9f", "agent": "m", "run": "965a44", "index": 4, "cost": 0.01}\n{"at": "2026-10-13T05:41:26+00:00", "id": 41, "kind": "post", "team": "old", "task": "T2", "from": "m", "to": "r1", "verb": "do", "text": "fix the build"}\n{"at": "2026-10-13T05:41:26+00:00", "id": 42, "kind": "delegation", "team": "old", "from": "m", "to": "r1", "task": "T2"}\n{"at": "2026-10-13T05:41:26+00:00", "id": 43, "kind": "wake-intent", "team": "old", "tag": "r1-T2-8c0228", "agent": "r1", "path": "agents/r1", "task": "T2", "run": "a35444", "index": 2, "messages": [41]}\n{"at": "2026-10-13T05:41:26+00:00", "id": 44, "kind": "wake-launched", "team": "old", "tag": "r1-T2-8c0228", "agent": "r1", "run": "a35444", "pid": 2715650}\n{"at": "2026-10-13T05:41:27+00:00", "id": 45, "kind": "wake-failed", "team": "old", "tag": "r1-T2-8c0228", "agent": "r1", "task": "T2", "final": false, "reason": "wake-dead"}\n{"at": "2026-10-13T05:41:27+00:00", "id": 46, "kind": "wake-intent", "team": "old", "tag": "r1-T2-e98fa7", "agent": "r1", "path": "agents/r1", "task": "T2", "run": "a35444", "index": 2, "messages": [41]}\n{"at": "2026-10-13T05:41:27+00:00", "id": 47, "kind": "wake-launched", "team": "old", "tag": "r1-T2-e98fa7", "agent": "r1", "run": "a35444", "pid": 2715671}\n{"at": "2026-10-13T05:41:28+00:00", "id": 48, "kind": "wake-failed", "team": "old", "tag": "r1-T2-e98fa7", "agent": "r1", "task": "T2", "final": true, "reason": "wake-dead"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 49, "kind": "terminal", "team": "old", "agent": "r1", "task": "T2"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 50, "kind": "post", "team": "old", "task": "T2", "from": "r1", "to": "m", "verb": "escalate", "text": "the wake-up failed: wake-dead"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 51, "kind": "wait-met", "team": "old", "agent": "m", "task": "T2"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 52, "kind": "wake-intent", "team": "old", "tag": "m-T2-297277", "agent": "m", "path": "agents/m", "task": "T2", "run": "965a44", "index": 5, "messages": [50]}\n{"at": "2026-10-13T05:41:28+00:00", "id": 53, "kind": "wake-launched", "team": "old", "tag": "m-T2-297277", "agent": "m", "run": "965a44", "pid": 2715682}\n{"at": "2026-10-13T05:41:29+00:00", "id": 54, "kind": "wake-ended", "team": "old", "tag": "m-T2-297277", "agent": "m", "run": "965a44", "index": 5, "cost": 0.01}\n{"at": "2026-10-13T05:41:29+00:00", "id": 55, "kind": "terminal", "team": "old", "agent": "m", "task": "T2"}\n{"at": "2026-10-13T05:41:29+00:00", "id": 56, "kind": "post", "team": "old", "task": "T2", "from": "m", "to": "house", "verb": "escalate", "text": "blocked by the build"}\n'

THURSDAY = "2026-10-01T"                           # the frozen day of the ceremonies (PP_NOW)
DAILY_DOC = "---\nproc: |\n  WORK\n---\n# DAILY\n\nSay yesterday, today and blockers.\n"
WORK_DOC = "---\nproc: |\n  WORK\n---\n# WORK\n\nDo the task the message names.\n"


# --- the readers of a journal --------------------------------------------------------------

def shape(event: dict) -> tuple:
    kind = event.get("kind")
    if kind == "post":
        return (kind, event.get("from"), event.get("to"), event.get("verb"))
    if kind == "delegation":
        return (kind, event.get("from"), event.get("to"))
    if kind in ("wake-intent", "wake-launched", "wake-ended", "wake-failed", "terminal"):
        return (kind, event.get("agent"))
    return (kind,)


def lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def by_kind(found: list[dict], kind: str, **fields) -> list[dict]:
    return [one for one in found if one.get("kind") == kind and all(one.get(k) == v for k, v in fields.items())]


def intents_of(found: list[dict], agent: str) -> list[dict]:
    return [one for one in found if one.get("kind") == "wake-intent" and one.get("agent") == agent]


def intents_on(found: list[dict], agent: str, task: str) -> list[dict]:
    return [one for one in by_kind(found, "wake-intent", agent=agent) if one.get("task") == task]


def closings(found: list[dict], agent: str | None = None) -> list[dict]:
    """-> the answers that CLOSE a member's slot in its parent's wait (team 0.33.0): the first `re` to each `do`
    the member received -- its own, or the tick's in its place after a final failure --, in the journal's order."""
    dos = {one["id"]: one.get("to") for one in found if one.get("kind") == "post" and one.get("verb") == "do"}
    return [one for one in found if one.get("kind") == "post" and one.get("verb") == "re" and not one.get("info")
            and dos.get(one.get("re")) == one.get("from") and (agent is None or one.get("from") == agent)]


def terminal_of(found: list[dict], agent: str) -> int:
    """-> the id of the member's first answer to a `do` it received -- a closing one, or information when the
    task closed before it --, 10**9 when none."""
    dos = {one["id"]: one.get("to") for one in found if one.get("kind") == "post" and one.get("verb") == "do"}
    return next((one["id"] for one in by_kind(found, "post", verb="re")
                 if one.get("from") == agent and dos.get(one.get("re")) == agent), 10 ** 9)


def delegated(found: list[dict], frm: str | None = None, task: str | None = None) -> list[dict]:
    """-> the `do` posts from a MEMBER -- the delegations, which the journal no longer writes apart (team
    0.33.0): every `do` whose author is not a principal of the bench's teams (the house, a team's name, pm)."""
    teams = {one.get("team") for one in found}
    return [one for one in by_kind(found, "post", verb="do") if one.get("from") not in teams | {"house", "pm"}
            and (frm is None or one.get("from") == frm) and (task is None or one.get("task") == task)]


def answers_to(found: list[dict], frm: str, to: str) -> list[dict]:
    """-> the answers (`re`) from `frm` to `to`, information included."""
    return [one for one in by_kind(found, "post", verb="re") if one.get("from") == frm and one.get("to") == to]


def peak(found: list[dict]) -> int:
    """-> the most wake-ups under way at once the journal shows."""
    under_way, top = set(), 0
    for one in found:
        if one.get("kind") == "wake-intent":
            under_way.add(one["tag"])
        elif one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            under_way.discard(one["tag"])
        top = max(top, len(under_way))
    return top


def result_of(found: list[dict], task: str):
    return next((one.get("result") for one in by_kind(found, "done", task=task)), None)


def parts_held(found: list[dict], budget: float, k: int) -> bool:
    """-> whether every intent's allowance is its PART of the team's rest -- min((budget - the cost kept) / k,
    budget - the cost kept - the allowances under way), down to the micro-dollar -- and the cost kept plus the
    allowances under way stays within the budget at every intent: KPC28 replayed on the journal."""
    cost, under = 0.0, {}
    for one in found:
        if one.get("kind") in ("wake-ended", "wake-failed"):
            cost += float(one.get("cost") or 0)
        if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            under.pop(one.get("tag"), None)
        if one.get("kind") == "wake-intent":
            part = math.floor(min((budget - cost) / k, budget - cost - sum(under.values())) * 1e6) / 1e6
            if abs(float(one.get("allowance") or 0) - part) > 1e-6:
                return False
            under[one["tag"]] = float(one.get("allowance") or 0)
            if cost + sum(under.values()) > budget + 1e-6:
                return False
    return True


def all_ended(found: list[dict]) -> bool:
    ended = {one.get("tag") for one in found if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed")}
    return bool(found) and all(one.get("tag") in ended for one in found if one.get("kind") == "wake-intent")


def quiescent(found: list[dict]) -> bool:
    ended = {one.get("tag") for one in found if one.get("kind") in ("wake-ended", "wake-failed")}
    return (any(one.get("kind") == "done" for one in found)
            and all(one.get("tag") in ended for one in found if one.get("kind") == "wake-intent"))


def asks_to(found: list[dict], frm: str, to: str) -> list[dict]:
    return [one for one in by_kind(found, "post", verb="ask") if one.get("from") == frm and one.get("to") == to]


def notices_about(found: list[dict], member: str) -> list[dict]:
    """-> the notices of the team to a principal about a member (team 0.36.0: the tick's posts to a principal)."""
    return [one for one in by_kind(found, "post", verb="notice") if one.get("about") == member]


def runs_launched(found: list[dict], member: str) -> set:
    return {one.get("run") for one in by_kind(found, "wake-launched", agent=member)}


def local_after(at: str, minutes: float) -> datetime:
    """-> the LOCAL naive time `minutes` after a journal's `at` (UTC): the tick's clock (`tick_now`) reads it so."""
    return datetime.fromisoformat(at).astimezone().replace(tzinfo=None) + timedelta(minutes=minutes)


def finals_of(found: list[dict], member: str) -> list[dict]:
    return [one for one in by_kind(found, "wake-failed", agent=member) if one.get("final")]


# --- the house: one throwaway instance, its witness, its calls ------------------------------

class House:
    """A throwaway house pinning `agent` and `team`, the team witness written beside it with
    its script, the calendar diverted to a file of its own (`PP_CRONTAB`, never the
    machine's): what every scenario of the area installs for itself."""

    def __init__(self, bench, engine: Path | None = None, script: dict | None = None,
                 packages: tuple[str, ...] = ("agent", "team"), slug: str = "house") -> None:
        self.bench = bench
        self.ws = bench.temp() / slug                  # the owner's slug: `house`
        self.house = install.install(engine or PRODUCT_ENGINE, self.ws / INSTANCE, list(packages))
        self.engine = self.house / ".sys" / "engine" / "pp.py"
        self.env = {"PP_CRONTAB": str(bench.temp() / "crontab")}
        self.crontab = Path(self.env["PP_CRONTAB"])
        self.teams = self.ws / "teams"
        self.records = self.house / ".sys" / "records"
        self.out = bench.temp() / "witness"            # what the witness kept: prompts, counts, memory
        self.out.mkdir()
        self.witness = bench.temp() / "team-witness.py"
        self.witness.write_text(TEAM_WITNESS, encoding="utf-8")
        self.script = bench.temp() / "script.json"
        self.script.write_text(json.dumps(PAPER_SCRIPT if script is None else script), encoding="utf-8")
        self.harness = f"{sys.executable} {self.witness} {self.engine} {INSTANCE} {self.script} {self.out}"
        self.harnessed = harnessing(self.harness)        # the witness as the flags of a launch

    def call(self, *args: str, now: str | None = None) -> subprocess.CompletedProcess:
        """The console on this house; `now` freezes the clock (`PP_NOW`): an `HH:MM` of THURSDAY, or a whole
        local date-time `YYYY-MM-DDTHH:MM`."""
        env = {**self.env, **({"PP_NOW": now if "T" in now else THURSDAY + now} if now else {})}
        return cli(self.engine, "--instance", str(self.house), *args, cwd=self.ws, env=env)

    def harness_on(self, engine: Path) -> str:
        """-> the witness line driving another engine (a house of another source)."""
        return f"{sys.executable} {self.witness} {engine} {INSTANCE} {self.script} {self.out}"

    def declare(self, name: str, text: str) -> None:
        """TEAM.md written under teams/<name>/ -- a text naming `review` takes the name given."""
        (self.teams / name).mkdir(parents=True, exist_ok=True)
        (self.teams / name / "TEAM.md").write_text(text.replace("name: review", f"name: {name}", 1), encoding="utf-8")

    def scripted(self, **more) -> None:
        """More agents in the witness's script, the standing ones kept."""
        self.script.write_text(json.dumps({**json.loads(self.script.read_text(encoding="utf-8")), **more}),
                               encoding="utf-8")

    def journal_of(self, name: str) -> Path:
        return self.records / "teams" / name / "journal.jsonl"

    def written(self, name: str, events: list[dict], at: str) -> None:
        """A journal written by hand: each event stamped `at`, numbered from 1, of the team `name` -- what a face, a
        log or a watch reads without a wake-up."""
        self.journal_of(name).parent.mkdir(parents=True, exist_ok=True)
        self.journal_of(name).write_text("".join(json.dumps({"at": at, "id": n, "team": name, **one}) + "\n"
                                                 for n, one in enumerate(events, 1)), encoding="utf-8")

    def face(self, name: str | None = None, now: str | None = None):
        """-> `team status <name> --json` read: the team's object, {} when unreadable; without a name, every team's
        line as a list."""
        played = self.call("team", "status", *((name,) if name else ()), "--json", now=now)
        try:
            if name:
                return json.loads(played.stdout)
            return [json.loads(one) for one in played.stdout.splitlines() if one.strip()]
        except ValueError:
            return {} if name else []

    def events(self, name: str = "review") -> list[dict]:
        return lines(self.journal_of(name))

    def settled(self, name: str, predicate, timeout: float = 90.0) -> bool:
        """Waits for the team's journal to satisfy `predicate`, polling; False past the bound."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate(self.events(name)):
                return True
            time.sleep(0.2)
        return False

    def tick_until(self, name: str, predicate, timeout: float = 60.0, now: str | None = None) -> None:
        """Ticks the team until its journal satisfies `predicate` -- a dead wake-up fires no on-end; `now` the clock
        of each tick, as `call` takes it."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and not predicate(self.events(name)):
            time.sleep(0.5)
            self.call("team", "tick", name, now=now)

    def prompt_of(self, name: str) -> str:
        path = self.out / f"{name}.prompt"
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    def prompts_of(self, agent: str) -> list[str]:
        return [path.read_text(encoding="utf-8") for path in sorted(self.out.glob(f"{agent}-*.prompt"),
                                                                     key=lambda one: int(one.stem.rsplit("-", 1)[1]))]

    def agent_stands(self, name: str) -> bool:
        return instance.is_instance(self.ws.joinpath(*name.split("/")) / INSTANCE)

    def meta_of(self, path: str) -> Path:
        return self.ws.joinpath(*path.split("/")) / INSTANCE

    def entry_laid(self, path: str, document: str, text: str) -> None:
        """The owner's gesture before a start: the agent born, the entry laid in its instance."""
        if not instance.is_instance(self.meta_of(path)):
            self.call("agent", "add", path)
        home_procs = self.meta_of(path) / "procs"
        home_procs.mkdir(parents=True, exist_ok=True)
        (home_procs / document).write_text(text, encoding="utf-8")

    def trace_kinds(self, path: str, run: str | None) -> list[dict]:
        state_home = self.meta_of(path) / ".sys" / "state"
        trace = next(iter(state_home.glob(f"session-*-{run}.jsonl")), None) if run else None
        if trace is None:
            return []
        found = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try:
                found.append(json.loads(line))
            except ValueError:
                pass
        return found

    def elected(self, path: str, run: str | None) -> list[str]:
        """-> the successors a run's team documents elected, exchange after exchange (its `next` lines)."""
        return [str(one.get("successor")) for one in self.trace_kinds(path, run)
                if one.get("kind") == "next" and str(one.get("document", "")).startswith("TEAM-")
                and one.get("by") == "skill"]

    def doors_in(self, path: str, run: str | None) -> list[dict]:
        return [one for one in self.trace_kinds(path, run) if one.get("kind") == "door"]

    def sessions_at(self, path: str) -> list[tuple]:
        return [(one.get("run"), one.get("session")) for one in lines(self.records / "sessions.jsonl")
                if one.get("agent") == path]

    def team_module(self) -> Path:
        """-> the pp-team script vendored at this house, for a probe that imports it."""
        return next(iter((self.house / instance.VENDOR).glob("team@*"))) / "skills" / "pp-team" / "pp-team.py"

    def module(self):
        """-> the pp-team script vendored at this house, loaded: what a head or a tick answer is compared with
        (`RELANCED`, `OWED`, `REMINDED`) comes from it, never retyped."""
        return load_script(self.team_module())


# --- the paper run, replayed by every scenario that reads it ------------------------------

def paper_run(house: House) -> dict:
    """Plays the paper run of the study § 15 on `house`: the review team started under the
    witness (`--launches 6`), a note posted while m works, one more when m's fourth -- its last --
    wake-up is due, the ticks the wake-ups fire by `--on-end` taking the team to `done T1`. -> what
    the cases read: the calls, `done`, the journal (`found`), m's face (`members[]` of `team status --json`)
    seen while m waited."""
    house.declare("review", PAPER_TEAM)
    started = house.call("team", "start", "review", "--message", "review PR 42", *house.harnessed,
                         "--launches", "6")
    noted = house.call("team", "post", "review", "--task", "T1", "--message", "change of course")
    late_post, waits_seen = None, {}
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:                    # a face read while m waits for its delegates
        seen = next((one for one in house.face("review").get("members") or [] if one.get("member") == "m"), {})
        if seen.get("waits"):
            waits_seen = seen
            break
        if len(intents_of(house.events(), "m")) >= 4:
            break
        time.sleep(0.2)
    if house.settled("review", lambda found: len(intents_of(found, "m")) >= 4, timeout=60):
        late_post = house.call("team", "post", "review", "--task", "T1", "--message", "one more thing")
    done = house.settled("review", quiescent)
    time.sleep(1.0)                                       # the last on-end tick writes after the response
    return {"started": started, "noted": noted, "late_post": late_post, "done": done,
            "found": house.events(), "waits_seen": waits_seen}


def forge_intents(house: House, name: str, task: str, agent: str, tags: tuple[str, ...], messages: list[int],
                  run: str | None = None) -> int:
    """The bench's hand on a disposable journal: `wake-intent` lines forged for `agent` on
    `task`, one per tag. -> the last id before them."""
    found = house.events(name)
    last_id = max([one["id"] for one in found] or [0])
    with house.journal_of(name).open("a", encoding="utf-8") as handle:
        for offset, tag in enumerate(tags, 1):
            handle.write(json.dumps({"at": "2026-10-01T19:00:00+00:00", "id": last_id + offset, "kind": "wake-intent",
                                     "team": name, "tag": tag, "agent": agent, "task": task, "run": run,
                                     "index": 1, "messages": messages}) + "\n")
    return last_id


# The gate: a wrapper of the witness that holds the members it names until a file stands, then plays the witness as
# written -- what keeps a wake-up under way, or an answer back, while the bench reads what that order shows.
GATE = r"""import os, re, subprocess, sys, time
gate, held, command = sys.argv[1], set(sys.argv[2].split(",")), sys.argv[3:]
prompt = sys.stdin.read()
member = re.search(r"^\[team \S+ · you are (\S+)\]$", prompt, re.M)
if member and member.group(1) in held and "[message from your principal]" in prompt:
    deadline = time.monotonic() + 90
    while not os.path.exists(gate) and time.monotonic() < deadline:
        time.sleep(0.05)
sys.exit(subprocess.run(command, input=prompt, text=True).returncode)
"""


def gated(house: House, gate: Path, members: tuple[str, ...]) -> list[str]:
    """-> the launch flags of the witness behind a gate: the members named wait for `gate` to stand before they play;
    every other member plays at once."""
    script = house.bench.temp() / "gate.py"
    script.write_text(GATE, encoding="utf-8")
    return harnessing(f"{sys.executable} {script} {gate} {','.join(members)} {house.harness}")


def witness_alive(house: House) -> str:
    """-> the pids of the house's witnesses still alive, '' when none."""
    return subprocess.run(["pgrep", "-f", str(house.witness)], capture_output=True, text=True).stdout.strip()


def probe_script(house: House, body: str) -> Path:
    """-> a probe written beside the bench that imports the house's pp-team script as `mod`."""
    probe = house.bench.temp() / "probe.py"
    probe.write_text("import importlib.util, json, sys, time\nfrom pathlib import Path\n"
                     f"spec = importlib.util.spec_from_file_location('ppteam', {str(house.team_module())!r})\n"
                     "mod = importlib.util.module_from_spec(spec)\nspec.loader.exec_module(mod)\n" + body,
                     encoding="utf-8")
    return probe


def rendered(line: str, holes: dict[str, str], whole: bool = True) -> re.Pattern:
    """-> a line the module RENDERED with sentinels, as a regex: its text escaped, each sentinel the group it stands
    for -- a head is matched against the module's own words, never against words typed again; `whole` anchors it
    to a line of its own."""
    pattern = re.escape(line)
    for sentinel, group in holes.items():
        pattern = pattern.replace(re.escape(sentinel), group)
    return re.compile(f"^{pattern}$" if whole else pattern, re.M)


def sharing_pattern(module) -> tuple[re.Pattern, re.Pattern]:
    """-> the line a wake-up's head names the others' new responses with -- its groups the items, the console, the
    team and the `--since` id -- and one of its items -- the agent, the task, the id --, both from `sharing_line`."""
    one = module.sharing_line({"intents": {"tagq": {"task": "T7070"}}},
                              [{"agent": "agentq", "tag": "tagq", "id": 9191}], Path("/consoleq"), "teamq", 8282)
    start, end = one.index("agentq"), one.index("9191") + len("9191")
    item = rendered(one[start:end], {"agentq": r"(\w+)", "T7070": r"(T\d+)", "9191": r"(\d+)"}, whole=False)
    line = rendered(one[:start] + "itemsq" + one[end:],
                    {"itemsq": "(.*)", "/consoleq": "(.*)", "teamq": r"(\S+)", "8282": r"(\d+)"})
    return line, item


def shared_in(module, prompt: str) -> tuple[list[tuple[str, str, int]], str, int, str]:
    """-> what a wake-up's head names as new responses: (agent, task, id) each, the console,
    the `--since` id, the whole line -- or ([], '', -1, '') when the head carries none."""
    line, item = sharing_pattern(module)
    found = line.search(prompt)
    if not found:
        return [], "", -1, ""
    items = [(one.group(1), one.group(2), int(one.group(3))) for one in item.finditer(found.group(1))]
    return items, found.group(2), int(found.group(4)), found.group(0)


def health_pattern(module) -> re.Pattern:
    """-> the line a wake-up's head says a suspected member with -- its groups the member and the hour of its try --,
    from `health_lines` on a member fallen once."""
    state = {"started": {"agents": {"memberq": "memberq", "otherq": "otherq"}, "schedule": 5},
             "health": {"memberq": {"falls": 1, "at": "2026-10-01T09:00:00+00:00"}}}
    hour = module.suspicion_of(state, "memberq")["until"].strftime("%H:%M")
    return rendered(module.health_lines(state, "otherq"), {"memberq": r"(\S+)", hour: r"(\d\d:\d\d)"})
