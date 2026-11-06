"""Scenario `team-season-packages` -- 4 case(s) (batches les-reglages-de-la-saison, 2026-11-03, and la-saison-fait-foi,
2026-11-05): a season carries the SET of a member's packages -- one `<name>=on|off` per pin of the house beyond its base,
on when the season switches it on or the team requires it, off otherwise -- composed at the start, written whole at the
journal and handed whole at every wake-up: the member's SETTINGS decides no package. One house pinning `agent`, `team`,
`steering`, `plan` and `doc` (requires steering); the profiles themselves are `team-season-profiles`'s.
- (e) the team's `--package` and the profile that covers it: `--package plan=off --member d --package plan=on` --
  `team-started.packages` and `profiles[d].packages` the whole set, c's run plays `plan` off, d's on, every pin
  written at its run's own switches; `launch.packages` and `members[].launch.packages` say the set
- (f) `package-dependency`: `--package doc=on --package steering=off` refuses by its name -- no journal, no agent
  born; the same composition judged for a member (`--member c --package steering=off` over `--package doc=on`)
- (g) a silent season over a member's SETTINGS: m born first, its SETTINGS switching `plan` on, a season without
  `--package` -- its first block's heading says `plan` off, no `pp-plan` among its TOOLS, its run's switches name
  every pin: the required on, the rest off
- (h) a journal of before (team 0.49.0, `packages: [plan=off]`): `status --json` says the set -- `plan` off, every
  other pin the team does not require off -- at `launch.packages`, `members[].launch.packages` and the member's
  `packages`
"""
from __future__ import annotations

import re

from conductor import persistence, settings
from tests.harness import support

T = support(__file__, "team")

REFUSAL = re.compile(r"^pp-team: ([a-z][a-z-]*)", re.M)


def as_set(values) -> dict:
    """-> `{name: on|off}` of a list of `<name>=on|off`."""
    return dict(str(one).partition("=")[::2] for one in values or [])


def heading_of(prompt: str) -> dict:
    """-> the packages the heading of a prompt's first block says, `{name: on|off}`."""
    line = next((one for one in prompt.splitlines() if one.startswith("▌ ") and " on" in one and "team" in one), "")
    return dict(re.findall(r"(\S+) (on|off)\b", line))


def tools_of(prompt: str) -> list[str]:
    """-> every name the TOOLS sections of a prompt offer."""
    lines = prompt.splitlines()
    return [name for at, one in enumerate(lines) if one.startswith("▌ TOOLS") and at + 1 < len(lines)
            for name in lines[at + 1].strip("[]").split()]


