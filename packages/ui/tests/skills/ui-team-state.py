"""Scenario `ui-team-state` -- the Teams tab says what each team does and what waits for the owner (plan ui, batch
l-etat-et-les-gestes), on the bench's `pp-team` witness replaying seven teams, one per state the face says
(`state`, `waiting_on`, `paused`, team 0.30.0 and 0.32.0):
- the menu: `team · run · msg · done` -- `gamma`, the face of `test` on 10/10 (no wake-up under way, an escalation,
  four tasks done not seen), says `0 1 4`; `⏸` before the paused team, `-` for the team never started
- the look of a team's name is its state's (`--styles`): working, waiting and idle each their colour, waiting bold
  when the owner alone lifts what holds it, paused the colour of waiting without bold
- the head of the team chosen says its state -- `working`, `waiting · owner, budget`, `paused since … by house` --,
  and so does the status line
- the folded menu says the state beside the name
"""
from __future__ import annotations

import re
from datetime import datetime

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the bench's reader of styles


def _flat(text: str) -> str:
    return " ".join(text.split())


def _codes(params: str) -> tuple[bool, str | None]:
    """-> (bold, foreground) of one SGR sequence's parameters."""
    tokens, bold, fg, at = params.split(";"), False, None, 0
    while at < len(tokens):
        one = tokens[at]
        if one in ("38", "48") and at + 1 < len(tokens):
            width = 5 if tokens[at + 1] == "2" else 3
            if one == "38":
                fg = ";".join(tokens[at + 2:at + width])
            at += width
            continue
        if one == "1":
            bold = True
        elif one.isdigit() and (30 <= int(one) <= 37 or 90 <= int(one) <= 97):
            fg = one
        at += 1
    return bold, fg


def look_of(text: str, name: str) -> tuple[bool, str | None] | None:
    """-> how the first cell holding `name` as a word is drawn in a `--styles` capture: (bold, foreground)."""
    for row in text.split("\n"):
        if not re.search(rf"\b{name}\b", P.ANSI.sub("", row)):
            continue
        current = ""
        for part in re.split(r"(\x1b\[[0-9;]*m)", row):
            found = P.SGR.fullmatch(part)
            if found:
                current = found.group(1)
            elif re.search(rf"\b{name}\b", part):
                return _codes(current)
    return None


def _moment(iso: str) -> str:
    moment = datetime.fromisoformat(iso).astimezone()
    today = datetime.now().astimezone()
    if moment.date() == today.date():
        return moment.strftime("%H:%M:%S")
    return moment.strftime("%d/%m %H:%M" if moment.year == today.year else "%d/%m/%Y %H:%M")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-state", T.shades_script())

    # --- the menu and the looks of the names ----------------------------------------------------------------
    done = house.render("--render", "teams", "--size", "130x34", "--styles")
    plain = P.ANSI.sub("", done.stdout)
    rows = {"columns": r"team\s+run\s+msg\s+done", "gamma": r"gamma\s+0\s+1\s+4", "delta": r"⏸ delta\s+0\s+0\s+0",
            "epsilon": r"epsilon\s+0\s+0\s+2", "veille": r"veille\s+-\s+-\s+-"}
    missing = [key for key, pattern in rows.items() if not re.search(pattern, plain)]
    if done.returncode == 0 and not missing:
        held("the menu counts as the inbox", "team · run · msg · done; gamma 0 1 4 under an escalation, ⏸ delta, "
             "veille - - -")
    else:
        failures.append(f"  ✗ menu                        rc={done.returncode} missing={missing} {plain[:1800]!r} "
                        f"{done.stderr[-300:]!r}")
    looks = {name: look_of(done.stdout, name) for name in ("beta", "gamma", "delta", "epsilon", "zeta", "veille")}
    known = all(looks.values())
    if (done.returncode == 0 and known and looks["gamma"][0] and not looks["beta"][0] and not looks["delta"][0]
            and looks["gamma"][1] == looks["beta"][1] == looks["delta"][1]
            and len({looks[one][1] for one in ("beta", "epsilon", "zeta", "veille")}) == 4):
        held("a name in its state's look", "waiting bold on the owner's guards (gamma) and plain on its members' "
             "(beta), paused as waiting without bold, working, idle and never each their own colour")
    else:
        failures.append(f"  ✗ looks                       {looks}")

    # --- the head and the status line of the team chosen ----------------------------------------------------
    paused = f"paused since {_moment(T.PAUSED_AT['at'])} by house"
    for keys, name, said in (("", "alpha", "working"), ("down,down", "gamma", "waiting · owner, budget"),
                             ("down,down,down", "delta", paused), ("down,down,down,down", "epsilon", "idle")):
        done = house.render("--render", "teams", "--size", "130x34", *(["--press", keys] if keys else []))
        lines = done.stdout.rstrip("\n").split("\n")
        status = lines[-1].strip()
        head = next((line for line in lines if f"{name} · owner house" in line), None)
        after = lines[lines.index(head) + 1] if head in lines and lines.index(head) + 1 < len(lines) else ""
        if done.returncode == 0 and said in after and f"· {name} · {said.split(' ·')[0].split(' since')[0]} ·" in status:
            held(f"{name}'s state at its head and on the status", f"{said!r} under its name; {status[:60]!r}")
        else:
            failures.append(f"  ✗ head {name:<22} rc={done.returncode} {after!r} {status!r} {done.stdout[-1500:]!r} "
                            f"{done.stderr[-300:]!r}")

    # --- folded ---------------------------------------------------------------------------------------------
    done = house.render("--render", "teams", "--size", "60x20")
    if done.returncode == 0 and "team: < alpha · working >" in done.stdout:
        held("the folded menu says the state", "team: < alpha · working >")
    else:
        failures.append(f"  ✗ folded                      rc={done.returncode} {done.stdout[:900]!r} {done.stderr[-300:]!r}")
    return 0
