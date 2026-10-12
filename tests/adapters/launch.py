"""Scenario `launch` -- 38 case(s) (batch l-abstraction-du-harnais, 2026-09-26; batch la-politique-du-lancement, 2026-09-27, 2026-10-03 and 2026-10-07; batch le-package-agent, 2026-09-27; batch la-session-du-fournisseur, 2026-09-27; batch le-mode-de-permission, 2026-09-27; batch le-materiau-aux-adaptateurs, 2026-10-01; batch le-plafond-du-run, 2026-10-11):
- claude composes its non-interactive line: the print flag, the marble appended, the
  `auto` permission mode (nobody answers a prompt), the stream (`stream-json --verbose`), no prompt argument -- the session kept by the
  provider, no `--no-session-persistence`; the receipt in env; the prompt on stdin
- codex composes: exec, the workspace sandbox, full auto, json, `-` last (stdin); env empty --
  the config the wiring wrote carries the marble and the receipt
- gemini composes: no `-p`, the approval mode, the stream (`stream-json`); env names the composition
  and the receipt; the prompt on stdin
- cursor composes: the print flag, force, the stream (`stream-json`), no prompt argument; env empty -- no channel, no receipt
- the replace marble wins: `system.replace.md` written, claude switches to the replace flag and
  gemini's variable points at it
- a name no adapter carries refuses `provider-unknown`; an adapter without the face refuses
  `launch-unsupported` (a witness wire.py under the bench's temp, never under adapters/)
- a marble the caller hands wins over the adapter's own resolution
- `product_of`: the source engine answers the source, an instance addressed answers the
  source its manifest declares; nothing is launched -- no binary is consulted
- the policy is spelled by each provider: claude `--model`/`--max-budget-usd`, gemini and
  codex `-m`, cursor `--model`
- a provider without a budget refuses `policy-unsupported`, naming itself and the key
- every adapter declares `COST`, the scope of the cost its `answer` reads: `session` (the session's
  cumul), `launch` (this launch alone) or None (no cost read) -- read through `load`, never by the engine
- a malformed policy refuses at the face, before any adapter: `policy-unknown`, `policy-invalid`
- the root's wiring is handed to claude (`--settings <root>/.claude/settings.json` when the
  file stands, nothing otherwise) and ignored by the three others
- the positional call renders the opening lines: codex, gemini and cursor byte for byte those
  of 2026-09-26, claude the same without `--no-session-persistence` and in `auto` mode
- the permission regime is judged once at the face: `auto`, `strict`, `bypass` pass, any other
  value refuses `policy-invalid` naming the key -- before any adapter
- claude spells the three regimes: `auto` (the default) `--permission-mode auto`, `strict`
  `dontAsk`, `bypass` `bypassPermissions` -- one mode flag, nobody answers a prompt
- gemini, codex and cursor keep their line under `auto` and without a policy, byte for byte;
  `strict` and `bypass` refuse `policy-unsupported`, naming the provider and `permissions`
- the answer is read by the adapter: `answer(stdout, stderr)` of the four -- claude `result`,
  `total_cost_usd`, `permission_denials`; gemini `response`; codex the last `agent_message` of
  the JSONL; cursor `result` -- normalised to {response, cost_usd, denials, error, session}
- an error is named, never lost: claude `is_error` says its `subtype` as the error, the text
  kept; a stdout no reading parses refuses `session-missing`, its tail cited
- gemini names its `error` field; codex without an agent message answers the last line
- an adapter without the face refuses `answer-unsupported`, the face never launches
- the resume of the four: a session reopens it -- claude `--resume S`, codex `exec … resume S`,
  gemini `--resume S`, cursor `--resume S` -- and the marble comes back at every call: claude and
  gemini carry it with the receipt as at the opening (their session does not reliably record the
  system prompt), codex and cursor nothing more than at the opening; the policy, the wiring, the prompt
- the opening keeps the session: without a session, no line carries a resume
- the session is judged once at the face, before any adapter: empty, blank or not a text
  refuses `session-invalid`
- the identity is the provider's: `answer()` reads claude and cursor `session_id`, codex the
  `thread_id` of `thread.started`, gemini `session_id`
- no identity, no answer: an output that carries none refuses `session-missing`, for the four,
  its error or its tail cited
- the material rides every line: `workdir={path, branch, base}` adds the same `PP_WORKDIR` and
  `PP_CONSOLE` to the env of the four and opens their prompt on the same head, a blank line,
  the text -- the argv of before otherwise; no provider flag
- the head bends to what it knows: without `branch` and `base` their segments are absent
- a malformed material refuses at the face, before any adapter: an absolute path, a `..`, no
  path, an empty one, an unknown key, not a mapping -- `workdir-invalid` naming the key
- an adapter whose `launch` takes no `workdir` refuses `workdir-unsupported` by its name when a
  material is handed, and composes as before without one (a witness under the bench's temp)
- without a material the lines hold: `workdir=None` renders the four byte for byte as the
  positional call does, argv and env
- the effort is judged once at the face: `low`, `medium`, `high`, `xhigh`, `max` pass, any other
  value refuses `policy-invalid` naming the key -- before any adapter
- claude, codex and cursor spell the effort, each by its provider's channel: claude `--effort`,
  codex `-c model_reasoning_effort="…"`, cursor the model's suffix; `max` is codex's and cursor's
  `xhigh`; cursor without a model refuses `policy-unsupported`
- gemini refuses the effort `policy-unsupported`, naming itself and the key: no flag carries it
- (rework 2026-10-07) the prompt leaves by stdin at the four: `launch()` renders `(argv, env, stdin)`,
  `stdin` the prompt, no element of `argv` carrying it -- a prompt of 200 000 characters keeps every
  element of `argv` under the 131 072 bytes one argument may hold
- an adapter of the former shape, whose `launch` renders two elements, refuses `launch-malformed`
- a marble handed by its path reaches the provider's channel: claude appends `system.common.md`;
  gemini names `system.common.gemini.md` when `wire()` composed it, the file handed otherwise
- the mark of the principal is in nothing the face composes: `PP_CONDUCTED_BY_PRINCIPAL` absent from
  `env` at the four, a marble and a material handed
"""
from __future__ import annotations

