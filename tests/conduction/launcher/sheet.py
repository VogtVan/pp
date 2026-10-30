"""Scenario `launcher/sheet` -- 6 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
la-feuille-de-reponse and le-masque-et-le-contenu, 2026-10-28): the SHEET OF RESPONSE the campaign writes -- one
line per text pp handed to the agent, the oracle from the trace, the reader from the text alone, the observed
from the flow, a verdict each -- proven under the modelled LLM on a throwaway house:
- (a) `play --provider model --root long-read --root review --root gesture-while-held --root read-lines
  --channel relayed --conduction strict` writes `sheet.json` and `SHEET.md`: one line per text handed (the count of lines of an
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
- (f) the CONTENT and the EXPECTATION: `read-lines` says four `words` at the WORK of `READ_LINES` (the intention
  `read: LINES.txt`), each carrying one line of the file laid in the agent's workspace, the others naming the
  document and the keyword of their step; the manifest's `expect:` is judged per exchange in the sheet
  (`expect`, `expect_missed`: the `words` of the whole exchange, the boot's and the turn's included): the
  four roots hold theirs; a witness set whose root expects `words: 9` is counted missed
"""
from __future__ import annotations

import json

from tests.harness import support

C = support(__file__, "conduction")
VERDICTS = ("vert", "rouge-conduction", "rouge-agent", "trou")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, coverage, folder, house = C.played(bench, "--root", "long-read", "--root", "review",
                                             "--root", "gesture-while-held", "--root", "read-lines",
                                             "--channel", C.RELAYED, "--conduction", C.STRICT)
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
              for name in ("long-read-relayed-strict", "review-relayed-strict", "gesture-while-held-relayed-strict",
                           "read-lines-relayed-strict")}
    long_read = by_exchange.get("long-read-relayed-strict", [])
    chunk = [one for one in long_read if one["channel"] == "prompt" and one["oracle"]
             and one["oracle"]["form"] == "R"]
    review = by_exchange.get("review-relayed-strict", [])
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
    gesture = by_exchange.get("gesture-while-held-relayed-strict", [])
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
    run = json.loads((folder / "review-relayed-strict" / "run.json").read_text(encoding="utf-8")) \
        if (folder / "review-relayed-strict" / "run.json").is_file() else {}
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
    bare = C.launcher("sheet", "--out", str(folder.parent))
    if (missing.returncode == 2 and "campaign-missing" in missing.stderr
            and unknown.returncode == 2 and "run-unknown" in unknown.stderr
            and bare.returncode == 2 and "date-missing" in bare.stderr):
        held("(e) the refusals", "no campaign at the date: campaign-missing; a run the house never opened: run-unknown; "
             "no date and no run: date-missing -- exit 2, nothing written")
    else:
        failures.append(f"  ✗ (e) the refusals            {missing.returncode} {missing.stderr[-80:]!r} "
                        f"{unknown.returncode} {unknown.stderr[-80:]!r} {bare.returncode}")

    # --- (f) the content and the expectation ------------------------------------------------------------------------
    file_lines = (C.SET / "LINES.txt").read_text(encoding="utf-8").splitlines()
    read_lines = by_exchange.get("read-lines-relayed-strict", [])
    work = [one for one in read_lines if any(two.startswith("WORK") for two in one["reader"].get("instructions", []))]
    carrying = [said for said in work[0]["observed"]["said"] if any(line in said for line in file_lines)] if work else []
    carried = len(carrying) == len(file_lines) and all(line in said for line, said in zip(file_lines, carrying))
    cited = [one for one in review if one["observed"]["said"]
             and all("REVIEW" in said or "TURN" in said or "CAPABILITIES" in said for said in one["observed"]["said"])]
    expectations = sheet.get("expect") or []
    held_words = [one for one in expectations if one["exchange"] == "read-lines-relayed-strict" and one["key"] == "words"]
    witness = C.witness_set(bench, expect={"words": 9})
    missed, _cov, wrong, _h = C.played(bench, "--set", str(witness), "--channel", C.RELAYED, "--conduction", C.STRICT)
    wrong_sheet = C.sheet_of(wrong)
    if (work and carried and cited and held_words and held_words[0]["seen"] >= len(file_lines)
            and held_words[0]["held"] is True
            and sheet.get("expect_missed") == 0 and expectations
            and missed.returncode == 0 and wrong_sheet.get("expect_missed") == 2
            and all(one["held"] is False and one["expected"] == 9 for one in wrong_sheet.get("expect", [])
                    if one["key"] == "words")):
        held("(f) the content and the expectation", f"read-lines: {len(file_lines)} words at the WORK, each carrying its "
             f"line; review's words cite their document; {len(expectations)} expectation(s) judged, 0 missed; the "
             f"witness set expecting 9 words: {wrong_sheet['expect_missed']} exchange(s) missed")
    else:
        failures.append(f"  ✗ (f) the content             work={len(work)} carried={carried} cited={len(cited)} "
                        f"words={held_words} missed={sheet.get('expect_missed')} witness={missed.returncode} "
                        f"{wrong_sheet.get('expect_missed')} {wrong_sheet.get('expect')} {missed.stderr[-200:]!r}")
    return 0
