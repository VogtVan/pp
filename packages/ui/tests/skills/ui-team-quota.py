"""Scenario `ui-team-quota` -- a member its provider's usage limit stopped, as the Teams tab shows it beside a member
that does not answer (`members[].quota {until, said, at}`, team 1.25.0; batch le-quota-au-poste, s.1571), on the bench's
`pp-team` witness: `core-review` waiting on `suspected`, `lead` stopped until 15:00, `scribe` stopped with no hour
said -- until the house resumes it --, `reviewer` suspected; cut from `ui-team-state` by rule 10:
- the model of a member carries the quota as the face says it, None without
- the table Members draws `lead` and `scribe` with the mark of `reviewer`'s suspicion, their state the palette's QUOTA
  in place of `suspected`, `live` the hour of `until` -- QUOTA_OPEN without one --, `reviewer` its next try
- `d` says the quota, its day and hour or QUOTA_OPEN, and the provider's words
"""
from __future__ import annotations

import importlib.util
import re
import sys
from datetime import datetime

from tests.harness import SOURCE, support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

WIDE = ("--size", "145x34")     # the table of the members whole beside the menu, its column live included
MODEL = SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "model" / "teams.py"


def constant(name: str) -> str | None:
    """-> the palette's constant `name`, None while the palette names none."""
    try:
        return P.palette_constant(name)
    except KeyError:
        return None


QUOTA, QUOTA_OPEN = constant("QUOTA"), constant("QUOTA_OPEN")   # the state of a member a quota stopped; its no-hour


def quotas_read(members: list[dict]) -> dict[str, object]:
    """-> the quota the post's typed state reads of each member (`MemberLine.read(...).quota`), loaded from the
    source; the reading's error by name when the model raises."""
    spec = importlib.util.spec_from_file_location("pp_ui_model_teams", MODEL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # a dataclass reads its module there
    spec.loader.exec_module(module)
    try:
        return {one["member"]: getattr(module.MemberLine.read(one), "quota", "absent") for one in members}
    except Exception as error:                 # noqa: BLE001 -- what the model let out is the finding
        return {"error": f"{type(error).__name__} {error}"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    quoted = T.QUOTED
    script = T.script()
    script["states"]["core-review"] = [quoted]
    house = T.Teams(bench, "ui-team-quota", script)
    lead, reviewer, scribe = quoted["members"]
    suspicion = quoted["waiting_on"][0]
    tried = datetime.fromisoformat(reviewer["health"]["tried_at"])
    until = datetime.fromisoformat(lead["quota"]["until"]).astimezone()

    # --- the model ------------------------------------------------------------------------------------------------
    read = quotas_read(quoted["members"])
    if read == {lead["member"]: lead["quota"], reviewer["member"]: None, scribe["member"]: scribe["quota"]}:
        held("the model reads the quota", f"members[].quota of {lead['member']} and {scribe['member']} as the face "
             f"says it, None for {reviewer['member']}")
    else:
        failures.append(f"  ✗ quota read                  {read}")

    # --- the table Members ----------------------------------------------------------------------------------------
    table = house.render("--render", "teams", *WIDE, "--press", "tab", "--styles")    # the cursor on lead
    plain = P.ANSI.sub("", table.stdout).split("\n")
    cells = {one["member"]: T.cells_by_name(plain, "member", one["member"]) for one in quoted["members"]}
    marks = {one["member"]: T.look_of(table.stdout, one["member"], within=one["path"]) for one in quoted["members"]}
    states = {one["member"]: T.look_of(table.stdout, cells[one["member"]].get("state") or "?", within=one["path"])
              for one in quoted["members"]}
    live = {name: one.get("live") or "" for name, one in cells.items()}
    if (table.returncode == 0 and QUOTA and QUOTA_OPEN
            and [cells[one["member"]].get("state") for one in quoted["members"]] == [QUOTA, suspicion, QUOTA]
            and f"{until:%H:%M}" in live[lead["member"]] and QUOTA_OPEN not in live[lead["member"]]
            and live[scribe["member"]] == QUOTA_OPEN and f"{tried:%H:%M}" in live[reviewer["member"]]
            and marks[reviewer["member"]] is not None and marks[reviewer["member"]][0]
            and marks[lead["member"]] == marks[scribe["member"]] == marks[reviewer["member"]]
            and states[lead["member"]] == states[scribe["member"]] == states[reviewer["member"]] == marks[reviewer["member"]]):
        held("a member stopped by a quota is seen", f"{lead['member']} and {scribe['member']} {QUOTA} in the mark of "
             f"{reviewer['member']}'s {suspicion} {marks[reviewer['member']]}; live {live}")
    else:
        failures.append(f"  ✗ quota in the table          rc={table.returncode} QUOTA={QUOTA!r} QUOTA_OPEN={QUOTA_OPEN!r} "
                        f"{cells} marks={marks} states={states} {plain[:30]!r} {table.stderr[-300:]!r}")

    # --- d --------------------------------------------------------------------------------------------------------
    said = {}
    for one, keys, hour in ((lead, "tab,d", f"{until:%d/%m %H:%M}"), (scribe, "tab,down,down,d", QUOTA_OPEN)):
        done = house.render("--render", "teams", *WIDE, "--press", keys)
        overlay, title = P.overlay_rows(done.stdout), " ".join(P.title_of(done.stdout))
        said[one["member"]] = next((row for row in overlay if QUOTA and re.search(rf"\b{QUOTA}\b", row)
                                    and hour and hour in row and one["quota"]["said"] in row), "")
        if not (done.returncode == 0 and T.in_order(title, quoted["team"], one["member"]) and said[one["member"]]):
            failures.append(f"  ✗ d quota {keys:<19} rc={done.returncode} {title!r} {overlay!r} {done.stderr[-300:]!r}")
    if all(said.values()):
        held("d says the quota", f"{said}")
    return 0
