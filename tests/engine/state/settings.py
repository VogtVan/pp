"""Scenario `settings` -- the instance's settings, composed, preset and owned:
- `install.sync_settings` composes the engine's template then every fragment, keeps the
  operator's values, fills an empty key, carries a stranger after the known keys, and is
  idempotent; the template seeds every protocol key, valued -- every key an effort presets at
  what medium presets, the seeds the same, key by key
- the effort presets the weight keys over the written ones; an unknown level and an unknown
  body serve refuse
- the engine's effort table: `effective` renders its rows key by key under light, medium
  and full -- the packages' rows are proven in their own areas
- a key the engine retired (`settings.RETIRED_KEYS`): a SETTINGS document that carries one refuses
  `settings-invalid` at the reading, the refusal naming the key; no effort presets it, no seed, no
  typed setting and no line of the template carries it, and the face that writes one value refuses it
- the protocol key `tools_in_scope`: posed by the effort (light and medium `false`, full `true`),
  `false` when absent with no effort, `true` read, any other value refused, seeded by the template
  at what medium presets
- a package's settings are its own: the engine seeds and presets the protocol's keys
  alone, a package's keys ride its fragment, prefixed; an upgrade at constant pins moves
  nothing
- a `material.<name>` key is no key of the product any more: the sync carries it under
  `unowned` and says it once, the reading ignores it, the face that writes one value refuses it
- the system laws owe nothing to the effort: under light, medium and full every output says them
  whole, while a document's law comes back as its code under the efforts that preset the codes
- the engine key `records_read_limit`, the bound of every read of the records' store: 100 when
  absent, the value posed read, 0, a negative, a fraction or a word refused `settings-invalid`
The face that writes one value, a fragment's keys, its presets and its refusals are the
pattern `packaging/settings-fragment`'s; the records a package seeds, `packaging/seed`'s.
"""
from __future__ import annotations

import re

from conductor import (Conductor, Refusal, compiling, discovery, install, instance, persistence, reading,
                       settings)
from tests.harness import SOURCE, cli

# key -> (light, medium, full): the engine's own rows of the effort table
ENGINE_TABLE = {
    "verbatim_constraints": (False, False, True),
    "instructions_fusion": ("max", "max", "none"),
    "proc_body_serve": ("once", "once", "always"),
    "tools_in_scope": (False, False, True),
}
KIT_KEYS = ("session_memory_frequency", "history_day")


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
    seeds = dict(install.SEEDS)
    drift = [key for key in settings.PRESET
             if not (str(template_front.get(key)).lower() == seeds.get(key)
                     == settings._spelled(settings.PRESET[key]))]
    if (not unseeded and not empty and not drift
            and str(template_front.get("conduction_effort")) == settings.DEFAULT_EFFORT
            and all(key.startswith(name + "_") or name == instance.base_of(made)
                    for name, key in package_keys)
            and all(key in one.types for one in fragments for key, _ in one.defaults)):
        held("the template seeds the protocol alone", "every protocol key present, bare, "
             "none empty -- effort medium, no dead key; every key an effort presets seeded, "
             "written and spelled as medium presets it, key by key; every package "
             "key prefixed and typed at its fragment -- the base's bare (the stand-in "
             "declares none)")
    else:
        failures.append(f"  ✗ template completeness       missing {unseeded!r} empty {empty!r} drift {drift!r}")


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


