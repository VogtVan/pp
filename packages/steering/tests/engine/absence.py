"""Scenario `absence` -- what steering adds is exactly what its removal gives back (plan
pp-split, batch le-temoin-de-steering) -- 3 case(s):
- a kit-only instance carries no file, no catalogue line, no law and no setting of steering
- adding the package puts its declared surface there, and nothing else
- removing it gives that surface back entire -- the RECORDS excepted: they are the
  instance's data, and `remove_package` says so in its own contract
"""
from __future__ import annotations

from pathlib import Path

from conductor import compiling, install


def _surface(meta: Path) -> dict:
    """The four surfaces a package may touch, plus its records -- read off the disk."""
    def lines(name: str) -> set[str]:
        path = meta / name
        return set(path.read_text(encoding="utf-8").splitlines()) if path.is_file() else set()
    records = (meta / ".sys" / "records")
    return {"files": {str(p.relative_to(meta)) for p in meta.rglob("*")
                      if p.is_file() and ".sys/state" not in str(p.relative_to(meta))
                      and "__pycache__" not in p.parts},
            "catalogue": lines(".sys/tools.md"),
            "laws": set(compiling.render_registry(meta).splitlines()),   # derived --
                                       # no registry file exists since le-registre-aux-codes
            "settings": lines("SETTINGS.md"),
            "records": {p.name for p in records.glob("*")} if records.is_dir() else set()}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    bare = bench.env("bare-kit")
    full = bench.env("with-steering", ("steering",))

    absent, present = _surface(bare.made), _surface(full.made)
    added = {key: present[key] - absent[key] for key in absent}

    if (not any("steering" in one for one in absent["files"])
            and not any("steering" in one for one in absent["catalogue"] | absent["settings"])):
        held("the kit alone knows no steering", "no file, no catalogue line, no setting names it")
    else:
        failures.append(f"  ✗ kit alone                   {sorted(absent['files'])[:3]}")

    if (added["files"] and all("steering" in one for one in added["files"])
            and added["catalogue"] and added["laws"] and added["settings"]
            and not added["records"]):
        held("adding it puts its surface there", f"{len(added['files'])} files, "
             f"{len(added['catalogue'])} catalogue lines, {len(added['laws'])} laws, "
             f"{len(added['settings'])} settings, 0 record -- records are born at the first call")
    else:
        failures.append(f"  ✗ the added surface           {[(k, len(v)) for k, v in added.items()]}")

    # a thread written, so the records exist -- then the removal
    full.cli("-new")
    threads = full.made / ".sys" / "records" / "threads.json"
    threads.parent.mkdir(parents=True, exist_ok=True)
    threads.write_text('{"un-fil": {"steps": [{"id": 1, "text": "le pas", "status": "open"}], '
                       '"next": 1, "last": 1}}', encoding="utf-8")
    install.remove_package(full.member, "steering")
    after = _surface(full.made)
    given_back = {key: present[key] - after[key] for key in absent}

    if (given_back["files"] == added["files"] and given_back["laws"] == added["laws"]
            and given_back["catalogue"] == added["catalogue"]
            and "threads.json" in after["records"]):
        held("the removal gives back what the add put", "files, catalogue and laws exactly; "
             "the records STAY -- the instance's own data")
    else:
        failures.append(f"  ✗ the removal                 back={[(k, len(v)) for k, v in given_back.items()]} "
                        f"records={sorted(after['records'])}")
    return len(failures)
