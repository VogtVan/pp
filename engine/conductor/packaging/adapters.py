"""packaging.adapters -- the harness ABSTRACTION pp adapts per provider.

An adapter is `adapters/<host>/wire.py` at the PRODUCT checkout -- never in an
instance: a vendored engine reaches it through the `source:` its manifest
declares. Four faces per adapter, loaded by path: `wire(workspace, meta)`
writes the interactive surface at install; `launch(workspace, meta, marble, prompt,
wiring, policy, session)` COMPOSES the command line of ONE exchange of a provider's
session -- `(argv, env, stdin)`: the line, the variables, the prompt to write on the
process's standard input -- and never runs it: the engine keeps no clock and holds no
process (CONDUCTION § The principal); the skill that calls it launches, writes stdin, waits
and reads the exit code; `answer(stdout, stderr)` READS what the harness answered, in the
output format the adapter chose, as `{response, cost_usd, denials, error, session}`; `events(line)`,
the one face an adapter MAY lack, reads ONE line of that output as it arrives -- the calls of
tools, their results, the model's thought and words -- in the COMMON SCHEMA the face here holds,
so that a reader shows a launch as it plays without knowing which provider plays it.

An exchange pp launches is the one the editor's extension launches: a SESSION of the
provider, opened (no `session`: the provider keeps it and names it) or resumed (the
identity the provider gave, read back by `answer()`). The engine creates, keeps and
looks up no session: the identity is judged ONCE here (`session-invalid`) and handed
over, and an answer that carries none refuses `session-missing`. At every call of the
model the system prompt and the whole context reach the agent: an adapter whose host
does not reliably record the system prompt in its session hands the marble at EVERY
launch, the resume included; a host that re-reads it by itself hands nothing; a host
with no system-prompt channel carries no receipt, and the standing rules served inline
ride the session's history. The POLICY of an exchange -- the model, a budget, the permission
regime, the model's effort -- is judged ONCE here
(`policy-unknown`, `policy-invalid`) and spelled by each adapter in its host's own
flags, or refused by the adapter that cannot (`policy-unsupported`); the WIRING is
the directory whose harness configuration the adapter hands to the process. The
MATERIAL of an exchange -- `workdir`, the clone a run works on, under the workspace --
is judged ONCE here (`workdir-invalid`) and composed ONCE here, the same for every
provider: the head of the prompt that names it and the variables `PP_WORKDIR` and
`PP_CONSOLE`; an adapter whose `launch` takes no `workdir` refuses `workdir-unsupported`
when a material is handed.

The engine knows no harness by name: a provider is a directory under adapters/,
found or refused (`provider-unknown`); an adapter without the second face refuses
`launch-unsupported`. The marble each host carries is the adapter's own knowledge
(the file its launcher names): a caller that hands none gets the adapter's choice.
"""
from __future__ import annotations

import inspect
import os
from pathlib import Path, PurePosixPath

from ..core.errors import Refusal
from ..state import discovery, instance
from . import contributions

ENGINE = Path(__file__).resolve().parents[2] / "pp.py"   # the engine this module belongs to
POLICY = ("model", "max_budget_usd", "permissions", "effort")   # what a policy may name: the model, a budget in USD, a regime, an effort
PERMISSIONS = ("auto", "strict", "bypass")   # what the harness may do without asking: its own judgment, the written rules, everything
EFFORTS = ("low", "medium", "high", "xhigh", "max")   # how much the model reasons, in pp's words: each adapter maps them to its own
WORKDIR = ("path", "branch", "base")   # what a material may name: where it is under the workspace, its branch, what it was cut from
HEAD = ("[material {path}{branch}{base} · console {console} -- reach the material by git -C and "
        "relative paths, never cd; the target's hooks are not in the clone]")   # the head of a prompt with a material


def product_of(meta: Path | None = None) -> Path:
    """-> the product checkout the adapters live in: the running engine's own when it is
    the source's; the `source:` the instance declares when the engine is a vendored copy
    (its location says so) or an engine addressed to `meta` from outside it -- a vendored tree
    carries no packages and no adapters. `source-missing` names a source gone."""
    from . import install
    member = discovery.instance_member(ENGINE)
    if member is not None:
        meta = member.meta
    elif meta is None or not instance.is_instance(meta):
        return install.product_root(ENGINE)
    source = Path(instance.read(meta).get("source", ""))
    if not source.is_dir():
        raise Refusal("source-missing", f"{meta} points at `{source}` -- not a directory")
    return source


