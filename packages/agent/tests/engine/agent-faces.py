"""Scenario `agent-faces` -- the faces of the agents: what the post reads, one object per line, and the
exchanges paired with their messages.
- `status <path> --json` after two wake-ups on one run: one object per run with the state that prevails, the records summed (cost, launches, the first message, the hours), the providers' object last; the keys exactly the README's
- `name <path> <key> [<name>]`: a line to `names.jsonl`, the last one winning at `status --json` -- a name a user types,
  accents and punctuation kept as typed, its edges trimmed (agent 0.23.1); `run-unknown` and `name-invalid` (empty, two
  lines, 61 characters) refuse, nothing written
- `exchanges <path> <key> --json`: one object per exchange, the message paired with the response of its rank; a wake-up that crashed leaves a message with `response: null`
- `stats <path> <key> --json`: the engine's `-stats <key> -json` object under `conduction`, the sums beside
- `list --json`: the house (`.`, its runs of the post), then one object per agent
- the policy (batch les-parametres-du-run): `status --json` says each run's policy (its last message's) and,
  on the last object, `last` -- the provider and the policy the agent last played, `null` for an agent never
  sent a message; `providers --json` says what each wired adapter spells, the models it names and the scope of
  its cost (`COST`, read through the engine's face; batch le-plafond-du-run); `status --json` says `budget`, null
  without a cap
- `exchanges --json` says whether each exchange was conducted (batch la-suspension-par-l-agent; a bare one says
  false, `agent-chat-json`)
- the context (batch la-part-de-pp-dans-le-contexte): `status --json` says each run's `context` {tokens, used, pp,
  over, estimated}, `stats --json` the whole `context` -- the flow of a witness that says no event: its prompts and its
  answers, nothing measured, the estimate its flow under no adapter's constants (the detail is `agent-chat-voices`'s)
- `calibrate [<path> ...] --json` (batch le-contexte-mesure; its fit read whole, batch les-sommes-du-flux: the run
  handed to the fit is the store's first and last call with the flow and the thought its responses sum, the gaps of
  one run are that run's, the fit says its base, a ratio and a part kept of its grids, one gap): per run, the measure
  the provider's store keeps of its
  session -- its calls, its compactions, the last call's context, equal to the one its exchange measured -- beside
  the two estimates and their gaps, a run whose store says nothing `measured: null`; then per provider the gaps and
  the constants fitted; nothing written
- `calibrate` in text: one line per run, then one per provider with a measured run
- `status` in text while a wake-up plays a run (its wake lock held by the bench): as many lines as at rest, the
  run's own line another
- `flow --from <n>`: the lines of the kept flow from the n-th on; past the end nothing, 0 the usage; `--follow` on
  a run nobody plays streams the same lines and leaves at the exchange's verdict
- the weight (batch le-poids-des-runs): `status --json` says each run's `weight` {lines, files, bytes, flow}, EQUAL
  to what `agent purge <path> <key> --json` counts without `--yes`; the last object and `list --json` their sum
- the pairing, on runs of their own under a law of production: a conversation
  whose first message is stopped during the witness's pause keeps no response for it, `exchanges --json` says
  `null` for the first and the responses for the next two; records sharing seconds (lines the bench writes after
  a run of the witness) -- each response at its message, the order of both records kept; no record gains a field
- the order and the readings (batch la-face-lineaire): `status` says the runs by their last activity, the latest
  first, in text as in JSON; one call reads each record once, whatever the number of runs (a `sitecustomize` counts
  the reads of the script's process); a line the script appends is seen by the next reading of the same process
- the default window (batch la-fenetre-par-defaut): a run whose provider does not declare its model, or that names
  none, is judged against the provider's `DEFAULT_WINDOW` -- `used` at `status --json` is its tokens over it, and
  the window a launch gives its `context` events is the same; a caller's command keeps none
- the root (batch le-lieu-du-plan): `status --json` says each run's `documents` -- the absolute path of the root of
  documents the run was opened with (`--documents`, given relative), `null` for a run opened with none
- the overruns (agent 1.0.32): a run of two exchanges, the first whose last message is over `ANSWER_BOUND` --
  `stats --json` says `overruns` 1, the text of `stats` its line after the engine's; `exchanges --json` says each
  exchange's `overruns` and `finals`, the text of `exchanges` the overrun on the first line alone
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from conductor import adapters, install
from tests.harness import holding, support

A = support(__file__, "agent")

STATUS_KEYS = {"agent", "run", "name", "exchanges", "state", "awaits", "stack", "spaces", "session", "provider", "cost_usd",
               "launches", "responses", "first_message", "first_at", "last_at", "policy", "budget", "context",
               "packages", "weight", "documents"}
TAIL_KEYS = {"agent", "providers", "last", "weight", "packages"}
WEIGHT_KEYS = {"lines", "files", "bytes", "flow"}
PROVIDER_KEYS = {"provider", "spells", "models", "cost"}
EXCHANGE_KEYS = {"agent", "run", "index", "at", "message", "response", "cost_usd", "launches", "error", "harness_rc",
                 "conducted",
                 "words", "finals", "overruns", "model", "effort"}   # the three of plan fixes2; `finals` and
# `overruns`, agent 1.0.32
STATS_KEYS = {"agent", "run", "cost_usd", "launches", "overruns", "exchanges", "conduction", "context"}
CONTEXT_KEYS = {"flow", "tokens", "measured", "estimated", "window", "used", "pp", "calls", "reread", "since"}
LIST_KEYS = {"agent", "runs", "running", "responses", "weight"}
SENT_FIELDS = {"at", "from", "to", "run", "message", "policy", "conducted"}
HOLD = 10.0
WATCHED = ("responses.jsonl", "messages.jsonl", "names.jsonl", "sessions.jsonl")
READS_HOOK = f"""\
import atexit, json, os, pathlib, sys
_seen = {{}}
_read = pathlib.Path.read_text
def _counted(self, *args, **kwargs):
    if self.name in {WATCHED!r}:
        _seen[self.name] = _seen.get(self.name, 0) + 1
    return _read(self, *args, **kwargs)
