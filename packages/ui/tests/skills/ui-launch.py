"""Scenario `ui-launch` -- the post of a house, launched (plan ui, batch le-package-et-son-lanceur):
- a house that pins `ui` gets its prerequisites, `./pp help` lists `./pp ui (ui) …`, the catalog says the command plays at the terminal
- without a terminal `./pp ui` refuses `tty-missing` in one line; `--render` needs none and prints the frame as text at the asked size
- the refusals are one named line each: `pane-unknown`, `size-invalid`, `argument-unknown`
- the seam to the verbs: `command_for` names the witness of PP_UI_FACES when it carries the verb, the house's console otherwise; `run_verb` plays it
- the whole chain on a pseudo-terminal: the console hands the terminal to the skill, uv gives it Textual, the post draws, `q` closes it, exit 0
"""
from __future__ import annotations

import os
import pty
import select
import subprocess
import sys
import time

from conductor import contributions, instance
from tests.harness import SOURCE, cli

PTY_TIMEOUT = 20.0


def _pty_run(engine, cwd) -> tuple[int | None, bytes, float]:
    """`./pp ui` on a fresh pseudo-terminal: read until the frame shows, send `q`, wait."""
    leader, follower = pty.openpty()
    env = {**os.environ, "TERM": "xterm-256color", "COLUMNS": "80", "LINES": "24"}
    proc = subprocess.Popen([sys.executable, str(engine), "ui"], stdin=follower, stdout=follower,
                            stderr=follower, cwd=cwd, env=env, start_new_session=True)
    os.close(follower)
    seen, started, sent = b"", time.monotonic(), False
    try:
        while time.monotonic() - started < PTY_TIMEOUT:
            ready, _, _ = select.select([leader], [], [], 0.2)
            if ready:
                try:
                    chunk = os.read(leader, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                seen += chunk
            if not sent and b"Dialogue" in seen:
                os.write(leader, b"q")            # the frame is up: close it
                sent = True
            if proc.poll() is not None and sent:
                break
        try:
            rc = proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            rc = None
    finally:
        os.close(leader)
    return rc, seen, time.monotonic() - started


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("ui-house", packages=("ui",))
    ws, engine = env.made.parent, env.engine

    def call(*args: str, **kw):
        return cli(engine, *args, cwd=ws, **kw)

    # --- the house pins the closure, the console carries the verb at the terminal -------------
    pinned = set(instance.read(env.made)["packages"])
    helped = call("help")
    ui_line = next((one for one in helped.stdout.splitlines() if "./pp ui" in one), "")
    catalog = (env.made / ".sys" / "tools.md").read_text(encoding="utf-8")
    if ({"agent", "team", "ui"} <= pinned and helped.returncode == 0 and "(ui)" in ui_line
            and "verb=ui, skill=pp-ui, tty=True" in catalog):
        held("the house carries the post", f"pins {sorted(pinned)}; `./pp help` lists `./pp ui (ui) …`; "
             "the catalog says verb=ui, skill=pp-ui, tty=True")
    else:
        failures.append(f"  ✗ house and verb              {sorted(pinned)} {ui_line!r} "
                        f"{'tty=True' in catalog}")

    # --- no terminal: one line, nothing on stdout, exit 2 ----------------------------------------
    bare = call("ui")
    if (bare.returncode == 2 and bare.stdout == "" and "tty-missing" in bare.stderr
            and len(bare.stderr.strip().splitlines()) == 1):
        held("tty-missing without a terminal", bare.stderr.strip())
    else:
        failures.append(f"  ✗ tty-missing                 rc={bare.returncode} {bare.stdout[:80]!r} "
                        f"{bare.stderr[-200:]!r}")

    # --- the frame as text, at the asked size, twice (the second is the warm start) --------------
    t0 = time.monotonic()
    first = call("ui", "--render", "frame", "--size", "80x24")
    t1 = time.monotonic()
    second = call("ui", "--render", "frame", "--size", "80x24")
    t2 = time.monotonic()
    lines = first.stdout.rstrip("\n").split("\n")
    if (first.returncode == 0 and len(lines) == 24 and all(len(one) <= 80 for one in lines)
            and "pp" in lines[0] and ws.name in lines[0] and "1·Dialogue" in first.stdout
            and "name an agent to talk to" in " ".join(first.stdout.split()) and "[q] quit" in first.stdout
            and second.stdout.split("\n")[0] == lines[0] and not first.stderr):
        held("--render prints the frame", f"24 lines ≤ 80 cols, `pp · {ws.name}` on the first, the tabs "
             f"and the footer; {t1 - t0:.2f}s then {t2 - t1:.2f}s")
    else:
        failures.append(f"  ✗ render frame                rc={first.returncode} lines={len(lines)} "
                        f"{first.stdout[:300]!r} {first.stderr[-300:]!r}")
    wide = call("ui", "--render", "teams", "--size", "120x30")
    wide_lines = wide.stdout.rstrip("\n").split("\n")
    if (wide.returncode == 0 and len(wide_lines) == 30 and max(len(one) for one in wide_lines) <= 120
            and "no team declared" in " ".join(wide.stdout.split())):
        held("--render takes a pane and a size", "teams at 120x30: 30 lines, the Teams tab of a house without a team")
    else:
        failures.append(f"  ✗ render teams                rc={wide.returncode} lines={len(wide_lines)} "
                        f"{wide.stderr[-200:]!r}")

    # --- the refusals, one named line each ---------------------------------------------------------
    said = {}
    for code, args in (("pane-unknown", ("--render", "nowhere")),
                       ("size-invalid", ("--render", "frame", "--size", "10")),
                       ("argument-unknown", ("--open",))):
        done = call("ui", *args)
        said[code] = (done.returncode == 2 and done.stdout == "" and code in done.stderr
                      and len(done.stderr.strip().splitlines()) == 1)
    if all(said.values()):
        held("the refusals are named", "pane-unknown · size-invalid · argument-unknown, one line, rc 2")
    else:
        failures.append(f"  ✗ refusals                    {said}")

    # --- the seam: the witness of PP_UI_FACES, else the house's console ----------------------------
    faces = contributions.module_at(SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "faces" / "__init__.py")
    witnesses = env.made.parent / "witness-faces"
    witnesses.mkdir(exist_ok=True)
    stand_in = witnesses / "agent"
    stand_in.write_text("#!/bin/sh\nprintf '{\"ok\": 1, \"args\": \"%s\"}\\n' \"$*\"\n", encoding="utf-8")
    stand_in.chmod(0o755)
    plain = faces.command_for(["agent", "list", "--json"], str(ws))
    os.environ["PP_UI_FACES"] = str(witnesses)
    try:
        routed = faces.command_for(["agent", "list", "--json"], str(ws))
        other = faces.command_for(["team", "status"], str(ws))
        played = faces.run_verb(["agent", "list", "--json"], str(ws))
    finally:
        del os.environ["PP_UI_FACES"]
    if (plain == [str(ws / "pp"), "agent", "list", "--json"] and routed == [str(stand_in), "list", "--json"]
            and other == [str(ws / "pp"), "team", "status"]
            and played.rc == 0 and played.out.strip() == '{"ok": 1, "args": "list --json"}'):
        held("the seam routes to the witness or the console", "command_for: the house's `pp` by default, "
             "the witness when PP_UI_FACES carries the verb; run_verb played the witness")
    else:
        failures.append(f"  ✗ faces seam                  {plain} {routed} {other} {played}")

    # --- the whole chain on a pseudo-terminal: the post draws, `q` closes it ------------------------
    rc, seen, took = _pty_run(engine, ws)
    if rc == 0 and b"Dialogue" in seen:
        held("the post opens on a terminal and `q` closes it", f"console -> run_at_terminal -> uv -> "
             f"Textual drew the frame on a pty, `q` ended it with rc 0 in {took:.1f}s")
    else:
        failures.append(f"  ✗ pty launch                  rc={rc} {took:.1f}s {seen[-400:]!r}")
    return 0
