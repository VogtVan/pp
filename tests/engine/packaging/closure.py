"""Scenario `closure` -- what `remove` refuses, and where a source carries its base
(plan pp-split, batch la-resolution-des-dependances):
- remove refuses a name the instance does not pin
- a base lives under bases/: a source whose kit sits at the root is not the product
The closure, `add`, the requires topology, `package-required-by` and the closed reading are the
pattern `packaging/manifest`'s; the keys a removal leaves `unowned` `packaging/settings-fragment`'s;
the record a removal leaves `packaging/seed`'s; the base `remove` refuses `packaging/base`'s.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from conductor import install, instance

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.initialize, turn.begin, turn.end]\n")


def scenario(bench) -> int:
    expect = bench.expect
    env = bench.env("closed")
    kit_version = instance.pins(env.made)["kit"]

    # --- remove refuses a name nobody pinned ---------------------------------------------
    expect("package-unpinned", lambda: install.remove_package(env.member, "nowhere"))

    # --- a base lives under bases/, a package under packages/, nothing at the root --------
    # (batch les-bases-sous-un-toit): a source whose kit sits at the root is not the product
    rooted = Path(tempfile.mkdtemp()) / "rooted"
    (rooted / "kit").mkdir(parents=True)
    (rooted / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
    expect("package-unknown", lambda: install.package_dir(rooted, "kit"))
    return 0
