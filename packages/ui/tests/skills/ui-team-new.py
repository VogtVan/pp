"""Scenario `ui-team-new` -- `N` opens the form of TEAM.md empty, its presets read from `team templates --json`, and
plays `team declare` as it shows it, on the bench's `pp-team` witness (`_team_new`):
- `N` on the Teams tab opens the form read once from `templates --json`: the preset on the first preset of a team the
  verb says -- its members' names in the side pane's TEAM.md --; the list of presets offers no empty entry for a team
  to be born, `E` on a team that stands offers it (taken from `ui-team-new-sorts`)
- the help under `schedule` says the grammar by its examples -- `10s`, `2m`, `1h`
- what cannot play plays nothing and says why on the line of state: no name; a member without its path; the name of a
  team that stands (`core-review`: `E` changes it) -- a reason of its own each, never a command
Its sibling: `ui-team-new-start` (the fields of each section, what `enter` plays, its refusal, the first preset).
"""
from __future__ import annotations

from tests.harness import support

N = support(__file__, "team_new")
F, T, P = N.F, N.T, N.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new")

    # --- N, enter: the form on the first preset, nothing to play without a name; the lists of presets -----------
    house.clear_journal()
    nameless = house.render("--render", "teams", *N.SIZE, "--press", f"N,ctrl+enter,{N.TO_LIMITS},boxes")
    file = F.zone_rows(nameless.stdout, "form-file")
    reads = [one for one in house.journal_lines() if one.startswith("templates --json")]    # the documents' texts
    #                                                    rendered on Documents on the way (`templates --render`) apart
    schedule_help = N.help_under(F.fields(nameless.stdout), "schedule")
    if (nameless.returncode == 0 and f"template: {N.FIRST['template']}" in file
            and all(one in file for one in N.FIRST["members"]) and reads == ["templates --json"]):
        held("N opens the form on the first preset", f"{N.FIRST['template']}, its members {N.FIRST['members']} in "
             f"TEAM.md; {reads}")
    else:
        failures.append(f"  ✗ form                        rc={nameless.returncode} {reads} {file} "
                        f"{nameless.stderr[-400:]!r}")
    if nameless.returncode == 0 and all(one in schedule_help.split() for one in ("`10s`,", "`2m`,", "`1h`")):
        held("the help of schedule says its grammar", schedule_help[:100])
    else:
        failures.append(f"  ✗ schedule help               {schedule_help!r} {F.fields(nameless.stdout)!r}")
    blank = P.palette_constant("PRESET_BLANK")
    offered = house.render("--render", "teams", *N.SIZE, "--press", f"N,{N.TO_PRESET},space,boxes")
    edited = house.render("--render", "teams", *N.SIZE, "--press", f"E,{N.TO_PRESET},space,boxes")
    listed = lambda done: [one.strip(" ▼▊▎").split(" -- ")[0].strip() for one in F.fields(done.stdout)
                           if one.startswith("▊")]                                  # the rows of the list unrolled
    born, standing_list = listed(offered), listed(edited)
    if (offered.returncode == 0 and edited.returncode == 0 and N.FIRST["template"] in born and blank not in born
            and blank in standing_list and N.FIRST["template"] in standing_list):
        held("the presets: no empty entry for a team born, one for a team that stands",
             f"N: {N.FIRST['template']} …, no {blank!r}; E: {blank!r} offered")
    else:
        failures.append(f"  ✗ preset lists                {born!r} {standing_list!r}")

    # --- what cannot play: nothing played, a reason of its own on the line of state ----------------------------
    # the members' text typed, `tab` leaves it for the root -- `enter` in a text goes to the line (s.1647) -- then writes
    pathless = house.render("--render", "teams", *N.SIZE, "--press",
                            N.keys("N,x", N.TO_MEMBERS, "end," + N.typed(" agents/s"), "tab,ctrl+enter,boxes"))
    standing = house.render("--render", "teams", *N.SIZE, "--press", "N," + N.typed("core-review") + ",ctrl+enter,boxes")
    renders = (nameless, pathless, standing)
    gaps = [F.state(one.stdout) for one in renders]
    if (all(one.returncode == 0 for one in renders) and house.gestures() == [] and all(gaps)
            and len(set(gaps)) == 3 and "core-review" in gaps[2].split()
            and not any("./pp" in one.stdout for one in renders)):
        held("what cannot play plays nothing and says why", "no name, a member without its path, a team that stands: "
             "no command, a reason of its own each on the line of state; nothing in the witness's journal")
    else:
        failures.append(f"  ✗ nothing played              {house.gestures()} {gaps}")

    return 0
