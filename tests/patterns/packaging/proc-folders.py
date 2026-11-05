"""Scenario `proc-folders` -- the pattern `packaging/proc-folders`, played from its demonstration:
- a proc shelved in a folder of `procs/` keeps the name of its file: it is in the catalog, resolves by
  that name, a CALL reaches it, its laws and its overlay's stand while it plays, the proc that offers it
  offers it once it returns
- a folder whose name starts with `_` is never read: its proc is in no catalog and resolves nowhere
- two files of one name anywhere in one `procs/` refuse `document-duplicate` at the build, both paths named
"""
from __future__ import annotations

from conductor import compiling, instance, persistence
from tests.harness import codes, demos

DRAWER, PATTERN = "packaging", "proc-folders"
DEMOS = ("HUB.md", "REVIEW.overlay.md", "_drafts/IDEA.md", "workflows/REVIEW.md")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    found = sorted(path.relative_to(demos(DRAWER, PATTERN)).as_posix()
                   for path in demos(DRAWER, PATTERN).rglob("*.md"))
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("proc-folders", bare=True)
    for name in ("HUB.md", "_drafts/IDEA.md", "workflows/REVIEW.md"):
        env.write(f"procs/{name}", (demos(DRAWER, PATTERN) / name).read_text(encoding="utf-8"))
    env.write("REVIEW.md", (demos(DRAWER, PATTERN) / "REVIEW.overlay.md").read_text(encoding="utf-8"))
    shelved = env.made / "procs" / "workflows" / "REVIEW.md"

    # --- the shelved proc is in the catalog and resolves by its name -----------------------------
    built = env.cli("-build")
    names = [name for name, _front, _path in compiling.entries(env.made)]
    if (built.returncode == 0 and "REVIEW" in names and "HUB" in names
            and instance.resolve(env.made, "REVIEW.md") == shelved
            and instance.overlays_of(env.made, "REVIEW.md") == [env.made / "REVIEW.md"]):
        held("a shelved proc keeps its name", "REVIEW, under procs/workflows/, is in the catalog and "
             "resolves by its name; the instance's REVIEW.md is its overlay")
    else:
        failures.append(f"  ✗ catalog and resolution      rc={built.returncode} {names} "
                        f"{instance.resolve(env.made, 'REVIEW.md')} {built.stderr[-300:]!r}")

    # --- a CALL reaches it, its laws and its overlay's stand, the offer holds ---------------------
    opener = env.conductor()
    opener.forget()
    entered = opener.start(env.made / "procs" / "HUB.md")
    key = persistence.run_id_of(env.session())
    back = env.conductor(key).forward("") if entered is not None else None
    if (entered is not None and entered.document == "REVIEW" and {"PF1", "PF2"} <= set(codes(entered))
            and back is not None and back.document == "HUB" and "PF1" not in codes(back)
            and "REVIEW" in [one.name for one in back.tools]):
        held("a CALL reaches the shelved proc", f"REVIEW plays under HUB with {codes(entered)}, its "
             "overlay's law among them; back at HUB its laws fall and HUB offers REVIEW")
    else:
        failures.append(f"  ✗ the call                    {entered and entered.document!r} {codes(entered)} "
                        f"{back and back.document!r} {back and [one.name for one in back.tools]!r}")
    env.conductor(key).forget()

    # --- the workshop is never read ---------------------------------------------------------------
    if "IDEA" not in names and not instance.chain(env.made, "IDEA.md"):
        held("a `_` folder is never read", "IDEA, under procs/_drafts/, is in no catalog and resolves nowhere")
    else:
        failures.append(f"  ✗ the workshop                {names} {instance.chain(env.made, 'IDEA.md')}")

    # --- two files of one name in one procs/ refuse at the build -----------------------------------
    twin = env.write("procs/other/REVIEW.md", shelved.read_text(encoding="utf-8"))
    refused = env.cli("-build")
    twin.unlink()
    if (refused.returncode != 0 and "document-duplicate" in refused.stderr
            and "workflows" in refused.stderr and "other" in refused.stderr):
        held("a name twice in one procs/ refuses", "document-duplicate at the build, both paths named")
    else:
        failures.append(f"  ✗ the duplicate               rc={refused.returncode} {refused.stderr[-300:]!r}")
    return 0
