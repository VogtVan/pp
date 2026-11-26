"""Scenario `team-declaration-season` -- 2 cases (batch la-saison-ecrite, split out of `team-declaration` by rule
10): `team declaration --json` says the season a start without a flag opens and its gap to the season under way.
- (a) the season declared: a `SEASON.md` with a model and a profile -- `declared.season` says `{launch, limits,
  packages, profiles, work}` as the next start without a flag opens it; started, `pending: []`; the model and a budget
  changed, `pending` on `launch` and `season` with the start's values and the file's; a budget of 0, rc 0 and
  `verdict {ok: false}` with `budget-invalid`, the team's directory and journal byte for byte
- (b) the launch keys written by `declare` (batch les-cles-de-lancement-ecrites): `team declare <team> --season
  --budget 5 --member sx --model x --json` writes SEASON.md as `team start` with the same flags writes its twin, byte
  for byte -- the season's word and the other keys at their bytes --, `written` `["budget", "profiles"]`, the verdict
  ok, no journal; refused as `start` refuses them, SEASON.md byte for byte: `--member ghost --model x`
  `participant-unknown` (the code `start` gives), `--harness h` without its provider `grammar-missing`
"""
from __future__ import annotations

import json

from conductor import instance
from tests.harness import support

T = support(__file__, "team")
S = support(__file__, "templates")


def code(said: str) -> str:
    """-> the refusal's code: the first token of what pp-team says, after its name."""
    words = said.strip().removeprefix("pp-team: ").split()
    return words[0].rstrip(":") if words else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={}, packages=("agent", "team", "steering", "plan"))
    base = instance.base_of(h.house)
    pinned = [name for name in instance.pins(h.house) if name != base]

    def declaration(name: str) -> dict:
        played = h.call("team", "declaration", name, "--json")
        try:
            return json.loads(played.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    # --- (a) the season declared ----------------------------------------------------------------------------------
    h.declare("sw", "---\nagents: |\n  sx agents/sx\nroot: sx\nschedule: off\n---\nA season declared.\n")
    written = h.teams / "sw" / "SEASON.md"
    written.write_text("---\nmodel: m1\nprofiles: |\n  sx effort=high\n---\n", encoding="utf-8")
    seen = (declaration("sw").get("declared") or {}).get("season") or {}
    opened = h.call("team", "start", "sw", "--no-tick")
    quiet = declaration("sw")
    written.write_text("---\nmodel: m2\nbudget: 4\nprofiles: |\n  sx effort=high\n---\n", encoding="utf-8")
    shifted = {one.get("key"): one for one in declaration("sw").get("pending") or []}
    written.write_text("---\nbudget: 0\n---\n", encoding="utf-8")
    before = S.kept(h, "sw")
    zero = declaration("sw")
    same = S.kept(h, "sw") == before
    packages = {str(one).partition("=")[0]: str(one).partition("=")[2] for one in seen.get("packages") or []}
    if (seen.get("launch") == {"model": "m1"} and seen.get("limits") == {} and seen.get("work") is None
            and seen.get("profiles") == {"sx": {"effort": "high"}}
            and packages == {name: "on" if name in ("agent", "team") else "off" for name in pinned}
            and opened.returncode == 0 and quiet.get("pending") == [] and list(shifted) == ["launch", "season"]
            and shifted["launch"].get("started") == {"model": "m1"} and shifted["launch"].get("declared") == {"model": "m2"}
            and shifted["season"].get("started") == {} and shifted["season"].get("declared") == {"budget": 4.0}
            and (zero.get("verdict") or {}).get("ok") is False
            and code((zero.get("verdict") or {}).get("refusal") or "") == "budget-invalid" and same):
        held("(a) the season declared", "declared.season the launch m1, sx's profile, the set; started: pending []; "
             "m2 and budget 4: pending launch and season; budget 0: verdict budget-invalid, nothing written")
    else:
        failures.append(f"  ✗ (a) the season declared    seen={seen} rc={opened.returncode} quiet={quiet.get('pending')} "
                        f"shifted={shifted} zero={zero.get('verdict')} same={same} {opened.stderr.strip()[-200:]!r}")

    # --- (b) the launch keys written by `declare`, as `start` writes them ----------------------------------------------
    season = "---\nmodel: m1\nprofiles: |\n  sx effort=high\n---\nThe season's word.\n"
    for twin in ("dl", "st", "gh"):
        h.declare(twin, "---\nagents: |\n  sx agents/sx\nroot: sx\nschedule: off\n---\nTwins.\n")
        (h.teams / twin / "SEASON.md").write_text(season, encoding="utf-8")
    budgeted, membered = ("--budget", "5"), ("--member", "sx", "--model", "x")
    declared_dl = h.call("team", "declare", "dl", "--season", *budgeted, *membered, "--json")
    try:
        face = json.loads(declared_dl.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        face = {}
    started_st = h.call("team", "start", "st", *budgeted, "--no-tick", *membered)
    dl_season, st_season = ((h.teams / twin / "SEASON.md").read_text(encoding="utf-8") for twin in ("dl", "st"))
    kept = S.kept(h, "dl")
    ghost = h.call("team", "declare", "dl", "--season", "--member", "ghost", "--model", "x", "--json")
    ghost_start = h.call("team", "start", "gh", "--no-tick", "--member", "ghost", "--model", "x")
    harness = h.call("team", "declare", "dl", "--season", "--harness", "h", "--json")
    if (declared_dl.returncode == 0 and started_st.returncode == 0 and dl_season == st_season and dl_season != season
            and dl_season.endswith("---\nThe season's word.\n") and face.get("written") == ["budget", "profiles"]
            and (face.get("verdict") or {}).get("ok") is True and not h.journal_of("dl").exists()
            and ghost.returncode == 2 and code(ghost.stderr) == code(ghost_start.stderr) == "participant-unknown"
            and harness.returncode == 2 and code(harness.stderr) == "grammar-missing" and S.kept(h, "dl") == kept):
        bench.refusals += 2
        held("(b) the launch keys written by declare", "--budget 5 --member sx --model x: SEASON.md the bytes start "
             "writes for the same flags, written [budget, profiles], verdict ok, no journal; --member ghost "
             "participant-unknown as start, --harness alone grammar-missing, SEASON.md byte for byte")
    else:
        failures.append(f"  ✗ (b) launch keys declared    rc={declared_dl.returncode}/{started_st.returncode}/"
                        f"{ghost.returncode}/{harness.returncode} face={face} dl={dl_season!r} st={st_season!r} "
                        f"codes={code(ghost.stderr)}/{code(ghost_start.stderr)}/{code(harness.stderr)} "
                        f"{(declared_dl.stderr or started_st.stderr).strip()[-200:]!r}")
    return 0
