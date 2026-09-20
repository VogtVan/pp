#!/usr/bin/env python3
"""DETERMINISTIC keeper of an instance's plans -- the one writer of their structure.

A plan lives as documents under the instance root: `plans/<slug>/PLAN.md`, one
subdirectory and `PHASE.md` per phase, one subdirectory and `BATCH.md` per batch
under its phase -- three levels, always. The NAME is bare -- the identity, what
entries carry and what the caller addresses -- while the FOLDER on disk is
INDEXED, `<n>-<name>`, DERIVED from the position the `item.<n>` keys own; the
script alone renames folders when an order changes. Every document opens on a
YAML front matter that carries ONE entry PER CHILD (`item.<n>: <name>  <status>`,
statuses among todo, doing, done, blocked and redo) and a BODY of titled
SECTIONS -- the kind's own list, in its order (SECTIONS): the agent's prose goes
through `section`, never through an editor. An item exists in three moments:
PREPARED -- one line `- <slug> -- <brief>` in its parent's `Items` section, from
which its entry is derived, no document yet; BORN -- its first section written
creates its folder and its document from that line, the brief as its Context;
DELIVERED -- its statuses DEDUCED from what is written: Expected makes it `doing`,
Delivery makes a batch `done` (its todos all done) and the closing rises to the
phase and the plan, a framing section rewritten on a done node reopens it (`redo`,
the ancestry rises); `done` checks a todo off, `block` says a stop. The plan alone
is born by its own Context. Keys beyond the model (`constraints:`, `serve:`) are the framing's,
written by the engine's writer: every write returns them verbatim.

  pp-plan.py section <address> <Name> [--append]
                                             -> the named section of the body, prose on
                                                stdin (a trailing `-` marks it): replaced,
                                                inserted at its rank when absent, appended
                                                for a log (Decisions, Delivery) or with the
                                                flag; Items derives the entries; the first
                                                write on a prepared item births it
  pp-plan.py done <slug>/<phase>/<batch>/<todo>
                                             -> the todo checked off; a batch closes by its
                                                Delivery, the phase and the plan by the cascade
  pp-plan.py block <address> <reason ...>    -> the node blocked, the reason a dated line of
                                                its Decisions; the next framing section lifts it
  pp-plan.py move <src-address> <dst-parent-address> <index>
                                             -> the node changes parent or rank; folders follow
  pp-plan.py rename <address> <new-name>     -> a phase or a batch takes a new name: the entry,
                                                its Items line, the folder and the model keys
                                                follow; the prose stays the agent's
  pp-plan.py mount <address> [--whole]       -> the node's ::mount chain, printed -- a
                                                prepared item mounts its kind's method ahead;
                                                the node at work whole, its ancestors from
                                                their Target on (--whole: every body whole)
  pp-plan.py constrain <address> [<prefix>] --section production|behavior
                                             -> law TEXTS piped one per line, written under
                                                codes the engine's writer derives; a line that
                                                OPENS on a posed code replaces that law in place
  pp-plan.py constrain <address> --retire <code>
                                             -> the law leaves `constraints`, its code kept
                                                under `retired:` -- a code never returns
  pp-plan.py serve <address> <token ...>     -> ONE `serve:` row on the node's document
  pp-plan.py serve <address> -               -> the whole `serve:` section, rows piped
  pp-plan.py next-move                       -> the held next-move lines, read-only; a line
                                                ends with the vector of the node it names
  pp-plan.py verify                          -> this package's VERIFIER, the engine's call: a
                                                `plan:`/`plan-phase:`/`plan-lot:` vector on stdin, rc 0
                                                when its ADDRESS resolves in the tree (born or
                                                prepared); the depth must fit the family
  pp-plan.py status [<slug>]                 -> the derived progress table, markdown
  pp-plan.py check                           -> the lint: structure, statuses, prose
  pp-plan.py repair                          -> the mechanical findings mended and said --
                                                a node open over children all done closes --
                                                the others said with their gesture

An ADDRESS is bare names -- `memo/core/storage` -- never the numbered folders.
Every mutating call ends by SAYING the plan's next move: a `::push` line the
conductor collects into the NEXT (a `::clear` once the plan is done).

Anything unresolved refuses by name -- exit 2, nothing written: not-an-instance,
path-unknown, section-unknown, section-order, item-line-malformed, item-engaged,
items-open, done-invalid, slug-taken, name-invalid, kind-mismatch, code-unknown,
prose-missing, prose-heading, section-ambiguous, section-kept, frontmatter-malformed, argument-missing, argument-unexpected, verb-unknown.
Writes go through the engine's one write regime: atomic replace. No network, ever.

The conductor plays this skill: an agent reaches it as `./pp <key> -s pp-plan ...`,
and pp runs it with its own interpreter -- what the engine depends on, it may depend on.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
import contextlib
from pathlib import Path

import yaml

STATUSES = ("todo", "doing", "done", "blocked", "redo")
ENGAGED = ("doing", "redo", "blocked")   # started work, whatever its kind --
                                         # what a closed ancestor would hide
DOCS = {"plan": "PLAN.md", "phase": "PHASE.md", "batch": "BATCH.md"}
MODEL_KEYS = ("slug", "kind", "plan", "phase", "status", "created")
ITEM = re.compile(r"^item\.(\d+)$")   # the ONE child grammar, whatever the kind
FOREIGN = "_foreign"   # internal vehicle only -- never a key written to a document
WRITING = ("section", "done", "block", "move", "rename", "constrain", "serve")
                                         # the verbs that WRITE: they play under the plan's lock
KINDS = ("plan", "phase", "batch")
SECTIONS = {   # a kind's sections, in the order of the document
    "plan": ("Context", "Survey", "Target", "Protocol", "Expected", "Arbitrations",
             "Items", "Decisions"),
    "phase": ("Context", "Ground", "Target", "Expected", "Arbitrations", "Items", "Decisions"),
    "batch": ("Context", "Ground", "Target", "Expected", "Tests", "Arbitrations", "Items",
              "Decisions", "Delivery"),
}
REQUIRED = {   # the sections a later one waits for -- the order, guided
    "plan": ("Context", "Target", "Expected", "Items"),
    "phase": ("Context", "Ground", "Target", "Expected", "Items"),
    "batch": ("Context", "Ground", "Target", "Expected", "Tests", "Items"),
}
LOGS = ("Decisions", "Delivery")         # appended, never replaced
FRAMING = ("Ground", "Target", "Expected", "Tests", "Arbitrations", "Items")   # rewritten on a
                                         # done node, a framing section REOPENS it
ITEM_LINE = re.compile(r"^- ([a-z0-9][a-z0-9-]*) -- (.+?)\s*$")   # one prepared item
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")     # a node's name: kebab-case, the slugs' own grammar
LAW = re.compile(r"^\s\s([A-Z][A-Z0-9]*?[0-9]+)\s\s(.*)$")   # `  KX1  text` -- a posed law, the
                                                            # engine writer's own grammar
USAGE = {
    "section": "section <address> <Name> [--append]   (the prose on stdin, `-` marks it) | "
               "section <address> <Name> --remove[=<n>]   (no stdin)",
    "done": "done <slug>/<phase>/<batch>/<todo>",
    "block": "block <address> <reason ...>",
    "move": "move <src-address> <dst-parent-address> <index>",
    "rename": "rename <address> <new-name>",
    "mount": "mount <address> [--whole]   (--whole: every ancestor's body whole too)",
    "constrain": "constrain <address> [<prefix>] --section production|behavior   (laws on stdin; "
                 "a line opening on a posed code replaces it) | constrain <address> --retire <code>",
    "serve": "serve <address> <token ...> | serve <address> -   (the rows on stdin) -- a token is "
             "DOC, 'DOC[start..end]' (quoted here, bare on stdin) or, as a last resort, DOC[x-y,...]",
    "next-move": "next-move",
    "verify": "verify   (the vector on stdin -- the engine's call, never the agent's)",
    "status": "status [<slug>]",
    "check": "check",
    "repair": "repair",
}
ARITY = {"section": (2, 2), "done": (1, 1), "block": (2, None), "move": (3, 3), "rename": (2, 2),
         "mount": (1, 1),
         "constrain": (1, 4), "serve": (2, None), "next-move": (0, 0), "verify": (0, 0), "status": (0, 1),
         "check": (0, 0), "repair": (0, 0)}


def fail(code: str, detail: str) -> None:
    """Refuses aloud: the named code, the way back, exit 2 -- nothing was written."""
    sys.stderr.write(f"pp-plan: {code} -- {detail}\n")
    raise SystemExit(2)


def home() -> Path:
    """-> the instance this vendored copy belongs to -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import home as walk                       # noqa: E402 -- the bootstrap
    found = walk(__file__)
    if found is None:
        fail("not-an-instance", "no `.sys/instance.yaml` above this script; nothing to keep")
    return found



