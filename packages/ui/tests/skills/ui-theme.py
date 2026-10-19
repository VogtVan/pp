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
"""
from __future__ import annotations

import re

from conductor import metadata
from tests.harness import support

P = support(__file__, "dialogue")

RULE = r"^\s*─{60,}\s*$"


def _look(row: str) -> frozenset:
    """-> the styles (SGR sequences) one raw row of a `--styles` capture is drawn with."""
    return frozenset(P.SGR.findall(row)) - {"0", ""}


def _rules(lines: list[str]) -> list[int]:
    return [index for index, line in enumerate(lines) if re.match(RULE, line)]


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
        done = post.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", "i,h,i,enter",
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
    return 0
