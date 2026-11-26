"""Scenario `team-role-documents` -- 6 case(s): the documents of a ROLE, mounted for the members who hold one of its
keys by the vector `team-member:<team>/<member>` -- in a team's run and in a dialogue at the post --, the others
never reading them. One house pinning `agent` and `team`, the preset `seasons/split` of `_templates.py`: `notes/plain`
for everyone, `review/law` for `inspect` (it mounts: a law, a tool), `sources/read` for `make` (served), `guide/both`
for both. Team `rd` (`_roles.py`): `ma` holds `make`, `mi` `inspect`, `mb` both, `mn` none. The judging cases and the
verifier's refusals are `team-role-documents-judged`'s.
- (a) two roles, two views: ma's first prompt reads the notes, the maker's and the shared document, never the
  inspector's; mi's the notes, the inspector's and the shared document, never the maker's; the three documents of a
  role stand under `roles/`, the head of `TEAM-rd.md` serves none of them (G4)
- (b) two keys, each document once: mb's first prompt reads the three documents of a role, each once; `pp-team mount
  rd/mb` says them in the start's order, each once
- (c) no filtered document, no vector: mn's prompt reads none of them, `members[].vector` absent for mn and said for
  ma, the `opened` event of mn's run carries no vector, `pp-team mount rd/mn` says nothing (G5)
- (d) served and mounted keep their effect: mi's block carries the law of the mounted document, asked at its proof,
  and its tool -- the proof read on its run's flow --; ma's served document brings its body alone -- no law, no tool; mi's
  second exchange reads no body again (G6)
- (f) the dialogue: `agent chat agents/mi --documents teams/rd --vector team-member:rd/mi` reads what mi's team run
  read -- the same `INFORMATION` titles
- (g) a key lost: `inspect` taken from mi, a new season -- mi's next launch passes `--vector -`, its `opened` event
  carries no vector, the inspector's law is no longer in its block
"""
from __future__ import annotations

import json
import re

from tests.harness import cli, support

