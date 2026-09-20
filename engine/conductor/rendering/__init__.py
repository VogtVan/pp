"""rendering -- the serialization of a Block into the text the agent reads: `render`
writes the block's motif and nothing else does; `parts`, `cut`, `joined`, `head` and
`under` open that same text to the engine's cap (`packages` says the line the heading
carries) -- the matter is cut at a seam, the
output's heading and the tail come with every chunk. A layer above the data, below the
process: `console -> process -> rendering -> data`."""
from .render import packages, render, parts, cut, joined, anchor, head, under   # noqa: F401
