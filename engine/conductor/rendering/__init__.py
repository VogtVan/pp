"""rendering -- the serialization of a Block into the text the agent reads: `render`
writes the block's motif and nothing else does -- `laid` lays one segment out by the
engine's list of sections, `section` writes a titled one; `pieces`, `cut`, `joined`,
`head` and `under` open that same text to the engine's cap (`packages` says the line the
heading carries, `foot` writes the closing and the facts of an output or of a chunk) --
the matter is cut at a seam, the groups of the steps follow its last piece, the output's
heading comes with every chunk. A layer above the data, below the
process: `console -> process -> rendering -> data`."""
from .render import (packages, render, parts, cut, joined, anchor, head, heading, under, renewed, foot,   # noqa: F401
                     last_line, line_of, section, ordered, laid, segment, group, pieces, tail_of, SEAM)
