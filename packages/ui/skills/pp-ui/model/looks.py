"""model.looks -- the table of the JUDGMENTS: the one place where a measure of a team's stats gets a sense and a
threshold. A judgment is a CODE -- `good`, `nominal`, `watch`, `alert`, and `muted` for what is not judged -- drawn
from a measure's ratio to the median of the seasons and its sense, or from a share and its fixed thresholds; the
vocabulary of the drawing (`palette.py`) gives each code its look and knows no measure, the bench loads this module
from the source. Pure: no I/O, no clock, no Textual, no import from any other module of the post.

A measure is named by its path in the face of `team stats --json` (`per_delegation.usd`). Going UP is the wrong side
of every measure that has a sense here: what it costs, the launches it takes, the failures. The cost of a launch is
said without judgment -- a launch that lasts longer costs more without the work being dearer --, and the volumes, the
root's share, the active share and the parallelism have no sense: `nominal`. Three measures are SHARES judged without
a median, on thresholds of their own: the share of the stopped tasks, the context's p90, the share of the budget.
"""
from __future__ import annotations

GOOD, NOMINAL, WATCH, ALERT, MUTED = "good", "nominal", "watch", "alert", "muted"
CODES = (GOOD, NOMINAL, WATCH, ALERT, MUTED)

UP_BAD = "up-bad"                    # the sense of a measure whose going up is the wrong side

SENSE: dict[str, str | None] = {
    "per_delegation.usd": UP_BAD, "per_delegation.launches": UP_BAD, "per_delegation.tokens": UP_BAD,
    "per_effort_hour.usd": UP_BAD, "per_effort_hour.tokens": UP_BAD, "losses.failed": UP_BAD,
    "per_launch.usd": None, "per_launch.tokens": None, "delegations": None, "tasks.closed": None,
    "root.share": None, "time.active_share": None, "time.parallelism": None,
}

RATIO_GOOD = 0.8                     # at or under: the good side of the median
RATIO_WATCH = 1.25                   # from there: the wrong side, to watch
RATIO_ALERT = 1.5                    # from there: the wrong side, an alert
SEASONS_MIN = 3                      # under so many seasons played the median is said, the code stays `nominal`

# a share's thresholds: `watch` from its first (PAST it when `past`), `alert` from its second
SHARES: dict[str, dict] = {
    "stopped_tasks.share": {"watch": 0.10, "alert": 0.25, "past": False},
    "context.p90": {"watch": 0.70, "alert": 0.85, "past": False},
    "budget.share": {"watch": 0.80, "alert": 1.0, "past": True},
}

UP, DOWN, LEVEL = "▲", "▼", "="      # the glyph that says a ratio without colour
MARKS = {WATCH: "!", ALERT: "!!"}    # the mark that says a share's code without colour


def judged(measure: str, ratio: float | None, over: int | None) -> str:
    """-> the code of a measure compared to the median of `over` seasons, `ratio` the measure divided by it:
    `nominal` for a measure without a sense, without a ratio (no median, or a median of 0) or under `SEASONS_MIN`
    seasons; else `good` at or under `RATIO_GOOD`, `alert` from `RATIO_ALERT`, `watch` from `RATIO_WATCH`."""
    if SENSE.get(measure) != UP_BAD or ratio is None or (over or 0) < SEASONS_MIN:
        return NOMINAL
    if ratio >= RATIO_ALERT:
        return ALERT
    if ratio >= RATIO_WATCH:
        return WATCH
    return GOOD if ratio <= RATIO_GOOD else NOMINAL


def shared(measure: str, share: float | None) -> str:
    """-> the code of a share on its thresholds (`SHARES`): `muted` without a share, `alert` from its second,
    `watch` from its first -- past it when the table says `past` --, else `nominal`; `nominal` for a share the table
    has no thresholds for."""
    if share is None:
        return MUTED
    bounds = SHARES.get(measure)
    if bounds is None:
        return NOMINAL
    if share >= bounds["alert"]:
        return ALERT
    watch = share > bounds["watch"] if bounds["past"] else share >= bounds["watch"]
    return WATCH if watch else NOMINAL


def ratio_said(ratio: float | None) -> str:
    """-> a ratio said without colour: `▲ ×1.46` above 1, `▼ ×0.55` under, `= ×1.00` at it; empty without one."""
    if ratio is None:
        return ""
    value = round(ratio, 2)
    glyph = UP if value > 1 else DOWN if value < 1 else LEVEL
    return f"{glyph} ×{value:.2f}"


def mark_of(code: str) -> str:
    """-> what says a code without colour where no ratio says it (a share): `!` to watch, `!!` an alert, else
    nothing."""
    return MARKS.get(code, "")
