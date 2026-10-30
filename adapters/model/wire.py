"""The `model` adapter: the LLM MODELLED -- a provider whose harness is a script of the product
(`adapters/model/harness.py`) that reads a block by its structure and the engine's constants, decides
by the data of `semantics.py`, and acts: the call due with a conforming production of the form due,
`words` for a `=> words` step, or nothing. Deterministic, without content, without network, cost 0.

It wires no surface: nothing names it at `-install`, a launch names it by `--provider model`. Its
policy has ONE key, `model`, which names the VARIANT of its judgment: `conform` (the default), or a
variant that misses exactly ONCE, at the first place where the miss is possible, then conforms --
`wrong-form`, `wrong-channel`, `missing-code`, `bare-call`, `empty`. A budget, a regime or an effort
refuse `policy-unsupported`: the model spends nothing and reasons as much as its data say.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().with_name("harness.py")   # the modelled LLM, launched by the interpreter

SPELLS = ("model",)                                 # the one key `launch` spells: the variant of the judgment
MODELS = ("conform", "wrong-form", "wrong-channel", "missing-code", "bare-call", "empty")   # the variants
COST = "launch"                                     # the scope of the cost `answer` reads: this launch alone, 0
BINARY = None                                       # no binary: the interpreter on the harness is all a launch needs
CAP = None                                          # the modelled LLM reads any size: no cap -- the engine's floor holds,
CAPS: dict[str, int] = {}                           # so a campaign under `model` keeps playing the chunk at the prompt
GRAMMAR = ("words", "tool", "tool-result", "thinking")   # the kinds a line of the harness may say
RESULT = "result"                                   # the kind of the harness's last line: what `answer` reads


def wire(workspace: Path, meta: Path) -> list[str]:
    """The model writes no surface: no card, no launcher, no permission -- a launch names it."""
    print("pp: the model adapter wires nothing -- a launch names it by `--provider model`")
    return []


def launch(workspace: Path, meta: Path, marble: Path | None, prompt: str,
           wiring: Path | None = None, policy: dict | None = None,
           session: str | None = None, workdir: dict | None = None) -> tuple[list[str], dict[str, str], str]:
    """-> `(argv, env, stdin)`: the interpreter on `harness.py` with the variant and the session, the
    prompt whole on stdin, an empty env -- the model reads no marble and no wiring: it reads the block.
    A key of the policy the model does not spell refuses `policy-unsupported`, naming the model and
    the key; the variant goes to the harness as given, which refuses one it does not know."""
    from conductor.core.errors import Refusal
    policy = policy or {}
    for key in policy:
        if key not in SPELLS:
            raise Refusal("policy-unsupported", f"`model` spells no `{key}` -- its one key is `model`, the variant")
    argv = [sys.executable, str(HARNESS), "--variant", str(policy.get("model", MODELS[0]))]
    if session:
        argv += ["--session", session]
    return argv, {}, prompt


def answer(stdout: str, stderr: str) -> dict:
    """-> the reading of ONE launch: the LAST `result` line of the harness -- `cost_usd` 0.0, `denials`
    [], `error` what it names, `session` its identity. A stdout with no such line is unreadable: the
    error says so and cites its tail."""
    read = _result_of(stdout)
    if read is None:
        return {"cost_usd": None, "denials": [], "error": f"unreadable: {(stdout or stderr).strip()[-300:]}",
                "session": None}
    return {"cost_usd": float(read.get("cost_usd") or 0.0), "denials": list(read.get("denials") or []),
            "error": read.get("error"), "session": str(read.get("session") or "").strip() or None}


def _result_of(stdout: str) -> dict | None:
    for line in reversed(str(stdout).splitlines()):
        try:
            one = json.loads(line)
        except ValueError:
            continue
        if isinstance(one, dict) and one.get("kind") == RESULT:
            return one
    return None


def events(line: str) -> list[dict]:
    """ONE line of the harness -> its event in the common schema: the harness says each event as one
    JSON object whose `kind` is `words`, `tool`, `tool-result` or `thinking`, the fields of the schema
    as they are; the `result` line, or a line that does not read, says nothing."""
    try:
        data = json.loads(line)
    except ValueError:
        return []
    if not isinstance(data, dict) or data.get("kind") not in GRAMMAR:
        return []
    return [data]
