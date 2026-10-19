"""Scenario `stream` -- 4 case(s) (batch les-evenements-du-harnais, 2026-10-09; plan fixes4, batch
la-remontee/core, 2026-10-17): the third face of the adapters' contract, `events(line)`, read through the
engine's face `conductor.adapters.events` -- the one source of the model's text --, and the answer read on a
stream:
- the face holds the COMMON SCHEMA: a witness adapter written at run time whose events carry an unknown
  field, no `shell`, no `error`, a `delta` False comes back normalised (the field dropped, `shell: None`,
  `error: False`, `delta` kept only when True); a kind nobody knows, a `tool` without its `id`, a `delta`
  that is no boolean, a face that renders no list refuse `events-malformed` naming the adapter; an adapter
  without the face refuses `events-unsupported`
- claude, VERIFIED: on the fixture RECORDED by the probe of 2026-10-09 (`streams/claude.jsonl`, the
  `system/init` line reduced to its stable fields), `answer()` renders what the last `result` line read
  alone renders, no text among it; `events()` line by line renders the `Bash` call with its `shell`, its
  result, the words, then the thinking counted (50, then 188 tokens), the last words the last text; the
  empty `thinking` block renders nothing
- codex, gemini, cursor, NOT VERIFIED on a machine: on their fixtures written from their docs
  (`streams/<host>.from-docs.jsonl`), `answer()` renders the session and no text, `events()` a shell call
  with its `shell`, its result, a failed call, the words -- their last text the model's last message,
  gemini's pieces said `delta` --, and codex its reasoning as thinking
"""
from __future__ import annotations

import json
from pathlib import Path

from conductor import Refusal, adapters

