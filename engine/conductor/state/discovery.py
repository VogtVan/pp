"""Behaviour: finding the workspace we run in, and the members around it.

A member is recognized by its INSTANCE (a directory carrying `instance.yaml`) and by
nothing else: the engine runs INSTALLED, at `<instance>/.sys/engine/`, and its own
location says the member. Sibling members share a first-degree ancestor, so the
ROOT is the member's parent -- a path lookup, no command, nothing
asked of the outside.

documentary: the root was resolved through `git rev-parse --git-common-dir` until the
operator's word of 2026-08-31, to make a worktree answer its main checkout. A worktree
is not a member -- it carries a working copy of a repository, not an instance of the
siblings -- so the case it served does not exist, and the parent rule ends three defects
at once: the engine no longer needs git installed, the root no longer depends on the
process's working directory (git answered the RELATIVE `.git` in a plain repository),
and the walk no longer wanders outside the siblings.
"""
from __future__ import annotations

from pathlib import Path

from . import instance
from ..core.errors import Refusal
from ..core.model import Siblings, Member


def instance_member(script: Path) -> Member | None:
    """-> the member an INSTALLED engine belongs to -- the engine lives at
    `<instance>/.sys/engine/`, so its own location says everything: the instance
    directory's name (the meta_name parameter) and the member's root above it."""
    engine = script.resolve().parent
    machine = engine.parent
    holder = machine.parent
    if (engine.name == "engine" and machine.name == instance.SYS
            and instance.is_instance(holder)):
        return Member(path=holder.parent, name=holder.parent.name, meta_name=holder.name)
    return None


def installed_member(script: Path) -> Member:
    """-> the member an installed engine belongs to -- or the refusal that names the
    way: pp runs installed, an engine outside an instance conducts nothing."""
    member = instance_member(script)
    if member is None:
        raise Refusal("engine-uninstalled",
                      f"{script} is not an installed engine -- pp runs installed: "
                      f"`install <workspace>` puts one at <workspace>/{instance.DIRECTORY}")
    return member


def siblings_around(member: Member) -> Siblings:
    """-> the member's siblings: the directories beside it that carry an instance of
    the same name. The members share a first-degree ancestor, so the root is the
    member's own parent."""
    return Siblings(root=member.path.resolve().parent, meta_name=member.meta_name)


def members(siblings: Siblings) -> list[Member]:
    """A directory is a member when it carries an instance -- nothing else makes one."""
    if not siblings.root.is_dir():
        return []
    return [Member(path=d, name=d.name, meta_name=siblings.meta_name)
            for d in sorted(siblings.root.iterdir())
            if d.is_dir() and not d.name.startswith(".")
            and instance.is_instance(d / siblings.meta_name)]


def names(siblings: Siblings) -> list[str]:
    return [member.name for member in members(siblings)]


def member(siblings: Siblings, name: str) -> Member:
    for candidate in members(siblings):
        if candidate.name == name:
            return candidate
    raise Refusal("unknown-member", f"`{name}` -- known: {', '.join(names(siblings))}")


