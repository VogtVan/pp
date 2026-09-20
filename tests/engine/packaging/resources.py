"""Scenario `resources` -- a package's settings and records are its own (plan
pp-split, batch les-ressources-des-packages):
- the engine seeds and presets the protocol's keys alone; the kit's keys ride its fragment, bare
- install, add, remove and upgrade materialize exactly what the pinned packages declare
- a fragment's effort presets land typed, the same values under light, medium and full
"""
from __future__ import annotations

from conductor import compiling, contributions, install, instance, reading, settings

KIT_KEYS = ("workspace_improvement", "workspace_improvement_threshold",
            "workspace_improvement_next_max", "session_memory_frequency", "history_day")


def _front(made) -> dict:
    return reading.read(made / "SETTINGS.md").front


def _records(made) -> set[str]:
    home = made / ".sys" / "records"
    return {p.name for p in home.iterdir()} if home.is_dir() else set()


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- the engine's own tables carry the protocol alone ----------------------------
    seeded = {key for key, _ in settings.SEEDS}
    preset = {key for level in settings.EFFORTS.values() for key in level}
    if not (seeded & set(KIT_KEYS)) and not (preset & set(KIT_KEYS)) and not hasattr(settings.Settings(), "history_day"):
        held("the engine seeds the protocol", "no policy key in SEEDS, EFFORTS nor the "
             "typed Settings -- the kit's five ride its fragment")
    else:
        failures.append(f"  ✗ engine tables                {seeded & set(KIT_KEYS)} {preset & set(KIT_KEYS)}")

    # --- a fresh install: the kit's keys bare in their group, the records its seeds ---
    env = bench.env("owned")
    made = env.made
    front = _front(made)
    text = (made / "SETTINGS.md").read_text(encoding="utf-8")
    if (not any(key in front for key in KIT_KEYS) and "# ---- kit ----" not in text
            and _records(made) == set()):
        held("a fresh install, as declared", "the kit ships no fragment and no seed: "
             "the protocol keys alone, no record")
    else:
        failures.append(f"  ✗ fresh install                {[k for k in KIT_KEYS if k in front]} {_records(made)}")
    expect("contribution-kind-unknown", lambda: contributions.contributions(
        {"name": "x", "version": "1", "contributes": {"resources": {"seed": ["a"]}}}))

    # the late-add and unowned-keys cases ride closure.py now (a source probe with a
    # fragment): the kit no longer carries keys and plan waits for steering (KPS21).

    # --- upgrade at constant pins: nothing moves -------------------------------------
    stamp = (made / "SETTINGS.md").read_bytes(), _records(made), sorted(p.name for p in (made / ".sys" / "vendor").iterdir())
    told = install.upgrade(env.member)
    after = (made / "SETTINGS.md").read_bytes(), _records(made), sorted(p.name for p in (made / ".sys" / "vendor").iterdir())
    if told == [] and after == stamp:
        held("a constant upgrade moves nothing", "SETTINGS, records and vendor "
             "byte for byte")
    else:
        failures.append(f"  ✗ constant upgrade             {told} {after == stamp}")

    # --- a fragment's presets, typed, under the three efforts ------------------------
    probe_root = made / ".sys" / "vendor" / "probe@1"
    (probe_root / "settings").mkdir(parents=True)
    (probe_root / "package.yaml").write_text(
        "name: probe\nversion: '1'\ndescription: bench probe\nrequires: [kit]\n", encoding="utf-8")
    (probe_root / "settings" / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: fragment\npackage: probe\ndescription: probe keys\n"
        "probe_flag: true\nprobe_depth: 2\ntypes: |\n  probe_flag  free\n  probe_depth  natural\n"
        "effort: |\n  probe_flag  light=false medium=true full=true\n"
        "  probe_depth  light=1 medium=2 full=3\n---\n", encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["probe"] = "1"
    instance.write(made, pins)
    seen = {}
    for effort in ("light", "medium", "full"):
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {effort}\n---\n", encoding="utf-8")
        merged = settings.effective(_front(made), made)
        seen[effort] = (str(merged["probe_flag"]), merged["probe_depth"])
    if seen == {"light": ("false", 1), "medium": ("true", 2), "full": ("true", 3)}:
        held("the presets hold, three efforts", "a fragment's effort table lands typed -- "
             "the mechanism is the engine's, the values the package's")
    else:
        failures.append(f"  ✗ presets                      {seen}")
    return 0
