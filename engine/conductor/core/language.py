"""The procedure language: which keywords exist, what each needs, and what it answers with."""
from __future__ import annotations

from . import messages

BASE = "kit"        # the base package every instance stands on -- the one name of
                    # the composition the engine may speak: address grammar,
                    # settings fragments, the source of its own pushes
SYSTEM = "SYSTEM.md"   # the one file a section's system/ gives the marble: its standing orders
SYS = "SYS.md"         # the file beside it that declares the SYSTEM LAWS: in force at every block,
                       # said whole once per output -- the engine's and the instance's alone
SYS_KIND = "sys"       # the kind of a SYS.md: its laws and nothing else
SYS_KEYS = frozenset({"name", "description", "kind", "constraints.production", "constraints.behavior"})
SYS_CODE = r"SYS[0-9]+"   # the code of a system law, and of no other: `SYS<n>`
CARD = "PP.md"         # the engine's card under refs/: the calls of the agent's tasks
YIELDING = frozenset({"PICK", "INFER", "PROVE", "FIELD", "NEXT", "WORK"})  # yields to the agent: the block frames, the agent plays
FIELD = "@field"    # the DESCRIBED door: what `cycles()` answers for a document declaring `field:` --
                    # no token wears a `@`, so the sentinel never meets a provided one
ASK = "the ask"          # the section under the WORK that opens an exchange: what its context is
WORD = "the principal's word"   # the reading a stopped run serves when the principal's message takes it up
WORDS = "words"        # the MODE of a form that is said to the principal, standing alone: what an author
                       # writes on a `formats:` line beside `inline` and `stdin` -- never a channel
TERMINAL = "terminal"  # the CHANNEL of a production said to the principal while the work goes on: an
                       # intermediate message (`=> terminal`, derived by the flow, never declared)
RESPONSE = "response"  # the CHANNEL of the LAST message an output asks: decided where the output closes
                       # (`blocks.responding`), never declared and never a step's own -- no step of the
                       # stack carries it
STEP, ADDED = "step", "added"   # how an output asks its last message (`Block.response`): its last
                       # said step goes `=> response`, or the engine adds a line of the form `empty`
EMPTY = "empty"        # the form of a last message with nothing to say: the three dots, alone
DOTS = "..."           # what the `empty` form is
TOOL = "tool"          # the channel of a production handed to pp on the call: `./pp <key> <production>`
TOOL_HEREDOC = "tool_heredoc"   # the channel of a production handed to pp piped by a heredoc
SAID = "said"          # the base's generic form: what a form of the tool is wrapped in when said
MODES = ("inline", "stdin", WORDS)   # how a form travels: on the call, piped, said to the principal
RETIRED_MODES = frozenset({"chat"})  # a mode the language dropped: on a `formats:` line it refuses by name
FREE = frozenset({"INFER", "WORK"})  # the agent-production pair -- WORK serves the standing ask, free
                                     # chaining until its RESULT stands; INFER is the unitary variant
CHAINING = frozenset({"SERVE", "CALL", "OPEN", "HOOK"})   # runs inside the tool, the next instruction follows
OPEN = "OPEN"       # a CALL whose frame never leaves by its exhaustion: the SPACE it opens is the
                    # root of the passages until `-close` -- entered by the same path as a CALL
NEEDS_OPTIONS = frozenset({"PICK", "NEXT"})  # a choice with nothing to choose from is not a choice
TRANSPARENT = frozenset({"SERVE", "HOOK", "PROVE", "FIELD", "NEXT"})  # act on the side: the pipeline flows
# past them. A CALL is NOT transparent anymore: it YIELDS its callee's last production --
# every output is the next instruction's input, across the frame boundary. A PROVE is a
# CHECKPOINT ON the flow: neither a reader nor a consumer -- the upstream production
# passes through it once proven; its own production (the proof) never travels downstream
BARE = frozenset({"SERVE", "INFER", "PROVE", "FIELD", "NEXT", "WORK"})  # may appear with no argument -- INFER's
                                     # ORDER is the document's served BODY, its form the front matter
KEYWORDS = YIELDING | CHAINING
RETIRED = frozenset({"FINAL"})       # a keyword the language dropped: written in a proc, it refuses by
                                     # name -- no keyword closes a passage, the ROOT's exhaustion does

CONTINUE = "CONTINUE"   # the closing over the call owed now
AWAIT = "AWAIT"         # the closing of a PARKED run: the root of the passage is exhausted, every
                        # production was said at its own step, nothing is delivered -- the run waits
                        # for the principal's message, which opens the next passage on the root
