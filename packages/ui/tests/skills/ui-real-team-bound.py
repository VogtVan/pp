"""Scenario `ui-real-team-bound` -- 1 case (batch le-minuteur-arme-au-debut-du-tick, s.1373, H2): a gesture of the post
played by `play_verb` under its bound, on the REAL verbs of `team`, its wake-ups played by the team witness, never a
provider. `essai` started; a post without a tick timed (B), then `dev` due on it launched by one `team tick` timed (L);
then `lead` due on T3 by a post without a tick, and the gesture `team post essai --to rev`, composed by the post
(`gestures.post`: `--no-tick`), played as the Teams and Tasks tabs play a gesture (`faces.play_gesture`) under
`PP_UI_TIMEOUT` = B + 1.5 L: the verb answers rc 0 within its bound, and the team's tick, played apart, launches
`lead`, then `rev` -- nothing ended by the bound: no intent of `rev` without its launch, both witnesses run.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time

from conductor import contributions
from tests.harness import SOURCE, support

R = support(__file__, "real_team")
POST_UI = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
FACES = POST_UI / "faces" / "__init__.py"
SCRIPT = {"lead": {"T1": [{"sleep": 0.2, "body": {"done": "started"}}],
                   "T3": [{"sleep": 8.0, "body": {"done": "lead's part"}}]},
          "dev": {"T2": [{"sleep": 8.0, "body": {"done": "dev's part"}}]},
          "rev": {"T4": [{"sleep": 8.0, "body": {"done": "rev's part"}}]}}


def _timed(call) -> tuple[object, float]:
    began = time.monotonic()
    played = call()
    return played, time.monotonic() - began


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-bound", SCRIPT)
    faces = contributions.module_at(FACES)
    sys.path.insert(0, str(POST_UI))
    try:
        from model import gestures                               # the post's own composer
    finally:
        sys.path.remove(str(POST_UI))
    gesture = gestures.post(R.TEAM, "and yours", to="rev")
    begun = team.start("go")
    lead_over = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events)
                             and sum(1 for one in events if one.get("kind") == "wake-ended") >= 1)
    time.sleep(1.0)                                              # lead's on-end tick has left
    posted, post_b = _timed(lambda: team.call("team", "post", R.TEAM, "--to", "dev", "--message", "yours", "--no-tick"))
    ticked, launch_l = _timed(lambda: team.call("team", "tick", R.TEAM))   # dev's one launch
    nudged = team.call("team", "post", R.TEAM, "--to", "lead", "--message", "yours too", "--no-tick")
    limit = post_b + 1.5 * launch_l
    kept = {key: os.environ.get(key) for key in (*team.env, "PP_UI_TIMEOUT")}
    os.environ.update({**team.env, "PP_UI_TIMEOUT": f"{limit:.3f}"})
    try:
        face, took = _timed(lambda: asyncio.run(faces.play_gesture(gesture, str(team.ws))))
    finally:
        for key, value in kept.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    team.settled(lambda events: {one.get("task") for one in events if one.get("kind") == "wake-launched"} >= {"T3", "T4"},
                 timeout=30.0)                                   # the tick apart launches both
    time.sleep(1.0)                                              # whatever outlives the verb has written
    events = team.events()
    intents = {one.get("agent"): one.get("tag") for one in events if one.get("kind") == "wake-intent"
               and one.get("task") in ("T3", "T4")}
    launched = {one.get("tag") for one in events if one.get("kind") == "wake-launched"}
    unlaunched = sorted(agent for agent, tag in intents.items() if tag not in launched)
    ran = {agent: (team.out / f"{agent}@{task}.count").is_file() for agent, task in (("lead", "T3"), ("rev", "T4"))}
    said = (f"gesture={' '.join(gesture)!r} B={post_b:.2f}s L={launch_l:.2f}s bound={limit:.2f}s took={took:.2f}s rc={face.rc} err={face.err.strip()!r} "
            f"intents={intents} launched={sorted(tag for tag in launched if tag in intents.values())} "
            f"unlaunched={unlaunched} witness-ran={ran}")
    if begun.returncode == 0 and lead_over and posted.returncode == ticked.returncode == nudged.returncode == 0 \
            and face.rc == 0 and "--no-tick" in gesture and set(intents) == {"lead", "rev"} \
            and not unlaunched and all(ran.values()):
        held("a gesture is not ended mid-tick", said)
    else:
        failures.append(f"  ✗ gesture bounded mid-tick     start={begun.returncode} lead={lead_over} "
                        f"post={posted.returncode}/{ticked.returncode}/{nudged.returncode} {said}")
    team.settled(lambda events: not team.alive(), timeout=30.0)
    return 0
