"""ONE exchange of a message with an agent, conducted by the house: the opening or the resume, the loop of its launches,
the records written."""
from __future__ import annotations

import os
import re
import shlex
import shutil
from dataclasses import replace
from pathlib import Path

from acts.context import windowed
from acts.flow import step_sayer, keeper, followed, waited, hearer, Flow
from acts.launch import unmeasured, policy_of, bounds_of, compose, harness_environment, conducted, principal_line, reported
from acts.material import base_of, planned, placed, shipped
from acts.mounts import verified, mounted, released
from acts.refusal import ruled
from model.exchange import Account, Footing, Issue, Message, Response, Terms
from model.policy import Asked
from model.refusal import VectorRefused, Unserved, WorkFailure
from model.run import Session, Traced
from model.words import RESPONSES, MESSAGES, SESSIONS, HEAD, TOO_LONG
from rules.budget import budget_of, costed, limiter
from rules.houses import identity_of
from rules.passage import composed, spoke, message_head, served_of, asks, headed
from rules.policy import grammar_of, provider_of
from rules.refusals import refusal_of
from rules.resume import documents_judged, resumable, standing_material
from rules.switches import packages_line
from rules.verdict import reason_of
from store.adapters import cost_scope, launcher_cap, spells_of, receipted, read_answer
from store.clock import now
from store.houses import wired_of, documents_asked, refusal_line
from store.locks import locks, marked, standing_mark, interrupted_mark, mark_of, launch_of, under_way
from store.records import (record, append, session_of_run, spent_of, resume_of, vectors_due, vectors_kept,
                           answered_by, material_kept)
from store.refusal import refuse
from store.settings import mounts_of, cap_of, packages_of
from store.traces import standing_of, stack_of, tracing, documents_kept, refusal_traced, captures

VECTOR_REFUSED = "vector-refused"   # the ONE code every refusal of a vector says to who launched: its cause in the detail
UNSERVED = "first-prompt-unserved"   # the code of the `refused` event when the bare call does not serve the first prompt

PARENTHESIS = "[your principal has suspended conduction for this exchange, the run resumes at their word]"
# opens the prompt of an exchange the house does not conduct (`conduct off`), before the heads

KEY_LINE = re.compile(r"^▌ pp · run ([0-9a-f]{6})")   # the first line of every output of the engine


def opened(conductor, root: Path, meta: Path, message: str, door: str | None,
           documents: str | None = None, marble: bool = False, cap: int | None = None,
           packages: str | None = None, hold: bool = False) -> tuple[str, str]:
    """-> (the key, the first output) of the run `-new "<message>"` opened by the principal on the
    agent's instance -- the key read on the output's first line; `packages` rides `PP_PACKAGES`, so the
    first block is composed as the switches say. A `-new` the engine refuses (`door-unknown`,
    `documents-unknown`, `packages-invalid`) launches nothing and leaves no run. `hold`:
    the output waits at the run, open, for the mounts that follow -- the call prints the output's heading, where
    the key is read, and one line."""
    played = conducted(conductor, root, meta, "-new", message, door=door, documents=documents, marble=marble, cap=cap,
                       packages=packages, hold=hold)
    found = KEY_LINE.match(played.stdout)
    if played.returncode != 0 or found is None:
        refuse(f"{refusal_of(refusal_line(), played) or 'the opening gave no key'} -- nothing launched, no run opened")
    return found.group(1), played.stdout


def served(conductor, root: Path, meta: Path, key: str, say, saying: bool, marble: bool = False,
           cap: int | None = None) -> str | None:
    """The principal's bare call on a run the harness just left: it serves the output the agent's
    value call HELD, or the chunk waiting, or makes the run advance -- the engine alone judges
    which. -> what the engine printed, the next prompt; None when it refused (the repair bound,
    a run complete), the refusal said."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    what = ("served held output" if persistence.held_of(slot) else
            "served chunk" if persistence.pending_of(slot) else "advanced")
    played = conducted(conductor, root, meta, key, marble=marble, cap=cap)
    if played.returncode != 0 or not played.stdout.strip():
        why = refusal_of(refusal_line(), played)
        if saying:
            say(key, f"refused {why or 'nothing'}", "refusal", {"detail": why})
        return None
    if saying:
        say(key, what, "advanced" if what == "advanced" else "served", {"what": what})
    return played.stdout


def resumed(conductor, root: Path, meta: Path, key: str, message: str, marble: bool = False,
            pending: str | None = None, cap: int | None = None, hold: bool = False) -> tuple[str, bool]:
    """-> (the first output a resume serves, whether the run was STANDING). A run parked (its passage
    over), or renewed by an upgrade: the principal's `<key> "<message>"` opens the exchange (traced
    `prompt`; a renewed run reopens under its key). A run standing mid-exchange: the output its last
    wake-up kept `pending` -- served by the engine, launched on by nobody: the bound was spent -- as it
    is, no call made; else what it holds or the chunk waiting, by the principal's bare call; else -- a
    wake-up died in its loop -- the block that stands, by `-peek`. `hold` (vectors are mounted next): ONE path,
    parked or standing -- the principal's message under the hold opens the exchange and the engine renders nothing:
    the passage of a parked run, nothing more on a run that stands; the output served is empty, the bare call
    that follows the mounts renders the first prompt (`released`). A message the engine refuses under the hold
    raises `Unserved`: nothing is mounted nor launched."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    waiting = bool(persistence.held_of(slot) or persistence.pending_of(slot))
    parked = persistence.renewed(slot) is not None or (standing_of(conductor, meta, key) == "parked" and not waiting)
    if hold:
        played = conducted(conductor, root, meta, key, message, marble=marble, cap=cap, hold=True)
        if played.returncode != 0:
            raise Unserved(f"{refusal_of(refusal_line(), played) or f'the message that opens the exchange of run {key} exited {played.returncode} without a word'} -- nothing mounted, nothing launched; `--run {key}` takes the run up", refusal_of(refusal_line(), played))
        return "", not parked
    if parked:
        return conducted(conductor, root, meta, key, message, marble=marble, cap=cap).stdout, False
    if pending:
        return pending, True
    if waiting:
        return conducted(conductor, root, meta, key, marble=marble, cap=cap).stdout, True
    return conducted(conductor, root, meta, key, "-peek", marble=marble, cap=cap).stdout, True


