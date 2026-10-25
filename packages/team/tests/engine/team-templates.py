"""Scenario `team-templates` -- 7 case(s): a team is born from a TEMPLATE -- `team templates` lists them, `team new
<name> --template <t>` writes `teams/<name>/TEAM.md` judged by `start`'s own judge, and `team start` accepts it as it
stands; what `team new` is told, and what it refuses writing nothing. No wake-up plays: every start is `--no-tick`.
- (a) the templates read: `team templates` says one line per template, its first word the template's name --
  `supervisor-workers`, `lead-reviewers`, `chain`, `solo`, `empty`, `council`, `triage`, `cross-check`, `tree`;
  `--json` one object per template, its keys exactly `{template, description, members, root, reports, ceremony,
  limits, intention}`, its members and root those of the template
- (b) each template written then started (the first five): its members at `agents/<team>/<member>`, its root, its
  edges, the daily of the two forms with two members or more reporting to the root, the default limits (`budget: 5`,
  `launches: 24`, `timeout: 900`) and `schedule: off`, read at `team-started`; the intention names each member by its
  id; `empty` the smallest declaration -- no intention, no limit, the schedule `start` defaults to
- (a) the four written then started: `council`, `triage` and `cross-check` on the form `star` without a ceremony,
  `tree` with the daily of its squad leads and two levels of edges; members, root, edges, limits read at
  `team-started`; each intention names its members by their ids, no hole of the template left in it
- (b) the form tree: five members under `--squads 1` make one squad lead over three workers, no daily; four members
  under the template's two squads refuse `team-invalid`, `--squads` on `council` and `--squads 0` too -- nothing
  written, no `teams/<name>` left behind
- (a) the options: `--member` replaces the template's members in the order given, the form making the root, the
  edges and the ids of the intention again (`lead-reviewers` with one reviewer: no daily); `--principal`,
  `--budget`, `--launches`, `--timeout`, `--schedule` read at `team-started`; `--root` takes another member as the
  root, `--no-ceremony` drops the daily, `--intention-file` is the body as the file holds it; `chain` given three
  members delegates each to the next
- (b) refused, nothing written: `template-unknown`; `team-exists` on a TEAM.md already there, its bytes kept; a
  member's path `team-invalid` and a root nobody declared `participant-unknown` -- `start`'s own refusals --; `solo`
  given two members `team-invalid`; `--budget` not a number `team-invalid`; no `--template` the usage; no
  `teams/<name>` left behind
- (c) two writers at once: two `team new` of one name played at once, `solo` and `empty`, three times -- one writes,
  the other refuses `team-exists`; the TEAM.md standing is the winner's whole (its declaration judged `ok`, its
  members the winner's alone), no temporary left beside it
"""
from __future__ import annotations

import json
import re
import threading

from tests.harness import support

T = support(__file__, "team")

FIRST = ("supervisor-workers", "lead-reviewers", "chain", "solo", "empty")
TEMPLATES = FIRST + ("council", "triage", "cross-check", "tree")
KEYS = {"template", "description", "members", "root", "reports", "ceremony", "limits", "intention"}
LIMITS = {"budget": 5, "launches": 24, "timeout": 900}
# the first five: template -> (members, root, edges, the daily's line or None)
SHAPES = {
    "supervisor-workers": (["supervisor", "worker-1", "worker-2"], "supervisor",
                           [{"from": ["worker-1", "worker-2"], "to": "supervisor"}],
                           "daily every weekday 09:30 with worker-1 worker-2 -> supervisor"),
    "lead-reviewers": (["lead", "reviewer-1", "reviewer-2"], "lead",
                       [{"from": ["reviewer-1", "reviewer-2"], "to": "lead"}],
                       "daily every weekday 09:30 with reviewer-1 reviewer-2 -> lead"),
    "chain": (["step-1", "step-2", "step-3"], "step-1",
              [{"from": ["step-2"], "to": "step-1"}, {"from": ["step-3"], "to": "step-2"}], None),
    "solo": (["worker"], "worker", [], None),
    "empty": (["lead"], "lead", [], None),
}
# the four after them: template -> (members, root, edges, the daily's line or None, limits)
FORMS = {
    "council": (["facilitator", "expert-1", "expert-2", "expert-3"], "facilitator",
                [{"from": ["expert-1", "expert-2", "expert-3"], "to": "facilitator"}], None, LIMITS),
    "triage": (["dispatcher", "spec-a", "spec-b", "spec-c"], "dispatcher",
               [{"from": ["spec-a", "spec-b", "spec-c"], "to": "dispatcher"}], None, LIMITS),
    "cross-check": (["judge", "twin-1", "twin-2"], "judge",
                    [{"from": ["twin-1", "twin-2"], "to": "judge"}], None, LIMITS),
    "tree": (["lead", "squad-1", "squad-2", "worker-1", "worker-2", "worker-3", "worker-4"], "lead",
             [{"from": ["squad-1", "squad-2"], "to": "lead"}, {"from": ["worker-1", "worker-3"], "to": "squad-1"},
              {"from": ["worker-2", "worker-4"], "to": "squad-2"}],
             "daily every weekday 09:30 with squad-1 squad-2 -> lead", {"budget": 10, "launches": 24, "timeout": 900}),
}
# every template as `templates --json` says it: template -> (members, root)
LISTED = {**{one: shape[:2] for one, shape in SHAPES.items()}, **{one: shape[:2] for one, shape in FORMS.items()}}
HAND = "---\nagents: |\n  m agents/m\nroot: m\n---\nThe owner's own words.\n"


