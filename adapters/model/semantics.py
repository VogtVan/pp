"""The data of the conduction model -- what a text pp hands to the agent lets it READ, what each
form it may read MEANS, and what the agent does about it (design/conduction-model.md says the model;
this module is its source, read by the `model` adapter, by the campaign's sheet and by
`tests/adapters/semantics.py`).

Data alone: no behavior, no import of the engine. Two tables never meet: the READINGS say, for the
TRAITS of a text (the channel it came on, its closing, the call under it, a fact, where its
INSTRUCTION lines stand), the SET of forms the text may be -- a set of one reads, a set of several is
ambiguous, an empty set a hole, and no order settles it (since the batch la-main-et-les-clotures,
2026-10-28, every reading of the engine's texts names one form); the FORMS say, for each form and each
channel, the three concepts -- what the stack AWAITS, who OWES the next step, how the sequel COMES --
and the ONE act they lead to. The state lives with the form, never with the text. The ZONES are the closed
list of the situations of the conduction a run crosses (batch le-recensement-et-la-table, 2026-10-29), each
with the CHANNELS where it exists (batch les-zones-muettes, the same day): the campaign reads each one from the
events of a run's trace and the census of the model's document counts the tests by zone, on the zone's own
channels; `root` is a zone of a LINE of the sheet (the root at its end), never of the conduction."""
from __future__ import annotations

# --- the three concepts, each an enumeration -------------------------------------------------
AWAITS = ("production", "message", "nothing")   # what the stack awaits after this text
OWES = ("agent", "principal", "nobody")          # who owes the next step
COMES = ("tool", "turn", "none")                 # how the sequel reaches the agent: in the result of
                                                 # the call it types, at its next turn, or never

# --- the six acts -----------------------------------------------------------------------------
ACTIONS = {
    "CALL": "type the call the closing shows, the production due in its place when one is due",
    "SAY_CALL": "say the productions the INSTRUCTION lines ask, then type the call",
    "SAY_HAND_BACK": "say the productions the INSTRUCTION lines ask, then hand back",
    "HAND_BACK": "say `...` -- nothing is due -- and hand back",
    "STOP": "tell the principal what the refusal says, then hand back: nothing plays until their word",
    "READ_ON": "read it, go on with the step that stands",
}

