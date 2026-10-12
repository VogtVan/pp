"""Scenario `agent-faces` -- the JSON faces of the agents (plan ui, phase les-faces, batch
les-runs-nommes): what the post reads exists here as one object per line, beside the text.
- `status <path> --json` after two wake-ups on one run: one object per run with the state that prevails, the records summed (cost, launches, the first message, the hours), the providers' object last; the keys exactly the README's
- `name <path> <key> [<name>]`: a line to `names.jsonl`, the last one winning at `status --json` -- a name a user types,
  accents and punctuation kept as typed, its edges trimmed (agent 0.23.1); `run-unknown` and `name-invalid` (empty, two
  lines, 61 characters) refuse, nothing written
- `exchanges <path> <key> --json`: one object per exchange, the message paired with the response of its rank; a wake-up that crashed leaves a message with `response: null`
- `stats <path> <key> --json`: the engine's `-stats <key> -json` object under `conduction`, the sums beside
- `list --json`: the house (`.`, its runs of the post), then one object per agent
- the text verbs render the same bytes as before: their shape held against today's templates
- the policy (batch les-parametres-du-run): `status --json` says each run's policy (its last message's) and,
  on the last object, `last` -- the provider and the policy the agent last played, `null` for an agent never
  sent a message; `providers --json` says what each wired adapter spells, the models it names and the scope of
  its cost (`COST`, read through the engine's face; batch le-plafond-du-run); `status --json` says `budget`, null
  without a cap
- `exchanges --json` says whether each exchange was conducted (batch la-suspension-par-l-agent; a bare one says
  false, `agent-chat-json`)
- the context (batch la-part-de-pp-dans-le-contexte): `status --json` says each run's `context` {tokens, used, pp},
  `stats --json` the whole `context` -- the flow of a witness that says no event: its prompts and its answers
  (the detail is `agent-context`'s)
- the weight (batch le-poids-des-runs): `status --json` says each run's `weight` {lines, files, bytes, flow}, EQUAL
  to what `agent purge <path> <key> --json` counts without `--yes`; the last object and `list --json` their sum
"""
from __future__ import annotations

import json
import re

from conductor import adapters, install
from tests.harness import support

A = support(__file__, "agent")

STATUS_KEYS = {"agent", "run", "name", "exchanges", "state", "stack", "session", "provider", "cost_usd",
               "launches", "responses", "first_message", "first_at", "last_at", "policy", "budget", "context",
               "weight"}
TAIL_KEYS = {"agent", "providers", "last", "weight", "packages"}
WEIGHT_KEYS = {"lines", "files", "bytes", "flow"}
PROVIDER_KEYS = {"provider", "spells", "models", "cost"}
EXCHANGE_KEYS = {"agent", "run", "index", "at", "message", "response", "cost_usd", "launches", "error", "harness_rc",
                 "conducted"}
STATS_KEYS = {"agent", "run", "cost_usd", "launches", "exchanges", "conduction", "context"}
CONTEXT_KEYS = {"flow", "window", "used", "pp", "calls", "reread", "since"}
LIST_KEYS = {"agent", "runs", "running", "responses", "weight"}
STATUS_LINE = re.compile(r"^run [0-9a-f]{6} · \d+ exchange\(s\) · (parked at FINAL|standing on .+|running .+|dead .+) · "
                         r"(session \S+ \((\w+)\)|no session)$")


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
            and runs[0]["name"] == "" and runs[0]["responses"] == 2 and runs[0]["launches"] == launches
            and abs(runs[0]["cost_usd"] - sum(costs)) < 1e-6 and runs[0]["first_message"] == "hello there"
            and runs[0]["first_at"] and runs[0]["last_at"] >= runs[0]["first_at"] and runs[0]["session"]
            and runs[0]["provider"] == "harness" and runs[0]["policy"] == {"model": "m1"} and runs[0]["budget"] is None
            and set(runs[0]["context"] or {}) == {"tokens", "used", "pp"} and runs[0]["context"]["tokens"] > 0
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
            and turns[0]["response"] == "witness answer: play" and turns[1]["response"] == "witness answer: play"
            and turns[0]["cost_usd"] == costs[0] and turns[1]["cost_usd"] == costs[1]
            and turns[2]["response"] is None and turns[2]["cost_usd"] is None and turns[2]["harness_rc"] is None
            and all(one["conducted"] is True for one in turns)
            and text.returncode == 0 and text.stdout.count("\n") == 3 and "#3  " in text.stdout
            and "(no response)" in text.stdout and "#1  " in text.stdout and "-> witness answer: play" in text.stdout):
        held("exchanges pairs each message with its response", "three exchanges: two answered with their cost, the "
             "third (a crashed wake-up) with response null; the text says (no response)")
    else:
        failures.append(f"  ✗ exchanges                   rc={history.returncode} {turns} {text.stdout!r} {history.stderr[-200:]!r}")

    # --- stats: the engine's object under conduction --------------------------------------------
    measured = h.call("agent", "stats", "agents/ag1", key, "--json")
    stat = objects(measured.stdout)[0] if measured.returncode == 0 and measured.stdout.strip() else {}
    plain = h.call("agent", "stats", "agents/ag1", key)
    engine_said = h.stats(key)
    if (measured.returncode == 0 and set(stat) == STATS_KEYS and stat["run"] == key and stat["exchanges"] == 2
            and stat["launches"] == launches and abs(stat["cost_usd"] - sum(costs)) < 1e-6
            and stat["conduction"].get("exchanges") == engine_said.get("exchanges")
            and stat["conduction"].get("blocks", 0) >= 1 and "spent" in stat["conduction"]
            and stat["conduction"].get("key") == key
            and set(stat["context"] or {}) == CONTEXT_KEYS and stat["context"]["calls"] == launches
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

    # --- the text verbs keep their shape ---------------------------------------------------------
    status_text = h.call("agent", "status", "agents/ag1").stdout.splitlines()
    list_text = h.call("agent", "list").stdout
    responses_text = h.call("agent", "responses", "agents/ag1", "--last", "2").stdout.splitlines()
    messages_text = h.call("agent", "messages", "agents/ag1", "--last", "1").stdout.splitlines()
    if (len(status_text) == 3 and STATUS_LINE.match(status_text[0]) and status_text[1] == "2 response(s)"
            and status_text[2].startswith("providers: ")
            and list_text == "agents/ag1 · 1 run(s) · 0 running · 2 response(s)\n"
            and len(responses_text) == 4 and f"agents/ag1 · run {key} · #2 · rc 0" in responses_text[0]
            and responses_text[1] == "witness answer: play"
            and len(messages_text) == 2 and f"-> agents/ag1 · run {key} · policy " in messages_text[0]
            and messages_text[1] == "third, crashing"):
        held("the text verbs keep their shape", "status: the run's line, the responses, the providers; list; "
             "responses --last 2; messages --last 1 -- as before, no name in the text")
    else:
        failures.append(f"  ✗ text shape                  {status_text} {list_text!r} {responses_text} {messages_text}")

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

    return 0
