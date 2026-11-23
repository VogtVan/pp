"""Scenario `team-declare-existing` -- 9 case(s): `team declare <name>` on a team that STANDS -- the verb that gave
it birth writes the keys its flags name and they alone, the season under way untouched --, cut out of
`team-templates-options`, the flags at a birth (rule 10); its houses and readings shared in `_templates.py`. A team
started is stopped before it is written: `TEAM.md` is written off season alone. No wake-up plays: every start is
`--no-tick`.
- (a) the same verb on the team it made: `team declare crew --template teams/supervisor-workers --member a … --member b …`
  writes a `TEAM.md` -- the preset's role keys filled with the members the form puts in their places, `supervisor a`
  and `workers b` -- `declaration` judges `ok` and `team start` opens; `team stop crew`, then `team declare crew
  --member c … --role make c --json` adds the member's line and the key's, every other byte of `TEAM.md` as it stood, no event in the journal,
  no other file of the directory moved; its face `{team, file, written, verdict, pending}` -- `written` the keys the
  flags name, `pending` saying `agents`, `reports`, `roles` and `ceremonies`, the daily a second worker brings --; the
  call played again leaves the same bytes, `written` empty; the next `team start` gives birth to the agent and keeps
  the key at `team-started.roles`, beside the preset's
- (b) each flag its key alone, on a `TEAM.md` the owner retouched (a comment, a `reports:`, a ceremony, a body): a
  limit, `--value` and `--no-value` (the block gone with its last line), `--role` saying its whole line and
  `--no-role`, `--member`, `--principal`, `--no-member`, `--document` (a line added, then replaced) and
  `--no-document`, `--description`, `--root`, `--template`, `--launches`, `--timeout`, `--schedule`, `--body-file`
  -- after each call the file is the one before with that change alone, byte for byte, `written` its keys, the
  journal and the other files of the directory as they stood
- (c) refused on a team that stands, nothing written: `template-unknown`, `value-unknown` (a value nothing
  declares), `participant-unknown` (a role for a member nobody declared, a member taken out that an edge names),
  `team-invalid` (a member given twice, a member given to `--member` and to `--no-member`, `solo` over three
  members, a line of `--document` of another form, a `--body-file` that is no file), `flag-retired`
  (`--compose`), the usage (`--value` without `=`, `--member` under `--season`, no key
  named) -- the team's directory and its journal byte for byte
- (d) a contrary on a line that stands not: `--no-value`, `--no-document`, `--no-member` and `--no-role` naming
  nothing the file holds answer rc 0, `written` empty, and write nothing -- `TEAM.md`, the directory and the
  journal byte for byte; under `--season`, on a team without `SEASON.md`, no `SEASON.md` is born, `written` empty
- (e) the tick's lock held: the bench holds the team's `tick.lock`; `team declare` waits `call_lock_wait` (1 s)
  then refuses `team-busy`, nothing written -- the directory and the journal byte for byte; the lock let go, the
  same call writes its key
- (f) the pair judged: what the next `team start` would refuse of `TEAM.md` and `SEASON.md` TOGETHER is refused
  before the write, by `start`'s own codes -- `--no-role make` under a `SEASON.md` whose line reaches `make`
  `role-unknown`, `--document "all other/plain"` beside the season's `notes/plain` `document-collision`, `--no-member
  c` under a profile of `c` `participant-unknown`, `--season --document "all other/plain"` beside the `notes/plain`
  `TEAM.md` names `document-collision` and no `SEASON.md` born -- each directory and journal byte for byte; the profile taken out
  of `SEASON.md`, `--no-member c` writes `agents:` alone
- (g) a refusal that stood before the call: on a team whose `TEAM-<name>.md` holds a body written by hand
  (`intention-misplaced`, said by `declaration`), `--body-file` writes the body of `TEAM.md` and that alone, rc 0,
  `written` `body`, `verdict.ok` false with that refusal, `TEAM-<name>.md` at its bytes -- the call neither causes
  it nor settles it --; what the call causes still refuses: `--no-role make` under the season's line
  `role-unknown`, nothing written
- (h) the write's own refusal, and it alone: `--document "all rules/strict"`, a document that mounts a law coded off `TM`,
  refuses `common-code-prefix`, nothing written -- the call lays it in the members' view --; under a `SEASON.md`
  that switches on a package the house does not pin (`package-unpinned`, said by `declaration`), `--description`
  writes its key alone, rc 0, `verdict.ok` false with that refusal; `--no-member` of the member that holds the open
  task, the season under way, refuses `season-running` naming `team stop` -- `TEAM.md` and the journal byte for
  byte
- (i) a check that could not run before the call never stops it: a `SEASON.md` whose line reaches a key `TEAM.md`
  does not declare, beside a `TEAM-<name>.md` written by hand -- `--role make b` settles `role-unknown`, writes
  `roles:` alone, rc 0, and the verdict names the next one, `intention-misplaced` --; a `TEAM.md` whose role names
  a member nobody declared, under a season that switches on a package the house does not pin -- `--member` mends
  `TEAM.md`, written, the verdict `package-unpinned` --; under a `TEAM.md` refused, `--season --template ghost`
  gives birth to `SEASON.md`, no document judged, the verdict `TEAM.md`'s refusal -- each journal byte for byte
"""
from __future__ import annotations

