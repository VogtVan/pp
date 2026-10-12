"""Scenario `bench-engine` -- 4 case(s):
- la-provenance: the conductor the bench judges comes from the source
- la-reprise-de-main: a vendored engine hands `-test` over to the engine of the source its
  instance declares
- la-base-par-aire: a root scenario's environment stands on the bench's stand-in for the
  base, any other area's on the product's kit; no root sector stands on the kit any more --
  `KIT_BOUND` is empty (rule 9)
- le-membre-temoin: `env.write_member()` writes the member a case needs at run time -- a proc
  attached at `boot.ready` the stand-in's BOOT calls, its laws in force on the first block,
  its tag resolved; the stand-in itself keeps its four files
"""
from __future__ import annotations

from pathlib import Path

import conductor
from conductor import instance, render
from tests.harness import ENGINE, KIT_BOUND, PRODUCT_ENGINE, WITNESSES, Bench, cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- la-provenance: one code judges, in process and in subprocess ---------------
    imported = Path(conductor.__file__).resolve().parent
    if imported == (ENGINE / "conductor").resolve():
        held("the bench judges the source", f"`conductor` is imported from {imported} -- "
             f"the same tree {PRODUCT_ENGINE.name} installs every throwaway instance from, "
             "so both halves of the bench judge one code")
    else:
        failures.append(f"  ✗ the engine judged           {imported} -- not {ENGINE / 'conductor'}")

    # --- la-reprise-de-main: the vendored engine hands the call over ----------------
    env = bench.env("relay")
    source_engine = Path(instance.read(env.made)["source"]) / "engine" / "pp.py"
    answer = cli(env.engine, "-test", "nothing-answers-to-this-name")
    if (f"bench on {source_engine}" in answer.stdout and answer.returncode == 2
            and "no scenario answers" in answer.stdout):
        held("a vendored engine hands the bench over", "its `-test` opens on the header line "
             "of the engine its instance declares as SOURCE and returns the usual refusal -- "
             "the call plays where the product lives, whatever was typed")
    else:
        failures.append(f"  ✗ the bench was not handed over rc {answer.returncode}: "
                        f"{answer.stdout[:160]!r}")

    # --- le-membre-temoin: the member a case needs, written at run time --------------------
    witnessed = bench.env("membered")
    written = witnessed.write_member("character: >-\n  curt, dry wit\nconstraints.behavior: |\n"
                               "  M1  your name is @MEMBER.name\n  M2  you behave: @MEMBER.character\n",
                               body="A terse witness.", name="Sextant")
    opener = witnessed.conductor("t")
    first = opener.start(opener.boot("BOOT.md"))
    texts = {one.code: one.text for one in first.constraints} if first is not None else {}
    kept = sorted(str(one.relative_to(WITNESSES / "kit")) for one in (WITNESSES / "kit").rglob("*")
                  if one.is_file() and "__pycache__" not in one.parts)
    if (written == witnessed.made / "procs" / "MEMBER.md"
            and first is not None and "▸ MEMBER" in first.stack
            and first.instruction is not None and first.instruction.keyword == "INFER"
            and texts.get("M1") == "your name is Sextant"
            and texts.get("M2") == "you behave: curt, dry wit"
            and "A terse witness." in render(first)
            and kept == ["package.yaml", "procs/BOOT.md", "procs/TURN.md", "system/SYSTEM.COMMON.md"]):
        held("env.write_member() writes the member at run time", "procs/MEMBER.md attached at "
             "boot.ready: the boot calls it first, M1 and M2 in force with their tags resolved, "
             f"its body served; the stand-in keeps its {len(kept)} files")
    else:
        failures.append(f"  ✗ the witness member          {written} stack={first and first.stack!r} "
                        f"{texts!r} kept={kept}")
    witnessed.conductor("t").forget()
    # --- la-base-par-aire: the stand-in at the root, the kit elsewhere ------------------
    vendored_kit = next((env.made / ".sys" / "vendor").glob("kit@*"))
    stand_in = instance.manifest_of(vendored_kit)
    elsewhere = Bench("kit")
    try:
        if ("STAND-IN" in str(stand_in.get("description", ""))
                and stand_in == instance.manifest_of(WITNESSES / "kit")
                and "base" not in instance.read(env.made)
                and bench.on_stand_in() and bench.engine() != PRODUCT_ENGINE
                and bench.source() == bench.engine().parent.parent
                and not elsewhere.on_stand_in() and elsewhere.engine() == PRODUCT_ENGINE
                and KIT_BOUND == ()):
            held("the base follows the area", "a root scenario's environment vendors the "
                 "bench's stand-in as `kit`, its manifest naming no `base:`, its source the "
                 "witness source; a bench of another area installs from the product's own "
                 "engine; KIT_BOUND names no sector")
        else:
            failures.append(f"  ✗ the base by area            {stand_in.get('description', '')[:40]!r} "
                            f"{bench.engine()} {elsewhere.engine()} {KIT_BOUND!r}")
    finally:
        elsewhere.teardown()

    return 0
