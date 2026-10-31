"""Scenario `payload` -- the pattern `context/payload`, played from its demonstration:
- a document that names a token (`payloads:`) receives, as a section of its block, the output of the
  skill every provider of that token names (`provides:` + `with:`); a refusing skill is said in the
  section and the step goes on
- a token enters an output once: a second consumer in the same output runs no provider and is
  spared; across two outputs the providers run again and the content decides
- a refusal is said once; the re-serve of a compaction resolves a token once
- a mounted body enters once, `proc_body_serve: always` forces it, a spared nested body keeps its
  segment
- a contributor's body rides WITH the section its token renders, before it, and not at all when
  nothing rendered
The packages that provide the tokens and their skills are written at the test's time.
"""
from __future__ import annotations

import re

from conductor import compiling, render
from tests.harness import body_of, demonstrated, demos, plant, traced, vendor

DRAWER, PATTERN = "context", "payload"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("ASK1.md", "ASK2.md", "BOARD.md", "MOUNTED.md", "NESTED.md", "NOTICE.md", "POSTER.md")
PACKAGE = "name: {name}\nversion: 0.0.1\ndescription: a package of providers\nrequires: [kit]\n"
PROVIDER = ("---\nname: {name}\nkind: doc\ndescription: a provider\nprovides: {token}\n"
            "with: {skill}\n---\n\n{name} provides\n")
NEWS = ("#!/usr/bin/env python3\nfrom pathlib import Path\n"
        "print('{who}: ' + Path('news.txt').read_text(encoding='utf-8').strip())\n")
FILED = ("#!/usr/bin/env python3\nfrom pathlib import Path\n"
         "print(Path('inbox.txt').read_text(encoding='utf-8').strip() if Path('inbox.txt').exists() else '')\n")
REFUSES = "#!/usr/bin/env python3\nimport sys\nsys.stderr.write('it refuses\\n')\nsys.exit(2)\n"
SPEAKS = "#!/usr/bin/env python3\nprint('the witness skill says hello')\n"
PROVIDERS = {
    "alpha": {"NEWS-A": ("alpha-news", "pp-alpha", NEWS.format(who="a")),
              "NEWS-B": ("alpha-news", "pp-alpha-beta", NEWS.format(who="b")),
              "BROKEN": ("alpha-broken", "pp-alpha-broken", REFUSES)},
    "witness": {"GIVER": ("witness", "pp-witness", SPEAKS),
                "BREAKER": ("witness-broken", "pp-witness-broken", REFUSES),
                "INBOX": ("witness-inbox", "pp-witness-inbox", FILED)},
}


def _providers_of(env) -> None:
    """The two packages of providers, written at the test's time."""
    for package, providers in PROVIDERS.items():
        vendor(env.made, package, PACKAGE.format(name=package),
               {name: PROVIDER.format(name=name, token=token, skill=skill)
                for name, (token, skill, _) in providers.items()},
               {skill: code for _, skill, code in providers.values()})


def _lines(env, key: str, subject: str) -> list[dict]:
    return [line for one in traced(env, key) if one.get("kind") == "block"
            for line in (one.get("served") or []) if line.get("subject") == subject]


def _ran(env, key: str, token: str) -> int:
    return sum(1 for one in traced(env, key) if one.get("kind") == "provider" and one.get("token") == token)


def _tune(env, fusion: str, body_serve: str) -> None:
    settings = env.made / "SETTINGS.md"
    text = settings.read_text(encoding="utf-8")
    text = re.sub(r"^instructions_fusion: \S+", f"instructions_fusion: {fusion}", text, flags=re.M)
    text = re.sub(r"^proc_body_serve: \S+", f"proc_body_serve: {body_serve}", text, flags=re.M)
    settings.write_text(text, encoding="utf-8")


def _asking(env, token: str = "alpha-news", fusion: str = "none", body_serve: str = "once") -> None:
    """ASK1 and ASK2 planted on `token`, a member that CALLs one after the other, the settings tuned."""
    (env.root / "news.txt").write_text("the first news\n", encoding="utf-8")
    for name in ("ASK1.md", "ASK2.md"):
        env.write(f"procs/{name}", (DEMO / name).read_text(encoding="utf-8").replace("alpha-news", token))
    env.write_member(body="The member asks twice.", proc="CALL ASK1.md\n  CALL ASK2.md\n  INFER", name="AGENT")
    _tune(env, fusion, body_serve)


