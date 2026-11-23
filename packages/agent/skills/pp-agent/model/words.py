"""The words the layers share: the names of the records, the usage, the tables several of them read."""
from __future__ import annotations

RESPONSES = "responses.jsonl"
MESSAGES = "messages.jsonl"
SESSIONS = "sessions.jsonl"
NAMES = "names.jsonl"            # the name of a run, given by `name`: the last line of a run wins
WORKDIRS = "workdirs.jsonl"
VECTORS = "vectors.jsonl"       # the vectors a run keeps, `{at, agent, run, vectors}`: the last line of a run wins
EMPTIED = "-"                   # `--vector -`: the run keeps no vector any more

USAGE = ("usage: pp-agent add <path> [--type member|chat] | import <path> --from <workspace> | run|start <path> (--message <text> | "
         "--message-file <path>) [--model <m>] [--max-budget-usd <n>] [--permissions auto|strict|bypass] "
         "[--effort low|medium|high|xhigh|max] [--launches <n>] [--new | --run <key>] [--provider <name>] [--harness <command>] [--work <repo> [--base <ref>]] "
         "[--door <document>] [--package <name>=on|off]... [--vector <family>:<id>]... [--tag <id>] [--on-end <command>] "
         "[--json] [--quiet] [--heartbeat <seconds>] [--dry-run] | chat <path> [--run <key>] [--model <m>] "
         "[--max-budget-usd <n>] [--permissions auto|strict|bypass] [--effort low|medium|high|xhigh|max] "
         "[--launches <n>] [--provider <name>] [--harness <command>] [--work <repo> [--base <ref>]] "
         "[--door <document>] [--documents <dir>] [--package <name>=on|off]... [--vector <family>:<id>]... "
         "[--json] [--quiet] [--heartbeat <seconds>] | wait <path> <key> [--timeout <seconds>] | "
         "result <path> <key> | workdirs [<path>] | prune <path> <key> [--force] | "
         "purge <path> (<key> ... | --before <YYYY-MM-DD>) [--yes] [--force] [--json] | remove <path> [--yes] [--json] | "
         "flow <path> <key> [--exchange <n>] [--from <n>] [--follow] [--json] | calibrate [<path> ...] [--json] | "
         "open <path> <key> <NAME[@n]> [<the flags of a launch>] [--json] | close <path> <key> [<the flags of a launch>] [--json] | "
         "list [--json] | status <path> [--json] | name <path> <key> [<name>] | exchanges <path> <key> [--json] | "
         "stats <path> <key> [--json] | providers [--json] | responses [<path>] [--last n] | messages [<path>] [--last n]")

WAIT_INTERVAL = 0.2             # seconds between two looks at the wake lock while `wait` waits

HEAD = "[message from your principal]"    # opens the first prompt of a wake-up, the message under it

PROFILES = {                    # what `add --type <profile>` writes at the agent's SETTINGS, key by key
    "member": (("capabilities", "false"), ("package.steering", "off")),
    "chat": (("capabilities", "false"), ("package.steering", "off"), ("continuity_history_day", "never")),
}

ASIDE = "aside"                 # the kind of a text the harness wrote that a call follows: kept apart of the `words`
FINAL = "final"                 # the kind of the last message of a launch: its text and its length
HAND_BACK = "..."               # a last message that hands back and says nothing: a final of no characters, no text

ANSWER_BOUND = 100              # the characters a last message may hold before the next prompt opens on `TOO_LONG`
TOO_LONG = ("pp: your last answer was too long. Do not say what you print: pp drops it, and the principal does "
            "not hear it. It only wastes context.")

HOUSE = "."                     # the house itself, addressed as an agent: its own instance, its own runs
FAMILY = "agent-run"            # the vector family of the runs: `agent-run:<path>/<key>`, verified here

FLOW_VOICES = ("principal", "conduction", "pp_input", "pp_result", "tool_input", "tool_result", "words",
               "thinking")       # the voices a `flow` sums, in tokens; `calls` beside them

ESTIMATE = {"base": ("CONTEXT_BASE", 0), "ratio": ("FLOW_RATIO", 1.0), "kept": ("THINKING_KEPT", 1.0)}
# what an adapter declares of the estimate of a context where no call measured it, and what holds when it declares
# nothing: no base, every token of the flow as the engine counts it

PURGED = (RESPONSES, MESSAGES, SESSIONS, NAMES, WORKDIRS, VECTORS)   # the records a run of an agent leaves lines in
