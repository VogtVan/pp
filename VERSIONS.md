# Versions

This copy of Procedural Prompting carries the engine and the packages below.

| component | version |
|---|---|
| engine | 0.1.0-beta.66 |
| kit | 0.1.113 |
| agent | 0.24.1 |
| authoring | 0.1.19 |
| continuity | 0.1.4 |
| daneel | 0.1.1 |
| monitoring | 0.1.4 |
| plan | 0.1.47 |
| steering | 0.7.6 |
| team | 0.32.2 |
| ui | 0.39.0 |

Source: commit bf6f2763.

The packages doc, federation and improvement are not published for now.

## Changes since the previous publication

The previous publication is the tag `PUB-e0.1.0-beta.14-a0.1.12-c0.1.0-d0.1.0-k0.1.107-m0.1.0-p0.1.40-s0.7.3`, on commit 966643ea (2026-09-23).

- 2026-10-12 · #104 · tests: the ui body test keeps README_INTERNAL.md (plan publication)
- 2026-10-12 · #103 · ui: the season and the pause on the real verbs of team (plan ui, les-equipes, le-reel-de-la-saison)
- 2026-10-12 · #102 · ui: the launch profile, the season, the tasks alive, the state and the pause of a team, the thin lines (merge of #101, plan ui)
- 2026-10-12 · Merge branch 'master' of https://git.sw7.local/sw7/procedural-prompting
- 2026-10-11 · #99 · ui: the two tabs of the teams, the footer and the overlays, a task's text and last event, the steps of a task, the weight and the purge, the zone of the chat, the following of the teams, a team born from a template (plan ui)
- 2026-10-11 · #98 · agent: exchanges pairs each response with the message it answers (plan agent, le-chat, l-appariement-des-echanges)
- 2026-10-11 · #97 · agent: the budget cap of a run, the grammar of a --harness, the bench through the providers' abstraction, purge, the kept flow, the team's budget, the weight of a run, the task's name, the team templates, a run named as typed, the declaration read (pla…
- 2026-10-11 · #96 · engine: one seam for what the engine serves (beta.65) and ./pp -purge (beta.66) (plan core: la-conduction-au-prompt la-remise rework, l-etat la-purge)
- 2026-10-10 · #95 · team faces in --json, the Teams tab of the post and the thread of a task, read only (plan ui, les-faces + les-equipes)
- 2026-10-10 · #94 · team: a task taken back, a ceremony rung at hand and its quorum (plan agent, la-communication)
- 2026-10-10 · #93 · team: an ask to any member, a reply answers an ask, team reset (plan agent, la-communication, le-tick)
- 2026-10-10 · #92 · agent and team: a team plays from its directory -- --documents, teams/<name>/ (plan agent, la-communication)
- 2026-10-10 · #91 · engine: a launcher gives a run a root of documents -- PP_DOCUMENTS, beta.64 (plan core, l-etat)
- 2026-10-10 · #90 · ui: the list of a line floats as a Select's -- ▼, the whole list on an exact name (plan ui, le-dialogue)
- 2026-10-10 · #89 · ui: the date of the runs, EventScreen straight, model and effort that list; the packages editor and a message line on several lines (plan ui, le-dialogue)
- 2026-10-10 · #88 · agent: a switch of a package waits until the run can take it (plan agent, le-chat)
- 2026-10-09 · #87 · ui: the run known at the opening; a stop button (plan ui, le-dialogue)
- 2026-10-09 · #86 · agent: the run said before any message -- `ready` opens the flow (plan agent, le-chat)
- 2026-10-09 · #85 · ui: one run, one tab; overlays that hold; a post read at a glance; lines that say whether they open (plan ui, le-dialogue)
- 2026-10-09 · #84 · agent: the interruption said to the model; the calls of a launch in their own scenario; team: the grammar of a wake-up (plan agent)
- 2026-10-09 · #83 · ui: the calls of a launch in the transcript (plan ui, le-dialogue, les-appels-d-outils)
- 2026-10-09 · #82 · agent: the calls of a launch on the flow (plan agent, le-chat, les-appels-au-flux)
- 2026-10-09 · #81 · engine and adapters: the third face of the harness, events (plan core, le-packaging, les-evenements-du-harnais)
- 2026-10-09 · #80 · agent and ui: the lines of the events (plan ui, le-dialogue, les-lignes-d-evenement)
- 2026-10-08 · #79 · engine, agent and ui: the floor of a principal's cap; the house as an agent, the themes, the regime of a run (plan ui, les-faces, le-plancher-du-mode-principal and la-maison-et-ses-themes)
- 2026-10-08 · #78 · agent and ui: the returns of the real -- a resume keeps the run, the theme, the overlays (plan ui, le-dialogue, les-retours-du-reel)
- 2026-10-08 · #77 · tests: a tolerance of 10 % on the scenario target (plan core, le-banc, les-scenarios-par-maison, rework)
- 2026-10-08 · #76 · ui and agent: the post without a hub, the turn under way, the transcript as blocks, the parameters of a run, the suspension by the agent -- engine beta.61, kit 0.1.113, ui 0.8.0, agent 0.9.0 (plan ui, le-dialogue)
- 2026-10-08 · #75 · ui: the post at the real of the bench -- ui-dialogue-real on the real verb and faces, the flags after -- carried to every conversation; ui 0.4.1 (plan ui, le-dialogue, la-conversation-au-reel-du-banc, last batch)
- 2026-10-08 · #74 · ui: the hub of the post -- the runs of every agent from the faces, resume with history, name for good, statistics; ui 0.4.0 (plan ui, le-dialogue, l-onglet-conversations)
- 2026-10-08 · #73 · agent: the faces of the agents -- list/status --json, name (names.jsonl), exchanges, stats relaying -stats; agent 0.7.0 (plan ui, les-faces, les-runs-nommes)
- 2026-10-08 · #72 · ui: the post of conversations, with tabs -- one tab per conversation on its own task, the hub, n/x/r and ctrl+arrows, the openings on the app's loop before it draws; ui 0.3.0 (plan ui, le-dialogue, le-poste-a-onglets)
- 2026-10-08 · #71 · ui: the face of a conversation -- model/dialogue.py, faces/chat.py Conversation (the verb held, a reader thread, send/stop/quit), the witness pp-chat; ui-chat-face on the real agent chat --json (plan ui, le-dialogue)
- 2026-10-07 · #70 · agent: the flow of a conversation -- chat --json, commands on stdin and events on stdout each naming its voice (principal, conduction, agent, step…); agent 0.6.0
- 2026-10-07 · #69 · ui: the frame and the palette -- THEME_CSS in palette.py, the least size 40x8, --press on --render, the panes' text, ui-frame at two sizes; ui 0.1.1 (plan ui, le-socle, last batch)
- 2026-10-07 · #68 · ui: the package and its launcher -- ui 0.1.0, ./pp ui at the terminal, pp-ui.py re-executed under uv with Textual 8.2.8 inline, the frame of the cockpit, --render as text; ui-launch 7 cases (plan ui, le-socle)
- 2026-10-07 · #67 · agent: a conversation with an agent -- chat <path> [--run <key>], one run from a message to the next; exchange() extracted from run (run unchanged to the byte); the harness ended on SIGINT; the verb at the terminal (agent 0.5.0)
- 2026-10-07 · #66 · ui: a package command at the terminal -- tty: true on commands hands the skill the console's three streams (run_at_terminal), strict boolean at the build; contributions.py +2, console/command-at-terminal (plan ui, le-socle)
- 2026-10-07 · #65 · agent: the cap of an agent's outputs written through the engine's settings face -- capped() calls settings.write; settings-at-the-skills green (agent 0.4.1)
- 2026-10-07 · #64 · core: a setting written through the face -- settings.write(meta, key, value), one line of SETTINGS.md rewritten in place or added, judged by of(), the bytes restored on a refusal (beta.60)
- 2026-10-07 · #63 · core: a scenario is one house and one subject -- rule 10, the support module, team-review and agent-home split (the bench's wall from 325 s to 77 s)
- 2026-10-07 · #62 · agent: the wake-up conducted by the house -- the loop of pp-agent, --launches, the cost per launch, the cap at add; team without a run-less answer (agent 0.4.0, team 0.14.0)
- 2026-10-07 · #61 · plan: the material of a plan's nodes -- the verb material, the birth, the serve reminder, check (0.1.47)
- 2026-10-07 · #60 · agent: the prompt on stdin at the four adapters, the marble of the mode (beta.59, agent 0.3.4)
- 2026-10-07 · #58 · kit: the turn in its two channels -- SYSTEM.COMMON and SYSTEM.CONDUCT (0.1.112)
- 2026-10-07 · #57 · core: the conduction's baseline, the run's mode, a marble per mode, two files per section, the bench's stand-in base and its two last sectors sorted, the conduction handed to the principal, the material of a reading (beta.53-beta.58)
- 2026-10-06 · #59 · plan: the test policy as recommendations, a law leaves on the principal's word alone (0.1.45-0.1.46)
- 2026-10-04 · #56 · agent, team: no reading gives pp an order, a refused resume leaves its run as it was (agent 0.3.3, team 0.13.5)
- 2026-10-04 · #55 · team: a member's one run, one wake-up at a time (team 0.13.1)
- 2026-10-04 · #54 · core: the proof's way out and its coverage (beta.51, beta.52)
- 2026-10-04 · #52 · team: a team's members, a name and a path -- one birth per path (team 0.13.0, agent 0.3.2)
- 2026-10-04 · #53 · core: an upgrade renews the runs, the key kept (beta.50)
- 2026-10-04 · #51 · team: an agent's tasks in parallel, a lost run reopened (team 0.12.0)
- 2026-10-03 · #50 · agent: the model's effort in the launch policy (beta.49, agent 0.2.3, team 0.10.4)
- 2026-10-03 · #49 · core: the machine's maintenance lock, readers/writer; a key reserved by its slot (beta.47-48)
- 2026-10-03 · #48 · core: an instance borrows the machine above it (beta.46)
- 2026-10-03 · #47 · core: the store withdrawn (beta.45)
- 2026-10-02 · #46 · agent: l-equipe-au-reel -- the answer of a team wake-up is a conducted production (team 0.10.0)
- 2026-10-02 · #45 · agent: la-communication -- the run's call lock (beta.38), what is due once and the shared writers (beta.39)
- 2026-10-01 · #44 · core: the store immutable, indexed and pruned (beta.37)
- 2026-09-30 · #43 · core: the switch sees every mount address, a gone mount says so (beta.36)
- 2026-09-27 · #42 · agent: the wake-up followed (beta.35, agent 0.1.5)
- 2026-09-27 · #41 · agent: the result at the output (agent 0.1.4)
- 2026-09-27 · #40 · agent: the permission regime in the policy (beta.34, agent 0.1.3)
- 2026-09-27 · #39 · core: the mount by address (beta.33)
- 2026-09-27 · #38 · agent: the key before the launch (agent 0.1.2)
- 2026-09-27 · #37 · core: the key given by the caller (beta.32)
- 2026-09-27 · #36 · agent: the resume in the provider's session (agent 0.1.1)
- 2026-09-27 · #35 · core: the provider's session and the response channel (beta.30, beta.31)
- 2026-09-27 · #34 · agent: the withdrawal of kit-agent -- bases/ carries the kit alone; the sink-on-the-store proof moves to a witness package (beta.29)
- 2026-09-27 · #33 · core: one entry, one table -- ENTRIES and _enter, the socket's laws proven at the turn's checkpoint (beta.28)
- 2026-09-27 · #32 · agent: the policy of the launch -- `launch(…, wiring, policy)` judges the model and the budget once at the face and each adapter spells or refuses them (beta.26)
- 2026-09-26 · #31 · core: the message at the opening -- `./pp -new [<message>]` and the reprise trace `prompt` at any tuning, `capture_prompt` leaves the protocol for the kit's fragment (beta.25)
- 2026-09-26 · #30 · agent: the harness abstraction -- conductor.adapters composes the non-interactive command line per provider, launch() in the four adapters (beta.24)
- 2026-09-26 · #29 · agent: the bases under one roof -- kit and kit-agent move to bases/ (beta.23)
- 2026-09-26 · #28 · agent: the base applies its own -- MEMBER.md to kit/user/, the engine's template seeds the protocol alone (beta.21, kit 0.1.109)
- 2026-09-26 · #27 · agent: the engine renders its own diagnostics, says the principal, drops the siblings from its facade, lets the console address an instance and name its base, and keeps the machine on a store (beta.16-20)
- 2026-09-26 · #26 · agent: the marble and the card descend to the engine (beta.15, kit 0.1.108)
- 2026-09-26 · #25 · authoring: the theory says the principal (0.1.13)
