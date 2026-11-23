"""The TURN -- ONE turn of a prompt played on a harness, without pp nor house: the verb `turn` of the
campaign's launcher (`campaign.py turn`).

THE SET. A set is a directory with its manifest `turn.yaml`. `files:` names the accessories laid in every
throwaway directory: a mapping of the name there to the path in the set, or a list of paths laid under
their own names. `variants:` maps each variant to its keys: `prompts:` (one file of the set, or several:
each file is one launch, and the next launch resumes the session of the one before), `fixed:` (the file of
the fixed part, in the set or outside it; left out, the variant plays none), `place:` (where the fixed part
goes: `system`, the default, or `head`) and `model:` (what the modelled LLM is told to do, a list of
one-key acts). `name:` and `description:` are free.

A REPETITION. Each repetition plays in a fresh throwaway directory (`mkdtemp`), made a git repository
without a commit (`git init`, whatever the provider). It holds the accessories and a FAKE console `./pp`,
which writes what it receives -- its arguments, its standard input -- as one JSON line and answers
the held line of a value (`messages.held`), or to a print call (`-print <DOCUMENT> -`) the line pp answers a print taken. The harness is launched by its adapter (`adapters.launch`), which also reads its
output: its events as they come (`adapters.reader`), then its session, its cost and its error
(`adapters.answer`). The directory is removed afterwards.

THE FIXED PART. Under `place: system` it goes to the system prompt where the adapter declares that it
gives one at the call (`SYSTEM_PROMPT`), and to the head of the first prompt otherwise. Under
`place: head` it goes to the head of the first prompt everywhere. A resumed launch never says it again.

WHAT STOPS A LAUNCH, A REPETITION, THE PLAY. A launch that lasts more than `--timeout` seconds is killed
with its process group, and ends on the error `timeout`. A repetition that fails -- a launch in error, a
face of the adapter that raises, a throwaway directory that cannot be laid -- keeps its row, with its
error and the cause the harness said; the other repetitions play. An interruption of the play (SIGINT,
SIGTERM) stops its queue: no repetition and no launch starts after it, the launches in flight are killed
with their groups and end on the error `interrupted`, and the table of what played is written.

WHAT IS KEPT. Under `<out>/<date>/<variant>/<k>/`: `launch.json`, the prompt as it left (`prompt.txt`),
`stdout.txt` and `stderr.txt` of each launch (`.2`, `.3`… before the extension from the second launch on),
`events.jsonl` (the adapter's events in order, each with its launch), `received.jsonl` (what the fake
console received), and `transcript.jsonl` when the adapter knows where the harness keeps the session
(`transcript(session)`, which also gives the phase of each message). Under `<out>/<date>/`: `turn.json`
and `TURN.md`, one row per repetition and the foot of each variant, written again at every repetition
that ends. The table counts facts of form -- how many messages, whether the last one is a JSON value
alone -- and judges none of them: what a count means is read by the measure that plays the set. `<date>`
is the second the play starts, with a rank (`-2`, `-3`…) when another play of the same second holds it:
one folder per play.

WHAT THE VERB RENDERS. 0 when no repetition ended on an error; 1 when at least one did; 130 when the play
was interrupted; 2 on a refusal, said by its code before any launch.

The player names no provider: the launch, the reading, the place of the fixed part and the transcript
come from the adapter.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                       # the repository: tools/campaign/ -> root
ADAPTERS = ROOT / "adapters"                    # the adapters of this checkout: a turn plays on no instance
if str(ROOT / "engine") not in sys.path:
    sys.path.insert(0, str(ROOT / "engine"))
from conductor.core import messages    # noqa: E402 -- the product's own faces
from conductor.core.errors import Refusal    # noqa: E402
from conductor.packaging import adapters   # noqa: E402
from conductor import VERSION   # noqa: E402 -- the engine whose adapters play, written in the table

MANIFEST = "turn.yaml"
SET_KEYS = ("name", "description", "files", "variants")
VARIANT_KEYS = ("description", "fixed", "prompts", "place", "model")
SYSTEM, HEAD = "system", "head"
PLACES = (SYSTEM, HEAD)                         # where a variant asks its fixed part to go
FLAGS = ("--set", "--variant", "--provider", "--model", "--effort", "--permissions", "--budget", "--repeat",
         "--jobs", "--timeout", "--out")        # every flag takes one value
BUDGET, REPEAT, JOBS = "2", "1", "1"            # USD a launch may spend where the adapter spells a budget
TIMEOUT = "600"                                 # seconds a launch may last before it is killed
TABLE, TABLE_TEXT = "turn.json", "TURN.md"      # the table of a play, under its folder beside the variants
CAUSE = 300                                     # the characters kept of the cause of an error
LATE = "timeout"                                # the error of a launch killed at its bound
INTERRUPTED = "interrupted"                     # the error of a launch killed, or never started, at an interruption
STOPPED_CODE = 130                              # what the verb renders once interrupted: neither a play's nor a refusal's
STOPPED = threading.Event()                     # set at SIGINT or SIGTERM: no new repetition, no new launch
FLYING: set = set()                             # the processes of the launches in flight
INTENT = "PP_MODEL_INTENT"                      # the intention of the modelled LLM, as its principal's message
CONSOLE, HOME = "pp", ".pp"                     # the fake console and the directory it keeps its record in
GIT, BRANCH = "git", "main"                     # the throwaway directory is a repository, on that branch, without a commit
RECEIVED = "received.jsonl"
BLANK = "system.md"                             # the empty system prompt, under HOME: a call that carries no fixed part
JUDGED = messages.held("value")                 # what the fake console answers to every call but a print
PRINTED = messages.printed("more", messages.next_print("<DOCUMENT>"))   # what it answers to a print call, as pp does
DOTS, JSON, TEXT, NONE = "dots", "json", "text", "none"    # the nature of a message, by its form
NATURES = (JSON, DOTS, TEXT, NONE)
SUMMED = ("launches", "messages", "json_messages", "received", "received_json", "thinking", "thinking_chars",
          "thinking_tokens")                    # the counts of a row the foot sums
USAGE = """campaign.py turn --set <dir> --provider <name> [--variant <name>]... [--model <m>] [--effort <e>]
                 [--permissions <regime>] [--budget <usd>] [--repeat <n>] [--jobs <n>] [--timeout <seconds>]
                 [--out <dir>]
    -> plays the variants of the set's `turn.yaml` -- all of them, or those `--variant` names -- `--repeat`
       times each (1), `--jobs` repetitions at once (1), on the harness of `--provider`. A repetition plays
       in a throwaway directory, a git repository without a commit, where `./pp` is a fake that records
       what it receives. A launch that lasts more than `--timeout` seconds (600) is killed.
       `--model`, `--effort` and `--permissions` go to the harness as its adapter writes them; one the
       adapter cannot write refuses before any launch. `--budget` (USD a launch may spend, 2) is given
       where the adapter can write a budget, and left out elsewhere.
       Kept under `<out>/<date>/<variant>/<k>/`: the pieces of each repetition. Written under
       `<out>/<date>/`, again at every repetition that ends: `turn.json` and `TURN.md`. `<out>` is
       `<set>/../out/turn` unless `--out` names it.
       Renders 0 when no repetition ended on an error; 1 when at least one did (its row keeps the error
       and its cause, the others play); 130 when the play was interrupted (SIGINT, SIGTERM: the launches
       in flight are killed, the table says what played); 2 on a refusal, before any launch: a flag, a
       manifest, a provider or a variant the verb cannot play."""
OWED = {"--set": "name the directory that holds `turn.yaml` after `--set`",      # what repairs a flag left out
        "--provider": "name the adapter of the harness to play on after `--provider` (`model`, or a real one)"}
FAKE = '''import json
import select
import sys
from pathlib import Path

args = sys.argv[1:]
piped = ""
if "-" in args or (not sys.stdin.isatty() and select.select([sys.stdin], [], [], 0.2)[0]):
    piped = sys.stdin.read()
with (Path(__file__).resolve().parent / "{received}").open("a", encoding="utf-8") as kept:
    kept.write(json.dumps({{"argv": args, "stdin": piped}}, ensure_ascii=False) + "\\n")
print("{printed}" if args[1:2] == ["-print"] else "{judged}")
'''


class Refused(Exception):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code, self.detail = code, detail


# --- the set and its manifest ----------------------------------------------------------------------

def _inside(set_dir: Path, rel, what: str) -> str:
    """-> `rel` as a file standing under the set; `manifest-invalid` names what it was written for."""
    if not isinstance(rel, str) or not rel.strip():
        raise Refused("manifest-invalid",
            f"{what}: {rel!r} is no path -- name a file of the set, by its path from the set's directory")
    if Path(rel).is_absolute() or ".." in Path(rel).parts or not (set_dir / rel).is_file():
        raise Refused("manifest-invalid",
            f"{what}: `{rel}` is no file under {set_dir} -- name a file that stands in the set, by a path "
            "from its directory, without `..`")
    return rel


def _fixed(set_dir: Path, rel, what: str) -> tuple[str, str, int]:
    """-> (`rel`, the sha256 of its bytes, its size in characters) for the file of a fixed part: a path
    relative to the set's directory -- `..` allowed: several sets play one text kept beside them -- or an
    absolute one; the text is read, never laid in the throwaway directory. `manifest-invalid` names a path
    that is no file, or a file that is no UTF-8 text."""
    if not isinstance(rel, str) or not rel.strip():
        raise Refused("manifest-invalid",
            f"{what}: {rel!r} is no path -- name the file of the fixed part, by a path from the set's "
            "directory (`..` allowed) or an absolute one")
    if not (set_dir / rel).is_file():
        raise Refused("manifest-invalid",
            f"{what}: `{rel}`, read from {set_dir}, is no file -- correct the path, or leave `fixed:` out "
            "to play no fixed part")
    read = (set_dir / rel).read_bytes()
    try:
        return rel, hashlib.sha256(read).hexdigest(), len(read.decode("utf-8"))
    except UnicodeDecodeError as wrong:
        raise Refused("manifest-invalid",
            f"{what}: `{rel}` is no UTF-8 text ({wrong}) -- save the file as UTF-8") from None


def manifest_of(set_dir: Path) -> dict:
    """-> the manifest of the set at `set_dir`, judged: the accessories (the name in the throwaway directory
    -> the path in the set) and the variants, each with its prompts, its fixed part and its fingerprint, the
    place asked for it and the intention of the modelled LLM. A key nobody knows, a file the set lacks, a
    place that is none, a variant or an accessory whose name is no name of a folder or of a file refuse
    `manifest-invalid`, naming it."""
    path = set_dir / MANIFEST
    if not set_dir.is_dir():
        raise Refused("set-missing",
            f"`{set_dir}` is no directory -- give `--set` the directory that holds `{MANIFEST}`")
    if not path.is_file():
        raise Refused("manifest-missing",
            f"{set_dir} holds no `{MANIFEST}` -- write the manifest there, or give `--set` the directory "
            "that holds one")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as wrong:
        raise Refused("manifest-invalid",
            f"{path} cannot be read as YAML -- correct the place this names: {wrong}") from None
    if not isinstance(loaded, dict) or not isinstance(loaded.get("variants"), dict) or not loaded["variants"]:
        raise Refused("manifest-invalid",
            f"{path}: `variants:` is missing, empty or no mapping -- write at least one variant under it: "
            f"its name, then its keys ({', '.join(VARIANT_KEYS)})")
    unknown = sorted(set(map(str, loaded)) - set(SET_KEYS))
    if unknown:
        raise Refused("manifest-invalid",
            f"{path}: unknown key(s) {', '.join(unknown)} -- remove them, or correct their spelling: the "
            f"keys of a set are {', '.join(SET_KEYS)}")
    given = loaded.get("files") or {}
    if isinstance(given, list) and all(isinstance(one, str) for one in given):
        given = {one: one for one in given}
    if not isinstance(given, dict):
        raise Refused("manifest-invalid",
            f"{path}: `files:` is neither a mapping nor a list of paths -- write one line "
            "`<name in the throwaway directory>: <path in the set>` per accessory, or a list of paths of "
            "the set")
    files = {}
    for name, rel in given.items():
        name = str(name)
        target = Path(name)
        if (not target.parts or name.endswith(("/", "\\")) or target.is_absolute() or ".." in target.parts
                or target.parts[0] in (CONSOLE, HOME, f".{GIT}")):
            raise Refused("manifest-invalid",
                f"file `{name}`: an accessory cannot be laid under that name -- give it the relative name of "
                f"a file, without `..` and without a `/` at its end, other than `{CONSOLE}` and outside "
                f"`{HOME}/` and `.{GIT}/`: the player writes those itself")
        files[name] = _inside(set_dir, rel, f"file `{name}`")
    variants = {}
    for name, spec in loaded["variants"].items():
        name = str(name)
        if (not isinstance(spec, dict) or not name.strip() or "/" in name or "\\" in name or name.startswith(".")
                or name.lower() in (TABLE.lower(), TABLE_TEXT.lower())):
            raise Refused("manifest-invalid",
                f"variant `{name}`: its pieces are kept in a folder of that name beside `{TABLE}` and "
                f"`{TABLE_TEXT}` -- give it a plain name (not empty, no `/`, no `\\`, no `.` at its start, "
                f"neither of these two file names) and write its keys under it ({', '.join(VARIANT_KEYS)})")
        unknown = sorted(set(map(str, spec)) - set(VARIANT_KEYS))
        if unknown:
            raise Refused("manifest-invalid",
                f"variant `{name}`: unknown key(s) {', '.join(unknown)} -- remove them, or correct their "
                f"spelling: the keys of a variant are {', '.join(VARIANT_KEYS)}")
        prompts = spec.get("prompts")
        prompts = [prompts] if isinstance(prompts, str) else prompts
        if not isinstance(prompts, list) or not prompts:
            raise Refused("manifest-invalid",
                f"variant `{name}`: `prompts:` is missing or empty -- name one file of the set, or a list of "
                "them: each file is one launch")
        place = spec.get("place", SYSTEM)
        if place not in PLACES:
            raise Refused("manifest-invalid",
                f"variant `{name}`: `place: {place}` is no place for a fixed part -- write one of "
                f"{', '.join(PLACES)}, or leave `place:` out for `{SYSTEM}`")
        intent = spec.get("model") or []
        if not isinstance(intent, list) or not all(isinstance(one, dict) and len(one) == 1 for one in intent):
            raise Refused("manifest-invalid",
                f"variant `{name}`: `model:` is no list of one-key acts -- write one line `- <act>: <value>` "
                "per act of the modelled LLM, or leave `model:` out")
        fixed, sha256, chars = (_fixed(set_dir, spec["fixed"], f"variant `{name}`, `fixed:`")
                                if spec.get("fixed") is not None else (None, None, None))
        variants[name] = {"prompts": [_inside(set_dir, one, f"variant `{name}`, `prompts:`") for one in prompts],
                          "fixed": fixed, "fixed_sha256": sha256, "fixed_chars": chars, "place": place, "model": intent}
    return {"name": str(loaded.get("name") or set_dir.name), "set": str(set_dir), "files": files, "variants": variants}


# --- the call ---------------------------------------------------------------------------------------

def asked_of(argv: list[str]) -> dict:
    """-> what the call asks, every flag judged before anything is read or launched: `flag-unknown` names a
    word that is no flag, `flag-invalid` a flag without its value or a count that is none, `flag-missing` the
    set or the provider left out."""
    found: dict[str, list[str]] = {}
    at = 0
    while at < len(argv):
        flag = argv[at]
        if flag not in FLAGS:
            raise Refused("flag-unknown",
                f"`{flag}` is no flag of `turn` -- write one of {', '.join(FLAGS)}, each followed by its "
                "value")
        if at + 1 >= len(argv):
            raise Refused("flag-invalid", f"`{flag}` comes without its value -- write the value after it")
        found.setdefault(flag, []).append(argv[at + 1])
        at += 2
    for flag in ("--set", "--provider"):
        if flag not in found:
            raise Refused("flag-missing", f"`{flag}` is left out -- {OWED[flag]}")

    def last(flag: str, default: str | None = None) -> str | None:
        return found[flag][-1] if flag in found else default

    counts = {}
    for flag, default in (("--repeat", REPEAT), ("--jobs", JOBS), ("--timeout", TIMEOUT)):
        value = str(last(flag, default))
        if not value.isdigit() or int(value) < 1:
            raise Refused("flag-invalid", f"`{flag} {value}` is no count -- give `{flag}` a whole number, 1 or more")
        counts[flag] = int(value)
    return {"set": Path(str(last("--set"))).resolve(), "variants": found.get("--variant", []),
            "provider": str(last("--provider")), "model": last("--model"), "effort": last("--effort"),
            "permissions": last("--permissions"), "budget": str(last("--budget", BUDGET)),
            "repeat": counts["--repeat"], "jobs": counts["--jobs"], "timeout": counts["--timeout"],
            "out": last("--out")}


def adapter_of(provider: str):
    """-> the provider's adapter of this checkout, loaded by the engine's face; `provider-unknown` as it
    says it."""
    try:
        return adapters.load(provider, root=ADAPTERS)
    except Refusal as refusal:
        raise Refused(refusal.code, str(refusal)) from None


def policy_of(asked: dict, module) -> dict | None:
    """-> the policy of every launch, judged at the engine's face: the model, the effort and the regime as
    asked; the budget where the adapter spells one, left out where it does not."""
    policy = {key: asked[key] for key in ("model", "effort", "permissions") if asked.get(key)}
    if "max_budget_usd" in getattr(module, "SPELLS", ()):
        policy["max_budget_usd"] = asked["budget"]
    try:
        return adapters.judged(policy) or None
    except Refusal as refusal:
        raise Refused(refusal.code, str(refusal)) from None


def harness_of(module, provider: str) -> dict:
    """-> the harness a launch plays: the binary its adapter declares and the version that binary says of
    itself; `provider-missing` when a binary is due and absent. An adapter that needs none says neither."""
    binary = getattr(module, "BINARY", provider)
    if binary is None:
        return {"binary": None, "version": None}
    if shutil.which(binary) is None:
        raise Refused("provider-missing",
            f"`{provider}` needs `{binary}`, which is not on this machine -- install it, or put its "
            "directory on the PATH")
    try:
        said = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        said = ""
    return {"binary": binary, "version": said.splitlines()[0] if said else None}


# --- one launch --------------------------------------------------------------------------------------

def went_of(module, fixed, place: str) -> str | None:
    """-> where the fixed part goes: `system` when the variant asks it and the adapter gives a system
    prompt at the call, `head` otherwise; None without a fixed part."""
    if fixed is None:
        return None
    return SYSTEM if place == SYSTEM and getattr(module, "SYSTEM_PROMPT", False) else HEAD


def composition(provider: str, where: Path, fixed: Path | None, place: str, prompt: str,
                policy: dict | None = None, session: str | None = None) -> tuple[list[str], dict, str, str | None]:
    """-> `(argv, env, stdin, went)` of ONE launch in the directory `where`, composed by the adapter and
    never run. An adapter that gives a system prompt at the call receives the fixed part as its marble when
    it goes there, an empty one otherwise -- the call carries the fixed part or nothing, never a text of
    another instance. A fixed part that goes to the head leads the prompt of the launch that opens the
    session; a resumed launch (`session`) says its prompt alone."""
    module = adapter_of(provider)
    went = went_of(module, fixed, place)
    marble = None
    if getattr(module, "SYSTEM_PROMPT", False):
        marble = Path(fixed) if went == SYSTEM else where / HOME / BLANK
        if went != SYSTEM and not marble.is_file():
            marble.parent.mkdir(parents=True, exist_ok=True)
            marble.write_text("", encoding="utf-8")
    stdin = prompt
    if went == HEAD and session is None:
        stdin = Path(fixed).read_text(encoding="utf-8").rstrip("\n") + "\n\n" + prompt
    try:
        argv, env, stdin = adapters.launch(provider, where, where / HOME, stdin, marble=marble, root=ADAPTERS,
                                           wiring=where, policy=policy, session=session)
    except Refusal as refusal:
        raise Refused(refusal.code, str(refusal)) from None
    return argv, env, stdin, went


def laid(manifest: dict, where: Path) -> None:
    """The throwaway directory of a repetition: a git repository -- as an agent's workspace is one, and a
    harness may refuse to work outside one --, initialized without any template on the branch `BRANCH`, no
    commit made; the set's accessories; and the fake console -- `./pp` hands its arguments and its standard
    input to the record under `.pp/` and answers the held line of a value -- a print call, the line pp answers it."""
    made = subprocess.run([GIT, "-c", f"init.defaultBranch={BRANCH}", "init", "-q", "--template=", str(where)],
                          capture_output=True, text=True,
                          env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")})
    if made.returncode != 0:
        raise Refused("git-failed",
            f"`{GIT} init` failed at {where} -- check that `{GIT}` can create a repository in an empty "
            f"directory; it said: {made.stderr.strip()[-300:]}")
    set_dir = Path(manifest["set"])
    for name, rel in manifest["files"].items():
        target = where / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(set_dir / rel, target)
    home = where / HOME
    home.mkdir(exist_ok=True)
    (home / "console.py").write_text(FAKE.format(received=RECEIVED, judged=JUDGED, printed=PRINTED), encoding="utf-8")
    console = where / CONSOLE
    console.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$(dirname "$0")/{HOME}/console.py" "$@"\n',
                       encoding="utf-8")
    console.chmod(0o755)


def environment_of(intent: list) -> dict:
    """-> the environment of a launch: the caller's shell without what a conducted session of theirs carries
    (`PP_*`), plus the intention of the modelled LLM when the variant says one."""
    kept = {key: value for key, value in os.environ.items() if not key.startswith("PP_")}
    return {**kept, **({INTENT: json.dumps(intent)} if intent else {})}


def keep(folder: Path, name: str, text: str) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(text, encoding="utf-8")


def transcript_of(module, session: str | None, folder: Path) -> list[dict] | None:
    """-> the messages the harness's own transcript of the session keeps, each with its `phase`, the
    transcript copied beside the pieces; None when the adapter has no such face or holds no transcript."""
    face = getattr(module, "transcript", None)
    if face is None or not session:
        return None
    try:
        read = face(session)
    except Exception:                                   # noqa: BLE001 -- a store that does not read keeps no phase
        return None
    if not isinstance(read, dict) or not isinstance(read.get("messages"), list):
        return None
    if isinstance(read.get("path"), str) and Path(read["path"]).is_file():
        shutil.copy(read["path"], folder / "transcript.jsonl")
    return [one for one in read["messages"] if isinstance(one, dict)]


def killed(process) -> None:
    """Kills a launch with its whole group; a process already gone is left alone."""
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (AttributeError, OSError):
        try:
            process.kill()
        except OSError:
            pass


def interrupted(_signum=None, _frame=None) -> None:
    """The play interrupted: from now on no repetition and no launch starts, and the launches in flight are
    killed with their groups -- each launch is a session of its own, the terminal's signal reaches none."""
    STOPPED.set()
    for process in list(FLYING):
        killed(process)


