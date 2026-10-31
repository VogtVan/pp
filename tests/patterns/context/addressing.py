"""Scenario `addressing` -- the pattern `context/addressing`, played from its demonstration:
- a bare NAME: a package's document by its name, the repository's twin never served; a name no
  search path answers at the repository's root
- a PATH is the repository's: a token carrying a `/` serves the repository's file even when the
  instance holds a homonym under `.sys/`; without it the instance answers; the ledger says the place
  (`repository`, `machine`); a shadowing is SAID once (`serve-shadowed`)
- a mount names a package's document by its bare name and a file of a package's bundle by
  `<package>:<path>`: its law in force, its body served; an absolute path, a `..`, a package not in
  play, an address no file answers refuse `mount-missing`; a mounted document gone is said once,
  `mount-gone` of level note, never on a peek
The package `shelf`, the repository's files and the machine's homonym are written at the test's time.
"""
from __future__ import annotations

import json

from conductor import render
from tests.harness import body_of, codes, demonstrated, demos, plant, traced, vendor

DRAWER, PATTERN = "context", "addressing"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("DESK.md", "FINDER.md", "LEDGER.md", "NOTE.md", "PATHS.md")
SHELF = "name: shelf\nversion: 0.0.1\ndescription: a witness package\nrequires: [kit]\n"
AT_REPO = "FROM = 'the repository'\n"
AT_MACHINE = "FROM = 'the machine'\n"
TWIN = "the repository's twin of the ledger -- never served\n"
MANUAL = "the repository's own manual\n"


def _text(name: str) -> str:
    return (DEMO / name).read_text(encoding="utf-8")


def _signals(env, name: str) -> list[dict]:
    return [one for log in sorted((env.made / ".sys" / "state").glob("session-*.jsonl"))
            for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
            if one.get("kind") == "signal" and one.get("signal") == name]


def _ledger(env, key: str) -> list[dict]:
    return [line for one in traced(env, key) if one.get("kind") == "block" for line in (one.get("served") or [])]


def names(bench, env) -> None:
    """A bare name: the package's document, the repository's root as the last resort."""
    held, failures = bench.held, bench.failures
    (env.root / "LEDGER.md").write_text(TWIN, encoding="utf-8")
    (env.root / "MANUAL.md").write_text(MANUAL, encoding="utf-8")
    runner = env.conductor("n")
    runner.forget()
    served = dict(runner.start(env.made / "procs" / "FINDER.md").payloads)
    if (served.get("LEDGER.md", "").strip() == body_of(DEMO / "LEDGER.md") and TWIN.strip() not in served.get("LEDGER.md", "")
            and served.get("MANUAL.md", "").strip() == MANUAL.strip()):
        held("a bare name resolves nearest first", "LEDGER.md served from the package shelf, its repository twin "
             "never; MANUAL.md, which no search path answers, from the repository's root")
    else:
        failures.append(f"  ✗ bare names                  {list(served)} {served.get('LEDGER.md', '')[:80]!r}")
    runner.forget()
    # --- a name shelved in a folder of procs/ answers its bare name, nearer than the package's ---
    shelved = env.write("procs/shelved/LEDGER.md", "---\nname: LEDGER\nkind: doc\n---\n\nthe instance's ledger, shelved\n")
    runner = env.conductor("n")
    runner.forget()
    folded = dict(runner.start(env.made / "procs" / "FINDER.md").payloads)
    shelved.unlink()
    if "shelved" in folded.get("LEDGER.md", "") and TWIN.strip() not in folded.get("LEDGER.md", ""):
        held("a name shelved in a folder answers", "procs/shelved/LEDGER.md answers LEDGER.md, nearer than the "
             "package's: the folder shelves, the name is the file's")
    else:
        failures.append(f"  ✗ the names                   {served!r}")
    runner.forget()


