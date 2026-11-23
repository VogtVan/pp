"""files -- a values file of a team (`TEAM.md`, `SEASON.md`) as the post reads it from the text a face gives and shows
it as `team declare` will write it: its keys -- a scalar, or a block of lines, each line named by its first word (a
value by its name before `=`, an edge by the member it reports to) --, its body; the changes a form makes, key by key
and line by line, each line named and written as `team declare` names and writes it. Pure: no I/O, no Textual."""
from __future__ import annotations

import json

BORDER = "---"
BLOCK = "|"


def split(text: str) -> tuple[list[str], str]:
    """-> the lines of the front matter, its borders left out, and the body after it; no front matter, `[]` and the
    text whole."""
    lines = text.split("\n")
    if lines[:1] != [BORDER]:
        return [], text
    end = next((n for n in range(1, len(lines)) if lines[n].strip() == BORDER), None)
    if end is None:
        return [], text
    return lines[1:end], "\n".join(lines[end + 1:])


def _scalar(said: str) -> str:
    """-> a scalar as the file says it, its JSON quotes read."""
    said = said.strip()
    if said.startswith('"'):
        try:
            return str(json.loads(said))
        except ValueError:
            return said
    return said


def read(text: str) -> dict[str, str | list[str]]:
    """-> the keys of the front matter: a scalar as a text, a block (`key: |`) as its lines stripped, blanks left out."""
    found: dict[str, str | list[str]] = {}
    key = None
    for line in split(text)[0]:
        if line[:1] in (" ", "\t") and key is not None and isinstance(found.get(key), list):
            if line.strip():
                found[key].append(line.strip())
            continue
        name, colon, said = line.partition(":")
        if not colon or not name.strip() or line[:1] in (" ", "\t"):
            key = None
            continue
        key = name.strip()
        found[key] = [] if said.strip() == BLOCK else _scalar(said)
    return found


def name_of(key: str, line: str) -> str:
    """-> the name a line of a block goes by: a value its name before `=`, an edge the member it reports to (after
    `->`), any other line its first word."""
    if key == "values":
        return line.partition("=")[0].strip()
    if key == "reports":
        return line.partition("->")[2].strip()
    return (line.split() or [""])[0]


def written_line(key: str, line: str) -> str:
    """-> a line of a block as `team declare` writes it: an edge `<member>... -> <member>` its blanks one each, any other
    line stripped."""
    if key == "reports" and "->" in line:
        sources, _, target = line.partition("->")
        return f"{' '.join(sources.split())} -> {target.strip()}"
    return line.strip()


def by_name(key: str, lines: list[str], typed: bool = False) -> dict[str, str]:
    """-> the lines of a block by their name, each written as `team declare` writes it: of a file, the first line of a
    name kept, as `team declare` reaches the first edge of a member; of a field (`typed`), the last one -- the line
    typed last is the one asked; of `documents:`, the lines of a key ONE line, every document of them kept, as the
    list of documents writes it."""
    if key == "documents":
        return {name: " ".join([name, *named]) for name, named in documents_by("\n".join(lines)).items()}
    found: dict[str, str] = {}
    for line in lines:
        if typed:
            found.pop(name_of(key, line), None)
            found[name_of(key, line)] = written_line(key, line)
        else:
            found.setdefault(name_of(key, line), written_line(key, line))
    return found


def lines_of(text: str) -> list[str]:
    """-> the lines of a field of several lines, stripped, blanks left out."""
    return [line.strip() for line in str(text or "").splitlines() if line.strip()]


def line_changes(key: str, before: list[str], after: list[str]) -> tuple[list[str], list[str]]:
    """-> (the lines of `after` new or changed against `before`, by their name; the names of `before` gone)."""
    then, now = by_name(key, before), by_name(key, after, typed=True)
    same = lambda one, other: " ".join(str(one).split()) == " ".join(str(other).split())
    return ([line for name, line in now.items() if name not in then or not same(then[name], line)],
            [name for name in then if name not in now])


