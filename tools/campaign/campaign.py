#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""The CAMPAIGN -- a SET of procs played on a harness, modelled or real, its conduction measured.

A set is a directory: `campaign.yaml` at its root, and one sub-directory per ROOT of documents
(what `PP_DOCUMENTS` serves). The manifest says, per root, the door, the message, the manual
message, what to look at, and the INTENTION the modelled LLM plays (`model:`); and for the set its
accessories (`files:`, laid in the agent's workspace), its witness skills (`skills:`, copied into
the agent's instance), what an exchange leaves behind (`clean:`, removed before the next one) and what
an exchange may rewrite (`keep:`, put back before the next one as it stood when the house was laid). The
launcher names no root: the patterns are its first set
(`tests/conduction/roots`, the default of `--set`).

  campaign.py plan [--set <dir>] [--root <name>]...
                   [--provider <name>] [--model <m>] [--effort <e>]
                   [--repeat <n>] [--budget <usd>] [--launches <n>] [--out <dir>]
      -> writes one plan per root as JSON under
         `<out>` (`<set>/../out/dry` by default), each carrying its `repeat` and its `effort`;
         launches NOTHING (`launched: false`), consults no binary.
  campaign.py play [the same] [--house <dir>]
      -> installs a DISPOSABLE house of the product (`-install` on a mktemp, the `agent` package),
         gives birth to the set's agent, lays the accessories and the skills, says the BOUND of the
         cost (plans x repetitions x budget, the provider, the model, the effort), and plays each plan
         `--repeat` times on the same agent (a new run each time, the workspace cleaned between two),
         on the campaign's one channel, RELAYED: `agent run`, the house conducts, no setting of the agent
         written. The provider's binary is asked of its adapter (`BINARY`): `provider-missing` only when
         one is due and absent. Each exchange is bounded (`--budget` USD, `--launches`). What came back is
         kept under `<out>/<date>/<root>-relayed[#<k>]/` (`run.json`, `stdout.txt`, `stderr.txt`,
         `flow.jsonl`, `exchanges.json`, `stats.json`, `trace.jsonl`), the campaign itself under
         `<out>/<date>/campaign.json`, and the
         REPORT below written from those artifacts; the real cost, summed from the records, is said
         last.
  campaign.py prepare [--set <dir>] [--root <name>]... [--out <dir>] [--fresh]
      -> the OPERATOR's bench: one disposable house per root under `<out>`
         (`~/.local/share/pp-campaign/<set>/` by default), the set's agent born, the root's documents
         laid in its procs with an overlay of `TURN` that offers the door, Claude Code wired at the house,
         `ui` pinned.
  campaign.py runsheet [--set <dir>] [--out <dir>]
      -> the run sheet of the operator's bench, markdown on stdout.
  campaign.py sheet <date> [--out <dir>] [--mask <zone>[,<zone>…]|agent] [--against <date>]
  campaign.py sheet --house <ws> --agent <name> --run <key> --out <dir> [--mask …]
      -> the SHEET OF RESPONSE: one line per text pp handed to the agent -- a block, a chunk of it, a
         `pp:` line, a refusal, the result of a gesture --, read from the artifacts alone: the ORACLE
         from the run's trace (what the stack awaited after that text, who owed the next step, how the
         sequel came, the act due), the READER from the text alone (the candidate forms its traits admit
         in `adapters/model/semantics.py`, never settled), the OBSERVED from the flow (the words said,
         the call typed, the hand given back). The verdict per line: `vert`; `rouge-conduction` when the
         reader admits several forms, or one that is not the oracle's, or when the engine bounced a call
         that moves nothing (a gesture); `rouge-agent` when the observed act is not the reader's; `trou`
         when the reader admits none. Written as `sheet.json` and `SHEET.md` under `<out>/<date>/` by
         `play` and by `sheet <date>` (the same bytes on the same artifacts); `sheet --run` reads one run of
         a house (its flow and its trace, as `play` reads them) and writes under `<out>/<key>/`. Every line
         carries the ZONE of the oracle's item that handed its text (`chunk`, `held-output`, `bounce`, `door`,
         `value-judged`, `free-step`, `root`…); `--mask` names zones, or `agent` for the `rouge-agent` lines:
         a masked line keeps its verdict and carries `masked: true`, every count of the foot leaves it out and
         the masked lines are counted apart with their reds. The manifest's `expect:` (words, launches,
         parked, proofs, calls) is judged per exchange in the sheet's EXPECT table. `--against
         <date>` then writes `compare.json` and `COMPARE.md`: the lines of the two sheets paired by (exchange,
         channel, rank), the verdict before and after, the lines appeared and disappeared, the counts of each
         side by verdict and by zone; `sheet-missing` when a side has no sheet.
  campaign.py zones [--evidence <dir>] [--model <date>] [--real <date>]... [--doc <path>]
      -> the CENSUS of the conduction tests: reads the evidence alone -- by default the latest COMPLETE
         `model` campaign under `<evidence>` (`tests/conduction/evidence/campaigns`) (every root of its set played;
         of a campaign before 2026-11-21, only its exchanges on the relayed channel are read) and every real
         campaign standing there -- and writes, between the two markers `<!-- coverage:begin … -->` and
         `<!-- coverage:end -->` of the model's document (`design/conduction-model.md`), the coverage section:
         the model campaign, its date and the engine it played on, the real campaigns (provider, model,
         effort, engine, exchanges), then one row per zone of `semantics.ZONES` -- what it is, the roots
         that cross it under the model, the real exchanges that cross it on the same engine (and on an older
         one, apart), its STATUS: `safe` (crossed under the model, three real exchanges at least on the same
         engine, their lines without `rouge-conduction` nor `trou`), `measured` (crossed under the model),
         `silent` (never crossed) -- and the count by status. The section is inserted at the end of a document that carries none, replaced otherwise;
         nothing else of the document moves; no date of "now" is written: replayed on the same evidence, the
         same bytes. A campaign without `engine` in its `campaign.json`: `evidence-unversioned`; no complete
         model campaign: `model-missing`; a `ZONE_EVENTS` whose keys are not `ZONES`: `zones-mismatch`.
  campaign.py zones --check [--doc <path>]
      -> reads the begin marker of the section and says the engine the census was written on, its model
         campaign, its real campaigns and the zones `safe`; `engine-moved` when the engine in place is another
         (the campaigns are to be played again before a publication); `coverage-missing` without the section.
  campaign.py report <date> [--out <dir>]
      -> reads the artifacts kept under `<out>/<date>/` (`campaign.json`, each exchange's `run.json`
         and `stats.json`) and writes there `coverage.json` and `COVERAGE.md` -- the zones of the
         conduction crossed by each exchange, read from the run's trace, from `-stats -json`, from the
         flow and from the harness's lines --, `report.json` and `REPORT.md` -- one line per exchange
         (the run, the cost, the launches, the seconds, parked, the repairs, the refusals, the holes,
         the bounces, the values handed, the mass, the tokens) and, per root over its
         repetitions, the cost and the launches (mean, p90 at the nearest rank), the seconds, the
         passages finished, the deviations (repairs + refusals + holes + bounces), the held outputs,
         the inline outputs, the values and the CONFORMITY (values handed without a repair / values
         handed). Replayed on the same artifacts it renders the same bytes; `play` writes it too.
         No campaign at that date: `campaign-missing`.
  campaign.py turn --set <dir> --provider <name> [--variant <name>]... [--model <m>] [--effort <e>]
                   [--permissions <regime>] [--budget <usd>] [--repeat <n>] [--jobs <n>]
                   [--timeout <seconds>] [--out <dir>]
      -> ONE turn of a prompt on a harness, without pp nor house (`tools/campaign/turn.py`): each
         variant of the set's `turn.yaml` played `--repeat` times, `--jobs` repetitions at once. A
         variant names its prompts (each file is one launch, the next resumes the session) and its
         fixed part (`fixed:`, a file in the set or outside it), which goes to the system prompt or
         to the head of the first prompt. A repetition plays in a throwaway directory -- a git
         repository without a commit, the set's accessories, and a fake `./pp` that records what it
         receives and answers the held line of a value (`messages.held`) -- a print call, the line pp answers a print taken. Kept under `<out>/<date>/<variant>/<k>/`:
         `launch.json`, the prompt, the output and the errors of each launch, `events.jsonl`,
         `received.jsonl`, and a copy of the harness's own transcript where the adapter finds it.
         The table, `turn.json` and `TURN.md` under `<out>/<date>/`, is written again at every
         repetition that ends. A launch that lasts more than `--timeout` seconds (600) is killed.
         Renders 0 when no repetition ended on an error; 1 when one did (its row keeps the error and
         its cause, the others play); 130 when the play was interrupted (SIGINT, SIGTERM: the
         launches in flight are killed, the table says what played); 2 on a refusal.

Deterministic, refuses by name (exit 2, nothing played). Played from the repository root:
`uv run tools/campaign/campaign.py plan`."""
from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                  # the repository: tools/campaign/ -> root
ENGINE = ROOT / "engine" / "pp.py"
sys.path.insert(0, str(ROOT / "engine"))
from conductor.core import language, messages    # noqa: E402 -- the product's own faces
from conductor.core.errors import Refusal    # noqa: E402
from conductor.packaging import adapters   # noqa: E402
from conductor.state import log, persistence, settings   # noqa: E402
from conductor import VERSION   # noqa: E402 -- the engine that plays, written in the evidence

MANIFEST = "campaign.yaml"
DEFAULT_SET = ROOT / "tests" / "conduction" / "roots"      # the set of the situations, the conduction sector's
HOUSES = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "pp-campaign"
CHANNEL = "relayed"                             # the campaign's one channel: the house conducts
INTENT = "PP_MODEL_INTENT"                      # the intention of the modelled LLM, as its principal's message
HOST_CAP = "25000"                              # the template's cap of ONE tool result at the host
BUDGET, LAUNCHES, REPEAT = "2", "16", "1"
CAMPAIGN = "campaign.json"                      # what a play keeps of itself under <out>/<date>/: the report reads it
EVIDENCE = DEFAULT_SET.parent / "evidence" / "campaigns"   # tests/conduction/evidence/campaigns: the light artifacts kept in git
MODEL_DOC = ROOT / "design" / "conduction-model.md"        # the model's document, where the census is written
COVERAGE_BEGIN, COVERAGE_END = "<!-- coverage:begin", "<!-- coverage:end -->"   # the two markers of the section
PROVIDER_MODEL = "model"                        # the modelled LLM: cost 0, the census's model campaign
SAFE_REAL = 3                                   # the real exchanges a zone needs on the same engine to be `safe`
STATUSES = ("safe", "measured", "silent")
ROOT_KEYS = ("door", "message", "manual", "look", "model", "expect", "launches", "renew", "again", "open")
EXPECT_KEYS = ("words", "launches", "parked", "proofs", "calls")   # what a root's `expect:` may count
HOLE = "hole"
BARE_CALL = re.compile(r"^\S*pp [0-9a-f]{6}$")      # the bare keyed call, as the harness typed it
LAUNCHES_SPENT = "launches-spent"
KEPT = ".campaign-kept"                        # where `keep:` holds the first state of what an exchange may rewrite
RESUME_MESSAGE = "go on"                        # the message the second wake-up of a renewed exchange carries
BOUNCE = messages.bounced()      # the engine's own line of a bounce, read at the start of a line of a result                # what pp-agent says when its bound stops an exchange

# the ZONES of the conduction (adapters/model/semantics.py) and the events of a run's trace that say
# an exchange crossed them; a zone no event says is read elsewhere (`hole` from the harness's lines,
# `bounce` and `bare-call` from its tool results, `launcher-bound` from the agent's record)
ZONE_EVENTS = {
    "boot": ("new",),
    "free-step": ("pending",),
    "fusion": ("print-due",),                # a step said in the output, due to print from its close
    "section-break": ("section",),
    "chunk": ("cut", "chunk"),
    "held-output": ("held",),
    "value-judged": ("answer",),
    "mount": ("mounted",),
    "door": ("door", "routed"),
    "space": ("opened", "closed"),        # `opened` says the name the agent opened, `closed` the frame left
    "compaction": ("compacted",),
    "renewal": ("reopened", "renewed"),
    "reseat": ("reseated",),
    "bounce": (),                # answered by the console, never traced: read on the tool results
    "bare-call": (),
    "soft-catch": ("stray",),
    "offer-absent": ("offer-absent",),
    "package-switch": ("switch",),
    "stopping-refusals": ("refusal",),
    "launcher-bound": (),        # the launcher's own refusal (`launches-spent`), read on its stderr
    "lap": ("lap",),
    "proof": (),                 # the answers to a PROVE
    "next": ("next",),
    "repair": ("repair", "repair-in-place"),
    "inline": ("inline",),
    "advance": ("advance",),
    "print": (),                 # a production said to the principal, captured by its print call: read on `answer`
    "print-refused": (),         # a print refused on its form, still due: read on `repair-in-place` of a document
    "print-waived": ("print-waived",),       # a print the bound lifted without a capture
}


def semantics_module():
    """-> the data of the conduction model, `adapters/model/semantics.py`, loaded by path: the ZONES the
    census counts, the FORMS the sheet reads."""
    path = ROOT / "adapters" / "model" / "semantics.py"
    spec = importlib.util.spec_from_file_location("pp_model_semantics", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _zones_declared() -> dict:
    """-> `semantics.ZONES`; `zones-mismatch` when ZONE_EVENTS is not keyed on exactly those names."""
    zones = dict(semantics_module().ZONES)
    if list(ZONE_EVENTS) != list(zones):
        missing = [one for one in zones if one not in ZONE_EVENTS]
        extra = [one for one in ZONE_EVENTS if one not in zones]
        raise Refused("zones-mismatch", f"ZONE_EVENTS is not keyed on semantics.ZONES: missing {missing or 'none'}, "
                                        f"extra {extra or 'none'}, or another order")
    return zones


def turn_module():
    """-> the player of ONE turn, `tools/campaign/turn.py`, loaded by path: the verb `turn`."""
    spec = importlib.util.spec_from_file_location("pp_campaign_turn", HERE / "turn.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def refuse(code: str, detail: str) -> int:
    print(f"campaign: REFUSED -- {code} -- {detail}\n  nothing played.", file=sys.stderr)
    return 2


class Refused(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code, self.detail = code, detail


# --- the set and its manifest ----------------------------------------------------------------------

def manifest_of(set_dir: Path) -> dict:
    """-> the manifest of the set at `set_dir`, judged: a name, an agent, the roots (each a
    sub-directory with a message), the files and the skills (paths relative to the set, standing), the
    packages its house carries (packages of the source)."""
    path = set_dir / MANIFEST
    if not set_dir.is_dir():
        raise Refused("set-missing", f"`{set_dir}` is no directory")
    if not path.is_file():
        raise Refused("manifest-missing", f"no `{MANIFEST}` under {set_dir}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as wrong:
        raise Refused("manifest-invalid", f"{path}: {wrong}") from None
    if not isinstance(loaded, dict) or not isinstance(loaded.get("roots"), dict) or not loaded["roots"]:
        raise Refused("manifest-invalid", f"{path}: `roots:` must map each root to its description")
    roots = {}
    for name, spec in loaded["roots"].items():
        spec = spec or {}
        if not (set_dir / str(name)).is_dir():
            raise Refused("manifest-invalid", f"root `{name}`: no directory `{set_dir / str(name)}`")
        if not isinstance(spec, dict) or not str(spec.get("message", "")).strip():
            raise Refused("manifest-invalid", f"root `{name}`: `message:` is missing")
        unknown = sorted(set(spec) - set(ROOT_KEYS))
        if unknown:
            raise Refused("manifest-invalid", f"root `{name}`: unknown key(s) {unknown} -- the keys are {ROOT_KEYS}")
        door = spec.get("door")
        if door is not None and not (set_dir / str(name) / str(door)).is_file():
            raise Refused("manifest-invalid", f"root `{name}`: door `{door}` is no document of the root")
        intent = spec.get("model") or []
        if not isinstance(intent, list) or not all(isinstance(one, dict) and len(one) == 1 for one in intent):
            raise Refused("manifest-invalid", f"root `{name}`: `model:` is a list of one-key acts (open, pick, field)")
        launches = spec.get("launches")
        if launches is not None and (isinstance(launches, bool) or not isinstance(launches, int) or launches < 1):
            raise Refused("manifest-invalid", f"root `{name}`: `launches:` is a whole number of launches, at least 1 -- "
                          "the bound of one wake-up")
        renew = spec.get("renew", False)
        if not isinstance(renew, bool):
            raise Refused("manifest-invalid", f"root `{name}`: `renew:` is true or false -- the run renewed between two "
                          "launches")
        again = spec.get("again")
        if again is not None and not str(again).strip():
            raise Refused("manifest-invalid", f"root `{name}`: `again:` is the principal's next message -- the "
                          "passage parked, a second wake-up takes the run up on it")
        opening = spec.get("open")
        if opening is not None and not str(opening).strip():
            raise Refused("manifest-invalid", f"root `{name}`: `open:` is the space the PRINCIPAL opens once the "
                          "first passage parked -- `agent open <NAME[@n]>`, a wake-up of its own")
        roots[str(name)] = {"door": door, "message": str(spec["message"]).strip(),
                            "manual": str(spec.get("manual") or spec["message"]).strip(),
                            "look": str(spec.get("look") or "").strip(), "model": intent,
                            "expect": expectation_of(str(name), spec.get("expect")),
                            "launches": launches, "renew": renew,
                            "again": str(again).strip() if again is not None else None,
                            "open": str(opening).strip() if opening is not None else None}
    files = loaded.get("files") or {}
    skills = loaded.get("skills") or []
    clean = loaded.get("clean") or []
    keep = loaded.get("keep") or []
    packages = loaded.get("packages") or []
    if not isinstance(packages, list) or not all(isinstance(one, str) for one in packages):
        raise Refused("manifest-invalid", f"{path}: `packages:` lists the names of packages of the source")
    absent = [one for one in packages if not (ROOT / "packages" / one / "package.yaml").is_file()]
    if absent:
        raise Refused("manifest-invalid", f"{path}: `packages:` names {absent} -- no such package under {ROOT / 'packages'}")
    if not isinstance(files, dict) or not isinstance(skills, list) or not isinstance(clean, list):
        raise Refused("manifest-invalid", f"{path}: `files:` maps a name to a path, `skills:` and `clean:` list paths")
    if not isinstance(keep, list):
        raise Refused("manifest-invalid", f"{path}: `keep:` lists paths")
    for key, listed in (("clean", clean), ("keep", keep)):
        if any(str(one).startswith("/") or ".." in Path(str(one)).parts for one in listed):
            raise Refused("manifest-invalid", f"{path}: `{key}:` names paths under the agent's workspace alone")
    for name, rel in files.items():
        if not (set_dir / str(rel)).is_file():
            raise Refused("manifest-invalid", f"file `{name}`: `{set_dir / str(rel)}` is missing")
    for rel in skills:
        if not (set_dir / str(rel) / "SKILL.md").is_file():
            raise Refused("manifest-invalid", f"skill `{rel}`: no SKILL.md under {set_dir / str(rel)}")
    return {"name": str(loaded.get("name") or set_dir.name), "agent": str(loaded.get("agent") or "agents/pat"),
            "set": str(set_dir), "roots": roots, "files": {str(k): str(v) for k, v in files.items()},
            "skills": [str(one) for one in skills], "clean": [str(one) for one in clean],
            "keep": [str(one) for one in keep], "packages": list(packages)}


def expectation_of(root: str, given) -> dict:
    """-> the `expect:` of a root, judged: a mapping of EXPECT_KEYS -- `words`, `launches`, `proofs`, `calls`
    whole numbers, `parked` true or false -- on the campaign's one channel; {} when the root expects nothing.
    The expectation counts what
    one looks at of a root over the WHOLE exchange (the boot's and the turn's words included), never the
    text of a production: the sheet judges it per exchange."""
    if given is None:
        return {}
    if not isinstance(given, dict):
        raise Refused("manifest-invalid", f"root `{root}`: `expect:` maps counts -- the keys are {EXPECT_KEYS}")
    unknown = sorted(set(given) - set(EXPECT_KEYS))
    if unknown:
        raise Refused("manifest-invalid", f"root `{root}`: unknown key(s) {unknown} under `expect:` -- the keys are {EXPECT_KEYS}")

    def whole(key: str, value) -> bool:
        if key == "parked":
            return isinstance(value, bool)
        return isinstance(value, int) and not isinstance(value, bool) and value >= 0

    judged = {}
    for key, value in given.items():
        if not whole(key, value):
            raise Refused("manifest-invalid", f"root `{root}`: `expect: {key}` is "
                          + ("true or false" if key == "parked" else "a whole number"))
        judged[key] = value
    return judged


# --- the plans ------------------------------------------------------------------------------------

def plan_name(root: str) -> str:
    """-> the name of a root's plan: the root and the campaign's channel, as the evidence names it."""
    return f"{root}-{CHANNEL}"


def plan_of(manifest: dict, root: str, asked: dict) -> dict:
    """-> ONE plan of launch: what the house would play for `root`."""
    spec = manifest["roots"][root]
    documents = str(Path(manifest["set"]) / root)
    door = spec["door"]
    agent = manifest["agent"]
    policy = ["--model", asked["model"]] if asked.get("model") else []
    policy += ["--effort", asked["effort"]] if asked.get("effort") else []
    launches = str(spec["launches"]) if spec["launches"] is not None else asked["launches"]
    resume, opening = None, None
    # a root that RENEWS plays its exchange in two wake-ups: the first bounded at one launch, the run
    # renewed between the two (as an upgrade renews it), the second taking the run up by `--run`; a
    # root that says `open:` has the principal open that space once the first passage parked (`agent open`,
    # a wake-up without a message); a root that says `again:` plays its next message as one more wake-up
    command = ["./pp", "agent", "run", agent, "--message", spec["message"], "--documents", documents,
               *(["--door", door] if door else []), "--max-budget-usd", asked["budget"],
               "--launches", "1" if spec["renew"] else launches, "--provider", asked["provider"], *policy, "--json"]
    if spec["open"]:
        opening = ["./pp", "agent", "open", agent, "<key>", spec["open"], "--max-budget-usd", asked["budget"],
                   "--launches", launches, "--provider", asked["provider"], *policy, "--json"]
    if spec["renew"] or spec["again"]:
        resume = ["./pp", "agent", "run", agent, "--run", "<key>", "--message", spec["again"] or RESUME_MESSAGE,
                  "--max-budget-usd", asked["budget"], "--launches", launches, "--provider", asked["provider"],
                  *policy, "--json"]
    environment = {INTENT: json.dumps(spec["model"], ensure_ascii=False)} if spec["model"] else {}
    return {"name": plan_name(root), "set": manifest["name"], "root": root,
            "channel": CHANNEL, "provider": asked["provider"],
            "model": asked.get("model"), "effort": asked.get("effort"), "repeat": asked["repeat"],
            "budget": asked["budget"], "door": door, "documents": documents, "message": spec["message"],
            "intent": spec["model"], "expect": spec["expect"], "launches": int(launches), "renew": spec["renew"],
            "again": spec["again"], "open": spec["open"],
            "packages": manifest["packages"], "command": command, "resume": resume, "opening": opening,
            "environment": environment, "launched": False}


def plans(manifest: dict, asked: dict) -> list[dict]:
    return [plan_of(manifest, root, asked) for root in asked["roots"] or list(manifest["roots"])]


def option(argv: list[str], name: str, default: str | None = None) -> str | None:
    if name in argv:
        at = argv.index(name)
        if at + 1 < len(argv):
            return argv[at + 1]
    return default


def options(argv: list[str], name: str) -> list[str]:
    return [argv[i + 1] for i, one in enumerate(argv) if one == name and i + 1 < len(argv)]


def asked_of(argv: list[str], manifest: dict) -> dict:
    roots = options(argv, "--root")
    unknown = [one for one in roots if one not in manifest["roots"]]
    if unknown:
        raise Refused("root-unknown", f"{unknown} -- the roots of `{manifest['name']}` are {', '.join(manifest['roots'])}")
    repeat = str(option(argv, "--repeat", REPEAT))
    if not repeat.isdigit() or int(repeat) < 1:
        raise Refused("repeat-invalid", f"`--repeat {repeat}`: a whole number of repetitions, at least 1")
    effort = option(argv, "--effort")
    if effort is not None:
        try:
            adapters.judged({"effort": effort})       # the engine's five words, judged at its face: no binary asked
        except Refusal as refusal:
            raise Refused(refusal.code, str(refusal)) from None
    return {"roots": roots,
            "provider": option(argv, "--provider", "claude"), "model": option(argv, "--model"), "effort": effort,
            "repeat": int(repeat), "budget": option(argv, "--budget", BUDGET),
            "launches": option(argv, "--launches", LAUNCHES)}


def set_of(argv: list[str]) -> Path:
    return Path(option(argv, "--set", str(DEFAULT_SET))).resolve()


def mask_of(argv: list[str]) -> list[str]:
    """-> the MASK asked (`--mask <zone>[,<zone>…]`): zones of a line (LINE_ZONES) and the word `agent`
    (the `rouge-agent` lines), each once in the order given; `mask-unknown` names what no zone says."""
    given = option(argv, "--mask")
    if given is None:
        return []
    names = [one.strip() for one in given.split(",") if one.strip()]
    unknown = [one for one in names if one not in (*LINE_ZONES, AGENT_MASK)]
    if unknown:
        raise Refused("mask-unknown", f"{unknown} -- a mask names zones of a line ({', '.join(LINE_ZONES)}) or `{AGENT_MASK}`")
    return list(dict.fromkeys(names))


def write_plans(out: Path, planned: list[dict]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for one in planned:
        (out / f"{one['name']}.json").write_text(json.dumps(one, indent=2, ensure_ascii=False) + "\n",
                                                 encoding="utf-8")


def plan(argv: list[str]) -> int:
    set_dir = set_of(argv)
    manifest = manifest_of(set_dir)
    asked = asked_of(argv, manifest)
    out = Path(option(argv, "--out", str(set_dir.parent / "out" / "dry")))
    planned = plans(manifest, asked)
    write_plans(out, planned)
    print(f"campaign: {len(planned)} plan(s) of `{manifest['name']}` written under {out} -- nothing launched")
    return 0


# --- the house ------------------------------------------------------------------------------------

def adapter_of(provider: str):
    """-> the provider's adapter, loaded by the engine's face; `provider-unknown` as it says it."""
    try:
        return adapters.load(provider)
    except Refusal as refusal:
        raise Refused(refusal.code, str(refusal)) from None


def binary_of(provider: str) -> str | None:
    """-> the binary the provider's adapter declares (`BINARY`), None when it needs none."""
    return getattr(adapter_of(provider), "BINARY", provider)


def bound_of(provider: str, exchanges: int, budget: str) -> float | None:
    """-> the BOUND of a campaign's cost in USD, said before the first launch: exchanges x budget where the
    adapter spells `max_budget_usd` (the cap handed to every exchange); 0 where the adapter needs no binary
    (the product's own harness, which spends nothing); None where a binary spells no budget -- the
    launches are not bounded."""
    module = adapter_of(provider)
    if "max_budget_usd" in getattr(module, "SPELLS", ()):
        return exchanges * float(budget)
    return 0.0 if getattr(module, "BINARY", provider) is None else None


def provider_present(provider: str) -> None:
    binary = binary_of(provider)
    if binary is not None and shutil.which(binary) is None:
        raise Refused("provider-missing", f"`{provider}` needs `{binary}`, which is not on this machine")


def laid(manifest: dict, agent: Path) -> None:
    """The set's accessories in the agent's workspace, its witness skills in the agent's instance, what
    the previous exchange left behind removed, what it rewrote put back as the first laying found it
    (kept under `KEPT` in the workspace) -- played before every exchange: each starts clean."""
    set_dir = Path(manifest["set"])
    for rel in manifest["keep"]:
        target, kept = agent / rel, agent / KEPT / rel
        if kept.is_file():
            shutil.copy(kept, target)
        elif target.is_file():
            kept.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(target, kept)
    for rel in manifest["clean"]:
        target = agent / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    for name, rel in manifest["files"].items():
        target = agent / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(set_dir / rel, target)
    for rel in manifest["skills"]:
        source = (set_dir / rel).resolve()
        shutil.copytree(source, agent / ".pp" / "skills" / source.name, dirs_exist_ok=True)


def house(manifest: dict, where: Path | None) -> tuple[Path, Path]:
    """-> (the disposable house's workspace, its console): the product installed with `agent` and the
    set's `packages:` (the agent borrows the house's machine, its packages with it), the set's agent born
    under the host's cap (`max_harness_tool_output`: what a tool result is cut by); a house standing at
    `where` is reused."""
    ws = where if where is not None else Path(tempfile.mkdtemp(prefix="pp-campaign-"))
    console = ws / "pp"
    if console.is_file() and (ws / manifest["agent"] / ".pp").is_dir():
        return ws, console                        # a standing house of a previous play: reused as it stands
    ws.mkdir(parents=True, exist_ok=True)
    done = subprocess.run([sys.executable, str(ENGINE), "-install", str(ws), "agent", *manifest["packages"],
                           "-slug", manifest["name"]], capture_output=True, text=True)
    if done.returncode != 0:
        raise Refused("install-failed", done.stderr.strip()[-300:])
    born = subprocess.run([str(console), "agent", "add", manifest["agent"]], cwd=ws, capture_output=True, text=True)
    if born.returncode != 0:
        raise Refused("agent-add-failed", born.stderr.strip()[-300:])
    capped(ws, manifest["agent"])                 # a tool result cut as the host cuts it
    return ws, console


def keep(folder: Path, name: str, text: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(text, encoding="utf-8")


# --- the play -------------------------------------------------------------------------------------

def key_of(stdout: str) -> str:
    """-> the run's key read on the house's JSON lines (`run`), else ""."""
    for line in reversed(stdout.splitlines()):
        try:
            data = json.loads(line)
        except ValueError:
            continue
        if isinstance(data, dict) and isinstance(data.get("run"), str):
            return data["run"]
    return ""


def environment_of(one: dict) -> dict:
    """-> the environment of an exchange: the operator's shell without what a conducted session of
    theirs carries (`PP_*`: a marble receipt, a run, a home), plus the plan's own variables."""
    return {**{key: value for key, value in os.environ.items() if not key.startswith("PP_")}, **one["environment"]}


def record_of(stdout: str, key: str) -> dict:
    """-> the JSON record of the exchange `key` on the house's lines, {} when none."""
    for line in reversed(stdout.splitlines()):
        try:
            data = json.loads(line)
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("run") == key:
            return data
    return {}


def renewed(agent_meta: Path, key: str) -> None:
    """The run `key` RENEWED between two wake-ups, as `./pp upgrade` renews every run of a house whose
    pins moved: its slot becomes a renewal mark by the engine's own face (`persistence.renew`), `renewed`
    written in its trace -- the house of the campaign is installed from the source at the engine's own
    version, so an upgrade would move nothing and renew nothing: the launcher plays the face."""
    slot = persistence.slot_of(agent_meta, key)
    moved = {"engine": VERSION}
    at = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    persistence.renew(slot, moved, moved, at)
    trace = persistence.trace_of(slot)
    if trace:
        log.record(slot.parent / trace, "renewed", **{"from": moved, "to": moved})


def relayed(ws: Path, console: Path, agent_meta: Path, one: dict) -> dict:
    """ONE exchange: `agent run`, on the agent's settings as they stand; a root that
    renews plays two wake-ups, the run renewed between them and taken up by the plan's `resume`; a root
    that says `again:` takes its parked run up by the same `resume`, on its next message; a root that says `open:`
    has the principal open the space first (`opening`: `agent open`, a wake-up without a message), then `again:`."""
    command = [str(console) if word == "./pp" else word for word in one["command"]]
    started = time.monotonic()
    played = subprocess.run(command, cwd=ws, capture_output=True, text=True, env=environment_of(one))
    key = key_of(played.stdout)
    stdout, stderr, launches = played.stdout, played.stderr, record_of(played.stdout, key).get("launches")
    if one.get("opening") and key:
        opening = [str(console) if word == "./pp" else key if word == "<key>" else word for word in one["opening"]]
        played = subprocess.run(opening, cwd=ws, capture_output=True, text=True, env=environment_of(one))
        stdout += played.stdout
        stderr += played.stderr
        launches = (launches or 0) + (record_of(played.stdout, key).get("launches") or 0)
    if one.get("resume") and key:
        if one.get("renew"):
            renewed(agent_meta, key)
        resume = [str(console) if word == "./pp" else key if word == "<key>" else word for word in one["resume"]]
        played = subprocess.run(resume, cwd=ws, capture_output=True, text=True, env=environment_of(one))
        stdout += played.stdout
        stderr += played.stderr
        launches = (launches or 0) + (record_of(played.stdout, key).get("launches") or 0)
    seconds = round(time.monotonic() - started, 2)
    record = record_of(played.stdout, key)
    return {"rc": played.returncode, "stdout": stdout, "stderr": stderr, "run": key,
            "seconds": seconds, "launches": launches, "cost_usd": record.get("cost_usd"),
            "error": record.get("error")}


def trace_of(agent_meta: Path, key: str) -> list[dict]:
    if not key:
        return []
    slot = persistence.slot_of(agent_meta, key)
    log = persistence.trace_of(slot)
    path = slot.parent / log if log else None
    if path is None or not path.is_file():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            found.append(json.loads(line))
        except ValueError:
            continue
    return found


def stats_of(console: Path, ws: Path, agent: str, key: str) -> dict:
    read = subprocess.run([str(console), "agent", "stats", agent, key, "--json"], cwd=ws, capture_output=True,
                          text=True)
    try:
        return json.loads(read.stdout.splitlines()[-1]) if read.stdout.strip() else {}
    except ValueError:
        return {}


def tool_results(flow: list[dict]) -> list[str]:
    return [str(one.get("content") or "") for one in flow if one.get("kind") == "tool-result"]


def exchange_name(plan: str, repetition: int, repeat: int) -> str:
    """-> the name of one exchange: the plan's, `#<k>` behind it when the plan is repeated."""
    return f"{plan}#{repetition}" if repeat > 1 else plan


