"""The SUPPORT module of the `adapters` area's scenarios of the `model` provider (tests/README.md,
rule 10): the HOUSE a scenario installs for itself -- a throwaway instance pinning `agent`, its agents
born as borrowers of its machine --, the readers of its records and of a run's trace, the modelled
harness launched by hand as the editor's extension would launch it, and the witness roots of the
patterns' campaign. Loaded by `support(__file__, "model")`; every scenario installs its own house.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from conductor import install, persistence
from tests.harness import INSTANCE, PRODUCT_ENGINE, SOURCE, cli

DOCS = SOURCE / "tests" / "conduction" / "roots"              # the witness roots: read-lines, laps, route…
MODEL = SOURCE / "adapters" / "model"
HARNESS = MODEL / "harness.py"
PROVIDER = "model"
INTENT = "PP_MODEL_INTENT"                                 # the intention of the modelled LLM, in its environment
ROUTE = SOURCE / "tests" / "conduction" / "roots" / "route"   # the workflow: STAGE then LEFT or RIGHT at a PICK next
REVIEW = SOURCE / "tests" / "conduction" / "roots" / "review" # the door offered to the WORK by the root's TURN overlay
LAWFUL = "---\nname: TURN\nconstraints.production: |\n  L1  the answer lands\n---\n"   # an overlay of
# the kit's TURN: a law of production, so that every exchange owes a proof -- a value due to the tool
HYBRID = "conduction: hybrid"
PROVEN_LAPS = ("---\nname: LAPS\nkind: proc\noutput: any\ndescription: a described door proven at every lap\n"
               "field: |\n  three names\nconstraints.production: |\n  LP1  the lap names its element\n"
               "proc: |\n  INFER\n  PROVE\n---\n\nOne line per element.\n")   # a lap's line and its proof fuse
# in one output whose closing asks a value: what `conduction: hybrid` answers in the tool result


def proven_laps(bench) -> Path:
    """-> a root of documents holding a LAPS door whose every lap ends on a PROVE: the witness on which
    hybrid takes fewer launches than strict (the campaign's own LAPS writes no PROVE)."""
    root = bench.temp() / "laps-proven"
    root.mkdir()
    (root / "LAPS.md").write_text(PROVEN_LAPS, encoding="utf-8")
    return root


def loaded(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def harness_module():
    """-> the harness as a module: its grammar and its data, read by a scenario."""
    return loaded(HARNESS, "pp_model_harness")


def lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def objects(text: str) -> list[dict]:
    found = []
    for line in text.splitlines():
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict):
            found.append(one)
    return found


def harnessed(cwd: Path, message: str, variant: str = "conform", documents: Path | None = None,
              door: str | None = None, session: str | None = None) -> tuple[subprocess.CompletedProcess, list[dict]]:
    """The modelled harness launched BY HAND on the workspace `cwd`, as the editor's extension launches a
    model: the message on stdin, no output of pp in it, the root and the door in its environment -- the
    model opens the run itself. -> (the play, the events it said)."""
    env = dict(os.environ)
    if documents is not None:
        env["PP_DOCUMENTS"] = str(documents)
    if door is not None:
        env["PP_DOOR"] = door
    argv = [sys.executable, str(HARNESS), "--variant", variant, *(["--session", session] if session else [])]
    played = subprocess.run(argv, cwd=str(cwd), input=message, capture_output=True, text=True, env=env)
    return played, objects(played.stdout)


def timed(call):
    """-> (what the call returned, the seconds it took)."""
    started = time.monotonic()
    result = call()
    return result, round(time.monotonic() - started, 2)


class House:
    """A throwaway house pinning `agent`, its agents born under `agents/<name>` as borrowers, launched
    on the `model` provider: what every scenario of the model's relayed channel installs for itself."""

    def __init__(self, bench, agents: tuple[str, ...] = ("ag1",)) -> None:
        self.bench = bench
        self.ws = bench.temp() / "house"
        self.house = install.install(PRODUCT_ENGINE, self.ws / INSTANCE, ["agent"])
        self.engine = self.house / ".sys" / "engine" / "pp.py"
        self.records = self.house / ".sys" / "records"
        self.metas: dict[str, Path] = {}
        for name in agents:
            self.born(name)

    def born(self, name: str) -> Path:
        meta = self.ws / "agents" / name / INSTANCE
        install.install(self.engine, meta, [], slug=name, doors=False, borrow=True)
        self.metas[name] = meta
        return meta

    def call(self, *args: str, stdin: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
        return cli(self.engine, "--instance", str(self.house), *args, cwd=self.ws, stdin=stdin, env=env)

    def run(self, name: str, message: str, *flags: str, variant: str | None = None,
            intent: list | None = None) -> subprocess.CompletedProcess:
        """`agent run agents/<name> --provider model --message …`, the variant as the policy's model, the
        INTENTION of the model in the harness's environment (`PP_MODEL_INTENT`) when one is given."""
        policy = ["--model", variant] if variant else []
        env = {INTENT: json.dumps(intent)} if intent is not None else None
        return self.call("agent", "run", f"agents/{name}", "--provider", PROVIDER, "--message", message,
                         *policy, *flags, env=env)

    def lawful(self, name: str) -> None:
        """The agent's TURN under a law of production: every exchange owes a proof (a value due)."""
        home = self.metas[name] / "procs"
        home.mkdir(exist_ok=True)
        (home / "TURN.md").write_text(LAWFUL, encoding="utf-8")
        cli(self.engine, "--instance", str(self.metas[name]), "-build", cwd=self.ws)

    def hybrid(self, name: str) -> None:
        """`conduction: hybrid` at the agent's SETTINGS: the operator's edit of their document."""
        path = self.metas[name] / "SETTINGS.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(re.sub(r"^conduction: .*$", HYBRID, text, count=1, flags=re.M), encoding="utf-8")

    def keys(self, name: str) -> list[str]:
        return [persistence.run_id_of(one) for one in persistence.slots(self.metas[name])]

    def awaits(self, name: str, key: str) -> str:
        return persistence.awaits(persistence.slot_of(self.metas[name], key))

    def trace(self, name: str, key: str) -> list[dict]:
        slot = persistence.slot_of(self.metas[name], key)
        log = persistence.trace_of(slot)
        return lines(slot.parent / log) if log else []

    def stats(self, name: str, key: str) -> dict:
        played = cli(self.engine, "--instance", str(self.metas[name]), "-stats", key, "-json", cwd=self.ws)
        try:
            return (json.loads(played.stdout).get("runs") or [{}])[0]
        except ValueError:
            return {}

    def responses(self) -> list[dict]:
        return lines(self.records / "responses.jsonl")

    def sessions(self) -> list[dict]:
        return lines(self.records / "sessions.jsonl")

    def flow(self, key: str) -> list[dict]:
        found = []
        for path in sorted((self.records / "flows").rglob(f"{key}.jsonl")):
            found += lines(path)
        return found
