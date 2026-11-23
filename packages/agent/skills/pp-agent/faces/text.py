"""A text as stdout prints it: what an agent said, harmless to the house's bus."""
from __future__ import annotations


def harmless(text: str) -> str:
    """-> a text an agent or a message carried, as stdout may print it: each line opening on
    `::`, blanks before it included, prefixed with a backslash -- the console reads such a line
    as a directive of the house's bus, and an agent's words never give pp an order."""
    return "\n".join("\\" + one if one.lstrip().startswith("::") else one for one in text.split("\n"))
