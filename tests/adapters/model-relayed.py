"""Scenario `model-relayed` -- 5 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
l-adaptateur-model, 2026-10-27; the intention at la-campagne-au-banc, `read` at le-masque-et-le-contenu): the modelled LLM on the RELAYED channel -- the house conducts
(`agent run --provider model`), one launch of the harness per output of pp -- on throwaway houses:
- READ_LINES under `conduction: strict`: the run ends parked, the record says cost 0, one launch at
  least (the boot's WORK, the house's advance parking the run), words said, the session the model's; no
  repair, no refusal
- a LAPS door proven at every lap (the support's witness root: the campaign's LAPS writes no PROVE),
  under strict and under `conduction: hybrid` (a second agent of the same house): both parked at cost 0,
  no repair; hybrid takes FEWER launches -- the value asked comes back in the model's tool result, the
  next lap with it
- the measure (KM28): launches and seconds of an exchange on READ_LINES per channel, strict and hybrid,
  printed for the Delivery
- the INTENTION of the model plays, handed in the harness's environment and remembered across the
  launches of a session: ROUTE picks RIGHT when the intention names it (the engine judges `RIGHT.md`),
  REVIEW's door is opened during the WORK when the intention names it (the trace says `routed`);
  without an intention the model conforms alone -- ROUTE's PICK elects the first option, no door opens
- the intention `read: <file>`: READ_LINES with `LINES.txt` laid in the agent's workspace says one `words`
  per line of the file at the WORK, each carrying its line, in order (the file's lines, never a sentence of
  the test); the boot's and the turn's words stand beside them
"""
from __future__ import annotations

from conductor import persistence
from tests.harness import support

