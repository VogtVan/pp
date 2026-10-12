"""Scenario `absence` -- what monitoring adds is exactly what its removal gives back
(plan pp-split, batch le-package-monitoring) -- 3 case(s):
- a kit-only instance carries no file, no catalogue line, no law and no setting of monitoring
- adding the package puts its declared surface there -- and the composed SETTINGS carries
  `monitoring_capture` VALUED, without one body line documenting it (the non-public switch)
- removing it gives that surface back entire -- the record monitoring.json STAYS: it is the
  instance's data, born at the first setup
"""
from __future__ import annotations

from pathlib import Path

from conductor import compiling, install
from conductor.packaging import contributions


def _surface(meta: Path) -> dict:
    def lines(name: str) -> set[str]:
        path = meta / name
        return set(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else set()
    records = (meta / ".sys" / "records")
    return {"files": {str(p.relative_to(meta)) for p in meta.rglob("*")
                      if p.is_file() and ".sys/state" not in str(p.relative_to(meta))
                      and "__pycache__" not in p.parts},
            "catalogue": lines(".sys/tools.md"),
            "laws": set(compiling.render_registry(meta).splitlines()),   # derived --
            "settings": lines("SETTINGS.md"),                            # no registry file
            "records": {p.name for p in records.glob("*")} if records.is_dir() else set()}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    bare = bench.env("bare-kit-mon")
    full = bench.env("with-monitoring", ("monitoring",))

    absent, present = _surface(bare.made), _surface(full.made)
    added = {key: present[key] - absent[key] for key in absent}

    if (not any("monitoring" in one for one in absent["files"])
            and not any("monitoring" in one for one in absent["catalogue"] | absent["settings"])):
        held("the kit alone knows no monitoring", "no file, no catalogue line, no setting names it")
    else:
        failures.append(f"  ✗ kit alone                   {sorted(absent['files'])[:3]}")

    text = (full.made / "SETTINGS.md").read_text(encoding="utf-8")
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

    # the record is born at the first setup -- then the removal
    script = full.made.parent / "playbook.md"
    script.write_text("composition: kit\n\n## S1\n\n| id | gesture | expected |\n"
                      "|---|---|---|\n| S1.01 | S1.01 hello | -- |\n", encoding="utf-8")
    contributions.run_skill(full.made, "pp-monitoring",
                            ["setup", "temoin", str(bare.made), str(script)])
    install.remove_package(full.member, "monitoring")
    after = _surface(full.made)
    given_back = {key: present[key] - after[key] for key in absent}
    if (given_back["files"] == added["files"]
            and given_back["catalogue"] == added["catalogue"]
            and "monitoring.json" in after["records"]):
        held("the removal gives back what the add put", "files and catalogue exactly; the "
             "record STAYS -- the instance's own data, born at the first setup")
    else:
        failures.append(f"  ✗ the removal                 back={[(k, len(v)) for k, v in given_back.items()]} "
                        f"records={sorted(after['records'])}")
    return len(failures)
