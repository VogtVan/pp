"""Scenario `agent-exchange-record` -- the record of an exchange: the words its launches said, the response
they compose, the policy played, the launches it costs -- on one house, plain first, then under a law of
production, then on a described door:
- a plain house: ONE launch, the AWAIT fused in the boot's output; the words are the prints the conduction asked
  (its `print-due`), each the `play` witness handed by its print call -- its answer is none --, the response their composition; no model and no
  effort asked: null
- the last message and its length (agent 1.1.0): `finals` keeps, under its launch, each launch's last message, its
  blanks stripped -- its characters, then its `text` --, and `overruns` the count of them over `ANSWER_BOUND` -- a
  short answer none, a long one one; neither text is in `words`; `exchanges --json` says the same `finals`
- the `stream` witness under a law of production: an exchange of ONE launch keeps `words` -- the productions due
  handed, under its launch number; the text it wrote before a call and its last message are no words --,
  `response` their composition, `model` and `effort` the policy played; every field of the record there
- the tokens sent (agent 1.0.33): `tokens_sent` sums what the stream's calls sent the model, each message once by
  its id -- 300606 for the three messages of the `stream` witness's launch --; the `worded` witness measures no
  call: null
- the two lines that exchange wrote, whole: its line of `messages.jsonl` and its line of `responses.jsonl` say
  every key in its order with its value -- the hour apart, the sums of the flow by their names
- the faces: `agent responses` renders the composed response, each words once; `agent exchanges --json`
  carries `words`, `model` and `effort`
- words no reader can read -- a list one item of which is no mapping, a text -- written under the run by the
  bench: `agent exchanges --json` says them as their line of `responses.jsonl` does
- the `worded` witness (three texts at each launch, the first before a call, a blank one among the others, the
  `result` line the last text alone): `words` keeps the productions handed; the texts no call follows are the
  launch's last message, one `finals` item of their characters and their text -- joined, the blank one dropped --;
  `response` carries the productions, in their order, each once -- the words joined, nothing added
- the `agent` event that ends a launch carries no text: the flow keeps the words once, under `words`
- an output that asks the agent nothing -- the bare AWAIT served once the proof is judged -- launches
  nothing: under a law of production ONE exchange costs ONE launch, the boot with the WORK and the proof fused
  under it, the witness piping its proof there; the flow says one `conduction` and one `agent` event -- a
  conduction is a launch's --, the verdict `parked`
- a described door: ONE exchange on LAPS, offered to the TURN's WORK and
  opened by the witness, costs ONE launch per block never served -- the witness hands the prints due before the
  WORK and opens the door; the door's block, then each lap's, serves what the agent has not read (its brief, its
  element): it is held, never answered in a tool result (0 inline), and its launch pipes the field, or hands the
  lap's production and pipes its proof: 5 launches, 5 blocks held (the door, 3 laps, the AWAIT); the door consumes
  the WORK and the print it owed, the AWAIT comes bare at the principal's call and launches nothing --; 3 proofs,
  the run parked, the response the productions due handed, the laps among them
- a line of `messages.jsonl` and a line of `responses.jsonl` read there and back (`Message`, `Response`): the
  lines the exchanges above wrote, a line written here in the writer's order with every key, and a line of a form
  of before -- keys fewer and in another order, a key nobody names, a policy with a key of another time, a null --
  each give the same JSON text back; the line of the writer's order composed anew gives it too, and a type that
  names none of the keys written when named writes none of them; a line of before with its `flow` (a context
  measured, another order with a sum nobody names, a null) and with its `words` (the writer's order, another order
  with a key nobody names, none, a null) gives the same text back, its sums and its words read by their fields
  (`Sums`, `Said`); the voices of the flow are the same list, in the same order, in `FLOW_VOICES`, in what
  `Sums.voices()` renders and in the fields of `Sums` before `calls`
- a line read on which a field it does not carry is named after the fact (`dataclasses.replace`) is not written:
  `json()` raises a `ValueError`, for a message, a response and a material; a field its line carries is written,
  and a push and a prune of a material, which carry their keys with them, pass
"""
from __future__ import annotations

import dataclasses
import json
import re

from tests.harness import support

A = support(__file__, "agent")
LAPS = ("---\nname: LAPS\nkind: proc\ndescription: a described door\noutput: any\nfield: |\n  three names\n"
        "constraints.production: |\n  LP1  the lap names its element\nproc: |\n  INFER\n  PROVE\n---\nlap\n")
TURN = "---\nname: TURN\ntools: |\n  +LAPS\n---\n"


