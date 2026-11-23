"""Scenario `launcher/sheet` -- 10 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
la-feuille-de-reponse and le-masque-et-le-contenu, 2026-10-28): the SHEET OF RESPONSE the campaign writes -- one
line per text pp handed to the agent, the oracle from the trace, the reader from the text alone, the observed
from the flow, a verdict each -- proven under the modelled LLM on a throwaway house:
- (a) `play --provider model --root long-read --root review --root gesture-while-held --root read-lines`
  writes `sheet.json` and `SHEET.md`: one line per text handed (the count of lines of an
  exchange equals its `conduction` events plus the `tool-result` events that carry a text of pp); `long-read`
  has no red line: the chunk at the prompt closes on `MORE` and reads R alone, as the oracle says (the batch
  la-main-et-les-clotures, 2026-10-28); `review` has no red line
- (b) `gesture-while-held`: the script called while an output waited (`-s pp-cyclewit next`) PLAYS -- its line
  reads the gesture's own answer, `vert`; the lines of the door and of the words are `vert`
- (c) `sheet <date>` replayed on the same artifacts renders `sheet.json` byte for byte
- (d) `sheet --house <ws> --agent agents/pat --run <key>` on the run of `review` renders the same lines as the
  campaign's for that exchange (the fields compared, the exchange's name apart)
- (e) a date no campaign wrote refuses `campaign-missing`; a run the house never opened refuses `run-unknown`;
  `sheet` without a date or a run refuses `date-missing`
- (f) the CONTENT and the EXPECTATION: `read-lines` PRINTS the production of the WORK of `READ_LINES` (the
  intention `read: LINES.txt`): the trace keeps it as an `answer` of channel `terminal` naming its document,
  carrying the four lines of the file laid in the agent's workspace, in order; `review`'s prints name their
  document; the manifest's `expect:` is judged per exchange in the sheet (`expect`, `expect_missed`: the
  `words` of the whole exchange, every production printed -- a launch's last message is none): the four roots
  hold theirs; a witness set
  whose root expects `words: 9` is counted missed
- (g) the JUDGE reads the capture: every print call of an exchange's flow has its `answer` of channel
  `terminal` at the trace; a block whose `=> terminal` line asks a print conforms to a print call
  (`conforming`), never to the production said as words beside a value
- (h) the prints DUE against the prints taken (`prints_missed`, `prints_owed`): a trace of two steps said on
  `terminal` and one capture names the document left; with its two captures, or with a debt a door lifted, it
  names none; a debt the bound lifted is a production never taken; the prints of an output no launch carried
  (the launcher's bound) and those a renewal of the run dropped are no miss of the agent; the exchange's last
  line, green, goes `rouge-agent` and carries the documents left
- (i) the house's ADVANCE caught while a print is due (a run its principal conducts): the oracle reads the block
  that stands, served again, as an OUTPUT of the channel `prompt`, of the form of the output before it, in the
  zone `soft-catch` -- no view of the channel `tool`
- (j) the VIEW of a block that asks a value, in a run its principal conducts: a value handed while a print is
  due brings back the block with its lines -- the oracle's view carries the form V, as the output before it; a
  view behind an output that asks no value carries D
"""
from __future__ import annotations

import json

from tests.harness import support

