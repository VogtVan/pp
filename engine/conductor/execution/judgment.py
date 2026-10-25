"""execution.judgment -- the judgment: the one point of proof (the PROVE a document writes), the checks of an answer. A mixin of the facade: no state of its own."""
from __future__ import annotations

import json
from ..core import deviation, language
from ..state import instance, settings
from ..core.errors import Refusal
from ..core.model import Frame, Instruction, Stack
from ..state import persistence


def _fix(one: dict) -> str:
    """-> the fix a proof object names, "" when it names none."""
    return str(one.get("fix", "")).strip()


def _gap(one: dict) -> str:
    """-> what a `fail` object declares missing (`blocked`, a non-empty text), "" otherwise."""
    blocked = one.get("blocked")
    return blocked.strip() if isinstance(blocked, str) else ""

class Judging:
    """The judgment: the checkpoint's one regime, the checks of an answer -- a mixin of the facade."""

    def _production_in_force(self, frame: Frame) -> bool:
        """-> whether ONE law of production binds `frame` (its chain and the mounts):
        the proof asks the production laws alone, so none in force means no
        checkpoint at all -- a behavior law binds the block, never the proof."""
        return any(one.section == "production" for one in self._in_force(frame))

    @staticmethod
    def _depth(holder: str) -> int:
        return int(holder.split(":", 1)[0]) if holder.split(":", 1)[0].isdigit() else 0

    def _indebted(self, stack: Stack, frame: Frame) -> bool:
        """-> whether `frame` or a frame above it PRODUCED since the PROVE that covers them:
        the slot's holders at the frame's depth and deeper -- its own debt, and the debt of the
        callees that produced under its laws and popped."""
        slot = self._session or self._slot()
        if not slot:
            return False
        depth = stack.frames.index(frame) if frame in stack.frames else len(stack.frames)
        return any(self._depth(one) >= depth for one in persistence.debt_of(slot))

    def _produced(self, stack: Stack, frame: Frame) -> None:
        """A production of the agent's was given in `frame` (a PICK, an INFER, a WORK -- said
        or handed): that frame owes it to the next written PROVE at its depth or below."""
        if self._dry or self._session is None:
            return
        holder = self.holder_of(stack, frame)
        debt = persistence.debt_of(self._session)
        if holder not in debt:
            persistence.set_debt(self._session, debt + [holder])

    def _debt_paid(self, stack: Stack, frame: Frame) -> None:
        """A written PROVE of `frame` was proven: the frames at its depth and deeper are paid,
        the laws a contributor left due with them; a frame below keeps its debt."""
        self._settle_owed()
        if self._dry or self._session is None:
            return
        depth = stack.frames.index(frame) if frame in stack.frames else 0
        persistence.set_debt(self._session,
                             [one for one in persistence.debt_of(self._session) if self._depth(one) < depth])

    def _due_proof(self, stack: Stack, frame: Frame) -> bool:
        """-> whether a written PROVE reached NOW has something to ask: a law of production
        in force (the chain, the mounts, the laws a contributor left due) and a debt -- a
        production given since the PROVE that covers it, by this frame or a callee above it,
        or laws left due. The proof has ONE point: the PROVE the document writes; the engine injects none, no site arms or disarms a frame, and
        without a written PROVE nothing is due. A PROVE with nothing to ask resolves on a line."""
        if not self._production_in_force(frame):
            return False
        return self._indebted(stack, frame) or bool(self._owed_laws())

    def _prove_ahead(self, frame: Frame, instruction: Instruction) -> bool:
        """-> whether a written PROVE stands AHEAD of `instruction` with nothing the agent
        plays between -- HOOKs that inject nothing and SERVEs skipped -- and a law of
        production is in force: the output about to leave a batched step keeps it batched,
        the proof is asked in the same output (one launch, as the LLM's mode asks it)."""
        if not self._production_in_force(frame):
            return False
        at = frame.procedure.instructions.index(instruction)
        for following in frame.procedure.instructions[at:]:
            if following.keyword == "PROVE":
                return not following.done
            if following.keyword == "HOOK" and not self._hook_injects(frame, following):
                continue
            if following.keyword == "SERVE":
                continue
            return False
        return False

    def _prove_coming(self, frame: Frame, instruction: Instruction) -> str:
        """-> `obliged` when a written PROVE stands right after `instruction` and a law of
        production is in force -- the step's own production will be its debt --, '' when
        none follows: what the fusion reads one step ahead."""
        if not self._production_in_force(frame):
            return ""
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        if following and following[0].keyword == "PROVE" and not following[0].done:
            return "obliged"
        return ""

    def _fusion_cap(self, frame: Frame) -> int:
        """-> the yields-per-output cap in force for `frame`'s steps: the document's
        own `fusion:` when declared, the instance's otherwise. 0 = unlimited."""
        declared = frame.document.front.get("fusion")
        if declared is not None:
            return settings.fusion_of(declared)
        return self._settings.fusion

    def _check(self, stack: Stack, frame: Frame, instruction: Instruction,
               answer: str) -> str:
        """-> what the answer missed, or "" when it arrives. One checker per keyword, by name."""
        checker = getattr(self, f"_check_{instruction.keyword.lower()}", None)
        return checker(stack, frame, instruction, answer) if checker else ""

    def _check_pick(self, stack: Stack, frame: Frame, instruction: Instruction,
                    answer: str) -> str:
        return "" if answer in instruction.options else deviation.wrong_answer(instruction, answer)

    def _check_next(self, stack: Stack, frame: Frame, instruction: Instruction,
                    answer: str) -> str:
        """The successor the agent elects is a PICK: judged by membership among the
        names of `next:`, a name outside the graph a miss that repairs."""
        return self._check_pick(stack, frame, instruction, answer)

    def _check_prove(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """The proof is machine-checked: valid JSON, the declared shape, one object for
        every code the line asks -- the laws of production in force: a code left unnamed
        is a named miss, a code no law in force carries is one too -- and any `fail`
        verdict reopens the whole document.
        `n/a` says a law without bearing on this production: neither earned nor
        failed, it repairs nothing -- `ok` is reserved for the VERIFIED. A `fail` that
        carries `blocked` (what is missing, a non-empty text) DECLARES a gap: accepted,
        the checkpoint closes; a bare `fail` outweighs it, a `fix` repairs in place."""
        try:
            proof = json.loads(answer)
        except ValueError as wrong:
            return f"the PROOF is not one valid JSON value -- {wrong}."
        if (not isinstance(proof, list)
                or not all(isinstance(one, dict) and {"code", "evidence", "verdict"} <= set(one)
                           for one in proof)):
            return ('the PROOF is not a JSON array of {"code", "evidence", "verdict"} '
                    "objects.")
        odd = [one for one in proof if one["verdict"] not in ("ok", "fail", "n/a")]
        if odd:
            return f"a verdict is `ok`, `fail` or `n/a` -- not {odd[0]['verdict']!r}."
        if instruction.refit:
            # the MINI-PROOF: the repaired codes alone come back, verified -- a code
            # failing twice loses the cheap branch, the document replays
            expected = set(instruction.refit)
            if {one["code"] for one in proof} != expected:
                # the ask stands: the mini-proof re-presents, the document never
                # reopens on a coverage slip -- the bound still counts the try
                self._inplace = instruction.refit
                return ("the mini-proof covers exactly the repaired code(s): "
                        f"{', '.join(instruction.refit)}.")
            relapsed = [one for one in proof if one["verdict"] == "fail" and not _gap(one)]
            instruction.refit = ()
            if relapsed:
                return ("the repaired code failed AGAIN -- the cheap branch closes: "
                        + " · ".join(f"{one['code']}: {one['evidence']}" for one in relapsed))
            self._declared([one for one in proof if one["verdict"] == "fail"])
            return ""
        covered = [one["code"] for one in proof]
        # a behavior law never enters the proof: it binds the block, the judge asks
        # the production laws alone (an object offered for a behavior law is not a miss);
        # a code no law in force carries is a miss -- the proof judges what stands --
        # and a proof naming no law of production proves nothing
        in_force = {one.code: one.section for one in self._in_force(frame)}
        foreign = [code for code in covered if code not in in_force]
        if foreign:
            return f"the PROOF names law(s) not in force: {', '.join(foreign)}."
        if not any(in_force[code] == "production" for code in covered):
            return "the PROOF names no law of production -- the codes at risk, at least one."
        unnamed = [code for code, section in in_force.items()
                   if section == "production" and code not in covered]
        if unnamed:
            # every code the line asks takes its verdict: a silence is no n/a
            return (f"the PROOF leaves {len(unnamed)} code(s) unnamed: {', '.join(unnamed)} -- "
                    "each one takes ok, fail or n/a.")
        failed = [one for one in proof if one["verdict"] == "fail"]
        bare = [one for one in failed if not _fix(one) and not _gap(one)]
        if bare:
            # a fail that neither fixes nor says what is missing: the document replays
            return ("your own proof failed -- "
                    + " · ".join(f"{one['code']}: {one['evidence']}" for one in bare))
        fixed = [one for one in failed if _fix(one)]
        self._declared([one for one in failed if not _fix(one)])
        if fixed:
            # every remaining fail NAMES its fix: the repair plays IN PLACE -- the agent
            # corrects the production and re-proves the fixed codes alone
            self._inplace = tuple(one["code"] for one in fixed)
            return ("your proof failed and NAMES its fixes -- repair the "
                    "production IN PLACE, then pipe a mini-proof over the failed "
                    "code(s) alone: "
                    + " · ".join(f"{one['code']}: {one['fix']}" for one in fixed))
        return ""

    def _declared(self, gapped: list[dict]) -> None:
        """The gaps a proof DECLARED -- `fail` objects carrying `blocked`: accepted, not
        repaired; written on the trace, and held for the closing of the block this call
        renders, which says them."""
        if not gapped:
            return
        found = [{"code": one["code"], "text": _gap(one)} for one in gapped]
        self._trace("blocked", gaps=found)
        self._gaps.extend((one["code"], one["text"]) for one in found)

    def _check_field(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """The FIELD is machine-checked on its FORM alone -- one valid JSON value, an
        array, scalars (strings or numbers) none empty, each once, under the bound -- and
        never on what an element IS: the engine knows no nature, an array of integers
        passes exactly as an array of paths that do not exist."""
        try:
            field = json.loads(answer)
        except ValueError as wrong:
            return f"the FIELD is not one valid JSON value -- {wrong}."
        return language.listed("field", field)

    def _check_infer(self, stack: Stack, frame: Frame, instruction: Instruction,
                     answer: str) -> str:
        """A CAPTURED production validates against its format -- the mechanical seed
        of the convergence: `json` must parse; a consumed empty is no production. A
        production the next step ELECTS from takes the engine's `list` form -- the one
        a FIELD has, whatever the document's `output:` -- and is judged on it before the
        renderer ever meets it: a text or a list of objects is the agent's miss, named,
        and the document reopens."""
        consumed, _ = self._consumer(stack, frame, instruction)
        if consumed and not answer.strip():
            return "an empty production -- the next step consumes it; hand it over."
        form = self._form_of(stack, frame, instruction)
        if form in ("json", language.LIST) and answer.strip():
            try:
                value = json.loads(answer)
            except ValueError as wrong:
                return f"not one valid JSON value -- {wrong}."
            if form == language.LIST:
                return language.listed(language.LIST, value)
        return ""

    _check_work = _check_infer   # a WORK a PICK elects from owes the list as an INFER does

