"""Scenario `ui-team-state` -- the Teams tab says what each team does, what waits for the owner, what a member owes
and how it answers, in colours the cursor keeps, on the bench's `pp-team` witness: first seven teams, one per state the
face says (`state`, `waiting_on`, `paused`), then `core-review` waiting on `suspected` -- `reviewer` suspected, tried
again at 09:30, its run dead; `lead` fallen once and back, owing two messages, one reminded already; T3 with a `do`
answered by #46 and one still running, a wait counted 1 of 3, and `lead` woken again without a new message, a relance
the face says `owed`:
- the menu counts what the face counts per team -- runs, messages, tasks done --, `⏸` before the paused team only,
  no figure for the team never started
- the look of a team's name is its state's (`--styles`): working, waiting and idle each their colour, waiting bold
  when the owner alone lifts what holds it, paused the colour of waiting without bold
- the head of the team chosen says its state, what it waits on and, paused, how long ago and by whom; the status line
  says the state after the team's name
- on a narrow screen the menu folds into one line, the team chosen beside its state, no other team shown
- a stopped task keeps its colour under the cursor of Tasks: the row under the cursor has a background of its own,
  its state drawn as the same state on the rows off it
- the table Members draws `reviewer` and its suspicion in one bold colour in place of its run's state, the hour of its
  next try in `live`, `lead` plain; the head waits on `suspected`, bold in another colour; the status line and the
  menu say the team
- the column owes counts `lead`'s debts, in the look of a problem -- that of the head's wait --, nothing for
  `reviewer`
- the colours stay under the cursor: the suspicion and the count of a reminded debt drawn the same on and off the
  cursor's row, the cursor's background following it
- `d` on `reviewer` says its health -- suspected, its falls, its next try, its repents; on `lead` its debts in order
  (id, verb, sender, task, reminders) and its health
- the band of T3 says its dos -- the answered one with its answer's id --, its wait counted, and `lead`'s wake-up a
  relance owed, launched as long ago as the face says
"""
from __future__ import annotations

import re
from datetime import datetime

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

WIDE = ("--size", "130x34")
SEP = P.palette_constant("SEP")
SEGMENT = re.compile(r"\x1b\[([0-9;]*)m([^\x1b]*)")


def background(text: str, name: str, within: str) -> str | None:
    """-> the background of the segment writing `name` on the first row holding `within`, its SGR parameters."""
    for row in text.split("\n"):
        if within not in P.ANSI.sub("", row):
            continue
        for params, part in SEGMENT.findall(row):
            if re.search(rf"\b{re.escape(name)}\b", part):
                found = re.search(r"48;2;(\d+;\d+;\d+)", params)
                return found.group(1) if found else None
    return None


def centre(text: str, within: str) -> str:
    """-> the first row of a `--styles` capture holding `within` right of the menu, from the menu's edge on."""
    for row in text.split("\n"):
        bare = P.ANSI.sub("", row)
        if "│" in bare and within in bare.split("│", 1)[1]:
            return row[row.index("│"):]
    return ""


def rows_of(text: str) -> list[str]:
    return P.ANSI.sub("", text).split("\n")


def state_row(rows: list[str], face: dict) -> str:
    """-> the row under the head of the team chosen -- its name, its owner and its principals --: its state."""
    at = next((n for n, row in enumerate(rows) if face["team"] in row and face["owner"] in row
               and all(one in row for one in face["principals"])), -1)
    return rows[at + 1].split("│")[-1] if 0 <= at < len(rows) - 1 else ""




