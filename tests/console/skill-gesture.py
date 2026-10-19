"""Scenario `skill-gesture` -- a skill called by `-s`: conducted as a CALL, played as a GESTURE:
- le-skill-est-un-call: an offered skill IS a CALL -- adoption on offer, its law in force
  with its frame and gone with it; an incompatible one orients, an unoffered copy is no name
- le-geste-dit-ou: a gesture renders no block -- the anchor line under a fusion, the
  address when two segments compete, and the run untouched either way
- le-manuel-a-l-appel-nu: a script called bare mounts its contract, body alone -- the
  manual through the one reader, the run where it stood
- la-dataclass-se-resout: a script declaring a dataclass under postponed annotations plays
  as a gesture through the console, exactly as it runs by hand
"""
from __future__ import annotations

import ast
import re

from conductor import Conductor, compiling, discovery, instance
from tests.harness import bench_key, cli, session_of

HOUSE_STYLE = "the house style, judged by its own law"   # the adopted skill's description
STAMP_LAW = "S1  a stamp is dated, never edited."           # the gesture's own law
MANUAL = "The manual of the witness: the verb `go` prints what it was given."

DATED = '''from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stamp:
    day: str


def main(argv):
    print(f"dated: {Stamp(day='2026-09-13').day}")
    return 0
'''


def laws(out: str) -> list[str]:
    """-> the CODES of the laws a rendered output's CONSTRAINTS section puts in force --
    rendered whole (`H1  ...`) or held as codes (`[H1 S1]`)."""
    lines, codes = out.splitlines(), []
    if "▌ CONSTRAINTS" not in lines:
        return codes
    for one in lines[lines.index("▌ CONSTRAINTS") + 1:]:
        if not one.strip():
            break
        if one.startswith("[") and one.endswith("]"):
            codes += one[1:-1].split()
        elif re.match(r"^[A-Z]+\d+\s", one):
            codes.append(one.split()[0])
    return codes