def coverage_of(one: dict, played: dict, trace: list[dict], flow: list[dict], awaits: str,
                name: str, repetition: int) -> dict:
    """-> what ONE exchange crossed: the zones by their events, the holes of the model, the bounces and
    refusals it met, whether the passage ended, the launches, the seconds, the cost."""
    sockets = socket_mounts(trace)
    kinds = [str(event.get("kind") or "") for at, event in enumerate(trace) if at not in sockets]
    zones = {}
    for zone, events in ZONE_EVENTS.items():
        count = sum(kinds.count(event) for event in events)
        if count:
            zones[zone] = count
    proofs = sum(1 for event in trace if event.get("kind") == "answer"
                 and str(event.get("instruction") or "").startswith("PROVE"))
    if proofs:
        zones["proof"] = proofs
    prints = sum(1 for event in trace if is_print(event))
    if prints:
        zones["print"] = prints
        zones["value-judged"] = zones.get("value-judged", 0) - prints   # a print is no value
        if not zones["value-judged"]:
            del zones["value-judged"]
    refused = sum(1 for event in trace if event.get("kind") == "repair-in-place" and event.get("document"))
    if refused:
        zones["print-refused"] = refused
        zones["repair"] = zones.get("repair", 0) - refused                # a print refused replays nothing
        if not zones["repair"]:
            del zones["repair"]
    results = tool_results(flow)
    thoughts = [str(ev.get("text") or "") for ev in flow if ev.get("kind") == "thinking"]
    holes = [one for one in thoughts if one.startswith(HOLE)]
    answered = [line for one in results for line in one.splitlines() if line.startswith("pp: ")]
    bounces = sum(1 for line in answered if line.startswith(BOUNCE))
    refusals = [messages.read_refused(line)[0].strip() for line in answered if messages.read_refused(line)]
    bare_calls = sum(1 for ev in flow if ev.get("kind") == "tool" and BARE_CALL.match(str(ev.get("shell") or "")))
    if bounces:
        zones["bounce"] = bounces
    if bare_calls:
        zones["bare-call"] = bare_calls
    if played.get("error") == "budget-spent" or LAUNCHES_SPENT in str(played.get("stderr") or ""):
        zones["launcher-bound"] = 1
    return {"name": name, "root": one["root"], "channel": one["channel"], "repetition": repetition,
            "run": played["run"], "rc": played["rc"], "parked": awaits == persistence.MESSAGE,
            "launches": played["launches"], "seconds": played["seconds"], "cost_usd": played["cost_usd"],
            "error": played["error"], "zones": zones, "holes": holes, "bounces": bounces, "refusals": refusals,
            "blocks": kinds.count("block"), "calls": sum(1 for ev in flow if ev.get("kind") == "tool")}


