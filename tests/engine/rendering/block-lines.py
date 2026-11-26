"""Scenario `block-lines` -- the shape of a rendered output, on one house:
- the weld: every section opens on a blank line; the tool's channel never fuses; the packages'
  state line sits under the output's heading, one cell per package
- the order: the sections of a segment follow the engine's list -- the block's sections once, a
  reading a later step brings among them, then one group per step: its context, its OPTIONS, its
  line; a DEVIATION and a DIAGNOSTIC take their rank among the block's
- the heading's hour: once per output, a later output a later hour, the keyless console too
- the closings stand bare; after a judged proof the AWAIT
  stands bare too, no look-ahead; the engine adds no line behind the proof: the last step keeps
  `terminal`, its print handed before the run moves
- a view cut under the cap says so by ONE fact line at its foot
- every instruction line ends on the name of its document in parentheses
- the form of each category of the engine's messages, read at its one function (`core.messages`): the
  frame's marks; a refusal and the line under it, both in pp's voice; a deviation that says the fact and
  the call that mends it, in pp's voice, the second person, no capitals of insistence, no rule of the
  standing orders said again; an acknowledgement, a console's state, `<said> — <what is due now>`; a
  fact `(pp: <fact>)`; a complement alone; a diagnostic `<code> · <level> · <fact> — <way>`; a
  maintenance line and its warning -- one separator, `—`, nowhere `--`; a deviation rendered on a
  disposable run under its section in that form; a malformed call of the console refused by name,
  exit 2
"""
from __future__ import annotations

import json
import re
from dataclasses import replace
from datetime import timedelta

from conductor import persistence, render, rendering, settings
from conductor.core import language, messages
from conductor.execution import blocks
from tests.harness import cli, stepped, titled, titles

LAWFUL = ("---\nname: LAWFUL\nkind: doc\ndescription: a law mounted at the boot\n"
          "mount: boot.initialize\nconstraints.behavior: |\n  W1  the witness law sits next to the ask.\n---\n")
SWITCHES = (("alpha", ""), ("beta", "alpha"), ("gamma", "gamma"))

MARK = re.compile(r" · (\d\d):(\d\d):(\d\d) · \+(\d+):(\d\d):(\d\d)$")

CLOSED = "---\nname: CLOSED\nkind: proc\ndescription: a witness\nproc: |\n  WORK\n  WORK\n---\nwork\n"
PROVEN = ("---\nname: PROVEN\nkind: proc\ndescription: a witness under a law\n"
          "constraints.production: |\n  Z1  say it plainly\nproc: |\n  INFER\n  PROVE\n---\nsay\n")

KEY = re.compile(r"run ([0-9a-f]{6})")
OVERLAY = "---\nname: TURN\ntools: |\n  +SIDE\n---\n"
SIDE = ("---\nname: SIDE\nkind: proc\ndescription: a side door\noutput: any\n"
        "constraints.production: |\n  S1  say it plainly.\nproc: |\n  INFER\n---\n\nthe side door's brief\n")
NAMED = re.compile(r"^(WORK|INFER|PICK)\b.*\((\w+)\)$")
# the witness of the order: a root that calls STEPPED -- two readings, the second served between its
# two steps, an offer, a law, then the fork its `next:` injects, a choice with its own brief
STEPS = {
    "WAY.md": "---\nname: WAY\nkind: proc\ndescription: the root of the witness\nproc: |\n"
              "  CALL STEPPED.md\n  INFER\n---\n\nthe way's brief\n",
    "STEPPED.md": "---\nname: STEPPED\nkind: proc\ndescription: two steps, then a fork\n"
                  "tools: |\n  SIDE\nconstraints.behavior: |\n  O1  the witness law of the steps.\n"
                  "next: LEFT.md RIGHT.md\nchoose: |\n  either way.\nfusion: max\n"
                  "proc: |\n  SERVE FIRST.md\n  INFER\n  SERVE SECOND.md\n  INFER\n---\n\nthe steps' brief\n",
    "FIRST.md": "---\nname: FIRST\nkind: doc\n---\n\nthe first reading\n",
    "SECOND.md": "---\nname: SECOND\nkind: doc\n---\n\nthe second reading\n",
    "LEFT.md": "---\nname: LEFT\nkind: proc\ndescription: one way\nproc: |\n  INFER\n---\n\nleft\n",
    "RIGHT.md": "---\nname: RIGHT\nkind: proc\ndescription: the other way\nproc: |\n  INFER\n---\n\nright\n",
}
MISS, FAULT = "a miss", "a fault"

