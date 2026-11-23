"""Scenario `ui-tasks-sequence` -- the SEQUENCE of the task under the cursor on the Tasks tab, at rest, on ONE house
of the bench's `pp-team` witness (`_tasks_sequence`):
- the model of a sequence (`model.teams.sequence_of`, loaded from the source): T3's thread gives its principal's column
  first, then its members in the order they appear, one row per post with its pair (from, to), the wake-up joined by
  its tag; centred on `reviewer`, its column first and the rows it sends, receives or wakes in alone; the model says
  the task's birth
- the band of a task a wake-up plays: its detail, then its SEQUENCE and no result -- T3's thread read once the cursor
  rested on it (`log core-review T3`), one row per post in the order of their `id`
- the footer says the keys of where the focus stands: none of the sequence's (`w`) while the focus is on the tasks
- the parts of the columns: the model reads each member's role keys at the face (`members[].roles`, team 1.35.16) and
  gives the sequence those of its members and the team's owner and principals (`with_roles`); the head drawn by
  `palette.sequence_head` holds a line under the names when a column has a part -- under `lead`, a member with keys,
  and `house`, a principal, none under `reviewer`, a member without --, five lines then, four without any part; the
  team itself a principal: T2, the task its ceremony gave (`from` the team), has the part under its first column; the
  threads of a pane (`panes.sequence.Threads`) read the face of a team by the reading handed to them at their birth
  (`face=`), the pane itself holding none; on
  the Tasks tab, the head of T3's sequence drawn from the face of `core-review` holds that line, its five lines in
  sight -- its structure read, never its words
The time scale of the rows is `ui-tasks-sequence-scale`'s, the sequence followed live `ui-tasks-sequence-live`'s.
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks_sequence")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.house(bench, "ui-tasks-sequence")
    posts = [one for one in T.T3_LOG if one["event"] == "post"]

    # --- the model of a sequence ------------------------------------------------------------------------
    teams = S.model()
    lines = [teams.ThreadLine.read(one) for one in T.T3_LOG]
    whole, centred = teams.sequence_of(lines), teams.sequence_of(lines, "reviewer")
    pairs = [(one.source, one.target) for one in whole.rows if one.kind == "post"]
    wakes = [(one.source, one.run, one.over) for one in whole.rows if one.kind == "wake"]
    mine = [one.id for one in centred.rows]
    if (whole.columns == ("house", "lead", "reviewer") and pairs == [(one["from"], one["to"]) for one in posts]
            and whole.start == T.T3_LOG[0]["at"]
            and wakes == [("reviewer", "a01389", True)] and centred.columns == ("reviewer", "lead", "house")
            and mine == [one["id"] for one in T.T3_LOG if "reviewer" in (one.get("from"), one.get("to"), one.get("agent"))]):
        held("the model of a sequence", f"columns {whole.columns}, pairs {pairs}, wake {wakes}; centred on reviewer "
             f"{centred.columns}, rows {mine}")
    else:
        failures.append(f"  ✗ model                       {whole} {centred}")

    # --- the band of a task a wake-up plays: its sequence, no result ------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", *S.SIZE)
    reads = [one for one in house.journal_lines() if one == "log core-review T3"]
    regions = S.inner_of(house.render("--render", "tasks", *S.SIZE, "--regions").stdout)
    if (done.returncode == 0 and S.heads_of(done.stdout) == [one["id"] for one in posts] and len(reads) == 1
            and "tasks-sequence" in regions and "tasks-result" not in regions and "tasks-live" not in regions):
        held("a task a wake-up plays shows its sequence, no result", f"rows {S.heads_of(done.stdout)}, the thread "
             f"read {len(reads)} time; the band shows {sorted(regions)}")
    else:
        failures.append(f"  ✗ sequence                    rc={done.returncode} {S.heads_of(done.stdout)} {reads} "
                        f"{sorted(regions)} {done.stdout[-2400:]!r} {done.stderr[-400:]!r}")
    keys = P.keys_of(done.stdout)
    if "[w]" not in keys:
        held("the footer says no key of the sequence before it is focused", "`w` absent on the tasks")
    else:
        failures.append(f"  ✗ keys of the tasks           {keys!r}")

    # --- the parts of the columns: the model, the head, the Tasks tab -------------------------------------------
    face = {**T.LIVE_CORE, "members": [{**one, "roles": S.ROLES.get(one["member"], [])} for one in T.LIVE_CORE["members"]]}
    state = teams.TeamState.read(face)
    with_parts = teams.with_roles(whole, state) if hasattr(teams, "with_roles") else whole
    keys_read = {one.member: getattr(one, "roles", None) for one in state.members}
    if (keys_read == {"lead": ("workers", "reviewers"), "reviewer": ()}
            and getattr(with_parts, "roles", None) == (("lead", ("workers", "reviewers")),)
            and getattr(with_parts, "principals", None) == ("house", "pm", T.CORE["team"])
            and with_parts.rows == whole.rows):
        held("the model gives the columns their parts", f"roles {keys_read}; the sequence's {with_parts.roles}, "
             f"principals {with_parts.principals}")
    else:
        failures.append(f"  ✗ parts of the model          {keys_read} {getattr(with_parts, 'roles', None)} "
                        f"{getattr(with_parts, 'principals', None)}")
    drawn, played = S.head_probe(bench, face, T.T2_LOG)
    bare, parts, team = drawn.get("bare") or {}, drawn.get("parts") or {}, drawn.get("team") or {}
    if (bare.get("lines") == 4 and parts.get("lines") == 5
            and parts.get("under") == {"house": True, "lead": True, "reviewer": False}):
        held("the head holds the line of the parts", f"4 lines without a part, 5 with; under {parts.get('under')}")
    else:
        failures.append(f"  ✗ head of the parts           {drawn} {played.stderr[-600:]!r}")
    if team.get("lines") == 5 and team.get("under") == {T.CORE["team"]: True, "lead": True, "reviewer": False}:
        held("the team is a principal of its ceremony's task", f"T2 from {T.CORE['team']}: under {team.get('under')}")
    else:
        failures.append(f"  ✗ the team as a principal     {team} {played.stderr[-600:]!r}")
    read, played = S.threads_probe(bench, face, T.T3_LOG)
    if (read.get("roles") == [["lead", ["workers", "reviewers"]]]
            and read.get("principals") == ["house", "pm", T.CORE["team"]]):
        held("the threads read the face handed to them", f"on a pane holding no face: roles {read['roles']}, "
             f"principals {read['principals']}")
    else:
        failures.append(f"  ✗ the face handed to threads  {read} {played.stderr[-600:]!r}")
    parted = S.house(bench, "ui-tasks-sequence-parts", S.ROLES).render("--render", "tasks", *S.SIZE)
    head, xs = S.head_of(parted.stdout)
    said = [S.under(head[1], x) for x in xs] if len(head) > 1 else []
    if parted.returncode == 0 and len(head) == 5 and said == [True, True, False]:
        held("the Tasks tab draws the parts in T3's head", f"5 lines in sight, the parts under the columns {said}")
    else:
        failures.append(f"  ✗ parts on the Tasks tab      rc={parted.returncode} head={head} xs={xs} "
                        f"{parted.stderr[-400:]!r}")

    return 0
