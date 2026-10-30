"""Scenario `cut` -- 8 case(s):
- la-coupe-tient-le-cap: a block over the cap comes back in chunks, none over it
- la-matiere-est-entiere: the chunks carry the block's matter, byte for byte
- l-entete-ride-chaque-morceau: every chunk opens on the output's heading, run, hour and the packages' state
- la-tranche-qui-se-dit: an intermediate chunk says it is one and carries no instruction; the last carries the tail
- le-prouve-a-la-livraison: a document is proven when its last chunk has left, every chunk traced
- l-invariant-du-cap: whatever the matter, no output goes over the cap -- three regimes
- le-mount-sous-le-cap: a MOUNT's text is cut like any output, the rest on the bare calls
- la-vue-sous-le-cap: a VIEW (peek, keyless, denied) is clipped under the cap, nothing kept
- le-plafond-suit-l-appel-marque: `PP_PROMPT_CAP` on the principal's marked call is the cap of its
  outputs; without it the floor holds; a value that does not parse refuses `prompt-cap-invalid`; the
  variable is inert in the LLM's mode and on an unmarked call
- le-morceau-au-prompt-clot-more: a chunk before the last closes on `MORE` and the fact at the prompt,
  on `CONTINUE`, the bare call and the fact by the tool; the last chunk carries the block's own foot
"""
from __future__ import annotations

import os

from conductor import Conductor, discovery, rendering, settings
from conductor.core import language
from conductor.core.model import Block
from conductor.state import context

LONGRUN = "---\nname: LONGRUN\nkind: proc\ndescription: a witness\nproc: |\n  SERVE LONG.md\n  WORK\n---\nread\n"


def _under(value: str | None, call):
    """-> what `call` returns with the principal's mark set to `value` (None: absent) in THIS process."""
    spot = os.environ.get(context.CONDUCTED_BY)
    if value is None:
        os.environ.pop(context.CONDUCTED_BY, None)
    else:
        os.environ[context.CONDUCTED_BY] = value
    try:
        return call()
    finally:
        if spot is None:
            os.environ.pop(context.CONDUCTED_BY, None)
        else:
            os.environ[context.CONDUCTED_BY] = spot