def _cell(name: str, cause: str) -> str:
    """-> the state a switch says of its package: on, off, or off with its cause."""
    if not cause:
        return f"{name} on"
    return f"{name} off" if cause == name else f"{name} off (<- {cause})"


def _cells(line: str) -> list[str]:
    """-> the cells of a packages' state line, its mark dropped."""
    return line.removeprefix(f"{messages.MARK} ").split(" · ")


def _sections(text: str) -> list[tuple[str, str]]:
    """-> the marked lines of a rendering in order, each read by the engine's list: (section, subject),
    a heading reading no section."""
    mark = f"{messages.MARK} "
    return [language.section_of(line.removeprefix(mark)) for line in text.splitlines() if line.startswith(mark)]


def _listed(carried: dict[str, int], steps: tuple[set[str], ...]) -> list[str]:
    """-> the sections of ONE segment as the engine's list orders them: the block's, each as many
    times as the segment carries it, then one group per step, in the order of the steps."""
    return ([name for name in language.BLOCK_SECTIONS for _ in range(carried.get(name, 0))]
            + [name for step in steps for name in language.STEP_SECTIONS if name in step])


def _marks(text: str) -> list[re.Match]:
    return [m for line in text.splitlines() if (m := MARK.search(line))]


def _closing(text: str) -> list[str]:
    lines = text.splitlines()
    at = max((i for i, one in enumerate(lines) if one.startswith("▶ ")), default=len(lines))
    return lines[at:]


def weld(bench, env) -> None:
    """The weld of the sections, the tool's channel, the packages' line."""
    held, failures = bench.held, bench.failures
    conductor = env.conductor()
    booted = render(conductor.resume(conductor.boot("BOOT.md")))
    marked = [one for one in booted.splitlines()
              if one.startswith((messages.MARK, messages.SIGNAL))]
    glued = marked[1:]        # the output's FIRST line has nothing above it to part from
    seams = [f"\n\n{one}" in booted for one in glued]
    if glued and all(seams):
        held("every section opens on a blank line",
             f"{len(glued)} marked lines, none welded to what stands above -- the "
             "INSTRUCTION and the closing come through the same weld as the rest")
    else:
        missing = [one for one, ok in zip(glued, seams) if not ok]
        failures.append(f"  ✗ la soudure                  {missing[:3]!r}")

    to_tool = {one for one in language.YIELDING if one not in language.FREE}
    if (to_tool == {"PICK", "PROVE", "FIELD", "NEXT"} and "INFER" in language.FREE
            and "WORK" in language.FREE):
        held("the tool's channel never fuses",
             "the fusion takes FREE productions alone, and a channel reads `tool` for a "
             "PICK, a checkpoint, a described door's field, a leaving document's successor "
             "or a CONSUMED production -- "
             "exactly what it refuses to fuse: the closing's command always answers the "
             "LAST step rendered")
    else:
        failures.append(f"  ✗ le canal tool               {sorted(to_tool)!r}")

    cells = rendering.packages(SWITCHES)
    switched = replace(conductor.resume(conductor.boot("BOOT.md")), switches=SWITCHES[:2])
    lines = rendering.head(switched).splitlines()
    if (cells.startswith(f"{messages.MARK} ")
            and _cells(cells) == [_cell(*one) for one in SWITCHES]
            and rendering.packages(()) == ""
            and len(lines) == 2 and lines[0].startswith(f"{messages.MARK} pp · ")
            and lines[1].startswith(f"{messages.MARK} ")
            and _cells(lines[1]) == [_cell(*one) for one in SWITCHES[:2]]
            and f"{messages.MARK} pp · " not in lines[1]):
        held("the packages' state says itself",
             "one cell per package: `on` where it plays, `off` where a switch took it out, "
             "`off (<- <dependency>)` where its requirement did -- and the line sits UNDER the "
             "output's own heading, the two welded by a single newline: one heading, two lines; "
             "nothing to say, no line")
    else:
        failures.append(f"  ✗ l-etat-des-packages         {cells!r} {lines[-1:]!r}")


