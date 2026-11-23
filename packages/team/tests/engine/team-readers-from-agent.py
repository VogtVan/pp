"""Scenario `team-readers-from-agent` -- 2 case(s): a team's verbs called from an agent that borrows the house's
machine (`agents/m`, born by `agent add`), on a team `old` declared in the house with the journal team 0.32.2 wrote
(`T.OLD_JOURNAL`) -- nothing under the agent's own `teams/`.
- (a) the readers read the house: `log`, `log --last`, `result`, `responses`, `inbox` with the team's name and
  without a name, and `watch` say from the agent what they say from the house
- (b) the writers stay at the instance that calls (s.1613): `snapshot` and `inbox --seen` refuse `team-unknown`,
  `follow` `team-not-started`; the house's journal as it was
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    h.declare("old", T.OLD_DECLARED)
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(T.OLD_JOURNAL, encoding="utf-8")
    born = h.call("agent", "add", "agents/m")
    meta = h.meta_of("agents/m")

    def from_agent(*args: str):
        return T.cli(h.engine, "--instance", str(meta), "team", *args, cwd=meta.parent, env=h.env)

    # --- (a) the readers read the house ------------------------------------------------------------------------
    readers = {"log": ("log", "old", "--json"), "log --last": ("log", "old", "--last", "2"),
               "result": ("result", "old", "T1"), "responses": ("responses", "old", "--json"),
               "inbox": ("inbox", "old", "--json"), "inbox bare": ("inbox", "--json"),
               "watch": ("watch", "old", "--json", "--for", "1")}
    read = {key: (from_agent(*args), h.call("team", *args)) for key, args in readers.items()}
    missed = {key: (agent, own) for key, (agent, own) in read.items()
              if agent.returncode or own.returncode or agent.stdout != own.stdout
              or not (agent.stdout.strip() or key == "watch")}
    if born.returncode == 0 and h.agent_stands("agents/m") and not missed and not (meta.parent / "teams").exists():
        held("(a) the readers read the house", f"{', '.join(readers)} from agents/m say what the house says; nothing "
             "under the agent's teams/")
    else:
        failures.append(f"  ✗ (a) the readers             born={born.returncode} " + " ".join(
            f"{key}={agent.returncode}/{own.returncode}:{agent.stderr.strip()[-90:]!r}"
            for key, (agent, own) in missed.items()))

    # --- (b) the writers stay at the instance that calls -----------------------------------------------------
    journal = h.journal_of("old").read_bytes()
    writers = {"snapshot": (("snapshot", "old"), "team-unknown"), "inbox --seen": (("inbox", "old", "--seen"), "team-unknown"),
               "follow": (("follow", "old", "m-T1-f5b1b9"), "team-not-started")}
    wrote = {key: (from_agent(*args), code) for key, (args, code) in writers.items()}
    wrong = {key: played for key, (played, code) in wrote.items() if played.returncode != 2 or code not in played.stderr}
    if not wrong and h.journal_of("old").read_bytes() == journal:
        held("(b) the writers stay at the instance that calls", "from agents/m: snapshot and inbox --seen refuse "
             "team-unknown, follow team-not-started; the house's journal as it was")
    else:
        failures.append(f"  ✗ (b) the writers             " + " ".join(
            f"{key}={played.returncode}:{(played.stderr or played.stdout).strip()[-90:]!r}" for key, played in wrong.items())
            + f" journal={'same' if h.journal_of('old').read_bytes() == journal else 'written'}")
    return 0
