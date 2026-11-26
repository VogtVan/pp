"""Scenario `ui-line-keys` -- the keys of the message line (batch la-saisie-et-le-tour), on the bench's `pp-chat`
witness:
- the line keeps its keys: `hi` typed then `ctrl+a`, `ctrl+c` -- the status says `copied 2 chars`: the selection is the
  line's, not the transcript's; `ctrl+x` empties the line, `ctrl+v` fills it again, `ctrl+z` undoes the paste
- twelve `ctrl+z` on the empty line, then on a line typed, leave the post standing: exit 0, the footer drawn
- `ctrl+c` on a selection that runs past the lines of a task's result in markdown (on the `pp-team` witness: the
  task's detail selected whole, then the result from the row under its last) leaves the post standing (s.1313):
  exit 0, no `ui.crash` kept, the clipboard carries the detail's text alone and the status counts it
"""
from __future__ import annotations

import json

from conductor.state import metadata
from tests.harness import support

P = support(__file__, "dialogue")
T = support(__file__, "teams")
RESOLVED = "shift+tab,shift+tab,down,down,down,down,tab,tab,down"   # SHOW `resolved`, the cursor on ops' T2: its result
PAST = "select:#tasks-detail:-:-:-:-,select:#tasks-result-text:0:h:-:-"   # the detail whole, the result past its lines
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

    # --- ctrl+c on a selection past the lines of a markdown result leaves the post standing -----------------------
    house = T.Teams(bench, "ui-line-keys-result")
    copied = house.render("--render", "tasks", "--size", "150x40", "--press", f"{RESOLVED},{PAST},ctrl+c,clipboard")
    path = metadata.path_of(house.made)
    kept = json.loads(path.read_text(encoding="utf-8") or "{}") if path.is_file() else {}
    crash = str((kept.get("ui") or {}).get("crash") or "")
    noted = [line for line in copied.stdout.split("\n") if line.startswith("clipboard ")]
    clip = json.loads(noted[-1][len("clipboard "):]) if noted else None
    status = P.status_of(copied.stdout.split("\nclipboard ")[0])
    if (copied.returncode == 0 and not crash and clip and "Weekly" not in clip and "check" not in clip
            and clip.split("\n")[0][:20] in copied.stdout and f"copied {len(clip)} chars" in status):
        held("ctrl+c past a markdown result's lines stands", f"exit 0, no ui.crash; the clipboard {clip[:40]!r}, "
             f"the detail alone; the status {status.strip()[-30:]!r}")
    else:
        failures.append(f"  ✗ ctrl+c past the result      rc={copied.returncode} clip={clip!r} crash={crash[-300:]!r} "
                        f"{status!r} {copied.stderr[-300:]!r}")
    return 0