import json
from pathlib import Path

from conductor import Refusal, adapters, instance
from tests.harness import INSTANCE, PRODUCT_ENGINE, SOURCE


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("launch").made
    ws = made.parent
    sys_dir = made / ".sys"
    prompt = "▌ pp · run abc123\nthe pending block, then the message"

    def compose(provider: str, **kw):
        return adapters.launch(provider, ws, made, prompt, **kw)

    def refusal_of(call) -> str:
        """-> `<code>: <message>` of the refusal the call raises, or what it did instead."""
        try:
            return f"accepted: {call()}"
        except Refusal as refusal:
            return f"{refusal.code}: {refusal}"
        except Exception as raised:                       # noqa: BLE001 -- said, never swallowed
            return f"{type(raised).__name__}: {raised}"

    def composed(provider: str, **kw):
        """-> (argv, env, stdin) of the four, or (['<code>: …'], {}, '') when the face refused or raised."""
        try:
            return compose(provider, **kw)
        except Exception as raised:                       # noqa: BLE001 -- said in the failure line
            return [f"{getattr(raised, 'code', type(raised).__name__)}: {raised}"], {}, ""

    # --- claude ------------------------------------------------------------------------
    argv, env, stdin = composed("claude")
    marble = str(sys_dir / "system.md")
    if (argv[0] == "claude" and argv[1] == "-p" and prompt not in argv and stdin == prompt
            and argv[argv.index("--append-system-prompt-file") + 1] == marble
            and argv[argv.index("--permission-mode") + 1] == "auto"
            and argv[argv.index("--permission-prompts") + 1] == "none"
            and argv[argv.index("--output-format") + 1] == "stream-json" and "--verbose" in argv
            and "--no-session-persistence" not in argv and "--resume" not in argv
            and "--system-prompt-file" not in argv
            and env == {"PP_MARBLE": "1"}):
        held("claude composes", "-p, the marble appended, auto/none, stream-json --verbose, the session kept, "
             "no prompt argument; env carries the receipt; the prompt on stdin")
    else:
        failures.append(f"  ✗ claude launch              {argv} {env} {stdin[:40]!r}")

    # --- codex -------------------------------------------------------------------------
    argv, env, stdin = composed("codex")
    if (argv[:2] == ["codex", "exec"] and argv[-1] == "-" and prompt not in argv and stdin == prompt
            and argv[argv.index("--sandbox") + 1] == "workspace-write"
            and "--full-auto" in argv and "--json" in argv and env == {}):
        held("codex composes", "exec, workspace-write, full-auto, json, `-` last; "
             "env empty -- config.toml carries the marble and the receipt; the prompt on stdin")
    else:
        failures.append(f"  ✗ codex launch               {argv} {env} {stdin[:40]!r}")

    # --- gemini ------------------------------------------------------------------------
    argv, env, stdin = composed("gemini")
    composition = str(sys_dir / "system.gemini.md")
    if (argv[:1] == ["gemini"] and "-p" not in argv and prompt not in argv and stdin == prompt
            and argv[argv.index("--approval-mode") + 1] == "yolo"
            and argv[argv.index("--output-format") + 1] == "stream-json"
            and env == {"GEMINI_SYSTEM_MD": composition, "PP_MARBLE": "1"}):
        held("gemini composes", "no -p, yolo, stream-json; env names the composition and the receipt; "
             "the prompt on stdin")
    else:
        failures.append(f"  ✗ gemini launch              {argv} {env} {stdin[:40]!r}")

    # --- cursor ------------------------------------------------------------------------
    argv, env, stdin = composed("cursor")
    if (argv[:2] == ["agent", "-p"] and prompt not in argv and stdin == prompt and "--force" in argv
            and argv[argv.index("--output-format") + 1] == "stream-json" and env == {}):
        held("cursor composes", "agent -p, force, stream-json, no prompt argument; env empty -- "
             "no system-prompt channel, no receipt; the prompt on stdin")
    else:
        failures.append(f"  ✗ cursor launch              {argv} {env} {stdin[:40]!r}")

    # --- the replace marble wins ---------------------------------------------------------
    replace = sys_dir / "system.replace.md"
    replace.write_text("# replaced\n", encoding="utf-8")
    try:
        claude_argv = composed("claude")[0]
        gemini_env = composed("gemini")[1]
    finally:
        replace.unlink()
    if (claude_argv[claude_argv.index("--system-prompt-file") + 1] == str(replace)
            and "--append-system-prompt-file" not in claude_argv
            and gemini_env["GEMINI_SYSTEM_MD"] == str(replace)):
        held("the replace marble wins", "claude switches to --system-prompt-file, "
             "gemini's variable points at system.replace.md -- as the launchers do")
    else:
        failures.append(f"  ✗ replace marble             {claude_argv} {gemini_env}")

    # --- the two refusals ----------------------------------------------------------------
    expect("provider-unknown", lambda: compose("nope"))
    witness = bench.temp() / "witness-adapters" / "mute" / "wire.py"
    witness.parent.mkdir(parents=True)
    witness.write_text("def wire(workspace, meta):\n    return []\n", encoding="utf-8")
    expect("launch-unsupported", lambda: compose("mute", root=witness.parent.parent))

    # --- a marble the caller hands wins ------------------------------------------------
    handed = bench.temp() / "handed.md"
    handed.write_text("# handed\n", encoding="utf-8")
    argv = composed("claude", marble=handed)[0]
    env = composed("gemini", marble=handed)[1]
    if (argv[argv.index("--append-system-prompt-file") + 1] == str(handed)
            and env.get("GEMINI_SYSTEM_MD") == str(handed)):
        held("a handed marble wins", "claude appends it, gemini's variable names it")
    else:
        failures.append(f"  ✗ handed marble              {argv} {env}")

    # --- product_of, and nothing launched --------------------------------------------------
    addressed = bench.install(bench.temp() / "addressed" / INSTANCE)
    at_source = adapters.product_of()
    at_meta = adapters.product_of(addressed)
    declared = Path(instance.read(addressed)["source"])   # the witness source it was installed from
    face_text = (SOURCE / "engine" / "conductor" / "packaging" / "adapters.py").read_text(encoding="utf-8")
    quiet = not any(word in face_text for word in ("subprocess", "shutil", "which(", "Popen"))
    if at_source == SOURCE and at_meta == declared and quiet:
        held("product_of, nothing launched", f"the source engine answers {SOURCE.name}, an "
             "instance addressed answers its declared source; the face names no process")
    else:
        failures.append(f"  ✗ product_of                 {at_source} {at_meta} quiet={quiet}")

    # --- la-politique-du-lancement: the policy, spelled by each provider ------------------
    policy = {"model": "m", "max_budget_usd": 0.5}
    spelled = {}
    for provider in ("claude", "gemini", "codex", "cursor"):
        spelled[provider] = composed(provider, policy={"model": "m"})[0]
    claude_argv, _, claude_stdin = composed("claude", policy=policy)
    if (claude_argv and "--model" in claude_argv and claude_argv[claude_argv.index("--model") + 1] == "m"
            and claude_argv[claude_argv.index("--max-budget-usd") + 1] == "0.5"
            and claude_stdin == prompt
            and "-m" in spelled["gemini"] and spelled["gemini"][spelled["gemini"].index("-m") + 1] == "m"
            and "-m" in spelled["codex"] and spelled["codex"][spelled["codex"].index("-m") + 1] == "m"
            and "--model" in spelled["cursor"] and spelled["cursor"][spelled["cursor"].index("--model") + 1] == "m"):
        held("the policy is spelled by each provider", "claude --model/--max-budget-usd, gemini -m, "
             "codex -m, cursor --model -- the prompt still on stdin")
    else:
        failures.append(f"  ✗ policy spelled             {claude_argv} {spelled}")

    # --- a provider without a budget refuses by its name ----------------------------------
    refused = {}
    for provider in ("gemini", "codex", "cursor"):
        try:
            compose(provider, policy={"max_budget_usd": 1})
            refused[provider] = "accepted"
        except Exception as raised:
            refused[provider] = f"{getattr(raised, 'code', type(raised).__name__)}: {raised}"
    if all(one.startswith("policy-unsupported") and "max_budget_usd" in one and name in one
           for name, one in refused.items()):
        held("a provider without a budget refuses by its name", "gemini, codex, cursor: "
             "policy-unsupported naming the provider and max_budget_usd")
    else:
        failures.append(f"  ✗ policy unsupported         {refused}")

    # --- every adapter declares the scope of the cost it reads ------------------------------
    product = adapters.product_of(made) / "adapters"
    declared = {one.name: getattr(adapters.load(one.name, made), "COST", "absent")
                for one in sorted(product.iterdir()) if (one / "wire.py").is_file()}
    if declared and all(value in ("session", "launch", None) for value in declared.values()):
        held("every adapter declares the scope of its cost", f"COST read through load: {declared}")
    else:
        failures.append(f"  ✗ cost declared              {declared}")

    # --- a malformed policy refuses at the face, before any adapter -----------------------
    expect("policy-unknown", lambda: compose("claude", policy={"turns": 3}))
    expect("policy-invalid", lambda: compose("claude", policy={"max_budget_usd": -1}))
    expect("policy-invalid", lambda: compose("claude", policy={"model": ""}))
    expect("policy-unknown", lambda: compose("mute", policy={"turns": 3}, root=witness.parent.parent))

    # --- the root's wiring is handed to claude, ignored by the others ---------------------
    home = bench.temp() / "home"
    (home / ".claude").mkdir(parents=True)
    settings = home / ".claude" / "settings.json"
    settings.write_text('{"permissions": {"allow": ["Bash(./pp:*)"]}}\n', encoding="utf-8")
    wired_argv = composed("claude", wiring=home)[0]
    bare_argv = composed("claude", wiring=bench.temp() / "nowhere")[0]
    others = [composed(provider, wiring=home)[0] for provider in ("gemini", "codex", "cursor")]
    if ("--settings" in wired_argv and wired_argv[wired_argv.index("--settings") + 1] == str(settings)
            and "--settings" not in bare_argv
            and all("--settings" not in one and str(home) not in " ".join(one) for one in others)):
        held("the root's wiring is handed to claude", "--settings <root>/.claude/settings.json "
             "when the file stands, nothing when it does not; gemini, codex and cursor ignore it")
    else:
        failures.append(f"  ✗ wiring handed              {wired_argv} {bare_argv} {others}")

    # --- the positional call holds: the opening lines, the prompt on stdin ------------------------
    before = {"claude": (["claude", "-p", "--append-system-prompt-file", marble,
                          "--permission-mode", "auto", "--permission-prompts", "none",
                          "--output-format", "stream-json", "--verbose"],
                         {"PP_MARBLE": "1"}, prompt),
              "codex": (["codex", "exec", "--sandbox", "workspace-write", "--full-auto", "--json", "-"], {}, prompt),
              "gemini": (["gemini", "--approval-mode", "yolo", "--output-format", "stream-json"],
                         {"GEMINI_SYSTEM_MD": composition, "PP_MARBLE": "1"}, prompt),
              "cursor": (["agent", "-p", "--force", "--output-format", "stream-json"], {}, prompt)}
    after = {provider: composed(provider) for provider in before}
    if all(after[provider] == (list(argv), env, text) for provider, (argv, env, text) in before.items()):
        held("the positional call holds", "launch(provider, ws, meta, prompt) renders the opening: "
             "the lines of 2026-09-26 less the prompt, claude without --no-session-persistence, in auto "
             "mode; the prompt on stdin")
    else:
        failures.append(f"  ✗ positional call            {after}")

    # --- le-package-agent: the answer, read by the adapter ---------------------------------
    claude_json = json.dumps({"type": "result", "subtype": "success", "is_error": False, "duration_ms": 2398,
                              "num_turns": 1, "result": "pong", "total_cost_usd": 0.045,
                              "permission_denials": [], "session_id": "c-1"})
    codex_jsonl = ('{"type": "thread.started", "thread_id": "t1"}\n'
                   '{"type": "item.completed", "item": {"id": "item_0", "type": "agent_message", "text": "done"}}\n'
                   '{"type": "turn.completed", "usage": {"input_tokens": 10}}\n')
    read = {}
    try:
        read["claude"] = adapters.answer("claude", made, claude_json, "")
        read["gemini"] = adapters.answer("gemini", made, json.dumps({"session_id": "g-1", "response": "hi",
                                                                     "stats": {}}), "")
        read["codex"] = adapters.answer("codex", made, codex_jsonl, "")
        read["cursor"] = adapters.answer("cursor", made, json.dumps({"type": "result", "result": "ok",
                                                                     "is_error": False, "session_id": "u-1"}), "")
    except Exception as raised:                       # an AttributeError before the batch
        read = {"raised": f"{type(raised).__name__}: {raised}"}
    if (read.get("claude") == {"response": "pong", "cost_usd": 0.045, "denials": [], "error": None,
                               "session": "c-1"}
            and read.get("gemini") == {"response": "hi", "cost_usd": None, "denials": [], "error": None,
                                       "session": "g-1"}
            and read.get("codex") == {"response": "done", "cost_usd": None, "denials": [], "error": None,
                                      "session": "t1"}
            and read.get("cursor") == {"response": "ok", "cost_usd": None, "denials": [], "error": None,
                                       "session": "u-1"}):
        held("the answer is read by the adapter", "claude result/cost/denials, gemini response, "
             "codex the agent_message, cursor result -- one shape")
    else:
        failures.append(f"  ✗ answer read                {read}")

    # --- an error is named, never lost ------------------------------------------------------------
    try:
        broke = adapters.answer("claude", made, json.dumps({"type": "result", "subtype": "error_max_budget_usd",
                                                            "is_error": True, "result": "", "total_cost_usd": 0.223,
                                                            "permission_denials": [],
                                                            "session_id": "c-2"}), "")
    except Exception as raised:
        broke = {"raised": type(raised).__name__}
    garbage = refusal_of(lambda: adapters.answer("claude", made, "not json at all\nsecond line", "boom on stderr"))
    if (broke.get("error") == "error_max_budget_usd" and broke.get("response") is None
            and broke.get("cost_usd") == 0.223 and broke.get("session") == "c-2"
            and garbage.startswith("session-missing") and "unreadable" in garbage and "second line" in garbage):
        held("an error is named, never lost", "is_error names the subtype, an empty result is None, "
             "the session kept; an unreadable stdout refuses session-missing with its tail")
    else:
        failures.append(f"  ✗ answer error               {broke} {garbage}")

    # --- gemini's error, codex's last line ----------------------------------------------------------
    try:
        gem = adapters.answer("gemini", made, json.dumps({"session_id": "g-2", "response": "",
                                                           "error": {"message": "quota"}}), "")
        cod = adapters.answer("codex", made, '{"type": "thread.started", "thread_id": "t2"}\n'
                              '{"type": "turn.completed"}\nplain last line\n', "")
    except Exception as raised:
        gem, cod = {"raised": type(raised).__name__}, {}
    if (gem.get("response") is None and "quota" in str(gem.get("error"))
            and cod.get("response") == "plain last line" and cod.get("error") is None):
        held("gemini's error, codex's last line", "gemini names its error field; codex without an "
             "agent message answers the last non-empty line")
    else:
        failures.append(f"  ✗ answer gemini/codex        {gem} {cod}")

    # --- an adapter without the face refuses -----------------------------------------------------------
    try:
        expect("answer-unsupported", lambda: adapters.answer("mute", made, "{}", "", root=witness.parent.parent))
    except AttributeError as raised:
        failures.append(f"  ✗ answer-unsupported         {raised}")

    # --- la-session-du-fournisseur: the resume of the four -----------------------------------------
    policy = {"model": "m"}
    resumed = {}
    for provider in ("claude", "codex", "gemini", "cursor"):
        resumed[provider] = composed(provider, session="S", policy=policy, wiring=home)
    c_argv, c_env, c_in = resumed["claude"]
    x_argv, x_env, x_in = resumed["codex"]
    g_argv, g_env, g_in = resumed["gemini"]
    u_argv, u_env, u_in = resumed["cursor"]
    marble_flags = ("--append-system-prompt-file", "--system-prompt-file")
    if (c_argv[:2] == ["claude", "-p"] and c_argv[c_argv.index("--resume") + 1] == "S"
            and c_argv[c_argv.index("--append-system-prompt-file") + 1] == marble
            and c_argv[c_argv.index("--permission-mode") + 1] == "auto"
            and c_argv[c_argv.index("--output-format") + 1] == "stream-json"
            and c_argv[c_argv.index("--model") + 1] == "m"
            and c_argv[c_argv.index("--settings") + 1] == str(settings)
            and prompt not in c_argv and c_in == prompt and c_env == {"PP_MARBLE": "1"}
            and x_argv[:2] == ["codex", "exec"] and x_argv[-3:] == ["resume", "S", "-"] and x_in == prompt
            and x_argv[x_argv.index("--sandbox") + 1] == "workspace-write" and "--full-auto" in x_argv
            and "--json" in x_argv and x_argv[x_argv.index("-m") + 1] == "m" and x_env == {}
            and g_argv[:3] == ["gemini", "--resume", "S"] and "-p" not in g_argv and g_in == prompt
            and g_argv[g_argv.index("--approval-mode") + 1] == "yolo"
            and g_argv[g_argv.index("--output-format") + 1] == "stream-json"
            and g_argv[g_argv.index("-m") + 1] == "m"
            and g_env == {"GEMINI_SYSTEM_MD": composition, "PP_MARBLE": "1"}
            and not any(flag in x_argv + u_argv for flag in marble_flags)
            and u_argv[:4] == ["agent", "-p", "--resume", "S"] and "--force" in u_argv
            and u_argv[u_argv.index("--output-format") + 1] == "stream-json"
            and u_argv[u_argv.index("--model") + 1] == "m" and prompt not in u_argv and u_in == prompt
            and u_env == {}):
        held("the resume of the four", "claude --resume S, codex exec … resume S -, gemini --resume S, "
             "cursor --resume S -- the marble and the receipt where the opening puts them, policy, wiring, "
             "the prompt on stdin")
    else:
        failures.append(f"  ✗ resume of the four         {resumed}")

    # --- the opening keeps the session ------------------------------------------------------------
    opened = {provider: compose(provider)[0] for provider in ("claude", "codex", "gemini", "cursor")}
    if all("--resume" not in argv and "resume" not in argv and "--no-session-persistence" not in argv
           for argv in opened.values()):
        held("the opening keeps the session", "no session: no line resumes, none throws the session away")
    else:
        failures.append(f"  ✗ opening keeps the session  {opened}")

    # --- the session is judged once, before any adapter ------------------------------------------------
    expect("session-invalid", lambda: compose("claude", session=""))
    expect("session-invalid", lambda: compose("claude", session="   "))
    expect("session-invalid", lambda: compose("claude", session=42))
    expect("session-invalid", lambda: compose("mute", session="", root=witness.parent.parent))

    # --- the identity is the provider's ---------------------------------------------------------------
    identity = {}
    for provider, out in (("claude", json.dumps({"type": "result", "result": "a", "session_id": "c-9"})),
                          ("cursor", json.dumps({"type": "result", "result": "b", "session_id": "u-9"})),
                          ("gemini", json.dumps({"session_id": "g-9", "response": "c"})),
                          ("codex", '{"type": "thread.started", "thread_id": "t-9"}\n'
                                    '{"type": "item.completed", "item": {"type": "agent_message", "text": "d"}}\n')):
        try:
            identity[provider] = adapters.answer(provider, made, out, "").get("session")
        except Exception as raised:
            identity[provider] = f"{type(raised).__name__}: {raised}"
    if identity == {"claude": "c-9", "cursor": "u-9", "gemini": "g-9", "codex": "t-9"}:
        held("the identity is the provider's", "claude and cursor session_id, codex thread_id of "
             "thread.started, gemini session_id")
    else:
        failures.append(f"  ✗ identity read              {identity}")

    # --- no identity, no answer ---------------------------------------------------------------------
    missing = {provider: refusal_of(lambda provider=provider, out=out: adapters.answer(provider, made, out, "stderr tail"))
               for provider, out in (("claude", json.dumps({"type": "result", "result": "a"})),
                                     ("cursor", json.dumps({"type": "result", "result": "b"})),
                                     ("gemini", json.dumps({"response": "c", "stats": {}})),
                                     ("codex", '{"type": "item.completed", "item": {"type": "agent_message", "text": "d"}}\n'))}
    if all(one.startswith("session-missing") and name in one for name, one in missing.items()):
        held("no identity, no answer", "claude, cursor, gemini, codex: an output without its identity "
             "refuses session-missing, the provider named")
    else:
        failures.append(f"  ✗ session missing            {missing}")

    # --- the permission regime is judged once, at the face ----------------------------------------
    try:
        passed = {regime: adapters.judged({"permissions": regime}) for regime in ("auto", "strict", "bypass")}
    except Exception as raised:                       # a face that does not know the key: policy-unknown
        passed = {"raised": f"{getattr(raised, 'code', type(raised).__name__)}: {raised}"}
    wrong = {repr(value): refusal_of(lambda value=value: compose("claude", policy={"permissions": value}))
             for value in ("yolo", "", 1, None, "bypassPermissions")}
    ahead = refusal_of(lambda: compose("mute", policy={"permissions": "yolo"}, root=witness.parent.parent))
    if (passed == {regime: {"permissions": regime} for regime in ("auto", "strict", "bypass")}
            and all(one.startswith("policy-invalid") and "permissions" in one for one in wrong.values())
            and ahead.startswith("policy-invalid")):
        held("the permission regime is judged at the face", "auto, strict, bypass pass; yolo, '', 1, None "
             "and claude's own word refuse policy-invalid naming the key, before any adapter")
    else:
        failures.append(f"  ✗ permissions judged         {passed} {wrong} {ahead}")

    # --- claude spells the three regimes ------------------------------------------------------------
    def mode_of(argv: list[str]) -> tuple:
        """-> (the value of every --permission-mode, the value of --permission-prompts)."""
        modes = tuple(argv[i + 1] for i, word in enumerate(argv) if word == "--permission-mode")
        prompts = argv[argv.index("--permission-prompts") + 1] if "--permission-prompts" in argv else None
        return modes, prompts

    regimes = {}
    for regime in (None, "auto", "strict", "bypass"):
        argv, _, text = composed("claude", policy=None if regime is None else {"permissions": regime})
        regimes[regime] = mode_of(argv) + ((text == prompt and prompt not in argv),)
    if regimes == {None: (("auto",), "none", True), "auto": (("auto",), "none", True),
                   "strict": (("dontAsk",), "none", True), "bypass": (("bypassPermissions",), "none", True)}:
        held("claude spells the three regimes", "no policy and auto: --permission-mode auto; strict: "
             "dontAsk; bypass: bypassPermissions -- one mode flag, --permission-prompts none, the prompt on stdin")
    else:
        failures.append(f"  ✗ claude regimes             {regimes}")

    # --- gemini, codex, cursor keep their line; strict and bypass refuse by name ---------------------
    kept, refused = {}, {}
    for provider in ("gemini", "codex", "cursor"):
        kept[provider] = composed(provider, policy={"permissions": "auto"}) == before[provider]
        for regime in ("strict", "bypass"):
            refused[(provider, regime)] = refusal_of(lambda provider=provider, regime=regime:
                                                     compose(provider, policy={"permissions": regime}))
    if (kept == {"gemini": True, "codex": True, "cursor": True}
            and all(one.startswith("policy-unsupported") and provider in one and "permissions" in one
                    for (provider, _), one in refused.items())):
        held("gemini, codex, cursor keep their line", "auto renders the line of 2026-09-26 byte for byte; "
             "strict and bypass refuse policy-unsupported naming the provider and permissions")
    else:
        failures.append(f"  ✗ other regimes              {kept} {refused}")

    # --- le-materiau-aux-adaptateurs: the material rides every line ------------------------------
    material = {"path": "work/a1b2c3", "branch": "agent/dev1/a1b2c3", "base": "main@1234abc"}
    console = str(ws.resolve() / "pp")
    head = (f"[material work/a1b2c3 · branch agent/dev1/a1b2c3 · from main@1234abc · console {console} -- "
            "reach the material by git -C and relative paths, never cd; the target's hooks are not in the clone]")
    carried = {provider: composed(provider, workdir=material) for provider in before}
    wanted = {provider: (list(argv), {**env, "PP_WORKDIR": "work/a1b2c3", "PP_CONSOLE": console},
                         head + "\n\n" + prompt)
              for provider, (argv, env, _) in before.items()}
    if carried == wanted:
        held("the material rides every line", "claude, codex, gemini, cursor: the same PP_WORKDIR and "
             "PP_CONSOLE in env, stdin the same head then a blank line then the prompt; the argv of before")
    else:
        failures.append(f"  ✗ material on the four       {carried}")

    # --- the head bends to what it knows ------------------------------------------------------------
    bent_argv, bent_env, bent_in = composed("claude", workdir={"path": "work/k"})
    bent_head = (f"[material work/k · console {console} -- reach the material by git -C and relative paths, "
                 "never cd; the target's hooks are not in the clone]")
    if bent_in == bent_head + "\n\n" + prompt and bent_env.get("PP_WORKDIR") == "work/k":
        held("the head bends to what it knows", "no branch, no base: their segments are absent")
    else:
        failures.append(f"  ✗ head bends                 {bent_argv[-1:]} {bent_env} {bent_in[:80]!r}")

    # --- a malformed material refuses at the face, before any adapter --------------------------------
    malformed = {"absolute": ({"path": "/abs"}, "path"), "dotdot": ({"path": "../x"}, "path"),
                 "no path": ({}, "path"), "empty": ({"path": ""}, "path"),
                 "unknown key": ({"path": "w", "repo": "x"}, "repo"), "not a mapping": ("w", "mapping")}
    judged = {name: refusal_of(lambda bad=bad: compose("claude", workdir=bad)) for name, (bad, _) in malformed.items()}
    ahead = refusal_of(lambda: compose("mute", workdir={"path": "/abs"}, root=witness.parent.parent))
    if (all(judged[name].startswith("workdir-invalid") and key in judged[name] for name, (_, key) in malformed.items())
            and ahead.startswith("workdir-invalid")):
        held("a malformed material refuses at the face", "absolute, .., no path, empty, an unknown key, not a "
             "mapping: workdir-invalid naming the key -- before any adapter")
    else:
        failures.append(f"  ✗ material judged            {judged} {ahead}")

    # --- an adapter without the keyword refuses by its name ------------------------------------------
    deaf = witness.parent.parent / "deaf" / "wire.py"
    deaf.parent.mkdir(parents=True)
    deaf.write_text("def wire(workspace, meta):\n    return []\n\n\n"
                    "def launch(workspace, meta, marble, prompt, wiring=None, policy=None, session=None):\n"
                    "    return ['deaf'], {}, prompt\n", encoding="utf-8")
    unsupported = refusal_of(lambda: compose("deaf", workdir={"path": "w"}, root=witness.parent.parent))
    plain = composed("deaf", root=witness.parent.parent)
    if (unsupported.startswith("workdir-unsupported") and "deaf" in unsupported
            and plain == (["deaf"], {}, prompt)):
        held("an adapter without the keyword refuses by its name", "workdir-unsupported naming the adapter "
             "when a material is handed; without one it composes as before")
    else:
        failures.append(f"  ✗ workdir unsupported        {unsupported} {plain}")

    # --- without a material the lines hold -------------------------------------------------------------
    bare = {provider: composed(provider, workdir=None) for provider in before}
    if all(bare.get(provider) == (list(argv), env, text) for provider, (argv, env, text) in before.items()):
        held("without a material the lines hold", "workdir=None renders the four byte for byte as the "
             "positional call does, argv, env and stdin")
    else:
        failures.append(f"  ✗ lines hold                 {bare}")

    # --- la-politique-du-lancement (rework): the effort, judged once at the face --------------------
    levels = ("low", "medium", "high", "xhigh", "max")
    try:
        accepted = {level: adapters.judged({"effort": level}) for level in levels}
    except Exception as raised:                       # a face that does not know the key: policy-unknown
        accepted = {"raised": f"{getattr(raised, 'code', type(raised).__name__)}: {raised}"}
    rejected = {repr(value): refusal_of(lambda value=value: compose("claude", policy={"effort": value}))
                for value in ("turbo", "", 1, None, "minimal")}
    ahead = refusal_of(lambda: compose("mute", policy={"effort": "turbo"}, root=witness.parent.parent))
    if (accepted == {level: {"effort": level} for level in levels}
            and all(one.startswith("policy-invalid") and "effort" in one for one in rejected.values())
            and ahead.startswith("policy-invalid")):
        held("the effort is judged at the face", "low, medium, high, xhigh, max pass; turbo, '', 1, None and "
             "codex's own minimal refuse policy-invalid naming the key, before any adapter")
    else:
        failures.append(f"  ✗ effort judged              {accepted} {rejected} {ahead}")

    # --- claude, codex and cursor spell the effort by their channel ---------------------------------
    def spelled_effort(provider: str, level: str, model: str | None = "m") -> list[str] | str:
        asked = {"effort": level, **({"model": model} if model else {})}
        try:
            return compose(provider, policy=asked)[0]
        except Exception as raised:
            return f"{getattr(raised, 'code', type(raised).__name__)}: {raised}"

    table = {provider: {level: spelled_effort(provider, level) for level in levels}
             for provider in ("claude", "codex", "cursor")}

    def flag_value(argv, flag: str):
        return argv[argv.index(flag) + 1] if isinstance(argv, list) and flag in argv else None

    claude_words = {level: flag_value(argv, "--effort") for level, argv in table["claude"].items()}
    codex_words = {level: flag_value(argv, "-c") for level, argv in table["codex"].items()}
    cursor_models = {level: flag_value(argv, "--model") for level, argv in table["cursor"].items()}
    bare_cursor = spelled_effort("cursor", "high", model=None)
    if (claude_words == {level: level for level in levels}
            and all(prompt not in argv for argv in table["claude"].values())
            and codex_words == {"low": 'model_reasoning_effort="low"', "medium": 'model_reasoning_effort="medium"',
                                "high": 'model_reasoning_effort="high"', "xhigh": 'model_reasoning_effort="xhigh"',
                                "max": 'model_reasoning_effort="xhigh"'}
            and all(argv[-1] == "-" for argv in table["codex"].values())
            and cursor_models == {"low": "m-low", "medium": "m-medium", "high": "m-high", "xhigh": "m-xhigh",
                                  "max": "m-xhigh"}
            and bare_cursor.startswith("policy-unsupported") and "cursor" in bare_cursor and "model" in bare_cursor):
        held("claude, codex and cursor spell the effort", "claude --effort <word>; codex -c "
             "model_reasoning_effort=\"<word>\", max as xhigh; cursor the model's suffix, max as xhigh, "
             "and without a model policy-unsupported")
    else:
        failures.append(f"  ✗ effort spelled             {table} {bare_cursor}")

    # --- gemini refuses the effort by its name ---------------------------------------------------------
    unspelled = refusal_of(lambda: compose("gemini", policy={"effort": "high", "model": "m"}))
    if unspelled.startswith("policy-unsupported") and "gemini" in unspelled and "effort" in unspelled:
        held("gemini refuses the effort by its name", "policy-unsupported naming gemini and effort -- no flag "
             "carries it")
    else:
        failures.append(f"  ✗ gemini effort              {unspelled}")

    # --- la-politique-du-lancement (rework A): a long prompt leaves by stdin, whole -----------------------
    long_prompt = "▌ pp · run abc123\n" + ("a line of the boot, served whole in the prompt\n" * 4300)
    longest = {}
    for provider in ("claude", "codex", "gemini", "cursor"):
        try:
            argv, _, text = adapters.launch(provider, ws, made, long_prompt)
            longest[provider] = (text == long_prompt, max(len(one.encode("utf-8")) for one in argv))
        except Exception as raised:                       # noqa: BLE001 -- said in the failure line
            longest[provider] = (f"{type(raised).__name__}: {raised}", 0)
    if (len(long_prompt) > 200000
            and all(whole is True and widest < 131072 for whole, widest in longest.values())):
        held("a long prompt leaves by stdin, whole", f"{len(long_prompt)} characters: stdin carries them at the "
             f"four, the widest element of argv is {max(widest for _, widest in longest.values())} bytes, under "
             "the 131 072 one argument may hold")
    else:
        failures.append(f"  ✗ long prompt on stdin       {len(long_prompt)} {longest}")

    # --- an adapter of the former shape refuses by its name --------------------------------------------
    former = witness.parent.parent / "former" / "wire.py"
    former.parent.mkdir(parents=True)
    former.write_text("def wire(workspace, meta):\n    return []\n\n\n"
                      "def launch(workspace, meta, marble, prompt, wiring=None, policy=None, session=None):\n"
                      "    return ['former', prompt], {}\n", encoding="utf-8")
    malformed = refusal_of(lambda: compose("former", root=witness.parent.parent))
    if malformed.startswith("launch-malformed") and "former" in malformed:
        held("an adapter of the former shape refuses", "a launch that renders two elements: launch-malformed "
             "naming the adapter -- (argv, env, stdin) is the one shape")
    else:
        failures.append(f"  ✗ launch-malformed           {malformed}")

    # --- the marble of the mode reaches the provider's channel -------------------------------------------
    common = sys_dir / "system.common.md"
    common_composition = sys_dir / "system.common.gemini.md"
    stood = common.is_file()                          # compiled by the build since beta.56
    claude_common = composed("claude", marble=common)[0]
    gemini_plain = composed("gemini", marble=common)[1]
    common_composition.write_text("# baseline\n\n# the common marble\n", encoding="utf-8")
    try:
        gemini_composed = composed("gemini", marble=common)[1]
    finally:
        common_composition.unlink()
    if (stood and claude_common[claude_common.index("--append-system-prompt-file") + 1] == str(common)
            and "--system-prompt-file" not in claude_common
            and gemini_plain.get("GEMINI_SYSTEM_MD") == str(common)
            and gemini_composed.get("GEMINI_SYSTEM_MD") == str(common_composition)):
        held("the marble of the mode reaches its channel", "claude appends system.common.md; gemini names "
             "system.common.gemini.md once wire() composed it, the file itself before")
    else:
        failures.append(f"  ✗ marble of the mode         stood={stood} {claude_common} {gemini_plain} {gemini_composed}")

    # --- the mark of the principal is in nothing the face composes ---------------------------------------
    leaked = {}
    for provider in ("claude", "codex", "gemini", "cursor"):
        _, env, _ = composed(provider, marble=common, workdir=material)
        leaked[provider] = sorted(key for key in env if key.startswith("PP_") and key not in ("PP_MARBLE", "PP_WORKDIR", "PP_CONSOLE"))
    if all(not keys for keys in leaked.values()):
        held("the mark is in nothing the face composes", "a marble and a material handed: env carries "
             "PP_MARBLE, PP_WORKDIR and PP_CONSOLE at most -- never PP_CONDUCTED_BY_PRINCIPAL")
    else:
        failures.append(f"  ✗ env leaks                  {leaked}")
    return 0
