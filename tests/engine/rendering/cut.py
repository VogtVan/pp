"""Scenario `cut` -- 8 case(s):
- la-coupe-tient-le-cap: a block over the cap comes back in chunks, none over it
- la-matiere-est-entiere: the chunks carry the block's matter, byte for byte
- l-entete-ride-chaque-morceau: every chunk opens on the output's heading, run, hour and the packages' state
- la-tranche-qui-se-dit: an intermediate chunk says it is one and carries no instruction; the last carries the tail
- le-prouve-a-la-livraison: a document is proven when its last chunk has left, every chunk traced
- l-invariant-du-cap: whatever the matter, no output goes over the cap -- three regimes
- le-mount-sous-le-cap: a MOUNT's text is cut like any output, the rest on the bare calls
- la-vue-sous-le-cap: a VIEW (peek, keyless, denied) is clipped under the cap, nothing kept
"""
from __future__ import annotations

from conductor import Conductor, discovery, rendering

CAP = 2000


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("cut").made
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
    conductor = Conductor(member, discovery.siblings_around(member),
                          made / ".sys" / "engine" / "pp.py")
    block = conductor.resume(conductor.boot("BOOT.md"))
    whole, tail = rendering.parts(block)

    chunks = [conductor.rendered(block)]
    while conductor.pending() and len(chunks) < 200:
        chunks.append(conductor.next_chunk())

    over = [len(one) for one in chunks if len(one) > CAP]
    if len(chunks) > 1 and not over:
        held("the cut holds the cap",
             f"{len(chunks)} chunks, none over {CAP} -- the block was {len(whole) + len(tail)} characters")
    else:
        failures.append(f"  ✗ cut over the cap            {len(chunks)} chunk(s), over: {over}")

    # the head comes with the tail: a chunk arriving alone still says which run it is from
    head = rendering.head(block)
    strayed = [one[:40] for one in chunks if not one.startswith(head)]
    if head and not strayed:
        held("the head comes with every chunk", f"`{head}` opens each of the {len(chunks)} chunks -- "
             "no piece arrives without saying which run it comes from")
    else:
        failures.append(f"  ✗ head off a chunk            {head!r} {strayed[:1]}")

    # the packages' state belongs to that heading: it rides every chunk by the same seam,
    # never by a second mechanism -- the pairs are posed here, the instance pinning none
    from dataclasses import replace
    from conductor.core.model import Block
    switched = replace(block, switches=(("alpha", ""), ("beta", "alpha")))
    state = f"{Block.MARK} alpha on · beta off (<- alpha)"
    switched_head = rendering.head(switched)
    matter, rode = rendering.parts(switched)[0], []
    while matter:
        piece, matter = rendering.cut(matter, CAP - len(tail))
        rode.append(rendering.under(switched_head, piece))
    if state in switched_head and len(rode) > 1 and all(state in one for one in rode):
        held("the packages' state rides every chunk", f"the state line opens each of the "
             f"{len(rode)} chunks with the heading -- it IS the heading's second line, so the "
             "cut carries it without knowing it exists")
    else:
        failures.append(f"  ✗ state off a chunk           {switched_head!r} {len(rode)} chunk(s)")

    # the matter of a chunk is the chunk minus the tail that rides it: the last one carries
    # the block's own closing, the others the bare call back
    seen, rest = [], whole
    while rest:
        piece, rest = rendering.cut(rest, CAP - len(tail))
        seen.append(piece)
    if "".join(seen) == whole:
        held("the matter comes back whole", "the chunks' matter concatenates to the block's, byte for byte")
    else:
        failures.append("  ✗ matter lost                 the concatenation is not the block's matter")

    # --- l-invariant-du-cap: the PERMANENT guard, on matter the scenario poses itself ----
    # the composition is `kit` alone and both the matter and the CAP are written here: the
    # invariant answers for the MECHANISM, never for what a real composition weighs (KPS17).
    # Three regimes, the cap moving around the block: it fits, it just overflows, it dwarfs.
    (made / "MATTER.md").write_text("m" * 1000 + "\n", encoding="utf-8")
    (made / "MATTERRUN.md").write_text(
        "---\nname: MATTERRUN\nproc: |\n  SERVE MATTER.md\n  INFER\n---\n", encoding="utf-8")
    regimes, broken = [], False
    for label, cap in (("it fits", 40000), ("it just overflows", 20000), ("it dwarfs", 2000)):
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: {cap}\n---\n", encoding="utf-8")
        run = Conductor(member, discovery.siblings_around(member),
                        made / ".sys" / "engine" / "pp.py")
        run.forget()
        posed = run.start(made / "MATTERRUN.md")
        posed_matter, posed_tail = rendering.parts(posed)
        pieces = [run.rendered(posed)]
        while run.pending() and len(pieces) < 400:
            pieces.append(run.next_chunk())
        biggest = max(len(one) for one in pieces)
        regimes.append(f"cap {cap}: block {len(posed_matter) + len(posed_tail)} -> "
                       f"{len(pieces)} chunk(s), biggest {biggest}")
        rebuilt, rest = [], posed_matter
        while rest:
            piece, rest = rendering.cut(rest, cap - len(posed_tail))
            rebuilt.append(piece)
        if biggest > cap or "".join(rebuilt) != posed_matter or (cap == 40000 and len(pieces) != 1):
            failures.append(f"  ✗ cap invariant ({label})    {regimes[-1]}")
            broken = True
            break
        run.forget()
    if not broken:
        held("no output goes over the cap", " | ".join(regimes))

    # --- la-tranche-qui-se-dit (rework of 2026-09-09): an intermediate chunk carries no
    # instruction and closes on the reading itself; the block's own tail rides the LAST
    middles, last = chunks[:-1], chunks[-1]
    said = [one for one in middles if "a reading continues" in one and "the bare call alone" in one
            and "▶ CONTINUE" in one and "▌ INSTRUCTION" not in one]
    if len(said) == len(middles) and last.endswith(tail.rstrip("\n").splitlines()[-1]) \
            and ("▌ INSTRUCTION" in last or "▌ END" in last or not block.command):
        held("a chunk says it is a chunk",
             f"each of the {len(middles)} intermediate chunks closes on `CONTINUE ./pp <key>` naming what "
             "remains and the bare call that alone serves it, and carries no instruction; the last "
             "chunk alone carries the block's own tail -- nothing invites a production before the reading is whole")
    else:
        failures.append(f"  ✗ chunk without its word      {len(said)}/{len(middles)} intermediate chunks said the reading; last={last[-160:]!r}")

    # --- le-prouve-a-la-livraison: a document is proven when its last chunk has left ------
    proved = Conductor(member, discovery.siblings_around(member), made / ".sys" / "engine" / "pp.py")
    proved.forget()
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    (made / "LONG.md").write_text("---\nname: LONG\nkind: doc\n---\n\n" + ("long line of matter\n" * 200) + "\n", encoding="utf-8")
    (made / "LONGRUN.md").write_text(
        "---\nname: LONGRUN\nproc: |\n  SERVE LONG.md\n  INFER\n---\n", encoding="utf-8")
    from conductor import persistence
    first = proved.rendered(proved.start(made / "LONGRUN.md"))
    slot = next(iter(sorted((made / ".sys" / "state").glob("session-*.json"))), None)
    import json as _json
    early = _json.loads(slot.read_text(encoding="utf-8")) if slot else {}
    staged_early, proven_early = len(early.get("pending", {}).get("staged", [])), len(early.get("proven", []))
    served_chunks = 1
    while proved.pending() and served_chunks < 400:
        proved.next_chunk()
        served_chunks += 1
    late = _json.loads(slot.read_text(encoding="utf-8")) if slot else {}
    proven_late = len(late.get("proven", []))
    kinds = [_json.loads(one).get("kind") for one in (made / ".sys" / "state" / early.get("log", "x")).read_text(encoding="utf-8").splitlines()] if slot and (made / ".sys" / "state" / early.get("log", "x")).exists() else []
    if (served_chunks > 1 and staged_early >= 1 and proven_early == 0 and proven_late >= 1
            and kinds.count("chunk") == served_chunks - 1 and kinds.count("cut") >= 1):
        held("a document is proven when its last chunk has left, and every chunk is traced",
             f"after the first chunk the reading stands STAGED ({staged_early}) and the run proves nothing; "
             f"once the {served_chunks} chunks are served the proof lands ({proven_late}); the trace says "
             f"`cut` then {kinds.count('chunk')} `chunk` -- whether the agent drained is read at the journal")
    else:
        failures.append(f"  ✗ proven at delivery          chunks={served_chunks} staged={staged_early} proven={proven_early}->{proven_late} kinds={ {k: kinds.count(k) for k in set(kinds)} }")
    proved.forget()
    # --- le-mount-sous-le-cap: a MOUNT's text goes through the ONE cut ---------------------
    # before the fix `mount()` returned a bare render: 41 610 characters in one output on a
    # real plan (core, 2026-08-26) -- the one text of the engine that could exceed the cap
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    (made / "BIG.md").write_text(
        "---\nname: BIG\nkind: doc\n---\n\n" + ("big matter line\n" * 300) + "\n",
        encoding="utf-8")
    host = Conductor(member, discovery.siblings_around(member),
                     made / ".sys" / "engine" / "pp.py")
    host.forget()
    booted = host.start(host.boot("BOOT.md"))   # the boot block, over the cap: the view's matter
    view = host.shown(booted)                  # a VIEW never taints the conductor (a peek would)
    view_kept = host.pending()
    mounted = [host.mount([{"doc": "BIG.md", "body": True}])]
    while host.pending() and len(mounted) < 400:
        mounted.append(host.next_chunk())
    mount_over = [len(one) for one in mounted if len(one) > CAP]
    if len(mounted) > 1 and not mount_over and "big matter line" in "".join(mounted):
        held("a mount is cut like any output",
             f"{len(mounted)} chunks, none over {CAP} -- the mounted body came through whole")
    else:
        failures.append(f"  ✗ mount over the cap          {len(mounted)} chunk(s), over: {mount_over}")

    # --- la-vue-sous-le-cap: a VIEW is clipped, and keeps nothing at the run ----------------
    if (booted is not None and len(rendering.render(booted)) > CAP and len(view) <= CAP
            and "cut under the host's cap" in view and not view_kept):
        held("a view is clipped under the cap",
             f"the view of a {len(rendering.render(booted))}-character block shows {len(view)}, "
             "says it is cut, and leaves no chunk waiting")
    else:
        failures.append(f"  ✗ view over the cap           {len(view)} kept={view_kept}")

    return 0
