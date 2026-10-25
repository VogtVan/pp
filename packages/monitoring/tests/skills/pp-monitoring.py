"""Scenario `pp-monitoring` -- the analyses of the measure (plan pp-split, batches
le-package-monitoring + la-codification-des-scenarios + les-procs-de-campagne +
le-parametrage-de-conduction) -- 10 case(s):
- setup declares a PLAYBOOK analysis; run refuses capture-off while the switch is false
- derive builds the disposable repo from the instance (pins and settings copied, member
  neutral, records empty) and refuses a non-empty target
- armed, run plays the playbook on the derived repo -- fixture executed, one run per
  session -- and report renders volume by subject and package, tokens ~
- the replay holds: a second run plays the same book again
- the guards: composition-short on missing pins, analysis-unknown, analysis-taken
- every report opens on the HEADER (versions, llm, settings) and a conduite campaign
  (live traces, no mechanical run) reports too -- said LIVE
- the transcript pairing bounds to the LIVE run: a dead run in the same Claude log never
  shifts the by-turn labels; the window is read from the traces (_pair, _live_window)
- an ARCHIVE reads back with the same grammar: setup over the directory a campaign left,
  report says ARCHIVED and renders the live volume, the stamped turns and the levers; run
  refuses (an archive is never played), an empty directory refuses by name
- the console plays the skill: `./pp -s pp-monitoring list` hands the arguments without the
  program name, and the skill lists as it does run by hand
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from conductor.packaging import contributions

BOOK = """composition: kit

## S1 -- the bare surface

shell: touch seed-was-here.txt

| id | gesture | expected |
|---|---|---|
| S1.01 | hello | the boot renders the catalog |
| S1.02 | end of session | -- |

## S2 -- one more exchange

