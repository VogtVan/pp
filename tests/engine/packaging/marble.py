"""Scenario `marble` -- 1 case(s), in the monolith's order:
- le-marbre-se-compile: the standing rules, compiled; the replace lock
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, compiling, discovery
from tests.harness import SOURCE, body_of, kept_document


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- le-marbre-se-compile: the standing rules, compiled; the replace lock ---------
    marbled_made = bench.env("marble").made
    system_art = marbled_made / ".sys" / "system.md"
    replace_art = marbled_made / ".sys" / "system.replace.md"
    first = system_art.read_bytes() if system_art.is_file() else b""
    compiling.build_system(marbled_made)
    if (system_art.is_file() and b"conducted" in first and b"verbatim" in first
            and system_art.read_bytes() == first
            and not (marbled_made / "SYSTEM_PROMPT.md").exists()
            and not replace_art.exists()):
        held("the marble compiles, append-only",
             "system.md at install, byte-stable across builds; SYSTEM_PROMPT.md never "
             "seeded, no replace artifact unasked")
    else:
        failures.append(f"  ✗ marble compile              {system_art.is_file()} {first[:60]!r}")

    (marbled_made / "SYSTEM_PROMPT.md").write_text("just prose, no front matter\n",
                                                   encoding="utf-8")
    compiling.build_system(marbled_made)
    warned_bare = (not replace_art.exists()
                   and any("override: true" in one for one in compiling.lint(marbled_made)))
    (marbled_made / "SYSTEM_PROMPT.md").write_text(
        "---\nname: SYSTEM_PROMPT\noverride: false\n---\nMy own base prompt.\n",
        encoding="utf-8")
    compiling.build_system(marbled_made)
    warned_false = (not replace_art.exists()
                    and any("override: true" in one for one in compiling.lint(marbled_made)))
    (marbled_made / "SYSTEM_PROMPT.md").write_text(
        "---\nname: SYSTEM_PROMPT\noverride: true\n---\nMy own base prompt.\n",
        encoding="utf-8")
    compiling.build_system(marbled_made)
    composed = replace_art.read_text(encoding="utf-8") if replace_art.is_file() else ""
    granted = (composed and not any("override: true" in one for one in compiling.lint(marbled_made))
               and composed.index("My own base prompt.") < composed.index("conducted"))
    (marbled_made / "SYSTEM_PROMPT.md").write_text(
        "---\nname: SYSTEM_PROMPT\noverride: false\n---\nMy own base prompt.\n",
        encoding="utf-8")
    compiling.build_system(marbled_made)
    retracted = not replace_art.exists()
    if warned_bare and warned_false and granted and retracted:
        held("the replace lock holds", "no `override: true`, no effect -- said by lint; "
             "granted, the user body leads and the marble appends; revoked, the artifact retracts")
    else:
        failures.append(f"  ✗ replace lock                {warned_bare}/{warned_false}/"
                        f"{bool(granted)}/{retracted}")

    extra_fragment = next((marbled_made / ".sys" / "vendor").glob("kit@*")) / "system" / "ZZ-extra.md"
    extra_fragment.parent.mkdir(exist_ok=True)
    extra_fragment.write_text("---\nname: ZZ\nkind: doc\ndescription: a second fragment\n---\n"
                              "Zebra orders hold.\n", encoding="utf-8")
    compiling.build_system(marbled_made)
    joined = system_art.read_text(encoding="utf-8")
    marble_head = body_of(kept_document(SOURCE / "kit", "MARBLE"))[:60]
    fragment_order = (marble_head in joined and "Zebra orders hold." in joined
                      and joined.index(marble_head) < joined.index("Zebra orders"))
    extra_fragment.unlink()
    compiling.build_system(marbled_made)
    if fragment_order and system_art.read_bytes() == first:
        held("fragments join in order", "kit first, name order within a package, no EOS "
             "leaked -- and the aggregate returns byte-identical once the fragment leaves")
    else:
        failures.append(f"  ✗ fragment order              {fragment_order}")

    marbled_engine = marbled_made / ".sys" / "engine" / "pp.py"
    marbled_member = discovery.instance_member(marbled_engine)
    import os as os_mod                                                   # noqa: PLC0415

    def marbled_boot() -> str:
        one = Conductor(marbled_member, discovery.siblings_around(marbled_member),
                        marbled_engine)
        block = one.start(one.boot("BOOT.md"))
        one.forget()
        return render(block) if block else ""

    served_boot = marbled_boot()
    os_mod.environ["PP_MARBLE"] = "1"
    try:
        quiet_boot = marbled_boot()
    finally:
        del os_mod.environ["PP_MARBLE"]
    if ("INFORMATION — standing orders" in served_boot
            and marble_head in served_boot
            and "standing orders" not in quiet_boot):
        held("the standing orders find their channel",
             "no PP_MARBLE: the boot serves them first; a wired marble declares itself "
             "and the boot stays quiet")
    else:
        failures.append(f"  ✗ standing orders channel     {('standing orders' in served_boot)}/"
                        f"{('standing orders' in quiet_boot)}")
    return 0
