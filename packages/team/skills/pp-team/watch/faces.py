"""The `watch` domain, layer `faces`: how a watch puts a launch's activity into words.

A definition belongs here when it turns one event of a launch's flow into what a user reads -- the object `--json`
gives, or the line the text says -- and gives it back without printing it. A line of a launch's flow is no event of
the journal: it stays a dictionary, read by key.
"""
from __future__ import annotations

from watch.model import ACTIVITY_TEXT


def activity_of(kind: str, one: dict) -> dict:
    """-> what an `activity` object of `watch` says of one event of a flow: a `tool` its `name`, its `title` and
    `pp`; a `tool-result` its `error` and the `size` of its content -- never the content --; a `thinking` its
    `tokens` or its `text`; `words` its `text`; a `context` its `tokens`, `used` and `window`; every text cut at
    `ACTIVITY_TEXT`."""
    def cut(text: object) -> str:
        return " ".join(str(text or "").split())[:ACTIVITY_TEXT]
    if kind == "tool":
        return {"kind": kind, "name": str(one.get("name") or ""), "title": cut(one.get("title")), "pp": one.get("pp") is True}
    if kind == "tool-result":
        return {"kind": kind, "error": one.get("error") is True, "size": len(str(one.get("content") or ""))}
    if kind == "thinking":
        tokens = one.get("tokens")
        return {"kind": kind, "tokens": tokens} if isinstance(tokens, int) else {"kind": kind, "text": cut(one.get("text"))}
    if kind == "words":
        return {"kind": kind, "text": cut(one.get("text"))}
    return {"kind": kind, "tokens": one.get("tokens"), "used": one.get("used"), "window": one.get("window")}


def activity_line(fields: dict) -> str:
    """-> an activity as the text watch says it: `tool Read · pp.py`, `result ✓ 10.0 kB`, `thinking <text>`,
    `words <text>`, `context 34000 tokens`."""
    kind = fields.get("kind")
    if kind == "tool":
        return f"tool {fields.get('name')}" + (f" · {fields['title']}" if fields.get("title") else "")
    if kind == "tool-result":
        size = int(fields.get("size") or 0)
        said = f"{size} B" if size < 1024 else f"{size / 1024:.1f} kB"
        return f"result {'✗' if fields.get('error') else '✓'} {said}"
    if kind == "context":
        return f"context {fields.get('tokens')} tokens"
    return f"{kind} {fields.get('text') if fields.get('text') is not None else fields.get('tokens', '')}".rstrip()
