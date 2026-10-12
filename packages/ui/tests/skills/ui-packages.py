"""Scenario `ui-packages` -- the overlay of the packages of a run, an editor of its own (plan ui, batch
l-overlay-des-packages), on the bench's `pp-chat` witness: `ag1`'s run plays `plan`, `steering` and `ghost`; a switch
of `steering` waits for the next message, one of `plan` plays at once, `ghost` is a name the verb does not know:
- `k` then `space` on two lines: both marked `on → off`, nothing sent
- `enter` sends one `package` per line changed; `escape` sends none
- a switch that waits is seen until it plays: `⧗` on the tab's title, `packages: steering off …` on the status, `k`
  says `pending`; the next message plays it and every mark leaves
- a switch the verb refuses: the remedy says its code and its detail, nothing waits
The packages in a run's profile, and a package required: `ui-packages-profile`.
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "160x30")
SENT = "h,i,enter,wait:waiting,escape"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-packages", P.held_script())
    render, tabs_of = post.render, post.tabs_of

    def sent() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("package")]

    # --- space toggles in the overlay alone ------------------------------------------------------------
    post.clear_journal()
    toggled = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,down,space", "--wait", "none:1")
    rows = [row for row in toggled.stdout.split("\n") if "→" in row]
    if (toggled.returncode == 0 and sent() == [] and any("plan" in row and "on → off" in row for row in rows)
            and any("steering" in row and "on → off" in row for row in rows) and "[space] toggle" in toggled.stdout):
        held("space toggles in the overlay alone", "plan and steering marked on → off; the journal has no package")
    else:
        failures.append(f"  ✗ toggle                      rc={toggled.returncode} {sent()} {toggled.stdout!r} "
                        f"{toggled.stderr[-300:]!r}")

    # --- enter sends the differences, escape none --------------------------------------------------------
    post.clear_journal()
    applied = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,down,space,enter,wait:package,k")
    first = sent()
    text = applied.stdout
    status = text.rstrip("\n").split("\n")[-1]
    post.clear_journal()
    render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,escape", "--wait", "none:1")
    cancelled = sent()
    if (applied.returncode == 0 and first == ['package ag1 {"name": "plan", "on": false}',
                                              'package ag1 {"name": "steering", "on": false}'] and cancelled == []):
        held("enter sends the differences, escape none", f"enter: {first}; escape: no package")
    else:
        failures.append(f"  ✗ apply                       {first} / {cancelled} {applied.stderr[-300:]!r}")

    # --- the wait is seen until it plays ------------------------------------------------------------------
    pending = [row for row in text.split("\n") if "steering" in row and "pending" in row]
    post.clear_journal()
    played = render("ag1", "--render", "dialogue", *SIZE, "--press",
                    f"{SENT},k,down,space,enter,wait:package,i,g,o,enter", "--wait", "principal")
    status_p = played.stdout.rstrip("\n").split("\n")[-1]
    if (applied.returncode == 0 and "⧗" in tabs_of(text) and "packages: steering off …" in status and pending
            and played.returncode == 0 and "⧗" not in tabs_of(played.stdout) and "packages:" not in status_p
            and sent() == ['package ag1 {"name": "steering", "on": false}']):
        held("a switch that waits is seen until it plays", f"the bar {tabs_of(text).strip()!r}, the status "
             f"`packages: steering off …`, k says {pending[0].strip(' ┃')!r}; after the next message, no mark")
    else:
        failures.append(f"  ✗ pending                     bar={tabs_of(text)!r} status={status!r} pending={pending} / "
                        f"bar={tabs_of(played.stdout)!r} status={status_p!r} {sent()} {played.stderr[-300:]!r}")

    # --- a refusal says its code and its detail ----------------------------------------------------------
    refused = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,down,down,space,enter",
                     "--wait", "refused")
    lines = refused.stdout.rstrip("\n").split("\n")
    if (refused.returncode == 0 and "package-unknown" in lines[-2] and "no package `ghost` pinned here" in lines[-2]
            and "⧗" not in tabs_of(refused.stdout)):
        held("a refused switch is said with its detail", lines[-2].strip()[:100])
    else:
        failures.append(f"  ✗ refused                     rc={refused.returncode} {lines[-3:]!r} {refused.stderr[-300:]!r}")
    return 0
