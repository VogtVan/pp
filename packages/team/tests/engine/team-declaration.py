"""Scenario `team-declaration` -- 10 case(s): `team declaration <name> [--json]` READS a team's declaration -- its
text, start's own judge's verdict, its gap to the start key by key, and `declared`, the front matter as that judge
reads it with each member's birth and packages -- and writes nothing. No wake-up plays: every start is `--no-tick`.
- (a) before any start: the text byte for byte, `verdict {ok: true}`, `started: null`, `pending: []`, `changed: false`
- (b) the gap to the start: `budget` raised and a member added with its edge -- `changed: true`, `pending` on `agents`,
  `reports` and `limits` with the start's values and the file's; then the body alone rewritten -- `changed: true`,
  `pending: []` (the body is served at once, never pending)
- (c) a broken TEAM.md is said: a root nobody declares -- rc 0, `verdict {ok: false, refusal}`, the refusal's code the
  one `team start` refuses with on the same file, `pending: null`, `declared: null`
- (d) refused, nothing written: `team-unknown`, the usage; the journal, TEAM.md and the calendar to the byte
  across every read
- (a) a team never started says its declaration: `declared` carries its members and their paths in the order
  declared -- each not born, with the packages its birth gives --, its root, its edges, its principals, its limits,
  its schedule, its ceremonies' lines
- (b) the next season's declaration: a team started under a season's `--budget 30`, then a member added to its
  `TEAM.md`: `declared` says the new member and `TEAM.md`'s own budget (5) -- `status --json` keeps the start's
  members and the season's limit --; started again, `team-started` keeps the members and the limits `declared`
  said; the text of `declaration` the same bytes before and after the face is read
- (a) members not born: a team never started, its agents not born: each member `born: false`, `packages` the
  house's pins beyond its base, each on -- what a birth gives
- (b) a member born, a package off: one agent born by `agent add`: `born: true`, every package on; then
  `package.plan: off` written at its SETTINGS by the engine's face: `plan` off, the others on, the member not born
  unchanged; the text of `declaration` the same bytes throughout
- (e) a limit mis-written refuses: `parallel: 0`, `budget: free`, `retries: -1`, `timeout: soon`, `launches: 0`,
  `budget-launches: -1` -- `team-invalid` naming the key, no agent born, no journal
- (f) the name and the path judged: a name with `/`, a name declared twice, a path out of the house -- `team-invalid`
  naming them, no journal, no agent born
"""
from __future__ import annotations

import hashlib
import json

from conductor import instance, settings
from tests.harness import support

T = support(__file__, "team")

# The gap: team `d`, its members f, p1, p2 (p3 added).
FRONT = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> f\nroot: f\n"
         "budget: 5\nschedule: off\n---\n")
BODY = "Name the work.\n"
WIDER = ("---\nagents: |\n  f agents/f\n  p1 agents/p1\n  p2 agents/p2\n  p3 agents/p3\nreports: |\n  p1 p2 p3 -> f\n"
         "root: f\nbudget: 9\nschedule: off\n---\n")
BROKEN = FRONT.replace("root: f", "root: ghost")


def judged_team(root: str, worker: str) -> str:
    """-> a TEAM.md with every key `declared` says: two members, an edge, a principal, limits, a ceremony."""
    return (f"---\nagents: |\n  {root} agents/{root}\n  {worker} agents/{worker}\nreports: |\n  {worker} -> {root}\n"
            f"root: {root}\nprincipals: |\n  pm\nbudget: 5\nlaunches: 8\nschedule: off\nceremonies: |\n"
            f"  daily every weekday 09:30 with {worker} -> {root}\n---\nShip it.\n")


# The declared face: team `new` (lead, dev), team `crew` (head, maker, qa added).
FIRST = judged_team("lead", "dev")
CREW = judged_team("head", "maker")
CREW_WIDER = (CREW.replace("  maker agents/maker\n", "  maker agents/maker\n  qa agents/qa\n")
              .replace("  maker -> head", "  maker qa -> head"))
# The packages: team `squad` (chief, coder).
SQUAD = ("---\nagents: |\n  chief agents/chief\n  coder agents/coder\nreports: |\n  coder -> chief\nroot: chief\n"
         "schedule: off\n---\nShip it.\n")


