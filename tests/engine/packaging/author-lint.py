"""Scenario `author-lint` -- a law the AUTHOR wrote never blocks the build (plan
pp-split, batch le-lint-qui-avertit) -- 6 case(s):
- a code declared twice by the instance's own documents WARNS and the build passes;
  the first declaration stands in both registries
- the same double between two PACKAGES refuses `constraint-doubled`, nothing written
- a law line out of form in an author's document WARNS and the document plays WITHOUT
  it -- its other law is in the registry
- the same line in a package's document refuses `constraint-malformed`
- an attach no proc hooks WARNS for the author, refuses between packages
- a bare `constraints:` key still refuses `constraints-unsectioned`, author or not:
  the migration gate is not a law defect
"""
from __future__ import annotations

from pathlib import Path

from conductor import instance
from conductor.packaging import compiling

DOUBLED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
           "constraints.behavior: |\n  Z9  the same code, twice\n---\n\nx\n")
MALFORMED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
             "constraints.behavior: |\n  Z7  a law in form\n  nocode\n---\n\nx\n")
ATTACHED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
            "attach: nobody.hooks.this\n---\n\nx\n")
UNSECTIONED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
               "constraints: |\n  Z6  the old regime\n---\n\nx\n")


def _package(env, name: str, text: str) -> Path:
    """The same document, written INSIDE the vendored kit -- a package's, by the only
    thing that makes one: a manifest above it."""
    vendor = next((env.made / instance.VENDOR).glob("kit@*"))
    path = vendor / "procs" / f"{name}.md"
    path.write_text(text.format(name=name), encoding="utf-8")
    return path


def _clear(env, *relpaths: str) -> None:
    for relpath in relpaths:
        (env.made / relpath).unlink(missing_ok=True)
    for stray in (env.made / instance.VENDOR).glob("kit@*/procs/Z*.md"):
        stray.unlink()


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("author-lint")
    meta = env.made

    # --- the discriminant: who owns a document ----------------------------------------
    vendored = next((meta / instance.VENDOR).glob("kit@*"))
    if compiling.authored(meta, "MEMBER.md") and not compiling.authored(
            meta, str((vendored / "procs" / "TURN.md").relative_to(meta))):
        held("the discriminant judges", "MEMBER.md is the author's, the vendored TURN.md "
             "is the kit's")
    else:
        failures.append("  ✗ the discriminant judges       author/package told apart")

    # --- a double the AUTHOR holds: a warning, and the build passes --------------------
    env.write("ONE.md", DOUBLED.format(name="ONE"))
    env.write("TWO.md", DOUBLED.format(name="TWO"))
    built = env.cli("-build")
    warned = [one for one in compiling.lint(meta) if one.startswith("constraint-doubled")]
    registry = compiling.render_registry(meta)   # derived on demand -- no file since the build left
    written = any((meta / instance.SYS / name).is_file() for name in ("constraints.md", "_constraints.md"))
    if built.returncode == 0 and warned and "WARNING" in built.stdout and registry.count("`Z9`") == 1 and not written:
        held("the author's double warns", f"-build rc=0, `{warned[0][:52]}…`, Z9 once in "
             "the derived table -- and no registry file on disk")
    else:
        failures.append(f"  ✗ the author's double warns    rc={built.returncode} {warned}")
    _clear(env, "ONE.md", "TWO.md")

    # --- the same double between two PACKAGES: the refusal, unchanged -----------------
    _package(env, "ZONE", DOUBLED)
    _package(env, "ZTWO", DOUBLED)
    expect("constraint-doubled", lambda: compiling.render_registry(meta))
    _clear(env)

    # --- a malformed law line: the author's document plays WITHOUT it ------------------
    env.write("THREE.md", MALFORMED.format(name="THREE"))
    warned = [one for one in compiling.lint(meta) if one.startswith("constraint-malformed")]
    kept = compiling.declarations(meta)
    if warned and "`nocode`" in warned[0] and "Z7" in kept:
        held("the malformed line is dropped", "the warning names it, Z7 still declared")
    else:
        failures.append(f"  ✗ the malformed line is dropped {warned} {'Z7' in kept}")
    _clear(env, "THREE.md")

    # --- the same line in a package's document: the refusal, unchanged ----------------
    _package(env, "ZTHREE", MALFORMED)
    expect("constraint-malformed", lambda: compiling.render_registry(meta))
    _clear(env)

    # --- an attach no proc hooks: warned for the author, refused for a package --------
    env.write("FOUR.md", ATTACHED.format(name="FOUR"))
    warned = [one for one in compiling.lint(meta) if one.startswith("attach-unhooked")]
    passes = compiling.render_registry(meta)
    _clear(env, "FOUR.md")
    _package(env, "ZFOUR", ATTACHED)
    expect("attach-unhooked", lambda: compiling.render_registry(meta))
    _clear(env)
    if warned and passes:
        held("the author's attach warns", f"`{warned[0][:48]}…`, the registry renders")
    else:
        failures.append(f"  ✗ the author's attach warns    {warned}")

    # --- the migration gate is not a law defect: it refuses on both sides -------------
    env.write("FIVE.md", UNSECTIONED.format(name="FIVE"))
    expect("constraints-unsectioned", lambda: compiling.render_registry(meta))
    _clear(env, "FIVE.md")
    return len(failures)
