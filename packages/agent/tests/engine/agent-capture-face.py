"""Scenario `agent-capture-face` -- the face `words` of an exchange is what the agent HANDED to pp, and that alone
-- on one house whose agent's turn asks productions said to the principal (among them the catalog's table and a
contributor's step), as many as the conduction asks -- the `print-due` of the run's trace, never a count typed --,
under a witness that says a text before each of its print calls:
- (a) the words are the captures: the exchange's `words` carry, under their launch, the `given` of each `answer`
  of the trace said on that channel -- byte for byte, a production of several lines with an indented one and a
  blank one, as the witness handed it --, in the order of the trace; the last message of the launch is none
- (b) an aside is no words: the text the witness wrote before each call stands neither in `words` nor in
  `response`; `agent flow --json` says each under its own kind (`ASIDE`), in order
- (c) the order of the flow: the words of a capture follow the result of the call that handed it and come before
  the next call; the last message comes last, under `FINAL`
- (d) the response: a witness whose last message is the hand-back mark alone -- `response` joins the captures and
  carries no such mark; `exchanges --json` says the same words and the same response as the record; the flow says
  that last message under `FINAL` with no characters and no `text`, the record's `finals` the same
- (e) a print refused is not rendered: a first print handed empty, refused in place, then handed whole -- one
  words per production, the text pp took; at the bound of the repairs -- every print handed empty -- the debt is
  lifted without a capture and the words carry nothing
- (f) under the modelled LLM: the words carry the captures of the trace, in order, and nothing else
- (h) one capture a result: a witness that writes its output once its print calls are over -- every
  production stands on the trace when the house reads the result of the first call --: each capture is said at the
  result of its own call, the order of the flow and the sums of the record as in (c) and (g)
- (i) the last message is no words (agent 1.1.0): a launch whose last message is long -- the words carry the
  productions alone, the response is theirs, the last message stands under `FINAL` in the flow with its `text`, its
  blanks stripped, and its `chars`, the length of that text; the record's `finals` keep the same; the run's trace
  holds none of it
- (j) the three forms of a last message (agent 1.1.0): the skill's `hearer`, fed by a reader that passes every
  text, says the hand-back mark alone as a `FINAL` of no characters and no `text`, a text of blanks alone as no
  characters and an empty `text`, any other text by its `text` stripped and its `chars`; its `Flow` keeps each in
  `finals` in that same form, none of them an overrun
- (g) a capture is counted once: the sums of the record count each production among the model's text (`words`,
  with the asides, the last message apart) and take its tokens out of the input of the console's call that handed
  it (`pp_input`), which keeps what the call says beside the production
"""
from __future__ import annotations

import json
import types

from conductor import metrics
from tests.harness import support

A = support(__file__, "agent")
ECHO = ("---\nname: ECHO\nkind: proc\ndescription: a contributor behind the work\nattach: turn.end\n"
        "proc: |\n  INFER\n---\nECHO speaks\n")
CALLS = ("aside", "tool", "tool-result", "words")       # what a launch says of its texts and of its calls
FINAL = getattr(A.skill(), "FINAL", "<no kind>")        # the last message of a launch: its text and its length


def woken(h, message: str, mode: str, *flags: str):
    """`agent run` under the witness in `mode` -> (the call, the key of the run it opened, its record)."""
    before = set(h.keys())
    woke = h.wake(message, mode, *flags)
    key = next((one for one in h.keys() if one not in before), "")
    kept = next((one for one in reversed(h.responses()) if key and one.get("run") == key), {})
    return woke, key, kept


