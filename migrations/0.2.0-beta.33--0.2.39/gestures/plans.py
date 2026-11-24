"""The plans: every document of the form 0.2.0-beta.33 wrote takes the form 0.2.39 reads.

At the front, `kind: <k>` becomes `template: <k>`, the `phase:` line leaves, and the blueprint law
the old script posed at a plan's birth leaves `constraints.production` (the template of 0.2.39
carries it); every other line of the front stays as written, `status:` included. In the body, a
section whose text is still the instruction of its old template leaves; a section the templates no
longer carry takes the name of the one that replaced it -- merged after that section's own text,
under a `### <old name>` title, when that section is already there --; the sections stand in the template's order, a
section no template knows after the one it followed. The open batches whose todos are all done are
said, never closed.

Counted per plan root: the documents, and the lines of the operator's prose -- every line that is
not blank and not a title -- before and after."""
from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path

import _common

from . import DATA, joined, replace, split

TEMPLATES = {"plan": "_PLAN.md", "phase": "_PHASE.md", "batch": "_BATCH.md"}
DOCUMENTS = {"PLAN.md": "plan", "PHASE.md": "phase", "BATCH.md": "batch"}
SECTIONS = {                                # the sections of each template of 0.2.39, in their order
    "plan": ("Context", "Ground", "Expected", "Choices", "Items", "Delivery"),
    "phase": ("Ground", "Expected", "Choices", "Items", "Delivery"),
    "batch": ("Ground", "Expected", "Tests", "Choices", "Items", "Delivery"),
}
RENAMED = {"Survey": "Ground", "Target": "Expected", "Arbitrations": "Choices", "Decisions": "Choices"}
PRUNED = {"_templates", ".git", "__pycache__"}
HEADING = re.compile(r"^## (.+?)\s*$")
ITEM = re.compile(r"^item\.\d+: (\S+)\s+(\S+)\s*$")
LAWS = "constraints.production: |"


def sections_of(body: str) -> list[tuple[str | None, list[str]]]:
    """-> the sections of a body, (name, the lines under its heading), the head first (named None);
    a `## ` line inside a code fence is no heading."""
    found: list[tuple[str | None, list[str]]] = [(None, [])]
    fenced = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
        matched = None if fenced else HEADING.match(line)
        if matched:
            found.append((matched.group(1), []))
        else:
            found[-1][1].append(line)
    return found


def instructions() -> dict[str, dict[str, str]]:
    """-> kind -> section -> the instruction text of the old template; a section holding a hole
    (`{prose}`) is no instruction."""
    found: dict[str, dict[str, str]] = {}
    for kind, name in TEMPLATES.items():
        _, body = split((DATA / name).read_text(encoding="utf-8"))
        found[kind] = {section: "\n".join(lines).strip() for section, lines in sections_of(body)
                       if section and "\n".join(lines).strip() and "{" not in "\n".join(lines)}
    return found


def blueprint() -> str:
    return (DATA / "BLUEPRINT.txt").read_text(encoding="utf-8").strip()


def prose(text: str) -> list[str]:
    """-> the lines of prose of a body: neither blank nor a title."""
    return [line for line in text.split("\n") if line.strip() and not line.lstrip().startswith("#")]


def renamed(name: str, kind: str) -> str:
    if name in SECTIONS.get(kind, ()):
        return name
    if name == "Context":
        return "Ground"
    if name == "Protocol":
        return "Tests" if kind == "batch" else "Expected"
    return RENAMED.get(name, name)


def front_of(front: list[str], law: str) -> tuple[list[str], str | None]:
    """-> the front 0.2.39 reads, and the template it names: `kind:` renamed, `phase:` and the
    blueprint law out."""
    out, named, at = [], None, None
    for line in front:
        if line.startswith("kind: "):
            named = line.removeprefix("kind: ").strip()
            out.append(f"template: {named}")
        elif line.startswith("phase: "):
            continue
        else:
            out.append(line)
    if LAWS in out:
        at = out.index(LAWS)
        end = at + 1
        while end < len(out) and out[end].startswith("  "):
            end += 1
        kept = [line for line in out[at + 1:end] if re.sub(r"^\s*\S+\s+", "", line, count=1).strip() != law]
        out[at:end] = [LAWS, *kept] if kept else []
    return out, named


