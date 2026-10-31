"""The procedure language: which keywords exist, what each needs, and what it answers with."""
from __future__ import annotations

BASE = "kit"        # the base package every instance stands on -- the one name of
                    # the composition the engine may speak: address grammar,
                    # settings fragments, the source of its own pushes
SYSTEM = ("SYSTEM.COMMON.md", "SYSTEM.CONDUCT.md")  # the two files a section's system/ gives the
                    # marble: what holds in both modes, then what makes the LLM advance pp
CARDS = ("PP.COMMON.md", "PP.CONDUCT.md")   # the engine's two cards under refs/, the same split:
                    # the calls of the agent's tasks, then the calls that make the LLM advance pp
YIELDING = frozenset({"PICK", "INFER", "PROVE", "FIELD", "NEXT", "WORK"})  # yields to the agent: the block frames, the agent plays
FIELD = "@field"    # the DESCRIBED door: what `cycles()` answers for a document declaring `field:` --
                    # no token wears a `@`, so the sentinel never meets a provided one
ASK = "the ask"          # the section under the WORK that opens an exchange: what its context is
ASK_TEXT = "the principal's last message is the context: say the productions above"
WORD = "the principal's word"   # the reading a stopped run serves when the principal's message takes it up
WORDS = "words"        # the text the agent writes outside any tool call: the CHANNEL of a production said
                       # to the principal (`=> words`, derived by the flow, never declared) and the MODE of a
                       # form that is said, standing alone -- one word for one destination
TOOL = "tool"          # the channel of what is handed to pp: the call the closing shows
SAID = "said"          # the base's generic form: what a form of the tool is wrapped in when said
MODES = ("inline", "stdin", WORDS)   # how a form travels: on the call, piped, in the words
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
PROMPT = "prompt"       # the CHANNEL an output reaches the agent by when its principal conducts the run
                        # and the output moves the run on: the prompt of a launch; `TOOL` is the other
                        # one -- the result of the agent's own call (the LLM's mode, a view, an inline)
# what the stack AWAITS after an output -- with the channel, the one parameter the foot is deduced
# from (`blocks.closing`): a value due to the tool, a response due in the agent's words (what the agent
# produces during its turn, by its two channels), a message of the principal due (the root exhausted), a
# reading that continues (a chunk before the last)
VALUE_DUE, RESPONSE_DUE, MESSAGE_DUE, READING_ON = "value", "response", "message", "reading"
AWAITED = (VALUE_DUE, RESPONSE_DUE, MESSAGE_DUE, READING_ON)

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
         LIST: ("OPTIONS", False, ", one at least: the values the next step offers under "
                "OPTIONS, one of which it elects")}
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
           "options": ("inline", "one token, VERBATIM, from OPTIONS"),
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
           **{name: ("stdin", f"{SCALARS}{said}") for name, (_, _, said) in LISTS.items()}}
IMPOSED = ("options", "proof", *LISTS)   # the forms whose mode no `formats:` line moves
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
