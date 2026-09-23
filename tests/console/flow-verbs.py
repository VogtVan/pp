"""Scenario `flow-verbs` -- 10 case(s):
- les-cas-qui-avancent: the four calls that ANSWER the pending step move the run
- les-cas-qui-n-avancent-pas: the calls that render without moving it
- la-vue-tient-le-bloc-pendant: at a frontier, `-peek` shows the block that STANDS
- une-seule-carte-des-offres: the view and the dispatch read the same offer map
- la-vue-redit-le-pas-demande: an output cut at a `§` keeps its ask at the view
- le-rebond-redit-le-pas-demande: a denied `-s` re-shows that same ask
- les-refus-du-dispatch: a malformed form refuses, and the run stands untouched
- la-garde-des-formes: a keyed verb of the dispatch without its case is NAMED here
- le-rebond-chunk-pending: a call on a waiting chunk bounces and plays after the last
- la-trace-des-morceaux: every chunk the console serves is a `chunk` line of the run's trace, and `-stats` counts it

The subject is the CONSOLE's dispatch, so every call goes through `cli()` -- the
facade in process never runs it, and that is exactly where the flow verbs decide.
"""
from __future__ import annotations

import re
from tests.harness import SOURCE, cli, session_of

WITNESS = """---
name: AGENT
kind: proc
description: the witness the console's flow verbs are exercised on
constraints.production: |
  W1  the witness produces what the step names, nothing else.
tools: |
  CAPABILITIES
proc: |
  WORK
  CALL LISTER.md
  PICK one
  WORK
  FINAL
---

the witness member.
"""

BARRIER = """---
name: AGENT
kind: proc
description: a witness whose output is CUT at a barrier, right after its step
tools: |
  CAPABILITIES
proc: |
  WORK
  §
  HOOK turn.end
  FINAL
---

the witness member.
"""

LISTER = """---
name: LISTER
kind: proc
description: hands a list downstream
output: json
proc: |
  INFER
---

the siblings
"""

READER = """---
name: AGENT
kind: proc
description: a witness whose boot reads a document longer than the host's cap
proc: |
  SERVE LONG.md
  WORK
  FINAL
---

the witness member.
"""

LONG = "---\nname: LONG\nkind: doc\n---\n\n" + "long line of matter\n" * 400

