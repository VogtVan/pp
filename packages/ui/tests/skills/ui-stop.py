"""Scenario `ui-stop` -- the stop button (plan ui, batch le-bouton-d-arret; split out of `ui-turn`, rule 10), on the
bench's `pp-chat` witness, `ag1`'s second exchange running until a `stop`:
- `■ stop` beside the message line and `[ctrl+g] stop the turn` in the footer during a turn alone, neither at rest
- `escape` twice during the turn sends no `stop` (the witness's journal): the turn goes on
- `ctrl+g`, or `tab` to the button and `enter`, sends `stop` -- the journal says `stop ag1`, the verdict interrupted
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-stop")
    render = post.render
    rest = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", "h,i,enter", "--wait", "waiting")
    text_rest = rest.stdout

    # --- the stop button: there during a turn alone; escape stops nothing; ctrl+g and the button stop ----
    def stops() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("stop ")]

    TURNING = "h,i,enter,wait:waiting,g,o,enter,wait:conduction"   # ag1's second exchange runs until a stop
    post.clear_journal()
    seen = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", TURNING)
    footer_seen = P.keys_of(seen.stdout)
    footer_rest = P.keys_of(text_rest)
    if (seen.returncode == 0 and "■ stop" in seen.stdout and "[ctrl+g] stop the turn" in footer_seen
            and "■ stop" not in text_rest and "stop the turn" not in footer_rest and stops() == []):
        held("the stop button is there during a turn alone", "during ag1's second exchange: `■ stop` beside the "
             "line and `[ctrl+g] stop the turn` in the footer; at rest neither")
    else:
        failures.append(f"  ✗ stop button                 rc={seen.returncode} {footer_seen!r} / {footer_rest!r} {seen.stdout!r}")
    post.clear_journal()
    kept = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", f"{TURNING},escape,escape",
                  "--wait", "none:1.5")
    if kept.returncode == 0 and stops() == [] and "interrupted" not in kept.stdout and "■ stop" in kept.stdout:
        held("escape stops nothing", "escape twice during the turn: no stop in the witness's journal, the turn goes on")
    else:
        failures.append(f"  ✗ escape                      rc={kept.returncode} {post.journal_lines()} {kept.stdout!r}")
    post.clear_journal()
    keyed = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", f"{TURNING},ctrl+g", "--wait", "waiting")
    keyed_stops = stops()
    post.clear_journal()
    pressed = render("ag1", "--render", "dialogue", "--size", "100x30", "--press", f"{TURNING},tab,enter",
                     "--wait", "waiting")
    if (keyed.returncode == 0 and keyed_stops == ["stop ag1"] and "⚠ interrupted" in keyed.stdout
            and pressed.returncode == 0 and stops() == ["stop ag1"] and "⚠ interrupted" in pressed.stdout
            and "■ stop" not in pressed.stdout):
        held("ctrl+g and the button stop the turn", "ctrl+g: `stop ag1` in the journal, ⚠ interrupted; tab to the "
             "button and enter: the same; the button gone at rest")
    else:
        failures.append(f"  ✗ stop                        {keyed_stops} {post.journal_lines()} {keyed.stdout[-500:]!r} / "
                        f"{pressed.stdout[-500:]!r}")
    return 0
