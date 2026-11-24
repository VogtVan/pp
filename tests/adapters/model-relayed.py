"""Scenario `model-relayed` -- 4 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
l-adaptateur-model, 2026-10-27; the intention at la-campagne-au-banc, `read` at le-masque-et-le-contenu): the modelled LLM on the RELAYED channel -- the house conducts
(`agent run --provider model`), one launch of the harness per output pp holds for it -- on a throwaway house:
- READ_LINES: the run ends parked, the record says cost 0, one launch at least (the boot's WORK, the
  house's advance parking the run), words said, the session the model's; no repair, no refusal; its
  launches and its seconds are the measure (KM28), printed for the Delivery
- a LAPS door proven at every lap (the support's witness root: the campaign's LAPS writes no PROVE):
  parked at cost 0, no repair; each lap a block never served, held even though it asks a value -- the
  trace says `held`, never `inline`, and the exchange takes one launch per output the house served
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
from conductor.core import language
from tests.harness import support

M = support(__file__, "model")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = M.House(bench)
    read_lines = (str(M.DOCS / "read-lines"), "READ_LINES.md")
    laps = (str(M.proven_laps(bench)), "LAPS.md")

    def played(name: str, root: tuple[str, str], message: str) -> dict:
        (done, seconds) = M.timed(lambda: h.run(name, message, "--documents", root[0], "--door", root[1]))
        record = h.responses()[-1] if h.responses() else {}
        key = str(record.get("run") or "")        # the run of the exchange: the slots sort by name, not by hour
        stats = h.stats(name, key) if key else {}
        return {"rc": done.returncode, "key": key, "awaits": h.awaits(name, key) if key else "",
                "launches": record.get("launches"), "cost": record.get("cost_usd"), "words": record.get("words") or [],
                "repairs": stats.get("repairs"), "refusals": stats.get("refusals"), "seconds": seconds,
                "stderr": done.stderr[-300:], "record": record}

    # --- READ_LINES, and its measure ------------------------------------------------------------------------
    read = played("ag1", read_lines, "read the four lines")
    session = next((one for one in h.sessions() if one.get("run") == read["key"]), {})
    if (read["rc"] == 0 and read["awaits"] == persistence.MESSAGE and read["cost"] == 0.0
            and isinstance(read["launches"], int) and read["launches"] >= 1
            and read["words"] and all(str(one.get("text", "")).strip() for one in read["words"])
            and session.get("provider") == M.PROVIDER and str(session.get("session", "")).startswith("model-")
            and read["repairs"] == 0 and read["refusals"] == 0):
        held("READ_LINES plays on the relayed channel", f"run {read['key']}: parked, cost 0, {read['launches']} "
             f"launches, {len(read['words'])} words, session {session.get('session')} of {session.get('provider')}, "
             f"0 repair, 0 refusal, {read['seconds']} s -- the measure of the channel (KM28)")
    else:
        failures.append(f"  ✗ read-lines relayed         {read}")

    # --- LAPS proven at every lap: each lap never served, held for the house -----------------------------------
    lapped = played("ag1", laps, "play the door")
    kinds = [one.get("kind") for one in h.trace("ag1", lapped["key"])] if lapped["key"] else []
    inline, outputs = kinds.count("inline"), kinds.count("held")
    if (lapped["rc"] == 0 and lapped["awaits"] == persistence.MESSAGE and lapped["cost"] == 0.0
            and lapped["repairs"] == 0 and isinstance(lapped["launches"], int)
            and not inline and outputs >= 3 and lapped["launches"] == outputs):
        held("each lap is held for the house", f"LAPS: {lapped['launches']} launches ({lapped['seconds']} s) for "
             f"{outputs} outputs held, none inline; parked at cost 0, no repair")
    else:
        failures.append(f"  ✗ laps relayed               inline={inline} outputs={outputs} {lapped}")

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

    # --- the intention `read`: one line of the production per line of the file ---------------------------------
    source_lines = (M.DOCS / "LINES.txt").read_text(encoding="utf-8")
    (h.ws / "agents" / "ag1" / "LINES.txt").write_text(source_lines, encoding="utf-8")
    read_key = fresh("read the four lines", read_lines[0], read_lines[1], [{"read": "LINES.txt"}])
    read_prints = [str(one.get("given") or "") for one in (h.trace("ag1", read_key) if read_key else [])
                   if one.get("kind") == "answer" and one.get("channel") == language.TERMINAL]
    read_words = [line for one in read_prints for line in one.splitlines()]      # the lines of the WORK's print
    wanted = source_lines.splitlines()
    carrying = [said for said in read_words if any(line in said for line in wanted)]
    if (read_key and len(carrying) == len(wanted) and all(line in said for line, said in zip(wanted, carrying))
            and h.awaits("ag1", read_key) == persistence.MESSAGE):
        held("the intention `read` hands one line per line", f"run {read_key}: the WORK's print captured, "
             f"{len(read_words)} line(s), {len(carrying)} of them carrying one line of LINES.txt each, in order; parked")
    else:
        failures.append(f"  ✗ the intention read         key={read_key!r} words={read_words} wanted={len(wanted)}")
    return 0
