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
   it (a template with the form's name where the production goes, the bare keyed call, the call that
   carries a message), the facts under the foot; or, when no output stands, the engine's own line
   that answered a call (a held line, a bounce, a refusal, a gesture);
2. **the act** (`semantics`): the FORMS the text may be, read in the data's READINGS by the TRAITS
   of the text alone (the channel it came on, the closing, the call, a fact, where the INSTRUCTION
   lines stand) -- one form, the act its FORMS entry gives on that channel; several forms that agree
   on the act, that act and the thought `ambiguous`; several that disagree, no act and the thought
   `undecided`: the hand given back, nothing said; none, a HOLE: said as such, nothing guessed -- or
   in ANSWERS (by the engine's own line answering a call);
3. **the execution**: the `=> words` productions said as `words` in the form the line names
   (`STRATEGIES`), the call typed by a subprocess of the console (`./pp <key> …`, the production of the
   form due in the template's place), its answer fed back into the loop while the sequel comes by the
   tool; when it comes at the next turn, or never, the launch ends.

The VARIANTS of the judgment (`--variant`): `conform` does what the data say; every other one makes
exactly ONE miss, the one its name says, at the first place where it is possible, then conforms --
`wrong-form` hands a production of another form, `wrong-channel` hands a `=> words` production to
the tool, `missing-code` leaves one code out of a proof, `bare-call` types the bare call where a value
is due, `empty` hands an empty production. The one miss is remembered for the SESSION (a file under
the system's temp dir, the model's own memory of its conversation), so that a second launch of the
same session conforms.

The INTENTION (`PP_MODEL_INTENT` in the environment, a JSON list of one-key acts): what a real model
would decide of itself on reading its principal's message -- `{"open": "REVIEW"}` opens the door
named where a free step offers it, `{"pick": "LEFT"}` elects the option named where a PICK offers it,
`{"field": [...]}` answers the field with the elements named, `{"echo": "<title>"}` names in every
free production the matter an `INFORMATION — <title>` section serves (the element of a lap),
`{"read": "<file>"}` makes the model read the file named in its workspace at the WORK of a document
and say ONE `words` per line of it, each carrying its line (what a real model does of « read the
lines one at a time »), `{"bounce": true}` makes the model type its last call AGAIN once a held line
answered it (the output waits for the principal: the console answers `not played`, the model hands
back). Read as a model reads the message of its principal, never as a state of the
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
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE.parents[1] / "engine" / "conductor" / "core"   # the engine's constants, read where they live
BOUND = 80                                                  # calls one launch may type: a loop that never ends is a miss
CONSOLE = "./pp"                                            # the console, typed as the card shows it


def loaded(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def constant(module: Path, name: str) -> str:
    """-> the text a `NAME = "…"` line of an engine module assigns: a constant read from the module
    that prints it, never typed again here."""
    found = re.search(rf'^\s*{name} = "([^"]+)"', module.read_text(encoding="utf-8"), re.M)
    if found is None:
        raise SystemExit(f"model: constant-missing -- {name} in {module}")
    return found.group(1)


language = loaded(CORE / "language.py", "pp_language")       # the keywords, the channels, the closings
semantics = loaded(HERE / "semantics.py", "pp_model_semantics")   # the data of the model
MARK = constant(CORE / "model.py", "MARK")                   # the bar that opens a section
SIGNAL = constant(CORE / "model.py", "SIGNAL")               # the arrow that opens the closing
HEAD = re.compile(rf"^{re.escape(MARK)} pp · run ([0-9a-f]{{6}})", re.M)
INSTRUCTION = re.compile(r"^(?P<keyword>[A-Z]+)(?P<rest>.*?)  \((?P<document>[^()]+)\)$")
CODES = re.compile(r"\[([^\]]*)\]")
PLACEHOLDER = re.compile(r"<([a-z][\w-]*)>")                 # the form's name where the production goes
CLOSING = re.compile(rf"^{re.escape(SIGNAL)} (\w+)$")
FACT = re.compile(r"^   \(.*\)$")
INLINE_FACT = re.compile(r"^(\S.*?)\s{2,}(\(.*\))$")             # a fact on the call's own line: `./pp <key>   (a reading continues: …)`
PP_LINE = re.compile(r"^pp: (.*)$", re.M)
REFUSAL = re.compile(r"^REFUSED — ([a-z][a-z0-9-]*)")       # the code of a refusal, after `pp: `
HOLE = "hole"
INTENT = "PP_MODEL_INTENT"                                 # the intention of the model, as its principal's message
TOOLS = re.compile(r"^\[(.*)\]$")                          # the offers of a step: `[A B C]`
SEGMENT = re.compile(r"^(\[\d+\] )?\S.* ▸ .*|^(\[\d+\] )?[A-Z_][\w-]*\{[\d/-]+\}")   # a segment's heading: the stack
READING_FACT = re.compile(r"^\(a reading continues: ")        # the fact of a chunk: a reading continues


# --- the grammar ----------------------------------------------------------------------------------

def grammar(text: str) -> dict | None:
    """-> the LAST output of pp in `text`, read by its structure: `key`, `instructions` (keyword,
    form, codes, channel, document), `options`, `closing` (the word after the arrow, "" when none),
    `call` (its kind: `template`, `bare`, `message`, "") with the `template` lines, `facts`, `tools` (the
    offers of the step) and `served` (the matter of every `INFORMATION — <title>` section, by title);
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
        if title != "INSTRUCTION":
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
        elif title == "INSTRUCTION" and segments and any(
                INSTRUCTION.match(one) and INSTRUCTION.match(one).group("keyword") in language.YIELDING
                for one in lines):
            segments[-1] = True
    instructed = "last" if segments and segments[-1] else ("earlier" if any(segments) else "none")
    headings = [title for title, _ in sections if SEGMENT.match(title) and not title.startswith("pp · run")]
    options = [one for title, lines in sections if title == "OPTIONS" for one in lines if one.strip()]
    tools = [name for title, lines in sections if title == "TOOLS" for line in lines
             if TOOLS.match(line.strip()) for name in TOOLS.match(line.strip()).group(1).split()]
    served = {title.split(" — ", 1)[1]: "\n".join(lines).strip() for title, lines in sections
              if title.startswith("INFORMATION — ")}
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
    return {"key": key, "instructions": instructions, "options": options, "tools": tools, "served": served,
            "closing": closing, "call": _call_kind(key, closing, call_lines), "template": call_lines, "facts": facts,
            "fact": "reading" if any(READING_FACT.match(one) for one in facts) else "", "instructed": instructed,
            "heading": headings[-1] if headings else ""}


def traits_of(reading: dict, channel: str) -> dict:
    """-> the TRAITS of a text (`semantics.TRAITS`): the channel it came on and what its grammar read --
    the closing, the call, the fact of the foot, where the INSTRUCTION lines stand."""
    return {"channel": channel, "closing": reading["closing"], "call": reading["call"],
            "fact": reading.get("fact", ""), "instructed": reading.get("instructed", "none")}


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
    """-> what stands under the closing: a `template` (a placeholder names the form due), the `bare`
    keyed call, a call that carries the principal's `message` (under AWAIT, whatever its shape), or
    nothing."""
    if not lines:
        return ""
    if closing == language.AWAIT:
        return "message"
    joined = "\n".join(lines)
    if PLACEHOLDER.search(joined):
        return "template"
    if lines[0].strip() == f"{CONSOLE} {key}":
        return "bare"
    return "message"


def answered(text: str) -> tuple[str, dict | None]:
    """-> (the name of the answer, its ANSWERS row) for the engine's own line in a call's result --
    a held line, a bounce, a refusal, a gesture --; (`hole`, None) when the data know no such line."""
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
            if row["kind"] == "bounce" and said.startswith(row["said"]):
                return name, row
        return HOLE, None
    return HOLE, None


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
        self.memory.write_text(json.dumps({"missed": self.missed, "variant": self.variant, "intent": self.intent}),
                               encoding="utf-8")

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
            return json.dumps([{"code": code, "evidence": strategy["evidence"].format(code=code, **cited),
                                "verdict": strategy["verdict"]} for code in codes])
        return strategy["production"].format(**cited)

    def handed(self, reading: dict) -> tuple[list[str], str | None]:
        """-> (args, stdin) of the call a template asks: the production of the form due in the
        placeholder's place -- on the call for an inline form, piped for the rest; the variants that
        bear on a value due play here."""
        key = reading["key"]
        joined = "\n".join(reading["template"])
        form = PLACEHOLDER.search(joined).group(1)
        due = next((one for one in reading["instructions"] if one["channel"] == language.TOOL),
                   {"keyword": "INFER", "form": form, "codes": [], "channel": language.TOOL})
        due = {**due, "element": self.element_of(reading)}
        if self.miss("bare-call") or self.meant("bare") is not None:
            return [key], None
        piped = " - " in joined or joined.rstrip().endswith("EOF")
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
        text, channel, opened, key = prompt, "prompt", False, ""
        for _ in range(BOUND):
            reading = grammar(text)
            key = reading["key"] if reading else key
            if reading is None:
                name, row = answered(text)
                if row is None and channel == "prompt" and not opened:
                    # no output in the prompt: the model opens the run itself, as the door of its
                    # workspace tells it to -- the principal's message is the context of its WORK
                    opened, channel = True, "tool"
                    text = self.call(["-new"])
                    continue
                if row is None:
                    self.think(f"{HOLE}: {_first_line(text)}")
                    return
                self.think(f"answer {name} · form {row['form']} · act {row['act']}")
                if row["act"] == "STOP":
                    self.words(_first_line(text, "pp: "))
                    return
                if row["kind"] == "held" and self.meant("bounce") is not None:
                    # the output waits for the principal: the call typed again moves nothing -- the
                    # console answers `not played`, read at the next turn of the loop
                    args, stdin = self.last
                    text, channel = self.call(args, stdin), "tool"
                    continue
                if row["act"] == "READ_ON":
                    # the work that remains of the step: a gesture meant -- over a held output, one that moves
                    # nothing (a view, a script); a gesture that moves the run waits for the next turn
                    gesture = self.meant("gesture", still=row["kind"] == "held")
                    if gesture is not None:
                        text, channel = self.call([key, *shlex.split(str(gesture))]), "tool"
                        continue
                return                                      # held, bounced, refused: the sequel comes at the next turn
            forms, act, note = foot(reading, channel)
            self.think(f"read {' '.join(forms) or HOLE} · channel {channel} · closing {reading['closing'] or '-'}"
                       f" · act {act or (note or HOLE)}")
            if not act:
                if not forms:
                    self.think(f"{HOLE}: {_first_line(text)}")
                return                                      # undecided, or a hole: the hand given back
            if act == "READ_ON":                            # a view of the block that stands: nothing moved
                gesture = self.meant("gesture")
                if gesture is not None:
                    text, channel = self.call([key, *shlex.split(str(gesture))]), "tool"
                    continue
                return
            called = self.spoken(reading, channel)         # a wrong-channel miss types a call of its own
            if called is not None:
                text, channel = called, "tool"
                continue
            free = any(one["channel"] == language.WORDS for one in reading["instructions"])
            door = self.meant("open", reading["tools"]) if free else None
            if door is not None:                            # the door the message asked for, opened during the WORK
                text, channel = self.call([key, "-s", door]), "tool"
                continue
            gesture = self.meant("gesture") if free else None
            if gesture is not None:                         # the gesture the message asked for, during the WORK
                text, channel = self.call([key, *shlex.split(str(gesture))]), "tool"
                continue
            if act in ("CALL", "SAY_CALL"):
                if reading["call"] == "template":
                    args, stdin = self.handed(reading)
                else:
                    args, stdin = [reading["key"]], None
                text, channel = self.call(args, stdin), "tool"
                continue
            return                                          # hand back: the sequel comes at the next turn

    def spoken(self, reading: dict, channel: str) -> str | None:
        """Says the `=> words` productions of the output, in the order of its lines. -> what a
        wrong-channel miss made the console answer, None when nothing was typed."""
        for instruction in reading["instructions"]:
            if instruction["channel"] != language.WORDS:
                continue
            step = (reading["key"], reading.get("heading", ""), instruction["document"], instruction["keyword"],
                    instruction.get("form"), self.element_of(reading))
            if step in self.said:
                continue                                    # a view of the step that stands: said already
            text = self.production({**instruction, "element": self.element_of(reading)}, reading["options"], reading)
            if self.miss("wrong-channel") or self.meant("stray") is not None:
                return self.call([reading["key"], text])
            self.said.add(step)
            read = self.meant("read") if instruction["keyword"] == "WORK" else None
            lines = self.read_lines(str(read)) if read is not None else []
            for line in lines:                              # the file named: one words per line, each carrying its line
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
    if asked.variant not in ("conform", "wrong-form", "wrong-channel", "missing-code", "bare-call", "empty"):
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
