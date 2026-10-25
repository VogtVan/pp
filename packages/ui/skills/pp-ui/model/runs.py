"""runs -- the typed state of the AGENTS tab: the agents of the house and the runs of each, as
the faces of `agent` say them (`agent list --json`, `agent status <path> --json`); pure
dataclasses, no I/O, no Textual."""
from __future__ import annotations

from dataclasses import dataclass, field

AGENT_COLUMNS = ("agent", "runs", "running", "last state", "USD", "launches", "weight", "last")
EFFORTS = ("low", "medium", "high", "xhigh", "max")   # the effort's five words, as pp judges them
PERMISSIONS = ("auto", "strict", "bypass")            # the permission regimes, as pp judges them
RUN_COLUMNS = ("name", "team", "run", "exch.", "state", "USD", "launches", "weight", "pp", "ctx", "last", "session")


@dataclass(frozen=True)
class RunLine:
    """One run as `agent status <path> --json` says it: its agent, its key, its name, its
    exchanges, the state that prevails, the sums the house kept."""
    agent: str
    run: str
    name: str = ""
    exchanges: int = 0
    state: str = ""
    stack: str = ""
    session: str | None = None
    provider: str | None = None
    cost_usd: float | None = None
    launches: int = 0
    responses: int = 0
    first_message: str | None = None
    first_at: str | None = None
    last_at: str | None = None
    context: dict | None = None
    weight: dict | None = None        # what a purge of the run would count, `{lines, files, bytes, flow}`

    @staticmethod
    def read(obj: dict) -> "RunLine":
        """-> the line an object of the face carries; a field the face left out stays empty."""
        cost = obj.get("cost_usd")
        return RunLine(str(obj.get("agent", "")), str(obj.get("run", "")), str(obj.get("name") or ""),
                       int(obj.get("exchanges") or 0), str(obj.get("state") or ""), str(obj.get("stack") or ""),
                       obj.get("session") if isinstance(obj.get("session"), str) else None,
                       obj.get("provider") if isinstance(obj.get("provider"), str) else None,
                       float(cost) if isinstance(cost, (int, float)) else None,
                       int(obj.get("launches") or 0), int(obj.get("responses") or 0),
                       obj.get("first_message") if isinstance(obj.get("first_message"), str) else None,
                       obj.get("first_at") if isinstance(obj.get("first_at"), str) else None,
                       obj.get("last_at") if isinstance(obj.get("last_at"), str) else None,
                       obj.get("context") if isinstance(obj.get("context"), dict) else None,
                       obj.get("weight") if isinstance(obj.get("weight"), dict) else None)

    @property
    def label(self) -> str:
        """The title a tab on this run takes: its name, else `<agent> · <run>`."""
        return self.name or f"{self.agent} · {self.run}"


@dataclass(frozen=True)
class AgentLine:
    """One agent as the faces say it: its path, the runs its `status --json` lists (in the
    face's order), how many a wake-up plays now; its sums deduced from its runs."""
    agent: str
    runs: tuple[RunLine, ...] = ()
    running: int = 0
    providers: tuple[str, ...] = ()  # the providers the house is wired with, as the agent's status says them
    played: dict | None = None       # `last` of the status: the provider and the policy the agent last played
    weight: dict | None = None       # the sum of its runs' weights, as `list --json` says it
    packages: dict[str, bool] | None = None   # the packages its instance pins beyond its base, as its status says
    unread: bool = False             # its status could not be read: nothing of its runs is known

    @staticmethod
    def read(listed: dict, runs: list[RunLine], tail: dict | None = None) -> "AgentLine":
        """-> the agent's line: what `list --json` says of it, its runs, and the last object of its
        `status --json` (the providers, `last`, `packages` -- None when the face says none)."""
        tail = tail or {}
        providers = tail.get("providers") if isinstance(tail.get("providers"), list) else []
        played = tail.get("last") if isinstance(tail.get("last"), dict) else None
        packages = ({str(one.get("name", "")): one.get("on") is True for one in tail["packages"] if isinstance(one, dict)}
                    if isinstance(tail.get("packages"), list) else None)
        return AgentLine(str(listed.get("agent", "")), tuple(runs), int(listed.get("running") or 0),
                         tuple(str(one) for one in providers), played,
                         listed.get("weight") if isinstance(listed.get("weight"), dict) else None, packages)

    @staticmethod
    def unread_of(listed: dict) -> "AgentLine":
        """-> the line of an agent whose status could not be read: what `list --json` says of it, no run."""
        return AgentLine(str(listed.get("agent", "")), (), int(listed.get("running") or 0),
                         weight=listed.get("weight") if isinstance(listed.get("weight"), dict) else None, unread=True)

    @property
    def defaults(self) -> dict:
        """The parameters a new run of the agent starts from: the provider and the policy it last
        played -- the provider when it is one the house is wired with, else the only one wired."""
        played = self.played or {}
        found = dict(played.get("policy") or {})
        provider = played.get("provider")
        if provider in self.providers:
            found["provider"] = provider
        elif len(self.providers) == 1:
            found["provider"] = self.providers[0]
        return found

    @property
    def last(self) -> RunLine | None:
        """The run whose last event is the latest, None without a run."""
        dated = [one for one in self.runs if one.last_at]
        return max(dated, key=lambda one: one.last_at or "") if dated else (self.runs[-1] if self.runs else None)

    @property
    def state(self) -> str:
        return self.last.state if self.last else ""

    @property
    def last_at(self) -> str | None:
        return self.last.last_at if self.last else None

    @property
    def cost_usd(self) -> float | None:
        costs = [one.cost_usd for one in self.runs if one.cost_usd is not None]
        return round(sum(costs), 6) if costs else None

    @property
    def launches(self) -> int:
        return sum(one.launches for one in self.runs)


@dataclass
class Catalogue:
    """The agents the Agents tab read, in the faces' order, and the hour of the reading."""
    agents: list[AgentLine] = field(default_factory=list)
    read_at: str = ""

    def at(self, index: int) -> AgentLine | None:
        return self.agents[index] if 0 <= index < len(self.agents) else None

    def agent(self, name: str) -> AgentLine | None:
        return next((one for one in self.agents if one.agent == name), None)

    def find(self, agent: str, run: str) -> RunLine | None:
        line = self.agent(agent)
        return next((one for one in line.runs if one.run == run), None) if line else None

    @property
    def runs(self) -> int:
        return sum(len(one.runs) for one in self.agents)
