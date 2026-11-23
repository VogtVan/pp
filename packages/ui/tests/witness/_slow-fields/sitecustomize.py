"""The bench's form whose fields come late, as a loaded post may make them -- loaded by Python at the start of every
process whose `PYTHONPATH` names this directory, it acts in the post alone (`pp-ui.py` once it runs with Textual):
- `PP_UI_SLOW_FIELDS` set: a box of values (`ValueFields`) that makes its fields anew takes that many seconds before
  it mounts them; its first fields, those the form opens on, come at once.
- `PP_UI_SLOW_CHOICE` set: a list (`Select`) whose choice changed carries its new value at once and tells it
  (`Select.Changed`) that many seconds late -- the form hears of the choice after the list shows it.
Nowhere else does it change anything."""
import os
import sys

SLOW = os.environ.get("PP_UI_SLOW_FIELDS")
CHOICE = os.environ.get("PP_UI_SLOW_CHOICE")

if (SLOW or CHOICE) and sys.argv and sys.argv[0].endswith("pp-ui.py"):
    try:
        import asyncio
        from textual.await_complete import AwaitComplete
        from textual.widget import Widget
        from textual.widgets import Select
    except ImportError:          # the post before it is run again with Textual
        pass
    else:
        mounted = Widget.mount
        posted = Select.post_message
        opened = set()           # the boxes of values whose first fields are mounted

        def mount_late(self, *widgets, **where):
            if type(self).__name__ != "ValueFields":
                return mounted(self, *widgets, **where)
            if id(self) not in opened:
                opened.add(id(self))
                return mounted(self, *widgets, **where)

            async def later() -> None:
                await asyncio.sleep(float(SLOW))
                await mounted(self, *widgets, **where)

            return AwaitComplete(later())

        def post_late(self, message):
            if not isinstance(message, Select.Changed):
                return posted(self, message)
            asyncio.get_running_loop().call_later(float(CHOICE), posted, self, message)
            return True

        if SLOW:
            Widget.mount = mount_late
        if CHOICE:
            Select.post_message = post_late
