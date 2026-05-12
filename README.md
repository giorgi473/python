# Modern Async CLI Workbench

A modern terminal productivity environment written in Python.

## Project Structure

- `main.py` - Entry point that starts the workbench.
- `workbench.py` - Contains the `ModernWorkbench` class and the dynamic command palette.
- `commands.py` - Defines the lightweight `Command` dataclass used for registration.
- `terminal.py` - Terminal styling utilities, progress rendering and helper functions.

## Features

- Dynamic command palette with categories, aliases, prefix matching, and fuzzy suggestions.
- Async shell command runner with live stdout/stderr streaming.
- Workspace analyzer with file type, folder activity, TODO detection, and project type hints.
- Modern focus timer, momentum booster, creative prompt generator, and secret easter egg.
- Smart search with regex, extension filtering, path targeting, and preview context.
- ANSI-rich terminal visuals, centered layouts, and auto-completion support.

## Usage

Run the workbench:

```bash
python main.py
```

Show version:

```bash
python main.py --version
```

Run a single command directly:

```bash
python main.py --run status
```

Run a command with arguments:

```bash
python main.py --run timer --args 10 2
```

Search for text in files:

```bash
python main.py --run search --path . "def" --type py --preview 3
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
