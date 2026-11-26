"""The `net` domain, layer `acts`: what the team does to the system to keep its net.

A definition belongs here when it plays an effect of several steps on the system for the net: it arms a team's timer on
the next deadline, spawns it, finds and ends it, arms another when a timer's tick failed, plays the timer's tick through
the house's console, tells whether a process is alive, or lays, judges, lays again and removes the house's relaunch
entry -- a line of the crontab, or a value of the Windows Run key, and the line itself (`reboot_line`). It also finds
the teams of the house that still need their net (`needing`), and composes the face of the net from what it reads of
the timer and the relaunch entry (`schedule_face`). What it writes to the journal -- `timer-armed`, the
owner's notice of a relaunch entry the system refused or of a timer's tick that failed -- is decided and composed by
`net/rules.py` from what the effect gave; the act plays the effect, then writes. The Windows code is here as it stood;
the bench of a machine that is not Windows does not play it. It may use the lower layers of any domain.

THE NET of a team is its TIMER, at every step of `schedule:` (`off` for none ever, 5 minutes unless
said, kept in seconds at `team-started.schedule`): the tick arms it when a deadline stands, the
step bounding its sleep. The timer dies with the machine; ONE RELAUNCH ENTRY per HOUSE plays
`team tick --all --entry` at the user's next logon -- one tick per team that needs its net -- and so arms the
timers again: the value `pp-team-<12 hex of the house>` of the user's Run key
(`HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run`) under Windows, written with no right the
user lacks; a line `@reboot <python> <engine> --instance <house> team tick --all --entry >/dev/null 2>&1
# pp-team <house>` in the user's crontab elsewhere, and under WSL (`WSL_DISTRO_NAME` set) the same value of the
Run key too, `wsl.exe -d <distro> --exec <python> <engine> --instance <house> team tick --all --entry`, written by
`reg.exe`:
Windows starts the distribution at logon -- or, under `PP_CRONTAB=<file>` and
`PP_RUNKEY=<file>`, those files (the bench, a try); `PP_SCHEDULER=nt|posix` names the façade. A
verb whose team needs its net -- a task open or a ceremony declared -- lays it after writing its
journal (`start`, a `post` that finds it gone); the tick at `schedule-off`, `stop` and `delete`
remove it only when NO team of the house needs it any more, judged and removed under
`state/relaunch.lock`. The system plays the entry with its own minimal PATH, where a harness's command is not found:
every lay keeps the PATH of the process that lays it at `state/relaunch.path`, written whole even when the entry
stands unchanged, and removed with the entry; `--entry` takes it up before any team advances, so the timers and the
launches inherit it -- an entry laid by an earlier version, without `--entry`, differs and is rewritten at the next
lay. An entry the system refuses is SAID -- stderr (`relaunch not laid`), a notice
of the team to the owner once per season, the face -- and the team starts: it runs on its timer.
"""
from __future__ import annotations

import json
import os
import re
import secrets
import shlex
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from house.model import TEAMS, TEAM_DOC
from house.rules import journal_of
from house.store import ENTRY, engine_of, locks, placed, tick_now
from declaration.model import TICK_LOCK
from wake.model import FOLLOW_LOG
from net.model import CRONTAB, RUNKEY, RUN_KEY, TIMER_ENV, TIMER_RETRIES, TIMER_RETRY, TIMER_TICKING
from season.rules import schedule_seconds
from wake.acts import ended_now
from net.rules import (kept_path, mark_of, marked, relaunch_notice, relaunch_notice_of, timer_armed_of,
                       timer_mark, timer_notice_of, value_name)
from net.store import apart, asked_alive, relaunch_held, run_command, scheduler, wsl_command, wsl_distro
from journal.store import appended, state_of
from tick.rules import deadline_of, netless


# --- the relaunch entry: the house's way back after a restart, ONE for all its teams ------------

def table_read() -> tuple[list[str], str]:
    """-> (the calendar's lines, '') -- the file `PP_CRONTAB` names when it is set (absent:
    empty), else the user's crontab (`crontab -l`; none yet: empty); or ([], why) when no
    table can be read."""
    given = os.environ.get(CRONTAB)
    if given:
        path = Path(given)
        if not path.is_file():
            return [], ""
        try:
            return path.read_text(encoding="utf-8").splitlines(), ""
        except OSError as why:
            return [], f"{given}: {why}"
    try:
        played = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    except OSError as why:
        return [], f"crontab: {why}"
    if played.returncode == 0:
        return played.stdout.splitlines(), ""
    if "no crontab" in (played.stderr or ""):
        return [], ""
    return [], (played.stderr or "").strip() or f"crontab -l rc {played.returncode}"


