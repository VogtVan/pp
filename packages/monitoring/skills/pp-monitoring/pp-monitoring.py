#!/usr/bin/env python3
"""pp-monitoring -- the analyses of the measure: setup, run, report, list.

  pp-monitoring.py setup <name> <repo> <playbook>
  pp-monitoring.py setup <name> <archive-dir>   an ARCHIVE: the traces a campaign left, read back
  pp-monitoring.py derive <dir>          a disposable repo from THIS instance (pins, settings)
  pp-monitoring.py run <name>
  pp-monitoring.py report <name>
  pp-monitoring.py list
  pp-monitoring.py wire <provider>       write the harness link (claude only, never overwrites)
  pp-monitoring.py stamp                 the hook's target: silent while the switch is off

The record `monitoring.json` is this skill's own; the MEASURE is the engine's --
this script drives a declared repo's console through a scripted session and
reads the traces the engine wrote -- or reads them back from the ARCHIVE a campaign
left, with the same grammar. `run` is gated by `monitoring_capture`.
Guards refuse by name, exit 2, nothing written. No network, ever.

documentary: the driven repo is addressed through its OWN console (`pp.py -new`,
then the key), never through an import -- two engines never share one process,
and the same drive will work on any instance an operator declares.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

RECORD = "monitoring.json"
NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,59}$")
BUDGET = 20                       # analyses one record holds -- a roster, not a lake
ADVANCES = 12                     # bare advances per exchange before the drive gives up


def refuse(code: str, detail: str) -> None:
    print(f"pp-monitoring: {code} -- {detail}", file=sys.stderr)
    raise SystemExit(2)


def home() -> Path:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from _core import home as walk                        # noqa: E402 -- the bootstrap
    root = walk(__file__)
    if root is None:
        refuse("not-an-instance", "no .sys/instance.yaml above this skill")
    return root


def engine():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from _core import core                                # noqa: E402 -- the bootstrap
    return core(__file__)


def record_path(root: Path) -> Path:
    return root / ".sys" / "records" / RECORD


def held(root: Path) -> dict:
    path = record_path(root)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        refuse("record-corrupt", f"{path} is not JSON -- restore it from your VCS")


def meta_of(path: Path) -> Path | None:
    """-> the instance meta at or under `path` -- the declared repo's home."""
    if (path / ".sys" / "instance.yaml").is_file():
        return path
    for child in sorted(path.iterdir()) if path.is_dir() else []:
        if child.is_dir() and (child / ".sys" / "instance.yaml").is_file():
            return child
    return None


def capture_armed(root: Path) -> bool:
    face = engine().settings
    value = face.of(root).of_package("monitoring_capture", False)
    return value is True or str(value).strip().lower() == "true"


@dataclass(frozen=True)
class Source:
    """Where an analysis READS: a LIVE instance -- its state directory, the harness's own
    transcripts -- or an ARCHIVE directory holding what a campaign left (`session-*.jsonl`
    beside a `transcripts/` folder, `SETTINGS.md` and `instance.yaml` when the archive kept
    them). One reader, two homes: a figure never depends on where the traces stand.

    documentary: a campaign is archived at its witness batch and read back from there at
    any later date -- declared once over the directory, then reported like a live run."""
    home: Path
    archived: bool = False

    @classmethod
    def of(cls, entry: dict) -> "Source":
        if "archive" in entry:
            return cls(Path(entry["archive"]), True)
        return cls(Path(entry["repo"]), False)

    @property
    def traces(self) -> list[Path]:
        where = self.home if self.archived else self.home / ".sys" / "state"
        return sorted(where.glob("session-*.jsonl")) if where.is_dir() else []

    @property
    def transcripts(self) -> list[Path]:
        """-> the harness transcripts paired to the traces, oldest first: an archive keeps
        them beside its traces; a live instance's live at the harness (claude: at
        ~/.claude/projects/<workspace path with / as ->/ -- provider knowledge)."""
        if self.archived:
            return sorted((self.home / "transcripts").glob("*.jsonl"), key=_first_ts)
        slug = str(self.home.parent.resolve()).replace("/", "-")
        found = Path.home() / ".claude" / "projects" / slug
        if not found.is_dir():
            return []
        return sorted(found.glob("*.jsonl"), key=lambda one: one.stat().st_mtime)

    @property
    def manifest(self) -> Path:
        return self.home / ("instance.yaml" if self.archived else ".sys/instance.yaml")

    @property
    def settings(self) -> Path:
        return self.home / "SETTINGS.md"


def _first_ts(path: Path):
    """-> the first row timestamp of a transcript, the order an archive's copies keep
    (a copy's mtime says nothing of the session)."""
    with path.open(encoding="utf-8", errors="ignore") as lines:
        for line in lines:
            try:
                ts = _ts(json.loads(line).get("timestamp"))
            except (json.JSONDecodeError, AttributeError):
                continue
            if ts is not None:
                return ts
    return datetime.max.replace(tzinfo=timezone.utc)


NEUTRAL_MEMBER = """---
name: AGENT
kind: proc
description: >-
  This agent's identity -- the derived repo's neutral member: the playbooks
  judge the COMPOSITION, never a role.
character: >-
  cooperative, honest, helpful, and respectful
constraints.behavior: |
  M1  your name is @MEMBER.name
  M2  you must behave like this: @MEMBER.character
tools: |
  CAPABILITIES
proc: |
  CALL CAPABILITIES.md
  CALL TURN.md
---

A neutral member, derived for the measure.
"""