def coverage_table(covered: list[dict], provider: str, manifest: dict, when: str) -> tuple[dict, str]:
    """-> (coverage.json, COVERAGE.md): zone x exchange x count, the zones never crossed, the holes,
    the bounces and refusals, the passages ended, the launches and seconds."""
    names = [one["name"] for one in covered]
    zones = list(ZONE_EVENTS)
    crossed = {zone: {one["name"]: one["zones"].get(zone, 0) for one in covered} for zone in zones}
    never = [zone for zone in zones if not any(crossed[zone].values())]
    data = {"date": when, "provider": provider, "set": manifest["name"], "roots": list(manifest["roots"]),
            "exchanges": covered, "zones": crossed, "never": never}
    lines = [f"# COVERAGE -- `{manifest['name']}` under `{provider}`, {when}", "",
             f"{len(covered)} exchange(s): {sum(1 for one in covered if one['parked'])} parked, "
             f"{sum(one['launches'] or 0 for one in covered)} launch(es), "
             f"{round(sum(one['seconds'] for one in covered), 1)} s, "
             f"{sum(len(one['holes']) for one in covered)} hole(s), {sum(one['bounces'] for one in covered)} bounce(s), "
             f"{sum(len(one['refusals']) for one in covered)} refusal(s).", "",
             "## The zones crossed, by exchange", "",
             "| zone | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for zone in zones:
        if zone in never:
            continue
        lines.append(f"| {zone} | " + " | ".join(str(crossed[zone][name] or "") for name in names) + " |")
    lines += ["", "## The zones never crossed", "", ", ".join(f"`{one}`" for one in never) or "none", "",
              "## The exchanges", "",
              "| exchange | run | parked | launches | seconds | blocks | calls | holes | bounces | refusals | error |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for one in covered:
        lines.append(f"| {one['name']} | {one['run'] or '?'} | {'yes' if one['parked'] else 'no'} | {one['launches']} | "
                     f"{one['seconds']} | {one['blocks']} | {one['calls']} | {len(one['holes'])} | {one['bounces']} | "
                     f"{' '.join(one['refusals']) or ''} | {one['error'] or ''} |")
    holes = [(one["name"], hole) for one in covered for hole in one["holes"]]
    if holes:
        lines += ["", "## The holes -- a text the model has no act for", ""]
        lines += [f"- `{name}`: {hole}" for name, hole in holes]
    return data, "\n".join(lines) + "\n"


def play(argv: list[str]) -> int:
    set_dir = set_of(argv)
    manifest = manifest_of(set_dir)
    asked = asked_of(argv, manifest)
    mask_of(argv)                                   # judged before anything plays
    provider_present(asked["provider"])
    when = _dt.datetime.now().strftime("%Y-%m-%dT%H%M")
    out = Path(option(argv, "--out", str(set_dir.parent / "out"))) / when
    planned = plans(manifest, asked)
    repeat = asked["repeat"]
    bound = bound_of(asked["provider"], len(planned) * repeat, asked["budget"])
    print(f"campaign: bound {len(planned)} plan(s) x {repeat} x {asked['budget']} USD = "
          + (f"{bound:g} USD" if bound is not None else f"no bound (`{asked['provider']}` spells no budget)")
          + f" -- provider {asked['provider']}, model {asked.get('model') or 'default'}, "
          f"effort {asked.get('effort') or 'default'}")
    where = option(argv, "--house")
    ws, console = house(manifest, Path(where) if where else None)
    agent = manifest["agent"]
    agent_meta = ws / agent / ".pp"
    print(f"campaign: house at {ws}, {len(planned) * repeat} exchange(s) of `{manifest['name']}` to play, kept under {out}")
    order = []
    for one in planned:
        for repetition in range(1, repeat + 1):
            name = exchange_name(one["name"], repetition, repeat)
            folder = out / name
            laid(manifest, ws / agent)
            played = relayed(ws, console, agent_meta, one)
            kept_plan = {**one, "launched": True, "repetition": repetition, "rc": played["rc"], "run": played["run"],
                         "seconds": played["seconds"]}
            keep(folder, "stdout.txt", played["stdout"])
            keep(folder, "stderr.txt", played["stderr"])
            key = played["run"]
            flow, awaits = [], ""
            if key:
                for file, verb in (("flow.jsonl", ["flow", agent, key, "--json"]),
                                   ("exchanges.json", ["exchanges", agent, key, "--json"])):
                    read = subprocess.run([str(console), "agent", *verb], cwd=ws, capture_output=True, text=True)
                    keep(folder, file, read.stdout)
                keep(folder, "stats.json", json.dumps(stats_of(console, ws, agent, key), indent=2) + "\n")
                flow = [json.loads(line) for line in (folder / "flow.jsonl").read_text(encoding="utf-8").splitlines()
                        if line.strip().startswith("{")]
                trace = trace_of(agent_meta, key)
                keep(folder, "trace.jsonl", "".join(json.dumps(ev, ensure_ascii=False) + "\n" for ev in trace))
                awaits = persistence.awaits(persistence.slot_of(agent_meta, key))
            else:
                trace = []
            covered = coverage_of(one, played, trace, flow, awaits, name, repetition)
            keep(folder, "run.json", json.dumps({**kept_plan, "coverage": covered}, indent=2, ensure_ascii=False) + "\n")
            order.append(name)
            print(f"campaign: {name} -- rc {played['rc']}, run {key or '?'}, "
                  f"{'parked' if covered['parked'] else awaits or 'no run'}, {played['launches']} launch(es), "
                  f"{played['seconds']} s, zones {' '.join(sorted(covered['zones'])) or '-'}")
    keep(out, CAMPAIGN, json.dumps({"date": when, "set": manifest["name"], "roots": list(manifest["roots"]),
                                    "engine": VERSION, "provider": asked["provider"], "model": asked.get("model"),
                                    "effort": asked.get("effort"), "repeat": repeat, "budget": asked["budget"],
                                    "launches": asked["launches"], "bound_usd": bound, "house": str(ws),
                                    "exchanges": order}, indent=2, ensure_ascii=False) + "\n")
    report = reported(out)
    sheet_data = sheeted(out, mask_of(argv))
    print(f"campaign: done -- {len(order)} exchange(s), {report['parked']} parked, cost {report['cost_usd']:g} USD "
          f"(bound " + (f"{bound:g} USD" if bound is not None else "none") + f"); the report at {out / 'REPORT.md'}, "
          f"the sheet at {out / 'SHEET.md'}: {sheet_said(sheet_data)}")
    return 0


# --- the report -------------------------------------------------------------------------------------

def artifacts_of(out: Path) -> tuple[dict, list[dict], list[dict]]:
    """-> (the campaign, each exchange's run.json, each exchange's stats.json) read under `out`, in the order
    the campaign played them; `campaign-missing` when no campaign stands there, `exchange-missing` when an
    exchange it names left no `run.json`."""
    path = out / CAMPAIGN
    if not path.is_file():
        raise Refused("campaign-missing", f"no `{CAMPAIGN}` under {out}: no campaign was played at that date")
    campaign = json.loads(path.read_text(encoding="utf-8"))
    runs, stats = [], []
    for name in campaign["exchanges"]:
        kept = out / name / "run.json"
        if not kept.is_file():
            raise Refused("exchange-missing", f"the campaign names `{name}` and {kept} is missing")
        runs.append(json.loads(kept.read_text(encoding="utf-8")))
        read = out / name / "stats.json"
        stats.append(json.loads(read.read_text(encoding="utf-8")) if read.is_file() else {})
    return campaign, runs, stats


def line_of(run: dict, stats: dict) -> dict:
    """-> ONE line of the report: what the exchange's coverage and the engine's `-stats -json` (relayed by
    `agent stats`) say of it -- the run, the cost, the launches, the seconds, parked, the repairs, the
    refusals, the holes, the bounces, the held and inline outputs, the values handed, the mass, the tokens;
    the deviations their sum, the conformity the values handed without a repair over the values handed."""
    covered = run["coverage"]
    conduction = stats.get("conduction") or {}
    values = sum(int(count) for count in (conduction.get("values") or {}).values())
    repairs = int(conduction.get("repairs") or 0)
    refusals = int(conduction.get("refusals") or 0)
    holes, bounces = len(covered.get("holes") or []), int(covered.get("bounces") or 0)
    return {"name": covered["name"], "root": run["root"], "channel": run["channel"],
            "repetition": int(run.get("repetition") or 1), "run": covered.get("run") or None, "rc": covered["rc"],
            "parked": bool(covered["parked"]), "cost_usd": float(covered.get("cost_usd") or 0.0),
            "launches": int(covered.get("launches") or 0), "seconds": float(covered.get("seconds") or 0.0),
            "blocks": int(covered.get("blocks") or 0), "repairs": repairs, "refusals": refusals, "holes": holes,
            "bounces": bounces, "deviations": repairs + refusals + holes + bounces,
            "held": int(conduction.get("held") or 0), "inline": int(conduction.get("inline") or 0),
            "proofs": int(conduction.get("proofs") or 0), "values": values,
            "conformity": round((values - repairs) / values, 4) if values else None,
            "mass": conduction.get("mass"), "tokens": conduction.get("tokens"), "error": covered.get("error")}


def p90_of(values: list[float]) -> float:
    """-> the p90 at the NEAREST RANK, `ceil(0.9 n)`: said as it is whatever n (the mean when n is 1)."""
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.9 * len(ordered)) - 1)]


