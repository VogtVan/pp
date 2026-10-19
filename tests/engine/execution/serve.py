"""Scenario `serve` -- what SERVE puts in a block, and the ledger that says it:
- SERVE: rides the block, served with nothing to ask, one ROW one SERVE, a bare SERVE reads one
  SECTION and the next follows, `serve-exhausted`, a section serves WHOLE, a document is proven
  once, a served document says its title, a bare name reaches the repo's root, a document is
  served once
- the ledger: a line per payload in the block's order, each line says where it came from, the
  package is attributed, a spared reading keeps its line, a gone document is `missing`, the
  measure never moved, a payload says its provider and a refusal and a re-read say theirs, a
  door's element and a sink say theirs, a re-serve says what comes back
- a payload served once: one output the token once, two outputs the content decides, a refusal
  said once, the re-serve resolves a token once, a mounted body enters once, always forces the
  mounted body, a spared nested body keeps its segment
"""
from __future__ import annotations

import re

from conductor import render
from tests.harness import document, support

run = support(__file__, "run")

# --- the witness packages: `alpha` (two providers of one token, one that refuses), `witness`
# (one provider that speaks, one that refuses)
NEWS = ("#!/usr/bin/env python3\nfrom pathlib import Path\n"
        "print('{who}: ' + Path('news.txt').read_text(encoding='utf-8').strip())\n")
REFUSES = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('it refuses\\n')\nsys.exit(2)\n"
SPEAKS = "#!/usr/bin/env python3\nprint('the witness skill says hello')\n"
ALPHA = {"NEWS-A": ("alpha-news", "pp-alpha", NEWS.format(who="a")),
         "NEWS-B": ("alpha-news", "pp-alpha-beta", NEWS.format(who="b")),
         "BROKEN": ("alpha-broken", "pp-alpha-broken", REFUSES)}
WITNESS = {"GIVER": ("witness", "pp-witness", SPEAKS),
           "BREAKER": ("witness-broken", "pp-witness-broken", REFUSES)}

ASK = """---
name: {name}
kind: proc
description: a consumer of the witness tokens
payloads: {tokens}
proc: |
  INFER
---

{name} reads the news
"""
MOUNTED = """---
name: MOUNTED
kind: doc
description: a mounted witness
payloads: alpha-news
constraints.behavior: |
  KMO1  the mounted law holds
---

{body}
"""
NESTED = ("---\nname: NESTED\nkind: doc\ndescription: a nested witness\n"
          "tools: |\n  pp-alpha\n---\n\nThe nested body.\n")
INNER = """---
name: INNER
kind: proc
description: a called document
serve: |
  code: NOTE.md GONE.md
proc: |
  SERVE
  INFER
---

The inner body.
"""
ASKER = """---
name: ASKER
kind: proc
description: a document that asks for both payloads
payloads: witness witness-broken
proc: |
  INFER
---

ASKER asks
"""
SINKER = """---
name: SINKER
kind: proc
description: a document whose production goes to a sink
sink: pp-witness
proc: |
  INFER
---

SINKER hands its production over
"""
LOOPER = """---
name: LOOPER
kind: proc
description: an iterated door on the witness token
cycle: witness
proc: |
  INFER
---

LOOPER turns once per element
"""


def _blocks(env, key: str) -> list[dict]:
    """-> every block event of the run's own trace, in order."""
    return [one for one in run.trace(env, key) if one.get("kind") == "block"]


def _lines(env, key: str, subject: str | None = None) -> list[dict]:
    """-> every ledger line of the run's blocks, of `subject` when named."""
    return [line for one in _blocks(env, key) for line in (one.get("served") or [])
            if subject is None or line.get("subject") == subject]


def _providers(env, key: str, token: str) -> int:
    """-> how many provider runs the run's trace counts for `token`."""
    return sum(1 for one in run.trace(env, key) if one.get("kind") == "provider" and one.get("token") == token)