C = support(__file__, "conduction")
VERDICTS = ("vert", "rouge-conduction", "rouge-agent", "trou")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, coverage, folder, house = C.played(bench, "--root", "long-read", "--root", "review",
                                             "--root", "gesture-while-held", "--root", "read-lines")
    sheet = C.sheet_of(folder)
    lines = sheet.get("lines", [])
    by_exchange: dict[str, list[dict]] = {}
    for one in lines:
        by_exchange.setdefault(one["exchange"], []).append(one)

    # --- (a) one line per text handed, long-read red at the prompt, review green ---------------------------
    def handed(name: str) -> int:
        """-> the texts the flow says handed: the prompts of the launches and the results of the console's calls."""
        path = folder / name / "flow.jsonl"
        if not path.is_file():
            return -1
        events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip().startswith("{")]
        pp_calls = {str(one.get("id")) for one in events if one.get("kind") == "tool" and one.get("pp")}
        return (sum(1 for one in events if one.get("kind") == "conduction")
                + sum(1 for one in events if one.get("kind") == "tool-result" and str(one.get("id")) in pp_calls))

    counts = {name: (len(by_exchange.get(name, [])), handed(name))
              for name in ("long-read-relayed", "review-relayed", "gesture-while-held-relayed",
                           "read-lines-relayed")}
    long_read = by_exchange.get("long-read-relayed", [])
    chunk = [one for one in long_read if one["channel"] == "prompt" and one["oracle"]
             and one["oracle"]["form"] == "R"]
    review = by_exchange.get("review-relayed", [])
    if (done.returncode == 0 and (folder / "SHEET.md").is_file() and lines
            and all(found == owed and owed > 0 for found, owed in counts.values())
            and chunk and all(one["reader"]["forms"] == ["R"] and one["verdict"] == "vert"
                              and one["reader"]["traits"]["closing"] == "MORE" for one in chunk)
            and all(one["verdict"] == "vert" for one in long_read)
            and review and all(one["verdict"] == "vert" for one in review)
            and all(one["verdict"] in VERDICTS for one in lines)):
        held("(a) one line per text, the chunk at the prompt read R", f"{len(lines)} lines for {counts}; long-read: "
             f"{len(chunk)} chunk(s) at the prompt close on MORE and read R alone, {len(long_read)} lines vert; "
             f"review: {len(review)} vert")
    else:
        failures.append(f"  ✗ (a) the sheet               rc={done.returncode} counts={counts} chunk={[(one['reader']['forms'], one['verdict']) for one in chunk]} "
                        f"long={[one['verdict'] for one in long_read]} review={[one['verdict'] for one in review]} {done.stderr[-200:]!r}")

    # --- (b) the gesture bounced while an output waited ---------------------------------------------------------
    gesture = by_exchange.get("gesture-while-held-relayed", [])
    played = [one for one in gesture if one["channel"] == "tool" and " -s pp-" in str(one.get("shell", ""))]
    others = [one for one in gesture if one not in played]
    if (played and all(one["verdict"] == "vert" and one["oracle"] and one["oracle"].get("answer") == "gesture"
                       and one["reader"].get("answer") == "gesture" for one in played)
            and others and all(one["verdict"] == "vert" for one in others)):
        held("(b) a gesture plays while an output waits", f"{len(played)} line(s) vert on "
             f"`{played[0]['shell']}` answered by the gesture's own output; the {len(others)} other lines vert")
    else:
        failures.append(f"  ✗ (b) the gesture             played={[(one['verdict'], one.get('shell'), (one['oracle'] or {}).get('answer')) for one in played]} "
                        f"others={[one['verdict'] for one in others]}")

    # --- (c) the sheet replayed, byte for byte --------------------------------------------------------------------
    before = (folder / "sheet.json").read_bytes() if (folder / "sheet.json").is_file() else b""
    again = C.launcher("sheet", folder.name, "--out", str(folder.parent))
    after = (folder / "sheet.json").read_bytes() if (folder / "sheet.json").is_file() else b""
    if again.returncode == 0 and before and before == after:
        held("(c) the sheet replayed byte for byte", f"`sheet {folder.name}`: {len(after)} bytes, the same")
    else:
        failures.append(f"  ✗ (c) the replay              rc={again.returncode} same={before == after} {again.stderr[-200:]!r}")

    # --- (d) the sheet of one run of the house ------------------------------------------------------------------
    run = json.loads((folder / "review-relayed" / "run.json").read_text(encoding="utf-8")) \
        if (folder / "review-relayed" / "run.json").is_file() else {}
    key = str(run.get("run") or "")
    out = bench.temp() / "runsheet"
    one_run = C.launcher("sheet", "--house", str(house), "--agent", "agents/pat", "--run", key, "--out", str(out))
    captured = C.sheet_of(out / key).get("lines", [])

    def stripped(line: dict) -> dict:
        return {name: value for name, value in line.items() if name not in ("n", "exchange", "root")}

    if (key and one_run.returncode == 0 and captured and [stripped(one) for one in captured] == [stripped(one) for one in review]):
        held("(d) a captured run reads the same", f"run {key}: {len(captured)} lines, the campaign's for review "
             "field for field")
    else:
        failures.append(f"  ✗ (d) the run                 key={key!r} rc={one_run.returncode} n={len(captured)}/{len(review)} "
                        f"{one_run.stderr[-200:]!r}")

    # --- (e) the refusals -------------------------------------------------------------------------------------------
    missing = C.launcher("sheet", "1999-01-01T0000", "--out", str(folder.parent))
    unknown = C.launcher("sheet", "--house", str(house), "--agent", "agents/pat", "--run", "abcdef", "--out", str(out))
    undated = C.launcher("sheet", "--out", str(folder.parent))
    if (missing.returncode == 2 and "campaign-missing" in missing.stderr
            and unknown.returncode == 2 and "run-unknown" in unknown.stderr
            and undated.returncode == 2 and "date-missing" in undated.stderr):
        held("(e) the refusals", "no campaign at the date: campaign-missing; a run the house never opened: run-unknown; "
             "no date and no run: date-missing -- exit 2, nothing written")
    else:
        failures.append(f"  ✗ (e) the refusals            {missing.returncode} {missing.stderr[-80:]!r} "
                        f"{unknown.returncode} {unknown.stderr[-80:]!r} {undated.returncode}")

    # --- (f) the content and the expectation ------------------------------------------------------------------------
    file_lines = (C.SET / "LINES.txt").read_text(encoding="utf-8").splitlines()

    def prints_of(exchange: str) -> list[dict]:
        """-> the prints the trace of an exchange keeps: its `answer` events of channel `terminal` naming a document."""
        path = folder / exchange / "trace.jsonl"
        events = [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()] \
            if path.is_file() else []
        return [one for one in events if one.get("kind") == "answer" and one.get("channel") == "terminal"
                and one.get("document")]

    work = [one for one in prints_of("read-lines-relayed") if one["document"] == "READ_LINES"]
    given = str(work[0].get("given", "")) if work else ""
    at = [given.find(line) for line in file_lines]
    carried = bool(work) and all(one >= 0 for one in at) and at == sorted(at)
    cited = [one for one in prints_of("review-relayed") if one["document"] in str(one.get("given", ""))]
    expectations = sheet.get("expect") or []
    held_words = [one for one in expectations if one["exchange"] == "read-lines-relayed" and one["key"] == "words"]
    witness = C.witness_set(bench, expect={"words": 9})
    missed, _cov, wrong, _h = C.played(bench, "--set", str(witness))
    wrong_sheet = C.sheet_of(wrong)
    if (work and carried and cited and held_words and held_words[0]["held"] is True
            and sheet.get("expect_missed") == 0 and expectations
            and missed.returncode == 0 and wrong_sheet.get("expect_missed") == 2
            and all(one["held"] is False and one["expected"] == 9 for one in wrong_sheet.get("expect", [])
                    if one["key"] == "words")):
        held("(f) the content and the expectation", f"read-lines: the WORK printed, its answer at the trace carrying "
             f"the {len(file_lines)} lines in order; review's {len(cited)} print(s) cite their document; {len(expectations)} expectation(s) judged, 0 missed; the "
             f"witness set expecting 9 words: {wrong_sheet['expect_missed']} exchange(s) missed")
    else:
        failures.append(f"  ✗ (f) the content             work={len(work)} carried={carried} cited={len(cited)} "
                        f"words={held_words} missed={sheet.get('expect_missed')} witness={missed.returncode} "
                        f"{wrong_sheet.get('expect_missed')} {wrong_sheet.get('expect')} {missed.stderr[-200:]!r}")

    # --- (g) the judge reads the capture ------------------------------------------------------------------------------
    campaign = C.module()
    flow_path = folder / "read-lines-relayed" / "flow.jsonl"
    flow = [json.loads(one) for one in flow_path.read_text(encoding="utf-8").splitlines() if one.strip()] \
        if flow_path.is_file() else []
    print_calls = [one for one in flow if one.get("kind") == "tool"
                   and campaign.call_kind(str(one.get("shell") or "")) == "print"]
    printed = campaign.conforming("SAY_CALL", {"calls": ["print"], "words": 0, "prints": 1}, True)
    worded = campaign.conforming("SAY_CALL", {"calls": ["value"], "words": 1, "prints": 0}, True)
    if print_calls and len(print_calls) == len(prints_of("read-lines-relayed")) and printed and not worded:
        held("(g) the judge reads the capture", f"read-lines: {len(print_calls)} print call(s) in the flow, as many "
             "answers of channel terminal at the trace; a print conforms where a `=> terminal` line asks, a "
             "production said as words beside a value does not")
    else:
        failures.append(f"  ✗ (g) the judge               calls={len(print_calls)} prints={len(prints_of('read-lines-relayed'))} "
                        f"printed={printed} worded={worded}")

    # --- (h) the prints due against the prints taken --------------------------------------------------------------------
    def due(document: str) -> dict:
        return {"kind": "print-due", "instruction": "INFER ", "document": document}

    def taken(document: str) -> dict:
        return {"kind": "answer", "instruction": "INFER ", "document": document, "given": "x", "channel": "terminal"}

    missed_of = getattr(campaign, "prints_missed", lambda trace: None)
    owed = getattr(campaign, "prints_owed", lambda lines, trace: None)
    one_left = missed_of([due("ALPHA"), due("BETA"), taken("ALPHA")])
    none_left = missed_of([due("ALPHA"), due("BETA"), taken("BETA"), taken("ALPHA")])
    by_door = missed_of([due("ALPHA"), due("BETA"), taken("ALPHA"),
                         {"kind": "print-by-door", "instruction": "INFER ", "document": "BETA", "door": "GAMMA"}])
    at_bound = missed_of([due("ALPHA"), {"kind": "print-waived", "instruction": "INFER ", "document": "ALPHA",
                                         "refused": 2}])
    try:
        never_handed = missed_of([due("ALPHA"), due("BETA"), taken("ALPHA")], ["BETA"])
    except TypeError:
        never_handed = None
    renewed = missed_of([due("ALPHA"), due("BETA"), {"kind": "reopened"}, due("BETA"), taken("BETA")])
    green = [{"exchange": "x", "launch": 1, "verdict": "vert", "why": ""}]
    owed(green, [due("ALPHA"), due("BETA"), taken("ALPHA")])
    kept = [{"exchange": "x", "launch": 1, "verdict": "vert", "why": ""}]
    owed(kept, [due("ALPHA"), taken("ALPHA")])
    if (one_left == ["BETA"] and none_left == [] and by_door == [] and at_bound == ["ALPHA"]
            and never_handed == [] and renewed == []
            and green[0]["verdict"] == "rouge-agent" and green[0].get("prints_missed") == ["BETA"]
            and kept[0]["verdict"] == "vert" and not kept[0].get("prints_missed")):
        held("(h) the prints due against the prints taken", "two steps due and one capture: the document left is "
             "named and the last line goes rouge-agent; both captured, or one lifted by a door: none left; a debt "
             "the bound lifted is left")
    else:
        failures.append(f"  ✗ (h) the prints due          one={one_left} none={none_left} door={by_door} bound={at_bound} "
                        f"never={never_handed} renewed={renewed} "
                        f"green={green[0]['verdict']} {green[0].get('prints_missed')} kept={kept[0]['verdict']}")

    # --- (i) the house's advance caught while a print is due ---------------------------------------------------------
    def said(*behind: dict) -> list[dict]:
        """-> the trace of an output that says one step on `terminal` and closes on it, then `behind`."""
        return [{"kind": "new"},
                {"kind": "block", "stack": "ROOT ▸ SAID{1/1}", "command": "INFER", "wait": False},
                {"kind": "block", "stack": "ROOT{2/3}", "command": "WORK", "wait": False},
                {"kind": "pending", "instruction": "WORK "}, due("SAID"),
                {"kind": "block", "stack": "ROOT{2/3}", "command": "", "wait": False}, *behind]

    caught = {"kind": "stray", "instruction": "INFER ", "due": ["SAID"], "handed": False}
    relayed = campaign.outputs_of(said(caught, {"kind": "advance"}, taken("SAID")))
    outputs = [one for one in relayed if one["kind"] == "output"]
    if (len(outputs) == 2 and all(one["channel"] == "prompt" for one in outputs)
            and outputs[1]["form"] == outputs[0]["form"] and campaign.zone_of(outputs[1]) == "soft-catch"
            and not [one for one in relayed if one["kind"] == "view"]):
        held("(i) the house's advance caught", f"{len(outputs)} outputs at the prompt, the second of the form "
             f"{outputs[1]['form']} in the zone soft-catch, no view")
    else:
        failures.append(f"  ✗ (i) the advance caught      relayed={[(one['kind'], one.get('channel'), one.get('form')) for one in relayed]}")

    # --- (j) the view of a block that asks a value ---------------------------------------------------------------------
    handed = {"kind": "stray", "instruction": "INFER ", "due": ["SAID"], "handed": True}
    valued = [{"kind": "new"},
              {"kind": "block", "stack": "ROOT ▸ SAID{1/2}", "command": "INFER", "wait": False},
              {"kind": "block", "stack": "ROOT ▸ SAID{2/2}", "command": "PICK", "wait": False},
              due("SAID"), handed, taken("SAID")]
    views_v = [one for one in campaign.outputs_of(valued) if one["kind"] == "view"]
    views_d = [one for one in campaign.outputs_of(said(handed, taken("SAID"))) if one["kind"] == "view"]
    if ([one.get("form") for one in views_v] == ["V"] and [one.get("form") for one in views_d] == ["D"]
            and all(one["channel"] == "tool" for one in views_v + views_d)):
        held("(j) the view of a block that asks a value", "a value handed while a print is due: the view carries V "
             "behind an output that asks a value, D behind one that asks none")
    else:
        failures.append(f"  ✗ (j) the view of a value     V={[one.get('form') for one in views_v]} "
                        f"D={[one.get('form') for one in views_d]}")
    return 0