def intention_of(text: str) -> str:
    """-> the body of a TEAM.md, after its front matter; '' when it has none."""
    return text.split("---\n", 2)[-1].strip() if text.startswith("---\n") else ""


def names_all(intention: str, members: list[str]) -> bool:
    """-> whether the intention carries every member's id, as the templates mark one: `<id>`."""
    return all(f"`{one}`" in intention for one in members)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind = T.by_kind

    def started_from(team: str):
        """-> (the TEAM.md's text, `team start` played on it, the journal's `team-started`)."""
        doc = h.teams / team / "TEAM.md"
        text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
        started = h.call("team", "start", team, "--message", "go", "--no-tick", now="07:50")
        return text, started, next(iter(by_kind(h.events(team), "team-started")), {})

    # --- (a) the templates read -----------------------------------------------------------------
    listed = h.call("team", "templates")
    said = [line.split()[0] for line in listed.stdout.splitlines() if line.strip()]
    faced = h.call("team", "templates", "--json")
    objects = [json.loads(line) for line in faced.stdout.splitlines() if line.strip()] if faced.returncode == 0 else []
    if (listed.returncode == 0 and said == list(TEMPLATES) and len(objects) == len(TEMPLATES)
            and all(set(one) == KEYS for one in objects) and [one["template"] for one in objects] == list(TEMPLATES)
            and all((one["members"], one["root"]) == LISTED[one["template"]] for one in objects)):
        held("(a) the templates read", f"nine lines ({', '.join(said)}); --json nine objects, keys {sorted(KEYS)}")
    else:
        failures.append(f"  ✗ (a) templates              rc={listed.returncode}/{faced.returncode} said={said} "
                        f"objects={[sorted(one) for one in objects][:1]} {(listed.stderr or faced.stderr).strip()[-160:]!r}")

    # --- (b) each of the first five written, then started ---------------------------------------
    wrong = []
    for template in FIRST:
        team = f"t-{template}"
        made = h.call("team", "new", team, "--template", template)
        text, started, first = started_from(team)
        members, root, edges, daily = SHAPES[template]
        intention = intention_of(text)
        named = intention == "" if template == "empty" else names_all(intention, members)
        if not (made.returncode == 0 and text and started.returncode == 0
                and first.get("agents") == {one: f"agents/{team}/{one}" for one in members}
                and first.get("root") == root and first.get("reports") == edges
                and [one.get("text") for one in first.get("ceremonies") or []] == ([daily] if daily else [])
                and first.get("limits") == ({} if template == "empty" else LIMITS)
                and first.get("schedule") == (5 if template == "empty" else None) and named):
            wrong.append(f"{template}: rc={made.returncode}/{started.returncode} agents={first.get('agents')} "
                         f"root={first.get('root')} reports={first.get('reports')} limits={first.get('limits')} "
                         f"schedule={first.get('schedule')} named={named} "
                         f"{(made.stderr or started.stderr).strip()[-160:]!r}")
    if not wrong:
        held("(b) each template written then started", "five teams written by `team new` and started as they "
             "stand: members at agents/<team>/<member>, root, edges, the daily of the two wide forms, the default "
             "limits, schedule off; each intention names its members, `empty` none")
    else:
        failures.extend(f"  ✗ (b) {one}" for one in wrong)

    # --- (a) the four after them written, then started ------------------------------------------
    wrong = []
    for template, (members, root, edges, daily, limits) in FORMS.items():
        team = f"t-{template}"
        made = h.call("team", "new", team, "--template", template)
        text, started, first = started_from(team)
        intention = intention_of(text)
        if not (made.returncode == 0 and started.returncode == 0
                and first.get("agents") == {one: f"agents/{team}/{one}" for one in members}
                and first.get("root") == root and first.get("reports") == edges
                and [one.get("text") for one in first.get("ceremonies") or []] == ([daily] if daily else [])
                and first.get("limits") == limits and first.get("schedule") is None
                and names_all(intention, members) and not re.search(r"\{[a-z]+\}", intention)):
            wrong.append(f"{template}: rc={made.returncode}/{started.returncode} agents={first.get('agents')} "
                         f"root={first.get('root')} reports={first.get('reports')} limits={first.get('limits')} "
                         f"ceremonies={first.get('ceremonies')} named={names_all(intention, members)} "
                         f"{(made.stderr or started.stderr).strip()[-160:]!r}")
    if not wrong:
        held("(a) the four written then started", "council, triage, cross-check (star, no daily) and tree (lead over "
             "two squad leads over two workers each, the squads' daily, budget 10 launches 24) written by `team new` "
             "and started as they stand; each intention names its members, no hole left")
    else:
        failures.extend(f"  ✗ (a) {one}" for one in wrong)

    # --- (b) the form tree, and what it refuses ---------------------------------------------------
    one_squad = h.call("team", "new", "small", "--template", "tree", "--squads", "1", "--member", "l", "agents/s/l",
                       "--member", "s", "agents/s/s", "--member", "a", "agents/s/a", "--member", "b", "agents/s/b",
                       "--member", "c", "agents/s/c")
    _, started, first = started_from("small")
    asks = {
        "four members, two squads": ("ghost-tree-1", "--template", "tree", "--member", "l", "agents/g/l", "--member",
                                     "s", "agents/g/s", "--member", "t", "agents/g/t", "--member", "w", "agents/g/w"),
        "--squads off tree": ("ghost-tree-2", "--template", "council", "--squads", "2"),
        "--squads 0": ("ghost-tree-3", "--template", "tree", "--squads", "0"),
    }
    answers = {why: h.call("team", "new", *args) for why, args in asks.items()}
    refused = [f"{why}: rc={one.returncode} {one.stderr.strip()[-160:]!r}" for why, one in answers.items()
               if one.returncode != 2 or "team-invalid" not in one.stderr]
    left = sorted(path.name for path in (h.teams.iterdir() if h.teams.is_dir() else ()) if path.name.startswith("ghost"))
    if (one_squad.returncode == 0 and started.returncode == 0 and first.get("root") == "l"
            and first.get("reports") == [{"from": ["s"], "to": "l"}, {"from": ["a", "b", "c"], "to": "s"}]
            and first.get("ceremonies") == [] and not refused and not left):
        bench.refusals += len(asks)
        held("(b) the form tree", "--squads 1 on five members: s -> l, a b c -> s, no daily; team-invalid for four "
             "members under two squads, --squads on council, --squads 0; no teams/ghost-* left")
    else:
        failures.append(f"  ✗ (b) tree                   rc={one_squad.returncode}/{started.returncode} "
                        f"root={first.get('root')} reports={first.get('reports')} refused={refused} left={left} "
                        f"{(one_squad.stderr or started.stderr).strip()[-160:]!r}")

    # --- (a) the options --------------------------------------------------------------------------
    told = h.call("team", "new", "pairing", "--template", "lead-reviewers", "--member", "writer", "agents/x/writer",
                  "--member", "critic", "agents/x/critic", "--principal", "pm", "--principal", "boss",
                  "--budget", "12.5", "--launches", "3", "--timeout", "60", "--schedule", "10")
    text, started, first = started_from("pairing")
    own = bench.temp() / "intention.md"
    own.write_text("Each member must answer `hi`.\n", encoding="utf-8")
    rooted = h.call("team", "new", "rooted", "--template", "supervisor-workers", "--root", "worker-2",
                    "--no-ceremony", "--intention-file", str(own))
    rooted_text, started_r, first_r = started_from("rooted")
    chained = h.call("team", "new", "line", "--template", "chain", "--member", "a", "agents/l/a", "--member", "b",
                     "agents/l/b", "--member", "c", "agents/l/c")
    _, started_c, first_c = started_from("line")
    pairing = intention_of(text)
    if (told.returncode == 0 and started.returncode == 0
            and first.get("agents") == {"writer": "agents/x/writer", "critic": "agents/x/critic"}
            and first.get("root") == "writer" and first.get("reports") == [{"from": ["critic"], "to": "writer"}]
            and first.get("ceremonies") == [] and first.get("principals") == ["pm", "boss"]
            and first.get("limits") == {"budget": 12.5, "launches": 3, "timeout": 60} and first.get("schedule") == 10
            and names_all(pairing, ["writer", "critic"]) and not names_all(pairing, ["lead"])
            and rooted.returncode == 0 and started_r.returncode == 0 and first_r.get("root") == "worker-2"
            and first_r.get("reports") == [{"from": ["supervisor", "worker-1"], "to": "worker-2"}]
            and first_r.get("ceremonies") == [] and rooted_text.endswith("---\n" + own.read_text(encoding="utf-8"))
            and chained.returncode == 0 and started_c.returncode == 0 and first_c.get("root") == "a"
            and first_c.get("reports") == [{"from": ["b"], "to": "a"}, {"from": ["c"], "to": "b"}]):
        held("(a) the options", "--member writer critic: root writer, critic -> writer, no daily, the intention "
             "names them; principals pm boss, budget 12.5, launches 3, timeout 60, schedule 10; --root worker-2 "
             "--no-ceremony --intention-file; chain a b c: b -> a, c -> b")
    else:
        failures.append(f"  ✗ (a) options                rc={told.returncode}/{started.returncode}/{rooted.returncode}/"
                        f"{started_r.returncode}/{chained.returncode}/{started_c.returncode} first={first} "
                        f"rooted={first_r.get('root')}/{first_r.get('reports')} chain={first_c.get('reports')} "
                        f"{(told.stderr or started.stderr or rooted.stderr or chained.stderr).strip()[-200:]!r}")

    # --- (b) refused, nothing written -------------------------------------------------------------
    h.declare("kept", HAND)
    before = (h.teams / "kept" / "TEAM.md").read_bytes()
    asks = {
        "template-unknown": ("ghost-1", "--template", "pair"),
        "team-exists": ("kept", "--template", "solo"),
        "team-invalid": ("ghost-2", "--template", "solo", "--member", "w", "Bad/Path"),
        "participant-unknown": ("ghost-3", "--template", "supervisor-workers", "--root", "nobody"),
        "team-invalid ": ("ghost-4", "--template", "solo", "--member", "a", "agents/a", "--member", "b", "agents/b"),
        "team-invalid  ": ("ghost-5", "--template", "solo", "--budget", "lots"),
        "usage": ("ghost-6",),
    }
    answers = {code: h.call("team", "new", *args) for code, args in asks.items()}
    wrong = [f"{code.strip()}: rc={one.returncode} {one.stderr.strip()[-160:]!r}" for code, one in answers.items()
             if one.returncode != 2 or code.strip() not in one.stderr]
    left = sorted(path.name for path in h.teams.iterdir() if path.name.startswith("ghost"))
    if not wrong and not left and (h.teams / "kept" / "TEAM.md").read_bytes() == before:
        bench.refusals += len(asks)
        held("(b) refused, nothing written", "template-unknown, team-exists (the TEAM.md kept to the byte), "
             "team-invalid (a path, solo with two, --budget lots), participant-unknown, the usage; no teams/ghost-* "
             "left")
    else:
        failures.append(f"  ✗ (b) refused                {wrong} left={left}")

    # --- (c) two writers at once ------------------------------------------------------------------
    races = []
    for name in ("race-1", "race-2", "race-3"):
        gate = threading.Barrier(2)
        answers: dict = {}

        def played(template: str) -> None:
            gate.wait()
            answers[template] = h.call("team", "new", name, "--template", template)

        both = [threading.Thread(target=played, args=(one,)) for one in ("solo", "empty")]
        for one in both:
            one.start()
        for one in both:
            one.join()
        won = [template for template, one in answers.items() if one.returncode == 0]
        lost = [one for one in answers.values() if one.returncode != 0]
        doc = h.teams / name / "TEAM.md"
        text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
        read = h.call("team", "declaration", name, "--json")
        face = json.loads(read.stdout) if read.returncode == 0 else {}
        agents = [(one.get("member"), one.get("path")) for one in (face.get("declared") or {}).get("agents") or []]
        mark = {"solo": [("worker", f"agents/{name}/worker")], "empty": [("lead", f"agents/{name}/lead")]}
        races.append((won, [one.returncode for one in lost], all("team-exists" in one.stderr for one in lost),
                      len(won) == 1 and (face.get("verdict") or {}).get("ok") is True and agents == mark[won[0]]
                      and text.endswith("\n"),
                      sorted(path.name for path in (h.teams / name).iterdir() if path.name != "TEAM.md")))
    if all(len(won) == 1 and codes == [2] and exists and whole and not rest for won, codes, exists, whole, rest in races):
        bench.refusals += len(races)
        held("(c) two writers at once", f"three races solo/empty: one writes ({', '.join(one[0][0] for one in races)}), "
             "the other refuses team-exists; the TEAM.md the winner's whole, nothing beside it")
    else:
        failures.append(f"  ✗ (c) two writers           {races}")
    return 0
