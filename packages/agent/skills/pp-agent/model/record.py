"""A record's line: what a type of one is read with and written by -- a field per key, the line's own keys and
what the fields cannot give back, kept for the line to be written as it was."""
from __future__ import annotations

import json
from dataclasses import MISSING, field, fields

READ = ("keys", "kept")         # what a line read leaves beside the fields: its keys, what they cannot give back


def _read(kind, line: dict) -> dict:
    """-> what a type of a record's line is built with, read from `line`: a field per key it names -- a field
    that is a type itself reads its own mapping (`of`), a field whose items are types reads each of them
    (`each`), None where its reader finds nothing to read --, the line's `keys` in their order, and `kept`, what
    the fields cannot give back: a key the type does not name, a value its typed field would write otherwise."""
    named = {one.metadata.get("key", one.name): one for one in fields(kind) if one.name not in READ}
    found, kept = {}, []
    for key, value in line.items():
        if key not in named:
            kept.append((key, value))
            continue
        typed, each = named[key].metadata.get("of"), named[key].metadata.get("each")
        read = value
        if typed:
            read = typed(value)
        elif each:
            items = tuple(each(one) for one in value) if isinstance(value, list) else (None,)
            read = None if any(one is None for one in items) else items
        found[named[key].name] = read
        if (typed or each) and (read is None or json.dumps(_said(named[key], read)) != json.dumps(value)):
            kept.append((key, value))
    return {**found, "keys": tuple(line), "kept": tuple(kept)}


def _said(field, value):
    """-> what a field writes of its value: a type by its `json()`, a tuple of types by each one's, in a list;
    any other value, and None, as it stands."""
    if value is None:
        return None
    if field.metadata.get("of"):
        return value.json()
    if field.metadata.get("each"):
        return [one.json() for one in value]
    return value


def _written(one) -> dict:
    """-> the line of a record: for a type read from one, the line as it was, key for key in its order; for a
    type composed to be written, a key per field in their order -- always, null when unnamed, but for the fields
    declared `named`, written only when they name something. A line whose keys leave out a field that names
    something would be written without it: a `ValueError`."""
    said = {field.metadata.get("key", field.name): (field, getattr(one, field.name))
            for field in fields(one) if field.name not in READ}
    said = {key: (field, _said(field, value)) for key, (field, value) in said.items()}
    if one.keys is not None:
        lost = [key for key, (field, _) in said.items()
                if key not in one.keys and getattr(one, field.name) != _unnamed(field)]
        if lost:
            raise ValueError(f"{type(one).__name__} names {', '.join(lost)}, which the keys of its line leave out")
        held = dict(one.kept)
        return {key: held[key] if key in held else said[key][1] for key in one.keys}
    return {key: value for key, (field, value) in said.items() if value is not None or not field.metadata.get("named")}


def _unnamed(field):
    """-> what a field holds when nothing names it: its default."""
    return field.default_factory() if field.default_factory is not MISSING else field.default


def only_named():
    """-> a field written only when it names something: absent from the line otherwise."""
    return field(default=None, metadata={"named": True})
