"""Scenario `material` -- 9 case(s) (plan core, phase la-lecture, batch le-materiau-des-lectures,
2026-10-07): a reading knows which TREE it reads from. A MATERIAL is a named tree -- `repo`
the repository (tacit), `work` the launcher's (`PP_WORKDIR` at `-new`), any other declared
`material.<name>: <path>` at SETTINGS; a row names one by `@<name>`, a document by
`material:`, a CALLed document inherits its caller's; the nearest word wins; a row that
names none reads exactly as it always did.
- (a) a marked row reads its material: `@alt engine/x.py` serves `alt`'s file, titled
  `engine/x.py @alt`, the ledger's place `alt`; with a nature and tags too
- (b) an unmarked row reads as today: the repository's file, the title bare, the place
  `repository`
- (c) a document says its own (`material: alt`), a row `@repo` reads the repository again, a
  CALLed document inherits, a mounted document carries its own
- (d) the launcher's `work`: `-new` under `PP_WORKDIR` writes the material at the slot and on
  the `new` line, `@work` reads that tree, the renewal mark keeps it; without `PP_WORKDIR`,
  `@work` says `material-unknown` and serves as today
- (e) what is missing is SAID: `@nope` -> `material-unknown`; a declared path that is no
  directory -> `material-missing`; a file absent from the material -> served as today, said;
  each a DIAGNOSTIC line of level `note`
- (f) a bare NAME ignores the material: `@alt TURN.md` serves the instance's document
- (g) SETTINGS refuses the badly written: `material.`, `material.repo`, `material.work`
- (h) the lint skips the mark, the writer accepts it, a bare `@` refuses `material-invalid`
- (i) the proof holds: two contents, two hashes, both served; one text in two trees, one
"""
from __future__ import annotations

import json
import re

from conductor import Refusal, persistence, reading, sections, settings, topology
from tests.harness import cli

KEY = re.compile(r"run ([0-9a-f]{6})")
AT_REPO = "FROM = 'the repository'\n"
AT_ALT = "FROM = 'alt'\n"
AT_OTHER = "FROM = 'other'\n"
AT_ALT_Y = "FROM = 'alt, y'\n"          # distinct texts: an identical text would be PROVEN once and spared
AT_REPO_ABSENT = "FROM = 'the repository, absent from alt'\n"
TAGGED_ALT = "head\ndef alpha():\n    return 'alt'\ndef beta():\n    return 2\n"
TAGGED_REPO = "head\ndef alpha():\n    return 'repo'\ndef beta():\n    return 2\n"
MARKED = """---
name: MARKED
kind: proc
description: a witness whose rows name their material
serve: |
  @alt engine/x.py
  engine/x.py
  code: @alt engine/t.py[def alpha..def beta]
  @alt TURN.md
proc: |
  SERVE
  INFER
---

The witness of the marked rows.
"""
OWNED = """---
name: OWNED
kind: proc
description: a witness whose document names its material
material: alt
serve: |
  engine/x.py
  @repo engine/x.py
proc: |
  SERVE
  CALL HEIR.md
  INFER
---

The witness of the owned material.
"""
HEIR = """---
name: HEIR
kind: proc
description: a witness that inherits its caller's material
serve: |
  engine/y.py
proc: |
  SERVE
  INFER
---

The heir.
"""
NODE = "---\nname: NODE\nkind: doc\nmaterial: alt\nserve: |\n  engine/t.py\n---\n\nthe node\n"
WORKER = """---
name: WORKER
kind: proc
description: a witness that reads the launcher's material
serve: |
  @work engine/x.py
proc: |
  SERVE
  INFER
---

The worker.
"""
LACKING = """---
name: LACKING
kind: proc
description: a witness of what a material cannot give
serve: |
  @nope engine/x.py
  @gone engine/x.py
  @alt engine/absent.py
proc: |
  SERVE
  INFER
---

The lacking.
"""
SAME = """---
name: SAME
kind: proc
description: a witness of one text in two trees
serve: |
  engine/same.py
  @alt engine/same.py
  engine/x.py
  @alt engine/x.py
proc: |
  SERVE
  INFER
---

The same.
"""


def _settings(env, extra: str = "") -> None:
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\nmaterial.alt: alt\nmaterial.other: other\n"
                             "material.gone: nowhere/at/all\n" + extra + "---\n")


