"""fields -- the fields the post types in, shared by its panes and its overlays: `MessageArea`, a text on several
lines -- the message line of a conversation, and the text of a gesture's overlay."""
from __future__ import annotations

from textual import events
from textual.message import Message
from textual.widgets import TextArea


class MessageArea(TextArea):
    """A text on several lines -- the message line of a conversation, the text of a gesture: one row at rest,
    growing with its text up to 8 rows, then scrolled. `enter` sends the whole text, its line breaks kept (`Submitted`);
    `shift+enter` goes to the line -- `alt+enter` and `ctrl+j` too, for a terminal that tells no
    `shift+enter` from `enter`."""

    NEW_LINE = ("shift+enter", "alt+enter", "ctrl+j")
    DEFAULT_CSS = """
    MessageArea { height: auto; max-height: 10; }
    """

    class Submitted(Message):
        """`enter` in the line: its whole text."""

        def __init__(self, area: "MessageArea", text: str) -> None:
            super().__init__()
            self.area, self.text = area, text

    async def _on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            event.stop()
            event.prevent_default()                  # no line break: the text leaves
            self.post_message(self.Submitted(self, self.text))
        elif event.key in self.NEW_LINE:
            event.stop()
            event.prevent_default()
            start, end = self.selection
            self._replace_via_keyboard("\n", start, end)
