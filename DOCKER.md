# Running AgentSpec with Docker

## First-Time Setup
Change the .env_example file to just env and add your real API key
Run these commands from the project root:

```bash
docker compose build
docker compose run --rm agentspec
```

## Quick Start

**Interactive menu (works reliably on local machines and Codespaces):**
```bash
docker compose run --rm agentspec
```

Type a number and press Enter.

**Optional (may work depending on terminal/input forwarding):**
```bash
docker compose up
```

**Run specific test:**
```bash
docker compose run --rm agentspec 9    # Full smoke suite (tests 2,5,6,7)
docker compose run --rm agentspec 2    # Parser unit tests
docker compose run --rm agentspec 5    # Controlled agent import test
docker compose run --rm agentspec 6    # Predicate registry test
docker compose run --rm agentspec 7    # Bytecode compilation test
docker compose run --rm agentspec 8    # Regenerate ANTLR parser (requires Java)
```

## Setup Environment

Before running Docker for the first time, you must rename `.env_example` to `.env` and add a real API key:
```bash
cp AgentSpec/.env_example AgentSpec/.env
# Edit AgentSpec/.env and add OPENAI_API_KEY="sk-..."
```

## Build Image

```bash
docker compose build              # Build image
docker compose build --no-cache   # Rebuild from scratch
```

## Common Commands

```bash
docker compose run --rm agentspec            # Interactive menu (recommended)
docker compose up                            # Alternative (terminal-dependent)
docker compose run --rm agentspec 9          # Run full test suite
docker compose run --rm agentspec bash       # Enter container shell
docker images | grep agentspec               # Check image size (~1.2GB)
```

## Troubleshooting

**"No such file or directory: .env"**
```bash
cp AgentSpec/.env_example AgentSpec/.env
```

**"OpenAI API key not found"**
```bash
cat AgentSpec/.env
docker compose run --rm agentspec bash -c "echo \$OPENAI_API_KEY"
```

**"Permission denied: src/run.sh"**
```bash
docker compose build --no-cache
```

**Clean up Docker:**
```bash
docker system prune -a
```

## Test Menu Reference

| #  | Test |
|----|------|
| 1  | LangChain smoke demo |
| 2  | Parser unit tests |
| 3  | Parse inline rule: user inspection |
| 4  | Parse inline rule: stop |
| 5  | Controlled agent import test |
| 6  | Predicate registry test |
| 7  | Bytecode compilation test |
| 8  | Regenerate parser (requires Java) |
| 9  | Full local smoke suite |
| 0  | Exit |
