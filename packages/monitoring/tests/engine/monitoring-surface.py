"""Scenario `monitoring-surface` -- what monitoring adds to an instance, what it wires and what
its removal gives back, on ONE house: the kit alone, then `add`, then `remove` -- 6 case(s):
- the kit alone carries no file, no catalogue line and no setting of monitoring
- adding the package puts its declared surface there -- the composed SETTINGS carries
  `monitoring_capture` VALUED, without one body line documenting it (the non-public switch)
- wire writes .claude/settings.json with the Stop hook alone; wired again it touches
  NOTHING, prints the snippet and says the skip; provider-unknown refuses
- the stamp is gated at the SKILL: silent (rc 0, no line) while the switch is false, and
  the engine's turn-end line lands once it is true -- the wired hook never changes
- the console resolves `./pp monitoring-stamp` as the package's command; the kit alone
  knows no such verb
- removing the package gives that surface back entire -- the record monitoring.json STAYS:
  it is the instance's data, born at the first setup
"""
from __future__ import annotations

from pathlib import Path

from conductor import compiling
from conductor.packaging import contributions, install
from conductor.state import instance


def _surface(meta: Path) -> dict:
    def lines(name: str) -> set[str]:
        path = meta / name
        return set(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else set()
    records = meta / ".sys" / "records"
    return {"files": {str(p.relative_to(meta)) for p in meta.rglob("*")
                      if p.is_file() and ".sys/state" not in str(p.relative_to(meta))
                      and "__pycache__" not in p.parts},
            "catalogue": lines(".sys/tools.md"),
            "laws": set(compiling.render_registry(meta).splitlines()),   # derived --
            "settings": lines("SETTINGS.md"),                            # no registry file
            "records": {p.name for p in records.glob("*")} if records.is_dir() else set()}


def _stamps(made: Path) -> int:
    return sum(1 for trace in (made / instance.STATE).glob("session-*.jsonl")
               for line in trace.read_text(encoding="utf-8").splitlines()
               if '"turn-end"' in line)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("monitoring-surface")
    made = env.made
    settings_json = env.root / ".claude" / "settings.json"

    # --- the kit alone -----------------------------------------------------------------
    absent = _surface(made)
    missing = env.cli("monitoring-stamp")
    if (not any("monitoring" in one for one in absent["files"])
            and not any("monitoring" in one for one in absent["catalogue"] | absent["settings"])):
        held("the kit alone knows no monitoring", "no file, no catalogue line, no setting names it")
    else:
        failures.append(f"  ✗ kit alone                   {sorted(absent['files'])[:3]}")

    # --- add ---------------------------------------------------------------------------
    install.add_package(env.member, "monitoring")
    present = _surface(made)
    added = {key: present[key] - absent[key] for key in absent}
    text = env.read("SETTINGS.md")
    front, body = text[4:text.find("\n---", 4)], text[text.find("\n---", 4):]
    if (added["files"] and all("monitoring" in one for one in added["files"])
            and added["settings"] and not added["records"]
            and "monitoring_capture: false" in front
            and "monitoring_capture" not in body):
        held("adding it puts its surface there, the switch valued and undocumented",
             f"{len(added['files'])} files, {len(added['settings'])} settings lines, 0 record; "
             "monitoring_capture: false in the front matter, not one body line about it")
    else:
        failures.append(f"  ✗ the added surface           {[(k, len(v)) for k, v in added.items()]} "
                        f"documented={'monitoring_capture' in body}")

    # --- wire: born once, never overwritten, unknown refused ----------------------------
    rc, _, _ = contributions.run_skill(made, "pp-monitoring", ["wire", "claude"])
    written = settings_json.read_text(encoding="utf-8") if settings_json.is_file() else ""
    rc2, out2, _ = contributions.run_skill(made, "pp-monitoring", ["wire", "claude"])
    after = settings_json.read_text(encoding="utf-8")
    rc3, _, err3 = contributions.run_skill(made, "pp-monitoring", ["wire", "codex"])
    if (rc == 0 and '"Stop"' in written and "./pp monitoring-stamp" in written
            and rc2 == 0 and after == written and "skipped" in out2 and "./pp monitoring-stamp" in out2
            and rc3 == 2 and "provider-unknown" in err3):
        held("wire writes once and never overwrites",
             "the hook born on the bare workspace; the second wire prints the snippet "
             "and skips; codex refuses by name")
    else:
        failures.append(f"  ✗ wire                       rc={rc}/{rc2}/{rc3} same={after == written}")

    # --- the stamp gated at the skill ---------------------------------------------------
    env.cli("-new")                                       # a run, so a trace exists
    rc4, _, _ = contributions.run_skill(made, "pp-monitoring", ["stamp"])
    silent = _stamps(made)
    env.write("SETTINGS.md", env.read("SETTINGS.md")
              .replace("monitoring_capture: false", "monitoring_capture: true"))
    rc5, _, _ = contributions.run_skill(made, "pp-monitoring", ["stamp"])
    armed = _stamps(made)
    if rc4 == 0 and silent == 0 and rc5 == 0 and armed == 1:
        held("the switch interrupts at the skill",
             "stamp silent and lineless while false; one turn-end line once true")
    else:
        failures.append(f"  ✗ gated stamp                rc={rc4}/{rc5} lines={silent}/{armed}")

    # --- the console command, present with the package, absent on the kit alone ---------
    con = env.cli("monitoring-stamp")
    if con.returncode == 0 and _stamps(made) == 2 and missing.returncode != 0:
        held("the console resolves the package's command",
             "./pp monitoring-stamp lands a second line; the kit-only console knows no such verb")
    else:
        failures.append(f"  ✗ console command            rc={con.returncode}/{missing.returncode} "
                        f"lines={_stamps(made)}")

    # --- remove: the record is born at the first setup, then the package leaves ----------
    script = env.root / "playbook.md"
    script.write_text("composition: kit\n\n## S1\n\n| id | gesture | expected |\n"
                      "|---|---|---|\n| S1.01 | S1.01 hello | -- |\n", encoding="utf-8")
    contributions.run_skill(made, "pp-monitoring", ["setup", "temoin", str(made), str(script)])
    install.remove_package(env.member, "monitoring")
    after_removal = _surface(made)
    given_back = {key: present[key] - after_removal[key] for key in absent}
    if (given_back["files"] == added["files"]
            and given_back["catalogue"] == added["catalogue"]
            and "monitoring.json" in after_removal["records"]):
        held("the removal gives back what the add put", "files and catalogue exactly; the "
             "record STAYS -- the instance's own data, born at the first setup")
    else:
        failures.append(f"  ✗ the removal                 back={[(k, len(v)) for k, v in given_back.items()]} "
                        f"records={sorted(after_removal['records'])}")
    return len(failures)
