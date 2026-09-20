"""Scenario `gesture-cut` -- 7 case(s):
- le-geste-tient-le-cap: a gesture's output over the host's cap comes in chunks, none over it
- la-sortie-est-entiere: the chunks' matter concatenates to the script's output, byte for byte
- un-autre-appel-rebondit: while a chunk waits, any other call bounces `chunk-pending`
- le-geste-court-ne-bouge-pas: under the cap the output is the script's own, nothing waits
- le-run-ne-bouge-pas: the standing block is the same before the gesture and after its last chunk
- le-mount-apres-le-texte: a script that prints long and mounts leaves ONE rest at the run
- la-trace-pese-le-geste: `gesture` carries its chars and tokens, `cut` then one `chunk` each
"""
from __future__ import annotations

import json

from conductor import Conductor, discovery, persistence
from tests.harness import bench_key, cli, session_of

CAP = 3000
WAITING = "\n▶ CONTINUE"


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
    for proc in ("TURN", "CAPABILITIES"):
        (made / "procs" / f"{proc}.md").write_text(
            f"---\nname: {proc}\ntools: |\n  +bigout\n---\n", encoding="utf-8")
    settings = made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8")
                        .replace("max_harness_tool_output: 60000",
                                 f"max_harness_tool_output: {CAP}"), encoding="utf-8")

    def fresh() -> Conductor:
        return Conductor(member, discovery.siblings_around(member), engine, "t")

    boot = fresh().rendered(fresh().start(fresh().boot("BOOT.md")))
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
    return 0
