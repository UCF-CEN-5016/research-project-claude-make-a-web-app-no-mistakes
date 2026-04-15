[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/7oQPi1Yr)

# Beginner Guide (Step-by-Step)

This repository contains the AgentSpec project inside the `AgentSpec` folder.

## 1. Clone the repository

```bash
git clone https://github.com/UCF-CEN-5016/research-project-claude-make-a-web-app-no-mistakes.git
cd research-project-claude-make-a-web-app-no-mistakes
```

## 2. Move into the project folder

```bash
cd AgentSpec
```

## 3. Create a Python virtual environment

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirement.txt
```

## 5. Configure environment variables

Create a `.env` file in the `AgentSpec` folder. Add your keys as needed, for example:

```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 6. Run the test menu

From the `AgentSpec` folder:

```bash
bash src/run.sh
```

If you are on Windows and do not have bash, use Git Bash, WSL, or run the individual Python commands shown in the project README.

## 7. Read the full project documentation

See `AgentSpec/README.md` for full usage details, rule customization, and evaluation notes.
