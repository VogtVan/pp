"""agents -- the AGENTS tab: the table of the agents of the house, read from the faces of
`agent` on the app's loop (never polled: at the start, on `u`, after each verdict a
conversation receives), and over it the overlay of one agent's runs -- where a run is
resumed with its history, measured (`agent stats`), purged (`agent purge`), or a new conversation
opened through the overlay of its parameters, prefilled with what the agent last played, its name
among them. A run is named in its parameters: at its opening, or `p` on its tab. Each run, and each
agent, says its WEIGHT -- what a purge would remove, as `status --json` and `list --json` say it.

A purge is shown before it plays: the verb is played WITHOUT `--yes`, what it says it would remove is
shown with the exact `--yes` command, and that command plays only once the run's key -- or the date --
is typed as it is; a clone with unsent commits gets `--force` offered under a second typing. Every
refusal of the verb goes to the remedy line as it said it; the post adds no guard of its own. `a` gives birth to an agent (`agent add`, its exact command shown first). The tab
opens nothing itself: it says `OpenAsked`, and the app opens the conversation on its loop and
shows it in the dialogue.

A run a MEMBER of a team holds is marked `<team>/<member>` in the overlay of the runs: as the overlay
opens, `team status --json` gives the teams, and `team status <name> --json` each started one -- the
member's `path` and `run` are the link, nothing else. `enter` on such a run says `MemberAsked`: the app
opens it READ, never as a conversation (an `agent chat` would hold the run the team wakes)."""
from __future__ import annotations

import asyncio

from textual.binding import Binding
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import DataTable, Static

import palette
import panes
from faces import objects, play_verb
from faces import team as team_faces
from model import PaneSpec
import memory
from model import gestures
from model.runs import AGENT_COLUMNS, RUN_COLUMNS, AgentLine, Catalogue, RunLine
from panes import live
from panes.overlays import AskScreen, ConfirmScreen, Overlay, RunParamsScreen, StatsScreen

RELOAD = "agents-reload"             # the worker group of the tab's reading: one at a time


def said_of(face) -> str:
    """-> the last line a verb said on a refusal, for the remedy line."""
    lines = (face.err or face.out).strip().splitlines()
    return lines[-1] if lines else f"rc {face.rc}"


def tail_of(faced: list[dict]) -> dict:
    """-> the last object of an agent's `status --json`: the providers, `last`."""
    return next((one for one in reversed(faced) if "run" not in one), {})


def flags_of(found: dict) -> tuple[str, ...]:
    """-> the flags of a launch the profile makes, the filled-in ones alone, then one `--package <name>=on|off` per
    package changed; a caller's command (`harness`) is no provider: the flags after `--` name it."""
    flags: list[str] = []
    if found.get("provider") and found["provider"] != "harness":
        flags += ["--provider", str(found["provider"])]
    if found.get("model"):
        flags += ["--model", str(found["model"])]
    if found.get("max_budget_usd") is not None:
        flags += ["--max-budget-usd", f"{float(found['max_budget_usd']):g}"]
    if found.get("effort"):
        flags += ["--effort", str(found["effort"])]
    if found.get("permissions"):
        flags += ["--permissions", str(found["permissions"])]
    for name, on in (found.get("packages") or {}).items():
        flags += ["--package", f"{name}={'on' if on else 'off'}"]
    return tuple(flags)


