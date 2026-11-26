#!/usr/bin/env python3
"""The LLM MODELLED -- the harness of the `model` adapter.

It plays ONE launch: the prompt on stdin, the events of the launch on stdout, one JSON object per
line (`words`, `tool`, `tool-result`, `thinking`; the `result` line last). It knows of the run what a
model would know: the prompt it read and what its own calls answered -- no record of the run, no
marble, no network.

What it does with a text, in three steps:

1. **the grammar** (`grammar`, `answered`): the LAST output of pp in the text, read by its structure
   and the engine's constants -- the sections opening on the engine's mark, the INSTRUCTION lines
   (keyword, form, codes, channel, document), the OPTIONS, the closing (`▶ <word>`), the call under
   it (the bare keyed call, the call that carries a message), the facts under the foot, the channel
   the last step that hands a value hands it by, the line that asks the last message; or, when no output stands, the engine's own line
   that answered a call (a held line, a bounce, a refusal, a gesture);
2. **the act** (`semantics`): the FORMS the text may be, read in the data's READINGS by the TRAITS
   of the text alone (the channel it came on, the closing, the call, a fact, where the INSTRUCTION
   lines stand, the value its last step hands) -- one form, the act its FORMS entry gives on that channel; several forms that agree
   on the act, that act and the thought `ambiguous`; several that disagree, no act and the thought
   `undecided`: the hand given back, nothing said; none, a HOLE: said as such, nothing guessed -- or
   in ANSWERS (by the engine's own line answering a call);
3. **the execution**, in the ORDER of a launch: the `=> terminal` productions said as `words` in the
   form the line names (`STRATEGIES`); the call typed by a subprocess of the console (`./pp <key> …`,
   the production of the form due on the call or piped by a heredoc, as the channel of its step
   names), its answer fed back into the loop while the sequel comes by the tool; then, where the
   launch hands back, its last message, said LAST, once: the `=> response` production the latest output
   asked when one did, the three dots of the form `empty` otherwise -- the final message pp never reads.

The VARIANTS of the judgment (`--variant`): `conform` does what the data say; every other one makes
exactly ONE miss, the one its name says, at the first place where it is possible, then conforms --
`wrong-form` hands a production of another form, `wrong-channel` hands a said production to
the tool, `missing-code` leaves one code out of a proof, `bare-fail` gives every code of a proof a
`fail` with no fix and no gap, `bare-call` types the bare call where a value is due, `empty` hands an
empty production, `no-response` hands back without its last message. The one miss is remembered for the SESSION (a file under
the system's temp dir, the model's own memory of its conversation), so that a second launch of the
same session conforms. `quota` is the provider's usage limit, at EVERY launch: the block is not played,
the limit is said as `words`, and the result line carries the error `quota` and its `stop` -- `until` an
hour after the launch, in ISO and UTC --, the launch ending on 1, as a host whose turn ends on an error.

The INTENTION (`PP_MODEL_INTENT` in the environment, a JSON list of one-key acts): what a real model
would decide of itself on reading its principal's message -- `{"open": "REVIEW"}` opens the door
named where a free step offers it, `{"pick": "LEFT"}` elects the option named where a PICK offers it,
`{"field": [...]}` answers the field with the elements named, `{"echo": "<title>"}` names in every
free production the matter an `INFORMATION — <title>` section serves (the element of a lap),
`{"read": "<file>"}` makes the model read the file named in its workspace at the WORK of a document
and say ONE `words` per line of it, each carrying its line (what a real model does of « read the
lines one at a time »), `{"bounce": true}` makes the model type its last call AGAIN once a held line
answered it (the output waits for the principal: the console answers `not played`, the model hands
back), `{"bare": true}` makes the model type the bare call where a value is due (the call the principal's
conduction answers `principal-advances`), `{"unprinted": true}` makes the model WRITE in its message the productions an output asks on
`terminal`, no print call typed (what a real model does when it takes such a line for a message: the next
call that moves the run comes back with the prints due, which it then hands). Read as a model reads the message of its principal, never as a state of the
run; each act but `echo` plays once, at the first place where it can, and what is left is remembered
for the SESSION as the miss is; without it the model conforms alone.

Every free production CITES what the model read (`STRATEGIES`): the document and the keyword of
its step, the titles the block served, the element of the lap -- so that a sheet reads, in the
words said, which block the model answered.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import os
import secrets
import shlex
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parents[1] / "engine" / "conductor" / "core"   # the engine's constants, read where they live
BOUND = 80                                                  # calls one launch may type: a loop that never ends is a miss
CONSOLE = "./pp"                                            # the console, typed as the card shows it
PRINT = "-print"                                            # the verb of the print call: `<key> -print <DOCUMENT> -`


def loaded(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def package(directory: Path, name: str):
    """-> the package at `directory`, loaded under `name` -- its modules import one another relatively."""
    spec = importlib.util.spec_from_file_location(name, directory / "__init__.py",
                                                  submodule_search_locations=[str(directory)])
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


core = package(CORE, "pp_model_core")                         # the engine's data layer, read where it lives
language = importlib.import_module(f"{core.__name__}.language")   # the keywords, the channels, the closings
messages = importlib.import_module(f"{core.__name__}.messages")   # the engine's lines, where they are written
semantics = loaded(HERE / "semantics.py", "pp_model_semantics")   # the data of the model
MARK = messages.MARK                                          # the bar that opens a section
SIGNAL = messages.SIGNAL                                      # the arrow that opens the closing
HEAD = re.compile(rf"^{re.escape(MARK)} pp · run ([0-9a-f]{{6}})", re.M)
INSTRUCTION = re.compile(r"^(?P<keyword>[A-Z]+)(?P<rest>.*?)  \((?P<document>[^()]+)\)$")
CODES = re.compile(r"\[([^\]]*)\]")
CLOSING = re.compile(rf"^{re.escape(SIGNAL)} (\w+)$")
FACT = re.compile(r"^   \(.*\)$")
INLINE_FACT = re.compile(r"^(\S.*?)\s{2,}(\(.*\))$")             # a fact on the call's own line: `./pp <key>   (a reading continues: …)`
PP_LINE = re.compile(rf"^{re.escape(messages.console(''))}(.*)$", re.M)   # a line of the console
REFUSAL = re.compile(rf"^{re.escape(messages.unsaid(messages.REFUSED))}([a-z][a-z0-9-]*)")   # its code, after `pp: `
HOLE = "hole"
QUOTA_SAID = "model: the usage limit of the modelled provider is reached"   # what the `quota` variant says
QUOTA_HOURS = 1                                            # the reset its stop gives, after the launch
INTENT = "PP_MODEL_INTENT"                                 # the intention of the model, as its principal's message
STEP_ACTS = ("open", "gesture")                            # the acts the message asks of a step, in its order
RESERVING = ("opened", "mounted", "re-served", "reopened")   # the held lines whose next block serves the step again
TOOLS = re.compile(r"^\[(.*)\]$")                          # the offers of a step: `[A B C]`
SEGMENT = re.compile(r"^(\[\d+\] )?\S.* ▸ .*|^(\[\d+\] )?[A-Z_][\w-]*\{[\d/-]+\}")   # a segment's heading: the stack
READING_FACT = re.compile("^" + re.escape(messages.fact(messages.READING).strip()[:-1]))   # the fact of a chunk


# --- the grammar ----------------------------------------------------------------------------------

def grammar(text: str) -> dict | None:
    """-> the LAST output of pp in `text`, read by its structure: `key`, `instructions` (keyword,
    form, codes, channel, document), `options`, `closing` (the word after the arrow, "" when none),
    `call` (its kind: `bare`, `message`, ""), `facts`, `due` (the channel the last step that is no
    last message hands a value by, "" when it hands none) with `valued` (that step), `response` (the
    line that asks the last message, None when the output asks none), `tools` (the offers of the step)
    and `served` (the matter of every `INFORMATION — <title>` section, by title);
    None when no output stands in the text."""
    heads = list(HEAD.finditer(text))
    if not heads:
        return None
    output = text[heads[-1].start():]
    key = heads[-1].group(1)
    sections: list[tuple[str, list[str]]] = []
    for line in output.splitlines():
        if line.startswith(MARK + " "):
            sections.append((line[len(MARK) + 1:], []))
        elif sections:
            sections[-1][1].append(line)
    instructions = []
    for title, lines in sections:
        if title != language.INSTRUCTION:
            continue
        for line in lines:
            read = INSTRUCTION.match(line)
            if read is None or read.group("keyword") not in language.YIELDING:
                continue
            instructions.append(_instruction(read))
    # the segments in order: an INSTRUCTION section belongs to the heading before it, and where the
    # lines stand -- the last segment, an earlier one, none -- is a trait of the text
    segments: list[bool] = []
    for title, lines in sections:
        if SEGMENT.match(title) and not title.startswith("pp · run"):
            segments.append(False)
        elif title == language.INSTRUCTION and segments and any(
                INSTRUCTION.match(one) and INSTRUCTION.match(one).group("keyword") in language.YIELDING
                for one in lines):
            segments[-1] = True
    instructed = "last" if segments and segments[-1] else ("earlier" if any(segments) else "none")
    headings = [title for title, _ in sections if SEGMENT.match(title) and not title.startswith("pp · run")]
    options = [one for title, lines in sections if title == language.OPTIONS for one in lines if one.strip()]
    tools = [name for title, lines in sections if title == language.TOOLS for line in lines
             if TOOLS.match(line.strip()) for name in TOOLS.match(line.strip()).group(1).split()]
    served = {subject: "\n".join(lines).strip() for (name, subject), lines
              in ((language.section_of(title), lines) for title, lines in sections)
              if name == language.INFORMATION and subject}
    closing, call_lines, facts = "", [], []
    lines = output.splitlines()
    for at, line in enumerate(lines):
        closed = CLOSING.match(line)
        if closed:
            closing = closed.group(1)
            for following in lines[at + 1:]:
                if FACT.match(following) or not following.strip():
                    break
                inline = INLINE_FACT.match(following)
                if inline:                          # the call and its fact on one line: the fact kept apart
                    facts.append(inline.group(2))
                    following = inline.group(1)
                call_lines.append(following)
        if FACT.match(line):
            facts.append(line.strip())
    # the line that asks the last message stands last; the value due is read on the last line before
    # it, wherever its heading stands
    response = instructions[-1] if instructions and instructions[-1]["channel"] == language.RESPONSE else None
    last = next((one for one in reversed(instructions) if one["channel"] != language.RESPONSE), None)
    valued = last if last and language.valued(last["channel"] or "") else None
    due = valued["channel"] if valued else ""
    return {"key": key, "instructions": instructions, "options": options, "tools": tools, "served": served,
            "closing": closing, "call": _call_kind(key, closing, call_lines), "due": due, "facts": facts,
            "valued": valued, "response": response,
            "fact": "reading" if any(READING_FACT.match(one) for one in facts) else "", "instructed": instructed,
            "heading": headings[-1] if headings else ""}


def traits_of(reading: dict, channel: str) -> dict:
    """-> the TRAITS of a text (`semantics.TRAITS`): the channel it came on and what its grammar read --
    the closing, the call, the fact of the foot, where the INSTRUCTION lines stand, the channel the
    last step that is no last message hands a value by."""
    return {"channel": channel, "closing": reading["closing"], "call": reading["call"],
            "fact": reading.get("fact", ""), "instructed": reading.get("instructed", "none"),
            "due": reading.get("due", "")}


def _instruction(read) -> dict:
    rest = read.group("rest").strip()
    tokens = rest.split()
    form = tokens[0] if tokens and not tokens[0].startswith("[") and tokens[0] != "=>" else None
    codes = CODES.search(rest)
    channel = tokens[tokens.index("=>") + 1] if "=>" in tokens and tokens.index("=>") + 1 < len(tokens) else None
    return {"keyword": read.group("keyword"), "form": form,
            "codes": codes.group(1).split() if codes else [], "channel": channel,
            "document": read.group("document")}


def _call_kind(key: str, closing: str, lines: list[str]) -> str:
    """-> what stands under the closing: the `bare` keyed call, a call that carries the principal's
    `message` (under AWAIT, whatever its shape), or nothing."""
    if not lines:
        return ""
    if closing == language.AWAIT:
        return "message"
    if lines[0].strip() == f"{CONSOLE} {key}":
        return "bare"
    return "message"


def answered(text: str, gesture: bool = False) -> tuple[str, dict | None]:
    """-> (the name of the answer, its ANSWERS row) for the engine's own line in a call's result --
    a held line, the line of a print taken, a bounce, a refusal, a gesture --; (`hole`, None) when the data know no such line.
    `gesture` says the call typed was a gesture (`gestured`): a result that carries no line of pp is
    then the script's own output -- on an output of one segment the engine renders no anchor line
    over it -- and reads as the gesture's answer; behind any other call such a result is a hole."""
    rows = semantics.ANSWERS
    if any(line.startswith(rows["gesture"]["said"]) for line in text.splitlines()):
        return "gesture", rows["gesture"]
    for said in PP_LINE.findall(text):
        refused = REFUSAL.match(said)
        if refused:
            code = refused.group(1)
            if code in rows and rows[code]["kind"] == "refusal":
                return code, rows[code]
            return "refusal", rows["refusal"]
        for name, row in rows.items():
            if row["kind"] == "held" and said == row["said"]:
                return name, row
            if row["kind"] == "printed" and said.startswith(row["said"]):   # `more` names the call due after it
                return name, row
            if row["kind"] == "bounce" and said.startswith(row["said"]):
                return name, row
        return HOLE, None
    return ("gesture", rows["gesture"]) if gesture else (HOLE, None)


