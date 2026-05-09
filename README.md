# Modern Async CLI Workbench

A lightweight terminal productivity tool written in Python.

## Project Structure

- `main.py` - Entry point that starts the workbench.
- `workbench.py` - Contains the `ModernWorkbench` class and the interactive command palette.
- `commands.py` - Defines the `Command` dataclass used by the workbench.
- `terminal.py` - Terminal helpers and ANSI styling utilities.

## Features

- Interactive CLI palette with command aliases, fuzzy matching, and history.
- Enhanced system pulse with git branch detection and load averages.
- Creative prompt engine with project blueprints and surprise sparks.
- Focus timer with Pomodoro support and cycle summaries.
- Adaptive visual flow preview with rainbow text and terminal-aware layout.

## Usage

Run the workbench:

```bash
python main.py
```

Run a single command directly:

```bash
python main.py --command status
```

Run a command with arguments:

```bash
python main.py --command timer --args 10 2
```

Available commands:

- `status` (`sys`, `pulse`, `info`) - Show system pulse and environment info
- `idea` (`spark`, `prompt`) - Generate an innovation prompt and design blueprint
- `timer` (`focus`, `pomodoro`) - Run a countdown, work session, or Pomodoro cycle
- `demo` (`show`, `view`) - Render an adaptive visual flow preview
- `history` (`log`) - Review the commands executed during the session

## Shell shortcuts

- `help`, `menu`, `list` - Show command palette
- `clear`, `cls` - Clear the screen
- `exit`, `quit`, `q` - Exit the workbench

## Notes

- The project uses only standard Python libraries.
- For best terminal visuals, use Windows Terminal, PowerShell 7+, or any ANSI-compatible terminal.
