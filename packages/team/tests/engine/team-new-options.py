"""Scenario `team-new-options` -- 3 case(s) (batch les-modeles-d-equipe, 2026-10-11: row 79 of the study § 18,
team 0.25.0): what `team new` is told, and what it refuses -- writing nothing.
- (a) the options: `--member` replaces the template's members in the order given, the form making the root, the
  edges and the names of the intention again (`lead-reviewers` with one reviewer: no daily); `--principal`,
  `--budget`, `--wakes`, `--timeout`, `--schedule` read at `team-started`; `--root` takes another member as the
  root, `--no-ceremony` drops the daily, `--intention-file` is the body; `chain` given three members delegates
  each to the next
- (b) refused, nothing written: `template-unknown`; `team-exists` on a TEAM.md already there, its bytes kept;
  a member's path `team-invalid` and a root nobody declared `participant-unknown` -- `start`'s own refusals --;
  `solo` given two members `team-invalid`; `--budget` not a number `team-invalid`; no `--template` the usage;
  no `teams/<name>` left behind
- (c) two writers (KC33): two `team new` of one name played at once, `solo` and `empty`, three times -- one writes,
  the other refuses `team-exists`; the TEAM.md standing is the winner's whole, no temporary left beside it
"""
from __future__ import annotations

import threading

from tests.harness import support

T = support(__file__, "team")

HAND = "---\nagents: |\n  m agents/m\nroot: m\n---\nThe owner's own words.\n"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind = T.by_kind

    # --- (a) the options --------------------------------------------------------------------------
    told = h.call("team", "new", "pairing", "--template", "lead-reviewers", "--member", "writer", "agents/x/writer",
                  "--member", "critic", "agents/x/critic", "--principal", "pm", "--principal", "boss",
                  "--budget", "12.5", "--wakes", "3", "--timeout", "60", "--schedule", "10")
    text = (h.teams / "pairing" / "TEAM.md").read_text(encoding="utf-8") if told.returncode == 0 else ""
    started = h.call("team", "start", "pairing", "--message", "go", "--no-tick", now="07:50")
    first = next(iter(by_kind(h.events("pairing"), "team-started")), {})
    own = bench.temp() / "intention.md"
    own.write_text("Each member must answer `hi`.\n", encoding="utf-8")
    rooted = h.call("team", "new", "rooted", "--template", "supervisor-workers", "--root", "worker-2",
                    "--no-ceremony", "--intention-file", str(own))
    rooted_text = (h.teams / "rooted" / "TEAM.md").read_text(encoding="utf-8") if rooted.returncode == 0 else ""
    started_r = h.call("team", "start", "rooted", "--message", "go", "--no-tick", now="07:50")
    first_r = next(iter(by_kind(h.events("rooted"), "team-started")), {})
    chained = h.call("team", "new", "line", "--template", "chain", "--member", "a", "agents/l/a", "--member", "b",
                     "agents/l/b", "--member", "c", "agents/l/c")
    started_c = h.call("team", "start", "line", "--message", "go", "--no-tick", now="07:50")
    first_c = next(iter(by_kind(h.events("line"), "team-started")), {})
    if (told.returncode == 0 and started.returncode == 0
            and first.get("agents") == {"writer": "agents/x/writer", "critic": "agents/x/critic"}
            and first.get("root") == "writer" and first.get("reports") == [{"from": ["critic"], "to": "writer"}]
            and first.get("ceremonies") == [] and first.get("principals") == ["pm", "boss"]
            and first.get("limits") == {"budget": 12.5, "wakes": 3, "timeout": 60} and first.get("schedule") == 10
            and "`writer`" in text and "`critic`" in text and "`lead`" not in text
            and rooted.returncode == 0 and started_r.returncode == 0 and first_r.get("root") == "worker-2"
            and first_r.get("reports") == [{"from": ["supervisor", "worker-1"], "to": "worker-2"}]
            and first_r.get("ceremonies") == [] and rooted_text.endswith("---\nEach member must answer `hi`.\n")
            and chained.returncode == 0 and started_c.returncode == 0 and first_c.get("root") == "a"
            and first_c.get("reports") == [{"from": ["b"], "to": "a"}, {"from": ["c"], "to": "b"}]):
        held("(a) the options", "--member writer critic: root writer, critic -> writer, no daily, the intention "
             "names them; principals pm boss, budget 12.5, wakes 3, timeout 60, schedule 10; --root worker-2 "
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
        text = (h.teams / name / "TEAM.md").read_text(encoding="utf-8") if (h.teams / name / "TEAM.md").is_file() else ""
        mark = {"solo": f"worker agents/{name}/worker", "empty": f"lead agents/{name}/lead"}
        races.append((won, [one.returncode for one in lost], all("team-exists" in one.stderr for one in lost),
                      len(won) == 1 and mark[won[0]] in text and text.endswith("\n")
                      and not any(other in text for key, other in mark.items() if key != won[0]),
                      sorted(path.name for path in (h.teams / name).iterdir() if path.name != "TEAM.md")))
    if all(len(won) == 1 and codes == [2] and exists and whole and not rest for won, codes, exists, whole, rest in races):
        bench.refusals += len(races)
        held("(c) two writers at once", f"three races solo/empty: one writes ({', '.join(one[0][0] for one in races)}), "
             "the other refuses team-exists; the TEAM.md the winner's whole, nothing beside it")
    else:
        failures.append(f"  ✗ (c) two writers           {races}")
    return 0
