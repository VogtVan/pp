"""Scenario `installer` -- `install.sh` as a user plays it, on a throwaway source, HOME and PATH:
- without uv: the installer plays uv's installer (its witness, `PP_UV_INSTALLER`), finds uv in
  `~/.local/bin`, installs the house beside the source, writes the post's launcher beside the house
- played again: the house only gets `upgrade --from <source>` -- no `-install`, a file of the house kept
- a source extracted elsewhere: the house's manifest names it after the next play
- piped (`sh < install.sh`, the one-command way): the archive `PP_ARCHIVE` names is extracted as `pp/`
  in the current folder, then installed; played again, the `pp/` is replaced, the house kept
- two houses in one folder: `house` keeps `pp-ui`, another gets `pp-ui-<name>`
- nothing written under the HOME but uv's own folder
The source is the witness source reduced to what an install reads, `install.sh` copied from the product.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from conductor import instance
from tests.harness import SOURCE

SHIPPED = ("engine", "bases", "packages", "template", "adapters", "pyproject.toml")
BARE_PATH = "/usr/bin:/bin"                  # a PATH without uv (`/usr/local/bin` holds it here)


def _source(bench, at: Path) -> Path:
    """-> a copy of the witness source holding what an install reads, `install.sh` beside it."""
    root = bench.source()
    for name in SHIPPED:
        found = root / name
        if found.is_dir():
            shutil.copytree(found, at / name, ignore=shutil.ignore_patterns("__pycache__", "tests"))
        elif found.is_file():
            shutil.copy2(found, at / name)
    if (SOURCE / "install.sh").is_file():
        shutil.copy2(SOURCE / "install.sh", at / "install.sh")
    return at


def _uv_witness(at: Path, log: Path) -> Path:
    """-> uv's installer stand-in: it writes `~/.local/bin/uv`, which logs its arguments and plays the real uv."""
    real = shutil.which("uv")
    script = at / "uv-installer.sh"
    script.write_text(
        "#!/bin/sh\nmkdir -p \"$HOME/.local/bin\"\n"
        "cat > \"$HOME/.local/bin/uv\" <<EOF\n#!/bin/sh\necho \"\\$*\" >> " + str(log) + "\n"
        "exec " + str(real) + " \"\\$@\"\nEOF\nchmod +x \"$HOME/.local/bin/uv\"\n", encoding="utf-8")
    return script


def _play(script: Path | None, cwd: Path, home: Path, env: dict, *args: str, piped: Path | None = None):
    """`sh install.sh <args>`, or `sh -s -- <args> < install.sh` when `piped` names the script."""
    full = {**os.environ, **env, "HOME": str(home), "PATH": BARE_PATH}
    if piped is not None:
        with piped.open("rb") as stdin:
            return subprocess.run(["sh", "-s", "--", *args], cwd=cwd, env=full, stdin=stdin,
                                  capture_output=True, text=True, timeout=120)
    return subprocess.run(["sh", str(script), *args], cwd=cwd, env=full, stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=120)


