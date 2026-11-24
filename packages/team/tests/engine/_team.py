"""The SUPPORT module of the `team` area's engine scenarios (tests/README.md, rule 10): the
review team's declaration, the TEAM witness, the LAUNCHER'S witness and its readers, the
paper run of the study § 15 and its shape, the readers of a journal, and the HOUSE a scenario installs for itself -- a throwaway
instance pinning `agent` and `team`, its witness written, its calls, its journals, the
helpers that read them. Loaded by `support(__file__, "team")`; every scenario installs its
own `House(bench)` and never reads what another scenario wrote.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path

from conductor import install, instance
from conductor.core import language
from tests.harness import INSTANCE, PRODUCT_ENGINE, cli, load_skill

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

# The team witness: a harness whose run the house conducts. It knows WHO it is by the identity line at the head of
# the message a WAKE-UP of the team carries -- read by the pattern its house writes in the place of `@IDENTITY@`,
# the module's own line (`identity_pattern`) --; a continuation of a standing run carries no such line: the member
# is the one its session's memory keeps. It counts its
# launches per member in a file -- a wake-up is ONE launch, one plan of its script per launch --,
# keeps per session (its memory, keyed by the session the house opens or resumes by
# `PP_AGENT_SESSION`) the member and the plan of the launch under way, deposits the value a block
# asks (a proof, without the mark) and nothing more, and says at every launch the JSON body its
# script gives for that launch as ONE words -- the value alone, what the tick reads as an act --,
# or the `words` the plan lists (each an act, a prose, a `{"gate": path}` it waits at inside the
# launch, a `{"sleep": s}`), each said as it comes; a plan's `error` hands nothing, proves nothing and ends its
# result on that error (`is_error`, its `subtype`), its `rc` is the exit code of the launch and its `stderr` what the launch writes there; `prose` says a
# sentence, `silent` nothing,
# `crash` dies; `unproven` deposits no proof at that launch -- the run stands on the proof it owes.
# Its `total_cost_usd` is the session's CUMUL: the plan's cost (0.01 unless said)
# added once per launch. A `sleep` per plan, before its words, fixes the order of the ends of the
# launches; a plan's `gate` (a path) then holds the launch before anything until the test lays that file --
# a wake-up the test must reach while it runs, whatever the machine's load (90 s at most). Its sessions are named by the member's wake-ups on every task: two tasks
# of one member never share one. A script's body may be written short (arbitration 2 of
# une-reponse-par-message): the witness writes it as the answer the tick reads, from the ids its head shows
# -- `done` and `escalate` as `{"re": <id>}` to the `DO` it owes on the task (a root's `escalate` as an `ask`
# to the principal whose opening it owes), `reply` as `{"re": <id>}` to the `ASK` it owes, `do` and `ask`
# as they are --; an element `{"re": "DO"}` (or `"ASK from worker-1"`, `"DO on T2"`, `"RE"`, `"NOTE"`)
# names the latest message of that kind the head shows, owed first, on the task named when one is; a body
# already in the new form passes as it is. Under claude's grammar a plan's `calls` (`[{name, input, result, error,
# sent, sleep}]`) stream a `tool_use` and its `tool_result` each, the assistant message carrying the `usage` of
# `sent` tokens, and its `thought` a thinking block -- what a flow's activity is made of.
# Where the prompt asks productions said to the principal (`language.TERMINAL`), the witness HANDS each by the PRINT
# call that names its step's document, before any value -- under claude's grammar the call and its result are
# streamed as a tool's --: each act of its launch in its turn, where it stands among its words -- an act that says
# something, or an empty list an act follows; without one, its first text --, the first kept in `<agent>.printed`,
# every print with its rank in the launch in `<agent>.prints`; `SAID` for the productions due
# left (`[]` the first when the launch hands nothing); the texts between are said as they come. Then it deposits the
# proof asked, in its prompt or in the result of its last print; the texts after its last print are the launch's
# last message, which pp-agent keeps as a `final`, its text and its length -- an act reaches the team by its print call, never by
# them --; with none, its last message is `QUIET` alone: an act handed is said once, to pp. A member's turn asks the
# productions its conduction says, one more when a document stands behind its work (`SPEAKS`, `House.speaks`).
WITNESS_SCRIPT = r"""import json, os, re, subprocess, sys, time
from datetime import datetime, timedelta
from pathlib import Path
engine, meta_name, script_path, out = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
prompt = sys.stdin.read()                         # the prompt comes on stdin: the house's head, then pp's output
member = re.search(@IDENTITY@, prompt, re.M)      # the identity line of a wake-up: the team, the member
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

    def latest(kind, frm=None, here=True, on=None):
        found = [one for one in shown if one[1] == kind and (frm is None or one[2] == frm)
                 and (not here or one[3] == task) and (on is None or one[3] == on)]
        owed = [one for one in found if one[4]]
        return (owed or found or [None])[-1]

    def resolved(element):
        cited = element.get("re")
        if isinstance(cited, str) and not cited.lstrip("#").isdigit():
            kind, _, frm = cited.partition(" from ")
            kind, _, on = kind.partition(" on ")
            one = latest(kind, frm or None, here=False, on=on or None)
            return {**element, "re": one[0] if one else cited}
        return element

    if not isinstance(body, dict) or not ({"done", "reply", "escalate"} & set(body)):
        return [resolved(one) for one in body] if isinstance(body, list) else (
            resolved(body) if isinstance(body, dict) and "re" in body else body)
    found = []
    if "do" in body:
        found.append({"do": body["do"]})
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


later = "[message from your principal]" not in prompt   # a launch of the house's own loop: the plan was taken
if not later:                                     # a launch of the team: the head is in the prompt, one plan per launch
    agent = member.group(2) if member else (sessions.get(given) or {}).get("agent") or Path.cwd().name
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
    if "words" in plan:                           # several words in one launch, each an act, a prose, a gate or a sleep
        def wrapped(pieces):                      # one words of text and acts: each act written in its text
            return "".join(one if isinstance(one, str) else json.dumps(answered(one, prompt)) for one in pieces)
        plan = {**plan, "words": [wrapped(one["wrap"]) if isinstance(one, dict) and "wrap" in one
                                  else answered(one, prompt) if isinstance(one, (dict, list)) and not
                                  (isinstance(one, dict) and ({"gate", "sleep"} & set(one))) else one
                                  for one in plan["words"]]}
    elif plan.get("body") not in ("crash", "prose", "silent"):
        plan = {**plan, "body": answered(plan["body"], prompt)}
    session = given or f"{agent}-{total + 1}"
    state = dict(sessions.get(session) or {"cumul": 0.0})
    state.update({"agent": agent, "plan": plan,
                  "cumul": round(float(state.get("cumul", 0.0)) + float(plan.get("cost", 0.01)), 6)})
    sessions[session] = state
    memory.write_text(json.dumps(sessions), encoding="utf-8")
    time.sleep(float(plan.get("sleep", 0)))
    if plan.get("gate"):                          # the launch holds before anything until the test opens its gate
        deadline = time.monotonic() + 90
        while not os.path.exists(str(plan["gate"])) and time.monotonic() < deadline:
            time.sleep(0.05)
