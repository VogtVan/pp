"""Scenario `mount` -- the MOUNT verb: hosted documents ride the exchange:
- the verb: a mount rides the view, its law is judged at the proof, it lives one exchange, a
  nested mount stacks its own addressable segment; the mount plays the serves softly, a stale
  serve latches, a proven reading is silent; a refusing row or chain mounts nothing, the
  repaired gesture replays whole
- a mount re-shows the standing step: the pointer stands
- overlays: a mounted document carries the deltas of its overlays, a homonym outside the
  name's chain takes none, the collision looks at the effective laws
- selections: a mount entry's `body` as a LIST of selections, stacked or nested, each part a
  reading of the one reader, kept at the slot, said when absent, refused when badly written
- the `::mount` directive: a script's chain mounts in the same gesture
- the lint names a `proc:` outside a played kind, never a flow
"""
from __future__ import annotations

import contextlib
import io
import json

from conductor import Conductor, Refusal, compiling, navigation, persistence, reading, render, revive
from tests.harness import steady

FORMS = ("---\nname: MFORMS\ndescription: mount bench formats\nformats: |\n"
         "  json  inline  one valid JSON value\n---\n")
CYCLE = "---\nname: MJOB\ncycle: true\noutput: json\nproc: |\n  INFER\n  PICK member\n---\n"

BASE = ("---\nname: WNODE\nkind: doc\nconstraints.production: |\n  W1  the base law binds.\n"
        "  W2  the base law an overlay lifts.\ntools: |\n  WBASE\n---\n\nThe witness node.\n")
OVERLAY = ("---\nname: WNODE\nconstraints.production: |\n  -W2\n  W3  the overlay law binds.\n"
           "tools: |\n  +WOVER\n---\n")
HOMONYM = ("---\nname: WNODE\nkind: doc\nconstraints.production: |\n  H1  the homonym's own law.\n"
           "---\n\nA node that only shares the file name.\n")

NODE = """---
name: NODE
kind: doc
---

# NODE

## Alpha
a1 -- the ground nobody asked for
a2
## Beta
b1
b2
## Gamma
g1
## Delta
d1
"""
PARTS = ["## Beta..## Gamma", "## Delta.."]
FLOOR = "---\nname: FLOOR\nkind: proc\ndescription: a floor\ncycle: true\nproc: |\n  INFER\n---\n\nthe floor\n"


def house(bench):
    """-> the bare environment the verb, the overlays, the directive and the lint share: the
    formats and the cycling floor written; each subject plays on its own run."""
    env = bench.env("mount", bare=True)
    env.write("MFORMS.md", FORMS)
    env.write("MJOB.md", CYCLE)
    return env


