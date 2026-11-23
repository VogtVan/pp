"""Scenario `team-role-documents-judged` -- 3 case(s): the VIEW of each member judged at `start`, and the verifier of
the family `team-member:<team>/<member>` -- the cases of `team-role-documents` cut out of it by case (rule 10), its
house `_roles.py`'s. No wake-up plays.
- (e) judged in each view: two documents of disjoint roles may carry the same code; a member holding both keys
  refuses `common-collision` naming it; a tool one member of the role resolves passes, given to a member who does
  not resolve it refuses `common-tool-unknown` naming it; a document of a role mounted at another moment than
  `turn.begin` refuses `common-mount-moment` -- the team's directory and its journal byte for byte (G7, G8)
- (h) the verifier refuses under `vector-refused`, nothing launched: a member the season does not know
  (`member-unknown`), another member's agent (`member-foreign`), a run under another root (`root-foreign`), a team
  never started (`team-not-started`), a team nobody declared (`team-unknown`) -- the team's directory and its journal
  byte for byte
- (i) a document of a role deleted by hand stays in the view: mi's vector still said by `status --json`; mi's next
  launch fails, a final `wake-failed` whose reason says `vector-refused` and `mount-missing`, naming
  `roles/TEAM-rd-law.md` -- never `--vector -` in silence; a `team start` renders it again
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
R = support(__file__, "roles")
laid, code_of, kept = S.laid, S.code_of, S.kept


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"mi": [R.DONE]})
    R.declared(h)
    h.call("team", "start", "rd", *h.harnessed, "--no-tick")

    # --- (e) judged in each view -- G7, G8 -----------------------------------------------------------------------
    laid(h.house / "teams" / "templates", {
        "seasons/clash.md": "---\ndescription: one code, two roles\ndocuments: |\n  inspect review/law\n"
                            "  make notes/twin\n---\n",
        "notes/twin.md": "---\ndescription: the same code\nmount: turn.begin\nconstraints.behavior: |\n  TM5  zztwin.\n"
                         "---\nzztwinbody\n",
        "guide/owntool.md": "---\ndescription: a tool of one agent\nmount: turn.begin\ntools: |\n  zz-own\n---\nzzown\n",
        "guide/late.md": "---\ndescription: mounted late\nmount: turn.end\n---\nzzlate\n"})
    h.call("agent", "add", "agents/xo")
    skill = h.meta_of("agents/xo") / "skills" / "zz-own" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("---\nname: zz-own\ndescription: a tool xo alone has\n---\nUse it.\n", encoding="utf-8")
    rx = ("---\nagents: |\n  xa agents/xa\n  xi agents/xi\n  xo agents/xo\nroot: xa\nroles: |\n  make xa\n"
          "  inspect xi\n  own xo\nschedule: off\n---\nJudge the views.\n")
    h.declare("rx", rx)
    season_rx = h.teams / "rx" / "SEASON.md"
    season_rx.write_text("---\ntemplate: seasons/clash\ndocuments: |\n  own guide/owntool\n---\n", encoding="utf-8")
    disjoint = h.call("team", "start", "rx", "--no-tick")
    h.off_season("rx")                                   # the next starts judged off season
    refusals = {}
    for code, (team_text, season_text, named) in {
            "common-collision": (rx.replace("  make xa\n", "  make xa xi\n"), None, "xi"),
            "common-tool-unknown": (rx.replace("  own xo\n", "  own xo xa\n"), None, "xa"),
            "common-mount-moment": (rx, "---\ntemplate: seasons/clash\ndocuments: |\n  own guide/late\n---\n",
                                    "TEAM-rx-late.md")}.items():
        (h.teams / "rx" / "TEAM.md").write_text(team_text.split("---\n", 2)[1].join(("---\n", "---\n")),
                                                encoding="utf-8")
        if season_text:
            season_rx.write_text(season_text, encoding="utf-8")
        before_rx = kept(h, "rx")
        played = h.call("team", "start", "rx", "--no-tick")
        refusals[code] = (played.returncode, code_of(played), named in played.stderr, kept(h, "rx") == before_rx)
        (h.teams / "rx" / "TEAM.md").write_text(rx.split("---\n", 2)[1].join(("---\n", "---\n")), encoding="utf-8")
        season_rx.write_text("---\ntemplate: seasons/clash\ndocuments: |\n  own guide/owntool\n---\n", encoding="utf-8")
    if disjoint.returncode == 0 and all(one == (2, code, True, True) for code, one in refusals.items()):
        bench.refusals += len(refusals)
        held("(e) judged in each view", "TM5 on two disjoint roles starts; xi holding both: common-collision naming "
             "xi; zz-own given to xa: common-tool-unknown naming xa; a document mounted at turn.end: common-mount-moment "
             "-- the directory and the journal byte for byte -- G7, G8")
    else:
        failures.append(f"  ✗ (e) judged in each view     rc={disjoint.returncode} {refusals} "
                        f"{disjoint.stderr.strip()[-300:]!r}")

    # --- (h) the verifier refuses under vector-refused ----------------------------------------------------------
    h.declare("never", "---\nagents: |\n  nv agents/nv\nroot: nv\nschedule: off\n---\nNever started.\n")
    h.declare("other", "---\nagents: |\n  ot agents/ot\nroot: ot\nschedule: off\n---\nAnother root.\n")
    asks = {"member-unknown": ("agents/ma", "rd", "team-member:rd/ghost"),
            "member-foreign": ("agents/ma", "rd", "team-member:rd/mi"),
            "root-foreign": ("agents/ma", "other", "team-member:rd/ma"),
            "team-not-started": ("agents/ma", "rd", "team-member:never/nv"),
            "team-unknown": ("agents/ma", "rd", "team-member:nosuch/x")}
    wrong = []
    for cause, (path, root, vector) in asks.items():
        before_rd, prompts_before = kept(h, "rd"), len(h.prompts_of(path.split("/")[-1]))
        played = h.call("agent", "start", path, "--message", "refuse me", "--documents", str(h.teams / root),
                        "--vector", vector, *h.harnessed)
        last = (played.stderr.strip().splitlines() or [""])[-1]
        if (played.returncode != 2 or not last.startswith("pp-agent: vector-refused -- ") or cause not in last
                or kept(h, "rd") != before_rd or len(h.prompts_of(path.split("/")[-1])) != prompts_before):
            wrong.append(f"{cause}: rc={played.returncode} {last[-200:]!r}")
    if not wrong:
        bench.refusals += len(asks)
        held("(h) the verifier refuses", "member-unknown, member-foreign, root-foreign, team-not-started, team-unknown, "
             "each under vector-refused, nothing launched, rd's directory and journal byte for byte")
    else:
        failures.append(f"  ✗ (h) the verifier            {wrong}")

    # --- (i) a document of a role deleted by hand is said, never dropped -------------------------------------
    missing = h.teams / "rd" / "roles" / "TEAM-rd-law.md"
    missing.unlink(missing_ok=True)
    vector = next((one.get("vector") for one in h.face("rd").get("members") or [] if one.get("member") == "mi"), None)
    h.call("team", "post", "rd", "--to", "mi", "--message", "work mi", "--no-tick")
    h.call("team", "tick", "rd")
    h.settled("rd", lambda found: bool(T.by_kind(found, "wake-failed", agent="mi")) and T.all_ended(found), 60)
    failed = (T.by_kind(h.events("rd"), "wake-failed", agent="mi") or [{}])[-1]
    reason = str(failed.get("reason") or "")
    h.off_season("rd")
    again = h.call("team", "start", "rd", "--no-tick")
    if (vector == "team-member:rd/mi" and failed.get("final") is True and "vector-refused" in reason
            and "mount-missing" in reason and "roles/TEAM-rd-law.md" in reason
            and again.returncode == 0 and missing.is_file()):
        held("(i) a document of a role deleted by hand is said", "mi keeps its vector; its launch fails final, "
             "vector-refused, mount-missing naming roles/TEAM-rd-law.md; a start renders it again")
    else:
        failures.append(f"  ✗ (i) a role document deleted vector={vector} final={failed.get('final')} "
                        f"reason={reason[-300:]!r} rc={again.returncode} back={missing.is_file()}")
    return 0