class RunsScreen(Overlay):
    """The runs of one agent: `enter` resumes the run under the cursor, `n` opens a new one,
    `s` stacks its statistics, `P` purges it, `B` purges the agent's runs before a date, `u` reads
    them again, `escape` closes. Resuming and opening close the overlay with what was asked;
    measuring and purging keep it."""

    BINDINGS = Overlay.BINDINGS + [Binding("q", "cancel", "close"), Binding("n", "new", "new"),
                                   Binding("s", "stats", "stats"), Binding("u", "reread", "reload"),
                                   Binding("P", "purge", "purge"), Binding("B", "purge_before", "before")]
    keys = [("enter", "resume"), ("n", "new"), ("s", "stats"), ("P", "purge"), ("B", "purge before"),
            ("u", "reload"), ("esc", "close")]
    DEFAULT_CSS = """
    RunsScreen > Vertical#box { width: 95%; max-width: 160; max-height: 90%; }
    """
    scrolls = False             # its table scrolls itself

    def __init__(self, owner: "AgentsPane", line: AgentLine, marks: dict[tuple[str, str], tuple[str, str]] | None = None) -> None:
        super().__init__()
        self.owner, self.line = owner, line
        self.marks = dict(marks or {})        # (agent, run) -> (team, member): the runs members of teams hold

    def body(self):
        yield Static(palette.strong(f"runs of {palette.agent_label(self.line.agent, self.owner.house)}"),
                     id="runs-title", markup=False)
        yield panes.table(id="runs", zebra_stripes=True, cell_padding=2)

    def on_mount(self) -> None:
        table = self.query_one("#runs", DataTable)
        table.add_columns(*RUN_COLUMNS)
        self._fill()
        table.focus()

    def _fill(self) -> None:
        table = self.query_one("#runs", DataTable)
        table.clear()
        for index, run in enumerate(self.line.runs):
            mark = self.marks.get((run.agent, run.run))
            table.add_row(palette.cell_of(run.name), palette.cell_of(f"{mark[0]}/{mark[1]}" if mark else None),
                          run.run, str(run.exchanges), run.state,
                          palette.cell_of(run.cost_usd, money=True), str(run.launches), palette.weight_cell(run.weight),
                          palette.share_of((run.context or {}).get("pp")), palette.context_cell(run.context),
                          palette.moment_of(run.last_at) if run.last_at else palette.NONE,
                          palette.cell_of(run.session), key=str(index))

    def highlighted(self) -> RunLine | None:
        table = self.query_one("#runs", DataTable)
        runs = self.line.runs
        return runs[table.cursor_row] if table.row_count and 0 <= table.cursor_row < len(runs) else None

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        event.stop()
        run = self.highlighted()
        if run is not None:
            mark = self.marks.get((run.agent, run.run))
            self.dismiss(("member", run, mark) if mark else ("resume", run))

    def action_new(self) -> None:
        self.dismiss(("new", self.line))

    async def action_stats(self) -> None:
        run = self.highlighted()
        if run is not None:
            await self.owner.show_stats(run)

    async def action_reread(self) -> None:
        await self.reread()

    async def action_purge(self) -> None:
        run = self.highlighted()
        if run is not None:
            await self.owner.purge(self, key=run.run)

    def action_purge_before(self) -> None:
        async def dated(date: str | None) -> None:
            if date:
                await self.owner.purge(self, before=date)
        agent = self.line.agent
        self.app.push_screen(AskScreen(f"purge the runs of {palette.agent_label(agent, self.owner.house)} before",
                                       palette.BEFORE_HELP, "",
                                       preview=lambda date: gestures.preview(gestures.purge(agent, before=date or "…"))),
                             dated)

    async def reread(self) -> None:
        """The agent's runs read again (`status --json`), the list redrawn."""
        self.line = await self.owner.read_agent(self.line)
        self._fill()


