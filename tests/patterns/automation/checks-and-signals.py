"""Scenario `checks-and-signals` -- the pattern `automation/checks-and-signals`, played from its
demonstration: the BUS knows no policy, it carries what a package DECLARES:
- the witness declares sectors, a family and signals: the bus reads them; a threshold is a key of
  the settings, the instance's value wins; the sectors fall where declared; stand and `acquit`;
  the sector caps read the settings
- the directives a script prints: `::push` stands, `::clear` drops it; a sink speaks to the bus,
  an absent one is said
- the family's VERIFIER: an unverified slug never writes, the verifier's no is said back, a dead
  node drops at the service; a family without its verifier refuses at the build, a missing
  verifier by name; the GUARDIAN: merged with the verifier, its no relayed, two refuse, a guarded
  family nobody verifies refuses, without one nothing plays; `improve:` refuses `manifest-key-unknown`; two
  default sectors collide
- the pushes nobody declared refuse; a signal `at: gesture:<skill>` pushes when the gesture plays
- the sectors: a latch learns its own or the default, a named sector serves its declarant alone,
  a collision refuses every read; the arbitration ranks by priority then count, each sector
  under its own cap
The skills (verifier, guardian, sink, broom) and the witness's settings are written at the test's time.
"""
from __future__ import annotations

from conductor import compiling, events, instance, persistence
from conductor import settings as settings_module
from tests.harness import cli, demonstrated, demos, manifests, session_of, vendor

DRAWER, PATTERN = "automation", "checks-and-signals"
DEMOS = ("SWEEP.md",)
MANIFESTS = ("broom.yaml", "keeper.ghost.yaml", "keeper.yaml", "probe.arbitration.yaml", "probe.yaml",
             "rival.foreign.yaml", "rival.yaml", "witness.bare.yaml", "witness.defaults.yaml",
             "witness.guarded.yaml", "witness.nowhere.yaml", "witness.retired.yaml", "witness.yaml")
FRAGMENT = ("---\nname: SETTINGS\nkind: doc\nwitness_patience: 2\n---\n\n# Witness\n\n"
            "- `witness_patience` -- how many sightings cross.\n")
SINK = ("import sys\nline = sys.stdin.read().strip()\n"
        "print('::push aside-seen', line, 'the sink saw it')\nprint('the sink says: seen', line)\n")
GUARDIAN = ("import sys\nvector = sys.stdin.read().strip()\nslug = vector.split(':', 1)[-1]\n"
            "if slug.startswith('held'):\n"
            "    print(f'pp-keeper: `{slug}` is still held by a neighbour', file=sys.stderr)\n"
            "    raise SystemExit(2)\nraise SystemExit(0)\n")
VERIFIER = ("import sys\nvector = sys.stdin.read().strip()\nslug = vector.split(':', 1)[-1]\n"
            "if slug.startswith('ghost') or slug in sys.argv[2:]:\n"
            "    print(f'pp-witness: `{slug}` is no node of the witness', file=sys.stderr)\n"
            "    raise SystemExit(2)\nraise SystemExit(0)\n")
ZONE = "import sys\nsys.stdin.read()\nraise SystemExit(0)\n"
BROOM = "def main(argv):\n    print('pp-probe-broom: swept', ' '.join(argv) or 'clean')\n    return 0\n"


def _root(made, name: str):
    return made / ".sys" / "vendor" / f"{name}@0.0.1"


def _rewrite(made, name: str, manifest: str) -> None:
    (_root(made, name) / "package.yaml").write_text(manifest, encoding="utf-8")


def _witness(bench, declared):
    """-> a house carrying the witness, its settings fragment, its verifier and its sink."""
    made = bench.env("bus").made
    vendor(made, "witness", declared["witness.yaml"], {},
           {"pp-witness": VERIFIER, "pp-witness-watch": SINK})
    (_root(made, "witness") / "settings").mkdir(parents=True, exist_ok=True)
    (_root(made, "witness") / "settings" / "SETTINGS.md").write_text(FRAGMENT, encoding="utf-8")
    return made


