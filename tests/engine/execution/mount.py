"""Scenario `mount` -- 9 case(s), in the monolith's order:
- the MOUNT verb: hosted documents ride the exchange
- le-serve-au-mount: the mount plays the serves, the degradation is soft
- le-corps-une-fois: a reading proven in the run renders nothing at the mount either
- the shared records never lose: the lock serializes the read-modify-write
- le-serve-stale-reel: the soft degradation LATCHES -- the signal is real
- le-mount-atomique: a row that refuses mounts NOTHING -- the state is untouched
- le-mount-atomique: the same mount, replayed once the row is repaired, mounts whole
- le-mount-refuse-au-banc: a CHAIN whose last document refuses mounts none of them
- le-mount-qui-recharge: a mount re-shows the standing step -- the pointer stands
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from conductor import Conductor, Refusal, revive, compiling, discovery, navigation, persistence, render
from tests.harness import document, session_of, steady, SOURCE


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- the first environment: three instances side by side, `core` the home
    town = bench.town(["core", "perso", "sw7-hub"])
    siblings = town.siblings
    home = town["core"].member
    script = town["core"].engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")


    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, siblings, script, "t")


    # --- the MOUNT verb: hosted documents ride the exchange ----------------------------
    mnt_siblings = bench.town(["core"]).siblings
    mnt_home = discovery.member(mnt_siblings, "core")

    def mnt_c() -> Conductor:
        return Conductor(mnt_home, mnt_siblings, script, "t")

    (mnt_home.meta / "MFORMS.md").write_text(
        "---\nname: MFORMS\ndescription: mount bench formats\nformats: |\n"
        "  json  inline  one valid JSON value\n---\n", encoding="utf-8")
    (mnt_home.meta / "EXT.md").write_text(
        "---\nname: EXT\nconstraints.production: |\n  X1  the hosted law binds.\ntools: |\n"
        "  TAGGED\n---\n\nThe hosted body.\n", encoding="utf-8")
    (mnt_home.meta / "EXT2.md").write_text(
        "---\nname: EXT2\nconstraints.production: |\n  X2  the second hosted law binds.\n---\n\n"
        "quiet matter\n", encoding="utf-8")
    mnt_doc = document("---\nname: MJOB\ncycle: true\noutput: json\nproc: |\n"
                       "  INFER\n  PICK member\n---\n", at=mnt_home.meta)
    mnt_c().start(mnt_doc)
    mnt_said = mnt_c().mount([{"doc": "EXT.md", "body": True}, {"doc": "EXT2.md"}])
    mnt_block = mnt_c().peek()
    mnt_codes = [one.code for one in mnt_block.constraints]
    mnt_tools = [one.name for one in mnt_block.tools]
    if ("X1" in mnt_codes and "X2" in mnt_codes and "TAGGED" in mnt_tools
            and "The hosted body." in mnt_said):
        held("a mount rides the view", "hosted laws and tools at the block, the asked-for body served")
    else:
        failures.append(f"  ✗ mount rides                 {mnt_codes} {mnt_tools}")

    mnt_ctl = mnt_c()
    mnt_stack = mnt_ctl._rebind(persistence.restore(session_of(mnt_home.meta), revive))
    mnt_frame = navigation.current(mnt_stack)
    mnt_owed = mnt_ctl._check_prove(mnt_stack, mnt_frame, navigation.peek(mnt_frame),
                                    '[{"code": "Q9", "evidence": "x", "verdict": "ok"}]')
    mnt_fine = mnt_ctl._check_prove(mnt_stack, mnt_frame, navigation.peek(mnt_frame),
                                    '[{"code": "X1", "evidence": "held", "verdict": "ok"},'
                                    ' {"code": "X2", "evidence": "held", "verdict": "ok"}]')
    if "Q9" in mnt_owed and "not in force" in mnt_owed and mnt_fine == "":
        held("a mounted law is judged at the proof", "X1/X2 stand in force like any law -- "
             "named, they pass; a stranger code is refused")
    else:
        failures.append(f"  ✗ mount proof                 {mnt_owed!r} {mnt_fine!r}")

    expect("mount-collision", lambda: mnt_c().mount([{"doc": "EXT.md"}]))
    expect("mount-missing", lambda: mnt_c().mount([{"doc": "GHOST.md"}]))
    expect("mount-invalid", lambda: mnt_c().mount(["EXT.md"]))

    mnt_c().submit('["a", "b"]')                # the INFER feeds the PICK -- X1 rides it
    mnt_swept = mnt_c().submit("a")             # the cycling floor exhausts: the rewind
    mnt_left = [one.code for one in mnt_swept.constraints]
    if ("X1" not in mnt_left and "X2" not in mnt_left
            and persistence.mounted_of(session_of(mnt_home.meta)) == []):
        held("a mount lives one exchange", "the rewind sweeps the hosted documents -- no stale law")
    else:
        failures.append(f"  ✗ mount sweep                 {mnt_left}")

    mnt_out = mnt_c().mount([{"doc": "EXT.md", "scope": "nested", "body": True},
                             {"doc": "EXT2.md", "body": True}])
    mnt_seg = mnt_out.split("▌ [2]")[0]
    if ("▸ EXT" in mnt_out and "▌ [2]" in mnt_out
            and "X1  the hosted law binds." in mnt_seg
            and "The hosted body." in mnt_seg
            and "[X1]" in mnt_out and "quiet matter" in mnt_out
            and mnt_out.count("X1  the hosted law binds.") == 1):
        held("a nested mount stacks its scope", "own numbered heading, laws verbatim at home, "
             "held as codes at the pending block; the stacked one rides the frame")
    else:
        failures.append(f"  ✗ nested mount                {mnt_out[:160]!r}")

    mnt_routed = mnt_c().route("TAGGED", 1)
    if mnt_routed and mnt_routed.get("frame") == "EXT":
        held("a mounted segment is addressable", "route @1 answers the mounted scope, like any fused segment")
    else:
        failures.append(f"  ✗ mount route                 {mnt_routed!r}")

    expect("mount-invalid", lambda: mnt_c().mount([{"doc": "EXT.md", "scope": "beside"}]))

    # --- le-serve-au-mount: the mount plays the serves, the degradation is soft --------
    (mnt_home.meta / "GROUND.md").write_text(
        "---\nname: GROUND\ndescription: the framing's reading\n---\n"
        "the encyclopedic ground\n", encoding="utf-8")
    (mnt_home.meta / "NODE.md").write_text(
        "---\nname: NODE\nconstraints.behavior: |\n  N1  the node's law.\nserve: |\n"
        "  GROUND.md GHOSTED.md\n  MFORMS.md[2-99]\n---\n\nnode prose\n", encoding="utf-8")
    served_out = mnt_c().mount([{"doc": "NODE.md"}])
    if ("the encyclopedic ground" in served_out
            and "GHOSTED.md" in served_out and "(this section's document is gone)" in served_out
            and "INFORMATION — MFORMS.md[2-99]" in served_out
            and "INFORMATION — GROUND.md" in served_out):
        held("the mount plays the serves, soft", "the framing's readings ride the mount, each "
             "titled by its token as written (path and range); a gone document skips with "
             "its note, a clipped range clamps -- nothing refuses")
    else:
        failures.append(f"  ✗ mount serves                {served_out[:160]!r}")

    # --- le-serve-stale-reel: the soft degradation LATCHES -- the signal is real --------
    # the gone document above pushed serve-stale; the push is BARE (a vector is the
    # typed channel of the improvement families), so the bus accepts it and the run
    # holds the latch -- before the fix, the document-name vector refused
    # family-unknown in silence and the signal never landed anywhere
    stale_latched = [one for one in persistence.signals_of(session_of(mnt_home.meta))
                     if one.get("signal") == "serve-stale"]
    if stale_latched and stale_latched[0].get("n", 0) >= 1:
        held("a stale serve latches for real",
             f"serve-stale rides the slot (n={stale_latched[0]['n']}) -- the improve "
             "will say it; the reading's note already oriented the agent")
    else:
        failures.append(f"  ✗ serve-stale never lands     latches: {stale_latched!r}")

    # --- le-corps-une-fois: a reading proven in the run renders nothing at the mount either
    (mnt_home.meta / "NODE2.md").write_text(
        "---\nname: NODE2\nserve: |\n  GROUND.md\n---\n\nsecond node\n", encoding="utf-8")
    silent_out = mnt_c().mount([{"doc": "NODE2.md"}])
    if ("the encyclopedic ground" not in silent_out and "served earlier" not in silent_out
            and "GROUND" not in silent_out):
        held("a proven reading is silent at the mount", "GROUND rode at the first mount; the "
             "second renders nothing for it -- no line, no text: the one reader's rule")
    else:
        failures.append(f"  ✗ mount silence               {silent_out[:160]!r}")

    # the shared-records lock case migrated RED to steering with pp-steering (KPS21,
    # batch la-purete-du-kit); the lock itself left at the rework: steering carries its own.

    # --- le-mount-atomique: a refusing row leaves the mount exactly where it stood -----
    # the row carries a MALFORMED range on a document that exists: the refusal fires
    # inside the rendering half (the readings serve before the state is written), which
    # is precisely where the state used to be already written.
    (mnt_home.meta / "RANGED.md").write_text(
        "---\nname: RANGED\nkind: doc\n---\n\nnow it reads\n", encoding="utf-8")
    (mnt_home.meta / "ATOMIC.md").write_text(
        "---\nname: ATOMIC\nkind: doc\nserve: |\n  reference: RANGED.md[3-1]\n---\n"
        "\nthe node whose row cannot be read\n", encoding="utf-8")
    before_peek = steady(render(mnt_c().peek()))
    before_state = persistence.mounted_of(session_of(mnt_home.meta))
    refused = None
    try:
        mnt_c().mount([{"doc": "ATOMIC.md"}])
    except Refusal as wrong:
        refused = wrong
    after_peek = steady(render(mnt_c().peek()))
    after_state = persistence.mounted_of(session_of(mnt_home.meta))
    bench.refusals += 1
    if (refused is not None and before_peek == after_peek and before_state == after_state
            and "ATOMIC" in str(refused)):
        held("a refusing row mounts nothing",
             f"`{refused.code}` names its row; the two -peek are identical byte for byte "
             f"and the state still carries {len(after_state)} mount(s)")
    else:
        failures.append(f"  ✗ mount not atomic            refused={refused!r} "
                        f"peek={before_peek == after_peek} state={before_state == after_state}")

    # --- le-mount-atomique: repaired, the SAME gesture plays whole ---------------------
    (mnt_home.meta / "ATOMIC.md").write_text(
        "---\nname: ATOMIC\nkind: doc\nserve: |\n  reference: RANGED.md\n---\n"
        "\nthe node whose row cannot be read\n", encoding="utf-8")
    replayed = mnt_c().mount([{"doc": "ATOMIC.md"}])
    now_state = persistence.mounted_of(session_of(mnt_home.meta))
    if len(now_state) == len(after_state) + 1 and "RANGED.md" in replayed:
        held("the repaired mount replays whole",
             "the same gesture, unchanged, mounts the node and serves its row")
    else:
        failures.append(f"  ✗ replay lost                 {len(after_state)} -> {len(now_state)} "
                        f"mount(s), row served={'RANGED.md' in replayed}")

    # --- le-mount-refuse-au-banc: a CHAIN with a refusing row mounts nothing at all -------
    # the lived defect (core, engine alpha.91, 2026-08-26): the plan's PLAN and PHASE stayed
    # in force after the batch's row refused, and every later mount collided -- three
    # documents in ONE call here, the last one refusing
    (mnt_home.meta / "CHAIN1.md").write_text(
        "---\nname: CHAIN1\nconstraints.behavior: |\n  C1  the first law.\n---\n\nfirst\n", encoding="utf-8")
    (mnt_home.meta / "CHAIN2.md").write_text(
        "---\nname: CHAIN2\nconstraints.behavior: |\n  C2  the second law.\n---\n\nsecond\n", encoding="utf-8")
    (mnt_home.meta / "CHAIN3.md").write_text(
        "---\nname: CHAIN3\nkind: doc\nserve: |\n  reference: RANGED.md[3-1]\n---\n\nthird\n",
        encoding="utf-8")
    chain_before = persistence.mounted_of(session_of(mnt_home.meta))
    chain_refused = None
    try:
        mnt_c().mount([{"doc": "CHAIN1.md"}, {"doc": "CHAIN2.md"}, {"doc": "CHAIN3.md"}])
    except Refusal as wrong:
        chain_refused = wrong
    chain_after = persistence.mounted_of(session_of(mnt_home.meta))
    bench.refusals += 1
    try:
        chain_again = mnt_c().mount([{"doc": "CHAIN1.md"}, {"doc": "CHAIN2.md"}])
    except Refusal as wrong:
        chain_again = wrong
    chain_now = persistence.mounted_of(session_of(mnt_home.meta))
    if (chain_refused is not None and chain_after == chain_before
            and isinstance(chain_again, str) and len(chain_now) == len(chain_before) + 2):
        held("a refusing chain mounts nothing",
             f"`{chain_refused.code}` on the third document keeps the two before it out; "
             "the same two mount afterwards, no collision")
    else:
        failures.append(f"  ✗ chain not atomic            refused={chain_refused!r} "
                        f"after={len(chain_after)}/{len(chain_before)} again={chain_again!r}")

    # the two bords of the rule: a kind the engine PLAYS carries a flow and says nothing,
    # any other kind with a `proc:` is an authoring slip the build names
    (mnt_home.meta / "plans").mkdir(exist_ok=True)
    (mnt_home.meta / "plans" / "BAD.md").write_text(
        "---\nname: BAD\nproc: |\n  WORK\n---\nsome body\n", encoding="utf-8")
    (mnt_home.meta / "FLOWING.md").write_text(
        "---\nname: FLOWING\nkind: boot\nproc: |\n  HOOK boot.ready\n---\na boot's flow\n",
        encoding="utf-8")
    said = [one for one in compiling.lint(mnt_home.meta) if "carries a `proc:`" in one]
    if (any("plans/BAD.md" in one for one in said)
            and not any("FLOWING" in one for one in said)):
        held("the lint names a slip, not a flow",
             "a `plans/` document with a `proc:` and no kind is named; a `kind: boot` "
             "carrying `HOOK boot.ready` -- what the engine plays at every boot -- is not")
    else:
        failures.append(f"  ✗ plans lint                  {said!r}")

    # --- le-mount-qui-recharge: a mount re-shows the standing step, the pointer stands ---
    # the lived defect (campagne plan D2, 2026-09-04): at the TURN the output closes at
    # the `§` after WORK; the mount used to ADVANCE like a bare call -- crossing the
    # break, rendering the hook and the checkpoint before any work. Now it re-shows the
    # asked step in the richer context: the pointer is where it was, the `@n` addresses
    # route, and the next bare call is the one that crosses.
    rch_made = bench.env("rechw").made
    rch_member = discovery.instance_member(rch_made / ".sys" / "engine" / "pp.py")
    (rch_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n", encoding="utf-8")
    (rch_made / "RICH.md").write_text(
        "---\nname: RICH\nkind: doc\nconstraints.production: |\n  R1  the richer law binds.\n"
        "tools: |\n  RICHTOOL\n---\n\nThe richer context.\n", encoding="utf-8")

    def rch_c() -> Conductor:
        return Conductor(rch_member, discovery.siblings_around(rch_member),
                         rch_made / ".sys" / "engine" / "pp.py", "t")

    rch_c().start(rch_c().boot("BOOT.md"))              # the boot flows into the TURN: the
    # first output closes at the `§` after WORK -- the agent is at its work
    rch_slot = session_of(rch_member.meta)
    rch_before = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_before = navigation.current(rch_before)
    rch_pos_before = (rch_frame_before.document.name, navigation.position(rch_frame_before))
    rch_out = rch_c().mount([{"doc": "RICH.md", "scope": "nested", "body": True}])
    rch_after = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_after = navigation.current(rch_after)
    rch_pos_after = (rch_frame_after.document.name, navigation.position(rch_frame_after))
    rch_shown = rch_c().peek()
    rch_routed = rch_c().route("RICHTOOL", 1)         # offered by [1] RICH and [2] TURN: addressed
    rch_next = rch_c().forward("")                       # the bare call crosses the `§`
    if (rch_pos_before == rch_pos_after and rch_pos_before[0] == "TURN"
            and "▸ RICH" in rch_out and "The richer context." in rch_out
            and "WORK" in rch_out and "proof" not in rch_out
            and rch_shown is not None and rch_shown.command == "WORK"
            and rch_routed is not None
            and rch_next is not None and rch_next.instruction.keyword in ("PROVE", "FINAL")):
        held("a mount re-shows the standing step",
             "the pointer stands at the `§`, WORK re-shown with the mounted scope, the "
             "address routes -- the bare call after it crosses to the checkpoint")
    else:
        failures.append(f"  ✗ mount recharge              before={rch_pos_before} after={rch_pos_after} "
                        f"shown={rch_shown and rch_shown.command!r} routed={rch_routed is not None} "
                        f"next={rch_next and rch_next.instruction.keyword!r} "
                        f"out={rch_out[:200]!r}")

    return 0
