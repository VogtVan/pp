"""Scenario `identity-in-behavior` -- 2 case(s) (plan pp-split, batch la-migration-des-sections, the reprise):
- an instance born from the template puts M1 and M2 on the boot block under behavior -- no production group
- the bare kit turn of that instance owes no checkpoint: no proof block from WORK to FINAL, the closing says why
"""
from __future__ import annotations

from conductor import render


def _drive(env, opening, cap: int = 8) -> list:
    """Advance to the frontier on bare submits: the kit turn's productions are ephemeral."""
    seen = [opening]
    while seen[-1] is not None and "▶ FINAL" not in render(seen[-1]) and len(seen) < cap:
        seen.append(env.conductor("t").submit(""))
    return [one for one in seen if one is not None]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("identity")

    # --- the identity is behavior on a vanilla instance -------------------------------
    opener = env.conductor("t")
    opening = opener.resume(opener.boot("BOOT.md"))
    for _ in range(6):            # a long boot reading rides CONTINUEs first
        if opening.command:
            break
        opening = env.conductor("t").resume(env.conductor("t").boot("BOOT.md"))
    sections = {one.code: one.section for one in opening.constraints}
    if (sections.get("M1") == "behavior" and sections.get("M2") == "behavior"
            and "production" not in sections.values()):
        held("the identity is behavior on a vanilla instance",
             "M1 and M2 under behavior on the boot block, no production law in force")
    else:
        failures.append(f"  ✗ identity sections          {sections}")

    # --- the bare kit turn owes no checkpoint ------------------------------------------
    seen = _drive(env, env.conductor("t").submit(""))      # CAPABILITIES answered -> TURN
    texts = [render(one) for one in seen]
    if (seen and all(one.output != "proof" for one in seen)
            and "▶ FINAL" in texts[-1] and "no law of production in force" in texts[-1]):
        held("the kit turn owes no checkpoint",
             "no proof block from WORK to FINAL, the closing says no law of production is in force")
    else:
        failures.append(f"  ✗ kit checkpoint             {[(one.document, one.output) for one in seen]!r} "
                        f"{texts[-1][-200:]!r}")
    env.conductor("t").forget()
    return 0
