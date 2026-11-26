"""Scenario `chunked-output` -- an output over the host's cap, served in chunks through the console:
- le-geste-tient-le-cap: a gesture's output over the host's cap comes in chunks, none over it
- la-sortie-est-entiere: the chunks' matter concatenates to the script's output, byte for byte
- rien-ne-joue-sur-un-morceau: while a chunk waits, a script's gesture and a `-print` BOUNCE -- each
  says `chunk-pending` first and serves the next chunk, the script not run, the print not kept
- le-geste-court-ne-bouge-pas: under the cap the output is the script's own, nothing waits
- le-run-ne-bouge-pas: the standing block is the same before the gesture and after its last chunk
- le-mount-apres-le-texte: a script that prints long and mounts leaves ONE rest at the run
- la-trace-pese-le-geste: `gesture` carries its chars and tokens, `cut` then one `chunk` each
- le-manuel-en-morceaux: a script's manual over the cap, called bare, closes on the seam and
  the bare call serves the rest
- la-suite-sous-le-premier-plafond: the rest of a cut output keeps the cap of its first chunk --
  a bare call under a roomier cap serves it in chunks under that first cap, never whole
- le-rebond-chunk-pending: a keyed call that MOVES the run on a waiting chunk -- a door, a value, a
  heredoc -- serves the next chunk and plays nothing, the fact said FIRST, the chunk after; after the
  last, the same door plays
- la-trace-des-morceaux: every chunk the console serves, each on a fresh conductor, is a
  `chunk` line of the run's trace, and `-stats` counts it
- le-skip: `-skip` on a waiting reading drops its rest -- nothing waits, the block's closing is
  served, `chunk-dropped` is traced, and the next keyed call plays without `chunk-pending`
- le-skip-garde-le-plafond: `-skip` under a roomier cap serves the steps that wait in chunks under
  the cap of the first cut, their brief read whole
"""
from __future__ import annotations

import json
import os
import re

from conductor import Conductor, discovery, persistence
from conductor.core import language, messages
from conductor.state import context
from tests.harness import bench_key, cli, session_of, support

shared = support(__file__, "console")
DOOR, WITNESS, LISTER, key_of = shared.DOOR, shared.WITNESS, shared.LISTER, shared.key_of

CAP = 3000
WAITING = "\n▶ MORE"                 # the foot of a chunk before the last, at the prompt

READER = """---
name: AGENT
kind: proc
description: a witness whose boot reads a document longer than the host's cap
proc: |
  SERVE LONG.md
  WORK
---

the witness member.
"""

LONG = "---\nname: LONG\nkind: doc\n---\n\n" + "long line of matter\n" * 400


