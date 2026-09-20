"""Scenario `mount-directive` -- 1 case(s), in the monolith's order:
- the ::mount directive: a script's chain mounts in the same gesture
"""
from __future__ import annotations

import contextlib
import io
from conductor import Conductor, discovery, persistence
from tests.harness import document, session_of


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


    # --- the ::mount directive: a script's chain mounts in the same gesture ------------
    import pp as pp_cli
    mnt3_siblings = bench.town(["core"]).siblings
    mnt3_home = discovery.member(mnt3_siblings, "core")

    def mnt3_c() -> Conductor:
        return Conductor(mnt3_home, mnt3_siblings, script, "t")

    (mnt3_home.meta / "MFORMS.md").write_text(
        "---\nname: MFORMS\ndescription: f\nformats: |\n"
        "  json  inline  one valid JSON value\n---\n", encoding="utf-8")
    (mnt3_home.meta / "EXT3.md").write_text(
        "---\nname: EXT3\nconstraints.behavior: |\n  Y1  the harvested law binds.\n---\n\n"
        "harvested matter\n", encoding="utf-8")
    mnt3_doc = document("---\nname: MJOB\ncycle: true\noutput: json\nproc: |\n"
                        "  INFER\n  PICK member\n---\n", at=mnt3_home.meta)
    mnt3_c().start(mnt3_doc)
    mnt3_probe = mnt3_home.meta / "probe-mount.py"
    mnt3_probe.write_text(
        'def main(argv):\n'
        '    print(\'::mount [{"doc": "EXT3.md", "scope": "nested"}]\')\n'
        '    print("probe: chain derived")\n'
        '    return 0\n', encoding="utf-8")
    mnt3_buffer = io.StringIO()
    with contextlib.redirect_stdout(mnt3_buffer):
        mnt3_rc = pp_cli._played(mnt3_c(), mnt3_probe, [], "probe-mount")
    mnt3_said = mnt3_buffer.getvalue()
    mnt3_standing = persistence.mounted_of(session_of(mnt3_home.meta))
    if (mnt3_rc == 0 and "::mount" not in mnt3_said
            and "probe: chain derived" in mnt3_said and "▸ EXT3" in mnt3_said
            and "Y1  the harvested law binds." in mnt3_said
            and [one["doc"] for one in mnt3_standing] == ["EXT3.md"]):
        held("the ::mount directive is harvested", "the script derives, pp hosts in the same "
             "gesture -- the directive never reaches the terminal, the mounted scope renders")
    else:
        failures.append(f"  ✗ mount harvest               rc={mnt3_rc} {mnt3_said[:140]!r}")
    return 0
