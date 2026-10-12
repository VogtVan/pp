"""Scenario `ui-overlays` -- overlays that hold (plan ui, batch les-overlays-qui-tiennent), on the bench's `pp-chat`
witness:
- a `◀` line of 4k characters over 80 lines opened at 120x40: its title on ONE line, the kind first (`agent answer`),
  `[esc] close` in sight, its last line read after `end`
- the parameters of a run at 80x24: `p`, then `tab` from the model down to the last field -- `permissions` in sight
  and `[enter] sets · [space] lists`
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
TURN = "h,i,enter,wait:waiting"
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    def title_of(text: str) -> list[str]:
        """-> the title of the overlay: its first rows of text inside the border, up to the first blank row."""
        rows = text.split("\n")
        top = next((n for n, row in enumerate(rows) if "┏" in row and "┓" in row), -1)
        if top < 0:
            return []
        left, right = rows[top].index("┏"), rows[top].index("┓")
        found: list[str] = []
        for row in rows[top + 1:]:
            inner = row[left + 1:right].strip() if len(row) > right else ""
            if not inner and not found:
                continue                              # the box's padding above the title
            if not inner or inner.startswith("━"):
                break
            found.append(inner)
        return found

    # --- a long answer opens and closes ------------------------------------------------------------
    long = P.Post(bench, "ui-overlays-long", P.long_answer_script())
    answer_up = ",".join(["shift+tab"] * 3)                 # from the message line, up to launch 1's ◀ line
    opened = long.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", f"{TURN},{answer_up},enter,end")
    title = title_of(opened.stdout)
    if (opened.returncode == 0 and len(title) == 1 and title[0].startswith("agent answer")
            and "[esc] close" in opened.stdout and "answer line 80 -- the end of the answer" in opened.stdout):
        held("a long answer opens and closes", f"the title on one row ({title[0][:40]!r}…); [esc] close in sight; "
             "after end its last line read")
    else:
        failures.append(f"  ✗ long answer                 rc={opened.returncode} title={title} {opened.stdout[-1500:]!r} "
                        f"{opened.stderr[-300:]!r}")

    # --- the parameters at 80x24: the last field and the keys in sight ----------------------------------
    small = P.Post(bench, "ui-overlays-params")
    params = small.render("ag1", "--render", "dialogue", "--size", "80x24", "--press",
                          f"{TURN},escape,p,wait:none:1.5,tab,tab,tab", *PAUSE)
    if params.returncode == 0 and "permissions" in params.stdout and "[enter] sets · [space] lists" in params.stdout:
        held("the parameters reach their last field at 80x24", "permissions and [enter] sets · [space] lists in sight")
    else:
        failures.append(f"  ✗ params 80x24                rc={params.returncode} {params.stdout!r} {params.stderr[-300:]!r}")
    return 0
