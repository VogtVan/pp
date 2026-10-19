"""Scenario `base-and-user` -- the base an instance installs on, and the user layer it places.
- the named base: `install(..., base=<name>)` composes on it -- `base:` at the manifest,
  `base_of` answers it, the vendor carries it and not the kit, the marble compiles its
  precision, a run boots on its BOOT.md; it is never removed (`package-base`); an install that
  names no base writes no `base:`; a base without `procs/TURN.md` refuses `base-incomplete`, a
  base without `system/` refuses `base-silent`, nothing written; its sockets are their own
  address and its settings keys are bare
- the user layer: one bearer among the packages (`user-packages-conflict`), the base's own
  layer no rival; a placement replaces with a net -- the operator's own words survive as
  `.old`; a base without `user/` installs no member
(that a member still equal to the kit's seeded file is pristine and swaps silently is the
kit's: `bases/kit/tests/engine/seeded-member.py`)
"""
from __future__ import annotations

import shutil
from pathlib import Path

from conductor import Conductor, discovery, install, instance, render
from conductor.state import settings as tuning
from tests.harness import INSTANCE, PRODUCT_ENGINE, SOURCE, body_of

BASE = "kit-witness"
MUTE = "kit-mute"          # the same copy of the kit, its user/ layer and its CALL MEMBER.md removed
FRAGMENT = """---
name: SETTINGS
kind: fragment
package: kit-witness
description: the witness base's own settings -- one bare key, as a base declares them
witness_word: hello
types: |
  witness_word  free
---
"""
GREETED = "Witness greeting holds at the boot."
GREETING = f"""---
name: HELLO
kind: doc
description: a document of the instance mounted at the base's boot socket
mount: boot.ready
---
{GREETED}
"""
PERSONA_A = "Persona A's member\n"
PERSONA_B = "Persona B's member\n"
OWN_WORDS = "the operator's own words\n"
BASE_MEMBER = "The base's member\n"