def _trees(env) -> None:
    for relative, text in (("engine/x.py", AT_REPO), ("engine/t.py", TAGGED_REPO), ("engine/y.py", AT_REPO),
                           ("engine/absent.py", AT_REPO_ABSENT), ("engine/same.py", "SAME = 1\n"),
                           ("alt/engine/x.py", AT_ALT), ("alt/engine/t.py", TAGGED_ALT), ("alt/engine/y.py", AT_ALT_Y),
                           ("alt/engine/same.py", "SAME = 1\n"), ("other/engine/x.py", AT_OTHER)):
        path = env.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _trace(made) -> list[dict]:
    return [json.loads(line)
            for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def _ledger(made) -> list[dict]:
    return [line for one in _trace(made) if one.get("kind") == "block" for line in (one.get("served") or [])]


def _signals(made, name: str) -> list[dict]:
    return [one for one in _trace(made) if one.get("kind") == "signal" and one.get("signal") == name]


def _diagnostics(made) -> list[str]:
    return [one.get("line", "") for one in _trace(made) if one.get("kind") == "diagnostic"]


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("material")
    _settings(env)
    _trees(env)
    for name, text in (("MARKED.md", MARKED), ("OWNED.md", OWNED), ("HEIR.md", HEIR), ("NODE.md", NODE),
                       ("WORKER.md", WORKER), ("LACKING.md", LACKING), ("SAME.md", SAME)):
        env.write(name, text)

    # --- (a) a marked row reads its material; (b) an unmarked one reads as today ------------------------
    first = env.conductor("a")
    first.forget()
    served = dict(first.start(env.made / "MARKED.md").payloads)
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
    block = second.start(env.made / "OWNED.md")
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
            and owned.get("engine/x.py", "").strip() == AT_REPO.strip()
            and heir.get("engine/y.py @alt", "").strip() == AT_ALT_Y.strip()
            and "engine/t.py @alt" in mounted and "return 'alt'" in mounted):
        held("(c) the document's material, `@repo`, the heir, the mount", "OWNED's rows read alt, its "
             "`@repo` row the repository; HEIR, CALLed without `material:`, reads alt; NODE mounts alt's t.py")
    else:
        failures.append(f"  ✗ (c) the owned material        owned={list(owned)} heir={list(heir)} "
                        f"mounted={'engine/t.py @alt' in mounted}")

    # --- (d) the launcher's work -----------------------------------------------------------------------
    opened = cli(env.engine, "-new", cwd=env.root, env={"PP_WORKDIR": "other", "PP_DOOR": "WORKER.md"})
    key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
    slot = persistence.slot_of(env.made, key) if key else None
    at_slot = persistence.material_of(slot) if slot else {}
    new_line = next((one for one in _trace(env.made) if one.get("kind") == "new" and one.get("run") == key), {})
    if (opened.returncode == 0 and "engine/x.py @work" in opened.stdout and AT_OTHER.strip() in opened.stdout
            and at_slot == {"name": "work", "path": "other"} and new_line.get("material") == at_slot):
        held("(d) the launcher's work", f"run {key}: `PP_WORKDIR=other` at the slot and on the `new` line; "
             "`@work engine/x.py` serves other's file")
    else:
        failures.append(f"  ✗ (d) the work                  rc={opened.returncode} slot={at_slot} new={new_line} "
                        f"{opened.stdout[-300:]!r}")
    if slot is not None:
        persistence.renew(slot, {"kit": "0"}, {"kit": "1"}, "2026-10-07T00:00:00Z")
        mark = persistence.renewed(slot) or {}
        reopened = cli(env.engine, key, cwd=env.root)
        kept = persistence.material_of(slot)
        if mark.get("material") == {"name": "work", "path": "other"} and reopened.returncode == 0 and kept == mark["material"]:
            held("(d) the renewal keeps the work", "the mark carries the material, the reopened run has it")
        else:
            failures.append(f"  ✗ (d) the renewal               mark={mark.get('material')} kept={kept} rc={reopened.returncode}")
    bare = cli(env.engine, "-new", cwd=env.root, env={"PP_DOOR": "WORKER.md"})
    bare_key = KEY.search(bare.stdout).group(1) if KEY.search(bare.stdout) else ""
    unknown = [one for one in _signals(env.made, "material-unknown") if "@work" in str(one)]
    if (bare.returncode == 0 and "engine/x.py @work" not in bare.stdout and AT_REPO.strip() in bare.stdout
            and any("@work" in line and "material-unknown" in line for line in _diagnostics(env.made))):
        held("(d) `@work` without a material is said", f"run {bare_key}: material-unknown, the row served "
             "from the repository, a DIAGNOSTIC line")
    else:
        failures.append(f"  ✗ (d) the work unknown          rc={bare.returncode} {bare.stdout[-300:]!r} "
                        f"{_diagnostics(env.made)[-3:]}")

    # --- (e) what is missing is said -------------------------------------------------------------------
    third = env.conductor("e")
    third.forget()
    lacking = dict(third.start(env.made / "LACKING.md").payloads)
    lines = _diagnostics(env.made)
    said = {"unknown": any("material-unknown" in one and "@nope" in one for one in lines),
            "missing": any("material-missing" in one and "@gone" in one for one in lines),
            "absent": any("serve-stale" in one and "not in material `alt`" in one for one in lines)}
    if (all(said.values()) and lacking.get("engine/x.py", "").strip() == AT_REPO.strip()
            and lacking.get("engine/absent.py", "").strip() == AT_REPO_ABSENT.strip() and all("@" not in k for k in lacking)
            and all(" · note · " in one for one in lines if "material" in one)):
        held("(e) what is missing is said", "`@nope`: material-unknown; `@gone`: material-missing; a file "
             "absent from alt: serve-stale -- each a `note` diagnostic, the rows served from the repository")
    else:
        failures.append(f"  ✗ (e) the missing               said={said} served={list(lacking)} {lines[-4:]}")

    # --- (g) SETTINGS refuses the badly written ---------------------------------------------------------
    bad = bench.env("material-bad")
    verdicts = []
    for key_, value in (("material.", "x"), ("material.repo", "y"), ("material.work", "z"), ("material.alt", "")):
        bad.write("SETTINGS.md", f"---\nname: SETTINGS\nkind: doc\n{key_}: '{value}'\n---\n")
        try:
            settings.of(bad.made)
            verdicts.append("ok")
        except Refusal as refusal:
            verdicts.append(refusal.code)
            bench.refusals += 1
    if verdicts == ["settings-invalid"] * 4:
        held("(g) SETTINGS refuses the badly written", "an empty name, `repo`, `work` and an empty path: "
             "settings-invalid by name")
    else:
        failures.append(f"  ✗ (g) the settings              {verdicts}")

    # --- (h) the lint skips the mark, the writer accepts it, a bare `@` refuses -----------------------------
    from pathlib import Path
    scanned = topology.references(Path("w.md"), {"serve": "code: @alt engine/x.py other.md"})
    doc = env.write("WRITTEN.md", "---\nname: WRITTEN\nkind: doc\n---\n\nwritten\n")
    written = sections.serve(doc, [["@alt", "engine/x.py"]])
    back = reading.serve_sections(reading.read(doc))
    env.write("BARE.md", "---\nname: BARE\nkind: proc\ndescription: a bare mark\nserve: |\n  @ engine/x.py\n"
                         "proc: |\n  SERVE\n  INFER\n---\n\nbare\n")
    torn = env.conductor("h")
    torn.forget()
    if (scanned == [("serve", "engine/x.py"), ("serve", "other.md")]
            and back == ((("@alt", "engine/x.py"),),) and "1 line(s)" in written):
        held("(h) the lint skips the mark, the writer accepts it", "`@alt` is no document for the lint; "
             "the writer writes it and reads it back")
    else:
        failures.append(f"  ✗ (h) the lint and the writer   {scanned} {back} {written!r}")
    expect("material-invalid", lambda: torn.start(env.made / "BARE.md"))

    # --- (i) the proof: two contents, two readings; one text, one -----------------------------------------
    fourth = env.conductor("i")
    fourth.forget()
    same = dict(fourth.start(env.made / "SAME.md").payloads)
    states = [(line["subject"], line["state"]) for line in _ledger(env.made)
              if line["subject"].startswith("engine/same.py") or line["subject"].startswith("engine/x.py")]
    tail = states[-4:]
    if (("engine/same.py", "served") in tail and ("engine/same.py @alt", "spared") in tail
            and ("engine/x.py", "served") in tail and ("engine/x.py @alt", "served") in tail
            and same.get("engine/x.py", "") != same.get("engine/x.py @alt", "")):
        held("(i) the proof holds", "one text in two trees: served once, spared the second time; two "
             "contents: two readings, two hashes")
    else:
        failures.append(f"  ✗ (i) the proof                 {tail} {list(same)}")
    return 0
