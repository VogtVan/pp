"""Scenario `ui-team-form-frame` -- a file form keeps its geometry whatever it shows (batch les-formulaires-jumeaux,
KFJ1), on the bench's `pp-team` witness, `core-review` declaring 200 members:
- at 120x40 and 200x60, the regions the word `boxes` notes in ONE render: the form of a new team (`N`) on its first
  section, then on its next section (`ctrl+pagedown`), the form of `core-review` and its 200 members (`S`), its season
  read only (`s`)
- in every state the box, the zone of the fields and the side pane's file stand, and each stands at the same region in
  all four; the box takes 90 % of the screen, 160 columns at most
- the two forms captured as SVG at each size (the word `svg:`), for the eye -- under `UI_FORM_CAPTURES` when it names a
  directory, the pass's own otherwise: each file an SVG
- each section shows the side pane its table says (batch les-volets-par-onglet), on the whole height of the fields'
  zone: `E` -- Team, Preset and Limits the file, Members the view by member, Documents the holes over the text,
  Owner's word the words --, `S` -- Preset and Launch the file, Documents the holes over the text, Members the view,
  Season's word the words --; no other zone of the side pane shown
"""
from __future__ import annotations

import os
from pathlib import Path

from tests.harness import support

T = support(__file__, "teams")
F = support(__file__, "team_forms")    # the templates of team 1.26.0

SIZES = ((120, 40), (200, 60))
LONG = 200
ZONES = ("box", "form-fields", "form-file")     # what never moves from one state to the next
STATES = ("N", "N then ctrl+pagedown", f"S on {LONG} members", "s, read only")
KEYS = "N,boxes,svg:{team},ctrl+pagedown,boxes,escape,S,boxes,svg:{season},escape,s,boxes"
WALK = lambda form, tabs: ",".join([form, "boxes"] + ["ctrl+pagedown,boxes"] * (len(tabs) - 1))
TABS = f"{WALK('E', F.TEAM_TABS)},escape,{WALK('S', F.SEASON_TABS)}"     # every section of both forms, each noted
SIDE = tuple(zone for zones in F.PANES.values() for zone in zones)


def _boxes(text: str) -> list[dict[str, tuple[int, ...]]]:
    """-> the regions of each noting, `{id: (x, y, w, h)}`, from the closing line `boxes …`."""
    line = next((one for one in text.splitlines() if one.startswith("boxes ")), "")
    found = []
    for noted in line[len("boxes "):].split(" | ") if line else []:
        regions = {}
        for one in noted.split(";"):
            name, _, where = one.partition("=")
            if where:
                regions[name] = tuple(int(each) for each in where.split(","))
        found.append(regions)
    return found


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    members = [(f"m{n:03}", f"agents/m{n:03}") for n in range(LONG)]
    many = {**T.DECLARATIONS, "core-review": {**T.DECLARATIONS["core-review"], "declared": {
        **T.DECLARATIONS["core-review"]["declared"],
        "agents": [{**T.DECLARATIONS["core-review"]["declared"]["agents"][0], "member": name, "path": path}
                   for name, path in members]}}}
    house = T.Teams(bench, "ui-team-form-frame", T.script(declarations=many, templates=F.TEMPLATES))
    captures = Path(os.environ.get("UI_FORM_CAPTURES") or bench.temp())
    captures.mkdir(parents=True, exist_ok=True)
    made = []
    for width, height in SIZES:
        files = {form: captures / f"{form}-form-{width}x{height}.svg" for form in ("team", "season")}
        done = house.render("--render", "teams", "--size", f"{width}x{height}", "--press", KEYS.format(**files))
        made += list(files.values())
        noted = _boxes(done.stdout)
        missing = [f"{state}: {', '.join(one for one in ZONES if one not in regions)}"
                   for state, regions in zip(STATES, noted) if any(one not in regions for one in ZONES)]
        moved = [f"{one}: {sorted({regions.get(one) for regions in noted}, key=str)}" for one in ZONES
                 if len({regions.get(one) for regions in noted}) > 1]
        box = noted[0].get("box") if noted else None
        sized = box is not None and abs(box[3] - height * 0.9) <= 1 and box[2] == min(160, round(width * 0.9))
        if done.returncode == 0 and len(noted) == len(STATES) and not missing and not moved and sized:
            held(f"the form at {width}x{height}: one geometry in {len(STATES)} states",
                 "; ".join(f"{one} {noted[0][one]}" for one in ZONES))
        else:
            failures.append(f"  ✗ form at {width}x{height}       rc={done.returncode} {len(noted)} noting(s); "
                            f"missing {missing}; moved {moved}; box {box} sized={sized} {done.stderr[-300:]!r}")
    # --- each section, its side pane on the whole height ---------------------------------------------------------------
    walked = _boxes(house.render("--render", "teams", *F.SIZE, "--press", TABS).stdout)
    wanted = [(f"E {tab}", pane) for tab, pane in zip(F.TEAM_TABS, F.TEAM_PANES)] + \
             [(f"S {tab}", pane) for tab, pane in zip(F.SEASON_TABS, F.SEASON_PANES)]
    wrong = []
    for (tab, pane), regions in zip(wanted, walked):
        shown = [zone for zone in SIDE if zone in regions]
        fields = regions.get("form-fields", (0, 0, 0, 0))
        zones = [regions[zone] for zone in F.PANES[pane] if zone in regions]
        whole = (len(zones) == len(F.PANES[pane]) and zones[0][1] == fields[1]
                 and zones[-1][1] + zones[-1][3] == fields[1] + fields[3])
        if shown != list(F.PANES[pane]) or not whole:
            wrong.append(f"{tab}: {pane} wanted, {shown} shown {zones} beside {fields}")
    if len(walked) == len(wanted) and not wrong:
        held("each section shows its side pane, whole height", "; ".join(f"{tab} {pane}" for tab, pane in wanted))
    else:
        failures.append(f"  ✗ side pane by section        {len(walked)}/{len(wanted)} noted; {wrong}")
    svg = [one for one in made if one.is_file() and one.read_text(encoding="utf-8").lstrip().startswith("<svg")]
    if len(svg) == len(made) == 4:
        held("the two forms captured at each size", ", ".join(str(one) for one in svg))
    else:
        failures.append(f"  ✗ captures                    {[str(one) for one in made]} {[str(one) for one in svg]}")
    return 0
