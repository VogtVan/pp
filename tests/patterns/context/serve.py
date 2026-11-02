"""Scenario `serve` -- the pattern `context/serve`, played from its demonstration:
- SERVE: the tool reads, the reading rides the block of the next step, or of the parked closing when
  nothing is asked; one row of several documents is one SERVE; a bare SERVE reads one SECTION, the
  next bare SERVE the next one, one too many refuses `serve-exhausted`; a section serves whole; a
  document is proven once, by content too; a served document says its title; a bare name reaches
  the repository's root, the instance keeping the upper hand; a proven reading stays spared from one
  passage to the next -- under both conductions
- the rows: a token with blanks, between two tags, by a section, a `SERVE <doc>` and a mount alike,
  titled as written, spared when proven; what is absent is said (`serve-stale`), what is badly
  written refuses `serve-range-malformed`; a text file serves whole, a line range serves its lines;
  a CALLed body rides once under `once`, every time under `always`
- a mount plays its document's rows: softly (a gone document said, a range clamped), the stale latch
  held, a proven reading silent; a row that refuses mounts nothing, nor does its chain, and the
  repaired gesture plays whole; a mount's `body` may be a list of selections, stacked or nested,
  spared once proven, back after a compaction, said when absent, refused when badly written
- one grammar: the reader, the writer and the lint's scan give a token the same name and verdict;
  two tags cut a `.md`, a `.py` and a `.yaml` alike; the writer writes what the reader reads back and
  discourages a line range; a line range serves its lines; a gone document refuses
The repository's files a row names are written at the test's time.
"""
from __future__ import annotations

import json

from pathlib import Path

from conductor import Refusal, persistence, reading, render, sections, topology
from tests.harness import body_of, demonstrated, demos, plant, principal, steady, traced

DRAWER, PATTERN = "context", "serve"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("ALONE.md", "ATOMIC.md", "BUNDLE.md", "CALLER.md", "CHAIN1.md", "CHAIN2.md", "CHAIN3.md",
         "COPY.md", "DESK.md", "FRAMING.md", "FRAMING2.md", "GLOSSARY.md", "NOTES.md", "ONCE.md",
         "ONE.md", "OVERRUN.md", "PACED.md", "PARTS.md", "RANGE.md", "RIDE.md", "ROOTED.md",
         "SECTION.md", "STYLE.md", "TAGGED.md", "TORN.md", "TWICE.md", "TWINS.md", "WHOLE.md")
PARTS = ["## Beta..## Gamma", "## Delta.."]
WELL = {
    "d.md": ("d.md", (), None),
    "d.md[2-3,5-9]": ("d.md", ((2, 3), (5, 9)), None),
    "d.py[def a..def b]": ("d.py", (), ("def a", "def b")),
    "d.md[## Target..## Tests]": ("d.md", (), ("## Target", "## Tests")),
    "d.md[..## Target]": ("d.md", (), ("", "## Target")),
    "d.md[## Delivery..]": ("d.md", (), ("## Delivery", "")),
}
TORN = ("d.md[..]", "d.md[a..b..c]", "d.md[abc]", "d.md[## A")
TORN_LINES = ("d.md[3-2]", "d.md[0-4]", "d.md[2-5,4-9]", "d.md[9-12,2-4]", "d.md[a-b]")

# one witness per kind of document: a head, a line that MENTIONS the second tag before it
# stands, then three tagged parts -- the third one indented
WITNESSES = {
    "W.md": (("## Alpha", "## Beta", "## Gamma"), "## Be",
             "# Title\nsee ## Beta below\n## Alpha\na1\n## Beta\nb1\nb2\n  ## Gamma\ng1\n"),
    "w.py": (("def alpha", "def beta", "def gamma"), "def be",
             "import os\n# def beta comes second\ndef alpha():\n    return 1\ndef beta():\n"
             "    x = 2\n    return x\n  def gamma():\n    return 3\n"),
    "w.yaml": (("alpha:", "beta:", "gamma:"), "bet",
               "top: 0\n# beta: comes second\nalpha:\n  a: 1\nbeta:\n  b: 1\n  c: 2\n"
               "  gamma:\n  g: 1\n"),
}