def retired(bench) -> None:
    """A key the engine retired is refused by its name: at the reading, and at the face that writes one
    value; the presets, the seeds, the typed settings and the template carry none."""
    held, failures = bench.held, bench.failures
    made = bench.env("retired").made
    path = made / settings.DOCUMENT
    keys = tuple(getattr(settings, "RETIRED_KEYS", ()))
    said = {}
    for key in keys:
        _rewrite_key(path, key, "anything")
        try:
            settings.of(made)
            said[key] = ""
        except Refusal as refusal:
            said[key] = f"{refusal.code}: {refusal}"
            bench.refusals += 1
        _rewrite_key(path, key, None)
    unrefused = [key for key in keys if not (said[key].startswith("settings-invalid") and f"`{key}`" in said[key])]
    try:
        settings.of(made)
        standing = True
    except Refusal:
        standing = False
    if "conduction" in keys and not unrefused and standing:
        held("a retired key refuses by its name", f"{', '.join(keys)}: a SETTINGS document that carries the key "
             "refuses settings-invalid at the reading, the key in the refusal; the key taken out, the reading plays")
    else:
        failures.append(f"  ✗ a retired key               keys={keys!r} unrefused={unrefused!r} said={said!r} "
                        f"standing={standing}")

    template = reading.read(SOURCE / "template" / "instance" / "SETTINGS.md").front
    carried = {"efforts": [key for key in keys if any(key in level for level in settings.EFFORTS.values())],
               "seeds": [key for key in keys if key in dict(settings.SEEDS)],
               "typed": [key for key in keys if hasattr(settings.Settings(), key)],
               "template": [key for key in keys if key in template]}
    if keys and not any(carried.values()):
        held("nothing carries a retired key", "no level of the efforts, no seed, no field of the typed settings "
             "and no line of the template's front matter")
    else:
        failures.append(f"  ✗ a retired key carried       keys={keys!r} {carried!r}")
    for key in keys:
        bench.expect("settings-invalid", lambda key=key: settings.write(made, key, "anything"))


def scoped(bench) -> None:
    """The protocol key `tools_in_scope`: whether the offers of a step are part of its scope -- `false`,
    a difference of offers opens no segment; `true`, it opens one."""
    held, failures = bench.held, bench.failures
    made = bench.env("scoped").made
    path = made / settings.DOCUMENT
    _rewrite_key(path, "conduction_effort", "none")
    _rewrite_key(path, "tools_in_scope", None)
    absent = getattr(settings.of(made), "tools_in_scope", None)
    _rewrite_key(path, "tools_in_scope", "true")
    read = getattr(settings.of(made), "tools_in_scope", None)
    _rewrite_key(path, "tools_in_scope", "maybe")
    try:
        settings.of(made)
        said = ""
    except settings.Refusal as refusal:
        said = refusal.code
        bench.refusals += 1
    template = (SOURCE / "template" / "instance" / "SETTINGS.md").read_text(encoding="utf-8")
    seeded = dict(settings.SEEDS).get("tools_in_scope")
    if (absent is False and read is True and said == "settings-invalid"
            and seeded == "false" and settings.PRESET.get("tools_in_scope") is False
            and f"\ntools_in_scope: {seeded}\n" in template.split("\n---\n", 1)[0] + "\n"):
        held("tools_in_scope is a flag, false unless said", "absent with no effort: false; `true` read; any "
             "other value refuses settings-invalid; the template's front matter and the engine's seed say "
             "`false`, what medium presets")
    else:
        failures.append(f"  ✗ tools_in_scope              absent={absent!r} read={read!r} refused={said!r} "
                        f"seeded={seeded!r} preset={settings.PRESET.get('tools_in_scope')!r}")


def read_limit(bench) -> None:
    """`records_read_limit`: the default, a value posed, the values refused."""
    held, failures = bench.held, bench.failures
    made = bench.env("read-limit").made
    path = made / settings.DOCUMENT
    _rewrite_key(path, "records_read_limit", None)
    absent = getattr(settings.of(made), "records_read_limit", None)
    _rewrite_key(path, "records_read_limit", "250")
    posed = getattr(settings.of(made), "records_read_limit", None)
    refused = []
    for wrong in ("0", "-3", "2.5", "many"):
        _rewrite_key(path, "records_read_limit", wrong)
        try:
            settings.of(made)
            refused.append("")
        except Refusal as refusal:
            refused.append(refusal.code)
            bench.refusals += 1
    _rewrite_key(path, "records_read_limit", None)
    template = reading.read(SOURCE / "template" / "instance" / "SETTINGS.md").front
    install.sync_settings(made, SOURCE)
    synced = reading.read(path).front.get("records_read_limit")
    unowned = "records_read_limit" in path.read_text(encoding="utf-8").split("# ---- unowned ----", 1)[-1] \
        if "# ---- unowned ----" in path.read_text(encoding="utf-8") else False
    settings.write(made, "records_read_limit", "40")
    written = settings.of(made).records_read_limit
    try:
        settings.write(made, "records_read_limit", "0")
        kept = ""
    except Refusal as refusal:
        kept, bench.refusals = refusal.code, bench.refusals + 1
    if (absent == settings.RECORDS_READ_LIMIT == 100 and posed == 250
            and refused == ["settings-invalid"] * 4
            and template.get("records_read_limit") == settings.RECORDS_READ_LIMIT and synced == 100
            and not unowned and written == 40 and kept == "settings-invalid"
            and settings.of(made).records_read_limit == 40):
        held("records_read_limit bounds the reads", "100 when absent, the value posed read; 0, a "
             "negative, a fraction and a word refuse settings-invalid; the template carries it, the sync "
             "places it among the engine's keys, settings.write poses it and refuses 0")
    else:
        failures.append(f"  ✗ records_read_limit          absent={absent!r} posed={posed!r} refused={refused!r} "
                        f"template={template.get('records_read_limit')!r} synced={synced!r} unowned={unowned} "
                        f"written={written!r} kept={kept!r}")


