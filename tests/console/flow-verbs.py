"""Scenario `flow-verbs` -- the console's flow verbs, what moves the run and what stands:
- les-cas-qui-avancent: the four calls that ANSWER the pending step move the run
- les-cas-qui-n-avancent-pas: the calls that render without moving it
- la-vue-tient-le-bloc-pendant: at a frontier, `-peek` shows the block that STANDS
- une-seule-carte-des-offres: the view and the dispatch read the same offer map
- la-vue-redit-le-pas-demande: an output cut at a `§` keeps its ask at the view
- le-rebond-redit-le-pas-demande: a denied `-s` re-shows that same ask
- les-refus-du-dispatch: a malformed form refuses, and the run stands untouched
- la-garde-des-formes: a keyed verb of the dispatch without its case is NAMED here
- le-message-a-l-ouverture: `-new <message…>` opens the run with the principal's message, traced `prompt` before the first block
- la-porte-sous-un-tube-ferme: a door played by `-s` whose stdout is closed before the
  console prints moves the run, says so on stderr in one line, exit 0, no traceback

The subject is the CONSOLE's dispatch, so every call goes through `cli()` -- the
facade in process never runs it, and that is exactly where the flow verbs decide.

The witness is the DOOR `-new` opens above the boot (`PP_DOOR`, as a launcher names it):
its own flow, its own law, proven at its frontier -- the stand-in base below it.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

from conductor import persistence
from tests.harness import SOURCE, cli, session_of, support

shared = support(__file__, "console")
DOOR, WITNESS, LISTER, key_of = shared.DOOR, shared.WITNESS, shared.LISTER, shared.key_of

DOORWAY = "---\nname: DOOR\nkind: proc\ndescription: a witness door\nproc: |\n  WORK\n---\nopen\n"
KEY = re.compile(r"run ([0-9a-f]{6})")

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

# every keyed verb the dispatch handles, and what it does to the RUN -- the case
# list this scenario covers; `la-garde-des-formes` confronts it to the source
COVERED = {"-s": False, "-peek": False, "-mount": False, "-compacted": False,
           "-disable": False, "-enable": False}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("flow").made
    engine = made / ".sys" / "engine" / "pp.py"
    (made / "procs" / "AGENT.md").write_text(WITNESS, encoding="utf-8")
    (made / "LISTER.md").write_text(LISTER, encoding="utf-8")
    cli(engine, "-new", env=DOOR)
    key = key_of(made)

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
    # the view renders what stands: it never plays the flow forward to find a block,
    # so the screen never offers a name the router would refuse
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
    # a fused output batches its WORK and closes on the barrier: the view re-says the
    # step it asked, never the tail behind the barrier, which carries no INSTRUCTION
    cut = bench.env("cut").made
    cut_engine = cut / ".sys" / "engine" / "pp.py"
    (cut / "procs" / "AGENT.md").write_text(BARRIER, encoding="utf-8")
    # the bench pins `fusion: none`; this shape IS a fused output, so it opts back in
    tuned = cut / "SETTINGS.md"
    tuned.write_text(tuned.read_text(encoding="utf-8")
                     .replace("instructions_fusion: none", "instructions_fusion: max"),
                     encoding="utf-8")
    opened = cli(cut_engine, "-new", env=DOOR)
    barred = key_of(cut)

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
    (fresh / "procs" / "AGENT.md").write_text(WITNESS, encoding="utf-8")
    (fresh / "LISTER.md").write_text(LISTER, encoding="utf-8")
    cli(still_engine, "-new", env=DOOR)
    still = key_of(fresh)

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

    # --- le-message-a-l-ouverture: `-new <message…>` opens the run WITH the principal's
    #     message -- the words after `-new` joined by a blank, traced `prompt` before the
    #     first block; `-new` bare opens exactly as before
    told = bench.env("flow-message").made
    told_engine = told / ".sys" / "engine" / "pp.py"
    (told / "procs" / "AGENT.md").write_text(WITNESS, encoding="utf-8")
    (told / "LISTER.md").write_text(LISTER, encoding="utf-8")
    worded = cli(told_engine, "-new", "hello", "world")
    told_key = key_of(told)
    told_trace = session_of(told).parent / persistence.trace_of(session_of(told))
    told_lines = [json.loads(line) for line in told_trace.read_text(encoding="utf-8").splitlines()
                  if line.strip()] if told_trace.is_file() else []
    told_kinds = [one["kind"] for one in told_lines]
    if (worded.returncode == 0 and f"run {told_key}" in worded.stdout
            and told_kinds[:2] == ["new", "prompt"] and told_lines[1]["text"] == "hello world"
            and "block" in told_kinds):
        held("-new carries the principal's message",
             "`-new hello world` hands the key and the trace says new, prompt `hello world`, "
             "then block -- the console's grammar of `<key> <message>`, at the opening")
    else:
        failures.append(f"  ✗ -new <message>              rc={worded.returncode} {told_kinds[:4]} "
                        f"{worded.stderr[-160:]!r}")

    # --- la-porte-sous-un-tube-ferme: the reader gone before the console prints -------
    pipe = bench.env("pipe")
    pipe.write("procs/DOOR.md", DOORWAY)
    pipe.write_member(front="tools: |\n  DOOR\n", body="The member works.", proc="WORK", name="AGENT")
    entered = pipe.cli("-new", "hello")
    door_key = KEY.search(entered.stdout).group(1)
    out = entered.stdout
    while "a reading continues" in out.rsplit("▶", 1)[-1]:
        out = pipe.cli(door_key).stdout
    child = subprocess.Popen([sys.executable, str(pipe.engine), door_key, "-s", "DOOR"],
                             cwd=str(pipe.root), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True)
    child.stdout.close()                 # the reader gone before the engine prints: BrokenPipe at its print
    err = child.stderr.read()
    rc = child.wait()
    peeked = pipe.cli(door_key, "-peek")
    slot = json.loads(persistence.slot_of(pipe.made, door_key).read_text(encoding="utf-8"))
    frames = [one.get("document", "").rsplit("/", 1)[-1] for one in slot.get("frames", [])]
    log = pipe.made / persistence.DIRECTORY / slot["log"]
    kinds = [json.loads(one).get("kind") for one in log.read_text(encoding="utf-8").splitlines()
             if one.strip()]
    if (rc == 0 and "Traceback" not in err and "Exception ignored" not in err and "pp: " in err
            and "-peek" in err and frames[-1:] == ["DOOR.md"] and kinds[-2:] == ["routed", "block"]
            and peeked.returncode == 0 and "▸ DOOR{1/1}" in peeked.stdout
            and "WORK any => response  (DOOR)" in peeked.stdout):
        held("a door under a closed stdout", f"run {door_key}: rc 0, one stderr line naming -peek, "
             "no traceback; the door's frame stands, `routed` then its block traced; -peek shows "
             "the door's block")
    else:
        failures.append(f"  ✗ broken pipe                rc={rc} err={err[-200:]!r} frames={frames} "
                        f"kinds={kinds[-3:]} peek={peeked.returncode}")
    return 0