def order(bench, env) -> None:
    """The sections of a segment follow the engine's list, the block's first, then each step's."""
    held, failures = bench.held, bench.failures
    for name, text in STEPS.items():
        env.write(f"procs/{name}", text)
    env.write("procs/SIDE.md", SIDE)
    conductor = env.conductor()
    conductor.forget()
    block = conductor.start(conductor.boot("WAY.md"))
    read = _sections(render(block))
    missed = _sections(render(replace(block, deviation=MISS, diagnostics=(FAULT,))))
    # what the witness carries: its readings -- the last two its own, the second served between its
    # two steps --, an offer, the laws; a first step under its document's brief, a second with
    # nothing of its own, the fork under its `next` brief
    readings = [subject for name, subject in read if name == language.INFORMATION]
    carried = {language.INFORMATION: len(readings), language.TOOLS: 1, language.CONSTRAINTS: 1}
    steps = ({language.CONTEXT, language.INSTRUCTION}, set(),
             {language.CONTEXT, language.OPTIONS, language.INSTRUCTION})
    lines = [line.split()[0] for line in render(block).splitlines() if line.endswith("(STEPPED)")]
    if ([name for name, _ in read if name] == _listed(carried, steps)
            and [name for name, _ in missed if name]
            == _listed({**carried, language.DEVIATION: 1, language.DIAGNOSTIC: 1}, steps)
            and sum(1 for name, _ in read if not name) == 2
            and readings[-2:] == ["FIRST.md", "SECOND.md"]
            and [subject for name, subject in read if name == language.CONTEXT] == ["STEPPED", "next"]
            and lines == ["INFER", "INFER", "PICK"] and list(block.options) == ["LEFT.md", "RIGHT.md"]):
        held("the sections follow the engine's list",
             f"one segment, {len(read) - 2} sections: its {len(readings)} readings -- the last brought by "
             "the second step -- then the offer and the laws, then the first step under its brief, the "
             "second on the next line, the fork under its own brief and its OPTIONS; a DEVIATION and a "
             "DIAGNOSTIC stand behind the laws, before the first step")
    else:
        failures.append(f"  ✗ l'ordre des sections        {read!r} missed={missed!r} lines={lines!r}")


def clock(bench, env) -> None:
    """The heading's hour: read at the render, relative to the run's -new."""
    held, failures = bench.held, bench.failures
    real = blocks.clock
    conductor = env.conductor()
    frozen = {"after": timedelta(seconds=65)}
    blocks.clock = lambda: ((blocks._opened_at(conductor._log or "") or real()) + frozen["after"])
    try:
        text = render(conductor.resume(conductor.boot("BOOT.md")))
        opened = blocks._opened_at(conductor._log)
        first = text.splitlines()[0]
        marks = _marks(text)
        local = (opened + frozen["after"]).astimezone().strftime("%H:%M:%S")
        if (first.startswith("▌ pp · ") and len(marks) == 1 and MARK.search(first)
                and first.endswith(f" · {local} · +0:01:05")):
            held("the output's heading says the hour once", f"`{first[-24:]}` on the boot -- "
                 "the local hour and +0:01:05 since -new, the mark once")
        else:
            failures.append(f"  ✗ clock once                 {first!r} marks={len(marks)}")

        frozen["after"] = timedelta(hours=1, minutes=2, seconds=3)
        later = render(conductor.forward(""))
        later_first = later.splitlines()[0]
        peeked = conductor.peek()
        peek_text = render(peeked) if peeked else ""
        if (later_first.endswith(" · +1:02:03") and len(_marks(later)) == 1
                and peek_text.splitlines()[0].endswith(" · +1:02:03")):
            held("a later output says a later hour", "`+1:02:03` on the advance and on the peek")
        else:
            failures.append(f"  ✗ clock later                {later_first!r} {peek_text.splitlines()[:1]!r}")
    finally:
        blocks.clock = real

    shelf = env.cli()
    if shelf.returncode == 0 and len(_marks(shelf.stdout)) == 1:
        held("the keyless console shows the hour once", "it shows the pending block, the mark with it")
    else:
        failures.append(f"  ✗ keyless clock              rc={shelf.returncode} {shelf.stdout[:160]!r}")


