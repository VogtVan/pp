"""Scenario `ui-purge-refused` -- the purges the verb refuses, on the bench's `pp-chat` witness replaying the faces
of `agent` where they refuse:
- a run a conversation holds (`run-busy`) and a run a team keeps (`run-held`): refused at the purge without `--yes`,
  their code on the remedy line, no `--yes` played; the overlay of the runs stays, its weight read
- a clone with commits the repository has not received (`workdir-unpushed`): refused at `--yes`, the purge shown
  again, the key typed again, `--yes --force` played
"""
from __future__ import annotations

import copy

from tests.harness import support

P = support(__file__, "dialogue")
KEY = ",".join("w00001")


def said(*words: str) -> str:
    """-> a command the witness journals, written word by word."""
    return " ".join(words)


def refusing_script() -> dict:
    """The faces where the verb refuses: ag1's w00009 held by a conversation, its w00001 a clone not pushed; ag2's
    w00002 kept by a team."""
    script = copy.deepcopy(P.SCRIPT)
    purge = script["faces"]["purge"]
    purge["ag1"]["busy"] = ["w00009"]
    purge["ag1"]["unpushed"] = ["w00001"]
    purge["ag2"] = {"runs": {"w00002": {"key": "w00002", "lines": {"responses.jsonl": 1}, "files": [], "bytes": 0,
                                        "workdir": None, "flow": None}},
                    "held": {"w00002": "team core-review keeps run w00002 of ag2 -- stop the team first"}}
    return script


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    post = P.Post(bench, "ui-purge-refused", refusing_script())
    render, remedy = post.render, P.remedy_of

    def purges() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("purge ")]

    def row_of(text: str, name: str) -> str:
        return next((line for line in text.split("\n") if f" {name} " in f" {line} "), "")

    post.clear_journal()
    busy = render("ag1", "--run", "w00009", "--render", "dialogue", "--size", "160x40", "--press",
                  "escape,2,enter,down,P", "--wait", "none:1")   # escape: the open tab's line lets the letters act
    weight = row_of(busy.stdout, "w00001")
    busy_said = purges()
    post.clear_journal()
    kept = render("--render", "dialogue", "--size", "160x40", "--press", "2,down,enter,P", "--wait", "none:1")
    if (busy.returncode == 0 and "run-busy" in remedy(busy.stdout) and "1.2 MB" in weight and busy_said == ["purge ag1 w00009 --json"]
            and kept.returncode == 0 and "run-held" in remedy(kept.stdout) and purges() == ["purge ag2 w00002 --json"]):
        held("a run busy or held is refused at once", f"run-busy, then run-held on the remedy line; the journal says "
             f"{busy_said} then {purges()}, no --yes; the overlay of the runs stays, w00001 at 1.2 MB")
    else:
        failures.append(f"  ✗ busy, held                  {busy_said} {purges()} {weight!r} {remedy(busy.stdout)!r} {remedy(kept.stdout)!r}")

    post.clear_journal()
    forced = render("--render", "dialogue", "--size", "160x40", "--press", f"2,enter,P,{KEY},enter,{KEY},enter",
                    "--wait", "none:1.5")
    if (forced.returncode == 0 and purges() == [said("purge", "ag1", "w00001", "--json"),
                                                said("purge", "ag1", "w00001", "--yes", "--json"),
                                                said("purge", "ag1", "w00001", "--json"),
                                                said("purge", "ag1", "w00001", "--yes", "--force", "--json")]):
        held("workdir-unpushed offers --force", f"the journal says {purges()}")
    else:
        failures.append(f"  ✗ force                       {purges()} {forced.stdout[-1500:]!r} {forced.stderr[-300:]!r}")
    return 0