LINES = ("d.md[3-2]", "d.md[0-4]", "d.md[2-5,4-9]", "d.md[9-12,2-4]", "d.md[a-b]")

# one witness per kind of document: a head, a line that MENTIONS the second tag before it
# stands, then three tagged parts -- the third one indented
WITNESSES = {
    "W.md": (("## Alpha", "## Beta", "## Gamma"), "## Be",
             "# Title\nsee ## Beta below\n## Alpha\na1\n## Beta\nb1\nb2\n  ## Gamma\ng1\n"),
    "w.py": (("def alpha", "def beta", "def gamma"), "def be",
             "import os\n# def beta comes second\ndef alpha():\n    return 1\ndef beta():\n"
             "    x = 2\n    return x\n  def gamma():\n    return 3\n"),
    "w.yaml": (("alpha:", "beta:", "gamma:"), "bet",
               "top: 0\n# beta: comes second\nalpha:\n  a: 1\nbeta:\n  b: 1\n  c: 2\n"
               "  gamma:\n  g: 1\n"),
}

PROC = """---
name: TAGGED
kind: proc
description: a witness whose rows carry tokens with blanks
serve: |
  reference: W.md[## Beta..## Gamma] NOTE.md
  reference: W.md[## Beta..## Gamma]
  reference: W.md[## Nowhere..## Gamma] W.md[## Alpha..## Nowhere]
proc: |
  SERVE
  SERVE W.md[..## Alpha]
  INFER
---

The witness of the tagged rows.
"""
BAD = "---\nname: BAD\nkind: proc\ndescription: a badly written row\nserve: |\n  {row}\nproc: |\n  SERVE\n  INFER\n---\n\nbad\n"

CODE = "def served_whole():\n    return 1\n\n\nclass Bare:\n    pass\n"
LINES = "ligne un\nligne deux\nligne trois\nligne quatre\nligne cinq\n"
CODE = "def served_whole():\n    return 1\n\n\nclass Bare:\n    pass\n"


def _text(name: str) -> str:
    return (DEMO / name).read_text(encoding="utf-8")


def _signals(env) -> int:
    return sum(1 for log in sorted((env.made / ".sys" / "state").glob("session-*.jsonl"))
               for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
               if one.get("kind") == "signal" and one.get("signal") == "serve-stale")


def _read(block) -> list[tuple[str, str]]:
    """-> the readings a block carries, the playing proc's own body set apart."""
    return [(name, text) for name, text in block.payloads if name != block.document] if block else []


def _ledger(env, key: str) -> list[dict]:
    return [line for one in traced(env, key) if one.get("kind") == "block" for line in (one.get("served") or [])]


