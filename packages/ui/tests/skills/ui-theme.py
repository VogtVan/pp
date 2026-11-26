"""Scenario `ui-theme` -- the theme of the post, chosen in a list, and the looks of a conversation in a dark and a
light theme, on a throwaway house pinning `ui` and the bench's witness of `agent`:
- `t` opens the overlay of the themes Textual knows: the light ones first, the dark, `ansi-*` last, the
  current one marked
- the theme under the cursor applies once the cursor rests: `t`, `down` leaves the header in the look of the theme
  of before, `t`, `down`, `rest:0.6` draws it in `nord`'s; `t`, `down`, `rest:0.6`, `escape` brings `textual-dark`
  back -- the footer's `t` and the memory unchanged
- `t`, `down`, `enter` keeps the theme after the current one, at once: the post's memory says it in the space `ui` of
  the metadata, the footer's `t` names it; the next opening takes it without a key
- a conversation after a turn that thinks (the script swapped by `use()`), one styled render per theme kept in the
  memory: a row of `─` between the transcript and the message line, the message line in `┌─┐`, a row of `─` above
  the footer; under `textual-dark` and `textual-light` the rows drawn in a look of the theme -- not the status
  line's, and not the same in the two themes
- a line with nothing to open (a thought of a count alone) is drawn in the `STALE` look under both themes: neither
  the dim of a line of conduction nor the look of the head of the agent's words, and not the same in the two themes
- the table of the judgments (`model/looks.py`, pure, loaded from the source): a ratio on each side of each of its
  thresholds gives the code it says for a measure where going up is the wrong side; a measure without a sense, a
  ratio without a median and fewer seasons than its minimum give `nominal`; a share on each side of each of its own
  thresholds gives its code, `muted` without a share; a ratio is said without colour, `▲ ×1.46`, `▼ ×0.55` -- every
  threshold read in the module, never typed again here
- the plate (`--render looks`), without `--styles`: each judged cell carries its glyph and its ratio; the figures and
  the ratios of its table end on one column, aligned right
- the plate under `--styles`, in `textual-dark` then `textual-light`: `good`, `watch` and `alert` drawn each in a look
  of its own, not the same in the two themes; the table's header, its rows, its other rows and the tile each on a
  ground, the header and the two kinds of rows on three different ones; the `alert` cell on a ground of its own, in
  bold; under `ansi-dark`, that cell in bold without a mixed ground
- the share of the stopped tasks judged under the path the face gives it, `stopped_tasks.share`; the plate says each
  code a share gives without colour: `nominal` bare, `watch` with its mark, `alert` with its own, read in the module
- the closing rows of the plate's table on the header's ground; under `textual-dark` the tile and the bar each on a
  ground other than the page's (under `textual-light` `$boost` is transparent: the tile takes the page's)
- a threshold is written once: the plate's ratios are not typed numbers, and the gauge's warning of the budget
  (`palette.WARN_SHARE`) is not a number of its own -- both read from the table
"""
from __future__ import annotations

import ast
import importlib.util
import re

from conductor import metadata
from tests.harness import support

P = support(__file__, "dialogue")

RULE = r"^\s*─{60,}\s*$"
LOOKS = P.SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "model" / "looks.py"
PLATE = P.SOURCE / "packages" / "ui" / "skills" / "pp-ui" / "panes" / "looks.py"
RATIO = re.compile(r"[▲▼=] ×\d+\.\d\d")


def _look(row: str) -> frozenset:
    """-> the styles (SGR sequences) one raw row of a `--styles` capture is drawn with."""
    return frozenset(P.SGR.findall(row)) - {"0", ""}


def _rules(lines: list[str]) -> list[int]:
    return [index for index, line in enumerate(lines) if re.match(RULE, line)]


def _judgments():
    """-> the module of the table of the judgments, loaded from the source -- pure, no Textual --; None while absent."""
    try:
        spec = importlib.util.spec_from_file_location("pp_ui_model_looks", LOOKS)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except (OSError, ImportError, SyntaxError):
        return None
    return module


