"""Support module (rule 10) -- a throwaway house at the arrival version carrying the data in the
form the starting version wrote: the records of continuity and steering as files, a plan of three
levels born on the old templates, a held line of the bus under an old key, a team declared by
`team new`, the door and the marble the old install wrote. What the scenarios of this migration
share; never a scenario itself."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tests.harness import INSTANCE
from conductor import install

MIGRATION = Path(__file__).resolve().parents[1]
DATA = MIGRATION / "data"
PACKAGES = ("agent", "team", "plan", "steering", "continuity")
AGENT = Path("agents") / "a1"
TEAM = "t1"
DOOR_BASH = ("This workspace is conducted. Run now:\n```bash\n./pp -new\n```\n"
             "Then follow what it prints: the conductor's output names the next call.\n")
STAMP = "2026-11-20T10:00:00.000000+00:00"
FIELDS = ("name", "at", "work", "comment", "status", "reason", "labels", "key", "touched", "closed", "archived",
          "recalled")

# the operator's prose of each document, by section: what a migration never loses
PROSE = {
    "plan": {"Context": ["A notebook kept on the command line."],
             "Target": ["The notes stay in one file; a web front stays out."],
             "Expected": ["`memo add` then `memo list` prints the note back."],
             "Items": ["- core -- the store and its two commands"]},
    "phase": {"Context": ["the store and its two commands"],
              "Ground": ["`memo/storage.py` holds add and list."],
              "Target": ["the store gains add and list."],
              "Expected": ["the store's bench green."],
              "Items": ["- store -- the store"]},
    "batch": {"Context": ["the store"],
              "Ground": ["`storage.py` lines 1-40."],
              "Target": ["`add(note)` and `list()`, one file."],
              "Expected": ["`add` then `list` gives the note back."],
              "Tests": ["`tests/test_storage.py`, written first."],
              "Arbitrations": ["a scan or an index -- the scan."],
              "Items": ["- add -- the add verb", "- list -- the list verb"],
              "Decisions": ["23/11: the scan kept."]},
}
SHARED = {"Context": ["A plan of the team's own."], "Arbitrations": ["none yet."]}
WORK_WITH_KEY = "the store batch, tracked as plan-lot:memo/core/store"   # prose: kept as written (T8)
OPERATION_WITH_KEY = "framed plan-phase:memo/core"                      # prose: kept as written (T8)
TEMPLATES = {"plan": "_PLAN.md", "phase": "_PHASE.md", "batch": "_BATCH.md"}


def house(bench, name: str):
    """-> a throwaway house at the arrival version, its own folder: the public packages pinned, a
    borrowing agent, the old form written in both instances, a team, a plan in the house and in the
    team's root."""
    env = bench.env(name, packages=PACKAGES, at=bench.temp() / name)
    install.install(env.engine, env.root / AGENT / INSTANCE, [], slug="a1", borrow=True)
    written(env.root, env.made, env.root / AGENT / INSTANCE)
    return env


def blueprint() -> str:
    return (DATA / "BLUEPRINT.txt").read_text(encoding="utf-8").strip()


def document(kind: str, slug: str, plan: str, phase: str, items: list[str], prose: dict | None = None) -> str:
    """-> a plan document as the old script rendered it from its template: the holes filled, the
    operator's prose written over the sections it names, the others left as the template's
    instruction, the sections the template lacks appended."""
    prose = PROSE[kind] if prose is None else prose
    text = (DATA / TEMPLATES[kind]).read_text(encoding="utf-8")
    text = (text.replace("{slug}", slug).replace("{plan}", plan).replace("{phase}", phase)
            .replace("{created}", "2026-11-20").replace("status: todo", "status: doing").replace("{blueprint}", f"KM1  {blueprint()}"))
    front, body = text.split("\n---\n", 1)
    front += "".join(f"\nitem.{n}: {item}" for n, item in enumerate(items, 1))
    head, *chunks = re.split(r"(?m)^## ", body)
    out, seen = head, []
    for chunk in chunks:
        name, _, rest = chunk.partition("\n")
        seen.append(name)
        if name in prose:
            rest = "\n" + "\n".join(prose[name]) + "\n\n"
        out += f"## {name}\n{rest}"
    for name in [one for one in prose if one not in seen]:
        out = out.rstrip("\n") + f"\n\n## {name}\n\n" + "\n".join(prose[name]) + "\n"
    return front + "\n---\n" + out.rstrip("\n") + "\n"


