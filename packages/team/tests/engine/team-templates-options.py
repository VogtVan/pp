"""Scenario `team-templates-options` -- 6 case(s): the flags of `team declare <name>` at a team's BIRTH -- the one
verb that writes a team's values; the team that stands is `team-declare-existing`'s --, what a `TEAM.md` writes
over its template, and what is refused writing nothing -- the sibling of `team-templates`, its houses and readings
shared in `_templates.py`. No wake-up plays: every start is `--no-tick`.
- (b) the form tree: five members under `--value squads=1` make one squad lead over three workers, no daily, the
  value `squads = 1` written under `values:` and kept at `team-started.values`; four members under the template's
  two squads and `--value squads=0` refuse `team-invalid`, `--value squads=2` on `council` -- a value it does not
  declare -- `value-unknown`: nothing written, no `teams/<name>` left behind
- (a) the flags at a birth: `--member` replaces the template's members in the order given, the form making the root,
  the edges and the ids of the intention again (`lead-reviewers` with one reviewer: no daily); `--principal`,
  `--budget`, `--launches`, `--timeout`, `--schedule` written and read at `team-started`; `--root` written under
  `root:`, another member the root; `--value daily=` written `daily =` under `values:`, no daily; `--body-file` is
  the body of `TEAM.md` as the file holds it, the intention still the template's, rendered by the start; `chain`
  given three members delegates each to the next, its face `--json` one object `{team, file, written, verdict,
  pending}` -- `written` `template` and `agents`, the verdict `ok`, nothing pending before a start --; no `TEAM.md`
  writes `reports:`
- (d) what `TEAM.md` writes wins: under `supervisor-workers`, a `reports:`, a `budget:` and a ceremony named `daily`
  written are the team's -- the root the form's, the other limits the template's, one daily --; a `root:` written
  makes the others report to it, a value `daily` left empty takes the daily out -- read at `declaration --json`,
  `declared.template.values` saying each value `from` `default` or `team`; the daily counts who reports to the root
  in the edges as the team plays: `b -> a`, `c -> b` written and no ceremony, no daily -- one member reports to
  the root --; `b c -> a` written, the daily of b and c
- (b) refused at a birth, nothing written: `template-unknown` (`teams/pair`, a preset this house lacks); a member's
  path `team-invalid` and a root nobody declared `participant-unknown` -- `start`'s own refusals --; `teams/solo`
  given two members `team-invalid`; `--budget`
  not a number `team-invalid`; `--teams` (the flag `--template` replaced) the usage; `team new` `verb-retired`,
  naming `team declare`; no `teams/<name>` left behind
- (e) a `TEAM.md` its template refuses: `template: ghost` `template-unknown`, a value the template does not declare
  `value-unknown`, a value without a default left out `value-missing` (a house's template), `solo` over two members
  `team-invalid`, a house's template that still writes `daily:` and one whose front matter never closes
  `template-invalid` -- `team start` refuses
  each by its code, `declaration` says the same code with rc 0; `roster --json` and `status --json` give each of
  these teams no member and no root, `delete --json` (said, not played) no agent of the last; the teams' directories
  and their journals byte for byte across all
- (c) two writers at once: two `team declare` of one name played at once, one giving `--description`, the other
  `--budget`, three times -- both write, one after the other under the team's lock: the TEAM.md standing holds both
  keys, its declaration judged `ok`, no temporary left beside it
"""
from __future__ import annotations

import json
import threading

from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")
DAILY = S.DAILY
# What TEAM.md writes over `supervisor-workers`: its edges, a limit and a daily of its own; then its root and no daily.
WON = ("---\ntemplate: teams/supervisor-workers\nagents: |\n  a agents/w/a\n  b agents/w/b\n  c agents/w/c\n"
       "reports: |\n  b -> a\n  c -> b\nbudget: 7\nceremonies: |\n  daily every mon 10:00 with b c -> a\n---\n")
ROOTED = ("---\ntemplate: teams/supervisor-workers\nvalues: |\n  daily =\nagents: |\n  a agents/w/a\n  b agents/w/b\n"
          "  c agents/w/c\nroot: c\n---\n")
