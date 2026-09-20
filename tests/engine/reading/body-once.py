"""Scenario `body-once` -- 1 case(s), in the monolith's order:
- le-corps-une-fois: a CALLed body rides once under `once`, every time under `always`
"""
from __future__ import annotations

from conductor import Conductor, discovery
from tests.harness import document


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the first environment: three instances side by side, `core` the home
    town = bench.town(["core", "perso", "sw7-hub"])
    siblings = town.siblings
    home = town["core"].member
    script = town["core"].engine
    (home.meta / "TAGGED.md").write_text("some corpus\n", encoding="utf-8")


    def conductor() -> Conductor:
        """A fresh object every time -- what survives must survive on disk, not in memory."""
        return Conductor(home, siblings, script, "t")


    # --- le-corps-une-fois: a CALLed body rides once under `once`, every time under `always`
    body_home = bench.town(["bodies"]).siblings
    body_member = discovery.member(body_home, "bodies")
    (body_member.meta / "ONE.md").write_text(
        "---\nname: ONE\nkind: proc\ndescription: one step\nproc: |\n  INFER\n---\n"
        "the brief of ONE\n", encoding="utf-8")
    body_doc = document("---\nname: X\nproc: |\n  CALL ONE.md\n  CALL ONE.md\n---\n",
                        at=body_member.meta)
    for regime, expected in (("once", ""), ("always", "the brief of ONE")):
        (body_member.meta / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nproc_body_serve: {regime}\n---\n", encoding="utf-8")
        body_c = Conductor(body_member, body_home, script, "t")
        body_c.forget()
        first_call = body_c.start(body_doc)
        second_call = body_c.submit("")
        first_text = dict(first_call.payloads).get("ONE", "")
        second_text = dict(second_call.payloads).get("ONE", "") if second_call else ""
        if first_text.startswith("the brief of ONE") and (
                second_text == "" if regime == "once" else expected in second_text):
            held(f"a CALLed body under {regime}", "the first CALL serves the brief; the second "
                 + ("renders nothing -- proven once, like any reading" if regime == "once"
                    else "serves it again -- always means always"))
        else:
            failures.append(f"  ✗ body under {regime:<14} {first_text[:30]!r} / {second_text[:60]!r}")
        body_c.forget()
    return 0
