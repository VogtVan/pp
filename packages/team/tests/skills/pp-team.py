"""packages/team/skills/pp-team -- the house's console verb `team`, as the operator drives it
(batch l-equipe-et-son-journal, 2026-10-01): `./pp help` lists `team` with its package; `./pp team`
without a verb says the usage in one line, exit 2; (batch l-attente) `./pp team stop <name> --kill`
on a team never started refuses `team-not-started` in one line, exit 2; (batch le-suivi-de-l-equipe)
the owner's inbox reaches the owner's own turn: a started team whose journal holds an `ask` to the
owner and a resolved task puts `review: T2 done · 1 question waiting for you` under
`INFORMATION — team-inbox` at the turn's first block; `team inbox review --seen` takes the result out of
the next exchange's line and keeps the question; a `post --reply` leaves no section; (batch le-partage-tire)
`./pp team responses review` on a team never started refuses `team-not-started` in one line, exit 2;
(batch le-calendrier) every call carries `PP_CRONTAB`, a throwaway file standing for the machine's
calendar; a calendar that cannot be written (`PP_CRONTAB` under a directory never made) says
`schedule not laid` on stderr and the team starts, rc 0, the journal opened; (batch
les-garde-fous) `./pp team snapshot review` on a team never started refuses `team-not-started`
in one line, exit 2; (batch le-rythme-et-les-entrees, rework; realigned by les-fichiers-sous-l-equipe,
2026-10-10) two `team start` of two teams that share an agent, raced five times: each team's documents
written whole in ITS directory, the bytes of their sources, nothing written at the shared agent, no
temporary left, nothing said kept (KC33).
"""
from __future__ import annotations

