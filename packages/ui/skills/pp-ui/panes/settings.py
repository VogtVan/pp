"""settings -- the SETTINGS of the post, in an overlay its footer's key opens: the base the costs are said in --
`usd`, `launches` or `tokens`, the bases `team stats --json` gives each cost in. The base chosen is the one the
summary of a season, its dashboard and the cost column of the Tasks table say; the post keeps it from one opening to
the next (`memory.keep_base`). The overlay is an `Overlay`: `ctrl+enter` gives the base chosen, `escape` gives nothing
-- after a confirmation once the choice moved."""
from __future__ import annotations

from textual.widgets import Static

import palette
from model.teams import COST_BASES
from panes.overlays import Overlay, ParamSelect
from panes.season import BASE_WORDS


class SettingsScreen(Overlay):
    """The settings: the list of the bases of the costs, on the base in force."""

    keys = [palette.SENDS, ("esc", "cancel")]

    def __init__(self, base: str) -> None:
        super().__init__()
        self.base = base if base in COST_BASES else COST_BASES[0]

    def body(self):
        yield Static(palette.strong(palette.SETTINGS), markup=False)
        yield Static(palette.field_title("costs in"), classes="field", markup=False)
        yield ParamSelect([(BASE_WORDS[one], one) for one in COST_BASES], id="field-base", allow_blank=False,
                          value=self.base)
        yield Static("the unit every cost is said in -- in the season's summary, its dashboard and the Tasks table; "
                     "ctrl+enter applies it, and the post keeps it for its next opening", classes="help", markup=False)

    def on_mount(self) -> None:
        super().on_mount()
        self.query_one("#field-base", ParamSelect).focus()

    def action_send(self) -> None:
        self.dismiss(self.query_one("#field-base", ParamSelect).value)
