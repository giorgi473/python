# Modern Async CLI Workbench

A modern terminal productivity environment written in Python with async capabilities.

## Installation

1. Clone or download the project.
2. Install dependencies (optional, for enhanced features):

```bash
pip install -r requirements.txt
```

Note: Core functionality works without additional dependencies. Optional packages enable hardware monitoring, testing, and code quality checks.

## Project Structure

- `main.py` - Entry point that starts the workbench.
- `workbench.py` - Contains the `ModernWorkbench` class and the dynamic command palette.
- `commands.py` - Defines the lightweight `Command` dataclass used for registration.
- `terminal.py` - Terminal styling utilities, progress rendering and helper functions.
- `requirements.txt` - Optional dependencies for enhanced features.

## Features

- **Dynamic Command Palette**: Categorized commands with aliases, prefix matching, and fuzzy suggestions.
- **Async Shell Runner**: Execute shell commands with live stdout/stderr streaming.
- **Workspace Analyzer**: File type analysis, folder activity, TODO detection, and project type identification.
- **Productivity Tools**: Focus timer, momentum booster, creative prompt generator, and hidden easter eggs.
- **Smart Search**: Regex support, extension filtering, path targeting, and context previews.
- **Code Quality**: Integrated linting and testing commands (requires external tools).
- **Rich Terminal UI**: ANSI styling, centered layouts, progress bars, and auto-completion.

## Commands

### System Commands
- `status` - Show system pulse, environment, and git metadata.
- `workspace` - Analyze project structure and provide recommendations.
- `search` - Smart file search with filters and previews.

### Flow Commands
- `timer` - Run focus timers (Pomodoro, countdown, intervals).
- `boost` - Generate productivity prompts and action plans.

### Creative Commands
- `idea` - Create project ideas and innovation blueprints.
- `demo` - Render command palette previews.
- `secret` - Reveal hidden easter eggs.

### Utility Commands
- `history` - Review command execution history.
- `shell` - Run shell commands with output streaming.
- `lint` - Run code quality checks (flake8, pylint, etc.).
- `test` - Execute test suites (pytest, unittest).
- `version` - Show workbench version and runtime info.

## Usage

### Interactive Mode

```bash
python main.py
```

Type commands at the prompt. Use `help` for the command palette, `!` for shell shortcuts, or `quit` to exit.

### Direct Command Execution

```bash
python main.py --run <command> [args...]
```

Examples:

```bash
python main.py --run status
python main.py --run timer 25
python main.py --run search "TODO" --type py
python main.py --run lint
```

### Command Line Options

- `--version` - Show version information.
- `--run` - Execute a single command and exit.
- `--args` - Additional arguments for the command.

## Development

The workbench is built with modern Python practices:
- Type hints throughout
- Async/await for concurrency
- Dataclasses for data structures
- Modular design for extensibility

## Contributing

Feel free to extend the command palette or improve the terminal UI. Ensure new commands follow the async handler pattern and include proper error handling.
```

## Available commands

- `status` (`sys`, `pulse`, `info`) - Show system pulse, git branch, and environment metadata
- `workspace` (`inspect`, `analyze`, `audit`, `radar`) - Inspect the current project structure and suggest improvements
- `search` (`find`, `grep`, `seek`) - Search with regex, extension and path filters plus preview context
- `timer` (`focus`, `pomodoro`, `pomo`) - Run a focus timer or Pomodoro session
- `boost` (`mood`, `hype`, `charge`) - Generate a high-energy action prompt
- `idea` (`spark`, `prompt`) - Generate a creative productivity or project idea
- `demo` (`show`, `view`, `palette`) - Render a terminal-friendly visual flow preview
- `history` (`log`, `recent`) - Review session command history
- `shell` (`run`, `exec`, `cmd`) - Execute a shell command with streamed output
- `version` (`ver`, `about`) - Show version and runtime details
- `secret` (`magic`, `easter`, `hidden`) - Reveal a hidden workspace message

## Shell shortcuts

- `help`, `menu`, `list` - Show the command palette
- `clear`, `cls` - Clear the screen
- `exit`, `quit`, `q` - Exit the workbench
- `!<command>` - Run a shell command directly, for example `!dir` or `!ls`

## Notes

- The project runs with standard Python libraries; optional `psutil` adds richer memory and CPU output.
- For best terminal visuals, use Windows Terminal, PowerShell 7+, or an ANSI-compatible terminal.