def strays_of(persistence, meta: Path, known: set, key: str, say, saying: bool) -> list[str]:
    """-> the runs born at the agent since `known` but `key`: STRAY runs -- a `-new` the harness
    typed at the parked run --, each said; `known` grows with them."""
    found = sorted({persistence.run_id_of(one) for one in persistence.slots(meta)} - known - {key})
    for stray in found:
        known.add(stray)
        if saying:
            say(key, f"stray run {stray}", "stray", {"run": stray})
    return found


def counted(loop, conductor, *rest, **named) -> Account:
    """-> the account `loop` renders of ONE exchange, with what its flow summed and said when the loop ended:
    the sums frozen, the words and the finals in their order. The loop hears the launches through the `Flow` it is handed."""
    flow = Flow(conductor.metrics.tokens)
    done = loop(flow, conductor, *rest, **named)
    return replace(done, flow=flow.summed(), tokens_sent=flow.sent(), words=tuple(flow.words),
                   finals=tuple(flow.finals))


def unconducted(flow: Flow, conductor, root: Path, meta: Path, key: str, head: list[str], provider: str | None, grammar: str,
                limit, session: str | None, material: dict | None, identity: dict, message: str,
                neighbours: list, log, beat: int, say, cumul: float | None, scope: str | None, exchange_no: int = 0,
                after: bool = False, before=None, overrun: bool = False) -> Account:
    """An exchange the house does NOT conduct (`conduct off`): ONE launch of the harness on its
    session, the prompt opening on `PARENTHESIS`, then the message under its head (`after`: the
    interruption's head before it) and nothing
    of pp -- no call of pp before, during or after; the answer read as `exchanged` reads it, its
    cost read in the adapter's scope (`costed`); the launch's policy is `limit`'s (`limiter`), none
    left and nothing is launched. The run stays where it stands. `before(key)`, when a conversation
    gives it, plays ahead of the launch. `overrun`: the last launch of the run's exchange before held a last message
    over `ANSWER_BOUND` -- the prompt opens on `TOO_LONG`. -> the account `exchanged` renders."""
    done = Account(launches=1, session_cost_usd=cumul, session=session)
    launched = limit(None)
    if launched is None:
        return replace(done, launches=0, budget_spent=True)
    if before is not None:
        before(key, say)
    prompt = headed(f"{PARENTHESIS}\n{message_head(after)}\n{message}", neighbours)
    prompt = f"{TOO_LONG}\n\n{prompt}" if overrun else prompt
    flow.launch(prompt, "")
    argv, env, stdin = compose(conductor, root, meta, head, provider, prompt, launched, session, material)
    environment = harness_environment(env, key)
    environment.update(identity)
    listened = hearer(conductor, meta, grammar, key, say, exchange_no, 1, flow,
                      windowed(conductor, root, provider, launched))
    try:
        played = waited(argv, meta.parent, environment, None, key, beat, say, log, stdin, heard=listened)
    except KeyboardInterrupt:
        listened.cut()                             # the texts said before the interruption stay in the flow
        return replace(done, interrupted=True)
    listened.end()
    done = done.ended(played.returncode, played.stderr)
    if played.returncode != 0 and not played.stdout.strip():
        return done
    read = read_answer(conductor, meta, grammar, played)
    launch_cost, summed = costed(scope, read.cost_usd, cumul)
    say(key, "", "agent", {"exchange": exchange_no, "launch": 1, "cost_usd": launch_cost})
    return replace(done, session=read.session, session_cost_usd=summed, cost_usd=launch_cost,
                   denials=read.denials, answered=read)


