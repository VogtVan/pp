"""Scenario `tiers` -- 1 case(s), in the monolith's order:
- l-adn: the daneel package proves the tiers end to end
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, discovery, instance, reading
from conductor import install as install_module
from tests.harness import SOURCE, body_of, kept_document, reaches


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- l-adn: the daneel package proves the tiers end to end ------------------------
    dan_made = bench.env("daneelws", ("daneel",)).made
    dan_system = (dan_made / ".sys" / "system.md").read_text(encoding="utf-8")
    dan_member = (dan_made / "MEMBER.md").read_text(encoding="utf-8")
    marble_head = body_of(kept_document(SOURCE / "kit", "MARBLE"))[:60]
    laws_head = body_of(kept_document(SOURCE / "packages" / "daneel", "LAWS"))[:60]
    nature_head = body_of(kept_document(SOURCE / "packages" / "daneel" / "system", "NATURE"))[:60]
    across = (dan_system.index(marble_head) < dan_system.index(laws_head) < dan_system.index(nature_head))
    dan_engine = dan_made / ".sys" / "engine" / "pp.py"
    dan_member_obj = discovery.instance_member(dan_engine)
    dan_c = Conductor(dan_member_obj, discovery.siblings_around(dan_member_obj), dan_engine)
    dan_boot = render(dan_c.start(dan_c.boot("BOOT.md")))
    speech = reading.served(instance.resolve(dan_made, "SPEECH.md"))[0]
    if (across and "Daneel" in dan_member and "Partner" in dan_member
            and dan_member == kept_document(SOURCE / "packages" / "daneel" / "user", "MEMBER").read_text(encoding="utf-8")
            and not (dan_made / "MEMBER.md.old").exists()
            and reaches(dan_boot, laws_head)
            and "Partner Elijah" not in dan_boot        # the DNA serves at MEMBER, not before
            and "Partner" in speech and "homage" in speech):
        held("daneel is born on the three tiers",
             "system aggregates kit then Laws then nature; the fresh install seats the "
             "member silently; the boot opens on the Laws; the DNA refs stand servable")
    else:
        failures.append(f"  ✗ daneel package              {across} {dan_boot[:80]!r}")

    plain_made = bench.env("plainws").made
    (plain_made / "MEMBER.md").write_text("the operator's own words\n", encoding="utf-8")
    plain_member = discovery.instance_member(plain_made / ".sys" / "engine" / "pp.py")
    install_module.add_package(plain_member, "daneel")
    grown_system = (plain_made / ".sys" / "system.md").read_text(encoding="utf-8")
    if ("Daneel" in (plain_made / "MEMBER.md").read_text(encoding="utf-8")
            and (plain_made / "MEMBER.md.old").read_text(encoding="utf-8")
            == "the operator's own words\n"
            and laws_head in grown_system
            and "daneel" in instance.pins(plain_made)):
        held("a persona lands on lived ground", "add_package: the operator's member "
             "survives as .old, Daneel takes the seat, the Laws join the system")
    else:
        failures.append("  ✗ daneel add_package          .old or system missing")
    return 0