def _tune(env, fusion: str, body_serve: str) -> None:
    """The settings a case plays under: the fusion of instructions and how a body rides."""
    settings = env.made / "SETTINGS.md"
    text = settings.read_text(encoding="utf-8")
    text = re.sub(r"^instructions_fusion: \S+", f"instructions_fusion: {fusion}", text, flags=re.M)
    text = re.sub(r"^proc_body_serve: \S+", f"proc_body_serve: {body_serve}", text, flags=re.M)
    settings.write_text(text, encoding="utf-8")


def _asking(env, tokens: str = "alpha-news", fusion: str = "none", body_serve: str = "once") -> None:
    """A case's own setup on the shared lab: the first news, two consumers of `tokens` the member
    CALLs one after the other, the settings tuned."""
    (env.root / "news.txt").write_text("the first news\n", encoding="utf-8")
    env.write("ASK1.md", ASK.format(name="ASK1", tokens=tokens))
    env.write("ASK2.md", ASK.format(name="ASK2", tokens=tokens))
    env.write_member(body="The member asks twice.", proc="CALL ASK1.md\n  CALL ASK2.md\n  INFER", name="AGENT")
    _tune(env, fusion, body_serve)


def _booted(env, key: str):
    """-> the first block of a fresh run under `key`, booted."""
    runner = run.conductor_of(env, key)
    return runner.start(runner.boot("BOOT.md"))