def exchanged(flow: Flow, conductor, root: Path, meta: Path, key: str, head: list[str], provider: str | None, grammar: str,
              limit, session: str | None, material: dict | None, identity: dict, message: str | None, output: str,
              neighbours: list, trace, log, beat: int, say, bound: int, cumul: float | None, scope: str | None,
              exchange_no: int = 0, after: bool = False, before=None, marble: bool = False,
              cap: int | None = None, overrun: bool = False) -> Account:
    """The LOOP of one exchange: the harness launched on the prompt -- the first time the message
    under its head (`after`: the interruption's head before it) then `output`, pp's first output;
    then pp's outputs alone --, in the session the
    first launch opened; after each launch the run is read: an output held, a chunk waiting or a
    block to advance -> this script's bare call, and the harness again on what came back;
    parked at its AWAIT with nothing held -> over, the words of the launches are the response.
    Every step is `say`d while the trace is followed; two VOICES are said at every launch whatever
    the trace -- `conduction`, pp's output served to the harness, alone; `agent`, the launch's end and
    its cost, no text (the model's text is its `words` and its asides) --, which a flow renders and a wake-up watched from stderr leaves unsaid.
    Before every launch `limit` (`limiter`) gives its policy, the run's remainder in it: none left, the
    loop stops there (`budget_spent`), the last response kept. The bound of launches is judged after the
    advance that follows a launch: spent, with an output served that asks something, that output is
    the prompt the next wake-up of the run owes its launch -- kept as `pending`, never served to
    nobody.
    -> the ACCOUNT of its launches (`Account`), a copy at each step: the cost the SUM of the launches' costs, each read in the adapter's scope (`costed`);
    `interrupted` when a SIGINT ended the launch under way -- the harness terminated, what the
    finished launches answered kept, the run left where it stands. `before(key)`, when a conversation
    gives it, plays ahead of every launch -- `run` gives none. A launch whose last message held more than
    `ANSWER_BOUND` characters -- or, by `overrun`, the last launch of the run's exchange before -- opens the next
    prompt on `TOO_LONG`, its first line, once."""
    persistence = conductor.persistence
    slot = persistence.slot_of(meta, key)
    saying = trace is not None
    known = {persistence.run_id_of(one) for one in persistence.slots(meta)}
    done = Account(session_cost_usd=cumul, session=session)
    kept: list[dict] = []                          # the trace's events since the conduction said last
    taken = captures(conductor, meta, key)         # the productions pp takes during this exchange, read at the trace
    first = True
    while True:
        if done.launches >= bound:
            return replace(done, spent=True)
        launched = limit(done.cost_usd)
        if launched is None:                       # the run's cap leaves nothing: no launch more
            return replace(done, budget_spent=True)
        if before is not None:
            before(key, say)
        prompt = headed(f"{message_head(after)}\n{message}\n\n{output}" if message is not None else output,
                        neighbours) if first else output
        prompt, overrun = (f"{TOO_LONG}\n\n{prompt}" if overrun else prompt), False
        argv, env, stdin = compose(conductor, root, meta, head, provider, prompt, launched, done.session, material)
        environment = harness_environment(env, key)
        environment.update(identity)
        done = replace(done, launches=done.launches + 1)
        flow.launch(prompt, output)
        if saying:
            followed(trace, log, key, say, kept)
        say(key, "", "conduction", {"exchange": exchange_no, "launch": done.launches, "text": output,
                                    **served_of([Traced.of(one) for one in kept] if saying else None, output)})
        kept.clear()
        listened = hearer(conductor, meta, grammar, key, say, exchange_no, done.launches, flow,
                          windowed(conductor, root, provider, launched), taken)
        try:
            played = waited(argv, meta.parent, environment, trace, key, beat, say, log, stdin, kept, listened)
        except KeyboardInterrupt:                  # the harness ended with the interruption: the loop stops here,
            listened.cut()                         # what it said and handed before it stays in the flow
            return replace(done, interrupted=True)
        listened.end()
        overrun = any(one.over() for one in flow.finals if one.launch == flow.launches)
        done = done.ended(played.returncode, played.stderr)
        first = False
        done = replace(done, strays=done.strays + tuple(strays_of(persistence, meta, known, key, say, saying)))
        if played.returncode != 0 and not played.stdout.strip():
            return done
        read = read_answer(conductor, meta, grammar, played)   # no identity: nothing kept, said
        launch_cost, summed = costed(scope, read.cost_usd, done.session_cost_usd)
        done = replace(done, session=read.session, session_cost_usd=summed,
                       cost_usd=(done.cost_usd if launch_cost is None
                                 else round(float(done.cost_usd or 0.0) + launch_cost, 6)),
                       denials=done.denials + read.denials, answered=read)
        say(key, "", "agent", {"exchange": exchange_no, "launch": done.launches, "cost_usd": launch_cost})
        if saying:
            say(key, f"launch {done.launches} · {len(stdin)} chars"
                + (f" · {launch_cost:g} USD" if launch_cost is not None else ""), "launch",
                {"launch": done.launches, "chars": len(stdin), "cost_usd": launch_cost})
        if played.returncode != 0 or read.stop is not None:   # a provider's stop: no launch after it here
            return done
        if (not persistence.held_of(slot) and not persistence.pending_of(slot)
                and standing_of(conductor, meta, key) == "parked"):
            return done
        output = served(conductor, root, meta, key, say, saying, marble, cap)
        if output is None:
            return done
        if (not asks(output) and not persistence.held_of(slot) and not persistence.pending_of(slot)
                and standing_of(conductor, meta, key) == "parked"):
            # the output served parks the run and asks the agent nothing -- the bare AWAIT after a
            # judged proof: launching the harness on it would buy a message nobody owes. The
            # exchange is over, its words are the response; a conduction event is a
            # launch's, and this output was served to nobody
            return done
        if done.launches >= bound:
            # the bound is spent and the output served asks something: it is the PROMPT the next
            # wake-up of the run owes its launch -- kept with the response (`pending`), never served
            # to nobody; the run stands on the step it asks
            return replace(done, spent=True, pending=output)