def _booted(env, key: str):
    runner = env.conductor(key)
    return runner.start(runner.boot("BOOT.md"))


def consumers(bench) -> None:
    """A token in one output, in two, refused, re-served."""
    held, failures = bench.held, bench.failures
    env = bench.env("payload")
    _providers_of(env)

    _asking(env, fusion="max")
    text = render(_booted(env, "fused"))
    lines = _lines(env, "fused", "alpha-news")
    served = [one for one in lines if one["state"] == "served"]
    spared = [one for one in lines if one["state"] == "spared"]
    if (_ran(env, "fused", "alpha-news") == 2 and len(served) == 2
            and text.count("▌ INFORMATION — alpha-news") == 2
            and len(spared) == 2 and all(one.get("by") == "ASK2" and one.get("spared") for one in spared)):
        held("one output, the token once", "ASK1 and ASK2 fused in one output: two providers run once, two "
             "sections, ASK2 spared twice with the mass avoided")
    else:
        failures.append(f"  ✗ one output                  {[one['state'] for one in lines]}")

    def split(key: str, move: bool) -> tuple[list[str], int]:
        _asking(env)
        _booted(env, key)
        if move:
            (env.root / "news.txt").write_text("the news moved\n", encoding="utf-8")
        for _ in range(4):
            if len(_lines(env, key, "alpha-news")) >= 4:
                break
            env.conductor(key).forward("")
        return [one["state"] for one in _lines(env, key, "alpha-news")], _ran(env, key, "alpha-news")

    kept, ran_kept = split("split", move=False)
    moved, ran_moved = split("moved", move=True)
    if (kept[:4] == ["served", "served", "spared", "spared"] and ran_kept == 4
            and moved[:4] == ["served", "served", "served", "served"] and ran_moved == 4):
        held("two outputs, the content decides", "the providers run again in the second output: the same "
             "rendering is spared, a rewritten news enters whole")
    else:
        failures.append(f"  ✗ two outputs                 kept={kept}/{ran_kept} moved={moved}/{ran_moved}")

    _asking(env, token="alpha-broken", fusion="max")
    _booted(env, "broken")
    states = [one["state"] for one in _lines(env, "broken", "alpha-broken")]
    if _ran(env, "broken", "alpha-broken") == 1 and states == ["refused", "spared"]:
        held("a refusal said once", "one provider run, `refused` for ASK1, `spared` for ASK2")
    else:
        failures.append(f"  ✗ the refusal                 {states}")

    _asking(env)
    plant(env, DRAWER, PATTERN, ("MOUNTED.md", "NESTED.md"))
    _booted(env, "reserve")
    env.conductor("reserve").mount([{"doc": "MOUNTED.md", "body": True}])
    before = _ran(env, "reserve", "alpha-news")
    env.conductor("reserve").compacted()
    reserved = [one for one in _lines(env, "reserve", "alpha-news") if one["state"] == "reserved"]
    if _ran(env, "reserve", "alpha-news") - before == 2 and len(reserved) >= 2:
        held("the re-serve resolves a token once", "a CALLed consumer and a mounted one on one token: two "
             "provider runs for two providers, the lines `reserved`")
    else:
        failures.append(f"  ✗ the re-serve                {len(reserved)}")


