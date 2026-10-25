"""Scenario `ui-team-new` -- `N` writes a team from a template, its fields composing their flags, and `ctrl+s` starts
the team it gives birth to, on the bench's `pp-team` witness replaying `team templates --json`:
- `N` on the Teams tab opens the form of the first template, read once from `templates --json`: its members, its
  ceremony, its limits
- what cannot play plays nothing and says why, where the command stands otherwise: no name; a member without its
  path -- a reason of its own each
- another template (`lead-reviewers`), its members changed -- each line `<name> <path>` --, a root chosen, a
  principal, the budget changed: `--member lead agents/l --member reviewer agents/r --root reviewer --principal pm
  --budget 10`, in the order the command shows, played word for word
- the ceremony of `supervisor-workers` left out: `--no-ceremony`
- `ctrl+s` gives birth to the team, then starts it by the path of `S` -- its first message, the line `all` edited in
  its profile --: `team new ram --template supervisor-workers`, then `team start ram --message go …`, in this order
  in the witness's journal
- a name typed, the command under the fields is `./pp team new ram --template supervisor-workers` -- no flag for a
  field left at its default --, and `enter` plays it word for word
- a refusal of `team new` goes to the remedy line by its code, the form open again on its values
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of an overlay

SIZE = ("--size", "140x110")             # the ten fields and the command under them in view
FIRST, LEAD = T.TEMPLATES[0], T.TEMPLATES[1]


def typed(text: str) -> str:
    """-> the keys that type `text`, a blank as `space`."""
    return ",".join("space" if char == " " else char for char in text)


def keys(*parts: str) -> str:
    return ",".join(parts)


NAMED = "N," + typed("ram")
NEW = f"./pp team new ram --template {FIRST['template']}"
NAME = "N,x"
TO_LEAD = "shift+tab,down,down,enter"                       # from the name: the template list, its second line
MEMBERS = "tab,tab,end," + typed(" agents/l") + ",down,end," + typed(" agents/r")
ROOT = "tab,down,down,down,enter"                           # the blank, lead, reviewer
REST = "tab," + typed("pm") + ",tab,tab," + typed("10")
FIELDS = (f"./pp team new x --template {LEAD['template']} --member lead agents/l --member reviewer agents/r "
          "--root reviewer --principal pm --budget 10")
NO_CEREMONY = "N,x,tab,tab,tab,tab,down,down,enter,enter"   # the ceremony's list, its second line: left out
START = NAMED + ",ctrl+s,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter,ctrl+s"
BORN = T.declaration("ram", [(one, f"agents/ram/{one}") for one in FIRST["members"]],
                     FIRST["limits"], started=False)       # what `team new` wrote
DECLARATIONS = {**T.DECLARATIONS, "ram": BORN}






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

    # --- another template, its fields changed: the command shown; a member without its path -----------------
    pressed = keys(NAME, TO_LEAD, MEMBERS, ROOT, REST)
    composing = house.render("--render", "teams", *SIZE, "--press", pressed)
    composed = T.preview_folded(composing, "./pp team new")
    pathless = house.render("--render", "teams", *SIZE, "--press", keys(NAME, "tab,end," + typed(" agents/s"), "enter"))
    command = P.under_fields(P.overlay_rows(composing.stdout))
    gaps = [P.under_fields(P.overlay_rows(one.stdout)) for one in (nameless, pathless)]
    if (nameless.returncode == 0 and pathless.returncode == 0 and house.gestures() == []
            and " ".join(command) == composed and all(gaps) and gaps[0] != gaps[1]
            and not any(row.startswith("./pp") for gap in gaps for row in gap)):
        held("what cannot play plays nothing and says why", "no name, a member without its path: no command, a "
             "reason of its own each where the command stands; nothing in the witness's journal")
    else:
        failures.append(f"  ✗ nothing played              {house.gestures()} {command} {gaps} "
                        f"{nameless.stdout[-1200:]!r} {pathless.stdout[-1200:]!r}")

    # --- played in one render: the fields changed, the ceremony left out, ctrl+s -----------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", keys(pressed, "enter", NO_CEREMONY, START))
    played = house.gestures()
    if composing.returncode == 0 and done.returncode == 0 and composed == FIELDS and played[:1] == [FIELDS[5:]]:
        held("a field changed composes its flag", FIELDS)
    else:
        failures.append(f"  ✗ fields                      {composed!r} {played} {composing.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")
    if done.returncode == 0 and played[1:2] == [f"team new x --template {FIRST['template']} --no-ceremony"]:
        held("the ceremony unchecked composes --no-ceremony", played[1])
    else:
        failures.append(f"  ✗ ceremony                    {played}")
    expected = [NEW[5:], f"team start ram --message go --provider {T.D.PROVIDER} --model opus"]
    if done.returncode == 0 and played[2:] == expected:
        held("ctrl+s gives birth to the team, then starts it", f"{played[2:]}")
    else:
        failures.append(f"  ✗ new then start              rc={done.returncode} {played} {done.stdout[-1800:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- a name typed, enter: the command shown played as shown, refused by its code, the form open again ----
    house.use(T.script(declarations=DECLARATIONS,
                       answers={"new": {"rc": 2, "err": "pp-team: team-exists -- teams/ram/TEAM.md stands: a "
                                                        "template writes a new team, never over the owner's.\n"}}))
    house.clear_journal()
    refused = house.render("--render", "teams", *SIZE, "--press", NAMED + ",enter")
    preview, remedy = T.preview_in(refused, "./pp team new"), T.remedy_of(refused)
    if refused.returncode == 0 and preview == NEW and house.gestures() == [NEW[5:]]:
        held("the form plays what it shows", f"{preview!r}, played as shown; no flag for a field left as it opened")
    else:
        failures.append(f"  ✗ played                      {preview!r} {house.gestures()} {refused.stdout[-1800:]!r}")
    if refused.returncode == 0 and "team-exists" in remedy.split() and preview == NEW:
        held("a refusal of team new is said, the form open again", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     {remedy!r} {refused.stdout[-1500:]!r}")
    return 0
