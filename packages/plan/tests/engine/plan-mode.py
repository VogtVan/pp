"""packages/plan -- the plan MODE: the package's TURN overlay rides every turn, and
the serve doctrine rides its procs (PLAN and PHASE serve references, a BATCH serves
code in touched/dependent sections)."""
from __future__ import annotations

import json

from conductor import Conductor, compiling, discovery, instance, reading
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, kept_document, load_script, reaches

FLOOR = "---\nname: FLOOR\nkind: proc\ndescription: a floor\ncycle: true\nproc: |\n  INFER\n---\n\nthe floor\n"


def _mounted(made) -> list[dict]:
    """-> the ledger lines the mounts of the instance wrote for its OWN plan documents."""
    return [line for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
            if one.get("kind") == "block" for line in (one.get("served") or [])
            if line.get("origin") == "mount" and line.get("package") == "instance"]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    proven_engine = PRODUCT_ENGINE
    # --- the plan package's TURN overlay: the plan mode rides every turn ----------------
    pmode_made = bench.env("pmode", ("plan",), pin=False).made
    pmode_member = discovery.instance_member(pmode_made / ".sys" / "engine" / "pp.py")
    pmode_c = Conductor(pmode_member, discovery.siblings_around(pmode_member),
                        proven_engine)
    pmode_base = instance.resolve(pmode_member.meta, "TURN.md")
    pmode_laws, pmode_tools = compiling.effective(pmode_member.meta,
                                                  reading.read(pmode_base))
    pmode_text, _ = pmode_c._composed(pmode_base)
    if ({"KT1", "KT2", "KT3", "KT4"} <= {one.code for one in pmode_laws}
            and "pp-plan" in [one.name for one in pmode_tools]
            and reaches(pmode_text, body_of(kept_document(SOURCE / "packages" / "plan", "TURN")))
            and str(pmode_base).endswith("procs/TURN.md")):
        held("the plan package overlays the TURN", "KT laws in force, pp-plan offered, "
             "the mode's body rides the served text -- the kit stays the base")
    else:
        failures.append(f"  \u2717 plan TURN overlay           base={pmode_base} "
                        f"{[one.code for one in pmode_laws]}")

    # --- the requires closure: `("plan",)` composes kit + steering + plan -------------
    vendored = {one.name.split("@")[0]
                for one in (pmode_made / instance.VENDOR).iterdir() if one.is_dir()}
    declared = instance.manifest_of(SOURCE / "packages" / "plan").get("requires") or []
    if {"kit", "steering", "plan"} <= vendored and declared == ["steering"]:
        held("the requires closure brings steering", 'the env `("plan",)` installs kit + '
             "steering + plan -- the manifest declares the functional dependency alone")
    else:
        failures.append(f"  \u2717 requires closure            vendored={sorted(vendored)} "
                        f"declared={declared}")

    # --- a mounted chain: the batch whole, its ancestors by selection, the laws untouched -----
    env = bench.env("pmount", ("plan",))
    settings = env.made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    env.write("FLOOR.md", FLOOR)
    vendor = next((env.made / ".sys" / "vendor").glob("plan@*"))
    plans = load_script(vendor / "skills" / "pp-plan" / "pp-plan.py")
    for address, name, prose in ((["job"], "Context", "the thesis nobody below needs again"),
                                 (["job"], "Target", "the plan's target"),
                                 (["job"], "Expected", "the plan's expected"),
                                 (["job"], "Items", "- ph -- a phase"),
                                 (["job", "ph"], "Ground", "the phase's ground, measured"),
                                 (["job", "ph"], "Target", "the phase's target"),
                                 (["job", "ph"], "Expected", "the phase's expected"),
                                 (["job", "ph"], "Items", "- bt -- a batch"),
                                 (["job", "ph", "bt"], "Ground", "the batch's ground")):
        plans.write_section(env.made, address, name, prose)
    plans.sections().constrain(env.made, env.made / "plans" / "job" / "PLAN.md", "KJ", "production",
                               ["the plan's own law"])

    def opened(key: str):
        runner = env.conductor(key)
        runner.forget()
        runner.start(env.made / "FLOOR.md")
        return lambda: env.conductor(key)

    by_selection, entire = opened("sel"), opened("all")
    chain = plans.mount_chain(env.made, ["job", "ph", "bt"])
    said = by_selection().mount(chain)
    codes = sorted(one.code for one in by_selection()._mount_laws())
    light = sum(line.get("chars", 0) for line in _mounted(env.made) if line["state"] == "served")
    again = by_selection().mount([{**one, "constraints": False} for one in chain])
    spared = [line["subject"] for line in _mounted(env.made) if line["state"] == "spared"]
    entire().mount(plans.mount_chain(env.made, ["job", "ph", "bt"], whole=True))
    heavy = sum(line.get("chars", 0) for line in _mounted(env.made) if line["state"] == "served") - light
    if ("the batch's ground" in said and "the plan's target" in said and "the phase's expected" in said
            and "the thesis nobody below needs again" not in said
            and "the phase's ground, measured" not in said
            and "INFORMATION — PLAN[## Target.." in said and "INFORMATION — PHASE[## Target.." in said
            and codes == sorted(one.code for one in entire()._mount_laws()) and "KJ1" in codes
            and any(one.startswith("PLAN[## Target") for one in spared) and "the plan's target" not in again
            and 0 < light < heavy):
        held("a mounted chain shows what the level needs", f"the batch whole, the plan and the phase "
             f"from their Target on, each part under its token and spared at a second mount; the same "
             f"laws in force either way; {light} c by selection, {heavy} c whole")
    else:
        failures.append(f"  \u2717 mounted chain               codes={codes} spared={spared} "
                        f"light={light} heavy={heavy} {said[-300:]!r}")

    # --- the serve doctrine rides the procs: references above, code in sections --------
    doc_plan = reading.served(instance.resolve(pmode_member.meta, "PLAN.md"))[0]
    doc_phase = reading.served(instance.resolve(pmode_member.meta, "PHASE.md"))[0]
    doc_batch = reading.served(instance.resolve(pmode_member.meta, "BATCH.md"))[0]
    procs = SOURCE / "packages" / "plan" / "procs"
    doctrine = (reaches(doc_plan, body_of(kept_document(procs, "PLAN"))) and reaches(doc_phase, body_of(kept_document(procs, "PHASE")))
                and reaches(doc_batch, body_of(kept_document(procs, "BATCH"))))
    if doctrine:
        held("the serve doctrine rides the procs", "PLAN and PHASE serve references, "
             "a BATCH serves code in touched/dependent sections, re-aligned at the landing")
    else:
        failures.append("  \u2717 serve doctrine              a proc lost its teaching")
    return 0