def gestured(words: list[str]) -> bool:
    """-> whether the call typed is a GESTURE: a skill played by its name, `-s <name>`, whatever the
    name -- the one call whose result may carry a script's own output and nothing of pp: a door and
    a manual answer by lines of pp, so a result without one behind `-s` is a script's text. The one
    site that says it: the campaign's reader asks here."""
    return "-s" in words and words.index("-s") + 1 < len(words)


AMBIGUOUS, UNDECIDED = "ambiguous", "undecided"


def foot(reading: dict, channel: str) -> tuple[tuple[str, ...], str, str]:
    """-> (forms, act, note): the CANDIDATE forms the data's READINGS give the text's traits, never
    settled by an order -- one form, its act on the channel; several that agree on the act, that act
    and the note `ambiguous`; several that disagree, no act and the note `undecided`; none, no act:
    a hole."""
    found = semantics.reading_of(traits_of(reading, channel))
    forms = tuple(found["forms"]) if found else ()
    acts = []
    for form in forms:
        act = semantics.FORMS[form][channel]["act"]
        if act not in acts:
            acts.append(act)
    if not forms:
        return (), "", ""
    if len(forms) == 1:
        return forms, acts[0], ""
    return forms, (acts[0] if len(acts) == 1 else ""), (AMBIGUOUS if len(acts) == 1 else UNDECIDED)