def rows_of(played) -> list[dict]:
    """-> the objects of a `--json` call, one per line; [] when a line does not read."""
    try:
        return [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
    except ValueError:
        return []


def owed(h, key: str, kept: dict, handed: list[dict]) -> list[dict]:
    """-> the words an exchange owes: under each launch, the captures of the trace the witness handed in it, in
    the order of the trace -- its last message is none of them."""
    launch_of = {one["text"]: one["launch"] for one in handed}
    captures = [(launch_of.get(text), text) for text in h.captured(key)]
    return [item for n in range(1, int(kept.get("launches") or 0) + 1)
            for item in [{"launch": n, "text": text} for launch, text in captures if launch == n]]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    aside = getattr(h.module(), "ASIDE", "<no kind>")
    (h.agent_meta / "procs").mkdir(exist_ok=True)
    (h.agent_meta / "procs" / "ECHO.md").write_text(ECHO, encoding="utf-8")
    A.cli(h.engine, "--instance", str(h.agent_meta), "-build", cwd=h.ws, env=h.env)

    # --- (a) the words are the captures ------------------------------------------------------------------------
    woke, key, kept = woken(h, "say them", "printing")
    handed, given, dues = h.prints(), h.captured(key), h.dues(key)
    words, last = kept.get("words") or [], A.answer_of("printing")
    if (woke.returncode == 0 and dues and len(given) == len(dues) and given == [one["text"] for one in handed]
            and all(text.count("\n") == 3 for text in given) and words == owed(h, key, kept, handed)
            and last not in [one.get("text") for one in words]):
        held("(a) the words are the captures", f"run {key}: {len(given)} productions of several lines on the trace "
             "as the witness handed them; the words carry them byte for byte under their launch, in order, and not "
             "the last message")
    else:
        failures.append(f"  ✗ (a) the captures             rc={woke.returncode} given={given!r} "
                        f"handed={[one['text'] for one in handed]!r} words={words!r} dues={dues} "
                        f"{woke.stderr[-300:]!r}")

    # --- (g) a capture is counted once --------------------------------------------------------------------------
    tokens = metrics.tokens
    typed = [tokens(json.dumps(one["input"], ensure_ascii=False)) for one in handed]
    sums = kept.get("flow") or {}
    owed_sums = {"pp_input": sum(max(0, size - tokens(one["text"])) for size, one in zip(typed, handed)),
                 "words": sum(tokens(one["aside"]) + tokens(one["text"]) for one in handed)}
    if (handed and all(size > tokens(one["text"]) > 0 for size, one in zip(typed, handed))
            and {voice: sums.get(voice) for voice in owed_sums} == owed_sums):
        held("(g) a capture is counted once", f"{len(handed)} productions: their tokens among the words "
             f"({owed_sums['words']} with the asides, the last message apart), out of the input of their calls "
             f"({owed_sums['pp_input']} left of {sum(typed)})")
    else:
        failures.append(f"  ✗ (g) counted once             sums={sums} owed={owed_sums} typed={typed}")

    # --- (b) an aside is no words ------------------------------------------------------------------------------
    flowed = [one for one in rows_of(h.call("agent", "flow", "agents/ag1", key, "--json"))]
    asides = [one["aside"] for one in handed]
    apart = [one.get("text") for one in flowed if one.get("kind") == aside]
    spoken = [one.get("text") for one in words]
    if (asides and apart == asides and not set(asides) & set(spoken)
            and not any(one in (kept.get("response") or "") for one in asides)):
        held("(b) an aside is no words", f"{len(asides)} texts written before a call: none in the words, none in "
             f"the response; the flow says each under `{aside}`, in order")
    else:
        failures.append(f"  ✗ (b) the asides               asides={asides!r} apart={apart!r} words={spoken!r} "
                        f"response={kept.get('response')!r}")

    # --- (c) the order of the flow -----------------------------------------------------------------------------
    calls = [one for one in flowed if one.get("kind") in CALLS + (FINAL,)]   # the steps of the run stand between
    order = [one.get("kind") for one in calls]
    capture_at = [rank for rank, one in enumerate(calls) if one.get("kind") == "words" and one.get("text") in given]
    piped = [calls[rank - 1].get("kind") == "tool-result" and calls[rank - 2].get("pp") is True
             for rank in capture_at]
    if (kept.get("launches") == 1 and order == list(CALLS) * len(given) + [FINAL]
            and len(piped) == len(given) and all(piped)
            and [calls[rank].get("text") for rank in capture_at] == given):
        held("(c) a capture follows its call", f"{len(given)} times an aside, the console's call, its result, the "
             "words of the capture; the last message last, its text and its length")
    else:
        failures.append(f"  ✗ (c) the order                launches={kept.get('launches')} order={order} piped={piped}")

    # --- (h) one capture a result: a launch that writes its output once its calls are over ---------------------
    before = len(h.prints())
    woke, key, kept = woken(h, "say them, write late", "late")
    handed, given, dues = h.prints()[before:], h.captured(key), h.dues(key)
    calls = [one for one in rows_of(h.call("agent", "flow", "agents/ag1", key, "--json"))
             if one.get("kind") in CALLS + (FINAL,)]
    capture_at = [rank for rank, one in enumerate(calls) if one.get("kind") == "words" and one.get("text") in given]
    typed = [tokens(json.dumps(one["input"], ensure_ascii=False)) for one in handed]
    sums = kept.get("flow") or {}
    owed_sums = {"pp_input": sum(max(0, size - tokens(one["text"])) for size, one in zip(typed, handed)),
                 "words": sum(tokens(one["aside"]) + tokens(one["text"]) for one in handed)}
    if (woke.returncode == 0 and dues and len(given) == len(dues) and given == [one["text"] for one in handed]
            and [one.get("kind") for one in calls] == list(CALLS) * len(given) + [FINAL]
            and [calls[rank].get("text") for rank in capture_at] == given
            and all(calls[rank - 1].get("kind") == "tool-result" for rank in capture_at)
            and {voice: sums.get(voice) for voice in owed_sums} == owed_sums):
        held("(h) one capture a result", f"run {key}: the {len(given)} productions stand on the trace before the house reads "
             "the first result -- each is said at the result of its own call, the order of the flow and the sums "
             "as when the launch writes as it goes")
    else:
        failures.append(f"  ✗ (h) one a result             rc={woke.returncode} given={len(given)} dues={dues} "
                        f"order={[one.get('kind') for one in calls]} sums={sums} owed={owed_sums}")

    # --- (d) the response: the captures joined, no hand-back mark ----------------------------------------------
    before = len(h.prints())
    woke, key, kept = woken(h, "say them and hand back", "quiet")
    handed, given, dues = h.prints()[before:], h.captured(key), h.dues(key)
    rows = rows_of(h.call("agent", "exchanges", "agents/ag1", key, "--json"))
    row = rows[0] if len(rows) == 1 else {}
    quiet = [one for one in rows_of(h.call("agent", "flow", "agents/ag1", key, "--json")) if one.get("kind") == FINAL]
    if (woke.returncode == 0 and dues and len(given) == len(dues) and kept.get("words") == owed(h, key, kept, handed)
            and kept.get("response") == "\n\n".join(given)
            and row.get("words") == kept.get("words") and row.get("response") == kept.get("response")
            and quiet and all("text" not in one and one.get("chars") == 0 for one in quiet)
            and kept.get("finals") and all(set(one) == {"launch", "chars"} and one["chars"] == 0
                                           for one in kept["finals"])):
        held("(d) the response joins the captures", f"run {key}: a last message that is the hand-back mark alone -- "
             "the response is the captures joined, the mark is not in it; exchanges --json says the record's words "
             f"and response; the flow's {len(quiet)} `{FINAL}` and the record's finals carry no characters and no text")
    else:
        failures.append(f"  ✗ (d) the response             rc={woke.returncode} given={given!r} dues={dues} "
                        f"words={kept.get('words')!r} response={kept.get('response')!r} row={row!r} "
                        f"flow finals={quiet!r} finals={kept.get('finals')!r}")

    # --- (e) a print refused is not rendered --------------------------------------------------------------------
    before = len(h.prints())
    woke, key, kept = woken(h, "say it badly once", "misprint")
    handed, given, dues = h.prints()[before:], h.captured(key), h.dues(key)
    kinds = [one.get("kind") for one in h.trace(key)]
    whole = [one for one in handed if one["text"]]
    if (woke.returncode == 0 and dues and len(handed) == len(dues) + 1 and len(whole) == len(dues) and given == [one["text"] for one in whole]
            and "repair-in-place" in kinds
            and kept.get("words") == owed(h, key, kept, whole)):
        held("(e) a print refused then handed whole is one words", f"run {key}: {len(handed)} print calls, the first "
             f"empty and refused in place; the words carry the {len(whole)} productions pp took, once each")
    else:
        failures.append(f"  ✗ (e) refused then whole       rc={woke.returncode} dues={dues} handed={handed!r} given={given!r} "
                        f"kinds={kinds} words={kept.get('words')!r} {woke.stderr[-300:]!r}")

    woke, key, kept = woken(h, "never say it", "waived")
    kinds, dues = [one.get("kind") for one in h.trace(key)], h.dues(key)
    launches = int(kept.get("launches") or 0)
    if (woke.returncode == 0 and not h.captured(key) and dues and kinds.count("print-waived") == len(dues)
            and launches >= 1
            and kept.get("words") == []):
        held("(e) at the bound, no words", f"run {key}: every print handed empty -- {len(dues)} debts lifted without a "
             "capture; the words carry nothing")
    else:
        failures.append(f"  ✗ (e) the bound                rc={woke.returncode} dues={dues} captured={h.captured(key)!r} "
                        f"kinds={kinds} words={kept.get('words')!r} {woke.stderr[-300:]!r}")

    # --- (f) under the modelled LLM ------------------------------------------------------------------------------
    known = set(h.keys())
    woke = h.call("agent", "run", "agents/ag1", "--provider", "model", "--message", "say them")
    key = next((one for one in h.keys() if one not in known), "")
    kept = next((one for one in reversed(h.responses()) if key and one.get("run") == key), {})
    given, spoken = h.captured(key) if key else [], [one.get("text") for one in kept.get("words") or []]
    dues = h.dues(key) if key else []
    launches = int(kept.get("launches") or 0)
    others = [text for text in spoken if text not in given]
    if (woke.returncode == 0 and dues and len(given) == len(dues) and [text for text in spoken if text in given] == given
            and not others and launches >= 1):
        held("(f) the modelled LLM's words are its captures", f"run {key}: {len(given)} productions handed by their "
             f"print call, the words carry them in order and nothing else, over {launches} launch(es)")
    else:
        failures.append(f"  ✗ (f) the model                rc={woke.returncode} dues={dues} given={given!r} words={spoken!r} "
                        f"launches={launches} {woke.stderr[-300:]!r}")

    # --- (i) the last message is no words ---------------------------------------------------------------------
    final = getattr(h.module(), "FINAL", "<no kind>")
    woke, key, kept = woken(h, "say it all again", "long")
    long, spoken = A.LONG.strip(), [one.get("text") for one in kept.get("words") or []]
    flowed = rows_of(h.call("agent", "flow", "agents/ag1", key, "--json"))
    finals = [one for one in flowed if one.get("kind") == final]
    kept_texts = [(h.records / "responses.jsonl").read_text(encoding="utf-8"),
                  json.dumps(flowed, ensure_ascii=False), json.dumps(h.trace(key), ensure_ascii=False)]
    if (woke.returncode == 0 and long not in spoken and long not in (kept.get("response") or "")
            and kept.get("response") == A.composed(kept)
            and [(one.get("chars"), one.get("text")) for one in finals] == [(len(long), long)]
            and [(one.get("chars"), one.get("text")) for one in kept.get("finals") or []] == [(len(long), long)]
            and [long in one for one in kept_texts] == [True, True, False]):
        held("(i) the last message is no words", f"run {key}: a last message of {len(long)} characters -- not in "
             f"the words nor the response; the flow says it under `{final}` with its text and its length, the "
             "record's finals the same; the trace holds none of it")
    else:
        failures.append(f"  ✗ (i) the last message        rc={woke.returncode} words={spoken!r} "
                        f"response={kept.get('response')!r} finals={finals!r} record={kept.get('finals')!r} "
                        f"kept={[long in one for one in kept_texts]} {woke.stderr[-300:]!r}")

    # --- (j) the three forms of a last message, as the hearer says them -------------------------------------------
    skill = h.module()
    told: list[tuple[str, dict]] = []

    class Reader:
        """A reader that passes every text the harness writes, blanks alone among them."""
        def heard(self, line: str) -> list[dict]:
            return [{"kind": "words", "text": line}]

        def end(self) -> list[dict]:
            return []

    conductor = types.SimpleNamespace(Refusal=Exception, adapters=types.SimpleNamespace(
        console_of=lambda _: h.ws / "pp", reader=lambda grammar, meta: Reader()))
    flow = skill.Flow(metrics.tokens)
    forms = [skill.HAND_BACK, " \n\t ", "  the text kept\n"]
    for launch, said in enumerate(forms, 1):
        flow.launch("prompt", "")
        heard = skill.hearer(conductor, h.agent_meta, "reader", "k",
                             lambda k, line, kind, one: told.append((kind, one)), 1, launch, flow)
        heard(said)
        heard.end()
    owed_forms = [{"chars": 0}, {"chars": 0, "text": ""}, {"chars": len("the text kept"), "text": "the text kept"}]
    spoken_forms = [{k: v for k, v in one.items() if k not in ("exchange", "launch")} for kind, one in told
                    if kind == final]
    kept_forms = [one.json() for one in flow.finals]
    if (spoken_forms == owed_forms and kept_forms == [{"launch": n, **one} for n, one in enumerate(owed_forms, 1)]
            and not any(one.over() for one in flow.finals)):
        held("(j) the three forms of a last message", f"the hand-back mark: {owed_forms[0]}; blanks alone: "
             f"{owed_forms[1]}; a text: its text stripped and its length -- the flow's finals the same, none over")
    else:
        failures.append(f"  ✗ (j) the three forms         said={spoken_forms!r} kept={kept_forms!r}")
    return 0
