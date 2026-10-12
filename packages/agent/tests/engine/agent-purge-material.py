"""Scenario `agent-purge-material` -- 2 case(s) (batch la-purge-agent, 2026-10-11): `agent purge` and the material of
a run (its clone under `<path>/work/<key>`), the rule of `prune`.
- a clone with a commit the repository has not received: `purge --yes` refuses `workdir-unpushed`, and nothing is
  removed -- neither the clone, nor a line of the records, nor a file of the agent's state
- `--force` removes it: the clone gone, the run's lines gone, its files at the agent gone
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from conductor import persistence
from tests.harness import support

A = support(__file__, "agent")
RECORDS = ("responses.jsonl", "messages.jsonl", "sessions.jsonl", "names.jsonl", "workdirs.jsonl")


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                          env={"GIT_AUTHOR_NAME": "bench", "GIT_AUTHOR_EMAIL": "bench@bench",
                               "GIT_COMMITTER_NAME": "bench", "GIT_COMMITTER_EMAIL": "bench@bench",
                               "HOME": str(cwd), "PATH": "/usr/bin:/bin:/usr/local/bin"})


def files_under(root: Path) -> dict[str, bytes]:
    return {str(path.relative_to(root)): path.read_bytes() for path in sorted(root.rglob("*")) if path.is_file()} \
        if root.is_dir() else {}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    state = h.agent_meta / persistence.DIRECTORY
    target = bench.temp() / "target"
    target.mkdir()
    git("init", "-q", "-b", "main", cwd=target)
    (target / "README").write_text("target\n", encoding="utf-8")
    git("add", "README", cwd=target)
    git("commit", "-q", "-m", "first", cwd=target)

    worked = h.wake("work on it", "play", "--work", str(target))
    key = (h.keys() or [""])[0]
    clone = h.agent_ws / "work" / key
    git("commit", "-q", "--allow-empty", "-m", "not sent", cwd=clone)   # a commit the repository never received

    def lines_of() -> int:
        return sum(1 for name in RECORDS for one in A.lines(h.records / name)
                   if one.get("run") == key and (one.get("agent") == "agents/ag1" or one.get("to") == "agents/ag1"))

    # --- a clone with unsent commits refuses, nothing removed ------------------------------------------------
    records_before, state_before, kept = files_under(h.records), files_under(state), lines_of()
    refused = h.call("agent", "purge", "agents/ag1", key, "--yes")
    if (worked.returncode == 0 and clone.is_dir() and refused.returncode == 2 and "workdir-unpushed" in refused.stderr
            and files_under(h.records) == records_before and files_under(state) == state_before and kept):
        bench.refusals += 1
        held("a clone with unsent commits refuses", f"run {key}: workdir-unpushed, the clone, {kept} line(s) and the "
             "agent's state untouched")
    else:
        failures.append(f"  ✗ unpushed                    rc={worked.returncode}/{refused.returncode} clone={clone.is_dir()} "
                        f"{refused.stderr[-300:]!r} {worked.stderr[-300:]!r}")

    # --- --force removes it ------------------------------------------------------------------------------------
    forced = h.call("agent", "purge", "agents/ag1", key, "--yes", "--force")
    left = [name for name in files_under(state) if key in name]
    if (forced.returncode == 0 and not clone.exists() and lines_of() == 0 and not left
            and f"material work/{key}" in forced.stdout):
        held("--force removes the clone with the run", f"run {key}: the clone, the lines and the agent's files gone")
    else:
        failures.append(f"  ✗ forced                      rc={forced.returncode} clone={clone.exists()} lines={lines_of()} "
                        f"left={left} {forced.stdout[-300:]!r} {forced.stderr[-300:]!r}")
    return 0
