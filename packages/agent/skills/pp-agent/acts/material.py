"""The material of a run: one clone inside the agent's home, placed before the harness and pushed after it."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from model.material import Push, Workdir
from model.refusal import WorkFailure
from model.words import WORKDIRS, HOUSE, HOUSE_BRANCH
from store.clock import now
from store.houses import agent_at
from store.locks import under_repo_lock
from store.records import record, append

WORK = "work"                   # under an agent's directory: one clone per run, `work/<key>`


def branch_of(name: str, key: str) -> str:
    """-> the branch of a run's material: `agent/<path>/<key>`, the house's `agent/_house/<key>`."""
    return f"agent/{HOUSE_BRANCH if name == HOUSE else name}/{key}"


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """One git command, captured, no input: the clone and the repository are always named by absolute paths."""
    return subprocess.run(["git", *args], stdin=subprocess.DEVNULL, capture_output=True, text=True,
                          cwd=str(cwd) if cwd else None)


def base_of(repo: Path, asked: str | None) -> tuple[str, str]:
    """-> (ref, short sha) of what the run's branch is cut from: the repository's current
    branch, or the ref asked by `--base`; a ref that is no commit refuses `work-clone-failed`."""
    ref = asked
    if ref is None:
        current = git("symbolic-ref", "--short", "-q", "HEAD", cwd=repo)
        ref = current.stdout.strip() or "HEAD"
    found = git("rev-parse", "--short", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=repo)
    if found.returncode != 0 or not found.stdout.strip():
        raise WorkFailure(f"work-clone-failed -- `{ref}` is no commit of {repo}: "
                          f"{found.stderr.strip()[-200:] or 'not a git repository'}")
    return ref, found.stdout.strip()


def planned(name: str, key: str, repo: Path, asked: str | None) -> Workdir:
    """-> the material a dry run would place: nothing cloned, the repository read for its base -- the four keys
    it names, no line of `workdirs.jsonl`."""
    try:
        ref, sha = base_of(repo, asked)
    except WorkFailure:
        ref, sha = asked or "HEAD", "?"
    return Workdir(repo=str(repo), path=f"{WORK}/{key}", branch=branch_of(name, key), base=f"{ref}@{sha}",
                   keys=("repo", "path", "branch", "base"))


def placed(conductor, root: Path, name: str, meta: Path, key: str, repo: Path, asked: str | None) -> Workdir:
    """The clone of the run: under the repository's lock, `git clone --no-checkout` to
    `<path>/work/<key>` (hard links on one file system), the branch
    `branch_of` names cut from the base; a `.gitignore` under `work/` once. A git that
    fails refuses `work-clone-failed`, the half clone removed. -> the `open` line written."""
    home = meta.parent / WORK
    clone = home / key
    with under_repo_lock(conductor, root, repo):
        ref, sha = base_of(repo, asked)
        home.mkdir(parents=True, exist_ok=True)
        ignore = home / ".gitignore"
        if not ignore.exists():
            ignore.write_text("*\n", encoding="utf-8")
        cloned = git("clone", "-q", "--no-checkout", str(repo), str(clone))
        if cloned.returncode != 0:
            shutil.rmtree(clone, ignore_errors=True)
            raise WorkFailure(f"work-clone-failed -- git clone of {repo}: {cloned.stderr.strip()[-300:]}")
        local = git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=clone)
        start = ref if local.returncode == 0 else f"origin/{ref}"
        branch = branch_of(name, key)
        switched = git("switch", "-q", "-c", branch, start, cwd=clone)
        if switched.returncode != 0:
            shutil.rmtree(clone, ignore_errors=True)
            raise WorkFailure(f"work-clone-failed -- git switch -c {branch} {start}: "
                              f"{switched.stderr.strip()[-300:]}")
    entry = Workdir(at=now(), agent=name, run=key, repo=str(repo), path=f"{WORK}/{key}",
                    branch=branch_of(name, key), base=f"{ref}@{sha}", state="open")
    append(record(root, WORKDIRS), entry.json())
    return entry


def shipped(conductor, root: Path, name: str, entry: Workdir) -> Push:
    """The push after the harness, under the repository's lock: the branch to the repository
    by its absolute path; `commits` ahead of the base, `dirty` when the clone has unstaged
    changes. A push that fails is recorded (`pushed: false`, its `reason`) -- the response
    is the harness's, the branch stays in the clone. -> the push, its line written."""
    clone = agent_at(root, name).parent / entry.path
    repo = Path(entry.repo)
    base_sha = str(entry.base).rsplit("@", 1)[-1]
    counted = git("rev-list", "--count", f"{base_sha}..HEAD", cwd=clone)
    commits = int(counted.stdout.strip()) if counted.returncode == 0 and counted.stdout.strip().isdigit() else None
    dirty = bool(git("status", "--porcelain", cwd=clone).stdout.strip())
    reason = None
    try:
        with under_repo_lock(conductor, root, repo):
            pushed = git("push", "-q", str(repo), entry.branch, cwd=clone)
        if pushed.returncode != 0:
            reason = pushed.stderr.strip()[-300:] or f"git push rc {pushed.returncode}"
    except WorkFailure as failure:
        reason = str(failure)
    push = Push(branch=entry.branch, path=entry.path, pushed=reason is None, commits=commits, dirty=dirty,
                reason=reason)
    append(record(root, WORKDIRS), entry.sent(now(), push).json())
    return push


def unpushed(entry: Workdir, clone: Path) -> int:
    """-> the commits of a run's clone the repository has not received: 0 when the clone is gone."""
    if not clone.is_dir():
        return 0
    at_target = git("rev-parse", "--verify", "--quiet", entry.branch, cwd=Path(entry.repo))
    since = at_target.stdout.strip() if at_target.returncode == 0 else str(entry.base).rsplit("@", 1)[-1]
    counted = git("rev-list", "--count", f"{since}..HEAD", cwd=clone)
    return int(counted.stdout.strip()) if counted.returncode == 0 and counted.stdout.strip().isdigit() else 0
