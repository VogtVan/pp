"""Scenario `principal-open-output` -- the principal holds an output OPEN: `PP_HOLD_OUTPUT=true`
on the calls of an exchange -- an opening, a message, a mount. The call that carries the message opens the
exchange and renders no block, each mount is posed, and the principal's bare call plays the exchange and renders
ONE output: the scopes the mounts nested, then every step once, with the laws then in force.
- (a) the principal's `-new` under the flag renders no block: the trace says `held` (act value, open), the slot holds
  the output open; nothing of the step that stands is traced as a block
- (b) two mounts under the flag are posed: the trace says `held` (act mount, open) at each, the documents are
  mounted, no block is rendered between them
- (c) the principal's bare call renders the whole: one segment in the offer map, one block traced after
  the last mount, the laws of both mounts in force on the step that stands (the slot's segments), the matter of
  the first mount served before the second's, the hold gone; the proof given next names both laws, and the run
  parks on it
- (d) the same calls without the flag render the block that stands at each mount: one block after each
- (e) a message under the flag at the parked run, one mount, the release: the same, at a resume -- nothing repaired
- (g) an output that closed already waits at the run (the agent's value, held): a message under the flag changes
  nothing -- the call prints the run's key and the line that says an output waits (s.1785), the slot's held output is as it was, nothing open,
  nothing traced; the principal's bare call serves it
- (h) a bare call whose release fails (the test damages the open output at the slot) serves nothing and leaves
  the output open at the slot; the damage undone, the next bare call serves it whole
- (i) a door of four fused steps opened under the flag: the release renders the door's steps under their range,
  `{1-4/4}`, as the same door renders it when nothing holds the output
- (o) a closed output waits at the run and several of its segments offer the script (the agent opened a door
  of two steps under two scopes): the principal's gesture under the flag names the script bare and mounts -- judged on
  what the root of the passage offers, never on a segment --, its view joins the output that waits, and the bare
  call serves one output, the step that stands once
- (j) the context of an exchange stands before its steps, at an opening: a contributor's step plays before the
  WORK; the opening and each of two mounts render nothing -- an open output without a segment, no block traced
  --, and the bare call renders ONE output: the readings of both mounts before the first step's line, their
  laws in the block of that step, one line per step, nothing of the text the script printed
- (k) the same at the resume of a parked run: the message opens the exchange and renders nothing
- (l) the same on a run that stands on its WORK: the mounts render nothing, the bare call renders the step
  that stands once, the readings before its line
- (m) an exchange left open -- its message played, one mount posed, the next refused -- is taken up: the
  refusal renders nothing and leaves the output open; a second message opens nothing more, a mount the view
  already holds serves nothing more, and the bare call renders the exchange once, the context before its steps
- (q) a DOOR the root of the passage offers, named by the principal before the bare call, is refused -- at an
  opening and at the resume of a parked run, by `-s` and by `-open`, bare and addressed to a segment of the
  last output, under the flag and without it: nothing stacks, nothing is rendered, the output still waits
  open, and the bare call renders each step once, none of the door's
- (n) the release cut under a cap (`PP_PROMPT_CAP` on the bare calls): the first bare call serves the first
  chunk, the next ones the rest, every chunk under the cap; over the chunks the readings of both mounts stand
  before the first step's line and each step's line stands once
"""
from __future__ import annotations

import json
import re

from conductor.core import messages
from conductor import persistence
from conductor.core import language
from conductor.state import context
from tests.harness import cli, support, titled, titles

run = support(__file__, "run")

HOLD = {context.HOLD: "true"}
OFFERING = "---\nname: TURN\ntools: |\n  +pp-probe\n---\n"        # the base's TURN offers the script to its WORK
EXT = ("---\nname: EXT\nkind: doc\nconstraints.production: |\n  X1  the first matter holds\n---\n\n"
       "the mounted matter\n")
DEEP = ("---\nname: DEEP\nkind: doc\nconstraints.production: |\n  X2  the second matter holds\n---\n\n"
        "the deeper matter\n")
DUO = ("---\nname: DUO\nkind: proc\ndescription: a door of two steps under two scopes\nfusion: max\n"
       "constraints.behavior: |\n  D1  say it short\nproc: |\n  INFER\n  CALL INNER.md\n---\n\nsay one\n")
