"""Scenario `house-ground` -- the pattern `packaging/house-ground`, played from its demonstration on
one house and two agents that borrow its machine:
- the agent whose TURN imports the house's HOUSE.md has, from its first block, HOUSE's law, its offer
  SALON and its body
- HOUSE's rows read where the house lives: `notes/charter.md` from the house's workspace, never the
  agent's file of the same path; `notes/visitor.md`, which the agent alone holds, not served and said
  in the block; `notes/shelf.md @shelf` from the tree the row names, never the house's file of that path;
  `engine/patterns/packaging/house-ground/README.md`, which the house reads in its machine's copy, served
  from that copy
- at the park the offer stands: on one run the agent's own `-s SALON`, under its key, opens SALON; on
  another run the principal's `-s SALON` opens it
- at the next exchange the law and the offer hold, HOUSE's body and its reading are not served again
- the agent without the line has nothing of HOUSE
The rows that read the shelf and the visitor's note are added to HOUSE at the test's time; the house's
files, the agent's files of the same paths and the shelf are written then too.
"""
from __future__ import annotations

from conductor import Conductor, compiling, discovery, render
from tests.harness import agents, cli, demonstrated, demos, na_proof, plant, stepped

DRAWER, PATTERN = "packaging", "house-ground"
DEMOS = ("HOUSE.md", "SALON.md", "TURN.ground.md")
DEMO = demos(DRAWER, PATTERN)
CHARTER = "notes/charter.md"
HOUSE_NOTE = "The house's charter: one ground, read where the house lives."
AGENT_NOTE = "The agent's own charter, a file of the same path in its workspace."
VISITOR = "notes/visitor.md"
VISITOR_NOTE = "The visitor's note, which the agent alone holds."
SHELF = "notes/shelf.md"
SHELF_NOTE = "The shelf's note, read from the tree the row names."
HOUSE_SHELF = "The house's copy of the shelf's note, never read."
MACHINE_ROW = "engine/patterns/packaging/house-ground/README.md"


def _agent(env, console, name: str):
    """-> (the agent's instance, its workspace): `-install agents/<name>` under the house."""
    cli(console, "-install", f"agents/{name}", cwd=env.root)
    home = env.root / "agents" / name
    return home / env.made.name, home


def _parked(make, block) -> object:
    """-> the block the run parks on, every step from `block` answered."""
    for _ in range(12):                              # bounded: a run that stops moving fails the case
        if block is None or block.wait:
            return block
        block = stepped(make, na_proof(block) if block.judged else "")
    return block


def _offered(text: str) -> list[str]:
    """-> the names the TOOLS sections of a rendering offer."""
    lines = text.splitlines()
    return [name for at, line in enumerate(lines) if line.startswith("▌ TOOLS") and at + 1 < len(lines)
            for name in lines[at + 1].strip("[]").split()]