def serving(bench) -> None:
    """SERVE: what rides, when, section by section, once."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("serve", bare=True)
    plant(env, DRAWER, PATTERN, DEMOS)
    style, notes = (body_of(DEMO / name) for name in ("STYLE.md", "NOTES.md"))

    def opened(name: str):
        runner = env.conductor("t")
        runner.forget()
        return runner.start(env.made / "procs" / name)

    riding = opened("RIDE.md")
    if [name for name, _ in _read(riding)] == ["STYLE.md"] and riding.instruction.keyword == "INFER":
        held("SERVE rides the block", "RIDE's SERVE asks nothing: STYLE rides the block of its INFER")
    else:
        failures.append(f"  ✗ the ride                    {_read(riding)!r}")
    alone = opened("ALONE.md")
    if alone.wait and [name for name, _ in _read(alone)] == ["STYLE.md"] and style in _read(alone)[0][1]:
        held("served with nothing to ask", "ALONE's only step is a SERVE: STYLE rides the parked closing")
    else:
        failures.append(f"  ✗ alone                       {_read(alone)!r}")
    bundled = opened("BUNDLE.md")
    if bundled.wait and [name for name, _ in _read(bundled)] == ["STYLE.md", "GLOSSARY.md"]:
        held("one row, one SERVE", "STYLE and GLOSSARY on one row ride the same call")
    else:
        failures.append(f"  ✗ the row                     {_read(bundled)!r}")
    paced = opened("PACED.md")
    following = env.conductor("t").submit("")
    if ([name for name, _ in _read(paced)] == ["STYLE.md"] and paced.instruction.keyword == "INFER"
            and following.wait and [name for name, _ in _read(following)] == ["GLOSSARY.md"]):
        held("a bare SERVE reads one section, the next follows", "PACED's first SERVE brings STYLE's "
             "section; GLOSSARY's waits for the second, once the INFER is answered")
    else:
        failures.append(f"  ✗ the pace                    {_read(paced)!r} {_read(following)!r}")
    env.conductor("t").forget()
    expect("serve-exhausted", lambda: opened("OVERRUN.md"))
    section = opened("SECTION.md")
    if [name for name, _ in _read(section)] == ["STYLE.md", "GLOSSARY.md", "NOTES.md"]:
        held("a section serves whole", "three lines, one section, one SERVE")
    else:
        failures.append(f"  ✗ the section                 {_read(section)!r}")
    opened("ONCE.md")
    second = env.conductor("t").submit("")
    third = env.conductor("t").submit("")
    if ([name for name, _ in _read(second)] == ["NOTES.md"] and dict(_read(second))["NOTES.md"].strip() == notes
            and third.wait and not _read(third)):
        held("a document is proven once", "STYLE in two sections rides once; an explicit SERVE GLOSSARY.md "
             "after its section renders nothing")
    else:
        failures.append(f"  ✗ proven once                 {_read(second)!r} {_read(third)!r}")
    titled = opened("ALONE.md")
    if "▌ INFORMATION — STYLE" in render(titled):
        held("a served document says its title", "one titled section per reading")
    else:
        failures.append("  ✗ the title")
    twins = opened("TWINS.md")
    if [name for name, _ in _read(twins)] == ["TWICE.md"]:
        held("the same content is served once", "TWICE and COPY hold the same bytes: COPY renders nothing")
    else:
        failures.append(f"  ✗ the twins                   {_read(twins)!r}")
    env.conductor("t").forget()

    (env.root / "README.md").write_text("the repo's own readme\n", encoding="utf-8")
    (env.root / "design").mkdir(exist_ok=True)
    (env.root / "design" / "target.md").write_text("the target\n", encoding="utf-8")
    env.write("OWN.md", "the member's\n")
    (env.root / "OWN.md").write_text("the repo's twin -- never served\n", encoding="utf-8")
    rooted = dict(_read(opened("ROOTED.md")))
    if (rooted.get("README.md", "").startswith("the repo's own readme")
            and rooted.get("design/target.md", "").startswith("the target")
            and rooted.get("OWN.md", "").startswith("the member's") and "gone" in rooted.get("NOWHERE.md", "")):
        held("a bare name reaches the repository's root", "README.md and design/target.md served from the "
             "repository; the instance's OWN wins over its twin; NOWHERE is said gone")
    else:
        failures.append(f"  ✗ the root                    {sorted(rooted)}")
    env.conductor("t").forget()


def passages(bench) -> None:
    """A proven reading stays spared from one passage to the next, under both conductions."""
    held, failures = bench.held, bench.failures
    for label, conduct in (("LLM", lambda call: call()), ("principal", principal)):
        env = bench.env(f"serve-{label.lower()}", bare=True)
        plant(env, DRAWER, PATTERN, ("RIDE.md", "STYLE.md"))
        opener = env.conductor()
        first = conduct(lambda: opener.start(env.made / "procs" / "RIDE.md"))
        key = opener.run_id
        block = conduct(lambda: env.conductor(key).submit(""))
        while block is not None and not block.wait:
            block = conduct(lambda: env.conductor(key).submit(""))
        again = conduct(lambda: env.conductor(key).submit("the next message"))
        states = [line["state"] for line in _ledger(env, key) if line["subject"] == "STYLE.md"]
        if ("STYLE.md" in dict(_read(first)) and again is not None
                and not _read(again) and states[:2] == ["served", "spared"]):
            held(f"a proven reading stays spared ({label})", "STYLE served at the first passage, spared at the "
                 "next one, its line `spared` in the ledger")
        else:
            failures.append(f"  ✗ across passages ({label})    {states} {again and _read(again)!r}")
        env.conductor(key).forget()


def rows(bench) -> None:
    """The rows: blanks, tags, the absent, the badly written, a whole file, a range, a CALLed body."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("serve-rows", bare=True)
    plant(env, DRAWER, PATTERN, DEMOS)
    lines = body_of(DEMO / "GLOSSARY.md").splitlines()
    raw = (DEMO / "GLOSSARY.md").read_text(encoding="utf-8").splitlines()

    opener = env.conductor("t")
    opener.forget()
    before = _signals(env)
    tagged = opener.start(env.made / "procs" / "TAGGED.md")
    texts = dict(tagged.payloads)
    titles = [name for name, _ in tagged.payloads if name.startswith(("GLOSSARY", "NOTES"))]
    states = [(line["subject"], line["state"]) for line in _ledger(env, "t")]
    between = "\n".join(lines[lines.index(next(one for one in lines if one.startswith("draft --"))):
                              lines.index(next(one for one in lines if one.startswith("finding --")))])
    if (titles[:2] == ["GLOSSARY.md[draft --..finding --]", "NOTES.md"]
            and texts["GLOSSARY.md[draft --..finding --]"].strip() == between
            and states.count(("GLOSSARY.md[draft --..finding --]", "spared")) == 1
            and texts.get("GLOSSARY.md[..draft --]", "").strip() == "\n".join(raw[:raw.index(lines[0])]).strip()):
        held("a row with blanks is cut right", "the reading between two tags titled as written, spared the "
             "second time; a `SERVE <doc>` with a tag served")
    else:
        failures.append(f"  ✗ the tagged row              {titles} {states}")
    if (("GLOSSARY.md[nowhere --..finding --]", "missing") in states
            and texts.get("GLOSSARY.md[draft --..nowhere --]", "").strip().endswith(lines[-1])
            and _signals(env) - before == 2):
        held("what is absent is said", "a start tag gone: `missing`; an end tag gone: served to the end; "
             "`serve-stale` for each")
    else:
        failures.append(f"  ✗ the absent tags             {states} {_signals(env) - before}")
    mounted = env.conductor("t").mount([{"doc": "FRAMING2.md"}])
    if ("GLOSSARY.md[verdict --..ground --]\n" in mounted and lines[1] in mounted
            and lines[-1] not in mounted):
        held("a mount's row reads the same", "the tagged token of a mounted document served under its title")
    else:
        failures.append(f"  ✗ the mount's row             {mounted[-300:]!r}")
    torn = _text("TORN.md")
    for token in ("GLOSSARY.md[..]", "GLOSSARY.md[a..b..c]", "GLOSSARY.md[abc]", "GLOSSARY.md[## Beta"):
        env.write("procs/TORN.md", torn.replace("GLOSSARY.md[..]", token))
        runner = env.conductor("b")
        runner.forget()
        expect("serve-range-malformed", lambda runner=runner: runner.start(env.made / "procs" / "TORN.md"))
    plant(env, DRAWER, PATTERN, ("TORN.md",))

    (env.root / "TOOL.py").write_text(CODE, encoding="utf-8")
    whole = env.conductor("w")
    whole.forget()
    served = dict(whole.start(env.made / "procs" / "WHOLE.md").payloads).get("TOOL.py", "")
    tool = env.root / "TOOL.py"
    if served.strip() == CODE.strip() and reading.served(tool)[1] != reading.sliced(tool, ((1, 2),))[1]:
        held("a text file serves whole", "a code file named without a range rides entire, its hash "
             "taken on what was served -- the slice hashes otherwise")
    else:
        failures.append(f"  ✗ the whole file              {served[-60:]!r}")
    ranged = env.conductor("r")
    ranged.forget()
    got = dict(ranged.start(env.made / "procs" / "RANGE.md").payloads).get("GLOSSARY.md[7-8]", "")
    if got.strip() == "\n".join(raw[6:8]).strip():
        held("a line range serves its lines", "GLOSSARY.md[7-8]: the file's lines 7 and 8, front matter counted")
    else:
        failures.append(f"  ✗ the range                   {got!r}")
    brief = body_of(DEMO / "ONE.md")
    for regime in ("once", "always"):
        env.write("SETTINGS.md", f"---\nname: SETTINGS\nkind: doc\nproc_body_serve: {regime}\n---\n")
        calls = env.conductor("o")
        calls.forget()
        first = dict(calls.start(env.made / "procs" / "CALLER.md").payloads).get("ONE", "")
        second = env.conductor("o").submit("")
        second_text = dict(second.payloads).get("ONE", "") if second else ""
        if first.startswith(brief) and (second_text == "" if regime == "once" else brief in second_text):
            held(f"a CALLed body under {regime}", "the first CALL serves ONE's brief; the second " +
                 ("renders nothing" if regime == "once" else "serves it again"))
        else:
            failures.append(f"  ✗ the body under {regime:<10} {first[:30]!r} / {second_text[:40]!r}")
        env.conductor("o").forget()