def closing_notes(bench, env) -> None:
    """A run closes on a line where its passage is over, and nowhere else: AWAIT, no call under it, no
    note."""
    over = [f"{messages.SIGNAL} {language.AWAIT}"]
    held, failures = bench.held, bench.failures
    closed = env.write("CLOSED.md", CLOSED)
    proven = env.write("PROVEN.md", PROVEN)

    conductor = env.conductor()
    first = conductor.start(closed)
    key = conductor.run_id
    stepped(lambda: env.conductor(key))            # the first WORK printed: the second pending, its closing bare
    final = stepped(lambda: env.conductor(key))    # the second printed: the frontier comes
    work_tail, final_tail = _closing(render(first)), _closing(render(final))
    if work_tail == [] and final_tail == over:
        held("the principal's outputs close where the passage is over", "the pending WORK ends on its last "
             "section; the end of the passage closes on AWAIT with no call under it -- nothing tells the agent "
             "who calls next")
    else:
        failures.append(f"  ✗ bare closings                {work_tail} {final_tail}")

    env.conductor(key).forget()
    conductor = env.conductor()
    opened = conductor.start(proven)
    key = conductor.run_id
    before = _closing(render(opened))
    proving = stepped(lambda: env.conductor(key))               # the INFER printed: the proof block
    state = json.loads(persistence.slot_of(env.made, key).read_text(encoding="utf-8"))
    awaited = persistence.awaits_of(state)                      # read while the proof is due
    mapped = (persistence.segments_of(persistence.slot_of(env.made, key)) or [{}])[-1].get("at")
    judged = env.conductor(key).submit(json.dumps([{"code": "Z1", "evidence": "a line", "verdict": "ok"}]))
    tail = _closing(render(judged))
    # the INFER stays pending until the principal's call: no closing line; the written PROVE
    # asks its proof; the end of the passage after it closes on AWAIT, no call under it
    if (before == [] and proving.output == "proof" and tail == over):
        held("the end after a written proof closes on AWAIT", "no closing on the INFER, the PROVE asked, "
             "AWAIT with no call at the end")
    else:
        failures.append(f"  ✗ bare after proof             before={before} tail={tail}")

    # the engine ADDS no line behind the proof: the proof's line stands alone under the ONE INSTRUCTION
    # title, the text the block's as it stands -- the heading's count, the offers and the laws --, and the
    # judged proof found the stack awaiting its value at the position the offer map holds
    added = rendering.last_line("PROVEN")
    text, plain = render(proving), render(replace(proving, response=""))
    asked = text.split(f"{titled(language.INSTRUCTION)}\n")[-1].splitlines()
    if (not proving.response and titles(text).count(titled(language.INSTRUCTION)) == 1
            and len(asked) == 1 and asked[0].startswith("INFER proof [Z1]")
            and text == plain and added not in text
            and (proving.position, proving.total) == (2, 2) and awaited == persistence.PRODUCTION
            and mapped == proving.position
            and judged.wait and not judged.response and added not in render(judged)):
        held("no line is added behind the proof", f"`{added}` stands nowhere: the proof's line alone under the "
             "one INSTRUCTION title -- PROVEN{2/2}, its offers and its laws --, the stack awaited the proof at "
             "the position the offer map holds, and the end of the passage carries no line either")
    else:
        failures.append(f"  ✗ the added line              response={proving.response!r} asked={asked} "
                        f"at={proving.position}/{proving.total} awaited={awaited!r} mapped={mapped!r} "
                        f"same={text == plain}")