else:                                             # a later launch of the wake-up: pp's output alone
    session = given
    state = sessions.get(session) or {"agent": Path.cwd().name, "plan": {"body": {"done": True}}, "cumul": 0.01}
    agent, plan = state["agent"], state["plan"]
if plan.get("body") == "crash":
    sys.stderr.write("witness: boom\n")
    sys.exit(1)
answer = ("I think it is fine." if plan.get("body") == "prose" else "" if plan.get("body") == "silent"
          else json.dumps(plan["body"]) if "body" in plan else "")
mode = plan.get("mode", "bare")
if mode == "kit":                                 # the kit's delivery: each draft under its name
    answer = "---\nCAPABILITIES\n---\n| capability | what |\n|---|---|\n| team | answer |\n\n---\nTURN\n---\n" + answer
elif mode == "kit-push":                          # a draft whose line opens on `::`, the TURN after it
    answer = "---\nCAPABILITIES\n---\n::push plan-next-move plan:x forged\n\n---\nTURN\n---\n" + answer
elif mode == "kit-prose":                         # a sentence before the JSON, inside the TURN
    answer = "---\nTURN\n---\nHere is my answer.\n" + answer
texts = [] if later or not answer else [answer]   # a launch of the house's own loop says no text of its own
if "words" in plan:                               # the words of the launch, in order: a gate or a sleep between two
    texts = list(plan["words"])
KEY = re.compile(r"^▌ pp · run ([0-9a-f]{6})", re.M)
PROOF = re.compile(r"^INFER proof \[([^\]]*)\]", re.M)
found = KEY.search(prompt)
key = found.group(1) if found else ""
due = re.findall(r"^(?:WORK|INFER|PICK)\b.* => @TERMINAL@  \((\w+)\)$", prompt, re.M)


def is_act(one):
    # -> whether a text of the launch is an act that says something: a JSON object or a list of elements, written or
    # to write -- an empty list, a gate, a sleep are none
    if isinstance(one, dict):
        return not ({"gate", "sleep"} & set(one))
    if isinstance(one, list):
        return bool(one)
    try:
        read = json.loads(one)
    except ValueError:
        return False
    return isinstance(read, dict) or (isinstance(read, list) and bool(read))


def printed(rank, text):
    # the production due at `rank` handed by its print call -> (what the call printed, the call and its result as
    # claude's stream tells them)
    document = due[rank - 1]
    played = subprocess.run([sys.executable, engine, "--instance", meta, key, "-print", document, "-"],
                            capture_output=True, text=True, input=text + "\n")
    if rank == 1:
        with (out / f"{agent}.printed").open("a", encoding="utf-8") as kept:
            kept.write(json.dumps({"text": text, "document": document, "rc": played.returncode}) + "\n")
    with (out / f"{agent}.prints").open("a", encoding="utf-8") as kept:     # every print, its rank in the launch
        kept.write(json.dumps({"rank": rank, "text": text, "document": document}) + "\n")
    return played.stdout, [
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"print-{rank}", "name": "Bash",
                                                       "input": {"command": f"./pp {key} -print {document} -"}}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": f"print-{rank}",
                                                  "content": played.stdout}]}}]


def prove(asked):
    # the value asked, in the prompt or behind the prints -- once, as soon as the last production due is handed
    if state_of["proven"]:
        return
    state_of["proven"] = True
    if key and PROOF.search(asked) and not plan.get("unproven") and not plan.get("error"):
        codes = PROOF.search(asked).group(1).split()
        proof = json.dumps([{"code": c, "evidence": "witness", "verdict": "n/a"} for c in codes])
        subprocess.run([sys.executable, engine, "--instance", meta, key, "-"], capture_output=True, text=True, input=proof)


# where productions are due, each act of the launch -- else its first text -- is handed in its turn by the print call
# of the next production due, the others `SAID` once its last act is handed (`[]` the first when the launch has
# nothing to hand); the texts
# between are said as they come, the ones after the last print are its last message (`QUIET` when none); the proof
# follows the last print at once. A launch that ends on an error of its harness hands nothing and proves nothing
handing = bool(key and due and not plan.get("error"))
chosen = sorted({i for i, one in enumerate(texts)          # an empty list an act follows is handed in its turn too
                 if is_act(one) or (one == [] and any(is_act(later) for later in texts[i + 1:]))} or {
    next((i for i, one in enumerate(texts) if isinstance(one, str)), -1)})[:len(due)]
last_act = chosen[-1] if chosen else -1   # once it is handed, the productions due left are handed at once
state_of = {"rank": 0, "asked": prompt, "last": False, "proven": False}   # the prints made, the text still to
# answer, a text said after them, the proof deposited


def hand(text, tell):
    state_of["rank"] += 1
    shown, lines = printed(state_of["rank"], text)
    if KEY.search(shown):                         # the block the last print moved the run to is read on
        state_of["asked"] = shown
    state_of["last"] = False
    tell(lines)
    if state_of["rank"] == len(due):              # every production due handed: the value asked, at once
        prove(state_of["asked"])


def rest(tell):
    while handing and state_of["rank"] < len(due):
        hand(@SAID@ if state_of["rank"] else "[]", tell)


if plan.get("grammar") == "codex":               # codex's grammar (`exec --json`): the session, then the answer
    spoken = []
    for i, text in enumerate(texts):
        if handing and i in chosen:
            hand(text if isinstance(text, str) else json.dumps(text), lambda lines: None)
        else:
            spoken.append(text)
    rest(lambda lines: None)
    prove(state_of["asked"])
    print(json.dumps({"type": "thread.started", "thread_id": session}))
    for text in spoken or ([@QUIET@] if handing else []):
        print(json.dumps({"type": "item.completed", "item": {"id": "m1", "type": "agent_message", "text": text}}))