def named_base(bench, plain) -> None:
    """Install on a named base: it composes, it stays, its refusals write nothing, its names are bare."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    engine = bench.source_with(BASE)
    witness = engine.parent.parent / "bases" / BASE
    (witness / "settings").mkdir(exist_ok=True)
    (witness / "settings" / "SETTINGS.md").write_text(FRAGMENT, encoding="utf-8")

    # --- the named base composes ----------------------------------------------------------
    ws = bench.temp() / "ws"
    made = install.install(engine, ws / INSTANCE, [], base=BASE)
    declared = instance.read(made)
    vendored = [root.name for root in instance.vendored(made)]
    precision = body_of(witness / "system" / "SYSTEM.COMMON.md")[:60]
    orders = body_of(SOURCE / "engine" / "system" / "SYSTEM.COMMON.md")[:60]
    marble = (made / ".sys" / "system.md").read_text(encoding="utf-8")
    vendored_engine = made / ".sys" / "engine" / "pp.py"
    member = discovery.instance_member(vendored_engine)
    (made / "procs" / "HELLO.md").write_text(GREETING, encoding="utf-8")
    conductor = Conductor(member, vendored_engine, "t")
    block = conductor.start(conductor.boot("BOOT.md"))
    booted = render(block) if block else ""
    if (declared.get("base") == BASE and instance.base_of(made) == BASE
            and vendored and all(one.startswith(f"{BASE}@") for one in vendored)
            and precision in marble and orders in marble
            and marble.index(orders) < marble.index(precision)
            and block is not None and block.next_call):
        held("the named base composes", f"`base: {BASE}` at the manifest, the vendor carries "
             f"{vendored[0]} alone, the marble compiles its precision after the orders, the run boots")
    else:
        failures.append(f"  ✗ named base                  {declared.get('base')!r} {vendored} "
                        f"precision={precision in marble} block={block is not None}")

    # --- never removed ---------------------------------------------------------------------
    expect("package-base", lambda: install.remove_package(member, BASE))

    # --- no base named, no `base:` written --------------------------------------------------
    if "base" not in instance.read(plain.made) and instance.base_of(plain.made) != BASE:
        held("no base named, no key written", "the manifest of an install without -base "
             "carries no `base:` -- yesterday's bytes, the role's default answers")
    else:
        failures.append(f"  ✗ plain manifest              {instance.read(plain.made)}")

    # --- an incomplete base refuses before anything is written -----------------------------
    turn = witness / "procs" / "TURN.md"
    aside = turn.with_name("TURN.aside")
    turn.rename(aside)
    ws2 = bench.temp() / "ws2"
    try:
        expect("base-incomplete", lambda: install.install(engine, ws2 / INSTANCE, [], base=BASE))
    finally:
        aside.rename(turn)
    if not ws2.exists():
        held("nothing written on base-incomplete", "the target directory does not exist after the refusal")
    else:
        failures.append(f"  ✗ base-incomplete wrote       {list(ws2.rglob('*'))[:5]}")

    # --- a silent base refuses before anything is written ---------------------------------
    system = witness / "system"
    hushed = witness / "system.aside"
    system.rename(hushed)
    ws3 = bench.temp() / "ws3"
    try:
        expect("base-silent", lambda: install.install(engine, ws3 / INSTANCE, [], base=BASE))
    finally:
        hushed.rename(system)
    if not ws3.exists():
        held("nothing written on base-silent", "the target directory does not exist after the refusal")
    else:
        failures.append(f"  ✗ base-silent wrote           {list(ws3.rglob('*'))[:5]}")

    # --- the base's sockets are bare, its keys are bare -------------------------------------
    mounted = instance.mounting(made, "boot.ready")
    fragments = [one for one in tuning.fragments(made) if one.name == BASE]
    bare = fragments and ("witness_word", "hello") in fragments[0].defaults
    if mounted == ("HELLO.md",) and GREETED in booted and bare:
        held("the base's names are bare", "`boot.ready` is the base's socket address, the "
             "instance's document mounted there reaches the boot; the fragment's bare key is read")
    else:
        failures.append(f"  ✗ bare names                  mounted={mounted} reached="
                        f"{GREETED in booted} fragment={fragments}")


def _persona(root: Path, member: str) -> Path:
    (root / "user").mkdir(parents=True)
    (root / "user" / "MEMBER.md").write_text(member, encoding="utf-8")
    return root


def user_layer(bench, plain) -> None:
    """The user layer: one bearer, the placement's net, the base's own layer, a base without one."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- one bearer, backed-up replacement --------------------------------------------------
    persona_a = _persona(bench.temp() / "a", PERSONA_A)
    persona_b = _persona(bench.temp() / "b", PERSONA_B)
    expect("user-packages-conflict",
           lambda: install._single_user_bearer([("a", persona_a), ("b", persona_b)]))

    user_made = plain.made
    member_doc = user_made / "MEMBER.md"
    src_root = install.product_root(PRODUCT_ENGINE)
    saved0 = install._place_user(user_made, persona_a, src_root, backup=True)
    pristine_ok = (member_doc.read_text(encoding="utf-8") == PERSONA_A
                   and not saved0 and not (user_made / "MEMBER.md.old").exists())
    saved1 = install._place_user(user_made, persona_a, src_root, backup=True)
    idem_ok = not saved1 and not (user_made / "MEMBER.md.old").exists()
    member_doc.write_text(OWN_WORDS, encoding="utf-8")
    saved2 = install._place_user(user_made, persona_b, src_root, backup=True)
    edited_ok = (saved2 == ["MEMBER.md"]
                 and member_doc.read_text(encoding="utf-8") == PERSONA_B
                 and (user_made / "MEMBER.md.old").read_text(encoding="utf-8") == OWN_WORDS)
    if pristine_ok and idem_ok and edited_ok:
        held("user files replace with a net", "a template seed or an identical copy "
             "swaps silently; the operator's own words survive as .old")
    else:
        failures.append(f"  ✗ user placement              {pristine_ok}/{idem_ok}/{edited_ok}")

    # --- the base's own user layer is no rival ----------------------------------------------
    base_root = _persona(bench.temp() / "base", BASE_MEMBER)
    install._single_user_bearer([("base", base_root), ("a", persona_a)], base="base")
    expect("user-packages-conflict",
           lambda: install._single_user_bearer(
               [("base", base_root), ("a", persona_a), ("b", persona_b)], base="base"))
    held("the base's user layer is no rival", "a base carrying user/ and one persona pass, "
         "two personas still refuse")

    # --- a base without user/ installs no member ---------------------------------------------
    mute_engine = bench.source_with(MUTE)
    mute = mute_engine.parent.parent / "bases" / MUTE
    shutil.rmtree(mute / "user", ignore_errors=True)       # the witness is a copy of the kit
    boot = mute / "procs" / "BOOT.md"
    boot.write_text(boot.read_text(encoding="utf-8").replace("  CALL MEMBER.md\n", ""),
                    encoding="utf-8")
    ws4 = bench.temp() / "ws4"
    mute_made = install.install(mute_engine, ws4 / INSTANCE, [], base=MUTE)
    (mute_made / "procs" / "HELLO.md").write_text(GREETING, encoding="utf-8")
    mute_engine_copy = mute_made / ".sys" / "engine" / "pp.py"
    mute_c = Conductor(discovery.instance_member(mute_engine_copy), mute_engine_copy, "t")
    mute_block = mute_c.start(mute_c.boot("BOOT.md"))
    if (not (mute_made / "MEMBER.md").exists()
            and "member_seed" not in instance.read(mute_made)
            and mute_block is not None):
        held("a base without user/ installs no member", "no MEMBER.md at the root, no "
             "member_seed at the manifest -- the template seeds the engine's own; the run boots")
    else:
        failures.append(f"  ✗ mute base                   member={(mute_made / 'MEMBER.md').exists()} "
                        f"seed={'member_seed' in instance.read(mute_made)} block={mute_block is not None}")


def scenario(bench) -> int:
    plain = bench.env("plain")
    named_base(bench, plain)
    user_layer(bench, plain)
    return 0