def read(path: Path) -> tuple[dict, str]:
    """-> (front matter mapping, body text) of a plan document.

    The script trusts only what it wrote: a document that no longer opens on a
    well-formed front matter refuses `frontmatter-malformed` -- the named signal
    that a hand edited what the script alone owns.

    A document may carry keys the model does not own -- `constraints:`,
    `serve:` -- a plan document IS a proc. Those foreign segments travel
    with the mapping, raw text in original order, so the next write gives
    them back verbatim: the script preserves what it does not possess."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        fail("frontmatter-malformed", f"{path} does not open on `---`")
    end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), None)
    if end is None:
        fail("frontmatter-malformed", f"{path} never closes its front matter")
    try:
        front = yaml.safe_load("".join(lines[1:end])) or {}
    except yaml.YAMLError as wrong:
        fail("frontmatter-malformed", f"{path}: {str(wrong).splitlines()[0]}")
    if not isinstance(front, dict):
        fail("frontmatter-malformed", f"{path}: the front matter is not a mapping")
    # raw capture only after the successful parse -- malformed still refuses first
    foreign, keep = [], False
    for line in lines[1:end]:
        if line[:1] not in (" ", "\t") and ":" in line:
            key = line.split(":", 1)[0].strip()
            keep = key not in MODEL_KEYS and not ITEM.match(key)
        if keep:
            foreign.append(line)
    front[FOREIGN] = "".join(foreign)
    return front, "".join(lines[end + 1:])


def emit(front: dict, body: str) -> str:
    """-> the document text, front matter in CANONICAL form -- the model's keys
    in one fixed order, then the foreign segments verbatim, then one `item.<n>`
    entry per child, renumbered from their order. The canonical emit keeps the
    round trip safe both ways: what the model owns is re-derived on every write
    so no hand formatting can drift it, and what the model does not own comes
    back untouched -- emitting twice yields the same text."""
    out = ["---\n"]
    for key in MODEL_KEYS:
        if key in front:
            out.append(f"{key}: {front[key]}\n")
    out.append(front.get(FOREIGN, ""))
    for position, (name, status) in enumerate(children(front), 1):
        out.append(f"item.{position}: {name}  {status}\n")
    out.append("---\n")
    return "".join(out) + body


def regime():
    """-> the engine's ONE write regime (`conductor.record`): lock and atomic
    replace, carried for every shared record of the product."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                # noqa: E402 -- the bootstrap
    return core(__file__).record


@contextlib.contextmanager
def guarded(root: Path, slug: str):
    """The PLAN's critical section: one lock per plan, held from a verb's first read
    to its last write. A verb walks several documents -- the node and its ancestors --
    and modifies each between a read and a write; without this span two sessions of
    one member lose an update to each other.

    documentary: the lock sits BESIDE the plan's directory (`plans/<slug>.lock`), never
    inside it: the regime creates the parent of what it locks, and a lock on the root
    document would bring the plan's own directory into being before `new` could refuse
    a slug already taken. The granularity is the one a verb works at -- never less.
    Readers take nothing: the atomic replace keeps every read consistent."""
    with regime().held(root / "plans" / slug):
        yield


def write(path: Path, front: dict, body: str) -> None:
    # the engine's one write regime: a crash never leaves a half document. The
    # LOCK is not taken here: a verb walks several documents and modifies each
    # between a read and this write -- closing that critical section is its own
    # batch, said at `le-rebalayage / l-ecriture-atomique`
    regime().replace(path, emit(front, body))


def children(front: dict) -> list[tuple[str, str]]:
    """-> the item entries of a front matter, in document order: (name, status).

    One reader for the three kinds -- whether the entries say phases, batches
    or todos, an `item.<n>` key holds `<name>  <status>` and nothing else."""
    found = []
    for key, value in front.items():
        if isinstance(key, str) and ITEM.match(key):
            parts = str(value).split(None, 1)
            found.append((parts[0], parts[1] if len(parts) > 1 else ""))
    return found


def set_child(front: dict, name: str, status: str) -> None:
    """Rewrites ONE item entry's status in place -- the name is untouched."""
    for key, value in list(front.items()):
        if isinstance(key, str) and ITEM.match(key) and str(value).split(None, 1)[0] == name:
            front[key] = f"{name}  {status}"


def add_child(front: dict, name: str, status: str) -> None:
    # the key's number is derived, never chosen: position = existing entries + 1
    front[f"item.{len(children(front)) + 1}"] = f"{name}  {status}"


BLUEPRINT = ("a plan document is a BLUEPRINT, never a history manual: every framing and "
             "every reframing writes the state TRUE at the moment it speaks, and of the "
             "history it keeps the reasons and the justifications alone, one dated line")


def free_code(root: Path, slug: str) -> str:
    """-> a constraint code free across the WHOLE instance, for a plan being born:
    `K` and the initials of the slug's words, numbered past everything declared.

    documentary: a template cannot carry a fixed code -- two plans would then declare
    the same one, and the build would warn for the life of the instance; the code is
    derived at birth, exactly as a framing derives the codes it writes later."""
    taken = set()
    for document in root.rglob("*.md"):
        if ".git" in document.parts:
            continue
        try:
            text = document.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            found = re.match(r"^\s{2}([A-Z][A-Z0-9]*\d+)\s\s", line)
            if found:
                taken.add(found.group(1))
    words = [one for one in re.split(r"[-_.]", slug) if one and not one.isdigit()]
    stem = "K" + "".join(one[0].upper() for one in words)[:3]
    rank = max((int(re.fullmatch(rf"{stem}(\d+)", one).group(1))
                for one in taken if re.fullmatch(rf"{stem}(\d+)", one)), default=0)
    return f"{stem}{rank + 1}"


def template(kind: str) -> str:
    """-> the template of `kind`. Its file is `_`-prefixed: a template CARRIES laws --
    the plan's blueprint rule is one -- and a working file is never walked by the
    registry, so a placeholder never reaches the build as a malformed constraint."""
    return (Path(__file__).resolve().parent / "templates" / f"_{DOCS[kind]}").read_text(
        encoding="utf-8")


def render(kind: str, prose: str, **names: str) -> str:
    # plain replace, never str.format: prose and slugs may carry braces
    text = template(kind)
    names["created"] = datetime.now(timezone.utc).date().isoformat()
    names["prose"] = prose.strip()
    for key, value in names.items():
        text = text.replace("{" + key + "}", value)
    return text


LEVEL_TITLE = re.compile(r"^# (PLAN|PHASE|BATCH)\b")   # a title the level owns; any other is free


def title_of(front: dict) -> str:
    """-> the title line the kind's template gives this front matter."""
    body = template(front["kind"]).split("\n---\n", 1)[1]
    line = next(one for one in body.splitlines() if one.startswith("# "))
    for key in ("slug", "plan", "phase"):
        line = line.replace("{" + key + "}", str(front.get(key, "")))
    return line


def title_line(body: str) -> str | None:
    """-> the body's title: its first `# ` line before the first section, None when absent."""
    for line in body.splitlines():
        if line.startswith("## "):
            return None
        if line.startswith("# "):
            return line
    return None


def titled(front: dict, body: str) -> str:
    """-> the body carrying the title its front matter gives: a level title set, a missing one
    inserted, a free title kept -- every other line byte for byte."""
    lines = body.splitlines(keepends=True)
    for at, line in enumerate(lines):
        if line.startswith("## "):
            break
        if line.startswith("# "):
            if LEVEL_TITLE.match(line):
                lines[at] = title_of(front) + ("\n" if line.endswith("\n") else "")
            return "".join(lines)
    lead = len(body) - len(body.lstrip("\n"))
    return body[:lead] + title_of(front) + "\n\n" + body[lead:]


def doc_of(root: Path, *segments: str) -> Path:
    """-> the document a node path addresses: plans/<slug>[/<phase>[/<batch>]].

    The caller addresses by BARE names; the folders on disk are INDEXED
    (`<n>-<name>`). The path is DERIVED parent by parent from the item
    entries -- the tree shows the order the front matters own."""
    kind = ("plan", "phase", "batch")[len(segments) - 1]
    path = root / "plans" / segments[0]
    for depth, name in enumerate(segments[1:], 1):
        parent = path / DOCS[("plan", "phase")[depth - 1]]
        if not parent.is_file():
            fail("path-unknown", f"{'/'.join(segments[:depth])} has no document")
        front, _ = read(parent)
        position = next((i for i, (child, _) in enumerate(children(front), 1)
                         if child == name), None)
        if position is None:
            if re.match(r"^\d+-", name):
                bare = "/".join(segments[:depth]) + "/" + name.split("-", 1)[1]
                fail("path-unknown", f"`{name}` is a FOLDER -- address the node by its bare name: {bare}")
            fail("path-unknown", f"{'/'.join(segments[:depth + 1])} has no entry -- prepare it in "
                                 f"its parent's Items first (`- {name} -- <brief>`)")
        path = path / f"{position}-{name}"
    return path / DOCS[kind]


def new(root: Path, slug: str, prose: str) -> Path:
    """Births a plan: its directory and its PLAN.md, prose aboard, no phase yet."""
    spot = root / "plans" / slug
    if spot.exists():
        fail("slug-taken", f"plans/{slug} already stands -- a slug is born once")
    spot.mkdir(parents=True)
    path = spot / DOCS["plan"]
    path.write_text(render("plan", prose, slug=slug,
                           blueprint=f"{free_code(root, slug)}  {BLUEPRINT}"), encoding="utf-8")
    return path


FAMILIES = {"plan": 1, "plan-phase": 2, "plan-lot": 3}   # the families this package declares -> the depth of their address


