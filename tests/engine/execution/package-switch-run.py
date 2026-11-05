"""Scenario `package-switch-run` -- 3 cases (plan pp-split, batch l-interrupteur-de-package; plan agent, batch
les-reglages-de-la-saison):
- (a) a compaction keeps the run's switch, the trace says `switch` and `-stats` counts it
- (b) `PP_PACKAGES` at `-new`: the FIRST output carries the composition the launcher gives -- `alpha on` at the
  heading over `package.alpha: off` at SETTINGS, ALPHA played at the turn's end --, the trace's `new` line says the
  switches, the slot keeps them; a keyed call under the variable ignores it
- (c) `packages-invalid`, `package-unpinned` and `package-base` refuse before anything is written: no slot
`-disable` and `-enable` as the operator plays them -- the slot, the play, the run's own switch,
the refusals, the state line, the keyless view -- are the pattern `packaging/package-switch`'s.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from conductor import install, instance
from conductor.state import traces
from tests.harness import cli

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.initialize, turn.begin, turn.end]\n")
ALPHA = "name: alpha\nversion: 0.0.1\ndescription: needs the kit\nrequires: [kit]\n"
BETA = "name: beta\nversion: 0.0.1\ndescription: needs alpha\nrequires: [alpha]\n"
ATTACHED = ("---\nname: {n}\nkind: proc\ndescription: a witness at the turn's end\n"
            "attach: turn.end\nproc: |\n  INFER\n---\n\nSay `{n}`.\n")


def _source(product: Path, kit_version: str) -> Path:
    """The bench's source REDUCED to manifests: the base whole (the stand-in), and two
    witness packages -- `alpha` and `beta` (requires alpha), each attaching one document at
    `turn.end`."""
    root = Path(tempfile.mkdtemp()) / "product"
    for part in ("engine", "bases", "template"):
        shutil.copytree(product / part, root / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (root / "bases" / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
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
    source = _source(bench.source(), kit_version)

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

    call("-new")
    key = opened()
    switched = call(key, "-disable", "beta")
    state = next(one for one in switched.stdout.splitlines() if one.startswith("▌ ") and " on" in one)

    # --- a compaction keeps it; the trace says switch, the stats count -----------------
    served = call(key, "-compacted")
    lines = [json.loads(line) for path in (made / ".sys" / "state").glob("session-*.jsonl")
             for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    counted = traces.summary(traces.runs(made / ".sys" / "state"))
    switches = [one for one in lines if one.get("kind") == "switch"]
    if (served.returncode == 0 and slot(key).get("switches") == {"beta": "off"}
            and "▸ BETA" not in served.stdout and state in served.stdout and len(switches) == 1
            and counted["switches"] == 1 and switches[0].get("package") == "beta"):
        held("a compaction keeps the switch, the trace says it", "the re-served run still has "
             "beta out, its state line the same; one `switch` line at the trace and one at the period's count")
    else:
        failures.append(f"  ✗ compacted and traced        rc={served.returncode} "
                        f"off={slot(key).get('switches')} switches={len(switches)} "
                        f"counted={counted['switches']}")

    # --- (b) the launcher's composition composes the first output -------------------------------
    import os
    from conductor.state import context

    def walk(key: str, env: dict | None = None) -> str:
        seen = []
        for _ in range(12):
            answered = cli(engine, key, cwd=made.parent, env=env)
            seen.append(answered.stdout)
            if "▶ AWAIT" in answered.stdout or answered.returncode:
                break
        return "".join(seen)

    def heading(text: str) -> str:
        return next((one for one in text.splitlines() if one.startswith("▌ ") and "alpha" in one), "")

    def slots() -> int:
        return len(list((made / ".sys" / "state").glob("session-*.json")))

    path = made / "SETTINGS.md"
    path.write_text(path.read_text(encoding="utf-8").replace("package.alpha: on", "package.alpha: off"),
                    encoding="utf-8")
    plain = cli(engine, "-new", cwd=made.parent)
    key_plain = opened()
    played_plain = walk(key_plain)
    lit = cli(engine, "-new", cwd=made.parent, env={context.PACKAGES: "alpha=on"})
    key_lit = opened()
    played_lit = walk(key_lit, env={context.PACKAGES: "beta=off"})   # a keyed call under the variable: ignored
    new_line = next((json.loads(line) for line in (made / ".sys" / "state" / persistence_trace(made, key_lit))
                     .read_text(encoding="utf-8").splitlines() if '"new"' in line), {})
    if (plain.returncode == 0 and "alpha off" in heading(plain.stdout) and "▸ ALPHA" not in played_plain
            and lit.returncode == 0 and "alpha on" in heading(lit.stdout) and "beta on" in heading(lit.stdout)
            and "▸ ALPHA" in played_lit and "▸ BETA" in played_lit
            and slot(key_lit).get("switches") == {"alpha": "on"}
            and new_line.get("switches") == {"alpha": "on"} and not slot(key_plain).get("switches")):
        held("(b) PP_PACKAGES composes the first output", f"run {key_plain} on SETTINGS: alpha off, ALPHA never "
             f"played; run {key_lit} under PP_PACKAGES=alpha=on: alpha on at its first heading, ALPHA and BETA "
             "played, the trace's new line and the slot say the switch; a keyed call under the variable ignores it")
    else:
        failures.append(f"  ✗ (b) PP_PACKAGES             rc={plain.returncode}/{lit.returncode} "
                        f"plain={heading(plain.stdout)!r} lit={heading(lit.stdout)!r} "
                        f"alpha={'▸ ALPHA' in played_lit} slot={slot(key_lit).get('switches')} new={new_line} "
                        f"{lit.stderr[-200:]!r}")

    # --- (c) the three refusals write nothing -----------------------------------------------------
    before = slots()
    refused = {code: cli(engine, "-new", cwd=made.parent, env={context.PACKAGES: value})
               for code, value in (("packages-invalid", "alpha"), ("package-unpinned", "alpha=on,nowhere=on"),
                                   ("package-base", "kit=off"))}
    if all(one.returncode == 2 and code in one.stderr for code, one in refused.items()) and slots() == before:
        held("(c) the refusals write nothing", "packages-invalid (`alpha`), package-unpinned (`nowhere=on`), "
             "package-base (`kit=off`): rc 2, no slot added")
    else:
        failures.append("  ✗ (c) refusals                " + " ".join(f"{code}={one.returncode}:{one.stderr[-100:]!r}"
                                                                    for code, one in refused.items())
                        + f" slots={before}->{slots()}")
    return 0


def persistence_trace(made: Path, key: str) -> str:
    """-> the name of the run's trace file, read at its slot."""
    from conductor import persistence
    return persistence.trace_of(persistence.slot_of(made, key))
