"""Scenario `initialize` -- the pattern `composition/initialize`, played from its demonstration:
- every proc carries the implicit socket `<proc>.initialize`, played once at its frame's entry,
  before its first step: an `attach:` there is CALLed once, a `mount:` there is mounted
- their laws stay on screen while the frame lives -- after the called document popped and at the
  next passage, once each, no body served again, one `initialize` in the trace -- under both
  conductions
- a callee's own `initialize` contributors live with it: its law binds the callee's step and leaves
  when it pops, the trace says `released`
- a proc that writes `HOOK <proc>.initialize` refuses `socket-reserved` at the build
"""
from __future__ import annotations

from conductor import compiling, render
from tests.harness import body_of, codes, demonstrated, demos, law, na_proof, plant, principal, traced

DEMOS = ("BADGE.md", "GUEST.md", "KEYS.md", "OFFICE.md", "RESERVED.md", "ROOM.md", "VISIT.md")
DRAWER, PATTERN = "composition", "initialize"
DEMO = demos(DRAWER, PATTERN)


def _held(bench, env, label: str, conduct) -> None:
    """Plays OFFICE's entry and two passages through `conduct` (the LLM's or the principal's)."""
    held, failures = bench.held, bench.failures
    opener = env.conductor()
    first = conduct(lambda: opener.start(env.made / "procs" / "OFFICE.md"))
    key = opener.run_id
    shown = render(first)
    badge, keys = law(DRAWER, PATTERN, "BADGE.md", "IN1"), law(DRAWER, PATTERN, "KEYS.md", "IN2")
    if ("OFFICE ▸ KEYS{" in shown and body_of(DEMO / "KEYS.md") in shown and body_of(DEMO / "BADGE.md") in shown
            and shown.count(badge) == 1 and shown.count(keys) == 1):
        held(f"an initialize contributor plays once at the entry ({label})", "OFFICE opens on KEYS's "
             "own step; BADGE's body and law and KEYS's body and law ride the first output, once each")
    else:
        failures.append(f"  ✗ the entry ({label})          {shown[:400]!r}")
    parked = []
    for _ in range(2):
        block = conduct(lambda: env.conductor(key).submit(""))
        while block is not None and not block.wait:
            answer = na_proof(block) if block.judged else ""
            block = conduct(lambda: env.conductor(key).submit(answer))
        parked.append(conduct(lambda: env.conductor(key).peek()))
    laws = [codes(one) for one in parked]
    texts = [render(one) for one in parked]
    played = [one for one in traced(env, key) if one.get("kind") == "initialize"
              and one.get("document") == "OFFICE"]
    if (all(one is not None and one.document == "OFFICE" for one in parked)
            and all(one.count("IN1") == 1 and one.count("IN2") == 1 for one in laws)
            and not any(body_of(DEMO / "KEYS.md") in text or body_of(DEMO / "BADGE.md") in text for text in texts)
            and len(played) == 1):
        held(f"its laws stay while the frame lives ({label})", "IN1 and IN2 bind OFFICE after KEYS "
             "popped and at the next passage, once each; one `initialize` in the trace, no body again")
    else:
        failures.append(f"  ✗ held ({label})               laws={laws} played={len(played)}")
    env.conductor(key).forget()


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0

    # --- once at the entry, held for the frame's life, under both conductions ----------------
    for label, conduct in (("LLM", lambda call: call()), ("principal", principal)):
        env = bench.env(f"initialize-{label.lower()}", pin=False)
        plant(env, DRAWER, PATTERN, ("BADGE.md", "KEYS.md", "OFFICE.md"))
        env.cli("-build")
        _held(bench, env, label, conduct)

    # --- a callee's initialize lives with it ---------------------------------------------------
    visit = bench.env("initialize-pop", pin=False)
    plant(visit, DRAWER, PATTERN, ("GUEST.md", "ROOM.md", "VISIT.md"))
    visit.cli("-build")
    opener = visit.conductor()
    opened = opener.start(visit.made / "procs" / "VISIT.md")
    shown = render(opened)
    guest = law(DRAWER, PATTERN, "GUEST.md", "IN3")
    released = [one for one in traced(visit, opener.run_id) if one.get("kind") == "released"
                and "GUEST.md" in one.get("docs", [])]
    if ("VISIT ▸ ROOM{" in shown and shown.count(guest) == 1 and body_of(DEMO / "GUEST.md") in shown
            and opened.document == "VISIT" and "IN3" not in codes(opened) and len(released) == 1):
        held("a callee's initialize leaves with it", "IN3 binds ROOM's step and leaves with ROOM: "
             "VISIT's step that follows carries it no more, the trace says `released`")
    else:
        failures.append(f"  ✗ the pop                     {opened.document}:{codes(opened)} "
                        f"released={len(released)} {shown[:300]!r}")
    opener.forget()

    # --- the implicit socket is never written ---------------------------------------------------
    reserved = bench.env("initialize-reserved", bare=True)
    plant(reserved, DRAWER, PATTERN, ("RESERVED.md",))
    expect("socket-reserved", lambda: compiling.build_tools(reserved.made))
    return 0