def table_write(lines: list[str]) -> str:
    """Replaces the calendar with these lines -- the `PP_CRONTAB` file, or `crontab -`.
    -> '' or why it could not be written."""
    text = "\n".join(lines) + ("\n" if lines else "")
    given = os.environ.get(CRONTAB)
    if given:
        try:
            Path(given).write_text(text, encoding="utf-8")
            return ""
        except OSError as why:
            return f"{given}: {why}"
    try:
        played = subprocess.run(["crontab", "-"], input=text, capture_output=True, text=True)
    except OSError as why:
        return f"crontab: {why}"
    return "" if played.returncode == 0 else ((played.stderr or "").strip() or f"crontab - rc {played.returncode}")


def reg_played(*args: str) -> tuple[str, str]:
    """-> (stdout, '') of `reg.exe <args>` -- Windows' own console on the registry, reached from WSL --, or ('', why)."""
    try:
        played = subprocess.run(["reg.exe", *args], capture_output=True, text=True, errors="replace")
    except OSError as why:
        return "", f"reg.exe: {why}"
    if played.returncode == 0:
        return played.stdout, ""
    return "", f"reg.exe: {(played.stderr or played.stdout or '').strip() or f'rc {played.returncode}'}"


def runkey_read() -> tuple[dict[str, str], str]:
    """-> ({value: command}, '') of the user's Run key -- the file `PP_RUNKEY` names when it is set (one line
    `<value>\t<command>` per value; absent: empty), else `RUN_KEY` under HKEY_CURRENT_USER by `winreg`, else by
    `reg.exe query` (WSL); or ({}, why)."""
    given = os.environ.get(RUNKEY)
    if given:
        path = Path(given)
        if not path.exists():
            return {}, ""
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as why:
            return {}, f"{given}: {why}"
        return dict(one.split("\t", 1) for one in lines if "\t" in one), ""
    try:
        import winreg
        found: dict[str, str] = {}
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            index = 0
            while True:
                try:
                    value, data, _ = winreg.EnumValue(key, index)
                except OSError:
                    return found, ""
                found[str(value)] = str(data)
                index += 1
    except ImportError:
        pass
    except OSError as why:
        return {}, f"Run key: {why}"
    said, why = reg_played("query", f"HKCU\\{RUN_KEY}")
    if why:
        return {}, why
    rows = (re.match(r"^ {4}(.+?) {4}REG_\w+ {4}(.*)$", one) for one in said.splitlines())
    return {row.group(1): row.group(2) for row in rows if row}, ""


def runkey_write(value: str, command: str | None) -> str:
    """Writes ONE value of the user's Run key -- `command` set, None removed -- in the `PP_RUNKEY` file, by `winreg`, or
    by `reg.exe add|delete` (WSL), under no right the user lacks. -> '' or why it could not be written."""
    given = os.environ.get(RUNKEY)
    if given:
        found, why = runkey_read()
        if why:
            return why
        found.pop(value, None)
        if command is not None:
            found[value] = command
        try:
            Path(given).write_text("".join(f"{one}\t{data}\n" for one, data in found.items()), encoding="utf-8")
            return ""
        except OSError as why:
            return f"{given}: {why}"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if command is None:
                winreg.DeleteValue(key, value)
            else:
                winreg.SetValueEx(key, value, 0, winreg.REG_SZ, command)
        return ""
    except FileNotFoundError:
        return ""
    except ImportError:
        pass
    except OSError as why:
        return f"Run key: {why}"
    if command is None:
        return reg_played("delete", f"HKCU\\{RUN_KEY}", "/v", value, "/f")[1]
    return reg_played("add", f"HKCU\\{RUN_KEY}", "/v", value, "/t", "REG_SZ", "/d", command, "/f")[1]


def runkey_laid(value: str, command: str) -> str:
    """Lays ONE value of the Run key when it differs. -> '' or why the system refused it."""
    found, why = runkey_read()
    if why:
        return why
    return "" if found.get(value) == command else runkey_write(value, command)


def runkey_removed(value: str) -> str:
    """Removes ONE value of the Run key when it stands. -> '' or why the system refused it."""
    found, why = runkey_read()
    return why or (runkey_write(value, None) if value in found else "")