INNER = ("---\nname: INNER\nkind: proc\ndescription: a step under a law of its own\nfusion: max\n"
         "constraints.behavior: |\n  D2  say it plain\nproc: |\n  INFER\n---\n\nsay two\n")
DOORED = "---\nname: TURN\ntools: |\n  +pp-probe\n  +DUO\n---\n"       # the turn offers the script and the door
CONTRACT = "---\nname: pp-probe\ndescription: a witness script that mounts\n---\n\nthe probe's manual\n"
PROBE = ("def main(argv):\n"
         "    print('::mount ' + argv[0])\n"
         "    print('probe: derived')\n"
         "    return 0\n")
QUAD = ("---\nname: QUAD\nkind: proc\ndescription: four steps in a row\noutput: any\nfusion: max\nproc: |\n"
        "  INFER\n  INFER\n  INFER\n  INFER\n---\n\nsay four lines\n")
RANGE = re.compile(r"QUAD\{(\d+)(?:-(\d+))?/(\d+)\}")        # the pointer of the door's heading: a step, or a range
GATE = "---\nname: GATE\nkind: proc\ndescription: a door the turn offers\noutput: any\nproc: |\n  INFER\n---\n\nsay the gate\n"
GATED = "---\nname: TURN\ntools: |\n  +pp-probe\n  +GATE\n---\n"   # the turn offers the script and a door
BEGIN = ("---\nname: BEGIN\nkind: proc\ndescription: a contributor at the turn's beginning\nattach: turn.begin\n"
         "output: any\ntools: |\n  aside\nproc: |\n  INFER\n---\n\nsay one line before the work\n")   # an offer of its own
FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n"
STEP = re.compile(r"^(?:WORK|INFER|PICK)\b.* => \w+  \((\w+)\)$")   # a step's line: the document it ends on
SAID = "probe: derived"                                              # what the probe prints beside its directive
CUT = 3000                                                           # the cap the bare calls of case (n) name
STACKED = json.dumps([{"doc": "EXT.md", "body": True}])
BESIDE = json.dumps([{"doc": "DEEP.md", "body": True}])              # the second document, stacked like the first


def _blocks(events: list[dict]) -> tuple[int, int]:
    """-> (the blocks traced between the first mount and the last, the blocks traced after the last mount)."""
    mounted = [rank for rank, one in enumerate(events) if one.get("kind") == "mounted"]
    blocks = [rank for rank, one in enumerate(events) if one.get("kind") == "block"]
    if not mounted:
        return -1, -1
    return (len([one for one in blocks if mounted[0] < one < mounted[-1]]),
            len([one for one in blocks if one > mounted[-1]]))


def _laws(env, key: str) -> list[str]:
    """-> the codes in force on the step that stands, as the run's offer map keeps them."""
    last = (run.slot(env, key).get("segments") or [{}])[-1]
    return [str(one).split()[0] for one in last.get("constraints", [])]


def _served_by(events: list[dict]) -> list[str]:
    """-> the documents whose matter the mounts served, in the order the blocks' ledgers say them."""
    return [str(line.get("by")) for one in events if one.get("kind") == "block"
            for line in one.get("served") or [] if line.get("origin") == "mount" and line.get("state") == "served"]


def _holds(events: list[dict]) -> list[tuple]:
    """-> (act, open) of each `held` the trace says, in order."""
    return [(one.get("act"), one.get("open")) for one in events if one.get("kind") == "held"]


def _proved(events: list[dict]) -> list[set]:
    """-> the codes each proof the trace says was given names, in order."""
    return [{str(verdict.get("code")) for verdict in json.loads(one.get("given") or "[]")}
            for one in events if one.get("kind") == "answer" and str(one.get("instruction", "")).startswith("PROVE")]


