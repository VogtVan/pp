"""Scenario `chunked-output` -- an output over the host's cap, served in chunks through the console:
- le-geste-tient-le-cap: a gesture's output over the host's cap comes in chunks, none over it
- la-sortie-est-entiere: the chunks' matter concatenates to the script's output, byte for byte
- un-autre-appel-rebondit: while a chunk waits, any other call bounces `chunk-pending`
- le-geste-court-ne-bouge-pas: under the cap the output is the script's own, nothing waits
- le-run-ne-bouge-pas: the standing block is the same before the gesture and after its last chunk
- le-mount-apres-le-texte: a script that prints long and mounts leaves ONE rest at the run
- la-trace-pese-le-geste: `gesture` carries its chars and tokens, `cut` then one `chunk` each
- le-manuel-en-morceaux: a script's manual over the cap, called bare, closes on the seam and
  the bare call serves the rest
- le-rebond-chunk-pending: a keyed call on a waiting chunk -- a gesture, a value, a heredoc --
  serves the next chunk and plays nothing; after the last, the same gesture plays
- la-trace-des-morceaux: every chunk the console serves, each on a fresh conductor, is a
  `chunk` line of the run's trace, and `-stats` counts it
- le-skip: `-skip` on a waiting reading drops its rest -- nothing waits, the block's closing is
  served, `chunk-dropped` is traced, and the next keyed call plays without `chunk-pending`
"""
from __future__ import annotations

import json
import re

from conductor import Conductor, discovery, persistence
from tests.harness import bench_key, cli, session_of, support

shared = support(__file__, "console")
DOOR, WITNESS, LISTER, key_of = shared.DOOR, shared.WITNESS, shared.LISTER, shared.key_of

CAP = 3000
WAITING = "\n▶ CONTINUE"

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
    """The host's cap of the instance `made`, set in its SETTINGS."""
    settings = made / "SETTINGS.md"
    settings.write_text(re.sub(r"^max_harness_tool_output: \d+", f"max_harness_tool_output: {cap}",
                               settings.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")


def scenario(bench) -> int:
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
    bounced = cli(engine, key, "-s", "bigout", "lines", "2") if fresh().pending() else None
    if bounced is not None:
        outs.append(bounced.stdout.split("pp: chunk-pending")[0])
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

    # --- un-autre-appel-rebondit ------------------------------------------------------
    if bounced is not None and "chunk-pending" in bounced.stdout \
            and "line 0000" not in bounced.stdout.split("chunk-pending")[0][:80] \
            and rebuilt.count("line 0001") == 1:
        held("any other call bounces", "a second gesture while a chunk waits serves the next "
             "chunk and is said not played")
    else:
        failures.append(f"  ✗ no bounce                   {bounced and bounced.stdout[-160:]!r}")

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
             f"`gesture` carries {weighed[0]['chars']} chars and its tokens; `cut` then one "
             "`chunk` per bare call, counted by -stats")
    else:
        failures.append(f"  ✗ gesture unweighed           gestures={len(gestures)} "
                        f"weighed={len(weighed)} cut={kinds.count('cut')} chunk={kinds.count('chunk')}")

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
    if ("a reading continues" in first_chunk and "▌ INSTRUCTION" not in first_chunk
            and left_0 > 0 and 0 < left_1 < left_0 and 0 < left_2 < left_1 and 0 <= left_3 < left_2
            and all(one.returncode == 0 and "chunk-pending" in one.stdout and "a reading continues" in one.stdout
                    for one in (gestured, valued, piped) if left_3 > 0 or one is not piped)
            and "chunk-pending" not in played.stdout):
        held("a call on a waiting chunk bounces, and plays after the last",
             f"the boot cut under a 4000 cap closes its first chunk on the reading (no instruction); "
             f"a gesture, a value and a heredoc each served the next chunk and said `chunk-pending` "
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
    return 0
