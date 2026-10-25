"""Scenario `ui-conduct` -- the suspension of the conduction and the packages of a run, from a
conversation's tab (plan ui, batch le-on-off-au-poste), on the bench's `pp-chat` witness:
- `o` sends `conduct {"on": false}`: once the witness answered `conduct`, the tab's title carries `⏸`, the footer's
  `[o]` entry and the status say it
- a message under `pp off` is a bare exchange: one answer, no line of conduction, the verdict `unconducted`;
  `o` again sends `conduct {"on": true}`, the `⏸` leaves the title, the status and the `[o]` entry change back
- `o` before the run is opened: the witness refuses `run-missing`, the remedy says it, nothing shows paused
- `k` lists the run's packages as `opened` said them, each with its state; `space` on `plan` then `enter` sends
  `package {"name": "plan", "on": false}`, the list read again says `plan  off`; a name the verb does not
  know is refused `package-unknown`, on the remedy line (the editor of the overlay is `ui-packages`'s)
- `k` before any message lists the packages `ready` said
- a flow whose `ready` and `opened` say no packages: `k` says so on the remedy line, no overlay, nothing sent
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "160x30")          # wide enough for the footer's `[o]` and `[k]`
TALL = ("--size", "160x40")
SENT = "i,h,i,enter,wait:waiting,escape"
CLOCK = re.compile(r"\d\d:\d\d:\d\d")


def status(text: str) -> str:
    """-> the status line of a capture, its hours taken out."""
    return CLOCK.sub("hh:mm:ss", P.status_of(text))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-conduct", P.conduct_script())
    render, tabs_of = post.render, post.tabs_of

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- o: pp off, said once the verb answered ---------------------------------------------------------
    post.clear_journal()
    off = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},o", "--wait", "conduct")
    text = off.stdout
    lines = text.rstrip("\n").split("\n")
    if (off.returncode == 0 and journal("conduct") == ['conduct ag1 {"on": false}'] and "⏸" in tabs_of(text)
            and P.entry_of(text, "o") and P.entry_of(text, "k")):
        held("o suspends the conduction and says it", f"the journal says {journal('conduct')}; the bar "
             f"{tabs_of(text).strip()!r}; the footer says {P.entry_of(text, 'o')!r}")
    else:
        failures.append(f"  ✗ o off                       rc={off.returncode} {post.journal_lines()} {text!r} {off.stderr[-300:]!r}")

    # --- a bare exchange under pp off, then o again: pp on ----------------------------------------------
    post.clear_journal()
    back = render("ag1", "--render", "dialogue", *TALL, "--press",   # both turns in view over a footer of two lines
                  f"{SENT},o,wait:conduct,i,g,o,enter,wait:waiting,escape,o", "--wait", "conduct")
    text_b = back.stdout
    lines_b = text_b.rstrip("\n").split("\n")
    if (back.returncode == 0 and journal("conduct") == ['conduct ag1 {"on": false}', 'conduct ag1 {"on": true}']
            and journal("message") == ["message ag1 hi", "message ag1 go"] and "bare answer" in text_b
            and "unconducted" in text_b and text_b.count("◇") == 2 and "⏸" not in tabs_of(text_b)
            and status(text_b) != status(text) and P.entry_of(text_b, "o") != P.entry_of(text, "o")):
        held("a bare exchange shows no conduction, o brings it back", "under pp off the second message got one "
             "answer, no line of conduction (the first turn's two alone), the verdict unconducted; o again: the journal "
             "says on, no ⏸, the status and the footer's [o] back from their pp-off state")
    else:
        failures.append(f"  ✗ bare and on                 rc={back.returncode} {post.journal_lines()} {text_b!r} {back.stderr[-300:]!r}")

    # --- o before the run: refused run-missing on the remedy ---------------------------------------------
    early = render("ag1", "--render", "dialogue", *SIZE, "--press", "escape,o", "--wait", "refused")
    lines_e = early.stdout.rstrip("\n").split("\n")
    if (early.returncode == 0 and "run-missing" in P.remedy_of(early.stdout) and "⏸" not in tabs_of(early.stdout)
            and P.entry_of(early.stdout, "o") == P.entry_of(text_b, "o")):
        held("o before the run is refused", lines_e[-2].strip()[:90])
    else:
        failures.append(f"  ✗ o early                     rc={early.returncode} {early.stdout!r} {early.stderr[-300:]!r}")

    # --- k: the packages of the run, each with its state -------------------------------------------------
    listed = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k")
    text_k = listed.stdout
    title_k = P.title_of(text_k)
    if (listed.returncode == 0 and title_k[:1] and "w00001" in title_k[0] and "plan  on" in text_k
            and "steering  on" in text_k and "ghost  on" in text_k):
        held("k lists the run's packages", "the overlay says plan on, steering on, ghost on -- as opened said them")
    else:
        failures.append(f"  ✗ k list                      rc={listed.returncode} {text_k!r} {listed.stderr[-300:]!r}")

    # --- k before any message: the packages `ready` said --------------------------------------------------
    before = render("ag1", "--render", "dialogue", *SIZE, "--press", "escape,k")
    if (before.returncode == 0 and "plan  on" in before.stdout and "steering  on" in before.stdout
            and "no package list" not in before.stdout):
        held("k lists the packages before any message", "plan on, steering on -- as ready said them")
    else:
        failures.append(f"  ✗ k early                     rc={before.returncode} {before.stdout!r} {before.stderr[-300:]!r}")

    # --- space then enter on plan: package sent, the list read again says plan off ------------------------
    post.clear_journal()
    toggled = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,space,enter,wait:package,k")
    text_t = toggled.stdout
    if (toggled.returncode == 0 and journal("package") == [P.switched("ag1", "plan", False)]
            and "plan  off" in text_t and "steering  on" in text_t and P.title_of(text_t)):
        held("space then enter toggles a package, the list follows", f"the journal says {journal('package')}; "
             "k again says plan off")
    else:
        failures.append(f"  ✗ k toggle                    rc={toggled.returncode} {post.journal_lines()} {text_t!r} {toggled.stderr[-300:]!r}")

    # --- a name the verb does not know: refused package-unknown on the remedy ----------------------------
    post.clear_journal()
    unknown = render("ag1", "--render", "dialogue", *SIZE, "--press", f"{SENT},k,down,down,space,enter", "--wait", "refused")
    lines_u = unknown.stdout.rstrip("\n").split("\n")
    if (unknown.returncode == 0 and journal("package") == [P.switched("ag1", "ghost", False)]
            and "package-unknown" in P.remedy_of(unknown.stdout)):
        held("a package the verb does not know is refused", lines_u[-2].strip()[:90])
    else:
        failures.append(f"  ✗ k unknown                   rc={unknown.returncode} {post.journal_lines()} {unknown.stdout!r} {unknown.stderr[-300:]!r}")

    # --- a flow with no packages: k says so, nothing sent ------------------------------------------------
    post.clear_journal()
    bare = render("ag2", "--render", "dialogue", *SIZE, "--press", f"{SENT},k")
    lines_n = bare.stdout.rstrip("\n").split("\n")
    if (bare.returncode == 0 and P.remedy_of(bare.stdout) and journal("package") == []
            and not P.title_of(bare.stdout)):
        held("k without a list says so", lines_n[-2].strip()[:90])
    else:
        failures.append(f"  ✗ k no list                   rc={bare.returncode} {post.journal_lines()} {bare.stdout!r} {bare.stderr[-300:]!r}")
    return 0
