"""The data of the conduction model -- what a text pp hands to the agent lets it READ, what each
form it may read MEANS, and what the agent does about it (design/conduction-model.md says the model;
this module is its source, read by the `model` adapter, by the campaign's sheet and by
`tests/adapters/semantics.py`).

Data alone: no behavior, no import of the engine but its messages (`engine/conductor/core/messages.py`,
read by path: the lines the ANSWERS name are the module's). Two tables never meet: the READINGS say, for the
TRAITS of a text (the channel it came on, its closing, the call under it, a fact, where its
INSTRUCTION lines stand, the channel the last step that is no last message hands a value by), the SET of forms the text may be -- a set of one reads, a set of several is
ambiguous, an empty set a hole, and no order settles it (since the batch la-main-et-les-clotures,
2026-10-28, every reading of the engine's texts names one form); the FORMS say, for each form and each
channel, the three concepts -- what the stack AWAITS, who OWES the next step, how the sequel COMES --
and the ONE act they lead to. The state lives with the form, never with the text. The ZONES are the closed
list of the situations of the conduction a run crosses (batch le-recensement-et-la-table, 2026-10-29): the
campaign reads each one from the events of a run's trace, on its one channel -- the house conducts --, and the
census of the model's document counts the tests by zone; `root` is a zone of a LINE of the sheet (the root at
its end), never of the conduction."""
from __future__ import annotations

import importlib.util
from pathlib import Path


