"""Scenario `package-switch-run` -- 8 case(s) (plan pp-split, batch l-interrupteur-de-package):
- `-disable <package>` writes the run's slot and answers with the block that STANDS
- what is switched off does not PLAY: the turn's end passes it by, its dependent with it
- the switch belongs to the RUN: a second run of the same instance plays every package whole
- `-enable` brings the package back into the play, and the slot carries no switch
- the three refusals name their reason and write nothing: the base, an unpinned name, a package in flight
- a compaction keeps the switch, the trace says `switch` and `-stats` counts it
- the STATE rides every output of the run: one cell per pin beyond the base, in the requires topology, the cause said
- with no run standing the keyless view says the durable state, and an instance pinning nothing beyond its base says nothing
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from conductor import install, instance
from conductor.state import traces
from tests.harness import PRODUCT_ENGINE, cli

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.ready, turn.begin, turn.end]\n")
ALPHA = "name: alpha\nversion: 0.0.1\ndescription: needs the kit\nrequires: [kit]\n"
BETA = "name: beta\nversion: 0.0.1\ndescription: needs alpha\nrequires: [alpha]\n"
ATTACHED = ("---\nname: {n}\nkind: proc\ndescription: a witness at the turn's end\n"
            "attach: turn.end\nproc: |\n  INFER\n---\n\nSay `{n}`.\n")


def _source(kit_version: str) -> Path:
    """A product checkout REDUCED to manifests: the kit whole, and two witness packages
    -- `alpha` and `beta` (requires alpha), each attaching one document at `turn.end`."""
    root = Path(tempfile.mkdtemp()) / "product"
    for part in ("engine", "kit", "template"):
        shutil.copytree(PRODUCT_ENGINE.parent.parent / part, root / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (root / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
    for name, manifest in (("alpha", ALPHA), ("beta", BETA)):
        home = root / "packages" / name
        (home / "procs").mkdir(parents=True)
        (home / "package.yaml").write_text(manifest, encoding="utf-8")
        (home / "procs" / f"{name.upper()}.md").write_text(ATTACHED.format(n=name.upper()),
                                                           encoding="utf-8")
    return root


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    kit_version = instance.pins(bench.env("run-kit").made)["kit"]
    source = _source(kit_version)

    def witness(name: str) -> tuple[Path, Path]:
        """An instance of the witness composition, one step per block: what the play
        skips is then visible block by block."""
        made = install.install(source / "engine" / "pp.py",
                               Path(tempfile.mkdtemp()) / name / ".pp", ["beta"])
        path = made / "SETTINGS.md"
        path.write_text(path.read_text(encoding="utf-8")
                        .replace("conduction_effort: medium", "conduction_effort: none")
                        .replace("instructions_fusion: max", "instructions_fusion: none"),
                        encoding="utf-8")
        return made, made / ".sys" / "engine" / "pp.py"

    made, engine = witness("switched")

    def call(*args: str):
        return cli(engine, *args, cwd=made.parent)

    def opened() -> str:
        """-> the key of the run `-new` just opened: the newest slot of the instance."""
        newest = max((made / ".sys" / "state").glob("session-*.json"), key=lambda p: p.stat().st_mtime)
        return newest.stem[len("session-"):]

    def slot(key: str, home: Path = None) -> dict:
        return json.loads(((home or made) / ".sys" / "state" / f"session-{key}.json")
                          .read_text(encoding="utf-8"))

    def walk(key: str, home: Path = None, machine: Path = None, rounds: int = 12) -> str:
        """Advances until the frontier, gathering what the outputs carried."""
        seen = []
        for _ in range(rounds):
            answered = cli(machine or engine, key, cwd=(home or made).parent)
            seen.append(answered.stdout)
            if "▶ FINAL" in answered.stdout or "▶ END" in answered.stdout or answered.returncode:
                break
        return "".join(seen)

    call("-new")
    key = opened()
    standing = call(key, "-peek").stdout
    answered = call(key, "-disable", "beta")
    after = call(key, "-peek").stdout
    state_before = [one for one in standing.splitlines() if one.startswith("▌ ")][1]
    state_after = [one for one in after.splitlines() if one.startswith("▌ ")][1]

    # --- the slot written, the block that stands comes back ---------------------------
    if (answered.returncode == 0 and slot(key).get("off") == ["beta"]
            and "`beta` off for this run" in answered.stdout
            and standing.splitlines()[2:] == after.splitlines()[2:]
            and after.splitlines()[2:] and after.splitlines()[2:] == answered.stdout.splitlines()[4:]):
        held("a disable writes the slot and answers the standing block",
             "`off: [beta]` at the slot, the fact said, and the same step standing before and "
             "after -- every line but the output's own two (the hour and the state), the "
             "block the answer itself carries")
    else:
        failures.append(f"  ✗ disable                     rc={answered.returncode} "
                        f"off={slot(key).get('off')} {answered.stdout[:200]!r}")

    # --- what is off does not PLAY ----------------------------------------------------
    played = walk(key)
    if "▸ ALPHA" in played and "▸ BETA" not in played and "▶ FINAL" in played:
        held("what is off does not play", "the turn's end played ALPHA and passed BETA by, "
             "then the frontier -- the socket's contributor list follows the play")
    else:
        failures.append(f"  ✗ the play                    alpha={'▸ ALPHA' in played} "
                        f"beta={'▸ BETA' in played}")

    # --- the switch belongs to the run -------------------------------------------------
    call("-new")
    beside = opened()
    whole = walk(beside)
    if ("▸ ALPHA" in whole and "▸ BETA" in whole and not slot(beside).get("off")
            and slot(key).get("off") == ["beta"]):
        held("the switch belongs to the run", "a run opened beside it in the same instance "
             "plays ALPHA and BETA whole, its slot switching nothing; the first run keeps beta off")
    else:
        failures.append(f"  ✗ per run                     alpha={'▸ ALPHA' in whole} "
                        f"beta={'▸ BETA' in whole} off={slot(beside).get('off')}")

    # --- `-enable` brings it back ------------------------------------------------------
    back = call(beside, "-disable", "beta")
    lifted = call(beside, "-enable", "beta")
    call(beside, "the operator's word")                # the frontier resumes: a fresh turn
    again = walk(beside)
    if (back.returncode == 0 and lifted.returncode == 0 and not slot(beside).get("off")
            and "`beta` on for this run" in lifted.stdout and "▸ BETA" in again):
        held("an enable brings the package back", "beta off then on: the slot carries no switch, "
             "the fact says nothing is out, and the next turn's end plays BETA again")
    else:
        failures.append(f"  ✗ enable                      off={slot(beside).get('off')} "
                        f"{lifted.stdout[:160]!r} beta={'▸ BETA' in again}")

    # --- the three refusals, nothing written -------------------------------------------
    kept = slot(key)
    base = call(key, "-disable", "kit")
    unpinned = call(key, "-disable", "nope")
    flight_made, flight_engine = witness("in-flight")
    cli(flight_engine, "-new", cwd=flight_made.parent)
    flight_key = max((flight_made / ".sys" / "state").glob("session-*.json"),
                     key=lambda p: p.stat().st_mtime).stem[len("session-"):]
    for _ in range(12):                      # walk to the block ALPHA's own frame holds
        answered = cli(flight_engine, flight_key, cwd=flight_made.parent)
        if "▸ ALPHA" in answered.stdout:
            break
    flight = cli(flight_engine, flight_key, "-disable", "alpha", cwd=flight_made.parent)
    if (base.returncode and "package-base" in base.stderr
            and unpinned.returncode and "package-unpinned" in unpinned.stderr
            and flight.returncode and "package-in-flight" in flight.stderr
            and "ALPHA.md" in flight.stderr
            and slot(key) == kept and not slot(flight_key, flight_made).get("off")):
        held("the three refusals write nothing", "`-disable kit` package-base, `-disable nope` "
             "package-unpinned, and a package whose document holds the standing view "
             "package-in-flight (ALPHA.md named); both slots byte for byte")
    else:
        failures.append(f"  ✗ refusals                    {base.returncode}/{unpinned.returncode}/"
                        f"{flight.returncode} {flight.stderr[:200]!r}")

    # --- a compaction keeps it; the trace says switch, the stats count -----------------
    served = call(key, "-compacted")
    lines = [json.loads(line) for path in (made / ".sys" / "state").glob("session-*.jsonl")
             for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    counted = traces.summary(traces.runs(made / ".sys" / "state"))
    switches = [one for one in lines if one.get("kind") == "switch"]
    if (served.returncode == 0 and slot(key).get("off") == ["beta"]
            and "▸ BETA" not in served.stdout and len(switches) == 3
            and counted["switches"] == 3
            and [one.get("package") for one in switches] == ["beta", "beta", "beta"]):
        held("a compaction keeps the switch, the trace says it", "the re-served run still has "
             "beta out; three `switch` lines at the traces (two off, one on) and three at the "
             "period's count -- a refused switch leaves no line")
    else:
        failures.append(f"  ✗ compacted and traced        rc={served.returncode} "
                        f"off={slot(key).get('off')} switches={len(switches)} "
                        f"counted={counted['switches']}")

    # --- the state rides every output ---------------------------------------------------
    caused = call(beside, "-disable", "alpha").stdout
    if (state_before == "▌ alpha on · beta on" and state_after == "▌ alpha on · beta off"
            and state_after in served.stdout and played.count(state_after) >= 2
            and "▌ alpha off · beta off (<- alpha)" in caused):
        held("the state rides every output", "`alpha on · beta on` under the heading before the "
             "switch and `alpha on · beta off` after it, on every output of the walk and on the "
             "re-served view; alpha switched off in the run beside says `alpha off · beta off "
             "(<- alpha)` -- one cell per pin beyond the base, dependencies first, so the cause "
             "reads before what it took out")
    else:
        failures.append(f"  ✗ the state line              {state_before!r} -> {state_after!r} "
                        f"walk={played.count(state_after)} caused={caused[:120]!r}")

    # --- the keyless view, and an instance with nothing beyond its base -----------------
    quiet_made, quiet_engine = witness("keyless")
    path = quiet_made / "SETTINGS.md"
    path.write_text(path.read_text(encoding="utf-8")
                    .replace("package.beta: on", "package.beta: off"), encoding="utf-8")
    keyless = cli(quiet_engine, cwd=quiet_made.parent)
    bare = bench.env("bare-of-packages")
    bare_keyless = bare.cli()
    if (keyless.returncode == 0 and "▌ alpha on · beta off" in keyless.stdout
            and "no run is under way" in keyless.stdout
            and bare_keyless.returncode == 0
            and not any(one.startswith("▌ ") and " on" in one
                        for one in bare_keyless.stdout.splitlines())):
        held("the keyless view says the durable state", "no run standing: the line says "
             "`alpha on · beta off` from SETTINGS alone, then that no run is under way; "
             "an instance pinning nothing beyond its base says nothing of packages")
    else:
        failures.append(f"  ✗ keyless                     {keyless.stdout[:200]!r} "
                        f"bare={bare_keyless.stdout[:120]!r}")
    return 0
