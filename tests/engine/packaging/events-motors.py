"""Scenario `signal-motors` -- 1 case(s), in the monolith's order:
- A2/L2 les-moteurs-kit: the engine pushes from its own moments
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, Refusal, discovery, instance, persistence
from tests.harness import session_of
from conductor import events as events_module


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- A2/L2 les-moteurs-kit: the engine pushes from its own moments --------------
    # the motors push the PACKAGES' declared checks and vectors: member-bare and offers-idle
    # are authoring's checks, the frustration vector and IMPROVE.md are improvement's
    mot_made = bench.env("motw", packages=("authoring", "improvement")).made
    mot_ws = mot_made.parent
    mot_engine = mot_made / ".sys" / "engine" / "pp.py"
    mot_member = discovery.instance_member(mot_engine)
    (mot_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\nhistory_day: never\ninstructions_fusion: max\n---\n",
        encoding="utf-8")

    def mot_c() -> Conductor:
        return Conductor(mot_member, discovery.siblings_around(mot_member), mot_engine, "t")

    stamped_seed = str(instance.read(mot_made).get("member_seed", ""))
    mot_c().start(mot_c().boot("IMPROVE.md"))
    bare_first = [one.get("signal") for one in persistence.signals_of(session_of(mot_member.meta))]
    for _ in range(2):
        mot_c().submit("improvement-proc:IMPROVE")
        mot_c().forget()
        mot_c().start(mot_c().boot("IMPROVE.md"))
    crossed_third = mot_c().submit("improvement-proc:IMPROVE")
    # the crossing is a STANDING entry now (the vector's family is improvement's, the
    # recommendation holds across runs until acquitted), no longer a per-run latch
    crossed = [one for one in events_module.standing_entries(mot_made)
               if one.get("signal") == "frustration" and one.get("vector") == "improvement-proc:IMPROVE"]
    if (len(stamped_seed) == 64 and "member-bare" in bare_first
            and crossed and "3 projections" in crossed[0].get("text", "")):
        held("the capture motor counts", "install fingerprints the member; a fresh boot "
             "latches member-bare; the third projection on one vector crosses at the bound "
             "and STANDS as the package's recommendation")
    else:
        failures.append(f"  ✗ motor capture               {bare_first} {crossed} "
                        f"{events_module.counters(mot_made)}")

    # the repair motor needs a JUDGED step: IMPROVE.md's own INFER is free and takes any
    # answer (its sink reads it), so a bench document with `output: json` carries the case
    (mot_made / "JUDGED.md").write_text(
        "---\nname: JUDGED\nkind: proc\ndescription: a judged step for the repair motor\n"
        "output: json\nproc: |\n  INFER\n  PICK member\n---\n\nname the members, then pick\n",
        encoding="utf-8")
    repair_run = mot_c()
    repair_run.forget()
    repair_run.start(mot_made / "JUDGED.md")
    repair_run.submit('["a", "b"]')           # the INFER feeds the PICK
    repair_run.submit("zzz")                  # not a member: repair 1
    repair_run.submit("zzz")                  # again: repair 2 -- `repaired` latches
    repaired_latch = [one.get("signal") for one in
                      persistence.signals_of(session_of(mot_member.meta))]
    if "repaired" in repaired_latch:
        held("the repair motor pushes", "two repairs on one document in one run -- the "
             "second latches `repaired`, evidence in the trace")
    else:
        failures.append(f"  ✗ motor repair                {repaired_latch}")

    ref_run = mot_c()
    ref_run.submit("")                       # binds the run: the trace is the scope
    ref_run.noted(Refusal("ghost-code", "a bench refusal"))
    ref_run.noted(Refusal("ghost-code", "a bench refusal"))
    refused_latch = [one.get("signal") for one in
                     persistence.signals_of(session_of(mot_member.meta))]
    if "refused" in refused_latch:
        held("the refusal motor pushes", "the same code refused twice in one run -- the "
             "second latches `refused`")
    else:
        failures.append(f"  ✗ motor refusal               {refused_latch}")

    (mot_ws / ".claude" / "skills" / "housework").mkdir(parents=True)
    (mot_ws / ".claude" / "skills" / "housework" / "SKILL.md").write_text(
        "---\nname: housework\ndescription: a home skill\n---\nsweep\n",
        encoding="utf-8")
    mot_c().forget()
    mot_c().start(mot_c().boot("IMPROVE.md"))
    idle_latched = [one.get("signal") for one in
                    persistence.signals_of(session_of(mot_member.meta))]
    (mot_made / "procs" / "HOME.md").write_text(
        "---\nname: HOME\nkind: doc\ntools: |\n  +housework\n---\n",
        encoding="utf-8")
    (mot_made / "MEMBER.md").write_text(
        (mot_made / "MEMBER.md").read_text(encoding="utf-8") + "\n<!-- shaped -->\n",
        encoding="utf-8")
    mot_c().forget()
    mot_c().start(mot_c().boot("IMPROVE.md"))
    settled = [one.get("signal") for one in
               persistence.signals_of(session_of(mot_member.meta))]
    if ("offers-idle" in idle_latched and "member-bare" in idle_latched
            and "offers-idle" not in settled and "member-bare" not in settled):
        held("the bare predicates settle", "a stocked home with no offer latches "
             "offers-idle; the `+` adoption and an edited member quiet both")
    else:
        failures.append(f"  ✗ motor bare                  {idle_latched} / {settled}")
    return 0