pathlib.Path.read_text = _counted
@atexit.register
def _said():
    if _seen and any(arg.endswith("pp-agent.py") for arg in sys.argv):
        pathlib.Path(os.environ["READS_DIR"], f"{{os.getpid()}}.json").write_text(json.dumps(_seen))
"""


def objects(text: str) -> list[dict]:
    return [json.loads(one) for one in text.splitlines() if one.strip()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = A.House(bench)
    first = h.wake("hello there", "play", "--model", "m1")
    key = h.keys()[0] if h.keys() else ""
    second = h.wake("and again", "play", "--run", key, "--model", "m1")
    if not (first.returncode == 0 and second.returncode == 0 and key and len(h.responses()) == 2):
        failures.append(f"  ✗ two wake-ups                rc={first.returncode},{second.returncode} key={key!r} "
                        f"{first.stderr[-200:]!r} {second.stderr[-200:]!r}")
        return 0
    costs = [one["cost_usd"] for one in h.responses()]
    launches = sum(one["launches"] for one in h.responses())

    # --- status --json: the run, its sums, the providers -----------------------------------------
    faced = h.call("agent", "status", "agents/ag1", "--json")
    rows = objects(faced.stdout) if faced.returncode == 0 else []
    runs = [one for one in rows if "run" in one]
    tail = rows[-1] if rows else {}
    if (faced.returncode == 0 and len(runs) == 1 and set(runs[0]) == STATUS_KEYS and runs[0]["run"] == key
            and runs[0]["agent"] == "agents/ag1" and runs[0]["exchanges"] == 2 and runs[0]["state"] == "parked"
            and runs[0]["awaits"] == "message"
            and runs[0]["name"] == "" and runs[0]["responses"] == 2 and runs[0]["launches"] == launches
            and abs(runs[0]["cost_usd"] - sum(costs)) < 1e-6 and runs[0]["first_message"] == "hello there"
            and runs[0]["first_at"] and runs[0]["last_at"] >= runs[0]["first_at"] and runs[0]["session"]
            and runs[0]["provider"] == "harness" and runs[0]["policy"] == {"model": "m1"} and runs[0]["budget"] is None
            and runs[0]["documents"] is None
            and set(runs[0].get("spaces") or {}) == {"open", "openable"} and runs[0]["spaces"]["open"] == []
            and set(runs[0]["context"] or {}) == {"tokens", "used", "pp", "over", "estimated"} and runs[0]["context"]["tokens"] > 0
            and runs[0]["context"]["estimated"] is True
            and runs[0]["context"]["used"] is None and 0 < runs[0]["context"]["pp"] <= 1
            and set(tail) == TAIL_KEYS and tail["agent"] == "agents/ag1"
            and tail["last"] == {"provider": "harness", "policy": {"model": "m1"}}):
        held("status --json says the run and its sums", f"one run: exchanges 2, parked, cost {runs[0]['cost_usd']} = "
             f"{costs[0]} + {costs[1]}, launches {launches}, first message `hello there`, session {runs[0]['session']}, "
             "policy {model: m1}; the providers' object last with last = harness and {model: m1}; the keys exactly the README's")
    else:
        failures.append(f"  ✗ status --json               rc={faced.returncode} {rows} {faced.stderr[-200:]!r}")

    # --- the weight: what a purge would count, read without one -------------------------------------------
    dry = h.call("agent", "purge", "agents/ag1", key, "--json")
    try:
        counted = (json.loads(dry.stdout).get("runs") or [{}])[0]
    except ValueError:
        counted = {}
    owed = {"lines": sum((counted.get("lines") or {}).values()), "files": len(counted.get("files") or []),
            "bytes": counted.get("bytes"), "flow": counted.get("flow")}
    listed = next((one for one in objects(h.call("agent", "list", "--json").stdout) if one.get("agent") == "agents/ag1"), {})
    weight = runs[0].get("weight") if runs else None
    if (dry.returncode == 0 and isinstance(weight, dict) and set(weight) == WEIGHT_KEYS and weight == owed
            and owed["files"] > 0 and owed["lines"] > 0 and owed["flow"]
            and tail.get("weight") == owed and listed.get("weight") == owed):
        held("the weight is the purge's count", f"run {key}: {weight} -- the dry `purge --json` counts the same; "
             "the last object and list --json say the sum")
    else:
        failures.append(f"  ✗ weight                      rc={dry.returncode} weight={weight} owed={owed} "
                        f"tail={tail.get('weight')} list={listed.get('weight')} {dry.stderr[-200:]!r}")

    # --- name: written, the last one wins, the refusals write nothing ------------------------------
    named = h.call("agent", "name", "agents/ag1", key, "demo")
    slashed = h.call("agent", "name", "agents/ag1", key, "a/b")
    priced = h.call("agent", "name", "agents/ag1", key, "Prix de la DDR4 (v2)")
    renamed = h.call("agent", "name", "agents/ag1", key, "  Réunion fournisseurs  ")
    said = h.call("agent", "name", "agents/ag1", key)
    names = A.lines(h.records / "names.jsonl")
    kept = (h.records / "names.jsonl").read_bytes()
    after = [one for one in objects(h.call("agent", "status", "agents/ag1", "--json").stdout) if "run" in one]
    unknown = h.call("agent", "name", "agents/ag1", "zzzzzz", "x")
    invalid = [h.call("agent", "name", "agents/ag1", key, given) for given in ("   ", "line one\nline two", "x" * 61)]
    if (named.returncode == 0 and f"run {key} · named demo" in named.stdout and slashed.returncode == 0
            and priced.returncode == 0 and renamed.returncode == 0
            and f"run {key} · named Réunion fournisseurs" in renamed.stdout
            and said.stdout.strip().endswith("named Réunion fournisseurs")
            and [one["name"] for one in names] == ["demo", "a/b", "Prix de la DDR4 (v2)", "Réunion fournisseurs"]
            and set(names[0]) == {"at", "agent", "run", "name"}
            and names[0]["agent"] == "agents/ag1" and names[0]["run"] == key
            and "Réunion fournisseurs".encode("utf-8") in kept
            and after and after[0]["name"] == "Réunion fournisseurs"
            and unknown.returncode == 2 and "run-unknown" in unknown.stderr
            and all(one.returncode == 2 and "name-invalid" in one.stderr for one in invalid)
            and (h.records / "names.jsonl").read_bytes() == kept):
        held("name keeps the run's name, the last one wins", "four lines at names.jsonl -- `a/b`, `Prix de la DDR4 "
             "(v2)`, `Réunion fournisseurs` trimmed, its accent as typed --, status --json and `name` alone say it; "
             "run-unknown and name-invalid (empty, two lines, 61 characters) refuse with nothing written")
    else:
        failures.append(f"  ✗ name                        {named.returncode}/{slashed.returncode}/{priced.returncode}/"
                        f"{renamed.returncode} {said.stdout!r} {names} {after[:1]} {unknown.stderr[-100:]!r} "
                        f"{[one.stderr[-100:] for one in invalid]!r}")

    # --- exchanges: paired by rank; a crashed wake-up leaves a message without a response --------
    crashed = h.wake("third, crashing", "crash", "--run", key)
    history = h.call("agent", "exchanges", "agents/ag1", key, "--json")
    turns = objects(history.stdout) if history.returncode == 0 else []
    text = h.call("agent", "exchanges", "agents/ag1", key)
    if (crashed.returncode != 0 and history.returncode == 0 and len(turns) == 3
            and all(set(one) == EXCHANGE_KEYS for one in turns)
            and [one["index"] for one in turns] == [1, 2, 3]
            and [one["message"] for one in turns] == ["hello there", "and again", "third, crashing"]
            and turns[0]["response"] == A.opening(h.dues(key, 1)) and turns[1]["response"] == A.composed(turns[1])
            and turns[0]["cost_usd"] == costs[0] and turns[1]["cost_usd"] == costs[1]
            and turns[2]["response"] is None and turns[2]["cost_usd"] is None and turns[2]["harness_rc"] is None
            and all(one["conducted"] is True for one in turns)
            and text.returncode == 0 and text.stdout.count("\n") == 3):
        held("exchanges pairs each message with its response", "three exchanges: two answered with their cost, the "
             "third (a crashed wake-up) with response null; the text one line each")
    else:
        failures.append(f"  ✗ exchanges                   rc={history.returncode} {turns} {text.stdout!r} {history.stderr[-200:]!r}")

    # --- stats: the engine's object under conduction --------------------------------------------
    measured = h.call("agent", "stats", "agents/ag1", key, "--json")
    stat = objects(measured.stdout)[0] if measured.returncode == 0 and measured.stdout.strip() else {}
    plain = h.call("agent", "stats", "agents/ag1", key)
    engine_said = h.stats(key)
    # two exchanges completed: the crashed wake-up's stays OPEN -- its WORK pending, the AWAIT comes at the
    # principal's call, which the crash never let play (plan fixes2); the engine's object counts it open
    if (measured.returncode == 0 and set(stat) == STATS_KEYS and stat["run"] == key and stat["exchanges"] == 2
            and stat["launches"] == launches and abs(stat["cost_usd"] - sum(costs)) < 1e-6
            and stat["conduction"].get("exchanges") == engine_said.get("exchanges")
            and stat["conduction"].get("blocks", 0) >= 1 and "spent" in stat["conduction"]
            and stat["conduction"].get("key") == key
            and set(stat["context"] or {}) == CONTEXT_KEYS and stat["context"]["calls"] == launches
            and stat["context"]["measured"] is None and stat["context"]["estimated"] is True
            and stat["context"]["tokens"] == stat["context"]["flow"]["total"]
            and stat["context"]["pp"]["served"] == stat["conduction"].get("tokens")
            and plain.returncode == 0 and key in plain.stdout):
        held("stats relays the engine's -stats under conduction", f"conduction.exchanges {stat['conduction'].get('exchanges')}, "
             f"blocks {stat['conduction'].get('blocks')}, spent present; the sums beside; the text relayed")
    else:
        failures.append(f"  ✗ stats                       rc={measured.returncode} {stat} {measured.stderr[-200:]!r} {plain.stdout[:120]!r}")

    # --- list --json ---------------------------------------------------------------------------
    listed = h.call("agent", "list", "--json")
    agents = objects(listed.stdout) if listed.returncode == 0 else []
    if (listed.returncode == 0 and len(agents) == 2 and all(set(one) == LIST_KEYS for one in agents)
            and agents[0] == {"agent": ".", "runs": 0, "running": 0, "responses": 0,   # the house heads the face
                              "weight": {"lines": 0, "files": 0, "bytes": 0, "flow": None}}
            and {k: v for k, v in agents[1].items() if k != "weight"} == {"agent": "agents/ag1", "runs": 1, "running": 0,
                                                                         "responses": 2}
            and agents[1]["weight"]["files"] > 0):
        held("list --json says the house, then each agent", f"{agents}")
    else:
        failures.append(f"  ✗ list --json                 rc={listed.returncode} {agents} {listed.stderr[-200:]!r}")

    # --- an agent never sent a message: last is null; providers says what each adapter knows --------
    h.born("agents/ag2")
    wired = install.wired_providers(h.ws)                      # the house wired by its witness's adapter
    spells = list(A.declared(h.house, wired[0], "SPELLS", ())) if wired else []
    models = list(A.declared(h.house, wired[0], "MODELS", ())) if wired else []
    bare = objects(h.call("agent", "status", "agents/ag2", "--json").stdout)
    offered = h.call("agent", "providers", "--json")
    known = objects(offered.stdout) if offered.returncode == 0 else []
    plain = h.call("agent", "providers")
    if (len(wired) == 1 and bare == [{"agent": "agents/ag2", "providers": wired, "last": None, "weight": {"lines": 0, "files": 0, "bytes": 0, "flow": None},
                                     "packages": [{"name": "agent", "on": True}]}]
            and len(known) == 1 and set(known[0]) == PROVIDER_KEYS and known[0]["provider"] == wired[0]
            and known[0]["spells"] == spells and known[0]["models"] == models
            and known[0]["cost"] == getattr(adapters.load(known[0]["provider"], h.house), "COST", "absent")
            and plain.returncode == 0 and plain.stdout.count("\n") == 1
            and plain.stdout.startswith(f"{wired[0]} · spells {', '.join(spells)} · models ")):
        held("last is null without a message, providers says the adapters", f"agents/ag2: {bare[0]}; providers --json "
             f"{known[0]['provider']} spells {known[0]['spells']}, {len(known[0]['models'])} models; one line in text")
    else:
        failures.append(f"  ✗ last and providers          {bare} rc={offered.returncode} {known} {plain.stdout!r} {offered.stderr[-200:]!r}")

    h.lawful()          # the exchanges owe a proof, fused under the WORK: one launch, the AWAIT held after it

    # --- the state is read at the SLOT, never at the trace ------------------------
    known = set(h.keys())
    h.wake("parked, then its trace gone", "play")
    traced = next((one for one in h.keys() if one not in known), "")
    slot = A.persistence.slot_of(h.agent_meta, traced)
    log = A.persistence.trace_of(slot) if traced else ""
    before_state = h.face(traced).get("state") if traced else None
    if log:
        (slot.parent / log).unlink()
    after_state = h.face(traced).get("state") if traced else None
    known = set(h.keys())
    h.defers = True     # the witness keeps its proof for its next launch: the bound of one launch leaves the run standing
    spent = h.wake("one launch only", "play", "--launches", "1")
    h.defers = False
    standing = next((one for one in h.keys() if one not in known), "")
    standing_state = h.face(standing).get("state") if standing else None
    repaired = [one.get("kind") for one in h.trace(standing)].count("repair") if standing else -1
    if (traced and before_state == "parked" and after_state == "parked"
            and spent.returncode == 2 and "launches-spent" in spent.stderr and standing_state == "standing"
            and repaired == 1):
        held("status reads the slot, not the trace", f"run {traced}: parked before and after its trace is gone; "
             f"run {standing}: one launch under a law of production, its proof kept back, launches-spent, standing on "
             "the repair it owes (1 repair traced)")
    else:
        failures.append(f"  ✗ state at the slot           traced={traced} before={before_state!r} after={after_state!r} "
                        f"spent rc={spent.returncode} standing={standing_state!r} repairs={repaired} {spent.stderr[-160:]!r}")

    # --- the flow from a rank: what a reader that follows a launch asks again ----------------------
    whole = objects(h.call("agent", "flow", "agents/ag1", standing, "--json").stdout) if standing else []
    tail = h.call("agent", "flow", "agents/ag1", standing, "--json", "--from", "3") if standing else None
    beyond = h.call("agent", "flow", "agents/ag1", standing, "--json", "--from", str(len(whole) + 5)) if standing else None
    zero = h.call("agent", "flow", "agents/ag1", standing, "--json", "--from", "0") if standing else None
    began = time.monotonic()
    followed = h.call("agent", "flow", "agents/ag1", standing, "--json", "--from", "3", "--follow") if standing else None
    took_f = time.monotonic() - began
    if (standing and len(whole) >= 4 and tail is not None and tail.returncode == 0
            and objects(tail.stdout) == whole[2:]
            and beyond is not None and beyond.returncode == 0 and beyond.stdout == ""
            and zero is not None and zero.returncode == 2
            and followed is not None and followed.returncode == 0 and objects(followed.stdout) == whole[2:]
            and took_f < 5.0):
        held("flow --from reads from a rank", f"run {standing}: {len(whole)} lines kept; --from 3 gives the "
             f"{len(whole) - 2} from the third on, past the end nothing, --from 0 the usage; --follow on a run "
             f"nobody plays streams the same and leaves at its verdict ({took_f:.1f}s)")
    else:
        failures.append(f"  ✗ flow --from                 run={standing} whole={len(whole)} "
                        f"tail={getattr(tail, 'returncode', None)}:{len(objects(tail.stdout)) if tail else '-'} "
                        f"beyond={getattr(beyond, 'returncode', None)}:{(beyond.stdout if beyond else '')[:60]!r} "
                        f"zero={getattr(zero, 'returncode', None)} follow={getattr(followed, 'returncode', None)}:"
                        f"{len(objects(followed.stdout)) if followed else '-'} took={took_f:.1f}")

    def talk(mode: str, where: Path) -> subprocess.Popen:
        argv = [sys.executable, str(h.engine), "--instance", str(h.house), "agent", "chat", "agents/ag1",
                "--json", *h.harnessed_at(mode, where)]
        return subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, cwd=h.ws, env={**os.environ, **h.env})

    def command(kind: str, **fields) -> str:
        return json.dumps({"kind": kind, **fields}) + "\n"

    def until_kind(live, kind: str) -> list[dict]:
        seen = []
        while True:
            line = live.stdout.readline()
            if not line:
                return seen
            seen.append(json.loads(line))
            if seen[-1].get("kind") == kind:
                return seen

    def exchanges(key: str, *flags: str) -> subprocess.CompletedProcess:
        return h.call("agent", "exchanges", "agents/ag1", key, *flags)

    # --- the pairing: a message stopped before its launch ended, then two; each response at its message -----
    known = set(h.keys())
    out = bench.temp() / "pa"
    live = talk("pause", out)
    live.stdin.write(command("message", text="un"))
    live.stdin.flush()
    opened = time.monotonic()
    while not h.read(".pid", out) and time.monotonic() - opened < HOLD:
        time.sleep(0.05)
    live.stdin.write(command("stop"))
    live.stdin.flush()
    first = until_kind(live, "verdict")
    key = next((one for one in h.keys() if one not in known), "")
    live.stdin.write(command("message", text="deux") + command("message", text="trois") + command("quit"))
    live.communicate(timeout=120)
    paired = objects(exchanges(key, "--json").stdout)
    text = exchanges(key).stdout.splitlines()
    kept = [one for one in h.responses() if one.get("run") == key]
    if ([one.get("state") for one in first if one.get("kind") == "verdict"] == ["interrupted"]
            and len(kept) == 2 and [one.get("message") for one in paired] == ["un", "deux", "trois"]
            and [one.get("response") is None for one in paired] == [True, False, False]
            and [one.get("index") for one in paired] == [1, 2, 3]
            and len(text) == 3):
        held("an interrupted message keeps no response, the next ones keep theirs",
             f"run {key}: 3 messages, 2 responses kept; `un` null, `deux` and `trois` answered; the text one line each")
    else:
        failures.append(f"  ✗ interrupted then two      key={key} kept={len(kept)} "
                        f"paired={[(one.get('message'), one.get('response')) for one in paired]} text={text}")

    # --- shared seconds: the bench writes a run's lines after a real exchange ------------------------
    known = set(h.keys())
    made = h.wake("m1", "play")
    run = next((one for one in h.keys() if one not in known), "")
    template_sent = next((one for one in h.messages() if one.get("run") == run), {})
    template_kept = next((one for one in h.responses() if one.get("run") == run), {})

    def sent(at: str, message: str) -> dict:
        return {**template_sent, "at": at, "message": message}

    def answer(at: str, index: int, response: str) -> dict:
        return {**template_kept, "at": at, "index": index, "response": response}

    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as messages, \
            (h.records / "responses.jsonl").open("a", encoding="utf-8") as responses:
        messages.write(json.dumps(sent("2099-01-01T00:00:10+00:00", "m2")) + "\n")     # kept nothing
        messages.write(json.dumps(sent("2099-01-01T00:00:20+00:00", "m3")) + "\n")
        responses.write(json.dumps(answer("2099-01-01T00:00:20+00:00", 2, "r3")) + "\n")   # its own second
        messages.write(json.dumps(sent("2099-01-01T00:00:30+00:00", "m4")) + "\n")
        responses.write(json.dumps(answer("2099-01-01T00:00:31+00:00", 3, "r4")) + "\n")
        messages.write(json.dumps(sent("2099-01-01T00:00:31+00:00", "m5")) + "\n")      # r4's second
        responses.write(json.dumps(answer("2099-01-01T00:00:40+00:00", 4, "r5")) + "\n")
    shared = objects(exchanges(run, "--json").stdout)
    pairs = [(one.get("message"), one.get("response")) for one in shared]
    if (made.returncode == 0 and run and [one.get("message") for one in shared] == ["m1", "m2", "m3", "m4", "m5"]
            and shared[0].get("response") == template_kept.get("response")
            and pairs[1:] == [("m2", None), ("m3", "r3"), ("m4", "r4"), ("m5", "r5")]):
        held("shared seconds", f"run {run}: m2 kept nothing; r3 in m3's own second, r4 in m5's second -- each "
             "response at its message, the order of both records kept")
    else:
        failures.append(f"  ✗ shared seconds            rc={made.returncode} run={run} pairs={pairs}")

    # --- the order: the run that spoke last heads the face, whatever its key -----------------------------------
    keys = sorted(h.keys())
    newest = keys[-1]
    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as messages:
        messages.write(json.dumps({**template_sent, "run": newest, "at": "2100-01-01T00:00:00+00:00",
                                   "message": "latest"}) + "\n")
    ordered = [one for one in objects(h.call("agent", "status", "agents/ag1", "--json").stdout) if "run" in one]
    lasts = [one.get("last_at") or "" for one in ordered]
    texted = [line.split(" · ", 1)[0].removeprefix("run ") for line in
              h.call("agent", "status", "agents/ag1").stdout.splitlines() if line.startswith("run ")]
    if (len(keys) >= 2 and ordered and ordered[0]["run"] == newest and lasts == sorted(lasts, reverse=True)
            and texted == [one["run"] for one in ordered]):
        held("status says the runs by their last activity", f"{[one['run'] for one in ordered]}: {newest}, the last "
             "key, heads them once it spoke last; the text in the same order")
    else:
        failures.append(f"  ✗ order                       keys={keys} json={[(one['run'], one.get('last_at')) for one in ordered]} "
                        f"text={texted}")

    # --- one reading of each record per call, whatever the number of runs ---------------------------------
    watch = bench.temp() / "reads"
    watch.mkdir()
    (watch / "sitecustomize.py").write_text(READS_HOOK, encoding="utf-8")
    counted = h.call("agent", "status", "agents/ag1", "--json",
                     extra={"PYTHONPATH": str(watch), "READS_DIR": str(watch)})
    reads = [json.loads(one.read_text(encoding="utf-8")) for one in sorted(watch.glob("*.json"))]
    script_reads = reads[0] if len(reads) == 1 else {}
    if (counted.returncode == 0 and len(keys) >= 3
            and set(script_reads) == set(WATCHED) and all(n == 1 for n in script_reads.values())):
        held("status reads each record once", f"{len(keys)} runs: {script_reads}")
    else:
        failures.append(f"  ✗ reads                       rc={counted.returncode} runs={len(keys)} {reads} "
                        f"{counted.stderr[-200:]!r}")

    # --- a line appended to a record is read by the next reading of the same process ----------------------
    script = A.skill()
    record = bench.temp() / "kept.jsonl"
    record.write_text(json.dumps({"n": 1}) + "\n", encoding="utf-8")
    before = script.lines_of(record)
    before.append({"mutated": True})
    with record.open("a", encoding="utf-8") as kept:
        kept.write(json.dumps({"n": 2}) + "\n")
    after = script.lines_of(record)
    if [one.get("n") for one in after] == [1, 2] and script.lines_of(record) == after and after is not before:
        held("the reading kept never hides a write", "a line appended between two readings in one process: the "
             "second sees both lines; a caller's list is its own")
    else:
        failures.append(f"  ✗ kept reading                before={before} after={after}")

    # --- a record's lines are made into objects once per state of the record, whatever the number of runs -----
    made = script.every_response(h.house)
    again = script.every_response(h.house)
    by_run = script.answered_by(h.house, "agents/ag1", key)
    with (h.records / "responses.jsonl").open("a", encoding="utf-8") as kept:
        kept.write(json.dumps({**h.responses()[-1], "run": "zzzzzz"}) + "\n")
    grown = script.every_response(h.house)
    if (made and len(again) == len(made) and all(one is other for one, other in zip(made, again))
            and again is not made and by_run and all(any(one is other for other in made) for one in by_run)
            and len(grown) == len(made) + 1 and grown[-1].run == "zzzzzz"):
        held("the records are made once", f"{len(made)} responses: a second reading and a run's own share the "
             "objects of the first; a line appended is made at the next reading")
    else:
        failures.append(f"  ✗ made once                   made={len(made)} again={len(again)} "
                        f"shared={sum(one is other for one, other in zip(made, again))} run={len(by_run)} "
                        f"grown={len(grown)}")

    # --- no record gains a field --------------------------------------------------------------------
    answered = {field for one in h.responses() for field in one}
    written = {field for one in h.messages() for field in one}
    if (answered <= A.RECORD_FIELDS | {"conducted", A.PENDING} and written <= SENT_FIELDS
            and all(A.PENDING not in one or one.get("launches") for one in h.responses())):
        held("no record gains a field", f"responses {sorted(answered)}; messages {sorted(written)}")
    else:
        failures.append(f"  ✗ records                     responses={sorted(answered)} messages={sorted(written)}")
    # --- calibrate: the measure the provider's store keeps beside the estimates, nothing written --------
    store = bench.temp() / "store"
    known = set(h.keys())
    gauged = h.call("agent", "run", "agents/ag1", "--new", "--message", "measure me",
                    *h.harnessed_at("stream", bench.temp() / "gauged"), extra={h.store: str(store)})
    gkey = next((one for one in h.keys() if one not in known), "")
    record = [one for one in h.responses() if one.get("run") == gkey]
    session = next((one.get("session") for one in reversed(h.sessions()) if one.get("run") == gkey), "")
    with open(h.records / "sessions.jsonl", "a", encoding="utf-8") as sessions:   # the run's session made its grammar's
        sessions.write(json.dumps({"at": A.now_iso(), "agent": "agents/ag1", "run": gkey,
                                   "provider": A.WITNESS_GRAMMAR, "session": session}) + "\n")

    def print_of() -> dict:
        return {str(one): one.read_bytes() for where in (h.records, h.agent_meta / ".sys", store)
                for one in sorted(where.rglob("*")) if one.is_file()}
    before = print_of()
    calibrated = h.call("agent", "calibrate", "agents/ag1", "--json", extra={h.store: str(store)})
    untouched = print_of() == before
    said = objects(calibrated.stdout) if calibrated.returncode == 0 else []
    per_run = {one.get("run"): one for one in said if "run" in one}
    summed = [one for one in said if "run" not in one]
    mine = per_run.get(gkey, {})
    launched = (record[-1].get("launches") or 0) if record else 0
    skill, prior = A.skill(), os.environ.get(h.store)
    os.environ[h.store] = str(store)                       # the store as the adapter's face reads it
    try:
        kept_store = adapters.contexts(A.WITNESS_GRAMMAR, h.agent_meta, session, None) or {}
    finally:
        os.environ.pop(h.store, None) if prior is None else os.environ.update({h.store: prior})
    flows = [one.get("flow") or {} for one in record]
    run_owed = skill.Gauged(first=(kept_store.get("calls") or [0])[0], last=mine.get("measured"),
                            flow=sum(int(one.get(voice) or 0) for one in flows for voice in skill.FLOW_VOICES),
                            thinking=sum(int(one.get("thinking") or 0) for one in flows))
    fit = (summed[0].get("fitted") or {}) if summed else {}
    gaps_owed = {kind: dict.fromkeys(("median", "p10", "p90"), round(abs((mine.get("gap") or {}).get(kind, 0)), 4))
                 for kind in ("flow", "calibrated")}
    if (gauged.returncode == 0 and calibrated.returncode == 0 and untouched and record
            and run_owed.thinking > 0 and (mine.get("estimate") or {}).get("flow") == run_owed.flow
            and fit == skill.fitted([run_owed]).json() and fit.get("CONTEXT_BASE") == run_owed.first
            and fit.get("FLOW_RATIO") in skill.RATIOS and fit.get("THINKING_KEPT") in skill.KEPTS
            and isinstance(fit["gap"].get("median"), float) and fit["gap"]["median"] == fit["gap"].get("p90")
            and summed[0].get("gap") == gaps_owed
            and mine.get("measured") == (record[-1].get("flow") or {}).get("context")
            and mine.get("calls") == 3 * launched and mine.get("compactions") == 0
            and set(mine.get("estimate") or {}) == {"flow", "calibrated"} and set(mine.get("gap") or {}) == {"flow", "calibrated"}
            and all(one.get("measured") is None for run, one in per_run.items() if run != gkey) and len(per_run) >= 2
            and [one.get("provider") for one in summed] == [A.WITNESS_GRAMMAR] and summed[0].get("runs") == 1
            and set(summed[0].get("fitted") or {}) == {"CONTEXT_BASE", "FLOW_RATIO", "THINKING_KEPT", "gap"}):
        held("calibrate reads the provider's store beside the estimates", f"run {gkey}: {mine.get('calls')} calls, "
             f"measured {mine.get('measured')} = its exchange's measure, estimates {mine.get('estimate')}; "
             f"{len(per_run) - 1} run(s) without a store null; {A.WITNESS_GRAMMAR} fitted {summed[0].get('fitted')}; "
             "nothing written")
    else:
        failures.append(f"  ✗ calibrate                   rc={gauged.returncode}/{calibrated.returncode} untouched={untouched} "
                        f"run_owed={run_owed} gaps_owed={gaps_owed} "
                        f"{mine} {summed} launches={launched} {calibrated.stderr[-300:]!r}")

    # --- calibrate in text: one line per run, one per provider with a measured run -----------------------------
    told = h.call("agent", "calibrate", "agents/ag1", extra={h.store: str(store)})
    told_lines = told.stdout.splitlines()
    if told.returncode == 0 and summed and not told.stderr and len(told_lines) == len(per_run) + len(summed):
        held("calibrate says the same in text", f"{len(per_run)} line(s) of runs, then {len(summed)} of providers "
             "with a measured run")
    else:
        failures.append(f"  ✗ calibrate in text           rc={told.returncode} lines={len(told_lines)} "
                        f"runs={len(per_run)} providers={len(summed)} {told.stderr[-200:]!r}")

    # --- status in text under a held wake lock: the run a wake-up plays is said apart ---------------------------
    with holding(A.launcher(h.agent_meta, gkey)):
        live = h.call("agent", "status", "agents/ag1")
    rested = h.call("agent", "status", "agents/ag1")
    live_lines, rested_lines = live.stdout.splitlines(), rested.stdout.splitlines()
    moved = [rank for rank, (one, other) in enumerate(zip(live_lines, rested_lines)) if one != other]
    if (live.returncode == 0 and rested.returncode == 0 and len(live_lines) == len(rested_lines) > 2
            and len(moved) == 1):
        held("status says a run a wake-up plays", f"run {gkey} under a held wake lock: {len(live_lines)} lines as at "
             "rest, one of them another -- the run's")
    else:
        failures.append(f"  ✗ status of a running run     rc={live.returncode}/{rested.returncode} "
                        f"lines={len(live_lines)}/{len(rested_lines)} moved={moved}")

    # --- the root of each run: the absolute path it was opened with, null without ---------------------
    rooted = h.ws / "teams" / "rooted"
    rooted.mkdir(parents=True)
    known = set(h.keys())
    opened = h.wake("under a root", "play", "--documents", "teams/rooted")
    rkey = next((one for one in h.keys() if one not in known), "")
    faced_rooted = h.face(rkey) if rkey else {}
    faced_bare = h.face(key) if key else {}
    if (opened.returncode == 0 and rkey and faced_rooted.get("documents") == str(rooted.resolve())
            and Path(faced_rooted["documents"]).is_absolute()
            and "documents" in faced_bare and faced_bare["documents"] is None):
        held("status --json says each run's root", f"run {rkey} opened with --documents teams/rooted: "
             f"documents {faced_rooted['documents']}; run {key} opened with none: null")
    else:
        failures.append(f"  ✗ documents                   rc={opened.returncode} run={rkey!r} "
                        f"rooted={faced_rooted.get('documents', 'absent')!r} bare={faced_bare.get('documents', 'absent')!r} "
                        f"{opened.stderr[-200:]!r}")

    # --- the default window: a model its provider does not declare, or no model named ---------------------
    default = A.declared(h.house, A.WITNESS_GRAMMAR, "DEFAULT_WINDOW")
    declared = A.declared(h.house, A.WITNESS_GRAMMAR, "CONTEXT_WINDOWS", {}) or {}
    undeclared = "m1" if "m1" not in declared else "m1-undeclared"
    known = set(h.keys())
    named = h.wake("an undeclared model", "play", "--model", undeclared)
    nkey = next((one for one in h.keys() if one not in known), "")
    with open(h.records / "sessions.jsonl", "a", encoding="utf-8") as sessions:   # the runs made their grammar's
        for one in (nkey, traced):                                                 # `traced` named no model
            sessions.write(json.dumps({"at": A.now_iso(), "agent": "agents/ag1", "run": one,
                                       "provider": A.WITNESS_GRAMMAR, "session": f"s-{one}"}) + "\n")
    faced = {one["run"]: one.get("context") or {} for one in objects(h.call("agent", "status", "agents/ag1",
                                                                            "--json").stdout) if "run" in one}
    seen = {one: faced.get(one, {}) for one in (nkey, traced) if one}
    script = A.skill()
    import conductor
    launched = [script.windowed(conductor, h.house, provider, script.Policy.of(policy))
                for provider, policy in ((A.WITNESS_GRAMMAR, {"model": undeclared}), (A.WITNESS_GRAMMAR, {}),
                                         (None, {"model": undeclared}))]
    if (named.returncode == 0 and nkey and traced and len(seen) == 2
            and isinstance(default, int) and default > 0
            and all(isinstance(one.get("tokens"), int) and one["tokens"] > 0
                    and one.get("used") == round(one["tokens"] / default, 4) for one in seen.values())
            and launched == [default, default, None]):
        held("a model its provider does not declare takes the default window", f"{A.WITNESS_GRAMMAR} "
             f"DEFAULT_WINDOW {default}: run {nkey} (`{undeclared}`) used {seen[nkey].get('used')}, run {traced} (no "
             f"model) used {seen[traced].get('used')}; a launch's window {launched} -- None for a caller's command")
    else:
        failures.append(f"  ✗ default window              rc={named.returncode} default={default!r} {seen} "
                        f"launched={launched} {named.stderr[-200:]!r}")

    # --- the overruns: stats and exchanges say them ------------------------------------------------------------
    known = set(h.keys())
    long = h.wake("say it all again", "long")
    over = next((one for one in h.keys() if one not in known), "")
    short = h.wake("and now", "play", "--run", over)
    measured = h.call("agent", "stats", "agents/ag1", over, "--json")
    stat = objects(measured.stdout)[0] if measured.returncode == 0 and measured.stdout.strip() else {}
    plain = h.call("agent", "stats", "agents/ag1", over)
    rows = objects(h.call("agent", "exchanges", "agents/ag1", over, "--json").stdout)
    text = h.call("agent", "exchanges", "agents/ag1", over).stdout.splitlines()
    bound = getattr(A.skill(), "ANSWER_BOUND", None)
    if (long.returncode == 0 and short.returncode == 0 and stat.get("overruns") == 1
            and plain.returncode == 0 and plain.stdout.splitlines()[-1:] == [
                f"overruns: 1 last message(s) over {bound} characters"]
            and [one.get("overruns") for one in rows] == [1, 0]
            and [len(one.get("finals") or []) for one in rows] == [1, 1]
            and len(text) == 2 and "· 1 overrun(s)" in text[0] and "overrun" not in text[1]):
        held("stats and exchanges say the overruns", f"run {over}: a long last message, then a short one -- stats "
             "--json overruns 1, its line after the engine's text; exchanges --json overruns [1, 0] with the finals, "
             "the text the overrun on the first line alone")
    else:
        failures.append(f"  ✗ overruns                    rc={long.returncode}/{short.returncode} stat={stat.get('overruns')!r} "
                        f"plain={plain.stdout.splitlines()[-1:]!r} rows={[one.get('overruns') for one in rows]} "
                        f"text={text!r}")
    return 0
