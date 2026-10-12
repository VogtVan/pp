"""Scenario `slug` -- 2 case(s), in the monolith's order:
- the slug: kit's own -- defaults to the workspace's kebab, `-slug` overrides
- instance.slug(): reads the declared slug, or derives one -- never blank
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from conductor import instance
from tests.harness import cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- the slug: kit's own -- defaults to the workspace's kebab, `-slug` overrides ----
    hamlet_slug = Path(tempfile.mkdtemp())
    console = bench.engine()
    default_rc = cli(console, "-install", str(hamlet_slug / "My Workspace")).returncode
    default_slug = instance.read(hamlet_slug / "My Workspace" / ".pp").get("slug")
    given_rc = cli(console, "-install", str(hamlet_slug / "other"), "-slug", "sw7-hub-infra").returncode
    given_slug = instance.read(hamlet_slug / "other" / ".pp").get("slug")
    invalid = cli(console, "-install", str(hamlet_slug / "bad"), "-slug", "Not Kebab!")
    invalid_refused = invalid.returncode == 2 and "slug-invalid" in invalid.stderr
    if (default_rc == 0 and default_slug == "my-workspace"
            and given_rc == 0 and given_slug == "sw7-hub-infra"
            and invalid_refused and not (hamlet_slug / "bad").exists()):
        held("the slug defaults and overrides", "kebab of the workspace name, or `-slug`, never both silently")
    else:
        failures.append(f"  ✗ slug                      default={default_slug!r} given={given_slug!r} "
                         f"invalid_refused={invalid_refused}")

    # --- instance.slug(): reads the declared slug, or derives one -- never blank ---------
    undeclared = bench.env("Undeclared Dir").made          # an instance whose manifest says no slug
    manifest = instance.read(undeclared)
    manifest.pop("slug", None)
    instance.write(undeclared, manifest)
    if (instance.slug(hamlet_slug / "other" / ".pp") == "sw7-hub-infra"
            and instance.slug(undeclared) == "undeclared-dir"):
        held("instance.slug() reads or derives", "declared in instance.yaml, or kebab of the workspace")
    else:
        failures.append(f"  ✗ instance.slug()           {instance.slug(undeclared)!r}")
    return 0