def plans(root: Path) -> None:
    folder = root / "plans" / "memo"
    (folder / "1-core" / "1-store").mkdir(parents=True)
    (folder / "PLAN.md").write_text(document("plan", "memo", "memo", "", ["core  doing"]), encoding="utf-8")
    (folder / "1-core" / "PHASE.md").write_text(document("phase", "core", "memo", "", ["store  doing"]),
                                                encoding="utf-8")
    (folder / "1-core" / "1-store" / "BATCH.md").write_text(
        document("batch", "store", "memo", "core", ["add  done", "list  done"]), encoding="utf-8")


def step(n: int, member: str, name: str, key: str | None, status: str = "open", labels=(),
         work: str = "") -> tuple[str, dict]:
    body = {field: None for field in FIELDS}
    body.update(name=name, at=STAMP, work=work or f"the work of {name}", comment="", status=status, reason="",
                labels=list(labels), key=key, touched=STAMP)
    if status in ("done", "dropped"):
        body["closed"] = STAMP
    return f"{member}.s.{n}", body


def records(meta: Path, member: str, steps: list[tuple[str, dict]], operations: int, torn: bool) -> None:
    folder = meta / ".sys" / "records"
    folder.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps({"at": f"2026-11-{10 + n:02d}T09:00:00+00:00",
                         "entry": OPERATION_WITH_KEY if n == 0 else f"operation {n} of {member}"})
             for n in range(operations)]
    (folder / "operations.jsonl").write_text("\n".join(lines) + "\n" + ('{"at": "2026-11' if torn else ""),
                                             encoding="utf-8")
    (folder / "operations.jsonl.lock").write_text("", encoding="utf-8")
    (folder / "history.jsonl").write_text(json.dumps({"at": "2026-11-16T08:00:00+00:00",
                                                      "synthesis": f"the week of {member}"}) + "\n",
                                          encoding="utf-8")
    labels = {"memo": {"note": "the memo plan", "order": [sid for sid, one in steps if "memo" in one["labels"]]}}
    (folder / "steps.json").write_text(json.dumps({"counters": {"s": len(steps)}, "steps": dict(steps),
                                                   "labels": labels}, ensure_ascii=False, indent=1) + "\n",
                                       encoding="utf-8")
    (folder / "steps.json.lock").write_text("", encoding="utf-8")
    (meta / ".sys" / "system.common.md").write_text("# the marble of a run its principal conducts\n",
                                                    encoding="utf-8")


def written(root: Path, made: Path, agent: Path) -> None:
    """The old form, in the house's instance and in its agent's."""
    records(made, made.parent.name, [step(1, "house", "store-batch", "plan-lot:memo/core/store", labels=["memo"],
                                          work=WORK_WITH_KEY),
                                     step(2, "house", "core-phase", "plan-phase:memo/core", labels=["memo"]),
                                     step(3, "house", "loose", None, status="done")], 3, torn=True)
    records(agent, "a1", [step(1, "a1", "agent-step", None)], 2, torn=False)
    bus = {"standing|plan|plan-next-move|plan:memo": {
        "last_at": STAMP, "text": "the batch core/store awaits its implementation (plan-lot:memo/core/store)"}}
    (made / ".sys" / "records" / "events.json").write_text(json.dumps(bus, indent=2) + "\n", encoding="utf-8")
    plans(made)
    (root / "CLAUDE.md").write_text(DOOR_BASH, encoding="utf-8")
    (root / "AGENTS.md").write_text(DOOR_BASH + "\nThe operator's own line.\n", encoding="utf-8")
    team = root / "teams" / TEAM
    (team / "plans").mkdir(parents=True)
    (team / "TEAM.md").write_text("---\nagents: |\n  worker agents/a1\nroot: worker\nbudget: 5\nlaunches: 24\n"
                                  "timeout: 900\nschedule: off\n---\n", encoding="utf-8")
    (team / f"TEAM-{TEAM}.md").write_text("---\nproc: |\n  SERVE\nserve: |\n  TEAM-t1.md\nattach: turn.begin\n---\n"
                                          + "\n".join(INTENTION) + "\n", encoding="utf-8")
    folder = team / "plans" / "shared"
    folder.mkdir()
    (folder / "PLAN.md").write_text(document("plan", "shared", "shared", "", [], SHARED), encoding="utf-8")


INTENTION = ["`worker` does every task itself and answers it.",
             "",
             "Every answer must stay short and say only what the task needs."]


def gestures():
    """-> the migration's gesture modules, imported from its folder."""
    for path in (str(MIGRATION.parent), str(MIGRATION)):
        if path not in sys.path:
            sys.path.insert(0, path)
    from gestures import cleanup, continuity, keys, plans as planned, steering, teams   # noqa: E402
    return {"plans": planned, "plan-keys": keys, "steering": steering, "continuity": continuity,
            "teams": teams, "cleanup": cleanup}