def measured(values: list[float], digits: int) -> dict:
    return {"mean": round(sum(values) / len(values), digits) if values else 0, "p90": round(p90_of(values), digits) if values else 0}


def aggregate_of(lines: list[dict]) -> dict:
    """-> the aggregate of the lines of ONE root over its repetitions."""
    first = lines[0]
    values, repairs = sum(one["values"] for one in lines), sum(one["repairs"] for one in lines)
    return {"plan": plan_name(first["root"]), "root": first["root"],
            "channel": first["channel"], "n": len(lines),
            "parked": sum(1 for one in lines if one["parked"]),
            "cost_usd": measured([one["cost_usd"] for one in lines], 4),
            "launches": measured([one["launches"] for one in lines], 2),
            "seconds": measured([one["seconds"] for one in lines], 2),
            "deviations": sum(one["deviations"] for one in lines), "repairs": repairs,
            "refusals": sum(one["refusals"] for one in lines), "holes": sum(one["holes"] for one in lines),
            "bounces": sum(one["bounces"] for one in lines), "held": sum(one["held"] for one in lines),
            "inline": sum(one["inline"] for one in lines), "values": values,
            "conformity": round((values - repairs) / values, 4) if values else None}


def shown(value) -> str:
    """-> a number as a cell shows it, '' for none."""
    return "" if value is None else f"{value:g}"