else:                                            # claude's grammar: each text said AS IT COMES, then the `result` line
    said = []                                          # (the CLI's result: the last text alone)

    def told(lines):
        for line in lines:
            print(json.dumps(line), flush=True)

    def speak(text):
        if isinstance(text, dict) and "gate" in text:   # a gate inside the launch: the words before it are out
            deadline = time.monotonic() + 90
            while not os.path.exists(str(text["gate"])) and time.monotonic() < deadline:
                time.sleep(0.05)
            return
        if isinstance(text, dict) and "sleep" in text:
            time.sleep(float(text["sleep"]))
            return
        text = text if isinstance(text, str) else json.dumps(text)
        said.append(text)
        state_of["last"] = True
        print(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}), flush=True)

    for n, call in enumerate(plan.get("calls") or [], 1):   # a call of a tool and its result, as the CLI streams them:
        if "sleep" in call:                            # `tool_use` in an assistant message (its `usage` what the call
            time.sleep(float(call["sleep"]))           # sent), `tool_result` in a user message
        block = {"type": "tool_use", "id": f"call-{n}", "name": call.get("name", "Bash"), "input": call.get("input") or {}}
        print(json.dumps({"type": "assistant", "message": {"content": [block], "usage": {"input_tokens": int(call.get("sent", 1000))}}}),
              flush=True)
        print(json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": block["id"],
                                                                    "content": str(call.get("result", "")),
                                                                    "is_error": bool(call.get("error"))}]}}), flush=True)
    if plan.get("thought"):                            # a thought with its text
        print(json.dumps({"type": "assistant", "message": {"content": [{"type": "thinking", "thinking": plan["thought"]}]}}),
              flush=True)
    if last_act < 0:
        rest(told)                                     # nothing to hand: the productions due at once
    for i, text in enumerate(texts):
        if handing and i in chosen:
            hand(text if isinstance(text, str) else json.dumps(text), told)
            if i == last_act:
                rest(told)
        else:
            speak(text)
    rest(told)
    prove(state_of["asked"])
    if handing and not state_of["last"]:
        speak(@QUIET@)                                 # nothing said after the prints: the last message hands back
    print(json.dumps({"type": "result", "result": said[-1] if said else "", "session_id": session,
                      "total_cost_usd": state["cumul"], "permission_denials": [],
                      **({"is_error": True, "subtype": plan["error"]} if plan.get("error") else {})}), flush=True)
if plan.get("stderr"):
    sys.stderr.write(str(plan["stderr"]) + "\n")
sys.exit(int(plan.get("rc") or 0))
"""

# The grammar the witness writes -- the provider whose adapter reads its answer: named beside every `--harness`
# (`harnessing`), never read from a default; under a plan's `"grammar": "codex"` it writes OTHER_GRAMMAR.
QUIET = "..."                   # the last message of a launch that has nothing more to say
SAID = "witness print"          # what the witness hands for a production due before the one its act answers
# The witness as its users write it: the channel of a production said to the principal and the quiet last message
# read here, the identity line (`@IDENTITY@`) left to the house that writes it.
TEAM_WITNESS = (WITNESS_SCRIPT.replace("@TERMINAL@", language.TERMINAL).replace("@QUIET@", repr(QUIET))
                .replace("@SAID@", repr(SAID)))
SPEAKS = ("---\nname: SPEAKS\nkind: proc\ndescription: a contributor behind the work\nattach: turn.end\n"
          "proc: |\n  INFER\n---\nSPEAKS speaks\n")   # behind a turn's work: the work is said to the principal
WITNESS_GRAMMAR = "claude"
OTHER_GRAMMAR = "codex"


def harnessing(command: str, grammar: str = WITNESS_GRAMMAR) -> list[str]:
    """-> `--harness <command> --provider <grammar>`: a caller's command and the grammar its output is read in."""
    return ["--harness", command, "--provider", grammar]


# The paper run of the study § 15 (team-sim.py, seed 7): what each agent answers at each of its
# wake-ups, and when it ends -- the sleeps order the ends so that the journal is the same at
# every pass (the acts routed as they come: r2's ask well after m's relaunch on the owner's note,
# r3's answer well after m's launch on that ask, the late note during m's last launch). Nothing holds m: every
# message launches it. m: delegates, says nothing on the owner's note, nothing on r1's answer, answers r2's
# question, says nothing on r2's answer, closes on r3's; r1: done; r2: asks, then done; r3: dies once, then done.
PAPER_SCRIPT = {
    "m": [{"sleep": 1.0, "body": {"do": ["r1", "r2", "r3"]}},
          {"sleep": 0.3, "body": []},
          {"sleep": 0.3, "body": []},
          {"sleep": 0.3, "body": {"reply": {"to": "r2", "text": "the whole diff"}}},
          {"sleep": 0.3, "body": []},
          {"sleep": 4.0, "body": {"done": "LGTM"}}],
    "r1": [{"sleep": 3.0, "body": {"done": True}},
           {"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": "crash"}],   # T2, after the forged intents
    "r2": [{"sleep": 5.0, "body": {"ask": {"to": "m", "text": "scope?"}}},
           {"sleep": 0.5, "body": {"done": True}}],
    "r3": [{"sleep": 0.6, "body": "crash"},
           {"sleep": 9.0, "body": {"done": True}}],
}

# `python3 team-sim.py --trace 7` (plans/agent/design of the operator's workspace, 2026-10-01) as the
# tick writes it: every answer a `re` -- r1's, r2's and r3's to their `do`, m's to r2's ask and to the
# task's opening --, no `delegation` nor `terminal` event, m launched by the owner's note and by each answer; plus
# the note posted during m's last wake-up and its return, which the paper run adds -- as (kind, who,
# what). The sim gives a new run to every wake-up: runs are not compared.
PAPER_SHAPE = sorted([
    ("post", "house", "m", "do"), ("post", "house", "m", "info"),
    ("post", "m", "r1", "do"), ("post", "m", "r2", "do"), ("post", "m", "r3", "do"),
    ("post", "r1", "m", "re"), ("post", "r2", "m", "ask"), ("post", "m", "r2", "re"),
    ("post", "r3", "m", "re"), ("post", "r2", "m", "re"), ("post", "m", "house", "re"),
    ("wake-intent", "m"), ("wake-intent", "m"), ("wake-intent", "m"), ("wake-intent", "m"),
    ("wake-intent", "m"), ("wake-intent", "m"),
    ("wake-intent", "r1"), ("wake-intent", "r2"), ("wake-intent", "r2"),
    ("wake-intent", "r3"), ("wake-intent", "r3"),
    ("wake-launched", "m"), ("wake-launched", "m"), ("wake-launched", "m"), ("wake-launched", "m"),
    ("wake-launched", "m"), ("wake-launched", "m"),
    ("wake-launched", "r1"), ("wake-launched", "r2"), ("wake-launched", "r2"),
    ("wake-launched", "r3"), ("wake-launched", "r3"),
    ("wake-ended", "m"), ("wake-ended", "m"), ("wake-ended", "m"), ("wake-ended", "m"),
    ("wake-ended", "m"), ("wake-ended", "m"),
    ("wake-ended", "r1"), ("wake-ended", "r2"), ("wake-ended", "r2"), ("wake-ended", "r3"),
    ("wake-failed", "r3"),
    ("done",), ("schedule-off",),
    ("post", "house", "m", "info"), ("returned",),
])
SIM_KINDS = {"post", "delegation", "wake-intent", "wake-launched", "wake-ended", "wake-failed",
             "terminal", "done", "schedule-off", "returned"}

