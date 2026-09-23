"""Scenario `install-workspace` -- 1 case(s), in the monolith's order:
- `install <workspace>` is the CLI's convenience: it appends `.pp` itself
"""
from __future__ import annotations

import contextlib
import io
import tempfile
from pathlib import Path
from conductor import instance
import pp as pp_cli


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- `install <workspace>` is the CLI's convenience: it appends `.pp` itself -------
    village = Path(tempfile.mkdtemp())
    with contextlib.redirect_stdout(io.StringIO()):
        cli_rc = pp_cli.main(["-install", str(village / "workspace"), "daneel"])
    if (cli_rc == 0 and instance.is_instance(village / "workspace" / ".pp")
            and (village / "workspace" / "CLAUDE.md").is_file()
            and not instance.is_instance(village / "workspace")):
        held("install <workspace> suffixes .pp", "the bare argument is not the instance dir")
    else:
        failures.append(f"  ✗ install suffix            rc={cli_rc} {list((village/'workspace').iterdir())}")
    return 0