def mounted(bench) -> None:
    """A mounted body once, forced, nested and spared."""
    held, failures = bench.held, bench.failures
    env = bench.env("payload-mounted")
    _providers_of(env)
    plant(env, DRAWER, PATTERN, ("MOUNTED.md", "NESTED.md"))
    body = body_of(DEMO / "MOUNTED.md")

    _asking(env)
    _booted(env, "body")
    entry = {"doc": "MOUNTED.md", "body": True, "constraints": False}
    shown = [env.conductor("body").mount([entry]), env.conductor("body").mount([entry])]
    moved = env.made / "procs" / "MOUNTED.md"
    moved.write_text(moved.read_text(encoding="utf-8").replace(body, body + " Rewritten."), encoding="utf-8")
    shown.append(env.conductor("body").mount([entry]))
    states = [one["state"] for one in _lines(env, "body", "MOUNTED")]
    if (states == ["served", "spared", "served"] and body in shown[0] and body not in shown[1]
            and "Rewritten." in shown[2]):
        held("a mounted body enters once", "served, spared at the second mount, served again once it moved")
    else:
        failures.append(f"  ✗ the mounted body            {states}")
    plant(env, DRAWER, PATTERN, ("MOUNTED.md",))

    _asking(env, body_serve="always")
    _booted(env, "always")
    env.conductor("always").mount([entry])
    env.conductor("always").mount([entry])
    states = [one["state"] for one in _lines(env, "always", "MOUNTED")]
    if states == ["served", "forced"]:
        held("always forces the mounted body", "`proc_body_serve: always`: served, then forced")
    else:
        failures.append(f"  ✗ always                      {states}")

    _asking(env)
    _booted(env, "nested")
    nested = {"doc": "NESTED.md", "scope": "nested", "body": True}
    first = env.conductor("nested").mount([nested])
    second = env.conductor("nested").mount([nested])
    states = [one["state"] for one in _lines(env, "nested", "NESTED")]
    inner = body_of(DEMO / "NESTED.md")
    if (states == ["served", "spared"] and inner in first and "▸ NESTED" in second
            and "pp-alpha" in second and inner not in second):
        held("a spared nested body keeps its segment", "the second mount renders the heading and the offer, "
             "never the body again")
    else:
        failures.append(f"  ✗ the nested body             {states} {second[:200]!r}")


def contributors(bench) -> None:
    """A contributor's payloads at a socket: the output, the refusal, the body with its section."""
    held, failures = bench.held, bench.failures
    env = bench.env("payload-board", bare=True)
    _providers_of(env)
    plant(env, DRAWER, PATTERN, ("BOARD.md", "POSTER.md"))
    compiling.build_tools(env.made)
    board = env.conductor().start(env.made / "procs" / "BOARD.md")
    shown = render(board)
    if ("INFORMATION — witness\n" in shown and "the witness skill says hello" in shown
            and body_of(DEMO / "POSTER.md") in shown):
        held("a payload is a skill's output", "POSTER, mounted at BOARD, serves its body and pp-witness's "
             "output as the section `witness`")
    else:
        failures.append(f"  ✗ the section                 {shown[:300]!r}")
    if ("INFORMATION — witness-broken" in shown and "pp-witness-broken refused (2)" in shown
            and board.document == "BOARD" and board.instruction.keyword == "INFER"):
        held("a refusing skill is said", "the section `witness-broken` carries the refusal; BOARD's step "
             "plays on")
    else:
        failures.append(f"  ✗ the refusal                 {board.stack!r}")
    env.conductor().forget()

    quiet = bench.env("payload-notice", bare=True)
    _providers_of(quiet)
    plant(quiet, DRAWER, PATTERN, ("BOARD.md", "NOTICE.md"))
    compiling.build_tools(quiet.made)
    brief = body_of(DEMO / "NOTICE.md")
    silent = render(quiet.conductor().start(quiet.made / "procs" / "BOARD.md"))
    quiet.conductor().forget()
    (quiet.root / "inbox.txt").write_text("T1 waits for you\n", encoding="utf-8")
    spoken = render(quiet.conductor().start(quiet.made / "procs" / "BOARD.md"))
    quiet.conductor().forget()
    at_body, at_section = spoken.find(brief), spoken.find("INFORMATION — witness-inbox")
    if (brief not in silent and "INFORMATION — witness-inbox" not in silent
            and 0 <= at_body < at_section and "T1 waits for you" in spoken):
        held("the body rides with its section", "the provider prints nothing: neither NOTICE's body nor the "
             "section; it prints a line: the body first, then the section it explains")
    else:
        failures.append(f"  ✗ the body and its section    body={at_body} section={at_section}")


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    consumers(bench)
    mounted(bench)
    contributors(bench)
    return 0
