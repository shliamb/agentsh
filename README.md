<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/status-early%20MVP-orange?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/LiteLLM-multi--provider-1F6FEB?style=flat-square" alt="LiteLLM">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/github/stars/shliamb/agentsh?style=flat-square&color=yellow&cacheSeconds=3600" alt="Stars">
  <img src="https://img.shields.io/github/last-commit/shliamb/agentsh?style=flat-square&cacheSeconds=3600" alt="Last commit">
  <img src="https://img.shields.io/github/issues/shliamb/agentsh?style=flat-square" alt="Issues">
</p>

# Agent Shell

A minimal, layered terminal agent. Built for personal use, opened because others might find the architecture useful.

**Status: early MVP.** Bootstrap, config, logging and i18n are working. The agent loop, tools and policy engine are in progress.

---

## What it is

Agent Shell (`agentsh`) is a CLI tool that runs an LLM agent inside your terminal, in your project folder, with your rules. It is not trying to compete with Claude Code or Cursor. It is a small, transparent, hackable alternative — built layer by layer, easy to understand, easy to modify.

Design principles:

- **Layered.** Every concern lives in its own layer with a clear boundary. No magic.
- **Local-first.** No Docker, no services, no cloud. A Python process and some files.
- **Provider-agnostic.** Any LLM through LiteLLM. Cheap models first, expensive on demand.
- **Transparent.** You see every command the agent wants to run, before it runs it.
- **Minimal dependencies.** Stdlib where possible.

---

## Architecture

Inspired by Claude Code's decomposition, but drastically simplified.

| Layer | Responsibility | Status |
|-------|----------------|--------|
| L0 | Bootstrap — project detection, config, i18n, logging | ✅ done |
| L1 | Transport — stdin/stdout (later: Telegram, web) | ⏳ planned |
| L2 | Core Loop — context → LLM → tool calls → results | ⏳ planned |
| L3 | Tools — `run_command`, `ask_user` (minimal set) | ⏳ planned |
| L4 | Policy — allow/deny every tool call | ⏳ planned |
| L5 | Secret Broker — inject secrets, never expose them | ⏳ planned |
| L6 | Context Manager — trimming, compaction | ⏳ planned |
| L7 | Memory — project notes in markdown, grep-searchable | ⏳ planned |
| L8 | Model Router — cheap vs expensive per task | ⏳ planned |
| L9 | Orchestration — sub-agents | ⏳ planned |

Each layer talks only to its neighbors through a defined interface. Every layer can be replaced or rewritten independently.

---

## Install

Requirements: Python 3.10+, Linux/macOS.

```bash
git clone https://github.com/<you>/agentsh.git
cd agentsh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Add the CLI wrapper:

```bash
cat > ~/.local/bin/agentsh << 'EOF'
#!/bin/bash
python3 /path/to/agentsh/agentshell/main.py "$@"
EOF
chmod +x ~/.local/bin/agentsh
```

Make sure `~/.local/bin` is in your `PATH`.

---

## Usage

```bash
cd ~/my-project
agentsh init            # create .agentshell/ skeleton
agentsh                 # run the agent (placeholder for now)
agentsh --lang ru       # override language for this run
agentsh --version
```

Project files:

```
.agentshell/
├── config.json     # project settings (model, lang, limits)
├── CLAUDE.md       # instructions for the agent (project rules)
├── MEMORY.md       # index of memory notes
├── memory/         # long-form notes, loaded on demand
└── logs/
    └── agent.log   # everything the agent did
```

Global config lives in `~/.agentshell/config.json` and is merged underneath the project config (project wins).

---

## Roadmap

- [x] Bootstrap: project detection, config, i18n, logging
- [ ] L1 Transport: interactive CLI loop
- [ ] L3 Tools: `run_command` with smart output trimming, `ask_user`
- [ ] L4 Policy: regex + argv-based command filter
- [ ] L2 Core Loop: LLM → tools → context
- [ ] L5 Secret Broker: inject credentials without exposing them
- [ ] L6 Context Manager: hard trimmer, then smarter compaction
- [ ] L7 Memory: markdown notes + grep
- [ ] L8 Model Router
- [ ] L9 Sub-agents

---

## Non-goals

- Replacing Claude Code.
- Supporting every LLM feature.
- Being production-grade for teams.
- Enterprise anything.

---

## Contributing

Issues and PRs welcome, but this is a personal tool first. If something doesn't fit the design philosophy (minimal, layered, transparent), it probably won't get merged.

---

## License

MIT (or whatever you pick).

---

## По-русски

Agent Shell — минимальный слоистый терминальный агент. Сделан для личного использования, открыт, потому что архитектура может быть кому-то полезна.

**Статус: ранний MVP.** Работают Bootstrap, конфиг, логирование, i18n. Цикл агента, инструменты и Policy Engine — в разработке.

Принципы:
- **Слоистость.** Каждая задача — в своём слое с чёткой границей.
- **Local-first.** Без Docker, без сервисов. Python-процесс и файлы.
- **Любая модель.** Через LiteLLM. Дешёвые по умолчанию, дорогие — по требованию.
- **Прозрачность.** Ты видишь каждую команду до её выполнения.
- **Минимум зависимостей.** Stdlib, где возможно.

Установка, использование и roadmap — см. выше.