def mounts(bench) -> None:
    """A mount plays its rows: softly, latched, silent once proven, atomic; and its selections."""
    held, failures = bench.held, bench.failures
    env = bench.env("serve-mount", bare=True)
    plant(env, DRAWER, PATTERN, DEMOS)
    slot = persistence.slot_of(env.made, "t")
    env.conductor("t").start(env.made / "procs" / "DESK.md")
    out = env.conductor("t").mount([{"doc": "FRAMING.md"}])
    if (body_of(DEMO / "STYLE.md") in out and "GHOSTED.md" in out and "(this section's document is gone)" in out
            and "INFORMATION — GLOSSARY.md[2-99]" in out and "INFORMATION — STYLE.md" in out):
        held("a mount plays its rows, softly", "FRAMING's readings ride the mount titled by their tokens; "
             "a gone document skips with its note, a clipped range clamps")
    else:
        failures.append(f"  ✗ the soft rows               {out[:200]!r}")
    latched = [one for one in persistence.signals_of(slot) if one.get("signal") == "serve-stale"]
    if latched and latched[0].get("n", 0) >= 1:
        held("a stale serve latches", f"serve-stale stands at the slot (n={latched[0]['n']})")
    else:
        failures.append(f"  ✗ the latch                   {latched!r}")
    silent = env.conductor("t").mount([{"doc": "FRAMING2.md", "constraints": False}])
    if body_of(DEMO / "STYLE.md") not in silent:
        held("a proven reading is silent at the mount", "STYLE rode the first mount; the second renders nothing for it")
    else:
        failures.append(f"  ✗ the silence                 {silent[:160]!r}")

    before_view, before_state = steady(render(env.conductor("t").peek())), persistence.mounted_of(slot)
    refused = None
    try:
        env.conductor("t").mount([{"doc": "ATOMIC.md"}])
    except Refusal as wrong:
        refused = wrong
    bench.refusals += 1
    if (refused is not None and "ATOMIC" in str(refused) and steady(render(env.conductor("t").peek())) == before_view
            and persistence.mounted_of(slot) == before_state):
        held("a refusing row mounts nothing", f"`{refused.code}` names ATOMIC's row; the view and the slot unmoved")
    else:
        failures.append(f"  ✗ the refusing row            {refused!r}")
    env.write("procs/ATOMIC.md", _text("ATOMIC.md").replace("GLOSSARY.md[3-1]", "GLOSSARY.md"))
    replayed = env.conductor("t").mount([{"doc": "ATOMIC.md"}])
    if len(persistence.mounted_of(slot)) == len(before_state) + 1 and "GLOSSARY.md" in replayed:
        held("the repaired mount plays whole", "the same gesture mounts ATOMIC and serves its row")
    else:
        failures.append(f"  ✗ the replay                  {len(persistence.mounted_of(slot))}")
    chain_before, chain_refused = persistence.mounted_of(slot), None
    try:
        env.conductor("t").mount([{"doc": "CHAIN1.md"}, {"doc": "CHAIN2.md"}, {"doc": "CHAIN3.md"}])
    except Refusal as wrong:
        chain_refused = wrong
    bench.refusals += 1
    chain_after = persistence.mounted_of(slot)
    again = env.conductor("t").mount([{"doc": "CHAIN1.md"}, {"doc": "CHAIN2.md"}])
    if (chain_refused is not None and chain_after == chain_before and isinstance(again, str)
            and len(persistence.mounted_of(slot)) == len(chain_before) + 2):
        held("a refusing chain mounts nothing", f"`{chain_refused.code}` on CHAIN3 keeps the two before it "
             "out; the same two mount afterwards")
    else:
        failures.append(f"  ✗ the chain                   {chain_refused!r}")
    env.conductor("t").forget()


