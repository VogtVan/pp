"""The verbs that read: list, status, exchanges, stats, flow, calibrate, providers, responses, messages, workdirs,
verify."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from acts.context import model_of
from acts.material import git
from faces.exchanges import (NO_MESSAGE, NO_RESPONSE, exchange_line, exchange_object, message_lines,
                             response_lines)
from faces.flow import event_line
from faces.listing import (NO_MATERIAL, agent_line, agent_object, material_line, no_agent, provider_line,
                           provider_object)
from faces.stats import fit_line, fit_object, gauged_line, gauged_object, overruns_line, stats_object
from faces.status import (no_run, run_line, run_object, status_lines, status_object, unopened_line, weight_sum,
                          paired)
from model.cost import Gauged
from model.exchange import Response
from model.policy import Policy
from model.run import Session
from model.text import first_line
from model.words import USAGE, WAIT_INTERVAL, HOUSE, FAMILY
from rules.budget import budget_of
from rules.context import weighed, context_of, gaps_of, spread, fitted
from store.adapters import declared_of
from store.houses import house, agents_of, engine_of
from store.locks import locks, mark_of, launch_of, under_way
from store.records import (session_of_run, name_of, cumuls_of, spent_of, flow_of, every_response, every_message,
                           every_session, every_workdir, answered_by, sent_to, weights_of, last_played)
from store.refusal import refuse
from store.settings import packages_of
from store.traces import faced_slots, counted_since, run_known, standing_of, spaces_of, stack_of
from verbs.asked import agent_of, json_flag, last_of, named_agent


def workdirs(rest: list[str]) -> int:
    """`agent workdirs [<path>]`: one line per material, the last state of each run's --
    the branch, the repository, the commits ahead of the base (read in the clone), clean or
    dirty, pushed or not, the run's state."""
    root, conductor = house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, _, rest = named_agent(root, conductor, rest)
    if rest:
        refuse(USAGE)
    lock, persistence = locks(conductor), conductor.persistence
    latest: dict = {}
    for one in every_workdir(root):
        if name is None or one.agent == name:
            latest[(one.agent, one.run)] = one
    if not latest:
        print(NO_MATERIAL)
        return 0
    for (agent, key), one in latest.items():
        meta = agent_of(root, conductor, agent)
        if one.state == "pruned":
            print(material_line(agent, key, one, None, None, None))
            continue
        clone = meta.parent / one.path
        ahead, dirty = None, None
        if clone.is_dir():
            counted = git("rev-list", "--count", f"{str(one.base).rsplit('@', 1)[-1]}..HEAD", cwd=clone)
            ahead = counted.stdout.strip() if counted.returncode == 0 else None
            dirty = bool(git("status", "--porcelain", cwd=clone).stdout.strip())
        if lock.held(launch_of(meta, key)):
            state = "running"
        elif not persistence.slot_of(meta, key).is_file():
            state = "gone"
        else:
            state = standing_of(conductor, meta, key)
        print(material_line(agent, key, one, ahead, dirty, state))
    return 0