class AgentsPane(Vertical):
    """The Agents tab: the table of the agents, and the overlay of the runs of one."""

    DEFAULT_CSS = """
    AgentsPane { height: 1fr; }
    #agents { height: 1fr; }
    #agents-text { height: auto; padding: 1 2; }
    """

    class OpenAsked(Message):
        """A conversation is asked: a new one with `agent` (`run` None) -- `name` the name typed for it --,
        or `run` resumed -- its `history` (`agent exchanges --json`) replayed first, read by the opener when a
        tab is born (`None`)."""

        def __init__(self, agent: str, run: str | None, history: list[dict] | None,
                     flags: tuple[str, ...] = (), name: str = "") -> None:
            super().__init__()
            self.agent, self.run, self.history, self.flags, self.name = agent, run, history, tuple(flags), name

    class MemberAsked(Message):
        """A run a member of a team holds is asked: the app opens it READ."""

        def __init__(self, team: str, member: str, path: str, run: str) -> None:
            super().__init__()
            self.team, self.member, self.path, self.run = team, member, path, run

    class Reloaded(Message):
        """The faces were read again: the catalogue and the hour of the reading."""

        def __init__(self, catalogue: Catalogue) -> None:
            super().__init__()
            self.catalogue = catalogue

    class Refused(Message):
        """A verb the tab played refused: what it said, for the remedy line."""

        def __init__(self, said: str) -> None:
            super().__init__()
            self.said = said

    def __init__(self, spec: PaneSpec, house: str) -> None:
        super().__init__(id=f"pane-{spec.key}")
        self.spec, self.house = spec, house
        self.catalogue = Catalogue()
        self._loaded = False
        self._opening = 0                    # overlays of the runs being opened: the teams read first

    def compose(self):
        yield panes.table(id="agents", zebra_stripes=True, cell_padding=2)
        yield Static(palette.agents_text(0), id="agents-text", markup=False)

    def on_mount(self) -> None:
        self.query_one("#agents", DataTable).add_columns(*AGENT_COLUMNS)
        self.reread()

    async def settled(self) -> None:
        """Returns once the faces were read once -- what a render waits for."""
        while not self._loaded:
            await asyncio.sleep(0.01)

    # ---------- the faces ----------
    async def read_agent(self, line: AgentLine) -> AgentLine:
        """-> the agent's line with its runs read again from `agent status <path> --json`."""
        faced = objects(await play_verb(["agent", "status", line.agent, "--json"], self.house))
        return AgentLine.read({"agent": line.agent, "running": line.running},
                              [RunLine.read(obj) for obj in faced if "run" in obj], tail_of(faced))

    async def reload(self) -> None:
        """One `agent list --json`, one `agent status --json` per agent; the table rebuilt."""
        agents: list[AgentLine] = []
        for listed in objects(await play_verb(["agent", "list", "--json"], self.house)):
            faced = objects(await play_verb(["agent", "status", str(listed.get("agent", "")), "--json"], self.house))
            agents.append(AgentLine.read(listed, [RunLine.read(obj) for obj in faced if "run" in obj], tail_of(faced)))
        if not live(self):                       # the post left while the faces were read
            return
        self.catalogue = Catalogue(agents, palette.hhmmss())
        table = self.query_one("#agents", DataTable)
        table.clear()
        for index, line in enumerate(agents):
            table.add_row(palette.agent_label(line.agent, self.house), str(len(line.runs)), str(line.running), palette.cell_of(line.state),
                          palette.cell_of(line.cost_usd, money=True), str(line.launches), palette.weight_cell(line.weight),
                          palette.moment_of(line.last_at) if line.last_at else palette.NONE, key=str(index))
        self.query_one("#agents-text", Static).update(palette.agents_text(len([one for one in agents
                                                                            if one.agent != palette.HOUSE])))
        self._loaded = True
        self.post_message(self.Reloaded(self.catalogue))

    def reread(self) -> None:
        """At the start, on `u`, after every verdict: the faces again, one reading at a time."""
        self.run_worker(self._reload(), group=RELOAD, exclusive=True)

    async def _reload(self) -> None:
        """The faces read under the guard; a reading that failed counts as read."""
        try:
            await panes.guarded(self, self.reload(), "agents")
        finally:
            self._loaded = True

    # ---------- the gestures ----------
    def highlighted(self) -> AgentLine | None:
        table = self.query_one("#agents", DataTable)
        return self.catalogue.at(table.cursor_row) if table.row_count else None

    def focus_table(self) -> None:
        table = self.query_one("#agents", DataTable)
        if table.row_count:
            table.focus()
        else:
            self.screen.set_focus(None)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id != "agents":
            return
        event.stop()
        line = self.catalogue.at(event.cursor_row)
        if line is not None:
            self._opening += 1
            self.run_worker(self._show_runs(line))

    async def _show_runs(self, line: AgentLine) -> None:
        """The overlay of the agent's runs, the runs members of teams hold marked."""
        try:
            marks = await self.read_teams()
            if live(self):
                await self.app.push_screen(RunsScreen(self, line, marks), self._ran)
        finally:
            self._opening -= 1

    async def opened(self) -> None:
        """Returns once no overlay of the runs is being opened -- what a render waits for after a key."""
        while self._opening:
            await asyncio.sleep(0.01)

    async def read_teams(self) -> dict[tuple[str, str], tuple[str, str]]:
        """-> `(agent, run) -> (team, member)`: the run each member of a started team holds, as `team status
        <name> --json` says it -- read now, one face per started team; nothing kept between two openings."""
        marks: dict[tuple[str, str], tuple[str, str]] = {}
        badges, _face = await team_faces.badges(self.house)
        for badge in badges:
            if not isinstance(badge.get("started"), dict):
                continue
            name = str(badge.get("team", ""))
            state, _face = await team_faces.state(self.house, name)
            for member in (state or {}).get("members") or []:
                if isinstance(member, dict) and member.get("path") and member.get("run"):
                    marks[(str(member["path"]), str(member["run"]))] = (name, str(member.get("member", "")))
        return marks

    async def _ran(self, asked) -> None:
        """What the overlay of the runs closed with: a run to resume, a new conversation, or nothing."""
        if not asked:
            return
        what, which = asked[0], asked[1]
        if what == "member":
            team, member = asked[2]
            self.post_message(self.MemberAsked(team, member, which.agent, which.run))
        elif what == "resume":
            await self.resume(which)
        elif what == "new":
            self.ask_params(which)

    def new_run(self) -> bool:
        """`n` on the table: a new conversation with the agent under the cursor, through the overlay
        of its parameters."""
        line = self.highlighted()
        if line is None:
            return False
        self.ask_params(line)
        return True

    def ask_params(self, line: AgentLine) -> None:
        """The overlay of a new run's parameters, prefilled with what the agent last played, the
        models and the spells read from `agent providers --json` as it opens, its packages as the agent's
        `status --json` says them; `enter` asks the conversation with the flags filled in -- a package changed
        among them --, and the name typed -- played once the run is opened."""
        latest = next((one for one in self.catalogue.agents if one.agent == line.agent), line)

        def opened(found: dict | None) -> None:
            if found is not None:
                self.post_message(self.OpenAsked(line.agent, None, [], flags_of(found), str(found.get("name") or "")))
        self.app.push_screen(RunParamsScreen(f"a new run of {palette.agent_label(line.agent, self.house)}", list(latest.providers), self.offered,
                                             latest.defaults, packages=latest.packages), opened)

    async def offered(self) -> dict[str, dict]:
        """-> what each wired provider spells and names, `agent providers --json` read now."""
        face = await play_verb(["agent", "providers", "--json"], self.house)
        if face.rc != 0:
            self.post_message(self.Refused(said_of(face)))
        return {str(one.get("provider", "")): one for one in objects(face)}

    def ask_add(self) -> None:
        """`a`: the path of a new agent asked, the exact command shown under it as it is typed;
        `enter` plays `agent add <path>`, the table read again, a refusal on the remedy line."""
        async def added(path: str | None) -> None:
            if not path:
                return
            face = await play_verb(["agent", "add", path], self.house)
            if face.rc != 0:
                self.post_message(self.Refused(said_of(face)))
                return
            self.reread()
        self.app.push_screen(AskScreen("path of the new agent", "relative to the house, e.g. agents/ag2 -- born of "
                                       "the kit, borrowing the house's machine", "",
                                       preview=lambda path: f"./pp agent add {path}"), added)

    async def resume(self, run: RunLine) -> None:
        """The conversation asked on `--run`: the opener reads its history when a tab is born for it."""
        self.post_message(self.OpenAsked(run.agent, run.run, None))

    # ---------- the purge ----------
    async def purge(self, screen: RunsScreen, key: str | None = None, before: str | None = None,
                    force: bool = False) -> None:
        """A purge of the run `key` (or of the runs before the date `before`) of the overlay's agent, SHOWN
        first: the verb played without `--yes`, what it would remove shown with the exact `--yes` command,
        played once the key -- or the date -- is typed as it is. A refusal goes to the remedy line."""
        agent, target = screen.line.agent, key or before
        dry = gestures.purge(agent, key, before)
        yes = gestures.purge(agent, key, before, yes=True, force=force)
        if dry is None or yes is None:
            return
        self._opening += 1                   # a render waits for the overlay the verb's answer opens
        try:
            face = await play_verb(dry, self.house)
            found = objects(face)
            if face.rc != 0 or not found:
                self.post_message(self.Refused(self._refused(face, agent, key)))
                return

            async def confirmed(sure: bool | None) -> None:
                if sure:
                    await self._purged(screen, agent, key, before, yes, force)
            title = f"purge {f'run {key}' if key else f'the runs before {before}'} of " \
                    f"{palette.agent_label(agent, self.house)}" + (" -- with --force" if force else "")
            await self.app.push_screen(ConfirmScreen(title, gestures.preview(yes), expect=target,
                                                     detail=palette.purge_text(found[0])), confirmed)
        finally:
            self._opening -= 1

    async def _purged(self, screen: RunsScreen, agent: str, key: str | None, before: str | None,
                      yes: list[str], force: bool) -> None:
        """The `--yes` command played as shown: the runs it removed leave the memory, the faces are read again; a
        clone with unsent commits offers `--force`, a refusal goes to the remedy line."""
        self._opening += 1
        try:
            face = await play_verb(yes, self.house)
            found = objects(face)
            if face.rc != 0 or not found:
                said = self._refused(face, agent, key)
                if "workdir-unpushed" in said and not force:
                    self.post_message(self.Refused(said))
                    await self.purge(screen, key, before, force=True)
                    return
                self.post_message(self.Refused(said))
                return
            memory.forget([(agent, str(one.get("key"))) for one in found[0].get("runs") or [] if isinstance(one, dict)])
            if live(screen):
                await screen.reread()
            self.reread()
        finally:
            self._opening -= 1

    def _refused(self, face, agent: str, key: str | None) -> str:
        """-> what the verb said on its refusal, headed by `x closes its tab --` when a tab of the dialogue holds the
        run the verb finds busy (the remedy line cuts the end of a long refusal, never its head)."""
        said = said_of(face)
        dialogue = getattr(self.app, "dialogue", None)
        if "run-busy" in said and key and dialogue is not None and dialogue.view_of(agent, key) is not None:
            said = f"x closes its tab -- {said}"
        return said

    async def show_stats(self, run: RunLine) -> None:
        """`agent stats --json` of a run, stacked in an overlay."""
        face = await play_verb(["agent", "stats", run.agent, run.run, "--json"], self.house)
        found = objects(face)
        if face.rc != 0 or not found:
            self.post_message(self.Refused(said_of(face)))
            return
        self.app.push_screen(StatsScreen(run, found[0]))

    @property
    def keys(self) -> list[tuple[str, str]]:
        return ([("enter", "runs"), ("n", "new"), ("a", "add"), ("u", "reload")] if self.catalogue.agents
                else [("a", "add"), ("u", "reload")])