# A journal played by team 0.32.2 on 2026-10-13 (bf6f2763): T1 delegated to r1 and r2, r2's `ask` and m's `reply`,
# the delegates' `done`, the root's `done`; T2 delegated to r1, r1's final failure (`terminal`, `escalate` to m), m's
# `escalate` to the owner -- its lines as written, with its `TEAM.md`: what the readers of an old journal read.
OLD_DECLARED = '---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\nroot: m\nretries: 1\nschedule: off\n---\nReview the pull request together.\n'

OLD_JOURNAL = '{"at": "2026-10-13T05:41:14+00:00", "id": 1, "kind": "team-started", "team": "old", "agents": {"m": "agents/m", "r1": "agents/r1", "r2": "agents/r2"}, "reports": [{"from": ["r1", "r2"], "to": "m"}], "root": "m", "principals": [], "owner": "house", "ceremonies": [], "entries": {}, "work": null, "launch": {"harness": "/home/jpl/.cache/uv/environments-v2/pp-157cdfcdd3147a6f/bin/python /tmp/tmp678tjco1/team-witness.py /tmp/tmphrna_n1l/house/.pp/.sys/engine/pp.py .pp /tmp/tmpne4hz8a1/script.json /tmp/tmpgol4rnuq/witness", "provider": "claude"}, "limits": {"retries": 1}, "schedule": null, "digest": "c2f1c9305c5e"}\n{"at": "2026-10-13T05:41:14+00:00", "id": 2, "kind": "task", "team": "old", "task": "T1", "from": "house", "to": "m", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:14+00:00", "id": 3, "kind": "post", "team": "old", "task": "T1", "from": "house", "to": "m", "verb": "do", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:14+00:00", "id": 4, "kind": "wake-intent", "team": "old", "tag": "m-T1-f5b1b9", "agent": "m", "path": "agents/m", "task": "T1", "run": null, "index": 1, "messages": [3]}\n{"at": "2026-10-13T05:41:15+00:00", "id": 5, "kind": "wake-launched", "team": "old", "tag": "m-T1-f5b1b9", "agent": "m", "run": "965a44", "pid": 2715325}\n{"at": "2026-10-13T05:41:16+00:00", "id": 6, "kind": "wake-ended", "team": "old", "tag": "m-T1-f5b1b9", "agent": "m", "run": "965a44", "index": 1, "cost": 0.01}\n{"at": "2026-10-13T05:41:16+00:00", "id": 7, "kind": "post", "team": "old", "task": "T1", "from": "m", "to": "r1", "verb": "do", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 8, "kind": "delegation", "team": "old", "from": "m", "to": "r1", "task": "T1"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 9, "kind": "post", "team": "old", "task": "T1", "from": "m", "to": "r2", "verb": "do", "text": "review PR 42"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 10, "kind": "delegation", "team": "old", "from": "m", "to": "r2", "task": "T1"}\n{"at": "2026-10-13T05:41:16+00:00", "id": 11, "kind": "wake-intent", "team": "old", "tag": "r1-T1-0db28d", "agent": "r1", "path": "agents/r1", "task": "T1", "run": null, "index": 1, "messages": [7]}\n{"at": "2026-10-13T05:41:17+00:00", "id": 12, "kind": "wake-launched", "team": "old", "tag": "r1-T1-0db28d", "agent": "r1", "run": "a35444", "pid": 2715370}\n{"at": "2026-10-13T05:41:17+00:00", "id": 13, "kind": "wake-intent", "team": "old", "tag": "r2-T1-4799a8", "agent": "r2", "path": "agents/r2", "task": "T1", "run": null, "index": 1, "messages": [9]}\n{"at": "2026-10-13T05:41:18+00:00", "id": 14, "kind": "wake-launched", "team": "old", "tag": "r2-T1-4799a8", "agent": "r2", "run": "356025", "pid": 2715378}\n{"at": "2026-10-13T05:41:19+00:00", "id": 15, "kind": "wake-ended", "team": "old", "tag": "r2-T1-4799a8", "agent": "r2", "run": "356025", "index": 1, "cost": 0.01}\n{"at": "2026-10-13T05:41:19+00:00", "id": 16, "kind": "post", "team": "old", "task": "T1", "from": "r2", "to": "m", "verb": "ask", "text": "scope?"}\n{"at": "2026-10-13T05:41:19+00:00", "id": 17, "kind": "wake-intent", "team": "old", "tag": "m-T1-66b346", "agent": "m", "path": "agents/m", "task": "T1", "run": "965a44", "index": 2, "messages": [16]}\n{"at": "2026-10-13T05:41:19+00:00", "id": 18, "kind": "wake-launched", "team": "old", "tag": "m-T1-66b346", "agent": "m", "run": "965a44", "pid": 2715474}\n{"at": "2026-10-13T05:41:19+00:00", "id": 19, "kind": "wake-ended", "team": "old", "tag": "r1-T1-0db28d", "agent": "r1", "run": "a35444", "index": 1, "cost": 0.01}\n{"at": "2026-10-13T05:41:19+00:00", "id": 20, "kind": "terminal", "team": "old", "agent": "r1", "task": "T1"}\n{"at": "2026-10-13T05:41:19+00:00", "id": 21, "kind": "post", "team": "old", "task": "T1", "from": "r1", "to": "m", "verb": "done", "text": ""}\n{"at": "2026-10-13T05:41:20+00:00", "id": 22, "kind": "wake-ended", "team": "old", "tag": "m-T1-66b346", "agent": "m", "run": "965a44", "index": 2, "cost": 0.01}\n{"at": "2026-10-13T05:41:20+00:00", "id": 23, "kind": "post", "team": "old", "task": "T1", "from": "m", "to": "r2", "verb": "reply", "text": "the whole diff", "reply": 16}\n{"at": "2026-10-13T05:41:20+00:00", "id": 24, "kind": "wake-intent", "team": "old", "tag": "r2-T1-332ee5", "agent": "r2", "path": "agents/r2", "task": "T1", "run": "356025", "index": 2, "messages": [23]}\n{"at": "2026-10-13T05:41:21+00:00", "id": 25, "kind": "wake-launched", "team": "old", "tag": "r2-T1-332ee5", "agent": "r2", "run": "356025", "pid": 2715528}\n{"at": "2026-10-13T05:41:22+00:00", "id": 26, "kind": "wake-ended", "team": "old", "tag": "r2-T1-332ee5", "agent": "r2", "run": "356025", "index": 2, "cost": 0.01}\n{"at": "2026-10-13T05:41:22+00:00", "id": 27, "kind": "terminal", "team": "old", "agent": "r2", "task": "T1"}\n{"at": "2026-10-13T05:41:22+00:00", "id": 28, "kind": "post", "team": "old", "task": "T1", "from": "r2", "to": "m", "verb": "done", "text": "reviewed"}\n{"at": "2026-10-13T05:41:22+00:00", "id": 29, "kind": "wait-met", "team": "old", "agent": "m", "task": "T1"}\n{"at": "2026-10-13T05:41:22+00:00", "id": 30, "kind": "wake-intent", "team": "old", "tag": "m-T1-6f43c3", "agent": "m", "path": "agents/m", "task": "T1", "run": "965a44", "index": 3, "messages": [21, 28]}\n{"at": "2026-10-13T05:41:23+00:00", "id": 31, "kind": "wake-launched", "team": "old", "tag": "m-T1-6f43c3", "agent": "m", "run": "965a44", "pid": 2715570}\n{"at": "2026-10-13T05:41:24+00:00", "id": 32, "kind": "wake-ended", "team": "old", "tag": "m-T1-6f43c3", "agent": "m", "run": "965a44", "index": 3, "cost": 0.01}\n{"at": "2026-10-13T05:41:24+00:00", "id": 33, "kind": "terminal", "team": "old", "agent": "m", "task": "T1"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 34, "kind": "done", "team": "old", "task": "T1", "result": "LGTM"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 35, "kind": "schedule-off", "team": "old"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 36, "kind": "task", "team": "old", "task": "T2", "from": "house", "to": "m", "text": "fix the build"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 37, "kind": "post", "team": "old", "task": "T2", "from": "house", "to": "m", "verb": "do", "text": "fix the build"}\n{"at": "2026-10-13T05:41:24+00:00", "id": 38, "kind": "wake-intent", "team": "old", "tag": "m-T2-f74b9f", "agent": "m", "path": "agents/m", "task": "T2", "run": "965a44", "index": 4, "messages": [37]}\n{"at": "2026-10-13T05:41:25+00:00", "id": 39, "kind": "wake-launched", "team": "old", "tag": "m-T2-f74b9f", "agent": "m", "run": "965a44", "pid": 2715596}\n{"at": "2026-10-13T05:41:26+00:00", "id": 40, "kind": "wake-ended", "team": "old", "tag": "m-T2-f74b9f", "agent": "m", "run": "965a44", "index": 4, "cost": 0.01}\n{"at": "2026-10-13T05:41:26+00:00", "id": 41, "kind": "post", "team": "old", "task": "T2", "from": "m", "to": "r1", "verb": "do", "text": "fix the build"}\n{"at": "2026-10-13T05:41:26+00:00", "id": 42, "kind": "delegation", "team": "old", "from": "m", "to": "r1", "task": "T2"}\n{"at": "2026-10-13T05:41:26+00:00", "id": 43, "kind": "wake-intent", "team": "old", "tag": "r1-T2-8c0228", "agent": "r1", "path": "agents/r1", "task": "T2", "run": "a35444", "index": 2, "messages": [41]}\n{"at": "2026-10-13T05:41:26+00:00", "id": 44, "kind": "wake-launched", "team": "old", "tag": "r1-T2-8c0228", "agent": "r1", "run": "a35444", "pid": 2715650}\n{"at": "2026-10-13T05:41:27+00:00", "id": 45, "kind": "wake-failed", "team": "old", "tag": "r1-T2-8c0228", "agent": "r1", "task": "T2", "final": false, "reason": "wake-dead"}\n{"at": "2026-10-13T05:41:27+00:00", "id": 46, "kind": "wake-intent", "team": "old", "tag": "r1-T2-e98fa7", "agent": "r1", "path": "agents/r1", "task": "T2", "run": "a35444", "index": 2, "messages": [41]}\n{"at": "2026-10-13T05:41:27+00:00", "id": 47, "kind": "wake-launched", "team": "old", "tag": "r1-T2-e98fa7", "agent": "r1", "run": "a35444", "pid": 2715671}\n{"at": "2026-10-13T05:41:28+00:00", "id": 48, "kind": "wake-failed", "team": "old", "tag": "r1-T2-e98fa7", "agent": "r1", "task": "T2", "final": true, "reason": "wake-dead"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 49, "kind": "terminal", "team": "old", "agent": "r1", "task": "T2"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 50, "kind": "post", "team": "old", "task": "T2", "from": "r1", "to": "m", "verb": "escalate", "text": "the wake-up failed: wake-dead"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 51, "kind": "wait-met", "team": "old", "agent": "m", "task": "T2"}\n{"at": "2026-10-13T05:41:28+00:00", "id": 52, "kind": "wake-intent", "team": "old", "tag": "m-T2-297277", "agent": "m", "path": "agents/m", "task": "T2", "run": "965a44", "index": 5, "messages": [50]}\n{"at": "2026-10-13T05:41:28+00:00", "id": 53, "kind": "wake-launched", "team": "old", "tag": "m-T2-297277", "agent": "m", "run": "965a44", "pid": 2715682}\n{"at": "2026-10-13T05:41:29+00:00", "id": 54, "kind": "wake-ended", "team": "old", "tag": "m-T2-297277", "agent": "m", "run": "965a44", "index": 5, "cost": 0.01}\n{"at": "2026-10-13T05:41:29+00:00", "id": 55, "kind": "terminal", "team": "old", "agent": "m", "task": "T2"}\n{"at": "2026-10-13T05:41:29+00:00", "id": 56, "kind": "post", "team": "old", "task": "T2", "from": "m", "to": "house", "verb": "escalate", "text": "blocked by the build"}\n'

