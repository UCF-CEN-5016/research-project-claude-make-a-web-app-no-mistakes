# AgentSpec

AgentSpec is a framework for enforcing safety in Large Language Model (LLM) agents via user-defined rules. It integrates with LangChain and supports safety enforcement across embodied environments, code execution, and tool-using agents.

## Quick Start

This section is intended for new contributors and artifact evaluators.

### 1. Prerequisites

- Python 3.12+
- Java 17+ (needed for parser regeneration)
- Git

### 2. Create and activate a virtual environment

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

### 3. Install dependencies

Navigate into the `AgentSpec` subdirectory first; all subsequent commands in this guide are run from there.

```bash
cd AgentSpec
pip install -r requirement.txt
```

### 4. Verify installation with smoke tests

These commands are deterministic and were validated locally on a fresh virtual environment.

```bash
python -m unittest src.spec_lang.test_parse
python -c "from src.controlled_agent_excector import initialize_controlled_agent; print('Import OK:', initialize_controlled_agent.__name__)"
python -m py_compile src/demos.py src/controlled_agent_excector.py src/rule.py src/rules/manual/pythonrepl.py src/rules/manual/table.py
```

### 5. Optional: regenerate parser from grammar

Only needed if you edit `src/spec_lang/AgentSpec.g4`.

```bash
java -jar ./src/spec_lang/antlr-4.13.2-complete.jar -Dlanguage=Python3 ./src/spec_lang/AgentSpec.g4
```

### 6. Optional: run the provided shell script

The repository ships a shell script at `src/run.sh`. If you want to use it, invoke it with its actual path:

```bash
bash ./src/run.sh
```

## Reproducing Results

For step-by-step artifact reproduction, see [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

That document includes:

- complete setup flow,
- exact commands for provided result artifacts,
- known assumptions and credential requirements,
- limitations for full end-to-end reruns.

## Usage with LangChain

Run the following from the `AgentSpec/` directory (i.e. after `cd AgentSpec`):

```python
from src.controlled_agent_excector import initialize_controlled_agent
from src.rule import Rule
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o", temperature=0)

example_rule = """rule @check_shell_exec
trigger
  PythonREPL
check
  is_destructive
enforce
  user_inspection
end
"""

rule = Rule.from_text(example_rule)

tool = PythonREPL()
agent = initialize_controlled_agent(
  tools=[tool],
  llm=llm,
  rules=[rule],
)

response = agent.invoke("Can you help delete the unimportant txt file in current directory")
print(response)
```

Notes:

- `OPENAI_API_KEY` is required for OpenAI-backed examples.
- `user_inspection` prompts on stdin by default.

## Customizing AgentSpec Rules

1. Match the rule event name to the actual tool name.
2. Implement a predicate function with `(user_input, tool_input, intermediate_steps)`.
3. Register the predicate in `src/rules/manual/table.py`.
4. Use one enforcement strategy: `stop`, `user_inspection`, or `llm_self_reflect`.

## Known Limitations

- Some benchmark-generation/evaluation scripts require external datasets or simulators not bundled in this repository.
- LLM-backed evaluations require API credentials and may incur usage cost.

## Citation

If you found AgentSpec useful, please cite:

```
@misc{wang2025agentspeccustomizableruntimeenforcement,
    title={AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents},
    author={Haoyu Wang and Christopher M. Poskitt and Jun Sun},
    year={2025},
    eprint={2503.18666},
    archivePrefix={arXiv},
    primaryClass={cs.AI},
    url={https://arxiv.org/abs/2503.18666},
}
```

