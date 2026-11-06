"""Scenario `semantics` -- 7 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batches
le-modele-de-la-conduction, la-feuille-de-reponse and le-masque-et-le-contenu, 2026-10-27/28): the DATA of the conduction model,
`adapters/model/semantics.py`, cover the engine's constants -- what the case compares is read from the data
and from the engine's modules, never from the design document:
- the data load as a module of their own: no module of the engine among their imports (`language` at
  most), and the seven tables stand -- ACTIONS, FORMS, READINGS, ANSWERS, STRATEGIES, TRAITS, ZONES (the closed
  list of the zones of the conduction, each worded and each with the channels it exists on, within CHANNELS,
  dated by `ZONES_READ`, `root` out of it: a zone of a line of the sheet, never of the conduction; batch
  les-zones-muettes, 2026-10-29); no FEET, no row marked `proposed`: the data say what the engine renders,
  nothing it does not
- the table of READINGS is keyed by the TRAITS of a text alone (channel, closing, call, fact, where the
  INSTRUCTION lines stand) and renders a SET of candidate forms, never a state: every closing word of
  `language` (CONTINUE, AWAIT) has a reading, every reading names forms of FORMS, no two readings share
  the same traits (a text has exactly one reading), and no reading is empty
- every form of FORMS carries, on both channels, the three concepts in their enumerations and exactly ONE
  act of ACTIONS; every form stands in at least one reading or one answer
- `ACTIONS["HAND_BACK"]` says `...`: an agent with nothing to say answers three dots (the harness relaunches on
  an empty message), and `tools/campaign/campaign.py conforming()` takes words on HAND_BACK
- every line of `Conductor.HELD_SAID`, the bounce (`pp._HELD_BOUNCE`), `chunk-pending`,
  `principal-advances` and the refusals that stop the conduction (`repair-exhausted`, `exec-refused`,
  `artifact-stale`) have an answer, each on a form of FORMS and an act of ACTIONS
- every keyword of `language.YIELDING` and every form of `FORMATS`, `IMPOSED`, `LISTS` have a strategy
- the strategies CITE: the production of every free form (`any`, `line`, `json`, `table`, `free`) is a template
  whose fields name the document, the keyword and the titles served (`string.Formatter` reads the fields; no
  sentence is compared), the proof's evidence a template naming its code; no template is a constant
- a text whose traits no reading names is a hole, and the readings that admit several forms are listed by
  the data themselves (`ambiguous()`): the ambiguity is the data's to say, never an order's to settle; since
  the batch la-main-et-les-clotures (2026-10-28) every reading names ONE form: a chunk at the prompt closes
  on `MORE` and reads R alone, a prompt text with no closing and no instruction reads M alone, and by the
  tool a chunk carries its fact (R) where a free step at a section break carries none (T)
"""
from __future__ import annotations

import ast
import importlib.util
import re
import string
from pathlib import Path

from conductor import Conductor
from conductor.core import language

STOPPING = ("repair-exhausted", "exec-refused", "artifact-stale")   # the refusals that stop the conduction
CITING = ("any", "line", "json", "table", "free")                   # the free forms, whose production cites
CITED = {"document", "keyword", "served"}                            # what every citing template names
BOUNCES = ("chunk-pending", "principal-advances")                  # the console's own answers to a call
CHANNELS = ("tool", "prompt")


