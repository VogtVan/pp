"""Scenario `overlays` -- a same-name document in a nearer space carries DELTAS, never a
shadow, on one house:
- the user's overlay merges its deltas (`+` a law, `+` a tool) on the bare TURN; the base still
  resolves to the bundle and the overlaid boot still plays
- a delta that adds an existing law, removes an absent one or carries a `proc:` refuses by name
- the packages' overlay space: interposed, never the base
- the overlay BODY appends to the served text
- the overlay's serve ROWS compose: `+` stripped, application order, none without overlay
- a `-` serve row refuses by name (`overlay-serve-removal`), at the composer and at compile
- the rows are SERVED as the base enters: the boot's TURN block carries the witness reading
"""
from __future__ import annotations

from conductor import Conductor, compiling, discovery, instance, reading
from tests.harness import PRODUCT_ENGINE, pin_step


def deltas(bench, env) -> None:
    """The user's overlay of TURN on the bare base: its deltas merge, its refusals name
    themselves, the bundle still resolves and plays past the member. The house is left as it
    was found: no overlay, no member, no run, its settings as they stood. The boot plays step
    by step (`pin_step`): the member's block, then the turn's cession."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made, engine = env.made, env.engine
    settings = made / "SETTINGS.md"
    standing = settings.read_text(encoding="utf-8")
    pin_step(made)
    env.write_member()
    member = discovery.instance_member(engine)

    def fresh() -> Conductor:
        return Conductor(member, engine, "t")

    kit_turn = next((made / ".sys" / "vendor").glob("kit@*/procs/TURN.md"))
    (made / "procs").mkdir(exist_ok=True)
    (made / "procs" / "NOTE.md").write_text(
        "---\nname: NOTE\nkind: proc\ndescription: a note the overlay offers\nproc: |\n  INFER\n---\njot\n",
        encoding="utf-8")
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  +X9  overlays add.\ntools: |\n  +NOTE\n---\n",
        encoding="utf-8")
    laws, tool_kit = compiling.effective(member.meta, reading.read(kit_turn))
    if ([one.code for one in laws] == ["X9"]
            and [one.name for one in tool_kit] == ["NOTE"]
            and tool_kit[-1].contract.endswith("NOTE.md")):
        held("an overlay merges its deltas", "+X9 lands, +NOTE joins the bare TURN")
    else:
        failures.append(f"  ✗ overlay merge             {[one.code for one in laws]} / {tool_kit}")

    if instance.resolve(member.meta, "TURN.md") == kit_turn:
        held("the base still executes", "the overlay never shadows -- resolution stays on the bundle")
    else:
        failures.append(f"  ✗ overlay shadowed          {instance.resolve(member.meta, 'TURN.md')}")

    landed = fresh().resume(fresh().boot("BOOT.md"))
    for _ in range(6):             # ride the boot reading's CONTINUEs to the member's step
        if landed and landed.command:
            break
        landed = fresh().resume(fresh().boot("BOOT.md"))
    ceded = fresh().submit("")
    if (ceded is not None and ceded.document == "TURN"
            and ceded.instruction.keyword == "WORK"):
        held("the overlaid boot still plays", "merged sections in force, the bundle's proc intact -- the turn still cedes")
    else:
        failures.append(f"  ✗ overlaid boot             {ceded and ceded.command!r}")
    fresh().forget()

    # a silent no-op delta is a lie -- and flow never extends by shadowing a proc
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  +X9  once.\n  +X9  doubled.\n---\n", encoding="utf-8")
    expect("overlay-adds-existing",
           lambda: compiling.effective(member.meta, reading.read(kit_turn)))
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -ZZ\n---\n", encoding="utf-8")
    expect("overlay-removes-nothing",
           lambda: compiling.effective(member.meta, reading.read(kit_turn)))
    (made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nproc: |\n  HOOK mine\n---\n", encoding="utf-8")
    expect("overlay-carries-proc",
           lambda: compiling.effective(member.meta, reading.read(kit_turn)))
    (made / "procs" / "TURN.md").unlink()
    (made / "procs" / "NOTE.md").unlink()
    (made / "procs" / "MEMBER.md").unlink()
    compiling.build_tools(made)
    settings.write_text(standing, encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    proven_engine = PRODUCT_ENGINE
    ovl_env = bench.env("ovl", pin=False)
    ovl_made = ovl_env.made
    deltas(bench, ovl_env)
    # --- the packages' overlay space: interposed, never the base ------------------------
    ovl_meta = discovery.instance_member(ovl_made / ".sys" / "engine" / "pp.py").meta
    ovl_kit = instance.vendored(ovl_meta)[0]
    (ovl_kit / "overlays").mkdir()
    (ovl_kit / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  TK9  the package overlay law binds.\n"
        "  TK8  the package's other law binds.\n---\n", encoding="utf-8")
    ovl_base = instance.resolve(ovl_meta, "TURN.md")
    ovl_laws = [one.code for one in
                compiling.effective(ovl_meta, reading.read(ovl_base))[0]]
    ovl_packaged = str(ovl_base).endswith("procs/TURN.md") and "TK9" in ovl_laws
    (ovl_meta / "procs").mkdir(exist_ok=True)
    (ovl_meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK9\n---\n", encoding="utf-8")
    ovl_after = [one.code for one in
                 compiling.effective(ovl_meta,
                                     reading.read(instance.resolve(ovl_meta, "TURN.md")))[0]]
    if ovl_packaged and ovl_after == ["TK8"]:
        held("the packages' overlay space", "interposed: never the base, applied before "
             "the user -- and the user's own space still wins")
    else:
        failures.append(f"  ✗ package overlays            base={ovl_base} "
                        f"codes={ovl_laws} after={ovl_after}")

    # --- the overlay BODY appends to the served text -----------------------------------
    ovl_member = discovery.instance_member(ovl_made / ".sys" / "engine" / "pp.py")
    ovl_c = Conductor(ovl_member, proven_engine)
    (ovl_kit / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  TK9  the package overlay law binds.\n---\n\n"
        "The appended method rides every serve.\n", encoding="utf-8")
    (ovl_meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK9\n---\n\n"
        "The user's word lands last.\n", encoding="utf-8")
    apd_base = instance.resolve(ovl_meta, "TURN.md")
    apd_text, apd_hash = ovl_c._composed(apd_base)
    raw_text, raw_hash = reading.served(apd_base)
    apd_ok = ("The appended method rides every serve." in apd_text
              and apd_text.find("appended method") < apd_text.find("word lands last")
              and apd_text.endswith("The user's word lands last.\n")
              and apd_hash != raw_hash)
    bare_doc = instance.resolve(ovl_meta, "BOOT.md")        # a base without an overlay
    apd_same = ovl_c._composed(bare_doc) == reading.served(bare_doc)
    if apd_ok and apd_same:
        held("the overlay body appends", "packages' prose then the user's, the hash over "
             "the composition -- and no overlay means bytes untouched")
    else:
        failures.append(f"  ✗ body append                 ok={apd_ok} same={apd_same} "
                        f"{apd_text[-160:]!r}")

    # --- the overlay's serve ROWS compose -------------------------------------------------
    (ovl_meta / "procs" / "WITNESS.md").write_text(
        "---\nname: WITNESS\nkind: doc\n---\n\nThe witness reading rides the overlay's row.\n",
        encoding="utf-8")
    (ovl_meta / "procs" / "SECOND.md").write_text(
        "---\nname: SECOND\nkind: doc\n---\n\nThe user's reading lands after the package's.\n",
        encoding="utf-8")
    (ovl_kit / "overlays" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  TK9  the package overlay law binds.\n"
        "serve: |\n  +WITNESS.md\n---\n\nThe appended method rides every serve.\n", encoding="utf-8")
    (ovl_meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK9\nserve: |\n  reference: SECOND.md\n---\n\n"
        "The user's word lands last.\n", encoding="utf-8")
    rows = ovl_c._overlay_rows(apd_base)
    bare_rows = ovl_c._overlay_rows(bare_doc)
    if rows == (("WITNESS.md",), ("reference:", "SECOND.md")) and bare_rows == ():
        held("the overlay's serve rows compose",
             "`+` stripped, the package's row before the user's, a base without overlay adds none")
    else:
        failures.append(f"  ✗ overlay rows                {rows!r} bare={bare_rows!r}")

    # --- a `-` serve row refuses by name --------------------------------------------------
    (ovl_meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK9\nserve: |\n  -WITNESS.md\n---\n", encoding="utf-8")
    minus_composer = minus_compile = ""
    try:
        ovl_c._overlay_rows(apd_base)
    except Exception as refusal:                      # the composer refuses
        minus_composer = str(refusal)
    try:
        compiling.effective(ovl_meta, reading.read(apd_base))
    except Exception as refusal:                      # and so does the compile
        minus_compile = str(refusal)
    if "overlay-serve-removal" in minus_composer and "overlay-serve-removal" in minus_compile:
        held("a `-` serve row refuses by name",
             "overlay-serve-removal at the composer and at compile -- an overlay never removes a reading")
    else:
        failures.append(f"  ✗ minus row                   composer={minus_composer[:80]!r} "
                        f"compile={minus_compile[:80]!r}")
    (ovl_meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  -TK9\n---\n", encoding="utf-8")

    # --- the rows are SERVED as the base enters --------------------------------------------
    from tests.harness import cli as _cli
    first = _cli(ovl_made / ".sys" / "engine" / "pp.py", "-new", cwd=ovl_made.parent)
    out = first.stdout
    key = ""
    for line in out.splitlines():
        if line.startswith("./pp ") and len(line.split()) >= 2:
            key = line.split()[1]
    served = out
    while key and "INFORMATION — WITNESS.md" not in out and "▶ CONTINUE" in served:
        served = _cli(ovl_made / ".sys" / "engine" / "pp.py", key, cwd=ovl_made.parent).stdout
        out += served                          # a cut boot continues on the bare call
    if "INFORMATION — WITNESS.md" in out and "witness reading rides" in out:
        held("the overlay's rows are served as the base enters",
             "the boot's TURN block carries `INFORMATION — WITNESS.md` -- the reading the "
             "package's overlay added, titled by its token")
    else:
        failures.append(f"  ✗ rows served at entry        key={key!r} {out[-200:]!r}")
    return 0