def verify(root: Path, vector: str) -> None:
    """This package's VERIFIER, the engine's call at every entry and service of the bus:
    a `plan:`/`plan-phase:`/`plan-lot:` vector is valid when its slug is an ADDRESS of the tree
    -- the same bare names every verb takes -- that RESOLVES: a plan born, a phase or a
    batch born or PREPARED (an entry of its parent's Items, no document yet). The depth
    must fit the family (`address-depth`); a family this package does not declare is not
    its to judge (`family-foreign`); an address that resolves nowhere refuses with the
    resolver's own reason (`path-unknown`). READ-ONLY, no lock: exit 2 says no.

    documentary: the frontier's next lot is often prepared, not born -- a frustration of a
    plan's work may point at it, so the entry is the node, whatever its birth."""
    prefix, _, address = vector.strip().partition(":")
    depth = FAMILIES.get(prefix)
    if depth is None:
        fail("family-foreign", f"`{prefix}:` is not a family plan declares "
                               f"({', '.join(FAMILIES)}); its owner verifies it")
    segments = address.split("/") if address else []
    if len(segments) != depth or not all(segments):
        shape = "/".join(("<slug>", "<phase>", "<batch>")[:depth])
        fail("address-depth", f"`{vector}` -- a {prefix} is addressed by {depth} bare name(s): {shape}")
    if depth == 1:
        if not (root / "plans" / segments[0] / DOCS["plan"]).is_file():
            fail("path-unknown", f"plans/{segments[0]} has no PLAN.md -- no plan of that name is born")
        return
    doc_of(root, *segments)                 # resolves the entry, or refuses path-unknown by name


def standing(root: Path, segments: list[str]) -> Path:
    """-> the node's document, which must be BORN: a prepared item (an entry, no
    document) refuses by name -- its first section births it."""
    path = doc_of(root, *segments)
    if not path.is_file():
        fail("path-unknown", f"{'/'.join(segments)} is prepared, not born -- its first section "
                             "births it; a status, a law or a row waits a born node")
    return path


def split_sections(body: str) -> list[tuple[str | None, str]]:
    """-> the body cut at its `## ` headings: [(name or None, text)] -- the first
    chunk, unnamed, is the title and whatever precedes the first section."""
    parts: list[tuple[str | None, str]] = []
    name, buf = None, []
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            parts.append((name, "".join(buf)))
            name, buf = line[3:].strip(), []
        else:
            buf.append(line)
    parts.append((name, "".join(buf)))
    return parts


def join_sections(parts: list[tuple[str | None, str]]) -> str:
    return "".join(("" if name is None else f"## {name}\n") + text for name, text in parts)


def section_text(body: str, name: str) -> str | None:
    """-> the text under `## <name>`, None when the heading is absent."""
    for found, text in split_sections(body):
        if found == name:
            return text
    return None


def consigne(kind: str, name: str) -> str:
    """-> what the template says under a section -- the guidance an unwritten
    section still carries; empty for a section the template lacks."""
    body = template(kind).split("\n---\n", 1)[1]
    return (section_text(body, name) or "").strip()


def is_written(kind: str, name: str, body: str) -> bool:
    """A section is WRITTEN once its text is neither absent, empty, nor the
    template's own guidance."""
    text = section_text(body, name)
    return text is not None and text.strip() != "" and text.strip() != consigne(kind, name)


def item_lines(text: str) -> list[tuple[str, str]]:
    """-> the (slug, brief) pairs an Items text declares, in order -- a line that is
    neither blank nor an item refuses by name; a slug twice refuses."""
    found: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = ITEM_LINE.match(line)
        if match is None:
            fail("item-line-malformed", f"`{line.strip()[:60]}` -- an item is one line `- <slug> -- <brief>`")
        slug, brief = match.group(1), match.group(2).strip()
        if slug in [one for one, _ in found]:
            fail("slug-taken", f"`{slug}` twice in Items -- an item is prepared once under its parent")
        found.append((slug, brief))
    return found


def prepared_brief(root: Path, segments: list[str]) -> str:
    """-> the brief the parent's Items line prepared for this item -- its Context
    at birth; the bare name when no line stands (an entry born another way)."""
    kind = KINDS[len(segments) - 2]
    _, body = read(doc_of(root, *segments[:-1]))
    if not is_written(kind, "Items", body):
        return segments[-1]
    for slug, brief in item_lines(section_text(body, "Items") or ""):
        if slug == segments[-1]:
            return brief
    return segments[-1]


def birth(root: Path, segments: list[str], brief: str) -> Path:
    """Births a PREPARED phase or batch: the entry stands at the parent, the folder
    is born at the entry's position, the document on the template with the
    brief as its Context -- the first section written on a prepared item is
    what calls this."""
    path = doc_of(root, *segments)            # refuses path-unknown without the entry
    kind = KINDS[len(segments) - 1]
    names = {"slug": segments[-1], "plan": segments[0]}
    if kind == "batch":
        names["phase"] = segments[1]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(kind, brief, **names), encoding="utf-8")
    return path


def derive_items(front: dict, lines: list[tuple[str, str]], kind: str, home: Path) -> None:
    """The Items section is the SOURCE of the child block: the entries follow the
    lines -- a new slug enters `todo`, a known one keeps its status and takes the
    line's rank, a slug gone leaves only while it is still `todo` and, under a
    plan or a phase, unborn (item-engaged otherwise). Nothing is written here:
    the caller writes the document once, the front matter with the section."""
    existing = dict(children(front))
    kept = {one for one, _ in lines}
    for slug, status in existing.items():
        if slug in kept:
            continue
        born = kind != "batch" and any(
            d.is_dir() and re.fullmatch(rf"\d+-{re.escape(slug)}", d.name) for d in home.iterdir())
        if status != "todo" or born:
            fail("item-engaged", f"`{slug}` is {status}{' and born' if born else ''} -- an item "
                                 "leaves Items only while it is todo and unborn")
    for key in [k for k in front if isinstance(k, str) and ITEM.match(k)]:
        del front[key]
    for position, (slug, _) in enumerate(lines, 1):
        front[f"item.{position}"] = f"{slug}  {existing.get(slug, 'todo')}"


def write_section(root: Path, segments: list[str], name: str, prose: str,
                  append: bool = False) -> tuple[Path, list[str], list[str]]:
    """Writes ONE named section of a node's body -- the agent's prose through the
    script, never an editor. The body is titled sections in the kind's order:
    a standing section has its content REPLACED; an absent one is INSERTED at
    its rank (a name beyond the kind's list lands at the tail); a LOG (Decisions,
    Delivery) or the flag APPENDS. The order GUIDES: a required section ranked
    before must be written first (section-order). The first write on a PREPARED
    item births it from its line; a plan is born by its Context. Items derives
    the child entries. The STATUS is deduced from the intention: Expected written
    on a node not yet framed makes it `doing`; Delivery written on a batch whose
    todos are all done makes it `done` and the closing rises; a framing section
    rewritten on a `done` node reopens it first (`redo`, the ancestry rises); a
    blocked node is lifted by its next framing section or its Delivery.
    -> (path, what the write did, the status lines the console says)"""
    if not prose.strip():
        fail("prose-missing", "a section is written WITH its prose -- pipe it on stdin")
    heading = next((line for line in prose.splitlines() if line.startswith("## ")), None)
    if heading is not None:
        # the reader cuts the body at every `## ` line, a code block included
        fail("prose-heading", f"`{heading.strip()[:60]}` would open a section of its own -- a "
                              "subtitle inside a section is written `###`")
    if name == "Todos":
        fail("section-unknown", "Todos is the Items section now -- `- <slug> -- <text>` lines")
    if not 1 <= len(segments) <= 3:
        fail("path-unknown", f"{'/'.join(segments)} -- an address is <slug>[/<phase>[/<batch>]]")
    kind = KINDS[len(segments) - 1]
    order = SECTIONS[kind]
    path = doc_of(root, *segments)
    said: list[str] = []
    if not path.is_file():
        if len(segments) == 1:
            if name != "Context":
                fail("section-order", f"{segments[0]} is not born -- write its Context first, the plan's brief")
            new(root, segments[0], prose)
            return path, ["born"], []
        if name not in ("Context", "Ground"):
            fail("section-order", f"{'/'.join(segments)} is prepared, not framed -- its Ground first")
        birth(root, segments, prepared_brief(root, segments))
        said.append("born")
    front, body = read(path)
    if name in order and name not in LOGS:
        for before in order[:order.index(name)]:
            if before in REQUIRED[kind] and not is_written(kind, before, body):
                fail("section-order", f"{'/'.join(segments)}: write {before} before {name} -- "
                                      f"the order of a {kind} is {' > '.join(order)}")
    if name == "Delivery" and front.get("status") == "todo":
        fail("section-order", f"{'/'.join(segments)} is not framed -- its Expected first")
    if name == "Delivery":
        open_items = [child for child, cstatus in children(front) if cstatus != "done"]
        if open_items:
            fail("items-open", f"{'/'.join(segments)} still carries `{'`, `'.join(open_items)}` -- "
                               "a batch delivers when its todos are done, or once they leave Items")
    moves: list[str] = []
    if name in FRAMING and front.get("status") == "done":
        # the rework opens on the node's own history: the reopen walk, then the write
        if len(segments) == 1:
            set_status(root, segments, "doing")
        else:
            reopen(root, segments)
        moves.append(f"pp-plan: {'/'.join(segments)} -> {'doing' if len(segments) == 1 else 'redo'} -- the rework is open")
        front, body = read(path)
    lines = item_lines(prose) if name == "Items" else None
    if lines is not None:
        derive_items(front, lines, kind, path.parent)
    parts = split_sections(body)
    names = [one for one, _ in parts]
    block = "\n" + prose.strip() + "\n\n"
    if name in names:
        at = names.index(name)
        if (name in LOGS or append) and is_written(kind, name, body):
            parts[at] = (name, parts[at][1].rstrip("\n") + "\n\n" + prose.strip() + "\n\n")
            said.append("appended")
        else:
            parts[at] = (name, block)
            said.append("replaced")
    else:
        at = len(parts)
        if name in order:
            rank = order.index(name)
            for i, (one, _) in enumerate(parts):
                if one is not None and one in order and order.index(one) > rank:
                    at = i
                    break
        parts.insert(at, (name, block))
        said.append("inserted")
    write(path, front, join_sections(parts))
    if lines is not None and kind != "batch":
        reindex(path.parent, front)
    status = front.get("status")
    if name == "Expected" and status in ("todo", "blocked"):
        set_status(root, segments, "doing")
        moves.append(f"pp-plan: {'/'.join(segments)} -> doing")
    elif name in FRAMING and status == "blocked":
        lifted = "doing" if is_written(kind, "Expected", join_sections(parts)) else "todo"
        set_status(root, segments, lifted)
        moves.append(f"pp-plan: {'/'.join(segments)} -> {lifted} -- the block is lifted")
    elif name == "Delivery" and kind == "batch" and status != "done":
        closed = set_status(root, segments, "done")
        moves.append(f"pp-plan: {'/'.join(segments)} -> done"
                     + (f" -- closes {', '.join(closed)}" if closed else ""))
    return path, said, moves


