"""Scenario `launcher/turn` -- 20 case(s) (plan moteur-0.3.0-mesure, phase la-mesure-d-abord, batch
le-joueur-d-un-tour, 2026-11-14): the verb `turn` of the campaign's launcher -- ONE turn of a prompt played
on a harness, without pp nor house -- proven under the modelled LLM on a throwaway set (`turn.yaml`: an
accessory, a variant of one prompt with its fixed part, a variant of two prompts), never on a real provider:
- (a) `turn --provider model --repeat 2 --jobs 2` plays every variant twice and renders 0; every repetition
  keeps its pieces under `<out>/<date>/<variant>/<k>/` -- `launch.json`, `stdout.txt`, `stderr.txt`,
  `events.jsonl`, `received.jsonl`, the prompt as it left --, and its throwaway directory is gone
- (b) the fake `./pp` receives the print and the proof: one line of `received.jsonl` per call the model typed --
  the production of the `=> terminal` line by its print call (`-print WITNESS -`), then the proof, its input a JSON
  value --, and what the fake answered is what the model reads: the line of a print taken (the engine's
  `messages.PRINTED`), then a value judged (the data's own line)
- (c) the accessory stands in the throwaway directory (the model prints its lines) and the fixed part of a
  variant leads the first prompt where the adapter gives no system prompt at the call: `launch.json` says
  where it went
- (d) a variant of two prompts plays two launches of ONE session, the second resumed, the fixed part not
  said again
- (e) the table counts: `turn.json` carries one row per repetition and the foot of the variant, its counts
  equal to what the kept pieces say; the one-prompt variant ends on `...` (its production is printed, no
  line asks a last message): `dots`; the last message of the two-prompt variant is a JSON value alone;
  `TURN.md` stands beside it
- (f) nothing plays on a call the verb does not know: `--help`, an unknown flag, a variant the set lacks, a
  manifest badly written, a set without its manifest and a policy the adapter cannot spell each render a
  refusal code and write no folder of a launch
- (g) nothing of a provider lives in the player: its code names no host of `adapters/`; where the fixed part
  goes comes from the adapter's own declaration (`SYSTEM_PROMPT`) -- composed in-process, nothing launched:
  the marble of the call where the adapter gives one, the head of the first prompt otherwise and under
  `place: head`, never the head of a resumed launch; the nature of a message is read by its form alone
- (h) the phase of a message comes from the adapter's transcript: on a witness face written at run time
  (`transcript(session)`), the transcript is copied beside the pieces and the row gives each message its
  phase, the foot the phase of the last one; an adapter without the face gives none
- (i) the fixed part of a variant may live OUTSIDE the set: a path relative to the set's directory, `..`
  allowed, or an absolute one -- both variants play and their first prompt opens on that text; a `fixed:`
  that names no file refuses `manifest-invalid`, and so do a prompt or an accessory outside the set
- (j) the throwaway directory is a git repository, whatever the provider: the model reads `.git/HEAD` there
  and prints the branch it names; the pieces kept carry nothing of the repository
- (k) a repetition that raises does not lose the campaign: its row carries its error and its cause, the others
  play, the table is written -- rewritten at every repetition that ends -- and the verb renders 1
- (l) a launch is bounded by `--timeout`: past it the process is killed and the launch ends on the error
  `timeout`; a stream that is no UTF-8 is read all the same; a face of the adapter that raises ends the
  repetition on its error, the campaign goes on -- three witness adapters written at run time, never a real one
- (m) the last message is the one of the LAST launch: a variant of two prompts whose first launch says its
  JSON message and whose second ends on `...` renders `dots`, at the row and at the foot
- (n) a call of the console is read at what the fake answered, never at the shape of the shell line: the
  sequence marks `pp` as many times as the fake answered in the call's result, and equals `received`
- (o) a manifest badly written refuses `manifest-invalid` before any launch: a variant named as a piece of the
  table or without a name, an accessory without a name or named as a directory, a `files:` of another type
- (p) the row of a repetition in error keeps, with its code, the cause the harness said
- (q) the fixed part is cited by its fingerprint: its sha256 and its size in characters, in `launch.json`
  and in the table; none where the variant plays no fixed part
- (r) two plays of the same second under one `--out` never write the same folder
- (s) a play interrupted stops its queue, on SIGINT as on SIGTERM: no new repetition starts, the launches in
  flight are killed, the table of what played is written and says the interruption, the verb renders a code
  of its own -- neither 0, nor 1, nor a refusal's -- and gives the signals back to whoever held them
- (t) the cause of an error says what the harness said, or nothing: an adapter that names an error and
  answers a session, its stderr empty, leaves the cause empty
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import signal
import threading
import time
import types
from pathlib import Path

from conductor.core import messages
from conductor import Conductor
from tests.harness import SOURCE, support

C = support(__file__, "conduction")
PLAYER = SOURCE / "tools" / "campaign" / "turn.py"
MANIFEST = "turn.yaml"
KEY = "abc123"
NOTES = ("alpha-note", "beta-note")
FIXED = "the standing text of the witness\n"
PIECES = ("launch.json", "stdout.txt", "stderr.txt", "events.jsonl", "received.jsonl", "prompt.txt")
BLOCK_ONE = f"""▌ pp · run {KEY} · 00:00:00 · +0:00:00

▌ WITNESS{{1/2}}

