"""What the verbs of an agent's life say: its birth, its import, the material of a run removed, the name of a
run, the runs purged, the agent taken out of the house."""
from __future__ import annotations


def born_line(path: str, meta: str, machine: str, capped: str, profiled: str | None) -> str:
    """-> what `add` says of a birth: the agent's path, the instance that borrows the house's `machine`, what
    was said of its cap (`capped`) and, under a type, of its profile (`profiled`)."""
    said = capped + (f"; {profiled}" if profiled is not None else "")
    return f"pp-agent: {path} born -- {meta} borrows the machine of {machine}; {said}"


def imported_lines(path: str, workspace: str, meta: str, machine: str, capped: str, told: list[str]) -> list[str]:
    """-> what `import` says: the agent's path and the `workspace` it comes from, the instance that borrows the
    house's `machine`, what was said of its cap; then one line per file of the workspace the engine `told` of."""
    return [f"pp-agent: {path} imported from {workspace} -- {meta} borrows the machine of {machine}; {capped}",
            *(f"pp-agent: {line}" for line in told)]


def pruned_line(name: str, key: str, path: str | None) -> str:
    """-> what `prune` says once a run's clone is removed: the agent, the run, the `path` of the clone."""
    return f"pp-agent: {name} · run {key} · {path} removed"


def named_line(name: str, key: str, named: str) -> str:
    """-> what `name` says of a run: the name it bears, or that it bears none."""
    return f"pp-agent: {name} · run {key} · " + (f"named {named}" if named else "(no name)")


def lock_left_line(name: str) -> str:
    """-> what `purge` says on stderr of a wake lock's file it could not remove."""
    return f"pp-agent: {name} left -- another process holds it open"


def purged_run(key: str, lines: dict, files: list[str], size: int, workdir: str | None, flow: int | None) -> dict:
    """-> one run as `purge --json` says it: its `lines` in each record, the `files` its agent keeps of it and
    their `bytes`, its clone when one stands (`workdir`), the bytes of its `flow` file, null without one."""
    return {"key": key, "lines": lines, "files": files, "bytes": size, "workdir": workdir, "flow": flow}


def purge_object(dry: bool, name: str, runs: list[dict]) -> dict:
    """-> a purge as `purge --json` says it: whether it is `dry`, the agent, its `runs`, then the lines, the
    files and the bytes summed."""
    totals = {"lines": sum(sum(one["lines"].values()) for one in runs),
              "files": sum(len(one["files"]) for one in runs), "bytes": sum(one["bytes"] for one in runs)}
    return {"dry": dry, "agent": name, "runs": runs, **totals}


def purge_lines(confirmed: bool, name: str, runs: list[dict]) -> list[str]:
    """-> a purge as `purge` says it, from its runs' objects: the sums, played or not, then one line per run --
    its lines by record, its files and their bytes, its material and its flow when it has them."""
    told = purge_object(not confirmed, name, runs)
    verb = "purged" if confirmed else "would purge"
    said = [f"pp-agent: {name} · {verb} {len(runs)} run(s) -- {told['lines']} line(s), {told['files']} file(s), "
            f"{told['bytes']} bytes"]
    for one in runs:
        counted = ", ".join(f"{record_name.removesuffix('.jsonl')} {n}" for record_name, n in one["lines"].items() if n)
        said.append(f"  run {one['key']} · lines {counted or 'none'} · {len(one['files'])} file(s), "
                    f"{one['bytes']} bytes"
                    + (f" · material {one['workdir']}" if one["workdir"] else "")
                    + (f" · flow {one['flow']} bytes" if one["flow"] is not None else ""))
    return said


def removal_object(dry: bool, name: str, runs: list[str], files: list[str], left: list[str],
                   directory: str | None = None) -> dict:
    """-> a removal as `remove --json` says it: whether it is `dry`, the agent, its `runs`, the `files` taken out
    of its directory (or that would be), what is `left` beside them, and once played whether the `directory` was
    removed or kept."""
    said = {"dry": dry, "agent": name, "runs": runs, "files": files, "left": left}
    return said if dry else {**said, "directory": directory}


def would_remove_line(name: str, runs: list[str], files: list[str], left: list[str]) -> str:
    """-> what `remove` says without `--yes`: the runs and the files it would remove, how to remove them, what
    would be left."""
    return (f"pp-agent: {name} · would remove {len(runs)} run(s)" + (f" ({', '.join(runs)})" if runs else "")
            + f", then {', '.join(files) or 'nothing'} -- `agent remove {name} --yes` removes it"
            + (f"; left: {', '.join(left)}" if left else ""))


def removed_lines(name: str, runs: list[str], removed: list[str], left: list[str], directory: str,
                  told: list[str]) -> list[str]:
    """-> what `remove --yes` says: the runs and the files removed, the directory with them when nothing else
    stood in it; what the engine `told` it left of a harness's wiring; the directory kept, and what stays in it."""
    said = [f"pp-agent: {name} · removed -- {len(runs)} run(s), {', '.join(removed) or 'nothing'}"
            + ("; the directory with them" if directory == "removed" else "")]
    said += [f"pp-agent: {line}" for line in told if line.startswith("left")]
    if directory == "kept":
        said.append(f"pp-agent: directory-kept -- {name}: {', '.join(left)} left; the directory stays")
    return said