def woken(h, message: str, mode: str = "play", *flags: str):
    """`agent run` on the house -> (the call, the key of the run it opened, that run's last record)."""
    before = set(h.keys())
    woke = h.wake(message, mode, *flags)
    key = next((one for one in h.keys() if one not in before), "")
    kept = next((one for one in reversed(h.responses()) if key and one.get("run") == key), {})
    return woke, key, kept


def flow_of(h, key: str) -> list[dict]:
    """-> the events of the run's flow file under the house's records, in order."""
    found = []
    for path in sorted((h.records / "flows").rglob(f"{key}.jsonl")) if key else []:
        found += A.lines(path)
    return found


def rows_of(played) -> list[dict]:
    """-> the objects of a `--json` call, one per line; [] when a line does not read."""
    try:
        return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
    except ValueError:
        return []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)

    # --- a plain house: one launch, the production handed is the words -----------------------------------------
    plain, key, kept = woken(h, "plain")
    dues = h.dues(key) if key else []          # the prints the conduction asked
    if (plain.returncode == 0 and dues
            and kept.get("words") == [{"launch": 1, "text": A.PRINTED}] * len(dues)
            and kept.get("response") == A.opening(dues)
            and kept.get("model") is None and kept.get("effort") is None):
        held("(c) the production handed is the response", f"words [{{launch 1, each of the {len(dues)} prints due}}] -- the answer none "
             "--, the response their composition; no model and no effort asked: null")
    else:
        failures.append(f"  ✗ (c) plain                    rc={plain.returncode} dues={dues} words={kept.get('words')!r} "
                        f"model={kept.get('model')!r}")

    plain, _, kept = woken(h, "un")
    if plain.returncode == 0 and kept.get("launches") == 1 and "· parked ·" in plain.stderr:
        held("(b) a plain house: one launch", "the AWAIT fused in the boot's output, nothing more to launch")
    else:
        failures.append(f"  ✗ (b) plain                   rc={plain.returncode} launches={kept.get('launches')} "
                        f"{plain.stderr[-200:]!r}")

    # --- the last message and its length: `finals` and `overruns` at the record, and at `exchanges --json` -------
    bound = getattr(A.skill(), "ANSWER_BOUND", None)
    short = A.answer_of("play")
    woke, key, long_kept = woken(h, "say it all again", "long")
    long = A.LONG.strip()
    listed = rows_of(h.call("agent", "exchanges", "agents/ag1", key, "--json"))
    if (plain.returncode == 0 and woke.returncode == 0 and isinstance(bound, int) and len(short) <= bound < len(long)
            and kept.get("finals") == [{"launch": 1, "chars": len(short), "text": short}] and kept.get("overruns") == 0
            and long_kept.get("finals") == [{"launch": 1, "chars": len(long), "text": long}]
            and long_kept.get("overruns") == 1
            and [one.get("finals") for one in listed] == [long_kept.get("finals")]
            and all(one.get("text") not in (short, long) for one in kept.get("words", []) + long_kept.get("words", []))):
        held("(j) the last message and its length", f"a short answer: finals [launch 1, {len(short)} chars, its text], "
             f"overruns 0; run {key}, a long one: [launch 1, {len(long)} chars, its text], overruns 1 -- over {bound}; "
             "exchanges --json says the same finals; neither text in the words")
    else:
        failures.append(f"  ✗ (j) finals                   bound={bound!r} short={kept.get('finals')!r}/"
                        f"{kept.get('overruns')!r} long={long_kept.get('finals')!r}/{long_kept.get('overruns')!r} "
                        f"listed={[one.get('finals') for one in listed]!r} {woke.stderr[-200:]!r}")
    h.lawful()

    # --- the stream witness: words, model and effort at the record --------------------------------------------
    woke, key, kept = woken(h, "say it", "stream", "--model", "m-one", "--effort", "high")
    words = kept.get("words") or []
    said = [A.PRINTED] * len(h.dues(key))  # a print for each due; the text before the call: an aside; the last message: no words
    owed_words = [{"launch": 1, "text": text} for text in said]
    if (woke.returncode == 0 and kept.get("launches") == 1 and said
            and words == owed_words
            and kept.get("response") == "\n\n".join(said)
            and kept.get("model") == "m-one" and kept.get("effort") == "high"
            and A.RECORD_FIELDS <= set(kept)):
        held("(a) words, model and effort at the record", f"run {key}: 1 launch, the {len(said)} productions due handed "
             "under it, response their composition, model m-one, effort high; the "
             "fields of before kept")
    else:
        failures.append(f"  ✗ (a) record                   rc={woke.returncode} launches={kept.get('launches')} "
                        f"words={words!r} model={kept.get('model')!r} effort={kept.get('effort')!r} "
                        f"missing={A.RECORD_FIELDS - set(kept)} {woke.stderr[-200:]!r}")

    # --- the two lines that exchange wrote, whole ---------------------------------------------------------------
    def line_of(one: dict) -> list:
        """-> a record's line key by key in its order: the hour apart, a policy by its pairs, a flow by the names
        of its sums."""
        return [(name, "<at>" if name == "at" else list(value.items()) if name == "policy"
                 else list(value) if name == "flow" else value) for name, value in one.items()]
    sent = next((one for one in h.messages() if one.get("run") == key), {})
    owed = {"message": [("at", "<at>"), ("from", "house"), ("to", "agents/ag1"), ("run", key), ("message", "say it"),
                        ("policy", [("model", "m-one"), ("effort", "high")])],
            "response": [("at", "<at>"), ("agent", "agents/ag1"), ("run", key), ("index", 1),
                         ("response", "\n\n".join(said)), ("cost_usd", 0.1), ("session_cost_usd", 0.1),
                         ("launches", 1), ("denials", []), ("error", None), ("harness_rc", 0),
                         ("flow", ["principal", "conduction", "pp_input", "pp_result", "tool_input", "tool_result",
                                   "words", "thinking", "calls", "context"]),
                         ("tokens_sent", 300606),
                         ("words", owed_words),
                         ("finals", [{"launch": 1, "chars": len(A.answer_of("stream")),
                                      "text": A.answer_of("stream")}]), ("overruns", 0),
                         ("model", "m-one"), ("effort", "high")]}
    wrote = {"message": line_of(sent), "response": line_of(kept)}
    if wrote == owed:
        held("the two lines that exchange wrote, whole", f"run {key}: its line of messages.jsonl says its "
             f"{len(owed['message'])} keys and its line of responses.jsonl its {len(owed['response'])}, each in its "
             "order with its value -- the hour apart, the flow's sums by their names")
    else:
        failures.append(f"  ✗ the two lines written       {wrote}")

    # --- the faces: `responses` says the agent's last response -- this run's ---------------------------------
    shown = h.call("agent", "responses", "agents/ag1")
    listed = h.call("agent", "exchanges", "agents/ag1", key, "--json")
    rows = rows_of(listed)
    if (shown.returncode == 0 and "witness words" not in shown.stdout and shown.stdout.count(A.PRINTED) == len(said)
            and A.answer_of("stream") not in shown.stdout and "[launch" not in shown.stdout
            and listed.returncode == 0 and len(rows) == 1 and rows[0].get("words") == words
            and rows[0].get("model") == "m-one" and rows[0].get("effort") == "high"):
        held("(b) responses and exchanges --json render them", "the composed response, each words once; "
             "words, model and effort on the exchange's line")
    else:
        failures.append(f"  ✗ (b) faces                    rc={shown.returncode}/{listed.returncode} "
                        f"{shown.stdout[-300:]!r} rows={rows!r}")

    # --- words no reader can read: `exchanges --json` says them as their line does ---------------------------
    odd = [["a", {"launch": 1, "text": "b"}], "a text"]    # an item that is no mapping; no list at all
    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as messages, \
            (h.records / "responses.jsonl").open("a", encoding="utf-8") as responses:
        for rank, unread in enumerate(odd, 1):             # two exchanges of before written after the real one
            at = f"2099-01-01T00:00:{rank}0+00:00"
            messages.write(json.dumps({**sent, "at": at, "message": f"odd {rank}"}) + "\n")
            responses.write(json.dumps({**kept, "at": at, "index": rank + 1, "words": unread}) + "\n")
    aged_rows = rows_of(h.call("agent", "exchanges", "agents/ag1", key, "--json"))
    if [one.get("words") for one in aged_rows] == [words] + odd:
        held("(c) words no reader can read are said as their line says them", f"run {key}: exchanges --json "
             "renders the real exchange's words, then a list one item of which is no mapping and a text, each as "
             "its line of responses.jsonl says it")
    else:
        failures.append(f"  ✗ (c) unread words             {[one.get('words') for one in aged_rows]!r}")

    # --- the worded witness: the words, and their composition -----------------------------------------------
    woke, key, kept = woken(h, "say three", "worded")
    launches = kept.get("launches") if isinstance(kept.get("launches"), int) else 0
    owed_words = [{"launch": 1, "text": A.PRINTED}] * len(h.dues(key))
    texts = [one["text"] for one in owed_words]            # the first text of a launch stands before a call: an aside
    owed_finals = [{"launch": n, "chars": len(f"second words {n}\n\nthird words {n}"),
                    "text": f"second words {n}\n\nthird words {n}"} for n in range(1, launches + 1)]
    words = kept.get("words") or []
    response = kept.get("response") or ""
    if (woke.returncode == 0 and launches == 1 and owed_words and words == owed_words and response == "\n\n".join(texts)
            and kept.get("finals") == owed_finals and "tokens_sent" in kept and kept["tokens_sent"] is None):
        held("(a) the response composed of the words", f"run {key}: {launches} launch, {len(words)} words under "
             "their launch -- the productions due handed --; the texts no call follows one last message of their "
             "characters, the blank one dropped; the response carries the words, in order, each once")
    else:
        failures.append(f"  ✗ (a) composed                 rc={woke.returncode} launches={launches} words={words!r} "
                        f"response={response!r} finals={kept.get('finals')!r} sent={kept.get('tokens_sent')!r} {woke.stderr[-200:]!r}")

    # --- the flow: the words once, the `agent` event without text ---------------------------------------------
    flowed = h.call("agent", "flow", "agents/ag1", key, "--json")
    lines = rows_of(flowed)
    agents = [one for one in lines if one.get("kind") == "agent"]
    spoken = [one.get("text") for one in lines if one.get("kind") == "words"]
    if flowed.returncode == 0 and len(agents) == launches and not any("text" in one for one in agents) and spoken == texts:
        held("(b) the agent event carries no text", f"{len(agents)} agent events, their metadata alone; the words said "
             "once each, in order")
    else:
        failures.append(f"  ✗ (b) flow                     rc={flowed.returncode} agents={agents!r} words={spoken!r}")

    # --- the bare AWAIT under a law of production: one launch, the AWAIT unlaunched ----------------------------
    woke, key, kept = woken(h, "un")
    events = flow_of(h, key)
    kinds = [one.get("kind") for one in events]
    conduction_events = [one for one in events if one.get("kind") == "conduction"]
    last_text = conduction_events[-1].get("text", "") if conduction_events else ""
    if (woke.returncode == 0 and kept.get("launches") == 1 and "1 launch(es)" in woke.stderr
            and "· parked ·" in woke.stderr and kinds.count("conduction") == 1 and kinds.count("agent") == 1
            and "INFER proof" in last_text and not re.search(r"^▶ AWAIT", last_text, re.M)
            and "served held output" in woke.stderr and "launch 2" not in woke.stderr
            and woke.stdout.strip() == A.composed(kept) and A.answer_of("play") not in woke.stdout):
        held("(a) the bare AWAIT launches nothing", "one launch -- the boot with the WORK, the proof fused under "
             "it --, the AWAIT served and not launched, the run parked, the response composed of the launch's words, its last "
             "message not among them")
    else:
        failures.append(f"  ✗ (a) the AWAIT               rc={woke.returncode} launches={kept.get('launches')} "
                        f"kinds={kinds} final_launched={bool(re.search(r'^▶ AWAIT', last_text, re.M))} {woke.stderr[-300:]!r}")

    # --- the door: each block never served held, one launch each; the AWAIT unlaunched -------------------------
    home = h.agent_meta / "procs"
    (home / "LAPS.md").write_text(LAPS, encoding="utf-8")
    (home / "TURN.md").write_text(TURN, encoding="utf-8")   # the law of production gone: the door's own laws alone

    def doors() -> dict:
        A.cli(h.engine, "--instance", str(h.agent_meta), "-build", cwd=h.ws, env=h.env)
        where = bench.temp() / "doors"
        before = set(h.keys())
        woke = h.call("agent", "run", "agents/ag1", "--message", "play the door", *h.harnessed_at("doors", where))
        key = next((one for one in h.keys() if one not in before), "")
        kept = next((one for one in reversed(h.responses()) if key and one.get("run") == key), {})
        events = h.trace(key) if key else []
        return {"key": key, "launches": kept.get("launches"), "rc": woke.returncode, "out": woke.stdout.strip(),
                "proofs": sum(1 for e in events if e.get("kind") == "answer"
                              and str(e.get("instruction", "")).startswith("PROVE")),
                "inline": sum(1 for e in events if e.get("kind") == "inline"),
                "held": sum(1 for e in events if e.get("kind") == "held"),
                "acts": [e.get("act") for e in events if e.get("kind") == "held"],
                "parked": "· parked ·" in woke.stderr, "calls": len(h.calls(where)), "err": woke.stderr[-300:],
                "dues": A.dues_of(events)}

    m = doors()
    if (m["rc"] == 0 and m["launches"] == 5 and m["proofs"] == 3 and m["inline"] == 0 and m["held"] == 5
            and m["acts"] == ["door", "value", "value", "value", "value"] and m["parked"] and m["dues"] and m["calls"] == len(m["dues"]) + 5   # the prints, the door, the field, 3 proofs
            and m["out"] == A.opening(m["dues"])):
        held("(a) the door, one launch per block never served", f"run {m['key']}: the witness handed the prints "
             "due and opened LAPS on the pending WORK; the door's block and each lap's held, none inline, each its "
             f"launch -- the field piped, 3 laps' productions handed and 3 proofs piped ({m['launches']} launches, "
             f"{m['calls']} calls, {len(m['dues'])} prints due, held {m['acts']}); the AWAIT held, served, not "
             "launched; parked")
    else:
        failures.append(f"  ✗ (a) the door                 {m!r}")

    # --- a line of messages.jsonl and of responses.jsonl, there and back ---------------------------------------
    skill = h.module()
    text = lambda one: json.dumps(one, ensure_ascii=False)   # noqa: E731
    whole = {"messages": {"at": "2026-10-01T09:00:00+00:00", "from": "house", "to": "agents/ag1", "run": "abc123",
                          "message": None, "policy": {"model": "m", "max_budget_usd": 1.5, "permissions": "strict",
                                                      "effort": "high"},
                          "conducted": False, "tag": "t1", "pid": 4242},
             "responses": {"at": "2026-10-01T09:00:05+00:00", "agent": "agents/ag1", "run": "abc123", "index": 3,
                           "response": None, "cost_usd": None, "session_cost_usd": 0.5, "launches": 2,
                           "denials": [{"tool": "Bash"}], "error": None, "harness_rc": 0,
                           "budget": {"cap": 1.0, "spent": 1.0}, "quota": {"until": None, "said": "s"},
                           "conducted": False, "flow": {"words": 3}, "tokens_sent": 1200, "pending": "next",
                           "words": [{"launch": 1, "text": "a"}], "finals": [{"launch": 1, "chars": 4, "text": "abcd"},
                                                                      {"launch": 2, "chars": 0}],
                           "overruns": 0, "model": None, "effort": "low"}}
    before = {"messages": {"at": "2026-09-27T09:00:00+00:00", "to": "agents/ag1", "from": "house", "message": "old",
                           "policy": {"turns": 3, "model": "m"}, "handed": True, "run": None},
              "responses": {"run": "abc123", "agent": "agents/ag1", "at": "2026-09-27T09:00:05+00:00",
                            "response": "old", "harness_rc": 0, "cost_usd": None, "turns": 4}}
    kinds = {"messages": (skill.Message, h.messages()), "responses": (skill.Response, h.responses())}
    strays, bare = {}, {}
    for record, (kind, lines) in kinds.items():
        for one in lines + [whole[record], before[record]]:
            if text(kind.of(one).json()) != text(one):
                strays.setdefault(record, []).append(kind.of(one).json())
        anew = dataclasses.replace(kind.of(whole[record]), keys=None, kept=())   # composed, as its writer does
        if text(anew.json()) != text(whole[record]):
            strays.setdefault(record, []).append(anew.json())
        bare[record] = sorted(set(whole[record]) - set(kind().json()))
    flows = [{"principal": 4, "conduction": 30, "pp_input": 1, "pp_result": 2, "tool_input": 0, "tool_result": 0,
              "words": 5, "thinking": 7, "calls": 2, "context": 900},      # a call measured: the context said
             {"words": 5, "calls": 1, "principal": 4, "cached": 12},        # another order, no context, a sum unnamed
             None]
    aged = [skill.Response.of({**before["responses"], "flow": flow}) for flow in flows]
    for flow, one in zip(flows, aged):                     # a line of before with its `flow`: the same text
        if text(one.json()) != text({**before["responses"], "flow": flow}):
            strays.setdefault("flow", []).append(one.json())
    for flow in flows:                                     # the sums alone: a response keeps what they cannot give back
        if flow is not None and text(skill.Sums.of(flow).json()) != text(flow):
            strays.setdefault("sums", []).append(skill.Sums.of(flow).json())
    named = [one.name for one in dataclasses.fields(skill.Sums)]
    voices = list(skill.Sums().voices())                   # the voices: the constant, the method, the fields
    even = (voices == list(skill.FLOW_VOICES) == named[:len(voices)]
            and named[len(voices):] == ["calls", "context", "keys", "kept"])
    sums = [(one.flow.context, one.flow.words, one.flow.calls, one.flow.thinking) if one.flow is not None else None
            for one in aged]                               # its sums read by their fields
    spoken = [[{"launch": 1, "text": "a"}, {"launch": 2, "text": ""}],     # the writer's order
              [{"text": "b", "launch": 3, "delta": True}],                 # another order, a key unnamed
              [], None]
    voiced = [skill.Response.of({**before["responses"], "words": words}) for words in spoken]
    for words, one in zip(spoken, voiced):                 # a line of before with its `words`: the same text
        if text(one.json()) != text({**before["responses"], "words": words}):
            strays.setdefault("words", []).append(one.json())
    for one in [one for words in spoken for one in words or []]:    # each words alone, for the same reason
        if text(skill.Said.of(one).json()) != text(one):
            strays.setdefault("said", []).append(skill.Said.of(one).json())
    said = [[(one.launch, one.text) for one in each.words] if each.words is not None else None for each in voiced]
    old = skill.Message.of(before["messages"]), skill.Response.of(before["responses"])
    read = (old[0].sender, old[0].policy.model, old[0].tag, old[1].response, old[1].index, old[1].words)
    if (not strays and all(lines for _, lines in kinds.values())
            and sums == [(900, 5, 2, 7), (None, 5, 1, 0), None] and even
            and said == [[(1, "a"), (2, "")], [(3, "b")], [], None]
            and bare == {"messages": ["conducted", "pid", "tag"], "responses": ["budget", "conducted", "pending", "quota"]}
            and read == ("house", "m", None, "old", None, None)):
        held("a line of messages and of responses reads there and back", f"{len(kinds['messages'][1])} lines of "
             f"messages.jsonl and {len(kinds['responses'][1])} of responses.jsonl as the exchanges wrote them, a "
             "line of the writer's order with every key, a line of a form of before: the same JSON text each; "
             f"composed anew the same; unnamed, a type writes none of {bare}; a line of before with its flow "
             f"({len(flows)} forms) and with its words ({len(spoken)} forms): the same text, read by their fields; the "
             f"{len(voices)} voices the same in FLOW_VOICES, in Sums.voices() and in its fields")
    else:
        failures.append(f"  ✗ the lines there and back    strays={strays} bare={bare} read={read} sums={sums} "
                        f"voices={voices} named={named} "
                        f"said={said} "
                        f"lines={ {record: len(lines) for record, (_, lines) in kinds.items()} }")

    # --- a field named after the fact on a line read: the writing refuses ---------------------------------------
    opened = {"at": "2026-10-01T09:00:00+00:00", "agent": "agents/ag1", "run": "abc123", "repo": "/r",
              "path": "work/abc123", "branch": "agent/ag1/abc123", "base": "main@1234567", "state": "open"}
    read = {"messages": old[0], "responses": old[1], "workdirs": skill.Workdir.of(opened)}
    late = {"messages": {"tag": "t2"}, "responses": {"index": 4}, "workdirs": {"reason": "no"}}
    lost = {}
    for record, one in read.items():
        try:
            lost[record] = dataclasses.replace(one, **late[record]).json()
        except ValueError:
            lost[record] = None
    carried = dataclasses.replace(old[0], message="new").json()
    sent = read["workdirs"].sent("t1", skill.Push(pushed=False, commits=None, dirty=True, reason="still")).json()
    pruned = read["workdirs"].pruned("t2").json()
    if (lost == {record: None for record in read} and text(carried) == text({**before["messages"], "message": "new"})
            and text(sent) == text({**opened, "at": "t1", "state": "unpushed", "pushed": False, "commits": None,
                                    "dirty": True, "reason": "still"})
            and text(pruned) == text({**opened, "at": "t2", "state": "pruned"})):
        held("a field named after the fact on a line read is not written", f"{sorted(late)}: a replace that names "
             "a field the line does not carry, then json(): a ValueError each; a field the line carries is written; "
             "a push and a prune carry their keys and pass")
    else:
        failures.append(f"  ✗ a field named after the fact  lost={lost} carried={carried} sent={sent} pruned={pruned}")
    return 0
