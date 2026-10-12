"""Scenario `settings-written` -- the face WRITES one value (plan core, phase l-etat,
batch le-reglage-ecrit-par-la-face): `settings.write(meta, key, value)` rewrites ONE
line of the instance's SETTINGS.md front matter and `of()` reads it back; a value the
reading refuses, or a key no fragment owns, refuses `settings-invalid` and leaves the
bytes; an absent line is added before the closing `---`, the body intact.
"""
from __future__ import annotations

from conductor import settings


def changed(before: str, after: str) -> list:
    """-> the positions of the lines of `after` that differ from `before`, an added or a
    removed line counting as one each."""
    old, new = before.splitlines(), after.splitlines()
    tail = range(min(len(old), len(new)), max(len(old), len(new)))
    return [n for n, (a, b) in enumerate(zip(old, new)) if a != b] + list(tail)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("written").made
    path = made / "SETTINGS.md"

    # --- one line moves: the cap the bench seeds goes to 200000, the previous value said
    before = path.read_text(encoding="utf-8")
    previous = settings.write(made, "max_harness_tool_output", 200000)
    after = path.read_text(encoding="utf-8")
    moved = changed(before, after)
    if previous == "60000" and settings.of(made).harness_cap == 200000 and len(moved) == 1:
        held("one line moves", f"max_harness_tool_output {previous} -> 200000, read back by of(); "
             f"{len(moved)} line changed, the rest byte for byte")
    else:
        failures.append(f"  ✗ one line moves             previous={previous!r} "
                        f"cap={settings.of(made).harness_cap} moved={moved}")

    # --- a refused value leaves the bytes: the reading's judge is the writing's
    kept = path.read_text(encoding="utf-8")
    bench.expect("settings-invalid", lambda: settings.write(made, "max_harness_tool_output", "banana"))
    if path.read_text(encoding="utf-8") == kept and settings.of(made).harness_cap == 200000:
        held("a refused value leaves the bytes", "SETTINGS.md identical after the refusal, 200000 still read")
    else:
        failures.append("  ✗ refused value              the file moved under a refusal")

    # --- an unknown key refuses: no fragment of the instance owns it
    bench.expect("settings-invalid", lambda: settings.write(made, "nobody_owns_this", "1"))
    if path.read_text(encoding="utf-8") == kept:
        held("an unknown key refuses", "no fragment owns `nobody_owns_this`; the file identical")
    else:
        failures.append("  ✗ unknown key                the file moved under a refusal")

    # --- an absent key is added before the closing ---, the body intact, no previous value
    bare = bench.env("bare").made
    head, body = "---\nname: SETTINGS\nkind: doc\n", "---\n\n# Tuning\n\nthe body\n"
    (bare / "SETTINGS.md").write_text(head + body, encoding="utf-8")
    previous = settings.write(bare, "work_repairs_allowed", 2)
    text = (bare / "SETTINGS.md").read_text(encoding="utf-8")
    if previous == "" and settings.of(bare).repairs_allowed == 2 and text == head + "work_repairs_allowed: 2\n" + body:
        held("an absent key is added", "work_repairs_allowed: 2 inserted before the closing ---, "
             "the body byte for byte, the previous value empty")
    else:
        failures.append(f"  ✗ absent key                 previous={previous!r} text={text!r}")
    return 0