def stated(text: str, team: str) -> str:
    """-> what the status line says after the team's name: its next part."""
    parts = [one.strip() for one in P.status_of(P.ANSI.sub("", text)).split(SEP)]
    return parts[parts.index(team) + 1] if team in parts and parts.index(team) + 1 < len(parts) else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-state", T.shades_script())
    shades = {name: T.state_of(name, state, waits, paused) for name, state, waits, _, _, _, paused in T.SHADES}

    # --- seven teams: the menu, the looks of the names, the head and the status of alpha -------------------------
    menu = house.render("--render", "teams", *WIDE, "--styles")
    rows = rows_of(menu.stdout)
    paused = P.palette_constant("PAUSED")
    counted = {name: rf"(^|\s){name}\s+{running}\s+{asks}\s+{done}\s" for name, _, _, running, asks, done, _ in T.SHADES}
    missing = [name for name, pattern in counted.items() if not any(re.search(pattern, row) for row in rows)]
    marked = [name for name, *_ in T.SHADES if any(re.search(rf"{re.escape(paused)} {name}\b", row) for row in rows)]
    never = next((row.split("│")[0] for row in rows if re.search(r"^\s*veille\b", row)), "")
    pausing = [name for name, *_, pause in T.SHADES if pause]
    if menu.returncode == 0 and not missing and marked == pausing and never and not re.search(r"\d", never):
        held("the menu counts as the inbox", "runs, messages and tasks done as each badge counts them; "
             f"{paused} before {', '.join(pausing)} alone; veille without a figure")
    else:
        failures.append(f"  ✗ menu                        rc={menu.returncode} missing={missing} marked={marked} "
                        f"{never!r} {rows[:14]!r} {menu.stderr[-300:]!r}")
    under = menu.stdout.split("\n", 1)[-1]           # the header says the versions (`…-beta.18`): the names are read under it
    looks = {name: T.look_of(under, name) for name in ("beta", "gamma", "delta", "epsilon", "zeta", "veille")}
    if (menu.returncode == 0 and all(looks.values()) and looks["gamma"][0] and not looks["beta"][0]
            and not looks["delta"][0] and looks["gamma"][1] == looks["beta"][1] == looks["delta"][1]
            and len({looks[one][1] for one in ("beta", "epsilon", "zeta", "veille")}) == 4):
        held("a name in its state's look", "waiting bold on the owner's guards (gamma) and plain on its members' "
             "(beta), paused as waiting without bold, working, idle and never each their own colour")
    else:
        failures.append(f"  ✗ looks                       {looks}")

    aged = T.age_said(T.PAUSED_AT["at"])             # the pause of 10/10, in days: its age before a render, and after

    def headed(done, name: str, keys: str) -> None:
        face = shades[name]
        said = state_row(rows_of(done.stdout), face)
        words = [face["state"], *face["waiting_on"]]
        if face["paused"]:
            words += [face["paused"]["by"]]
        ages = ({T.age_said(face["paused"]["at"])} | {aged} if face["paused"] else set())
        if (done.returncode == 0 and T.in_order(said, *words) and (not ages or any(one in said for one in ages))
                and stated(done.stdout, name) == face["state"]):
            held(f"{name}'s state at its head and on the status", f"{said.strip()!r} under its name ({keys or 'no key'}); "
                 f"the status says {face['state']} after {name}")
        else:
            failures.append(f"  ✗ head {name:<22} rc={done.returncode} {said!r} {ages} {stated(done.stdout, name)!r} "
                            f"{done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    headed(menu, "alpha", "")
    headed(house.render("--render", "teams", *WIDE, "--press", "down,down"), "gamma", "down,down")
    folded = house.render("--render", "teams", "--size", "60x20", "--press", "down,down,down")
    headed(folded, "delta", "down,down,down at 60x20")
    lines = rows_of(folded.stdout)[1:]                # under the header, which says the versions
    fold = next((row for row in lines if re.search(r"\bdelta\b", row)), "")
    others = [name for name, *_ in T.SHADES if name != "delta" and any(re.search(rf"\b{name}\b", row) for row in lines)]
    if folded.returncode == 0 and T.in_order(fold, "delta", shades["delta"]["state"]) and not others:
        held("the folded menu says the state", f"{fold.strip()!r} -- no other team on the screen")
    else:
        failures.append(f"  ✗ folded                      rc={folded.returncode} {fold!r} others={others} "
                        f"{folded.stdout[:900]!r} {folded.stderr[-300:]!r}")
    headed(house.render("--render", "teams", *WIDE, "--press", "down,down,down,down"), "epsilon", "down,down,down,down")

    # --- Tasks, the stopped filter: the state's colour under the cursor ------------------------------------------
    stopped = house.render("--render", "tasks", "--size", "150x40", "--press", "shift+tab,shift+tab,down,down",
                           "--styles")
    first, second = T.SHADES[0][0], T.SHADES[1][0]        # one task stopped per team, the first under the cursor
    under, off = (T.look_of(centre(stopped.stdout, f" {one} "), "stopped") for one in (first, second))
    grounds = tuple(background(centre(stopped.stdout, f" {one} "), "T1", f" {one} ") for one in (first, second))
    if (stopped.returncode == 0 and under is not None and under[0] and under[1] is not None and under == off
            and None not in grounds and grounds[0] != grounds[1]):
        held("a stopped task in its colour under the cursor", f"stopped {under} on the row of {first} under the cursor "
             f"(background {grounds[0]}) as on {second}'s (background {grounds[1]})")
    else:
        failures.append(f"  ✗ stopped under the cursor    rc={stopped.returncode} {under} {off} {grounds} "
                        f"{P.ANSI.sub('', stopped.stdout)[:1500]!r} {stopped.stderr[-300:]!r}")

    # --- core-review waiting on a suspected member, its debts: the table, under and off the cursor ---------------
    face = {**T.SUSPECTED, "tasks": T.DEBTS["tasks"]}
    script = T.script()
    script["states"]["core-review"] = [face]
    house.use(script)
    lead, reviewer = face["members"]
    tried = datetime.fromisoformat(reviewer["health"]["tried_at"])
    suspicion = face["waiting_on"][0]
    on = house.render("--render", "teams", *WIDE, "--press", "tab,down", "--styles")      # the cursor on reviewer
    at_lead = house.render("--render", "teams", *WIDE, "--press", "tab", "--styles")      # the cursor on lead
    plain = rows_of(at_lead.stdout)
    row = next((one for one in plain if re.search(
        rf"{reviewer['member']}\s+{reviewer['path']}\s+{reviewer['run']}\s+{suspicion}\s+{len(reviewer['tasks'])}\s+"
        rf"\S+\s+.*\b{tried:%H:%M}\b", one)), "")
    name = T.look_of(at_lead.stdout, reviewer["member"], within=reviewer["path"])
    state = T.look_of(at_lead.stdout, suspicion, within=reviewer["path"])
    plain_lead = T.look_of(on.stdout, lead["member"], within=lead["path"])
    head = state_row(plain, face)
    waiting = T.look_of(at_lead.stdout, face["state"], within=head.strip()) if head.strip() else None
    if (at_lead.returncode == 0 and on.returncode == 0 and row and name is not None and name[0] and name[1] is not None
            and state == name and plain_lead is not None and not plain_lead[0] and T.in_order(head, face["state"], suspicion)
            and waiting is not None and waiting[0] and waiting[1] != name[1]):
        held("a member that does not answer is seen", f"{reviewer['member']} and {suspicion} bold in one colour {name}, "
             f"its try at {tried:%H:%M}; {lead['member']} plain; the head {face['state']} on {suspicion} in another "
             f"{waiting}")
    else:
        failures.append(f"  ✗ suspected                   rc={at_lead.returncode}/{on.returncode} {row!r} {name} {state} "
                        f"{plain_lead} {head!r} {waiting} {plain[-30:]!r} {at_lead.stderr[-300:]!r}")
    badge = next(one for one in T.BADGES if one["team"] == face["team"])
    listed = [one for one in plain if re.search(rf"^\s*{face['team']}\s+{badge['running']}\s+{badge['asks']}\s+"
                                                rf"{badge['done']}\s", one)]
    if at_lead.returncode == 0 and stated(at_lead.stdout, face["team"]) == face["state"] and listed:
        held("the status line and the menu say the team waits", f"the status says {face['state']} after "
             f"{face['team']}; the menu {listed[0].split('│')[0].strip()!r}")
    else:
        failures.append(f"  ✗ status                      {P.status_of(plain[-1] if plain else '')!r} {listed}")

    plain = rows_of(on.stdout)
    owing = next((one for one in plain if re.search(rf"{lead['member']}\s+{lead['path']}\s+{lead['run']}\s+"
                                                     rf"{lead['how']}\s+{len(lead['tasks'])}\s+{len(lead['owes'])}\s", one)), "")
    owed = re.search(rf"{reviewer['member']}\s+{reviewer['path']}\s+{reviewer['run']}\s+\S+\s+"
                     rf"{len(reviewer['tasks'])}\s+(\S+)", "\n".join(plain))
    count = T.look_of(on.stdout, str(len(lead["owes"])), within=lead["path"])
    problem = T.look_of(on.stdout, face["state"], within=head.strip()) if head.strip() else None
    if (on.returncode == 0 and owing and owed and not re.search(r"\d", owed.group(1)) and count is not None
            and count[0] and count[1] is not None and count == problem):
        held("the column owes", f"{lead['member']} {len(lead['owes'])} in the look of a problem {count}, as the head's "
             f"wait; nothing counted for {reviewer['member']} ({owed.group(1)})")
    else:
        failures.append(f"  ✗ owes                        rc={on.returncode} {owing!r} {owed and owed.group(0)!r} "
                        f"{count} {problem} {plain[-30:]!r} {on.stderr[-300:]!r}")

    red_on = T.look_of(on.stdout, suspicion, within=reviewer["path"])
    owes_on = T.look_of(at_lead.stdout, str(len(lead["owes"])), within=lead["path"])
    ground = (background(on.stdout, reviewer["member"], reviewer["path"]),
              background(on.stdout, lead["member"], lead["path"]),
              background(at_lead.stdout, lead["member"], lead["path"]))
    if (red_on is not None and red_on[0] and red_on == state and owes_on is not None and owes_on == count
            and None not in ground and ground[0] != ground[1] and ground[2] == ground[0]):
        held("the colour stays under the cursor (textual-dark)", f"{suspicion} {red_on} on and off the cursor; owes "
             f"{owes_on} both ways; the cursor's background {ground[0]} against {ground[1]}, on whichever row it stands")
    else:
        failures.append(f"  ✗ cursor                      {suspicion} {red_on}/{state} owes {owes_on}/{count} "
                        f"ground {ground}")

    # --- d: the health and the debts of a member ------------------------------------------------------------------
    health = reviewer["health"]
    done = house.render("--render", "teams", *WIDE, "--press", "tab,down,d")
    overlay, title = P.overlay_rows(done.stdout), " ".join(P.title_of(done.stdout))
    said = next((one for one in overlay if re.search(rf"^\D*\b{health['falls']}\b\D*{tried:%d/%m %H:%M}\D*"
                                                     rf"\b{health['repents']}\b\D*$", one)), "")
    if done.returncode == 0 and T.in_order(title, face["team"], reviewer["member"]) and suspicion in said:
        held("d says the health (tab,down,d)", f"{said!r}: {suspicion}, falls {health['falls']}, next try "
             f"{tried:%d/%m %H:%M}, repents {health['repents']}")
    else:
        failures.append(f"  ✗ d health tab,down,d         rc={done.returncode} {title!r} {overlay!r}")

    health = lead["health"]
    done = house.render("--render", "teams", *WIDE, "--press", "tab,d")
    overlay, title = P.overlay_rows(done.stdout), " ".join(P.title_of(done.stdout))
    said = next((one for one in overlay if re.search(rf"^\D*\b{health['falls']}\b\D*\b{health['repents']}\b\D*$", one)), "")
    if done.returncode == 0 and T.in_order(title, face["team"], lead["member"]) and said and suspicion not in said:
        held("d says the health (tab,d)", f"{said!r}: falls {health['falls']}, repents {health['repents']}, not "
             f"{suspicion}")
    else:
        failures.append(f"  ✗ d health tab,d              rc={done.returncode} {title!r} {overlay!r}")
    words = [word for one in lead["owes"] for word in
             (f"#{one['id']}", one["verb"], one["from"], one["task"], *([str(one["reminded"])] if one["reminded"] else []))]
    debts = next((one for one in overlay if T.in_order(one, *words)), "")
    if done.returncode == 0 and debts:
        held("d lists the debts of a member", f"{debts!r}: {' '.join(words)}")
    else:
        failures.append(f"  ✗ d owes                      rc={done.returncode} {words} {overlay!r}")

    # --- the band of T3: its dos answered, its wait counted, the relance of lead -----------------------------------
    task = next(one for one in face["tasks"] if one["id"] == "T3")
    wait, wake = task["waits"][0], task["running"][0]
    since = {T.age_said(wake["since"])}
    done = house.render("--render", "tasks", "--size", "150x40")
    since |= {T.age_said(wake["since"])}
    plain = rows_of(done.stdout)
    dos = next((one for one in plain if all(re.search(rf"\b{d['from']}\W+{d['to']}\b", one) for d in task["dos"])), "")
    answered = all(re.search(rf"\b{d['from']}\W+{d['to']}\W+#{d['answered']}\b", dos) if d["answered"]
                   else re.search(rf"\b{d['from']}\W+{d['to']}\b(?!\W+#)", dos) for d in task["dos"])
    waits = next((one for one in plain if re.search(rf"\b{wait['member']}\D+\b{wait['any']}\D+\b{wait['answered']}/"
                                                    rf"{wait['of']}\b", one)), "")
    live = next((one for one in plain if T.in_order(one, wake["member"], wake["run"], wake["relance"])), "")
    if done.returncode == 0 and dos and answered and waits and live and any(one in live for one in since):
        held("the band says the debts and the relance", f"{dos.split('│')[-1].strip()!r}; "
             f"{waits.split('│')[-1].strip()!r}; {live.split('│')[-1].strip()!r}")
    else:
        failures.append(f"  ✗ band                        rc={done.returncode} {dos!r} {answered} {waits!r} {live!r} "
                        f"{since} {plain[-30:]!r} {done.stderr[-300:]!r}")
    return 0