M = support(__file__, "model")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = M.House(bench, agents=("ag1", "ag2"))
    h.hybrid("ag2")
    read_lines = (str(M.DOCS / "read-lines"), "READ_LINES.md")
    laps = (str(M.proven_laps(bench)), "LAPS.md")

    def played(name: str, root: tuple[str, str], message: str) -> dict:
        (done, seconds) = M.timed(lambda: h.run(name, message, "--documents", root[0], "--door", root[1]))
        key = h.keys(name)[-1] if h.keys(name) else ""
        record = h.responses()[-1] if h.responses() else {}
        stats = h.stats(name, key) if key else {}
        return {"rc": done.returncode, "key": key, "awaits": h.awaits(name, key) if key else "",
                "launches": record.get("launches"), "cost": record.get("cost_usd"), "words": record.get("words") or [],
                "repairs": stats.get("repairs"), "refusals": stats.get("refusals"), "seconds": seconds,
                "stderr": done.stderr[-300:], "record": record}

    # --- READ_LINES, strict ----------------------------------------------------------------------------
    strict = played("ag1", read_lines, "read the four lines")
    session = next((one for one in h.sessions() if one.get("run") == strict["key"]), {})
    if (strict["rc"] == 0 and strict["awaits"] == persistence.MESSAGE and strict["cost"] == 0.0
            and isinstance(strict["launches"], int) and strict["launches"] >= 1
            and strict["words"] and all(str(one.get("text", "")).strip() for one in strict["words"])
            and session.get("provider") == M.PROVIDER and str(session.get("session", "")).startswith("model-")
            and strict["repairs"] == 0 and strict["refusals"] == 0):
        held("READ_LINES plays on the relayed channel", f"run {strict['key']}: parked, cost 0, {strict['launches']} "
             f"launches, {len(strict['words'])} words, session {session.get('session')} of {session.get('provider')}, "
             f"0 repair, 0 refusal, {strict['seconds']} s")
    else:
        failures.append(f"  ✗ read-lines strict          {strict}")

    # --- LAPS, strict against hybrid ------------------------------------------------------------------------
    laps_strict = played("ag1", laps, "play the door")
    laps_hybrid = played("ag2", laps, "play the door")
    if (laps_strict["rc"] == 0 and laps_hybrid["rc"] == 0
            and laps_strict["awaits"] == persistence.MESSAGE and laps_hybrid["awaits"] == persistence.MESSAGE
            and laps_strict["cost"] == 0.0 and laps_hybrid["cost"] == 0.0
            and laps_strict["repairs"] == 0 and laps_hybrid["repairs"] == 0
            and isinstance(laps_strict["launches"], int) and isinstance(laps_hybrid["launches"], int)
            and laps_hybrid["launches"] < laps_strict["launches"]):
        held("hybrid takes fewer launches than strict", f"LAPS: strict {laps_strict['launches']} launches "
             f"({laps_strict['seconds']} s), hybrid {laps_hybrid['launches']} ({laps_hybrid['seconds']} s); both parked "
             "at cost 0, no repair")
    else:
        failures.append(f"  ✗ laps strict/hybrid         {laps_strict} / {laps_hybrid}")

    # --- the intention: a choice named, a door opened; conform without ------------------------------------
    route = (str(M.ROUTE), "ROUTE.md")

    def fresh(message: str, documents: str, door: str | None, intent: list | None) -> str:
        """-> the key of the run an `agent run` opens (the slots are sorted by name, not by hour)."""
        before = set(h.keys("ag1"))
        flags = ["--documents", documents, *(["--door", door] if door else [])]
        h.run("ag1", message, *flags, intent=intent)
        return next(iter(set(h.keys("ag1")) - before), "")

    def given(trace: list[dict], keyword: str) -> list[str]:
        return [str(one.get("given")) for one in trace if one.get("kind") == "answer"
                and str(one.get("instruction", "")).startswith(keyword)]

    alone_trace = h.trace("ag1", fresh("the number is 7", route[0], route[1], None))
    meant_key = fresh("the number is 7", route[0], route[1], [{"pick": "RIGHT.md"}])
    meant_trace = h.trace("ag1", meant_key)
    opened_trace = h.trace("ag1", fresh("say hello, then open the review", str(M.REVIEW), None, [{"open": "REVIEW"}]))
    closed_trace = h.trace("ag1", fresh("say hello", str(M.REVIEW), None, None))
    routed = [one.get("document") or one.get("name") or "" for one in opened_trace if one.get("kind") == "routed"]
    if (given(alone_trace, "NEXT") == ["LEFT.md"] and given(meant_trace, "NEXT") == ["RIGHT.md"]
            and routed and not any(one.get("kind") == "routed" for one in closed_trace)
            and h.awaits("ag1", meant_key) == persistence.MESSAGE):
        held("the intention of the model plays", f"ROUTE: LEFT.md without an intention, RIGHT.md with "
             f"`pick RIGHT.md`; REVIEW: routed {routed} with `open REVIEW`, no door without; both runs parked")
    else:
        failures.append(f"  ✗ the intention              alone={given(alone_trace, 'NEXT')} meant={given(meant_trace, 'NEXT')} "
                        f"routed={routed} closed={[one.get('kind') for one in closed_trace if one.get('kind') == 'routed']}")

    # --- the intention `read`: one words per line of the file -------------------------------------------------
    source_lines = (M.DOCS / "LINES.txt").read_text(encoding="utf-8")
    (h.ws / "agents" / "ag1" / "LINES.txt").write_text(source_lines, encoding="utf-8")
    read_key = fresh("read the four lines", read_lines[0], read_lines[1], [{"read": "LINES.txt"}])
    read_record = next((one for one in reversed(h.responses()) if one.get("run") == read_key), {})
    read_words = [str(one.get("text", "")) for one in (read_record.get("words") or [])]
    wanted = source_lines.splitlines()
    carrying = [said for said in read_words if any(line in said for line in wanted)]
    if (read_key and len(carrying) == len(wanted) and all(line in said for line, said in zip(wanted, carrying))
            and h.awaits("ag1", read_key) == persistence.MESSAGE):
        held("the intention `read` says one words per line", f"run {read_key}: {len(read_words)} words, {len(carrying)} "
             "of them carrying one line of LINES.txt each, in order; parked")
    else:
        failures.append(f"  ✗ the intention read         key={read_key!r} words={read_words} wanted={len(wanted)}")

    # --- the measure: READ_LINES on hybrid too -------------------------------------------------------------
    hybrid = played("ag2", read_lines, "read the four lines")
    if hybrid["rc"] == 0 and hybrid["awaits"] == persistence.MESSAGE and hybrid["cost"] == 0.0:
        held("the measure per channel (KM28)", f"READ_LINES relayed strict: {strict['launches']} launches, "
             f"{strict['seconds']} s; relayed hybrid: {hybrid['launches']} launches, {hybrid['seconds']} s; "
             f"LAPS strict {laps_strict['launches']} / hybrid {laps_hybrid['launches']} launches")
    else:
        failures.append(f"  ✗ read-lines hybrid          {hybrid}")
    return 0