def report_text(campaign: dict, report: dict) -> str:
    bound = campaign.get("bound_usd")
    lines = [f"# REPORT -- `{campaign['set']}` under `{campaign['provider']}`, {campaign['date']}", "",
             f"model {campaign.get('model') or 'default'} · effort {campaign.get('effort') or 'default'} · "
             f"{campaign['repeat']} repetition(s) · budget {campaign['budget']} USD per exchange · "
             f"bound {shown(bound) + ' USD' if bound is not None else 'none'} · cost {report['cost_usd']:g} USD · "
             f"{len(report['exchanges'])} exchange(s), {report['parked']} parked, {report['launches']} launch(es), "
             f"{report['seconds']:g} s, {report['deviations']} deviation(s)",
             "", "## By root, over the repetitions", "",
             "| plan | n | parked | cost mean | cost p90 | launches mean | launches p90 | seconds mean | "
             "deviations | repairs | refusals | holes | bounces | held | inline | values | conformity |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for one in report["aggregates"]:
        lines.append(f"| {one['plan']} | {one['n']} | {one['parked']} | {shown(one['cost_usd']['mean'])} | "
                     f"{shown(one['cost_usd']['p90'])} | {shown(one['launches']['mean'])} | "
                     f"{shown(one['launches']['p90'])} | {shown(one['seconds']['mean'])} | {one['deviations']} | "
                     f"{one['repairs']} | {one['refusals']} | {one['holes']} | {one['bounces']} | {one['held']} | "
                     f"{one['inline']} | {one['values']} | {shown(one['conformity'])} |")
    lines += ["", "## The exchanges", "",
              "| exchange | run | parked | cost | launches | seconds | blocks | repairs | refusals | holes | bounces | "
              "held | inline | values | conformity | mass | tokens | error |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for one in report["exchanges"]:
        lines.append(f"| {one['name']} | {one['run'] or '?'} | {'yes' if one['parked'] else 'no'} | "
                     f"{shown(one['cost_usd'])} | {one['launches']} | {shown(one['seconds'])} | {one['blocks']} | "
                     f"{one['repairs']} | {one['refusals']} | {one['holes']} | {one['bounces']} | {one['held']} | "
                     f"{one['inline']} | {one['values']} | {shown(one['conformity'])} | {shown(one['mass'])} | "
                     f"{shown(one['tokens'])} | {one['error'] or ''} |")
    return "\n".join(lines) + "\n"


def reported(out: Path) -> dict:
    """Writes, from the artifacts kept under `out` alone, `coverage.json` and `COVERAGE.md`, `report.json` and
    `REPORT.md` -- the ONE writer of the four, played by `play` and by `report`: replayed on the same
    artifacts it renders the same bytes. -> the report."""
    campaign, runs, stats = artifacts_of(out)
    covered = [run["coverage"] for run in runs]
    data, text = coverage_table(covered, campaign["provider"], {"name": campaign["set"], "roots": campaign["roots"]},
                                campaign["date"])
    keep(out, "coverage.json", json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    keep(out, "COVERAGE.md", text)
    lines = [line_of(run, read) for run, read in zip(runs, stats)]
    groups: dict[tuple, list[dict]] = {}
    for one in lines:
        groups.setdefault((one["root"], one["channel"]), []).append(one)
    report = {"date": campaign["date"], "set": campaign["set"], "provider": campaign["provider"],
              "model": campaign.get("model"), "effort": campaign.get("effort"), "repeat": campaign["repeat"],
              "budget": campaign["budget"], "bound_usd": campaign.get("bound_usd"),
              "cost_usd": round(sum(one["cost_usd"] for one in lines), 6),
              "parked": sum(1 for one in lines if one["parked"]), "launches": sum(one["launches"] for one in lines),
              "seconds": round(sum(one["seconds"] for one in lines), 2),
              "deviations": sum(one["deviations"] for one in lines),
              "aggregates": [aggregate_of(group) for group in groups.values()], "exchanges": lines}
    keep(out, "report.json", json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    keep(out, "REPORT.md", report_text(campaign, report))
    return report


def report(argv: list[str]) -> int:
    if not argv or argv[0].startswith("--"):
        raise Refused("date-missing", "`report <date> [--out <dir>]`: the date names the campaign's folder under <out>")
    set_dir = set_of(argv)
    out = Path(option(argv, "--out", str(set_dir.parent / "out"))) / argv[0]
    told = reported(out)
    print(f"campaign: report of {argv[0]} -- {len(told['exchanges'])} exchange(s), {told['parked']} parked, "
          f"cost {told['cost_usd']:g} USD, {told['deviations']} deviation(s); {out / 'REPORT.md'}, {out / 'COVERAGE.md'}")
    return 0


# --- the sheet of response -------------------------------------------------------------------------

SHEET = "sheet.json"
COMPARE = "compare.json"
VERDICTS = ("vert", "rouge-conduction", "rouge-agent", "trou")
REDS = ("rouge-conduction", "rouge-agent", "trou")
AGENT_MASK = "agent"                                                        # the mask of the `rouge-agent` lines
ROOT_ZONE = "root"                                                          # the zone of the root at its end
LINE_ZONES = (*ZONE_EVENTS, ROOT_ZONE)                                      # what the zone of a LINE may be
# the act that OPENED an output (the event before its first block) -> the zone of its lines; what no act
# names is a free step; a cut output is `chunk`, a held one `held-output`, the root at its end `root`
OPENED_ZONES = {"new": "boot", "answer": "value-judged", "print": "print", "print-waived": "print-waived", "routed": "door", "door": "door", "mounted": "mount",
                "inline": "inline", "opened": "space", "closed": "space", "compacted": "compaction",
                "reopened": "renewal", "switch": "package-switch", "stray": "soft-catch",
                "offer-absent": "offer-absent", "repair": "repair", "repair-in-place": "repair"}
STOPPING = ("repair-exhausted", "exec-refused", "artifact-stale")   # the refusals that stop the conduction (S)
CONSOLE_BOUNCES = ("bounce", "chunk-pending")                               # answered by the console, never traced
# the acts that END a call's rendering in the trace: what follows them was rendered by the NEXT call
ACTS = ("answer", "routed", "gesture", "mounted", "stray", "switch", "compacted", "reopened", "refusal",
        "released", "door-argument", "mount-gone", "repair", "repair-in-place", "chunk-dropped", "closed",
        "opened", "signal", "signal-refused", "exec", "diagnostic")
HELD_ANSWERS = {"value": "value-judged", "mount": "mounted", "door": "opened", "closed": "closed",
                "compacted": "re-served", "reopened": "reopened"}          # the act held -> the ANSWERS row
RENDERING = ("new", "prompt", "initialize")   # after these, the call is still rendering its output
SAID = ("WORK", "INFER")                     # the commands of a step said in an output: the output may go on behind it
CLOSED = ("print-due", "pending", "held", "inline", "advance", "section", "cut")
                                             # traced once an output closed: what follows is the next call's


def is_print(event: dict) -> bool:
    """-> whether a trace event is a print taken: the `answer` of a production said on `terminal`, handed by
    its print call -- it names the document of its step (the principal's bare call over a pending step names none)."""
    return event.get("kind") == "answer" and event.get("channel") == "terminal" and bool(event.get("document"))


def socket_mounts(trace: list[dict]) -> set[int]:
    """-> the indexes of the `mounted` events a SOCKET traced while a call rendered its output -- a contributor
    mounted at `turn.begin` or at a frame's `initialize`, never an act of the agent. Such a mount is traced
    inside the rendering: with `held` (a contributor's laws held by its frame), or after the call opened and
    before its next block came (`new`, `prompt`, `initialize`), or between two blocks of one output (after the
    block of a step said, the output still open: nothing says it closed). The `mounted` of the agent's `-mount`
    opens a call of its own: an output closed before it."""
    found, rendering = set(), False
    for at, event in enumerate(trace):
        kind = event.get("kind")
        if kind == "mounted" and (event.get("held") or rendering):
            found.add(at)
        elif kind == "block":
            rendering = str(event.get("command") or "") in SAID and not event.get("wait")
        elif kind in RENDERING:
            rendering = True
        elif kind in CLOSED or kind in ACTS:
            rendering = False
    return found
PP_CALL = re.compile(r"(^|\s|/)pp(\s|$)")                                  # a shell line that calls the console
MOVING = ("bare", "value", "new")                                          # the calls that move the run on
CONSOLE_VERBS = {"-open": "open", "-close": "close", "-compacted": "compacted", "-disable": "switch",
                 "-enable": "switch", "-skip": "skip", "-print": "print"}    # the keyed verbs, by their kind


def harness_module():
    """-> the modelled harness as a module: its grammar (`grammar`, `answered`, `traits_of`) and its data
    (`semantics`), the READER of the sheet -- the same reading the modelled LLM makes of a text."""
    path = ROOT / "adapters" / "model" / "harness.py"
    spec = importlib.util.spec_from_file_location("pp_model_harness", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outputs_of(trace: list[dict]) -> list[dict]:
    """The ORACLE: the trace cut into the ITEMS pp handed over, in order -- each an OUTPUT (the blocks one
    call rendered, the channel it left by, the form the stack's state gives it: V a value due, T a free
    step pending, M the root exhausted; `chunks` the texts it was served in, the first ones R) or an
    ANSWER (a held line, the line of a print, a gesture, a refusal: what a call of the agent was answered).
    Read from the trace alone: `block`, `print-due`, `pending`, `held`, `inline`, `advance`, `cut`, `chunk`,
    `gesture`, `refusal`, the prints taken, lifted or stood for by a door, and the acts that end a call's rendering; nothing of the
    text. A print answers its line -- other calls due, or the last message alone -- unless it was the last due
    of an output closed on its prints: the run moved on, and the block it moved to is the call's result."""
    items: list[dict] = []
    open_: dict | None = None
    held_at: dict | None = None
    last_act = ""                                   # the event before the next output's first block
    seal_next = False                               # a `section` was traced: the block that follows closes its output
    due = 0                                         # the prints due at the run
    principal_opened = False                            # a space the principal opened on the parked run: its held line
                                                    # answers the principal's own call, never the agent's

    def moved_after(at: int) -> bool:
        """-> whether the call that traced the event at `at` moved the run: a block follows before any act."""
        for event in trace[at + 1:]:
            kind = event.get("kind")
            if kind == "block":
                return True
            if kind in ACTS or kind in ("print-waived", "prompt", "advance"):
                return False
        return False

    def printed(at: int, name: str) -> None:
        """A print call answered: its line, unless the run moved on -- `more` while prints stay due or the
        output it answers awaits a value, `last` when the last message alone remains."""
        if moved_after(at):
            return
        if name != "printed-waived":
            before = last_output()
            name = "printed-more" if due or (before is not None and before["form"] == "V") else "printed-last"
        items.append({"kind": "answer", "channel": "tool", "answer": name, "form": "D", "chunks": 1})

    def last_output() -> dict | None:
        """-> the last output the trace closed, None before the first."""
        return next((one for one in reversed(items) if one["kind"] == "output"), None)

    def close(channel: str, delivered: bool = True) -> None:
        nonlocal open_
        if open_ is None:
            return
        last = open_["blocks"][-1]
        if last["wait"]:
            form = "M"                      # the root exhausted: a message of the principal is due
        elif not last["command"] or last["command"] == "WORK" or open_["pending"]:
            form = "T"                      # a free step pending, said, or rendered again: the agent's words are due
        else:
            form = "V"                      # a step that asks the tool (a proof, a field, a choice, a consumed
                                            # production): a value is due
        open_.update({"channel": channel, "form": form, "delivered": delivered})
        items.append(open_)
        open_ = None

    def sealed() -> bool:
        """-> whether the open output can take no more block: a section break closed it (`section`, the
        marked step opening the next call), its last block is the pending step rendered again (no command:
        the output closed on it) or the root at its end, or its chunks are all served."""
        if open_ is None:
            return False
        last = open_["blocks"][-1]
        return open_.get("sealed", False) or not last["command"] or last["wait"] or open_.get("complete", False)

    sockets = socket_mounts(trace)
    for at, event in enumerate(trace):
        kind = event.get("kind")
        if at in sockets:
            continue                                 # a contributor a socket mounted: no act of the agent
        if kind == "new":
            last_act = "new"
        elif kind == "block":
            if sealed():
                close("prompt")
            if open_ is None:
                open_ = {"kind": "output", "blocks": [], "pending": "", "chunks": 1, "facts": [], "opened": last_act}
            open_["blocks"].append({"stack": event.get("stack", ""), "command": event.get("command", ""),
                                    "wait": bool(event.get("wait"))})
            if seal_next:
                open_["sealed"], seal_next = True, False   # the `§`: this block is the output's last
        elif kind == "print-due":
            due += 1
            if open_ is not None:                    # the documents whose print this output leaves due
                open_.setdefault("due", []).append(str(event.get("document") or ""))
        elif is_print(event):
            due = max(due - 1, 0)
            close("prompt")
            printed(at, "")
            last_act = "print"
            continue
        elif kind == "print-by-door":
            due = max(due - 1, 0)                    # a door stands for the step: no call answered, nothing rendered
        elif kind == "print-waived":
            due = max(due - 1, 0)
            following = trace[at + 1].get("kind") if at + 1 < len(trace) else ""
            if following not in ("print-waived", "prompt"):   # a print the bound lifted, not a passage's debts
                close("prompt")
                printed(at, "printed-waived")
                last_act = "print-waived"
            continue
        elif kind == "section":
            seal_next = True                         # the `§`: the block rendered next closes the output
        elif (kind == "stray" and ("due" in event or "document" in event)) or (
                kind == "repair-in-place" and event.get("document")):
            # a call CAUGHT while prints are due, a print of nothing due, a print refused on its form: the block
            # that stands answers with its deviation -- nothing moved. The agent's call is answered by a VIEW in
            # its result; the house's own advance is answered at the PROMPT of the next launch: an output of the
            # form the output before it left
            close("prompt")
            before = last_output()
            following = trace[at + 1].get("kind") if at + 1 < len(trace) else ""
            if (kind == "stray" and "due" in event and not event.get("handed")
                    and following == "advance" and before is not None):
                items.append({"kind": "output", "blocks": [dict(before["blocks"][-1])],
                              "pending": before.get("pending", ""), "chunks": 1, "facts": [], "opened": "stray",
                              "channel": "prompt", "form": before["form"], "delivered": True})
            else:
                zone = "print-refused" if kind == "repair-in-place" else "soft-catch"
                items.append({"kind": "view", "channel": "tool", "answer": "caught", "zone": zone,
                              "form": view_form(before["form"] if before is not None else ""),
                              "name": str(event.get("document") or ""), "chunks": 1})
            last_act = str(kind)
            continue
        elif kind == "offer-absent":
            # a name the step does not offer: the block that stands answers the call as a VIEW, with its
            # deviation -- nothing moved; the text is the oracle's to expect, its zone the event's
            close("prompt")
            before = last_output()
            items.append({"kind": "view", "channel": "tool", "answer": "offer-absent", "zone": "offer-absent",
                          "form": view_form(before["form"] if before is not None else ""),
                          "name": str(event.get("name") or ""), "chunks": 1})
        elif kind == "pending" and open_ is not None:
            open_["pending"] = str(event.get("instruction", ""))
        elif kind == "prove-idle" and open_ is not None:
            open_["facts"].append("prove-idle")
        elif kind == "cut":
            target = open_ if open_ is not None else (items[-1] if items else None)
            if target is not None:
                target["cut"] = int(event.get("left") or 0)
        elif kind == "chunk":
            target = open_ if open_ is not None else (items[-1] if items else None)
            if target is not None:
                target["chunks"] = int(target.get("chunks", 1)) + 1
                if not int(event.get("left") or 0):
                    target["complete"] = True
        elif kind == "held":
            if open_ is not None:
                open_["held"] = True
            close("prompt", delivered=False)
            held_at = items[-1] if items else None
            if not principal_opened:
                items.append({"kind": "answer", "channel": "tool",
                              "answer": HELD_ANSWERS.get(str(event.get("act")), "value-judged"), "form": "D", "chunks": 1})
            principal_opened = False
        elif kind == "inline":
            close("tool")
        elif kind == "advance":
            if event.get("held"):
                if held_at is not None:
                    held_at["delivered"] = True
                    held_at = None
            else:
                close("prompt")
        elif kind == "gesture":
            close("prompt")
            items.append({"kind": "answer", "channel": "tool", "answer": "gesture", "form": "D", "chunks": 1})
        elif kind == "refusal":
            close("prompt")
            code = str(event.get("code") or "")
            items.append({"kind": "answer", "channel": "tool", "answer": "refusal", "code": code, "chunks": 1})
        elif kind in ACTS:
            if kind == "routed" and open_ is None and (last_output() or {}).get("form") == "M":
                principal_opened = True                  # the run parked, and a space opened: the principal's `agent open`
            close("prompt")
        if kind in ACTS or kind in ("inline", "advance", "offer-absent"):
            last_act = str(kind)
    close("prompt")
    return items


def view_form(last_form: str) -> str:
    """-> the form of a VIEW, the block that stands rendered again in a call's result: it carries no closing --
    D, unless the output before it asks a value: its lines then read V, as that output did."""
    return "V" if last_form == "V" else "D"


def zone_of(item: dict, piece: int = 1) -> str:
    """-> the ZONE of a text the oracle's item handed: the root at its end `root`, a cut output `chunk`
    (every piece), a held one `held-output`, else the zone of the act that opened it (OPENED_ZONES),
    else `free-step`; an answer: the held line `held-output`, a stopping refusal `stopping-refusals`,
    `principal-advances` `bare-call`, a gesture or another refusal `free-step`."""
    if item["kind"] == "view":
        return str(item.get("zone") or "free-step")
    if item["kind"] == "answer":
        if item.get("answer") in HELD_ANSWERS.values():
            return "held-output"
        if item.get("answer") in ("printed-more", "printed-last"):
            return "print"
        if item.get("answer") == "printed-waived":
            return "print-waived"
        if item.get("answer") == "refusal":
            code = item.get("code", "")
            return "stopping-refusals" if code in STOPPING else ("bare-call" if code == "principal-advances" else "free-step")
        return "free-step"
    last = item["blocks"][-1]
    if last["wait"]:
        return ROOT_ZONE
    if int(item.get("chunks", 1)) > 1 or item.get("cut"):
        return "chunk"
    if item.get("held"):
        return "held-output"
    return OPENED_ZONES.get(str(item.get("opened", "")), "free-step")


def oracle_texts(items: list[dict], semantics) -> list[dict]:
    """-> the oracle's TEXTS, one per text handed over: an output in `chunks` pieces (R but the last, which
    carries the output's form), an answer as one; each with the three concepts and the act its form gives
    on its channel (`semantics.FORMS`), an answer with its ANSWERS row."""
    texts = []
    for n, item in enumerate(items, 1):
        if item["kind"] == "answer":
            # a refusal is named by its code where the data know the code's line, `refusal` otherwise
            name = item["answer"] if item["answer"] != "refusal" else (
                item.get("code") if item.get("code") in semantics.ANSWERS else "refusal")
            row = semantics.ANSWERS[name]
            state = semantics.FORMS[row["form"]]["tool"]
            texts.append({"item": n, "kind": "answer", "channel": "tool", "answer": name,
                          "code": item.get("code", ""), "form": row["form"],
                          "awaits": row.get("awaits", state["awaits"]),
                          "owes": state["owes"], "comes": state["comes"], "act": row["act"], "delivered": True,
                          "zone": zone_of(item)})
            continue
        if item["kind"] == "view":
            # the block that stands, answering a call that moved nothing (a name not offered, a call caught):
            # read as a view, of the form `view_form` gives it, settled by the lines
            state = semantics.FORMS[item.get("form", "D")]["tool"]
            texts.append({"item": n, "kind": "view", "channel": "tool", "answer": item["answer"],
                          "name": item.get("name", ""), "form": item.get("form", "D"), "awaits": state["awaits"],
                          "owes": state["owes"], "comes": state["comes"], "act": state["act"], "delivered": True,
                          "zone": zone_of(item)})
            continue
        for piece in range(1, int(item.get("chunks", 1)) + 1):
            form = item["form"] if piece == item["chunks"] else "R"
            state = semantics.FORMS[form][item["channel"]]
            texts.append({"item": n, "kind": "output", "channel": item["channel"], "form": form,
                          "piece": f"{piece}/{item['chunks']}", "stack": item["blocks"][-1]["stack"],
                          "blocks": len(item["blocks"]), "pending": item.get("pending", ""),
                          "awaits": state["awaits"], "owes": state["owes"], "comes": state["comes"],
                          "act": state["act"], "delivered": bool(item.get("delivered", True)),
                          "zone": zone_of(item, piece)})
    return texts


def call_kind(shell: str) -> str:
    """-> what a call of the console is, read from its shell line alone: `new`, `bare` (the key alone),
    `value` (a production on the call or piped), `print` (a production said to the principal, by its print
    call), `offer` (`-s <name>`), `mount`, `view` (`-peek`), `open` and `close` (a space), `compacted`, `switch`
    (`-disable`, `-enable`), `skip`, `other`; "" for a shell
    that does not call the console. The calls that hand the pending step its production are `MOVING`."""
    if not PP_CALL.search(shell.splitlines()[0] if shell else ""):
        return ""
    words = shlex.split(shell.splitlines()[0]) if shell else []
    if words and words[-1] == "<<'EOF'":
        words = words[:-1]
    rest = words[1:]
    if rest[:1] == ["-new"]:
        return "new"
    if len(rest) == 1 and re.fullmatch(r"[0-9a-f]{6}", rest[0]):
        return "bare"
    if len(rest) >= 2 and rest[1] == "-s":
        return "offer"
    if len(rest) >= 2 and rest[1] == "-mount":
        return "mount"
    if len(rest) >= 2 and rest[1] == "-peek":
        return "view"
    if len(rest) >= 2 and rest[1] in CONSOLE_VERBS:
        return CONSOLE_VERBS[rest[1]]
    if len(rest) >= 2 and rest[0] and re.fullmatch(r"[0-9a-f]{6}", rest[0]):
        return "value"
    return "other"


def flow_texts(flow: list[dict], harness) -> list[dict]:
    """-> the texts pp handed to the agent, in the order the flow says them: the prompt of every launch
    (`conduction`, channel `prompt`) and the result of every call of the console (`tool-result`, channel
    `tool`), each with what the agent did until the next text -- the words said, the calls typed (their
    kind), the harness's own reading when it thought one --; a tool result that carries no text of pp
    (a file read) is skipped."""
    events = [one for one in flow if one.get("kind") not in ("step",)]
    calls: dict[str, str] = {}
    shells: dict[str, str] = {}
    texts: list[dict] = []
    current: dict | None = None

    def observed(kind: str, **fields) -> None:
        if current is not None:
            current["after"].append({"kind": kind, **fields})

    for one in events:
        kind = one.get("kind")
        if kind == "conduction":
            current = {"channel": "prompt", "launch": one.get("launch"), "exchange": one.get("exchange"),
                       "text": str(one.get("text") or ""), "after": []}
            texts.append(current)
        elif kind == "tool":
            shell = str(one.get("shell") or "")
            what = call_kind(shell)
            calls[str(one.get("id"))] = what
            shells[str(one.get("id"))] = shell.splitlines()[0] if shell else ""
            if what:
                observed("call", call=what, shell=shell.splitlines()[0] if shell else "")
        elif kind == "tool-result":
            what = calls.get(str(one.get("id")), "")
            if not what:
                continue
            current = {"channel": "tool", "launch": one.get("launch"), "text": str(one.get("content") or ""),
                       "error": bool(one.get("error")), "call": what, "shell": shells.get(str(one.get("id")), ""),
                       "after": []}
            texts.append(current)
        elif kind == "words":
            observed("words", text=str(one.get("text") or ""))
        elif kind == "thinking":
            text = str(one.get("text") or "")
            if text.startswith(("read ", "answer ", harness.HOLE)):
                observed("thought", text=text)
    return texts


def read_text(text: dict, harness) -> dict:
    """The READER: the text alone -- a block read by its grammar and the READINGS of the data (the candidate
    forms, the act when they agree), or the engine's own line read in ANSWERS; a result that carries no line
    of pp is read with the call that printed it: a script's own output behind a gesture."""
    semantics = harness.semantics
    reading = harness.grammar(text["text"])
    if reading is not None:
        forms, act, note = harness.foot(reading, text["channel"])
        return {"kind": "block", "forms": list(forms), "act": act, "note": note,
                "traits": harness.traits_of(reading, text["channel"]), "heading": reading.get("heading", ""),
                "instructions": [f"{one['keyword']} {one['form'] or ''} => {one['channel'] or ''}".strip()
                                 for one in reading["instructions"]]}
    name, row = harness.answered(text["text"], gesture=harness.gestured(shlex.split(text.get("shell") or "")))
    if row is None:
        return {"kind": "answer", "answer": harness.HOLE, "forms": [], "act": "", "note": ""}
    return {"kind": "answer", "answer": name, "forms": [row["form"]], "act": row["act"], "note": ""}


def observed_act(after: list[dict], kind: str) -> dict:
    """-> what the agent DID after a text: the words said -- productions pp took, those the trace holds as prints
    left out (`messages_of`); a launch's last message is never one --, the prints handed (`print`
    calls: the productions said on `terminal`), the calls typed by kind, and the act those make -- for a
    block: SAY_CALL, CALL, SAY_HAND_BACK, HAND_BACK (a print or a message says; a call that moves the run on
    counts, a gesture, a door or a view does not); for an answer: READ_ON when work followed, HAND_BACK when
    nothing did."""
    words = [one["text"] for one in after if one["kind"] == "words"]
    calls = [one["call"] for one in after if one["kind"] == "call"]
    prints = [one for one in calls if one == "print"]
    moving = [one for one in calls if one in MOVING]
    said = bool(words or prints)
    if kind == "block":
        act = ("SAY_CALL" if said and moving else "CALL" if moving else "SAY_HAND_BACK" if said else "HAND_BACK")
    else:
        act = "READ_ON" if (words or calls) else "HAND_BACK"
    done = [one["kind"] for one in after if one["kind"] in ("words", "call")]
    return {"words": len(words), "said": words, "prints": len(prints), "calls": calls, "act": act,
            "last": done[-1] if done else ""}


def conforming(expected: str, seen: dict, asks: bool = True) -> bool:
    """-> whether what the agent did conforms to the act the reader gives: a print first where a `=> terminal`
    line asks one (`asks`) -- each print call answers by its own text, so the act of a block that asks prints
    begins with one --, a call that moves the run where one is owed and nowhere else; on HAND_BACK the agent
    moves nothing. The last message of a launch is never judged: pp does not read it."""
    moving = any(one in MOVING for one in seen["calls"])
    prints = int(seen.get("prints") or 0)
    if expected == "SAY_CALL" and asks:
        return bool(prints)
    if expected in ("CALL", "SAY_CALL"):
        return moving or bool(prints)      # the prints kept from the chunks of a cut output come first
    if expected == "SAY_HAND_BACK":
        return (bool(prints) or not asks) and not moving
    if expected == "HAND_BACK":
        return not moving
    if expected == "STOP":
        return not moving
    if expected == "READ_ON":
        return not moving
    return False


def messages_of(flow: list[dict], trace: list[dict]) -> list[dict]:
    """-> the flow of a relayed exchange with its MESSAGES alone for `words`: the house's flow also says as
    `words` each production the trace holds as pp took it (`is_print`), and a print is judged at the trace, by
    the `answer` of its step, never as a message -- a `words` whose text is one of those productions is left
    out, each production once, so that a message saying a production again stays."""
    taken: dict[str, int] = {}
    for event in trace:
        if is_print(event):
            taken[str(event.get("given") or "")] = taken.get(str(event.get("given") or ""), 0) + 1
    said = []
    for one in flow:
        text = str(one.get("text") or "")
        if one.get("kind") == "words" and taken.get(text):
            taken[text] -= 1
            continue
        said.append(one)
    return said


def lines_of(name: str, run: dict, flow: list[dict], trace: list[dict], harness) -> list[dict]:
    """-> the LINES of one exchange: the texts the flow says handed -- its `words` the messages alone
    (`messages_of`) --, each aligned with the oracle's text of its channel in order, read by the reader, judged against what the agent did. A text the console
    answered without playing anything (a bounce, the block a name not offered brings back) has no item of
    the trace: its oracle says the run did not move."""
    semantics = harness.semantics
    items = outputs_of(trace)
    oracle = oracle_texts(items, semantics)
    texts = flow_texts(messages_of(flow, trace), harness)
    cursors = {"prompt": 0, "tool": 0}
    by_channel = {"prompt": [one for one in oracle if one["channel"] == "prompt"],
                  "tool": [one for one in oracle if one["channel"] == "tool"]}
    lines = []
    last_form = ""
    skipped: list[dict] = []
    wake = None
    for n, text in enumerate(texts, 1):
        read = read_text(text, harness)
        channel = text["channel"]
        queue = by_channel[channel]
        if channel == "prompt" and text.get("exchange") is not None:
            if wake is not None and text["exchange"] != wake:
                # the first text of a later wake-up on a parked run (`again:`): the root at its end that the
                # launcher's own call rendered before it was never handed -- skipped, counted as such
                while (cursors[channel] < len(queue) and queue[cursors[channel]]["kind"] == "output"
                       and queue[cursors[channel]]["form"] == "M"):
                    skipped.append(queue[cursors[channel]])
                    cursors[channel] += 1
            wake = text["exchange"]
        at = cursors[channel]
        expected = None
        due = queue[at] if at < len(queue) else None
        if read["kind"] == "answer":
            # an answer the trace knows (a held line, a gesture, a refusal) consumes the oracle's item of its
            # name; one the console gave without playing anything (a bounce) has no item: the run did not move
            if due is not None and due["kind"] == "answer" and due["answer"] == read["answer"]:
                expected = {**due, "moved": True}
                cursors[channel] += 1
            else:
                state = semantics.FORMS["D"]["tool"]
                expected = {"kind": "answer", "form": "D", "answer": "bounce", "awaits": _awaits(last_form),
                            "owes": state["owes"], "comes": state["comes"], "act": "HAND_BACK", "moved": False,
                            "zone": "bounce"}
        elif channel == "tool" and (text.get("error") or due is None or due["kind"] != "output"):
            # a block in a tool result the trace rendered no output for: the VIEW of the block that stands, of
            # the form `view_form` gives it; nothing moved. A view the trace says (`offer-absent`, a call caught:
            # the oracle's view item) is consumed and gives the line its zone; a view it does not say (a `-peek`)
            # is read on the text alone
            form = view_form(last_form)
            state = semantics.FORMS[form]["tool"]
            zone = "free-step"
            if due is not None and due["kind"] == "view":
                zone = due["zone"]
                cursors[channel] += 1
            expected = {"kind": "output", "form": form, "answer": "view", "awaits": state["awaits"],
                        "owes": state["owes"], "comes": state["comes"], "act": "READ_ON", "moved": False,
                        "zone": zone}
        elif due is not None:
            expected = {**due, "moved": True}
            cursors[channel] += 1
            last_form = expected["form"]
        seen = observed_act(text["after"], read["kind"])
        line = {"n": n, "exchange": name, "root": run.get("root"), "channel": channel, "launch": text.get("launch"),
                "call": text.get("call", ""), "shell": text.get("shell", ""),
                "head": (text["text"].splitlines() or [""])[0][:80],
                "zone": (expected or {}).get("zone", "free-step"),
                "oracle": expected, "reader": read, "observed": seen}
        line["verdict"], line["why"] = judged(line, text)
        lines.append(line)
    unhanded = skipped + [one for channel in ("prompt", "tool") for one in by_channel[channel][cursors[channel]:]]
    never = [document for item in sorted({one["item"] for one in unhanded if one["kind"] == "output"})
             for document in items[item - 1].get("due", [])]
    prints_owed(lines, trace, never)
    return lines, unhanded


def prints_missed(trace: list[dict], never: list[str] | tuple = ()) -> list[str]:
    """-> the documents of the productions an exchange left UNPRINTED, in the order their steps were said: every
    step the trace says due (`print-due`), but those a print call captured (`is_print`) and those a door stood
    for (`print-by-door`). A debt the bound or the principal's next message lifted (`print-waived`) is a
    production pp never took: it stays in the list. No miss of the agent: the prints a renewal of the run
    dropped (`reopened`: the run starts again on what it re-serves), and those of an output no launch carried
    (`never`: the documents due of the outputs the flow never handed)."""
    due: list[str] = []
    for event in trace:
        document = str(event.get("document") or "")
        if event.get("kind") == "print-due":
            due.append(document)
        elif event.get("kind") == "reopened":
            due.clear()
        elif (is_print(event) or event.get("kind") == "print-by-door") and document in due:
            due.remove(document)
    for document in never:
        if document in due:
            due.remove(document)
    return due


def prints_owed(lines: list[dict], trace: list[dict], never: list[str] | tuple = ()) -> None:
    """The prints DUE against the prints taken, judged on the exchange whole: a production said on `terminal`
    that no print call handed is the agent's red -- written on the exchange's last line when that line stood
    green, the documents left kept on it (`prints_missed`) whatever its verdict. `never` names the documents
    due of the outputs no launch carried."""
    missed = prints_missed(trace, never)
    if not missed or not lines:
        return
    last = lines[-1]
    last["prints_missed"] = missed
    if last["verdict"] == "vert":
        last["verdict"] = "rouge-agent"
        last["why"] = f"{len(missed)} production(s) said on `terminal` never printed: {', '.join(missed)}"


def _awaits(last_form: str) -> str:
    """-> what the stack awaits after the last output handed: a message once the root is exhausted, a
    production otherwise (nothing where a refusal stopped the conduction)."""
    return "message" if last_form == "M" else ("nothing" if last_form == "S" else "production")


def judged(line: dict, text: dict) -> tuple[str, str]:
    """-> (verdict, why) of one line -- `trou` when the reader admits no form; `rouge-conduction` when it
    admits several, or one that is not the oracle's, or when the console bounced a call that moves nothing
    (a gesture: the run did not move, the agent lost nothing by playing it); `rouge-agent` when what the
    agent did is not the act the reader gives; `vert` otherwise."""
    read, oracle, seen = line["reader"], line["oracle"], line["observed"]
    if not read["forms"]:
        return "trou", "the reader admits no form"
    if oracle is None:
        return "trou", "no text of the oracle left for this one: the trace and the flow disagree"
    if read["kind"] == "answer":
        if oracle.get("answer") == "bounce" and is_gesture(text.get("shell", "")):
            return "rouge-conduction", "a gesture bounced: the run did not move, the call moved nothing"
        if read["forms"][0] != oracle["form"]:
            return "rouge-conduction", f"the line reads {read['forms'][0]}, the oracle says {oracle['form']}"
        if read["act"] != oracle["act"]:
            return "rouge-conduction", f"the line leads to {read['act']}, the oracle to {oracle['act']}"
        if str(read.get("answer") or "").startswith("printed") and read["act"] == "READ_ON":
            return "vert", ""          # the line of a print: the agent goes on with what stands -- a print, a call
        if not conforming(read["act"], seen):
            return "rouge-agent", f"the agent did {seen['act']} where {read['act']} was due"
        return "vert", ""
    if len(read["forms"]) > 1:
        return "rouge-conduction", f"the text admits {' or '.join(read['forms'])}: the oracle says {oracle['form']}"
    if read["forms"][0] != oracle["form"]:
        return "rouge-conduction", f"the text reads {read['forms'][0]}, the oracle says {oracle['form']}"
    due = oracle["act"] if oracle.get("answer") == "view" else read["act"]     # a view: the step stands, go on
    asks = any(one.endswith(f"=> {language.TERMINAL}") for one in read.get("instructions", []))
    if asks and due == "CALL" and read["forms"] == ["V"]:
        due = "SAY_CALL"           # the value waits behind the prints its text asks: a print comes first
    if not conforming(due, seen, asks):
        if asks and not seen.get("prints") and due in ("SAY_CALL", "SAY_HAND_BACK"):
            return "rouge-agent", "the agent printed none of the productions its text asks on `terminal`"
        return "rouge-agent", f"the agent did {seen['act']} where {due} was due"
    return "vert", ""


def is_gesture(shell: str) -> bool:
    """-> whether a call of the console was a GESTURE: `-s <script> …`, the script's name opening on `pp-`
    (the product's own convention for a skill's script), never a door or a contract opened as a step."""
    words = shlex.split(shell) if shell else []
    return "-s" in words and words.index("-s") + 1 < len(words) and words[words.index("-s") + 1].startswith("pp-")


def sheet_lines(folder: Path, name: str, harness) -> tuple[list[dict], list[dict]]:
    """-> (lines, the oracle's texts never handed) of the exchange kept under `folder`, read from its artifacts:
    `run.json`, `flow.jsonl`, `trace.jsonl`."""
    run = json.loads((folder / "run.json").read_text(encoding="utf-8")) if (folder / "run.json").is_file() else {}
    return lines_of(name, run, _lines(folder / "flow.jsonl"), _lines(folder / "trace.jsonl"), harness)


def _lines(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("{"):
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            continue
    return found


def masked_by(line: dict, mask: list[str]) -> bool:
    """-> whether a line is under the MASK: its zone named, or `agent` named and the line `rouge-agent`."""
    return line.get("zone", "") in mask or (AGENT_MASK in mask and line["verdict"] == "rouge-agent")


def counted(lines: list[dict]) -> dict:
    return {verdict: sum(1 for one in lines if one["verdict"] == verdict) for verdict in VERDICTS}


def expectations_of(name: str, run: dict, flow: list[dict]) -> list[dict]:
    """-> the EXPECTATION of an exchange judged: one entry per key the root expects -- `words` (the `words` of
    the flow whole: every production pp took by its print call, as the house's flow says it, and every
    message the agent said at the end of a launch), `launches` (read from the coverage), `parked`, `proofs`
    (the answers to a PROVE) and `calls` (the calls of the console) -- with what was seen and whether it
    held; nothing when the root expects nothing."""
    expect = run.get("expect") or {}
    if not expect:
        return []
    covered = run.get("coverage") or {}
    seen = {"words": sum(1 for one in flow if one.get("kind") == "words"),
            "launches": covered.get("launches"), "parked": bool(covered.get("parked")),
            "proofs": int((covered.get("zones") or {}).get("proof", 0)), "calls": covered.get("calls")}
    judged = []
    for key in EXPECT_KEYS:
        if key not in expect:
            continue
        wanted = expect[key]
        judged.append({"exchange": name, "key": key, "expected": wanted, "seen": seen[key], "held": seen[key] == wanted})
    return judged


def sheet_table(lines: list[dict], left: list[dict], zones: dict[str, dict], title: str,
                mask: list[str] | None = None, expectations: list[dict] | None = None) -> tuple[dict, str]:
    """-> (sheet.json, SHEET.md): the lines, each with its zone and its mask flag, then the foot -- the
    count by verdict, by channel, by zone of the line and by zone crossed (the coverage of each line's
    exchange), every count OUTSIDE the mask, the masked lines counted apart with their reds; the
    expectations judged per exchange; the oracle's texts no launch carried (`left`): the root at its end
    (form M) is what the LAUNCHER PARKS ON, read on the trace and handed to no agent -- counted
    `launcher_parked`, apart --, a text of an exchange the launcher's bound stopped (`launches-spent`, the
    output kept `pending` for the next wake-up) is counted `launcher_kept`, apart; any other text is
    `unhanded`, never expected. A mask changes no verdict: a masked line keeps it and carries
    `masked: true`."""
    mask = list(mask or [])
    expectations = list(expectations or [])
    parked = [one for one in left if one.get("form") == "M"]
    kept_ = [one for one in left if one.get("form") != "M" and one.get("bound")]
    unhanded = [one for one in left if one.get("form") != "M" and not one.get("bound")]
    for one in lines:
        one["masked"] = masked_by(one, mask)
    shown_lines = [one for one in lines if not one["masked"]]
    hidden = [one for one in lines if one["masked"]]
    by_verdict = counted(shown_lines)
    by_channel = {}
    for one in shown_lines:
        slot = by_channel.setdefault(one["channel"], {verdict: 0 for verdict in VERDICTS})
        slot[one["verdict"]] += 1
    by_line_zone: dict[str, dict] = {}
    for one in shown_lines:
        slot = by_line_zone.setdefault(one["zone"], {verdict: 0 for verdict in VERDICTS})
        slot[one["verdict"]] += 1
    by_zone: dict[str, dict] = {}
    for one in shown_lines:
        for zone in sorted(zones.get(one["exchange"], {})):
            slot = by_zone.setdefault(zone, {verdict: 0 for verdict in VERDICTS})
            slot[one["verdict"]] += 1
    apart = {"lines": len(hidden), "red": sum(1 for one in hidden if one["verdict"] in REDS),
             "by_verdict": counted(hidden)}
    missed = sorted({one["exchange"] for one in expectations if not one["held"]})
    data = {"title": title, "mask": mask, "lines": lines, "launcher_parked": parked, "launcher_kept": kept_,
            "unhanded": unhanded,
            "by_verdict": by_verdict,
            "by_channel": by_channel, "by_line_zone": by_line_zone, "by_zone": by_zone, "masked": apart,
            "expect": expectations, "expect_missed": len(missed)}
    out = [f"# SHEET -- {title}", "",
           f"{len(lines)} line(s), {len(shown_lines)} outside the mask: " + ", ".join(f"{by_verdict[v]} {v}" for v in VERDICTS)
           + f"; {apart['lines']} masked (`{','.join(mask) or '-'}`), {apart['red']} red among them; "
           f"{len(parked)} text(s) the launcher parked on (the root at its end), {len(kept_)} kept at the launcher's "
           f"bound, {len(unhanded)} never handed"
           + (f"; {len(missed)} exchange(s) whose expectation is not held" if expectations else "") + ".", "",
           "## The lines", "",
           "| # | exchange | ch | launch | zone | text | oracle | reader | observed | verdict | mask | why |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for one in lines:
        oracle = one["oracle"] or {}
        read = one["reader"]
        seen = one["observed"]
        oracle_cell = (f"{oracle.get('form', '?')} · {oracle.get('awaits', '')} · {oracle.get('owes', '')} · "
                       f"{oracle.get('comes', '')} · {oracle.get('act', '')}" if oracle else "—")
        reader_cell = (f"{' | '.join(read['forms']) or 'trou'} · {read['act'] or read['note'] or '—'}")
        seen_cell = f"{seen['act']} · {seen['words']} words · {' '.join(seen['calls']) or 'no call'}"
        head = one["head"].replace("|", "\\|")
        out.append(f"| {one['n']} | {one['exchange']} | {one['channel']} | {one['launch'] or ''} | {one['zone']} | `{head}` | "
                   f"{oracle_cell} | {reader_cell} | {seen_cell} | {one['verdict']} | {'masked' if one['masked'] else ''} | "
                   f"{one['why']} |")
    out += ["", "## By verdict, outside the mask", "", "| verdict | lines |", "|---|---|"]
    out += [f"| {verdict} | {by_verdict[verdict]} |" for verdict in VERDICTS]
    out += ["", "## By channel", "", "| channel | " + " | ".join(VERDICTS) + " |", "|---|" + "---|" * len(VERDICTS)]
    out += [f"| {channel} | " + " | ".join(str(by_channel[channel][v]) for v in VERDICTS) + " |"
            for channel in sorted(by_channel)]
    out += ["", "## By zone of the line", "", "| zone | " + " | ".join(VERDICTS) + " |", "|---|" + "---|" * len(VERDICTS)]
    out += [f"| {zone} | " + " | ".join(str(by_line_zone[zone][v]) for v in VERDICTS) + " |" for zone in sorted(by_line_zone)]
    out += ["", "## By zone crossed", "", "| zone | " + " | ".join(VERDICTS) + " |", "|---|" + "---|" * len(VERDICTS)]
    out += [f"| {zone} | " + " | ".join(str(by_zone[zone][v]) for v in VERDICTS) + " |" for zone in sorted(by_zone)]
    if mask:
        out += ["", "## Masked, apart", "", f"`{','.join(mask)}`: {apart['lines']} line(s), {apart['red']} red -- "
                + ", ".join(f"{apart['by_verdict'][v]} {v}" for v in VERDICTS)]
    if expectations:
        out += ["", "## EXPECT -- what the manifest expects of each exchange", "",
                "| exchange | key | expected | seen | held |", "|---|---|---|---|---|"]
        out += [f"| {one['exchange']} | {one['key']} | {one['expected']} | {one['seen']} | {'yes' if one['held'] else 'NO'} |"
                for one in expectations]
    for title_, found in (("Parked by the launcher -- the root at its end, read on the trace, handed to no launch", parked),
                          ("Kept by the launcher -- its bound spent, the output pending for the next wake-up", kept_),
                          ("Never handed -- what the oracle rendered and no launch carried", unhanded)):
        if found:
            out += ["", f"## {title_}", "", "| exchange | ch | form | zone | stack |", "|---|---|---|---|---|"]
            out += [f"| {one.get('exchange', '')} | {one['channel']} | {one['form']} | {one.get('zone', '')} | {one.get('stack', '')} |"
                    for one in found]
    return data, "\n".join(out) + "\n"


def sheeted(out: Path, mask: list[str] | None = None) -> dict:
    """Writes, from the artifacts kept under `out` alone, `sheet.json` and `SHEET.md` -- the ONE writer of the
    two, played by `play` and by `sheet <date>`: replayed on the same artifacts, under the same mask, it
    renders the same bytes. -> the sheet."""
    campaign, runs, _stats = artifacts_of(out)
    harness = harness_module()
    lines, left, zones, expectations = [], [], {}, []
    for run in runs:
        name = run["coverage"]["name"]
        folder = out / name
        found, left_ = sheet_lines(folder, name, harness)
        for one in found:
            one["n"] = len(lines) + 1
            lines.append(one)
        bound = bool((run["coverage"].get("zones") or {}).get("launcher-bound")) and not run["coverage"].get("parked")
        for one in left_:
            left.append({**one, "exchange": name, "bound": bound})
        zones[name] = run["coverage"].get("zones") or {}
        expectations += expectations_of(name, run, _lines(folder / "flow.jsonl"))
    data, text = sheet_table(lines, left, zones, f"`{campaign['set']}` under `{campaign['provider']}`, {campaign['date']}",
                             mask, expectations)
    keep(out, SHEET, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    keep(out, "SHEET.md", text)
    return data


def sheet_said(data: dict) -> str:
    said = ", ".join(f"{data['by_verdict'][v]} {v}" for v in VERDICTS)
    apart = data.get("masked") or {}
    if apart.get("lines"):
        said += f"; {apart['lines']} masked ({apart['red']} red)"
    if data.get("expect"):
        said += f"; {data['expect_missed']} expectation(s) missed"
    return said


# --- the comparison of two sheets ------------------------------------------------------------------

def picked(line: dict) -> dict:
    """-> what a comparison keeps of a line: its verdict, its zone, its mask flag, the forms read, the act seen."""
    return {"n": line["n"], "verdict": line["verdict"], "zone": line.get("zone", ""), "masked": bool(line.get("masked")),
            "oracle": (line.get("oracle") or {}).get("form"), "reader": list((line.get("reader") or {}).get("forms") or []),
            "observed": (line.get("observed") or {}).get("act"), "head": line.get("head", "")}


def ranked(lines: list[dict]) -> dict[tuple, dict]:
    """-> the lines keyed by (exchange, channel, rank): the rank of a line among the lines of its exchange on
    its channel, in the order they were handed."""
    keyed, ranks = {}, {}
    for one in lines:
        at = (one["exchange"], one["channel"])
        ranks[at] = ranks.get(at, 0) + 1
        keyed[(one["exchange"], one["channel"], ranks[at])] = one
    return keyed


def compared(out: Path, before_out: Path) -> dict:
    """Writes `compare.json` and `COMPARE.md` under `out` from the two sheets alone -- the sheet under `out`
    (after) against the sheet under `before_out` (before): the lines paired by (exchange, channel, rank),
    the verdict before and after, the lines that appeared and disappeared, the counts by verdict and by
    zone of each side; replayed on the same sheets it renders the same bytes. -> the comparison."""
    sheets = []
    for folder in (before_out, out):
        path = folder / SHEET
        if not path.is_file():
            raise Refused("sheet-missing", f"no `{SHEET}` under {folder}: `sheet <date>` writes it first")
        sheets.append(json.loads(path.read_text(encoding="utf-8")))
    before, after = sheets
    was, is_ = ranked(before.get("lines", [])), ranked(after.get("lines", []))
    paired = [{"exchange": key[0], "channel": key[1], "rank": key[2], "before": picked(was[key]), "after": picked(is_[key]),
               "changed": was[key]["verdict"] != is_[key]["verdict"]} for key in is_ if key in was]
    appeared = [{"exchange": key[0], "channel": key[1], "rank": key[2], "after": picked(is_[key])} for key in is_ if key not in was]
    disappeared = [{"exchange": key[0], "channel": key[1], "rank": key[2], "before": picked(was[key])} for key in was if key not in is_]

    def side(sheet: dict) -> dict:
        return {"lines": len(sheet.get("lines", [])), "by_verdict": sheet.get("by_verdict", {}),
                "masked": sheet.get("masked", {"lines": 0, "red": 0}), "mask": sheet.get("mask", []),
                "by_line_zone": sheet.get("by_line_zone", {}), "expect_missed": sheet.get("expect_missed", 0)}

    by_zone: dict[str, dict] = {}
    for name, sheet in (("before", before), ("after", after)):
        for one in sheet.get("lines", []):
            slot = by_zone.setdefault(one.get("zone", ""), {"before": {v: 0 for v in VERDICTS}, "after": {v: 0 for v in VERDICTS}})
            slot[name][one["verdict"]] += 1
    counts = {"paired": len(paired), "changed": sum(1 for one in paired if one["changed"]), "appeared": len(appeared),
              "disappeared": len(disappeared), "before": side(before), "after": side(after), "by_zone": by_zone}
    data = {"before": before_out.name, "after": out.name, "before_title": before.get("title", ""),
            "after_title": after.get("title", ""), "paired": paired, "appeared": appeared, "disappeared": disappeared,
            "counts": counts}
    lines = [f"# COMPARE -- {after.get('title', out.name)} against {before.get('title', before_out.name)}", "",
             f"{counts['paired']} line(s) paired by (exchange, channel, rank): {counts['changed']} changed verdict, "
             f"{counts['appeared']} appeared, {counts['disappeared']} disappeared.", "",
             "## The two sides", "",
             "| side | lines | " + " | ".join(VERDICTS) + " | masked | masked red | mask | expectations missed |",
             "|---|---|" + "---|" * len(VERDICTS) + "---|---|---|---|"]
    for name in ("before", "after"):
        one = counts[name]
        lines.append(f"| {name} | {one['lines']} | " + " | ".join(str(one['by_verdict'].get(v, 0)) for v in VERDICTS)
                     + f" | {one['masked'].get('lines', 0)} | {one['masked'].get('red', 0)} | `{','.join(one['mask']) or '-'}` | "
                     f"{one['expect_missed']} |")
    lines += ["", "## By zone of the line", "", "| zone | " + " | ".join(f"before {v}" for v in VERDICTS) + " | "
              + " | ".join(f"after {v}" for v in VERDICTS) + " |", "|---|" + "---|" * (2 * len(VERDICTS))]
    lines += [f"| {zone} | " + " | ".join(str(by_zone[zone]['before'][v]) for v in VERDICTS) + " | "
              + " | ".join(str(by_zone[zone]['after'][v]) for v in VERDICTS) + " |" for zone in sorted(by_zone)]
    changed = [one for one in paired if one["changed"]]
    if changed:
        lines += ["", "## The lines whose verdict changed", "",
                  "| exchange | ch | rank | zone | before | after | reader before | reader after | observed before | observed after |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        lines += [f"| {one['exchange']} | {one['channel']} | {one['rank']} | {one['after']['zone']} | {one['before']['verdict']} | "
                  f"{one['after']['verdict']} | {' '.join(one['before']['reader'])} | {' '.join(one['after']['reader'])} | "
                  f"{one['before']['observed']} | {one['after']['observed']} |" for one in changed]
    for name, found in (("appeared", appeared), ("disappeared", disappeared)):
        if found:
            side_name = "after" if name == "appeared" else "before"
            lines += ["", f"## The lines that {name}", "", "| exchange | ch | rank | zone | verdict | text |", "|---|---|---|---|---|---|"]
            lines += [f"| {one['exchange']} | {one['channel']} | {one['rank']} | {one[side_name]['zone']} | "
                      f"{one[side_name]['verdict']} | `{one[side_name]['head'].replace('|', chr(92) + '|')}` |" for one in found]
    keep(out, COMPARE, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    keep(out, "COMPARE.md", "\n".join(lines) + "\n")
    return data


def sheet(argv: list[str]) -> int:
    if "--run" in argv:
        return run_sheet(argv)
    if not argv or argv[0].startswith("--"):
        raise Refused("date-missing", "`sheet <date> [--out <dir>] [--mask <zones>] [--against <date>]`, or "
                      "`sheet --house <ws> --agent <name> --run <key> --out <dir>`")
    set_dir = set_of(argv)
    mask = mask_of(argv)
    out = Path(option(argv, "--out", str(set_dir.parent / "out"))) / argv[0]
    data = sheeted(out, mask)
    print(f"campaign: sheet of {argv[0]} -- {len(data['lines'])} line(s): {sheet_said(data)}; {out / 'SHEET.md'}")
    against = option(argv, "--against")
    if against:
        told = compared(out, Path(against) if Path(against).is_dir() else out.parent / against)
        counts = told["counts"]
        print(f"campaign: {argv[0]} against {against} -- {counts['paired']} line(s) paired, {counts['changed']} changed, "
              f"{counts['appeared']} appeared, {counts['disappeared']} disappeared; {out / 'COMPARE.md'}")
    return 0


def run_sheet(argv: list[str]) -> int:
    """`sheet --house <ws> --agent <name> --run <key> --out <dir> [--mask <zones>]`: the sheet of ONE run of a
    house, its flow read by the house's console (`agent flow --json`) and its trace at the agent's slot, as
    `play` reads them; written under `<out>/<key>/`."""
    ws = option(argv, "--house")
    agent = option(argv, "--agent")
    key = option(argv, "--run")
    out = option(argv, "--out")
    if not (ws and agent and key and out):
        raise Refused("argument-missing", "`sheet --house <ws> --agent <name> --run <key> --out <dir>`: the four are owed")
    mask = mask_of(argv)
    house = Path(ws)
    console = house / "pp"
    agent_meta = house / agent / ".pp"
    if not console.is_file() or not agent_meta.is_dir():
        raise Refused("house-unknown", f"no console at {console} or no agent at {agent_meta}")
    if not re.fullmatch(r"[0-9a-f]{6}", key or ""):
        raise Refused("run-unknown", f"`{key}` names no run")
    try:
        persistence.slot_of(agent_meta, key)
        trace = trace_of(agent_meta, key)
    except Exception:                   # noqa: BLE001 -- a slot the face refuses: the run is unknown here
        trace = []
    if not trace:
        raise Refused("run-unknown", f"`{key}` has no trace at {agent_meta}")
    read = subprocess.run([str(console), "agent", "flow", agent, key, "--json"], cwd=house, capture_output=True, text=True)
    flow = [json.loads(line) for line in read.stdout.splitlines() if line.strip().startswith("{")]
    harness = harness_module()
    lines, left = lines_of(f"{agent}/{key}", {"root": None}, flow, trace, harness)
    data, text = sheet_table(lines, [{**one, "exchange": f"{agent}/{key}"} for one in left], {},
                             f"run {key} of {agent} at {house}", mask)
    folder = Path(out) / key
    keep(folder, SHEET, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    keep(folder, "SHEET.md", text)
    print(f"campaign: sheet of run {key} -- {len(lines)} line(s): {sheet_said(data)}; {folder / 'SHEET.md'}")
    return 0


# --- the census: the coverage section of the model's document ----------------------------------------

def evidence_campaign(evidence: Path, name: str) -> dict:
    """-> one campaign of the evidence: its `campaign.json`, `coverage.json` and `sheet.json` read under
    `<evidence>/<name>/`; `campaign-missing` when none stands there, `evidence-unversioned` when its
    `campaign.json` does not say the engine it played on."""
    folder = evidence / name
    path = folder / CAMPAIGN
    if not path.is_file():
        raise Refused("campaign-missing", f"no `{CAMPAIGN}` under {folder}: no campaign of that name in the evidence")
    campaign = json.loads(path.read_text(encoding="utf-8"))
    if not campaign.get("engine"):
        raise Refused("evidence-unversioned", f"{path} does not say the engine it played on (`engine`): "
                                              "a campaign of the census names its engine")
    coverage = json.loads((folder / "coverage.json").read_text(encoding="utf-8")) if (folder / "coverage.json").is_file() else {}
    sheet_ = json.loads((folder / SHEET).read_text(encoding="utf-8")) if (folder / SHEET).is_file() else {}
    return {"name": name, "campaign": campaign, "coverage": coverage, "sheet": sheet_}


def relayed_exchange(exchange: dict) -> bool:
    """-> whether an exchange of the coverage played on the campaign's channel: the campaigns before 2026-11-21
    played a second one, and those before the launcher said a channel carry the field `conduction` -- neither
    is read."""
    return "conduction" not in exchange and exchange.get("channel") == CHANNEL


def complete(one: dict) -> bool:
    """-> whether a campaign played every root of its set on the campaign's channel."""
    roots = set(one["campaign"].get("roots") or [])
    played = {exchange.get("root") for exchange in one["coverage"].get("exchanges", []) if relayed_exchange(exchange)}
    return bool(roots) and roots <= played


def campaign_names(evidence: Path) -> list[str]:
    return sorted(one.name for one in evidence.iterdir() if (one / CAMPAIGN).is_file()) if evidence.is_dir() else []


def latest_complete_model(evidence: Path) -> str:
    """-> the name of the latest complete `model` campaign of the evidence; `model-missing` when none."""
    found = ""
    for name in campaign_names(evidence):
        campaign = json.loads((evidence / name / CAMPAIGN).read_text(encoding="utf-8"))
        if campaign.get("provider") != PROVIDER_MODEL:
            continue
        if campaign.get("engine") and complete(evidence_campaign(evidence, name)):
            found = name
    if not found:
        raise Refused("model-missing", f"no complete `model` campaign (every root played, its engine "
                                       f"said) under {evidence}: play one, or name one with `--model <date>`")
    return found


def real_names(evidence: Path) -> list[str]:
    return [name for name in campaign_names(evidence)
            if json.loads((evidence / name / CAMPAIGN).read_text(encoding="utf-8")).get("provider") != PROVIDER_MODEL]


def verdict_counts(sheet_: dict) -> str:
    by_verdict = sheet_.get("by_verdict") or {}
    return ", ".join(f"{by_verdict.get(v, 0)} {v}" for v in VERDICTS) if by_verdict else "no sheet"


def census_of(zones: dict, model: dict, reals: list[dict]) -> dict:
    """-> the census: per zone, the roots the model campaign crosses it with, the real exchanges that cross it on
    the same engine and on an older one, the red lines among the former, and the status; the count by status.
    The exchanges of another channel than the campaign's are not read (`relayed_exchange`)."""
    engine = model["campaign"]["engine"]
    rows = []
    for zone, spec in zones.items():
        roots = sorted({str(exchange.get("root")) for exchange in model["coverage"].get("exchanges", [])
                        if relayed_exchange(exchange) and exchange.get("zones", {}).get(zone)})
        same, older, red = 0, 0, 0
        for real in reals:
            crossing = {exchange["name"] for exchange in real["coverage"].get("exchanges", [])
                        if relayed_exchange(exchange) and exchange.get("zones", {}).get(zone)}
            if real["campaign"]["engine"] == engine:
                same += len(crossing)
                red += sum(1 for line in real["sheet"].get("lines", [])
                           if line.get("exchange") in crossing and line.get("verdict") in ("rouge-conduction", "trou"))
            else:
                older += len(crossing)
        if not roots:
            status = "silent"
        else:
            status = "safe" if same >= SAFE_REAL and red == 0 else "measured"
        rows.append({"zone": zone, "what": spec["what"], "roots": roots, "real_same": same, "real_older": older,
                     "real_red": red, "status": status})
    counts = {status: sum(1 for row in rows if row["status"] == status) for status in STATUSES}
    return {"model": model, "reals": reals, "rows": rows, "counts": counts}


def census_text(census: dict, evidence: Path) -> str:
    """-> the coverage section, its two markers included: no date of now, the campaigns' own alone."""
    model, reals, rows, counts = census["model"], census["reals"], census["rows"], census["counts"]
    campaign = model["campaign"]
    engine = campaign["engine"]
    where = str(evidence.relative_to(ROOT)) if evidence.is_relative_to(ROOT) else str(evidence)
    exchanges = [one for one in model["coverage"].get("exchanges", []) if relayed_exchange(one)]
    marker = (f"{COVERAGE_BEGIN} model={model['name']} engine={engine} "
              f"real={','.join(one['name'] for one in reals) or 'none'} zones={len(rows)} safe={counts['safe']} -->")
    out = [marker, "## 8. The coverage -- the census of the conduction tests", "",
           f"Written by `tools/campaign/campaign.py zones` from the evidence under `{where}/`, never by hand; replayed "
           "on the same evidence it renders the same bytes. The exchanges read are those of the campaign's one "
           "channel, the house conducting. "
           f"A zone is `safe` when the model campaign crosses it and {SAFE_REAL} real "
           "exchanges at least, on the same engine, cross it with no `rouge-conduction` and no `trou` on their lines; "
           "`measured` when the model campaign crosses it; `silent` when never.", "",
           f"**The model campaign**: `{model['name']}` -- set `{campaign.get('set')}`, engine `{engine}`, "
           f"{len(exchanges)} exchanges ({len(campaign.get('roots') or [])} roots), "
           f"the sheet: {verdict_counts(model['sheet'])}.", ""]
    if reals:
        out.append("**The real campaigns**: " + "; ".join(
            f"`{one['name']}` -- `{one['campaign'].get('provider')}` {one['campaign'].get('model') or 'default'}, "
            f"effort {one['campaign'].get('effort') or 'default'}, engine `{one['campaign']['engine']}`"
            + (" (older)" if one["campaign"]["engine"] != engine else "")
            + f", {sum(1 for ex in one['coverage'].get('exchanges', []) if relayed_exchange(ex))} exchanges, "
            f"the sheet: {verdict_counts(one['sheet'])}"
            for one in reals) + ".")
    else:
        out.append("**The real campaigns**: none read.")
    out += ["", "| zone | what | model: roots | real: exchanges (same engine / older) | status |",
            "|---|---|---|---|---|"]
    for row in rows:
        model_cell = f"{len(row['roots'])} root{'s' if len(row['roots']) > 1 else ''}" if row["roots"] else "none"
        real_cell = f"{row['real_same']} / {row['real_older']}" + (f" ({row['real_red']} red)" if row["real_red"] else "")
        out.append(f"| `{row['zone']}` | {row['what']} | {model_cell} | {real_cell} | {row['status']} |")
    out += ["", f"{len(rows)} zones: " + ", ".join(f"{status} {counts[status]}" for status in STATUSES) + ".", COVERAGE_END]
    return "\n".join(out) + "\n"


def written_between(doc: Path, section: str) -> str:
    """Writes the section between the two markers of `doc` -- replaced when they stand, appended at the end
    otherwise; nothing else of the document moves. -> `replaced` or `inserted`."""
    if not doc.is_file():
        raise Refused("doc-missing", f"{doc} does not stand: the census is written in a document that exists")
    text = doc.read_text(encoding="utf-8")
    begin, end = text.find(COVERAGE_BEGIN), text.find(COVERAGE_END)
    if begin >= 0 and end >= 0:
        stop = end + len(COVERAGE_END)
        tail = text[stop:]
        text = text[:begin] + section.rstrip("\n") + tail
        how = "replaced"
    else:
        text = text.rstrip("\n") + "\n\n" + section
        how = "inserted"
    tmp = doc.with_suffix(doc.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(doc)
    return how


def marker_of(doc: Path) -> dict:
    """-> the keys of the begin marker of the section in `doc`; `coverage-missing` when none stands."""
    text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
    hit = re.search(re.escape(COVERAGE_BEGIN) + r"([^\n]*?)-->", text)
    if not hit:
        raise Refused("coverage-missing", f"{doc} carries no coverage section: play `zones` first")
    return dict(re.findall(r"(\w+)=(\S+)", hit.group(1)))


def zones(argv: list[str]) -> int:
    zones_ = _zones_declared()
    doc = Path(option(argv, "--doc", str(MODEL_DOC)))
    if "--check" in argv:
        marker = marker_of(doc)
        if marker.get("engine") != VERSION:
            raise Refused("engine-moved", f"the census of {doc} was written on engine {marker.get('engine')} and the engine "
                                          f"in place is {VERSION}: play the campaigns again and write the census before "
                                          "a publication")
        print(f"campaign: the census of {doc} stands on engine {VERSION} -- model campaign {marker.get('model')}, real "
              f"{marker.get('real')}, {marker.get('safe')} of {marker.get('zones')} zones safe")
        return 0
    evidence = Path(option(argv, "--evidence", str(EVIDENCE)))
    model_name = option(argv, "--model") or latest_complete_model(evidence)
    model = evidence_campaign(evidence, model_name)
    reals = [evidence_campaign(evidence, name) for name in (options(argv, "--real") or real_names(evidence))]
    census = census_of(zones_, model, reals)
    how = written_between(doc, census_text(census, evidence))
    counts = census["counts"]
    print(f"campaign: the census {how} in {doc} -- model {model_name} on engine {model['campaign']['engine']}, "
          f"{len(reals)} real campaign(s); {len(census['rows'])} zones: "
          + ", ".join(f"{status} {counts[status]}" for status in STATUSES))
    return 0


# --- the operator's bench --------------------------------------------------------------------------

def house_of(out: Path, root: str) -> Path:
    return out / root


def prepare_one(manifest: dict, out: Path, root: str, fresh: bool) -> str:
    """Builds ONE house for `root` under `out` -> `built` or `standing`; refuses by name."""
    ws = house_of(out, root)
    agent_name = manifest["agent"]
    if (ws / "pp").is_file() and (ws / agent_name / ".pp").is_dir() and not fresh:
        # a standing house follows the SOURCE it was installed from: `upgrade` re-vendors the engine and
        # the packages at the versions the source holds now -- played by the SOURCE's engine on the house
        moved = subprocess.run([sys.executable, str(ENGINE), "--instance", str(ws / ".pp"), "upgrade"],
                               cwd=ws, capture_output=True, text=True)
        if moved.returncode != 0:
            raise Refused("upgrade-failed", f"{root}: {moved.stderr.strip()[-300:]}")
        wire_house(ws)
        capped(ws, agent_name)
        return "standing"
    if ws.exists():
        shutil.rmtree(ws)
    ws.mkdir(parents=True)
    done = subprocess.run([sys.executable, str(ENGINE), "-install", str(ws), "agent", "ui", *manifest["packages"],
                           "-slug", f"{manifest['name']}-{root}"], capture_output=True, text=True)
    if done.returncode != 0:
        raise Refused("install-failed", done.stderr.strip()[-300:])
    born = subprocess.run([str(ws / "pp"), "agent", "add", agent_name], cwd=ws, capture_output=True, text=True)
    if born.returncode != 0:
        raise Refused("agent-add-failed", born.stderr.strip()[-300:])
    agent = ws / agent_name
    procs = agent / ".pp" / "procs"
    procs.mkdir(parents=True, exist_ok=True)
    spec = manifest["roots"][root]
    for document in (Path(manifest["set"]) / root).iterdir():
        if document.is_file():
            shutil.copy(document, procs / document.name)
    if spec["door"]:
        # the door is OFFERED to the turn's WORK: the operator's message asks to open it
        (procs / "TURN.md").write_text(f"---\nname: TURN\ntools: |\n  +{Path(spec['door']).stem}\n---\n",
                                       encoding="utf-8")
    laid(manifest, agent)
    built = subprocess.run([str(agent / "pp"), "-build"], cwd=agent, capture_output=True, text=True)
    if built.returncode != 0:
        raise Refused("build-failed", f"{root}: {built.stderr.strip()[-300:]}")
    wire_house(ws)
    capped(ws, agent_name)
    return "built"


def capped(ws: Path, agent_name: str) -> None:
    """Sets the agent's `max_harness_tool_output` back to the host's cap through the engine's settings
    face: `agent add` raises it to 200000 (the cap of a relayed output, which goes to the harness's
    stdin), but a view, a manual or an inline answer returns in a TOOL RESULT the host cuts."""
    settings.write(ws / agent_name / ".pp", "max_harness_tool_output", HOST_CAP)


def wire_house(ws: Path) -> None:
    """Wires Claude Code at the HOUSE's root and pins `ui` when a standing house lacks it; idempotent."""
    if not (ws / ".claude" / "settings.json").is_file():
        subprocess.run([str(ws / "pp"), "-install", "-claude"], cwd=ws, capture_output=True, text=True)
    pinned = subprocess.run([str(ws / "pp"), "version"], cwd=ws, capture_output=True, text=True).stdout
    if "\nui " not in pinned and not pinned.startswith("ui "):
        subprocess.run([str(ws / "pp"), "add", "ui"], cwd=ws, capture_output=True, text=True)


def prepare(argv: list[str]) -> int:
    set_dir = set_of(argv)
    manifest = manifest_of(set_dir)
    asked = asked_of(argv, manifest)
    out = Path(option(argv, "--out", str(HOUSES / manifest["name"])))
    roots = asked["roots"] or list(manifest["roots"])
    for root in roots:
        state = prepare_one(manifest, out, root, "--fresh" in argv)
        print(f"campaign: {root} -- {state} at {house_of(out, root)}")
    (out / "RUNSHEET.md").write_text(runsheet_text(manifest, out, roots), encoding="utf-8")
    print(f"campaign: {len(roots)} house(s) under {out}, the run sheet at {out / 'RUNSHEET.md'} -- nothing launched")
    return 0


def runsheet_text(manifest: dict, out: Path, roots: list[str] | None = None) -> str:
    agent = manifest["agent"]
    lines = [f"# The run sheet of `{manifest['name']}`", "",
             "One house per root, under `" + str(out) + "`. For each root, play its message at the post (the",
             "house calls pp) and look at what you see: the productions printed at their step, the headers, the",
             "proof.", ""]
    for n, root in enumerate(roots or manifest["roots"], 1):
        spec = manifest["roots"][root]
        ws = house_of(out, root)
        lines += [f"## {n}. `{root}`" + (f" -- the door `{Path(spec['door']).stem}`" if spec["door"] else ""), "",
                  f"- house: `{ws}`",
                  f"- message: « {spec['manual']} »",
                  f"- post: `cd {ws} && ./pp ui {agent}`, type the message in the conversation tab",
                  f"- look at: {spec['look']}", ""]
    lines += ["After the runs, each house keeps its runs: `./pp agent status <agent> --json`, `agent flow`,",
              "`agent exchanges`, `agent stats` read them.", ""]
    return "\n".join(lines)


def runsheet(argv: list[str]) -> int:
    set_dir = set_of(argv)
    manifest = manifest_of(set_dir)
    out = Path(option(argv, "--out", str(HOUSES / manifest["name"])))
    print(runsheet_text(manifest, out))
    return 0


def main(argv: list[str]) -> int:
    verb = argv[0] if argv else ""
    try:
        if verb in ("plan", "--dry-run"):
            return plan(argv[1:])
        if verb == "play":
            return play(argv[1:])
        if verb == "prepare":
            return prepare(argv[1:])
        if verb == "runsheet":
            return runsheet(argv[1:])
        if verb == "sheet":
            return sheet(argv[1:])
        if verb == "report":
            return report(argv[1:])
        if verb == "zones":
            return zones(argv[1:])
        if verb == "turn":
            return turn_module().main(argv[1:])
    except Refused as refused:
        return refuse(refused.code, refused.detail)
    print(__doc__.split("\n\n")[1], file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
