"""Scenario `material` -- the pattern `context/material`, played from its demonstration:
- the mark last: `engine/x.py @alt` reads its material in a SERVE row, a natured ranged row and a
  mount's row, no orphan `@alt`; two marks on one row refuse `material-invalid`
- the marks: (a) `@alt engine/x.py` serves `alt`'s file, titled `engine/x.py @alt`, the ledger's
  place `alt`, with a nature and tags too; (b) an unmarked row reads the repository, the title bare,
  the place `repository`; (c) a document says its own (`material: alt`), a row marked otherwise
  reads its own tree, a CALLed document inherits, a mounted document carries its own; (d) `-new`
  under `PP_WORKDIR` writes the run's tree at the slot and on the `new` line, a row that names no
  tree reads it, the renewal mark keeps it, and without `PP_WORKDIR`
  the same row reads the repository; (e) the reading DUE: a row whose named tree cannot answer --
  a name no document declares (SETTINGS' `material.nope` declares nothing), a path that is no
  directory, a file the tree lacks -- is never served from another tree: the block carries a line
  in its place, the ledger says `missing` and why (`lacks`), each a `note` DIAGNOSTIC; (f) a bare
  NAME ignores the material; (g) a badly written `materials:` refuses `material-invalid`; (h) the
  lint skips the mark, the writer accepts it, a bare `@` refuses `material-invalid`; (i) two
  contents, two hashes; one text in two trees, one; (p) `repo` and `work` name no tree: a mark
  `@repo` or `@work` and a `material: repo` or `material: work` refuse `material-invalid` -- said
  by the document that carries the row, or by a caller whose `material:` its row would inherit
- the declaration: every tree is declared by a document (`materials:`, one `<name>: <path>` a line),
  its relative path read from the folder of the document that declares it; (j) a called document
  that declares a name again wins over its caller, a name it does not declare comes from the
  caller; (k) a mounted document finds its tree in the document mounted before it, and without it
  its row is missing (`material-unknown`); (l) two instances whose SETTINGS carry no `material.`
  key mount the same document of a shared root: the same reading, the same proof, titled `@tree`,
  a decoy tree of that name in the reader's workspace never read; (m) a compaction re-serves a
  called document's row from the tree it was first read in; (n) a badly written declaration
  refuses `material-invalid` when a row of a called document looks its tree up in it, never read
  as a document gone; (o) the rows an overlay adds to a called document read the tree its caller
  names and declares
The trees `alt` and `other`, the shared root, the repository's files and SETTINGS are written at
the test's time.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from conductor import Refusal, persistence, reading, sections, settings, topology
from tests.harness import cli, demonstrated, demos, plant

KEY = re.compile(r"run ([0-9a-f]{6})")
AT_REPO = "FROM = 'the repository'\n"
AT_ALT = "FROM = 'alt'\n"
AT_OTHER = "FROM = 'other'\n"
AT_ALT_Y = "FROM = 'alt, y'\n"          # distinct texts: an identical text would be PROVEN once and spared
AT_REPO_ABSENT = "FROM = 'the repository, absent from alt'\n"
AT_OTHER_Z = "FROM = 'other, z'\n"
AT_OTHER_W = "FROM = 'other, w'\n"
AT_REPO_W = "FROM = 'the repository, w'\n"
AT_ALT_U = "FROM = 'alt, u'\n"
AT_ALT_V = "FROM = 'alt, v'\n"
AT_REPO_U = "FROM = 'the repository, u'\n"
AT_REPO_V = "FROM = 'the repository, v'\n"
AT_SHARED = "FROM = 'the shared tree'\n"
AT_DECOY = "FROM = 'a tree of the reader'\n"
TAGGED_ALT = "head\ndef alpha():\n    return 'alt'\ndef beta():\n    return 2\n"
TAGGED_REPO = "head\ndef alpha():\n    return 'repo'\ndef beta():\n    return 2\n"
DRAWER, PATTERN = "context", "material"
DEMOS = ("BARE.md", "CHAIN.md", "HEIR.md", "LACKING.md", "LEAF.md", "MARKED.md", "MISCHAIN.md",
         "MISDECLARED.md", "NEAR.md", "NODE.md", "OWNED.md", "RETIRED.md", "SAME.md", "SHARED.md",
         "TRAILED.md", "TRAILING.md", "TREES.md", "TWICE.md", "WORKER.md")
CALLING = ("---\nname: CALLING\nkind: proc\ndescription: a caller that names a retired tree for the document "
           "it calls.\nmaterial: {name}\nproc: |\n  CALL HEIR.md\n  INFER\n---\n\nSay what the heir read.\n")
ROWED = ("---\nname: ROWED\nkind: proc\ndescription: a row or a document that names a retired tree.\n{front}"
         "serve: |\n  {row}\nproc: |\n  SERVE\n  INFER\n---\n\nSay what was read.\n")
OVERLAYS = ("HEIR.overlay.md",)        # placed at its base's name in the instance, for its case alone
OPENED = ("---\nname: OPENED\nkind: proc\ndescription: the door of the shared root.\n"
          "proc: |\n  INFER\n---\n\nSay hello.\n")
WRONG = ("---\nname: WRONG\nkind: proc\ndescription: a declaration badly written.\n{declared}"
         "serve: |\n  engine/x.py\nproc: |\n  SERVE\n  INFER\n---\n\nSay what was read.\n")


def _settings(env, extra: str = "") -> None:
    """SETTINGS declares no tree: the one `material.` key left there names nothing a row can read."""
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmaterial.nope: alt\n" + extra + "---\n")


def _trees(env) -> None:
    for relative, text in (("engine/x.py", AT_REPO), ("engine/t.py", TAGGED_REPO), ("engine/y.py", AT_REPO),
                           ("engine/absent.py", AT_REPO_ABSENT), ("engine/same.py", "SAME = 1\n"),
                           ("alt/engine/x.py", AT_ALT), ("alt/engine/t.py", TAGGED_ALT), ("alt/engine/y.py", AT_ALT_Y),
                           ("alt/engine/same.py", "SAME = 1\n"), ("other/engine/x.py", AT_OTHER),
                           ("other/engine/z.py", AT_OTHER_Z), ("other/engine/w.py", AT_OTHER_W),
                           ("engine/w.py", AT_REPO_W), ("engine/u.py", AT_REPO_U), ("engine/v.py", AT_REPO_V),
                           ("alt/engine/u.py", AT_ALT_U), ("alt/engine/v.py", AT_ALT_V)):
        path = env.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _logs(made) -> set:
    """-> the trace files of the instance, one per run."""
    return set((made / ".sys" / "state").glob("session-*.jsonl"))


def _trace(made, since: set = frozenset()) -> list[dict]:
    """-> every line of the traces born after `since` -- a run's lines stand in its own file,
    the files of runs born in one second in no order a name could tell."""
    return [json.loads(line)
            for log in sorted(_logs(made) - since)
            for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def _ledger(made, since: set = frozenset()) -> list[dict]:
    return [line for one in _trace(made, since) if one.get("kind") == "block"
            for line in (one.get("served") or [])]


def _signals(made, name: str) -> list[dict]:
    return [one for one in _trace(made) if one.get("kind") == "signal" and one.get("signal") == name]


def _diagnostics(made) -> list[str]:
    return [one.get("line", "") for one in _trace(made) if one.get("kind") == "diagnostic"]


def trailing(bench, env) -> None:
    """The mark last: a SERVE row, a natured ranged row, a mount's row; two marks refuse."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- (a) a SERVE row marked last ----------------------------------------------------------------------
    first = env.conductor("r")
    first.forget()
    try:
        served = dict(first.start(env.made / "procs" / "TRAILING.md").payloads)
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        served = {"raised": f"{type(raised).__name__}: {raised}"}
    tagged = served.get("engine/t.py[def alpha..def beta] @alt", "")
    if (served.get("engine/x.py @alt", "").strip() == AT_ALT.strip() and "return 'alt'" in tagged
            and "def beta" not in tagged and "@alt" not in served and not _signals(env.made, "serve-stale")):
        held("(a) a row marked last reads its material", "`engine/x.py @alt` serves alt's file, titled by it; the "
             "natured, ranged row too; no orphan `@alt`, no serve-stale")
    else:
        failures.append(f"  ✗ (a) trailing serve           {list(served)} "
                        f"stale={len(_signals(env.made, 'serve-stale'))}")

    # --- (b) the mount ------------------------------------------------------------------------------------
    try:
        mounted = env.conductor("r").mount([{"doc": "TRAILED.md"}])
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        mounted = f"{type(raised).__name__}: {raised}"
    if ("engine/y.py @alt" in mounted and AT_ALT_Y.strip() in mounted and "gone" not in mounted
            and not _signals(env.made, "serve-stale")):
        held("(b) a mounted row marked last reads its material", "TRAILED's `engine/y.py @alt` mounts alt's file, "
             "no orphan")
    else:
        failures.append(f"  ✗ (b) trailing mount           {mounted[-400:]!r} "
                        f"stale={len(_signals(env.made, 'serve-stale'))}")

    # --- (c) two marks refuse -----------------------------------------------------------------------------
    twice = env.conductor("twice")
    twice.forget()
    expect("material-invalid", lambda: twice.start(env.made / "procs" / "TWICE.md"))


