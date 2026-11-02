"""Scenario `model-grammar` -- 6 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
l-adaptateur-model and la-feuille-de-reponse, 2026-10-27/28): the modelled LLM reads a REAL block by its
structure and the engine's constants, and finds every text its CANDIDATE forms in the data -- what the case
compares is read from the engine (a block it rendered, its constants) and from the data, never a sentence
typed here:
- the boot the engine renders in the LLM's mode is read: its key, its INSTRUCTION lines (every keyword
  one of `language.YIELDING`, a `=> words` step among them), its closing and the call under it, where
  the INSTRUCTION lines stand (`instructed`); the foot gives ONE candidate form and its act, no hole
- a block whose closing shows a template: a member under a law of production, the proof asked --
  the line read with its form `proof`, its code and its channel `tool`, the call read as a template
  naming the form, the one candidate V and the act CALL on both channels
- the boot of the principal's mode has no closing and its last segment carries the step: read as T on
  the prompt channel, hand back after the productions; the same text with no INSTRUCTION line reads TWO
  candidates (M, R) whose acts disagree: no act, the note `undecided` -- the text alone cannot say
- the engine's own lines that answer a call are read: every line of `Conductor.HELD_SAID`, the bounce
  (`pp._HELD_BOUNCE`), `principal-advances`, the refusals that stop the conduction, a gesture, any
  other refusal -- each to its row of ANSWERS and its act; a line the data never saw is a `hole`
- no reading of READINGS is a hole: for every reading, a text of its traits leads `foot` to exactly its
  forms, and the harness chooses no form among several (no site picks a first row)
- the module imports nothing of the engine but `language`, reads its two marks from the module that
  prints them, and names no record of the run
"""
from __future__ import annotations

import ast

from conductor import Conductor, persistence
from conductor.core import language
from tests.harness import support

