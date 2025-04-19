# Autochat Agent with Code Editor and Terminal

This project implements an AI agent equipped with a code editor and terminal capabilities, allowing it to perform coding tasks and execute shell commands.

## Author

ben

## Project Structure

- `main.py`: The main script that initializes and runs the Autochat agent.
- `src/autocode/`:
  - `code_editor.py`: Implements the CodeEditor class.
  - `terminal.py`: Implements the Terminal class.
  - `code_editor_utils.py`: Utility functions for the code editor.

## Installation

1. Ensure you have access to the private repository.

2. Clone the repository (replace `<repository_url>` with the actual URL provided to you):
   ```
   git clone <repository_url>
   cd <project_directory>
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
## Usage

After installing the package (either from source with `pip install -e .` or from PyPI once published) the CLI entry‑points become available on your shell.

### Start an interactive session

```
autocode "Your initial prompt here"
```

If you omit the prompt the program will ask for it and keep an interactive loop alive until you type `exit` / `quit` or press `Ctrl+C` twice.

### Additional entry‑points

The project exposes a few other convenience commands:

```
autocode-export        # run the exporter defined in autocode.export:main
autocode-dual          # run the dual‑agent demo
autocode-github-issue-server  # start the webhook micro‑service
```

If you prefer running the module directly you can still use the classic Python invocation:

```
python -m autocode.cli "Your prompt"
```

Or, for historical reasons, call the script that used to live at the repository root:

```
python main.py
```

You can then interact with the agent by entering prompts. The agent can:

- Open shell sessions to run commands
- Edit code using the built-in code editor
- Perform various coding tasks based on your instructions

## Features

- AI-powered agent using the Anthropic provider
- Integrated terminal for running shell commands
- Code editor for creating and modifying files
- Ability to handle code transformations and development tasks

## Contributing

As this is a private repository, please contact the project maintainers for information on how to contribute or report issues.

## License

This project is proprietary and confidential. Unauthorized copying, transferring, or reproduction of the contents of this project, via any medium, is strictly prohibited.