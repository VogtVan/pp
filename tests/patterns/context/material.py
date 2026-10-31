"""Scenario `material` -- the pattern `context/material`, played from its demonstration:
- the mark last: `engine/x.py @alt` reads its material in a SERVE row, a natured ranged row and a
  mount's row, no orphan `@alt`; two marks on one row refuse `material-invalid`
- the marks: (a) `@alt engine/x.py` serves `alt`'s file, titled `engine/x.py @alt`, the ledger's
  place `alt`, with a nature and tags too; (b) an unmarked row reads the repository, the title bare,
  the place `repository`; (c) a document says its own (`material: alt`), `@repo` reads the
  repository again, a CALLed document inherits, a mounted document carries its own; (d) `-new`
  under `PP_WORKDIR` writes `work` at the slot and on the `new` line, `@work` reads that tree --
  under both conductions --, the renewal mark keeps it, and without `PP_WORKDIR` `@work` says
  `material-unknown`; (e) what is missing is SAID, each a `note` DIAGNOSTIC; (f) a bare NAME
  ignores the material; (g) SETTINGS refuses `material.`, `material.repo`, `material.work` and an
  empty path; (h) the lint skips the mark, the writer accepts it, a bare `@` refuses
  `material-invalid`; (i) two contents, two hashes; one text in two trees, one
The trees `alt` and `other`, the repository's files and SETTINGS are written at the test's time.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from conductor import Refusal, persistence, reading, sections, settings, topology
from tests.harness import PRINCIPAL, cli, demonstrated, plant

KEY = re.compile(r"run ([0-9a-f]{6})")
AT_REPO = "FROM = 'the repository'\n"
AT_ALT = "FROM = 'alt'\n"
AT_OTHER = "FROM = 'other'\n"
AT_ALT_Y = "FROM = 'alt, y'\n"          # distinct texts: an identical text would be PROVEN once and spared
AT_REPO_ABSENT = "FROM = 'the repository, absent from alt'\n"
TAGGED_ALT = "head\ndef alpha():\n    return 'alt'\ndef beta():\n    return 2\n"
TAGGED_REPO = "head\ndef alpha():\n    return 'repo'\ndef beta():\n    return 2\n"
DRAWER, PATTERN = "context", "material"
DEMOS = ("BARE.md", "HEIR.md", "LACKING.md", "MARKED.md", "NODE.md", "OWNED.md", "SAME.md",
         "TRAILED.md", "TRAILING.md", "TWICE.md", "WORKER.md")


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
            and owned.get("engine/x.py", "").strip() == AT_REPO.strip()
            and heir.get("engine/y.py @alt", "").strip() == AT_ALT_Y.strip()
            and "engine/t.py @alt" in mounted and "return 'alt'" in mounted):
        held("(c) the document's material, `@repo`, the heir, the mount", "OWNED's rows read alt, its "
             "`@repo` row the repository; HEIR, CALLed without `material:`, reads alt; NODE mounts alt's t.py")
    else:
        failures.append(f"  ✗ (c) the owned material        owned={list(owned)} heir={list(heir)} "
                        f"mounted={'engine/t.py @alt' in mounted}")

    # --- (d) the run's work, under both conductions ------------------------------------------------------
    slot, first_key = None, ""
    for label, mark in (("LLM", {}), ("principal", {PRINCIPAL: "true"})):
        opened = cli(env.engine, "-new", cwd=env.root, env={"PP_WORKDIR": "other", "PP_DOOR": "WORKER.md", **mark})
        key = KEY.search(opened.stdout).group(1) if KEY.search(opened.stdout) else ""
        whole_d = opened.stdout
        for _ in range(8):           # a boot cut at the cap continues on the bare keyed call
            if "a reading continues" not in whole_d.rstrip().splitlines()[-1]:
                break
            whole_d += "\n" + cli(env.engine, key, cwd=env.root, env=mark).stdout
        at = persistence.slot_of(env.made, key) if key else None
        at_slot = persistence.material_of(at) if at else {}
        new_line = next((one for one in _trace(env.made) if one.get("kind") == "new" and one.get("run") == key), {})
        if (opened.returncode == 0 and "engine/x.py @work" in whole_d and AT_OTHER.strip() in whole_d
                and at_slot == {"name": "work", "path": "other"} and new_line.get("material") == at_slot):
            held(f"(d) the run's work ({label})", f"run {key}: `PP_WORKDIR=other` at the slot and on the "
                 "`new` line; `@work engine/x.py` serves other's file")
        else:
            failures.append(f"  ✗ (d) the work ({label})        rc={opened.returncode} slot={at_slot} new={new_line} "
                            f"{opened.stdout[-300:]!r}")
        slot, first_key = slot or at, first_key or key
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
    if (bare.returncode == 0 and "engine/x.py @work" not in whole and AT_REPO.strip() in whole
            and any("@work" in line and "material-unknown" in line for line in _diagnostics(env.made))):
        held("(d) `@work` without a material is said", f"run {bare_key}: material-unknown, the row served "
             "from the repository, a DIAGNOSTIC line")
    else:
        failures.append(f"  ✗ (d) the work unknown          rc={bare.returncode} {whole[-300:]!r} "
                        f"{_diagnostics(env.made)[-3:]}")

    # --- (e) what is missing is said -------------------------------------------------------------------
    third = env.conductor("e")
    third.forget()
    lacking = dict(third.start(env.made / "procs" / "LACKING.md").payloads)
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


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("material")
    _settings(env)
    _trees(env)
    plant(env, DRAWER, PATTERN, DEMOS)
    trailing(bench, env)           # first: its rows say no serve-stale in the whole trace
    marks(bench, env)
    return 0
