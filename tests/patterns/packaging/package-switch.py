"""Scenario `package-switch` -- the pattern `packaging/package-switch`, played from its demonstration:
- `package.<name>: off` at SETTINGS: the package leaves the play with every package requiring it, its
  cause said; a package that names it under `optional:` stays; the base never switches and a value
  other than on/off refuses `settings-invalid`, the face restoring the bytes
- off is not gone: the pins, the vendored bundles and the settings sections stand; the key is
  seeded `on` per pin beyond the base, under its own group, and the sync follows the pins keeping the
  operator's `off`
- a switched package leaves the catalog: no entry for its skill, no format; `on` again renders the
  catalog byte for byte
- `-disable` / `-enable` switch a package for ONE run: the slot written, the standing block answered,
  what is off does not play, another run plays everything; the base, an unpinned name and a package
  in flight refuse and write nothing
- the state line rides every output, dependencies first, the cause said; with no run standing the
  keyless view says the durable state, an instance with nothing beyond its base says nothing
- under the principal's conduction `-disable` writes the same slot and says the same state
The skill the package carries is written at the test's time.
"""
from __future__ import annotations

import json

from conductor import compiling, install, instance, settings
from tests.harness import PRINCIPAL, cli, closing, demonstrated, demos, fragments, manifests, support

DRAWER, PATTERN = "packaging", "package-switch"
DEMOS = ("ALPHA.md", "BETA.md")
MANIFESTS = ("alpha.yaml", "beta.yaml", "gamma.yaml")
FRAGMENTS = ("alpha.md",)
SKILL = "import sys\nprint('alpha:', *sys.argv[1:])\n"
packaging = support(__file__, "source")


def _doc(name: str) -> str:
    return (demos(DRAWER, PATTERN) / name).read_text(encoding="utf-8")


def _root(bench, declared, given):
    return packaging.source(bench, {
        "alpha": {"manifest": declared["alpha.yaml"], "procs": {"ALPHA": _doc("ALPHA.md")},
                  "fragment": given["alpha.md"], "skills": {"pp-alpha": SKILL}},
        "beta": {"manifest": declared["beta.yaml"], "procs": {"BETA": _doc("BETA.md")}},
        "gamma": {"manifest": declared["gamma.yaml"]}})


def _names(made) -> list[str]:
    return [root.name.split("@")[0] for root in instance.vendored(made)]


def _front(made) -> str:
    return (made / settings.DOCUMENT).read_text(encoding="utf-8").split("\n---", 1)[0]