THURSDAY = "2026-10-01T"                           # the frozen day of the ceremonies (PP_NOW)
MONDAY, TUESDAY, WEDNESDAY = "2026-10-05T", "2026-10-06T", "2026-10-07T"   # the week of the recurrences
PAIR = ("---\nagents: |\n  {m} agents/{m}\n  {w} agents/{w}\nreports: |\n  {w} -> {m}\nroot: {m}\n"   # a root and its
        "schedule: off\n---\nDo the task you are given, then answer.\n")                           # worker, no net
DAILY_DOC = "---\nproc: |\n  WORK\n---\n# DAILY\n\nSay yesterday, today and blockers.\n"
WORK_DOC = "---\nproc: |\n  WORK\n---\n# WORK\n\nDo the task the message names.\n"


# --- the declaration read: what the `team-declaration*` scenarios share -------------------------------

def judged_team(root: str, worker: str) -> str:
    """-> a TEAM.md with every key `declared` says: two members, an edge, a principal, limits, a ceremony."""
    return (f"---\nagents: |\n  {root} agents/{root}\n  {worker} agents/{worker}\nreports: |\n  {worker} -> {root}\n"
            f"root: {root}\nprincipals: |\n  pm\nbudget: 5\nlaunches: 8\nschedule: off\nceremonies: |\n"
            f"  daily every weekday 09:30 with {worker} -> {root}\n---\nShip it.\n")