def vector_refused(conductor, root: Path, name: str, asked: Asked, key: str | None, given, refusal: VectorRefused,
                   held=None, where: str = "") -> None:
    """A vector refused, under the ONE code a caller reads (`vector-refused`), its cause first in the
    detail: the `refused` event -- kept in the run's flow when a run stands --, the lock this call took
    given back, then the refusal on stderr: nothing mounted, nothing kept, nothing launched. `given` is the
    caller's own `say`, None for the engine's on stderr."""
    detail = f"{refusal.cause} -- {refusal.detail}"
    teller = keeper(root, name, given if given is not None else step_sayer(tracing(conductor), asked.json))
    teller(key or "", f"refused {VECTOR_REFUSED} · {refusal.cause}", "refused",
           {"code": VECTOR_REFUSED, "vector": refusal.vector, "detail": detail})
    if held is not None:
        locks(conductor).release(held)
    refuse(f"{VECTOR_REFUSED} -- {refusal.vector}: {detail} -- nothing launched{where}")


def unserved(conductor, root: Path, name: str, asked: Asked, key: str | None, given, failure: Unserved,
             held=None) -> None:
    """The first prompt was not served: a `refused` event `{code: first-prompt-unserved, detail}` -- the
    detail what the engine said -- kept in the run's flow, the lock this call took given back, then the
    refusal on stderr; nothing is launched."""
    teller = keeper(root, name, given if given is not None else step_sayer(tracing(conductor), asked.json))
    teller(key or "", f"refused {failure.detail or 'nothing'}", "refused",
           {"code": UNSERVED, "detail": failure.detail})
    if held is not None:
        locks(conductor).release(held)
    refuse(str(failure))


def judged(conductor, root: Path, name: str, meta: Path, asked: Asked, key: str | None, message: str | None,
           lease, say, waiting: dict | None, headless: bool) -> tuple[Issue | None, Terms | None, object, object]:
    """The JUDGMENTS of one exchange, every one before the launch: the harness, the policy, the run, its
    session, its material, the composed line. The launcher's lock of a resume is taken here when the caller
    holds none (`run-busy`); a refusal met here gives a lock taken here back and leaves the run as it was. The
    VECTORS of the run -- the ones it keeps, then the `--vector` of this wake-up -- are judged before anything
    (`mounts_of`), at a resume every one verified before the message; a vector refused launches nothing: a
    `refused` event, then the refusal on stderr. -> (an ISSUE when the exchange is over already -- the run's
    cap reached: nothing launched, nothing recorded; `dry` alone for a dry run: said, nothing opened --, else
    None; the TERMS the judgments settled; the launcher's lock; `limit`, which gives the policy of the next
    launch). `say` is the caller's own, None for the engine's on stderr."""
    instance, persistence = conductor.instance, conductor.persistence
    bare = asked.conduct is False and key is not None   # `conduct off`: one launch, no call of pp
    policy = policy_of(conductor, asked)
    beat, bound = bounds_of(asked)
    # the harness first: a refusal writes nothing
    head, provider = ruled(provider_of, asked, wired_of(conductor, root))
    grammar = grammar_of(asked, provider)
    refused = unmeasured(conductor, root, asked, policy)
    marble = receipted(conductor, root, meta, head, provider, policy)   # the receipt the launch declares
    if refused is not None:
        refuse(refused)
    try:
        scope = cost_scope(conductor, root, grammar)
        cap = launcher_cap(conductor, root, grammar, policy)   # the cap of the outputs served at the prompt
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    opening = key is None
    if asked.door is not None and not opening:
        refuse("door-on-resume -- a door opens a run's FIRST exchange; a resume continues the conversation.")
    documents = documents_asked(root, asked)
    lock = locks(conductor)
    if not opening and not persistence.slot_of(meta, key).is_file():
        refuse(f"run-unknown -- no run `{key}` at {meta}.")
    ruled(documents_judged, key, *documents_kept(conductor, meta, key, documents))
    if not asked.dry_run and message is None and not headless:   # judged before anything is opened
        refuse("message-missing -- a wake-up carries a message: it is the harness's prompt, as a message "
               "typed in a session.")
    spent = spent_of(root, name, key)
    try:                                           # the adapter's spelling is read under a cap alone
        spells = spells_of(conductor, root, provider) if budget_of(policy, spent) is not None else ()
    except conductor.Refusal as refusal:
        refuse(str(refusal))
    limit = limiter(policy, spent, spells)
    if limit(None) is None:                        # the cap reached: nothing launched, nothing recorded
        said = budget_of(policy, spent)
        reason = (f"budget-spent -- run {key} spent {said.spent:g} USD of its {said.cap:g} USD cap: nothing "
                  f"launched, the run as it was -- raise the cap (`--max-budget-usd`, a `set`) to go on")
        if asked.dry_run:
            refuse(reason)
        return (Issue(key=key, reason=reason, account=Account(budget_spent=True),
                      exchanges=persistence.turns_of(persistence.slot_of(meta, key)), bound=bound, budget=said),
                None, lease, None)
    slug = str(instance.read(root).get("slug", ""))
    taken = False                                  # the launcher's lock, when this call takes it itself
    if lease is None and not opening and not asked.dry_run:
        lease = lock.try_(launch_of(meta, key))
        if lease is None:
            refuse(f"run-busy -- a wake-up plays run {key}: one wake-up at a time on a run.")
        taken = True
    work = Path(asked.work).resolve() if asked.work is not None else None
    shown = message if message is not None else ("" if headless else "<the message>")
    try:                                           # every judgment before the opening and the launch: a
        try:                                       # refusal here leaves the run as it was, and opens none
            due = [] if bare else vectors_due(root, name, key, asked)
            mounts = mounts_of(conductor, meta, key, waiting, due)
            if not opening:                        # a resume: EVERY vector verified before any is mounted
                verified(conductor, meta, key, waiting, mounts)
        except VectorRefused as refusal:           # the run's vectors: a form, a family the run does not play,
            vector_refused(conductor, root, name, asked, key, say, refusal)   # an address its family's verifier refuses
        if opening:
            session = None
        elif lease is not None and not taken and session_of_run(root, name, key) is None:
            session = None                         # the caller's own run, no launch of it ever answered: a fresh session
        else:
            session = ruled(resumable, key, str(meta), *resume_of(conductor, root, meta, name, key), provider)
        entry = None
        try:
            if not opening:
                entry = standing_material(name, key, *material_kept(root, name, meta, key))
                if work is not None and entry is not None:
                    raise WorkFailure(f"work-standing -- run {key} has its material already ({entry.path} of "
                                      f"{entry.repo}): one run, one material.")
            if work is not None and entry is None:
                base_of(work, asked.base)       # a repository that cannot be cloned refuses now: no run opened
                entry = planned(name, key or "<key>", work, asked.base)
        except WorkFailure as failure:
            refuse(str(failure))
        material = entry.where() if entry is not None else None
        preview = headed(f"{HEAD}\n{shown}\n\n<the output of ./pp {'-new' if opening else key}>",
                         under_way(lock, persistence, meta, key))
        argv, env, stdin = compose(conductor, root, meta, head, provider, preview, limit(None), session, material)
    except SystemExit:
        if taken:
            lock.release(lease)
        raise
    identity = identity_of(name, slug) if material is not None else {}
    packages = packages_line(waiting) if opening else None   # the opening's composition, the switches waiting
    if asked.dry_run:
        print(f"pp-agent: dry run -- {name} · cwd {meta.parent} · nothing launched, no run opened")
        print(principal_line(conductor, root, meta, *(["-new", shown] if opening else [key, shown]),
                             door=asked.door if opening else None,
                             documents=documents if opening else None, marble=marble, cap=cap, packages=packages,
                             hold=bool(mounts)))
        print(shlex.join(argv))
        for one, value in {**env, **identity}.items():
            print(f"  env {one}={value}")
        for value in asked.package:                # the switches a launch would play, none played
            switch, _, state = str(value).partition("=")
            print(f"  package {switch} {state}")
        for one in mounts:                         # the gestures a launch would play, none played
            print(f"  vector {one.vector} -- -s {one.script} mount {one.ident}")
        print(f"--- stdin ({len(stdin)} chars) ---")   # the head of the first prompt: what the harness reads first
        print(stdin)
        return Issue(dry=True), None, lease, None
    if not head and argv and shutil.which(argv[0]) is None:
        # the provider's binary is not on the PATH: nothing opened, nothing recorded -- a caller's own
        # command (`--harness`) is not judged, it is the caller's
        refuse(f"harness-missing -- `{argv[0]}` is not on the PATH: install {provider}'s CLI, or run a "
               "command of your own with --harness.")
    return None, Terms(
        opening=opening, bare=bare, policy=policy, beat=beat, bound=bound, head=tuple(head), provider=provider,
        grammar=grammar, scope=scope, marble=marble, cap=cap, documents=documents, spent=spent, slug=slug,
        taken=taken, work=str(work) if work is not None else None, due=tuple(due), mounts=tuple(mounts),
        session=session, entry=entry, identity=tuple(identity.items()), packages=packages), lease, limit