def code(played) -> str:
    """-> the code of the refusal a call wrote on stderr, '' when none."""
    found = REFUSAL.search(played.stderr or "")
    return found.group(1) if found else ""


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, packages=("agent", "team", "steering", "plan", "doc"), script={
        # (e) c delegates to d; the team's switch, d's profile over it
        "c": [{"sleep": 0.1, "body": {"do": ["d"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "d": [{"sleep": 0.1, "body": {"done": True}}],
        # (g) m answers its opening
        "m": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def played(entries: list, key: str) -> dict:
        return {one.get(key): {pack.get("name"): pack.get("on") for pack in one.get("packages") or []}
                for one in entries}

    h.declare("crew", "---\nagents: |\n  c agents/c\n  d agents/d\nreports: |\n  d -> c\nroot: c\nschedule: off\n"
                      "---\nThe team's switch.\n")
    h.declare("none", "---\nagents: |\n  n agents/n\nroot: n\nschedule: off\n---\nNever started.\n")
    crewed = h.call("team", "start", "crew", "--message", "both of you", *h.harnessed, "--package", "plan=off",
                    "--member", "d", "--package", "plan=on")
    h.declare("mute", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\nA silent season.\n")
    born = h.call("agent", "add", "agents/m")
    settings.write(h.meta_of("agents/m"), "package.plan", "on")
    muted = h.call("team", "start", "mute", "--message", "alone", *h.harnessed)
    tries = {"team": ("--package", "doc=on", "--package", "steering=off"),
             "member": ("--package", "doc=on", "--member", "n", "--package", "steering=off")}
    said = {whom: h.call("team", "start", "none", "--message", "x", *h.harnessed, "--no-tick", *extra)
            for whom, extra in tries.items()}

    # --- (e) the team's switch, covered by a profile -------------------------------------------------------------
    crew_done = h.settled("crew", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    crew = h.events("crew")
    started_crew = next((one for one in crew if one.get("kind") == "team-started"), {})
    runs = {member: next((one.get("run") for one in by_kind(crew, "wake-launched", agent=member)), "")
            for member in ("c", "d")}
    kept = {member: persistence.switches_of(persistence.slot_of(h.meta_of(f"agents/{member}"), run)) if run else {"?": "?"}
            for member, run in runs.items()}
    crew_face = h.face("crew")
    crew_members = {one.get("member"): one for one in crew_face.get("members") or []}
    whole = {"agent": "on", "team": "on", "steering": "off", "plan": "off", "doc": "off"}
    with_plan = {**whole, "plan": "on"}
    profile_d = ((started_crew.get("profiles") or {}).get("d") or {}).get("packages")
    if (crewed.returncode == 0 and crew_done and as_set(started_crew.get("packages")) == whole
            and len(started_crew.get("packages") or []) == len(whole) and as_set(profile_d) == with_plan
            and kept == {"c": whole, "d": with_plan}
            and as_set((crew_face.get("launch") or {}).get("packages")) == whole
            and as_set(((crew_members.get("c") or {}).get("launch") or {}).get("packages")) == whole
            and as_set(((crew_members.get("d") or {}).get("launch") or {}).get("packages")) == with_plan
            and {name: packs.get("plan") for name, packs in played(crew_face.get("members") or [], "member").items()}
            == {"c": False, "d": True}):
        held("(e) the team's switch, covered by a profile", f"`--package plan=off` for the team, d's profile plan=on: "
             f"c's run {runs['c']} plans off, d's {runs['d']} on, every pin at their switches; the whole set at "
             "team-started.packages, profiles[d], launch.packages and members[].launch")
    else:
        failures.append(f"  ✗ (e) team switch            rc={crewed.returncode} done={crew_done} "
                        f"started={started_crew.get('packages')} kept={kept} launch={(crew_face.get('launch') or {}).get('packages')} "
                        f"members={ {m: (one.get('launch') or {}).get('packages') for m, one in crew_members.items()} } "
                        f"{crewed.stderr.strip()[-200:]!r}")

    # --- (f) a package without its requirement ------------------------------------------------------------------
    untouched = not h.journal_of("none").exists() and not h.agent_stands("agents/n")
    if all(one.returncode == 2 and code(one) == "package-dependency" for one in said.values()) and untouched:
        held("(f) package-dependency", "doc=on with steering=off, for the team and over a member's profile: refused "
             "by its name, no journal, no agent born")
    else:
        failures.append("  ✗ (f) dependency             " + " ".join(f"{whom}={one.returncode}:{code(one)!r}"
                                                                    for whom, one in said.items())
                        + f" untouched={untouched}")

    # --- (g) a silent season over a member's SETTINGS ------------------------------------------------------------
    mute_done = h.settled("mute", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    run_m = next((one.get("run") for one in by_kind(h.events("mute"), "wake-launched", agent="m")), "")
    switched = persistence.switches_of(persistence.slot_of(h.meta_of("agents/m"), run_m)) if run_m else {}
    first = (h.out / "m-1.prompt").read_text(encoding="utf-8") if (h.out / "m-1.prompt").is_file() else ""
    said, offered = heading_of(first), tools_of(first)
    if (born.returncode == 0 and muted.returncode == 0 and mute_done and switched == whole
            and {name: said.get(name) for name in whole} == whole and offered and "pp-plan" not in offered):
        held("(g) a silent season over a member's SETTINGS", f"m's SETTINGS plan on, no --package: run {run_m}'s first "
             f"heading says plan off, no pp-plan among {len(offered)} offers, its switches {switched}")
    else:
        failures.append(f"  ✗ (g) silent season         born={born.returncode} rc={muted.returncode} done={mute_done} "
                        f"switches={switched} heading={said} pp-plan offered={'pp-plan' in offered} "
                        f"{muted.stderr.strip()[-200:]!r}")

    # --- (h) a journal of before, read as a set -----------------------------------------------------------------
    h.declare("olden", "---\nagents: |\n  o agents/o\nroot: o\nschedule: off\n---\nA journal of before.\n")
    h.written("olden", [{"kind": "team-started", "agents": {"o": "agents/o"}, "reports": [], "root": "o",
                         "principals": [], "owner": "house", "ceremonies": [], "entries": {}, "work": None,
                         "launch": {}, "limits": {}, "packages": ["plan=off"], "schedule": None, "digest": "0"}],
              "2026-11-03T20:00:00+00:00")
    old_face = h.face("olden")
    old_member = next(iter(old_face.get("members") or []), {})
    old_packages = {one.get("name"): "on" if one.get("on") else "off" for one in old_member.get("packages") or []}
    if (as_set((old_face.get("launch") or {}).get("packages")) == whole
            and as_set((old_member.get("launch") or {}).get("packages")) == whole and old_packages == whole):
        held("(h) a journal of before, read as a set", "packages [plan=off] of team 0.49.0: launch, the member's "
             "launch and its packages say the set -- the pins it does not name off")
    else:
        failures.append(f"  ✗ (h) journal of before      launch={(old_face.get('launch') or {}).get('packages')} "
                        f"member={(old_member.get('launch') or {}).get('packages')} packages={old_packages}")
    return 0
