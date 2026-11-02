"""Scenario `census` -- the CENSUS of the conduction sector (tests/README.md, rule 11): every zone of
`semantics.ZONES` is either carried by a scenario `zones/<zone>.py` or declared `silent:` at the set's
manifest with the batch or the step that owes it; nothing is played here -- the constants of the zone
scenarios (`ZONE`, `ROOTS`) are read on their syntax tree (the channels a zone is crossed on are the data's,
`semantics.ZONES`, never a scenario's):
- (a) the sector in place holds: every zone carried or silent, none both, every silent zone owed, every
  scenario's ZONE in ZONES and equal to its file's name, no CHANNELS constant left in a scenario, every
  root of the manifest played by at least one zone scenario
- (b) on a throwaway copy of the sector, each defect is refused by its name: a zone taken out of `silent:`
  without its scenario (`zone-uncarried`), a scenario of a zone ZONES does not know (`zone-unknown`), a zone
  both silent and carried (`zone-doubled`), a silent zone without the batch that owes it (`silent-unowed`), a
  root of the manifest no scenario plays (`root-unplayed`)
"""
from __future__ import annotations

import ast
import shutil
from pathlib import Path

from tests.harness import support

C = support(__file__, "conduction")


def constants_of(path: Path) -> dict:
    """-> the module-level constants of a zone scenario (ZONE, ROOTS), read on its syntax tree."""
    found = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                found[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                continue
    return found


def defects(sector: Path, zones: dict) -> list[tuple[str, str]]:
    """-> (code, detail) of every defect of a sector: its manifest's `silent:` and `roots:`, its `zones/*.py`."""
    import yaml
    manifest = yaml.safe_load((sector / "roots" / "campaign.yaml").read_text(encoding="utf-8")) or {}
    silent = manifest.get("silent") or {}
    roots = set(manifest.get("roots") or {})
    carried = {}
    found = []
    for path in sorted((sector / "zones").glob("*.py")):
        if path.name.startswith("_"):
            continue
        read = constants_of(path)
        zone = read.get("ZONE")
        if zone not in zones:
            found.append(("zone-unknown", f"{path.name}: ZONE {zone!r} is not in semantics.ZONES"))
            continue
        if zone != path.stem:
            found.append(("zone-misnamed", f"{path.name}: ZONE {zone!r} is not its file's name"))
        if "CHANNELS" in read:
            found.append(("channels-declared", f"{path.name}: a scenario declares no CHANNELS -- the channels a zone "
                                               "exists on are semantics.ZONES's"))
        carried[zone] = tuple(read.get("ROOTS") or ())
    for zone in zones:
        if zone in carried and zone in silent:
            found.append(("zone-doubled", f"`{zone}` is both carried by zones/{zone}.py and declared silent"))
        elif zone not in carried and zone not in silent:
            found.append(("zone-uncarried", f"`{zone}` has no scenario under zones/ and is not declared silent at the manifest"))
    for zone, owed in silent.items():
        if zone not in zones:
            found.append(("zone-unknown", f"silent `{zone}` is not in semantics.ZONES"))
        if not str(owed or "").strip():
            found.append(("silent-unowed", f"silent `{zone}` names no batch or step that owes it"))
    played = {root for roots_ in carried.values() for root in roots_}
    for root in sorted(roots - played):
        found.append(("root-unplayed", f"root `{root}` of the manifest is played by no zone scenario"))
    for root in sorted(played - roots):
        found.append(("root-unknown", f"a zone scenario plays `{root}`, which the manifest does not declare"))
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    zones = dict(C.semantics().ZONES)
    sector = C.SECTOR

    # --- (a) the sector in place ---------------------------------------------------------------------------------
    found = defects(sector, zones)
    carried = sorted(path.stem for path in (sector / "zones").glob("*.py") if not path.name.startswith("_"))
    import yaml
    silent = (yaml.safe_load((sector / "roots" / "campaign.yaml").read_text(encoding="utf-8")) or {}).get("silent") or {}
    if not found and carried and set(carried) | set(silent) == set(zones):
        held("(a) the sector in place", f"{len(zones)} zones: {len(carried)} carried, {len(silent)} silent "
             f"({', '.join(sorted(silent)) or 'none'}); every root of the manifest played")
    else:
        failures.append(f"  ✗ (a) the sector              defects={found} carried={len(carried)} silent={len(silent)}")

    # --- (b) each defect refused by its name, on a throwaway copy --------------------------------------------------
    def copy_of(name: str) -> Path:
        made = bench.temp() / name
        shutil.copytree(sector / "roots", made / "roots", ignore=shutil.ignore_patterns("*.txt", "mounts"))
        shutil.copytree(sector / "zones", made / "zones", ignore=shutil.ignore_patterns("__pycache__"))
        return made

    def with_manifest(made: Path, edit) -> None:
        path = made / "roots" / "campaign.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        edit(data)
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


    # a zone whose roots other scenarios play too: taking its scenario out leaves every root played
    played_by = {}
    for path in (sector / "zones").glob("*.py"):
        if not path.name.startswith("_"):
            read = constants_of(path)
            played_by[path.stem] = set(read.get("ROOTS") or ())
    spare = sorted(zone for zone, roots_ in played_by.items()
                   if all(any(root in others for other, others in played_by.items() if other != zone) for root in roots_))
    gone, muted = spare[0], spare[1]
    uncarried = copy_of("uncarried")
    (uncarried / "zones" / f"{gone}.py").unlink()               # a carried zone whose scenario is gone: uncarried
    unknown = copy_of("unknown")
    (unknown / "zones" / "nowhere.py").write_text('ZONE = "nowhere"\nROOTS = ("read-lines",)\n', encoding="utf-8")
    doubled = copy_of("doubled")
    with_manifest(doubled, lambda data: data.setdefault("silent", {}).__setitem__(carried[0], "a batch"))
    unowed = copy_of("unowed")
    with_manifest(unowed, lambda data: data.setdefault("silent", {}).__setitem__(muted, ""))
    (unowed / "zones" / f"{muted}.py").unlink()                 # silent and owed by nobody
    unplayed = copy_of("unplayed")
    with_manifest(unplayed, lambda data: data["roots"].__setitem__("ghost", {"door": "GHOST.md", "message": "play"}))
    codes = {name: [code for code, _ in defects(made, zones)]
             for name, made in (("uncarried", uncarried), ("unknown", unknown), ("doubled", doubled),
                                ("unowed", unowed), ("unplayed", unplayed))}
    if (codes["uncarried"] == ["zone-uncarried"] and codes["unknown"] == ["zone-unknown"]
            and codes["doubled"] == ["zone-doubled"] and codes["unowed"] == ["silent-unowed"]
            and codes["unplayed"] == ["root-unplayed"]):
        held("(b) each defect refused by its name", f"on throwaway copies: zones/{gone}.py gone: zone-uncarried; "
             f"zones/nowhere.py: zone-unknown; `{carried[0]}` silent too: zone-doubled; `{muted}` silent without its "
             "batch: silent-unowed; a root no scenario plays: root-unplayed")
    else:
        failures.append(f"  ✗ (b) the defects             {codes}")
    return 0