def on_record(root: Path, name: str, asked: Asked, message: str | None, terms: Terms, run: str) -> None:
    """The message's line at `messages.jsonl`, at the launch: a wake-up under way is on record."""
    sent = Message(at=now(), sender=terms.slug, to=name, run=run, message=message, policy=terms.policy,
                   conducted=False if terms.bare else None, tag=str(asked.tag) if asked.tag is not None else None,
                   pid=os.getpid() if asked.detached else None)
    append(record(root, MESSAGES), sent.json())


def begun(conductor, root: Path, name: str, meta: Path, asked: Asked, key: str | None, message: str | None,
          lease, say, before, waiting: dict | None, terms: Terms) -> tuple[Footing, object, object, object]:
    """The OPENING or the RESUME of one exchange, once everything is judged. An opening (`key` None): the marked
    `-new`, the launcher's lock taken then, the material cloned. A resume: under `lease`, the wake-up's mark,
    the exchange opened by the message or taken up where it stands. An exchange the house does not conduct
    calls no pp. The VECTORS of the run are mounted at every exchange the house conducts, by ONE path in three
    moves, at an opening and at a resume: the call that carries the message opens the exchange under the hold
    (`PP_HOLD_OUTPUT`) and the engine renders nothing; each vector is posed (`mounted`); one bare call plays the
    exchange and renders the first prompt once, what the vectors mount before its first step (`released`). On a
    run that stands, the bare call renders the step it stands on, once; the output its last wake-up kept
    `pending` -- never launched on -- stands before it in the first prompt. A vector refused launches nothing: a
    `refused` event, then the refusal on stderr. When the refusal comes after the message opened the exchange (a
    resume whose gesture does not mount), nothing was rendered: the message's line is written at `messages.jsonl`
    and the run stands on that exchange, its mark without a count of responses (`standing_mark`): `agent status`
    says it standing, never dead, and the next `--run <key>` takes it up -- its message opens nothing more, its
    mounts are posed, its bare call plays the exchange. A message or a bare call the engine refuses (`Unserved`)
    says the `refused` event under its own code, `first-prompt-unserved`, then exits 2: it leaves the run the same
    way at a resume -- the message on record, the run standing --, and opened and never launched at an opening.
    Then the message's line at `messages.jsonl`, the `opened` event, the switches that rode an opening said
    applied (`waiting`, emptied), the principal's voice. -> (the FOOTING of the exchange, the launcher's lock, the
    exchange's sayer -- the keeper of the run's flow --, the trace followed, None under `--quiet`). `say` is the
    caller's own, None for the engine's on stderr; `before(key, say)`, when the caller gives it, plays the
    switches that still wait ahead of the mounts of a resume."""
    persistence, lock = conductor.persistence, locks(conductor)
    given = say                                    # the caller's own `say`, before the exchange wraps one
    opening, bare, policy, taken = terms.opening, terms.bare, terms.policy, terms.taken
    marble, cap, documents, packages, spent = terms.marble, terms.cap, terms.documents, terms.packages, terms.spent
    work = Path(terms.work) if terms.work is not None else None
    due, mounts, entry, provider = list(terms.due), terms.mounts, terms.entry, terms.provider
    standing = False
    after = not opening and mark_of(lock, meta, key).interrupted   # read before this wake-up's mark
    pending = (answered_by(root, name, key)[-1:] or [Response()])[0].pending if not opening else None
    log = tracing(conductor)
    trace = None
    if opening:                                    # all judged: the run opened, the lock, the material
        key, output = opened(conductor, root, meta, message or "", asked.door, documents, marble, cap, packages,
                             hold=bool(mounts))
        lease = lock.try_(launch_of(meta, key))
        if lease is None:
            refuse(f"run-busy -- a wake-up plays run {key}: one wake-up at a time on a run.")
        marked(lease, message or "", 0)
        if work is not None:
            try:
                entry = placed(conductor, root, name, meta, key, work, asked.base)
            except WorkFailure as failure:
                lock.release(lease)
                refuse(f"{failure} -- run {key} opened, nothing launched")
        if mounts:                                 # the run's vectors: every one verified now that the run
            try:                                   # stands, then posed on the exchange the opening left unplayed
                verified(conductor, meta, key, None, mounts)
                mounted(conductor, root, meta, key, mounts, marble, cap)
            except VectorRefused as refusal:
                vector_refused(conductor, root, name, asked, key, given, refusal, lease, f", run {key} opened")
            vectors_kept(root, name, key, due)
            try:
                output = released(conductor, root, meta, key, marble, cap)   # ONE output: the boot, played once
            except Unserved as failure:            # the run opened and never launched, as a vector refused leaves it
                unserved(conductor, root, name, asked, key, given, failure, lease)
    elif bare:                                     # an exchange the house does not conduct: pp is not called
        marked(lease, message or "", len(answered_by(root, name, key)))
        output = ""
    else:                                          # the wake-up's mark, then the exchange opened or taken up
        if mounts and before is not None:          # the switches this wake-up asks play first: a family's
            before(key, keeper(root, name, given if given is not None      # script is offered by its package
                               else step_sayer(log, asked.json)))
        marked(lease, message or "", len(answered_by(root, name, key)))
        if not asked.quiet:                     # followed BEFORE the call that serves the first output
            trace = log.follow(meta, key, from_end=True)
        try:
            output, standing = resumed(conductor, root, meta, key, message or "", marble, pending=pending, cap=cap,
                                       hold=bool(mounts))
        except Unserved as failure:                # the message refused under the hold: nothing mounted
            on_record(root, name, asked, message, terms, key)
            standing_mark(lease, message or "")
            unserved(conductor, root, name, asked, key, given, failure, lease if taken else None)
        if mounts:                                 # the run's vectors, verified before the message, posed on
            try:                                   # the exchange the message opened or the step the run stands on
                mounted(conductor, root, meta, key, mounts, marble, cap)
            except VectorRefused as refusal:       # the exchange stands opened by the message: it is on record,
                on_record(root, name, asked, message, terms, key)                     # and the mark keeps no count of responses -- no launch ended
                standing_mark(lease, message or "")
                vector_refused(conductor, root, name, asked, key, given, refusal, lease if taken else None,
                               f"; the message is recorded and run {key} stands on the exchange it opened -- "
                               f"`agent run {name} --run {key} --message <text>` takes it up with the vectors the "
                               "run kept, `--vector -` with none")
            try:
                served_first = released(conductor, root, meta, key, marble, cap)   # ONE output, rendered once
            except Unserved as failure:            # the exchange stands opened by the message: it is on record,
                on_record(root, name, asked, message, terms, key)                     # and the mark keeps no count of responses -- no launch ended
                standing_mark(lease, message or "")
                unserved(conductor, root, name, asked, key, given, failure, lease if taken else None)
            # the output the run's last wake-up kept and never launched on stands first: the agent has not read it
            output = "\n\n".join(one for one in ((pending or "").rstrip("\n") if standing else "", served_first)
                                  if one)
        vectors_kept(root, name, key, due)         # the set this wake-up replaced or emptied, written once
    neighbours = under_way(lock, persistence, meta, key)
    if asked.detached:                          # the lock held, the run known: the parent may go
        reported(lock, meta, key)
    on_record(root, name, asked, message, terms, key)
    if say is None:
        say = step_sayer(log, asked.json)
    say = keeper(root, name, say)                  # every event of the exchange kept in the run's flow
    if opening and not asked.quiet:             # an opening reads its trace whole: the boot's blocks
        trace = log.follow(meta, key)
    exchange_no = persistence.turns_of(persistence.slot_of(meta, key)) + 1
    said_budget = budget_of(policy, spent)
    say(key, "", "opened", {"agent": name, "exchange": exchange_no, "resumed": not opening, "standing": standing,
                            "provider": provider or "harness", "policy": policy.json(),
                            "packages": packages_of(conductor, meta, key), "cap": cap_of(conductor, meta, cap),
                            "documents": persistence.documents_of(persistence.slot_of(meta, key)) or None,
                            **({"vectors": [one.vector for one in mounts]} if mounts else {}),
                            "budget": said_budget.json() if said_budget is not None else None,
                            **({"tag": str(asked.tag)} if asked.tag is not None else {}),   # the launch's
                            **({"conducted": False} if bare else {}), **({"interrupted": True} if after else {})})
    if opening and waiting:                        # the switches rode the opening: said applied, the list emptied
        for switch, (on, _) in list(waiting.items()):
            waiting.pop(switch, None)
            say(key, f"package {switch} {'on' if on else 'off'}", "package",
                {"name": switch, "on": on, "pending": False, "packages": packages_of(conductor, meta, key)})
    if message is not None:                        # an exchange without a message has no principal's voice
        say(key, "", "principal", {"exchange": exchange_no, "text": message})
    return (Footing(key=key, output=output, standing=standing, after=after, number=exchange_no,
                    neighbours=tuple(neighbours), entry=entry), lease, say, trace)


