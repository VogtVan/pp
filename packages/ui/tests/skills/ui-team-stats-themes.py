"""Scenario `ui-team-stats-themes` -- the local hours and the themes of the dashboard of a season (cut out of
`ui-team-stats-teams` past 22 s, stats-d-equipe/le-detail-des-lancements), on the bench's `pp-team` witness in the
face of the socle, read by the structure of the render, never a text of the post:
- the hours are local (stats-d-equipe/les-trois-ecrans): the same face drawn under `TZ=Asia/Tokyo` and under `TZ=UTC`
  does not say the same start in the head of the dashboard
- the dashboard follows the theme: drawn under `textual-dark` then `textual-light`, the styles of the header of the
  table of the tasks and of the cell of the cost per delegation the witness judges `alert` differ
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "team_stats")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.T.Teams(bench, "ui-team-stats-themes", S.T.script(stats=S.T.STATS))
    house.env["TZ"] = "UTC"

    def render(*keys: str, regions: bool = False):
        return house.render("--render", "teams", *S.SIZE, *(["--press", ",".join(keys)] if keys else []),
                            *(["--regions"] if regions else ["--styles"]))

    # --- the local hours, the themes ------------------------------------------------------------------------------
    S.D.keep_theme(house.made, "textual-dark")
    laid = S.laid(render("z", regions=True).stdout)
    house.env["TZ"] = "Asia/Tokyo"
    tokyo = render("z")
    house.env["TZ"] = "UTC"
    dark = render("z")
    S.D.keep_theme(house.made, "textual-light")
    light = render("z")
    heads = [S.inside(one.stdout, S.framed(one.stdout, "⊟"))[:1] for one in (tokyo, dark)]
    now = S.T.STATS["core-review"]["seasons"][-1]
    ratio = S.judgments().ratio_said(now["against"]["per_delegation"]["usd"]["ratio"])

    def drawn(text: str) -> tuple:
        tasks = laid.get("board-tasks")
        price = laid.get("board-price")
        header = tasks[2] + 1 if tasks else 0
        cell = next((y for y in range(price[2], price[2] + price[4]) if ratio in S.rows(text)[y]), 0) if price else 0
        return S.styles(text, header), S.styles(text, cell) if cell else frozenset()
    looks = [drawn(one.stdout) for one in (dark, light)]
    if (tokyo.returncode == dark.returncode == light.returncode == 0 and all(heads) and heads[0] != heads[1]
            and all(all(one) for one in looks) and looks[0][0] != looks[1][0] and looks[0][1] != looks[1][1]):
        held("the local hours, the themes", f"the head under Tokyo and UTC: {heads[0]} / {heads[1]}; the header and "
             "the alert cell styled otherwise under textual-dark and textual-light")
    else:
        failures.append(f"  ✗ the hours and the themes    {heads} {looks} {laid}")

    return 0