import json
import re

from conductor.state import lock
from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
# A TEAM.md the owner retouched: a comment, its own edges, a ceremony, a body -- what `declare` leaves at its bytes.
OWNED = ("---\n# the owner's note\ntemplate: teams/supervisor-workers\nvalues: |\n  daily = every mon 10:00\nagents: |\n"
         "  a agents/w/a\n  b agents/w/b\n  c agents/w/c\nreports: |\n  b c -> a\nroles: |\n  make b\n  watch\n"
         "budget: 7\nceremonies: |\n  retro every fri 16:00 with b c -> a\n---\nThe owner's own words.\n")
# A team by its form, one key of role; the season that reaches the key by a line and profiles a member.
PAIR = ("---\ntemplate: teams/supervisor-workers\nagents: |\n  a agents/p/a\n  b agents/p/b\n  c agents/p/c\nroles: |\n"
        "  make b\n---\n")
REACHING = "---\ndocuments: |\n  make notes/plain\nprofiles: |\n  c model=m-1\n---\n"
# A document that mounts a law coded off the team's prefix; a season that switches on a package the house does not pin.
RULES = {"rules/strict.md": ("---\ndescription: strict\nmount: turn.begin\nconstraints.behavior: |\n"
                             "  KX1  keep it short.\n---\nStrict.\n")}
