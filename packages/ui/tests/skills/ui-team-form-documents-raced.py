"""Scenario `ui-team-form-documents-raced` -- keys typed back to back in a hole of the document chosen while Preset holds
a field of the same name (s.1646, batch la-boucle-du-trou-tape; cut from `ui-team-form-documents-typed`, rule 10), on
the bench's `pp-team` witness (`_documents`), TEAM.md naming `teams/lead-reviewers`, which declares `folder` as
`review/read-files` does:
- `burst:` types `abcdef` in the hole `folder`, none settled before the next: the form settles, and both fields and
  `values:` end on the last value typed -- the field the form sets follows without a `Changed` of its own; a render
  bounded, its processes stopped past the bound, the form never settling
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys

from tests.harness import support

D = support(__file__, "documents")
F, T = D.F, D.T

FILES = "down,down,down,down"                  # notes/style, the separator, review/read-commits, review/read-files
BURST = "abcdef"                                # typed back to back in the hole `folder`
FOLDED = f"notes{BURST}"                        # the value both fields of `folder` end on
RACED = f"E,{D.TO_DOCUMENTS},{FILES},tab,end,burst:{':'.join(BURST)},{D.PAUSE},ctrl+pageup,ctrl+pageup,rest:1,boxes"
BOUND = 12.0                                    # seconds a render of the race may take: past them, it never settles


def bounded(house, *args: str) -> subprocess.CompletedProcess | None:
    """-> `ui <args>` as `house.render` plays it, its whole group of processes stopped past `BOUND` -- None then: the
    form never settled."""
    child = subprocess.Popen([sys.executable, str(house.engine), "ui", *args], cwd=house.ws, text=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={**os.environ, **house.env},
                             start_new_session=True)
    try:
        out, err = child.communicate(timeout=BOUND)
    except subprocess.TimeoutExpired:
        os.killpg(child.pid, signal.SIGKILL)
        child.communicate()
        subprocess.run(["pkill", "-KILL", "-f", f"{house.faces}/"], check=False)    # the watch it spawned, apart
        return None
    return D.P.rendered(subprocess.CompletedProcess(child.args, child.returncode, out, err))


def preset_folder() -> dict:
    """-> the script of `_documents` with TEAM.md naming `teams/lead-reviewers`, which declares `folder` too."""
    face = D.declaration()
    text = face["text"].replace('description: "reviews the PRs"\n', 'description: "reviews the PRs"\n'
                                                                     'template: teams/lead-reviewers\n')
    templates = [{**one, "values": [{"name": "folder", "description": "the folder read", "default": None}]}
                 if one["template"] == "teams/lead-reviewers" else one for one in D.TEMPLATES]
    return T.script(templates=templates, renders=D.RENDERS, sources=D.SOURCES,
                    declarations={**T.DECLARATIONS, "core-review": {**face, "text": text}})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-documents-raced", preset_folder())

    # --- s.1646: keys typed back to back in a hole whose name Preset holds: one value, the last typed ------------------
    raced = bounded(house, "--render", "teams", *D.SIZE, "--press", RACED)
    if raced is None:
        failures.append(f"  ✗ s.1646 typed back to back   the form never settled in {BOUND:.0f}s: the fields of `folder` "
                        f"echo each other")
        return 0
    rows, file = F.fields(raced.stdout), F.zone_rows(raced.stdout, "form-file")
    folders = [one for one in file if one.startswith("folder")]
    shown = [one for one in rows if one.startswith("notes")]
    if raced.returncode == 0 and folders == [f"folder = {FOLDED}"] and shown == [FOLDED]:
        held("s.1646: keys typed back to back in a hole, one value in both fields", f"{folders}; Preset {shown}")
    else:
        failures.append(f"  ✗ s.1646 typed back to back   rc={raced.returncode} {folders} {shown} {rows} "
                        f"{raced.stderr[-300:]!r}")
    return 0
