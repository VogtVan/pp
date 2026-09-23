"""Scenario `manifests` -- 3 case(s):
- a manifest is parsed ONCE per state of its file: identical bytes never parse again
- a rewritten manifest is parsed again at the next call, same size or not, in process
- the memo hands out copies: a declaration edited before its write never leaks back
"""
from __future__ import annotations

from conductor.state import instance


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    made = bench.env("memo", ("daneel",)).made
    parses = []                                        # one entry per yaml parse
    real = instance.yaml.safe_load
    instance.yaml.safe_load = lambda text: parses.append(1) or real(text)
    try:
        # --- parsed once: identical bytes hand back the parse already made -------------
        del parses[:]
        first = instance.read(made)
        for _ in range(4):
            instance.read(made)
        kit_root = next(one for one in instance.vendored(made) if one.name.startswith("kit@"))
        for _ in range(4):
            instance.manifest_of(kit_root)
            instance.vendored(made)
            instance.search_paths(made)
        manifests = 1 + len(instance.pins(made))            # instance.yaml + one per pin
        settings = 1 if (made / "SETTINGS.md").is_file() else 0   # the switches, read once too
        if len(parses) == manifests + settings and first.get("packages"):
            held("a manifest parses once", f"{manifests} parses for "
                 f"{5 + 4 * 3} reads of the instance and its {manifests - 1} packages, "
                 f"plus {settings} for the SETTINGS the package switches read")
        else:
            failures.append(f"  ✗ manifest memo                {len(parses)} parses, "
                            f"expected {manifests}")

        # --- a rewrite is read back at the next call: the bytes decide, not a clock ----
        del parses[:]
        pinned = instance.read(made)
        before = list(pinned["packages"])
        pinned["packages"] = dict(reversed(list(pinned["packages"].items())))
        instance.write(made, pinned)                        # same size, new bytes, same tick
        reordered = list(instance.read(made)["packages"])
        again = len(parses)
        (made / instance.MANIFEST).write_text((made / instance.MANIFEST).read_text(encoding="utf-8"),
                                              encoding="utf-8")   # identical bytes, by hand
        instance.read(made)
        if reordered == list(reversed(before)) and again == 1 and len(parses) == 1:
            held("a rewrite is read back", "new bytes parse once more at the next "
                 "call, identical bytes rewritten by hand parse nothing")
        else:
            failures.append(f"  ✗ manifest rewrite             {before} {reordered} "
                            f"parses={parses}")

        # --- the memo never leaks: the caller's copy is its own --------------------------
        edited = instance.read(made)
        edited["packages"]["ghost"] = "0"
        if "ghost" not in instance.read(made).get("packages", {}):
            held("the memo hands out copies", "a declaration edited before its write "
                 "leaves the memo untouched")
        else:
            failures.append("  ✗ manifest memo leaked         an edit reached the memo")
    finally:
        instance.yaml.safe_load = real
    return 0