STREAMS = Path(__file__).resolve().parent / "streams"


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("stream").made

    def events_of(provider: str, text: str) -> list[dict]:
        found = []
        for line in text.splitlines():
            found += adapters.events(provider, made, line)
        return found

    def refusal_of(call) -> str:
        try:
            return f"accepted: {call()}"
        except Refusal as refusal:
            return f"{refusal.code}: {refusal}"
        except Exception as raised:                       # noqa: BLE001 -- said, never swallowed
            return f"{type(raised).__name__}: {raised}"

    # --- the face holds the common schema, on witnesses written at run time ---------------------------
    root = bench.temp() / "witness-adapters"
    faces = {
        "mute": "",
        "loose": ("def events(line):\n"
                  "    return [{'kind': 'tool', 'id': 't1', 'name': 'Run', 'input': {'x': 1}, 'colour': 'red'},\n"
                  "            {'kind': 'tool-result', 'id': 't1', 'content': 'ok'},\n"
                  "            {'kind': 'thinking', 'tokens': 12}, {'kind': 'words', 'text': 'hi', 'delta': False},\n"
                  "            {'kind': 'words', 'text': ' there', 'delta': True}]\n"),
        "strange": "def events(line):\n    return [{'kind': 'dance'}]\n",
        "anonymous": "def events(line):\n    return [{'kind': 'tool', 'name': 'Run'}]\n",
        "scalar": "def events(line):\n    return 'tool'\n",
        "wavy": "def events(line):\n    return [{'kind': 'words', 'text': 'hi', 'delta': 'yes'}]\n",
    }
    for name, face in faces.items():
        wire = root / name / "wire.py"
        wire.parent.mkdir(parents=True)
        wire.write_text("def wire(workspace, meta):\n    return []\n\n\n" + face, encoding="utf-8")
    try:
        loose = adapters.events("loose", made, "any line", root=root)
    except Exception as raised:                           # an AttributeError before the batch
        loose = [f"{type(raised).__name__}: {raised}"]
    mute = refusal_of(lambda: adapters.events("mute", made, "any line", root=root))
    refused = {name: refusal_of(lambda name=name: adapters.events(name, made, "any line", root=root))
               for name in ("strange", "anonymous", "scalar", "wavy")}
    if (loose == [{"kind": "tool", "id": "t1", "name": "Run", "title": "", "shell": None, "input": {"x": 1}},
                  {"kind": "tool-result", "id": "t1", "content": "ok", "error": False},
                  {"kind": "thinking", "tokens": 12}, {"kind": "words", "text": "hi"},
                  {"kind": "words", "text": " there", "delta": True}]
            and mute.startswith("events-unsupported") and "mute" in mute
            and all(one.startswith("events-malformed") and name in one for name, one in refused.items())
            and "dance" in refused["strange"] and "tool" in refused["anonymous"] and "delta" in refused["wavy"]):
        held("the face holds the common schema", "an unknown field dropped, shell None and error False posed, "
             "delta kept only when True; a kind nobody knows, a tool without its id, a delta no boolean, a face "
             "rendering no list refuse events-malformed naming the adapter; no face: events-unsupported")
    else:
        failures.append(f"  ✗ common schema               {loose} {mute} {refused}")

    # --- claude, verified: the recorded stream -----------------------------------------------------------
    claude = (STREAMS / "claude.jsonl").read_text(encoding="utf-8")
    results = [line for line in claude.splitlines() if json.loads(line).get("type") == "result"]
    try:
        streamed = adapters.answer("claude", made, claude, "")
        alone = adapters.answer("claude", made, results[-1], "")
    except Exception as raised:
        streamed, alone = {"raised": f"{type(raised).__name__}: {raised}"}, {}
    if streamed == alone and "response" not in streamed and isinstance(streamed.get("cost_usd"), float) \
            and streamed.get("session") == "5b1c7ee4-d348-4f23-a25b-6edb99dc46e8" and streamed.get("denials") == []:
        held("claude reads its answer on the stream", f"the stream renders what its last result line renders: "
             f"{streamed}")
    else:
        failures.append(f"  ✗ claude answer               {streamed} / {alone}")
    try:
        said = events_of("claude", claude)
    except Exception as raised:
        said = [{"raised": f"{type(raised).__name__}: {raised}"}]
    if said == [{"kind": "tool", "id": "toolu_01RiFYjEsXBkb3LkZTPDjWup", "name": "Bash", "title": "echo hello-probe",
                 "shell": "echo hello-probe",
                 "input": {"command": "echo hello-probe", "description": "Print a test string"}},
                {"kind": "tool-result", "id": "toolu_01RiFYjEsXBkb3LkZTPDjWup", "content": "hello-probe", "error": False},
                {"kind": "words", "text": "hello-probe"},
                {"kind": "thinking", "tokens": 50}, {"kind": "thinking", "tokens": 188},
                {"kind": "words", "text": "927"}]:
        held("claude says its events, verified", "the Bash call with its shell, its result, the words; the thinking "
             "counted 50 then 188 tokens, the empty thinking block nothing; the last words the last text")
    else:
        failures.append(f"  ✗ claude events               {said}")

    # --- codex, gemini, cursor, from their docs: NOT verified on a machine ---------------------------------
    hosts = {"codex": ("The repository holds docs and src.", "0199a213-81c0-7800-8aa1-bbab2a035a53", "bash -lc ls"),
             "gemini": ("The repository holds docs and src.", "c25acda3-b51f-41f9-9bc5-954c70c17bf4", "ls"),
             "cursor": ("The repository holds docs and src.", "c6b62c6f-7ead-4fd6-9922-e952131177ff", "ls")}

    def texts_of(said: list[dict]) -> list[str]:
        """-> the texts the words say, in order -- pieces that follow one another, `delta`, are one text."""
        texts, piece = [], False
        for one in said:
            if one["kind"] == "words" and one.get("delta") and piece:
                texts[-1] += one["text"]
            elif one["kind"] == "words":
                texts.append(one["text"])
            piece = one["kind"] == "words" and bool(one.get("delta"))
        return texts
    seen = {}
    for host, (response, session, shell) in hosts.items():
        text = (STREAMS / f"{host}.from-docs.jsonl").read_text(encoding="utf-8")
        try:
            read = adapters.answer(host, made, text, "")
            said = events_of(host, text)
        except Exception as raised:
            seen[host] = f"{type(raised).__name__}: {raised}"
            continue
        tools = [one for one in said if one["kind"] == "tool"]
        results = {one["id"]: one for one in said if one["kind"] == "tool-result"}
        words = texts_of(said)
        seen[host] = {"text": "response" in read, "last": words[-1] if words else None, "session": read.get("session"),
                      "shells": [one["shell"] for one in tools], "errors": [results[one["id"]]["error"] for one in tools
                                                                            if one["id"] in results],
                      "words": words, "thinking": [one.get("text") for one in said if one["kind"] == "thinking"]}
    if (all(isinstance(seen.get(host), dict) and not seen[host]["text"] and seen[host]["last"] == response
            and seen[host]["session"] == session
            and seen[host]["shells"][0] == shell and seen[host]["errors"] == [False, True] and seen[host]["words"]
            for host, (response, session, shell) in hosts.items())
            and seen["codex"]["thinking"] == ["**Listing the repository**"]):
        held("codex, gemini, cursor say their events -- NOT VERIFIED on a machine",
             "on fixtures written from their docs: the session and no text; a shell call with its shell, its "
             "result, a failed call, the words, the last text the model's last message, gemini's pieces one; "
             "codex's reasoning as thinking")
    else:
        failures.append(f"  ✗ from the docs               {seen}")
    return 0
