"""Scenario `agent-exchange-record` -- the record of an exchange: the words its launches said, the response
they compose, the policy played, the launches it costs -- on one house, plain first, then under a law of
production, then under the two settings of conduction:
- a plain house: ONE launch, the AWAIT fused in the boot's output; the `play` witness's answer, said as its
  words, is the response; no model and no effort asked: null
- the `stream` witness under a law of production: an exchange of two launches keeps `words` -- the words of
  each launch under its launch number, its answer among them --, `response` their composition, `model` and
  `effort` the policy played; every field of the record there
- the faces: `agent responses` renders the composed response, each words once; `agent exchanges --json`
  carries `words`, `model` and `effort`
- the `worded` witness (three texts at each launch, a blank one among them, the `result` line the last text
  alone): `words` keeps every text under its launch, in order, the blank one dropped; `response` carries them
  all, in their order, each once -- the words joined, nothing added
- the `agent` event that ends a launch carries no text: the flow keeps the words once, under `words`
- an output that asks the agent nothing -- the bare AWAIT served once the proof is judged -- launches
  nothing: under a law of production ONE exchange costs TWO launches, the boot with the WORK then the
  checkpoint the witness pipes its proof to; the flow says two `conduction` and two `agent` events -- a
  conduction is a launch's --, the verdict `parked`
- `conduction: hybrid`: ONE exchange on a described door, LAPS, offered to the TURN's WORK and
  opened by the witness, costs ONE launch -- the witness opens the door, pipes the field and the three proofs,
  each block read in its tool result (4 inline); the door consumes the WORK, the AWAIT comes bare at the
  principal's call and launches nothing --; 3 proofs, the run parked
- `conduction: strict`, the same house: one launch per output -- the door's opening, the field, three laps --,
  5 launches, 5 held, 3 proofs, the run parked
"""
from __future__ import annotations

import json

