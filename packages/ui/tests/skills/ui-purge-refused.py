"""Scenario `ui-purge-refused` -- the purge refused by the verb (plan ui, batch le-poids-et-la-purge), on the bench's
`pp-chat` witness:
- a run a conversation holds (`run-busy`) and a run a team keeps (`run-held`): refused at the purge without `--yes`,
  said on the remedy line as the verb said it -- with `x closes its tab` when a tab of the dialogue holds the run --,
  no `--yes` played
- a clone with commits the repository has not received (`workdir-unpushed`): refused at `--yes`, then the purge
  shown again without `--yes`, `--force` offered, the key typed again, `--yes --force` played
"""
from __future__ import annotations

import copy

from tests.harness import support

P = support(__file__, "dialogue")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = copy.deepcopy(P.SCRIPT)
    purge = script["faces"]["purge"]
    purge["ag1"]["busy"] = ["w00009"]
    purge["ag1"]["unpushed"] = ["w00001"]
    purge["ag2"] = {"runs": {"w00002": {"key": "w00002", "lines": {"responses.jsonl": 1}, "files": [], "bytes": 0,
                                        "workdir": None, "flow": None}},
                    "held": {"w00002": "team core-review keeps run w00002 of ag2 -- stop the team first"}}
    post = P.Post(bench, "ui-purge-refused", script)

    def purges() -> list[str]:
        return [one for one in post.journal_lines() if one.startswith("purge ")]

    def remedy(text: str) -> str:
        return text.rstrip("\n").split("\n")[-2]

    # --- run-busy, a tab holding the run; run-held -----------------------------------------------------
    post.clear_journal()
    busy = post.render("ag1", "--run", "w00009", "--render", "dialogue", "--size", "160x40", "--press",
                       "escape,2,enter,down,P", "--wait", "none:1")   # escape: the open tab's line lets the letters act
    busy_said = purges()
    post.clear_journal()
    kept = post.render("--render", "dialogue", "--size", "160x40", "--press", "2,down,enter,P", "--wait", "none:1")
    if (busy.returncode == 0 and "run-busy" in remedy(busy.stdout) and "x closes its tab" in remedy(busy.stdout)
            and busy_said == ["purge ag1 w00009 --json"] and kept.returncode == 0 and "run-held" in remedy(kept.stdout)
            and purges() == ["purge ag2 w00002 --json"]):
        held("a run busy or held is refused at once", f"{remedy(busy.stdout).strip()[:70]!r}; "
             f"{remedy(kept.stdout).strip()[:70]!r}; no --yes")
    else:
        failures.append(f"  ✗ busy, held                  {busy_said} {purges()} {remedy(busy.stdout)!r} {remedy(kept.stdout)!r}")

    # --- workdir-unpushed, then --force under a second typing ---------------------------------------
    key = ",".join("w00001")
    post.clear_journal()
    forced = post.render("--render", "dialogue", "--size", "160x40", "--press", f"2,enter,P,{key},enter,{key},enter",
                         "--wait", "none:1.5")
    if (forced.returncode == 0 and purges() == ["purge ag1 w00001 --json", "purge ag1 w00001 --yes --json",
                                                "purge ag1 w00001 --json", "purge ag1 w00001 --yes --force --json"]):
        held("workdir-unpushed offers --force", f"the journal says {purges()}")
    else:
        failures.append(f"  ✗ force                       {purges()} {forced.stdout[-1500:]!r} {forced.stderr[-300:]!r}")
    return 0
