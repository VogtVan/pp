"""Scenario `ui-theme` -- the theme of the post, chosen in a list (plan ui, batches les-retours-du-reel and
la-maison-et-ses-themes), on a throwaway house pinning `ui`:
- `t` opens the overlay of the themes Textual knows: the light ones first, the dark, `ansi-*` last, the
  current one marked
- `t`, `down`, `enter` keeps the theme after the current one: the post's memory says it in the space `ui` of
  the metadata, the footer says `[t] theme: <name>`; the next opening takes it without a key
- `t`, `down`, `escape` brings the theme of before back: the footer and the memory unchanged
- a line with nothing to open (a thought of a count alone) is drawn in the `STALE` look under `textual-dark` and
  `textual-light` alike: neither the dim of a line of conduction nor the look of a live line (`--styles`, batch
  les-glyphes-vivants)
"""
from __future__ import annotations

from conductor import metadata
from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-theme")

    def kept() -> str:
        return str(metadata.of_package(post.made, "ui").get("theme") or "")

    def footer(played) -> str:
        return P.keys_of(played.stdout)

    # --- t: the list of the themes, the current one marked ---------------------------------------------
    listed = post.render("--render", "frame", "--size", "120x40", "--press", "t")
    text = listed.stdout
    order = [name for name in ("textual-light", "atom-one-light", "textual-dark", "nord", "ansi-dark") if name in text]
    if (listed.returncode == 0 and "textual-dark  ●" in text and len(order) == 5
            and text.index("textual-light") < text.index("textual-dark") < text.index("nord") < text.index("ansi-dark")
            and "[enter] keeps" in text and "[esc] restores" in text):
        held("t lists the themes, the current one marked", "light first, then the dark, ansi last; textual-dark marked")
    else:
        failures.append(f"  ✗ list                        rc={listed.returncode} {order} {text!r} {listed.stderr[-300:]!r}")

    # --- t, down, enter keeps the next one; the next opening takes it ----------------------------------
    chose = post.render("--render", "frame", "--size", "120x30", "--press", "t,down,enter")
    remembered = kept()
    again = post.render("--render", "frame", "--size", "120x30", keep=True)
    if (chose.returncode == 0 and remembered == "nord" and "[t] theme: nord" in footer(chose)
            and again.returncode == 0 and "[t] theme: nord" in footer(again)):
        held("enter keeps the theme, the post remembers", "down from textual-dark: nord, kept in the memory, said in "
             "the footer; the next opening is nord without a key")
    else:
        failures.append(f"  ✗ keep                        {footer(chose)!r} kept={remembered!r} / {footer(again)!r} "
                        f"{chose.stderr[-300:]!r}")

    # --- t, down, escape brings the theme of before back ------------------------------------------------
    cancelled = post.render("--render", "frame", "--size", "120x30", "--press", "t,down,escape", keep=True)
    if cancelled.returncode == 0 and "[t] theme: nord" in footer(cancelled) and kept() == "nord":
        held("escape restores the theme of before", "the preview of the next one undone: nord in the footer and the memory")
    else:
        failures.append(f"  ✗ restore                     {footer(cancelled)!r} kept={kept()!r} {cancelled.stderr[-300:]!r}")

    # --- STALE is its own look in a dark and a light theme: neither dim nor a live line --------------------
    thought = P.Post(bench, "ui-theme-stale", P.thinking_script())
    looks = {}
    for theme in ("textual-dark", "textual-light"):
        P.keep_theme(thought.made, theme)
        shown = thought.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", "h,i,enter",
                               "--wait", "waiting", "--styles", keep=True)
        looks[theme] = (shown.returncode,
                        P.styles_of(shown.stdout, r"∴ \d\d:\d\d:\d\d · launch 1 · thinking ~42 tokens"),
                        P.styles_of(shown.stdout, r"◇ \d\d:\d\d:\d\d · launch 1 · "),
                        P.styles_of(shown.stdout, r"◀ \d\d:\d\d:\d\d · launch 1 · "), shown.stderr[-300:])
    if all(rc == 0 and stale and stale != dim and stale != alive
           for rc, stale, dim, alive, _ in looks.values()) and looks["textual-dark"][1] != looks["textual-light"][1]:
        held("STALE is its own look in both themes", "; ".join(
            f"{theme}: ∴ {sorted(one[1])} against ◇ dim {sorted(one[2])} and ◀ live {sorted(one[3])}"
            for theme, one in looks.items()))
    else:
        failures.append(f"  ✗ stale in both themes        {looks!r}")
    return 0
