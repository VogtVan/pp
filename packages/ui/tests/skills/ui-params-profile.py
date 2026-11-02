"""Scenario `ui-params-profile` -- the profile of a NEW run, on the bench's `pp-chat` witness and its faces (`ag1`'s
`status --json` says `packages`, `plan` and `steering` both on; `ag2` never played a model and says no packages):
- one new run of `ag1` chosen whole: `strict` from the regime's list, `plan` toggled off in the overlay of the
  packages, a name typed; `enter` opens the conversation with `--permissions strict --package plan=off` after the flags
  the agent last played, and `agent name` plays once the flow's `opened` says the key -- after the first message
- `enter` on the closed list opens the conversation, no flag composed for an untouched field, the overlay gone
- the line of the packages says the state of each one, a toggled one marked before `enter`
- `n` on `ag2` under `--styles`: the titles of the fields bold, the help under a field lighter than the text -- its
  weight at most half the text's, an example's the same --, the free fields left empty showing their example, no
  line of packages
- a house wired with no provider (its faces say none, `last` played by `--harness`): `enter` opens the conversation
  with the flags of `--` alone, no `--provider` composed
"""
from __future__ import annotations

import re

from tests.harness import support

P = support(__file__, "dialogue")
SIZE = ("--size", "110x45")
PAUSE = ("--wait", "none:1.5")       # no event of that kind comes: a pause for the providers' face
OPEN = "2,n,wait:none:1.5"           # the overlay of a new run of ag1, the providers' face read
TO_PACKAGES = "tab,tab,tab,tab"      # from the model, down to the packages: budget, effort, permissions, packages;
                                     # the name stands under them
SEGMENT = re.compile(r"\x1b\[([0-9;]*)m([^\x1b]*)")


def look(capture: str, words: str) -> tuple | None:
    """-> (bold, fg, bg) of the segment of a `--styles` capture that holds `words`, or None."""
    for params, text in SEGMENT.findall(capture):
        if words not in text:
            continue
        parts, bold, fg, bg, at = params.split(";"), False, None, None, 0
        while at < len(parts):
            if parts[at] in ("38", "48") and at + 4 < len(parts) and parts[at + 1] == "2":
                colour = tuple(int(one) for one in parts[at + 2:at + 5])
                fg, bg = (colour, bg) if parts[at] == "38" else (fg, colour)
                at += 5
                continue
            bold = bold or parts[at] == "1"
            at += 1
        return bold, fg, bg
    return None


def weight(found: tuple | None) -> float:
    """-> how far a segment's colour stands from its background, the brightest channel: its weight."""
    if not found or found[1] is None or found[2] is None:
        return -1.0
    return max(abs(a - b) for a, b in zip(found[1], found[2]))


