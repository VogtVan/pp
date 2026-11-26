"""The `stats` domain, layer `model`: what the stats of a team are, held as plain values.

A definition belongs here when it is data about the stats and does nothing: the flags of the verb that shows them, the
units a cost is said in, the width of a slot of time, the events that end a wake-up, the figures a median is taken of,
or a type that carries one of them. Nothing here reads the disk, the clock or the environment.
"""
from __future__ import annotations

# --- the stats of a season ---------------------------------------------------------------------------------

STATS_FLAGS = {"season": True, "all": False, "cost": True, "json": False}
COST_BASES = ("usd", "launches", "tokens")         # the units a cost is said in: `--cost`, `usd` by default
CONCENTRATION = 0.8                                # the share of the cost whose tasks `task_cost.concentration` counts
SLOT = 7200                                        # the width of one slot of `effort_by_slot`, in seconds
DURATIONS = (0, 60, 180, 600, 1800)                # the bands of a launch's duration, in seconds: each from its bound
#                                                    to the next one, the last without an end (`by_duration`)
CONTEXT_BANDS = (0.0, 0.25, 0.5, 0.75, 0.9)        # the bands of the context a launch's end left, a share of the window
#                                                    (`context.by_band`), the last without an end: 90 % renews a run
ENDS = ("wake-ended", "wake-failed", "quota-reached", "wake-killed")   # what ends a wake-up
MEDIAN_OF = (("tasks", "closed"), ("tasks", "stopped"), ("cost", "usd"), ("cost", "launches"), ("cost", "tokens"),
             ("time", "elapsed"), ("time", "active"), ("time", "effort"), ("time", "active_share"),
             ("time", "parallelism"), ("opening", "median"), ("principal", "wait_median"), ("context", "median"),
             ("losses", "failed"),
             ("per_delegation", "usd"), ("per_delegation", "launches"), ("per_delegation", "tokens"),
             ("per_effort_hour", "usd"), ("per_effort_hour", "tokens"), ("context", "p90"))
COMPARED = (("per_delegation", "usd"), ("per_delegation", "launches"), ("per_delegation", "tokens"),
            ("per_effort_hour", "usd"), ("per_effort_hour", "tokens"), ("losses", "failed"),
            ("context", "p90"))                    # the measures a season says `against` the median of the seasons