def verb(bench, env) -> None:
    """The MOUNT verb on run `t`: the view, the proof, the sweep, the nested scope, the serves,
    the atomicity of a refusing row or chain."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    meta = env.made
    slot = persistence.slot_of(meta, "t")

    def mnt_c() -> Conductor:
        return env.conductor("t")

    env.write("EXT.md", "---\nname: EXT\nconstraints.production: |\n  X1  the hosted law binds.\n"
                        "tools: |\n  TAGGED\n---\n\nThe hosted body.\n")
    env.write("EXT2.md", "---\nname: EXT2\nconstraints.production: |\n"
                         "  X2  the second hosted law binds.\n---\n\nquiet matter\n")
    mnt_c().start(meta / "MJOB.md")
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
    mnt_stack = mnt_ctl._rebind(persistence.restore(slot, revive))
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
    if "X1" not in mnt_left and "X2" not in mnt_left and persistence.mounted_of(slot) == []:
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

    # --- the mount plays the serves; a gone document or a clipped range degrades softly ----
    env.write("GROUND.md", "---\nname: GROUND\ndescription: the framing's reading\n---\n"
                           "the encyclopedic ground\n")
    env.write("NODE.md", "---\nname: NODE\nconstraints.behavior: |\n  N1  the node's law.\nserve: |\n"
                         "  GROUND.md GHOSTED.md\n  MFORMS.md[2-99]\n---\n\nnode prose\n")
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

    # --- the gone document pushes a BARE serve-stale: the run holds the latch ------------
    stale_latched = [one for one in persistence.signals_of(slot) if one.get("signal") == "serve-stale"]
    if stale_latched and stale_latched[0].get("n", 0) >= 1:
        held("a stale serve latches for real",
             f"serve-stale rides the slot (n={stale_latched[0]['n']}) -- the improve "
             "will say it; the reading's note already oriented the agent")
    else:
        failures.append(f"  ✗ serve-stale never lands     latches: {stale_latched!r}")

    # --- a reading proven in the run renders nothing at a later mount ---------------------
    env.write("NODE2.md", "---\nname: NODE2\nserve: |\n  GROUND.md\n---\n\nsecond node\n")
    silent_out = mnt_c().mount([{"doc": "NODE2.md"}])
    if ("the encyclopedic ground" not in silent_out and "served earlier" not in silent_out
            and "GROUND" not in silent_out):
        held("a proven reading is silent at the mount", "GROUND rode at the first mount; the "
             "second renders nothing for it -- no line, no text: the one reader's rule")
    else:
        failures.append(f"  ✗ mount silence               {silent_out[:160]!r}")

    # --- a refusing row leaves the mount where it stood: a MALFORMED range on a document
    # that exists refuses inside the rendering half, before the state is written
    env.write("RANGED.md", "---\nname: RANGED\nkind: doc\n---\n\nnow it reads\n")
    env.write("ATOMIC.md", "---\nname: ATOMIC\nkind: doc\nserve: |\n  reference: RANGED.md[3-1]\n---\n"
                           "\nthe node whose row cannot be read\n")
    before_peek = steady(render(mnt_c().peek()))
    before_state = persistence.mounted_of(slot)
    refused = None
    try:
        mnt_c().mount([{"doc": "ATOMIC.md"}])
    except Refusal as wrong:
        refused = wrong
    after_peek = steady(render(mnt_c().peek()))
    after_state = persistence.mounted_of(slot)
    bench.refusals += 1
    if (refused is not None and before_peek == after_peek and before_state == after_state
            and "ATOMIC" in str(refused)):
        held("a refusing row mounts nothing",
             f"`{refused.code}` names its row; the two -peek are identical byte for byte "
             f"and the state still carries {len(after_state)} mount(s)")
    else:
        failures.append(f"  ✗ mount not atomic            refused={refused!r} "
                        f"peek={before_peek == after_peek} state={before_state == after_state}")

    # --- repaired, the SAME gesture plays whole -------------------------------------------
    env.write("ATOMIC.md", "---\nname: ATOMIC\nkind: doc\nserve: |\n  reference: RANGED.md\n---\n"
                           "\nthe node whose row cannot be read\n")
    replayed = mnt_c().mount([{"doc": "ATOMIC.md"}])
    now_state = persistence.mounted_of(slot)
    if len(now_state) == len(after_state) + 1 and "RANGED.md" in replayed:
        held("the repaired mount replays whole",
             "the same gesture, unchanged, mounts the node and serves its row")
    else:
        failures.append(f"  ✗ replay lost                 {len(after_state)} -> {len(now_state)} "
                        f"mount(s), row served={'RANGED.md' in replayed}")

    # --- a CHAIN of three documents in one call, the last refusing: none of them mounts ----
    env.write("CHAIN1.md", "---\nname: CHAIN1\nconstraints.behavior: |\n  C1  the first law.\n---\n\nfirst\n")
    env.write("CHAIN2.md", "---\nname: CHAIN2\nconstraints.behavior: |\n  C2  the second law.\n---\n\nsecond\n")
    env.write("CHAIN3.md", "---\nname: CHAIN3\nkind: doc\nserve: |\n  reference: RANGED.md[3-1]\n---\n\nthird\n")
    chain_before = persistence.mounted_of(slot)
    chain_refused = None
    try:
        mnt_c().mount([{"doc": "CHAIN1.md"}, {"doc": "CHAIN2.md"}, {"doc": "CHAIN3.md"}])
    except Refusal as wrong:
        chain_refused = wrong
    chain_after = persistence.mounted_of(slot)
    bench.refusals += 1
    try:
        chain_again = mnt_c().mount([{"doc": "CHAIN1.md"}, {"doc": "CHAIN2.md"}])
    except Refusal as wrong:
        chain_again = wrong
    chain_now = persistence.mounted_of(slot)
    if (chain_refused is not None and chain_after == chain_before
            and isinstance(chain_again, str) and len(chain_now) == len(chain_before) + 2):
        held("a refusing chain mounts nothing",
             f"`{chain_refused.code}` on the third document keeps the two before it out; "
             "the same two mount afterwards, no collision")
    else:
        failures.append(f"  ✗ chain not atomic            refused={chain_refused!r} "
                        f"after={len(chain_after)}/{len(chain_before)} again={chain_again!r}")


def recharge(bench) -> None:
    """A mount re-shows the standing step: at the TURN the output closes at the `§` after
    WORK; the mount re-shows the asked step in the richer context, the pointer where it was,
    the `@n` addresses routing, and the next bare call is the one that crosses."""
    held, failures = bench.held, bench.failures
    env = bench.env("rechw")
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n")
    env.write("RICH.md", "---\nname: RICH\nkind: doc\nconstraints.production: |\n  R1  the richer law binds.\n"
                         "tools: |\n  RICHTOOL\n---\n\nThe richer context.\n")

    def rch_c() -> Conductor:
        return env.conductor("t")

    rch_c().start(rch_c().boot("BOOT.md"))     # the boot flows into the TURN, closed at the `§`
    rch_slot = persistence.slot_of(env.made, "t")
    rch_before = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_before = navigation.current(rch_before)
    rch_pos_before = (rch_frame_before.document.name, navigation.position(rch_frame_before))
    rch_out = rch_c().mount([{"doc": "RICH.md", "scope": "nested", "body": True}])
    rch_after = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_after = navigation.current(rch_after)
    rch_pos_after = (rch_frame_after.document.name, navigation.position(rch_frame_after))
    rch_shown = rch_c().peek()
    rch_routed = rch_c().route("RICHTOOL", 1)   # offered by [1] RICH and [2] TURN: addressed
    rch_next = rch_c().forward("")              # the bare call crosses the `§`
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


def overlays(bench, env) -> None:
    """A MOUNTED document puts in force what a frame on it would, on run `o`: the base's
    sections and the deltas of its overlays; a homonym outside the chain takes none."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    meta = env.made

    def c() -> Conductor:
        return env.conductor("o")

    env.write("procs/WNODE.md", BASE)               # the base of the name
    env.write("WNODE.md", OVERLAY)                  # its overlay, nearer
    env.write("elsewhere/WNODE.md", HOMONYM)        # outside the chain

    def sweep() -> None:
        """One exchange played out: the cycling floor exhausts and its rewind sweeps the mounts."""
        c().submit('["a", "b"]')
        c().submit("a")

    # --- a stacked mount carries its overlay's deltas ----------------------------------------
    c().start(meta / "MJOB.md")
    c().mount([{"doc": "procs/WNODE.md"}])
    block = c().peek()
    codes = [one.code for one in block.constraints]
    tools = [one.name for one in block.tools]
    if "W1" in codes and "W3" in codes and "W2" not in codes and {"WBASE", "WOVER"} <= set(tools):
        held("a stacked mount carries its overlay's deltas",
             "the base's law, the overlay's added law and offer in force; the lifted law gone")
    else:
        failures.append(f"  ✗ stacked deltas             codes={codes} tools={tools}")

    # --- the overlay's law is owed at the proof ------------------------------------------------
    judge = c()
    stack = judge._rebind(persistence.restore(persistence.slot_of(meta, "o"), revive))
    frame = navigation.current(stack)
    fine = judge._check_prove(stack, frame, navigation.peek(frame),
                              '[{"code": "W1", "evidence": "held", "verdict": "ok"}, '
                              '{"code": "W3", "evidence": "held", "verdict": "ok"}]')
    lifted = judge._check_prove(stack, frame, navigation.peek(frame),
                                '[{"code": "W2", "evidence": "held", "verdict": "ok"}]')
    if fine == "" and "W2" in lifted and "not in force" in lifted:
        held("the overlay's law is judged at the proof",
             "W1 and W3 pass as laws in force; W2, lifted by the overlay, is refused as a stranger")
    else:
        failures.append(f"  ✗ overlay proof              fine={fine!r} lifted={lifted!r}")

    # --- the collision looks at the effective laws ---------------------------------------------
    env.write("procs/WOTHER.md", "---\nname: WOTHER\nkind: doc\n---\n\nquiet\n")
    env.write("WOTHER.md", "---\nname: WOTHER\nconstraints.production: |\n  W3  the same code again.\n---\n")
    expect("mount-collision", lambda: c().mount([{"doc": "procs/WOTHER.md"}]))

    # --- a nested mount shows the same in its own segment ------------------------------------
    sweep()
    out = c().mount([{"doc": "procs/WNODE.md", "scope": "nested"}])
    segment = out.split("▌ [2]")[0]
    if ("▸ WNODE" in segment and "WBASE WOVER" in segment and "W3  the overlay law binds." in segment
            and "W1  the base law binds." in segment and "W2  the base law" not in segment):
        held("a nested mount shows its overlay's deltas",
             "its own heading, the two offers, the base's and the overlay's laws verbatim, the lifted one absent")
    else:
        failures.append(f"  ✗ nested deltas              {segment[:300]!r}")

    # --- the BASE guard: a homonym outside the chain takes no delta -----------------------------
    sweep()
    c().mount([{"doc": "elsewhere/WNODE.md"}])
    block = c().peek()
    codes = [one.code for one in block.constraints]
    tools = [one.name for one in block.tools]
    if "H1" in codes and "W3" not in codes and "WOVER" not in tools:
        held("a homonym outside the chain takes no delta",
             "mounted by its path, it is not the base of its name: its own law alone, no overlay's law or offer")
    else:
        failures.append(f"  ✗ base guard                 codes={codes} tools={tools}")


