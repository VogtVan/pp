#!/usr/bin/env python3
"""DETERMINISTIC keeper of an instance's plans -- the one writer of their structure.

A plan lives as documents under the instance root: `plans/<slug>/<TEMPLATE>.md`, then
one subdirectory per node under it, as deep as the chain of its templates goes: each
template says `next: <template>` (its items are nodes on that template) or `leaf: yes`
(its items are todos), and a node's file is named after its template (`PLAN.md`,
`PHASE.md`, `BATCH.md` for the product's chain). A plan may also live under the ROOT OF
DOCUMENTS the run was opened with (`<root>/plans/<slug>/`, read at the run's slot
through `PP_RUN`): a SHARED plan, born by `section <slug> <first section> --shared`, that
every run opened under the same root reads and writes alike. A slug lives in ONE tree,
the instance or the shared root, and every verb plays on it under that tree's own lock;
`status` says `shared`. A plan standing in both trees is refused `plan-twice` by every
verb that resolves its slug -- `status`, `next-move` and `check` say the double --, no tree
winning in silence. The NAME is bare -- the identity, what
entries carry and what the caller addresses -- while the FOLDER on disk is
INDEXED, `<n>-<name>`, DERIVED from the position the `item.<n>` keys own; the
script alone renames folders when an order changes. Every document opens on a
YAML front matter that carries ONE entry PER CHILD (`item.<n>: <name>  <status>`,
statuses among todo, doing, done, blocked and redo) and a BODY of titled
SECTIONS. Every node names its TEMPLATE (`template:`): a document whose FRONT MATTER alone
says the level's structure -- its `sections`, in their order, Items and Delivery added last
when it does not place them, and its `statuses`, the sections whose writing makes a node
`doing` and the ones whose rewriting reopens a `done` one (`redo`). A tree's own templates
(`<tree>/plans/_templates/<name>.md`) are read before the product's (`templates/`). The
agent's prose goes through `section`, never through an editor. An item exists in three
moments: PREPARED -- one line `- <slug> -- <brief>` in its parent's `Items` section, from
which its entry is derived, no document yet; BORN -- its first section written creates its
folder and its document on its level's template, its title and that section alone;
DELIVERED -- its statuses DEDUCED from what is written, as its template's `statuses` say:
a leaf's Delivery delivers one todo (`--item`), and a node is `done` once all its items
are, the closing rising to the plan; a branch's Delivery is a journal; a `redo` section
reopens a done node, the plan included; any section written lifts a `blocked` node; `done`
closes by hand a todo, a node or a prepared item, `block` says a stop. A plan is born by its template's first section. Keys beyond the model (`constraints:`, `serve:`) are the framing's,
written by the engine's writer: every write returns them verbatim.

  pp-plan.py section <address> <Name> [--append]
                                             -> the named section of the body, prose on
                                                stdin (a trailing `-` marks it): replaced,
                                                inserted at its template's rank when absent,
                                                appended for Delivery or with the flag; a
                                                name the template does not carry refuses;
                                                Items derives the entries; the first write
                                                on a prepared item births it
  pp-plan.py section <slug> <first> --shared -> the plan born under the run's root of documents
                                                (documents-none without one; slug-taken when the
                                                slug stands in either tree)
  pp-plan.py done <address>                  -> closed by hand: a todo of a leaf, a born node (a
                                                dated line of its Delivery names the todos left
                                                open), a prepared item; the closing rises
  pp-plan.py block <address> <reason ...>    -> the node blocked, the reason a dated line of
                                                its Delivery; the next section written lifts it
  pp-plan.py move <src-address> <dst-parent-address> <index>
                                             -> the node changes parent or rank; folders follow
  pp-plan.py rename <address> <new-name>     -> a node under a plan takes a new name: the entry,
                                                its Items line, the folder and the model keys
                                                follow; the prose stays the agent's
  pp-plan.py mount <address> [--whole]       -> the node's ::mount chain, printed -- a
                                                prepared item mounts its template ahead;
                                                the node at work whole, its ancestors by the
                                                sections their template shows (--whole: every
                                                body whole)
  pp-plan.py constrain <address> [<prefix>] --section production|behavior
                                             -> law TEXTS piped one per line, written under
                                                codes the engine's writer derives; a line that
                                                OPENS on a posed code replaces that law in place
  pp-plan.py constrain <address> --retire <code>
                                             -> the law leaves `constraints`;
                                                NOTHING is kept: the law disappears
  pp-plan.py serve <address> <token ...>     -> ONE `serve:` row on the node's document
  pp-plan.py serve <address> -               -> the whole `serve:` section, rows piped
  pp-plan.py material <slug> [<name> [<path>]|-]
                                             -> `material: <name>` on the plan and on every phase
                                                and batch born under it -- the tree their rows read
                                                from; with a path, `<name>: <path>` declared in the
                                                plan's `materials:` block first (the path as given,
                                                read from the plan's folder when relative); the
                                                slug by default, `-` takes the key out everywhere,
                                                the declaration kept; a name the plan does not
                                                declare refuses material-undeclared -- `repo` and
                                                `work` among them: no tree is called so
  pp-plan.py material <slug> - <name>       -> the line `<name>` leaves the PLAN.md's `materials:`
                                                block, nothing else written; an absent name refuses
                                                material-undeclared
  pp-plan.py next-move                      -> the next-move lines, read-only: the held line of
                                                each plan of the instance, the line of each shared
                                                plan computed from its document; a line ends with
                                                the vector of the node it names
  pp-plan.py verify                          -> this package's VERIFIER, the engine's call: a
                                                `plan:<address>` vector on stdin, rc 0 when
                                                its ADDRESS resolves in the tree (born or
                                                prepared), at every depth
  pp-plan.py status [<slug>] [--all] [--engaged] [--json] -> the derived progress list, one line per
                                               node, the plans of the instance then the shared ones
                                               (`shared` after the status); --engaged the engaged
                                               nodes under each open plan; --json the same nodes as data
  pp-plan.py templates [--json]              -> the templates the tree sees, read-only: its own
                                                (`plans/_templates/`) first, the shared root's,
                                                then the product's -- name, origin, description,
                                                `leaf` or the chain it opens, sections; one that
                                                cannot serve with its refusal
  pp-plan.py check                           -> the lint: structure, statuses, prose
  pp-plan.py repair                          -> the mechanical findings mended and said --
                                                a node open over children all done closes --
                                                the others said with their gesture

An ADDRESS is bare names -- `memo/core/storage` -- never the numbered folders.
Every mutating call ends by SAYING the plan's next move: a `::push` line the
conductor collects into the NEXT (a `::clear` once the plan is done).

Anything unresolved refuses by name -- exit 2, nothing written: not-an-instance,
path-unknown, section-unknown, node-unframed, template-unknown, template-invalid,
template-missing, family-foreign, address-malformed, item-line-malformed, item-engaged, item-missing, item-is-node, done-invalid, slug-taken, name-invalid, kind-mismatch, code-unknown,
prose-missing, prose-heading, section-ambiguous, section-kept, material-undeclared, frontmatter-malformed,
documents-none, argument-missing, argument-unexpected, verb-unknown.
Writes go through the engine's one write regime: atomic replace. No network, ever.

The conductor plays this skill: an agent reaches it as `./pp <key> -s pp-plan ...`,
and pp runs it with its own interpreter -- what the engine depends on, it may depend on.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
import contextlib
from pathlib import Path
from types import SimpleNamespace

import yaml

STATUSES = ("todo", "doing", "done", "blocked", "redo")
ENGAGED = ("doing", "redo", "blocked")   # started work, whatever its kind --
                                         # what a closed ancestor would hide
MODEL_KEYS = ("slug", "template", "plan", "status", "created", "material")
                                         # `template`: the template the node is an instance of;
                                         # `material`: the tree the node's rows read from, emitted
                                         # after `created` when the plan declares one, absent otherwise
ITEM = re.compile(r"^item\.(\d+)$")   # the ONE child grammar, whatever the kind
FOREIGN = "_foreign"   # internal vehicle only -- never a key written to a document
WRITING = ("section", "done", "block", "move", "rename", "constrain", "serve", "material")
                                         # the verbs that WRITE: they play under the plan's lock
READING = Path(__file__).resolve().parents[2] / "procs" / "PLANS-TEMPLATES.md"
                                         # the reading of the templates, mounted last in every chain
ROOT_TEMPLATE = "plan"                   # the template a plan is born on when `--template` names none
TEMPLATES = Path(__file__).resolve().parents[2] / "templates"   # the product's templates, `<name>.md`
TREE_TEMPLATES = "_templates"            # under a tree's `plans/`: that tree's own templates, read
                                         # first -- no slug opens on `_`, so no plan is named so
HARD = ("Items", "Delivery")             # the two sections every template carries: the children and
                                         # the log; placed last, in this order, when it does not place them
DECLARED = ("doing", "redo")             # the only statuses a template's `statuses` names
SERVING = ("served", "unserved")         # the mark a line of `sections` may end on: served at the mount or not
ITEM_LINE = re.compile(r"^- ([a-z0-9][a-z0-9-]*) -- (.+?)\s*$")   # one prepared item
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")     # a node's name: kebab-case, the slugs' own grammar
LAW = re.compile(r"^\s\s([A-Z][A-Z0-9]*?[0-9]+)\s\s(.*)$")   # `  KX1  text` -- a posed law, the
                                                            # engine writer's own grammar
USAGE = {
    "section": "section <address> <Name> [--append]   (the prose on stdin, `-` marks it) | "
               "section <slug> <first section> --template <name>   (a plan born on that template) | "
               "section <address of a leaf> Delivery --item <todo>   (the todo delivered) | "
               "section <address> <Name> --remove[=<n>]   (no stdin) | "
               "section <slug> <first section> --shared   (the plan born under the run's root of documents)",
    "done": "done <address>   (a todo of a leaf, a node or a prepared item, closed by hand)",
    "block": "block <address> <reason ...>",
    "move": "move <src-address> <dst-parent-address> <index>",
    "rename": "rename <address> <new-name>",
    "mount": "mount <address> [--whole]   (--whole: every ancestor's body whole too)",
    "constrain": "constrain <address> [<prefix>] --section production|behavior   (laws on stdin; "
                 "a line opening on a posed code replaces it) | constrain <address> --retire <code>",
    "serve": "serve <address> <token ...> | serve <address> -   (the rows on stdin) -- a token is "
             "DOC, 'DOC[start..end]' (quoted here, bare on stdin) or, as a last resort, DOC[x-y,...]",
    "material": "material <slug> [<name> [<path>]|- [<name>]]   (the slug by default; a path declares the tree "
                "in the plan's `materials:`; `-` takes the key out everywhere, `- <name>` withdraws one declaration)",
    "next-move": "next-move",
    "verify": "verify   (the vector on stdin -- the engine's call, never the agent's)",
    "status": "status [<slug>] [--all] [--engaged] [--json]   (without a slug: --all the closed plans too, "
              "--engaged each open plan's doing, redo and blocked nodes under it)",
    "templates": "templates [--json]   (the templates the tree sees, its own first, then the product's)",
    "check": "check",
    "repair": "repair",
}
ARITY = {"section": (2, 2), "done": (1, 1), "block": (2, None), "move": (3, 3), "rename": (2, 2),
         "mount": (1, 1),
         "constrain": (1, 4), "serve": (2, None), "material": (1, 3), "next-move": (0, 0), "verify": (0, 0),
         "status": (0, 1), "templates": (0, 0),
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


def shared_root(home: Path) -> Path | None:
    """-> the ROOT OF DOCUMENTS of the run `PP_RUN` names -- the second tree of plans, under
    `<root>/plans/` -- read at the run's slot through the engine's face; None without a run,
    without its slot, or for a run opened with no root. The ONE site that reads it: no verb
    deduces a root from anything else."""
    engine = conductor()
    key = os.environ.get(engine.context.VARIABLE, "").strip()
    if not key:
        return None
    found = engine.persistence.documents_of(engine.persistence.slot_of(home, key))
    return Path(found).resolve() if found else None


def trees(home: Path) -> list[Path]:
    """-> the trees a plan may live in: the instance first, the run's root of documents second."""
    shared = shared_root(home)
    return [home] if shared is None or shared == home.resolve() else [home, shared]


def doubles(home: Path) -> dict[str, list[Path]]:
    """-> {slug: [its directory in the instance, its directory under the run's root]} for every plan
    whose `PLAN.md` stands in BOTH trees -- a copy, a plan born before the root: neither wins."""
    shared = trees(home)[1:]
    if not shared:
        return {}
    return {slug: [home / "plans" / slug, shared[0] / "plans" / slug]
            for slug in sorted(plans_in(home) & plans_in(shared[0]))}


