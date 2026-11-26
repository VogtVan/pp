"""Scenario `ui-team-chat` -- the dialogue under the root of a team (plan travail-en-equipe, batch le-dialogue-a-racine),
on the bench's witnesses: `pp-team` says the declaration of `core-review` at `teams/core-review/TEAM.md` -- a folder
of the team's name, as `pp-team` keeps every team --, `pp-chat` echoes `--documents` in its `ready` and `opened` as the verb does, and its
`status` gives each run its `documents` in the frozen form of `agent status --json` (an absolute path or null):
- `C` on `reviewer` reads `team declaration core-review --json` and pushes the overlay of a new run's parameters
  (batch les-gestes-du-membre, s.1515), the team's root said in its title (`◈ core-review`), prefilled with the
  agent's provider: nothing is launched before `enter`, and `escape` launches nothing
- `enter` there launches `agent chat agents/reviewer --json --provider <its provider> --documents
  <house>/teams/core-review` -- the folder of the declaration's `path`, resolved from the house --, a conversation
  like any other: not read only, no gesture of `team`; the run opened says that root, and its tab carries
  `◈ core-review`, the name of the root's folder
- a member whose row in `team status --json` carries a `vector` (an opaque `<family>:<id>`): `enter` launches the
  same conversation with `--vector <that string>` after the root -- the post passes the string, it composes none;
  a member without a `vector` launches no `--vector`
- the Agents tab ALONE -- no `C`, no `e` before, no declaration read -- marks the same run `◈ core-review` in the list
  of the runs; a run under another root bears the name of its folder; a run without a root bears nothing: the mark is
  the run's own, no cache of the post
- a run opened from the Agents tab -- the Dialogue's own way -- launches no `--documents` and carries no mark
(a new scenario: `ui-team-member`, the home of the member's gestures, stands at 17 s of the 22 rule 10 allows)
Its sibling, cut by case: `ui-team-chat-house` (a member the house plays).
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

ROOTED = "◈"                                       # the glyph of a run under a root (`palette.ROOTED`)
SIZE = ("--size", "150x40")
OPENING = [{"kind": "ready"}, {"kind": "opened", "exchange": 1}, {"kind": "waiting"}]
CHAT = "3,tab,down,C"                              # the members, `reviewer` under the cursor, `C`
SETTLE = "rest:1"                                  # time enough for a launch the post would play unasked


def head_of(text: str) -> str:
    """-> the head of a capture: the header, the post's tabs and the dialogue's own -- where a tab's title stands."""
    return "\n".join(text.split("\n")[:5])


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-chat")
    root = str(house.ws.resolve() / "teams" / "core-review")    # the bench's expectation, never the post's
    elsewhere = str(house.ws.resolve() / "notes")
    runs = [{**one, "documents": None} for one in T.MEMBER_STATUS if "run" in one]
    status = runs + [{**runs[1], "run": "w00001", "first_message": "", "documents": root},
                     {**runs[1], "run": "w00002", "first_message": "", "documents": elsewhere},
                     T.MEMBER_STATUS[-1]]
    house.use_chat({"agents/reviewer": status}, opening=OPENING)

    # --- C on a member: the overlay of the run's parameters, nothing launched before enter ------------------
    house.clear_journal()
    P.forget(house.made)
    done = house.render("--render", "teams", *SIZE, "--press", f"{CHAT},{SETTLE}")
    opens = [one for one in house.chat_lines() if one.startswith("open ")]
    if (done.returncode == 0 and opens == [] and f"{ROOTED} core-review" in done.stdout
            and "declaration core-review" in house.journal_lines()):
        held("C pushes the overlay of the run's parameters", f"the root said in its title ({ROOTED} core-review); "
             "nothing launched")
    else:
        failures.append(f"  ✗ C overlay                   rc={done.returncode} {opens} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-500:]!r}")

    # --- escape launches nothing -----------------------------------------------------------------------
    house.clear_journal()
    P.forget(house.made)
    done = house.render("--render", "teams", *SIZE, "--press", f"{CHAT},{SETTLE},escape")
    opens = [one for one in house.chat_lines() if one.startswith("open ")]
    if done.returncode == 0 and opens == [] and ROOTED not in done.stdout:
        held("escape on the overlay launches nothing", "no agent chat, the overlay closed")
    else:
        failures.append(f"  ✗ C escape                    rc={done.returncode} {opens} {done.stdout[-1500:]!r}")

    # --- enter: the dialogue under the team's root, with the parameters chosen ----------------------------
    house.clear_journal()
    P.forget(house.made)
    done = house.render("--render", "dialogue", *SIZE, "--press", f"{CHAT},{SETTLE},ctrl+enter", "--wait", "opened")
    opens = [one for one in house.chat_lines() if one.startswith("open ")]
    tabs = head_of(done.stdout)
    if (done.returncode == 0 and opens == [f"open agents/reviewer --provider {P.PROVIDER} --documents {root}"]
            and "--vector" not in opens[0] and "declaration core-review" in house.journal_lines() and house.gestures() == []
            and f"{ROOTED} core-review" in tabs and "read only" not in done.stdout):
        held("enter opens the dialogue under the team's root", f"{opens[0]}; the tab carries {ROOTED} core-review; "
             "the declaration read, no gesture of team")
    else:
        failures.append(f"  ✗ C enter                     rc={done.returncode} {opens} {house.journal_lines()} "
                        f"{tabs!r} {done.stdout[-1500:]!r} {done.stderr[-500:]!r}")

    # --- a member whose row carries a vector: the conversation names it, as the face says it ----------------
    vector = "crew:core-review/reviewer"            # opaque: the post passes the string the face gives
    vectored = {**T.CORE, "members": [T.CORE["members"][0], {**T.CORE["members"][1], "vector": vector}]}
    house.use(T.script(states={**T.script()["states"], "core-review": [vectored]}))
    house.clear_journal()
    P.forget(house.made)
    done = house.render("--render", "dialogue", *SIZE, "--press", f"{CHAT},{SETTLE},ctrl+enter", "--wait", "opened")
    opens = [one for one in house.chat_lines() if one.startswith("open ")]
    house.use(T.script())
    if done.returncode == 0 and opens == [f"open agents/reviewer --provider {P.PROVIDER} --documents {root} --vector {vector}"]:
        held("enter passes the member's vector", f"{opens[0]}; without a vector on the row, no --vector (the case above)")
    else:
        failures.append(f"  ✗ C vector                    rc={done.returncode} {opens} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-500:]!r}")

    # --- the Agents tab alone marks the same run; another root by its folder; no root, nothing -------------
    house.clear_journal()
    P.forget(house.made)
    done = house.render("--render", "agents", *SIZE, "--press", "2,enter")
    rows = done.stdout.split("\n")
    row = {key: next((one for one in rows if key in one), "") for key in ("w00001", "w00002", "a00007")}
    if (done.returncode == 0 and f"{ROOTED} core-review" in row["w00001"] and f"{ROOTED} notes" in row["w00002"]
            and row["a00007"] and ROOTED not in row["a00007"]
            and not any(one.startswith("declaration") for one in house.journal_lines())):
        held("the Agents tab alone marks a run under a root", f"w00001 {ROOTED} core-review, w00002 {ROOTED} notes, "
             "a00007 nothing; no declaration read")
    else:
        failures.append(f"  ✗ agents                      rc={done.returncode} {row} {done.stdout[-2000:]!r} "
                        f"{done.stderr[-500:]!r}")

    # --- the Dialogue's own way: no root, no mark ----------------------------------------------------------
    house.use_chat({"agents/reviewer": status}, opening=OPENING, run="w00003")
    house.clear_journal()
    P.forget(house.made)
    done = house.render("--render", "dialogue", *SIZE, "--press", "2,n,ctrl+enter", "--wait", "opened")
    opens = [one for one in house.chat_lines() if one.startswith("open ")]
    tabs = head_of(done.stdout)
    if (done.returncode == 0 and len(opens) == 1 and "--documents" not in opens[0] and "w00003" in done.stdout
            and ROOTED not in tabs):
        held("the Dialogue opens without a root", f"{opens[0]}; no mark on its tab")
    else:
        failures.append(f"  ✗ dialogue                    rc={done.returncode} {opens} {tabs!r} {done.stdout[-1500:]!r}")
    return 0