def remove_section(root: Path, segments: list[str], name: str, nth: int | None) -> tuple[Path, str]:
    """Removes ONE occurrence of a section from a born node's body -- its heading and its
    text, nothing else. The call names the occurrence: a name standing several times
    without a rank refuses, listing each; a section of the kind's list standing once is
    kept -- it is rewritten, a log is never erased. No status moves.
    -> (path, what was removed)"""
    if not 1 <= len(segments) <= 3:
        fail("path-unknown", f"{'/'.join(segments)} -- an address is <slug>[/<phase>[/<batch>]]")
    path = standing(root, segments)
    front, body = read(path)
    parts = split_sections(body)
    at = [i for i, (one, _) in enumerate(parts) if one == name]
    where = "/".join(segments)
    if not at:
        fail("section-unknown", f"`{name}` stands nowhere in {where}")
    if nth is None and len(at) > 1:
        listed = " · ".join(f"{rank}: {len(parts[i][1].strip())} c, "
                            f"`{(parts[i][1].strip().splitlines() or [''])[0][:50]}`"
                            for rank, i in enumerate(at, 1))
        fail("section-ambiguous", f"`{name}` stands {len(at)} times in {where} -- {listed} -- "
                                  f"name the one to remove: --remove=<n>")
    rank = nth or 1
    if rank > len(at):
        fail("section-unknown", f"`{name}` stands {len(at)} time(s) in {where} -- no occurrence {rank}")
    if name in SECTIONS[front["kind"]] and len(at) == 1:
        fail("section-kept", f"`{name}` is a section of a {front['kind']} and stands once -- rewrite it "
                             "by `section`; a log is never erased")
    removed = parts.pop(at[rank - 1])
    write(path, front, join_sections(parts))
    return path, f"{name} ({rank} of {len(at)}, {len(removed[1].strip())} c)"


def done(root: Path, segments: list[str]) -> None:
    """Checks a todo off -- the one status a verb still moves, as the work lands. A
    node closes by its work alone: a batch by its Delivery, the phase and the plan by
    the cascade -- `done` on a node refuses by name."""
    if len(segments) != 4:
        fail("done-invalid", f"{'/'.join(segments)} -- a node closes by its work (Delivery for a "
                             "batch, the cascade above); `done` checks a todo off: "
                             "<slug>/<phase>/<batch>/<todo>")
    set_status(root, segments, "done")


def block(root: Path, segments: list[str], reason: str) -> None:
    """Says a stop: the node is `blocked` and the reason lands as a dated line of its
    Decisions -- the next framing section written, or its Delivery, lifts it."""
    if not 1 <= len(segments) <= 3:
        fail("path-unknown", f"{'/'.join(segments)} -- a node blocks: <slug>[/<phase>[/<batch>]]")
    standing(root, segments)
    set_status(root, segments, "blocked")
    stamp = datetime.now(timezone.utc).date().isoformat()
    write_section(root, segments, "Decisions", f"- {stamp} : blocked -- {' '.join(reason.split())}")


def _splice_line(path: Path, hit, replacement: str) -> bool:
    """The SURGICAL point mutation -- the sections' base doctrine re-expressed
    here without an import (the skills stay self-carried; the duplicated motif
    is a consigned debt): the ONE line `hit` matches is replaced, every other
    byte of the document stays exactly as it was."""
    lines = path.read_text(encoding="utf-8").splitlines()
    for at, line in enumerate(lines):
        if hit(line):
            lines[at] = replacement
            regime().replace(path, "\n".join(lines) + "\n")
            return True
    return False


def _splice_child(path: Path, name: str, status: str) -> bool:
    """-> the parent's `item.<n>` line for `name` moved surgically -- the child
    block's other entries never travel through a re-emit."""
    stamp = re.compile(rf"^item\.(\d+): {re.escape(name)}  ")
    hit = lambda line: stamp.match(line) is not None   # noqa: E731
    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines:
        match = stamp.match(line)
        if match:
            return _splice_line(path, hit, f"item.{match.group(1)}: {name}  {status}")
    return False


def set_status(root: Path, segments: list[str], status: str) -> list[str]:
    """One call, both truths: the node's own `status:` AND its line in the
    parent's child block move together -- the check confronts them, this call
    is why they never diverge. A node's `done` then RISES: every ancestor whose
    children are all `done` closes in the same call (a delivered batch closes
    its phase, a delivered phase its plan) -- the closing is the script's, never
    the agent's bookkeeping; a todo's `done` moves its line alone, the batch
    delivers by its log. Internal since the statuses are deduced: no console verb
    moves one but `done` (a todo) and `block`. -> the ancestors closed, deepest first."""
    if status not in STATUSES or status == "redo":
        # redo is real but not settable: the guarded reopen call alone reaches it
        fail("status-invalid", f"`{status}` -- statuses are {', '.join(s for s in STATUSES if s != 'redo')}; `redo` comes by a framing section rewritten on a done node")
    if not 1 <= len(segments) <= 4:
        fail("path-unknown", f"{'/'.join(segments)} -- a path is <slug>[/<phase>[/<batch>[/<todo>]]]")
    if len(segments) == 4:
        # four segments name a todo -- the depth says the kind, never the spelling
        path = doc_of(root, *segments[:-1])
        if not path.is_file():
            fail("path-unknown", f"{'/'.join(segments)} names no todo")
        front, _ = read(path)
        if segments[-1] not in [c[0] for c in children(front)]:
            fail("path-unknown", f"{segments[-1]} is not among {'/'.join(segments[:-1])}'s todos")
        _splice_child(path, segments[-1], status)   # surgical: the one line moves
        return []                        # a todo closes nothing above: the batch delivers by its log
    path = standing(root, segments)
    read(path)                       # the guards still judge a malformed document
    _splice_line(path, lambda line: line.startswith("status:"), f"status: {status}")
    if len(segments) > 1:            # d6: the parent's line follows in the same call
        parent_doc = doc_of(root, *segments[:-1])
        read(parent_doc)
        _splice_child(parent_doc, segments[-1], status)
    return _cascade(root, segments[:-1], status)


def _cascade(root: Path, parent: list[str], status: str) -> list[str]:
    """The closing rises. From the parent of the node just moved, and only for
    a `done`: a parent whose children are ALL `done` closes -- its `status:` by
    splice, its own line at the grandparent by splice -- and the walk goes on
    one level up, until the plan or the first level that keeps an open child
    (`todo`, `doing`, `blocked` or `redo` alike). A parent already `done`
    closes nothing more. `reopen` is the same walk downward.
    -> the paths closed, deepest first -- what the console says."""
    closed: list[str] = []
    while status == "done" and parent:
        doc = doc_of(root, *parent)
        front, _ = read(doc)
        if front.get("status") == "done" or any(s != "done" for _, s in children(front)):
            break
        _splice_line(doc, lambda line: line.startswith("status:"), "status: done")
        if len(parent) > 1:
            _splice_child(doc_of(root, *parent[:-1]), parent[-1], "done")
        closed.append("/".join(parent))
        parent = parent[:-1]
    return closed


def reindex(parent_dir: Path, front: dict) -> None:
    """Renames the child folders to their DERIVED names (`<position>-<name>`) --
    two phases, so a position swap never collides on its way through."""
    moves = {}
    for position, (name, _) in enumerate(children(front), 1):
        current = next((d for d in parent_dir.iterdir() if d.is_dir()
                        and re.fullmatch(rf"\d+-{re.escape(name)}", d.name)), None)
        wanted = parent_dir / f"{position}-{name}"
        if current is not None and current != wanted:
            moves[current] = wanted
    parked = {}
    for spot, wanted in moves.items():
        stop = parent_dir / f".tmp-{spot.name}"
        spot.rename(stop)
        parked[stop] = wanted
    for stop, wanted in parked.items():
        stop.rename(wanted)


def items_follow(front: dict, body: str, kind: str, briefs: dict[str, str]) -> str:
    """-> the body with its Items section rebuilt on the ENTRIES -- the source of the
    entries must say what the entries say after a move: one line per child, its
    brief kept from the standing line, or given, or the bare name; an unwritten
    Items stays as it is."""
    if not is_written(kind, "Items", body):
        return body
    known = dict(item_lines(section_text(body, "Items") or ""))
    lines = "\n".join(f"- {slug} -- {known.get(slug) or briefs.get(slug) or slug}"
                       for slug, _ in children(front))
    parts = split_sections(body)
    return join_sections([(name, "\n" + lines + "\n\n" if name == "Items" else text)
                          for name, text in parts])