def load(name: str, meta: Path | None = None, root: Path | None = None):
    """-> the adapter module `<root>/<name>/wire.py`, `root` the product's adapters/ when
    omitted -- loaded by path, as the console loads it. No such adapter: `provider-unknown`."""
    root = product_of(meta) / "adapters" if root is None else root
    path = root / name / "wire.py"
    if not path.is_file():
        raise Refusal("provider-unknown", f"`{name}` -- no adapter of that name under {root}")
    return contributions.module_at(path)


def judged(policy: dict | None) -> dict:
    """-> the policy as every adapter reads it: known keys, typed values -- `model` a
    non-empty name, `max_budget_usd` a number above 0, `permissions` one of `PERMISSIONS`,
    `effort` one of `EFFORTS`.
    Judged ONCE, here, before any adapter: an unknown key refuses `policy-unknown`, a value
    that does not parse `policy-invalid`, each naming the key."""
    if policy is None:
        return {}
    if not isinstance(policy, dict):
        raise Refusal("policy-invalid", f"a policy is a mapping of {', '.join(POLICY)} -- got {type(policy).__name__}")
    found: dict = {}
    for key, value in policy.items():
        if key not in POLICY:
            raise Refusal("policy-unknown", f"`{key}` -- a policy names one of: {', '.join(POLICY)}")
        if key == "model":
            if not isinstance(value, str) or not value.strip():
                raise Refusal("policy-invalid", f"`model: {value!r}` -- a non-empty model name")
            found[key] = value.strip()
        elif key == "permissions":
            if value not in PERMISSIONS:
                raise Refusal("policy-invalid", f"`permissions: {value!r}` -- one of: {', '.join(PERMISSIONS)}")
            found[key] = value
        elif key == "effort":
            if value not in EFFORTS:
                raise Refusal("policy-invalid", f"`effort: {value!r}` -- one of: {', '.join(EFFORTS)}")
            found[key] = value
        else:
            try:
                amount = float(value)
            except (TypeError, ValueError):
                raise Refusal("policy-invalid", f"`{key}: {value!r}` -- a number above 0")
            if not amount > 0:
                raise Refusal("policy-invalid", f"`{key}: {value!r}` -- a number above 0")
            found[key] = amount
    return found


def session_of(session) -> str | None:
    """-> the identity of a provider's session as every adapter reads it: None opens a
    new session, a non-blank text resumes that one. Judged ONCE, here, before any
    adapter: anything else refuses `session-invalid`."""
    if session is None:
        return None
    if not isinstance(session, str) or not session.strip():
        raise Refusal("session-invalid", f"`{session!r}` -- a session is the non-blank identity its provider gave")
    return session.strip()


def material(workdir: dict | None) -> dict:
    """-> the material as every adapter reads it: `path`, where it is -- a RELATIVE path
    under the workspace, no `..` --, `branch` and `base` non-empty texts when given. Judged
    ONCE, here, before any adapter: anything else refuses `workdir-invalid`, naming the
    key. Nothing is read on disk: whether the path exists is the caller's business (a dry
    run composes before any clone)."""
    if workdir is None:
        return {}
    if not isinstance(workdir, dict):
        raise Refusal("workdir-invalid", f"a material is a mapping of {', '.join(WORKDIR)} -- got {type(workdir).__name__}")
    found: dict = {}
    for key, value in workdir.items():
        if key not in WORKDIR:
            raise Refusal("workdir-invalid", f"`{key}` -- a material names one of: {', '.join(WORKDIR)}")
        if not isinstance(value, str) or not value.strip():
            raise Refusal("workdir-invalid", f"`{key}: {value!r}` -- a non-empty text")
        found[key] = value.strip()
    if "path" not in found:
        raise Refusal("workdir-invalid", "`path` -- a material names where it is, relative to the workspace")
    parts = PurePosixPath(found["path"].replace("\\", "/"))
    if parts.is_absolute() or Path(found["path"]).is_absolute() or ".." in parts.parts:
        raise Refusal("workdir-invalid", f"`path: {found['path']!r}` -- a relative path under the workspace, no `..`")
    return found


def console_of(workspace: Path) -> Path:
    """-> the console of the instance at `workspace`, by its absolute path: the launcher
    `install.console` writes beside the instance (`pp`, `pp.cmd` on Windows) -- what a
    harness calls once its model has left the workspace by `cd`."""
    return Path(workspace).resolve() / ("pp.cmd" if os.name == "nt" else "pp")


