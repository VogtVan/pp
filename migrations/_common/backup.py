"""_common.backup -- the backup of a house, and the way back to it: the ONE place that writes it.

The whole house but its own `<house>/.git`, in one `tarfile` archive (`.tar.gz`) BESIDE the house
(never in it), written under a temporary name and renamed once complete. A `.git` deeper in the
house -- an agent's repository -- is kept in the archive, and the restoration gives it back."""
from __future__ import annotations

import shlex
import tarfile
from pathlib import Path

SUFFIX = ".tar.gz"          # the archive's suffix, beside the house
SKIPPED = ".git"            # what the archive leaves out: the house's own, at its root alone


def archive(root: Path, target: Path) -> int:
    """Writes the backup of the house `root` at `target`, its members under `<house name>/`.
    -> the archive's size in bytes."""
    partial = target.with_name(target.name + ".partial")

    own = f"{root.name}/{SKIPPED}"

    def kept(info: tarfile.TarInfo):
        return None if info.name == own else info      # its directory left out, nothing under it read

    try:
        with tarfile.open(partial, "w:gz") as tar:
            tar.add(root, arcname=root.name, filter=kept)
        partial.rename(target)
    finally:
        partial.unlink(missing_ok=True)
    return target.stat().st_size


def restore(root: Path, target: Path) -> str:
    """-> the commands that bring the house back to its backup -- said to the user, never played:
    the migrated house moved aside, the backup extracted in its place, the house's own `.git` put
    back from the house moved aside."""
    root, aside = shlex.quote(str(root)), shlex.quote(f"{root}.migrated")
    back = f"mv {root} {aside} && tar -xzf {shlex.quote(str(target))} -C {shlex.quote(str(Path(target).parent))}"
    return f"{back} && (test ! -d {aside}/{SKIPPED} || mv {aside}/{SKIPPED} {root}/)"