def _params(styles: frozenset):
    """-> each attribute of a look, as its SGR says it: a colour whole (`38;2;r;g;b`, `48;5;n`), any other alone."""
    for one in styles:
        said, at = one.split(";"), 0
        while at < len(said):
            width = (5 if said[at + 1:at + 2] == ["2"] else 3) if said[at] in ("38", "48") else 1
            yield ";".join(said[at:at + width])
            at += width


def _grounds(styles: frozenset) -> frozenset:
    """-> the grounds (background colours) a look carries, each as its SGR spells it."""
    return frozenset(one for one in _params(styles)
                     if one.startswith("48;") or one == "49" or re.fullmatch(r"4[0-7]|10[0-7]", one))


def _bold(styles: frozenset) -> bool:
    return "1" in set(_params(styles))


def _row_look(text: str, pattern: str) -> frozenset:
    """-> the styles of the first row of a `--styles` capture whose text, every control sequence taken off (the
    cursor's place that opens a row among them), matches `pattern`; empty when none does."""
    for row in text.split("\n"):
        if re.search(pattern, P.ANSI.sub("", row)):
            return frozenset(P.SGR.findall(row)) - {"0", ""}
    return frozenset()


def _end(row: str, pattern) -> int | None:
    """-> the column where the first match of `pattern` in a plain row ends; None without one."""
    found = re.search(pattern, row)
    return found.end() if found else None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-theme")

    def kept() -> str:
        return str(metadata.of_package(post.made, "ui").get("theme") or "")

    def theme_entry(played) -> str:
        return P.entry_of(played.stdout, "t")

    # --- t: the list of the themes, the current one marked ---------------------------------------------
    listed = post.render("--render", "frame", "--size", "120x40", "--press", "t")
    text = listed.stdout
    order = [name for name in ("textual-light", "atom-one-light", "textual-dark", "nord", "ansi-dark") if name in text]
    marked = [row for row in text.split("\n") if "●" in row]
    if (listed.returncode == 0 and len(order) == 5 and len(marked) == 1 and "textual-dark" in marked[0]
            and text.index("textual-light") < text.index("textual-dark") < text.index("nord") < text.index("ansi-dark")):
        held("t lists the themes, the current one marked", "light first, then the dark, ansi last; textual-dark marked")
    else:
        failures.append(f"  ✗ list                        rc={listed.returncode} {order} {text!r} {listed.stderr[-300:]!r}")

    # --- the preview waits for the cursor to rest; escape brings the theme of before back --------------
    def header(*keys: str) -> tuple:
        pressed = ("--press", ",".join(keys)) if keys else ()
        shown = post.render("--render", "frame", "--size", "120x30", *pressed, "--styles")
        return (shown.returncode, P.styles_of(shown.stdout, r" pp · ui-theme"),
                P.entry_of(P.ANSI.sub("", shown.stdout), "t"), shown.stderr[-300:])
    before, moved, rested = header("t"), header("t", "down"), header("t", "down", "rest:0.6")
    plain, restored = header(), header("t", "down", "rest:0.6", "escape")
    if (all(one[0] == 0 and one[1] for one in (before, moved, rested, plain, restored)) and moved[1] == before[1]
            and rested[1] != before[1] and restored[1] == plain[1] and "textual-dark" in restored[2]
            and kept() == ""):
        held("the preview waits for the cursor to rest", f"t, down: the header as before {sorted(before[1])}; after "
             f"rest:0.6 {sorted(rested[1])}; escape: the header of textual-dark again, {restored[2]!r}, nothing kept")
    else:
        failures.append(f"  ✗ preview                     {before} / {moved} / {rested} / {plain} / {restored} "
                        f"kept={kept()!r}")

    # --- t, down, enter keeps the next one at once; the next opening takes it ----------------------------
    chose = post.render("--render", "frame", "--size", "120x30", "--press", "t,down,enter")
    remembered = kept()
    again = post.render("--render", "frame", "--size", "120x30", keep=True)
    if (chose.returncode == 0 and remembered == "nord" and remembered in theme_entry(chose)
            and again.returncode == 0 and remembered in theme_entry(again)):
        held("enter keeps the theme, the post remembers", f"down from textual-dark: {remembered!r} in the memory, "
             f"{theme_entry(chose)!r} in the footer; the next opening is {remembered} without a key")
    else:
        failures.append(f"  ✗ keep                        {theme_entry(chose)!r} kept={remembered!r} / "
                        f"{theme_entry(again)!r} {chose.stderr[-300:]!r}")

    # --- a conversation after a turn that thinks, in each theme the memory keeps -------------------------
    post.use(P.thinking_script())
    looks, stales = {}, {}
    for theme in ("textual-dark", "textual-light"):
        P.keep_theme(post.made, theme)
        done = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", "i,h,i,ctrl+enter",
                           "--wait", "waiting", "--styles", keep=True)
        raw = done.stdout.rstrip("\n").split("\n")
        lines = [P.ANSI.sub("", one) for one in raw]
        rules = _rules(lines)
        box = next((index for index, line in enumerate(lines) if "┌" in line and index > 3), None)
        keys = P.keys_rows("\n".join(lines))
        first_keys = next((index for index, line in enumerate(lines) if keys and line.strip() == keys[0]), None)
        looks[theme] = (_look(raw[rules[-1]]) if rules else frozenset(), _look(raw[-1]))
        stales[theme] = (P.styles_of(done.stdout, r"∴ \d\d:\d\d:\d\d · launch 1 · thinking ~42 tokens"),
                         P.styles_of(done.stdout, r"◇ \d\d:\d\d:\d\d · launch 1 · "),
                         P.styles_of(done.stdout, r"◀ \d\d:\d\d:\d\d · launch 1\s*$"))
        if (done.returncode == 0 and theme in P.entry_of("\n".join(lines), "t") and box is not None
                and box - 1 in rules and first_keys is not None and first_keys - 1 in rules):
            held(f"the dialogue set apart under {theme}", f"─ above the message line (row {box - 1}) drawn in ┌─┐, "
                 f"─ above the footer (row {first_keys - 1})")
        else:
            failures.append(f"  ✗ dialogue {theme:<18} rc={done.returncode} rules={rules} box={box} keys={first_keys} "
                            f"{lines!r} {done.stderr[-300:]!r}")
    dark, light = looks["textual-dark"], looks["textual-light"]
    if dark[0] and light[0] and dark[0] != dark[1] and light[0] != light[1] and dark[0] != light[0]:
        held("the line in each theme's look", f"dark {sorted(dark[0])} against its status {sorted(dark[1])}; "
             f"light {sorted(light[0])} against {sorted(light[1])}")
    else:
        failures.append(f"  ✗ looks                       {looks!r}")

    # --- STALE is its own look in a dark and a light theme: neither dim nor a live line --------------------
    if (all(stale and stale != dim and stale != alive for stale, dim, alive in stales.values())
            and stales["textual-dark"][0] != stales["textual-light"][0]):
        held("STALE is its own look in both themes", "; ".join(
            f"{theme}: ∴ {sorted(one[0])} against ◇ dim {sorted(one[1])} and the head of the words {sorted(one[2])}"
            for theme, one in stales.items()))
    else:
        failures.append(f"  ✗ stale in both themes        {stales!r}")

    # --- the table of the judgments: the codes, the senses, the thresholds, read in their module -------------------
    looks, step = _judgments(), 0.01
    if looks is None:
        failures.append(f"  ✗ judgments                   no table at {LOOKS}")
    else:
        bad = next(measure for measure, sense in looks.SENSE.items() if sense == looks.UP_BAD)
        flat = next(measure for measure, sense in looks.SENSE.items() if sense is None)
        over = looks.SEASONS_MIN
        wanted = [(looks.RATIO_GOOD - step, looks.GOOD), (looks.RATIO_GOOD, looks.GOOD),
                  (looks.RATIO_GOOD + step, looks.NOMINAL), (looks.RATIO_WATCH - step, looks.NOMINAL),
                  (looks.RATIO_WATCH, looks.WATCH), (looks.RATIO_ALERT - step, looks.WATCH),
                  (looks.RATIO_ALERT, looks.ALERT)]
        missed = [(ratio, code, looks.judged(bad, ratio, over)) for ratio, code in wanted
                  if looks.judged(bad, ratio, over) != code]
        missed += [(name, looks.NOMINAL, got) for name, got in (
            ("no sense", looks.judged(flat, looks.RATIO_ALERT * 2, over)),
            ("few seasons", looks.judged(bad, looks.RATIO_ALERT * 2, over - 1)),
            ("no median", looks.judged(bad, None, over))) if got != looks.NOMINAL]
        for measure, bounds in looks.SHARES.items():
            watch, alert = bounds["watch"], bounds["alert"]
            edge = [(watch, looks.NOMINAL), (watch + step, looks.WATCH)] if bounds["past"] else \
                [(watch - step, looks.NOMINAL), (watch, looks.WATCH)]
            for share, code in edge + [(alert - step, looks.WATCH), (alert, looks.ALERT), (None, looks.MUTED)]:
                if looks.shared(measure, share) != code:
                    missed.append((measure, share, code, looks.shared(measure, share)))
        if "stopped_tasks.share" not in looks.SHARES:
            missed.append(("stopped_tasks.share", "no thresholds", sorted(looks.SHARES)))
        said = (looks.ratio_said(1.46), looks.ratio_said(0.55), looks.ratio_said(None))
        if not missed and said == ("▲ ×1.46", "▼ ×0.55", ""):
            held("the table of the judgments", f"{bad}: good to {looks.RATIO_GOOD}, watch from {looks.RATIO_WATCH}, "
                 f"alert from {looks.RATIO_ALERT}, nominal under {over} seasons; shares "
                 f"{ {name: (one['watch'], one['alert']) for name, one in looks.SHARES.items()} }; said {said[:2]}")
        else:
            failures.append(f"  ✗ judgments                   {missed!r} said={said!r}")

    # --- the plate, without styles: each judged cell says its glyph and its ratio, the figures aligned right --------
    P.forget(post.made)
    plate = post.render("--render", "looks", "--size", "120x48")
    rows = plate.stdout.split("\n")
    head = next((at for at, row in enumerate(rows) if re.match(r"^\s*row\s+figure", row)), len(rows))
    block = rows[head + 1:]
    block = block[:next((at for at, row in enumerate(block) if not row.strip()), len(block))]
    table = [row for row in block if re.match(r"^\s*(row \d|all|median)\s", row)]
    judged = [row for row in rows if re.match(r"^\s*row \d\s", row)]
    figures = {_end(row, r"(?:row \d|all|median)\s+\d+\.\d\d") for row in table}
    ratios = {_end(row, RATIO) for row in judged}
    codes = [row for row in rows if re.match(r"^\s*(good|nominal|watch|alert)\s+[▲▼=] ×", row)]
    marks = {found.group(1): found.group(2) for found in
             (re.match(r"^\s*(nominal|watch|alert)\s+share \d+%\s*(!*)\s*$", row) for row in rows) if found}
    if (plate.returncode == 0 and len(judged) >= 4 and all(RATIO.search(row) for row in judged) and len(codes) == 4
            and len(table) >= 6 and len(figures) == 1 and None not in figures and len(ratios) == 1
            and None not in ratios and looks is not None
            and marks == {code: looks.mark_of(code) for code in (looks.NOMINAL, looks.WATCH, looks.ALERT)}):
        held("the plate says each judgment without colour", f"{len(codes)} codes and {len(judged)} judged rows each "
             f"with its glyph and ratio; figures end on column {figures}, ratios on {ratios}; shares marked {marks}")
    else:
        failures.append(f"  ✗ plate plain                 rc={plate.returncode} codes={codes!r} table={table!r} "
                        f"figures={figures} ratios={ratios} marks={marks} {plate.stderr[-300:]!r}")

    # --- the plate in the looks of a dark and a light theme, and of an ansi one --------------------------------------
    drawn = {}
    for theme in ("textual-dark", "textual-light", "ansi-dark"):
        P.keep_theme(post.made, theme)
        done = post.render("--render", "looks", "--size", "120x48", "--styles", keep=True)
        text = done.stdout
        look = lambda pattern: _row_look(text, pattern)
        drawn[theme] = {"rc": done.returncode, "theme": theme in P.ANSI.sub("", text).split("\n")[0],
                        **{code: look(rf"^\s*{code}\s+[▲▼=] ×") for code in ("good", "nominal", "watch", "alert")},
                        "header": look(r"^\s*row\s+figure"), "first": look(r"^\s*row 1\s"),
                        "second": look(r"^\s*row 2\s"), "fourth": look(r"^\s*row 4\s"),
                        "tile": look(r"42\.00 / 50"), "closing": look(r"^\s*all\s"), "page": look(r"^\s*looks · "),
                        "bar": look(r"^\s*bar\s"), "err": done.stderr[-300:]}
    shown = lambda one: {key: sorted(value) for key, value in one.items() if isinstance(value, frozenset)}
    themed = []
    for theme in ("textual-dark", "textual-light"):
        one = drawn[theme]
        grounds = [_grounds(one[key]) for key in ("header", "first", "second", "tile", "closing")]
        page = _grounds(one["page"])
        own = theme != "textual-dark" or (_grounds(one["tile"]) - page and _grounds(one["bar"]) - page)
        alert_ground = _grounds(one["fourth"]) - _grounds(one["second"]) - _grounds(one["first"])
        if (one["rc"] == 0 and one["theme"] and all(one[code] for code in ("good", "watch", "alert"))
                and len({one["good"], one["watch"], one["alert"]}) == 3 and page and own
                and grounds[4] == grounds[0]
                and len({grounds[0], grounds[1], grounds[2]}) == 3 and alert_ground and _bold(one["fourth"])):
            themed.append(theme)
        else:
            failures.append(f"  ✗ plate {theme:<20} rc={one['rc']} theme={one['theme']} {shown(one)} {one['err']!r}")
    dark, light, ansi = drawn["textual-dark"], drawn["textual-light"], drawn["ansi-dark"]
    if len(themed) == 2:
        if all(dark[code] != light[code] for code in ("good", "watch", "alert")):
            held("the plate in each theme's look", f"good {sorted(dark['good'])} / {sorted(light['good'])}; alert "
                 f"{sorted(dark['alert'])} / {sorted(light['alert'])}; closing rows on the header's ground "
                 f"{sorted(_grounds(dark['closing']))}; tile {sorted(_grounds(dark['tile']) - _grounds(dark['page']))} "
                 f"and bar {sorted(_grounds(dark['bar']) - _grounds(dark['page']))} off the page's ground in the dark")
        else:
            failures.append(f"  ✗ plate themes                {shown(dark)} / {shown(light)}")
    alert_ansi = [one for one in _grounds(ansi["fourth"]) if one.startswith("48;2;")]
    if ansi["rc"] == 0 and ansi["fourth"] and _bold(ansi["fourth"]) and not alert_ansi:
        held("the alert cell under an ansi theme", f"bold, no mixed ground: {sorted(ansi['fourth'])}")
    else:
        failures.append(f"  ✗ plate ansi                  rc={ansi['rc']} {sorted(ansi['fourth'])} {ansi['err']!r}")

    # --- a threshold is written once: the plate's ratios and the gauge's warning read from the table -----------------
    typed = []
    try:
        typed.append(f"palette.WARN_SHARE = {P.palette_constant('WARN_SHARE')!r}")
    except KeyError:
        pass
    for node in ast.parse(PLATE.read_text(encoding="utf-8")).body:
        if (isinstance(node, ast.Assign) and any(isinstance(one, ast.Name) and one.id == "RATIOS" for one in node.targets)
                and isinstance(node.value, ast.Tuple) and all(isinstance(one, ast.Constant) for one in node.value.elts)):
            typed.append(f"panes/looks.py RATIOS = {ast.unparse(node.value)}")
    if not typed:
        held("a threshold is written once", "the plate's ratios and palette.WARN_SHARE are no typed numbers")
    else:
        failures.append(f"  ✗ thresholds typed again      {typed!r}")
    return 0
