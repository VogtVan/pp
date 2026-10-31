"""Scenario `tiers` -- the daneel package on the three tiers of the system:
- a fresh install aggregates the kit's marble, then the Laws, then the nature; seats the
  member silently; boots on the Laws, the DNA served after them at MEMBER; its refs
  stand servable
- added to an instance with a member of its own, daneel seats its member and keeps the
  operator's as `.old`; the Laws join the system
"""
from __future__ import annotations

from conductor import Conductor, render, discovery, instance, reading
from conductor import install as install_module
from tests.harness import SOURCE, body_of, kept_document, reaches


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    daneel = SOURCE / "packages" / "daneel"
    kept_member = kept_document(daneel / "user", "MEMBER").read_text(encoding="utf-8")
    dan_made = bench.env("daneelws", ("daneel",)).made
    dan_system = (dan_made / ".sys" / "system.md").read_text(encoding="utf-8")
    dan_member = (dan_made / "MEMBER.md").read_text(encoding="utf-8")
    marble_head = body_of(kept_document(SOURCE / "engine", "SYSTEM.COMMON"))[:60]
    section = body_of(kept_document(daneel, "SYSTEM.COMMON"))
    laws_head = section[:60]
    nature_head = section[section.index("# Nature"):][:60]
    across = (dan_system.index(marble_head) < dan_system.index(laws_head) < dan_system.index(nature_head))
    dan_engine = dan_made / ".sys" / "engine" / "pp.py"
    dan_member_obj = discovery.instance_member(dan_engine)
    dan_c = Conductor(dan_member_obj, dan_engine)
    dan_boot = render(dan_c.start(dan_c.boot("BOOT.md")))
    speech = reading.served(instance.resolve(dan_made, "SPEECH.md"))[0]
    speech_head = body_of(kept_document(daneel, "SPEECH"))[:120]
    if (across and dan_member == kept_member
            and not (dan_made / "MEMBER.md.old").exists()
            and reaches(dan_boot, laws_head) and reaches(dan_boot, speech_head)
            and dan_boot.index(laws_head) < dan_boot.index(speech_head)   # the DNA serves at MEMBER, after the Laws
            and reaches(speech, speech_head)):
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
    if ((plain_made / "MEMBER.md").read_text(encoding="utf-8") == kept_member
            and (plain_made / "MEMBER.md.old").read_text(encoding="utf-8")
            == "the operator's own words\n"
            and laws_head in grown_system
            and "daneel" in instance.pins(plain_made)):
        held("a persona lands on lived ground", "add_package: the operator's member "
             "survives as .old, Daneel takes the seat, the Laws join the system")
    else:
        failures.append("  ✗ daneel add_package          .old or system missing")
    return 0