def laid_now(root: Path, conductor, system: str | None = None) -> str:
    """Lays the house's entry, the relaunch lock held by the caller: the PATH of this process kept at
    `state/relaunch.path` at every lay, then the Run key's value when it differs, or the crontab with every line marked
    for the house replaced by its one line -- and under WSL the Run key's value that starts the distribution as well.
    -> '' or why the system refused it."""
    placed(kept_path(root), os.environ.get("PATH", "").encode("utf-8"))
    if scheduler(system) == "nt":
        return runkey_laid(value_name(root), run_command(root, conductor))
    lines, why = table_read()
    if not why:
        line = reboot_line(root, conductor)
        kept = [one for one in lines if not marked(one, root)]
        why = "" if [one for one in lines if marked(one, root)] == [line] else table_write(kept + [line])
    distro = wsl_distro(system)
    said = runkey_laid(value_name(root), wsl_command(root, conductor, distro)) if distro else ""
    return "; ".join(one for one in (why, said) if one)


def relaunch_laid(root: Path, conductor, system: str | None = None) -> str:
    """Lays the house's ONE relaunch entry under the relaunch lock -- after the verb wrote its journal. -> '' or why the
    system refused it."""
    lease = relaunch_held(root, conductor)
    if lease is None:
        return "the relaunch lock is busy"
    try:
        return laid_now(root, conductor, system)
    finally:
        locks(conductor).release(lease)


def relaunch_removed(root: Path, conductor, name: str, but: str | None = None, system: str | None = None) -> None:
    """Removes the house's relaunch entry when NO team of the house needs its net any more (`but` left out) -- judged
    and removed in one hold of the relaunch lock; a removal the system refuses is said on stderr, in the words of the
    team `name` whose verb tried it."""
    lease = relaunch_held(root, conductor)
    if lease is None:
        sys.stderr.write(f"pp-team: {name} · relaunch not removed -- the relaunch lock is busy\n")
        return
    try:
        if needing(root, but):
            return
        if scheduler(system) == "nt":
            why = runkey_removed(value_name(root))
        else:
            lines, why = table_read()
            kept = [one for one in lines if not marked(one, root)]
            if not why and len(kept) != len(lines):
                why = table_write(kept)
            said = runkey_removed(value_name(root)) if wsl_distro(system) else ""
            why = "; ".join(one for one in (why, said) if one)
        if why:
            sys.stderr.write(f"pp-team: {name} · relaunch not removed -- {why}\n")
        else:
            kept_path(root).unlink(missing_ok=True)        # the entry gone, the PATH it took up goes with it
    finally:
        locks(conductor).release(lease)


def relaunch_standing(root: Path, system: str | None = None) -> bool:
    """-> whether the house's relaunch entry stands: its value in the Run key, or its line in the crontab -- and under
    WSL its value in the Run key as well."""
    if scheduler(system) == "nt":
        return value_name(root) in runkey_read()[0]
    return (any(one.rstrip().endswith(mark_of(root)) for one in table_read()[0])
            and (not wsl_distro(system) or value_name(root) in runkey_read()[0]))


def relaunch_said(root: Path, conductor, name: str, journal: Path) -> None:
    """Lays the relaunch entry, and SAYS a refusal of the system without failing: on stderr, and ONCE per season as a
    notice of the team to the owner (`relaunch: true`, its `why`, no `about`: it holds no wait); the team runs on its
    timer meanwhile."""
    why = relaunch_laid(root, conductor)
    if not why:
        return
    sys.stderr.write(f"pp-team: {name} · relaunch not laid -- {why}\n")
    appended(conductor, root, journal, name, relaunch_notice_of(state_of(journal), name, why))


def netted(root: Path, conductor, name: str, state: dict) -> None:
    """Lays the team's relaunch entry again when a verb finds it gone and the team needs its net; the timer is armed
    by the tick that follows the verb (`armed`); nothing under `off`."""
    if schedule_seconds(state.season.started) is not None and not netless(state) and not relaunch_standing(root):
        relaunch_said(root, conductor, name, journal_of(root, name))


