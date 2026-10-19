"""Scenario `settings` -- the instance's settings, written, composed, preset and owned:
- `settings.write(meta, key, value)` rewrites ONE line of SETTINGS.md's front matter and
  `of()` reads it back; a value the reading refuses, or a key no fragment owns, refuses
  `settings-invalid` and leaves the bytes; an absent line is added before the closing
  `---`, the body intact
- `install.sync_settings` composes the engine's template then every fragment, keeps the
  operator's values, fills an empty key, carries a stranger after the known keys, and is
  idempotent; the template seeds every protocol key, valued
- the effort presets the weight keys over the written ones; an unknown level, an unknown
  body serve and a fragment's unprefixed key refuse
- the engine's effort table: `effective` renders its rows key by key under light, medium
  and full -- the packages' rows are proven in their own areas
- the protocol key `conduction`: `strict` when absent, `hybrid` read, any other value
  refused naming the two, written by the face and seeded `strict` by the template
- a package's settings are its own: the engine seeds and presets the protocol's keys
  alone, a package's keys ride its fragment, prefixed; an upgrade at constant pins moves
  nothing; a fragment's effort presets land typed under the three levels
"""
from __future__ import annotations

import shutil

from conductor import Conductor, contributions, discovery, install, instance, reading, settings
from tests.harness import SOURCE

# key -> (light, medium, full): the engine's own rows of the effort table
ENGINE_TABLE = {
    "verbatim_constraints": (False, False, True),
    "instructions_fusion": ("max", "max", "none"),
    "proc_body_serve": ("once", "once", "always"),
}
KIT_KEYS = ("session_memory_frequency", "history_day")


def changed(before: str, after: str) -> list:
    """-> the positions of the lines of `after` that differ from `before`, an added or a
    removed line counting as one each."""
    old, new = before.splitlines(), after.splitlines()
    tail = range(min(len(old), len(new)), max(len(old), len(new)))
    return [n for n, (a, b) in enumerate(zip(old, new)) if a != b] + list(tail)


def written(bench) -> None:
    """One line moves, a refusal leaves the bytes, an absent key is added."""
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


def _front_keys(text: str) -> list[str]:
    """-> the keys of a settings front matter, in order, the document's own three left out."""
    return [line.split(":", 1)[0] for line in text.split("\n---\n", 1)[0].splitlines()
            if line and line[0] not in "#- " and ":" in line
            and not line.startswith(("name", "kind", "description"))]