def view_fact(bench, env) -> None:
    """A view over the cap is clipped, and the clip is said by a fact at the foot."""
    held, failures = bench.held, bench.failures
    env.write("LONG.md", "---\nname: LONG\nkind: doc\n---\n\n" + "a long line of matter\n" * 12000 + "\n")
    # past the principal's floor: the view is clipped under the cap
    viewrun = env.write("VIEWRUN.md", "---\nname: VIEWRUN\nkind: proc\ndescription: a witness\nproc: |\n"
                                      "  SERVE LONG.md\n  WORK\n---\nread\n")
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmax_harness_tool_output: 2000\n---\n")
    conductor = env.conductor()
    conductor.forget()
    view = conductor.shown(conductor.start(viewrun))
    feet = [one for one in view.splitlines() if one.startswith("   (")]
    shape = [re.sub(r"\d+", "N", one) for one in feet]
    if (len(feet) == 1 and len(view) <= settings.PRINCIPAL_CAP
            and view.rstrip().splitlines()[-1] == feet[0] and "(this view" not in view):
        held("a cut view says so by one fact at its foot", f"`{shape[0].strip()}` closes the view, nothing in "
             "the body says it")
    else:
        failures.append(f"  ✗ the view's fact             {feet} size={len(view)}")


def instruction_names(bench, env) -> None:
    """Every instruction line of a fused output ends on the name of its document."""
    held, failures = bench.held, bench.failures
    env.write("procs/TURN.md", OVERLAY)
    env.write("procs/SIDE.md", SIDE)
    opened = cli(env.engine, "-new", "go", cwd=env.root)
    key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
    door = cli(env.engine, key, "-s", "SIDE", cwd=env.root)
    lines = [line for text in (opened.stdout, door.stdout) for line in text.splitlines()
             if line.startswith(("WORK ", "INFER ", "PICK ")) and "=>" in line]
    named = [NAMED.match(line) for line in lines]
    if (lines and all(named) and any(m.group(2) == "TURN" for m in named)
            and any(m.group(2) == "SIDE" for m in named)
            and any(f"INFER any => {language.TERMINAL}  (SIDE)" == line for line in lines)):
        held("every instruction line names its document", f"{len(lines)} lines, e.g. {lines[:3]}")
    else:
        failures.append(f"  ✗ the lines                   {lines}")


def print_lines(bench) -> None:
    """What pp answers a print call is read at the engine's messages: the three lines of
    `messages.PRINTED`, the first naming the call due, and the DEVIATION of a print that misses, which
    names each document due."""
    from conductor.core import messages                                         # noqa: PLC0415
    held, failures = bench.held, bench.failures
    said = {"more": messages.printed("more", messages.next_print("ALPHA")), "last": messages.printed("last"),
            "waived": messages.printed("waived")}
    lines = list(said.values())
    named = messages.prints_due(("ALPHA", "BRAVO", "ALPHA"))
    if (sorted(said) == ["last", "more", "waived"] and all(isinstance(one, str) and one.strip() for one in lines)
            and len(set(lines)) == 3 and not set(lines) & {messages.held(act) for act in messages.ACKNOWLEDGED}
            and "`-print ALPHA -`" in said["more"]
            and named.count("ALPHA") == 2 and 0 <= named.find("ALPHA") < named.find("BRAVO") < named.rfind("ALPHA")):
        held("the answers to a print are the engine's messages", "three lines, `more` naming the print due "
             "next, `last` and `waived`, none a held line; the DEVIATION of a print that misses names each document "
             "due, in the order of the debts")
    else:
        failures.append(f"  ✗ the print lines             said={said!r} named={named!r}")