def twice_said(slug: str, both: list[Path]) -> str:
    """-> the one line a double is said by, at `check` and `next-move`."""
    return (f"{slug}: plan-twice -- plans/{slug} stands in the instance ({both[0]}) and under "
            f"the run's root of documents ({both[1]})")


def refuse_twice(home: Path, slug: str) -> None:
    """Refuses `plan-twice` when the plan `slug` stands in both trees: nothing is read, nothing written."""
    both = doubles(home).get(slug)
    if both:
        fail("plan-twice", f"plans/{slug} stands in the instance ({both[0]}) and under the run's root "
                           f"of documents ({both[1]}) -- a plan lives in one tree: remove one of the two "
                           "by hand, then play the verb again")


def tree_of(home: Path, slug: str) -> Path:
    """-> the tree the plan `slug` lives in: the one of `trees` where `plans/<slug>/PLAN.md`
    stands; the instance when it stands nowhere, so a refusal keeps its text. A plan that stands
    in BOTH trees refuses `plan-twice`: no tree wins in silence."""
    refuse_twice(home, slug)
    for tree in trees(home):
        if plan_doc(tree, slug) is not None:
            return tree
    return home


def plans_in(tree: Path) -> set[str]:
    """-> the slugs of the plans whose document stands in ONE tree."""
    plans_dir = tree / "plans"
    if not plans_dir.is_dir():
        return set()
    return {one.name for one in plans_dir.iterdir()
            if one.is_dir() and not one.name.startswith("_") and plan_doc(tree, one.name) is not None}



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
    Readers take nothing: the atomic replace keeps every read consistent. The lock file is
    NEVER taken away: a session that waits holds the file it opened, and a file removed
    would let a newcomer lock a new one beside it -- two holders. What needs no lock is
    refused before it (`main`): no lock file is made for a plan that is not there."""
    with regime().held(root / "plans" / slug):
        yield


def judge_prose(prose: str) -> None:
    """A section's prose judged on its own: present, and opening no section of its own -- the
    reader cuts the body at every `## ` line, a code block included."""
    if not prose.strip():
        fail("prose-missing", "a section is written WITH its prose -- pipe it on stdin")
    heading = next((line for line in prose.splitlines() if line.startswith("## ")), None)
    if heading is not None:
        fail("prose-heading", f"`{heading.strip()[:60]}` would open a section of its own -- a "
                              "subtitle inside a section is written `###`")


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


class Unfit(Exception):
    """A template that cannot serve: its refusal code and detail -- `level` says it by `fail`,
    `check` as a finding."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code, self.detail = code, detail


def template_file(tree: Path, name: str) -> Path:
    """-> the file of the template `name`: the tree's own, `<tree>/plans/_templates/<name>.md`,
    else the product's -- a plan reads the templates of the tree it lives in, so a shared plan
    and its templates travel together. REFUSES `template-unknown`."""
    for place in (tree / "plans" / TREE_TEMPLATES, TEMPLATES):
        path = place / f"{name}.md"
        if path.is_file():
            return path
    raise Unfit("template-unknown", f"`{name}` -- no `{name}.md` under {tree / 'plans' / TREE_TEMPLATES} "
                                    "nor among the product's templates")


def level(tree: Path, name: str) -> SimpleNamespace:
    """-> the template `name`, read by `shape_of` -- a template that cannot serve refuses by its code."""
    try:
        return shape_of(tree, name)
    except Unfit as unfit:
        fail(unfit.code, unfit.detail)


def shape_of(tree: Path, name: str, path: Path | None = None) -> SimpleNamespace:
    """-> the template `name` as its FRONT MATTER declares it, read by the engine's reader: its
    `sections` in their order -- Items and Delivery added last when it does not place them -- and
    its `statuses`, the sections whose writing makes a node `doing` and the ones whose rewriting
    reopens a `done` one (`redo`) -- and its place in the chain: `leaf: yes`, its items are things to
    do, or `next: <template>`, its items are instances of that template. Its BODY is the agent's: the script takes from it the title of
    the level and the guidance a section holds until it is written, never a section nor a status.
    REFUSES `template-invalid`: an unreadable front, no section, a name twice, a status other
    than doing or redo, a status twice, a section a status names that the template does not
    carry, Delivery among the statuses, neither or both of `leaf` and `next`. `path` reads that file as
    the template `name`, the one the tree would read otherwise."""
    path = path or template_file(tree, name)
    engine = conductor()
    try:
        front = engine.reading.read(path).front
    except engine.Refusal as refusal:
        raise Unfit("template-invalid", f"{path}: {str(refusal).split(' — ', 1)[-1]}")

    def invalid(detail: str) -> None:
        raise Unfit("template-invalid", f"{path}: {detail}")

    names, hidden = [], []
    for line in str(front.get("sections") or "").split("\n"):
        # a section line is its name, then -- two spaces apart -- `served` (the default) or
        # `unserved`: whether the node's mount serves it
        words = re.split(r"\s{2,}", line.strip())
        if not words[0]:
            continue
        named, mark = words[0], (words[1] if len(words) > 1 else "served")
        if len(words) > 2 or mark not in SERVING:
            invalid(f"section line `{line.strip()}` -- a name, then `served` or `unserved`, two spaces apart")
        names.append(named)
        if mark == "unserved":
            hidden.append(named)
    if not names:
        invalid("`sections` declares no section -- one section name per line")
    for twice in sorted({one for one in names if names.count(one) > 1}):
        invalid(f"section `{twice}` declared twice")
    for one in HARD:
        if one not in names:
            names.append(one)
    declared: dict[str, tuple[str, ...]] = {}
    for line in str(front.get("statuses") or "").split("\n"):
        words = line.split()
        if not words:
            continue
        status, named = words[0], tuple(words[1:])
        if status not in DECLARED:
            invalid(f"status `{status}` -- a template declares `doing` and `redo` alone")
        if status in declared:
            invalid(f"status `{status}` declared twice")
        if not named:
            invalid(f"status `{status}` names no section")
        for one in named:
            if one not in names:
                invalid(f"status `{status}` names `{one}`, a section the template does not carry")
            if one == "Delivery":
                invalid("Delivery makes no status a template declares -- it closes a batch whose items are done")
        declared[status] = named
    shows = tuple(one.strip() for one in str(front.get("shown") or "").split("\n") if one.strip())
    for one in shows:
        if one not in names:
            invalid(f"`shown` names `{one}`, a section the template does not carry")
    leaf = front.get("leaf") in (True, "yes")
    after = str(front.get("next") or "").strip() or None
    if leaf == (after is not None):
        invalid("a template says `leaf: yes` or `next: <template>` -- one of the two")
    if after is not None:
        template_file(tree, after)          # a chain that leads nowhere refuses template-unknown
    text = path.read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1] if "\n---\n" in text else ""
    return SimpleNamespace(name=name, path=path, sections=tuple(names), body=body, leaf=leaf, next=after, shown=shows,
                           served=tuple(one for one in names if one not in hidden),
                           doing=declared.get("doing", ()), redo=declared.get("redo", ()))


def templates(home: Path) -> list[dict]:
    """-> every template the instance's tree sees, READ-ONLY: its own (`plans/_templates/`) first, then
    the shared root's when the run has one, then the product's -- by name in each. One object each: its
    `name`, its `origin` (`tree`, `shared` or `product`), its `description`, `leaf` and the `chain` it
    opens (itself, then each `next:` down to the leaf, read in the tree that sees it), its `sections` in
    their order; a template that cannot serve carries its `refusal` (`code`, `detail`) instead."""
    places = [(home, "tree", home / "plans" / TREE_TEMPLATES)]
    shared = shared_root(home)
    if shared is not None:
        places.append((shared, "shared", shared / "plans" / TREE_TEMPLATES))
    places.append((home, "product", TEMPLATES))
    found: list[dict] = []
    engine = conductor()
    for tree, origin, place in places:
        for path in sorted(place.glob("*.md")) if place.is_dir() else []:
            name = path.stem
            one: dict = {"name": name, "origin": origin}
            try:
                description = engine.reading.read(path).front.get("description")
            except engine.Refusal:               # an unreadable front: the shape says its refusal below
                description = None
            one["description"] = str(description).strip() if description else None
            if origin == "product" and (tree / "plans" / TREE_TEMPLATES / path.name).is_file():
                one["shadowed"] = True           # the tree's own of that name is the one read
            try:
                head = shape = shape_of(tree, name, path)
                chain = [name]
                while not shape.leaf:
                    if shape.next in chain:
                        raise Unfit("template-invalid", f"the chain loops back on `{shape.next}`")
                    chain.append(shape.next)
                    shape = shape_of(tree, shape.next)
                one.update(leaf=head.leaf, chain=chain, sections=list(head.sections))
            except Unfit as unfit:
                one["refusal"] = {"code": unfit.code, "detail": unfit.detail}
            found.append(one)
    return found


def templates_text(found: list[dict]) -> str:
    """-> the templates said one line each: name, origin, `leaf` or the chain, the sections, the
    description -- or the refusal."""
    lines = []
    for one in found:
        head = f"{one['name']}  {one['origin']}" + ("  shadowed" if one.get("shadowed") else "")
        if "refusal" in one:
            lines.append(f"{head}  {one['refusal']['code']} -- {one['refusal']['detail']}")
            continue
        shape = "leaf" if one["leaf"] else " -> ".join(one["chain"])
        lines.append(f"{head}  {shape}  [{' '.join(one['sections'])}]  -- {one['description'] or 'no description'}")
    return "\n".join(lines)


def template_name(front: dict) -> str:
    """-> the template the node names. A node without one is a document of the form before the
    templates -- `kind:` at its front --: REFUSES `template-missing`; the migration script of the
    re-pin rewrites the key, never this script."""
    name = front.get("template")
    if not name:
        fail("template-missing", f"`{front.get('slug')}` names no template -- a node of the form before "
                                 "the templates: the migration script of the re-pin rewrites it")
    return str(name)


def level_of(tree: Path, front: dict) -> SimpleNamespace:
    """-> the template a born node names, read in the tree it lives in."""
    return level(tree, template_name(front))


def render(tree: Path, name: str, prose: str | None, foreign: str = "", **names: str) -> str:
    """-> the text of a node born on the template `name`: the front the script writes (the model's
    keys, then `foreign`), the title the template gives -- its holes `{slug}`, `{plan}`, `{parent}`
    filled -- and `prose` as the template's FIRST section, the title alone when `prose` is None.
    Nothing else of the template's body is copied: the body is the method of the level, read at
    the mount."""
    shape = level(tree, name)
    front = {"slug": names["slug"], "template": name}
    front.update({key: names[key] for key in ("plan", "material") if names.get(key)})
    front.update(status="todo", created=datetime.now(timezone.utc).date().isoformat())
    front[FOREIGN] = foreign
    title = next((one for one in shape.body.splitlines() if one.startswith("# ")), f"# {names['slug']}")
    for key in ("slug", "plan", "parent"):
        # plain replace, never str.format: prose and slugs may carry braces
        title = title.replace("{" + key + "}", names.get(key, ""))
    if prose is None:
        return emit(front, f"\n{title}\n\n")
    return emit(front, f"\n{title}\n\n## {shape.sections[0]}\n\n{prose.strip()}\n\n")


def owned(tree: Path, front: dict, line: str) -> bool:
    """-> whether a title line is the one the node's template owns: it opens on the same first
    word as the template's title (`# BATCH`); any other title is the author's, left free."""
    word = (title_of(tree, front).split()[1:2] or [""])[0]
    return bool(word) and re.match(rf"^# {re.escape(word)}\b", line) is not None


def title_of(tree: Path, front: dict, parent: str = "") -> str:
    """-> the title line the node's template gives this front matter, `parent` the name of the
    node above it."""
    line = next(one for one in level_of(tree, front).body.splitlines() if one.startswith("# "))
    for key, value in (("slug", front.get("slug", "")), ("plan", front.get("plan", "")), ("parent", parent)):
        line = line.replace("{" + key + "}", str(value))
    return line


def title_line(body: str) -> str | None:
    """-> the body's title: its first `# ` line before the first section, None when absent."""
    for line in body.splitlines():
        if line.startswith("## "):
            return None
        if line.startswith("# "):
            return line
    return None


def titled(tree: Path, front: dict, body: str, parent: str = "") -> str:
    """-> the body carrying the title its front matter gives: a level title set, a missing one
    inserted, a free title kept -- every other line byte for byte."""
    lines = body.splitlines(keepends=True)
    for at, line in enumerate(lines):
        if line.startswith("## "):
            break
        if line.startswith("# "):
            if owned(tree, front, line):
                lines[at] = title_of(tree, front, parent) + ("\n" if line.endswith("\n") else "")
            return "".join(lines)
    lead = len(body) - len(body.lstrip("\n"))
    return body[:lead] + title_of(tree, front, parent) + "\n\n" + body[lead:]


