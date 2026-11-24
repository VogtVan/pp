"""The records of the house: the one reader and the one writer of its `.jsonl` files and of a run's flow file."""
from __future__ import annotations

import json
import os
from pathlib import Path

from model.cost import Cumuls
from model.exchange import Message, Response
from model.material import Workdir
from model.policy import Asked, Policy
from model.run import Session, Naming
from model.vector import Keeping
from model.words import RESPONSES, MESSAGES, SESSIONS, NAMES, WORKDIRS, VECTORS, EMPTIED, PURGED
from store.clock import now
from store.houses import bootstrap
from store.refusal import refuse
from store.traces import engine_purge_of

FLOWS = "flows"                 # under the house's records: one file per run, every event its exchanges said


def record(root: Path, name: str) -> Path:
    return root / ".sys" / "records" / name


_READ: dict[Path, tuple[tuple[int, int], list[dict]]] = {}   # each record read in this process, by its size and last write
_MADE: dict[tuple[Path, object], tuple[tuple[int, int], list]] = {}   # each record's lines made into objects, by its state
_RUNS: dict[tuple[Path, object, str], tuple[tuple[int, int], dict]] = {}   # those objects grouped by agent and run


def lines_of(path: Path) -> list[dict]:
    """-> the record's lines, oldest first, a list of the caller's own. A LAST line that does not
    parse is a writer still writing it and is skipped; one anywhere else is a hand in the file and
    refuses. A record unchanged since this process last read it -- the same size, the same last
    write -- is not read again."""
    if not path.is_file():
        return []
    seen = path.stat()
    mark = (seen.st_size, seen.st_mtime_ns)
    kept = _READ.get(path)
    if kept is not None and kept[0] == mark:
        return list(kept[1])
    raw = path.read_text(encoding="utf-8").splitlines()
    found = []
    for number, line in enumerate(raw, 1):
        if not line.strip():
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            if number == len(raw):
                continue
            refuse(f"line {number} of {path.name} is not a record -- this script is the "
                   "only writer, the file is not for hand edits.")
    _READ[path] = (mark, found)
    return list(found)


def state_of(path: Path) -> tuple[int, int] | None:
    """-> the state of a record -- its size and its last write --, None when it does not stand."""
    if not path.is_file():
        return None
    seen = path.stat()
    return seen.st_size, seen.st_mtime_ns


def made_of(path: Path, make) -> list:
    """-> the record's lines made into objects by `make`, oldest first, a list of the caller's own: each line is
    made ONCE per state of the record in this process, so a face that reads every run of a house makes every line
    once, not once per run. The objects are frozen: the lists share them."""
    mark = state_of(path)
    if mark is None:
        return []
    kept = _MADE.get((path, make))
    if kept is None or kept[0] != mark:
        kept = (mark, [make(one) for one in lines_of(path)])
        _MADE[(path, make)] = kept
    return list(kept[1])


def of_runs(path: Path, make, holder: str) -> dict[tuple[str, str], list]:
    """-> the objects of a record grouped by `(<holder>, run)`, oldest first in each group -- `holder` the field that
    names the agent (`agent` on a response, `to` on a message) --, grouped once per state of the record."""
    made = made_of(path, make)
    mark = state_of(path)
    kept = _RUNS.get((path, make, holder))
    if kept is None or kept[0] != mark:
        grouped: dict[tuple[str, str], list] = {}
        for one in made:
            grouped.setdefault((getattr(one, holder), one.run), []).append(one)
        kept = (mark, grouped)
        _RUNS[(path, make, holder)] = kept
    return kept[1]


def append(path: Path, entry: dict) -> None:
    """Appends ONE line under the record's lock: two wake-ups never mix their lines."""
    core, _ = bootstrap()
    path.parent.mkdir(parents=True, exist_ok=True)
    with core(__file__).record.held(path):
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def every_session(root: Path) -> list[Session]:
    """-> every session the house recorded, oldest first."""
    return made_of(record(root, SESSIONS), Session.of)


def session_of_run(root: Path, name: str, key: str) -> Session | None:
    """-> the run's last line at `sessions.jsonl` -- its provider and its session -- or None."""
    found = [one for one in every_session(root) if one.agent == name and one.run == key]
    return found[-1] if found else None


