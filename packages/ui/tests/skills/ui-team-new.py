"""Scenario `ui-team-new` -- `N` writes a team from a template, its fields composing their flags, and `ctrl+s` starts
the team it gives birth to, on the bench's `pp-team` witness replaying `team templates --json`:
- `N` on the Teams tab opens the form of the first template, read once from `templates --json`: its members, its
  ceremony, its limits
- what cannot play plays nothing and says why under the fields: no name; a member without its path -- a reason of its
  own each, never a command
- another template (`lead-reviewers`), its members changed -- each line `<name> <path>` --, a root chosen, a
  principal, the budget changed: `--member lead agents/l --member reviewer agents/r --root reviewer --principal pm
  --budget 10`, in that order in the witness's journal
- the ceremony of `supervisor-workers` left out: `--no-ceremony`
- `ctrl+s` gives birth to the team, then starts it by the path of `S` -- its first message, the line `all` edited in
  its profile --: `team new ram --template supervisor-workers`, then `team start ram --message go …`, in this order
  in the witness's journal
- a name typed, `enter` plays `team new ram --template supervisor-workers` -- no flag for a field left at its
  default --, as the witness's journal says it
- a refusal of `team new` goes to the remedy line by its code, the form open again on its values (its name)
- the help under `schedule` says the grammar by its examples -- `10s`, `2m`, `1h` (batch les-equipes-au-poste)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of an overlay

SIZE = ("--size", "140x110")             # the ten fields and the line under them in view
FIRST, LEAD = T.TEMPLATES[0], T.TEMPLATES[1]


def typed(text: str) -> str:
    """-> the keys that type `text`, a blank as `space`."""
    return ",".join("space" if char == " " else char for char in text)


def keys(*parts: str) -> str:
    return ",".join(parts)


NAMED = "N," + typed("ram")
NEW = f"team new ram --template {FIRST['template']}"
NAME = "N,x"
TO_LEAD = "shift+tab,down,down,enter"                       # from the name: the template list, its second line
MEMBERS = "tab,tab,end," + typed(" agents/l") + ",down,end," + typed(" agents/r")
ROOT = "tab,down,down,down,enter"                           # the blank, lead, reviewer
REST = "tab," + typed("pm") + ",tab,tab," + typed("10")
FIELDS = (f"team new x --template {LEAD['template']} --member lead agents/l --member reviewer agents/r "
          "--root reviewer --principal pm --budget 10")
NO_CEREMONY = "N,x,tab,tab,tab,tab,down,down,enter,enter"   # the ceremony's list, its second line: left out
START = NAMED + ",ctrl+s,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter,ctrl+s"
BORN = T.declaration("ram", [(one, f"agents/ram/{one}") for one in FIRST["members"]],
                     FIRST["limits"], started=False)       # what `team new` wrote
DECLARATIONS = {**T.DECLARATIONS, "ram": BORN}






def help_under(rows: list[str], name: str) -> str:
    """-> the help a form shows under the field `name`: the rows after its box, up to the next title or blank."""
    at = next((n for n, row in enumerate(rows) if row == P.field_title(name)), None)
    if at is None:
        return ""
    close = next((n for n in range(at, len(rows)) if rows[n].startswith("└")), None)
    if close is None:
        return ""
    found = []
    for row in rows[close + 1:]:
        if not row or row.startswith("[") or row == P.field_title(row.lower()) and row[:1].isupper():
            break
        found.append(row)
    return " ".join(found)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new", T.script(declarations=DECLARATIONS))

    # --- N, enter: the form of the first template, nothing to play without a name ---------------------------
    house.clear_journal()
    nameless = house.render("--render", "teams", *SIZE, "--press", "N,enter")
    rows = P.overlay_rows(nameless.stdout)
    reads = [one for one in house.journal_lines() if one.startswith("templates")]
    limits = FIRST["limits"]
    opened = {"template": P.field_of(rows, "template")[:1], "members": P.field_of(rows, "members"),
              "ceremony": P.field_of(rows, "ceremony"),
              **{key: P.field_of(rows, key) for key in ("budget", "launches", "timeout")}}
    if (nameless.returncode == 0 and opened["template"] and opened["template"][0].split()[0] == FIRST["template"]
            and opened["members"] == FIRST["members"] and opened["ceremony"] == [FIRST["ceremony"]]
            and all(opened[key] == [str(limits[key])] for key in limits) and reads == ["templates --json"]):
        held("N opens the form of a template", f"{FIRST['template']}, {', '.join(FIRST['members'])}, its ceremony, "
             f"{limits}; {reads}")
    else:
        failures.append(f"  ✗ form                        rc={nameless.returncode} {reads} {opened} {rows!r} "
                        f"{nameless.stderr[-400:]!r}")
    schedule_help = help_under(rows, "schedule")
    if nameless.returncode == 0 and all(one in schedule_help.split() for one in ("`10s`,", "`2m`,", "`1h`")):
        held("the help of schedule says its grammar", schedule_help[:100])
    else:
        failures.append(f"  ✗ schedule help               {schedule_help!r}")

    # --- a member without its path: nothing played, a reason of its own ---------------------------------------
    pressed = keys(NAME, TO_LEAD, MEMBERS, ROOT, REST)
    pathless = house.render("--render", "teams", *SIZE, "--press", keys(NAME, "tab,end," + typed(" agents/s"), "enter"))
    gaps = [P.under_fields(P.overlay_rows(one.stdout)) for one in (nameless, pathless)]
    if (nameless.returncode == 0 and pathless.returncode == 0 and house.gestures() == []
            and all(gaps) and gaps[0] != gaps[1] and not any("./pp" in one.stdout for one in (nameless, pathless))):
        held("what cannot play plays nothing and says why", "no name, a member without its path: no command, a "
             "reason of its own each under the fields; nothing in the witness's journal")
    else:
        failures.append(f"  ✗ nothing played              {house.gestures()} {gaps} "
                        f"{P.overlay_rows(nameless.stdout)[-8:]!r} {P.overlay_rows(pathless.stdout)[-8:]!r}")

    # --- played in one render: the fields changed, the ceremony left out, ctrl+s -----------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", keys(pressed, "enter", NO_CEREMONY, START))
    played = house.gestures()
    if done.returncode == 0 and played[:1] == [FIELDS]:
        held("a field changed composes its flag", FIELDS)
    else:
        failures.append(f"  ✗ fields                      {played} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")
    if done.returncode == 0 and played[1:2] == [f"team new x --template {FIRST['template']} --no-ceremony"]:
        held("the ceremony unchecked composes --no-ceremony", played[1])
    else:
        failures.append(f"  ✗ ceremony                    {played}")
    expected = [NEW, f"team start ram --message go --provider {T.D.PROVIDER} --model opus"]
    if done.returncode == 0 and played[2:] == expected:
        held("ctrl+s gives birth to the team, then starts it", f"{played[2:]}")
    else:
        failures.append(f"  ✗ new then start              rc={done.returncode} {played} {done.stdout[-1800:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- a name typed, enter: the command played, refused by its code, the form open again on its name -------
    house.use(T.script(declarations=DECLARATIONS,
                       answers={"new": {"rc": 2, "err": "pp-team: team-exists -- teams/ram/TEAM.md stands: a "
                                                        "template writes a new team, never over the owner's.\n"}}))
    house.clear_journal()
    refused = house.render("--render", "teams", *SIZE, "--press", NAMED + ",enter")
    named, remedy = P.field_of(P.overlay_rows(refused.stdout), "name"), T.remedy_of(refused)
    if refused.returncode == 0 and house.gestures() == [NEW]:
        held("the form plays its fields", f"{NEW!r}; no flag for a field left as it opened")
    else:
        failures.append(f"  ✗ played                      {house.gestures()} {refused.stdout[-1800:]!r}")
    if refused.returncode == 0 and "team-exists" in remedy.split() and named == ["ram"]:
        held("a refusal of team new is said, the form open again", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     {remedy!r} {named} {refused.stdout[-1500:]!r}")
    return 0
