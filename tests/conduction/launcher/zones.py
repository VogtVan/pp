"""Scenario `launcher/zones` -- 4 case(s) (plan moteur-0.2.0, phase la-validation-de-la-conduction, batch
le-recensement-et-la-table, 2026-10-29): the CENSUS of the conduction tests -- the closed list of the zones
in the data of the model, the engine's version in the evidence, the verb `zones` that writes the coverage
section of the model's document from the evidence alone, and `zones --check` -- proven under the modelled
LLM on a throwaway house and a throwaway document:
- (a) `semantics.ZONES` stands (every zone with a phrase, dated by `ZONES_READ`, `root` out of it) and the
  launcher's `ZONE_EVENTS` has exactly its keys; a launcher whose `ZONE_EVENTS` lost a key refuses
  `zones-mismatch` at its first verb; `read-lines` played on the three channels writes `engine` in
  `campaign.json`, the engine's own VERSION
- (b) `zones --evidence <out> --doc <copy>` without a complete model campaign refuses `model-missing`; named by
  `--model`, it inserts the section between its two markers in a document that carries none: one row per zone of ZONES, the zones `read-lines` crosses on every channel they exist on
  `measured`, on fewer `partial`, the others `silent`; the begin marker names the model campaign and its engine;
  replayed, the same bytes; the text outside the markers untouched
- (c) a copy of the campaign read as a REAL one (`--real`): the zones three real exchanges cross on the same
  engine turn `safe` and their lines are vert; the same copy on another engine counts for nothing: no `safe`
- (d) `zones --check` on the written document rc 0 and names the engine; the marker rewritten on another
  engine: `engine-moved`; a document without the section: `coverage-missing`; a campaign whose `campaign.json`
  lacks `engine`: `evidence-unversioned`
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil

from conductor import VERSION
from tests.harness import support

C = support(__file__, "conduction")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ROW = re.compile(r"^\| `([a-z-]+)` \| .* \| (safe|measured|partial|silent) \|$")
PROSE = "# A witness document\n\nSome prose before.\n\n## 1. A section\n\nIts text.\n"


def rows_of(section: str) -> dict[str, str]:
    found = {}
    for line in section.splitlines():
        hit = ROW.match(line)
        if hit:
            found[hit.group(1)] = hit.group(2)
    return found


def marker_of(section: str) -> dict[str, str]:
    head = section.splitlines()[0] if section else ""
    return dict(re.findall(r"(\w+)=(\S+)", head.replace(" -->", "")))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    semantics = C.semantics()
    launcher = C.module()
    zones = dict(getattr(semantics, "ZONES", {}) or {})
    events = dict(getattr(launcher, "ZONE_EVENTS", {}) or {})

    # --- (a) the closed list, the events keyed on it, the engine in the evidence --------------------------------
    done, coverage, folder, _house = C.played(bench, "--root", "read-lines")
    campaign = C.campaign_of(folder)
    amputated = dict(events)
    amputated.pop("boot", None)
    launcher.ZONE_EVENTS = amputated
    err = io.StringIO()
    with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
        rc = launcher.main(["zones", "--evidence", str(folder.parent), "--doc", str(bench.temp() / "never.md")])
    launcher.ZONE_EVENTS = events
    if (zones and set(zones) == set(events)
            and all(isinstance(spec, dict) and str(spec.get("what", "")).strip() and spec.get("channels") for spec in zones.values())
            and "root" not in zones and DATE.match(str(getattr(semantics, "ZONES_READ", "")))
            and rc == 2 and "zones-mismatch" in err.getvalue()
            and done.returncode == 0 and len(coverage.get("exchanges", [])) == 3
            and campaign.get("engine") == VERSION):
        held("(a) the closed list and the engine", f"{len(zones)} zones, ZONE_EVENTS keyed on them, read on "
             f"{semantics.ZONES_READ}; a launcher short of `boot` refuses zones-mismatch; 3 exchanges of read-lines, "
             f"campaign.json says engine {campaign.get('engine')}")
    else:
        failures.append(f"  ✗ (a) the list                zones={len(zones)} same={set(zones) == set(events)} "
                        f"rc={rc} {err.getvalue()[-120:]!r} play={done.returncode} n={len(coverage.get('exchanges', []))} "
                        f"engine={campaign.get('engine')!r} {done.stderr[-200:]!r}")

    # --- (b) the section written from the evidence, replayed byte for byte ---------------------------------------
    doc = bench.temp() / "model.md"
    doc.write_text(PROSE, encoding="utf-8")
    incomplete = C.launcher("zones", "--evidence", str(folder.parent), "--doc", str(doc))
    first = C.launcher("zones", "--evidence", str(folder.parent), "--model", folder.name, "--doc", str(doc))
    before, section, after = C.section_of(doc)
    once = doc.read_bytes()
    again = C.launcher("zones", "--evidence", str(folder.parent), "--model", folder.name, "--doc", str(doc))
    twice = doc.read_bytes()
    rows = rows_of(section)
    marker = marker_of(section)
    by_channel: dict[str, set] = {}
    for one in coverage.get("exchanges", []):
        key = one.get("conduction") or one.get("channel")
        by_channel[key] = set(one.get("zones", {}))
    # a zone is measured when crossed on every channel it EXISTS on (the data's), partial on fewer
    full = {zone for zone, spec in zones.items() if all(zone in by_channel.get(key, set()) for key in spec["channels"])}
    some = set.union(*by_channel.values()) if by_channel else set()
    expected = {zone: ("measured" if zone in full else "partial" if zone in some else "silent") for zone in zones}
    if (incomplete.returncode == 2 and "model-missing" in incomplete.stderr and C.section_of(doc)[1]
            and first.returncode == 0 and again.returncode == 0 and section and once == twice
            and rows == expected and (before + after).strip() == PROSE.strip()
            and marker.get("model") == folder.name and marker.get("engine") == VERSION):
        held("(b) the section written and replayed", f"an incomplete evidence names no model campaign by default "
             f"(model-missing); named by `--model`: {len(rows)} rows: "
             + ", ".join(f"{status} {sum(1 for one in rows.values() if one == status)}"
                         for status in ("safe", "measured", "partial", "silent"))
             + f"; marker model={marker.get('model')} engine={marker.get('engine')}; replayed {len(twice)} bytes, the same; "
             "the prose around untouched")
    else:
        wrong = {zone: (rows.get(zone), expected.get(zone)) for zone in set(rows) | set(expected) if rows.get(zone) != expected.get(zone)}
        failures.append(f"  ✗ (b) the section             default={incomplete.returncode} rc={first.returncode}/{again.returncode} same={once == twice} "
                        f"wrong={wrong} around={(before + after).strip() == PROSE.strip()} marker={marker} {first.stderr[-200:]!r}")

    # --- (c) a real campaign read: safe on the same engine, nothing on another ----------------------------------
    real = folder.parent / f"{folder.name}-sonnet"
    shutil.copytree(folder, real)
    kept = json.loads((real / "campaign.json").read_text(encoding="utf-8"))
    (real / "campaign.json").write_text(json.dumps({**kept, "provider": "claude", "model": "sonnet"}, indent=2) + "\n",
                                        encoding="utf-8")
    with_real = C.launcher("zones", "--evidence", str(folder.parent), "--model", folder.name, "--real", real.name,
                           "--doc", str(doc))
    _b, section_real, _a = C.section_of(doc)
    rows_real = rows_of(section_real)
    marker_real = marker_of(section_real)
    safe = sorted(zone for zone, status in rows_real.items() if status == "safe")
    # safe: crossed on every channel the zone exists on, and by three real exchanges at least -- the copy
    # has three exchanges, so a zone the bare channel never crosses stays measured
    crossings = {zone: sum(1 for one in coverage.get("exchanges", []) if one.get("zones", {}).get(zone)) for zone in zones}
    owed_safe = sorted(zone for zone in full if crossings.get(zone, 0) >= launcher.SAFE_REAL)
    (real / "campaign.json").write_text(json.dumps({**kept, "provider": "claude", "model": "sonnet", "engine": "0.0.0"},
                                                   indent=2) + "\n", encoding="utf-8")
    older = C.launcher("zones", "--evidence", str(folder.parent), "--model", folder.name, "--real", real.name,
                       "--doc", str(doc))
    _b, section_older, _a = C.section_of(doc)
    rows_older = rows_of(section_older)
    if (with_real.returncode == 0 and safe and safe == owed_safe
            and all(rows_real[zone] == expected[zone] for zone in rows_real if zone not in owed_safe)
            and marker_real.get("real") == real.name
            and older.returncode == 0 and rows_older == expected):
        held("(c) a real campaign read", f"safe on the same engine: {safe} (three exchanges each); the other zones as "
             "under the model; "
             f"on engine 0.0.0 the real campaign counts for nothing: {sum(1 for s in rows_older.values() if s == 'safe')} safe")
    else:
        failures.append(f"  ✗ (c) the real                rc={with_real.returncode}/{older.returncode} safe={safe} "
                        f"owed={owed_safe} marker={marker_real} older_safe={[z for z, s in rows_older.items() if s == 'safe']} "
                        f"{with_real.stderr[-200:]!r}")

    # --- (d) the check and the refusals ----------------------------------------------------------------------------
    C.launcher("zones", "--evidence", str(folder.parent), "--model", folder.name, "--doc", str(doc))
    checked = C.launcher("zones", "--check", "--doc", str(doc))
    moved_doc = bench.temp() / "moved.md"
    moved_doc.write_text(doc.read_text(encoding="utf-8").replace(f"engine={VERSION}", "engine=0.0.0", 1), encoding="utf-8")
    moved = C.launcher("zones", "--check", "--doc", str(moved_doc))
    blank = bench.temp() / "blank.md"
    blank.write_text(PROSE, encoding="utf-8")
    missing = C.launcher("zones", "--check", "--doc", str(blank))
    (real / "campaign.json").write_text(json.dumps({**kept, "provider": "claude", "model": "sonnet"}, indent=2) + "\n",
                                        encoding="utf-8")
    unversioned_json = json.loads((folder / "campaign.json").read_text(encoding="utf-8"))
    unversioned_json.pop("engine", None)
    (folder / "campaign.json").write_text(json.dumps(unversioned_json, indent=2) + "\n", encoding="utf-8")
    unversioned = C.launcher("zones", "--evidence", str(folder.parent), "--model", folder.name, "--doc", str(blank))
    if (checked.returncode == 0 and VERSION in checked.stdout and folder.name in checked.stdout
            and moved.returncode == 2 and "engine-moved" in moved.stderr
            and missing.returncode == 2 and "coverage-missing" in missing.stderr
            and unversioned.returncode == 2 and "evidence-unversioned" in unversioned.stderr
            and C.section_of(blank)[1] == ""):
        held("(d) the check and the refusals", f"`zones --check`: {checked.stdout.strip()[:100]}; another engine: "
             "engine-moved; no section: coverage-missing; no `engine` in the evidence: evidence-unversioned, nothing written")
    else:
        failures.append(f"  ✗ (d) the check               {checked.returncode} {checked.stdout[-100:]!r} {checked.stderr[-100:]!r} "
                        f"{moved.returncode} {moved.stderr[-60:]!r} {missing.returncode} {missing.stderr[-60:]!r} "
                        f"{unversioned.returncode} {unversioned.stderr[-80:]!r}")
    return 0
