"""The context of a run: the window of its model, the weight of its flow, the estimate fitted to what was measured."""
from __future__ import annotations

import statistics

from model.context import Context, Declared, Fit, Gauged, Measure, Scale, Share, Spread
from model.exchange import Response
from model.flow import Sums


def window_of(declared: Declared, model: str | None) -> int | None:
    """-> the window of `model` as `declared_of` reads its adapter: the one it declares for that model, else its
    `default` -- a model it does not declare, or no model named; None when neither is a positive count."""
    def counted(window) -> int | None:
        return window if isinstance(window, int) and not isinstance(window, bool) and window > 0 else None
    named = next((window for name, window in declared.windows if name == model), None) if model else None
    return counted(named) or counted(declared.default)


def weighed(flow: Sums, model: Scale | Declared) -> float:
    """-> what one exchange's flow adds to a context, weighed by the adapter's constants: the flow but the
    thought times `ratio`, the thought times `kept`."""
    thinking = int(flow.thinking or 0)
    return model.ratio * (flow.total() - thinking) + model.kept * thinking


def context_of(rows: list[Response], model: Scale, served=None, since: int | None = None) -> Context | None:
    """-> what the flow of the run's responses `rows` says of its context: the voices summed in tokens and their
    `total`; `measured` the context the LAST call measured by its provider sent the model ({tokens, index}, the
    response it closed; None when no call was measured); `tokens` the context now -- that measure, plus the flow
    of the exchanges after it weighed by the adapter's constants (`weighed`), or without a measure the adapter's
    `base` plus the whole flow weighed --, `estimated` whether anything was added to a measure; the `window` of
    the run's model and the part of it `used`; pp's part OF THE CONTEXT -- pp's voices of the flow plus the
    `marble`, the standing orders every launch carries, both weighed by the adapter's `ratio`: `tokens` that part,
    `marble` the standing orders' tokens within it, `share` that part over the context's `tokens`, `over` true when
    that part passes the context's `tokens` (the estimate past what was measured) -- then no `share` --, `served`
    what the engine's `-stats` counts beside --, the `calls`, the
    `reread` (per exchange, its calls times the flow at its start plus half its own) and `since`; None when no row
    carries a flow."""
    counted = [one for one in rows if one.flow is not None]
    flows = [one.flow for one in counted]
    if not flows:
        return None
    whole = Sums()
    for one in flows:
        whole = whole.plus(one)
    total = whole.total()
    pp = whole.conduction + whole.pp_input + whole.pp_result   # what of the flow is pp's: its outputs, the calls of it
    reread, at_start = 0, 0
    for one in flows:
        size = one.total()
        reread += int(one.calls or 0) * (at_start + size // 2)
        at_start += size
    measured, added = None, 0.0
    for row in counted:
        sent = row.flow.context
        if isinstance(sent, int) and not isinstance(sent, bool):
            measured, added = Measure(tokens=sent, index=row.index), 0.0
        else:
            added += weighed(row.flow, model)
    tokens = round((measured.tokens if measured is not None else model.base) + added)
    window = model.window
    inside = model.ratio * (pp + model.marble)
    return Context(flow=whole, total=total,
                   tokens=tokens, measured=measured,
                   estimated=measured is None or added > 0, window=window,
                   used=round(tokens / window, 4) if window else None,
                   pp=Share(tokens=round(inside), marble=round(model.ratio * model.marble),
                            share=round(inside / tokens, 4) if 0 < tokens and inside <= tokens else None,
                            over=inside > tokens, served=served if isinstance(served, int) else None),
                   reread=reread, since=since)


RATIOS = [round(0.5 + 0.05 * one, 2) for one in range(51)]   # the weights `calibrate` tries for the flow: 0.5 to 3
KEPTS = [round(0.05 * one, 2) for one in range(21)]           # and for the part of the thought kept: 0 to 1


def gaps_of(flow: int, calibrated: int, measured: int | None) -> tuple[float, float] | None:
    """-> how far the two estimates of a run's context stand from what its provider's store `measured`, each as
    a part of the measure: (the gap of the `flow` summed, the gap of the `calibrated` estimate); None without a
    measure."""
    if not measured:
        return None
    return round((flow - measured) / measured, 4), round((calibrated - measured) / measured, 4)


def spread(gaps: list[float]) -> Spread:
    """-> the median, p10 and p90 of absolute relative gaps, rounded; None each without a gap."""
    ranked = sorted(abs(one) for one in gaps)
    if not ranked:
        return Spread()
    at = lambda share: ranked[min(len(ranked) - 1, int(share * len(ranked)))]   # noqa: E731
    return Spread(median=round(statistics.median(ranked), 4), p10=round(at(0.1), 4), p90=round(at(0.9), 4))


def fitted(measured: list[Gauged]) -> Fit | None:
    """-> the constants of the estimate that fit the runs `measured` best (none compacted): the base the median
    of their first calls, the ratio and the part of the thought kept that make the median gap to their last call
    least (`RATIOS` x `KEPTS`), and that gap; None without a run."""
    if not measured:
        return None
    base = round(statistics.median(one.first for one in measured))

    def gaps(ratio: float, kept: float) -> list[float]:
        return [(base + ratio * (one.flow - one.thinking) + kept * one.thinking - one.last) / one.last
                for one in measured]
    ratio, kept = min(((r, k) for r in RATIOS for k in KEPTS), key=lambda rk: statistics.median(abs(g) for g in gaps(*rk)))
    found = spread(gaps(ratio, kept))
    return Fit(base=base, ratio=ratio, kept=kept, median=found.median, p90=found.p90)
