"""Scenario `ui-spaces` -- the row of the SPACES of a conversation (plan ui, batch les-boutons-des-espaces), on the
bench's `pp-chat` witness whose run offers `PLANS` and `STEERING` as spaces:
- the row says the stack and the offer: `ready.spaces` draws `+ PLANS · + STEERING` above the message line, a zone of
  `--regions` (`ready` says no root); the block step of the first exchange adds `root TURN`, the other steps, without
  `spaces` nor `root`, change nothing; a block step of the second exchange that says `STEERING` open draws
  `STEERING ×` and `+ PLANS`, the root no more (the space is the root)
- a click opens, a click closes: `+ STEERING` writes `{"kind": "open", "name": "STEERING"}` on the witness's
  entry, the status says the wait until the `space` event, then the row says `STEERING ×`; a click on it writes
  `{"kind": "close"}` and the row offers `STEERING` again
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "120x30")
TURN = "i,h,i,enter,wait:waiting"


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
    opened = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},i,g,o,enter,wait:step")
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

    # --- a click opens, a click closes --------------------------------------------------------------------------
    post.clear_journal()
    waiting = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},click:#space-open-2:1:0")
    status = P.status_of(waiting.stdout)
    first = list(sent())
    post.clear_journal()
    after = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{TURN},click:#space-open-2:1:0,wait:space")
    row_after = P.spaces_row(after.stdout)
    status_after = P.status_of(after.stdout)
    post.clear_journal()
    closed = render("ag1", "--render", "dialogue", *SIZE, "--press",
                    f"{TURN},click:#space-open-2:1:0,wait:space,click:#space-close-1:1:0,wait:space")
    row_closed = P.spaces_row(closed.stdout)
    if (waiting.returncode == 0 and first == [P.spaced("ag1", {"kind": "open", "name": "STEERING"})]
            and "open STEERING" in status and after.returncode == 0 and "STEERING ×" in row_after
            and "open STEERING" not in status_after and closed.returncode == 0
            and sent() == [P.spaced("ag1", {"kind": "open", "name": "STEERING"}), P.spaced("ag1", {"kind": "close"})]
            and "+ STEERING" in row_closed and "×" not in row_closed):
        held("a click opens, a click closes", f"{first[0]!r}; the status waits: {status.strip()[-60:]!r}; then "
             f"{row_after!r}; close: {row_closed!r}")
    else:
        failures.append(f"  ✗ click                       rc={waiting.returncode} {first} {status!r} after={row_after!r} "
                        f"{status_after!r} closed={row_closed!r} {sent()} {closed.stderr[-300:]!r}")

    return 0