# --- the model ------------------------------------------------------------------------------------

class Model:
    def __init__(self, variant: str, session: str, cwd: Path, intent: list[dict] | None = None) -> None:
        self.variant, self.session, self.cwd = variant, session, cwd
        self.memory = Path(tempfile.gettempdir()) / f"pp-model-{session}.json"
        remembered = self._remembered()
        self.missed = bool(remembered.get("missed"))
        self.intent = list(remembered["intent"] if "intent" in remembered else (intent or []))   # the acts left
        self.echo = [one["echo"] for one in self.intent if "echo" in one]   # the titles echoed, never consumed
        self.persisting = next((one["persist"] for one in self.intent if "persist" in one), None)   # a miss at every place
        self.said: set[tuple] = set()   # the steps whose production this launch said: a view brings them back unsaid
        self.kept: list[list] = list(remembered.get("kept", []))   # the lines read in a chunk before the last, each
                                        # with what its chunk served: said when the output is whole
        self.owed: tuple[dict, dict] | None = None   # the last message the launch owes: the line that asks it, its output
        self.held_back: tuple[dict, dict] | None = None   # the free step's line held while its gestures play
        self.calls = 0
        self.last: tuple[list[str], str | None] = ([], None)   # the last call typed: what a bounce types again

    def _remembered(self) -> dict:
        """-> the memory of the session: the one miss once made, the acts of the intention still meant."""
        try:
            read = json.loads(self.memory.read_text(encoding="utf-8"))
            return read if isinstance(read, dict) else {}
        except (OSError, ValueError):
            return {}

    def remember(self) -> None:
        self.memory.write_text(json.dumps({"missed": self.missed, "variant": self.variant, "intent": self.intent,
                                           "kept": self.kept}), encoding="utf-8")

    def meant(self, kind: str, where=None, still: bool = False) -> object:
        """-> the value of the first act of `kind` still meant, taken out -- when `where` is given, the
        act whose value `where` holds (an option among OPTIONS, a door among TOOLS); when `still` is
        asked, a gesture that moves nothing (a view, a script) -- what plays while an output waits, as
        the standing orders say; None otherwise."""
        for at, one in enumerate(self.intent):
            value = one.get(kind)
            if value is None or (where is not None and value not in where):
                continue
            if still and not moves_nothing(str(value)):
                continue
            del self.intent[at]
            self.remember()
            self.think(f"intent {kind} {value}")
            return value
        return None

    def means(self, kind: str, where=None) -> bool:
        """-> whether the NEXT act the message asks of a step -- the first door or gesture still meant -- is of
        `kind` (its value held by `where`, when given), nothing taken out: an act of THIS step, which the
        message puts before the step's production; a later act belongs to a later step."""
        first = next((one for one in self.intent if any(name in one for name in STEP_ACTS)), None)
        return first is not None and first.get(kind) is not None and (where is None or first[kind] in where)

    def element_of(self, reading: dict) -> str:
        """-> the element the step serves: the engine's `field`, or a section the intention echoes."""
        served = reading["served"]
        return served.get("field") or next((served[title] for title in self.echo if served.get(title)), "")

    def cited(self, instruction: dict, reading: dict | None = None) -> dict:
        """-> what a production cites: the document and the keyword of its step, the titles served by the
        block (`nothing` when none), the element of the lap."""
        served = ", ".join(sorted(reading["served"])) if reading and reading.get("served") else "nothing"
        return {"document": instruction.get("document", ""), "keyword": instruction.get("keyword", ""),
                "served": served, "element": instruction.get("element", "")}

    def miss(self, what: str) -> bool:
        """-> whether the miss `what` is made NOW: the variant's name and no miss made yet in this session,
        or the miss the intention PERSISTS in, made at every place where it is possible."""
        if self.persisting == what:
            self.think(f"miss {what}")
            return True
        if self.variant != what or self.missed:
            return False
        self.missed = True
        self.remember()
        self.think(f"miss {what}")
        return True

    # the events
    def say(self, kind: str, **fields) -> None:
        print(json.dumps({"kind": kind, **fields}, ensure_ascii=False), flush=True)

    def words(self, text: str) -> None:
        self.say("words", text=text)

    def think(self, text: str) -> None:
        self.say("thinking", text=text)

    def call(self, args: list[str], stdin: str | None = None) -> str:
        """The console typed: `./pp <args…>`, a production piped when `stdin` is given; -> what it
        printed, both streams. Said as a `tool` and its `tool-result`."""
        self.calls += 1
        self.last = (list(args), stdin)
        identity = f"c{self.calls}"
        shell = shlex.join([CONSOLE, *args]) + (f" <<'EOF'\n{stdin}\nEOF" if stdin is not None else "")
        self.say("tool", id=identity, name="Bash", title=shell.splitlines()[0], shell=shell,
                 input={"command": shell})
        played = subprocess.run([CONSOLE, *args], cwd=str(self.cwd), capture_output=True, text=True,
                                input=stdin if stdin is not None else "")
        content = played.stdout + (("\n" + played.stderr) if played.stderr.strip() else "")
        self.say("tool-result", id=identity, content=content, error=played.returncode != 0)
        return content

    # the productions
    def production(self, instruction: dict, options: list[str], reading: dict | None = None) -> str:
        """-> the conforming production of the step: the form the line names, else the one its keyword
        rules, rendered by the data's strategy -- a form the data do not know renders `any`."""
        strategies = semantics.STRATEGIES
        form = instruction["form"] or strategies["keywords"].get(instruction["keyword"], {}).get("form", "any")
        return self.rendered(form, instruction, options, reading)

    def rendered(self, form: str, instruction: dict, options: list[str], reading: dict | None = None) -> str:
        strategy = semantics.STRATEGIES["forms"].get(form) or semantics.STRATEGIES["forms"]["any"]
        if form == "options":
            meant = self.meant("pick", options)
            return meant if meant is not None else (options[0] if options else "")
        if form == "field":
            meant = self.meant("field")
            if isinstance(meant, list):
                return json.dumps(meant, ensure_ascii=False)
        cited = self.cited(instruction, reading)
        if form == "proof":
            codes = list(instruction["codes"])
            if codes and self.miss("missing-code"):
                codes = codes[1:]
            verdict = "fail" if codes and self.miss("bare-fail") else strategy["verdict"]
            return json.dumps([{"code": code, "evidence": strategy["evidence"].format(code=code, **cited),
                                "verdict": verdict} for code in codes])
        return strategy["production"].format(**cited)

    def handed(self, reading: dict) -> tuple[list[str], str | None]:
        """-> (args, stdin) of the call the last step's channel names: the production of the form
        due -- on the call for the channel `tool`, piped by a heredoc for `tool_heredoc`; the variants
        that bear on a value due play here."""
        key = reading["key"]
        due = {**reading["valued"], "element": self.element_of(reading)}
        chosen = semantics.STRATEGIES["keywords"]["PICK"]["form"]      # a choice names what is chosen, its form is the engine's
        form = chosen if due["keyword"] == "PICK" else (due["form"] or "any")
        if self.miss("bare-call") or self.meant("bare") is not None:
            return [key], None
        piped = reading["due"] == language.TOOL_HEREDOC
        if self.miss("empty"):
            return ([key, "-"], "") if piped else ([key, ""], None)
        if self.miss("wrong-form"):
            other = "json" if form != "json" else "list"
            text = self.rendered(other, due, reading["options"], reading) if piped else "not-an-option"
        else:
            text = self.rendered(form, due, reading["options"], reading)
        return ([key, "-"], text) if piped else ([key, text], None)

    # the loop
    def play(self, prompt: str) -> None:
        text, channel, key = prompt, "prompt", ""
        for _ in range(BOUND):
            reading = grammar(text)
            key = reading["key"] if reading else key
            if reading is not None and reading["response"] is not None:
                self.owed = (reading["response"], reading)      # the latest output that asks a last message
            if reading is None:
                name, row = answered(text, gesture=channel == "tool" and gestured(self.last[0]))
                if row is None:
                    self.think(f"{HOLE}: {_first_line(text)}")
                    return
                self.think(f"answer {name} · form {row['form']} · act {row['act']}")
                if row["act"] == "STOP":
                    self.words(_first_line(text, "pp: "))     # the refusal said is the launch's last message
                    return
                if row["kind"] == "held" and self.meant("bounce") is not None:
                    # the output waits for the principal: the call typed again moves nothing -- the
                    # console answers `not played`, read at the next turn of the loop
                    args, stdin = self.last
                    text, channel = self.call(args, stdin), "tool"
                    continue
                if name in RESERVING:
                    self.held_back = None                   # the engine serves the step again: its line comes back
                if row["act"] == "READ_ON":
                    # the work that remains of the step: a gesture meant -- over a held output, one that moves
                    # nothing (a view, a script); a gesture that moves the run waits for the next turn
                    gesture = self.meant("gesture", still=row["kind"] == "held")
                    if gesture is not None:
                        text, channel = self.call([key, *shlex.split(str(gesture))]), "tool"
                        continue
                    called = self.released()                # the step's production, once its gestures are done
                    if called is not None:
                        text, channel = called, "tool"
                        continue
                called = self.responded()                   # held, bounced, refused: the sequel comes at the next turn
                if called is None:
                    return
                text, channel = called, "tool"
                continue
            forms, act, note = foot(reading, channel)
            self.think(f"read {' '.join(forms) or HOLE} · channel {channel} · closing {reading['closing'] or '-'}"
                       f" · due {reading['due'] or '-'} · act {act or (note or HOLE)}")
            if not act:
                if not forms:
                    self.think(f"{HOLE}: {_first_line(text)}")
                return                                      # undecided, or a hole: the hand given back
            if act != "READ_ON":
                self.held_back = None                       # a block that moved on says again the lines still due
            if act == "READ_ON":                            # a view of the block that stands: nothing moved
                gesture = self.meant("gesture")
                if gesture is not None:
                    text, channel = self.call([key, *shlex.split(str(gesture))]), "tool"
                    continue
                called = self.released()
                if called is not None:
                    text, channel = called, "tool"
                    continue
                called = self.responded()
                if called is None:
                    return
                text, channel = called, "tool"
                continue
            chunk = reading["fact"] == "reading"
            free = not chunk and any(language.said(one["channel"] or "") for one in reading["instructions"])
            # a door or a gesture the message asks for plays DURING the free step: its production, the last
            # said on `terminal`, waits for it -- printed, it would end the step
            during = free and (self.means("open", reading["tools"]) or self.means("gesture"))
            if chunk:
                self.keep(reading)                          # nothing is due before the output is whole
            else:
                called = self.spoken(reading, channel, during)   # a wrong-channel miss types a call of its own
                if called is not None:
                    text, channel = called, "tool"
                    continue
            door = self.meant("open", reading["tools"]) if free else None
            if door is not None:                            # the door the message asked for, opened during the WORK
                text, channel = self.call([key, "-s", door]), "tool"
                continue
            gesture = self.meant("gesture") if free else None
            if gesture is not None:                         # the gesture the message asked for, during the WORK
                text, channel = self.call([key, *shlex.split(str(gesture))]), "tool"
                continue
            if act in ("CALL", "SAY_CALL"):
                if reading["due"] and not reading["closing"]:
                    args, stdin = self.handed(reading)
                else:
                    args, stdin = [reading["key"]], None
                text, channel = self.call(args, stdin), "tool"
                continue
            called = self.responded()                       # hand back: the sequel comes at the next turn
            if called is None:
                return
            text, channel = called, "tool"

    def keep(self, reading: dict) -> None:
        """A chunk before the last: the `=> terminal` lines it carries are KEPT, each with what its
        chunk served -- their productions are said when the output is whole, in the order of the steps."""
        served = {"key": reading["key"], "heading": reading.get("heading", ""), "options": [],
                  "served": reading["served"]}
        lines = [[one, served] for one in reading["instructions"] if one["channel"] == language.TERMINAL]
        if lines:
            self.kept += lines
            self.remember()

    def spoken(self, reading: dict, channel: str, during: bool = False) -> str | None:
        """Hands the `=> terminal` productions of the output, each by its print call, in the order of
        its lines: the lines kept from its chunks first, then the lines of the text that ends it. ->
        what the console answered when a call's result is to be read on -- the next block (the last
        print of an output closed on its prints moved the run), a held line, a block that came back
        with its deviation --, None when every print was answered by its own line. An `unprinted`
        meant writes those productions as texts of the message instead, once: no call is typed. `during`
        holds back the last of those lines: the free step a door or a gesture plays during."""
        if self.meant("unprinted") is not None:
            lines = [*self.kept, *([one, reading] for one in reading["instructions"]
                                   if one["channel"] == language.TERMINAL)]
            self.kept = []
            self.remember()
            for instruction, served in lines:
                self.words(self.production({**instruction, "element": self.element_of(served)},
                                           served["options"], served))
            return None
        while self.kept:
            instruction, served = self.kept.pop(0)
            self.remember()
            called = self.printed(instruction, served)
            if called is not None:
                return called
        lines = [one for one in reading["instructions"] if one["channel"] == language.TERMINAL]
        if during and lines:
            self.held_back = (lines[-1], reading)
        for instruction in lines[:-1] if during else lines:
            called = self.printed(instruction, reading)
            if called is not None:
                return called
        return None

    def released(self) -> str | None:
        """Hands the production a free step held back while its gestures played (`spoken`, `during`), once
        they are done and nothing serves the step again -- a door, a mount, a re-serve or a block that moves
        on brings its line back (`RESERVING`); a gesture that moved nothing and a space left do not. ->
        what the console answered when it is no line of a print taken, None otherwise."""
        if self.held_back is None:
            return None
        (instruction, reading), self.held_back = self.held_back, None
        return self.printed(instruction, reading)

    def printed(self, instruction: dict, reading: dict) -> str | None:
        """Hands ONE production said on `terminal`: the print call that names the document of its
        line, the production piped -- every such line a text shows is due, so none is skipped. ->
        what the console answered when it is no line of a print taken (`ANSWERS`, kind `printed`),
        None otherwise. The wrong-channel miss hands the production as a value instead."""
        text = self.production({**instruction, "element": self.element_of(reading)}, reading["options"], reading)
        if self.miss("wrong-channel") or self.meant("stray") is not None:
            return self.call([reading["key"], text])
        read = self.meant("read") if instruction["keyword"] == "WORK" else None
        lines = self.read_lines(str(read)) if read is not None else []
        handed = "\n".join(f"{text}: {line}" for line in lines) or text   # the file named: a line per line
        content = self.call([reading["key"], PRINT, instruction["document"], "-"], handed)
        _, row = answered(content)
        return None if row is not None and row["kind"] == "printed" else content

    def responded(self) -> str | None:
        """Says the LAST message of the launch, where it hands back -- once, after every call: the
        `=> response` production of the latest output that asked one, the three dots of the form `empty`
        when none did. -> what a wrong-channel miss made the console answer, None when nothing was
        typed (the launch ends there). The variant `no-response` hands back without it."""
        if self.miss("no-response"):
            self.owed = None
            return None
        if self.owed is None:
            self.words(language.DOTS)
            return None
        (instruction, reading), self.owed = self.owed, None
        return self.voiced(instruction, reading)

    def voiced(self, instruction: dict, reading: dict) -> str | None:
        """Says the LAST message of a launch, as `words`: the production of the step its output
        asked on `response`, in the form its line names -- once per launch, a view of the step that
        stands brings none back. -> what the console answered when the production was handed to the
        tool instead (the wrong-channel miss, a stray meant), None when it was said or stood said
        already."""
        step = (reading["key"], reading.get("heading", ""), instruction["document"], instruction["keyword"],
                instruction.get("form"), self.element_of(reading))
        if step in self.said:
            return None                                     # a view of the step that stands: said already
        text = self.production({**instruction, "element": self.element_of(reading)}, reading["options"], reading)
        if instruction.get("form") != language.EMPTY and (self.miss("wrong-channel") or self.meant("stray") is not None):
            return self.call([reading["key"], text])
        self.said.add(step)
        read = self.meant("read") if instruction["keyword"] == "WORK" else None
        lines = self.read_lines(str(read)) if read is not None else []
        for line in lines:                                  # the file named: one words per line, each carrying its line
            self.words(f"{text}: {line}")
        if not lines:
            self.words(text)
        return None

    def read_lines(self, name: str) -> list[str]:
        """-> the lines of the file `name` in the workspace, read as a model reads them: one at a time;
        none when the file does not stand (the words then say the production alone)."""
        path = self.cwd / name
        if not path.is_file():
            return []
        return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def moves_nothing(gesture: str) -> bool:
    """-> whether a gesture MOVES NOTHING of the run, as the console judges it: a view (`-peek`, a switch)
    or a script called by its name (`-s pp-…`); a door, a mount, a space, a re-serve move the run or its
    view, and wait while an output is held."""
    words = shlex.split(gesture)
    if words[:1] in (["-peek"], ["-disable"], ["-enable"]):
        return True
    return len(words) >= 2 and words[0] == "-s" and words[1].startswith("pp-")