def marks(bench, env) -> None:
    """The marks, the document's material, the run's work, what is missing, the proof."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- (a) a marked row reads its material; (b) an unmarked one reads as today ------------------------
    first = env.conductor("a")
    first.forget()
    served = dict(first.start(env.made / "procs" / "MARKED.md").payloads)
    places = {line["subject"]: line.get("package") for line in _ledger(env.made)}
    if (served.get("engine/x.py @alt", "").strip() == AT_ALT.strip()
            and served.get("engine/x.py", "").strip() == AT_REPO.strip()
            and places.get("engine/x.py @alt") == "alt" and places.get("engine/x.py") == "repository"):
        held("(a) a marked row reads its material", "`@alt engine/x.py` serves alt's file, titled "
             "`engine/x.py @alt`, the ledger says `alt`")
        held("(b) an unmarked row reads as today", "`engine/x.py` serves the repository, bare title, "
             "the ledger says `repository`")
    else:
        failures.append(f"  ✗ (a)(b) the marked row         {served.keys()} {places}")
    tagged = served.get("engine/t.py[def alpha..def beta] @alt", "")
    if "return 'alt'" in tagged and "def beta" not in tagged and places.get("engine/t.py[def alpha..def beta] @alt") == "alt":
        held("(a) with a nature and tags", "`code: @alt engine/t.py[def alpha..def beta]` serves the "
             "material's cut, titled by the token and the material")
    else:
        failures.append(f"  ✗ (a) the tagged marked row     {tagged!r}")

    # --- (f) a bare name ignores the material -------------------------------------------------------------
    if "TURN.md" in served and "@alt" not in " ".join(k for k in served if k.startswith("TURN")):
        held("(f) a bare name ignores the material", "`@alt TURN.md` serves the instance's TURN, no suffix")
    else:
        failures.append(f"  ✗ (f) the bare name             {[k for k in served if 'TURN' in k]}")

    # --- (c) the document's own material, `@repo`, the inheritance, the mount ----------------------------
    second = env.conductor("c")
    second.forget()
    block = second.start(env.made / "procs" / "OWNED.md")
    owned = dict(block.payloads)
    mounted = env.conductor("c").mount([{"doc": "NODE.md"}])   # before the run moves: alt's t.py is fresh here
    heir: dict = dict(owned)                            # a fused output may already carry HEIR's row
    for _ in range(4):                                  # else the bare advances open HEIR and play its SERVE
        if "engine/y.py @alt" in heir:
            break
        out = env.conductor("c").forward("")
        if out is None:
            break
        heir.update(dict(out.payloads))
    if (owned.get("engine/x.py @alt", "").strip() == AT_ALT.strip()
            and owned.get("engine/x.py @other", "").strip() == AT_OTHER.strip()
            and heir.get("engine/y.py @alt", "").strip() == AT_ALT_Y.strip()
            and "engine/t.py @alt" in mounted and "return 'alt'" in mounted):
        held("(c) the document's material, a row marked otherwise, the heir, the mount", "OWNED's rows read "
             "alt, its `@other` row the tree it names; HEIR, CALLed without `material:`, reads alt; NODE mounts "
             "alt's t.py")
    else:
        failures.append(f"  ✗ (c) the owned material        owned={list(owned)} heir={list(heir)} "
                        f"mounted={'engine/t.py @alt' in mounted}")

    # --- (m) a compaction re-serves the heir's row from the tree it was read in --------------------------
    try:
        again = env.conductor("c").compacted()
        back = dict(again.payloads) if again is not None else {}
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        back = {"raised": f"{type(raised).__name__}: {raised}"}
    if back.get("engine/y.py @alt", "").strip() == AT_ALT_Y.strip() and "engine/y.py" not in back:
        held("(m) a compaction keeps the heir's tree", "HEIR's row comes back from alt, titled "
             "`engine/y.py @alt`, as it was first served")
    else:
        failures.append(f"  ✗ (m) the re-serve              {list(back)}")

    # --- (d) the run's work ------------------------------------------------------
    opened = cli(env.engine, "-new", cwd=env.root, env={"PP_WORKDIR": "other", "PP_DOOR": "WORKER.md"})
    key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
    whole_d = opened.stdout
    for _ in range(8):           # a boot cut at the cap continues on the bare keyed call
        if "a reading continues" not in whole_d.rstrip().splitlines()[-1]:
            break
        whole_d += "\n" + cli(env.engine, key, cwd=env.root).stdout
    at = persistence.slot_of(env.made, key) if key else None
    at_slot = persistence.material_of(at) if at else {}
    new_line = next((one for one in _trace(env.made) if one.get("kind") == "new" and one.get("run") == key), {})
    if (opened.returncode == 0 and "— engine/x.py\n" in whole_d and "@work" not in whole_d
            and AT_OTHER.strip() in whole_d and AT_REPO.strip() not in whole_d
            and at_slot == {"name": "work", "path": "other"} and new_line.get("material") == at_slot):
        held(f"(d) the run's work", f"run {key}: `PP_WORKDIR=other` at the slot and on the "
             "`new` line; the row that names no tree serves other's file, its title bare")
    else:
        failures.append(f"  ✗ (d) the work        rc={opened.returncode} slot={at_slot} new={new_line} "
                        f"{opened.stdout[-300:]!r}")
    slot, first_key = at, key
    if slot is not None:
        persistence.renew(slot, {"kit": "0"}, {"kit": "1"}, "2026-10-07T00:00:00Z")
        mark = persistence.renewed(slot) or {}
        reopened = cli(env.engine, first_key, cwd=env.root)
        kept = persistence.material_of(slot)
        if mark.get("material") == {"name": "work", "path": "other"} and reopened.returncode == 0 and kept == mark["material"]:
            held("(d) the renewal keeps the work", "the mark carries the material, the reopened run has it")
        else:
            failures.append(f"  ✗ (d) the renewal               mark={mark.get('material')} kept={kept} rc={reopened.returncode}")
    bare = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "WORKER.md"})
    bare_key = KEY.search(bare.stdout).group(1) if KEY.search(bare.stdout) else ""
    whole = bare.stdout
    for _ in range(8):           # a boot cut at the cap continues on the bare keyed call
        if "a reading continues" not in whole.rstrip().splitlines()[-1]:
            break
        whole += "\n" + cli(env.engine, bare_key, cwd=env.root).stdout
    if (bare.returncode == 0 and "@work" not in whole and AT_REPO.strip() in whole
            and not any("material-unknown" in line for line in _diagnostics(env.made))):
        held("(d) without a tree of its own the run reads the repository", f"run {bare_key}: the same row "
             "serves the repository's file, nothing said")
    else:
        failures.append(f"  ✗ (d) the work unknown          rc={bare.returncode} {whole[-300:]!r} "
                        f"{_diagnostics(env.made)[-3:]}")

    # --- (e) the reading due: a named tree that cannot answer is never replaced by another ---------------
    third = env.conductor("e")
    third.forget()
    before = _logs(env.made)
    lacking = dict(third.start(env.made / "procs" / "LACKING.md").payloads)
    lines = _diagnostics(env.made)
    said = {"unknown": any("material-unknown" in one and "@nope" in one for one in lines),
            "missing": any("material-missing" in one and "@gone" in one for one in lines),
            "absent": any("serve-stale" in one and "not in material `alt`" in one for one in lines)}
    lacks = {line["subject"]: line.get("lacks") for line in _ledger(env.made, before) if line.get("state") == "missing"}
    rows = ("engine/x.py @nope", "engine/x.py @gone", "engine/absent.py @alt")
    if (all(said.values()) and all(one in lacking for one in rows)
            and lacks == {rows[0]: "material-unknown", rows[1]: "material-missing", rows[2]: "serve-stale"}
            and not any(AT_REPO.strip() in text or AT_REPO_ABSENT.strip() in text for text in lacking.values())
            and "engine/x.py" not in lacking and "engine/absent.py" not in lacking
            and all(" · note · " in one for one in lines if "material" in one)):
        held("(e) a reading due is said missing", "`@nope`, a name SETTINGS alone carries; `@gone`, a path that "
             "is no directory; a file absent from alt: each row a line of the block in place of the reading, "
             "`missing` at the ledger with what lacks, a `note` diagnostic -- nothing read from the repository")
    else:
        failures.append(f"  ✗ (e) the reading due           said={said} lacks={lacks} served={list(lacking)} {lines[-4:]}")

    # --- (g) a declaration badly written refuses ----------------------------------------------------------
    wrong = env.conductor("g")
    wrong.forget()
    expect("material-invalid", lambda: wrong.start(env.made / "procs" / "MISDECLARED.md"))
    verdicts = []
    for declared in ("materials: |\n  work: ../../alt\n", "materials: |\n  alt:\n",
                     "materials: |\n  : ../../alt\n", "materials: |\n  alt ../../alt\n",
                     "materials:\n  alt: ../../alt\n"):
        env.write("procs/WRONG.md", WRONG.format(declared=declared))
        one = env.conductor("g")
        one.forget()
        try:
            one.start(env.made / "procs" / "WRONG.md")
            verdicts.append("ok")
        except Refusal as refusal:
            verdicts.append(refusal.code)
            bench.refusals += 1
    if verdicts == ["material-invalid"] * 5 and not hasattr(settings.of(env.made), "materials"):
        held("(g) a declaration badly written refuses", "`work`, an empty path, an empty name, a line "
             "without `:` and a mapping in place of the block: material-invalid by name; SETTINGS "
             "carries no catalogue of trees")
    else:
        failures.append(f"  ✗ (g) the declaration           {verdicts} "
                        f"settings.materials={hasattr(settings.of(env.made), 'materials')}")

    # --- (p) `repo` and `work` name no tree ---------------------------------------------------------------
    gone = env.conductor("p")
    gone.forget()
    expect("material-invalid", lambda: gone.start(env.made / "procs" / "RETIRED.md"))
    verdicts = []
    for front, row in (("", "@work engine/x.py"), ("", "engine/x.py @repo"),
                       ("material: repo\n", "engine/x.py"), ("material: work\n", "engine/x.py")):
        env.write("procs/ROWED.md", ROWED.format(front=front, row=row))
        one = env.conductor("p")
        one.forget()
        try:
            one.start(env.made / "procs" / "ROWED.md")
            verdicts.append("ok")
        except Refusal as refusal:
            verdicts.append(refusal.code)
            bench.refusals += 1
    if verdicts == ["material-invalid"] * 4:
        held("(p) `repo` and `work` name no tree", "a mark `@work`, a mark `@repo` last, `material: repo` and "
             "`material: work`: material-invalid by name")
    else:
        failures.append(f"  ✗ (p) the retired names         {verdicts}")
    inherited = []
    for name in ("work", "repo"):                          # the caller says it, the heir's row would inherit it
        env.write("procs/CALLING.md", CALLING.format(name=name))
        one = env.conductor("p")
        one.forget()
        try:
            one.start(env.made / "procs" / "CALLING.md")
            for _ in range(4):                             # the bare advances open HEIR and play its SERVE
                if env.conductor("p").forward("") is None:
                    break
            inherited.append("ok")
        except Refusal as refusal:
            inherited.append(refusal.code)
            bench.refusals += 1
    if inherited == ["material-invalid"] * 2:
        held("(p) a caller that names one refuses too", "CALLING says `material: work`, then `material: repo`, and "
             "calls HEIR, whose row names no tree: material-invalid when the row looks its tree up the call")
    else:
        failures.append(f"  ✗ (p) the caller's retired name {inherited}")

    # --- (h) the lint skips the mark, the writer accepts it, a bare `@` refuses -----------------------------
    scanned = topology.references(Path("w.md"), {"serve": "code: @alt engine/x.py other.md"})
    doc = env.write("WRITTEN.md", "---\nname: WRITTEN\nkind: doc\n---\n\nwritten\n")
    written = sections.serve(doc, [["@alt", "engine/x.py"]])
    back = reading.serve_sections(reading.read(doc))
    torn = env.conductor("h")
    torn.forget()
    if (scanned == [("serve", "engine/x.py"), ("serve", "other.md")]
            and back == ((("@alt", "engine/x.py"),),) and "1 line(s)" in written):
        held("(h) the lint skips the mark, the writer accepts it", "`@alt` is no document for the lint; "
             "the writer writes it and reads it back")
    else:
        failures.append(f"  ✗ (h) the lint and the writer   {scanned} {back} {written!r}")
    expect("material-invalid", lambda: torn.start(env.made / "procs" / "BARE.md"))

    # --- (i) the proof: two contents, two readings; one text, one -----------------------------------------
    fourth = env.conductor("i")
    fourth.forget()
    before = _logs(env.made)
    same = dict(fourth.start(env.made / "procs" / "SAME.md").payloads)
    states = [(line["subject"], line["state"]) for line in _ledger(env.made, before)
              if line["subject"].startswith("engine/same.py") or line["subject"].startswith("engine/x.py")]
    tail = states[-4:]
    if (("engine/same.py", "served") in tail and ("engine/same.py @alt", "spared") in tail
            and ("engine/x.py", "served") in tail and ("engine/x.py @alt", "served") in tail
            and same.get("engine/x.py", "") != same.get("engine/x.py @alt", "")):
        held("(i) the proof holds", "one text in two trees: served once, spared the second time; two "
             "contents: two readings, two hashes")
    else:
        failures.append(f"  ✗ (i) the proof                 {tail} {list(same)}")


def _texts(pairs, title: str) -> list[str]:
    """-> the texts served under `title`, in the order the outputs carried them."""
    return [text.strip() for subject, text in pairs if subject == title]


def declared(bench, env) -> None:
    """The declaration: the nearest document that declares a name wins, in a call chain and at a mount."""
    held, failures = bench.held, bench.failures

    # --- (j) the chain of calls: the nearest declaration wins, the caller's answers the rest ------------
    chained = env.conductor("j")
    chained.forget()
    pairs: list = []
    try:
        pairs += list(chained.start(env.made / "procs" / "CHAIN.md").payloads)
        for _ in range(4):                               # the bare advances open NEAR and play its SERVE
            if _texts(pairs, "engine/z.py @side"):
                break
            out = env.conductor("j").forward("")
            if out is None:
                break
            pairs += list(out.payloads)
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        pairs.append(("raised", f"{type(raised).__name__}: {raised}"))
    if (_texts(pairs, "engine/x.py @alt") == [AT_ALT.strip(), AT_OTHER.strip()]
            and _texts(pairs, "engine/z.py @side") == [AT_OTHER_Z.strip()]):
        held("(j) the nearest declaration wins", "CHAIN declares `alt` and reads alt's module; NEAR, called, "
             "declares `alt` again and reads other's under the same mark; `side`, declared by the caller "
             "alone, answers NEAR's row")
    else:
        failures.append(f"  ✗ (j) the chain                 {[(s, x[:30]) for s, x in pairs]}")

    # --- (k) the mounted chain: the document mounted before declares the tree ---------------------------
    alone = env.conductor("k")
    alone.forget()
    alone.start(env.made / "procs" / "HEIR.md")
    try:
        bare = env.conductor("k").mount([{"doc": "LEAF.md"}])
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        bare = f"{type(raised).__name__}: {raised}"
    unknown = any("material-unknown" in one and "@branch" in one for one in _diagnostics(env.made))
    both = env.conductor("k2")
    both.forget()
    both.start(env.made / "procs" / "HEIR.md")
    try:
        mounted = env.conductor("k2").mount([{"doc": "TREES.md"}, {"doc": "LEAF.md"}])
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        mounted = f"{type(raised).__name__}: {raised}"
    if ("engine/w.py @branch" in mounted and AT_OTHER_W.strip() in mounted
            and AT_OTHER_W.strip() not in bare and AT_REPO_W.strip() not in bare and unknown):
        held("(k) a mounted document reads the tree its chain declares", "LEAF after TREES mounts other's "
             "module, titled `engine/w.py @branch`; LEAF alone says material-unknown and its row is missing: "
             "nothing read from the repository")
    else:
        failures.append(f"  ✗ (k) the mounted chain         with={mounted[-300:]!r} alone={bare[-200:]!r} "
                        f"unknown={unknown}")

    # --- (n) a declaration badly written refuses through the chain, never read as a document gone ------
    def looked() -> None:
        run = env.conductor("n")
        run.forget()
        run.start(env.made / "procs" / "MISCHAIN.md")
        for _ in range(4):                               # the bare advances open HEIR and play its SERVE
            if env.conductor("n").forward("") is None:
                break
    bench.expect("material-invalid", looked)

    # --- (o) the rows an overlay adds to a called document read its caller's tree -----------------------
    overlay = env.write("HEIR.md", (demos(DRAWER, PATTERN) / "HEIR.overlay.md").read_text(encoding="utf-8"))
    overlaid = env.conductor("o")
    overlaid.forget()
    pairs = []
    try:
        pairs += list(overlaid.start(env.made / "procs" / "OWNED.md").payloads)
        for _ in range(4):                               # the bare advances enter HEIR: its overlay's rows
            if _texts(pairs, "engine/y.py @alt"):
                break
            out = env.conductor("o").forward("")
            if out is None:
                break
            pairs += list(out.payloads)
    except Exception as raised:                           # noqa: BLE001 -- said in the failure line
        pairs.append(("raised", f"{type(raised).__name__}: {raised}"))
    overlay.unlink()
    if (_texts(pairs, "engine/v.py @alt") == [AT_ALT_V.strip()] and _texts(pairs, "engine/u.py @alt") == [AT_ALT_U.strip()]
            and not _texts(pairs, "engine/v.py") and not _texts(pairs, "engine/u.py")):
        held("(o) an overlay's rows read the caller's tree", "HEIR's overlay adds `@alt engine/v.py` and "
             "`engine/u.py`: OWNED, the caller, declares `alt` and names it -- both come from alt, titled by it")
    else:
        failures.append(f"  ✗ (o) the overlay's rows        {[(s, x[:30]) for s, x in pairs if s.startswith('engine/')]}")


def shared(bench) -> None:
    """Two instances without a `material.` key mount one document of a shared root: one reading."""
    held, failures = bench.held, bench.failures
    root = bench.temp() / "shared"
    (root / "tree" / "engine").mkdir(parents=True)
    (root / "tree" / "engine" / "x.py").write_text(AT_SHARED, encoding="utf-8")
    (root / "SHARED.md").write_text((demos(DRAWER, PATTERN) / "SHARED.md").read_text(encoding="utf-8"),
                                    encoding="utf-8")
    (root / "OPENED.md").write_text(OPENED, encoding="utf-8")
    seen = []
    for name, decoy in (("material-one", False), ("material-two", True)):
        env = bench.env(name)
        if decoy:                                         # a tree of the same name in the reader's workspace
            (env.root / "tree" / "engine").mkdir(parents=True)
            (env.root / "tree" / "engine" / "x.py").write_text(AT_DECOY, encoding="utf-8")
        given = {"PP_DOCUMENTS": str(root), "PP_DOOR": "OPENED.md"}
        opened = cli(env.engine, "-new", cwd=env.root, env=given)
        key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
        whole = opened.stdout
        for _ in range(8):           # a boot cut at the cap continues on the bare keyed call
            if not whole.strip() or "a reading continues" not in whole.rstrip().splitlines()[-1]:
                break
            whole += "\n" + cli(env.engine, key, cwd=env.root).stdout
        mounted = cli(env.engine, key, "-mount", "SHARED.md", cwd=env.root) if key else None
        out = mounted.stdout if mounted is not None else ""
        slot = persistence.slot_of(env.made, key) if key else None
        proven = set((persistence._read(slot) or {}).get("proven", [])) if slot else set()
        tag = env.conductor(key)._reading(root / "tree" / "engine" / "x.py", ())[1] if key else ""
        place = {line["subject"]: line.get("package") for line in _ledger(env.made)}.get("engine/x.py @tree")
        seen.append({"rc": mounted.returncode if mounted is not None else None,
                     "titled": "engine/x.py @tree" in out, "text": AT_SHARED.strip() in out,
                     "decoy": AT_DECOY.strip() in out, "proof": tag if tag in proven else "", "place": place,
                     "keys": "material." in env.read("SETTINGS.md"),
                     "digest": hashlib.sha256(out[out.find("engine/x.py @tree"):].encode()).hexdigest()
                     if "engine/x.py @tree" in out else ""})
    if (len(seen) == 2 and all(one["rc"] == 0 and one["titled"] and one["text"] and not one["decoy"]
                               and one["proof"] and one["place"] == "tree" and not one["keys"] for one in seen)
            and seen[0]["proof"] == seen[1]["proof"]):
        held("(l) two instances, one reading", "no `material.` key at either SETTINGS; both mount SHARED.md of "
             "the shared root and read `engine/x.py @tree` from the tree beside it -- the same text, the same "
             "proof, the ledger's place `tree`; the reader's own `tree` is never read")
    else:
        failures.append(f"  ✗ (l) the shared document       {seen}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS + OVERLAYS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS + OVERLAYS)!r}")
        return 0
    env = bench.env("material")
    _settings(env)
    _trees(env)
    plant(env, DRAWER, PATTERN, DEMOS)
    trailing(bench, env)           # first: its rows say no serve-stale in the whole trace
    marks(bench, env)
    declared(bench, env)
    shared(bench)
    return 0