# every keyed verb the dispatch handles, and what it does to the RUN -- the case
# list this scenario covers; `la-garde-des-formes` confronts it to the source
COVERED = {"-s": False, "-peek": False, "-mount": False, "-compacted": False,
           "-disable": False, "-enable": False}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("flow").made
    engine = made / ".sys" / "engine" / "pp.py"
    (made / "MEMBER.md").write_text(WITNESS, encoding="utf-8")
    (made / "LISTER.md").write_text(LISTER, encoding="utf-8")
    cli(engine, "-new")
    key = session_of(made).name[len("session-"):-len(".json")]

    def state() -> bytes:
        return session_of(made).read_bytes()

    # --- les-cas-qui-avancent: the four answers ---------------------------------------
    moves = []
    opened = state()
    bare = cli(engine, key)                               # the bare advance
    moves.append(("bare", bare.returncode == 0 and state() != opened))
    piped = state()
    fed = cli(engine, key, "-", stdin='["io"]')           # the piped production
    moves.append(("-", fed.returncode == 0 and state() != piped))
    chosen = state()
    picked = cli(engine, key, "io")                       # a PICK's value, verbatim
    moves.append(("<value>", picked.returncode == 0 and state() != chosen))
    proved = state()
    proven = cli(engine, key, "-", stdin='[{"code": "W1", "evidence": "held", "verdict": "ok"}]')
    moves.append(("- (proof)", proven.returncode == 0 and state() != proved
                  and "FINAL" in proven.stdout))
    if all(ok for _, ok in moves):
        held("only an answer to the pending step advances",
             "the forms that carry the step's answer -- the bare call, a piped "
             "production, a PICK's value, the piped proof at the checkpoint -- each moved the run: "
             f"{', '.join(one for one, _ in moves)}")
    else:
        failures.append(f"  ✗ les cas qui avancent        {moves!r}")

    # --- la-vue-tient-le-bloc-pendant: at the frontier, the view shows what STANDS ----
    # S1.04, the second witness session (2026-08-29): the screen offered a name the
    # router refused, because the view PLAYED the flow forward to render something
    at_final = state()
    viewed = cli(engine, key, "-peek")
    marked = [one for one in viewed.stdout.splitlines() if one.startswith("▌ ")]
    if (viewed.returncode == 0 and "▶ FINAL" in viewed.stdout
            and "the conduction is over" not in viewed.stdout
            and state() == at_final):
        held("the view shows the block that stands",
             "at a delivered frontier `-peek` re-renders the FINAL that closed the "
             "output -- never the END the next call would reach; the slot is byte-identical")
    else:
        failures.append(f"  ✗ la vue tient le pendant     rc={viewed.returncode} "
                        f"{marked[:2]!r} {viewed.stdout[-60:]!r}")

    # --- une-seule-carte-des-offres: the view and the dispatch read the same map ------
    offers = next((one for one in viewed.stdout.splitlines() if one.startswith("[")), "")
    stranger = cli(engine, key, "-peek", "NOPE")
    gestured_stranger = cli(engine, key, "-s", "NOPE")
    if (stranger.returncode == 2 and gestured_stranger.returncode == 2
            and "not offered at this step" in stranger.stdout
            and "not offered at this step" in gestured_stranger.stdout
            and "NOPE" not in offers and state() == at_final):
        held("the view and the dispatch read one map",
             "a name the output does not offer is refused the same way by `-peek <name>` "
             "and by `-s <name>` -- one reader, and the screen never carries what it refuses")
    else:
        failures.append(f"  ✗ une seule carte des offres  {stranger.returncode}/"
                        f"{gestured_stranger.returncode} offers={offers!r}")

    # --- la-vue-redit-le-pas-demande: an output CUT at a barrier keeps its ask --------
    # S3.07, the steering witness (2026-08-30): the turn's output batched its WORK and
    # closed on the barrier; the view showed the TAIL -- the next step, with no
    # INSTRUCTION -- and the agent lost the production it still owed.
    cut = bench.env("cut").made
    cut_engine = cut / ".sys" / "engine" / "pp.py"
    (cut / "MEMBER.md").write_text(BARRIER, encoding="utf-8")
    # the bench pins `fusion: none`; this shape IS a fused output, so it opts back in
    tuned = cut / "SETTINGS.md"
    tuned.write_text(tuned.read_text(encoding="utf-8")
                     .replace("instructions_fusion: none", "instructions_fusion: max"),
                     encoding="utf-8")
    opened = cli(cut_engine, "-new")
    barred = session_of(cut).name[len("session-"):-len(".json")]

    def shown(out: str) -> tuple[str, list[str]]:
        """-> (the segment's heading, the instruction lines) of a rendered output."""
        marked = [one for one in out.splitlines() if one.startswith("▌ ")]
        steps = [one for one in out.splitlines()
                 if re.match(r"^(WORK|INFER|PICK) ", one)]
        return (marked[1] if len(marked) > 1 else ""), steps

    asked_at, asked_steps = shown(opened.stdout)
    resting = session_of(cut).read_bytes()
    seen = cli(cut_engine, barred, "-peek")
    view_at, view_steps = shown(seen.stdout)
    if (seen.returncode == 0 and view_at == asked_at and view_steps == asked_steps
            and session_of(cut).read_bytes() == resting):
        held("the view re-says the step the output asked for",
             f"an output cut at a `§` closes on a block carrying no step of its own; "
             f"`-peek` re-renders what it ASKED -- {asked_at.split()[-1]} and "
             f"{asked_steps} -- never the tail behind the barrier, and the slot is "
             "byte-identical")
    else:
        failures.append(f"  ✗ la vue redit le pas demande  asked={asked_at!r}{asked_steps!r} "
                        f"vue={view_at!r}{view_steps!r}")

    # --- le-rebond-redit-le-pas-demande: the denial rides the same block --------------
    bounced = cli(cut_engine, barred, "-s", "NOPE")
    bounce_at, bounce_steps = shown(bounced.stdout)
    if (bounced.returncode == 2 and bounce_at == asked_at and bounce_steps == asked_steps
            and "not offered at this step" in bounced.stdout
            and session_of(cut).read_bytes() == resting):
        held("a denied gesture re-says the same ask",
             "`-s <name>` on a name the output does not offer poses its DEVIATION on the "
             "block the view shows -- one site, one ask, and nothing played")
    else:
        failures.append(f"  ✗ le rebond redit le pas      rc={bounced.returncode} "
                        f"{bounce_at!r}{bounce_steps!r}")

    # --- les-cas-qui-n-avancent-pas: what renders and stands --------------------------
    fresh = bench.env("still").made
    still_engine = fresh / ".sys" / "engine" / "pp.py"
    (fresh / "MEMBER.md").write_text(WITNESS, encoding="utf-8")
    (fresh / "LISTER.md").write_text(LISTER, encoding="utf-8")
    cli(still_engine, "-new")
    still = session_of(fresh).name[len("session-"):-len(".json")]

    def stands() -> bytes:
        return session_of(fresh).read_bytes()

    def position() -> str:
        """-> the standing block's own heading: where the run STANDS. The first
        marked line is the OUTPUT's heading (the run and the hour), the second the
        segment's -- the stack is on that one."""
        marked = [one for one in cli(still_engine, still, "-peek").stdout.splitlines()
                  if one.startswith("▌ ")]
        return marked[1] if len(marked) > 1 else ""

    quiet = []
    before, stood = stands(), position()
    looked = cli(still_engine, still, "-peek")            # a view writes nothing at all
    quiet.append(("-peek", looked.returncode == 0 and stands() == before
                  and "▌ pp · " in looked.stdout))
    gestured = cli(still_engine, still, "-s", "NOPE")     # denied: nothing played
    quiet.append(("-s", gestured.returncode == 2 and stands() == before))
    mounted = cli(still_engine, still, "-mount", "LISTER.md")   # hosts, never advances
    quiet.append(("-mount", mounted.returncode == 0 and position() == stood))
    told = cli(still_engine, still, "-compacted")         # arms its own flag, nothing else
    quiet.append(("-compacted", told.returncode == 0 and position() == stood))
    kept = stands()                  # what -mount and -compacted wrote is the ground now
    switched = cli(still_engine, still, "-disable", "nope")   # no such pin: refuses
    quiet.append(("-disable", switched.returncode == 2 and "package-unpinned" in switched.stderr
                  and stands() == kept))
    lifted = cli(still_engine, still, "-enable", "kit")       # the base is never switched
    quiet.append(("-enable", lifted.returncode == 2 and "package-base" in lifted.stderr
                  and stands() == kept))
    if all(ok for _, ok in quiet):
        held("a verb renders, it does not conduct",
             "`-peek` and a denied `-s` leave the slot byte-identical; `-mount` and "
             "`-compacted` write their own state and leave the POSITION where it stood; "
             "`-disable` and `-enable` refuse by name on a kit-only instance and write "
             f"nothing -- none of the six answers the pending step ({stood})")
    else:
        failures.append(f"  ✗ les cas qui n'avancent pas  {quiet!r}")

    # --- le-rebond-chunk-pending (rework of la-coupe-du-bloc, 2026-09-09): while a cut
    # output's rest waits, any keyed call but the bare one BOUNCES: the next chunk is
    # served, the call is said not played, the run stands; the throwaway of 2026-09-09 --
    # a gesture played on a chunk lost the rest -- replays green here
    bounce = bench.env("bounce").made
    bounce_engine = bounce / ".sys" / "engine" / "pp.py"
    (bounce / "MEMBER.md").write_text(WITNESS, encoding="utf-8")
    (bounce / "LISTER.md").write_text(LISTER, encoding="utf-8")
    low = bounce / "SETTINGS.md"
    low.write_text(re.sub(r"^max_harness_tool_output: \d+", "max_harness_tool_output: 4000",
                          low.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    opened = cli(bounce_engine, "-new")
    bkey = session_of(bounce).name[len("session-"):-len(".json")]
    first_chunk = opened.stdout

    def left() -> int:
        import json as _json
        return len(_json.loads(session_of(bounce).read_text(encoding="utf-8")).get("pending", {}).get("matter", ""))

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
    (traced / "MEMBER.md").write_text(READER, encoding="utf-8")
    (traced / "LONG.md").write_text(LONG, encoding="utf-8")
    tuned = traced / "SETTINGS.md"
    tuned.write_text(re.sub(r"^max_harness_tool_output: \d+", "max_harness_tool_output: 4000",
                            tuned.read_text(encoding="utf-8"), flags=re.M), encoding="utf-8")
    booted = cli(traced_engine, "-new")
    tkey = session_of(traced).name[len("session-"):-len(".json")]

    def waiting() -> bool:
        import json as _json
        return bool(_json.loads(session_of(traced).read_text(encoding="utf-8"))
                    .get("pending", {}).get("matter"))

    served_chunks = 0
    while waiting() and served_chunks < 200:
        cli(traced_engine, tkey)
        served_chunks += 1
    import json as _json
    trace = traced / ".sys" / "state" / _json.loads(session_of(traced).read_text(encoding="utf-8"))["log"]
    events = [_json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines() if line.strip()]
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

    # --- les-refus-du-dispatch: a malformed form refuses and touches nothing ----------
    wrong, kept = [], stands()
    for form in (("-sp",), ("-compacted", "extra"), ("-mount",)):
        answered = cli(still_engine, still, *form)
        wrong.append((" ".join(form), answered.returncode != 0
                      and bool(answered.stderr.strip()) and stands() == kept))
    if all(ok for _, ok in wrong):
        held("a malformed form refuses and plays nothing",
             "`-sp` is no verb any more, `-compacted` takes no other argument, `-mount` takes documents: "
             "each says why on stderr, exits non-zero, and leaves the slot byte-identical")
    else:
        failures.append(f"  ✗ les refus du dispatch       {wrong!r}")

    # --- la-garde-des-formes: the list is DERIVED from the dispatch -------------------
    console = (SOURCE / "engine" / "pp.py").read_text(encoding="utf-8")
    keyed = console[console.index("if key is not None:"):console.index('if argv[0] == "-s":')]
    declared = set(re.findall(r'\["(-[a-z]+)"\]', keyed))
    orphan = sorted(declared - set(COVERED))
    if declared and not orphan:
        held("every keyed verb of the dispatch has its case",
             f"{len(declared)} verb(s) read from the console's own source "
             f"({', '.join(sorted(declared))}) -- the list is derived, never held by hand")
    else:
        failures.append(f"  ✗ la garde des formes         sans cas : {orphan!r}")
    return 0