def serving(bench) -> None:
    """SERVE on a bare instance: what rides, when, and once."""
    held, expect, over, failures = bench.held, bench.expect, bench.over, bench.failures
    env = bench.env("core", bare=True)
    meta = env.made
    (meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")

    def conductor():
        return run.conductor_of(env, "t")

    # --- SERVE does not yield: the TOOL reads, and the document rides the next block --
    reader = conductor()
    reader.forget()
    riding = reader.start(document("---\nname: X\nproc: |\n  HOOK warp\n"
                                   "  SERVE TAGGED.md\n  INFER\n---\n"))
    if [name for name, _ in riding.payloads] == ["TAGGED.md"] and riding.instruction.keyword == "INFER":
        held("SERVE rides the block", "the tool read it; the agent is asked nothing about it")
    else:
        failures.append(f"  ✗ SERVE payload             {[n for n, _ in riding.payloads]}")

    reader.forget()
    closing = reader.start(document("---\nname: X\nproc: |\n  SERVE TAGGED.md\n---\n"))
    if (over(closing) and [n for n, _ in closing.payloads] == ["TAGGED.md"]
            and "some corpus" in closing.payloads[0][1]):
        held("served with nothing to ask", "the payload rides the COMPLETION block — never a bare drain")
    else:
        failures.append("  ✗ a payload was swallowed at completion")

    # --- a `serve:` ROW may hold several documents -- one bare SERVE, both ride together ----
    (meta / "UNO.md").write_text("uno\n", encoding="utf-8")
    (meta / "DOS.md").write_text("dos\n", encoding="utf-8")
    together = conductor()
    together.forget()
    bundled_end = together.start(document("---\nname: X\nserve: |\n  UNO.md DOS.md\nproc: |\n  SERVE\n---\n"))
    if over(bundled_end) and bundled_end.payloads == (("UNO.md", "uno"), ("DOS.md", "dos")):
        held("one ROW, one SERVE", "UNO and DOS ride the SAME call, untagged -- the row decides the batch")
    else:
        failures.append(f"  ✗ bundled row               {bundled_end and bundled_end.payloads}")
    together.forget()

    # --- a bare SERVE dequeues one `serve:` ROW -- pacing across a PICK, one row at a time ----
    (meta / "FIRST.md").write_text("first\n", encoding="utf-8")
    (meta / "SECOND.md").write_text("second\n", encoding="utf-8")
    pacer = conductor()
    pacer.forget()
    first_block = pacer.start(document("---\nname: X\nserve: |\n  FIRST.md\n\n  SECOND.md\nproc: |\n"
                                       "  SERVE\n  INFER\n  SERVE\n---\n"))
    if ([n for n, _ in first_block.payloads] == ["FIRST.md"]
            and first_block.instruction.keyword == "INFER"):
        held("a bare SERVE reads one SECTION", "FIRST's paragraph rides this block; SECOND's waits its turn")
    else:
        failures.append(f"  ✗ paced serve — first block {first_block.payloads} "
                        f"/ {first_block.instruction}")
    paced_end = pacer.submit("")
    if over(paced_end) and paced_end.payloads == (("SECOND.md", "second"),):
        held("the next bare SERVE follows", "SECOND's section rides only once the PICK is answered")
    else:
        failures.append(f"  ✗ paced serve — second entry {paced_end and paced_end.payloads}")
    pacer.forget()

    expect("serve-exhausted", lambda: conductor().start(
        document("---\nname: X\nserve: |\n  TAGGED.md\nproc: |\n  SERVE\n  SERVE\n---\n")))

    # --- a SECTION serves whole -- three lines, one bare SERVE ----------------------------
    (meta / "TRES.md").write_text("tres\n", encoding="utf-8")
    sectioned = conductor()
    sectioned.forget()
    section_block = sectioned.start(document("---\nname: X\nserve: |\n  UNO.md\n  DOS.md\n  TRES.md\n"
                                             "proc: |\n  SERVE\n  INFER\n---\n"))
    if ([n for n, _ in section_block.payloads] == ["UNO.md", "DOS.md", "TRES.md"]
            and section_block.instruction.keyword == "INFER"):
        held("a section serves WHOLE", "three lines, one SERVE -- the paragraph is the unit, "
             "the line never beats the rhythm")
    else:
        failures.append(f"  ✗ whole section             {section_block.payloads}")
    sectioned.forget()

    # --- the proof is per DOCUMENT: a reading never rides twice, whatever brought it ----
    once_c = conductor()
    once_c.forget()
    once_c.start(document("---\nname: X\nserve: |\n  UNO.md DOS.md\n\n  UNO.md TRES.md\nproc: |\n"
                          "  SERVE\n  INFER\n  SERVE\n  INFER\n  SERVE DOS.md\n---\n"))
    second = once_c.submit("")            # the chat INFER takes nothing back: the bare advance
    third = once_c.submit("")
    if ([n for n, _ in second.payloads] == ["TRES.md"] and dict(second.payloads).get("TRES.md") == "tres"
            and over(third) and not dict(third.payloads)):
        held("a document is proven once", "UNO in two sections rides once, the second section "
             "renders nothing for it; an explicit SERVE DOS.md after DOS's section renders nothing")
    else:
        failures.append(f"  ✗ proven once               {second.payloads} / {third and third.payloads}")
    once_c.forget()

    # --- a served document says its title: `▌ TITLE` ---------------------------------------
    titled = conductor()
    (meta / "LONG.md").write_text("a served line\n", encoding="utf-8")
    first_chunk = titled.start(document("---\nname: X\nproc: |\n  SERVE LONG.md\n---\n"))
    if "▌ INFORMATION — LONG" in render(first_chunk):
        held("a served document says its title", "one titled section per reading -- the cut "
             "of an overflowing output is the block's business, never the reading's")
    else:
        failures.append(f"  ✗ served title               {first_chunk.payloads[:1]!r}")
    titled.forget()

    # --- a bare name falls back to the ROOT OF THE REPO -- the instance and the packages
    # keep the upper hand, a name nothing answers to is gone
    (env.root / "README.md").write_text("the repo's own readme\n", encoding="utf-8")
    (env.root / "design").mkdir(exist_ok=True)
    (env.root / "design" / "target.md").write_text("the target\n", encoding="utf-8")
    (meta / "OWN.md").write_text("the member's\n", encoding="utf-8")
    (env.root / "OWN.md").write_text("the repo's twin -- never served\n", encoding="utf-8")
    away = run.conductor_of(env, None)
    away.forget()
    at_root = dict(away.start(document(
        "---\nname: X\nproc: |\n  SERVE README.md\n  SERVE design/target.md\n  SERVE OWN.md\n"
        "  SERVE NOWHERE.md\n---\n", at=meta)).payloads)
    if (at_root.get("README.md", "").startswith("the repo's own readme")
            and at_root.get("design/target.md", "").startswith("the target")
            and at_root.get("OWN.md", "").startswith("the member's")
            and "gone" in at_root.get("NOWHERE.md", "")):
        held("a bare name reaches the repo's root", "README.md and design/target.md resolve at "
             "the repo and title by their token; the instance's OWN wins over the repo's twin; "
             "NOWHERE is gone, said")
    else:
        failures.append(f"  ✗ repo root resolution      {sorted(at_root)} / {at_root}")
    away.forget()

    # --- the same CONTENT is not served twice: a run proves a reading once -----------
    (meta / "TWICE.md").write_text("same bytes\n", encoding="utf-8")
    (meta / "COPY.md").write_text("same bytes\n", encoding="utf-8")
    once = conductor()
    once.forget()
    once_end = once.start(document("---\nname: X\nproc: |\n  SERVE TWICE.md\n  SERVE COPY.md\n---\n"))
    if ([name for name, _ in once_end.payloads] == ["TWICE.md"]
            and dict(once_end.payloads)["TWICE.md"].startswith("same bytes")):
        held("a document is served once", "the second SERVE renders nothing -- same content, "
             "same proof, the text never rides twice")
    else:
        failures.append(f"  ✗ the same document was served twice  {once_end.payloads}")
    once.forget()


def ledger(bench) -> None:
    """The ledger of a member's first block: one line per payload, its origin, its package,
    what is spared, what is gone, the measure -- and the re-serve of a compaction."""
    held, failures = bench.held, bench.failures
    env = bench.env("ledger", ("greeter",))       # the greeter MOUNTS a document at boot.ready
    env.write("INNER.md", INNER)
    env.write("NOTE.md", "---\nname: NOTE\nkind: doc\ndescription: a note\n---\n\nThe note's body.\n")
    env.write_member("serve: |\n  reference: NOTE.md\nconstraints.behavior: |\n  M1  your name is AGENT\n",
                     body="The witness member.", proc="SERVE\n  CALL INNER.md\n  INFER", name="AGENT")
    text = render(_booted(env, "t"))
    blocks = _blocks(env, "t")
    first = blocks[0]
    lines = first.get("served") or []
    payloads = first.get("payloads") or {}

    # --- one line per payload, in the same order, and the block's text stands ---------
    served = [line for line in lines if line.get("state") != "spared"]
    titles = [line["subject"] for line in served]
    sections = re.findall(r"^▌ INFORMATION — (.+)$", text, flags=re.M)
    if titles and sections and titles[:len(sections)] == sections and set(payloads) <= set(titles):
        held("a line per payload, in the block's order",
             f"{len(served)} line(s) for {len(sections)} INFORMATION section(s), the same "
             "subjects in the same order -- the ledger reads as the block reads")
    else:
        failures.append(f"  ✗ the order                   {titles!r} vs {sections!r}")

    # --- the origins, and who asked ----------------------------------------------------
    origins = {}
    for line in lines:             # a subject served twice keeps BOTH lines: the first wins here
        origins.setdefault(line["subject"], (line.get("origin"), line.get("by"), line.get("nature")))
    if (origins.get("standing orders", ("",))[0] == "marble"
            and origins.get("AGENT", ("",))[0] == "body"
            and origins.get("NOTE.md") == ("serve", "MEMBER", "reference")
            and any(v[0] == "mount" for v in origins.values())):
        held("each line says where it came from",
             "the marble at the boot, the member's body, `NOTE.md` served by a row of MEMBER "
             "with its declared nature (`reference`), and the greeter's GREETING mounted at the "
             "socket -- a subject asked twice keeps both its lines")
    else:
        failures.append(f"  ✗ the origins                 {origins!r}")

    # --- the package of the asking document --------------------------------------------
    packages = {line["subject"]: line.get("package") for line in lines}
    if (packages.get("standing orders") == "engine" and packages.get("AGENT") == "instance"
            and packages.get("NOTE.md") == "instance"
            and any(value == "greeter" for value in packages.values())):
        held("the package is attributed", "`engine` for the marble, `instance` for the "
             "operator's own documents, `greeter` for what its package serves")
    else:
        failures.append(f"  ✗ the packages                {packages!r}")

    # --- a reading already proven is SPARED --------------------------------------------
    spared = [line for line in _lines(env, "t") if line.get("state") == "spared"]
    if spared and all(line.get("spared") for line in spared):
        held("a spared reading keeps its line", f"{len(spared)} line(s) `spared`, each with "
             "the mass it avoided -- what was invisible before is counted now")
    else:
        failures.append(f"  ✗ spared                      {spared[:2]!r}")

    # --- a gone document is missing -----------------------------------------------------
    missing = [line for line in _lines(env, "t") if line.get("state") == "missing"]
    if missing and missing[0].get("origin") == "serve" and missing[0].get("by"):
        held("a gone document is `missing`", f"`{missing[0]['subject']}` -- the row that "
             f"asked it is named ({missing[0]['by']}), and the block says so in its place")
    else:
        failures.append(f"  ✗ missing                     {missing[:1]!r}")

    # --- `payloads` did not move ---------------------------------------------------------
    shaped = all(isinstance(pair, list) and len(pair) == 2 and all(isinstance(n, int) for n in pair)
                 for pair in payloads.values())
    weighed = first.get("weight", {}).get("payload")
    total = sum(pair[0] for pair in payloads.values())
    if shaped and weighed == total:
        held("the measure never moved", f"`payloads` is still {{subject: [chars, tokens]}} and "
             f"its sum ({total} c) is the block's payload part -- the readers of the measure "
             "read what they always read")
    else:
        failures.append(f"  ✗ payloads                    {shaped} {weighed} vs {total}")

    # --- a compaction's re-serve says `reserved` ------------------------------------------
    run.conductor_of(env, "t").compacted()
    reserved = [line for line in (_blocks(env, "t")[-1].get("served") or [])
                if line.get("state") == "reserved"]
    if reserved and any(line.get("origin") == "marble" for line in reserved):
        held("a re-serve says what comes back", f"{len(reserved)} line(s) `reserved` after "
             "`-compacted`, the marble among them -- the matter a summary took away, served "
             "back and said so")
    else:
        failures.append(f"  ✗ reserved                    {[line.get('state') for line in (_blocks(env, 't')[-1].get('served') or [])]!r}")


def payloads(bench) -> None:
    """The payloads of the witness packages on one lab: each case sets its own member, its own
    consumers and its own settings, and reads its own run's ledger."""
    held, failures = bench.held, bench.failures
    env = bench.env("payloads")
    run.pin_package(env.made, "alpha", ALPHA)
    run.pin_package(env.made, "witness", WITNESS)

    # --- one output, two consumers -------------------------------------------------------
    _asking(env, fusion="max")
    text = render(_booted(env, "fused"))
    lines = _lines(env, "fused", "alpha-news")
    served = [one for one in lines if one["state"] == "served"]
    spared = [one for one in lines if one["state"] == "spared"]
    sections = text.count("▌ INFORMATION — alpha-news")
    ran = _providers(env, "fused", "alpha-news")
    if (ran == 2 and len(served) == 2 and sections == 2
            and len(spared) == 2 and all(one.get("by") == "ASK2" and one.get("spared") for one in spared)):
        held("one output, the token once", "two consumers fused in one output: 2 provider lines, "
             "2 sections, ASK2 spared twice with the mass avoided")
    else:
        failures.append(f"  ✗ one output                 providers={ran} "
                        f"sections={sections} states={[one['state'] for one in lines]!r}")

    # --- two outputs of one exchange -----------------------------------------------------
    def split(key: str, move: bool) -> tuple[list[str], int]:
        """ASK1 renders in the first output, ASK2 in the next one; `move` rewrites the news
        between them. -> the ledger states of alpha-news, in order, and the provider runs."""
        _asking(env)
        _booted(env, key)
        if move:
            (env.root / "news.txt").write_text("the news moved\n", encoding="utf-8")
        for _ in range(4):
            if len(_lines(env, key, "alpha-news")) >= 4:
                break
            run.conductor_of(env, key).forward("")
        return [one["state"] for one in _lines(env, key, "alpha-news")], _providers(env, key, "alpha-news")

    kept, ran_kept = split("split", move=False)
    moved, ran_moved = split("moved", move=True)
    if (kept[:4] == ["served", "served", "spared", "spared"] and ran_kept == 4
            and moved[:4] == ["served", "served", "served", "served"] and ran_moved == 4):
        held("two outputs, the content decides", "the providers run again in the second output: "
             "their identical rendering is spared, a rewritten news enters whole")
    else:
        failures.append(f"  ✗ two outputs                kept={kept!r}/{ran_kept} moved={moved!r}/{ran_moved}")

    # --- a refusing provider -------------------------------------------------------------
    _asking(env, tokens="alpha-broken", fusion="max")
    _booted(env, "broken")
    broken = [one["state"] for one in _lines(env, "broken", "alpha-broken")]
    if _providers(env, "broken", "alpha-broken") == 1 and broken == ["refused", "spared"]:
        held("a refusal said once", "one provider line, `refused` for ASK1, `spared` for ASK2")
    else:
        failures.append(f"  ✗ refusal                    providers={_providers(env, 'broken', 'alpha-broken')} "
                        f"{broken!r}")

    # --- the re-serve: a frame and a mount on one token ----------------------------------
    _asking(env)
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body."))
    _booted(env, "reserve")
    run.conductor_of(env, "reserve").mount([{"doc": "MOUNTED.md", "body": True}])
    before = _providers(env, "reserve", "alpha-news")
    run.conductor_of(env, "reserve").compacted()
    reserved = [one for one in _lines(env, "reserve", "alpha-news") if one["state"] == "reserved"]
    added = _providers(env, "reserve", "alpha-news") - before
    if added == 2 and len(reserved) >= 2:
        held("the re-serve resolves a token once", "the frame's CALL and the mounted document both "
             "consume alpha-news: 2 provider lines for 2 providers, the lines `reserved`")
    else:
        failures.append(f"  ✗ re-serve                   +{added} reserved={len(reserved)}")

    # --- a mounted body enters once ------------------------------------------------------
    _asking(env)
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body."))
    _booted(env, "body")
    entry = {"doc": "MOUNTED.md", "body": True, "constraints": False}
    shown = [run.conductor_of(env, "body").mount([entry]), run.conductor_of(env, "body").mount([entry])]
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body, rewritten."))
    shown.append(run.conductor_of(env, "body").mount([entry]))
    states = [one["state"] for one in _lines(env, "body", "MOUNTED")]
    if (states == ["served", "spared", "served"] and "The mounted body." in shown[0]
            and "The mounted body." not in shown[1] and "rewritten" in shown[2]):
        held("a mounted body enters once", "served, spared at the second mount, served again once "
             "the document moved")
    else:
        failures.append(f"  ✗ mounted body               {states!r}")

    _asking(env, body_serve="always")
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body."))
    _booted(env, "always")
    run.conductor_of(env, "always").mount([entry])
    run.conductor_of(env, "always").mount([entry])
    states = [one["state"] for one in _lines(env, "always", "MOUNTED")]
    if states == ["served", "forced"]:
        held("always forces the mounted body", "`proc_body_serve: always` -- served, then forced")
    else:
        failures.append(f"  ✗ always                     {states!r}")

    # --- a spared nested body keeps its segment ------------------------------------------
    _asking(env)
    env.write("NESTED.md", NESTED)
    _booted(env, "nested")
    nested = {"doc": "NESTED.md", "scope": "nested", "body": True}
    first_text = run.conductor_of(env, "nested").mount([nested])
    second_text = run.conductor_of(env, "nested").mount([nested])
    states = [one["state"] for one in _lines(env, "nested", "NESTED")]
    if (states == ["served", "spared"] and "The nested body." in first_text
            and "▸ NESTED" in second_text and "pp-alpha" in second_text
            and "The nested body." not in second_text):
        held("a spared nested body keeps its segment", "the second mount renders the heading and "
             "the tools, never the body again -- the ledger says `spared`")
    else:
        failures.append(f"  ✗ nested                     {states!r} second={second_text[:240]!r}")

    # --- a payload's provider, a refusal, a body re-read on purpose -----------------------
    env.write("ASKER.md", ASKER)
    env.write_member(body="The member calls ASKER twice.", proc="CALL ASKER.md\n  CALL ASKER.md\n  INFER",
                     name="AGENT")
    _tune(env, "none", "always")
    runner = run.conductor_of(env, "p")
    block = runner.start(runner.boot("BOOT.md"))
    for _ in range(6):
        if block is None or block.wait:
            break
        block = runner.forward("")
    lines = _lines(env, "p")
    given = next((line for line in lines if line.get("subject") == "witness"), {})
    broken = next((line for line in lines if line.get("subject") == "witness-broken"), {})
    forced = [line for line in lines if line.get("state") == "forced"]
    if (given.get("origin") == "payload" and given.get("with") == "pp-witness"
            and given.get("package") == "witness" and given.get("by") == "ASKER"
            and broken.get("state") == "refused" and broken.get("with") == "pp-witness-broken"
            and forced and forced[0].get("subject") == "ASKER"):
        held("a payload says its provider, a refusal and a re-read say theirs",
             "`witness` served by the skill pp-witness of the package witness, asked by ASKER; "
             "`witness-broken` refused by pp-witness-broken; ASKER's body CALLed again under "
             "`proc_body_serve: always` is `forced`")
    else:
        failures.append(f"  ✗ payloads and states        given={given!r} broken={broken.get('state')!r} "
                        f"forced={[line.get('subject') for line in forced]!r}")

    # --- an iterated door's element, and what a sink said back ---------------------------
    env.write("SINKER.md", SINKER)
    env.write("LOOPER.md", LOOPER)
    env.write_member(body="The member hands a production to a sink, then opens a door.",
                     proc="CALL SINKER.md\n  CALL LOOPER.md\n  INFER", name="AGENT")
    _tune(env, "none", "always")
    walker = run.conductor_of(env, "d")
    step = walker.start(walker.boot("BOOT.md"))
    for _ in range(5):
        if step is None or step.wait:
            break
        step = walker.forward("a production for the step")
    door_lines = _lines(env, "d")
    lap = next((line for line in door_lines if line.get("origin") == "cycle"), {})
    sank = next((line for line in door_lines if line.get("origin") == "sink"), {})
    if (lap.get("by") == "LOOPER" and lap.get("state") == "served"
            and sank.get("with") == "pp-witness" and sank.get("chars")):
        held("a door's element and a sink say theirs", f"LOOPER's element `{lap.get('subject')}` "
             "is `cycle`, asked by the door itself; what pp-witness said back from SINKER's "
             f"production is `sink` ({sank.get('chars')} c)")
    else:
        failures.append(f"  ✗ cycle and sink              lap={lap!r} sink={sank!r} "
                        f"origins={sorted({line.get('origin') for line in door_lines})!r}")


def scenario(bench) -> int:
    serving(bench)
    ledger(bench)
    payloads(bench)
    return 0
