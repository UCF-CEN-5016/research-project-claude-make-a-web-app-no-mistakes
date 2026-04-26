# Reproducibility Guide

This guide is for researchers and new contributors who want a clear, step-by-step way to:

1. install dependencies,
2. execute the artifact,
3. reproduce packaged result summaries.

All commands below assume you run from the repository root.

## Scope

This repository provides two reproducible paths:

- runtime and parser checks through Python commands and run.sh,
- deterministic analysis of packaged outputs in expres/.

Full end-to-end regeneration of all paper-level evaluations may require external APIs, simulator dependencies, or datasets that are not fully bundled in this repository.

## Prerequisites

- Python 3.12+
- Java 17+ (needed for parser regeneration only)
- Git

## 1. Clone The Repository

```bash
git clone <repo-url>
cd AgentSpec-CEN5016
```

## 2. Create And Activate A Virtual Environment

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

## 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirement.txt
```

## 4. Run Core Artifact Checks

### 4.1 Parser Unit Test

```bash
python -m unittest src.spec_lang.test_parse
```

Expected outcome: test run ends with OK.

### 4.2 Bytecode Compilation Smoke Check

```bash
python -m py_compile src/demos.py src/controlled_agent_excector.py src/rule.py src/rules/manual/pythonrepl.py src/rules/manual/table.py
```

Expected outcome: command exits successfully. You may see warnings from regex escape sequences in src/rules/manual/pythonrepl.py.

### 4.3 Regenerate Parser (Optional)

Use this only if you modify the grammar:

```bash
java -jar ./src/spec_lang/antlr-4.13.2-complete.jar -Dlanguage=Python3 ./src/spec_lang/AgentSpec.g4
```

Expected outcome: parser files are regenerated under src/spec_lang/.

## 5. Execute The Artifact Runner

Interactive mode:

```bash
bash run.sh
```

Direct option mode:

```bash
bash run.sh 2
bash run.sh 3
bash run.sh 4
bash run.sh 7
bash run.sh 8
```

Option reference in run.sh:

- 1: LangChain smoke demo (requires OPENAI_API_KEY)
- 2: Parser unit tests
- 3: Parse inline rule with user_inspection
- 4: Parse inline rule with stop
- 5: Controlled agent import smoke
- 6: Predicate registry smoke
- 7: Bytecode compilation smoke
- 8: Regenerate parser
- 9: Full local smoke suite

## 6. Reproduce Packaged Result Summaries

### 6.1 Embodied Summary

```bash
cd expres/embodied
python analyze.py
cd ../..
```

Expected output pattern: category lines and a final overall value.

Validated final value for current artifact snapshot:

```text
0.5426621160409556
```

### 6.2 ToolEmu Sanity Count

```bash
python -c "from pathlib import Path; p=Path('expres/toolemu/gpt4o-no_controll_eval_agent_safe.jsonl'); print('toolemu safe lines:', sum(1 for _ in p.open('r', encoding='utf-8')))"
```

Validated output for current artifact snapshot:

```text
toolemu safe lines: 134
```

## 7. External Requirements And Caveats

- OPENAI_API_KEY is required for API-backed flows (for example run.sh option 1).
- Some evaluation scripts rely on external assets and environment setup beyond this repository.
- On Windows, run.sh should be executed via Bash (Git Bash or WSL).

## Verification Status

The commands in Sections 4.1, 6.1, and 6.2 were validated in this workspace on 2026-04-21.
