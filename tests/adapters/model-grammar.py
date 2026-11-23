"""Scenario `model-grammar` -- 6 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
l-adaptateur-model and la-feuille-de-reponse, 2026-10-27/28): the modelled LLM reads a REAL block by its
structure and the engine's constants, and finds every text its CANDIDATE forms in the data -- what the case
compares is read from the engine (a block it rendered, its constants) and from the data, never a sentence
typed here:
- a block where a value is due: a member under a law of production, the proof asked -- the line
  read with its form `proof`, its code and its heredoc channel, no closing, the value due read on the line
  naming the form, the one candidate V and the act CALL on both channels
- the boot has no closing and its last segment carries the step: read as T on
  the prompt channel, hand back after the productions; the end of its passage, served by the last of their
  print calls, closes on AWAIT with no call under it: read as M
- a prompt text with no closing and no value due is a step pending, wherever its line stands: a step said
  under a law of its own, then the order block of the caller in a segment that carries no step, reads T;
  the last chunk of a cut output, which carries the step's line and no heading, reads T
- the engine's own lines that answer a call are read: every line of `messages.ACKNOWLEDGED`, the bounce
  (`messages.bounced`), `principal-advances`, the refusals that stop the conduction, a gesture, any
  other refusal -- each to its row of ANSWERS and its act; a line the data never saw is a `hole`
- a result that carries no line of pp is a script's own output where the call typed was a gesture: read
  as the gesture's answer; behind any other call, and behind a gesture whose result carries a line of pp
  the data never saw, it stays a `hole`; a gesture is any call that names a skill by `-s`, whatever the
  script is called -- a value handed, the bare call, a view are none
- no reading of READINGS is a hole: for every reading, a text of its traits leads `foot` to exactly its
  forms, and the harness chooses no form among several (no site picks a first row)
- a value due is read on its own line when the line that asks the last message (`=> response`) stands
  behind it; without the value, the same text reads a production due to the principal
- an output cut between two steps: the line of the step read in the chunk before the last is KEPT, with
  the memory of the session, and nothing is said; its production is said when the output is whole, before
  the value the last chunk asks
- the module imports nothing of the engine but `language`, reads its two marks from the module that
  prints them, and names no record of the run
"""
from __future__ import annotations

import ast
import os

from conductor.core import messages
from conductor import Conductor, persistence
from conductor.core import language
from conductor.rendering.render import last_line
from conductor.state import context
from tests.harness import stepped, support

M = support(__file__, "model")
STOPPING = ("repair-exhausted", "exec-refused", "artifact-stale")
# the witness of a cut between two steps: a root that calls FORKED -- one step under a brief, then the
# fork its `next:` injects under its own, each brief over half the cap the case sets
CUT_CAP = 2000
CUT = {
    "CUTROOT.md": "---\nname: CUTROOT\nkind: proc\ndescription: the root of the witness\nproc: |\n"
                  "  CALL FORKED.md\n  INFER\n---\n\nroot\n",
    "FORKED.md": ("---\nname: FORKED\nkind: proc\ndescription: one step, then a fork\nfusion: max\n"
                  "next: LEFT.md RIGHT.md\nchoose: |\n"
                  + "".join(f"  fork line {n:04d} of the choice\n" for n in range(34))
                  + "proc: |\n  INFER\n---\n\n"
                  + "".join(f"brief line {n:04d} of the step\n" for n in range(34))),
    "LEFT.md": "---\nname: LEFT\nkind: proc\ndescription: a way\nproc: |\n  INFER\n---\n\nleft\n",
    "RIGHT.md": "---\nname: RIGHT\nkind: proc\ndescription: a way\nproc: |\n  INFER\n---\n\nright\n",
}


