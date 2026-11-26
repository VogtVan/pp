"""The `journal` domain, layer `faces`: how the journal's events are put into words.

A definition belongs here when it turns an event into what a user reads -- one line of the log, the object `--json`
gives, the words of a deletion, a text made safe to show -- and gives it back without printing it. `shown` and
`event_object` read by key what the reader of the journal returns (`read_on`, `journal/replay.py`): the line of an
event, or the dictionary that says a post in the words of its debt. That is the edge where the log is printed.
"""
from __future__ import annotations

import json

from journal.model import RETURNED_MARK
from rhythm.faces import said_when


def deleting_said(name: str) -> str:
    """-> the refusal of a write on a team a delete has begun to remove (`deleting` written)."""
    return f"team-deleting -- {name} is being deleted: `team delete {name} --yes` again finishes it."


# --- the readers: watch, log, result, inbox ------------------------------------------------

def harmless(text: str) -> str:
    """-> a text an agent or a principal wrote, as stdout may print it: each line opening on
    `::`, blanks before it included, prefixed with a backslash -- the console reads such a line
    as a directive of the house's bus, and nobody's words give pp an order."""
    return "\n".join("\\" + one if one.lstrip().startswith("::") else one for one in text.split("\n"))


def shown(one: dict) -> str:
    """-> one event as ONE line: `#<id> <kind> <what it says>` -- the form `log` prints and
    `watch` writes on stderr; a text of several lines is said on one."""
    kind = one.get("kind")
    text = " ".join(str(one.get("text") or "").split())
    short = text if len(text) <= 60 else text[:57] + "…"
    if kind == "post":
        return (f"#{one.get('id')} post {one.get('verb')}" + (f" #{one['re']}" if one.get("re") is not None else "")
                + f" {one.get('from')} -> {one.get('to')} on {one.get('task')}"
                + (f" · about {one['about']}" if one.get("about") else "")
                + (" · info" if one.get("info") else "") + (" · by the tick" if one.get("by") == "tick" else "")
                + (RETURNED_MARK if one.get("returned") else "")
                + (f": {short}" if short else ""))
    if kind == "task":
        return (f"#{one.get('id')} task {one.get('task')}" + (f" {one['name']}" if one.get("name") else "")
                + f" from {one.get('from')} to {one.get('to')}: {short}")
    if kind == "team-started":
        return f"#{one.get('id')} team-started · members {', '.join(one.get('agents') or {})} · root {one.get('root')}"
    if kind == "wake-intent":
        return f"#{one.get('id')} wake-intent {one.get('agent')} on {one.get('task')} · tag {one.get('tag')}"
    if kind == "wake-launched":
        return (f"#{one.get('id')} wake-launched {one.get('agent')} · run {one.get('run')} · pid {one.get('pid')}"
                + (f" · name refused: {one['name-refused']}" if one.get("name-refused") else ""))
    if kind == "wake-ended":
        return (f"#{one.get('id')} wake-ended {one.get('agent')} · run {one.get('run')}"
                + (f" · launch {one.get('launch')}" if one.get("launch") is not None else "")
                + (f" · {one.get('state')}" if one.get("state") else "") + f" · cost {one.get('cost')}")
    if kind == "wake-routed":
        return (f"#{one.get('id')} wake-routed {one.get('agent')} · run {one.get('run')} · words {one.get('words')}"
                + (" · nowhere" if one.get("nowhere") else ""))
    if kind == "wake-refused":
        return f"#{one.get('id')} wake-refused {one.get('agent')} · run {one.get('run')} · {one.get('why')}"
    if kind == "wake-failed":
        return (f"#{one.get('id')} wake-failed {one.get('agent')} on {one.get('task')} · {one.get('reason')}"
                + (f" · spent {one.get('spent')} of its share {one.get('share')} USD" if "share" in one else "")
                + (" · the house" if one.get("house") else "") + (" · final" if one.get("final") else ""))
    if kind == "wake-halted":
        return (f"#{one.get('id')} wake-halted {one.get('agent')} on {one.get('task')} · {one.get('count')} failures in "
                f"a row · {one.get('reason')}")
    if kind == "quota-reached":
        return (f"#{one.get('id')} quota-reached {one.get('agent')} on {one.get('task')} · until "
                f"{one.get('until') or 'team resume'}" + (f" · {one['said']}" if one.get("said") else ""))
    if kind == "quota-lifted":
        return f"#{one.get('id')} quota-lifted {', '.join(one.get('members') or [])} · by {one.get('by')}"
    if kind == "timer-armed":
        return f"#{one.get('id')} timer-armed · due {str(one.get('due'))[11:19]}"
    if kind == "wake-killed":
        return f"#{one.get('id')} wake-killed {one.get('agent')} on {one.get('task')} · run {one.get('run')} · pid {one.get('pid')}"
    if kind == "deferred":
        return f"#{one.get('id')} {kind} {one.get('agent')} on {one.get('task')}"
    if kind == "done":
        return f"#{one.get('id')} done {one.get('task')} · {json.dumps(one.get('result'), ensure_ascii=False)}"
    if kind == "returned":
        return f"#{one.get('id')} returned #{one.get('message')} to {one.get('to')}"
    if kind == "stopped":
        return f"#{one.get('id')} stopped {one.get('task')} by {one.get('by')}"
    if kind == "ceremony-due":
        return (f"#{one.get('id')} ceremony-due {one.get('ceremony')} · {one.get('period')}"
                + (f" by {one.get('by')}" if one.get("by") else ""))
    if kind == "resumed":
        return f"#{one.get('id')} resumed {one.get('task')} by {one.get('by')} · from {', '.join(one.get('from') or [])}"
    if kind == "recurrence":
        when = one.get("when") or {}
        return (f"#{one.get('id')} recurrence {one.get('recurrence')}" + (f" {one['name']}" if one.get("name") else "")
                + f" from {one.get('from')} to {one.get('to')} · every {said_when(when)}"
                + (f" · from {one['task']}" if one.get("task") else "")
                + (f" · context {one['context']}%" if one.get("context") is not None else "") + f": {short}")
    if kind == "recurrence-skipped":
        return f"#{one.get('id')} recurrence-skipped {one.get('recurrence')} · {one.get('period')} · {one.get('open')} open"
    if kind == "recurrence-stopped":
        return f"#{one.get('id')} recurrence-stopped {one.get('recurrence')} by {one.get('by')}"
    if kind in ("recurrence-paused", "recurrence-resumed"):
        return f"#{one.get('id')} {kind} {one.get('recurrence')} by {one.get('by')}"
    if kind == "recurrence-changed":
        when = one.get("when") or {}
        return (f"#{one.get('id')} recurrence-changed {one.get('recurrence')} by {one.get('by')}"
                + (f" · every {said_when(when)}" if "when" in one else "")
                + (f" · context {one['context']}%" if one.get("context") is not None
                   else " · context off" if "context" in one else "")
                + (" · description changed" if "description" in one else "")
                + (f": {short}" if "text" in one else ""))
    if kind == "run-renewed":                            # a null model or provider is said `none`; a pair unchanged, silent
        said = lambda value: "none" if value is None else value
        return (f"#{one.get('id')} run-renewed {one.get('member')} · run {one.get('run')}"
                + (f" of {one.get('recurrence')}" if one.get("recurrence") else "") + f" on {one.get('task')} · "
                + (", ".join(f"{key} {said((one.get('was') or {}).get(key))} -> {said((one.get('now') or {}).get(key))}"
                             for key in ("model", "provider")
                             if (one.get("was") or {}).get(key) != (one.get("now") or {}).get(key))
                   if one.get("why") == "model"
                   else f"used {round(float(one.get('used') or 0) * 100)}% of {one.get('limit')}%"))
    if kind == "budget-spent":
        return (f"#{one.get('id')} budget-spent {one.get('spent')} of {one.get('budget')} "
                + ("launches" if one.get("unit") in ("launches", "wakes") else "USD"))
    if kind == "silence":
        return (f"#{one.get('id')} silence {one.get('agent')} on {one.get('task')} · "
                f"{one.get('passages', one.get('exchanges'))} exchange(s)")   # `exchanges`: a journal of before
    if kind == "inbox-seen":
        return f"#{one.get('id')} inbox-seen up to #{one.get('upto')}"
    if kind == "inbox-read":
        return f"#{one.get('id')} inbox-read #{one.get('message')}"
    return f"#{one.get('id')} {kind}"


def event_object(name: str, one: dict) -> dict:
    """-> one journal event as the faces give it: `{at, team, event, ...}` -- its kind as `event`,
    the rest of its fields, its `id` among them. `watch --json` and `log --json` both write it."""
    return {"at": one.get("at"), "team": name, "event": one.get("kind"),
            **{key: value for key, value in one.items() if key not in ("at", "kind", "team")}}