▌ INSTRUCTION
WORK line => terminal  (WITNESS)
INFER proof [W1] => tool_heredoc  (WITNESS)
"""
BLOCK_PROOF = f"""▌ pp · run {KEY} · 00:00:01 · +0:00:01

▌ WITNESS{{2/2}}

▌ INSTRUCTION
INFER proof [W2] => tool_heredoc  (WITNESS)
"""
WITNESS_ADAPTER = """import sys

BINARY, SPELLS, COST = None, (), None
SCRIPT = {script!r}


def wire(workspace, meta):
    return []


def launch(workspace, meta, marble, prompt, wiring=None, policy=None, session=None, workdir=None):
    return [sys.executable, "-c", SCRIPT], {{}}, prompt


def answer(stdout, stderr):
    return {{"cost_usd": None, "denials": [], "error": {error!r}, "session": "s-witness"}}


def events(line):
    {events}
"""
WITNESS_ADAPTERS = {       # name -> (what its launch runs, what its `events` face does, the error its `answer` names)
    "slow": ("import time; time.sleep(60)", "return []", None),
    "garbled": ("import sys; sys.stdout.buffer.write(b'\\xff\\xfe no utf-8\\n')", "return []", None),
    "raising": ("print('a line')", "raise ValueError('no reading')", None),
    "spent": ("pass", "return []", "budget spent"),
}
BLOCK_TWO = f"""▌ pp · run {KEY} · 00:00:01 · +0:00:01

▌ WITNESS{{2/2}}

▌ INSTRUCTION
INFER json => response  (WITNESS)
"""


def witness(bench, manifest: str | None = None) -> Path:
    """-> a throwaway set of the player: an accessory, a fixed part, two prompts and the manifest -- the
    one given when a case tries a manifest of its own, None for none at all."""
    made = bench.temp() / "set"
    made.mkdir(parents=True)
    (made / "NOTES.txt").write_text("\n".join(NOTES) + "\n", encoding="utf-8")
    (made / "fixed.md").write_text(FIXED, encoding="utf-8")
    (made / "one.md").write_text(BLOCK_ONE, encoding="utf-8")
    (made / "two.md").write_text(BLOCK_TWO, encoding="utf-8")
    (made / "proof.md").write_text(BLOCK_PROOF, encoding="utf-8")
    if manifest is None:
        return made
    (made / MANIFEST).write_text(manifest, encoding="utf-8")
    return made


WHOLE = """files:
  NOTES.txt: NOTES.txt
variants:
  single:
    fixed: fixed.md
    prompts: [one.md]
    model: [{read: NOTES.txt}]
  double:
    fixed: fixed.md
    place: head
    prompts: [one.md, two.md]
