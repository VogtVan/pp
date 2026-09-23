"""Scenario `fresh-install` -- 1 case(s), in the monolith's order:
- le-member-s-ouvre: the template opens doors; a fresh install stays INERT
"""
from __future__ import annotations

from pathlib import Path
from conductor import compiling, instance, reading
from tests.harness import SOURCE, kept_document



def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- le-member-s-ouvre: the template opens doors; a fresh install stays INERT ----
    shelf_made = bench.env("shelfws").made
    shelf_member = (shelf_made / "MEMBER.md").read_text(encoding="utf-8")
    shelf_formats = (shelf_made / "FORMATS.md").read_text(encoding="utf-8")
    shelf_enum = compiling.format_enumeration(shelf_made)
    shelf_turn = next((shelf_made / ".sys" / "vendor").glob("kit@*/procs/TURN.md"))
    inert_laws, _ = compiling.effective(shelf_made, reading.read(shelf_turn))
    shelf_names = {name for name, _, _ in compiling.entries(shelf_made)}
    shelf_served = reading.body_of(reading.served(shelf_made / "MEMBER.md")[0])
    if (shelf_member == kept_document(SOURCE / "template", "MEMBER").read_text(encoding="utf-8") and "# M3 " in shelf_member
            and "uncomment" not in shelf_served and "M3" not in shelf_served
            and shelf_formats == kept_document(SOURCE / "template", "FORMATS").read_text(encoding="utf-8")
            and (shelf_made / "procs" / "_TURN.md").is_file()
            and (shelf_made / "procs" / "_BOOTNOTE.md").is_file()
            and "theme" not in shelf_enum and "brief" not in shelf_enum
            and [one.code for one in inert_laws] == ["T1", "T2", "T3", "T4"]
            and not any(one.startswith("_") or one == "BOOTNOTE" for one in shelf_names)
            and not instance.attached(shelf_made, "boot.ready")):
        held("the template opens doors, inert", "preferences in readme:, the SERVED body pure, "
             "the shelf seeded `_` -- nothing in force, cataloged or attached")
    else:
        failures.append(f"  ✗ template inert            {sorted(shelf_enum)} / "
                        f"{[c.code for c in inert_laws]} / {sorted(shelf_names)}")

    # arming: rename the overlay, paste a format, paste an M-code -- each takes hold
    (shelf_made / "procs" / "_TURN.md").rename(shelf_made / "procs" / "TURN.md")
    armed_laws, _ = compiling.effective(shelf_made, reading.read(shelf_turn))
    (shelf_made / "FORMATS.md").write_text(
        "---\nname: FORMATS\nkind: doc\nformats: |\n"
        "  table  stdin   the HOUSE table style\n"
        "  theme  stdin   a one-line theme statement, then themed sections\n---\n",
        encoding="utf-8")
    armed_enum = compiling.format_enumeration(shelf_made)
    (shelf_made / "MEMBER.md").write_text(
        shelf_member.replace("  # M3 ", "  M3 ", 1), encoding="utf-8")
    kit_member = instance.resolve(shelf_made, "MEMBER.md")
    armed_member_laws, _ = compiling.effective(shelf_made, reading.read(kit_member))
    (shelf_made / "procs" / "_BOOTNOTE.md").rename(shelf_made / "procs" / "BOOTNOTE.md")
    if ([one.code for one in armed_laws] == ["T1", "T2", "T3", "T6"]
            and armed_enum["table"][1] == "the HOUSE table style"
            and "theme" in armed_enum and "brief" not in armed_enum
            and any(one.code == "M3" for one in armed_member_laws)
            and instance.attached(shelf_made, "boot.ready") == ("BOOTNOTE.md",)):
        held("renaming, uncommenting and pasting arm the doors", "the overlay merges, the house "
             "table supersedes the kit's, uncommented M3 enters the laws, the note attaches")
    else:
        failures.append(f"  ✗ arming                    {[c.code for c in armed_laws]} / "
                        f"{armed_enum.get('table')!r} / {[c.code for c in armed_member_laws]}")
    return 0
