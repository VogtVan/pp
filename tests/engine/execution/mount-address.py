"""Scenario `mount-address` -- a document mounts by its address:
- on an instance the engine addresses (`--instance`), a script called bare serves its manual:
  the body of its `SKILL.md`, found by the skill's name, no traceback
- the slot keeps the ADDRESSES -- a package's document by its bare NAME, a file of the bundle by
  `<package>:<path>` -- and after `doctor` re-materializes the machine a `-compacted` serves the
  mounted bodies again
- a vendored twin mounts the same document by its old instance path and by its name: the
  two blocks are identical to the byte, and identical to the addressed instance's
- the switch sees every form of address: a manual mounted by the skill's
  name and a `<package>:<path>` alone standing, `-disable` refuses `package-in-flight` and names
  both, nothing written
The mount by each form of address, `mount-missing` and `mount-gone` are the pattern
`context/addressing`'s (`tests/patterns/context/addressing.py`).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from conductor import discovery, install, persistence
from tests.harness import INSTANCE, bench_key, cli, steady

MANIFEST = """name: wit
version: 0.0.1
description: a witness -- a document, a file outside the search paths, a script that mounts them
requires: [kit]
"""
WIT = """---
name: WIT
kind: doc
description: the witness document a script mounts by its name
constraints.production: |
  W1  the witness law rides the block.
---
The witness body, served by its name.
"""
NOTE_BODY = "The note body, served by its package's address."
NOTE = f"""---
name: NOTE
kind: doc
description: a file of the bundle no search path reaches
constraints.production: |
  W2  the note law rides the block.
---
{NOTE_BODY}
"""
TURN_OVERLAY = """---
name: TURN
tools: |
  +pp-wit
---
"""
CONTRACT = """---
name: pp-wit
description: the witness script -- `mount` mounts WIT.md by its name, `kind` the note by its package's address
---
The witness manual, served when the script is called bare.
"""
SCRIPT = """import json


def main(argv):
    verb = argv[0] if argv else ""
    doc = {"mount": "WIT.md", "kind": "wit:kinds/NOTE.md"}.get(verb, verb)
    print("::mount " + json.dumps([{"doc": doc, "scope": "stacked", "body": True}]))
    return 0
