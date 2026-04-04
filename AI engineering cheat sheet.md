## AI engineering cheat sheet

### Foundation

* [ ] **Use Codex to build the software, but use the Responses API to build the AI product.** For new app development, Responses is the recommended API primitive and already includes built-in agentic tools, MCP support, and multi-turn state. ([OpenAI Developers][3])
* [ ] **Default to `gpt-5.4`; use `gpt-5.4-mini` for cheap/light subtasks.** OpenAI’s current guidance is to start with `gpt-5.4` for most Codex work; use mini for lighter tasks or helper agents. ([OpenAI Developers][4])
* [ ] **Keep one small `AGENTS.md` in the repo root.** Put only the things Codex should always know: repo map, commands, invariants, review rules, and non-negotiable constraints. Keep it small; Codex has a default 32 KiB project-doc cap. ([OpenAI Developers][5])
* [ ] **Create deterministic scripts before serious prompting.** At minimum: `setup`, `dev`, `test`, `lint`, `typecheck`, `eval`. Current best practice is to let scripts do the deterministic work and the model do the contextual work. ([OpenAI Developers][6])

### Execution loop

* [ ] **Start every feature with a short plan and acceptance checks.** Current agent guidance strongly favors planning before coding; the agent loop is plan → edit → run tools → observe → repair → repeat. ([OpenAI Developers][7])
* [ ] **Give the agent verifiable goals, not vibes.** Typed schemas, tests, linters, and explicit success conditions are more important than fancy prompts. ([Cursor][8])
* [ ] **Use sandboxed/on-request permissions by default.** Tight approvals are still the sane default; full autonomy without guardrails creates real failure modes. OpenAI documents `on-request`/granular approvals, and Anthropic explicitly calls out approval fatigue and incidents from overeager agents. ([OpenAI Developers][9])
* [ ] **Review every non-trivial diff.** Codex now supports `/review`, and OpenAI says Codex should test, check, and review code—not just generate it. ([OpenAI Developers][10])
* [ ] **When the agent repeats a mistake twice, fix the repo, not the conversation.** Add the correction to `AGENTS.md` or a skill so the behavior persists. ([OpenAI Developers][11])

### Add complexity only when earned

* [ ] **Create a skill only after a workflow repeats.** Skills are now a first-class Codex feature and are best for reusable workflows with a clear trigger, concise instructions, optional scripts, and references. ([OpenAI Developers][1])
* [ ] **Use subagents only for parallel research, review, or context isolation.** They are useful when they preserve the main context or let you parallelize exploration; they are not mandatory for normal feature work. ([OpenAI Developers][12])
* [ ] **Use MCP only when the project repeatedly needs outside systems.** Good use case: docs, ticketing, data stores, internal APIs. Bad use case: adding ceremony before you know what external access is actually needed. Codex customization treats MCP as an external-system layer, not the starting point. ([OpenAI Developers][11])
* [ ] **Use plugins only for sharing stable workflows across repos or teammates.** Plugins are real now, but they are a packaging/distribution step, not an MVP requirement. ([OpenAI Developers][13])
* [ ] **Be skeptical of hooks for now.** Hooks exist, but they are still experimental, and Windows support is temporarily disabled. Use them later for deterministic lifecycle actions, not as the backbone of your process. ([OpenAI Developers][14])

### Reliability

* [ ] **Add evals from day 1.** The modern pattern is eval-driven development: prompt/task → captured run/trace/artifacts → checks → score. Treat them like lightweight end-to-end tests. ([OpenAI Developers][15])
* [ ] **Treat context as scarce.** The cutting-edge advice is to pass the smallest set of high-signal tokens possible, load details just in time, and avoid bloated instruction files. ([OpenAI Developers][1])
* [ ] **Add tracing/guardrails once the app becomes multi-step or tool-using.** Current agent guidance increasingly treats tracing, policy enforcement, and guardrails as production requirements rather than extras. ([OpenAI Developers][16])

### Don’t do this

* [ ] **Do not start by building a big multi-agent harness.** Both OpenAI and Anthropic now emphasize the harness/agent loop, but the practical lesson is to keep it simple first and add orchestration only when a single-agent loop stops being enough. ([OpenAI][17])
* [ ] **Do not build on deprecated primitives.** For new apps, prefer Responses over Chat Completions; custom prompts are deprecated in favor of skills; Assistants API is on a deprecation path. ([OpenAI Developers][3])
* [ ] **Do not confuse bigger context or more agents with better engineering.** Current frontier guidance is explicitly moving toward tighter context engineering and verifiable loops, not prompt bloat. ([Anthropic][18])

## New project first steps

1. Write a one-page spec with scope, non-goals, acceptance tests.
2. Set up repo scripts plus a small `AGENTS.md`.
3. Build one working vertical slice with one agent loop.
4. Add evals.
5. Only then add one skill for the first repeated workflow.
6. Only then consider subagents, MCP, or plugins.

That is the 2026 practical path: **small context, strong scripts, evals early, controlled autonomy, reusable workflows only after repetition**. ([OpenAI Developers][11])

[1]: https://developers.openai.com/codex/skills/ "Agent Skills – Codex | OpenAI Developers"
[2]: https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide/ "Codex Prompting Guide"
[3]: https://developers.openai.com/api/docs/guides/migrate-to-responses/ "Migrate to the Responses API | OpenAI API"
[4]: https://developers.openai.com/codex/models/ "Models – Codex | OpenAI Developers"
[5]: https://developers.openai.com/codex/guides/agents-md/ "Custom instructions with AGENTS.md – Codex | OpenAI Developers"
[6]: https://developers.openai.com/blog/skills-agents-sdk/ "Using skills to accelerate OSS maintenance | OpenAI Developers"
[7]: https://developers.openai.com/blog/run-long-horizon-tasks-with-codex/?utm_source=chatgpt.com "Run long horizon tasks with Codex"
[8]: https://cursor.com/blog/agent-best-practices "Best practices for coding with agents · Cursor"
[9]: https://developers.openai.com/codex/config-reference/ "Configuration Reference – Codex | OpenAI Developers"
[10]: https://developers.openai.com/codex/learn/best-practices/ "Best practices – Codex | OpenAI Developers"
[11]: https://developers.openai.com/codex/concepts/customization/ "Customization – Codex | OpenAI Developers"
[12]: https://developers.openai.com/codex/subagents/ "Subagents – Codex | OpenAI Developers"
[13]: https://developers.openai.com/codex/changelog/ "Changelog – Codex | OpenAI Developers"
[14]: https://developers.openai.com/codex/hooks/ "Hooks – Codex | OpenAI Developers"
[15]: https://developers.openai.com/blog/eval-skills/ "Testing Agent Skills Systematically with Evals | OpenAI Developers"
[16]: https://developers.openai.com/api/docs/guides/agents-sdk/ "Agents SDK | OpenAI API"
[17]: https://openai.com/index/unrolling-the-codex-agent-loop/ "Unrolling the Codex agent loop | OpenAI"
[18]: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents "Effective context engineering for AI agents \ Anthropic"