def looped(conductor, root: Path, name: str, meta: Path, message: str | None, before, headless: bool,
           terms: Terms, footing: Footing, limit, say, trace) -> Account:
    """The LOOP of one exchange, once it is opened or taken up: one launch of the harness per output of pp
    (`exchanged`), or the ONE launch of an exchange the house does not conduct (`unconducted`), its cost counted
    from the session's cumul so far. `limit` gives the policy of each launch, `say` says its steps and its
    voices, `trace` is the run's trace followed (None under `--quiet`), `before(key, say)`, when the caller
    gives it, plays what still waits ahead of every launch. The run's last record says whether the last launch of
    its exchange before overran `ANSWER_BOUND` (`overran`): the first prompt then opens on `TOO_LONG`. -> the
    account of its launches, with what its flow summed and said when the loop ended (`counted`)."""
    bare, bound = terms.bare, terms.bound
    head, provider, grammar, beat, scope = list(terms.head), terms.provider, terms.grammar, terms.beat, terms.scope
    marble, cap, session, identity = terms.marble, terms.cap, terms.session, dict(terms.identity)
    key, output, after = footing.key, footing.output, footing.after
    exchange_no, neighbours, entry = footing.number, footing.neighbours, footing.entry
    material = entry.where() if entry is not None else None
    log = tracing(conductor)
    answered = answered_by(root, name, key)
    cumul_before = next((one.session_cost_usd for one in reversed(answered)
                         if isinstance(one.session_cost_usd, (int, float))), None)   # the session's cumul so far
    overrun = overran(answered[-1]) if answered else False
    if bare:
        done = counted(unconducted, conductor, root, meta, key, head, provider, grammar, limit, session, material, identity,
                           message or "", neighbours, log, beat, say, cumul_before, scope, exchange_no, after, before,
                           overrun=overrun)
    else:
        done = counted(exchanged, conductor, root, meta, key, head, provider, grammar, limit, session, material, identity,
                         None if headless else (message or ""), output, neighbours, trace, log, beat, say, bound,
                         cumul_before, scope,
                         exchange_no, after, before, marble, cap, overrun=overrun)
    return done