def bus(bench, declared) -> None:
    """The declarations, the threshold, the sectors, stand and acquit, the caps, the directives."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = _witness(bench, declared)
    registry = events.providers(made)
    if (list(registry)[-1:] == ["witness"] and "engine" in registry and events.default_sector(made) == "watch"
            and set(events.families(made)) == {"witness-spot"}):
        held("the bus reads the declarations", "the engine's builtin then the witness, the package "
             "default wins -- no policy word of the engine's own")
    else:
        failures.append(f"  ✗ declarations                 {list(registry)} {events.default_sector(made)}")

    first = events.push(made, "witness", "noticed", vector="witness-spot:door")
    second = events.push(made, "witness", "noticed", vector="witness-spot:door")
    if first is None and second is not None and second["n"] == 2 and second["sector"] == "watch":
        held("a threshold by key", "witness_patience: 2 from the package's fragment -- the second "
             "sighting crosses, in the default sector")
    else:
        failures.append(f"  ✗ threshold                    {first} {second}")
    settings = made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace("---\n", "---\nwitness_patience: 5\n", 1),
                        encoding="utf-8")
    third = events.push(made, "witness", "noticed", vector="witness-spot:door")
    if third is None and events.counters(made)["witness-spot:door"]["count"] == 3:
        held("the instance's value wins", "witness_patience: 5 at SETTINGS -- three sightings do not "
             "cross, the count stands at 3")
    else:
        failures.append(f"  ✗ instance threshold           {third} {events.counters(made)}")

    aside = events.push(made, "witness", "aside-seen", vector="witness-spot:x")
    nameless = events.push(made, "witness", "nameless", vector="witness-spot:y")
    if aside and aside["sector"] == "aside" and nameless and nameless["sector"] == "watch":
        held("sectors fall where declared", "aside-seen in its own sector, nameless in the declared default")
    else:
        failures.append(f"  ✗ sectors                      {aside} {nameless}")

    events.stand(made, "noticed", "witness-spot:door", "a standing sighting")
    events.stand(made, "noticed", "witness-spot:window", "one that stays")
    stood = [one for one in events.standing_entries(made) if one.get("vector") == "witness-spot:door"]
    fell = events.acquit(made, "witness-spot:door")
    left = events.counters(made)
    kept = [one["vector"] for one in events.standing_entries(made)]
    expect("vector-unknown", lambda: events.acquit(made, "witness-spot:never-seen"))
    if (stood and fell >= 2 and "witness-spot:door" not in left and kept == ["witness-spot:window"]
            and left.keys() == events.counters(made).keys() and "acquit" in compiling.RESERVED):
        held("stand and acquit", "a standing entry rides, the acquit drops counter and entry together, "
             "the other vector serves on, an unknown one refuses with nothing written -- `acquit` "
             "reserved at the console")
    else:
        failures.append(f"  ✗ acquit                       {stood} {fell} {kept}")

    probed = [{"source": "witness", "signal": "aside-seen", "vector": f"witness-spot:v{i}",
               "sector": "aside", "n": 1} for i in range(3)]
    served_default = events.emitted(made, probed)
    kept_text = settings.read_text(encoding="utf-8")
    settings.write_text("---\nname: SETTINGS\nkind: doc\ncap.aside: 3\n---\n", encoding="utf-8")
    widened = dict(settings_module.of(made).sector_caps)
    served_widened = events.emitted(made, probed, sector_caps=widened)
    # the second write is LONGER: the reader's memo is guarded by (mtime_ns, size)
    settings.write_text("---\nname: SETTINGS\nkind: doc\ncap.aside: 0\ncap.watch: 9\n---\n", encoding="utf-8")
    muted = dict(settings_module.of(made).sector_caps)
    served_muted = events.emitted(made, probed, sector_caps=muted)
    settings.write_text(kept_text, encoding="utf-8")
    if (len(served_default) == 1 and len(served_widened) == 3 and served_muted == []
            and widened == {"aside": 3} and muted == {"aside": 0, "watch": 9}):
        held("the sector caps read the settings", "the manifest's cap holds unsaid, `cap.<sector>` "
             "widens the serve, 0 mutes")
    else:
        failures.append(f"  ✗ sector caps                  {len(served_default)}/{len(served_widened)}/"
                        f"{len(served_muted)} {widened}/{muted}")

    # --- the directives: `::push` stands, `::clear` drops it -------------------------------------
    events.harvest(made, "::push aside-seen witness-spot:k a note")
    pushed = [one for one in events.standing_entries(made) if one.get("vector") == "witness-spot:k"]
    events.harvest(made, "::clear aside-seen witness-spot:k")
    cleared = [one for one in events.standing_entries(made) if one.get("vector") == "witness-spot:k"]
    expect("push-malformed", lambda: events.harvest(made, "::clear aside-seen"))
    if pushed and not cleared:
        held("a push stands, a clear drops it", "`::push aside-seen witness-spot:k` stood an entry, "
             "`::clear aside-seen witness-spot:k` took it out")
    else:
        failures.append(f"  ✗ push / clear                 {pushed} {cleared}")

    said = events.sink(made, "pp-witness-watch", "witness-spot:window")
    stood = [one for one in events.standing_entries(made) if one.get("signal") == "aside-seen"]
    if said == ["the sink says: seen witness-spot:window"] and stood and stood[0].get("vector") == "witness-spot:window":
        held("a sink speaks to the bus", "the production on stdin, `::push` harvested, the other line said back")
    else:
        failures.append(f"  ✗ sink                         {said} {stood}")
    refused = events.sink(made, "pp-nowhere", "witness-spot:z")
    if refused and refused[0].startswith("pp-nowhere"):
        held("an absent sink is said", refused[0])
    else:
        failures.append(f"  ✗ absent sink                  {refused}")

    # --- the pushes nobody declared refuse --------------------------------------------------------
    expect("provider-unknown", lambda: events.push(made, "ghost", "noticed"))
    expect("signal-unknown", lambda: events.push(made, "witness", "moods"))
    expect("family-unknown", lambda: events.push(made, "witness", "noticed", vector="planet:mars"))


def families(bench, declared) -> None:
    """The verifier and the guardian of a family; the retired key refused; the default sector."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = _witness(bench, declared)
    events.stand(made, "noticed", "witness-spot:window", "one that stays")
    before = dict(events.counters(made))
    expect("vector-unverified", lambda: events.push(made, "witness", "noticed", vector="witness-spot:ghost-1"))
    expect("vector-unverified", lambda: events.stand(made, "noticed", "witness-spot:ghost-2", "never"))
    after = events.counters(made)
    if after == before and not any("ghost" in key for key in after):
        held("an unverified slug never writes", "push and stand ask the family's verifier first -- "
             "`vector-unverified` at both entries, the record untouched")
    else:
        failures.append(f"  ✗ verified entries             {sorted(after)}")

    said_back = events.harvest(made, "::push aside-seen witness-spot:ghost-3 nope\nplain line")
    ghosts = [one for one in events.standing_entries(made) if "ghost" in one.get("vector", "")]
    if (len(said_back) == 2 and said_back[0].startswith("witness-spot:ghost-3 refused")
            and "pp-witness" in said_back[0] and said_back[1] == "plain line" and not ghosts):
        held("the verifier's no is said back", "a harvested push the verifier refuses becomes a line for "
             "the producer, nothing stands, the other line rides")
    else:
        failures.append(f"  ✗ harvest says no              {said_back} {ghosts}")

    verifier = _root(made, "witness") / "skills" / "pp-witness" / "pp-witness.py"
    verifier.write_text(VERIFIER.replace("sys.argv[2:]", "['window']"), encoding="utf-8")
    served_after_death = [one["vector"] for one in events.standing_entries(made)]
    latched = [{"source": "witness", "signal": "noticed", "vector": "witness-spot:window", "sector": "watch", "n": 1},
               {"source": "witness", "signal": "aside-seen", "vector": "witness-spot:x", "sector": "aside", "n": 1}]
    standing_after_death = [one["vector"] for one in events.standing(made, latched)]
    verifier.write_text(VERIFIER, encoding="utf-8")
    served_alive = [one["vector"] for one in events.standing_entries(made)]
    if ("witness-spot:window" not in served_after_death and "witness-spot:window" in served_alive
            and standing_after_death == ["witness-spot:x"]):
        held("a dead node drops at the service", "the verifier refuses `window`: the held entry and the "
             "run latch fall from the serve -- the verifier IS the broom")
    else:
        failures.append(f"  ✗ service broom                {served_after_death} {standing_after_death} {served_alive}")

    _rewrite(made, "witness", declared["witness.bare.yaml"])
    expect("family-unverified", lambda: compiling.build_tools(made))
    expect("family-unverified", lambda: events.providers(made))
    _rewrite(made, "witness", declared["witness.nowhere.yaml"])
    expect("verifier-missing", lambda: events.push(made, "witness", "noticed", vector="witness-spot:door"))
    _rewrite(made, "witness", declared["witness.yaml"])
    if events.families(made) == {"witness-spot": {"verify": "pp-witness", "source": "witness"}}:
        held("no vector without its verifier", "a family without `verify:` refuses at the build and at "
             "every read; a verifier no skill carries refuses by name; the registry holds the prefix, "
             "its verifier and its source")
    else:
        failures.append(f"  ✗ family form                  {events.families(made)}")

    vendor(made, "keeper", declared["keeper.yaml"], {}, {"pp-keeper": GUARDIAN})
    merged = events.families(made)
    if merged == {"witness-spot": {"verify": "pp-witness", "source": "witness", "guard": "pp-keeper",
                                   "guard_source": "keeper"}}:
        held("the registry merges a verifier and a guardian", "the owner verifies, another provider "
             "guards, each with its source -- one entry")
    else:
        failures.append(f"  ✗ merged registry              {merged}")
    events.guarded(made, "witness-spot:door")
    expect("vector-guarded", lambda: events.guarded(made, "witness-spot:held-gate"))
    guardian = _root(made, "keeper") / "skills" / "pp-keeper" / "pp-keeper.py"
    guardian.unlink()
    expect("guardian-missing", lambda: events.guarded(made, "witness-spot:door"))
    guardian.write_text(GUARDIAN, encoding="utf-8")
    held("the guardian answers on the verifier's contract", "the verb `guard`, the vector on stdin: a "
         "free node passes, a held one refuses `vector-guarded`, a guardian no skill carries refuses by name")
    _rewrite(made, "witness", declared["witness.guarded.yaml"])
    expect("family-collision", lambda: events.families(made))
    _rewrite(made, "witness", declared["witness.yaml"])
    _rewrite(made, "keeper", declared["keeper.ghost.yaml"])
    expect("family-unverified", lambda: compiling.build_tools(made))
    _rewrite(made, "keeper", declared["keeper.yaml"])
    held("one guardian per family, and no family without its verifier", "two guardians refuse "
         "`family-collision`; a family one provider guards and nobody verifies refuses at the build")
    pins = instance.read(made)
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
        held("no guardian, nothing plays", "the keeper unpinned, `guarded` returns without a subprocess")
    else:
        failures.append(f"  ✗ guard without guardian       {ran} {events.families(made)}")

    _rewrite(made, "witness", declared["witness.retired.yaml"])
    expect("manifest-key-unknown", lambda: compiling.build_tools(made))
    _rewrite(made, "witness", declared["witness.defaults.yaml"])
    expect("sector-collision", lambda: events.default_sector(made))