def synced(bench) -> None:
    """The settings follow the engine: composed, filled, idempotent; the template seeds them all."""
    held, failures = bench.held, bench.failures
    made = bench.env("synced").made
    path = made / "SETTINGS.md"
    path.write_text(
        "---\nname: SETTINGS\nkind: doc\n"
        "max_harness_tool_output: 26000\n---\n\n"
        "# SETTINGS\n\n"
        "- `stale_key` — the OLD prose, stale the day the template moved on\n"
        "  and its continuation line.\n"
        "- `capture_prompt` — the operator's own words, byte-for-byte.\n",
        encoding="utf-8")
    told = install.sync_settings(made, SOURCE)
    composed = path.read_text(encoding="utf-8")
    again = install.sync_settings(made, SOURCE)
    template_text = (SOURCE / "template" / "instance" / "SETTINGS.md").read_text(encoding="utf-8")
    fragments = settings.fragments(made)
    switches = [f"package.{name}" for name in instance.pins(made) if name != instance.base_of(made)]
    keys = _front_keys(template_text) + switches + [key for one in fragments for key, _ in one.defaults]
    body = template_text.split("\n---\n", 1)[1] + "".join(
        "\n" + one.body + ("" if one.body.endswith("\n") else "\n") for one in fragments)
    composed_body = composed.split("\n---\n", 1)[1]
    sections = [composed_body.index(f"## {one.name.capitalize()} — ") for one in fragments]
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
    if ("max_harness_tool_output: 26000" in composed
            and "conduction_effort: medium" in composed
            and "conduction: strict" in composed
            and _front_keys(composed) == keys
            and composed_body == body
            and sections == sorted(sections)
            and all(f"# ---- {one.name} ----" in composed for one in fragments)
            and "stale_key" not in composed
            and Conductor(member, made / ".sys" / "engine" / "pp.py")._settings.harness_cap == 26000
            and not again):
        held("the settings are composed", "the engine's template then every fragment in the "
             "requires topology -- keys grouped and marked, one named section each -- the "
             "operator's VALUES kept, every "
             "missing key lands VALUED -- and the sync is idempotent")
    else:
        failures.append(f"  ✗ settings sync               {told!r} {again!r} "
                        f"{_front_keys(composed) == keys} {composed_body == body}")

    path.write_text(
        "---\nname: SETTINGS\nkind: doc\nstranger_day: never\ndocument_serve: whole\n"
        "conduction_effort: medium\nwork_repairs_allowed:\n"
        "cap.stranger: 4\n# memory: 5\n---\n", encoding="utf-8")
    healed_told = install.sync_settings(made, SOURCE)
    healed = path.read_text(encoding="utf-8")
    front = healed.split("\n---\n", 1)[0]
    if ("work_repairs_allowed: 3" in healed
            and "# memory: 5" in healed
            and "document_serve: whole" in healed       # a dead key the operator still carries
            and "cap.stranger: 4" in healed          # an unowned stranger, kept, theirs to remove
            and front.index("cap.stranger") > front.index("conduction_effort")
            and front.index("stranger_day") > front.index("cap.stranger")
            and front.index("document_serve: whole") > front.index("cap.stranger")
            and front.index("# memory: 5") > front.index("stranger_day")
            and any("filled" in one for one in healed_told)):
        held("no key stays empty", "a key standing EMPTY fills with the default it "
             "silently played, the operator's own keys -- a dead one included -- travel "
             "after the known ones, a commented relic stays at the tail")
    else:
        failures.append(f"  ✗ empty fill                  {healed_told!r}")

    template_front = reading.read(SOURCE / "template" / "instance" / "SETTINGS.md").front
    unseeded = [key for key, _ in install.SEEDS if key not in template_front]
    empty = [key for key, value in template_front.items() if value is None or str(value).strip() == ""]
    package_keys = [(one.name, key) for one in fragments for key, _ in one.defaults]
    if (not unseeded and not empty
            and template_front.get("conduction") == "strict"
            and str(template_front.get("conduction_effort")) == "medium"
            and all(key.startswith(name + "_") or name == instance.base_of(made)
                    for name, key in package_keys)
            and all(key in one.types for one in fragments for key, _ in one.defaults)):
        held("the template seeds the protocol alone", "every protocol key present, bare, "
             "none empty -- effort medium, no dead key; every package "
             "key prefixed and typed at its fragment -- the base's bare (the stand-in "
             "declares none)")
    else:
        failures.append(f"  ✗ template completeness       missing {unseeded!r} empty {empty!r} {package_keys!r}")


