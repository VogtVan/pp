"""core.document -- a file becomes a Document, its front matter a Procedure: the
PARSER of the engine's documents, a datum like the model it feeds. Nothing here
serves, slices or proves a reading (that is `reading`, the process above): the
data layer reads its own files -- settings, instance, persistence -- without
reaching upward."""
from __future__ import annotations

import os
import time
import re
from pathlib import Path

import yaml

from . import language, tokens
from .errors import Refusal
from .model import Constraint, Document, Instruction, Procedure

_PARSED: dict[str, dict[str, object]] = {}   # the front matters parsed this process, by CONTENT
_READ: dict[tuple, str] = {}                 # the files read this process, by path and state
FRESH_NS = 50_000_000    # 50 ms: wider than any kernel file-timestamp tick (1-10 ms) -- a
                         # file younger than this is served from disk, never from the drawer

BORDER = "---"


STATEMENT = re.compile(r"^([A-Z]+)(?:\s+(?!\^)(\S*\[[^\]]*\]|\S+))?"
                       r"(?:\s+\^\s+@([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+))?$")


LAW = re.compile(r"^(\S+)\s+(.+)$")


def text_of(path: Path, stamp: os.stat_result) -> str:
    """-> the file's text, read from disk ONCE per state of its bytes. The key is the
    path as the caller spelled it plus what `stat` says of the file -- its last write
    and its size; a file rewritten between two calls carries a new key and is read
    again. The drawer is bounded and purged like `_PARSED`, its twin one layer down.

    documentary: a boot reads seventeen documents and calls for them four hundred and
    seventy times -- the same TURN, the same MEMBER, over and over. What costs there is
    not the parse (already memoized by content) but the file access, and a `stat` is the
    cheap half of it. A miss is harmless -- two spellings of one path simply read twice;
    a wrong hit would not be, which is why the state, never the path alone, is the key."""
    key = (os.fspath(path), stamp.st_mtime_ns, stamp.st_size)
    known = _READ.get(key)
    if known is not None:
        return known
    text = path.read_text(encoding="utf-8")
    if time.time_ns() - stamp.st_mtime_ns < FRESH_NS:
        # a file written within the clock's own granularity is not cached: two writes
        # of one size inside the same timestamp tick share the key, and the drawer
        # would hand the first text back for the second -- read, never remember, until
        # the file has aged past the tick (la-veille-de-core, le-banc-stable)
        return text
    if len(_READ) > 4096:
        _READ.clear()          # a bench installs thousands of instances -- bound the drawer
    _READ[key] = text
    return text


def read(path: Path) -> Document:
    try:
        stamp = path.stat()
    except OSError:
        raise Refusal("document-missing", f"{path} does not exist")
    lines = text_of(path, stamp).splitlines()
    if not lines or lines[0].strip() != BORDER:
        raise Refusal("front-matter-missing", f"{path.name} does not open with a front matter")
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    if end is None:
        raise Refusal("front-matter-unterminated", f"{path.name} never closes its front matter")
    # SKILL.md is the MOLD's filename, never an identity: a contract is named by its
    # directory -- the same name the catalog and the dispatch resolve it under
    name = path.parent.name if path.stem == "SKILL" else path.stem
    return Document(name=name, front=front_matter(lines[1:end]), path=path)


def front_matter(lines: list[str]) -> dict[str, object]:
    """The front matter is YAML -- `yaml.safe_load`, one flat mapping. Values keep
    their YAML types (`true` is a bool, `3` an int); a key holding null is treated
    as ABSENT (a bare `tools:` declares nothing); a non-mapping or broken front
    matter refuses by name. The parse is memoized by content: catalog sweeps read
    the same few hundred documents thousands of times."""
    raw = "\n".join(lines)
    known = _PARSED.get(raw)
    if known is not None:
        return dict(known)     # a fresh top -- no caller ever mutates another's read
    try:
        loaded = yaml.safe_load(raw)
    except yaml.YAMLError as wrong:
        raise Refusal("front-matter-invalid",
                      f"the front matter is not valid YAML -- {str(wrong).splitlines()[0]}")
    if loaded is None:
        parsed: dict[str, object] = {}
    elif not isinstance(loaded, dict) or any(not isinstance(key, str) for key in loaded):
        raise Refusal("front-matter-invalid",
                      "the front matter must be one flat mapping of named keys")
    else:
        parsed = {key: value for key, value in loaded.items() if value is not None}
    if len(_PARSED) > 4096:
        _PARSED.clear()        # a bench rewrites thousands of variants -- bound the drawer
    _PARSED[raw] = parsed
    return dict(parsed)


def truthy(value: object) -> bool:
    """-> a YAML-typed flag read tolerantly: `true` the bool, or "true" the word."""
    return value is True or (isinstance(value, str) and value.strip().lower() == "true")


