"""Scenario `overlay` -- the pattern `composition/overlay`, played from its demonstration:
- an overlay of a package's proc, in the instance's space, carries DELTAS: a law added, a law
  lifted, an offer added, an offer lifted; its body follows the base's; its `+` rows are served as
  the base enters; the base still resolves to the package's file and plays; without the overlay,
  the base alone
- a delta that adds what stands, removes what is absent, carries a `proc:` or removes a reading
  refuses by name -- the removed reading at the run's entry and at the build alike
- an `overlays/` directory at the instance's root is never read: the build warns `overlays-ignored`
- a mounted document carries its overlay's deltas, stacked and nested: the effective laws stand,
  asked at the PROVE -- a lifted one is a stranger there; a mount whose effective laws collide
  refuses `mount-collision`; a homonym outside the name's chain takes no delta -- under both
  conductions
The package that owns the base is written at the test's time: `desk` carries DRAFT and REVISE.
"""
from __future__ import annotations

import json

from conductor import compiling, instance, reading, render
from tests.harness import body_of, codes, demonstrated, demos, law, na_proof, plant, principal, vendor

DRAWER, PATTERN = "composition", "overlay"
DEMO = demos(DRAWER, PATTERN)
DEMOS = ("DRAFT.absent.md", "DRAFT.doubled.md", "DRAFT.flow.md", "DRAFT.md", "DRAFT.minus.md",
         "DRAFT.overlay.md", "EDITOR.md", "NODE.homonym.md", "NODE.md", "NODE.overlay.md",
         "OTHER.md", "OTHER.overlay.md", "REVISE.md", "SHIFT.md", "STYLE.md")
DESK = "name: desk\nversion: 0.0.1\ndescription: a witness package owning the base\nrequires: [kit]\n"


def _text(name: str) -> str:
    return (DEMO / name).read_text(encoding="utf-8")


def _place(env, name: str, where: str) -> None:
    """The demonstration `name` written at `where` in the house -- an overlay at its base's name."""
    env.write(where, _text(name))


def _tools(block) -> list[str]:
    return [one.name for one in block.tools] if block is not None else []


