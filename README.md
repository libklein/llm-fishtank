# llm-fishtank

[![Release](https://img.shields.io/github/v/release/libklein/llm-fishtank)](https://img.shields.io/github/v/release/libklein/llm-fishtank)
[![Build status](https://img.shields.io/github/actions/workflow/status/libklein/llm-fishtank/main.yml?branch=main)](https://github.com/libklein/llm-fishtank/actions/workflows/main.yml?query=branch%3Amain)
[![codecov](https://codecov.io/gh/libklein/llm-fishtank/branch/main/graph/badge.svg)](https://codecov.io/gh/libklein/llm-fishtank)
[![Commit activity](https://img.shields.io/github/commit-activity/m/libklein/llm-fishtank)](https://img.shields.io/github/commit-activity/m/libklein/llm-fishtank)
[![License](https://img.shields.io/github/license/libklein/llm-fishtank)](https://img.shields.io/github/license/libklein/llm-fishtank)

The modern fishtank: Observe LLMs playing conversational games.

- **Github repository**: <https://github.com/libklein/llm-fishtank/>

## Usage

1. Clone the repository
2. Create a virtual environment

```bash
uv venv
```

3. Run the main command

```bash
uv run llm-fishtank
```

Each subcommand corresponds to a game.

### CrossClues

```bash
uv run llm-fishtank cross-clues play "Donald Trump" "Hilary Clinton" "Bruce Springsteen" "Arnold Schwarzenegger" --api-key="<your api key>" --llm-endpoint="<openai compatible endpoint>"
```
