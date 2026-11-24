"""team-sim -- one simulation of a team, played on paper, many times: the model check of its tick.

ONE core plays the tick of a team under random interleavings of ticks, wake-ups ending, posts, a
crash and a schedule: the journal is the truth, replayed at every read; every tick is a generator,
each `yield` a place where another process may run; the tick holds its lock by the v2 protocol
(try, mark, release, then read the mark). The core carries the whole dynamics of the reframings:
the intent before the spawn, the answer kept by (run, index), the wake lock, `--on-end`, the reap,
the routing, the rounds, the ring, the wake; the member's run per carrier, its key kept across an upgrade,
the bounds and the shares of the budget, the pause, the seasons; the answer and the debt.
A number in brackets -- [119] -- tags the decision that brought a rule into the dynamics: the rule is said
where its tag stands, in a comment or in the name of the line that plays it, and nothing else is to be read.
2026-11-06 [119]: a run is kept per (member, CARRIER) -- the recurrence of an occurrence, the ceremony of a
ring's task, the task itself otherwise --, one key, one session and one clone per run (I18, I13), one wake-up at a
time per member whatever its run (I19).
2026-11-06 [120]: a recurrence carries a context LIMIT; every `wake-ended` of a run says the context it
left (none for an unmeasured exchange), and the member's first wake-up on a NEW occurrence renews the run of the
recurrence -- `run-renewed`, a new run -- when the last measure of that run reached the limit (I21, I18 per renewal).
2026-11-06 [121]: a recurrence may come back by a DURATION -- its slots at k x INTERVAL from its pose, the
first at the pose itself, the slot under way alone judged at every ring (I27).

The core plays ONE of two TRANSPORTS, the grain at which the tick reads a member: `final`, team 0.39.0 -- a
wake-up is one whole exchange of the member, its acts read in its last answer and routed at its end --, or
`message`, owed -- a wake-up is ONE launch of the harness; what the member says in a launch is its
`words`, each routed as soon as it is read; a launch that leaves the member with more to say leaves
its run STANDING (« relaunch me ») and the tick relaunches it, the head of the next launch carrying
nothing: what arrived for it meanwhile waits for its park [s.1377]; a launch that leaves nothing to say
PARKS the run (« wait for a message »), and the next message for it opens a new launch -- its turn. The
tick reads standing or parked at
the agent's face and nothing else of the run (R14). Nothing holds a member (2026-11-10): every message for
it launches it, no answer is kept back for a round, and a member that delegated answers once the answers it
wants are in -- its own count. There is no death (R12): a debt is due until its answer -- said
at every head, relanced --, a launch that crashes is counted for the detector and the
run is relaunched, only the words it was writing are lost; the bounds are the launcher's: the
launches of a task, the launches of a season, the seconds of one launch (R13).

The RULES of the transport by message the comments cite:

  R10  the launcher relaunches a run while the agent says « relaunch me » and stops when it says « wait for a
       message »: it advances what the run holds without seeing it, and its bounds are its own
  R12  there is no death: a debt is due until its answer -- at the head of every launch, relanced, then
       preempted --, a launch that crashes or is killed is a `wake-failed` counted under the retries and for the
       detector, and nothing is judged at a launch nor at a parking
  R13  the bounds stand by level: the budget by launch and by season, the launches by task, the timeout by launch
  R14  the tick knows no step, no frame and no passage of a run: standing or parked, read at the agent's face
  T7   under `work:` a member works one task at a time in its one clone: a run that stands and may be relaunched
       takes no other task's head [105]

A SCENARIO is a profile of that core -- its members and the agents that play them, its edges, the
tasks its owner posts, what each member answers, the faults it draws, what quiescence owes:

  review   m -> r1 r2 r3, one task; the lock protocol compared
  reframe  m -> r1 r2, tasks T1 T2 -- and, extended, T3 answered at its first answer, T4 killed then resumed, the
           daily rung by the tick and at hand, the bounds, timeout:, a pause, a season, and a
           recurrence the owner posted, one occurrence per period, skipped while the one before is open, and
           its hour changed by the owner in the season, its run renewed past its context limit [112] [117] [120]
  squad    m -> dev1 dev2 dev3, three members of ONE agent, an upgrade, a daily rung before it and after it

  debt     m -> r1 r2 played by the GENERIC agent: it answers each message it owes, now or later,
           asks a peer or its supervisor, may be stubborn (a relance gets nothing back) or silent
           (a parking launch that says nothing) -- the answer, the debt, the deadlock, the failure
           detector, the seasons, the info and the silence, under both transports
  workers  a supervisor and its workers on a CLOCK: the seconds of a launch, the overhead of a
           wake-up, the dollars -- the end, the launches and the cost of both transports

The NET of a team is its TIMER (team 0.44.0 [110]): a tick at the next deadline, at every step of
`schedule:`, drawn as a random tick while a task is open; a MACHINE CUT kills every tick, every wake-up under
way and the timer, and the relaunch entry laid at the start (`ONLOGON`, `@reboot`) plays one tick at the next
logon, which arms the timer again -- without it the team waits for a gesture. A line of `review` named `timer`
plays the ARMING itself: the timer stands once a tick armed it, plays one tick and leaves; a wake-up's end may
fire no tick, the net alone reaping it, and the timer's tick may fail before any lock -- the timer then arms the
next itself [s.1357]; the tick arms at the start of its round as at its end, so that a tick killed mid-round leaves
a timer [s.1373], and a timer whose tick found the lock held arms the next too.

A LINE is a scenario, its flags, the net and the death of a tick; it renders its runs, the
runs that hold every invariant, the runs that break each one, its VERDICT -- an owed line holds on
every run, a variant breaks the invariants it names (BREAKS, the batches' `breaks`) -- and what it
spent: its end p50/p90 in steps, its wake-ups, its launches and its cost per run. The lines of the
tick play under both transports (the table says which); the invariants are the catalogue below.

The INVARIANTS, each said once -- the code is what a line's verdict and BREAKS name:

  I1    every task of the scenario settles as its profile owes -- resolved, stopped, or open for a reason the
        owner was told --, and the calendar line leaves when no task stays open and no ceremony is declared;
        with a machine cut, the tasks settle once the user logs on again, with no gesture [110] [111]
  I2    two ticks never play their steps at once
  I3    every message is delivered exactly once; a failed wake-up puts its messages back
  I4    nothing is left unreaped, unrouted or unwoken
  I7    no task dies of an upgrade, and no member changes its key across one
  I9    a stop closes its task whatever holds it and costs no wake-up; a `stop --kill` ends the wake-ups under
        way on that task alone
  I10   no bound is exceeded -- the parallel wake-ups, the wake-ups (launches) of a task, the budget, the
        wake-ups (launches) of a season, the retries --, each spent event written once with its notice
  I10e  no bound is reached by wake-ups never launched
  I10r  the cost kept plus the allowances under way stay within the budget
  I10p  a member due is never deferred `reserved` while fewer than k wake-ups play at an unchanged cost
  I11a  no `do` leaves an edge; an `ask` stays in the team or goes to a principal
  I11b  no post to a principal is returned
  I12   every answer kept without a run is counted once, against its own wake-up; the cost the journal sums
        is the cost the house kept
  I13   under `work:` a run works in ONE clone, never changed, never shared by two runs, and two wake-ups
        never share a material
  I15   each period rings once, at its hour, and its task resolves; a ring at hand takes no period and
        resolves too
  I16   a stuck wake-up is killed once and fails `wake-timeout`; a wake-up whose answer is kept is never
        killed, by `timeout:` nor by a `stop --kill`
  I17   no wake-up fails `run-busy` because its run's wake lock is still being released
  I18   one key and one harness session per run -- (member, carrier) -- from its first answer, between two
        renewals; never two carriers of a member on one key or in one session [119] [120]
  I19   a member plays ONE wake-up at a time -- under `message`, its launches never overlap
  I20   two members never share a key nor a session, the members of one agent included
  I21   no new occurrence is launched in a run whose last measure reached its recurrence's limit, and no run
        under its limit is renewed
  I22   every wake-up a ceremony brings plays the ceremony's entry, at an opening as at a resume
  I23   a task the owner resumes ends done, or open for a reason the owner was told after the resume
  I24   between a team's `paused` and its `unpaused` the tick writes no `wake-intent` and no `ceremony-due`;
        a period whose span passed whole is never rung
  I25   a recurrence sounds each of its periods once -- an occurrence, or a skip while the occurrence before
        it is open, its origin counted as one [122] --, never two occurrences open at once, nothing while paused
  I26   no occurrence of a recurrence sounds before its moment under the period in force
  I27   a slot of a recurrence by a duration that is due sounds or is skipped -- the first occurrence at the
        first tick after its pose --, never later, never twice
  J1    a debt is settled ONCE: by the first answer that cites it, the member's or the tick's in its place
  J2    no relance outside the bottom of a deadlocked set
  J3    no silent stall: a run ends with its task resolved or with the owner told
  J4    no task of a season stands blocked in silence
  J5    no debt stands open once the root's answer closed the task, and a message posted after the close
        opens none
  J8    an `info` opens no debt, whoever wrote it; a member's `info` launches nobody -- it
        rides the head of its recipient's next wake-up
  J9    a stubborn debtor is suspected within `silence:` silent PASSAGES -- a wake-up and its continuations,
        until the run parks --, its creditors unblocked, no gesture of the principal: no more than `silence:`
        relances in a row carry a debt without an act of the member or its fall
  J10   a debtor that says an act at every passage is never suspected by silence, never the subject of a
        notice -- however many launches its passage takes: a continuation counts for nothing
  J12   a run that stands on a task its root closed is continued ONCE at most: a run that stands after that
        continuation is held as parked, and nothing launches it but a message [s.1409]
  J13   a member that waits for a principal's answer on the task never falls by silence: a passage that ends
        while it waits counts for nothing, and resets nothing
  J14   the beat of a wake-up says the right number: the exchanges left to the member to say an act, this one
        counted -- never under 1, and 1 at the wake-up of the last silent passage before a fall
  M1    every `do` and `ask` routed gets an answer: a debt is due until it, through every parking and every
        launch (R12)
  M5    every message delivered to a member gives it a turn: it is delivered at the head of a launch that opens
        an exchange, never to one that continues a standing run -- it waits for the run's park; the try of a
        suspected member delivers whatever its run, and so does a launch on a run its standing task's bound
        holds [s.1377]
  H1    no member is suspected for a refusal of the house [107]
  H2    a message of a principal to a member is delivered by a launch of that member at the tick it is due,
        whatever its health [108]
  H3    no act of an earlier exchange is ever routed by a later launch [106]

A ZONE is a group of lines that share their invariants: `--zone <zone>` plays its lines alone, each with the
seeds and the verdict it has in the whole, so that a change to the dynamics replays the zones it touches, and the
whole once, at the end. Every line is of one zone, and the whole is the zones together. The lines, the runs and
the seconds below are those of `3000 --owed --transport message --jobs 12`, each zone played alone (2026-11-10,
748 s together); a zone of `final`'s batches alone has no line there.

  zone        lines     runs  seconds  its lines, and the invariants they judge
  review         17    51000        9  the scenario `review` -- the lock, the net, its timer, the machine cut: I1 I2 I3
                                       I4 I12
  reframe        17    51000       22  the scenario `reframe` -- the run, the upgrade, the edges, the stop: I1 I3 I4 I7
                                       I9 I11a I11b I12 I13 I18 I19 I20 M5
  extended        8    24000       28  `ext` -- the owed lines, which hold every invariant of the scenario, and the run
                                       kept across a kill, a season and the carriers: I13 I18
  bounds          9    27000       34  `ext` -- the bounds, the allowances, the timeout, the kill: I9 I10 I10e I10r I10p
                                       I12 I16 I17
  calendar        6    18000       22  `ext` -- the rings, the resume, the pause: I15 I23 I24
  recurrence     13    39000       53  `ext` -- the recurrence, its periods, its hour, its run, its slots: I21 I25 I26
                                       I27
  squad          12    36000       26  the scenario `squad` -- the members of one agent: I1 I4 I12 I13 I16 I18 I19
                                       I20 I22
  answer          -        -        -  the debt, `final` alone -- une-reponse-par-message: J1 J5
  relance         -        -        -  the debt, `final` alone -- la-relance-et-le-cycle: J2 J3 J9
  detector        -        -        -  the debt, `final` alone -- le-detecteur-de-fautes: J4
  transport       3   324000       85  the debt -- le-transport-par-message: J1 J3 J5 J9 I19 M1 M5
  failures        4   192000      254  the debt, seasons of 4 tasks -- les-echecs-du-tick: H1 H2 H3 J4 M1
  info            3    72000       26  the debt -- le-message-info: J8
  silence         6   432000        -  the debt -- le-silence-au-detecteur, in passages (le-battement-du-reveil):
                                       J9 J10 J12 J13 J14; with `final`'s five lines, 672000 runs in 358 s
                                       (`--jobs 8`, 2026-11-14)
  workers         4    12000        1  the scenario `workers` -- the clock and the cost of both transports, no
                                       verdict: I10 J3 M1 said as violations

Usage: python3 team-sim.py [runs] [--owed] [--transport final|message] [--only <scenario>] [--zone <zone>]
                           [--jobs <n>]
       python3 team-sim.py --trace <seed> <line> [final|message]
       python3 team-sim.py --trace <seed> <line of the debt> [<scenario> [<fault> [<agent>]]]
  --transport final    the lines of the tick and the debt as team 0.39.0 plays them
  --transport message  the lines of the tick and the debt under the transport by message, and the
                       workers' clock of both; absent, both transports play
  --only <scenario>    review, reframe, ext, squad, debt or workers alone
  --zone <zone>        the lines of one zone alone; exits 2 when the zone has no line under the transport
  --owed               exits 1 when a line does not hold its verdict
"""
import math
import os
import random
import sys
import zlib
from collections import Counter, defaultdict
from multiprocessing import Pool

OWNER = "owner"
TEAM = "team"                                 # the author of a ceremony's task and of the team's posts
EPS = 1e-9                                    # money compared to the micro-dollar
MAX_COST = 5
TIMEOUT = 2                                   # timeout:, in clock units
PERIOD_LEN, PERIODS = 3, 2                    # the daily rings at clock 3 and 6
CLOCK_END = PERIOD_LEN * PERIODS
RAISE = 15                                    # what the owner adds to a spent budget [76]
INTERVAL = 2                                  # [121] the duration of a recurrence by a duration, in clock units
CTX_LIMIT = 50                                # [120] the recurrence's context limit, in % of the window
CTX_STEPS = (None, 20, 40, 60)                # [120] what one launch adds to its run's context; None: unmeasured
HORIZON = 288                                 # the schedule's ticks a task is watched with nothing written


def counted(c):
    """-> a copy of a Counter, made by the dict's own update."""
    out = Counter()
    dict.update(out, c)
    return out


COPY = {dict: dict.copy, set: set.copy, list: list.copy, Counter: counted}   # the state's containers, copied flat


# -- the flags: what a line changes in the dynamics -------------------------------------------------

BASE = dict(lock="v2", tags=True, run="carrier", busy="member", upgrade="keep",
            work=True, edges=True, owner=True, handed="key", stop=True, spawn=True, unread="keep", delivered="parked",
            answers="re", entry="dag", timeout="response", transport="final")
WORK = 2                                      # a words is ready after 0 to WORK launches of work (message)
EXT = dict(live=True, count="launched", ring="one", timeout="response", lockbusy=True,
           kill="task", killrun="keep", killans="spare", resume="holders", manual="id",
           share="parts", season="keep", pause="owed", recur="skip", rehour="none", renew="limit",
           every="date", slot="owed", origin="none")


# -- the core ---------------------------------------------------------------------------------------