def playbook(path: Path) -> dict:
    """-> {composition: [...], sessions: [{heading, fixture, gestures: [...]}]} -- the
    codified grammar of refs/PLAYBOOK.md, parsed; a book without one session refuses by
    name. The id names the ROW; the gesture is the operator message exactly as typed --
    it never carries the id: play is deterministic, table order, sessions in book order."""
    if not path.is_file():
        refuse("scenario-missing", f"{path} does not exist")
    composition: list[str] = []
    sessions: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("composition:") and not sessions:
            composition = stripped.split(":", 1)[1].split()
        elif stripped.startswith("## "):
            sessions.append({"heading": stripped[3:], "fixture": "", "gestures": []})
        elif stripped.startswith("shell:") and sessions and not sessions[-1]["gestures"]:
            sessions[-1]["fixture"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("|") and sessions:
            cells = [one.strip() for one in stripped.strip("|").split("|")]
            if len(cells) >= 2 and cells[0] not in ("id", "") and not set(cells[0]) <= {"-"}:
                sessions[-1]["gestures"].append(cells[1])
    if not any(one["gestures"] for one in sessions):
        refuse("scenario-missing", f"{path} holds no session with gestures")
    return {"composition": composition, "sessions": sessions}


def pinned(meta: Path) -> set[str]:
    """-> the packages the instance's pins carry (instance.yaml, read lightly)."""
    import re as re_
    text = (meta / ".sys" / "instance.yaml").read_text(encoding="utf-8")
    block = re_.search(r"^packages:\n((?:[ \t]+\S+:.*\n?)+)", text, re_.M)
    return {line.split(":")[0].strip() for line in block.group(1).splitlines()} if block else set()


def derive(root: Path, target: str, fusion: str | None = None) -> int:
    """The disposable repo, derived from THIS instance: the engine and the pins
    copied whole, the operator's SETTINGS and FORMATS with them, a NEUTRAL member,
    records and state born empty -- never the instance itself."""
    import shutil
    where = Path(target).expanduser().resolve()
    if where.exists() and any(where.iterdir()):
        refuse("target-not-empty", f"{where} exists and holds files")
    meta = where / root.name
    sys_root = root / ".sys"

    def _skip(directory, names):
        # records and state stay behind only at the .sys ROOT -- deeper directories
        # of those names (conductor/state) travel whole
        top = Path(directory) == sys_root
        return [one for one in names
                if one == "__pycache__" or (top and one in ("records", "state"))]

    shutil.copytree(sys_root, meta / ".sys", ignore=_skip)
    (meta / ".sys" / "records").mkdir()
    (meta / ".sys" / "state").mkdir()
    for name in ("SETTINGS.md", "FORMATS.md"):
        if (root / name).is_file():
            shutil.copy2(root / name, meta / name)
    (meta / "MEMBER.md").write_text(NEUTRAL_MEMBER, encoding="utf-8")
    if fusion is not None:
        # borne B: a granularity pass -- `fusion: none` renders ONE output per step, so an
        # interval per step; the report says the regime, never feigns the granularity
        import re as re_
        s = (meta / "SETTINGS.md")
        s.write_text(re_.sub(r"^instructions_fusion: .*$", f"instructions_fusion: {fusion}",
                             s.read_text(encoding="utf-8"), flags=re_.M), encoding="utf-8")
    print(f"pp-monitoring: derived -- {meta} (pins and settings copied, member neutral, "
          f"records empty{', fusion=' + fusion if fusion else ''})")
    return 0


def _ts(raw):
    """-> the aware datetime of a transcript row's `timestamp` (ISO, trailing Z), or None."""
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


# an op message precedes its turn's first pp call by seconds; a dead run in the same
# workspace sits well outside the live window -- this margin lets the first real message
# in without letting an invalidated run's tail bleed in.
_WINDOW_MARGIN = 120  # seconds


def _live_window(source: Source):
    """-> (first, last) aware datetimes spanning the source's traces (the live state, or
    the archive's copies), or None when there are none (a mechanical run leaves its trace
    elsewhere). The transcript readers bound to this window, so an INVALIDATED run left in
    the same workspace's Claude log never mislabels a live turn nor bleeds into the conduite."""
    from datetime import timedelta
    times = []
    for path in source.traces:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                at = _at(json.loads(line))
            except json.JSONDecodeError:
                continue
            if at is not None:
                times.append(at)
    if not times:
        return None
    margin = timedelta(seconds=_WINDOW_MARGIN)
    return (min(times) - margin, max(times) + margin)


def _settings_of(source: Source) -> dict[str, str]:
    """-> the keys the source's SETTINGS.md front matter spells, as written -- {} when the
    source carries none (an archive that kept no settings says nothing, never a default)."""
    keys: dict[str, str] = {}
    in_front = False
    if source.settings.is_file():
        for line in source.settings.read_text(encoding="utf-8").splitlines():
            if line.strip() == "---":
                if in_front:
                    break
                in_front = True
            elif (in_front and ":" in line and not line.startswith((" ", "#"))
                  and not line.startswith(("name:", "kind:", "description:"))):
                key, value = line.split(":", 1)
                keys[key.strip()] = value.strip()
    return keys


def _header(source: Source) -> list[str]:
    """The header every result opens on: the measured pins, the LLM read from the
    paired transcripts (`unknown` said, never guessed), the settings played --
    documentary: a figure without its provenance steers nobody (operator word). An
    archive says its directory first; what it did not keep is said unknown."""
    versions, origin, in_packages = [], "", False
    manifest = source.manifest
    if manifest.is_file():
        for line in manifest.read_text(encoding="utf-8").splitlines():
            if line.startswith("source:"):
                origin = line.split(":", 1)[1].strip()
            elif line.startswith("engine:"):
                versions.append("engine " + line.split(":", 1)[1].strip())
            elif line.startswith("packages:"):
                in_packages = True
            elif in_packages and line.startswith("  ") and ":" in line:
                versions.append(line.strip().replace(":", ""))
            else:
                in_packages = False
    models: dict[str, int] = {}
    efforts: dict[str, int] = {}
    window = _live_window(source)   # count the LLM/effort of the live run only, not a dead one
    for transcript in source.transcripts:
        for line in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
            if window is not None:
                try:
                    ts = _ts(json.loads(line).get("timestamp"))
                except json.JSONDecodeError:
                    ts = None
                if ts is not None and not (window[0] <= ts <= window[1]):
                    continue
            for hit in re.findall(r'"model":"([^"]+)"', line):
                models[hit] = models.get(hit, 0) + 1
            for hit in re.findall(r'"effort":"([^"]+)"', line):
                efforts[hit] = efforts.get(hit, 0) + 1
    def _mix(counts: dict[str, int]) -> str:
        # EVERY distinct value in the live window, the dominant first with its share -- a
        # campaign may span models (the operator switches mid-run); a bare majority lies.
        if not counts:
            return "unknown"
        ranked = sorted(counts, key=lambda one: -counts[one])
        return ranked[0] if len(ranked) == 1 else " + ".join(f"{one} ({counts[one]})" for one in ranked)
    # the LLM(s) and the effort level(s), read from the paired transcripts; unknown is said
    llm = _mix(models) + " -- effort " + _mix(efforts)
    keys = [f"{key}: {value}" for key, value in _settings_of(source).items()]
    return ([f"  header   archive  {source.home}"] if source.archived else []) + [
            f"  header   source   {origin or 'unknown'}",
            f"  header   versions {' / '.join(versions) or 'unknown'}",
            f"  header   llm      {llm}",
            f"  header   settings {' / '.join(keys) or 'unknown'}"]


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(one.get("text", "") for one in content if isinstance(one, dict))
    return ""


def conduite(root: Path, name: str) -> int:
    """The CONDUITE: a DETERMINISTIC concatenation of conduction and chat, in transcript
    order -- the operator's messages, the `pp` calls and their FULL output, the agent's
    chat, verbatim. No headings, no numbering, no prose, no interpretation: the raw
    interleaved stream a script produces, nothing an author adds (operator word 2026-09-03).
    Claude provider only. -> printed text."""
    state = held(root)
    if name not in state:
        refuse("analysis-unknown", f"`{name}` -- declare it with setup")
    source = Source.of(state[name])
    transcripts = source.transcripts
    if not transcripts:
        refuse("transcript-missing",
               f"no Claude transcript at {source.home / 'transcripts'}" if source.archived
               else f"no Claude transcript for {source.home.parent} -- the conduite reads the harness's own log")
    window = _live_window(source)   # the campaign's live span -- an invalidated run is excluded
    rows = []
    for transcript in transcripts:
        for line in transcript.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if window is not None:
                ts = _ts(row.get("timestamp"))
                if ts is not None and not (window[0] <= ts <= window[1]):
                    continue          # outside the live campaign -- a dead run's row
            rows.append(row)
    out: list[str] = []
    for row in rows:
        kind, message = row.get("type"), row.get("message", {})
        if kind == "user":
            content = message.get("content")
            if isinstance(content, list):
                for one in content:
                    if one.get("type") == "text":
                        text = one.get("text", "").rstrip()
                        if text and not text.startswith(("<", "Caveat")):
                            out += ["op> " + text, ""]
                    elif one.get("type") == "tool_result":
                        block = _text(one.get("content", "")).rstrip()
                        if block:
                            out += [block, ""]
            else:
                text = _text(content).rstrip()
                if text and not text.startswith(("<", "Caveat")):
                    out += ["op> " + text, ""]
        elif kind == "assistant":
            for one in message.get("content", []):
                if one.get("type") == "tool_use" and one.get("name") == "Bash":
                    cmd = one.get("input", {}).get("command", "")
                    if "pp" in cmd:
                        out += ["$ " + cmd, ""]
                elif one.get("type") == "text" and one.get("text", "").strip():
                    out += [one["text"].rstrip(), ""]
    print("\n".join(out))
    return 0


# --- the verbs -----------------------------------------------------------------------

def setup(root: Path, name: str, repo: str, scenario: str) -> int:
    if not NAME.match(name):
        refuse("name-invalid", "an analysis name is kebab-case, 60 characters at most")
    meta = meta_of(Path(repo).expanduser().resolve())
    if meta is None:
        refuse("repo-not-instance", f"no .sys/instance.yaml at or under {repo}")
    script = Path(scenario).expanduser().resolve()
    book = playbook(script)                 # the codified grammar, refused by name early
    core = engine()
    with core.record.held(record_path(root)):
        state = held(root)
        if name in state:
            refuse("analysis-taken", f"`{name}` is declared -- report or re-setup under another name")
        if len(state) >= BUDGET:
            refuse("budget", f"{BUDGET} analyses at most -- retire one first")
        state[name] = {"repo": str(meta), "scenario": str(script),
                       "packages": sorted(book["composition"]),
                       "declared_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        core.record.replace(record_path(root), json.dumps(state, indent=1, ensure_ascii=False))
    print(f"pp-monitoring: declared -- {name} over "
          f"{', '.join(sorted(book['composition'])) or 'the composition'}, "
          f"{len(book['sessions'])} session(s)")
    return 0


def setup_archive(root: Path, name: str, archive: str) -> int:
    """An analysis declared over an ARCHIVE: the directory a campaign left its traces in
    (`session-*.jsonl` directly under it). Read only -- reported, never run."""
    if not NAME.match(name):
        refuse("name-invalid", "an analysis name is kebab-case, 60 characters at most")
    where = Path(archive).expanduser().resolve()
    if not Source(where, True).traces:
        refuse("archive-empty", f"no session-*.jsonl directly under {where}")
    core = engine()
    with core.record.held(record_path(root)):
        state = held(root)
        if name in state:
            refuse("analysis-taken", f"`{name}` is declared -- report or re-setup under another name")
        if len(state) >= BUDGET:
            refuse("budget", f"{BUDGET} analyses at most -- retire one first")
        state[name] = {"archive": str(where),
                       "declared_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
        core.record.replace(record_path(root), json.dumps(state, indent=1, ensure_ascii=False))
    print(f"pp-monitoring: declared -- {name} over the archive {where}, "
          f"{len(Source(where, True).traces)} trace(s)")
    return 0


def _console(meta: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(meta / ".sys" / "engine" / "pp.py"), *args],
                          capture_output=True, text=True, cwd=str(meta.parent), input=stdin)


def _mechanical_proof(out: str) -> str | None:
    """-> the proof a MECHANICAL run pipes at a checkpoint, or None when none stands:
    every code the block names (`INFER proof [A1 B2 ...]`) said n/a -- the drive
    produced nothing worth judging, and a checkpoint has no skip (operator word
    2026-09-05): the proof is rendered from the block, never dodged."""
    named = re.search(r"INFER proof \[([^\]]*)\]", out)
    if named is None:
        return None
    codes = named.group(1).split()
    return json.dumps([{"code": code, "evidence": "mechanical run -- nothing to judge",
                        "verdict": "n/a"} for code in codes] or
                      [{"code": "none", "evidence": "no code named", "verdict": "n/a"}])


def _drive(meta: Path, messages: list[str]) -> None:
    """One exchange per message on the TARGET's console: minimal plausible answers --
    `none` to a consumed line, an all-n/a proof at a checkpoint, the bare advance elsewhere."""
    state = meta / ".sys" / "state"
    before = set(state.glob("session-*.json")) if state.is_dir() else set()
    opened = _console(meta, "-new")
    if opened.returncode != 0:
        refuse("target-refused", f"-new on {meta}: {opened.stderr.strip()[-200:]}")
    born = sorted(set(state.glob("session-*.json")) - before)
    if not born:
        refuse("target-refused", f"-new on {meta} left no run slot")
    key = born[-1].stem.replace("session-", "")
    for message in messages:
        out = _console(meta, key, message).stdout
        for _ in range(ADVANCES):
            if "▶ FINAL" in out or "(once the operator replies" in out:
                break
            proof = _mechanical_proof(out) if "INFER proof" in out else None
            if proof is not None:
                out = _console(meta, key, "-", stdin=proof).stdout
            elif "line => tool" in out:
                out = _console(meta, key, "none").stdout
            else:
                out = _console(meta, key).stdout


def run(root: Path, name: str) -> int:
    if not capture_armed(root):
        refuse("capture-off", "monitoring_capture is false -- the measure is not armed")
    state = held(root)
    if name not in state:
        refuse("analysis-unknown", f"`{name}` -- declare it with setup")
    entry = state[name]
    if "archive" in entry:
        refuse("analysis-archived", f"`{name}` reads an archive -- report it, it is never played")
    meta = Path(entry["repo"])
    if not (meta / ".sys" / "instance.yaml").is_file():
        refuse("repo-not-instance", f"{meta} is gone -- re-setup the analysis")
    book = playbook(Path(entry["scenario"]))
    missing = sorted(set(book["composition"]) - pinned(meta) - {"kit"})
    if missing:
        refuse("composition-short", f"{meta} lacks {', '.join(missing)} -- the playbook "
               "requires them")
    played = 0
    for session in book["sessions"]:
        if not session["gestures"]:
            continue
        if session["fixture"]:
            done = subprocess.run(session["fixture"], shell=True, capture_output=True,
                                  text=True, cwd=str(meta.parent))
            if done.returncode != 0:
                refuse("fixture-failed", f"`{session['fixture']}` -- rc {done.returncode}: "
                       f"{done.stderr.strip()[-200:]}")
        _drive(meta, session["gestures"])   # each session is its own run
        played += 1
    traces = sorted((meta / ".sys" / "state").glob("session-*.jsonl"))
    if not traces:
        refuse("target-refused", f"{meta} wrote no trace")
    kept = [str(one) for one in traces[-played:]] if played else []
    core = engine()
    with core.record.held(record_path(root)):
        state = held(root)
        state[name]["last_trace"] = kept[-1] if kept else str(traces[-1])
        state[name]["traces"] = kept
        state[name]["played_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        core.record.replace(record_path(root), json.dumps(state, indent=1, ensure_ascii=False))
    print(f"pp-monitoring: played -- {name}, {played} session(s), trace {Path(kept[-1]).name if kept else traces[-1].name}")
    return 0


def _at(event: dict):
    """-> the event's UTC datetime, or None."""
    from datetime import datetime
    raw = event.get("at")
    try:
        return datetime.fromisoformat(raw) if raw else None
    except (TypeError, ValueError):
        return None


def _function(event: dict) -> str:
    """-> the FUNCTION a block belongs to: its stack's tail document and its command,
    the label the time is attributed to (`TURN/WORK`, `NEXT/INFER`, ...)."""
    tail = str(event.get("stack") or "").split("\u25b8")[-1].strip()
    doc = tail.split("{")[0].strip() or "?"
    command = str(event.get("command") or "").strip() or "-"
    return f"{doc}/{command}"


def _op_messages(source: Source) -> list[tuple[datetime, str]]:
    """-> the operator's TYPED chat messages with their timestamps, across the campaign's
    transcripts (claude provider), sorted by time. A user row carrying tool results is the
    harness's, not the operator's -- only typed text counts (the conduite's own filter).
    Paired to the turns BY TIME (turns_of), so an invalidated run's messages in the same
    workspace never mislabel a live turn; the play is deterministic -- the operator types
    the playbook's gestures in order, no marker needed (operator word 2026-09-03)."""
    said: list[tuple[datetime, str]] = []
    for transcript in source.transcripts:
        for line in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("type") != "user":
                continue
            ts = _ts(row.get("timestamp"))
            content = row.get("message", {}).get("content")
            if isinstance(content, list) and any(
                    isinstance(one, dict) and one.get("type") == "tool_result"
                    for one in content):
                continue                       # a tool result rides a user row -- not typed
            text = _text(content).strip()
            if ts is not None and text and not text.startswith(("<", "Caveat")):
                said.append((ts, text.splitlines()[0][:40]))
    said.sort(key=lambda one: one[0])
    return said


def turns_of(paths: list[Path], source: Source | None = None) -> list[dict]:
    """-> ONE row per TURN (a `turn-end` closes a turn), aggregated: the operator message
    (paired by order to the stamps, when the repo is given), the distinct functions the turn
    touched, its total volume, its agent seconds and the engine ms inside it. The finest
    reading the trace allows (operator word 2026-09-03 -- generalize from here)."""
    turns: list[dict] = []
    cur = None
    def fresh():
        return {"functions": [], "c": 0, "tk": 0, "agent_s": 0.0, "engine_ms": 0.0,
                "session": session, "start": None}
    for session, path in enumerate(paths, start=1):
        cur = None
        pending = None
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            at, kind = _at(event), event.get("kind")
            if at is None:
                continue
            if cur is None and kind in ("block",):
                cur = fresh()
            if kind in ("provider", "sink"):
                if cur is not None:
                    cur["engine_ms"] += float(event.get("ms") or 0)
                continue
            if pending is not None and kind not in ("new", "prompt") and cur is not None:
                cur["agent_s"] += max(0.0, (at - pending).total_seconds())
                pending = None
            if kind in ("new", "prompt"):
                pending = None
                continue
            if kind == "turn-end":
                if cur is not None:
                    turns.append(cur); cur = None
                pending = None
                continue
            if kind == "block":
                if cur is None:
                    cur = fresh()
                if cur["start"] is None:
                    cur["start"] = at
                fn = _function(event).split("/")[0]
                if fn not in cur["functions"]:
                    cur["functions"].append(fn)
                w = event.get("weight") or {}
                cur["c"] += int(w.get("total") or 0)
                cur["tk"] += int(w.get("tokens") or 0)
                pending = at
    return _pair(turns, _op_messages(source) if source is not None else [])


def _pair(turns: list[dict], ops: list[tuple[datetime, str]]) -> list[dict]:
    """Label each turn with the op message that TRIGGERED it -- BY TIME, not by naive order:
    the last operator message at or before the turn's first block. A dead run's messages
    (all before the first live turn) are consumed ahead of turn 1 and discarded, so an
    invalidated run left in the same Claude log never shifts the labels."""
    oi = 0
    for i, turn in enumerate(turns):
        turn["n"] = i + 1
        chosen = "-"
        start = turn.get("start")
        if start is not None:
            while oi < len(ops) and ops[oi][0] <= start:
                chosen = ops[oi][1]
                oi += 1
        turn["op"] = chosen
    return turns


def time_of(paths: list[Path]) -> dict:
    """-> agent TIME by function, in seconds: each interval between a rendered block and
    the agent's NEXT call is agent work, owned by that block's function; the tail (last
    block to `turn-end`) is the answer's delivery. The operator's wait (a `prompt`/`new`
    opens the next exchange) never enters, and the engine's own milliseconds (providers,
    sinks) are said apart -- they run INSIDE a block, not between them.

    documentary: pp only traces when the agent calls it, so the wall time from a block's
    render to the next event IS the agent thinking and working; `turn-end`, stamped by
    the harness hook or `./pp -et`, closes the invisible tail after the last block."""
    from collections import defaultdict
    by_function: dict[str, float] = defaultdict(float)
    tail_seconds, engine_ms, stamps, turns = 0.0, 0.0, 0, 0
    proof_seconds, proofs = 0.0, 0
    for path in paths:
        pending = None                       # (at, function) of the last block awaiting its close
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            at, kind = _at(event), event.get("kind")
            if at is None:
                continue
            if kind in ("new", "prompt"):    # the operator's boundary: their wait is theirs
                pending = None
                continue
            if kind in ("provider", "sink"):
                engine_ms += float(event.get("ms") or 0)
                continue
            if kind == "turn-end":
                if pending is not None:
                    tail_seconds += max(0.0, (at - pending[0]).total_seconds())
                    pending = None
                stamps += 1
                turns += 1
                continue
            if pending is not None:          # this event CLOSES the previous block's interval
                interval = max(0.0, (at - pending[0]).total_seconds())
                # the ENGINE marks the proof: an advancement whose instruction is PROVE
                # is the agent PROVING, dissociated from the work
                is_proof = "PROVE" in str(event.get("instruction") or "")
                if is_proof:
                    proof_seconds += interval; proofs += 1
                else:
                    by_function[pending[1]] += interval
                pending = None
            if kind == "block":
                pending = (at, _function(event))
    return {"by_function": dict(by_function), "tail_seconds": tail_seconds,
            "engine_ms": engine_ms, "stamps": stamps,
            "proof_seconds": proof_seconds, "proofs": proofs}


def analyse(paths: list[Path]) -> dict:
    """The aggregate of one or several traces -- descended from the plan's
    campagne-effort.py: parts, payload subjects, engine-run skills, and the token
    map providers themselves declare (their line carries the package)."""
    parts: dict[str, int] = defaultdict(int)
    subjects: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    providers: dict[str, list[float]] = defaultdict(lambda: [0, 0.0])
    sinks: dict[str, list[float]] = defaultdict(lambda: [0, 0.0])
    token_owner: dict[str, str] = {}
    stamps, blocks, engine_ms = 0, 0, 0.0
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = event.get("kind")
            if kind == "block":
                blocks += 1
                for part, value in (event.get("weight") or {}).items():
                    parts[part] += int(value)
                for subject, pair in (event.get("payloads") or {}).items():
                    subjects[subject][0] += int(pair[0]); subjects[subject][1] += int(pair[1])
            elif kind == "provider":
                token_owner[str(event.get("token"))] = str(event.get("package") or "?")
                slot = providers[f"{event.get('name')} ({event.get('package') or '?'})"]
                slot[0] += 1; slot[1] += float(event.get("ms") or 0); engine_ms += float(event.get("ms") or 0)
            elif kind == "sink":
                slot = sinks[str(event.get("skill"))]
                slot[0] += 1; slot[1] += float(event.get("ms") or 0); engine_ms += float(event.get("ms") or 0)
            elif kind == "turn-end":
                stamps += 1
    per_package: dict[str, int] = defaultdict(int)
    for subject, (chars, _tk) in subjects.items():
        per_package[token_owner.get(subject, "?")] += chars
    return {"blocks": blocks, "parts": dict(parts), "subjects": dict(subjects),
            "providers": dict(providers), "sinks": dict(sinks), "stamps": stamps,
            "engine_ms": engine_ms, "per_package": dict(per_package)}


PROTOCOL = ("standing orders", "constraints", "tools.md")   # the protocol's own payloads


def _nature(subject: str, tokens: dict[str, str]) -> str:
    """-> what a payload SUBJECT is, by its NAME alone (the rule METRICS.md states, the one
    an archive can still apply): a provider line marks a `token`, the protocol's own are
    `protocol`, an extension marks a `reading` (a serve row, a SERVEd file), the rest are
    `body` (a CALLed or mounted document, served by its name)."""
    if subject in tokens:
        return "token"
    if subject in PROTOCOL:
        return "protocol"
    if "." in subject.rsplit("/", 1)[-1]:
        return "reading"
    return "body"


def levers_of(paths: list[Path]) -> dict:
    """-> what the traces attribute to each SETTING: every subject's serves and the
    RE-SERVES within one run (the same subject served again after its first time -- what
    `proc_body_serve: once` spares for a body, what a repair re-serves for a reading), the
    provider tokens with their owning package, the cuts and the turns they fell in, the
    repairs, the refusals, the blocks and the stamped turns.

    documentary: a lever is worth its figure -- this reading says, key by key, what the
    traces charge to it, so a default moves on a number rather than a hunch."""
    served: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])  # serves, c, re-serves, re-c
    tokens: dict[str, str] = {}
    counts = {"blocks": 0, "stamps": 0, "cuts": 0, "repairs": 0, "refusals": 0,
              "runs": len(paths)}
    cut_turns: set[tuple[int, int]] = set()
    for run_index, path in enumerate(paths):
        within: set[str] = set()
        turn = 1
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = event.get("kind")
            if kind == "provider":
                tokens[str(event.get("token"))] = str(event.get("package") or "?")
            elif kind == "block":
                counts["blocks"] += 1
                for subject, pair in (event.get("payloads") or {}).items():
                    slot = served[subject]
                    slot[0] += 1; slot[1] += int(pair[0])
                    if subject in within:
                        slot[2] += 1; slot[3] += int(pair[0])
                    within.add(subject)
            elif kind == "cut":
                counts["cuts"] += 1; cut_turns.add((run_index, turn))
            elif kind in ("repair", "repair-in-place"):
                counts["repairs"] += 1
            elif kind == "refusal":
                counts["refusals"] += 1
            elif kind == "turn-end":
                counts["stamps"] += 1; turn += 1
    return {"served": dict(served), "tokens": tokens, "cut_turns": len(cut_turns), **counts}


def _token_owners(paths: list[Path]) -> dict[str, str]:
    """-> token -> owning package, from the provider lines the engine left."""
    found: dict[str, str] = {}
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("kind") == "provider":
                found[str(event.get("token"))] = str(event.get("package") or "?")
    return found


def _subject_owners(source: Source) -> dict[str, str]:
    """-> a payload SUBJECT (a served document name or a generated one) mapped to the
    PACKAGE that owns it, read from the repo's composition -- so `report` attributes the
    volume by package without a provider line (a served body has no provider; it belongs
    to its document's package all the same). An archive carries no composition: the
    protocol's own alone are attributed, the rest is said unattributed."""
    owners = {"standing orders": "kit", "tools.md": "kit", "constraints": "kit"}
    if source.archived:
        return owners
    from conductor.state import instance as inst
    try:
        for docname, _path, package, front in inst.documents(source.home):
            title = str(front.get("name") or docname[:-3])
            owners[title] = package or "instance"
    except Exception:
        pass
    return owners


def report(root: Path, name: str) -> int:
    engine()  # sets the engine path so _subject_owners can read the composition
    state = held(root)
    if name not in state:
        refuse("analysis-unknown", f"`{name}` -- declare it with setup")
    source = Source.of(state[name])
    kept = [Path(one) for one in state[name].get("traces", []) if Path(one).is_file()]
    last = state[name].get("last_trace")
    if not kept and last and Path(last).is_file():
        kept = [Path(last)]
    live = False
    if not kept:
        # a CONDUITE campaign leaves live traces, not a mechanical run's -- and an archive
        # holds nothing else: read them all
        kept = source.traces
        live = not source.archived
    if not kept:
        refuse("trace-missing", f"`{name}` has no trace -- run it, or play its sessions")
    agg = analyse(kept)
    parts = agg["parts"]
    owners = _subject_owners(source)                        # subject -> owning package,
    unowned = "?" if source.archived else "instance"         # from the repo (borne A: the
    per_package: dict[str, float] = {}                      # provider line is not the only
    for subject, (chars, _tk) in agg["subjects"].items():   # owner -- a served body belongs
        owner = owners.get(subject, unowned)                # to its package); an archive
        per_package[owner] = per_package.get(owner, 0) + chars   # knows no composition
    agg["per_package"] = per_package
    print(f"pp-monitoring: {name} -- {agg['blocks']} block(s), {len(kept)} trace(s)"
          f"{' ARCHIVED' if source.archived else ' LIVE (no mechanical run)' if live else ''}")
    for line in _header(source):
        print(line)
    timing = time_of(kept)
    print("  volume (c) : " + " · ".join(f"{k} {parts.get(k, 0)}" for k in
          ("constraints", "payload", "options", "instruction", "frame", "total"))
          + f" · tokens ~{parts.get('tokens', 0)}")
    # ONE table per function (operator word 2026-09-02): a row joins a subject's
    # VOLUME, the agent seconds of its steps, the engine ms of its provider and the
    # setting that governs it -- generic rules only, no package named by this skill
    agent_by_proc: dict[str, float] = {}
    for function, seconds in timing["by_function"].items():
        agent_by_proc[function.split("/")[0]] = (
            agent_by_proc.get(function.split("/")[0], 0.0) + seconds)
    engine_by_skill = {label.split(" ")[0]: ms for label, (_c, ms) in
                       {**agg["providers"], **agg["sinks"]}.items()}
    tokens = _token_owners(kept)

    def governed(subject: str) -> str:
        # the same rule the levers apply (`_nature`): the name says what a setting governs
        nature = _nature(subject, tokens)
        if subject == "tools.md":
            return "the catalog -- served per -new"
        if nature == "protocol":
            return "verbatim_constraints / conduction_effort"
        if nature == "reading":
            return "a row serves (no key)"
        if nature == "body":
            return "proc_body_serve"
        return f"{tokens[subject]}_* (its fragment)"
    print(f"  {'function':26s} {'c':>8s} {'~tk':>7s} {'agent s':>8s} {'engine ms':>10s}  governed by")
    shown: set[str] = set()
    for subject, (chars, tk) in sorted(agg["subjects"].items(), key=lambda kv: -kv[1][0]):
        proc = subject.split(".")[0]
        seconds = agent_by_proc.pop(proc, 0.0); shown.add(proc)
        ms = engine_by_skill.get(subject, 0.0)
        print(f"  {subject:26s} {chars:8d} {tk:>7d} {seconds:8.1f} {ms:10.1f}  {governed(subject)}")
    for proc, seconds in sorted(agent_by_proc.items(), key=lambda kv: -kv[1]):
        label = "closures (fused turns)" if proc.endswith("TURN") or proc == "TURN" else proc
        print(f"  {label:26s} {'-':>8s} {'-':>7s} {seconds:8.1f} {'-':>10s}  instructions_fusion")
    print(f"  {'laws (constraints)':26s} {parts.get('constraints', 0):8d} {'-':>7s} {'-':>8s} {'-':>10s}  verbatim_constraints / conduction_effort")
    print(f"  {'frame':26s} {parts.get('frame', 0):8d} {'-':>7s} {'-':>8s} {'-':>10s}  -")
    print()
    print(f"  {'tour':>4s}  {'instruction (op)':40s} {'fonctions':26s} {'c':>7s} {'~tk':>6s} {'agent s':>8s} {'mot ms':>7s}")
    last_session = None
    rows = turns_of(kept, source)
    for row in rows:
        if row.get("session") != last_session:
            if last_session is not None:
                # a session boundary is a `-reset` + fresh run: `_proven` empties, bodies re-serve
                print(f"  {'':>4s}  -- reset (session {row['session']}) : nouveau run, "
                      "les corps deja servis se re-servent --")
            last_session = row.get("session")
        print(f"  {row['n']:>4d}  {row['op'][:40]:40s} {('+'.join(row['functions']))[:26]:26s} "
              f"{row['c']:7d} {row['tk']:6d} {row['agent_s']:8.1f} {row['engine_ms']:7.1f}")
    if timing["stamps"] > len(rows):
        # a stamp that closed no rendered block is a turn the agent left UNCONDUCTED
        # (the operator's word) -- it costs nothing here and earns no row, said rather than lost
        print(f"  {'':>4s}  {timing['stamps'] - len(rows)} turn-end stamp(s) closed no conducted "
              "block: unconducted turn(s), no row")
    print()
    for label, (count, ms) in sorted(agg["providers"].items()):
        print(f"  provider {label:28s} x{count}  {ms:7.1f} ms")
    for label, (count, ms) in sorted(agg["sinks"].items()):
        print(f"  sink     {label:28s} x{count}  {ms:7.1f} ms")
    for package, chars in sorted(agg["per_package"].items(), key=lambda kv: -kv[1]):
        label = "unattributed (an archive carries no composition)" if package == "?" else package
        print(f"  package  {label:28s} {chars:7d} c of payload")
    total_agent = (sum(timing["by_function"].values()) + timing["tail_seconds"]
                   + timing["proof_seconds"])
    from conductor.state import settings as _settings
    values = _settings_of(source)
    try:
        if source.archived:
            # an archive's regime is what its kept SETTINGS spell: none says none
            spelled = values["instructions_fusion"]
            fusion = 1 if spelled == "none" else 0 if spelled == "max" else int(spelled)
        else:
            fusion = _settings.of(source.home).fusion   # int: 1 none, 0 max, n cap
    except Exception:
        fusion = -1
    grain = ("per STEP" if fusion == 1 else "per TURN (fused)" if fusion == 0
             else f"capped at {fusion}" if fusion > 1 else "unknown regime")
    print(f"  -- agent time by function (s) -- {total_agent:.1f}s total, "
          f"engine {timing['engine_ms']:.1f} ms apart -- fusion={fusion}, time is {grain}")
    for function, seconds in sorted(timing["by_function"].items(), key=lambda kv: -kv[1]):
        print(f"  time     {function:28s} {seconds:7.1f} s")
    if timing["proofs"]:
        print(f"  time     {'proof (dissociated)':28s} {timing['proof_seconds']:7.1f} s "
              f"-- {timing['proofs']} proof advancement(s)")
    else:
        print("  time     proof -- none this session (no law of production in force): the "
              "engine marks a proof advancement apart when it happens")
    if timing["stamps"]:
        print(f"  time     {'tail (answer delivery)':28s} {timing['tail_seconds']:7.1f} s "
              f"-- {timing['stamps']} turn-end stamp(s)")
    else:
        print("  time     the tail is UNKNOWN -- no turn-end stamp on this trace (the "
              "harness hook or ./pp -et arms it)")
    _levers(kept, values, timing, parts, total_agent)
    return 0


def _levers(kept: list[Path], values: dict[str, str], timing: dict, parts: dict,
            total_agent: float) -> None:
    """The LEVERS section: one line per setting, the value the source spells (`?` when it
    kept none) and the figure the traces charge to it -- generic keys only; a package's
    keys are named by the provider lines its tokens left, never by this skill."""
    lv = levers_of(kept)
    tokens = lv["tokens"]

    def val(key: str) -> str:
        return f"{key}={values.get(key, '?')}"

    def names(chosen: dict, index: int) -> str:
        top = sorted(chosen.items(), key=lambda kv: -kv[1][index])[:4]
        return ", ".join(f"{one} x{v[index - 1]}" for one, v in top if v[index]) or "none"

    bodies = {s: v for s, v in lv["served"].items() if _nature(s, tokens) == "body"}
    readings = {s: v for s, v in lv["served"].items() if _nature(s, tokens) == "reading"}
    total = parts.get("total", 0) or 1
    print()
    print("  -- levers: what each setting governed here (the value as the source's SETTINGS "
          "spell it, ? when it kept none) --")
    print(f"  lever    {val('proc_body_serve'):32s} bodies re-served within a run: "
          f"{sum(v[3] for v in bodies.values())} c over {sum(v[2] for v in bodies.values())} "
          f"re-serve(s) -- {names(bodies, 3)}; `once` spares exactly these")
    print(f"  lever    {'readings (no key: a row serves)':32s} {sum(v[1] for v in readings.values())} c "
          f"over {sum(v[0] for v in readings.values())} serve(s) -- {names(readings, 1)}; "
          f"{sum(v[3] for v in readings.values())} c re-served after a repair (none since 2026-09-05)")
    print(f"  lever    {val('verbatim_constraints'):32s} laws {parts.get('constraints', 0)} c = "
          f"{100 * parts.get('constraints', 0) / total:.0f} % of the total; standing orders "
          f"{lv['served'].get('standing orders', [0, 0])[1]} c ride the marble channel beside")
    print(f"  lever    {'proofs (no key: the checkpoint stands)':32s} {timing['proofs']} proof(s), "
          f"{timing['proof_seconds']:.1f} s = {100 * timing['proof_seconds'] / (total_agent or 1):.0f} % "
          f"of the agent time")
    print(f"  lever    {val('work_repairs_allowed'):32s} {lv['repairs']} repair(s), "
          f"{lv['refusals']} refusal(s)")
    print(f"  lever    {val('max_harness_tool_output'):32s} {lv['cuts']} cut(s) in "
          f"{lv['cut_turns']} turn(s) -- one more bare call each")
    per_turn = (f"{lv['blocks'] / lv['stamps']:.1f} block(s) per stamped turn" if lv["stamps"]
                else "no stamp -- the blocks per turn are unknown")
    print(f"  lever    {val('instructions_fusion'):32s} {lv['blocks']} block(s) over "
          f"{lv['stamps']} turn(s), {lv['runs']} run(s): {per_turn}")
    by_owner: dict[str, list[str]] = defaultdict(list)
    for token, owner in sorted(tokens.items()):
        serves, chars = lv["served"].get(token, [0, 0])[:2]
        by_owner[owner].append(f"{token} x{serves}: {chars} c")
    for owner, its in sorted(by_owner.items()):
        print(f"  lever    {owner + '_* (its fragment)':32s} {'; '.join(its)} -- regenerated "
              "at every turn the token plays")
    print(f"  lever    {val('conduction_effort'):32s} presets verbatim_constraints, "
          "instructions_fusion, proc_body_serve and capture_prompt, and every fragment's effort: block")


def stamp(root: Path) -> int:
    """The hook's target: SILENT while `monitoring_capture` is false -- the switch is
    the runtime interrupter, the wired hook never changes -- and the engine's `-et`
    when it is true, its output and code relayed as they are."""
    if not capture_armed(root):
        return 0
    done = subprocess.run([sys.executable, str(root / ".sys" / "engine" / "pp.py"), "-et"],
                          capture_output=True, text=True, cwd=str(root.parent))
    sys.stdout.write(done.stdout); sys.stderr.write(done.stderr)
    return done.returncode


def wire(root: Path, provider: str) -> int:
    """The harness link, written once and never overwritten (the wire.py motif): an
    absent `.claude/settings.json` is born with the hook alone; a present one is left
    untouched, the exact snippet printed for the operator's own merge."""
    home_dir = Path(__file__).resolve().parent.parent.parent / "providers" / provider
    snippet = home_dir / "hook.json"
    if not snippet.is_file():
        known = sorted(one.name for one in (home_dir.parent.glob("*")) if one.is_dir())
        refuse("provider-unknown", f"`{provider}` -- this package carries: {', '.join(known) or 'none'}")
    target = root.parent / ".claude" / "settings.json"
    text = snippet.read_text(encoding="utf-8")
    if target.is_file():
        print(f"pp-monitoring: skipped -- {target} exists and is yours; add this yourself:")
        print(text.rstrip())
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"pp-monitoring: wired -- {target} (the Stop hook plays ./pp monitoring-stamp)")
    return 0