def refusal_code(said: str) -> str:
    """-> the refusal's code: the first token of what pp-team says, after its name."""
    words = said.strip().removeprefix("pp-team: ").split()
    return words[0].rstrip(":") if words else ""


def declaration_read(house, name: str) -> dict:
    """-> `team declaration <name> --json` read: its last line's object, whatever the exit; {} when it says none."""
    played = house.call("team", "declaration", name, "--json")
    try:
        return json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return {}


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


def words_of(path: Path, name: str) -> tuple:
    """-> the tuple of words the script at `path` declares under `name`, read from its source; () without it."""
    import ast
    found = re.search(rf"^{name} = (\([^)]*\))", path.read_text(encoding="utf-8"), re.M)
    return ast.literal_eval(found.group(1)) if found else ()


def acts_handed(out: Path, agent: str) -> list[int]:
    """-> the rank, in its launch, of each print by which the witness of `agent` handed an act -- a JSON object or a
    list of elements --, in order: the `words` of the launch that carried it."""
    def act(text: str) -> bool:
        try:
            read = json.loads(text)
        except ValueError:
            return False
        return isinstance(read, dict) or (isinstance(read, list) and bool(read))
    return [int(one["rank"]) for one in lines(out / f"{agent}.prints") if act(str(one.get("text")))]


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
    ended = {one.get("tag") for one in found
             if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed", "quota-reached")}
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


def local_after(at: str, minutes: float = 0, seconds: float = 0) -> datetime:
    """-> the LOCAL naive time `minutes` and `seconds` after a journal's `at` (UTC): the tick's clock (`tick_now`)
    reads it so."""
    return datetime.fromisoformat(at).astimezone().replace(tzinfo=None) + timedelta(minutes=minutes, seconds=seconds)


def finals_of(found: list[dict], member: str) -> list[dict]:
    return [one for one in by_kind(found, "wake-failed", agent=member) if one.get("final")]


# A root and its one report under `retries: 1`: what the scenarios of the failure detector declare, each under its names.
SUSPECT_PAIR = ("---\nagents: |\n  {a} agents/{a}\n  {b} agents/{b}\nreports: |\n  {b} -> {a}\nroot: {a}\nretries: 1\n"
                "schedule: off\n---\nSplit the work, report.\n")
DEATH = {"sleep": 0.1, "body": "crash"}            # a launch of the witness that dies at once


def ticked(h, waits: list[tuple], timeout: float = 40.0) -> None:
    """Ticks every team named, side by side, until its journal satisfies its predicate -- `waits` as (team,
    predicate, now), each team on its own clock."""
    deadline = time.monotonic() + timeout
    pending = list(waits)
    with ThreadPoolExecutor(max_workers=len(waits)) as pool:
        while time.monotonic() < deadline:
            pending = [one for one in pending if not one[1](h.events(one[0]))]
            if not pending:
                return
            time.sleep(0.3)
            list(pool.map(lambda one: h.call("team", "tick", one[0], now=one[2]), pending))


# --- the house: one throwaway instance, its witness, its calls ------------------------------

# The LAUNCHER'S WITNESS (team 1.14.5): the house's `pp-agent` script replaced by this stand-in, which writes each
# line it is called with -- one JSON array a line --, then answers as the launcher's contract of vectors says: a
# vector of the family `refused` is refused `vector-refused` (rc 2, the code at the head of the refusal); a line
# carrying a vector of the family `busy` is refused ONCE by the house (`house-busy`, rc 2: no vector's refusal); any
# other vector is accepted -- its flags taken off the line, the launcher's own source, kept aside, played as it is.
LAUNCHER_WITNESS = """import json, sys
from pathlib import Path
args = sys.argv[1:]
with open(%(log)r, "a", encoding="utf-8") as handle:     # the line the launcher is called with
    handle.write(json.dumps(args) + "\\n")
vectors = [value for flag, value in zip(args, args[1:]) if flag == "--vector"]
if any(one.startswith("refused:") for one in vectors):
    sys.stderr.write("pp-agent: vector-refused -- the family `refused` refuses its node\\n")
    raise SystemExit(2)
busy = Path(%(log)r + ".busy")
if any(one.startswith("busy:") for one in vectors) and not busy.exists():
    busy.write_text("once", encoding="utf-8")
    sys.stderr.write("pp-agent: house-busy -- the house cannot launch now\\n")
    raise SystemExit(2)
kept, index = [], 0                                       # the vectors accepted: off the line
while index < len(args):
    if args[index] == "--vector":
        index += 2
        continue
    kept.append(args[index])
    index += 1
sys.argv = [sys.argv[0], *kept]
exec(compile(Path(%(real)r).read_text(encoding="utf-8"), __file__, "exec"))   # then the launcher as it is
"""


def launcher_witness(bench, h) -> Path:
    """The LAUNCHER'S WITNESS (`LAUNCHER_WITNESS`) in place of the house's `pp-agent` script, the launcher's own source
    kept aside. -> the log of the lines it was called with."""
    script = instance.skill_contract(h.house, "pp-agent").parent / "pp-agent.py"
    real = bench.temp() / "pp-agent.real.py"
    real.write_text(script.read_text(encoding="utf-8"), encoding="utf-8")
    log = bench.temp() / "launcher.jsonl"
    script.write_text(LAUNCHER_WITNESS % {"log": str(log), "real": str(real)}, encoding="utf-8")
    return log


def starts(log: Path, tag: str) -> list[list[str]]:
    """-> the `agent start` lines the witness kept whose `--tag` begins with `tag` (`<member>-<task>-`)."""
    found = [json.loads(one) for one in log.read_text(encoding="utf-8").splitlines()] if log.is_file() else []
    return [one for one in found if one[:1] == ["start"] and
            str(dict(zip(one, one[1:])).get("--tag", "")).startswith(tag)]


def vectors_on(line: list[str]) -> list[str]:
    """-> the values of the line's `--vector` flags, in order."""
    return [value for flag, value in zip(line, line[1:]) if flag == "--vector"]



class House:
    """A throwaway house pinning `agent` and `team`, the team witness written beside it with
    its script, the system's schedulers diverted to files of their own (`PP_CRONTAB` for the
    crontab, `PP_RUNKEY` for the user's Run key under Windows, never the machine's): what every scenario of
    the area installs for itself."""

    def __init__(self, bench, engine: Path | None = None, script: dict | None = None,
                 packages: tuple[str, ...] = ("agent", "team"), slug: str = "house") -> None:
        self.bench = bench
        self.ws = bench.temp() / slug                  # the owner's slug: `house`
        self.house = install.install(engine or PRODUCT_ENGINE, self.ws / INSTANCE, list(packages))
        self.engine = self.house / ".sys" / "engine" / "pp.py"
        self.env = {"PP_CRONTAB": str(bench.temp() / "crontab"), "PP_RUNKEY": str(bench.temp() / "runkey")}
        self.crontab = Path(self.env["PP_CRONTAB"])
        self.runkey = Path(self.env["PP_RUNKEY"])
        self.teams = self.ws / "teams"
        self.records = self.house / ".sys" / "records"
        self.out = bench.temp() / "witness"            # what the witness kept: prompts, counts, memory
        self.out.mkdir()
        self.witness = bench.temp() / "team-witness.py"
        self.witness.write_text(TEAM_WITNESS.replace("@IDENTITY@", repr(identity_pattern(self.module()).pattern)),
                                encoding="utf-8")
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
        """The owner's file under teams/<name>/: `text` whole as `TEAM.md` -- its front matter the declaration, its
        body the owner's word, served to every member; `team start` writes the team's other documents."""
        (self.teams / name).mkdir(parents=True, exist_ok=True)
        (self.teams / name / "TEAM.md").write_text(text.replace("name: review", f"name: {name}", 1), encoding="utf-8")

    def speaks(self, path: str) -> None:
        """The agent at `path` born with a document behind its turn's work (`SPEAKS`): its work is then a production
        said to the principal, which its witness hands by the print call."""
        self.entry_laid(path, "SPEAKS.md", SPEAKS)
        cli(self.engine, "--instance", str(self.meta_of(path)), "-build", cwd=self.ws, env=self.env)

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

    def measured_in(self, name: str, window: int) -> None:
        """The measures kept at the team's `wake-ended` given the `window` and the `used` a house that launched a
        provider would have said -- under a caller's command the house knows no window --, written while the team
        rests, every id and every other field kept: a renewal is judged on the journal alone."""
        journal = self.journal_of(name)
        found = lines(journal)
        for one in found:
            if one.get("kind") == "wake-ended" and isinstance(one.get("context"), dict):
                tokens = int(one["context"].get("tokens") or 0)
                one["context"] = {**one["context"], "window": window, "used": round(tokens / window, 4)}
        journal.write_text("".join(json.dumps(one, ensure_ascii=False) + "\n" for one in found), encoding="utf-8")

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

    def off_season(self, name: str, now: str | None = None) -> None:
        """The team's season stopped when one runs (`team stop <name> --no-tick`): what a scenario plays before it
        writes the team's values or opens its next season; nothing for a team never started or off season."""
        marks = [one.get("kind") for one in self.events(name) if one.get("kind") in ("team-started", "season-stopped")]
        if marks and marks[-1] == "team-started":
            self.call("team", "stop", name, "--no-tick", now=now)

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
        """-> the skill `pp-team` vendored at this house, loaded: what a head or a tick answer is compared with
        (`RELANCED`, `OWED`, `IDENTITY`) comes from it, never retyped."""
        return skill(self.team_module())

    def timer_spawned(self, name: str, token: str, marked: str, sleep: float = 1.0) -> subprocess.Popen:
        """A TIMER of the team behind one more process -- `sh -c '<the console> team timer … --token <token> ; :'`, as
        uv's launcher stands under Windows --, sleeping `sleep` seconds, its mark naming the `sh` and carrying
        `marked`."""
        due = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + sleep))
        console = f"{sys.executable} {self.engine} --instance {self.house}"
        shell = subprocess.Popen(["sh", "-c", f"{console} team timer {name} --sleep {sleep:g} --due {due} --token {token} ; :"],
                                 cwd=self.ws, env={**os.environ, **self.env}, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        mark = self.records / "teams" / name / "tick.timer"
        mark.write_text(json.dumps({"pid": shell.pid, "due": due, "token": marked}), encoding="utf-8")
        return shell

    def timer_gone(self, name: str) -> bool:
        """-> whether the team's timer is gone: its mark `tick.timer` left and no `team timer <name>` process alive, both
        within 10 s -- the tick that follows the end disarms the timer, and a timer that played that tick took its mark
        away first and ends once the tick has returned."""

        def alive() -> bool:
            return bool(subprocess.run(["pgrep", "-f", f"timer {name} --sleep"], capture_output=True,
                                       text=True).stdout.strip())

        mark = self.records / "teams" / name / "tick.timer"
        gone_at = time.monotonic() + 10
        while time.monotonic() < gone_at and (mark.exists() or alive()):
            time.sleep(0.2)
        return not mark.exists() and not alive()


# --- the paper run, replayed by every scenario that reads it ------------------------------

def paper_run(house: House) -> dict:
    """Plays the paper run of the study § 15 on `house`: the review team started under the
    witness, a note posted while m works, one more when m's sixth -- its last --
    wake-up is due, the ticks the wake-ups fire by `--on-end` taking the team to `done T1`. -> what
    the cases read: the calls, `done`, the journal (`found`)."""
    house.declare("review", PAPER_TEAM)
    started = house.call("team", "start", "review", "--message", "review PR 42", *house.harnessed)
    noted = house.call("team", "post", "review", "--task", "T1", "--message", "change of course")
    late_post = None
    if house.settled("review", lambda found: len(intents_of(found, "m")) >= 6, timeout=60):
        late_post = house.call("team", "post", "review", "--task", "T1", "--message", "one more thing")
    done = house.settled("review", quiescent)
    time.sleep(1.0)                                       # the last on-end tick writes after the response
    return {"started": started, "noted": noted, "late_post": late_post, "done": done,
            "found": house.events()}


def flow_file(house: House, path: str, key: str) -> Path:
    """-> the flow file the house keeps for the run `key` of the agent at `path` -- `flows/<digest of the
    path>/<key>.jsonl` under the house's records, the digest the first 12 hexadecimal characters of the path's
    sha1, as agent's README_INTERNAL says it: what a case forges a launch's end in."""
    import hashlib
    return house.records / "flows" / hashlib.sha1(path.encode("utf-8")).hexdigest()[:12] / f"{key}.jsonl"


def forge_flow(house: House, path: str, key: str, cost: float, state: str = "parked", text: str = '{"done": true}',
               tag: str | None = None) -> None:
    """The bench's hand on a disposable flow: ONE exchange of the run `key` -- opened (with the launch's `tag` when
    one is given: what the tick's reader starts at), a words, the agent's cost, the response and its verdict --
    written as the house keeps them, the end a reap reads."""
    target = flow_file(house, path, key)
    target.parent.mkdir(parents=True, exist_ok=True)
    at = "2026-10-03T12:00:05+00:00"
    with target.open("a", encoding="utf-8") as handle:
        for one in ({"kind": "opened", "exchange": 1, "agent": path, **({"tag": tag} if tag else {})},
                    {"kind": "words", "exchange": 1, "launch": 1, "text": text},
                    {"kind": "agent", "exchange": 1, "launch": 1, "cost_usd": cost},
                    {"kind": "response", "index": 1, "response": text, "cost_usd": cost, "launches": 1,
                     "error": None, "harness_rc": 0, "state": state},
                    {"kind": "verdict", "exchange": 1, "state": state, "harness_rc": 0, "cost_usd": cost, "launches": 1}):
            handle.write(json.dumps({"at": at, "run": key, **one}) + "\n")


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
member = re.search(@IDENTITY@, prompt, re.M)      # the identity line of a wake-up: the team, the member
if member and member.group(2) in held and "[message from your principal]" in prompt:
    deadline = time.monotonic() + 90
    while not os.path.exists(gate) and time.monotonic() < deadline:
        time.sleep(0.05)
sys.exit(subprocess.run(command, input=prompt, text=True).returncode)
"""


def gated(house: House, gate: Path, members: tuple[str, ...]) -> list[str]:
    """-> the launch flags of the witness behind a gate: the members named wait for `gate` to stand before they play;
    every other member plays at once."""
    script = house.bench.temp() / "gate.py"
    script.write_text(GATE.replace("@IDENTITY@", repr(identity_pattern(house.module()).pattern)), encoding="utf-8")
    return harnessing(f"{sys.executable} {script} {gate} {','.join(members)} {house.harness}")


def witness_alive(house: House) -> str:
    """-> the pids of the house's witnesses still alive, '' when none."""
    return subprocess.run(["pgrep", "-f", str(house.witness)], capture_output=True, text=True).stdout.strip()


SKILL = PRODUCT_ENGINE.parents[1] / "packages" / "team" / "skills" / "pp-team" / "pp-team.py"
LOADED: dict = {}                   # the skills loaded, by the path of their entry


def skill(script: Path = SKILL):
    """-> the skill `pp-team` loaded as ONE object (the harness's `load_skill`), whichever of its modules
    defines a name: the product's the houses are installed from, or the one at `script`. A path is loaded
    once: every reading of a scenario gets the same object, and so the same classes. Its constants are read
    by a scenario rather than copied as literals (tests/README.md, rule 2); the area reads its skill through
    here alone."""
    if script not in LOADED:
        LOADED[script] = load_skill(script)
    return LOADED[script]


def probe_script(house: House, body: str) -> Path:
    """-> a probe written beside the bench that loads the house's skill `pp-team` as `mod`, by the harness's
    `load_skill` as the scenarios do, in a process of its own."""
    probe = house.bench.temp() / "probe.py"
    probe.write_text("import importlib.util, json, sys, time\nfrom pathlib import Path\n"
                     f"sys.path[:0] = [{str(PRODUCT_ENGINE.parent)!r}, {str(PRODUCT_ENGINE.parents[1])!r}]\n"
                     "from tests.harness import load_skill\n"
                     f"mod = load_skill(Path({str(house.team_module())!r}))\n" + body,
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


def ends_named(prompt: str, found: list[dict], agent: str) -> list[int]:
    """-> the ids of the OTHER members' `wake-ended` events a wake-up's head names, `#<id>` on a line of the head
    itself -- a message's text, indented under its head line, never counts --: [] when the head names no response of
    the others."""
    ended = {one["id"] for one in found if one.get("kind") == "wake-ended" and one.get("agent") != agent}
    return sorted({int(one) for line in prompt.splitlines() if line[:1] not in (" ", "\t")
                   for one in re.findall(r"#(\d+)", line)} & ended)


def handed_back(module, prompt: str) -> dict[int, dict]:
    """-> the messages a wake-up's head hands back to their author, by the id of the message: `how` the tick answered
    in the member's place -- a key of the module's `ANSWERED_FOR` --, the `member`, the `vector` the head says (None
    without one) and the `text` shown under it, whole. The head is read against the module's own words, rendered
    with sentinels; {} for a module that says none."""
    said = getattr(module, "ANSWERED_FOR", None)
    if not said:
        return {}
    holes = {"memberq": r"(\S+)", "77077": r"(\d+)"}
    answered = {how: rendered("  " + line.format(member="memberq", id=77077), holes) for how, line in said.items()}
    plain = rendered("  " + module.HANDED_BACK.format(id=77077), holes)
    vectored = rendered("  " + module.HANDED_BACK_VECTOR.format(id=77077, vector="vectorq"), {**holes, "vectorq": r"(\S+)"})
    found: dict[int, dict] = {}
    lines = prompt[:prompt.find("▌ pp · run")].splitlines() if "▌ pp · run" in prompt else prompt.splitlines()
    for at, line in enumerate(lines):
        for how, pattern in answered.items():
            match = pattern.match(line)
            if match:
                groups = match.groups()
                key = int(next(one for one in groups if one.isdigit()))
                found.setdefault(key, {}).update({"how": how, "member": next(one for one in groups if not one.isdigit())})
        match = vectored.match(line) or plain.match(line)
        if match:
            key = int(match.group(1))
            text = []
            for under in lines[at + 1:]:
                if not under.startswith("    "):
                    break
                text.append(under[4:])
            found.setdefault(key, {}).update({"vector": match.group(2) if match.re is vectored else None,
                                              "text": "\n".join(text)})
    return found


def identity_pattern(module) -> re.Pattern:
    """-> the line that opens the head of a WAKE-UP -- its groups the team and the member --, from the module's
    `IDENTITY`: every reader of that line, the witnesses included, reads it through here."""
    return rendered(module.IDENTITY.format(team="teamq", member="memberq"), {"teamq": r"(\S+)", "memberq": r"(\S+)"})


def health_pattern(module) -> re.Pattern:
    """-> the line a wake-up's head says a suspected member with -- its groups the member and the hour of its try --,
    from `health_lines` on a member fallen once."""
    state = {"started": {"agents": {"memberq": "memberq", "otherq": "otherq"}, "schedule": 5}, "limits": {},
             "health": {"memberq": {"falls": 1, "at": "2026-10-01T09:00:00+00:00"}}}
    hour = module.suspicion_of(state, "memberq")["until"].strftime("%H:%M:%S")
    return rendered(module.health_lines(state, "otherq"), {"memberq": r"(\S+)", hour: r"(\d\d:\d\d:\d\d)"})
