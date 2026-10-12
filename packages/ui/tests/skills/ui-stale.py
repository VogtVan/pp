"""Scenario `ui-stale` -- a line of the transcript that has nothing to open is STALE (plan ui, batch
les-glyphes-vivants), on the bench's `pp-chat` witness:
- a thought of a count alone (`thinking {tokens: 42}`) is drawn in its own look, neither the dim of a line of
  conduction nor a live one; `tab` skips it -- six `shift+tab` from the message line reach the conduction of launch 1
  -- and nothing opens on it
- a thought that gets its text after its count is judged again: drawn as the dim lines beside it, reached by
  `shift+tab`, `enter` opens its text
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")

TURN = "h,i,enter,wait:waiting"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    sent = ("ag1", "--render", "dialogue", "--size", "120x40")

    # --- a thought of a count alone is STALE: its own look, tab skips it, nothing opens -----------------------
    thought = P.Post(bench, "ui-stale", P.thinking_script())
    looked = thought.render(*sent, "--press", TURN, "--styles")
    stale, dim = (P.styles_of(looked.stdout, r"∴ \d\d:\d\d:\d\d · launch 1 · thinking ~42 tokens"),
                  P.styles_of(looked.stdout, r"◇ \d\d:\d\d:\d\d · launch 1 · "))
    up = ",".join(["shift+tab"] * 6)                       # from the message line: ◀ 2, ∴ 2, ◇ 2, ◀ 1, the steps, ◇ 1
    skipped = thought.render(*sent, "--press", f"{TURN},{up},enter")
    if (looked.returncode == 0 and stale and dim and stale != dim
            and skipped.returncode == 0 and "launch 1 · BOOT" in skipped.stdout and "▌ pp · run w00001" in skipped.stdout
            and "no text said" not in skipped.stdout):
        held("a thought with nothing to show is stale", f"∴ ~42 tokens drawn {sorted(stale)} against the dim ◇ "
             f"{sorted(dim)}; six shift+tab from the message line reach ◇ 1, the stale line skipped, nothing opens on it")
    else:
        failures.append(f"  ✗ stale                       rc={looked.returncode}/{skipped.returncode} stale={sorted(stale)} "
                        f"dim={sorted(dim)} {skipped.stdout!r} {looked.stderr[-300:]!r}")

    # --- the same kind of line judged again: a count, then a text -- live, its text opens -----------------
    live = P.styles_of(looked.stdout, r"∴ \d\d:\d\d:\d\d · launch 2 · thinking")
    beside = P.styles_of(looked.stdout, r"◇ \d\d:\d\d:\d\d · launch 2 · ")
    opened_t = thought.render(*sent, "--press", f"{TURN},shift+tab,shift+tab,enter")
    if (live and live == beside and live != stale
            and opened_t.returncode == 0 and P.THOUGHT in opened_t.stdout and "thinking" in opened_t.stdout):
        held("a thought that gets its text is live again", f"∴ launch 2 drawn as the dim ◇ beside it {sorted(live)}, "
             "not stale; two shift+tab reach it and enter opens its text")
    else:
        failures.append(f"  ✗ judged again                live={sorted(live)} beside={sorted(beside)} "
                        f"{opened_t.stdout!r} {opened_t.stderr[-300:]!r}")
    return 0