def name_of(root: Path, name: str, key: str) -> str:
    """-> the run's name, the last line of `names.jsonl` for it -- '' when none was given."""
    found = [one for one in map(Naming.of, lines_of(record(root, NAMES))) if one.agent == name and one.run == key]
    return str(found[-1].name or "") if found else ""


def cumuls_of(root: Path, name: str, key: str) -> Cumuls:
    """-> what the records say of a run, summed: the responses, the cost (the sum of the
    numeric `cost_usd`, None when none), the launches, the overruns, the first message and its hour, the
    hour of the last line of either record."""
    answered = answered_by(root, name, key)
    sent = sent_to(root, name, key)
    costs = [one.cost_usd for one in answered if isinstance(one.cost_usd, (int, float))]
    launches = [one.launches for one in answered if isinstance(one.launches, int)]
    overruns = [one.overruns for one in answered if isinstance(one.overruns, int)]
    ats = [str(one.at) for one in answered + sent if one.at]
    return Cumuls(responses=len(answered),
                  cost_usd=round(sum(costs), 6) if costs else None,
                  launches=sum(launches),
                  overruns=sum(overruns),
                  first_message=str(sent[0].message) if sent else None,
                  first_at=str(sent[0].at) if sent and sent[0].at else None,
                  last_at=max(ats) if ats else None)


def spent_of(root: Path, name: str, key: str | None) -> float:
    """-> what the run spent so far: the sum of the `cost_usd` of its responses, 0 for a run not yet opened
    or whose costs are unknown."""
    return float(cumuls_of(root, name, key).cost_usd or 0.0) if key is not None else 0.0


def resume_of(conductor, root: Path, meta: Path, name: str, key: str) -> tuple[bool, Session | None]:
    """-> (whether the run stands, its last session recorded): the records are read for a run that stands alone."""
    if not conductor.persistence.slot_of(meta, key).is_file():
        return False, None
    return True, session_of_run(root, name, key)


def run_was(conductor, root: Path, name: str, key: str | None) -> tuple[Session | None, list[str], Policy]:
    """-> what a resume reads of what the RUN was: its last session, the providers the house is wired with, the
    policy of its last message (the `policy` of its last line at `messages.jsonl`); without a run, or without
    a session recorded, nothing more is read."""
    known = session_of_run(root, name, key) if key else None
    if known is None:
        return None, [], Policy()
    wired = conductor.install.wired_providers(root.parent)
    sent = sent_to(root, name, key)
    return known, wired, sent[-1].policy if sent else Policy()


def flow_of(root: Path, name: str, key: str) -> Path:
    """-> the flow file of the run `key` of the agent `name`: `flows/<digest of its path>/<key>.jsonl`."""
    import hashlib
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:12]
    return record(root, FLOWS) / digest / f"{key}.jsonl"


def vectors_of(root: Path, name: str, key: str | None) -> list[str]:
    """-> the vectors the run keeps, in the order they came: the last line of `vectors.jsonl` for it,
    [] for a run that keeps none and without a run."""
    if key is None:
        return []
    found = [one for one in map(Keeping.of, lines_of(record(root, VECTORS))) if one.agent == name and one.run == key]
    return [str(one) for one in (found[-1].vectors or [])] if found else []


def vectors_due(root: Path, name: str, key: str | None, asked: Asked) -> list[str]:
    """-> the vectors an exchange of the run mounts: the `--vector` of this wake-up when it gives any -- they
    REPLACE the set the run keeps, each once, in the order given; `-` alone empties it --, the set the run
    keeps otherwise."""
    given = [str(one) for one in asked.vector or []]
    if not given:
        return vectors_of(root, name, key)
    if given == [EMPTIED]:
        return []
    return list(dict.fromkeys(given))


def vectors_kept(root: Path, name: str, key: str, vectors: list[str]) -> None:
    """The run KEEPS the vectors of its exchange: one line of `vectors.jsonl` when the set moved -- replaced
    or emptied by this wake-up's `--vector` --, nothing otherwise."""
    if vectors != vectors_of(root, name, key):
        append(record(root, VECTORS), Keeping(at=now(), agent=name, run=key, vectors=vectors).json())