def loaded(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    source = bench.source()
    data = source / "adapters" / "model" / "semantics.py"

    # --- the data load, engine-free, the six tables, nothing proposed -----------------------
    if not data.is_file():
        failures.append(f"  ✗ data absent                {data}")
        return 0
    tree = ast.parse(data.read_text(encoding="utf-8"))
    imported = sorted({(node.module or "") if isinstance(node, ast.ImportFrom) else node.names[0].name
                       for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))})
    foreign = [one for one in imported if one.startswith("conductor") and not one.endswith("language")]
    semantics = loaded(data, "semantics")
    tables = ("ACTIONS", "FORMS", "READINGS", "ANSWERS", "STRATEGIES", "TRAITS", "ZONES")
    standing = [one for one in tables if hasattr(semantics, one)]
    gone = [one for one in ("FEET",) if hasattr(semantics, one)]
    proposed = [one for one in getattr(semantics, "READINGS", ()) if isinstance(one, dict) and one.get("proposed")]
    zones = dict(getattr(semantics, "ZONES", {}) or {})
    dated = re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(getattr(semantics, "ZONES_READ", "")))
    channels = tuple(getattr(semantics, "CHANNELS", ()))
    worded = all(isinstance(spec, dict) and isinstance(spec.get("what"), str) and spec["what"].strip()
                 and spec.get("channels") and set(spec["channels"]) <= set(channels) for spec in zones.values())
    narrowed = sorted(zone for zone, spec in zones.items() if worded and tuple(spec["channels"]) != channels)
    if (not foreign and standing == list(tables) and not gone and not proposed
            and zones and worded and len(channels) == 3 and narrowed and "root" not in zones and dated):
        held("the data load, engine-free", f"imports {imported or 'none'}; the seven tables stand; ZONES: "
             f"{len(zones)} zones, each worded and on its channels (within {channels}; {len(narrowed)} on fewer than "
             f"the three: {', '.join(narrowed)}), read on {semantics.ZONES_READ}, `root` out of it; no FEET, nothing proposed")
    else:
        failures.append(f"  ✗ data load                  foreign={foreign} standing={standing} gone={gone} "
                        f"proposed={len(proposed)} zones={len(zones)} worded={worded} channels={channels} "
                        f"narrowed={narrowed} dated={bool(dated)}")
        return 0
    actions, forms = set(semantics.ACTIONS), semantics.FORMS
    readings, answers, traits = semantics.READINGS, semantics.ANSWERS, semantics.TRAITS

    # --- the readings: keyed by the traits of a text, a set of forms each ---------------------
    closings = [language.CONTINUE, language.AWAIT, language.MORE]
    keys = [tuple(one.get(name) for name in traits) for one in readings]
    doubled = sorted({key for key in keys if keys.count(key) > 1})
    empty = [one for one in readings if not one.get("forms")]
    unformed = sorted({form for one in readings for form in one["forms"] if form not in forms})
    footed = {word: [one for one in readings if one.get("closing") == word] for word in closings}
    unknown = sorted({one["closing"] for one in readings if one.get("closing") and one["closing"] not in closings})
    off_channel = [one for one in readings if one.get("channel") not in CHANNELS]
    stateful = [one for one in readings if any(name in one for name in ("awaits", "owes", "comes", "act"))]
    if (all(footed[word] for word in closings) and not doubled and not empty and not unformed and not unknown
            and not off_channel and not stateful):
        held("the readings are keyed by the traits of a text", f"{len(readings)} readings on {traits}; "
             f"{closings} read; no two share their traits; every form one of {sorted(forms)}; no state in a reading")
    else:
        failures.append(f"  ✗ readings                   doubled={doubled} empty={len(empty)} unformed={unformed} "
                        f"unknown={unknown} off_channel={len(off_channel)} stateful={len(stateful)}")

    # --- the forms: three concepts and one act, per channel -----------------------------------
    concepts = {"awaits": set(semantics.AWAITS), "owes": set(semantics.OWES), "comes": set(semantics.COMES)}
    off = []
    for name, form in forms.items():
        for channel in CHANNELS:
            state = form.get(channel) or {}
            if any(state.get(concept) not in values for concept, values in concepts.items()) \
                    or state.get("act") not in actions:
                off.append((name, channel))
    read_forms = {form for one in readings for form in one["forms"]} | {one["form"] for one in answers.values()}
    unread = sorted(set(forms) - read_forms)
    if not off and not unread and len(actions) == 6:
        held("three concepts, one act, per form and channel", f"{len(forms)} forms x {len(CHANNELS)} channels, each "
             f"in the three enumerations, each on one of the {len(actions)} acts; every form read or answered")
    else:
        failures.append(f"  ✗ forms                      off={off} unread={unread}")

    # --- nothing to say is said `...` ---------------------------------------------------------
    campaign = loaded(source / "tools" / "campaign" / "campaign.py", "pp_campaign")
    silent = {"words": [], "calls": []}
    dotted = {"words": ["..."], "calls": []}
    moved = {"words": ["..."], "calls": ["bare"]}
    if ("..." in semantics.ACTIONS["HAND_BACK"] and campaign.conforming("HAND_BACK", silent)
            and campaign.conforming("HAND_BACK", dotted) and not campaign.conforming("HAND_BACK", moved)):
        held("nothing to say is said `...`", "HAND_BACK names the three dots; conforming() takes silence or words "
             "on HAND_BACK and refuses a call that moves the run")
    else:
        failures.append(f"  ✗ the dots                   act={semantics.ACTIONS['HAND_BACK']!r} "
                        f"{campaign.conforming('HAND_BACK', silent)}/{campaign.conforming('HAND_BACK', dotted)}/"
                        f"{campaign.conforming('HAND_BACK', moved)}")

    # --- every answer of the engine has a line ---------------------------------------------
    console = loaded(source / "engine" / "pp.py", "pp_console")
    bounce = console._HELD_BOUNCE.split(": ", 1)[1]
    owed = (*Conductor.HELD_SAID.values(), bounce, *BOUNCES, *STOPPING)
    said = {one["said"] for one in answers.values()}
    missing = [one for one in owed if one not in said]
    off_answers = [name for name, one in answers.items() if one.get("form") not in forms or one.get("act") not in actions]
    if not missing and not off_answers:
        held("every answer of the engine has a line", f"{len(owed)} owed: the held lines, the bounce, "
             f"the console's two, the {len(STOPPING)} stopping refusals; each on a form and an act")
    else:
        failures.append(f"  ✗ answers                    missing={missing} off={off_answers}")

    # --- the refusal that parks carries the slot's state --------------------------------------
    others = [code for code in STOPPING if code != "repair-exhausted" and "awaits" in answers.get(code, {})]
    if answers.get("repair-exhausted", {}).get("awaits") == "message" and not others:
        held("the repair bound parks", "`repair-exhausted` awaits a message of its own; the two other stopping "
             "refusals keep the form's state")
    else:
        failures.append(f"  ✗ the bound's await          {answers.get('repair-exhausted')} others={others}")

    # --- every keyword and every form has a strategy ----------------------------------------
    strategies = semantics.STRATEGIES
    keywords = sorted(language.YIELDING)
    engine_forms = sorted(set(language.FORMATS) | set(language.IMPOSED) | set(language.LISTS))
    no_keyword = [one for one in keywords if one not in strategies["keywords"]]
    no_form = [one for one in engine_forms if one not in strategies["forms"]]
    if not no_keyword and not no_form:
        held("every keyword and form has a strategy", f"{len(keywords)} keywords, {len(engine_forms)} forms")
    else:
        failures.append(f"  ✗ strategies                 keywords={no_keyword} forms={no_form}")

    # --- the strategies cite ------------------------------------------------------------------
    def fields_of(template: str) -> set[str]:
        return {name for _, name, _, _ in string.Formatter().parse(template) if name}

    productions = {form: strategies["forms"].get(form, {}).get("production", "") for form in CITING}
    uncited = [form for form, text in productions.items() if not CITED <= fields_of(str(text))]
    evidence = strategies["forms"].get("proof", {}).get("evidence", "")
    if not uncited and {"code", "document"} <= fields_of(str(evidence)):
        held("the strategies cite", f"{len(CITING)} free forms name {sorted(CITED)} in their template; the proof's "
             f"evidence names {sorted(fields_of(str(evidence)))}")
    else:
        failures.append(f"  ✗ strategies cite            uncited={uncited} evidence={sorted(fields_of(str(evidence)))}")

    # --- the ambiguity is the data's to say, and the data say none ------------------------------
    ambiguous = semantics.ambiguous()
    listed = [one for one in readings if len(one["forms"]) > 1]
    ended = {"channel": "prompt", "closing": "", "call": "", "fact": "", "instructed": "none"}
    more = {"channel": "prompt", "closing": language.MORE, "call": "", "fact": "reading", "instructed": "none"}
    broken = {"channel": "tool", "closing": language.CONTINUE, "call": "bare", "fact": "", "instructed": "earlier"}
    chunked = {"channel": "tool", "closing": language.CONTINUE, "call": "bare", "fact": "reading", "instructed": "none"}
    forms_of = lambda traits: tuple((semantics.reading_of(traits) or {}).get("forms", ()))   # noqa: E731
    nowhere = semantics.reading_of({**ended, "closing": "ELSEWHERE"})
    if (ambiguous == listed == [] and forms_of(ended) == ("M",) and forms_of(more) == ("R",)
            and forms_of(broken) == ("T",) and forms_of(chunked) == ("R",) and nowhere is None):
        held("every text reads one form", "no ambiguous reading left: at the prompt no closing and no instruction "
             "reads M, MORE and its fact R; by the tool the bare call with the fact reads R, without it T; "
             "unknown traits read nothing")
    else:
        failures.append(f"  ✗ ambiguity                  ambiguous={len(ambiguous)} ended={forms_of(ended)} "
                        f"more={forms_of(more)} broken={forms_of(broken)} chunked={forms_of(chunked)} nowhere={nowhere}")
    return 0