def _logged(log: Path) -> list[str]:
    return log.read_text(encoding="utf-8").splitlines() if log.is_file() else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    depot = bench.temp()
    home = depot / "home"
    home.mkdir()
    before = sorted(one.name for one in home.iterdir())
    log = depot / "uv.log"
    env = {"PP_UV_INSTALLER": str(_uv_witness(depot, log))}
    flags = ("--packages", "agent team ui", "--no-launch")

    # --- without uv: uv's installer played, the house installed, its launcher written ----------------
    place = depot / "place"
    source = _source(bench, place / "pp")
    house = place / "house"
    first = _play(source / "install.sh", place, home, env, *flags)
    calls = _logged(log)
    launcher = place / "pp-ui"
    if (first.returncode == 0 and (home / ".local" / "bin" / "uv").is_file() and instance.is_instance(house / ".pp")
            and any("-install" in one for one in calls) and launcher.is_file() and os.access(launcher, os.X_OK)
            and (place / "pp-ui.cmd").is_file()):
        held("without uv, a house and its launcher", "uv's installer played, uv found in ~/.local/bin, "
             "the house installed beside the source, pp-ui and pp-ui.cmd beside the house")
    else:
        failures.append(f"  ✗ first play                  rc={first.returncode} {calls} {first.stderr[-600:]!r}")

    # --- played again: upgrade --from alone, the house kept ---------------------------------------------
    kept = house / "mine.txt"
    if house.is_dir():
        kept.write_text("the operator's own\n", encoding="utf-8")
    seen = len(_logged(log))
    second = _play(source / "install.sh", place, home, env, *flags)
    again = _logged(log)[seen:]
    if (second.returncode == 0 and kept.is_file() and not any("-install" in one for one in again)
            and any("upgrade --from" in one for one in again)
            and instance.read(house / ".pp").get("source") == str(source)):
        held("played again, nothing destroyed", "the house got `upgrade --from <source>` alone, no -install, "
             "the operator's file kept")
    else:
        failures.append(f"  ✗ second play                 rc={second.returncode} {again} {second.stderr[-600:]!r}")

    # --- a source elsewhere: the house follows it -------------------------------------------------------
    moved = _source(bench, depot / "moved" / "pp-main")
    third = _play(moved / "install.sh", depot / "moved", home, env, "--house", str(house), *flags)
    if third.returncode == 0 and instance.read(house / ".pp").get("source") == str(moved) and kept.is_file():
        held("a source elsewhere is followed", "`--house` names the house, its manifest names the new source")
    else:
        failures.append(f"  ✗ moved source                rc={third.returncode} "
                        f"{instance.read(house / '.pp').get('source')} {third.stderr[-400:]!r}")

    # --- piped: the archive extracted as pp/, then played again -----------------------------------------
    archive = depot / "main.zip"
    with zipfile.ZipFile(archive, "w") as made:
        for path in sorted(moved.rglob("*")):
            if path.is_file():
                made.write(path, Path("pp-main") / path.relative_to(moved))
    fresh = depot / "fresh"
    fresh.mkdir()
    piped_env = {**env, "PP_ARCHIVE": str(archive)}
    script = moved / "install.sh"
    fourth = _play(None, fresh, home, piped_env, *flags, piped=script)
    stale = fresh / "pp" / "stale.txt"
    if fourth.returncode == 0:
        stale.write_text("left by the archive before\n", encoding="utf-8")
        (fresh / "house" / "mine.txt").write_text("the operator's own\n", encoding="utf-8")
    fifth = _play(None, fresh, home, piped_env, *flags, piped=script)
    if (fourth.returncode == 0 and fifth.returncode == 0 and (fresh / "pp" / "engine" / "pp.py").is_file()
            and not stale.exists() and (fresh / "house" / "mine.txt").is_file()
            and instance.read(fresh / "house" / ".pp").get("source") == str(fresh / "pp")):
        held("piped, the archive becomes pp/", "extracted beside the house, replaced at the next play, the house kept")
    else:
        failures.append(f"  ✗ piped                       rc={fourth.returncode}/{fifth.returncode} "
                        f"{fourth.stderr[-400:]!r} {fifth.stderr[-400:]!r}")

    # --- two houses in one folder: each its own launcher ---------------------------------------------
    neighbour = place / "house2"
    sixth = _play(source / "install.sh", place, home, env, "--house", str(neighbour), *flags)
    own = place / "pp-ui-house2"
    pointed = {one.name: one.read_text(encoding="utf-8") for one in (launcher, own) if one.is_file()}
    if (sixth.returncode == 0 and instance.is_instance(neighbour / ".pp") and own.is_file()
            and (place / "pp-ui-house2.cmd").is_file() and "/house/pp" in pointed.get("pp-ui", "")
            and "/house2/pp" in pointed.get("pp-ui-house2", "")):
        held("two houses in one folder, two launchers", "`house` keeps pp-ui, `house2` gets pp-ui-house2 "
             "and pp-ui-house2.cmd, each naming its own house")
    else:
        failures.append(f"  ✗ neighbour houses            rc={sixth.returncode} {sorted(pointed)} "
                        f"{sixth.stderr[-400:]!r}")

    # --- the HOME: uv's folder alone ----------------------------------------------------------------------
    after = sorted(one.name for one in home.iterdir())
    if before == [] and after == [".local"]:
        held("nothing under the HOME but uv's folder", "~ held nothing before, `.local` alone after six plays")
    else:
        failures.append(f"  ✗ home                        {before} -> {after}")
    return 0