def effort(bench) -> None:
    """The effort presets the weight keys over the written ones; the refusals of the reading."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("effort").made
    path = made / "SETTINGS.md"
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")

    def read():
        return Conductor(member, made / ".sys" / "engine" / "pp.py")._settings

    path.write_text("---\nname: SETTINGS\nkind: doc\nconduction_effort: light\n"
                    "verbatim_constraints: true\nmax_harness_tool_output: 26000\n---\n", encoding="utf-8")
    styled = read()
    if (styled.effort == "light" and not styled.verbatim_constraints
            and styled.body_serve == "once" and styled.fusion == 0 and styled.harness_cap == 26000):
        held("the effort presets alone", "light presets verbatim false, fusion max and body "
             "once over the written keys -- the cap stays the operator's; no role, no "
             "serve regime: the dead keys are gone")
    else:
        failures.append(f"  ✗ effort alone                {styled!r}")
    path.write_text("---\nname: SETTINGS\nkind: doc\nconduction_effort: heavy\n---\n", encoding="utf-8")
    expect("settings-invalid", read)

    def front(text: str) -> dict:
        path.write_text(f"---\nname: SETTINGS\nkind: doc\n{text}---\n", encoding="utf-8")
        return settings.effective(reading.read(path).front, made)

    medium = front("conduction_effort: medium\nproc_body_serve: always\n")
    none = front("conduction_effort: none\nproc_body_serve: once\n")
    if medium.get("proc_body_serve") == "once" and none.get("proc_body_serve") == "once":
        held("medium and none on the body's serve", "medium presets once over the "
             "operator's always; under none the bare key rules -- once stays once")
    else:
        failures.append(f"  ✗ medium/none on the body     {medium.get('proc_body_serve')!r} "
                        f"{none.get('proc_body_serve')!r}")
    path.write_text("---\nname: SETTINGS\nkind: doc\nproc_body_serve: sometimes\n---\n", encoding="utf-8")
    expect("settings-invalid", read)

    bad = made / ".sys" / "vendor" / "badpkg@0.0.1"
    (bad / "settings").mkdir(parents=True)
    (bad / "package.yaml").write_text("name: badpkg\nversion: 0.0.1\nrequires: []\n", encoding="utf-8")
    (bad / "settings" / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: fragment\npackage: badpkg\nloose_key: 1\n---\n", encoding="utf-8")
    pins = made / ".sys" / "instance.yaml"
    kept = pins.read_text(encoding="utf-8")
    pins.write_text(kept.replace("packages:\n", "packages:\n  badpkg: 0.0.1\n"), encoding="utf-8")
    expect("settings-fragment-invalid", lambda: settings.fragments(made))
    pins.write_text(kept, encoding="utf-8")
    shutil.rmtree(bad)


def effort_table(bench) -> None:
    """The engine's rows of the light / medium / full table, key by key under `effective`."""
    held, failures = bench.held, bench.failures
    made = bench.env("efforts").made
    seen = {}
    for level in ("light", "medium", "full"):
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n", encoding="utf-8")
        merged = settings.effective(reading.read(made / "SETTINGS.md").front, made)
        seen[level] = {key: merged.get(key) for key in ENGINE_TABLE}
    wrong = [(key, level, seen[level][key], want)
             for key, wants in ENGINE_TABLE.items()
             for level, want in zip(("light", "medium", "full"), wants)
             if seen[level][key] != want]
    if not wrong and seen["medium"] != seen["full"]:
        held("the effort table, three distinct levels", "light and medium keep the laws in codes "
             "and the body once, full fuses nothing and says everything -- key by key under "
             "`effective`; light and medium share the engine's rows, the packages' rows part them")
    else:
        failures.append(f"  ✗ effort table                {wrong!r}")


