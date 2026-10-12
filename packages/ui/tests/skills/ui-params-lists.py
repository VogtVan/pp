"""Scenario `ui-params-lists` -- `model` and `effort` are lines that list (plan ui, batch les-retours-du-reel-0-18;
beside `ui-params`, rule 10), on the bench's `pp-chat` witness and its faces (`ag1` last played `{model: m1}`;
`providers --json` names the fixture's two models):
- `down` on `model` unrolls the models the adapter declares under the line, each on a row of the list; the helps say
  `[down] lists`
- in the list `enter` fills the line and folds the list; `enter` in the line then opens the run with that name
- the list is filtered by what the line holds (its prefix, any case): the prefix of the second then `down` lists it alone;
  a line no name begins with lists them all
- `effort` the same with its five words; `escape` in a list folds it and leaves the line as it was, the overlay up
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
OPEN = "2,n,wait:none"                # the overlay of a new run of ag1, a pause for the providers' face: an
                                     # inline wait is bound by the seconds of `--wait`


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-params-lists")
    render = post.render

    def opens() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("open")]

    # --- down unrolls the models under the line --------------------------------------------------------
    shown = render("--render", "dialogue", "--size", "110x40", "--press", f"{OPEN},down", "--wait", "none:1.5")
    text = shown.stdout
    rows = [row.strip(" ┃│").strip() for row in text.split("\n")]
    if shown.returncode == 0 and P.MODELS[0] in rows and P.MODELS[1] in rows and "[down] lists" in text:
        held("down unrolls the models", f"{P.MODELS[0]} and {P.MODELS[1]} each on a row of the list under the line; "
             "the helps say [down] lists")
    else:
        failures.append(f"  ✗ unrolled                    rc={shown.returncode} {text!r} {shown.stderr[-300:]!r}")

    # --- every model, enter fills; effort filtered by its prefix --------------------------------------
    post.clear_journal()
    chosen = render("--render", "dialogue", "--size", "110x40", "--press",
                    f"{OPEN},down,enter,tab,tab,h,down,enter,enter", "--wait", "waiting:2")
    first = opens()
    # --- the model filtered by its prefix; escape folds the effort's list, then medium chosen ----------
    post.clear_journal()
    filtered = render("--render", "dialogue", "--size", "110x40", "--press",
                      f"{OPEN},{','.join(P.MODELS[1][:6])},down,enter,tab,tab,down,escape,down,down,enter,enter", "--wait", "waiting:2")
    second = opens()
    if (chosen.returncode == 0 and first == [f"open ag1 --provider {P.PROVIDER} --model {P.MODELS[0]} --effort high"]
            and filtered.returncode == 0
            and second == [f"open ag1 --provider {P.PROVIDER} --model {P.MODELS[1]} --effort medium"]):
        held("enter in a list fills the line, the list filtered", f"m1 lists all and enter takes the first, h lists "
             f"high alone: {first}; {P.MODELS[1][:6]} lists the second alone, escape folds the effort's list: {second}")
    else:
        failures.append(f"  ✗ chosen                      {first} / {second} {chosen.stderr[-300:]!r} "
                        f"{filtered.stdout[-1500:]!r}")
    return 0
