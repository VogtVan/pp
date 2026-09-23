"""The procedure language: which keywords exist, what each needs, and what it answers with."""
from __future__ import annotations

BASE = "kit"        # the base package every instance stands on -- the one name of
                    # the composition the engine may speak: address grammar,
                    # settings fragments, the source of its own pushes
YIELDING = frozenset({"PICK", "INFER", "PROVE", "FIELD", "NEXT", "WORK"})  # yields to the agent: the block frames, the agent plays
FIELD = "@field"    # the DESCRIBED door: what `cycles()` answers for a document declaring `field:` --
                    # no token wears a `@`, so the sentinel never meets a provided one
FREE = frozenset({"INFER", "WORK"})  # the agent-production pair -- WORK serves the standing ask, free
                                     # chaining until its RESULT stands; INFER is the unitary variant
CHAINING = frozenset({"SERVE", "CALL", "HOOK"})        # runs inside the tool, the next instruction follows
NEEDS_OPTIONS = frozenset({"PICK", "NEXT"})  # a choice with nothing to choose from is not a choice
TRANSPARENT = frozenset({"SERVE", "HOOK", "PROVE", "FIELD", "NEXT", "FINAL"})  # act on the side: the pipeline flows
# past them. A CALL is NOT transparent anymore: it YIELDS its callee's last production --
# every output is the next instruction's input, across the frame boundary. A PROVE is a
# CHECKPOINT ON the flow: neither a reader nor a consumer -- the upstream production
# passes through it once proven; its own production (the proof) never travels downstream
CLOSING = frozenset({"FINAL"})  # closes the EXCHANGE where the proc declares it -- the
# frontier is a property of the FLOW, written in the proc; looping is the DOCUMENT's
# (`cycle: true`), orthogonal. A finished proc is finished: the closing is END
BARE = frozenset({"SERVE", "INFER", "PROVE", "FIELD", "NEXT", "FINAL", "WORK"})  # may appear with no argument -- INFER's
                                     # ORDER is the document's served BODY, its form the front matter
KEYWORDS = YIELDING | CHAINING | CLOSING

CONTINUE = "CONTINUE"   # the DEFAULT closing: call back now
FINAL = "FINAL"         # the declared frontier: DELIVER the turn's validated ephemerals
                        # in ONE chat message, then call back once the operator replies
END = "END"             # the proc is finished, no cycle: the conduction stops, pp says it
END_TEXT = ("the conduction is over — report to the operator; "
            "do not call the tool again.")

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
           "proof": ("stdin", 'a JSON array -- the codes AT RISK, one object each, the '
                              'deepest first, a code unnamed is n/a: {"code", "evidence", '
                              '"verdict": "ok"|"fail"|"n/a"} -- ok is EARNED by a verification and '
                              'its evidence is a RENDERING (a command, a diff, a count, '
                              'a file:line), n/a says a law without bearing here, fail '
                              'names the gap and MAY name its "fix" (the named fix '
                              'repairs in place: the failed codes alone re-prove); '
                              'a non-ok is better than a sloppy ok'),
           "field": ("stdin", "a JSON array -- the elements the brief describes, scalars "
                              "(strings or numbers), each once, none empty, 200 at most; an "
                              "empty array says nothing is due; the document then serves one element "
                              "per lap, nothing else travels")}
FIELD_MAX = 200     # the bound of a described field and of a PICK's options -- a constant,
                    # said at the miss
# the engine's own OUTPUT formats -- the enumeration the kit and the packages EXTEND
# by declaring `formats:` lines; pp dictates the form, the agent never negotiates it

# PROVE is ENGINE vocabulary -- only injected checkpoints carry it (a written one
# refuses at parse: prove-retired); the agent sees an ordinary INFER whose form is
# the `proof` format above; the marble teaches the mechanism: no brief is ever served
# FIELD is ENGINE vocabulary too -- the described door injects it at its entry (a
# written one refuses at parse: field-keyword); the agent sees an ordinary INFER whose
# form is the `field` format above, the document's `field:` prose served as its brief
# NEXT is ENGINE vocabulary too -- a document leaving with several successors (`next:`)
# and a `choose:` prose injects it at its exit (a written one refuses at parse:
# next-keyword); the agent sees an ordinary PICK whose OPTIONS are the names of `next:`


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
    answers `options`, a PROVE always `proof`; an INFER answers `free` unless its
    document declares better."""
    if keyword in ("PICK", "NEXT"):
        return "options"
    if keyword == "PROVE":
        return "proof"
    if keyword == "FIELD":
        return "field"
    return "free"