MORE = "MORE"           # the closing of a chunk at the PROMPT: the output is not complete, nothing is
                        # due, the rest comes at the agent's next turn
PROMPT = "prompt"       # the CHANNEL an output reaches the agent by when it moves the run on: the
                        # prompt of a launch; `TOOL` is the other one -- the result of the agent's own
                        # call (a view, an inline)
# what the stack AWAITS after an output -- with the channel, the one parameter the foot is deduced
# from (`blocks.closing`): a value due to pp, a response due from the agent (a production it says to
# the principal), a message of the principal due (the root exhausted), a reading that continues (a
# chunk before the last)
VALUE_DUE, RESPONSE_DUE, MESSAGE_DUE, READING_ON = "value", "response", "message", "reading"
AWAITED = (VALUE_DUE, RESPONSE_DUE, MESSAGE_DUE, READING_ON)

# the SECTIONS of an output: their titles and their order, said here and nowhere else. A segment
# reads its BLOCK's sections once, in this order; then one group per STEP, in the order of the
# steps -- what the step alone reads, its context, its options, its line. The renderer lays a
# segment out by walking the two lists; every other reader of a title takes it here
INFORMATION, TOOLS, CONSTRAINTS = "INFORMATION", "TOOLS", "CONSTRAINTS"
DEVIATION, DIAGNOSTIC = "DEVIATION", "DIAGNOSTIC"
CONTEXT, OPTIONS, INSTRUCTION = "INSTRUCTION CONTEXT", "OPTIONS", "INSTRUCTION"
BLOCK_SECTIONS = (INFORMATION, TOOLS, CONSTRAINTS, DEVIATION, DIAGNOSTIC)
STEP_SECTIONS = (INFORMATION, CONTEXT, OPTIONS, INSTRUCTION)
ELEMENT = "field"   # the subject the element of a DESCRIBED door's lap is served under; a provided
                    # door serves its element under its token's name
INPUT = "input"     # the subject the production a document opens on is served under

FIELD_MAX = 200     # the bound of a described field and of a PICK's options -- a constant,
                    # said at the miss
SCALARS = (f"a JSON array of scalars -- strings or numbers, never a boolean --, each once, "
           f"none empty, {FIELD_MAX} at most")
LIST = "list"       # the form of the step a PICK elects from, whatever its document's `output:`
# the forms the engine IMPOSES as an array of scalars, one entry each: the list a miss
# names, whether an empty array is a form, what the definition adds to SCALARS -- the
# mode, the definition and the judge (`scalars_form`) all read here
LISTS = {"field": ("FIELD", True, ": the elements the brief describes; an empty array says "
                   "nothing is due; the document then serves one element per lap, nothing "
                   "else travels"),
         LIST: (OPTIONS, False, ", one at least: the values the next step offers under "
                f"{OPTIONS}, one of which it elects")}
FORMATS = {"free": ("stdin", "structure with titled sections and an appropriate icon "
                    "when it serves -- one table per concern, a blank line around every "
                    "title and table, short cells that point at the detail; plain "
                    "markdown only"),
           "json": ("stdin", "one valid JSON value, nothing around it"),
           "table": ("stdin", "a titled markdown table -- bold TITLE above with an "
                     "appropriate icon, named columns, one short clause per cell; status "
                     "cells use ✅ done · 🔄 ongoing · ⏳ pending · ⛔ gate · ⚠️ alert · "
                     "❌ fail · 💤 dormant · ⏭️ skip; plain markdown only"),
           "line": ("inline", "one line, plainly worded"),
           "options": ("inline", f"one token, VERBATIM, from {OPTIONS}"),
           "any": ("stdin", "whatever the upstream carries -- the untyped wildcard"),
           "proof": ("stdin", 'a JSON array -- one object for EVERY code the line asks, the '
                              'deepest first, a code left unnamed a miss: {"code", "evidence", '
                              '"verdict": "ok"|"fail"|"n/a"} -- ok is EARNED by a verification and '
                              'its evidence is a RENDERING (a command, a diff, a count, '
                              'a file:line), n/a says a law without bearing here, fail '
                              'names the gap and MAY name its "fix" (the named fix '
                              'repairs in place: the failed codes alone re-prove) or '
                              'declare it "blocked" (what is missing: the checkpoint '
                              'closes, the gap said at the closing); '
                              'a non-ok is better than a sloppy ok'),
           EMPTY: (WORDS, f"the three dots `{DOTS}`, alone"),
           **{name: ("stdin", f"{SCALARS}{said}") for name, (_, _, said) in LISTS.items()}}
