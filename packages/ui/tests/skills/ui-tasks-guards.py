"""Scenario `ui-tasks-guards` -- the guards of the Tasks tab's readings, on the bench's `pp-team` witness replaying the
faces of `team` for three declared teams -- `core-review` and `ops` started, `veille` never (`_tasks`):
- a verb found ended as its bound passes gives a face `verb-timeout`, never an exception; a reading of the tab that
  raises leaves the post standing -- `2` shows the agents -- and says the exception on the remedy line
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "tasks")
T, P = S.T, S.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-guards")

    # --- the guards: a verb ended at its bound, a reading that raises ------------------------------------
    face, raised = S.ended_at_its_bound(str(house.ws))
    if face is not None and face.rc == -1 and "verb-timeout" in face.err and not raised:
        held("a verb ended at its bound gives a face", f"rc {face.rc}, `verb-timeout` on its err, nothing raised")
    else:
        failures.append(f"  ✗ verb at its bound           {face!r} raised={raised!r}")
    (house.faces / "team").chmod(0o644)        # the console of `team` cannot be played: the reading raises
    broken = house.render("--render", "tasks", "--size", "150x40", "--press", "2")
    remedy = P.remedy_of(broken.stdout)
    if broken.returncode == 0 and "PermissionError" in remedy and "agents/reviewer" in broken.stdout:
        held("a reading that raises leaves the post standing", f"the remedy says {remedy.split(' [')[0]!r}; `2` shows "
             "the agents")
    else:
        failures.append(f"  ✗ reading guarded             rc={broken.returncode} {remedy!r} {broken.stdout[-1200:]!r} "
                        f"{broken.stderr[-600:]!r}")
    (house.faces / "team").chmod(0o755)
    return 0
