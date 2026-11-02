# Versions

This copy of Procedural Prompting carries the engine and the packages below.

| component | version |
|---|---|
| engine | 0.2.0-beta.33 |
| kit | 0.2.4 |
| agent | 0.32.4 |
| authoring | 0.2.1 |
| continuity | 0.2.1 |
| daneel | 0.1.2 |
| monitoring | 0.1.4 |
| plan | 0.2.2 |
| steering | 1.2.1 |
| team | 0.46.3 |
| ui | 0.56.3 |

Source: commit ff44b115.

## Changes since the release 0.2.0-beta.18

The release 0.2.0-beta.18 is the tag `PUB-e0.2.0-beta.18-ag0.29.0-au0.2.0-c0.1.4-d0.1.2-k0.2.2-m0.1.4-p0.1.50-s1.0.0-t0.40.2-u0.51.0`, on commit d6145a25 (2026-10-25).

- 2026-11-02 · #169 · engine 0.2.0-beta.33: a space starts again from its own first step, a proof that breaks its form or misses a code is asked again without replaying the document, and the effort presets the conduction -- `hybrid` under `light` and `medium`, `strict` under `full`
- 2026-11-01 · #167 · team 0.46.2: the team's timer knows itself by a token, so it holds under Windows, and a stop no longer leaves a timer behind
- 2026-11-01 · #166 · engine 0.2.0-beta.31: `./pp develop <package>` plays a house package from its own folder -- nothing copied, every file read at the next call; `./pp develop <package> off` copies it back
- 2026-11-01 · #165 · team 0.46.0: one relaunch entry per house -- a value of the user's Run key on Windows, no administrator rights needed, one `@reboot` line elsewhere -- and recurring tasks, `team post … --every`
- 2026-11-01 · #164 · engine 0.2.0-beta.30: a house declares its own packages under its `packages/` folder; `add`, `doctor`, `upgrade` and `remove` play on them, and its agents use them
- 2026-10-31 · #163 · engine 0.2.0-beta.29: a document rewritten while a run plays no longer stops the run -- the run goes on under the document's new laws -- and an ambiguous address is asked again under the verb typed
- 2026-10-31 · #162 · agent 0.32.3, team 0.44.1, ui 0.56.3: the chat answers and stops under Windows -- every child of the agent says its standard input, so none freezes on a pipe its parent reads; one net for the teams -- a timer at every step of `schedule:`, no periodic line in any calendar, and one relaunch entry per team that brings it back at logon (`@reboot` on Linux, the Task Scheduler on Windows), a refusal of the system said to the owner, never a failure
- 2026-10-31 · #161 · engine 0.2.0-beta.28, agent 0.32.2, team 0.43.1: launches and purges under Windows -- a detached launch without a window, the team's timer judged alive by asking the system, a purge that leaves a file another process holds open and says so; the bench keeps its temporary houses on disk
- 2026-10-31 · #160 · an installer for Linux, macOS and Windows -- `install.sh`, `install.ps1` and `pp-install.cmd`: uv installed when missing, the product taken from its folder or from the archive of `main`, the house installed or brought up to date, the post's launcher beside it; played again, it destroys nothing
- 2026-10-31 · #159 · ui 0.56.2: the post on Windows -- each verb launched apart in a hidden console of its own, the post's relaunch waited for so the console keeps the terminal
- 2026-10-30 · #158 · the bench: five scenarios aligned on what the product guarantees -- the preset guard reads the bases' settings, a member's boot without the retired pass, the sharing line and a task's live wake-up read on the journal and on the sequence
- 2026-10-30 · #157 · ui 0.56.0: the Teams tab stays in place while a team works, and each row of a task's sequence says the time since the row before
- 2026-10-30 · #156 · ui 0.55.0, team 0.43.0: the recent tasks first, a task's result shown as markdown, a team deleted from the post
- 2026-10-30 · #155 · team 0.42.0, ui 0.54.0: a team in two files -- its declaration and its intention --, its name free, the contract of its acts in the standing orders, and `team delete`
- 2026-10-29 · #154 · engine 0.2.0-beta.26, plan 0.2.1: a mount can replace the nodes it supersedes (`replaces`), so two batches of one phase no longer add up their laws
- 2026-10-29 · #152 · plan 0.2.0, steering 1.2.0: `pp-plan status` as a list and in `--json`, the PLANS space, the plan's reference served at its first mount only, the skill's fixes; `pp-steering list --key`
- 2026-10-29 · #153 · engine 0.2.0-beta.25: procedures may live in sub-folders of `procs/`, and a deeper mount in the same exchange extends the chain instead of refusing
- 2026-10-29 · #151 · team 0.41.0, agent 0.32.0: the tick's failures fixed -- the reader starts at the launch's exchange, a refusal of the house is no member's fault, the principal's word reaches a suspected member, a schedule in seconds -- and the context gauge measured from the provider's usage
- 2026-10-29 · #150 · ui 0.52.0: fixed zones on the message line and the status row; a reopened tab filled from the catalogue
- 2026-10-29 · #149 · agent 0.30.0: the launcher sets each provider's prompt cap (`PP_PROMPT_CAP`) from the limits its adapter declares
- 2026-10-29 · #148 · the bench: a census of the 25 zones of the conduction and a conduction sector (`tests/conduction/`), every zone crossed by the modelled agent
- 2026-10-29 · #147 · engine 0.2.0-beta.22: at its repair bound a run parks instead of refusing in a loop; the agent's text is called `words` in every block
- 2026-10-28 · #146 · a modelled LLM (`adapters/model/`) and a campaign launcher (`tools/campaign/`) that plays sets of procedures on it or on a real harness and compares their answer sheets; engine 0.2.0-beta.20: a long output is cut only past the provider's cap, and gestures and views play on a held output
- 2026-10-26 · #144 · engine 0.2.0-beta.19: a block asks the agent for nothing it does not need -- no closing outside a call that is due, the call given as a template, two cards (common and conducted), the documents swept within bounds
- 2026-10-26 · #145 · continuity 0.2.0: the agent records an operation whenever the work gives one, by its standing orders -- the step at the end of the turn that asked for it is gone
- 2026-10-26 · #143 · steering 1.1.0: views of the steps -- a board with counts and durations, labels, filters, several changes applied at once, and `./pp steering` to read them