IMPOSED = ("options", "proof", EMPTY, *LISTS)   # the forms whose mode no `formats:` line moves
# the engine's own OUTPUT formats -- the enumeration the kit and the packages EXTEND
# by declaring `formats:` lines; pp dictates the form, the agent never negotiates it

# PROVE is the AUTHOR's word: the one point
# of proof is the PROVE a `proc:` writes -- it pays every law of production on screen over
# what was produced since the last PROVE played, the laws a contributor left due included;
# the engine injects none, and without a written PROVE nothing is due. The agent sees an
# ordinary INFER whose form is the `proof` format above; the marble teaches the mechanism
# FIELD is ENGINE vocabulary too -- the described door injects it at its entry (a
# written one refuses at parse: field-keyword); the agent sees an ordinary INFER whose
# form is the `field` format above, the document's `field:` prose served as its brief
# NEXT is ENGINE vocabulary too -- a document leaving with several successors (`next:`)
# and a `choose:` prose injects it at its exit (a written one refuses at parse:
# next-keyword); the agent sees an ordinary PICK whose OPTIONS are the names of `next:`


def section_of(title: str) -> tuple[str, str]:
    """-> (the section a title names, the subject it serves); ("", "") for a line that names no
    section of the lists -- a heading."""
    name, _, subject = title.partition(messages.SUBJECT)
    return (name, subject) if name in BLOCK_SECTIONS or name in STEP_SECTIONS else ("", "")


def listed(name: str, value) -> str:
    """-> what a value MISSES as the imposed list form `name` (`field`, `list`), or "" --
    the judge the form's entry in LISTS names."""
    what, empty_ok, _ = LISTS[name]
    return scalars_form(value, what, empty_ok)


def scalars_form(value, what: str, empty_ok: bool) -> str:
    """-> what a list of scalars MISSES, or "" when it holds -- the ONE form OPTIONS and
    FIELD share, judged on the value's shape alone: an array, scalars (strings or
    numbers, never a boolean) none empty, each once, FIELD_MAX at most; `what` names
    the list the message speaks of (`OPTIONS`, `FIELD`), `empty_ok` whether an empty
    array is a form (a FIELD with nothing due) or a miss (a PICK with nothing to elect).
    The nature of an element is never judged: an array of integers passes exactly as
    an array of paths that do not exist."""
    if not isinstance(value, list):
        return f"the {what} is not a JSON array."
    for one in value:
        if isinstance(one, bool) or not isinstance(one, (str, int, float)):
            return f"an element of the {what} is not a scalar -- a string or a number."
        if isinstance(one, str) and not one.strip():
            return f"an element of the {what} is empty."
    if len({str(one) for one in value}) != len(value):
        return f"an element of the {what} appears twice -- each once."
    if not value and not empty_ok:
        return f"the {what} are empty -- the next step elects among them."
    if len(value) > FIELD_MAX:
        return f"the {what} holds {len(value)} elements -- {FIELD_MAX} at most."
    return ""


def handed(mode: str) -> str:
    """-> the CHANNEL a form of `mode` is handed to pp by: on the call for an inline form, piped by a
    heredoc for every other."""
    return TOOL if mode == "inline" else TOOL_HEREDOC


def valued(channel: str) -> bool:
    """-> True when `channel` hands a VALUE to pp: on the call or piped by a heredoc."""
    return channel in (TOOL, TOOL_HEREDOC)


def said(channel: str) -> bool:
    """-> True when `channel` SAYS a production to the principal: while the work goes on, or last."""
    return channel in (TERMINAL, RESPONSE)


def listing(name: str, mode: str) -> str:
    """-> what the catalogue of the forms says of the form `name`, of `mode`: the channel a step
    hands it to pp by; for a form that is said, the two channels its step's line chooses between;
    for `empty`, the last message alone."""
    if name == EMPTY:
        return RESPONSE
    return f"{TERMINAL} · {RESPONSE}" if mode == WORDS else handed(mode)


def yields(keyword: str) -> bool:
    return keyword in YIELDING


def needs_options(keyword: str) -> bool:
    return keyword in NEEDS_OPTIONS


def transparent(keyword: str) -> bool:
    """-> True when the instruction feeds nothing downstream: the pipeline flows past it."""
    return keyword in TRANSPARENT


def output_of(keyword: str) -> str:
    """-> the OUTPUT format a yielding keyword produces by default -- a PICK always
    answers `options`, a PROVE always `proof`; an INFER or a WORK answers `any`, the
    untyped form, unless its document declares one: a work has no shape before its
    document gives it one."""
    if keyword in ("PICK", "NEXT"):
        return "options"
    if keyword == "PROVE":
        return "proof"
    if keyword == "FIELD":
        return "field"
    return "any"