def move(root: Path, src: list[str], dst: list[str], index: str) -> list[str]:
    """Transfers a phase or a batch to a target parent at an index -- or
    reorders it inside its own parent. The entry leaves, the entry is written at
    the index, both parents renumber, the folders follow their derived names,
    and the moved documents' model keys say their new home; every refusal
    fires BEFORE anything is written. The subtree's prose stays the agent's.

    -> the plans whose next move must be re-announced."""
    if len(src) not in (2, 3):
        fail("kind-mismatch", "a plan does not move -- a phase or a batch does")
    if len(dst) != len(src) - 1:
        fail("kind-mismatch", "a phase lands in a plan, a batch in a phase")
    name = src[-1]
    src_doc = standing(root, src)
    src_parent_doc = doc_of(root, *src[:-1])
    try:
        dst_parent_doc = doc_of(root, *dst)
    except SystemExit:
        fail("target-unknown", f"{'/'.join(dst)} has no document to receive `{name}`")
    if not dst_parent_doc.is_file():
        fail("target-unknown", f"{'/'.join(dst)} has no document to receive `{name}`")
    same_parent = src_parent_doc == dst_parent_doc
    src_front, src_body = read(src_parent_doc)
    dst_front, dst_body = (src_front, src_body) if same_parent else read(dst_parent_doc)
    kids = children(src_front)
    status = next(s for child, s in kids if child == name)
    landing = [c for c in children(dst_front) if not (same_parent and c[0] == name)]
    if any(child == name for child, _ in landing):
        fail("slug-taken", f"{'/'.join(dst)} already holds `{name}`")
    if not index.isdigit() or not 1 <= int(index) <= len(landing) + 1:
        fail("index-invalid", f"`{index}` -- the landing rank is 1..{len(landing) + 1}")
    landing.insert(int(index) - 1, (name, status))

    # every guard passed -- the effect starts here, model keys first
    moved_front, moved_body = read(src_doc)
    moved_front["plan"] = dst[0]
    if len(src) == 3:
        moved_front["phase"] = dst[1]
    write(src_doc, moved_front, titled(moved_front, moved_body))
    if len(src) == 2:
        for batch_doc in src_doc.parent.glob(f"*/{DOCS['batch']}"):
            bfront, bbody = read(batch_doc)
            bfront["plan"] = dst[0]
            write(batch_doc, bfront, titled(bfront, bbody))

    def rewrite(front: dict, rebuilt: list[tuple[str, str]]) -> None:
        for key in [k for k in front if isinstance(k, str) and ITEM.match(k)]:
            del front[key]
        for position, (child, child_status) in enumerate(rebuilt, 1):
            front[f"item.{position}"] = f"{child}  {child_status}"

    src_kind = KINDS[len(src) - 2]
    carried = dict(item_lines(section_text(src_body, "Items") or "")).get(name, "") \
        if is_written(src_kind, "Items", src_body) else ""
    if same_parent:
        rewrite(src_front, landing)
        write(src_parent_doc, src_front, items_follow(src_front, src_body, src_kind, {}))
    else:
        rewrite(src_front, [c for c in kids if c[0] != name])
        rewrite(dst_front, landing)
        write(src_parent_doc, src_front, items_follow(src_front, src_body, src_kind, {}))
        write(dst_parent_doc, dst_front, items_follow(dst_front, dst_body, src_kind, {name: carried}))
        # parked at rank 0 -- a rank no entry owns -- until the reindex derives its place
        src_doc.parent.rename(dst_parent_doc.parent / f"0-{name}")
    reindex(src_parent_doc.parent, src_front)
    if not same_parent:
        reindex(dst_parent_doc.parent, dst_front)
    return [src[0]] if same_parent or src[0] == dst[0] else [src[0], dst[0]]


def rename(root: Path, segments: list[str], new: str) -> None:
    """Gives a phase or a batch a new NAME -- the identity every entry, folder and
    model key carries: the parent's entry at its rank and its Items line, the
    document's `slug:`, the `phase:` of the batches under a phase, the derived
    folder -- in one call, every refusal BEFORE the first write. A plan keeps the
    name it was born under (its folder, every `plan:` key and the bus's vectors
    say it); a todo is a line of Items and renames there. What the prose says of
    the old name -- the bodies, the threads -- stays the agent's: the call says so."""
    if len(segments) not in (2, 3):
        fail("kind-mismatch", "a phase or a batch renames -- a plan keeps the name it was born "
                              "under, a todo renames by its parent's Items")
    if not NAME.fullmatch(new):
        fail("name-invalid", f"`{new}` -- a name is kebab-case, the slugs' own grammar")
    old = segments[-1]
    if new == old:
        fail("name-invalid", f"`{new}` is the name it already carries")
    path = doc_of(root, *segments)               # refuses path-unknown without the entry
    if not path.is_file():
        fail("path-unknown", f"{'/'.join(segments)} is prepared, not born -- rename its line in "
                             "the parent's Items")
    parent_doc = doc_of(root, *segments[:-1])
    pfront, pbody = read(parent_doc)
    if any(child == new for child, _ in children(pfront)):
        fail("slug-taken", f"{'/'.join(segments[:-1])} already holds `{new}`")

    # every guard passed -- the effect starts here, the node's own document first
    front, body = read(path)
    front["slug"] = new
    write(path, front, titled(front, body))
    if len(segments) == 2:
        for batch_doc in path.parent.glob(f"*/{DOCS['batch']}"):
            bfront, bbody = read(batch_doc)
            bfront["phase"] = new
            write(batch_doc, bfront, titled(bfront, bbody))
    kind = KINDS[len(segments) - 2]
    carried = dict(item_lines(section_text(pbody, "Items") or "")).get(old, "") \
        if is_written(kind, "Items", pbody) else ""
    for key, value in list(pfront.items()):
        if isinstance(key, str) and ITEM.match(key) and str(value).split(None, 1)[0] == old:
            status = str(value).split(None, 1)[1] if len(str(value).split(None, 1)) > 1 else ""
            pfront[key] = f"{new}  {status}"            # the rank is the key's: untouched
    write(parent_doc, pfront, items_follow(pfront, pbody, kind, {new: carried}))
    # the folder is DERIVED: its position stays, its name follows
    position = path.parent.name.split("-", 1)[0]
    path.parent.rename(path.parent.parent / f"{position}-{new}")


def reopen(root: Path, segments: list[str]) -> None:
    """Reopens a DONE phase or batch for a rework -- the maintenance cycle's
    hinge: the component's lot accumulates its history instead of spawning
    twins. The transition is done -> redo, and the whole ANCESTRY rises with
    it in the SAME call: every parent entry follows, and a parent found
    closed reopens too -- a phase wears `redo`, a plan wears the only opening
    it knows, `doing`."""
    if len(segments) not in (2, 3):
        # a todo path carries four segments -- the depth alone tells the kinds apart
        fail("reopen-invalid", "a phase or a batch reopens -- plans and todos do not")
    path = standing(root, segments)
    front, body = read(path)
    if front.get("status") != "done":
        fail("reopen-invalid", f"{'/'.join(segments)} is `{front.get('status')}` -- only a done node reopens")
    front["status"] = "redo"
    write(path, front, body)
    child, carried = segments[-1], "redo"
    for depth in range(len(segments) - 1, 0, -1):
        # an ancestor left `done` hides the rework from the walk, which reads a
        # closed node as nothing to do -- the branch would never be descended
        parent_doc = doc_of(root, *segments[:depth])
        pfront, pbody = read(parent_doc)
        set_child(pfront, child, carried)
        if pfront.get("status") == "done":
            pfront["status"] = "doing" if depth == 1 else "redo"
        write(parent_doc, pfront, pbody)
        child, carried = segments[depth - 1], pfront["status"]


SHOWN = {   # what an ANCESTOR shows of its body when a node below it is at work
    "plan": ("Target", "Expected"),
    "phase": ("Target", "Expected", "Arbitrations"),
}


def shown(kind: str, body: str) -> list[str]:
    """-> the selections an ancestor of `kind` mounts: one couple of tags per run of shown
    sections, from the first one's heading to the next section OF THE KIND the document
    holds -- a heading that is no section of the kind stays with the section it details;
    a shown section the document lacks says nothing."""
    present = [name for name, _ in split_sections(body) if name in SECTIONS[kind]]
    couples: list[str] = []
    start = None
    for rank, name in enumerate(present):
        if name in SHOWN[kind] and start is None:
            start = name
        following = present[rank + 1] if rank + 1 < len(present) else None
        if start is not None and following not in SHOWN[kind]:
            couples.append(f"## {start}..## {following}" if following else f"## {start}..")
            start = None
    return couples