def written(text: str, scalars: dict[str, str | None], blocks: dict[str, list[str]],
            body: str | None = None) -> str:
    """-> the file `text` as it will be written: each scalar of `scalars` set (None takes the key out), each block of
    `blocks` set to its lines -- a line of the same name in place, a new one at the end, one gone taken out; a block
    left without a line goes --, the body replaced whole under `body`, as `team declare --body-file` replaces it; every
    other line as it stands, and the body at its bytes -- the blank line after the front matter kept. A text without a
    front matter is given one."""
    front, said_body = split(text)
    front = list(front)
    for key, value in scalars.items():
        at = next((n for n, line in enumerate(front) if line.partition(":")[0].strip() == key
                   and line[:1] not in (" ", "\t")), None)
        line = None if value is None else f"{key}: {value}"
        if at is None and line is not None:
            front.append(line)
        elif at is not None and line is None:
            del front[at]
        elif at is not None:
            front[at] = line
    for key, lines in blocks.items():
        at = next((n for n, line in enumerate(front) if line.partition(":")[0].strip() == key
                   and line[:1] not in (" ", "\t")), None)
        end = at
        old: list[str] = []
        if at is not None:
            end = at + 1
            while end < len(front) and (front[end][:1] in (" ", "\t") or not front[end].strip()):
                if front[end].strip():
                    old.append(front[end].strip())
                end += 1
        kept = by_name(key, lines, typed=True)
        olds = [name_of(key, line) for line in old]
        merged = [kept[name] for name in dict.fromkeys(olds) if name in kept]
        merged += [line for name, line in kept.items() if name not in olds]
        made = [f"{key}: |", *(f"  {line}" for line in merged)] if merged else []
        if at is None:
            front += made
        else:
            front[at:end] = made
    return "\n".join([BORDER, *front, BORDER]) + "\n" + (said_body if body is None else body)


def documents_by(text: str) -> dict[str, list[str]]:
    """-> the documents each key of a field of `documents:` gives, `<key>|all <document> ...` per line: `{key:
    [document, ...]}` in their order, a key written on several lines the documents of all of them, each once."""
    found: dict[str, list[str]] = {}
    for line in lines_of(text):
        key, named = line.split()[0], line.split()[1:]
        found.setdefault(key, [])
        found[key] += [one for one in named if one not in found[key]]
    return found


def keys_given(text: str, document: str) -> list[str]:
    """-> the keys whose line of `documents:` names `document`, in their order."""
    return [key for key, named in documents_by(text).items() if document in named]


def documents_given(text: str, document: str, keys: list[str]) -> str:
    """-> the field of `documents:` with `document` given to `keys` alone, ONE line per key -- the lines of a key
    written twice made one, every document of them kept --: `document` added at the end of the line of each key of
    `keys` that lacks it -- a new line `<key> <document>` for a key without one --, taken out of the line of every
    other key, a line left without a document taken out; every other document and order as it stands."""
    given = documents_by(text)
    for key, named in given.items():
        if key in keys and document not in named:
            named.append(document)
        elif key not in keys and document in named:
            named.remove(document)
    given.update({key: [document] for key in keys if key not in given})
    return "\n".join(" ".join([key, *named]) for key, named in given.items() if named)


def values_of(text: str) -> dict[str, str]:
    """-> the values a field of `values:` gives, `<name> = <value>` per line: `{name: value}` in their order."""
    return {line.partition("=")[0].strip(): line.partition("=")[2].strip() for line in lines_of(text) if "=" in line}


def values_merged(text: str, given: dict[str, str]) -> str:
    """-> the field of `values:` with each value of `given` set: its line in place when it stands, a new line at the
    end otherwise; a value given empty takes its line out; every other line as it stands."""
    lines, done = [], set()
    for line in lines_of(text):
        name = name_of("values", line)
        if name not in given:
            lines.append(line)
        elif given[name]:
            lines.append(f"{name} = {given[name]}")
        done.add(name)
    lines += [f"{name} = {value}" for name, value in given.items() if value and name not in done]
    return "\n".join(lines)