def headed(prompt: str, held: dict, console: Path) -> str:
    """-> the prompt with the material's HEAD before it -- `[material <path> · branch … ·
    from … · console <console> -- …]`, a blank line, the prompt as given -- or the prompt
    alone without a material. The segments a material does not name are absent."""
    if not held:
        return prompt
    line = HEAD.format(path=held["path"],
                       branch=f" · branch {held['branch']}" if "branch" in held else "",
                       base=f" · from {held['base']}" if "base" in held else "",
                       console=console)
    return f"{line}\n\n{prompt}"


def launch(provider: str, workspace: Path, meta: Path, prompt: str,
           marble: Path | None = None, root: Path | None = None,
           wiring: Path | None = None, policy: dict | None = None,
           session: str | None = None, workdir: dict | None = None) -> tuple[list[str], dict[str, str], str]:
    """-> `(argv, env, stdin)`: the command line that plays ONE exchange on the instance
    `meta` under the harness `provider`, the variables to add to its environment, and the
    text to write on its standard input -- the prompt as composed here, the material's
    head before it -- composed by the adapter, never run here. The prompt travels by
    stdin at every provider, never as an argument: an argument is bounded (128 KiB on
    Linux), a prompt is bounded by the model alone. `session` None opens a
    session of the provider, an identity it gave resumes that one (`session_of`).
    `marble` None lets the adapter name the marble its launcher carries; a marble
    handed wins -- the marble of the run's mode, when the caller names it, reaches the
    provider's channel as the adapter spells it. `wiring` is the directory whose harness configuration the adapter
    hands to the process (the home of an agent), None when there is nothing to hand;
    `policy` the model, the budget, the permission regime and the effort, judged here (`judged`) and spelled by the
    adapter or refused by it (`policy-unsupported`). `workdir` is the MATERIAL the exchange
    works on (`material`: `path` under the workspace, `branch`, `base`), composed here and
    the same for every provider -- the head of the prompt names it with the console's
    absolute path, `env` gains `PP_WORKDIR` and `PP_CONSOLE`, no provider flag --; the
    adapter receives it as judged and may refuse it, and one whose `launch` takes no
    `workdir` refuses `workdir-unsupported` before anything is composed. An adapter
    without the face refuses `launch-unsupported`; one whose face renders anything but
    the three elements refuses `launch-malformed`."""
    asked = judged(policy)
    resumed = session_of(session)
    held = material(workdir)
    module = load(provider, meta, root)
    face = getattr(module, "launch", None)
    if face is None:
        raise Refusal("launch-unsupported",
                      f"`{provider}` -- its adapter wires but composes no launch")
    if held and "workdir" not in inspect.signature(face).parameters:
        raise Refusal("workdir-unsupported",
                      f"`{provider}` -- its adapter composes a launch but takes no material (`workdir`)")
    where = Path(workspace).resolve()
    console = console_of(where)
    composed = face(where, Path(meta), marble, headed(prompt, held, console),
                    wiring=Path(wiring).resolve() if wiring is not None else None, policy=asked,
                    session=resumed, **({"workdir": held} if held else {}))
    if not isinstance(composed, tuple) or len(composed) != 3:
        raise Refusal("launch-malformed",
                      f"`{provider}` -- its adapter's launch renders {type(composed).__name__}"
                      f"{f' of {len(composed)}' if isinstance(composed, tuple) else ''}, not (argv, env, stdin)")
    argv, env, stdin = composed
    env = dict(env)
    if held:
        env.update({"PP_WORKDIR": held["path"], "PP_CONSOLE": str(console)})
    return [str(one) for one in argv], {str(key): str(value) for key, value in env.items()}, str(stdin)


ANSWER = ("cost_usd", "denials", "error", "session")   # the one shape every adapter's reading takes


