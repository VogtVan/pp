"""The vectors of a run verified and mounted, the switches of its packages played, by the principal."""
from __future__ import annotations

import os
import re
from dataclasses import replace
from pathlib import Path

from acts.launch import conducted
from model.policy import Asked
from model.refusal import VectorRefused, Unserved
from model.vector import Mount
from model.words import FAMILY
from rules.refusals import refused_mount, refusal_of, refused_switch
from store.houses import refusal_line
from store.refusal import refuse
from store.settings import switches_played, packages_of, worded


def verified(conductor, meta: Path, key: str, waiting: dict | None, mounts: list[Mount]) -> None:
    """EVERY vector verified before ANY is mounted: the engine's face `events.verified` -- the script the
    family's manifest names, its verb `verify`, the vector on stdin --, asked for the run: its switches in the
    play, and in the environment the verifier inherits `PP_HOME`, the agent's instance (the script's file lives
    in its machine's vendor), and the run's key (a tree the run alone reaches is read at its slot). The first
    vector a verifier refuses raises `VectorRefused`, its cause the script's own code when its last line says
    one (`<script>: <code> -- <detail>`), the engine's otherwise: nothing was mounted."""
    if not mounts:
        return
    instance, variable = conductor.instance, conductor.context.VARIABLE
    named = {"PP_HOME": conductor.contributions.launched_environment(meta)["PP_HOME"], variable: key}
    before = {one: os.environ.get(one) for one in named}
    os.environ.update(named)
    instance.play_switches(meta, switches_played(conductor, meta, key, waiting))
    try:
        for one in mounts:
            try:
                conductor.events.verified(meta, one.vector)
            except conductor.Refusal as refusal:
                said = str(refusal).split(" — ", 1)[-1]
                own = re.search(rf"{re.escape(one.script)}: ([a-z0-9-]+) -- (.*)$", said)
                if own is not None:
                    raise VectorRefused(own.group(1), one.vector, own.group(2)) from refusal
                raise VectorRefused(refusal.code, one.vector, said) from refusal
    finally:
        instance.play_switches(meta, {})
        for one, value in before.items():
            if value is None:
                os.environ.pop(one, None)
            else:
                os.environ[one] = value


def mounted(conductor, root: Path, meta: Path, key: str, mounts: list[Mount], marble: bool = False,
            cap: int | None = None) -> None:
    """The vectors of the run POSED, in their order, once every one is verified (`verified`): `-s <script>
    mount <id>` as the principal, under the hold (`PP_HOLD_OUTPUT`), by the one path of the launcher's
    gestures (`conducted`) -- the script says what to mount, the engine mounts it for the exchange and renders
    nothing: the laws and the offers of each mount are in force, its matter waits at the run with the output the
    message opened, in the order of the mounts, for the one bare call that follows (`released`). The gesture
    names the script alone: the engine judges it on what the root of the exchange offers. A gesture that does
    not mount though its vector was verified (a script the root does not offer, a refusal of the engine) raises
    `VectorRefused`."""
    for mount in mounts:
        played = conducted(conductor, root, meta, key, "-s", mount.script, "mount", mount.ident, marble=marble,
                           cap=cap, hold=True)
        if played.returncode != 0:
            cause, detail = refused_mount(refusal_line(), played, mount.script, key)
            raise VectorRefused(cause, mount.vector, detail)


def released(conductor, root: Path, meta: Path, key: str, marble: bool = False, cap: int | None = None) -> str:
    """-> the first prompt of an exchange that mounts vectors, served by the principal's bare call once the last one
    is posed: the engine plays the exchange the message opened and renders it once -- what the mounts serve
    before its first step, every step with the laws then in force --, or renders the step a run stands on; the
    text as the engine rendered it. When the bare call fails, nothing is launched and the refusal says why: the
    engine's own, else the call's exit code."""
    played = conducted(conductor, root, meta, key, marble=marble, cap=cap)
    if played.returncode != 0:
        raise Unserved(f"{refusal_of(refusal_line(), played) or f'the bare call that serves the first prompt of run {key} exited {played.returncode} without a word'} -- nothing launched; at an opening the run stays opened and never launched, a new wake-up opens another; at a resume `--run {key}` takes the run up", refusal_of(refusal_line(), played))
    return played.stdout