def node_file(template: str) -> str:
    """-> the file name of a node on `template`: the template's name in capitals."""
    return f"{template.upper()}.md"


def node_in(tree: Path, folder: Path) -> Path | None:
    """-> the node document a folder holds: the one `<NAME>.md` whose name, in small letters,
    is a template the tree sees; None when it holds none. REFUSES `node-twice` for two."""
    found = []
    for one in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        if one.stem != one.stem.upper() or not NAME.fullmatch(one.stem.lower()):
            continue
        try:
            template_file(tree, one.stem.lower())
        except Unfit:
            continue
        found.append(one)
    if len(found) > 1:
        fail("node-twice", f"{folder} holds {', '.join(one.name for one in found)} -- a folder holds one node")
    return found[0] if found else None


def plan_doc(tree: Path, slug: str) -> Path | None:
    """-> the document of the plan `slug` in one tree, None when no plan of that name is born there."""
    return node_in(tree, tree / "plans" / slug)


def doc_of(root: Path, *segments: str, template: str | None = None) -> Path:
    """-> the document a node path addresses: plans/<slug>[/<n>-<name>...], at any depth.

    The caller addresses by BARE names; the folders on disk are INDEXED (`<n>-<name>`),
    DERIVED parent by parent from the item entries. The FILE is named after the node's
    template: the plan's own, found in its folder -- `template` names it for a plan not
    born yet, the root template otherwise --, then each child's, the `next:` of its
    parent's. An address deeper than the chain, or under a leaf, refuses `path-unknown`."""
    path = root / "plans" / segments[0]
    doc = plan_doc(root, segments[0])
    if doc is None:
        doc = path / node_file(template or ROOT_TEMPLATE)
        if len(segments) > 1:
            fail("path-unknown", f"plans/{segments[0]} is not born -- no plan of that name stands")
    for depth, name in enumerate(segments[1:], 1):
        if not doc.is_file():
            fail("path-unknown", f"{'/'.join(segments[:depth])} has no document")
        front, _ = read(doc)
        shape = level_of(root, front)
        if shape.leaf:
            fail("path-unknown", f"{'/'.join(segments[:depth])} is a leaf -- its items are things to do, "
                                 f"never nodes: `{name}` has no document")
        position = next((i for i, (child, _) in enumerate(children(front), 1)
                         if child == name), None)
        if position is None:
            if re.match(r"^\d+-", name):
                bare = "/".join(segments[:depth]) + "/" + name.split("-", 1)[1]
                fail("path-unknown", f"`{name}` is a FOLDER -- address the node by its bare name: {bare}")
            fail("path-unknown", f"{'/'.join(segments[:depth + 1])} has no entry -- prepare it in "
                                 f"its parent's Items first (`- {name} -- <brief>`)")
        path = path / f"{position}-{name}"
        doc = path / node_file(shape.next)
    return doc


def template_at(root: Path, segments: list[str], template: str | None = None) -> str:
    """-> the template of the node `segments` addresses, born or not: its own when born, the plan's
    `template` (the root template by default) for a plan to be born, its parent's `next:` else."""
    path = doc_of(root, *segments, template=template)
    if path.is_file():
        return template_name(read(path)[0])
    if len(segments) == 1:
        return template or ROOT_TEMPLATE
    return level_of(root, read(doc_of(root, *segments[:-1]))[0]).next


def address_of(plans_dir: Path, doc: Path) -> list[str]:
    """-> the bare address of a node document: its folders under `plans/`, indexes dropped."""
    parts = doc.parent.relative_to(plans_dir).parts
    return [parts[0]] + [one.split("-", 1)[1] for one in parts[1:]]


def walk(root: Path, segments: list[str]) -> list[list[str]]:
    """-> the address of every BORN node under the node `segments`, itself first, in item order."""
    found, doc = [segments], doc_of(root, *segments)
    front = read(doc)[0]
    if level_of(root, front).leaf:
        return found
    for child, _ in children(front):
        if doc_of(root, *segments, child).is_file():
            found += walk(root, segments + [child])
    return found


def new(tree: Path, slug: str, prose: str, home: Path, template: str = ROOT_TEMPLATE) -> Path:
    """Births a plan in `tree` -- the instance, or the run's root of documents under
    `--shared`: its directory and its PLAN.md, prose aboard, no phase yet. A slug that
    stands in ANY tree refuses: no plan is born in the shadow of another."""
    for where in trees(home):
        if (where / "plans" / slug).exists():
            fail("slug-taken", f"plans/{slug} already stands"
                               f"{' in the shared root' if where != home else ''} -- a slug is born once")
    spot = tree / "plans" / slug
    spot.mkdir(parents=True)
    path = spot / node_file(template)
    path.write_text(render(tree, template, prose, slug=slug), encoding="utf-8")
    return path


FAMILY = "plan"   # the one family this package declares: `plan:<address>`, at every depth


def verify(home: Path, vector: str) -> None:
    """This package's VERIFIER, the engine's call at every entry and service of the bus:
    a `plan:<address>` vector is valid when its address -- the bare names every verb takes,
    as deep as the plan's chain of templates goes -- RESOLVES in a tree, the instance's or
    the shared root's: a plan born, a node under it born or PREPARED (an entry of its
    parent's Items, no document yet). A family other than `plan` is not this package's to
    judge (`family-foreign`); an empty address or an empty name refuses `address-malformed`;
    an address that resolves nowhere refuses with the resolver's own reason
    (`path-unknown`). READ-ONLY, no lock: exit 2 says no.

    documentary: the frontier's next node is often prepared, not born -- a run's vector may
    point at it, so the entry is the node, whatever its birth."""
    prefix, _, address = vector.strip().partition(":")
    if prefix != FAMILY:
        fail("family-foreign", f"`{prefix}:` is not a family plan declares ({FAMILY}:); its owner verifies it")
    segments = address.split("/") if address else []
    if not segments or not all(segments):
        fail("address-malformed", f"`{vector}` -- a plan's node is addressed by its bare names: "
                                  "<slug>/<name>/..., none empty")
    root = tree_of(home, segments[0])
    if len(segments) == 1:
        if plan_doc(root, segments[0]) is None:
            fail("path-unknown", f"plans/{segments[0]} is not born -- no plan of that name stands")
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


def is_written(name: str, body: str) -> bool:
    """A section is WRITTEN once it stands with text under its heading."""
    text = section_text(body, name)
    return text is not None and text.strip() != ""


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


def birth(root: Path, segments: list[str]) -> Path:
    """Births a PREPARED item of a branch: the entry stands at the parent, the folder is born
    at the entry's position, the document on the parent's `next:` template, its title alone --
    the first section written on a prepared item is what calls this, and that section is the
    node's first prose: the parent's Items line stays the parent's."""
    path = doc_of(root, *segments)            # refuses path-unknown without the entry
    names = {"slug": segments[-1], "plan": segments[0], "parent": segments[-2]}
    # the plan's material travels to every node born under it: a node is mounted on
    # its own, never through its plan, so each document carries the key itself
    names["material"] = str(read(doc_of(root, segments[0]))[0].get("material") or "")
    text = render(root, template_at(root, segments), None, **names)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def declared_in(path: Path, front: dict | None = None) -> list[tuple[str, str]]:
    """-> the trees ONE document declares, (name, path as written) in the order written: its
    `materials:` block, read by the engine's own reader (`reading.materials`) -- one grammar
    for the writer and the mount; a block badly written raises the reader's Refusal
    (`material-invalid`), which `refused` turns into the script's refusal."""
    front = read(path)[0] if front is None else front
    return list(conductor().reading.materials(SimpleNamespace(front=front, name=path.name)))


def refused(call):
    """-> what `call` answers; a Refusal of the engine's refuses here by its own code."""
    engine = conductor()
    try:
        return call()
    except engine.Refusal as refusal:
        fail(refusal.code, str(refusal).split(" — ", 1)[-1])


def chain_docs(path: Path) -> list[Path]:
    """-> the node's document and its ancestors' up to its plan's, the nearest first --
    the documents a row of the node looks its tree up in, as the mount stacks them."""
    docs, folder = [path], path.parent
    plans_dir = next(one for one in path.parents if one.name == "plans")
    while folder.parent != plans_dir:
        folder = folder.parent
        above = node_in(plans_dir.parent, folder)
        if above is not None:
            docs.append(above)
    return docs


def trees_of(path: Path, lenient: bool = False) -> dict[str, Path]:
    """-> name -> the tree on disk, for every name the node's chain declares: the NEAREST
    declaration wins, its relative path read from the folder of the document that declares
    it -- never from the reader's workspace, so two instances read one tree. A block badly
    written raises the reader's Refusal; `lenient` (the lint, which says that block at its own
    document) reads it as declaring nothing."""
    found: dict[str, Path] = {}
    for doc in chain_docs(path):
        try:
            pairs = declared_in(doc)
        except conductor().Refusal:
            if not lenient:
                raise
            pairs = []
        for name, written in pairs:
            if name not in found:
                tree = Path(os.path.expanduser(written))
                found[name] = tree if tree.is_absolute() else Path(os.path.normpath(doc.parent / tree))
    return found


def _block(front: dict) -> tuple[list[str], list[str], int | None]:
    """-> (the `materials:` block's lines as written, stripped -- `#` lines and declarations alike;
    the other foreign lines; where the block stood among them, None without one)."""
    block, keep, at, inside = [], [], None, False
    for line in front.get(FOREIGN, "").splitlines(keepends=True):
        if line[:1] not in (" ", "\t") and ":" in line:
            inside = line.split(":", 1)[0].strip() == "materials"
            if inside:
                at = len(keep)
                continue
        if inside:
            if line.strip():
                block.append(line.strip())
            continue
        keep.append(line)
    return block, keep, at


def _named(line: str) -> str | None:
    """-> the name a block line declares, None for a `#` line."""
    return None if line.startswith("#") else line.partition(":")[0].strip()


def _rewrite(front: dict, block: list[str], keep: list[str], at: int | None) -> None:
    """Puts the block back where it stood, its lines in their order -- no block at all once
    no line is left."""
    if block:
        keep.insert(len(keep) if at is None else at, "materials: |\n" + "".join(f"  {one}\n" for one in block))
    front[FOREIGN] = "".join(keep)


def declare(front: dict, name: str, written: str) -> None:
    """Writes `<name>: <written>` in the front's `materials:` block -- a name declared already
    has its line rewritten in place, a new one goes last; the `#` lines and the other foreign
    keys stay as written."""
    block, keep, at = _block(front)
    line = f"{name}: {written}"
    block = ([line if _named(one) == name else one for one in block] if any(_named(one) == name for one in block)
             else block + [line])
    _rewrite(front, block, keep, at)


def undeclare(front: dict, name: str) -> bool:
    """Takes the line of `<name>` out of the front's `materials:` block, every other line kept;
    -> whether the name was declared there."""
    block, keep, at = _block(front)
    if not any(_named(one) == name for one in block):
        return False
    _rewrite(front, [one for one in block if _named(one) != name], keep, at)
    return True


def withdraw(root: Path, slug: str, name: str) -> Path:
    """`material <slug> - <name>`: the declaration of `<name>` leaves the PLAN.md's
    `materials:` block, and nothing else changes -- a node that still names it is said by
    `check` (material-undeclared). An absent name refuses material-undeclared, nothing
    written. -> the plan document."""
    if "/" in slug:
        fail("kind-mismatch", f"a tree is declared by the plan: {USAGE['material']}")
    path = standing(root, [slug])
    front, body = read(path)
    if not undeclare(front, name):
        fail("material-undeclared", f"`{name}` is no tree of plan {slug} -- nothing to withdraw")
    write(path, front, body)
    return path