def answer(provider: str, meta: Path, stdout: str, stderr: str,
           root: Path | None = None) -> dict:
    """-> what the harness ANSWERED beside its words, read by the adapter that chose its output
    format: `{cost_usd, denials, error, session}` -- the cost the harness reports (None when it
    reports none), the permissions it was denied, the error it names (None on success), the
    identity of the provider's session. No text: the model's text is the `words` its events
    say (`events`), in their order -- the one source; a key of the adapter's reading outside
    the four is dropped. The identity is owed: a reading that carries none refuses
    `session-missing`, naming the provider and citing the error read or the stream's tail.
    Nothing is run here: the skill that launched hands the streams it captured. An adapter
    without the face refuses `answer-unsupported`; one without the `events` face, whose text
    nobody can read, refuses `events-unsupported`."""
    module = load(provider, meta, root)
    face = getattr(module, "answer", None)
    if face is None:
        raise Refusal("answer-unsupported",
                      f"`{provider}` -- its adapter composes a launch but reads no answer")
    if getattr(module, "events", None) is None:
        raise Refusal("events-unsupported",
                      f"`{provider}` -- its adapter says no events: the model's words cannot be read")
    read = dict(face(str(stdout), str(stderr)))
    session = read.get("session")
    if not isinstance(session, str) or not session.strip():
        said = read.get("error") or (str(stdout).strip() or str(stderr).strip())[-300:] or "no output"
        raise Refusal("session-missing", f"`{provider}` answered no session identity -- {said}")
    read["session"] = session.strip()
    return {key: read.get(key, [] if key == "denials" else None) for key in ANSWER}


def contexts(provider: str, meta: Path, session: str, root: Path | None = None) -> dict | None:
    """-> what the provider's own store keeps of a session's calls, read by its adapter: `calls`, the context
    each call sent the model in tokens, in order, and `compactions`, the compactions the host made of the
    session; None when the adapter cannot read its store (no `contexts` face) or the store holds no such
    session. A reading of another shape refuses `contexts-malformed`, naming the provider. Reads only."""
    face = getattr(load(provider, meta, root), "contexts", None)
    read = face(session) if face is not None else None
    if read is None:
        return None
    calls = read.get("calls") if isinstance(read, dict) else None
    compactions = read.get("compactions") if isinstance(read, dict) else None
    if (not isinstance(calls, list) or not all(isinstance(one, int) and not isinstance(one, bool) and one >= 0
                                               for one in calls)
            or not isinstance(compactions, int) or isinstance(compactions, bool) or compactions < 0):
        raise Refusal("contexts-malformed", f"`{provider}` -- its contexts face renders no calls and compactions")
    return {"calls": list(calls), "compactions": compactions}


# the COMMON SCHEMA of the third face: kind -> (required fields and their types, optional fields and defaults)
EVENTS = {
    "tool": ({"id": str, "name": str}, {"title": "", "shell": None, "input": {}}),
    "tool-result": ({"id": str, "content": str}, {"error": False}),
    "thinking": ({}, {}),                      # `text` or `tokens`, one of the two at least
    "words": ({"text": str}, {}),              # and `delta`, True alone: a piece of a message streamed
    "context": ({"tokens": int}, {"id": ""}),  # what ONE call sent the model, in tokens; `id` the message it answered
}
_FACES: dict[Path, object] = {}                # the `events` face of each adapter read once, by its path


def events(provider: str, meta: Path, line: str, root: Path | None = None) -> list[dict]:
    """-> the events ONE line of a harness's standard output carries, read by the adapter that
    chose its output format, each in the COMMON SCHEMA -- `tool` {id, name, title, shell,
    input}: a call of a tool as it leaves, `shell` its command when the tool runs one; `tool-result`
    {id, content, error}: what the tool gave back, as the model read it; `thinking` {text and/or
    tokens}: the model's thought, its text when the host gives it, what it counts otherwise;
    `words` {text, delta}: words of the model during the launch, the last text included -- the ONE
    source of the model's text, `answer` says none; `delta`, kept only when True, says the text is a
    piece of a message the host streams in pieces: pieces that follow one another, no event between
    them, are one text; `context` {tokens, id}: the size of what one call sent the model -- its input,
    read from the cache or written to it --, as the host counts it, `id` the message the call answered.
    A field the schema does not name is dropped, an optional
    one absent takes its default; a kind outside the five, a required field missing or of another
    type, or a face that renders no list refuses `events-malformed`, naming the adapter and the kind.
    An adapter without the face refuses `events-unsupported`. Nothing is run here: the skill hands
    the line it read."""
    path = (product_of(meta) / "adapters" if root is None else root) / provider / "wire.py"
    if path not in _FACES:
        _FACES[path] = getattr(load(provider, meta, root), "events", None)
    face = _FACES[path]
    if face is None:
        raise Refusal("events-unsupported",
                      f"`{provider}` -- its adapter says no events: the model's words cannot be read")
    said = face(str(line))
    if not isinstance(said, list):
        raise Refusal("events-malformed", f"`{provider}` -- its events face renders {type(said).__name__}, not a list")
    return [_event(provider, one) for one in said]