M = support(__file__, "model")
STOPPING = ("repair-exhausted", "exec-refused", "artifact-stale")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    harness = M.harness_module()
    semantics = harness.semantics
    console = M.loaded(M.SOURCE / "engine" / "pp.py", "pp_console")

    # --- the boot of the LLM's mode, read ---------------------------------------------------------------
    env = bench.env("grammar-llm")
    boot = env.cli("-new", "hello").stdout
    key = persistence.run_id_of(persistence.slots(env.made)[0]) if persistence.slots(env.made) else ""
    read = harness.grammar(boot)
    forms, act, note = harness.foot(read, "tool") if read else ((), "", "")
    if (read and read["key"] == key and read["instructions"]
            and all(one["keyword"] in language.YIELDING for one in read["instructions"])
            and any(one["channel"] == language.WORDS for one in read["instructions"])
            and read["closing"] in (language.CONTINUE, language.AWAIT) and read["call"]
            and read["instructed"] in ("last", "earlier", "none")
            and len(forms) == 1 and forms[0] in ("T", "M") and act and not note):
        held("the boot is read by its structure", f"run {key}: {len(read['instructions'])} instruction line(s), "
             f"closing {read['closing']} over a {read['call']} call, instructed {read['instructed']} -> form "
             f"{forms[0]}, act {act}")
    else:
        failures.append(f"  ✗ boot read                  {read and {k: v for k, v in read.items() if k not in ('template', 'served')}} "
                        f"forms={forms} act={act} note={note}")

    # --- a template under the closing: the proof asked ---------------------------------------------------
    lawful = bench.env("grammar-law")
    lawful.write_member(front="constraints.production: |\n  L1  the answer lands\n")
    proving = harness.grammar(lawful.cli("-new", "hello").stdout)
    for _ in range(4):                                  # the free steps pass by the bare call; the turn ends on its proof
        if proving is None or proving["call"] == "template":
            break
        proving = harness.grammar(lawful.cli(proving["key"]).stdout)
    proof = next((one for one in (proving or {}).get("instructions", []) if one["form"] == "proof"), None)
    on_tool = harness.foot(proving, "tool") if proving else ((), "", "")
    on_prompt = harness.foot(proving, "prompt") if proving else ((), "", "")
    if (proof and proof["codes"] == ["L1"] and proof["channel"] == language.TOOL
            and proving["closing"] == language.CONTINUE and proving["call"] == "template"
            and harness.PLACEHOLDER.search("\n".join(proving["template"])).group(1) == "proof"
            and on_tool[:2] == (("V",), "CALL") and on_prompt[:2] == (("V",), "CALL")):
        held("a template names the form due", "INFER proof [L1] => tool read; the call under CONTINUE a template "
             "naming `proof`; V and CALL on both channels")
    else:
        failures.append(f"  ✗ template                   {proof} {proving and proving['closing']} "
                        f"{proving and proving['call']} {on_tool} {on_prompt}")

    # --- the boot of the principal's mode: no closing ----------------------------------------------------
    marked = bench.env("grammar-principal")
    served = M.cli(marked.engine, "-new", "hello", cwd=marked.root, env={"PP_CONDUCTED_BY_PRINCIPAL": "true"}).stdout
    pending = harness.grammar(served)
    at_prompt = harness.foot(pending, "prompt") if pending else ((), "", "")
    bare_text = harness.grammar("\n".join(line for line in served.splitlines()
                                          if not harness.INSTRUCTION.match(line))) if pending else None
    unstepped = harness.foot(bare_text, "prompt") if bare_text else ((), "", "")
    if (pending and pending["instructions"] and pending["closing"] == "" and pending["call"] == ""
            and pending["instructed"] == "last" and at_prompt == (("T",), "SAY_HAND_BACK", "")
            and bare_text is not None and bare_text["instructed"] == "none"
            and unstepped == (("M",), "SAY_HAND_BACK", "")):
        held("the principal's boot hands back, the same text unstepped is the root's end", "no closing, the step in "
             "the last segment: T on the prompt channel, the productions said then the turn handed back; the "
             f"INSTRUCTION lines taken out: {unstepped[0]} alone -- a prompt text with no closing and no step is "
             "the end of a passage, a chunk closing on MORE (batch la-main-et-les-clotures, 2026-10-28)")
    else:
        failures.append(f"  ✗ principal boot             {pending and pending['closing']!r} {at_prompt} {unstepped}")

    # --- the answers to a call -------------------------------------------------------------------------
    seen = {}
    for act_name, line in Conductor.HELD_SAID.items():
        seen[act_name] = harness.answered(f"pp: {line}")
    bounce = harness.answered(console._HELD_BOUNCE)
    advances = harness.answered(f"pp: REFUSED — principal-advances — {console._ALREADY}\n  nothing played.")
    stopping = {code: harness.answered(f"pp: REFUSED — {code} — the detail") for code in STOPPING}
    other = harness.answered("pp: REFUSED — run-unknown — the detail")
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

    # --- no reading is a hole, and no form is chosen among several ---------------------------------------
    holes = []
    for row in semantics.READINGS:
        traits = {name: ("" if row[name] == semantics.ANY else row[name]) for name in semantics.TRAITS}
        if row["instructed"] == semantics.ANY:
            traits["instructed"] = "none"
        reading = {"closing": traits["closing"], "call": traits["call"], "fact": traits["fact"],
                   "instructed": traits["instructed"], "instructions": []}
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

    # --- the harness imports nothing of the engine but language ---------------------------------------------
    tree = ast.parse(M.HARNESS.read_text(encoding="utf-8"))
    imported = sorted({node.module.split(".")[0] if isinstance(node, ast.ImportFrom) else alias.name.split(".")[0]
                       for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))
                       for alias in (node.names if isinstance(node, ast.Import) else [None])})
    text = M.HARNESS.read_text(encoding="utf-8")
    if ("conductor" not in imported and harness.MARK == harness.constant(harness.CORE / "model.py", "MARK")
            and all(word not in text for word in (".sys", "urllib", "socket", "http", "trace", "persistence"))):
        held("the harness knows nothing more than a model", f"imports {imported}: no conductor; the marks read from "
             "core/model.py; no .sys, no network, no record of the run")
    else:
        failures.append(f"  ✗ imports                    {imported}")
    return 0
