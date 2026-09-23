"""Scenario `served-once` -- 7 case(s) (plan core, batch le-payload-servi-une-fois):
- one output, two consumers of a token: the providers run once, the second consumer is spared
- two outputs of one exchange: the providers run again, an identical rendering is spared, a changed one enters
- a refusing provider is said once in the output, the second consumer spared
- a compaction's re-serve resolves a token once for a frame and a mount that both consume it
- a mounted body enters once: served, then spared, then served again once rewritten
- under `proc_body_serve: always` a mounted body comes back `forced`
- a spared NESTED body leaves its segment its heading and its tools, without the body
"""
from __future__ import annotations

import json

from conductor import Conductor, discovery, instance, render

PACKAGE = """name: alpha
version: 0.0.1
description: a witness package -- two providers of one token, one that refuses
requires: [kit]
"""
PROVIDER = """---
name: {name}
kind: doc
description: a witness provider
provides: {token}
with: {skill}
---

{name} provides
"""
NEWS = ("#!/usr/bin/env python3\nfrom pathlib import Path\n"
        "print('{who}: ' + Path('news.txt').read_text(encoding='utf-8').strip())\n")
REFUSES = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('no news\\n')\nsys.exit(2)\n"
ASKER = """---
name: {name}
kind: proc
description: a consumer of the witness tokens
payloads: {tokens}
proc: |
  INFER
---

{name} reads the news
"""
MEMBER = """---
name: AGENT
kind: proc
description: the witness member
proc: |
  CALL ASK1.md
  CALL ASK2.md
  INFER
---

The member asks twice.
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


def _pin(made) -> None:
    root = made / ".sys" / "vendor" / "alpha@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(PACKAGE, encoding="utf-8")
    for name, token, skill, code in (("NEWS-A", "alpha-news", "pp-alpha", NEWS.format(who="a")),
                                     ("NEWS-B", "alpha-news", "pp-alpha-beta", NEWS.format(who="b")),
                                     ("BROKEN", "alpha-broken", "pp-alpha-broken", REFUSES)):
        (root / "procs" / f"{name}.md").write_text(
            PROVIDER.format(name=name, token=token, skill=skill), encoding="utf-8")
        home = root / "skills" / skill
        home.mkdir(parents=True, exist_ok=True)
        (home / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: a witness\n---\n\n{skill}\n",
                                       encoding="utf-8")
        (home / f"{skill}.py").write_text(code, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["alpha"] = "0.0.1"
    instance.write(made, pins)


def _lab(bench, name: str, tokens: str = "alpha-news", fusion: str = "none",
         body_serve: str = "once"):
    env = bench.env(name)
    _pin(env.made)
    (env.root / "news.txt").write_text("the first news\n", encoding="utf-8")
    env.write("ASK1.md", ASKER.format(name="ASK1", tokens=tokens))
    env.write("ASK2.md", ASKER.format(name="ASK2", tokens=tokens))
    env.write("MEMBER.md", MEMBER)
    settings = env.made / "SETTINGS.md"
    text = settings.read_text(encoding="utf-8")
    text = text.replace("instructions_fusion: none", f"instructions_fusion: {fusion}")
    for one in ("always", "once"):
        text = text.replace(f"proc_body_serve: {one}", f"proc_body_serve: {body_serve}")
    settings.write_text(text, encoding="utf-8")
    member = discovery.instance_member(env.engine)
    return env, (lambda: Conductor(member, discovery.siblings_around(member), env.engine, "s"))


def _events(made) -> list[dict]:
    log = sorted((made / ".sys" / "state").glob("session-*.jsonl"))[-1]
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def _providers(made, token: str) -> int:
    return sum(1 for one in _events(made) if one.get("kind") == "provider" and one.get("token") == token)


def _lines(made, subject: str) -> list[dict]:
    return [line for one in _events(made) if one.get("kind") == "block"
            for line in (one.get("served") or []) if line.get("subject") == subject]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- one output, two consumers -------------------------------------------------------
    env, make = _lab(bench, "once-fused", fusion="max")
    runner = make()
    text = render(runner.start(runner.boot("BOOT.md")))
    lines = _lines(env.made, "alpha-news")
    served = [one for one in lines if one["state"] == "served"]
    spared = [one for one in lines if one["state"] == "spared"]
    sections = text.count("▌ INFORMATION — alpha-news")
    if (_providers(env.made, "alpha-news") == 2 and len(served) == 2 and sections == 2
            and len(spared) == 2 and all(one.get("by") == "ASK2" and one.get("spared") for one in spared)):
        held("one output, the token once", "two consumers fused in one output: 2 provider lines, "
             "2 sections, ASK2 spared twice with the mass avoided")
    else:
        failures.append(f"  ✗ one output                 providers={_providers(env.made, 'alpha-news')} "
                        f"sections={sections} states={[one['state'] for one in lines]!r}")

    # --- two outputs of one exchange -----------------------------------------------------
    def split(name: str, move: bool) -> list[str]:
        """ASK1 renders in the first output, ASK2 in the next one; `move` rewrites the news
        between them. -> the ledger states of alpha-news, in order."""
        env, make = _lab(bench, name)
        make().start(make().boot("BOOT.md"))
        if move:
            (env.root / "news.txt").write_text("the news moved\n", encoding="utf-8")
        for _ in range(4):
            if len(_lines(env.made, "alpha-news")) >= 4:
                break
            make().forward("")
        return [one["state"] for one in _lines(env.made, "alpha-news")], _providers(env.made, "alpha-news")

    kept, ran_kept = split("once-split", move=False)
    moved, ran_moved = split("once-moved", move=True)
    if (kept[:4] == ["served", "served", "spared", "spared"] and ran_kept == 4
            and moved[:4] == ["served", "served", "served", "served"] and ran_moved == 4):
        held("two outputs, the content decides", "the providers run again in the second output: "
             "their identical rendering is spared, a rewritten news enters whole")
    else:
        failures.append(f"  ✗ two outputs                kept={kept!r}/{ran_kept} moved={moved!r}/{ran_moved}")

    # --- a refusing provider -------------------------------------------------------------
    env, make = _lab(bench, "once-broken", tokens="alpha-broken", fusion="max")
    runner = make()
    runner.start(runner.boot("BOOT.md"))
    broken = [one["state"] for one in _lines(env.made, "alpha-broken")]
    if _providers(env.made, "alpha-broken") == 1 and broken == ["refused", "spared"]:
        held("a refusal said once", "one provider line, `refused` for ASK1, `spared` for ASK2")
    else:
        failures.append(f"  ✗ refusal                    providers={_providers(env.made, 'alpha-broken')} "
                        f"{broken!r}")

    # --- the re-serve: a frame and a mount on one token ----------------------------------
    env, make = _lab(bench, "once-reserve")
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body."))
    runner = make()
    runner.start(runner.boot("BOOT.md"))
    make().mount([{"doc": "MOUNTED.md", "body": True}])
    before = _providers(env.made, "alpha-news")
    make().compacted()
    reserved = [one for one in _lines(env.made, "alpha-news") if one["state"] == "reserved"]
    if _providers(env.made, "alpha-news") - before == 2 and len(reserved) >= 2:
        held("the re-serve resolves a token once", "the frame's CALL and the mounted document both "
             "consume alpha-news: 2 provider lines for 2 providers, the lines `reserved`")
    else:
        failures.append(f"  ✗ re-serve                   +{_providers(env.made, 'alpha-news') - before} "
                        f"reserved={len(reserved)}")

    # --- a mounted body enters once ------------------------------------------------------
    env, make = _lab(bench, "once-body")
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body."))
    make().start(make().boot("BOOT.md"))
    entry = {"doc": "MOUNTED.md", "body": True, "constraints": False}
    shown = [make().mount([entry]), make().mount([entry])]
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body, rewritten."))
    shown.append(make().mount([entry]))
    states = [one["state"] for one in _lines(env.made, "MOUNTED")]
    if (states == ["served", "spared", "served"] and "The mounted body." in shown[0]
            and "The mounted body." not in shown[1] and "rewritten" in shown[2]):
        held("a mounted body enters once", "served, spared at the second mount, served again once "
             "the document moved")
    else:
        failures.append(f"  ✗ mounted body               {states!r}")

    env, make = _lab(bench, "always-body", body_serve="always")
    env.write("MOUNTED.md", MOUNTED.format(body="The mounted body."))
    make().start(make().boot("BOOT.md"))
    make().mount([entry])
    make().mount([entry])
    states = [one["state"] for one in _lines(env.made, "MOUNTED")]
    if states == ["served", "forced"]:
        held("always forces the mounted body", "`proc_body_serve: always` -- served, then forced")
    else:
        failures.append(f"  ✗ always                     {states!r}")

    # --- a spared nested body keeps its segment ------------------------------------------
    env, make = _lab(bench, "once-nested")
    env.write("NESTED.md", "---\nname: NESTED\nkind: doc\ndescription: a nested witness\n"
                           "tools: |\n  pp-alpha\n---\n\nThe nested body.\n")
    make().start(make().boot("BOOT.md"))
    nested = {"doc": "NESTED.md", "scope": "nested", "body": True}
    first_text = make().mount([nested])
    second_text = make().mount([nested])
    states = [one["state"] for one in _lines(env.made, "NESTED")]
    if (states == ["served", "spared"] and "The nested body." in first_text
            and "▸ NESTED" in second_text and "pp-alpha" in second_text
            and "The nested body." not in second_text):
        held("a spared nested body keeps its segment", "the second mount renders the heading and "
             "the tools, never the body again -- the ledger says `spared`")
    else:
        failures.append(f"  ✗ nested                     {states!r} second={second_text[:240]!r}")
    return 0