def capped(made, cap: int) -> None:
    """The cap of the outputs of the instance `made`: the host's in its SETTINGS, and the one the
    principal's launcher names on its calls (`PP_PROMPT_CAP`, set in THIS process, which every call
    of the console inherits) -- the cap a run its principal conducts is cut under."""
    settings = made / "SETTINGS.md"
    settings.write_text(re.sub(r"^max_harness_tool_output: \d+", f"max_harness_tool_output: {cap}",
                               settings.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    os.environ[context.PROMPT_CAP] = str(cap)


def scenario(bench) -> int:
    try:
        return _played(bench)
    finally:
        os.environ.pop(context.PROMPT_CAP, None)


def _played(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("gcut").made
    engine = made / ".sys" / "engine" / "pp.py"
    member = discovery.instance_member(engine)
    home = made / "skills" / "bigout"
    home.mkdir(parents=True)
    (home / "SKILL.md").write_text(
        "---\nname: bigout\ndescription: a witness that prints as many lines as asked\n---\n"
        "`lines <n>` prints n numbered lines; `mounted <n>` mounts NOTE.md first.\n",
        encoding="utf-8")
    (home / "bigout.py").write_text(
        "def main(argv):\n"
        "    if argv[0] == 'mounted':\n"
        "        print('::mount [{\"doc\": \"NOTE.md\", \"body\": true}]')\n"
        "    for n in range(int(argv[1])):\n"
        "        print(f'line {n:04d} of the witness output, padded to a steady width')\n"
        "    return 0\n", encoding="utf-8")
    (made / "NOTE.md").write_text("---\nname: NOTE\nkind: doc\n---\n\nthe mounted note\n",
                                  encoding="utf-8")
    manual = made / "skills" / "long"          # a script whose contract, its MANUAL, is over the cap
    manual.mkdir(parents=True)
    (manual / "SKILL.md").write_text(
        "---\nname: long\ndescription: a witness whose contract is its manual\n---\n"
        "The long manual.\n" + "A line of the long manual, one of many.\n" * 120, encoding="utf-8")
    (manual / "long.py").write_text(
        "def main(argv):\n    print('ran: ' + ' '.join(argv))\n    return 0\n", encoding="utf-8")
    for proc in ("TURN", "CAPABILITIES"):
        (made / "procs" / f"{proc}.md").write_text(
            f"---\nname: {proc}\ntools: |\n  +bigout\n  +long\n---\n", encoding="utf-8")
    capped(made, CAP)

    def fresh() -> Conductor:
        return Conductor(member, engine, "t")

    fresh().rendered(fresh().start(fresh().boot("BOOT.md")))   # the boot output, drained below
    while fresh().pending():
        fresh().next_chunk()
    key = bench_key(member.meta)
    expected = "".join(f"line {n:04d} of the witness output, padded to a steady width\n"
                       for n in range(110))

    def matter_of(out: str) -> str:
        """-> a chunk minus the output's heading and the closing of an intermediate chunk."""
        body = out
        if body.startswith("▌"):
            body = body.split("\n\n", 1)[1] if "\n\n" in body else ""
        if WAITING in body:
            body = body[:body.index(WAITING)]
        return body

    # --- le-geste-tient-le-cap / la-sortie-est-entiere --------------------------------
    before = fresh().peek()
    first = cli(engine, key, "-s", "bigout", "lines", "110")
    outs = [first.stdout]

    def waiting() -> int:
        return len(json.loads(session_of(member.meta).read_text(encoding="utf-8")).get("pending", {}).get("matter", ""))

    def handed() -> int:
        """-> how many prints the run's trace keeps: a print played, answered or stray."""
        slot = session_of(member.meta)
        log = slot.parent / json.loads(slot.read_text(encoding="utf-8")).get("log", "")
        lines = log.read_text(encoding="utf-8").splitlines() if log.is_file() else []
        return sum(1 for one in lines if one.strip() and json.loads(one).get("kind") in ("answer", "stray"))

    def bounced(out) -> bool:
        """-> whether the call `out` bounced: the fact first, the next chunk after it, which joins `outs`."""
        if out is None or out.returncode != 0 or not out.stdout.startswith("pp: chunk-pending"):
            return False
        outs.append(out.stdout.split("\n", 1)[1])
        return True

    left_gesture = waiting()
    gestured_meanwhile = cli(engine, key, "-s", "bigout", "lines", "2") if fresh().pending() else None
    gesture_bounced = bounced(gestured_meanwhile)
    left_still = waiting()
    prints_before = handed()
    printed_meanwhile = cli(engine, key, "-print", "TURN", "-", stdin="a print over a chunk\n") \
        if fresh().pending() else None
    print_bounced = bounced(printed_meanwhile)
    left_printed, prints_after = waiting(), handed()
    while fresh().pending() and len(outs) < 50:
        outs.append(cli(engine, key).stdout)
    over = [len(one) for one in outs if len(one) > CAP + 1]      # the print's own newline
    if len(outs) > 2 and not over and "a reading continues" in outs[0] \
            and all(f"run {key}" in one.splitlines()[0] for one in outs):
        held("a gesture over the cap comes in chunks",
             f"{len(outs)} chunks, none over {CAP}, each opening on the run's heading")
    else:
        failures.append(f"  ✗ gesture over the cap        {len(outs)} chunk(s), over: {over} "
                        f"{outs[0][-120:]!r}")
    rebuilt = "".join(matter_of(one.rstrip("\n")) for one in outs)
    if rebuilt.replace("\n", "") == expected.replace("\n", "") and \
            rebuilt.count("line ") == 110:
        held("the output comes back whole", "the chunks' matter is the script's output, "
             "every line once, in order")
    else:
        failures.append(f"  ✗ gesture matter lost         {rebuilt.count('line ')} line(s)")

    # --- rien-ne-joue-sur-un-morceau ----------------------------------------------------
    if (gesture_bounced and print_bounced and 0 < left_still < left_gesture and left_printed < left_still
            and prints_after == prints_before and rebuilt.count("line 0001") == 1):
        held("nothing plays while a chunk waits", "a second gesture and a -print over the first gesture's "
             "waiting chunk each say `chunk-pending` first and serve the next chunk "
             f"({left_gesture} -> {left_still} -> {left_printed} characters waiting); the script not run, "
             "the print not kept")
    else:
        failures.append(f"  ✗ played over a chunk         gesture={gestured_meanwhile and gestured_meanwhile.stdout[:120]!r} "
                        f"print={printed_meanwhile and printed_meanwhile.stdout[:120]!r} "
                        f"left={left_gesture}->{left_still}->{left_printed} prints={prints_before}->{prints_after}")

    # --- le-run-ne-bouge-pas ----------------------------------------------------------
    after = fresh().peek()
    same = (before is not None and after is not None
            and (before.stack, before.position, before.command)
            == (after.stack, after.position, after.command))
    if same and not persistence.pending_of(session_of(member.meta)):
        held("the run stands where it stood", "same stack, position and owed call before "
             "the gesture and after its last chunk; nothing left waiting")
    else:
        failures.append(f"  ✗ run moved                   same={same}")

    # --- le-geste-court-ne-bouge-pas --------------------------------------------------
    short = cli(engine, key, "-s", "bigout", "lines", "3")
    if short.stdout == "".join(expected.splitlines(keepends=True)[:3]) and not fresh().pending():
        held("a short gesture is untouched", "the script's own output, byte for byte: no "
             "heading, no closing, nothing waiting")
    else:
        failures.append(f"  ✗ short gesture changed       {short.stdout[:120]!r}")

    # --- le-mount-apres-le-texte ------------------------------------------------------
    mounted = [cli(engine, key, "-s", "bigout", "mounted", "110").stdout]
    while fresh().pending() and len(mounted) < 50:
        mounted.append(cli(engine, key).stdout)
    said = "".join(mounted)
    if len(mounted) > 2 and not [1 for one in mounted if len(one) > CAP + 1] \
            and said.count("line 0109") == 1 and "the mounted note" in said \
            and "::mount" not in said and said.index("line 0109") < said.index("the mounted note"):
        held("a long text then a mount is ONE cut output",
             f"{len(mounted)} chunks, the script's text first, the mounted view after, "
             "one rest at the run")
    else:
        failures.append(f"  ✗ text then mount             {len(mounted)} chunk(s) "
                        f"{[len(one) for one in mounted]}")

    # --- la-trace-pese-le-geste -------------------------------------------------------
    slot = session_of(member.meta)
    log_name = json.loads(slot.read_text(encoding="utf-8")).get("log", "")
    events = [json.loads(one) for one in
              (slot.parent / log_name).read_text(encoding="utf-8").splitlines() if one.strip()]
    gestures = [one for one in events if one.get("kind") == "gesture" and one.get("name") == "bigout"]
    weighed = [one for one in gestures if one.get("chars")]
    kinds = [one.get("kind") for one in events]
    stats = cli(engine, "-stats")
    if (len(gestures) == 3 and len(weighed) == 3 and weighed[0]["chars"] == len(expected.rstrip("\n"))
            and weighed[0].get("tokens") and kinds.count("cut") >= 2
            and kinds.count("chunk") >= len(outs) - 1 + len(mounted) - 1
            and " chunk(s)" in stats.stdout and "+ 0 chunk(s)" not in stats.stdout):
        held("the trace weighs the gesture",
             f"`gesture` carries {weighed[0]['chars']} chars and its tokens (3 gestures, the one bounced over a chunk never played); `cut` then one "
             "`chunk` per bare call, counted by -stats")
    else:
        failures.append(f"  ✗ gesture unweighed           gestures={len(gestures)} "
                        f"weighed={len(weighed)} cut={kinds.count('cut')} chunk={kinds.count('chunk')}")

    # --- la-suite-sous-le-premier-plafond: the bare calls of a roomier launcher -----------
    cut_first = cli(engine, key, "-s", "bigout", "lines", "110")      # cut under CAP
    roomy = {context.PROMPT_CAP: str(100 * CAP)}                      # a launcher whose cap holds it all
    rests = []
    while fresh().pending() and len(rests) < 50:
        rests.append(cli(engine, key, env=roomy).stdout)
    served = matter_of(cut_first.stdout.rstrip("\n")) + "".join(matter_of(one.rstrip("\n")) for one in rests)
    if ("a reading continues" in cut_first.stdout and len(rests) >= 2
            and all(len(one) <= CAP + 1 for one in rests) and served.count("line 0109") == 1
            and served.count("line 0000") == 1):
        held("the rest keeps the first chunk's cap", f"a gesture cut under {CAP}, its rest served by bare calls "
             f"under a cap of {100 * CAP}: {len(rests)} chunk(s), none over {CAP}, every line once")
    else:
        failures.append(f"  ✗ la suite sous le plafond   {len(rests)} chunk(s) {[len(one) for one in rests]} "
                        f"under the first cap {CAP}")

    # --- le-manuel-en-morceaux: a script called bare mounts its manual, cut at the cap ----
    first_chunk = cli(engine, key, "-s", "long")
    rest_chunk = cli(engine, key)
    if (first_chunk.returncode == 0 and "a reading continues" in first_chunk.stdout
            and "one of many" not in first_chunk.stdout
            and rest_chunk.returncode == 0 and "one of many" in rest_chunk.stdout
            and "INFORMATION — long" in first_chunk.stdout + rest_chunk.stdout):
        held("a manual over the cap comes in chunks", "the first output closes on the seam, "
             "the bare call serves the rest -- the manual is read whole, never truncated")
    else:
        failures.append(f"  ✗ long manual                 rc={first_chunk.returncode}/"
                        f"{rest_chunk.returncode} {first_chunk.stdout[-160:]!r}")

    # --- le-rebond-chunk-pending: while a cut output's rest waits, any keyed call but the
    # bare one BOUNCES -- the next chunk is served, the call is said not played, the run
    # stands; a gesture played on a chunk would lose the rest
    bounce = bench.env("bounce").made
    bounce_engine = bounce / ".sys" / "engine" / "pp.py"
    (bounce / "procs" / "AGENT.md").write_text(WITNESS, encoding="utf-8")
    (bounce / "LISTER.md").write_text(LISTER, encoding="utf-8")
    capped(bounce, 4000)
    opened = cli(bounce_engine, "-new", env=DOOR)
    bkey = key_of(bounce)
    first_chunk = opened.stdout

    def left() -> int:
        return len(json.loads(session_of(bounce).read_text(encoding="utf-8"))
                   .get("pending", {}).get("matter", ""))

    left_0 = left()
    gestured = cli(bounce_engine, bkey, "-s", "CAPABILITIES")     # offered, but a chunk waits
    left_1 = left()
    valued = cli(bounce_engine, bkey, "io")                         # a value: bounces too
    left_2 = left()
    piped = cli(bounce_engine, bkey, "-", stdin='["io"]')           # a heredoc: bounces too
    left_3 = left()
    drained = 0
    while left() and drained < 200:
        cli(bounce_engine, bkey)
        drained += 1
    played = cli(bounce_engine, bkey, "-s", "CAPABILITIES")        # nothing waits: it plays
    # the heading LINE of a step, never the words a served text may cite
    instruction = re.compile(rf"^{re.escape(messages.title(language.INSTRUCTION))}$", re.M)
    if ("a reading continues" in first_chunk and not instruction.search(first_chunk)
            and left_0 > 0 and 0 < left_1 < left_0 and 0 < left_2 < left_1 and 0 <= left_3 < left_2
            and all(one.returncode == 0 and one.stdout.startswith("pp: chunk-pending") and "a reading continues" in one.stdout
                    for one in (gestured, valued, piped) if left_3 > 0 or one is not piped)
            and "chunk-pending" not in played.stdout):
        held("a call that moves the run bounces on a waiting chunk, and plays after the last",
             f"the boot cut under a 4000 cap closes its first chunk on the reading (no instruction); "
             f"a door, a value and a heredoc each said `chunk-pending` FIRST and served the next chunk "
             f"({left_0} -> {left_1} -> {left_2} -> {left_3} characters waiting), nothing played; "
             f"after {drained} bare call(s) the same gesture plays -- the rest is never lost")
    else:
        failures.append(f"  ✗ le rebond                   left={left_0}/{left_1}/{left_2}/{left_3} "
                        f"rc={gestured.returncode}/{valued.returncode}/{piped.returncode} "
                        f"{gestured.stdout[-120:]!r} played={played.stdout[-80:]!r}")

    # --- la-trace-des-morceaux: the console serves each chunk on a FRESH conductor, so the
    # trace is read where the console writes it -- never on a facade held in process
    traced = bench.env("traced").made
    traced_engine = traced / ".sys" / "engine" / "pp.py"
    (traced / "procs" / "AGENT.md").write_text(READER, encoding="utf-8")
    (traced / "LONG.md").write_text(LONG, encoding="utf-8")
    capped(traced, 4000)
    booted = cli(traced_engine, "-new", env=DOOR)
    tkey = key_of(traced)

    def waiting() -> bool:
        return bool(json.loads(session_of(traced).read_text(encoding="utf-8"))
                    .get("pending", {}).get("matter"))

    served_chunks = 0
    while waiting() and served_chunks < 200:
        cli(traced_engine, tkey)
        served_chunks += 1
    trace = traced / ".sys" / "state" / json.loads(session_of(traced).read_text(encoding="utf-8"))["log"]
    events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()]
    chunks = [one for one in events if one.get("kind") == "chunk"]
    cuts = [one for one in events if one.get("kind") == "cut"]
    stats = cli(traced_engine, "-stats", tkey)
    counted = re.search(r"(\d+) chunk\(s\)", stats.stdout)
    if (booted.returncode == 0 and "a reading continues" in booted.stdout
            and served_chunks >= 1 and len(cuts) == 1
            and len(chunks) == served_chunks and chunks[-1].get("left") == 0
            and counted and int(counted.group(1)) == served_chunks):
        held("every chunk the console serves is traced and counted",
             f"the boot cut under a 4000 cap: one `cut`, then {served_chunks} bare call(s) and "
             f"{len(chunks)} `chunk` line(s) in the run's trace, the last saying `left: 0`; "
             f"`-stats {tkey}` says {counted.group(1)} chunk(s)")
    else:
        failures.append(f"  ✗ la trace des morceaux       served={served_chunks} cut={len(cuts)} "
                        f"chunk={len(chunks)} last={chunks[-1] if chunks else None} "
                        f"stats={counted.group(0) if counted else stats.stdout[-120:]!r}")

    # --- le-skip: the rest of a cut reading dropped on the agent's word ------------------------
    skipping = bench.env("skipping").made
    skipping_engine = skipping / ".sys" / "engine" / "pp.py"
    (skipping / "procs" / "AGENT.md").write_text(READER, encoding="utf-8")
    (skipping / "LONG.md").write_text(LONG, encoding="utf-8")
    capped(skipping, 4000)
    cli(skipping_engine, "-new", env=DOOR)
    skey = key_of(skipping)
    cut_before = bool(json.loads(session_of(skipping).read_text(encoding="utf-8")).get("pending", {}).get("matter"))
    skipped = cli(skipping_engine, skey, "-skip")
    after = json.loads(session_of(skipping).read_text(encoding="utf-8"))
    log = skipping / ".sys" / "state" / after["log"]
    dropped = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()
               if line.strip() and json.loads(line).get("kind") == "chunk-dropped"]
    next_call = cli(skipping_engine, skey)
    if (cut_before and skipped.returncode == 0 and not after.get("pending", {}).get("matter")
            and "▌ INSTRUCTION" in skipped.stdout and len(dropped) == 1 and dropped[0].get("left", 0) > 0
            and next_call.returncode == 0 and "chunk-pending" not in next_call.stdout):
        held("-skip drops the rest of a reading", f"{dropped[0]['left']} characters dropped, the block's "
             "closing served, `chunk-dropped` traced; the next call plays")
    else:
        failures.append(f"  ✗ le skip                     cut={cut_before} rc={skipped.returncode} "
                        f"{skipped.stdout[-200:]!r} {skipped.stderr[-160:]!r} dropped={dropped}")

    # --- le-skip-garde-le-plafond: the steps after -skip, under the first cut's cap -------------------
    briefed = bench.env("skipcap").made
    briefed_engine = briefed / ".sys" / "engine" / "pp.py"
    (briefed / "procs" / "AGENT.md").write_text(
        READER + "".join(f"brief line {n:03d} of the witness's step\n" for n in range(200)), encoding="utf-8")
    (briefed / "LONG.md").write_text(LONG, encoding="utf-8")
    capped(briefed, 4000)
    cli(briefed_engine, "-new", env=DOOR)
    bkey2 = key_of(briefed)
    roomy = {context.PROMPT_CAP: str(100 * 4000)}

    def briefed_left() -> dict:
        return json.loads(session_of(briefed).read_text(encoding="utf-8")).get("pending", {})

    skipped_roomy = cli(briefed_engine, bkey2, "-skip", env=roomy)
    after_skip = [skipped_roomy.stdout]
    while briefed_left() and len(after_skip) < 50:
        after_skip.append(cli(briefed_engine, bkey2, env=roomy).stdout)
    read = "".join(after_skip)
    if (skipped_roomy.returncode == 0 and len(after_skip) >= 2 and all(len(one) <= 4001 for one in after_skip)
            and all(read.count(f"brief line {n:03d} ") == 1 for n in range(200))):
        held("-skip keeps the first cut's cap", f"the boot cut under 4000, `-skip` and the bare calls under a "
             f"cap of 400000: the steps in {len(after_skip)} chunks, none over 4000, the brief whole")
    else:
        failures.append(f"  ✗ le skip garde le plafond    rc={skipped_roomy.returncode} "
                        f"chunks={[len(one) for one in after_skip]} {skipped_roomy.stderr[-160:]!r}")
    return 0
