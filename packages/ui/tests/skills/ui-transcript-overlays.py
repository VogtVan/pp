"""Scenario `ui-transcript-overlays` -- what a line of the transcript opens, and what shows whole in place, on ONE post
of the bench's `pp-chat` witness whose script changes by `use()`:
- each kind of line opened names its kind in the title: the call of pp (`Bash`), the `Read`, the steps (the
  conduction's title: the markdown case; a thought's: the last case) -- the agent's words are no line to open: they
  show whole, in place
- words whose rows open on an emoji and its selector `U+FE0F` (🛠️) draw straight: no `U+FE0F` in the transcript, the
  table's right border on one column of the terminal (a selector counted as nothing, the terminal's way)
- the agent's words drawn as MARKDOWN: their table drawn, no `|---|` left; a conduction opens as the text pp served,
  the keys of its overlay without `ctrl+c`
- words of 4k characters over 80 lines at 120x40: shown whole in the transcript, no overlay -- their last line in
  sight, the transcript's end held in view
- a thought of a count alone is STALE: its own look, neither the dim of a line of conduction nor a live one; `tab`
  skips it, as it skips the end of a launch -- four `shift+tab` from the message line reach the conduction of launch 1
  -- and nothing opens on it; a thought that gets its text after its count is judged again: drawn as the dim lines
  beside it, reached by `shift+tab`, `enter` opens its text
"""
from __future__ import annotations

import re
import unicodedata

from tests.harness import support

P = support(__file__, "dialogue")
TURN = "i,h,i,enter,wait:waiting"