def deltas(bench) -> None:
    """The overlay of a package's proc: deltas, body, rows, resolution; the refusals; the root
    `overlays/`."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("overlay", bare=True)
    vendor(env.made, "desk", DESK, {"DRAFT": _text("DRAFT.md"), "REVISE": _text("REVISE.md")})
    plant(env, DRAWER, PATTERN, ("EDITOR.md", "STYLE.md"))
    base = env.made / ".sys" / "vendor" / "desk@0.0.1" / "procs" / "DRAFT.md"
    compiling.build_tools(env.made)
    plain = env.conductor().start(base)
    plain_shown = render(plain)
    env.conductor().forget()

    _place(env, "DRAFT.overlay.md", "procs/DRAFT.md")
    compiling.build_tools(env.made)
    overlaid = env.conductor().start(base)
    shown = render(overlaid)
    env.conductor().forget()
    added, lifted = body_of(DEMO / "DRAFT.overlay.md"), body_of(DEMO / "DRAFT.md")
    if (codes(overlaid) == ["OV1", "OV3"] and "EDITOR" in _tools(overlaid) and "REVISE" not in _tools(overlaid)
            and instance.resolve(env.made, "DRAFT.md") == base and overlaid.document == "DRAFT"
            and overlaid.instruction.keyword == "INFER"):
        held("an overlay carries deltas", "OV3 added, OV2 lifted, EDITOR offered, REVISE withdrawn; "
             "DRAFT still resolves to desk's file and plays its own step")
    else:
        failures.append(f"  ✗ the deltas                  {codes(overlaid)} {_tools(overlaid)} "
                        f"{instance.resolve(env.made, 'DRAFT.md')}")
    if (lifted in shown and added in shown and shown.index(lifted) < shown.index(added)
            and "INFORMATION — STYLE.md" in shown and body_of(DEMO / "STYLE.md") in shown
            and added not in plain_shown and "STYLE.md" not in plain_shown
            and codes(plain) == ["OV1", "OV2"] and "REVISE" in _tools(plain)):
        held("the body follows, the rows are served", "the overlay's body after DRAFT's, STYLE.md served "
             "as DRAFT enters; without the overlay, DRAFT alone: OV1 and OV2, REVISE, no reading")
    else:
        failures.append(f"  ✗ body and rows               plain={codes(plain)} {shown[:300]!r}")

    for name, code in (("DRAFT.doubled.md", "overlay-adds-existing"),
                       ("DRAFT.absent.md", "overlay-removes-nothing"),
                       ("DRAFT.flow.md", "overlay-carries-proc"),
                       ("DRAFT.minus.md", "overlay-serve-removal")):
        _place(env, name, "procs/DRAFT.md")
        expect(code, lambda: env.conductor().start(base))
        env.conductor().forget()
    expect("overlay-serve-removal", lambda: compiling.effective(env.made, reading.read(base)))
    (env.made / "procs" / "DRAFT.md").unlink()

    quiet = [one for one in compiling.lint(env.made) if one.startswith("overlays-ignored")]
    _place(env, "DRAFT.overlay.md", "overlays/DRAFT.md")
    warned = [one for one in compiling.lint(env.made) if one.startswith("overlays-ignored")]
    unread = codes(env.conductor().start(base))
    env.conductor().forget()
    if not quiet and len(warned) == 1 and "OV3" not in unread:
        held("a root overlays/ is never read", "overlays/DRAFT.md amends nothing (OV3 absent) and the "
             "build warns `overlays-ignored`; without the directory it says nothing")
    else:
        failures.append(f"  ✗ overlays-ignored            quiet={quiet} warned={warned} codes={unread}")


def _mounted(env, conduct, label: str, bench) -> None:
    """NODE mounted stacked on SHIFT: its effective laws, asked at the PROVE, a lifted law a stranger."""
    held, failures = bench.held, bench.failures
    opener = env.conductor()
    conduct(lambda: opener.start(env.made / "procs" / "SHIFT.md"))
    key = opener.run_id
    conduct(lambda: env.conductor(key).mount([{"doc": "procs/NODE.md"}]))
    view = conduct(lambda: env.conductor(key).peek())
    proving = conduct(lambda: env.conductor(key).submit(""))
    stranger = conduct(lambda: env.conductor(key).submit(json.dumps(
        [{"code": one, "evidence": "held", "verdict": "ok"} for one in ("OV5", "OV6", "OV7")])))
    block = stranger
    while block is not None and not block.wait:
        answer = na_proof(block) if block.judged else ""
        block = conduct(lambda: env.conductor(key).submit(answer))
    if (codes(view) == ["OV5", "OV7"] and {"EDITOR", "REVISE"} <= set(_tools(view))
            and proving is not None and set(proving.judged) == {"OV5", "OV7"}
            and "OV6" in (stranger.deviation or "") and block is not None and block.wait):
        held(f"a mounted document carries its deltas ({label})", "NODE stacked on SHIFT: OV5 and the "
             "overlay's OV7 in force, OV6 lifted, both offers; the PROVE asks OV5 and OV7, OV6 is refused "
             "as a stranger, the run parks")
    else:
        failures.append(f"  ✗ mounted deltas ({label})     view={codes(view)} {_tools(view)} "
                        f"asked={proving and proving.judged} {stranger and stranger.deviation!r}")
    env.conductor(key).forget()


def mounted(bench) -> None:
    """A mounted document and its overlay: stacked, nested, the collision, the homonym."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("overlay-mount", bare=True)
    vendor(env.made, "desk", DESK, {"DRAFT": _text("DRAFT.md"), "REVISE": _text("REVISE.md")})
    plant(env, DRAWER, PATTERN, ("EDITOR.md", "NODE.md", "OTHER.md", "SHIFT.md"))
    _place(env, "NODE.overlay.md", "NODE.md")
    _place(env, "OTHER.overlay.md", "OTHER.md")
    _place(env, "NODE.homonym.md", "elsewhere/NODE.md")
    compiling.build_tools(env.made)
    _mounted(env, lambda call: call(), "LLM", bench)
    _mounted(env, principal, "principal", bench)

    opener = env.conductor()
    opener.start(env.made / "procs" / "SHIFT.md")
    key = opener.run_id
    env.conductor(key).mount([{"doc": "procs/NODE.md"}])
    expect("mount-collision", lambda: env.conductor(key).mount([{"doc": "procs/OTHER.md"}]))
    env.conductor(key).forget()

    opener = env.conductor()
    opener.start(env.made / "procs" / "SHIFT.md")
    key = opener.run_id
    nested = env.conductor(key).mount([{"doc": "procs/NODE.md", "scope": "nested"}])
    segment = nested.split("▌ [2]")[0]
    kept, added = law(DRAWER, PATTERN, "NODE.md", "OV5"), law(DRAWER, PATTERN, "NODE.overlay.md", "OV7")
    lifted = law(DRAWER, PATTERN, "NODE.md", "OV6")
    if ("▸ NODE" in segment and kept in segment and added in segment and lifted not in nested
            and "EDITOR" in segment and "REVISE" in segment):
        held("a nested mount shows its deltas", "NODE's own segment writes OV5 and the overlay's OV7, "
             "both offers; OV6, lifted, is nowhere")
    else:
        failures.append(f"  ✗ the nested deltas           {segment[:300]!r}")
    env.conductor(key).forget()

    opener = env.conductor()
    opener.start(env.made / "procs" / "SHIFT.md")
    key = opener.run_id
    env.conductor(key).mount([{"doc": "elsewhere/NODE.md"}])
    other = env.conductor(key).peek()
    if codes(other) == ["OV8"] and "REVISE" not in _tools(other):
        held("a homonym takes no delta", "elsewhere/NODE.md, mounted by its path, is not the base of its "
             "name: its own OV8 alone, no overlay's law nor offer")
    else:
        failures.append(f"  ✗ the homonym                 {codes(other)} {_tools(other)}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    deltas(bench)
    mounted(bench)
    return 0