def mount_chain(root: Path, segments: list[str], whole: bool = False) -> list[dict]:
    """-> the `::mount` payload a node commands -- the chain GROWS by level: TWO
    entries for a plan (the package's PLAN method, nested with its body, then the
    plan instance, stacked), FOUR for a phase, SIX for a batch. A PREPARED item --
    an entry without a document yet -- and an item not even prepared under a born
    parent mount the METHOD of their kind ahead, the instance absent: three entries
    for a phase to come, five for a batch to come -- the combined GO that frames the
    parent, then the child, mounts once. The LAST document of the chain mounts its whole
    body; an ancestor mounts the selections `shown` gives it, or every body under `whole`.
    Method paths follow the PIN -- derived from this script's own
    vendored position, never configured; instance paths from the node's walk.
    READ-ONLY: nothing written, no status read, no next move touched -- the verb
    plays at any moment."""
    if not 1 <= len(segments) <= 3:
        fail("path-unknown", "a node is <slug>[/<phase>[/<batch>]]")
    procs = Path(__file__).resolve().parents[2] / "procs"
    entries: list[dict] = []
    for depth in range(1, len(segments) + 1):
        kind = KINDS[depth - 1]
        method = procs / f"{kind.upper()}.md"
        try:
            method_name = str(method.relative_to(root))
        except ValueError:
            method = None
        if method is None or not method.is_file():
            fail("method-missing",
                 "the script's vendored position carries no reachable procs/ -- "
                 "the mount verb plays from an installed instance")
        entries.append({"doc": method_name, "scope": "nested", "body": True})
        if depth == len(segments) > 1:
            # the last segment may be PREPARED (an entry, no document) or not even that:
            # under a born parent its kind's method rides ahead, its instance absent --
            # the combined GO that frames the parent, then the child, mounts once
            parent_front, _ = read(doc_of(root, *segments[:-1]))
            if segments[-1] not in {c for c, _ in children(parent_front)}:
                break
        instance_doc = doc_of(root, *segments[:depth])
        if not instance_doc.is_file():
            if depth == 1:
                fail("path-unknown", f"plans/{segments[0]} is not born -- write its Context first")
            if depth != len(segments):
                fail("path-unknown", f"{'/'.join(segments[:depth])} is prepared, not born -- "
                                     "nothing stands under it yet")
            break                       # a prepared item: its method rides, no instance yet
        # the node's OWN document comes with its BODY: what its framing wrote -- the
        # context, the ground, the arbitrations, the items -- is the matter of the work
        entries.append({"doc": str(instance_doc.relative_to(root)), "scope": "stacked",
                        "body": True, "kind": kind})
    # the node at work -- the last document of the chain -- keeps its whole body; each
    # ancestor above it shows the sections that arm the level below
    nodes = [one for one in entries if "kind" in one]
    for entry in nodes[:-1]:
        if not whole:
            entry["body"] = shown(entry["kind"], read(root / entry["doc"])[1]) or False
    for entry in nodes:
        del entry["kind"]
    return entries


def next_move(root: Path, slug: str) -> str | None:
    """-> the plan's next move, computed from what the script itself wrote -- the
    DEEPEST node that awaits something, said with its full parent path and the
    WORD it awaits; None once the plan is done. This is the content of the
    plan's push: the script has the information, it says it. ENGAGEMENT primes
    order: at every level the walk serves the first engaged node (doing, redo,
    blocked -- in item order) and, without one, the first todo. The line
    DESCRIBES -- the GO it names is the operator's, never an order to the
    agent: a plan's next move is carried to the surface, not played. The
    script's own writes never leave a delivered parent open (a Delivery closes it
    in the call that delivers its last child): the two lines that say a node
    stands open over delivered children describe a tree older than the cascade,
    or a hand edit -- `repair` closes it. The line ENDS with the VECTOR of the
    node it names, in parentheses -- `plan:<slug>`, `plan-phase:<slug>/<phase>` or
    `plan-lot:<slug>/<phase>/<batch>`, the address `verify` resolves: the key the
    thread's step carries, so a line served again finds its step and never
    adds one (batch la-cle-au-next-move)."""

    def at(text: str, *node: str) -> str:
        # the deepest node named, as the vector families spell it: the last token of the
        # line is what the agent copies into the step's key
        family = next(name for name, depth in FAMILIES.items() if depth == len(node))
        return f"{text} ({family}:{'/'.join(node)})"

    def first_open(kids: list[tuple[str, str]]) -> tuple[str, str] | None:
        # engagement primes order: a started node outranks one never opened
        alive = [one for one in kids if one[1] != "done"]
        working = [one for one in alive if one[1] in ENGAGED]
        return (working or alive or [None])[0]

    front, _ = read(doc_of(root, slug))
    if front.get("status") == "done":
        return None
    kids = children(front)
    if not kids:
        return at("the plan has no phase yet -- its phases come on the operator's GO "
                  "(one GO creates and frames them)", slug)
    picked = first_open(kids)
    if picked is None:
        return at("every phase is delivered and the plan stands open -- `repair` closes it", slug)
    phase, pstatus = picked
    pdoc = doc_of(root, slug, phase)
    batches = children(read(pdoc)[0]) if pdoc.is_file() else []   # prepared: no document yet
    if not batches:
        if pstatus == "todo":
            return at(f"the phase {phase} awaits its framing -- its batches come on the operator's GO", slug, phase)
        if pstatus == "redo":
            return at(f"the phase {phase} is reopened -- its rework awaits the operator's GO", slug, phase)
        if pstatus == "blocked":
            return at(f"the phase {phase} is blocked -- the GO that unblocks it is awaited", slug, phase)
        # a framed phase walks doing without batches yet: its move is
        # their creation -- closing is for delivered batches alone
        return at(f"the phase {phase} awaits its batches -- their creation awaits the operator's GO", slug, phase)
    # a reopened phase walks its batches like any open one: the line
    # names the batch that carries the work, never the phase alone
    b = first_open(batches)
    if b is None:
        # every batch delivered: a reopened phase carries its own rework,
        # an open one is ready to close
        return at(f"the phase {phase} is reopened -- its rework awaits the operator's GO" if pstatus == "redo"
                  else f"the phase {phase} is delivered and stands open -- `repair` closes it", slug, phase)
    batch, bstatus = b
    if bstatus == "todo":
        return at(f"the batch {phase}/{batch} awaits its framing", slug, phase, batch)
    if bstatus == "blocked":
        return at(f"the batch {phase}/{batch} is blocked -- the GO that unblocks it is awaited", slug, phase, batch)
    if bstatus == "redo":
        return at(f"the batch {phase}/{batch} is reopened -- its rework awaits the operator's GO", slug, phase, batch)
    return at(f"the batch {phase}/{batch} awaits its implementation -- on the GO that names it", slug, phase, batch)

BUS = "events.json"          # the engine's record: written by the engine, read here
SIGNAL = "plan-next-move"    # this package's own signal -- the manifest declares it
SOURCE = "plan"              # the provider name a standing key carries


def law_line(lines: list[str], code: str) -> int | None:
    """-> the index of the law `code` inside a `constraints.*` block of the front
    matter, None when the code is not posed on this document."""
    key = None
    for at, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            break
        if line[:1] not in (" ", "\t") and ":" in line:
            key = line.split(":", 1)[0].strip()
            continue
        match = LAW.match(line)
        if key and key.startswith("constraints") and match and match.group(1) == code:
            return at
    return None


def amend_law(path: Path, address: str, code: str, text: str) -> None:
    """Replaces ONE posed law by its code -- the line alone moves, every other byte
    of the document stays; a code not posed here refuses by name."""
    lines = path.read_text(encoding="utf-8").splitlines()
    at = law_line(lines, code)
    if at is None:
        fail("code-unknown", f"`{code}` is not posed on {address} -- a bare text derives its code")
    lines[at] = f"  {code}  {text.strip()}"
    regime().replace(path, "\n".join(lines) + "\n")


def retire_law(path: Path, address: str, code: str) -> str:
    """Retires ONE law by its code: the line leaves its `constraints.*` block (the
    block's key with it when it was the last), and the code stays DECLARED under
    `retired:` with the date and the text it carried -- the writer's inventory reads
    that line as taken, so a retired number never returns. -> the text retired"""
    lines = path.read_text(encoding="utf-8").splitlines()
    at = law_line(lines, code)
    if at is None:
        fail("code-unknown", f"`{code}` is not posed on {address} -- nothing to retire")
    text = LAW.match(lines[at]).group(2).strip()
    del lines[at]
    head = at - 1
    while lines[head].startswith("  "):
        head -= 1
    if head == at - 1 and (at >= len(lines) or not lines[at].startswith("  ")):
        del lines[head]                              # the block emptied: its key goes too
    end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    entry = f"  {code}  retired {datetime.now(timezone.utc).date().isoformat()} -- {text}"
    spot = next((i for i, line in enumerate(lines[1:end], 1) if line.startswith("retired:")), None)
    if spot is None:
        lines[end:end] = ["retired: |", entry]
    else:
        stop = spot + 1
        while stop < end and lines[stop].startswith("  "):
            stop += 1
        lines[stop:stop] = [entry]
    regime().replace(path, "\n".join(lines) + "\n")
    return text


def sections():
    """-> the engine's front matter writer. A plan document carries the model keys THIS
    script owns and, beside them, the laws and the rows a framing writes: that writer is the engine's, imported through the vendored bootstrap -- never a second
    implementation of the same span.

    documentary: what a framing needs on its own document is `constrain` and `serve`; the
    package that owns the model offers them, and the composition no longer has to carry
    an author's package to write a law."""
    return conductor().sections


