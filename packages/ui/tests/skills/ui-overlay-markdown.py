"""Scenario `ui-overlay-markdown` -- what the agent wrote opens as markdown (plan ui, batch le-pied-et-les-overlays;
cut from `ui-overlay-kinds`, rule 10), on the bench's `pp-chat` witness:
- an answer of the agent opens as MARKDOWN: its table drawn, no `|---|` left; a conduction opens as the text pp served;
  the keys of the overlay say no `ctrl+c`
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
TURN = "h,i,enter,wait:waiting"


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

    # --- the agent's answer in markdown, a conduction in text, no ctrl+c among the keys ----------------------
    marked = P.Post(bench, "ui-overlays-markdown", P.markdown_script())
    answer = marked.render("ag1", "--render", "dialogue", "--size", "120x40", "--press", f"{TURN},shift+tab,enter")
    served = marked.render("ag1", "--render", "dialogue", "--size", "120x40", "--press",
                           f"{TURN},shift+tab,shift+tab,enter")
    title_a, title_c = title_of(answer.stdout), title_of(served.stdout)
    boxed = answer.stdout[answer.stdout.find("┏"):]
    body = "\n".join(row for row in boxed.split("\n") if not title_a or title_a[0][:30] not in row)   # the title says the start
    if (answer.returncode == 0 and title_a[:1] and title_a[0].startswith("agent answer") and "build" in body
            and "|---|" not in body and "| frame | done |" not in body and "┌" in body and "ctrl+c" not in boxed
            and "[esc] close" in boxed and served.returncode == 0 and title_c[:1] and title_c[0].startswith("conduction")
            and "▌ INSTRUCTION" in served.stdout and "WORK any => ephemeral" in served.stdout):
        held("an answer opens as markdown, a conduction as text", "the table drawn, no |---| nor ctrl+c in the "
             "overlay; the conduction's ▌ lines as served")
    else:
        failures.append(f"  ✗ markdown                    {title_a} {title_c} {boxed[:1500]!r} {answer.stderr[-300:]!r}")
    return 0
