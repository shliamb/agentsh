# Project Progress (Shared)

## Project Facts

**Project:** `agentsh` — a personal terminal LLM agent (~1.5k lines of Python, LiteLLM, four layers L0–L3). Not a DSH plugin; a standalone CLI repo.

**Repository:** `git@github.com:shliamb/agentsh.git`, branch `main`. Local checkout: `/home/alex/Desktop/data/programs/agentsh`.

**Status:** FROZEN as of 2026-10-24. The core works end to end; no further development is planned. The README documents the freeze, the unfixed security gaps, and what was left on the roadmap.

**What works:** bootstrap (`init` / `run`, project detection, config merge, file logger), terminal transport (`/help`, `/clear`, `/exit`, Ctrl+C), LiteLLM loop with tool calls, `run_command` with `cwd` pinned to the project root and a 30 s timeout, regex policy (ALLOW/DENY/ASK), rendering of every tool call and its result (bounded for the screen), iteration budget with an `ask()` confirmation prompt.

**Known gaps (designed, not implemented):** confirmation gate for commands (they run immediately unless a regex denies), secret broker and output redaction, context manager (`fit` / `bound`), memory tools, output bounding for the model, streaming, typed errors instead of a synthetic response, tool registry inside L3.

**Security posture:** unsafe for untrusted repositories. `~/.agentshell/.env` is loaded into the process and readable by any command; the policy is a 7-rule regex denylist, not a sandbox.

**Layout:** `agentshell/{bootstrap,transport,core,tools,tools/subsystems}` map to L0–L3; `main.py` is wiring only.

**Install:** `./install.sh` creates `.venv/` at the repo root and wrappers `~/.local/bin/{agentsh,agentshell}`. Keys via `agentshell setup-keys` → `~/.agentshell/.env`.

## Progress Timeline



## 2026-10-24 22:49 · Session session- · Manual update

2026-10-24 — Project frozen and documented as such.

Done this session (uncommitted in the working tree):
- README rewritten for the four-layer architecture (L0 bootstrap, L1 transport, L2 core, L3 tools + subsystems), with the L2→L3 cycle, the `ask()` human-in-the-loop channel, and per-layer boundaries.
- Fixed `agentshell init` (logger created `.agentshell/logs/` before the "already exists" check) and `setup-keys` (`sys.path` insert after import). `~/.agentshell` is no longer mistaken for a project root.
- Policy moved to `tools/subsystems/`; dead `TrafficRouter` removed; `__init__.py` added.
- Tool calls and results are now rendered in the terminal before/after execution, bounded for the screen.
- `run_command` pins `cwd` to the project root; iteration budget asks the human via `ask()` before running away.

Decision: freeze. The core works end to end but is unguarded (no confirmation gate, no secret broker, `.env` readable by any command) and does not beat existing agents. README now opens with a frozen-status block, the security section states plainly what is not protected, and the roadmap is kept as a record of what was designed vs written.

Next step if ever resumed: wire the Policy `ASK` decision to `ask()` — the single change that moves it from a demo into a tool you can leave running.