def flow(rest: list[str]) -> int:
    """`agent flow <path> <key> [--exchange <n>] [--from <n>] [--follow] [--json]`: the flow the run's exchanges
    kept -- under `--json` each line as it was kept, the very object `chat --json` said; otherwise one line per
    event: the hour, the exchange, the kind (a step by its event), the first line of its text. `--exchange <n>`
    keeps the events of the n-th exchange, from its `opened` on; `--from <n>` keeps the lines from the n-th of
    the file on (the first is 1) -- what a reader that follows the flow asks again, from the rank it reached.
    `--follow` STREAMS: the lines kept so far, then each line the file gains, as it comes, until the exchange's
    `verdict` is printed, or the run's wake lock is free and nothing came for a second (a launch over, or none)
    -- what a reader that follows a launch keeps open while it plays, one process for the launch. `run-unknown`
    for a key no run wears; a run older than the keeper has no flow: nothing printed."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    following, rest = "--follow" in rest, [one for one in rest if one != "--follow"]
    wanted, start = None, 1
    for flag in ("--exchange", "--from"):
        if flag in rest:
            at = rest.index(flag)
            value = rest[at + 1] if at + 1 < len(rest) else ""
            if not value.isdigit() or int(value) < 1:
                refuse(USAGE)
            if flag == "--exchange":
                wanted = int(value)
            else:
                start = int(value)
            del rest[at:at + 2]
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    path = flow_of(root, name, key)
    if not path.is_file() and not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    current = None
    rank, line = 0, 0                               # the n-th `opened` of the flow: the rank `exchanges` gives the
    lock = locks(conductor)                         # message, never the exchange number the run counts

    def said(event: dict) -> None:
        nonlocal current, rank
        if event.get("kind") == "opened":
            rank += 1
            current = rank
        if (wanted is not None and current != wanted) or line < start:
            return
        if as_json:
            print(json.dumps(event, ensure_ascii=False), flush=True)
            return
        print(event_line(event, current), flush=True)

    offset, rest_bytes, quiet = 0, b"", 0.0
    while True:
        gained = b""
        if path.is_file():
            with path.open("rb") as handle:
                handle.seek(offset)
                gained = handle.read()
            offset += len(gained)
        rest_bytes += gained
        *whole, rest_bytes = rest_bytes.split(b"\n")
        ended = False
        for raw in whole:
            if not raw.strip():
                continue
            try:
                event = json.loads(raw.decode("utf-8", "replace"))
            except ValueError:
                continue
            line += 1
            said(event)
            ended = ended or (event.get("kind") == "verdict" and line >= start)
        if not following or ended:
            return 0
        quiet = 0.0 if gained else quiet + WAIT_INTERVAL
        if quiet >= 1.0 and not lock.held(launch_of(meta, key)):
            return 0                                # no launch plays and nothing comes: the stream is over
        time.sleep(WAIT_INTERVAL)


def verify(rest: list[str]) -> int:
    """`pp-agent verify` (the vector on stdin): the VERIFIER of the family `agent-run:<path>/<key>`, the
    engine's call -- rc 0 when the house or the agent keeps something of the run (a line of the records,
    a file of the engine, its flow), `run-unknown` otherwise; a family this package does not declare is not
    its to judge (`family-foreign`). Reads only."""
    if rest:
        refuse(USAGE)
    root, conductor = house()
    prefix, _, ident = conductor.reading.piped().strip().partition(":")
    if prefix != FAMILY:
        refuse(f"family-foreign -- `{prefix}:` is not a family agent declares ({FAMILY}); its owner verifies it.")
    path, _, key = ident.rpartition("/")
    if not path or not key:
        refuse(f"run-unknown -- `{ident}`: a run is named `<path>/<key>`.")
    name, meta, _ = named_agent(root, conductor, [path])
    weight = weights_of(conductor, root, name, meta, [key])[key]
    if not (weight["lines"] or weight["files"] or weight["flow"] is not None):
        refuse(f"run-unknown -- no run `{key}` of {name}.")
    return 0


def listing(rest: list[str]) -> int:
    root, conductor = house()
    as_json, rest = json_flag(rest)
    if rest:
        refuse(USAGE)
    found = agents_of(root, conductor)
    if not found and not as_json:
        print(no_agent(str(root.parent)))
        return 0
    responses = every_response(root)
    lock = locks(conductor)
    for name, meta in ([(HOUSE, root)] if as_json else []) + found:   # the house heads the face, never the text
        slots = faced_slots(conductor, meta)
        running = len(under_way(lock, conductor.persistence, meta))
        answered = len([one for one in responses if one.agent == name])
        if as_json:
            keys = [conductor.persistence.run_id_of(slot) for slot in slots]
            weight = weight_sum(list(weights_of(conductor, root, name, meta, keys).values()))
            print(json.dumps(agent_object(name, len(slots), running, answered, weight)))
            continue
        print(agent_line(name, len(slots), running, answered))
    return 0


def providers(rest: list[str]) -> int:
    """`agent providers [--json]`: each provider the house is wired with, what its adapter SPELLS
    of a policy, the MODELS it names and the scope of the COST it reads -- read from the adapter
    itself (`SPELLS`, `MODELS`, `COST` of its `wire.py`, loaded by the engine's face); one line each,
    or one object `{provider, spells, models, cost}` under `--json`; nothing when the house is wired
    with none."""
    root, conductor = house()
    as_json, rest = json_flag(rest)
    if rest:
        refuse(USAGE)
    for provider in conductor.install.wired_providers(root.parent):
        try:
            wire = conductor.adapters.load(provider, root)
        except conductor.Refusal as refusal:
            refuse(str(refusal))
        spells, models = list(getattr(wire, "SPELLS", ())), list(getattr(wire, "MODELS", ()))
        cost = getattr(wire, "COST", None)
        if as_json:
            print(json.dumps(provider_object(provider, spells, models, cost)))
            continue
        print(provider_line(provider, spells, models, cost))
    return 0


def status(rest: list[str]) -> int:
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    if rest:
        refuse(USAGE)
    persistence, lock = conductor.persistence, locks(conductor)
    slots = faced_slots(conductor, meta)
    if not slots and not as_json:
        print(no_run(name))

    def dead(key: str) -> bool:
        """The last launch of `key` is over and added no response: its mark says how many stood."""
        launched = mark_of(lock, meta, key).responses
        return launched is not None and len(answered_by(root, name, key)) <= launched

    sent = [one for one in every_message(root) if one.to == name]
    answered = [one for one in every_response(root) if one.agent == name]

    def policy_of_run(key: str) -> Policy:
        """-> the policy of the run's last message, none named when none was sent."""
        found = [one for one in sent if one.run == key]
        return found[-1].policy if found else Policy()

    latest: dict[str, str] = {}                    # the hour of each run's last line, either record
    for one in sent + answered:
        if one.run and one.at:
            latest[one.run] = max(latest.get(one.run, ""), str(one.at))
    slots = sorted(slots, key=persistence.run_id_of)
    slots.sort(key=lambda slot: latest.get(persistence.run_id_of(slot), ""), reverse=True)   # the last spoken first

    windows: dict = {}                             # what the adapters declare, loaded once per provider
    state_dir = meta / persistence.DIRECTORY
    standing = {persistence.run_id_of(one) for one in persistence.slots(meta)}
    lone = [path.name.removeprefix("session-").split(".", 1)[0]
            for path in (sorted(state_dir.glob("session-*.wake.lock")) if state_dir.is_dir() else [])]
    weights = (weights_of(conductor, root, name, meta,
                          list(dict.fromkeys([persistence.run_id_of(slot) for slot in slots] + lone)))
               if as_json else {})
    faced_keys: list[str] = []

    def faced(key: str, exchanges: int, state: str, stack: str, known: Session | None, awaits: str,
              packages: list[dict] | None = None, documents: str | None = None) -> None:
        """One run read for the face (`run_object`) and printed: its records summed, its policy, its budget under
        a cap, its context, beside what the caller read of its slot."""
        rows, since = counted_since(conductor, meta, key, answered_by(root, name, key))
        context = context_of(rows, model_of(conductor, root, name, key, windows), None, since)
        policy = policy_of_run(key)
        budget = budget_of(policy, spent_of(root, name, key))
        print(json.dumps(run_object(name, key, name_of(root, name, key), exchanges, state, awaits, stack,
                                    spaces_of(conductor, meta, key), known, cumuls_of(root, name, key), policy, budget,
                                    context, packages, weights[key], documents), ensure_ascii=False))
        faced_keys.append(key)

    for slot in slots:
        key = persistence.run_id_of(slot)
        resting, stack = standing_of(conductor, meta, key), stack_of(conductor, meta, key)
        awaits = "message" if resting == "parked" else "production"
        state = resting
        if lock.held(launch_of(meta, key)):    # the wake lock IS the state: a wake-up plays
            state = "running"
        elif dead(key):
            state = "dead"
        known = session_of_run(root, name, key)
        if as_json:
            rooted = persistence.documents_of(slot)
            faced(key, persistence.turns_of(slot), state, stack, known, awaits, packages_of(conductor, meta, key),
                  str(Path(rooted).resolve()) if rooted else None)
            continue
        print(run_line(key, persistence.turns_of(slot), state, resting, stack, known))
    for path in sorted(state_dir.glob("session-*.wake.lock")) if state_dir.is_dir() else []:
        key = path.name.removeprefix("session-").split(".", 1)[0]    # a launch whose agent opened no run
        if key in standing:
            continue
        if lock.held(path):
            if as_json:
                faced(key, 0, "running", "", None)
                continue
            print(unopened_line(key, "running"))
        elif dead(key):
            if as_json:
                faced(key, 0, "dead", "", None)
                continue
            print(unopened_line(key, "dead"))
    wired = conductor.install.wired_providers(root.parent)
    if as_json:
        print(json.dumps(status_object(name, wired, last_played(root, name, sent),
                                       weight_sum([weights[key] for key in faced_keys]),
                                       packages_of(conductor, meta, None)), ensure_ascii=False))
        return 0
    for line in status_lines(len(answered), wired):
        print(line)
    return 0


def exchanges(rest: list[str]) -> int:
    """`exchanges <path> <key> [--json]`: the run's history -- its messages in order, each paired with
    the response that answers it, by the hour of the two records (`paired`), `null` when none came."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    if not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    sent = sent_to(root, name, key)
    answered = paired(sent, answered_by(root, name, key))
    for number, message in enumerate(sent, 1):
        if as_json:
            response = answered[number] if number in answered else Response()   # none: every field unnamed
            print(json.dumps(exchange_object(name, key, number, message, response), ensure_ascii=False))
            continue
        print(exchange_line(number, message, answered[number] if number in answered else None))
    return 0


def stats(rest: list[str]) -> int:
    """`stats <path> <key> [--json]`: the detail of the run's conduction, as the engine's own
    `-stats <key>` renders it on the agent's instance -- relayed, never recomputed --, then the overruns its
    records sum; under `--json` the records' sums and the run's object under `conduction`."""
    root, conductor = house()
    name, meta, rest = named_agent(root, conductor, rest)
    as_json, rest = json_flag(rest)
    if len(rest) != 1 or rest[0].startswith("--"):
        refuse(USAGE)
    key = rest[0]
    if not run_known(conductor, meta, key):
        refuse(f"run-unknown -- no run `{key}` at {name} (`./pp agent status {name}` lists them).")
    played = subprocess.run([sys.executable, str(engine_of(conductor, root)), "--instance", str(meta), "-stats", key]
                            + (["-json"] if as_json else []), stdin=subprocess.DEVNULL, capture_output=True,
                            text=True, cwd=root.parent)
    if not as_json:
        sys.stdout.write(played.stdout)
        sys.stderr.write(played.stderr)
        if played.returncode == 0:
            print(overruns_line(cumuls_of(root, name, key)))
        return played.returncode
    try:
        runs = json.loads(played.stdout).get("runs") or []
    except (ValueError, AttributeError):
        refuse(f"stats-unreadable -- the engine's `-stats {key} -json` rendered no JSON: {first_line(played.stderr)}")
    slot = conductor.persistence.slot_of(meta, key)
    summed = cumuls_of(root, name, key)
    conduction = runs[0] if runs else {}
    rows, since = counted_since(conductor, meta, key, answered_by(root, name, key))
    context = context_of(rows, model_of(conductor, root, name, key), conduction.get("tokens"), since)
    print(json.dumps(stats_object(name, key, summed, conductor.persistence.turns_of(slot), conduction, context),
                     ensure_ascii=False))
    return 0


def calibrate(rest: list[str]) -> int:
    """`calibrate [<path> ...] [--json]`: the estimate of a run's context against what the provider's own store
    measured, for every run of the agents named -- every agent and the house without a path. Per run: its
    provider, `calls` and `compactions` as the store of its session keeps them (`conductor.adapters.contexts`),
    `measured` the context its last call sent, `estimate` -- `flow`, the flow summed as the engine counts it, and
    `calibrated`, the adapter's base plus the flow weighed by its constants -- and each one's `gap` to the measure;
    `measured: null` where the store says nothing (a caller's command, an adapter that cannot read its store, a
    session it no longer holds). Then one object per provider with a measured run: the `runs`, those `compacted`,
    the two estimates' gaps (median, p10, p90), what the adapter `declared` and the constants `fitted` on its runs
    without a compaction. Writes nothing."""
    root, conductor = house()
    as_json, rest = json_flag(rest)
    if any(one.startswith("--") for one in rest):
        refuse(USAGE)
    paths = rest or [HOUSE] + [path for path, _ in agents_of(root, conductor)]
    sessions = every_session(root)
    lines, by_provider, cache = [], {}, {}
    for path in paths:
        name, meta, _ = named_agent(root, conductor, [path])
        for key in dict.fromkeys(one.run for one in sessions if one.agent == name and one.run):
            known = session_of_run(root, name, key)
            provider, session = (known.provider, known.session) if known is not None else (None, None)
            rows, _ = counted_since(conductor, meta, key, answered_by(root, name, key))
            flows = [one.flow for one in rows if one.flow is not None]
            store = conductor.adapters.contexts(provider, meta, session, None) if provider and session else None
            calls = store["calls"] if store else None
            compactions = store["compactions"] if store else None
            measured = calls[-1] if calls else None
            flow = sum(one.total() for one in flows)
            thinking = sum(int(one.thinking or 0) for one in flows)
            declared = declared_of(conductor, root, provider, cache)
            calibrated = round(declared.base + sum(weighed(one, declared) for one in flows))
            gaps = gaps_of(flow, calibrated, measured)
            lines.append((name, key, provider, session, len(calls) if store else None, compactions, measured,
                          flow, calibrated, gaps))
            if measured and flows:
                by_provider.setdefault(provider, []).append((gaps, compactions, Gauged(
                    first=calls[0], last=measured, flow=flow, thinking=thinking)))
    summaries = []
    for provider, measured in by_provider.items():
        declared = declared_of(conductor, root, provider, cache)
        clean = [(gaps, run) for gaps, compactions, run in measured if not compactions]
        fit = fitted([run for _, run in clean])
        summaries.append((provider, len(measured), len(measured) - len(clean),
                          spread([gaps[0] for gaps, _ in clean]), spread([gaps[1] for gaps, _ in clean]),
                          declared, fit))
    if as_json:
        for one in lines:
            print(json.dumps(gauged_object(*one), ensure_ascii=False))
        for one in summaries:
            print(json.dumps(fit_object(*one), ensure_ascii=False))
        return 0
    for name, key, provider, _, calls, compactions, measured, flow, calibrated, gaps in lines:
        print(gauged_line(name, key, provider, calls, compactions, measured, flow, calibrated, gaps))
    for one in summaries:
        print(fit_line(*one))
    return 0


def responses(rest: list[str]) -> int:
    root, conductor = house()
    name, count = last_of(rest)
    if name is not None:
        named_agent(root, conductor, [name])
    found = [one for one in every_response(root) if name is None or one.agent == name]
    if not found:
        print(NO_RESPONSE)
        return 0
    for one in list(reversed(found))[:count]:
        for line in response_lines(one):
            print(line)
    return 0


def messages(rest: list[str]) -> int:
    root, conductor = house()
    name, count = last_of(rest)
    if name is not None:
        named_agent(root, conductor, [name])
    found = [one for one in every_message(root) if name is None or one.to == name]
    if not found:
        print(NO_MESSAGE)
        return 0
    for one in list(reversed(found))[:count]:
        for line in message_lines(one):
            print(line)
    return 0
