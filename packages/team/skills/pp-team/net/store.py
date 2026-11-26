"""The `net` domain, layer `store`: where the net reads the system.

A definition belongs here when it reaches the system for the net: it reads how long a verb waits for the house's locks
and takes the relaunch lock, reads which scheduler the system
plays and in which WSL distribution, builds the command a restart runs, gives the arguments that start a process
apart from its caller, or asks Windows whether a process is alive. What it reads, it gives back; a judgement that needs
no system belongs to a rule, and what chains a read and a judgement -- the teams that need their net, the relaunch
line -- belongs to `net/acts.py`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from house.store import engine_of, house_console, locks
from net.model import (CREATE_NEW_PROCESS_GROUP, CREATE_NO_WINDOW, ERROR_ACCESS_DENIED,
                       PROCESS_QUERY_LIMITED_INFORMATION, RELAUNCH_LOCK, SCHEDULER, STILL_ACTIVE, WSL_DISTRO)


def call_wait(root: Path, conductor) -> float:
    """-> `call_lock_wait` as the house's SETTINGS say it, 30 s without them: how long a verb
    waits for one of the house's locks."""
    try:
        return float(conductor.settings.of(root).call_lock_wait)
    except (AttributeError, TypeError, ValueError):
        return 30.0


def relaunch_held(root: Path, conductor):
    """-> the lease on the house's RELAUNCH lock (`state/relaunch.lock`), waited for within `call_lock_wait` -- the
    entry is laid, judged and removed under it, so that the stop of one team and the start of another at once never
    take the net of the team in need --, or None past the bound."""
    return locks(conductor).acquire(root / ".sys" / "state" / RELAUNCH_LOCK, wait=call_wait(root, conductor))


def scheduler(system: str | None = None) -> str:
    """-> the façade that holds the relaunch entry: `nt` (the user's Run key) or `posix` (the user's crontab) -- the
    system given, else `PP_SCHEDULER` (the bench plays both façades on one machine), else the system this process runs
    on."""
    return system or os.environ.get(SCHEDULER) or ("nt" if os.name == "nt" else "posix")


def run_command(root: Path, conductor) -> str:
    """-> what the Run key plays at logon: `uvw run <engine> --instance <house> team tick --all --entry` -- uv's
    launcher without a window -- when `uvw` is found, else the house's console by its absolute path."""
    windowless = shutil.which("uvw")
    if windowless:
        return f'"{windowless}" run "{engine_of(root, conductor)}" --instance "{root}" team tick --all --entry'
    return f'"{house_console(root, conductor)}" team tick --all --entry'


def wsl_distro(system: str | None = None) -> str:
    """-> the WSL distribution this process runs in under the posix façade (`WSL_DISTRO_NAME`), '' elsewhere: where
    the Run key's value must start the distribution at logon, cron playing `@reboot` only once it runs."""
    return os.environ.get(WSL_DISTRO, "") if scheduler(system) == "posix" else ""


def wsl_command(root: Path, conductor, distro: str) -> str:
    """-> what the Run key plays at logon under WSL: `wsl.exe -d <distro> --exec <python> <engine> --instance <house>
    team tick --all --entry`, the paths absolute -- the tick played by the distribution it starts, cron or not."""
    return subprocess.list2cmdline(["wsl.exe", "-d", distro, "--exec", sys.executable, str(engine_of(root, conductor)),
                                    "--instance", str(root), "team", "tick", "--all", "--entry"])


def asked_alive(pid: int) -> bool:
    """-> whether Windows says the process `pid` runs: `OpenProcess` for its exit code alone, then
    `GetExitCodeProcess` -- `STILL_ACTIVE` while it runs. A process the system refuses to open (another
    user's) runs; one it cannot find has ended."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    handle = kernel.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ctypes.get_last_error() == ERROR_ACCESS_DENIED
    try:
        code = wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle, ctypes.byref(code)):
            return False
        return code.value == STILL_ACTIVE
    finally:
        kernel.CloseHandle(handle)


def apart(system: str = os.name) -> dict:
    """-> the arguments that start a process detached from the caller: under Windows a console of its own that
    no window shows, in a process group of its own -- closing the operator's window ends nothing; elsewhere a
    session of its own, its group, which `ended_now` ends whole."""
    if system == "nt":
        return {"creationflags": CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP}
    return {"start_new_session": True}
