"""Scenario `ui-line-keys` -- the keys of the message line (batch la-saisie-et-le-tour), on the bench's `pp-chat`
witness:
- the line keeps its keys: `hi` typed then `ctrl+a`, `ctrl+c` -- the status says `copied 2 chars`: the selection is the
  line's, not the transcript's; `ctrl+x` empties the line, `ctrl+v` fills it again, `ctrl+z` undoes the paste
- twelve `ctrl+z` on the empty line, then on a line typed, leave the post standing: exit 0, the footer drawn
"""
from __future__ import annotations

from tests.harness import support

P = support(__file__, "dialogue")
WIDE = ("--size", "160x40")            # the status row keeps its note


def line_text(text: str) -> str:
    """-> the text inside the message line's box: its rows between the last `┌` and `└`, their borders taken off."""
    lines = text.rstrip("\n").split("\n")
    bottom = max((n for n, line in enumerate(lines) if "└───" in line), default=-1)
    top = max((n for n, line in enumerate(lines[:bottom]) if "┌───" in line), default=-1)
    if not 0 <= top < bottom:
        return ""
    left = lines[top].index("┌")
    right = lines[top].index("┐", left)
    return "\n".join(line[left + 1:right].strip() for line in lines[top + 1:bottom]).strip()


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-line-keys")
    render = post.render

    # --- the line keeps its keys: ctrl+a and ctrl+c act on its text; ctrl+x, ctrl+v, ctrl+z too -------------
    copied = render("ag1", "--render", "dialogue", *WIDE, "--press", "i,h,i,ctrl+a,ctrl+c")
    status = P.status_of(copied.stdout)
    if copied.returncode == 0 and "copied 2 chars" in status and line_text(copied.stdout) == "hi":
        held("ctrl+a and ctrl+c act on the line", f"hi typed: {status.strip()[-60:]!r}, the line keeps hi")
    else:
        failures.append(f"  ✗ ctrl+a, ctrl+c              rc={copied.returncode} {status!r} line={line_text(copied.stdout)!r} "
                        f"{copied.stderr[-300:]!r}")
    cut = render("ag1", "--render", "dialogue", *WIDE, "--press", "i,h,i,ctrl+a,ctrl+x")
    pasted = render("ag1", "--render", "dialogue", *WIDE, "--press", "i,h,i,ctrl+a,ctrl+x,ctrl+v")
    undone = render("ag1", "--render", "dialogue", *WIDE, "--press", "i,h,i,ctrl+a,ctrl+x,ctrl+v,ctrl+z")
    texts = ["hi" in line_text(one.stdout) for one in (cut, pasted, undone)]   # the empty line shows its placeholder
    if all(one.returncode == 0 for one in (cut, pasted, undone)) and texts == [False, True, False]:
        held("ctrl+x, ctrl+v, ctrl+z act on the line", f"hi in the line after cut, paste, undo: {texts}")
    else:
        failures.append(f"  ✗ ctrl+x, ctrl+v, ctrl+z      {texts} {cut.stderr[-200:]!r} {undone.stderr[-200:]!r}")

    # --- twelve ctrl+z leave the post standing ----------------------------------------------------------------
    twelve = ",".join(["ctrl+z"] * 12)
    empty = render("ag1", "--render", "dialogue", *WIDE, "--press", f"i,{twelve}")
    typed_z = render("ag1", "--render", "dialogue", *WIDE, "--press", f"i,h,i,{twelve}")
    if (empty.returncode == 0 and typed_z.returncode == 0 and P.keys_of(empty.stdout) and P.keys_of(typed_z.stdout)
            and "Traceback" not in empty.stderr + typed_z.stderr):
        held("twelve ctrl+z leave the post standing", "on the empty line and after hi: exit 0, the footer drawn")
    else:
        failures.append(f"  ✗ ctrl+z twelve times         rc={empty.returncode}/{typed_z.returncode} "
                        f"{empty.stderr[-300:]!r} {typed_z.stderr[-300:]!r}")
    return 0
