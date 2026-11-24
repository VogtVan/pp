"""The bench's row of tabs as a loaded or closing post may meet it -- loaded by Python at the start of every process
whose `PYTHONPATH` names this directory, it acts in the post alone (`pp-ui.py` once it runs with Textual):
- `PP_UI_SLOW_TABS` set: the tabbed content takes that many seconds before it handles a `Tabs.TabActivated` of its
  row, as a loaded machine may;
- `PP_UI_CLOSED_ROW` set: the row's message pump is closed once a second tab is added, the row still in place -- a
  callback asked of it is refused (`call_later` answers False).
Nowhere else does it change anything."""
import os
import sys

SLOW = os.environ.get("PP_UI_SLOW_TABS")
CLOSED = os.environ.get("PP_UI_CLOSED_ROW")

if (SLOW or CLOSED) and sys.argv and sys.argv[0].endswith("pp-ui.py"):
    try:
        import asyncio
        from textual.await_complete import AwaitComplete
        from textual.widgets import Tabs, _tabbed_content
    except ImportError:          # the post before it is run again with Textual
        pass
    else:
        if SLOW:
            handled = _tabbed_content.TabbedContent._on_tabs_tab_activated

            async def late(self, event) -> None:
                await asyncio.sleep(float(SLOW))
                handled(self, event)

            _tabbed_content.TabbedContent._on_tabs_tab_activated = late
        if CLOSED:
            added = _tabbed_content.TabbedContent.add_pane

            def add_then_close(self, pane, **where):
                adding = added(self, pane, **where)

                async def closing() -> None:
                    await adding
                    if self.tab_count >= 2:
                        await self.query_children(Tabs).first()._close_messages(wait=False)

                return AwaitComplete(closing())

            _tabbed_content.TabbedContent.add_pane = add_then_close
