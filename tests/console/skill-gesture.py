"""Scenario `skill-gesture` -- 4 case(s), in the monolith's order:
- le-skill-est-un-call: an offered skill IS a CALL -- adoption on offer
- le-geste-dit-ou: a gesture renders no block -- the anchor line under a fusion, the
  address when two segments compete, and the run untouched either way
- le-manuel-a-l-appel-nu: a script called bare mounts its contract, body alone -- the
  manual through the one reader, chunked at the cap, the run where it stood
- le-bloc-pendant-repond: a name declared NOWHERE gets the pending block, never the usage
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, compiling, discovery
from tests.harness import bench_key, cli, session_of


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- le-skill-est-un-call: an offered skill IS a CALL -- adoption on offer --------
    adopt_made = bench.env("aws").made
    adopt_ws = adopt_made.parent
    adopt_engine = adopt_made / ".sys" / "engine" / "pp.py"
    adopt_member = discovery.instance_member(adopt_engine)
    for stem, text in (
            ("housestyle", "---\nname: housestyle\ndescription: the house style, judged by its own law\n"
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
        "constraints.behavior: |\n  S1  a stamp is dated, never edited.\n---\nrun it.\n",
        encoding="utf-8")
    (stamp_home / "stamp.py").write_text(
        "def main(argv):\n    print('stamp: done')\n    return 0\n", encoding="utf-8")
    # two witnesses whose contract is their MANUAL: one under the host's cap, one over it
    for stem, body in (("manual", "The manual of the witness: the verb `go` prints what it "
                                  "was given.\n"),
                       ("long", "The long manual.\n"
                                + "A line of the long manual, one of many.\n" * 120)):
        witness_home = adopt_made / "skills" / stem
        witness_home.mkdir(parents=True)
        (witness_home / "SKILL.md").write_text(
            f"---\nname: {stem}\ndescription: a witness whose contract is its manual\n---\n{body}",
            encoding="utf-8")
        (witness_home / f"{stem}.py").write_text(
            "def main(argv):\n    print('ran: ' + ' '.join(argv))\n    return 0\n",
            encoding="utf-8")
    (adopt_made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\ntools: |\n  +housestyle\n  +rawtool\n  +stamp\n  +manual\n  +long\n---\n",
        encoding="utf-8")
    (adopt_made / "procs" / "CAPABILITIES.md").write_text(   # the SAME name on two scopes:
        "---\nname: CAPABILITIES\ntools: |\n  +stamp\n---\n", encoding="utf-8")   # the boot fuses both

    adopt_catalog = compiling.render_tools(adopt_member.meta)
    adopt_registry = compiling.render_registry(adopt_member.meta)
    adopt_warnings = compiling.lint(adopt_member.meta)
    if ("Adopted skills (offered from your harness)" in adopt_catalog
            and "the house style, judged by its own law" in adopt_catalog
            and "- `rawtool`" in adopt_catalog and "hidden" not in adopt_catalog
            and "`H1`" in adopt_registry and "hidden" not in adopt_registry
            and any("offered-not-conductible: `rawtool`" in one and "no front matter" in one
                    for one in adopt_warnings)
            and not any("housestyle" in one for one in adopt_warnings)):
        held("adoption on offer", "an offered harness skill joins the catalog FULL and the "
             "registry; the incompatible one stays name-only, the warning says why; "
             "the unoffered copy is invisible")
    else:
        failures.append(f"  ✗ adoption                    {adopt_warnings!r}")

    def adopt_c() -> Conductor:
        return Conductor(adopt_member, discovery.siblings_around(adopt_member), adopt_engine, "t")

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
            and "S1  a stamp is dated" not in addressed.stdout
            and session_of(adopt_member.meta).read_bytes() == before_boot):
        held("a gesture says WHERE it hooked", "two segments offer the name: bare REFUSES, "
             "`@n` plays -- one anchor line for the owning segment, then the skill's "
             "output; no block, no laws, and the run stands where it stood")
    else:
        failures.append(f"  ✗ anchor line                 rc={ambiguous.returncode}/"
                        f"{addressed.returncode} {ambiguous.stderr[:90]!r} {anchor_line!r}")

    adopt_c().submit("")                       # CAPABILITIES said -> the turn's step stands
    played = cli(adopt_engine, "-s", "housestyle")
    if (played.returncode == 0 and "▸ housestyle{1/1}" in played.stdout
            and "H1  the house voice is plain and short." in played.stdout
            and "NEXT INSTRUCTION CONTEXT — housestyle" in played.stdout
            and "▶ CONTINUE" in played.stdout):
        held("an offered skill is a CALL", "adopted and played: a frame opens, H1 in force, "
             "the body the brief, an implicit INFER carries the work")
    else:
        failures.append(f"  ✗ skill-as-call               rc={played.returncode} "
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
            and "S1  a stamp is dated, never edited." not in stamped.stdout
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
            and "the verb `go` prints what it was given" in manual.stdout
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
    adopt_settings.write_text(adopt_settings.read_text(encoding="utf-8")
                              .replace("max_harness_tool_output: 60000",
                                       "max_harness_tool_output: 3000"), encoding="utf-8")
    first_chunk = cli(adopt_engine, "-s", "long")
    rest_chunk = cli(adopt_engine, adopt_key)
    adopt_settings.write_text(adopt_settings.read_text(encoding="utf-8")
                              .replace("max_harness_tool_output: 3000",
                                       "max_harness_tool_output: 60000"), encoding="utf-8")
    if (first_chunk.returncode == 0 and "a reading continues" in first_chunk.stdout
            and "one of many" not in first_chunk.stdout
            and rest_chunk.returncode == 0 and "one of many" in rest_chunk.stdout
            and "INFORMATION — long" in first_chunk.stdout + rest_chunk.stdout):
        held("a manual over the cap comes in chunks", "the first output closes on the seam, "
             "the bare call serves the rest -- the manual is read whole, never truncated")
    else:
        failures.append(f"  ✗ long manual                 rc={first_chunk.returncode}/"
                        f"{rest_chunk.returncode} {first_chunk.stdout[-160:]!r}")

    oriented_raw = cli(adopt_engine, "-s", "rawtool")
    invisible = cli(adopt_engine, "-s", "hidden")
    if (oriented_raw.returncode == 0 and "yours, through your harness" in oriented_raw.stdout
            and invisible.returncode == 2
            and "`hidden` is not offered at this step" in invisible.stdout
            and "The KEY leads" not in (invisible.stdout + invisible.stderr)):
        held("indifferent and invisible", "offered-incompatible orients, 0 effect; an "
             "unoffered harness copy is not even a name -- the pending block answers, never the usage")
    else:
        failures.append(f"  ✗ indifferent/invisible       {oriented_raw.returncode}/"
                        f"{invisible.returncode}")
    # --- le-bloc-pendant-repond: a stranger gets the pending block, never the usage ---------
    # the witness (S1.09, 2026-08-26): `-s NOPE` printed the console's docstring, exit 1;
    # the card says the pending block answers an ask offered nowhere
    stranger = cli(adopt_engine, "-s", "NOPE")
    if (stranger.returncode == 2 and "`NOPE` is not offered at this step" in stranger.stdout
            and "The conductor's entry point" not in stranger.stdout + stranger.stderr):
        held("a stranger gets the pending block",
             "no usage dump: the pending block with its deviation, exit 2 like any denied ask")
    else:
        failures.append(f"  ✗ stranger                    rc={stranger.returncode} "
                        f"{(stranger.stdout + stranger.stderr)[-200:]!r}")

    return 0
