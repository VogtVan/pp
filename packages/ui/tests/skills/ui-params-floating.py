"""Scenario `ui-params-floating` -- the list of a `ListInput` floats over the overlay as a `Select`'s does (plan ui,
batch les-retours-du-reel-0-18, its rework; beside `ui-params-lists`, rule 10), on the bench's `pp-chat` witness:
`ag1` last played the second of the two models `providers --json` names:
- at rest `model` and `effort` carry the `▼` of a list at their right, as `provider` and `permissions` do
- `down` on a line that holds an exact name unrolls the WHOLE list, the cursor on that name: both models listed,
  `up` from the cursor reaches the first model above it; the arrow turns `▲`
- the list unrolled floats over the fields below and moves none: the row of `budget`'s line (`no bound`) is the
  same, list folded or unrolled
"""
from __future__ import annotations

import copy

from tests.harness import support

P = support(__file__, "dialogue")
OPEN = "2,n,wait:none"                # the overlay of a new run of ag1, a pause for the providers' face
PAUSE = ("--wait", "none:1.5")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = copy.deepcopy(P.SCRIPT)
    script["faces"]["status"]["ag1"][-1]["last"] = {"provider": P.PROVIDER, "policy": {"model": P.MODELS[1]}}
    post = P.Post(bench, "ui-params-floating", script)
    render = post.render

    def listed(text: str, name: str) -> bool:
        """-> whether `name` stands on a row of its own in the capture -- a row of the list, not the help that names it."""
        return any(row.strip(" ┃│").strip() == name for row in text.split("\n"))

    def row_of(text: str, words: str) -> int:
        """-> the row `words` stands on in a capture, -1 when absent."""
        return next((n for n, line in enumerate(text.split("\n")) if words in line), -1)

    # --- at rest: the arrows; unrolled: the whole list, the arrow up, budget where it was ----------------
    rest = render("--render", "dialogue", "--size", "110x40", "--press", OPEN, *PAUSE)
    unrolled = render("--render", "dialogue", "--size", "110x40", "--press", f"{OPEN},down", *PAUSE)
    arrows = rest.stdout.count("▼")
    before, after = row_of(rest.stdout, "no bound"), row_of(unrolled.stdout, "no bound")
    if (rest.returncode == 0 and unrolled.returncode == 0 and arrows == 4 and "▲" in unrolled.stdout
            and listed(unrolled.stdout, P.MODELS[0]) and before > 0 and before == after):
        held("the list floats and lists every name", f"4 ▼ at rest (provider, model, effort, permissions), ▲ once "
             f"unrolled; {P.MODELS[0]} listed beside the exact {P.MODELS[1]}; budget's line on row {before} both times")
    else:
        failures.append(f"  ✗ floating                    ▼={arrows} ▲={'▲' in unrolled.stdout} budget={before}/{after} "
                        f"{unrolled.stdout!r} {unrolled.stderr[-300:]!r}")

    # --- the cursor on the exact name: up reaches the name above it -------------------------------------
    post.clear_journal()
    kept = render("--render", "dialogue", "--size", "110x40", "--press", f"{OPEN},down,up,enter,enter",
                  "--wait", "waiting:2")
    opens = [one for one in post.journal_lines() if one.startswith("open")]
    if kept.returncode == 0 and opens == [f"open ag1 --provider {P.PROVIDER} --model {P.MODELS[0]}"]:
        held("the cursor stands on the exact name", f"down, up, enter, enter: {opens}")
    else:
        failures.append(f"  ✗ cursor                      {opens} {kept.stderr[-300:]!r}")
    return 0
