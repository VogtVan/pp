"""Scenario `overlays` -- the PACKAGES' overlay space, on one house:
- a package's `overlays/` is interposed: never the base, applied before the user's
- the overlay BODY appends to the served text: the packages' prose, then the user's
- the overlay's serve ROWS compose: `+` stripped, the package's before the user's, none without
  overlay
- the rows are SERVED as the base enters: the boot's TURN block carries the package's reading
The user's overlay -- its deltas, its refusals, the root `overlays/` -- is the pattern
`composition/overlay`.
"""
from __future__ import annotations

from conductor import Conductor, compiling, discovery, instance, reading
from tests.harness import PRODUCT_ENGINE


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    proven_engine = PRODUCT_ENGINE
    ovl_env = bench.env("ovl", pin=False)
    ovl_made = ovl_env.made
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
