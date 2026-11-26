"""Refusals -- the conductor never guesses: it stops and names what was not met. What a refusal
says, and the console's lines of it, are the messages' (`core.messages`)."""

from . import messages


class Refusal(Exception):
    """A named refusal. `code` identifies the contract that failed. `settled` says the run REACHED
    the state the refusal reports -- a run stopped at the repair bound -- so the call that raises it
    keeps what it wrote; a refusal left unsettled reports a state the run never reached, and the
    call writes nothing of the run's state (`execution.advancing`). `armed` says the refusal ended the RE-SERVE of
    a declared compaction: the re-serve wrote nothing, the declaration stands at the slot and the next call
    re-serves -- the console says `messages.ARMED` under it."""

    settled = False
    armed = False

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(messages.refusal_text(code, detail))
        self.code = code
        self.detail = detail


def printed(text: str) -> Refusal | None:
    """-> the refusal a console printed in `text` -- its last refusal line, read back into its
    code and its detail --, None when `text` carries none."""
    for line in reversed(text.splitlines()):
        read = messages.read_refused(line)
        if read is not None:
            return Refusal(*read)
    return None
