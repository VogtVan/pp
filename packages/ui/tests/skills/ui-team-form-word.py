"""Scenario `ui-team-form-word` -- the owner's word and the season's written from the forms (batch
les-formulaires-jumeaux, team 1.27.0), on the bench's `pp-team` witness, `core-review` off season, its TEAM.md with a
body (the edges: `ui-team-form-edges`, cut by case, rule 10):
- `E`, the owner's word typed on a new line (`enter` in the text goes to the line, s.1647), `ctrl+enter` from the
  text itself (batch les-touches-du-poste): `team declare core-review --body-file -`, the body read on its standard
  input
- `S`, the season's word typed, `ctrl+s`: `team declare core-review --season --body-file - --context 90`, the body on its
  input, then `team start core-review`
- `E`, the owner's word: its field takes the whole height of the fields' zone -- its help on the zone's last rows --, and
  the side pane shows the words rendered as markdown as they are typed -- a title and an emphasis drawn, their marks
  gone (batch les-volets-par-onglet) --, by Textual's `Markdown` as the overlay `e` draws (AV5): the words' title a
  `MarkdownH1`, TEAM.md's keys a `MarkdownFence` (`blocks`); its lines broken by `enter`, nothing played, and the
  line of keys gives `enter` the label `FORM_TEXT_ENTER` there, beside `palette.SEND_KEY` and its verb
"""
from __future__ import annotations

import json

from tests.harness import support

F = support(__file__, "team_forms")
W = support(__file__, "team_form_word")
T, P = F.T, F.P

TO_WORD = F.team_to("Owner's word")             # the owner's word, the last section
TO_SEASON_WORD = F.season_to("Season's word")   # from the preset `S` focuses: the season's word
MARKED = "# Rules"                              # a title, then an emphasis: what the words render draws without marks
EMPHASIS = "Be **brief**."


def constant(name: str) -> str | None:
    """-> the string constant `name` of `palette.py`, None while it has none."""
    try:
        return P.palette_constant(name)
    except KeyError:
        return None


def bodies(house) -> list[str]:
    return [json.loads(one[len("body "):]) for one in house.journal_lines() if one.startswith("body ")]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-word", T.script(declarations={**T.DECLARATIONS, "core-review": W.EDGED}))

    # --- the owner's word: on the standard input of team declare -------------------------------------------------------
    house.render("--render", "teams", *F.SIZE, "--press", f"E,{TO_WORD},end,enter," + F.typed("Be brief.") + ",ctrl+enter")
    wanted = ["team declare core-review --body-file - --json"]
    if house.gestures() == wanted and bodies(house) == ["The owner's word.\nBe brief.\n"]:
        held("the owner's word written on the input", f"{wanted[0]}; {bodies(house)}")
    else:
        failures.append(f"  ✗ owner's word                {house.gestures()} {bodies(house)}")

    # --- the season's word, then the start ---------------------------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"S,{TO_SEASON_WORD}," + F.typed("Go slow.") + ",ctrl+s")
    wanted = ["team declare core-review --season --body-file - --context 90 --json", T.NEXT]
    if house.gestures() == wanted and bodies(house) == ["Go slow.\n"]:
        held("the season's word written, then the start", f"{wanted}; {bodies(house)}")
    else:
        failures.append(f"  ✗ season's word               {house.gestures()} {bodies(house)}")

    # --- the owner's word on the whole height, rendered as it is typed ------------------------------------------------
    house.clear_journal()
    typed = f"E,{TO_WORD},ctrl+home,{F.typed(MARKED)},enter,{F.typed(EMPHASIS)},enter,boxes,blocks"
    shown = house.render("--render", "teams", *F.SIZE, "--press", typed)
    keys, entered = F.keys_row(shown.stdout), constant("FORM_TEXT_ENTER")
    words, rows = F.zone_rows(shown.stdout, "form-words"), F.fields(shown.stdout)
    said = " ".join(words)
    blocks = next((one[len("blocks "):].split(",") for one in shown.stdout.splitlines() if one.startswith("blocks ")),
                  [])
    last = max((n for n, row in enumerate(rows) if row), default=-1)
    if (shown.returncode == 0 and "Rules" in said and MARKED not in said and "Be brief." in said
            and "**" not in said and len(rows) > 10 and last >= len(rows) - 3
            and {"MarkdownH1", "MarkdownFence"} <= set(blocks)
            and house.gestures() == [] and keys and P.send_key()[0] and f"[{P.send_key()[0]}] {P.send_key()[1]}" in keys
            and entered is not None and keys.count("[enter]") == 1 and f"[enter] {entered}" in keys):
        held("the owner's word on the whole height, rendered as typed, enter its new line",
             f"{len(rows)} rows, the last written at {last}; {[one for one in words if one][:3]}; "
             f"blocks {sorted(set(blocks))}; nothing played; {keys!r}")
    else:
        failures.append(f"  ✗ words                       rc={shown.returncode} {words} {blocks} {rows} "
                        f"{house.gestures()} {keys!r} "
                        f"{shown.stderr[-300:]!r}")
    return 0
