"""Scenario `launcher/mask` -- 4 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
le-masque-et-le-contenu, 2026-10-28): the MASK of the sheet of response and the COMPARISON of two sheets,
proven under the modelled LLM on a throwaway house -- `long-read`, `gesture-while-held` and `stray` played
on the relayed channel, `strict`:
- (a) every line of the sheet carries the ZONE of the oracle's item that handed its text, and the foot counts
  the lines by that zone (`by_line_zone`) beside the zones the exchange crossed; the chunks of `long-read`
  stand in `chunk`; since the batch la-main-et-les-clotures (2026-10-28) neither `long-read` nor
  `gesture-while-held` carries a `rouge-conduction` line
- (b) `sheet <date> --mask chunk,bounce` rewrites the sheet with zero `rouge-conduction` outside the mask, the
  masked lines counted apart with their reds (none left); the lines with and without the mask differ by the flag `masked`
  alone (the fields compared, the flag stripped); `--mask agent` leaves zero `rouge-agent` outside the mask on
  `stray`; a zone no coverage knows refuses `mask-unknown`
- (c) `sheet <d2> --against <d1>` on two campaigns of the same roots (the other named by its path here: the two
  plays of a scenario fall in the same minute) writes `compare.json` and `COMPARE.md`: every line paired by
  (exchange, channel, rank), zero changed verdict, nothing appeared or disappeared; replayed, the same bytes
- (d) the same comparison with the mask on one side pairs the same lines and counts the masked apart: the
  counts of the two sides differ by the masked lines alone
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")
ROOTS = ("--root", "long-read", "--root", "gesture-while-held", "--root", "stray")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, _coverage, folder, _house = C.played(bench, *ROOTS, "--channel", C.RELAYED, "--conduction", C.STRICT)
    sheet = C.sheet_of(folder)
    lines = sheet.get("lines", [])

    # --- (a) the zone of every line -----------------------------------------------------------------------------
    zoned = [one for one in lines if one.get("zone")]
    reds = {one["exchange"].split("-relayed")[0]: sorted({two["zone"] for two in lines
                                                           if two["exchange"] == one["exchange"]
                                                           and two["verdict"] == "rouge-conduction"})
            for one in lines}
    by_line_zone = sheet.get("by_line_zone") or {}
    if (done.returncode == 0 and lines and len(zoned) == len(lines) and by_line_zone
            and reds.get("long-read") == [] and reds.get("gesture-while-held") == []
            and "chunk" in {one["zone"] for one in lines if one["exchange"].startswith("long-read")}
            and sum(sum(one.values()) for one in by_line_zone.values()) == len(lines)):
        held("(a) every line carries its zone", f"{len(lines)} lines, every one zoned; long-read's chunks zoned "
             "`chunk`, no rouge-conduction in long-read nor gesture-while-held; by_line_zone "
             f"{ {zone: sum(one.values()) for zone, one in by_line_zone.items()} }")
    else:
        failures.append(f"  ✗ (a) the zones               rc={done.returncode} zoned={len(zoned)}/{len(lines)} "
                        f"reds={reds} by_line_zone={sorted(by_line_zone)} {done.stderr[-200:]!r}")

    # --- (b) the mask ---------------------------------------------------------------------------------------------
    masked = C.launcher("sheet", folder.name, "--out", str(folder.parent), "--mask", "chunk,bounce")
    after = C.sheet_of(folder)
    apart = after.get("masked") or {}
    same = C.bare_lines(after.get("lines", [])) == C.bare_lines(lines)
    flagged = [one for one in after.get("lines", []) if one.get("masked")]
    agent = C.launcher("sheet", folder.name, "--out", str(folder.parent), "--mask", "agent")
    by_agent = C.sheet_of(folder)
    unknown = C.launcher("sheet", folder.name, "--out", str(folder.parent), "--mask", "nowhere")
    if (masked.returncode == 0 and after.get("mask") == ["chunk", "bounce"]
            and after["by_verdict"].get("rouge-conduction") == 0 and sheet["by_verdict"].get("rouge-conduction", 0) == 0
            and apart.get("lines") == len(flagged) and len(flagged) > 0 and apart.get("red", 0) == 0 and same
            and all(one["verdict"] == sheet["lines"][one["n"] - 1]["verdict"] for one in flagged)
            and agent.returncode == 0 and by_agent["by_verdict"].get("rouge-agent") == 0
            and sheet["by_verdict"].get("rouge-agent", 0) > 0
            and unknown.returncode == 2 and "mask-unknown" in unknown.stderr):
        held("(b) the mask changes no verdict", f"`--mask chunk,bounce`: {apart['lines']} lines masked, "
             f"{apart['red']} red among them, 0 rouge-conduction outside (was {sheet['by_verdict']['rouge-conduction']}); "
             f"the lines identical but the flag; `--mask agent`: 0 rouge-agent outside (was "
             f"{sheet['by_verdict']['rouge-agent']}); `nowhere`: mask-unknown")
    else:
        failures.append(f"  ✗ (b) the mask                rc={masked.returncode} mask={after.get('mask')} "
                        f"reds={after.get('by_verdict')} apart={apart} same={same} agent={by_agent.get('by_verdict')} "
                        f"unknown={unknown.returncode} {masked.stderr[-200:]!r}")

    # --- (c) two campaigns compared -------------------------------------------------------------------------------
    C.launcher("sheet", folder.name, "--out", str(folder.parent))        # the first sheet bare again
    again, _c2, second, _h2 = C.played(bench, *ROOTS, "--channel", C.RELAYED, "--conduction", C.STRICT)
    compared = C.launcher("sheet", second.name, "--out", str(second.parent), "--against", str(folder))
    first = C.compare_of(second)
    before = (second / "compare.json").read_bytes() if (second / "compare.json").is_file() else b""
    replay = C.launcher("sheet", second.name, "--out", str(second.parent), "--against", str(folder))
    bytes_after = (second / "compare.json").read_bytes() if (second / "compare.json").is_file() else b""
    counts = first.get("counts") or {}
    if (again.returncode == 0 and compared.returncode == 0 and replay.returncode == 0
            and first.get("before") == folder.name and first.get("after") == second.name
            and len(first.get("paired", [])) == len(lines) and counts.get("changed") == 0
            and not first.get("appeared") and not first.get("disappeared")
            and (second / "COMPARE.md").is_file() and before and before == bytes_after):
        held("(c) two campaigns compared", f"{len(first['paired'])} lines paired by (exchange, channel, rank), "
             f"0 changed, 0 appeared, 0 disappeared; compare.json {len(before)} bytes, replayed the same")
    else:
        failures.append(f"  ✗ (c) the comparison          rc={again.returncode}/{compared.returncode} paired="
                        f"{len(first.get('paired', []))}/{len(lines)} counts={counts} appeared={len(first.get('appeared', []))} "
                        f"same={before == bytes_after} {compared.stderr[-200:]!r}")

    # --- (d) the mask on one side -------------------------------------------------------------------------------
    sided = C.launcher("sheet", second.name, "--out", str(second.parent), "--mask", "chunk", "--against", str(folder))
    compare = C.compare_of(second)
    counts = compare.get("counts") or {}
    masked_after = (counts.get("after") or {}).get("masked") or {}
    masked_before = (counts.get("before") or {}).get("masked") or {}
    if (sided.returncode == 0 and len(compare.get("paired", [])) == len(lines) and counts.get("changed") == 0
            and masked_after.get("lines", 0) > 0 and masked_before.get("lines") == 0
            and (counts.get("after") or {}).get("by_verdict") != (counts.get("before") or {}).get("by_verdict")):
        held("(d) the mask on one side", f"the same {len(compare['paired'])} lines paired, 0 changed; after: "
             f"{masked_after['lines']} masked ({masked_after.get('red')} red), before: 0; the counts outside differ")
    else:
        failures.append(f"  ✗ (d) the sided mask          rc={sided.returncode} paired={len(compare.get('paired', []))} "
                        f"counts={counts} {sided.stderr[-200:]!r}")
    return 0
