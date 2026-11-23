"""What the readings list: the agents of a house, the providers it is wired with, the materials of the runs."""
from __future__ import annotations

from model.material import Workdir

NO_MATERIAL = "pp-agent: no material yet."


def no_agent(workspace: str) -> str:
    """-> what `list` says of a house without an agent: the `workspace` it looked under, how one is created."""
    return f"pp-agent: no agent under {workspace} yet -- `./pp agent add <path>` creates one."


def agent_line(name: str, runs: int, running: int, responses: int) -> str:
    """-> one agent as `list` says it: its path, its runs, those a wake-up plays, its responses."""
    return f"{name} · {runs} run(s) · {running} running · {responses} response(s)"


def agent_object(name: str, runs: int, running: int, responses: int, weight: dict) -> dict:
    """-> one agent as `list --json` says it: the same, and the `weight` of its runs summed."""
    return {"agent": name, "runs": runs, "running": running, "responses": responses, "weight": weight}


def provider_line(provider: str, spells: list[str], models: list[str], cost: str | None) -> str:
    """-> one provider as `providers` says it: what its adapter spells of a policy, the models it names, the
    scope of the cost it reads -- a dash for what it declares none of."""
    return (f"{provider} · spells {', '.join(spells) or '—'} · models {', '.join(models) or '—'} "
            f"· cost {cost or '—'}")


def provider_object(provider: str, spells: list[str], models: list[str], cost: str | None) -> dict:
    """-> one provider as `providers --json` says it: `{provider, spells, models, cost}`."""
    return {"provider": provider, "spells": spells, "models": models, "cost": cost}


def material_line(agent: str, key: str, one: Workdir, ahead: str | None, dirty: bool | None, state: str | None) -> str:
    """-> one material as `workdirs` says it: the agent, the run, the branch, the repository, the commits `ahead`
    of the base (None when the clone cannot count them), clean or `dirty` (None when the clone is gone), pushed
    or not, the run's `state`; a material pruned says so, and nothing after it."""
    if one.state == "pruned":
        return f"{agent} · run {key} · {one.branch} · {one.repo} · pruned"
    tidy = "clone gone" if dirty is None else ("dirty" if dirty else "clean")
    sent = "pushed" if one.pushed else ("unpushed" if one.state == "unpushed" else "not pushed yet")
    return (f"{agent} · run {key} · {one.branch} · {one.repo} · {ahead if ahead is not None else '?'} ahead "
            f"· {tidy} · {sent} · {state}")
