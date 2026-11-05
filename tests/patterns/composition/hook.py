"""Scenario `hook` -- the pattern `composition/hook`, played from its demonstration:
- every document that attaches to a socket is CALLed at the host's HOOK, each in its own frame, by
  name, and the host resumes after the last
- a socket nobody attaches to plays nothing: the host goes on to its next step
- a proc that HOOKs the same socket twice refuses `socket-doubled` at the build
- an attach to a socket no proc hooks is a warning of the build, which passes
"""
from __future__ import annotations

from conductor import compiling
from tests.harness import demonstrated, plant

DEMOS = ("ALPHA.md", "BARE.md", "BRAVO.md", "DESK.md", "TWICE.md")
def _documents(env, first, cap: int = 6) -> list:
    """-> the blocks from `first` on, each step answered, until the host's own step or the cap."""
    seen, block = [first], first
    while block is not None and block.document != "DESK" and len(seen) < cap:
        block = env.conductor().submit("")
        seen.append(block)
    return seen


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    found = demonstrated("composition", "hook")
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0

    # --- the contributors are CALLed at the HOOK, by name --------------------------------------
    env = bench.env("hook", bare=True)
    plant(env, "composition", "hook", ("DESK.md", "ALPHA.md", "BRAVO.md"))
    compiling.build_tools(env.made)
    desk = env.made / "procs" / "DESK.md"
    blocks = _documents(env, env.conductor().start(desk))
    order = [one.document for one in blocks if one is not None]
    stacks = [one.stack for one in blocks if one is not None]
    if (order == ["ALPHA", "BRAVO", "DESK"]
            and all(one.startswith(f"DESK ▸ {name}{{") for one, name in zip(stacks, order[:2]))
            and blocks[-1].instruction.keyword == "INFER"):
        held("the contributors are called at the HOOK", "ALPHA then BRAVO, by name, each in its own "
             "frame under DESK, then DESK's own step")
    else:
        failures.append(f"  ✗ the call at the HOOK        {order!r} {stacks!r}")
    env.conductor().forget()

    # --- a socket nobody attaches to plays nothing ---------------------------------------------
    bare = bench.env("hook-bare", bare=True)
    plant(bare, "composition", "hook", ("BARE.md",))
    opened = bare.conductor().start(bare.made / "procs" / "BARE.md")
    if opened is not None and opened.document == "BARE" and opened.instruction.keyword == "INFER" \
            and opened.stack.startswith("BARE{"):
        held("an empty socket plays nothing", f"BARE opens on its own step, `{opened.stack}`")
    else:
        failures.append(f"  ✗ the empty socket            {opened and opened.stack!r}")

    # --- the same socket twice in one proc refuses ---------------------------------------------
    twice = bench.env("hook-twice", bare=True)
    plant(twice, "composition", "hook", ("TWICE.md",))
    expect("socket-doubled", lambda: compiling.build_tools(twice.made))

    # --- an attach no proc hooks: the build warns and passes ------------------------------------
    stray = bench.env("hook-stray", bare=True)
    plant(stray, "composition", "hook", ("ALPHA.md", "BRAVO.md"))
    for name in ("ALPHA.md", "BRAVO.md"):       # a socket no document of the pattern hooks
        paper = stray.made / "procs" / name
        paper.write_text(paper.read_text(encoding="utf-8").replace("attach: desk.open", "attach: nowhere.open"),
                         encoding="utf-8")
    built = stray.cli("-build")
    warned = [one for one in compiling.lint(stray.made) if one.startswith("attach-unhooked")]
    if built.returncode == 0 and len(warned) == 1 and "ALPHA" in warned[0] and "BRAVO" in warned[0]:
        held("an attach no proc hooks is a warning", "ALPHA and BRAVO attached to `nowhere.open`, "
             "which no proc hooks: `attach-unhooked` names it once, the build passes")
    else:
        failures.append(f"  ✗ the unhooked attach         rc={built.returncode} {warned!r}")
    return 0