def paths(bench) -> None:
    """A path is the repository's; without it the instance answers; the place; the shadowing."""
    held, failures = bench.held, bench.failures
    env = bench.env("addressing-paths")
    plant(env, DRAWER, PATTERN, ("PATHS.md",))
    env.write(".sys/engine/x.py", AT_MACHINE)
    at_repository = env.root / "engine" / "x.py"
    at_repository.parent.mkdir(parents=True, exist_ok=True)
    at_repository.write_text(AT_REPO, encoding="utf-8")

    # --- both homonyms stand: the path is the repository's, `.sys/` addresses the machine ---
    first = env.conductor("t")
    first.forget()
    served = dict(first.start(env.made / "procs" / "PATHS.md").payloads)
    if (served.get("engine/x.py", "").strip() == AT_REPO.strip()
            and served.get(".sys/engine/x.py", "").strip() == AT_MACHINE.strip()):
        held("a path is the repository's", "`engine/x.py` serves the repository's file though "
             "the instance holds a homonym under `.sys/`; `.sys/engine/x.py` serves the machine")
    else:
        failures.append(f"  ✗ the repository's path       engine/x.py={served.get('engine/x.py')!r} "
                        f".sys/engine/x.py={served.get('.sys/engine/x.py')!r}")

    places = {line["subject"]: line.get("package") for line in _ledger(env, "t")}
    if places.get("engine/x.py") == "repository" and places.get(".sys/engine/x.py") == "machine":
        held("the ledger says the place", "`repository` for what the repository served, "
             "`machine` for what `.sys/` served")
    else:
        failures.append(f"  ✗ the place                   engine/x.py={places.get('engine/x.py')!r} "
                        f".sys/engine/x.py={places.get('.sys/engine/x.py')!r}")

    shadowed = _signals(env, "serve-shadowed")
    if len(shadowed) == 1:
        held("a shadowing is said once", "both homonyms stand: the engine pushes `serve-shadowed` "
             "for that path, one time in the run")
    else:
        failures.append(f"  ✗ the shadowing               {shadowed!r}")

    # --- the repository's file gone: the instance answers, and nothing is shadowed ----------
    at_repository.unlink()
    alone = dict(env.conductor("u").start(env.made / "procs" / "PATHS.md").payloads)
    quiet = _signals(env, "serve-shadowed")
    if alone.get("engine/x.py", "").strip() == AT_MACHINE.strip() and len(quiet) == len(shadowed):
        held("without the repository's file the instance answers", "`engine/x.py` serves the "
             "machine's copy -- what a member without the source sees -- and no shadowing is said")
    else:
        failures.append(f"  ✗ the instance alone          engine/x.py={alone.get('engine/x.py')!r} {quiet!r}")


def mounts(bench, env) -> None:
    """A mount by a package document's name and by `<package>:<path>`; the refusals; a mount gone."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    opener = env.conductor("m")
    opener.forget()
    opener.start(env.made / "procs" / "DESK.md")
    by_name = env.conductor("m").mount([{"doc": "LEDGER.md", "body": True}])
    by_package = env.conductor("m").mount([{"doc": "shelf:kinds/NOTE.md", "body": True}])
    view = env.conductor("m").peek()
    if (body_of(DEMO / "LEDGER.md") in by_name and body_of(DEMO / "NOTE.md") in by_package
            and {"AD1", "AD2"} <= set(codes(view))):
        held("a mount names a document by its address", "LEDGER.md by its bare name, shelf:kinds/NOTE.md -- "
             "outside every search path -- by its package: their laws AD1 and AD2 in force, their bodies served")
    else:
        failures.append(f"  ✗ the mounts                  {codes(view)} {by_name[-200:]!r} {by_package[-200:]!r}")

    for address in ("/etc/hosts", "../x.md", "nope:procs/X.md", "NOPE.md"):
        expect("mount-missing", lambda address=address: env.conductor("m").mount([{"doc": address}]))

    (env.made / ".sys" / "vendor" / "shelf@0.0.1" / "kinds" / "NOTE.md").unlink()
    peeked = render(env.conductor("m").peek())
    formed_at_peek = [one for one in traced(env, "m") if one.get("kind") == "diagnostic"]
    following = render(env.conductor("m").submit("a first answer"))
    following += render(env.conductor("m").submit("a second answer"))
    formed = [one for one in traced(env, "m")
              if one.get("kind") == "diagnostic" and one.get("signal") == "mount-gone"]
    weighed = [one.get("weight", {}).get("diagnostic") or 0 for one in traced(env, "m") if one.get("kind") == "block"]
    if ("mount-gone" not in peeked and not formed_at_peek and following.count("mount-gone") == 1
            and len(formed) == 1 and formed[0].get("level") == "note" and sum(1 for w in weighed if w) == 1
            and "AD2" not in codes(env.conductor("m").peek())):
        held("a mount whose document is gone says so", "NOTE removed from the bundle: the peek forms nothing, "
             f"the blocks that follow say `mount-gone` once, of level note, weighed {max(weighed)} c on the one "
             "block that rendered it, and AD2 leaves")
    else:
        failures.append(f"  ✗ mount-gone                  peek={'mount-gone' in peeked} said={following.count('mount-gone')} "
                        f"formed={formed} weighed={weighed}")
    env.conductor("m").forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("addressing")
    vendor(env.made, "shelf", SHELF, {"LEDGER": _text("LEDGER.md")})
    note = env.made / ".sys" / "vendor" / "shelf@0.0.1" / "kinds" / "NOTE.md"
    note.parent.mkdir(parents=True, exist_ok=True)
    note.write_text(_text("NOTE.md"), encoding="utf-8")
    plant(env, DRAWER, PATTERN, ("DESK.md", "FINDER.md"))
    names(bench, env)
    mounts(bench, env)
    paths(bench)                   # its own house: a homonym under `.sys/`, the repository's file removed
    return 0
