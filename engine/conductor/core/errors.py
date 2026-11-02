"""Refusals -- the conductor never guesses: it stops and names what was not met."""


class Refusal(Exception):
    """A named refusal. `code` identifies the contract that failed."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code} — {detail}")
        self.code = code