def _print(make):
    """-> the block the agent's prints due move the run to, None when nothing was due."""
    for document in make().prints_due():
        _, block = make().printed(document, "said")
        if block is not None:
            return block
    return None


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    found = demonstrated(DRAWER, PATTERN)
    if found != sorted(DEMOS):
        failures.append(f"  ✗ the demonstration           {found!r} -- owed {sorted(DEMOS)!r}")
        return 0
    env = bench.env("house-ground")
    plant(env, DRAWER, PATTERN, ("HOUSE.md", "SALON.md"))
    house = env.made / "procs" / "HOUSE.md"
    house.write_text(house.read_text(encoding="utf-8").replace(
        f"serve: |\n  {CHARTER}\n",
        f"materials: |\n  shelf: {env.root / 'shelf'}\nserve: |\n  {CHARTER}\n  {VISITOR}\n  {SHELF} @shelf\n  {MACHINE_ROW}\n"),
        encoding="utf-8")
    for root, files in ((env.root, {CHARTER: HOUSE_NOTE, SHELF: HOUSE_SHELF}), (env.root / "shelf", {SHELF: SHELF_NOTE})):
        for relpath, text in files.items():
            (root / relpath).parent.mkdir(parents=True, exist_ok=True)
            (root / relpath).write_text(text + "\n", encoding="utf-8")
    console = env.made / ".sys" / "engine" / "pp.py"
    taker, home = _agent(env, console, "taker")
    (taker / "procs").mkdir(exist_ok=True)
    (taker / "procs" / "TURN.md").write_text((DEMO / "TURN.ground.md").read_text(encoding="utf-8"),
                                             encoding="utf-8")
    (home / "notes").mkdir(exist_ok=True)
    (home / CHARTER).write_text(AGENT_NOTE + "\n", encoding="utf-8")
    (home / VISITOR).write_text(VISITOR_NOTE + "\n", encoding="utf-8")
    compiling.build_tools(taker)
    member = discovery.member_at(taker)
    make = lambda key=None: Conductor(member, console, key)   # noqa: E731
    opener = make()
    first = opener.start(opener.boot("BOOT.md"), "the first ask")
    key = opener.run_id
    shown = render(first)
    body = (DEMO / "HOUSE.md").read_text(encoding="utf-8").rsplit("---\n", 1)[-1].strip()
    if "HG1  " in shown and "SALON" in _offered(shown) and body in shown:
        held("the agent that imports takes the ground", "HG1, the offer SALON and HOUSE's body in its first block")
    else:
        failures.append(f"  ✗ the ground taken            {_offered(shown)} law={'HG1  ' in shown} body={body in shown}")
    said = f"(not served: `{VISITOR}`"
    machine_text = (env.made / ".sys" / MACHINE_ROW).read_text(encoding="utf-8").strip()
    if (HOUSE_NOTE in shown and AGENT_NOTE not in shown and VISITOR_NOTE not in shown and said in shown
            and SHELF_NOTE in shown and HOUSE_SHELF not in shown and machine_text in shown):
        held("HOUSE's rows read where the house lives", f"{CHARTER} the house's, the agent's unread; {VISITOR}, "
             f"the agent's alone, not served and said; {SHELF} @shelf from the shelf, the house's copy unread; "
             f"{MACHINE_ROW} from the machine's copy")
    else:
        failures.append(f"  ✗ the house's reading         house={HOUSE_NOTE in shown} agent={AGENT_NOTE in shown} "
                        f"visitor={VISITOR_NOTE in shown} said={said in shown} shelf={SHELF_NOTE in shown} "
                        f"house_shelf={HOUSE_SHELF in shown} machine={machine_text in shown}")

    # --- at the park, the offer answers the agent and the principal --------------------------------
    parked = _parked(lambda: make(key), first)
    by_agent = cli(console, "--instance", str(taker), key, "-s", "SALON", cwd=home, env=agents(key))
    shown_agent = cli(console, "--instance", str(taker), key, cwd=home)          # the held view, rendered
    closed = _print(lambda: make(key))
    if (parked is not None and parked.wait and by_agent.returncode == 0
            and "▸ SALON{" in by_agent.stdout + shown_agent.stdout and "HG2" in by_agent.stdout + shown_agent.stdout):
        held("the agent opens the door at the park", "its `-s SALON` under its key on the parked run: SALON's "
             "frame, HG2 in force")
    else:
        failures.append(f"  ✗ the agent's door            parked={parked and parked.wait} rc={by_agent.returncode} "
                        f"{by_agent.stdout[-200:]!r} {shown_agent.stdout[-200:]!r} {by_agent.stderr[-160:]!r} "
                        f"closed={closed and closed.stack}")
    other_run = make()
    other_first = other_run.start(other_run.boot("BOOT.md"), "the principal's own ask")
    other_key = other_run.run_id
    other_parked = _parked(lambda: make(other_key), other_first)
    by_principal = cli(console, "--instance", str(taker), other_key, "-s", "SALON", cwd=home)
    if (other_parked is not None and other_parked.wait and by_principal.returncode == 0
            and "▸ SALON{" in by_principal.stdout and "HG2" in by_principal.stdout):
        held("the principal opens the door at the park", "on a run of its own, the principal's `-s SALON` at the "
             "park: SALON's frame, HG2 in force")
    else:
        failures.append(f"  ✗ the principal's door        parked={other_parked and other_parked.wait} "
                        f"rc={by_principal.returncode} {by_principal.stdout[-200:]!r} {by_principal.stderr[-160:]!r}")
    make(other_key).forget()

    # --- the next exchange: the law and the offer hold, nothing served again ------------------------
    second = make(key).forward("the second ask")
    text = render(second)
    if ("HG1" in text and "SALON" in _offered(text) and body not in text and HOUSE_NOTE not in text):
        held("the ground holds at the next exchange", "HG1 and SALON in force, HOUSE's body and the "
             "charter not served again")
    else:
        failures.append(f"  ✗ the next exchange           {second.stack} {_offered(text)} body={body in text} "
                        f"note={HOUSE_NOTE in text} {text[-600:]!r}")
    make(key).forget()

    # --- the agent without the line has nothing of HOUSE ---------------------------------------------
    plain, _ = _agent(env, console, "plain")
    other = Conductor(discovery.member_at(plain), console, None)
    bare = other.start(other.boot("BOOT.md"), "the first ask")
    plain_text = render(bare)
    if "HG1" not in plain_text and "SALON" not in _offered(plain_text) and body not in plain_text:
        held("the agent without the line has nothing", "no HG1, no SALON, no HOUSE body")
    else:
        failures.append(f"  ✗ the agent without the line  {_offered(plain_text)}")
    other.forget()
    return 0