def body_of(body: str, kind: str, said: dict[str, str]) -> tuple[str, list[str], list[str]]:
    """-> the body 0.2.39 reads, the instruction sections removed, the sections renamed."""
    found = sections_of(body)
    head = "\n".join(found[0][1]).rstrip("\n")
    removed, moved = [], []
    pieces: list[tuple[str, str, str]] = []           # (the section it lands in, its old name, its text)
    for name, lines in found[1:]:
        text = "\n".join(lines).strip("\n")
        if name in said and text.strip() == said[name]:
            removed.append(name)
            continue
        pieces.append((renamed(name, kind), name, text))
    order: list[str] = []
    landed: dict[str, list[tuple[str, str]]] = {}
    for target, name, text in pieces:
        if target not in landed:
            order.append(target)
            landed[target] = []
        landed[target].append((name, text))
    rendered: dict[str, str] = {}
    for target in order:
        olds = [(name, text) for name, text in landed[target] if name != target]
        natives = [text for name, text in landed[target] if name == target]
        moved += [name for name, _ in olds]
        if len(natives) > 1:                       # a section twice stays twice: the operator's to settle
            rendered[target] = f"\n\n## {target}\n\n".join(one.strip("\n") for one in natives)
        elif olds and (natives or len(olds) > 1):
            parts = [one.strip("\n") for one in natives] + [f"### {name}\n\n{text.strip(chr(10))}" for name, text in olds]
            rendered[target] = "\n\n".join(parts)
        else:
            rendered[target] = (natives or [olds[0][1]])[0].strip("\n")
    ranks = SECTIONS.get(kind, ())
    groups: list[tuple[int, list[str]]] = [(-1, [])]
    for target in order:
        if target in ranks:
            groups.append((ranks.index(target), [target]))
        else:
            groups[-1][1].append(target)
    groups.sort(key=lambda group: group[0])
    names = [name for _, members in groups for name in members]
    text = head + "".join(f"\n\n## {name}\n\n{rendered[name]}".rstrip() for name in names)
    return text.rstrip("\n") + "\n", removed, moved


def migrated(text: str, kind: str, said: dict[str, dict[str, str]], law: str) -> dict:
    """-> what the document becomes: its new text and what moved."""
    front, body = split(text)
    if front is None:
        raise _common.Refused("plan-unreadable", "a plan document carries no front")
    if not any(line.startswith("kind: ") for line in front) and not any(line.startswith("phase: ") for line in front):
        return {"text": text, "removed": [], "moved": [], "before": prose(body), "after": prose(body),
                "front": front}
    new_front, named = front_of(front, law)
    kind = named or kind
    new_body, removed, moved = body_of(body, kind, said.get(kind, {}))
    kept_sections = [lines for name, lines in sections_of(body) if name not in removed or name is None]
    before = [line for lines in kept_sections for line in prose("\n".join(lines))]
    return {"text": joined(new_front, new_body), "removed": removed, "moved": moved, "before": before,
            "after": prose(new_body), "front": new_front}


def documents(root: Path) -> list[tuple[Path, str]]:
    """-> (a plan document, its kind by its file name) under a plan root."""
    found = []
    for here, directories, files in os.walk(root):
        directories[:] = sorted(one for one in directories if one not in PRUNED)
        found += [(Path(here) / name, DOCUMENTS[name]) for name in files if name in DOCUMENTS]
    return sorted(found)


def open_done(front: list[str]) -> str | None:
    """-> the status of an open batch whose todos are all done, None otherwise."""
    status = next((line.removeprefix("status: ").strip() for line in front if line.startswith("status: ")), "")
    items = [ITEM.match(line) for line in front if line.startswith("item.")]
    if status != "done" and items and all(one and one.group(2) == "done" for one in items):
        return status
    return None


def gesture(house, engine) -> list[tuple]:
    said, law = instructions(), blueprint()
    planned: list[tuple[Path, list[tuple[Path, dict]]]] = []
    for root in house.plans:
        planned.append((root, [(path, migrated(path.read_text(encoding="utf-8"), kind, said, law))
                               for path, kind in documents(root)]))
    rows = []
    for root, done in planned:                     # every document read before the first one is written
        for path, one in done:
            if one["text"] != path.read_text(encoding="utf-8"):
                replace(path, one["text"])
            status = open_done(one["front"]) if path.name == "BATCH.md" else None
            if status is not None:
                print(f"migrate: plans: {path.parent.relative_to(house.root)} is {status} and every todo is "
                      "done -- `pp-plan done` closes it, on your word", flush=True)
        on_template = sum(any(line.startswith("template: ") for line in one["front"])
                          and not any(line.startswith(("kind: ", "phase: ")) for line in one["front"])
                          for _, one in done)
        before = sum(len(one["before"]) for _, one in done)
        kept = sum(sum((Counter(one["before"]) & Counter(one["after"])).values()) for _, one in done)
        removed = sum(len(one["removed"]) for _, one in done)
        moved = sum(len(one["moved"]) for _, one in done)
        print(f"migrate: plans: {root.relative_to(house.root)} -- {len(done)} document(s), {removed} instruction "
              f"section(s) removed, {moved} section(s) renamed or merged", flush=True)
        rows += [(root.parent, "plan-documents", len(done), on_template), (root.parent, "plan-lines", before, kept)]
    return rows
