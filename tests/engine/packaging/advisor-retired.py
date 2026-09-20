"""Scenario `advisor-retired` -- 1 case(s), in the monolith's order:
- A1/L3 les-retraits: the advisor era is over
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, revive, discovery, persistence
from tests.harness import session_of, cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- A1/L3 les-retraits: the advisor era is over ----------------------------------
    era_made = bench.env("eraw").made
    era_engine = era_made / ".sys" / "engine" / "pp.py"
    era_member = discovery.instance_member(era_engine)
    (era_made / "SETTINGS.md").write_text(   # a stale advisor key must be IGNORED now
        "---\nname: SETTINGS\nkind: doc\nadvisor_days: soon\nera_day: monday\n---\n", encoding="utf-8")

    def era_c() -> Conductor:
        return Conductor(era_member, discovery.siblings_around(era_member), era_engine, "t")

    from conductor import settings as tuning
    era_c()   # constructing did not refuse
    stale_ignored = tuning.referenced(era_member.meta, "@SETTINGS.era_day") == "monday"
    era_booted = era_c().start(era_c().boot("BOOT.md"))
    era_floor = persistence.restore(session_of(era_member.meta), revive)[1].frames[0].procedure.instructions
    gone_mentor = cli(era_engine, "-s", "pp-pp")
    era_catalog = (era_made / ".sys" / "tools.md").read_text(encoding="utf-8")
    if (era_booted is not None and stale_ignored
            and not any(one.argument == "ADVISOR.md" for one in era_floor)
            and gone_mentor.returncode != 0
            and "pp-pp" not in era_catalog and "ADVISOR" not in era_catalog
            and not list((era_made / ".sys").rglob("*advisor*"))):
        held("the advisor era is over", "a stale `advisor_days` is ignored; nothing "
             "injects ADVISOR; `pp-pp` is not even a name -- catalog, kit and seeds clean")
    else:
        failures.append(f"  ✗ advisor era                 rc={gone_mentor.returncode} "
                        f"{[one.argument for one in era_floor]}")
    return 0