def overran(last: Response) -> bool:
    """-> whether the last launch of the exchange `last` records held a last message over `ANSWER_BOUND`: the
    overrun the next prompt of the run still owes its `TOO_LONG`."""
    return any(one is not None and one.launch == last.launches and one.over() for one in last.finals or ())


def consigned(conductor, root: Path, name: str, meta: Path, terms: Terms, footing: Footing, done: Account,
              lease) -> Issue:
    """What ONE exchange leaves once its loop is over: an interruption marked in the launcher's lock, for the
    next wake-up of the run to say it; the material sent back, whatever the answer; the response, then the
    session, recorded in that order -- nothing kept when no launch finished --; the run's state read. -> the
    ISSUE of the exchange."""
    persistence = conductor.persistence
    bare, policy, bound, spent, provider = terms.bare, terms.policy, terms.bound, terms.spent, terms.provider
    key, standing, after, entry = footing.key, footing.standing, footing.after, footing.entry
    answered, interrupted = done.answered, done.interrupted
    if interrupted:                                # the next wake-up of the run says it to the model
        interrupted_mark(lease)
    sent_back = shipped(conductor, root, name, entry) if entry is not None else None   # the branch, whatever the answer
    budget = budget_of(policy, spent + float(done.cost_usd or 0.0))
    if answered is None:                           # no launch finished: nothing kept
        stack = stack_of(conductor, meta, key)
        reason = (f"interrupted -- run {key} stands on `{stack}`, nothing recorded: the next message, or "
                  f"`--run {key}`, takes it up" if interrupted else
                  f"harness rc {done.harness_rc}: {done.harness_stderr or 'no output'} -- nothing recorded")
        return Issue(key=key, reason=reason, account=done, standing=standing, sent_back=sent_back, bound=bound,
                     interrupted=interrupted, after=after, budget=budget)
    error, stop = answered.error, answered.stop
    if interrupted:
        error = "interrupted"
    elif stop is not None:
        error = stop.kind                          # the provider's usage limit: `quota`, whatever the rc
    elif done.harness_rc != 0 and error is None:
        error = f"harness rc {done.harness_rc}: {done.harness_stderr or 'nothing on stderr'}"
    elif done.harness_rc == 0 and done.budget_spent:
        error = "budget-spent"                     # the run's cap stopped it between two launches
    at = now()
    index = len(answered_by(root, name, key)) + 1
    kept = Response(
        at=at, agent=name, run=key, index=index, response=composed(done.words), cost_usd=done.cost_usd,
        session_cost_usd=done.session_cost_usd, launches=done.launches, denials=list(done.denials), error=error,
        harness_rc=done.harness_rc,
        budget={"cap": budget.cap, "spent": budget.spent} if error == "budget-spent" else None,
        quota={"until": stop.until, "said": stop.said} if stop is not None and error == "quota" else None,
        conducted=False if bare else None, flow=done.flow, tokens_sent=done.tokens_sent,
        pending=done.pending or None,              # the output the next wake-up launches on: served, launched on by nobody
        words=done.words,                          # the matter: every words of the exchange's launches, under their
        finals=done.finals,                        # launch; `response` their composition, written once (`composed`);
        overruns=sum(1 for one in done.finals if one.over()),   # the last messages over the bound, by their length
        model=policy.model, effort=policy.effort)
    append(record(root, RESPONSES), kept.json())
    known = session_of_run(root, name, key)
    if (known.session if known is not None else None) != done.session:
        append(record(root, SESSIONS), Session(at=at, agent=name, run=key, provider=provider,
                                               session=done.session).json())
    slot = persistence.slot_of(meta, key)
    state, stack = standing_of(conductor, meta, key), stack_of(conductor, meta, key)
    settled = not persistence.held_of(slot) and not persistence.pending_of(slot)
    arrived = (done.harness_rc == 0 and (state == "parked" or bare) and settled and not done.spent
               and not done.budget_spent and not interrupted and spoke(kept))
    said = ("interrupted" if interrupted else "stopped" if done.harness_rc != 0 else
            "unconducted" if bare else "parked" if arrived else "standing")
    return Issue(key=key, kept=kept, account=done, said=said, arrived=arrived, stack=stack,
                 exchanges=persistence.turns_of(slot) + (0 if state == "parked" else 1),   # the one under way
                 standing=standing, sent_back=sent_back, bound=bound, interrupted=interrupted, after=after,
                 budget=budget)