def code(said: str) -> str:
    """-> the refusal's code: the first token of what pp-team says, after its name."""
    words = said.strip().removeprefix("pp-team: ").split()
    return words[0].rstrip(":") if words else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={}, packages=("agent", "team", "steering", "plan"))
    base = instance.base_of(h.house)
    pinned = [name for name in instance.pins(h.house) if name != base]
    every_on = [{"name": name, "on": True} for name in pinned]
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
        played = h.call("team", "declaration", name, "--json")
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

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
    doc.write_text(WIDER + BODY, encoding="utf-8")
    _, wide = faced()
    text = read()
    doc.write_text(FRONT + "Name the work, now in one line each.\n", encoding="utf-8")
    _, body = faced()
    pending = {one["key"]: one for one in wide.get("pending") or []}
    if (wide.get("changed") is True and wide.get("verdict", {}).get("ok") is True
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
    unborn = {"born": False, "packages": every_on}
    wanted = {"agents": [{"member": "lead", "path": "agents/lead", **unborn}, {"member": "dev", "path": "agents/dev", **unborn}],
              "root": "lead", "reports": [{"from": ["dev"], "to": "lead"}], "principals": ["pm"],
              "limits": {"budget": 5.0, "launches": 8}, "schedule": None,
              "ceremonies": ["daily every weekday 09:30 with dev -> lead"], "entries": {}, "work": None}
    if said == wanted:
        held("(a) a team never started says its declaration", "members in order, root, edges, principals, limits, "
             "schedule off, the daily's line")
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
            and all(one.get("born") is False and one.get("packages") == every_on for one in unborn_members.values())):
        held("(a) members not born", f"born false, packages {[one['name'] for one in every_on]} each on")
    else:
        failures.append(f"  ✗ (a) members not born       pinned={pinned} members={unborn_members}")

    # --- one agent born, then a package switched off at its SETTINGS ---------------------------
    added = h.call("agent", "add", "agents/coder")
    birth = members("squad").get("coder") or {}
    settings.write(h.meta_of("agents/coder"), "package.plan", "off")
    switched = members("squad")
    wanted_off = [{"name": name, "on": name != "plan"} for name in pinned]
    after = text_sha("squad")
    if (added.returncode == 0 and birth.get("born") is True and birth.get("packages") == every_on
            and (switched.get("coder") or {}).get("born") is True
            and (switched.get("coder") or {}).get("packages") == wanted_off
            and (switched.get("chief") or {}).get("born") is False and before == after):
        held("(b) a member born, a package off", f"birth gives every pin on; package.plan off -> {wanted_off}; the "
             f"member not born unchanged; text sha {before}")
    else:
        failures.append(f"  ✗ (b) born and switched      rc={added.returncode} birth={birth} switched={switched} "
                        f"{before} {after} {added.stderr.strip()[-160:]!r}")

    # --- (e) a limit mis-written refuses before anything is written -------------------------------
    limits = {"bad-par": ("z1", "parallel: 0", "parallel"), "bad-bud": ("z2", "budget: free", "budget"),
              "bad-ret": ("z3", "retries: -1", "retries"), "bad-tmo": ("z4", "timeout: soon", "timeout"),
              "bad-wak": ("z5", "launches: 0", "launches"), "bad-bwk": ("z6", "budget-launches: -1", "budget-launches")}
    for name, (agent, line, _key) in limits.items():
        h.declare(name, f"---\nagents: |\n  {agent} {agent}\nroot: {agent}\n{line}\n---\n")
    bad = {name: h.call("team", "start", name, "--message", "x", "--no-tick") for name in limits}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == "" for one in bad.values())
            and all(key in bad[name].stderr for name, (_agent, _line, key) in limits.items())
            and not any(h.agent_stands(agent) for agent, _line, _key in limits.values())
            and not any(h.journal_of(name).exists() for name in bad)):
        held("(e) a limit mis-written refuses", "parallel 0, budget free, retries -1, timeout soon, launches 0, "
             "budget-launches -1: team-invalid naming the key; no agent, no journal")
    else:
        failures.append("  ✗ (e) limits invalid          " + " ".join(f"{name}={one.returncode}:{one.stderr[-100:]!r}"
                                                                      for name, one in bad.items()))

    # --- (f) the name and the path judged -----------------------------------------------------------
    h.declare("slashed", "---\nagents: |\n  nm/r9 agents/r9\nroot: nm/r9\nschedule: off\n---\nA name with a slash.\n")
    h.declare("twice", "---\nagents: |\n  dn agents/a1x\n  dn agents/b1x\nroot: dn\nschedule: off\n---\nOne name twice.\n")
    h.declare("escaped", "---\nagents: |\n  ex ../x\nroot: ex\nschedule: off\n---\nA path out of the house.\n")
    judged = {name: h.call("team", "start", name, "--message", "x", "--no-tick") for name in ("slashed", "twice", "escaped")}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == "" for one in judged.values())
            and "nm/r9" in judged["slashed"].stderr and "dn" in judged["twice"].stderr and "../x" in judged["escaped"].stderr
            and not any(h.journal_of(name).exists() for name in judged)
            and not any(path.exists() for path in (h.ws / "nm", h.ws / "agents" / "r9", h.ws / "agents" / "a1x",
                                                   h.ws / "agents" / "b1x", h.ws / "ex", h.ws.parent / "x"))):
        held("(f) the name and the path judged", "a name with `/`, a name declared twice, a path out of the "
             "house: team-invalid naming them, no journal, no agent born")
    else:
        failures.append("  ✗ (f) name and path judged    "
                        + " ".join(f"{name}={one.returncode}:{one.stdout[-80:]!r}:{one.stderr[-100:]!r}" for name, one in judged.items()))
    return 0