def selections(bench) -> None:
    """A mount's `body` as a list of selections: stacked, spared, kept, nested, absent, refused."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("serve-parts")
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    plant(env, DRAWER, PATTERN, ("DESK.md", "PARTS.md"))
    titles = [f"PARTS[{part}]" for part in PARTS]

    def opened(key: str):
        runner = env.conductor(key)
        runner.forget()
        runner.start(env.made / "procs" / "DESK.md")
        return lambda: env.conductor(key)

    said = opened("s")().mount([{"doc": "PARTS.md", "body": PARTS}])
    if (all(f"INFORMATION — {title}\n" in said for title in titles) and "## Beta\nb1\nb2" in said
            and "## Delta\nd1" in said and "a1" not in said and "g1" not in said):
        held("a stacked entry serves its parts", "two readings under `PARTS[<selection>]`, the rest left out")
    else:
        failures.append(f"  ✗ the stacked parts           {said[-300:]!r}")
    again = env.conductor("s").mount([{"doc": "PARTS.md", "body": PARTS, "constraints": False}])
    states = [(line["subject"], line["state"], line.get("origin")) for line in _ledger(env, "s")
              if line["subject"].startswith("PARTS[")]
    path = env.made / "procs" / "PARTS.md"
    hashes = {reading.served(path)[1], *(reading.spanned(path, reading.ranged(f"x[{part}]")[1].span)[1]
                                         for part in PARTS)}
    if (states.count((titles[0], "served", "mount")) == 1 and states.count((titles[0], "spared", "mount")) == 1
            and "b1" not in again and len(hashes) == 3):
        held("a part is proven and spared", "served once, `spared` at the second mount, origin `mount`; "
             "the hash of a part is not the body's")
    else:
        failures.append(f"  ✗ the spared parts            {states}")
    kept = persistence.mounted_of(persistence.slot_of(env.made, "s"))
    back = {subject for subject, _ in env.conductor("s").compacted().payloads}
    reserved = [line["subject"] for line in _ledger(env, "s") if line.get("state") == "reserved"]
    if kept and kept[0]["body"] == PARTS and set(titles) <= back and set(titles) <= set(reserved):
        held("the selection comes back", "the list stands at the slot; after `-compacted` the parts serve "
             "again, `reserved`")
    else:
        failures.append(f"  ✗ the re-serve                {kept!r} {sorted(back)}")
    nested = opened("n")().mount([{"doc": "PARTS.md", "scope": "nested", "body": PARTS}])
    returned = {subject for subject, _ in env.conductor("n").compacted().payloads}
    if ("▸ PARTS" in nested and all(f"INFORMATION — {title}\n" in nested for title in titles)
            and "## Beta\nb1\nb2" in nested and "a1" not in nested and set(titles) <= returned):
        held("a nested entry serves its parts", "the same two readings under the segment's heading, and "
             "back after `-compacted`")
    else:
        failures.append(f"  ✗ the nested parts            {nested[-300:]!r}")
    before = _signals(env)
    absent = opened("a")().mount([{"doc": "PARTS.md", "body": ["## Nowhere..## Gamma", "## Delta.."]}])
    missing = [line["subject"] for line in _ledger(env, "a") if line.get("state") == "missing"]
    if "PARTS[## Nowhere..## Gamma]" in missing and _signals(env) == before + 1 and "## Delta\nd1" in absent:
        held("an absent tag is said", "`missing` for that part, `serve-stale` pushed, the other part served")
    else:
        failures.append(f"  ✗ the absent part             {missing}")
    torn = opened("x")
    slot = persistence.slot_of(env.made, "x")
    frozen = slot.read_bytes()
    for body in ([".."], ["a..b..c"], [], [3]):
        expect("mount-invalid", lambda body=body: torn().mount([{"doc": "PARTS.md", "body": body}]))
    if slot.read_bytes() == frozen:
        held("a refused selection writes nothing", "four badly written selections, the slot untouched")
    else:
        failures.append("  ✗ the slot moved")
    opened("w")().mount([{"doc": "PARTS.md", "body": True}])
    served = [line for line in _ledger(env, "w") if line.get("origin") == "mount" and line.get("state") == "served"]
    heavy = max((line.get("chars", 0) for line in served if line["subject"] == "PARTS"), default=0)
    thin = max((line.get("chars", 0) for line in _ledger(env, "s") if line["subject"] == titles[0]), default=0)
    if 0 < thin < heavy:
        held("the trace tells the effect", f"{heavy} c mounted whole, {thin} c for one selection")
    else:
        failures.append(f"  ✗ the weight                  whole={heavy} selection={thin}")


def _verdict(call) -> str:
    try:
        call()
    except Refusal as refusal:
        return refusal.code
    return "ok"


def grammar(bench) -> None:
    """One grammar for the reader, the writer and the lint's scan; the cut between two tags on three kinds
    of document; the writer and the reader agree; a line range; a gone document."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("serve-grammar", bare=True)
    # --- the table: one grammar, three readers ---------------------------------------------
    wrong = []
    for token, (name, ranges, span) in WELL.items():
        read_name, cut = reading.ranged(token)
        scanned = topology.references(Path("w.md"), {"serve": f"reference: {token} other.md"})
        if not (read_name == name and cut == ranges and getattr(cut, "span", None) == span
                and bool(cut) == bool(ranges or span)
                and _verdict(lambda token=token: sections.valid_token(token)) == "ok"
                and scanned == [("serve", name), ("serve", "other.md")]):
            wrong.append(token)
    for token in TORN:
        verdicts = {_verdict(lambda token=token: reading.ranged(token)),
                    _verdict(lambda token=token: sections.valid_token(token)),
                    _verdict(lambda token=token: topology.references(Path("w.md"), {"serve": token}))}
        if verdicts != {"serve-range-malformed"}:
            wrong.append(f"{token} -> {sorted(verdicts)}")
    if not wrong:
        held("one grammar, three readers", f"{len(WELL)} well-formed and {len(TORN)} torn tokens: "
             "the reader, the writer and the lint's scan give the same names and verdicts")
    else:
        failures.append(f"  ✗ the table of tokens         {wrong}")

    # --- the cut between two tags, the same cases on three kinds of document ---------------
    for name, (tags, prefix, text) in WITNESSES.items():
        path = env.write(name, text)
        lines = text.splitlines()
        at = [next(i for i, line in enumerate(lines) if line.lstrip().startswith(tag)) for tag in tags]
        expected = {
            (tags[1], tags[2]): lines[at[1]:at[2]],
            ("", tags[1]): lines[:at[1]],
            (tags[2], ""): lines[at[2]:],
            (prefix, tags[2]): lines[at[1]:at[2]],
            (tags[2], tags[1]): lines[at[2]:],          # the end is sought AFTER the start
        }
        off = []
        hashes = {reading.served(path)[1]}
        for span, want in expected.items():
            got, tag, missing = reading.spanned(path, span)
            if got != "\n".join(want) + "\n" or missing != ("end" if span == (tags[2], tags[1]) else ""):
                off.append((span, got, missing))
            hashes.add(tag)
        gone = reading.spanned(path, ("nowhere at all", tags[2]))
        if not off and gone[0] == "" and gone[2] == "start" and len(hashes) == 4:
            held(f"two tags cut a {path.suffix}", "both tags, an open start, an open end, a prefix; "
                 "the mention before the tag ignored, the end excluded, the selection hashed")
        else:
            failures.append(f"  ✗ the cut of {name:<17}{off} {gone} {len(hashes)} hashes")

    # --- the writer: what it writes reads back, and a line range is discouraged ------------
    doc = env.write("WRITTEN.md", "---\nname: WRITTEN\nkind: doc\n---\n\nwritten\n")
    row = ["reference:", "W.md[## Beta..## Gamma]", "NOTE.md"]
    quiet = sections.serve(doc, [row])
    back = reading.serve_sections(reading.read(doc))
    loud = sections.serve(doc, [["w.py[1-2]", "w.py[def alpha..]"]])
    if (back == ((tuple(row),),) and "w.py[" not in quiet and "W.md" not in quiet
            and loud.count("w.py[1-2]") == 1 and "w.py[def alpha..]" not in loud
            and "prefer tags" in loud):
        held("the writer and the reader agree", "a row with blanks reads back identical; the answer "
             "discourages a line range and says nothing of a whole or a tagged token")
    else:
        failures.append(f"  ✗ the writer                  {back!r} {quiet!r} {loud!r}")

    expect("document-missing", lambda: reading.served(env.made / "NOWHERE.md"))
    ranged_doc = env.write("notes-banc.py", LINES)
    _, cut = reading.ranged("notes-banc.py[2-3,5-9]")
    sliced_text, sliced_hash = reading.sliced(ranged_doc, cut)
    same_text, same_hash = reading.sliced(ranged_doc, cut)
    want = "".join(LINES.splitlines(keepends=True)[i] for i in (1, 2, 4))
    torn = []
    for bad in TORN_LINES:
        try:
            reading.ranged(bad)
        except Refusal as refusal:
            torn.append(refusal.code)
    if (sliced_text == want and sliced_text == same_text and sliced_hash == same_hash
            and len(sliced_hash) == 6 and torn == ["serve-range-malformed"] * len(TORN_LINES)):
        held("a ranged token serves its lines", "the writer's grammar verbatim, the selection "
             "hashed, a bound past the end serves what stands -- and no EOS hold on a code file")
    else:
        failures.append(f"  ✗ ranged serve              {cut}/{sliced_text!r}/{torn}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    serving(bench)
    passages(bench)
    rows(bench)
    mounts(bench)
    selections(bench)
    grammar(bench)
    return 0
