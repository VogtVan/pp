"""Scenario `ui-spaces` -- the row of the SPACES of a conversation (plan ui, batch les-boutons-des-espaces), on the
bench's `pp-chat` witness whose run offers `PLANS` and `STEERING` as spaces:
- the row says the stack and the offer: `ready.spaces` draws `+ PLANS · + STEERING` above the message line, a zone of
  `--regions` (`ready` says no root); the block step of the first exchange adds `root TURN`, the other steps, without
  `spaces` nor `root`, change nothing; a block step of the second exchange that says `STEERING` open draws
  `STEERING ×` and `+ PLANS`, the root no more (the space is the root)
- a button plays with the line empty too (batch les-espaces-sans-overlay, agent 1.0.34): a click on `+ STEERING` writes
  ONE command `{"kind": "open", "name": "STEERING"}`, no text, no `message`, and the space opens; with `ok` typed, ONE
  command `{"kind": "open", "name": "STEERING", "text": "ok"}` and no `message`, the line emptied, the turn shown as a
  message sent -- the stop button while it runs
- a click opens, a click closes: with a message typed, `+ STEERING` writes `{"kind": "open", "name": "STEERING",
  "text": "ok"}` on the witness's entry, the status says the wait until the `space` event, then the row says
  `STEERING ×`; once the turn of the message ended, a click on it writes `{"kind": "close"}` and the row offers
  `STEERING` again
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "120x30")
TURN = "i,h,i,ctrl+enter,wait:waiting"
OPEN = {"kind": "open", "name": "STEERING", "text": "ok"}


def message_line(text: str) -> str | None:
    """-> the text inside the message line of a capture -- the rows between its last top border (`┌─`) and its last
    bottom one (`└─`) --, None when the capture has none."""
    lines = text.rstrip("\n").split("\n")
    bottom = max((n for n, line in enumerate(lines) if "└───" in line), default=-1)
    top = max((n for n, line in enumerate(lines[:bottom]) if "┌───" in line), default=-1)
    return " ".join(lines[top + 1:bottom]) if 0 <= top < bottom else None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-spaces", P.spaces_script(delay=1.0, second={
        "root": "STEERING", "spaces": {"open": ["STEERING"], "openable": [{"name": "PLANS", "segment": None}]}}))
    render = post.render

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("space ")]

    # --- the row says the stack and the offer ---------------------------------------------------------------
    rest = render("ag1", "--render", "dialogue", *SIZE)
    regions = render("ag1", "--render", "dialogue", *SIZE, "--regions")
    zone = P.zones_of(regions.stdout).get("spaces")
    message = P.zones_of(regions.stdout).get("message")
    row = P.spaces_row(rest.stdout)
    turned = render("ag1", "--render", "dialogue", *SIZE, "--press", TURN)
    row_turned = P.spaces_row(turned.stdout)
    opened = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},i,g,o,ctrl+enter,wait:step")
    row_opened = P.spaces_row(opened.stdout)
    if (rest.returncode == 0 and "root" not in row and "+ PLANS" in row and "+ STEERING" in row
            and zone and message and zone[3] == 2 and zone[1] < message[1]
            and turned.returncode == 0 and row_turned.startswith("root TURN") and "+ PLANS" in row_turned
            and "+ STEERING" in row_turned
            and opened.returncode == 0 and "STEERING ×" in row_opened and "+ PLANS" in row_opened
            and "+ STEERING" not in row_opened and "root" not in row_opened):
        held("the row says the stack and the offer", f"{row!r} (zone spaces at y={zone[1]}, the message at "
             f"y={message[1]}); after a turn {row_turned!r}; then {row_opened!r}")
    else:
        failures.append(f"  ✗ row                         rc={rest.returncode} {row!r} zone={zone} message={message} "
                        f"turned={row_turned!r} opened={row_opened!r} {rest.stderr[-300:]!r} {opened.stderr[-300:]!r}")

    # --- a button plays, the line empty or a message typed ------------------------------------------------------------------
    def launched() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(("space ", "message "))]

    post.clear_journal()
    bare = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},click:#space-open-2:1:0,wait:space")
    bare_sent = launched()
    post.clear_journal()
    typed = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},o,k,click:#space-open-2:1:0,wait:principal")
    typed_sent = launched()
    line = message_line(typed.stdout)
    if (bare.returncode == 0 and bare_sent == ["message ag1 hi", P.spaced("ag1", {"kind": "open", "name": "STEERING"})]
            and "STEERING ×" in P.spaces_row(bare.stdout) and typed.returncode == 0
            and typed_sent == ["message ag1 hi", P.spaced("ag1", OPEN)] and line is not None and "ok" not in line
            and "■ stop" in typed.stdout):
        held("a button plays, the line empty or a message typed", f"the line empty: {bare_sent[-1]!r}, the space open; "
             f"`ok` typed: {typed_sent[-1]!r} "
             "alone, the line emptied, the stop button shown")
    else:
        failures.append(f"  ✗ message                     rc={bare.returncode}/{typed.returncode} bare={bare_sent} "
                        f"typed={typed_sent} line={line!r} stop={'■ stop' in typed.stdout} {typed.stderr[-300:]!r}")

    # --- a click opens, a click closes --------------------------------------------------------------------------
    post.clear_journal()
    waiting = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},o,k,click:#space-open-2:1:0")
    status = P.status_of(waiting.stdout)
    first = list(sent())
    row_after = P.spaces_row(typed.stdout)                # the `space` came before the message's principal
    status_after = P.status_of(typed.stdout)
    post.clear_journal()
    closed = render("ag1", "--render", "dialogue", *SIZE, "--press",
                    f"{TURN},o,k,click:#space-open-2:1:0,wait:space,wait:verdict,click:#space-close-1:1:0,wait:space")
    row_closed = P.spaces_row(closed.stdout)
    if (waiting.returncode == 0 and first == [P.spaced("ag1", OPEN)]
            and "open STEERING" in status and "STEERING ×" in row_after
            and "open STEERING" not in status_after and closed.returncode == 0
            and sent() == [P.spaced("ag1", OPEN), P.spaced("ag1", {"kind": "close"})]
            and "+ STEERING" in row_closed and "×" not in row_closed):
        held("a click opens, a click closes", f"{first[0]!r}; the status waits: {status.strip()[-60:]!r}; then "
             f"{row_after!r}; close: {row_closed!r}")
    else:
        failures.append(f"  ✗ click                       rc={waiting.returncode} {first} {status!r} after={row_after!r} "
                        f"{status_after!r} closed={row_closed!r} {sent()} {closed.stderr[-300:]!r}")

    return 0