CAP = 2000


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("cut").made
    (made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n", encoding="utf-8")
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
    conductor = Conductor(member, made / ".sys" / "engine" / "pp.py")
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
        run = Conductor(member, made / ".sys" / "engine" / "pp.py")
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
    said = [one for one in middles if "a reading continues" in one and one.rstrip().endswith("more chunk(s))")
            and "▶ CONTINUE" in one and "▌ INSTRUCTION" not in one.splitlines()]
    if len(said) == len(middles) and last.endswith(tail.rstrip("\n").splitlines()[-1]) \
            and ("▌ INSTRUCTION" in last or "▌ END" in last or not block.command):
        held("a chunk says it is a chunk",
             f"each of the {len(middles)} intermediate chunks closes on `CONTINUE ./pp <key>` and the count of "
             "what remains, nothing more, and carries no instruction; the last "
             "chunk alone carries the block's own tail -- nothing invites a production before the reading is whole")
    else:
        failures.append(f"  ✗ chunk without its word      {len(said)}/{len(middles)} intermediate chunks said the reading; last={last[-160:]!r}")

    # --- le-prouve-a-la-livraison: a document is proven when its last chunk has left ------
    proved = Conductor(member, made / ".sys" / "engine" / "pp.py")
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
    host = Conductor(member, made / ".sys" / "engine" / "pp.py")
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
            and view.rstrip().splitlines()[-1].startswith("   (") and not view_kept):
        held("a view is clipped under the cap",
             f"the view of a {len(rendering.render(booted))}-character block shows {len(view)}, "
             "says it is cut by one fact at its foot, and leaves no chunk waiting")
    else:
        failures.append(f"  ✗ view over the cap           {len(view)} kept={view_kept}")

    # --- le-plafond-suit-l-appel-marque: the cap of a principal's output is the launcher's --------
    # the one rule, `settings.served_cap`: the floor without the variable, the variable's value with
    # it, the LLM's setting untouched, 0 cutting nothing
    floor = settings.PRINCIPAL_CAP
    ruled = {(20000, True, None): floor, (20000, True, 2000000): 2000000, (20000, True, 50000): 50000,
             (300000, True, None): 300000, (20000, False, 2000000): 20000, (0, True, 2000000): 0}
    got = {triple: settings.served_cap(*triple) for triple in ruled}
    # the reader of the variable: on the marked call alone, a number or a refusal
    def capped(mark: str | None, value: str | None):
        spot = {name: os.environ.get(name) for name in (context.CONDUCTED_BY, context.PROMPT_CAP)}
        for name, given in ((context.CONDUCTED_BY, mark), (context.PROMPT_CAP, value)):
            if given is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = given
        try:
            return context.prompt_cap()
        except Exception as refused:          # noqa: BLE001 -- the refusal's code is what the case reads
            return getattr(refused, "code", type(refused).__name__)
        finally:
            for name, was in spot.items():
                if was is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = was
    read = {"marked": capped("true", "2000000"), "unmarked": capped(None, "2000000"),
            "absent": capped("true", None), "odd": capped("true", "plenty"), "zero": capped("true", "0")}
    if (got == ruled and read["marked"] == 2000000 and read["unmarked"] is None and read["absent"] is None
            and read["odd"] == "prompt-cap-invalid" and read["zero"] == "prompt-cap-invalid"):
        held("the cap follows the marked call", f"served_cap: {ruled}; PP_PROMPT_CAP read on the marked "
             "call alone (2000000), None unmarked or absent, `plenty` and `0` refuse prompt-cap-invalid")
    else:
        failures.append(f"  ✗ the launcher's cap          got={got} read={read}")

    # the rendering under the mark: a 300 000-character block served WHOLE under PP_PROMPT_CAP=2000000,
    # in two chunks without the variable (the floor), cut under 2 000 000 with a bigger block
    capped_env = bench.env("prompt-cap")
    capped_env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 20000\n---\n")
    capped_env.write("LONG.md", "---\nname: LONG\nkind: doc\n---\n\n" + "long line of matter\n" * 15000 + "\n")
    capped_env.write("procs/LONGRUN.md", LONGRUN)
    capped_env.write("HUGE.md", "---\nname: HUGE\nkind: doc\n---\n\n" + "long line of matter\n" * 125000 + "\n")
    capped_env.write("procs/HUGERUN.md", LONGRUN.replace("LONGRUN", "HUGERUN").replace("LONG.md", "HUGE.md"))

    caps: list = []

    def served(doc: str, value: str | None) -> list[int]:
        """-> the sizes of the chunks the output comes in, the principal's calls serving the rest."""
        conductor = capped_env.conductor()
        conductor.forget()
        spot = os.environ.get(context.PROMPT_CAP)
        if value is None:
            os.environ.pop(context.PROMPT_CAP, None)
        else:
            os.environ[context.PROMPT_CAP] = value
        try:
            block = _under("true", lambda: conductor.start(capped_env.made / "procs" / doc))
            sizes = [len(_under("true", lambda: conductor.rendered(block)))]
            while _under("true", conductor.pending) and len(sizes) < 50:
                sizes.append(len(_under("true", conductor.next_chunk)))
            caps.append((_under("true", conductor._cap), value))
        finally:
            if spot is None:
                os.environ.pop(context.PROMPT_CAP, None)
            else:
                os.environ[context.PROMPT_CAP] = spot
        return sizes

    whole = served("LONGRUN.md", "2000000")
    floored = served("LONGRUN.md", None)
    huge = served("HUGERUN.md", "2000000")
    # the first seam of a block is a section boundary: the first chunk is short, the body comes after,
    # cut at a line under the cap -- what the case reads is the cap each chunk holds and how many come
    if (len(whole) == 1 and whole[0] > 290000
            and len(floored) > 1 and max(floored) <= floor and sum(floored) > 290000
            and len(huge) > 1 and floor < max(huge) <= 2000000 and sum(huge) > 2400000):
        held("the principal's output is served under the launcher's cap", f"300 000 characters in ONE output "
             f"({whole[0]}) under PP_PROMPT_CAP=2000000; {len(floored)} chunks under the floor without it "
             f"(the biggest {max(floored)}); a 2 500 000-character block in {len(huge)} chunks under 2 000 000 "
             f"(the biggest {max(huge)}, over the floor)")
    else:
        failures.append(f"  ✗ the output under the cap    whole={whole} floored={floored} huge={huge} caps={caps}")

    # --- le-morceau-au-prompt-clot-more: the foot of a chunk follows the channel -------------------
    led = capped_env.conductor()
    led.forget()
    led_block = _under("true", lambda: led.start(capped_env.made / "procs" / "LONGRUN.md"))
    led_chunks = [_under("true", lambda: led.rendered(led_block))]
    while _under("true", led.pending) and len(led_chunks) < 50:
        led_chunks.append(_under("true", led.next_chunk))
    llm = capped_env.conductor()
    llm.forget()
    llm_block = _under(None, lambda: llm.start(capped_env.made / "procs" / "LONGRUN.md"))
    llm_chunks = [llm.rendered(llm_block)]
    while llm.pending() and len(llm_chunks) < 500:
        llm_chunks.append(llm.next_chunk())
    more = f"{Block.SIGNAL} {language.MORE}"

    def foot_of(text: str) -> list[str]:
        lines = text.splitlines()
        at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
        return lines[at:]

    led_feet = [foot_of(one) for one in led_chunks[:-1]]
    llm_feet = [foot_of(one) for one in llm_chunks[:-1]]
    if (len(led_chunks) > 1 and len(llm_chunks) > 1
            and all(foot[0] == more and len(foot) == 2 and foot[1].startswith("   (a reading continues")
                    for foot in led_feet)
            and all("./pp" not in "\n".join(foot) for foot in led_feet)
            and all(foot[0] == f"{Block.SIGNAL} {language.CONTINUE}" and foot[1].startswith("./pp ")
                    and len(foot) == 3 and foot[2].startswith("   (a reading continues") for foot in llm_feet)
            and not any(line.startswith(("▌ INSTRUCTION", "▌ CONSTRAINTS")) for one in led_chunks[:-1] + llm_chunks[:-1] for line in one.splitlines())
            and "WORK any => words" in led_chunks[-1] and "WORK any => words" in llm_chunks[-1]
            and not foot_of(led_chunks[-1]) and foot_of(llm_chunks[-1])[:1] == [f"{Block.SIGNAL} {language.AWAIT}"]):
        held("a chunk closes on MORE at the prompt, on CONTINUE by the tool", f"{len(led_chunks) - 1} chunk(s) "
             f"at the prompt close on `{more}` and the fact, no call; {len(llm_chunks) - 1} by the tool on CONTINUE, "
             "the bare call and the fact; no INSTRUCTION nor law before the last chunk, which carries the WORK and "
             "the foot of its form (none at the prompt where the step stays pending, AWAIT by the tool where the "
             "root's last step parks the run)")
    else:
        checks = {"led_more": all(foot[0] == more and len(foot) == 2 and foot[1].startswith("   (a reading continues") for foot in led_feet),
                  "led_nocall": all("./pp" not in "\n".join(foot) for foot in led_feet),
                  "llm_foot": all(foot[0] == f"{Block.SIGNAL} {language.CONTINUE}" and foot[1].startswith("./pp ") and len(foot) == 3 and foot[2].startswith("   (a reading continues") for foot in llm_feet),
                  "no_instruction": not any(line.startswith(("▌ INSTRUCTION", "▌ CONSTRAINTS")) for one in led_chunks[:-1] + llm_chunks[:-1] for line in one.splitlines()),
                  "work_led": "WORK any => words" in led_chunks[-1], "work_llm": "WORK any => words" in llm_chunks[-1],
                  "last_led": not foot_of(led_chunks[-1]), "last_llm": foot_of(llm_chunks[-1])[:1] == [f"{Block.SIGNAL} {language.AWAIT}"]}
        failures.append(f"  ✗ the chunk's foot            checks={checks} led={led_feet[:1]} llm={llm_feet[:1]} "
                        f"last={foot_of(led_chunks[-1])!r}/{foot_of(llm_chunks[-1])[:1]!r} "
                        f"n={len(led_chunks)}/{len(llm_chunks)}")
    return 0
