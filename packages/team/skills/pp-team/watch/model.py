"""The `watch` domain, layer `model`: what watching a team is, held as plain values.

A definition belongs here when it is data about the watch and does nothing: the flags of the verb, how long it waits
before it says it heard nothing, how many activity objects it says per second and how long their text is, the kinds of
activity a flow reports, or a type that carries one of them. Nothing here reads the disk, the clock or the environment.
"""
from __future__ import annotations

WATCH_FLAGS = {"task": True, "json": False, "heartbeat": True, "for": True, "until-done": False}
DEFAULT_HEARTBEAT = 60                           # seconds without a step before watch says so
ACTIVITY_RATE = 4                                # activity objects `watch` says per second and per launch: a reader
                                                 # takes in four lines a second; the surplus is folded into the last
                                                 # one said (`more`), a `context` always passes
ACTIVITY_TEXT = 80                               # characters of a text an activity object carries: a tool's title,
                                                 # a thought, the words -- never the content of a result
ACTIVITY_KINDS = ("tool", "tool-result", "thinking", "words", "context")   # what a flow says of a launch's activity
ACTIVITY_DRAIN = 1.0                             # seconds a reader of a flow keeps draining after its wake-up ended