"""
CHUNK = re.compile(r"^\./pp \S+\s+\(a reading continues", re.M)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    source = bench.source_with("kit-witness").parent.parent
    wit = source / "packages" / "wit"
    for relpath, text in (("package.yaml", MANIFEST), ("procs/WIT.md", WIT), ("kinds/NOTE.md", NOTE),
                          ("overlays/TURN.md", TURN_OVERLAY), ("skills/pp-wit/SKILL.md", CONTRACT),
                          ("skills/pp-wit/pp-wit.py", SCRIPT)):
        path = wit / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    script = source / "engine" / "pp.py"
    addressed = install.install(script, bench.temp() / "addressed" / INSTANCE, ["wit"])
    vendored = install.install(script, bench.temp() / "vendored" / INSTANCE, ["wit"])
    addressed_engine = addressed / ".sys" / "engine" / "pp.py"

    def call(engine: Path, made: Path, *args: str):
        return cli(engine, "--instance", str(made), *args, cwd=made.parent)

    def whole(engine: Path, made: Path, key: str, text: str) -> str:
        """-> the output whole: the chunks after the first, each read on the LAST call's
        text alone -- a chunk already read must not trigger one more bare call, which
        would advance the run past its pending step."""
        whole_text, last = text, text
        for _ in range(20):
            if not CHUNK.search(last):
                break
            last = call(engine, made, key).stdout
            whole_text += last
        return whole_text

    def opened(engine: Path, made: Path) -> str:
        run = call(engine, made, "-new")
        key = bench_key(made)
        whole(engine, made, key, run.stdout)
        return key

    # --- the manual, by the skill's name -----------------------------------------------------------
    key = opened(addressed_engine, addressed)
    manual = call(addressed_engine, addressed, key, "-s", "pp-wit")
    if (manual.returncode == 0 and "The witness manual" in manual.stdout
            and "Traceback" not in manual.stdout + manual.stderr):
        held("a bare script serves its manual", "the SKILL.md body found by the skill's "
             "name, rc 0, no traceback")
    else:
        failures.append(f"  ✗ manual by name              rc={manual.returncode} "
                        f"{manual.stdout[-200:]!r} {manual.stderr[-400:]!r}")

    # --- a package's document by its name, a bundle's file by its package's address --------------
    call(addressed_engine, addressed, key, "-s", "pp-wit", "mount")
    call(addressed_engine, addressed, key, "-s", "pp-wit", "kind")

    # --- the slot keeps the addresses; the machine re-materialized, the bodies serve again ------
    kept = [one.get("doc") for one in persistence.mounted_of(persistence.slot_of(addressed, key))]
    install.doctor(discovery.member_at(addressed))
    home_engine = addressed / ".sys" / "engine" / "pp.py"
    again = call(home_engine, addressed, key, "-compacted")
    text = whole(home_engine, addressed, key, again.stdout)
    if (kept == ["pp-wit", "WIT.md", "wit:kinds/NOTE.md"] and home_engine.is_file()
            and again.returncode == 0 and "The witness body, served by its name." in text
            and NOTE_BODY in text):
        held("the slot keeps the addresses", f"{kept}; after doctor, -compacted serves both "
             "bodies from the machine re-materialized")
    else:
        failures.append(f"  ✗ addresses at the slot       kept={kept} rc={again.returncode} "
                        f"{text[-300:]!r} {again.stderr[-300:]!r}")

    # --- the vendored twin: the old path and the name mount the same block ------------------------
    vkey = opened(vendored / ".sys" / "engine" / "pp.py", vendored)
    vengine = vendored / ".sys" / "engine" / "pp.py"
    old_path = ".sys/vendor/wit@0.0.1/procs/WIT.md"
    by_path = call(vengine, vendored, vkey, "-s", "pp-wit", old_path)
    vkey2 = opened(vengine, vendored)
    by_name = call(vengine, vendored, vkey2, "-s", "pp-wit", "mount")
    skey = opened(home_engine, addressed)
    on_twin = call(home_engine, addressed, skey, "-s", "pp-wit", "mount")

    def body(out: str, run: str) -> str:
        return steady(out).replace(run, "<key>")

    blocks = [body(by_path.stdout, vkey), body(by_name.stdout, vkey2), body(on_twin.stdout, skey)]
    if (by_path.returncode == by_name.returncode == on_twin.returncode == 0
            and blocks[0] == blocks[1] == blocks[2] and "The witness body" in blocks[0]):
        held("the old path and the name mount alike", f"{len(blocks[0])} chars, identical: the vendored "
             "instance path, the name, the name on the addressed instance")
    else:
        at = next((i for i, (x, y) in enumerate(zip(blocks[0], blocks[1])) if x != y), None)
        failures.append(f"  ✗ vendored twin               rc={by_path.returncode}/{by_name.returncode}/"
                        f"{on_twin.returncode} first difference at {at}: "
                        f"{blocks[0][at:at+80] if at is not None else ''!r} / "
                        f"{blocks[1][at:at+80] if at is not None else ''!r} {by_path.stderr[-200:]!r}")

    # --- the switch sees every form of address --------------------------------------------------
    # a run where the manual (the skill's name) and the qualified address ALONE stand: no frame
    # of the package, no name a search path answers -- the two forms a switch once passed by
    fkey = opened(home_engine, addressed)
    call(home_engine, addressed, fkey, "-s", "pp-wit")
    call(home_engine, addressed, fkey, "-s", "pp-wit", "kind")
    switched = call(home_engine, addressed, fkey, "-disable", "wit")
    fslot = persistence.slot_of(addressed, fkey)

    def traced() -> list[dict]:
        return [json.loads(one) for one in
                (fslot.parent / persistence.trace_of(fslot)).read_text(encoding="utf-8").splitlines()
                if one.strip()]

    if (switched.returncode == 2 and "package-in-flight" in switched.stderr
            and "pp-wit" in switched.stderr and "wit:kinds/NOTE.md" in switched.stderr
            and not persistence.off_of(fslot)
            and not any(one.get("kind") == "switch" for one in traced())):
        held("the switch sees every form of address", "the manual by the skill's name and "
             "`wit:kinds/NOTE.md` alone standing: `-disable wit` refuses package-in-flight, names "
             "both addresses, writes no `off` at the slot and no `switch` at the trace")
    else:
        failures.append(f"  ✗ switch by address           rc={switched.returncode} "
                        f"{switched.stdout[-120:]!r} {switched.stderr[-300:]!r} "
                        f"off={persistence.off_of(fslot)}")

    return 0
