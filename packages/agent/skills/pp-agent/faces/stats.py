"""What the readings count of a run: the sums of its records beside its conduction, the estimates of its context
beside what its provider measured, the constants that fit a provider's runs."""
from __future__ import annotations

from model.cost import Context, Cumuls, Declared, Fit, Spread
from model.words import ANSWER_BOUND, ESTIMATE


def stats_object(name: str, key: str, summed: Cumuls, exchanges: int, conduction: dict,
                 context: Context | None) -> dict:
    """-> a run as `stats --json` says it: the cost, the launches and the overruns its records sum, its exchanges,
    the run's object of the engine's own `-stats` under `conduction`, and its context -- None without a flow."""
    return {"agent": name, "run": key, "cost_usd": summed.cost_usd, "launches": summed.launches,
            "overruns": summed.overruns, "exchanges": exchanges, "conduction": conduction,
            "context": context.json() if context is not None else None}


def overruns_line(summed: Cumuls) -> str:
    """-> what `stats` says of the run's last messages beside the engine's text: the overruns its records sum."""
    return f"overruns: {summed.overruns} last message(s) over {ANSWER_BOUND} characters"


def gauged_object(name: str, key: str, provider: str | None, session: str | None, calls: int | None,
                  compactions: int | None, measured: int | None, flow: int, calibrated: int,
                  gaps: tuple[float, float] | None) -> dict:
    """-> a run as `calibrate --json` says it: its provider and its session, the `calls` and the `compactions`
    its provider's store keeps and the context its last call `measured` -- null each where the store says
    nothing --, the two estimates (`flow`, `calibrated`) and the `gap` of each to the measure, null without one."""
    return {"agent": name, "run": key, "provider": provider, "session": session,
            "calls": calls, "compactions": compactions, "measured": measured,
            "estimate": {"flow": flow, "calibrated": calibrated},
            "gap": {"flow": gaps[0], "calibrated": gaps[1]} if gaps is not None else None}


def gauged_line(name: str, key: str, provider: str | None, calls: int | None, compactions: int | None,
                measured: int | None, flow: int, calibrated: int, gaps: tuple[float, float] | None) -> str:
    """-> a run as `calibrate` says it: its provider, the measure with its calls and its compactions, each
    estimate with its gap -- or that nothing was measured."""
    flow_gap, calibrated_gap = gaps if gaps is not None else (0, 0)
    return (f"{name} · {key} · {provider or 'harness'} · "
            + (f"measured {measured} over {calls} calls, {compactions} compaction(s) · "
               f"flow {flow} ({flow_gap:+.0%}) · calibrated "
               f"{calibrated} ({calibrated_gap:+.0%})" if measured
               else "nothing measured"))


def fit_object(provider: str, runs: int, compacted: int, flow: Spread, calibrated: Spread, declared: Declared,
               fit: Fit | None) -> dict:
    """-> a provider as `calibrate --json` says it once a run of its was measured: its `runs`, those
    `compacted`, how the gaps of the two estimates spread over its runs without a compaction, the constants its
    adapter `declared` and the ones `fitted` on those runs, null when none fits."""
    return {"provider": provider, "runs": runs, "compacted": compacted,
            "gap": {"flow": flow.json(), "calibrated": calibrated.json()},
            "declared": constants_of(declared),
            "fitted": fit.json() if fit is not None else None}


def fit_line(provider: str, runs: int, compacted: int, flow: Spread, calibrated: Spread, declared: Declared,
             fit: Fit | None) -> str:
    """-> a provider as `calibrate` says it: its runs measured and compacted, the median gap of each estimate,
    the constants its adapter declared and the ones fitted."""
    return (f"{provider}: {runs} run(s) measured, {compacted} compacted · median gap flow "
            f"{flow.median}, calibrated {calibrated.median} · declared "
            f"{constants_of(declared)} · fitted {fit.json() if fit is not None else None}")


def constants_of(declared: Declared) -> dict:
    """-> the constants of the estimate an adapter declared, under the names it declares them by."""
    return {name: getattr(declared, key) for key, (name, _) in ESTIMATE.items()}