def every_response(root: Path) -> list[Response]:
    """-> every response the house recorded, oldest first."""
    return made_of(record(root, RESPONSES), Response.of)


def every_message(root: Path) -> list[Message]:
    """-> every message the house sent, oldest first."""
    return made_of(record(root, MESSAGES), Message.of)


def answered_by(root: Path, name: str, key: str) -> list[Response]:
    """-> the responses of the run `key`, oldest first."""
    return list(of_runs(record(root, RESPONSES), Response.of, "agent").get((name, key), ()))


def sent_to(root: Path, name: str, key: str) -> list[Message]:
    """-> the messages sent to the run `key`, oldest first."""
    return list(of_runs(record(root, MESSAGES), Message.of, "to").get((name, key), ()))


def every_workdir(root: Path) -> list[Workdir]:
    """-> every state of a material the house recorded, oldest first."""
    return [Workdir.of(one) for one in lines_of(record(root, WORKDIRS))]


def workdir_of(root: Path, name: str, key: str) -> Workdir | None:
    """-> the last line of `workdirs.jsonl` for the run: its material's state, or None."""
    found = [one for one in every_workdir(root) if one.agent == name and one.run == key]
    return found[-1] if found else None


def material_kept(root: Path, name: str, meta: Path, key: str) -> tuple[Workdir | None, bool]:
    """-> (the run's material as recorded, None when it has none; whether its clone stands under the agent)."""
    entry = workdir_of(root, name, key)
    return entry, entry is not None and (meta.parent / str(entry.path)).is_dir()


def of_run(one: dict, name: str, key: str) -> bool:
    """Whether a record's line belongs to the run `key` of the agent `name` (`to` names it on `messages`)."""
    return one.get("run") == key and (one.get("agent") == name or one.get("to") == name)


def rewritten_without(path: Path, name: str, key_set: set) -> None:
    """Rewrites a record WITHOUT the lines of the runs `key_set` of the agent `name`, under the record's
    lock: a temporary beside it, then one rename -- every other line kept to the byte. The one write of a
    record that is not an append: `purge` alone plays it."""
    core, _ = bootstrap()
    if not path.is_file():
        return
    with core(__file__).record.held(path):
        kept = []
        for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
            try:
                one = json.loads(line)
            except ValueError:
                kept.append(line)
                continue
            if not (isinstance(one, dict) and one.get("run") in key_set
                    and (one.get("agent") == name or one.get("to") == name)):
                kept.append(line)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.purge")
        temporary.write_text("".join(kept), encoding="utf-8")
        os.replace(temporary, path)


def weights_of(conductor, root: Path, name: str, meta: Path, keys: list[str]) -> dict:
    """-> {key: {lines, files, bytes, flow}}: what a purge of each run would count -- the lines of the six
    records that carry it, the files the engine keeps of it (`state.purge.files_of`: `session-<key>.*` and
    the traces of its key, the table of the traces' keys read once), their bytes, and the bytes of its flow
    file (`null` without one). Reads only."""
    engine_purge = engine_purge_of(conductor)
    found = {record_name: lines_of(record(root, record_name)) for record_name in PURGED}
    state = meta / conductor.persistence.DIRECTORY
    keyed = engine_purge.traces.keys_of(state) if state.is_dir() else {}
    weights = {}
    for key in keys:
        own = set(state.glob(f"session-{key}.*")) if state.is_dir() else set()
        own |= {state / trace for trace, run in keyed.items() if run == key}
        files = [path for path in own if path.is_file()]
        kept_flow = flow_of(root, name, key)
        weights[key] = {"lines": sum(1 for lines in found.values() for one in lines if of_run(one, name, key)),
                        "files": len(files), "bytes": sum(path.stat().st_size for path in files),
                        "flow": kept_flow.stat().st_size if kept_flow.is_file() else None}
    return weights


def last_played(root: Path, name: str, sent: list[Message]) -> tuple[str | None, Policy] | None:
    """-> what the agent's last run played: (the provider of its last session -- `harness` for a caller's
    command, None without a session --, the policy of its last message), all runs taken together;
    None when no message was ever sent to it."""
    if not sent:
        return None
    sessions = [one for one in every_session(root) if one.agent == name]
    provider = (sessions[-1].provider or "harness") if sessions else None
    return provider, sent[-1].policy
