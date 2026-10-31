"""Scenario `settings-fragment` -- the pattern `packaging/settings-fragment`, played from its
demonstration:
- the instance's SETTINGS composes the package's fragment: its keys in their own group, its section
  in the body, the operator's value kept, a second sync moving nothing
- a skill writes ONE value through the face and reads it back; a value the key's type refuses and a
  key no fragment owns refuse `settings-invalid` and leave the bytes; an absent key is added before
  the closing `---`, the body intact
- the fragment's effort presets land typed under the three levels
- a key without the package's prefix and an effort level the engine does not know refuse
  `settings-fragment-invalid`
- removing the package leaves its keys `unowned`, the operator's value intact; adding it back
  brings them home
"""
from __future__ import annotations

from conductor import install, reading, settings
from tests.harness import fragments, manifests, support, vendor

DRAWER, PATTERN = "packaging", "settings-fragment"
MANIFESTS = ("keeper.yaml", "levels.yaml", "loose.yaml")
FRAGMENTS = ("keeper.md", "levels.md", "loose.md")
packaging = support(__file__, "source")


def _front(text: str) -> str:
    return text.split("\n---", 1)[0]


def _changed(before: str, after: str) -> int:
    old, new = before.splitlines(), after.splitlines()
    return sum(a != b for a, b in zip(old, new)) + abs(len(old) - len(new))


def composed(bench, declared, given) -> None:
    """The fragment composed into the instance's SETTINGS, then written through the face."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("composed").made
    path = made / settings.DOCUMENT
    vendor(made, "keeper", declared["keeper.yaml"], {}, fragment=given["keeper.md"])
    install.sync_settings(made, bench.source())
    text = path.read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    section = given["keeper.md"].split("\n---\n", 1)[1].strip()
    again = install.sync_settings(made, bench.source())
    if ("# ---- keeper ----" in _front(text) and "keeper_care: asked" in _front(text)
            and section and section in body and not again):
        held("the fragment composes", "keeper's keys under their own group, its section in the "
             "body; a second sync moves nothing")
    else:
        failures.append(f"  ✗ composed                     again={again} {_front(text)[-200:]!r}")

    before = path.read_text(encoding="utf-8")
    previous = settings.write(made, "keeper_care", "total")
    after = path.read_text(encoding="utf-8")
    if (previous == "asked" and settings.of(made).of_package("keeper_care") == "total"
            and _changed(before, after) == 1):
        held("one line moves", "keeper_care asked -> total through the face, read back; one line changed")
    else:
        failures.append(f"  ✗ one line moves               previous={previous!r} "
                        f"read={settings.of(made).of_package('keeper_care')!r}")
    install.sync_settings(made, bench.source())
    if "keeper_care: total" in path.read_text(encoding="utf-8"):
        held("the sync keeps the operator's value", "keeper_care: total after a sync")
    else:
        failures.append("  ✗ value kept                   the sync moved keeper_care")

    kept = path.read_text(encoding="utf-8")
    expect("settings-invalid", lambda: settings.write(made, "keeper_depth", "deep"))
    expect("settings-invalid", lambda: settings.write(made, "keeper_nothing", "1"))
    if path.read_text(encoding="utf-8") == kept:
        held("a refused write leaves the bytes", "a depth that is no natural, a key nobody owns: "
             "SETTINGS.md identical")
    else:
        failures.append("  ✗ refused write                the file moved under a refusal")

    head, rest = kept.split("\n---\n", 1)
    path.write_text("\n".join(line for line in head.splitlines() if not line.startswith("keeper_depth:"))
                    + "\n---\n" + rest, encoding="utf-8")
    previous = settings.write(made, "keeper_depth", 3)
    added = path.read_text(encoding="utf-8")
    if (previous == "" and settings.of(made).of_package("keeper_depth") == 3
            and _front(added).endswith("keeper_depth: 3") and added.split("\n---\n", 1)[1] == rest):
        held("an absent key is added", "keeper_depth: 3 inserted before the closing ---, the body "
             "byte for byte, no previous value")
    else:
        failures.append(f"  ✗ absent key                   previous={previous!r} {_front(added)[-80:]!r}")

    seen = {}
    for level in ("light", "medium", "full"):
        path.write_text(f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n", encoding="utf-8")
        seen[level] = settings.effective(reading.read(path).front, made).get("keeper_depth")
    if seen == {"light": 1, "medium": 2, "full": 3}:
        held("the effort presets land typed", "keeper_depth 1, 2, 3 under light, medium, full -- numbers")
    else:
        failures.append(f"  ✗ presets                      {seen}")


def refused(bench, declared, given) -> None:
    """What a fragment may not declare."""
    expect = bench.expect
    for name in ("loose", "levels"):
        made = bench.env(f"refused-{name}").made
        vendor(made, name, declared[f"{name}.yaml"], {}, fragment=given[f"{name}.md"])
        expect("settings-fragment-invalid", lambda: settings.fragments(made))


def unowned(bench, declared, given) -> None:
    """The keys of a removed package wait under `unowned`."""
    held, failures = bench.held, bench.failures
    root = packaging.source(bench, {"keeper": {"manifest": declared["keeper.yaml"],
                                               "fragment": given["keeper.md"]}})
    made, member = packaging.installed(bench, root, "owned", ["keeper"])
    path = made / settings.DOCUMENT
    settings.write(made, "keeper_care", "total")
    install.remove_package(member, "keeper")
    removed = path.read_text(encoding="utf-8")
    install.add_package(member, "keeper")
    added = path.read_text(encoding="utf-8")
    if ("# ---- unowned ----" in removed and "keeper_care: total" in removed
            and "# ---- unowned ----" not in added and "keeper_care: total" in added):
        held("the keys wait under unowned", "keeper's key survives its removal under unowned, the "
             "operator's value intact; add brings it home")
    else:
        failures.append(f"  ✗ unowned keys                 {'unowned' in removed} {'total' in added}")


def scenario(bench) -> int:
    failures = bench.failures
    declared, given = manifests(DRAWER, PATTERN), fragments(DRAWER, PATTERN)
    if sorted(declared) != sorted(MANIFESTS) or sorted(given) != sorted(FRAGMENTS):
        failures.append(f"  ✗ the demonstration           {sorted(declared)!r} {sorted(given)!r} -- owed "
                        f"{sorted(MANIFESTS)!r} {sorted(FRAGMENTS)!r}")
        return 0
    composed(bench, declared, given)
    refused(bench, declared, given)
    unowned(bench, declared, given)
    return 0
