"""Scenario `team-recurrence-described` -- 1 case(s): a RECURRENCE carries its DESCRIPTION -- one sentence of what it
does, beside its short `--name` -- laid by `team post … --every … --description <text>` or by `team recurrence --task
T<n> --every … --description <text>`, said at `status --json`. One team under a frozen clock (`PP_NOW`), Monday
2026-10-05, nothing woken; the pose, the sounding and the faces are `team-recurrence`'s, the change of a description
`team-recurrence-changed`'s.
- (a) a recurrence described: `--description` of 201 characters or of two lines refuses `description-invalid`,
  `--description` without `--every` the usage, the journal byte-identical; `post --every … --description <text>`
  writes it in the `recurrence` event, `team recurrence --task T<n> --every … --description <text>` in its own, a
  recurrence posted without it says nothing in its event; `status --json` says `recurrences[].description`, `null`
  for the one without
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")

MONDAY, PAIR = T.MONDAY, T.PAIR


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    by_kind = T.by_kind
    # --- (a) a recurrence described -------------------------------------------------------------------------------
    h.declare("desc", PAIR.format(m="em", w="ew"))
    begun = h.call("team", "start", "desc", "--message", "go", "--no-tick", now=MONDAY + "07:50")
    described = "Reviews the open PRs every morning."
    post = lambda *rest: h.call("team", "post", "desc", "--message", "x", "--to", "ew", *rest, "--no-tick",
                                now=MONDAY + "08:00")
    before = h.journal_of("desc").read_bytes()
    refused = {"description-invalid": post("--every", "day 09:30", "--description", "x" * 201),
               "description-invalid ": post("--every", "day 09:30", "--description", "one line\nand another"),
               "usage": post("--description", described)}
    untouched = h.journal_of("desc").read_bytes() == before
    with_it = post("--every", "day 09:30", "--description", described)
    without = post("--every", "day 10:30")
    task = post("--name", "once")
    born = h.call("team", "recurrence", "desc", "--task", "T1", "--every", "day 12:00", "--description", "Its own.",
                  "--no-tick", now=MONDAY + "08:01")
    poses = {one.get("recurrence"): one for one in by_kind(h.events("desc"), "recurrence")}
    faced = {one.get("id"): one for one in h.face("desc", now=MONDAY + "08:02").get("recurrences") or []}
    if (begun.returncode == 0 and untouched
            and all(call.returncode == 2 and code.strip() in call.stderr for code, call in refused.items()
                    if code != "usage")
            and refused["usage"].returncode == 2 and "usage" in refused["usage"].stderr
            and all(call.returncode == 0 for call in (with_it, without, task, born))
            and (poses.get("R1") or {}).get("description") == described and "description" not in (poses.get("R2") or {"description": 0})
            and (poses.get("R3") or {}).get("description") == "Its own." and (poses.get("R3") or {}).get("task") == "T1"
            and [(faced.get(one) or {}).get("description", "?") for one in ("R1", "R2", "R3")] == [described, None, "Its own."]):
        held("(a) a recurrence described", "201 characters and two lines description-invalid, without --every the usage, "
             "the journal byte-identical; the post and the --task pose carry it in their event, the one without "
             "nothing; status --json says it, null without")
    else:
        failures.append(f"  ✗ (a) a recurrence described   rc={[call.returncode for call in (begun, with_it, without, task, born)]} "
                        f"untouched={untouched} refused={[(code, call.returncode, call.stderr.strip()[-90:]) for code, call in refused.items()]} "
                        f"poses={poses} faced={[(one, (faced.get(one) or {}).get('description', '?')) for one in ('R1', 'R2', 'R3')]} "
                        f"{(with_it.stderr or born.stderr).strip()[-160:]!r}")
    return 0