# documentary: the two sections of a document's laws -- `constraints.production`
# (what the agent makes: proven at every checkpoint) and `constraints.behavior`
# (what it does, says or reads: served at every block, never proven); the bare
# `constraints:` key refuses by name -- a document migrates with the product's
# `tools/migrate-sections.py`, never by a tolerant read
SECTIONS = (("constraints.production", "production"), ("constraints.behavior", "behavior"))


def law_lines(document: Document, key: str) -> list[str]:
    """-> the law lines of one section, comments and blank lines dropped. Public: the
    build drives the sections line by line when it must name ONE bad line and keep
    the others."""
    if "constraints" in document.front:
        raise Refusal("constraints-unsectioned",
                      f"{document.name}: a bare `constraints:` key -- a law lives in "
                      "`constraints.production` or `constraints.behavior`; migrate the "
                      "document with tools/migrate-sections.py")
    return [line.strip() for line in str(document.front.get(key, "")).splitlines()
            if line.strip() and not line.strip().startswith("#")]   # a `#` line inside a
    # declarative block is a comment: uncommenting it is how a seed gets armed


def constraints(document: Document) -> tuple[Constraint, ...]:
    """-> the laws this document puts in force, one per line `CODE  what it demands`,
    production first, then behavior -- each carrying its section."""
    found = []
    for key, section in SECTIONS:
        for line in law_lines(document, key):
            match = LAW.match(line)
            if not match:
                raise Refusal("constraint-malformed", f"`{line}` is not `CODE  what it demands`")
            found.append(Constraint(code=match.group(1), text=match.group(2).strip(),
                                    section=section))
    return tuple(found)


def constraint_delta(line: str, section: str) -> tuple[str, str, str, str]:
    """-> (sign, code, text, section) for ONE line of the overlay dialect -- `-CODE`
    removes by code alone (whatever its section), `+CODE  text` or `CODE  text` adds in
    `section`. Strict: a line out of form refuses, here as everywhere."""
    if line.startswith("-"):
        code = line[1:].strip()
        if not code or " " in code:
            raise Refusal("constraint-malformed", f"`{line}` -- a removal is `-CODE`, alone")
        return ("-", code, "", "")
    match = LAW.match(line.removeprefix("+").strip())
    if not match:
        raise Refusal("constraint-malformed", f"`{line}` is not `[+]CODE  what it demands`")
    return ("+", match.group(1), match.group(2).strip(), section)


def constraint_deltas(document: Document) -> list[tuple[str, str, str, str]]:
    """-> (sign, code, text, section) per line of an overlay's sections. The overlay
    dialect; a base document stays strict."""
    return [constraint_delta(line, section)
            for key, section in SECTIONS for line in law_lines(document, key)]


def tool_deltas(document: Document) -> list[tuple[str, str]]:
    """-> (sign, name) per token of an overlay's `tools:` -- same dialect."""
    lines = [one for one in str(document.front.get("tools", "")).splitlines()
             if not one.strip().startswith("#")]
    return [("-", token[1:]) if token.startswith("-") else ("+", token.removeprefix("+"))
            for token in " ".join(lines).split()]


def serve_sections(document: Document) -> tuple[tuple[tuple[str, ...], ...], ...]:
    """-> the ordered SECTIONS of `serve:` -- a section is a PARAGRAPH of the block
    (contiguous lines; a blank line separates), each line its tokens (the nature
    first when declared; a blank inside a token's brackets does not cut it). A bare `SERVE` serves one whole section, every line of
    it; n sections take n bare SERVEs, in the declared order."""
    declared = str(document.front.get("serve", ""))
    sections: list[tuple[tuple[str, ...], ...]] = []
    current: list[tuple[str, ...]] = []
    for line in declared.splitlines():
        if line.strip():
            try:
                current.append(tokens.split_row(line))
            except Refusal as refusal:
                detail = str(refusal).split(" — ", 1)[-1]
                raise Refusal(refusal.code,
                              f"{detail} -- `serve:` of {document.path.name}") from refusal
        elif current:
            sections.append(tuple(current))
            current = []
    if current:
        sections.append(tuple(current))
    return tuple(sections)


def serve_lines(document: Document) -> tuple[tuple[str, ...], ...]:
    """-> every line of every `serve:` section, in order -- what a mount plays whole."""
    return tuple(line for section in serve_sections(document) for line in section)


