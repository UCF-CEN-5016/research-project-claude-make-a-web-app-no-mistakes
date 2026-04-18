# Reproducibility Guide

This document provides concrete steps to reproduce key artifact checks and result summaries from this repository without requiring insider knowledge.

## Scope

This guide covers:

- environment setup and dependency installation,
- executable smoke checks for the AgentSpec runtime,
- reproduction of packaged result summaries under `expres/`.

This guide does not claim full from-scratch regeneration of every paper result because some pipelines require external datasets, simulator assets, and API credentials not fully bundled in this repository.

## Prerequisites

- Python 3.12+
- Java 17+
- Git

## Step 1: Clone and enter the repository

```bash
git clone <repo-url>
cd AgentSpec-CEN5016
cd AgentSpec
```

All subsequent commands in this guide are run from the `AgentSpec/` subdirectory.

## Step 2: Create a clean virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Step 3: Install dependencies

```bash
pip install -U pip
pip install -r requirement.txt
```

## Step 4: Reproduce core artifact checks

### 4.1 Parser unit tests

```bash
python -m unittest src.spec_lang.test_parse
```

Expected outcome: test suite passes (`OK`).

### 4.2 Controlled-agent import smoke check

```bash
python -c "from src.controlled_agent_excector import initialize_controlled_agent; print('Import OK:', initialize_controlled_agent.__name__)"
```

Expected outcome: prints `Import OK: initialize_controlled_agent`.

### 4.3 Bytecode compilation smoke check

```bash
python -m py_compile src/demos.py src/controlled_agent_excector.py src/rule.py src/rules/manual/pythonrepl.py src/rules/manual/table.py
```

Expected outcome: no errors (warnings may appear from regex escape sequences).

### 4.4 Parser regeneration check

```bash
java -jar ./src/spec_lang/antlr-4.13.2-complete.jar -Dlanguage=Python3 ./src/spec_lang/AgentSpec.g4
```

Expected outcome: command exits successfully and generated parser files are updated.

## Step 5: Reproduce packaged experiment summaries

The repository includes pre-generated result files in `expres/` that can be re-analyzed deterministically.

### 5.1 Embodied summary

```bash
cd expres/embodied
python analyze.py
cd ../..
```

Expected outcome: prints aggregated rates. Example output pattern:

- category lines ending with `: <rate>, <count>`
- final overall value line

### 5.2 ToolEmu file-level summary

```bash
python -c "from pathlib import Path; p=Path('expres/toolemu/gpt4o-no_controll_eval_agent_safe.jsonl'); print('toolemu safe lines:', sum(1 for _ in p.open('r', encoding='utf-8')))"
```

Expected outcome: prints a positive record count (for the current artifact, `134`).

## Optional: Run the provided shell script

The repository ships `src/run.sh`. To use it:

```bash
bash ./src/run.sh
```

## Credentials and External Requirements

- `OPENAI_API_KEY` is required for OpenAI-backed demo/evaluation paths.
- `expres/embodied/detail_evaluate.py` uses OpenAI calls and AI2-THOR simulator runtime.
- Some generation/evaluation scripts in `src/rules/llm/` reference benchmark datasets outside this repository (for example under `benchmarks/.../dataset/...`).

## Known Limitations and Assumptions

- Full regeneration of all paper-level metrics may require external benchmark assets not distributed here.
- LLM-backed outcomes are partially non-deterministic and sensitive to model version, API behavior, and rate limits.
- If your shell is PowerShell, prefer direct `python ...` commands over Bash heredoc syntax (`<<'PY'`).

## Verification Status for This Guide

Commands in this file were verified to execute on a fresh local virtual environment on Windows (PowerShell) on 2026-04-14, except steps explicitly marked as requiring external credentials/assets.