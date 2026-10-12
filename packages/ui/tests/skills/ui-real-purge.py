"""Scenario `ui-real-purge` -- a run purged from the post on the REAL `agent purge` (plan ui, batch
le-poids-et-la-purge), a real run of two exchanges made first at the post, on the witness harness of `agent`,
never a provider:
- the overlay of the runs says the run's weight, read from the real `status --json`
- `P` on the run, its key typed, `enter`: `agent status --json` no longer says the run, `responses.jsonl` keeps
  none of its lines
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = R.RealPost(bench, "ui-real-purge")
    made = post.talk()
    runs = post.status_json()
    key = runs[0]["run"] if runs else ""
    if made.returncode != 0 or len(runs) != 1 or len(post.responses()) != 2:
        failures.append(f"  ✗ real run                    rc={made.returncode} runs={runs} {made.stderr[-300:]!r}")
        return 0
    weight = runs[0].get("weight") or {}
    listed = post.render("--render", "dialogue", "--size", "160x40", "--press", "2,down,enter")
    row = next((line for line in listed.stdout.split("\n") if key in line), "")
    purged = post.render("--render", "dialogue", "--size", "160x40", "--press",
                         f"2,down,enter,P,{','.join(key)},enter", "--wait", "none:3")
    after, answered = post.status_json(), post.responses()
    if (listed.returncode == 0 and weight.get("bytes") and (" B " in row or " kB " in row or " MB " in row)
            and purged.returncode == 0 and after == [] and answered == []):
        held("P purges a real run", f"its weight {weight.get('bytes')} bytes on its row; after P: status --json says no "
             "run, responses.jsonl none of its lines")
    else:
        failures.append(f"  ✗ real purge                  weight={weight} row={row!r} after={after} responses={len(answered)} "
                        f"{purged.stdout[-1500:]!r} {purged.stderr[-300:]!r}")
    return 0
