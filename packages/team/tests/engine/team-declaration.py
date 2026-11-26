"""Scenario `team-declaration` -- 11 case(s): `team declaration <name> [--json]` READS a team's declaration -- its
text, start's own judge's verdict, its gap to the start key by key, and `declared`, the front matter as that judge
reads it with each member's birth and packages -- and writes nothing. No wake-up plays: every start is `--no-tick`.
The keys a TEAM.md writes are `team-declaration-keys`'s, the team's documents `team-declaration-documents`'s, cut
out of it by rule 10; its readings shared in `_team.py`.
- (a) before any start: the text byte for byte, `verdict {ok: true}`, `started: null`, `pending: []`, `changed: false`
- (b) the gap to the start: the `team-started` of a `TEAM.md` without `template:` carries no `template` key, no
  `cut` and no document; the start wrote `TEAM-<name>.md`, its head and an empty body -- no template, no intention
  --, its digest kept at `team-started.rendered`, its head serving `TEAM.md`, whose body is the owner's word;
  `budget` raised and a member added with its edge -- `changed: true`, `pending` on `agents`,
  `reports` and `limits` with the start's values and the file's; then the body alone rewritten -- `changed: true`,
  `pending: []` (the body is served at once, never pending)
- (c) a broken TEAM.md is said: a root nobody declares -- rc 0, `verdict {ok: false, refusal}`, the refusal's code the
  one `team start` refuses with on the same file, `pending: null`, `declared: null`
- (d) refused, nothing written: `team-unknown`, the usage; the journal, TEAM.md and the calendar to the byte
  across every read
- (a) a team never started says its declaration: `declared` carries its members and their paths in the order
  declared -- each not born, with the packages a season without `--package` gives, `no description` and no role --,
  its root, its edges, its principals, its limits, its schedule, its ceremonies' lines, no contract, no role, each
  member's view empty, no template (`declared.template` null: without `template:` the team is what `TEAM.md` writes),
  the season a start without a flag opens on the team's defaults
- (b) the next season's declaration: a team started under a season's `--budget 30`, then a member added to its
  `TEAM.md`: `declared` says the new member and `TEAM.md`'s own budget (5) -- `status --json` keeps the start's
  members and the season's limit --; stopped and started again, `team-started` keeps the members and the limits `declared`
  said; the text of `declaration` the same bytes before and after the face is read
- (a) members not born: a team never started, its agents not born: each member `born: false`, `packages` the
  house's pins beyond its base as a season without `--package` gives them -- the team's requirements on, the rest off
- (b) a member born, its SETTINGS out of the set: one agent born by `agent add` (its SETTINGS playing every pin):
  `born: true`, the same packages; then `package.plan: off` written at its SETTINGS by the engine's face: the packages
  unchanged, the member not born unchanged; the text of `declaration` the same bytes throughout
- (e) a candidate read, nothing written: `declaration --json --text-file -` reads a `TEAM.md` on standard input and
  says it as if written -- its text, a role given to dev in `declared.roles` and dev's view, `verdict` ok; a candidate
  whose root nobody declares says `participant-unknown`, rc 0; under `--season`, a candidate `SEASON.md` gives its
  model to `declared.season.launch`, a key `SEASON.md` does not say `season-invalid` -- `TEAM.md`, no `SEASON.md` and
  the journal byte for byte
- (f) a member's path and name, judged on candidates: `.` (the house) is a member's path, verdict ok and `declared`
  saying `path: "."`; `./x`, `x/.` and `..` refuse `team-invalid`; a member named as the owner -- the house's slug --
  refuses `team-invalid`, whatever its path; nothing written
- (g) a start that kept no schedule: a journal written by hand whose `team-started` carries no `schedule` key reads as
  the default net (300 s) -- a `TEAM.md` without `schedule:` has no gap on it, one that says `schedule: off` has the
  gap `schedule` from 300 to null
"""
from __future__ import annotations

import hashlib
import json

from conductor import instance, settings
from tests.harness import cli, support

T = support(__file__, "team")
code = T.refusal_code

# The gap: team `d`, its members f, p1, p2 (p3 added).
FRONT = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
         "budget: 5\nschedule: off\n---\n")
BODY = "Name the work.\n"
WIDER = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\n  p3 agents/p3\nreports: |\n  p1 p2 p3 -> f\n"
         "root: f\nbudget: 9\nschedule: off\n---\n")
