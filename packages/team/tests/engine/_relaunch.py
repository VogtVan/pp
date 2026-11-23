"""Support of the scenarios `team-member-relaunch-vector*` (rule 10): a member's run taken up again with its VECTORS --
its task's node, `plan:job/ph/bt` of a shared plan under the team's directory, then its own `team-member:rd/mi` --,
as the tick passes them at every launch. One house pinning `agent`, `team` and `plan`, the team `rd` of `_roles.py`
(`mi` holds `inspect`: its view mounts `review/law`, the law TM5); `plan` switched on by the season; T1 posted to mi
with the node. mi's first launch deposits no proof (`unproven`) and spends its bound (`launches-spent`): the run
STANDS on the proof its first prompt asked, the tick takes it up and the run PARKS (its held output served, launched
on by nobody). Loaded by
`support(__file__, "relaunch")`, never collected as a scenario."""
from __future__ import annotations

import json

from conductor import instance, persistence
from tests.harness import load_script, support

T = support(__file__, "team")
R = support(__file__, "roles")

NODE, GHOST, MEMBER = "plan:job/ph/bt", "plan:ghost/ph/bt", "team-member:rd/mi"
SECTIONS = ((["job"], "Context", "a shared plan"), (["job"], "Ground", "the ground"),
            (["job"], "Expected", "the expected"), (["job"], "Choices", "the choices"),
            (["job"], "Items", "- ph -- a phase"),
            (["job", "ph"], "Ground", "the ground"), (["job", "ph"], "Expected", "the expected"),
            (["job", "ph"], "Choices", "the choices"), (["job", "ph"], "Items", "- bt -- a batch"),
            (["job", "ph", "bt"], "Ground", "the batch's ground"))


class Relaunched:
    """The house, mi's run settled -- standing, then taken up by the tick and parked -- and the readings of that run:
    `key`, `flow()`, `relaunch(*vectors)`, `turns()`, `messages()`. `more` adds launches of the witness for mi after
    the three the settling plays."""

    def __init__(self, bench, more: tuple = ()) -> None:
        self.h = h = T.House(bench, packages=("agent", "team", "plan"),
                             script={"mi": [{"sleep": 0.1, "unproven": True,
                                             "body": {"ask": {"to": "house", "text": "which?"}}},
                                            R.DONE, R.DONE, *more]})
        by_kind, all_ended = T.by_kind, T.all_ended
        R.declared(h)
        self.started = h.call("team", "start", "rd", *h.harnessed, "--package", "plan=on", "--no-tick")
        self.shared = h.teams / "rd"                        # the root of documents of the team's runs
        plans = load_script(instance.bundle_of(h.house, "plan") / "skills" / "pp-plan" / "pp-plan.py")
        for address, name, prose in SECTIONS:
            plans.write_section(self.shared, address, name, prose)
        self.posted = h.call("team", "post", "rd", "--to", "mi", "--message", "work mi", "--vector", NODE, "--no-tick")
        h.call("team", "tick", "rd")
        self.settled = h.settled("rd", lambda found: bool(by_kind(found, "done")) and all_ended(found), 40)
        self.key = next((one.get("run") for one in by_kind(h.events("rd"), "wake-launched", agent="mi")
                         if one.get("run")), "")
        self.meta = h.meta_of("agents/mi")

    def flow(self) -> list[dict]:
        said = self.h.call("agent", "flow", "agents/mi", self.key, "--json") if self.key else None
        return [json.loads(line) for line in (said.stdout.splitlines() if said else []) if line.startswith("{")]

    def relaunch(self, *vectors: str, message: str = "again"):
        flags = [one for vector in vectors for one in ("--vector", vector)]
        return self.h.call("agent", "run", "agents/mi", "--run", self.key, "--message", message, "--documents",
                           str(self.shared), *flags, "--package", "plan=on", *self.h.harnessed)

    def turns(self) -> int:
        return persistence.turns_of(persistence.slot_of(self.meta, self.key)) if self.key else -1

    def messages(self) -> list[dict]:
        found = self.h.records / "messages.jsonl"
        return [json.loads(line) for line in (found.read_text(encoding="utf-8").splitlines() if found.is_file() else [])
                if line.strip()]