# the witness of an order block in a segment of its own: INNER's step, said under a law of its own, then the
# section break of OUTER, whose order block closes the output under OUTER's laws alone
ORDER = {
    "OUTER.md": "---\nname: OUTER\nkind: proc\ndescription: calls the inner step, then breaks\nproc: |\n"
                "  CALL INNER.md\n  §\n  INFER\n---\n\nouter\n",
    "INNER.md": "---\nname: INNER\nkind: proc\ndescription: one step under a law of its own\n"
                "constraints.behavior: |\n  IN1  the inner step keeps to its part\nproc: |\n  INFER\n---\n\ninner\n",
}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    harness = M.harness_module()
    semantics = harness.semantics
    console = M.loaded(M.SOURCE / "engine" / "pp.py", "pp_console")

    # --- a value due on the step's line: the proof asked ---------------------------------------------------
    lawful = bench.env("grammar-law")
    lawful.write_member(front="constraints.production: |\n  L1  the answer lands\n")
    proving = harness.grammar(lawful.cli("-new", "hello").stdout)
    for _ in range(4):                                  # the free steps pass by their print; the turn ends on its proof
        if proving is None or proving["due"]:
            break
        key_of_run = proving["key"]
        stepped(lambda: lawful.conductor(key_of_run))
        proving = harness.grammar(lawful.cli(key_of_run, "-peek").stdout)
    proof = next((one for one in (proving or {}).get("instructions", []) if one["form"] == "proof"), None)
    on_tool = harness.foot(proving, "tool") if proving else ((), "", "")
    on_prompt = harness.foot(proving, "prompt") if proving else ((), "", "")
    if (proof and proof["codes"] == ["L1"] and proof["channel"] == language.TOOL_HEREDOC
            and proving["closing"] == "" and proving["call"] == "" and proving["due"] == language.TOOL_HEREDOC
            and on_tool[:2] == (("V",), "CALL") and on_prompt[:2] == (("V",), "CALL")):
        held("the step's line names the value due", "INFER proof [L1] read on the heredoc channel; no closing, "
             "the value due read on the line; V and CALL on both channels")
    else:
        failures.append(f"  ✗ value due                  {proof} {proving and proving['closing']!r} "
                        f"{proving and proving['due']!r} {on_tool} {on_prompt}")

    # --- the boot: no closing -------------------------------------------------------------------------
    marked = bench.env("grammar-principal")
    served = M.cli(marked.engine, "-new", "hello", cwd=marked.root).stdout
    pending = harness.grammar(served)
    at_prompt = harness.foot(pending, "prompt") if pending else ((), "", "")
    last = ""
    for one in (pending or {}).get("instructions", []):    # the productions printed: the last moves the run on
        if one["channel"] == language.TERMINAL:
            last = M.cli(marked.engine, pending["key"], "-print", one["document"], "-", cwd=marked.root,
                         stdin="said").stdout
    ended = harness.grammar(last) if pending else None
    at_end = harness.foot(ended, "prompt") if ended else ((), "", "")
    if (pending and pending["instructions"] and pending["closing"] == "" and pending["call"] == ""
            and pending["instructed"] == "last" and at_prompt == (("T",), "SAY_HAND_BACK", "")
            and ended is not None and ended["closing"] == language.AWAIT and ended["call"] == ""
            and at_end == (("M",), "SAY_HAND_BACK", "")):
        held("the principal's boot hands back, the end of its passage closes on AWAIT", "no closing, the step in "
             "the last segment: T on the prompt channel, the productions printed then the turn handed back; the "
             "last print serves the end of the passage, closed on AWAIT with no call under it: M")
    else:
        failures.append(f"  ✗ principal boot             {pending and pending['closing']!r} {at_prompt} "
                        f"ended={ended and harness.traits_of(ended, 'prompt')} {at_end}")

    # --- no closing and no value due at the prompt: a step pending, wherever its line stands ---------------
    ordered = bench.env("grammar-order", pin=False)
    for name, text in ORDER.items():
        ordered.write(f"procs/{name}", text)
    behind = harness.grammar(M.cli(ordered.engine, "-new", cwd=ordered.root,
                                   env={"PP_DOOR": "OUTER.md"}).stdout)
    cut = bench.env("grammar-last-chunk")
    capped = {"PP_PROMPT_CAP": str(CUT_CAP)}
    piece = M.cli(cut.engine, "-new", "hello", cwd=cut.root, env=capped).stdout
    pieces = 1
    while harness.grammar(piece) and harness.grammar(piece)["closing"] == language.MORE and pieces < 60:
        piece = M.cli(cut.engine, harness.grammar(piece)["key"], cwd=cut.root, env=capped).stdout
        pieces += 1
    tail = harness.grammar(piece)
    traits = [harness.traits_of(one, "prompt") if one else {} for one in (behind, tail)]
    feet = [harness.foot(one, "prompt") if one else ((), "", "") for one in (behind, tail)]
    if (traits[0].get("instructed") == "earlier" and traits[1].get("instructed") == "none" and pieces > 1
            and all((one.get("closing"), one.get("call"), one.get("due")) == ("", "", "") for one in traits)
            and all(one["instructions"] for one in (behind, tail))
            and feet == [(("T",), "SAY_HAND_BACK", "")] * 2):
        held("no closing and no value due at the prompt is a step pending", "INNER's step said, then OUTER's order "
             "block in a segment of its own that carries no step: T; the last of "
             f"{pieces} chunks, the step's line under no heading: T -- the productions said, then the turn handed back")
    else:
        failures.append(f"  ✗ a step pending at the prompt {traits} {feet} pieces={pieces}")

    # --- the answers to a call -------------------------------------------------------------------------
    seen = {}
    for act_name in messages.ACKNOWLEDGED:
        seen[act_name] = harness.answered(messages.held(act_name))
    bounce = harness.answered(messages.bounced())
    advances = harness.answered(messages.refused("principal-advances", messages.refusal_principal_advances()))
    stopping = {code: harness.answered(messages.refused(code, "the detail")) for code in STOPPING}
    other = harness.answered(messages.refused("run-unknown", "the detail"))
    gesture = harness.answered(f"{semantics.ANSWERS['gesture']['said']} · [1] BOOT ▸ TURN\nthe script's output")
    hole = harness.answered("pp: a line the data never saw")
    if (all(row is not None and row["kind"] == "held" and row["act"] == "READ_ON" for _, row in seen.values())
            and bounce[0] == "bounce" and bounce[1]["act"] == "HAND_BACK"
            and advances[0] == "principal-advances" and advances[1]["act"] == "HAND_BACK"
            and all(name == code and row["act"] == "STOP" for code, (name, row) in stopping.items())
            and other[0] == "refusal" and other[1]["act"] == "READ_ON"
            and gesture[0] == "gesture" and gesture[1]["act"] == "READ_ON"
            and hole == (harness.HOLE, None)):
        held("the answers to a call are read", f"{len(seen)} held lines READ_ON, the bounce and principal-advances "
             "HAND_BACK, the three stopping refusals STOP, another refusal READ_ON, a gesture READ_ON; an "
             "unknown line a hole")
    else:
        failures.append(f"  ✗ answers                    {seen} {bounce} {advances} {stopping} {other} {gesture} {hole}")

    # --- a result with no line of pp: a gesture's answer behind a gesture, a hole behind any other call -----
    alone = "the script's own output\n"
    try:
        spoken = [harness.answered(alone, gesture=True), harness.answered(alone, gesture=False),
                  harness.answered(alone), harness.answered("pp: a line the data never saw", gesture=True)]
    except TypeError as refused:
        spoken = [(str(refused), None)]
    typed = {"script": ["abc123", "-s", "pp-wit", "go"], "unprefixed": ["abc123", "-s", "wit", "go"],
             "addressed": ["abc123", "-s", "wit@2", "go"], "value": ["abc123", "a production"],
             "piped": ["abc123", "-"], "bare": ["abc123"], "view": ["abc123", "-peek"], "new": ["-new"]}
    gestures = [name for name, words in typed.items() if harness.gestured(words)]
    if (len(spoken) == 4 and spoken[0] == ("gesture", semantics.ANSWERS["gesture"])
            and spoken[1:] == [(harness.HOLE, None)] * 3
            and gestures == ["script", "unprefixed", "addressed"]):
        held("a script's own output answers a gesture", "a result with no line of pp: `gesture`, READ_ON, behind "
             "a call typed as a gesture; a hole behind any other call, and behind a gesture when a line of pp "
             "the data never saw stands in it; a gesture is a call by `-s`, whatever the script's name -- a "
             "value, the bare call, a view, `-new` are none")
    else:
        failures.append(f"  ✗ a gesture's own output     {[name for name, _ in spoken]} gestures={gestures}")

    # --- no reading is a hole, and no form is chosen among several ---------------------------------------
    holes = []
    for row in semantics.READINGS:
        traits = {name: ("" if row[name] == semantics.ANY else row[name]) for name in semantics.TRAITS}
        if row["instructed"] == semantics.ANY:
            traits["instructed"] = "none"
        reading = {"closing": traits["closing"], "call": traits["call"], "fact": traits["fact"],
                   "instructed": traits["instructed"], "due": traits["due"], "instructions": []}
        forms, act, note = harness.foot(reading, traits["channel"])
        acts = {semantics.FORMS[form][traits["channel"]]["act"] for form in row["forms"]}
        expected_act = next(iter(acts)) if len(acts) == 1 else ""
        if forms != tuple(row["forms"]) or act != expected_act:
            holes.append((traits, forms, act, note))
    text = M.HARNESS.read_text(encoding="utf-8")
    picking = [line for line in text.splitlines() if "rows[0]" in line or "others" in line]
    if not holes and not picking:
        held("no reading is a hole, none is settled by an order", f"{len(semantics.READINGS)} readings: each "
             "reached by a text of its traits with exactly its forms; no site of the harness picks a first row")
    else:
        failures.append(f"  ✗ readings                   holes={holes} picking={picking}")

    # --- the value due is read under the line that asks the last message --------------------------------------
    proof = f"INFER proof [W1] on all produced areas => {language.TOOL_HEREDOC}  (WITNESS)\n"
    asked = (f"{harness.MARK} pp · run abc123 · 00:00:00 · +0:00:00\n\n{harness.MARK} WITNESS{{1-2/2}}\n\n"
             f"{harness.MARK} INSTRUCTION\nWORK any => {language.TERMINAL}  (WITNESS)\n{proof}"
             f"{last_line('WITNESS')}\n")
    valued, lone = harness.grammar(asked), harness.grammar(asked.replace(proof, ""))
    if (valued and valued["due"] == language.TOOL_HEREDOC and valued["valued"]["form"] == "proof"
            and valued["response"] is not None and valued["response"]["form"] == language.EMPTY
            and harness.foot(valued, "prompt")[:2] == (("V",), "CALL")
            and lone and lone["due"] == "" and lone["valued"] is None and lone["response"] is not None
            and harness.foot(lone, "prompt")[0] == ("T",)):
        held("the last message never hides the value due", "an output whose proof is followed by the line "
             "`=> response`: the value is read due on the proof's line (V, the call), the last message kept apart; "
             "without the proof the same text reads a production due to the principal (T)")
    else:
        failures.append(f"  ✗ the value under the line    {valued and (valued['due'], valued['response'])} "
                        f"{lone and (lone['due'], lone['response'])}")

    # --- a line read in a chunk before the last is kept, and said when the output is whole -----------------
    cut = bench.env("grammar-chunk")
    cut.write("SETTINGS.md", f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {CUT_CAP}\n---\n")
    for name, text in CUT.items():
        cut.write(name, text)
    server = cut.conductor()
    server.forget()
    os.environ[context.PROMPT_CAP] = str(CUT_CAP)    # the cap the principal's launcher names on its calls
    try:
        chunks = [server.rendered(server.start(cut.made / "CUTROOT.md"))]
        while server.pending() and len(chunks) < 400:
            chunks.append(server.next_chunk())
    finally:
        os.environ.pop(context.PROMPT_CAP, None)
    readings = [harness.grammar(one) for one in chunks]
    lined = [rank for rank, one in enumerate(readings) if one and one["instructions"]]
    session = f"grammar-chunk-{persistence.run_id_of(persistence.slots(cut.made)[0])}"
    reader, voiced = harness.Model("conform", session, cut.root), []
    reader.say = lambda kind, **fields: voiced.append(kind)
    for one in readings[:-1]:
        reader.keep(one)
    kept = [(instruction["keyword"], instruction["channel"]) for instruction, _ in reader.kept]
    remembered = [(instruction["keyword"], instruction["channel"])
                  for instruction, _ in harness.Model("conform", session, cut.root).kept]
    silent = list(voiced)
    reader.spoken(readings[-1], "tool")
    last = readings[-1]
    if (len(chunks) > 2 and all(one is not None for one in readings)
            and lined == [len(chunks) - 2, len(chunks) - 1]
            and all(one["fact"] == "reading" for one in readings[:-1]) and not last["fact"]
            and kept == [("INFER", language.TERMINAL)] and remembered == kept and not silent
            and voiced == ["tool", "tool-result"] and not reader.kept
            and not harness.Model("conform", session, cut.root).kept
            and last["valued"] and last["valued"]["keyword"] == "PICK" and last["options"]):
        held("a line read in a chunk is kept until the output is whole",
             f"{len(chunks)} chunks under {CUT_CAP}: the step's line stands in chunk {lined[0] + 1}, a reading "
             "that continues -- kept with the session's memory, nothing said; at the last chunk its production "
             "is handed once by its print call, before the choice that chunk asks, and nothing stays kept")
    else:
        failures.append(f"  ✗ the kept line               n={len(chunks)} lined={lined} kept={kept} "
                        f"remembered={remembered} silent={silent} voiced={voiced} "
                        f"facts={[one and one['fact'] for one in readings][-3:]}")
    reader.memory.unlink(missing_ok=True)

    # --- the harness imports nothing of the engine but language ---------------------------------------------
    tree = ast.parse(M.HARNESS.read_text(encoding="utf-8"))
    imported = sorted({node.module.split(".")[0] if isinstance(node, ast.ImportFrom) else alias.name.split(".")[0]
                       for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                       for alias in (node.names if isinstance(node, ast.Import) else [None])})
    text = M.HARNESS.read_text(encoding="utf-8")
    if ("conductor" not in imported and harness.MARK == messages.MARK
            and all(word not in text for word in (".sys", "urllib", "socket", "http", "trace", "persistence"))):
        held("the harness knows nothing more than a model", f"imports {imported}: no conductor; the marks read from "
             "core/model.py; no .sys, no network, no record of the run")
    else:
        failures.append(f"  ✗ imports                    {imported}")
    return 0
