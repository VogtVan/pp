"""Scenario `ui-team-season-prefilled` -- `S` on a team never started whose SEASON.md writes its first season opens the
form PREFILLED from the declaration alone, on the bench's witnesses: `veille`, never started -- its declaration (`team
declaration --json`: `scout`, its root, and `writer`, their agents born, and `scribe`, its agent not born; the season
SEASON.md writes -- `all`'s launch, `writer`'s own model --; TEAM.md's lines of documents, one of a role):
- the line `all` prefilled from the season written, `writer` the model SEASON.md gives it, `·` elsewhere; no agent's
  `status` asked -- the form reads the declaration, never what an agent last played
- what each member reads at the next start said in the view by member, as `declared.views` says it: each member, its
  role keys, each document and its effect
- `enter` on the form left as it is (in Values: on Documents, `enter` gives a document its roles) plays nothing and
  says why on the line of state
- `ctrl+s` on the form left as it is declares the season's context, empty in SEASON.md, at the form's default
  (`team declare veille --season --context 90`), then plays `team start veille` without a flag: no `--message`
- a member not born opens its profile on the packages the declaration gives it, in their order; `plan` switched on
  on that member composes `--member scribe --package plan=on` on the declare, its change of `all`'s set alone, then
  the same start
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source
F = support(__file__, "team_forms")    # the readers of a form by its zones

SEP = P.palette_constant("SEP")
WRITTEN = T.season_written({"provider": T.D.PROVIDER, "model": "opus", "effort": "high"}, None,
                           {"writer": {"model": "sonnet"}})
DOCUMENTS = (("all", ["git/trunk"]), ("shape", ["git/branches"]))     # TEAM.md's lines: one for all, one for a role
READS = {"scout": ["TEAM-veille-trunk.md", "roles/TEAM-veille-branches.md"], "writer": ["TEAM-veille-trunk.md"],
         "scribe": ["TEAM-veille-trunk.md"]}           # what `declared.views` says each member reads
VIEWS = [{"member": member, "roles": ["shape"] if member == "scout" else [],
          "documents": [T.document(one, "mounted" if one.startswith("roles/") else "served") for one in documents]}
         for member, documents in READS.items()]
VEILLE = T.declaration("veille", [("scout", "agents/scout"), ("writer", "agents/writer"),
                                  ("scribe", "agents/scribe", False)], {"budget": 3.0}, started=False,
                       roles=(("shape", ["scout"]),), season=WRITTEN, documents=DOCUMENTS, views=VIEWS)
DECLARED = "team declare veille --season --context 90"       # the context at the form's default, then what changed
BARE = [f"{DECLARED} --json", "team start veille --no-tick"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-prefilled", T.script(declarations={**T.DECLARATIONS, "veille": VEILLE}),
                    agents=T.SEASON_AGENTS)

    # --- the season written, the views, enter on a form left as it is ------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"down,down,S,{F.TO_LAUNCH},ctrl+enter,{F.section(1)},boxes")
    lines = T.season_rows(shown.stdout, VEILLE)
    rows = T.form_rows(shown.stdout)
    view, state = F.zone_rows(shown.stdout, "form-view"), F.state(shown.stdout)
    launch = WRITTEN["launch"]
    carried = [launch["provider"], launch["model"], launch["effort"]]
    paths = [one["path"] for one in VEILLE["declared"]["agents"]]
    asked = [one for one in house.chat_lines() if one.split()[:2] in (["status", path] for path in paths)]
    if (shown.returncode == 0 and len(lines) == 4 and lines[0][2:5] == carried and lines[2][3:4] == ["sonnet"]
            and set(lines[1][2:]) == {P.palette_constant("AS_ALL")} and asked == [] and "./pp" not in shown.stdout):
        held("the season written prefills the lines", f"all {carried}; writer {lines[2][3]}; no agent asked")
    else:
        failures.append(f"  ✗ season written              rc={shown.returncode} {lines} {asked} {rows!r} "
                        f"{shown.stderr[-400:]!r}")
    said = F.by_member(view, list(READS))
    if all(said[member] and all(one in said[member] for one in documents) for member, documents in READS.items()):
        held("what each member reads is said", f"{said}")
    else:
        failures.append(f"  ✗ views                       {said} {view!r}")
    if state and house.gestures() == []:
        held("enter on a form left as it is plays nothing", state)
    else:
        failures.append(f"  ✗ nothing changed             {state!r} {house.gestures()}")

    # --- ctrl+s on a form left as it is ------------------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", "down,down,S,ctrl+s")
    if done.returncode == 0 and house.gestures() == BARE:
        held("a form left as it is starts the season written", " ; ".join(BARE))
    else:
        failures.append(f"  ✗ left as it is               rc={done.returncode} {house.gestures()} {done.stdout[-1500:]!r}")

    # --- a member not born: its packages, one switched -------------------------------------------------------------
    profile = f"down,down,S,{T.TO_LINES},down,down,down,enter"
    shown = house.render("--render", "teams", *T.SEASON_SMALL, "--press", profile)
    top = P.on_top(shown.stdout)
    title = P.title_of(top) or [""]
    names = [one["name"] for one in VEILLE["declared"]["agents"][2]["packages"]]
    row = next((one for one in P.overlay_rows(top) if T.in_order(one, *names)), "")
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press",
                        f"{profile},{T.TO_PACKAGES},enter,space,ctrl+enter,ctrl+enter,ctrl+s")
    wanted = [f"{DECLARED} --member scribe --package plan=on --json", BARE[1]]
    if (shown.returncode == 0 and "scribe" in title[0].split() and row and len(row.split(SEP)) == len(names)
            and done.returncode == 0 and house.gestures() == wanted):
        held("a member not born has its packages", f"{row!r}; {' ; '.join(wanted)}")
    else:
        failures.append(f"  ✗ not born                    rc={shown.returncode},{done.returncode} {title} {row!r} "
                        f"{house.gestures()} {top[-1500:]!r} {done.stderr[-300:]!r}")
    return 0
