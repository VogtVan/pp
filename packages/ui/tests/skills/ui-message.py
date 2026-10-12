"""Scenario `ui-message` -- the message line of a conversation on several lines (plan ui, batch
l-overlay-des-packages), on the bench's `pp-chat` witness:
- at rest the line is ONE row high; it grows with its text up to 8 rows, then scrolls
- `shift+enter`, `alt+enter` and `ctrl+j` go to the line without sending -- `ctrl+enter` no longer (batch
  le-pied-et-les-overlays); `enter` sends the whole text, its line breaks kept (the witness's journal writes them
  `\\n`), and the line comes back to one row
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "100x40")


def rows_of(text: str) -> int:
    """-> the rows of text inside the message line: between the last top border (`┌─`) and the last bottom one (`└─`) --
    its thin line (batch les-separateurs)."""
    lines = text.rstrip("\n").split("\n")
    bottom = max((n for n, line in enumerate(lines) if "└───" in line), default=-1)
    top = max((n for n, line in enumerate(lines[:bottom]) if "┌───" in line), default=-1)
    return bottom - top - 1 if 0 <= top < bottom else -1


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-message")
    render = post.render

    def messages() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("message ")]

    # --- one row at rest, growing up to 8 ----------------------------------------------------------------
    rest = render("ag1", "--render", "dialogue", *SIZE)
    four = render("ag1", "--render", "dialogue", *SIZE, "--press", "h,i,shift+enter,y,o,alt+enter,z,ctrl+j,w")
    many = render("ag1", "--render", "dialogue", *SIZE, "--press", ",".join(["a", "ctrl+j"] * 11) + ",a")
    sizes = [rows_of(one.stdout) for one in (rest, four, many)]
    if all(one.returncode == 0 for one in (rest, four, many)) and sizes == [1, 4, 8]:
        held("the line grows with its text", f"rows at rest, with 4 lines, with 12 lines: {sizes}")
    else:
        failures.append(f"  ✗ rows                        {sizes} {four.stdout[-900:]!r} {four.stderr[-300:]!r}")

    # --- enter sends the whole text, its line breaks kept --------------------------------------------------
    post.clear_journal()
    sent = render("ag1", "--render", "dialogue", *SIZE, "--press",
                  "h,i,shift+enter,y,o,alt+enter,z,ctrl+j,w,enter", "--wait", "waiting")
    if sent.returncode == 0 and messages() == ["message ag1 hi\\nyo\\nz\\nw"] and rows_of(sent.stdout) == 1:
        held("enter sends the text on several lines", f"the journal says {messages()}; the line back to one row")
    else:
        failures.append(f"  ✗ sent                        {messages()} rows={rows_of(sent.stdout)} {sent.stderr[-300:]!r}")
    # --- ctrl+enter goes to the line no more ---------------------------------------------------------------
    plain = render("ag1", "--render", "dialogue", *SIZE, "--press", "h,i,ctrl+enter,y,o")
    if plain.returncode == 0 and rows_of(plain.stdout) == 1:
        held("ctrl+enter goes to the line no more", "h, i, ctrl+enter, y, o: the line stays one row")
    else:
        failures.append(f"  ✗ ctrl+enter                  rows={rows_of(plain.stdout)} {plain.stdout[-600:]!r}")
    return 0
