"""The `status` domain, layer `model`: what the status of the teams is, held as plain values.

A definition belongs here when it is data about the status and the roster and does nothing: the flags of their verbs, or
a type that carries one of them. Nothing here reads the disk, the clock or the environment.
"""
from __future__ import annotations

ROSTER_FLAGS = {"json": False}
STATUS_FLAGS = {"json": False}