def played_of(argv: list[str], where: Path, stdin: str, env: dict, timeout: int) -> tuple[int, str, str, bool]:
    """ONE process played to its end, or killed with its whole group once `timeout` seconds have passed, or
    at an interruption of the play. -> (its exit code, its standard output, its standard error, whether its
    bound killed it); both streams read as UTF-8, a byte that is none replaced."""
    process = subprocess.Popen(argv, cwd=where, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=env, start_new_session=True)
    FLYING.add(process)
    late = False
    try:
        if STOPPED.is_set():
            killed(process)
        try:
            out, err = process.communicate(stdin.encode("utf-8"), timeout=timeout)
        except subprocess.TimeoutExpired:
            late = True
            killed(process)
            out, err = process.communicate()
    finally:
        FLYING.discard(process)
    return process.returncode, out.decode("utf-8", errors="replace"), err.decode("utf-8", errors="replace"), late


def said(text: str) -> str | None:
    """-> the end of a text on one line, `CAUSE` characters at most: what a harness said of its own fault;
    None when it said nothing."""
    return " ".join(str(text).split())[-CAUSE:] or None


def repetition(manifest: dict, asked: dict, name: str, k: int, folder: Path) -> dict:
    """ONE repetition of a variant: its prompts played one after the other in a fresh throwaway directory,
    each a launch, the next resuming the session the one before answered; the pieces kept under `folder`.
    A launch that names an error, that is killed at its bound or at an interruption of the play, whose
    reading raises or that answers no session to resume ends the repetition there, and so does anything the
    repetition itself raises: the error and its cause are kept, nothing rises. -> its `launch.json`."""
    variant, set_dir, provider = manifest["variants"][name], Path(manifest["set"]), asked["provider"]
    module = adapter_of(provider)
    fixed = (set_dir / variant["fixed"]).resolve() if variant["fixed"] else None
    kept = {"variant": name, "repetition": k, "provider": provider, "harness": asked["harness"],
            "model": asked.get("model"), "effort": asked.get("effort"), "permissions": asked.get("permissions"),
            "timeout": asked["timeout"], "prompts": variant["prompts"], "fixed": variant["fixed"],
            "fixed_sha256": variant["fixed_sha256"], "fixed_chars": variant["fixed_chars"],
            "place": went_of(module, fixed, variant["place"]), "session": None, "seconds": 0.0, "cost_usd": None,
            "error": None, "cause": None, "workdir": None, "launches": [], "transcript": None}
    launches, events, spoken, session, where = kept["launches"], [], None, None, None
    try:
        folder.mkdir(parents=True, exist_ok=True)
        where = Path(tempfile.mkdtemp(prefix="pp-turn-"))
        kept["workdir"], meta = str(where), where / HOME
        laid(manifest, where)
        for n, rel in enumerate(variant["prompts"], 1):
            if STOPPED.is_set():
                kept.update(error=INTERRUPTED, cause="the play stopped before this launch")
                break
            mark = "" if n == 1 else f".{n}"
            argv, env, stdin, _went = composition(provider, where, fixed, variant["place"],
                                                  (set_dir / rel).read_text(encoding="utf-8"), asked["policy"], session)
            keep(folder, f"prompt{mark}.txt", stdin)
            started = time.monotonic()
            rc, stdout, stderr, late = played_of(argv, where, stdin, {**environment_of(variant["model"]), **env},
                                                 asked["timeout"])
            launch = {"prompt": rel, "rc": rc, "session": None, "resumed": session is not None,
                      "seconds": round(time.monotonic() - started, 2), "cost_usd": None, "error": None, "cause": None}
            launches.append(launch)
            keep(folder, f"stdout{mark}.txt", stdout)
            keep(folder, f"stderr{mark}.txt", stderr)
            try:
                reader = adapters.reader(provider, meta, root=ADAPTERS)
                heard = []
                for line in stdout.splitlines():
                    try:
                        heard += reader.heard(line)
                    except Refusal:
                        continue
                heard += reader.end()
                events += [{"launch": n, **one} for one in heard]
                try:
                    read = adapters.answer(provider, meta, stdout, stderr, root=ADAPTERS)
                except Refusal as refusal:
                    read = {"cost_usd": None, "error": refusal.code, "session": None}
                    launch["cause"] = said(str(refusal))
                launch.update(session=read.get("session"), cost_usd=read.get("cost_usd"),
                              error=read.get("error") or (f"exit {rc}" if rc else None))
            except Exception as raised:                 # noqa: BLE001 -- a face of the adapter that raises: the launch's error
                launch.update(error=type(raised).__name__, cause=said(str(raised)))
            if late:
                launch.update(error=LATE, cause=f"killed after {asked['timeout']} s")
            elif STOPPED.is_set() and rc is not None and rc < 0:
                launch.update(error=INTERRUPTED, cause="killed when the play stopped")
            if launch["error"] and not launch["cause"]:
                launch["cause"] = said(stderr)
            session = launch["session"] or session
            if launch["error"] or session is None:
                kept["error"] = launch["error"] or "session-missing"
                kept["cause"] = launch["cause"] or (None if launch["session"]
                                                    else "the launch answered no session to resume")
                break
        spoken = transcript_of(module, session, folder)
    except Refused as refused:
        kept.update(error=refused.code, cause=said(refused.detail))
    except Exception as raised:                         # noqa: BLE001 -- the repetition says its own fault, the play goes on
        kept.update(error=type(raised).__name__, cause=said(str(raised)))
    finally:
        record = where / HOME / RECEIVED if where is not None else None
        try:
            keep(folder, RECEIVED, record.read_text(encoding="utf-8") if record is not None and record.is_file() else "")
            keep(folder, "events.jsonl", "".join(json.dumps(one, ensure_ascii=False) + "\n" for one in events))
        finally:
            if where is not None:
                shutil.rmtree(where, ignore_errors=True)
    costs = [one["cost_usd"] for one in launches if one["cost_usd"] is not None]
    kept.update(session=session, seconds=round(sum(one["seconds"] for one in launches), 2),
                cost_usd=None if not costs else costs[-1] if getattr(module, "COST", None) == "session"
                else round(sum(costs), 6),
                transcript="transcript.jsonl" if (folder / "transcript.jsonl").is_file() else None)
    keep(folder, "launch.json", json.dumps(kept, indent=2, ensure_ascii=False) + "\n")
    return {**kept, "events": events, "spoken": spoken}


