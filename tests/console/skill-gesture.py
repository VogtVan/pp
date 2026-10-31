"""Scenario `skill-gesture` -- a script called by `-s`, played as a GESTURE:
- le-geste-dit-ou: a gesture renders no block -- the anchor line under a fusion, the
  address when two segments compete, and the run untouched either way; a script is a gesture,
  its own law never rendered
- le-manuel-a-l-appel-nu: a script called bare mounts its contract, body alone -- the
  manual through the one reader, the run where it stood
- la-dataclass-se-resout: a script declaring a dataclass under postponed annotations plays
  as a gesture through the console, exactly as it runs by hand
A skill adopted on offer and played as a CALL is the pattern `composition/adoption`.
"""
from __future__ import annotations

from conductor import Conductor, discovery
from tests.harness import bench_key, cli, session_of

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


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the house of the gestures: two scripts offered, one of them on two scopes --------
    adopt_made = bench.env("aws").made
    adopt_engine = adopt_made / ".sys" / "engine" / "pp.py"
    adopt_member = discovery.instance_member(adopt_engine)
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
        "---\nname: TURN\ntools: |\n  +stamp\n  +manual\n---\n",
        encoding="utf-8")
    (adopt_made / "procs" / "CATALOG.md").write_text(   # the SAME name on two scopes: the
        "---\nname: CATALOG\nkind: proc\ndescription: a catalog said at the boot\n"   # boot
        "attach: boot.initialize\noutput: any\ntools: |\n  stamp\nproc: |\n  INFER\n---\n"   # fuses
        "the catalog.\n", encoding="utf-8")                                                # both

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

    adopt_c().submit("")                       # CATALOG said -> the turn runs to its end: the run parks

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
            and "▶ AWAIT" in manual.stdout and "ran:" not in manual.stdout
            and standing
            and ran.returncode == 0 and "ran: go now" in ran.stdout and "▌" not in ran.stdout
            and any("manual" in row and "mount" in row for row in ledger.stdout.splitlines())):
        held("a script called bare mounts its MANUAL", "the contract's body enters the view "
             "under INFORMATION, the standing block under it, the run where it stood; with "
             "an argument the script runs as before; the ledger says `mount`")
    else:
        failures.append(f"  ✗ bare manual                 rc={manual.returncode}/{ran.returncode} "
                        f"standing={standing} {manual.stdout[:120]!r} {ran.stdout[:60]!r}")

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
