"""The SUPPORT module of the conduction sector (tests/README.md, rules 10 and 11): the launcher
`tools/campaign/campaign.py` played on a throwaway house, the set of the situations under `roots/`, the
coverage, the sheet and the report it writes read back, a throwaway SET a scenario writes for itself, and
`zone_case` -- what every scenario of `zones/` plays. Loaded by `support(__file__, "conduction")`; every
scenario plays its own house.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tests.harness import SOURCE

LAUNCHER = SOURCE / "tools" / "campaign" / "campaign.py"
SECTOR = SOURCE / "tests" / "conduction"
SET = SECTOR / "roots"                                       # the set of the situations, the launcher's default
MANIFEST = "campaign.yaml"
PROVIDER = "model"
ROOTS = ("read-lines", "laps", "cycle", "route", "begin", "review")       # the six patterns of the engine
SITUATIONS = ("long-read", "gesture-while-held", "two-steps", "mounted", "unoffered", "bare-call", "stubborn", "stray",
              "space", "compacted", "switched", "bounded", "bouncing", "renewed")
PATTERNS = tuple(flag for root in ROOTS for flag in ("--root", root))      # the six alone, for a channel's play
RELAYED, BARE = "relayed", "bare"
STRICT, HYBRID = "strict", "hybrid"
CHANNEL_KEYS = ("strict", "hybrid", "bare")                # the three channels a zone is crossed on
ZONES = {                                                   # what each root crosses, whatever the channel
    "read-lines": ("boot", "door"),
    "laps": ("boot", "door", "lap", "proof", "value-judged"),
    "cycle": ("boot", "door", "lap", "value-judged"),
    "route": ("boot", "door", "next", "value-judged"),
    "begin": ("boot", "proof", "value-judged"),
    "review": ("boot", "door"),
}


def launcher(*args: str, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(LAUNCHER), *args], capture_output=True, text=True,
                          cwd=str(cwd or SOURCE), env=env)


def played(bench, *args: str) -> tuple[subprocess.CompletedProcess, dict, Path, Path]:
    """`play --provider model …` on a throwaway house, its output under a throwaway path ->
    (the play, coverage.json read back -- {} when none --, the campaign's folder, the house)."""
    out = bench.temp() / "out"
    house = bench.temp() / "house"
    done = launcher("play", "--provider", PROVIDER, "--out", str(out), "--house", str(house), *args)
    folders = sorted(out.iterdir()) if out.is_dir() else []
    folder = folders[-1] if folders else out
    coverage = {}
    if (folder / "coverage.json").is_file():
        coverage = json.loads((folder / "coverage.json").read_text(encoding="utf-8"))
    return done, coverage, folder, house


def report_of(folder: Path) -> dict:
    """-> `report.json` of a campaign's folder read back, {} when none stands."""
    path = folder / "report.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def sheet_of(folder: Path) -> dict:
    """-> `sheet.json` of a campaign's folder (or of a run's) read back, {} when none stands."""
    path = folder / "sheet.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def compare_of(folder: Path) -> dict:
    """-> `compare.json` of a campaign's folder read back, {} when none stands."""
    path = folder / "compare.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def bare_lines(lines: list[dict]) -> list[dict]:
    """-> the lines of a sheet without their mask flag: what a mask must leave byte-identical."""
    return [{name: value for name, value in one.items() if name != "masked"} for one in lines]


def setting_of(house: Path, agent: str, key: str) -> str:
    path = house / agent / ".pp" / "SETTINGS.md"
    if not path.is_file():
        return ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def exchanges_of(coverage: dict) -> dict[str, dict]:
    return {one["name"]: one for one in coverage.get("exchanges", [])}


def crossed(exchange: dict, zones: tuple[str, ...]) -> list[str]:
    """-> the zones of `zones` the exchange did NOT cross."""
    return [zone for zone in zones if not exchange.get("zones", {}).get(zone)]


def all_parked(coverage: dict) -> bool:
    found = coverage.get("exchanges", [])
    return bool(found) and all(one.get("parked") and one.get("rc") == 0 and one.get("cost_usd") == 0.0
                               and not one.get("holes") and not one.get("refusals") for one in found)


def witness_set(bench, roots: tuple[str, ...] = ("alpha", "beta"), message: bool = True,
                expect: dict | None = None, launches=None, renew=None, packages=None) -> Path:
    """-> a throwaway SET of two roots, each a one-step proc at its door, with its manifest -- a
    manifest whose roots carry no message when `message` is False, the same `expect:` on every
    root when one is given (the keys as written: a wrong key is the scenario's to try), and `launches:`
    or `renew:` on every root when given (as written: a wrong value is the scenario's to try), and the
    set's `packages:` when given (as written)."""
    made = bench.temp() / "set"
    for name in roots:
        root = made / name
        root.mkdir(parents=True)
        (root / f"{name.upper()}.md").write_text(
            f"---\nname: {name.upper()}\nkind: proc\noutput: any\ndescription: the witness {name}\n"
            "proc: |\n  WORK\n---\n\nSay one line.\n", encoding="utf-8")
    lines = ["name: witness", "agent: agents/w"]
    if packages is not None:
        lines.append(f"packages: {json.dumps(packages)}")
    lines.append("roots:")
    for name in roots:
        lines.append(f"  {name}:")
        lines.append(f"    door: {name.upper()}.md")
        if message:
            lines.append(f"    message: play {name}")
        if expect:
            lines.append("    expect:")
            lines += [f"      {key}: {json.dumps(value)}" for key, value in expect.items()]
        if launches is not None:
            lines.append(f"    launches: {json.dumps(launches)}")
        if renew is not None:
            lines.append(f"    renew: {json.dumps(renew)}")
    (made / MANIFEST).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return made


def module(name: str = "campaign"):
    """-> the launcher loaded as a module by its path (its verbs callable in-process: `main`, `zones`…);
    its own `sys.path` line puts the engine first."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(f"pp_{name}_launcher", LAUNCHER)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def semantics():
    """-> the data of the conduction model, `adapters/model/semantics.py`, loaded by path."""
    import importlib.util
    path = SOURCE / "adapters" / "model" / "semantics.py"
    spec = importlib.util.spec_from_file_location("pp_model_semantics_data", path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def campaign_of(folder: Path) -> dict:
    """-> `campaign.json` of a campaign's folder read back, {} when none stands."""
    path = folder / "campaign.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def section_of(doc: Path) -> tuple[str, str, str]:
    """-> (before, section, after) of a document carrying the coverage section between its two markers --
    the begin marker included in `section`; ("", "", whole) when the document carries none."""
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    begin = text.find("<!-- coverage:begin")
    end = text.find("<!-- coverage:end -->")
    if begin < 0 or end < 0:
        return "", "", text
    stop = end + len("<!-- coverage:end -->")
    return text[:begin], text[begin:stop], text[stop:]


def expected_parked(root: str, channel: str) -> bool:
    """-> whether the root's `expect:` says its passage ENDS on that channel: true unless it says otherwise
    (a root the launcher's bound stops by nature says `parked: false` on the relayed channels)."""
    import yaml
    manifest = yaml.safe_load((SET / MANIFEST).read_text(encoding="utf-8")) or {}
    parked = ((manifest.get("roots") or {}).get(root) or {}).get("expect", {}).get("parked", True)
    if isinstance(parked, dict):
        return bool(parked.get(channel, True))
    return bool(parked)


def zone_case(bench, zone: str, roots: tuple[str, ...]) -> int:
    """What every scenario of `zones/` plays (rule 11): the roots named, on the three channels under the
    modelled LLM, on a throwaway house; then, on the coverage and the sheet of THAT play alone: every
    exchange played at cost 0, without a hole, parked (rc 0) unless its root expects otherwise on that
    channel (`expected_parked`); the zone crossed on every channel it EXISTS on (`semantics.ZONES`); no
    `rouge-conduction` and no `trou` on the lines. A refusal is the zone's own matter (stubborn stops on
    `repair-exhausted`, bare-call meets `principal-advances`, bounded meets `launches-spent`); a
    `rouge-agent` is the agent's (stray)."""
    held, failures = bench.held, bench.failures
    channels = tuple(semantics().ZONES[zone]["channels"])
    flags = tuple(flag for root in roots for flag in ("--root", root))
    done, coverage, folder, _house = played(bench, *flags)
    exchanges = coverage.get("exchanges", [])
    by_channel: dict[str, list[dict]] = {}
    for one in exchanges:
        by_channel.setdefault(str(one.get("conduction") or one.get("channel")), []).append(one)
    crossing = {key: sum(1 for one in found if one.get("zones", {}).get(zone)) for key, found in by_channel.items()}
    missing = [key for key in channels if not crossing.get(key)]

    def ended(one: dict) -> bool:
        if expected_parked(str(one.get("root")), str(one.get("conduction") or one.get("channel"))):
            return one.get("rc") == 0 and bool(one.get("parked"))
        return not one.get("parked")

    whole = (len(exchanges) == 3 * len(roots)
             and all(ended(one) and one.get("cost_usd") == 0.0 and not one.get("holes") for one in exchanges))
    lines = sheet_of(folder).get("lines", [])
    reds = [(one["exchange"], one["verdict"], one.get("why", "")) for one in lines
            if one.get("verdict") in ("rouge-conduction", "trou")]
    if done.returncode == 0 and whole and not missing and lines and not reds:
        held(f"`{zone}` crossed on {', '.join(channels)}", f"{', '.join(roots)}: {len(exchanges)} exchanges at "
             f"cost 0, {sum(1 for one in exchanges if one.get('parked'))} parked (as expected), {len(lines)} lines "
             "without rouge-conduction nor trou; crossed "
             + ", ".join(f"{key} {crossing.get(key, 0)}" for key in CHANNEL_KEYS if crossing.get(key)))
    else:
        failures.append(f"  ✗ `{zone}`                  rc={done.returncode} exchanges={len(exchanges)}/{3 * len(roots)} "
                        f"whole={whole} missing={missing} crossing={crossing} reds={reds[:3]} {done.stderr[-200:]!r}")
    return 0
