"""Scenario `team-rename` -- `team rename <name> <new> [--json]` moves a team to a new directory name (batch
les-equipes-au-poste, team 0.51.0):
- (h) moved: on a team at rest `t` whose `name:` is `t`, `rename t u` moves `teams/t` to `teams/u` and its journal to
  the records of `u`, rewrites `name:` to `u`; `status u --json` answers, `status t` refuses `team-unknown`; the face
  says `{from, to, name}`; a team `v` whose `name:` is its own (`shown`) keeps it when moved to `w`
- (i) refused, nothing written: a team at work (a task open) `team-busy`; a name a team stands under already
  `team-exists`; `a/b` `team-invalid`; a team nobody declared `team-unknown` -- the directories and the journals the
  same to the byte
- (j) a team renamed starts again: a team under a template, started, renamed -- its `TEAM-<name>.md` moved with it
  at its bytes --, a member added, then started: the start passes -- the document, which the journal kept under
  its former name, is no intention misplaced --, `TEAM-<new>.md` rendered again, its head serving itself, its body
  naming the new member, its digest at `team-started.rendered` under the new name alone
- (k) a document the former `team new` left: a `TEAM-<name>.md` no start rendered whose body is the template's
  intention for the same members starts; the same body with a word of the owner's refuses `intention-misplaced`,
  nothing written
"""
from __future__ import annotations

import json
from pathlib import Path

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
FORMER_HEAD = "---\nproc: |\n  SERVE\nserve: |\n  TEAM-{team}.md\n  TEAM_WORK.md\nattach: turn.begin\n---\n"   # as `team new` wrote it