class Core:
    """The tick of a team. A scenario sets the class attributes and the hooks below."""

    MEMBERS = ()
    AGENT_OF = {}                             # member -> the agent that plays it (itself when absent)
    EDGES = {}                                # member -> the member it reports to
    PARALLEL = 3
    MAX_RETRY = 1
    CLOCKED = False                           # an abstract clock: timeout:, the answer before the release
    LOCKBUSY = False                          # a run whose wake lock is held is busy [45]
    STEPS = 30000

    def __init__(self, seed, flags, net=False, crash=0.0, upgrade=True, ext=None):
        self.rng = random.Random(seed)
        self.f = dict(BASE, **flags)
        self.net, self.crash, self.upgrade_on = net, crash, upgrade   # net: the TIMER, a tick at the next deadline
        self.cut = False             # [110] the machine stopped once
        self.net_alive = True        # the timer dies with the machine; the relaunch entry arms it again at logon
        self.timer = False           # a line that plays the timer's arming (`timer`): one stands, armed by a tick
        self.timer_ticks = set()     # the ticks a timer played
        self.entry = True            # [111] the HOUSE's one relaunch entry, laid by the team's start
        self.other = bool(self.f.get("house"))   # [111] a second team of the house needing its net, until it stops
        self.x = ext
        self.transport = self.f["transport"]  # the transport: `final` (team 0.39.0) or `message` (owed)
        self.standing = {}           # run key -> the task its run stands on, « relaunch me »: what the tick
        #                              reads at the agent's face; a key absent from here is parked (message)
        self.mind = {}               # run key -> the words the member still has to say, between two
        #                              launches: the member's own, the tick never reads it (message)
        self.k = min(self.PARALLEL, len(self.MEMBERS))   # [75] the wake-ups that may play together
        self.clock = 0
        self.bounds = {"wakes": None, "budget": None, "budget_wakes": None}   # message: launches of a task,
        #                              dollars, launches of a season -- a wake-up being one launch there
        self.killed = set()          # the tags a timeout ended
        self.journal = []
        self.version = 0
        self.memo = (None, None)
        self.base = None             # (events folded, the last of them, the state they give)
        self.now = 0
        self.ids = 0
        self.lock = None
        self.pending = False
        self.inside = None
        self.ticks = []
        self.running = {}            # key -> wake-up under way (the launcher's wake lock held)
        self.slots = set()           # the runs that stand (an upgrade forgets them)
        self.marks = set()           # the keys an upgrade kept (the engine's renewal mark) [50]
        self.sessions = {}           # key -> the harness session it plays in
        self.forgotten = set()       # the keys a kill made the team forget
        self.answered = defaultdict(set)      # (member, carrier) -> the keys that answered for it (I18)
        self.session_of = defaultdict(set)    # (member, carrier) -> the sessions that answered for it (I18)
        self.played_by = defaultdict(set)     # key -> the members that answered on it (I20)
        self.kill_beside = False
        self.parallel_seen = False   # two members of one agent played at once
        self.responses = []          # the house's responses.jsonl
        self.materials = {}          # run key -> material
        self.carriers = {}           # task -> its carrier [119]: its recurrence, its ceremony, or itself
        self.carried = defaultdict(set)       # key -> the (member, carrier) pairs that answered on it (I18)
        self.ctx = Counter()         # [120] run key -> the context its launches left, in % of the window
        self.tag_record = {}         # tag -> key handed (messages.jsonl)
        self.memory = defaultdict(dict)       # (member, task) -> memory of that conversation
        self.plans = {}              # (member, task) -> the fault its first wake-up plays
        self.attempts = Counter()
        self.violations = set()
        self.tick_count = 0
        self.upgraded = False
        self.schedule = True
        self.returned_seen = set()
        self.skipped = set()         # the periods whose span passed whole during a pause [83]
        rehour = (ext or {}).get("rehour", "none") != "none"
        self.hour0 = 1 if rehour else 0          # [117] the hour of the day the recurrence is posted at
        self.clock_end = CLOCK_END + (PERIOD_LEN - 1 if rehour else 0)   # the last day's later hours reached
        self.changed = None          # [117] (clock, hour, the periods sounded before) of the owner's change
        self.quiet = 0               # the schedule's ticks in a row that wrote nothing
        self.quiet_version = -1

    @property
    def clocked(self):
        return self.CLOCKED or self.x is not None

    @property
    def lockbusy(self):
        return self.x["lockbusy"] if self.x else self.LOCKBUSY

    def agent_of(self, member):
        return self.AGENT_OF.get(member, member)

    def watched(self):
        """-> whether the schedule may tick again: a task is watched until HORIZON of its ticks in a row
        write nothing -- then the run ends, and the check says whether its owner was told."""
        if self.version == self.quiet_version:
            self.quiet += 1
        else:
            self.quiet, self.quiet_version = 0, self.version
        return self.quiet < HORIZON

    # -- the hooks of a scenario ------------------------------------------------------------------
    def script(self, member, task, inbox, mem):
        return {}

    def schedule_may_leave(self, st):
        """-> whether the calendar line leaves once no task is open."""
        return True

    # -- the journal ------------------------------------------------------------------------------
    def nid(self):
        self.ids += 1
        return self.ids

    def append(self, **e):
        e.setdefault("id", self.nid())
        e["at"] = self.now
        if e["kind"] == "task":
            self.carriers[e["task"]] = e.get("recurrence") or e.get("ceremony") or e["task"]
        self.journal.append(e)
        self.version += 1
        return e

    def violate(self, code):
        self.violations.add(code)

    def carrier(self, task):
        """[119] -> what carries a task's run: the recurrence of an occurrence, the ceremony of a ring's task, the task
        itself otherwise."""
        return self.carriers.get(task, task)

    def unit(self, agent, task):
        """-> the key the team keeps a run under: (member, carrier) [119], the member [47], (member, task), or the
        agent [48]."""
        if self.f["run"] == "carrier":
            return (agent, self.carrier(task))
        if self.f["run"] == "member":
            return agent
        if self.f["run"] == "agent":
            return self.agent_of(agent)
        return (agent, task)

    def same_run(self, agent, task, other):
        """-> whether the memory of (agent, other) belongs to the run of (agent, task): what a run opened without its
        history forgets [33] -- under the carrier, the tasks of its carrier alone [119]."""
        if self.f["run"] == "member":
            return True
        if self.f["run"] == "carrier":
            return self.carrier(other) == self.carrier(task)
        return other == task

    # -- the replay -------------------------------------------------------------------------------
    def replay(self):
        """-> the state the journal says; read-only for its callers, memoized by version and folded on from
        the last state while the journal only grew -- a journal cut (an unreadable answer's end taken back)
        is folded again from its start."""
        if self.memo[0] == self.version:
            return self.memo[1]
        n, base = len(self.journal), self.base
        if base is not None and base[0] <= n and (base[0] == 0 or self.journal[base[0] - 1] is base[1]):
            st = {k: COPY[type(v)](v) if type(v) in COPY else v for k, v in base[2].items()}
            events = self.journal[base[0]:]
        else:
            st, events = self.fresh(), self.journal
        for e in events:
            self.fold(st, e)
        self.base = (n, self.journal[-1] if n else None, st)
        self.memo = (self.version, st)
        return st

    def fresh(self):
        """-> the state of an empty journal."""
        return {"tasks": {}, "messages": {}, "delivered": set(), "intents": {}, "launched": {},
               "ended": {}, "failed": {}, "killed": {}, "failures": Counter(), "terminals": set(),
               "delegations": [], "runs": {}, "done": set(), "stopped": set(), "returned": set(),
               "deferred": 0, "rung": Counter(),
               "budget_spent": 0, "budget_spent_n": 0, "wakes_spent": Counter(), "wakes_spent_n": 0, "cost": 0,
               "resumed": {}, "fell": set(), "season_at": 0, "paused": False, "debts": {}, "opening": {},
               "settles": Counter(), "recurred": Counter(), "recurred_since": Counter(), "rec_hour": None,
               "rec_since": -1, "rec_changed": 0, "measured": {}, "renewals": Counter()}

    def fold(self, st, e):
        """One event of the journal folded into the state."""
        debts = self.f["answers"] == "re"
        k = e["kind"]
        if k == "task":
            st["tasks"][e["task"]] = e
            if e.get("recurrence"):
                st["recurred"][e["period"]] += 1                 # [112] the period sounded by its occurrence
                st["recurred_since"][e["period"]] += 1
        elif k == "recurrence-skipped":
            st["recurred"][e["period"]] += 1                     # [112] sounded, nothing opened
            st["recurred_since"][e["period"]] += 1
        elif k == "recurrence-changed":                          # [117] the hour and since replaced, the periods kept
            st["rec_hour"], st["rec_since"], st["rec_changed"] = e["hour"], e["since"], e["id"]
            st["recurred_since"] = Counter()
        elif k == "post":
            st["messages"][e["id"]] = e
            task = e["task"]
            if debts and e["verb"] == "do" and e["to"] in self.MEMBERS:
                t = st["tasks"].get(task) or {}
                if e["from"] in self.MEMBERS:                    # [84] a delegation is its do
                    st["delegations"].append({"id": e["id"], "from": e["from"], "to": e["to"], "task": task})
                elif t.get("to") == e["to"] and task not in st["opening"]:
                    st["opening"][task] = e["id"]                # the task's opening message
                st["terminals"].discard((e["to"], task))         # a new round
            if (debts and e["verb"] in ("do", "ask") and e["to"] in self.MEMBERS
                    and (self.open_task(st, task) or self.f.get("debt_after_close"))):
                st["debts"][e["id"]] = None                      # [85] one debt, open
            if debts and e["verb"] == "info" and e["to"] in self.MEMBERS and self.f.get("info_debt"):
                st["debts"][e["id"]] = None                      # the variant: an info opens a debt (J8)
            if debts and e["verb"] == "re" and not e.get("info"):
                state = st["debts"].get(e["re"], "x")
                if state is None or (self.f.get("resettle") and isinstance(state, int)):
                    st["debts"][e["re"]] = e["id"]               # [85] the first answer settles it
                    st["settles"][e["re"]] += 1
                    cited = st["messages"][e["re"]]
                    if cited["verb"] == "do" and cited["to"] == e["from"]:
                        st["terminals"].add((e["from"], task))   # the delegate answered its do
            if e["to"] == OWNER and self.f["owner"]:
                st["delivered"].add(e["id"])                     # [36] its box reads it
            if e["verb"] == "stop":
                st["delivered"].add(e["id"])                     # a stop is delivered at once
        elif k == "wake-intent":
            st["intents"][e["tag"]] = e
            st["delivered"].update(e["messages"])
        elif k == "wake-launched":
            st["launched"][e["tag"]] = e
        elif k == "absorbed":                                    # [93] answered in place, never woken
            st["delivered"].update(e["messages"])
        elif k == "washed":                                      # the detector of 2026-10-12
            if st["debts"].get(e["re"], "x") is None:
                st["debts"][e["re"]] = "washed"
                st["settles"][e["re"]] += 1
        elif k == "wake-ended":
            st["ended"][e["tag"]] = e
            st["cost"] += e.get("cost", 0)
            i = st["intents"][e["tag"]]
            st["runs"][self.unit(i["agent"], i["task"])] = e["run"]   # the run that answered
            if e.get("context") is not None:
                st["measured"][e["run"]] = e["context"]          # [120] the run's last measure, an unmeasured end kept out
        elif k == "run-renewed":                                 # [120] the run of the recurrence left past its limit
            unit = self.unit(e["agent"], e["task"])
            if st["runs"].get(unit) == e["run"]:
                del st["runs"][unit]
            st["renewals"][unit] += 1
        elif k == "wake-killed":
            st["killed"][e["tag"]] = e
        elif k == "wake-failed":
            st["failed"][e["tag"]] = e
            st["cost"] += e.get("cost", 0)
            i = st["intents"][e["tag"]]
            if e.get("run") and self.f["unread"] == "keep":
                st["runs"][self.unit(i["agent"], i["task"])] = e["run"]   # [47] the run answered
            if not (self.f["spawn"] and e["reason"] == "launch-missing") and not e.get("house"):
                st["failures"][(i["agent"], i["task"])] += 1     # [43] no spawn, no retry spent; [107] the house's
            if e["final"] and i["task"] not in st["stopped"]:
                st["fell"].add((i["agent"], i["task"]))
                if debts:
                    st["terminals"].add((i["agent"], i["task"]))
            if not e["final"]:
                for mid in i["messages"]:
                    st["delivered"].discard(mid)                 # back in the inbox
        elif k == "terminal":
            st["terminals"].add((e["agent"], e["task"]))
        elif k == "delegation":
            st["delegations"].append(e)
        elif k == "ceremony-due":
            st["rung"][e["period"]] += 1
        elif k == "budget-spent":
            st["budget_spent"] += 1
            st["budget_spent_n"] += 1
        elif k == "budget-raised":                               # [76]
            st["budget_spent"] = 0
        elif k == "wakes-spent":
            st["wakes_spent"][e["task"]] += 1
            st["wakes_spent_n"] += 1
        elif k == "season":                                      # [82] the counts afresh
            st["cost"], st["budget_spent"], st["season_at"] = 0, 0, e["id"]
            if self.x and self.x.get("season") == "forget":
                st["runs"] = {}
        elif k == "paused":                                      # [83]
            st["paused"] = True
        elif k == "unpaused":
            st["paused"] = False
        elif k == "resumed":                                     # [67]
            task = e["task"]
            st["stopped"].discard(task)
            st["resumed"][task] = e["id"]
            st["wakes_spent"][task] = 0
            for slot in [s for s in st["failures"] if s[1] == task]:
                del st["failures"][slot]
            for slot in [s for s in st["fell"] if s[1] == task]:
                st["fell"].discard(slot)
                st["terminals"].discard(slot)
        elif k == "done":
            st["done"].add(e["task"])
            for mid, state in st["debts"].items():
                if state is None and st["messages"][mid]["task"] == e["task"]:
                    st["debts"][mid] = "close"                   # [84] the root's answer settles them all
        elif k == "stopped":
            st["stopped"].add(e["task"])
        elif k == "returned":
            st["returned"].add(e["message"])
            st["delivered"].add(e["message"])

    def open_task(self, st, task):
        return task in st["tasks"] and task not in st["done"] and task not in st["stopped"]

    def inbox(self, st, agent, task=None):
        return [m for m in st["messages"].values()
                if m["to"] == agent and m["id"] not in st["delivered"]
                and self.open_task(st, m["task"]) and (task is None or m["task"] == task)]

    def unended(self, st):
        return [t for t in st["intents"]
                if t not in st["ended"] and t not in st["failed"] and t not in st["killed"]]

    def reserved(self, st):
        """[75] the allowances of the intents without an end."""
        return sum(st["intents"][t].get("allowance") or 0 for t in self.unended(st))

    def exposure(self, st):
        """-> what the wake-ups under way may still spend: each its allowance, MAX_COST without one."""
        return sum(MAX_COST if st["intents"][t].get("allowance") is None else st["intents"][t]["allowance"]
                   for t in self.unended(st))

    def busy(self, st, agent, task):
        me = self.unit(agent, task)
        for tag in self.unended(st):
            i = st["intents"][tag]
            if self.f["busy"] == "member":
                if i["agent"] == agent:
                    return True                                      # [119] one wake-up per member, whatever its run
            elif self.f["busy"] == "task":
                if i["agent"] == agent and i["task"] == task:
                    return True
            elif self.unit(i["agent"], i["task"]) == me:
                return True                                          # [49] one wake-up per run
        if self.lockbusy:
            kept = st["runs"].get(me)
            if kept is not None and kept in self.running:
                return True                                          # [45] its wake lock still held
        return False

    def parent_of(self, st, agent, task):
        for d in reversed(st["delegations"]):
            if d["to"] == agent and d["task"] == task:
                return d["from"]
        return st["tasks"][task]["from"]

    def holders(self, st, task):
        t = st["tasks"][task]
        found = [] if (t["to"], task) in st["terminals"] else [t["to"]]
        for d in st["delegations"]:
            if d["task"] == task and (d["to"], task) not in st["terminals"] and d["to"] not in found:
                found.append(d["to"])
        return found

    # -- one tick -----------------------------------------------------------------------------------
    def tick(self, tid):
        """The lock of the tick -- v2: try, mark, release, then read the mark; `read-before-release`
        reads the mark before releasing; `no-mark` exits on a held lock."""
        self.tick_count += 1
        if self.lock is not None:
            if self.f["lock"] == "no-mark":
                return
            self.pending = True
            yield
            if self.lock is not None:
                self.relayed(tid)
                return
        self.lock = tid
        while True:
            if self.inside is not None:
                self.violate("I2")
            self.inside = tid
            self.pending = False
            self.arm("start")
            yield
            yield from self.reap()
            yield from self.rounds_in()
            if self.x:
                yield from self.ring()
            yield from self.wake()
            self.conclude()
            self.arm("end")
            self.inside = None
            if self.f["lock"] == "read-before-release":
                again = self.pending
                yield
                self.lock = None
                yield
            else:
                self.lock = None
                yield
                again = self.pending
            if again and self.lock is None:
                self.lock = tid
                continue
            return

    def arm(self, when):
        """The tick arms the team's timer at the end of each round, while the calendar line stands, and [s.1373] at
        its start, as soon as it holds the lock: a tick killed during its round leaves a timer standing. The next
        tick of the net is that timer's -- a line that plays the arming (`timer`) has no other net."""
        timer = self.f.get("timer")
        if timer and (when == "end" or timer["arm"] == "start"):
            self.timer = self.schedule

    def relayed(self, tid):
        """A timer's tick that found the lock held leaves without a round, its timer gone: owed, the timer arms the
        next all the same -- the tick that holds the lock may die before it arms one."""
        timer = self.f.get("timer")
        if timer and tid in self.timer_ticks and timer["relay"] == "always":
            self.timer = self.schedule

    def net_tick(self):
        """One tick of the net. Under a line that plays the arming, the timer takes its mark away and plays ONE tick
        by the console, which may FAIL before any lock (`fails`): owed, the timer arms the next itself (`relay`)."""
        timer = self.f.get("timer")
        if not timer:
            return self.spawn_tick()
        self.timer = False
        if self.rng.random() < timer["fails"]:
            self.timer = timer["relay"] != "none" and self.schedule
            return                                               # [s.1357] the next armed by the timer itself
        self.spawn_tick()
        self.timer_ticks.add(self.ticks[-1][0])

    def reap(self):
        st = self.replay()
        for tag in self.unended(st):
            i = st["intents"][tag]
            launched = st["launched"].get(tag)
            key = launched["run"] if launched else (self.tag_record.get(tag) if self.f["tags"] else None)
            if key is None:
                self.fail(st, i, "launch-missing")
                yield
                continue
            if launched is None:
                self.append(kind="wake-launched", tag=tag, run=key, late=True)   # read back by its tag
            body = next((r for r in self.responses if r["run"] == key and r["index"] == i["index"]), None)
            if self.clocked and key in self.running:
                w = self.running[key]
                overdue = w["tag"] == tag and self.clock - w["start"] >= TIMEOUT
                stray = any(r["run"] is None and r.get("handed") == key for r in self.responses)
                timeout = self.x["timeout"] if self.x else self.f["timeout"]
                if timeout == "response" and stray:
                    overdue = False                                  # [46] answered without its run: kept first
                if overdue and (body is None or timeout == "first"):
                    if body is not None or stray:
                        self.violate("I16")                          # a kept response killed
                    del self.running[key]
                    self.killed.add(tag)
                    self.fail(st, i, "wake-timeout")
                    yield
                    continue
                if body is None:
                    continue                                         # the wake-up plays
            elif key in self.running:
                continue
            if body is not None:
                step = CTX_STEPS[zlib.crc32(f"{key}:{i['index']}".encode()) % len(CTX_STEPS)]
                if step is not None:
                    self.ctx[key] += step                            # [120] what the launch left in its run
                self.append(kind="wake-ended", tag=tag, run=key, cost=body["cost"],
                            context=None if step is None else self.ctx[key])
                pair = (i["agent"], self.carrier(i["task"]), i.get("generation", 0))
                self.answered[pair].add(key)
                self.session_of[pair].add(self.sessions[key])
                self.carried[key].add(pair)
                self.played_by[key].add(i["agent"])
                self.route(self.replay(), i, body["body"], tag, body["cost"])
                yield
                continue
            # no response by (run, index): an answer kept without a run, or a dead wake-up
            if self.f["handed"] == "key":
                cand = [r for r in self.responses if r["run"] is None and r.get("handed") == key]
            else:
                cand = [r for r in self.responses if r["run"] is None
                        and self.agent_of(r["agent"]) == self.agent_of(i["agent"]) and r["at"] >= i["at"]]
            match = min(cand, key=lambda r: r["at"], default=None)
            if match is not None:
                match.setdefault("used", []).append(tag)
                self.fail(st, i, "run-unfound", cost=match["cost"])
            else:
                self.fail(st, i, "wake-dead")
            yield

    def fail(self, st, i, reason, cost=0, run=None):
        final = st["failures"][(i["agent"], i["task"])] >= self.MAX_RETRY
        if self.f["spawn"] and reason == "launch-missing":
            final = False                                            # [43] nothing was launched
        if i["task"] in st["stopped"]:
            self.append(kind="wake-failed", tag=i["tag"], final=True, reason=reason, cost=cost)
            return
        self.append(kind="wake-failed", tag=i["tag"], final=final, reason=reason, cost=cost, run=run)
        if final:                                                    # [104] its retries spent: the tick stops
            self.standing.pop(self.tag_record.get(i["tag"]), None)   # relaunching it; what it still had to
        #                                                              say waits the next message for it
        if final and self.f["answers"] == "re":
            # [88] the tick answers in place of the member every message of its wake-up that owes --
            # never the opening of a principal: the root escalates to it
            st = self.replay()
            for mid in i["messages"]:
                m = st["messages"][mid]
                if st["debts"].get(mid, "x") is None and mid != st["opening"].get(m["task"]):
                    self.post(st, "re", i["agent"], m["from"], m["task"], re=mid, meant="escalate",
                              final_of=reason)
                    st = self.replay()
            t = st["tasks"][i["task"]]
            if t["to"] == i["agent"] and t["from"] in (OWNER, TEAM):
                self.post(st, "escalate", i["agent"], self.told_of(t["from"]), i["task"], final_of=reason)
        elif final:
            self.append(kind="terminal", agent=i["agent"], task=i["task"])
            st = self.replay()
            self.post(st, "escalate", i["agent"], self.told_of(self.parent_of(st, i["agent"], i["task"])),
                      i["task"], final_of=reason)

    def told_of(self, author):
        """-> who hears of a final failure on a task: its author, the owner when the team wrote it -- a
        ceremony has no mandator for author."""
        return OWNER if author == TEAM else author

    def post(self, st, verb, frm, to, task, **extra):
        return self.append(kind="post", verb=verb, **{"from": frm}, to=to, task=task, **extra)

    def answers_of(self, st, a, task, body):
        """[84] -> the elements an intent of the script is written as: do and ask as
        they are; a reply as the answer to the ask it answers; done and escalate as the answer to the do
        the member holds -- the root's to the task's opening; a root that escalates ASKS the owner."""
        found = []
        if "do" in body:
            found.append({"do": body["do"]})
        if "ask" in body:
            found.append({"ask": body["ask"]})

        def latest(pred):
            mine = [m for m in st["messages"].values() if m["to"] == a and m["task"] == task
                    and m["id"] in st["delivered"] and pred(m)]
            owed = [m for m in mine if st["debts"].get(m["id"], "x") is None]
            return (owed or mine or [None])[-1]

        if "reply" in body:
            cited = latest(lambda m: m["verb"] == "ask" and m["from"] == body["reply"]["to"])
            if cited is not None:
                found.append({"re": cited["id"], "meant": "reply"})
        t = st["tasks"][task]
        root = t["to"] == a and t["from"] in (OWNER, TEAM)
        for verb in ("done", "escalate"):
            if not body.get(verb):
                continue
            if verb == "escalate" and root:
                found.append({"ask": {"to": t["from"]}, "meant": "escalate"})
                continue
            opening = st["opening"].get(task)
            cited = (st["messages"].get(opening) if root and opening is not None
                     else latest(lambda m: m["verb"] == "do"))
            if cited is not None:
                found.append({"re": cited["id"], "meant": verb})
        return found

    # -- what the tick reads of a run (message): standing or parked ---------------------------------
    def stands(self, st, a, task):
        """-> whether the run of (a, task) stands, « relaunch me »: read at the agent's face, never in
        the journal; under `final` a run never stands between two wake-ups."""
        return self.transport == "message" and self.standing.get(st["runs"].get(self.unit(a, task))) == task

    def stood(self, tag, task, park, stopped=False):
        """A launch ended: its run parks (« wait for a message ») or stands (« relaunch me »); on a task
        stopped meanwhile, what it still had to say on it is dropped and it stands on what is left."""
        key = self.tag_record.get(tag)
        if park:
            self.parked(key)
        elif stopped and key in self.mind:
            self.mind[key] = [one for one in self.mind[key] if one["task"] != task]
            self.repoint(key)
        elif key is not None:
            self.standing[key] = task

    def parked(self, key):
        self.standing.pop(key, None)
        self.mind.pop(key, None)

    def has_words(self, st, a, task):
        """-> whether the member still has words to say on the task (its own knowledge; the tick reads it
        nowhere -- the simulation's shortcut for « relaunch me » on a run standing on several tasks)."""
        key = st["runs"].get(self.unit(a, task))
        return self.transport == "message" and any(one["task"] == task for one in self.mind.get(key) or [])

    def repoint(self, key):
        """The task a standing run was last launched on closed: it stands on the next task it still has
        words for, or parks."""
        st = self.replay()
        left = [one["task"] for one in self.mind.get(key, []) if self.open_task(st, one["task"])]
        if left:
            self.standing[key] = left[0]
        else:
            self.parked(key)

    # -- the routing ----------------------------------------------------------------------------
    def route(self, st, i, body, tag, cost):
        a, task = i["agent"], i["task"]
        if self.transport == "message":                              # [96] a launch: its words, in order,
            self.stood(tag, task, body["park"], stopped=task in st["stopped"])   # each on its own task
            for one in body["words"]:
                t = one.get("task") or task
                if t not in st["stopped"]:                           # a stopped task: routed nowhere
                    self.route_words(self.replay(), dict(i, task=t), one["say"], cost)
            return
        if task in st["stopped"]:
            return                                                   # ended, routed nowhere
        if self.f["answers"] == "re":
            return self.route_re(st, i, self.answers_of(st, a, task, body), cost)
        self.route_verbs(st, i, body, cost)

    def route_words(self, st, i, one, cost):
        """[98] one words of a launch: an act is routed as it is read; a words that does not read as an act
        is said -- journalized, it opens nothing and kills nothing, the engine never repairs it."""
        a, task = i["agent"], i["task"]
        if not one:
            self.append(kind="said", agent=a, task=task)
            return
        if self.f["answers"] == "re":
            return self.route_re(st, i, self.answers_of(st, a, task, one), cost)
        self.route_verbs(st, i, one, cost)

    def refused(self, st, i, off, cost):
        """[35] an act off the edges: under `final` the whole answer is unreadable and the wake-up fails;
        under `message` the words alone is refused at the routing and the member is told (I11a)."""
        a, task = i["agent"], i["task"]
        if not self.f["edges"]:
            self.violate("I11a")
            return False
        if self.transport == "message":
            self.post(st, "info", TEAM, a, task, about=a, what="refused", to_=list(off))
            return True
        ended = self.journal.pop()                                   # the wake-ended just written
        self.version += 1
        self.fail(self.replay(), i, "response-unreadable", cost=cost, run=ended["run"])
        return True

    def route_verbs(self, st, i, body, cost):
        a, task = i["agent"], i["task"]
        off = []
        if "do" in body:
            off += [to for to in body["do"] if self.EDGES.get(to) != a]
        if "ask" in body and body["ask"]["to"] not in self.MEMBERS and body["ask"]["to"] != OWNER:   # [62]
            off.append(body["ask"]["to"])
        if off and self.refused(st, i, off, cost):
            return
        if "do" in body:
            for to in body["do"]:
                self.post(st, "do", a, to, task)
                self.append(kind="delegation", **{"from": a}, to=to, task=task)
        if "ask" in body:
            self.post(st, "ask", a, body["ask"]["to"], task)
        if "reply" in body:
            self.post(st, "reply", a, body["reply"]["to"], task)
        if body.get("done"):
            self.append(kind="terminal", agent=a, task=task)
            t = st["tasks"][task]
            if t["to"] == a and t["from"] in (OWNER, TEAM):
                self.append(kind="done", task=task)
            else:
                self.post(st, "done", a, self.parent_of(st, a, task), task)
        if "escalate" in body:
            self.append(kind="terminal", agent=a, task=task)
            self.post(st, "escalate", a, self.parent_of(st, a, task), task)

    def route_re(self, st, i, elements, cost):
        """[84] the elements in order: do posts, ask posts, answers -- each to the author
        of the message it cites, the root's answer to the opening resolving the task."""
        a, task = i["agent"], i["task"]
        off = []
        for one in elements:
            if "do" in one:
                off += [to for to in one["do"] if self.EDGES.get(to) != a]
            if "ask" in one and one["ask"]["to"] not in self.MEMBERS and one["ask"]["to"] not in (OWNER, TEAM):
                off.append(one["ask"]["to"])
            if "info" in one and one["info"]["to"] not in self.MEMBERS and one["info"]["to"] not in (OWNER, TEAM):
                off.append(one["info"]["to"])
        if off and self.refused(st, i, off, cost):
            return
        for one in elements:
            st = self.replay()
            if "do" in one:
                for to in one["do"]:
                    self.post(st, "do", a, to, task)
            elif "ask" in one:
                self.post(st, "ask", a, one["ask"]["to"], task, **({"meant": one["meant"]} if "meant" in one else {}))
            elif "info" in one:
                self.post(st, "info", a, one["info"]["to"], task)   # [114] no debt, no edge
            elif "re" in one:
                cited = st["messages"][one["re"]]
                state = st["debts"].get(one["re"], "x")
                if state == "washed":
                    continue                                         # an answer to a washed message: never relayed
                owed = state is None or (self.f.get("resettle") and isinstance(state, int))
                self.post(st, "re", a, cited["from"], cited["task"], re=one["re"], meant=one.get("meant", "re"),
                          info=not owed)
                if owed and one["re"] == st["opening"].get(cited["task"]):
                    self.append(kind="done", task=cited["task"])     # [86] the root's answer resolves it

    def rounds_in(self):
        """Step 3: a member whose delegates on a task are all terminal knows its round is in -- its own knowledge,
        which holds nothing: every message for a member launches it."""
        st = self.replay()
        for d in st["delegations"]:
            key = (d["from"], d["task"])
            mine = [x for x in st["delegations"] if (x["from"], x["task"]) == key]
            if all((x["to"], x["task"]) in st["terminals"] for x in mine):
                self.memory[key]["round_in"] = True
        yield

    def ring(self):
        """Step 4: each period come and not yet rung becomes ONE ceremony task; never under a pause, and
        a period whose span passed whole during the pause never rings [83]."""
        if self.replay()["paused"] and self.x["pause"] != "ignore":
            return
        for p in range(1, min(PERIODS, self.clock // PERIOD_LEN) + 1):
            st = self.replay()
            if st["rung"][p]:
                continue
            if p in self.skipped and self.x["pause"] != "catchup":
                continue
            if st["paused"] and self.x["pause"] != "ignore":
                return
            if st["paused"] or p in self.skipped:
                self.violate("I24")
            self.append(kind="ceremony-due", period=p, clock=self.clock)
            if self.x["ring"] == "two":
                yield                                                # a tick may die here
            self.ringing(st, f"C{p}", p)
            yield
        yield from self.recur()

    def recur(self):
        """Step 4, the RECURRENCE the owner posted [112]: each period come and not sounded opens ONE occurrence, a task
        to m with its opening do -- or, the occurrence before it still open, writes recurrence-skipped and opens nothing;
        never under a pause, a period passed whole during the pause never sounds."""
        if self.x["recur"] == "none":
            return
        judged = (self.clock // INTERVAL) * INTERVAL             # [121] the slot this ring reads
        for p in self.recurrence_due(self.replay()):
            st = self.replay()
            if p not in self.recurrence_due(st):                 # [117] judged again on the journal as it stands:
                continue                                         # a change written meanwhile moved its moment
            counted = st["recurred_since"][p] if self.x["rehour"] == "twice" else st["recurred"][p]
            if counted or (p in self.skipped and self.x["pause"] != "catchup"):
                continue
            if st["paused"] and self.x["pause"] != "ignore":
                return
            if st["paused"] or p in self.skipped:
                self.violate("I24")
            before = [t for t in st["tasks"] if t.startswith("Q") and self.open_task(st, t)]
            if self.x["origin"] == "task" and self.open_task(st, "O1"):
                before.insert(0, "O1")                           # [122] the origin, the recurrence's last occurrence
            if before and self.x["recur"] == "skip":
                self.append(kind="recurrence-skipped", period=p, open=before[0], clock=self.clock,
                            moment=self.slot_moment(p))
                yield
                continue
            if before:
                self.violate("I25")                                  # two occurrences open at once
            self.append(kind="task", task=f"Q{p}", **{"from": OWNER}, to="m", period=p, recurrence="R1",
                        clock=self.clock, moment=self.slot_moment(p))
            self.post(self.replay(), "do", OWNER, "m", f"Q{p}")
            yield
        if self.x["every"] == "interval" and not self.replay()["paused"]:
            if judged not in {e.get("moment") for e in self.journal
                            if e["kind"] == "recurrence-skipped" or (e["kind"] == "task" and e.get("recurrence"))}:
                self.violate("I27")                                  # [121] the slot it read, not counted

    def recurrence_hour(self, st):
        """-> the hour of the day and the since a tick reads of the recurrence [117]: the last `recurrence-changed`'s,
        the pose's before it -- or, under the variant `old`, the pose's always."""
        if st["rec_hour"] is None or self.x["rehour"] == "old":
            return self.hour0, -1
        return st["rec_hour"], st["rec_since"]

    def recurrence_due(self, st):
        """-> the periods (days) whose moment -- the day at the hour in force -- is past and comes after since; by a
        DURATION [121], the slot under way alone -- k x INTERVAL past, k from 0 at the pose (`late`: from 1) --, its
        period the slot's instant (`date`: the day it falls in, the variant)."""
        if self.x["every"] == "interval":
            k = self.clock // INTERVAL
            if k < (1 if self.x["slot"] == "late" else 0):
                return []
            moment = k * INTERVAL
            return [moment // PERIOD_LEN + 1 if self.x["slot"] == "date" else f"i{moment}"]
        hour, since = self.recurrence_hour(st)
        return [p for p in range(1, PERIODS + 1) if since < p * PERIOD_LEN + hour <= self.clock]

    def slot_moment(self, p):
        """[121] -> the instant a period of the recurrence stands for: a slot's, or, by a date, the clock it sounds at."""
        if self.x["every"] == "interval":
            return (self.clock // INTERVAL) * INTERVAL if not isinstance(p, str) else int(p[1:])
        return None

    def ringing(self, st, task, period, facilitator="m", participants=("r1", "r2")):
        """The ceremony task, a do (and a delegation under verbs) per participant -- the tick's ring and the hand's
        alike: nothing holds the facilitator, which receives each answer as a message; the task carries its
        ceremony, the daily."""
        self.append(kind="task", task=task, **{"from": TEAM}, to=facilitator, period=period, ceremony="daily")
        if self.f["answers"] == "re":
            self.post(self.replay(), "do", TEAM, facilitator, task)  # [86] the opening, to its facilitator
        for one in participants:
            self.post(self.replay(), "do", facilitator, one, task)
            if self.f["answers"] != "re":
                self.append(kind="delegation", **{"from": facilitator}, to=one, task=task)

    def launched_count(self, st, pred, as_tick):
        if as_tick and self.x["count"] == "intents":
            return sum(1 for i in st["intents"].values() if pred(i))
        if as_tick:
            return sum(1 for t, i in st["intents"].items() if pred(i) and (t in st["launched"] or t in self.tag_record))
        return sum(1 for t, i in st["intents"].items() if pred(i) and t in self.tag_record)

    def bounded(self, st, judged, a, task):
        """The bounds of step 5 (wakes, budget, budget-wakes), judged on `judged`. -> True when held."""
        b = self.bounds
        since = max(judged["resumed"].get(task, 0), judged["season_at"])
        on_task = lambda i: i["task"] == task and i["id"] > since
        anyone = lambda i: i["id"] > judged["season_at"]
        if b["wakes"] is not None and self.launched_count(judged, on_task, True) >= b["wakes"]:
            if not st["wakes_spent"][task]:
                if self.launched_count(st, on_task, False) < b["wakes"]:
                    self.violate("I10e")
                self.append(kind="wakes-spent", task=task)
                self.post(st, "escalate", TEAM, OWNER, task)
            return True
        if b["budget"] is not None and judged["cost"] >= b["budget"]:
            if not st["budget_spent"]:
                self.append(kind="budget-spent", unit="usd")
                self.post(st, "escalate", TEAM, OWNER, task)
            return True
        if b["budget_wakes"] is not None and self.launched_count(judged, anyone, True) >= b["budget_wakes"]:
            if not st["budget_spent"]:
                if self.launched_count(st, anyone, False) < b["budget_wakes"]:
                    self.violate("I10e")
                self.append(kind="budget-spent", unit="wakes")
                self.post(st, "escalate", TEAM, OWNER, task)
            return True
        return False

    def over_bound(self, st, task):
        b = self.bounds
        since = max(st["resumed"].get(task, 0), st["season_at"])
        return ((b["wakes"] is not None
                 and self.launched_count(st, lambda i: i["task"] == task and i["id"] > since, False) >= b["wakes"])
                or (b["budget"] is not None and st["cost"] >= b["budget"])
                or (b["budget_wakes"] is not None
                    and self.launched_count(st, lambda i: i["id"] > st["season_at"], False) >= b["budget_wakes"]))

    def wake(self):
        first = self.replay() if self.x else None
        if self.x and first["paused"] and self.x["pause"] != "ignore":
            return                                                   # [83] nobody woken under the pause
        for a in self.MEMBERS:
            st = self.replay()
            tasks = sorted({m["task"] for m in self.inbox(st, a)}
                           | {t for t in st["tasks"] if self.stands(st, a, t) or self.has_words(st, a, t)})
            while tasks:
                task = tasks.pop(0)
                st = self.replay()
                if self.x and st["paused"] and self.x["pause"] != "ignore":
                    return
                box = self.inbox(st, a, task)
                key = st["runs"].get(self.unit(a, task))
                stands = self.transport == "message" and key in self.standing   # its run stands (any task)
                here = stands and (self.standing[key] == task or self.has_words(st, a, task))   # with words on it
                spent = stands and (st["wakes_spent"].get(self.standing[key]) or st["budget_spent"])
                if stands and not spent and self.f["delivered"] == "parked":
                    box = []                                         # [s.1377] nothing is delivered to a run that
                #                                                      stands: its messages wait for its park, and
                #                                                      open the launch that follows it -- a turn; a
                #                                                      run its standing task's bound holds is continued
                #                                                      no more, and takes them (no starvation)
                if here and not self.open_task(st, task):
                    self.repoint(key)                                # the task closed: what else it has to say
                    if key in self.standing and self.standing[key] not in tasks:
                        tasks.append(self.standing[key])
                    continue
                if (self.f["work"] and stands and not here and self.open_task(st, self.standing[key])
                        and not (st["wakes_spent"].get(self.standing[key]) or st["budget_spent"])):
                    continue                                         # [105] under work: a run relaunchable on its standing
                #                                                      task takes no other task's head (T7); held by
                #                                                      that task's bound, it does -- no starvation
                if not box and not here:
                    continue                                         # an empty head relaunches the standing task
                #                                                      alone
                if self.busy(st, a, task):
                    continue                                         # [49] its run plays: next wake-up
                if self.x and self.bounded(st, st if self.x["live"] else first, a, task):
                    continue
                if len(self.unended(st)) >= self.PARALLEL:
                    self.append(kind="deferred", agent=a, task=task)
                    continue
                allowance = None
                if self.x and self.x["share"] in ("parts", "reserve") and self.bounds["budget"] is not None:
                    rest = self.bounds["budget"] - st["cost"] - self.reserved(st)
                    if rest <= 0:
                        under = self.unended(st)
                        if len(under) < self.k and all(st["intents"][t].get("seen") == st["cost"] for t in under):
                            self.violate("I10p")
                        self.append(kind="deferred", agent=a, task=task, reserved=True)
                        continue
                    allowance = (rest if self.x["share"] == "reserve"
                                 else math.floor(min((self.bounds["budget"] - st["cost"]) / self.k, rest) * 1e6) / 1e6)
                kept = st["runs"].get(self.unit(a, task))
                run = kept
                if kept in self.forgotten:
                    run = None
                renewed = run is not None and self.renewing(st, a, task, run)
                if run is not None and self.first_on_occurrence(st, a, task):
                    last = self.last_measure(run)                    # I21 judged on the journal, apart from the fold
                    if renewed != (last is not None and last >= CTX_LIMIT):
                        self.violate("I21")                          # past its limit and kept, or renewed under it
                if renewed:
                    self.append(kind="run-renewed", agent=a, task=task, recurrence=st["tasks"][task]["recurrence"],
                                run=run, used=st["measured"].get(run), limit=CTX_LIMIT)
                    run = None                                       # [120] a new run, named after the recurrence
                lost = run is not None and run not in self.slots and run not in self.marks
                if lost and self.f["upgrade"] in ("newrun", "nohistory"):
                    run = None                                       # [33] a new run
                    if self.f["upgrade"] == "nohistory":
                        for k in [k for k in self.memory if k[0] == a and self.same_run(a, task, k[1])]:
                            self.memory[k] = {}
                if stands and box and not spent:
                    self.violate("M5")                               # delivered to a launch that continues a run
                tag = f"t{self.nid()}"
                before = self.ids + 1
                fresh = run is None or (lost and self.f["upgrade"] == "newkey")
                index = 1 if fresh else 1 + len([r for r in self.responses if r["run"] == run])
                if self.x and self.over_bound(st, task):
                    self.violate("I10")
                if (self.x and self.bounds["budget"] is not None
                        and st["cost"] + self.exposure(st) + (MAX_COST if allowance is None else allowance)
                        > self.bounds["budget"] + EPS):
                    self.violate("I10r")
                if self.x and st["paused"]:
                    self.violate("I24")
                intent = self.append(kind="wake-intent", tag=tag, agent=a, task=task, run=run,
                                     messages=[m["id"] for m in box], index=index, allowance=allowance,
                                     seen=st["cost"], relaunch=stands,
                                     generation=self.replay()["renewals"][self.unit(a, task)])
                assert intent["id"] == before
                yield
                if run is not None and run not in self.slots:
                    if self.f["upgrade"] == "keep" and run in self.marks:
                        self.marks.discard(run)                      # [50] the engine renews it under its key
                        self.slots.add(run)
                    elif self.f["upgrade"] != "newkey":
                        self.fail(self.replay(), intent, "launch-failed: run-unknown")
                        yield
                        continue
                if run is not None and run in self.running:
                    self.violate("I17" if self.running[run]["answered"] else "I19")
                    self.fail(self.replay(), intent, "launch-failed: run-busy")
                    yield
                    continue
                key = self.launch(intent, a, task, run, box)
                yield                                                # the tick may die here: a launch hidden
                self.append(kind="wake-launched", tag=tag, run=key)
                yield

    def first_on_occurrence(self, st, agent, task):
        """[120] -> whether the member's next wake-up is its FIRST on an occurrence of a recurrence that carries a
        limit -- the one moment its run may change: an occurrence is never cut between two runs."""
        if not (self.x and self.x["renew"] != "none" and (st["tasks"].get(task) or {}).get("recurrence")):
            return False
        return not any(i["agent"] == agent and i["task"] == task for i in st["intents"].values())

    def renewing(self, st, agent, task, run):
        """[120] -> whether the first wake-up on a new occurrence renews the recurrence's run: its last measure kept at
        `wake-ended` reached the limit (owed); `never`, `every` the variants that break I21."""
        if not self.first_on_occurrence(st, agent, task):
            return False
        used = st["measured"].get(run)
        return {"limit": used is not None and used >= CTX_LIMIT, "never": False, "every": True}[self.x["renew"]]

    def last_measure(self, run):
        """-> the context the last measured `wake-ended` of the run says, read on the journal itself; None."""
        return next((e["context"] for e in reversed(self.journal)
                     if e["kind"] == "wake-ended" and e["run"] == run and e.get("context") is not None), None)

    def launch(self, intent, a, task, run, box):
        opening = run is None
        key = run if run is not None else f"k{self.nid()}"
        if opening:
            self.slots.add(key)                                      # the reservation
            self.sessions[key] = f"s{self.nid()}"                    # a new harness session
        elif run not in self.slots:
            key = f"k{self.nid()}"                                   # upgrade "newkey": the session, a new key
            self.slots.add(key)
            self.sessions[key] = self.sessions[run]
            if run in self.materials:
                self.materials[key] = self.materials[run]
        if any(w["agent"] == a and not w["answered"] for w in self.running.values()):
            self.violate("I19")                                      # one member, two wake-ups at once
        if task.startswith("C") and self.f["entry"] == "door" and not opening:
            self.violate("I22")                                      # [55] a resume never opens a door
        if self.f["work"]:
            material = self.materials.setdefault(key, ("clone", key))
        else:
            material = ("home", self.agent_of(a))
        for other in self.running.values():
            if other["agent"] == a and other["material"] == material and self.f["work"]:
                self.violate("I13")
        if not self.f["work"] and any(o["agent"] == a for o in self.running.values()):
            self.violate("I13")
        self.attempts[(a, task)] += 1
        fault = self.plans.get((a, task)) if self.attempts[(a, task)] == 1 else None
        self.tag_record[intent["tag"]] = key
        self.running[key] = {"agent": a, "task": task, "tag": intent["tag"], "box": box, "key": key,
                             "relaunch": bool(intent.get("relaunch")),
                             "left": self.rng.randint(1, 6), "fault": fault, "opening": opening,
                             "material": material, "index": intent["index"], "start": self.clock,
                             "answered": False, "allowance": intent.get("allowance")}
        if len([w for w in self.running.values() if not w["answered"]]) > self.PARALLEL:
            self.violate("I10")
        playing = defaultdict(set)
        for w in self.running.values():
            playing[self.agent_of(w["agent"])].add(w["agent"])
        if any(len(who) >= 2 for who in playing.values()):
            self.parallel_seen = True                                # two members of one agent at once
        return key

    def kill(self, st, task):
        """`stop --kill <task>`: the wake-ups under way that the flag names are ended (`wake-killed`)."""
        holders = set(self.holders(st, task))
        for key, w in list(self.running.items()):
            if w["answered"]:
                if self.x["killans"] == "spare" or w["task"] != task:
                    continue                                         # [58] its answer is kept: the reap ends it
                self.violate("I16")
            if w["task"] == task or (self.x["kill"] == "member" and w["agent"] in holders):
                if w["task"] != task:
                    self.violate("I9")
                if any(self.open_task(st, t) and t != task and (w["agent"] == st["tasks"][t]["to"]
                       or any(d["to"] == w["agent"] and d["task"] == t for d in st["delegations"]))
                       for t in st["tasks"]):
                    self.kill_beside = True
                del self.running[key]
                self.append(kind="wake-killed", tag=w["tag"], agent=w["agent"], task=w["task"], run=key)
                if self.x["killrun"] == "forget":
                    self.forgotten.add(key)

    def conclude(self):
        st = self.replay()
        for task in list(st["done"] | st["stopped"]):
            for mid, m in st["messages"].items():
                if m["task"] == task and mid not in st["delivered"] and mid not in self.returned_seen:
                    self.returned_seen.add(mid)
                    if m["to"] == OWNER:
                        self.violate("I11b")
                    self.append(kind="returned", message=mid, to=m["from"])
        st = self.replay()
        if self.schedule and not any(self.open_task(st, t) for t in st["tasks"]) and self.schedule_may_leave(st):
            self.schedule = False
            self.append(kind="schedule-off")

    # -- the processes ----------------------------------------------------------------------------
    def spawn_tick(self):
        self.ticks.append([self.nid(), None])
        self.ticks[-1][1] = self.tick(self.ticks[-1][0])

    def step_tick(self, entry):
        tid, gen = entry
        try:
            if self.crash and self.rng.random() < self.crash and self.lock == tid:
                raise StopIteration
            next(gen)
        except StopIteration:
            if self.lock == tid:
                self.lock = None
            if self.inside == tid:
                self.inside = None
            self.ticks.remove(entry)

    def steppable(self, key):
        """-> whether a wake-up can move: a hung one never does, a late or slow one once overdue."""
        w = self.running[key]
        if not self.clocked or w["answered"]:
            return True
        if w["fault"] == "hang":
            return False
        if w["fault"] in ("late", "slow"):
            return self.clock - w["start"] >= TIMEOUT
        return True

    def step_wakeup(self, key):
        w = self.running[key]
        if self.clocked and w["answered"]:
            del self.running[key]                                    # the wake lock released
            self.spawn_tick()                                        # --on-end
            return
        w["left"] -= 1
        if w["left"] > 0 and not (self.clocked and w["fault"] in ("late", "slow")):
            return
        if self.clocked:
            w["answered"] = True                                     # the response kept, the lock still held
        else:
            del self.running[key]
        cost = self.rng.randint(1, MAX_COST)
        if w.get("allowance") is not None:
            cost = min(cost, w["allowance"])                         # [75] the run's cap holds the allowance
        if w["fault"] == "crash":
            if w["opening"]:
                self.slots.discard(key)                              # the reservation taken back
            if hasattr(self, "flows"):
                self.flows[key].append(("opened", w["tag"]))         # [106] the exchange opened, the harness dead
        elif w["fault"] in ("unconducted", "slow") and w["opening"]:
            self.slots.discard(key)
            r = {"agent": w["agent"], "run": None, "index": None, "at": self.now, "cost": cost,
                 "body": {}, "own": w["tag"]}
            if self.f["handed"] == "key":
                r["handed"] = key
            self.responses.append(r)
        else:
            self.responses.append({"agent": w["agent"], "run": key, "index": w["index"],
                                   "at": self.now, "cost": cost, "body": self.answer(key, w), "own": w["tag"]})
        timer = self.f.get("timer")
        if not self.clocked and not (timer and self.rng.random() < timer["lost"]):
            self.spawn_tick()                                        # --on-end -- lost with its launch under a line
            #                                                          that plays the timer: the net alone reaps it

    def answer(self, key, w):
        """-> what a launch answers: under `final` the script's whole answer, the acts of the wake-up; under
        `message` the words of THIS launch and whether the run parks -- a scenario whose agent says its
        words itself answers in that form already."""
        body = self.script(w["agent"], w["task"], w["box"], self.memory[(w["agent"], w["task"])]) \
            if self.decides(w) else {}
        if self.transport == "message" and "words" not in body:
            body = self.words_of(key, body, w["task"])
        return body

    def decides(self, w):
        """-> whether the member decides at this launch: the scripts of the lines decide on a head -- a
        relaunch with an empty head works on what the member already decided; an agent that decides at
        every launch says so."""
        return not (self.transport == "message" and w["relaunch"] and not w["box"])

    def words_of(self, key, body, task):
        """[96] the generic member under `message`: what it decided on this head joins what it still had
        to say, each act a words ready after 0 to WORK launches of work; a launch says the first words
        ready -- none when none is -- and the run parks when nothing is left to say."""
        mind = self.mind.setdefault(key, [])
        for one in self.split(body):
            mind.append({"say": one, "task": task, "ready": self.rng.randint(0, WORK)})
        for one in mind:
            one["ready"] -= 1
        ready = next((one for one in mind if one["ready"] < 0), None)
        if ready is not None:
            mind.remove(ready)
        return {"words": [ready] if ready else [], "park": not mind}

    def split(self, body):
        """-> the words of a script's answer, one per act: do, ask, reply, done, escalate."""
        out = []
        for verb in ("do", "ask", "reply", "done", "escalate"):
            if verb in body:
                out.append({verb: body[verb]})
        return out

    # -- the checks every scenario shares ---------------------------------------------------------
    def check_identity(self):
        """I18 [119]: one key and one session per run (member, carrier), never two carriers of a member on one key or in
        one session; I13: one clone per run, never changed, never shared by two runs; I20: a key and a session, one
        member."""
        def two_carriers(pairs):
            return any(len({p[1] for p in pairs if p[0] == one}) > 1 for one in {p[0] for p in pairs})

        for pair in self.answered:
            if len(self.answered[pair]) > 1 or len(self.session_of[pair]) > 1:
                self.violate("I18")                                  # a run split, or renamed
        by_session = defaultdict(set)
        for pair, sessions in self.session_of.items():
            for s in sessions:
                by_session[s].add(pair)
        if any(two_carriers(pairs) for pairs in list(self.carried.values()) + list(by_session.values())):
            self.violate("I18")                                      # two carriers of a member on one key, one session
        if self.f["work"]:
            clones = defaultdict(set)
            for pair, keys in self.answered.items():
                if len({self.materials[k] for k in keys}) > 1:
                    self.violate("I13")                              # a run worked in two clones
                for k in keys:
                    clones[self.materials[k]].add(pair)
            if any(len(pairs) > 1 for pairs in clones.values()):
                self.violate("I13")                                  # two runs worked in one clone
        if any(len(who) > 1 for who in self.played_by.values()):
            self.violate("I20")                                      # one key, two members
        if any(len({p[0] for p in pairs}) > 1 for pairs in by_session.values()):
            self.violate("I20")                                      # one session, two members

    def check_delivery(self, st):
        seen = Counter()
        for tag, i in st["intents"].items():
            if tag in st["ended"]:
                seen.update(i["messages"])
        if any(n > 1 for n in seen.values()):
            self.violate("I3")

    def check_money(self, st):
        kept = sum(r["cost"] for r in self.responses)
        counted = sum(e.get("cost", 0) for e in self.journal if e["kind"] in ("wake-ended", "wake-failed"))
        unconducted = [r for r in self.responses if r["run"] is None]
        if any(len(r.get("used", [])) != 1 or r["used"][0] != r["own"] for r in unconducted) or abs(kept - counted) > EPS:
            self.violate("I12")

    def check_killed(self):
        if any(r["own"] in self.killed for r in self.responses):
            self.violate("I16")                                      # a wake-up whose answer is kept, killed

    def died_of_upgrade(self):
        died = any(e["kind"] == "wake-failed" and e["final"] and "run-unknown" in e["reason"]
                   for e in self.journal)
        if died:
            self.violate("I7")
        return died

    def told_owner(self, st, task):
        """-> whether an open task is left open for a reason the owner was told: a bound reached, or a
        final failure escalated to the owner."""
        if st["budget_spent"] or st["wakes_spent"][task]:
            return True
        return any(m["verb"] == "escalate" and m["to"] == OWNER and m["task"] == task
                   and m.get("final_of") for m in st["messages"].values())

    def trace(self):
        for e in self.journal:
            e = dict(e)
            kind = e.pop("kind")
            e.pop("at", None)
            print(f"  {kind:14} " + " ".join(f"{k}={v}" for k, v in e.items()))


# -- the scenario `review`: the lock protocol of the tick -------------------------------------------

class Review(Core):
    """m -> r1 r2 r3, one task from the owner: m delegates to the three, r2 asks m a question, m
    replies; r3's first wake-up dies; the owner posts a change of course once."""

    MEMBERS = ("m", "r1", "r2", "r3")
    EDGES = {"r1": "m", "r2": "m", "r3": "m"}
    PARALLEL = 4
    STEPS = 20000

    def script(self, agent, task, inbox, mem):
        verbs = [m.get("meant", m["verb"]) for m in inbox]
        if agent == "m":
            if "do" in verbs and not mem.get("delegated"):
                mem["delegated"] = True
                return {"do": ["r1", "r2", "r3"]}
            if "ask" in verbs:
                ask = next(m for m in inbox if m.get("meant", m["verb"]) == "ask")
                return {"reply": {"to": ask["from"]}}
            if mem.get("round_in"):
                return {"done": True}
            return {}
        if agent == "r2":
            return {"done": True} if "reply" in verbs else {"ask": {"to": "m"}}
        return {"done": True}

    def run(self):
        self.plans[("r3", "T1")] = "crash"                           # its first wake-up dies, on-end fires
        self.append(kind="task", task="T1", **{"from": OWNER}, to="m")
        self.post(self.replay(), "do", OWNER, "m", "T1")
        self.spawn_tick()
        posted, steps = False, 0
        while True:
            steps += 1
            self.now += 1
            if steps > self.STEPS:
                self.violate("no-termination")
                break
            st = self.replay()
            choices = [("tick", e) for e in self.ticks] + [("wake", k) for k in self.running]
            netting = self.net and self.schedule and self.net_alive and (self.timer or not self.f.get("timer"))
            if netting and self.rng.random() < 0.05:
                choices.append(("net", None))
            if not posted and self.rng.random() < 0.1 and self.open_task(st, "T1"):
                choices.append(("post", None))
            if self.f.get("cut") and not self.cut and self.rng.random() < 0.02:
                choices.append(("cut", None))
            if self.cut and not self.net_alive and self.f["cut"] == "relaunch" and self.entry:
                choices.append(("logon", None))
            if self.other and self.rng.random() < 0.03:
                choices.append(("other-stop", None))
            if not choices:
                if netting and not self.net_idle(st) and self.watched():
                    choices = [("net", None)]
                else:
                    break
            kind, arg = self.rng.choice(choices)
            if kind == "tick":
                self.step_tick(arg)
            elif kind == "wake":
                self.step_wakeup(arg)
            elif kind == "net":
                self.net_tick()
            elif kind == "cut":
                self.cut_machine()
            elif kind == "other-stop":
                self.other_stopped(st)
            elif kind == "logon":
                self.net_alive = True                                # [110] the relaunch entry plays one tick
                self.spawn_tick()                                    # at logon, which arms the timer again
            else:
                posted = True
                self.post(st, "info", OWNER, "m", "T1")
                self.spawn_tick()
        self.check()
        return self.violations

    def other_stopped(self, st):
        """[111] the house's other team stops: its need of the net ends. Owed (`shared`): the house's entry leaves only
        when no team of the house needs it any more -- this team still does while T1 is open; the variant `one-removes`
        removes it with the stop of one team, the way an entry per team was removed."""
        self.other = False
        if self.f["house"] == "one-removes" or not self.open_task(st, "T1"):
            self.entry = False

    def cut_machine(self):
        """[110] the machine stops: every tick and every wake-up under way dies with it -- no response, no
        on-end, the locks released, the marks kept -- and the timer with them."""
        self.cut = True
        self.ticks, self.lock, self.inside = [], None, None
        self.running = {}
        self.net_alive = False

    def net_idle(self, st):
        """-> whether a tick of the net can change nothing any more: the task settled, its line gone or no
        holder left -- the horizon of a task."""
        if not self.open_task(st, "T1"):
            return not self.schedule
        return not self.holders(st, "T1") and not any(self.inbox(st, a, "T1") for a in self.MEMBERS) \
            and not self.unended(st) and not self.standing

    def check(self):
        st = self.replay()
        self.died_of_upgrade()
        if self.schedule and not self.open_task(st, "T1"):
            self.violate("I1")
        if "T1" not in st["done"] and not self.told_owner(st, "T1"):
            self.violate("I1")
        for tag in self.unended(st):
            self.violate("I4")
        for a in self.MEMBERS:
            if self.inbox(st, a) and not self.told_owner(st, "T1"):
                self.violate("I4")
        self.check_delivery(st)
        self.check_money(st)


# -- the scenario `reframe`: the dynamics of the reframings --------------------------------------------

class Reframe(Core):
    """The members m (manager), r1 and r2 (reviewers), each its own agent, edges r1 -> m, r2 -> m.
    T1: m asks the owner, then delegates to r1 and r2; r2 asks m, m replies;
    r1 and r2 answer, m answers: resolved; r2's first answer may stray off the edges. T2, posted at a
    random time: m delegates to r1, r1 escalates, m escalates to the owner, who stops it. Extended:
    T3 answered at its first answer, T4 stopped with --kill then resumed, the daily rung by the tick at its
    periods and at hand, the bounds, timeout:, a pause, a season, a budget raised, and the owner's recurrence to m:
    its occurrences Q<p>, one per period, a period skipped while the occurrence before it is open [112]."""

    MEMBERS = ("m", "r1", "r2")
    EDGES = {"r1": "m", "r2": "m"}
    PARALLEL = 3
    P_FAIL, P_STRAY = 0.25, 0.3

    def __init__(self, seed, flags, net=False, crash=0.0, upgrade=True, ext=None):
        super().__init__(seed, flags, net, crash, upgrade, ext)
        self.MAX_RETRY = 2 if ext else 1
        self.t3_posted = self.t4_posted = not ext
        self.t2_posted = self.replied = self.stop_tried = False
        self.t4_holders = []
        self.t4_resumed = self.manual_rung = self.raised = self.seasoned = False
        self.paused_once = self.unpaused_once = False
        self.pause_until = 0

    def script(self, agent, task, inbox, mem):
        verbs = [m.get("meant", m["verb"]) for m in inbox]
        froms = [(m.get("meant", m["verb"]), m["from"]) for m in inbox]
        if agent == "m" and task.startswith("C"):                    # a ceremony: its facilitator answers the
            return {"done": True} if ("done" in verbs or "escalate" in verbs) else {}   # opening once an answer is in
        if task.startswith(("C", "Q", "O")):                         # a ceremony, an occurrence [112], an origin [122]
            return {"done": True}
        if agent == "m" and task == "T3":
            if not mem.get("delegated"):
                mem["delegated"] = True
                return {"do": ["r1", "r2"]}
            return {"done": True} if ("done" in verbs or "escalate" in verbs) else {}
        if task == "T3":
            return {"done": True}
        if agent == "m" and task == "T4":
            if not mem.get("delegated") or ("info" in verbs and not mem.get("round_in")):
                mem["delegated"] = True
                return {"do": ["r1"]}
            return {"done": True} if ("done" in verbs or mem.get("round_in")) else {}
        if task == "T4":
            return {"done": True}
        if agent == "m" and task == "T1":
            if not mem.get("asked"):
                mem["asked"] = True
                return {"ask": {"to": OWNER}}
            if ("reply", OWNER) in froms and not mem.get("delegated"):
                mem["delegated"] = True
                return {"do": ["r1", "r2"]}
            if ("ask", "r2") in froms:
                return {"reply": {"to": "r2"}}
            if mem.get("round_in"):
                return {"done": True}
            return {}
        if agent == "m" and task == "T2":
            if not mem.get("delegated"):
                mem["delegated"] = True
                return {"do": ["r1"]}
            if "escalate" in verbs:
                return {"escalate": "blocked by the build"}
            return {}
        if agent == "r1":
            return {"done": True} if task == "T1" else {"escalate": "the PR does not build"}
        if agent == "r2":
            if mem.get("stray") and not mem.get("strayed"):
                mem["strayed"] = True
                return {"do": ["r1"]}                                # off the edges: r1 reports to m
            if "reply" in verbs:
                return {"done": True}
            if not mem.get("asked"):
                mem["asked"] = True
                return {"ask": {"to": "m"}}
            return {}
        return {}

    def schedule_may_leave(self, st):
        return self.t2_posted and not self.x                         # a declared daily keeps the line

    def ringing(self, st, task, period, facilitator="m", participants=("r1", "r2")):
        super().ringing(st, task, period, facilitator, participants)

    # -- the owner and the machine --------------------------------------------------------------
    def owner_actions(self, st):
        acts = []
        if not self.t2_posted:
            acts.append("post-T2")
        if not self.t3_posted:
            acts.append("post-T3")
        if not self.t4_posted:
            acts.append("post-T4")
        if (self.x and "T4" in st["tasks"] and self.open_task(st, "T4") and not self.t4_resumed
                and any(w["task"] == "T4" for w in self.running.values())):
            acts.append("kill-T4")
        ask = [m for m in st["messages"].values() if m["verb"] == "ask" and m["to"] == OWNER and m["task"] == "T1"]
        if ask and not self.replied and self.open_task(st, "T1"):
            acts.append("reply")
        if ("T2" in st["tasks"] and self.open_task(st, "T2") and not self.stop_tried and not self.unended(st)
                and (not self.holders(st, "T2") if self.f["answers"] != "re" else
                     any(m["verb"] == "ask" and m["to"] == OWNER and m["task"] == "T2"
                         and m.get("meant") == "escalate" for m in st["messages"].values()))):
            acts.append("stop-T2")
        if (self.x and not self.manual_rung
                and not any(self.open_task(st, t) for t in st["tasks"] if t.startswith("C"))):
            acts.append("ring-daily")
        if self.x and "T4" in st["stopped"] and not self.t4_resumed and not st["budget_spent"]:
            acts.append("resume-T4")
        if (self.x and st["budget_spent"] and not self.raised and self.bounds["budget"] is not None
                and self.x["share"] in ("parts", "reserve")):
            acts.append("raise")
        if self.x and self.x.get("season") in ("keep", "forget") and not self.seasoned and st["tasks"]:
            acts.append("season")
        if (self.x and self.x["rehour"] != "none" and self.changed is None and st["recurred"][1]
                and self.clock < self.clock_end):                # [117] the hour changed once a period sounded
            acts.append("rehour")
        if self.x and self.x["pause"] != "none":
            if not self.paused_once and any(self.open_task(st, t) for t in st["tasks"]):
                acts.append("pause")
            if st["paused"] and not self.unpaused_once and self.clock >= self.pause_until:
                acts.append("unpause")
        if (self.upgrade_on and not self.upgraded and not self.running and not self.ticks
                and any(k in self.slots for k in st["runs"].values())):
            acts.append("upgrade")
        return acts

    def act(self, what):
        st = self.replay()
        if what in ("post-T2", "post-T3", "post-T4"):
            task = what[5:]
            setattr(self, f"t{task[1]}_posted", True)
            self.append(kind="task", task=task, **{"from": OWNER}, to="m")
            self.post(st, "do", OWNER, "m", task)
            self.spawn_tick()
        elif what == "kill-T4":
            to = self.holders(st, "T4")
            self.t4_holders = list(to)
            self.kill(st, "T4")
            self.append(kind="stopped", task="T4")
            for one in to:
                self.post(st, "stop", OWNER, one, "T4")
            self.spawn_tick()
        elif what == "ring-daily":
            self.manual_rung = True
            if self.x["manual"] == "id":
                e = self.append(kind="ceremony-due", period=f"m{self.ids + 1}", clock=self.clock)
                self.ringing(self.replay(), f"CM{e['id']}", e["period"])
            else:
                p = self.clock // PERIOD_LEN + 1
                if p > PERIODS or self.replay()["rung"][p]:
                    return
                self.append(kind="ceremony-due", period=p, clock=self.clock)
                self.ringing(self.replay(), f"C{p}", p)
            self.spawn_tick()
        elif what == "resume-T4":
            self.t4_resumed = True
            fell = [a for a, t in sorted(st["fell"]) if t == "T4"]
            to = (list(dict.fromkeys(self.t4_holders + fell)) if self.x["resume"] == "holders"
                  else [st["tasks"]["T4"]["to"]])
            self.append(kind="resumed", task="T4")
            st = self.replay()
            for one in to:
                self.post(st, "info", OWNER, one, "T4")
            self.spawn_tick()
        elif what == "rehour":                                   # [117] team recurrence R1 --every: a new hour
            hour = self.rng.choice([0, PERIOD_LEN - 1])
            self.changed = (self.clock, hour, {p for p in range(1, PERIODS + 1) if st["recurred"][p]})
            self.append(kind="recurrence-changed", hour=hour, since=self.clock, clock=self.clock)
            self.spawn_tick()
        elif what == "pause":
            self.paused_once = True
            self.pause_until = min(CLOCK_END, self.clock + self.rng.choice([0, 1, PERIOD_LEN, PERIOD_LEN + 1]))
            self.append(kind="paused")
        elif what == "unpause":
            self.unpaused_once = True
            self.append(kind="unpaused")
            self.spawn_tick()
        elif what == "season":
            self.seasoned = True
            self.append(kind="season")
            self.spawn_tick()
        elif what == "raise":
            self.raised = True
            self.bounds["budget"] += RAISE
            self.append(kind="budget-raised", budget=self.bounds["budget"])
            self.spawn_tick()
        elif what == "reply":
            self.replied = True
            self.post(st, "reply", OWNER, "m", "T1")
            self.spawn_tick()
        elif what == "stop-T2":
            self.stop_tried = True
            to = self.holders(st, "T2")
            for one in to:
                self.post(st, "stop", OWNER, one, "T2")
            if to or self.f["stop"]:
                self.append(kind="stopped", task="T2")
            self.spawn_tick()
        elif what == "upgrade":
            self.upgraded = True
            if self.f["upgrade"] == "keep":
                self.marks |= self.slots
            self.slots.clear()

    def net_idle(self, st):
        opened = [t for t in st["tasks"] if self.open_task(st, t)]
        if self.x:
            if any(not st["rung"][p] and p not in self.skipped
                   for p in range(1, min(PERIODS, self.clock // PERIOD_LEN) + 1)):
                return False
            counted = st["recurred_since"] if self.x["rehour"] == "twice" else st["recurred"]
            if self.x["recur"] != "none" and any(not counted[p] and p not in self.skipped
                                                 for p in self.recurrence_due(st)):
                return False
            if any(self.clock - w["start"] >= TIMEOUT and not w["answered"] for w in self.running.values()):
                return False
            playing = {w["tag"] for w in self.running.values()}
            if any(t not in playing for t in self.unended(st)):
                return False
            if st["budget_spent"]:
                return True
            opened = [t for t in opened if not st["wakes_spent"][t]]
            if not opened:
                return True
        if not opened:
            return not self.schedule
        return not self.standing and all(not self.holders(st, t) and not any(self.inbox(st, a, t) for a in self.MEMBERS)
                                         for t in opened)

    def clock_moves(self):
        if self.clock < self.clock_end:
            return True
        return any(not w["answered"] and w["fault"] in ("hang", "late") and self.clock - w["start"] < TIMEOUT
                   for w in self.running.values())

    def run(self):
        pairs = (("m", "T1"), ("m", "T2"), ("r1", "T1"), ("r1", "T2"), ("r2", "T1"))
        faults = ["crash", "unconducted"]
        if self.x:
            pairs += (("m", "T3"), ("r2", "T3"), ("r1", "C1"), ("r1", "T4"))
            faults += ["hang", "late"]
            self.bounds = {"wakes": self.rng.choice([None, None, 8, 10]),
                           "budget": self.rng.choice([None, None, 30, 45]),
                           "budget_wakes": self.rng.choice([None, None, 16, 20])}
        for a, task in pairs:
            if self.rng.random() < self.P_FAIL:
                self.plans[(a, task)] = self.rng.choice(faults)
        if "r2" not in [a for a, _ in self.plans] and self.rng.random() < self.P_STRAY:
            self.memory[("r2", "T1")]["stray"] = True
        self.append(kind="task", task="T1", **{"from": OWNER}, to="m")
        self.post(self.replay(), "do", OWNER, "m", "T1")
        if self.x and self.x["origin"] != "none":                    # [122] the recurrence born of a task open to m:
            self.append(kind="task", task="O1", **{"from": OWNER}, to="m")   # `team recurrence --task O1 --every`
            self.post(self.replay(), "do", OWNER, "m", "O1")
        self.spawn_tick()
        steps = 0
        while True:
            steps += 1
            self.now += 1
            if steps > (2000 if self.x else 30000):
                self.violate("no-termination")
                break
            st = self.replay()
            choices = [("tick", e) for e in self.ticks] + [("wake", k) for k in self.running
                                                           if self.steppable(k)]
            acts = self.owner_actions(st)
            if acts and self.rng.random() < 0.15:
                choices += [("act", a) for a in acts]
            elif "kill-T4" in acts and self.rng.random() < 0.3:
                choices.append(("act", "kill-T4"))
            if self.net and self.schedule and self.rng.random() < 0.05:
                choices.append(("net", None))
            if self.x and self.clock_moves() and self.rng.random() < 0.05:
                choices.append(("time", None))
            if not choices:
                if acts:
                    choices = [("act", a) for a in acts]
                elif self.x and self.clock_moves():
                    choices = [("time", None)]
                elif self.net and self.schedule and not self.net_idle(st) and self.watched():
                    choices = [("net", None)]
                else:
                    break
            kind, arg = self.rng.choice(choices)
            if kind == "tick":
                self.step_tick(arg)
            elif kind == "wake":
                self.step_wakeup(arg)
            elif kind == "act":
                self.act(arg)
            elif kind == "net":
                self.spawn_tick()
            elif kind == "time":
                p = self.clock // PERIOD_LEN
                if (self.x and st["paused"] and 1 <= p <= PERIODS and not st["rung"][p]
                        and (self.clock + 1) // PERIOD_LEN > p):
                    self.skipped.add(p)
                self.clock += 1
        self.check()
        return self.violations

    def check_ext(self, st):
        if not self.schedule:
            self.violate("I1")
        if "T2" in st["tasks"] and "T2" not in st["stopped"] and self.stop_tried:
            self.violate("I9")
        manual = [t for t in st["tasks"] if t.startswith("CM")]
        occurrences = [t for t in st["tasks"] if t.startswith(("Q", "O"))]
        for task in ["T1", "T3", "T4"] + [f"C{p}" for p in range(1, PERIODS + 1)] + manual + occurrences:
            if (task in st["tasks"] and task not in st["done"] and task not in st["stopped"]
                    and not self.told_owner(st, task)):
                self.violate("I1")
        for tag in self.unended(st):
            self.violate("I4")
        for a in self.MEMBERS:
            if any(not self.told_owner(st, m["task"]) for m in self.inbox(st, a)):
                self.violate("I4")
        if st["budget_spent"] > 1 or any(n > 1 for n in st["wakes_spent"].values()):
            self.violate("I10")
        told = sum(1 for m in st["messages"].values() if m["from"] == TEAM and m["verb"] == "escalate")
        if told != st["budget_spent_n"] + st["wakes_spent_n"]:
            self.violate("I10")
        if self.bounds["budget"] is not None and st["cost"] > self.bounds["budget"] + self.PARALLEL * MAX_COST:
            self.violate("I10")
        if self.bounds["budget"] is not None and st["cost"] > self.bounds["budget"] + EPS:
            self.violate("I10r")
        lost, epoch = Counter(), {}
        for e in self.journal:
            if e["kind"] == "resumed":
                epoch[e["task"]] = e["id"]
            if (e["kind"] == "wake-failed" and not e["final"]
                    and not (self.f["spawn"] and e["reason"] == "launch-missing")):
                i = st["intents"][e["tag"]]
                lost[(i["agent"], i["task"], epoch.get(i["task"], 0))] += 1
        if any(n > self.MAX_RETRY for n in lost.values()):
            self.violate("I10")
        if self.t4_resumed and "T4" not in st["done"]:
            since = st["resumed"].get("T4", 0)
            told_after = any(m["to"] == OWNER and m["task"] == "T4" and m["id"] > since
                             and (m.get("final_of") or m["from"] == TEAM) for m in st["messages"].values())
            if not (st["budget_spent"] or st["wakes_spent"]["T4"] or told_after):
                self.violate("I23")
        for p in range(1, PERIODS + 1):
            task = f"C{p}"
            if p in self.skipped and self.x["pause"] != "catchup":
                if st["rung"][p]:
                    self.violate("I24")
                continue
            if st["rung"][p] != 1 or task not in st["tasks"]:
                self.violate("I15")
            if any(e["kind"] == "ceremony-due" and e["period"] == p and e["clock"] < p * PERIOD_LEN
                   for e in self.journal):
                self.violate("I15")
        if any(t not in st["done"] and not self.told_owner(st, t) for t in manual):
            self.violate("I15")
        if self.x["recur"] != "none":                                # [112] each period sounded once, never two open
            for p in (range(1, PERIODS + 1) if self.x["every"] != "interval" else ()):
                if p in self.skipped and self.x["pause"] != "catchup":
                    if st["recurred"][p]:
                        self.violate("I24")
                    continue
                owed = 1                                             # [117] a period whose moment under the new
                if self.changed is not None:                         # hour is not after the change, and that had
                    at, hour, before = self.changed                  # not sounded, never sounds
                    if p not in before and p * PERIOD_LEN + hour <= at:
                        owed = 0
                if st["recurred"][p] != owed:
                    self.violate("I25")
            opened = sorted((e["id"], e["task"]) for e in self.journal if e["kind"] == "task"
                            and (e.get("recurrence") or e["task"] == "O1"))   # [122] the origin counts as one
            for (_, one), (born, _) in zip(opened, opened[1:]):
                closed = next((e["id"] for e in self.journal if e["kind"] in ("done", "stopped") and e.get("task") == one),
                              None)
                if closed is None or closed > born:
                    self.violate("I25")
            changed = next((e for e in self.journal if e["kind"] == "recurrence-changed"), None)
            for e in self.journal:                                   # [117] I26: no period sounds before its moment
                if e["kind"] == "recurrence-skipped" or (e["kind"] == "task" and e.get("recurrence")):
                    if e.get("moment") is not None:                  # [121] a slot: never before its instant, once
                        if e["clock"] < e["moment"] or sum(1 for o in self.journal if o.get("moment") == e["moment"]
                                                           and o["kind"] in ("task", "recurrence-skipped")) > 1:
                            self.violate("I26" if e["clock"] < e["moment"] else "I25")
                        continue
                    hour = changed["hour"] if changed is not None and e["id"] > changed["id"] else self.hour0
                    if e["clock"] < e["period"] * PERIOD_LEN + hour:
                        self.violate("I26")
        for tag, i in st["intents"].items():
            if self.tag_record.get(tag) is None:
                continue
            timed = [e for e in self.journal if e["kind"] == "wake-failed" and e["tag"] == tag
                     and e["reason"] == "wake-timeout"]
            if len(timed) > 1:
                self.violate("I16")
            kept = any(r["own"] == tag for r in self.responses)
            if timed and kept:
                self.violate("I16")

    def check(self):
        st = self.replay()
        died = self.died_of_upgrade()
        self.check_identity()
        if self.x:
            self.check_ext(st)
            self.check_delivery(st)
            self.check_money(st)
            return
        if "T1" not in st["done"] or "T2" not in st["stopped"] or self.schedule:
            if not died:
                if "T2" in st["tasks"] and "T2" not in st["stopped"] and self.stop_tried:
                    self.violate("I9")
                else:
                    self.violate("I1")
        for tag in self.unended(st):
            self.violate("I4")
        for a in self.MEMBERS:
            if self.inbox(st, a):
                self.violate("I4")
        self.check_delivery(st)
        self.check_money(st)


# -- the scenario `squad`: three members of one agent --------------------------------------------------

class Squad(Core):
    """m (agents/ag1) and dev1 dev2 dev3 (all three agents/ag2), dev1 dev2 dev3 -> m. T1: m delegates
    to the three devs at once; T2, posted at a random time, to dev1, who may still play T1; C1, the
    daily rung at a random time, its entry elected by the DAG; the upgrade once the daily rung; T3
    posted once the upgrade played, to dev2, and the daily rung again, C2 -- every member resumes its
    daily run after the upgrade (the run of a member is kept per carrier [119]: the daily carries C1 and
    C2, T1 T2 T3 each their own)."""

    MEMBERS = ("m", "dev1", "dev2", "dev3")
    DEVS = ("dev1", "dev2", "dev3")
    AGENT_OF = {"m": "agents/ag1", "dev1": "agents/ag2", "dev2": "agents/ag2", "dev3": "agents/ag2"}
    EDGES = {"dev1": "m", "dev2": "m", "dev3": "m"}
    PARALLEL = 4
    CLOCKED = True
    LOCKBUSY = True
    STEPS = 20000
    P_FAIL = 0.2

    def __init__(self, seed, flags, net=False, crash=0.0, upgrade=True, ext=None):
        super().__init__(seed, dict(flags, answers="verbs"), net, crash, upgrade, ext)
        self.t2_posted = self.t3_posted = self.rung = self.rung_again = False

    def script(self, member, task, inbox, mem):
        if member == "m":
            if task.startswith("C"):
                return {"done": True}
            if not mem.get("delegated"):
                mem["delegated"] = True
                return {"do": {"T1": list(self.DEVS), "T2": ["dev1"], "T3": ["dev2"]}[task]}
            return {"done": True}
        return {"done": True}

    def owner_actions(self, st):
        acts = []
        if not self.t2_posted:
            acts.append("post-T2")
        if not self.rung:
            acts.append("ring")
        if self.rung and not self.upgraded and not self.running and not self.ticks and st["runs"]:
            acts.append("upgrade")
        if self.upgraded and not self.t3_posted:
            acts.append("post-T3")
        if self.upgraded and not self.rung_again:
            acts.append("ring-again")
        return acts

    def act(self, what):
        if what in ("post-T2", "post-T3"):
            task = what[5:]
            setattr(self, f"t{task[1]}_posted", True)
            self.append(kind="task", task=task, **{"from": OWNER}, to="m")
            self.post(self.replay(), "do", OWNER, "m", task)
        elif what == "ring":
            self.rung = True
            self.append(kind="ceremony-due", ceremony="daily", period="d")
            self.ringing(self.replay(), "C1", "d", "m", self.DEVS)
        elif what == "ring-again":                                   # the daily's next day, after the upgrade
            self.rung_again = True
            self.append(kind="ceremony-due", ceremony="daily", period="d2")
            self.ringing(self.replay(), "C2", "d2", "m", self.DEVS)
        elif what == "upgrade":
            self.upgraded = True
            if self.f["upgrade"] == "keep":
                self.marks |= self.slots
            self.slots.clear()
            return
        self.spawn_tick()

    def schedule_may_leave(self, st):
        return False                                                 # the daily keeps the line

    def idle(self, st):
        return not self.unended(st) and not any(self.inbox(st, a) for a in self.MEMBERS) and not self.standing

    def run(self):
        for member, task in (("m", "T1"), ("m", "T2"), ("dev1", "T1"), ("dev1", "T2"),
                             ("dev2", "T1"), ("dev3", "C1"), ("m", "C1")):
            if self.rng.random() < self.P_FAIL:
                self.plans[(member, task)] = self.rng.choice(["crash", "unconducted", "slow"])
        self.append(kind="task", task="T1", **{"from": OWNER}, to="m")
        self.post(self.replay(), "do", OWNER, "m", "T1")
        self.spawn_tick()
        steps = 0
        while True:
            steps += 1
            self.now += 1
            if steps > self.STEPS:
                self.violate("no-termination")
                break
            st = self.replay()
            choices = [("tick", e) for e in self.ticks] + [("wake", k) for k in self.running
                                                           if self.steppable(k)]
            acts = self.owner_actions(st)
            if acts and self.rng.random() < 0.15:
                choices += [("act", a) for a in acts]
            if self.net and self.rng.random() < 0.05:
                choices.append(("net", None))
            playing = any(not w["answered"] for w in self.running.values())
            if playing and self.rng.random() < 0.05:
                choices.append(("time", None))
            if not choices:
                if acts:
                    choices = [("act", a) for a in acts]
                elif playing:
                    choices = [("time", None)]
                elif self.net and not self.idle(st) and self.watched():
                    choices = [("net", None)]
                else:
                    break
            kind, arg = self.rng.choice(choices)
            if kind == "tick":
                self.step_tick(arg)
            elif kind == "wake":
                self.step_wakeup(arg)
            elif kind == "act":
                self.act(arg)
            elif kind == "time":
                self.clock += 1
            else:
                self.spawn_tick()
        self.check()
        return self.violations

    def told(self, st, task):
        return any(m["verb"] == "escalate" and m["to"] == OWNER and m["task"] == task
                   for m in st["messages"].values())

    def check(self):
        st = self.replay()
        self.died_of_upgrade()
        if any(t not in st["done"] and not self.told(st, t) for t in ("T1", "T2", "T3", "C1", "C2")):
            self.violate("I1")
        if self.unended(st) or any(not self.told(st, m["task"]) for a in self.MEMBERS for m in self.inbox(st, a)):
            self.violate("I4")
        self.check_delivery(st)
        self.check_money(st)
        self.check_killed()
        self.check_identity()


# -- the scenario `debt`: the answer, the debt, the deadlock and the failure detector ------------------

INTERVAL = 1                                  # the base of a suspicion's interval: one tick of the schedule
LONG_EXCHANGES = 10                           # [115] the exchanges a long root keeps its opening, informing
HOUSE_REFUSALS = 2                            # [107] the launches of a member the HOUSE refuses before any harness
PROBES = 3                                    # the probes of the detector of 2026-10-12
LAUNCHES = 24                                 # `launches:` -- the launches of a task (`wakes:` under final)
BUDGET_LAUNCHES = 4 * LAUNCHES                # `budget-launches:` -- the launches of a season (message)


class Debt(Core):
    """m (the root), r1 and r2 reporting to m, the owner. A generic agent (the agent's profile `debt`):
    it answers on the debts it was woken with, now or later (0.7 a message), a delegated worker may ask its
    peer (`cross`) or its supervisor (`up`), a root delegates to both and answers the
    opening once the answers it wants -- one or two -- are in; a later answer now and then (information); a stray do off the edges (2 %);
    STUBBORN, a relance gets nothing back. The faults: flaky, an outage (the first 3 to 6 wake-ups of a
    member fail), broken for good -- for a worker or for the root -- each failure a crash, a hang (killed past
    timeout:) or garbage (an unreadable answer: under `final` the wake-up fails, under `message` the words
    is said and lost -- the debt it carried stays due); a HOUSE outage ([107]: the first HOUSE_REFUSALS
    launches of a member refused by the house before any harness -- no harness ran, nothing of the member).
    A SEASON is 4 tasks one after the other, the detector's state carried; each task watched for HORIZON
    ticks of the schedule. Under `message` each run has a FLOW [106]: every launch writes its `opened`
    with its tag, its words and its `verdict`, and the reader routes from the exchange the launch opened --
    found by its tag from the rank the journal last kept (none for the first task's launches: a journal
    written before the rank was kept) --, or, under the variant `reader: first`, from the first `opened` met
    as team 0.40.2 did."""

    MEMBERS = ("m", "r1", "r2")
    EDGES = {"r1": "m", "r2": "m"}
    PARALLEL = 3
    CLOCKED = True
    LOCKBUSY = True
    STEPS = 8000

    def __init__(self, seed, v, scen, faults, tasks=1, stubborn=False):
        super().__init__(seed, dict(answers="re", resettle=v.get("resettle", False),
                                    debt_after_close=v.get("debt_after_close", False),
                                    info_debt=v.get("info_debt", False),
                                    transport=v.get("transport", "final")))
        self.v, self.scen, self.faults, self.season_len = v, scen, faults, tasks
        self.stubborn = stubborn is True
        self.silent_p = 0.1 if stubborn == "silent" else 0.0   # an incorrect agent: parks saying nothing
        self.stuck_p = 0.1 if stubborn == "stuck" else 0.0     # another: its run stands and says nothing, for good
        self.held_over = defaultdict(list)     # the answers a silent parking left owed
        self.eager = {a: self.rng.random() for a in self.MEMBERS}
        self.abandoned = set()                 # the variant `abandon`: the debts a parking forgot
        self.season_launches = 0               # `budget-launches:` counts them
        self.current = None
        self.opened_at = 0
        self.outage = {}
        self.woke = set()                      # the members woken once in the season (m broken after its 1st)
        self.tolerance = Counter()             # [93] one silent retry more per repentance
        self.streak = Counter()                # the failures of a member since its last answer
        self.finals = Counter()                # its final failures in a row: the interval doubles
        self.failures = Counter()              # team 0.34.0: a member's failures, never reset
        self.suspects = {}                     # [93] member -> {"interval", "next"}
        self.faulty = {}                       # 2026-10-12: member -> probes spent
        self.left_out = set()
        self.guard = set()                     # the tasks whose wakes: are spent
        self.owner_seen = {}                   # task -> the last journal id the owner acted on
        self.owner_posts = Counter()
        self.acted = set()
        self.fates = []
        self.waking = None
        self.flows = defaultdict(list)         # [106] run key -> the flow: ("opened", tag), ("words", one), ("verdict",)
        self.flow_marks = {}                   # run key -> the rank the journal kept at the run's last wake-ended
        self.house_left = Counter({faults["house"]: HOUSE_REFUSALS}) if faults.get("house") else Counter()
        self.house_falls = Counter()           # [107] the variant: a member's house refusals counted as falls
        self.passages = []                     # [115] each wake-up and its continuations: {id, agent, task, owing,
        #                                        beat, end, waiting} -- `end` the journal id its run parked at
        self.asked_owner = False               # the root asked its principal, and says nothing while it waits

    # -- the season -------------------------------------------------------------------------------
    def open_next(self):
        n = len(self.fates) + 1                # the next task opens its own launches; a run that stands on a
        self.current = f"T{n}"                 # settled one is continued there (`continued`)
        self.opened_at = self.clock
        self.owner_seen[self.current] = self.ids
        self.append(kind="task", task=self.current, **{"from": OWNER}, to="m")
        self.post(self.replay(), "do", OWNER, "m", self.current)
        self.spawn_tick()

    def told(self, st, task):
        """-> whether the owner was told something on the task, or acted on it, or its wakes: are spent."""
        return (task in self.acted or task in self.guard
                or any(m["to"] == OWNER and m["task"] == task for m in st["messages"].values()))

    def told_since(self, st, task):
        key = (self.version, task, self.owner_seen[task])
        if getattr(self, "_told", (None,))[0] != key:
            self._told = (key, any(m["to"] == OWNER and m["task"] == task and m["id"] > self.owner_seen[task]
                                   for m in st["messages"].values()))
        return self._told[1]

    # -- reading the debts ------------------------------------------------------------------------
    def known(self, st, a, task):
        return [m for m in st["messages"].values() if m["to"] == a and m["task"] == task and m["id"] in st["delivered"]]

    def owed(self, st, a, task):
        return [m["id"] for m in self.known(st, a, task)
                if st["debts"].get(m["id"], "x") is None and m["id"] not in self.abandoned]

    def asking(self, st, a, task):
        """-> whether a waits on the owner: its question, until an answer of the owner cites it (`waits_owner`), or
        the team's notice about it, after the owner's last word on the task -- a notice the member answered since
        (a wake-up of its ended after it) is stale: it asks nothing any more."""
        if self.waits_owner(st, a, task):
            return True
        last = max([m["id"] for m in st["messages"].values() if m["from"] == OWNER and m["task"] == task] or [0])
        ended = max([e["id"] for t, e in st["ended"].items()
                     if st["intents"][t]["agent"] == a and st["intents"][t]["task"] == task] or [0])
        return any(m["task"] == task and m["to"] == OWNER and m["id"] > last
                   and m["verb"] == "notice" and m.get("about") == a and m["id"] > ended
                   for m in st["messages"].values())

    def waits_for(self, st, a, task):
        found = {m["to"] for m in st["messages"].values() if m["from"] == a and m["task"] == task
                 and m["to"] in self.MEMBERS and st["debts"].get(m["id"], "x") is None}
        return found | ({OWNER} if self.asking(st, a, task) else set())

    def held(self, st, a, task, m):
        s = self.suspects.get(a) if self.v.get("detector") == "eventual" else None
        if s is not None and self.clock < s["next"]:
            return True                                          # [93] it receives nothing in its interval
        if a in self.faulty or a in self.left_out:
            return True                                          # 2026-10-12: nothing but the probes
        return False

    def receivable(self, st, a, task):
        return [m for m in self.inbox(st, a, task) if not self.held(st, a, task, m)]

    def rides(self, m):
        """[114] -> whether a message launches nobody: a MEMBER's info -- it rides the head of its recipient's next
        launch, whatever its cause; the variant `info_wakes` launches on it as on any message."""
        return m["verb"] == "info" and m["from"] in self.MEMBERS and not self.v.get("info_wakes")

    def idle(self, st, a, task):
        return (not self.playing(a) and a not in self.left_out
                and not [m for m in self.receivable(st, a, task) if not self.rides(m)])

    def playing(self, a):
        key = (self.version, len(self.running), tuple(self.running))
        if getattr(self, "_playing", (None,))[0] != key:
            st = self.replay()
            self._playing = (key, {w["agent"] for w in self.running.values()}
                             | {st["intents"][t]["agent"] for t in self.unended(st)})
        return a in self._playing[1]

    def deadlocked(self, st, task):
        key = (self.version, tuple(self.running), task, self.clock)
        if getattr(self, "_deadlocked", (None,))[0] == key:
            return self._deadlocked[1]
        found = self._deadlocked_now(st, task)
        self._deadlocked = (key, found)
        return found

    def _deadlocked_now(self, st, task):
        s = {a for a in self.MEMBERS if self.idle(st, a, task)}
        changed = True
        while changed:
            changed = False
            for a in list(s):
                if any(b not in s for b in self.waits_for(st, a, task)):
                    s.discard(a)
                    changed = True
        return frozenset(s)

    def reach(self, st, a, task):
        seen, stack = set(), list(self.waits_for(st, a, task))
        while stack:
            b = stack.pop()
            if b not in seen:
                seen.add(b)
                if b in self.MEMBERS:
                    stack.extend(self.waits_for(st, b, task))
        return seen

    def bottom(self, st, a, task):
        """[91] a stands at the bottom of the deadlocked set: in it, every member it reaches reaching it back."""
        if a not in self.deadlocked(st, task):
            return False
        return all(b in self.MEMBERS and a in self.reach(st, b, task) for b in self.reach(st, a, task))

    def in_cycle(self, st, a, task):
        seen, stack = set(), [m["to"] for m in st["messages"].values() if m["from"] == a and m["task"] == task
                              and m["to"] in self.MEMBERS and st["debts"].get(m["id"], "x") is None]
        while stack:
            b = stack.pop()
            if b == a:
                return True
            if b not in seen:
                seen.add(b)
                stack.extend(m["to"] for m in st["messages"].values() if m["from"] == b and m["task"] == task
                             and m["to"] in self.MEMBERS and st["debts"].get(m["id"], "x") is None)
        return False

    def silence_since(self, st, a, task):
        """[115] -> the id the member's silence on the task counts from: its last routed act there (never the tick's in
        its place), the task's opening, its last silence fall; under the variant `count: delivery`, as before team
        0.48.0, its last delivery."""
        if self.v.get("count") == "delivery":
            acts = [i["id"] for i in st["intents"].values() if i["agent"] == a and i["task"] == task and i["messages"]
                    and not i.get("relance")]
        else:
            acts = [m["id"] for m in st["messages"].values() if m["from"] == a and m["task"] == task and m.get("by") != "tick"]
        falls = [e["id"] for e in self.journal if e["kind"] == "silence" and e["agent"] == a and e["task"] == task]
        return max(acts + falls + [st["tasks"][task]["id"]])

    def unanswered(self, st, task):
        """-> the questions to the owner on the task that no answer of the owner cites yet, in order."""
        cited = {m.get("re") for m in st["messages"].values() if m["from"] == OWNER and m["verb"] == "re"}
        return [m for m in st["messages"].values() if m["verb"] == "ask" and m["to"] == OWNER and m["task"] == task
                and m["id"] not in cited]

    def waits_owner(self, st, a, task):
        """-> whether the member waits for its PRINCIPAL's answer on the task: a question of its own to the owner
        that no answer of the owner cites yet -- whatever else the owner said on the task since: an answer that
        cites the question alone ends the wait."""
        return any(m["from"] == a for m in self.unanswered(st, task))

    def silence_count(self, st, a, task, after=0):
        """[115] -> the member's SILENT PASSAGES on the task since `silence_since` -- and since `after`, the fall a
        suspect's passages count from --: each wake-up of its begun after its last act there, with its continuations,
        whose run PARKED -- the member owed an answer at that wake-up and waited for no principal's answer at the
        park. A CONTINUATION counts for nothing: a standing run is continued while it does not park. The variants of
        the rule of before: `count: launches`, every launch ended counts, a continuation included (team 0.48.0 to
        1.32.0); `waiting: counted`, a passage counts while the member waits for its principal."""
        since = max(self.silence_since(st, a, task), after)
        if self.v.get("count") == "launches":
            return sum(1 for tag, i in st["intents"].items() if i["agent"] == a and i["task"] == task
                       and i["id"] > since and tag in st["ended"])
        waited = self.v.get("waiting") == "counted"
        return sum(1 for one in self.passages if one["agent"] == a and one["task"] == task and one["id"] > since
                   and one["end"] is not None and one["owing"] and (waited or not one["waiting"]))

    def beat_of(self, st, a, task, tried):
        """[115] -> the BEAT a wake-up's intent keeps: the exchanges left to the member to say an act on the task,
        this one counted -- `silence:` less its silent passages in a row, never under 1; 1 for the try of a
        suspect. Under the variant `beat: after` the exchange under way is left out."""
        limit = self.v.get("silence", 3)
        if limit is None or self.v.get("detector") != "eventual":
            return None
        if self.v.get("beat") == "after":
            return (1 if tried else limit - self.silence_count(st, a, task)) - 1
        return 1 if tried else max(1, limit - self.silence_count(st, a, task))

    def passage_ended(self, a, task):
        """The member's run parked: its passage on the task ends here, and says whether it waited for its principal."""
        one = next((p for p in reversed(self.passages) if p["agent"] == a and p["task"] == task and p["end"] is None), None)
        if one is not None:
            one["end"], one["waiting"] = self.ids, self.waits_owner(self.replay(), a, task)

    def rewake(self, st, a, task):
        """[91] the relance: `cmh` the bottom of the deadlocked set; `literal` (2026-10-12) a member that waits
        for no answer, or stands in a cycle; `always`; `none` (team 0.33.0); `fell` spares a fallen member."""
        relance = self.v.get("relance", "cmh")
        owed = self.owed(st, a, task)
        if relance == "none" or not owed or (self.v.get("fell") and (a, task) in st["fell"]):
            return False
        if relance == "cmh":
            return self.bottom(st, a, task)                  # [115] no count: relanced while it owes
        waits = self.waits_for(st, a, task)
        if not waits or relance == "always":
            return True
        return self.in_cycle(st, a, task)

    # -- the tick's own steps ---------------------------------------------------------------------
    def notice(self, st, about, task, what):
        return self.post(st, "notice", TEAM, OWNER, task, about=about, what=what)

    def answer_for(self, st, a, ids, why):
        """The answer in the member's place on every debt it owes among `ids`; the owner's opening never --
        the team tells the owner, once."""
        for mid in dict.fromkeys(ids):
            st = self.replay()
            if st["debts"].get(mid, "x") is not None:
                continue
            m = st["messages"][mid]
            if m["from"] == OWNER:
                if not self.asking(st, a, m["task"]):
                    self.notice(st, a, m["task"], why)
            else:
                self.post(st, "re", a, m["from"], m["task"], re=mid, by="tick", **{why: True})

    def silences(self, member=None):
        """[115] the SILENCE: a member, not playing, whose silent PASSAGES in a row on a task it owes on reach
        silence: falls: `silence` written, the member SUSPECTED as after a final failure (its interval, cause
        silence); a suspect, its interval passed, falls at ONE silent passage begun since its last fall, of a launch
        or of its silence -- its try said nothing. A root's owner is told once. A run that stands
        is not judged for itself: it is continued while it does not park. Judged for ONE member right before its
        own wake, on the journal as it stands then -- never on a state read before a launch of its ended."""
        limit = self.v.get("silence", 3)
        if limit is None or self.v.get("detector") != "eventual":
            return
        task = self.current
        for a in (self.MEMBERS if member is None else (member,)):
            st = self.replay()
            if self.playing(a) or not self.open_task(st, task):
                continue
            if not self.owed(st, a, task):
                continue
            s = self.suspects.get(a)
            n = self.silence_count(st, a, task, after=s["since"] if s is not None else 0)
            fell = (n >= 1 and self.clock >= s["next"]) if s is not None else n >= limit
            if not fell:
                continue
            self.append(kind="silence", agent=a, task=task, passages=n, waiting=self.waits_owner(st, a, task))
            self.finals[a] += 1
            interval = INTERVAL * 2 ** (self.finals[a] - 1)
            self.suspects[a] = {"interval": interval, "next": self.clock + interval, "cause": "silence", "since": self.ids}
            self.answer_for(self.replay(), a, self.owed(st, a, task), "silence")   # its debts to members settled in
            self.spawn_tick()                                    # its place; the owner told once; the creditor woken

    def detect(self):
        """[93] each suspected member: within its interval, what it owes and every do or ask that reaches it
        answered in its place, the owner's opening told once; the interval passed, its next message -- or the
        owner's opening alone -- is its TRY."""
        if self.v.get("detector") != "eventual":
            return []
        task, tries = self.current, []
        for a in list(self.suspects):
            if self.playing(a):
                continue
            st = self.replay()
            box = [m for m in self.inbox(st, a, task) if not self.rides(m)]   # [114] a member's info is no try: it
            #                                                                    rides the next launch
            due = self.clock >= self.suspects[a]["next"]
            root_owes = any(st["messages"][i]["from"] == OWNER for i in self.owed(st, a, task)) or any(
                m["from"] == OWNER and st["debts"].get(m["id"], "x") is None for m in box)
            if due and (box or root_owes):
                tries.append((a, box))
                continue
            if due:
                continue
            owing = [m["id"] for m in box if st["debts"].get(m["id"], "x") is None and m["from"] != OWNER]
            if owing:
                self.append(kind="absorbed", agent=a, messages=owing)
                self.answer_for(self.replay(), a, owing, "suspected")
            from_owner = [m for m in box if m["from"] == OWNER]
            if from_owner and not self.v.get("principal_held") and not self.v.get("silent_opening"):
                tries.append((a, from_owner))                    # [108] the principal's word launches it: its try
                continue
            if from_owner:
                self.violate("H2")                               # held for the try: the principal waits the interval
            if not self.v.get("silent_opening"):
                opening = [m["id"] for m in from_owner if m["verb"] == "do"]
                self.answer_for(self.replay(), a, opening, "suspected")
        return tries

    def continued(self):
        """[s.1404] each run that STANDS on a task its root closed is continued -- one launch at a time, nothing at
        its head; what it says there opens nothing: a second answer. No silence judges a closed task: [s.1409]
        ONE continuation is all it gets -- a run that stands after it is held as parked (`route`); under the
        variant `closed: parked`, as team 1.14.1 did, it is continued until it parks, the launches of the task
        and of the season its only bounds."""
        for a in self.MEMBERS:
            st = self.replay()
            for task in [t for t in st["tasks"] if t in st["done"]]:
                run = st["runs"].get(self.unit(a, task))
                if (self.standing.get(run) != task or self.playing(a) or a in self.left_out
                        or len(self.unended(st)) >= self.PARALLEL or self.season_launches >= BUDGET_LAUNCHES
                        or sum(1 for i in st["intents"].values() if i["task"] == task) >= LAUNCHES):
                    continue
                tag = f"t{self.nid()}"
                intent = self.append(kind="wake-intent", tag=tag, agent=a, task=task, run=run, messages=[],
                                     index=1 + len([r for r in self.responses if r["run"] == run]), relance=None,
                                     probe=False, debt_only=False, relaunch=True, empty=True, closed=True, seen=[])
                yield
                key = self.launch(intent, a, task, run, [])
                yield
                self.append(kind="wake-launched", tag=tag, run=key)
                yield
                st = self.replay()

    def wake(self):
        if self.transport == "message":
            yield from self.continued()
        task = self.current
        st = self.replay()
        if task is None or not self.open_task(st, task) or task in self.guard:
            return
        tries = dict(self.detect())
        for a in self.MEMBERS:
            st = self.replay()
            if not self.open_task(st, task) or task in self.guard:
                return
            if self.playing(a) or a in self.left_out:
                continue
            self.silences(a)                                     # [115] its silence judged now, on the journal as it is
            st = self.replay()
            relance, probe, riding = None, False, []
            stands = self.stands(st, a, task)                    # R10: « relaunch me » read at agent's face
            if a in tries:
                box = tries[a]
                relance = None if box else "tried"
            elif (a in self.suspects and self.v.get("detector") == "eventual"
                  and not (stands and self.clock >= self.suspects[a]["next"])):
                continue                                         # [93] woken by nobody -- but, its interval passed, a
            #                                                      run of its that STANDS is continued as any other
            #                                                      [115]: its passage ends at its park, never before
            elif a in self.faulty:
                box, probe = [], True
            else:
                box = self.receivable(st, a, task)               # [97] the head: what arrived since
                riding = [m for m in box if self.rides(m)]       # [114] members' infos: no launch of their own,
                box = [m for m in box if not self.rides(m)]      # they ride the head of the next one
                if not box and not stands:
                    if not self.rewake(st, a, task):             # nothing new for a parked run: a relance alone
                        continue                                 # launches it (R12, J2)
                    if not self.bottom(st, a, task):
                        self.violate("J2")                       # a relance outside the bottom
                    relance = "cycle" if self.in_cycle(st, a, task) else "owed"   # [115] one kind of head: it
                    #                                              asks an answer or an info, whatever its silence
            if stands and (box or riding) and a not in tries and self.v.get("delivered") != "standing":
                box, riding = [], []                             # [s.1377] nothing is delivered to a run that stands:
            #                                                      its messages wait for its park and open the launch
            #                                                      that follows it -- the turn each of them is owed;
            #                                                      the TRY of a suspect alone delivers [108]: its run
            #                                                      may stand for good
            if stands and box and a not in tries:
                self.violate("M5")                               # delivered to a launch that continues a run
            if self.transport == "message":                      # [101] the launcher's bounds, in launches
                if sum(1 for i in st["intents"].values() if i["task"] == task) >= LAUNCHES:
                    self.guard.add(task)                         # `launches:` of the task spent: it stops
                    self.notice(st, None, task, "launches-spent")
                    return
                if self.season_launches >= BUDGET_LAUNCHES:
                    self.guard.add(task)                         # `budget-launches:` of the season spent
                    self.notice(st, None, task, "budget-launches-spent")
                    return
            elif sum(1 for i in st["intents"].values() if i["task"] == task) >= LAUNCHES:
                self.guard.add(task)                             # `wakes:` of the task spent (final)
                self.notice(st, None, task, "wakes-spent")
                return
            if len(self.unended(st)) >= self.PARALLEL:
                continue
            carried = ([m["id"] for m in box] if (box or stands) else self.owed(st, a, task)) + [m["id"] for m in riding]
            run = st["runs"].get(self.unit(a, task))                # [119] the run of the member on this task's carrier
            tag = f"t{self.nid()}"
            owing = bool(self.owed(st, a, task)) or any(st["debts"].get(m["id"], "x") is None for m in box)
            beat = self.beat_of(st, a, task, a in tries) if owing and not stands else None   # [115] the wake-up alone
            intent = self.append(kind="wake-intent", tag=tag, agent=a, task=task, run=run, messages=carried,
                                 index=1 + len([r for r in self.responses if r["run"] == run]) if run else 1,
                                 relance=relance, probe=probe, debt_only=not box and not stands, relaunch=stands,
                                 empty=not box, beat=beat,
                                 seen=sorted(i for i, d in self.replay()["debts"].items() if d is None))
            if not stands:                                       # a wake-up opens a passage; a continuation is of
                self.passages.append({"id": intent["id"], "agent": a, "task": task, "owing": owing, "beat": beat,
                                      "end": None, "waiting": False})   # the passage its run stands in
            yield
            if self.house_left[a] > 0:                           # [107] the house refuses, before any harness
                self.house_left[a] -= 1
                if self.v.get("house_fall"):                     # the variant: counted as the member's fall
                    self.house_falls[a] += 1
                    self.fail(self.replay(), intent, "launch-failed: house")
                    if a in self.suspects:
                        self.violate("H1")                       # suspected for what the house did
                else:
                    self.append(kind="wake-failed", tag=tag, final=False, reason="launch-failed: house", house=True)
                self.spawn_tick()                                # the NET's next tick launches the member again
                yield
                continue
            key = self.launch(intent, a, task, run, box)
            yield
            self.append(kind="wake-launched", tag=tag, run=key)
            yield

    def launch(self, intent, a, task, run, box):
        key = super().launch(intent, a, task, run, box)
        outcome = self.outcome(a)
        w = self.running[key]
        if self.transport == "message":
            w["left"] = 1                                        # a launch of the generic agent ends in one
            self.season_launches += 1                            # step: the interleavings worth playing are
            if not intent["relaunch"]:                           # between launches
                self.mind.setdefault(key, {"plan": [{"el": e, "ready": 0} for e in self.held_over.pop(a, [])],
                                           "held": [], "n": 0, "planned": set()})
        w["fault"] = outcome if outcome in ("crash", "hang") else None
        w["garbage"] = outcome == "garbage"
        w["intent"] = intent
        if self.v.get("view") or self.v.get("broadcast"):
            w["view"] = set(self.suspects) | set(self.faulty) | set(self.left_out)
        return key

    def outcome(self, a):
        f = self.faults
        if f.get("outage") == a:
            left = self.outage.setdefault(a, self.rng.randint(3, 6))
            if left > 0:
                self.outage[a] = left - 1
                return self.rng.choice(("crash", "hang", "garbage"))
            return "ok"
        broken = f.get("broken") == a or (f.get("broken") == "m-after-1" and a == "m" and "m" in self.woke)
        self.woke.add(a)
        if broken:
            return self.rng.choice(("crash", "hang", "garbage"))
        return "ok" if self.rng.random() >= f.get("p", 0) else self.rng.choice(("crash", "hang", "garbage"))

    # -- the wake-up's end ------------------------------------------------------------------------
    def step_wakeup(self, key):
        self.waking = self.running.get(key)
        super().step_wakeup(key)
        self.waking = None

    def flow_written(self, key, tag, words):
        """[106] a launch's exchange at the run's flow: `opened` with the launch's tag, its words, its verdict."""
        self.flows[key].append(("opened", tag))
        self.flows[key].extend(("words", one) for one in words)
        self.flows[key].append(("verdict",))

    def flow_read(self, key, tag):
        """[106] -> the words the reader routes for the launch `tag`: read from the rank the journal last kept of the
        run (0 when it kept none), from the `opened` that carries the tag -- or, under `reader: first`, from the
        first `opened` met, as team 0.40.2 did --, to its `verdict`; a words of another exchange routed breaks H3.
        The rank reached is kept, except for the first task's launches (a journal written before the rank)."""
        flow, first = self.flows[key], self.v.get("reader") == "first"
        start = self.flow_marks.get(key, 0)
        opened, out, mark = None, [], None
        for rank in range(start, len(flow)):
            kind, *rest = flow[rank]
            if kind == "opened":
                if first:
                    opened = rest[0] if opened is None else opened
                else:
                    opened = rest[0] if rest[0] == tag else None
            elif kind == "words" and opened is not None:
                if opened != tag:
                    self.violate("H3")                           # an act of an earlier exchange routed again
                out.append(rest[0])
            elif kind == "verdict" and opened is not None:
                mark = rank + 1
                break
        if mark is not None and self.fates:                      # the first task's journal kept no rank
            self.flow_marks[key] = mark
        return out

    def route(self, st, i, body, tag, cost):
        w, a = body, i["agent"]
        if self.transport == "message" and "words" in w:         # [106] through the run's flow, by the reader
            key = self.tag_record.get(tag)
            self.flow_written(key, tag, w["words"])
            w = dict(w, words=self.flow_read(key, tag))
        elements = [one["say"] for one in w["words"]] if "words" in w else w.get("elements", [])
        off = any(to for one in elements if "do" in one for to in one["do"] if self.EDGES.get(to) != a)
        if self.transport == "message":
            held = i.get("closed") and self.v.get("closed") != "parked"   # [s.1409] its one continuation on a closed
            self.stood(tag, i["task"], w["park"] or held)        # task played: held as parked; [96] the run parks,
            if w.get("garbage"):                                 # or stands                                 # [98] said, not an act: nothing routed
                self.append(kind="said", agent=a, task=i["task"])
                elements = []
        elif w.get("garbage") or off:
            ended = self.journal.pop()
            self.version += 1
            self.fail(self.replay(), i, "response-unreadable", cost=cost, run=ended["run"])
            return
        self.streak[a] = 0
        if i.get("probe"):
            del self.faulty[a]
            self.post(self.replay(), "info", TEAM, self.EDGES.get(a, OWNER), i["task"], about=a, what="correct")
        if (a in self.suspects and self.v.get("detector") == "eventual"
                and (self.suspects[a].get("cause") != "silence" or elements)):
            del self.suspects[a]                                 # [93] the try answers: it repents; [115] a silence
            self.tolerance[a] += 1                               # is lifted by an act alone
            self.finals[a] = 0
        if a not in self.suspects:
            self.finals[a] = 0
        self.route_re(self.replay(), i, elements, cost)
        if self.transport != "message" or w["park"] or (i.get("closed") and self.v.get("closed") != "parked"):
            self.passage_ended(a, i["task"])                     # [115] its run parked: the passage ends
        if self.transport == "message" and w["park"] and self.v.get("abandon"):
            st = self.replay()                                   # the variant: a parking forgets its debts
            self.abandoned.update(self.owed(st, a, i["task"]))

    def fail(self, st, i, reason, cost=0, run=None):
        """A failed wake-up, under the detector of the line: `eventual` [93], `fixed` (2026-10-12), or none --
        team 0.34.0 [88]: one silent retry, then the answer in the member's place. Under `message` a
        launch that crashes or hangs counts the same, its run standing or parked (R12, [104]): the standing
        run is relaunched while its retries last, the words it was writing lost."""
        a, task = i["agent"], i["task"]
        detector = self.v.get("detector")
        if reason == "launch-missing":
            self.append(kind="wake-failed", tag=i["tag"], final=False, reason=reason, cost=cost)
            return
        if i.get("closed") and self.v.get("closed") != "parked":
            self.parked(i["run"])                                # [s.1409] its one continuation on a closed task,
        #                                                          failed: held as parked all the same
        box = list(i["messages"])
        owed = self.owed(st, a, task)
        if detector == "fixed" and i.get("probe"):
            self.append(kind="wake-failed", tag=i["tag"], final=True, reason=reason, cost=cost, run=run)
            self.faulty[a] += 1
            if self.faulty[a] >= PROBES:
                del self.faulty[a]
                self.left_out.add(a)
                st = self.replay()
                for mid in [m["id"] for m in self.inbox(st, a, task)] + self.owed(st, a, task):
                    if self.replay()["debts"].get(mid, "x") is None:
                        self.append(kind="washed", re=mid)
                        frm = st["messages"][mid]["from"]
                        if frm in self.MEMBERS:
                            self.post(self.replay(), "info", TEAM, frm, task, about=a, what="washed", re_of=mid)
                self.notice(self.replay(), a, task, "left-out")
            return
        if detector is None:
            self.failures[a] += 1
            final = self.failures[a] > 1
        else:
            suspected = detector == "eventual" and a in self.suspects
            final = suspected or self.streak[a] >= 1 + self.tolerance[a]
            self.streak[a] += 1
        self.append(kind="wake-failed", tag=i["tag"], final=final, reason=reason, cost=cost, run=run)
        if not final:
            return                                               # the silent retry: its messages back
        if detector == "fixed":
            self.streak[a] = 0
            self.faulty[a] = 0
            for mid in box:
                if self.replay()["debts"].get(mid, "x") is None and self.replay()["messages"][mid]["from"] != OWNER:
                    self.append(kind="washed", re=mid)
                    frm = self.replay()["messages"][mid]["from"]
                    if frm in self.MEMBERS:
                        self.post(self.replay(), "info", TEAM, frm, task, about=a, what="washed", re_of=mid)
            self.post(self.replay(), "info", TEAM, self.EDGES.get(a, OWNER), task, about=a, what="faulty")
            return
        if detector == "eventual":
            self.finals[a] += 1
            interval = INTERVAL * 2 ** (self.finals[a] - 1)
            self.suspects[a] = {"interval": interval, "next": self.clock + interval, "since": self.ids}
            self.streak[a] = 0
        self.answer_for(self.replay(), a, box + owed, "suspected" if detector == "eventual" else "failed")

    # -- the generic agent, profile `debt` --------------------------------------------------------
    def decides(self, w):
        return True                                              # it decides on its debts at every launch

    def script(self, a, task, inbox, mem):
        w = self.waking
        if self.transport == "message":
            said = self.message(a, task, mem, w)
            if w.get("garbage"):                                 # [98] the words is garbled: said, not read
                said["garbage"] = True
            return said
        if w.get("garbage"):
            return {"garbage": True}
        return {"elements": self.brain(a, task, mem, w)}

    def informs(self, a):
        """[114] -> the info the root says to its principal while it keeps the opening: where it stands."""
        return [{"info": {"to": OWNER}}] if self.v.get("info") and a == "m" else []

    def brain(self, a, task, mem, w):
        """-> the elements the member has ready when woken, deciding on the debts open at its wake-up; under `info`
        [114] the root says where it stands to its principal at every launch that keeps the opening, a worker to its
        supervisor now and then while it holds a do."""
        i = w["intent"]
        if self.stubborn and i["debt_only"]:
            return []
        st = self.replay()
        rng, out = self.rng, []
        seen = set(i["seen"])
        is_open = (lambda mid: mid in seen) if self.v.get("stale", True) else \
            (lambda mid: st["debts"].get(mid, "x") is None)
        now = lambda: rng.random() < 0.7
        known = self.known(st, a, task)
        view = w.get("view", set())
        answered = mem.setdefault("answered", [])
        if self.v.get("follow", True):
            followed = mem.setdefault("followed", set())
            for mid in answered:
                if mid not in followed and rng.random() < 0.1:
                    followed.add(mid)
                    out.append({"re": mid})
        for m in known:
            if m["verb"] == "ask" and is_open(m["id"]) and now():
                out.append({"re": m["id"]})
                answered.append(m["id"])
        notes = [m for m in known if m["verb"] == "info"]
        if a == "m":
            asks = [m for m in known if m["verb"] == "do" and m["from"] == OWNER and is_open(m["id"])]
            if not asks:
                return out
            if self.asked_owner and self.waits_owner(st, a, task):
                return []                                        # it waits for its principal: it says nothing
            if "delegated" not in mem:
                mem["delegated"] = True
                mem["need"] = rng.choice((1, 2))
                return out + [{"do": ["r1", "r2"]}] + self.informs(a)
            if self.v.get("principal") and not mem.get("asked_owner") and rng.random() < 0.3:
                mem["asked_owner"] = self.asked_owner = True     # [115] a root that asks its principal, then says
                return out + [{"ask": {"to": OWNER}}]            # nothing until the answer: it waits
            dos = {m["id"]: m["to"] for m in st["messages"].values() if m["from"] == "m" and m["verb"] == "do"
                   and m["task"] == task}
            results = {dos[m["re"]] for m in known if m["verb"] == "re" and m.get("re") in dos}
            gone = {m["about"] for m in notes if m.get("what") in ("faulty", "left-out")} | view
            back = {m["about"] for m in notes if m.get("what") == "correct"}
            for r in back - results:
                if not mem.get("redo_" + r):
                    mem["redo_" + r] = True
                    return out + [{"do": [r]}] + self.informs(a)
            settled = results | (gone - back)
            launches = sum(1 for i in st["intents"].values() if i["agent"] == a and i["task"] == task)
            if self.v.get("long") and launches < LONG_EXCHANGES:
                return out + self.informs(a)                     # [115] a long task: the opening kept, an info each time
            if (len(results) >= mem["need"] or len(settled) >= 2 or rng.random() < 0.05) and now():
                opening = st["opening"].get(task)
                target = opening if opening in [m["id"] for m in asks] else asks[-1]["id"]
                out.append({"re": target})
                answered.append(target)
            return out + self.informs(a)                         # [114] where it stands, at every launch: the answer
            #                                                      it works is said launches later, and [s.1355] a run
            #                                                      that stands without an act counts toward its silence
        if self.scen == "up" and a == "r1":
            for d in [m for m in known if m["verb"] == "do" and is_open(m["id"])]:
                if mem.get("asked_for") != d["id"]:
                    mem["asked_for"] = d["id"]
                    out.append({"ask": {"to": "m"}})
                    continue
                mine = [m["id"] for m in st["messages"].values() if m["from"] == a and m["verb"] == "ask"
                        and m["task"] == task]
                if any(m["verb"] == "re" and m.get("re") in mine for m in known) and rng.random() < 0.7:
                    out.append({"re": d["id"]})
                    answered.append(d["id"])
            return out
        peer = "r2" if a == "r1" else "r1"
        dos = [m for m in known if m["verb"] == "do" and is_open(m["id"])]
        if rng.random() < 0.02 and dos:
            return {"elements": out + [{"do": [peer]}]}             # a stray do: off the edges, unreadable
        for d in dos:
            if self.scen == "cross":
                if peer in view and mem.get("asked_for") != d["id"]:
                    mem["asked_for"] = d["id"]
                    if now():
                        out.append({"re": d["id"]})
                        answered.append(d["id"])
                    continue
                if peer in view and not mem.get("gave_up_" + str(d["id"])):
                    mem["gave_up_" + str(d["id"])] = True
                    out.append({"re": d["id"]})
                    answered.append(d["id"])
                    continue
                if mem.get("asked_for") != d["id"]:
                    mem["asked_for"] = d["id"]
                    out.append({"ask": {"to": peer}})
                    continue
                mine = [m["id"] for m in st["messages"].values() if m["from"] == a and m["verb"] == "ask"
                        and m["task"] == task]
                replied = any(m["verb"] == "re" and m.get("re") in mine for m in known)
                washed = any(m["verb"] == "info" and m.get("what") == "washed" and m.get("re_of") in mine for m in known)
                if not (replied or washed):
                    continue
            if now():
                out.append({"re": d["id"]})
                answered.append(d["id"])
        if (self.v.get("info") and dos and rng.random() < 0.5
                and not any("re" in e and e["re"] in {d["id"] for d in dos} for e in out)):
            out.append({"info": {"to": "m"}})                   # [114] a worker at work says so to its supervisor
        return out

    def message(self, a, task, mem, w):
        """[96] one launch of the generic agent under `message`: what the member decides on the head it was
        delivered joins what it still has to say, each words ready after its work -- a do one a launch, an
        answer to a do after 0 to 2 launches (0 to 5 under `slow`), the others at once; a ready answer leaves now (eagerly) or is
        held for the parking launch, the one with nothing left to work, which says every answer held; a
        member that parks saying nothing is an incorrect agent (`silent`). The member DECIDES at the launch that
        opens an exchange: a launch that continues a standing run works what was decided -- a message at its
        head gets no turn [s.1377]."""
        mind, rng = self.mind[w["key"]], self.rng
        mind["n"] += 1
        n = mind["n"]
        if mind.get("stuck") or rng.random() < self.stuck_p:     # an incorrect agent [s.1355]: from this launch on
            mind["stuck"] = True                                 # its run stands and says nothing
            return {"words": [], "park": False}
        for e in ([] if w["intent"]["relaunch"] else self.brain(a, task, mem, w)):
            if "do" in e:
                for lap, to in enumerate(e["do"]):
                    key = ("do", to, mem.get("redo_" + to, False))
                    if key not in mind["planned"]:
                        mind["planned"].add(key)
                        mind["plan"].append({"el": {"do": [to]}, "ready": n + lap})
            elif "ask" in e:
                key = ("ask", e["ask"]["to"], len(mind["planned"]))
                mind["planned"].add(key)
                mind["plan"].append({"el": e, "ready": n})
            elif "info" in e:
                mind["plan"].append({"el": e, "ready": n})       # [114] said at this launch
            elif "re" in e:
                if ("re", e["re"]) in mind["planned"] and e["re"] not in mem.get("followed", set()):
                    continue
                mind["planned"].add(("re", e["re"]))
                cited = self.replay()["messages"].get(e["re"]) or {}
                work = rng.randint(0, 5 if self.v.get("slow") else 2) if cited.get("verb") == "do" else 0   # a turn
                #                                                  played over several launches: five continuations
                #                                                  at most in the journals of a supervisor
                mind["plan"].append({"el": e, "ready": n + work})
        out = []
        for p in [p for p in mind["plan"] if p["ready"] <= n]:
            mind["plan"].remove(p)
            e = p["el"]
            if "do" in e or "ask" in e or "info" in e or rng.random() < self.eager[a]:
                out.append(e)
            else:
                mind["held"].append(e)
        park = not mind["plan"]
        if park:
            if rng.random() < self.silent_p:                     # an incorrect agent: parks saying nothing
                self.held_over[a] += mind["held"]
                out = [e for e in out if "do" in e or "ask" in e]
            else:
                out += mind["held"]
            mind["held"] = []
        return {"words": [{"say": e} for e in out], "park": park}

    # -- the owner and the run ----------------------------------------------------------------------
    def owner_moves(self, st):
        task = self.current
        return (self.open_task(st, task) and self.told_since(st, task) and self.owner_posts[task] < 2)

    def owner_acts(self):
        st = self.replay()
        task = self.current
        self.owner_seen[task] = self.ids
        self.acted.add(task)
        asked = self.unanswered(st, task)
        if asked and self.rng.random() < 0.6:                    # [115] a question waits for the owner: it answers
            self.owner_posts[task] += 1                          # it, citing it -- or says something else below,
            self.post(st, "re", OWNER, asked[0]["from"], task, re=asked[0]["id"])   # and the question waits on
            self.spawn_tick()
            return
        if self.rng.random() < 0.8 and "m" not in self.left_out:
            self.owner_posts[task] += 1
            self.post(st, "do", OWNER, "m", task)
            self.spawn_tick()

    def tries_due(self, st):
        """-> the hours of the tries a suspected member waits for, within the task's horizon."""
        task = self.current
        found = []
        for a, s in self.suspects.items():
            if self.playing(a):
                continue
            box = self.inbox(st, a, task)
            if (box or any(st["messages"][i]["from"] == OWNER for i in self.owed(st, a, task))
                    or (self.stands(st, a, task) and self.clock < s["next"])):   # [115] its standing run, continued then
                found.append(s["next"])
        return [t for t in found if t <= self.opened_at + HORIZON]

    def run(self):
        self.open_next()
        steps = 0
        while True:
            steps += 1
            self.now += 1
            if steps > self.STEPS:
                self.violate("no-termination")
                break
            st = self.replay()
            choices = [("tick", e) for e in self.ticks] + [("wake", k) for k in self.running if self.steppable(k)]
            if self.owner_moves(st):
                choices.append(("owner", None))
            hung = any(not w["answered"] and w["fault"] == "hang" for w in self.running.values())
            if hung and self.rng.random() < 0.05:
                choices.append(("time", None))
            if not choices:
                if hung:
                    choices = [("time", None)]
                else:
                    due = self.tries_due(st) if self.open_task(st, self.current) and self.current not in self.guard else []
                    if due:
                        self.clock = max(self.clock + 1, min(due))       # the schedule's ticks, up to the next try
                        self.spawn_tick()
                        continue
                    self.settle_task(st)
                    if len(self.fates) < self.season_len:
                        self.open_next()
                        continue
                    break
            kind, arg = self.rng.choice(choices)
            if kind == "tick":
                self.step_tick(arg)
            elif kind == "wake":
                self.step_wakeup(arg)
            elif kind == "owner":
                self.owner_acts()
            else:
                self.clock += 1
                if not self.ticks and any(not w["answered"] and self.clock - w["start"] >= TIMEOUT
                                          for w in self.running.values()):
                    self.spawn_tick()                            # the schedule's tick reaps a stuck wake-up
        self.check()
        return self.violations

    def settle_task(self, st):
        task = self.current
        if task in st["done"]:
            self.fates.append("resolved")
        elif self.told(st, task):
            self.fates.append("owner-told")                      # a member left out on this task: told by its notice
        else:
            self.fates.append("STALL")
            self.violate("J4" if self.season_len > 1 else "J3")

    def check(self):
        st = self.replay()
        if any(n > 1 for n in st["settles"].values()):
            self.violate("J1")                                   # a debt settled twice
        for mid, state in st["debts"].items():
            if state is None and st["messages"][mid]["task"] in st["done"]:
                self.violate("J5")                               # a debt open after the close
        for mid, m in st["messages"].items():
            if m["verb"] == "info" and mid in st["debts"]:
                self.violate("J8")                               # [114] an info opened a debt
        for i in st["intents"].values():
            carried = [st["messages"][x] for x in i.get("messages", []) if x in st["messages"]]
            if (carried and all(m["verb"] == "info" and m["from"] in self.MEMBERS for m in carried)
                    and not i.get("relance") and not i.get("relaunch")):
                self.violate("J8")                               # [114] a launch for a member's info alone
        if self.transport == "message":
            for mid, state in st["debts"].items():
                m = st["messages"][mid]
                if state is None and m["task"] not in self.guard and m["from"] in self.MEMBERS:
                    self.violate("M1")                           # a do or an ask never answered
        limit = self.v.get("silence") or 3                       # the owed rule, judged on the variant without one too
        dead = {e["tag"] for e in self.journal if e["kind"] == "wake-failed"}
        for a in self.MEMBERS:                                   # [115] J9: no more than silence: relances in a row
            streak = 0                                           # carry a debt without an act of the member or its fall
            for e in self.journal:
                if e["kind"] == "post" and e["from"] == a and e.get("by") != "tick":
                    streak = 0
                elif e["kind"] == "silence" and e["agent"] == a:
                    streak = 0
                elif (e["kind"] == "wake-intent" and e["agent"] == a and e.get("relance") in ("owed", "cycle")
                      and not e.get("relaunch") and e["tag"] not in dead):   # a continuation opens no passage, a dead
                    streak += 1                                  # launch ends none: the detector's other input
                    if streak > limit:
                        self.violate("J9")
        if any(e["kind"] == "silence" and e.get("waiting") for e in self.journal):
            self.violate("J13")                                  # [115] fallen while it waits for its principal
        if self.v.get("silence", 3) is not None:                 # [115] J14: the beat says the right number
            if any(one["beat"] is not None and not 1 <= one["beat"] <= limit for one in self.passages):
                self.violate("J14")
            for e in self.journal:
                if e["kind"] != "silence":
                    continue
                last = next((one for one in reversed(self.passages) if one["agent"] == e["agent"]
                             and one["task"] == e["task"] and one["id"] < e["id"]), None)
                if last is None or last["beat"] != 1:
                    self.violate("J14")                          # fallen after a wake-up that left it more than one
        continued = Counter((e["agent"], e["task"]) for e in self.journal if e["kind"] == "wake-intent"
                            and e.get("closed") and e["tag"] in self.tag_record)   # launched: one never launched is none
        if any(n > 1 for n in continued.values()):
            self.violate("J12")                                  # [s.1409] continued twice on a task that closed
        garbled = any(e["kind"] == "said" and e["agent"] == "m" for e in self.journal) or any(
            e["kind"] == "wake-failed" and st["intents"][e["tag"]]["agent"] == "m" for e in self.journal)
        if (self.v.get("long") and self.v.get("info") and not self.stubborn and not self.stuck_p and not garbled
                and not self.asked_owner):                       # [115] J10: a root that says an act at EVERY passage
            #                                                      -- none garbled, none dead, none spent waiting
            if any(e["kind"] == "silence" and e["agent"] == "m" for e in self.journal) or any(
                    m["verb"] == "notice" and m.get("about") == "m" and m.get("what") == "silence"
                    for m in st["messages"].values()):
                self.violate("J10")


# -- the scenario `workers`: the clock of the launches, the overhead of a wake-up, the cost ----------------
#
# A supervisor-workers team on a CLOCK: the supervisor S gives each of K files to a worker by a do
# and answers the opening once every do is answered -- each answer a message that launches it; a worker works each do it holds, may ask S, and answers
# when its work is done -- at once (eagerly) or held for its TURN. Each launch lasts 4 to 12 s and costs
# 0.022 USD; a wake-up adds its overhead. Under `final` a wake-up plays the whole exchange and its acts are
# routed at its end; under `message` a wake-up is one launch, its acts routed at once, every relaunch delivering
# what waits. The laps of S's cycle fold in one launch: each proof's answer brings the next lap.
# The processes advance by their dates, not by draws: this scenario measures the end, the launches and the
# cost; the interleavings and the invariants of the transport are the scenario `debt`'s.

import copy
import heapq
import statistics

LAUNCH = (4.0, 12.0)        # seconds a launch lasts (relayed launches measured 5 to 10 s on 16/10)
COST = 0.022                # USD per launch (laps relayed 16/10: 0.130 USD / 6 launches)


class Member:
    def __init__(self, name, parent):
        self.name, self.parent = name, parent
        self.items = []          # what it works or owes: {id, kind, work, blocked, ready, frm, asked}
        self.held = []           # answers ready, not said yet: message ids
        self.inbox = []          # messages waiting for delivery
        self.standing = False    # its run stands mid-exchange
        self.busy = False
        self.snapshot = None     # its state at the exchange's opening (a `final` replay)
        self.taken = []          # the messages delivered in this exchange
        self.eager = 0.5


class Timed:
    def __init__(self, seed, transport, a):
        self.rng = random.Random(seed)
        self.transport, self.a = transport, a
        self.now, self.events, self.n = 0.0, [], 0
        self.members = {"S": Member("S", None)}
        self.workers = [f"w{i + 1}" for i in range(a.workers)]
        for w in self.workers:
            self.members[w] = Member(w, "S")
        for one in self.members.values():
            one.eager = a.eager if a.eager is not None else self.rng.random()
        self.ids = 0
        self.messages = {}       # id -> message
        self.answered = defaultdict(int)
        self.answer_at, self.sent_at = {}, {}
        self.pending = defaultdict(list)   # `final`: acts said, routed at the wake-up's end
        self.dos_out = set()     # S's dos of the round under way, routed
        self.files_given = set()
        self.dup = 0
        self.launches, self.wakes, self.ticks, self.crashes = defaultdict(int), 0, 0, 0
        self.at_turn = self.mid = 0          # answers said at a TURN / before it
        self.resolved_at = None
        self.first_worker = None
        self.repaired = False
        self.max_par = 0
        self.violations = set()

    # -- the clock ------------------------------------------------------------------------------
    def at(self, delay, kind, payload=None):
        self.n += 1
        heapq.heappush(self.events, (self.now + delay, self.n, kind, payload))

    # -- messages -------------------------------------------------------------------------------
    def post(self, kind, frm, to, ref=None, file=None):
        self.ids += 1
        m = {"id": self.ids, "kind": kind, "frm": frm, "to": to, "ref": ref, "file": file}
        self.messages[self.ids] = m
        return m

    def route(self, acts):
        """The transport: each act posted to its addressee's inbox -- a `re` to the author of the message
        it cites, as a message that launches it."""
        for m in acts:
            self.routed.add(m["id"])
            if m["kind"] == "do" and m["frm"] == "S":
                if m["file"] in self.files_given:
                    self.dup += 1
                self.files_given.add(m["file"])
                self.dos_out.add(m["id"])
            if m["kind"] in ("do", "ask"):
                self.sent_at[m["id"]] = self.now
                self.members[m["to"]].inbox.append(m)
            elif m["kind"] == "re":
                asked = self.messages[m["ref"]]
                if not self.answered[asked["id"]]:
                    self.answer_at[asked["id"]] = self.now
                self.answered[asked["id"]] += 1
                if asked["kind"] in ("do", "ask"):
                    self.members[asked["frm"]].inbox.append(m)
                elif asked["kind"] == "open":
                    self.resolved_at = self.now

    def deliver(self, member):
        """Every message waiting, delivered to the member's exchange."""
        for m in member.inbox:
            member.taken.append(m)
            if m["kind"] == "open":
                member.items.append({"id": m["id"], "kind": "open", "work": None, "blocked": None,
                                     "ready": False, "frm": "owner", "cycle": self.cycle(),
                                     "dos": set(), "got": set()})
            elif m["kind"] in ("do", "ask"):
                member.items.append({"id": m["id"], "kind": m["kind"],
                                     "work": self.a.work if m["kind"] == "do" else 1,
                                     "blocked": None, "ready": False, "frm": m["frm"], "asked": False})
            elif m["kind"] == "re":                       # the answer to its ask: the do goes on; to a do of
                for it in member.items:                   # its round: counted, the last one frees the opening
                    if it["blocked"] == m["ref"]:
                        it["blocked"] = None
                    if it["kind"] == "open" and m["ref"] in it["dos"]:
                        it["got"].add(m["ref"])
                        if it["blocked"] == "answers" and it["got"] >= it["dos"]:
                            it["blocked"], it["work"] = None, 1
        member.inbox = []

    def cycle(self):
        return [("laps", list(range(self.a.files)))]

    # -- one launch of a member -----------------------------------------------------------------
    def workable(self, member):
        """-> one item the member can work now, picked at random: a generic agent's choice."""
        can = [it for it in member.items if not it["ready"] and it["blocked"] is None
               and ((it["kind"] == "open" and (it["cycle"] or it["work"]))
                    or (it["kind"] != "open" and it["work"]))]
        return self.rng.choice(can) if can else None

    def step(self, member):
        """-> (acts, parks, said): what this launch says, whether it is the TURN, whether it
        carried a team message (a TURN says `[]` when it holds nothing -- unless faulty)."""
        acts = []
        it = self.workable(member)
        if it is None:                                    # the TURN: every answer still held
            if self.rng.random() < self.a.faulty:
                return [], True, False
            for mid in member.held:
                acts.append(self.post("re", member.name, self.messages[mid]["frm"], ref=mid))
                self.at_turn += 1
            member.held = []
            member.items = [x for x in member.items if not x["ready"]]
            return acts, True, True
        if it["kind"] == "open" and it["cycle"]:
            _, files = it["cycle"].pop(0)
            for f in files:
                acts.append(self.post("do", "S", self.workers[f % len(self.workers)], file=f))
                it["dos"].add(acts[-1]["id"])
            if not it["cycle"]:                           # the round of delegations closes with the cycle: S
                it["cycled_now"] = True                   # works the opening once every do of it is answered,
                if it["got"] >= it["dos"]:                # its own count of the answers it received
                    it["blocked"], it["work"] = None, 1
                else:
                    it["blocked"] = "answers"
        else:
            if (it["kind"] == "do" and not it["asked"] and member.parent
                    and self.rng.random() < self.a.ask / max(1, self.a.work)):
                it["asked"] = True                        # the do waits for the parent's answer
                m = self.post("ask", member.name, member.parent)
                it["blocked"] = m["id"]
                acts.append(m)
                return acts, False, True
            it["work"] -= 1
            if it["work"] == 0:
                it["ready"] = True
                member.held.append(it["id"])
        for mid in list(member.held):                     # a ready answer: now, or held
            if self.rng.random() < member.eager:
                member.held.remove(mid)
                acts.append(self.post("re", member.name, self.messages[mid]["frm"], ref=mid))
                self.mid += 1
        member.items = [x for x in member.items if not (x["ready"] and x["id"] not in member.held)]
        return acts, False, bool(acts)

    # -- the tick and the wake-ups ---------------------------------------------------------------
    def tick(self):
        self.ticks += 1
        for member in self.members.values():
            if sum(m.busy for m in self.members.values()) >= self.a.parallel:
                break
            if member.busy:
                continue
            owes = bool(member.held) and not member.standing
            if member.standing or member.inbox or owes:
                self.wake(member)

    def wake(self, member):
        member.busy = True
        self.wakes += 1
        self.max_par = max(self.max_par, sum(m.busy for m in self.members.values()))
        if sum(m.busy for m in self.members.values()) > self.a.parallel:
            self.violations.add("I10")
        if not member.standing:                           # an exchange opens
            for it in member.items:
                it["cycled_now"] = False
            member.snapshot = (copy.deepcopy(member.items), list(member.held))
            member.taken = []
            member.standing = True
            if member.name != "S" and self.first_worker is None:
                self.first_worker = self.now
        self.deliver(member)
        self.at(self.a.overhead / 2, "launch", member.name)

    def launch(self, name):
        member = self.members[name]
        self.launches[name] += 1
        crashed = self.rng.random() < self.a.crash
        self.at(self.rng.uniform(*LAUNCH), "launched", (name, crashed))

    def launched(self, name, crashed):
        member = self.members[name]
        if crashed:
            self.crashes += 1
            if self.transport == "final":                 # the wake-up is played again from its start
                member.items, member.held = copy.deepcopy(member.snapshot[0]), list(member.snapshot[1])
                member.inbox = member.taken + member.inbox
                self.pending[name] = []
                member.standing = False
                self.end(member)
            else:
                self.end(member)                          # the standing run is relaunched
            return
        acts, parks, said = self.step(member)
        cycled = any(it["kind"] == "open" and it.get("cycled_now") for it in member.items)
        if name == "S" and parks and cycled and not self.repaired and self.rng.random() < self.a.repair:
            self.repaired = True                          # the checkpoint fails: the cycle replays
            for it in member.items:
                if it["kind"] == "open":
                    it["cycle"], it["blocked"], it["work"] = self.cycle(), None, None
                    it["dos"], it["got"] = set(), set()
            if self.transport == "final":                 # nothing had left: said again by the replay
                self.pending[name] = [m for m in self.pending[name] if m["kind"] != "do"]
            else:                                         # they had left: a new round, its own answers counted
                self.dos_out = set()
            parks = False
        if self.transport == "message":
            self.route(acts)
        else:
            self.pending[name] += acts
        if parks:
            member.standing = False                       # R12: a parking judges nothing -- what it still
            if self.transport == "final":                 # holds is owed, the tick wakes it again (owes)
                self.route(self.pending[name])
                self.pending[name] = []
            self.end(member)
            return
        if self.transport == "final":
            self.launch(name)                             # the same wake-up goes on
            return
        self.end(member)

    def end(self, member):
        member.busy = False
        self.at(self.a.overhead / 2, "tick")

    # -- the run --------------------------------------------------------------------------------
    def play(self):
        self.routed = set()
        opening = self.post("open", "owner", "S")
        self.members["S"].inbox.append(opening)
        self.at(0, "tick")
        guard = 0
        while self.events and self.resolved_at is None:
            guard += 1
            if guard >= 200000:
                self.violations.add("no-termination")
                break
            self.now, _, kind, payload = heapq.heappop(self.events)
            if kind == "tick":
                self.tick()
            elif kind == "launch":
                self.launch(payload)
            else:
                self.launched(*payload)
        if self.resolved_at is None:
            self.violations.add("J3")
            self.resolved_at = self.now
        # the task's resolution settles every debt (team): owed are the asks routed and the current round
        owed = [m for m in self.messages.values() if m["id"] in self.routed and not self.answered[m["id"]]
                and (m["kind"] == "ask" or m["id"] in self.dos_out)]
        if owed:
            self.violations.add("M1")
        total = sum(self.launches.values())
        return {"makespan": self.resolved_at, "first_re": min(self.answer_at.values()),
                "re_mean": statistics.mean(self.answer_at.values()), "launches": total,
                "wakes": self.wakes, "cost": total * COST, "dup": self.dup,
                "asks": sum(1 for m in self.messages.values() if m["kind"] == "ask" and m["id"] in self.routed),
                "at_turn": self.at_turn / max(1, self.at_turn + self.mid), "par": self.max_par,
                "first_worker": self.first_worker, "violations": self.violations}


class TimedArgs:
    def __init__(self, argv):
        def opt(name, default, cast):
            return cast(argv[argv.index(name) + 1]) if name in argv else default
        self.runs, self.files = opt("--runs", 300, int), opt("--files", 10, int)
        self.workers, self.parallel = opt("--workers", 3, int), opt("--parallel", 4, int)
        self.overhead, self.work = opt("--overhead", 3.0, float), opt("--work", 6, int)
        self.ask, self.eager = opt("--ask", 0.3, float), opt("--eager", None, float)
        self.crash, self.repair = opt("--crash", 0.0, float), opt("--repair", 0.0, float)
        self.faulty, self.seed = opt("--faulty", 0.0, float), opt("--seed", 1, int)




# -- the lines ----------------------------------------------------------------------------------------

R_OWED = dict(answers="re")
R_TODAY = dict(run="task", busy="task", upgrade="newrun", unread="drop", answers="verbs")   # team 0.12.2
X_OWED = dict(EXT)
X_TODAY = dict(EXT, killans="kill", share="none", season="none", pause="none", recur="none", renew="none")
S_OWED = dict(run="carrier", busy="member", upgrade="keep", entry="dag", handed="key",
              timeout="response")
S_TODAY = dict(S_OWED, run="task", busy="task", upgrade="newrun", entry="door")

# (scenario, name, flags, net, crash, ext)
LINES = [
    ("review", "v2", dict(answers="verbs", spawn=False), False, 0.0, None),
    ("review", "read-before-release", dict(answers="verbs", spawn=False, lock="read-before-release"), False, 0.0, None),
    ("review", "no-mark", dict(answers="verbs", spawn=False, lock="no-mark"), False, 0.0, None),
    ("review", "no-mark + schedule", dict(answers="verbs", spawn=False, lock="no-mark"), True, 0.0, None),
    ("review", "v2 + schedule", dict(answers="verbs", spawn=False), True, 0.0, None),
    ("review", "v2 + tick death 2 %", dict(answers="verbs", spawn=False), False, 0.02, None),
    ("review", "v2 + schedule + tick death 2 %", dict(answers="verbs", spawn=False), True, 0.02, None),
    ("review", "v2 + timer, its tick failing [s.1357]",
     dict(answers="verbs", spawn=False, timer=dict(arm="end", relay="failed", fails=0.3, lost=0.3)), True, 0.0, None),
    ("review", "v2 + timer, a failed tick arms no next (team 1.4.2) [s.1357]",
     dict(answers="verbs", spawn=False, timer=dict(arm="end", relay="none", fails=0.3, lost=0.3)), True, 0.0, None),
    ("review", "v2 + timer + tick death 2 % [s.1373]",
     dict(answers="verbs", spawn=False, timer=dict(arm="start", relay="always", fails=0.3, lost=0.3)), True, 0.02, None),
    ("review", "v2 + timer + tick death, armed at the round's end alone (team 1.4.3) [s.1373]",
     dict(answers="verbs", spawn=False, timer=dict(arm="end", relay="always", fails=0.3, lost=0.3)), True, 0.02, None),
    ("review", "v2 + timer + tick death, its tick finding the lock held arms no next (team 1.14.0)",
     dict(answers="verbs", spawn=False, timer=dict(arm="start", relay="failed", fails=0.3, lost=0.3)), True, 0.02, None),
    ("review", "v2 + schedule + tick death, no tag", dict(answers="verbs", spawn=False, tags=False), True, 0.02, None),
    ("review", "v2 + schedule + tick death + machine cut, relaunch at logon [110]",
     dict(answers="verbs", spawn=False, cut="relaunch"), True, 0.02, None),
    ("review", "v2 + schedule + machine cut, no relaunch [110]", dict(answers="verbs", spawn=False, cut="none"), True,
     0.0, None),
    ("review", "v2 + schedule + tick death + machine cut, two teams under one house entry [111]",
     dict(answers="verbs", spawn=False, cut="relaunch", house="shared"), True, 0.02, None),
    ("review", "v2 + schedule + machine cut, the stop of one team removes the entry [111]",
     dict(answers="verbs", spawn=False, cut="relaunch", house="one-removes"), True, 0.0, None),

    ("reframe", "today (team 0.12.2)", R_TODAY, False, 0.0, None),
    ("reframe", "owed", R_OWED, False, 0.0, None),
    ("reframe", "owed but the answers by verbs (team 0.32.2) [84]", dict(R_OWED, answers="verbs"), False, 0.0, None),
    ("reframe", "owed + schedule + tick death 2 %", R_OWED, True, 0.02, None),
    ("reframe", "owed but busy per (member, task) [49]", dict(R_OWED, busy="task"), False, 0.0, None),
    ("reframe", "owed but upgrade opens a new run [50]", dict(R_OWED, upgrade="newrun"), False, 0.0, None),
    ("reframe", "owed, upgrade new run without history [33]", dict(R_OWED, upgrade="nohistory"), False, 0.0, None),
    ("reframe", "owed but upgrade, same session, new key [50]", dict(R_OWED, upgrade="newkey"), False, 0.0, None),
    ("reframe", "owed but upgrade resumes the dead key [33]", dict(R_OWED, upgrade="dead"), False, 0.0, None),
    ("reframe", "owed but edges routed [35 b]", dict(R_OWED, edges=False), False, 0.0, None),
    ("reframe", "owed but owner returned [36 b]", dict(R_OWED, owner=False), False, 0.0, None),
    ("reframe", "owed but by the hour [38 a]", dict(R_OWED, handed="hour"), False, 0.0, None),
    ("reframe", "owed but stop needs a holder", dict(R_OWED, stop=False), False, 0.0, None),
    ("reframe", "owed but stop needs a holder, by verbs [84]", dict(R_OWED, stop=False, answers="verbs"), False, 0.0, None),
    ("reframe", "owed + tick death, a lost spawn retried [43 b]", dict(R_OWED, spawn=False), True, 0.02, None),
    ("reframe", "owed but an unreadable answer drops its run [47]", dict(R_OWED, unread="drop"), False, 0.0, None),
    ("reframe", "owed but one run per member [119]", dict(R_OWED, run="member", busy="run"), False, 0.0, None),
    ("reframe", "owed but a message rides the head of a continuation (team 1.13.1) [s.1377]",
     dict(R_OWED, delivered="standing"), False, 0.0, None),

    ("ext", "ext: today (team 0.12.2)", R_TODAY, True, 0.0, X_TODAY),
    ("ext", "ext: owed", R_OWED, True, 0.0, X_OWED),
    ("ext", "ext: owed but the answers by verbs (team 0.32.2) [84]", dict(R_OWED, answers="verbs"), True, 0.0, X_OWED),
    ("ext", "ext: owed + tick death 2 %", R_OWED, True, 0.02, X_OWED),
    ("ext", "ext: owed but bounds read once a tick", R_OWED, True, 0.0, dict(X_OWED, live=False)),
    ("ext", "ext: owed + tick death, bounds count intents [44]", R_OWED, True, 0.02, dict(X_OWED, count="intents")),
    ("ext", "ext: owed + tick death, ring in two writes", R_OWED, True, 0.02, dict(X_OWED, ring="two")),
    ("ext", "ext: owed but timeout judged first", R_OWED, True, 0.0, dict(X_OWED, timeout="first")),
    ("ext", "ext: owed but run-null answer read after the timeout", R_OWED, True, 0.0, dict(X_OWED, timeout="code")),
    ("ext", "ext: owed but a held run resumed [45]", R_OWED, True, 0.0, dict(X_OWED, lockbusy=False)),
    ("ext", "ext: owed but no schedule", R_OWED, False, 0.0, X_OWED),
    ("ext", "ext: owed but a kill ends the member's run", R_OWED, True, 0.0, dict(X_OWED, kill="member")),
    ("ext", "ext: owed but a killed run is forgotten", R_OWED, True, 0.0, dict(X_OWED, killrun="forget")),
    ("ext", "ext: owed but an answered wake-up killed [58]", R_OWED, True, 0.0, dict(X_OWED, killans="kill")),
    ("ext", "ext: owed but the resume notes T4's member alone [67]", R_OWED, True, 0.0, dict(X_OWED, resume="agent")),
    ("ext", "ext: owed but a ring at hand takes the date [69 b]", R_OWED, True, 0.0, dict(X_OWED, manual="date")),
    ("ext", "ext: owed but no allowance reserved [75]", R_OWED, True, 0.0, dict(X_OWED, share="none")),
    ("ext", "ext: owed but the whole rest to one wake-up [75]", R_OWED, True, 0.0, dict(X_OWED, share="reserve")),
    ("ext", "ext: owed but a season forgets the runs [82]", R_OWED, True, 0.0, dict(X_OWED, season="forget")),
    ("ext", "ext: owed but the tick ignores the pause [83]", R_OWED, True, 0.0, dict(X_OWED, pause="ignore")),
    ("ext", "ext: owed but the pause's periods rung at resume [83]", R_OWED, True, 0.0, dict(X_OWED, pause="catchup")),
    ("ext", "ext: owed but a recurrence sounds while open [112]", R_OWED, True, 0.0,
     dict(X_OWED, recur="open")),
    ("ext", "ext: owed, the recurrence's hour changed [117]", R_OWED, True, 0.0, dict(X_OWED, rehour="new")),
    ("ext", "ext: owed but the old hour still sounds [117]", R_OWED, True, 0.0, dict(X_OWED, rehour="old")),
    ("ext", "ext: owed but the day sounds again at the new hour [117]", R_OWED, True, 0.0,
     dict(X_OWED, rehour="twice")),
    ("ext", "ext: owed but one run per member [119]", dict(R_OWED, run="member", busy="run"), True, 0.0, X_OWED),
    ("ext", "ext: owed but a run per (member, task) [47]", dict(R_OWED, run="task"), True, 0.0, X_OWED),
    ("ext", "ext: owed but the run of a recurrence never renewed [120]", R_OWED, True, 0.0, dict(X_OWED, renew="never")),
    ("ext", "ext: owed but the run renewed at every occurrence [120]", R_OWED, True, 0.0, dict(X_OWED, renew="every")),
    ("ext", "ext: owed, a recurrence by a duration [121]", R_OWED, True, 0.0, dict(X_OWED, every="interval")),
    ("ext", "ext: owed, a recurrence by a duration + tick death 2 % [121]", R_OWED, True, 0.02,
     dict(X_OWED, every="interval")),
    ("ext", "ext: owed but the first slot waits one period [121]", R_OWED, True, 0.0,
     dict(X_OWED, every="interval", slot="late")),
    ("ext", "ext: owed but a slot counted by its date [121]", R_OWED, True, 0.0,
     dict(X_OWED, every="interval", slot="date")),
    ("ext", "ext: owed, a recurrence born of a task [122]", R_OWED, True, 0.0, dict(X_OWED, origin="task")),
    ("ext", "ext: owed, a recurrence by a duration born of a task [122]", R_OWED, True, 0.0,
     dict(X_OWED, origin="task", every="interval")),
    ("ext", "ext: owed but the origin forgotten [122]", R_OWED, True, 0.0,
     dict(X_OWED, origin="forgot", every="interval")),

    ("squad", "squad: today (team 0.12.2)", S_TODAY, False, 0.0, None),
    ("squad", "squad: owed", S_OWED, False, 0.0, None),
    ("squad", "squad: owed + schedule + tick death 2 %", S_OWED, True, 0.02, None),
    ("squad", "squad: owed but run+busy per (member, task), daily split [47]", dict(S_OWED, run="task", busy="task"), False,
     0.0, None),
    ("squad", "squad: owed but busy per (member, task) [49]", dict(S_OWED, busy="task"), False, 0.0, None),
    ("squad", "squad: owed but one run per member [119]", dict(S_OWED, run="member", busy="run"), False, 0.0, None),
    ("squad", "squad: owed but upgrade opens a new run [50]", dict(S_OWED, upgrade="newrun"), False, 0.0, None),
    ("squad", "squad: owed but upgrade, same session, new key [50]", dict(S_OWED, upgrade="newkey"), False, 0.0, None),
    ("squad", "squad: owed but one run per agent [48]", dict(S_OWED, run="agent", busy="run"), False, 0.0, None),
    ("squad", "squad: owed but entries as doors at -new [55]", dict(S_OWED, entry="door"), False, 0.0, None),
    ("squad", "squad: owed but by the hour [38 a]", dict(S_OWED, handed="hour"), False, 0.0, None),
    ("squad", "squad: owed but the run-null answer read after the timeout [46]", dict(S_OWED, timeout="code"), False, 0.0, None),
]

SCENARIOS = {"review": Review, "reframe": Reframe, "ext": Reframe, "squad": Squad}

# The invariants each variant owes to break (the catalogue of the docstring); a line absent from here is OWED: it
# holds on every run. The no-tag line breaks I12: a hidden launch is paid twice.
BREAKS = {
    "read-before-release": ("I1",),
    "no-mark": ("I1",),
    "v2 + tick death 2 %": ("I1",),
    "v2 + timer, a failed tick arms no next (team 1.4.2) [s.1357]": ("I1",),
    "v2 + timer + tick death, armed at the round's end alone (team 1.4.3) [s.1373]": ("I1",),
    "v2 + timer + tick death, its tick finding the lock held arms no next (team 1.14.0)": ("I1",),
    "v2 + schedule + tick death, no tag": ("I12",),
    "v2 + schedule + machine cut, no relaunch [110]": ("I1",),
    "v2 + schedule + machine cut, the stop of one team removes the entry [111]": ("I1",),
    "today (team 0.12.2)": ("I13", "I18", "I19"),
    "owed but busy per (member, task) [49]": ("I19",),
    "owed but upgrade opens a new run [50]": ("I13", "I18"),
    "owed, upgrade new run without history [33]": ("I1", "I13", "I18"),
    "owed but upgrade, same session, new key [50]": ("I18",),
    "owed but upgrade resumes the dead key [33]": ("I1", "I4", "I7"),
    "owed but edges routed [35 b]": ("I11a",),
    "owed but owner returned [36 b]": ("I11b",),
    "owed but stop needs a holder, by verbs [84]": ("I9",),
    "owed + tick death, a lost spawn retried [43 b]": ("I1",),
    "owed but an unreadable answer drops its run [47]": ("I13", "I18"),
    "owed but one run per member [119]": ("I13", "I18"),
    "ext: today (team 0.12.2)": ("I10r", "I12", "I13", "I16", "I18", "I19"),
    "ext: owed but bounds read once a tick": ("I10",),
    "ext: owed + tick death, bounds count intents [44]": ("I10e",),
    "ext: owed + tick death, ring in two writes": ("I15",),
    "ext: owed but timeout judged first": ("I12", "I16"),
    "ext: owed but a held run resumed [45]": ("I17",),
    "ext: owed but no schedule": ("I1", "I15", "I23", "I25", "I4"),
    "ext: owed but a kill ends the member's run": ("I1", "I9"),
    "ext: owed but a killed run is forgotten": ("I13", "I18"),
    "ext: owed but an answered wake-up killed [58]": ("I12", "I16"),
    "ext: owed but a ring at hand takes the date [69 b]": ("I15",),
    "ext: owed but no allowance reserved [75]": ("I10r",),
    "ext: owed but the whole rest to one wake-up [75]": ("I10p",),
    "ext: owed but a season forgets the runs [82]": ("I13", "I18"),
    "ext: owed but the tick ignores the pause [83]": ("I24",),
    "ext: owed but the pause's periods rung at resume [83]": ("I24",),
    "ext: owed but a recurrence sounds while open [112]": ("I25",),
    "ext: owed but the old hour still sounds [117]": ("I26",),
    "ext: owed but the day sounds again at the new hour [117]": ("I25",),
    "ext: owed but one run per member [119]": ("I13", "I18"),
    "ext: owed but a run per (member, task) [47]": ("I13", "I18"),
    "ext: owed but the run of a recurrence never renewed [120]": ("I21",),
    "ext: owed but the run renewed at every occurrence [120]": ("I21",),
    "ext: owed but the first slot waits one period [121]": ("I27",),
    "ext: owed but a slot counted by its date [121]": ("I27",),
    "ext: owed but the origin forgotten [122]": ("I25",),
    "squad: today (team 0.12.2)": ("I13", "I18", "I19"),
    "squad: owed but run+busy per (member, task), daily split [47]": ("I13", "I18", "I19"),
    "squad: owed but busy per (member, task) [49]": ("I19",),
    "squad: owed but one run per member [119]": ("I13", "I18"),
    "squad: owed but upgrade opens a new run [50]": ("I13", "I18"),
    "squad: owed but upgrade, same session, new key [50]": ("I18",),
    "squad: owed but one run per agent [48]": ("I13", "I18", "I20"),
    "squad: owed but entries as doors at -new [55]": ("I22",),
    "squad: owed but by the hour [38 a]": ("I12", "I16"),
    "squad: owed but the run-null answer read after the timeout [46]": ("I12", "I16"),
}


# A variant whose mechanism is `final`'s alone has nothing to break under `message`: that line is not played
# there, said under the table. No answer is unreadable under message: a words that does not read as an act is
# said [98], and "an unreadable answer drops its run" drops nothing.
FINAL_ONLY = {
    "owed but an unreadable answer drops its run [47]",
}
# The run kept per (member, carrier) (2026-11-06 [119]), measured on 3000 runs under both transports: the owed
# run is (member, carrier), the owed busy the member -- one wake-up at a time, whatever its run; I18 and I13 are judged
# per run: one key, one session, one clone per (member, carrier), never two carriers of a member on one key, in one
# session or in one clone. One run per member (the owed unit before [119]) carries T1 T2, the daily and the
# recurrence on one key: I18 and I13 on every run that answers on two carriers (3000/3000; 2994 in `ext` under
# message). Busy judged per (member, task) wakes a member on two carriers at once (I19) and splits no run, each task
# woken at once being a carrier of its own -- the split it caused under the member's one run (I13 I18, and I1 I4 I12 in
# `reframe`) is gone. A run per (member, task) splits the carriers of several tasks -- the daily's C1 C2 in `squad` and
# `ext`, the recurrence's Q1 Q2 in `ext`: I13 I18, and I19 by the busy per (member, task) `squad` plays with it. One run
# per agent puts the members of agents/ag2 on one key (I20) and a member's carriers with them (I13 I18), and under
# `message` it leaves a task unanswered (I1), as before [119].
BREAKS[("message", "squad: owed but one run per agent [48]")] = ("I1", "I13", "I18", "I20")
# No run stands under final: a message delivered to a continuation is `message`'s alone.
BREAKS[("message", "owed but a message rides the head of a continuation (team 1.13.1) [s.1377]")] = ("M5",)
# Reading the run-null answer after the timeout holds under final (0/3000); under message it lost the race on one
# draw of 3000 (seed 206 of `ext`, 2026-10-23: a kept answer killed -- the owed reading is `response`). Since the
# recurrence entered `ext` (2026-11-01 [112]) its events move the draws and no draw of 3000 reaches that race under
# either transport: the line holds as under final, its race said here and not in BREAKS. Since the run is kept per
# carrier (2026-11-06 [119]) the race is reached again under final on one draw of 3000 (seed 1473 of `ext`: a kept
# answer killed, I12 I16), none under message. Since nothing holds a member any more (2026-11-10, the wait left the
# model) the race is reached under message on one draw of 3000 (seed 1801 of `ext`: a wake-up answered without its
# run, killed `wake-timeout`, its cost never counted -- I12 I16), and no longer under final (0/3000).
BREAKS[("message", "ext: owed but run-null answer read after the timeout")] = ("I12", "I16")

# The ZONE of a line of the tick: its scenario's -- `review`, `reframe`, `squad` --, and for a line of `ext` the
# zone of what its variant turns, `extended` when absent from here: the owed lines, which hold every invariant, and
# the run kept across a kill, a season and the carriers (I13 I18).
ZONE_OF = {
    "ext: owed but bounds read once a tick": "bounds",
    "ext: owed + tick death, bounds count intents [44]": "bounds",
    "ext: owed but timeout judged first": "bounds",
    "ext: owed but run-null answer read after the timeout": "bounds",
    "ext: owed but a held run resumed [45]": "bounds",
    "ext: owed but a kill ends the member's run": "bounds",
    "ext: owed but an answered wake-up killed [58]": "bounds",
    "ext: owed but no allowance reserved [75]": "bounds",
    "ext: owed but the whole rest to one wake-up [75]": "bounds",
    "ext: owed + tick death, ring in two writes": "calendar",
    "ext: owed but no schedule": "calendar",
    "ext: owed but the resume notes T4's member alone [67]": "calendar",
    "ext: owed but a ring at hand takes the date [69 b]": "calendar",
    "ext: owed but the tick ignores the pause [83]": "calendar",
    "ext: owed but the pause's periods rung at resume [83]": "calendar",
    "ext: owed but a recurrence sounds while open [112]": "recurrence",
    "ext: owed, the recurrence's hour changed [117]": "recurrence",
    "ext: owed but the old hour still sounds [117]": "recurrence",
    "ext: owed but the day sounds again at the new hour [117]": "recurrence",
    "ext: owed but the run of a recurrence never renewed [120]": "recurrence",
    "ext: owed but the run renewed at every occurrence [120]": "recurrence",
    "ext: owed, a recurrence by a duration [121]": "recurrence",
    "ext: owed, a recurrence by a duration + tick death 2 % [121]": "recurrence",
    "ext: owed but the first slot waits one period [121]": "recurrence",
    "ext: owed but a slot counted by its date [121]": "recurrence",
    "ext: owed, a recurrence born of a task [122]": "recurrence",
    "ext: owed, a recurrence by a duration born of a task [122]": "recurrence",
    "ext: owed but the origin forgotten [122]": "recurrence",
}
assert set(ZONE_OF) <= {l[1] for l in LINES}, "ZONE_OF names a line LINES does not carry"
TICK_ZONES = ("review", "reframe", "extended", "bounds", "calendar", "recurrence", "squad")


def zone_of(line):
    """-> the zone of a line of the tick."""
    scenario, name = line[:2]
    return ZONE_OF.get(name, "extended") if scenario == "ext" else scenario


def verdict(runs, ok, bad, breaks):
    """-> whether a line holds what it owes: an owed line every run clean, a variant each of its invariants broken."""
    return ok == runs if not breaks else all(bad[c] for c in breaks)


def measures(w, launches=None):
    """-> what one run spent: its end (the steps of the run), its wake-ups, its launches, its cost."""
    st = w.replay()
    cost = sum(e.get("cost", 0) for e in w.journal if e["kind"] in ("wake-ended", "wake-failed"))
    wakes = sum(1 for i in st["intents"].values() if not i.get("relaunch"))
    return w.now, wakes, len(w.tag_record) if launches is None else launches, cost


def said_measures(ends, wakes, launches, cost, runs):
    q = statistics.quantiles(ends, n=10) if len(ends) > 1 else [ends[0]] * 9
    return (f"{q[4]:>6.0f} /{q[8]:>6.0f} {wakes / runs:>6.1f} {launches / runs:>6.1f} {cost / runs:>6.1f}")

FAULTS = [("clean", {}), ("flaky 15%", dict(p=0.15)), ("r2 broken", dict(broken="r2")),
          ("m broken after 1st", dict(broken="m-after-1"))]
SEASON_FAULTS = [("flaky 15%", dict(p=0.15)), ("r2 outage 3-6", dict(outage="r2")), ("r2 broken", dict(broken="r2")),
                 ("m outage 3-6", dict(outage="m")), ("m broken after 1st", dict(broken="m-after-1"))]
HOUSE_FAULTS = SEASON_FAULTS + [("house refuses r2 twice", dict(house="r2")), ("house refuses m twice", dict(house="m")),
                                ("house refuses m twice, flaky 15%", dict(house="m", p=0.15))]
ANSWER = dict(relance="literal", detector="fixed", broadcast=True)          # the rules of 2026-10-12
DEADLOCK = dict(relance="cmh", silence=3, detector="eventual")              # team 0.34.0, the silence in passages [115]
DETECTED = dict(relance="cmh", silence=3)
MESSAGE = dict(DETECTED, detector="eventual", view=True, transport="message")   # the rules of 2026-10-18
INFORMED = dict(DETECTED, detector="eventual", view=True, info=True)            # [114] the root informs, team 0.47.0
# (batch, codes, scenarios, faults, agents, tasks, [(name, v, breaks)])
DEBT_LINES = [
    ("une-reponse-par-message", ("J1", "J5"), ("simple", "cross"), FAULTS, (False,), 1, [
        ("owed", ANSWER, ()),
        ("owed but a later answer settles again", dict(ANSWER, resettle=True), ("J1",)),
        ("owed but a do after the close opens a debt", dict(ANSWER, debt_after_close=True), ("J5",))]),
    ("la-relance-et-le-cycle", ("J2", "J3", "J9"), ("simple", "cross", "up"), FAULTS, (False, True), 1, [
        ("owed", DEADLOCK, ()),
        ("owed but the literal cycle (2026-10-12)", dict(DEADLOCK, relance="literal"), ("J2",)),
        ("owed but a relance without exception", dict(DEADLOCK, relance="always"), ("J2",)),
        ("owed but no relance (team 0.33.0)", dict(DEADLOCK, relance="none"), ("J3",)),
        ("owed but no relance once a final failure stands", dict(DEADLOCK, fell=True), ("J3",)),
        ("owed but no silence: relances without end [115]", dict(DEADLOCK, silence=None), ("J9",))]),
    ("le-detecteur-de-fautes", ("J4",), ("simple", "cross"), SEASON_FAULTS, (False,), 4, [
        ("owed: ◇P, the try the next message, the health view", dict(DETECTED, detector="eventual", view=True), ()),
        ("owed but no health view", dict(DETECTED, detector="eventual"), ()),
        ("owed but an opening to a suspected root waits in silence",
         dict(DETECTED, detector="eventual", view=True, silent_opening=True), ("J4",)),
        ("owed but the detector of 2026-10-12 (excluded for good)", dict(DETECTED, detector="fixed", broadcast=True), ("J4",)),
        ("team 0.34.0, no detector", dict(DETECTED, detector=None), ())]),
    ("le-transport-par-message", ("J1", "J3", "J5", "J9", "I19", "M1", "M5"), ("simple", "cross", "up"),
     FAULTS, (False, True, "silent"), 1, [
        ("message: owed", MESSAGE, ()),
        ("message: owed but a parking abandons its debts", dict(MESSAGE, abandon=True), ("J3", "M1")),
        ("message: owed but a message rides the head of a continuation (team 1.13.1) [s.1377]",
         dict(MESSAGE, delivered="standing"), ("M5",))]),
    ("les-echecs-du-tick", ("H1", "H2", "H3", "J4", "M1"), ("simple", "cross"), HOUSE_FAULTS, (False,), 4, [
        ("message: owed (the reader by the tag, a house refusal no fall, the principal launches a suspect)",
         MESSAGE, ()),
        ("message: owed but the reader takes the first opened (team 0.40.2) [106]", dict(MESSAGE, reader="first"), ("H3",)),
        ("message: owed but a house refusal is a fall (team 0.40.2) [107]", dict(MESSAGE, house_fall=True), ("H1",)),
        ("message: owed but the principal's word waits for the try (team 0.40.2) [108]", dict(MESSAGE, principal_held=True),
         ("H2",))]),
    ("le-message-info (final)", ("J8",), ("simple", "cross"), FAULTS, (False,), 1, [
        ("owed: the root informs its principal at each launch, a worker its supervisor [114]", INFORMED, ()),
        ("owed but an info opens a debt", dict(INFORMED, info_debt=True), ("J8",)),
        ("owed but a member's info wakes its recipient", dict(INFORMED, info_wakes=True), ("J8",))]),
    ("le-message-info (message)", ("J8",), ("simple", "cross"), FAULTS, (False,), 1, [
        ("message: owed, the root informs its principal at each launch, a worker its supervisor [114]",
         dict(MESSAGE, info=True), ()),
        ("message: owed but an info opens a debt", dict(MESSAGE, info=True, info_debt=True), ("J8",)),
        ("message: owed but a member's info wakes its recipient", dict(MESSAGE, info=True, info_wakes=True), ("J8",))]),
    ("le-silence-au-detecteur (final)", ("J9", "J10", "J13", "J14"), ("simple", "cross"), FAULTS, (False, True), 1, [
        ("owed: the root informs ten exchanges or waits for its principal, a stubborn member suspected at silence: "
         "passages [115]", dict(INFORMED, long=True, principal=True), ()),
        ("owed but no silence: relances without end", dict(INFORMED, long=True, principal=True, silence=None), ("J9",)),
        ("owed but the silence counted from the last delivery", dict(INFORMED, long=True, principal=True, count="delivery"),
         ("J10",)),
        ("owed but the silence runs while a member waits for its principal",
         dict(INFORMED, long=True, principal=True, waiting="counted"), ("J13",)),
        ("owed but the beat leaves the exchange under way out", dict(INFORMED, long=True, principal=True, beat="after"),
         ("J14",))]),
    ("le-silence-au-detecteur (message)", ("J9", "J10", "J12", "J13", "J14"), ("simple", "cross"), FAULTS,
     (False, True, "stuck"), 1, [
        ("message: owed, a turn over several launches, the root informs ten exchanges or waits for its principal, a "
         "stubborn member suspected at silence: passages [115]", dict(MESSAGE, info=True, long=True, principal=True, slow=True), ()),
        ("message: owed but no silence: relances without end",
         dict(MESSAGE, info=True, long=True, principal=True, slow=True, silence=None), ("J9",)),
        ("message: owed but the silence counted in launches, a continuation included (team 1.32.0)",
         dict(MESSAGE, info=True, long=True, principal=True, slow=True, count="launches"), ("J10",)),
        ("message: owed but the silence runs while a member waits for its principal",
         dict(MESSAGE, info=True, long=True, principal=True, slow=True, waiting="counted"), ("J13",)),
        ("message: owed but the beat leaves the exchange under way out",
         dict(MESSAGE, info=True, long=True, principal=True, slow=True, beat="after"), ("J14",)),
        ("message: owed but a run standing on a closed task is continued until it parks (team 1.14.1) [s.1409]",
         dict(MESSAGE, info=True, long=True, principal=True, slow=True, closed="parked"), ("J12",))]),
]

# The ZONE of a batch of the debt: its own, the two transports of one batch together.
DEBT_ZONES = {
    "une-reponse-par-message": "answer",
    "la-relance-et-le-cycle": "relance",
    "le-detecteur-de-fautes": "detector",
    "le-transport-par-message": "transport",
    "les-echecs-du-tick": "failures",
    "le-message-info (final)": "info",
    "le-message-info (message)": "info",
    "le-silence-au-detecteur (final)": "silence",
    "le-silence-au-detecteur (message)": "silence",
}
ZONES = TICK_ZONES + tuple(dict.fromkeys(DEBT_ZONES.values())) + ("workers",)


def transport_of(batch):
    return batch[6][0][1].get("transport", "final")


def zone_plays(zone, transport):
    """-> whether a zone has a line under the transport (None: both): a batch of the debt plays under its own
    transport, the workers' clock under `message`."""
    if zone in TICK_ZONES:
        return True
    if zone == "workers":
        return transport in (None, "message")
    return any(DEBT_ZONES[b[0]] == zone and transport in (None, transport_of(b)) for b in DEBT_LINES)


def play_debt(job):
    """One chunk of seeds of one combination of a debt line -> (key, runs, ok, violations, resolved, measures)."""
    key, v, scen, faults, stubborn, tasks, seeds = job
    bad, runs, ok, resolved = Counter(), 0, 0, 0
    ends, wakes, launches, cost = [], 0, 0, 0
    for seed in seeds:
        w = Debt(seed, v, scen, faults, tasks, stubborn)
        found = w.run()
        bad.update(found)
        ok += not found
        runs += 1
        resolved += w.fates.count("resolved")
        end, wk, la, co = measures(w)
        ends.append(end)
        wakes, launches, cost = wakes + wk, launches + la, cost + co
    return key, runs, ok, bad, resolved, (ends, wakes, launches, cost)


def debt_campaign(n, jobs, transport=None, zone=None):
    """-> the lines of the debt that do not hold their verdict; each line said with its codes and its measures."""
    chunk = max(20, n // 30)
    batches = [(b, one) for b, one in enumerate(DEBT_LINES) if transport in (None, transport_of(one))
               and zone in (None, DEBT_ZONES[one[0]])]
    work = []
    for b, (batch, codes, scens, faults, agents, tasks, lines) in batches:
        for l, (name, v, _) in enumerate(lines):
            for scen in scens:
                for f, (_, fault) in enumerate(faults):
                    for stubborn in agents:
                        for lo in range(0, n, chunk):
                            work.append(((b, l, f), v, scen, fault, stubborn, tasks, range(lo, min(n, lo + chunk))))
    work.reverse()                               # the dearest batches first: no long job left for the end
    total = defaultdict(lambda: [0, 0, Counter(), 0, [], 0, 0, 0])
    with Pool(jobs) as pool:
        for key, runs, ok, bad, resolved, (ends, wakes, launches, cost) in pool.imap_unordered(play_debt, work):
            t = total[key]
            t[0] += runs
            t[1] += ok
            t[2].update(bad)
            t[3] += resolved
            t[4] += ends
            t[5], t[6], t[7] = t[5] + wakes, t[6] + launches, t[7] + cost
    failed = []
    for b, (batch, codes, scens, faults, agents, tasks, lines) in batches:
        print(f"\n== {batch}, transport {transport_of(DEBT_LINES[b])} ({n} runs per scenario, fault and agent) ==")
        print(f"  {'line':58} {'verdict':7} {'end p50/p90':>13} {'wakes':>6} {'launch':>6} {'cost':>6}  codes")
        for l, (name, v, breaks) in enumerate(lines):
            parts = [total[(b, l, f)] for f in range(len(faults))]
            runs, ok = sum(t[0] for t in parts), sum(t[1] for t in parts)
            bad = sum((t[2] for t in parts), Counter())
            held = all(not bad[c] for c in codes) if not breaks else all(bad[c] for c in breaks)
            if not held:
                failed.append(name)
            said = " ".join(f"{c} {runs - bad[c]}/{runs}" for c in codes)
            extra = sorted(c for c in bad if c not in codes)
            per = ""
            if tasks > 1:
                per = " | " + " · ".join(f"{t[3] / max(1, t[0]):.2f}/{tasks} {t[5] / max(1, t[0]):5.1f}w" for t in parts)
            spent = said_measures(sum((t[4] for t in parts), []), sum(t[5] for t in parts), sum(t[6] for t in parts),
                                  sum(t[7] for t in parts), runs)
            print(f"  {name:58} {'holds' if held else 'FAILS':7} {spent}  {said}{per}"
                  + (f" | breaks {', '.join(breaks)}" if breaks else "")
                  + (f" | also {' '.join(f'{c} {bad[c]}' for c in extra)}" if extra else ""))
    return failed


def world(line, seed, transport="final"):
    scenario, _, flags, net, crash, ext = LINES[line]
    return SCENARIOS[scenario](seed, dict(flags, transport=transport), net, crash, ext=ext)


def play(job):
    """One chunk of seeds of one line -> (line, ok, Counter of violations, beside, parallel, measures)."""
    line, seeds, transport = job
    bad, ok, beside, parallel = Counter(), 0, 0, 0
    ends, wakes, launches, cost = [], 0, 0, 0
    for seed in seeds:
        w = world(line, seed, transport)
        v = w.run()
        beside += w.kill_beside
        parallel += w.parallel_seen
        if v:
            bad.update(v)
        else:
            ok += 1
        end, wk, la, co = measures(w)
        ends.append(end)
        wakes, launches, cost = wakes + wk, launches + la, cost + co
    return line, ok, bad, beside, parallel, (ends, wakes, launches, cost)


def campaign(lines, n, jobs, transport):
    chunk = max(50, n // 20)
    work = [(line, range(lo, min(n, lo + chunk)), transport) for line in lines for lo in range(0, n, chunk)]
    total = {line: [0, Counter(), 0, 0, [], 0, 0, 0] for line in lines}
    with Pool(jobs) as pool:
        for line, ok, bad, beside, parallel, (ends, wakes, launches, cost) in pool.imap_unordered(play, work):
            t = total[line]
            t[0] += ok
            t[1].update(bad)
            t[2] += beside
            t[3] += parallel
            t[4] += ends
            t[5], t[6], t[7] = t[5] + wakes, t[6] + launches, t[7] + cost
    return total


def lines_table(only, n, jobs, transport="final", zone=None):
    """-> the lines of the tick that do not hold their verdict under the transport; each line said with its
    violations and measures."""
    chosen = [l for l in LINES if (only is None or l[0] == only) and zone in (None, zone_of(l))]
    lines = [i for i, l in enumerate(LINES) if l in chosen and (transport == "final" or l[1] not in FINAL_ONLY)]
    left = [l[1] for l in chosen if transport != "final" and l[1] in FINAL_ONLY]
    total = campaign(lines, n, jobs, transport)
    print(f"== the lines of the tick, transport {transport} ({n} runs per line) ==")
    print(f"{'line':64} {'runs':>5} {'ok':>5} {'verdict':7} {'end p50/p90':>13} {'wakes':>6} {'launch':>6} "
          f"{'cost':>6}  violations (runs touched)")
    failed = []
    for i in lines:
        ok, bad, beside, parallel, ends, wakes, launches, cost = total[i]
        name = LINES[i][1]
        breaks = BREAKS.get((transport, name), BREAKS.get(name, ()))
        held = verdict(n, ok, bad, breaks)
        if not held:
            failed.append(name)
        said = " ".join(f"{k} {bad[k]}" for k in sorted(bad)) if bad else "-"
        print(f"{name:64} {n:>5} {ok:>5} {'holds' if held else 'FAILS':7} "
              f"{said_measures(ends, wakes, launches, cost, n)}  {said}"
              + (f" | breaks {', '.join(breaks)}" if breaks else ""))
    if left:
        print(f"{len(left)} line(s) of final's mechanisms alone, not played under {transport}: " + " · ".join(left))
    return failed


def timed_runs(job):
    transport, argv, seeds = job
    a = TimedArgs(argv)
    return transport, [Timed(a.seed + r, transport, a).play() for r in seeds]


def timed_table(n, argv):
    """The end p50/p90, the launches, the wake-ups and the cost of the scenario `workers` under each transport."""
    a = TimedArgs(argv)
    eager = "random per member" if a.eager is None else f"{a.eager:g}"
    print(f"K={a.files} files, {a.workers} workers, parallel {a.parallel}, overhead {a.overhead:g} s, work {a.work} "
          f"launches per do, ask {a.ask:g}, eager {eager}, crash {a.crash:g}, repair {a.repair:g}, "
          f"faulty {a.faulty:g}, {n} runs")
    print(f"{'transport':<9} {'end p50/p90 s':>14} {'1st re':>6} {'launch':>6} {'wakes':>6} {'USD':>5} "
          f"{'@park':>6} {'dup':>4} {'par':>3}  violations")
    chunk = max(20, n // 20)
    work = [(t, argv, range(lo, min(n, lo + chunk))) for t in ("final", "message") for lo in range(0, n, chunk)]
    found = defaultdict(list)
    with Pool(os.cpu_count()) as pool:
        for t, rs in pool.imap_unordered(timed_runs, work):
            found[t] += rs
    for t in ("final", "message"):
        rs = found[t]
        q = lambda k, p=50: statistics.quantiles([x[k] for x in rs], n=100)[p - 1]
        mean = lambda k: statistics.mean(x[k] for x in rs)
        bad = Counter(c for x in rs for c in x["violations"])
        print(f"{t:<9} {q('makespan'):>6.0f} / {q('makespan', 90):<5.0f} {q('first_re'):>6.0f} "
              f"{mean('launches'):>6.1f} {mean('wakes'):>6.1f} {mean('cost'):>5.2f} {mean('at_turn'):>6.0%} "
              f"{mean('dup'):>4.2f} {max(x['par'] for x in rs):>3}  "
              + (" ".join(f"{k} {bad[k]}" for k in sorted(bad)) or "-"))


def main(argv):
    if len(argv) > 2 and argv[0] == "--trace":
        seed, name = int(argv[1]), argv[2]
        line = next((i for i, l in enumerate(LINES) if l[1] == name), None)
        if line is None:                                     # a line of the debt: its scenario, its fault, its agent
            batch, v = next((b, v) for b in DEBT_LINES for one, v, _ in b[6] if one == name)
            scen = argv[3] if len(argv) > 3 else batch[2][0]
            fault = dict(batch[3]).get(argv[4], {}) if len(argv) > 4 else batch[3][0][1]
            agent = {"False": False, "True": True}.get(argv[5], argv[5]) if len(argv) > 5 else batch[4][0]
            w = Debt(seed, v, scen, fault, batch[5], agent)
        else:
            w = world(line, seed, argv[3] if len(argv) > 3 else "final")
        print("violations:", sorted(w.run()) or "-")
        w.trace()
        return 0
    value = lambda flag: argv[argv.index(flag) + 1] if flag in argv else None
    named = {value(f) for f in ("--only", "--zone", "--jobs", "--transport")} - {None}
    args = [a for a in argv if not a.startswith("--") and a not in named]
    n = int(args[0]) if args else 2000
    only, zone, transport = value("--only"), value("--zone"), value("--transport")
    jobs = int(value("--jobs") or os.cpu_count())
    if transport not in (None, "final", "message"):
        print(f"team-sim: --transport final|message, not {transport}", file=sys.stderr)
        return 2
    if zone is not None and only is not None:
        print("team-sim: --only or --zone, not both", file=sys.stderr)
        return 2
    if zone not in (None,) + ZONES:
        print(f"team-sim: --zone {'|'.join(ZONES)}, not {zone}", file=sys.stderr)
        return 2
    if zone is not None and not zone_plays(zone, transport):
        print(f"team-sim: the zone {zone} has no line under the transport {transport}", file=sys.stderr)
        return 2
    failed = []
    if only in (None, "review", "reframe", "ext", "squad") and zone in (None,) + TICK_ZONES:
        for t in ("final", "message") if transport is None else (transport,):
            failed += lines_table(only, n, jobs, t, zone)
    if only in (None, "debt") and zone in (None,) + tuple(DEBT_ZONES.values()):
        failed += debt_campaign(n, jobs, transport, zone)
    if only in (None, "workers") and zone in (None, "workers") and transport in (None, "message"):
        print(f"\n== the scenario workers: the clock and the cost of both transports ==")
        timed_table(n, argv)
    if failed:
        print(f"\n{len(failed)} line(s) do not hold their verdict: " + " · ".join(failed))
    return 1 if failed and "--owed" in argv else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