UNPINNED = "---\npackages: |\n  nowhere=on\n---\n"
# A team whose role names a member nobody declared; a season whose line reaches a key.
BROKEN = PAIR.replace("  make b\n", "  make zed\n")
KEYED = "---\ndocuments: |\n  make notes/plain\n---\n"
NOTES = {"notes/plain.md": "---\ndescription: plain notes\n---\nNotes of {team}.\n",
         "notes/dated.md": "---\ndescription: dated notes\nvalues: |\n  day = monday -- the day\n---\nOn {day}.\n",
         "other/plain.md": "---\ndescription: another plain\n---\nOther.\n"}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    started_from = S.started_from

    # --- (a) the same verb on the team it made ----------------------------------------------------
    crew = h.teams / "crew" / "TEAM.md"
    made = h.call("team", "declare", "crew", "--template", "teams/supervisor-workers", "--member", "a", "agents/c/a",
                  "--member", "b", "agents/c/b")
    born = crew.read_text(encoding="utf-8") if crew.is_file() else ""
    judged_ok = (S.declaration_of(h, "crew").get("verdict") or {}).get("ok")
    _, opened, _ = started_from(h, "crew")
    h.call("team", "stop", "crew", "--no-tick")
    before = S.kept(h, "crew")
    again = h.call("team", "declare", "crew", "--member", "c", "agents/c/c", "--role", "make", "c", "--json")
    try:
        face = json.loads(again.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    after = S.kept(h, "crew")
    replayed = h.call("team", "declare", "crew", "--member", "c", "agents/c/c", "--role", "make", "c", "--json")
    try:
        said_again = json.loads(replayed.stdout.strip().splitlines()[-1]).get("written")
    except (ValueError, IndexError):
        said_again = None
    same = S.kept(h, "crew") == after and said_again == []
    wanted = ("---\ntemplate: teams/supervisor-workers\nagents: |\n  a agents/c/a\n  b agents/c/b\nroles: |\n  supervisor a\n"
              "  workers b\n---\n")                    # the preset's keys, each with the members of its places
    grown = (wanted.replace("  b agents/c/b\n", "  b agents/c/b\n  c agents/c/c\n")
             .replace("  workers b\n", "  workers b\n  make c\n"))
    rest = lambda files: {one: data for one, data in files.items() if one != "TEAM.md"}
    _, second, _ = started_from(h, "crew")
    kept_roles = (T.by_kind(h.events("crew"), "team-started") or [{}])[-1]
    if (made.returncode == 0 and born == wanted and judged_ok is True and opened.returncode == 0
            and again.returncode == 0 and after[0].get("TEAM.md") == grown.encode("utf-8")
            and rest(after[0]) == rest(before[0]) and after[1] == before[1] and before[1]
            and set(face) == {"team", "file", "written", "verdict", "pending"} and face.get("team") == "crew"
            and face.get("file") == "teams/crew/TEAM.md" and face.get("written") == ["agents", "roles"]
            and face.get("verdict") == {"ok": True, "refusal": None}
            and {"agents", "reports", "roles", "ceremonies"} <= {one.get("key") for one in face.get("pending") or []}
            and replayed.returncode == 0 and same
            and second.returncode == 0 and h.agent_stands("agents/c/c") and kept_roles.get("roles") == {"supervisor": ["a"], "workers": ["b"], "make": ["c"]}):
        held("(a) the same verb on the team it made", "declare crew --template teams/supervisor-workers --member a b: "
             "TEAM.md born with the preset's keys filled by the form (supervisor a, workers b), judged ok, started; declare crew --member c --role make c: the member's line and the key's "
             "added, every other byte kept, no event, no other file moved; --json {team, file, written [agents, "
             f"roles], verdict ok, pending {[one.get('key') for one in face.get('pending') or []]}}}; played again, "
             "the same bytes, written []; the next start: agents/c/c born, team-started.roles make: c beside the preset's keys")
    else:
        failures.append(f"  ✗ (a) the team it made       rc={made.returncode}/{opened.returncode}/{again.returncode}/"
                        f"{replayed.returncode}/{second.returncode} born={born!r} ok={judged_ok} "
                        f"after={after[0].get('TEAM.md')!r} rest={rest(after[0]) == rest(before[0])} "
                        f"journal={after[1] == before[1]} face={face} same={same} roles={kept_roles.get('roles')} "
                        f"{(made.stderr or again.stderr or second.stderr).strip()[-200:]!r}")

    # --- (b) each flag its key alone, on a TEAM.md the owner retouched ------------------------------
    S.laid(h.house / "teams" / "templates", NOTES)
    h.declare("own", OWNED)
    _, opened, _ = started_from(h, "own")
    h.call("team", "stop", "own", "--no-tick")
    word = bench.temp() / "word.md"
    word.write_text("Another word.\n", encoding="utf-8")
    steps = (
        (("--budget", "9"), ["budget"], lambda text: text.replace("budget: 7\n", "budget: 9\n")),
        (("--value", "daily="), ["values"], lambda text: text.replace("  daily = every mon 10:00\n", "  daily =\n")),
        (("--no-value", "daily"), ["values"], lambda text: text.replace("values: |\n  daily =\n", "")),
        (("--role", "make", "b", "c", "--no-role", "watch"), ["roles"],
         lambda text: text.replace("  make b\n  watch\n", "  make b c\n")),
        (("--member", "d", "agents/w/d", "--principal", "pm"), ["agents", "principals"],
         lambda text: text.replace("  c agents/w/c\n", "  c agents/w/c\n  d agents/w/d\n")
         .replace("---\nThe owner", "principals: |\n  pm\n---\nThe owner")),
        (("--no-member", "d"), ["agents"], lambda text: text.replace("  d agents/w/d\n", "")),
        (("--document", "make notes/plain"), ["documents"],
         lambda text: text.replace("---\nThe owner", "documents: |\n  make notes/plain\n---\nThe owner")),
        (("--document", "make notes/plain notes/dated", "--description", "The crew: it works.", "--root", "a"),
         ["description", "documents", "root"],
         lambda text: text.replace("  make notes/plain\n", "  make notes/plain notes/dated\n")
         .replace("---\nThe owner", 'description: "The crew: it works."\nroot: a\n---\nThe owner')),
        (("--no-document", "make", "--template", "teams/lead-reviewers", "--launches", "3", "--timeout", "60",
          "--schedule", "10", "--body-file", str(word)), ["template", "documents", "launches", "timeout", "schedule", "body"],
         lambda text: text.replace("documents: |\n  make notes/plain notes/dated\n", "")
         .replace("template: teams/supervisor-workers\n", "template: teams/lead-reviewers\n")
         .replace("---\nThe owner's own words.\n", "launches: 3\ntimeout: 60\nschedule: 10\n---\nAnother word.\n")),
    )
    still, wrong = S.kept(h, "own"), []
    for args, keys, change in steps:
        played = h.call("team", "declare", "own", *args, "--json")
        try:
            face = json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            face = {}
        now = S.kept(h, "own")
        wanted = change(still[0]["TEAM.md"].decode("utf-8")).encode("utf-8")
        if not (played.returncode == 0 and now[0].get("TEAM.md") == wanted and wanted != still[0]["TEAM.md"]
                and rest(now[0]) == rest(still[0]) and now[1] == still[1] and face.get("written") == keys
                and (face.get("verdict") or {}).get("ok") is True):
            wrong.append(f"{' '.join(args)}: rc={played.returncode} written={face.get('written')} "
                         f"verdict={face.get('verdict')} file={now[0].get('TEAM.md')!r} rest={rest(now[0]) == rest(still[0])} "
                         f"journal={now[1] == still[1]} {played.stderr.strip()[-160:]!r}")
        still = now
    if opened.returncode == 0 and still[1] and not wrong:
        held("(b) each flag its key alone", f"{len(steps)} calls on a TEAM.md the owner retouched: a limit, a value "
             "set then taken out with its block, a role's whole line and a role out, a member and a principal in, "
             "the member out, a line of documents written then replaced then out, description, root, template, "
             "launches, timeout, schedule, the body -- each file the one before with that change alone, the comment, "
             "reports: and the ceremony at their bytes; written its keys; journal and documents as they stood")
    else:
        failures.append(f"  ✗ (b) each flag its key      rc={opened.returncode} {wrong} {opened.stderr.strip()[-160:]!r}")

    # --- (c) refused on a team that stands, nothing written ---------------------------------------
    h.declare("own", OWNED)
    before = S.kept(h, "own")
    asks = {
        "template-unknown": ("--template", "ghost"),
        "value-unknown": ("--value", "tone=warm"),
        "participant-unknown": ("--role", "make", "zed"),
        "participant-unknown ": ("--no-member", "c"),
        "team-invalid": ("--member", "x", "agents/w/x", "--member", "x", "agents/w/y"),
        "team-invalid ": ("--no-value", "daily", "--template", "teams/solo"),
        "team-invalid  ": ("--document", "make notes/plain/x"),
        "team-invalid   ": ("--member", "x", "agents/w/x", "--no-member", "x"),
        "team-invalid    ": ("--body-file", str(bench.temp() / "no-such-word.md")),
        "flag-retired": ("--compose", "notes plain"),
        "usage": ("--value", "daily"),
        "usage ": ("--season", "--member", "x", "agents/w/x"),
        "usage  ": ("--json",),
    }
    answers = {code: h.call("team", "declare", "own", *args) for code, args in asks.items()}
    wrong = [f"{code.strip()}: rc={one.returncode} {one.stderr.strip()[-160:]!r}" for code, one in answers.items()
             if one.returncode != 2 or (S.code_of(one) != code.strip() if code.strip() != "usage"
                                         else "usage:" not in one.stderr)]
    if not wrong and S.kept(h, "own") == before and before[1]:
        bench.refusals += len(asks)
        held("(c) refused on a team that stands, nothing written", "template-unknown, value-unknown, "
             "participant-unknown (a role for zed, c taken out under its edge), team-invalid (x twice, x given "
             "and taken out, teams/solo over three, a documents line of another form, a --body-file that is no file), "
             "flag-retired (--compose), the usage (--value without =, --member under --season, no key named); "
             "teams/own and its journal byte for byte")
    else:
        failures.append(f"  ✗ (c) refused, standing      {wrong} same={S.kept(h, 'own') == before}")

    # --- (d) a contrary on a line that stands not ------------------------------------------------
    none = h.call("team", "declare", "own", "--no-value", "ghost", "--no-document", "make", "--no-member", "zed",
                  "--no-role", "ghost", "--json")
    try:
        face = json.loads(none.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    season = h.call("team", "declare", "own", "--season", "--no-document", "make", "--no-value", "ghost", "--json")
    try:
        unborn = json.loads(season.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        unborn = {}
    if (none.returncode == 0 and face.get("written") == [] and (face.get("verdict") or {}).get("ok") is True
            and season.returncode == 0 and unborn.get("written") == [] and unborn.get("file") == "teams/own/SEASON.md"
            and S.kept(h, "own") == before and "SEASON.md" not in before[0]):
        held("(d) a contrary on a line that stands not", "--no-value ghost, --no-document make, --no-member zed, "
             "--no-role ghost: rc 0, written [], nothing written; --season on a team without SEASON.md: none born, "
             "written []; teams/own and its journal byte for byte")
    else:
        failures.append(f"  ✗ (d) a line that stands not rc={none.returncode}/{season.returncode} face={face} "
                        f"unborn={unborn} "
                        f"same={S.kept(h, 'own') == before} files={sorted(S.kept(h, 'own')[0])} "
                        f"{(none.stderr or season.stderr).strip()[-160:]!r}")

    # --- (e) the tick's lock held ------------------------------------------------------------------
    settings = h.house / "SETTINGS.md"                      # the owner's edit: a short wait for the house's locks
    settings.write_text(re.sub(r"^call_lock_wait: \d+$", "call_lock_wait: 1", settings.read_text(encoding="utf-8"),
                               count=1, flags=re.M), encoding="utf-8")
    before = S.kept(h, "own")
    lease = lock.acquire(h.journal_of("own").parent / "tick.lock", wait=5)
    try:
        waited = h.call("team", "declare", "own", "--budget", "9")
    finally:
        if lease is not None:
            lock.release(lease)
    busy = S.kept(h, "own")
    freed = h.call("team", "declare", "own", "--budget", "9")
    after = S.kept(h, "own")
    if (lease is not None and waited.returncode == 2 and S.code_of(waited) == "team-busy" and busy == before
            and before[1] and freed.returncode == 0
            and after[0].get("TEAM.md") == before[0]["TEAM.md"].replace(b"budget: 7\n", b"budget: 9\n")
            and after[1] == before[1]):
        bench.refusals += 1
        held("(e) the tick's lock held", "declare --budget 9 waits call_lock_wait (1 s), then team-busy: teams/own "
             "and its journal byte for byte; the lock let go, the same call writes budget: 9")
    else:
        failures.append(f"  ✗ (e) the lock held          lease={lease is not None} rc={waited.returncode}/"
                        f"{freed.returncode} code={S.code_of(waited)} same={busy == before} "
                        f"file={after[0].get('TEAM.md')!r} {(waited.stderr or freed.stderr).strip()[-160:]!r}")

    # --- (f) the pair judged: TEAM.md and SEASON.md together, as the next start reads them ----------
    h.declare("pair", PAIR)
    (h.teams / "pair" / "SEASON.md").write_text(REACHING, encoding="utf-8")
    h.declare("lone", PAIR.replace("roles: |\n", "documents: |\n  all notes/plain\nroles: |\n"))
    stands = [(S.declaration_of(h, one).get("verdict") or {}).get("ok") for one in ("pair", "lone")]
    before = {one: S.kept(h, one) for one in ("pair", "lone")}
    asks = {
        "role-unknown": ("pair", "--no-role", "make"),
        "document-collision": ("pair", "--document", "all other/plain"),
        "participant-unknown": ("pair", "--no-member", "c"),
        "document-collision ": ("lone", "--season", "--document", "all other/plain"),
    }
    answers = {code: h.call("team", "declare", *args) for code, args in asks.items()}
    wrong = [f"{code.strip()}: rc={one.returncode} {one.stderr.strip()[-200:]!r}" for code, one in answers.items()
             if one.returncode != 2 or S.code_of(one) != code.strip()]
    kept_all = {one: S.kept(h, one) for one in ("pair", "lone")} == before
    (h.teams / "pair" / "SEASON.md").write_text(REACHING.replace("profiles: |\n  c model=m-1\n", ""), encoding="utf-8")
    freed = h.call("team", "declare", "pair", "--no-member", "c", "--json")
    try:
        face = json.loads(freed.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    if (stands == [True, True] and not wrong and kept_all and "SEASON.md" not in before["lone"][0]
            and freed.returncode == 0 and face.get("written") == ["agents"]
            and face.get("verdict") == {"ok": True, "refusal": None}
            and S.kept(h, "pair")[0].get("TEAM.md") == PAIR.replace("  c agents/p/c\n", "").encode("utf-8")):
        bench.refusals += len(asks)
        held("(f) the pair judged", "under a SEASON.md whose line reaches make and that profiles c: --no-role make "
             "role-unknown, --document all other/plain document-collision, --no-member c participant-unknown; --season "
             "--document all other/plain beside TEAM.md's notes/plain document-collision, no SEASON.md born; each directory and "
             "journal byte for byte; the profile out of SEASON.md, --no-member c writes agents alone")
    else:
        failures.append(f"  ✗ (f) the pair judged        stands={stands} {wrong} same={kept_all} "
                        f"rc={freed.returncode} face={face} file={S.kept(h, 'pair')[0].get('TEAM.md')!r} "
                        f"{freed.stderr.strip()[-200:]!r}")

    # --- (g) a refusal that stood before the call: the values are written, the verdict says it -------
    h.declare("hand", PAIR)
    (h.teams / "hand" / "TEAM-hand.md").write_text("Words the owner wrote by hand.\n", encoding="utf-8")
    said = ((S.declaration_of(h, "hand").get("verdict") or {}).get("refusal") or "").split(" --")[0]
    before = S.kept(h, "hand")
    moved = h.call("team", "declare", "hand", "--body-file", str(word), "--json")
    try:
        face = json.loads(moved.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    after = S.kept(h, "hand")
    (h.teams / "hand" / "SEASON.md").write_text(REACHING, encoding="utf-8")
    still = S.kept(h, "hand")
    paired = h.call("team", "declare", "hand", "--no-role", "make")
    verdict = face.get("verdict") or {}
    if (said == "intention-misplaced" and moved.returncode == 0 and face.get("written") == ["body"]
            and verdict.get("ok") is False and (verdict.get("refusal") or "").split(" --")[0] == "intention-misplaced"
            and after[0].get("TEAM.md") == (PAIR + "Another word.\n").encode("utf-8")
            and rest(after[0]) == rest(before[0]) and after[1] == before[1]
            and paired.returncode == 2 and S.code_of(paired) == "role-unknown" and S.kept(h, "hand") == still):
        bench.refusals += 1
        held("(g) a refusal that stood before the call", "TEAM-hand.md written by hand, declaration intention-misplaced: "
             "--body-file writes TEAM.md's body alone, rc 0, written [body], verdict ok false with "
             "intention-misplaced, TEAM-hand.md at its bytes; --no-role make under the season's line: role-unknown, "
             "nothing written")
    else:
        failures.append(f"  ✗ (g) a refusal that stood   said={said} rc={moved.returncode}/{paired.returncode} "
                        f"face={face} file={after[0].get('TEAM.md')!r} rest={rest(after[0]) == rest(before[0])} "
                        f"code={S.code_of(paired)} same={S.kept(h, 'hand') == still} "
                        f"{(moved.stderr or paired.stderr).strip()[-200:]!r}")

    # --- (h) the write's own refusal, and it alone -------------------------------------------------
    def faced(played) -> dict:
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    code = lambda face: ((face.get("verdict") or {}).get("refusal") or "").split(" --")[0]
    S.laid(h.house / "teams" / "templates", RULES)
    h.declare("cause", PAIR)
    before = S.kept(h, "cause")
    mounted = h.call("team", "declare", "cause", "--document", "all rules/strict")
    same = S.kept(h, "cause") == before
    (h.teams / "cause" / "SEASON.md").write_text(UNPINNED, encoding="utf-8")
    stood = code(S.declaration_of(h, "cause"))
    before = S.kept(h, "cause")
    told = h.call("team", "declare", "cause", "--description", "A crew.", "--json")
    face, after = faced(told), S.kept(h, "cause")
    h.declare("busy", PAIR)
    _, opened, _ = started_from(h, "busy")
    working = S.kept(h, "busy")
    dropped = h.call("team", "declare", "busy", "--no-member", "a", "--json")
    gone, left = faced(dropped), S.kept(h, "busy")
    if (mounted.returncode == 2 and S.code_of(mounted) == "common-code-prefix" and same
            and stood == "package-unpinned" and told.returncode == 0 and face.get("written") == ["description"]
            and (face.get("verdict") or {}).get("ok") is False and code(face) == "package-unpinned"
            and after[0].get("TEAM.md") == PAIR.replace("roles: |\n  make b\n",
                                                        'roles: |\n  make b\ndescription: "A crew."\n').encode("utf-8")
            and rest(after[0]) == rest(before[0]) and after[1] == before[1]
            and opened.returncode == 0 and working[1] and dropped.returncode == 2
            and S.code_of(dropped) == "season-running" and "team stop" in dropped.stderr and left == working):
        bench.refusals += 2
        held("(h) the write's own refusal, and it alone", "--document all rules/strict, a document mounting KX1: "
             "common-code-prefix, nothing written; under a SEASON.md switching on a package the house does not pin: "
             "--description writes its key alone, rc 0, verdict ok false with package-unpinned; --no-member a under "
             "its open task, in season: season-running naming team stop, TEAM.md and the journal byte for byte")
    else:
        failures.append(f"  ✗ (h) the write's own refusal rc={mounted.returncode}/{told.returncode}/{opened.returncode}/"
                        f"{dropped.returncode} code={S.code_of(mounted)} same={same} stood={stood} face={face} "
                        f"file={after[0].get('TEAM.md')!r} gone={gone} left={left[0].get('TEAM.md')!r} "
                        f"journal={left[1] == working[1]} "
                        f"{(mounted.stderr or told.stderr or dropped.stderr).strip()[-200:]!r}")

    # --- (i) a check that could not run before the call never stops it ------------------------------
    h.declare("late", PAIR.replace("roles: |\n  make b\n", ""))
    (h.teams / "late" / "TEAM-late.md").write_text("Words the owner wrote by hand.\n", encoding="utf-8")
    (h.teams / "late" / "SEASON.md").write_text(KEYED, encoding="utf-8")
    h.declare("mend", BROKEN)
    (h.teams / "mend" / "SEASON.md").write_text(UNPINNED, encoding="utf-8")
    h.declare("shut", BROKEN)
    stood = [code(S.declaration_of(h, one)) for one in ("late", "mend")]
    before = {one: S.kept(h, one) for one in ("late", "mend", "shut")}
    played = {"late": h.call("team", "declare", "late", "--role", "make", "b", "--json"),
              "mend": h.call("team", "declare", "mend", "--member", "zed", "agents/p/zed", "--json"),
              "shut": h.call("team", "declare", "shut", "--season", "--template", "ghost", "--json")}
    faces = {one: faced(call) for one, call in played.items()}
    after = {one: S.kept(h, one) for one in played}
    wanted = {"late": ("TEAM.md", PAIR, ["roles"], "intention-misplaced"),
              "mend": ("TEAM.md", BROKEN.replace("  c agents/p/c\n", "  c agents/p/c\n  zed agents/p/zed\n"), ["agents"],
                       "package-unpinned"),
              "shut": ("SEASON.md", "---\ntemplate: ghost\n---\n", ["template"], "participant-unknown")}
    wrong = [f"{one}: rc={played[one].returncode} face={faces[one]} file={after[one][0].get(file)!r} "
             f"{played[one].stderr.strip()[-160:]!r}"
             for one, (file, text, keys, said) in wanted.items()
             if not (played[one].returncode == 0 and after[one][0].get(file) == text.encode("utf-8")
                     and {path: data for path, data in after[one][0].items() if path != file}
                     == {path: data for path, data in before[one][0].items() if path != file}
                     and after[one][1] == before[one][1] and faces[one].get("written") == keys
                     and (faces[one].get("verdict") or {}).get("ok") is False and code(faces[one]) == said)]
    if stood == ["role-unknown", "participant-unknown"] and not wrong:
        held("(i) a check that could not run before the call", "role-unknown settled by --role make b: roles written "
             "alone, rc 0, verdict intention-misplaced; a TEAM.md mended by --member zed: agents written alone, "
             "verdict package-unpinned; --season --template ghost under a TEAM.md refused: SEASON.md born, verdict "
             "participant-unknown; each journal byte for byte")
    else:
        failures.append(f"  ✗ (i) a check that could not run stood={stood} {wrong}")
    return 0
