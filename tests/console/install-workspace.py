"""Scenario `install-workspace` -- 2 case(s), in the monolith's order:
- `install <workspace>` is the CLI's convenience: it appends `.pp` itself
- `-install <workspace> -base <name>` composes the instance on the named base (batch
  l-instance-adressee, 2026-09-26)
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from conductor import instance
from tests.harness import cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- `install <workspace>` is the CLI's convenience: it appends `.pp` itself -------
    village = Path(tempfile.mkdtemp())
    cli_rc = cli(bench.engine(), "-install", str(village / "workspace"), "wit").returncode
    if (cli_rc == 0 and instance.is_instance(village / "workspace" / ".pp")
            and (village / "workspace" / "CLAUDE.md").is_file()
            and not instance.is_instance(village / "workspace")):
        held("install <workspace> suffixes .pp", "the bare argument is not the instance dir")
    else:
        failures.append(f"  ✗ install suffix            rc={cli_rc} {list((village/'workspace').iterdir())}")

    # --- `-install <workspace> -base <name>` composes on the named base -------------------
    witness = bench.source_with("kit-witness")
    based = cli(witness, "-install", str(village / "based"), "-base", "kit-witness")
    manifest = instance.read(village / "based" / ".pp") if based.returncode == 0 else {}
    if (based.returncode == 0 and manifest.get("base") == "kit-witness"
            and list(manifest.get("packages") or {}) == ["kit-witness"]):
        held("-base names the base", "`-install <ws> -base kit-witness`: `base:` at the manifest, "
             "the composition is the witness alone")
    else:
        failures.append(f"  ✗ -base                     rc={based.returncode} {based.stderr[:120]!r} {manifest}")
    return 0