def _messages():
    """-> the engine's lines, read where they are written: `core/messages.py`, depending on nothing."""
    path = Path(__file__).resolve().parent.parents[1] / "engine" / "conductor" / "core" / "messages.py"
    spec = importlib.util.spec_from_file_location("pp_model_messages", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


messages = _messages()

# --- the three concepts, each an enumeration -------------------------------------------------
AWAITS = ("production", "message", "nothing")   # what the stack awaits after this text
OWES = ("agent", "principal", "nobody")          # who owes the next step
COMES = ("tool", "turn", "none")                 # how the sequel reaches the agent: in the result of
                                                 # the call it types, at its next turn, or never

# --- the six acts -----------------------------------------------------------------------------
ACTIONS = {
    "CALL": "type the call owed: the one the closing shows, or the one the channel of the step names, the production due on it",
    "SAY_CALL": "hand the productions the `=> terminal` lines ask, each by its print call, then type the call",
    "SAY_HAND_BACK": "hand the productions the `=> terminal` lines ask, each by its print call, then say `...` and hand back",
    "HAND_BACK": "say `...` -- the last message, which pp never reads -- and hand back",
    "STOP": "tell the principal what the refusal says, then hand back: nothing plays until their word",
    "READ_ON": "read it, go on with the step that stands",
}
# The ORDER of a launch, whatever the acts it chains: the productions `=> terminal` as their texts are
# read, each handed by its print call (`-print <DOCUMENT>`, the production piped), the calls owed, then -- where
# the launch hands back -- its last message, said ONCE and last, which pp never reads: every production the
# principal reads goes by its print call. A text never says it twice, and an answer to a call (a held
# line, a bounce) hands back on it. One text is read before its `=> terminal` productions are due: a
# chunk before the last. Its lines are kept, and their productions said once the output is whole, before
# those of the last chunk.

# --- the six forms: who owes what when the text is read, the state and the act per channel ------
# channel `tool`: the text reached the agent in the result of its own call (a view, a manual, an inline
# answer -- a block brought back with its deviation); channel `prompt`: the text is the prompt of a launch.
FORMS = {
    "V": {"what": "a value is due to the tool: a proof, a field, a choice, a production a consumer takes",
          "tool": {"awaits": "production", "owes": "agent", "comes": "tool", "act": "CALL"},
          "prompt": {"awaits": "production", "owes": "agent", "comes": "tool", "act": "CALL"}},
    "T": {"what": "a production is due to the principal, said by the agent, then the run moves on",
          "tool": {"awaits": "production", "owes": "agent", "comes": "tool", "act": "SAY_CALL"},
          "prompt": {"awaits": "production", "owes": "agent", "comes": "turn", "act": "SAY_HAND_BACK"}},
    "M": {"what": "a message of the principal is due: the root of the passage is exhausted",
          "tool": {"awaits": "message", "owes": "principal", "comes": "turn", "act": "SAY_HAND_BACK"},
          "prompt": {"awaits": "message", "owes": "principal", "comes": "turn", "act": "SAY_HAND_BACK"}},
    "S": {"what": "a decision of the principal is due: a refusal stopped the conduction -- a row of ANSWERS "
                  "may say what the run awaits then (`repair-exhausted`: a message, the run stopped on its step)",
          "tool": {"awaits": "nothing", "owes": "principal", "comes": "turn", "act": "STOP"},
          "prompt": {"awaits": "nothing", "owes": "principal", "comes": "turn", "act": "STOP"}},
    "R": {"what": "a reading continues: the rest of an output started comes next",
          "tool": {"awaits": "nothing", "owes": "agent", "comes": "tool", "act": "CALL"},
          "prompt": {"awaits": "nothing", "owes": "nobody", "comes": "turn", "act": "HAND_BACK"}},
    "D": {"what": "the answer to this call is elsewhere: its output comes by the other channel, or was served already",
          "tool": {"awaits": "production", "owes": "agent", "comes": "turn", "act": "READ_ON"},
          "prompt": {"awaits": "production", "owes": "agent", "comes": "turn", "act": "READ_ON"}},
}

# --- the zones of the conduction: the situations a run crosses, each read from its trace by the campaign ---
# A closed list, in the order the census prints them; `ZONES_READ` is the day the list was last read on the
# engine (every zone a situation the engine renders, none it does not). Each zone says WHAT it is; every zone
# is a situation of the conduction of the principal, the campaign's one channel. The campaign's `ZONE_EVENTS`
# is keyed on exactly these names and refuses `zones-mismatch` otherwise; a zone is `measured` when crossed.
ZONES_READ = "2026-11-21"
ZONES = {
    "boot": {"what": "the first output of a run, opened by `-new`"},
    "free-step": {"what": "an output that ends on a free step (`WORK`, `INFER`) the agent says, and waits for it"},
    "fusion": {"what": "several steps in one output, in one segment while the laws in force stay the same"},
    "section-break": {"what": "an output closed at a `§` of the author, the marked step opening the next call"},
    "chunk": {"what": "an output cut under a cap and served in pieces"},
    "held-output": {"what": "an output held for the next launch, the call that produced it answered by a held line"},
    "value-judged": {"what": "an output opened by the answer to a value handed (a proof, a field, a choice)"},
    "mount": {"what": "an output opened by a document mounted during the run"},
    "door": {"what": "a document entered by its door, or opened by `-s <name>`"},
    "space": {"what": "an output opened or closed by `-open` / `-close`"},
    "compaction": {"what": "the run served back after a declared compaction"},
    "renewal": {"what": "a run renewed by an upgrade, reopened on its boot"},
    "reseat": {"what": "a run taken up on the steps of a document rewritten during its last passage, nothing replayed"},
    "bounce": {"what": "a call that moves the run while an output waits, answered `not played`"},
    "bare-call": {"what": "the bare keyed call where a value is due, or the principal's own bare call"},
    "soft-catch": {"what": "a production due to the principal handed to the tool, answered by a fact, nothing recorded"},
    "offer-absent": {"what": "a name the step does not offer, the pending block brought back"},
    "package-switch": {"what": "a package switched off or on for the run"},
    "stopping-refusals": {"what": "a refusal that stops the conduction (`repair-exhausted`, `exec-refused`, `artifact-stale`)"},
    "launcher-bound": {"what": "the launcher's bound reached (`--launches`), the exchange stopped there"},
    "lap": {"what": "a lap of a turning door (`field:`, `cycle:`)"},
    "proof": {"what": "the answer to a `PROVE`"},
    "next": {"what": "a successor elected at `PICK next`"},
    "repair": {"what": "a step replayed after a miss, or fixed in place"},
    "inline": {"what": "a replay that asks the agent a value -- a block it has read, its deviation said -- answered in its tool result under the principal's conduction"},
    "advance": {"what": "the principal's launcher moving the run on"},
    "print": {"what": "a production said to the principal, handed by its print call and captured as handed"},
    "print-refused": {"what": "a print refused on the form of its step, still due"},
    "print-waived": {"what": "a print the bound lifted without a capture, the run going on"},
}


# --- the traits of a text: what the reader takes from the text alone -----------------------------
# `channel`: tool | prompt; `closing`: the word after the arrow, "" when the text ends on its matter;
# `call`: what stands under the closing -- the `bare` keyed call, the call that carries the
# principal's `message`, "" for none (no closing, or the AWAIT of a prompt); `fact`: the
# fact of the foot -- `reading` (a reading continues), "" for none; `instructed`: where the
# INSTRUCTION lines stand -- `last` (the last segment carries one: the step the text asks), `earlier`
# (an earlier segment carries one, the last none: steps said, then an order block under other laws),
# `none` (no segment carries one: no line, or a line under no heading -- the last chunk of a cut output);
# `due`: the channel the last INSTRUCTION line of the text that is no last message hands a value by --
# `tool` (on the call), `tool_heredoc` (piped by a heredoc) --, "" when that line hands none or the text
# carries no such line: a value due is read on the step's own line, wherever its heading stands (the
# last chunk of a cut output carries the line and no heading), no closing repeats its call, and the line
# `=> response` that may stand behind it (the last message the output asks) never hides it.
TRAITS = ("channel", "closing", "call", "fact", "instructed", "due")
ANY = "*"                                        # a trait a reading does not look at

# --- the readings: the traits of a text -> the forms it may be ------------------------------------
# One reading per distinct text the engine renders; the forms are the ones that render that text.
READINGS = (
    # the tool channel: a value due ends on its step, whose line names the channel the value is handed by;
    # every other output carries a closing, a chunk of a view the bare call alone
    {"channel": "tool", "closing": "", "call": "", "fact": ANY, "instructed": ANY, "due": "tool", "forms": ("V",)},
    {"channel": "tool", "closing": "", "call": "", "fact": ANY, "instructed": ANY, "due": "tool_heredoc", "forms": ("V",)},
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "reading", "instructed": ANY, "due": ANY, "forms": ("R",)},
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "", "instructed": "last", "due": "", "forms": ("T",)},
    # the bare call under CONTINUE with no fact and no step in the last segment: the closing of a free step
    # at a section break (the step's line in an earlier segment or an earlier chunk); a chunk of a view or
    # of an inline answer carries its fact (R, above) since the batch la-main-et-les-clotures (2026-10-28)
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "", "instructed": "earlier", "due": "", "forms": ("T",)},
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "", "instructed": "none", "due": "", "forms": ("T",)},
    {"channel": "tool", "closing": "AWAIT", "call": "message", "fact": ANY, "instructed": ANY, "due": ANY, "forms": ("M",)},
    # a block with no closing and no value due in a tool result: the view of the block that stands, nothing moved
    {"channel": "tool", "closing": "", "call": "", "fact": ANY, "instructed": ANY, "due": "", "forms": ("D",)},
    # the prompt channel: a closing says a chunk before the last (MORE, its fact) or a passage over (AWAIT,
    # no call under it: the launcher carries the next message); a text with no closing ends on its matter --
    # a value due on its step's line, or a free step pending, wherever its line stands: in the last segment,
    # in an earlier one (an order block under other laws closes the output), under no heading (the last
    # chunk of a cut output)
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": ANY, "due": "tool", "forms": ("V",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": ANY, "due": "tool_heredoc", "forms": ("V",)},
    {"channel": "prompt", "closing": "MORE", "call": "", "fact": "reading", "instructed": ANY, "due": ANY, "forms": ("R",)},
    {"channel": "prompt", "closing": "AWAIT", "call": "", "fact": ANY, "instructed": ANY, "due": ANY, "forms": ("M",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": "last", "due": "", "forms": ("T",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": "earlier", "due": "", "forms": ("T",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": "none", "due": "", "forms": ("T",)},
)


def reading_of(found: dict) -> dict | None:
    """-> the ONE reading whose traits match `found` (a mapping of TRAITS), None when no reading
    names such a text -- a hole. A reading's `*` matches any value of the trait."""
    for one in READINGS:
        if all(one[name] in (ANY, found.get(name, "")) for name in TRAITS):
            return one
    return None


def ambiguous() -> list[dict]:
    """-> the readings that admit several forms: the texts the engine renders alike for different
    states -- what the sheet marks red, what the data say and no order settles."""
    return [one for one in READINGS if len(one["forms"]) > 1]


# --- the answers to a call: a line, a bounce, a refusal, read in the tool result ------------------
# `said` is the engine's own text after `pp: ` (a held line, the bounce) or the refusal's code; the
# form and the act are the ones the line leads to on the tool channel. A gesture is read by its anchor
# line, or -- on an output of one segment, where the engine renders none -- by the call typed: the
# result of a script's call that carries no line of pp is the script's own output.
ANSWERS = {
    "value-judged": {"said": messages.unsaid(messages.held("value")), "kind": "held", "form": "D", "act": "READ_ON"},
    "mounted": {"said": messages.unsaid(messages.held("mount")), "kind": "held", "form": "D", "act": "READ_ON"},
    "opened": {"said": messages.unsaid(messages.held("door")), "kind": "held", "form": "D", "act": "READ_ON"},
    "closed": {"said": messages.unsaid(messages.held("closed")), "kind": "held", "form": "D", "act": "READ_ON"},
    "re-served": {"said": messages.unsaid(messages.held("compacted")), "kind": "held", "form": "D", "act": "READ_ON"},
    "reopened": {"said": messages.unsaid(messages.held("reopened")), "kind": "held", "form": "D", "act": "READ_ON"},
    "held-open": {"said": messages.unsaid(messages.opened("opened")), "kind": "held", "form": "D", "act": "READ_ON"},
    # the answers to a print call: the production was taken -- other calls are due (the next print, the
    # value the output awaits), or the last message alone remains; a print that was the last due of an
    # output closed on its prints is answered by the next block, read as any text
    "printed-more": {"said": messages.unsaid(messages.acknowledged(messages.PRINTED["more"], messages.NEXT)), "kind": "printed", "form": "D", "act": "READ_ON"},
    "printed-last": {"said": messages.unsaid(messages.printed("last")), "kind": "printed", "form": "D",
                     "act": "HAND_BACK"},
    # a print refused at the bound: nothing kept, the debt lifted -- the agent goes on with what stands
    "printed-waived": {"said": messages.unsaid(messages.printed("waived")),
                       "kind": "printed", "form": "D", "act": "READ_ON"},
    "bounce": {"said": messages.unsaid(messages.bounced()), "kind": "bounce", "form": "D", "act": "HAND_BACK"},
    "chunk-pending": {"said": messages.CHUNK_PENDING, "kind": "bounce", "form": "D", "act": "HAND_BACK"},
    "principal-advances": {"said": "principal-advances", "kind": "refusal", "form": "D", "act": "HAND_BACK"},
    "repair-exhausted": {"said": "repair-exhausted", "kind": "refusal", "form": "S", "act": "STOP",
                         "awaits": "message"},   # the run STOPS on its step: the principal's word takes it up
    "exec-refused": {"said": "exec-refused", "kind": "refusal", "form": "S", "act": "STOP"},
    "artifact-stale": {"said": "artifact-stale", "kind": "refusal", "form": "S", "act": "STOP"},
    "gesture": {"said": messages.framed(messages.ANCHOR, messages.VOICE), "kind": "served", "form": "D",
                "act": "READ_ON"},
    "refusal": {"said": messages.unsaid(messages.REFUSED).split()[0], "kind": "refusal", "form": "D",
                "act": "READ_ON"},
}

# --- the strategies: the conforming production the modelled LLM renders -------------------------
# by keyword: which form rules the production (`line` says the form the INSTRUCTION line names);
# by form: a production that holds the form's definition of `output.md`. A form the instance
# declares and the engine does not (`said`, `choices`, `team-act`…) renders the `any` strategy.
# A free production CITES what the model read: the template's fields name the DOCUMENT and the
# KEYWORD of the step, the titles SERVED (every `INFORMATION — <title>` of the block, `nothing` when
# none) and the ELEMENT of the lap (empty when the step serves none); the harness fills them. A
# proof's evidence names its code the same way. The imposed forms (`options`, `field`, `list`) cite
# nothing: their value is the engine's to judge.
STRATEGIES = {
    "keywords": {
        "PICK": {"form": "options"},
        "NEXT": {"form": "options"},
        "PROVE": {"form": "proof"},
        "FIELD": {"form": "field"},
        "INFER": {"form": "line"},
        "WORK": {"form": "line"},
    },
    "forms": {
        "any": {"mode": "stdin", "production": "{document} {keyword} · read {served} · {element}"},
        "empty": {"mode": "words", "production": "..."},
        "line": {"mode": "inline", "production": "{document} {keyword} · read {served} · {element}"},
        "options": {"mode": "inline", "production": "the first value of the closed list the step chooses from"},
        "json": {"mode": "stdin",
                 "production": '{{"document": "{document}", "keyword": "{keyword}", "served": "{served}", "element": "{element}"}}'},
        "table": {"mode": "stdin",
                  "production": "**{document} {keyword}**\n\n| part | value |\n|---|---|\n| served | {served} |\n| element | {element} |"},
        "free": {"mode": "stdin",
                 "production": "## {document} {keyword}\n\n| part | value |\n|---|---|\n| served | {served} |\n| element | {element} |"},
        "proof": {"mode": "stdin", "verdict": "ok", "evidence": "{document} {keyword} on {code}: modelled, no rendering"},
        "field": {"mode": "stdin", "production": '["one", "two", "three"]'},
        "list": {"mode": "stdin", "production": '["one", "two"]'},
    },
}
