"""_real -- what the scenarios of the post at the REAL of the bench share (rule 10): a throwaway
house pinning `ui`, the agent `agents/ag1` born under it as a borrower of its machine, the
witness harness of `agent` (its support's `WITNESS`, mode `play`) written beside it and handed
to every conversation by `-- --harness` with the grammar it writes, never a provider launched;
`render` plays `./pp ui …` there, the post's memory forgotten first unless kept; the readers of
the house's records, of the agent's runs (`agent status --json`), of the prompts the witness
received and of a run's trace."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from conductor import contributions, install, metadata, persistence
from tests.harness import INSTANCE, SOURCE, cli, support

A = contributions.module_at(SOURCE / "packages" / "agent" / "tests" / "engine" / "_agent.py")
P = support(__file__, "dialogue")
AGENT = "agents/ag1"
WITNESS_GRAMMAR = A.WITNESS_GRAMMAR   # the grammar the witness writes, named beside its `--harness`
EXCHANGE = "waiting:120"             # a real exchange of the witness: several launches, each a call of pp


def lines(path: Path) -> list[dict]:
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()] if path.is_file() else []


class RealPost:
    """One house, one agent, the witness harness: what each real scenario installs for itself."""

    def __init__(self, bench, name: str) -> None:
        env = bench.env(name, packages=("ui",))
        self.made, self.engine = env.made, env.engine
        self.ws = env.made.parent
        self.agent_meta = self.ws / "agents" / "ag1" / INSTANCE
        install.install(self.engine, self.agent_meta, [], slug="ag1", doors=False, borrow=True)
        witness = bench.temp() / "witness.py"
        witness.write_text(A.WITNESS, encoding="utf-8")
        self.out = bench.temp() / "prompt"
        self.witness = witness
        self.harness = self.harness_in("play")
        self.records = self.made / ".sys" / "records"

    def harness_in(self, mode: str) -> str:
        """-> the command of the witness in `mode` (`play`; `pause`, a long thought at its first launch)."""
        return f"{sys.executable} {self.witness} {self.engine} {self.agent_meta} {mode} {self.out}"

    def render(self, *args: str, keep: bool = False, mode: str = "play"):
        """`./pp ui <args> -- --harness <the witness in mode> --provider <its grammar>` in the house; the post's memory forgotten
        first unless `keep`, so that the bench chooses what the post opens."""
        if not keep:
            P.forget(self.made)
        return cli(self.engine, "ui", *args, "--", *A.harnessing(self.harness_in(mode), WITNESS_GRAMMAR), cwd=self.ws)

    def talk(self):
        """Two messages typed at the post to the agent, the model set to `m2` between them: a real run of
        two exchanges, what the scenarios of the Agents tab start from. -> the render."""
        return self.render(AGENT, "--render", "dialogue", "--size", "120x30", "--press",
                           "h,i,enter,wait:waiting,escape,p,m,2,enter,wait:policy,i,y,o,enter", "--wait", EXCHANGE)

    # ---------- the records the verbs keep ----------
    def responses(self) -> list[dict]:
        return lines(self.records / "responses.jsonl")

    def messages(self) -> list[dict]:
        return lines(self.records / "messages.jsonl")

    def sessions(self) -> list[dict]:
        return lines(self.records / "sessions.jsonl")

    def names(self) -> list[dict]:
        return lines(self.records / "names.jsonl")

    def remembered(self) -> list:
        """-> the conversations the post keeps open, as the engine reads its space `ui`."""
        return metadata.of_package(self.made, "ui").get("open") or []

    def status_json(self) -> list[dict]:
        """-> the runs of the agent, as `agent status --json` says them (the agent's last object left out)."""
        played = cli(self.engine, "agent", "status", AGENT, "--json", cwd=self.ws)
        return [one for one in (json.loads(line) for line in played.stdout.splitlines() if line.strip()) if "run" in one]

    def last_policy(self) -> dict:
        """-> `last` of the agent's last object of `agent status --json`: what it last played."""
        played = cli(self.engine, "agent", "status", AGENT, "--json", cwd=self.ws)
        tail = [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        return (tail[-1].get("last") or {}) if tail and "run" not in tail[-1] else {}

    # ---------- what the witness received, what the run traced ----------
    def prompt(self) -> str:
        """-> the last prompt the witness received."""
        return self.out.read_text(encoding="utf-8") if self.out.is_file() else ""

    def launches(self) -> int:
        """-> how many times the witness was launched, every session together."""
        return len(list(self.out.parent.glob(self.out.name + ".prompt.*")))

    def trace(self, key: str) -> list[dict]:
        slot = persistence.slot_of(self.agent_meta, key)
        log = persistence.trace_of(slot)
        return lines(slot.parent / log) if log else []