def _lines(made, kind: str) -> list[dict]:
    """-> every trace line of `kind`, across the instance's trace files."""
    return [one for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
            if one.get("kind") == kind]


def _ledger(made) -> list[dict]:
    """-> every reading the blocks' ledgers name."""
    return [line for block in _lines(made, "block") for line in (block.get("served") or [])]


def selection(bench) -> None:
    """A mount entry's `body` as a LIST of selections, on a body served once: each part served
    alone under `<document>[<selection>]`, stacked or nested, a reading of the one reader."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("msel")
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    env.write("NODE.md", NODE)
    env.write("FLOOR.md", FLOOR)
    titles = [f"NODE[{part}]" for part in PARTS]

    def opened(key: str):
        runner = env.conductor(key)
        runner.forget()
        runner.start(env.made / "FLOOR.md")
        return lambda: env.conductor(key)

    # --- stacked: the asked parts alone, each under its own title ---------------------------
    stacked = opened("s")
    said = stacked().mount([{"doc": "NODE.md", "body": PARTS}])
    if (all(f"INFORMATION — {title}\n" in said for title in titles)
            and "## Beta\nb1\nb2" in said and "## Delta\nd1" in said
            and "a1 -- the ground" not in said and "g1" not in said):
        held("a stacked entry serves its parts", "two readings under `NODE[<selection>]`, the "
             "rest of the body left out")
    else:
        failures.append(f"  ✗ the stacked parts           {said[-500:]!r}")

    # --- a second mount of the same parts is spared; a part's hash is its own ----------------
    again = env.conductor("s").mount([{"doc": "NODE.md", "body": PARTS, "constraints": False}])
    states = [(line["subject"], line["state"], line.get("origin")) for line in _ledger(env.made)
              if line["subject"].startswith("NODE[")]
    path = env.made / "NODE.md"
    hashes = {reading.served(path)[1], *(reading.spanned(path, reading.ranged(f"x[{part}]")[1].span)[1]
                                         for part in PARTS)}
    if (states.count((titles[0], "served", "mount")) == 1
            and states.count((titles[0], "spared", "mount")) == 1
            and "b1" not in again and len(hashes) == 3):
        held("a part is proven and spared", "served once, `spared` at the second mount, origin "
             "`mount`; the hash of a part is not the body's")
    else:
        failures.append(f"  ✗ the spared parts            {states} {len(hashes)} hashes")

    # --- the selection stands at the slot and comes back after a compaction -----------------
    kept = persistence.mounted_of(env.session())
    back = {subject for subject, _ in env.conductor("s").compacted().payloads}
    reserved = [line["subject"] for line in _ledger(env.made) if line.get("state") == "reserved"]
    if kept and kept[0]["body"] == PARTS and set(titles) <= back and set(titles) <= set(reserved):
        held("the selection comes back", "the list stands at the slot; after `-compacted` the "
             "same parts are served again, `reserved`")
    else:
        failures.append(f"  ✗ the re-serve                {kept!r} {sorted(back)} {reserved}")

    # --- nested: the same parts under the segment's heading ---------------------------------
    nested = opened("n")
    said = nested().mount([{"doc": "NODE.md", "scope": "nested", "body": PARTS}])
    returned = {subject for subject, _ in env.conductor("n").compacted().payloads}
    if ("▸ NODE" in said and all(f"INFORMATION — {title}\n" in said for title in titles)
            and "## Beta\nb1\nb2" in said and "a1 -- the ground" not in said
            and set(titles) <= returned):
        held("a nested entry serves its parts", "the same two readings under the segment's "
             "heading, and back after `-compacted`")
    else:
        failures.append(f"  ✗ the nested parts            {said[-500:]!r}")

    # --- a start tag found on no line -------------------------------------------------------
    absent = opened("a")
    before = len([one for one in _lines(env.made, "signal") if one.get("signal") == "serve-stale"])
    said = absent().mount([{"doc": "NODE.md", "body": ["## Nowhere..## Gamma", "## Delta.."]}])
    stale = len([one for one in _lines(env.made, "signal") if one.get("signal") == "serve-stale"])
    missing = [line["subject"] for line in _ledger(env.made) if line.get("state") == "missing"]
    if "NODE[## Nowhere..## Gamma]" in missing and stale == before + 1 and "## Delta\nd1" in said:
        held("an absent tag is said", "`missing` for that part, `serve-stale` pushed, the other "
             "part served")
    else:
        failures.append(f"  ✗ the absent tag              {missing} {stale - before} signal(s)")

    # --- a badly written selection refuses, nothing written ----------------------------------
    torn = opened("t")
    slot = persistence.slot_of(env.made, "t")
    bytes_before = slot.read_bytes()
    for body in ([".."], ["a..b..c"], [], [3]):
        expect("mount-invalid", lambda body=body: torn().mount([{"doc": "NODE.md", "body": body}]))
    if slot.read_bytes() == bytes_before:
        held("a refusal writes nothing", "four badly written selections, the slot's bytes untouched")
    else:
        failures.append("  ✗ the slot moved under a refused mount")

    # --- the weight of the block: the whole body against the selection ----------------------
    whole = opened("w")
    whole().mount([{"doc": "NODE.md", "body": True}])
    served = [line for line in _ledger(env.made)
              if line.get("origin") == "mount" and line.get("state") == "served"]
    heavy = max((line.get("chars", 0) for line in served if line["subject"] == "NODE"), default=0)
    thin = max((line.get("chars", 0) for line in served if line["subject"] == titles[0]), default=0)
    if 0 < thin < heavy:
        held("the trace tells the effect", f"{heavy} c mounted whole, {thin} c for one selection")
    else:
        failures.append(f"  ✗ the weight                  whole={heavy} selection={thin}")


def directive(bench, env) -> None:
    """The `::mount` directive on run `d`: a script's chain mounts in the same gesture."""
    import pp as pp_cli
    held, failures = bench.held, bench.failures
    meta = env.made

    env.write("EXT3.md", "---\nname: EXT3\nconstraints.behavior: |\n  Y1  the harvested law binds.\n---\n\n"
                         "harvested matter\n")
    env.conductor("d").start(meta / "MJOB.md")
    probe = env.write("probe-mount.py",
                      'def main(argv):\n'
                      '    print(\'::mount [{"doc": "EXT3.md", "scope": "nested"}]\')\n'
                      '    print("probe: chain derived")\n'
                      '    return 0\n')
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        rc = pp_cli._played(env.conductor("d"), probe, [], "probe-mount")
    said = buffer.getvalue()
    standing = persistence.mounted_of(persistence.slot_of(meta, "d"))
    if (rc == 0 and "::mount" not in said
            and "probe: chain derived" in said and "▸ EXT3" in said
            and "Y1  the harvested law binds." in said
            and [one["doc"] for one in standing] == ["EXT3.md"]):
        held("the ::mount directive is harvested", "the script derives, pp hosts in the same "
             "gesture -- the directive never reaches the terminal, the mounted scope renders")
    else:
        failures.append(f"  ✗ mount harvest               rc={rc} {said[:140]!r}")


def plans_lint(bench, env) -> None:
    """The two edges of the `proc:` rule: a kind the engine PLAYS carries a flow and says
    nothing, any other kind with a `proc:` is an authoring slip the lint names."""
    held, failures = bench.held, bench.failures
    env.write("plans/BAD.md", "---\nname: BAD\nproc: |\n  WORK\n---\nsome body\n")
    env.write("FLOWING.md", "---\nname: FLOWING\nkind: boot\nproc: |\n  HOOK boot.ready\n---\na boot's flow\n")
    said = [one for one in compiling.lint(env.made) if "carries a `proc:`" in one]
    if (any("plans/BAD.md" in one for one in said)
            and not any("FLOWING" in one for one in said)):
        held("the lint names a slip, not a flow",
             "a `plans/` document with a `proc:` and no kind is named; a `kind: boot` "
             "carrying `HOOK boot.ready` -- what the engine plays at every boot -- is not")
    else:
        failures.append(f"  ✗ plans lint                  {said!r}")


def scenario(bench) -> int:
    env = house(bench)
    verb(bench, env)
    recharge(bench)
    overlays(bench, env)
    selection(bench)
    directive(bench, env)
    plans_lint(bench, env)
    return 0