def at_settings(bench, root) -> None:
    """The durable switch, read by every reader of the composition."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made, member = packaging.installed(bench, root, "switched", ["beta", "gamma"])
    front = _front(made)
    if ("# ---- packages ----" in front and all(f"package.{one}: on" in front for one in ("alpha", "beta", "gamma"))
            and "package.kit" not in front and settings.of(made).switches == ()
            and front.index("# ---- packages ----") < front.index("# ---- alpha ----")):
        held("the key is seeded", "`package.<name>: on` per pin beyond the base under `# ---- packages ----`, "
             "before the packages' own sections; none for the base")
    else:
        failures.append(f"  ✗ seeded                       {front[-300:]!r}")

    def stamp():
        return (instance.pins(made), sorted(p.name for p in (made / instance.VENDOR).iterdir()),
                (made / settings.DOCUMENT).read_text(encoding="utf-8"))

    before, whole = stamp(), _names(made)
    settings.write(made, "package.alpha", "off")
    after = stamp()
    if (whole == ["kit", "gamma", "alpha", "beta"] and _names(made) == ["kit", "gamma"]
            and instance.switched_off(made) == {"alpha": "alpha", "beta": "alpha"}):
        held("a switched package leaves with its dependents", "alpha off: beta off (<- alpha), gamma -- "
             "optional on alpha -- plays on")
    else:
        failures.append(f"  ✗ hard switch                  {whole} -> {_names(made)} {instance.switched_off(made)}")
    if (before[:2] == after[:2]
            and after[2].replace("package.alpha: off", "package.alpha: on") == before[2]):
        held("off is not gone", "the pins, the vendored bundles and the settings sections stand byte "
             "for byte; one line moved")
    else:
        failures.append(f"  ✗ off is not gone             {after[:2]}")
    kept = (made / settings.DOCUMENT).read_bytes()
    expect("settings-invalid", lambda: settings.write(made, "package.kit", "off"))
    expect("settings-invalid", lambda: settings.write(made, "package.beta", "maybe"))
    if (made / settings.DOCUMENT).read_bytes() == kept:
        held("a refused switch leaves the bytes", "the base off, a value neither on nor off: SETTINGS.md identical")
    else:
        failures.append("  ✗ refused switch               the file moved")

    install.remove_package(member, "beta")
    removed = _front(made)
    install.add_package(member, "beta")
    added = _front(made)
    if ("package.beta" not in removed and "package.alpha: off" in removed
            and "package.beta: on" in added and "package.alpha: off" in added
            and settings.of(made).switches == ("alpha",)):
        held("the sync follows the pins", "remove drops `package.beta`, add seeds it `on` again, the "
             "operator's `package.alpha: off` travels untouched")
    else:
        failures.append(f"  ✗ sync                         {removed[-160:]!r} {added[-160:]!r}")


def in_catalog(bench, root) -> None:
    """What plays is what the catalog says."""
    held, failures = bench.held, bench.failures
    made, _ = packaging.installed(bench, root, "cataloged", ["beta"])
    lit, forms = compiling.render_tools(made), compiling.render_formats(made)
    settings.write(made, "package.alpha", "off")
    dark, dark_forms = compiling.render_tools(made), compiling.render_formats(made)
    if ("`pp-alpha`**" in lit and "- `pp-alpha`\n" not in lit and "`alpha-form`**" in forms
            and "pp-alpha" not in dark and "alpha-form" not in dark_forms):
        held("a switched package leaves the catalog", "alpha on: `pp-alpha` described, `alpha-form` "
             "listed; alpha off: neither, bare or described")
    else:
        failures.append(f"  ✗ catalog dark                 lit={'pp-alpha' in lit} dark={'pp-alpha' in dark}")
    settings.write(made, "package.alpha", "on")
    if compiling.render_tools(made) == lit and compiling.render_formats(made) == forms:
        held("on again renders byte for byte", "the catalog and the formats return as they were")
    else:
        failures.append("  ✗ catalog relit                the catalog moved after `on`")


def in_a_run(bench, root) -> None:
    """`-disable` and `-enable`, one run at a time."""
    held, failures = bench.held, bench.failures

    def witness(name: str):
        made, _ = packaging.installed(bench, root, name, ["beta", "gamma"])
        settings.write(made, "conduction_effort", "none")
        settings.write(made, "instructions_fusion", "none")
        return made, made / ".sys" / "engine" / "pp.py"

    made, engine = witness("run")

    def call(*args: str, home=None, machine=None, env=None):
        return cli(machine or engine, *args, cwd=(home or made).parent, env=env)

    def opened(home=None) -> str:
        newest = max(((home or made) / ".sys" / "state").glob("session-*.json"), key=lambda p: p.stat().st_mtime)
        return newest.stem[len("session-"):]

    def slot(key: str, home=None) -> dict:
        return json.loads(((home or made) / ".sys" / "state" / f"session-{key}.json").read_text(encoding="utf-8"))

    def walk(key: str, home=None, machine=None) -> str:
        seen = []
        for _ in range(12):
            answered = call(key, home=home, machine=machine)
            seen.append(answered.stdout)
            if closing(answered.stdout)[:1] == ["▶ AWAIT"] or answered.returncode:   # the closing, never a reading
                break
        return "".join(seen)

    def state(text: str) -> str:
        return next((one for one in text.splitlines() if one.startswith("▌ ") and " on" in one), "")

    def cells(text: str) -> list[str]:
        """-> the cells of the state line, one per pin beyond the base."""
        return state(text)[2:].split(" · ")

    call("-new")
    key = opened()
    standing = call(key, "-peek").stdout
    answered = call(key, "-disable", "beta")
    after = call(key, "-peek").stdout
    if (answered.returncode == 0 and slot(key).get("off") == ["beta"]
            and standing.splitlines()[2:] == after.splitlines()[2:]
            and after.splitlines()[2:] and after.splitlines()[2:] == answered.stdout.splitlines()[4:]):
        held("a disable writes the slot and answers the standing block", "`off: [beta]` at the slot, "
             "the same step standing before and after")
    else:
        failures.append(f"  ✗ disable                      rc={answered.returncode} off={slot(key).get('off')}")
    played = walk(key)
    if "▸ ALPHA" in played and "▸ BETA" not in played and "▶ AWAIT" in played:
        held("what is off does not play", "the turn's end played ALPHA and passed BETA by")
    else:
        failures.append(f"  ✗ the play                     alpha={'▸ ALPHA' in played} beta={'▸ BETA' in played}")
    if cells(standing) == ["gamma on", "alpha on", "beta on"] and cells(after) == ["gamma on", "alpha on", "beta off"] \
            and played.count(state(after)) >= 2:
        held("the state rides every output", f"{state(standing)!r} then {state(after)!r} on every output of the walk")
    else:
        failures.append(f"  ✗ the state line               {state(standing)!r} -> {state(after)!r}")

    call("-new")
    beside = opened()
    whole = walk(beside)
    if "▸ ALPHA" in whole and "▸ BETA" in whole and not slot(beside).get("off") and slot(key).get("off") == ["beta"]:
        held("the switch belongs to the run", "a run beside plays ALPHA and BETA; the first keeps beta off")
    else:
        failures.append(f"  ✗ per run                      off={slot(beside).get('off')}")
    call(beside, "-disable", "beta")
    lifted = call(beside, "-enable", "beta")
    call(beside, "the operator's word")
    again = walk(beside)
    if lifted.returncode == 0 and not slot(beside).get("off") \
            and "▸ BETA" in again:
        held("an enable brings the package back", "the slot carries no switch, the next turn's end plays BETA")
    else:
        failures.append(f"  ✗ enable                       off={slot(beside).get('off')} beta={'▸ BETA' in again}")
    caused = state(call(beside, "-disable", "alpha").stdout)
    if cells(caused) == ["gamma on", "alpha off", "beta off (<- alpha)"]:
        held("the cause is said", caused)
    else:
        failures.append(f"  ✗ the cause                    {caused!r}")

    kept = slot(key)
    base, unpinned = call(key, "-disable", "kit"), call(key, "-disable", "nope")
    flight_made, flight_engine = witness("in-flight")
    call("-new", home=flight_made, machine=flight_engine)
    flight_key = opened(flight_made)
    for _ in range(12):
        if "▸ ALPHA" in call(flight_key, home=flight_made, machine=flight_engine).stdout:
            break
    flight = call(flight_key, "-disable", "alpha", home=flight_made, machine=flight_engine)
    if (base.returncode and "package-base" in base.stderr and unpinned.returncode
            and "package-unpinned" in unpinned.stderr and flight.returncode
            and "package-in-flight" in flight.stderr and "ALPHA.md" in flight.stderr
            and slot(key) == kept and not slot(flight_key, flight_made).get("off")):
        held("the three refusals write nothing", "package-base, package-unpinned, package-in-flight "
             "(ALPHA.md named); both slots byte for byte")
    else:
        failures.append(f"  ✗ refusals                     {base.returncode}/{unpinned.returncode}/{flight.returncode}")

    call("-new", env={PRINCIPAL: "true"})
    led = opened()
    switched = call(led, "-disable", "beta", env={PRINCIPAL: "true"})
    if switched.returncode == 0 and slot(led).get("off") == ["beta"] and state(switched.stdout) == state(after):
        held("the principal's conduction switches the same", f"slot `off: [beta]`, {state(switched.stdout)!r}")
    else:
        failures.append(f"  ✗ principal                    rc={switched.returncode} off={slot(led).get('off')}")

    quiet_made, quiet_engine = witness("keyless")
    settings.write(quiet_made, "package.beta", "off")
    keyless = call(home=quiet_made, machine=quiet_engine)
    bare = bench.env("bare-of-packages").cli()
    if (keyless.returncode == 0 and cells(keyless.stdout) == ["gamma on", "alpha on", "beta off"]
            and bare.returncode == 0 and not any(one.startswith("▌ ") and " on" in one
                                                 for one in bare.stdout.splitlines())):
        held("the keyless view says the durable state", "no run standing: the line from SETTINGS alone; "
             "an instance with nothing beyond its base says nothing of packages")
    else:
        failures.append(f"  ✗ keyless                      {keyless.stdout[:200]!r}")


def scenario(bench) -> int:
    failures = bench.failures
    found, declared, given = demonstrated(DRAWER, PATTERN), manifests(DRAWER, PATTERN), fragments(DRAWER, PATTERN)
    if found != sorted(DEMOS) or sorted(declared) != sorted(MANIFESTS) or sorted(given) != sorted(FRAGMENTS):
        failures.append(f"  ✗ the demonstration           {found!r} {sorted(declared)!r} {sorted(given)!r} -- "
                        f"owed {sorted(DEMOS)!r} {sorted(MANIFESTS)!r} {sorted(FRAGMENTS)!r}")
        return 0
    root = _root(bench, declared, given)
    at_settings(bench, root)
    in_catalog(bench, root)
    in_a_run(bench, root)
    return 0