def gesture(bench, declared) -> None:
    """A signal pushed when a gesture plays: the declaration and a skill, no line of engine code."""
    held, failures = bench.held, bench.failures
    env = bench.env("broom")
    made = env.made
    vendor(made, "probe", declared["broom.yaml"], {}, {"pp-probe-broom": BROOM})
    (made / "procs" / "SWEEP.md").write_text((demos(DRAWER, PATTERN) / "SWEEP.md").read_text(encoding="utf-8"),
                                             encoding="utf-8")
    compiling.build_tools(made)
    opener = env.conductor("t")
    opener.forget()
    opener.start(made / "procs" / "SWEEP.md")
    swept = cli(env.engine, "t", "-s", "pp-probe-broom", "the-yard", cwd=env.root)
    latch = [one for one in persistence.signals_of(session_of(env.member.meta)) if one.get("signal") == "swept"]
    if swept.returncode == 0 and latch and latch[0].get("door") == "REVIEW" and latch[0].get("source") == "probe":
        held("a gesture pushes without code", "the manifest declares `at: gesture:pp-probe-broom`; the "
             "gesture plays and the engine pushes `swept` -- data end to end")
    else:
        failures.append(f"  ✗ gesture motor                rc={swept.returncode} {swept.stderr[-200:]!r} {latch}")