def listing(root: Path) -> int:
    state = held(root)
    if not state:
        print("pp-monitoring: no analysis declared")
        return 0
    for name, entry in sorted(state.items()):
        played = entry.get("played_at", "never played")
        print(f"  {name:24s} {', '.join(entry.get('packages') or ['—']):24s} {played}")
    return 0


def main(argv: list[str]) -> int:
    """`argv` holds the arguments WITHOUT the program name -- the verb first -- as every
    script skill receives them, whether the console plays it or `python` runs it."""
    root = home()
    if len(argv) == 4 and argv[0] == "setup":
        return setup(root, argv[1], argv[2], argv[3])
    if len(argv) == 3 and argv[0] == "setup":
        return setup_archive(root, argv[1], argv[2])
    if len(argv) >= 2 and argv[0] == "derive":
        fusion = None
        rest = argv[1:]
        if "--fusion" in rest:
            i = rest.index("--fusion")
            fusion = rest[i + 1] if i + 1 < len(rest) else None
            rest = rest[:i] + rest[i + 2:]
        return derive(root, rest[0], fusion)
    if len(argv) == 2 and argv[0] == "run":
        return run(root, argv[1])
    if len(argv) == 2 and argv[0] == "conduite":
        return conduite(root, argv[1])
    if len(argv) == 2 and argv[0] == "report":
        return report(root, argv[1])
    if len(argv) == 1 and argv[0] == "list":
        return listing(root)
    if len(argv) == 2 and argv[0] == "wire":
        return wire(root, argv[1])
    if len(argv) == 1 and argv[0] == "stamp":
        return stamp(root)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