from tests.harness import SOURCE, cli, race


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("team-house", packages=("team",))
    ws = env.made.parent
    crontab = bench.temp() / "crontab"             # the bench's calendar, never the machine's

    def call(*args: str):
        return cli(env.engine, *args, cwd=ws, env={"PP_CRONTAB": str(crontab)})

    # --- the console carries the verb ------------------------------------------------------
    helped = call("help")
    if helped.returncode == 0 and "./pp team" in helped.stdout and "(team)" in helped.stdout:
        held("the console carries the verb", "./pp help lists `./pp team (team) …`")
    else:
        failures.append(f"  ✗ console verb                rc={helped.returncode} {helped.stdout[-300:]!r}")

    # --- a bare call says the usage in one line -------------------------------------------------
    bare = call("team")
    said = (bare.stderr + bare.stdout).strip()
    if bare.returncode == 2 and "usage" in said.lower() and len(said.splitlines()) == 1:
        held("a bare call says the usage", "./pp team: one line, exit 2")
    else:
        failures.append(f"  ✗ bare call                   rc={bare.returncode} {said[-300:]!r}")

    # --- tick without a team's name says the usage in one line ----------------------------------
    bare_tick = call("team", "tick")
    said = (bare_tick.stderr + bare_tick.stdout).strip()
    if bare_tick.returncode == 2 and "usage" in said.lower() and len(said.splitlines()) == 1:
        held("tick without a name says the usage", "./pp team tick: one line, exit 2")
    else:
        failures.append(f"  ✗ bare tick                   rc={bare_tick.returncode} {said[-300:]!r}")

    # --- stop --kill on a team never started refuses by its name ----------------------------------
    (ws / "teams" / "review").mkdir(parents=True, exist_ok=True)
    (ws / "teams" / "review" / "TEAM.md").write_text("---\nagents: |\n  m m\nroot: m\n---\n", encoding="utf-8")
    killed = call("team", "stop", "review", "--kill")
    said = (killed.stderr + killed.stdout).strip()
    if killed.returncode == 2 and "team-not-started" in said and len(said.splitlines()) == 1 and "usage" not in said:
        held("stop --kill refuses a team never started", "./pp team stop review --kill: team-not-started, one line, exit 2")
    else:
        failures.append(f"  ✗ stop --kill                 rc={killed.returncode} {said[-300:]!r}")

    # --- snapshot on a team never started refuses by its name ---------------------------------------
    unsnapped = call("team", "snapshot", "review")
    said = (unsnapped.stderr + unsnapped.stdout).strip()
    if unsnapped.returncode == 2 and "team-not-started" in said and len(said.splitlines()) == 1 and "usage" not in said:
        held("snapshot refuses a team never started", "./pp team snapshot review: team-not-started, one line, exit 2")
    else:
        failures.append(f"  ✗ snapshot refusal            rc={unsnapped.returncode} {said[-300:]!r}")

    # --- responses on a team never started refuses by its name -------------------------------------
    unread = call("team", "responses", "review")
    said = (unread.stderr + unread.stdout).strip()
    if unread.returncode == 2 and "team-not-started" in said and len(said.splitlines()) == 1 and "usage" not in said:
        held("responses refuses a team never started", "./pp team responses review: team-not-started, one line, exit 2")
    else:
        failures.append(f"  ✗ responses                   rc={unread.returncode} {said[-300:]!r}")

    # --- the owner's inbox reaches the owner's own turn ---------------------------------------------
    import json
    from conductor import render
    from tests.harness import bench_key
    started = call("team", "start", "review", "--message", "review it", "--no-tick")
    journal = env.made / ".sys" / "records" / "teams" / "review" / "journal.jsonl"
    owner = json.loads(journal.read_text(encoding="utf-8").splitlines()[0]).get("owner") if journal.is_file() else "?"
    with journal.open("a", encoding="utf-8") as handle:          # the bench's hand on a disposable journal
        for offset, line in enumerate((
                {"kind": "post", "task": "T1", "from": "m", "to": owner, "verb": "ask", "text": "which branch?"},
                {"kind": "task", "task": "T2", "from": owner, "to": "m", "text": "and this"},
                {"kind": "post", "task": "T2", "from": owner, "to": "m", "verb": "do", "text": "and this"},
                {"kind": "done", "task": "T2", "result": "fine"}), 4):
            handle.write(json.dumps({"at": "2026-10-01T20:00:00+00:00", "id": offset, "team": "review", **line}) + "\n")
    from tests.harness import na_proof
    opener = env.conductor()
    opener.start(opener.boot("BOOT.md"))
    key = bench_key(env.made)

    def parked(block) -> None:
        """Takes the exchange to its frontier: the response steps closed bare, the proofs n/a."""
        for _ in range(8):
            if block.wait:
                return
            block = env.conductor(key).submit(na_proof(block) if block.judged else "")

    def boxed() -> tuple[str, dict]:
        """-> the console's inbox, its lines and the review team's object."""
        lines = call("team", "inbox").stdout.strip()
        objects = [json.loads(one) for one in call("team", "inbox", "--json").stdout.splitlines() if one.strip()]
        return lines, next((one for one in objects if one.get("team") == "review"), {})

    box_1, object_1 = boxed()
    first = env.conductor(key).submit("")                # the capabilities said: the turn opens
    booted = render(first)
    parked(first)
    seen = call("team", "inbox", "review", "--seen")
    box_2, object_2 = boxed()
    next_one = env.conductor(key).submit("what now?")
    second = render(next_one)
    parked(next_one)
    replied = call("team", "post", "review", "--task", "T1", "--reply", "4", "--message", "main", "--no-tick")
    third = render(env.conductor(key).submit("and now?"))
    plain = call("team", "inbox")

    def section(shown: str) -> str:
        at = shown.find("▌ INFORMATION — team-inbox")
        if at < 0:
            return ""
        rest = shown[at:]
        end = rest.find("\n▌ ", 1)
        return rest if end < 0 else rest[:end]

    first_line = section(booted)
    if (started.returncode == 0 and box_1 and box_1 in first_line
            and [one.get("task") for one in object_1.get("done") or []] == ["T2"]
            and [one.get("id") for one in object_1.get("questions") or []] == [4]
            and seen.returncode == 0 and box_2 and box_2 in section(second) and box_2 != box_1
            and object_2.get("done") == [] and [one.get("id") for one in object_2.get("questions") or []] == [4]
            and replied.returncode == 0 and section(third) == ""
            and plain.returncode == 0 and plain.stdout == ""
            and "inbox-seen" in journal.read_text(encoding="utf-8")):
        held("the owner's inbox reaches the owner's turn", "the turn's first block carries the console's `team inbox` "
             "(T2 done, the question #4); after --seen the result leaves and the question stays; after the reply no section")
    else:
        failures.append(f"  ✗ owner inbox                 rc={started.returncode}/{seen.returncode}/{replied.returncode} "
                        f"first={first_line[:160]!r} box={box_1!r}/{object_1} second={section(second)[:160]!r} "
                        f"box={box_2!r}/{object_2} third={section(third)[:80]!r} "
                        f"plain={plain.stdout!r} {started.stderr[-200:]!r} {seen.stderr[-200:]!r}")

    # --- a calendar that cannot be written is said, the team starts ---------------------------------
    (ws / "teams" / "late").mkdir(parents=True, exist_ok=True)
    (ws / "teams" / "late" / "TEAM.md").write_text("---\nagents: |\n  m m\nroot: m\n---\n", encoding="utf-8")
    nowhere = bench.temp() / "gone" / "crontab"    # the parent directory is never made
    laidless = cli(env.engine, "team", "start", "late", "--message", "start anyway", "--no-tick",
                   cwd=ws, env={"PP_CRONTAB": str(nowhere)})
    journal_late = env.made / ".sys" / "records" / "teams" / "late" / "journal.jsonl"
    started_late = journal_late.is_file() and "team-started" in journal_late.read_text(encoding="utf-8")
    faced = cli(env.engine, "team", "status", "late", "--json", cwd=ws, env={"PP_CRONTAB": str(nowhere)})
    schedule = (json.loads(faced.stdout or "{}").get("schedule") or {}) if faced.returncode == 0 else {}
    if (laidless.returncode == 0 and laidless.stderr.strip() and started_late
            and schedule.get("laid") is False and not nowhere.exists()):
        held("an unwritable calendar is said, the team starts", "PP_CRONTAB under a directory never made: "
             "team start late rc 0, said on stderr, the journal opened, the face's schedule not laid, nothing written")
    else:
        failures.append(f"  ✗ schedule not laid           rc={laidless.returncode} started={started_late} schedule={schedule} "
                        f"laid={nowhere.exists()} {laidless.stderr[-300:]!r} {laidless.stdout[-200:]!r}")

    # --- two starts that lay one agent's shared entry files at once (KC33) --------------------------
    procs = env.made.parent / "agents" / "sh" / env.made.name / "procs"
    added = call("agent", "add", "agents/sh")
    procs.mkdir(parents=True, exist_ok=True)
    (procs / "WORK.md").write_text("---\nproc: |\n  WORK\n---\n# WORK\n\nDo it.\n", encoding="utf-8")
    here = SOURCE / "packages" / "team" / "skills" / "pp-team"
    at_agent = sorted(one.name for one in procs.iterdir())
    rounds = []
    for n in range(5):
        names = [f"share{n}a", f"share{n}b"]
        shared = {ws / "teams" / name / "TEAM-IDLE.md": here / "agent-idle.md" for name in names}
        for name in names:
            (ws / "teams" / name).mkdir(parents=True, exist_ok=True)
            (ws / "teams" / name / "TEAM.md").write_text(
                f"---\nagents: |\n  w{name} agents/sh\nroot: w{name}\nentries: |\n  do -> WORK.md\n"
                "schedule: off\n---\n", encoding="utf-8")
        both = race(env.engine, [["team", "start", name, "--message", "x", "--no-tick"] for name in names],
                    cwd=ws, env={"PP_CRONTAB": str(crontab)})
        stray = sorted(one.name for one in [*procs.iterdir(), *(ws / "teams" / names[0]).iterdir(),
                                            *(ws / "teams" / names[1]).iterdir()] if one.name.startswith("."))
        rounds.append(([one.returncode for one in both],
                       all((ws / "teams" / name / f"TEAM-{name}.md").is_file() for name in names)
                       and sorted(one.name for one in procs.iterdir()) == at_agent
                       and not (procs.parent / "skills" / "team-entry").exists(),
                       all(target.is_file() and target.read_bytes() == source.read_bytes()
                           for target, source in shared.items()),
                       stray, any("kept" in one.stderr for one in both)))
    if added.returncode == 0 and all(rc == [0, 0] and laid and whole and not stray and not kept
                                     for rc, laid, whole, stray, kept in rounds):
        held("two starts that share an agent write their own directories", "five races of two team starts "
             "sharing agents/sh: each team's TEAM-<name>.md and TEAM-IDLE.md whole in its directory, the "
             "bytes of their sources, nothing written at agents/sh, no temporary left, nothing said kept -- KC33")
    else:
        failures.append(f"  ✗ shared entries raced        add={added.returncode} {rounds}")
    return 0