def material(root: Path, slug: str, name: str | None, written: str | None = None) -> tuple[str | None, list[Path]]:
    """Writes the plan's MATERIAL -- `material: <name>`, the tree its rows read from -- on
    the plan document and on every phase and batch born under it; the plan's slug when no
    name is given (one plan, one branch, its slug), `-` takes the key out everywhere and
    keeps the declaration. A TREE is the plan's own: `<path>` declares `<name>: <path>` in
    the PLAN.md's `materials:` block, the path kept as given -- absolute, or relative to the
    plan's folder, the way the engine reads it --; without a path the name must be declared
    there already. No tree is called `repo` or `work`: neither is declared nor chosen -- a plan
    whose rows read each run's own tree, or the reader's repository, names no material (`-`).
    No SETTINGS is read. Every refusal fires before the first write.
    -> (the name written, None when taken out; the documents written)"""
    if "/" in slug:
        fail("kind-mismatch", "a material is the plan's -- every node born under it carries it: "
                              f"{USAGE['material']}")
    path = standing(root, [slug])
    engine = conductor()
    retired = engine.settings.RETIRED_MATERIALS
    chosen = None if name == "-" else (slug if name is None else name)
    if written is not None:
        if chosen in retired:
            fail("material-invalid", f"no tree is called `{chosen}` -- give the tree a name of its own: "
                                     f"`material {slug} <name> {written.strip()}`")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", chosen) or not written.strip():
            fail("material-invalid", f"`{chosen}: {written}` -- a tree is `<name> <path>`, the name one "
                                     "word of letters, digits, `.`, `_` or `-`")
    front, body = read(path)
    if written is not None:
        declare(front, chosen, written.strip())
        # the engine's reader judges the block as it will stand, before anything is written
        refused(lambda: declared_in(path, yaml.safe_load(front[FOREIGN]) or {}))
    elif chosen in retired:
        fail("material-undeclared", f"no tree is called `{chosen}` -- a plan names a tree it declares "
                                    f"(`material {slug} <name> <path>`), or none: `material {slug} -`, and "
                                    "its rows read the run's own tree, or the repository")
    elif chosen is not None and chosen not in dict(refused(lambda: declared_in(path))):
        fail("material-undeclared", f"`{chosen}` is no tree of plan {slug} -- declare it: "
                                    f"`material {slug} {chosen} <path>`, then play the verb again")
    documents = [doc_of(root, *one) for one in walk(root, [slug])]
    for document in documents:
        front, body = (front, body) if document == path else read(document)
        if chosen is None:
            front.pop("material", None)
        else:
            front["material"] = chosen
        write(document, front, body)
    return chosen, documents


def unmarked(row: list[str]) -> bool:
    """-> whether a serve row names a document without a material mark: a token that is
    neither a nature (`code:`) nor a mark (`@<name>`), and no mark anywhere on the row."""
    tokens = [one for one in row if one]
    return (any(not one.endswith(":") and not one.startswith("@") for one in tokens)
            and not any(one.startswith("@") for one in tokens))


BUDGET_KEY = "plan_serve_budget"     # the instance decides; the package says the default


def weighed(home: Path, name: str, material: str, engine, trees: dict[str, Path] | None = None) -> Path | None:
    """-> the file a serve token's name reads, as the mount will find it: a PATH whose row or
    node names a material is read in that tree and in no other -- the tree the node's chain
    declares (`trees`, from `trees_of`); a path that names none the repository's, else the
    instance's; a bare NAME the instance's. None when no file stands -- the row passes: the
    mount says a reading its tree lacks. The run's own tree is known to the run alone: a
    row that names no material weighs at the repository."""
    workspace = home.parent
    if "/" in name and material:
        tree = (trees or {}).get(material)
        return tree / name if tree is not None and (tree / name).is_file() else None
    candidates = ([workspace / name] if "/" in name else []) + [engine.instance.resolve(home, name)]
    return next((one for one in candidates if one.is_file()), None)


def heavy(home: Path, path: Path, rows: list[list[str]], engine) -> None:
    """Refuses `serve-heavy`, before anything is written, a token WITHOUT a range whose file
    weighs more characters than `plan_serve_budget`: heavy code serves by ranges -- its
    function or section tags --, a light file whole. A token with a range, a file absent, a
    budget below 1 pass as today; a token the grammar refuses is the writer's to judge."""
    face = engine.settings
    try:
        budget = int(face.of(home).of_package(BUDGET_KEY, face.default_of(home, BUDGET_KEY)) or 0)
    except (ValueError, engine.Refusal):
        budget = 0
    if budget < 1:
        return
    declared = str(read(path)[0].get("material") or "")
    trees = refused(lambda: trees_of(path))
    for row in rows:
        tokens = [one for one in row if one]
        if tokens and tokens[0].endswith(":") and tokens[0][:-1] in face.SERVE_NATURES:
            tokens = tokens[1:]
        marks = [one[1:] for one in tokens if one.startswith("@")]
        material = marks[0] if marks else declared
        for token in tokens:
            if token.startswith("@"):
                continue
            try:
                name, cut = engine.core.tokens.parse(token)
            except engine.Refusal:
                continue
            found = None if cut else weighed(home, name, material, engine, trees)
            size = len(found.read_text(encoding="utf-8", errors="replace")) if found else 0
            if size > budget:
                fail("serve-heavy", f"`{token}` weighs {size} characters, over the budget of {budget} "
                                    f"(`{BUDGET_KEY}`) -- serve it by ranges on its function or section "
                                    f"tags, `{name}[<start>..<end>]`, or by lines, `{name}[x-y]`")


def derive_items(front: dict, lines: list[tuple[str, str]], leaf: bool, home: Path) -> None:
    """The Items section is the SOURCE of the child block: the entries follow the
    lines -- a new slug enters `todo`, a known one keeps its status and takes the
    line's rank, a slug gone leaves only while it is still `todo` and, under a
    branch, unborn (item-engaged otherwise). Nothing is written here:
    the caller writes the document once, the front matter with the section."""
    existing = dict(children(front))
    kept = {one for one, _ in lines}
    for slug, status in existing.items():
        if slug in kept:
            continue
        born = not leaf and any(
            d.is_dir() and re.fullmatch(rf"\d+-{re.escape(slug)}", d.name) for d in home.iterdir())
        if status != "todo" or born:
            fail("item-engaged", f"`{slug}` is {status}{' and born' if born else ''} -- an item "
                                 "leaves Items only while it is todo and unborn")
    for key in [k for k in front if isinstance(k, str) and ITEM.match(k)]:
        del front[key]
    for position, (slug, _) in enumerate(lines, 1):
        front[f"item.{position}"] = f"{slug}  {existing.get(slug, 'todo')}"


def write_section(root: Path, segments: list[str], name: str, prose: str,
                  append: bool = False, home: Path | None = None,
                  template: str | None = None, item: str | None = None) -> tuple[Path, list[str], list[str]]:
    """Writes ONE named section of a node's body -- the agent's prose through the
    script, never an editor. The sections are the ones the node's TEMPLATE declares,
    in its order; a name it does not declare refuses `section-unknown`. A standing
    section has its content REPLACED, an absent one is INSERTED at its rank; Delivery,
    the log, or the flag APPENDS. The first write on a PREPARED item births it on its
    level's template, its title and the section written alone -- the parent's Items line
    is not copied; a plan is born by its template's first section. Items derives the child entries. The
    STATUS follows the template's `statuses`: a `doing` section written on a node not
    yet framed makes it `doing`; a `redo` section rewritten on a `done` node reopens
    it first (`redo`, the ancestry rises); any section written on a `blocked` node
    lifts it. On a LEAF, Delivery delivers one item (`item`): its entry is appended and the
    item turns `done`; on a branch, Delivery is a journal that moves nothing. A node is
    `done` once all its items are, whatever closed the last one, and the closing rises. `root` is the tree the node lives in, `home` the instance
    (the tree itself when not given): a birth judges its slug against every tree;
    `template` names the template a plan is born on, the root template by default.
    -> (path, what the write did, the status lines the console says)"""
    judge_prose(prose)
    path = doc_of(root, *segments, template=template)
    kind = template_at(root, segments, template)
    said: list[str] = []
    if not path.is_file():
        first = level(root, kind).sections[0]
        if len(segments) == 1:
            if name != first:
                fail("path-unknown", f"plans/{segments[0]} is not born -- its first section, {first}, births it")
            new(root, segments[0], prose, home or root, kind)
            if name in level(root, kind).doing:
                # born by a section that frames: the plan is doing at once
                set_status(root, segments, "doing")
                return path, ["born"], [f"pp-plan: {segments[0]} -> doing"]
            return path, ["born"], []
        shape = level(root, kind)
        if name not in shape.sections:
            fail("section-unknown", f"`{name}` is no section of the template `{kind}` -- "
                                    f"{', '.join(shape.sections)}")
        if name == "Delivery":
            # every refusal before the birth: a prepared item is not framed, it delivers nothing
            fail("node-unframed", f"{'/'.join(segments)} is not framed -- write one of its `doing` sections "
                                  f"first: {', '.join(shape.doing) or 'none declared'}")
        birth(root, segments)
        said.append("born")
    front, body = read(path)
    shape = level_of(root, front)
    order = shape.sections
    if name not in order:
        fail("section-unknown", f"`{name}` is no section of the template `{shape.name}` -- {', '.join(order)}")
    if name == "Delivery" and front.get("status") == "todo":
        fail("node-unframed", f"{'/'.join(segments)} is not framed -- write one of its `doing` sections "
                              f"first: {', '.join(shape.doing) or 'none declared'}")
    if item is not None and name != "Delivery":
        fail("argument-unexpected", "--item names the item a Delivery delivers -- on Delivery alone")
    if name == "Delivery" and not shape.leaf and item is not None:
        fail("item-is-node", f"{'/'.join(segments)} is a branch -- its items are nodes, closed by their own "
                             "items; its Delivery is a journal, written without --item")
    if name == "Delivery" and shape.leaf and item is None:
        fail("item-missing", f"{'/'.join(segments)} is a leaf -- its Delivery delivers one item: "
                             "--item <slug>")
    if item is not None and item not in [child for child, _ in children(front)]:
        fail("path-unknown", f"`{item}` is no item of {'/'.join(segments)}")
    moves: list[str] = []
    if name in shape.redo and front.get("status") == "done":
        # the rework opens on the node's own history: the reopen walk, then the write
        reopen(root, segments)
        moves.append(f"pp-plan: {'/'.join(segments)} -> redo -- the rework is open")
        front, body = read(path)
    lines = item_lines(prose) if name == "Items" else None
    if lines is not None and append and is_written("Items", body):
        written = item_lines(section_text(body, "Items") or "")
        taken = sorted({slug for slug, _ in lines} & {slug for slug, _ in written})
        if taken:
            fail("slug-taken", f"{', '.join(taken)} -- already a line of Items; --append adds new names")
        lines = written + lines
    if lines is not None:
        derive_items(front, lines, shape.leaf, path.parent)
    if item is not None:
        prose = f"- {item} -- {prose.strip()}"
    parts = put_section(shape, body, name, prose, append or name == "Delivery", said)
    write(path, front, join_sections(parts))
    if lines is not None and not shape.leaf:
        reindex(path.parent, front)
    status = front.get("status")
    if item is not None:
        # the entry delivers its item: the item turns done, the leaf with its last one
        moves += said_closing("/".join(segments + [item]), set_status(root, segments + [item], "done"))
        return path, said, moves
    if name in shape.doing and status in ("todo", "blocked"):
        set_status(root, segments, "doing")
        moves.append(f"pp-plan: {'/'.join(segments)} -> doing")
    elif status == "blocked":
        framed = any(is_written(one, join_sections(parts)) for one in shape.doing)
        lifted = "doing" if framed else "todo"
        set_status(root, segments, lifted)
        moves.append(f"pp-plan: {'/'.join(segments)} -> {lifted} -- the block is lifted")
    now = read(path)[0]
    kids = children(now)
    if lines is not None and kids and all(one == "done" for _, one in kids) and now.get("status") != "done":
        # Items rewritten over items all done: the node is done, the closing rises
        closed = set_status(root, segments, "done")
        moves.append(f"pp-plan: {'/'.join(segments)} -> done" + (f" -- closes {', '.join(closed)}" if closed else ""))
    return path, said, moves


def said_closing(address: str, closed: list[str]) -> list[str]:
    """-> the console's lines for `address` turned done and the nodes `closed` with it, deepest
    first: the first one closed says the others it closes."""
    lines = [f"pp-plan: {address} -> done"]
    if closed:
        lines.append(f"pp-plan: {closed[0]} -> done" + (f" -- closes {', '.join(closed[1:])}" if closed[1:] else ""))
    return lines


def put_section(shape: SimpleNamespace, body: str, name: str, prose: str, append: bool,
                said: list[str]) -> list[tuple[str | None, str]]:
    """-> the body's parts with `prose` under `## <name>`: appended to a written section when
    `append`, replacing it otherwise, inserted at the rank the template gives it when absent;
    `said` takes what the write did."""
    parts = split_sections(body)
    names = [one for one, _ in parts]
    block = "\n" + prose.strip() + "\n\n"
    if name in names:
        at = names.index(name)
        if append and is_written(name, body):
            parts[at] = (name, parts[at][1].rstrip("\n") + "\n\n" + prose.strip() + "\n\n")
            said.append("appended")
        else:
            parts[at] = (name, block)
            said.append("replaced")
        return parts
    at, rank = len(parts), shape.sections.index(name)
    for i, (one, _) in enumerate(parts):
        if one is not None and one in shape.sections and shape.sections.index(one) > rank:
            at = i
            break
    parts.insert(at, (name, block))
    said.append("inserted")
    return parts