# --- the table ---------------------------------------------------------------------------------------

def whole_json(text: str) -> bool:
    """-> whether the text is ONE JSON value and nothing else -- an object or an array: what an act, a
    proof or a field is; a number or a word alone is a text."""
    try:
        return isinstance(json.loads(text), (dict, list))
    except ValueError:
        return False


def nature(text: str) -> str:
    """-> the nature of a message by its form alone: `json` (one JSON value, alone), `dots` (the three dots,
    alone), `none` (nothing), `text` (anything else -- a value in a fence or beside a sentence included)."""
    said = text.strip()
    if not said:
        return NONE
    if said == "...":
        return DOTS
    return JSON if whole_json(said) else TEXT


def received_of(folder: Path) -> list[dict]:
    path, found = folder / RECEIVED, []
    for line in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict):
            found.append(one)
    return found


def row_of(played: dict, folder: Path, out: Path) -> dict:
    """-> the row of ONE repetition, read from its kept pieces: the sequence of its events launch by launch
    (`thinking`, `words`, `tool`, and `pp` for a call of the console -- read at what the fake answered in the
    call's result, once per answer, never at the shape of the shell line), its messages with their nature
    and their phase, the nature of the last message of the LAST launch the variant asks (`none` when that
    launch said nothing, or never played), what the fake console received, the thoughts the harness shows,
    the error the repetition ended on and its cause."""
    events, launches = played["events"], played["launches"]
    results = {(one["launch"], one.get("id")): str(one.get("content") or "") for one in events
               if one["kind"] == "tool-result"}
    sequence = []
    for n in range(1, len(launches) + 1):
        told = []
        for one in events:
            if one["launch"] != n or one["kind"] not in ("thinking", "words", "tool"):
                continue
            answered = sum(1 for line in results.get((n, one.get("id")), "").splitlines() if line.strip() in (JUDGED, PRINTED)) \
                if one["kind"] == "tool" else 0
            told += [CONSOLE] * answered if answered else [one["kind"]]
        sequence.append(told)
    spoken = list(played["spoken"] or [])
    texts = []
    for one in events:
        if one["kind"] != "words":
            continue
        at = next((i for i, kept in enumerate(spoken) if str(kept.get("text", "")).strip() == one["text"].strip()), None)
        phase = spoken[at].get("phase") if at is not None else None
        del spoken[:at + 1 if at is not None else 0]
        texts.append({"launch": one["launch"], "nature": nature(one["text"]), "phase": phase, "text": one["text"]})
    final = [one for one in texts if one["launch"] == len(played.get("prompts") or launches)]
    thoughts = [one for one in events if one["kind"] == "thinking"]
    received = received_of(folder)
    return {"repetition": played["repetition"], "folder": str(folder.relative_to(out)), "launches": len(launches),
            "error": played["error"], "cause": played.get("cause"), "seconds": played["seconds"],
            "cost_usd": played["cost_usd"], "sequence": sequence, "messages": len(texts),
            "last": final[-1]["nature"] if final else NONE,
            "json_messages": sum(1 for one in texts if one["nature"] == JSON),
            "received": len(received),
            "received_json": sum(1 for one in received if whole_json(str(one.get("stdin", "")))),
            "thinking": len(thoughts), "thinking_chars": sum(len(str(one.get("text") or "")) for one in thoughts),
            "thinking_tokens": sum(int(one.get("tokens") or 0) for one in thoughts),
            "phases": [one["phase"] for one in texts] if played["spoken"] is not None else None,
            "last_phase": final[-1]["phase"] if final and played["spoken"] is not None else None,
            "transcript": played["transcript"], "texts": texts}