BROKEN = FRONT.replace("root: f", "root: ghost")
# The declared face: team `new` (lead, dev), team `crew` (head, maker, qa added).
FIRST = T.judged_team("lead", "dev")
CREW = T.judged_team("head", "maker")
CREW_WIDER = (CREW.replace("  maker agents/maker\n", "  maker agents/maker\n  qa agents/qa\n")
              .replace("  maker -> head", "  maker qa -> head"))
# The packages: team `squad` (chief, coder).
SQUAD = ("---\nagents: |\n  chief agents/chief\n  coder agents/coder\nreports: |\n  coder -> chief\nroot: chief\n"
         "schedule: off\n---\nShip it.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={}, packages=("agent", "team", "steering", "plan"))
    base = instance.base_of(h.house)
    pinned = [name for name in instance.pins(h.house) if name != base]
    silent = [{"name": name, "on": name in ("agent", "team")} for name in pinned]   # a season without --package
    doc = h.teams / "d" / "TEAM.md"
    reads: list[tuple[bytes, bytes, bytes]] = []

    def kept() -> tuple[bytes, bytes, bytes]:
        journal = h.journal_of("d")
        return (journal.read_bytes() if journal.is_file() else b"", doc.read_bytes() if doc.is_file() else b"",
                h.crontab.read_bytes() if h.crontab.is_file() else b"")

    def read(*flags: str):
        before = kept()
        said = h.call("team", "declaration", "d", *flags, now="08:00")
        reads.append((before, kept()))
        return said

    def faced():
        said = read("--json")
        lines = said.stdout.splitlines()
        return said, (json.loads(lines[0]) if said.returncode == 0 and len(lines) == 1 else {})

    def declaration(name: str) -> dict:
        return T.declaration_read(h, name)

    def members(name: str) -> dict:
        return {one.get("member"): one for one in (declaration(name).get("declared") or {}).get("agents") or []}

    def text_sha(name: str) -> str:
        return hashlib.sha256(h.call("team", "declaration", name).stdout.encode()).hexdigest()[:12]

    # --- (a) before any start ---------------------------------------------------------------------
    h.declare("d", FRONT + BODY)
    said, face = faced()
    text = read()
    if (said.returncode == 0 and face.get("team") == "d" and face.get("text") == FRONT + BODY
            and face.get("verdict") == {"ok": True, "refusal": None} and face.get("started") is None
            and face.get("pending") == [] and face.get("changed") is False and str(face.get("path", "")).endswith("TEAM.md")
            and text.returncode == 0):
        held("(a) before any start", "the text byte for byte, verdict ok, started null, pending [], changed false")
    else:
        failures.append(f"  ✗ (a) before the start      rc={said.returncode}/{text.returncode} face={face} "
                        f"{(said.stderr or text.stderr).strip()[-160:]!r}")

    # --- (b) the gap to the start ---------------------------------------------------------------
    h.call("team", "start", "d", "--message", "go", "--no-tick", now="07:50")
    started = next(iter(T.by_kind(h.events("d"), "team-started")), {})
    own = h.teams / "d" / "TEAM-d.md"
    rendered = own.read_bytes() if own.is_file() else b""
    doc.write_text(WIDER + BODY, encoding="utf-8")
    _, wide = faced()
    text = read()
    doc.write_text(FRONT + "Name the work, now in one line each.\n", encoding="utf-8")
    _, body = faced()
    pending = {one["key"]: one for one in wide.get("pending") or []}
    if (wide.get("changed") is True and wide.get("verdict", {}).get("ok") is True
            and started.get("reports") == [{"from": ["p1", "p2"], "to": "f"}]
            and "template" not in started and "cut" not in started and started.get("documents") == []
            and rendered.startswith(b"---\nproc: |\n  SERVE\nserve: |\n  TEAM-d.md\n  TEAM.md\n")
            and rendered.endswith(b"\n---\n")
            and started.get("rendered") == {"TEAM-d.md": hashlib.sha256(rendered).hexdigest()[:12]}
            and list(pending) == ["agents", "reports", "limits"]
            and pending["agents"]["started"] == started.get("agents")
            and pending["agents"]["declared"] == {**started.get("agents", {}), "p3": "agents/p3"}
            and pending["reports"]["declared"] == [{"from": ["p1", "p2", "p3"], "to": "f"}]
            and pending["limits"]["started"] == {"budget": 5} and pending["limits"]["declared"] == {"budget": 9}
            and (wide.get("started") or {}).get("id") == started.get("id")
            and text.returncode == 0
            and body.get("changed") is True and body.get("pending") == []):
        held("(b) the gap to the start", "budget 5 -> 9 and p3 added: pending agents, reports, limits with the "
             "start's values and the file's; the body alone rewritten: changed, pending []")
    else:
        failures.append(f"  ✗ (b) the gap              wide={wide.get('changed')} {list(pending)} {pending} "
                        f"started={sorted(started)} rendered={rendered[-80:]!r}/{started.get('rendered')} "
                        f"body={body.get('changed')}/{body.get('pending')} rc={text.returncode}")

    # --- (c) a broken TEAM.md is said -------------------------------------------------------------
    doc.write_text(BROKEN + BODY, encoding="utf-8")
    said, broken = faced()
    text = read()
    refused = h.call("team", "start", "d", "--message", "again", "--no-tick", now="08:01")
    verdict = broken.get("verdict") or {}
    if (said.returncode == 0 and refused.returncode == 2 and code(refused.stderr) == "participant-unknown"
            and verdict.get("ok") is False and code(verdict.get("refusal") or "") == code(refused.stderr)
            and broken.get("pending") is None and "declared" in broken and broken["declared"] is None
            and broken.get("text") == BROKEN + BODY and text.returncode == 0):
        held("(c) a broken TEAM.md is said", f"rc 0, verdict refused with start's own code `{code(refused.stderr)}`; "
             "pending null, declared null")
    else:
        failures.append(f"  ✗ (c) broken                rc={said.returncode} verdict={verdict} "
                        f"start={refused.returncode}/{code(refused.stderr)} pending={broken.get('pending', '?')} "
                        f"declared={broken.get('declared', '?')}")

    # --- (d) refused, nothing written -----------------------------------------------------------
    unknown = h.call("team", "declaration", "ghost")
    bare = h.call("team", "declaration")
    flagged = h.call("team", "declaration", "d", "--yes")
    if (unknown.returncode == 2 and code(unknown.stderr) == "team-unknown"
            and bare.returncode == 2 and code(bare.stderr) == "usage"
            and flagged.returncode == 2 and code(flagged.stderr) == "usage"
            and reads and all(before == after for before, after in reads)):
        bench.refusals += 3
        held("(d) refused, nothing written", f"team-unknown, the usage twice; the journal, TEAM.md and the calendar "
             f"to the byte across {len(reads)} reads")
    else:
        failures.append(f"  ✗ (d) refused / written     rc={unknown.returncode}/{bare.returncode}/{flagged.returncode} "
                        f"codes={code(unknown.stderr)}/{code(bare.stderr)}/{code(flagged.stderr)} "
                        f"unchanged={[before == after for before, after in reads]}")

    # --- a team never started says its declaration --------------------------------------------
    h.declare("new", FIRST)
    said = declaration("new").get("declared") or {}
    unborn = {"born": False, "packages": silent, "description": "no description", "roles": []}   # no MEMBER.md yet
    wanted = {"agents": [{"member": "lead", "path": "agents/lead", **unborn}, {"member": "dev", "path": "agents/dev", **unborn}],
              "root": "lead", "reports": [{"from": ["dev"], "to": "lead"}], "principals": ["pm"],
              "limits": {"budget": 5.0, "launches": 8}, "schedule": None,
              "ceremonies": ["daily every weekday 09:30 with dev -> lead"], "entries": {}, "work": None,
              "documents": [], "values": [{"name": "team", "value": "new", "from": "built-in"}], "roles": [],
              "views": [{"member": "lead", "roles": [], "documents": []}, {"member": "dev", "roles": [], "documents": []}],
              "template": None,
              "season": {"launch": {}, "limits": {}, "profiles": {}, "work": None,   # no SEASON.md: the team's defaults
                         "packages": [f"{one['name']}={'on' if one['on'] else 'off'}" for one in silent]}}
    if said == wanted:
        held("(a) a team never started says its declaration", "members in order, root, edges, principals, limits, "
             "schedule off, the daily's line, template null")
    else:
        failures.append(f"  ✗ (a) never started          {said}")

    # --- what the next season will have -------------------------------------------------------
    h.declare("crew", CREW)
    h.call("team", "start", "crew", "--message", "go", "--budget", "30", *h.harnessed, "--no-tick")
    h.declare("crew", CREW_WIDER)
    before = text_sha("crew")
    declared = declaration("crew").get("declared") or {}
    after = text_sha("crew")
    state = h.face("crew")
    h.call("team", "stop", "crew", "--no-tick")
    h.call("team", "start", "crew", *h.harnessed, "--no-tick")
    started = ([one for one in h.events("crew") if one.get("kind") == "team-started"] or [{}])[-1]
    names = [one.get("member") for one in declared.get("agents") or []]
    if (names == ["head", "maker", "qa"] and declared.get("limits", {}).get("budget") == 5.0
            and [one.get("member") for one in state.get("members") or []] == ["head", "maker"]
            and (state.get("limits") or {}).get("budget") == 30.0
            and list(started.get("agents") or {}) == names and started.get("limits") == declared.get("limits")
            and before == after):
        held("(b) the next season's declaration", f"declared {names}, budget 5 where status says the start's "
             f"two members and the season's 30; the next start keeps what declared said; text sha {before}")
    else:
        failures.append(f"  ✗ (b) next season            declared={declared} status_members="
                        f"{[one.get('member') for one in state.get('members') or []]} limits={state.get('limits')} "
                        f"started={started.get('agents')} {started.get('limits')} {before} {after}")

    # --- agents not born: what a birth gives --------------------------------------------------
    h.declare("squad", SQUAD)
    before = text_sha("squad")
    unborn_members = members("squad")
    if (set(pinned) == {"agent", "team", "steering", "plan"} and list(unborn_members) == ["chief", "coder"]
            and all(one.get("born") is False and one.get("packages") == silent for one in unborn_members.values())):
        held("(a) members not born", f"born false, packages {silent}: the team's requirements on, the rest off")
    else:
        failures.append(f"  ✗ (a) members not born       pinned={pinned} members={unborn_members}")

    # --- one agent born, then a package switched off at its SETTINGS ---------------------------
    added = h.call("agent", "add", "agents/coder")
    birth = members("squad").get("coder") or {}
    settings.write(h.meta_of("agents/coder"), "package.plan", "off")
    switched = members("squad")
    after = text_sha("squad")
    if (added.returncode == 0 and birth.get("born") is True and birth.get("packages") == silent
            and (switched.get("coder") or {}).get("born") is True
            and (switched.get("coder") or {}).get("packages") == silent
            and (switched.get("chief") or {}).get("born") is False and before == after):
        held("(b) a member born, its SETTINGS out of the set", f"born, its SETTINGS playing every pin, then "
             f"package.plan off: packages {silent} throughout; the member not born unchanged; text sha {before}")
    else:
        failures.append(f"  ✗ (b) born and switched      rc={added.returncode} birth={birth} switched={switched} "
                        f"{before} {after} {added.stderr.strip()[-160:]!r}")


    # --- (e) a candidate read, nothing written -------------------------------------------------------------------
    cand = "---\nagents: |\n  lead agents/lead\n  dev agents/dev\nreports: |\n  dev -> lead\nroot: lead\nschedule: off\n---\n"
    h.declare("cand", cand)
    stood_c = ((h.teams / "cand" / "TEAM.md").read_bytes(), (h.teams / "cand" / "SEASON.md").exists())

    def candidate(text: str, *flags: str) -> tuple:
        played = cli(h.engine, "--instance", str(h.house), "team", "declaration", "cand", "--json", *flags,
                     "--text-file", "-", cwd=h.ws, env=h.env, stdin=text)
        try:
            return played.returncode, json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return played.returncode, {}

    roled = cand.replace("schedule: off\n", "schedule: off\nroles: |\n  make dev\n")
    rc_r, face_r = candidate(roled)
    rc_b, face_b = candidate(cand.replace("root: lead", "root: ghost"))
    rc_s, face_s = candidate("---\nmodel: m-9\n---\nThe season to come.\n", "--season")
    rc_k, face_k = candidate("---\nmount: turn.begin\n---\n", "--season")
    views_r = {one.get("member"): one.get("roles") for one in (face_r.get("declared") or {}).get("views") or []}
    if (rc_r == 0 and face_r.get("text") == roled and (face_r.get("verdict") or {}).get("ok") is True
            and (face_r.get("declared") or {}).get("roles") == [{"role": "make", "members": ["dev"]}]
            and views_r == {"lead": [], "dev": ["make"]}
            and rc_b == 0 and code((face_b.get("verdict") or {}).get("refusal") or "") == "participant-unknown"
            and rc_s == 0 and (((face_s.get("declared") or {}).get("season") or {}).get("launch") or {}).get("model") == "m-9"
            and (face_s.get("season") or {}).get("text") == "---\nmodel: m-9\n---\nThe season to come.\n"
            and rc_k == 0 and code((face_k.get("verdict") or {}).get("refusal") or "") == "season-invalid"
            and ((h.teams / "cand" / "TEAM.md").read_bytes(), (h.teams / "cand" / "SEASON.md").exists()) == stood_c
            and not h.journal_of("cand").exists()):
        held("(e) a candidate read, nothing written", "--text-file -: the candidate TEAM.md said as written, make for "
             "dev in declared.roles and its view, verdict ok; a root nobody declares: participant-unknown, rc 0; "
             "--season: model m-9 in declared.season.launch, a key of another file season-invalid; nothing written")
    else:
        failures.append(f"  ✗ (e) a candidate read        rc={rc_r}/{rc_b}/{rc_s}/{rc_k} views={views_r} "
                        f"roles={(face_r.get('declared') or {}).get('roles')} verdicts={face_r.get('verdict')}/"
                        f"{face_b.get('verdict')}/{face_k.get('verdict')} season={(face_s.get('declared') or {}).get('season')}")

    # --- (f) a member's path and name -------------------------------------------------------------------------------
    owner = str(instance.slug(h.house))
    home = lambda agents: f"---\nagents: |\n{agents}root: lead\nschedule: off\n---\n"
    rc_h, face_h = candidate(home("  lead .\n  dev agents/dev\n"))
    paths_h = {one.get("member"): one.get("path") for one in (face_h.get("declared") or {}).get("agents") or []}
    odd = {at: candidate(home(f"  lead {at}\n")) for at in ("./x", "x/.", "..")}
    owned = {at: candidate(home(f"  lead agents/lead\n  {owner} {at}\n")) for at in (f"agents/{owner}", ".")}
    verdicts_f = {at: (rc, code((face.get("verdict") or {}).get("refusal") or ""))
                  for at, (rc, face) in {**odd, **{f"{owner} {at}": one for at, one in owned.items()}}.items()}
    if (rc_h == 0 and (face_h.get("verdict") or {}).get("ok") is True and paths_h == {"lead": ".", "dev": "agents/dev"}
            and verdicts_f and all(one == (0, "team-invalid") for one in verdicts_f.values())
            and ((h.teams / "cand" / "TEAM.md").read_bytes(), (h.teams / "cand" / "SEASON.md").exists()) == stood_c
            and not h.journal_of("cand").exists()):
        held("(f) a member's path and name", f"`.` a member's path, verdict ok, declared path `.`; ./x, x/., .. and a "
             f"member named `{owner}` (the owner) at agents/{owner} and at `.`: team-invalid; nothing written")
    else:
        failures.append(f"  ✗ (f) a member's path and name rc={rc_h} verdict={face_h.get('verdict')} paths={paths_h} "
                        f"verdicts={verdicts_f}")

    # --- (g) a start that kept no schedule ----------------------------------------------------------------------
    unkept = {"kind": "team-started", "agents": {"n": "agents/n"}, "reports": [], "root": "n", "principals": [],
              "owner": "house", "ceremonies": [], "entries": {}, "work": None, "launch": {}, "limits": {}}
    schedules = {"netted": "", "netless": "schedule: off\n"}
    for name, line in schedules.items():
        h.declare(name, f"---\nagents: |\n  n agents/n\nroot: n\n{line}---\nKeep the net.\n")
        h.written(name, [unkept], T.THURSDAY + "08:00:00")
    gaps = {name: {one["key"]: one for one in T.declaration_read(h, name).get("pending") or []} for name in schedules}
    if ("schedule" not in gaps["netted"]
            and {key: gaps["netless"].get("schedule", {}).get(key) for key in ("started", "declared")}
            == {"started": 300, "declared": None}):
        held("(g) a start that kept no schedule", "team-started without schedule reads as the default net, 300 s: no "
             "gap under a TEAM.md without schedule, the gap schedule 300 -> null under schedule: off")
    else:
        failures.append(f"  ✗ (g) no schedule kept       netted={gaps['netted']} netless={gaps['netless']}")
    return 0