def remove_section(root: Path, segments: list[str], name: str, nth: int | None) -> tuple[Path, str]:
    """Removes ONE occurrence of a section from a born node's body -- its heading and its
    text, nothing else. The call names the occurrence: a name standing several times
    without a rank refuses, listing each; a section of the node's template standing once is
    kept -- it is rewritten, a log is never erased. No status moves.
    -> (path, what was removed)"""
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
    if name in level_of(root, front).sections and len(at) == 1:
        fail("section-kept", f"`{name}` is a section of the template `{template_name(front)}` and stands once -- rewrite it "
                             "by `section`; a log is never erased")
    removed = parts.pop(at[rank - 1])
    write(path, front, join_sections(parts))
    return path, f"{name} ({rank} of {len(at)}, {len(removed[1].strip())} c)"


def leaf_above(root: Path, segments: list[str]) -> Path | None:
    """-> the document of the born LEAF whose item `segments` names -- a todo --, None when
    the address names a node."""
    if len(segments) < 2:
        return None
    parent = doc_of(root, *segments[:-1])
    if parent.is_file() and level_of(root, read(parent)[0]).leaf:
        return parent
    return None


def done(root: Path, segments: list[str]) -> list[str]:
    """Closes BY HAND what the address names -- the maintenance of a plan: a todo of a leaf
    checked off; a born node closed with its todo items left as they are, a dated line of
    its Delivery naming them; a prepared item of a branch closed without being born. The
    closing rises as for any `done`. A node whose item is under way refuses `item-engaged`:
    the hand closes no work in progress. -> the nodes closed, deepest first."""
    if leaf_above(root, segments) is not None:
        return set_status(root, segments, "done")
    path = doc_of(root, *segments)
    if not path.is_file():
        # a prepared item: its line at the parent closes, nothing is born
        if len(segments) < 2:
            fail("path-unknown", f"plans/{segments[0]} is not born -- no plan of that name stands")
        parent = doc_of(root, *segments[:-1])
        _splice_child(parent, segments[-1], "done")
        return _cascade(root, segments[:-1], "done")
    front, body = read(path)
    if front.get("status") == "done":
        fail("done-invalid", f"{'/'.join(segments)} is done already")
    kids = children(front)
    engaged = [child for child, status in kids if status in ENGAGED]
    if engaged:
        fail("item-engaged", f"{'/'.join(segments)} carries `{'`, `'.join(engaged)}` under way -- close or "
                             "drop it first: the hand closes no work in progress")
    still = [child for child, status in kids if status != "done"]
    if still:
        stamp = datetime.now(timezone.utc).date().isoformat()
        parts = put_section(level_of(root, front), body, "Delivery",
                            f"- {stamp} : closed by hand -- open: {', '.join(still)}", True, [])
        write(path, front, join_sections(parts))
    return set_status(root, segments, "done")


def block(root: Path, segments: list[str], reason: str) -> None:
    """Says a stop: the node is `blocked` and the reason lands as a dated line of its
    Delivery, the log -- the next section written lifts it."""
    if leaf_above(root, segments) is not None:
        fail("path-unknown", f"{'/'.join(segments)} names a todo -- a node blocks")
    path = standing(root, segments)
    set_status(root, segments, "blocked")
    stamp = datetime.now(timezone.utc).date().isoformat()
    front, body = read(path)
    # the line goes in by the section writer alone: a block moves no status beyond its own
    parts = put_section(level_of(root, front), body, "Delivery",
                        f"- {stamp} : blocked -- {' '.join(reason.split())}", True, [])
    write(path, front, join_sections(parts))


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
    path = leaf_above(root, segments)
    if path is not None:
        # an item of a leaf is a todo -- the template says it, never the depth
        front, _ = read(path)
        if segments[-1] not in [c[0] for c in children(front)]:
            fail("path-unknown", f"{segments[-1]} is not among {'/'.join(segments[:-1])}'s todos")
        _splice_child(path, segments[-1], status)   # surgical: the one line moves
        left = [one for _, one in children(read(path)[0]) if one != "done"]
        if status != "done" or left or read(path)[0].get("status") == "done":
            return []
        # its last todo done: the leaf is done, and the closing rises
        return ["/".join(segments[:-1])] + set_status(root, segments[:-1], "done")
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


def items_follow(shape: SimpleNamespace, front: dict, body: str, briefs: dict[str, str]) -> str:
    """-> the body with its Items section rebuilt on the ENTRIES -- the source of the
    entries must say what the entries say after a move: one line per child, its
    brief kept from the standing line, or given, or the bare name; an unwritten
    Items stays as it is."""
    if not is_written("Items", body):
        return body
    known = dict(item_lines(section_text(body, "Items") or ""))
    lines = "\n".join(f"- {slug} -- {known.get(slug) or briefs.get(slug) or slug}"
                       for slug, _ in children(front))
    parts = split_sections(body)
    return join_sections([(name, "\n" + lines + "\n\n" if name == "Items" else text)
                          for name, text in parts])


def move(root: Path, src: list[str], dst: list[str], index: str,
         dst_root: Path | None = None) -> list[str]:
    """Transfers a node to a target parent at an index -- or
    reorders it inside its own parent. The entry leaves, the entry is written at
    the index, both parents renumber, the folders follow their derived names,
    and the moved documents' model keys say their new home; every refusal
    fires BEFORE anything is written. The subtree's prose stays the agent's.
    `root` is the source plan's tree, `dst_root` the target plan's (the same when
    not given): a node moves between the instance and the shared root like
    between two plans of one tree.

    -> the plans whose next move must be re-announced."""
    if len(src) < 2:
        fail("kind-mismatch", "a plan does not move -- a node under it does")
    name = src[-1]
    dst_root = dst_root or root
    src_doc = standing(root, src)
    src_parent_doc = doc_of(root, *src[:-1])
    try:
        dst_parent_doc = doc_of(dst_root, *dst)
    except SystemExit:
        fail("target-unknown", f"{'/'.join(dst)} has no document to receive `{name}`")
    if not dst_parent_doc.is_file():
        fail("target-unknown", f"{'/'.join(dst)} has no document to receive `{name}`")
    same_parent = src_parent_doc == dst_parent_doc
    src_front, src_body = read(src_parent_doc)
    dst_front, dst_body = (src_front, src_body) if same_parent else read(dst_parent_doc)
    moved_template, landing_shape = template_name(read(src_doc)[0]), level_of(dst_root, dst_front)
    if landing_shape.leaf or landing_shape.next != moved_template:
        fail("kind-mismatch", f"`{name}` is a `{moved_template}` -- it lands under a node whose `next:` is "
                              f"`{moved_template}`, and {'/'.join(dst)} holds "
                              f"{'todos' if landing_shape.leaf else '`' + str(landing_shape.next) + '`'}")
    kids = children(src_front)
    status = next(s for child, s in kids if child == name)
    landed_done = dst_front.get("status") == "done"
    landing = [c for c in children(dst_front) if not (same_parent and c[0] == name)]
    if any(child == name for child, _ in landing):
        fail("slug-taken", f"{'/'.join(dst)} already holds `{name}`")
    if not index.isdigit() or not 1 <= int(index) <= len(landing) + 1:
        fail("index-invalid", f"`{index}` -- the landing rank is 1..{len(landing) + 1}")
    landing.insert(int(index) - 1, (name, status))

    # every guard passed -- the effect starts here, model keys first
    moved_front, moved_body = read(src_doc)
    moved_front["plan"] = dst[0]
    write(src_doc, moved_front, titled(root, moved_front, moved_body, dst[-1]))
    for below in sorted(src_doc.parent.rglob("*.md")):
        # every node under the moved one carries the plan it now lives in
        if below != src_doc and node_in(root, below.parent) == below:
            bfront, bbody = read(below)
            bfront["plan"] = dst[0]
            write(below, bfront, titled(root, bfront, bbody, below.parent.parent.name.split("-", 1)[1]))

    def rewrite(front: dict, rebuilt: list[tuple[str, str]]) -> None:
        for key in [k for k in front if isinstance(k, str) and ITEM.match(k)]:
            del front[key]
        for position, (child, child_status) in enumerate(rebuilt, 1):
            front[f"item.{position}"] = f"{child}  {child_status}"

    src_shape, dst_shape = level_of(root, src_front), level_of(dst_root, dst_front)
    carried = dict(item_lines(section_text(src_body, "Items") or "")).get(name, "") \
        if is_written("Items", src_body) else ""
    if same_parent:
        rewrite(src_front, landing)
        write(src_parent_doc, src_front, items_follow(src_shape, src_front, src_body, {}))
    else:
        rewrite(src_front, [c for c in kids if c[0] != name])
        rewrite(dst_front, landing)
        write(src_parent_doc, src_front, items_follow(src_shape, src_front, src_body, {}))
        write(dst_parent_doc, dst_front, items_follow(dst_shape, dst_front, dst_body, {name: carried}))
        # parked at rank 0 -- a rank no entry owns -- until the reindex derives its place
        src_doc.parent.rename(dst_parent_doc.parent / f"0-{name}")
    reindex(src_parent_doc.parent, src_front)
    if not same_parent:
        reindex(dst_parent_doc.parent, dst_front)
        if status in ENGAGED and landed_done:
            reopen(dst_root, dst)   # work under way lands: the done parent reopens, its ancestry rising
    return [src[0]] if same_parent or src[0] == dst[0] else [src[0], dst[0]]


