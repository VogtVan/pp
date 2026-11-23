"""fields -- the fields the post types in, shared by its panes and its overlays: `MessageArea`, a text on several
lines -- the message line of a conversation, and the text of a gesture's overlay --, and `FormArea`, a text on several
lines of a file form. In every text `enter` goes to the line; `ctrl+enter` sends (`SEND_KEYS`)."""
from __future__ import annotations

from textual import events
from textual.message import Message
from textual.widgets import TextArea

SEND_KEYS = ("ctrl+enter", "ctrl+j")    # the key that sends: a terminal tells `ctrl+enter` as itself or as `ctrl+j`


class MessageArea(TextArea):
    """A text on several lines -- the message line of a conversation, the text of a gesture: one row at rest,
    growing with its text up to 8 rows, then scrolled. `enter` goes to the line, as in any `TextArea`; `ctrl+enter`
    sends the whole text, its line breaks kept (`Submitted`) -- taken by the line itself as it comes, so that a key
    typed right after it (`ctrl+right`) never moves the text sent. In an overlay the overlay's own `ctrl+enter`
    comes first: it sends the overlay whole."""

    DEFAULT_CSS = """
    MessageArea { height: auto; max-height: 10; }
    """

    class Submitted(Message):
        """`ctrl+enter` in the line: its whole text."""

        def __init__(self, area: "MessageArea", text: str) -> None:
            super().__init__()
            self.area, self.text = area, text

    async def _on_key(self, event: events.Key) -> None:
        if event.key in SEND_KEYS:
            event.stop()
            event.prevent_default()
            self.post_message(self.Submitted(self, self.text))
            return
        await super()._on_key(event)


class FormArea(MessageArea):
    """A text on several lines of a file form -- a team's, a season's: `enter` goes to the line, `tab` leaves the
    text, `ctrl+enter` writes the form."""