def _rewrite_key(path, key: str, value: str | None) -> None:
    """Rewrites ONE top-level key of the front matter: set when `value` is given, dropped otherwise."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    end = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
    kept = [l for i, l in enumerate(lines) if not (0 < i < end and l.split(":", 1)[0].strip() == key)]
    if value is not None:
        kept.insert(end - (len(lines) - len(kept)), f"{key}: {value}\n")
    path.write_text("".join(kept), encoding="utf-8")


def conduction(bench) -> None:
    """The protocol key `conduction`: where an output the agent's call renders goes in a run its
    principal conducts -- `strict` (held for the principal) or `hybrid` (a value asked comes
    back in the tool result)."""
    held, failures = bench.held, bench.failures
    made = bench.env("conduction").made
    path = made / settings.DOCUMENT

    # --- absent: strict -------------------------------------------------------------------------
    _rewrite_key(path, "conduction", None)
    absent = settings.of(made).conduction
    if absent == "strict" and "conduction:" not in path.read_text(encoding="utf-8"):
        held("absent is strict", "no `conduction:` line, of() says strict")
    else:
        failures.append(f"  ✗ absent                     {absent!r}")

    # --- hybrid read ----------------------------------------------------------------------------
    _rewrite_key(path, "conduction", "hybrid")
    read = settings.of(made).conduction
    if read == "hybrid":
        held("hybrid read", "`conduction: hybrid` -> of().conduction == hybrid")
    else:
        failures.append(f"  ✗ hybrid read                {read!r}")

    # --- a value outside the two refuses --------------------------------------------------------
    _rewrite_key(path, "conduction", "maybe")
    try:
        settings.of(made)
        said = ""
    except settings.Refusal as refusal:
        said = f"{refusal.code}: {refusal}"
        bench.refusals += 1
    if said.startswith("settings-invalid") and "strict" in said and "hybrid" in said:
        held("maybe refuses settings-invalid", f"{said}")
    else:
        failures.append(f"  ✗ maybe                      {said!r}")

    # --- written by the face; the template seeds it ---------------------------------------------
    _rewrite_key(path, "conduction", None)
    previous = settings.write(made, "conduction", "hybrid")
    template = (SOURCE / "template" / "instance" / "SETTINGS.md").read_text(encoding="utf-8")
    seeded = dict(settings.SEEDS).get("conduction")
    if (previous == "" and settings.of(made).conduction == "hybrid"
            and "\nconduction: strict\n" in template.split("\n---\n", 1)[0] + "\n" and seeded == "strict"):
        held("written by the face, seeded by the template", "write() adds the line, of() reads hybrid; the "
             "template's front matter says `conduction: strict`, the engine's seed the same")
    else:
        failures.append(f"  ✗ written/seeded             previous={previous!r} "
                        f"read={settings.of(made).conduction!r} seeded={seeded!r}")


def _front_of(made) -> dict:
    return reading.read(made / "SETTINGS.md").front


def _records(made) -> set[str]:
    home = made / ".sys" / "records"
    return {p.name for p in home.iterdir()} if home.is_dir() else set()


def resources(bench) -> None:
    """A package's settings and records are its own: the engine's tables carry the protocol
    alone, an install and an upgrade materialize what the pins declare, a fragment's presets
    land typed."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    # --- the engine's own tables carry the protocol alone ----------------------------
    seeded = {key for key, _ in settings.SEEDS}
    preset = {key for level in settings.EFFORTS.values() for key in level}
    if not (seeded & set(KIT_KEYS)) and not (preset & set(KIT_KEYS)) and not hasattr(settings.Settings(), "history_day"):
        held("the engine seeds the protocol", "no policy key in SEEDS, EFFORTS nor the "
             "typed Settings -- the kit's five ride its fragment")
    else:
        failures.append(f"  ✗ engine tables                {seeded & set(KIT_KEYS)} {preset & set(KIT_KEYS)}")

    # --- a fresh install: a package's keys in their group, prefixed; the records its seeds
    env = bench.env("owned", packages=("greeter",))
    made = env.made
    front = _front_of(made)
    text = (made / "SETTINGS.md").read_text(encoding="utf-8")
    if (not any(key in front for key in KIT_KEYS) and "# ---- greeter ----" in text
            and front.get("greeter_word") == "hello" and _records(made) == set()):
        held("a fresh install, as declared", "the greeter's fragment ships ONE prefixed key, "
             "greeter_word, in its own group; the base declares none of the five policy "
             "keys; no seed: no record")
    else:
        failures.append(f"  ✗ fresh install                {[k for k in KIT_KEYS if k in front]} "
                        f"greeter group={'# ---- greeter ----' in text} word={front.get('greeter_word')!r} {_records(made)}")
    expect("contribution-kind-unknown", lambda: contributions.contributions(
        {"name": "x", "version": "1", "contributes": {"resources": {"seed": ["a"]}}}))

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
    for level in ("light", "medium", "full"):
        (made / "SETTINGS.md").write_text(
            f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n", encoding="utf-8")
        merged = settings.effective(_front_of(made), made)
        seen[level] = (str(merged["probe_flag"]), merged["probe_depth"])
    if seen == {"light": ("false", 1), "medium": ("true", 2), "full": ("true", 3)}:
        held("the presets hold, three efforts", "a fragment's effort table lands typed -- "
             "the mechanism is the engine's, the values the package's")
    else:
        failures.append(f"  ✗ presets                      {seen}")


def scenario(bench) -> int:
    written(bench)
    synced(bench)
    effort(bench)
    effort_table(bench)
    conduction(bench)
    resources(bench)
    return 0