def rename(root: Path, segments: list[str], new: str) -> None:
    """Gives a node under a plan a new NAME -- the identity every entry, folder and
    model key carries: the parent's entry at its rank and its Items line, the
    document's `slug:`, the titles of the nodes right under it, the derived
    folder -- in one call, every refusal BEFORE the first write. A plan keeps the
    name it was born under (its folder, every `plan:` key and the bus's vectors
    say it); a todo is a line of Items and renames there. What the prose says of
    the old name -- the bodies, the threads -- stays the agent's: the call says so."""
    if len(segments) < 2 or leaf_above(root, segments) is not None:
        fail("kind-mismatch", "a node under a plan renames -- a plan keeps the name it was born "
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
    write(path, front, titled(root, front, body, segments[-2]))
    for below in sorted(path.parent.glob("*/*.md")):
        # the nodes right under it say their parent in their title
        if node_in(root, below.parent) == below:
            bfront, bbody = read(below)
            write(below, bfront, titled(root, bfront, bbody, new))
    pshape = level_of(root, pfront)
    carried = dict(item_lines(section_text(pbody, "Items") or "")).get(old, "") \
        if is_written("Items", pbody) else ""
    for key, value in list(pfront.items()):
        if isinstance(key, str) and ITEM.match(key) and str(value).split(None, 1)[0] == old:
            status = str(value).split(None, 1)[1] if len(str(value).split(None, 1)) > 1 else ""
            pfront[key] = f"{new}  {status}"            # the rank is the key's: untouched
    write(parent_doc, pfront, items_follow(pshape, pfront, pbody, {new: carried}))
    # the folder is DERIVED: its position stays, its name follows
    position = path.parent.name.split("-", 1)[0]
    path.parent.rename(path.parent.parent / f"{position}-{new}")


def reopen(root: Path, segments: list[str]) -> None:
    """Reopens a DONE node for a rework -- the maintenance cycle's hinge: the
    component's node accumulates its history instead of spawning twins. The
    transition is done -> redo, the plan included, and the whole ANCESTRY rises
    with it in the SAME call: every parent entry follows, and a parent found
    closed reopens too, `redo` as well."""
    if leaf_above(root, segments) is not None:
        fail("reopen-invalid", "a node reopens -- a todo does not")
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
            pfront["status"] = "redo"
        write(parent_doc, pfront, pbody)
        child, carried = segments[depth - 1], pfront["status"]


def selection(shape: SimpleNamespace, body: str, wanted: tuple[str, ...], top: bool = False) -> list[str]:
    """-> one couple of tags per run of the `wanted` sections the body holds, from the first one's
    heading to the next section OF ITS TEMPLATE -- a heading that is no section of the template
    stays with the section it details; with `top`, a run that opens on the first section starts
    at the top of the document, its title with it."""
    present = [name for name, _ in split_sections(body) if name in shape.sections]
    couples: list[str] = []
    start = None
    for rank, name in enumerate(present):
        if name in wanted and start is None:
            start = "" if top and rank == 0 else f"## {name}"
        following = present[rank + 1] if rank + 1 < len(present) else None
        if start is not None and following not in wanted:
            couples.append(f"{start}..## {following}" if following else f"{start}..")
            start = None
    return couples


def shown(shape: SimpleNamespace, body: str) -> list[str]:
    """-> the selections a node above the one at work mounts: the sections its template names in
    `shown:`; a shown section the document lacks says nothing."""
    return selection(shape, body, shape.shown)


def package_name() -> str:
    """-> the name this package is played under -- the prefix of a mount address of its bundle."""
    return str(yaml.safe_load((Path(__file__).resolve().parents[2] / "package.yaml").read_text(encoding="utf-8"))["name"])


def template_address(root: Path, name: str) -> str:
    """-> the mount address of the template `name`: its path under the tree's `plans/`, or
    `<package>:templates/<name>.md` for the product's."""
    path = template_file(root, name)
    if path.parent == TEMPLATES:
        return f"{package_name()}:templates/{path.name}"
    return str(path.relative_to(root))


def mount_chain(root: Path, segments: list[str], whole: bool = False) -> list[dict]:
    """-> the `::mount` payload a node commands: the one method, `PLAN`, by its NAME (the engine
    resolves it to the composition's base, its overlays applying); then, for each level from
    the plan down to the node, its TEMPLATE -- `<package>:templates/<name>.md` for the
    product's, its path for a tree's own -- and its instance by its path; last, `PLANS-TEMPLATES`
    by its name, whose `payloads:` serve the reading `plan-templates` -- a mounted document's
    payloads come at the tail of its mount, so the one that carries them is the last of the chain
    and the method keeps the head. A template puts its
    laws and readings in force at every level, and serves its BODY, the method of its level,
    at the node at work alone. The node at work mounts its whole body; an ancestor mounts the
    sections its template names in `shown:`, or every body under `whole`. A PREPARED item --
    an entry without a document yet -- and an item not even prepared under a born parent
    mount their template ahead, the instance absent: the combined GO that frames the parent,
    then the child, mounts once. The last entry REPLACES the plan's other born nodes
    (`replaces`), so a node mounted after its sibling in the same passage leaves the
    sibling out of the view.
    READ-ONLY: nothing written, no status read, no next move touched -- the verb
    plays at any moment."""
    method = Path(__file__).resolve().parents[2] / "procs" / "PLAN.md"
    if not READING.is_file():
        fail("method-missing", "the package carries no procs/PLANS-TEMPLATES.md beside this script -- "
                               "the mount verb plays from an installed bundle")
    if not method.is_file():
        fail("method-missing", "the package carries no procs/PLAN.md beside this script -- "
                               "the mount verb plays from an installed bundle")
    entries: list[dict] = [{"doc": method.name, "body": True}]     # the one method, by its name
    nodes: list[dict] = []
    kind = ""
    for depth in range(1, len(segments) + 1):
        kind = template_at(root, segments[:1]) if depth == 1 else level(root, kind).next
        if kind is None:
            fail("path-unknown", f"{'/'.join(segments[:depth - 1])} is a leaf -- its items are todos, never nodes")
        # the level's template: its laws always, its body -- the method of the level -- at the node at work
        entries.append({"doc": template_address(root, kind), "body": depth == len(segments) or whole})
        if depth == len(segments) > 1:
            # the last segment may be PREPARED (an entry, no document) or not even that:
            # under a born parent its template rides ahead, its instance absent --
            # the combined GO that frames the parent, then the child, mounts once
            parent_front, _ = read(doc_of(root, *segments[:-1]))
            if segments[-1] not in {c for c, _ in children(parent_front)}:
                break
        instance_doc = doc_of(root, *segments[:depth])
        if not instance_doc.is_file():
            if depth == 1:
                fail("path-unknown", f"plans/{segments[0]} is not born -- write its template's first section first")
            if depth != len(segments):
                fail("path-unknown", f"{'/'.join(segments[:depth])} is prepared, not born -- "
                                     "nothing stands under it yet")
            break                       # a prepared item: its template rides, no instance yet
        # the node's OWN document comes with its BODY: what its framing wrote -- the
        # context, the ground, the arbitrations, the items -- is the matter of the work
        entries.append({"doc": str(instance_doc.relative_to(root)), "body": True})
        nodes.append(entries[-1])
    for entry in nodes[:-1] if not whole else []:
        # each node above the last shows its template's `shown:`
        front, body = read(root / entry["doc"])
        entry["body"] = shown(level_of(root, front), body) or False
    if nodes and not whole:
        # the last node serves its `served` sections -- the whole body when none is `unserved`
        front, body = read(root / nodes[-1]["doc"])
        shape = level_of(root, front)
        if shape.served != shape.sections:
            nodes[-1]["body"] = selection(shape, body, shape.served, top=True) or False
    # the node mounted REPLACES the other born nodes of its plan: a sibling mounted earlier in
    # the passage leaves the view, its laws with it
    chain = {one["doc"] for one in entries}
    others = [str(one.relative_to(root)) for one in born_nodes(root, segments[0])]
    replaced = [one for one in others if one not in chain]
    if replaced:
        entries[-1]["replaces"] = replaced
    return entries + [{"doc": READING.name, "body": True}]


def plural(word: str) -> str:
    """-> a template's name said of several nodes."""
    return word + ("es" if word.endswith(("s", "x", "z", "ch", "sh")) else "s")


def born_nodes(root: Path, slug: str) -> list[Path]:
    """-> the documents of the plan's born nodes under its root, in item order."""
    return [doc_of(root, *one) for one in walk(root, [slug])[1:]]


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
    node it names, in parentheses -- `plan:<address>` at every depth, the address `verify`
    resolves: the key the
    thread's step carries, so a line served again finds its step and never
    adds one (batch la-cle-au-next-move)."""

    def at(text: str, *node: str) -> str:
        # the deepest node named, as its vector spells it: the last token of the line is
        # what the agent copies into the step's key
        return f"{text} ({vector_of('/'.join(node))})"

    def first_open(kids: list[tuple[str, str]]) -> tuple[str, str] | None:
        # engagement primes order: a started node outranks one never opened
        alive = [one for one in kids if one[1] != "done"]
        working = [one for one in alive if one[1] in ENGAGED]
        return (working or alive or [None])[0]

    def leaf_move(shape: SimpleNamespace, status: str, node: list[str]) -> str:
        where = f"the {shape.name} {'/'.join(node[1:]) or node[0]}"
        if status == "todo":
            return at(f"{where} awaits its framing", *node)
        if status == "blocked":
            return at(f"{where} is blocked -- the GO that unblocks it is awaited", *node)
        if status == "redo":
            return at(f"{where} is reopened -- its rework awaits the principal's GO", *node)
        return at(f"{where} awaits its implementation -- on the GO that names it", *node)

    front, _ = read(doc_of(root, slug))
    if front.get("status") == "done":
        return None
    shape, node = level_of(root, front), [slug]
    if shape.leaf:
        return leaf_move(shape, str(front.get("status")), node)
    kids = children(front)
    if not kids:
        return at(f"the {shape.name} has no {shape.next} yet -- its {plural(shape.next)} come on the principal's GO "
                  "(one GO creates and frames them)", slug)
    picked = first_open(kids)
    if picked is None:
        return at(f"every {shape.next} is delivered and the {shape.name} stands open -- `repair` closes it", slug)
    while True:
        # one level down: the node the walk picked, born or prepared
        child, status = picked
        shape, node = level(root, shape.next), node + [child]
        if shape.leaf:
            return leaf_move(shape, status, node)
        where = f"the {shape.name} {'/'.join(node[1:])}"
        doc = doc_of(root, *node)
        kids = children(read(doc)[0]) if doc.is_file() else []   # prepared: no document yet
        if not kids:
            if status == "todo":
                return at(f"{where} awaits its framing -- its {plural(shape.next)} come on the principal's GO", *node)
            if status == "redo":
                return at(f"{where} is reopened -- its rework awaits the principal's GO", *node)
            if status == "blocked":
                return at(f"{where} is blocked -- the GO that unblocks it is awaited", *node)
            # a framed node walks doing without children yet: its move is their
            # creation -- closing is for delivered children alone
            return at(f"{where} awaits its {plural(shape.next)} -- their creation awaits the principal's GO", *node)
        # a reopened node walks its children like any open one: the line names the
        # deepest node that carries the work, never its parent alone
        picked = first_open(kids)
        if picked is None:
            return at(f"{where} is reopened -- its rework awaits the principal's GO" if status == "redo"
                      else f"{where} is delivered and stands open -- `repair` closes it", *node)

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
    """Takes ONE law out by its code: the line leaves its `constraints.*` block (the
    block's key with it when it was the last) and NOTHING is kept -- the law is gone, and
    the writer's inventory no longer sees its number. The principal's word that allows
    the gesture is the method's to wait for (PN15), never the script's to record.
    -> the text the law carried"""
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


def served(home: Path) -> list[str]:
    """-> the next move lines, plan by plan: for a plan of the instance, the line the bus
    HOLDS; for a plan of the shared root, the line COMPUTED from its document now -- the
    bus is this run's alone, and another run may have moved the plan since this one
    pushed its line. A plan standing in BOTH trees serves neither line: the double is said
    instead, the line `check` says.

    A standing key reads `standing|<source>|<signal>|<vector>`; this package reads its
    own three and nothing else -- another provider's held entry is not its business.

    documentary: the emission and the reception are two halves of one mechanism -- the
    call pushes, the turn serves; keeping the reader here is what lets the package
    carry its own line without asking anything of a neighbour."""
    path = home / ".sys" / "records" / BUS
    try:
        held = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except ValueError:
        held = {}                # an unreadable record holds nothing
    double = doubles(home)
    own = plans_in(home) - set(double)
    prefix = f"standing|{SOURCE}|{SIGNAL}|"
    lines = [twice_said(slug, both) for slug, both in double.items()]
    lines += [str((entry or {}).get("text", "")).strip()
             for key, entry in sorted(held.items())
             if key.startswith(prefix) and (key[len(prefix):].partition(":")[2] in own)]
    for tree in trees(home)[1:]:
        for slug in sorted(plans_in(tree) - own - set(double)):
            lines.append(next_move(tree, slug) or "")
    return [line for line in lines if line]


def born_plans(home: Path) -> set[str]:
    """-> the slugs of the plans whose document stands in any tree -- a held line of any
    other is a plan gone."""
    return set().union(*(plans_in(tree) for tree in trees(home)))


def gone(home: Path) -> list[str]:
    """-> the slugs of the plans the bus still holds a next move for, whose document is gone
    from every tree."""
    path = home / ".sys" / "records" / BUS
    try:
        held = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except ValueError:
        return []
    prefix = f"standing|{SOURCE}|{SIGNAL}|plan:"
    standing = born_plans(home)
    return sorted({key[len(prefix):] for key in held if key.startswith(prefix)} - standing)


def announce(root: Path, slug: str) -> None:
    """Prints the plan's push after a mutating call -- the generating event is
    THIS moment: the state just changed, the fresh next move replaces the held
    line (or clears it, a closed plan cleans its own push)."""
    action = next_move(root, slug)
    if action is None:
        print(f"::clear plan-next-move plan:{slug}")
    else:
        print(f"::push plan-next-move plan:{slug} {action}")


def vector_of(address: str) -> str:
    """-> the vector of the node at `address`, whatever its depth: `plan:<address>`."""
    return f"{FAMILY}:{address}"


def status_nodes(home: Path, slug: str | None, everything: bool = False,
                 engaged: bool = False) -> tuple[list[dict], list[str]]:
    """-> (the progress LIST, the closed plans left out), DERIVED from the front matters alone --
    nothing stored, everything read. Without a slug: one node per plan, the plans of the instance
    then those of the shared root (`shared` true), the
    open ones, every one with `everything`, a slug standing in BOTH trees said once as a
    `plan-twice` finding (`twice`: its two directories) instead of either plan, and under each open
    plan its ENGAGED phases and batches (doing, redo, blocked) with `engaged`; with a slug: the plan, its phases and its
    batches in document order, a todo counted on its batch, never listed. A node counts its BORN
    children done or open and its PREPARED ones apart (an entry, no document); an open plan says
    its next move, computed from its document."""

    def node(tree: Path, path: Path, address: str, depth: int) -> dict:
        front, _ = read(path)
        shape, status = level_of(tree, front), front.get("status")
        one = {"address": address, "template": shape.name, "status": status, "born": True, "depth": depth,
               "vector": vector_of(address), "shared": tree != home}
        kids = children(front)
        if shape.leaf:
            one["todos"] = {"done": sum(1 for _, s in kids if s == "done"), "total": len(kids)}
        else:
            born = [s for position, (child, s) in enumerate(kids, 1)
                    if child_doc(path, shape, position, child).is_file()]
            done = sum(1 for s in born if s == "done")
            one["children"] = {"template": shape.next, "done": done, "open": len(born) - done,
                               "prepared": len(kids) - len(born)}
        if depth == 0 and status != "done":
            one["next"] = next_move(tree, address)
        return one

    def child_doc(path: Path, shape: SimpleNamespace, position: int, child: str) -> Path:
        return path.parent / f"{position}-{child}" / node_file(shape.next)

    def walk(tree: Path, path: Path, address: str, depth: int, found: list[dict]) -> None:
        one = node(tree, path, address, depth)
        found.append(one)
        if "todos" in one:
            return
        front, _ = read(path)
        shape = level_of(tree, front)
        for position, (child, status) in enumerate(children(front), 1):
            doc = child_doc(path, shape, position, child)
            if doc.is_file():
                walk(tree, doc, f"{address}/{child}", depth + 1, found)
            else:
                found.append({"address": f"{address}/{child}", "template": shape.next, "status": status,
                              "born": False, "depth": depth + 1, "vector": vector_of(f"{address}/{child}"),
                              "shared": tree != home})

    if slug is not None:
        tree = tree_of(home, slug)
        doc = doc_of(tree, slug)
        if not doc.is_file():
            fail("path-unknown", f"{slug} has no plan document")
        found: list[dict] = []
        walk(tree, doc, slug, 0, found)
        return found, []
    found, closed, seen = [], [], set()
    for slug, both in doubles(home).items():
        seen.add(slug)               # neither tree wins: the double is said, never one plan of it
        found.append({"address": slug, "template": None, "status": "plan-twice", "born": True, "depth": 0,
                      "vector": f"plan:{slug}", "shared": None, "twice": [str(one) for one in both]})
    for tree in trees(home):
        for doc in [plan_doc(tree, one) for one in sorted(plans_in(tree))]:
            if doc.parent.name in seen:
                continue             # a double, said above
            seen.add(doc.parent.name)
            one = node(tree, doc, doc.parent.name, 0)
            if one["status"] == "done" and not everything:
                closed.append(one["address"])
                continue
            if engaged and one["status"] != "done":
                branch: list[dict] = []
                walk(tree, doc, one["address"], 0, branch)
                found += [branch[0]] + [kid for kid in branch[1:] if kid["born"] and kid["status"] in ENGAGED]
            else:
                found.append(one)
    return found, closed


def status_text(found: list[dict], closed: list[str]) -> str:
    """-> the list said one line per node, indented by level: its address, template and status --
    `shared` after it for a plan of the shared root --, its progress, its next move; then the
    closed plans left out, counted and named."""
    lines = []
    for one in found:
        parts = [one["address"], one["template"] or "-", one["status"] or "-"]
        if one.get("twice"):
            lines.append("  ".join(parts + [" and ".join(one["twice"])]))
            continue
        if one.get("shared"):
            parts.append("shared")
        if not one["born"]:
            parts.append("prepared")
        elif "todos" in one:
            parts.append(f"{one['todos']['done']}/{one['todos']['total']} todos")
        else:
            kids = one["children"]
            parts.append(f"{kids['done']}/{kids['done'] + kids['open']} {plural(kids['template'])}"
                         + (f" +{kids['prepared']} prepared" if kids["prepared"] else ""))
        line = "  " * one["depth"] + "  ".join(parts)
        lines.append(line + (f"  · {one['next']}" if one.get("next") else ""))
    if closed:
        lines.append(f"+{len(closed)} closed: {', '.join(closed)}")
    return "\n".join(lines) if lines else "pp-plan: no plan"


def documents_in(home: Path) -> list[tuple[Path, Path]]:
    """-> (the tree, the document) for every plan document of every tree, the instance
    first -- the walk `check` and `repair` share."""
    found: list[tuple[Path, Path]] = []
    for tree in trees(home):
        for slug in sorted(plans_in(tree)):
            folder = tree / "plans" / slug
            found += [(tree, doc) for doc in sorted(folder.glob("**/*.md"))
                      if doc.parent == folder or re.fullmatch(r"\d+-.+", doc.parent.name)
                      if node_in(tree, doc.parent) == doc]
    return found


def check(home: Path) -> list[str]:
    """-> every incoherence the structure holds, in the instance and in the shared root --
    the lint that catches the hand: a child line without its document, a document without
    its line, statuses out of the enumeration, a line disagreeing with its document, a body
    with no prose, a DERIVED folder (`<n>-<name>`) without its entry -- any other directory
    is the plan's own material and says nothing. Empty means clean."""
    found: list[str] = [twice_said(slug, both) for slug, both in doubles(home).items()]
    materials: dict[str, set[str]] = {}     # plan -> the names its documents carry and their chain lacks
    engine = conductor()
    for tree, doc in documents_in(home):
        plans_dir = tree / "plans"
        front, body = read(doc)
        spot = "/".join(doc.parent.relative_to(plans_dir).parts)
        try:
            declared_in(doc, front)              # every block judged once, at its own document
        except engine.Refusal as refusal:
            found.append(f"{spot}: {str(refusal).split(' — ', 1)[-1]} (material-invalid)")
        named = str(front.get("material") or "")
        if named and named not in trees_of(doc, lenient=True):
            materials.setdefault(spot.split("/")[0], set()).add(named)
        if front.get("status") not in STATUSES:
            found.append(f"{spot}: status `{front.get('status')}` out of the enumeration")
        if not front.get("template"):
            found.append(f"{spot}: `kind:` and no `template:` -- the form before the templates")
            continue
        try:
            shape = shape_of(tree, str(front["template"]))
        except Unfit as unfit:
            found.append(f"{spot}: {unfit.detail} ({unfit.code})")
            continue
        # prose = what remains once headings and blanks are gone -- a heading is a label
        prose = [l for l in body.splitlines() if l.strip() and not l.lstrip().startswith("#")]
        if not prose:
            found.append(f"{spot}: no prose in the body")
        if "phase" in front:
            found.append(f"{spot}: `phase:` -- a key of the form before the templates")
        address = address_of(plans_dir, doc)
        title, wanted = title_line(body), title_of(tree, front, address[-2] if len(address) > 1 else "")
        if title is None:
            found.append(f"{spot}: no title -- the front says `{wanted}`")
        elif owned(tree, front, title) and title != wanted:
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
            if shape.leaf:
                # a todo is named by its SLUG -- a positional tag says nothing in a
                # status line, and every entry owns its `- <name> -- ...` body line
                if re.fullmatch(r"T\d+", child):
                    found.append(f"{spot}: todo `{child}` wears a positional tag -- a todo is named by its slug")
                elif f"- {child} -- " not in body:
                    found.append(f"{spot}: todo `{child}` has no `- {child} -- ...` line in the body")
                continue
            # the folder is DERIVED (<position>-<name>) -- a drifted rename reddens here
            child_doc = doc.parent / f"{position}-{child}" / node_file(shape.next)
            if not child_doc.is_file():
                if cstatus not in ("todo", "done"):   # a prepared item: todo, or closed by hand unborn
                    found.append(f"{spot}: entry `{child}` is {cstatus} without its folder `{position}-{child}`")
            else:
                cfront, _ = read(child_doc)
                if cfront.get("status") != cstatus:
                    found.append(f"{spot}: entry `{child}` says {cstatus}, the document says {cfront.get('status')}")
        if not shape.leaf:
            lined = {f"{i}-{c}" for i, (c, _) in enumerate(kids, 1)}
            # a DERIVED folder without its entry reddens; a cache, campaigns, playbooks --
            # the plan's own material -- carries no entry and says nothing
            for sub in sorted(p for p in doc.parent.iterdir() if p.is_dir()):
                if re.fullmatch(r"\d+-.+", sub.name) and sub.name not in lined:
                    found.append(f"{spot}: derived folder `{sub.name}` has no entry")
    for slug, names in sorted(materials.items()):
        # a name no document of the node's chain declares: the mount serves none of its
        # rows and says material-unknown at every turn -- one line per plan and name; a
        # retired name (`repo`, `work`) can never be declared: its one gesture is `-`
        for name in sorted(names):
            if name in engine.settings.RETIRED_MATERIALS:
                found.append(f"{slug}: material `{name}` names no tree -- `repo` and `work` name no tree any "
                             f"more: take the key out by `material {slug} -` (material-undeclared)")
                continue
            found.append(f"{slug}: material `{name}` is declared in no document of its chain -- declare "
                         f"it by `material {slug} {name} <path>`, or take the key out by "
                         f"`material {slug} -` (material-undeclared)")
    return found


# the gesture `repair` says with a finding it leaves: the first key the finding carries
GESTURES = {
    "out of the enumeration": "close it by `done <address>`, or stop it by `block <address> <reason>`",
    "no prose": "write its first section by `section`",
    "legacy": "rewrite the children by `section … Items`",
    "a name is born once": "rewrite Items with one line per item",
    "the writer reaches the first": "keep the prose that holds, then remove the other by "
                                    "`section <address> <Name> --remove=<n>`",
    "carries open work": "reopen the parent by rewriting one of its `redo` sections, or close the child by "
                         "`done <address>`",
    "positional tag": "rewrite Items with slugs",
    "line in the body": "rewrite Items with the missing line",
    "has no entry": "prepare the item in Items, or remove the folder by hand",
    "without its folder": "the document is gone: close the item by `done <address>`, or restore the folder by hand",
    "plan-twice": "remove one of the two by hand -- a plan lives in one tree",
    "name no tree any more": "take the key out by `material <slug> -`",
    "material-undeclared": "declare its tree by `material <slug> <name> <path>`, or take the key out "
                           "by `material <slug> -`",
    "the form before the templates": "the migration script of the re-pin rewrites it",
}


def repair(home: Path) -> tuple[list[str], list[str]]:
    """Mends what is MECHANICAL, in the instance and in the shared root -- and says every
    mend: the item keys renumbered in the order of their entries; a line disagreeing with
    its child's document moved to the DOCUMENT's own status; a child folder without its
    entry given one, at the end, from the document it holds; a plan or a phase open over
    children all done CLOSED -- the cascade that never ran, on a tree older than it. Every
    other finding is SAID with its gesture and left as it is; the next move of a plan gone from
    every tree is a mend too, its `::clear` said by the caller. -> (mended, left)"""
    mended: list[str] = []
    for tree, doc in documents_in(home):
        plans_dir = tree / "plans"
        front, body = read(doc)
        spot = "/".join(doc.parent.relative_to(plans_dir).parts)
        changed = False
        if not front.get("template"):
            continue                     # the form before the templates: check says it, the migration rewrites it
        try:
            shape = shape_of(tree, template_name(front))
        except Unfit:
            continue                     # a template that cannot serve: check says it, a hand mends it
        address = address_of(plans_dir, doc)
        numbers = [int(ITEM.match(k).group(1)) for k in front if isinstance(k, str) and ITEM.match(k)]
        if numbers != list(range(1, len(numbers) + 1)):
            kids = children(front)
            for key in [k for k in front if isinstance(k, str) and ITEM.match(k)]:
                del front[key]
            for position, (child, cstatus) in enumerate(kids, 1):
                front[f"item.{position}"] = f"{child}  {cstatus}"
            mended.append(f"{spot}: item keys renumbered 1..{len(kids)}")
            changed = True
        if not shape.leaf and front.get("status") != "done" and children(front) \
                and all(cstatus == "done" for _, cstatus in children(front)):
            # the cascade that never ran: an open node over children all delivered closes
            front["status"] = "done"
            mended.append(f"{spot}: open over children all done -- closed, the cascade that never ran")
            changed = True
        if not shape.leaf:
            kids = children(front)
            for position, (child, cstatus) in enumerate(kids, 1):
                child_doc = doc.parent / f"{position}-{child}" / node_file(shape.next)
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
                held = sub / node_file(shape.next)
                if match and match.group(1) not in lined and held.is_file():
                    truth = read(held)[0].get("status")
                    add_child(front, match.group(1), truth if truth in STATUSES else "todo")
                    mended.append(f"{spot}: folder `{sub.name}` had no entry -- `{match.group(1)}` "
                                  "entered at the end, from its document")
                    changed = True
        parent = address[-2] if len(address) > 1 else ""
        retitled = titled(tree, front, body, parent)
        if retitled != body:
            body = retitled
            mended.append(f"{spot}: title set to `{title_of(tree, front, parent)}` -- the front's names")
            changed = True
        if changed:
            write(doc, front, body)
            if not shape.leaf:
                reindex(doc.parent, front)
            if front.get("status") == "done" and len(address) > 1:
                # a node closed by the mend: its line at its parent follows
                _splice_child(node_in(tree, doc.parent.parent), front["slug"], "done")
    for slug in gone(home):
        mended.append(f"the next move of `{slug}`, a plan gone, leaves the bus")
    left = []
    for finding in check(home):
        why = next((g for key, g in GESTURES.items() if key in finding), "a hand's business")
        left.append(f"{finding} -- {why}")
    return mended, left


def main(argv: list[str]) -> int:
    """The gate: the verb's arity is judged BEFORE anything plays -- a malformed
    call refuses by name with the verb's usage, never the whole of this text -- and
    a verb that WRITES plays inside the plan's critical section: the lock is taken
    before the first read and released after the last write, whatever the number
    of documents the verb walks -- and AFTER its stdin is read: a call that waits for
    its prose holds nobody up. What needs no lock is refused BEFORE it: what refuses
    without stdin (the shared root, a plan born in no tree for any verb but the birth of
    that plan by its first section) before stdin is read, then a prose missing or opening a
    section of its own -- so no lock file is ever made for a plan that is not there."""
    if not argv:
        sys.stderr.write(f"pp-plan: argument-missing -- pp-plan <verb> ...; the verbs are {', '.join(USAGE)}\n")
        return 2
    verb, rest = argv[0], list(argv[1:])
    if verb not in USAGE:
        fail("verb-unknown", f"`{verb}` -- the verbs are {', '.join(USAGE)}")
    chosen, delivered = ROOT_TEMPLATE, None
    if verb == "section" and "--item" in rest:
        # the item a leaf's Delivery delivers: a value of its own, taken before the flags are read
        at = rest.index("--item")
        if at + 1 >= len(rest) or not NAME.fullmatch(rest[at + 1]):
            fail("argument-missing", f"--item takes the slug of an item -- {USAGE['section']}")
        delivered = rest[at + 1]
        del rest[at:at + 2]
    if verb == "section" and "--template" in rest:
        # the template a plan is born on: a value of its own, taken before the flags are read
        at = rest.index("--template")
        if at + 1 >= len(rest) or not NAME.fullmatch(rest[at + 1]):
            fail("argument-missing", f"--template takes a template's name -- {USAGE['section']}")
        chosen = rest[at + 1]
        del rest[at:at + 2]
        if rest and "/" in rest[0]:
            fail("argument-unexpected", "--template names the template a PLAN is born on -- a node under "
                                        "it takes its parent's `next:`")
    flagged = verb in ("section", "mount", "status", "templates")
    flags = [one for one in rest if one.startswith("--") and flagged]
    rest = [one for one in rest if not (one.startswith("--") and flagged)]
    if verb in ("section", "constrain") and rest and rest[-1] == "-":
        rest.pop()                                  # the stdin marker, said and dropped
    low, high = ARITY[verb]
    if len(rest) < low:
        fail("argument-missing", f"{verb} takes {USAGE[verb]}")
    if high is not None and len(rest) > high:
        fail("argument-unexpected", f"`{rest[high]}` -- {verb} takes {USAGE[verb]}")
    for flag in flags if verb == "status" else ():
        if flag not in ("--all", "--engaged", "--json") or (flag in ("--all", "--engaged") and rest):
            fail("argument-unexpected", f"`{flag}` -- {USAGE['status']}")
    for flag in flags if verb == "templates" else ():
        if flag != "--json":
            fail("argument-unexpected", f"`{flag}` -- {USAGE['templates']}")
    for flag in flags if verb == "mount" else ():
        if flag != "--whole":
            fail("argument-unexpected", f"`{flag}` -- {USAGE['mount']}")
    for flag in flags if verb == "section" else ():
        if flag not in ("--append", "--shared") and not re.fullmatch(r"--remove(=[1-9][0-9]*)?", flag):
            fail("argument-unexpected", f"`{flag}` -- {USAGE['section']}")
    if len(flags) > 1 and verb == "section":
        fail("argument-unexpected", f"`{' '.join(flags)}` -- one flag at a time: {USAGE['section']}")
    if verb in WRITING and rest and rest[0].startswith("-") and rest[0] != "-":
        fail("argument-unexpected", f"`{rest[0]}` is no address -- {verb} takes {USAGE[verb]}")
    home_ = home()
    reads = ((verb == "section" and not any(one.startswith("--remove") for one in flags))
             or (verb == "constrain" and "--retire" not in rest) or (verb == "serve" and rest[1:] == ["-"]))
    if (verb in WRITING or verb == "mount") and rest:
        # the TREE of the plan is decided here, once, before the lock: the lock, the reads and
        # the writes of the verb live in it; the bus, the catalogue and the regime stay the instance's
        slug = rest[0].split("/")[0]
        if "--shared" in flags:
            tree = shared_root(home_)
            first = level(tree or home_, chosen).sections[0]
            if "/" in rest[0] or rest[1] != first:
                fail("argument-unexpected", "`--shared` births a plan under the run's root of documents: "
                                            f"section <slug> {first} --shared")
            if tree is None:
                fail("documents-none", "this run was opened with no root of documents, or no run names "
                                       "this call -- a shared plan lives under that root")
            for where in trees(home_):
                if (where / "plans" / slug).exists():
                    fail("slug-taken", f"plans/{slug} already stands"
                                       f"{' in the shared root' if where != home_ else ''} -- a slug is born once")
        else:
            tree = tree_of(home_, slug)
        if verb in WRITING and plan_doc(tree, slug) is None:
            # a plan born in no tree: only its birth by its first section takes the lock -- anything else refuses here
            first = level(tree, chosen).sections[0]
            if verb == "section" and "/" not in rest[0] and rest[1] != first and reads:
                fail("path-unknown", f"plans/{slug} is not born -- its first section, {first}, births it")
            if not (verb == "section" and "/" not in rest[0] and reads):
                fail("path-unknown", f"plans/{slug} has no PLAN.md -- no plan of that name is born")
        piped = conductor().reading.piped() if reads else None    # what refuses without stdin refused first
        if verb == "section" and piped is not None:
            judge_prose(piped)                      # before the lock: a prose refused takes none
        if verb not in WRITING:
            return _play(home_, tree, verb, rest, flags, piped, chosen, delivered)    # a view takes no lock
        with guarded(tree, slug):
            return _play(home_, tree, verb, rest, flags, piped, chosen, delivered)
    return _play(home_, home_, verb, rest, flags, conductor().reading.piped() if reads else None, chosen, delivered)


def _play(home: Path, root: Path, verb: str, rest: list[str], flags: list[str], piped: str | None = None,
          template: str = ROOT_TEMPLATE, item: str | None = None) -> int:
    """Plays the verb: `root` is the tree of the plan addressed (the instance, or the shared
    root), `home` the instance -- what reads the bus, the catalogue, every tree; `piped` the
    stdin the caller read before the lock, for the verbs that read one."""
    removal = next((flag for flag in flags if flag.startswith("--remove")), None)
    if verb == "section" and removal is not None:
        segments = rest[0].split("/")
        nth = int(removal.split("=", 1)[1]) if "=" in removal else None
        path, said = remove_section(root, segments, rest[1], nth)
        print(f"pp-plan: {said} removed from {rest[0]} -- {path.relative_to(root.parent)}")
        announce(root, segments[0])
    elif verb == "section":
        segments = rest[0].split("/")
        path, said, moves = write_section(root, segments, rest[1], piped or "",
                                          "--append" in flags, home, template, item)
        print(f"pp-plan: {rest[1]} {' and '.join(said)} on {rest[0]} -- {path.relative_to(root.parent)}")
        for line in moves:
            print(line)
        announce(root, segments[0])
    elif verb == "done":
        closed = done(root, rest[0].split("/"))
        print(f"pp-plan: {rest[0]} -> done")
        if closed:
            print(f"pp-plan: {closed[0]} -> done" + (f" -- closes {', '.join(closed[1:])}" if closed[1:] else ""))
        announce(root, rest[0].split("/")[0])
    elif verb == "block":
        block(root, rest[0].split("/"), " ".join(rest[1:]))
        print(f"pp-plan: {rest[0]} -> blocked -- {' '.join(rest[1:])}")
        announce(root, rest[0].split("/")[0])
    elif verb == "move":
        landing = tree_of(home, rest[1].split("/")[0])
        touched = move(root, rest[0].split("/"), rest[1].split("/"), rest[2], landing)
        print(f"pp-plan: moved -- {rest[0]} -> {rest[1]} [{rest[2]}]")
        print("pp-plan: the subtree's prose is yours -- sweep its references to the old home")
        for moved_plan in touched:
            announce(tree_of(home, moved_plan), moved_plan)
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
            print(f"pp-plan: retired -- {code} on {rest[0]} -- the law is gone, nothing kept")
            return 0
        section = rest[rest.index("--section") + 1] if "--section" in rest and rest.index("--section") + 1 < len(rest) else ""
        spare = [one for one in rest[1:] if one != "--section" and one != section]
        if len(spare) > 1:
            fail("argument-unexpected", f"`{spare[1]}` -- {USAGE['constrain']}")
        amended, fresh = [], []
        for text in writer.bounded((piped or "").splitlines()):
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
            rows = ([list(engine.reading.split_row(one)) for one in (piped or "").splitlines()]
                    if whole else [rest[1:]])
            if whole:
                while rows and not rows[-1]:
                    rows.pop()
                while rows and not rows[0]:
                    rows.pop(0)
                if not any(rows):
                    fail("value-malformed", "an empty serve section writes nothing")
            for row in rows:                     # a mark no tree takes: the mount would refuse the row
                for mark in (one[1:] for one in row if one.startswith("@")):
                    if mark in engine.settings.RETIRED_MATERIALS:
                        fail("material-invalid", f"`{' '.join(one for one in row if one)}` -- no tree is called "
                                                 f"`{mark}`: mark the row with a tree the plan declares, or "
                                                 "leave it unmarked on a node that names no material")
            heavy(home, path, rows, engine)
            answer = engine.sections.serve(path, rows, whole)
        except engine.Refusal as refusal:
            fail(refusal.code, str(refusal).split(" — ", 1)[-1])
        print(f"pp-plan: served -- {answer} on {rest[0]}")
        declared = read(path)[0].get("material")
        if declared and any(unmarked(row) for row in rows):
            # a reminder, never a refusal: the line of share between the plan's trees is the
            # operator's, the script does not know it
            print(f"pp-plan: the rows read the material `{declared}`, and that tree alone; a document of "
                  "another tree takes the mark of a tree the plan declares, `@<name>`")
    elif verb == "material" and len(rest) == 3 and rest[1] == "-":
        path = withdraw(root, rest[0], rest[2])
        print(f"pp-plan: tree `{rest[2]}` withdrawn from {rest[0]} -- {path.relative_to(root.parent)}")
    elif verb == "material":
        chosen, documents = material(root, rest[0], rest[1] if len(rest) > 1 else None,
                                     rest[2] if len(rest) > 2 else None)
        listed = ", ".join(str(one.relative_to(root.parent)) for one in documents)
        if chosen is None:
            print(f"pp-plan: material taken out of {rest[0]} -- {len(documents)} document(s): {listed}")
        else:
            print(f"pp-plan: material `{chosen}` written on {rest[0]} -- {len(documents)} document(s): {listed}")
    elif verb == "next-move":
        # read-only, like `status`: a payload SERVES what the bus holds -- and what a shared
        # plan's document says now --, it never pushes
        for line in served(home):
            print(line)
    elif verb == "verify":
        verify(home, conductor().reading.piped())      # read-only: the engine asks, the trees answer
    elif verb == "status":
        found, closed = status_nodes(home, rest[0] if rest else None, "--all" in flags, "--engaged" in flags)
        print(json.dumps(found, ensure_ascii=False) if "--json" in flags else status_text(found, closed))
    elif verb == "templates":
        found = templates(home)
        print(json.dumps(found, ensure_ascii=False) if "--json" in flags else templates_text(found))
    elif verb == "check":
        findings = check(home)
        if findings:
            sys.stderr.write("pp-plan: check FAILED --\n" + "\n".join(f"  {f}" for f in findings) + "\n")
            return 2
        print("pp-plan: check clean")
    elif verb == "repair":
        mended, left = repair(home)
        for one in mended:
            print(f"pp-plan: repaired -- {one}")
        for one in left:
            print(f"pp-plan: left -- {one}")
        for slug in gone(home):
            print(f"::clear {SIGNAL} plan:{slug}")
        for slug in sorted({one.split("/", 1)[0].split(":", 1)[0] for one in mended} & born_plans(home)
                           - set(doubles(home))):
            announce(tree_of(home, slug), slug)
        if not mended and not left:
            print("pp-plan: check clean -- nothing to repair")
        elif not left:
            print("pp-plan: check clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
