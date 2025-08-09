# Autocode

An AI development agent built with [autochat](https://github.com/BenderV/autochat).

Give it a task and it will autonomously code, test, and deploy using real development tools.

Think about it as a simple Claude Code but for any LLM provider.

## What it does

- **Code Editor**: Read, write, edit files with syntax awareness
- **Terminal**: Run commands, scripts, build tools, tests
- **Git Operations**: Branch, commit, push, create PRs
- **Web Rendering**: Take screenshots of web apps for testing
- **Multi-Agent**: Coordinate multiple specialized agents

## Installation

```bash
pip install -e .
```

Requires:

- Python 3.9+
- OpenAI or Anthropic API key

## Usage

### Interactive Development Agent

```bash
# Start with a task
autocode "Create a FastAPI app with user authentication"

# Or start interactive mode
autocode
> Create a React component for file upload
> Add unit tests
> Deploy to Vercel
```

### Available Commands

The project exposes a few other convenience commands:

```bash
autocode                    # Interactive agent
autocode-dual              # Dual-agent collaboration demo
autocode-export            # Export conversation history
autocode-github-issue-server  # GitHub webhook server
```

## How it Works

Built on [autochat](../autochat/), autocode gives AI agents access to real development tools:

```python
from autochat import Autochat
from autocode.code_editor import CodeEditor
from autocode.terminal import Terminal
from autocode.git import Git

agent = Autochat(
    instruction="You are a senior developer...",
    provider="anthropic",
    model="claude-sonnet-4-20250514"
)

# Add development tools as classes
agent.add_tool(CodeEditor(), "CodeEditor")
agent.add_tool(Terminal(), "Terminal")
agent.add_tool(Git(), "Git")

# Agent now has full development capabilities
agent.run_conversation("Build a web scraper with tests")
```

## Configuration

Choose your provider:

```bash
export AUTOCHAT_PROVIDER="anthropic"
export ANTHROPIC_API_KEY="your-key"
```

```bash
export AUTOCHAT_PROVIDER="openai"
export OPENAI_API_KEY="your-key"
```