def overlay_serve_lines(overlay: Document) -> tuple[tuple[str, ...], ...]:
    """-> the `serve:` lines an OVERLAY adds to its base, in order -- a leading `+`
    on a line's first token says the addition and is optional; a leading `-` refuses
    by name: an overlay never removes a reading from its base."""
    lines: list[tuple[str, ...]] = []
    for line in serve_lines(overlay):
        head = line[0]
        if head.startswith("-"):
            raise Refusal("overlay-serve-removal",
                          f"{overlay.path.name}: `{head}` -- an overlay adds readings, "
                          "it never removes one")
        head = head[1:] if head.startswith("+") else head
        lines.append(((head,) + line[1:]) if head else line[1:])
    return tuple(line for line in lines if line)


FORMAT_LINE = re.compile(r"^(\S+)\s+(inline|stdin)\s+(.+)$")


def formats(document: Document) -> tuple[tuple[str, str, str], ...]:
    """-> the OUTPUT formats this document declares: (name, mode, definition) -- the
    MODE is mandatory (the format dictates the transport, the agent never chooses)."""
    found = []
    for line in document.front.get("formats", "").splitlines():
        if not line.strip():
            continue
        match = FORMAT_LINE.match(line.strip())
        if not match:
            raise Refusal("format-malformed",
                          f"`{line.strip()}` is not `name  inline|stdin  definition`")
        found.append((match.group(1), match.group(2), match.group(3).strip()))
    return tuple(found)


def tool_names(document: Document) -> tuple[str, ...]:
    """-> the `tools:` this document proposes -- an unordered SET, unlike `serve:`'s paced rows."""
    lines = [one for one in str(document.front.get("tools", "")).splitlines()
             if not one.strip().startswith("#")]
    return tuple(" ".join(lines).split())


def body_of(text: str) -> str:
    """-> everything after the closing `---` of the front matter -- what a CALL actually serves."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != BORDER:
        return text
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == BORDER), None)
    return "".join(lines[end + 1:]) if end is not None else text


def title(path: Path) -> str:
    """-> what a served document is called. A front matter names it; otherwise its file does."""
    try:
        return read(path).front.get("name", path.stem)
    except Refusal:
        return path.stem


def cycles(document: Document) -> bool | str:
    """-> the frame's CYCLE, said by the value of `cycle:`: True -- the session cycle, exhausted
    it rewinds instead of popping/completing; a TOKEN -- the iterated cycle, a lap per
    element the token's providers render, the frame leaving when they render nothing;
    False -- no cycle."""
    value = document.front.get("cycle")
    if truthy(value):
        return True
    if isinstance(value, str) and value.strip() and value.strip().lower() != "false":
        return value.strip()
    return False


def procedure(document: Document) -> Procedure:
    """-> every instruction the single `proc:` key carries, in the order it writes them.
    A `#`-prefixed line is a comment of pp's own (uncommenting arms it -- the same rule
    as the constraints block); a lone `§` is the SECTION BREAK: fusion never crosses
    it -- it marks the NEXT instruction, it is not an instruction itself."""
    listing = document.front.get("proc", "")
    instructions = []
    pending_barrier = False
    for line in listing.splitlines():
        bare = line.strip()
        if not bare or bare.startswith("#"):
            continue
        if bare == "§":
            pending_barrier = True
            continue
        one = statement(line)
        one.barrier = pending_barrier
        pending_barrier = False
        instructions.append(one)
    if not instructions:
        raise Refusal("procedure-undeclared",
                      f"{document.name} declares no `proc:` in its front matter")
    for one in instructions:
        if one.keyword == "PROVE":
            raise Refusal("prove-retired",
                          f"{document.name}: `PROVE` is no author keyword anymore -- "
                          "declare `prove: auto|true|false` in the front matter and the "
                          "checkpoint plays by itself where productions leave the document")
    return Procedure(instructions=instructions)


def playable(document: Document) -> Procedure:
    """-> the procedure a CALL plays: the declared one -- or, for a document without a
    `proc:`, the IMPLICIT one (the skill is a CALL): one INFER, its served body the
    brief, the work free, the close resumes the caller's flow. ONE home for the rule:
    the runner opens frames with it, the restore rebuilds them with it."""
    if str(document.front.get("proc", "")).strip():
        return procedure(document)
    return Procedure(instructions=[Instruction(keyword="WORK", argument="")])


def statement(line: str) -> Instruction:
    match = STATEMENT.match(line.strip())
    if not match:
        raise Refusal("instruction-malformed",
                      f"`{line.strip()}` is not `KEYWORD [argument] [^ @Doc.field]`")
    keyword, argument = match.group(1), match.group(2) or ""
    guard = f"{match.group(3)}.{match.group(4)}" if match.group(3) else ""
    if keyword not in language.KEYWORDS:
        raise Refusal("unknown-keyword",
                      f"`{keyword}` -- known: {', '.join(sorted(language.KEYWORDS))}")
    if not argument and keyword not in language.BARE:
        raise Refusal("instruction-malformed", f"`{keyword}` needs an argument")
    return Instruction(keyword=keyword, argument=argument, guard=guard)
