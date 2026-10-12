"""Scenario `ui-run-stats` -- the statistics of a run stacked over the overlay of the runs (plan ui, batch
le-poste-sans-hub; split out of `ui-agents` by la-part-de-pp-dans-le-contexte, 2026-10-10, rule 10), on the bench's
`pp-chat` witness replaying the faces of `agent`:
- `s` in the overlay of an agent's runs stacks the statistics of the run under the cursor, in three sections: the
  run (its sums), pp (the engine's conduction: blocks, proofs, the seconds spent) and ctx (the context approached
  from the run's flow, `~17% of 1M tokens`, pp's share of the flow with what the engine served beside, the voices,
  the reread) -- one line for a run whose flow was never counted
- the seconds pp spent read in `h min s` (batch le-pied-et-les-overlays): `1 h 02 min 05 s`, `5 min 03 s`, `12.3 s`
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-run-stats")
    render = post.render

    # --- s in the overlay: the statistics stacked over it ---------------------------------------------
    measured = render("--render", "dialogue", "--size", "120x50", "--press", "2,enter,s", "--wait", "waiting:1")
    text_s = measured.stdout
    flowless = render("--render", "dialogue", "--size", "120x50", "--press", "2,enter,down,s", "--wait", "waiting:1")
    if (measured.returncode == 0 and "blocks      9" in text_s and "proofs      2" in text_s
            and "work 10.5 s" in text_s and "escape closes" in text_s
            and "context     ~17% of 1M tokens" in text_s and "pp          ~33% of the flow · ~56k · served ~54k" in text_s
            and "reread      ~3.6M" in text_s and "tool_result ~100k" in text_s
            and flowless.returncode == 0 and "no flow counted for this run" in flowless.stdout):
        held("s stacks the statistics over the overlay", "run, pp (blocks 9, proofs 2, spent work 10.5 s) and ctx "
             "(~17% of 1M tokens, pp ~33% of the flow, reread ~3.6M); one line for a run without a flow")
    else:
        failures.append(f"  ✗ stats                       rc={measured.returncode}/{flowless.returncode} {text_s!r} "
                        f"{flowless.stdout[-800:]!r} {measured.stderr[-300:]!r}")

    # --- the durations in h min s ------------------------------------------------------------------
    spent = next((line.strip() for line in flowless.stdout.split("\n") if "spent" in line), "")
    if ("work 1 h 02 min 05 s" in spent and "proof 5 min 03 s" in spent and "answer 12.3 s" in spent):
        held("the durations read in h min s", spent[:90])
    else:
        failures.append(f"  ✗ durations                   {spent!r}")
    return 0
