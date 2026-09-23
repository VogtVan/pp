"""Scenario `events` -- the BUS knows no policy (plan pp-split, batch
le-bus-des-evenements):
- a witness package declares families, signals, sectors and the default sector
- a threshold is a key of the SETTINGS the declaration references
- push, count, cross, stand, acquit -- with no improvement package at all
- the sector caps read `cap.<sector>` of the settings (migrated from improvement)
- a declared sink receives the production on stdin and speaks to the bus
- the family's VERIFIER (batch le-bus-lit-le-registre): an unverified slug never writes at
  either entry, the verifier's no is said back by the harvest, a latch whose node died
  drops at the service, a family without `verify:` refuses at the build, a missing
  verifier script refuses by name
- `improve:` at a manifest refuses by name
- the family's GUARDIAN (batch le-gardien-declare): a second provider guards a family it
  does not own, the registry merges verifier and guardian, two guardians refuse, a
  guard-only family nobody verifies refuses at the build, `guarded` relays the guardian's
  no and plays nothing when no guardian is declared
"""
from __future__ import annotations

import re

from conductor import compiling, contributions, events, instance

WITNESS = """name: witness
version: 0.0.1
description: a package whose events the bus carries without knowing them
requires: []
contributes:
  events:
    sectors:
      watch: {icon: 👁, default: true}
      aside: {cap: 1}
    vectors:
      witness-spot: {verify: pp-witness}
    signals:
      noticed: {threshold: "@SETTINGS.witness_patience", priority: 2, door: WATCH, standing: true}
      aside-seen: {sector: aside, priority: 3, standing: true}
      nameless: {priority: 4}
"""
FRAGMENT = "---\nname: SETTINGS\nkind: doc\nwitness_patience: 2\n---\n\n# Witness\n\n- `witness_patience` -- how many sightings cross.\n"
SINK = ("#!/usr/bin/env python3\nimport sys\nline = sys.stdin.read().strip()\n"
        "print('::push aside-seen', line, 'the sink saw it')\nprint('the sink says: seen', line)\n")
KEEPER = """name: keeper
version: 0.0.1
description: a package that guards a family it does not own
requires: [witness]
contributes:
  events:
    vectors:
      witness-spot: {guard: pp-keeper}
"""
# the keeper's GUARDIAN: the verb `guard`, the vector on stdin, rc 0 = free -- a slug that
# starts with `held` is still worked elsewhere, the keeper says no with its reason
GUARDIAN = ("#!/usr/bin/env python3\nimport sys\nvector = sys.stdin.read().strip()\n"
            "slug = vector.split(':', 1)[-1]\n"
            "if slug.startswith('held'):\n"
            "    print(f'pp-keeper: `{slug}` is still held by a neighbour', file=sys.stderr)\n"
            "    raise SystemExit(2)\nraise SystemExit(0)\n")
# the witness's VERIFIER: the verb `verify`, the vector on stdin, rc 0 or a named no --
# a slug that starts with `ghost` is no node of the witness
VERIFIER = ("#!/usr/bin/env python3\nimport sys\nvector = sys.stdin.read().strip()\n"
            "slug = vector.split(':', 1)[-1]\n"
            "if slug.startswith('ghost') or slug in sys.argv[2:]:\n"
            "    print(f'pp-witness: `{slug}` is no node of the witness', file=sys.stderr)\n"
            "    raise SystemExit(2)\nraise SystemExit(0)\n")