# The daily under edges written: a chain of two edges, one member reporting to the root; the form's own edge written.
LINED = ("---\ntemplate: teams/supervisor-workers\nagents: |\n  a agents/w/a\n  b agents/w/b\n  c agents/w/c\n"
         "reports: |\n  b -> a\n  c -> b\n---\n")
FLAT = LINED.replace("  b -> a\n  c -> b\n", "  b c -> a\n")
# A house's templates of `teams`: one declares a value without a default, one still writes `daily:` as a key, the
# last never closes its front matter.
TONED = {"teams/toned.md": ("---\ndescription: a tone to give\nform: star\nmembers: |\n  a\n  b\nvalues: |\n"
                            "  tone -- how the team speaks\n---\n{root} leads {others}.\n"),
         "teams/dated.md": ("---\ndescription: a daily written as a key\nform: star\nmembers: |\n  a\n  b\n"
                            "daily: every weekday 09:30\n---\n{root} leads {others}.\n"),
         "teams/torn.md": "---\ndescription: a front matter left open\nform: star\nmembers: |\n  a\n  b\n"}
# The TEAM.md a template refuses, by the code of its refusal.
REFUSED = (
    ("template-unknown", "---\ntemplate: ghost\nagents: |\n  m agents/m\n---\n"),
    ("value-unknown", "---\ntemplate: teams/solo\nvalues: |\n  tone = warm\nagents: |\n  m agents/m\n---\n"),
    ("value-missing", "---\ntemplate: teams/toned\nagents: |\n  m agents/m\n  n agents/n\n---\n"),
    ("team-invalid", "---\ntemplate: teams/solo\nagents: |\n  m agents/m\n  n agents/n\n---\n"),
    ("template-invalid", "---\ntemplate: teams/dated\nagents: |\n  m agents/m\n  n agents/n\n---\n"),
    ("template-invalid", "---\ntemplate: teams/torn\nagents: |\n  m agents/m\n  n agents/n\n---\n"),
)
intention_of = S.intention_of
names_all = S.names_all


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    started_from = S.started_from

    # --- (b) the form tree, and what it refuses ---------------------------------------------------
    one_squad = h.call("team", "declare", "small", "--template", "teams/tree", "--value", "squads=1", "--member", "l", "agents/s/l",
                       "--member", "s", "agents/s/s", "--member", "a", "agents/s/a", "--member", "b", "agents/s/b",
                       "--member", "c", "agents/s/c")
    _, started, first = started_from(h, "small")
    asks = {
        "four members, two squads": ("team-invalid", "ghost-tree-1", "--template", "teams/tree", "--member", "l", "agents/g/l",
                                     "--member", "s", "agents/g/s", "--member", "t", "agents/g/t", "--member", "w",
                                     "agents/g/w"),
        "squads off tree": ("value-unknown", "ghost-tree-2", "--template", "teams/council", "--value", "squads=2"),
        "squads = 0": ("team-invalid", "ghost-tree-3", "--template", "teams/tree", "--value", "squads=0"),
    }
    answers = {why: (code, h.call("team", "declare", *args)) for why, (code, *args) in asks.items()}
    refused = [f"{why}: rc={one.returncode} {one.stderr.strip()[-160:]!r}" for why, (code, one) in answers.items()
               if one.returncode != 2 or S.code_of(one) != code]
    left = sorted(path.name for path in (h.teams.iterdir() if h.teams.is_dir() else ()) if path.name.startswith("ghost"))
    squads = S.keys_of((h.teams / "small" / "TEAM.md").read_text(encoding="utf-8")) if one_squad.returncode == 0 else []
    if (one_squad.returncode == 0 and started.returncode == 0 and first.get("root") == "l"
            and first.get("reports") == [{"from": ["s"], "to": "l"}, {"from": ["a", "b", "c"], "to": "s"}]
            and first.get("ceremonies") == [] and "values" in squads and not {"reports", "root"} & set(squads)
            and first.get("values") == {"squads": "1", "daily": DAILY}
            and not refused and not left):
        bench.refusals += len(asks)
        held("(b) the form tree", "--value squads=1 on five members: s -> l, a b c -> s, no daily, squads = 1 written "
             "and kept; team-invalid for four members under two squads and squads=0, value-unknown for squads on "
             "council; no teams/ghost-* left")
    else:
        failures.append(f"  ✗ (b) tree                   rc={one_squad.returncode}/{started.returncode} "
                        f"root={first.get('root')} reports={first.get('reports')} refused={refused} left={left} "
                        f"keys={squads} values={first.get('values')} "
                        f"{(one_squad.stderr or started.stderr).strip()[-160:]!r}")

    # --- (a) the options --------------------------------------------------------------------------
    told = h.call("team", "declare", "pairing", "--template", "teams/lead-reviewers", "--member", "writer", "agents/x/writer",
                  "--member", "critic", "agents/x/critic", "--principal", "pm", "--principal", "boss",
                  "--budget", "12.5", "--launches", "3", "--timeout", "60", "--schedule", "10")
    text, started, first = started_from(h, "pairing")
    own = bench.temp() / "intention.md"
    own.write_text("Each member must answer `hi`.\n", encoding="utf-8")
    rooted = h.call("team", "declare", "rooted", "--template", "teams/supervisor-workers", "--root", "worker-2",
                    "--value", "daily=", "--body-file", str(own))
    rooted_text, started_r, first_r = started_from(h, "rooted")
    chained = h.call("team", "declare", "line", "--template", "teams/chain", "--member", "a", "agents/l/a", "--member", "b",
                     "agents/l/b", "--member", "c", "agents/l/c", "--json")
    try:
        face = json.loads(chained.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    _, started_c, first_c = started_from(h, "line")
    pairing = intention_of(text)
    keys = {team: S.keys_of((h.teams / team / "TEAM.md").read_text(encoding="utf-8"))
            if (h.teams / team / "TEAM.md").is_file() else [] for team in ("pairing", "rooted", "line")}
    if (told.returncode == 0 and started.returncode == 0
            and not any("reports" in one for one in keys.values())
            and "root" not in keys["pairing"] and {"root", "values"} <= set(keys["rooted"])
            and first.get("values") == {"daily": DAILY} and first_r.get("values") == {"daily": ""}
            and (first_c.get("template") or {}).get("template") == "teams/chain"
            and first.get("agents") == {"writer": "agents/x/writer", "critic": "agents/x/critic"}
            and first.get("root") == "writer" and first.get("reports") == [{"from": ["critic"], "to": "writer"}]
            and first.get("ceremonies") == [] and first.get("principals") == ["pm", "boss"]
            and first.get("limits") == {"budget": 12.5, "launches": 3, "timeout": 60} and first.get("schedule") == 600
            and names_all(pairing, ["writer", "critic"]) and not names_all(pairing, ["lead"])
            and rooted.returncode == 0 and started_r.returncode == 0 and first_r.get("root") == "worker-2"
            and first_r.get("reports") == [{"from": ["supervisor", "worker-1"], "to": "worker-2"}]
            and first_r.get("ceremonies") == []
            and (h.teams / "rooted" / "TEAM.md").read_text(encoding="utf-8").endswith("---\n" + own.read_text(encoding="utf-8"))
            and names_all(intention_of(rooted_text), ["supervisor", "worker-1", "worker-2"])
            and chained.returncode == 0 and started_c.returncode == 0 and first_c.get("root") == "a"
            and face == {"team": "line", "file": "teams/line/TEAM.md", "written": ["template", "agents"],
                         "verdict": {"ok": True, "refusal": None}, "pending": []}
            and first_c.get("reports") == [{"from": ["b"], "to": "a"}, {"from": ["c"], "to": "b"}]):
        held("(a) the flags at a birth", "--member writer critic: root writer, critic -> writer, no daily, the "
             "intention names them; principals pm boss, budget 12.5, launches 3, timeout 60, schedule 10; --root "
             "worker-2 under root:, --value daily= under values: (daily empty), --body-file; chain a b c: b -> a, "
             "c -> b, --json {team, file, written [template, agents], verdict ok, pending []}; no reports: written")
    else:
        failures.append(f"  ✗ (a) options                rc={told.returncode}/{started.returncode}/{rooted.returncode}/"
                        f"{started_r.returncode}/{chained.returncode}/{started_c.returncode} first={first} "
                        f"rooted={first_r.get('root')}/{first_r.get('reports')} chain={first_c.get('reports')} "
                        f"keys={keys} values={first.get('values')}/{first_r.get('values')} face={face} "
                        f"{(told.stderr or started.stderr or rooted.stderr or chained.stderr).strip()[-200:]!r}")

    # --- (d) what TEAM.md writes wins ------------------------------------------------------------
    h.declare("won", WON)
    h.declare("turned", ROOTED)
    h.declare("lined", LINED)
    h.declare("flat", FLAT)
    won, turned = S.declaration_of(h, "won"), S.declaration_of(h, "turned")
    said, other = won.get("declared") or {}, turned.get("declared") or {}
    lined, flat = (S.declaration_of(h, one).get("declared") or {} for one in ("lined", "flat"))
    values = lambda face: [(one.get("name"), one.get("value"), one.get("from"))
                           for one in (face.get("template") or {}).get("values") or []]
    if ((won.get("verdict") or {}).get("ok") is True and (turned.get("verdict") or {}).get("ok") is True
            and said.get("reports") == [{"from": ["b"], "to": "a"}, {"from": ["c"], "to": "b"}]
            and said.get("root") == "a" and said.get("limits") == {"budget": 7, "launches": 24, "timeout": 900}
            and said.get("ceremonies") == ["daily every mon 10:00 with b c -> a"] and said.get("schedule") is None
            and values(said) == [("daily", DAILY, "default")]
            and other.get("root") == "c" and other.get("reports") == [{"from": ["a", "b"], "to": "c"}]
            and other.get("ceremonies") == [] and other.get("limits") == S.LIMITS
            and values(other) == [("daily", "", "team")]
            and lined.get("reports") == said.get("reports") and lined.get("root") == "a"
            and lined.get("ceremonies") == []
            and flat.get("reports") == [{"from": ["b", "c"], "to": "a"}]
            and flat.get("ceremonies") == [f"daily {DAILY} with b c -> a"]):
        held("(d) what TEAM.md writes wins", "under supervisor-workers: reports, budget 7 and a daily of its own "
             "written -- root a the form's, launches and timeout the template's, one daily; root c written -- a b "
             "-> c --, daily left empty -- no daily; the values said from default and from team; b -> a, c -> b "
             "written: no daily, one member reports to the root; b c -> a written: the daily of b and c")
    else:
        failures.append(f"  ✗ (d) TEAM.md wins           verdicts={won.get('verdict')}/{turned.get('verdict')} "
                        f"won={said} turned={other} lined={lined.get('reports')}/{lined.get('ceremonies', '?')} "
                        f"flat={flat.get('reports')}/{flat.get('ceremonies', '?')}")

    # --- (b) refused, nothing written -------------------------------------------------------------
    asks = {
        "template-unknown": ("declare", "ghost-1", "--template", "teams/pair"),
        "team-invalid": ("declare", "ghost-2", "--template", "teams/solo", "--member", "w", "Bad/Path"),
        "participant-unknown": ("declare", "ghost-3", "--template", "teams/supervisor-workers", "--root", "nobody"),
        "team-invalid ": ("declare", "ghost-4", "--template", "teams/solo", "--member", "a", "agents/a", "--member", "b",
                          "agents/b"),
        "team-invalid  ": ("declare", "ghost-5", "--template", "teams/solo", "--budget", "lots"),
        "usage": ("declare", "ghost-6", "--teams", "solo"),
        "verb-retired": ("new", "ghost-7", "--teams", "solo"),
    }
    answers = {code: h.call("team", *args) for code, args in asks.items()}
    wrong = [f"{code.strip()}: rc={one.returncode} {one.stderr.strip()[-160:]!r}" for code, one in answers.items()
             if one.returncode != 2 or code.strip() not in one.stderr]
    left = sorted(path.name for path in h.teams.iterdir() if path.name.startswith("ghost"))
    if not wrong and not left and "team declare" in answers["verb-retired"].stderr:
        bench.refusals += len(asks)
        held("(b) refused at a birth, nothing written", "template-unknown, team-invalid (a path, solo with two, "
             "--budget lots), participant-unknown, the usage (--teams), verb-retired for team new, naming team "
             "declare; no teams/ghost-* left")
    else:
        failures.append(f"  ✗ (b) refused                {wrong} left={left} "
                        f"{answers['verb-retired'].stderr.strip()[-160:]!r}")

    # --- (e) a TEAM.md its template refuses -------------------------------------------------------
    S.laid(h.house / "teams" / "templates", TONED)
    wrong, before = [], {}
    for at, (code, text) in enumerate(REFUSED):
        team = f"hand-{at}"
        h.declare(team, text)
        before[team] = S.kept(h, team)
        refused = h.call("team", "start", team, "--message", "x", "--no-tick")
        verdict = S.declaration_of(h, team).get("verdict") or {}
        said = (verdict.get("refusal") or "").split(" --")[0]
        if not (refused.returncode == 2 and S.code_of(refused) == code and verdict.get("ok") is False
                and said == code and before[team][0] and before[team][1] == b""):
            wrong.append(f"{code}: rc={refused.returncode} start={S.code_of(refused)} declaration={said} "
                         f"{refused.stderr.strip()[-160:]!r}")
    faces = {verb: h.call("team", *args, "--json") for verb, args in
             (("roster", ("roster",)), ("status", ("status",)), ("delete", ("delete", team)))}
    read = {verb: [json.loads(line) for line in one.stdout.splitlines() if line.strip()]
            if one.returncode == 0 else [] for verb, one in faces.items()}
    rows = {one.get("team"): (one.get("members"), one.get("root"))
            for one in (read["roster"] or [{}])[0].get("teams") or [] if one.get("team") in before}
    badges = {one.get("team"): one.get("declared_members") for one in read["status"] if one.get("team") in before}
    gone = (read["delete"] or [{}])[0]
    moved = [one for one in before if S.kept(h, one) != before[one]]
    if (not wrong and not moved and rows == {one: (0, None) for one in before}
            and badges == {one: [] for one in before} and gone.get("dry") is True and gone.get("agents") == []
            and not any(h.agent_stands(one) for one in ("agents/m", "agents/n"))):
        bench.refusals += len(REFUSED)
        held("(e) a TEAM.md its template refuses", f"{', '.join(code for code, _ in REFUSED)} (a `daily:` key, "
             "then a front matter left open): start refuses each by its code, "
             "declaration says it with rc 0; roster and status give each no member, delete (said) no agent of the "
             "last; the teams' directories and journals byte for byte, no agent born")
    else:
        failures.append(f"  ✗ (e) the template refuses   {wrong} moved={moved} roster={rows} status={badges} "
                        f"delete={gone} faces={[one.returncode for one in faces.values()]} born="
                        f"{[one for one in ('agents/m', 'agents/n') if h.agent_stands(one)]} "
                        f"{faces['roster'].stderr.strip()[-200:]!r}")

    # --- (c) two writers at once ------------------------------------------------------------------
    races = []
    for name in ("race-1", "race-2", "race-3"):
        gate = threading.Barrier(2)
        answers: dict = {}

        def played(flag: str, value: str) -> None:
            gate.wait()
            answers[flag] = h.call("team", "declare", name, "--template", "teams/solo", flag, value)

        both = [threading.Thread(target=played, args=one) for one in (("--description", "The first."), ("--budget", "7"))]
        for one in both:
            one.start()
        for one in both:
            one.join()
        doc = h.teams / name / "TEAM.md"
        text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
        face = S.declaration_of(h, name)
        races.append(([one.returncode for one in answers.values()], sorted(S.keys_of(text)),
                      (face.get("verdict") or {}).get("ok"), face.get("description"),
                      ((face.get("declared") or {}).get("limits") or {}).get("budget"),
                      sorted(path.name for path in (h.teams / name).iterdir() if path.name != "TEAM.md")
                      if (h.teams / name).is_dir() else None))
    if all(one == ([0, 0], ["agents", "budget", "description", "template"], True, "The first.", 7, []) for one in races):
        held("(c) two writers at once", "three races --description/--budget on one name: both write, one after the "
             "other; the TEAM.md holds both keys, judged ok, nothing beside it")
    else:
        failures.append(f"  ✗ (c) two writers           {races}")

    return 0
