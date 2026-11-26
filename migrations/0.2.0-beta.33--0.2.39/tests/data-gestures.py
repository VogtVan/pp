"""Scenario `data-gestures` -- the data gestures of the migration 0.2.0-beta.33 -> 0.2.39, played in
their order on a throwaway house at the arrival version that carries the old form (a house, a
borrowing agent, a team):
- (a) a section merged into one already there follows its text, under `### <old name>` (T2)
- (a) every count equal per instance and per record; the new forms: the store's records read back
  equal to the files, the plans' fronts on `template:`, the old sections gone, no old key left
- (b) every line of prose the operator wrote in a plan or a team document is still there
- (e) played again, steering and continuity refuse the instances they already filled, nothing written
- (c) once the cleanup's paths are gone: `team declaration` says ok, `pp-plan check` is clean,
  `pp-steering list` reads the steps, `pp-continuity recall` reads the operations
- (d) a step file that does not parse refuses the gesture by code, nothing written in any store, the
  files keep their bytes
- (f) the other refusals, each on its own house: `key-taken`, `records-unreadable` (a middle line),
  `team-intention`, `plan-unreadable`, `bus-unreadable` -- nothing written, no store filled
- the keys (T8): the steps' `key` and the bus's held lines move to `plan:`; a step's work or an
  operation that names an old key keeps its words; the torn last line has its own row in the counts
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from tests.harness import INSTANCE, support

import conductor
from conductor import store

old = support(__file__, "old_form")
sys.path.insert(0, str(old.MIGRATION.parent))
from _common import Refused, house as houses   # noqa: E402 -- `_common` lives beside the migrations

ORDER = ("plans", "plan-keys", "steering", "continuity", "teams")
OLD_KEYS = ("plan-lot:", "plan-phase:")
OLD_FRONT = ("kind:", "phase:")
PLANNED = ("PLAN.md", "PHASE.md", "BATCH.md")


def every(meta: Path, record: str) -> list:
    found, cursor = [], None
    kept = store.of(meta)
    while True:
        page = kept.read(record, order="asc", **({} if cursor is None else {"after": cursor}))
        found += page.rows
        if page.next is None:
            return found
        cursor = page.next["after"]


def played(gestures: dict, house, names=ORDER) -> tuple[list[tuple], list[str]]:
    """-> the count rows of the gestures named, and the codes of the ones that refused."""
    rows, refused = [], []
    for name in names:
        try:
            rows += list(gestures[name].gesture(house, conductor))
        except Refused as refusal:
            refused.append(refusal.code)
    return rows, refused


def texts(meta: Path) -> list[Path]:
    """-> the text files of an instance a reader of keys meets: its plans and its records but the store."""
    found = [one for one in (meta / "plans").rglob("*.md")] if (meta / "plans").is_dir() else []
    records = meta / ".sys" / "records"
    return found + [one for one in records.glob("*.json*") if one.is_file()]


def prose_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip() and not line.startswith("#")]


def merged(text: str, section: str) -> list[str]:
    """-> the lines of a section of a migrated document, its heading out."""
    lines = text.splitlines()
    start = lines.index(f"## {section}") + 1
    end = next((n for n in range(start, len(lines)) if lines[n].startswith("## ")), len(lines))
    return [line for line in lines[start:end] if line.strip()]


def fingerprint(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.parts and "engine" not in path.parts and "vendor" not in path.parts:
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def vendored(made: Path, package: str, script: str) -> Path:
    return next((made / ".sys" / "vendor").glob(f"{package}@*")) / "skills" / script / f"{script}.py"


def verb(made: Path, package: str, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(vendored(made, package, script)), *args], capture_output=True,
                          text=True, cwd=made.parent, stdin=subprocess.DEVNULL)


def scenario(bench) -> int:
    gestures = old.gestures()
    env = old.house(bench, "house")
    root, made, agent = env.root, env.made, env.root / old.AGENT / INSTANCE
    before_files = {meta: json.loads((meta / ".sys" / "records" / "steps.json").read_text(encoding="utf-8"))
                    for meta in (made, agent)}
    house = houses.read(root)
    before_docs = {path: path.read_text(encoding="utf-8")
                   for path in [one for plans in house.plans for one in plans.rglob("*.md") if one.name in PLANNED]
                   + [team / f"TEAM-{team.name}.md" for team in house.teams]}

    # (a) the gestures in their order
    rows, refused = played(gestures, house)
    unequal = [row for row in rows if row[2] != row[3]]
    records = {(Path(row[0]), row[1]) for row in rows}
    if not refused and rows and not unequal and {(made, "steps"), (agent, "steps"), (made, "operations"),
                                                 (agent, "history")} <= records:
        bench.held("counts", f"{len(rows)} rows, every count equal, both instances")
    else:
        bench.failures.append(f"  ✗ counts                      refused {refused}; unequal {unequal}; rows {rows}")
    stored = {meta: every(meta, "steps") for meta in (made, agent)}
    same = all([one.key for one in stored[meta]] == sorted(before_files[meta]["steps"], key=lambda s: int(s.split(".")[-1]))
               and all(one.body["name"] == before_files[meta]["steps"][one.key]["name"] for one in stored[meta])
               and store.of(meta).get("counters", "s").body["value"] == before_files[meta]["counters"]["s"]
               and [one.key for one in every(meta, "labels")] == list(before_files[meta]["labels"])
               for meta in (made, agent))
    operations = [one.body["entry"] for one in every(made, "operations")]
    if same and len(operations) == 3 and len(every(agent, "operations")) == 2 and len(every(made, "history")) == 1:
        bench.held("store", "steps, labels, counter, operations, history read back from the store")
    else:
        bench.failures.append(f"  ✗ store                       same {same}; operations {operations}")
    keys = [one.body["key"] for one in stored[made] if one.body["key"]]
    bus = json.loads((made / ".sys" / "records" / "events.json").read_text(encoding="utf-8"))
    held = [key for key, value in bus.items() if any(old in json.dumps([key, value]) for old in OLD_KEYS)]
    works = [one.body["work"] for one in stored[made]]
    entries = [one.body["entry"] for one in every(made, "operations")]
    if (keys == ["plan:memo/core/store", "plan:memo/core"] and not held and old.WORK_WITH_KEY in works
            and old.OPERATION_WITH_KEY in entries):
        bench.held("keys", "the steps' keys and the bus's held lines on `plan:`, the prose that names an old key kept")
    else:
        bench.failures.append(f"  ✗ keys                        {keys}; held lines left {held}; prose kept "
                              f"{old.WORK_WITH_KEY in works}, {old.OPERATION_WITH_KEY in entries}")
    named = gestures["continuity"].TORN.format(record="operations")
    torn = [row for row in rows if row[1].endswith(named.removeprefix("operations"))]
    if torn == [(made, named, 1, 1)]:
        bench.held("torn-line", "the torn last line skipped stands in the counts, its own row")
    else:
        bench.failures.append(f"  ✗ torn-line                   rows {torn}")
    fronts, sections = [], []
    for path in before_docs:
        if path.name not in PLANNED:
            continue
        text = path.read_text(encoding="utf-8")
        front = text.split("\n---\n", 1)[0].splitlines()
        if not any(line.startswith("template: ") for line in front) or any(line.startswith(OLD_FRONT) for line in front):
            fronts.append(path.name)
        if any(line.startswith(("## Target", "## Arbitrations", "## Decisions")) for line in text.splitlines()):
            sections.append(path.name)
        if path.name != "PLAN.md" and "## Context" in text.splitlines():
            sections.append(path.name)
    if not fronts and not sections:
        bench.held("plan-forms", f"{sum(p.name in PLANNED for p in before_docs)} documents on `template:`, "
                                 "no section of the old templates")
    else:
        bench.failures.append(f"  ✗ plan-forms                  fronts {fronts}; sections {sections}")
    batch = next(path for path in before_docs if path.name == "BATCH.md").read_text(encoding="utf-8")
    expected = merged(batch, "Expected")
    native, title, moved = old.PROSE["batch"]["Expected"][0], "### Target", old.PROSE["batch"]["Target"][0]
    if native in expected and title in expected and moved in expected and (
            expected.index(native) < expected.index(title) < expected.index(moved)):
        bench.held("merge-after", "a merged section: its own text first, then the old section under its title")
    else:
        bench.failures.append(f"  ✗ merge-after                 {expected}")

    # (b) the operator's prose kept
    lost = []
    for path, text in before_docs.items():
        after = path.read_text(encoding="utf-8") if path.is_file() else ""
        if path.name.startswith("TEAM-"):
            after = (path.parent / "TEAM.md").read_text(encoding="utf-8")
            wanted = [line for line in old.INTENTION if line.strip()]
        else:
            kind = {"PLAN.md": "plan", "PHASE.md": "phase", "BATCH.md": "batch"}.get(path.name)
            prose = old.SHARED if "shared" in path.parts else old.PROSE.get(kind, {})
            wanted = [line for lines in prose.values() for line in lines]
        lost += [f"{path.name}: {line}" for line in wanted if line not in prose_lines(after)]
    if not lost:
        bench.held("prose-kept", "every line the operator wrote stands after the gestures")
    else:
        bench.failures.append(f"  ✗ prose-kept                  lost {lost}")

    # (e) played again
    print_before = fingerprint(root)
    counted = {meta: (store.of(meta).count("steps"), store.of(meta).count("operations")) for meta in (made, agent)}
    _, again = played(gestures, houses.read(root), ("steering", "continuity"))
    if (len(again) == 2 and fingerprint(root) == print_before
            and counted == {meta: (store.of(meta).count("steps"), store.of(meta).count("operations"))
                            for meta in (made, agent)}):
        bench.held("replayed", f"refused {again}, nothing written")
    else:
        bench.failures.append(f"  ✗ replayed                    refused {again}; counts {counted}")

    # (c) the cleanup's paths gone, the verbs of the arrival version read the house
    paths = [Path(one) for one in gestures["cleanup"].cleanup(houses.read(root))]
    for path in paths:
        path.unlink()
    gone = {path.name for path in paths}
    kept_door = (root / "AGENTS.md").is_file() and not (root / "CLAUDE.md").exists()
    declared = env.cli("team", "declaration", old.TEAM, "--json")
    verdict = json.loads(declared.stdout).get("verdict", {}) if declared.returncode == 0 else {}
    checked = verb(made, "plan", "pp-plan", "check")
    listed = verb(made, "steering", "pp-steering", "list", "--json")
    recalled = verb(made, "continuity", "pp-continuity", "recall", "last", "60")
    if ({"operations.jsonl", "history.jsonl", "steps.json", "system.common.md", f"TEAM-{old.TEAM}.md"} <= gone
            and kept_door and verdict.get("ok") and checked.returncode == 0 and listed.returncode == 0
            and recalled.returncode == 0):
        bench.held("verbs", "team declaration ok, pp-plan check clean, steering and continuity read")
    else:
        bench.failures.append(f"  ✗ verbs                       gone {sorted(gone)}; door kept {kept_door}; "
                              f"declaration {declared.returncode} {verdict}; check {checked.returncode} "
                              f"{checked.stderr.strip()[-300:]}; list {listed.returncode} {listed.stderr.strip()[-200:]}; "
                              f"recall {recalled.returncode} {recalled.stderr.strip()[-200:]}")

    # (d) a step file that does not parse
    env = old.house(bench, "torn")
    root, made, agent = env.root, env.made, env.root / old.AGENT / INSTANCE
    steps = agent / ".sys" / "records" / "steps.json"
    lines = steps.read_text(encoding="utf-8").splitlines()
    steps.write_text("\n".join(lines[:4] + ["}{"] + lines[4:]) + "\n", encoding="utf-8")
    print_before = fingerprint(root)
    _, refused = played(gestures, houses.read(root), ("steering",))
    if (refused == ["steps-unreadable"] and fingerprint(root) == print_before
            and not any(store.of(meta).count("steps") for meta in (made, agent))):
        bench.held("steps-unreadable", "refused by code, no store written, the files keep their bytes")
    else:
        bench.failures.append(f"  ✗ steps-unreadable            refused {refused}")

    # (f) every other refusal of a gesture: nothing written for the instance it refuses (KB2)
    for code, gesture, spoil in REFUSALS:
        env = old.house(bench, code)
        root, made, agent = env.root, env.made, env.root / old.AGENT / INSTANCE
        spoil(root, made, agent)
        print_before = fingerprint(root)
        _, refused = played(gestures, houses.read(root), (gesture,))
        if refused == [code] and fingerprint(root) == print_before and not any(
                store.of(meta).count(record) for meta in (made, agent) for record in ("steps", "operations")):
            bench.held(code, "refused by code, nothing written, no store filled")
        else:
            bench.failures.append(f"  ✗ {code:<28}refused {refused}")
    return 0


def key_taken(root: Path, made: Path, agent: Path) -> None:
    """A step already keyed where an old key lands."""
    path = made / ".sys" / "records" / "steps.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    sid, one = old.step(4, "house", "taken", "plan:memo/core")
    record["steps"][sid] = one
    record["counters"]["s"] = 4
    path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")


def records_unreadable(root: Path, made: Path, agent: Path) -> None:
    """A line in the middle of the agent's operations that is no entry."""
    path = agent / ".sys" / "records" / "operations.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    path.write_text("\n".join(lines[:1] + ["{not an entry"] + lines[1:]) + "\n", encoding="utf-8")


def team_intention(root: Path, made: Path, agent: Path) -> None:
    """A TEAM.md whose body the owner already wrote, other than TEAM-<name>.md's."""
    path = root / "teams" / old.TEAM / "TEAM.md"
    path.write_text(path.read_text(encoding="utf-8") + "\nThe owner's own word.\n", encoding="utf-8")


def plan_unreadable(root: Path, made: Path, agent: Path) -> None:
    """A plan document without its front."""
    path = next((made / "plans").rglob("BATCH.md"))
    path.write_text(path.read_text(encoding="utf-8").split("\n---\n", 1)[1], encoding="utf-8")


def bus_unreadable(root: Path, made: Path, agent: Path) -> None:
    (made / ".sys" / "records" / "events.json").write_text("{", encoding="utf-8")


REFUSALS = (("key-taken", "plan-keys", key_taken), ("records-unreadable", "continuity", records_unreadable),
            ("team-intention", "teams", team_intention), ("plan-unreadable", "plans", plan_unreadable),
            ("bus-unreadable", "plan-keys", bus_unreadable))