def foot_of(rows: list[dict]) -> dict:
    """-> the foot of a variant: the counts of its rows summed, the repetitions by the nature of the last
    message of their last launch and by its phase where the harness gives one, the repetitions that ended on
    an error."""
    foot = {"repetitions": len(rows), "errors": sum(1 for row in rows if row["error"])}
    foot.update({key: sum(row[key] for row in rows) for key in SUMMED})
    foot["last"] = {one: sum(1 for row in rows if row["last"] == one) for one in NATURES}
    phases = [row["last_phase"] for row in rows if row["last_phase"] is not None]
    foot["last_phase"] = {str(one): phases.count(one) for one in dict.fromkeys(phases)} if phases else None
    foot["seconds"] = round(sum(row["seconds"] for row in rows), 2)
    costs = [row["cost_usd"] for row in rows if row["cost_usd"] is not None]
    foot["cost_usd"] = round(sum(costs), 6) if costs else None
    return foot


def shown(value) -> str:
    if value is None:
        return "-"
    return f"{value:g}" if isinstance(value, float) else str(value)


def table_text(table: dict) -> str:
    """-> `TURN.md`: the play (the harness and its version, the model, the effort, the regime, the
    repetitions), then per variant its rows and its foot."""
    harness = table["harness"]
    lines = [f"# TURN -- `{table['name']}` on `{table['provider']}`, {table['date']}", "",
             f"- harness: {shown(harness['binary'])} {shown(harness['version'])} · model {shown(table['model'])} · "
             f"effort {shown(table['effort'])} · permissions {shown(table['permissions'])}",
             f"- {table['repeat']} repetition(s) per variant, {table['launches']} launch(es), {table['jobs']} at once, "
             f"{table['timeout']} s each at most · bound {shown(table['bound_usd'])} USD · engine {table['engine']}",
             f"- set: `{table['set']}`"]
    lines += ["- INTERRUPTED: the rows below are the repetitions that had started when the play stopped", ""] \
        if table["interrupted"] else [""]
    for name, variant in table["variants"].items():
        foot = variant["foot"]
        lines += [f"## `{name}`", "",
                  f"prompts {', '.join(f'`{one}`' for one in variant['prompts'])} · fixed part "
                  + (f"`{variant['fixed']}` (sha256 {variant['fixed_sha256']}, {variant['fixed_chars']} characters) "
                     f"at the {variant['place']} (asked: {variant['asked']})" if variant["fixed"] else "none"), "",
                  "| k | launches | sequence | messages | last | json | received | received json | thinking | phases "
                  "| seconds | USD | error | pieces |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for row in variant["rows"]:
            sequence = " / ".join(" ".join(one) or "-" for one in row["sequence"]) or "-"
            thinking = f"{row['thinking']} ({row['thinking_chars']} chars, {row['thinking_tokens']} tokens)"
            phases = " ".join(shown(one) for one in row["phases"]) if row["phases"] else "-"
            error = shown(row["error"]) + (f" -- {row['cause']}" if row["error"] and row["cause"] else "")
            lines.append(f"| {row['repetition']} | {row['launches']} | {sequence} | {row['messages']} | {row['last']} | "
                         f"{row['json_messages']} | {row['received']} | {row['received_json']} | {thinking} | {phases} | "
                         f"{shown(row['seconds'])} | {shown(row['cost_usd'])} | "
                         f"{error.replace('|', '/')} | `{row['folder']}/` |")
        last = ", ".join(f"{one} {count}" for one, count in foot["last"].items())
        lines += ["",
                  f"Foot: {foot['repetitions']} repetition(s), {foot['launches']} launch(es), {foot['errors']} error(s) · "
                  f"last message: {last}"
                  + (" · its phase: " + ", ".join(f"{one} {count}" for one, count in foot["last_phase"].items())
                     if foot["last_phase"] else "")
                  + f" · {foot['messages']} message(s), {foot['json_messages']} JSON · {foot['received']} call(s) "
                  f"received, {foot['received_json']} with a JSON input · {foot['thinking']} thought(s) · "
                  f"{shown(foot['seconds'])} s · {shown(foot['cost_usd'])} USD", ""]
    return "\n".join(lines)


# --- the verb ----------------------------------------------------------------------------------------

def folder_of(out: Path, when: str) -> Path:
    """-> the folder of ONE play under `out`, made here: `<when>`, or `<when>-2`, `<when>-3`… when another
    play of the same second holds it -- the making is the claim, two plays never write one folder."""
    out.mkdir(parents=True, exist_ok=True)
    rank = 1
    while True:
        folder = out / (when if rank == 1 else f"{when}-{rank}")
        try:
            folder.mkdir()
            return folder
        except FileExistsError:
            rank += 1


def keep_whole(folder: Path, name: str, text: str) -> None:
    """Writes a piece that is rewritten while the play goes on: beside itself, then in its place -- a play
    killed between two repetitions leaves the piece whole."""
    folder.mkdir(parents=True, exist_ok=True)
    beside = folder / f".{name}.writing"
    beside.write_text(text, encoding="utf-8")
    os.replace(beside, folder / name)


def turn(argv: list[str]) -> int:
    asked = asked_of(argv)
    manifest = manifest_of(asked["set"])
    unknown = [one for one in asked["variants"] if one not in manifest["variants"]]
    if unknown:
        raise Refused("variant-unknown",
            f"{', '.join(unknown)}: no variant of the set `{manifest['name']}` has that name -- give "
            f"`--variant` one of {', '.join(manifest['variants'])}")
    names = list(dict.fromkeys(asked["variants"])) or list(manifest["variants"])
    provider = asked["provider"]
    module = adapter_of(provider)
    if shutil.which(GIT) is None:
        raise Refused("git-missing",
            f"`{GIT}` is not on this machine, and every throwaway directory is made a git repository -- "
            "install it, or put its directory on the PATH")
    asked["harness"] = harness_of(module, provider)
    asked["policy"] = policy_of(asked, module)
    set_dir = Path(manifest["set"])
    with tempfile.TemporaryDirectory(prefix="pp-turn-") as nowhere:    # a launch composed once, nothing run: a
        composition(provider, Path(nowhere), None, SYSTEM, "", asked["policy"])   # policy the adapter cannot spell
                                                                        # refuses before the first launch
    launches = sum(len(manifest["variants"][name]["prompts"]) for name in names) * asked["repeat"]
    spelled = bool(asked["policy"]) and "max_budget_usd" in asked["policy"]
    bound = launches * float(asked["budget"]) if spelled else 0.0 if asked["harness"]["binary"] is None else None
    out = folder_of(Path(asked["out"] or set_dir.parent / "out" / "turn").resolve(),
                    _dt.datetime.now().strftime("%Y-%m-%dT%H%M%S"))
    print(f"campaign: bound {launches} launch(es) x {asked['budget']} USD = "
          + (f"{bound:g} USD" if bound is not None else f"no bound (`{provider}` spells no budget)")
          + f" -- provider {provider}, harness {shown(asked['harness']['version'])}, model {asked['model'] or 'default'}, "
          f"effort {asked['effort'] or 'default'}, permissions {asked['permissions'] or 'default'}, "
          f"{asked['timeout']} s a launch at most; kept under {out}", flush=True)
    rows: dict[str, dict[int, dict]] = {name: {} for name in names}
    writing = threading.Lock()

    def written() -> dict:
        """The table of what has played so far, written whole: one row per repetition that ended."""
        variants = {}
        for name in names:
            variant = manifest["variants"][name]
            fixed = (set_dir / variant["fixed"]).resolve() if variant["fixed"] else None
            ended = [rows[name][k] for k in sorted(rows[name])]
            variants[name] = {"prompts": variant["prompts"], "fixed": variant["fixed"],
                              "fixed_sha256": variant["fixed_sha256"], "fixed_chars": variant["fixed_chars"],
                              "asked": variant["place"], "place": went_of(module, fixed, variant["place"]),
                              "rows": ended, "foot": foot_of(ended)}
        table = {"date": out.name, "name": manifest["name"], "set": manifest["set"], "engine": VERSION,
                 "provider": provider, "harness": asked["harness"], "model": asked["model"], "effort": asked["effort"],
                 "permissions": asked["permissions"], "repeat": asked["repeat"], "jobs": asked["jobs"],
                 "timeout": asked["timeout"], "launches": launches, "interrupted": STOPPED.is_set(),
                 "budget_usd": float(asked["budget"]) if spelled else None, "bound_usd": bound, "variants": variants}
        keep_whole(out, TABLE, json.dumps(table, indent=2, ensure_ascii=False) + "\n")
        keep_whole(out, TABLE_TEXT, table_text(table))
        return table

    def one(name: str, k: int) -> None:
        if STOPPED.is_set():
            return
        folder = out / name / str(k)
        try:
            row = row_of(repetition(manifest, asked, name, k, folder), folder, out)
        except Exception as raised:                     # noqa: BLE001 -- pieces that could not be kept: the row says so
            row = row_of({"repetition": k, "launches": [], "events": [], "spoken": None, "seconds": 0.0,
                          "cost_usd": None, "transcript": None, "prompts": manifest["variants"][name]["prompts"],
                          "error": type(raised).__name__, "cause": said(str(raised))}, folder, out)
        with writing:
            rows[name][k] = row
            written()
            print(f"campaign: {name}#{k} -- {row['launches']} launch(es), {row['messages']} message(s), "
                  f"last {row['last']}, {row['received']} call(s) received, {shown(row['seconds'])} s"
                  + (f", error {row['error']}" + (f" -- {row['cause']}" if row["cause"] else "") if row["error"] else ""),
                  flush=True)

    STOPPED.clear()
    held = {}
    for signum in (signal.SIGINT, signal.SIGTERM):
        try:
            held[signum] = signal.signal(signum, interrupted)
        except ValueError:                              # a play outside the main thread: its caller holds the signals
            pass
    try:
        with ThreadPoolExecutor(max_workers=asked["jobs"]) as pool:
            for each in [pool.submit(one, name, k) for name in names for k in range(1, asked["repeat"] + 1)]:
                each.result()
        table = written()
    finally:
        for signum, before in held.items():
            signal.signal(signum, before)
    feet = [variant["foot"] for variant in table["variants"].values()]
    errors = sum(foot["errors"] for foot in feet)
    costs = [foot["cost_usd"] for foot in feet if foot["cost_usd"] is not None]
    ended = (f"{sum(foot['repetitions'] for foot in feet)} repetition(s) of {len(names)} variant(s), {errors} error(s), "
             f"cost {shown(round(sum(costs), 6)) if costs else '-'} USD; the table at {out / TABLE_TEXT}")
    if table["interrupted"]:
        print(f"campaign: INTERRUPTED -- {len(names) * asked['repeat']} repetition(s) were asked: {ended}")
        return STOPPED_CODE
    print(f"campaign: done -- {ended}")
    return 1 if errors else 0


def main(argv: list[str]) -> int:
    """The verb as the launcher distributes it: `--help` says the usage and plays nothing; a refusal is
    said by its code, exit 2, nothing played."""
    if "--help" in argv or "-h" in argv:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        return turn(argv)
    except Refused as refused:
        print(f"campaign: REFUSED -- {refused.code} -- {refused.detail}\n  nothing played.", file=sys.stderr)
        return 2