T = support(__file__, "team")
R = support(__file__, "roles")
DONE, titles, section, script = R.DONE, R.titles, R.section, R.script


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "ma": [DONE], "mb": [DONE], "mn": [DONE],
        "mi": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which?"}}}, DONE, DONE, DONE]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def run_of(member: str) -> str:
        return next((one.get("run") for one in reversed(by_kind(h.events("rd"), "wake-launched", agent=member))
                     if one.get("run")), "")

    def opened(path: str, key: str) -> list:
        said = h.call("agent", "flow", path, key, "--json") if key else None
        return [json.loads(line).get("vectors") for line in (said.stdout.splitlines() if said else [])
                if line.strip().startswith("{") and json.loads(line).get("kind") == "opened"]

    def mounted_docs(played) -> list[str]:
        line = next((one for one in played.stdout.splitlines() if one.startswith("::mount ")), "")
        return [one.get("doc") for one in json.loads(line[len("::mount "):])] if line else []

    R.declared(h)
    started = h.call("team", "start", "rd", *h.harnessed, "--no-tick")
    for member in ("ma", "mi", "mb", "mn"):
        h.call("team", "post", "rd", "--to", member, "--message", f"work {member}", "--no-tick")
    h.call("team", "tick", "rd")
    h.settled("rd", lambda found: bool(by_kind(found, "post", verb="ask")) and len(by_kind(found, "done")) >= 3
              and all_ended(found), 90)
    ask = [one["id"] for one in by_kind(h.events("rd"), "post", verb="ask")]
    if ask:
        h.call("team", "post", "rd", "--task", next(one.get("task") for one in by_kind(h.events("rd"), "post", verb="ask")),
               "--reply", str(ask[0]), "--message", "this one")
    h.settled("rd", lambda found: len(by_kind(found, "done")) >= 4 and all_ended(found), 60)
    first = {member: (h.prompts_of(member) or [""])[0] for member in ("ma", "mi", "mb", "mn")}
    mi_prompts = h.prompts_of("mi")
    directory = h.teams / "rd"
    head = (directory / "TEAM-rd.md").read_text(encoding="utf-8") if (directory / "TEAM-rd.md").is_file() else ""
    served = (re.search(r"^serve: \|\n((?:  .*\n)+)", head, re.M) or [None, ""])[1].split()

    # --- (a) two roles, two views -- G4 ---------------------------------------------------------------------
    under = sorted(one.name for one in (directory / "roles").glob("*.md")) if (directory / "roles").is_dir() else []
    if (started.returncode == 0 and under == ["TEAM-rd-both.md", "TEAM-rd-law.md", "TEAM-rd-read.md"]
            and "TEAM-rd-plain.md" in served and not any(part in one for part in ("-law", "-read", "-both")
                                                         for one in served)
            and all(one in first["ma"] for one in ("zzmakebody", "zzbothbody", "Notes of rd"))
            and "zzinspectbody" not in first["ma"]
            and all(one in first["mi"] for one in ("zzinspectbody", "zzbothbody", "Notes of rd"))
            and "zzmakebody" not in first["mi"]):
        held("(a) two roles, two views", f"roles/ holds {under}, the head serves {served}; ma reads the maker's and "
             "the shared document, mi the inspector's and the shared document, neither the other's -- G4")
    else:
        failures.append(f"  ✗ (a) two views               rc={started.returncode} under={under} served={served} "
                        f"ma={titles(first['ma'])[4:]} mi={titles(first['mi'])[4:]} {started.stderr.strip()[-200:]!r}")

    # --- (b) two keys, each document once -- G4 -------------------------------------------------------------
    mb_titles = titles(first["mb"])
    said_mb = script(h, "mount", "rd/mb", path="agents/mb", run=run_of("mb"))
    if (all(mb_titles.count(one) == 1 for one in ("TEAM-rd-law", "TEAM-rd-read", "TEAM-rd-both"))
            and said_mb.returncode == 0
            and mounted_docs(said_mb) == ["roles/TEAM-rd-law.md", "roles/TEAM-rd-both.md", "roles/TEAM-rd-read.md"]):
        held("(b) two keys, each document once", "mb reads law, read and both once each; pp-team mount rd/mb "
             "says them in the start's order, once each")
    else:
        failures.append(f"  ✗ (b) two keys                titles={mb_titles[4:]} rc={said_mb.returncode} "
                        f"mount={mounted_docs(said_mb)} {said_mb.stderr.strip()[-120:]!r}")

    # --- (c) no filtered document, no vector -- G5 -----------------------------------------------------------
    face = h.face("rd")
    vectors = {one.get("member"): one.get("vector", "absent") for one in face.get("members") or []}
    said_mn = script(h, "mount", "rd/mn", path="agents/mn", run=run_of("mn"))
    if (not any(one in first["mn"] for one in ("zzmakebody", "zzinspectbody", "zzbothbody")) and first["mn"]
            and vectors.get("mn") == "absent" and vectors.get("ma") == "team-member:rd/ma"
            and opened("agents/mn", run_of("mn")) and all(one is None for one in opened("agents/mn", run_of("mn")))
            and said_mn.returncode == 0 and "::mount" not in said_mn.stdout):
        held("(c) no filtered document, no vector", "mn reads none of the roles' documents; members[].vector absent for "
             "mn, team-member:rd/ma for ma; mn's opened events carry no vector; pp-team mount rd/mn says nothing -- G5")
    else:
        failures.append(f"  ✗ (c) no vector               vectors={vectors} opened={opened('agents/mn', run_of('mn'))} "
                        f"rc={said_mn.returncode} {said_mn.stdout[:200]!r} {said_mn.stderr.strip()[-120:]!r}")

    # --- (d) served and mounted keep their effect -- G6 -------------------------------------------------------
    second = mi_prompts[1] if len(mi_prompts) > 1 else ""
    mi_flow = h.call("agent", "flow", "agents/mi", run_of("mi"), "--json").stdout if run_of("mi") else ""
    if ("TM5" in section(first["mi"], "CONSTRAINTS") and re.search(r"INFER proof \[[^\]]*\bTM5\b", mi_flow)
            and "pp-agent" in section(first["mi"], "TOOLS")
            and "TM6" not in first["ma"] and "pp-agent" not in section(first["ma"], "TOOLS")
            and second and "zzinspectbody" not in second and "zzbothbody" not in second
            and "TM5" in section(second, "CONSTRAINTS")):
        held("(d) served and mounted keep their effect", "mi's block carries TM5, asked at its proof, and pp-agent "
             "offered; ma's served document brings its body alone; mi's second exchange reads no body again -- G6")
    else:
        failures.append(f"  ✗ (d) effects                 proof={re.findall(r'INFER proof [^\\\\]*', mi_flow)[:2]} "
                        f"mi={section(first['mi'], 'CONSTRAINTS')[:160]!r} "
                        f"tools={section(first['mi'], 'TOOLS')[:120]!r}/{section(first['ma'], 'TOOLS')[:120]!r} "
                        f"second={section(second, 'CONSTRAINTS')[:160]!r}")

    # --- (f) the dialogue reads what the team's run read --------------------------------------------------------
    before = len(h.prompts_of("mi"))
    talked = cli(h.engine, "--instance", str(h.house), "agent", "chat", "agents/mi", "--documents", str(directory),
                 "--vector", "team-member:rd/mi", *h.harnessed, cwd=h.ws, env=h.env, stdin="hello\n")
    chat_prompt = (h.prompts_of("mi")[before:] or [""])[0]
    if (talked.returncode == 0 and chat_prompt
            and sorted(set(titles(chat_prompt))) == sorted(set(titles(first["mi"])))):
        held("(f) the dialogue", f"agent chat --vector team-member:rd/mi reads the titles of mi's team run: "
             f"{sorted(set(titles(chat_prompt)))}")
    else:
        failures.append(f"  ✗ (f) the dialogue            rc={talked.returncode} chat={sorted(set(titles(chat_prompt)))} "
                        f"run={sorted(set(titles(first['mi'])))} {talked.stderr.strip()[-200:]!r}")

    # --- (g) a key lost, a new season -------------------------------------------------------------------------
    (h.teams / "rd" / "TEAM.md").write_text((h.teams / "rd" / "TEAM.md").read_text(encoding="utf-8")
                                            .replace("  inspect mi mb\n", "  inspect mb\n"), encoding="utf-8")
    h.off_season("rd")
    season = h.call("team", "start", "rd", *h.harnessed, "--no-tick")
    count = len(by_kind(h.events("rd"), "wake-ended", agent="mi"))
    h.call("team", "post", "rd", "--to", "mi", "--message", "again", "--no-tick")
    h.call("team", "tick", "rd")
    h.settled("rd", lambda found: len(by_kind(found, "wake-ended", agent="mi")) > count and all_ended(found), 60)
    last_mi = (h.prompts_of("mi") or [""])[-1]
    lost_opened = opened("agents/mi", run_of("mi"))
    if (season.returncode == 0 and len(by_kind(h.events("rd"), "wake-ended", agent="mi")) > count
            and lost_opened and lost_opened[-1] is None and "TM5" not in section(last_mi, "CONSTRAINTS")):
        held("(g) a key lost", "inspect taken from mi, a new season: mi's next launch passes --vector -, its opened "
             "event carries no vector, TM5 no longer in its block")
    else:
        failures.append(f"  ✗ (g) a key lost              rc={season.returncode} opened={lost_opened} "
                        f"constraints={section(last_mi, 'CONSTRAINTS')[:200]!r} {season.stderr.strip()[-200:]!r}")

    return 0
