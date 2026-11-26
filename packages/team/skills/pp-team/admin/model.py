"""The `admin` domain, layer `model`: what deleting or renaming a team needs, held as plain values.

A definition belongs here when it is data about those verbs and does nothing: their flags, the files an earlier version
laid in an agent's instance, or a type that carries one of them. Nothing here reads the disk, the clock or the
environment.
"""
from __future__ import annotations

from documents.model import IDLE

DELETE_FLAGS = {"yes": False, "json": False}     # `--agent <path>`, repeatable, is taken out before (`agents_asked`)
RENAME_FLAGS = {"json": False}
RETIRED = {("procs", "TURN.md"): "retired/agent-turn-0.32.txt",   # what an earlier version laid at an agent -> the
           ("procs", IDLE): "agent-idle.md",       # bytes it laid, beside the entry or under `retired/`
           ("skills", "team-entry", "SKILL.md"): "retired/agent-entry.md",
           ("skills", "team-entry", "team-entry.py"): "retired/agent-entry.py"}