def _front_of(made) -> dict:
    return reading.read(made / "SETTINGS.md").front


def resources(bench) -> None:
    """A package's settings are its own: the engine's tables carry the protocol alone, an
    install and an upgrade materialize what the pins declare."""
    held, failures = bench.held, bench.failures

    # --- the engine's own tables carry the protocol alone ----------------------------
    seeded = {key for key, _ in settings.SEEDS}
    preset = {key for level in settings.EFFORTS.values() for key in level}
    if not (seeded & set(KIT_KEYS)) and not (preset & set(KIT_KEYS)) and not hasattr(settings.Settings(), "history_day"):
        held("the engine seeds the protocol", "no policy key in SEEDS, EFFORTS nor the "
             "typed Settings -- the kit's five ride its fragment")
    else:
        failures.append(f"  ✗ engine tables                {seeded & set(KIT_KEYS)} {preset & set(KIT_KEYS)}")

    # --- a fresh install: a package's keys in their group, prefixed --------------------
    env = bench.env("owned", packages=("greeter",))
    made = env.made
    front = _front_of(made)
    text = (made / "SETTINGS.md").read_text(encoding="utf-8")
    if (not any(key in front for key in KIT_KEYS) and "# ---- greeter ----" in text
            and front.get("greeter_word") == "hello"):
        held("a fresh install, as declared", "the greeter's fragment ships ONE prefixed key, "
             "greeter_word, in its own group; the base declares none of the five policy keys")
    else:
        failures.append(f"  ✗ fresh install                {[k for k in KIT_KEYS if k in front]} "
                        f"greeter group={'# ---- greeter ----' in text} word={front.get('greeter_word')!r}")

    # --- upgrade at constant pins: nothing moves -------------------------------------
    stamp = (made / "SETTINGS.md").read_bytes(), sorted(p.name for p in (made / ".sys" / "vendor").iterdir())
    told = install.upgrade(env.member)
    after = (made / "SETTINGS.md").read_bytes(), sorted(p.name for p in (made / ".sys" / "vendor").iterdir())
    if told == [] and after == stamp:
        held("a constant upgrade moves nothing", "SETTINGS and vendor byte for byte")
    else:
        failures.append(f"  ✗ constant upgrade             {told} {after == stamp}")