def deviation(out: str) -> str:
    """-> the first line of the DEVIATION section of a rendered output, "" without one."""
    lines = out.splitlines()
    return next((lines[at + 1] for at, one in enumerate(lines[:-1]) if one == "▌ DEVIATION"), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- le-skill-est-un-call: an offered skill IS a CALL -- adoption on offer --------
    adopt_made = bench.env("aws").made
    adopt_ws = adopt_made.parent
    adopt_engine = adopt_made / ".sys" / "engine" / "pp.py"
    adopt_member = discovery.instance_member(adopt_engine)
    for stem, text in (
            ("housestyle", f"---\nname: housestyle\ndescription: {HOUSE_STYLE}\n"
                           "constraints.behavior: |\n  H1  the house voice is plain and short.\n---\n"
                           "Apply the house style to the work at hand.\n"),
            ("rawtool", "just prose, no front matter\n"),
            ("hidden", "---\nname: hidden\ndescription: compatible but never offered\n---\n"
                       "unreachable\n")):
        harness_home = adopt_ws / ".claude" / "skills" / stem
        harness_home.mkdir(parents=True)
        (harness_home / "SKILL.md").write_text(text, encoding="utf-8")
    stamp_home = adopt_made / "skills" / "stamp"
    stamp_home.mkdir(parents=True)
    (stamp_home / "SKILL.md").write_text(
        "---\nname: stamp\ndescription: a deterministic stamp under its own law\n"
        f"constraints.behavior: |\n  {STAMP_LAW}\n---\nrun it.\n",
        encoding="utf-8")
    (stamp_home / "stamp.py").write_text(
        "def main(argv):\n    print('stamp: done')\n    return 0\n", encoding="utf-8")
    witness_home = adopt_made / "skills" / "manual"     # a script whose contract is its MANUAL
    witness_home.mkdir(parents=True)
    (witness_home / "SKILL.md").write_text(
        f"---\nname: manual\ndescription: a witness whose contract is its manual\n---\n{MANUAL}\n",
        encoding="utf-8")
    (witness_home / "manual.py").write_text(
        "def main(argv):\n    print('ran: ' + ' '.join(argv))\n    return 0\n", encoding="utf-8")
    (adopt_made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\ntools: |\n  +housestyle\n  +rawtool\n  +stamp\n  +manual\n---\n",
        encoding="utf-8")
    (adopt_made / "procs" / "CATALOG.md").write_text(   # the SAME name on two scopes: the
        "---\nname: CATALOG\nkind: proc\ndescription: a catalog said at the boot\n"   # boot
        "attach: boot.ready\noutput: any\ntools: |\n  stamp\nproc: |\n  INFER\n---\n"   # fuses
        "the catalog.\n", encoding="utf-8")                                                # both

    adopt_catalog = compiling.render_tools(adopt_member.meta)
    adopt_registry = compiling.render_registry(adopt_member.meta)
    adopt_warnings = compiling.lint(adopt_member.meta)
    adopted = instance.adopted(adopt_member.meta, "housestyle")
    raw = instance.adopted(adopt_member.meta, "rawtool")
    lacking = compiling.conductible(raw) if raw is not None else ""
    if (adopted is not None and f"- **`housestyle`** (harness) — {HOUSE_STYLE}\n  contract: {adopted}\n" in adopt_catalog
            and "- `rawtool`" in adopt_catalog and "**`rawtool`**" not in adopt_catalog
            and "hidden" not in adopt_catalog
            and "`H1`" in adopt_registry and "hidden" not in adopt_registry
            and lacking and any("offered-not-conductible: `rawtool`" in one and lacking in one
                                for one in adopt_warnings)
            and not any("housestyle" in one for one in adopt_warnings)):
        held("adoption on offer", "an offered harness skill joins the catalog FULL and the "
             "registry; the incompatible one stays name-only, the warning says why; "
             "the unoffered copy is invisible")
    else:
        failures.append(f"  ✗ adoption                    {adopt_warnings!r}")

    def adopt_c() -> Conductor:
        return Conductor(adopt_member, adopt_engine, "t")

    adopt_settings = adopt_made / "SETTINGS.md"      # the bench pins fusion off: this
    adopt_settings.write_text(adopt_settings.read_text(encoding="utf-8")   # case needs it ON
                              .replace("instructions_fusion: none",
                                       "instructions_fusion: max"), encoding="utf-8")
    adopt_c().start(adopt_c().boot("BOOT.md"))   # the boot's FUSED output stands
    # --- le-geste-dit-ou: the address decides, the anchor line says where it landed ---
    before_boot = session_of(adopt_member.meta).read_bytes()
    ambiguous = cli(adopt_engine, "-s", "stamp", "now")
    addressed = cli(adopt_engine, "-s", "stamp@2", "now")
    anchor_line = addressed.stdout.splitlines()[0] if addressed.stdout else ""
    if (ambiguous.returncode == 2 and "address-ambiguous" in ambiguous.stderr
            and "[1, 2]" in ambiguous.stderr and "nothing played" in ambiguous.stderr
            and addressed.returncode == 0 and "stamp: done" in addressed.stdout
            and anchor_line.startswith("◀ pp · [2] ") and "▌" not in addressed.stdout
            and STAMP_LAW not in addressed.stdout
            and session_of(adopt_member.meta).read_bytes() == before_boot):
        held("a gesture says WHERE it hooked", "two segments offer the name: bare REFUSES, "
             "`@n` plays -- one anchor line for the owning segment, then the skill's "
             "output; no block, no laws, and the run stands where it stood")
    else:
        failures.append(f"  ✗ anchor line                 rc={ambiguous.returncode}/"
                        f"{addressed.returncode} {ambiguous.stderr[:90]!r} {anchor_line!r}")

    adopt_c().submit("")                       # CATALOG said -> the turn's step stands
    played = cli(adopt_engine, "-s", "housestyle")
    if (played.returncode == 0 and "▸ housestyle{1/1}" in played.stdout
            and "H1" in laws(played.stdout)
            and "NEXT INSTRUCTION CONTEXT — housestyle" in played.stdout
            and "▶ CONTINUE" in played.stdout):
        held("an offered skill is a CALL", "adopted and played: a frame opens, H1 in force, "
             "the body the brief, an implicit INFER carries the work")
    else:
        failures.append(f"  ✗ skill-as-call               rc={played.returncode} "
                        f"in force={laws(played.stdout)} "
                        f"{played.stdout[:150]!r} {played.stderr[:80]!r}")

    adopt_closed = cli(adopt_engine, bench_key(adopt_member.meta))
    adopt_back = adopt_c().resume(adopt_c().boot("BOOT.md"))
    if (adopt_closed.returncode == 0 and adopt_back is not None
            and "housestyle" not in adopt_back.stack
            and not any(one.code == "H1" for one in adopt_back.constraints)):
        held("the adopted frame pops clean", "closed, the law falls with its frame -- "
             "the turn resumes without H1")
    else:
        failures.append(f"  ✗ adopted pop                 {adopt_back and adopt_back.stack!r}")

    before_stamp = session_of(adopt_member.meta).read_bytes()
    stamped = cli(adopt_engine, "-s", "stamp", "now")
    if (stamped.returncode == 0 and "stamp: done" in stamped.stdout
            and STAMP_LAW not in stamped.stdout
            and "pp ·" not in stamped.stdout
            and session_of(adopt_member.meta).read_bytes() == before_stamp):
        held("a script is a GESTURE", "no block, no law rendered -- the skill's own guard "
             "refuses by name, and the run stands exactly where it stood")
    else:
        failures.append(f"  ✗ script gesture              rc={stamped.returncode} "
                        f"{stamped.stdout[:150]!r}")
    # --- le-manuel-a-l-appel-nu: a script called bare mounts its contract, body alone ------
    adopt_key = bench_key(adopt_member.meta)
    before_manual = adopt_c().peek()
    manual = cli(adopt_engine, "-s", "manual")
    after_manual = adopt_c().peek()
    ran = cli(adopt_engine, "-s", "manual", "go", "now")
    ledger = cli(adopt_engine, "-stats", "--blocks")   # the bench's run key is no hex
    standing = (before_manual is not None and after_manual is not None
                and (before_manual.stack, before_manual.position, before_manual.command)
                == (after_manual.stack, after_manual.position, after_manual.command))
    if (manual.returncode == 0 and "INFORMATION — manual" in manual.stdout
            and MANUAL in manual.stdout
            and "▶ CONTINUE" in manual.stdout and "ran:" not in manual.stdout
            and standing
            and ran.returncode == 0 and "ran: go now" in ran.stdout and "▌" not in ran.stdout
            and any("manual" in row and "mount" in row for row in ledger.stdout.splitlines())):
        held("a script called bare mounts its MANUAL", "the contract's body enters the view "
             "under INFORMATION, the standing block under it, the run where it stood; with "
             "an argument the script runs as before; the ledger says `mount`")
    else:
        failures.append(f"  ✗ bare manual                 rc={manual.returncode}/{ran.returncode} "
                        f"standing={standing} {manual.stdout[:120]!r} {ran.stdout[:60]!r}")

    usage = ast.get_docstring(ast.parse(adopt_engine.read_text(encoding="utf-8"))).splitlines()[0]
    before_raw = session_of(adopt_member.meta).read_bytes()
    oriented_raw = cli(adopt_engine, "-s", "rawtool")
    invisible = cli(adopt_engine, "-s", "hidden")
    if (oriented_raw.returncode == 0 and len(oriented_raw.stdout.splitlines()) == 1
            and "`rawtool`" in oriented_raw.stdout and "▌" not in oriented_raw.stdout
            and session_of(adopt_member.meta).read_bytes() == before_raw
            and invisible.returncode == 2 and "▌ pp · " in invisible.stdout
            and deviation(invisible.stdout).startswith("`hidden` ")
            and usage not in (invisible.stdout + invisible.stderr)):
        held("indifferent and invisible", "offered-incompatible orients, 0 effect; an "
             "unoffered harness copy is not even a name -- the pending block answers, never the usage")
    else:
        failures.append(f"  ✗ indifferent/invisible       {oriented_raw.returncode}/"
                        f"{invisible.returncode}")
    # --- la-dataclass-se-resout: the console loads a script as it runs by hand ------------
    dated_env = bench.env("loading")
    dated_home = dated_env.made / "skills" / "dated"
    dated_home.mkdir(parents=True)
    (dated_home / "SKILL.md").write_text(
        "---\nname: dated\ndescription: a stamp carried by a dataclass\n---\nrun it.\n",
        encoding="utf-8")
    (dated_home / "dated.py").write_text(DATED, encoding="utf-8")
    (dated_env.made / "procs" / "TURN.md").write_text(      # the turn offers it: an overlay
        "---\nname: TURN\ntools: |\n  +dated\n---\n", encoding="utf-8")
    dated_opened = dated_env.cli("-new")
    dated = dated_env.cli("-s", "dated", "now")
    if (dated_opened.returncode == 0 and dated.returncode == 0
            and "dated: 2026-09-13" in dated.stdout and "Traceback" not in dated.stderr):
        held("a dataclass skill plays as a gesture",
             "`./pp -s dated` runs the script in the console's process: its dataclass "
             "resolves its module, the skill prints what it prints by hand")
    else:
        failures.append(f"  ✗ dataclass gesture          rc={dated.returncode} "
                        f"{(dated.stderr or dated.stdout).strip().splitlines()[-1:]!r}")

    return 0
