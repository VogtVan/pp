"""Scenario `events-motors` -- 5 case(s): the engine pushes from its own moments, on what a
package DECLARES -- here the bench's witness `motor` (a `user/` member, the two boot checks,
a counting signal with its family), in the place of a product package:
- the capture motor: the install fingerprints the member the package places; a fresh boot
  latches `member-bare`; the third push on one vector crosses at the declared bound, a
  counter silent past its days dies at the write; a push on what nobody declares refuses
- the repair motor: two repairs on one document in one run latch `repaired`
- the refusal motor: the same code refused twice in one run latches `refused`
- the bare predicates settle: a stocked harness home with no offer latches `offers-idle`;
  a `+` adoption and an edited member quiet both
- a package motor without code: a probe package, written at run time, declares a signal
  `at: gesture:<skill>`; the gesture plays and the engine pushes
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from conductor import Conductor, Refusal, discovery, instance, persistence
from tests.harness import cli, session_of
from conductor import events as events_module

BROOM = """name: probe
version: 0.0.1
description: a package whose motor is a declaration and a skill, no line of engine code
requires: []
contributes:
  events:
    signals:
      swept: {door: PP-RULES, at: gesture:pp-probe-broom}
"""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the capture motor: a fingerprint worn, a bound crossed ---------------------------
    mot_made = bench.env("motw", packages=("motor",)).made
    mot_ws = mot_made.parent
    mot_engine = mot_made / ".sys" / "engine" / "pp.py"
    mot_member = discovery.instance_member(mot_engine)
    (mot_made / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n", encoding="utf-8")

    def mot_c() -> Conductor:
        return Conductor(mot_member, mot_engine, "t")

    stamped_seed = str(instance.read(mot_made).get("member_seed", ""))
    mot_c().start(mot_c().boot("BOOT.md"))
    bare_first = [one.get("signal") for one in persistence.signals_of(session_of(mot_member.meta))]
    aged = (datetime.now(timezone.utc) - timedelta(days=events_module.STALE_DAYS + 1)).isoformat(timespec="seconds")
    events_module._write(mot_made, {**events_module.counters(mot_made),
                                    "motor-proc:AGED": {"count": 5, "last_at": aged}})
    pushes = [events_module.push(mot_made, "motor", "frustration", vector="motor-proc:MOTOR")
              for _ in range(3)]
    if (len(stamped_seed) == 64 and (mot_made / "MEMBER.md").is_file() and "member-bare" in bare_first
            and pushes[:2] == [None, None] and pushes[2] is not None and pushes[2].get("n") == 3
            and pushes[2].get("vector") == "motor-proc:MOTOR"
            and "motor-proc:AGED" not in events_module.counters(mot_made)):
        held("the capture motor counts", "install fingerprints the member the witness places; a "
             "fresh boot latches member-bare; the third push on one vector crosses at the "
             "declared bound (3) and the entry says its count; a counter silent past "
             f"{events_module.STALE_DAYS} days dies at the write")
    else:
        failures.append(f"  ✗ motor capture               seed={len(stamped_seed)} {bare_first} {pushes} "
                        f"{events_module.counters(mot_made)}")
    bench.expect("provider-unknown", lambda: events_module.push(mot_made, "ghost", "frustration"))
    bench.expect("signal-unknown", lambda: events_module.push(mot_made, "motor", "moods"))
    bench.expect("family-unknown", lambda: events_module.push(
        mot_made, "motor", "frustration", vector="planet:mars"))

    # the repair motor needs a JUDGED step: a bench document with `output: json` carries the case
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
    mot_c().start(mot_c().boot("BOOT.md"))
    idle_latched = [one.get("signal") for one in
                    persistence.signals_of(session_of(mot_member.meta))]
    (mot_made / "procs" / "HOME.md").write_text(
        "---\nname: HOME\nkind: doc\ntools: |\n  +housework\n---\n",
        encoding="utf-8")
    (mot_made / "MEMBER.md").write_text(
        (mot_made / "MEMBER.md").read_text(encoding="utf-8") + "\n<!-- shaped -->\n",
        encoding="utf-8")
    mot_c().forget()
    mot_c().start(mot_c().boot("BOOT.md"))
    settled = [one.get("signal") for one in
               persistence.signals_of(session_of(mot_member.meta))]
    if ("offers-idle" in idle_latched and "member-bare" in idle_latched
            and "offers-idle" not in settled and "member-bare" not in settled):
        held("the bare predicates settle", "a stocked home with no offer latches "
             "offers-idle; the `+` adoption and an edited member quiet both")
    else:
        failures.append(f"  ✗ motor bare                  {idle_latched} / {settled}")

    # --- a package motor without code: the declaration and a skill ----------------------
    probe = mot_made / ".sys" / "vendor" / "probe@0.0.1"
    broom = probe / "skills" / "pp-probe-broom"
    broom.mkdir(parents=True)
    (probe / "package.yaml").write_text(BROOM, encoding="utf-8")
    (broom / "SKILL.md").write_text(
        "---\nname: pp-probe-broom\ndescription: the fixture's broom -- one sweep, one line.\n---\n"
        "sweep and say so\n", encoding="utf-8")
    (broom / "pp-probe-broom.py").write_text(
        "def main(argv):\n    print(f\"pp-probe-broom: swept {' '.join(argv) or 'clean'}\")\n"
        "    return 0\n", encoding="utf-8")
    pins = instance.read(mot_made)
    pins["packages"]["probe"] = "0.0.1"
    instance.write(mot_made, pins)
    (mot_made / "SWEEP.md").write_text(       # a bench document that offers the gesture
        "---\nname: SWEEP\nkind: proc\ndescription: a step that offers the broom\n"
        "tools: |\n  pp-probe-broom\nproc: |\n  INFER\n---\n\nsweep the yard\n", encoding="utf-8")
    mot_c().forget()
    mot_c().start(mot_made / "SWEEP.md")
    swept = cli(mot_engine, "t", "-s", "pp-probe-broom", "the-yard")
    swept_latch = [one for one in persistence.signals_of(session_of(mot_member.meta))
                   if one.get("signal") == "swept"]
    if (swept.returncode == 0 and "pp-probe-broom: swept the-yard" in swept.stdout
            and swept_latch and swept_latch[0].get("door") == "PP-RULES"
            and swept_latch[0].get("source") == "probe"):
        held("a package motor pushes without code", "the manifest declares "
             "`at: gesture:pp-probe-broom`; the gesture plays and the engine pushes -- data "
             "end to end. What REACHES a later block is the entry a `::push` STANDS: a "
             "motor's latch lives in its own run")
    else:
        failures.append(f"  ✗ package motor               rc={swept.returncode} "
                        f"{swept.stdout[-200:]!r} {swept.stderr[-200:]!r} {swept_latch}")
    return 0
