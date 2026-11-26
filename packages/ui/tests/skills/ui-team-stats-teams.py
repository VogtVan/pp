"""Scenario `ui-team-stats-teams` -- the dashboard of the seasons as the team chosen changes (cut out of
`ui-team-stats`, batch le-tableau-de-bord-range, s.1919), on the bench's `pp-team` witness answering
`team stats --json [--all]`, read by the structure of the render, never a text of the post:
- the base of the costs chosen in the settings (`SETTINGS_KEY`, its list unrolled, the next base chosen and sent;
  batch la-base-de-cout-en-reglages, s.1921) is kept in the post's memory (`base` in the space `ui` of the metadata):
  the next opening draws the summary's title as the opening that chose it did
- `down` in the menu, the dashboard open, draws the dashboard of the next team, its name in the title; `escape` then
  closes it, and `⊟` closes it too: the four bands of the centre back
- two teams chosen one after the other while the stats of the first are read (the witness tarries): the team chosen
  last drawn alone, `veille` never started -- no number in its title, one row in its summary
(the local hours and the themes: `ui-team-stats-themes`, cut out of this scenario past 22 s)
"""
from __future__ import annotations

import re

from conductor import metadata
from tests.harness import support

S = support(__file__, "team_stats")
K = support(__file__, "tasks")          # the footer's key of the settings


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.T.Teams(bench, "ui-team-stats-teams", S.T.script(stats=S.T.STATS))
    house.env["TZ"] = "UTC"

    def render(*keys: str, regions: bool = False):
        return house.render("--render", "teams", *S.SIZE, *(["--press", ",".join(keys)] if keys else []),
                            *(["--regions"] if regions else ["--styles"]))

    # --- the base chosen in the settings, kept for the next opening ------------------------------------------------
    kept = render(K.SETTINGS_KEY, "down", "down", "enter", "ctrl+enter")
    plain = render()
    summary = S.framed(plain.stdout, "⊞")
    expand = S.offset(plain.stdout, summary, "⊞")
    remembered = str(metadata.of_package(house.made, "ui").get("base") or "")
    if plain.returncode != 0 or expand is None:
        failures.append(f"  ✗ the glyph of the summary    rc={plain.returncode} {S.rows(plain.stdout)[:8]} "
                        f"{plain.stderr[-300:]!r}")
        return 0
    if (kept.returncode == 0 and remembered == "launches"
            and S.title(kept.stdout, S.framed(kept.stdout, "⊞")) == S.title(plain.stdout, summary)):
        held("the base kept for the next opening", f"{K.SETTINGS_KEY}, the next base chosen: {remembered!r} in the "
             "memory; the next opening draws the summary's title as the one that chose it")
    else:
        failures.append(f"  ✗ the base kept               rc={kept.returncode} kept={remembered!r} "
                        f"{S.title(kept.stdout, S.framed(kept.stdout, '⊞'))!r} / {S.title(plain.stdout, summary)!r} "
                        f"{kept.stderr[-300:]!r}")
    opening = f"click:#teams-stats:{expand}:0"

    # --- another team chosen, then escape; ⊟ ---------------------------------------------------------------------
    other = S.T.BADGES[1]["team"]
    moved = render(opening, "down")
    shown = S.framed(moved.stdout, "⊟")
    closed = render(opening, "down", "escape", regions=True)
    folded = render(opening, "down", f"click:#teams-board:{S.offset(moved.stdout, shown, '⊟')}:0", regions=True)
    backs = [[one[0] for one in S.regions(done.stdout).get("band", [])] for done in (closed, folded)]
    if (moved.returncode == 0 and shown and re.search(rf"\b{re.escape(other)}\b", S.title(moved.stdout, shown))
            and all(S.within(one, shown) or one in (shown, S.framed(moved.stdout, "Teams")) for one in S.frames(moved.stdout))
            and all(len(one) == 4 and "teams-board" not in one and "teams-top" in one for one in backs)):
        held("another team, escape, ⊟", f"down: the dashboard titled {other}; escape and ⊟: the bands {backs[0]} back")
    else:
        failures.append(f"  ✗ team, escape, ⊟             {S.title(moved.stdout, shown)!r} {backs}")

    # --- two teams chosen while the first one's stats are read -----------------------------------------------------
    house.use(S.T.script(stats={**S.T.STATS, S.T.BADGES[1]["team"]: {**S.T.STATS["core-review"], "sleep": 1.5}}))
    raced = render("burst:down:down")
    last = S.framed(raced.stdout, "⊞")
    named = S.beside(raced.stdout, last)
    if (raced.returncode == 0 and last and named and S.T.BADGES[2]["team"] in S.title(raced.stdout, named)
            and not re.search(r"\d", S.title(raced.stdout, named))
            and len([one for one in S.inside(raced.stdout, last) if one]) == 1):
        held("a team chosen during a reading of stats", f"down twice while {other}'s stats tarry: "
             f"{S.T.BADGES[2]['team']} drawn alone, no number in its title, one row in its summary")
    else:
        failures.append(f"  ✗ the race                    {S.title(raced.stdout, named)!r} "
                        f"{S.inside(raced.stdout, last)} {S.rows(raced.stdout)[3:12]}")
    return 0