CAPITALS = re.compile(r"\b[A-Z]{2,}\b")   # a word in capitals: insistence, or a name the agent types
NAMED_CAPS = {"REFUSED", "WARNING", "JSON", "OPTIONS", "FIELD", "PROOF", "OPEN", "CALL", "PROVE", "PICK",
              "INFER", "WORK", "SERVE", "DOCUMENT", "DEVIATION", "DIAGNOSTIC"}   # names, never insistence
# what a deviation may not say again: the rules the standing orders state, in their words
RULES = ("one call each", "the production piped", "verbatim", "the cheap branch", "each one takes",
         "never handed", "takes nothing back", "nothing was recorded")


def message_forms(bench, env) -> None:
    """The form of each category, read at its function of `core.messages`, and rendered on a run."""
    from conductor.core import messages                                         # noqa: PLC0415
    held, failures = bench.held, bench.failures
    deviations = {name: getattr(messages, name) for name in (
        "empty_answer", "prints_due", "empty_print", "print_stray", "wrong_answer", "not_offered",
        "stray_production", "soft_catch", "renewed_reopens", "mini_proof_codes", "mini_proof_relapsed",
        "proof_foreign", "proof_unlawful", "proof_unnamed", "proof_failed", "proof_fixes", "proof_unparsed",
        "proof_unshaped", "proof_verdict", "field_unparsed", "production_empty", "production_unparsed")
        if hasattr(messages, name)}
    witness = {"instruction": "INFER", "documents": ("ALPHA", "BRAVO"), "document": "ALPHA", "answer": "x",
               "section": "OPTIONS", "options": ("a", "b"), "name": "SIDE", "key": "abc123", "codes": ("Z1",),
               "relapsed": [{"code": "Z1", "evidence": "e"}], "foreign": ("Q9",), "unnamed": ("Z2",),
               "bare": [{"code": "Z1", "evidence": "e"}], "fixed": [{"code": "Z1", "fix": "f"}], "wrong": "w",
               "verdict": "maybe", "allowed": 3}
    said = {}
    for name, one in deviations.items():
        import inspect                                                          # noqa: PLC0415
        asked = [witness[arg] for arg in inspect.signature(one).parameters]
        said[name] = one(*asked)
    def bare(text: str) -> str:
        """-> a deviation's text without the witness's own values: the words the module wrote."""
        values = [one for value in witness.values() for one in (value if isinstance(value, tuple) else (value,))]
        for value in sorted((one for one in values if isinstance(one, str)), key=len, reverse=True):
            text = text.replace(value, "")
        return text
    off_deviations = [name for name, text in said.items()
                      if not text.startswith("pp: ") or not text.endswith(".") or " -- " in text
                      or set(CAPITALS.findall(bare(text))) - NAMED_CAPS or any(rule in text for rule in RULES)]
    checks = {
        "frame": lambda: messages.framed(messages.MARK, "x") == "▌ x" and messages.closing("AWAIT") == "▶ AWAIT",
        "refusal": lambda: messages.refused("c", "d") == "pp: REFUSED — c — d\npp: nothing was played\n",
        "deviation": lambda: (messages.deviation("the fact", "the call") == "pp: the fact. The call."
                              and len(said) == 22 and not off_deviations),
        "acknowledgement": lambda: (messages.acknowledged("said", "what is due") == "pp: said — what is due"
                                    and all(" — " in messages.held(act) for act in messages.ACKNOWLEDGED)
                                    and all(" — " in messages.printed(one) for one in messages.PRINTED)),
        "fact": lambda: messages.fact("x") == "   (pp: x)",
        "complement": lambda: all(" -- " not in one for one in (messages.ASK_TEXT, messages.RUN_COMPLETES,
                                                                 messages.NOTHING_OPENS, messages.FRAME_LEAVING)),
        "diagnostic": lambda: messages.diagnostic("c", "note", "f", "w") == "c · note · f — w",
        "console": lambda: messages.console("state", "next") == "pp: state — next",
        "maintenance": lambda: messages.maintenance("done") == "pp: done" and messages.warning("x") == "pp: WARNING — x",
    }
    forms = {}
    for name, check in checks.items():
        try:
            forms[name] = bool(check())
        except TypeError:                      # a form function that does not take its parts yet
            forms[name] = False
    import ast                                                                  # noqa: PLC0415
    tree = ast.parse((bench.source() / "engine" / "conductor" / "core" / "messages.py").read_text(encoding="utf-8"))
    documented = {id(node.body[0].value) for node in ast.walk(tree)
                  if isinstance(node, (ast.Module, ast.FunctionDef)) and node.body
                  and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)}
    doubled = [node.lineno for node in ast.walk(tree)          # a line of the module that says `--`, its docs apart
               if isinstance(node, ast.Constant) and isinstance(node.value, str) and " -- " in node.value
               and id(node) not in documented]
    # rendered: a print of a document nothing owes, caught -- its DEVIATION in pp's voice; a call of the
    # console its verb cannot take, refused by name, exit 2
    conductor = env.conductor()
    conductor.forget()
    conductor.start(conductor.boot("BOOT.md"))
    key = conductor.run_id
    said_back, block = env.conductor(key).printed("NOPE", "a production")
    shown = render(block) if block is not None else ""
    under = shown.split(f"{titled(language.DEVIATION)}\n", 1)[-1].splitlines()[:1]
    malformed = cli(env.engine, "doctor", "extra", cwd=env.root)
    refused = malformed.stderr.splitlines()
    # s.1785: an output closed already waits at the run -- the principal's message over it opens nothing,
    # and says an output waits for the bare call, never that it holds one open
    env.conductor(key).hold(env.conductor(key).peek(), "value")
    over = env.conductor(key).opens("the next message").splitlines()[-1:]
    env.conductor(key).forget()
    # one case per category: its form read at its function, and -- where it renders -- as it renders
    rendered = {
        "frame": (not doubled, f"no `--` in the module's lines {doubled[:4]}"),
        "refusal": (malformed.returncode == 2 and refused[:1] != [] and refused[0].startswith(messages.REFUSED)
                    and refused[1:2] == [messages.NOTHING_PLAYED], f"usage={malformed.returncode}/{refused[:2]!r}"),
        "deviation": (said_back == "caught" and under[:1] != [] and under[0].startswith("pp: "),
                      f"deviations={off_deviations[:4]} under={under!r}"),
        "acknowledgement": (over == [messages.opened("waiting")], f"over={over!r}"),
    }
    said_of = {
        "frame": "the marks and the heading's cells; one separator `—` across the module",
        "refusal": "`pp: REFUSED — <code> — <detail>` then pp's line; `doctor extra` refused by name, exit 2",
        "deviation": "the 22 deviations a fact and the call that mends it, in pp's voice; a caught print's "
                     "DEVIATION rendered in that form",
        "acknowledgement": "`pp: <verdict> — <what is due now>`; over a closed output that waits, the line says so",
        "fact": "`(pp: <fact>)`",
        "complement": "the text alone, one separator",
        "diagnostic": "`<code> · <level> · <fact> — <way>`",
        "console": "`pp: <state> — <what follows>`",
        "maintenance": "`pp: <what was done>`, `pp: WARNING — <fact>`",
    }
    for name, ok in forms.items():
        seen, detail = rendered.get(name, (True, ""))
        if ok and seen:
            held(f"the {name} speaks in its form", said_of[name])
        else:
            failures.append(f"  ✗ the {name:<26}form={ok} rendered={seen} {detail}")


def scenario(bench) -> int:
    print_lines(bench)
    env = bench.env("lines")
    env.write("procs/LAWFUL.md", LAWFUL)     # a law in force at the boot: its section has a place
    weld(bench, env)
    order(bench, env)
    clock(bench, env)
    closing_notes(bench, env)
    instruction_names(bench, env)
    view_fact(bench, env)
    message_forms(bench, env)
    return 0
