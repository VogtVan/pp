"""Scenario `ui-team-chat-house` -- a member the house plays (`path: "."`, team 1.36.0), on the bench's witnesses: the
face of `core-review` gives it `keeper`, its agent `.`; `agent list` names the house; cut by case from `ui-team-chat`:
- its cell `agent` on the Teams tab is the word the Agents tab gives `.` -- read there, never `.` --; `C` on it launches
  `agent chat . --json --provider <its provider> --documents <house>/teams/core-review --vector <its vector>`, a run of
  the house under the team's root; the model of a sequence (`model.teams`, from the source) gives it a column of its
  name, out of the principals
- the table of the season of `veille` (`S`, never started; `keeper` among its members at `.`): the cell `agent` of
  keeper's line is that same word of the Agents tab
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")
S = support(__file__, "tasks_sequence")

SIZE = ("--size", "150x40")
OPENING = [{"kind": "ready"}, {"kind": "opened", "exchange": 1}, {"kind": "waiting"}]
SETTLE = "rest:1"                                  # time enough for the overlay of the run's parameters
VEILLE = T.declaration("veille", [("scout", "agents/scout"), ("keeper", ".")], {"budget": 3.0}, started=False)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-chat-house")
    root = str(house.ws.resolve() / "teams" / "core-review")    # the bench's expectation, never the post's
    runs = [{**one, "documents": None} for one in T.MEMBER_STATUS if "run" in one]
    status = runs + [T.MEMBER_STATUS[-1]]

    # --- a member the house plays: the Agents tab's word, C under the team's root, a column of its own -------------
    keeper = {**T.CORE["members"][1], "member": "keeper", "path": ".", "run": "h00001", "how": "ended", "since": None,
              "tasks": [], "pending": [], "vector": "team-member:core-review/keeper"}
    homed = {**T.CORE, "members": [*T.CORE["members"], keeper]}
    house.use(T.script(states={**T.script()["states"], "core-review": [homed]},
                       declarations={**T.DECLARATIONS, "veille": VEILLE}))
    house.chat_faces["list"] = [{"agent": ".", "runs": 1, "running": 0, "responses": 1}, *T.MEMBER_FACES["list"]]
    house.use_chat({"agents/reviewer": status, ".": [{**runs[0], "agent": ".", "run": "h00001", "documents": root},
                                                     {**T.MEMBER_STATUS[-1], "agent": "."}]}, opening=OPENING)
    house.clear_journal()
    P.forget(house.made)
    agents = house.render("--render", "agents", *SIZE, "--press",       # C on keeper launches, then the Agents
                          f"3,tab,down,down,C,{SETTLE},ctrl+enter,wait:opened,2")   # tab: the word it gives `.`
    opens = [one for one in house.chat_lines() if one.startswith("open ")]
    table = [T.cells_of(one) for one in agents.stdout.split("\n")]
    at = next((n for n, cells in enumerate(table) if cells[:1] == ["agent"]), None)      # the header of the agents
    word = ([cells[0] for cells in table[at + 1:] if len(cells) == len(table[at]) and cells[0] != "agents/reviewer"]
            if at is not None else [])                                          # the first cell of the line of `.`
    members = house.render("--render", "teams", *SIZE, "--press", "3")
    cell = T.cells_by_name(members.stdout.split("\n"), "member", "keeper").get("agent")
    teams = S.model()
    lines = [teams.ThreadLine.read(one) for one in (
        T.event("09:20:00", "task", 70, task="T9", **{"from": "house"}, to="keeper", text="keep the house"),
        T.event("09:20:00", "post", 71, task="T9", **{"from": "house"}, to="keeper", verb="do", text="keep it"),
        T.event("09:21:00", "wake-ended", 72, tag="keeper-T9-1", agent="keeper", run="h00001", launch=1, cost=0.01))]
    sequence = teams.with_roles(teams.sequence_of(lines), teams.TeamState.read(homed))
    if (agents.returncode == 0 and members.returncode == 0 and len(word) == 1 and cell == word[0] and cell != "."
            and opens == [f"open . --provider {P.PROVIDER} --documents {root} --vector {keeper['vector']}"]
            and house.gestures() == [] and sequence.columns == ("house", "keeper")
            and "keeper" not in sequence.principals):
        held("a member the house plays", f"its cell agent `{cell}`, the Agents tab's word for `.`; {opens[0]}; its "
             f"sequence's columns {sequence.columns}, keeper out of the principals {sequence.principals}")
    else:
        failures.append(f"  ✗ the house a member          rc={agents.returncode}/{members.returncode} "
                        f"word={word} cell={cell!r} opens={opens} columns={sequence.columns} "
                        f"principals={sequence.principals} {agents.stdout[-1200:]!r} {agents.stderr[-400:]!r}")

    # --- the table of the season: keeper's agent by the same word ------------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"down,down,S,{T.TO_LINES},boxes")
    line = next((cells for cells in (T.cells_of(one) for one in T.form_rows(shown.stdout)) if cells[:1] == ["keeper"]),
                [])
    if shown.returncode == 0 and word and line[1:2] == word and house.gestures() == []:
        held("the season names the house by the same word", f"keeper's line {line}: its agent `{line[1]}`")
    else:
        failures.append(f"  ✗ the season of the house      rc={shown.returncode} word={word} line={line} "
                        f"{shown.stdout[-2000:]!r} {shown.stderr[-400:]!r}")
    return 0
