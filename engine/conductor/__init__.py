"""The conductor: it holds the procedure, the stack and the initiative; the agent infers.

The ONE public face of the engine (plan pp_core, phase la-decoupe-du-moteur): a
consumer -- the console, a package's script, an adapter, the bench -- imports
`conductor` and nothing else. The classes, VERSION and the modules named here are
the API; what a sub-package holds behind them may move without a consumer noticing.

Importing the face brings the engine with it, PyYAML included, and that is the
contract (operator word, 2026-08-31): a skill is played BY the conductor, with the
interpreter that runs pp, so what the engine depends on the skill may depend on.
No consumer is exempt.
"""
from .core.errors import Refusal
from .core.version import VERSION
from .core.model import (Block, Document, Siblings, Frame, Instruction, Member, Procedure,
                         Stack, Tool, console_command)
from .execution import Conductor, revive
from .rendering import render
from .core import navigation, sections
from .state import cadences, context, discovery, instance, metadata, metrics, persistence, record, settings
from . import reading, rendering
from .packaging import compiling, contributions, events, install, topology

__all__ = ["VERSION", "Block", "Conductor", "Document", "Siblings", "Frame", "Instruction",
           "Member", "Procedure", "Refusal", "Stack", "Tool", "console_command", "revive", "render",
           "cadences", "compiling", "context", "contributions", "discovery", "events", "install",
           "instance", "metadata", "metrics", "navigation", "persistence", "reading", "record", "rendering",
           "sections", "settings", "topology"]