def material_key(bench) -> None:
    """`material.<name>` left the product: carried as a stranger, said once, never read, never written."""
    held, failures = bench.held, bench.failures
    made = bench.env("material-key").made
    path = made / "SETTINGS.md"
    install.sync_settings(made, SOURCE)                       # the composed file, before the key
    text = path.read_text(encoding="utf-8")
    head, tail = text.split("\n---\n", 1)
    marked = "# ---- unowned ----"
    lines = head.splitlines()
    at = next(i for i, line in enumerate(lines) if line.startswith("conduction_effort:")) + 1
    path.write_text("\n".join(lines[:at] + ["material.x: ../elsewhere"] + lines[at:]) + "\n---\n" + tail,
                    encoding="utf-8")
    first = install.sync_settings(made, SOURCE)
    tidied = path.read_text(encoding="utf-8")
    front = tidied.split("\n---\n", 1)[0]
    second = install.sync_settings(made, SOURCE)
    _rewrite_key(path, "work_repairs_allowed", "")           # a later sync with something else to say
    third = install.sync_settings(made, SOURCE)
    said = [one for one in first if "material.x" in one]
    try:
        read = settings.of(made)
        refused = ""
    except Refusal as refusal:
        read, refused = None, refusal.code
    if (len(said) == 1 and "materials:" in said[0]
            and marked in front and front.index(marked) < front.index("material.x: ../elsewhere")
            and second == [] and third and not any("material.x" in one for one in third)
            and "material.x: ../elsewhere" in path.read_text(encoding="utf-8")
            and read is not None and not hasattr(read, "materials")):
        held("a `material.` key is carried and said once", "the sync moves it under `unowned` and says "
             "where a tree is declared now; a second sync is silent, a later one that fills a key says "
             "nothing of it; the reading ignores it")
    else:
        failures.append(f"  ✗ the material key            said={said} second={second} third={third} "
                        f"refused={refused!r} unowned={marked in front}")
    bench.expect("settings-invalid", lambda: settings.write(made, "material.y", "elsewhere"))


SAYS = ("---\nname: SAYS\nkind: proc\nconstraints.production: |\n  CP1  the line is short.\n"
        "constraints.behavior: |\n  CB1  say it plainly.\nproc: |\n  INFER\n  PROVE\n  INFER\n  PROVE\n---\n"
        "Say a line.\n")
PROOF = '[{"code": "CP1", "evidence": "one line", "verdict": "ok"}]'
KEY = re.compile(r"run ([0-9a-f]{6})")


def system_preset(bench) -> None:
    """The system laws owe nothing to the effort: under light, medium and full, every output says
    them whole at its first CONSTRAINTS, while a document's law comes back as its code under the
    efforts that preset the codes."""
    held, failures = bench.held, bench.failures
    env = bench.env("effort-sys")
    env.write("procs/SAYS.md", SAYS)
    env.write_system(behavior="SYS8  the system's behavior law holds.")
    system = compiling.system_laws(env.made)
    seen: dict[str, tuple] = {}
    for level in ("light", "medium", "full"):
        env.write("SETTINGS.md", f"---\nname: SETTINGS\nkind: doc\nconduction_effort: {level}\n---\n")
        opened = cli(env.engine, "-new", "go", cwd=env.root, env={"PP_DOOR": "SAYS.md"})
        key = (KEY.search(opened.stdout) or KEY.search("run ------")).group(1)
        outputs, hops = [opened.stdout], 0
        while len(outputs) < 3 and hops < 6:           # the run moved on: each call one output
            hops += 1
            due = persistence.prints_of(persistence.slot_of(env.made, key))
            moved = (cli(env.engine, key, "-print", due[0]["document"], "-", cwd=env.root, stdin="said")
                     if due else cli(env.engine, key, "-", cwd=env.root, stdin=PROOF))
            if "▸ SAYS{" in moved.stdout:
                outputs.append(moved.stdout)
        firsts = [one.split("\n▌ CONSTRAINTS\n", 1)[1].split("\n\n", 1)[0].splitlines()
                  for one in outputs if "\n▌ CONSTRAINTS\n" in one]
        whole = len(firsts) >= 2 and all(all(str(law) in lines for law in system) for lines in firsts)
        coded = any(line.startswith("[") and any(law.code in line for law in system)
                    for one in outputs for line in one.splitlines())
        seen[level] = (whole, coded, any("[CB1]" in lines for lines in firsts), len(firsts))
    codes = {level: found[2] for level, found in seen.items()}
    if (all(whole and not coded for whole, coded, _, _ in seen.values())
            and codes == {"light": True, "medium": True, "full": False}):
        held("the system laws owe nothing to the effort", "light, medium and full: every output says "
             f"{' '.join(law.code for law in system)} whole, never a code; CB1 by its code under light "
             "and medium, whole under full")
    else:
        failures.append(f"  ✗ system laws and effort      {seen}")


def scenario(bench) -> int:
    system_preset(bench)
    synced(bench)
    effort(bench)
    effort_table(bench)
    retired(bench)
    scoped(bench)
    resources(bench)
    material_key(bench)
    read_limit(bench)
    return 0
