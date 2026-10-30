"""Scenario `ui-message-line` -- the message line of a conversation: who takes it, and its text on several lines, on
the bench's `pp-chat` witness:
- no line takes the focus by itself: at the opening `h,i,enter` sends nothing, `i,h,i,enter` sends `hi`; a turn that
  ends (`waiting`) leaves the focus where it was -- `escape` during `ag3`'s turn, then `y,o,enter` after its end
  sends nothing more
- at rest the line is ONE row high; it grows with its text up to 8 rows, then scrolls
- `ctrl+enter` goes to the line without sending (batch les-formulaires-lisibles) -- `ctrl+j`, the name most terminals
  give it, `alt+enter` and `shift+enter` too; `enter` sends the whole text, its line breaks kept (the witness's
  journal writes them `\\n`), and the line comes back to one row
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
    post = P.Post(bench, "ui-message-line")
    render = post.render

    def messages() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("message ")]

    # --- the focus: i alone goes to the line; a turn's end takes nothing ---------------------------------------
    post.clear_journal()
    bare = render("ag1", "--render", "dialogue", *SIZE, "--press", "h,i,enter", "--wait", "none:1")
    none = messages()
    post.clear_journal()
    typed = render("ag1", "--render", "dialogue", *SIZE, "--press", "i,h,i,enter", "--wait", "waiting")
    sent_hi = messages()
    post.clear_journal()
    kept = render("ag3", "--render", "dialogue", "--size", "100x30",
                  "--press", "i,h,i,enter,wait:principal,escape,wait:waiting,y,o,enter", "--wait", "none:1")
    after = messages()
    if (bare.returncode == 0 and none == [] and typed.returncode == 0 and sent_hi == ["message ag1 hi"]
            and kept.returncode == 0 and after == ["message ag3 hi"]):
        held("i alone goes to the line", "h,i,enter at the opening sends nothing; i,h,i,enter sends hi; the end of a "
             "turn leaves the focus where escape put it: y,o,enter sends nothing more")
    else:
        failures.append(f"  ✗ focus                       {none} / {sent_hi} / {after} {bare.stderr[-200:]!r} "
                        f"{kept.stderr[-200:]!r}")

    # --- one row at rest, growing up to 8 ----------------------------------------------------------------
    rest = render("ag1", "--render", "dialogue", *SIZE)
    four = render("ag1", "--render", "dialogue", *SIZE, "--press", "i,h,i,shift+enter,y,o,alt+enter,z,ctrl+j,w")
    many = render("ag1", "--render", "dialogue", *SIZE, "--press", "i," + ",".join(["a", "ctrl+j"] * 11) + ",a")
    sizes = [rows_of(one.stdout) for one in (rest, four, many)]
    if all(one.returncode == 0 for one in (rest, four, many)) and sizes == [1, 4, 8]:
        held("the line grows with its text", f"rows at rest, with 4 lines, with 12 lines: {sizes}")
    else:
        failures.append(f"  ✗ rows                        {sizes} {four.stdout[-900:]!r} {four.stderr[-300:]!r}")

    # --- enter sends the whole text, its line breaks kept --------------------------------------------------
    post.clear_journal()
    sent = render("ag1", "--render", "dialogue", *SIZE, "--press",
                  "i,h,i,shift+enter,y,o,alt+enter,z,ctrl+j,w,enter", "--wait", "waiting")
    if sent.returncode == 0 and messages() == ["message ag1 hi\\nyo\\nz\\nw"] and rows_of(sent.stdout) == 1:
        held("enter sends the text on several lines", f"the journal says {messages()}; the line back to one row")
    else:
        failures.append(f"  ✗ sent                        {messages()} rows={rows_of(sent.stdout)} {sent.stderr[-300:]!r}")
    # --- ctrl+enter goes to the line ---------------------------------------------------------------------
    plain = render("ag1", "--render", "dialogue", *SIZE, "--press", "i,h,i,ctrl+enter,y,o")
    if plain.returncode == 0 and rows_of(plain.stdout) == 2:
        held("ctrl+enter goes to the line", "h, i, ctrl+enter, y, o: two rows, nothing sent")
    else:
        failures.append(f"  ✗ ctrl+enter                  rows={rows_of(plain.stdout)} {plain.stdout[-600:]!r}")
    return 0