def switch_tried(conductor, root: Path, meta: Path, key: str, name: str, on: bool, line: str, waiting: dict, say) -> None:
    """One switch of the conversation's WAITING LIST played on the run by the principal: accepted, it
    leaves the list and `package` says it applied (`pending: false`, the packages now); refused because
    the package holds the run's view (`package-in-flight`), it stays and waits for the next launch, said
    by nobody; refused for any other cause, it leaves the list and `refused` says the engine's code and
    detail."""
    played = conducted(conductor, root, meta, key, "-enable" if on else "-disable", name)
    if played.returncode == 0:
        waiting.pop(name, None)
        say(key, f"package {name} {'on' if on else 'off'}", "package",
            {"name": name, "on": on, "pending": False, "packages": packages_of(conductor, meta, key)})
        return
    code, detail = refused_switch(refusal_line(), played)
    if code == "package-in-flight":
        return
    waiting.pop(name, None)
    say(key, f"refused {code}", "refused", {"code": code, "line": line, "detail": detail})


def switched(conductor, root: Path, meta: Path, asked: Asked, key: str | None, item: tuple, say,
             waiting: dict) -> Asked:
    """`conduct` and `package`, the principal's words on a conversation's run; -> what is asked from now on.
    `conduct` says whether the next exchanges are conducted (`asked.conduct`; `run-missing` before the run is opened).
    `package` asks a package in or out of the run's play: the word the run's own switches hold already -> the
    waiting for that name drops, `package` says it (`pending: false`); no run yet -> it WAITS in the
    conversation's list (`waiting`, `{name: (on, line)}`), `package` says it (`pending: true`), and the
    first launch after the opening plays it; a run -> the engine's `-disable`/`-enable`
    at once: applied (`pending: false`), or held by the run's view (`package-in-flight`) -> it waits
    for the next launch (`pending: true`), or refused for another cause -> `refused` with the
    engine's code and detail. The list lives in this process alone: closing the conversation drops it."""
    line = item[-1]
    if item[0] == "conduct":
        if key is None:
            say("", "", "refused", {"code": "run-missing", "line": line})
            return asked
        say(key, "", "conduct", {"on": item[1]})
        return replace(asked, conduct=item[1])
    name, on = item[1], item[2]
    packages = packages_of(conductor, meta, key)
    if worded(conductor, meta, key, name) == ("on" if on else "off"):   # the run's own word already: nothing to wait for
        waiting.pop(name, None)
        say(key or "", "", "package", {"name": name, "on": on, "pending": False, "packages": packages})
        return asked
    waiting[name] = (on, line)
    if key is not None:
        switch_tried(conductor, root, meta, key, name, on, line, waiting, say)
        if name not in waiting:
            return asked
    say(key or "", "", "package", {"name": name, "on": on, "pending": True, "packages": packages})
    return asked


def replayer(conductor, root: Path, meta: Path, waiting: dict, say=None):
    """-> the hook handed to `exchange`: before every launch of a RESUME, the switches still waiting are played
    on the run in the order they came, each by `switch_tried` (`-enable`/`-disable`, which beat the agent's
    SETTINGS), said by `say` -- a conversation's flow --, else by the exchange's own (`told`: on stderr and kept
    in the run's flow, a wake-up's `--package`). An opening plays none of them here: they rode `PP_PACKAGES`."""
    def before(key: str, told=None) -> None:
        for name, (on, line) in list(waiting.items()):
            switch_tried(conductor, root, meta, key, name, on, line, waiting, say or told)
    return before


def held_by_guardian(conductor, root: Path, name: str, keys: list[str]) -> None:
    """Asks the engine, before any removal, whether the family's guardian keeps one of the runs
    (`events.guarded` on `agent-run:<path>/<key>`): a package that declares itself the guardian of the
    family answers -- this one names none. A no refuses `run-held` with the guardian's reason, nothing
    removed; no guardian declared, nothing plays."""
    for key in keys:
        try:
            conductor.events.guarded(root, f"{FAMILY}:{name}/{key}")
        except conductor.Refusal as refusal:
            refuse(f"run-held -- {str(refusal).split(' — ', 1)[-1]}; nothing removed.")