| id | gesture | expected |
|---|---|---|
| S2.01 | where do we stand? | -- |
"""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("monskill", ("monitoring",))
    made = env.made
    book = made.parent / "playbook.md"
    book.write_text(BOOK, encoding="utf-8")

    rc, out, err = contributions.run_skill(made, "pp-monitoring",
                                           ["setup", "boot-nu", str(made), str(book)])
    rc2, _, err2 = contributions.run_skill(made, "pp-monitoring", ["run", "boot-nu"])
    if rc == 0 and "2 session(s)" in out and rc2 == 2 and "capture-off" in err2:
        held("setup reads the playbook, run stays gated",
             "2 sessions declared from the book; capture-off named while false")
    else:
        failures.append(f"  ✗ setup / gate               rc={rc}/{rc2} {out[-80:]!r} {err2[-60:]!r}")

    target = made.parent / "derived"
    rc3, out3, _ = contributions.run_skill(made, "pp-monitoring", ["derive", str(target)])
    meta2 = target / made.name
    rc3b, _, err3b = contributions.run_skill(made, "pp-monitoring", ["derive", str(target)])
    if (rc3 == 0 and (meta2 / ".sys" / "vendor").is_dir()
            and (meta2 / "SETTINGS.md").is_file()
            and "neutral" in (meta2 / "MEMBER.md").read_text(encoding="utf-8")
            and not list((meta2 / ".sys" / "records").glob("*"))
            and rc3b == 2 and "target-not-empty" in err3b):
        held("derive builds the disposable repo",
             "pins and settings copied, member neutral, records empty; a held target refuses")
    else:
        failures.append(f"  ✗ derive                     rc={rc3}/{rc3b} {err3b[-60:]!r}")

    env.write("SETTINGS.md", env.read("SETTINGS.md")
              .replace("monitoring_capture: false", "monitoring_capture: true"))
    contributions.run_skill(made, "pp-monitoring", ["setup", "derive-nu", str(meta2), str(book)])
    rc4, out4, err4 = contributions.run_skill(made, "pp-monitoring", ["run", "derive-nu"])
    rc5, out5, _ = contributions.run_skill(made, "pp-monitoring", ["report", "derive-nu"])
    state = json.loads((made / ".sys" / "records" / "monitoring.json").read_text(encoding="utf-8"))
    if (rc4 == 0 and "2 session(s)" in out4
            and (target / "seed-was-here.txt").is_file()
            and len(state["derive-nu"].get("traces", [])) == 2
            and rc5 == 0 and "standing orders" in out5 and "~" in out5):
        held("the playbook plays on the derived repo",
             "the fixture ran, one run per session (2 traces kept), the report renders")
    else:
        failures.append(f"  ✗ playbook run               rc={rc4}/{rc5} {err4[-100:]!r}")

    rc6, out6, _ = contributions.run_skill(made, "pp-monitoring", ["run", "derive-nu"])
    if rc6 == 0 and "2 session(s)" in out6:
        held("the replay holds", "the same book plays again, 2 sessions anew")
    else:
        failures.append(f"  ✗ replay                     rc={rc6} {out6[-80:]!r}")

    short = made.parent / "short.md"
    short.write_text(BOOK.replace("composition: kit", "composition: kit steering"),
                     encoding="utf-8")
    contributions.run_skill(made, "pp-monitoring", ["setup", "trop-court", str(meta2), str(short)])
    rc7, _, err7 = contributions.run_skill(made, "pp-monitoring", ["run", "trop-court"])
    rc_c, _, err_c = contributions.run_skill(made, "pp-monitoring", ["conduite", "derive-nu"])
    if rc_c == 2 and "transcript-missing" in err_c:
        held("conduite refuses without a harness transcript",
             "transcript-missing named -- the conduite reads Claude's own log")
    else:
        failures.append(f"  ✗ conduite guard             rc={rc_c} {err_c[-60:]!r}")

    contributions.run_skill(made, "pp-monitoring", ["setup", "vivante", str(meta2), str(book)])
    rc_l, out_l, _ = contributions.run_skill(made, "pp-monitoring", ["report", "vivante"])
    if (rc_l == 0 and "LIVE (no mechanical run)" in out_l
            and "header   versions" in out_l and "header   llm" in out_l
            and "header   settings" in out_l and "header" in out5):
        held("the header opens every report, live traces report too",
             "versions/llm/settings lines on both; the conduite campaign said LIVE")
    else:
        failures.append(f"  ✗ header / live report       rc={rc_l} {out_l[-120:]!r}")

    rc8, _, err8 = contributions.run_skill(made, "pp-monitoring", ["report", "jamais-vue"])
    rc9, _, err9 = contributions.run_skill(made, "pp-monitoring",
                                           ["setup", "boot-nu", str(made), str(book)])
    if (rc7 == 2 and "composition-short" in err7
            and rc8 == 2 and "analysis-unknown" in err8
            and rc9 == 2 and "analysis-taken" in err9):
        held("the guards hold", "composition-short, analysis-unknown, analysis-taken by name")
    else:
        failures.append(f"  ✗ guards                     {err7[-50:]!r} {err8[-40:]!r} {err9[-40:]!r}")

    # the transcript pairing bounds to the LIVE run: a dead run left in the same Claude log
    # (its messages hours before the live traces) never shifts the by-turn labels, and the
    # live window is read from the traces (reprise of les-procs-de-campagne, 2026-09-03).
    import importlib.util as _il
    from datetime import datetime as _dt, timezone as _tz, timedelta as _td
    src = Path(__file__).resolve().parents[2] / "skills" / "pp-monitoring" / "pp-monitoring.py"
    import sys as _sys
    spec = _il.spec_from_file_location("pp_monitor_mod", src)
    mod = _il.module_from_spec(spec); _sys.modules[spec.name] = mod   # a dataclass resolves
    spec.loader.exec_module(mod)                                       # its annotations here
    base = _dt(2026, 9, 3, 17, 15, tzinfo=_tz.utc)
    dead = [(base - _td(hours=2), "dead one"), (base - _td(hours=2, seconds=-30), "dead two")]
    live = [(base, "live one"), (base + _td(seconds=60), "live two"),
            (base + _td(seconds=120), "live three")]
    ops = sorted(dead + live, key=lambda one: one[0])
    turns = [{"start": base + _td(seconds=1)}, {"start": base + _td(seconds=61)},
             {"start": base + _td(seconds=121)}]
    labels = [t["op"] for t in mod._pair(turns, ops)]
    repo = made.parent / "winrepo"; (repo / ".sys" / "state").mkdir(parents=True)
    (repo / ".sys" / "state" / "session-a.jsonl").write_text(
        json.dumps({"at": "2026-09-03T17:15:00+00:00", "kind": "new"}) + "\n"
        + "not json -- a torn line the window skips\n"
        + json.dumps({"at": "2026-09-03T17:20:00+00:00", "kind": "turn-end"}) + "\n",
        encoding="utf-8")
    window = mod._live_window(mod.Source(repo))
    within = window is not None and window[0] < base + _td(seconds=1) < window[1]
    outside = window is not None and not (window[0] <= dead[0][0] <= window[1])
    if labels == ["live one", "live two", "live three"] and within and outside:
        held("the transcript pairing bounds to the live run",
             "a dead run's messages are discarded, each live turn keeps its own message; the "
             "window is derived from the traces, a torn line skipped, a dead run outside it")
    else:
        failures.append(f"  ✗ pairing / window           {labels!r} within={within} outside={outside}")

    # the ARCHIVE: a campaign's traces copied to a directory read back with the same grammar
    # (le-parametrage-de-conduction, 2026-09-05) -- setup over the directory, report says
    # ARCHIVED and renders the same volume as the live analysis, the by-turn table on the
    # stamps the copies carry, the levers; run refuses (an archive is read, never played);
    # an empty directory refuses by name
    archive = made.parent / "archive-nu"; archive.mkdir()
    for one in state["derive-nu"]["traces"]:
        copied = archive / Path(one).name
        shutil.copy2(one, copied)
        with copied.open("a", encoding="utf-8") as tail:      # the stamp a hook would leave
            tail.write(json.dumps({"at": "2026-09-05T08:00:00+00:00", "kind": "turn-end"}) + "\n")
    rc_a, out_a, _ = contributions.run_skill(made, "pp-monitoring", ["setup", "archive-nu", str(archive)])
    rc_b, out_b, _ = contributions.run_skill(made, "pp-monitoring", ["report", "archive-nu"])
    rc_r, _, err_r = contributions.run_skill(made, "pp-monitoring", ["run", "archive-nu"])
    empty = made.parent / "archive-vide"; empty.mkdir()
    rc_e, _, err_e = contributions.run_skill(made, "pp-monitoring", ["setup", "archive-vide", str(empty)])

    def volume(text: str) -> str:
        return next((one for one in text.splitlines() if one.startswith("  volume (c)")), "")
    rows = [one for one in out_b.splitlines() if re.match(r"^ +\d+  ", one)]
    if (rc_a == 0 and "2 trace(s)" in out_a and rc_b == 0 and "ARCHIVED" in out_b
            and "header   archive" in out_b and volume(out_b) == volume(out5) and volume(out5)
            and len(rows) == 2 and "lever    proc_body_serve" in out_b
            and rc_r == 2 and "analysis-archived" in err_r
            and rc_e == 2 and "archive-empty" in err_e):
        held("the archive reads back with the same grammar",
             "setup over the directory, report ARCHIVED with the live volume, 2 stamped "
             "turns, the levers; run and an empty directory refuse by name")
    else:
        failures.append(f"  ✗ archive                    rc={rc_a}/{rc_b}/{rc_r}/{rc_e} "
                        f"rows={len(rows)} {out_b[-160:]!r} {err_r[-50:]!r} {err_e[-50:]!r}")

    # --- played through the console: the arguments arrive without the program name ------
    played = bench.env("gesture", ("monitoring",))
    (played.made / "procs" / "CAPABILITIES.md").write_text(
        "---\nname: CAPABILITIES\ntools: |\n  +pp-monitoring\n---\n", encoding="utf-8")
    played.cli("-new")
    listed = played.cli("-s", "pp-monitoring", "list")
    if listed.returncode == 0 and "pp-monitoring: no analysis declared" in listed.stdout:
        held("the console plays the skill",
             "`./pp -s pp-monitoring list` lists like the program itself -- the verb read "
             "from the arguments the console hands over")
    else:
        failures.append(f"  ✗ console gesture            rc={listed.returncode} "
                        f"{(listed.stdout + listed.stderr).strip().splitlines()[:2]!r}")
    return len(failures)