from conductor import settings
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

    # --- a plain house: one launch, the answer is the words ----------------------------------------------------
    plain, _, kept = woken(h, "plain")
    if (plain.returncode == 0 and kept.get("words") == [{"launch": 1, "text": "witness answer: play"}]
            and kept.get("response") == "witness answer: play"
            and kept.get("model") is None and kept.get("effort") is None):
        held("(c) the plain answer is the response", "words [{launch 1, the answer}], the response the same; no "
             "model and no effort asked: null")
    else:
        failures.append(f"  ✗ (c) plain                    rc={plain.returncode} words={kept.get('words')!r} "
                        f"model={kept.get('model')!r}")

    plain, _, kept = woken(h, "un")
    if plain.returncode == 0 and kept.get("launches") == 1 and "· parked ·" in plain.stderr:
        held("(b) a plain house: one launch", "the AWAIT fused in the boot's output, nothing more to launch")
    else:
        failures.append(f"  ✗ (b) plain                   rc={plain.returncode} launches={kept.get('launches')} "
                        f"{plain.stderr[-200:]!r}")
    h.lawful()

    # --- the stream witness: words, model and effort at the record --------------------------------------------
    woke, key, kept = woken(h, "say it", "stream", "--model", "m-one", "--effort", "high")
    words = kept.get("words") or []
    said = ["witness words", "witness answer: stream"]
    if (woke.returncode == 0 and kept.get("launches") == 2
            and words == [{"launch": n, "text": text} for n in (1, 2) for text in said]
            and kept.get("response") == "\n\n".join(said * 2)
            and kept.get("model") == "m-one" and kept.get("effort") == "high"
            and A.RECORD_FIELDS <= set(kept)):
        held("(a) words, model and effort at the record", f"run {key}: 2 launches, their words under each, "
             "response their composition, model m-one, effort high; the fields of before kept")
    else:
        failures.append(f"  ✗ (a) record                   rc={woke.returncode} launches={kept.get('launches')} "
                        f"words={words!r} model={kept.get('model')!r} effort={kept.get('effort')!r} "
                        f"missing={A.RECORD_FIELDS - set(kept)} {woke.stderr[-200:]!r}")

    # --- the faces: `responses` says the agent's last response -- this run's ---------------------------------
    shown = h.call("agent", "responses", "agents/ag1")
    listed = h.call("agent", "exchanges", "agents/ag1", key, "--json")
    rows = rows_of(listed)
    if (shown.returncode == 0 and shown.stdout.count("witness words") == 2
            and shown.stdout.count("witness answer: stream") == 2 and "[launch" not in shown.stdout
            and listed.returncode == 0 and len(rows) == 1 and rows[0].get("words") == words
            and rows[0].get("model") == "m-one" and rows[0].get("effort") == "high"):
        held("(b) responses and exchanges --json render them", "the composed response, each words once; "
             "words, model and effort on the exchange's line")
    else:
        failures.append(f"  ✗ (b) faces                    rc={shown.returncode}/{listed.returncode} "
                        f"{shown.stdout[-300:]!r} rows={rows!r}")

    # --- the worded witness: the words, and their composition -----------------------------------------------
    woke, key, kept = woken(h, "say three", "worded")
    launches = kept.get("launches") if isinstance(kept.get("launches"), int) else 0
    texts = [text for n in range(1, launches + 1)
             for text in (f"--- STEP ---\nfirst words {n}", f"second words {n}", f"third words {n}")]
    words = kept.get("words") or []
    response = kept.get("response") or ""
    if (woke.returncode == 0 and launches >= 2
            and words == [{"launch": n, "text": text} for n in range(1, launches + 1) for text in texts[3 * (n - 1):3 * n]]
            and response == "\n\n".join(texts)):
        held("(a) the response composed of the words", f"run {key}: {launches} launches, {len(words)} words under "
             "their launch, the blank one dropped; the response carries them all, in order, each once")
    else:
        failures.append(f"  ✗ (a) composed                 rc={woke.returncode} launches={launches} words={words!r} "
                        f"response={response!r} {woke.stderr[-200:]!r}")

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

    # --- the bare AWAIT under a law of production: two launches, the AWAIT unlaunched --------------------------
    woke, key, kept = woken(h, "un")
    events = flow_of(h, key)
    kinds = [one.get("kind") for one in events]
    conductions = [one for one in events if one.get("kind") == "conduction"]
    last_text = conductions[-1].get("text", "") if conductions else ""
    if (woke.returncode == 0 and kept.get("launches") == 2 and "2 launch(es)" in woke.stderr
            and "· parked ·" in woke.stderr and kinds.count("conduction") == 2 and kinds.count("agent") == 2
            and "INFER proof" in last_text and "▶ AWAIT" not in last_text
            and "served held output" in woke.stderr and "launch 3" not in woke.stderr
            and woke.stdout.strip() == A.composed(kept) and "witness answer: play" in woke.stdout):
        held("(a) the bare AWAIT launches nothing", "two launches -- the boot with the WORK, the checkpoint --, "
             "the AWAIT served and not launched, the run parked, the response composed of the two launches' words")
    else:
        failures.append(f"  ✗ (a) the AWAIT               rc={woke.returncode} launches={kept.get('launches')} "
                        f"kinds={kinds} final_launched={'▶ AWAIT' in last_text} {woke.stderr[-300:]!r}")

    # --- the door under the two settings of conduction: one launch in hybrid, one per output in strict ---------
    home = h.agent_meta / "procs"
    (home / "LAPS.md").write_text(LAPS, encoding="utf-8")
    (home / "TURN.md").write_text(TURN, encoding="utf-8")   # the law of production gone: the door's own laws alone

    def doors(conduction: str) -> dict:
        settings.write(h.agent_meta, "conduction", conduction)
        A.cli(h.engine, "--instance", str(h.agent_meta), "-build", cwd=h.ws, env=h.env)
        where = bench.temp() / f"doors-{conduction}"
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
                "parked": "· parked ·" in woke.stderr, "calls": len(h.calls(where)), "err": woke.stderr[-300:]}

    m = doors("hybrid")
    if (m["rc"] == 0 and m["launches"] == 1 and m["proofs"] == 3 and m["inline"] == 4 and m["held"] == 1
            and m["parked"] and m["calls"] == 5 and m["out"] == "witness answer: doors"):
        held("(a) hybrid: the whole door in the boot's launch", f"run {m['key']}: the witness opened LAPS on the "
             "pending WORK, piped the field and 3 proofs in the boot's launch (5 calls, 4 answered inline); the "
             "AWAIT held, served, not launched; parked -- 1 launch where strict takes 5")
    else:
        failures.append(f"  ✗ (a) hybrid                   {m!r}")
    ms = doors("strict")
    if (ms["rc"] == 0 and ms["launches"] == 5 and ms["proofs"] == 3 and ms["inline"] == 0 and ms["held"] == 5
            and ms["parked"] and ms["calls"] == 5):
        held("(b) strict: one launch per output", f"run {ms['key']}: the door, the field, three laps -- 5 launches, "
             "5 held outputs, 3 proofs; the AWAIT not launched; parked")
    else:
        failures.append(f"  ✗ (b) strict                   {ms!r}")
    return 0
