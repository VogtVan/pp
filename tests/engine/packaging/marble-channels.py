"""Scenario `marble-channels` -- 2 case(s), in the monolith's order:
- D1b un-texte-plusieurs-canaux: the ADN compiles, projects, never doubles
- D1c l-adn-se-prouve: the receipt, the hardened merge, the coverage
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, compiling, discovery
from tests.harness import load_script, PRODUCT_ENGINE, SOURCE, body_of, kept_document
from conductor import install as install_module


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    product_engine = PRODUCT_ENGINE
    # --- D1b un-texte-plusieurs-canaux: the ADN compiles, projects, never doubles ----
    dna_made = bench.env("dna").made
    dna_ws = dna_made.parent
    dna_system = (dna_made / ".sys" / "system.md").read_text(encoding="utf-8")
    dna_member = discovery.instance_member(dna_made / ".sys" / "engine" / "pp.py")

    def dna_c() -> Conductor:
        return Conductor(dna_member, discovery.siblings_around(dna_member),
                         dna_made / ".sys" / "engine" / "pp.py", "t")

    dna_boot = render(dna_c().start(dna_c().boot("BOOT.md")))
    canon_head = body_of(kept_document(SOURCE / "kit", "PP"))[:80]
    marble_head = body_of(kept_document(SOURCE / "kit", "MARBLE"))[:60]
    if (canon_head in dna_system
            and dna_system.index(marble_head) < dna_system.index(canon_head)
            and dna_boot.count(canon_head) == 1
            and "INFORMATION — pp" not in dna_boot):
        held("the ADN compiles and never doubles", "envelope then canon in ONE system.md; "
             "the boot carries it once as standing orders -- the card serve is gone")
    else:
        failures.append(f"  ✗ ADN compile                 canon-in-system={canon_head in dna_system} "
                        f"boot-count={dna_boot.count(canon_head)}")

    dna_adapters = install_module.product_root(product_engine) / "adapters"
    dna_claude = load_script(dna_adapters / "claude" / "wire.py")
    dna_claude.wire(dna_ws, dna_made)
    dna_card = dna_ws / ".claude" / "skills" / "pp" / "SKILL.md"
    dna_kit_pp = next((dna_made / ".sys" / "vendor").glob("kit@*/refs/PP.md"))
    pristine_ok = dna_card.read_text(encoding="utf-8") == dna_kit_pp.read_text(encoding="utf-8")
    def dna_amend(line: str) -> None:
        dna_kit_pp.write_text(dna_kit_pp.read_text(encoding="utf-8")
                              .replace("", f"\n{line}", 1),
                              encoding="utf-8")

    dna_amend("new law of the land")
    dna_claude.wire(dna_ws, dna_made)
    refreshed = "new law of the land" in dna_card.read_text(encoding="utf-8")
    dna_card.write_text(dna_card.read_text(encoding="utf-8") + "\nMY OWN NOTE\n",
                        encoding="utf-8")
    dna_amend("another law")
    dna_told = dna_claude.wire(dna_ws, dna_made)
    dna_candidate = dna_card.parent / (dna_card.name + ".candidate")
    edited_kept = ("MY OWN NOTE" in dna_card.read_text(encoding="utf-8")
                   and "another law" not in dna_card.read_text(encoding="utf-8")
                   and dna_candidate.is_file()
                   and "another law" in dna_candidate.read_text(encoding="utf-8")
                   and any("candidate" in one for one in dna_told))
    if pristine_ok and refreshed and edited_kept:
        held("a projection lives with provenance", "fresh copy byte-identical; a pristine "
             "card follows the new contract; an edited one is preserved -- the current "
             "projection lands beside it as a candidate, and the drift is said")
    else:
        failures.append(f"  ✗ projection lifecycle        {pristine_ok}/{refreshed}/"
                        f"{edited_kept}")

    # --- D1c l-adn-se-prouve: the receipt, the hardened merge, the coverage ----------
    import os as dna_os
    dna_os.environ["PP_MARBLE"] = "1"
    try:
        (dna_made / ".sys" / "system.md").rename(dna_made / ".sys" / "system.hidden")
        expect("marble-missing", lambda: dna_c().start(dna_c().boot("BOOT.md")))
    finally:
        (dna_made / ".sys" / "system.hidden").rename(dna_made / ".sys" / "system.md")
        del dna_os.environ["PP_MARBLE"]
    held("a lying receipt refuses", "PP_MARBLE declared with nothing compiled to "
         "carry -- the boot refuses rather than playing blind")

    dna_codex = load_script(dna_adapters / "codex" / "wire.py")
    dna_codex.wire(dna_ws, dna_made)
    dna_config = dna_ws / ".codex" / "config.toml"
    dna_config.write_text(dna_config.read_text(encoding="utf-8")
                          + '\n[model]\nprovider = "operator-custom"\n',
                          encoding="utf-8")
    dna_amend("third law")
    compiling.build_system(dna_made)
    merged_told = dna_codex.wire(dna_ws, dna_made)
    merged_text = dna_config.read_text(encoding="utf-8")
    merge_ok = ('provider = "operator-custom"' in merged_text
                and "third law" in merged_text
                and any("byte-preserved" in one for one in merged_told))
    import re as dna_re
    edited = dna_re.sub(r'developer_instructions = """\n', 'developer_instructions = """\nOPERATOR PREFACE\n',
                        merged_text, count=1)
    dna_config.write_text(edited, encoding="utf-8")
    dna_amend("fourth law")
    compiling.build_system(dna_made)
    edited_told = dna_codex.wire(dna_ws, dna_made)
    edited_ok = ("OPERATOR PREFACE" in dna_config.read_text(encoding="utf-8")
                 and "fourth law" not in dna_config.read_text(encoding="utf-8")
                 and (dna_config.parent / "config.toml.candidate").is_file()
                 and any("candidate" in one for one in edited_told))
    if merge_ok and edited_ok:
        held("the codex merge is hardened", "a pristine managed field follows the new "
             "contract with every foreign key byte-preserved; an edited one is never "
             "touched -- the fresh projection lands as candidate")
    else:
        failures.append(f"  ✗ codex merge                 {merge_ok}/{edited_ok} "
                        f"{merged_told!r}")

    doc_told = install_module.doctor(dna_member)
    doc_ok = ("MY OWN NOTE" in dna_card.read_text(encoding="utf-8")
              and any("candidate" in one or "refreshed" in one for one in doc_told))
    if doc_ok:
        held("doctor refreshes the projections", "the repair pass replays every wired "
             "adapter -- pristine surfaces follow, edited ones stay and are diagnosed")
    else:
        failures.append(f"  ✗ doctor refresh              {doc_told!r}")

    dna_canon = (install_module.product_root(product_engine)
                 / "kit" / "refs" / "PP.md").read_text(encoding="utf-8")
    dna_anchors = ["-new", "<key>", "@<n>", "-peek", "keyless",
                   "=> ephemeral", "=> chat", "tool (heredoc)", "{i-j/m}", "[n]",
                   "routed", "REPAIR", "#BLOCKED", "address-ambiguous",
                   "run-unknown", "OPTIONS", "CONSTRAINTS", "GRAMMAR"]
    missing_anchors = [one for one in dna_anchors if one not in dna_canon]
    if not missing_anchors:
        held("the coverage map holds", "every agent-visible construction of the map "
             "has its teaching in the canonical card -- one anchor per row")
    else:
        failures.append(f"  ✗ ADN coverage                missing {missing_anchors}")
    return 0