def conductor():
    """-> the engine's face, imported through the vendored bootstrap: its writer
    (`sections`), its row cutter (`reading.split_row`), its `Refusal`."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from _core import core                                  # noqa: E402 -- the bootstrap
    return core(__file__)


def served(root: Path) -> list[str]:
    """-> the next move lines the bus HOLDS for this package, plan by plan.

    A standing key reads `standing|<source>|<signal>|<vector>`; this package reads its
    own three and nothing else -- another provider's held entry is not its business.

    documentary: the emission and the reception are two halves of one mechanism -- the
    call pushes, the turn serves; keeping the reader here is what lets the package
    carry its own line without asking anything of a neighbour."""
    path = root / ".sys" / "records" / BUS
    if not path.is_file():
        return []
    try:
        held = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return []                # an unreadable record holds nothing
    prefix = f"standing|{SOURCE}|{SIGNAL}|"
    lines = [str((entry or {}).get("text", "")).strip()
             for key, entry in sorted(held.items()) if key.startswith(prefix)]
    return [line for line in lines if line]


def announce(root: Path, slug: str) -> None:
    """Prints the plan's push after a mutating call -- the generating event is
    THIS moment: the state just changed, the fresh next move replaces the held
    line (or clears it, a closed plan cleans its own push)."""
    action = next_move(root, slug)
    if action is None:
        print(f"::clear plan-next-move plan:{slug}")
    else:
        print(f"::push plan-next-move plan:{slug} {action}")


def status_table(root: Path, slug: str | None) -> str:
    """-> the progress table, DERIVED from the front matters alone -- what replaces
    a hand-kept index: nothing here is stored, everything is read."""
    plans = sorted((root / "plans").glob("*/PLAN.md")) if (root / "plans").is_dir() else []
    if slug is None:
        rows = ["| plan | status | phases |", "|---|---|---|"]
        for doc in plans:
            front, _ = read(doc)
            kids = children(front)
            done = sum(1 for _, s in kids if s == "done")
            rows.append(f"| {front.get('slug')} | {front.get('status')} | {done}/{len(kids)} done |")
        return "\n".join(rows)
    doc = doc_of(root, slug)
    if not doc.is_file():
        fail("path-unknown", f"{slug} has no plan document")
    rows = ["| node | kind | status |", "|---|---|---|"]

    def walk(path: Path, trail: str) -> None:
        front, _ = read(path)
        rows.append(f"| {trail} | {front['kind']} | {front.get('status')} |")
        for position, (child, cstatus) in enumerate(children(front), 1):
            if front["kind"] == "batch":
                rows.append(f"| {trail}/{child} | todo | {cstatus} |")
                continue
            child_doc = (path.parent / f"{position}-{child}"
                         / DOCS["phase" if front["kind"] == "plan" else "batch"])
            if child_doc.is_file():
                walk(child_doc, f"{trail}/{child}")
            else:                    # prepared: an entry, no document yet
                rows.append(f"| {trail}/{child} | {'phase' if front['kind'] == 'plan' else 'batch'} | {cstatus} |")
    walk(doc, slug)
    return "\n".join(rows)


def check(root: Path) -> list[str]:
    """-> every incoherence the structure holds -- the lint that catches the hand:
    a child line without its document, a document without its line, statuses out
    of the enumeration, a line disagreeing with its document, a body with no
    prose, a DERIVED folder (`<n>-<name>`) without its entry -- any other directory
    is the plan's own material and says nothing. Empty means clean."""
    found: list[str] = []
    plans_dir = root / "plans"
    for doc in sorted(plans_dir.glob("**/*.md")) if plans_dir.is_dir() else []:
        if doc.name not in DOCS.values():
            continue
        front, body = read(doc)
        spot = "/".join(doc.parent.relative_to(plans_dir).parts)
        if front.get("status") not in STATUSES:
            found.append(f"{spot}: status `{front.get('status')}` out of the enumeration")
        # prose = what remains once headings and blanks are gone -- a heading is a label
        prose = [l for l in body.splitlines() if l.strip() and not l.lstrip().startswith("#")]
        if not prose:
            found.append(f"{spot}: no prose in the body")
        title, wanted = title_line(body), title_of(front)
        if title is None:
            found.append(f"{spot}: no title -- the front says `{wanted}`")
        elif LEVEL_TITLE.match(title) and title != wanted:
            found.append(f"{spot}: title says `{title}` -- the front says `{wanted}`")
        sections = [name for name, _ in split_sections(body) if name is not None]
        for twice in sorted({n for n in sections if sections.count(n) > 1}):
            found.append(f"{spot}: section `{twice}` appears twice -- the writer reaches the first "
                         "alone; the second is prose to move or remove")
        for legacy in ("phases", "batches", "todos"):
            if legacy in front:
                found.append(f"{spot}: legacy `{legacy}:` block -- children are `item.<n>` entries now")
        # the key's number must SAY the position -- hand renumbering reddens here
        numbers = [int(ITEM.match(k).group(1)) for k in front
                   if isinstance(k, str) and ITEM.match(k)]
        if numbers != list(range(1, len(numbers) + 1)):
            found.append(f"{spot}: item numbering broken -- keys say {numbers}")
        kids = children(front)
        names = [child for child, _ in kids]
        for twice in sorted({n for n in names if names.count(n) > 1}):
            found.append(f"{spot}: child `{twice}` appears twice -- a name is born once")
        # a closed node over started work: line and document agree, so no other
        # rule here sees it -- and the walk skips the whole branch as delivered
        if front.get("status") == "done":
            started = [child for child, cstatus in kids if cstatus in ENGAGED]
            if started:
                found.append(f"{spot}: done while `{'`, `'.join(started)}` "
                             "carries open work -- the ancestry rises with its child")
        for position, (child, cstatus) in enumerate(kids, 1):
            if cstatus not in STATUSES:
                found.append(f"{spot}: child `{child}` status `{cstatus}` out of the enumeration")
            if front["kind"] == "batch":
                # a todo is named by its SLUG -- a positional tag says nothing in a
                # status line, and every entry owns its `- <name> -- ...` body line
                if re.fullmatch(r"T\d+", child):
                    found.append(f"{spot}: todo `{child}` wears a positional tag -- a todo is named by its slug")
                elif f"- {child} -- " not in body:
                    found.append(f"{spot}: todo `{child}` has no `- {child} -- ...` line in the body")
                continue
            # the folder is DERIVED (<position>-<name>) -- a drifted rename reddens here
            child_doc = (doc.parent / f"{position}-{child}"
                         / DOCS["phase" if front["kind"] == "plan" else "batch"])
            if not child_doc.is_file():
                if cstatus != "todo":    # a prepared item is a todo entry without a document
                    found.append(f"{spot}: entry `{child}` is {cstatus} without its folder `{position}-{child}`")
            else:
                cfront, _ = read(child_doc)
                if cfront.get("status") != cstatus:
                    found.append(f"{spot}: entry `{child}` says {cstatus}, the document says {cfront.get('status')}")
        if front["kind"] != "batch":
            lined = {f"{i}-{c}" for i, (c, _) in enumerate(kids, 1)}
            # a DERIVED folder without its entry reddens; a cache, campaigns, playbooks --
            # the plan's own material -- carries no entry and says nothing
            for sub in sorted(p for p in doc.parent.iterdir() if p.is_dir()):
                if re.fullmatch(r"\d+-.+", sub.name) and sub.name not in lined:
                    found.append(f"{spot}: derived folder `{sub.name}` has no entry")
    return found


def repair(root: Path) -> tuple[list[str], list[str]]:
    """Mends what is MECHANICAL -- and says every mend: the item keys renumbered in
    the order of their entries; a line disagreeing with its child's document moved
    to the DOCUMENT's own status; a child folder without its entry given one, at the
    end, from the document it holds; a plan or a phase open over children all done
    CLOSED -- the cascade that never ran, on a tree older than it. Every other
    finding is SAID with its gesture and left as it is. -> (mended, left)"""
    mended: list[str] = []
    plans_dir = root / "plans"
    for doc in sorted(plans_dir.glob("**/*.md")) if plans_dir.is_dir() else []:
        if doc.name not in DOCS.values():
            continue
        front, body = read(doc)
        spot = "/".join(doc.parent.relative_to(plans_dir).parts)
        changed = False
        numbers = [int(ITEM.match(k).group(1)) for k in front if isinstance(k, str) and ITEM.match(k)]
        if numbers != list(range(1, len(numbers) + 1)):
            kids = children(front)
            for key in [k for k in front if isinstance(k, str) and ITEM.match(k)]:
                del front[key]
            for position, (child, cstatus) in enumerate(kids, 1):
                front[f"item.{position}"] = f"{child}  {cstatus}"
            mended.append(f"{spot}: item keys renumbered 1..{len(kids)}")
            changed = True
        if front["kind"] != "batch" and front.get("status") != "done" and children(front) \
                and all(cstatus == "done" for _, cstatus in children(front)):
            # the cascade that never ran: an open node over children all delivered closes
            front["status"] = "done"
            mended.append(f"{spot}: open over children all done -- closed, the cascade that never ran")
            changed = True
        if front["kind"] != "batch":
            kids = children(front)
            child_kind = "phase" if front["kind"] == "plan" else "batch"
            for position, (child, cstatus) in enumerate(kids, 1):
                child_doc = doc.parent / f"{position}-{child}" / DOCS[child_kind]
                if child_doc.is_file():
                    truth = read(child_doc)[0].get("status")
                    if truth in STATUSES and truth != cstatus:
                        set_child(front, child, truth)
                        mended.append(f"{spot}: entry `{child}` said {cstatus}, the document says "
                                      f"{truth} -- the document wins")
                        changed = True
            lined = {c for c, _ in kids}
            for sub in sorted(p for p in doc.parent.iterdir() if p.is_dir()):
                match = re.fullmatch(r"\d+-(.+)", sub.name)
                held = sub / DOCS[child_kind]
                if match and match.group(1) not in lined and held.is_file():
                    truth = read(held)[0].get("status")
                    add_child(front, match.group(1), truth if truth in STATUSES else "todo")
                    mended.append(f"{spot}: folder `{sub.name}` had no entry -- `{match.group(1)}` "
                                  "entered at the end, from its document")
                    changed = True
        retitled = titled(front, body)
        if retitled != body:
            body = retitled
            mended.append(f"{spot}: title set to `{title_of(front)}` -- the front's names")
            changed = True
        if changed:
            write(doc, front, body)
            if front["kind"] != "batch":
                reindex(doc.parent, front)
            if front.get("status") == "done" and front["kind"] == "phase":
                _splice_child(doc.parent.parent / DOCS["plan"], front["slug"], "done")
    gestures = {
        "out of the enumeration": "set the status by `set`",
        "no prose": "write its Context by `section`",
        "legacy": "rewrite the children by `section … Items`",
        "a name is born once": "rewrite Items with one line per item",
        "the writer reaches the first": "keep the prose that holds, then remove the other by "
                                        "`section <address> <Name> --remove=<n>`",
        "carries open work": "`reopen` the parent, or `set` the child",
        "positional tag": "rewrite Items with slugs",
        "line in the body": "rewrite Items with the missing line",
        "has no entry": "prepare the item in Items, or remove the folder by hand",
        "without its folder": "the document is gone: `set` it todo, or restore the folder by hand",
    }
    left = []
    for finding in check(root):
        why = next((g for key, g in gestures.items() if key in finding), "a hand's business")
        left.append(f"{finding} -- {why}")
    return mended, left