def columns_of(text: str) -> int:
    """-> the columns a terminal draws `text` on: a wide character on two, a selector or a combining mark on none."""
    return sum(0 if char == "\ufe0f" or unicodedata.combining(char) else
               2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-transcript-overlays", P.tools_script())
    sent = ("ag1", "--render", "dialogue")

    # --- each kind names itself in the title -------------------------------------------------------------
    wanted = {5: "Bash", 3: "Read", 2: "step"}     # the conduction's title: the markdown case; a thought's: the last
    said = {}
    for up, kind in wanted.items():
        shown = post.render(*sent, "--size", "140x44", "--press", f"{TURN},{','.join(['shift+tab'] * up)},enter")
        found = P.title_of(shown.stdout)
        said[kind] = found[0] if found else ""
    if all(kind in said[kind] for kind in wanted.values()) and len(set(said.values())) == len(wanted):
        held("each kind names itself", "titles: " + "; ".join(said.values()))
    else:
        failures.append(f"  ✗ kinds                       {said}")

    # --- words with emoji draw straight ------------------------------------------------------------------
    post.use(P.emoji_answer_script())
    shown = post.render(*sent, "--size", "120x40", "--press", TURN)
    rows = [row for row in shown.stdout.split("\n") if "build" in row or "ship" in row]
    borders = {columns_of(row[:row.rindex("│")]) for row in rows if "│" in row}
    selectors = sum(row.count("\ufe0f") for row in shown.stdout.split("\n"))
    if shown.returncode == 0 and len(rows) == 2 and selectors == 0 and len(borders) == 1:
        held("words with emoji draw straight", f"no U+FE0F in the transcript; the table's right border on column "
             f"{borders.pop()} on both rows")
    else:
        failures.append(f"  ✗ emoji                       rc={shown.returncode} U+FE0F={selectors} columns={sorted(borders)} "
                        f"{rows!r} {shown.stderr[-300:]!r}")

    # --- the agent's words in markdown in the transcript, a conduction in text, no ctrl+c among its keys --------
    post.use(P.markdown_script())
    answer = post.render(*sent, "--size", "120x40", "--press", TURN)
    served = post.render(*sent, "--size", "120x40", "--press", f"{TURN},shift+tab,enter")
    title_c = P.title_of(served.stdout)
    boxed = served.stdout[served.stdout.find("┏"):]
    table_row = next(row for row in P.MARKDOWN.split("\n") if "frame" in row)
    served_lines = P.CONDUCTION.split("\n")[-2:]
    if (answer.returncode == 0 and "build" in answer.stdout and "|---|" not in answer.stdout
            and table_row not in answer.stdout and "┏" not in answer.stdout
            and served.returncode == 0 and title_c[:1] and "conduction" in title_c[0] and "ctrl+c" not in boxed
            and "[esc]" in boxed and all(line in served.stdout for line in served_lines)):
        held("the words read as markdown, a conduction opens as text", "the table drawn in the transcript, no |---|; "
             "the conduction's lines as served, no ctrl+c among the overlay's keys")
    else:
        failures.append(f"  ✗ markdown                    {title_c} {answer.stdout[-1500:]!r} {boxed[:800]!r} "
                        f"{answer.stderr[-300:]!r}")

    # --- long words show whole, in place --------------------------------------------------------------
    post.use(P.long_answer_script())
    shown = post.render(*sent, "--size", "135x40", "--press", f"{TURN},ctrl+a,ctrl+c")
    copied = re.search(r"(\d+) chars", P.status_of(shown.stdout))
    if (shown.returncode == 0 and not P.title_of(shown.stdout) and copied and int(copied.group(1)) >= len(P.ANSWER)
            and "the agent says two" in shown.stdout):
        held("long words show whole, in place", f"no overlay; the transcript holds them whole ({copied.group(0)} "
                                                f"copied, the words are {len(P.ANSWER)} chars), its end in view")
    else:
        failures.append(f"  ✗ long words                  rc={shown.returncode} {shown.stdout[-1500:]!r} {shown.stderr[-300:]!r}")

    # --- a thought of a count alone is STALE: its own look, tab skips it, nothing opens -----------------------
    post.use(P.thinking_script())
    looked = post.render(*sent, "--size", "120x40", "--press", TURN, "--styles")
    stale, dim = (P.styles_of(looked.stdout, r"∴ \d\d:\d\d:\d\d · launch 1 · thinking ~42 tokens"),
                  P.styles_of(looked.stdout, r"◇ \d\d:\d\d:\d\d · launch 1 · "))
    up = ",".join(["shift+tab"] * 4)                       # from the message line: ∴ 2, ◇ 2, the steps, ◇ 1
    skipped = post.render(*sent, "--size", "120x40", "--press", f"{TURN},{up},enter")
    title_s = P.title_of(skipped.stdout)
    head = P.CONDUCTION.split("\n")[0]
    if (looked.returncode == 0 and stale and dim and stale != dim
            and skipped.returncode == 0 and title_s[:1] and "conduction" in title_s[0] and head in skipped.stdout):
        held("a thought with nothing to show is stale", f"∴ ~42 tokens drawn {sorted(stale)} against the dim ◇ "
             f"{sorted(dim)}; four shift+tab from the message line reach ◇ 1, the stale lines skipped, nothing opens on it")
    else:
        failures.append(f"  ✗ stale                       rc={looked.returncode}/{skipped.returncode} stale={sorted(stale)} "
                        f"dim={sorted(dim)} {title_s} {skipped.stdout!r} {looked.stderr[-300:]!r}")

    # --- the same kind of line judged again: a count, then a text -- live, its text opens -----------------
    live = P.styles_of(looked.stdout, r"∴ \d\d:\d\d:\d\d · launch 2 · thinking")
    beside = P.styles_of(looked.stdout, r"◇ \d\d:\d\d:\d\d · launch 2 · ")
    opened_t = post.render(*sent, "--size", "120x40", "--press", f"{TURN},shift+tab,enter")
    title_t = P.title_of(opened_t.stdout)
    if (live and live == beside and live != stale and opened_t.returncode == 0 and P.THOUGHT in opened_t.stdout
            and title_t[:1] and "thinking" in title_t[0]):
        held("a thought that gets its text is live again", f"∴ launch 2 drawn as the dim ◇ beside it {sorted(live)}, "
             "not stale; one shift+tab reaches it and enter opens its text")
    else:
        failures.append(f"  ✗ judged again                live={sorted(live)} beside={sorted(beside)} "
                        f"{opened_t.stdout!r} {opened_t.stderr[-300:]!r}")
    return 0
