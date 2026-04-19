# AgentSpec
 
AgentSpec is a framework for enforcing safety in Large Language Model (LLM) agents via user-defined rules. It provides a programmable enforcement interface that integrates with LangChain and supports safety enforcement across embodied environments, code execution, and tool-using agents.

---

## 🚀 Getting Started

### 1. Installation

```bash
pip install -r requirement.txt
```

A working version:
langchain                                0.3.25
langchain-anthropic                      1.3.0
langchain-classic                        1.0.1
langchain-cli                            0.0.35
langchain-community                      0.4.1
langchain-core                           0.3.81
langchain-experimental                   0.4.1
langchain-openai                         0.3.35
langchain-text-splitters                 0.3.11

### 2. Generate the Parser (Only required if modifying the grammar)

```bash
java -jar ./src/spec_lang/antlr-4.13.2-complete.jar -Dlanguage=Python3 ./src/spec_lang/AgentSpec.g4
```

## Running Experiments

This project provides an interactive script to simplify running test configurations.

### Prerequisites Checked by `run.sh`

- Python available (from `.venv` if present, otherwise system `python`)
- Dependency file exists (`requirement.txt` or `requirements.txt`)
- Required Python modules are importable (antlr4 + langchain stack)

### Numpad Key Mapping

| Key | Test Configuration | What it runs |
|---|---|---|
| 1 | LangChain smoke demo | `python -m src.spec_lang.demo_langchain_working` |
| 2 | Parser unit tests | `python -m unittest src.spec_lang.test_parse` |
| 3 | Inline parse: user inspection | Parses a `user_inspection` inline rule |
| 4 | Inline parse: stop | Parses a `stop` inline rule |
| 5 | Controlled agent import smoke | Imports `initialize_controlled_agent` |
| 6 | Predicate registry smoke | Confirms `is_destructive` is registered |
| 7 | Bytecode compile smoke | Compiles key runtime files |
| 8 | Regenerate parser | Runs ANTLR on `src/spec_lang/AgentSpec.g4` |
| 9 | Full local smoke suite | Runs tests 2, 5, 6, and 7 |
| 0 | Exit | Leaves the interactive menu |

### How to Run

```bash
# Linux / Mac
chmod +x run.sh
./run.sh

# Windows (Git Bash / WSL)
bash run.sh

# Windows (CMD / PowerShell)
bash run.sh
```

You will see a menu where you can select a test using keys 1-9.

You can also run a test directly:

```bash
bash run.sh 3
```

---

## 🔧 Usage with LangChain

```python
from src.spec_lang.controlled_agent_excector import initialize_controlled_agent
from src.rule import Rule

from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)
 
def demo_langchain():
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

- `initialize_controlled_agent(...)` uses the `agent=` argument to select the agent implementation, so pass a value supported by the current AgentSpec/LangChain integration.
- LangChain tools must be compatible `BaseTool` instances when used with AgentSpec-controlled agents.
- `user_inspection` will prompt on stdin by default. Pass `approval_callback=...` if you want to integrate approval into your own UI.

## 🔧 Customizing AgentSpec Rule

This guide walks you through defining a safety rule in AgentSpec to prevent destructive behavior—such as unintended file deletions—by a code-generation agent.

---

### 1. **Event Name**

Ensure the **event name matches the tool name** exactly. You can obtain the tool name dynamically via `tool.name` in the agent runtime environment.

---

### 2. **Predicate Definition**

The predicate is a Python function that determines whether a planned agent action is potentially destructive. It receives:

- `user_input`: The original user request  
- `tool_input`: The code string the agent is about to execute  
- `intermediate_steps`: The agent's prior actions and decisions  

#### Example: `is_destructive` Predicate

```python
import re

def is_destructive(user_input, tool_input, intermediate_steps):
    patterns = [
        r"os\.remove",
        r"os\.unlink",
    ]
    return any(re.search(pattern, tool_input) for pattern in patterns)
```

#### Registering the Predicate

1. **Extend the grammar** (`spec_lang/AgentSpec.g4`):

```antlr
PREDICATE : ... | 'is_destructive';
```

2. **Register the function** in the rule interpreter:

```python
from src.rules.manual.table import predicate_table
from src.rules.manual.terminal import is_destructive

predicate_table['is_destructive'] = is_destructive
``` 
---

### 3. **Enforcement Strategy**

Specify one of the following enforcement modes in the rule body:

- **`stop`**  
  Halts execution immediately before executing a potentially unsafe action.

- **`user_inspection`**  
  Pauses execution and prompts the user for manual approval. If the user approves, the agent continues; otherwise, it halts.

- **`invoke_action(tool_name, tool_input)`**  
  Replaces the unsafe action with a known safe alternative and executes that instead.
  In this runtime, `tool_name` must match a registered tool name.
  Example: `invoke_action(safe_delete, "target.txt")`

- **`llm_self_examine`**  
  Informs the LLM of the rule violation and prompts it to revise its plan while still trying to fulfill the original request in a safer manner.

`llm_self_reflect` is still accepted as a compatibility alias.

--- 

## Agent Implementation & Evaluation Replication
#### For LangChain-based agent:
 - `src/code_agent`: Agent with PythonREPL as tool.
 - `src/embodied_agent`: Agent with access to robotic simulator as tool.
 - use rules in src/rules/manual/
#### Autonomous veichles 
 - The environment is built on top of Apollo https://github.com/ApolloAuto/apollo. See [uDrive](https://arxiv.org/pdf/2407.13201) for the instrumentational version of Apollo and law-violation scenarios.
 - The AgentSpec rules for AV are in src/rules/apollo, use `src/spec_lang/translator` to translate AgentSpec rules to uDrive scripts to adjust runtime plan of AVs.

 ---

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