def _first_line(text: str, opening: str = "") -> str:
    return next((line for line in text.splitlines() if line.startswith(opening) and line.strip()), text.strip()[:200])


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--variant", default="conform")
    parser.add_argument("--session", default=None)
    asked = parser.parse_args(argv)
    if asked.variant not in ("conform", "wrong-form", "wrong-channel", "missing-code", "bare-fail", "bare-call",
                             "empty", "no-response", "quota"):
        print(f"model: REFUSED -- variant-unknown -- `{asked.variant}`", file=sys.stderr)
        return 2
    cwd = Path.cwd()
    if not (cwd / CONSOLE).is_file():
        print(f"model: REFUSED -- console-missing -- no `{CONSOLE}` under {cwd}", file=sys.stderr)
        return 2
    session = asked.session or f"model-{secrets.token_hex(4)}"
    try:
        intent = json.loads(os.environ.get(INTENT) or "[]")
    except ValueError:
        print(f"model: REFUSED -- intent-invalid -- `{INTENT}` is no JSON list", file=sys.stderr)
        return 2
    if not isinstance(intent, list) or not all(isinstance(one, dict) and len(one) == 1 for one in intent):
        print(f"model: REFUSED -- intent-invalid -- `{INTENT}` is a JSON list of one-key acts", file=sys.stderr)
        return 2
    if asked.variant == "quota":                # the provider's limit: nothing played, the limit said, its stop
        sys.stdin.read()
        until = (datetime.now(timezone.utc) + timedelta(hours=QUOTA_HOURS)).replace(microsecond=0).isoformat()
        print(json.dumps({"kind": "words", "text": QUOTA_SAID}), flush=True)
        print(json.dumps({"kind": "result", "cost_usd": 0.0, "denials": [], "error": "quota", "session": session,
                          "variant": asked.variant, "missed": False, "calls": 0, "intent-left": intent,
                          "stop": {"kind": "quota", "until": until, "said": QUOTA_SAID}}), flush=True)
        return 1
    model = Model(asked.variant, session, cwd, intent)
    error = None
    try:
        model.play(sys.stdin.read())
    except Exception as raised:                 # noqa: BLE001 -- the launch says its own fault, as a provider would
        error = f"{type(raised).__name__}: {raised}"
    print(json.dumps({"kind": "result", "cost_usd": 0.0, "denials": [], "error": error, "session": session,
                      "variant": asked.variant, "missed": model.missed, "calls": model.calls,
                      "intent-left": model.intent}), flush=True)
    return 0 if error is None else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