def context_first(bench) -> None:
    """(j) (k) (l): what the principal mounts for an exchange is rendered before the steps of that exchange."""
    held, failures = bench.held, bench.failures
    env = bench.env("open-context", ("wit",))
    env.write("procs/TURN.md", OFFERING)
    env.write("procs/BEGIN.md", BEGIN)                # a step of the exchange before its WORK
    env.write("SETTINGS.md", FUSED)                   # the steps of an exchange in one output
    env.write("EXT.md", EXT)
    env.write("DEEP.md", DEEP)
    env.write("skills/pp-probe/SKILL.md", CONTRACT)
    env.write("skills/pp-probe/pp-probe.py", PROBE)

    def call(key: str, *words, variables=None, stdin=None):
        """The agent's call on `key` unless `variables` names the principal's (`{}` or the flag)."""
        return cli(env.engine, key, *words, cwd=env.root, stdin=stdin,
                   env=run.agent(key) if variables is None else variables)

    def posed(key: str, since: int) -> bool:
        """Whether NOTHING is rendered since: an output held open without a segment, no block traced."""
        hold = run.slot(env, key).get("held") or {}
        return (hold.get("open") is True
                and not [one for one in run.trace(env, key)[since:] if one.get("kind") == "block"])

    def mounted(key: str, since: int) -> list[bool]:
        """Two documents mounted under the flag -> what stands after each: mounted, nothing rendered."""
        stood = []
        for spec in (STACKED, BESIDE):
            played = call(key, "-s", "pp-probe", spec, variables=HOLD)
            stood.append(played.returncode == 0 and posed(key, since))
        docs = [one.get("doc") for one in run.slot(env, key).get("mounted", [])]
        return stood + [docs[-2:] == ["EXT.md", "DEEP.md"]]

    def read(text: str, key: str, steps: list[str]) -> dict:
        """What the released output says: the readings before the first step, the laws in the block of
        that step, one line per step, nothing of the script's own text."""
        shown = titles(text)
        readings = [titled(language.INFORMATION, name) for name in ("EXT", "DEEP")]
        asked = titled(language.INSTRUCTION)
        first = (run.slot(env, key).get("segments") or [{}])[0]
        return {"context first": (all(one in shown for one in readings) and asked in shown
                                  and max(shown.index(one) for one in readings) < shown.index(asked)),
                "laws": {"X1", "X2"} <= {str(one).split()[0] for one in first.get("constraints", [])},
                "lines": [found.group(1) for line in text.splitlines() if (found := STEP.match(line))] == steps,
                "no script text": SAID not in text}

    # --- (j) an opening ------------------------------------------------------------------------------------
    key, opened = run.opened(env, None, {context.HOLD: "true"}, "hello")
    opening = [bool(key) and opened.returncode == 0 and posed(key, 0)] + mounted(key, 0)
    released = call(key, variables={})
    said = read(released.stdout, key, ["BEGIN", "TURN"])
    if all(opening) and released.returncode == 0 and all(said.values()):
        held("(j) the context stands before the steps at an opening", f"run {key}: the opening prints its key "
             "and renders nothing, nor do the two mounts; the bare call renders BEGIN's step then the WORK, once "
             "each, behind the readings of both mounts, X1 and X2 in the block of the first step")
    else:
        failures.append(f"  ✗ (j) the context at an opening  posed={opening} rc={released.returncode} {said} "
                        f"{titles(released.stdout)}")

    # --- (k) the resume of a parked run --------------------------------------------------------------------
    asked = run.say_due(env, key)                             # BEGIN's line and the WORK handed: the proof asked
    call(key, "-", stdin=run.proof_of(asked))
    call(key, variables={})                          # the passage over: the run parked
    since = len(run.trace(env, key))
    message = call(key, "again", variables=HOLD)
    resuming = [message.returncode == 0 and posed(key, since)] + mounted(key, since)
    released = call(key, variables={})
    said = read(released.stdout, key, ["BEGIN", "TURN"])
    if all(resuming) and released.returncode == 0 and all(said.values()):
        held("(k) the context stands before the steps at a resume", "the message opens the exchange of the "
             "parked run and renders nothing, nor do the two mounts; the bare call renders BEGIN's step then the "
             "WORK, once each, behind the readings of both mounts, X1 and X2 in the block of the first step")
    else:
        failures.append(f"  ✗ (k) the context at a resume    posed={resuming} rc={released.returncode} {said} "
                        f"{titles(released.stdout)}")

    # --- (l) a run that stands on its WORK -----------------------------------------------------------------
    twin, _ = run.opened(env, None, None, "hello")   # served at once: the WORK stands, owed by the agent
    since = len(run.trace(env, twin))
    offered = list((run.slot(env, twin).get("segments") or [{}])[-1].get("tools", []))
    standing = mounted(twin, since)
    kept = list((run.slot(env, twin).get("segments") or [{}])[-1].get("tools", []))
    released = call(twin, variables={})
    said = read(released.stdout, twin, ["BEGIN", "TURN"])  # BEGIN's line, still due, said again
    if (all(standing) and released.returncode == 0 and all(said.values())
            and "aside" in offered and "pp-probe" in offered and kept[:len(offered)] == offered):
        held("(l) the context stands before the step of a standing run", f"run {twin}: the two mounts render "
             "nothing and leave the entry of the standing segment its offers -- BEGIN's own among them, in "
             "their order; the bare call renders the WORK that stands once, behind the readings of both "
             "mounts and the line of BEGIN's step still due, X1 and X2 in its block")
    else:
        failures.append(f"  ✗ (l) the context on a standing run posed={standing} rc={released.returncode} {said} "
                        f"offered={offered} kept={kept} {titles(released.stdout)}")

    # --- (m) an exchange left open by a mount refused, taken up ---------------------------------------------
    left, opened = run.opened(env, None, {context.HOLD: "true"}, "hello")
    first = call(left, "-s", "pp-probe", STACKED, variables=HOLD)
    refused = call(left, "-s", "pp-probe", json.dumps([{"doc": "NOWHERE.md"}]), variables=HOLD)
    stays = posed(left, 0)
    waited = len((run.slot(env, left).get("held") or {}).get("payloads", []))
    again = call(left, "once more", variables=HOLD)
    twice = call(left, "-s", "pp-probe", STACKED, variables=HOLD)
    same = len((run.slot(env, left).get("held") or {}).get("payloads", []))
    second = call(left, "-s", "pp-probe", BESIDE, variables=HOLD)
    taken = posed(left, 0)
    released = call(left, variables={})
    said = read(released.stdout, left, ["BEGIN", "TURN"])
    if (first.returncode == 0 and refused.returncode != 0 and stays and again.returncode == 0
            and run.key_of(again.stdout) == left and twice.returncode == 0 and same == waited
            and second.returncode == 0 and taken and released.returncode == 0 and all(said.values())
            and [one.get("kind") for one in run.trace(env, left)].count("prompt") == 1):
        held("(m) an exchange left open is taken up once", f"run {left}: a mount refused renders nothing and "
             "leaves the output open; a second message opens nothing more -- one `prompt` at the trace --, the "
             "mount the view holds serves nothing more, the other is posed; the bare call renders BEGIN's step "
             "then the WORK, once each, behind the readings of both mounts")
    else:
        failures.append(f"  ✗ (m) an exchange left open     rc={first.returncode}/{refused.returncode}/"
                        f"{again.returncode}/{twice.returncode}/{second.returncode}/{released.returncode} "
                        f"stays={stays} payloads={waited}/{same} taken={taken} {said} {titles(released.stdout)}")

    # --- (q) a door the root offers, named under the flag before the bare call, is refused -------------------
    env.write("procs/GATE.md", GATE)
    env.write("procs/TURN.md", GATED)

    def stacked(key: str) -> list[str]:
        """-> the documents of the run's frames, by their file's name."""
        return [str(one.get("document", "")).rsplit("/", 1)[-1] for one in run.slot(env, key).get("frames") or []]

    def refused(key: str, since: int) -> list[bool]:
        """A door and a space named on an exchange that is not played -> each call refused, nothing stacked,
        nothing rendered: bare under the flag, `-open`, addressed to each segment the last output's map
        counts (the first when it counts none), and bare without the flag."""
        owners = [one.get("ordinal") for one in run.slot(env, key).get("segments") or []] or [1]
        calls = ([("-s", "GATE"), ("-open", "GATE")] + [("-s", f"GATE@{one}") for one in owners]
                 + [("-open", f"GATE@{owners[-1]}")])
        played = [call(key, *words, variables=HOLD) for words in calls]
        played.append(call(key, "-s", "GATE", variables={}))
        return [one.returncode == 2 for one in played] + [posed(key, since), "GATE.md" not in stacked(key)]

    gated, _ = run.opened(env, None, {context.HOLD: "true"}, "hello")
    at_opening = refused(gated, 0)
    call(gated, "-s", "pp-probe", STACKED, variables=HOLD)
    released = call(gated, variables={})
    first = [found.group(1) for line in released.stdout.splitlines() if (found := STEP.match(line))]
    asked = run.say_due(env, gated)                           # BEGIN's line and the WORK handed: the proof asked
    call(gated, "-", stdin=run.proof_of(asked))
    call(gated, variables={})                        # the passage over: the run parked
    since = len(run.trace(env, gated))
    call(gated, "again", variables=HOLD)
    mapped = [one.get("ordinal") for one in run.slot(env, gated).get("segments") or []
              if "GATE" in (one.get("tools") or [])]
    at_resume = refused(gated, since)
    released = call(gated, variables={})
    second = [found.group(1) for line in released.stdout.splitlines() if (found := STEP.match(line))]
    doors = [one.get("kind") for one in run.trace(env, gated) if one.get("kind") in ("routed", "door-argument")]
    if (all(at_opening) and all(at_resume) and mapped and first == ["BEGIN", "TURN"] and second == ["BEGIN", "TURN"]
            and not doors and "GATE.md" not in stacked(gated)):
        held("(q) a door or a space named before the exchange is played is refused", f"run {gated}: GATE, offered "
             f"by the turn, named at the opening and at the resume of the parked run -- by `-s`, by `-open`, "
             f"addressed to a segment of the last output (it offers GATE at {mapped} at the resume), under the "
             f"flag and without it: rc 2 each ({len(at_opening) - 2} and {len(at_resume) - 2} calls), nothing "
             "stacked, no block traced, the output still open; each bare call renders BEGIN's step then the "
             "WORK, once each, no step of the door")
    else:
        failures.append(f"  ✗ (q) a door before the play    opening={at_opening} resume={at_resume} mapped={mapped} "
                        f"lines={first}/{second} doors={doors} frames={stacked(gated)}")
    env.write("procs/TURN.md", OFFERING)

    # --- (n) the release cut under a cap ---------------------------------------------------------------------
    capped = {context.PROMPT_CAP: str(CUT)}
    cut, _ = run.opened(env, None, {context.HOLD: "true"}, "hello")
    posed_n = mounted(cut, 0)
    chunks = [call(cut, variables=capped).stdout]
    while (run.slot(env, cut).get("pending") or {}) and len(chunks) < 200:
        chunks.append(call(cut, variables=capped).stdout)
    whole = "\n".join(chunks)
    lines = [found.group(1) for line in whole.splitlines()
             if (found := STEP.match(line)) and f" {language.EMPTY} " not in line]
    shown = titles(whole)
    readings = [titled(language.INFORMATION, name) for name in ("EXT", "DEEP")]
    asked = [rank for rank, line in enumerate(whole.splitlines())
             if STEP.match(line) and f" {language.EMPTY} " not in line]
    before = [rank for rank, line in enumerate(whole.splitlines()) if line in readings]
    if (all(posed_n) and len(chunks) > 1 and all(len(one) <= CUT for one in chunks)
            and lines == ["BEGIN", "TURN"] and all(one in shown for one in readings)
            and before and asked and max(before) < asked[0]
            and "cut" in run.kinds(env, cut) and run.kinds(env, cut).count("chunk") == len(chunks) - 1):
        held("(n) the release is cut under the cap", f"run {cut}: {len(chunks)} bare calls under {CUT} characters "
             "serve the exchange -- the first chunk, then the rest --, the readings of both mounts before the "
             "first step's line, BEGIN's step and the WORK once each over the chunks")
    else:
        failures.append(f"  ✗ (n) the release under a cap   posed={posed_n} chunks={len(chunks)} "
                        f"sizes={sorted({len(one) for one in chunks})[-2:]} lines={lines} "
                        f"before={before[-1:]} asked={asked[:1]} kinds={run.kinds(env, cut)[-6:]}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("open-output", ("wit",))
    env.write("procs/TURN.md", OFFERING)
    env.write("EXT.md", EXT)
    env.write("DEEP.md", DEEP)
    env.write("skills/pp-probe/SKILL.md", CONTRACT)
    env.write("skills/pp-probe/pp-probe.py", PROBE)

    def call(key: str, *words, variables=None, stdin=None):
        """The agent's call on `key` unless `variables` names the principal's (`{}` or the flag)."""
        return cli(env.engine, key, *words, cwd=env.root, stdin=stdin,
                   env=run.agent(key) if variables is None else variables)

    # --- (a) the opening held open ------------------------------------------------------------------------
    key, opened = run.opened(env, None, {context.HOLD: "true"}, "hello")
    hold = run.slot(env, key).get("held") or {}
    blocks_a = [one for one in run.trace(env, key) if one.get("kind") == "block"]
    if (key and opened.returncode == 0 and _holds(run.trace(env, key)) == [("value", True)]
            and opened.stdout.strip().splitlines()[-1:] == [messages.opened("opened")]
            and hold.get("open") is True and not hold.get("matter")
            and not [one for one in blocks_a if one.get("command")]):
        held("(a) the opening is held open", f"run {key}: the trace says `held`, act value, open; the slot holds "
             "the output open, no block of the step that stands is traced; the call says the exchange opened and "
             "that the bare call plays it")
    else:
        failures.append(f"  ✗ (a) the opening held open     rc={opened.returncode} holds={_holds(run.trace(env, key))} "
                        f"hold={sorted(hold)} blocks={[one.get('command') for one in blocks_a]}")

    # --- (b) two mounts join it ---------------------------------------------------------------------------
    first = call(key, "-s", "pp-probe", STACKED, variables=HOLD)
    second = call(key, "-s", "pp-probe", BESIDE, variables=HOLD)
    hold = run.slot(env, key).get("held") or {}
    docs = [one.get("doc") for one in run.slot(env, key).get("mounted", [])]
    events = run.trace(env, key)
    if (first.returncode == 0 and second.returncode == 0
            and _holds(events) == [("value", True), ("mount", True), ("mount", True)]
            and docs[-2:] == ["EXT.md", "DEEP.md"] and hold.get("open") is True
            and len(hold.get("payloads", [])) >= 2
            and _blocks(events) == (0, 0)):
        held("(b) the mounts are posed on the open output", "two documents, one after the other: the trace says "
             "`held`, act mount, open, at each; both mounted, their matter kept with the hold, no block rendered")
    else:
        failures.append(f"  ✗ (b) the mounts join           rc={first.returncode}/{second.returncode} "
                        f"holds={_holds(events)} docs={docs} hold={sorted(hold)} blocks={_blocks(events)}")

    # --- (c) the release: one output, the block that stands once ------------------------------------------
    released = call(key, variables={})
    events = run.trace(env, key)
    advanced = [one for one in events if one.get("kind") == "advance" and one.get("held") is True]
    laws, served = _laws(env, key), _served_by(events)
    ordinals = [one.get("ordinal") for one in run.slot(env, key).get("segments") or []]
    asked = run.say_due(env, key)                             # the WORK handed by its print call: the proof asked
    owed = _laws(env, key)
    proved = call(key, "-", stdin=run.proof_of(asked))
    parked = call(key, variables={})
    kinds = run.kinds(env, key)
    wanted = (_proved(run.trace(env, key)) or [set()])[-1]
    if (released.returncode == 0 and ordinals == [1]
            and _holds(events) == [("value", True), ("mount", True), ("mount", True)]
            and _blocks(events) == (0, 1) and len(advanced) == 1 and not run.slot(env, key).get("held")
            and {"X1", "X2"} <= set(laws) and "EXT.md" in served and "DEEP.md" in served
            and served.index("EXT.md") < served.index("DEEP.md")
            and {"X1", "X2"} <= set(owed) and {"X1", "X2"} <= wanted
            and proved.returncode == 0 and parked.returncode == 0
            and not [one for one in kinds if one.startswith("repair")]
            and (run.slot(env, key).get("frames") or [{}])[-1].get("document", "").endswith("TURN.md")):
        held("(c) the release renders one output", "one segment in the offer map, one block after "
             "the last mount, X1 and X2 in force on the step that stands, the first mount's matter before the "
             f"second's, the hold gone; the proof given next names {sorted(wanted)}, once, nothing repaired")
    else:
        failures.append(f"  ✗ (c) the release               rc={released.returncode} blocks={_blocks(events)} "
                        f"ordinals={ordinals} advanced={len(advanced)} laws={laws} owed={owed} served={served} "
                        f"wanted={sorted(wanted)} kinds={kinds[-8:]}")

    # --- (d) the same calls without the flag: the block at each mount --------------------------------------
    twin, _ = run.opened(env, None, None, "hello")
    call(twin, "-s", "pp-probe", STACKED, variables={})
    call(twin, "-s", "pp-probe", BESIDE, variables={})
    if twin and _blocks(run.trace(env, twin)) == (1, 1) and not run.slot(env, twin).get("held"):
        held("(d) without the flag, the block at each mount", f"run {twin}: the same principal's calls render the "
             "block that stands after each mount, nothing held")
    else:
        failures.append(f"  ✗ (d) without the flag          key={twin!r} blocks={_blocks(run.trace(env, twin))}")

    # --- (e) a message under the flag at the parked run ----------------------------------------------------
    before = len(run.trace(env, key))
    message = call(key, "again", variables=HOLD)
    mount = call(key, "-s", "pp-probe", STACKED, variables=HOLD)
    again = call(key, variables={})
    window = run.trace(env, key)[before:]
    asked = run.say_due(env, key)                             # the WORK handed by its print call: the proof asked
    owed = _laws(env, key)
    call(key, "-", stdin=run.proof_of(asked))
    call(key, variables={})
    kinds = [one.get("kind", "") for one in run.trace(env, key)[before:]]
    wanted = (_proved(run.trace(env, key)[before:]) or [set()])[-1]
    if (message.returncode == 0 and _holds(window) == [("value", True), ("mount", True)] and "X1" in owed
            and mount.returncode == 0 and again.returncode == 0
            and len([one for one in window if one.get("kind") == "block" and one.get("command")]) == 1
            and _blocks(window) == (0, 1) and wanted == {"X1"}
            and not [one for one in kinds if one.startswith("repair")] and kinds.count("prompt") == 1):
        held("(e) a message held open at a resume", "the message opens the exchange, the mount is posed, the "
             "release renders the step that stands once with X1 in force; the proof names X1, nothing repaired")
    else:
        failures.append(f"  ✗ (e) the resume                rc={message.returncode}/{mount.returncode}/{again.returncode} "
                        f"holds={_holds(window)} blocks={_blocks(window)} owed={owed} wanted={sorted(wanted)} "
                        f"kinds={kinds}")

    # --- (g) an output that closed already waits: a message held open joins it, never overwrites it ----------
    kept, _ = run.opened(env, None, None, "hello")
    call(kept, "-mount", STACKED)                          # the agent's mount: held, as any output
    call(kept, variables={})
    asked = run.say_due(env, kept)                            # the productions said: the proof of X1 asked
    call(kept, "-", stdin=run.proof_of(asked))      # the agent's value: its output held, the run parked
    waiting = run.slot(env, kept).get("held") or {}
    before = len(run.trace(env, kept))
    message = call(kept, "again", variables=HOLD)
    stays = run.slot(env, kept).get("held") or {}
    window = run.trace(env, kept)[before:]
    served = call(kept, variables={})
    if (waiting and not waiting.get("open") and stays == waiting
            and message.returncode == 0 and run.key_of(message.stdout) == kept and not window
            and message.stdout.strip().splitlines()[-1:] == [messages.opened("waiting")]
            and served.returncode == 0 and not run.slot(env, kept).get("held")):
        held("(g) a closed output waiting is left as it is", f"run {kept}: the agent's value left an output "
             "held; a message under the flag prints the run's key and says an output waits, for the bare call -- "
             "never that it is held open --, and changes nothing: the slot's held output "
             "as it was, nothing open, nothing traced; the principal's bare call serves it")
    else:
        failures.append(f"  ✗ (g) a closed output waiting   waiting={sorted(waiting)} same={stays == waiting} "
                        f"rc={message.returncode}/{served.returncode} kinds={[one.get('kind') for one in window]}")

    # --- (h) a release whose assembly fails leaves the open output at the run ------------------------------
    lost, _ = run.opened(env, None, {context.HOLD: "true"}, "hello")
    call(lost, "-s", "pp-probe", STACKED, variables=HOLD)
    path = persistence.slot_of(env.made, lost)
    whole = run.slot(env, lost)
    waited = list((whole.get("held") or {}).get("payloads", []))
    if whole.get("held"):                                  # a reading no output can be assembled from
        path.write_text(json.dumps({**whole, "held": {**whole["held"], "payloads": waited + [[0]]}}), encoding="utf-8")
    failed = call(lost, variables={})
    after = run.slot(env, lost)
    stays = after.get("held") or {}
    if stays:                                              # the damage undone: the output as the calls left it
        path.write_text(json.dumps({**after, "held": {**stays, "payloads": waited}}), encoding="utf-8")
    served = call(lost, variables={})
    events = run.trace(env, lost)
    advanced = [one for one in events if one.get("kind") == "advance" and one.get("held") is True]
    if (lost and failed.returncode != 0 and stays.get("open") is True
            and len(stays.get("payloads", [])) == len(waited) + 1
            and served.returncode == 0 and not run.slot(env, lost).get("held")
            and _blocks(events) == (0, 1) and len(advanced) == 1 and "X1" in _laws(env, lost)):
        held("(h) a release that fails keeps the open output", f"run {lost}: the bare call fails at the release "
             "-- the output still waits open at the slot, nothing traced as served; the damage undone, the next "
             "bare call serves it whole, one block after the mount, X1 in force")
    else:
        failures.append(f"  ✗ (h) a release that fails      rc={failed.returncode}/{served.returncode} "
                        f"stays={sorted(stays)} blocks={_blocks(events)} advanced={len(advanced)} "
                        f"held={sorted(run.slot(env, lost).get('held') or {})} {failed.stderr[-200:]!r}")

    # --- (o) a closed output waits, two segments offer the script: the bare name mounts under the flag ------
    env.write("procs/DUO.md", DUO)
    env.write("procs/INNER.md", INNER)
    env.write("procs/TURN.md", DOORED)
    shut, _ = run.opened(env, None, None, "hello")
    call(shut, "-s", "DUO")                                # the agent's door: its two segments held
    waiting = run.slot(env, shut).get("held") or {}
    owners = [one.get("ordinal") for one in run.slot(env, shut).get("segments") or []
              if "pp-probe" in (one.get("tools") or [])]
    bare = call(shut, "-s", "pp-probe", STACKED, variables=HOLD)
    joined = run.slot(env, shut).get("held") or {}
    docs = [one.get("doc") for one in run.slot(env, shut).get("mounted", [])]
    served = call(shut, variables={})
    asked = [found.group(1) for line in served.stdout.splitlines() if (found := STEP.match(line))]
    if (waiting and not waiting.get("open") and len(owners) > 1 and bare.returncode == 0
            and joined and not joined.get("open") and "EXT.md" in docs
            and served.returncode == 0 and asked == ["DUO", "INNER"]
            and titled(language.INFORMATION, "EXT") in titles(served.stdout)
            and "X1" in _laws(env, shut) and not run.slot(env, shut).get("held")):
        held("(o) the bare name mounts over a closed output", f"run {shut}: the agent's door waits, closed, "
             f"segments {owners} offering the script; under the flag the bare name mounts EXT, its view joins "
             "the output that waits; the bare call serves one output, the door's two steps once each, X1 in force")
    else:
        failures.append(f"  ✗ (o) the bare name, closed     waiting={sorted(waiting)} owners={owners} "
                        f"rc={bare.returncode}/{served.returncode} docs={docs} asked={asked} "
                        f"{bare.stderr[-200:]!r}")
    env.write("procs/TURN.md", OFFERING)

    # --- (i) the segment an open output keeps is released under the range of its steps ----------------------
    env.write("procs/QUAD.md", QUAD)
    env.write("procs/TURN.md", "---\nname: TURN\ntools: |\n  +pp-probe\n  +QUAD\n---\n")
    ranged, _ = run.opened(env, "QUAD.md", {context.HOLD: "true"}, "hello")
    released = call(ranged, variables={})
    twin, shown = run.opened(env, "QUAD.md", None, "hello")
    unheld = call(twin, variables={}) if not RANGE.search(shown.stdout) else shown
    pointers = [RANGE.search(text) for text in (released.stdout, unheld.stdout)]
    if (released.returncode == 0 and all(pointers)
            and [one.groups() for one in pointers] == [("1", "4", "4")] * 2):
        held("(i) the release renders a door's steps under their range", f"run {ranged}: the release renders the "
             "door's four fused steps under `QUAD{1-4/4}`, as the unheld run renders them")
    else:
        failures.append(f"  ✗ (i) the range at the release  rc={released.returncode} "
                        f"pointers={[one and one.group(0) for one in pointers]}")
    context_first(bench)
    return 0