def timer_standing(root: Path, name: str) -> dict:
    """-> the TIMER that stands for the team, `{pid, due, token}` while its process is alive -- the mark beside the
    journal, read and judged by its pid --, {} when none stands or the process is gone."""
    try:
        found = json.loads(timer_mark(root, name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    pid = found.get("pid")
    if not isinstance(pid, int) or isinstance(pid, bool):
        return {}
    return found if alive(pid) else {}


def alive(pid: int, system: str = os.name) -> bool:
    """-> whether the process `pid` runs. Under Windows the system is asked (`asked_alive`): there `os.kill`
    sends no signal 0, it ends the process. Elsewhere the signal 0, which a process of another user answers
    by a refusal -- alive all the same."""
    if system == "nt":
        return asked_alive(pid)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def disarmed(root: Path, name: str) -> None:
    """Ends the team's timer, when one stands, and removes its mark: the net leaves with `schedule-off`."""
    standing = timer_standing(root, name)
    if standing:
        ended_now(int(standing["pid"]))
    timer_mark(root, name).unlink(missing_ok=True)


def armed(root: Path, conductor, name: str, journal: Path) -> int:
    """The TIMER, under any `schedule:` but `off`, armed by the tick at the start of each round and again at its
    step 7 -- a tick killed between the two leaves the first standing. When the state leaves a deadline (`deadline_of`),
    ONE process is spawned detached -- the entry `pp-team.py`, `timer <name> --token <t>`, outside the console: it holds no hold
    on the machine while it sleeps until that hour, then plays one tick by the house's console and dies --, and the mark beside the journal says `{pid, due, token}`: the pid of the process spawned (uv's
    launcher under Windows, alive while the timer lives: the test of life and the root of the tree a stop ends), its
    hour, and the TOKEN the timer knows itself by; the journal is read again once the mark is written, and a team
    that no longer needs its net (a `stop` wrote and disarmed meanwhile, outside the tick's lock) is disarmed at once;
    a timer standing for an hour no later
    than the new one is kept, a later one ended and replaced; nothing is spawned when nothing is due. `timer-armed {due}` is
    written when a tick arms a timer where none stood -- once: the arming of step 7 finds the one of the round's
    start standing; the timer's own tick, which arms the next, writes nothing. -> the events written."""
    state = state_of(journal)
    seconds = schedule_seconds(state.season.started)
    if seconds is None or netless(state):
        return 0
    clock = tick_now()
    due = deadline_of(state, clock, seconds)
    if due is None:
        return 0
    standing = timer_standing(root, name)
    if standing:
        try:
            if datetime.fromisoformat(str(standing.get("due"))) <= due:
                return 0                                         # a timer stands for an hour no later: kept
        except ValueError:
            pass
        ended_now(int(standing["pid"]))
    if not timer_spawned(root, name, journal, clock, due):
        return 0
    if standing or TIMER_TICKING[0]:
        return 0
    return len(appended(conductor, root, journal, name, timer_armed_of(due)))


def timer_spawned(root: Path, name: str, journal: Path, clock: datetime, due: datetime) -> bool:
    """Spawns ONE timer for `due` -- the entry `pp-team.py`, `timer <name> --token <t>`, detached, its output in the follow log --
    and writes its mark `{pid, due, token}`; the journal is read again once the mark is written, and a team that no
    longer needs its net (a `stop` wrote and disarmed meanwhile, outside the tick's lock) is disarmed at once. -> whether
    the timer stands."""
    wait = max(0.0, (due - clock).total_seconds())
    token = secrets.token_hex(8)
    log = journal.parent / FOLLOW_LOG
    with log.open("ab") as handle:                # the skill itself, never the console: no hold on the machine while it sleeps
        child = subprocess.Popen([sys.executable, str(Path(ENTRY).resolve()), "timer", name,
                                  "--sleep", f"{wait:.3f}", "--due", due.isoformat(timespec="seconds"),
                                  "--token", token],
                                 stdin=subprocess.DEVNULL, stdout=handle, stderr=handle, cwd=str(root.parent),
                                 env={**os.environ, "PP_HOME": str(root)}, **apart())
    mark = timer_mark(root, name)
    temporary = mark.with_name(f".{mark.name}.{os.getpid()}")
    temporary.write_text(json.dumps({"pid": child.pid, "due": due.isoformat(timespec="seconds"), "token": token}),
                         encoding="utf-8")
    os.replace(temporary, mark)
    if netless(state_of(journal)):                 # a verb that leaves the net (a stop) wrote and disarmed while this
        disarmed(root, name)                       # tick spawned: read again after the mark, the timer leaves with it
        return False
    return True


def timer_relayed(root: Path, conductor, name: str, said: str) -> None:
    """The timer whose tick FAILED before its net (step 7) armed the next: when no timer stands after it and the team
    still needs its net (`schedule:` not `off`, not `netless`, no delete begun), ONE timer is armed at the team's step
    -- under the tick's lock taken without waiting: a tick that holds it arms its own --, and the owner is told ONCE
    per season (a `notice`, `timer: true`, the tick's stderr as its `why`, clipped, no `about`: it holds no wait). The
    notice is written on the journal that stands, the declaration away or not: a tick that fails `team-unknown` is
    told as any other. A team whose `deleting` stands gets neither a timer nor a notice, its declaration standing or
    gone: a delete is finishing it."""
    journal = journal_of(root, name)
    lock = locks(conductor)
    lease = lock.try_(journal.parent / TICK_LOCK)
    if lease is None:
        return
    try:
        state = state_of(journal)
        seconds = schedule_seconds(state.season.started)
        if seconds is None or netless(state) or state.season.deleting or timer_standing(root, name):
            return
        clock = tick_now()
        if not timer_spawned(root, name, journal, clock, clock + timedelta(seconds=seconds)):
            return
        appended(conductor, root, journal, name, timer_notice_of(state_of(journal), name, said, seconds), undeclared=True)
    finally:
        lock.release(lease)


def ticked_by_console(root: Path, conductor, name: str) -> subprocess.CompletedProcess:
    """The timer's tick, played by the house's console -- a process of its own under the machine's shared hold, the
    engine and this package as the machine holds them at that hour (after an upgrade, the new ones) --, marked by
    `TIMER_ENV`; a tick the console refuses `maintenance-in-progress` is played again every TIMER_RETRY seconds,
    TIMER_RETRIES times at most, then said, a failure as any other: the timer arms the next (`timer_relayed`). -> the
    tick played: its exit code and its stderr."""
    argv = [sys.executable, str(engine_of(root, conductor)), "--instance", str(root), "team", "tick", name]
    played = None
    for _ in range(TIMER_RETRIES + 1):
        played = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, cwd=str(root.parent),
                                env={**os.environ, TIMER_ENV: "1"})
        if "maintenance-in-progress" not in played.stderr:
            break
        time.sleep(TIMER_RETRY)
    sys.stdout.write(played.stdout)
    sys.stderr.write(played.stderr)
    if "maintenance-in-progress" in played.stderr:
        sys.stderr.write(f"pp-team: {name} · the timer's tick met a maintenance {TIMER_RETRIES} times -- "
                         "the next timer is armed at the step\n")
    return played


def schedule_face(root: Path, name: str, started: dict, state: dict) -> dict:
    """-> the net as the face says it: `{seconds, timer, relaunch, reason}` -- `seconds` the step, `timer` whether a
    timer is armed, `relaunch` whether the relaunch entry stands, `reason` why the system refused it this season
    while it stays absent, else null; every one null under `off`."""
    seconds = schedule_seconds(started)
    if seconds is None:
        return {"seconds": None, "timer": None, "relaunch": None, "reason": None}
    standing = relaunch_standing(root)
    refused = None if standing else relaunch_notice(state)
    return {"seconds": seconds, "timer": bool(timer_standing(root, name)), "relaunch": standing,
            "reason": refused.body.why if refused is not None else None}


def needing(root: Path, but: str | None = None) -> list[str]:
    """-> the teams of the house that need their net, in the order of their names: started, `schedule:` not `off`, a
    task open or a ceremony declared -- `but` left out (a team being deleted)."""
    home = root.parent / TEAMS
    names = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    found = []
    for name in names:
        journal = journal_of(root, name)
        if name == but or not journal.is_file():
            continue
        state = state_of(journal)
        started = state.season.started
        if started is not None and schedule_seconds(started) is not None and not netless(state):
            found.append(name)
    return found


def reboot_line(root: Path, conductor) -> str:
    """-> the house's relaunch line in the crontab: `@reboot`, the interpreter and the engine by their absolute paths --
    the form `--on-end` composes, a line cron replays as is."""
    engine = engine_of(root, conductor)
    return (f"@reboot {shlex.quote(sys.executable)} {shlex.quote(str(engine))} "
            f"--instance {shlex.quote(str(root))} team tick --all --entry >/dev/null 2>&1 {mark_of(root)}")
