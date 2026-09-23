"""Scenario `user-tier` -- 1 case(s), in the monolith's order:
- le-tier-user: a package's user files -- one bearer, backed-up replacement
"""
from __future__ import annotations

import tempfile
from pathlib import Path
from tests.harness import PRODUCT_ENGINE
from conductor import install as install_module


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    product_engine = PRODUCT_ENGINE
    # --- le-tier-user: a package's user files -- one bearer, backed-up replacement ----
    persona_a = Path(tempfile.mkdtemp()) / "a"
    (persona_a / "user").mkdir(parents=True)
    (persona_a / "user" / "MEMBER.md").write_text("Persona A's member\n", encoding="utf-8")
    persona_b = Path(tempfile.mkdtemp()) / "b"
    (persona_b / "user").mkdir(parents=True)
    (persona_b / "user" / "MEMBER.md").write_text("Persona B's member\n", encoding="utf-8")
    expect("user-packages-conflict",
           lambda: install_module._single_user_bearer([("a", persona_a), ("b", persona_b)]))

    user_made = bench.env("userws").made
    member_doc = user_made / "MEMBER.md"
    src_root = install_module.product_root(product_engine)
    saved0 = install_module._place_user(user_made, persona_a, src_root, backup=True)
    pristine_ok = (member_doc.read_text(encoding="utf-8") == "Persona A's member\n"
                   and not saved0 and not (user_made / "MEMBER.md.old").exists())
    saved1 = install_module._place_user(user_made, persona_a, src_root, backup=True)
    idem_ok = not saved1 and not (user_made / "MEMBER.md.old").exists()
    member_doc.write_text("the operator's own words\n", encoding="utf-8")
    saved2 = install_module._place_user(user_made, persona_b, src_root, backup=True)
    edited_ok = (saved2 == ["MEMBER.md"]
                 and member_doc.read_text(encoding="utf-8") == "Persona B's member\n"
                 and (user_made / "MEMBER.md.old").read_text(encoding="utf-8")
                 == "the operator's own words\n")
    if pristine_ok and idem_ok and edited_ok:
        held("user files replace with a net", "a template seed or an identical copy "
             "swaps silently; the operator's own words survive as .old")
    else:
        failures.append(f"  ✗ user placement              {pristine_ok}/{idem_ok}/{edited_ok}")
    return 0