def main(argv: list[str]) -> int:
    """The gate: the verb's arity is judged BEFORE anything plays -- a malformed
    call refuses by name with the verb's usage, never the whole of this text -- and
    a verb that WRITES plays inside the plan's critical section: the lock is taken
    before the first read and released after the last write, whatever the number
    of documents the verb walks."""
    if not argv:
        sys.stderr.write(__doc__)
        return 2
    verb, rest = argv[0], list(argv[1:])
    if verb not in USAGE:
        fail("verb-unknown", f"`{verb}` -- the verbs are {', '.join(USAGE)}")
    flags = [one for one in rest if one.startswith("--") and verb in ("section", "mount")]
    rest = [one for one in rest if not (one.startswith("--") and verb in ("section", "mount"))]
    if verb in ("section", "constrain") and rest and rest[-1] == "-":
        rest.pop()                                  # the stdin marker, said and dropped
    low, high = ARITY[verb]
    if len(rest) < low:
        fail("argument-missing", f"{verb} takes {USAGE[verb]}")
    if high is not None and len(rest) > high:
        fail("argument-unexpected", f"`{rest[high]}` -- {verb} takes {USAGE[verb]}")
    for flag in flags if verb == "mount" else ():
        if flag != "--whole":
            fail("argument-unexpected", f"`{flag}` -- {USAGE['mount']}")
    for flag in flags if verb == "section" else ():
        if flag != "--append" and not re.fullmatch(r"--remove(=[1-9][0-9]*)?", flag):
            fail("argument-unexpected", f"`{flag}` -- {USAGE['section']}")
    if len(flags) > 1 and verb == "section":
        fail("argument-unexpected", f"`{' '.join(flags)}` -- one flag at a time: {USAGE['section']}")
    root = home()
    if verb in WRITING and rest:
        with guarded(root, rest[0].split("/")[0]):
            return _play(root, verb, rest, flags)
    return _play(root, verb, rest, flags)


def _play(root: Path, verb: str, rest: list[str], flags: list[str]) -> int:
    removal = next((flag for flag in flags if flag.startswith("--remove")), None)
    if verb == "section" and removal is not None:
        segments = rest[0].split("/")
        nth = int(removal.split("=", 1)[1]) if "=" in removal else None
        path, said = remove_section(root, segments, rest[1], nth)
        print(f"pp-plan: {said} removed from {rest[0]} -- {path.relative_to(root.parent)}")
        announce(root, segments[0])
    elif verb == "section":
        segments = rest[0].split("/")
        path, said, moves = write_section(root, segments, rest[1], sys.stdin.read(), "--append" in flags)
        print(f"pp-plan: {rest[1]} {' and '.join(said)} on {rest[0]} -- {path.relative_to(root.parent)}")
        for line in moves:
            print(line)
        announce(root, segments[0])
    elif verb == "done":
        done(root, rest[0].split("/"))
        print(f"pp-plan: {rest[0]} -> done")
        announce(root, rest[0].split("/")[0])
    elif verb == "block":
        block(root, rest[0].split("/"), " ".join(rest[1:]))
        print(f"pp-plan: {rest[0]} -> blocked -- {' '.join(rest[1:])}")
        announce(root, rest[0].split("/")[0])
    elif verb == "move":
        touched = move(root, rest[0].split("/"), rest[1].split("/"), rest[2])
        print(f"pp-plan: moved -- {rest[0]} -> {rest[1]} [{rest[2]}]")
        print("pp-plan: the subtree's prose is yours -- sweep its references to the old home")
        for moved_plan in touched:
            announce(root, moved_plan)
    elif verb == "rename":
        segments = rest[0].split("/")
        rename(root, segments, rest[1])
        print(f"pp-plan: renamed -- {rest[0]} -> {'/'.join(segments[:-1] + [rest[1]])}")
        print("pp-plan: the prose is yours -- sweep what says the old name (bodies, threads)")
        announce(root, segments[0])
    elif verb == "mount":
        # read-only: the chain is SAID (the directive pp collects), nothing moves --
        # no announce either: a mount is a view, never an event of the plan
        chain = mount_chain(root, rest[0].split("/"), whole="--whole" in flags)
        print("::mount " + json.dumps(chain))
        print(f"pp-plan: {len(chain)} documents for {rest[0]} -- mounted when played through pp")
    elif verb == "constrain":
        writer = sections()
        path = standing(root, rest[0].split("/"))
        if "--retire" in rest:
            at = rest.index("--retire")
            code = rest[at + 1] if at + 1 < len(rest) else ""
            if not code:
                fail("argument-missing", f"--retire takes the code -- {USAGE['constrain']}")
            spare = [one for one in rest[1:] if one not in ("--retire", code)]
            if spare:
                fail("argument-unexpected", f"`{spare[0]}` -- {USAGE['constrain']}")
            retire_law(path, rest[0], code)
            print(f"pp-plan: retired -- {code} on {rest[0]}, kept under `retired:` -- the code never returns")
            return 0
        section = rest[rest.index("--section") + 1] if "--section" in rest and rest.index("--section") + 1 < len(rest) else ""
        spare = [one for one in rest[1:] if one != "--section" and one != section]
        if len(spare) > 1:
            fail("argument-unexpected", f"`{spare[1]}` -- {USAGE['constrain']}")
        amended, fresh = [], []
        for text in writer.bounded(sys.stdin.read().splitlines()):
            # a line that OPENS on a code amends that law; a bare text derives its code
            match = LAW.match("  " + text.strip())
            (amended if match else fresh).append((match.group(1), match.group(2)) if match else text)
        for code, text in amended:
            amend_law(path, rest[0], code, text)
        posed = writer.constrain(root, path, spare[0] if spare else None, section, fresh) if fresh else []
        said = []
        if amended:
            said.append(f"amended -- {' '.join(code for code, _ in amended)}")
        if posed:
            said.append(f"posed -- {' '.join(posed)} in constraints.{section}")
        print(f"pp-plan: {'; '.join(said)} on {rest[0]}")
    elif verb == "serve":
        engine = conductor()
        path = standing(root, rest[0].split("/"))
        whole = rest[1:] == ["-"]
        try:
            # a piped line is cut as the engine's reader will cut it: a blank inside a
            # token's brackets belongs to the token, as it does to a quoted argv word
            rows = ([list(engine.reading.split_row(one)) for one in sys.stdin.read().splitlines()]
                    if whole else [rest[1:]])
            if whole:
                while rows and not rows[-1]:
                    rows.pop()
                while rows and not rows[0]:
                    rows.pop(0)
                if not any(rows):
                    fail("value-malformed", "an empty serve section writes nothing")
            answer = engine.sections.serve(path, rows, whole)
        except engine.Refusal as refusal:
            fail(refusal.code, str(refusal).split(" — ", 1)[-1])
        print(f"pp-plan: served -- {answer} on {rest[0]}")
    elif verb == "next-move":
        # read-only, like `status`: a payload SERVES what the bus holds, it never pushes
        for line in served(root):
            print(line)
    elif verb == "verify":
        verify(root, sys.stdin.read())      # read-only: the engine asks, the tree answers
    elif verb == "status":
        print(status_table(root, rest[0] if rest else None))
    elif verb == "check":
        findings = check(root)
        if findings:
            sys.stderr.write("pp-plan: check FAILED --\n" + "\n".join(f"  {f}" for f in findings) + "\n")
            return 2
        print("pp-plan: check clean")
    elif verb == "repair":
        mended, left = repair(root)
        for one in mended:
            print(f"pp-plan: repaired -- {one}")
        for one in left:
            print(f"pp-plan: left -- {one}")
        if not mended and not left:
            print("pp-plan: check clean -- nothing to repair")
        elif not left:
            print("pp-plan: check clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