def firsts(rows: list[str]) -> list[str]:
    """-> the first word of every row: a field's title, or its value before its arrow."""
    return [row.split()[0] for row in rows if row.split()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-profile")
    render = post.render

    def journal(prefix: str) -> list[str]:
        return [one for one in post.journal_lines() if one.startswith(prefix)]

    # --- one new run chosen whole: strict, plan off, a name played once opened ------------------------------
    post.clear_journal()
    whole = render("--render", "dialogue", *SIZE, "--press",
                   f"{OPEN},tab,tab,tab,space,down,down,enter,tab,tab,d,e,m,o,shift+tab,enter,space,enter,enter,"
                   "wait:waiting,i,h,i,enter,wait:waiting", *PAUSE)
    opens = journal("open")
    flags = opens[0].split(" ")[2:] if len(opens) == 1 else []
    order = [one.split(" ")[0] for one in post.journal_lines() if one.split(" ")[0] in ("open", "message", "name")]
    if (whole.returncode == 0 and flags[:4] == ["--provider", P.PROVIDER, "--model", "m1"]
            and sorted(" ".join(flags[4:]).split(" --")) == sorted(["--permissions strict", "package plan=off"])
            and journal("name") == ["name ag1 w00001 demo"] and order == ["open", "message", "name"]
            and "demo" in post.tabs_of(whole.stdout)):
        held("a new run chosen whole", f"the journal says {opens}, then {order}; the tab says demo")
    else:
        failures.append(f"  ✗ whole                       {post.journal_lines()} {post.tabs_of(whole.stdout)!r} "
                        f"{whole.stdout[-800:]!r} {whole.stderr[-300:]!r}")

    # --- enter on the closed list: no flag for an untouched field, the overlay gone ---------------------------
    post.clear_journal()
    closed = render("--render", "dialogue", *SIZE, "--press", "2,n,tab,tab,tab,enter,wait:waiting", "--wait", "none:1")
    opens = journal("open")
    if closed.returncode == 0 and opens == [f"open ag1 --provider {P.PROVIDER} --model m1"] and not P.title_of(closed.stdout):
        held("enter on the closed list validates", f"the journal says {opens}; the overlay closed")
    else:
        failures.append(f"  ✗ closed list                 rc={closed.returncode} opens={opens} {closed.stdout[-800:]!r} "
                        f"{closed.stderr[-200:]!r}")

    # --- the line of the packages, a toggled one marked ----------------------------------------------------
    staged = render("--render", "agents", *SIZE, "--press", f"n,wait:none:1.5,{TO_PACKAGES},enter,space,enter", *PAUSE)
    marked = [row for row in P.overlay_rows(staged.stdout) if "plan on → off" in row and "steering on" in row]
    if staged.returncode == 0 and marked:
        held("the line of the packages says each one", f"the line of the face says {marked[0]!r}")
    else:
        failures.append(f"  ✗ staged                      {P.overlay_rows(staged.stdout)!r} {staged.stderr[-300:]!r}")

    # --- n on ag2 under --styles: titles bold, help and example light, the examples, no packages -------------
    shown = render("--render", "agents", "--size", "120x60", "--press", "down,n", *PAUSE, "--styles")
    rows = P.overlay_rows(P.ANSI.sub("", shown.stdout))
    titles = [P.field_title(one) for one in ("provider", "model", "budget", "effort", "permissions", "name")]
    looks = {one: look(shown.stdout, one) for one in titles}
    budget = P.palette_constant("BUDGET_EXAMPLE")
    examples = (f"{budget.split(' ')[0]} {P.MODELS[0]}", budget, P.palette_constant("EFFORT_EXAMPLE"),
                P.palette_constant("NAME_EXAMPLE"))
    at = next((n for n, row in enumerate(rows) if budget in row), -1)
    under = rows[at + 2] if 0 <= at < len(rows) - 2 else ""          # the help under the field, below its border
    text, help_, example = looks["Budget"], look(shown.stdout, under[:12]) if under else None, look(shown.stdout, budget)
    if (shown.returncode == 0 and all(one in firsts(rows) for one in titles) and all(one and one[0] for one in looks.values())
            and help_ and not help_[0] and 0 < weight(help_) <= weight(text) / 2 and 0 < weight(example) <= weight(text) / 2
            and all(any(word in row for row in rows) for word in examples)
            and P.field_title("packages") not in firsts(rows)):
        held("n: titles bold, help light, examples", f"{', '.join(titles)} bold; help weight {weight(help_):g}, example "
             f"{weight(example):g}, text {weight(text):g}; {', '.join(examples)}; no packages for ag2")
    else:
        failures.append(f"  ✗ n                           rc={shown.returncode} looks={looks} text={text} help={help_} "
                        f"example={example} rows={[one for one in rows if one]!r} {shown.stderr[-300:]!r}")

    # --- a house wired with no provider: no --provider composed --------------------------------------------
    faces = {**P.FACES, "providers": [],
             "status": {"ag1": [dict(P.FACES["status"]["ag1"][0]),
                                {"agent": "ag1", "providers": [], "last": {"provider": "harness", "policy": {}}}]}}
    post.use({"agents": {"ag1": P.script("w00001", "the agent says")}, "faces": faces})
    post.clear_journal()
    opened = render("--render", "dialogue", "--size", "110x40", "--press", "2,n,enter,wait:waiting",
                    "--wait", "none:0.5", "--", "--harness", "x")
    opens = journal("open ")
    if opened.returncode == 0 and opens == ["open ag1 --harness x"]:
        held("n on a house wired with no provider", f"enter: the journal says {opens}")
    else:
        failures.append(f"  ✗ unwired                     rc={opened.returncode} {opens} {opened.stderr[-300:]!r}")
    return 0
