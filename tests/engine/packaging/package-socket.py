"""Scenario `package-socket` -- a package's socket, named by its own documents and by another's:
- the qualified address: a proc of a package hooks `<proc>.<hook>`; a mount or an attach names
  it `<pkg>.<proc>.<hook>` and the build accepts it -- the build's orphan check qualifies the
  hooks as the run does; the bare two-segment form names the base, which hooks no such socket,
  and a qualified address no proc hooks is an orphan too: both refused by name
- the optional socket: a package names the packages it may USE when they are there under
  `optional:`; a document of it that mounts at a socket of an optional package plays when the
  package is in the composition and SLEEPS when it is not -- the build warns `mount-dormant`,
  refuses nothing; a socket the present package declares nowhere refuses, a socket of a package
  neither required nor optional refuses `dependency-undeclared`, and the optional package
  switched off for the run leaves the client `on`
"""
from __future__ import annotations

import re

from conductor import instance
from conductor.packaging import compiling

OPENER = """name: {name}
version: 0.0.1
description: a package that opens a socket of its own at the turn's end
requires: [kit]
contributes:
  sockets: [thr.begin]
"""
THR = """---
name: THR
kind: proc
description: the pass of the package -- after the work, it hooks its own socket
attach: turn.end
proc: |
  HOOK thr.begin
  WORK
---

THR: the pass.
"""
STAMP = """---
name: STAMP
kind: doc
description: a reading mounted on the pass's socket
mount: {socket}
---

STAMP rides the pass.
"""
CLIENT = """name: client
version: 0.0.1
description: a package that rides the socket of another when that one is there
requires: [kit]
{optional}"""


def _pin(made, name: str, manifest: str, procs: dict[str, str]) -> None:
    """A package forged in the vendor space and pinned: its manifest and its procs."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    (root / "procs").mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for stem, text in procs.items():
        (root / "procs" / f"{stem}.md").write_text(text, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


def qualified_address(bench) -> None:
    """One package opens the socket and mounts on it; the mount's address is repinned
    between builds on one house."""
    held, failures = bench.held, bench.failures
    env = bench.env("socket")
    cases = (("witness.thr.begin", 0, ""),
             ("thr.begin", 2, "attach-unhooked"),
             ("witness.gone.begin", 2, "attach-unhooked"))
    for socket, rc, code in cases:
        _pin(env.made, "witness", OPENER.format(name="witness"),
             {"THR": THR, "STAMP": STAMP.format(socket=socket)})
        built = env.cli("-build")
        if built.returncode == rc and code in built.stderr:
            held(f"mount `{socket}`", "accepted: the pass's socket, qualified by its package"
                 if rc == 0 else f"refused {code}")
        else:
            failures.append(f"  ✗ mount {socket:<22} rc={built.returncode} {built.stderr.strip()[-160:]!r}")


def optional_socket(bench) -> None:
    """The client mounts at the socket of `absent`; one house, the client repinned and
    `absent` added between builds."""
    held, failures = bench.held, bench.failures
    env = bench.env("optional-socket")

    def client(socket: str, optional: bool) -> None:
        _pin(env.made, "client", CLIENT.format(optional="optional: [absent]\n" if optional else ""),
             {"STAMP": STAMP.format(socket=socket)})

    # --- the optional package absent: dormant, not refused ---------------------------------
    client("absent.thr.begin", optional=True)
    built = env.cli("-build")
    dormant = [one for one in (compiling.lint(env.made) if built.returncode == 0 else [])
               if one.startswith("mount-dormant")]
    if built.returncode == 0 and dormant and "STAMP" in dormant[0] and "absent" in dormant[0]:
        held("optional absent: dormant", dormant[0])
    else:
        failures.append(f"  ✗ optional absent: rc={built.returncode} {built.stderr.strip()[-160:]!r} "
                        f"dormant={dormant}")

    # --- the optional package present: the socket plays, nothing dormant -------------------
    _pin(env.made, "absent", OPENER.format(name="absent"), {"THR": THR})
    built = env.cli("-build")
    dormant = [one for one in (compiling.lint(env.made) if built.returncode == 0 else [])
               if "dormant" in one]
    if built.returncode == 0 and not dormant and "STAMP.md" in instance.mounting(env.made, "absent.thr.begin"):
        held("optional present: the socket plays", "built, STAMP mounted at absent.thr.begin, nothing dormant")
    else:
        failures.append(f"  ✗ optional present: rc={built.returncode} {built.stderr.strip()[-160:]!r} "
                        f"dormant={dormant}")

    # --- a socket the present package declares nowhere: refused ----------------------------
    client("absent.nowhere.begin", optional=True)
    built = env.cli("-build")
    if built.returncode == 2 and re.search(r"reference-unknown|attach-unhooked", built.stderr):
        held("unknown socket of a present package: refused", built.stderr.strip().splitlines()[-1][:120])
    else:
        failures.append(f"  ✗ unknown socket: rc={built.returncode} {built.stderr.strip()[-160:]!r}")

    # --- neither required nor optional: refused dependency-undeclared ----------------------
    client("absent.thr.begin", optional=False)
    built = env.cli("-build")
    if built.returncode == 2 and "dependency-undeclared" in built.stderr:
        held("neither required nor optional: refused", "dependency-undeclared")
    else:
        failures.append(f"  ✗ undeclared: rc={built.returncode} {built.stderr.strip()[-160:]!r}")

    # --- both pinned, the optional one switched off: the client stays on -------------------
    client("absent.thr.begin", optional=True)
    built = env.cli("-build")
    opened = env.cli("-new") if built.returncode == 0 else built
    found = re.search(r"run ([0-9a-f]{6})", opened.stdout or "")
    line = ""
    if found:
        switched = env.cli(found.group(1), "-disable", "absent")
        line = next((one for one in (switched.stdout or "").splitlines() if "absent off" in one), "")
    if line and "client on" in line:
        held("optional switched off: the client stays on", line.strip())
    else:
        failures.append(f"  ✗ optional off: rc={built.returncode} {built.stderr.strip()[-120:]!r} "
                        f"line={line!r}")


def scenario(bench) -> int:
    qualified_address(bench)
    optional_socket(bench)
    return 0