"""


def lines_of(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def is_json(text: str) -> bool:
    try:
        return isinstance(json.loads(text), (dict, list))
    except ValueError:
        return False


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = witness(bench, WHOLE)
    out = bench.temp() / "out"

    # --- (a) every variant played twice under the model, the pieces kept -----------------------------------
    done = C.launcher("turn", "--set", str(made), "--provider", C.PROVIDER, "--repeat", "2", "--jobs", "2",
                      "--out", str(out))
    dated = sorted(one for one in out.iterdir() if one.is_dir()) if out.is_dir() else []
    folder = dated[-1] if dated else out
    kept = {(name, k): folder / name / str(k) for name in ("single", "double") for k in (1, 2)}
    missing = [f"{name}/{k}/{piece}" for (name, k), where in kept.items() for piece in PIECES
               if not (where / piece).is_file()]
    launches = {one: read(where / "launch.json") for one, where in kept.items()}
    standing = [one.get("workdir") for one in launches.values() if one.get("workdir") and Path(one["workdir"]).exists()]
    if (done.returncode == 0 and len(dated) == 1 and not missing and not standing
            and all(one.get("provider") == C.PROVIDER and one.get("error") is None and "harness" in one
                    and one.get("workdir") for one in launches.values())):
        held("(a) the verb plays a turn under the model", f"rc 0, {len(kept)} repetitions of 2 variants, "
             f"{len(PIECES)} pieces each under {folder.name}/<variant>/<k>/, every throwaway directory gone")
    else:
        failures.append(f"  ✗ (a) the play                rc={done.returncode} dated={len(dated)} missing={missing[:4]} "
                        f"standing={standing[:2]} {done.stderr[-300:]!r}")

    # --- (b) the fake console receives the proof ------------------------------------------------------------
    judged = "pp: " + C.semantics().ANSWERS["value-judged"]["said"]
    printed = messages.printed("more", messages.next_print("<DOCUMENT>"))   # the fake console's line of a print
    received = {one: lines_of(where / "received.jsonl") for one, where in kept.items()}
    events = {one: lines_of(where / "events.jsonl") for one, where in kept.items()}
    answers = {one: [ev.get("content", "") for ev in found if ev.get("kind") == "tool-result"]
               for one, found in events.items()}
    if (all(len(found) == 2 and all(one.get("argv", [None])[0] == KEY for one in found)
            and found[0].get("argv", [])[1:] == ["-print", "WITNESS", "-"] and is_json(found[1].get("stdin", ""))
            for found in received.values())
            and all([one.strip() for one in found] == [printed, judged] for found in answers.values())):
        held("(b) the fake console receives the print and the proof", "two lines per repetition, the run's key their "
             "first argument: the print of WITNESS, then the proof, its input a JSON value; the answers the line "
             "of a print taken, then the data's line of a value judged, read back by the model")
    else:
        failures.append(f"  ✗ (b) the fake console        received={ {str(k): v for k, v in received.items()} } "
                        f"answers={ {str(k): v for k, v in answers.items()} }")

    # --- (c) the accessory laid, the fixed part at the head of the first prompt ----------------------------
    said = [one.get("stdin", "") for one in received[("single", 1)] if one.get("argv", [])[1:2] == ["-print"]]
    prompts = {one: (where / "prompt.txt").read_text(encoding="utf-8") if (where / "prompt.txt").is_file() else ""
               for one, where in kept.items()}
    if (all(any(note in text for text in said) for note in NOTES)
            and all(text.startswith(FIXED) and text.endswith(BLOCK_ONE) for text in prompts.values())
            and all(one.get("place") == "head" and one.get("fixed") == "fixed.md" for one in launches.values())):
        held("(c) the accessory and the fixed part", "the model prints the lines of the accessory laid in its "
             "directory; the fixed part leads the first prompt, `launch.json` says `head`")
    else:
        failures.append(f"  ✗ (c) accessory, fixed part   said={said} places={[one.get('place') for one in launches.values()]} "
                        f"heads={[text[:40] for text in prompts.values()]}")

    # --- (d) two prompts, two launches of one session --------------------------------------------------------
    double = launches[("double", 1)]
    played = double.get("launches") or []
    second = (kept[("double", 1)] / "prompt.2.txt")
    if (len(played) == 2 and [one.get("resumed") for one in played] == [False, True]
            and played[0].get("session") and played[0].get("session") == played[1].get("session") == double.get("session")
            and len(launches[("single", 1)].get("launches") or []) == 1
            and second.is_file() and second.read_text(encoding="utf-8") == BLOCK_TWO
            and (kept[("double", 1)] / "stdout.2.txt").is_file()):
        held("(d) two prompts, one session", f"two launches, the second resumed on session {double.get('session')}, "
             "its prompt without the fixed part; one launch for the variant of one prompt")
    else:
        failures.append(f"  ✗ (d) two prompts             {played}")

    # --- (e) the table counts what the pieces say -------------------------------------------------------------
    table = read(folder / "turn.json")
    variants = table.get("variants", {})
    wrong = []
    for name in ("single", "double"):
        rows = variants.get(name, {}).get("rows", [])
        foot = variants.get(name, {}).get("foot", {})
        if [row.get("repetition") for row in rows] != [1, 2]:
            wrong.append(f"{name}: rows {[row.get('repetition') for row in rows]}")
            continue
        for row in rows:
            found = events[(name, row["repetition"])]
            words = [ev for ev in found if ev.get("kind") == "words"]
            got = received[(name, row["repetition"])]
            counted = {"messages": len(words), "json_messages": sum(1 for ev in words if is_json(ev["text"])),
                       "received": len(got), "received_json": sum(1 for one in got if is_json(one.get("stdin", ""))),
                       "thinking": sum(1 for ev in found if ev.get("kind") == "thinking"),
                       "launches": len(launches[(name, row["repetition"])].get("launches") or [])}
            moved = {key: (row.get(key), value) for key, value in counted.items() if row.get(key) != value}
            flat = [one for launch in row.get("sequence", []) for one in launch]
            if moved or flat.count("pp") != len(got) or flat.count("words") != len(words) \
                    or [one.get("text") for one in row.get("texts", [])] != [ev["text"] for ev in words]:
                wrong.append(f"{name}#{row['repetition']}: {moved} sequence={row.get('sequence')}")
        for key in ("messages", "json_messages", "received", "received_json", "thinking", "launches"):
            if foot.get(key) != sum(row.get(key, 0) for row in rows):
                wrong.append(f"{name} foot {key}: {foot.get(key)}")
        if foot.get("repetitions") != len(rows) or foot.get("errors") != 0:
            wrong.append(f"{name} foot: {foot}")
    lasts = {name: [row.get("last") for row in variants.get(name, {}).get("rows", [])] for name in ("single", "double")}
    if (not wrong and lasts == {"single": ["dots", "dots"], "double": ["json", "json"]}
            and variants.get("double", {}).get("foot", {}).get("last", {}).get("json") == 2
            and table.get("provider") == C.PROVIDER and (folder / "TURN.md").is_file()):
        held("(e) the table counts", "one row per repetition and the foot of each variant; the messages, the JSON "
             "values, the calls received and the thoughts equal to the kept pieces; the one-prompt variant ends "
             "on `...`, its production printed; the last message of the two-prompt variant a JSON value alone; TURN.md beside turn.json")
    else:
        failures.append(f"  ✗ (e) the table               wrong={wrong[:4]} lasts={lasts} keys={sorted(table)}")

    # --- (f) nothing plays on a call the verb does not know ----------------------------------------------------
    nowhere = bench.temp() / "refused"
    base = ("turn", "--set", str(made), "--provider", C.PROVIDER, "--out", str(nowhere))
    bad = witness(bench, "variants:\n  lone:\n    prompts: [absent.md]\n")
    plain = witness(bench)
    tried = {
        "help": (C.launcher("turn", "--help", "--out", str(nowhere)), ""),
        "flag": (C.launcher(*base, "--nope", "1"), "flag-unknown"),
        "variant": (C.launcher(*base, "--variant", "nobody"), "variant-unknown"),
        "manifest": (C.launcher("turn", "--set", str(bad), "--provider", C.PROVIDER, "--out", str(nowhere)),
                     "manifest-invalid"),
        "no-manifest": (C.launcher("turn", "--set", str(plain), "--provider", C.PROVIDER, "--out", str(nowhere)),
                        "manifest-missing"),
        "policy": (C.launcher(*base, "--effort", "low"), "policy-unsupported"),
        "provider": (C.launcher("turn", "--set", str(made), "--provider", "nobody", "--out", str(nowhere)),
                     "provider-unknown"),
    }
    accepted = {name: (one.returncode, one.stderr[-200:]) for name, (one, code) in tried.items()
                if one.returncode != 2 or code not in one.stderr}
    if not accepted and not nowhere.exists() and "absent.md" in tried["manifest"][0].stderr:
        held("(f) nothing plays on a call the verb does not know", f"{len(tried)} calls refused with code 2 -- "
             + ", ".join(code or "the usage" for _one, code in tried.values()) + " -- and no folder written")
    else:
        failures.append(f"  ✗ (f) the refusals            accepted={accepted} written={nowhere.exists()}")

    # --- (g) nothing of a provider in the player; the place of the fixed part is the adapter's ----------------
    hosts = sorted(one.name for one in (SOURCE / "adapters").iterdir() if (one / "wire.py").is_file())
    code = PLAYER.read_text(encoding="utf-8") if PLAYER.is_file() else ""
    named = [one for one in hosts if one != C.PROVIDER and one in code]
    try:
        player = C.module().turn_module()
        declared = {one: getattr(player.adapter_of(one), "SYSTEM_PROMPT", None) for one in hosts}
        fixed, where = made / "fixed.md", bench.temp()
        given = next(one for one, says in declared.items() if says is True)
        argv, _env, stdin, went = player.composition(given, where, fixed, "system", "the prompt")
        by_system = str(fixed) in argv and stdin == "the prompt" and went == "system"
        argv, _env, stdin, went = player.composition(given, where, fixed, "head", "the prompt")
        by_head = str(fixed) not in argv and stdin.startswith(FIXED) and stdin.endswith("the prompt") and went == "head"
        _argv, _env, stdin, went = player.composition(C.PROVIDER, where, fixed, "system", "the prompt")
        without = stdin.startswith(FIXED) and went == "head"
        _argv, _env, stdin, went = player.composition(C.PROVIDER, where, fixed, "system", "the prompt", session="s-1")
        resumed = stdin == "the prompt" and went == "head"
        _argv, _env, stdin, went = player.composition(C.PROVIDER, where, None, "system", "the prompt")
        nothing = stdin == "the prompt" and went is None
        natures = [player.nature(one) for one in ("...", " [] \n", '{"re": 1}', "done", "", "```json\n[]\n```", "7")]
    except Exception as raised:                                # a launcher without the player, a player without a face
        declared, by_system, by_head, without, resumed, nothing, natures = {}, False, False, False, False, False, []
        named = named or [f"{type(raised).__name__}: {raised}"]
    if (code and not named and all(isinstance(one, bool) for one in declared.values()) and len(declared) == len(hosts)
            and declared.get(C.PROVIDER) is False and by_system and by_head and without and resumed and nothing
            and natures == ["dots", "json", "json", "text", "none", "text", "text"]):
        held("(g) nothing of a provider in the player", f"its code names none of {', '.join(hosts)} but the model's "
             f"word; `SYSTEM_PROMPT` declared by every adapter: {declared}; the fixed part rides the marble of the "
             "call where the adapter gives one, the head of the first prompt otherwise and under `place: head`, "
             "never a resumed launch; a message is `dots`, `json`, `text` or `none` by its form")
    else:
        failures.append(f"  ✗ (g) the player              named={named} declared={declared} system={by_system} "
                        f"head={by_head} without={without} resumed={resumed} nothing={nothing} natures={natures}")

    # --- (h) the phase of a message, where the adapter gives the transcript -------------------------------------
    stored = bench.temp() / "stored.jsonl"
    stored.write_text("{}\n", encoding="utf-8")
    pieces = bench.temp() / "kept" / "lone" / "1"
    pieces.mkdir(parents=True)
    face = types.SimpleNamespace(transcript=lambda session: {"path": str(stored), "messages": [
        {"text": "working", "phase": "commentary"}, {"text": "[]", "phase": "final_answer"}]})
    heard = [{"launch": 1, "kind": "words", "text": "working"},
             {"launch": 1, "kind": "tool", "id": "t1", "name": "Bash", "shell": f"./pp {KEY} -"},
             {"launch": 1, "kind": "tool-result", "id": "t1", "content": judged + "\n"},
             {"launch": 1, "kind": "words", "text": "[]"}]
    try:
        spoken = player.transcript_of(face, "s-1", pieces)
        row = player.row_of({"repetition": 1, "launches": [{}], "events": heard, "spoken": spoken, "error": None,
                             "seconds": 0.0, "cost_usd": None, "transcript": "transcript.jsonl"}, pieces, pieces.parents[1])
        foot = player.foot_of([row])
        faceless = player.transcript_of(types.SimpleNamespace(), "s-1", pieces)
    except Exception as raised:                                # a player without the face: the row says what was raised
        row, foot, faceless = {"raised": f"{type(raised).__name__}: {raised}"}, {}, "raised"
    if ((pieces / "transcript.jsonl").is_file() and row.get("phases") == ["commentary", "final_answer"]
            and row.get("sequence") == [["words", "pp", "words"]] and row.get("last") == "json"
            and foot.get("last_phase") == {"final_answer": 1} and faceless is None):
        held("(h) the phase of a message", "the transcript the adapter names copied beside the pieces; each message "
             "its phase, the foot the phase of the last one; no face, no phase")
    else:
        failures.append(f"  ✗ (h) the phase               {row} {foot} {faceless}")

    # --- (i) a fixed part outside the set ------------------------------------------------------------------------
    apart = witness(bench)
    shared = apart.parent / "texts" / "shared.md"
    shared.parent.mkdir()
    shared.write_text(FIXED, encoding="utf-8")
    (apart / MANIFEST).write_text(
        "variants:\n  beside:\n    fixed: ../texts/shared.md\n    prompts: [two.md]\n"
        f"  absolute:\n    fixed: {shared}\n    prompts: [two.md]\n", encoding="utf-8")
    elsewhere = bench.temp() / "out"
    beside = C.launcher("turn", "--set", str(apart), "--provider", C.PROVIDER, "--out", str(elsewhere))
    found = sorted(elsewhere.glob("*/*/1")) if elsewhere.is_dir() else []
    heads = [(one / "prompt.txt").read_text(encoding="utf-8") if (one / "prompt.txt").is_file() else "" for one in found]
    wrongs = {"fixed": "variants:\n  lone:\n    fixed: ../texts/absent.md\n    prompts: [two.md]\n",
              "prompt": "variants:\n  lone:\n    prompts: [../texts/shared.md]\n",
              "file": "files:\n  NOTES.txt: ../texts/shared.md\nvariants:\n  lone:\n    prompts: [two.md]\n"}
    refused = {}
    for name, text in wrongs.items():
        (apart / MANIFEST).write_text(text, encoding="utf-8")
        refused[name] = C.launcher("turn", "--set", str(apart), "--provider", C.PROVIDER, "--out", str(nowhere))
    kept_out = {name: (one.returncode, one.stderr[-200:]) for name, one in refused.items()
                if one.returncode != 2 or "manifest-invalid" not in one.stderr}
    if (beside.returncode == 0 and sorted(one.parent.name for one in found) == ["absolute", "beside"]
            and all(text.startswith(FIXED) and text.endswith(BLOCK_TWO) for text in heads)
            and not kept_out and not nowhere.exists() and not (apart / "shared.md").exists()):
        held("(i) a fixed part outside the set", "`../texts/shared.md` and its absolute path both play, the first "
             "prompt opening on that text; a `fixed:` that names no file, a prompt and an accessory outside the "
             "set: manifest-invalid, nothing written")
    else:
        failures.append(f"  ✗ (i) a fixed part outside    rc={beside.returncode} found={[str(one) for one in found]} "
                        f"kept_out={kept_out} {beside.stderr[-300:]!r}")

    # --- (j) the throwaway directory is a git repository ----------------------------------------------------------
    repo = witness(bench, "variants:\n  lone:\n    prompts: [one.md]\n    model: [{read: .git/HEAD}]\n")
    there = bench.temp() / "out"
    lone = C.launcher("turn", "--set", str(repo), "--provider", C.PROVIDER, "--out", str(there))
    pieces = next(iter(sorted(there.glob("*/lone/1"))), there)
    heads = [one.get("stdin", "") for one in lines_of(pieces / "received.jsonl") if one.get("argv", [])[1:2] == ["-print"]]
    carried = sorted(one.name for one in pieces.iterdir() if one.name.startswith(".git")) if pieces.is_dir() else []
    if lone.returncode == 0 and len(heads) == 1 and "ref: refs/heads/" in heads[0] and not carried:
        held("(j) the throwaway directory is a git repository", "the model reads `.git/HEAD` in its directory and prints: "
             f"`{heads[0].rsplit(': ', 1)[-1]}`; nothing of the repository among the kept pieces")
    else:
        failures.append(f"  ✗ (j) a git repository        rc={lone.returncode} said={heads} carried={carried} "
                        f"{lone.stderr[-300:]!r}")

    def rows_under(where: Path, name: str = "lone") -> tuple[list[dict], dict]:
        """-> (the rows, the foot) of a variant in the one table written under `where`."""
        found = read(next(iter(sorted(where.glob("*/turn.json"))), where / "none"))
        variant = found.get("variants", {}).get(name, {})
        return variant.get("rows", []), variant.get("foot", {})

    # --- (k) a repetition that raises does not lose the campaign -----------------------------------------------
    alone = witness(bench, "variants:\n  lone:\n    prompts: [one.md]\n")
    raised_out = bench.temp() / "out"
    seen, calls = {}, []
    try:
        fresh = C.module().turn_module()
        real = fresh.laid

        def failing(manifest: dict, where: Path) -> None:
            calls.append(where)
            if len(calls) == 3:
                seen["rows"] = len(rows_under(raised_out)[0])
            if len(calls) == 2:
                raise RuntimeError("laid fails")
            real(manifest, where)

        fresh.laid = failing
        with contextlib.redirect_stdout(io.StringIO()):
            code_k = fresh.main(["--set", str(alone), "--provider", C.PROVIDER, "--repeat", "3",
                                 "--out", str(raised_out)])
    except Exception as raised:                                # the campaign lost: what a repetition raised
        code_k = f"{type(raised).__name__}: {raised}"
    rows_k, foot_k = rows_under(raised_out)
    second = read(next(iter(sorted(raised_out.glob("*/lone/2/launch.json"))), raised_out / "none"))
    if (code_k == 1 and [row.get("repetition") for row in rows_k] == [1, 2, 3]
            and [row.get("error") for row in rows_k] == [None, "RuntimeError", None]
            and "laid fails" in str(rows_k[1].get("cause")) and foot_k.get("errors") == 1
            and foot_k.get("repetitions") == 3 and seen.get("rows") == 2 and second.get("error") == "RuntimeError"
            and bool(list(raised_out.glob("*/TURN.md")))):
        held("(k) a repetition that raises", "three repetitions, the second raising at its laying: its row carries "
             "the error and its cause, the two others play, the table written with its foot (1 error), rewritten "
             "at every repetition that ends (2 rows when the third starts), the verb renders 1")
    else:
        failures.append(f"  ✗ (k) a repetition raises     code={code_k} seen={seen} second={second.get('error')} "
                        f"rows={[(row.get('repetition'), row.get('error'), row.get('cause')) for row in rows_k]}")

    # --- (l) the bound of a launch, a stream that is no UTF-8, a face that raises ---------------------------------
    wits = bench.temp() / "witness-adapters"
    for name, (script, events_body, named) in WITNESS_ADAPTERS.items():
        (wits / name).mkdir(parents=True)
        (wits / name / "wire.py").write_text(WITNESS_ADAPTER.format(script=script, events=events_body, error=named),
                                             encoding="utf-8")
    bounded = {}
    for name, extra in (("slow", ["--timeout", "1"]), ("garbled", []), ("raising", ["--repeat", "2"])):
        where = bench.temp() / "out"
        try:
            witnessed = C.module().turn_module()
            witnessed.ADAPTERS = wits
            with contextlib.redirect_stdout(io.StringIO()):
                code = witnessed.main(["--set", str(alone), "--provider", name, "--out", str(where), *extra])
        except Exception as raised:                            # the campaign lost: what a launch raised
            code = f"{type(raised).__name__}: {raised}"
        rows, foot = rows_under(where)
        kept_stdout = next(iter(sorted(where.glob("*/lone/1/stdout.txt"))), None)
        bounded[name] = {"code": code, "errors": [row.get("error") for row in rows], "foot": foot.get("errors"),
                         "seconds": [row.get("seconds") for row in rows],
                         "stdout": kept_stdout.read_text(encoding="utf-8") if kept_stdout else None}
    unbounded = C.launcher("turn", "--set", str(alone), "--provider", C.PROVIDER, "--timeout", "0", "--out", str(nowhere))
    if (bounded["slow"]["code"] == 1 and bounded["slow"]["errors"] == ["timeout"] and bounded["slow"]["seconds"][0] < 20
            and bounded["garbled"]["code"] == 0 and bounded["garbled"]["errors"] == [None]
            and "no utf-8" in str(bounded["garbled"]["stdout"])
            and bounded["raising"]["code"] == 1 and bounded["raising"]["errors"] == ["ValueError", "ValueError"]
            and bounded["raising"]["foot"] == 2
            and unbounded.returncode == 2 and "flag-invalid" in unbounded.stderr and not nowhere.exists()):
        held("(l) a launch is bounded, a stream is read, a face may raise", "`--timeout 1` on a launch that sleeps: "
             f"the error `timeout` after {bounded['slow']['seconds'][0]} s, the verb renders 1; a stream that is no "
             "UTF-8 read all the same, kept, no error; a face that raises: each repetition ends on `ValueError`, "
             "the table written; `--timeout 0`: flag-invalid")
    else:
        failures.append(f"  ✗ (l) the bound of a launch   {bounded} unbounded={unbounded.returncode}")

    # --- (m) the last message is the one of the last launch -----------------------------------------------------
    mute = witness(bench, "variants:\n  lone:\n    prompts: [two.md, proof.md]\n")
    muted_out = bench.temp() / "out"
    muted = C.launcher("turn", "--set", str(mute), "--provider", C.PROVIDER, "--out", str(muted_out))
    rows_m, foot_m = rows_under(muted_out)
    if (muted.returncode == 0 and len(rows_m) == 1 and rows_m[0].get("launches") == 2 and rows_m[0].get("messages") == 2
            and rows_m[0].get("last") == "dots" and foot_m.get("last", {}).get("dots") == 1
            and rows_m[0].get("received") == 1):
        held("(m) the last message is the last launch's", "two launches, the JSON message at the first, `...` at the "
             "second: `last` is `dots` at the row and at the foot")
    else:
        failures.append(f"  ✗ (m) the last message        rc={muted.returncode} "
                        f"{[(row.get('launches'), row.get('messages'), row.get('last')) for row in rows_m]} {foot_m.get('last')}")

    # --- (n) a call of the console is read at what the fake answered --------------------------------------------
    told = bench.temp() / "kept" / "lone" / "1"
    told.mkdir(parents=True)
    (told / "received.jsonl").write_text("".join(json.dumps({"argv": [], "stdin": ""}) + "\n" for _ in range(3)),
                                         encoding="utf-8")
    judged_line = judged + "\n"
    shells = [("bash -lc './pp'", judged_line), ("cat pp", "#!/bin/sh\nexec python .pp/console.py\n"),
              ("ls -la pp .pp", "pp\n.pp\n"), ("git add pp", ""), (f"./pp {KEY}; ./pp {KEY}", judged_line * 2)]
    called = []
    for at, (shell, content) in enumerate(shells):
        called += [{"launch": 1, "kind": "tool", "id": f"t{at}", "name": "Bash", "shell": shell},
                   {"launch": 1, "kind": "tool-result", "id": f"t{at}", "content": content}]
    try:
        row_n = player.row_of({"repetition": 1, "launches": [{}], "events": called, "spoken": None, "error": None,
                               "seconds": 0.0, "cost_usd": None, "transcript": None}, told, told.parents[1])
    except Exception as raised:                                # a player without the reading
        row_n = {"raised": f"{type(raised).__name__}: {raised}"}
    if row_n.get("sequence") == [["pp", "tool", "tool", "tool", "pp", "pp"]] and row_n.get("received") == 3:
        held("(n) a call of the console is read at the fake's answer", "a call under `bash -lc` whose result carries "
             "the answer is `pp`; `cat pp`, `ls -la pp .pp` and `git add pp` are `tool`; a call the fake answered "
             "twice is `pp` twice: three `pp`, three received")
    else:
        failures.append(f"  ✗ (n) the console's call      {row_n.get('sequence')} received={row_n.get('received')} "
                        f"{row_n.get('raised')}")

    # --- (o) the manifests refused -------------------------------------------------------------------------------
    lone_variant = "    prompts: [one.md]\n"
    written = {"variant turn.json": f"variants:\n  turn.json:\n{lone_variant}",
               "variant TURN.md": f"variants:\n  TURN.md:\n{lone_variant}",
               "variant unnamed": f"variants:\n  '':\n{lone_variant}",
               "file unnamed": f"files:\n  '': NOTES.txt\nvariants:\n  lone:\n{lone_variant}",
               "file a directory": f"files:\n  sub/: NOTES.txt\nvariants:\n  lone:\n{lone_variant}",
               "files mistyped": f"files: [{{a: b}}]\nvariants:\n  lone:\n{lone_variant}"}
    judged_sets = {}
    for name, text in written.items():
        (alone / MANIFEST).write_text(text, encoding="utf-8")
        judged_sets[name] = C.launcher("turn", "--set", str(alone), "--provider", C.PROVIDER, "--out", str(nowhere))
    passed = {name: (one.returncode, one.stderr[-160:]) for name, one in judged_sets.items()
              if one.returncode != 2 or "manifest-invalid" not in one.stderr}
    if not passed and not nowhere.exists():
        held("(o) the manifests refused", f"{len(written)} manifests refuse manifest-invalid, nothing written: "
             + ", ".join(written))
    else:
        failures.append(f"  ✗ (o) the manifests           passed={passed} written={nowhere.exists()}")

    # --- (p) the cause of an error ---------------------------------------------------------------------------------
    (alone / MANIFEST).write_text(f"variants:\n  lone:\n{lone_variant}", encoding="utf-8")
    caused_out = bench.temp() / "out"
    caused = C.launcher("turn", "--set", str(alone), "--provider", C.PROVIDER, "--model", "nobody", "--out", str(caused_out))
    rows_p, _foot = rows_under(caused_out)
    first = read(next(iter(sorted(caused_out.glob("*/lone/1/launch.json"))), caused_out / "none"))
    table_text = next(iter(sorted(caused_out.glob("*/TURN.md"))), None)
    if (caused.returncode == 1 and len(rows_p) == 1 and rows_p[0].get("error")
            and "variant-unknown" in str(rows_p[0].get("cause")) and "variant-unknown" in str(first.get("cause"))
            and "variant-unknown" in str((first.get("launches") or [{}])[0].get("cause"))
            and table_text is not None and "variant-unknown" in table_text.read_text(encoding="utf-8")):
        held("(p) the cause of an error", f"a variant the model's harness refuses: the row says `{rows_p[0]['error']}` "
             "and keeps the harness's own refusal as its cause, in turn.json, launch.json and TURN.md")
    else:
        failures.append(f"  ✗ (p) the cause               rc={caused.returncode} "
                        f"{[(row.get('error'), row.get('cause')) for row in rows_p]} {first.get('cause')!r}")

    # --- (q) the fingerprint of the fixed part --------------------------------------------------------------------
    print_of = {"fixed_sha256": hashlib.sha256(FIXED.encode("utf-8")).hexdigest(), "fixed_chars": len(FIXED)}
    printed = [{key: one.get(key) for key in print_of} for one in launches.values()]
    tabled = [{key: variants.get(name, {}).get(key) for key in print_of} for name in ("single", "double")]
    unprinted = read(next(iter(sorted(muted_out.glob("*/lone/1/launch.json"))), muted_out / "none"))
    if (all(one == print_of for one in printed + tabled) and len(printed) == 4
            and "fixed_sha256" in unprinted and unprinted["fixed_sha256"] is None and unprinted.get("fixed_chars") is None
            and print_of["fixed_sha256"] in (folder / "TURN.md").read_text(encoding="utf-8")):
        held("(q) the fingerprint of the fixed part", f"sha256 {print_of['fixed_sha256'][:12]}… and {print_of['fixed_chars']} "
             "characters in the four launch.json, in turn.json and in TURN.md; none for a variant without a fixed part")
    else:
        failures.append(f"  ✗ (q) the fingerprint         {printed[:1]} {tabled[:1]} unprinted={unprinted.get('fixed_sha256', 'absent')}")

    # --- (r) one folder per play ------------------------------------------------------------------------------------
    shared_out = bench.temp() / "out"
    try:
        twice = [player.folder_of(shared_out, "2026-11-15T000000") for _ in range(3)]
    except Exception as raised:                                # a player without the face
        twice = [f"{type(raised).__name__}: {raised}"]
    if len(twice) == 3 and len({str(one) for one in twice}) == 3 and all(Path(one).is_dir() for one in twice) \
            and all(Path(one).parent == shared_out for one in twice):
        held("(r) one folder per play", "three plays of the same second under one `--out`: three folders, "
             + ", ".join(Path(one).name for one in twice))
    else:
        failures.append(f"  ✗ (r) one folder per play     {twice}")

    # --- (s) a play interrupted stops its queue ---------------------------------------------------------------------
    def interrupted_by(signum: int, jobs: int) -> dict:
        """Four repetitions of a launch that sleeps, `jobs` at once, the signal sent to this process half a
        second after the first laying -> what the play rendered and left. A handler of the scenario's own
        stands under the player's: a signal the player lets through is counted, never fatal."""
        where, through, timers = bench.temp() / "out", [], []

        def fallback(*_signal) -> None:
            through.append(signum)

        before = signal.signal(signum, fallback)
        started = time.monotonic()
        try:
            play = C.module().turn_module()
            play.ADAPTERS = wits
            real = play.laid

            def then(manifest: dict, at: Path) -> None:
                if not timers:
                    timers.append(threading.Timer(0.5, os.kill, (os.getpid(), signum)))
                    timers[0].start()
                real(manifest, at)

            play.laid = then
            with contextlib.redirect_stdout(io.StringIO()):
                code = play.main(["--set", str(alone), "--provider", "slow", "--repeat", "4", "--jobs", str(jobs),
                                  "--timeout", "3", "--out", str(where)])
            given_back = signal.getsignal(signum) is fallback
        except BaseException as raised:                        # noqa: BLE001 -- the play lost: what the signal raised
            code, given_back = f"{type(raised).__name__}: {raised}", False
        finally:
            signal.signal(signum, before)
            for timer in timers:
                timer.cancel()
        rows, _foot = rows_under(where)
        table = read(next(iter(sorted(where.glob("*/turn.json"))), where / "none"))
        first = read(next(iter(sorted(where.glob("*/lone/1/launch.json"))), where / "none"))
        return {"code": code, "errors": [row.get("error") for row in rows], "through": len(through),
                "seconds": round(time.monotonic() - started, 1), "interrupted": table.get("interrupted"),
                "rc": [one.get("rc") for one in first.get("launches") or []], "given_back": given_back}

    stopped = {"SIGINT": interrupted_by(signal.SIGINT, 1), "SIGTERM": interrupted_by(signal.SIGTERM, 2)}
    if all(one["code"] not in (0, 1, 2) and isinstance(one["code"], int) and one["through"] == 0 and one["seconds"] < 2.5
           and one["interrupted"] is True and one["given_back"] and one["rc"] == [-signal.SIGKILL]
           for one in stopped.values()) \
            and stopped["SIGINT"]["errors"] == ["interrupted"] and stopped["SIGTERM"]["errors"] == ["interrupted"] * 2 \
            and stopped["SIGINT"]["code"] == stopped["SIGTERM"]["code"]:
        held("(s) a play interrupted stops its queue", f"four repetitions of a launch that sleeps: SIGINT with one "
             f"in flight, SIGTERM with two -- the launches in flight killed, their rows `interrupted`, no other "
             f"repetition started, the table written and marked, {stopped['SIGINT']['seconds']} s and "
             f"{stopped['SIGTERM']['seconds']} s where the bound of a launch is 3 s; the verb renders "
             f"{stopped['SIGINT']['code']}, the signals given back")
    else:
        failures.append(f"  ✗ (s) a play interrupted      {stopped}")

    # --- (t) the cause says what the harness said, or nothing -----------------------------------------------------
    spent_out = bench.temp() / "out"
    try:
        spending = C.module().turn_module()
        spending.ADAPTERS = wits
        with contextlib.redirect_stdout(io.StringIO()):
            code_t = spending.main(["--set", str(alone), "--provider", "spent", "--out", str(spent_out)])
    except Exception as raised:                                # the campaign lost: what the play raised
        code_t = f"{type(raised).__name__}: {raised}"
    rows_t, _foot = rows_under(spent_out)
    launch_t = read(next(iter(sorted(spent_out.glob("*/lone/1/launch.json"))), spent_out / "none"))
    if (code_t == 1 and [(row.get("error"), row.get("cause")) for row in rows_t] == [("budget spent", None)]
            and launch_t.get("session") == "s-witness" and launch_t.get("cause") is None
            and "cause" in launch_t and [one.get("cause") for one in launch_t.get("launches") or []] == [None]):
        held("(t) the cause says what the harness said, or nothing", "an adapter that names `budget spent`, "
             "answers a session and says nothing on stderr: the error at the row, no cause -- in turn.json and "
             "in launch.json")
    else:
        failures.append(f"  ✗ (t) the cause, or nothing   code={code_t} "
                        f"{[(row.get('error'), row.get('cause')) for row in rows_t]} {launch_t.get('cause')!r}")
    return 0