# --- the six forms: who owes what when the text is read, the state and the act per channel ------
# channel `tool`: the text reached the agent in the result of its own call (the LLM's mode, a view,
# an inline answer under `hybrid`); channel `prompt`: the text is the prompt of a launch.
FORMS = {
    "V": {"what": "a value is due to the tool: a proof, a field, a choice, a production a consumer takes",
          "tool": {"awaits": "production", "owes": "agent", "comes": "tool", "act": "CALL"},
          "prompt": {"awaits": "production", "owes": "agent", "comes": "tool", "act": "CALL"}},
    "T": {"what": "a response is due in the agent's words, then the run moves on",
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
# engine (every zone a situation the engine renders, none it does not). Each zone says WHAT it is and the
# CHANNELS where it exists (batch les-zones-muettes, 2026-10-29): the three for most; the zones of the
# conduction of the principal -- a free step pending, a held output, the advance, a bounce, the launcher's
# bound, a renewal between two launches -- on the relayed channels alone, `inline` under hybrid alone. The
# campaign's `ZONE_EVENTS` is keyed on exactly these names and refuses `zones-mismatch` otherwise; a zone is
# `measured` when crossed on every channel it exists on, never on a channel it does not.
ZONES_READ = "2026-10-29"
CHANNELS = ("strict", "hybrid", "bare")           # the channels of the campaign: relayed strict, relayed hybrid, bare
PRINCIPAL_CHANNELS = ("strict", "hybrid")           # where a run is conducted by its principal (the house relays)
ZONES = {
    "boot": {"what": "the first output of a run, opened by `-new`",
            "channels": CHANNELS},
    "free-step": {"what": "an output that ends on a free step (`WORK`, `INFER => words`) and waits the agent's words",
                 "channels": PRINCIPAL_CHANNELS},
    "fusion": {"what": "several steps in one output, each a segment",
              "channels": CHANNELS},
    "section-break": {"what": "an output closed at a `§` of the author, the marked step opening the next call",
                     "channels": CHANNELS},
    "chunk": {"what": "an output cut under a cap and served in pieces",
             "channels": CHANNELS},
    "held-output": {"what": "an output held for the next launch, the call that produced it answered by a held line",
                   "channels": PRINCIPAL_CHANNELS},
    "value-judged": {"what": "an output opened by the answer to a value handed (a proof, a field, a choice)",
                    "channels": CHANNELS},
    "mount": {"what": "an output opened by a document mounted during the run",
             "channels": CHANNELS},
    "door": {"what": "a document entered by its door, or opened by `-s <name>`",
            "channels": CHANNELS},
    "space": {"what": "an output opened or closed by `-open` / `-close`",
             "channels": CHANNELS},
    "compaction": {"what": "the run served back after a declared compaction",
                  "channels": CHANNELS},
    "renewal": {"what": "a run renewed by an upgrade, reopened on its boot",
               "channels": PRINCIPAL_CHANNELS},
    "bounce": {"what": "a call that moves the run while an output waits, answered `not played`",
              "channels": PRINCIPAL_CHANNELS},
    "bare-call": {"what": "the bare keyed call where a value is due, or the principal's own bare call",
                 "channels": CHANNELS},
    "soft-catch": {"what": "a `=> words` production handed to the tool, answered by a fact, nothing recorded",
                  "channels": CHANNELS},
    "offer-absent": {"what": "a name the step does not offer, the pending block brought back",
                    "channels": CHANNELS},
    "package-switch": {"what": "a package switched off or on for the run",
                      "channels": CHANNELS},
    "stopping-refusals": {"what": "a refusal that stops the conduction (`repair-exhausted`, `exec-refused`, `artifact-stale`)",
                         "channels": CHANNELS},
    "launcher-bound": {"what": "the launcher's bound reached (`--launches`), the exchange stopped there",
                      "channels": PRINCIPAL_CHANNELS},
    "lap": {"what": "a lap of a turning door (`field:`, `cycle:`)",
           "channels": CHANNELS},
    "proof": {"what": "the answer to a `PROVE`",
             "channels": CHANNELS},
    "next": {"what": "a successor elected at `PICK next`",
            "channels": CHANNELS},
    "repair": {"what": "a step replayed after a miss, or fixed in place",
              "channels": CHANNELS},
    "inline": {"what": "an output answered in the agent's tool result under `conduction: hybrid`",
              "channels": ("hybrid",)},
    "advance": {"what": "the principal's launcher moving the run on",
               "channels": PRINCIPAL_CHANNELS},
}


# --- the traits of a text: what the reader takes from the text alone -----------------------------
# `channel`: tool | prompt; `closing`: the word after the arrow, "" when the text ends on its matter;
# `call`: what stands under the closing -- `template` (the form's name where the production goes),
# the `bare` keyed call, the call that carries the principal's `message`, "" for none; `fact`: the
# fact of the foot -- `reading` (a reading continues), "" for none; `instructed`: where the
# INSTRUCTION lines stand -- `last` (the last segment carries one: the step the text asks), `earlier`
# (an earlier segment carries one, the last none: steps said, then the root at its end), `none`.
TRAITS = ("channel", "closing", "call", "fact", "instructed")
ANY = "*"                                        # a trait a reading does not look at

# --- the readings: the traits of a text -> the forms it may be ------------------------------------
# One reading per distinct text the engine renders; the forms are the ones that render that text.
READINGS = (
    # the tool channel: every output carries a closing, a chunk of a view carries the bare call alone
    {"channel": "tool", "closing": "CONTINUE", "call": "template", "fact": ANY, "instructed": ANY, "forms": ("V",)},
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "reading", "instructed": ANY, "forms": ("R",)},
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "", "instructed": "last", "forms": ("T",)},
    # the bare call under CONTINUE with no fact and no step in the last segment: the closing of a free step
    # at a section break (the step's line in an earlier segment or an earlier chunk); a chunk of a view or
    # of an inline answer carries its fact (R, above) since the batch la-main-et-les-clotures (2026-10-28)
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "", "instructed": "earlier", "forms": ("T",)},
    {"channel": "tool", "closing": "CONTINUE", "call": "bare", "fact": "", "instructed": "none", "forms": ("T",)},
    {"channel": "tool", "closing": "AWAIT", "call": "message", "fact": ANY, "instructed": ANY, "forms": ("M",)},
    # a block with no closing in a tool result: the view of the block that stands, nothing moved
    {"channel": "tool", "closing": "", "call": "", "fact": ANY, "instructed": ANY, "forms": ("D",)},
    # the prompt channel: a closing where a value is due and on a chunk before the last (MORE, its fact);
    # the rest ends on its matter -- a free step pending, or the root at its end
    {"channel": "prompt", "closing": "CONTINUE", "call": "template", "fact": ANY, "instructed": ANY, "forms": ("V",)},
    {"channel": "prompt", "closing": "MORE", "call": "", "fact": "reading", "instructed": ANY, "forms": ("R",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": "last", "forms": ("T",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": "earlier", "forms": ("M",)},
    {"channel": "prompt", "closing": "", "call": "", "fact": ANY, "instructed": "none", "forms": ("M",)},
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
# form and the act are the ones the line leads to on the tool channel.
ANSWERS = {
    "value-judged": {"said": "value judged", "kind": "held", "form": "D", "act": "READ_ON"},
    "mounted": {"said": "mounted", "kind": "held", "form": "D", "act": "READ_ON"},
    "opened": {"said": "opened", "kind": "held", "form": "D", "act": "READ_ON"},
    "closed": {"said": "closed", "kind": "held", "form": "D", "act": "READ_ON"},
    "re-served": {"said": "re-served", "kind": "held", "form": "D", "act": "READ_ON"},
    "reopened": {"said": "reopened", "kind": "held", "form": "D", "act": "READ_ON"},
    "bounce": {"said": "not played -- call already done", "kind": "bounce", "form": "D", "act": "HAND_BACK"},
    "chunk-pending": {"said": "chunk-pending", "kind": "bounce", "form": "D", "act": "HAND_BACK"},
    "principal-advances": {"said": "principal-advances", "kind": "refusal", "form": "D", "act": "HAND_BACK"},
    "repair-exhausted": {"said": "repair-exhausted", "kind": "refusal", "form": "S", "act": "STOP",
                         "awaits": "message"},   # the run STOPS on its step: the principal's word takes it up
    "exec-refused": {"said": "exec-refused", "kind": "refusal", "form": "S", "act": "STOP"},
    "artifact-stale": {"said": "artifact-stale", "kind": "refusal", "form": "S", "act": "STOP"},
    "gesture": {"said": "◀ pp", "kind": "served", "form": "D", "act": "READ_ON"},
    "refusal": {"said": "REFUSED", "kind": "refusal", "form": "D", "act": "READ_ON"},
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
        "line": {"mode": "inline", "production": "{document} {keyword} · read {served} · {element}"},
        "options": {"mode": "inline", "production": "the first value of OPTIONS"},
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