def _probe(bench, declared, name: str, manifest: str):
    made = bench.env(name).made
    vendor(made, "probe", declared[manifest], {}, {"pp-zone": ZONE})
    (made / "SETTINGS.md").write_text("---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n",
                                      encoding="utf-8")
    return made


def sectors(bench, declared) -> None:
    """The latch learns its sector; a named sector serves its declarant alone."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = _probe(bench, declared, "sectors", "probe.yaml")
    registry = events.sectors(made)
    default_latch = events.push(made, "probe", "bare", vector="zone:atelier")
    own_latch = events.push(made, "probe", "sectored", vector="zone:forge")
    if (registry.get("probe", {}).get("source") == "probe" and registry["probe"].get("cap") == 1
            and default_latch is not None and default_latch["sector"] == "protocol"
            and own_latch is not None and own_latch["sector"] == "probe"):
        held("the latch learns its sector", "a signal without `sector:` falls to the declared default -- "
             "the engine's `protocol` when no package declares one; one naming its own sector carries it")
    else:
        failures.append(f"  ✗ sector field                {registry} {default_latch}/{own_latch}")
    expect("sector-unowned", lambda: events.push(made, "probe", "astray"))
    vendor(made, "rival", declared["rival.yaml"], {})
    expect("sector-collision", lambda: events.sectors(made))
    expect("sector-collision", lambda: events.push(made, "probe", "bare", vector="zone:atelier"))
    expect("sector-collision", lambda: events.standing(made, [dict(own_latch)]))
    _rewrite(made, "rival", declared["rival.foreign.yaml"])
    expect("sector-unowned", lambda: events.push(made, "rival", "echo"))
    if events.standing(made, [dict(own_latch)]):
        held("a named sector serves its declarant alone", "the collision refuses the registry read, push "
             "and standing alike; resolved, the foreign claim still refuses while the owner's latch stands")
    else:
        failures.append("  ✗ sector ownership            the owner's latch fell")


def arbitration(bench, declared) -> None:
    """The bus ranks the latches and serves each sector under its own cap."""
    held, failures = bench.held, bench.failures
    made = _probe(bench, declared, "arbitration", "probe.arbitration.yaml")
    l_one = events.push(made, "probe", "arbone", vector="zone:a")
    l_two = events.push(made, "probe", "arbtwo", vector="zone:b")
    l_gamma = events.push(made, "probe", "gamma", vector="zone:c")
    l_delta = events.push(made, "probe", "delta", vector="zone:d")
    l_in = events.push(made, "probe", "inhouse", vector="zone:e")
    l_in2 = events.push(made, "probe", "inhouse2", vector="zone:f")
    l_broad = events.push(made, "probe", "broad", vector="zone:g")
    names = lambda served: [one["signal"] for one in served]                  # noqa: E731
    full = events.emitted(made, [l_gamma, l_two, l_one], setting_cap=2)
    risen = events.emitted(made, [l_gamma, l_two], setting_cap=2)
    tied = events.emitted(made, [l_delta, {**l_gamma, "n": 3}], setting_cap=2)
    if (names(full) == ["arbone", "arbtwo"] and names(risen) == ["arbtwo", "gamma"]
            and names(tied) == ["gamma", "delta"]):
        held("the arbitration ranks and caps", "priority first, the count breaks the tie, the overflow "
             "waits and rises as a place frees")
    else:
        failures.append(f"  ✗ arbitration order           {names(full)} {names(risen)} {names(tied)}")
    muted = events.emitted(made, [l_one, l_in], setting_cap=0)
    capped = events.emitted(made, [l_in2, l_in], setting_cap=2)
    wide = events.emitted(made, [l_broad, {**l_broad, "vector": "zone:h"}], setting_cap=0)
    order = events.emitted(made, [l_in, l_one], setting_cap=2)
    if names(muted) == ["inhouse"] and names(capped) == ["inhouse"] and len(wide) == 2 \
            and names(order) == ["arbone", "inhouse"]:
        held("each sector under its own cap", "0 mutes the default sector alone; a declared cap holds its "
             "sector; an unsaid one serves 2; the default sector leads the order")
    else:
        failures.append(f"  ✗ sector caps                 {names(muted)} {names(capped)} {len(wide)} {names(order)}")


def scenario(bench) -> int:
    found, declared = demonstrated(DRAWER, PATTERN), manifests(DRAWER, PATTERN)
    if found != sorted(DEMOS) or sorted(declared) != sorted(MANIFESTS):
        bench.failures.append(f"  ✗ the demonstration           {found!r} {sorted(declared)!r} -- owed "
                              f"{sorted(DEMOS)!r} {sorted(MANIFESTS)!r}")
        return 0
    bus(bench, declared)
    families(bench, declared)
    gesture(bench, declared)
    sectors(bench, declared)
    arbitration(bench, declared)
    return 0