class Reader:
    """The reader of ONE launch: what a launcher reads a harness's output with, line by line, and
    closes at the launch's end. Every event `heard` renders comes in the common schema WITHOUT
    `delta`: the pieces a host streams (`words` marked `delta` by the adapter) are held and rendered
    as ONE `words` at the next event of another nature, at a whole `words`, or at `end()` -- pieces
    that follow one another, no event between them, are one text. A `context` whose `id` is the one of
    the last `context` said is the same call told again (a host repeats a message's usage on each of its
    blocks): it is said once. The adapter stays a translation of one line; the reader is where a
    launch's words become whole and its calls counted once."""

    def __init__(self, provider: str, meta: Path, root: Path | None = None) -> None:
        self.provider, self.meta, self.root = provider, meta, root
        self._pieces: list[str] = []
        self._measured = ""                         # the id of the last `context` said

    def _whole(self) -> list[dict]:
        if not self._pieces:
            return []
        text, self._pieces = "".join(self._pieces), []
        return [{"kind": "words", "text": text}]

    def heard(self, line: str) -> list[dict]:
        """-> the events of ONE line, whole words among them; a refusal of the adapter's face rises as is."""
        said: list[dict] = []
        for one in events(self.provider, self.meta, line, self.root):
            if one["kind"] == "words" and one.pop("delta", False):
                self._pieces.append(one["text"])
                continue
            if one["kind"] == "context":
                if one["id"] and one["id"] == self._measured:
                    continue
                self._measured = one["id"]
            said += self._whole()
            said.append(one)
        return said

    def end(self) -> list[dict]:
        """-> the words still held at the launch's end, whole; [] when none."""
        return self._whole()


def reader(provider: str, meta: Path, root: Path | None = None) -> Reader:
    """-> a `Reader` of one launch for the adapter of `provider` (`events-unsupported` rises at its first
    line when the adapter says no events): one per launch, never shared between two."""
    return Reader(provider, meta, root)


def _event(provider: str, one) -> dict:
    """-> one event in the common schema, normalised; `events-malformed` when it is none."""
    kind = one.get("kind") if isinstance(one, dict) else None
    if kind not in EVENTS:
        raise Refusal("events-malformed", f"`{provider}` -- an event of kind `{kind}`: one of {', '.join(EVENTS)}")
    required, optional = EVENTS[kind]
    found: dict = {"kind": kind}
    for key, typed in required.items():
        value = one.get(key)
        if not isinstance(value, typed) or (typed is str and key != "content" and not value.strip()):
            raise Refusal("events-malformed", f"`{provider}` -- `{kind}` without its `{key}`")
        found[key] = value
    for key, default in optional.items():
        value = one.get(key, default)
        value = value if value is not None or default is None else default
        found[key] = dict(value) if isinstance(value, dict) else value     # never the shared default
    if kind == "tool":
        if not isinstance(found["title"], str) or not (found["shell"] is None or isinstance(found["shell"], str)) \
                or not isinstance(found["input"], dict):
            raise Refusal("events-malformed", f"`{provider}` -- `tool` with a title, shell or input of another type")
    if kind == "tool-result" and not isinstance(found["error"], bool):
        raise Refusal("events-malformed", f"`{provider}` -- `tool-result` with an `error` that is no boolean")
    if kind == "thinking":
        text, tokens = one.get("text"), one.get("tokens")
        if not isinstance(text, str) and not (isinstance(tokens, int) and not isinstance(tokens, bool)):
            raise Refusal("events-malformed", f"`{provider}` -- `thinking` without its `text` or its `tokens`")
        found.update({key: value for key, value in (("text", text), ("tokens", tokens)) if value is not None})
    if kind == "context" and (isinstance(found["tokens"], bool) or found["tokens"] < 0
                              or not isinstance(found["id"], str)):
        raise Refusal("events-malformed", f"`{provider}` -- `context` whose tokens are no count or whose id no text")
    if kind == "words" and one.get("delta") is not None:
        if not isinstance(one["delta"], bool):
            raise Refusal("events-malformed", f"`{provider}` -- `words` with a `delta` that is no boolean")
        if one["delta"]:
            found["delta"] = True
    return found