def reasoned(conductor, meta: Path, key: str, issue: Issue) -> str | None:
    """-> why an exchange that kept a response did not end well (`reason_of`), None when it ended well: the
    run's trace is read for its last refusal when the passage is not over, and then alone."""
    return reason_of(key, issue, None if issue.arrived else refusal_traced(conductor, meta, key))


def exchange(conductor, root: Path, name: str, meta: Path, asked: Asked, key: str | None, message: str | None,
             lease, say=None, before=None, waiting: dict | None = None,
             headless: bool = False) -> tuple[Issue, object, object]:
    """ONE exchange of a message with the agent at `meta`, conducted by the house -- the one function `run` and
    `chat` play, in four times: every judgment before the launch (`judged`), the opening (`key` None) or the
    resume (`begun`), the LOOP of its launches (`looped`), what it leaves on record (`consigned`). A refusal met
    before the launch gives a lock taken here back and leaves the run as it was. -> (the ISSUE, the launcher's
    lock, the exchange's sayer): the `Issue` -- `dry` alone for a dry run: said, nothing opened --, the lock held
    by the caller from here, and the keeper of the run's flow that said the exchange (None when nothing was
    launched). `say(key, line, kind, fields)` is who says the steps and the voices: the engine's `log.said` on
    stderr unless the caller gives its own; `waiting` is the switches waiting (`{name: (on, line)}`: a
    conversation's, or the `--package` of a wake-up): at an OPENING they all ride `PP_PACKAGES` on the `-new` --
    the first block is composed as they say, each then said `package` (`pending: false`) and dropped from the
    list --; at a resume `before(key, say)`, when the caller gives it, plays what still waits ahead of every
    launch, handed the exchange's own `say`. `headless`: an exchange WITHOUT a message on a run that holds an
    output -- the block a space the principal opened or closed --: the first prompt is that output
    alone, the bare call of the principal its head, nothing recorded as a message (`message` null at the
    record)."""
    early, terms, lease, limit = judged(conductor, root, name, meta, asked, key, message, lease, say, waiting, headless)
    if early is not None:                          # judged and over already: the cap reached, a dry run said
        return early, lease, None
    footing, lease, say, trace = begun(conductor, root, name, meta, asked, key, message, lease, say, before, waiting,
                                       terms)
    done = looped(conductor, root, name, meta, message, before, headless, terms, footing, limit, say, trace)
    return consigned(conductor, root, name, meta, terms, footing, done, lease), lease, say