def _strip_kit_events(made) -> None:
    """The kit's own events leave the composition: the bus must stand without them."""
    kit = next(one for one in instance.vendored(made) if one.name.startswith("kit@"))
    manifest = kit / "package.yaml"
    text = manifest.read_text(encoding="utf-8")
    head, _, _ = text.partition("  events:\n")
    manifest.write_text(head, encoding="utf-8")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("bus").made
    _strip_kit_events(made)
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    (root / "settings").mkdir(parents=True)
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (root / "settings" / "SETTINGS.md").write_text(FRAGMENT, encoding="utf-8")
    home = root / "skills" / "pp-witness-watch"
    home.mkdir(parents=True)
    (home / "SKILL.md").write_text("---\nname: pp-witness-watch\ndescription: the witness sink\n---\n\npp-witness-watch\n", encoding="utf-8")
    (home / "pp-witness-watch.py").write_text(SINK, encoding="utf-8")
    spot = root / "skills" / "pp-witness"
    spot.mkdir(parents=True)
    (spot / "SKILL.md").write_text("---\nname: pp-witness\ndescription: the witness verifier\n---\n\npp-witness\n", encoding="utf-8")
    (spot / "pp-witness.py").write_text(VERIFIER, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)

    # --- the declarations: the bus reads them, names nothing itself -----------------
    registry = events.providers(made)
    if (list(registry) == ["engine", "witness"] and events.default_sector(made) == "watch"
            and set(events.families(made)) == {"witness-spot"}):
        held("the bus reads the declarations", "the engine's builtin then the witness, "
             "the package default wins -- the kit's events stripped, no policy word left")
    else:
        failures.append(f"  ✗ declarations                 {list(registry)} {events.default_sector(made)}")

    # --- the threshold is a key the declaration references ----------------------------
    first = events.push(made, "witness", "noticed", vector="witness-spot:door")
    second = events.push(made, "witness", "noticed", vector="witness-spot:door")
    if first is None and second is not None and second["n"] == 2 and second["sector"] == "watch":
        held("a threshold by key", "witness_patience: 2 from the package's fragment -- the "
             "second sighting crosses, in the default sector")
    else:
        failures.append(f"  ✗ threshold                    {first} {second}")
    settings = made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace("---\n", "---\nwitness_patience: 5\n", 1),
                        encoding="utf-8")
    third = events.push(made, "witness", "noticed", vector="witness-spot:door")
    if third is None and events.counters(made)["witness-spot:door"]["count"] == 3:
        held("the instance's value wins", "witness_patience: 5 at SETTINGS -- three "
             "sightings do not cross, the count stands at 3")
    else:
        failures.append(f"  ✗ instance threshold           {third} {events.counters(made)}")

    # --- sectors: declared, default, unowned -------------------------------------------
    aside = events.push(made, "witness", "aside-seen", vector="witness-spot:x")
    nameless = events.push(made, "witness", "nameless", vector="witness-spot:y")
    if aside and aside["sector"] == "aside" and nameless and nameless["sector"] == "watch":
        held("sectors fall where declared", "aside-seen in its own sector, nameless in the "
             "declared default")
    else:
        failures.append(f"  ✗ sectors                      {aside} {nameless}")

    # --- standing and acquit ---------------------------------------------------------------
    events.stand(made, "noticed", "witness-spot:door", "a standing sighting")
    events.stand(made, "noticed", "witness-spot:window", "one that stays")
    stood = [one for one in events.standing_entries(made) if one.get("vector") == "witness-spot:door"]
    fell = events.acquit(made, "witness-spot:door")
    left = events.counters(made)
    kept = [one["vector"] for one in events.standing_entries(made)]
    expect("vector-unknown", lambda: events.acquit(made, "witness-spot:never-seen"))
    after_refusal = events.counters(made)
    if (stood and fell >= 2 and "witness-spot:door" not in left and kept == ["witness-spot:window"]
            and left.keys() == after_refusal.keys() and "acquit" in compiling.RESERVED):
        held("stand and acquit", "a standing entry rides, the acquit drops counter and "
             "entry together, the other vector serves on, and an unknown one refuses "
             "with nothing written -- `acquit` reserved at the console")
    else:
        failures.append(f"  ✗ acquit                       {stood} {fell} {kept}")

    # --- the sector caps: the manifest holds unsaid, the setting widens or mutes --------
    probed = [{"source": "witness", "signal": "aside-seen", "vector": f"witness-spot:v{i}",
               "sector": "aside", "n": 1} for i in range(3)]
    from conductor import settings as settings_module                       # noqa: PLC0415
    served_default = events.emitted(made, probed)
    document = made / "SETTINGS.md"
    kept_text = document.read_text(encoding="utf-8") if document.is_file() else ""
    document.write_text("---\nname: SETTINGS\nkind: doc\ncap.aside: 3\n---\n", encoding="utf-8")
    widened = dict(settings_module.of(made).sector_caps)
    served_widened = events.emitted(made, probed, sector_caps=widened)
    # the second write is LONGER on purpose: the reader's memo is guarded by (mtime_ns,
    # size), and two writes of the same size can share a tick on this filesystem
    document.write_text("---\nname: SETTINGS\nkind: doc\ncap.aside: 0\ncap.watch: 9\n---\n",
                        encoding="utf-8")
    muted = dict(settings_module.of(made).sector_caps)
    served_muted = events.emitted(made, probed, sector_caps=muted)
    document.write_text(kept_text, encoding="utf-8") if kept_text else document.unlink()
    if (len(served_default) == 1 and len(served_widened) == 3 and served_muted == []
            and widened == {"aside": 3} and muted == {"aside": 0, "watch": 9}):
        held("the sector caps read the settings", "the manifest's cap holds unsaid, "
             "`cap.<sector>` widens the serve, 0 mutes -- no hard constant at the cut")
    else:
        failures.append(f"  ✗ sector caps                  {len(served_default)}/"
                        f"{len(served_widened)}/{len(served_muted)} {widened}/{muted}")

    # --- the sink: stdin in, directives out, harvested by the ONE collector --------------
    said = events.sink(made, "pp-witness-watch", "witness-spot:window")
    stood = [one for one in events.standing_entries(made) if one.get("signal") == "aside-seen"]
    if said == ["the sink says: seen witness-spot:window"] and stood and stood[0].get("vector") == "witness-spot:window":
        held("a sink speaks to the bus", "the production on stdin, `::push` harvested, "
             "the other line said back")
    else:
        failures.append(f"  ✗ sink                         {said} {stood}")
    refused = events.sink(made, "pp-nowhere", "witness-spot:z")
    if refused and "no script skill" in refused[0]:
        held("an absent sink is said", refused[0])
    else:
        failures.append(f"  ✗ absent sink                  {refused}")

    # --- the verifier at the entries: an unverified slug never writes ------------------
    before = dict(events.counters(made))
    expect("vector-unverified", lambda: events.push(made, "witness", "noticed", vector="witness-spot:ghost-1"))
    expect("vector-unverified", lambda: events.stand(made, "noticed", "witness-spot:ghost-2", "never"))
    after = events.counters(made)
    if (after == before and not any("ghost" in key for key in after)):
        held("an unverified slug never writes", "push and stand ask the family's verifier "
             "first -- `vector-unverified` named at both entries, the record untouched")
    else:
        failures.append(f"  ✗ verified entries             {sorted(after)}")

    # --- the harvest says the verifier's no back: the producer hears it, the turn goes on
    said_back = events.harvest(made, "::push aside-seen witness-spot:ghost-3 nope\nplain line")
    ghosts = [one for one in events.standing_entries(made) if "ghost" in one.get("vector", "")]
    if (len(said_back) == 2 and said_back[0].startswith("witness-spot:ghost-3 refused")
            and "pp-witness" in said_back[0] and said_back[1] == "plain line" and not ghosts):
        held("the verifier's no is said back", "a harvested push the verifier refuses becomes "
             "a line for the producer, nothing stands, the other line rides")
    else:
        failures.append(f"  ✗ harvest says no              {said_back} {ghosts}")

    # --- the service's broom: a latch whose node died drops --------------------------
    (spot / "pp-witness.py").write_text(VERIFIER.replace("sys.argv[2:]", "['window']"), encoding="utf-8")
    served_after_death = [one["vector"] for one in events.standing_entries(made)]
    latched = [{"source": "witness", "signal": "noticed", "vector": "witness-spot:window", "sector": "watch", "n": 1},
               {"source": "witness", "signal": "aside-seen", "vector": "witness-spot:x", "sector": "aside", "n": 1}]
    standing_after_death = [one["vector"] for one in events.standing(made, latched)]
    (spot / "pp-witness.py").write_text(VERIFIER, encoding="utf-8")
    served_alive = [one["vector"] for one in events.standing_entries(made)]
    if ("witness-spot:window" not in served_after_death and "witness-spot:window" in served_alive
            and standing_after_death == ["witness-spot:x"]):
        held("a dead node drops at the service", "the verifier refuses `window`: the held "
             "entry and the run latch fall from the serve, the counter alone ages -- no "
             "broom of its own, the verifier IS the broom")
    else:
        failures.append(f"  ✗ service broom                {served_after_death} {standing_after_death} {served_alive}")

    # --- no vector without its verifier: the build refuses a bare family by its name ----
    (root / "package.yaml").write_text(WITNESS.replace("witness-spot: {verify: pp-witness}", "witness-spot: {}"), encoding="utf-8")
    expect("family-unverified", lambda: compiling.build_tools(made))
    expect("family-unverified", lambda: events.providers(made))
    (root / "package.yaml").write_text(WITNESS.replace("verify: pp-witness", "verify: pp-nowhere"), encoding="utf-8")
    expect("verifier-missing", lambda: events.push(made, "witness", "noticed", vector="witness-spot:door"))
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    if events.families(made) == {"witness-spot": {"verify": "pp-witness", "source": "witness"}}:
        held("no vector without its verifier", "a family without `verify:` refuses at the "
             "build and at every read; a verifier no skill carries refuses by name; the "
             "registry holds the prefix, its verifier and its source -- nothing else")
    else:
        failures.append(f"  ✗ family form                  {events.families(made)}")

    # --- the GUARD, the family's second worker (batch le-gardien-declare) -----------------
    keeper = made / ".sys" / "vendor" / "keeper@0.0.1"
    keep = keeper / "skills" / "pp-keeper"
    keep.mkdir(parents=True)
    (keeper / "package.yaml").write_text(KEEPER, encoding="utf-8")
    (keep / "SKILL.md").write_text("---\nname: pp-keeper\ndescription: the keeper's guardian\n---\n\npp-keeper\n", encoding="utf-8")
    (keep / "pp-keeper.py").write_text(GUARDIAN, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["keeper"] = "0.0.1"
    instance.write(made, pins)
    merged = events.families(made)
    if merged == {"witness-spot": {"verify": "pp-witness", "source": "witness", "guard": "pp-keeper", "guard_source": "keeper"}}:
        held("the registry merges a verifier and a guardian", "the owner verifies, another "
             "provider guards, each with its source -- one entry, the whole composition's")
    else:
        failures.append(f"  ✗ merged registry              {merged}")
    events.guarded(made, "witness-spot:door")
    expect("vector-guarded", lambda: events.guarded(made, "witness-spot:held-gate"))
    (keep / "pp-keeper.py").unlink()
    expect("guardian-missing", lambda: events.guarded(made, "witness-spot:door"))
    (keep / "pp-keeper.py").write_text(GUARDIAN, encoding="utf-8")
    held("the guardian answers on the verifier's contract", "the verb `guard`, the vector on "
         "stdin: a free node passes, a held one refuses `vector-guarded` with the keeper's "
         "reason, a guardian no skill carries refuses by name")
    (root / "package.yaml").write_text(WITNESS.replace("witness-spot: {verify: pp-witness}", "witness-spot: {verify: pp-witness, guard: pp-witness}"), encoding="utf-8")
    expect("family-collision", lambda: events.families(made))
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (keeper / "package.yaml").write_text(KEEPER.replace("witness-spot: {guard: pp-keeper}", "witness-ghost: {guard: pp-keeper}"), encoding="utf-8")
    expect("family-unverified", lambda: compiling.build_tools(made))
    (keeper / "package.yaml").write_text(KEEPER, encoding="utf-8")
    held("one guardian per family, and no family without its verifier", "two guardians refuse "
         "`family-collision`; a family one provider guards and nobody verifies refuses at the build")
    del pins["packages"]["keeper"]
    instance.write(made, pins)
    ran = []
    real_run = events.subprocess.run
    events.subprocess.run = lambda *a, **k: (ran.append(a[0]), real_run(*a, **k))[1]
    try:
        events.guarded(made, "witness-spot:door")
    finally:
        events.subprocess.run = real_run
    if not ran and events.families(made) == {"witness-spot": {"verify": "pp-witness", "source": "witness"}}:
        held("no guardian, nothing plays", "the keeper unpinned, `guarded` returns without a "
             "subprocess -- a composition without a guardian pays nothing")
    else:
        failures.append(f"  ✗ guard without guardian       {ran} {events.families(made)}")

    # --- the retired key means NOTHING: the build passes and reads no event from it -------
    # la-purete-du-noyau (reprise) : the named refusal left with the package's vocabulary --
    # a dead key is not aliased and not policed either, it is simply not a declaration
    (root / "package.yaml").write_text(WITNESS.split("contributes:")[0] + "improve:\n"
                                       + WITNESS.split("  events:", 1)[1],
                                       encoding="utf-8")
    compiling.build_tools(made)
    if not events.families(made):
        held("the retired key declares nothing", "the build passes, `improve:` reads as no "
             "declaration -- no alias, no named refusal")
    else:
        failures.append(f"  ✗ retired key                  {events.families(made)}")
    (root / "package.yaml").write_text(WITNESS, encoding="utf-8")
    (root / "package.yaml").write_text(WITNESS.replace("aside: {cap: 1}", "aside: {cap: 1, default: true}"), encoding="utf-8")
    expect("sector-collision", lambda: events.default_sector(made))
    return 0
