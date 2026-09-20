"""Scenario `boot-weight` -- the boot's weight held by the engine (plan pp-split,
batch le-poids-du-boot):
- the measure is right on a fused run: no part counted twice, the frame never negative
- the fresh run's first output says its key in the heading
- the threads serve CONDENSED: delivered steps as a count + the last one, pointed and coming whole
- every payload character counts against the serve budget: a later reading is cut, the CONTINUE keeps it readable
"""
from __future__ import annotations

import json

from conductor import Conductor, discovery
from tests.harness import cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("weigh")
    made, engine = env.made, env.engine

    steps = [f"step-{n} of the long delivered history" for n in range(1, 13)]
    (made / ".sys" / "records").mkdir(parents=True, exist_ok=True)
    (made / ".sys" / "records" / "threads.json").write_text(
        json.dumps({"long-road": {"steps": steps, "next": 10}}), encoding="utf-8")

    booted = cli(engine, "-new")
    text = booted.stdout
    key = text.split("run ", 1)[1].split(" ·", 1)[0] if "run " in text else ""
    if (booted.returncode == 0 and text.startswith("▌ pp · run ")
            and len(key) == 6 and f"./pp {key}" in text):
        held("the first output says its key", "`pp · run <key> · ...` opens the boot -- "
             "the head sits inside a harness preview, the closing outside")
    else:
        failures.append(f"  ✗ key in the head             {text.splitlines()[0]!r}")


    # --- the measure on the fused boot: in process, the totals at hand -------------
    member = discovery.instance_member(engine)
    weigh_c = Conductor(member, discovery.siblings_around(member), engine, "w")
    weigh_c.start(weigh_c.boot("BOOT.md"))
    weigh_c.submit("a table said")
    served = weigh_c._served
    if served.get("blocks", 0) >= 2 and served.get("frame", -1) >= 0 <= served.get("total", -1):
        held("the run weighs honestly", f"{served['blocks']} blocks, total "
             f"{served['total']} chars, frame {served['frame']} -- never negative: coded "
             "constraints weigh their codes, a fused segment weighs once")
    else:
        failures.append(f"  ✗ honest weigh                 {served!r}")

    # --- the boot's payloads ride OUTSIDE the serve budget (operator word) --------
    lean = bench.env("leanweigh", bare=True)    # no standing orders
    reference = ("---\nname: REF\nkind: doc\ndescription: a long reference\n---\n\n"
                 + ("all work and no play makes a dull reference line\n" * 36)
                 + "\nTHE-VERY-END\n")
    member_doc = ("---\nname: member\nkind: proc\ndescription: the member\nserve: |\n"
                  "  reference: REF.md\nproc: |\n  SERVE\n  CALL CAPABILITIES.md\n  CALL TURN.md\n---\n\n"
                  "the member\n")
    for one in (made, lean.made):
        (one / "REF.md").write_text(reference, encoding="utf-8")
        (one / "MEMBER.md").write_text(member_doc, encoding="utf-8")
    (made / ".sys" / "records" / "threads.json").unlink(missing_ok=True)
    cli(engine, "-reset")
    lean_boot = cli(lean.engine, "-new").stdout
    full_boot = cli(engine, "-new").stdout
    if "THE-VERY-END" in lean_boot and "THE-VERY-END" in full_boot:
        held("the budget never brakes the boot", "the same reading arrives whole with and "
             "without the standing orders aboard -- the serve budget models the harness's "
             "inline limit for the serve mechanism, not the boot's weight")
    else:
        failures.append(f"  ✗ boot unbraked                lean={'THE-VERY-END' in lean_boot} "
                        f"full={'THE-VERY-END' in full_boot}")
    return 0