def files_under(root: Path) -> dict[str, bytes]:
    """-> {relative path: bytes} of every file under `root` -- a lock's own file, laid at its first take, left out."""
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*"))
            if path.is_file() and path.suffix != ".lock"} if root.is_dir() else {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which branch?"}}}]})
    by_kind, all_ended = T.by_kind, T.all_ended
    records = h.records / "teams"
    h.declare("t", "---\nname: review\nagents: |\n  ta agents/ta\nroot: ta\nschedule: off\n---\nAt rest.\n")
    h.declare("v", "---\nname: shown\nagents: |\n  va agents/va\nroot: va\nschedule: off\n---\nShown.\n")
    h.declare("busy", "---\nagents: |\n  w agents/w\nroot: w\nschedule: off\n---\nAsk first.\n")
    started = [h.call("team", "start", name, "--no-tick") for name in ("t", "v")]
    at_work = h.call("team", "start", "busy", "--message", "merge PR 12", *h.harnessed)
    asked = h.settled("busy", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)

    def kept() -> tuple:
        """The teams' directories and the records of t and v -- busy's records are its own wake-up's, which writes
        after its end (the follower's drain)."""
        return files_under(h.teams), files_under(records / "t"), files_under(records / "v")

    # --- (i) refused, nothing written -------------------------------------------------------------------------
    before = kept()
    working = h.call("team", "rename", "busy", "idle")
    taken = h.call("team", "rename", "t", "v")
    invalid = h.call("team", "rename", "t", "a/b")
    unknown = h.call("team", "rename", "ghost", "spirit")
    refused = {"team-busy": working, "team-exists": taken, "team-invalid": invalid, "team-unknown": unknown}
    if (all(one.returncode == 0 for one in started) and at_work.returncode == 0 and asked
            and all(one.returncode == 2 and code in one.stderr for code, one in refused.items()) and kept() == before):
        bench.refusals += 4
        held("(i) refused, nothing written", "busy (T1 open) team-busy, t -> v team-exists, t -> a/b team-invalid, "
             "ghost team-unknown; the directories and the journals the same to the byte")
    else:
        failures.append(f"  ✗ (i) refused                rc={[one.returncode for one in started]}/{at_work.returncode} "
                        f"asked={asked} {[(code, one.returncode, one.stderr.strip()[-100:]) for code, one in refused.items()]} "
                        f"same={kept() == before}")

    # --- (h) moved ----------------------------------------------------------------------------------------------
    moved = h.call("team", "rename", "t", "u", "--json")
    try:
        told = json.loads(moved.stdout)
    except ValueError:
        told = {}
    shown = h.call("team", "rename", "v", "w")
    face_u = h.face("u")
    gone = h.call("team", "status", "t")
    front_u = (h.teams / "u" / "TEAM.md").read_text(encoding="utf-8") if (h.teams / "u" / "TEAM.md").is_file() else ""
    front_w = (h.teams / "w" / "TEAM.md").read_text(encoding="utf-8") if (h.teams / "w" / "TEAM.md").is_file() else ""
    if (moved.returncode == 0 and told == {"from": "t", "to": "u", "name": "u"} and shown.returncode == 0
            and not (h.teams / "t").exists() and not (records / "t").exists()
            and h.journal_of("u").is_file() and "name: u" in front_u and face_u.get("team") == "u"
            and gone.returncode == 2 and "team-unknown" in gone.stderr
            and not (h.teams / "v").exists() and h.journal_of("w").is_file() and "name: shown" in front_w):
        held("(h) moved", "t -> u: the directory and the journal moved, name: rewritten u, status u answers, status t "
             "team-unknown; v -> w keeps name: shown")
    else:
        failures.append(f"  ✗ (h) moved                  rc={moved.returncode}/{shown.returncode}/{gone.returncode} told={told} "
                        f"t={(h.teams / 't').exists()} journal_u={h.journal_of('u').is_file()} front_u={front_u[:80]!r} "
                        f"face={face_u.get('team')} front_w={front_w[:60]!r} {moved.stderr[-200:]!r} {shown.stderr[-200:]!r}")

    # --- (j) a team renamed starts again -------------------------------------------------------------------------
    last_start = lambda name: (by_kind(h.events(name), "team-started") or [{}])[-1]
    made = h.call("team", "declare", "ra", "--template", "teams/supervisor-workers", "--member", "boss", "agents/ta",
                  "--member", "x", "agents/va", "--member", "y", "agents/w")
    first = h.call("team", "start", "ra", "--no-tick")
    kept_first = (last_start("ra").get("rendered") or {}).get("TEAM-ra.md")
    renamed = h.call("team", "rename", "ra", "rb")
    document = h.teams / "rb" / "TEAM-rb.md"
    carried = document.read_bytes() if document.is_file() else b""
    declared = h.teams / "rb" / "TEAM.md"
    if declared.is_file():
        declared.write_text(declared.read_text(encoding="utf-8").replace("  y agents/w\n", "  y agents/w\n  z agents/ta\n"),
                            encoding="utf-8")
    h.off_season("rb")
    again = h.call("team", "start", "rb", "--no-tick")
    rendered = document.read_bytes() if document.is_file() else b""
    season = last_start("rb")
    if (made.returncode == 0 and first.returncode == 0 and renamed.returncode == 0 and kept_first
            and S.digest(carried) == kept_first and not S.names_all(S.intention_of(carried.decode()), ["z"])
            and again.returncode == 0 and rendered != carried
            and b"serve: |\n  TEAM-rb.md\n" in rendered
            and S.names_all(S.intention_of(rendered.decode()), ["boss", "x", "y", "z"])
            and (season.get("rendered") or {}) == {"TEAM-rb.md": S.digest(rendered)}):
        held("(j) a team renamed starts again", "ra started, renamed rb with its document at its bytes, z added: the "
             "start passes, TEAM-rb.md rendered again -- its head serving itself, its body naming z --, its digest "
             "kept under the new name alone")
    else:
        failures.append(f"  ✗ (j) renamed, started again  rc={made.returncode}/{first.returncode}/{renamed.returncode}/"
                        f"{again.returncode} carried={S.digest(carried) == kept_first} rendered={season.get('rendered')} "
                        f"head={rendered[:80]!r} {(renamed.stderr or again.stderr).strip()[-240:]!r}")

    # --- (k) a document the former `team new` left ---------------------------------------------------------------
    born = h.call("team", "declare", "fo", "--template", "teams/supervisor-workers", "--member", "supervisor", "agents/ta",
                  "--member", "worker-1", "agents/va", "--member", "worker-2", "agents/w")
    intention = (S.templates_of(h).get("teams/supervisor-workers") or {}).get("intention") or ""
    left = h.teams / "fo" / "TEAM-fo.md"
    left.write_text(FORMER_HEAD.format(team="fo") + intention + "\nA word of the owner.\n", encoding="utf-8")
    before = files_under(h.teams / "fo"), h.journal_of("fo").is_file()
    worded = h.call("team", "start", "fo", "--no-tick")
    same = (files_under(h.teams / "fo"), h.journal_of("fo").is_file()) == before
    left.write_text(FORMER_HEAD.format(team="fo") + intention + "\n", encoding="utf-8")
    former = h.call("team", "start", "fo", "--no-tick")
    if (born.returncode == 0 and intention and worded.returncode == 2 and S.code_of(worded) == "intention-misplaced"
            and same and not before[1]
            and former.returncode == 0
            and (last_start("fo").get("rendered") or {}).get("TEAM-fo.md") == S.digest(left.read_bytes())):
        bench.refusals += 1
        held("(k) a document the former team new left", "TEAM-fo.md never rendered, its body the template's intention "
             "for the same members: the start passes and renders it; the same body with a word of the owner's: "
             "intention-misplaced, nothing written")
    else:
        failures.append(f"  ✗ (k) the former document     rc={born.returncode}/{worded.returncode}/{former.returncode} "
                        f"intention={len(intention)} code={S.code_of(worded)} same={same} "
                        f"{(worded.stderr or former.stderr).strip()[-240:]!r}")
    return 0
