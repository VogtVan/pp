"""reading -- everything that READS for the agent: the parser's names (core.document's,
addressed here as `reading.<name>` by the engine and the consumers alike), the
serving of a document (tokens: line ranges, two tags, the whole text, each with its hash), its
composition through overlays, and the one reader the facade inherits."""
from ..core.document import (   # noqa: F401 -- the parser's names keep their address
    BORDER, FORMAT_LINE, LAW, SECTIONS, STATEMENT, body_of, chooses, constraint_delta,
    constraint_deltas, constraints, cycles, decides, fields, formats, front_matter, law_lines,
    nexts, playable,
    overlay_serve_lines, procedure, read, serve_lines, serve_sections, statement, title,
    tool_deltas,
    tool_names, truthy,
)
from ..core.tokens import Cut, split_row   # noqa: F401 -- the grammar, at the model
from .tokens import ranged, served, sliced, spanned   # noqa: F401
from .composition import Composing   # noqa: F401
from .serve import Reading   # noqa: F401
